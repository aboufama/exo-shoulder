"""B' (recommended, P0 section 8) over the whole plausible everyday workspace, not just the 6 fitting clips:
2R pointing shoulder (offset axes) + humeral-rotation ring + ONE torque-free passive slider, thorax plate.
Workspace = the red team's (pipeline/redteam/rt_common.plausible): plane -90..150, elevation 0..170, humeral rotation
r = axial + plane in -90..90; fit on a 10 deg grid, evaluate on the 5 deg grid and on the 8 clips (held-out ones
included, never fitted). Objective: worst GH misalignment over BOTH girdle laws (rig, literature), singular margin
>= MARGIN deg over the fitting grid. Also: where the arm never points over the workspace (the 2R singular direction).
    python3 p0_selfalign_ws.py -> p0_selfalign_ws.json"""
import json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(REPO, "pipeline", "redteam")); import girdle as GD
from rt_common import plausible
MARGIN = float(os.environ.get("MARGIN", 15.0)); ARCH = os.environ.get("ARCH", "ring")      # ring | 3r
def grid(step):
    pl, el, r = np.meshgrid(np.arange(-90, 151, step), np.arange(0, 171, step), np.arange(-90, 91, step), indexing="ij"); pl, el, r = pl.ravel(), el.ravel(), r.ravel()
    k = plausible(pl, el); P = np.c_[pl[k], el[k], r[k] - pl[k], np.full(k.sum(), 12.0), np.zeros(k.sum())]; return P
PF, PE = grid(10.0), grid(5.0); MF, ME = GD.Motion(PF), GD.Motion(PE)
C = json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", "cad_r13_n4_s1343_1", "clips.json")))
names = np.array([c["name"] for c in C["clips"] for f in c["frames"]]); WC = np.array([f["want"] for c in C["clips"] for f in c["frames"]], float); MC = GD.Motion(WC)
HOLD = json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["held_out"]; HO = np.isin(names, HOLD)
LAW = lambda M, P: dict(rig=M.lift, literature=GD.lift_literature(P))
LF, LE, LC = LAW(MF, PF), LAW(ME, PE), LAW(MC, WC)
print(f"workspace: fit grid {len(PF)} poses, eval grid {len(PE)} poses", flush=True)
# where the arm never points over the workspace
cand = GD.unit(np.random.default_rng(1).normal(size=(20000, 3))); ang = np.zeros(len(cand))
for k0 in range(0, len(cand), 2000): ang[k0:k0 + 2000] = np.degrees(np.arccos(np.clip(np.abs(cand[k0:k0 + 2000] @ ME.hdir.T), 0, 1))).min(1)
NEVER = cand[np.argmax(ang)]; print(f"over the workspace the arm never comes within {ang.max():.1f} deg of {NEVER.round(3)}", flush=True)
def proj(e): e = e / np.linalg.norm(e); return np.eye(3) - np.outer(e, e)
def prm_of(v, br): return dict(b=(float(v[0]), float(v[1])), a1=float(np.clip(v[2], 20, 160)), a2=float(np.clip(v[3], 20, 160)), branch=br, w=None if ARCH == "ring" else (float(v[6]), float(v[7])))
def fit(A, laws, e, exact):
    Pm = proj(e); AA = np.concatenate([np.einsum("ij,tjk->tik", Pm, A)] * len(laws)); yy = np.concatenate([y @ Pm.T for y in laws])
    return GD.fit_minimax(AA, yy, ARCH == "ring", 60.0) if exact else GD.fit_lsq(AA, yy, ARCH == "ring")
def obj(v, br, exact):
    ch = GD.Chain3(prm_of(v, br)); r = ch.kin(MF)
    if r is None: return 1e3
    A, mg, ok, *_ = r
    pen = 100 * (~ok).mean() + 5 * max(0.0, MARGIN - float(np.min(np.where(ok, mg, -90))))
    e = GD.bvec(v[4], v[5]); res = fit(A[ok], [LF["rig"][ok], LF["literature"][ok]], e, exact)[1]
    return float(res.max()) + pen
S = json.load(open(os.path.join(HERE, "p0_selfalign.json")))["2R+ring offset axes + slider, fitted to rig+literature" if ARCH == "ring" else "3R offset axes + slider, fitted to rig+literature"]
p = S["params"]; e0 = np.array(S["e"]); br0 = int(p["branch"]); t0 = time.time(); best = None
wx = [] if ARCH == "ring" else list(p["w"])
starts = [[p["b"][0], p["b"][1], p["a1"], p["a2"]] + GD.azel(e0) + wx] + ([GD.azel(s * NEVER) + [90.0, 90.0] + GD.azel(e0) for s in (1, -1)] if ARCH == "ring" else [])
for v0 in starts:
    for br in (br0, -br0):
        r = minimize(obj, v0, args=(br, False), method="Nelder-Mead", options=dict(maxiter=600, xatol=0.1, fatol=0.01))
        print(f"  start {np.round(v0, 1)} branch {br}: lsq objective {r.fun:.2f} ({time.time() - t0:.0f}s)", flush=True)
        if best is None or r.fun < best[0]: best = (r.fun, r.x, br)
r = minimize(obj, best[1], args=(best[2], True), method="Nelder-Mead", options=dict(maxiter=200, xatol=0.05, fatol=0.005)); v, br = r.x, best[2]
ch = GD.Chain3(prm_of(v, br)); e = GD.bvec(v[4], v[5]); A, mg, ok, *_ = ch.kin(MF); x, _ = fit(A[ok], [LF["rig"][ok], LF["literature"][ok]], e, True)
def res(M, L):
    A, mg, ok, *_ = ch.kin(M); out = {}
    for l, y in L.items():
        rr = np.linalg.norm((np.einsum("tij,j->ti", A, x) - y) @ proj(e).T, axis=1); rr = np.where(ok, rr, np.nan)
        out[l] = dict(max=round(float(np.nanmax(rr)), 2), p95=round(float(np.nanpercentile(rr, 95)), 2), over_4mm=round(float(np.nanmean(rr > 4)), 3))
    out["closes"] = round(float(ok.mean()), 4); out["margin_min"] = round(float(np.min(np.where(ok, mg, 999))), 1); out["margin_p1"] = round(float(np.percentile(np.where(ok, mg, -90), 1)), 1)
    return out, A, ok
o_ws, A_ws, ok_ws = res(ME, LE)
o_fit, _, _ = res(GD.Motion(WC[~HO]), dict(rig=LC["rig"][~HO], literature=LC["literature"][~HO])); o_ho, _, _ = res(GD.Motion(WC[HO]), dict(rig=LC["rig"][HO], literature=LC["literature"][HO]))
s_ws = (LE["literature"] - np.einsum("tij,j->ti", A_ws, x)) @ (e / np.linalg.norm(e))
out = dict(arch=ARCH, params=prm_of(v, br), e=e.round(3).tolist(), axis_points=x.tolist(), margin_required=MARGIN, workspace_5deg=o_ws, clips_fitting=o_fit, clips_held_out=o_ho,
           slider_travel_literature_mm=round(float(np.ptp(s_ws[ok_ws])), 1), joint_travel=ch.joint_travel(ME), never_points_workspace=dict(dir=NEVER.round(3).tolist(), deg=round(float(ang.max()), 1)))
print(json.dumps({k: v_ for k, v_ in out.items() if k != "axis_points"}, indent=1), flush=True)
json.dump(out, open(os.path.join(HERE, f"p0_selfalign_ws_{ARCH}.json"), "w"), indent=1)
