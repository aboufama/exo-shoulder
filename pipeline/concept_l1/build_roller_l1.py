"""L1 keep-out CAD of the generation-6 winner roller-longdyad-knuckle-3r (round 9; verified frozen exact Bench(110,360) 18.67 /
score 93.21, envelope-corrected 18.56, held out 23.73; docs/concepts/roller-longdyad-knuckle-3r.md; config =
docs/concepts/rows/roller-longdyad-knuckle-3r.json best_params = the verifier harness' BEST, with the auditor's knee fix
ang_min 26.8823 (docs/alignment/roller-longdyad-knuckle-3r.md: the claim's 25.22 lets the knee run to 154.8 deg for no score;
re-worn bench 18.67 / held out 23.72 at 26.88)) -> a judge-ready design dir pipeline/full-exo/designs/<out>/ (exo.glb, clips.json,
workspace.json, design.json, parts_full.json, build.json).

Derived from build_sidecar_l1.py (gen 6, the same chain: links, hubs, knee, K hub; only the drive differs), which is COPIED
from, never edited; build_minarc_l1.py (gen 4 / 4b) is IMPORTED unchanged. What changes for this morphology:
  * the model is the claim's RLModel (docs/concepts/models/roller-longdyad-knuckle-3r.py on sidecar-roller-flank-knuckle-3r.py,
    loaded unchanged), fit on Bench(60,160) FAST = the frozen protocol's hand-over: the L1 carries the shape the verifier
    wore on Bench(110,360) exact;
  * K is SLAVED (3 encoders J1 / J2 / J3; K never read, the two knee pins carry no encoders): past the onset q2hi the lin law
    dK = kK (q2 - q2hi) sets K; the drive's own range ends at |dK| = dK_lim (the synthesised cam's first failing step:
    pressure angle / lift-off / cusp / contact-off-lug / clearances) where the q2 dowel stop B sits - every pose past it is not
    taken (the model's _truncate on every bench);
  * the ROLLER-FLANK drive is POSED: the bell crank (group "dk", the model's member 9: boss, bent arm, MR63ZZ roller, integral
    O3 stub + O4.5 x 0.8 retaining head) turns about its pivot axis dR on link 1b by phi = sig |dK| / g (the claim's law,
    cprog 0), dK read off each frame's link 1a / 1b frames - nothing free; no rod, no ball links;
  * drive metal at its real envelope: the hub-2 rim lobe (sector in a 3 mm band of hub 2's upper boss, r = r_lobe + s_arm |phi|,
    inside the O20 skirt), the crank boss (O10 x 6, bore O3.2 for the O3 pivot pin, two MR63ZZ inside) stacked on link 1b +
    0.15, the bent arm 6 x 3 (straight run at the model's stepped levels, then the tangent arc concentric with hub K at the
    roller radius r_c, 3 mm past the roller), the roller (MR63ZZ O6 x 2.5 on the stub, radial axis), the stub + head, the O3
    pivot pin + DIN 6799 clip (link 1b), and the flank lug of link 1a = the model's own spherical-shell lug (a 0.3..6 mm band
    behind the synthesised conjugate flank over the used stroke [0, dK_lim], 3 mm thick on the sphere |X| = |C0| - 1.5, plus
    its radial root from hub K's rim at hub K's member level + hl);
  * stops: K = an opposed O3 dowel pair between stop A (0) and stop B (the model's a1max); J2 = one O3 dowel between q2lo and the
    drive-range stop B; gen-4b fixes carried over (E strap capped, knee stop tooth at 180 - ang_min, K slots clear of link 1a);
  * build.json declares the slaved K for the dynamics judge (judge/dynamics.py "SLAVED COORDINATES": force closure, drive
    group dk rides link 1b).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/build_roller_l1.py [--out l1_roller-longdyad] [--jobs 2] [--no-clips]
    ... --skin-only   (re-run the drive skin-clearance sweep over every clip frame on an existing build)
"""
import argparse, json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
os.environ.pop("CB_EXACT", None)                     # the frozen protocol's fit bench is FAST (Bench(60,160))
import build_minarc_l1 as MIN                                                   # noqa: E402  (gen-4/4b L1 builder, imported unchanged)
BASE = MIN.BASE; CB, REF = BASE.CB, BASE.REF

ID = "roller-longdyad-knuckle-3r"
RL = MIN._load("roller_longdyad_for_l1", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
RF = RL.RF; SC = RL.SC; S = SC.S; PK = SC.PK
BEST = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", ID + ".json")))["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
ANG_MIN_FIX = 26.8823                                                           # the auditor's knee-window fix (>= 26.88)
CFG = dict(BEST, ang_min=max(float(BEST["ang_min"]), ANG_MIN_FIX))
CROWN, UP, T_LINK, W_LINK, RUN = S.CROWN, S.UP, S.T_LINK, S.W_LINK, S.RUN
PLATE = MIN.PLATE; unit = S.unit; TI, STEEL = BASE.TI, BASE.STEEL
BOSS_H, RUNG = SC.BOSS_H, SC.RUNG                                               # crank boss height, running gap
ROLL_R, ROLL_W, LUG_BACK = RF.ROLL_R, RF.ROLL_W, RF.LUG_BACK                     # MR63ZZ O6 x 2.5, lug band depth behind the flank
HEAD_R, HEAD_T = RL.HEAD_R, RL.HEAD_T                                           # the roller's retaining stub head (O4.5 x 0.8)
LOBE_Z = (UP + 0.5, UP + 3.5)                                                   # the lobe's 3 mm band in hub 2's upper boss (link 2)
LOBE_RIN = 6.0
PIN_R, BORE_R, CLIP_H = 1.5, 1.6, 0.9                                           # crank pivot pin O3 h6, boss bore O3.2 (keep-out), DIN 6799 RS 2.3 land
STUB_R, ROLL_BORE = 1.5, 1.6                                                    # roller stub O3 (integral to the crank), MR63ZZ bore keep-out
ARM_ROOT = 4.0                                                                  # the arm's root inside the boss wall (bore free)
ARM_END = 3.0                                                                   # arm past the roller axis (round the stub)
GROUPS = MIN.GROUPS + ((9, "dk"),)
GRP_OF = {0: "base", 1: "l1a", 7: "l1b", 2: "l2", 3: "l3", 6: "l4", 5: "H", 9: "dk"}


# ---------------------------------------------------------------------------------------------------- the verified model
class L1Model(RL.RLModel):
    """the claim's RLModel; once fitted (self._l1), the crank (9) frame comes from the K opening read off the CURRENT member
    frames X[1], X[7] (so the clip / workspace swaps of BASE.swap_in pose the drive exactly), through the model's own law
    (RFModel._sc_pose: phi = sig |dK| / g about dR)"""
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
    """the claim's model on BEST (+ the knee fix), fit on Bench(60,160) FAST: the shape the verifier wore frozen"""
    B = CB.Bench(60, 160); P = RL._clamp(dict(RL.PARAMS, **CFG)); M = L1Model(B, P); r = M.run()
    a = PK.audit(M, B); r["gap_near1"] = a.get("gap_near1"); r["gap_near2"] = a.get("gap_near2"); r["near_touch_min_mm"] = a.get("near_touch_min_mm")
    M._bench = (M.Q, M.s, M.RS, M.X, M.K, M.q); M._l1 = True; M._l1c = None
    return M, r


def chain(M, poses):
    """MIN.chain + the drive group dk + the drive-range stop: |dK| > dK_lim is not taken (J2's stop B dowel sits there)"""
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
    D = M.D; P = D.p; L = D.law(); assert L.get("ok"), L
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
                                pressure_angle_deg=round(float(np.max(L["pa"])), 2)),
                L=L, ts_deg=ts, dK_deg=dKl)


def dK_of_q2(lg, q2_deg):
    """|dK| (deg) of the slaved K at J2 angle q2 (0 below the onset)"""
    t = ((np.asarray(q2_deg, float) - lg["law"]["q2hi_deg"] + 180) % 360 - 180) * lg["law"]["s_q"]
    return np.where(t > 0, np.interp(np.maximum(t, 0), lg["ts_deg"], lg["dK_deg"]), 0.0)


def _ang(a, b): return RF._ang(a, b)


def drive_geom(M):
    """the claim's roller-flank geometry, re-derived from RFModel._rod_metal's own values (pivot PV / axis dR, arm stations and
    levels = the model's crank samples, the arc about uK, roller centre C0, the flank synthesised per 0.25 deg of K exactly as
    the model does, cut at dK_lim) - asserted equal to the model's samples where both exist"""
    D = M.D; P = D.p; g = M._scg; vr = M._viz_rod; uK = g["uK"]; dR, PV = g["dR"], g["PV"]; sp, sig, gg, cc = g["sp"], g["sig"], g["g"], g["c"]
    C0 = np.asarray(vr["roller"], float); T3 = np.asarray(vr["armB"], float); R0 = float(np.linalg.norm(C0)); rL = R0 - 1.5; rA = R0 + 1.5 + RUNG
    zboss = float(PV @ dR); tK0 = unit(dR - (dR @ uK) * uK); bK0 = unit(np.cross(uK, tK0))
    beta = math.radians(float(P["beta"])); rc = float(P["r_c"]); lvK = float(M.fK + float(P["hl"])); lift = min(max(float(P.get("lift", 0.0)), 0.0), 8.0)
    h_tip = lvK + lift + T_LINK + RUNG
    Dp = float(np.linalg.norm(PV - (PV @ uK) * uK)); sgn_b = 1.0 if beta >= 0 else -1.0; psT = math.acos(min(1.0, rc / max(Dp, rc + 1e-6))) * sgn_b
    ch = T3 - PV; Lch = float(np.linalg.norm(ch)); ns = max(3, int(Lch / 2.0) + 1)
    nb = len(S.disc(5.0, 2.0)); arm = np.asarray(M.rigid["crank"][1][nb:], float); rows = arm.reshape(-1, 4, 3)
    straight, arc_m = rows[:ns], rows[ns:]
    psi = np.append(np.arange(psT, beta, sgn_b * 2.0 / rc), beta) if abs(beta) > abs(psT) + 1e-6 else np.array([beta])
    ws = np.array([-3.0, -1.0, 1.0, 3.0])
    arc_row = lambda a: np.array([unit(uK * h_tip + (rc + w_) * (math.cos(a) * tK0 + math.sin(a) * bK0)) * rA for w_ in ws])
    arc_re = np.array([arc_row(a) for a in psi[1:]]) if len(psi) > 1 else np.zeros((0, 4, 3))
    arc_dev = float(np.abs(arc_re - arc_m).max()) if len(arc_m) else 0.0
    assert len(arc_m) == len(arc_re) and arc_dev < 1e-6, (len(arc_m), len(arc_re), arc_dev)
    # ---- the cam pair on the K grid (RFModel._rod_metal, copied: roller centre path, contact normals, flank in link 1a's frame)
    kgrid = g["kgrid"]; nk = len(kgrid); lim = float(g["dK_lim"]); jl = int(np.argmin(np.abs(kgrid - lim)))
    Rk = S.rotm(uK, sp * kgrid); Rcg = S.rotm(dR, sig * RF.phi_of(kgrid, gg, cc)); Cg = np.einsum("nij,j->ni", Rcg, C0 - PV) + PV
    vH = lambda X: -sp * np.cross(uK, X); Qg = np.zeros((nk, 3)); ng = np.zeros((nk, 3)); nprev = None
    for j in range(nk):
        C = Cg[j]; vC = sig * float(RF.dphi_of(kgrid[j], gg, cc)) * np.cross(dR, C); vh = vH(C); vr_ = vC - vh; rh = unit(C)
        n = np.cross(rh, vr_); nn = float(np.linalg.norm(n))
        n = n / nn if nn > 1e-9 else (nprev if nprev is not None else unit(vh))
        if nprev is None: n = n if float(n @ vh) >= 0 else -n
        else: n = n if float(n @ nprev) >= 0 else -n
        nprev = n; Qg[j] = C + ROLL_R * n; ng[j] = n
    P1 = np.einsum("nij,nj->ni", Rk, Cg); N1 = np.einsum("nij,nj->ni", Rk, ng); Q1 = np.einsum("nij,nj->ni", Rk, Qg)
    sel = np.arange(0, jl + 1); dsum = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(Q1[sel], axis=0), axis=1))]); pick = [int(sel[0])]
    for jj, dsv in zip(sel, dsum):
        if dsv - dsum[list(sel).index(pick[-1])] >= 1.5: pick.append(int(jj))
    if pick[-1] != sel[-1]: pick.append(int(sel[-1]))
    return dict(dR=dR, PV=PV, uK=uK, sp=sp, sig=sig, g=gg, c=cc, C0=C0, T3=T3, R0=R0, rL=rL, rA=rA, zboss=zboss, tK0=tK0, bK0=bK0, beta=beta, rc=rc,
                lvK=lvK, lift=lift, h_tip=h_tip, psT=psT, psi=psi, sgn_b=sgn_b, Lch=Lch, ns=ns, straight=straight, arc=arc_re, arc_row=arc_row, ws=ws,
                kgrid=kgrid, phig=RF.phi_of(kgrid, gg, cc), lim=lim, jl=jl, P1=P1, N1=N1, Q1=Q1, pick=pick, lev=float(M._sc_info["lev_L1b"]),
                arc_dev_mm=arc_dev)


def boss_level(dg, strap, r=5.0):
    """underside level (along dR) for the crank boss: link 1b strap's highest top within the O10 footprint + RUNG, never below the model's"""
    import igl
    dR = dg["dR"]; e, f = S.frame_of(dR); g = np.linspace(-r, r, 41); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= r * r
    top = dg["zboss"]
    for h in np.arange(dg["zboss"] - 2.0, dg["zboss"] + 8.0, 0.05):
        P = h * dR + X[k][:, None] * e + Y[k][:, None] * f
        if float(igl.signed_distance(np.ascontiguousarray(P), np.ascontiguousarray(strap.vertices, float), np.ascontiguousarray(strap.faces, np.int64))[0].min()) < 0: top = h
    return max(dg["zboss"], top + RUNG)


def tube(p0, ax, h0, h1, ro, ri, n=64):
    """O(2 ro) / O(2 ri) tube along ax from p0 + h0 ax to p0 + h1 ax (one watertight genus-1 solid)"""
    e, f = S.frame_of(ax); f = np.cross(ax, e); ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    ring = lambda r: np.c_[r * np.cos(ang), r * np.sin(ang)]
    V2 = np.r_[ring(ro), ring(ri)]; F2 = []
    for i in range(n):
        j = (i + 1) % n; F2 += [[i, j, n + j], [i, n + j, n + i]]
    return MIN.extrude2d(V2, np.array(F2), p0, e, f, ax, h0, h1)


def stepped(p0, ax, prof, n=48):
    """solid of revolution about ax through p0 from a (r, z) profile [(r0, z0), (r1, z1), ...] (open polyline, ends on the axis)"""
    m = trimesh.creation.revolve(np.asarray(prof, float), sections=n)
    e, f = S.frame_of(ax); f = np.cross(ax, e); Tm = np.eye(4); Tm[:3, :3] = np.c_[e, f, ax]; Tm[:3, 3] = p0; m.apply_transform(Tm)
    return _outward(m)


def _outward(m):
    m = trimesh.Trimesh(m.vertices, m.faces, process=True)
    if m.is_watertight and m.volume < 0: m.invert()
    return m


def lobe_mesh(M, lg, dg, n=80):
    """the hub-2 rim lobe on link 2's rotor (member-local home frame): outer edge r(t) = r_lobe + s_arm |phi(dK(t))| (phi = |dK| / g,
    the claim's law) at the rotor angle that faces the crank pivot at q2 = q2hi + s_q t, t in [0, t_stop]; inner arc LOBE_RIN;
    band LOBE_Z over hub 2's face"""
    D = M.D; P = D.p; u2 = D.u[1]; c2 = D.c[1]; f2 = M.f[1]; H2 = c2 + f2 * u2
    e, f = S.frame_of(u2); f = np.cross(u2, e)
    zc = 0.5 * (LOBE_Z[0] + LOBE_Z[1]); hz = (H2 @ u2 + zc) / max(float(dg["dR"] @ u2), 0.2)
    w = dg["dR"] * hz - H2; w = w - (w @ u2) * u2; phiR = math.atan2(float(w @ f), float(w @ e)); d_ax = float(np.linalg.norm(w))
    ts = np.radians(np.linspace(0.0, lg["law"]["t_stop_deg"], n)); s_q = lg["law"]["s_q"]; q2hi = math.radians(lg["law"]["q2hi_deg"])
    dk = np.radians(np.interp(np.degrees(ts), lg["ts_deg"], lg["dK_deg"])); phi = RF.phi_of(dk, dg["g"], dg["c"])
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
                   note="inside hub 2's O20 skirt over the whole stroke (r <= HUB_R): the follower (the crank's short arm s_arm, at the boss's "
                        "hub-side flank) that rides it reaches through a window in hub 2's cap ring - an L2 detail; the verified model samples "
                        "neither the lobe nor the follower")


def arm_mesh(dg, zb):
    """the bent arm (6 x 3 Ti): the model's straight-run stations from ARM_ROOT (inside the boss wall) to the tangent point, then
    the arc about uK at the roller radius, ARM_END past the roller axis; underside = the model's samples, 3 mm radially thick;
    the root raised to the built boss level on a <= 60-deg ramp (never below the model's levels)"""
    st = dg["straight"]; Lch = dg["Lch"]; ns = dg["ns"]; d_s = np.linspace(0.0, Lch, ns)          # station distance from the boss axis
    keep = d_s > ARM_ROOT + 1e-6; dd = np.r_[ARM_ROOT, d_s[keep]]
    rows = np.array([[np.interp(x, d_s, st[:, c, k]) for k in range(3)] for x in dd for c in range(4)]).reshape(len(dd), 4, 3)
    lv = np.linalg.norm(rows.mean(axis=1), axis=1); want = np.maximum(lv, zb - math.tan(math.radians(S.RAMP)) * np.maximum(dd - 5.0, 0.0))
    rows = rows * (want / lv)[:, None, None]
    lifted = arm_over_strap(dg, rows) if "strap_L1b" in dg else np.zeros(len(rows))
    rows = rows * ((np.linalg.norm(rows.mean(axis=1), axis=1) + lifted) / np.linalg.norm(rows.mean(axis=1), axis=1))[:, None, None]
    ext = dg["beta"] + dg["sgn_b"] * ARM_END / dg["rc"]
    arc = np.r_[dg["arc"], dg["arc_row"](ext)[None]] if len(dg["arc"]) else dg["arc_row"](ext)[None]
    d0 = rows[-1, 3] - rows[-1, 0]; d1 = arc[0, 3] - arc[0, 0]
    if float(d0 @ d1) < 0: arc = arc[:, ::-1]
    Bot = np.concatenate([rows, arc]); Off = T_LINK * Bot / np.linalg.norm(Bot, axis=2)[:, :, None]
    return _outward(REF.grid_solid(Bot, Off)), dict(root_mm=ARM_ROOT, stations=int(len(Bot)), raised_root_rows=int((want > lv + 1e-6).sum()),
                                                    lifted_over_strap_mm=[round(float(x), 3) for x in lifted], 
                                                    level_root_mm=round(float(want[0]), 2), level_tip_mm=round(float(dg["rA"]), 2))


def arm_over_strap(dg, rows, nw=9):
    """radial lift (mm) per straight-run row so the arm's underside keeps RUNG over link 1b's BUILT strap over the crank's whole
    swing (phi 0 .. phi(dK_lim)); the model checks its arm against its own strap samples, the built strap is the fitted slab;
    lifts spread to the neighbours on the 60-deg ramp rule"""
    import igl
    V, F = np.ascontiguousarray(dg["strap_L1b"].vertices, float), np.ascontiguousarray(dg["strap_L1b"].faces, np.int64)
    phis = dg["sig"] * RF.phi_of(np.linspace(0.0, dg["lim"], 6), dg["g"], dg["c"]); need = np.zeros(len(rows))
    for i in range(len(rows)):
        w = np.linspace(0, 1, nw); X = rows[i, 0][None] + w[:, None] * (rows[i, 3] - rows[i, 0])[None]
        if i + 1 < len(rows):
            X2 = rows[i + 1, 0][None] + w[:, None] * (rows[i + 1, 3] - rows[i + 1, 0])[None]; X = np.r_[X, 0.5 * (X + X2)]
        for ph in phis:
            Xr = np.ascontiguousarray(X @ S.rotm(dg["dR"], ph)[0].T, float)
            sd = float(igl.signed_distance(Xr, V, F)[0].min()); need[i] = max(need[i], RUNG + 0.02 - sd)
    need = np.maximum(need, 0.0); d = np.linalg.norm(np.diff(rows.mean(axis=1), axis=0), axis=1); k = math.tan(math.radians(S.RAMP))
    for _ in range(len(rows)):                                       # ramp: a lifted row lifts its neighbours to <= 60 deg
        for i in range(len(rows) - 1):
            need[i + 1] = max(need[i + 1], need[i] - k * d[i]); need[i] = max(need[i], need[i + 1] - k * d[i])
    return need


def lug_mesh(dg, ncol=5):
    """the flank lug of link 1a (member-1 home frame): the model's band behind the synthesised flank (contact point Q + s n, s 0.3..6)
    over the used stroke, on the sphere |X| = |C0| - 1.5, 3 mm thick radially, plus the radial root from hub K's rim (r HUB_R + 0.5,
    at hub K's member level + hl) rising to the band's first station"""
    uK, rL = dg["uK"], dg["rL"]; Q1, N1, pick = dg["Q1"], dg["N1"], dg["pick"]; sv = np.linspace(0.3, LUG_BACK, ncol)
    plane = lambda X: X / np.linalg.norm(X, axis=-1)[..., None] * rL
    band = np.array([[plane(Q1[j] + s_ * N1[j]) for s_ in sv] for j in pick])
    b0 = band[0]; rb = np.linalg.norm(b0 - (b0 @ uK)[:, None] * uK, axis=1); hb = b0 @ uK; db = (b0 - hb[:, None] * uK) / rb[:, None]
    nr = max(2, int(math.ceil(float((rb - S.HUB_R).max()) / 1.0)))
    root = []
    for t_ in np.linspace(0.0, 1.0, nr + 1)[:-1]:
        r_ = S.HUB_R + 0.5 + t_ * (rb - S.HUB_R - 0.5); h_ = (1 - t_) * dg["lvK"] + t_ * hb
        x_ = h_[:, None] * uK + r_[:, None] * db; root.append(unit(x_) * ((1 - t_) * np.linalg.norm(x_, axis=1) + t_ * rL)[:, None])
    Bot = np.concatenate([np.array(root), band]); Off = T_LINK * Bot / np.linalg.norm(Bot, axis=2)[:, :, None]
    m = _outward(REF.grid_solid(Bot, Off))
    # the roller's swept path (link 1a frame) vs the lug: the model keeps lug samples >= ROLL_R + 0.3 off the roller-centre path
    from scipy.spatial import cKDTree
    Pp = dg["P1"][: dg["jl"] + 1]; Xs = np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 6000, seed=7)[0]]
    dmin = float(cKDTree(Pp).query(Xs)[0].min())
    return m, dict(band_rows=len(pick), root_rows=nr, s_mm=[round(float(x), 2) for x in sv], shell_r_mm=round(rL, 3),
                   r_from_uK_mm=[round(float(np.linalg.norm(Bot[..., :] - (Bot @ uK)[..., None] * uK, axis=-1).min()), 2),
                                 round(float(np.linalg.norm(Bot - (Bot @ uK)[..., None] * uK, axis=-1).max()), 2)],
                   roller_path_clear_mm=round(dmin - ROLL_R, 3), stroke_deg=round(math.degrees(dg["lim"]), 3))


def drive_parts(M, lg, dg):
    """[(group, member, name, mesh, material)] of the roller-flank drive + its info"""
    D = M.D; P = D.p; out = []
    lobe, linfo = lobe_mesh(M, lg, dg)
    out.append(("l2", 2, f"drive lobe keep-out (hub-2 rim lobe on link 2's rotor: r {linfo['r_lobe']:.2f} -> {linfo['r_at_stopB']:.2f} mm over {linfo['sweep_deg']:.1f} deg "
                f"of q2, lift s_arm x phi, phi = dK / g; {LOBE_Z[1] - LOBE_Z[0]:.0f} mm band F+{LOBE_Z[0]:.2f}..F+{LOBE_Z[1]:.2f})", lobe, "steel"))
    dR = dg["dR"]; zb = dg["zboss_built"]
    out.append(("dk", 9, f"drive bell crank boss keep-out (O10 x {BOSS_H:g} mm, bore O{2 * BORE_R:.1f} on the O3 pivot pin, two MR63ZZ 3x6x2.5 inside; "
                f"underside {zb:.2f} mm from GH = link 1b's highest top under its footprint + {RUNG:g}; the model's {dg['zboss']:.2f})", tube(np.zeros(3), dR, zb, zb + BOSS_H, 5.0, BORE_R), "ti"))
    am, ainfo = arm_mesh(dg, zb)
    out.append(("dk", 9, f"drive bell crank bent arm keep-out (6 x {T_LINK:g} mm Ti: straight run {dg['Lch']:.1f} mm at the model's stepped levels, tangent arc "
                f"r_c {dg['rc']:.2f} about hub K's axis over {math.degrees(abs(dg['beta'] - dg['psT'])):.1f} deg at radius {dg['rA']:.2f} from GH, {ARM_END:g} mm past the roller)", am, "ti"))
    C0 = dg["C0"]; cr = unit(C0)
    out.append(("dk", 9, f"drive roller keep-out (MR63ZZ 3x6x2.5, radial axis, centre {dg['R0']:.2f} mm from GH at r_c {dg['rc']:.2f} from hub K's axis)",
                tube(C0, cr, -ROLL_W / 2, ROLL_W / 2, ROLL_R, ROLL_BORE), "steel"))
    z_top = dg["rA"] - dg["R0"] + 1.5
    out.append(("dk", 9, f"drive roller stub + retaining head keep-out (O3 stub integral to the crank arm, O{2 * HEAD_R:g} x {HEAD_T:g} head on the skin side of the roller)",
                stepped(C0, cr, [(0.0, -ROLL_W / 2 - HEAD_T), (HEAD_R, -ROLL_W / 2 - HEAD_T), (HEAD_R, -ROLL_W / 2), (STUB_R, -ROLL_W / 2), (STUB_R, z_top), (0.0, z_top)]), "ti"))
    lev = dg["lev"]
    out.append(("l1b", 7, f"drive crank pivot pin keep-out (O3 h6 hardened, pressed in link 1b's strap {lev:.1f}..{lev + T_LINK:.1f}, through the boss)",
                REF.cyl(np.zeros(3), dR, lev, zb + BOSS_H + RUNG + CLIP_H, r=PIN_R), "steel"))
    out.append(("l1b", 7, f"drive crank pin clip keep-out (DIN 6799 RS 2.3, O6 x {CLIP_H:g} over the boss top + {RUNG:g})",
                tube(np.zeros(3), dR, zb + BOSS_H + RUNG, zb + BOSS_H + RUNG + CLIP_H, 3.0, PIN_R - 0.05), "steel"))
    lug, ginfo = lug_mesh(dg)
    out.append(("l1a", 1, f"drive flank lug keep-out (link 1a: the conjugate flank band 0.3..{LUG_BACK:g} mm behind the contact over the used stroke "
                f"0..{math.degrees(dg['lim']):.2f} deg of K, 3 mm Ti on the sphere r {dg['rL']:.2f}, root from hub K's rim; 5-axis / tilting-head wire-EDM flank)", lug, "ti"))
    info = getattr(M, "_sc_info", {}) or {}
    return out, dict(lobe=linfo, arm=ainfo, lug=ginfo, boss_level_mm=round(zb, 3), roller_centre_mm=np.round(C0, 3).tolist(), roller_r_from_GH_mm=round(dg["R0"], 3),
                     r_c=dg["rc"], beta_deg=round(math.degrees(dg["beta"]), 3), g=dg["g"], sig=dg["sig"], s_arm=float(P["s_arm"]), r_lobe=float(P["r_lobe"]),
                     hl=float(P["hl"]), lift=dg["lift"], arc_vs_model_mm=dg["arc_dev_mm"], dK_lim_deg=round(math.degrees(dg["lim"]), 3),
                     cam=M._cam_table and {k: info.get(k) for k in ("dK_lim", "why_lim", "pa_crank_rest", "pa_horn_rest", "pa_crank_max_taken", "pa_horn_max_taken",
                                                                     "flank_rho_min", "contact_r", "clear_hubK_min", "clear_roll_hubK_min", "clear_lowarm_lug_min",
                                                                     "phi_max_taken", "crest_exact", "arm_len", "arc_deg", "lug_r_max", "stub_head")},
                     model_sidecar=info)


# ---------------------------------------------------------------------------------------------------- parts
L1A_PATH = dict(ramp_deg=60.0, R=2.0, clr_J1=0.15, run_K=0.2, ext=3.0)      # link 1a's line/arc chain (the full CAD's: one source for both)


def link1a_path(M):
    """the centre-line chain of link 1a in span(u1, uK) (2-D: x along u1, y across; origin GH, both axes through it): start at the
    J1 seat face (J1 skirt + clr_J1: the climb starts outside the base's J1 upper boss - the gen-6 L1's R6 fault was the model
    strap's footprint lift rising INSIDE it), concave bend R, ramp at <= ramp_deg (the user's 60-deg ruling), convex bend R onto the
    K pad plane, a short run to the K seat face (solved, >= hr_K + 0.05). Returns (ex, ey, start, segs, info). Used by the L1 strap
    keep-out below and by pipeline/conformal/param_cad/user_style_roller.py (link 1a), so both are the same part."""
    sys.path.insert(0, os.path.join(REPO, "pipeline", "conformal", "param_cad")); import sketch2d as SK
    Uu, C, F4, hr = MIN.joints4(M); u1, uK = unit(Uu[0]), unit(Uu[1]); T = T_LINK
    assert np.linalg.norm(C[0]) < 1e-6 and np.linalg.norm(C[1]) < 1e-6, "link 1a's chain assumes J1 and K axes through GH"
    ex = u1; ey = unit(uK - (uK @ ex) * ex); phi = math.acos(float(np.clip(uK @ ex, -1, 1)))
    ha, hb = F4[0] + T / 2, F4[1] + T / 2; R = L1A_PATH["R"]; Ls_a = hr[0] + L1A_PATH["clr_J1"]; a1 = L1A_PATH["run_K"]
    B = hb * np.array([math.cos(phi), math.sin(phi)]); back = np.array([math.sin(phi), -math.cos(phi)])
    start = (ha, Ls_a, math.pi / 2); best = None
    for a_deg in np.arange(L1A_PATH["ramp_deg"], 20.0, -0.5):
        a = math.radians(a_deg)
        x1, y1, p1 = SK.advance(*start, -1.0 / R, R * a); d1 = np.array([math.cos(p1), math.sin(p1)])
        x2, y2, p2 = SK.advance(0.0, 0.0, p1, 1.0 / R, R * (a + phi)); v2 = np.array([x2, y2]); d2 = np.array([math.cos(p2), math.sin(p2)])
        sol = np.linalg.solve(np.c_[d1, -back], B - np.array([x1, y1]) - v2 - a1 * d2); Lr, Ls_b = float(sol[0]), float(sol[1])
        if Lr >= 0.0 and Ls_b >= hr[1] + 0.05: best = (a, Lr, Ls_b); break
    assert best is not None, "link 1a: no ramp <= 60 deg closes the dyad"
    a, Lr, Ls_b = best
    segs = [(-1.0 / R, R * a), (0.0, Lr), (1.0 / R, R * (a + phi)), (0.0, a1)]
    end = SK.end_pose(start, segs); E = B + Ls_b * back
    assert np.allclose(end[:2], E, atol=1e-6) and abs(end[2] - (math.pi / 2 + phi)) < 1e-9, (end, E)
    return ex, ey, start, segs, dict(ramp_deg=round(math.degrees(a), 2), ramp_mm=round(Lr, 3), K_run_mm=a1, bend_R_centre_mm=R, bend_R_inner_mm=R - T / 2,
                                    seat_J1_mm=round(Ls_a, 3), seat_K_mm=round(Ls_b, 3), dyad_deg=round(math.degrees(phi), 3), sd_b=back,
                                    climb_starts_at_J1_skirt_plus_mm=L1A_PATH["clr_J1"])


def link1a_strap_mesh(M):
    """the L1 keep-out of link 1a = the full CAD's bar: the 8 x 3 section swept along link1a_path, extended ext mm straight into each
    pad (over the J1 / K lower plates, same member) so the strap closes onto the plate keep-outs; a closed mesh, member-1 frame"""
    sys.path.insert(0, os.path.join(REPO, "pipeline", "conformal", "param_cad")); import sketch2d as SK
    ex, ey, start, segs, info = link1a_path(M); e = L1A_PATH["ext"]; nP = unit(np.cross(ex, ey))
    st = SK.advance(*start, 0.0, -e); segs2 = [(0.0, e)] + list(segs) + [(0.0, e)]
    P, Hd, _ = SK.sample(st, segs2, m=24); keep = np.r_[True, np.linalg.norm(np.diff(P, axis=0), axis=1) > 1e-6]; P, Hd = P[keep], Hd[keep]
    nrm = np.c_[np.sin(Hd), -np.cos(Hd)]; T, W = T_LINK, W_LINK
    ring = lambda p, n_: [(p[0] + s * T / 2 * n_[0]) * ex + (p[1] + s * T / 2 * n_[1]) * ey + w * W / 2 * nP for s, w in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    V = np.array([v for p, n_ in zip(P, nrm) for v in ring(p, n_)]); F = []; N = len(P)
    for i in range(N - 1):
        for k in range(4):
            a, b = 4 * i + k, 4 * i + (k + 1) % 4; F += [[a, b, b + 4], [a, b + 4, a + 4]]
    F += [[0, 2, 1], [0, 3, 2], [4 * (N - 1), 4 * (N - 1) + 1, 4 * (N - 1) + 2], [4 * (N - 1), 4 * (N - 1) + 2, 4 * (N - 1) + 3]]
    m = trimesh.Trimesh(V, np.array(F), process=True); trimesh.repair.fix_normals(m)
    assert m.is_watertight and m.volume > 0, "link 1a strap mesh not closed"
    info.pop("sd_b"); return m, info


def build_parts(M, lg, dg, knee_geom=None):
    """[(group, member, name, mesh in the MEMBER-LOCAL home frame, material)]; member 5 = arm-fixed (canonical arm frame)"""
    D = M.D; P = D.p; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; lc = float(P["lc"])
    U, C, F4, hr = MIN.joints4(M); H = lambda k: C[k] + F4[k] * U[k]; out = []
    capK = float(P.get("capK", 0) or 0)
    prof = MIN.link_rows(M); straps = {}
    for nm in ("L1a", "L1b", "L2"):
        lk, rows = prof[nm]; straps[nm] = MIN.link_solid(M, lk, rows)
    straps["L1a_model"] = straps["L1a"]                                         # the model's strap (its footprint lift rises inside J1's upper boss: R6 0.98)
    straps["L1a"], dg["link1a_chain"] = link1a_strap_mesh(M)                    # gen-6 fix: the full CAD's chain, climb from J1's skirt + 0.15 on a <= 60-deg ramp
    out.append(("base", 0, "J1 upper boss + cap keep-out (O20, F+3.15..F+12.25; base = J1's upper member, carried directly by the scapula handler at the hub ring)",
                REF.cyl(H(0), U[0], UP, CROWN, r=hr[0]), "ti"))
    out.append(("l1a", 1, "J1 lower plate keep-out (O20 x 3, link 1a)", REF.cyl(H(0), U[0], 0.0, PLATE, r=hr[0]), "ti"))
    out.append(("l1a", 1, f"link 1a strap keep-out (8 x 3 mm Ti, J1 -> K: the full CAD's line/arc chain, climb from J1's skirt + {L1A_PATH['clr_J1']:g} on a {dg['link1a_chain']['ramp_deg']:g}-deg ramp, R{L1A_PATH['R']:g} bends)", straps["L1a"], "ti"))
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
                        f"below the drive's onset and force-closes both rolling pairs (flank on the roller, follower on the lobe); K SLAVED to q2 by the roller-flank drive past it, never read)", REF.cyl(H(1), U[1], UP, CROWN + capK, r=hr[1]), "ti"))
            out.append(("l1b", 7, "link 1b strap keep-out (8 x 3 mm Ti, fitted underside, K -> J2)", straps["L1b"], "ti"))
    out.append(("l2", 2, "J2 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2; the rotor that carries the drive lobe)", REF.cyl(H(2), U[2], UP, CROWN, r=hr[2]), "ti"))
    out.append(("l2", 2, "link 2 strap keep-out (8 x 3 mm Ti, fitted underside, J2 -> J3)", straps["L2"], "ti"))
    out.append(("l2", 2, "J3 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2)", REF.cyl(H(3), U[3], UP, CROWN, r=hr[3]), "ti"))
    out.append(("l3", 3, "J3 lower plate keep-out (O20 x 3, member 3)", REF.cyl(H(3), U[3], 0.0, PLATE, r=hr[3]), "ti"))
    dg["zboss_built"] = boss_level(dg, straps["L1b"]); dg["strap_L1b"] = straps["L1b"]
    dparts, dinfo = drive_parts(M, lg, dg); out += dparts
    dinfo["stack_fix"] = dict(boss_underside_model_mm=round(dg["zboss"], 3), boss_underside_built_mm=round(dg["zboss_built"], 3),
                              raised_mm=round(dg["zboss_built"] - dg["zboss"], 3),
                              why="the model stacks the boss on its 6 link-1b strap samples nearest the pivot; the built boss + the arm root sit on the "
                                  "strap's highest top under the O10 footprint + 0.15 (raised only if the strap climbs there); the arm keeps the model's "
                                  "levels from there, the roller / flank (the cam) are unchanged")
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
    """minarc's built-part pairs + the drive's (crank boss / arm / roller / stub head / pin / lobe / flank lug vs their neighbours)"""
    MIN.set_adjacent(parts)
    find = lambda s: next((p for p in parts if p[2].startswith(s)), None)
    pairs = [("drive bell crank boss", b) for b in ("link 1b strap", "J2 upper boss", "drive lobe", "K upper boss")] + \
            [("drive bell crank bent arm", b) for b in ("link 1b strap", "J2 lower plate", "J2 upper boss", "link 2 strap", "K upper boss", "drive flank lug")] + \
            [("drive roller keep-out", b) for b in ("drive flank lug", "K upper boss", "link 1b strap")] + \
            [("drive roller stub", b) for b in ("drive flank lug", "K upper boss", "link 1b strap")] + \
            [("drive flank lug", b) for b in ("link 1b strap", "K upper boss")] + [("drive lobe", b) for b in ("link 1b strap", "J2 lower plate")]
    seen = set()                                                                # the moving drive pairs that can meet (a lean list: adj_built runs per frame)
    for a_, b_ in pairs:
        A, Bp = find(a_), find(b_)
        if A is None or Bp is None or A[1] == Bp[1] or (A[2], Bp[2]) in seen: continue
        seen.add((A[2], Bp[2]))
        XA = np.r_[np.asarray(A[3].vertices), trimesh.sample.sample_surface_even(A[3], 1500, seed=3)[0]]
        BASE.ADJ_PAIRS.append((A[2][:24], A[1], XA, Bp[2][:24], Bp[1], np.ascontiguousarray(Bp[3].vertices, float), np.ascontiguousarray(Bp[3].faces, np.int64)))


def drive_sweep(M, parts, lg, dg, dq=2.0):
    """red team of the drive's own motion, pose-independent: in link 1b's frame over the whole J2 window (q2lo .. stop B), link 2
    turns by q2 about u2, K opens by the law dK(q2), link 1a turns by -dK about uK, the
    crank by phi(dK). Every pair with a drive part on two different members: worst signed distance (mm, negative = inside) and where"""
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
        if mem == 9: R, t = Xd[9]; return R[j], t[j]
        return None
    cand = [p for p in parts if p[1] in (1, 2, 7, 9)]
    out = {}
    for ga, ma, na, mesh_a, _ in cand:
        if not na.startswith("drive"): continue
        XA = smp(mesh_a)
        for gb, mb, nb, mesh_b, _ in cand:
            if mb == ma: continue
            Vb, Fb = np.ascontiguousarray(mesh_b.vertices, float), np.ascontiguousarray(mesh_b.faces, np.int64)
            best = (1e9, None); first = None
            for j in np.argsort(qs * lg["law"]["s_q"]):                     # from the folded stop toward stop B (|dK| rising)
                Ra, ta = pose(ma, j); Rb, tb = pose(mb, j); XB = ((XA @ Ra.T + ta) - tb) @ Rb
                v = float(igl.signed_distance(XB, Vb, Fb)[0].min())
                if v < best[0]: best = (v, j)
                if v < BASE.ADJ and first is None: first = j
            out[f"{na[:44]} | {nb[:44]}"] = (round(best[0], 3), round(float(qs[best[1]]), 1), round(float(dks[best[1]]), 1),
                                             None if first is None else round(float(dks[first]), 1))
    return dict(sorted(out.items(), key=lambda kv: kv[1][0]))


def law_check(M, K, idx, dg):
    """per pose: the slaved K vs the law, from the member frames; the CAM closure in the world: the posed roller centre (crank
    frame) read in link 1a's posed frame vs the synthesised roller-centre path on the flank at that |dK| (mm)"""
    from scipy.spatial.transform import Rotation as Rot
    D = M.D; lg = M._lg; out = []; kdeg = np.degrees(dg["kgrid"]); C0 = dg["C0"]; P1 = dg["P1"]
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); BASE.swap_in(M, K)
    try:
        for i in idx:
            R1, t1 = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i); R9, t9 = M.T(9, i)
            dK = float(np.degrees(Rot.from_matrix(R1.T @ R1b).as_rotvec() @ D.uK)); q2 = float(np.degrees(Rot.from_matrix(R1b.T @ R2).as_rotvec() @ D.u[1]))
            want = float(dK_of_q2(lg, q2)) if K["state"][i] == 1 else 0.0
            Cw = R9 @ C0 + t9; C1a = R1.T @ (Cw - t1)
            ref = np.array([np.interp(abs(dK), kdeg, P1[:, k]) for k in range(3)])
            out.append(dict(pose=int(i), state=int(K["state"][i]), q2_deg=round(q2, 3), dK_deg=round(dK, 3), dK_law_deg=round(want, 3),
                            err_deg=round(abs(abs(dK) - want), 4), cam_closure_mm=round(float(np.linalg.norm(C1a - ref)), 4)))
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    return out


# ---------------------------------------------------------------------------------------------------- check vs the model
def check_frames(M, dd, parts, stack):
    """MIN.check_frames on this chain + the drive member: (a) the model's metal samples (hubs, E, boss, pad, knee, crank arm, roller +
    stub head, flank lug, link straps) posed by the model's own member transforms vs the posed exo.glb of their group: unsigned
    distance to the surface AND the outside distance (winding number: a sample inside the built keep-out reads 0)
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
                win = igl.fast_winding_number(np.ascontiguousarray(meshes[g].vertices, float), np.ascontiguousarray(meshes[g].faces, np.int64), np.ascontiguousarray(Pw, float))
                dout = np.where(win > 0.5, 0.0, d)
                if name == "hub2":
                    dl = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes["l1b"].vertices, float),
                                                                 np.ascontiguousarray(meshes["l1b"].faces, np.int64))[0]); d = np.minimum(d, dl)
                if name in ("hubK", "hub2"):
                    k = 1 if name == "hubK" else 2; cen = C[k] + F4[k] * U[k]; w = Xp - cen; rr = np.linalg.norm(w - (w @ U[k])[:, None] * U[k], axis=1)
                    inslot = (rr > MIN.SLOT_RS - MIN.DOWEL_R - MIN.SLOT_CLR - 0.6) & (rr < MIN.SLOT_RS + MIN.DOWEL_R + MIN.SLOT_CLR + 0.6)
                    res[name + " (slot band)"] = [round(float(d[inslot].max()), 4) if inslot.any() else None, int(inslot.sum())]
                    d = d[~inslot]; dout = dout[~inslot]
                res[name] = [round(float(d.max()), 4), round(float(np.percentile(d, 95)), 4), round(float(dout.max()), 4)]
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
        worst_out = max(v[2] for k, v in res.items() if not k.startswith(("L1", "L2")) and "slot band" not in k and v[0] is not None)
        worst_l = max(v[0] for k, v in res.items() if k in ("L1a", "L1b", "L2"))
        drv = {k: res[k] for k in ("crank", "roller", "horn") if k in res}
        out.append(dict(label=lab, bench_pose=int(i), pose=[round(float(x), 2) for x in pz[:3]], taken=bool(i in set(taken)), state=int(K["state"][i]),
                        rigid_samples_max_mm=round(worst, 4), rigid_samples_outside_max_mm=round(worst_out, 4), strap_samples_max_mm=round(worst_l, 4),
                        drive_samples_mm=drv,
                        per_part=res, frame_dev_mm=round(fdev, 6), res_deg=round(float(K["res"][i]), 4), knee_angle=round(float(K["Kn"]["ang"][i]), 1),
                        m3e=round(float(K["m3e"][i]), 2), stops=inside))
        print(f"  check {lab:38s} pose {i} {np.round(pz[:3], 1)} st {int(K['state'][i]):+d}: rigid vs glb max {worst:.4f} mm, outside {worst_out:.4f} (drive [max, p95, out] {drv}), straps {worst_l:.3f}, "
              f"frames dev {fdev:.2e}, dK {inside['K']['angle_deg']:.2f} q2 {inside['J2']['angle_deg']:.2f} dowels in slot {inside['K']['inside']} / {inside['J2']['inside']}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="l1_roller-longdyad")
    ap.add_argument("--jobs", type=int, default=1); ap.add_argument("--no-clips", action="store_true"); ap.add_argument("--skin-only", action="store_true")
    a = ap.parse_args(); t0 = time.time(); fb = (60, 160); fbs = "Bench(60,160)"
    if a.skin_only:
        dd = os.path.join(BASE.FULL, "designs", a.out); B_ = json.load(open(os.path.join(dd, "build.json")))
        B_["drive_skin"] = drive_skin(dd); json.dump(B_, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
        print(json.dumps({k_: v for k_, v in B_["drive_skin"].items() if k_ != "per_clip"}, default=float)); return
    import concept_kit as KIT
    dd = os.path.join(BASE.FULL, "designs", a.out); os.makedirs(dd, exist_ok=True)
    M, rep = fit(); D = M.D; P = M.p
    if M.B.mode != "fast": print(f"WARNING: the fit bench {fbs} ran {M.B.mode}, not fast", flush=True)
    lg = law_geom(M); M._lg = lg; dg = drive_geom(M)
    print(f"fit (claim RLModel, BEST + ang_min {CFG['ang_min']}) on {fbs} {M.B.mode} (fold margin {KIT.FOLD_MARGIN}): near-touch gap {rep['gap']} reach {rep['reach']} ib14 {rep['inband14']} "
          f"ib10 {rep['inband10']} contact {rep['contact']} near1 {rep.get('gap_near1')} near2 {rep.get('gap_near2')} | f {np.round(M.f, 3).tolist()} fK {M.fK:.3f} tr {M.tr:.2f} cam {M._sc_info} "
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
    law = lg["law"]; dinfo = stack["drive"]
    kin = dict(az=az, el=elv, a=[math.degrees(D.A[0]), math.degrees(D.A[1])], w=[w_d, w_a], branch=int(D.branch), order=[0, 1, 1],
               axis_points_mm=[np.round(c_, 3).tolist() for c_ in D.c], axes=[np.round(u_, 6).tolist() for u_ in D.u],
               axis_line_offsets_mm=[round(float(np.linalg.norm(c_)), 2) for c_ in D.c], u2_check_deg=round(math.degrees(math.acos(float(np.clip(chk @ u2, -1, 1)))), 5),
               seats=dict((k_, P[k_]) for k_ in ("az1", "el1", "az2", "el2", "wd", "wa", "b3")),
               knee=dict((k_, P[k_]) for k_ in ("lE", "lc", "phiE", "phib", "stk", "ang_min")), knee_mid_m_mm=np.round(D.m, 3).tolist(), hub_r_mm=list(M.hr),
               knuckle=dict(uK=np.round(D.uK, 6).tolist(), bk1=P["bk1"], bk2=P["bk2"], psiA_deg=round(math.degrees(D.psiA), 3), a1max=P["a1max"],
                            dK_stop_B_deg=stack["stops"]["K"]["stop_B_deg"], q2_stops_deg=stack["stops"]["J2"]["q2_stops_deg"], smlo=P["smlo"], smhi=P["smhi"],
                            slaved=dict(law="dK = kK (q2 - q2hi) along the stretching sense (lin), cut at the drive's own range dK_lim", kK=law["kK"],
                                        q2_onset_deg=law["q2hi_deg"], s_q=law["s_q"], dK_lim_deg=law["dK_stop_deg"], r_lobe=float(P["r_lobe"]), s_arm=float(P["s_arm"]),
                                        g=float(P["g"]), beta=float(P["beta"]), r_c=float(P["r_c"]), lift=float(P["lift"]), hl=float(P["hl"]), zr=float(P["zr"])),
                            note="az/el/a/w = the 3R with K on stop A; past the onset q2hi K is SLAVED to q2 by the roller-flank drive (lobe -> bell crank -> "
                                 "roller -> conjugate flank on link 1a; 3 active DOF; K never free, never read); the bell crank (dk) is a posed side member of link 1b"))
    design = dict(id=a.out, source=f"docs/concepts/{ID}.md (the verified config: docs/concepts/rows/{ID}.json best_params = docs/concepts/verify/{ID}.py BEST, "
                                   f"ang_min {CFG['ang_min']} = the auditor's knee fix), fit on {fbs} {M.B.mode} at fold margin {KIT.FOLD_MARGIN} = the shape the "
                                   "verifier wore frozen on Bench(110,360) exact (v_gap 18.67, score 93.21, envelope-corrected 18.56; held out 23.73, 23.72 at ang_min 26.88)",
                  params=dict(CFG), n_joints=4, sliding_cuff=False, dof=3,
                  passive=dict(count=2, translations=0, rotations=2, outside_dof_count=True, sensed=0,
                               kind="flat two-pin knee closing the loop at the cuff (pins a, b parallel to J3; NO encoders - pose from the 3 hub encoders, "
                                    "user 2026-10-17); set by loop closure. K (4th revolute) is NOT a DOF: slaved to q2 by the roller-flank drive past the onset, "
                                    "spring-held on stop A below it; the bell crank is set by the law phi = |dK| / g",
                               components=[dict(pin="a", between="member 3 (E boss) / knee link", part="IGLIDUR-PIN: iglidur GSM sleeve + 2 GTM washers on an integral O4 Ti pin, DIN 6799 RS 3.2 e-clip land",
                                                stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]]),
                                           dict(pin="b", between="knee link / arm pad (cuff)", part="IGLIDUR-PIN (as pin a)", stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]])]),
                  joints=[dict(joint="J1", part="O20 x 12.25 v5 hub, MR117-2RS pair, encoder", axis_offset_mm=kin["axis_line_offsets_mm"][0]),
                          dict(joint="K", part=f"O20 v5 hub, MR117-2RS pair, cap {CROWN + float(P.get('capK', 0)):.2f} mm (clock spring: holds stop A, force-closes both rolling pairs); "
                                                f"stops A / B = an opposed pair of O3 dowels in two {stack['stops']['K']['travel_deg']:.1f}-deg arc slots; slaved (no encoder)",
                               axis_offset_mm=0.0, passive=False, slaved=True, sensed=False),
                          dict(joint="J2", part=f"O20 x 12.25 v5 hub, MR117-2RS pair, encoder; drive lobe on its rotor; q2 stops = O3 dowel in a "
                                                 f"{stack['stops']['J2']['travel_deg']:.1f}-deg arc slot (folded stop q2lo, stop B at the drive's range)", axis_offset_mm=kin["axis_line_offsets_mm"][1]),
                          dict(joint="J3", part="O20 x 12.25 v5 hub, MR117-2RS pair, encoder", axis_offset_mm=kin["axis_line_offsets_mm"][2])],
                  drive=dict(kind="roller-flank: hub-2 rim lobe -> bell crank on link 1b (MR63ZZ pair on an O3 pin; follower on the short arm s_arm, bent long arm "
                                  "to r_c about hub K) -> MR63ZZ roller on an integral O3 stub -> conjugate spherical flank milled in link 1a's lateral boss (5-axis / "
                                  "tilting-head wire-EDM); one clock spring on K force-closes both rolling pairs; no rod, no ball links",
                             components=["MR63ZZ 3x6x2.5 x 2 (crank pivot)", "O3 h6 pin + DIN 6799 RS 2.3", "MR63ZZ 3x6x2.5 (flank roller) on an integral O3 stub + O4.5 x 0.8 head",
                                         "follower on the short arm (L2)"], **dinfo),
                  kinematics=kin, base=dict(mount="girdle", chain="roller_longdyad_knuckle", note="base rides the scapula on the user's scapula handler, carried directly at the J1 hub ring (no tab)"),
                  built_with="pipeline/concept_l1/build_roller_l1.py (L1 keep-out meshes: O20 hub keep-outs incl. hub K's 6 mm taller cap, fitted 8 x 3 straps 1a / 1b / 2, stop "
                             "dowels + arc slots, the lobe / bell crank boss / bent arm / roller / stub head / pin / flank lug drive (crank posed), E strap + boss, knee link + knee stop, "
                             "arm pad, pin retainers)",
                  label=f"roller-longdyad-knuckle-3r (verified config, ang_min {CFG['ang_min']}, fit {fbs}, fold margin {KIT.FOLD_MARGIN:g}), L1 keep-out", fit_bench=list(fb),
                  fold_margin=KIT.FOLD_MARGIN, build_fixes=dict(k_pair=True, j2_single_dowel_push_limit=True, e_cap=True, knee_stop_deg=knee_stop, ang_min_fix=CFG["ang_min"]),
                  faces_mm=[round(float(x), 2) for x in M.f], fK_mm=round(float(M.fK), 2), tr=round(float(M.tr), 2), stack_mm=stack,
                  bench=dict(near_touch_gap=rep["gap"], **{k_: rep[k_] for k_ in ("reach", "follow", "inband14", "contact")}, inband10=rep["inband10"]),
                  note="R17's dynamics judge orders posed groups as a serial chain (base, l<k>[a-z], cuff); the drive's side member dk rides link 1b "
                       "(build.json 'slaved', drive_groups)")
    json.dump(design, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    set_adjacent(parts)
    pts = [(m, X) for m, X in M.rigid.values()] + [(m, X) for m, X in M.link_pts.values()] + list(M.contact)
    for g, mem, n, m, mat in parts:
        pts.append((mem, np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 300, seed=1)[0]]))
    rep_out = dict(fit=dict(params=dict(CFG), source=f"docs/concepts/rows/{ID}.json best_params (+ ang_min {CFG['ang_min']}) through the claim's RLModel", bench=f"{fb[0]},{fb[1]}",
                            mode=M.B.mode, fold_margin=KIT.FOLD_MARGIN,
                            report={k_: rep.get(k_) for k_ in ("gap", "plain", "gap_near1", "gap_near2", "near_touch_min_mm", "reach", "follow", "inband14",
                                                               "inband10", "contact", "why", "min_clear_taken", "parts_ib14")},
                            m=np.round(D.m, 3).tolist(), tr=round(float(M.tr), 3), fK=round(float(M.fK), 3), cam=M._sc_info),
                   law={k_: v for k_, v in law.items()}, stops=stack["stops"], stack=stack, mount=mrep, kin_u2_check_deg=kin["u2_check_deg"], dowel_check=MIN.dowel_check())
    rep_out["slaved"] = [slaved_decl(M, lg, Kf, kin_)]
    print(f"slaved: {rep_out['slaved'][0]}", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    dsw = drive_sweep(M, parts, lg, dg)
    rep_out["drive_sweep"] = dict(rule="signed distance (mm, negative = inside), worst over the J2 window in link 1b's frame; (mm, q2 deg, |dK| deg, first |dK| where < 0.15 mm)",
                                  pairs=dsw, worst=next(iter(dsw.items())) if dsw else None)
    print(f"drive sweep (worst 8): {list(dsw.items())[:8]}", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep_out["check"] = check_frames(M, dd, parts, stack)
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench
    try: rep_out["law_check"] = law_check(M, Kf, [c["bench_pose"] for c in rep_out["check"]] + list(np.nonzero(kin_ & (Kf["state"] == 1))[0]), dg)
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    lc_ = rep_out["law_check"]; st1 = [x for x in lc_ if x["state"] == 1]
    rep_out["law_check_summary"] = dict(poses=len(lc_), stretched=len(st1), max_err_deg=max((x["err_deg"] for x in lc_), default=None),
                                        dK_max_deg=max((abs(x["dK_deg"]) for x in st1), default=None),
                                        cam_closure_max_mm=max((x["cam_closure_mm"] for x in st1), default=None))
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
        rep_out["slaved_vs_clips"] = slaved_vs_clips(rep_out["slaved"][0], C)
        print(f"slaved law vs clip frames: {rep_out['slaved_vs_clips']}", flush=True)
        W = BASE.make_workspace(M, a.jobs); json.dump(W, open(os.path.join(dd, "workspace.json"), "w"), separators=(",", ":"))
        rep_out["workspace"] = dict(poses=len(W["poses"]), closes=round(float(np.mean([p["closes"] for p in W["poses"]])), 4),
                                    feasible_kin_parts=round(float(np.mean([p["eval_feasible"] for p in W["poses"]])), 4),
                                    driven_feasible=int(sum(1 for p in W["poses"] if p["eval_feasible"] and p["knuckle"]["state"] != 0)))
        print(f"workspace.json: {rep_out['workspace']} ({time.time() - t0:.0f} s)", flush=True)
        json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
        rep_out["drive_skin"] = drive_skin(dd)
        print(f"drive skin: { {k_: v for k_, v in rep_out['drive_skin'].items() if k_ != 'per_clip'} }", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s -> {dd}")


def slaved_decl(M, lg, K, kin):
    """the dynamics judge's slaved-K declaration (judge/dynamics.py "SLAVED COORDINATES") from the build's own law, in the clips'
    convention (x = q.1 = the chain's q2 deg, y = knuckle.dK = the chain's signed dK deg), checked against the fit-bench chain"""
    law = lg["law"]; ts = lg["ts_deg"]; dk = lg["dK_deg"]; m = ts <= law["t_stop_deg"] + 1e-9
    T = np.r_[ts[m], law["t_stop_deg"]] if ts[m][-1] < law["t_stop_deg"] - 1e-9 else ts[m]; DKa = np.interp(T, ts, dk)
    st1 = kin & (K["state"] == 1) & (np.abs(K["dK"]) > 1e-6)
    sgn = float(np.sign(np.median(K["dK"][st1]))) if st1.any() else 1.0
    X = law["q2hi_deg"] + law["s_q"] * T; Y = sgn * DKa; o = np.argsort(X); X, Y = X[o], Y[o]
    q2 = K["q"][:, 1]; err = None
    if st1.any(): err = round(float(np.abs(np.interp(q2[st1], X, Y) - np.degrees(K["dK"][st1])).max()), 4)
    return {"slaved": ["l1a", "l1b"], "driver": ["l1b", "l2"], "x_key": "q.1", "y_key": "knuckle.dK",
            "law_x_deg": [round(float(x), 4) for x in X], "law_y_deg": [round(float(y), 4) for y in Y], "rest_y_deg": 0.0, "closure": "force",
            "drive_groups": {"dk": "l1b"}, "source": "build.json law (lin: kK, q2hi, cut at the drive's own range dK_lim)",
            "check_fit_bench_max_err_deg": err, "check_fit_bench_poses": int(st1.sum()),
            "note": "K = law(q2) past the onset (lobe -> bell crank -> MR63ZZ roller -> conjugate flank on link 1a); below it the clock spring holds K on "
                    "stop A; the same spring keeps the flank on the roller and the follower on the lobe (force closure)"}


def slaved_vs_clips(decl, C):
    """the declaration vs every non-held clip frame (q.1, knuckle.dK): max |law(q2) - dK| on driven frames and |dK| on dwell frames"""
    X, Y = np.array(decl["law_x_deg"]), np.array(decl["law_y_deg"]); e_dr = []; e_dw = []
    for cl in C["clips"]:
        for f in cl["frames"]:
            if f["held"] or "knuckle" not in f: continue
            q2 = float(f["q"][1]); dK = float(f["knuckle"]["dK"]); y = float(np.interp(q2, X, Y))
            (e_dr if int(f["knuckle"].get("state", 0)) == 1 else e_dw).append(abs(y - dK) if int(f["knuckle"].get("state", 0)) == 1 else abs(dK))
    return dict(driven_frames=len(e_dr), driven_max_err_deg=round(max(e_dr), 4) if e_dr else None, dwell_frames=len(e_dw), dwell_max_dK_deg=round(max(e_dw), 4) if e_dw else None)


def drive_skin(dd, every=1):
    """the drive's skin clearance over EVERY clip frame (docs/research/geneva-rod-gen5_fix.md section 2's tool, same skin: body_pose.posed
    of the frame's pose, signed by winding number): each drive part (group dk, the flank lug on l1a, the lobe on l2) sampled densely in
    its member frame, posed by the frame's G / T; min signed distance (mm) per part, where, frames < 0.3 / < 2 mm"""
    import igl
    sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); import body_pose as BP
    C = json.load(open(os.path.join(dd, "clips.json"))); src = trimesh.load(os.path.join(dd, "exo.glb")); BF = np.ascontiguousarray(BP.F, np.int64)
    parts = {}
    for node in src.graph.nodes_geometry:
        g, nm = node.split("|")[:2]
        if not nm.startswith("drive") or "pivot pin" in nm or "pin clip" in nm: continue
        T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_)
        parts[nm[:40]] = (g, np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 6000, seed=11)[0]])
    best = {k: (1e9, None) for k in parts}; n03 = {k: 0 for k in parts}; n2 = {k: 0 for k in parts}; nfr = 0; per_clip = {}
    for cl in C["clips"]:
        cmin = 1e9
        for k, f in enumerate(cl["frames"]):
            if k % every: continue
            nfr += 1; Vb = np.ascontiguousarray(BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], f["p"]))), float)
            for nm, (g, X) in parts.items():
                Qp = np.ascontiguousarray(X @ np.array(f["G"][g]).reshape(3, 3).T + np.array(f.get("T", {}).get(g, [0, 0, 0])), float)
                d = np.sqrt(igl.point_mesh_squared_distance(Qp, Vb, BF)[0]); w = igl.fast_winding_number(Vb, BF, Qp) > 0.5; v = float(np.where(w, -d, d).min())
                if v < best[nm][0]: best[nm] = (v, f"{cl['name']} frame {k}{' (held)' if f['held'] else ''}")
                n03[nm] += v < 0.3; n2[nm] += v < 2.0; cmin = min(cmin, v)
        per_clip[cl["name"]] = round(cmin, 3)
    worst = min(best.items(), key=lambda kv: kv[1][0])
    return dict(rule=">= 0.3 mm on every frame (gen-5 lobe ring: -0.26)", frames=nfr, every=every, min_mm=round(worst[1][0], 3), where=f"{worst[0]}: {worst[1][1]}",
                passes=bool(worst[1][0] >= 0.3), per_part={k: dict(min_mm=round(v[0], 3), at=v[1], frames_lt_0p3=n03[k], frames_lt_2=n2[k]) for k, v in best.items()},
                per_clip=per_clip)


if __name__ == "__main__":
    main()
