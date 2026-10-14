"""Swept skin envelope of the upper arm in the arm's rest frame (group H) over every clip frame, for the upper-arm cuff.
Cylindrical grid about the humerus axis (GH -> elbow): theta (0 = toward BOTTOM's bar), s (mm from GH).
  R_arm[t, s] = max over frames of the humerus-driven skin radius (the cuff's inner surface must stay outside it)
  R_obs[t, s] = min over frames of trunk / forearm skin radius in that cell (the cuff's outer surface must stay inside it)
    python3 cuff_envelope.py [step]  -> out_cuff/envelope.npz
"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..", ".."); sys.path.insert(0, os.path.join(EXO, "avg")); sys.path.insert(0, os.path.join(EXO, "full-exo"))
import body_pose as BP
STEP = int(sys.argv[1]) if len(sys.argv) > 1 else 2
rig = BP._rig(); L = rig.L; sk = rig.skin
w = np.zeros((len(sk["rest"]), 5)); np.add.at(w, (np.repeat(np.arange(len(w)), 4), sk["wi"].ravel()), sk["ww"].ravel())
F = rig.F; wf = w[F].mean(1)                                                                          # face weights
trF = wf[:, 0] > 0.6; foF = wf[:, 3] + wf[:, 4] > 0.6; armF = ~(trF | foF)                          # trunk + forearm obstacles / the upper-arm skin
n_ = 7; bb = np.array([(i, j, n_ - i - j) for i in range(n_ + 1) for j in range(n_ + 1 - i)], float) / n_   # barycentric samples
a = np.array(L["elbow"], float); S_EL = float(np.linalg.norm(a)); a /= S_EL
os.chdir(os.path.join(EXO, "full-exo")); sys.path.insert(0, os.path.join(EXO, "conformal", "band_cad"))
import arm_end as AE
bar = AE.CB + 124.25 * AE.uB - 2.8 * AE.axB; e1 = bar - (bar @ a) * a; e1 /= np.linalg.norm(e1); e2 = np.cross(a, e1)
TH = np.arange(-180, 180, 2.0); SS = np.arange(100, 330, 2.0)
R_arm = np.full((len(TH), len(SS)), -np.inf); R_tr = np.full((len(TH), len(SS)), np.inf); R_fo = np.full((len(TH), len(SS)), np.inf); R_arm0 = np.full((len(TH), len(SS)), -np.inf)
C = json.load(open(os.path.join(EXO, "full-exo", "designs", os.environ.get("CUFF_DESIGN", "cad_r13_n4_s1343_1"), "clips.json")))
poses = [tuple(fr["p"]) for c in C["clips"] for fr in c["frames"][::STEP]]; poses = list(dict.fromkeys(poses)); print(len(poses), "poses", flush=True)
def raster(P, faces, out, red):
    """sample the faces (barycentric) -> cylindrical cells, reduce r into out with red (np.maximum / np.minimum)"""
    s_v = P @ a; r_v = np.hypot(P @ e1, P @ e2); keep = ((s_v > SS[0] - 10) & (s_v < SS[-1] + 10) & (r_v < 150))[faces].any(1); fa = faces[keep]
    X = np.einsum("kq,fqc->fkc", bb, P[fa]).reshape(-1, 3); s = X @ a; x = X @ e1; y = X @ e2; r = np.hypot(x, y); t = np.degrees(np.arctan2(y, x))
    it = np.clip(((t + 180) / 2.0).astype(int), 0, len(TH) - 1); js = np.floor((s - SS[0]) / 2.0).astype(int); ok = (js >= 0) & (js < len(SS)) & (r < 140)
    red.at(out, (it[ok], js[ok]), r[ok])
import trimesh
_src = trimesh.load(os.path.join(EXO, "full-exo", "designs", os.environ.get("CUFF_DESIGN", "cad_r13_n4_s1343_1"), "exo.glb")); _V, _F, _o = [], [], 0
for node in _src.graph.nodes_geometry:
    if node.split("|")[0] != "F": continue
    T_, gn = _src.graph[node]; m = _src.geometry[gn].copy(); m.apply_transform(T_); _V.append(m.vertices); _F.append(m.faces + _o); _o += len(m.vertices)
XF_v = np.concatenate(_V); XF_f = np.concatenate(_F); print("forearm exo parts", len(XF_f), "faces", flush=True)
t0 = time.time()
for k, p in enumerate(poses):
    pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], p)); V = BP.posed(pose)
    sg, _ = BP.segs(L, rig.s, pose); R = np.array(sg[2][0]); t = np.array(sg[2][1]); P = (V - t) @ R
    Af = np.full_like(R_arm, -np.inf); raster(P, F[armF], Af, np.maximum); R_arm[:] = np.maximum(R_arm, Af)
    if k == 0: R_arm0[:] = Af
    from scipy.ndimage import maximum_filter
    Ad = maximum_filter(np.where(np.isfinite(Af), Af, -1e9), size=(5, 3), mode="wrap")         # this frame's arm surface (holes closed)
    Of = np.full_like(R_tr, np.inf); raster(P, F[trF], Of, np.minimum); R_tr[:] = np.minimum(R_tr, np.where(Of > Ad + 1.0, Of, np.inf))   # trunk outside the arm
    Of = np.full_like(R_fo, np.inf); raster(P, F[foF], Of, np.minimum)                                                                   # forearm skin
    Rf = np.array(sg[3][0]); tf = np.array(sg[3][1]); Q = ((XF_v @ Rf.T + tf) - t) @ R                                                   # forearm exo parts in the H frame
    raster(Q, XF_f, Of, np.minimum); R_fo[:] = np.minimum(R_fo, Of)
    if k % 50 == 0: print(k, f"{time.time() - t0:.0f}s", flush=True)
np.savez(os.path.join(HERE, "out_cuff", "envelope.npz"), TH=TH, SS=SS, R_arm=R_arm, R_arm0=R_arm0, R_tr=R_tr, R_fo=R_fo, a=a, e1=e1, e2=e2, S_EL=S_EL, bar=bar, uB=AE.uB, vB=AE.vB, axB=AE.axB, CB=AE.CB)
print("done", f"{time.time() - t0:.0f}s")
