"""The user's exception (2026-10-14): 3 kinematic DOF + ONE unpowered joint that needs no torque over the full ROM.
A self-aligning passive slider (prismatic, direction e, gravity-balanced) between the thorax plate and the shoulder chain
(Stienen et al. 2009, decoupling rotations and translations: a prismatic joint passes every moment, so the assist
torques still reach the plate, but leaves the translation along e free - the body drives it). The slider sits wherever
the body puts it, so the residual GH misalignment is the part perpendicular to e:
    residual(t) = | P_e (p(t) - lift(t)) |,  P_e = I - e e^T      (still linear in the axis points -> exact minimax LP)
Searched: e (2), and for the offset-axis chains the axis directions; worst over the girdle laws (rig, literature) on the
fitting clips; held-out clips and a +15 mm / -10 mm shrug (arm still, girdle moved along +y) reported, never fitted.
Slider travel = range of the free coordinate s(t) = e . (lift - p).
    python3 p0_selfalign.py -> p0_selfalign.json"""
import json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import girdle as GD
REPO = os.path.dirname(os.path.dirname(HERE)); HOLD = json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["held_out"]
C = json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", "cad_r13_n4_s1343_1", "clips.json")))
names = np.array([c["name"] for c in C["clips"] for f in c["frames"]]); W = np.array([f["want"] for c in C["clips"] for f in c["frames"]], float)
FIT = ~np.isin(names, HOLD); M = GD.Motion(W); MF, MT = GD.Motion(W[FIT]), GD.Motion(W[~FIT])
LAWS = dict(rig=M.lift, literature=GD.lift_literature(W)); SHRUG = dict(shrug_up_15=np.array([0, 15.0, 0]), shrug_down_10=np.array([0, -10.0, 0]))
P0 = json.load(open(os.path.join(HERE, "p0_results.json")))["architectures"]
def stats(x): return dict(max=round(float(np.max(x)), 2), p95=round(float(np.percentile(x, 95)), 2), mean=round(float(np.mean(x)), 2))
def proj(e): e = e / np.linalg.norm(e); return np.eye(3) - np.outer(e, e)
def fitP(A, ys, e, coax):
    Pm = proj(e); AA = np.concatenate([np.einsum("ij,tjk->tik", Pm, A)] * len(ys)); yy = np.concatenate([y @ Pm.T for y in ys])
    return GD.fit_minimax(AA, yy, coax, 60.0)
def res_of(A, x, y, e): return np.linalg.norm((np.einsum("tij,j->ti", A, x) - y) @ proj(e).T, axis=1)
def travel(A, x, y, e): s = (y - np.einsum("tij,j->ti", A, x)) @ (e / np.linalg.norm(e)); return float(np.ptp(s)), float(s.min()), float(s.max())
out = {}
# --- 1. spherical chain (every axis through one centre, the centre rides the slider): residual = |P_e (lift - c)|
for law_set in (("rig",), ("literature",), ("rig", "literature")):
    def f(v):
        e = GD.bvec(v[0], v[1]); Pm = proj(e); c = np.array(v[2:5]); return max(float(np.linalg.norm((LAWS[l][FIT] - c) @ Pm.T, axis=1).max()) for l in law_set)
    best = min((minimize(f, [az, el, 0, 10, 0], method="Nelder-Mead", options=dict(maxiter=3000, xatol=0.01, fatol=0.001)) for az in (0, 90, 180, 270) for el in (30, 60, 85)), key=lambda r: r.fun)
    e = GD.bvec(best.x[0], best.x[1]); c = best.x[2:5]; row = dict(e=e.round(3).tolist(), centre_mm=c.round(1).tolist())
    for l, y in LAWS.items(): row[l] = dict(fit=stats(np.linalg.norm((y[FIT] - c) @ proj(e).T, axis=1)), held_out=stats(np.linalg.norm((y[~FIT] - c) @ proj(e).T, axis=1)),
                                        travel_mm=round(float(np.ptp((y - c) @ e)), 1))
    for k, d in SHRUG.items(): row[k] = stats(np.linalg.norm((LAWS[law_set[-1]] + d - c) @ proj(e).T, axis=1))
    out[f"spherical + slider, fitted to {'+'.join(law_set)}"] = row
    print(f"spherical + 1 passive slider, fitted to {'+'.join(law_set):15s}: e {row['e']}  rig worst {row['rig']['fit']['max']:5.2f}/{row['rig']['held_out']['max']:5.2f}  literature {row['literature']['fit']['max']:5.2f}/{row['literature']['held_out']['max']:5.2f} mm  travel {row['literature']['travel_mm']} mm  shrug +15: {row['shrug_up_15']['max']}", flush=True)
# --- 2. offset-axis 3-DOF chains + slider
def prm_of(x, br, ring): p = dict(b=(float(x[0]), float(x[1])), a1=float(np.clip(x[2], 20, 160)), a2=float(np.clip(x[3], 20, 160)), branch=br); p["w"] = None if ring else (float(x[6]), float(x[7])); return p
for arch, key, ring in (("2R+ring", "3 DOF: 2R shoulder (offset axes) + humeral-rotation ring", True), ("3R", "3 DOF: 3R, offset axes", False)):
    p = P0[key]["params"]; br = int(p["branch"])
    for law_set in (("literature",), ("rig", "literature")):
        def obj(v, exact):
            ch = GD.Chain3(prm_of(v, br, ring)); r = ch.kin(MF)
            if r is None: return 1e3
            A, mg, ok, *_ = r
            if not ok.all(): return 600.0
            e = GD.bvec(v[4], v[5]); ys = [LAWS[l][FIT] for l in law_set]
            if exact: res = fitP(A, ys, e, ring)[1]
            else:
                Pm = proj(e); AA = np.concatenate([np.einsum("ij,tjk->tik", Pm, A)] * len(ys)); yy = np.concatenate([y @ Pm.T for y in ys]); res = GD.fit_lsq(AA, yy, ring)[1]
            return float(res.max()) + 10 * max(0.0, 20 - mg.min())
        best = None; t0 = time.time()
        for e0 in ((90.0, 80.0), (0.0, 60.0), (180.0, 60.0)):
            v0 = [p["b"][0], p["b"][1], p["a1"], p["a2"], e0[0], e0[1]] + ([] if ring else list(p["w"]))
            r = minimize(obj, v0, args=(False,), method="Nelder-Mead", options=dict(maxiter=1200, xatol=0.1, fatol=0.01))
            if best is None or r.fun < best.fun: best = r
        r = minimize(obj, best.x, args=(True,), method="Nelder-Mead", options=dict(maxiter=300, xatol=0.05, fatol=0.005)); v = r.x
        ch = GD.Chain3(prm_of(v, br, ring)); e = GD.bvec(v[4], v[5]); A, mg, *_ = ch.kin(MF); x, _ = fitP(A, [LAWS[l][FIT] for l in law_set], e, ring)
        Aa, *_ = ch.kin(M); At, mgt, *_ = ch.kin(MT); row = dict(e=e.round(3).tolist(), params={k: val for k, val in prm_of(v, br, ring).items()}, margin_fit_held_out=[round(float(mg.min()), 1), round(float(mgt.min()), 1)], _x=x.tolist())
        for l, y in LAWS.items(): row[l] = dict(fit=stats(res_of(A, x, y[FIT], e)), held_out=stats(res_of(At, x, y[~FIT], e)), travel=travel(Aa, x, y, e))
        for k, d in SHRUG.items(): row[k] = stats(res_of(Aa, x, LAWS[law_set[-1]] + d, e))
        if ring: row["ring_travel"] = ch.joint_travel(M)["J3"]
        out[f"{arch} offset axes + slider, fitted to {'+'.join(law_set)}"] = row
        print(f"{arch:8s} offset + 1 passive slider, fitted to {'+'.join(law_set):15s}: e {row['e']}  rig {row['rig']['fit']['max']:5.2f}/{row['rig']['held_out']['max']:5.2f}  literature {row['literature']['fit']['max']:5.2f}/{row['literature']['held_out']['max']:5.2f} mm  slider travel {row['literature']['travel'][0]:.0f} mm  shrug +15 {row['shrug_up_15']['max']}  margin {row['margin_fit_held_out']}  ({time.time() - t0:.0f}s)", flush=True)
json.dump(out, open(os.path.join(HERE, "p0_selfalign.json"), "w"), indent=1)
