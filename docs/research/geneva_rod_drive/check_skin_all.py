"""Skeptic's independent check: signed distance (igl winding number, inside negative) of EVERY part of a built design
(exo.glb mesh as built, not re-made by the builder) posed by the design's own clips.json (scene_export.frame_xforms, the
judges' convention), against the judges' posed skin (avg/body_pose), every frame of every clip.
   python3 docs/research/geneva_rod_drive/check_skin_all.py <design dir> <out.json> [step=1] [groups=all|g1,g2]
   env: CLIPS="Raise overhead;Comb hair" (clip filter), NAMES="D9-01;MR63ZZ" (part-name substrings),
        SRC=workspace (the design's workspace.json poses that close, instead of the clips)
Per part: min signed distance (mm), frames inside (< 0), frames under 0.3 mm, where. Written for
docs/research/geneva-rod-gen5_fix_check.md (independent check of user_geneva_rod_v2)."""
import json, os, sys, time
R = "/home/user/exo-shoulder"
for p in ("pipeline/full-exo", "pipeline/avg"): sys.path.insert(0, os.path.join(R, p))
import numpy as np, trimesh, igl
from scipy.spatial import cKDTree
import body_pose as BP, scene_export as SE
DD, OUT = sys.argv[1], sys.argv[2]; STEP = int(sys.argv[3]) if len(sys.argv) > 3 else 1
GROUPS = None if len(sys.argv) <= 4 or sys.argv[4] == "all" else set(sys.argv[4].split(","))
src = trimesh.load(os.path.join(DD, "exo.glb")); parts = {}
for node in src.graph.nodes_geometry:
    T_, gn = src.graph[node]; g, n = node.split("|")[:2]
    if GROUPS and g not in GROUPS: continue
    if os.environ.get("NAMES") and not any(x in n for x in os.environ["NAMES"].split(";")): continue
    m = src.geometry[gn].copy(); m.apply_transform(T_)
    ns = int(np.clip(m.area / 0.5, 2000, 80000)); P = np.concatenate([trimesh.sample.sample_surface(m, ns, seed=7)[0], m.vertices])
    parts.setdefault((g, n), []).append(P)
parts = {k: np.concatenate(v) for k, v in parts.items()}
BF = np.ascontiguousarray(BP.F, np.int64); C = json.load(open(os.path.join(DD, "clips.json")))
if os.environ.get("SRC") == "workspace":
    W = json.load(open(os.path.join(DD, "workspace.json"))); C = dict(clips=[dict(name="workspace", frames=[f for f in W["poses"] if f.get("closes")])])
    print("workspace poses closing:", len(C["clips"][0]["frames"]), "of", len(W["poses"]), flush=True)
res = {f"{g}|{n}": dict(min_sd=99.0, where=None, frames_neg=0, frames_lt03=0) for g, n in parts}
t0 = time.time(); nf = 0
CL = os.environ.get("CLIPS")
for c in C["clips"]:
    if CL and c["name"] not in CL.split(";"): continue
    for fi in range(0, len(c["frames"]), STEP):
        fr = c["frames"][fi]; X, pose = SE.frame_xforms(fr); V = np.ascontiguousarray(BP.posed(pose), float); vt = cKDTree(V)
        keys, Qs = [], []
        for (g, n), P0 in parts.items():
            if g not in X: continue
            Rm, t = X[g]; Q = P0 @ np.asarray(Rm).T + t
            near = vt.query(Q, distance_upper_bound=15.0)[0] < 15.0
            if near.any(): keys.append(f"{g}|{n}"); Qs.append(Q[near])
        if Qs:
            A = np.ascontiguousarray(np.concatenate(Qs), float); d = np.sqrt(igl.point_mesh_squared_distance(A, V, BF)[0])
            w = igl.fast_winding_number(V, BF, A) > 0.5; SD = np.where(w, -d, d); o = 0
            for k, Q in zip(keys, Qs):
                sd = SD[o:o + len(Q)]; o += len(Q); i = int(np.argmin(sd)); r = res[k]
                if sd[i] < 0: r["frames_neg"] += 1
                if sd[i] < 0.3: r["frames_lt03"] += 1
                if sd[i] < r["min_sd"]: r["min_sd"] = round(float(sd[i]), 3); r["where"] = [c["name"], fi, [round(float(x), 2) for x in Q[i]]]
        nf += 1
        if nf % 100 == 0: print(f"{nf} frames {time.time()-t0:.0f}s", flush=True)
json.dump(dict(design=DD, step=STEP, frames=nf, seconds=round(time.time() - t0), parts=dict(sorted(res.items(), key=lambda kv: kv[1]["min_sd"]))), open(OUT, "w"), indent=1)
print("done", nf, "frames", round(time.time() - t0), "s")
for k, v in sorted(res.items(), key=lambda kv: kv[1]["min_sd"])[:25]: print(f"{v['min_sd']:8.3f} neg {v['frames_neg']:4d} <0.3 {v['frames_lt03']:4d}  {k[:90]}  {v['where']}")
