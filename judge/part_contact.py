"""JUDGE R6: do parts that move relative to each other interpenetrate? For every pair of parts in different motion groups,
every step-th frame: vertices of A inside B (exact signed distance to B's closed tessellation). Geometry only - does not
use the pipeline's member fields. Designed coaxial fits at a shared joint (pin in sleeve, washer on seat) sit within tol.
    python3 judge/part_contact.py <design dir|id> [--step 4] [--tol 0.15]  -> <design>/judge/part_contact.json"""
import argparse, json, os, time
import numpy as np
from scipy.spatial import cKDTree
from common import design_dir, load_parts, frames
from sdist import signed_distance
ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--step", type=int, default=4); ap.add_argument("--tol", type=float, default=0.15)
a = ap.parse_args(); dd = design_dir(a.design)
import scene_export as SE
parts = load_parts(dd); info = []
for g, n, V, F in parts:
    info.append(dict(g=g, n=n, V=V[::2], Vf=V, F=F, tree=cKDTree(V[F].mean(1)), lo=V.min(0) - 1.0, hi=V.max(0) + 1.0))
pairs = [(i, j) for i in range(len(info)) for j in range(len(info)) if i != j and info[i]["g"] != info[j]["g"]]
res = {}; t0 = time.time(); nf = 0
for clip, fi, fr in frames(dd, a.step):
    X, _ = SE.frame_xforms(fr); nf += 1
    W = {g: (np.asarray(R), np.asarray(t)) for g, (R, t) in X.items()}
    for i, j in pairs:
        A, B = info[i], info[j]
        if A["g"] not in W or B["g"] not in W: continue
        Ra, ta = W[A["g"]]; Rb, tb = W[B["g"]]; P = ((A["V"] @ Ra.T + ta) - tb) @ Rb      # A's vertices in B's frame
        m = np.all((P >= B["lo"]) & (P <= B["hi"]), axis=1)
        if not m.any(): continue
        sd = signed_distance(P[m], B["Vf"], B["F"], tree=B["tree"]); dep = float(max(0.0, -sd.min()))
        if dep > a.tol:
            k = f"{A['g']}|{A['n']}  IN  {B['g']}|{B['n']}"; r = res.setdefault(k, dict(max_depth=0.0, frames=0, worst=None)); r["frames"] += 1
            if dep > r["max_depth"]: r["max_depth"] = round(dep, 2); r["worst"] = [clip, fi]
out = dict(step=a.step, tol_mm=a.tol, frames_checked=nf, pairs=len(pairs), seconds=round(time.time() - t0), violations=res,
           max_depth=max([r["max_depth"] for r in res.values()], default=0.0))
os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(out, open(os.path.join(dd, "judge", "part_contact.json"), "w"), indent=1)
print(f"part contact: {nf} frames x {len(pairs)} ordered pairs, {len(res)} interpenetrating by > {a.tol} mm (worst {out['max_depth']} mm)")
for k, v in sorted(res.items(), key=lambda kv: -kv[1]["max_depth"])[:15]: print(f"  {v['max_depth']:6.2f} mm in {v['frames']:3d} frames  {k[:110]}  worst {v['worst']}")
