"""A third girdle law: GH-centre displacement vs the thorax from the OpenSim Seth 2016 run (gh_seth.json).

    from seth_law import lift_seth
    d = lift_seth(P)            # P (T, >=2): plane (deg, ISB: 0 abduction .. 90 flexion), elevation (deg); -> (T, 3) mm

Frame: ISB thorax of the Seth model, mm, x anterior, y superior, z lateral (right), displacement from the plane's arm-hanging
(0 deg) posture. Bilinear interpolation of the table (planes 0 / 40 / 90, elevation 0..150 every 10 deg); plane clamped to
0..90, elevation clamped to 0..150. Rows below 15 deg and beyond 132-138 deg come from extrapolated published angle curves
(gh_seth.json 'extrapolated'). variant: 'primary' (equal angle weights, girdle ranges relaxed), 'clamped' (+-45 deg ranges as
distributed), 'w_clav' / 'w_scap' (clavicle / scapula angles weighted 10x). scale: multiply by a body-size factor (the generic
model's SC-GH distance is 137.7 mm; compare.py prints the rig's ratio). numpy only (runs in the repo's python).
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_J = json.load(open(os.path.join(HERE, "gh_seth.json")))


def lift_seth(P, variant="primary", scale=1.0):
    P = np.atleast_2d(np.asarray(P, float))
    G = np.asarray(_J["gh_mm"] if variant == "primary" else _J["variants"][variant]["gh_mm"])     # (planes, elevs, 3)
    pl, el = np.asarray(_J["planes_deg"], float), np.asarray(_J["elev_deg"], float)
    p, t = np.clip(P[:, 0], pl[0], pl[-1]), np.clip(P[:, 1], el[0], el[-1])
    out = np.zeros((len(P), 3))
    for k in range(3):
        per_plane = np.array([np.interp(t, el, G[i, :, k]) for i in range(len(pl))])                  # (planes, T)
        out[:, k] = [np.interp(p[j], pl, per_plane[:, j]) for j in range(len(P))]
    return scale * out
