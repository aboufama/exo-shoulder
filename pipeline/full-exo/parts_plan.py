"""Close-up stills of a design's custom parts (no body), one part per frame, for a CAD review on exo-blender-cycles
(joint-render/film_client.py stills). Parts come from exo.glb in their group frames; each is centred, turned to its
principal axes (longest along x) and laid out in a row; two cameras per part (outer face three-quarter, skin side).

    python3 parts_plan.py <design dir> <out dir> [name prefix ...]   (default prefixes: D6 D5)
"""
import json, math, os, sys
import numpy as np, trimesh
DD, OUT = sys.argv[1], sys.argv[2]; PRE = tuple(sys.argv[3:]) or ("D6", "D5"); os.makedirs(OUT, exist_ok=True)
src = trimesh.load(os.path.join(DD, "exo.glb")); groups = {}
for node in src.graph.nodes_geometry:
    T_, gn = src.graph[node]; g, nm = node.split("|")[:2]
    if not nm.startswith(PRE): continue
    m = src.geometry[gn].copy(); m.apply_transform(T_); groups.setdefault(nm, []).append(m)
names = sorted(groups); sc = trimesh.Scene(); frames = []; x0 = 0.0
for nm in names:
    m = trimesh.util.concatenate(groups[nm]); V = m.vertices - m.vertices.mean(0)
    U, S, Vt = np.linalg.svd(V[:: max(1, len(V) // 20000)], full_matrices=False)
    R = Vt.copy(); R[2] = np.cross(R[0], R[1]); V = V @ R.T                               # principal axes: x longest, z thinnest
    if (V[:, 2] ** 3).sum() < 0: V[:, 1:] *= -1                                          # a consistent side up
    ext = V.max(0) - V.min(0); V[:, 0] += x0 - V[:, 0].min()
    c = (V.max(0) + V.min(0)) / 2; x0 += ext[0] + 40.0
    sc.add_geometry(trimesh.Trimesh(V.astype(np.float32), m.faces, process=False), node_name=f"P|{nm}|0", geom_name=nm)
    r = 0.5 * float(np.linalg.norm(ext)); fov = 28.0; dist = r / math.tan(math.radians(fov / 2)) * 1.15
    for dv in ((0.35, -0.55, 0.76), (0.3, 0.6, -0.74)):
        d = np.array(dv) / np.linalg.norm(dv)
        frames.append(dict(cam=dict(pos=(c + d * dist).tolist(), target=c.tolist(), fov=fov, focus=float(dist), fstop=11.0)))
sc.export(os.path.join(OUT, "scene.glb"))
P = np.concatenate([g.vertices for g in sc.geometry.values()]); lc = ((P.max(0) + P.min(0)) / 2).tolist()
json.dump(dict(fps=1, body=False, frames=frames, lights_centre=lc, light_scale=max(1.0, float(np.ptp(P[:, 0])) / 150.0), exposure=-0.1),
          open(os.path.join(OUT, "motion.json"), "w"), indent=1)
print("parts:", names, f"-> {OUT} ({len(frames)} frames)")
