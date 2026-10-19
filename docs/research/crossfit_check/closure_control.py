# run from the repo root: OMP_NUM_THREADS=1 python3 docs/research/crossfit_check/closure_control.py  (writes closure_control.json)
"""CONTROL for the cross-fit diagnosis "the held-out drop is the benches' skewed workspace sample": kinematic closure
(the flood fill's node law: fold window + knee + closure; knee reference m from a Bench(60,160) fit, the same instrument
as docs/research/crossfit/kin_closure_diag.py) of configs that were NEVER optimised on the search benches - random
draws around H1 (z ~ N(0, 1.5) in the FREE step units, clipped to the ranges) - on the pool workspace poses vs the
held-out workspace poses. If the unoptimised draws show the same pool-minus-held closure gap as the polished configs
(0.05-0.07), the gap is a property of the pose sample; if they show ~0, it is selection on the pool."""
import sys, os, json, numpy as np
sys.path.insert(0, "tools"); import crossfit_polish as X, concept_bench as CB
Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; ws = np.nonzero(cid == names.index("Workspace (envelope)"))[0]
used = set(CB._select(110, 360)[0].tolist()) | set(CB._select(60, 160)[0].tolist())
inp = np.array([g in used for g in ws]); G = X._ws_grid(); P3 = G["POSE"]
pl = X.KneePlugin(); B = CB.Bench(60, 160); refs = json.load(open("docs/research/crossfit/refs.json"))
keys = [k for k in pl.FREE if k != "margin"]; rng = np.random.default_rng(20261016)
cfgs = {k: dict(v) for k, v in refs.items()}
for lab in ("XP1", "XP2"): cfgs[lab] = json.load(open(f"docs/research/crossfit/pick_{lab}.json"))["params"]
for j in range(int(os.environ.get("NDRAW", 16))):
    p = dict(refs["H1"])
    for k in keys:
        s0, lo, hi, _ = pl.FREE[k]; v = float(p.get(k, pl.base().get(k, 0.0))) + 1.5 * s0 * rng.standard_normal()
        if lo is not None: v = max(lo, v)
        if hi is not None: v = min(hi, v)
        p[k] = v
    cfgs[f"R{j:02d}"] = p
out = {}
for nm, p in cfgs.items():
    P = pl.full(p); pl.prep(P)
    try: M = pl.MK.Model(B, pl.model_params(P))
    except Exception as e: out[nm] = dict(error=repr(e)); continue
    if not M.kin_ok.any(): out[nm] = dict(nothing_closes=True); continue
    ok = pl.kin(M)(G["HG"])[0]
    big = np.abs(P3[:, 2]) >= 150
    out[nm] = dict(pool=round(float(ok[inp].mean()), 4), held=round(float(ok[~inp].mean()), 4), grid=round(float(ok.mean()), 4),
                   pool_minus_held=round(float(ok[inp].mean() - ok[~inp].mean()), 4),
                   ax150_pool=round(float(ok[inp & big].mean()), 4), ax150_held=round(float(ok[~inp & big].mean()), 4),
                   # held closure re-weighted to the pool's axial mix (25 axial levels): removes the axial skew only
                   held_rw_axial=round(float(sum(ok[~inp & (P3[:, 2] == a)].mean() * (inp & (P3[:, 2] == a)).sum() / inp.sum()
                                                 for a in sorted(set(P3[:, 2].tolist())) if (~inp & (P3[:, 2] == a)).any())), 4))
    print(nm, out[nm], flush=True)
R = [v for k, v in out.items() if k.startswith("R") and "pool" in v]; O = [v for k, v in out.items() if not k.startswith("R") and "pool" in v]
summ = {lab: dict(n=len(L), pool_minus_held=round(float(np.mean([v["pool_minus_held"] for v in L])), 4),
                  pool_minus_held_rw_axial=round(float(np.mean([v["pool"] - v["held_rw_axial"] for v in L])), 4)) for lab, L in (("random_draws", R), ("polished", O))}
print(summ); out["_summary"] = summ
json.dump(out, open("docs/research/crossfit_check/closure_control.json", "w"), indent=1)
