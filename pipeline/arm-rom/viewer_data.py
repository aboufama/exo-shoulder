"""Exports for the arm ROM viewer: arm_exo.glb (every exo part, grouped by what moves together, CAD frame in metres
via glTF) and arm_rom.json (mechanism tables, BOTTOM swing windows, elbow geometry, body-collision point samples).

    python3 viewer_data.py
"""
import json
import math
import os
import sys

import numpy as np
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "joint-verification")); sys.path.insert(0, os.path.join(HERE, "..", "joint-render"))
sys.argv = sys.argv[:1] + [os.path.join(HERE, "source", "right_arm.step")]
from features import read                                       # noqa: E402
from build_scene import mesh, write_glb                         # noqa: E402
import kinematics as K                                          # noqa: E402
import collisions as C                                          # noqa: E402

L = json.load(open(os.path.join(HERE, "rom_limits.json")))
E_AXIS = np.array([0.397, 0.765, 0.507]); E_AXIS /= np.linalg.norm(E_AXIS)
E_CENTRE = np.array([-435.77, 169.63, 224.11])
F_PT, F_DIR = np.array([-488.56, 123.08, 225.73]), np.array([-0.7125, -0.0914, 0.6956])


def closest(p1, d1, p2, d2):
    """Midpoint of the shortest segment between two lines."""
    w = p1 - p2; a, b, c, d, e = d1 @ d1, d1 @ d2, d2 @ d2, d1 @ w, d2 @ w
    den = a * c - b * b; s = (b * e - c * d) / den; t = (a * e - b * d) / den
    return (p1 + s * d1 + p2 + t * d2) / 2, float(np.linalg.norm(p1 + s * d1 - p2 - t * d2))


if __name__ == "__main__":
    PL = read(sys.argv[1])
    elbow_h, miss = closest(E_CENTRE, E_AXIS, F_PT, F_DIR / np.linalg.norm(F_DIR))
    print(f"human elbow centre {elbow_h.round(1)} (axes miss by {miss:.1f} mm); upper arm {np.linalg.norm(elbow_h - K.X):.0f} mm")
    hum = (elbow_h - K.X) / np.linalg.norm(elbow_h - K.X); fdir = F_DIR / np.linalg.norm(F_DIR)
    print(f"CAD elbow flexion {math.degrees(math.acos(hum @ fdir)):.1f} deg")

    # group every part by the body it moves with
    links = {C.NAME[i]: s for i, (n, s) in enumerate(PL) if n.startswith("SHOULDER LINK")}
    group = {k: [v] for k, v in links.items()}
    forearm_names = ("MIDDLE", "FOREARM CUFF")
    for i, (n, s) in enumerate(PL):
        c = np.array(s.Center().toTuple())
        if n.startswith("SHOULDER LINK"):
            continue
        if n in forearm_names or (n.startswith("Hex socket head countersunk") ):
            group.setdefault("FOREARM", []).append(s); continue
        if np.linalg.norm(c - K.X) < 170 and n.startswith(("DRY RUNNING", "RETAINING", "M4 ULTRA LOW PROFILE SOCKET HEAD SCREW, 8mm", "0.245")):
            p = min(K.PINS, key=lambda q: np.linalg.norm(np.cross(c - K.X, K.U0[q])))
            owner = "BOTTOM" if p == "p0" else K.PINS[p][1][0]
            group.setdefault(owner, []).append(s); continue
        group.setdefault("BOTTOM", []).append(s)                 # BOTTOM, elbow joint (TOP, bearing, washers, magnet, screws)
    items = []
    for gname, parts in group.items():
        for j, s in enumerate(parts):
            Pm, N, T, I = mesh(s, lin=0.06, ang=0.2)
            items.append((f"{gname}__{j}", Pm, N, T, I))
        print(f"{gname:8s} {len(parts):3d} parts", flush=True)
    write_glb(os.path.join(HERE, "arm_exo.glb"), items)
    print("arm_exo.glb", os.path.getsize(os.path.join(HERE, "arm_exo.glb")) // 1024, "KB")

    # sparse surface samples of every moving exo body, for body-collision checks in the viewer
    rng = np.random.default_rng(0)
    samples = {}
    for gname, parts in group.items():
        pts = np.vstack([C.sample(s, spacing=4.0)[0] for s in parts])
        if gname == "BOTTOM":
            pts = pts[np.linalg.norm(pts - K.X, axis=1) < 260]      # only its shoulder half can meet the torso/head
        if gname == "FOREARM":
            continue
        samples[gname] = pts[rng.choice(len(pts), size=min(400, len(pts)), replace=False)].round(1).tolist()
    sig = sorted(float(s) for s in L["sigma_table"])
    out = dict(
        X=L["X"], U0={k: v.tolist() for k, v in K.U0.items()},
        sigma=[s for s in sig if abs(s * 2 - round(s * 2)) < 1e-9],
        theta0=[L["sigma_table"][str(s)]["theta0"] for s in sig if abs(s * 2 - round(s * 2)) < 1e-9],
        R={lk: [L["sigma_table"][str(s)]["R"][lk] for s in sig if abs(s * 2 - round(s * 2)) < 1e-9] for lk in C.LINKS},
        u0=[L["sigma_table"][str(s)]["u0"] for s in sig if abs(s * 2 - round(s * 2)) < 1e-9],
        gamma=[[float(s), w[0][0], w[0][1]] for s, w in sorted(((float(k), v) for k, v in L["gamma_free"].items())) if w],
        sigma_why=L["sigma_why"], elbow=dict(centre=E_CENTRE.tolist(), axis=E_AXIS.tolist(), human=elbow_h.tolist(),
                                            forearm_dir=fdir.tolist(), exo_flex_limit=142.0),
        samples=samples)
    json.dump(out, open(os.path.join(HERE, "arm_rom.json"), "w"))
    print("arm_rom.json", os.path.getsize(os.path.join(HERE, "arm_rom.json")) // 1024, "KB")
