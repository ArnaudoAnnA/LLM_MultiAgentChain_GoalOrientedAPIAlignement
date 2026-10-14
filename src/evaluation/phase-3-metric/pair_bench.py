"""Build and label a bench of (generated goal, reference goal) pairs judged by a person.

Two commands:
  extract   draw the pairs from the output JSONs of one replica and freeze them on disk;
            with --append a further batch is added to an existing bench, keeping its pairs
  label     show the pairs one at a time and store one label per pair; a pair can be skipped
            and comes back after the others, or at the next session

Files written in the bench directory:
  pairs.csv       what the judge sees: pair id, system, system set, node, reference, generated
  selection.csv   how each pair was drawn: configuration, stratum and the similarity used
  manifest.json   seed, quotas, encoders and the counts actually drawn
  labels.csv      one row per judged pair: label, seconds spent, timestamp, whether the hint was seen
  suggestions.csv optional hints, one suggested label and a short reason per pair

Most pairs are drawn uniformly inside equal-width bands of the sampling encoder's cosine, so
that the whole similarity scale is covered. The remaining ones are the best match of a random
reference according to other encoders, so that no single encoder draws the whole bench. The
judge never sees a score: similarities live only in selection.csv.

Run from the repository root:
`python src/evaluation/phase-3-metric/pair_bench.py extract --run <replica dir> --out <bench dir>`
`python src/evaluation/phase-3-metric/pair_bench.py label --bench <bench dir>`
"""
import argparse
import csv
import json
import os
import random
import shutil
import sys
import textwrap
import time
from datetime import datetime

LABELS = {"1": "equivalente", "2": "parziale", "3": "diverso"}
SHOTS = ["ZERO_SHOT", "ONE_SHOT", "FEW_SHOT"]
CRITIC = {"ON": "", "OFF": "_noLlama"}
NODE_TITLES = {"actors": "ACTORS", "highLevelGoals": "HIGH-LEVEL GOALS", "lowLevelGoals": "LOW-LEVEL GOALS"}
# Pairs per node over the whole bench, shortest lists first: a system with no usable pair
# for one node is compensated on the following ones.
QUOTAS = {"actors": 20, "highLevelGoals": 40, "lowLevelGoals": 60}
BAND_EDGES = [0.2, 0.4, 0.6, 0.8]
SAMPLING_ENCODER = "minilm"
# Share of the pairs picked as best match by the other encoders.
OTHER_SHARE = 0.2
OTHER_ENCODERS = ["production", "mpnet"]


def band_of(cosine):
    return sum(cosine >= edge for edge in BAND_EDGES)


def normalise(text):
    return " ".join(text.lower().split())


def split_per_system(total, systems, rng, taken):
    """Spread `total` pairs over the systems as evenly as possible.

    Systems that already hold more pairs from other nodes get the smaller share, so the
    per-system totals stay equal when the node totals allow it.
    """
    base, extra = divmod(total, len(systems))
    order = sorted(systems, key=lambda s: (taken[s], rng.random()))
    return {s: base + (1 if i < extra else 0) for i, s in enumerate(order)}


def extract(args):
    import numpy as np

    sys.path.insert(0, os.getcwd())
    sys.path.insert(0, os.path.join(os.getcwd(), "notebook"))
    from src.diagnostics.metric_diagnostics import Embedder, PRODUCTION
    from src.evaluation.goal_evaluator import ENCODERS, GoalEvaluator
    from groundtruth import ALL_GROUNDTRUTHS
    from system_sets import SYSTEM_SETS

    pairs_path = os.path.join(args.out, "pairs.csv")
    existing = []
    if args.append:
        with open(pairs_path, encoding="utf-8") as f:
            existing = list(csv.DictReader(f))
    elif os.path.exists(os.path.join(args.out, "labels.csv")) and not args.force:
        raise SystemExit("this bench already has labels: extracting again would orphan them (--force to overwrite)")
    quotas = dict(QUOTAS)
    if args.quota:
        quotas = {node: int(n) for node, n in (item.split("=") for item in args.quota)}
        unknown = set(quotas) - set(QUOTAS)
        if unknown:
            raise SystemExit(f"unknown node(s): {sorted(unknown)}")
    # Text pairs already in the bench are never drawn again.
    frozen = {(normalise(p["generated"]), normalise(p["reference"])) for p in existing}

    rng = random.Random(args.seed)
    ground_truth = {g["name"]: g for g in ALL_GROUNDTRUTHS}
    systems = SYSTEM_SETS["all"]
    run_dir = args.run.rstrip("/")

    bert = GoalEvaluator(preprocess=True)
    embedders = {}

    def embedder(name):
        if name not in embedders:
            embedders[name] = Embedder(name, bert)
        return embedders[name]

    configs = [(shot, critic) for shot in SHOTS for critic in CRITIC]
    generated = {}
    for system in systems:
        for shot, critic in configs:
            path = os.path.join(run_dir, system, f"{system}_{shot}{CRITIC[critic]}.json")
            with open(path, encoding="utf-8") as f:
                generated[system, shot, critic] = json.load(f)

    taken = {s: 0 for s in systems}
    used_generated = set()
    pairs = []
    for node, total in quotas.items():
        # One candidate per distinct (generated, reference) text pair, with its configuration.
        pools = {s: {b: [] for b in range(len(BAND_EDGES) + 1)} for s in systems}
        best = {s: {name: [] for name in OTHER_ENCODERS} for s in systems}
        for system in systems:
            refs = ground_truth[system][node]
            seen = set()
            for shot, critic in configs:
                preds = generated[system, shot, critic][node]
                if not preds:
                    continue
                sim = embedder(SAMPLING_ENCODER).sim(preds, refs)
                for i, pred in enumerate(preds):
                    for j, ref in enumerate(refs):
                        key = (normalise(pred), normalise(ref))
                        if key[0] == key[1] or key in seen or key in frozen:
                            continue
                        seen.add(key)
                        pools[system][band_of(sim[i, j])].append(
                            {"generated": pred, "reference": ref, "shot": shot, "critic": critic,
                             "cosine": float(sim[i, j])})
                for name in OTHER_ENCODERS:
                    other = embedder(PRODUCTION[node] if name == "production" else name).sim(preds, refs)
                    for j, ref in enumerate(refs):
                        i = int(other[:, j].argmax())
                        if normalise(preds[i]) != normalise(ref) and (normalise(preds[i]), normalise(ref)) not in frozen:
                            best[system][name].append(
                                {"generated": preds[i], "reference": ref, "shot": shot, "critic": critic,
                                 "cosine": float(sim[i, j])})

        usable = [s for s in systems if any(pools[s].values())]
        capacity = {s: 0 for s in systems}
        capacity.update(split_per_system(total, usable, rng, taken))
        for system, n in capacity.items():
            taken[system] += n

        n_other = round(total * OTHER_SHARE)
        n_bands = len(BAND_EDGES) + 1
        strata = [f"best_{OTHER_ENCODERS[k % len(OTHER_ENCODERS)]}" for k in range(n_other)]
        strata += [f"band_{k % n_bands}" for k in range(total - n_other)]

        def candidates(system, stratum):
            pool = best[system][stratum[5:]] if stratum.startswith("best_") else pools[system][int(stratum[5:])]
            return [c for c in pool if normalise(c["generated"]) not in used_generated]

        # Scarce strata first: they can be served by few systems.
        rng.shuffle(strata)
        strata.sort(key=lambda st: sum(bool(candidates(s, st)) for s in systems))
        for stratum in strata:
            open_systems = [s for s in systems if capacity[s] > 0]
            able = [s for s in open_systems if candidates(s, stratum)]
            if able:
                # Prefer the systems with most room left, to keep the per-system totals reachable.
                most = max(capacity[s] for s in able)
                system = rng.choice([s for s in able if capacity[s] == most])
                drawn = stratum
            else:
                # Requested band empty everywhere there is room: take the nearest non-empty band.
                wanted = int(stratum[5:]) if stratum.startswith("band_") else n_bands - 1
                options = [(abs(b - wanted), rng.random(), s, b) for s in open_systems for b in range(n_bands)
                           if candidates(s, f"band_{b}")]
                # No system with room has an unused pair left: let any other system take the slot.
                options = options or [(abs(b - wanted), rng.random(), s, b) for s in systems
                                      for b in range(n_bands) if candidates(s, f"band_{b}")]
                if not options:
                    # Every distinct generated text of this node is already in a pair.
                    break
                _, _, system, b = min(options)
                drawn = f"band_{b}"
            choice = rng.choice(candidates(system, drawn))
            used_generated.add(normalise(choice["generated"]))
            capacity[system] -= 1
            pairs.append({"system": system, "node": node, "requested": stratum, "drawn": drawn, **choice})

    # Presentation order: by system, then by node, shuffled inside each group.
    node_order = list(NODE_TITLES)
    rng.shuffle(pairs)
    pairs.sort(key=lambda p: (systems.index(p["system"]), node_order.index(p["node"])))
    dev = set(SYSTEM_SETS["dev"])
    for k, pair in enumerate(pairs, start=len(existing) + 1):
        pair["pair_id"] = f"P{k:03d}"
        pair["set"] = "dev" if pair["system"] in dev else "holdout"
        pair["band"] = band_of(pair["cosine"])

    os.makedirs(args.out, exist_ok=True)
    mode = "a" if args.append else "w"
    with open(pairs_path, mode, newline="", encoding="utf-8") as f:
        fields = ["pair_id", "system", "set", "node", "reference", "generated"]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if not args.append:
            writer.writeheader()
        writer.writerows(pairs)
    with open(os.path.join(args.out, "selection.csv"), mode, newline="", encoding="utf-8") as f:
        fields = ["pair_id", "shot", "critic", "requested", "drawn", "band", "cosine"]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if not args.append:
            writer.writeheader()
        writer.writerows([{**p, "cosine": round(p["cosine"], 6)} for p in pairs])

    def count(key):
        values = [p[key] for p in pairs]
        return {str(v): values.count(v) for v in sorted(set(values), key=str)}

    manifest = {
        "seed": args.seed, "run": run_dir, "n_pairs": len(pairs), "quotas": quotas,
        "sampling_encoder": {SAMPLING_ENCODER: ENCODERS[SAMPLING_ENCODER]},
        "other_encoders": {"production": PRODUCTION, "mpnet": ENCODERS["mpnet"]},
        "band_edges": BAND_EDGES, "other_share": OTHER_SHARE,
        "per_system": count("system"), "per_node": count("node"), "per_set": count("set"),
        "per_shot": count("shot"), "per_critic": count("critic"),
        "per_band": count("band"), "per_requested_stratum": count("requested"),
        "fallbacks": sum(p["requested"] != p["drawn"] for p in pairs),
        "per_node_band": {node: {str(b): sum(p["node"] == node and p["band"] == b for p in pairs)
                                 for b in range(len(BAND_EDGES) + 1)} for node in quotas},
    }
    manifest_path = os.path.join(args.out, "manifest.json")
    if args.append:
        # The first batch keeps its manifest untouched; later ones are listed under it.
        with open(manifest_path, encoding="utf-8") as f:
            whole = json.load(f)
        manifest["first_pair_id"] = pairs[0]["pair_id"] if pairs else None
        whole.setdefault("appended_batches", []).append(manifest)
    else:
        whole = manifest
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(whole, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: manifest[k] for k in ("n_pairs", "per_node", "per_set", "per_band", "per_node_band",
                                               "per_shot", "fallbacks")}, indent=2))
    print(f"written: {args.out}")


def read_key():
    """One keypress without Enter on a terminal; a whole line otherwise."""
    if not sys.stdin.isatty():
        line = sys.stdin.readline()
        return line.strip()[:1] if line else "q"
    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def load_labels(path):
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {row["pair_id"]: row for row in csv.DictReader(f)}


def save_labels(path, labels, order):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pair_id", "label", "seconds", "timestamp", "hint_seen"])
        writer.writeheader()
        writer.writerows(labels[pid] for pid in order if pid in labels)
    os.replace(tmp, path)


def show_pair(pair, n_done, n_total, n_left, n_skipped, hint=None, has_hints=False):
    """Print one pair as a wrapped, spaced block."""
    width = min(shutil.get_terminal_size((100, 24)).columns, 110)
    rule = "─" * width

    def block(title, text):
        print(f"  {title}\n")
        for line in textwrap.wrap(text, width - 6) or [""]:
            print(f"      {line}")
        print()

    if sys.stdout.isatty():
        print("\033[2J\033[H", end="")
    print(f"\n{rule}")
    status = f"  Judged {n_done} of {n_total}   ·   to do {n_left}"
    print(status + (f"   ·   skipped, queued {n_skipped}" if n_skipped else ""))
    print(f"{rule}\n")
    print(f"  Pair {pair['pair_id']}   ·   {pair['system']}   ·   {NODE_TITLES[pair['node']]}\n")
    block("REFERENCE", pair["reference"])
    block("GENERATED", pair["generated"])
    if hint:
        print(f"  HINT: {hint['suggestion']}  —  {hint['reason']}\n")
    print(rule)
    print("  Judge action and object; actor and style do not count. When in doubt, take the stricter label.\n")
    print("  [1] equivalente (equivalent)    [2] parziale (partial)    [3] diverso (different)")
    print("  [s] skip (back to the end)    [b] go back    [q] quit and save" +
          ("    [h] show the hint" if has_hints and not hint else ""))
    print(f"{rule}\n")


def label(args):
    with open(os.path.join(args.bench, "pairs.csv"), newline="", encoding="utf-8") as f:
        pairs = {p["pair_id"]: p for p in csv.DictReader(f)}
    order = list(pairs)
    labels_path = os.path.join(args.bench, "labels.csv")
    labels = load_labels(labels_path)

    # Skipped pairs go to the back of the queue; a new session starts again from every unjudged pair.
    queue = [pid for pid in order if pid not in labels]
    skipped = set()
    history = []
    hints_path = os.path.join(args.bench, "suggestions.csv")
    hints = {}
    if os.path.exists(hints_path):
        with open(hints_path, newline="", encoding="utf-8") as f:
            hints = {row["pair_id"]: row for row in csv.DictReader(f)}
    revealed = set()
    started = None
    while queue:
        pid = queue[0]
        if args.show_hints and pid in hints:
            revealed.add(pid)
        show_pair(pairs[pid], len(labels), len(order), len(queue), len(skipped),
                  hint=hints.get(pid) if pid in revealed else None, has_hints=pid in hints)
        # The clock keeps running when the same pair is redrawn to reveal its hint.
        started = started or time.time()
        key = read_key().lower()
        if key == "q":
            break
        if key == "h":
            if pid in hints:
                revealed.add(pid)
            continue
        elapsed, started = round(time.time() - started, 1), None
        if key == "s":
            queue.append(queue.pop(0))
            skipped.add(pid)
        elif key == "b" and history:
            previous = history.pop()
            labels.pop(previous, None)
            save_labels(labels_path, labels, order)
            queue.insert(0, previous)
        elif key in LABELS:
            labels[pid] = {"pair_id": pid, "label": LABELS[key], "seconds": elapsed,
                           "timestamp": datetime.now().isoformat(timespec="seconds"),
                           "hint_seen": int(pid in revealed)}
            save_labels(labels_path, labels, order)
            queue.pop(0)
            skipped.discard(pid)
            history.append(pid)

    done = [labels[pid]["label"] for pid in order if pid in labels]
    print(f"\n  Judged {len(done)} pairs of {len(order)}: " +
          ", ".join(f"{name} {done.count(name)}" for name in LABELS.values()))
    if queue:
        print(f"  Still to judge: {len(queue)} (of which skipped: {len(skipped)}). They come back next session.")
    print(f"  Saved to {labels_path}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    p_extract = commands.add_parser("extract", help="draw and freeze the pairs")
    p_extract.add_argument("--run", required=True, help="replica output directory")
    p_extract.add_argument("--out", required=True)
    p_extract.add_argument("--seed", type=int, default=20261012)
    p_extract.add_argument("--force", action="store_true", help="overwrite a bench that already has labels")
    p_extract.add_argument("--append", action="store_true",
                           help="add a batch to an existing bench: its pairs and labels are kept")
    p_extract.add_argument("--quota", nargs="+", metavar="NODE=N",
                           help="pairs per node for this batch, e.g. actors=30 (default: the full bench)")
    p_extract.set_defaults(func=extract)
    p_label = commands.add_parser("label", help="judge the pairs one at a time")
    p_label.add_argument("--bench", required=True)
    p_label.add_argument("--show-hints", action="store_true",
                         help="show the suggested label on every pair instead of on request")
    p_label.set_defaults(func=label)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
