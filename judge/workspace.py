"""JUDGE R16: does the BUILT design (L1 keep-out CAD, exo.glb) move through the functional everyday workspace? For every
pose in <design>/workspace.json (written by band_to_design.py from the workspace envelope it was built on), at the
chain configuration the design takes there: the chain must close, no shoulder-exo part may enter the body (same test
as R2: exact closest point + winding number, judge/sdist.py) and no two parts that move relative to each other may
interpenetrate (as R6). Independent of the evaluator's own feasibility flags (reported alongside for comparison).
The user's forearm parts (group F) are left out of the body test: the rig's forearm is a size mismatch with the
user's cuff (R2 reports it), not part of the shoulder mechanism.
    python3 judge/workspace.py <design dir|id> [--step 1] [--jobs N]  -> <design>/judge/workspace.json"""
import argparse, contextlib, json, multiprocessing as mp, os, time
import numpy as np
from scipy.spatial import cKDTree
from common import design_dir, load_parts
from sdist import Mesh
ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--step", type=int, default=1); ap.add_argument("--jobs", type=int, default=min(4, os.cpu_count() or 1))
ap.add_argument("--tol_body", type=float, default=0.5); ap.add_argument("--tol_parts", type=float, default=0.15); ap.add_argument("--skip_groups", default="F")
a = ap.parse_args(); dd = design_dir(a.design); SKIP = set(x for x in a.skip_groups.split(",") if x)
import body_pose as BP, scene_export as SE, trimesh
W = json.load(open(os.path.join(dd, "workspace.json"))); poses = W["poses"][::a.step]
parts = load_parts(dd); info = []
for g, n, V, F in parts:
    m = trimesh.Trimesh(V, F, process=False); m.merge_vertices(digits_vertex=4); m.update_faces(m.nondegenerate_faces()); closed = bool(m.is_watertight)
    info.append(dict(g=g, n=n, V=V, Vs=V[::2], closed=closed, M=Mesh(np.asarray(m.vertices, float), np.asarray(m.faces)).build_grid() if closed else None, lo=V.min(0) - 1.0, hi=V.max(0) + 1.0))
pairs = [(i, j) for i in range(len(info)) for j in range(len(info)) if i != j and info[i]["g"] != info[j]["g"] and info[j]["closed"]]

def judge_pose(k):
    fr = poses[k]; res = dict(k=k, p=fr["p"][:3], eval_feasible=fr.get("eval_feasible"), closes=fr["closes"], body_mm=None, body_part=None, parts_mm=None, parts_pair=None)
    if not fr["closes"]: return res
    X, pose = SE.frame_xforms(fr); Wx = {g: (np.asarray(R), np.asarray(t)) for g, (R, t) in X.items()}
    V = BP.posed(pose); vt = cKDTree(V); Q = {}
    for x in info:
        if x["g"] in SKIP or x["g"] not in Wx: continue
        R, t = Wx[x["g"]]; P = x["V"] @ R.T + t; near = vt.query(P, distance_upper_bound=25.0)[0] < 25.0
        if near.any(): Q[(x["g"], x["n"])] = P[near]
    bd, bp = 0.0, None
    if Q:
        A = np.concatenate(list(Q.values())); M = Mesh(V, BP.F, 2.0).build_grid(1.0, A.min(0) - 3, A.max(0) + 3)
        for key, P in Q.items():
            d = M.max_depth(P, a.tol_body)[0]
            if d > bd: bd, bp = d, f"{key[0]}|{key[1]}"
    pd, pp = 0.0, None
    for i, j in pairs:
        A_, B_ = info[i], info[j]
        if A_["g"] not in Wx or B_["g"] not in Wx: continue
        Ra, ta = Wx[A_["g"]]; Rb, tb = Wx[B_["g"]]; P = ((A_["Vs"] @ Ra.T + ta) - tb) @ Rb; m = np.all((P >= B_["lo"]) & (P <= B_["hi"]), axis=1)
        if not m.any(): continue
        d = B_["M"].max_depth(P[m], a.tol_parts)[0]
        if d > pd: pd, pp = d, f"{A_['n'][:40]} IN {B_['n'][:40]}"
    res.update(body_mm=round(bd, 2), body_part=bp, parts_mm=round(pd, 2), parts_pair=pp); return res

if __name__ == "__main__":
    BP.posed(dict(plane=0, elev=0, axial=0, flex=90, pron=0)); t0 = time.time()
    with (mp.get_context("fork").Pool(a.jobs) if a.jobs > 1 else contextlib.nullcontext()) as pool:
        out = list(pool.imap(judge_pose, range(len(poses)), chunksize=4) if pool else map(judge_pose, range(len(poses))))
    ok = [r["closes"] and r["body_mm"] <= a.tol_body and r["parts_mm"] <= a.tol_parts for r in out]
    n = len(out); share = float(np.mean(ok)) if n else 0.0
    why = dict(chain_does_not_close=float(np.mean([not r["closes"] for r in out])), body_contact=float(np.mean([r["closes"] and r["body_mm"] > a.tol_body for r in out])),
               part_interference=float(np.mean([r["closes"] and r["parts_mm"] > a.tol_parts for r in out])))
    agree = float(np.mean([bool(o) == bool(r["eval_feasible"]) for o, r in zip(ok, out)]))
    res = dict(poses=n, step=a.step, share_passing=round(share, 4), fails=dict((k, round(v, 4)) for k, v in why.items()), evaluator_agreement=round(agree, 3),
               skip_groups=sorted(SKIP), tol_body_mm=a.tol_body, tol_parts_mm=a.tol_parts, seconds=round(time.time() - t0), per_pose=out)
    os.makedirs(os.path.join(dd, "judge"), exist_ok=True); json.dump(res, open(os.path.join(dd, "judge", "workspace.json"), "w"), indent=1)
    print(f"workspace (R16): {n} functional-workspace poses, {100 * share:.1f} % pass (chain closes, body <= {a.tol_body} mm, parts <= {a.tol_parts} mm); "
          f"fails: " + ", ".join(f"{k} {100 * v:.1f}%" for k, v in why.items()) + f"; agrees with the evaluator on {100 * agree:.0f}% of poses")
