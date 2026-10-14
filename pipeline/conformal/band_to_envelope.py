"""4R band result (fixed J4 axis // elbow) -> envelope json for build_full_conformal.py (real G2 CAD, v3 joints).

The band evaluator's fitted undersides (member-local samples) become the per-link envelope (ribbons) and caps (hub
faces); rest pins are solved at pose 0 with the spare angle the clip paths use at rest; z_j4 = BOTTOM's hub face.

    python3 band_to_envelope.py <band_eval json> <index> <out envelope json>
"""
import base64, gzip, io, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(EXO, "avg"))
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180"); os.environ.setdefault("H_LEN", "325")
_c = os.getcwd(); os.chdir(os.path.join(EXO, "avg")); import design_search as DS; os.chdir(_c)
D2R = math.pi / 180; HW = 7.0
R = json.load(open(sys.argv[1]))["results"][int(sys.argv[2])]; OUT = sys.argv[3]
assert R["n"] == 4 and abs(R["w"][0] - 85.9) < 0.5 and abs(R["w"][1]) < 0.5, "fast path: 4R with the J4 axis // elbow only"
A = [x * D2R for x in R["a"]]
def unit(v): return v / np.linalg.norm(v)
def bvec(az, el): return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
def w_dir(d, a): d, a = d * D2R, a * D2R; return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])
B = bvec(R["az"], R["el"]); W = w_dir(*R["w"]); e_ = unit(np.cross(B, [0, 1.0, 0])); f_ = np.cross(B, e_)
def pins_at(HG, q):
    c2 = math.cos(A[0]) * B + math.sin(A[0]) * (math.cos(q) * e_ + math.sin(q) * f_); u4 = HG @ W
    d = np.clip(c2 @ u4, -1, 1); n = unit(np.cross(c2, u4)); den = 1 - d * d
    a = (math.cos(A[1]) - d * math.cos(A[2])) / den; b = (math.cos(A[2]) - d * math.cos(A[1])) / den; p = a * c2 + b * u4; h2 = 1 - p @ p
    return None if h2 <= 0 else dict(b=B, c2=c2, c3=p + R["branch"] * math.sqrt(h2) * n, u4=u4)
# rest spare angle: the path's angle on the frames closest to pose 0
Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(EXO, "conformal", "band_poses.b64")).read()))))
POSE = Z["POSE"][::int(R.get("stride", 1))]; cfg = np.array(R["cfg"]); fe = np.array(R["feasible"], bool); Q = np.array(R["Q"]).reshape(-1)
cand = [i for i in np.argsort(np.abs(POSE[:, 1])) if fe[i]][:20]
q_rest = float(np.median(Q[cfg[cand]])) if len(cand) else 0.0
P0 = pins_at(np.eye(3), q_rest)
assert P0 is not None, "no closure at pose 0"
h = np.array(R["h"]); sizes = R["sizes"]; kind = np.array(R["kind"]); off = np.r_[0, np.cumsum(sizes)]; R_REF = 65.0
env, caps, fps = [], [], []
for k in range(3):                                                   # links 1..3 = members 1..3
    dl = np.array(R["dirs_local"][k + 1]); hm = h[off[k + 1]:off[k + 2]]; kd = kind[off[k + 1]:off[k + 2]]; th = A[k]
    s_ = np.where(kd == 0, np.arctan2(dl[:, 1], dl[:, 0]) / th, np.where(kd == 1, 0.0, 1.0))
    lat = np.where(kd == 0, np.round(dl[:, 2] / np.linalg.norm(dl[:, :2], axis=1) * R_REF / 6.0) * HW, 0.0)   # +-6 mm samples -> the +-7 rows
    cosa = np.array(R["cosa"])[off[k + 1]:off[k + 2]]; mi = k + 1; lower = {int(J): v for J, v in R["lower"].items()}
    face = hm.copy()
    for kk, J in ((1, mi), (2, mi + 1)):                              # hubs: the joint's lower face (flat), as the old envelopes
        m_ = kd == kk
        if J < 4: face[m_] = hm[m_] * cosa[m_] - (0.0 if lower[J] == mi else 6.0)
    env.append(face.tolist()); caps.append(face.tolist())
    fps.append(dict(dirs=dl.tolist(), s=s_.tolist(), w=lat.tolist(), kind=kd.tolist()))
des = dict(az=R["az"], el=R["el"], a1=R["a"][0], a2=R["a"][1], a3=R["a"][2], branch=R["branch"], order=R["order"][:3], delta=R["w"][0], waz=R["w"][1])
json.dump(dict(design=des, rest_pins={k: v.tolist() for k, v in P0.items()}, env=env, caps=caps, fp=fps, z_j4=R["zj4"], q_rest=q_rest,
               source=dict(file=sys.argv[1], index=int(sys.argv[2]), score=R["score"])), open(OUT, "w"))
print(f"envelope -> {OUT}: q_rest {q_rest:.0f} deg, z_j4 {R['zj4']:.1f}, joint faces J1-J3 {[round(float(max(np.array(caps[k])[np.array(fps[k]['kind']) == 1])), 1) for k in range(3)]}")
