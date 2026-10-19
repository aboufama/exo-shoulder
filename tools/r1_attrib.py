"""R1 attribution (the full-CAD-vs-L1 rule: which part makes a full CAD lose R1 against its own L1): score_design.py's own covered-skin rule (nearest shoulder metal along the skin normal, cos >= 0.8, within 60 mm),
with the nearest metal sample's PART recorded: per part, covered skin samples in band 2-14 / under 2 / over 14, summed over every
STEP-th frame of every following clip frame. Same sampling seeds as score_design.py.
    python3 r1_attrib.py <design dir> [step=9] -> prints JSON"""
import json, os, sys
import numpy as np, trimesh
from scipy.spatial import cKDTree
FE = "/home/user/exo-shoulder/pipeline/full-exo"; sys.path.insert(0, os.path.join(FE, "..", "avg")); sys.path.insert(0, FE)
import body_pose as BP, metal_groups as MG
DD = sys.argv[1]; STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 9; LO, HI, REACH = 2.0, 14.0, 60.0
C = json.load(open(os.path.join(DD, "clips.json"))); sc = trimesh.load(os.path.join(DD, "exo.glb"))
SCORED, EXCL = MG.classify({n.split("|")[0] for n in sc.graph.nodes_geometry}, MG.clip_groups(C))
HRm = np.array(json.load(open(os.path.join(FE, "..", "avg", "body_mesh.json")))["landmarks"]["rest_humerus"]); _U, _, _Vt = np.linalg.svd(HRm); HRm = _U @ _Vt
MET = {}; NAMES = []
for node in sc.graph.nodes_geometry:
    T_, gname = sc.graph[node]; g = node.split("|")[0]
    if g not in SCORED: continue
    m = sc.geometry[gname].copy(); m.apply_transform(T_)
    n = int(np.clip(m.area / 1.5, 500, 60000)); p, _ = trimesh.sample.sample_surface(m, n, seed=3)
    if g == "H":
        p = p[np.linalg.norm(p @ HRm, axis=1) < 110.0]
        if not len(p): continue
    NAMES.append(f"{g}|{node.split('|')[1][:60]}"); MET.setdefault(g, []).append((p, len(NAMES) - 1))
LSEG = json.load(open(os.path.join(FE, "..", "avg", "body_mesh.json"))); L_, S_ = LSEG["landmarks"], LSEG["scale"]
F = BP.F; V0 = BP.V0
near = np.nonzero(np.linalg.norm(V0[F].mean(1), axis=1) < 180)[0]
A0 = 0.5 * np.linalg.norm(np.cross(V0[F[near, 1]] - V0[F[near, 0]], V0[F[near, 2]] - V0[F[near, 0]]), axis=1)
rng = np.random.default_rng(1); NS = int(A0.sum() / 0.25)
fi = near[rng.choice(len(near), NS, p=A0 / A0.sum())]; uv = rng.random((NS, 2)); flip = uv.sum(1) > 1; uv[flip] = 1 - uv[flip]
def skin(P):
    a, b, c = P[F[fi, 0]], P[F[fi, 1]], P[F[fi, 2]]
    pts = a + uv[:, :1] * (b - a) + uv[:, 1:] * (c - a); nr = np.cross(b - a, c - a); nr /= np.linalg.norm(nr, axis=1, keepdims=True) + 1e-12
    return pts, nr
cnt = np.zeros((len(NAMES), 3)); frames = 0; shares = []
for c in C["clips"]:
    for k in range(0, len(c["frames"]), STEP):
        fr = c["frames"][k]
        if fr["held"]: continue
        pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"])); X = BP.posed(pose); sp, ns = skin(X); T = fr.get("T", {})
        parts, lab = [], []
        for g, lst in MET.items():
            for p, j in lst:
                if g == "H":
                    sg, _ = BP.segs(L_, S_, pose); q = p @ sg[2][0].T + sg[2][1]
                else: q = p @ np.array(fr["G"][g]).reshape(3, 3).T + np.array(T.get(g, (0.0, 0.0, 0.0)), float)
                parts.append(q); lab.append(np.full(len(q), j))
        E = np.concatenate(parts); L = np.concatenate(lab)
        d, ii = cKDTree(E).query(sp, workers=2, distance_upper_bound=REACH)
        hit = np.isfinite(d); u = (E[ii[hit]] - sp[hit]) / d[hit, None]; cov = np.zeros(len(sp), bool); cov[np.nonzero(hit)[0][(u * ns[hit]).sum(1) > 0.8]] = True
        g_ = d[cov]; lb = L[ii[cov]]
        np.add.at(cnt[:, 0], lb[(g_ >= LO) & (g_ <= HI)], 1); np.add.at(cnt[:, 1], lb[g_ < LO], 1); np.add.at(cnt[:, 2], lb[g_ > HI], 1)
        frames += 1; shares.append(float(((g_ >= LO) & (g_ <= HI)).mean()) if len(g_) else 0.0)
tot = cnt.sum()
rows = sorted([dict(part=NAMES[j], in_band=int(cnt[j, 0]), under2=int(cnt[j, 1]), over14=int(cnt[j, 2])) for j in range(len(NAMES)) if cnt[j].sum() > 0],
              key=lambda r: -(r["under2"] + r["over14"]))
print(json.dumps(dict(design=os.path.basename(DD), step=STEP, frames=frames, mean_share=round(float(np.mean(shares)), 4), covered=int(tot),
                      in_band=int(cnt[:, 0].sum()), under2=int(cnt[:, 1].sum()), over14=int(cnt[:, 2].sum()), parts=rows), indent=1))
