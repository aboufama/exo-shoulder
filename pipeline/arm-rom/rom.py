"""Human shoulder poses vs the exo: which humerus orientations the shoulder mechanism can follow, and what stops it.

Human: ISB shoulder angles (thorax -> humerus, Y-X-Y): plane of elevation (0 = abduction plane, 90 = flexion plane),
elevation (0 = arm down), axial rotation (+ internal). Body frame assumed from the CAD: Z up, +Y lateral (right),
+X posterior (the scapula mount sits 124 mm behind the shoulder centre). BOTTOM is rigidly strapped to the upper arm,
so the exo must reproduce the humerus orientation exactly; the human elbow axis is the exo elbow axis.
Exo inverse kinematics: output-pin direction u0 = R_B u0_cad fixes the scissor opening sigma (from its angle to the
base axis) and the base swing psi; BOTTOM's swing gamma about the output pin is what remains. A pose is reachable if
sigma is inside the collision-free scissor range and gamma inside BOTTOM's free window at that sigma.
Writes rom_summary.json (per-pose grid + headline ranges) and prints the summary.
"""
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(HERE, "rom_limits.json")))
X = np.array(L["X"])
U0 = {k: (np.array(c) - X) / np.linalg.norm(np.array(c) - X) for k, c in L["pins"].items()}
SIG = sorted(float(s) for s in L["sigma_table"])
TH = np.array([L["sigma_table"][f"{s}" if f"{s}" in L["sigma_table"] else str(s)]["theta0"] for s in SIG])
GRID = sorted(float(s) for s in L["gamma_free"])
E_AXIS = np.array([0.397, 0.765, 0.507]); E_AXIS /= np.linalg.norm(E_AXIS)
E_CENTRE = np.array([-435.77, 169.63, 224.11])          # exo elbow joint centre (CAD)
FOREARM_OFFSET = 53.0                                   # arm axis sits this far medial of the joint (cuff geometry)
M = np.column_stack([[-1, 0, 0], [0, 0, 1], [0, 1, 0]]) # thorax axes (anterior, up, right) in CAD coordinates


def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


Ry = lambda a: rot([0, 1, 0], a)
Rx = lambda a: rot([1, 0, 0], a)
ELBOW_H = E_CENTRE - FOREARM_OFFSET * E_AXIS           # human elbow centre in the CAD pose
H_LEN = float(np.linalg.norm(ELBOW_H - X))


def humerus_cad():
    y = (X - ELBOW_H) / H_LEN                            # elbow -> shoulder
    z = E_AXIS - (E_AXIS @ y) * y; z /= np.linalg.norm(z)  # lateral, along the flexion axis
    return np.column_stack([np.cross(y, z), y, z])


H_CAD = humerus_cad()


def human_R(plane, elev, axial):
    """Humerus frame in CAD coordinates for ISB angles (deg)."""
    return M @ (Ry(math.radians(plane)) @ Rx(-math.radians(elev)) @ Ry(math.radians(axial)))


def sigma_of(theta):
    """Scissor opening for an output-pin angle from the base axis (TH decreases with sigma)."""
    if theta > TH.max() or theta < TH.min():
        return None
    return float(np.interp(-theta, -TH, SIG))


def table_R(s, link):
    k = min(SIG, key=lambda v: abs(v - s))
    key = f"{k}" if f"{k}" in L["sigma_table"] else str(k)
    return np.array(L["sigma_table"][key]["R"][link]), np.array(L["sigma_table"][key]["u0"])


def gamma_window(s):
    """Free window of BOTTOM's swing (deg) interpolated between the scanned sigmas."""
    i = int(np.searchsorted(GRID, s)); i = max(1, min(len(GRID) - 1, i))
    a, b = GRID[i - 1], GRID[i]; t = (s - a) / (b - a) if b > a else 0
    wa, wb = L["gamma_free"][str(a) if str(a) in L["gamma_free"] else f"{a}"], L["gamma_free"][str(b) if str(b) in L["gamma_free"] else f"{b}"]
    if not wa or not wb:
        return None
    lo = wa[0][0] + (wb[0][0] - wa[0][0]) * t; hi = wa[0][1] + (wb[0][1] - wa[0][1]) * t
    return lo, hi


def exo_ik(Hh):
    """(ok, reason, sigma, psi, gamma) for a humerus orientation (3x3, CAD)."""
    RB = Hh @ H_CAD.T
    u0 = RB @ U0["p0"]
    theta = math.degrees(math.acos(max(-1, min(1, u0[0]))))
    s = sigma_of(theta)
    if s is None:
        lim = "scissor fully closed (I9 hits IL25)" if theta < TH.min() else "scissor fully open (I12 hits IL25)"
        return False, lim, None, None, None
    RI9, u0s = table_R(s, "I9")
    psi = math.atan2(u0[2], u0[1]) - math.atan2(u0s[2], u0s[1])
    RI9 = rot([1, 0, 0], psi) @ RI9
    Rg = RB @ RI9.T                                      # rotation about u0 by gamma
    g = math.degrees(math.atan2(np.dot(u0, [Rg[2, 1] - Rg[1, 2], Rg[0, 2] - Rg[2, 0], Rg[1, 0] - Rg[0, 1]]), np.trace(Rg) - 1))
    w = gamma_window(s)
    if w is None:
        return False, "no free BOTTOM swing", s, psi, g
    if g > w[1]:
        return False, "BOTTOM hits I9 (output inner link)", s, psi, g
    if g < w[0]:
        return False, "BOTTOM hits O4 (output outer link)", s, psi, g
    return True, "ok", s, psi, g


def human_ok(plane, elev, axial):
    """Rough healthy-adult limits (ISB angles)."""
    if elev < 0 or elev > 180: return False
    if plane < -60 or plane > 140: return False            # horizontal abduction 60 / adduction 140 (from abduction plane)
    if plane < 0 and elev > 120: return False              # extension side cannot go overhead
    lo, hi = -90, 70                                       # external .. internal rotation
    if elev < 30: lo, hi = -80, 80
    return lo <= axial <= hi


if __name__ == "__main__":
    print(f"implied upper-arm length (shoulder centre to elbow centre): {H_LEN:.0f} mm")
    rows, total, reach, reasons = [], 0, 0, {}
    for plane in range(-60, 141, 5):
        for elev in range(0, 181, 5):
            for axial in range(-90, 91, 10):
                if not human_ok(plane, elev, axial):
                    continue
                total += 1
                ok, why, s, psi, g = exo_ik(human_R(plane, elev, axial))
                reach += ok; reasons[why] = reasons.get(why, 0) + 1
                rows.append([plane, elev, axial, int(ok)])
    print(f"human shoulder poses sampled: {total}; exo can follow {reach} ({100 * reach / total:.0f}%)")
    for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"   {v:6d}  {k}")

    def sweep(plane, axial, label):
        ok_e = [e for e in range(0, 181) if exo_ik(human_R(plane, e, axial))[0]]
        bad = next((e for e in range(0, 181) if not exo_ik(human_R(plane, e, axial))[0]), None)
        why = exo_ik(human_R(plane, bad, axial))[1] if bad is not None else ""
        print(f"  {label:34s} reachable elevation {min(ok_e) if ok_e else '-'}..{max(ok_e) if ok_e else '-'} deg"
              + (f"   first stop {bad} deg: {why}" if bad is not None else "   (no stop up to 180)"))
        return [min(ok_e), max(ok_e)] if ok_e else None
    print("single-plane elevations (axial rotation 0):")
    heads = dict(flexion=sweep(90, 0, "flexion (sagittal plane)"), scaption=sweep(30, 0, "scaption (30 deg plane)"),
                 abduction=sweep(0, 0, "abduction (frontal plane)"), extension=sweep(-60, 0, "extension side (-60 plane)"))
    print("axial rotation reachable:")
    for elev, plane in ((0, 0), (90, 0), (90, 90)):
        rr = [a for a in range(-90, 91) if exo_ik(human_R(plane, elev, a))[0]]
        print(f"  at elevation {elev:3d}, plane {plane:3d}: {min(rr) if rr else '-'} .. {max(rr) if rr else '-'} deg")
    cad = exo_ik(H_CAD)
    json.dump(dict(upper_arm_mm=H_LEN, total=total, reach=reach, reasons=reasons, grid=rows, heads=heads),
              open(os.path.join(HERE, "rom_summary.json"), "w"))
