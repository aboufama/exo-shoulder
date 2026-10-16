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
