"""Underside gap (mm) of each shoulder member to the current skin (avg/body_pose.py): at rest and over the clips.
Underside = exo surface points whose outward normal faces the skin (they bound the air gap)."""
import json, os, sys
import numpy as np, trimesh
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "avg")); import body_pose as BP
DD = sys.argv[1]; C = json.load(open(os.path.join(DD, "clips.json"))); sc = trimesh.load(os.path.join(DD, "exo.glb"))
G = {}
for node in sc.graph.nodes_geometry:
    T_, gname = sc.graph[node]; g, nm = node.split("|")[:2]
    if g not in ("base", "l1", "l2", "l3") or not nm.startswith("D4-0"): continue          # the plates / links, not hardware
    m = sc.geometry[gname].copy(); m.apply_transform(T_); G.setdefault(g, []).append(m)
G = {g: trimesh.util.concatenate(v) for g, v in G.items()}
def gaps(fr):
    """skin-side view: for skin points the mechanism covers (metal straight out along the skin normal, within 40 mm),
    the distance to that metal, grouped by which member it is"""
    pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"])); X = BP.posed(pose)
    sk = trimesh.Trimesh(X, BP.F, process=False); keep = np.linalg.norm(sk.triangles_center, axis=1) < 200
    sub = sk.submesh([np.flatnonzero(keep)], append=True); sp, fi = trimesh.sample.sample_surface(sub, 400000, seed=1); ns = sub.face_normals[fi]
    E, gid = [], []
    for g, m in G.items():
        R = np.array(fr["G"][g]).reshape(3, 3); pe, _ = trimesh.sample.sample_surface(m, 60000, seed=3); E.append(pe @ R.T); gid += [g] * len(pe)
    E = np.concatenate(E); gid = np.array(gid); d, ii = cKDTree(E).query(sp, workers=4)
    u = (E[ii] - sp) / (d[:, None] + 1e-9); cov = ((u * ns).sum(1) > 0.8) & (d < 40)
    return {g: d[cov & (gid[ii] == g)] for g in G}
rest = gaps(C["clips"][0]["frames"][0])
print("rest (raise-overhead frame 0, pose %s):" % C["clips"][0]["frames"][0]["p"][:3])
for g, d in rest.items(): print(f"  {g:4s} skin->metal gap  min {d.min():4.1f}  median {np.median(d):4.1f}  p90 {np.percentile(d, 90):4.1f}  share <= 10 mm {100 * (d <= 10).mean():3.0f}%")
alld = np.concatenate([rest[g] for g in ("l1", "l2", "l3")]); print(f"  links together: median {np.median(alld):.1f}, {100 * (alld <= 10).mean():.0f}% of the underside within 10 mm")
rows = []
for c in C["clips"]:
    meds = []
    for k in range(0, len(c["frames"]), 30):
        o = gaps(c["frames"][k]); meds.append(float(np.median(np.concatenate([o[g] for g in ("l1", "l2", "l3")]))))
    print(f"  {c['name']:24s} underside median over the clip {np.median(meds):4.1f} (range {min(meds):4.1f}-{max(meds):4.1f})", flush=True)
