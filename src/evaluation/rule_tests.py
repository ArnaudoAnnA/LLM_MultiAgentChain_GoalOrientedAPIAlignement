"""False-alarm and missed-effect rates of candidate comparison rules.

Simulated experiments are built from the replica scores in cells.csv: every cell keeps its
observed mean and replica standard deviation, and simulated replicas are drawn around it.
Two copies of the same condition are compared (no effect) or a known effect is added to one
of them. Writes:
  rule_tests.csv            rate of "effect" verdicts per group, node, condition, scenario, rule
  rule_tests_summary.csv    the same rates averaged over conditions
  resample_check.csv        false-alarm rates when replicas are resampled from observed values
  pairing_check.csv         stability of per-replica rules under replica relabeling
"""
import argparse
import csv
import itertools
import os

import numpy as np
from scipy.stats import wilcoxon

SHOTS = ["ZERO_SHOT", "ONE_SHOT", "FEW_SHOT"]
CRITICS = ["ON", "OFF"]
NODES = ["actors", "highLevelGoals", "lowLevelGoals"]
GROUPS = ["all", "holdout", "dev"]
RULES = ["permissive", "intermediate", "strict", "strict_sign", "wilcoxon", "bootstrap"]
PER_REPLICA_RULES = RULES[:4]
DELTAS = [0.03, 0.05, 0.10]
PAIRS = [(0, 1), (0, 2), (1, 2)]
ALPHA = 0.05
DEVICE = "cpu"


def load_cells(path):
    """Return {(node, shot, critic): {system: (set, [f1_r1, f1_r2, f1_r3])}}."""
    cells = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            key = (row["node"], row["shot"], row["critic"])
            scores = [float(row[f"f1_r{i}"]) for i in (1, 2, 3)]
            cells.setdefault(key, {})[row["system"]] = (row["set"], scores)
    return cells


def group_matrix(cell, group):
    """Scores of one condition as a (systems, 3) array restricted to a system group."""
    rows = [scores for _, (sset, scores) in sorted(cell.items()) if group == "all" or sset == group]
    return np.array(rows)


def within_shifts(x):
    """Mean-over-systems shift between each pair of replicas. x: (..., systems, 3)."""
    return np.stack([(x[..., i] - x[..., j]).mean(axis=-1) for i, j in PAIRS], axis=-1)


def net_sign(d):
    """Systems with a positive difference minus systems with a negative one. d: (..., systems, k)."""
    return (d > 0).sum(axis=-2) - (d < 0).sum(axis=-2)


def baseline_reference(cells, node, group):
    """Largest replica-to-replica shift and sign imbalance over all conditions of a node."""
    shifts, nets = [], []
    for shot, critic in itertools.product(SHOTS, CRITICS):
        x = group_matrix(cells[(node, shot, critic)], group)
        shifts.append(np.abs(within_shifts(x)).max())
        nets.append(max(abs(net_sign((x[:, [i]] - x[:, [j]]))[0]) for i, j in PAIRS))
    return max(shifts), max(nets)


def bootstrap_weights(rng, n_boot, n_systems):
    """System indices and replica-mean weights shared by all simulations of a chunk."""
    idx = rng.integers(0, n_systems, (n_boot, n_systems))
    wa = rng.multinomial(3, [1 / 3] * 3, (n_boot, n_systems)) / 3
    wb = rng.multinomial(3, [1 / 3] * 3, (n_boot, n_systems)) / 3
    return idx, wa, wb


def bootstrap_excludes_zero(a, b, rng, n_boot, chunk=50):
    """Percentile interval of the mean difference, resampling systems and replicas within them.

    Resampling indices always come from the NumPy generator, so the verdicts do not depend on
    the device: only the gather, the weighted mean and the percentiles run on DEVICE.
    """
    out = np.zeros(len(a), dtype=bool)
    n_systems = a.shape[1]
    quantiles = [ALPHA / 2, 1 - ALPHA / 2]
    for start in range(0, len(a), chunk):
        idx, wa, wb = bootstrap_weights(rng, n_boot, n_systems)
        ca, cb = a[start:start + chunk], b[start:start + chunk]
        if DEVICE == "cpu":
            # (sims, boots, systems): replica-weighted mean of each resampled system.
            ma = np.einsum("nbsr,bsr->nbs", ca[:, idx, :], wa)
            mb = np.einsum("nbsr,bsr->nbs", cb[:, idx, :], wb)
            lo, hi = np.quantile((mb - ma).mean(axis=2), quantiles, axis=1)
        else:
            import torch
            ti = torch.as_tensor(idx, device=DEVICE)
            ta, tb = (torch.as_tensor(v, device=DEVICE) for v in (ca, cb))
            twa, twb = (torch.as_tensor(v, device=DEVICE) for v in (wa, wb))
            diff = (torch.einsum("nbsr,bsr->nbs", tb[:, ti, :], twb)
                    - torch.einsum("nbsr,bsr->nbs", ta[:, ti, :], twa)).mean(dim=2)
            lo, hi = torch.quantile(diff, torch.tensor(quantiles, device=DEVICE, dtype=diff.dtype), dim=1).cpu().numpy()
        out[start:start + chunk] = (lo > 0) | (hi < 0)
    return out


def apply_rules(a, b, ref_shift, ref_net, rng, n_boot):
    """Verdict of every rule on simulated experiments. a, b: (sims, systems, 3)."""
    d = b - a
    per_replica = d.mean(axis=1)
    sign = np.sign(per_replica)
    same_sign_all = (np.abs(sign.sum(axis=1)) == 3)

    own_shift = np.maximum(np.abs(within_shifts(a)).max(axis=1), np.abs(within_shifts(b)).max(axis=1))
    over_own = np.abs(per_replica) > own_shift[:, None]
    over_ref = np.abs(per_replica) > ref_shift

    verdicts = {}
    # Two replicas over the threshold and pointing the same way are enough.
    verdicts["permissive"] = ((over_own & (sign > 0)).sum(axis=1) >= 2) | ((over_own & (sign < 0)).sum(axis=1) >= 2)
    verdicts["intermediate"] = over_own.all(axis=1) & same_sign_all
    verdicts["strict"] = over_ref.all(axis=1) & same_sign_all
    aligned_net = net_sign(d) * sign
    verdicts["strict_sign"] = verdicts["strict"] & (aligned_net > ref_net).all(axis=1)

    means = d.mean(axis=2)
    verdicts["wilcoxon"] = wilcoxon(means, axis=1).pvalue < ALPHA
    verdicts["bootstrap"] = bootstrap_excludes_zero(a, b, rng, n_boot)
    return verdicts


def effect_vector(rng, shape, delta, n_sims, n_systems):
    """Per-system effect with mean delta. Shapes: uniform, half of the systems, one system."""
    if shape == "uniform":
        return np.full((n_sims, n_systems), delta)
    k = n_systems // 2 if shape == "half" else 1
    order = rng.random((n_sims, n_systems)).argsort(axis=1)
    return np.where(order < k, delta * n_systems / k, 0.0)


def simulate(rng, x, n_sims):
    """Normal replicas around each cell mean with the cell's own replica standard deviation."""
    mu, sd = x.mean(axis=1), x.std(axis=1, ddof=1)
    return mu[None, :, None] + sd[None, :, None] * rng.standard_normal((n_sims, len(mu), 3))


def resample(rng, x, n_sims):
    """Replicas drawn with replacement from the three observed values of each cell."""
    pick = rng.integers(0, 3, (n_sims, x.shape[0], 3))
    return np.take_along_axis(np.broadcast_to(x, (n_sims,) + x.shape), pick, axis=2)


def contrasts():
    for shot in SHOTS:
        yield f"critic ON-OFF @ {shot}", (shot, "ON"), (shot, "OFF")
    for critic in CRITICS:
        for hi, lo in [("ONE_SHOT", "ZERO_SHOT"), ("FEW_SHOT", "ZERO_SHOT"), ("FEW_SHOT", "ONE_SHOT")]:
            yield f"{hi}-{lo} @ critic {critic}", (hi, critic), (lo, critic)


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--sims", type=int, default=1000)
    parser.add_argument("--boots", type=int, default=1000)
    parser.add_argument("--relabelings", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20261011)
    parser.add_argument("--device", default="cpu", help="cpu or a torch device such as cuda")
    args = parser.parse_args()
    global DEVICE
    DEVICE = args.device

    rng = np.random.default_rng(args.seed)
    cells = load_cells(args.cells)
    os.makedirs(args.out, exist_ok=True)

    scenarios = [("none", 0.0)] + [(s, d) for s in ("uniform", "half", "single") for d in DELTAS]
    detail, check = [], []
    for group, node in itertools.product(GROUPS, NODES):
        ref_shift, ref_net = baseline_reference(cells, node, group)
        for shot, critic in itertools.product(SHOTS, CRITICS):
            x = group_matrix(cells[(node, shot, critic)], group)
            base = {"group": group, "node": node, "condition": f"{shot} critic {critic}", "n_systems": len(x)}
            for shape, delta in scenarios:
                a, b = simulate(rng, x, args.sims), simulate(rng, x, args.sims)
                if delta:
                    b = b + effect_vector(rng, shape, delta, args.sims, len(x))[:, :, None]
                for rule, verdict in apply_rules(a, b, ref_shift, ref_net, rng, args.boots).items():
                    detail.append({**base, "shape": shape, "delta": delta, "rule": rule, "effect_rate": float(verdict.mean())})
            a, b = resample(rng, x, args.sims), resample(rng, x, args.sims)
            for rule, verdict in apply_rules(a, b, ref_shift, ref_net, rng, args.boots).items():
                check.append({**base, "rule": rule, "effect_rate": float(verdict.mean())})

    summary = []
    keys = sorted({(r["group"], r["node"], r["shape"], r["delta"], r["rule"]) for r in detail},
                  key=lambda k: (GROUPS.index(k[0]), NODES.index(k[1]), k[2], k[3], RULES.index(k[4])))
    for group, node, shape, delta, rule in keys:
        rates = [r["effect_rate"] for r in detail
                 if (r["group"], r["node"], r["shape"], r["delta"], r["rule"]) == (group, node, shape, delta, rule)]
        summary.append({"group": group, "node": node, "shape": shape, "delta": delta, "rule": rule,
                        "effect_rate_mean": float(np.mean(rates)), "effect_rate_min": min(rates), "effect_rate_max": max(rates)})

    # Replica indices carry no meaning across systems, so any within-system relabeling is as
    # valid as the observed one. A per-replica rule is stable when its verdict ignores it.
    pairing = []
    for group, node in itertools.product(GROUPS, NODES):
        ref_shift, ref_net = baseline_reference(cells, node, group)
        for name, c1, c2 in contrasts():
            xa, xb = group_matrix(cells[(node,) + c2], group), group_matrix(cells[(node,) + c1], group)
            n = args.relabelings
            pa = rng.random((n,) + xa.shape).argsort(axis=2)
            pb = rng.random((n,) + xb.shape).argsort(axis=2)
            a = np.take_along_axis(np.broadcast_to(xa, (n,) + xa.shape), pa, axis=2)
            b = np.take_along_axis(np.broadcast_to(xb, (n,) + xb.shape), pb, axis=2)
            verdicts = apply_rules(a, b, ref_shift, ref_net, rng, 10)
            row = {"group": group, "node": node, "contrast": name}
            for rule in PER_REPLICA_RULES:
                row[f"{rule}_effect_share"] = float(verdicts[rule].mean())
            pairing.append(row)

    write_csv(os.path.join(args.out, "rule_tests.csv"), detail)
    write_csv(os.path.join(args.out, "rule_tests_summary.csv"), summary)
    write_csv(os.path.join(args.out, "resample_check.csv"), check)
    write_csv(os.path.join(args.out, "pairing_check.csv"), pairing)


if __name__ == "__main__":
    main()
