"""docs/research/stop_engage/l1_control.py <l1 design id> (nice -n 10; ~1 min) - control: the L1 keep-out stop slots (build_minarc_l1.slotted_plate, radial ends) measured with tools/stop_engage.Pair.
Axis (no bearings at L1): the slotted O20 plate keep-out's smallest-variance PCA direction through the least-squares circle
of its outer rim vertices (the K boss / spring-cap keep-out is not axisymmetric: its centroid sat 0.6-1 mm off the axis)."""
import json, math, sys
sys.path.insert(0, "/home/user/exo-shoulder/tools")
import stop_engage as SE
import numpy as np
def plate_axis(m):
    V = np.asarray(m.vertices); c0 = V.mean(0); _, U = np.linalg.eigh((V - c0).T @ (V - c0)); k = U[:, 0]; e = U[:, 2]; f = np.cross(k, e)
    x, y = (V - c0) @ e, (V - c0) @ f; r = np.hypot(x, y); rim = r > 0.97 * r.max()
    A = np.c_[2 * x[rim], 2 * y[rim], np.ones(rim.sum())]; (a, b, cc), *_ = np.linalg.lstsq(A, x[rim] ** 2 + y[rim] ** 2, rcond=None)
    R = float(np.sqrt(cc + a * a + b * b)); return c0 + a * e + b * f, k, dict(rim_R_mm=round(R, 4), rim_pts=int(rim.sum()))
did = sys.argv[1]; dd = f"/home/user/exo-shoulder/pipeline/full-exo/designs/{did}"
st = json.load(open(dd + "/build.json"))["stack"]["stops"]; m = SE.scene_meshes(dd + "/exo.glb")
win = {"K": sorted([st["K"]["stop_A_deg"], st["K"]["stop_B_deg"]]), "J2": sorted(st["J2"]["window_deg"])}
pat = {"K": dict(boss=r"\|K upper boss", dowel=r"\|K stop dowel", part=r"\|K lower plate keep-out"),
       "J2": dict(boss=r"\|J2 upper boss", dowel=r"\|J2 stop dowel", part=r"\|J2 lower plate keep-out")}
out = {}
for j, p in pat.items():
    part = SE.pick(m, p["part"]); c, k, ax = plate_axis(part[0][1]); q_lo, q_hi = win[j]
    for dn, dm in sorted(SE.pick(m, p["dowel"])):
        pr = SE.Pair(dm, part[0][1], c, k); a_max = max(abs(q_lo), abs(q_hi)) + 5
        fp, fm = pr.first_contact(+1, a_max), pr.first_contact(-1, a_max)
        r = {s: ((fp if s > 0 else fm)["angle_deg"] - q_hi, (fm if s > 0 else fp)["angle_deg"] + q_lo) for s in (1, -1)}
        s = min(r, key=lambda s: abs(r[s][0]) + abs(r[s][1]))
        out[f"{j} {dn.split('|')[1][:20]}"] = dict(rs=round(pr.rs, 4), past_hi_deg=round(r[s][0], 4), past_lo_deg=round(r[s][1], 4),
                                                   kinds=[(fp or {}).get("kind"), (fm or {}).get("kind")], axis=ax)
        print(did, j, dn.split("|")[1][:24], out[f"{j} {dn.split('|')[1][:20]}"], flush=True)
json.dump(out, open(f"/home/user/exo-shoulder/docs/research/stop_engage/{did}.json", "w"), indent=1)
