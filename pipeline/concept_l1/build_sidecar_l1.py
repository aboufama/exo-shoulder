"""L1 keep-out CAD of the generation-6 winner sidecar-longdyad-knuckle-3r (verified v_gap 18.91 / score 93.12 on Bench(110,360)
exact frozen, held out 22.67: docs/concepts/sidecar-longdyad-knuckle-3r.md; config = docs/concepts/rows/sidecar-longdyad-knuckle-3r.json
best_params = the verifier harness' BEST) -> a judge-ready design dir pipeline/full-exo/designs/<out>/ (exo.glb, clips.json,
workspace.json, design.json, parts_full.json, build.json).

Derived from build_geneva_l1.py (gen 5) and build_minarc_l1.py (gen 4 / 4b), which are IMPORTED (minarc) or copied from (geneva),
never edited. What changes for this morphology:
  * the model is the claim's SCModel (docs/concepts/models/sidecar-longdyad-knuckle-3r.py, loaded through the verifier harness
    docs/concepts/verify/sidecar-longdyad-knuckle-3r.py, config BEST, unchanged), fit on Bench(60,160) FAST = the frozen
    protocol's hand-over: the L1 carries the shape the verifier wore on Bench(110,360) exact;
  * K is SLAVED (3 encoders J1 / J2 / J3; K never read): past the onset q2hi the lin law dK = kK (q2 - q2hi) sets K; the drive's
    own range ends at |dK| = dK_lim (43.0 deg, ROD-hub2) where the physical q2 dowel stop B sits - every pose past it is not taken
    (as the model's _truncate does on every bench);
  * the SIDECAR drive is POSED, not frozen on link 1b: the bell crank (group "dk", the model's member 9) turns about its pivot
    axis dR on link 1b by phi(|dK|) and the rod (group "dr", member 8) closes the RSSR loop, both from the model's own RSSR table
    (SCModel._sc_pose) evaluated at the K opening read off each frame's link 1a / 1b frames - nothing free;
  * drive metal at its real envelope: the hub-2 rim lobe (sector in a 3 mm band of hub 2's upper boss, r = r_lobe + s_arm |phi|),
    the crank boss (O10 x 6, bore O3.2 for the O3 pivot pin, two MR63ZZ inside) stacked on link 1b + 0.15, its long arm 6 x 3 at
    the model's own stepped levels to the ball at La, the O3 pivot pin + DIN 6799 clip (link 1b), the O3 Ti rod and its two M2
    ball-link sockets (O7 envelope, 1 mm neck over the arm / lug top), the horn lug of link 1a (6 x 3 at hl above hub K's face,
    r_h + 4 long) on an L-bracket from K's lower plate (clear of K's upper boss by 0.65 mm radially);
  * stops: K = an opposed O3 dowel pair between stop A (0) and stop B (the model's a1max); J2 = one O3 dowel between q2lo and the
    drive-range stop B; gen-4b fixes carried over (E strap capped, knee stop tooth at 180 - ang_min, K slots clear of link 1a).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/build_sidecar_l1.py [--out l1_sidecar-longdyad] [--jobs 2] [--no-clips]
"""
import argparse, json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
os.environ.pop("CB_EXACT", None)                     # the frozen protocol's fit bench is FAST (Bench(60,160))
import build_minarc_l1 as MIN                                                   # noqa: E402  (gen-4/4b L1 builder, imported unchanged)
BASE = MIN.BASE; CB, REF = BASE.CB, BASE.REF

V = MIN._load("sidecar_verify_for_l1", os.path.join(REPO, "docs", "concepts", "verify", "sidecar-longdyad-knuckle-3r.py"))
SC = V.SC; S = SC.S; PK = SC.PK
ID = "sidecar-longdyad-knuckle-3r"
CROWN, UP, T_LINK, W_LINK, RUN = S.CROWN, S.UP, S.T_LINK, S.W_LINK, S.RUN
PLATE = MIN.PLATE; unit = S.unit; TI, STEEL = BASE.TI, BASE.STEEL
ER, ZB, BOSS_H, RUNG = SC.ER, SC.ZB, SC.BOSS_H, SC.RUNG                         # M2 ball-link socket r, ball over the arm / lug top, crank boss, gap
NECK = 1.0                                                                      # socket underside over the arm / lug top (the stud's neck)
LOBE_Z = (UP + 0.5, UP + 3.5)                                                   # the lobe's 3 mm band in hub 2's upper boss (link 2)
LOBE_RIN = 6.0
PIN_R, BORE_R, CLIP_H = 1.5, 1.6, 0.9                                           # crank pivot pin O3 h6, boss bore O3.2 (keep-out), DIN 6799 RS 2.3 land
GROUPS = MIN.GROUPS + ((9, "dk"), (8, "dr"))
GRP_OF = {0: "base", 1: "l1a", 7: "l1b", 2: "l2", 3: "l3", 6: "l4", 5: "H", 9: "dk", 8: "dr"}


# ---------------------------------------------------------------------------------------------------- the verified model
class L1Model(SC.SCModel):
    """the claim's SCModel; once fitted (self._l1), the crank (9) / rod (8) frames come from the K opening read off the CURRENT
    member frames X[1], X[7] (so the clip / workspace swaps of BASE.swap_in pose the drive exactly), through the model's own
    RSSR table (_sc_pose)"""
    def T(self, m, i):
        if m in (8, 9) and getattr(self, "_l1", False):
            X7 = self.X[7][0]; c = getattr(self, "_l1c", None)
            if c is None or c[0] is not X7: self._l1c = (X7, self._drive_frames(self.X[1][0], X7))
            Rb, tb = self._l1c[1][m]; R7, t7 = self.X[7][0][i], self.X[7][1][i]
            return R7 @ Rb[i], R7 @ tb[i] + t7
        return super().T(m, i)

    def dK_of(self, X1, X7):
        from scipy.spatial.transform import Rotation as Rot
        RK = np.einsum("nji,njk->nik", X1, X7); bad = ~np.isfinite(RK).all(axis=(1, 2)); RK[bad] = np.eye(3)
        return Rot.from_matrix(RK).as_rotvec() @ self._scg["uK"]

    def _drive_frames(self, X1, X7):
        save = (self.dK, self._sc); self.dK = self.dK_of(X1, X7); self._sc = None
        try: self._sc_pose(); X = self._sc["X"]
        finally: self.dK, self._sc = save
        return X


def fit():
    """the claim's model on BEST, fit on Bench(60,160) FAST: the shape the verifier wore frozen"""
    B = CB.Bench(60, 160); P = SC._clamp(dict(SC.PARAMS, **V.BEST)); M = L1Model(B, P); r = M.run()
    a = PK.audit(M, B); r["gap_near1"] = a.get("gap_near1"); r["near_touch_min_mm"] = a.get("near_touch_min_mm")
    M._bench = (M.Q, M.s, M.RS, M.X, M.K, M.q); M._l1 = True; M._l1c = None
    return M, r


def chain(M, poses):
    """MIN.chain + the drive groups dk / dr + the drive-range stop: |dK| > dK_lim is not taken (J2's stop B dowel sits there)"""
    D = M.D; RS = np.array([S.scap(float(p[1])) for p in poses]); RH = np.array([S.humerus(p) for p in poses])
    Q = np.einsum("nji,njk->nik", RS, RH); q, ok, X1, X2, X3, s = D.ik(Q)
    X1b = D._X1b; dK = np.asarray(D._dK, float).copy(); st = np.asarray(D._state).copy(); m3e = np.asarray(D._m3e, float).copy()
    lim = float(M._scg["dK_lim"]); past = np.abs(dK) > lim + 1e-9; ok = ok & ~past
    Kn = D.knee(s)
    R123 = X3[0]; res = np.degrees(np.arccos(np.clip((np.einsum("nij,nij->n", R123, Q) - 1) / 2, -1, 1)))
    kok = Kn["ok"] & (np.abs(s[:, 2]) <= M.p["R_tol"])
    K = dict(q=np.degrees(q), qr=q, ok=ok, kok=kok, res=res, s=s, Q=Q, RS=RS, X={1: X1, 2: X2, 3: X3, 7: X1b}, Kn=Kn, dK=dK, state=st, m3e=m3e,
             qq=np.degrees(np.c_[q[:, :2], q[:, 2] + Kn["phi"], Kn["qa"], Kn["qb"], dK]), past_drive=past)
    n = len(Q); G = {"base": RS}; T = {"base": np.zeros((n, 3))}
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BASE.swap_in(M, K)
    try:
        for m, g in GROUPS:
            Gm = np.zeros((n, 3, 3)); Tm = np.zeros((n, 3))
            for j in range(n):
                if not (ok[j] and np.isfinite(Kn["th"][j])): Gm[j] = RS[j]; continue
                R, t = M.T(m, j); Gm[j] = RS[j] @ R; Tm[j] = RS[j] @ t
            G[g] = Gm; T[g] = Tm
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    K["G"], K["T"] = G, T
    return K


MIN.chain = BASE.chain = chain                                                  # the gen-3 / gen-4 drivers run this chain


# ---------------------------------------------------------------------------------------------------- law, window, drive geometry
def law_geom(M):
    """the slaved K: the lin law on its valid prefix, cut at the drive's own range; the J2 window (q2lo .. q2 stop B at dK_lim)
    and K's stops (A 0 .. B at a1max)"""
    D = M.D; P = D.p; L = D.law(); assert L.get("ok") and L["emb"] == "rod", L.get("emb")
    q0 = math.degrees(D._q2c[2]); sg = D.q2sgn
    rel = lambda x: ((x - q0 + 180) % 360 - 180) * sg
    q2lo, q2hi = D.q2_stops; ts = np.degrees(L["ts"]); dKl = np.degrees(np.abs(L["dK"])); lim = math.degrees(M._scg["dK_lim"])
    t_stop = float(np.interp(lim, dKl, ts)) if lim < dKl[-1] else float(ts[-1])
    q2B = q2hi + float(L["s_q"]) * t_stop
    r_lo, r_hi = sorted((rel(q2lo), rel(q2B))); assert r_lo - 1e-6 <= rel(q2hi) <= r_hi + 1e-6, (q2lo, q2hi, q2B)
    qa, qb = sorted((q0 + sg * r_lo, q0 + sg * r_hi))
    spK = MIN.stop_specs(M)["K"]
    return dict(J2=(math.radians(qa), math.radians(qb), dict(q2_stops_deg=[round(q2lo, 3), round(q2B, 3)], q2_onset_deg=round(q2hi, 3),
                                                             window_deg=[round(qa, 3), round(qb, 3)],
                                                             stop_B=f"the drive's own range: |dK| = dK_lim {lim:.2f} deg ({M._scg['why_lim']}) at t = {t_stop:.2f} deg past the onset")),
                K=spK, law=dict(kK=float(P["kK"]), s_q=float(L["s_q"]), q2hi_deg=round(q2hi, 3), t_stop_deg=round(t_stop, 3), dK_stop_deg=round(lim, 3),
                                law_end_t_deg=round(float(ts[-1]), 3), law_end_dK_deg=round(float(dKl[-1]), 3), why_end=L["why_end"],
                                pressure_angle_deg=round(float(np.degrees(np.max(L["pa"]))) if np.max(L["pa"]) < 3.2 else float(np.max(L["pa"])), 2)),
                L=L, ts_deg=ts, dK_deg=dKl)


def dK_of_q2(lg, q2_deg):
    """|dK| (deg) of the slaved K at J2 angle q2 (0 below the onset)"""
    t = ((np.asarray(q2_deg, float) - lg["law"]["q2hi_deg"] + 180) % 360 - 180) * lg["law"]["s_q"]
    return np.where(t > 0, np.interp(np.maximum(t, 0), lg["ts_deg"], lg["dK_deg"]), 0.0)


def drive_geom(M):
    """the claim's drive geometry (SCModel._rod_metal's own values: pivot, axis, arm levels, balls, horn frame)"""
    D = M.D; P = D.p; g = M._scg; uK = g["uK"]; dR, PV, tip0, H0 = g["dR"], g["PV"], g["tip0"], g["H0"]
    La, RH = float(P["La"]), float(P["r_h"]); zboss = float(PV @ dR)
    arm = M.rigid["crank"][1]; rs = np.arange(0.0, La + 1e-6, 2.0); arm = arm[-4 * len(rs):]
    lvl = np.array([float(arm[4 * j] @ dR) for j in range(len(rs))])
    sR = unit(tip0 - (tip0 @ dR) * dR); bnR = unit(np.cross(dR, sR))
    sK = unit(H0 - (H0 @ uK) * uK); bnK = unit(np.cross(uK, sK)); lvK = float(M.fK + float(P["hl"]))
    lev = float(M._sc_info["lev_L1b"])
    return dict(dR=dR, PV=PV, tip0=tip0, H0=H0, uK=uK, sR=sR, bnR=bnR, sK=sK, bnK=bnK, rs=rs, lvl=lvl, La=La, RH=RH, zboss=zboss,
                lvK=lvK, lev=lev, L_rod=float(np.linalg.norm(H0 - tip0)), sp=float(g["sp"]), kgrid=g["kgrid"], phig=g["phig"])


def tube(p0, ax, h0, h1, ro, ri, n=64):
    """O(2 ro) / O(2 ri) tube along ax from p0 + h0 ax to p0 + h1 ax (one watertight genus-1 solid)"""
    e, f = S.frame_of(ax); f = np.cross(ax, e); ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ring = lambda r: np.c_[r * np.cos(ang), r * np.sin(ang)]
    V2 = np.r_[ring(ro), ring(ri)]; F2 = []
    for i in range(n):
        j = (i + 1) % n; F2 += [[i, j, n + j], [i, n + j, n + i]]
    return MIN.extrude2d(V2, np.array(F2), p0, e, f, ax, h0, h1)


def lobe_mesh(M, lg, dg, n=80):
    """the hub-2 rim lobe on link 2's rotor (member-local home frame): outer edge r(t) = r_lobe + s_arm |phi(dK(t))| at the
    rotor angle that faces the crank pivot at q2 = q2hi + s_q t, t in [0, t_stop]; inner arc LOBE_RIN; band LOBE_Z over hub 2's face"""
    D = M.D; P = D.p; u2 = D.u[1]; c2 = D.c[1]; f2 = M.f[1]; H2 = c2 + f2 * u2
    e, f = S.frame_of(u2); f = np.cross(u2, e)
    zc = 0.5 * (LOBE_Z[0] + LOBE_Z[1]); hz = (H2 @ u2 + zc) / max(float(dg["dR"] @ u2), 0.2)
    w = dg["dR"] * hz - H2; w = w - (w @ u2) * u2; phiR = math.atan2(float(w @ f), float(w @ e)); d_ax = float(np.linalg.norm(w))
    ts = np.radians(np.linspace(0.0, lg["law"]["t_stop_deg"], n)); s_q = lg["law"]["s_q"]; q2hi = math.radians(lg["law"]["q2hi_deg"])
    dk = np.radians(np.interp(np.degrees(ts), lg["ts_deg"], lg["dK_deg"])); phi = np.interp(dk, dg["kgrid"], dg["phig"])
    r = float(P["r_lobe"]) + float(P["s_arm"]) * np.abs(phi)
    psi = phiR - (q2hi + s_q * ts)
    outer = np.c_[r * np.cos(psi), r * np.sin(psi)]; inner = np.c_[LOBE_RIN * np.cos(psi), LOBE_RIN * np.sin(psi)]
    V2 = np.r_[outer, inner]; F2 = []
    for i in range(n - 1): F2 += [[i, i + 1, n + i + 1], [i, n + i + 1, n + i]]
    m = MIN.extrude2d(V2, np.array(F2), H2, e, f, u2, LOBE_Z[0], LOBE_Z[1])
    return m, dict(r_lobe=float(P["r_lobe"]), r_at_stopB=round(float(r[-1]), 3), past_O20_skirt_mm=round(float(r[-1]) - S.HUB_R, 3),
                   sweep_deg=round(lg["law"]["t_stop_deg"], 3), band_mm=list(LOBE_Z), crank_axis_to_hub2_axis_mm=round(d_ax, 2),
                   boss_flank_to_hub2_axis_mm=round(d_ax - 5.0, 2), gap_lobe_crest_to_boss_flank_mm=round(d_ax - 5.0 - float(r[-1]), 2),
                   phi_at_stopB_deg=round(math.degrees(float(abs(phi[-1]))), 2),
                   note="the follower (on the crank's short arm s_arm, at the boss's hub-side flank) that rides this lobe is an L2 detail: "
                        "the verified model samples neither the lobe (inside hub 2's O20 stack) nor the follower")


def drive_parts(M, lg, dg):
    """[(group, member, name, mesh, material)] of the sidecar drive + its info"""
    D = M.D; P = D.p; out = []
    lobe, linfo = lobe_mesh(M, lg, dg)
    out.append(("l2", 2, f"drive lobe keep-out (hub-2 rim lobe on link 2's rotor: r {linfo['r_lobe']:.2f} -> {linfo['r_at_stopB']:.2f} mm over {linfo['sweep_deg']:.1f} deg "
                f"of q2, the exact RSSR lift s_arm |phi|; {LOBE_Z[1] - LOBE_Z[0]:.0f} mm band F+{LOBE_Z[0]:.2f}..F+{LOBE_Z[1]:.2f})", lobe, "steel"))
    dR, PV, zb = dg["dR"], dg["PV"], dg["zboss"]
    # crank boss (group dk): O10 x 6 tube on the O3 pin (two MR63ZZ 3x6x2.5 inside the keep-out), underside on link 1b + 0.15
    out.append(("dk", 9, f"drive bell crank boss keep-out (O10 x {BOSS_H:g} mm, bore O{2 * BORE_R:.1f} on the O3 pivot pin, two MR63ZZ 3x6x2.5 inside; "
                f"underside {zb:.2f} mm from GH = link 1b's top + {RUNG:g})", tube(np.zeros(3), dR, zb, zb + BOSS_H, 5.0, BORE_R), "ti"))
    # long arm (group dk): 6 x 3 at the model's stepped levels (stations 0..La step 2), out to La + 3 round the ball stud
    rs = np.r_[dg["rs"], dg["La"], dg["La"] + 3.0]; lv = np.r_[dg["lvl"], dg["lvl"][-1], dg["lvl"][-1]]
    rs[0] = 4.0                                                                 # the arm root starts inside the boss wall (bore stays free)
    ws = np.array([-3.0, -1.0, 1.0, 3.0])
    Bot = np.stack([[dR * lv[j] + rs[j] * dg["sR"] + w_ * dg["bnR"] for w_ in ws] for j in range(len(rs))])
    Off = T_LINK * np.broadcast_to(dR, Bot.shape).copy()
    out.append(("dk", 9, f"drive bell crank long arm keep-out (6 x {T_LINK:g} mm Ti, La {dg['La']:.2f} mm + 3 round the ball stud; steps from the boss level "
                f"{zb:.1f} to link 1b's layer {dg['lvl'][-1]:.1f} at the model's 60-deg ramp)", REF.grid_solid(Bot, Off), "ti"))
    # ball-link sockets + rod (group dr): the model's O7 socket envelope about each stud axis, 1 mm neck over the arm / lug top
    tip0, H0 = dg["tip0"], dg["H0"]; uK = dg["uK"]
    out.append(("dr", 8, f"drive M2 ball-link socket at the crank (O{2 * ER:g} envelope, {ZB - NECK:g} below .. 3.5 above the ball centre; ball {ZB:g} over the arm top)",
                REF.cyl(tip0, dR, -(ZB - NECK), 3.5, r=ER), "steel"))
    out.append(("dr", 8, f"drive M2 ball-link socket at the horn (O{2 * ER:g} envelope, {ZB - NECK:g} below .. 3.5 above the ball centre; ball {ZB:g} over the lug top)",
                REF.cyl(H0, uK, -(ZB - NECK), 3.5, r=ER), "steel"))
    out.append(("dr", 8, f"drive rod keep-out (O3 Ti-6Al-4V, {dg['L_rod']:.2f} mm ball centre to ball centre, M2 threaded ends)",
                REF.cyl(tip0, unit(H0 - tip0), 0.0, dg["L_rod"], r=1.5), "ti"))
    # crank pivot pin (link 1b): through link 1b's strap, up through the boss, DIN 6799 clip land over the boss top
    lev = dg["lev"]
    out.append(("l1b", 7, f"drive crank pivot pin keep-out (O3 h6 hardened, pressed in link 1b's strap {lev:.1f}..{lev + T_LINK:.1f}, through the boss)",
                REF.cyl(np.zeros(3), dR, lev, zb + BOSS_H + RUNG + CLIP_H, r=PIN_R), "steel"))
    out.append(("l1b", 7, f"drive crank pin clip keep-out (DIN 6799 RS 2.3, O6 x {CLIP_H:g} over the boss top + {RUNG:g})",
                tube(np.zeros(3), dR, zb + BOSS_H + RUNG, zb + BOSS_H + RUNG + CLIP_H, 3.0, PIN_R - 0.05), "steel"))
    # horn lug (link 1a): L-bracket from K's lower plate, lug 6 x 3 at hl over hub K's face, r_h + 4 long
    sK, bnK, lvK = dg["sK"], dg["bnK"], dg["lvK"]; fK = M.fK; zl0 = lvK - fK
    r0, r1, rin, rout = S.HUB_R - 1.0, S.HUB_R + 0.65, S.HUB_R + 0.65, dg["RH"] + 4.0
    prof = np.array([[r0, 0.0], [r1 + 1.5, 0.0], [r1 + 1.5, zl0], [rout, zl0], [rout, zl0 + T_LINK], [rin, zl0 + T_LINK], [rin, PLATE], [r0, PLATE]])
    HK = fK * uK
    Fp = np.array([[0, 1, 2], [0, 2, 7], [7, 2, 6], [6, 2, 5], [2, 3, 4], [2, 4, 5]])
    horn = MIN.extrude2d(prof[:, [0, 1]] * 0 + np.c_[prof[:, 0], prof[:, 1]], Fp, HK - 3.0 * bnK, sK, uK, bnK, 0.0, 6.0)
    out.append(("l1a", 1, f"drive horn lug keep-out (link 1a: 6 x {T_LINK:g} mm lug at F+{zl0:.2f} over hub K's face, r {rin:.2f}..{rout:.2f} mm along the horn "
                f"direction (beta {float(P['beta']):.1f} deg), on an L-bracket from K's lower plate, {rin - S.HUB_R:.2f} mm radially clear of K's upper boss; "
                f"M2 ball stud at r_h {dg['RH']:.2f})", horn, "ti"))
    return out, dict(lobe=linfo, rod_len_mm=round(dg["L_rod"], 3), boss_level_mm=round(zb, 3), arm_levels_mm=[round(float(x), 2) for x in dg["lvl"]],
                     La=dg["La"], s_arm=float(P["s_arm"]), r_h=dg["RH"], beta=float(P["beta"]), hl=float(P["hl"]), i_rock=round(dg["La"] / float(P["s_arm"]), 3),
                     model_sidecar=M._sc_info)


# ---------------------------------------------------------------------------------------------------- parts
def build_parts(M, lg, dg, knee_geom=None):
    """[(group, member, name, mesh in the MEMBER-LOCAL home frame, material)]; member 5 = arm-fixed (canonical arm frame)"""
    D = M.D; P = D.p; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; lc = float(P["lc"])
    U, C, F4, hr = MIN.joints4(M); H = lambda k: C[k] + F4[k] * U[k]; out = []
    capK = float(P.get("capK", 0) or 0)
    prof = MIN.link_rows(M); straps = {}
    for nm in ("L1a", "L1b", "L2"):
        lk, rows = prof[nm]; straps[nm] = MIN.link_solid(M, lk, rows)
    out.append(("base", 0, "J1 upper boss + cap keep-out (O20, F+3.15..F+12.25; base = J1's upper member, carried directly by the scapula handler at the hub ring)",
                REF.cyl(H(0), U[0], UP, CROWN, r=hr[0]), "ti"))
    out.append(("l1a", 1, "J1 lower plate keep-out (O20 x 3, link 1a)", REF.cyl(H(0), U[0], 0.0, PLATE, r=hr[0]), "ti"))
    out.append(("l1a", 1, "link 1a strap keep-out (8 x 3 mm Ti, fitted underside, J1 -> K)", straps["L1a"], "ti"))
    info = {}
    smp = lambda m: np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 4000, seed=2)[0]]
    for key, k, lower_strap, glo, mlo, gup, mup, label in (("K", 1, "L1a", "l1a", 1, "l1b", 7, "K"), ("J2", 2, "L1b", "l1b", 7, "l2", 2, "J2")):
        q_lo, q_hi, meta = lg[key]
        pair = key == "K"
        spts = smp(straps[lower_strap])
        ka_ = 0 if key == "K" else 1; ex_ = unit(U[ka_]); ey_ = unit(U[k] - (U[k] @ ex_) * ex_)
        ph_ = math.acos(float(np.clip(unit(U[k]) @ ex_, -1, 1))); sd_ = math.sin(ph_) * ex_ - math.cos(ph_) * ey_
        lat_ = np.cross(U[k], sd_); rr_ = np.linspace(MIN.SLOT_RS - MIN.DOWEL_R - MIN.SLOT_CLR, hr[k], 8); ll_ = np.linspace(-W_LINK / 2, W_LINK / 2, 9)
        spts = np.r_[spts, np.array([H(k) + r_ * sd_ + l_ * lat_ + 1.5 * U[k] for r_ in rr_ for l_ in ll_])]
        th, a_lo, a_hi, clr = MIN.slot_place(spts, H(k), U[k], q_lo, q_hi, MIN.SLOT_RS, MIN.DOWEL_R + MIN.SLOT_CLR, MIN.DOWEL_R, pair=pair)
        plate = MIN.slotted_plate(H(k), U[k], 0.0, PLATE, hr[k], MIN.SLOT_RS, MIN.DOWEL_R + MIN.SLOT_CLR, a_lo, a_hi, extra=[(a_lo + np.pi, a_hi + np.pi)] if pair else ())
        e, f = S.frame_of(U[k]); f = np.cross(U[k], e); homes = [th, th + np.pi] if pair else [th]
        pds = [H(k) + MIN.SLOT_RS * (math.cos(t_) * e + math.sin(t_) * f) for t_ in homes]
        dws = [REF.cyl(pd, U[k], MIN.DOWEL_Z[0], MIN.DOWEL_Z[1], r=MIN.DOWEL_R) for pd in pds]
        travel = math.degrees(q_hi - q_lo)
        out.append((glo, mlo, f"{label} lower plate keep-out (O20 x 3, {'link 1a' if key == 'K' else 'link 1b'}) with the {label} stop slot{'s (an opposed pair)' if pair else ''} "
                    f"(r {MIN.SLOT_RS} mm, {2 * (MIN.DOWEL_R + MIN.SLOT_CLR):.1f} wide, {travel:.1f} deg of travel + the dowel; its ends = the stops)", plate, "ti"))
        for i_, dw in enumerate(dws):
            out.append((gup, mup, f"{label} stop dowel{f' {i_ + 1} of 2' if pair else ''} (ISO 8734 O{2 * MIN.DOWEL_R:g} m6 hardened, r {MIN.SLOT_RS} mm, F+{MIN.DOWEL_Z[0]}..F+{MIN.DOWEL_Z[1]:.2f}, "
                        f"pressed in the {label} upper boss)", dw, "steel"))
        info[key] = dict(meta, travel_deg=round(travel, 3), dowel_home_angle_deg=round(math.degrees(th), 2), dowel_home_angles_deg=[round(math.degrees(t_), 2) for t_ in homes],
                         pair=pair, slot_deg=[round(math.degrees(a_lo), 2), round(math.degrees(a_hi), 2)],
                         clearance_to_lower_strap_deg=round(clr, 2), dowel_mm=[2 * MIN.DOWEL_R, MIN.DOWEL_Z[0], MIN.DOWEL_Z[1]], slot_r_mm=MIN.SLOT_RS,
                         slot_w_mm=2 * (MIN.DOWEL_R + MIN.SLOT_CLR), end_clearance_mm=MIN.END_CLR,
                         frame="angles in frame_of(axis) of the lower member: dowel centre = home angle + joint angle")
        if key == "K":
            out.append(("l1b", 7, f"K upper boss + clock-spring cap keep-out (O20, F+3.15..F+{CROWN + capK:.2f}: cap {capK:g} mm taller - clock spring holds K on stop A "
                        f"below the drive's onset; K SLAVED to q2 by the sidecar drive past it, never read)", REF.cyl(H(1), U[1], UP, CROWN + capK, r=hr[1]), "ti"))
            out.append(("l1b", 7, "link 1b strap keep-out (8 x 3 mm Ti, fitted underside, K -> J2)", straps["L1b"], "ti"))
    out.append(("l2", 2, "J2 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2; the rotor that carries the drive lobe)", REF.cyl(H(2), U[2], UP, CROWN, r=hr[2]), "ti"))
    out.append(("l2", 2, "link 2 strap keep-out (8 x 3 mm Ti, fitted underside, J2 -> J3)", straps["L2"], "ti"))
    out.append(("l2", 2, "J3 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2)", REF.cyl(H(3), U[3], UP, CROWN, r=hr[3]), "ti"))
    out.append(("l3", 3, "J3 lower plate keep-out (O20 x 3, member 3)", REF.cyl(H(3), U[3], 0.0, PLATE, r=hr[3]), "ti"))
    dparts, dinfo = drive_parts(M, lg, dg); out += dparts
    Em, Einfo = MIN.e_strap_capped(M)
    out.append(("l3", 3, f"E strap keep-out (8 x 3 mm Ti, fitted underside, hub 3 plate -> pin a, thins to {tp:.2f} at the boss, top capped at the boss top tr+tp under the knee's reach)", Em, "ti"))
    out.append(("l3", 3, f"E boss = pin a lower plate (O{2 * MIN.BOSS_R:.0f} x {tp:.2f} mm, tr..tr+tp, member 3)", REF.cyl(fr["A0"], sn, tr, tr + tp, r=MIN.BOSS_R), "ti"))
    z0 = tr + tp + S.RUN; ck = fr["A0m"] + (lc / 2) * fr["eK"] + (z0 + tp / 2) * sn
    out.append(("l4", 6, f"knee link keep-out (flat Ti bar {lc + 2 * MIN.BOSS_R:.1f} x {MIN.KNEE_W:.0f} x {tp:.2f} mm, pins a, b {MIN.BOSS_R:.0f} mm from its ends, tr+tp+0.5)",
                REF.box(ck, np.stack([fr["eK"], fr["nK"], sn], 1), [lc + 2 * MIN.BOSS_R, MIN.KNEE_W, tp]), "ti"))
    out.append(("H", 5, f"arm pad = pin b lower plate (O{2 * MIN.PAD_R:.0f} x {tp:.2f} mm, tr..tr+tp, arm-fixed on the cuff)", REF.cyl(fr["Bm"], sn, tr, tr + tp, r=MIN.PAD_R), "ti"))
    if knee_geom is not None:
        ks = knee_geom; e_, n_ = fr["eK"], fr["nK"]
        out.append(("l4", 6, f"knee stop tooth keep-out ({ks['face']['s'][1] - ks['face']['s'][0]:.1f} x 2 mm, hangs {tr + tp + S.RUN + tp - ks['tooth'][1]:.2f} mm from the knee "
                    f"link top behind pin a; its face meets the E strap's side at knee angle {ks['ang_stop']:.2f} deg)", MIN.prism_mesh(ks["tooth"][0], fr["A0m"], e_, n_, sn, *ks["tooth"][1:]), "ti"))
        out.append(("l4", 6, f"knee stop web keep-out (knee link level, {tp:.2f} mm, joins the tooth to the knee link's back edge)",
                    MIN.prism_mesh(ks["web"][0], fr["A0m"], e_, n_, sn, *ks["web"][1:]), "ti"))
    zr = z0 + tp + S.RUN; RET = BASE.RET
    out.append(("l3", 3, f"pin a retainer keep-out (O8 x {RET} mm: DIN 6799 RS 3.2 e-clip land + pin end, over the 0.5 mm GTM washer on the knee link)",
                REF.cyl(fr["A0"], sn, zr, zr + RET, r=4.0), "steel"))
    out.append(("H", 5, f"pin b retainer keep-out (O8 x {RET} mm: DIN 6799 RS 3.2 e-clip land + pin end, over the 0.5 mm GTM washer on the knee link)",
                REF.cyl(fr["Bm"], sn, zr, zr + RET, r=4.0), "steel"))
    stack = dict(pin_stack_mm=float(P["stk"]), plate_tp=tp, run=S.RUN, knee_level_tr=round(float(tr), 3), f=[round(float(x), 3) for x in M.f], fK=round(float(M.fK), 3),
                 capK_mm=capK, hubK_crown_mm=CROWN + capK, boss=[round(float(tr), 3), round(float(tr + tp), 3)],
                 knee=[round(float(z0), 3), round(float(z0 + tp), 3)], E=Einfo, knee_link_mm=[round(lc + 2 * MIN.BOSS_R, 2), MIN.KNEE_W, tp], hubs_r=list(hr),
                 retainer=[round(float(zr), 3), round(float(zr + RET), 3)], full_pin_stack_mm=round(float(zr + RET - tr), 3), stops=info, drive=dinfo)
    return out, stack


def set_adjacent(parts):
    """minarc's built-part pairs + the drive's (crank / rod / sockets / pin / lobe / horn vs their neighbours)"""
    MIN.set_adjacent(parts)
    find = lambda s: next((p for p in parts if p[2].startswith(s)), None)
    drive = [p for p in parts if p[2].startswith("drive")]
    near = ("link 1b strap", "link 1a strap", "link 2 strap", "J2 upper boss", "J2 lower plate", "K upper boss", "K lower plate", "J1 upper boss", "J1 lower plate")
    pairs = [(a[2], b) for a in drive for b in near] + [(b, a[2]) for a in drive for b in near] + [(a[2], b[2]) for a in drive for b in drive]
    seen = set()
    for a_, b_ in pairs:
        A, Bp = find(a_), find(b_)
        if A is None or Bp is None or A[1] == Bp[1] or (A[2], Bp[2]) in seen: continue
        seen.add((A[2], Bp[2]))
        XA = np.r_[np.asarray(A[3].vertices), trimesh.sample.sample_surface_even(A[3], 1500, seed=3)[0]]
        BASE.ADJ_PAIRS.append((A[2][:24], A[1], XA, Bp[2][:24], Bp[1], np.ascontiguousarray(Bp[3].vertices, float), np.ascontiguousarray(Bp[3].faces, np.int64)))


def drive_sweep(M, parts, lg, dg, dq=2.0):
    """red team of the drive's own motion, pose-independent: in link 1b's frame over the whole J2 window (q2lo .. stop B), link 2
    turns by q2 about u2, K opens by the law dK(q2), link 1a turns by -dK about uK, the crank by phi(dK) and the rod closes the
    RSSR. Every pair with a drive part on two different members: worst signed distance (mm, negative = inside) and where"""
    import igl
    D = M.D; u2 = D.u[1]; uK = dg["uK"]
    g = M._scg; sp = dg["sp"]
    qa, qb = [math.degrees(x) for x in lg["J2"][:2]]; qs = np.arange(qa, qb + 1e-6, dq)
    dks = dK_of_q2(lg, qs)
    smp = lambda m: np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 2500, seed=4)[0]]
    save = (M.dK, M._sc); M.dK = np.radians(dks) * sp; M._sc = None; M._sc_pose(); Xd = M._sc["X"]; M.dK, M._sc = save
    def pose(mem, j):
        if mem == 7: return np.eye(3), np.zeros(3)
        if mem == 2: return S.rotm(u2, math.radians(qs[j]))[0], np.zeros(3)
        if mem == 1: return S.rotm(uK, sp * math.radians(dks[j]))[0].T, np.zeros(3)
        if mem in (8, 9): R, t = Xd[mem]; return R[j], t[j]
        return None
    cand = [p for p in parts if p[1] in (1, 2, 7, 8, 9)]
    out = {}
    for ga, ma, na, mesh_a, _ in cand:
        if not na.startswith("drive"): continue
        XA = smp(mesh_a)
        for gb, mb, nb, mesh_b, _ in cand:
            if mb == ma: continue
            Vb, Fb = np.ascontiguousarray(mesh_b.vertices, float), np.ascontiguousarray(mesh_b.faces, np.int64)
            best = (1e9, None)
            for j in range(len(qs)):
                Ra, ta = pose(ma, j); Rb, tb = pose(mb, j); XB = ((XA @ Ra.T + ta) - tb) @ Rb
                v = float(igl.signed_distance(XB, Vb, Fb)[0].min())
                if v < best[0]: best = (v, j)
            out[f"{na[:44]} | {nb[:44]}"] = (round(best[0], 3), round(float(qs[best[1]]), 1), round(float(dks[best[1]]), 1))
    return dict(sorted(out.items(), key=lambda kv: kv[1][0]))


def law_check(M, K, idx):
    """per pose: the slaved K vs the law, from the member frames; the RSSR closure in the world from the posed groups"""
    from scipy.spatial.transform import Rotation as Rot
    D = M.D; lg = M._lg; g = M._scg; out = []
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BASE.swap_in(M, K)
    try:
        for i in idx:
            R1, t1 = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i); R8, t8 = M.T(8, i); R9, t9 = M.T(9, i)
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            want = float(dK_of_q2(lg, q2)) if K["state"][i] == 1 else 0.0
            eh = float(np.linalg.norm((R1 @ g["H0"] + t1) - (R8 @ g["H0"] + t8))); et = float(np.linalg.norm((R9 @ g["tip0"] + t9) - (R8 @ g["tip0"] + t8)))
            out.append(dict(pose=int(i), state=int(K["state"][i]), q2_deg=round(q2, 3), dK_deg=round(dK, 3), dK_law_deg=round(want, 3),
                            err_deg=round(abs(abs(dK) - want), 4), closure_horn_mm=round(eh, 4), closure_crank_mm=round(et, 4)))
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    return out


# ---------------------------------------------------------------------------------------------------- check vs the model
def check_frames(M, dd, parts, stack):
    """MIN.check_frames on this chain + the drive members: (a) the model's metal samples (hubs, E, boss, pad, knee, crank, horn,
    rod, rod ends, link straps) posed by the model's own member transforms vs the posed exo.glb surface of their group
    (scene_export.frame_xforms = the judges' path); (b) every part's vertices posed by the model vs by frame_xforms; (c) dowels
    in their slots. Poses (fit bench): arm at the side, first, middle, highest two, behind the back, across the body, the
    overhead raise peak, the K-most-open taken pose (the drive's extreme) and the pose nearest the drive's stop B."""
    import scene_export as SE, igl
    M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench; B = M.B
    allp = np.array([[B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(B.idx))])
    K = chain(M, allp)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    el = lambda i: B.poses[i]["elev"]; pl = lambda i: B.poses[i]["plane"]
    behind = [i for i in taken if "back" in B.clip[i].lower() or (pl(i) < -30 and el(i) > 20)]
    across = [i for i in taken if pl(i) >= 100 and el(i) >= 40]
    kin = [i for i in range(len(B.idx)) if K["ok"][i] and K["kok"][i] and K["res"][i] < 0.5]
    pick = {"arm at side": min(taken, key=el), "first": taken[0], "middle": taken[len(taken) // 2], "highest": max(taken, key=el),
            "2nd highest": next(j for j in sorted(taken, key=el)[::-1] if j != max(taken, key=el))}
    if behind: pick["behind the back"] = max(behind, key=lambda i: -pl(i))
    if across: pick["across the body"] = max(across, key=pl)
    tgt = np.array([30.0, 150.0, -60.0]); pick["overhead raise peak"] = min(kin, key=lambda i: float(np.linalg.norm(allp[i, :3] - tgt)))
    st1 = [i for i in taken if K["state"][i] == 1]
    if st1: pick["K most open, taken (drive extreme)"] = max(st1, key=lambda i: abs(K["dK"][i]))
    st1k = [i for i in kin if K["state"][i] == 1]
    if st1k: pick["K most open, closes (nearest stop B)"] = max(st1k, key=lambda i: abs(K["dK"][i]))
    src = trimesh.load(os.path.join(dd, "exo.glb")); out = []
    U, C, F4, hr = MIN.joints4(M); D = M.D; st = stack["stops"]
    for lab, i in pick.items():
        pz = allp[i]; fr = MIN.frame_dict(K, i, pz, pz, False)
        X, _ = SE.frame_xforms(fr); meshes = {}; posed = {}
        for node in src.graph.nodes_geometry:
            g = node.split("|")[0]
            if g == "F" or (g == "H" and not any(s_ in node for s_ in ("arm pad", "pad mount", "pin b retainer"))): continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            m.vertices = m.vertices @ np.asarray(R).T + t; meshes.setdefault(g, []).append(m); posed["|".join(node.split("|")[:2])] = m
        meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}
        old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BASE.swap_in(M, K); res = {}
        try:
            for name, (m, Xp) in list(M.rigid.items()) + list(M.link_pts.items()):
                Pw = M.world(m, i, Xp); g = "l1a" if name == "hub1" else GRP_OF[m]
                if name == "hub2": g = "l2"                                     # the model rides hub 2's housing on link 1b; its upper boss (link 2) is the same O20 envelope
                d = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes[g].vertices, float),
                                                            np.ascontiguousarray(meshes[g].faces, np.int64))[0])
                if name == "hub2":
                    dl = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes["l1b"].vertices, float),
                                                                 np.ascontiguousarray(meshes["l1b"].faces, np.int64))[0]); d = np.minimum(d, dl)
                if name in ("hubK", "hub2"):
                    k = 1 if name == "hubK" else 2; cen = C[k] + F4[k] * U[k]; w = Xp - cen; rr = np.linalg.norm(w - (w @ U[k])[:, None] * U[k], axis=1)
                    inslot = (rr > MIN.SLOT_RS - MIN.DOWEL_R - MIN.SLOT_CLR - 0.6) & (rr < MIN.SLOT_RS + MIN.DOWEL_R + MIN.SLOT_CLR + 0.6)
                    res[name + " (slot band)"] = [round(float(d[inslot].max()), 4) if inslot.any() else None, int(inslot.sum())]
                    d = d[~inslot]
                res[name] = [round(float(d.max()), 4), round(float(np.percentile(d, 95)), 4)]
            fdev = 0.0
            for g, mem, nm, mesh, mat in parts:
                Vw = M.world(mem, i, np.asarray(mesh.vertices)); Pg = np.asarray(posed[f"{g}|{nm}"].vertices)
                fdev = max(fdev, float(np.abs(Vw - Pg).max()))
            from scipy.spatial.transform import Rotation as Rot
            R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            inside = {}
            for key, ang in (("K", dK), ("J2", q2)):
                s_ = st[key]; c_ = s_["dowel_home_angle_deg"] + ang; a0, a1 = s_["slot_deg"]
                dd_ = math.degrees(math.asin((MIN.DOWEL_R + MIN.END_CLR) / MIN.SLOT_RS)); lo_, hi_ = a0 + dd_, a1 - dd_
                pos = (c_ - lo_) % 360.0
                inside[key] = dict(angle_deg=round(ang, 3), from_stop_lo_deg=round(pos, 3), to_stop_hi_deg=round((hi_ - lo_) - pos, 3), inside=bool(pos <= (hi_ - lo_) + 0.01 or pos >= 360.0 - 0.01))
        finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
        worst = max(v[0] for k, v in res.items() if not k.startswith(("L1", "L2")) and "slot band" not in k and v[0] is not None)
        worst_l = max(v[0] for k, v in res.items() if k in ("L1a", "L1b", "L2"))
        drv = {k: res[k][0] for k in ("crank", "horn", "rod", "rodends") if k in res}
        out.append(dict(label=lab, bench_pose=int(i), pose=[round(float(x), 2) for x in pz[:3]], taken=bool(i in set(taken)), state=int(K["state"][i]),
                        rigid_samples_max_mm=round(worst, 4), strap_samples_max_mm=round(worst_l, 4), drive_samples_max_mm=drv,
                        per_part=res, frame_dev_mm=round(fdev, 6), res_deg=round(float(K["res"][i]), 4), knee_angle=round(float(K["Kn"]["ang"][i]), 1),
                        m3e=round(float(K["m3e"][i]), 2), stops=inside))
        print(f"  check {lab:38s} pose {i} {np.round(pz[:3], 1)} st {int(K['state'][i]):+d}: rigid vs glb max {worst:.4f} mm (drive {drv}), straps {worst_l:.3f}, "
              f"frames dev {fdev:.2e}, dK {inside['K']['angle_deg']:.2f} q2 {inside['J2']['angle_deg']:.2f} dowels in slot {inside['K']['inside']} / {inside['J2']['inside']}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="l1_sidecar-longdyad")
    ap.add_argument("--jobs", type=int, default=1); ap.add_argument("--no-clips", action="store_true")
    a = ap.parse_args(); t0 = time.time(); fb = (60, 160); fbs = "Bench(60,160)"
    import concept_kit as KIT
    dd = os.path.join(BASE.FULL, "designs", a.out); os.makedirs(dd, exist_ok=True)
    M, rep = fit(); D = M.D; P = M.p
    if M.B.mode != "fast": print(f"WARNING: the fit bench {fbs} ran {M.B.mode}, not fast", flush=True)
    lg = law_geom(M); M._lg = lg; dg = drive_geom(M)
    print(f"fit (claim SCModel, BEST) on {fbs} {M.B.mode} (fold margin {KIT.FOLD_MARGIN}): near-touch gap {rep['gap']} reach {rep['reach']} ib14 {rep['inband14']} "
          f"ib10 {rep['inband10']} contact {rep['contact']} near1 {rep.get('gap_near1')} | f {np.round(M.f, 3).tolist()} fK {M.fK:.3f} tr {M.tr:.2f} sidecar {M._sc_info} "
          f"law {lg['law']} J2 {lg['J2'][2]} ({time.time() - t0:.0f} s)", flush=True)
    Bf = M.B; allp_ = np.array([[Bf.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(Bf.idx))])
    Kf = chain(M, allp_); kin_ = Kf["ok"] & Kf["kok"]
    knee_stop = round(180.0 - float(P["ang_min"]), 4)
    kg = MIN.knee_stop_geom(M, knee_stop, K=Kf)
    knee_rep = dict({k_: v for k_, v in kg.items() if k_ not in ("tooth", "web")}, model_window_edge_deg=knee_stop,
                    fit_bench_knee_max_deg=round(float(Kf["Kn"]["ang"][kin_].max()), 3), fit_bench_poses_past_stop=int((Kf["Kn"]["ang"][kin_] > knee_stop).sum()))
    print(f"knee stop at {knee_stop} deg: {knee_rep}", flush=True)
    parts, stack = build_parts(M, lg, dg, kg); stack["knee_stop"] = knee_rep
    print(f"drive: {json.dumps(stack['drive'], default=float)}", flush=True)
    up = BASE.user_parts(); bot = next(m for g, n, m in up if n.startswith("BOTTOM"))
    bottom_c = np.asarray(bot.vertices) @ BASE.HR
    dense = lambda m: np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 40000, seed=5)[0]]
    mc = trimesh.Trimesh(bottom_c, np.asarray(bot.faces), process=False)
    sweep, swrep = BASE.arm_sweep(M, parts); xc, crep = BASE.cut_bottom(M, dense(mc), sweep)
    if xc is not None:
        mc = BASE.slice_bottom(mc, M, xc)
        k = next(i for i, (g, n, m) in enumerate(up) if n.startswith("BOTTOM")); n0 = up[k][1]
        up[k] = (up[k][0], n0 + f" + cut square to the arm {xc:.1f} mm distal of pin b, clear of the knee sweep",
                 trimesh.Trimesh(np.asarray(mc.vertices) @ BASE.HR.T, mc.faces, process=False))
        crep["bottom_watertight_after_cut"] = bool(mc.is_watertight)
    bottom_c = dense(mc)
    print(f"knee sweep in the arm frame: {len(sweep)} points ({swrep}); BOTTOM {crep}", flush=True)
    mount, mrep = BASE.pad_mount_sweep(M, bottom_c, sweep)
    if mount is None: print(f"WARNING: {mrep['note']} -> the nearest-end mount (may meet the sweep)", flush=True); mount, mrep = BASE.pad_mount(M, bottom_c)
    mrep["bottom"] = crep; mrep["sweep"] = swrep
    if mount is not None: parts.append(("H", 5, f"pad mount to BOTTOM (proxy) ({P['tp']:.2f} mm slab at the pad level, arm pad -> the BOTTOM bar, routed clear of the knee sweep)", mount, "ti"))
    def export_mesh(g, mem, m):
        if mem != 5: return m
        return trimesh.Trimesh(np.asarray(m.vertices) @ BASE.HR.T, m.faces, process=False)
    sc = trimesh.Scene(); pf = []
    allp = [(g, n, export_mesh(g, mem, m), mat) for g, mem, n, m, mat in parts] + [(g, n, m, "user") for g, n, m in up]
    for i, (g, n, m, mat) in enumerate(allp):
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        user = mat == "user"; mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else 0.0
        rho = STEEL if mat == "steel" else TI
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material="user part" if user else ("steel" if mat == "steel" else "Ti-6Al-4V"),
                       mass_g=None if user else round(vol / 1000 * rho, 2), valid=bool(user or (mm.is_watertight and mm.is_volume)),
                       pieces=None if user else int(len(mm.split(only_watertight=False))), faces=len(m.faces)))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=4, level="L1 keep-out", FACES={"1": round(float(M.f[0]), 2), "K": round(float(M.fK), 2), "2": round(float(M.f[1]), 2), "3": round(float(M.f[2]), 2)},
                   parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    ours = [p for p in pf if p["material"] != "user part"]
    bad = [p['name'] for p in ours if not p['valid'] or p['pieces'] != 1]
    print(f"exo.glb: {len(parts)} keep-out parts ({sum(p['mass_g'] or 0 for p in ours):.1f} g) + {len(up)} user parts; invalid: {bad or 'none'}; mount {mrep}; "
          f"stops {json.dumps(stack['stops'])}", flush=True)
    u1, u2, u3 = D.u; w_d = math.degrees(math.acos(float(np.clip(-u3[1], -1, 1)))); w_a = math.degrees(math.atan2(u3[0], u3[2]))
    az = math.degrees(math.atan2(u1[2], -u1[0])); elv = math.degrees(math.asin(float(np.clip(u1[1], -1, 1))))
    chk = S.circ_int(S.bvec(az, elv), D.A[0], S.w_dir(w_d, w_a), D.A[1], D.branch)
    law = lg["law"]
    kin = dict(az=az, el=elv, a=[math.degrees(D.A[0]), math.degrees(D.A[1])], w=[w_d, w_a], branch=int(D.branch), order=[0, 1, 1],
               axis_points_mm=[np.round(c_, 3).tolist() for c_ in D.c], axes=[np.round(u_, 6).tolist() for u_ in D.u],
               axis_line_offsets_mm=[round(float(np.linalg.norm(c_)), 2) for c_ in D.c], u2_check_deg=round(math.degrees(math.acos(float(np.clip(chk @ u2, -1, 1)))), 5),
               seats=dict((k_, P[k_]) for k_ in ("az1", "el1", "az2", "el2", "wd", "wa", "b3")),
               knee=dict((k_, P[k_]) for k_ in ("lE", "lc", "phiE", "phib", "stk", "ang_min")), knee_mid_m_mm=np.round(D.m, 3).tolist(), hub_r_mm=list(M.hr),
               knuckle=dict(uK=np.round(D.uK, 6).tolist(), bk1=P["bk1"], bk2=P["bk2"], psiA_deg=round(math.degrees(D.psiA), 3), a1max=P["a1max"],
                            dK_stop_B_deg=stack["stops"]["K"]["stop_B_deg"], q2_stops_deg=stack["stops"]["J2"]["q2_stops_deg"], smlo=P["smlo"], smhi=P["smhi"],
                            slaved=dict(law="dK = kK (q2 - q2hi) along the stretching sense (lin), cut at the drive's own range dK_lim", kK=law["kK"],
                                        q2_onset_deg=law["q2hi_deg"], s_q=law["s_q"], dK_lim_deg=law["dK_stop_deg"], r_lobe=float(P["r_lobe"]), s_arm=float(P["s_arm"]),
                                        La=float(P["La"]), r_h=float(P["r_h"])),
                            note="az/el/a/w = the 3R with K on stop A; past the onset q2hi K is SLAVED to q2 by the sidecar drive (lobe -> bell crank -> rod -> horn; "
                                 "3 active DOF; K never free, never read); the bell crank (dk) and the rod (dr) are posed side members of link 1b"))
    design = dict(id=a.out, source=f"docs/concepts/{ID}.md (the verified config: docs/concepts/rows/{ID}.json best_params = docs/concepts/verify/{ID}.py BEST), "
                                   f"fit on {fbs} {M.B.mode} at fold margin {KIT.FOLD_MARGIN} = the shape the verifier wore frozen on Bench(110,360) exact "
                                   "(v_gap 18.91, score 93.12; held out 22.67)",
                  params=dict(V.BEST), n_joints=4, sliding_cuff=False, dof=3,
                  passive=dict(count=2, translations=0, rotations=2, outside_dof_count=True,
                               kind="flat two-pin knee closing the loop at the cuff (pins a, b parallel to J3); set by loop closure. K (4th revolute) is NOT a DOF: slaved "
                                    "to q2 by the sidecar drive past the onset, spring-held on stop A below it; the bell crank / rod are set by the RSSR closure",
                               components=[dict(pin="a", between="member 3 (E boss) / knee link", part="IGLIDUR-PIN: iglidur GSM sleeve + 2 GTM washers on an integral O4 Ti pin, DIN 6799 RS 3.2 e-clip land",
                                                stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]]),
                                           dict(pin="b", between="knee link / arm pad (cuff)", part="IGLIDUR-PIN (as pin a)", stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]])]),
                  joints=[dict(joint="J1", part="O20 x 12.25 v5 hub, MR117-2RS pair, encoder", axis_offset_mm=kin["axis_line_offsets_mm"][0]),
                          dict(joint="K", part=f"O20 v5 hub, MR117-2RS pair, cap {CROWN + float(P.get('capK', 0)):.2f} mm (clock spring); stops A / B = an opposed pair of O3 "
                                                f"dowels in two {stack['stops']['K']['travel_deg']:.1f}-deg arc slots; slaved (no encoder)", axis_offset_mm=0.0, passive=False, slaved=True, sensed=False),
                          dict(joint="J2", part=f"O20 x 12.25 v5 hub, MR117-2RS pair, encoder; drive lobe on its rotor; q2 stops = O3 dowel in a "
                                                 f"{stack['stops']['J2']['travel_deg']:.1f}-deg arc slot (folded stop q2lo, stop B at the drive's range)", axis_offset_mm=kin["axis_line_offsets_mm"][1]),
                          dict(joint="J3", part="O20 x 12.25 v5 hub, MR117-2RS pair, encoder", axis_offset_mm=kin["axis_line_offsets_mm"][2])],
                  drive=dict(kind="sidecar RSSR: hub-2 rim lobe -> bell crank on link 1b (MR63ZZ pair on an O3 pin; short arm s_arm on the lobe, long arm La) -> O3 Ti rod "
                                  "+ 2 M2 ball links -> horn lug of link 1a at hub K",
                             components=["MR63ZZ 3x6x2.5 x 2 (crank pivot)", "O3 h6 pin + DIN 6799 RS 2.3", "M2 ball link x 2 (O7 socket envelope) + M2 ball studs",
                                         "O3 x %.1f mm Ti rod, M2 ends" % stack["drive"]["rod_len_mm"], "follower roller / pad on the short arm (L2)"],
                             **stack["drive"]),
                  kinematics=kin, base=dict(mount="girdle", chain="sidecar_longdyad_knuckle", note="base rides the scapula on the user's scapula handler, carried directly at the J1 hub ring (no tab)"),
                  built_with="pipeline/concept_l1/build_sidecar_l1.py (L1 keep-out meshes: O20 hub keep-outs incl. hub K's 6 mm taller cap, fitted 8 x 3 straps 1a / 1b / 2, stop "
                             "dowels + arc slots, the lobe / bell crank / pin / rod / ball-link / horn drive (crank and rod posed), E strap + boss, knee link + knee stop, arm pad, pin retainers)",
                  label=f"sidecar-longdyad-knuckle-3r (verified config, fit {fbs}, fold margin {KIT.FOLD_MARGIN:g}), L1 keep-out", fit_bench=list(fb), fold_margin=KIT.FOLD_MARGIN,
                  build_fixes=dict(k_pair=True, j2_single_dowel_push_limit=True, e_cap=True, knee_stop_deg=knee_stop),
                  faces_mm=[round(float(x), 2) for x in M.f], fK_mm=round(float(M.fK), 2), tr=round(float(M.tr), 2), stack_mm=stack,
                  bench=dict(near_touch_gap=rep["gap"], **{k_: rep[k_] for k_ in ("reach", "follow", "inband14", "contact")}, inband10=rep["inband10"]),
                  note="R17's dynamics judge orders posed groups as a serial chain (base, l<k>[a-z], cuff); the drive's side members dk / dr have no place in it")
    json.dump(design, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    set_adjacent(parts)
    pts = [(m, X) for m, X in M.rigid.values()] + [(m, X) for m, X in M.link_pts.values()] + list(M.contact)
    for g, mem, n, m, mat in parts:
        pts.append((mem, np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 300, seed=1)[0]]))
    rep_out = dict(fit=dict(params=dict(V.BEST), source=f"docs/concepts/verify/{ID}.py BEST through the claim's SCModel", bench=f"{fb[0]},{fb[1]}", mode=M.B.mode,
                            fold_margin=KIT.FOLD_MARGIN, report={k_: rep.get(k_) for k_ in ("gap", "plain", "gap_near1", "near_touch_min_mm", "reach", "follow", "inband14",
                                                                                              "inband10", "contact", "why", "min_clear_taken", "parts_ib14")},
                            m=np.round(D.m, 3).tolist(), tr=round(float(M.tr), 3), fK=round(float(M.fK), 3), sidecar=M._sc_info),
                   law={k_: v for k_, v in law.items()}, stack=stack, mount=mrep, kin_u2_check_deg=kin["u2_check_deg"], dowel_check=MIN.dowel_check())
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    dsw = drive_sweep(M, parts, lg, dg)
    rep_out["drive_sweep"] = dict(rule="signed distance (mm, negative = inside), worst over the J2 window in link 1b's frame; (mm, q2 deg, |dK| deg)",
                                  pairs=dsw, worst=next(iter(dsw.items())) if dsw else None)
    print(f"drive sweep (worst 8): {list(dsw.items())[:8]}", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep_out["check"] = check_frames(M, dd, parts, stack)
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench
    try: rep_out["law_check"] = law_check(M, Kf, [c["bench_pose"] for c in rep_out["check"]] + list(np.nonzero(kin_ & (Kf["state"] == 1))[0]))
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    lc_ = rep_out["law_check"]; st1 = [x for x in lc_ if x["state"] == 1]
    rep_out["law_check_summary"] = dict(poses=len(lc_), stretched=len(st1), max_err_deg=max((x["err_deg"] for x in lc_), default=None),
                                        dK_max_deg=max((abs(x["dK_deg"]) for x in st1), default=None),
                                        closure_max_mm=max((max(x["closure_horn_mm"], x["closure_crank_mm"]) for x in lc_), default=None))
    print(f"law check: {rep_out['law_check_summary']}", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    if not a.no_clips:
        C, st = BASE.make_clips(M, pts, a.jobs); C["subtitle"] = design["label"]
        C["design"] = dict(n=3, hub_r=max(M.hr), knuckle=True, **{k_: kin[k_] for k_ in ("az", "el", "a", "w", "branch", "order")})
        json.dump(C, open(os.path.join(dd, "clips.json"), "w"), separators=(",", ":"))
        ko = {cl["name"]: dict(frames_K_open=sum(1 for f in cl["frames"] if not f["held"] and abs(f.get("knuckle", {}).get("dK", 0)) > 1e-3),
                               dK_max=round(max([abs(f.get("knuckle", {}).get("dK", 0)) for f in cl["frames"] if not f["held"]] or [0]), 2)) for cl in C["clips"]}
        for k_ in st: st[k_]["knuckle"] = ko.get(k_)
        rep_out["clips"] = st; json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
        print(f"clips.json written ({time.time() - t0:.0f} s); K open on clips: { {k_: v for k_, v in ko.items() if v['frames_K_open']} }", flush=True)
        W = BASE.make_workspace(M, a.jobs); json.dump(W, open(os.path.join(dd, "workspace.json"), "w"), separators=(",", ":"))
        rep_out["workspace"] = dict(poses=len(W["poses"]), closes=round(float(np.mean([p["closes"] for p in W["poses"]])), 4),
                                    feasible_kin_parts=round(float(np.mean([p["eval_feasible"] for p in W["poses"]])), 4),
                                    driven_feasible=int(sum(1 for p in W["poses"] if p["eval_feasible"] and p["knuckle"]["state"] != 0)))
        print(f"workspace.json: {rep_out['workspace']} ({time.time() - t0:.0f} s)", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s -> {dd}")


if __name__ == "__main__":
    main()
