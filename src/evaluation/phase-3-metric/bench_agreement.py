"""Agreement between the judged pairs and the value two metrics give them.

Reads the bench of hand-judged pairs and the judged sample of zero-credit goals, embeds every
pair with the production BERT and with two sentence encoders, and writes:
  pairs.csv         one row per bench pair: label, cosine per encoder, ramp credit with the
                    points in use and with the points derived without the system of the pair
  agreement.csv     probability that a pair with the higher label is worth more than one with
                    the lower label (ties count one half), per node, subset of pairs and value;
                    for the two credits also their difference with a bootstrap interval
  points_check.csv  share of equivalent and different pairs below and above the ramp points
  partial.csv       ramp credit by label on the bench and on the judged sample: mean, share at
                    zero, share at full credit, and the same three probabilities

The current metric gives a pair its BERT cosine (goals preprocessed, actors as they are). The
new metric gives it the ramp credit on the MiniLM cosine. No model API is called.

Bench pairs listed in review.csv, when the bench has one, were labelled by agents and not by
the human judge. They are reported as a subset of their own and never enter the ramp points
recomputed without one system, as they did not enter the points in use.

Run from the repository root:
`python src/evaluation/phase-3-metric/bench_agreement.py --bench <bench dir> --sample <sample dir> --out <dir>`
"""
import argparse
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "notebook"))
from src.diagnostics.metric_diagnostics import Embedder, PRODUCTION  # noqa: E402
from src.evaluation.goal_evaluator import RAMPS, GoalEvaluator  # noqa: E402
from system_sets import SYSTEM_SETS  # noqa: E402

NODES = ["actors", "highLevelGoals", "lowLevelGoals"]
GOAL_NODES = ["highLevelGoals", "lowLevelGoals"]
LABELS = ["equivalente", "parziale", "diverso"]
CONTRASTS = [("equivalente", "diverso"), ("equivalente", "parziale"), ("parziale", "diverso")]
SENTENCE_ENCODERS = ["minilm", "mpnet"]
NEW_METRIC_ENCODER = "minilm"
LOW_PERCENTILE = 95
HIGH_PERCENTILE = 25


def read(directory, name):
    with open(os.path.join(directory, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})


def ahead(better, worse):
    """Probability that a value drawn from `better` exceeds one drawn from `worse`."""
    b, w = np.asarray(better)[:, None], np.asarray(worse)[None, :]
    return float(((b > w) + 0.5 * (b == w)).mean())


def ramp(cosine, low, high):
    # Without a high point above the low one there is no ramp, only the step at the low point.
    if high <= low:
        return float(cosine >= low)
    return float(np.clip((cosine - low) / (high - low), 0.0, 1.0))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bench", required=True, help="bench directory with pairs.csv and labels.csv")
    parser.add_argument("--sample", required=True, help="judged sample directory with pairs.csv and labels.csv")
    parser.add_argument("--out", required=True)
    parser.add_argument("--boots", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261013)
    parser.add_argument("--device", default=None, help="device of the sentence encoders (default: cuda if available)")
    args = parser.parse_args()

    bert = GoalEvaluator(preprocess=True)
    embedders = {name: Embedder(name, bert, args.device)
                 for name in list(dict.fromkeys(PRODUCTION.values())) + SENTENCE_ENCODERS}

    def cosine(name, generated, reference):
        return float(embedders[name].sim([generated], [reference])[0, 0])

    labels = {row["pair_id"]: row for row in read(args.bench, "labels.csv")}
    by_agents = set()
    if os.path.exists(os.path.join(args.bench, "review.csv")):
        by_agents = {row["pair_id"] for row in read(args.bench, "review.csv")}
    bench = []
    for pair in read(args.bench, "pairs.csv"):
        if pair["pair_id"] not in labels:
            continue
        judged = labels[pair["pair_id"]]
        row = {"pair_id": pair["pair_id"], "system": pair["system"], "set": pair["set"], "node": pair["node"],
               "label": judged["label"], "hint_seen": judged["hint_seen"] == "1",
               "judge": "agents" if pair["pair_id"] in by_agents else "user",
               "bert": cosine(PRODUCTION[pair["node"]], pair["generated"], pair["reference"])}
        for name in SENTENCE_ENCODERS:
            row[name] = cosine(name, pair["generated"], pair["reference"])
        bench.append(row)

    def points_without(node, system):
        """Ramp points of a node with the bench-derived ones recomputed without one system."""
        kept = [b for b in bench if b["system"] != system and b["judge"] == "user"]
        high_nodes = GOAL_NODES if node in GOAL_NODES else ["actors"]
        equivalent = [b[NEW_METRIC_ENCODER] for b in kept if b["node"] in high_nodes and b["label"] == "equivalente"]
        high = float(np.percentile(equivalent, HIGH_PERCENTILE))
        if node in GOAL_NODES:
            # The low point of the goals comes from cross-system pairs, not from the bench.
            return RAMPS[NEW_METRIC_ENCODER][node][0], high
        different = [b[NEW_METRIC_ENCODER] for b in kept if b["node"] == "actors" and b["label"] == "diverso"]
        return float(np.percentile(different, LOW_PERCENTILE)), high

    for row in bench:
        low, high = RAMPS[NEW_METRIC_ENCODER][row["node"]]
        row["low"], row["high"] = low, high
        row["ramp"] = ramp(row[NEW_METRIC_ENCODER], low, high)
        row["low_loso"], row["high_loso"] = points_without(row["node"], row["system"])
        row["ramp_loso"] = ramp(row[NEW_METRIC_ENCODER], row["low_loso"], row["high_loso"])

    os.makedirs(args.out, exist_ok=True)
    write_csv(os.path.join(args.out, "pairs.csv"), bench)

    def by_label(rows, value):
        return {label: np.array([r[value] for r in rows if r["label"] == label]) for label in LABELS}

    # Agreement: three similarities and two credits, on several subsets of the pairs.
    subsets = {"all": lambda r: True, "judged_by_user": lambda r: r["judge"] == "user",
               "judged_by_agents": lambda r: r["judge"] == "agents",
               "dev": lambda r: r["set"] == "dev", "holdout": lambda r: r["set"] != "dev",
               "hint_not_seen": lambda r: r["judge"] == "user" and not r["hint_seen"]}
    with_interval = ["all", "judged_by_user", "judged_by_agents"]
    # One generator per subset, so that adding a subset leaves the intervals of the others as they were.
    rngs = {name: np.random.default_rng(args.seed if i == 0 else [args.seed, i])
            for i, name in enumerate(with_interval)}
    values = [("cosine", "bert"), ("cosine", "minilm"), ("cosine", "mpnet"),
              ("credit_current", "bert"), ("credit_new_metric", "ramp"), ("credit_new_metric_loso", "ramp_loso")]
    agreement = []
    for node in NODES:
        for subset, keep in subsets.items():
            rows = [r for r in bench if r["node"] == node and keep(r)]
            for kind, value in values:
                groups = by_label(rows, value)
                for better, worse in CONTRASTS:
                    out = {"node": node, "subset": subset, "kind": kind, "value": value,
                           "contrast": f"{better}>{worse}", "n_better": len(groups[better]),
                           "n_worse": len(groups[worse]), "probability": "", "minus_current": "",
                           "ci_low": "", "ci_high": ""}
                    if len(groups[better]) and len(groups[worse]):
                        out["probability"] = ahead(groups[better], groups[worse])
                    if subset in with_interval and kind.startswith("credit_new_metric") and out["probability"] != "":
                        current = by_label(rows, "bert")
                        out["minus_current"] = out["probability"] - ahead(current[better], current[worse])
                        diffs = []
                        for _ in range(args.boots):
                            # Pairs are redrawn inside each label, the same draw for both credits.
                            i = rngs[subset].integers(0, len(groups[better]), len(groups[better]))
                            j = rngs[subset].integers(0, len(groups[worse]), len(groups[worse]))
                            diffs.append(ahead(groups[better][i], groups[worse][j])
                                         - ahead(current[better][i], current[worse][j]))
                        out["ci_low"], out["ci_high"] = (float(x) for x in np.percentile(diffs, [2.5, 97.5]))
                    agreement.append(out)
    write_csv(os.path.join(args.out, "agreement.csv"), agreement)

    # Where the labels fall with respect to the two ramp points.
    checks = []
    point_sets = (("in_use", "low", "high"), ("leave_one_system_out", "low_loso", "high_loso"))
    for node in NODES:
        for subset in with_interval:
            for name, low_key, high_key in point_sets:
                for label in LABELS:
                    rows = [r for r in bench if r["node"] == node and r["label"] == label and subsets[subset](r)]
                    if not rows:
                        continue
                    cos = np.array([r[NEW_METRIC_ENCODER] for r in rows])
                    low = np.array([r[low_key] for r in rows])
                    high = np.array([r[high_key] for r in rows])
                    checks.append({"node": node, "subset": subset, "points": name, "label": label, "n": len(rows),
                                   "share_below_low": float((cos < low).mean()),
                                   "share_between": float(((cos >= low) & (cos < high)).mean()),
                                   "share_at_or_above_high": float((cos >= high).mean()),
                                   "min_cosine": float(cos.min()), "max_cosine": float(cos.max())})
    write_csv(os.path.join(args.out, "points_check.csv"), checks)

    # Ramp credit by label on the two sets of judgements.
    sample_labels = {row["pair_id"]: row["label"] for row in read(args.sample, "labels.csv")}
    sample = []
    for pair in read(args.sample, "pairs.csv"):
        low, high = RAMPS[NEW_METRIC_ENCODER][pair["node"]]
        sample.append({"node": pair["node"], "label": sample_labels[pair["pair_id"]],
                       "ramp": ramp(cosine(NEW_METRIC_ENCODER, pair["generated"], pair["reference"]), low, high)})
    partial = []
    for source, rows_all in (("bench", [b for b in bench if b["judge"] == "user"]), ("sample", sample)):
        for node in GOAL_NODES:
            groups = by_label([r for r in rows_all if r["node"] == node], "ramp")
            for label in LABELS:
                credit = groups[label]
                partial.append({"source": source, "node": node, "row": label, "n": len(credit),
                                "mean_credit": float(credit.mean()), "share_zero": float((credit == 0).mean()),
                                "share_full": float((credit == 1).mean()), "probability": ""})
            for better, worse in CONTRASTS:
                partial.append({"source": source, "node": node, "row": f"{better}>{worse}", "n": "",
                                "mean_credit": "", "share_zero": "", "share_full": "",
                                "probability": ahead(groups[better], groups[worse])})
    write_csv(os.path.join(args.out, "partial.csv"), partial)
    print(f"bench pairs: {len(bench)}, sample pairs: {len(sample)}")
    print(f"written: {args.out}")


if __name__ == "__main__":
    main()
