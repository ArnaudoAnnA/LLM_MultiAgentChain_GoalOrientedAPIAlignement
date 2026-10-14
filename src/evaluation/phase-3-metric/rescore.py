"""Re-score generated lists already on disk and report what each score is made of.

Reads the output JSONs of one or more replicas and the ground truth, recomputes the soft
precision, recall and F1 with the chosen metric, and writes:
  lists.csv        one row per (replica, system, shot, critic, node) with the score, the two
                   list lengths, their ratio, the F1 ceiling set by the lengths alone and, for
                   the production metric, the mean cosine of the matched pairs
  aggregates.csv   one row per (replica, shot, critic, node, system set) with the mean of the
                   per-system F1 next to the F1 of the weighted precision and recall
  scores/<replica>/<prefix>_<shot><suffix>.csv
                   the same scores in the layout of the per-run score CSVs

With --metric production (default) the scores are those of the metric saved with the runs and
are checked against the run CSVs. With --metric new_metric every node is scored with a sentence
encoder, the ramp credit of RAMPS and the matching of MAX_PER_REF.

An empty generated list scores 0 instead of raising. No model API is called.

Run from the repository root:
`python src/evaluation/phase-3-metric/rescore.py --runs <replica dirs> --out <dir> [--metric new_metric]`
"""
import argparse
import csv
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "notebook"))
from src.diagnostics.metric_diagnostics import Embedder, PRODUCTION, read_csv_f1, soft_scores  # noqa: E402
from src.evaluation.goal_evaluator import MAX_PER_REF, RAMPS, GoalEvaluator  # noqa: E402
from groundtruth import ALL_GROUNDTRUTHS  # noqa: E402
from system_sets import SYSTEM_SETS  # noqa: E402

SHOTS = ["ZERO_SHOT", "ONE_SHOT", "FEW_SHOT"]
CRITIC = {"ON": "", "OFF": "_noLlama"}
NODES = {"actors": "actor", "highLevelGoals": "hl", "lowLevelGoals": "ll"}
# Largest accepted gap between a recomputed F1 and the one stored with the run.
CSV_TOLERANCE = 1e-5
NEW_METRIC_ENCODER = "minilm"


def ceiling_of(g, r, max_per_ref=1):
    """Highest F1 the two lengths allow when every matched pair earns full credit."""
    if not g or not r:
        return 0.0
    p, rec = min(g, max_per_ref * r) / g, min(g, r) / r
    return 2 * p * rec / (p + rec)


def score_list(embedder, preds, refs):
    """Soft scores of one generated list plus the quantities that explain them."""
    g, r = len(preds), len(refs)
    base = {"g": g, "r": r, "g_over_r": g / r if r else float("nan"), "ceiling": ceiling_of(g, r)}
    if not g or not r:
        return {**base, "precision": 0.0, "recall": 0.0, "f1": 0.0, "n_matched": 0,
                "matched_cosine_mean": float("nan")}
    res = soft_scores(embedder.sim(preds, refs))
    return {**base, "precision": float(res["p"]), "recall": float(res["r"]), "f1": float(res["f1"]),
            "n_matched": len(res["matched"]), "matched_cosine_mean": float(res["matched"].mean())}


def score_list_new_metric(evaluator, node, preds, refs):
    """Scores of one generated list with the new metric of its node."""
    g, r = len(preds), len(refs)
    evaluator.ramp, evaluator.max_per_ref = RAMPS[NEW_METRIC_ENCODER][node], MAX_PER_REF[node]
    res = evaluator.calculate_soft_f1(preds, refs)
    return {"g": g, "r": r, "g_over_r": g / r if r else float("nan"),
            "ceiling": ceiling_of(g, r, MAX_PER_REF[node]), "precision": float(res["precision"]),
            "recall": float(res["recall"]), "f1": float(res["f1_score"])}


def weighted_pr(rows):
    """Precision and recall averaged with the reference length as weight, and their F1."""
    total = sum(row["r"] for row in rows)
    p = sum(row["precision"] * row["r"] for row in rows) / total
    r = sum(row["recall"] * row["r"] for row in rows) / total
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in row.items()})


def write_run_csv(path, rows):
    """Same layout as the score CSV saved with each run: recall, precision, f1 per system."""
    p, r, f1 = weighted_pr(rows)
    with open(path, "w", encoding="utf-8") as f:
        f.write("dataset name; recall; precision; f1_score;\n")
        for row in rows:
            f.write(f"{row['system']}; {row['recall']}; {row['precision']}; {row['f1']};\n")
        f.write(f"Weighted averages; Precision: {p}; Recall: {r}; F1-score: {f1};\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", nargs="+", required=True, help="replica output directories")
    parser.add_argument("--out", required=True)
    parser.add_argument("--metric", choices=["production", "new_metric"], default="production")
    args = parser.parse_args()
    new_metric = args.metric == "new_metric"

    runs = {f"r{i}": run_dir.rstrip("/") for i, run_dir in enumerate(args.runs, start=1)}
    ground_truth = {g["name"]: g for g in ALL_GROUNDTRUTHS}
    systems = SYSTEM_SETS["all"]
    subset = {s: ("dev" if s in SYSTEM_SETS["dev"] else "holdout") for s in systems}

    if new_metric:
        evaluator = GoalEvaluator(encoder=NEW_METRIC_ENCODER)
    else:
        bert = GoalEvaluator(preprocess=True)
        embedders = {name: Embedder(name, bert) for name in set(PRODUCTION.values())}

    lists, aggregates = [], []
    max_diff, n_compared = 0.0, 0
    for replica, run_dir in runs.items():
        score_dir = os.path.join(args.out, "scores", replica)
        os.makedirs(score_dir, exist_ok=True)
        for shot in SHOTS:
            for critic, suffix in CRITIC.items():
                generated = {}
                for system in systems:
                    with open(os.path.join(run_dir, system, f"{system}_{shot}{suffix}.json"), encoding="utf-8") as f:
                        generated[system] = json.load(f)
                for node, prefix in NODES.items():
                    rows = []
                    for system in systems:
                        preds, refs = generated[system][node], ground_truth[system][node]
                        scores = (score_list_new_metric(evaluator, node, preds, refs) if new_metric
                                  else score_list(embedders[PRODUCTION[node]], preds, refs))
                        rows.append({"replica": replica, "system": system, "set": subset[system], "shot": shot,
                                     "critic": critic, "node": node, **scores})
                    lists.extend(rows)
                    write_run_csv(os.path.join(score_dir, f"{prefix}_{shot}{suffix}.csv"), rows)

                    on_disk_path = os.path.join(run_dir, f"{prefix}_{shot}{suffix}.csv")
                    if not new_metric and os.path.exists(on_disk_path):
                        on_disk = read_csv_f1(on_disk_path)
                        for row in rows:
                            max_diff = max(max_diff, abs(row["f1"] - on_disk[row["system"]]))
                            n_compared += 1

                    for set_name, names in SYSTEM_SETS.items():
                        group = [row for row in rows if row["system"] in names]
                        p_w, r_w, f1_w = weighted_pr(group)
                        mean_f1 = float(np.mean([row["f1"] for row in group]))
                        aggregates.append({
                            "replica": replica, "shot": shot, "critic": critic, "node": node, "set": set_name,
                            "n_systems": len(group), "mean_f1": mean_f1, "f1_of_weighted_pr": f1_w,
                            "weighted_minus_mean": f1_w - mean_f1,
                            "mean_precision": float(np.mean([row["precision"] for row in group])),
                            "mean_recall": float(np.mean([row["recall"] for row in group])),
                            "mean_ceiling": float(np.mean([row["ceiling"] for row in group])),
                            "mean_g_over_r": float(np.mean([row["g_over_r"] for row in group])),
                        })

    write_csv(os.path.join(args.out, "lists.csv"), lists)
    write_csv(os.path.join(args.out, "aggregates.csv"), aggregates)
    print(f"lists scored: {len(lists)}")
    if not new_metric:
        print(f"compared with the run CSVs: {n_compared}, max abs F1 difference: {max_diff:.2e}")
    print(f"written: {args.out}")
    if max_diff > CSV_TOLERANCE:
        raise SystemExit(f"recomputed F1 differs from the run CSVs by more than {CSV_TOLERANCE}")


if __name__ == "__main__":
    main()
