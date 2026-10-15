"""SIM-TO-REAL 3 - can per-joint mechanical end stops keep a powered 3R inside the human range of motion?
Joint angles of each 3R design along the 8 clips (from the evaluator's own axes, band_impl chain via transmission.axes):
q1 about the base axis b, q2 about J2, q3 about the arm-fixed J3, relative to the first valid frame. Their per-joint
range is the TIGHTEST set of hard stops that still lets every clip frame through. A 26^3 grid over that box is mapped
forward (spherical serial chain: R = Rot(b,q1) Rot(p2_ref,q2) Rot(p3_ref,q3) R_ref) and each reachable humerus
orientation is compared with the red team's plausible everyday workspace (rt_jam.py: plane -90..150, elevation 0..170,
humeral rotation +-90 about the twist-free neutral, rough active-ROM cap; 5 deg grid; scapula frame): rotation distance
to the nearest plausible pose. The box is generous to the design (the plausible set allows +-90 deg rotation everywhere).
    python3 rt_jointbox.py   -> results/jointbox.json"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "pipeline", "conformal", "analysis")); sys.path.insert(0, HERE)
import rt_common as RC                                                  # noqa: E402
from rt_common import GD, BP                                            # noqa: E402
os.chdir(os.path.join(REPO, "pipeline", "conformal"))
import transmission as TR                                               # noqa: E402
from scipy.spatial.transform import Rotation as Rot                     # noqa: E402
P = TR.poses(); HG = P["HG"]

def rotm(ax, a): return Rot.from_rotvec(np.asarray(ax, float) / np.linalg.norm(ax) * a).as_matrix()
def sang(a, b, ax):
    a = a - (a @ ax) * ax; b = b - (b @ ax) * ax; return math.atan2(np.cross(a, b) @ ax, a @ b)

pl_g = np.arange(-90, 151, 5.0); el_g = np.arange(0, 171, 5.0); r_g = np.arange(-90, 91, 5.0)
PL, EL, RR = np.meshgrid(pl_g, el_g, r_g, indexing="ij"); PL, EL, RR = PL.ravel(), EL.ravel(), RR.ravel(); AX = RR - PL
m = RC.plausible(PL, EL); Hp = np.array([BP.scap(e).T @ GD.Rh_of(p, e, a) for p, e, a in zip(PL[m], EL[m], AX[m])])
Qp = Rot.from_matrix(Hp).as_quat()
D = json.load(open(os.path.join(REPO, "pipeline", "conformal", "analysis", "designs_transmission.json"))); out = []
for d in D:
    if d["n"] != 3: continue
    U, ok = TR.axes(P, d); f0 = int(np.nonzero(ok)[0][0]); b, p2r, p3r, Rr = U[f0, 0], U[f0, 1], U[f0, 2], HG[f0]
    Q = []
    for f in np.nonzero(ok)[0]:
        q1 = sang(p2r, U[f, 1], b); R1 = rotm(b, q1); q2 = sang(R1 @ p3r, U[f, 2], U[f, 1]); R2 = rotm(p2r, q2)
        R3 = (R1 @ R2).T @ HG[f] @ Rr.T; v = np.array([R3[2, 1] - R3[1, 2], R3[0, 2] - R3[2, 0], R3[1, 0] - R3[0, 1]]) / 2
        q3 = math.atan2(v @ p3r, (np.trace(R3) - 1) / 2)
        assert np.allclose(R1 @ R2 @ rotm(p3r, q3) @ Rr, HG[f], atol=2e-3), "forward kinematics does not reproduce the clip frame"
        Q.append([q1, q2, q3])
    Qd = np.degrees(np.array(Q)); med = np.median(Qd, 0); Qd = (Qd - med + 180) % 360 - 180 + med; lo, hi = Qd.min(0), Qd.max(0)
    G3 = np.stack(np.meshgrid(*[np.linspace(lo[i], hi[i], 26) for i in range(3)], indexing="ij"), -1).reshape(-1, 3)
    Rb = np.array([rotm(b, math.radians(x)) @ rotm(p2r, math.radians(y)) @ rotm(p3r, math.radians(z)) @ Rr for x, y, z in G3])
    Qb = Rot.from_matrix(Rb).as_quat(); dist = np.empty(len(Qb))
    for i in range(0, len(Qb), 2000): dist[i:i + 2000] = np.degrees(2 * np.arccos(np.clip(np.abs(Qb[i:i + 2000] @ Qp.T).max(1), -1, 1)))
    row = dict(src=d["_src"], joint_stop_box_deg=[[round(float(a), 1), round(float(c), 1)] for a, c in zip(lo, hi)], spans_deg=[round(float(c - a), 1) for a, c in zip(lo, hi)],
               share_of_box_beyond_plausible={str(t): round(float((dist > t).mean()), 3) for t in (10, 20, 30, 45)}, worst_beyond_deg=round(float(dist.max()), 1))
    out.append(row)
    print(f"{row['src'][:44]:44s} stops {row['spans_deg']} deg: {100 * row['share_of_box_beyond_plausible']['20']:.1f}% of the box > 20 deg beyond the plausible ROM, worst {row['worst_beyond_deg']} deg")
json.dump(out, open(os.path.join(HERE, "results", "jointbox.json"), "w"), indent=1)
