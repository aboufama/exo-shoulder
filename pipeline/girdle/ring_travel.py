"""Least humeral-ring travel a 2R pointing shoulder can get away with. The ring (J3 = humerus axis) turns by the arm's axial
rotation relative to link 2; link 2's roll about the humerus axis is set by the 2R geometry (J1 direction, arcs a1, a2,
branch). Search those for the smallest J3 span over the clips, singular margin >= 20 deg (fit clips), and report the
intrinsic lower bound: the spread of axial rotation the clips use at nearly the same arm direction.
    python3 ring_travel.py -> ring_travel.json"""
import json, math, os, sys
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import girdle as GD
C = json.load(open(os.path.join(HERE, "..", "full-exo", "designs", "cad_r13_n4_s1343_1", "clips.json")))
names = [c["name"] for c in C["clips"] for f in c["frames"]]; W = np.array([f["want"] for c in C["clips"] for f in c["frames"]], float)
FIT = ~np.isin(names, ["Wave", "Walking arm swing"]); M = GD.Motion(W); MF = GD.Motion(W[FIT])
def span(x, br, MM):
    ch = GD.Chain3(dict(b=(x[0], x[1]), a1=float(np.clip(x[2], 20, 160)), a2=float(np.clip(x[3], 20, 160)), branch=br, w=None)); r = ch.kin(MM)
    if r is None: return 1e3, None
    A, mg, ok, *_ = r
    if not ok.all(): return 900, None
    tr = ch.joint_travel(MM); return tr["J3"]["span"] + 10 * max(0, 20 - mg.min()), tr
never = np.array([-0.525, -0.253, 0.812]); rng = np.random.default_rng(3); best = (1e9, None, None)
for s in range(16):
    v = never * (1 if s % 2 == 0 else -1) + (rng.normal(0, 0.3, 3) if s >= 4 else 0); x0 = GD.azel(v) + [90 + rng.normal(0, 15 if s >= 4 else 0), 90 + rng.normal(0, 15 if s >= 4 else 0)]
    br = [1, -1][(s // 2) % 2]
    r = minimize(lambda x: span(x, br, MF)[0], x0, method="Nelder-Mead", options=dict(maxiter=800, xatol=0.1, fatol=0.05))
    if r.fun < best[0]: best = (r.fun, r.x, br)
f, x, br = best; _, tr_fit = span(x, br, MF); _, tr_all = span(x, br, M)
# intrinsic: axial-rotation spread among frames whose humerus directions are within 10 deg of each other (after removing
# the swing-twist of the ISB YXY convention: twist about the humerus measured against a fixed reference vector)
h = M.hdir; ref = np.array([0.0, 0.0, 1.0])
def twist(Rh, hd):
    e = np.cross(hd, np.cross(ref, hd)); e /= np.linalg.norm(e) + 1e-12; v = Rh @ np.array([0.0, 0.0, 1.0]); v = v - (v @ hd) * hd; v /= np.linalg.norm(v) + 1e-12
    return math.degrees(math.atan2(np.cross(e, v) @ hd, e @ v))
tw = np.array([twist(Rh, hd) for Rh, hd in zip(M.RH, h)]); cosn = math.cos(math.radians(10)); spread = 0.0; where = None
for i in range(0, len(h), 3):
    nb = (h @ h[i]) > cosn; d = (tw[nb] - tw[i] + 180) % 360 - 180; sp = float(d.max() - d.min())
    if sp > spread: spread = sp; where = (names[i], [round(v) for v in W[i][:3]])
out = dict(best=dict(b=[round(float(v), 1) for v in x[:2]], a1=round(float(x[2]), 1), a2=round(float(x[3]), 1), branch=br,
                     ring_travel_fit=tr_fit["J3"], ring_travel_all=tr_all["J3"], J1=tr_all["J1"], J2=tr_all["J2"]),
           intrinsic_twist_spread_deg=round(spread, 1), intrinsic_where=where,
           note="intrinsic = largest spread of humeral twist among frames whose arm directions lie within 10 deg: no 2R pointing shoulder can make the ring travel less than this")
print(json.dumps(out, indent=1)); json.dump(out, open(os.path.join(HERE, "ring_travel.json"), "w"), indent=1)
