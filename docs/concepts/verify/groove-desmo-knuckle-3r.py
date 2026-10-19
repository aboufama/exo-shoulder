"""Independent verifier (skeptic) of groove-desmo-knuckle-3r (the lead's slaved roller-flank knuckle made positive both
ways: a track groove under hub 2's cap ring + an O1.5 dowel on the crank's short arm; an MR52 roller in a two-walled slot
in link 1a's boss at hub K; clock spring and stop A deleted).

The claim's model (docs/concepts/models/groove-desmo-knuckle-3r.py, GD_CELL=lead) is loaded UNCHANGED and worn by its own
claim protocol (GD._frozen_model: fit Bench(60,160) fast -> shape frozen, the claim's _groove copied -> worn on
Bench(110,360) exact / held out). No other model is imported in this process (the parents patch shared core modules).
Checks on every TAKEN pose of the worn bench, ADDED here:

  1. ROLLER-FLANK (the round's roller-flank verifier, copied, PA gate 43): roller centre carried by the crank (member 9)
     on link 1a's synthesised path within 0.5 mm; roller vs lug + the slot's outer wall >= ROLL_R; K inside [0, dK_lim];
     K sense; crank / horn pressure angles at the pose.
  2. FRAME CONSISTENCY: J2's axis carried by link 1b and link 2, J3's by link 2 and member 3 (< 0.05 deg); K read from
     the frames equals the model's dK.
  3. GROOVE IN 3-D (new; the claim's groove gates are planar, in hub 2's plane, with the dowel's azimuth drift ignored and
     the crank axis taken parallel to hub 2's axis). The crank turns about dR, a line through GH tilted g0 from u2, so the
     dowel moves on a tilted circle. From the worn frames (member 9 carries the dowel's rest point F0 and axis u2):
       a. pitch radius about hub 2's axis inside the groove window [R_LO, R_HI] on every taken pose (true, with drift);
       b. axial travel of the dowel along hub 2's axis (the groove is 1.5 deep, the dowel 2 long);
       c. dowel tilt against hub 2's axis, resolved ACROSS the groove's local direction: lateral run-out over the 1.5-mm
          engagement vs the 0.02-mm groove clearance (binding) -> the clearance (and K slop) the real groove needs;
       d. the groove's REAL pressure angle from the 3-D dowel velocity (rotation about dR) and the cap's rotation rate
          read from the frames (dq2/dK regressed over the taken rise poses: the with/against arrangement checked, not
          assumed); gate PA_GROOVE = 43 - atan(0.1) = 37.29;
       e. the groove centreline in the cap frame (dwell arc + rise over the taken q2 range): self-clearance between parts
          of the channel (the channels must not merge: >= GROOVE_W + 0.5 wall), and the frame-read cap-frame dowel
          points on it (<= 0.05 mm).
  4. FOLD MARGIN (docs/concepts/verify/roller-longdyad-knuckle-3r.py th_margin, copied).
  5. ENVELOPE (--env): the slot outer wall's first row (0.3 mm beyond the roller) is deleted by the claim's chord filter
     (projection onto the lug sphere shrinks the chord below ROLL_R + 0.3); rebuilt here at ROLL_R + 0.3 (filter at
     ROLL_R + 0.05) and the lug's flank-edge strip at ROLL_R + 0.6 behind the inner flank, added to rigid horn / contact /
     strap HORN before the fit, so the worn model checks them.
  6. CONTINUITY FLOOD (--flood: connected_report, unchanged).
Corrected gap: poses failing 1-3 dropped.

    GD_CELL=lead CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/groove-desmo-knuckle-3r.py wear <bench|held|fit> <out.json> [--flood] [--env] [--truewin]
    (--truewin: the drive's stop B moved to where the 3-D crest meets the claim's own window R_HI 8.44, before the fit:
     the honest re-run of the claim protocol with the corrected groove-fit limiter)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
os.environ.setdefault("GD_CELL", "lead")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


GD = _load("groove_desmo_claim_v", os.path.join(REPO, "docs", "concepts", "models", "groove-desmo-knuckle-3r.py"))
RF, S, PK, CB = GD.RF, GD.S, GD.PK, GD.CB
unit = S.unit; D2R = math.pi / 180
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "groove-desmo-knuckle-3r.json")))
BEST = ROW["best_params"]; BEST = json.loads(BEST) if isinstance(BEST, str) else BEST
BEST = {k: v for k, v in BEST.items() if k not in ("cell", "roller", "groove")}
PA_MAX, CLOSE_TOL, ROLL_R = 43.0, 0.5, GD.ROLL_R
ENGAGE, GROOVE_CLR, WALL_MIN = 1.5, GD.GROOVE_W - GD.DOWEL_D, 0.5


def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(unit(a), unit(b))), -1, 1))))


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def _rot_angle(R, u):
    e = unit(np.cross(u, [0.3, 0.5, 0.8])); Re = R @ e
    return math.atan2(float(np.cross(e, Re) @ u), float(e @ Re)), _ang(R @ u, u)


def taken_of(B): return [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]


# ---------------------------------------------------------------------------------------------------- 5. envelope
def add_envelope(M):
    g = M._scg; PV, dR, uK, sp, sig, gg, cc = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0)
    C0 = np.asarray(M._viz_rod["roller"], float); R0 = float(np.linalg.norm(C0)); rL = R0 - 1.5
    kk = np.arange(0.0, float(g["dK_lim"]) + 1e-9, math.radians(0.25))
    Rk = S.rotm(uK, sp * kk); Rcg = S.rotm(dR, sig * RF.phi_of(kk, gg, cc))
    Cg = np.einsum("nij,j->ni", Rcg, C0 - PV) + PV; P1 = np.einsum("nij,nj->ni", Rk, Cg)
    tree = cKDTree(P1); add = []
    m1, lug = M.rigid["horn"]; mid = lug + 1.5 * unit(lug)
    # tangent-plane offsets on both sides of the path, projected onto the lug sphere at the roller-centre radius
    T = np.gradient(P1, axis=0); T = T / np.maximum(np.linalg.norm(T, axis=1)[:, None], 1e-12)
    Nn = np.cross(unit(P1), T)
    for s_ in (+1.0, -1.0):
        for off in (ROLL_R + 0.3, ROLL_R + 0.6):
            Q = P1 + s_ * off * Nn; Q = unit(Q) * R0
            dq = tree.query(Q)[0]; Q = Q[dq >= ROLL_R + 0.05]
            if len(Q) == 0: continue
            # keep only where the claim has metal on that side within 2 mm (do not invent walls the design does not have)
            dm = cKDTree(mid).query(Q)[0]; Q = Q[dm <= 2.0]
            rax = np.linalg.norm(Q - (Q @ uK)[:, None] * uK, axis=1); Q = Q[rax >= S.HUB_R + 0.5]
            add.append(unit(Q) * rL)
    E = np.concatenate(add) if add else np.zeros((0, 3))
    if len(E):
        M.rigid["horn"] = (m1, np.concatenate([lug, E]))
        M.contact.append((1, E + S.T_LINK * unit(E)))
        mH, XH = M.strap["HORN"]; M.strap["HORN"] = (mH, np.concatenate([XH, E + 1.5 * unit(E)]))
        g["lugM"] = np.concatenate([g["lugM"], E + 1.5 * unit(E)])
    M._env_info = dict(edge_pts=int(len(E)))


# ---------------------------------------------------------------------------------------------------- 1. roller-flank
def roller_checks(M, Mfit, B, taken):
    g = M._scg; tab = Mfit._cam_table
    PV, dR, uK, sp, sig, gg, cc = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0)
    C0 = np.asarray(M._viz_rod["roller"], float); lugM = g["lugM"]; tL = cKDTree(lugM)
    dK = np.asarray(M.dK, float); ec, dl, pac, pah = [], [], [], []; bad = {}
    for i in taken:
        k = abs(float(dK[i])); ph = sig * float(RF.phi_of(k, gg, cc))
        R1, t1 = M.T(1, i); R9, t9 = M.T(9, i)
        Cw = R9 @ C0 + t9
        Cb = S.rotm(dR, ph)[0] @ (C0 - PV) + PV; Ca = S.rotm(uK, sp * k)[0] @ Cb; Cexp = R1 @ Ca + t1
        e = float(np.linalg.norm(Cw - Cexp)); ec.append(e)
        d = float(tL.query(R1.T @ (Cw - t1))[0]); dl.append(d)
        a = float(np.interp(math.degrees(k), tab["k"], tab["pa_crank"])); h = float(np.interp(math.degrees(k), tab["k"], tab["pa_horn"]))
        pac.append(a); pah.append(h); rs = []
        if e > CLOSE_TOL: rs.append("closure")
        if d < ROLL_R - 1e-6: rs.append("roller_in_lug")
        if k > float(g["dK_lim"]) + 1e-9: rs.append("beyond_flank")
        if abs(float(dK[i])) > math.radians(0.1) and np.sign(dK[i]) != sp: rs.append("wrong_sense")
        if a > PA_MAX or h > PA_MAX: rs.append("pressure")
        if rs: bad[i] = rs
    tk = np.array(taken, int); kmax = float(np.abs(dK[tk]).max()) if len(tk) else 0.0
    return bad, dict(closure_max_mm=round(max(ec), 4) if ec else None, roller_lug_min_mm=round(min(dl), 3) if dl else None,
                     roller_lug_max_mm=round(max(dl), 3) if dl else None, pa_crank_max=round(max(pac), 1) if pac else None,
                     pa_horn_max=round(max(pah), 1) if pah else None, dK_taken_max_deg=round(math.degrees(kmax), 2),
                     dK_lim_deg=round(math.degrees(float(g["dK_lim"])), 2), why_lim=g.get("why_lim"), drive_idle=bool(math.degrees(kmax) < 30.0))


# ---------------------------------------------------------------------------------------------------- 2. frames
def frame_checks(M, taken):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; bad = {}; fr = dict(j2_axis=0.0, j3_axis=0.0, k_from_frames=0.0)
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i); R3, _ = M.T(3, i)
        e2 = _ang(R1b @ u2, R2 @ u2); e3 = _ang(R2 @ u3, R3 @ u3)
        kf, kax = _rot_angle(R1.T @ R1b, uK); ekf = abs(math.degrees(kf - float(M.dK[i])))
        fr["j2_axis"] = max(fr["j2_axis"], e2); fr["j3_axis"] = max(fr["j3_axis"], e3); fr["k_from_frames"] = max(fr["k_from_frames"], ekf, kax)
        if e2 > 0.05 or e3 > 0.05 or ekf > 0.05: bad[i] = ["frames"]
    return bad, {k: round(v, 4) for k, v in fr.items()}


# ---------------------------------------------------------------------------------------------------- 3. groove in 3-D
def groove_checks(M, taken):
    gd = M._groove; g = M._scg; D = M.D
    u2 = unit(np.asarray(gd["u2"], float)); F0 = np.asarray(gd["F0"], float); dR = unit(np.asarray(g["dR"], float)); PV = np.asarray(g["PV"], float)
    sig, gg, cc, sp = float(g["sig"]), float(g["g"]), float(g.get("c", 0.0)), float(g["sp"])
    mh, cen2, ax2 = M.cyl["hub2"]; ax2 = unit(np.asarray(ax2, float)); cen2 = np.asarray(cen2, float)
    lin = float(np.linalg.norm(np.cross(cen2, ax2)))            # hub 2's axis through GH?
    ex = unit(np.asarray(gd["ex"], float)); ey = np.cross(u2, ex)
    dK = np.asarray(M.dK, float)
    rows = []
    for i in taken:
        R1b, t1b = M.T(7, i); R2, t2 = M.T(2, i); R9, t9 = M.T(9, i)
        Fw = R9 @ F0 + t9; aw = R9 @ u2
        Fb = R1b.T @ (Fw - t1b); ab = R1b.T @ aw                  # link 1b frame (hub 2's housing)
        Gc = R2.T @ (Fw - t2)                                       # cap (link 2) frame
        q2, _ = _rot_angle(R1b.T @ R2, u2)
        r = float(np.linalg.norm(Fb - (Fb @ u2) * u2)); h = float(Fb @ u2)
        rows.append(dict(i=i, K=abs(float(dK[i])), q2=q2, r=r, h=h, tilt=_ang(ab, u2), Fb=Fb, ab=ab, Gc=Gc))
    if not rows: return {}, dict(n=0)
    K = np.array([x["K"] for x in rows]); q2 = np.unwrap(np.array([x["q2"] for x in rows]))
    rise = K > math.radians(0.5)
    # 3a/b: true pitch radius and axial height over taken poses (incl. the dowel's drift)
    rr = np.array([x["r"] for x in rows]); hh = np.array([x["h"] for x in rows])
    # 3d: cap rate dq2/dK on the rise, read from the frames
    if rise.sum() >= 5:
        A = np.vstack([K[rise], np.ones(rise.sum())]).T; (s_rate, q_on), res_, *_ = np.linalg.lstsq(A, q2[rise], rcond=None)
        fit_err = float(np.max(np.abs(A @ np.array([s_rate, q_on]) - q2[rise])))
    else:
        s_rate, q_on, fit_err = float("nan"), float("nan"), float("nan")
    # analytic dowel path over the drive grid (rotation about dR through PV) - validated against the frame-read points
    kg = np.arange(0.0, float(g["dK_lim"]) + 1e-9, math.radians(0.25))
    def Fk(k):
        ph = sig * float(RF.phi_of(k, gg, cc)); return S.rotm(dR, ph)[0] @ (F0 - PV) + PV
    Fg = np.array([Fk(k) for k in kg]); ag = np.array([S.rotm(dR, sig * float(RF.phi_of(k, gg, cc)))[0] @ u2 for k in kg])
    val = max(float(np.linalg.norm(x["Fb"] - Fk(x["K"]))) for x in rows)
    # 3d: pressure angle on the grid: vF = dF/dK (3-D), groove tangent (1b frame) = vF - s_rate * (u2 x F), walls // u2
    vF = np.gradient(Fg, kg, axis=0)
    tg = vF - s_rate * np.cross(u2[None], Fg)
    tg_h = tg - (tg @ u2)[:, None] * u2[None]
    nrm = np.cross(u2[None], tg_h); nrm = nrm / np.maximum(np.linalg.norm(nrm, axis=1)[:, None], 1e-12)
    pa = np.degrees(np.arccos(np.clip(np.abs(np.sum(nrm * vF, 1)) / np.maximum(np.linalg.norm(vF, axis=1), 1e-12), 0, 1)))
    # the claim's planar formula on the same grid (for reference) is in M._sc_info['groove']
    kt = float(K.max()); jt = int(np.searchsorted(kg, kt + 1e-12))
    pa_taken = float(pa[1:max(jt, 2)].max()) if jt > 1 else None
    # 3c: tilt across the groove direction (rise: groove tangent; dwell: base-circle tangent - tilt is 0 there)
    tilt_dir = ag - (ag @ u2)[:, None] * u2[None]                     # horizontal tilt vector (sin tilt)
    t_unit = tg_h / np.maximum(np.linalg.norm(tg_h, axis=1)[:, None], 1e-12)
    across = np.abs(np.sum(tilt_dir * nrm, 1))                          # sin(tilt) across the groove
    runout = ENGAGE * across                                            # lateral run-out over the engagement (mm)
    runout_taken = float(runout[:max(jt, 1)].max())
    rg = np.linalg.norm(Fg - (Fg @ u2)[:, None] * u2[None], axis=1); hg = Fg @ u2
    # 3e: the groove centreline in the cap frame over the taken q2 range: dwell arc (phi 0) + rise
    q2min, q2max = float(q2.min()), float(q2.max())
    # cap-frame point of a 1b-frame point X at cap angle q: Rot(u2, -q) X (link 2 frame relative to its rest)
    sgn = np.sign(s_rate) if np.isfinite(s_rate) else 1.0
    q_dw = np.arange(q2min, q2max + 1e-9, math.radians(0.5)) if sgn > 0 else np.arange(q2min, q2max + 1e-9, math.radians(0.5))
    dwell = np.array([S.rotm(u2, -q)[0] @ F0 for q in q_dw if (q - q_on) * sgn <= 0])
    riseC = np.array([S.rotm(u2, -(q_on + s_rate * k))[0] @ Fk(k) for k in kg[:max(jt, 1)]])
    Cline = np.concatenate([x for x in (dwell[::-1] if len(dwell) else dwell, riseC) if len(x)])   # far dwell end -> onset -> rise top
    seg = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(Cline, axis=0), axis=1))]
    Ch = Cline - (Cline @ u2)[:, None] * u2[None]
    dmin = 99.0
    for j in range(len(Ch)):
        far = np.abs(seg - seg[j]) > 3.0
        if far.any(): dmin = min(dmin, float(np.linalg.norm(Ch[far] - Ch[j], axis=1).min()))
    # frame-read cap-frame points vs the centreline (relative to link 2's rest: Gc is in link 2's member frame)
    on_curve = float(max(cKDTree(Cline).query(x["Gc"])[0] for x in rows))
    span = math.degrees(abs(q2max - q2min))
    # 3f: link 2's strap vs the TRUE dowel and short arm (3-D crank rotation about dR, boss point carried by the crank),
    #     projected onto hub 2's plane in link 1b's frame; the claim's strap model (r >= 6 along the exit, half-width 5)
    Pb0 = u2 * float(gd["lvl2"]) + (float(gd["d"]) - 5.0) * ex
    mh3, cen3, _ = M.cyl["hub3"]
    l2c, l2a = [], []
    def strap_d(X, e, nrm_):
        a_ = float(X @ e); l_ = abs(float(X @ nrm_))
        if a_ < GD.BOSS2_R: return math.hypot(GD.BOSS2_R - a_, max(0.0, l_ - GD.L2_HALF)) if l_ > GD.L2_HALF else GD.BOSS2_R - a_
        return l_ - GD.L2_HALF
    for x in rows:
        i = x["i"]; R1b, t1b = M.T(7, i); Rh, th_ = M.T(mh, i); R3_, t3_ = M.T(mh3, i)
        c2w = Rh @ cen2 + th_; c3w = R3_ @ np.asarray(cen3, float) + t3_
        v = R1b.T @ (c3w - c2w); v = v - (v @ u2) * u2; e = np.array([float(v @ ex), float(v @ ey)]); e = e / np.linalg.norm(e); nrm_ = np.array([-e[1], e[0]])
        ph = sig * float(RF.phi_of(x["K"], gg, cc)); Rc = S.rotm(dR, ph)[0]
        Fp = x["Fb"]; Bp = Rc @ (Pb0 - PV) + PV
        f2 = np.array([float(Fp @ ex), float(Fp @ ey)]); b2 = np.array([float(Bp @ ex), float(Bp @ ey)])
        cl = strap_d(f2, e, nrm_) - GD.DOWEL_D / 2
        for t_ in np.linspace(0, 1, 9): cl = min(cl, strap_d(f2 + t_ * (b2 - f2), e, nrm_) - GD.ARM_W / 2)
        l2c.append(cl); l2a.append(math.degrees(math.atan2(e[1], e[0])))
        x["l2"] = cl
    bad = {}
    for j, x in enumerate(rows):
        rs = []
        if x["r"] < GD.R_LO - 1e-6 or x["r"] > GD.R_HI + 1e-6: rs.append("groove_window")
        if x["l2"] < GD.CLEAR_L2: rs.append("l2_true")
        if rs: bad[x["i"]] = rs
    # stroke at which the TRUE crest reaches the window (the claim's own stop B rule) and at a 0.4-mm outer wall
    def k_at(rlim):
        j = np.nonzero(rg > rlim + 1e-9)[0]; return round(math.degrees(float(kg[j[0] - 1])), 2) if len(j) else round(math.degrees(float(kg[-1])), 2)
    n_over_04 = int(sum(1 for x in rows if x["r"] > GD.CAP_R - 0.4 - GD.GROOVE_W / 2 + 1e-6))
    gpa_fail = pa_taken is not None and pa_taken > GD.PA_GROOVE + 1e-6
    out = dict(n=len(rows), n_rise=int(rise.sum()), hub2_axis_offset_from_GH_mm=round(lin, 4),
               dq2_dK_frames=round(float(s_rate), 4), q_onset_deg=round(math.degrees(float(q_on)), 2), law_fit_err_deg=round(math.degrees(fit_err), 4),
               crank_axis_tilt_from_u2_deg=round(_ang(dR, u2), 2), dowel_path_vs_frames_mm=round(val, 4),
               pitch_r_taken=[round(float(rr.min()), 3), round(float(rr.max()), 3)], window=[round(GD.R_LO, 2), round(GD.R_HI, 2)],
               pitch_r_grid=[round(float(rg.min()), 3), round(float(rg.max()), 3)],
               axial_travel_taken_mm=round(float(hh.max() - hh.min()), 3), axial_travel_grid_mm=round(float(hg.max() - hg.min()), 3),
               tilt_taken_max_deg=round(max(x["tilt"] for x in rows), 2),
               runout_across_groove_taken_mm=round(runout_taken, 3), groove_clearance_mm=round(GROOVE_CLR, 3),
               groove_width_needed_mm=round(GD.DOWEL_D + max(GROOVE_CLR, runout_taken + 0.005), 3),
               slop_K_deg_needed=round(math.degrees(gg * (max(GROOVE_CLR, runout_taken + 0.005) / 2) / max(float(M.D.p["s_arm"]), 1e-9)
                                       + 0.014 / max(float(M.D.p["r_c"]), 1.0)), 2),
               pa_groove_3d_taken_max=round(pa_taken, 2) if pa_taken is not None else None,
               pa_groove_3d_grid_max=round(float(pa[1:].max()), 2) if len(pa) > 1 else None, pa_groove_gate=round(GD.PA_GROOVE, 2),
               pa_groove_claim=(M._sc_info.get("groove") or {}).get("pa_groove_max") if hasattr(M, "_sc_info") else None,
               cap_q2_span_deg=round(span, 1), centreline_self_clear_mm=round(dmin, 3), centreline_rule_mm=GD.GROOVE_W + WALL_MIN,
               cap_points_on_centreline_mm=round(on_curve, 3), groove_pa_fail=bool(gpa_fail),
               channels_merge=bool(dmin < GD.GROOVE_W + WALL_MIN),
               stroke_true_window_deg=k_at(GD.R_HI), stroke_true_wall04_deg=k_at(GD.CAP_R - 0.4 - GD.GROOVE_W / 2), n_taken_over_wall04=n_over_04,
               n_taken_over_window=int(sum(1 for x in rows if x["r"] > GD.R_HI + 1e-6)),
               l2_true_min_mm=round(float(min(l2c)), 3), l2_true_lt1=int(sum(1 for c in l2c if c < GD.CLEAR_L2)), l2_exit_az_abs_min=round(float(min(abs(a) for a in l2a)), 1))
    return bad, out


# ---------------------------------------------------------------------------------------------------- 4. fold margin
def th_margin(M, B, taken):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK
    a1 = math.degrees(D.a1) if D.a1 < 4 else D.a1; a2 = math.degrees(D.a2) if D.a2 < 4 else D.a2; rows = []
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(M.dK[i])) > 1e-6
        rows.append((min(_dm(th, b1, c), _dm(th, a1e, a2e)) if forced else _dm(th, a1, a2), forced, i, th))
    if not rows: return dict(min=None)
    own = [r[0] for r in rows]; lo = min(rows)
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)), forced=int(sum(r[1] for r in rows)),
                lowest=dict(own=round(lo[0], 3), forced=bool(lo[1]), kind=B.kind[lo[2]], **{k: B.poses[lo[2]][k] for k in ("plane", "elev", "axial")}))


# ---------------------------------------------------------------------------------------------------- protocol
def wear(P, which="bench", flood=False, env=False, truewin=False):
    if env:
        orig = GD.GDModel._rod_metal
        def _rm(self):
            orig(self); add_envelope(self)
        GD.GDModel._rod_metal = _rm
    if truewin:                                                         # stop B moved to where the TRUE crest meets the window
        orig2 = GD.GDModel._rod_metal
        def _rm2(self):
            orig2(self)
            gd = self._groove; g = self._scg
            if not gd: return
            u2 = unit(np.asarray(gd["u2"], float)); F0 = np.asarray(gd["F0"], float); dR = unit(np.asarray(g["dR"], float)); PV = np.asarray(g["PV"], float)
            kgr = np.asarray(g["kgrid"], float)
            F = np.array([S.rotm(dR, float(g["sig"]) * float(RF.phi_of(k, g["g"], g.get("c", 0.0))))[0] @ (F0 - PV) + PV for k in kgr])
            rr_ = np.linalg.norm(F - (F @ u2)[:, None] * u2[None], axis=1); j = np.nonzero(rr_ > GD.R_HI + 1e-9)[0]
            if len(j) and float(kgr[max(j[0] - 1, 0)]) < float(g["dK_lim"]):
                g["dK_lim"] = float(kgr[max(j[0] - 1, 0)]); g["why_lim"] = "groove-fit-3d"
                self._sc_info.update(dK_lim=round(math.degrees(g["dK_lim"]), 2), why_lim="groove-fit-3d")
        GD.GDModel._rod_metal = _rm2
    nc, nw = {"bench": (110, 360), "held": (-1, -1), "fit": (60, 160)}[which]
    fit, M1, M, B, r = GD._frozen_model(dict(P), nc, nw)
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    taken = taken_of(B)
    b1, o1 = roller_checks(M, M1, B, taken)
    b2, o2 = frame_checks(M, taken)
    b3, o3 = groove_checks(M, taken)
    bad = {}
    for bb in (b1, b2, b3):
        for i, rs in bb.items(): bad.setdefault(i, []).extend(rs)
    why = {}
    for rs in bad.values():
        for x in set(rs): why[x] = why.get(x, 0) + 1
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    corr = {k: B.report()[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    ok = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(len(B.idx))])
    ov = ws & (elev >= 140)
    corr_ovh = dict(ws=int(ov.sum()), taken=int((ov & ok).sum()))
    B.res = res0
    if o3.get("groove_pa_fail") or o3.get("channels_merge"):
        corr_hard = dict(corr, note="groove gate failed in 3-D: the drive's stroke must be cut; see groove")
    else:
        corr_hard = None
    aud = PK.audit(M, B)
    out = dict(which=which, mode=B.mode, n=len(B.idx), fit_fast=fit, frozen=rep, why=r.get("why"), parts_ib14=r.get("parts_ib14"),
               audit={k: aud.get(k) for k in ("gap_near1", "gap_near2", "near_touch_min_mm", "overhead140") if k in aud},
               l2=getattr(M, "_l2", None), roller=o1, frames=o2, groove=o3, th_margin=th_margin(M, B, taken),
               poses_failing=len(bad), why_failing=why, failing_ids=sorted(bad)[:60], corrected=corr, corrected_overhead=corr_ovh,
               corrected_hard=corr_hard, env=getattr(M1, "_env_info", None), sc_info={k: (M1._sc_info or {}).get(k) for k in ("dK_lim", "why_lim", "groove", "wall2")})
    if flood:
        MECH = _load("minarc_mech_for_groove_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
        t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "wear":
        which, path = sys.argv[2], sys.argv[3]
        t = time.time(); out = wear(dict(BEST), which, "--flood" in sys.argv, "--env" in sys.argv, "--truewin" in sys.argv)
        out.update(secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", env_flag="--env" in sys.argv, truewin="--truewin" in sys.argv, params=BEST)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps({k: out.get(k) for k in ("which", "mode", "fit_fast", "frozen", "corrected", "corrected_overhead", "poses_failing", "why_failing",
                                                   "audit", "l2", "roller", "frames", "groove", "th_margin", "env", "connected", "secs")}, default=float))
