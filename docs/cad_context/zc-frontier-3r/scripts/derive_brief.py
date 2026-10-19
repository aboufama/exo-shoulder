"""Derive the tables of CAD_CONTEXT.md from geometry.json (no model run, no body data).

Writes derived.json and link_sketch_profiles.csv next to geometry.json:
  - FK re-check of the key poses from the rest data (the convention the brief states),
  - sketch planes (origin GH, x = start axis, normal) and 2-D underside profiles of link 1, link 2 and the neck,
  - swept part-to-part clearances on the model's metal (hub cylinders exact, straps as 0.5 mm point clouds),
  - BOTTOM's bar frame (from the K7 interface) in the as-built frame at rest, and its clearance to the chain per station.
Usage: python3 derive_brief.py [folder]   (default: this script's parent folder)
"""
import csv, json, math, sys
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
g = json.load(open(D / "geometry.json"))
U = lambda v: np.asarray(v, float) / np.linalg.norm(v)


def rot(k, deg):
    k = U(k); a = math.radians(deg); K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


J = {j: U(g["hubs"][j]["axis_unit_rest"]) for j in ("J1", "J2", "J3")}
F = {j: g["hubs"][j]["F_mm"] for j in ("J1", "J2", "J3")}
th_rest = np.array(g["rest_pose"]["theta_deg"])
a1, a2 = g["arcs"]["a1_deg"], g["arcs"]["a2_deg"]
out = {}


def fk(dth):
    R1 = rot(J["J1"], dth[0]); R2 = R1 @ rot(J["J2"], dth[1]); R3 = R2 @ rot(J["J3"], dth[2])
    return R1, R2, R3


# 1. FK re-check of the key poses (theta convention of the brief)
chk = []
for kp in g["key_poses"][1:]:
    R1, R2, R3 = fk(np.array(kp["theta_deg"]) - th_rest)
    ax = {"J1": J["J1"], "J2": R1 @ J["J2"], "J3": R2 @ J["J3"]}
    e_ax = max(math.degrees(math.acos(min(1, float(ax[j] @ U(kp["axes_as_built"][j]))))) for j in ax)
    e_cr = max(float(np.linalg.norm(ax[j] * (F[j] + 12.25) - np.array(kp["hub_crown_centres_as_built"][j]))) for j in ax)
    th = math.degrees(math.acos(float(ax["J1"] @ ax["J3"])))
    chk.append({"label": kp["label"], "max_axis_err_deg": e_ax, "max_crown_err_mm": e_cr, "th": th, "th_json": kp["th_deg"]})
out["fk_check"] = chk


# 2. sketch planes and 2-D profiles
def grid(name):
    L = g["links"][name]
    return np.array(L["model_sample_grid_underside"]).reshape(L["n_along"], L["n_across"], 3), L


land = U(g["bottom_interface"]["landing_direction_as_built_rest"])
planes, prof_rows = {}, []
for name, s, e, t in (("link1", "J1", "J2", 3.0), ("link2", "J2", "J3", 3.0), ("neck", "J3", None, 6.0)):
    e1 = J[s]; ev = J[e] if e else land
    ang = math.degrees(math.acos(float(e1 @ ev)))
    e2 = U(ev - (e1 @ ev) * e1); n = np.cross(e1, e2)
    P, L = grid(name)
    c = P[:, (L["n_across"] - 1) / 2 == np.arange(L["n_across"])] if L["n_across"] % 2 else 0.5 * (P[:, L["n_across"] // 2 - 1] + P[:, L["n_across"] // 2])
    c = c.reshape(-1, 3)
    off = float(np.abs(c @ n).max())
    planes[name] = {"origin": [0, 0, 0], "x_dir_start_axis": e1.round(6).tolist(), "y_dir": e2.round(6).tolist(),
                    "normal": n.round(6).tolist(), "arc_deg": round(ang, 4), "centre_samples_off_plane_mm": off}
    for i, p in enumerate(c):
        r = float(np.linalg.norm(p)); phi = math.degrees(math.atan2(float(p @ e2), float(p @ e1)))
        prof_rows.append([name, i, round(phi, 4), round(r, 3), round(r + t, 3),
                          round(r * math.cos(math.radians(phi)), 3), round(r * math.sin(math.radians(phi)), 3),
                          round((r + t) * math.cos(math.radians(phi)), 3), round((r + t) * math.sin(math.radians(phi)), 3)])
out["sketch_planes"] = planes
with open(D / "link_sketch_profiles.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["member", "sample", "phi_deg_from_start_axis", "r_underside_mm", "r_top_mm",
                "sketch_x_under", "sketch_y_under", "sketch_x_top", "sketch_y_top"])
    w.writerows(prof_rows)


# 3. point clouds of the model's metal (underside + top + both side faces, ~0.5 mm)
def cloud(name, t, step=0.5):
    P, L = grid(name); na, nc = P.shape[:2]
    ia = np.linspace(0, na - 1, int((na - 1) * 2 / step) + 1); ic = np.linspace(0, nc - 1, int((nc - 1) * 2 / step) + 1)
    def interp(A):
        i0 = np.clip(np.floor(ia).astype(int), 0, na - 2); fa = (ia - i0)[:, None, None]
        B = A[i0] * (1 - fa) + A[i0 + 1] * fa
        j0 = np.clip(np.floor(ic).astype(int), 0, nc - 2); fc = (ic - j0)[None, :, None]
        return B[:, j0] * (1 - fc) + B[:, j0 + 1] * fc
    Q = interp(P); r = np.linalg.norm(Q, axis=2, keepdims=True); Uq = Q / r
    pts = [Q, Q + t * Uq]
    for k in np.linspace(0, t, int(t / step) + 1):
        pts.append((Q[:, [0, -1]] + k * Uq[:, [0, -1]]))
    return np.concatenate([p.reshape(-1, 3) for p in pts])


C = {"link1": cloud("link1", 3.0), "link2": cloud("link2", 3.0), "neck": cloud("neck", 6.0)}


def hub_dist(p, j, R=np.eye(3)):
    k = R @ J[j]; a = p @ k; d = np.linalg.norm(p - a[:, None] * k, axis=1)
    return np.sqrt(np.maximum(d - 10, 0) ** 2 + np.maximum(np.maximum(F[j] - a, a - F[j] - 12.25), 0) ** 2)


def axis_off(p, j, R=np.eye(3)):
    k = R @ J[j]; a = p @ k
    return np.linalg.norm(p - a[:, None] * k, axis=1)


q2_rest = th_rest[1]
ths = lambda q2: math.degrees(math.acos(math.cos(math.radians(a1)) * math.cos(math.radians(a2)) +
                                        math.sin(math.radians(a1)) * math.sin(math.radians(a2)) * math.cos(math.radians(q2))))
sw = {}
# link 2 vs hub 1 near the folded stop (only theta2 matters)
rows = []
for q2 in np.arange(-24.389, -40.01, -0.25):
    d = float(hub_dist(C["link2"] @ rot(J["J2"], q2 - q2_rest).T, "J1").min())
    rows.append((round(float(q2), 3), round(ths(q2), 3), round(d, 3)))
sw["link2_to_hub1_near_fold"] = rows
sw["link2_to_hub1_1mm_at_theta2"] = next(r for r in rows if r[2] >= 1.0)
sw["link2_to_hub1_2mm_at_theta2"] = next(r for r in rows if r[2] >= 2.0)
sw["link2_to_hub1_at_-30"] = min(rows, key=lambda r: abs(r[0] + 30))

STOP_FOLD, STOP_STR = -30.0, -147.9
q2s = np.linspace(STOP_STR, STOP_FOLD, 60)
q3_lo, q3_hi = g["joint_ranges"]["verifier_bench_taken_all"]["dtheta3_from_rest"]
d3s = np.linspace(q3_lo, q3_hi, 60)


def pair_min(A, B):
    if len(A) == 0 or len(B) == 0:
        return float("inf")
    return float(cKDTree(B).query(A, k=1)[0].min())


# link 1 vs link 2 outside the J2 seat zone (> 14 mm from the J2 axis): theta2 only
l1 = C["link1"][axis_off(C["link1"], "J2") > 14.0]
res = []
for q2 in q2s:
    B = C["link2"] @ rot(J["J2"], q2 - q2_rest).T
    B = B[axis_off(B, "J2") > 14.0]
    res.append((round(float(q2), 2), round(pair_min(l1, B), 2)))
sw["link1_to_link2_outside_J2_seat"] = {"min": min(res, key=lambda r: r[1]), "at_stops": [res[0], res[-1]]}
# neck vs link 2 outside the J3 seat zone (> 14 mm from the J3 axis): theta3 only
l2 = C["link2"][axis_off(C["link2"], "J3") > 14.0]
res = []
for d3 in d3s:
    B = C["neck"] @ rot(J["J3"], d3).T
    B = B[axis_off(B, "J3") > 14.0]
    res.append((round(float(d3), 2), round(pair_min(l2, B), 2)))
sw["neck_to_link2_outside_J3_seat_over_taken_theta3"] = {"min": min(res, key=lambda r: r[1])}
# neck vs link 2 inside the seat zone: is the neck ever over link 2 there (vertical gap)?
l2s = C["link2"][(axis_off(C["link2"], "J3") > 10.0) & (axis_off(C["link2"], "J3") <= 14.0)]
res = []
for d3 in d3s:
    B = C["neck"] @ rot(J["J3"], d3).T
    B = B[(axis_off(B, "J3") > 10.0) & (axis_off(B, "J3") <= 14.0)]
    res.append((round(float(d3), 2), round(pair_min(l2s, B), 2)))
sw["neck_to_link2_in_J3_seat_ring_10_14_over_taken_theta3"] = {"min": min(res, key=lambda r: r[1])}
# link 1 and hub 1 vs neck / hub 3 / link 2 combos over (theta2, theta3) rectangle (conservative)
m_l1n, m_h1n, m_h2n = [], [], []
for q2 in q2s[::3]:
    R2 = rot(J["J2"], q2 - q2_rest)
    for d3 in d3s[::3]:
        R3 = R2 @ rot(J["J3"], d3)
        N = C["neck"] @ R3.T
        m_l1n.append((round(float(q2), 1), round(float(d3), 1), round(pair_min(C["link1"], N), 2)))
        m_h1n.append((round(float(q2), 1), round(float(d3), 1), round(float(hub_dist(N, "J1").min()), 2)))
for d3 in d3s:
    N = C["neck"] @ rot(J["J3"], d3).T
    m_h2n.append((round(float(d3), 1), round(float(hub_dist(N, "J2").min()), 2)))
sw["link1_to_neck_over_theta2_theta3_rectangle"] = min(m_l1n, key=lambda r: r[2])
sw["hub1_to_neck_over_theta2_theta3_rectangle"] = min(m_h1n, key=lambda r: r[2])
sw["hub2_to_neck_over_taken_theta3"] = min(m_h2n, key=lambda r: r[1])
sw["stops_used"] = {"folded": STOP_FOLD, "stretched": STOP_STR, "th_at_folded": ths(STOP_FOLD), "th_at_stretched": ths(STOP_STR)}
out["swept_clearances_model_metal"] = sw

# 4. BOTTOM's bar frame (K7) in the as-built frame at rest
bi = g["bottom_interface"]; H = np.array([bi["H_axes_at_rest_as_built"][k] for k in ("Hx", "Hy", "Hz")]).T  # columns
toB = lambda v: (H @ np.asarray(v, float))
anchor_H = np.array([0, -64.65, 74.45]); u_H = np.array([0, 0.9975, 0.0713]); v_H = np.array([-1.0, 0, 0]); z_H = np.array([0, -0.0713, 0.9975])
B0, bu, bv, bz = toB(anchor_H), U(toB(u_H)), U(toB(v_H)), U(toB(z_H))
ray = U(toB(np.array([0, -44.7128, 64.4792])))
cross = {}
for nm, zz in (("top_face_z+3.70", 3.70), ("channel_floor_z+1.70", 1.70), ("skin_side_flange_z-2.79", -2.79)):
    lam = (zz + float(B0 @ bz)) / float(ray @ bz)   # point lam*ray with (p - B0).bz = zz
    p = lam * ray
    cross[nm] = {"b_mm": round(float((p - B0) @ bu), 2), "c_mm": round(float((p - B0) @ bv), 2), "r_from_GH": round(lam, 2),
                 "xyz": p.round(3).tolist()}
out["bottom_frame_as_built_rest"] = {
    "B0_origin": B0.round(3).tolist(), "b_axis_along_bar_toward_shoulder": bu.round(6).tolist(),
    "c_axis_across": bv.round(6).tolist(), "n_axis_away_from_arm": bz.round(6).tolist(),
    "right_handed": bool(np.allclose(np.cross(bu, bv), bz, atol=1e-3)), "landing_ray": ray.round(6).tolist(),
    "neck_ray_crossings": cross}
# BOTTOM's outer envelope (b from -20 to +25, |c| <= 15, n -2.79..3.70) vs the chain over the ranges
bb = np.arange(-20, 25.01, 1.0); cc = np.arange(-15, 15.01, 1.5); nn = np.arange(-2.79, 3.71, 1.0)
G = np.array([B0 + b * bu + c * bv + n * bz for b in bb for c in cc for n in nn])
bcol = np.array([b for b in bb for c in cc for n in nn])
per_b = {}
dl2 = np.full(len(G), np.inf); dh = np.full(len(G), np.inf); dl1 = np.full(len(G), np.inf)
for d3 in d3s:
    R = rot(J["J3"], -d3)          # link 2 seen from member 3
    dl2 = np.minimum(dl2, cKDTree(C["link2"] @ R.T).query(G)[0])
    dh = np.minimum(dh, hub_dist(G, "J3"))
    dh = np.minimum(dh, hub_dist(G @ rot(J["J3"], d3).T, "J2"))
for q2 in q2s[::3]:
    for d3 in d3s[::3]:
        R3 = rot(J["J2"], q2 - q2_rest) @ rot(J["J3"], d3)
        Gm = G @ R3.T
        dl1 = np.minimum(dl1, cKDTree(C["link1"]).query(Gm)[0])
        dh = np.minimum(dh, hub_dist(Gm, "J1"))
for b in bb:
    m = bcol == b
    per_b[str(int(b))] = {"link2": round(float(dl2[m].min()), 2), "hubs": round(float(dh[m].min()), 2), "link1": round(float(dl1[m].min()), 2)}
out["bottom_envelope_clearance_per_station_b"] = per_b
json.dump(out, open(D / "derived.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ("fk_check", "sketch_planes")}, indent=1))
print(json.dumps({k: v for k, v in sw.items() if k != "link2_to_hub1_near_fold"}, indent=1))
print(json.dumps(out["bottom_frame_as_built_rest"], indent=1))
print(json.dumps(per_b))
