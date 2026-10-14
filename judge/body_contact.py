"""JUDGE R2: does any exo part enter the body? Exact signed distance (closest point on the nearest triangles of the posed,
closed body mesh) of every part vertex, every step-th frame of every clip. Independent of the pipeline's skin maps.
    python3 judge/body_contact.py <design dir|id> [--step 2] [--jobs N]  -> <design>/judge/body_contact.json
--jobs splits the frames over N processes (same measurement, merged in frame order; default min(4, cores))."""
import argparse, contextlib, json, multiprocessing as mp, os, time
import numpy as np
from scipy.spatial import cKDTree
from common import design_dir, load_parts, frames
from sdist import signed_distance
ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--step", type=int, default=2); ap.add_argument("--tol", type=float, default=0.5)
ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
a = ap.parse_args(); dd = design_dir(a.design)
import body_pose as BP, scene_export as SE
parts = load_parts(dd); F = BP.F

def depths(item):
    """per part: max depth (mm) inside the body in one frame (None: not near the body)"""
    clip, fi, fr = item; X, pose = SE.frame_xforms(fr); V = BP.posed(pose); vt = cKDTree(V); ct = cKDTree(V[F].mean(1)); out = {}
    for g, n, P0, _ in parts:
        if g not in X: continue
        R, t = X[g]; P = P0 @ np.asarray(R).T + t; near = vt.query(P, distance_upper_bound=25.0)[0] < 25.0
        if not near.any(): continue
        sd = signed_distance(P[near], V, F, tree=ct); out[f"{g}|{n}"] = float(max(0.0, -sd.min()))
    return clip, fi, [round(v) for v in fr["p"]], out

if __name__ == "__main__":
    BP.posed(dict(plane=0, elev=0, axial=0, flex=12, pron=0))                    # build the rig once before forking
    res = {f"{g}|{n}": dict(max_depth=0.0, frames=0, worst=None) for g, n, _, _ in parts}; t0 = time.time(); nf = 0
    todo = list(frames(dd, a.step))
    with (mp.get_context("fork").Pool(a.jobs) if a.jobs > 1 else contextlib.nullcontext()) as pool:
        it = pool.imap(depths, todo, chunksize=2) if pool else map(depths, todo)
        for clip, fi, p, out in it:                                              # frame order: same tie-breaking as one process
            nf += 1
            for k, dep in out.items():
                r = res[k]
                if dep > a.tol: r["frames"] += 1
                if dep > r["max_depth"]: r["max_depth"] = round(dep, 2); r["worst"] = [clip, fi, p]
    out = dict(step=a.step, tol_mm=a.tol, frames_checked=nf, seconds=round(time.time() - t0), jobs=a.jobs,
               parts=res, worst_part=max(res, key=lambda k: res[k]["max_depth"]), max_depth=max(r["max_depth"] for r in res.values()))
    os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(out, open(os.path.join(dd, "judge", "body_contact.json"), "w"), indent=1)
    bad = {k: v for k, v in res.items() if v["max_depth"] > a.tol}
    print(f"body contact: {nf} frames, {len(bad)} of {len(res)} parts enter the body by > {a.tol} mm (worst {out['max_depth']} mm: {out['worst_part']})")
    for k, v in sorted(bad.items(), key=lambda kv: -kv[1]["max_depth"])[:12]: print(f"  {v['max_depth']:6.2f} mm in {v['frames']:3d} frames  {k[:70]}  worst {v['worst']}")
