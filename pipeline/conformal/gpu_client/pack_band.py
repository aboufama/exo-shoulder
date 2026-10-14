"""Pose payload for the GPU band evaluator: every frame of the natural clips (full-exo/clip_keys.json) at FPS.

Per frame: HG (humerus rotation in the canonical scapula frame, = Rs^T H), RS (scapula in the thorax), EL (elevation,
for the map bins), clip id, frame index, weight (overhead-type clips weighted up: the user's main struggle).

    python3 pack_band.py [fps=10]      -> ../band_poses.b64
"""
import base64, gzip, io, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(EXO, "avg"))
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180"); os.environ.setdefault("H_LEN", "325")
_c = os.getcwd(); os.chdir(os.path.join(EXO, "avg")); import design_search as D; os.chdir(_c)
FPS = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
WEIGHT = {"Raise overhead": 2.0, "Reach a high shelf": 1.5, "Comb hair": 1.5}
def minjerk(t): return 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5
def frames_of(keys):
    out = []
    for (k0, dt), (k1, _) in zip(keys[:-1], keys[1:]):
        n = max(2, int(round(dt * FPS)))
        for i in range(n): s = minjerk(i / n); out.append(tuple(a + (b_ - a) * s for a, b_ in zip(k0, k1)))
    out.append(tuple(keys[-1][0])); return out
CL = json.load(open(os.path.join(EXO, "full-exo", "clip_keys.json")))
HG, RS, EL, CID, FI, WT, PO = [], [], [], [], [], [], []
for ci, (name, keys) in enumerate(CL):
    for k, (pl, el, ax, fx, pr) in enumerate(frames_of([(tuple(p), d) for p, d in keys])):
        H = D.Ry(pl * D.D2R) @ D.Rx(-el * D.D2R) @ D.Ry(ax * D.D2R); Rs = D.scapula(el)
        HG.append(Rs.T @ H); RS.append(Rs); EL.append(el); CID.append(ci); FI.append(k); WT.append(WEIGHT.get(name, 1.0)); PO.append((pl, el, ax, fx, pr))
Z = dict(HG=np.array(HG, np.float32), RS=np.array(RS, np.float32), EL=np.array(EL, np.float32), CID=np.array(CID, np.int32),
         FI=np.array(FI, np.int32), WT=np.array(WT, np.float32), POSE=np.array(PO, np.float32), NAMES=np.array([n for n, _ in CL]), FPS=np.array(FPS))
buf = io.BytesIO(); np.savez_compressed(buf, **Z)
open(os.path.join(HERE, "..", "band_poses.b64"), "w").write(base64.b64encode(gzip.compress(buf.getvalue())).decode())
print(f"{len(HG)} frames from {len(CL)} clips at {FPS} fps; payload {len(buf.getvalue()) / 1e3:.0f} kB")
