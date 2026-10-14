"""Noise tables from identical replicas of the same experiment matrix.

Reads the per-system score CSVs and the output JSONs of each replica and writes:
  cells.csv        one row per (system, shot, critic, node) with the three replica scores,
                   their range and whether the generated lists are identical
  oscillation.csv  median and max range of the cells, grouped along several axes
  null_shift.csv   absolute F1 shift between pairs of identical replicas
  comparisons.csv  paired mean differences between conditions (observed) and between
                   replicas of the same condition (null)
"""
import argparse
import csv
import itertools
import json
import os
import statistics
import sys

SHOTS = ["ZERO_SHOT", "ONE_SHOT", "FEW_SHOT"]
CRITIC = {"ON": "", "OFF": "_noLlama"}
NODES = {"actors": "actor", "highLevelGoals": "hl", "lowLevelGoals": "ll"}
METRICS = ["precision", "recall", "f1"]


def read_scores(run_dir, prefix, shot, suffix):
    """Return {system: {metric: value}} from one aggregated score CSV."""
    scores = {}
    with open(os.path.join(run_dir, f"{prefix}_{shot}{suffix}.csv")) as f:
        next(f)
        for line in f:
            parts = [p.strip() for p in line.split(";")]
            if parts[0] == "Weighted averages":
                continue
            # Column order in the file is recall, precision, f1.
            scores[parts[0]] = {"recall": float(parts[1]), "precision": float(parts[2]), "f1": float(parts[3])}
    return scores


def read_list(run_dir, system, shot, suffix, node):
    with open(os.path.join(run_dir, system, f"{system}_{shot}{suffix}.json")) as f:
        return frozenset(json.load(f)[node])


def identity_label(lists):
    distinct = len(set(lists))
    return {1: "all_equal", 2: "two_equal"}.get(distinct, "all_different")


def summarize(values):
    return {"n": len(values), "median": statistics.median(values), "mean": statistics.fmean(values), "max": max(values)}


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", nargs="+", required=True, help="replica output directories")
    parser.add_argument("--out", required=True)
    parser.add_argument("--notebook-dir", default="notebook")
    args = parser.parse_args()

    sys.path.insert(0, args.notebook_dir)
    from system_sets import SYSTEM_SETS

    systems = SYSTEM_SETS["all"]
    subset = {s: ("dev" if s in SYSTEM_SETS["dev"] else "holdout") for s in systems}
    n_rep = len(args.runs)
    pairs = list(itertools.combinations(range(n_rep), 2))

    # score[(system, shot, critic, node)][metric] -> list of values, one per replica
    score, cells = {}, []
    for shot, (critic, suffix), (node, prefix) in itertools.product(SHOTS, CRITIC.items(), NODES.items()):
        per_run = [read_scores(run, prefix, shot, suffix) for run in args.runs]
        for system in systems:
            key = (system, shot, critic, node)
            score[key] = {m: [r[system][m] for r in per_run] for m in METRICS}
            lists = [read_list(run, system, shot, suffix, node) for run in args.runs]
            row = {"system": system, "set": subset[system], "shot": shot, "critic": critic, "node": node,
                   "identity": identity_label(lists)}
            for i, lst in enumerate(lists):
                row[f"n_items_r{i + 1}"] = len(lst)
            for m in METRICS:
                for i, v in enumerate(score[key][m]):
                    row[f"{m}_r{i + 1}"] = v
                row[f"{m}_range"] = max(score[key][m]) - min(score[key][m])
            cells.append(row)
    os.makedirs(args.out, exist_ok=True)
    write_csv(os.path.join(args.out, "cells.csv"), cells)

    osc = []
    for axes in (["node"], ["node", "critic"], ["node", "critic", "shot"], ["node", "set"], ["node", "system"],
                 ["node", "critic", "system"]):
        groups = {}
        for row in cells:
            groups.setdefault(tuple(row[a] for a in axes), []).append(row)
        for group_key, rows in groups.items():
            out = {"grouping": "+".join(axes), "group": " | ".join(group_key), "n_cells": len(rows)}
            for label in ("all_equal", "two_equal", "all_different"):
                out[label] = sum(r["identity"] == label for r in rows)
            for m in METRICS:
                s = summarize([r[f"{m}_range"] for r in rows])
                out[f"{m}_range_median"], out[f"{m}_range_max"] = s["median"], s["max"]
            osc.append(out)
    write_csv(os.path.join(args.out, "oscillation.csv"), osc)

    shift = []
    for axes in (["node"], ["node", "set"], ["node", "critic"], ["node", "critic", "set"]):
        groups = {}
        for row in cells:
            key = (row["system"], row["shot"], row["critic"], row["node"])
            for a, b in pairs:
                groups.setdefault(tuple(row[x] for x in axes), []).append(abs(score[key]["f1"][a] - score[key]["f1"][b]))
        for group_key, values in groups.items():
            values.sort()
            s = summarize(values)
            shift.append({"grouping": "+".join(axes), "group": " | ".join(group_key), "n_pairs": s["n"],
                          "abs_f1_shift_median": s["median"], "abs_f1_shift_mean": s["mean"],
                          "abs_f1_shift_p90": values[int(0.9 * (len(values) - 1))], "abs_f1_shift_max": s["max"]})
    write_csv(os.path.join(args.out, "null_shift.csv"), shift)

    def paired(cond_a, rep_a, cond_b, rep_b, node, names):
        """Mean over systems of F1(cond_a, rep_a) - F1(cond_b, rep_b), plus sign counts."""
        diffs = [score[(s, *cond_a, node)]["f1"][rep_a] - score[(s, *cond_b, node)]["f1"][rep_b] for s in names]
        return {"mean_diff": statistics.fmean(diffs), "n_systems": len(diffs),
                "n_positive": sum(d > 0 for d in diffs), "n_negative": sum(d < 0 for d in diffs),
                "n_zero": sum(d == 0 for d in diffs)}

    contrasts = [(f"critic ON-OFF @ {shot}", (shot, "ON"), (shot, "OFF")) for shot in SHOTS]
    for critic in CRITIC:
        for a, b in itertools.combinations(SHOTS, 2):
            contrasts.append((f"{b}-{a} @ critic {critic}", (b, critic), (a, critic)))
    conditions = list(itertools.product(SHOTS, CRITIC))

    comp = []
    for set_name in ("all", "dev", "holdout"):
        names = SYSTEM_SETS[set_name]
        for node in NODES:
            for label, cond_a, cond_b in contrasts:
                for rep in range(n_rep):
                    comp.append({"kind": "observed", "set": set_name, "node": node, "contrast": label,
                                 "replicas": f"r{rep + 1}", **paired(cond_a, rep, cond_b, rep, node, names)})
            for cond in conditions:
                for a, b in pairs:
                    comp.append({"kind": "null", "set": set_name, "node": node,
                                 "contrast": f"same condition {cond[0]} critic {cond[1]}",
                                 "replicas": f"r{b + 1}-r{a + 1}", **paired(cond, b, cond, a, node, names)})
    write_csv(os.path.join(args.out, "comparisons.csv"), comp)


if __name__ == "__main__":
    main()
