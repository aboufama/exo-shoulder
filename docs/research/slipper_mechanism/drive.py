"""Slipper-nose drive red team on the extracted geometry (extract.py -> geo_*.npz). Copied from the gen-6 roller red team
(docs/research/roller_mechanism/drive.py: flank as a ruled surface + tangent-arc CAD sketch, the real lobe follower, loads,
bent-arm stiffness, play -> K, per-part skin) and changed for a SLIDING nose: the flank is the nose-centre path offset by
the nose radius NR (env NR, default the claim's nose_r), friction mu on BOTH strokes (outward: the crank drives the horn;
return: the clock spring drives the crank back through the sliding contact), signed flank curvature (conformal pocket vs
convex), Hertz line contact (440C nose on a-C:H DLC on Ti-6Al-4V) incl. the edge loading a straight extrude would cause
(slicing method), Archard wear maps on the nose and the flank over 1e6 cycles, the dowel press fit / pull-out / bending,
and every K error source -> the one fold-margin metric th per taken pose (exact re-solve on the slaved law, bench and held
out). Writes results_<tag>.json, flank_<tag>.csv, lobe_polar_<tag>.csv, spec_points_<tag>.json, slaved_law_<tag>.json.

    NR=1.25 python3 docs/research/slipper_mechanism/drive.py geo_bench.npz bench_r125 [geo_held.npz]
"""
import json, math, os, sys
import numpy as np
SP = os.path.dirname(os.path.abspath(__file__))
Z = np.load(os.path.join(SP, sys.argv[1])); g = {k: Z[k] for k in Z.files}; TAG = sys.argv[2]
ZH = np.load(os.path.join(SP, sys.argv[3])) if len(sys.argv) > 3 else None
D, R_ = math.degrees, math.radians
def unit(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)
def rotm(ax, a):
    ax = ax / np.linalg.norm(ax); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]]); return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K
def ang(a, b): return D(math.acos(max(-1.0, min(1.0, float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))))))
u1, u2, u3, uK, dR, PV, C0 = g["u1"], g["u2"], g["u3"], g["uK"], g["dR"], g["PV"], g["C0"]
f = g["f"]; f2 = float(f[1]); fK = float(g["fK"]); sp, sig, gg, cc = float(g["sp"]), float(g["sig"]), float(g["gg"]), float(g["cc"])
HUB_R, UP, T_LINK, CROWN, RUN, W_LINK, bk1, bk2, a1max, kK, r_c, beta, s_arm, r_lobe, hl, lift, g_, zr, ang_min, nose_r, MU = [float(x) for x in g["consts"]]
dK_lim = float(g["dK_lim"]); tk = g["taken"]; st = g["kstate"]; dKp = np.abs(g["dK"])
ROLL_R = float(os.environ.get("NR", nose_r)); ROLL_W = 2.5          # nose radius; modelled nose band +-1.25 about the lug mid layer
L_C = float(os.environ.get("LC", 2.2))                                   # effective line length: 2.5 band - ~0.3 end form of the dowel
MUS = (0.087, 0.12, 0.15)
res = dict(tag=TAG, nose_r_flank=ROLL_R, nose_r_claim=nose_r, mu_claim=MU, f2=f2, fK=fK, g=gg, kK=kK, r_c=r_c, beta=beta, lift=lift, hl=hl, dK_lim_deg=round(D(dK_lim), 2),
           dK_taken_max_deg=round(D(float(dKp[tk].max())), 2), dR_to_u2_deg=round(ang(dR, u2), 2), uK_to_u2_deg=round(ang(uK, u2), 2),
           dR_to_uK_deg=round(ang(dR, uK), 2), pivot_on_dR_mm=round(float(np.linalg.norm(PV)), 2), roller_centre_from_GH_mm=round(float(np.linalg.norm(C0)), 2))
if ZH is not None: res["dK_taken_max_held_deg"] = round(D(float(np.abs(ZH["dK"][ZH["taken"]]).max())), 2)

# ---------------- 1. the cam pair, re-synthesised (the model's own construction, 0.05 deg grid, to dK_lim + 6 deg) ----------------
def vH(X): return -sp * np.cross(uK, X)
kg = np.radians(np.arange(0.0, D(dK_lim) + 6.0 + 1e-9, 0.05)); nk = len(kg)
phi = kg / gg * (1 + cc * kg); dphi = (1 + 2 * cc * kg) / gg
Rk = np.array([rotm(uK, sp * k) for k in kg]); Rc = np.array([rotm(dR, sig * p) for p in phi])
Cg = np.einsum("nij,j->ni", Rc, C0 - PV) + PV
ng = np.zeros((nk, 3)); pac = np.zeros(nk); pah = np.zeros(nk); nprev = None
for j in range(nk):
    C = Cg[j]; vC = sig * dphi[j] * np.cross(dR, C); vr = vC - vH(C); n = unit(np.cross(unit(C), vr))
    if nprev is None: n = n if n @ vH(C) >= 0 else -n
    else: n = n if n @ nprev >= 0 else -n
    nprev = n; ng[j] = n; Q = C + ROLL_R * n; pac[j] = ang(n, vC); pah[j] = ang(n, vH(Q))
Qg = Cg + ROLL_R * ng
P1 = np.einsum("nij,nj->ni", Rk, Cg); N1 = np.einsum("nij,nj->ni", Rk, ng); Q1 = np.einsum("nij,nj->ni", Rk, Qg)   # link 1a frame (= model frame at K 0)
jl = int(round(D(dK_lim) / 0.05)); jt = int(round(res["dK_taken_max_deg"] / 0.05))
ct_k = np.degrees(g["kgrid"]); chk = float(np.max(np.abs(np.interp(ct_k[ct_k <= D(dK_lim)], np.degrees(kg), pah) - g["ct_pa_horn"][ct_k <= D(dK_lim)])))
res["cam_resynth_vs_model_pa_horn_maxdiff_deg"] = round(chk, 3)
mH = np.abs(np.einsum("ni,ni->n", np.cross(Qg, ng), np.tile(uK, (nk, 1))))          # normal's moment arm about uK (mm)
mC = np.abs(np.einsum("ni,ni->n", np.cross(Qg - PV, ng), np.tile(dR, (nk, 1))))     # ... about the crank axis
rQ = np.linalg.norm(Q1 - np.outer(Q1 @ uK, uK), axis=1)
def at(k_deg): j = min(int(round(k_deg / 0.05)), nk - 1); return j
pa_tab = []
for kd in (0, 10, 20, 30, 40, 44, 45, 45.62, 46.17, 46.25, 47, 48, 49, 50, 51):
    j = at(kd)
    if j < nk: pa_tab.append(dict(dK=kd, pa_horn=round(float(pah[j]), 2), pa_crank=round(float(pac[j]), 2), m_horn_mm=round(float(mH[j]), 2),
                                  m_crank_mm=round(float(mC[j]), 2), contact_r_mm=round(float(rQ[j]), 2)))
res["pressure_angle_table"] = pa_tab
# where would 45 / 50 deg be reached, and the model's clearances past the limit
res["dK_at_pa_horn"] = {str(a): (round(float(np.degrees(kg[np.argmax(pah >= a)])), 2) if (pah >= a).any() else None) for a in (43, 44, 45, 50, 55)}
ck = np.degrees(g["kgrid"])
res["model_clear_past_lim"] = [dict(dK=round(float(ck[j]), 2), arm_hubK=round(float(g["ct_clear_hubK"][j]), 2), roller_hubK=round(float(g["ct_clear_roll_hubK"][j]), 2),
                                    arm_hub2=round(float(g["ct_clear_hub2"][j]), 2)) for j in range(len(ck)) if D(dK_lim) - 2 <= ck[j] <= D(dK_lim) + 6.01 and j % 4 == 0]

cK, cR = g["ct_clear_hubK"], g["ct_clear_roll_hubK"]; inr = ck <= D(dK_lim) + 1e-6
res["hubK_clear_where"] = dict(arm_min=round(float(cK[inr].min()), 2), arm_at_dK=round(float(ck[inr][np.argmin(cK[inr])]), 2),
                               roller_min=round(float(cR[inr].min()), 2), roller_at_dK=round(float(ck[inr][np.argmin(cR[inr])]), 2))
# ---------------- 2. the flank: ruled developable surface Q1 + s unit(P1); machining + CAD ----------------
J = np.arange(0, min(at(D(dK_lim) + 2.0), nk - 1) + 1)            # built flank: used stroke + 2 deg run-out
rul = unit(P1[J]); zc = unit(rul.mean(axis=0))
taper = np.array([ang(r, zc) for r in rul])
ex = unit(uK - (uK @ zc) * zc); ey = np.cross(zc, ex)
h0 = float((Q1[J] @ zc).mean())
def section(s):
    X = Q1[J] + s * rul                                              # exact flank points at s along the ruling (mm)
    t = (h0 + s - X @ zc) / (rul @ zc); X = X + t[:, None] * rul      # move along the ruling onto the plane z = h0 + s
    return np.c_[X @ ex, X @ ey]
mid, top, bot = section(0.0), section(+1.5), section(-1.5)
def pl_dist(Pts, Poly):
    out = []
    for p in Pts:
        a, b = Poly[:-1], Poly[1:]; ab = b - a; t = np.clip(np.einsum("ij,ij->i", p - a, ab) / np.maximum(np.einsum("ij,ij->i", ab, ab), 1e-12), 0, 1)
        out.append(float(np.min(np.linalg.norm(a + t[:, None] * ab - p, axis=1))))
    return np.array(out)
err_ext = max(float(pl_dist(top, mid).max()), float(pl_dist(bot, mid).max()))
err_roll = max(float(pl_dist(section(1.25), mid).max()), float(pl_dist(section(-1.25), mid).max()))
def edge_gap():
    out = []
    for q, j in enumerate(J):
        for s_ in (-1.25, 1.25):
            X = P1[j] + s_ * rul[q]; t = (h0 - X @ zc); Xp = X + t * zc; p2 = np.array([[Xp @ ex, Xp @ ey]])
            out.append(float(pl_dist(p2, mid)[0]) - ROLL_R)
    return np.array(out)
eg = edge_gap(); res["flank_extrude_roller_edge_gap_mm"] = [round(float(eg.min()), 4), round(float(eg.max()), 4)]
mis = np.array([D(math.asin(min(1.0, abs(float(r @ unit(np.cross(zc, np.cross(n_, zc)))))))) for r, n_ in zip(rul, N1[J])])
# curvature of the flank section (mid plane) -> tool / wire radius limit
x, y = mid[:, 0], mid[:, 1]; s_ = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]
dx, dy = np.gradient(x, s_), np.gradient(y, s_); ddx, ddy = np.gradient(dx, s_), np.gradient(dy, s_); kap = dx * ddy - dy * ddx
nn2 = np.c_[N1[J] @ ex, N1[J] @ ey]; side = np.sign(kap * (-dy * nn2[:, 0] + dx * nn2[:, 1]) * -1)   # >0: concave toward the roller side
rho = 1 / np.maximum(np.abs(kap), 1e-9)
res["flank"] = dict(length_mm=round(float(s_[-1]), 2), built_to_dK=round(float(np.degrees(kg[J[-1]])), 2),
                    rulings_through_GH_offset_mm=ROLL_R, machine_axis_zc=zc.tolist(), wire_taper_deg=[round(float(taper.min()), 2), round(float(taper.max()), 2)],
                    straight_extrude_err_mm_at_pm1p5=round(err_ext, 4), straight_extrude_err_mm_over_roller_pm1p25=round(err_roll, 4),
                    roller_edge_misalignment_on_extrude_deg=round(float(mis.max()), 2),
                    rho_min_mm=round(float(rho.min()), 2), rho_min_at_dK=round(float(np.degrees(kg[J][np.argmin(rho)])), 2),
                    rho_concave_min_mm=round(float(rho[side > 0].min()), 2) if (side > 0).any() else None,
                    rho_convex_min_mm=round(float(rho[side <= 0].min()), 2) if (side <= 0).any() else None,
                    contact_r_from_uK_mm=[round(float(rQ[J].min()), 2), round(float(rQ[J].max()), 2)], mid_plane_h_on_zc_mm=round(h0, 3),
                    sketch_frame=dict(origin="GH", ex=ex.tolist(), ey=ey.tolist(), ez=zc.tolist()))
# tangent-arc fit of the mid section (greedy 3-point arcs, max error 3 um) -> the CAD sketch
def arc3(a, b, c):
    A = np.array([[b[0] - a[0], b[1] - a[1]], [c[0] - a[0], c[1] - a[1]]]) * 2
    rhs = np.array([b @ b - a @ a, c @ c - a @ a])
    try: o = np.linalg.solve(A, rhs)
    except np.linalg.LinAlgError: return None, np.inf
    return o, float(np.linalg.norm(a - o))
arcs = []; i0 = 0; m = len(mid)
while i0 < m - 1:
    best = None
    for i1 in range(m - 1, i0 + 1, -1):
        im = (i0 + i1) // 2; o, r = arc3(mid[i0], mid[im], mid[i1])
        if o is None: continue
        e = float(np.abs(np.linalg.norm(mid[i0:i1 + 1] - o, axis=1) - r).max())
        if e <= 0.003: best = (i1, o, r, e); break
    if best is None: best = (i0 + 1, None, np.inf, 0.0)
    i1, o, r, e = best
    arcs.append(dict(p0=[round(float(v), 4) for v in mid[i0]], pm=[round(float(v), 4) for v in mid[(i0 + i1) // 2]], p1=[round(float(v), 4) for v in mid[i1]],
                     centre=[round(float(v), 4) for v in o] if o is not None else None, r=round(float(r), 3), err_mm=round(e, 4),
                     dK=[round(float(np.degrees(kg[J[i0]])), 2), round(float(np.degrees(kg[J[i1]])), 2)]))
    i0 = i1
res["flank_arcs"] = arcs
with open(os.path.join(SP, f"flank_{TAG}.csv"), "w") as fh:
    fh.write("dK_deg,pa_horn_deg,pa_crank_deg,mid_x,mid_y,top_x,top_y,bot_x,bot_y,nose_cx,nose_cy,nose_cz,contact_x,contact_y,contact_z,normal_x,normal_y,normal_z\n")
    for q, j in enumerate(J[::5]):
        qi = q * 5
        fh.write(",".join(f"{v:.4f}" for v in [np.degrees(kg[j]), pah[j], pac[j], *mid[qi], *top[qi], *bot[qi], *P1[j], *Q1[j], *N1[j]]) + "\n")

# ---------------- 3. the real lobe follower (exact spatial cam; the sidecar red team's search, this design's law) ----------------
ts_l, dKl, q2t, q2hi = g["law_ts"], g["law_dK"], g["law_q2t"], float(g["q2hi"])
dKl_abs = np.abs(dKl); t_lim = float(np.interp(dK_lim, dKl_abs, ts_l)) if dKl_abs.max() >= dK_lim else dK_lim / kK
ts = np.radians(np.linspace(0, D(t_lim), 121)); kks = np.interp(ts, ts_l, dKl_abs); phs = sig * kks / gg * (1 + cc * kks)
res["law"] = dict(kK_eff=round(float(kks[-1] / ts[-1]), 4), t_lim_deg=round(D(t_lim), 3), q2_onset_deg=round(D(q2hi), 3), q2_at_dKlim_deg=round(D(q2hi - t_lim), 3),
                  phi_crank_at_dKlim_deg=round(D(float(abs(phs[-1]))), 2), q2_stops_deg=[round(D(float(v)), 3) for v in g["q2stops"]])
def follower(a_s, psi, rr, hmid):
    e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1)
    v = math.cos(psi) * e1 + math.sin(psi) * e2; s = (hmid - a_s * (v @ u2)) / (dR @ u2); F0 = s * dR + a_s * v
    C = np.array([rotm(dR, p) @ F0 for p in phs]); C2 = np.array([rotm(u2, t) @ c for c, t in zip(C, ts)])
    z = C2 @ u2; xy = C2 - z[:, None] * u2; rho_ = np.linalg.norm(xy, axis=1)
    T2 = np.gradient(C2, ts, axis=0); Tb = np.array([rotm(u2, -t) @ v_ for v_, t in zip(T2, ts)])
    n = unit(np.cross(Tb, u2)); vf = np.gradient(C, ts, axis=0)
    pa = np.degrees(np.arccos(np.clip(np.abs(np.einsum("ni,ni->n", n, unit(vf + 1e-12))), 0, 1)))
    bx = unit(xy[0]); by = np.cross(u2, bx); x_, y_ = xy @ bx, xy @ by
    dx_, dy_ = np.gradient(x_, ts), np.gradient(y_, ts); ddx_, ddy_ = np.gradient(dx_, ts), np.gradient(dy_, ts)
    kap_ = (dx_ * ddy_ - dy_ * ddx_) / np.maximum((dx_ ** 2 + dy_ ** 2) ** 1.5, 1e-12); rc_ = 1 / np.where(np.abs(kap_) < 1e-9, 1e-9, kap_)
    return dict(F0=F0, C=C, C2=C2, rho=rho_, z=z, pa=pa, rc=rc_, n=n, bx=bx, by=by, s=s)
hmid = f2 + 7.45; d_lvl = float(hmid * math.tan(math.acos(dR @ u2)))
best = []
for rr, part in ((3.0, "MR63ZZ (3x6x2.5) on an O3 pin"), (2.5, "IKO CFS2.5 stud cam follower (O5 x 3)")):
    for a_s in np.arange(4.5, 9.01, 0.5):
        for psi in np.radians(np.arange(0, 360, 3)):
            F = follower(a_s, psi, rr, hmid)
            dwell = F["rho"][0] - rr - 0.1; nose = float(F["rho"].max() - rr)
            if not (10.1 <= dwell <= 10.8): continue
            if float(F["rho"].min()) - rr < 10.1: continue                  # the profile never dips into hub 2's O20 housing (ring bore O18)
            if a_s < 3.0 + rr + 0.3: continue
            if nose > d_lvl - 3.0 - 0.5: continue
            if float(np.abs(F["z"] - F["z"][0]).max()) > 0.6: continue
            if not np.all(((F["rc"] < 0) & (np.abs(F["rc"]) > rr + 0.5)) | (F["rc"] > rr + 0.8)): continue
            best.append((float(F["pa"].max()), rr, part, round(float(a_s), 2), round(D(psi), 1), round(dwell, 2), round(nose, 2),
                         round(float(np.abs(F["z"] - F["z"][0]).max()), 2), round(float(np.min(np.abs(F["rc"]))), 2)))
best.sort(key=lambda r: (r[0] > 38.0, -r[1], -r[3], r[0]))
res["follower_neck_level_d_mm"] = round(d_lvl, 2); res["follower_n_feasible"] = len(best)
res["follower_options"] = [dict(pa_max=round(b[0], 1), rr=b[1], part=b[2], a_s=b[3], psi=b[4], dwell_r=b[5], nose_r=b[6], drift=b[7], rc_min=b[8]) for b in best[:10]]
if best:
    b0 = best[0]; RR, A_S, PSI = b0[1], b0[3], R_(b0[4])
else:
    RR, A_S, PSI = 2.5, 6.0, R_(201.0)
A_S = float(os.environ.get("A_S", A_S)); PSI = R_(float(os.environ.get("PSI", D(PSI)))); RR = float(os.environ.get("RR", RR))
FF = follower(A_S, PSI, RR, hmid)
m_f = np.abs(np.einsum("ni,i->n", np.cross(FF["C"] - PV, FF["n"]), dR)); m_2 = np.abs(np.einsum("ni,i->n", np.cross(FF["C"], FF["n"]), u2))
res["follower_chosen"] = dict(a_s=A_S, psi_deg=round(D(PSI), 1), rr=RR, pa_deg=[round(float(FF["pa"].min()), 1), round(float(FF["pa"].max()), 1)],
                              pitch_r=[round(float(FF["rho"].min()), 2), round(float(FF["rho"].max()), 2)],
                              profile_r=[round(float(FF["rho"].min() - RR), 2), round(float(FF["rho"].max() - RR), 2)], m_f_mm=[round(float(m_f.min()), 2), round(float(m_f.max()), 2)],
                              drift_mm=round(float(np.abs(FF["z"] - FF["z"][0]).max()), 2), pitch_rc_min=round(float(np.abs(FF["rc"]).min()), 2),
                              follower_centre_onset=[round(float(v), 3) for v in FF["F0"]], s_on_dR=round(FF["s"], 2))

# ---------------- 4. loads through the train WITH SLIDING FRICTION, both strokes ----------------
E_TI, G_TI, E_ST, NU_TI, NU_ST = 114e3, 44e3, 200e3, 0.34, 0.28
ESTAR = 1 / ((1 - NU_ST ** 2) / E_ST + (1 - NU_TI ** 2) / E_TI)            # 440C nose on the Ti-6Al-4V substrate (DLC 2-3 um is thin vs b)
def hertz_line(Fn, R1, R2, l, E1=E_ST, E2=E_TI, nu=0.3):                    # kept for the bearing / follower checks (roller code)
    Es = 1 / ((1 - nu ** 2) / E1 + (1 - nu ** 2) / E2); Rr = 1 / (1 / R1 + 1 / R2) if R2 > 0 else R1; return math.sqrt(Fn * Es / (2 * math.pi * l * Rr)) * 2 / math.sqrt(2)
def hline(w, Rr):                                                            # line contact: w N/mm, Rr mm -> p0 MPa, half-width b mm
    p0 = math.sqrt(w * ESTAR / (math.pi * Rr)); return p0, 2 * w / (math.pi * p0)
kidx = np.arange(0, jt + 1); kk_t = kg[kidx]
# flank curvature per K step (mid section, signed: concave toward the nose = conformal), on the built-flank index J
rho_k = np.interp(kk_t, kg[J], rho); conc_k = np.interp(kk_t, kg[J], (side > 0).astype(float)) > 0.5
def r_eq(rf, conc):
    if conc: return math.inf if rf <= ROLL_R else 1 / (1 / ROLL_R - 1 / rf)
    return 1 / (1 / ROLL_R + 1 / rf)
Req = np.array([r_eq(a, b) for a, b in zip(rho_k, conc_k)])
# velocities per unit |dK| (link 1b frame): nose point at Q, flank point at Q, sliding
vN = np.array([sig * dphi[j] * np.cross(dR, Qg[j]) for j in kidx]); vF = np.array([vH(Qg[j]) for j in kidx])
vS = vN - vF; vS = vS - np.einsum("ni,ni->n", vS, ng[kidx])[:, None] * ng[kidx]; vs = np.linalg.norm(vS, axis=1); us = vS / np.maximum(vs, 1e-12)[:, None]
nvf = np.einsum("ni,ni->n", ng[kidx], vF); uvf = np.einsum("ni,ni->n", us, vF); nvn = np.einsum("ni,ni->n", ng[kidx], vN); uvn = np.einsum("ni,ni->n", us, vN)
res["sliding"] = dict(v_slide_mm_per_rad=[round(float(vs.min()), 3), round(float(vs.max()), 3)], at_rest=round(float(vs[0]), 3),
                      slide_per_stroke_mm=round(float(np.trapz(vs, kk_t)), 3), normal_rel_vel_max=round(float(np.abs(nvn - nvf).max()), 5))
# contact point speed along the flank (link 1a frame) and along the nose circumference (crank frame) per unit |dK|
Q1t = Q1[kidx]; vcf = np.linalg.norm(np.gradient(Q1t, kk_t, axis=0), axis=1)
ncr = np.array([Rc[j].T @ ng[j] for j in kidx]); a_n = unit(C0); e1n = unit(ng[0] - (ng[0] @ a_n) * a_n); e2n = np.cross(a_n, e1n)
th_n = np.unwrap(np.arctan2(ncr @ e2n, ncr @ e1n))
vcn = ROLL_R * np.abs(np.gradient(th_n, kk_t))
res["contact_travel"] = dict(on_flank_mm=round(float(np.trapz(vcf, kk_t)), 3), on_nose_arc_deg=round(D(float(th_n.max() - th_n.min())), 2),
                             on_nose_arc_mm=round(float(ROLL_R * (th_n.max() - th_n.min())), 3), flank_contact_speed_at_rest=round(float(vcf[0]), 3),
                             nose_contact_speed_at_rest=round(float(vcn[0]), 3))
CASES = (("spring 0.08 N.m + 0.015 N.m/rad", 0.08, 0.0), ("spring + MVP1 0.033 N.m", 0.08, 0.033))
loads = {}; strokes = {}
for case, T0, Tx in CASES:
    TK = (T0 + 0.015 * kk_t) + Tx                                              # N.m about uK the nose must carry (MVP1 load adds on the opening side)
    loads[case] = {}
    for mu in (0.0,) + MUS:
        den_o = nvf + mu * uvf; den_r = nvf - mu * uvf                         # per unit dK (mm/rad): T_K [N.mm] = Fn * den
        Fo = TK * 1000 / den_o; Fr = np.where(den_r > 0, TK * 1000 / np.maximum(den_r, 1e-9), np.inf)
        Tco = Fo * (nvn + mu * uvn) / dphi[kidx]; Tcr = Fr * (nvn - mu * uvn) / dphi[kidx]     # crank torque N.mm (out: needed; return: delivered)
        eta_o = TK * 1000 / (Tco * dphi[kidx]); eta_r = Tcr * dphi[kidx] / (TK * 1000)
        TJo = TK * kK / eta_o; TJr = TK * kK * eta_r                            # J2 torque (N.m): out = the wearer pushes, return = the train gives back
        p0o = [hline(f / L_C, r)[0] if np.isfinite(r) else 0.0 for f, r in zip(Fo, Req)]; bo = [hline(f / L_C, r)[1] if np.isfinite(r) else 0.0 for f, r in zip(Fo, Req)]
        p0f = [hline(f / L_C, ROLL_R)[0] for f in Fo]
        loads[case][f"mu {mu}"] = dict(Fn_out_N=[round(float(Fo.min()), 2), round(float(Fo.max()), 2)], Fn_return_N=[round(float(Fr.min()), 2), round(float(Fr.max()), 2)],
                                      crank_T_out_Nmm=[round(float(Tco.min()), 1), round(float(Tco.max()), 1)], crank_T_return_Nmm=[round(float(Tcr.min()), 1), round(float(Tcr.max()), 1)],
                                      eta_out=[round(float(eta_o.min()), 3), round(float(eta_o.max()), 3)], eta_return=[round(float(eta_r.min()), 3), round(float(eta_r.max()), 3)],
                                      J2_T_out_Nm=[round(float(TJo.min()), 3), round(float(TJo.max()), 3)], J2_T_return_Nm=[round(float(TJr.min()), 3), round(float(TJr.max()), 3)],
                                      J2_hysteresis_Nm_max=round(float((TJo - TJr).max()), 3),
                                      hertz_p0_MPa_real_flank=round(float(max(p0o)), 0), hertz_half_width_um=round(1000 * float(max(bo)), 1),
                                      hertz_p0_MPa_if_flat_flank=round(float(max(p0f)), 0))
        if case.startswith("spring + MVP1") and mu == MU: Fn0, Tc0, worst = Fo, Tco, dict(Fo=Fo, Fr=Fr)
res["loads"] = loads
# effective pressure angles with friction (the design rule PA + atan(mu) <= 43; lock-up at 90)
pa_h_t, pa_c_t = pah[kidx], pac[kidx]
res["pa_friction"] = {f"mu {mu}": dict(friction_deg=round(D(math.atan(mu)), 2), horn_eff_max=round(float(pa_h_t.max() + D(math.atan(mu))), 2),
                                       crank_eff_max=round(float(pa_c_t.max() + D(math.atan(mu))), 2), margin_to_43=round(float(43 - pa_h_t.max() - D(math.atan(mu))), 2),
                                       margin_to_45=round(float(45 - pa_h_t.max() - D(math.atan(mu))), 2), margin_to_lock_90=round(float(90 - max(pa_h_t.max(), pa_c_t.max()) - D(math.atan(mu))), 2),
                                       mu_at_43=round(math.tan(R_(43 - float(pa_h_t.max()))), 3), mu_lock=round(math.tan(R_(90 - float(max(pa_h_t.max(), pa_c_t.max())))), 2))
                     for mu in MUS}
res["pa_friction"]["taken_stroke_deg"] = round(D(float(kk_t[-1])), 2)
res["flank_curvature_taken"] = dict(rho_min_mm=round(float(rho_k.min()), 3), at_dK=round(D(float(kk_t[int(np.argmin(rho_k))])), 2),
                                    concave_share=round(float(conc_k.mean()), 3), convex_rho_min=round(float(rho_k[~conc_k].min()), 3) if (~conc_k).any() else None,
                                    concave_rho_min=round(float(rho_k[conc_k].min()), 3) if conc_k.any() else None,
                                    pocket_clearance_min_mm=round(float((rho_k[conc_k] - ROLL_R).min()), 3) if conc_k.any() else None,
                                    R_equiv_min_mm=round(float(Req.min()), 2), rest_rho_mm=round(float(rho_k[0]), 3), rest_concave=bool(conc_k[0]),
                                    table=[dict(dK=round(D(float(kk_t[q])), 1), rho=round(float(rho_k[q]), 3), concave=bool(conc_k[q]), R_eq=round(float(Req[q]), 2))
                                           for q in range(0, len(kk_t), max(1, len(kk_t) // 18))])
# edge loading if the flank were a STRAIGHT extrude along z_c (slicing method on the worst mismatch): line split in 0.01 mm slices
def approach(w, Rr):                                                         # 2D line-contact approach (both bodies, Johnson 5.39-type), mm
    if w <= 0: return 0.0
    p0, b = hline(w, Rr); return 2 * w / (math.pi * ESTAR) * (math.log(4 * Rr / b) - 0.5)
def sliced(F, Rr, gap_end):
    xs = np.linspace(-L_C / 2, L_C / 2, 221); gx = gap_end * (xs - xs[0]) / (xs[-1] - xs[0]); dx_ = xs[1] - xs[0]
    def wloc(h):
        lo, hi = 0.0, 1e4
        if h <= 0: return 0.0
        for _ in range(60):
            m = (lo + hi) / 2
            if approach(m, Rr) < h: lo = m
            else: hi = m
        return lo
    lo, hi = 0.0, gap_end + 0.05
    for _ in range(50):
        dl = (lo + hi) / 2; Ft = sum(wloc(dl - gg_) for gg_ in gx) * dx_
        if Ft < F: lo = dl
        else: hi = dl
    ws_ = np.array([wloc(dl - gg_) for gg_ in gx]); return float(max(hline(w_, Rr)[0] for w_ in ws_ if w_ > 0)), float((ws_ > 0).mean() * L_C)
eg_mis = float(np.abs(eg).max()) if len(eg) else 0.0
Fw = float(worst["Fo"].max()); Rw = float(Req[int(np.argmax(worst["Fo"]))]) if np.isfinite(Req[int(np.argmax(worst["Fo"]))]) else 50.0
p_al, b_al = hline(Fw / L_C, Rw)
res["edge_loading"] = dict(F_worst_N=round(Fw, 2), R_eq_there_mm=round(Rw, 2), aligned_p0_MPa=round(p_al, 0), aligned_half_width_um=round(1000 * b_al, 1),
                           aligned_approach_um=round(1000 * approach(Fw / L_C, Rw), 3),
                           straight_extrude_edge_mismatch_um=round(1000 * eg_mis, 1))
for gap_um in (2.0, 5.0, 10.0, 20.0):
    pk, lc = sliced(Fw, Rw, gap_um / 1000); res["edge_loading"][f"mismatch_{gap_um:g}um"] = dict(p0_peak_MPa=round(pk, 0), contact_len_mm=round(lc, 2))
pk, lc = sliced(Fw, ROLL_R, 0.02); res["edge_loading"]["mismatch_20um_on_convex_worstcase_Rnose"] = dict(p0_peak_MPa=round(pk, 0), contact_len_mm=round(lc, 2))
# substrate / coating limits
SY_TI = 830.0
res["contact_limits"] = dict(Ti64_yield_MPa=SY_TI, p0_substrate_yield_line_MPa=round(SY_TI / (2 * 0.30), 0), dlc_eggshell_design_p0_MPa=1000,
                             sigma_vm_max_frictionless_factor=0.557, z_max_shear_over_b=0.786,
                             note="Tresca onset in the Ti under line contact at p0 = sigma_y / (2 x 0.30) = 1.67 sigma_y; a 2-3 um a-C:H coating on Ti needs p0 well under that (eggshell): 1.0 GPa design limit; sliding at mu <= 0.15 raises the peak von Mises ~10-20 % and moves it toward the surface")
# the crank pair (two-support statics on dR), the nose force incl. friction
Fpt = np.array([np.interp(kk_t, kks, FF["C"][:, c]) for c in range(3)]).T; Fdir = unit(np.array([np.interp(kk_t, kks, FF["n"][:, c]) for c in range(3)]).T)
f_m = np.interp(kk_t, kks, m_f); f_rc = np.interp(kk_t, kks, np.abs(FF["rc"]))
LAYOUTS = {"A: 2x MR63ZZ (3x6x2.5) in the O10 x 6 boss, 1 mm spacer": (1.25, 4.75, 73.0),
           "B: 2x 683ZZ (3x7x3) in an O10 x 6 boss, no spacer": (1.5, 4.5, 120.0),
           "C: 2x MR63ZZ straddling the follower, boss O10 x 9.5": (1.25, 8.25, 73.0),
           "D: 2x 683ZZ straddling the follower, boss O10 x 10": (1.5, 8.5, 120.0)}
def pair(Fs, Xs, a, b):
    A = PV + a * dR; M = sum(np.cross(X - A, F_) for F_, X in zip(Fs, Xs)); M = M - (M @ dR) * dR
    Ft = sum(Fs); Fp = Ft - (Ft @ dR) * dR; Rb = np.cross(dR, M) / (b - a); Ra = -Fp - Rb
    return max(float(np.linalg.norm(Ra)), float(np.linalg.norm(Rb))), abs(float(Ft @ dR))
lay = {}
for mu in (MU, 0.15):
    Fo = TK0 = None
    TK = 0.113 + 0.015 * kk_t; den_o = nvf + mu * uvf; Fo = TK * 1000 / den_o
    Fnose = -(Fo[:, None] * ng[kidx] + mu * Fo[:, None] * us)                  # force on the nose (crank) from the flank, outward stroke
    Tc = np.einsum("ni,i->n", np.cross(Qg[kidx] - PV, Fnose), dR)
    Ff = np.abs(Tc) / f_m; sgn = -np.sign(np.einsum("ni,ni->n", np.cross(Fpt - PV, Fdir), np.tile(dR, (len(kidx), 1))) * Tc); Ffv = (Ff * sgn)[:, None] * Fdir
    lay[f"MVP1, mu {mu}"] = {nm: (lambda rr_: dict(worst_radial_N=round(max(x[0] for x in rr_), 1), axial_N=round(max(x[1] for x in rr_), 1), C0r_N=c0,
                                                    SF_static=round(c0 / max(x[0] for x in rr_), 2)))([pair([Fnose[q], Ffv[q]], [Qg[kidx][q], Fpt[q]], a, b) for q in range(len(kidx))])
                             for nm, (a, b, c0) in LAYOUTS.items()}
    lay[f"MVP1, mu {mu}"]["F_follower_N"] = [round(float(Ff.min()), 1), round(float(Ff.max()), 1)]
    lay[f"MVP1, mu {mu}"]["hertz_follower_lobe_MPa"] = round(max(hertz_line(ff, RR, max(rc - RR, 0.5), 2.2, E2=E_ST) for ff, rc in zip(Ff, f_rc)), 0)
res["crank_pair_layouts"] = lay
Fn0 = worst["Fo"]

# ---------------- 5. stiffness: the bent arm (unit-load method on its polyline), the stub, the crank pair ----------------
arm = g["armPts"]                                                              # boss -> straight -> arc -> roller (link 1b frame, K 0)
seg = np.diff(arm, axis=0); Ls = np.linalg.norm(seg, axis=1); mids = 0.5 * (arm[1:] + arm[:-1]); tt = unit(seg)
b_w, h_t = W_ARM, H_ARM = float(os.environ.get("ARM_W", 6.0)), float(os.environ.get("ARM_T", 3.0))
I_t = b_w * h_t ** 3 / 12; I_w = h_t * b_w ** 3 / 12; bb, aa = max(b_w, h_t), min(b_w, h_t); Jt = aa ** 3 * bb * (1 / 3 - 0.21 * aa / bb * (1 - aa ** 4 / (12 * bb ** 4)))
def arm_defl(Fv, Pt, dirv):
    """deflection (mm) at Pt along dirv under force Fv (N) at Pt, the arm clamped at the boss: sum over segments of M.m/EI + T.t/GJ"""
    d = 0.0
    for x, t_, L in zip(mids, tt, Ls):
        r = Pt - x; M = np.cross(r, Fv); m = np.cross(r, dirv)
        er = unit(x - (x @ t_) * t_) if np.linalg.norm(x - (x @ t_) * t_) > 1e-9 else unit(np.cross(t_, [0, 0, 1.0]))
        ew = np.cross(t_, er)                                                    # thickness along er (radial), width along ew
        Mt, mt = M @ t_, m @ t_; Mr, mr = M @ er, m @ er; Mw, mw = M @ ew, m @ ew
        d += L * (Mt * mt / (G_TI * Jt) + Mw * mw / (E_TI * I_t) + Mr * mr / (E_TI * I_w))
    return d
jw = int(np.argmax(Fn0)); n0 = ng[0]; F0v = -float(Fn0[0]) * n0
stub_L = 0.15 + 1.5 + 0.5; I_stub = math.pi * 2.5 ** 4 / 64            # the O2.5 nose: arm underside -> contact band mid
d_arm = abs(arm_defl(F0v, C0, n0)); d_arm_w = abs(arm_defl(-float(Fn0.max()) * n0, C0, n0))
d_stub = float(Fn0.max()) * stub_L ** 3 / (3 * E_ST * I_stub)
res["arm"] = dict(load_case="MVP1 0.113 N.m + spring rate, outward stroke at mu claim", polyline_len_mm=round(float(Ls.sum()), 1), n_pts=int(len(arm)), section=f"{b_w} x {h_t} Ti-6Al-4V", I_thick_mm4=round(I_t, 2), J_mm4=round(Jt, 2),
                  defl_along_n_mm=[round(d_arm, 4), round(d_arm_w, 4)], stub_defl_mm=round(d_stub, 5),
                  K_error_from_arm_deg=round(D(d_arm_w / float(mH[kidx].min())), 3),
                  K_change_over_stroke_deg=round(D(abs(d_arm_w - d_arm) / float(mH[kidx].min())), 3),
                  root_stress_MPa=round(float(np.max([np.linalg.norm(np.cross(C0 - x, -float(Fn0.max()) * n0)) for x in arm[:2]])) * 6 / (b_w * h_t ** 2), 1),
                  nose_root_MPa=round(32 * float(Fn0.max()) * stub_L / (math.pi * 2.5 ** 3), 1))

# ---------------- 6. play -> K error (one-sided under the spring: a constant offset, then the variation) ----------------
mHmin, mHmax = float(mH[kidx].min()), float(mH[kidx].max()); lever_roll = float(np.linalg.norm(C0 - PV - ((C0 - PV) @ dR) * dR))
res["K_error_deg_per_10um"] = dict(flank_or_roller_normal=[round(D(0.01 / mHmax), 3), round(D(0.01 / mHmin), 3)],
                                   lobe_or_follower_normal=[round(D(0.01 / float(m_f.max()) * float(mC[kidx].min()) / mHmax), 3), round(D(0.01 / float(m_f.min()) * float(mC[kidx].max()) / mHmin), 3)],
                                   crank_pair_tilt_per_10um_radial_over_span=round(D(0.01 / 3.5 * lever_roll / mHmin), 3), crank_pair_tilt_per_10um_over_7mm_span=round(D(0.01 / 7.0 * lever_roll / mHmin), 3),
                                   lever_roller_from_dR_mm=round(lever_roll, 2), m_horn_mm=[round(mHmin, 2), round(mHmax, 2)],
                                   m_crank_mm=[round(float(mC[kidx].min()), 2), round(float(mC[kidx].max()), 2)])

# ---------------- 7. fold margin th per TAKEN pose vs a K offset: exact re-solve on the slaved law (the verifier's own metric:
# forced poses min(m_sub, m_eff), rest poses m_plain; a K offset moves only forced poses - K on stop A is set by the stop) ----------------
def dm(th, a, b): return np.minimum(th - np.abs(a - b), np.minimum(a + b, 360 - a - b) - th)
def angv(a, B_): return np.degrees(np.arccos(np.clip(B_ @ a, -1, 1)))
def fold_rows(Zx, offs):
    tk_, st_, dK_ = Zx["taken"], Zx["kstate"], np.asarray(Zx["dK"], float)
    a1d, a2d = (D(float(Zx["a1"])) if float(Zx["a1"]) < 4 else float(Zx["a1"])), (D(float(Zx["a2"])) if float(Zx["a2"]) < 4 else float(Zx["a2"]))
    R1, R7, R2 = Zx["R1"], Zx["R7"], Zx["R2"]
    b1 = ang(u1, uK)
    tsL, dKL, q2L = Zx["law_ts"], Zx["law_dK"], Zx["law_q2t"]
    tf = np.linspace(0, float(tsL[-1]), 4001); dKf = np.interp(tf, tsL, dKL); q2f = np.interp(tf, tsL, q2L)
    U3 = np.array([rotm(u2, q) @ u3 for q in q2f]); cf = angv(uK, U3)                       # c = angle(uK, Rq2 u3): K-invariant
    out = {}
    for off in offs:
        RK = np.array([rotm(uK, k + sp * R_(off) * (t > 0)) for k, t in zip(dKf, tf)])
        J2 = RK @ u2; J3 = np.einsum("nij,nj->ni", RK, U3)
        thf = angv(u1, J3); a1e = angv(u1, J2); a2e = np.array([ang(a_, b_) for a_, b_ in zip(J2, J3)])
        mf = np.minimum(dm(thf, b1, cf), dm(thf, a1e, a2e))
        own = []
        for i in np.nonzero(tk_)[0]:
            j3 = R2[i] @ u3; th_i = ang(u1, j3)
            if abs(dK_[i]) <= 1e-6:
                own.append(float(dm(np.array([th_i]), a1d, a2d)[0])); continue
            t_i = float(np.interp(abs(dK_[i]), np.abs(dKL), tsL))                            # the pose's place on the law
            w = np.nonzero(np.abs(tf - t_i) <= R_(6.0))[0]; jj = w[int(np.argmin(np.abs(thf[w] - th_i)))]
            own.append(float(mf[jj]))
        own = np.array(own); out[off] = dict(min=round(float(own.min()), 3), lt5=int((own < 5 - 1e-6).sum()), n=int(len(own)))
    return out
OFFS = (-0.5, -0.3, -0.2, -0.1, -0.05, 0.0, 0.1, 0.25, 0.5)
res["fold_vs_K_offset"] = dict(bench=fold_rows(g, OFFS), note="K offset in deg, + = K more open than the law (a lead), - = a lag; verifier th_margin: 5.181 bench / 5.006 held")
if ZH is not None: res["fold_vs_K_offset"]["held"] = fold_rows({k: ZH[k] for k in ZH.files}, OFFS)

# ---------------- 8. spring, return stroke, lift-off ----------------
b_s, t_s, E_s = 5.0, 0.3, 193e3                                                 # 1.4310 strip
k_spr = 0.015; L_s = E_s * b_s * t_s ** 3 / (12 * k_spr * 1000)
Tmax = 0.08 + 0.015 * R_(res["dK_taken_max_deg"] + 1.0)
res["spring"] = dict(strip=f"{b_s} x {t_s} 1.4310", length_mm_for_0p015=round(L_s, 1), windup_at_stopA_deg=round(D(0.08 / k_spr), 0),
                     torque_stopB_Nm=round(Tmax, 4), bend_stress_max_MPa=round(6 * Tmax * 1000 / (b_s * t_s ** 2), 0),
                     note="spiral (clock) spring in K's cap, the lead's part unchanged (custom from strip)")
# return stroke: the spring must drive horn -> nose -> crank -> follower -> (lobe moving away); drag the crank must beat:
# 2 x 683ZZ grease + shield drag ~0.5 N.mm each at this speed (pessimistic), the follower MR63ZZ rolling ~0.2 N.mm reflected
DRAG_CRANK = 1.2
ret = {}
I_K = 5e-4
for mu in MUS:
    den_r = nvf - mu * uvf; eta_r = (nvn - mu * uvn) / dphi[kidx] * dphi[kidx] / den_r
    for case, T0, Tx in (("spring alone", 0.08, 0.0), ("spring vs MVP1 0.033 opening", 0.08, 0.033)):
        TKn = T0 + 0.015 * kk_t - Tx                                            # net closing torque the spring has left (N.m)
        Tc_avail = TKn * 1000 * eta_r / dphi[kidx] * 1.0                        # crank torque delivered on return (N.mm), / dphi = per rad of crank
        ret[f"mu {mu}, {case}"] = dict(eta_return=[round(float(eta_r.min()), 3), round(float(eta_r.max()), 3)],
                                       crank_T_avail_Nmm=[round(float(Tc_avail.min()), 1), round(float(Tc_avail.max()), 1)],
                                       SF_vs_crank_drag=round(float(Tc_avail.min()) / DRAG_CRANK, 1),
                                       K_accel_limit_rad_s2=round(float((TKn * eta_r).min()) / I_K, 0),
                                       q2_accel_limit_rad_s2=round(float((TKn * eta_r).min()) / I_K / kK, 1))
res["return_stroke"] = ret
res["return_stroke_note"] = ("eta_return = the share of the spring's work that reaches the crank through the sliding nose; lock-up at eta 0 "
                             "(PA + atan(mu) -> 90 on the driving side). Drag 1.2 N.mm at the crank is a pessimistic 2 x 683ZZ (ZZ, greased) + follower. "
                             "Acceleration limit: the spring's net torque through eta over the gen-5 inertia 5e-4 kg m2 about uK")

# ---------------- 8b. wear (Archard, dimensional K in mm3/(N.m)) over 1e6 full-stroke cycles (2 passes each), MVP1 load at mu claim ----------------
NCYC = 1e6
FnW = worst["Fo"]; wl = FnW / L_C                                               # N/mm
dk = np.gradient(kk_t)
def wear_map(Kw, s_pos, v_c):
    # depth per pass at a surface point = K * w * v_s / v_c (contact sweeping over it); binned on the surface coordinate
    bins = np.arange(float(s_pos.min()) - 0.01, float(s_pos.max()) + 0.02, 0.01); hb = np.zeros(len(bins))
    for q in range(len(kk_t)):
        # this K step's sliding work spread over the Hertz width or the contact's own travel, whichever is larger
        pk, bq = hline(wl[q], Req[q] if np.isfinite(Req[q]) else 50.0); span = max(2 * bq, v_c[q] * dk[q], 0.01)
        m = np.abs(bins - s_pos[q]) <= span / 2 + 1e-12
        if not m.any(): m[np.argmin(np.abs(bins - s_pos[q]))] = True
        hb[m] += Kw * wl[q] * vs[q] * dk[q] * 1e-3 / (span) * 0.01 / (0.01)   # mm per pass (w N/mm x slide mm -> N.m per mm of line)
    return float(hb.max() * 2 * NCYC), bins[int(np.argmax(hb))]
s_flank = np.r_[0, np.cumsum(np.linalg.norm(np.diff(Q1t, axis=0), axis=1))]; s_nose = ROLL_R * (th_n - th_n.min())
wear = {}
for lab, Kf, Kn in (("greased (K_DLC 1e-9, K_440C 1e-8)", 1e-9, 1e-8), ("dry, typical a-C:H vs steel (K_DLC 1e-7, K_440C 1e-7)", 1e-7, 1e-7),
                    ("pessimistic / grease lost, abrasive (K_DLC 1e-6, K_440C 1e-6)", 1e-6, 1e-6)):
    hf, sf = wear_map(Kf, s_flank, vcf); hn, sn = wear_map(Kn, s_nose, vcn)
    wear[lab] = dict(flank_DLC_depth_um=round(1000 * hf, 3), at_flank_mm=round(float(sf), 2), nose_depth_um=round(1000 * hn, 3), at_nose_arc_mm=round(float(sn), 2),
                     K_lag_from_both_deg=round(D((hf + hn) / float(mH[kidx].min())), 3), DLC_through_if_2um=bool(hf > 0.002))
res["wear_1e6"] = wear
res["wear_note"] = ("Archard per surface point: depth per pass = K x w x v_slide / v_contact (the contact's own sweep speed on that surface; "
                    "spread over at least the Hertz width 2b); 2 passes per cycle, 1e6 full-stroke cycles at the MVP1 load (worst). "
                    "Friction work per stroke = mu x int(Fn v_s dK).")
res["friction_work_per_stroke_mJ"] = round(float(MU * np.trapz(FnW * vs, kk_t)), 4)

# ---------------- 8c. the dowel: press fit, pull-out, bending ----------------
d_p = 2 * ROLL_R if abs(ROLL_R - 1.25) < 0.01 else 2.5; L_press = 3.0; Do = 6.0
def press(delta):
    p = delta / (d_p * ((1 / E_TI) * ((Do ** 2 + d_p ** 2) / (Do ** 2 - d_p ** 2) + NU_TI) + (1 / E_ST) * (1 - NU_ST)))
    return p, p * (Do ** 2 + d_p ** 2) / (Do ** 2 - d_p ** 2), 0.12 * p * math.pi * d_p * L_press
fits = {}
for lab, dmin_, dmax_ in (("H7/m6 (hole 0/+10, pin +2/+8 um): transition", -0.008, 0.008), ("N7/m6 (hole -4/-14)", 0.006, 0.022),
                          ("P7/m6 (hole -6/-16)", 0.008, 0.024), ("reamed 2.495-2.500 / m6", 0.002, 0.013)):
    lo_, hi_ = press(max(dmin_, 0.0)), press(dmax_)
    fits[lab] = dict(interference_um=[round(1000 * dmin_, 0), round(1000 * dmax_, 0)], p_MPa=[round(lo_[0], 0), round(hi_[0], 0)],
                     hoop_bore_MPa_max=round(hi_[1], 0), pullout_N=[round(lo_[2], 0), round(hi_[2], 0)])
Lb = 0.15 + 1.5                                                                   # arm underside -> the contact band's mid (running gap + half lug)
Mb = float(FnW.max()) * (Lb + 0.5)
res["dowel"] = dict(d=d_p, L_press=L_press, boss_O=Do, fits=fits,
                    retaining_compound_pullout_N=round(15 * math.pi * d_p * L_press, 0),
                    bending_root_MPa=round(32 * Mb / (math.pi * d_p ** 3), 1), defl_tip_um=round(1000 * float(FnW.max()) * (Lb + 0.5) ** 3 / (3 * E_ST * math.pi * d_p ** 4 / 64), 3),
                    bearing_on_hole_MPa=round(float(FnW.max()) / (d_p * L_press), 1), axial_load_N_max=round(float(FnW.max()) * math.sin(R_(3.0)), 2),
                    note="pull-out with mu_s 0.12 (440C in Ti, dry after press); retaining compound 15 MPa shear on the 3 mm engagement")

# ---------------- 9. per-part skin distance (taken poses; contact poses attributed) ----------------
def part_skin(Zx, nm):
    names = list(Zx["PDnames"]); PD = Zx["PD"]; tk_ = Zx["taken"]; whys = Zx["whys"]; poses = Zx["poses"]; kin = Zx["kin_ok"]
    out = {}
    for j, n_ in enumerate(names):
        v = PD[tk_, j]
        if np.isfinite(v).any():
            i = np.nonzero(tk_)[0][int(np.nanargmin(v))]
            out[n_] = dict(min_mm=round(float(np.nanmin(v)), 3), lt0p3=int(np.nansum(v < 0.3)), lt1=int(np.nansum(v < 1.0)), lt2=int(np.nansum(v < 2.0)),
                           at=dict(kind="clip" if Zx["kind"][i] else "ws", plane=float(poses[i, 0]), elev=float(poses[i, 1]), axial=float(poses[i, 2])))
    cp = [i for i in np.nonzero(kin & ~tk_)[0] if whys[i] in ("contact", "skin")]
    att = []
    for i in cp:
        neg = {names[j]: round(float(PD[i, j]), 2) for j in range(len(names)) if np.isfinite(PD[i, j]) and PD[i, j] < 0}
        att.append(dict(plane=float(poses[i, 0]), elev=float(poses[i, 1]), axial=float(poses[i, 2]), kind="clip" if Zx["kind"][i] else "ws", parts=neg))
    return dict(taken=out, contact_poses=att)
res["skin_" + TAG] = part_skin(g, TAG)
if ZH is not None: res["skin_held"] = part_skin({k: ZH[k] for k in ZH.files}, "held")

# ---------------- exports ----------------
prof = FF["C2"] - (FF["C2"] @ u2)[:, None] * u2
nrm = []
for j in range(len(ts)):
    tg = np.gradient(prof, ts, axis=0)[j]; nn = unit(np.cross(u2, tg)); nn = nn if nn @ prof[j] > 0 else -nn; nrm.append(prof[j] - RR * nn)
nrm = np.array(nrm)
with open(os.path.join(SP, f"lobe_polar_{TAG}.csv"), "w") as fh:
    fh.write("t_deg_q2_past_onset,dK_deg,phi_crank_deg,pitch_az_deg,pitch_r_mm,profile_az_deg,profile_r_mm,pressure_angle_deg\n")
    for j in range(0, len(ts), 4):
        pa_ = D(math.atan2(prof[j] @ FF["by"], prof[j] @ FF["bx"])); qa = D(math.atan2(nrm[j] @ FF["by"], nrm[j] @ FF["bx"]))
        fh.write(f"{D(ts[j]):.3f},{D(kks[j]):.3f},{D(abs(phs[j])):.3f},{pa_:.3f},{np.linalg.norm(prof[j]):.4f},{qa:.3f},{np.linalg.norm(nrm[j]):.4f},{FF['pa'][j]:.2f}\n")
spec = dict(frame="model rigid frame = link 1b at q = 0 with K on stop A (= link 1a's frame at K 0), mm from GH",
            u1=u1.tolist(), u2=u2.tolist(), u3=u3.tolist(), uK=uK.tolist(), dR_crank_axis=dR.tolist(), crank_pivot_PV=PV.tolist(), nose_centre_rest=C0.tolist(),
            nose_axis_rest=unit(C0).tolist(), nose_r_flank=ROLL_R, nose_end_radius_from_GH=float(np.linalg.norm(C0)) - 1.25, lug_shell_radii=[float(np.linalg.norm(C0)) - 1.5, float(np.linalg.norm(C0)) + 1.5], arm_shell_radii=[float(np.linalg.norm(C0)) + 1.65, float(np.linalg.norm(C0)) + 4.65], arm_polyline=g["armPts"].tolist(), lug_polyline=g["lugPts"].tolist(), f=f.tolist(), fK=fK,
            crank_sense_sig=sig, K_sense_sp=sp, g_dK_per_dphi=gg, follower_centre_onset=FF["F0"].tolist(), follower_axis=dR.tolist(),
            lobe_polar_x=FF["bx"].tolist(), lobe_polar_y=FF["by"].tolist(), lobe_band_u2_levels=[f2 + 6.2, f2 + 9.2], flank_sketch_frame=res["flank"]["sketch_frame"],
            flank_mid_plane_h=h0, q2_onset_deg=res["law"]["q2_onset_deg"], dK_lim_deg=res["dK_lim_deg"])
json.dump(spec, open(os.path.join(SP, f"spec_points_{TAG}.json"), "w"), indent=1)
# the slaved coordinate for judge/dynamics.py (build.json "slaved"): K = law(q2), force closure
ttab = np.radians(np.arange(0, D(t_lim) + 1e-9, 0.5))
law_x = [round(D(q2hi - t), 4) for t in ttab][::-1]; law_y = [round(float(sp * D(np.interp(t, ts_l, dKl_abs))), 4) for t in ttab][::-1]
json.dump(dict(slaved=["l1a", "l1b"], driver=["l1b", "l2"], x_key="q.1", y_key="knuckle.dK", law_x_deg=law_x, law_y_deg=law_y, rest_y_deg=0.0, closure="force",
               drive_groups={"crank": "l1b"}, note="law in the model's convention (q2 deg, dK deg signed by the K sense); the CAD's build.json must map its own frame keys"),
          open(os.path.join(SP, f"slaved_law_{TAG}.json"), "w"), indent=1)
json.dump(res, open(os.path.join(SP, f"results_{TAG}.json"), "w"), indent=1, default=float)
print(json.dumps({k: v for k, v in res.items() if k not in ("flank_arcs", "skin_" + TAG, "skin_held", "model_clear_past_lim", "follower_options", "flank_curvature_taken")}, default=float))
print("n arcs", len(arcs), "max err", max(a["err_mm"] for a in arcs))
