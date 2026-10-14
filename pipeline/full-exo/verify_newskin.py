"""Clearance of the shoulder exo vs the current body rig (avg/body_pose.py) over every clip frame in <design>/clips.json.
Signed distance (outside +) from exo surface points to the posed render skin; prints per clip min / p5 and the rest gaps."""
import json, os, sys
import numpy as np, trimesh
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "avg"))
import body_pose as BP
DD = sys.argv[1]; STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 3
C = json.load(open(os.path.join(DD, "clips.json"))); sc = trimesh.load(os.path.join(DD, "exo.glb"))
pts = {}
for node in sc.graph.nodes_geometry:
    T_, gname = sc.graph[node]; g = node.split("|")[0]
    if g not in ("base", "l1", "l2", "l3"): continue
    m = sc.geometry[gname]; P = trimesh.transform_points(m.vertices, T_); pts.setdefault(g, []).append(P[:: max(1, len(P) // 1500)])
pts = {g: np.concatenate(v) for g, v in pts.items()}
F = BP.F
def signed(Q, X):
    m = trimesh.Trimesh(X, F, process=False); keep = np.linalg.norm(m.triangles_center, axis=1) < 300
    sub = m.submesh([np.flatnonzero(keep)], append=True); sp, fi = trimesh.sample.sample_surface(sub, 300000, seed=2)
    d, ii = cKDTree(sp).query(Q, workers=4); s = np.sign(((Q - sp[ii]) * sub.face_normals[fi][ii]).sum(1))
    neg = np.nonzero(s < 0)[0]
    if len(neg):                                          # nearest-normal sign is unreliable near the axilla pocket: winding number
        T = X[F]; inside = np.zeros(len(neg), bool)
        for lo in range(0, len(neg), 64):
            q = Q[neg[lo:lo + 64]]; A_ = T[None, :, 0] - q[:, None]; B_ = T[None, :, 1] - q[:, None]; C_ = T[None, :, 2] - q[:, None]
            la, lb, lc = (np.linalg.norm(v, axis=-1) for v in (A_, B_, C_))
            num = np.einsum("pfi,pfi->pf", A_, np.cross(B_, C_)); den = la * lb * lc + (A_ * B_).sum(-1) * lc + (B_ * C_).sum(-1) * la + (C_ * A_).sum(-1) * lb
            inside[lo:lo + 64] = np.abs(np.arctan2(num, den).sum(1) / (2 * np.pi)) > 0.5
        s[neg[~inside]] = 1.0
    return d * s
out = []
for c in C["clips"]:
    mins = []
    for k in range(0, len(c["frames"]), STEP):
        fr = c["frames"][k]; pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"]))
        X = BP.posed(pose); Q = []; gid = []
        for g in ("base", "l1", "l2", "l3"):
            R = np.array(fr["G"][g]).reshape(3, 3); Q.append(pts[g] @ R.T); gid += [g] * len(pts[g])
        Q = np.concatenate(Q); gid = np.array(gid); d = signed(Q, X)
        mins.append({g: float(d[gid == g].min()) for g in ("base", "l1", "l2", "l3")} | {"held": fr["held"], "k": k})
    lm = np.array([min(m_[g] for g in ("l1", "l2", "l3")) for m_ in mins]); bm = np.array([m_["base"] for m_ in mins])
    print(f"{c['name']:24s} links min {lm.min():5.1f} p5 {np.percentile(lm, 5):5.1f} | base min {bm.min():5.1f} | frames<1mm {int((lm < 1).sum())}/{len(lm)}", flush=True)
    out.append(dict(name=c["name"], mins=mins))
json.dump(out, open(os.path.join(DD, "newskin_clearance.json"), "w"))
