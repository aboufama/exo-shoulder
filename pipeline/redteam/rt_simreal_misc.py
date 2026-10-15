"""SIM-TO-REAL 4 - two checks on the human model the judges use.
(a) Clip speed profile: humerus angular speed of the 8 design clips (30 fps clips of a design dir). Keyframes are joined at
    constant speed (p95 = max), so a real minimum-jerk reach of the same duration peaks ~1.9x higher.
(b) Load-dependent muscle bulge: the rig's posed skin with all muscles relaxed (activation 0.06) vs shoulder + elbow
    flexors fully active (1.0), same pose: how far does activation move the skin near the shoulder?
    python3 rt_simreal_misc.py [design id]   -> results/simreal_misc.json"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
from rt_common import GD, BP                                            # noqa: E402
des = sys.argv[1] if len(sys.argv) > 1 else "l1_r14_3r_s1351_1"
C = json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", des, "clips.json")))
out = dict(design=des, clips={}, bulge=[])
for c in C["clips"]:
    R = [GD.Rh_of(*f["want"][:3]) for f in c["frames"]]; fps = c.get("fps") or 30
    w = np.array([math.degrees(math.acos(np.clip((np.trace(R[i] @ R[i - 1].T) - 1) / 2, -1, 1))) * fps for i in range(1, len(R))])
    out["clips"][c["name"]] = dict(seconds=round(len(R) / fps, 1), humerus_speed_max_deg_s=round(float(w.max()), 1), p95=round(float(np.percentile(w, 95)), 1), median_moving=round(float(np.median(w[w > 5])), 1))
    print(f"{c['name']:24s} {len(R) / fps:4.1f} s  humerus speed max {w.max():6.1f} deg/s  p95 {np.percentile(w, 95):6.1f}")
for pose in (dict(plane=30, elev=10, axial=-30, flex=15, pron=0), dict(plane=30, elev=90, axial=-45, flex=15, pron=0), dict(plane=60, elev=140, axial=-60, flex=90, pron=0)):
    A = BP.posed(pose, act=dict(shoulder=0.06, flexor=0.06, extensor=0.06)); B = BP.posed(pose, act=dict(shoulder=1.0, flexor=1.0, extensor=0.06))
    r = np.linalg.norm(A, axis=1); dd = np.linalg.norm(B - A, axis=1); dr = np.linalg.norm(B, axis=1) - r
    row = dict(pose=pose, **{f"within_{L}mm": dict(max_disp=round(float(dd[r < L].max()), 2), max_rise_from_GH=round(float(dr[r < L].max()), 2)) for L in (120, 200)})
    out["bulge"].append(row); print(pose, row["within_120mm"], row["within_200mm"])
json.dump(out, open(os.path.join(HERE, "results", "simreal_misc.json"), "w"), indent=1)
