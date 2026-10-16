"""Sidecar drive red team on the extracted geometry (extract.py -> geo_*.npz): RSSR stroke table, KBRM-02 eye clearance to hub K,
ball-link tilt, the REAL follower + lobe (exact spatial cam, roller on a short arm of the bell crank), loads / stresses,
play -> K error, K offset -> fold margin. Writes results_<tag>.json, lobe_polar_<tag>.csv, spec_points_<tag>.json.

    python3 docs/research/sidecar_mechanism/drive.py geo_rh155.npz rh155
"""
import json, math, os, sys
import numpy as np
SP = os.path.dirname(os.path.abspath(__file__))
Z = np.load(os.path.join(SP, sys.argv[1])); g = {k: Z[k] for k in Z.files}; TAG = sys.argv[2]
D, R_ = math.degrees, math.radians
def unit(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)
def rotm(ax, a):
    ax = ax / np.linalg.norm(ax); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]]); return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
u1, u2, u3, uK, dR = g["u1"], g["u2"], g["u3"], g["uK"], g["dR"]
f = g["f"]; f2 = float(f[1]); fK = float(g["fK"]); PV, tip0, H0 = g["PV"], g["tip0"], g["H0"]; sp = float(g["sp"])
HUB_R, UP, T_LINK, CROWN, RUN, W_LINK, bk1, bk2, a1max, kK, r_h, La, s_arm, r_lobe, hl, beta = [float(x) for x in g["consts"]]
kgrid, phig = g["kgrid"], g["phig"]; dK_lim = float(g["dK_lim"]); t_lim = dK_lim / kK
q2hi = float(g["q2hi"]); tk = g["taken"]; st = g["kstate"]; drv = tk & (st == 1)
dK_tk = float(np.abs(g["dK"][tk]).max())
res = dict(tag=TAG, r_h=r_h, f2=f2, fK=fK, dR_to_u2_deg=round(D(math.acos(dR @ u2)), 2), uK_to_u2_deg=round(D(math.acos(uK @ u2)), 2),
           pivot_from_u2_axis_mm=round(float(np.linalg.norm(PV - (PV @ u2) * u2)), 2), boss_underside_along_dR=round(float(np.linalg.norm(PV)), 2),
           dK_lim_deg=round(D(dK_lim), 2), dK_taken_max_deg=round(D(dK_tk), 2), t_lim_deg=round(D(t_lim), 2), q2_stopB_deg=round(D(q2hi - t_lim), 3),
           q2_onset_deg=round(D(q2hi), 3), rod_len=round(float(np.linalg.norm(H0 - tip0)), 3))
# ---------------- RSSR stroke table (link 1b frame) ----------------
kk = np.radians(np.arange(0, D(dK_lim) + 1e-6, 0.5)); ph = np.interp(kk, kgrid, phig)
tips = np.array([rotm(dR, p) @ tip0 for p in ph]); Hs = np.array([rotm(uK, sp * k).T @ H0 for k in kk])
rod = unit(Hs - tips); Lr = np.linalg.norm(Hs - tips, axis=1)
m_h = np.abs(np.einsum("ni,i->n", np.cross(Hs, rod), uK)); m_c = np.abs(np.einsum("ni,i->n", np.cross(tips, rod), dR))
tilt_c = np.degrees(np.arcsin(np.abs(rod @ dR))); tilt_h = np.degrees(np.arcsin(np.abs(rod @ uK)))
ratio = np.gradient(ph, kk)
res["rssr"] = dict(closure_err_mm=round(float(np.abs(Lr - Lr[0]).max()), 4), phi_end_deg=round(D(float(ph[-1])), 2),
                   ratio_dphi_ddK=[round(float(np.abs(ratio).min()), 3), round(float(np.abs(ratio).max()), 3)],
                   horn_arm_mm=[round(float(m_h.min()), 2), round(float(m_h.max()), 2)], crank_arm_mm=[round(float(m_c.min()), 2), round(float(m_c.max()), 2)],
                   tilt_crank_deg=[round(float(tilt_c.min()), 1), round(float(tilt_c.max()), 1)], tilt_horn_deg=[round(float(tilt_h.min()), 1), round(float(tilt_h.max()), 1)],
                   rod_sense="push (compression) when K opens" if np.linalg.norm(Hs[5] - tips[0]) < Lr[0] else "see table")
# ---------------- KBRM-02 eye (O9 x 4 head, O4.6 shank, h1 12.5) vs hub K / hub 2 over the drive range ----------------
def eye_pts(c, r_hat, stud, R=4.5, C1=4.0):
    nh = unit(stud - (stud @ r_hat) * r_hat); e2 = np.cross(nh, r_hat); a = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    ring = c + R * (np.cos(a)[:, None] * r_hat + np.sin(a)[:, None] * e2)
    return np.concatenate([ring + w * nh for w in (-C1 / 2, 0, C1 / 2)])
def shank_pts(c, r_hat, toward=1, R=2.3, L0=4.5, L1=12.5):
    nh = unit(np.cross(r_hat, [0.3, 0.5, 0.8])); e2 = np.cross(r_hat, nh); a = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    return np.concatenate([c + toward * s * r_hat + R * (np.cos(a)[:, None] * nh + np.sin(a)[:, None] * e2) for s in np.linspace(L0, L1, 9)])
def cyl_clear(X, ax, lo, hi, r):
    h = X @ ax; rr = np.linalg.norm(X - h[:, None] * ax, axis=1); inside = (h > lo) & (h < hi)
    return float((rr[inside] - r).min()) if inside.any() else 99.0
cl = dict(eyeH_hubK=[], eyeT_hub2=[], shankH_hubK=[], rodmid_hubK=[], rodmid_hub2=[], eyeH_low_vs_horn_top=[])
for j in range(len(kk)):
    eH = eye_pts(Hs[j], -rod[j], uK); eT = eye_pts(tips[j], rod[j], rotm(dR, ph[j]) @ dR)
    cl["eyeH_hubK"].append(cyl_clear(eH, uK, fK - 1, fK + CROWN, HUB_R)); cl["eyeT_hub2"].append(cyl_clear(eT, u2, f2 - 1, f2 + CROWN, HUB_R))
    sH = shank_pts(Hs[j], -rod[j]); cl["shankH_hubK"].append(cyl_clear(sH, uK, fK - 1, fK + CROWN, HUB_R))
    mid = tips[j][None] + np.linspace(0.3, 0.7, 9)[:, None] * (Hs[j] - tips[j])[None]
    cl["rodmid_hubK"].append(cyl_clear(mid, uK, fK - 1, fK + CROWN, HUB_R + 1.0)); cl["rodmid_hub2"].append(cyl_clear(mid, u2, f2 - 1, f2 + CROWN, HUB_R + 1.0))
    cl["eyeH_low_vs_horn_top"].append(float((eH @ uK).min() - (fK + hl + T_LINK)))
res["kbrm02_clear_mm"] = {k: round(float(np.min(v)), 2) for k, v in cl.items()}
res["kbrm02_clear_note"] = "eye = O9 x 4 head (KBRM-02 d2 9, C1 4), shank O4.6; rod mid = O2 stud (+1 mm r); horn top = fK + hl + T_LINK; ball centre 3 mm over the lug top (model ZB)"
# ---------------- follower + lobe (exact spatial cam) ----------------
ts = np.radians(np.linspace(0, D(t_lim), 121)); phs = np.interp(kK * ts, kgrid, phig)
def follower(a_s, psi, rr, hmid, ruling="mean"):
    # roller centre at u2-level hmid, a_s from the dR axis, azimuth psi about dR (e1 = unit(u2 - (u2.dR) dR) toward hub 2)
    e1 = unit(u2 - (u2 @ dR) * dR); e1 = -e1; e2 = np.cross(dR, e1)
    v = math.cos(psi) * e1 + math.sin(psi) * e2; s = (hmid - a_s * (v @ u2)) / (dR @ u2); C0 = s * dR + a_s * v
    C = np.array([rotm(dR, p) @ C0 for p in phs])                      # link 1b frame
    C2 = np.array([rotm(u2, t) @ c for c, t in zip(C, ts)])             # lobe (link 2) frame, onset reference (q2 = q2hi - t)
    z = C2 @ u2; xy = C2 - z[:, None] * u2; rho = np.linalg.norm(xy, axis=1)
    T2 = np.gradient(C2, ts, axis=0); Tb = np.array([rotm(u2, -t) @ v_ for v_, t in zip(T2, ts)])   # pitch tangent in 1b frame
    rul = dR if ruling == "roller" else u2
    n = unit(np.cross(Tb, rul)); vf = np.gradient(C, ts, axis=0)
    pa = np.degrees(np.arccos(np.clip(np.abs(np.einsum("ni,ni->n", n, unit(vf))), 0, 1)))
    # planar curvature of the pitch curve (projection on the lobe plane)
    bx = unit(xy[0]); by = np.cross(u2, bx); x, y = xy @ bx, xy @ by
    dx, dy = np.gradient(x, ts), np.gradient(y, ts); ddx, ddy = np.gradient(dx, ts), np.gradient(dy, ts)
    kap = (dx * ddy - dy * ddx) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); rc = 1 / np.where(np.abs(kap) < 1e-9, 1e-9, kap)
    return dict(C0=C0, C=C, C2=C2, rho=rho, z=z, pa=pa, rc=rc, n=n, x=x, y=y, bx=bx, by=by, s=s)
hmid = f2 + 7.45; d_lvl = float(hmid * math.tan(math.acos(dR @ u2)))
best = []
for rr, part in ((3.0, "MR63ZZ (3x6x2.5) on an O3 pin"), (2.5, "IKO CFS2.5 stud cam follower (O5 x 3)")):
    for a_s in np.arange(5.5, 9.01, 0.5):
        for psi in np.radians(np.arange(0, 360, 3)):
            F = follower(a_s, psi, rr, hmid)
            dwell = F["rho"][0] - rr - 0.1; nose = float(F["rho"].max() - rr)
            if not (10.1 <= dwell <= 10.8): continue
            if a_s < 3.0 + rr + 0.3: continue                              # roller clear of the O6 crank neck
            if nose > d_lvl - 3.0 - 0.5: continue                          # nose sweeps past the O6 neck on the whole J2 range
            if float(np.abs(F["z"] - F["z"][0]).max()) > 0.6: continue     # roller stays on the 3 mm lobe band
            rcp = F["rc"] - rr * np.sign(F["rc"]); conv_ok = np.all((F["rc"] < 0) & (np.abs(F["rc"]) > rr + 0.5) | (F["rc"] > rr + 0.8))
            if not conv_ok: continue
            best.append((float(F["pa"].max()), rr, part, round(float(a_s), 2), round(D(psi), 1), round(dwell, 2), round(nose, 2),
                         round(float(np.abs(F["z"] - F["z"][0]).max()), 2), round(float(np.min(np.abs(F["rc"]))), 2)))
best.sort(key=lambda r: (r[0] > 38.0, -r[1], r[0]))
res["follower_neck_level_d_mm"] = round(d_lvl, 2)
res["follower_options"] = [dict(pa_max=round(b[0], 1), rr=b[1], part=b[2], a_s=b[3], psi=b[4], dwell_r=b[5], nose_r=b[6], drift=b[7], rc_min=b[8]) for b in best[:12]]
res["follower_n_feasible"] = len(best)
json.dump(res, open(os.path.join(SP, f"results_{TAG}.json"), "w"), indent=1, default=float)
print(json.dumps(res, indent=1, default=float))
# ---------------- stage 2: the chosen follower, loads, play, fold sensitivity ----------------
A_S, PSI, RR = float(os.environ.get("A_S", 6.0)), R_(float(os.environ.get("PSI", 201.0))), float(os.environ.get("RR", 2.5))
F = follower(A_S, PSI, RR, hmid); n = F["n"]; C = F["C"]
kks = kK * ts; mh_t = np.interp(kks, kk, m_h); mc_t = np.interp(kks, kk, m_c); rat_t = np.interp(kks, kk, np.abs(ratio))
m_f = np.abs(np.einsum("ni,i->n", np.cross(C, n), dR)); m_2 = np.abs(np.einsum("ni,i->n", np.cross(C, n), u2))
def hertz_line(Fn, R1, R2, l, E=200e3, nu=0.29):
    Es = E / (2 * (1 - nu ** 2)); R = 1 / (1 / R1 + 1 / R2); return math.sqrt(Fn * Es / (math.pi * l * R))
loads = {}
for case, T0 in (("spring 0.08 N.m + 0.015 N.m/rad", 0.08), ("spring + MVP1 0.033 N.m", 0.113), ("low preload 0.05 + MVP1", 0.083)):
    TK = T0 + 0.015 * kks
    Frod = TK / (mh_t / 1000); Tc = Frod * mc_t / 1000; Fn = Tc / (m_f / 1000); TJ2 = Fn * m_2 / 1000
    Rl = np.abs(F["rc"]) - RR
    ph_ = [hertz_line(fn, RR, rl, 2.2) for fn, rl in zip(Fn, Rl)]
    lever_pin = 3.0 + 0.6 + 0.0                                         # horn stud: ball centre over the lug top (+0.6 spacer)
    loads[case] = dict(F_rod_N=[round(float(Frod.min()), 1), round(float(Frod.max()), 1)], crank_torque_Nmm=round(float(Tc.max() * 1000), 1),
                       F_follower_N=[round(float(Fn.min()), 1), round(float(Fn.max()), 1)], J2_torque_Nm=[round(float(TJ2.min()), 3), round(float(TJ2.max()), 3)],
                       J2_virtual_work_check_Nm=[round(float((TK * kK).min()), 3), round(float((TK * kK).max()), 3)],
                       hertz_roller_lobe_MPa=round(float(max(ph_)), 0), horn_pin_O2_MPa=round(32 * float(Frod.max()) * lever_pin / (math.pi * 2 ** 3), 0),
                       crank_long_arm_root_MPa=round(6 * float(Tc.max() * 1000) / (3 * 6 ** 2), 0),
                       roller_pin_O25_MPa=round(32 * float(Fn.max()) * 1.75 / (math.pi * 2.5 ** 3), 0),
                       crank_pin_O3_root_MPa=round(32 * float(np.hypot(Frod.max() * 4.0, Fn.max() * 7.5)) / (math.pi * 3 ** 3), 0))
res["follower_chosen"] = dict(a_s=A_S, psi_deg=D(PSI), rr=RR, pa_deg=[round(float(F["pa"].min()), 1), round(float(F["pa"].max()), 1)],
                              pitch_r=[round(float(F["rho"].min()), 2), round(float(F["rho"].max()), 2)], profile_r=[round(float(F["rho"].min() - RR), 2), round(float(F["rho"].max() - RR), 2)],
                              m_f_mm=[round(float(m_f.min()), 2), round(float(m_f.max()), 2)], drift_mm=round(float(np.abs(F["z"] - F["z"][0]).max()), 2),
                              pitch_rc_min=round(float(np.abs(F["rc"]).min()), 2), roller_centre_onset=[round(float(x), 3) for x in F["C0"]], s_on_dR=round(F["s"], 2))
res["loads"] = loads
# play -> K error (deg) per 10 um at the three interfaces (one-sided under the spring preload: a clearance is a constant offset, trimmed)
res["K_error_deg_per_10um"] = dict(rod_length=[round(D(0.01 / float(mh_t.max())), 3), round(D(0.01 / float(mh_t.min())), 3)],
                                   roller_or_lobe_form=[round(D(0.01 / float(m_f.max()) / float(rat_t.max())), 3), round(D(0.01 / float(m_f.min()) / float(rat_t.min())), 3)],
                                   crank_tip_eye=[round(D(0.01 / float(mc_t.max()) / float(rat_t.max())), 3), round(D(0.01 / float(mc_t.min()) / float(rat_t.min())), 3)])
# fold margin vs a K offset (the one th metric; the law's own curves)
a2 = float(g["a2"]); ts_l = g["law_ts"]; dKl = g["law_dK"]; q2t = g["law_q2t"]
def law_m(off):
    dk = dKl + sp * R_(off) * (ts_l > 0); th = []; a1e = []
    for q, k in zip(q2t, dk):
        RK = rotm(uK, k); th.append(D(math.acos(np.clip(u1 @ (RK @ (rotm(u2, q) @ u3)), -1, 1)))); a1e.append(D(math.acos(np.clip(u1 @ (RK @ u2), -1, 1))))
    th, a1e = np.array(th), np.array(a1e); return th, np.minimum(th - np.abs(a1e - a2), np.minimum(a1e + a2, 360 - a1e - a2) - th)
th0, m0 = law_m(0.0); camt = g["camt"]; sel = drv
thp = np.interp(np.radians(camt[sel]), ts_l, th0)
rows = []
for off in (-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0):
    th1, m1 = law_m(off); mp = np.interp(thp, th1, m1, left=np.nan, right=np.nan) if np.all(np.diff(th1) > 0) else np.full(len(thp), np.nan)
    rows.append(dict(K_offset_deg=off, taken_margin_min=round(float(np.nanmin(mp)), 3) if np.isfinite(mp).any() else None, below5=int(np.nansum(mp < 5.0))))
res["fold_vs_K_offset"] = dict(model_m3e_min_taken=round(float(g["m3e"][sel].min()), 3), law_margin_nominal_min=round(float(m0[ts_l > 0].min()), 3), rows=rows,
                               note="pose th held fixed; the chain re-solves q2 for the offset K (the encoders read the pose; the cuff does not feel it)")
# CAD exports: lobe polar (lobe frame: x = pitch dir at onset, y = u2 x x), stroke table, spec points
prof = F["C2"] - (F["C2"] @ u2)[:, None] * u2
nrm = []
for j in range(len(ts)):
    tg = np.gradient(prof, ts, axis=0)[j]; nn = unit(np.cross(u2, tg)); nn = nn if nn @ prof[j] > 0 else -nn; nrm.append(prof[j] - RR * nn)
nrm = np.array(nrm)
with open(os.path.join(SP, f"lobe_polar_{TAG}.csv"), "w") as fh:
    fh.write("t_deg_q2_past_onset,dK_deg,phi_crank_deg,pitch_az_deg,pitch_r_mm,profile_az_deg,profile_r_mm,pressure_angle_deg,rod_force_N_spring,follower_force_N_spring\n")
    TK = 0.08 + 0.015 * kks; Frod = TK / (mh_t / 1000); Fn = Frod * mc_t / m_f
    for j in range(0, len(ts), 4):
        pa_ = D(math.atan2(prof[j] @ F["by"], prof[j] @ F["bx"])); qa = D(math.atan2(nrm[j] @ F["by"], nrm[j] @ F["bx"]))
        fh.write(f"{D(ts[j]):.3f},{D(kks[j]):.3f},{D(phs[j]):.3f},{pa_:.3f},{np.linalg.norm(prof[j]):.4f},{qa:.3f},{np.linalg.norm(nrm[j]):.4f},{F['pa'][j]:.2f},{Frod[j]:.1f},{Fn[j]:.1f}\n")
spec = dict(frame="link 1b at q = 0, K on stop A (the model's rigid-sample frame, mm from GH); lobe frame = link 2 at the onset q2",
            u2=u2.tolist(), uK=uK.tolist(), dR_crank_axis=dR.tolist(), crank_pivot_on_dR_boss_underside=PV.tolist(), crank_tip_ball_centre=tip0.tolist(),
            horn_ball_centre=H0.tolist(), rod_centres_mm=res["rod_len"], roller_centre_onset=F["C0"].tolist(), roller_axis=dR.tolist(),
            lobe_polar_x=F["bx"].tolist(), lobe_polar_y=F["by"].tolist(), lobe_band_u2_levels=[f2 + 6.2, f2 + 9.2], q2_onset_deg=res["q2_onset_deg"],
            q2_stopB_deg=res["q2_stopB_deg"], K_stopB_dK_deg=res["dK_lim_deg"], r_h=r_h, beta_deg=beta, La=La, f2=f2, fK=fK)
json.dump(spec, open(os.path.join(SP, f"spec_points_{TAG}.json"), "w"), indent=1)
# clearance of the crank-tip eye vs hub 2 along the stroke (where it binds)
eT = [cyl_clear(eye_pts(tips[j], rod[j], rotm(dR, ph[j]) @ dR), u2, f2 - 1, f2 + CROWN, HUB_R) for j in range(len(kk))]
eH = [cyl_clear(eye_pts(Hs[j], -rod[j], uK), uK, fK - 1, fK + CROWN, HUB_R) for j in range(len(kk))]
res["eye_clear_vs_dK"] = [dict(dK=round(D(float(kk[j])), 1), tip_eye_hub2=round(eT[j], 2), horn_eye_hubK=round(eH[j], 2), tilt_h=round(float(tilt_h[j]), 1)) for j in range(0, len(kk), 8)]
json.dump(res, open(os.path.join(SP, f"results_{TAG}.json"), "w"), indent=1, default=float)
print(json.dumps({k: res[k] for k in ("follower_chosen", "loads", "K_error_deg_per_10um", "fold_vs_K_offset", "eye_clear_vs_dK")}, indent=1, default=float))
