"""Can ANY chain of the lead's two 3-DOF families absorb the girdle motion of the lead's own LITERATURE law
(girdle.lift_literature: Ludewig 2009 bone-pin angles through a 154 mm clavicle; 65 mm max on the clips vs 25 mm in the rig)?
Same search as p0_base_mount.py (axis directions by multi-start Nelder-Mead on the least-squares residual, singular margin
>= 20 deg on the fit clips, polish with the exact minimax LP), but fitted to the literature law. Starts: the lead's rig-law
optimum + random. Short budget (this is a red-team bound, not a design search).
    python3 rt_girdle_lit.py -> results/girdle_lit.json
"""
import time
import numpy as np
from scipy.optimize import minimize
import rt_common as RC
from rt_common import GD

t0 = time.time(); FR = RC.clips(); names = np.array([f[0] for f in FR]); WANT = np.array([f[2] for f in FR], float); FIT = ~np.isin(names, RC.HOLD_OUT)
M = GD.Motion(WANT, lift_fn=GD.lift_literature); MF = GD.Motion(WANT[FIT], lift_fn=GD.lift_literature); C = RC.load_candidates(with_mintravel=False)

def prm_of(x, br, ring):
    p = dict(b=(float(x[0]), float(x[1])), a1=float(np.clip(x[2], 20, 160)), a2=float(np.clip(x[3], 20, 160)), branch=br); p["w"] = None if ring else (float(x[4]), float(x[5])); return p

def obj(x, br, ring, exact=False):
    ch = GD.Chain3(prm_of(x, br, ring)); r = ch.kin(MF)
    if r is None: return 1e3
    A, mg, ok, *_ = r
    if not ok.all(): return 600 + 100 * (~ok).mean()
    res = GD.fit_minimax(A, MF.lift, ring, 60.0)[1] if exact else GD.fit_lsq(A, MF.lift, ring)[1]
    return float(res.max()) + 10 * max(0.0, 20 - mg.min())

rng = np.random.default_rng(11); out = {}
for tag, ring in (("ring", True), ("3R", False)):
    p = C[tag]["prm"]; x_lead = np.r_[p["b"][0], p["b"][1], p["a1"], p["a2"]] if ring else np.r_[p["b"][0], p["b"][1], p["a1"], p["a2"], p["w"][0], p["w"][1]]
    starts = [(x_lead, int(p["branch"]))] + [(x_lead + rng.normal(0, 25, len(x_lead)), int(rng.choice([-1, 1]))) for _ in range(5)]
    cands = []
    for x0, br in starts:
        r = minimize(obj, x0, args=(br, ring), method="Nelder-Mead", options=dict(maxiter=500, xatol=0.1, fatol=0.01)); cands.append((r.fun, r.x, br))
        print(tag, "start", round(r.fun, 2), f"{time.time() - t0:.0f}s", flush=True)
    cands.sort(key=lambda t: t[0]); f, x, br = cands[0]
    r = minimize(obj, x, args=(br, ring, True), method="Nelder-Mead", options=dict(maxiter=200, xatol=0.05, fatol=0.005)); x = r.x
    ch = GD.Chain3(prm_of(x, br, ring)); A, mg, ok, *_ = ch.kin(MF); xo, _ = GD.fit_minimax(A, MF.lift, ring, 60.0)
    A2, mg2, ok2, *_ = ch.kin(M); res = GD.residual(A2, xo, M.lift)
    out[tag] = dict(params=prm_of(x, br, ring), worst_all_mm=round(float(res.max()), 2), p95_mm=round(float(np.percentile(res, 95)), 2),
                    worst_held_out_mm=round(float(res[~FIT].max()), 2), singular_margin_fit=round(float(mg.min()), 1), closes=round(float(ok2.mean()), 3),
                    lead_rig_law_optimum_under_literature_refit_x=None)
    print(tag, out[tag], f"{time.time() - t0:.0f}s", flush=True)
out["note"] = "literature law max |GH displacement| on the clips: %.1f mm" % float(np.linalg.norm(M.lift, axis=1).max())
RC.jdump(out, "girdle_lit.json")
