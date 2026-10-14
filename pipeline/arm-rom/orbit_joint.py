"""The Orbit Joint: a ring-free joint that turns the cuff EXACTLY about the humerus axis, from pivots and tendons only.

Cross-section of the upper arm at station s (all three pivot axes parallel to the humerus axis h, through O on it):
  crank   pivots on the upper-arm bar at P, crank vector c (fixed length);  tip E = P + R(t) c
  coupler pivots on the crank tip E; tendon loop 1 (bar pulley at P -> coupler pulley at E, 1:1) holds its orientation,
          so the coupler only translates: it carries G = E + (G0 - P - c)
  bracket (cuff) pivots on the coupler at G; tendon loop 2 (crank pulley at E -> bracket pulley at G, 1:1) turns it by t
With c = G0 - O the bracket pose is  X -> O + R(t)(X - O): a pure rotation about the humerus axis, for every t, with no
pivot on that axis and nothing encircling the arm. No dead points (the tendons replace parallelogram links); travel is
limited only by the crank tip E nearing the arm.
"""
import math
import numpy as np


def rot2(t):
    c, s = math.cos(t), math.sin(t); return np.array([[c, -s], [s, c]])


def configure(rho, gam, dp, dphi, clear=12.0):
    """rho: arm skin radius at the station; G0 at azimuth gam, radius rho+clear; P at azimuth gam+dphi, radius dp."""
    d = rho + clear
    G0 = d * np.array([math.cos(gam), math.sin(gam)]); P = dp * np.array([math.cos(gam + dphi), math.sin(gam + dphi)])
    return dict(G0=G0, P=P, c=G0.copy(), off=G0 - P - G0)


def pose(J, t):
    R = rot2(t); E = J["P"] + R @ J["c"]; G = E + J["off"]
    return dict(P=J["P"], E=E, G=G)


def check_exact(J, ts):
    """max deviation of the bracket from a pure rotation about O (should be ~0)."""
    err = 0
    for t in ts:
        p = pose(J, t); X0 = J["G0"] + np.array([5.0, 3.0])               # any bracket point
        Xt = p["G"] + rot2(t) @ (X0 - J["G0"]); err = max(err, np.linalg.norm(Xt - rot2(t) @ X0))
    return err


def envelope(J, t, n=5):
    """points on the moving links (crank P..E, coupler E..G) in the cross-section, for collision checks."""
    p = pose(J, t); pts = [p["P"] + (p["E"] - p["P"]) * k / (n - 1) for k in range(n)] + [p["E"] + (p["G"] - p["E"]) * k / (n - 1) for k in range(n)]
    return np.array(pts)


if __name__ == "__main__":
    J = configure(55.0, 0.0, 90.0, math.radians(60))
    ts = np.radians(np.linspace(-120, 120, 49))
    print("pure-rotation error over +-120 deg:", round(check_exact(J, ts), 9), "mm")
    rmin = min(np.linalg.norm(envelope(J, t), axis=1).min() for t in ts)
    print("closest approach of the moving links to the arm axis:", round(rmin, 1), "mm (arm skin at 55)")
    for deg in (-110, 0, 110):
        p = pose(J, math.radians(deg)); print(deg, {k: v.round(1).tolist() for k, v in p.items()})
