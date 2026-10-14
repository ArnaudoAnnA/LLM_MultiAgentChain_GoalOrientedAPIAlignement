"""Study the generated goals that earn no credit under one-to-one matching.

Four commands:
  census   score every list and describe the items left without credit
  sample   draw a sample of those items, each with its closest references, to be judged
  winners  for the sampled items judged equivalent to a reference, pair that reference with
           the item that took it in the one-to-one matching
  grid     score every list under every combination of encoder, credit form and matching

Census. Every list is scored with a sentence encoder and the ramp credit, matching generated and
reference items one-to-one so that the credit counted is maximal. For every generated item
the script records the credit it earns, the reference it is most similar to and the zone of
that similarity:

  low   below the low point of the ramp: no reference would give it credit
  mid   between the two points
  high  from the high point upwards: its closest reference would give it full credit

It also scores every list with free coverage, where the one-to-one constraint is dropped:
precision is the mean, over the generated items, of the credit with their closest reference;
recall is the mean, over the references, of the credit with their closest generated item.
No more lenient matching can score higher, so the gap between the two F1 bounds what a
change of matching strategy can move.

Files written by `census` in the output directory:
  goals.csv     one row per generated item
  lists.csv     one row per list: counts, both F1 and their gap
  summary.csv   one row per node and per (node, system), with the noise across replicas

Sample. From one replica of the census, a fixed number of zero-credit items per system and
node is drawn by zone; repeated items and items already in another bench are left out. Each
item is paired with its closest references: the top ones of the census encoder plus the top
one of a second encoder, so that the shortlist does not rest on a single model.

Files written by `sample` in the bench directory, in the layout read by `pair_bench.py label`:
  pairs.csv       what the judge sees: pair id, item id, system, set, node, reference, generated
  selection.csv   how each pair was drawn: configuration, zone, reference rank and similarities
  manifest.json   seed, quotas, counts drawn and the check of the shortlist on judged pairs

Winners. A zero-credit item judged equivalent to a reference lost that reference to another
item of the same list. Judging that other item against the reference tells a redundant copy
(the winner is equivalent too) from a wrong match (it is not). `winners` reads labels.csv and,
when present, outside_review.csv from the bench directory and writes there:
  winner_pairs.csv       pair id, item id, system, set, node, reference, generated (the winner)
  winner_selection.csv   the losing item, its configuration and the winner's credit

Grid. Every list is scored under each combination of
  encoder    bert (mean-pooled bert-base-uncased; goals are preprocessed, actor names are not)
             or a sentence encoder
  credit     sum (the cosine itself) or ramp
  matching   one (a reference pays one generated item), two (at most two), free (no limit)
Precision is the credit earned by the generated items over their number. Recall counts each
reference once, with the highest credit among the items that took it, over the number of
references; under free matching it is the highest credit over all generated items. The ramp
points of an encoder are derived once and shared by the three matchings: for goals the low
point is a percentile of the cosine of pairs matched one-to-one across systems and the high
point a percentile of the bench pairs labelled equivalent; for actors both come from the bench.

Tests, per node and combination:
  cross      F1 against the ground truth of the other systems, over F1 against the own one
  foreign    how often one generated goal of another system, appended to the list, raises F1
  doubled    how often F1 rises when every item of the list appears twice
  agreement  on the judged sample, probability that an item with a better label earns more
             credit in its own list (ties count one half)
  noise      standard deviation of F1 across replicas
  order      ramp only: whether the ranking of the configurations survives a change of low point

Files written by `grid` in the output directory:
  grid.csv        one row per (node, encoder, credit, matching) with scores and tests
  lists.csv       F1, precision and recall of every list under every combination
  copies.csv      share of generated items that are near copies of an earlier item of the list
  points.json     ramp points per encoder, and the check of the copy rule on judged pairs

No model API is called. Run from the repository root:
`python src/evaluation/phase-3-metric/matching_forms.py census --runs <replica dirs> --out <dir>`
`python src/evaluation/phase-3-metric/matching_forms.py sample --census <dir> --out <bench dir>`
`python src/evaluation/phase-3-metric/matching_forms.py winners --census <dir> --bench <bench dir>`
`python src/evaluation/phase-3-metric/matching_forms.py grid --runs <replica dirs> --bench <pair bench dir>
    --sample <sample bench dir> --out <dir>`
"""
import argparse
import csv
import json
import os
import random
import sys

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import kendalltau

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "notebook"))
from src.evaluation.goal_evaluator import ENCODERS, RAMPS, GoalEvaluator, SentenceEncoder, SLOT_DISCOUNT  # noqa: E402
from groundtruth import ALL_GROUNDTRUTHS  # noqa: E402

SHOTS = ["ZERO_SHOT", "ONE_SHOT", "FEW_SHOT"]
CRITIC = {"ON": "", "OFF": "_noLlama"}
NODES = ["actors", "highLevelGoals", "lowLevelGoals"]
ZONES = ["low", "mid", "high"]
# Items drawn per system and node, by zone: the matching strategies differ above the low point.
ZONE_QUOTA = {"low": 1, "mid": 3, "high": 3}
SHORTLIST = 3
SECOND_ENCODER = "mpnet"
GOAL_NODES = ["highLevelGoals", "lowLevelGoals"]
MATCHINGS = ["one", "two", "free"]
LOW_PERCENTILES = [90, 95, 97]
MAIN_LOW = 95
HIGH_PERCENTILE = 25
FOREIGN_PER_LIST = 30
LABEL_ORDER = ["equivalente", "parziale", "diverso"]


def normalise(text):
    return " ".join(text.lower().split())


def zone_of(cosine, low, high):
    return "low" if cosine < low else "mid" if cosine < high else "high"


def census_list(sim, low, high, preds):
    """Per-item rows and list-level scores of one generated list against its references."""
    g, r = sim.shape
    credit = np.clip((sim - low) / (high - low), 0.0, 1.0)
    rows, cols = linear_sum_assignment(-credit)
    partner = dict(zip(rows.tolist(), cols.tolist()))
    seen = set()
    items = []
    for i, pred in enumerate(preds):
        best = int(sim[i].argmax())
        earned = float(credit[i, partner[i]]) if i in partner else 0.0
        key = normalise(pred)
        items.append({
            "index": i, "credit": round(earned, 6), "partner_ref": partner.get(i, ""),
            "best_ref": best, "best_cosine": round(float(sim[i, best]), 6),
            "best_credit": round(float(credit[i, best]), 6),
            "zone": zone_of(sim[i, best], low, high), "repeated": int(key in seen),
            # A partner that pays less than the closest reference would.
            "displaced": int(i in partner and credit[i, partner[i]] < credit[i, best] - 1e-9),
        })
        seen.add(key)
    total = credit[rows, cols].sum()
    precision, recall = credit.max(axis=1).mean(), credit.max(axis=0).mean()
    free = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    scores = {"g": g, "r": r, "f1_one_to_one": 2 * total / (g + r), "f1_free": float(free),
              "precision_one_to_one": total / g, "precision_free": float(precision),
              "recall_one_to_one": total / r, "recall_free": float(recall)}
    return items, scores


def census(args):
    encoder = SentenceEncoder(args.encoder, device=args.device)
    ramps = RAMPS[args.encoder]
    ground_truth = {g["name"]: g for g in ALL_GROUNDTRUTHS}
    systems = list(ground_truth)
    configs = [(shot, critic) for shot in SHOTS for critic in CRITIC]
    replicas = [f"r{i}" for i in range(1, len(args.runs) + 1)]

    goal_rows, list_rows = [], []
    for replica, run_dir in zip(replicas, args.runs):
        for system in systems:
            for shot, critic in configs:
                path = os.path.join(run_dir.rstrip("/"), system, f"{system}_{shot}{CRITIC[critic]}.json")
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                for node in NODES:
                    preds, refs = data[node], ground_truth[system][node]
                    key = {"replica": replica, "system": system, "shot": shot, "critic": critic, "node": node}
                    if not preds:
                        list_rows.append({**key, "g": 0, "r": len(refs), "f1_one_to_one": 0.0, "f1_free": 0.0,
                                          "precision_one_to_one": 0.0, "precision_free": 0.0,
                                          "recall_one_to_one": 0.0, "recall_free": 0.0, "gap": 0.0,
                                          "zero": 0, **{f"zero_{z}": 0 for z in ZONES},
                                          "repeated": 0, "displaced": 0})
                        continue
                    sim = encoder.encode(preds) @ encoder.encode(refs).T
                    items, scores = census_list(sim, *ramps[node], preds)
                    for item, pred in zip(items, preds):
                        goal_rows.append({**key, **item, "generated": pred})
                    zero = [it for it in items if it["credit"] == 0]
                    list_rows.append({
                        **key, **{k: round(v, 6) if isinstance(v, float) else v for k, v in scores.items()},
                        "gap": round(scores["f1_free"] - scores["f1_one_to_one"], 6), "zero": len(zero),
                        **{f"zero_{z}": sum(it["zone"] == z for it in zero) for z in ZONES},
                        "repeated": sum(it["repeated"] for it in items),
                        "displaced": sum(it["displaced"] for it in items),
                    })

    def summarise(node, system=None):
        rows = [row for row in list_rows if row["node"] == node and system in (None, row["system"])]
        g = sum(row["g"] for row in rows)
        zero = sum(row["zero"] for row in rows)
        by_cell = {}
        for row in rows:
            by_cell.setdefault((row["system"], row["shot"], row["critic"]), []).append(row)

        def noise(field):
            return float(np.mean([np.std([c[field] for c in cell], ddof=1) for cell in by_cell.values()]))

        return {
            "node": node, "system": system or "ALL", "lists": len(rows), "generated": g,
            "references": sum(row["r"] for row in rows),
            "zero": zero, "zero_share": round(zero / g, 4),
            **{f"zero_{z}_share": round(sum(row[f"zero_{z}"] for row in rows) / zero, 4) if zero else ""
               for z in ZONES},
            "repeated_share": round(sum(row["repeated"] for row in rows) / g, 4),
            "displaced_share": round(sum(row["displaced"] for row in rows) / g, 4),
            "f1_one_to_one": round(float(np.mean([row["f1_one_to_one"] for row in rows])), 4),
            "f1_free": round(float(np.mean([row["f1_free"] for row in rows])), 4),
            "gap": round(float(np.mean([row["gap"] for row in rows])), 4),
            "noise_sd_one_to_one": round(noise("f1_one_to_one"), 4) if len(replicas) > 1 else "",
            "noise_sd_free": round(noise("f1_free"), 4) if len(replicas) > 1 else "",
        }

    summary_rows = [summarise(node) for node in NODES]
    summary_rows += [summarise(node, system) for node in NODES for system in systems]

    os.makedirs(args.out, exist_ok=True)
    for name, rows in (("goals.csv", goal_rows), ("lists.csv", list_rows), ("summary.csv", summary_rows)):
        with open(os.path.join(args.out, name), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({"encoder": {args.encoder: ENCODERS[args.encoder]}, "ramps": ramps, "runs": args.runs}, f, indent=2)

    for row in summary_rows[:len(NODES)]:
        print(" | ".join(f"{k}={v}" for k, v in row.items()))
    print(f"written: {args.out}")


def shortlist(first, second, size=SHORTLIST):
    """Reference indices to show for one item: the top of `first`, with the top of `second` among them.

    Returns (index, source) pairs; the second encoder's favourite replaces the last slot when
    the first encoder did not already rank it there.
    """
    order = np.argsort(-first).tolist()
    chosen = order[:size]
    favourite = int(second.argmax())
    if favourite not in chosen:
        chosen[-1] = favourite
    return [(j, "second" if j == favourite and j not in order[:size] else "first") for j in chosen]


def sample(args):
    from system_sets import SYSTEM_SETS

    rng = random.Random(args.seed)
    ground_truth = {g["name"]: g for g in ALL_GROUNDTRUTHS}
    systems = SYSTEM_SETS["all"]
    dev = set(SYSTEM_SETS["dev"])
    with open(os.path.join(args.census, "manifest.json"), encoding="utf-8") as f:
        first_name = next(iter(json.load(f)["encoder"]))
    first = SentenceEncoder(first_name, device=args.device)
    second = SentenceEncoder(SECOND_ENCODER, device=args.device)

    def sims(encoder, text, refs):
        return (encoder.encode([text]) @ encoder.encode(refs).T)[0]

    # Check of the shortlist on pairs a judge already called equivalent: is that reference shown?
    check = {"equivalent_pairs": 0, "in_shortlist": 0, "rank_counts": {}}
    frozen = set()
    for bench in args.exclude or []:
        with open(os.path.join(bench, "pairs.csv"), encoding="utf-8") as f:
            judged = {p["pair_id"]: p for p in csv.DictReader(f)}
        frozen |= {normalise(p["generated"]) for p in judged.values()}
        with open(os.path.join(bench, "labels.csv"), encoding="utf-8") as f:
            labels = {row["pair_id"]: row["label"] for row in csv.DictReader(f)}
        for pair_id, label in labels.items():
            pair = judged[pair_id]
            if label != "equivalente" or pair["node"] not in args.nodes:
                continue
            refs = ground_truth[pair["system"]][pair["node"]]
            target = refs.index(pair["reference"])
            a, b = sims(first, pair["generated"], refs), sims(second, pair["generated"], refs)
            rank = np.argsort(-a).tolist().index(target) + 1
            check["equivalent_pairs"] += 1
            check["in_shortlist"] += target in [j for j, _ in shortlist(a, b)]
            check["rank_counts"][str(rank)] = check["rank_counts"].get(str(rank), 0) + 1

    with open(os.path.join(args.census, "goals.csv"), encoding="utf-8") as f:
        goals = [g for g in csv.DictReader(f)
                 if g["replica"] == args.replica and float(g["credit"]) == 0 and g["repeated"] == "0"]

    items = []
    for node in args.nodes:
        for system in systems:
            pools = {zone: [] for zone in ZONES}
            seen = set(frozen)
            for goal in goals:
                key = normalise(goal["generated"])
                if goal["node"] == node and goal["system"] == system and key not in seen:
                    seen.add(key)
                    pools[goal["zone"]].append(goal)
            for zone in ZONES:
                rng.shuffle(pools[zone])
            for zone in [z for z in ZONES for _ in range(ZONE_QUOTA[z])]:
                # Requested zone empty: take the nearest one that still has items.
                options = sorted((z for z in ZONES if pools[z]), key=lambda z: abs(ZONES.index(z) - ZONES.index(zone)))
                if not options:
                    break
                items.append({**pools[options[0]].pop(), "requested_zone": zone})

    rng.shuffle(items)
    node_order = list(args.nodes)
    items.sort(key=lambda it: (systems.index(it["system"]), node_order.index(it["node"])))
    pairs = []
    for k, item in enumerate(items, start=1):
        refs = ground_truth[item["system"]][item["node"]]
        a, b = sims(first, item["generated"], refs), sims(second, item["generated"], refs)
        ranks = np.argsort(-a).tolist()
        shown = shortlist(a, b)
        rng.shuffle(shown)
        for j, source in shown:
            pairs.append({
                "item_id": f"G{k:03d}", "system": item["system"],
                "set": "dev" if item["system"] in dev else "holdout", "node": item["node"],
                "reference": refs[j], "generated": item["generated"],
                "shot": item["shot"], "critic": item["critic"], "index": item["index"],
                "zone": item["zone"], "requested_zone": item["requested_zone"],
                "partner_ref": item["partner_ref"], "ref_index": j, "ref_rank": ranks.index(j) + 1,
                "ref_source": source, "cosine": round(float(a[j]), 6),
                "cosine_second": round(float(b[j]), 6),
            })
    for k, pair in enumerate(pairs, start=1):
        pair["pair_id"] = f"Q{k:03d}"

    os.makedirs(args.out, exist_ok=True)
    seen_fields = ["pair_id", "item_id", "system", "set", "node", "reference", "generated"]
    drawn_fields = ["pair_id", "item_id", "shot", "critic", "index", "zone", "requested_zone", "partner_ref",
                    "ref_index", "ref_rank", "ref_source", "cosine", "cosine_second"]
    for name, fields in (("pairs.csv", seen_fields), ("selection.csv", drawn_fields)):
        with open(os.path.join(args.out, name), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(pairs)

    def count(rows, key):
        values = [row[key] for row in rows]
        return {str(v): values.count(v) for v in sorted(set(values), key=str)}

    manifest = {
        "seed": args.seed, "census": args.census, "replica": args.replica, "nodes": args.nodes,
        "encoders": {first_name: ENCODERS[first_name], SECOND_ENCODER: ENCODERS[SECOND_ENCODER]},
        "zone_quota": ZONE_QUOTA, "shortlist": SHORTLIST, "excluded_benches": args.exclude or [],
        "n_items": len(items), "n_pairs": len(pairs),
        "items_per_node": count(items, "node"), "items_per_system": count(items, "system"),
        "items_per_zone": count(items, "zone"),
        "items_per_node_zone": {node: count([it for it in items if it["node"] == node], "zone")
                                for node in args.nodes},
        "fallbacks": sum(it["zone"] != it["requested_zone"] for it in items),
        "pairs_from_second_encoder": sum(p["ref_source"] == "second" for p in pairs),
        "shortlist_check": check,
    }
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(json.dumps({k: manifest[k] for k in ("n_items", "n_pairs", "items_per_node_zone", "fallbacks",
                                               "pairs_from_second_encoder", "shortlist_check")}, indent=2))
    print(f"written: {args.out}")


def winners(args):
    ground_truth = {g["name"]: g for g in ALL_GROUNDTRUTHS}

    def read(name):
        with open(os.path.join(args.bench, name), encoding="utf-8") as f:
            return list(csv.DictReader(f))

    pairs = read("pairs.csv")
    drawn = {row["pair_id"]: row for row in read("selection.csv")}
    labels = {row["pair_id"]: row["label"] for row in read("labels.csv")}
    with open(os.path.join(args.census, "goals.csv"), encoding="utf-8") as f:
        goals = [g for g in csv.DictReader(f) if g["replica"] == args.replica]
    holder = {(g["system"], g["shot"], g["critic"], g["node"], g["partner_ref"]): g
              for g in goals if g["partner_ref"] != ""}

    # (item, reference) couples judged equivalent, among the pairs shown and the references added later.
    first = {}
    for pair in pairs:
        first.setdefault(pair["item_id"], pair)
    targets = [(pair, pair["reference"]) for pair in pairs if labels[pair["pair_id"]] == "equivalente"]
    if os.path.exists(os.path.join(args.bench, "outside_review.csv")):
        targets += [(first[row["item_id"]], row["reference"]) for row in read("outside_review.csv")
                    if row["final"] == "equivalente"]

    rows = []
    for pair, reference in targets:
        how = drawn[first[pair["item_id"]]["pair_id"]]
        refs = ground_truth[pair["system"]][pair["node"]]
        winner = holder.get((pair["system"], how["shot"], how["critic"], pair["node"], str(refs.index(reference))))
        rows.append({
            "pair_id": f"W{len(rows) + 1:03d}", "item_id": pair["item_id"], "system": pair["system"],
            "set": pair["set"], "node": pair["node"], "reference": reference,
            "generated": winner["generated"] if winner else "", "loser": pair["generated"],
            "shot": how["shot"], "critic": how["critic"], "winner_index": winner["index"] if winner else "",
            "winner_credit": winner["credit"] if winner else "",
            # A verbatim copy of the losing item needs no judgement.
            "same_text": int(bool(winner) and normalise(winner["generated"]) == normalise(pair["generated"])),
        })

    seen_fields = ["pair_id", "item_id", "system", "set", "node", "reference", "generated"]
    drawn_fields = ["pair_id", "item_id", "loser", "shot", "critic", "winner_index", "winner_credit", "same_text"]
    to_judge = [row for row in rows if row["generated"] and not row["same_text"]]
    for name, fields, content in (("winner_pairs.csv", seen_fields, to_judge),
                                  ("winner_selection.csv", drawn_fields, rows)):
        with open(os.path.join(args.bench, name), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(content)
    print(json.dumps({"equivalent_items": len(rows), "to_judge": len(to_judge),
                      "reference_left_free": sum(not row["generated"] for row in rows),
                      "winner_is_verbatim_copy": sum(row["same_text"] for row in rows)}, indent=2))
    print(f"written: {args.bench}")


class BertEncoder:
    """Unit-norm embeddings of the default GoalEvaluator model, with a per-text cache."""

    def __init__(self, evaluator, preprocess, batch_size=32):
        self.evaluator = evaluator
        self.preprocess = preprocess
        self.batch_size = batch_size
        self.cache = {}

    def encode(self, texts):
        missing = [t for t in dict.fromkeys(texts) if t not in self.cache]
        self.evaluator.preprocess = self.preprocess
        for start in range(0, len(missing), self.batch_size):
            batch = missing[start:start + self.batch_size]
            emb = self.evaluator.encode_texts(batch).cpu().numpy().astype(np.float64)
            emb /= np.linalg.norm(emb, axis=1, keepdims=True)
            for text, vec in zip(batch, emb):
                self.cache[text] = vec.astype(np.float32)
        return np.stack([self.cache[t] for t in texts])


def to_credit(sim, form, low=None, high=None):
    return sim if form == "sum" else np.clip((sim - low) / (high - low), 0.0, 1.0)


def score(credit, matching):
    """Precision, recall, F1 and the credit earned by every generated item."""
    g, r = credit.shape
    if g == 0:
        return 0.0, 0.0, 0.0, np.zeros(0)
    earned = np.zeros(g)
    if matching == "free":
        earned = credit.max(axis=1)
        covered = credit.max(axis=0)
    else:
        # A reference that may pay twice is the same column offered twice. The second copy is
        # worth a hair less, so that among assignments of equal total credit the items spread
        # over more references and the scores do not depend on the order of the lists.
        slots = 1 if matching == "one" else 2
        offered = np.hstack([credit.astype(np.float64) * (1 - k * SLOT_DISCOUNT) for k in range(slots)])
        rows, cols = linear_sum_assignment(-offered)
        cols = cols % r
        earned[rows] = credit[rows, cols]
        # A cosine can be negative: a reference keeps the credit of its best item as it is.
        covered = np.full(r, -np.inf)
        np.maximum.at(covered, cols, earned[rows])
        covered[np.isinf(covered)] = 0.0
    precision, recall = earned.sum() / g, covered.sum() / r
    f1 = 2 * precision * recall / (precision + recall) if precision + recall != 0 else 0.0
    return float(precision), float(recall), float(f1), earned


def ahead(better, worse):
    """Probability that a value drawn from `better` exceeds one drawn from `worse`."""
    if not len(better) or not len(worse):
        return ""
    b, w = np.asarray(better)[:, None], np.asarray(worse)[None, :]
    return round(float(((b > w) + 0.5 * (b == w)).mean()), 4)


def grid(args):
    rng = random.Random(args.seed)
    ground_truth = {g["name"]: g for g in ALL_GROUNDTRUTHS}
    systems = list(ground_truth)
    configs = [(shot, critic) for shot in SHOTS for critic in CRITIC]
    replicas = [f"r{i}" for i in range(1, len(args.runs) + 1)]

    def read(directory, name):
        with open(os.path.join(directory, name), encoding="utf-8") as f:
            return list(csv.DictReader(f))

    lists = {}
    for replica, run_dir in zip(replicas, args.runs):
        for system in systems:
            for shot, critic in configs:
                path = os.path.join(run_dir.rstrip("/"), system, f"{system}_{shot}{CRITIC[critic]}.json")
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                for node in NODES:
                    lists[replica, system, shot, critic, node] = data[node]

    # Foreign goals are drawn once per list, so every combination is tested on the same additions.
    foreign = {}
    for (replica, system, shot, critic, node), preds in lists.items():
        pool = [goal for other in systems if other != system for goal in lists[replica, other, shot, critic, node]]
        foreign[replica, system, shot, critic, node] = rng.sample(pool, min(FOREIGN_PER_LIST, len(pool)))

    bench_pairs = {p["pair_id"]: p for p in read(args.bench, "pairs.csv")}
    bench_labels = {row["pair_id"]: row["label"] for row in read(args.bench, "labels.csv")}

    # Judged sample: where every item sits in its list, and the label it was given.
    sample_items = {row["item_id"]: row for row in read(args.sample, "items.csv")}
    sample_pairs = {row["pair_id"]: row["item_id"] for row in read(args.sample, "pairs.csv")}
    located = {}
    for row in read(args.sample, "selection.csv"):
        item = sample_items[sample_pairs[row["pair_id"]]]
        located[item["item_id"]] = ((args.replica, item["system"], row["shot"], row["critic"], item["node"]),
                                    int(row["index"]), item["label"])
    by_list = {}
    for key, index, label in located.values():
        by_list.setdefault(key, []).append((index, label))

    points, grid_rows, list_rows = {}, [], []
    encoders = {}
    for name in args.encoders:
        if name == "bert":
            # Actor names are embedded as they are, goals after preprocessing.
            evaluator = GoalEvaluator()
            raw, preprocessed = BertEncoder(evaluator, False), BertEncoder(evaluator, True)
            by_node = {node: preprocessed if node in GOAL_NODES else raw for node in NODES}
        else:
            by_node = dict.fromkeys(NODES, SentenceEncoder(name, device=args.device))
        encoders[name] = by_node

        def sim(preds, refs, node):
            # Double precision, so that a list and its exact copy score the same to the last digit.
            encoder = by_node[node]
            return encoder.encode(preds).astype(np.float64) @ encoder.encode(refs).astype(np.float64).T

        own_sim, cross_sim, foreign_sim = {}, {}, {}
        cross_matched = {node: [] for node in GOAL_NODES}
        for key, preds in lists.items():
            replica, system, shot, critic, node = key
            if not preds:
                continue
            own_sim[key] = sim(preds, ground_truth[system][node], node)
            cross_sim[key] = [sim(preds, ground_truth[other][node], node)
                              for other in systems if other != system]
            foreign_sim[key] = sim(foreign[key], ground_truth[system][node], node)
            if node in GOAL_NODES:
                for s in cross_sim[key]:
                    rows, cols = linear_sum_assignment(-s)
                    cross_matched[node].extend(s[rows, cols].tolist())

        bench = [(bench_pairs[pid]["node"], label,
                  float(sim([bench_pairs[pid]["generated"]], [bench_pairs[pid]["reference"]],
                            bench_pairs[pid]["node"])[0, 0]))
                 for pid, label in bench_labels.items()]

        def bench_cosines(nodes, label):
            return [c for node, lab, c in bench if node in nodes and lab == label]

        points[name] = {}
        for node in NODES:
            goal = node in GOAL_NODES
            low_source = cross_matched[node] if goal else bench_cosines(["actors"], "diverso")
            equivalent = bench_cosines(GOAL_NODES if goal else ["actors"], "equivalente")
            points[name][node] = {"low": {str(p): float(np.percentile(low_source, p)) for p in LOW_PERCENTILES},
                                  "high": float(np.percentile(equivalent, HIGH_PERCENTILE)),
                                  "low_n": len(low_source), "high_n": len(equivalent)}

        for node in NODES:
            high = points[name][node]["high"]
            for form in ("sum", "ramp"):
                lows = {p: points[name][node]["low"][str(p)] for p in LOW_PERCENTILES}
                for matching in MATCHINGS:
                    row = {"node": node, "encoder": name, "credit": form, "matching": matching,
                           "low": round(lows[MAIN_LOW], 4) if form == "ramp" else "",
                           "high": round(high, 4) if form == "ramp" else ""}
                    if form == "ramp" and high <= lows[MAIN_LOW]:
                        grid_rows.append({**row, "computable": 0})
                        continue

                    def f1_at(key, pct=MAIN_LOW, extra=None, matrix=None):
                        s = own_sim[key] if matrix is None else matrix
                        if extra is not None:
                            s = np.vstack([s, extra])
                        return score(to_credit(s, form, lows[pct], high), matching)

                    own, precision, recall, cross = {}, {}, {}, []
                    raised = rises = trials = 0
                    doubled_delta, earned_by_label = [], {label: [] for label in LABEL_ORDER}
                    for key, preds in lists.items():
                        if key[4] != node:
                            continue
                        if not preds:
                            own[key] = precision[key] = recall[key] = 0.0
                            continue
                        precision[key], recall[key], own[key], earned = f1_at(key)
                        cross.extend(f1_at(key, matrix=s)[2] for s in cross_sim[key])
                        for k in range(len(foreign[key])):
                            raised += f1_at(key, extra=foreign_sim[key][k:k + 1])[2] > own[key] + 1e-9
                            trials += 1
                        twice = f1_at(key, extra=own_sim[key])[2]
                        rises += twice > own[key] + 1e-9
                        doubled_delta.append(twice - own[key])
                        for index, label in by_list.get(key, []):
                            earned_by_label[label].append(float(earned[index]))
                        list_rows.append({"replica": key[0], "system": key[1], "shot": key[2], "critic": key[3],
                                          "node": node, "encoder": name, "credit": form, "matching": matching,
                                          "f1": round(own[key], 6), "precision": round(precision[key], 6),
                                          "recall": round(recall[key], 6)})

                    def config_means(pct):
                        return [float(np.mean([f1_at((r, s, shot, critic, node), pct)[2]
                                               if lists[r, s, shot, critic, node] else 0.0
                                               for r in replicas for s in systems])) for shot, critic in configs]

                    order_tau = ""
                    if form == "ramp" and all(high > lows[p] for p in LOW_PERCENTILES):
                        main = config_means(MAIN_LOW)
                        order_tau = round(float(min(kendalltau(main, config_means(p))[0]
                                                    for p in LOW_PERCENTILES if p != MAIN_LOW)), 4)
                    spreads = [np.std([own[r, system, shot, critic, node] for r in replicas], ddof=1)
                               for system in systems for shot, critic in configs]
                    f1_mean = float(np.mean(list(own.values())))
                    eq, part, diff = (earned_by_label[label] for label in LABEL_ORDER)
                    grid_rows.append({
                        **row, "computable": 1, "f1": round(f1_mean, 4),
                        "precision": round(float(np.mean(list(precision.values()))), 4),
                        "recall": round(float(np.mean(list(recall.values()))), 4),
                        "f1_cross": round(float(np.mean(cross)), 4),
                        "cross_over_own": round(float(np.mean(cross)) / f1_mean, 4),
                        "foreign_raises": round(raised / trials, 4),
                        "doubled_raises": round(rises / len(doubled_delta), 4),
                        "doubled_mean_change": round(float(np.mean(doubled_delta)), 4),
                        "agree_equivalent_over_partial": ahead(eq, part),
                        "agree_partial_over_different": ahead(part, diff),
                        "agree_equivalent_over_different": ahead(eq, diff),
                        "sample_mean_credit_equivalent": round(float(np.mean(eq)), 4) if eq else "",
                        "sample_mean_credit_partial": round(float(np.mean(part)), 4) if part else "",
                        "sample_mean_credit_different": round(float(np.mean(diff)), 4) if diff else "",
                        "noise_sd": round(float(np.mean(spreads)), 4),
                        "noise_sd_over_f1": round(float(np.mean(spreads)) / f1_mean, 4),
                        "order_tau_min": order_tau,
                    })
                    print(" | ".join(f"{k}={v}" for k, v in grid_rows[-1].items()), flush=True)

    # Near copies: an item whose cosine with an earlier item of the same list reaches the high point.
    copy_rows, copy_check = [], {}
    if args.copy_encoder in encoders:
        encoder = encoders[args.copy_encoder][GOAL_NODES[0]]
        for node in GOAL_NODES:
            high = points[args.copy_encoder][node]["high"]
            for system in [None] + systems:
                copies = total = 0
                for key, preds in lists.items():
                    if key[4] != node or not preds or (system and key[1] != system):
                        continue
                    emb = encoder.encode(preds)
                    earlier = np.tril(emb @ emb.T, k=-1)
                    copies += int((earlier.max(axis=1) >= high).sum())
                    total += len(preds)
                copy_rows.append({"node": node, "system": system or "all", "generated": total, "copies": copies,
                                  "share": round(copies / total, 4)})
        winner_file = os.path.join(args.sample, "winner_pairs.csv")
        if os.path.exists(winner_file):
            losers = {row["pair_id"]: row["loser"] for row in read(args.sample, "winner_selection.csv")}
            judged = {row["pair_id"]: row["suggestion"] for row in read(args.sample, "winner_labels.csv")}
            for pair in read(args.sample, "winner_pairs.csv"):
                emb = encoder.encode([pair["generated"], losers[pair["pair_id"]]])
                called = float(emb[0] @ emb[1]) >= points[args.copy_encoder][pair["node"]]["high"]
                cell = ("copy" if judged[pair["pair_id"]] == "equivalente" else "not_copy",
                        "rule_says_copy" if called else "rule_says_not")
                copy_check["/".join(cell)] = copy_check.get("/".join(cell), 0) + 1

    os.makedirs(args.out, exist_ok=True)
    fields = list(max(grid_rows, key=len))
    for name, rows, header in (("grid.csv", grid_rows, fields), ("lists.csv", list_rows, list(list_rows[0])),
                               ("copies.csv", copy_rows, list(copy_rows[0]) if copy_rows else [])):
        if rows:
            with open(os.path.join(args.out, name), "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=header, restval="")
                writer.writeheader()
                writer.writerows(rows)
    with open(os.path.join(args.out, "points.json"), "w", encoding="utf-8") as f:
        json.dump({"runs": args.runs, "seed": args.seed, "bench": args.bench, "sample": args.sample,
                   "sample_replica": args.replica, "encoders": {n: ENCODERS.get(n, "bert-base-uncased, preprocessed")
                                                                for n in args.encoders},
                   "low_percentiles": LOW_PERCENTILES, "main_low": MAIN_LOW, "high_percentile": HIGH_PERCENTILE,
                   "foreign_per_list": FOREIGN_PER_LIST, "points": points,
                   "copy_encoder": args.copy_encoder, "copy_rule_on_judged_pairs": copy_check}, f, indent=2)
    print(json.dumps({"points": points, "copy_rule_on_judged_pairs": copy_check}, indent=2))
    print(f"written: {args.out}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    p_census = commands.add_parser("census", help="score every list and describe the zero-credit items")
    p_census.add_argument("--runs", nargs="+", required=True, help="replica directories of the same experiment")
    p_census.add_argument("--out", required=True)
    p_census.add_argument("--encoder", default="minilm")
    p_census.add_argument("--device", default=None)
    p_census.set_defaults(func=census)
    p_sample = commands.add_parser("sample", help="draw zero-credit items with their closest references")
    p_sample.add_argument("--census", required=True, help="output directory of the census command")
    p_sample.add_argument("--out", required=True)
    p_sample.add_argument("--replica", default="r1")
    p_sample.add_argument("--nodes", nargs="+", default=["highLevelGoals", "lowLevelGoals"])
    p_sample.add_argument("--exclude", nargs="+", metavar="BENCH",
                          help="bench directories whose generated items are left out; their judged pairs "
                               "also check the shortlist")
    p_sample.add_argument("--seed", type=int, default=20261013)
    p_sample.add_argument("--device", default=None)
    p_sample.set_defaults(func=sample)
    p_winners = commands.add_parser("winners", help="pair each equivalent reference with the item that took it")
    p_winners.add_argument("--census", required=True, help="output directory of the census command")
    p_winners.add_argument("--bench", required=True, help="bench directory written by the sample command")
    p_winners.add_argument("--replica", default="r1")
    p_winners.set_defaults(func=winners)
    p_grid = commands.add_parser("grid", help="score every list under every encoder, credit and matching")
    p_grid.add_argument("--runs", nargs="+", required=True, help="replica directories of the same experiment")
    p_grid.add_argument("--bench", required=True, help="pair bench with pairs.csv and labels.csv, for the ramp")
    p_grid.add_argument("--sample", required=True, help="bench written by the sample command, with items.csv")
    p_grid.add_argument("--out", required=True)
    p_grid.add_argument("--encoders", nargs="+", default=["bert", "minilm"])
    p_grid.add_argument("--copy-encoder", default="minilm")
    p_grid.add_argument("--replica", default="r1", help="replica the judged sample was drawn from")
    p_grid.add_argument("--seed", type=int, default=20261013)
    p_grid.add_argument("--device", default=None)
    p_grid.set_defaults(func=grid)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
