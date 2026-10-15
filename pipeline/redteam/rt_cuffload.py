"""R11 first number: mean interface pressure under the reference's upper-arm cuff when the exo carries its assist torque.
Cuff = 'UPPER ARM CUFF' in exo.glb (arm rest frame). Skin-facing area = faces whose normal points toward the humerus axis
(n . radial < -0.5). Lever = the cuff's skin-facing area centroid distance from GH along the humerus. A torque T about the
GH centre is reacted by a cuff force F = T / lever, spread over the skin-facing area (uniform: a LOWER bound on peak).
    python3 rt_cuffload.py -> results/cuffload.json
"""
import json
import numpy as np
import rt_common as RC
from rt_common import BP
from common import load_parts

HR = np.array(json.load(open(RC.REPO + "/pipeline/avg/body_mesh.json"))["landmarks"]["rest_humerus"])
out = {}
for g, n, V, F in load_parts(RC.DD):
    if not n.startswith("UPPER ARM CUFF"): continue
    X = V @ HR                                                                  # rest -> canonical arm frame (humerus = -y)
    A, B, C = X[F[:, 0]], X[F[:, 1]], X[F[:, 2]]; cr = np.cross(B - A, C - A); ar = 0.5 * np.linalg.norm(cr, axis=1); nn = cr / (2 * ar[:, None] + 1e-12)
    cen = (A + B + C) / 3; rad = cen.copy(); rad[:, 1] = 0; rad /= np.linalg.norm(rad, axis=1, keepdims=True) + 1e-12
    inner = (nn * rad).sum(1) < -0.5; Ai = ar[inner].sum(); s = -(cen[inner, 1] * ar[inner]).sum() / Ai
    th = np.degrees(np.arctan2(-cen[inner, 0], cen[inner, 2]))
    out = dict(part=n, skin_facing_area_cm2=round(float(Ai / 100), 1), lever_mm=round(float(s), 1),
               theta_span_deg=[round(float(np.percentile(th, 2))), round(float(np.percentile(th, 98)))], s_span_mm=[round(float(-cen[inner, 1].max())), round(float(-cen[inner, 1].min()))])
    for T in (25.0, 10.0, 5.0):
        Fn = T / (s / 1000); p = Fn / (Ai * 1e-6)
        out[f"T{T:.0f}Nm"] = dict(force_N=round(float(Fn)), mean_pressure_kPa=round(float(p / 1000), 1), mean_pressure_mmHg=round(float(p / 133.3)))
# where must an elevation assist push? the arm's underside (world down, perpendicular to the humerus) in the arm frame,
# every clip frame with elevation >= 45 deg, vs the rigid saddle's theta span
from rt_common import GD
FR = RC.clips(); W = np.array([f[2] for f in FR], float); th = []
for w in W:
    d = GD.Rh_of(*w[:3]).T @ np.array([0, -1.0, 0]); d[1] = 0
    th.append(np.degrees(np.arctan2(-d[0], d[2])) if np.linalg.norm(d) > 0.3 else np.nan)
th = np.array(th); m = (W[:, 1] >= 45) & np.isfinite(th); lo, hi = out["theta_span_deg"]
out["assist_underside"] = dict(frames_elev_ge_45=int(m.sum()), share_on_rigid_saddle=round(float(((th >= lo) & (th <= hi))[m].mean()), 3),
                               underside_theta_p5_p50_p95=np.percentile(th[m], [5, 50, 95]).round().tolist(),
                               note="theta 0 = lateral, +90 = posterior, 180 = medial; the elevation-assist load lands where the arm faces down")
RC.jdump(out, "cuffload.json"); print(json.dumps(out, indent=1))
