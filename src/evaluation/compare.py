"""Compare two conditions measured in several replicas over the same systems.

Reads the per-cell replica scores written by replica_noise.py (cells.csv) and, for every
system group, node and metric, writes one row with:
  the mean difference B - A over systems,
  a percentile bootstrap interval of that difference, resampling systems and, within each
  system and condition, replicas,
  the number of systems that improve, worsen or stay equal,
  the Wilcoxon signed-rank p-value of the per-system differences of replica means.

The two conditions may come from the same cells.csv or from two different ones.
"""
import argparse
import csv
import os

import numpy as np
from scipy.stats import wilcoxon

NODES = ["actors", "highLevelGoals", "lowLevelGoals"]
METRICS = ["f1", "precision", "recall"]
GROUPS = ["all", "holdout", "dev"]
ALPHA = 0.05


def load_condition(path, shot, critic):
    """Return {(node, metric): {system: (set, [replica scores])}} for one condition."""
    cells = {}
    with open(path) as f:
        reader = csv.DictReader(f)
        replicas = sorted(c[len("f1_"):] for c in reader.fieldnames if c.startswith("f1_r") and c != "f1_range")
        for row in reader:
            if row["shot"] != shot or row["critic"] != critic:
                continue
            for metric in METRICS:
                scores = [float(row[f"{metric}_{r}"]) for r in replicas]
                cells.setdefault((row["node"], metric), {})[row["system"]] = (row["set"], scores)
    if not cells:
        raise SystemExit(f"no rows for shot={shot} critic={critic} in {path}")
    return cells


def paired_matrices(cell_a, cell_b, group):
    """Scores of both conditions as (systems, replicas) arrays over the same systems."""
    if set(cell_a) != set(cell_b):
        raise SystemExit(f"systems differ between conditions: {sorted(set(cell_a) ^ set(cell_b))}")
    names = [s for s in sorted(cell_a) if group == "all" or cell_a[s][0] == group]
    return np.array([cell_a[s][1] for s in names]), np.array([cell_b[s][1] for s in names])


def resampled_means(x, idx, rng):
    """Mean of replicas drawn with replacement, for every resampled system. Returns (boots, systems)."""
    n_rep = x.shape[1]
    weights = rng.multinomial(n_rep, [1 / n_rep] * n_rep, idx.shape) / n_rep
    return (x[idx] * weights).sum(axis=2)


def bootstrap_interval(a, b, n_boot, seed):
    """Percentile interval of the mean difference b - a over systems and replicas."""
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), (n_boot, len(a)))
    diff = (resampled_means(b, idx, rng) - resampled_means(a, idx, rng)).mean(axis=1)
    return np.quantile(diff, [ALPHA / 2, 1 - ALPHA / 2])


def signed_rank_p(d):
    """Two-sided Wilcoxon p-value, or None when no sample of this size can reach ALPHA."""
    nonzero = d[d != 0]
    # The smallest attainable two-sided p-value with n non-zero differences is 2 / 2**n.
    if len(nonzero) == 0 or 2 / 2 ** len(nonzero) >= ALPHA:
        return None
    return float(wilcoxon(d).pvalue)


def compare(cells_a, cells_b, n_boot, seed):
    rows = []
    for group in GROUPS:
        for node in NODES:
            for metric in METRICS:
                a, b = paired_matrices(cells_a[(node, metric)], cells_b[(node, metric)], group)
                d = b.mean(axis=1) - a.mean(axis=1)
                low, high = bootstrap_interval(a, b, n_boot, seed)
                p = signed_rank_p(d)
                rows.append({
                    "group": group, "node": node, "metric": metric, "n_systems": len(d),
                    "mean_a": round(float(a.mean()), 4), "mean_b": round(float(b.mean()), 4),
                    "mean_diff": round(float(d.mean()), 4),
                    "ci_low": round(float(low), 4) + 0.0, "ci_high": round(float(high), 4) + 0.0,
                    "recognized": bool(low > 0 or high < 0),
                    "n_better": int((d > 0).sum()), "n_worse": int((d < 0).sum()), "n_equal": int((d == 0).sum()),
                    "wilcoxon_p": "" if p is None else round(p, 4),
                })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cells-a", required=True, help="cells.csv holding the reference condition")
    parser.add_argument("--shot-a", required=True)
    parser.add_argument("--critic-a", required=True, choices=["ON", "OFF"])
    parser.add_argument("--cells-b", help="cells.csv holding the compared condition (default: --cells-a)")
    parser.add_argument("--shot-b", required=True)
    parser.add_argument("--critic-b", required=True, choices=["ON", "OFF"])
    parser.add_argument("--out", required=True, help="output CSV")
    parser.add_argument("--boots", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20261011)
    args = parser.parse_args()

    cells_a = load_condition(args.cells_a, args.shot_a, args.critic_a)
    cells_b = load_condition(args.cells_b or args.cells_a, args.shot_b, args.critic_b)
    rows = compare(cells_a, cells_b, args.boots, args.seed)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
