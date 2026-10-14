"""where may the cuff's outer surface go? per (theta, s) cell: min over every clip frame of the signed distance from the
candidate outer surface (fair inner + shell, cuff_fair.py) to the posed body (closed mesh, exact). -> out_cuff/trunkmap.npz"""
import json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..", ".."); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(EXO, "avg")); sys.path.insert(0, os.path.join(EXO, "full-exo"))
os.environ.setdefault("CUFF_FAST", "1")
_src = open(os.path.join(HERE, "cuff_fair.py")).read().split("# ---------------------------------------------------------------- the shell (cylindrical-chart version of sheet_solid)")[0]
__file__ = os.path.join(HERE, "cuff_fair.py"); sys.argv = ["x"]; exec(_src)
import body_pose as BP, scene_export as SE
from sdist import signed_distance
STEP = int(os.environ.get("STEP", 2))
tg = np.arange(-84.0, 124.1, 2.0); sg = np.arange(146.0, 254.1, 2.0); TG, SG = np.meshgrid(tg, sg, indexing="ij")
XG = R0 * np.radians(TG); RO = r_out(XG, SG); P0 = cyl(XG, SG, RO).reshape(-1, 3)
C = json.load(open(os.path.join(EXO, "full-exo", "designs", "cad_r13_n4_s1343_1", "clips.json")))
poses = list(dict.fromkeys(tuple(fr["p"]) for c in C["clips"] for fr in c["frames"][::STEP])); print(len(poses), "poses", flush=True)
L = BP._rig().L; S_ = BP._rig().s; dmin = np.full(len(P0), np.inf); t0 = time.time()
for k, p in enumerate(poses):
    pose = dict(zip(["plane", "elev", "axial", "flex", "pron"], p)); V = BP.posed(pose); sg_, _ = BP.segs(L, S_, pose)
    R = np.array(sg_[2][0]); t = np.array(sg_[2][1]); P = P0 @ R.T + t
    dmin = np.minimum(dmin, signed_distance(P, V, BP.F))
    if k % 40 == 0: print(k, f"{time.time() - t0:.0f}s", flush=True)
np.savez(os.path.join(HERE, "out_cuff", "trunkmap.npz"), tg=tg, sg=sg, dmin=dmin.reshape(TG.shape))
print("done", f"{time.time() - t0:.0f}s")
