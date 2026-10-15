"""Product stills of a design: posed scene GLB (exo only) + motion.json with three cameras framed on the shoulder parts.

    python3 stills_plan.py <design dir> <clip name> <frame fraction 0..1> <out dir>
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import scene_export as SE
DD, clipname, frac, OUT = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]; os.makedirs(OUT, exist_ok=True)
C = json.load(open(os.path.join(DD, "clips.json"))); ci = [c["name"] for c in C["clips"]].index(clipname); fi = int(frac * (len(C["clips"][ci]["frames"]) - 1))
sc = SE.posed_scene(DD, ci, fi, body=False)
import trimesh
crop = trimesh.Scene(); GRID = float(os.environ.get('GRID', 0.12))
for n in sc.graph.nodes_geometry:                                                  # shoulder stills: parts within ~170 mm of the GH centre
    g = sc.graph[n][1]; v = sc.geometry[g].vertices
    if np.linalg.norm(v, axis=1).min() >= 170.0: continue
    q = np.round(v / GRID).astype(np.int64); u, inv = np.unique(q, axis=0, return_inverse=True); inv = inv.ravel()   # vertex clustering
    fa = inv[sc.geometry[g].faces]; fa = fa[(fa[:, 0] != fa[:, 1]) & (fa[:, 1] != fa[:, 2]) & (fa[:, 0] != fa[:, 2])]
    vv = np.zeros((len(u), 3)); np.add.at(vv, inv, v); vv /= np.bincount(inv, minlength=len(u))[:, None]
    crop.add_geometry(trimesh.Trimesh(vv.astype(np.float32), fa, process=False), node_name=n, geom_name=n)
sc = crop; sc.export(os.path.join(OUT, "scene.glb"))
P = np.concatenate([sc.geometry[g].vertices for n in sc.graph.nodes_geometry for g in [sc.graph[n][1]] if n.split("|")[0] in ("base", "cuff") or n.split("|")[0].startswith("l")])
lo, hi = np.percentile(P, 1, 0), np.percentile(P, 99, 0); c = 0.5 * (lo + hi); r = 0.5 * np.linalg.norm(hi - lo)
def cam(dirv, fov, tight=1.0, tgt=None):
    d = np.array(dirv, float); d /= np.linalg.norm(d); t = c if tgt is None else np.array(tgt); dist = tight * r / math.tan(math.radians(fov) / 2) * 1.15
    return dict(pos=(t + d * dist).tolist(), target=t.tolist(), fov=fov, focus=float(dist), fstop=5.6)
# rig frame: x anterior, y up, z right (lateral)
stack = np.array([sc.geometry[g].vertices.mean(0) for n in sc.graph.nodes_geometry for g in [sc.graph[n][1]] if "cap (" in n or "cap Ø" in n])                  # v3 "cap (Ti..." / v4 "cap Ø22 G2 dome"
jt = stack[np.argmin(np.linalg.norm(stack - c, axis=1))] if len(stack) else c
frames = [dict(cam=cam((-0.55, 0.50, 0.68), 24)), dict(cam=cam((-0.35, 0.65, 0.68), 18, tight=0.45, tgt=jt)), dict(cam=cam((0.15, 0.25, 1.0), 24))]
json.dump(dict(fps=1, frames=frames, lights_centre=c.tolist(), light_scale=max(0.6, r / 90.0), exposure=-0.1), open(os.path.join(OUT, "motion.json"), "w"), indent=1)
print("wrote", OUT, "centre", np.round(c, 1), "radius", round(r, 1))
