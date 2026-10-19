"""What caps the zero-complexity class, from the exhaustive screen's exact lower bounds (screen_p*_bounds.npz) and full
bench rows (screen_p*.json): how many Sobol configs could still reach the golden gap 13.75 after the fold law alone
(stage A), after the three O20 hubs (stage B), which hub floats (F > 140 mm) where the fold would allow 95, and the
reach / in-band frontier of every fully evaluated config.

    python3 pipeline/gpu_pod/xs_ceiling.py DIR [DIR2 ...]  -> JSON on stdout
"""
import glob, json, os, sys
import numpy as np

GOLD = 13.75


def main():
    lbA, lbB, rubA, rubB, hubF, P, rows = [], [], [], [], [], [], []
    for d in sys.argv[1:]:
        for f in sorted(glob.glob(os.path.join(d, "screen_p*_bounds.npz"))):
            Z = np.load(f); lbA.append(Z["lbA"]); lbB.append(Z["lbB"]); rubA.append(Z["rubA"]); rubB.append(Z["rubB"]); hubF.append(Z["hubF"]); P.append(Z["P"])
        for f in sorted(glob.glob(os.path.join(d, "screen_p*.json"))):
            if f.endswith("_bounds.json"): continue
            rows += [r for r in json.load(open(f))["rows"] if r.get("params") and r.get("lbB") is not None]
    lbA, lbB, rubA, rubB, hubF, P = (np.concatenate(x) for x in (lbA, lbB, rubA, rubB, hubF, P))
    N = len(lbA); okA = lbA <= GOLD
    hb = np.nan_to_num(hubF, nan=999.0)
    out = dict(n_sobol=int(N), gold_gap=GOLD,
               stageA=dict(n_le_gold=int(okA.sum()), share=round(float(okA.mean()), 4),
                           kin_reach_ub_p50=round(float(np.nanmedian(rubA)), 4), kin_reach_ub_max=round(float(np.nanmax(rubA)), 4),
                           n_kin_reach_ge_0_7625=int((rubA >= 0.7625).sum())),
               stageB=dict(n_evaluated=int(np.isfinite(lbB).sum()), n_le_gold=int((lbB <= GOLD).sum()),
                           min_bound=round(float(np.nanmin(lbB)), 2),
                           n_le=dict({str(t): int((lbB <= t).sum()) for t in (15, 20, 25, 28.85, 30, 35, 40, 45)})))
    # where the fold allows 95 (stage A <= 13.75): which hub floats, how many keep all hubs on the body, their best bound
    sel = okA & np.isfinite(lbB)
    fl = hb[sel] > 140.0
    out["fold_allows_95"] = dict(n=int(sel.sum()), all_hubs_on_body=int((~fl.any(1)).sum()),
                                 hub_floats_share=dict(hub1=round(float(fl[:, 0].mean()), 4), hub2=round(float(fl[:, 1].mean()), 4),
                                                       hub3=round(float(fl[:, 2].mean()), 4)) if fl.size else None,
                                 hub_F_median=[round(float(np.median(hb[sel][:, k])), 1) for k in range(3)] if sel.any() else None,
                                 best_stageB_bound=round(float(np.min(lbB[sel])), 2) if sel.any() else None,
                                 reach_ub_after_hubs_p50=round(float(np.median(rubB[sel])), 4) if sel.any() else None)
    # arcs of the kinematically viable configs vs the hub-viable ones
    cols = ("az", "el", "a1", "a2", "wd", "wa", "sigma", "q", "end_extra")
    hv = sel & (hb <= 140).all(1)
    for name, m in (("fold_allows_95", sel), ("and_hubs_on_body", hv)):
        if m.any():
            out.setdefault("arcs", {})[name] = {c: [round(float(np.percentile(P[m][:, i], q)), 1) for q in (5, 50, 95)] for i, c in enumerate(cols[:6])}
    # full bench rows: reach / in-band frontier
    hon = [r for r in rows if r.get("honest")]
    out["full"] = dict(n_rows=len(rows), n_honest=len(hon), best_gap=min((r["gap"] for r in rows), default=None),
                       best_near=min((r.get("near", 999) for r in rows), default=None),
                       reach_max_at_inband={str(t): max((r["reach"] for r in hon if r["inband14"] >= t), default=None) for t in (0.9, 0.88, 0.85, 0.8, 0.7)},
                       inband_max_at_reach={str(t): max((r["inband14"] for r in hon if r["reach"] >= t), default=None) for t in (0.7625, 0.7, 0.65, 0.6)})
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
