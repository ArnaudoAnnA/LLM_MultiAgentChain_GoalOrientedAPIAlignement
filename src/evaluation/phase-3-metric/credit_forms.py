"""Compare three ways of turning the cosine of a matched pair into credit.

  sum        the credit is the cosine itself
  threshold  0 below the low point, 1 from it upwards
  ramp       0 below the low point, 1 from the high point upwards, linear in between

For every form the pairs are matched one-to-one on the credit matrix, so that the matching
maximises the credit actually counted, and F1 = 2 * credit / (generated + references).

Low and high points:
  goals    low = percentile of the cosine of the pairs matched between a generated list and the
           ground truth of another system; high = percentile of the cosine of the bench pairs
           labelled equivalent, high- and low-level goals pooled
  actors   both from the bench: low from the pairs labelled different, high from the equivalent

Four tests, per node and per form:
  cross      F1 of a list against the ground truth of the other systems
  foreign    how often one generated goal of another system, appended to the list, raises F1
  noise      standard deviation of F1 across replicas, same system and configuration
  order      whether the ranking of the configurations survives a change of the low point

Files written in the output directory:
  points.json        low and high points, with the leave-one-system-out range of the high ones
  tests.csv          one row per (node, form, low percentile) with the four tests
  bench_credit.csv   mean credit given to the bench pairs, by label
  lists.csv          F1 of every list under every form

No model API is called. Run from the repository root:
`python src/evaluation/phase-3-metric/credit_forms.py --runs <replica dirs> --bench <bench dir> --out <dir>`
"""
import argparse
import csv
import itertools
import json
import os
import random
import sys

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import kendalltau

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "notebook"))
from src.evaluation.goal_evaluator import ENCODERS, SentenceEncoder  # noqa: E402
from groundtruth import ALL_GROUNDTRUTHS  # noqa: E402

SHOTS = ["ZERO_SHOT", "ONE_SHOT", "FEW_SHOT"]
CRITIC = {"ON": "", "OFF": "_noLlama"}
NODES = ["actors", "highLevelGoals", "lowLevelGoals"]
GOAL_NODES = ["highLevelGoals", "lowLevelGoals"]
LOW_PERCENTILES = [90, 95, 97]
MAIN_LOW = 95
HIGH_PERCENTILE = 25
# Foreign goals tried per list: a fixed-size random sample keeps the test affordable.
FOREIGN_PER_LIST = 30


def credit(sim, form, low=None, high=None):
    if form == "sum":
        return sim
    if form == "threshold":
        return (sim >= low).astype(float)
    return np.clip((sim - low) / (high - low), 0.0, 1.0)


def f1_of(credit_matrix):
    g, r = credit_matrix.shape
    if g == 0:
        return 0.0
    rows, cols = linear_sum_assignment(-credit_matrix)
    return 2 * credit_matrix[rows, cols].sum() / (g + r)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", required=True, help="replica directories of the same experiment")
    parser.add_argument("--bench", required=True, help="bench directory with pairs.csv and labels.csv")
    parser.add_argument("--out", required=True)
    parser.add_argument("--encoder", default="minilm")
    parser.add_argument("--seed", type=int, default=20261013)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    encoder = SentenceEncoder(args.encoder)
    ground_truth = {g["name"]: g for g in ALL_GROUNDTRUTHS}
    systems = list(ground_truth)
    configs = [(shot, critic) for shot in SHOTS for critic in CRITIC]
    replicas = [f"r{i}" for i in range(1, len(args.runs) + 1)]

    lists = {}
    for replica, run_dir in zip(replicas, args.runs):
        for system in systems:
            for shot, critic in configs:
                path = os.path.join(run_dir.rstrip("/"), system, f"{system}_{shot}{CRITIC[critic]}.json")
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                for node in NODES:
                    lists[replica, system, shot, critic, node] = data[node]

    def sim(preds, refs):
        return encoder.encode(preds) @ encoder.encode(refs).T

    # Bench: cosine and label of every judged pair.
    with open(os.path.join(args.bench, "pairs.csv"), encoding="utf-8") as f:
        pairs = {p["pair_id"]: p for p in csv.DictReader(f)}
    with open(os.path.join(args.bench, "labels.csv"), encoding="utf-8") as f:
        labels = {row["pair_id"]: row["label"] for row in csv.DictReader(f)}
    bench = []
    for pair_id, label in labels.items():
        pair = pairs[pair_id]
        cosine = float(sim([pair["generated"]], [pair["reference"]])[0, 0])
        bench.append({"pair_id": pair_id, "node": pair["node"], "system": pair["system"], "label": label,
                      "cosine": cosine})

    def bench_cosines(nodes, label, without=None):
        return [b["cosine"] for b in bench if b["node"] in nodes and b["label"] == label and b["system"] != without]

    # Cosine of the pairs matched against the ground truth of another system.
    cross_matched = {node: [] for node in GOAL_NODES}
    for (replica, system, shot, critic, node), preds in lists.items():
        if node not in GOAL_NODES or not preds:
            continue
        for other in systems:
            if other != system:
                s = sim(preds, ground_truth[other][node])
                rows, cols = linear_sum_assignment(-s)
                cross_matched[node].extend(s[rows, cols].tolist())

    points = {}
    for node in NODES:
        goal = node in GOAL_NODES
        high_nodes = GOAL_NODES if goal else ["actors"]
        low_source = cross_matched[node] if goal else bench_cosines(["actors"], "diverso")
        equivalent = bench_cosines(high_nodes, "equivalente")
        left_out = [np.percentile(bench_cosines(high_nodes, "equivalente", without=s), HIGH_PERCENTILE)
                    for s in systems]
        points[node] = {
            "low": {str(p): float(np.percentile(low_source, p)) for p in LOW_PERCENTILES},
            "low_source": "cross-system matched pairs" if goal else "bench pairs labelled diverso",
            "low_n": len(low_source),
            "high": float(np.percentile(equivalent, HIGH_PERCENTILE)),
            "high_n": len(equivalent),
            "high_leave_one_system_out": [float(min(left_out)), float(max(left_out))],
        }

    variants = [("sum", None)]
    variants += [(form, p) for form in ("threshold", "ramp") for p in LOW_PERCENTILES]

    def credit_for(node, form, pct):
        low = points[node]["low"][str(pct)] if pct else None
        high = points[node]["high"]
        if form == "ramp" and high <= low:
            return None
        return lambda s: credit(s, form, low, high)

    list_rows, test_rows = [], []
    config_means = {}
    for node in NODES:
        # Foreign goals are drawn once per list, so every form is tested on the same additions.
        foreign = {}
        for (replica, system, shot, critic, n), preds in lists.items():
            if n != node:
                continue
            pool = [goal for other in systems if other != system
                    for goal in lists[replica, other, shot, critic, node]]
            foreign[replica, system, shot, critic] = rng.sample(pool, min(FOREIGN_PER_LIST, len(pool)))

        for form, pct in variants:
            to_credit = credit_for(node, form, pct)
            if to_credit is None:
                continue
            own, cross = {}, []
            raised = {"g_lt_r": [0, 0], "g_ge_r": [0, 0]}
            for (replica, system, shot, critic, n), preds in lists.items():
                if n != node:
                    continue
                refs = ground_truth[system][node]
                key = (replica, system, shot, critic)
                if not preds:
                    own[key] = 0.0
                    continue
                s = sim(preds, refs)
                own[key] = f1_of(to_credit(s))
                cross.extend(f1_of(to_credit(sim(preds, ground_truth[other][node])))
                             for other in systems if other != system)
                regime = "g_lt_r" if len(preds) < len(refs) else "g_ge_r"
                extra = sim(foreign[key], refs)
                for k in range(len(foreign[key])):
                    raised[regime][0] += f1_of(to_credit(np.vstack([s, extra[k:k + 1]]))) > own[key] + 1e-9
                    raised[regime][1] += 1
                list_rows.append({"replica": replica, "system": system, "shot": shot, "critic": critic,
                                  "node": node, "form": form, "low_percentile": pct or "",
                                  "f1": round(own[key], 6)})

            spreads = [np.std([own[r, system, shot, critic] for r in replicas], ddof=1)
                       for system in systems for shot, critic in configs]
            f1_mean = float(np.mean(list(own.values())))
            config_means[node, form, pct] = [
                float(np.mean([own[r, s, shot, critic] for r in replicas for s in systems]))
                for shot, critic in configs]
            n_raised = raised["g_lt_r"][0] + raised["g_ge_r"][0]
            n_trials = raised["g_lt_r"][1] + raised["g_ge_r"][1]
            test_rows.append({
                "node": node, "form": form, "low_percentile": pct or "",
                "low": "" if pct is None else round(points[node]["low"][str(pct)], 4),
                "high": round(points[node]["high"], 4) if form == "ramp" else "",
                "f1_own": round(f1_mean, 4), "f1_cross": round(float(np.mean(cross)), 4),
                "cross_over_own": round(float(np.mean(cross)) / f1_mean, 4),
                "foreign_raises": round(n_raised / n_trials, 4),
                "foreign_raises_g_lt_r": (round(raised["g_lt_r"][0] / raised["g_lt_r"][1], 4)
                                          if raised["g_lt_r"][1] else ""),
                "foreign_raises_g_ge_r": (round(raised["g_ge_r"][0] / raised["g_ge_r"][1], 4)
                                          if raised["g_ge_r"][1] else ""),
                "noise_sd": round(float(np.mean(spreads)), 4),
                "noise_sd_over_f1": round(float(np.mean(spreads)) / f1_mean, 4),
            })

    # Ranking of the configurations: agreement between the main low point and its neighbours.
    for row in test_rows:
        node, form = row["node"], row["form"]
        row["order_tau_min"] = row["order_same"] = ""
        if form == "sum" or row["low_percentile"] != MAIN_LOW or (node, form, MAIN_LOW) not in config_means:
            continue
        taus = [kendalltau(config_means[node, form, MAIN_LOW], config_means[node, form, p])[0]
                for p in LOW_PERCENTILES if p != MAIN_LOW]
        row["order_tau_min"] = round(float(min(taus)), 4)
        row["order_same"] = int(min(taus) > 1 - 1e-9)

    bench_rows = []
    for node in NODES:
        for form, pct in variants:
            to_credit = credit_for(node, form, pct)
            if to_credit is None:
                continue
            for label in ("equivalente", "parziale", "diverso"):
                cosines = np.array(bench_cosines([node], label))
                if cosines.size:
                    given = to_credit(cosines)
                    bench_rows.append({"node": node, "form": form, "low_percentile": pct or "", "label": label,
                                       "n": cosines.size, "mean_credit": round(float(given.mean()), 4),
                                       "share_zero": round(float((given == 0).mean()), 4),
                                       "share_full": round(float((given >= 1).mean()), 4)})

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "points.json"), "w", encoding="utf-8") as f:
        json.dump({"encoder": {args.encoder: ENCODERS[args.encoder]}, "runs": args.runs, "seed": args.seed,
                   "low_percentiles": LOW_PERCENTILES, "high_percentile": HIGH_PERCENTILE,
                   "foreign_per_list": FOREIGN_PER_LIST, "points": points}, f, indent=2)
    for name, rows in (("tests.csv", test_rows), ("bench_credit.csv", bench_rows), ("lists.csv", list_rows)):
        with open(os.path.join(args.out, name), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    print(json.dumps(points, indent=2))
    for row in test_rows:
        print(" | ".join(f"{k}={v}" for k, v in row.items()))
    print(f"written: {args.out}")


if __name__ == "__main__":
    main()
