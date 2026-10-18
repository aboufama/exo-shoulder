"""Desmo K-drive red team numbers (gen-9 winner desmo-conecut-knuckle-3r): loads, friction both ways, Hertz, pin / dowel
bending, press fits, wear, play stack, tolerance -> K law error, slot taper, CAD exports. Input: geo_fit.npz / .json
(extract.py: the claim's own model, BEST, fit bench). Every number in docs/research/desmo_mechanism_redteam.md comes from
results.json (this script) or fold_offset.json.
    python3 docs/research/desmo_mechanism/drive.py   -> results.json, groove_link2.csv, slot_crank.csv
"""
import json, math, os, csv
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
import sys; sys.path.insert(0, os.path.join(REPO, "tools"))
D = np.degrees; R_ = np.radians
G = dict(np.load(os.path.join(HERE, "geo_fit.npz"))); J = json.load(open(os.path.join(HERE, "geo_fit.json")))
def unit(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)
def rotm(ax, a):
    ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
def angv(a, b): return np.degrees(np.arccos(np.clip(np.einsum("ni,ni->n", unit(a), unit(b)), -1, 1)))
import importlib.util
_sp = importlib.util.spec_from_file_location("rf_x", os.path.join(REPO, "docs/concepts/models/roller-longdyad-knuckle-3r.py")) if False else None
# phi(K): the crank angle per K is the model's RF.phi_of; extract.py dumped it on kf (phi, dphi) - interpolate, never re-derive
kf, PHI, DPHI = G["kf"], G["phi"], G["dphi"]
def phi_of(k): return np.interp(k, kf, PHI)
def dphi_of(k): return np.interp(k, kf, DPHI)
PV, dR, uK, u2, F0, C0 = G["PV"], unit(G["dR"]), unit(G["uK"]), unit(G["u2"]), G["F0"], G["C0"]
sp, s_th, q_on, lim, kK = float(G["sp"]), float(G["s_th"]), float(G["q_on"]), float(G["lim"]), float(G["kK"])
bx, by, hmid = G["bx"], G["by"], float(G["hmid"])
P = J["clamped"]; MU = float(P["mu"]); MUS = (0.087, 0.12, 0.15, 0.17)
res = dict(source="extract.py fit of BEST (k57) on Bench(60,160): " + json.dumps({k: J["rod_info"].get(k) for k in ("dK_lim", "why_lim")}))
# ------------------------------------------------------------------ 0. axes / levels for the CAD
res["axes"] = dict(dR_vs_u2_deg=round(D(math.acos(abs(dR @ u2))), 2), dR_vs_uK_deg=round(D(math.acos(abs(dR @ uK))), 2), uK_vs_u2_deg=round(D(math.acos(abs(uK @ u2))), 2),
                   PV=G["PV"].round(3).tolist(), PV_along_dR=round(float(PV @ dR), 3), F0=F0.round(3).tolist(), F0_from_dR=round(float(np.linalg.norm(F0 - (F0 @ dR) * dR)), 3),
                   F0_pitch_r_from_u2=round(float(np.linalg.norm(F0 - (F0 @ u2) * u2)), 3), F0_level_u2=round(float(F0 @ u2), 3), hmid=round(hmid, 3),
                   C0=C0.round(3).tolist(), C0_R_from_GH=round(float(np.linalg.norm(C0)), 3), C0_r_from_uK=round(float(np.linalg.norm(C0 - (C0 @ uK) * uK)), 3),
                   C0_level_uK=round(float(C0 @ uK), 3), g=float(G["gg"]), kK=kK, s_th=round(s_th, 5),
                   frame="link 1b at q2 onset, K = 0 (stop A), mm from GH; all axes through GH")
# ------------------------------------------------------------------ 1. stage 2 (inverted slot): normal, levers, PA, forces
X, vN, vCx = G["X"], G["vN"], G["vCx"]; nk = len(kf); vr = vN - vCx
nB = unit(np.cross(unit(X), vr + 1e-15))
for j in range(1, nk):
    if nB[j] @ nB[j - 1] < 0: nB[j] = -nB[j]
lev2 = np.abs(np.einsum("ni,ni->n", nB, vN))                     # mm of nose normal motion per rad of K = T_K / F2
pa2h, pa2c = angv(nB, vN), angv(nB, vCx); pa2h = np.minimum(pa2h, 180 - pa2h); pa2c = np.minimum(pa2c, 180 - pa2c)
vs2 = np.linalg.norm(vr - np.einsum("ni,ni->n", vr, nB)[:, None] * nB, axis=1)
ins = kf <= lim + 1e-9
# ------------------------------------------------------------------ 2. stage 1 (pin in the BUILT blended groove)
xg, Kb, G2 = G["xg"], G["Kb"], G["G2"]
dKb = np.gradient(Kb, xg)
Cb = np.array([rotm(dR, phi_of(k)) @ F0 for k in Kb])
vpb = (dKb * dphi_of(Kb))[:, None] * np.cross(np.tile(dR, (len(xg), 1)), Cb)          # pin, per unit x (x = linear-law K)
vcb = s_th * np.cross(np.tile(u2, (len(xg), 1)), Cb)                                 # cap point, per unit x
n1 = unit(np.cross(vpb - vcb, np.tile(u2, (len(xg), 1))))
leverC = np.abs(np.einsum("ni,ni->n", n1, np.cross(np.tile(dR, (len(xg), 1)), Cb)))   # pin normal motion per rad of CRANK (mm)
mv = np.linalg.norm(vpb, axis=1) > 1e-6
pa1p = np.where(mv, angv(n1, np.where(mv[:, None], vpb, n1)), np.nan); pa1p = np.minimum(pa1p, 180 - pa1p)
pa1c = angv(n1, vcb); pa1c = np.minimum(pa1c, 180 - pa1c)
vs1 = np.linalg.norm((vpb - vcb) - np.einsum("ni,ni->n", vpb - vcb, n1)[:, None] * n1, axis=1)   # sliding per unit x
sel = (xg >= 0 - 1e-12) | (Kb > 0)
# centreline radius in link 2's ring plane (bx, by) and drift along u2
gx, gy, gz = G2 @ bx, G2 @ by, G2 @ u2 - hmid
dx, dy = np.gradient(gx), np.gradient(gy); ddx, ddy = np.gradient(dx), np.gradient(dy)
kap = (dx * ddy - dy * ddx) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); rcl = 1 / np.maximum(np.abs(kap), 1e-9)
used = Kb <= lim + 1e-9
# crank torque per N.m of K (frictionless): T_c = T_K / dphi/dK ; F1 = T_c / leverC ; F2 = T_K / lev2 ; T_J2 = T_K * dK/dq2
dphiK = np.abs(dphi_of(Kb)); dKdq = dKb / abs(s_th)
F1_perNm = np.where(used, 1000.0 / np.maximum(dphiK * leverC, 1e-9), np.nan)
F2_perNm = 1000.0 / np.maximum(lev2, 1e-9)
res["levers"] = dict(stage2_lever_mm_per_rad=[round(float(lev2[ins].min()), 3), round(float(lev2[ins].max()), 3)], stage2_lever_at_K0=round(float(lev2[0]), 3),
                     stage2_F_per_NmK=[round(float(F2_perNm[ins].min()), 1), round(float(F2_perNm[ins].max()), 1)],
                     stage1_leverC_mm=[round(float(np.nanmin(leverC[used])), 3), round(float(np.nanmax(leverC[used])), 3)],
                     stage1_F_per_NmK=[round(float(np.nanmin(F1_perNm[used])), 1), round(float(np.nanmax(F1_perNm[used])), 1)],
                     stage1_F_per_NmK_at_K=round(D(float(Kb[used][int(np.nanargmax(F1_perNm[used]))])), 2),
                     crank_T_per_NmK=[round(float(1 / np.abs(DPHI[ins]).max()), 3), round(float(1 / np.abs(DPHI[ins]).min()), 3)],
                     J2_T_per_NmK=round(kK, 4), note="F in N per N.m of torque about uK at K (frictionless, both directions)")
res["pa"] = dict(stage2_horn=[round(float(pa2h[ins].min()), 2), round(float(pa2h[ins].max()), 2)], stage2_crank=[round(float(pa2c[ins].min()), 2), round(float(pa2c[ins].max()), 2)],
                 stage1_pin_moving_max_to_lim=round(float(np.nanmax(np.where(used & (Kb > 0), pa1p, np.nan))), 2),
                 stage1_cap_outside_blend_max=round(float(pa1c[used & (dKb > 0.999)].max()), 2))
# ------------------------------------------------------------------ 3. friction: efficiency both power-flow directions, per stage, true lock
def eff(vd, vn, n, mu):
    """driver point velocity vd, driven point velocity vn, contact normal n (sign free) -> efficiency (<= 0: locked)"""
    s = vn - vd; s = s - np.einsum("ni,ni->n", s, n)[:, None] * n; sn = np.linalg.norm(s, axis=1); s_ = s / np.maximum(sn, 1e-12)[:, None]
    sg = np.sign(np.einsum("ni,ni->n", n, vd)); sg[sg == 0] = 1; n_ = n * sg[:, None]
    fin = np.einsum("ni,ni->n", n_, vd) - mu * np.einsum("ni,ni->n", s_, vd); fout = np.einsum("ni,ni->n", n_, vn) - mu * np.einsum("ni,ni->n", s_, vn)
    return np.where(fin > 1e-9, fout / np.maximum(fin, 1e-9), -1.0)
fr = {}
for mu in MUS:
    e1f = eff(vcb, vpb, n1, mu); e1b = eff(vpb, vcb, n1, mu)                     # stage 1: cap drives pin (J2 -> K) / pin drives cap (K -> J2)
    e2f = eff(vCx, vN, nB, mu); e2b = eff(vN, vCx, nB, mu)                      # stage 2: crank (slot) drives nose / nose drives slot
    moving = used & (dKb > 1e-3)
    Kd = D(1) * Kb
    lock1b = moving & (e1b <= 0)
    rule1f = used & (Kb > 0) & (pa1p + D(math.atan(mu)) > 43.0 + 1e-9)
    fr["%.3f" % mu] = dict(stage1_fwd_eta_min_to_lim=round(float(e1f[moving].min()), 3), stage1_fwd_eta_at_held_46_27=round(float(np.interp(R_(46.27), Kb[moving], e1f[moving])), 3),
                           stage1_back_eta_min_moving=round(float(e1b[moving].min()), 3),
                           stage1_back_locked_K_deg=[round(float(Kd[lock1b].min()), 2), round(float(Kd[lock1b].max()), 2)] if lock1b.any() else None,
                           stage1_rule43_first_K=round(float(Kd[rule1f][0]), 2) if rule1f.any() else None,
                           stage2_fwd_eta=[round(float(e2f[ins].min()), 3), round(float(e2f[ins].max()), 3)], stage2_back_eta=[round(float(e2b[ins][1:].min()), 3), round(float(e2b[ins][1:].max()), 3)],
                           overall_fwd_eta_at_46_27=round(float(np.interp(R_(46.27), Kb[moving], e1f[moving]) * np.interp(R_(46.27), kf, e2f)), 3))
res["friction"] = fr
res["friction_note"] = ("eta = output / input power through one sliding pair (normal + mu x sliding): fwd = J2 drives K (cap -> pin, slot -> nose), "
                        "back = the K load drives J2 (nose -> slot, pin -> cap); eta <= 0 is a true self-lock. stage1_rule43 = the family's design "
                        "rule PA + atan(mu) <= 43 on the pin side (the verifier's 'bind'), not a jam.")
# ------------------------------------------------------------------ 4. a manufactured pin-hole error: K law error on the NOMINAL groove
def law_err(F0e, xs):
    out = []
    P2 = np.c_[gx, gy]; seg0, seg1 = P2[:-1], P2[1:]
    for x in xs:
        k0 = float(np.interp(x, xg, Kb)); q = q_on + s_th * x; Rq = rotm(u2, -(q - q_on))
        def sd(ph):
            c = Rq @ (rotm(dR, ph) @ F0e); p = np.array([c @ bx, c @ by]); d = seg1 - seg0
            t = np.clip(np.einsum("ni,ni->n", p - seg0, d) / np.einsum("ni,ni->n", d, d), 0, 1); Q = seg0 + t[:, None] * d; j = int(np.argmin(np.linalg.norm(Q - p, axis=1)))
            nrm = np.array([-d[j, 1], d[j, 0]]); return float((p - Q[j]) @ nrm / np.linalg.norm(nrm))
        p0 = float(phi_of(k0)); a, b = p0 - R_(3), p0 + R_(3); fa = sd(a); fb = sd(b)
        if fa * fb > 0: out.append(np.nan); continue
        for _ in range(50):
            m = (a + b) / 2; fm = sd(m)
            if fa * fm <= 0: b, fb = m, fm
            else: a, fa = m, fm
        phe = (a + b) / 2; ke = float(np.interp(phe, PHI, kf)) if PHI[-1] > PHI[0] else float(np.interp(-phe, -PHI, kf))
        out.append(D(ke - k0))
    return np.array(out)
e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1)
psi0, as0 = R_(float(P["psi"])), float(P["a_s"]); s0 = float(G["s0"])
def F0_of(a_s, psi):
    v = math.cos(psi) * e1 + math.sin(psi) * e2; return s0 * dR + a_s * v
chk = np.linalg.norm(F0_of(as0, psi0) - F0)
xs = R_(np.array([2.0, 6.0, 15.0, 25.0, 35.0, 42.0, 44.0, 45.62, 46.27]))
tol = {"F0 rebuild check mm": round(float(chk), 6)}
for lab, (da, dp) in {"a_s +0.01": (0.01, 0), "a_s -0.01": (-0.01, 0), "psi +0.06 deg (0.01 mm at 9.5)": (0, 0.06)}.items():
    tol[lab] = np.round(law_err(F0_of(as0 + da, psi0 + R_(dp)), xs), 4).tolist()
tol["x_deg"] = np.round(D(1) * xs, 2).tolist()
# groove profile error 0.01 normal -> K: dK = 0.01 / (dphi * leverC) ; slot profile 0.01 -> 0.01 / lev2
tol["groove_profile_10um_deg_K"] = [round(float(D(0.01 / np.nanmax((dphiK * leverC)[used & (Kb > 0)]))), 4), round(float(D(0.01 / np.nanmin((dphiK * leverC)[used & (Kb > R_(1))]))), 4)]
tol["slot_profile_10um_deg_K"] = [round(float(D(0.01 / lev2[ins].max())), 4), round(float(D(0.01 / lev2[ins & (kf > R_(1))].min())), 4)]
res["tolerance_to_K"] = tol
# ------------------------------------------------------------------ 5. slot: radial rulings (the nose axis is radial through GH) vs a straight extrude
Zs = G["Z"][ins]; L = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Zs, axis=0), axis=1))]
zr = unit(Zs); zmean = unit(zr.mean(0))
taper = np.degrees(np.arccos(np.clip(zr @ zmean, -1, 1)))
plate_t = 2.5; half = plate_t / 2
dev = np.tan(R_(taper)) * half                                          # ruling end offset vs a straight extrude along the mean ruling
# in-plane curvature of the slot centreline (on the sphere R0): project to the plane normal to zmean
e_a = unit(np.cross(zmean, dR)); e_b = np.cross(zmean, e_a); sx, sy = Zs @ e_a, Zs @ e_b
sr = np.arange(0, L[-1], 0.05); Pr = np.c_[[np.interp(sr, L, Zs[:, i]) for i in range(3)]].T          # arc-length resample (the pole crowds the K grid)
rx, ry = Pr @ e_a, Pr @ e_b; ddx_, ddy_ = np.gradient(rx, sr), np.gradient(ry, sr); d2x, d2y = np.gradient(ddx_, sr), np.gradient(ddy_, sr)
kp2 = (ddx_ * d2y - ddy_ * d2x) / np.maximum((ddx_ ** 2 + ddy_ ** 2) ** 1.5, 1e-12); rc2 = 1 / np.maximum(np.abs(kp2), 1e-9)
res["slot"] = dict(length_mm=round(float(L[-1]), 3), ruling_taper_deg=[round(float(taper.min()), 3), round(float(taper.max()), 3)],
                   straight_extrude_end_dev_um=round(1000 * float(dev.max()), 1), centreline_radius_mm=[round(float(rc2[2:-2].min()), 2), round(float(np.median(rc2)), 1)],
                   inner_wall_radius_min_mm=round(float(rc2[2:-2].min()) - 0.76, 2), R0_mm=round(float(G["R0"]), 3),
                   note="the nose's axis is radial through GH; the slot walls are offsets of a ruled surface of radial lines (converging on GH). "
                        "A straight 2-axis extrude along the mean ruling leaves the wall off by up to this at the plate faces")
# ------------------------------------------------------------------ 6. Hertz (440C on Ti-6Al-4V / on 440C insert)
E_ST, NU_ST, E_TI, NU_TI = 200e3, 0.28, 114e3, 0.34
def estar(E1, n1_, E2, n2_): return 1 / ((1 - n1_ ** 2) / E1 + (1 - n2_ ** 2) / E2)
def hertz_pt(F, Rx, Ry, Es):
    """Hamrock-Brewe elliptical point contact: Rx, Ry effective radii (mm, positive = conforming sum >0) -> p0 MPa, a, b mm"""
    if Ry < Rx: Rx, Ry = Ry, Rx
    k = 1.0339 * (Ry / Rx) ** 0.636; Ek = 1.0003 + 0.5968 * Rx / Ry; R = 1 / (1 / Rx + 1 / Ry)
    a = (6 * k ** 2 * Ek * F * R / (math.pi * Es)) ** (1 / 3); b = (6 * Ek * F * R / (math.pi * k * Es)) ** (1 / 3)
    return 3 * F / (2 * math.pi * a * b), a, b
def hertz_line(F, Lc, Req, Es):
    w = F / Lc; p0 = math.sqrt(w * Es / (math.pi * Req)); return p0, 2 * w / (math.pi * p0)
RP = 0.75; RCR = 4.0                                                      # pin radius; crown radius (axial) - chosen below
def req_inplane(rwall, convex): return 1 / (1 / RP + 1 / rwall) if convex else (1 / (1 / RP - 1 / rwall) if rwall > RP else math.inf)
rc_used = rcl[used & sel]; Kd_used = D(1) * Kb[used & sel]
rc_min = float(rc_used.min()); K_at_rcmin = float(Kd_used[int(np.argmin(rc_used))])
res["groove_radius"] = dict(centreline_min_mm=round(rc_min, 3), at_K_deg=round(K_at_rcmin, 2), inner_wall_min_mm=round(rc_min - 0.76, 3),
                           centreline_radius_at_K=[(round(float(k), 1), round(float(np.interp(R_(k), Kb[used & sel], rcl[used & sel])), 2)) for k in (0.5, 1, 2, 3, 5, 8, 11, 15, 25, 35, 46)],
                           drift_mm=[round(float(gz[used].min()), 3), round(float(gz[used].max()), 3)])
CASES = [("nominal motion (judge drive torque peak, gen-8 CAD, mu_roll 0.005)", 0.034), ("upper in-motion bound (spring design: 0.08 + 0.015 x 0.81 + 0.034)", 0.126),
         ("felt line: 1 N.m at GH, all of it about uK", 1.0), ("cuff slip, fabric liner at strap preload", 1.06), ("cuff slip, mu 0.5 at 14 kPa", 2.28), ("lock line 10 N.m at GH x 0.84", 8.4)]
Es_ti, Es_st = estar(E_ST, NU_ST, E_TI, NU_TI), estar(E_ST, NU_ST, E_ST, NU_ST)
F1max = float(np.nanmax(F1_perNm[used])); F2max = float(F2_perNm[ins].max())
# where is stage 1 loaded hardest, and on which wall radius
jF1 = int(np.nanargmax(np.where(used, F1_perNm, -1))); K_F1 = D(float(Kb[jF1])); rc_F1 = float(rcl[jF1])
# rest-region (K 0-11, the blend: the ridge) force per N.m
blend = used & (Kb <= R_(11.0)) & (Kb > 0); F1_blend = float(np.nanmax(F1_perNm[blend])) if blend.any() else np.nan
rows = []
for lab, T in CASES:
    F1, F2 = F1max * T, F2max * T; Fb = F1_blend * T
    p_ridge_ti = hertz_pt(Fb, req_inplane(rc_min - 0.76, True), RCR, Es_ti)[0]
    p_ridge_st = hertz_pt(Fb, req_inplane(rc_min - 0.76, True), RCR, Es_st)[0]
    p_outer_ti = hertz_pt(F1, req_inplane(rc_F1 + 0.76, False), RCR, Es_ti)[0]
    p_inner_ti = hertz_pt(F1, req_inplane(max(rc_F1 - 0.76, 0.05), True), RCR, Es_ti)[0]
    p_inner_st = hertz_pt(F1, req_inplane(max(rc_F1 - 0.76, 0.05), True), RCR, Es_st)[0]
    r2w = float(rc2[2:-2].min()) - 0.76
    p2_ti = hertz_line(F2, 2.2, req_inplane(max(r2w, 0.05), True), Es_ti)[0]; p2_st = hertz_line(F2, 2.2, req_inplane(max(r2w, 0.05), True), Es_st)[0]
    # dowel (O1.5, 440C) bending at the boss face: arm 0.15 gap + 2.5/2 into the plate; stage-1 pin: arm 1.0 (load at mid groove depth)
    Zb = math.pi * 1.5 ** 3 / 32; sb2 = F2 * (0.15 + 1.25) / Zb; tau2 = 4 * F2 / (math.pi * 1.5 ** 2); sb1 = F1 * 1.0 / Zb
    rows.append(dict(case=lab, T_K_Nm=T, T_J2_Nm=round(T * kK, 3), crank_T_Nm=round(T / float(np.abs(DPHI[ins]).min()), 3), F_stage1_max_N=round(F1, 1), at_K=round(K_F1, 1),
                     F_stage1_blend_N=round(Fb, 1), F_stage2_max_N=round(F2, 1),
                     p0_ridge_Ti_MPa=round(p_ridge_ti), p0_ridge_440C_MPa=round(p_ridge_st), p0_stage1_worstF_outer_Ti=round(p_outer_ti), p0_stage1_worstF_inner_Ti=round(p_inner_ti),
                     p0_stage1_worstF_inner_440C=round(p_inner_st), p0_stage2_Ti=round(p2_ti), p0_stage2_440C=round(p2_st),
                     dowel_bend_MPa=round(sb2), dowel_shear_MPa=round(tau2), pin1_bend_MPa=round(sb1)))
res["loads"] = rows
res["loads_note"] = (f"stage-1 pin crowned R {RCR} axial; ridge = the blend's inner-wall radius {rc_min - 0.76:.3f} mm (convex); stage 2 line 2.2 mm "
                     "(2.5 plate minus 0.15 chamfers); allowables: 440C (58 HRC) bending ~1.9 GPa, shear ~1.1 GPa; Hertz p0 limits: Ti-6Al-4V "
                     "(sigma_y 830-880) onset of subsurface yield p0 ~ 1.6 sigma_y / ... point contact ~1.4 GPa (0.62 tau), hardened 440C ~3.5-4.0 GPa static")
res["stop_B_slot_end"] = dict(F_per_NmK=round(1000 / float(np.linalg.norm(vN[ins][-1])), 1), lever_mm=round(float(np.linalg.norm(vN[ins][-1])), 2),
                              note="the slot's far end stops the nose along its path: F = T_K / |vN|; and it also stops J2 through stage 1 (the pin carries T_J2 / lever)")
# ------------------------------------------------------------------ 7. press fit of the O1.5 dowel in the Ti boss (O5 x 3) and of the pin in the crank arm
def press(delta_dia, d=1.5, Do=5.0, Lf=3.0, mu=0.2, Eh=E_TI, nuh=NU_TI, Es=E_ST, nus=NU_ST):
    a, c = d / 2, Do / 2; dr = delta_dia / 2
    p = dr / (a / Eh * ((c ** 2 + a ** 2) / (c ** 2 - a ** 2) + nuh) + a / Es * (1 - nus))
    hoop = p * (c ** 2 + a ** 2) / (c ** 2 - a ** 2); return round(p), round(hoop), round(mu * p * math.pi * d * Lf, 1)
res["press_fit"] = {f"{int(i * 1000)}um": press(i) for i in (0.002, 0.005, 0.008, 0.013)}
res["press_fit_note"] = "(contact MPa, hoop MPa in the O5 boss, pull-out N at mu 0.2, 3 mm engagement); ream 1.500 -0.005/0 vs m6 1.502-1.508 -> 2-13 um"
# ------------------------------------------------------------------ 8. wear (Archard) over 1e6 full strokes x 2 passes at the in-motion upper load
st = used & (Kb > 0)
S1 = float(np.trapz(vs1[st], xg[st])); S2 = float(np.trapz(vs2[ins], kf[ins]))
# contact travel on the groove wall (link 2) and on the pin (pin pressed, the normal turns in the crank frame)
Lw1 = float(np.sum(np.linalg.norm(np.diff(G2[st], axis=0), axis=1)))
ncr = np.array([rotm(dR, -phi_of(k)) @ n for k, n in zip(Kb[st], n1[st])]); ang_pin = float(np.ptp(np.unwrap(np.arctan2(ncr @ np.cross(dR, e1), ncr @ e1))))
wear = {}
for lab, T in (("in-motion upper 0.126 N.m", 0.126), ("nominal 0.034 N.m", 0.034)):
    F1m, F2m = F1max * T, F2max * T
    for kname, kw in (("greased DLC / 440C insert (1e-8)", 1e-8), ("dry steel-steel (1e-7)", 1e-7), ("Ti bare vs 440C (galling, 1e-5)", 1e-5)):
        V1 = kw * F1m * S1 / 1000 * 2e6; V2 = kw * F2m * S2 / 1000 * 2e6         # mm3 (k in mm3/(N.m))
        h_w1 = V1 / (1.5 * Lw1); h_p1 = V1 / (1.5 * max(RP * ang_pin, 0.05)); h_w2 = V2 / (2.2 * float(L[-1])); h_p2 = V2 / (2.2 * 0.3)
        wear[f"{lab} | {kname}"] = dict(groove_wall_um=round(1000 * h_w1, 2), pin_um=round(1000 * h_p1, 2), slot_wall_um=round(1000 * h_w2, 2), dowel_um=round(1000 * h_p2, 2))
res["wear"] = dict(sliding_per_stroke_mm=dict(stage1=round(S1, 3), stage2=round(S2, 3)), groove_travel_mm=round(Lw1, 2), pin_normal_turn_deg=round(D(ang_pin), 1), cases=wear,
                   note="1e6 strokes x 2 passes; worst-case: wear spread over the groove wall length x 1.5 depth, over the pin's turning arc, over the slot length x 2.2 and a 0.3 mm dowel arc")
# ------------------------------------------------------------------ 9. play stack (one-sided, deg of K): slope from the model's nominal c 0.01
fs = J["rod_info"]["desmo"]["slop"]; free_nom = float(fs["crank_free"]["max_deg"]); slot_nom = float(fs["slotB"]["slop_max"])
DENSE = 0.187                                                   # verifier's dense crank-free scan (211 rows) at c 0.01
def stack(c1, c2, brg_um=0.0):
    b = D(brg_um / 1000 / np.nanmin((dphiK * leverC)[used & (Kb > R_(1))])) if brg_um else 0.0
    return round(DENSE * c1 / 0.01 + slot_nom * c2 / 0.01 + b, 3)
res["play"] = dict(model_crank_free_c010=free_nom, verifier_dense_c010=DENSE, slot_held_c010=slot_nom,
                   nominal_model_c=stack(0.01, 0.01), worst_model_c015=stack(0.015, 0.015),
                   wire_EDM_insert_nom=stack(0.010, 0.0075), wire_EDM_insert_worst=stack(0.0125, 0.0105), wire_EDM_insert_best=stack(0.0075, 0.0045),
                   milled_Ti_groove_worst=stack(0.020, 0.0105), with_unpreloaded_crank_pair_10um=stack(0.0125, 0.0105, 10.0),
                   note="groove c1 = (slot width - pin d) / 2; wire EDM 1.520 +-0.003 vs ground pin 1.500 +-0.002 -> 0.0075-0.0125; slot c2 vs m6 dowel 1.502-1.508 -> 0.0045-0.0105")
# metal shift at the cuff end of the chain from a K offset (rigid rotation about uK of everything distal, before re-closure)
res["metal_shift_per_0p25deg_K_mm"] = dict(at_R60=round(60 * R_(0.25), 3), at_R80=round(80 * R_(0.25), 3))
json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
# ------------------------------------------------------------------ exports
with open(os.path.join(HERE, "groove_link2.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["x_lawK_deg", "K_built_deg", "gx", "gy", "gz_drift", "centreline_r_mm", "pa_pin_deg", "pa_cap_deg", "F_stage1_N_per_NmK"])
    for j in np.nonzero(used)[0][::4]:
        w.writerow([round(D(float(xg[j])), 3), round(D(float(Kb[j])), 3), round(float(gx[j]), 4), round(float(gy[j]), 4), round(float(gz[j]), 4), round(float(rcl[j]), 3),
                    round(float(pa1p[j]), 2) if np.isfinite(pa1p[j]) else "", round(float(pa1c[j]), 2), round(float(F1_perNm[j]), 1)])
with open(os.path.join(HERE, "slot_crank.csv"), "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["K_deg", "Zx", "Zy", "Zz", "s_mm", "sx_plane", "sy_plane", "pa_horn", "pa_crank", "F_stage2_N_per_NmK"])
    for j in range(0, int(ins.sum()), 5):
        w.writerow([round(D(float(kf[j])), 2)] + [round(float(v), 4) for v in Zs[j]] + [round(float(L[j]), 4), round(float(sx[j]), 4), round(float(sy[j]), 4), round(float(pa2h[j]), 2), round(float(pa2c[j]), 2), round(float(F2_perNm[j]), 1)])
print(json.dumps({k: res[k] for k in ("levers", "pa", "friction", "slot", "groove_radius", "play", "tolerance_to_K")}, default=float, indent=0)[:6000])
print(json.dumps(res["loads"], default=float)[:3000]); print(json.dumps(res["wear"], default=float)[:1500]); print(res["press_fit"], res["stop_B_slot_end"])
