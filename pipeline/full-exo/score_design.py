"""Overall score of a built design over its clips (the number to beat).

Shoulder metal = every member group (base, l1..lN) + arm-mounted parts within 110 mm of the GH centre (BOTTOM's hub).
Per frame: the skin the mechanism covers = skin points (fixed barycentric samples on the body rig's render skin,
re-posed every frame with avg/body_pose.py) whose nearest shoulder metal lies straight out along the skin normal
(cos >= 0.8) within 60 mm. in-band share = fraction of that covered skin whose gap to the metal is 2..10 mm.
Frame score = in-band share if the exo follows the arm, 0 if it is held at its limit.
OVERALL = mean frame score over every frame of every clip (clips weighted by length).

    python3 score_design.py <design dir> [frame step=3]   -> <design dir>/score.json
"""
import json, os, sys
import numpy as np, trimesh
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "avg")); import body_pose as BP
DD = sys.argv[1]; STEP = int(sys.argv[2]) if len(sys.argv) > 2 else 3
LO, HI, REACH = 2.0, float(os.environ.get("BAND_HI", 10.0)), 60.0                 # BAND_HI=11: the 'tiny bit more' band
C = json.load(open(os.path.join(DD, "clips.json"))); sc = trimesh.load(os.path.join(DD, "exo.glb"))
# metal: uniform surface samples of every shoulder part (links, base, joint hardware) in their group frames
MET = {}
ARM_NEAR = 110.0                                     # arm-mounted metal within this of the GH centre (BOTTOM's hub / block) is shoulder metal too
HRm = np.array(json.load(open(os.path.join(HERE, "..", "avg", "body_mesh.json")))["landmarks"]["rest_humerus"]); _U, _, _Vt = np.linalg.svd(HRm); HRm = _U @ _Vt
for node in sc.graph.nodes_geometry:
    T_, gname = sc.graph[node]; g = node.split("|")[0]
    if not (g == "base" or (g[0] == "l" and g[1:].isdigit()) or g in ("H", "cuff")): continue
    m = sc.geometry[gname].copy(); m.apply_transform(T_)
    n = int(np.clip(m.area / 1.5, 500, 60000)); p, _ = trimesh.sample.sample_surface(m, n, seed=3)
    if g == "H":
        p = p[np.linalg.norm(p @ HRm, axis=1) < ARM_NEAR]                     # rest -> canonical: GH-centred radius
        if not len(p): continue
    MET.setdefault(g, []).append(p)
MET = {g: np.concatenate(v) for g, v in MET.items()}
LSEG = json.load(open(os.path.join(HERE, "..", "avg", "body_mesh.json"))); L_, S_ = LSEG["landmarks"], LSEG["scale"]
# skin: fixed barycentric samples on faces near the shoulder (chosen at rest, ~0.5 mm spacing)
F = BP.F; V0 = BP.V0
near = np.nonzero(np.linalg.norm(V0[F].mean(1), axis=1) < 180)[0]
A0 = 0.5 * np.linalg.norm(np.cross(V0[F[near, 1]] - V0[F[near, 0]], V0[F[near, 2]] - V0[F[near, 0]]), axis=1)
rng = np.random.default_rng(1); NS = int(A0.sum() / 0.25)
fi = near[rng.choice(len(near), NS, p=A0 / A0.sum())]; uv = rng.random((NS, 2)); flip = uv.sum(1) > 1; uv[flip] = 1 - uv[flip]
def skin(P):
    a, b, c = P[F[fi, 0]], P[F[fi, 1]], P[F[fi, 2]]
    pts = a + uv[:, :1] * (b - a) + uv[:, 1:] * (c - a); nr = np.cross(b - a, c - a); nr /= np.linalg.norm(nr, axis=1, keepdims=True) + 1e-12
    return pts, nr
def frame_metrics(fr):
    X = BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"]))); sp, ns = skin(X)
    pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], fr["p"]))
    T = fr.get("T", {})                                                                       # optional per-group translation (offset-axis chains)
    parts = [MET[g] @ np.array(fr["G"][g]).reshape(3, 3).T + np.array(T.get(g, (0.0, 0.0, 0.0)), float) for g in MET if g != "H" and g in fr["G"]]
    if "H" in MET:
        sg, _ = BP.segs(L_, S_, pose); parts.append(MET["H"] @ sg[2][0].T + sg[2][1])                 # rides on the humerus
    E = np.concatenate(parts)
    d, ii = cKDTree(E).query(sp, workers=4, distance_upper_bound=REACH)
    hit = np.isfinite(d); u = (E[ii[hit]] - sp[hit]) / d[hit, None]; cov = np.zeros(len(sp), bool); cov[np.nonzero(hit)[0][(u * ns[hit]).sum(1) > 0.8]] = True
    g = d[cov]
    if not len(g): return 0.0, np.nan, np.nan
    return float(((g >= LO) & (g <= HI)).mean()), float(np.median(g)), float(g.min())
rows = []; tot = 0.0; n_all = 0
for c in C["clips"]:
    fs = c["frames"]; idx = list(range(0, len(fs), STEP)); sc_, med, mn, fol = [], [], [], []
    for k in idx:
        share, md, mi = frame_metrics(fs[k]); f_ = not fs[k]["held"]
        sc_.append(share if f_ else 0.0); med.append(md); mn.append(mi); fol.append(f_)
    if os.environ.get("WRITE_BACK") == "1":                                              # per-frame closest / median gap into the viewer data
        for k_, f_ in enumerate(fs):
            j_ = min(range(len(idx)), key=lambda q_: abs(idx[q_] - k_))
            f_["clr"] = None if np.isnan(mn[j_]) else round(float(mn[j_]), 1); f_["med"] = None if np.isnan(med[j_]) else round(float(med[j_]), 1)
    s = float(np.mean(sc_)); rows.append(dict(name=c["name"], frames=len(fs), score=s, follow=float(np.mean(fol)),
                                         in_band_when_following=float(np.mean([x for x, f_ in zip(sc_, fol) if f_])) if any(fol) else 0.0,
                                         median_gap=float(np.nanmedian(med)), min_gap=float(np.nanmin(mn))))
    tot += s * len(fs); n_all += len(fs)
    r = rows[-1]; print(f"{r['name']:24s} score {100 * r['score']:5.1f}%  = follows {100 * r['follow']:5.1f}% x in-band {100 * r['in_band_when_following']:5.1f}%   median gap {r['median_gap']:5.1f}  min {r['min_gap']:4.1f} mm", flush=True)
overall = tot / n_all
fol_all = sum(r["follow"] * r["frames"] for r in rows) / n_all
band_all = sum(r["in_band_when_following"] * r["follow"] * r["frames"] for r in rows) / max(1e-9, sum(r["follow"] * r["frames"] for r in rows))
print(f"OVERALL {100 * overall:.1f}%   (follows {100 * fol_all:.1f}% of frames; while following, {100 * band_all:.1f}% of the covered skin is {LO:g}-{HI:g} mm from the metal)")
json.dump(dict(overall=overall, follow=fol_all, in_band=band_all, clips=rows, band=[LO, HI], step=STEP), open(os.path.join(DD, "score.json" if HI == 10.0 else f"score_{HI:g}mm.json"), "w"), indent=1)
if os.environ.get("WRITE_BACK") == "1": json.dump(C, open(os.path.join(DD, "clips.json"), "w"), separators=(",", ":"))
