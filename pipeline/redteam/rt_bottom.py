"""Is the elbow-region penetration of BOTTOM + neck + JN hub ours (the neck / hub we added) or the user's original BOTTOM
end, and is it a rig artifact? Depth of BOTTOM's vertices inside the posed body, split by distance s from GH along the
humerus (neck + hub: s < 250 mm; the user's original elbow end: s >= 250), and the user's own elbow / forearm parts at the
rest pose (arm hanging, elbow 12 deg) - parts built for the user's real arm.
    python3 rt_bottom.py -> results/bottom.json
"""
import json
import numpy as np
from scipy.spatial import cKDTree
import rt_common as RC
from rt_common import BP, GD
from common import load_parts
from sdist import signed_distance
import scene_export as SE

HR = np.array(json.load(open(RC.REPO + "/pipeline/avg/body_mesh.json"))["landmarks"]["rest_humerus"])
REG = RC.skin_regions()["region"]; FR = RC.clips(); parts = load_parts(RC.DD)
pick = {"rest (Raise overhead f0)": ("Raise overhead", 0), "Comb hair f67 (flex 120)": ("Comb hair", 67), "Drink f125 (flex 124)": ("Drink from a cup", 125),
        "Wash opposite shoulder f68": ("Wash opposite shoulder", 68), "Walking f0": ("Walking arm swing", 0), "Reach a high shelf f75": ("Reach a high shelf", 75)}
out = {}
for lab, (cn, fi) in pick.items():
    f = next(x for x in FR if x[0] == cn and x[1] == fi); X, pose = SE.frame_xforms(dict(p=f[3], G=f[5])); V = BP.posed(pose); ct = cKDTree(V[BP.F].mean(1)); vt = cKDTree(V)
    o = {}
    for g, n, P0, _ in parts:
        if not (n.startswith(("BOTTOM", "FOREARM CUFF", "MIDDLE", "TOP", "UPPER ARM CUFF")) or "IGUS" in n): continue
        R, t = X[g]; P = P0[:: max(1, len(P0) // 20000)] @ np.asarray(R).T + t; sd = signed_distance(P, V, BP.F, tree=ct)
        if g == "H":
            s = -(P0[:: max(1, len(P0) // 20000)] @ HR)[:, 1]
            for nm, m in (("s<250 (neck+hub, ours)", s < 250), ("s>=250 (user's original elbow end)", s >= 250)):
                if m.any():
                    k = np.flatnonzero(m)[np.argmin(sd[m])]; _, vj = vt.query(P[k])
                    o[f"{n[:24]} {nm}"] = dict(depth_mm=round(float(max(0, -sd[m].min())), 2), min_sd=round(float(sd[m].min()), 2), region=REG[vj], s=round(float(s[k])))
        else:
            k = int(np.argmin(sd)); _, vj = vt.query(P[k]); o[n[:24]] = dict(depth_mm=round(float(max(0, -sd.min())), 2), min_sd=round(float(sd.min()), 2), region=REG[vj])
    out[lab] = dict(pose=[round(v) for v in f[3]], parts=o); print(lab, out[lab]["pose"]); [print("   ", k, v) for k, v in o.items()]
RC.jdump(out, "bottom.json")
