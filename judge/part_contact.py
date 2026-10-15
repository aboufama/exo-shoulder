"""JUDGE R6: do parts that move relative to each other interpenetrate? For every pair of parts in different motion groups,
every step-th frame: vertices of A inside B (winding number + exact depth to B's welded tessellation; judge/sdist.py,
validated in judge/test_sdist.py; a B left open after welding is tested by the x / y / z ray majority + the generalized
winding number, and listed). Geometry only - does not use the pipeline's member fields. Designed coaxial fits at a shared joint (pin in sleeve, washer on seat) sit within tol.
    python3 judge/part_contact.py <design dir|id> [--step 4] [--tol 0.15] [--jobs N]  -> <design>/judge/part_contact.json
--jobs splits the frames over N processes (same measurement, merged in frame order; default min(4, cores))."""
import argparse, contextlib, json, multiprocessing as mp, os, time
import numpy as np
from common import design_dir, load_parts, frames
from sdist import Mesh
ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--step", type=int, default=4); ap.add_argument("--tol", type=float, default=0.15)
ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
a = ap.parse_args(); dd = design_dir(a.design)
import scene_export as SE
parts = load_parts(dd); info = []
for g, n, V, F in parts:                                                       # B side: Mesh welds the tessellation (glb faces
    M = Mesh(V, F).build_grid()                                                # come split at B-rep seams)
    info.append(dict(g=g, n=n, V=V[::2], M=M, lo=V.min(0) - 1.0, hi=V.max(0) + 1.0))
OPEN = [f"{x['g']}|{x['n']}" for x in info if not x["M"].closed]               # holes after welding: ray majority + GWN
pairs = [(i, j) for i in range(len(info)) for j in range(len(info)) if i != j and info[i]["g"] != info[j]["g"]]

def depths(item):
    """per ordered pair (A in B): depth (mm) of A's vertices inside B in one frame, only where > tol"""
    clip, fi, fr = item; X, _ = SE.frame_xforms(fr); out = {}
    W = {g: (np.asarray(R), np.asarray(t)) for g, (R, t) in X.items()}
    for i, j in pairs:
        A, B = info[i], info[j]
        if A["g"] not in W or B["g"] not in W: continue
        Ra, ta = W[A["g"]]; Rb, tb = W[B["g"]]; P = ((A["V"] @ Ra.T + ta) - tb) @ Rb      # A's vertices in B's frame
        m = np.all((P >= B["lo"]) & (P <= B["hi"]), axis=1)
        if not m.any(): continue
        dep = B["M"].max_depth(P[m], a.tol)[0]
        if dep > a.tol: out[f"{A['g']}|{A['n']}  IN  {B['g']}|{B['n']}"] = dep
    return clip, fi, out

if __name__ == "__main__":
    res = {}; t0 = time.time(); nf = 0; todo = list(frames(dd, a.step))
    with (mp.get_context("fork").Pool(a.jobs) if a.jobs > 1 else contextlib.nullcontext()) as pool:
        it = pool.imap(depths, todo, chunksize=2) if pool else map(depths, todo)
        for clip, fi, out in it:                                                 # frame order: same tie-breaking as one process
            nf += 1
            for k, dep in out.items():
                r = res.setdefault(k, dict(max_depth=0.0, frames=0, worst=None)); r["frames"] += 1
                if dep > r["max_depth"]: r["max_depth"] = round(dep, 2); r["worst"] = [clip, fi]
    out = dict(step=a.step, tol_mm=a.tol, frames_checked=nf, pairs=len(pairs), seconds=round(time.time() - t0), jobs=a.jobs, violations=res,
               open_parts=OPEN, inside="integer winding number on welded tessellations (grid + segment crossings; open parts: x/y/z ray majority + generalized winding number where they disagree), depth = exact distance (judge/sdist.py)",
               max_depth=max([r["max_depth"] for r in res.values()], default=0.0))
    os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(out, open(os.path.join(dd, "judge", "part_contact.json"), "w"), indent=1)
    print(f"part contact: {nf} frames x {len(pairs)} ordered pairs, {len(res)} interpenetrating by > {a.tol} mm (worst {out['max_depth']} mm); {len(OPEN)} open part(s) tested by ray majority + GWN")
    for k, v in sorted(res.items(), key=lambda kv: -kv[1]["max_depth"])[:15]: print(f"  {v['max_depth']:6.2f} mm in {v['frames']:3d} frames  {k[:110]}  worst {v['worst']}")
