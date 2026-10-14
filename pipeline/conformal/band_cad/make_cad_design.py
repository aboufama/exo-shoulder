"""CAD build -> viewer design dir: exo.glb from out_<key>/, clips copied from the band design with the base held
scapula-fixed (one fixed frame per design: its tab points away from link 1's mean direction), index.json entry.

    python3 make_cad_design.py <key> <source band design dir name> "<label>"
"""
import json, math, os, shutil, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..", ".."); FX = os.path.join(EXO, "full-exo")
sys.path.insert(0, os.path.join(EXO, "avg"))
KEY, SRC, LABEL = sys.argv[1], sys.argv[2], sys.argv[3]; NAME = f"cad_{KEY}"; sys.argv = sys.argv[:1]
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180"); os.environ.setdefault("H_LEN", "325")
_c = os.getcwd(); os.chdir(os.path.join(EXO, "avg")); import design_search as DS; os.chdir(_c)
DD = os.path.join(FX, "designs", NAME); os.makedirs(DD, exist_ok=True)
_g = os.path.join(HERE, f"out_{KEY}", "exo.glb")
if os.path.exists(_g): shutil.copy(_g, os.path.join(DD, "exo.glb"))     # old pipeline build (the fair pipeline writes its own)
C = json.load(open(os.path.join(FX, "designs", SRC, "clips.json")))
loc = []                                                                            # base frame in the scapula frame, per frame
for cl in C["clips"]:
    for f in cl["frames"]:
        Rs = DS.scapula(f["p"][1]); loc.append(Rs.T @ np.array(f["G"]["base"]).reshape(3, 3))
loc = np.array(loc); a = loc[0][:, 0]; print("J1 axis spread", float(np.abs(loc[:, :, 0] - a).max()))
MOUNT = {"5r_thin": [0.0, 1.0, -1.0], "4r_thin": [-1.0, 0.0, -1.0]}.get(KEY, [0.0, 0.6, -0.8])   # base tab toward the back plate (thorax: anterior, up, right)
nb0 = loc[:, :, 1].mean(0); nb0 = nb0 - (nb0 @ a) * a; nb0 /= np.linalg.norm(nb0)
d = np.array(MOUNT, float); d -= (d @ a) * a; d /= np.linalg.norm(d); nb = -d; Fb = np.c_[a, nb, np.cross(a, nb)]   # tab = local -y = d
e2 = np.cross(a, nb0); t = math.degrees(math.atan2(d @ e2, d @ nb0)); a1 = np.degrees(np.arctan2(loc[:, :, 1] @ e2, loc[:, :, 1] @ nb0))
print(f"base tab toward {MOUNT}: link 1 within +-16 deg of it in {100 * np.mean(np.abs((a1 - t + 180) % 360 - 180) < 16):.1f}% of frames")
ang = np.degrees(np.arctan2(loc[:, :, 1] @ np.cross(a, nb), loc[:, :, 1] @ nb)); print(f"link 1 swing about J1 vs the fixed base frame: {ang.min():.0f} .. {ang.max():.0f} deg")
for cl in C["clips"]:
    for f in cl["frames"]:
        Rs = DS.scapula(f["p"][1]); f["G"]["base"] = (Rs @ Fb).round(6).ravel().tolist(); f["clr"] = 0.0; f["med"] = None
C["subtitle"] = LABEL
json.dump(C, open(os.path.join(DD, "clips.json"), "w"), separators=(",", ":"))
idx = json.load(open(os.path.join(FX, "designs", "index.json"))); idx = [e for e in idx if e["id"] != NAME]
idx.insert(0, dict(id=NAME, label=LABEL)); json.dump(idx, open(os.path.join(FX, "designs", "index.json"), "w"), indent=1)
print("wrote", DD)
