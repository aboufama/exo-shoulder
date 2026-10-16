"""Placement points of the V0 (side +1) build drive in the design's reference frame (link 1b at q = 0, K on stop A; mm from GH)."""
import os, sys, json, pickle, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drive as DV
out = pickle.load(open(os.path.join(DV.SP, "drive.pkl"), "rb"))
r, a = out[("V0 model ratio 1, r_h 2.49, MR63 roller", 1)]
u2, uK = DV.u2, DV.uK; ax = DV.unit(DV.axis_off); by = np.cross(u2, ax)
dmid = a["dr"][len(a["dr"]) // 2]; pin = DV.unit(u2 - (u2 @ dmid) * dmid)
R = lambda v: [round(float(x), 3) for x in v]
spec = dict(frame="design reference frame (link 1b at q=0, K on stop A), mm from GH; polar frame of the lobe: x = rocker-axis direction from u2, y = u2 x x",
            u2=R(u2), uK=R(uK), lobe_polar_x=R(ax), lobe_polar_y=R(by), rocker_axis_point_lobe_level=R(DV.axis_off + DV.hL * u2), rocker_axis_dir=R(u2),
            rocker_base_on_link1b=R(DV.Pb), roller_centre_onset=R(a["Cs"][0]), crank_pin_onset=R(a["As"][0]), horn_pin_onset=R(a["Bs"][0]),
            horn_pin_end=R(a["Bs"][-1]), horn_axis_point=R(DV.hB * uK), rod_dir_mid=R(dmid), crank_pin_axis_tilted=R(pin),
            crank_pin_tilt_from_u2_deg=round(math.degrees(math.acos(float(pin @ u2))), 1), rod_centre_distance=r["L_rod"],
            lobe_band_from_F2=[6.2, 8.7], F2=round(DV.f2, 3), fK=round(DV.fK, 3), cap_top=round(DV.capTop, 3), horn_plate_top=round(DV.capTop + 1.5, 3),
            q2_onset_deg=round(math.degrees(DV.q2hi), 3), q2_stopB_deg=round(math.degrees(DV.q2hi + DV.s_q * DV.ts[-1]), 3), kK=round(DV.kK, 4))
json.dump(spec, open(os.path.join(DV.SP, "spec_points.json"), "w"), indent=1); print(json.dumps(spec))
