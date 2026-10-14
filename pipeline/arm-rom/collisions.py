"""Collision limits of the shoulder mechanism (exo parts may touch only where they are pinned together).

Each link carries the hardware that rides with it (sleeves, clamps, screws, washers: assigned to the nearest link in
the CAD pose). Bodies are sampled as dense surface point clouds; two bodies collide when their clouds come within
TOUCH mm, except inside the designed pin stack of a pin they share. Results (rom_limits.json):
  sigma_free   collision-free scissor opening interval containing the CAD pose (psi does not change the shape)
  gamma_free   for each sigma on a grid, the collision-free interval of BOTTOM's rotation about the output pin
  meshes       decimated triangle meshes of every body (CAD frame, mm) for the viewer, plus each pin's centre
"""
import json
import math
import os
import sys

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "joint-verification"))
STEP = os.path.join(HERE, "source", "right_arm.step")
sys.argv = sys.argv[:1] + [STEP]
from features import read                                         # noqa: E402
import kinematics as K                                            # noqa: E402

TOUCH = 0.3              # mm: closer than this = contact
PIN_ZONE = 9.5           # mm: radius around a shared pin's axis where stacked contact is by design
LINKS = ("O3", "O4", "OL5", "I9", "I12", "IL25")
NAME = {3: "O3", 4: "O4", 5: "OL5", 9: "I9", 12: "I12", 25: "IL25"}


def sample(shape, spacing=0.9):
    """Dense surface points (vertices + subdivided triangles) and a light mesh for display."""
    vs, tris = shape.tessellate(0.15, 0.3)
    V = np.array([(v.x, v.y, v.z) for v in vs]); F = np.array(tris)
    pts = [V]
    for a, b, c in F:
        A, B, C = V[a], V[b], V[c]
        L = max(np.linalg.norm(B - A), np.linalg.norm(C - A), np.linalg.norm(C - B))
        n = int(L / spacing)
        if n >= 1:
            for i in range(n + 1):
                for j in range(n + 1 - i):
                    u, v = i / n, j / n
                    pts.append((A + u * (B - A) + v * (C - A))[None])
    return np.vstack(pts), (V, F)


def build():
    PL = read(STEP)
    links = {NAME[i]: s for i, (n, s) in enumerate(PL) if n.startswith("SHOULDER LINK")}
    bottom = [s for n, s in PL if n == "BOTTOM"][0]
    hw = [s for n, s in PL if n.startswith(("DRY RUNNING", "RETAINING", "M4 ULTRA LOW PROFILE SOCKET HEAD SCREW, 8mm", "0.245"))]
    hw = [s for s in hw if np.linalg.norm(np.array(s.Center().toTuple()) - K.X) < 170]      # shoulder hardware only
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    def d(a, b):
        m = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped); m.Perform(); return m.Value()
    bodies = {k: [v] for k, v in links.items()}
    pin_of = {}
    for s in hw:                                                  # hardware belongs to a pin; it rides with the pin's first link
        c = np.array(s.Center().toTuple())
        p = min(K.PINS, key=lambda q: np.linalg.norm(np.cross(c - K.X, (np.array(K.PINS[q][0]) - K.X) / np.linalg.norm(np.array(K.PINS[q][0]) - K.X))))
        key = f"HW_{p}"
        bodies.setdefault(key, []).append(s); pin_of[key] = p
    clouds, meshes = {}, {}
    for k, parts in list(bodies.items()) + [("BOTTOM", [bottom])]:
        P, Ms = [], []
        for s in parts:
            p, m = sample(s, spacing=1.6 if k == "BOTTOM" else 0.9); P.append(p); Ms.append(m)
        clouds[k] = np.vstack(P); meshes[k] = Ms
    # BOTTOM: only its shoulder end can reach the links
    keep = np.linalg.norm(clouds["BOTTOM"] - K.X, axis=1) < 150
    clouds["BOTTOM_near"] = clouds["BOTTOM"][keep]
    clouds["_pin_of"] = pin_of
    return clouds, meshes, {k: len(v) for k, v in bodies.items()}


def shared_pin(a, b, u=None):
    """Centre of the pin two bodies share, at the current configuration (unit pin vectors u)."""
    for p, (c, ls) in K.PINS.items():
        if a in ls and b in ls:
            c = np.array(c)
            return c if u is None else K.X + u[p] * np.linalg.norm(c - K.X)
    return None


def touching(PA, PB, pin, treeB=None):
    """Min distance between two clouds outside the shared pin zone."""
    if pin is not None:
        ax = (pin - K.X) / np.linalg.norm(pin - K.X)
        def outside(P):
            v = P - K.X; r = v - np.outer(v @ ax, ax)
            return np.linalg.norm(r, axis=1) > PIN_ZONE
        PA = PA[outside(PA)]; PB = PB[outside(PB)]
        treeB = None
    if len(PA) == 0 or len(PB) == 0:
        return 1e9
    tree = treeB or cKDTree(PB)
    dd, _ = tree.query(PA, k=1, distance_upper_bound=5.0)
    return float(dd.min())


def pose(cloud, R):
    return (cloud - K.X) @ R.T + K.X


ZONE = 12.0              # mm around a shared pin where two links are stacked by design


def mover(k, pin_of):
    """Which link frame a body moves with."""
    if k.startswith("HW_"):
        return K.PINS[pin_of[k]][1][0]
    return k


def skip_or_pin(a, b, pin_of, u=None):
    """(skip?, shared pin centre or None) for a body pair."""
    la = set(K.PINS[pin_of[a]][1]) if a.startswith("HW_") else {a}
    lb = set(K.PINS[pin_of[b]][1]) if b.startswith("HW_") else {b}
    if a.startswith("HW_") and b.startswith("HW_"):
        return a == b, None
    if a.startswith("HW_") and (lb & la): return True, None      # a pin's hardware against a link on that pin
    if b.startswith("HW_") and (la & lb): return True, None
    if not a.startswith("HW_") and not b.startswith("HW_"):
        return False, shared_pin(a, b, u)
    return False, None


def min_gap(PA, PB, pin, zone=None):
    if pin is not None:
        ax = (pin - K.X) / np.linalg.norm(pin - K.X)
        def outside(P):
            v = P - K.X
            return np.linalg.norm(v - np.outer(v @ ax, ax), axis=1) > (zone or ZONE)
        PA = PA[outside(PA)]; PB = PB[outside(PB)]
    if len(PA) == 0 or len(PB) == 0:
        return 1e9
    dd, _ = cKDTree(PB).query(PA, k=1, distance_upper_bound=5.0)
    return float(dd.min())


def gamma_scan(job):
    """All collision-free windows of BOTTOM's swing about the output pin (deg, relative to I9) at one sigma."""
    s, (R, u), near, cl, pin_of, others = job
    PO = {k: pose(cl[k], R[mover(k, pin_of)]) for k in others}
    rng = np.random.default_rng(1)
    PO = {k: v[rng.choice(len(v), size=min(30000, len(v)), replace=False)] for k, v in PO.items()}
    ax = u["p0"]                                                 # the output pin where it is now
    def strip(P):                                                # BOTTOM's post boss bears on the p0 stack by design
        v = P - K.X
        return P[np.linalg.norm(v - np.outer(v @ ax, ax), axis=1) > 17.0]
    trees = {k: cKDTree(strip(v) if k in ("O4", "I9") else v) for k, v in PO.items()}
    ok = []
    for g in range(-180, 180, 2):
        RB = K.rot(u["p0"], math.radians(g)) @ R["I9"]
        PB = strip(pose(near, RB))
        clear = True
        for k, t in trees.items():
            dd, _ = t.query(PB, k=1, distance_upper_bound=1.5)
            if dd.min() < 0.8:                                   # sparser clouds: a slightly larger contact distance
                clear = False; break
        ok.append(clear)
    wins, start = [], None
    for i, c in enumerate(ok + [False]):
        g = -180 + 2 * i
        if c and start is None: start = g
        if not c and start is not None:
            wins.append([start, g - 2]); start = None
    if wins and ok[0] and ok[-1] and len(wins) > 1:                # wrap-around
        wins[0][0] = wins[-1][0] - 360; wins.pop()
    return wins


if __name__ == "__main__":
    clouds, meshes, counts = build()
    pin_of = clouds.pop("_pin_of")
    bodies = [k for k in clouds if k not in ("BOTTOM", "BOTTOM_near")]
    pairs = [(a, b) for i, a in enumerate(bodies) for b in bodies[i + 1:] if not skip_or_pin(a, b, pin_of)[0]]
    print("bodies", {k: len(clouds[k]) for k in clouds}, flush=True)
    S = K.sweep_sigma(step_deg=0.5)

    def worst(s):
        R, u = S[s]
        P = {k: pose(clouds[k], R[mover(k, pin_of)]) for k in bodies}
        return min((min_gap(P[a], P[b], skip_or_pin(a, b, pin_of, u)[1]), a, b) for a, b in pairs)
    w0 = worst(0.0)
    print(f"CAD pose: smallest gap {w0[0]:.2f} mm ({w0[1]} / {w0[2]})", flush=True)
    lim = {}
    for direction in (+1, -1):
        s = 0.0; why = "kinematic limit"
        while True:
            nxt = round(s + direction * 0.5, 4)
            if nxt not in S: break
            w = worst(nxt)
            if w[0] < TOUCH:
                why = f"{w[1]} hits {w[2]}"; break
            s = nxt
        lim[direction] = (s, why)
    lo, why_lo = lim[-1]; hi, why_hi = lim[+1]
    print(f"scissor free: sigma {lo} ({why_lo}) .. {hi} ({why_hi})", flush=True)

    near = clouds["BOTTOM_near"]
    rng = np.random.default_rng(0)
    near = near[rng.choice(len(near), size=min(90000, len(near)), replace=False)]
    others = [k for k in bodies if not (k.startswith("HW_") and pin_of[k] == "p0")]
    grid = [x for x in S if lo <= x <= hi and abs(round(x) - x) < 1e-9 and int(round(x)) % 3 == 0]
    import concurrent.futures as cf
    jobs = [(s, S[s], near, {k: clouds[k] for k in others}, pin_of, others) for s in grid]
    with cf.ProcessPoolExecutor(max_workers=max(1, os.cpu_count() - 1)) as ex:
        gam = dict(zip(grid, ex.map(gamma_scan, jobs)))
    for s in grid:
        print(f"  sigma {s:7.1f}: BOTTOM free intervals {gam[s]}", flush=True)
    out = dict(X=K.X.tolist(), pins={k: list(c) for k, (c, _) in K.PINS.items()},
               pin_links={k: list(ls) for k, (_, ls) in K.PINS.items()},
               sigma_free=[lo, hi], sigma_why=[why_lo, why_hi],
               sigma_table={str(s): {"theta0": math.degrees(math.acos(max(-1, min(1, float(S[s][1]["p0"][0]))))),
                                     "R": {k: S[s][0][k].round(6).tolist() for k in LINKS},
                                     "u0": S[s][1]["p0"].round(6).tolist()} for s in S if lo <= s <= hi},
               gamma_free=gam, mover={k: mover(k, pin_of) for k in bodies})
    json.dump(out, open(os.path.join(HERE, "rom_limits.json"), "w"))
    import pickle
    pickle.dump(meshes, open(os.path.join(HERE, "meshes.pkl"), "wb"))
    print("wrote rom_limits.json, meshes.pkl")
