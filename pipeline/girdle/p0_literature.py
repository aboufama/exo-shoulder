"""P0 re-run against the literature girdle law (girdle.lift_literature: bone-pin clavicle / scapula chain, 2-3x the
rig's GH rise, plus posterior and medial components, plane-dependent). Re-fits the two 3-DOF offset-axis architectures
to (a) the literature law, (b) both laws at once (minimax), and reports every design under both laws. Fit on 6 clips,
2 held out (data/raw/split.json). The repeatable part only: the literature puts +-7-12 mm (1 SD) of GH motion outside
any function of arm orientation, which no chain without an extra joint can follow.
    python3 p0_literature.py -> p0_literature.json"""
import json, math, os, sys, time
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import girdle as GD
REPO = os.path.dirname(os.path.dirname(HERE)); HOLD = json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["held_out"]
C = json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", "cad_r13_n4_s1343_1", "clips.json")))
names = np.array([c["name"] for c in C["clips"] for f in c["frames"]]); W = np.array([f["want"] for c in C["clips"] for f in c["frames"]], float)
FIT = ~np.isin(names, HOLD); M = GD.Motion(W); LAWS = dict(rig=M.lift, literature=GD.lift_literature(W))
P0 = json.load(open(os.path.join(HERE, "p0_results.json")))["architectures"]
def stats(x): return dict(max=round(float(np.max(x)), 2), p95=round(float(np.percentile(x, 95)), 2), mean=round(float(np.mean(x)), 2))
MF = GD.Motion(W[FIT]); MT = GD.Motion(W[~FIT])
def prm_of(x, br, ring): p = dict(b=(float(x[0]), float(x[1])), a1=float(np.clip(x[2], 20, 160)), a2=float(np.clip(x[3], 20, 160)), branch=br); p["w"] = None if ring else (float(x[4]), float(x[5])); return p
def fit_target(A, targets, ring, exact):
    """axis points minimising the worst residual over every target law (stacked frames)"""
    AA = np.concatenate([A] * len(targets)); yy = np.concatenate(targets)
    return (GD.fit_minimax(AA, yy, ring, 60.0) if exact else GD.fit_lsq(AA, yy, ring))
def obj(x, br, ring, laws, exact):
    ch = GD.Chain3(prm_of(x, br, ring)); r = ch.kin(MF)
    if r is None: return 1e3
    A, mg, ok, *_ = r
    if not ok.all(): return 600 + 100 * (~ok).mean()
    res = fit_target(A, [LAWS[l][FIT] for l in laws], ring, exact)[1]
    return float(res.max()) + 10 * max(0.0, 20 - mg.min())
out = {}
for arch, key, ring in (("2R+ring", "3 DOF: 2R shoulder (offset axes) + humeral-rotation ring", True), ("3R", "3 DOF: 3R, offset axes", False)):
    p = P0[key]["params"]; x0 = [p["b"][0], p["b"][1], p["a1"], p["a2"]] + ([] if ring else list(p["w"])); br0 = int(p["branch"])
    for target in (("literature",), ("rig", "literature")):
        t0 = time.time(); best = None
        rng = np.random.default_rng(5)
        for s in range(6):
            xs = np.array(x0, float) + (rng.normal(0, [20, 10, 10, 10] + ([15, 20] if not ring else []), len(x0)) if s else 0); br = br0 if s % 2 == 0 else -br0
            r = minimize(obj, xs, args=(br, ring, target, False), method="Nelder-Mead", options=dict(maxiter=900, xatol=0.1, fatol=0.01))
            if best is None or r.fun < best[0]: best = (r.fun, r.x, br)
        r = minimize(obj, best[1], args=(best[2], ring, target, True), method="Nelder-Mead", options=dict(maxiter=300, xatol=0.05, fatol=0.005))
        prm = prm_of(r.x, best[2], ring); ch = GD.Chain3(prm); A, mg, *_ = ch.kin(MF); x, _ = fit_target(A, [LAWS[l][FIT] for l in target], ring, True)
        rows = {}
        for law, y in LAWS.items():
            for tag, MM, sel in (("fit", MF, FIT), ("held_out", MT, ~FIT)):
                Ak, mgk, *_ = ch.kin(MM); rows[f"{law}|{tag}"] = stats(GD.residual(Ak, x, y[sel]))
        Aall, mga, *_ = ch.kin(M); rows["singular_margin_fit_held_out"] = [round(float(mg.min()), 1), round(float(ch.kin(MT)[1].min()), 1)]
        dirs = [ch.b, ch.c0, GD.Rh_of(0, 0, 0) @ ch.w]; offs = [round(float(np.linalg.norm(x[3 * i:3 * i + 3] - (x[3 * i:3 * i + 3] @ d) * d)), 1) for i, d in enumerate(dirs)]
        out[f"{arch} fitted to {'+'.join(target)}"] = dict(params={k: v for k, v in prm.items()}, axis_offset_from_GH_mm=offs, residual=rows, ring_travel=ch.joint_travel(M)["J3"] if ring else None, _x=x.tolist(), secs=round(time.time() - t0))
        print(f"{arch:8s} fitted to {'+'.join(target):15s}: rig law worst {rows['rig|fit']['max']:6.2f} / held-out {rows['rig|held_out']['max']:6.2f} | literature worst {rows['literature|fit']['max']:6.2f} / held-out {rows['literature|held_out']['max']:6.2f} mm | offsets {offs} | margin {rows['singular_margin_fit_held_out']}", flush=True)
# the P0 (rig-fitted) designs, evaluated under the literature law without refitting
for arch, key in (("2R+ring", "3 DOF: 2R shoulder (offset axes) + humeral-rotation ring"), ("3R", "3 DOF: 3R, offset axes")):
    p = dict(P0[key]["params"]); p["b"] = tuple(p["b"]); p["w"] = None if p.get("w") is None else tuple(p["w"]); ch = GD.Chain3(p); A, *_ = ch.kin(M)
    r = GD.residual(A, np.array(P0[key]["_x"]), LAWS["literature"]); out[f"{arch} P0 (rig-fitted) under the literature law"] = stats(r)
    print(f"{arch:8s} P0 rig-fitted design under the literature law: worst {r.max():.2f} mm", flush=True)
sph = np.linalg.norm(LAWS["literature"], axis=1); gc = (LAWS["literature"].max(0) + LAWS["literature"].min(0)) / 2
out["spherical chain, thorax plate, literature law"] = dict(centre_at_GH=stats(sph), best_fixed_centre_box=stats(np.linalg.norm(LAWS["literature"] - gc, axis=1)))
print("spherical chain under the literature law: worst", round(float(sph.max()), 1), "mm (GH rest centre)")
json.dump(out, open(os.path.join(HERE, "p0_literature.json"), "w"), indent=1)
