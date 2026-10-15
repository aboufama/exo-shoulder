"""JUDGE R2: does any exo part enter the body? Exact depth (exact closest point on the posed body mesh,
judge/sdist.py) of every part vertex near the body, every step-th frame of every clip; inside = the integer winding
number (the posed rig self-intersects in deep poses - armpit, elbow - where a pseudo-normal sign does not exist).
Independent of the pipeline's skin maps. Validated against brute force in judge/test_sdist.py.
Also per part (2026-10-15, a measurement addition; max_depth is unchanged): who owns it (this project's parts, BOTTOM
included, vs the user's own arm parts, parts_full.json material "user part"), and its ATTRIBUTABLE depth: the depth
beyond the rig's own self-intersection (the rig's arm lies in its chest, its forearm in its biceps - no soft-tissue
contact model): a part on a limb counts in full inside its own limb and, inside another body region, only as far as it
goes deeper than its own limb's skin under it (judge/body_regions.py, validated in judge/test_body_contact.py).
Body model: the rig (avg/body_pose.py), or the user-fitted rig with BODY_FIT=user (forearm and elbow bounded by the
user's own arm parts; recorded in the output).
    python3 judge/body_contact.py <design dir|id> [--step 2] [--jobs N] [--out path]  -> <design>/judge/body_contact.json
--jobs splits the frames over N processes (same measurement, merged in frame order; default min(4, cores))."""
import argparse, contextlib, json, multiprocessing as mp, os, time
import numpy as np
from scipy.spatial import cKDTree
from common import design_dir, load_parts, frames
from sdist import Mesh
import body_regions as BR
ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--step", type=int, default=2); ap.add_argument("--tol", type=float, default=0.5)
ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1)); ap.add_argument("--out", default=None, help="output json (default <design>/judge/body_contact.json)")
a = ap.parse_args(); dd = design_dir(a.design)
import body_pose as BP, scene_export as SE
parts = load_parts(dd); F = BP.F
try: OWNER = {(p["group"], p["name"]): ("user" if p.get("material") == "user part" else "ours") for p in json.load(open(os.path.join(dd, "parts_full.json")))["parts"]}
except Exception: OWNER = {}
owner = lambda g, n: OWNER.get((g, n), "ours")
_sk = BP._rig().skin; _W = np.zeros((_sk["n"], 5)); np.add.at(_W, (np.repeat(np.arange(_sk["n"]), 4), _sk["wi"].ravel()), _sk["ww"].ravel())
FREG = BR.face_regions(F, BR.vertex_regions(_W))                                 # trunk / upper arm / forearm per skin face

def depths(item):
    """per part: max depth (mm) inside the body in one frame (None: not near the body)"""
    clip, fi, fr = item; X, pose = SE.frame_xforms(fr); V = BP.posed(pose); vt = cKDTree(V); out = {}; Q = {}
    for g, n, P0, _ in parts:
        if g not in X: continue
        R, t = X[g]; P = P0 @ np.asarray(R).T + t; near = vt.query(P, distance_upper_bound=25.0)[0] < 25.0
        if near.any(): Q[f"{g}|{n}"] = P[near]
    if not Q: return clip, fi, [round(v) for v in fr["p"]], out, {}
    A = np.concatenate(list(Q.values())); M = Mesh(V, F, 2.0).build_grid(1.0, A.min(0) - 20, A.max(0) + 20)    # one body + winding grid per frame
    R = BR.Regions(V, F, FREG); att = {}
    for k, P in Q.items():
        out[k] = M.max_depth(P, a.tol)[0]
        if out[k] <= a.tol: att[k] = (0.0, None); continue
        g = k.split("|")[0]; s, _ = M.tree.query(P); c = np.where(s > a.tol)[0]; c = c[M.winding_at(P[c], s[c]) >= 1]
        d = M.closest(P[c])[0]; dep, _, kind = BR.attributable_depth(M, R, BR.OWN.get(g), P[c], d, a.tol); att[k] = (dep, kind)
    return clip, fi, [round(v) for v in fr["p"]], out, att

if __name__ == "__main__":
    BP.posed(dict(plane=0, elev=0, axial=0, flex=12, pron=0))                    # build the rig once before forking
    res = {f"{g}|{n}": dict(owner=owner(g, n), max_depth=0.0, frames=0, worst=None, attributable_depth=0.0, attributable_frames=0, attributable_worst=None, attributable_kind=None) for g, n, _, _ in parts}; t0 = time.time(); nf = 0
    todo = list(frames(dd, a.step))
    with (mp.get_context("fork").Pool(a.jobs) if a.jobs > 1 else contextlib.nullcontext()) as pool:
        it = pool.imap(depths, todo, chunksize=2) if pool else map(depths, todo)
        for clip, fi, p, out, att in it:                                         # frame order: same tie-breaking as one process
            nf += 1
            for k, dep in out.items():
                r = res[k]
                if dep > a.tol: r["frames"] += 1
                if dep > r["max_depth"]: r["max_depth"] = round(dep, 2); r["worst"] = [clip, fi, p]
                ad, kind = att.get(k, (0.0, None))
                if ad > a.tol: r["attributable_frames"] += 1
                if ad > r["attributable_depth"]: r["attributable_depth"] = round(ad, 2); r["attributable_worst"] = [clip, fi, p]; r["attributable_kind"] = kind
    mx = lambda key, who=None: max([r[key] for r in res.values() if who is None or r["owner"] == who], default=0.0)
    wp = lambda key, who=None: max([k for k in res if who is None or res[k]["owner"] == who] or [None], key=lambda k: res[k][key] if k else 0)
    out = dict(step=a.step, tol_mm=a.tol, frames_checked=nf, seconds=round(time.time() - t0), jobs=a.jobs, body_model=BP.BODY_FIT or "rig",
               inside="integer winding number (grid + segment crossings), depth = exact distance to the nearest surface (judge/sdist.py)", parts=res, worst_part=wp("max_depth"), max_depth=mx("max_depth"),
               max_depth_ours=mx("max_depth", "ours"), max_depth_user=mx("max_depth", "user"),
               attributable=dict(rule="depth beyond the rig's own self-intersection (judge/body_regions.py): in full inside the part's own limb, elsewhere only below its own limb's skin",
                                 max_depth=mx("attributable_depth"), worst_part=wp("attributable_depth"), max_depth_ours=mx("attributable_depth", "ours"), worst_part_ours=wp("attributable_depth", "ours"),
                                 max_depth_user=mx("attributable_depth", "user"), worst_part_user=wp("attributable_depth", "user")))
    path = a.out or os.path.join(dd, "judge", "body_contact.json"); os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True); json.dump(out, open(path, "w"), indent=1)
    bad = {k: v for k, v in res.items() if v["max_depth"] > a.tol}
    at = out["attributable"]
    print(f"body contact ({out['body_model']}): {nf} frames, {len(bad)} of {len(res)} parts enter the body by > {a.tol} mm (worst {out['max_depth']} mm: {out['worst_part']}); "
          f"ours {out['max_depth_ours']} mm, user's {out['max_depth_user']} mm; attributable (beyond the rig's self-intersection): ours {at['max_depth_ours']} mm ({at['worst_part_ours']}), user's {at['max_depth_user']} mm")
    for k, v in sorted(bad.items(), key=lambda kv: -kv[1]["max_depth"])[:12]: print(f"  {v['max_depth']:6.2f} mm in {v['frames']:3d} frames (attributable {v['attributable_depth']:6.2f} mm in {v['attributable_frames']:3d}, {v['attributable_kind']})  [{v['owner']}] {k[:60]}  worst {v['worst']}")
