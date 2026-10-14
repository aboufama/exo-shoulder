"""Kinematics of the EXO right-arm shoulder: a two-stage spherical scissor (remote centre at the glenohumeral joint).

Every pin axis passes through the remote centre X. Bodies: ground (scapula mount), O3/I12 (base outer/inner links
on the base pin), IL25/OL5 (long inner/outer links crossing at the middle pin), O4/I9 (output links) and BOTTOM
(upper-arm link, on the output pin). Configuration: alpha, beta = rotations of O3 and I12 about the base pin (x axis)
from the CAD pose, gamma = BOTTOM about the output pin relative to I9. sigma = alpha - beta opens/closes the scissor;
psi = (alpha + beta) / 2 swings the whole mechanism about the base axis (no change in shape).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
X = np.array([-119.5, 0.0, 0.0])                               # remote centre (from the pin axes; exact to 0.01 mm)
# pin centres in the CAD pose (STEP frame, mm) and the links each joins
PINS = {
    "p0": ((-70.1, 95.1, 63.1), ("O4", "I9", "BOTTOM")),         # output: BOTTOM's post
    "p1": ((-51.1, 32.1, 98.8), ("OL5", "I9")),
    "p2": ((-17.6, 61.1, -36.9), ("OL5", "I12")),
    "p3": ((4.9, 0.0, 0.0), ("O3", "I12")),                      # base pin, fixed to the scapula mount
    "p4": ((-51.1, 103.5, -8.7), ("O4", "IL25")),
    "p5": ((-17.6, -10.3, 70.6), ("O3", "IL25")),
    "p6": ((-15.5, 56.9, 37.8), ("OL5", "IL25")),               # middle crossing
}
U0 = {k: (np.array(c) - X) / np.linalg.norm(np.array(c) - X) for k, (c, _) in PINS.items()}


def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


def align(a0, b0, a, b):
    """Rotation taking the pair (a0, b0) onto (a, b) (unit vectors with equal separation)."""
    def frame(p, q):
        e1 = p; e3 = np.cross(p, q); e3 /= np.linalg.norm(e3); e2 = np.cross(e3, e1)
        return np.column_stack([e1, e2, e3])
    return frame(a, b) @ frame(a0, b0).T


def intersect(c1, r1, c2, r2, near):
    """Points on the unit sphere at angular distance r1 from c1 and r2 from c2; the one nearer `near`."""
    n = np.cross(c1, c2); s = np.linalg.norm(n)
    if s < 1e-9:
        return None
    n /= s
    # x = a c1 + b c2 + t n with c1.x = cos r1, c2.x = cos r2, |x| = 1
    d = c1 @ c2
    A = np.array([[1, d], [d, 1]]); rhs = np.array([math.cos(r1), math.cos(r2)])
    a, b = np.linalg.solve(A, rhs)
    p = a * c1 + b * c2; h2 = 1 - p @ p
    if h2 < 0:
        return None
    h = math.sqrt(h2)
    s1, s2 = p + h * n, p - h * n
    return s1 if np.linalg.norm(s1 - near) < np.linalg.norm(s2 - near) else s2


ARC = lambda a, b: math.acos(max(-1.0, min(1.0, float(U0[a] @ U0[b]))))


def fk(alpha, beta, prev=None):
    """Link rotations (from the CAD pose) for base angles alpha (O3) and beta (I12), radians. None if no assembly."""
    prev = prev or U0
    R = {"O3": rot([1, 0, 0], alpha), "I12": rot([1, 0, 0], beta)}
    u = {"p3": U0["p3"]}
    u["p5"] = R["O3"] @ U0["p5"]; u["p2"] = R["I12"] @ U0["p2"]
    u["p6"] = intersect(u["p5"], ARC("p5", "p6"), u["p2"], ARC("p2", "p6"), prev["p6"])
    if u["p6"] is None:
        return None
    R["IL25"] = align(U0["p5"], U0["p6"], u["p5"], u["p6"]); R["OL5"] = align(U0["p2"], U0["p6"], u["p2"], u["p6"])
    u["p4"] = R["IL25"] @ U0["p4"]; u["p1"] = R["OL5"] @ U0["p1"]
    u["p0"] = intersect(u["p4"], ARC("p4", "p0"), u["p1"], ARC("p1", "p0"), prev["p0"])
    if u["p0"] is None:
        return None
    R["O4"] = align(U0["p4"], U0["p0"], u["p4"], u["p0"]); R["I9"] = align(U0["p1"], U0["p0"], u["p1"], u["p0"])
    return R, u


def sweep_sigma(step_deg=0.25, limit=200):
    """Open and close the scissor from the CAD pose (psi = 0) until it can no longer assemble."""
    out = {0.0: fk(0, 0)}
    for sgn in (+1, -1):
        prev = U0; s = 0.0
        while abs(s) < limit:
            s += sgn * step_deg
            r = fk(math.radians(s) / 2, -math.radians(s) / 2, prev)
            if r is None:
                break
            out[round(s, 4)] = r; prev = r[1]
    return dict(sorted(out.items()))


if __name__ == "__main__":
    print("arcs between pins on each link (deg):")
    for L, pr in (("O3", ("p3", "p5")), ("I12", ("p3", "p2")), ("IL25", ("p5", "p6", "p4")), ("OL5", ("p2", "p6", "p1")),
                  ("O4", ("p4", "p0")), ("I9", ("p1", "p0"))):
        print(f"  {L:5s}", "  ".join(f"{a}-{b} {math.degrees(ARC(a, b)):.2f}" for a, b in zip(pr, pr[1:])),
              f"   total {math.degrees(ARC(pr[0], pr[-1])):.2f}")
    S = sweep_sigma()
    ss = sorted(S)
    th = {s: math.degrees(math.acos(S[s][1]["p0"] @ np.array([1, 0, 0]))) for s in ss}
    print(f"sigma assembles from {ss[0]:.2f} to {ss[-1]:.2f} deg; CAD pose sigma 0")
    for s in ss[:: max(1, len(ss) // 24)] + [ss[-1]]:
        print(f"  sigma {s:8.2f}  output pin angle from base axis {th[s]:7.2f} deg")
