"""Diagnostics of the evaluation metric on outputs already on disk. Zero API calls.

Reads the generated lists of the baseline replicas and the ground truth, then measures
properties of the metric itself (not of the pipeline):

  1. sanity check: the F1 recomputed here matches the per-system CSVs written with each run;
  2. where the cosines sit: matched pairs, all pairs of the same system, and pairs built
     by scoring the output of one system against the ground truth of another one;
  3. the score obtained by a list that is unrelated by construction (cross-system);
  4. how often appending one unrelated goal raises the F1;
  5. how often the one-to-one constraint displaces a generated goal from its best reference;
  6. post-hoc thresholding of the optimal assignment vs maximum matching on the thresholded graph;
  7. aggregation: F1 of weighted P/R vs mean of the per-dataset F1;
  8. code-level checks (empty list, stopword casing, determinism);
  9. the F1 ceiling imposed by the two list lengths alone, per system;
 10. exact duplicates inside a generated list and whether they get a partner.

Each measure is repeated for every encoder in --encoders: "bert_pre" and "bert_raw" are BERT
mean-pooled with and without the preprocessing used for HLG/LLG, the other names are sentence
encoders defined in src/evaluation/goal_evaluator.py, and "a+b" averages the cosines of two
encoders.

Run from the repository root:
`python src/diagnostics/metric_diagnostics.py --runs <replica dirs> --output <file.json>`
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

import numpy as np
import torch
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import maximum_bipartite_matching

sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "notebook"))
from src.evaluation.goal_evaluator import GoalEvaluator, SentenceEncoder  # noqa: E402
from groundtruth import ALL_GROUNDTRUTHS  # noqa: E402

SHOT_MODES = ["ZERO_SHOT", "ONE_SHOT", "FEW_SHOT"]
SUFFIXES = ["", "_noLlama"]
NODES = {"actors": "actor", "highLevelGoals": "hl", "lowLevelGoals": "ll"}
ENCODERS = ["bert_pre", "bert_raw", "minilm", "mpnet"]
# Encoder actually used by the pipeline for each node.
PRODUCTION = {"actors": "bert_raw", "highLevelGoals": "bert_pre", "lowLevelGoals": "bert_pre"}
TAUS = [round(t, 2) for t in np.arange(0.50, 0.96, 0.05)]


class Embedder:
    """Unit-norm embeddings with a per-text cache, one instance per encoder."""

    def __init__(self, name, bert_evaluator, device=None):
        self.name = name
        self.cache = {}
        self.bert = bert_evaluator
        self.parts = [Embedder(part, bert_evaluator, device) for part in name.split("+")] if "+" in name else None
        self.st = None if self.parts or name.startswith("bert_") else SentenceEncoder(name, device)

    def _encode(self, texts):
        if self.st is not None:
            return self.st.encode_uncached(texts)
        self.bert.preprocess = self.name == "bert_pre"
        emb = self.bert.encode_texts(texts)
        return torch.nn.functional.normalize(emb, p=2, dim=1).cpu().numpy()

    def __call__(self, texts):
        missing = [t for t in dict.fromkeys(texts) if t not in self.cache]
        for i in range(0, len(missing), 32):
            chunk = missing[i:i + 32]
            for text, vec in zip(chunk, self._encode(chunk)):
                self.cache[text] = vec
        return np.stack([self.cache[t] for t in texts])

    def sim(self, preds, refs):
        if self.parts:
            return np.mean([part.sim(preds, refs) for part in self.parts], axis=0)
        return self(preds) @ self(refs).T

    def warm(self, texts):
        """Embed every text once, measure repeatability, then free the model."""
        if self.parts:
            return {part.name: part.warm(texts) for part in self.parts}
        sample = texts[:32]
        first = self._encode(sample)
        checks = {"two_identical_calls": float(np.abs(first - self._encode(sample)).max()),
                  # Same texts, different batch composition: padding may change the result.
                  "different_batching": float(np.abs(first[:4] - self._encode(sample[:4])).max())}
        self(texts)
        if self.st is not None:
            self.st.release()
        return checks


def soft_scores(sim):
    rows, cols = linear_sum_assignment(-sim)
    total = sim[rows, cols].sum()
    g, r = sim.shape
    return {"p": total / g, "r": total / r, "f1": 2 * total / (g + r),
            "rows": rows, "cols": cols, "matched": sim[rows, cols]}


def load_cells(ground_truth, runs):
    """Returns a list of cells: one per (replica, shot, critic arm, system)."""
    cells = []
    for replica, run_dir in runs.items():
        for shot in SHOT_MODES:
            for suffix in SUFFIXES:
                for system in ground_truth:
                    path = os.path.join(run_dir, system, f"{system}_{shot}{suffix}.json")
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                    cells.append({"replica": replica, "shot": shot, "suffix": suffix, "system": system,
                                  "gen": {node: data[node] for node in NODES}})
    return cells


def read_csv_f1(path):
    values = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = [p.strip() for p in line.strip().split(";") if p.strip()]
            if len(parts) == 4 and not parts[0].startswith(("dataset", "Weighted")):
                values[parts[0]] = float(parts[3])
    return values


def describe(values):
    a = np.asarray(values, dtype=float)
    return {"n": int(a.size), "mean": float(a.mean()), "p05": float(np.percentile(a, 5)),
            "p50": float(np.percentile(a, 50)), "p95": float(np.percentile(a, 95)),
            "min": float(a.min()), "max": float(a.max())}


def auc_separation(positives, negatives):
    """Probability that a random matched pair scores higher than a random cross-system pair."""
    pos, neg = np.sort(np.asarray(positives)), np.sort(np.asarray(negatives))
    return float(np.searchsorted(neg, pos, side="left").sum() / (len(pos) * len(neg)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", required=True, help="replica directories of the same experiment")
    parser.add_argument("--output", required=True, help="output JSON")
    parser.add_argument("--encoders", nargs="+", default=ENCODERS, help="encoders to measure")
    parser.add_argument("--device", default=None, help="device of the sentence encoders (default: cuda if available)")
    args = parser.parse_args()

    runs = {f"r{i}": run_dir.rstrip("/") for i, run_dir in enumerate(args.runs, start=1)}
    ground_truth = {g["name"]: {node: g[node] for node in NODES} for g in ALL_GROUNDTRUTHS}
    systems = list(ground_truth)
    cells = load_cells(ground_truth, runs)

    bert = GoalEvaluator(preprocess=True)
    names = list(dict.fromkeys(list(args.encoders) + list(PRODUCTION.values())))
    embedders = {name: Embedder(name, bert, args.device) for name in names}
    out = {"runs": runs, "systems": systems, "n_cells_per_node": len(cells), "nodes": {}}

    all_texts = sorted({text for node in NODES for source in (ground_truth.values(), (c["gen"] for c in cells))
                        for lists in source for text in lists[node]})
    out["repeatability_max_abs_diff"] = {name: emb.warm(all_texts) for name, emb in embedders.items()}

    # 1. Sanity check against the per-system CSVs written with each run.
    max_diff = 0.0
    for node, prefix in NODES.items():
        for replica, run_dir in runs.items():
            for shot in SHOT_MODES:
                for suffix in SUFFIXES:
                    on_disk = read_csv_f1(os.path.join(run_dir, f"{prefix}_{shot}{suffix}.csv"))
                    for cell in cells:
                        if (cell["replica"], cell["shot"], cell["suffix"]) != (replica, shot, suffix):
                            continue
                        sim = embedders[PRODUCTION[node]].sim(cell["gen"][node], ground_truth[cell["system"]][node])
                        max_diff = max(max_diff, abs(soft_scores(sim)["f1"] - on_disk[cell["system"]]))
    out["sanity_max_abs_diff_vs_csv"] = max_diff

    for node in NODES:
        node_out = {"production_encoder": PRODUCTION[node], "encoders": {}}
        sizes = [(len(c["gen"][node]), len(ground_truth[c["system"]][node])) for c in cells]
        node_out["list_sizes"] = {
            "g_lt_r": sum(g < r for g, r in sizes), "g_eq_r": sum(g == r for g, r in sizes),
            "g_gt_r": sum(g > r for g, r in sizes),
            "ratio_g_over_r": describe([g / r for g, r in sizes]),
        }

        for enc_name in args.encoders:
            emb = embedders[enc_name]
            matched, within_all, cross_all, cross_matched = [], [], [], []
            duplicates = duplicates_matched = 0
            per_system = {s: {"g": [], "f1": [], "ceiling": []} for s in systems}
            f1_real, f1_cross = [], []
            raise_num = raise_den = 0
            raise_by_regime = {"g_lt_r": [0, 0], "g_ge_r": [0, 0]}
            displaced = n_gen_total = unmatched_gen = 0
            refs_contended = n_ref_total = 0
            above_half_f1_within, above_half_f1_cross = [], []
            posthoc_vs_max = {tau: {"cells_differ": 0, "tp_posthoc": 0, "tp_max": 0} for tau in TAUS}

            for cell in cells:
                preds = cell["gen"][node]
                refs = ground_truth[cell["system"]][node]
                sim = emb.sim(preds, refs)
                res = soft_scores(sim)
                f1_real.append(res["f1"])
                matched.extend(res["matched"].tolist())
                within_all.extend(sim.ravel().tolist())
                above_half_f1_within.append(float((sim > res["f1"] / 2).mean()))

                # 9. Best F1 reachable with perfect matches, given the two lengths only.
                g, r = sim.shape
                per_system[cell["system"]]["g"].append(g)
                per_system[cell["system"]]["f1"].append(res["f1"])
                per_system[cell["system"]]["ceiling"].append(2 * min(g, r) / (g + r))

                # 10. Exact repeats of an earlier item of the same list.
                matched_rows = set(res["rows"].tolist())
                seen = set()
                for i, text in enumerate(preds):
                    if text in seen:
                        duplicates += 1
                        duplicates_matched += i in matched_rows
                    seen.add(text)

                # 5. One-to-one constraint: generated goals not assigned to their best reference.
                assigned = dict(zip(res["rows"].tolist(), res["cols"].tolist()))
                best_ref = sim.argmax(axis=1)
                n_gen_total += len(preds)
                n_ref_total += len(refs)
                unmatched_gen += len(preds) - len(assigned)
                displaced += sum(1 for i in range(len(preds)) if assigned.get(i) != best_ref[i])
                refs_contended += int((np.bincount(best_ref, minlength=len(refs)) >= 2).sum())

                # 6. Thresholding the optimal assignment vs maximum matching on the thresholded graph.
                for tau in TAUS:
                    tp_posthoc = int((res["matched"] >= tau).sum())
                    graph = csr_matrix((sim >= tau).astype(int))
                    tp_max = int((maximum_bipartite_matching(graph, perm_type="column") >= 0).sum())
                    posthoc_vs_max[tau]["tp_posthoc"] += tp_posthoc
                    posthoc_vs_max[tau]["tp_max"] += tp_max
                    posthoc_vs_max[tau]["cells_differ"] += int(tp_max != tp_posthoc)

                # 2-4. Material from the other systems of the same run: unrelated by construction.
                foreign_goals = []
                for other in cells:
                    same_run = (other["replica"], other["shot"], other["suffix"]) == \
                               (cell["replica"], cell["shot"], cell["suffix"])
                    if not same_run or other["system"] == cell["system"]:
                        continue
                    cross_sim = emb.sim(preds, ground_truth[other["system"]][node])
                    cross_all.extend(cross_sim.ravel().tolist())
                    cross_res = soft_scores(cross_sim)
                    cross_matched.extend(cross_res["matched"].tolist())
                    f1_cross.append(cross_res["f1"])
                    foreign_goals.extend(other["gen"][node])

                cross_for_cell = emb.sim(foreign_goals, refs)
                above_half_f1_cross.append(float((cross_for_cell > res["f1"] / 2).mean()))
                regime = "g_lt_r" if len(preds) < len(refs) else "g_ge_r"
                for k in range(len(foreign_goals)):
                    new_f1 = soft_scores(np.vstack([sim, cross_for_cell[k:k + 1]]))["f1"]
                    rose = int(new_f1 > res["f1"] + 1e-9)
                    raise_num += rose
                    raise_den += 1
                    raise_by_regime[regime][0] += rose
                    raise_by_regime[regime][1] += 1

            node_out["encoders"][enc_name] = {
                "cosine_matched_pairs": describe(matched),
                "cosine_all_pairs_same_system": describe(within_all),
                "cosine_all_pairs_cross_system": describe(cross_all),
                "cosine_matched_pairs_cross_system": describe(cross_matched),
                "auc_matched_vs_cross": auc_separation(matched, cross_all),
                "auc_matched_vs_cross_matched": auc_separation(matched, cross_matched),
                "per_system": {s: {"n_ref": len(ground_truth[s][node]), "g_mean": float(np.mean(v["g"])),
                                   "f1_mean": float(np.mean(v["f1"])), "ceiling_mean": float(np.mean(v["ceiling"]))}
                               for s, v in per_system.items()},
                "exact_duplicates": {"total": duplicates, "matched": duplicates_matched},
                "f1_real": describe(f1_real),
                "f1_cross_system": describe(f1_cross),
                "share_pairs_above_half_f1_same_system": float(np.mean(above_half_f1_within)),
                "share_pairs_above_half_f1_cross_system": float(np.mean(above_half_f1_cross)),
                "unrelated_goal_raises_f1": {
                    "share": raise_num / raise_den, "trials": raise_den,
                    "raised_g_lt_r": raise_by_regime["g_lt_r"][0], "raised_g_ge_r": raise_by_regime["g_ge_r"][0],
                    "share_when_g_lt_r": (raise_by_regime["g_lt_r"][0] / raise_by_regime["g_lt_r"][1]
                                          if raise_by_regime["g_lt_r"][1] else None),
                    "trials_g_lt_r": raise_by_regime["g_lt_r"][1],
                    "share_when_g_ge_r": (raise_by_regime["g_ge_r"][0] / raise_by_regime["g_ge_r"][1]
                                          if raise_by_regime["g_ge_r"][1] else None),
                    "trials_g_ge_r": raise_by_regime["g_ge_r"][1],
                },
                "one_to_one": {
                    "generated_total": n_gen_total, "generated_unmatched": unmatched_gen,
                    "generated_not_on_best_ref": displaced,
                    "references_total": n_ref_total, "references_best_for_2plus_generated": refs_contended,
                },
                "posthoc_threshold_vs_max_matching": posthoc_vs_max,
            }

        # 7. Aggregation, production encoder only.
        emb = embedders[PRODUCTION[node]]
        weights = {s: len(ground_truth[s][node]) for s in systems}
        diffs = []
        for replica in runs:
            for shot in SHOT_MODES:
                for suffix in SUFFIXES:
                    group = [c for c in cells if (c["replica"], c["shot"], c["suffix"]) == (replica, shot, suffix)]
                    scores = {c["system"]: soft_scores(emb.sim(c["gen"][node], ground_truth[c["system"]][node]))
                              for c in group}
                    w_total = sum(weights.values())
                    p_w = sum(scores[s]["p"] * weights[s] for s in systems) / w_total
                    r_w = sum(scores[s]["r"] * weights[s] for s in systems) / w_total
                    diffs.append({
                        "f1_of_weighted_pr": 2 * p_w * r_w / (p_w + r_w),
                        "mean_of_f1": float(np.mean([scores[s]["f1"] for s in systems])),
                        "weighted_mean_of_f1": sum(scores[s]["f1"] * weights[s] for s in systems) / w_total,
                    })
        node_out["aggregation"] = {
            "weights": weights,
            "weight_share": {s: weights[s] / sum(weights.values()) for s in systems},
            "f1_of_weighted_pr": describe([d["f1_of_weighted_pr"] for d in diffs]),
            "mean_of_f1": describe([d["mean_of_f1"] for d in diffs]),
            "code_minus_mean_of_f1": describe([d["f1_of_weighted_pr"] - d["mean_of_f1"] for d in diffs]),
            "code_minus_weighted_mean_of_f1": describe([d["f1_of_weighted_pr"] - d["weighted_mean_of_f1"]
                                                        for d in diffs]),
        }
        out["nodes"][node] = node_out

    # 8. Code-level checks.
    checks = {}
    bert.preprocess = True
    sample = "The user can authenticate using the API and retrieve annotations."
    checks["preprocess_example"] = {"input": sample, "output": bert.preprocess_text(sample),
                                    "wordpieces": bert.tokenizer.tokenize(bert.preprocess_text(sample))}
    first = cells[0]
    refs = ground_truth[first["system"]]["lowLevelGoals"]
    a = bert.compute_similarity(first["gen"]["lowLevelGoals"], refs)
    b = bert.compute_similarity(first["gen"]["lowLevelGoals"], refs)
    checks["determinism_max_abs_diff_two_calls"] = float(np.abs(a - b).max())
    with tempfile.TemporaryDirectory() as tmp:
        try:
            bert.print_prec_rec_curve({"x": []}, {"x": ["a goal"]}, hide_prec_rec=True,
                                      output_file=os.path.join(tmp, "o.txt"))
            checks["empty_generated_list"] = "no error"
        except Exception as exc:  # the exception type is the finding
            checks["empty_generated_list"] = f"{type(exc).__name__}: {exc}"
    out["code_checks"] = checks

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False, default=float)
    print(f"written: {args.output}")


if __name__ == "__main__":
    main()
