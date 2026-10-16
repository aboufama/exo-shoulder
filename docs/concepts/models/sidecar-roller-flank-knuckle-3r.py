"""sidecar-roller-flank-knuckle-3r (round 8): the verified lead's slaved-knuckle chain (frontload-lobe-stopb-knuckle-3r: J1
acromion top, link 1a, K knuckle slaved and never read, link 1b, J2, link 2, J3, pin knee + cuff) with a RODLESS sidecar drive:
a bell crank on an MR63ZZ pair stacked on link 1b beside hub 2 (short arm s_arm on the hub-2 rim lobe), whose BENT long arm
(a straight run from the boss, then a tangent arc concentric with hub K at the roller radius r_c) carries an MR63ZZ roller
(O6 x 2.5 on an O3 shoulder pin) at the horn layer. The roller pushes a CONJUGATE FLANK cut in a lateral horn lug of link 1a.
K's clock spring keeps the flank on the roller and, through the crank, the follower on the lobe. 3 ACTIVE DOF (J1, J2, J3),
0 passive translations, no gears / pulleys / cables / rods.

THE CAM PAIR IS SYNTHESISED, NOT ASSUMED. The crank axis dR and K's axis uK both pass through GH, so the crank / link 1a
relative motion is a rotation about GH: a spherical cam with a radial roller axis. The law is chosen, phi = sig |dK| / g
(g = dK / dphi), so the lobe gate keeps its form (follower lift s_arm |dK| / g: r_horn := s_arm, i_rock := g in the lead's
per-t gated law). Per 0.25 deg of K (link 1b frame) the roller centre C, the two contact-point velocities v_C (crank) and
v_H (horn, at the contact point) and the contact normal n (tangent plane at C, n _|_ v_C - v_H) give
  * both pressure angles angle(n, v_C), angle(n, v_H) <= PA_MAX (45); n . v > 0 on both sides (no lift-off: the spring
    torque on K loads the flank, the crank then loads the lobe; both close iff both dot products stay positive);
  * the flank (the envelope of the roller circle, C + 3 n, in link 1a's frame) has no cusp / undercut, and where it is
    convex toward the roller its radius >= RHO_MIN (3.5);
  * the contact stays on the lug (contact radius from K's axis >= R_CMIN 13);
  * the arm and the roller keep >= 1 mm (+ half the arm thickness, the core's metric) off hub K's cylinder and the arm off
    hub 2; the low part of the arm keeps >= 1 mm off the swinging lug.
The first K step that fails ends the drive's own range (dK_lim); stop B sits there and every pose past it is lost on every
bench (the shared core's _truncate). The lug is built from the synthesised flank: a 6 mm band behind the flank over the used
stroke plus a radial root to hub K's rim, minus the roller's swept path (+0.3 mm).

THE MECHANISM CODE IS SHARED: per-pose transforms, the stacking rule, truncation and every part pair live in
docs/concepts/models/sidecar-longdyad-knuckle-3r.py (the rod sidecar); this file replaces only the drive metal and the
law-to-crank map (no RSSR: the crank angle is the law's phi(|dK|) directly).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/sidecar-roller-flank-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/sidecar-roller-flank-knuckle-3r.py frozen|held|flood '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("sidecar_core_for_rollerflank", os.path.join(HERE, "sidecar-longdyad-knuckle-3r.py"))
SC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SC)
FL, G, KR, KB, PK, S = SC.FL, SC.G, SC.KR, SC.KB, SC.PK, SC.S
unit = S.unit; D2R = math.pi / 180
ID = "sidecar-roller-flank-knuckle-3r"
PA_MAX, ROLL_R, ROLL_W, RHO_MIN, R_CMIN, LUG_BACK, RUNG = 45.0, 3.0, 2.5, 3.5, 13.0, 6.0, SC.RUNG
DK_IDLE = 30.0
LEAD_DYAD = {"bk1": 30.05, "bk2": 37.57, "a1max": 61.72}
SEED = dict(SC.LEAD, **LEAD_DYAD, law_mode="lin", kK=2.0, g=1.8, r_c=15.5, beta=-85.0, hl=3.15, zr=1.5, s_arm=5.0, r_lobe=7.5,
            chain="lead")
PARAMS = dict(SC.PARAMS, **SEED)


def _clamp(p):
    """component limits (CMA has no bounds): g 1.0-3.0 (dK / dphi), r_c 14-22 (roller radius from K's axis = the arm arc's
    radius), s_arm 4-6, lobe base 7-8.5, hl 0-3.15, zr >= 0; the lead's lobe law with r_horn := s_arm, i_rock := g"""
    if p.get("chain", "lead") == "lead": p.update(LEAD_DYAD)
    p["g"] = min(max(float(p["g"]), 1.0), 3.0); p["r_c"] = min(max(float(p["r_c"]), 14.0), 22.0)
    p["s_arm"] = min(max(float(p["s_arm"]), 4.0), 6.0); p["r_lobe"] = min(max(float(p["r_lobe"]), 7.0), 8.5)
    p["hl"] = min(max(float(p["hl"]), 0.0), 3.15); p["zr"] = max(float(p["zr"]), 0.0)
    p["i_rock"] = p["g"]; p["r_horn"] = p["s_arm"]; p["r_h"] = p["r_c"]; p["La"] = 0.0
    if p.get("law_mode", "lin") == "lin":
        p["kK"] = max(float(p["kK"]), 0.0); p["kA"] = p["kB"] = p["kK"]; p["t1"] = 6.0; p["law_mode_in"] = "lin"; p["law_mode"] = "seg"
    for k in ("kA", "kB"): p[k] = max(float(p[k]), 0.0)
    p["t1"] = max(float(p["t1"]), 0.5); p["smt"] = max(float(p.get("smt", 12.0)), 5.2)
    p["a1max"] = min(float(p["a1max"]), float(p["bk1"]) + float(p["bk2"]) - 5.0)
    return p


def _ring(c, r, axv, n=16): return SC._ring(c, r, axv, n)


def _ang(a, b):
    c = float(a @ b) / max(float(np.linalg.norm(a) * np.linalg.norm(b)), 1e-12); return math.degrees(math.acos(max(-1.0, min(1.0, c))))


class RFModel(SC.SCModel):
    def _sc_pose(self):
        g = self._scg; dKp = np.abs(np.asarray(self.dK, float)); n = len(dKp)
        php = g["sig"] * dKp / g["g"]
        Rc = S.rotm(g["dR"], php); tc = g["PV"][None] - np.einsum("nij,j->ni", Rc, g["PV"])
        self._sc = dict(n=n, X={9: (Rc, tc), 8: (Rc, tc)})

    def _rod_metal(self):
        D = self.D; P = D.p; u2, uK = D.u[1], D.uK; fK, f2 = self.fK, self.f[1]
        L1b = self.link_pts["L1b"][1]
        g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0); ax = unit(np.cross(u2, uK)); dR = unit(S.rotm(ax, g0)[0] @ u2)
        near = L1b[np.argsort(np.linalg.norm(unit(L1b) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max())
        tK0 = unit(dR - (dR @ uK) * uK); bK0 = unit(np.cross(uK, tK0))
        beta = float(P["beta"]) * D2R; rc = float(P["r_c"]); gg = float(P["g"])
        sK = math.cos(beta) * tK0 + math.sin(beta) * bK0
        lvK = fK + float(P["hl"]); lift = min(max(float(P.get("lift", 0.0)), 0.0), 8.0)   # lug / roller layer lifted off hub K's member level
        h_tip = lvK + lift + S.T_LINK + RUNG                                # arm underside over the lug layer (+ running gap)
        zboss = lev + S.T_LINK + RUNG; PV = dR * zboss
        C0 = uK * (lvK + lift + 1.5) + rc * sK                            # roller centre at the lug's mid layer
        sp = float(np.sign(D.psiA)) or 1.0
        def vH(X): return -sp * np.cross(uK, X)                           # horn point velocity per unit |dK| (link 1b frame)
        sig = 1.0 if float(np.cross(dR, C0) @ vH(C0)) >= 0 else -1.0       # crank sense: v_C . v_H > 0 (else both pa > 45 impossible)
        # ---- bent arm planform: straight from the boss to the tangent point T on the circle r_c about uK, then the arc to C0
        Dp = float(np.linalg.norm(PV - (PV @ uK) * uK)); psT = math.acos(min(1.0, rc / max(Dp, rc + 1e-6)))
        sgn_b = 1.0 if beta >= 0 else -1.0; psT *= sgn_b
        L1d = unit(L1b); L1r = np.linalg.norm(L1b, axis=1); w_ok = S.W_LINK / 2 + 1.0; k_r = math.tan(S.RAMP * D2R)
        if abs(beta) > abs(psT) + 1e-6:
            T3 = uK * h_tip + rc * (math.cos(psT) * tK0 + math.sin(psT) * bK0)
            psi = np.arange(psT, beta, sgn_b * 2.0 / rc)
            psi = np.append(psi, beta)
        else:
            T3 = uK * h_tip + rc * sK; psi = np.array([beta])
        R0 = float(np.linalg.norm(C0)); T3 = unit(T3) * (R0 + 1.5 + RUNG)
        P0 = PV; ch = T3 - P0; Lch = float(np.linalg.norm(ch)); ns = max(3, int(Lch / 2.0) + 1); ss_ = np.linspace(0, 1, ns)
        ws_ = np.array([-3.0, -1.0, 1.0, 3.0])
        dirs = np.array([unit(P0 + s * ch) for s in ss_]); chd = unit(ch)
        rad0 = np.array([float(np.linalg.norm(P0 + s * ch)) for s in ss_])
        # phi range of the arm swing (for the stacking rule): the law's K range / g
        L_ = D.law(); dKmax = math.radians(float(L_.get("dK_max", 0.0)) + 2.0) if L_.get("ok") else 0.2
        phis = sig * np.linspace(0.0, dKmax / gg, 7)
        lvl = np.zeros(ns)
        for j, (d_, s_) in enumerate(zip(dirs, ss_)):
            over = False
            for ph in phis:
                Rp = S.rotm(dR, ph)[0]
                for w_ in ws_:
                    x = Rp @ unit(d_ + (w_ / max(rad0[j], 1.0)) * unit(np.cross(d_, chd)))
                    if np.arccos(np.clip(L1d @ x, -1, 1)).min() * rad0[j] < w_ok: over = True; break
                if over: break
            jn = int(np.argmin(np.linalg.norm(L1d - d_, axis=1))); ref = float(L1r[jn])
            lvl[j] = (ref + S.T_LINK + RUNG) if (over or s_ * Lch < 5.0) else (ref + float(P["zr"]))
        lvl[-1] = max(lvl[-1], R0 + 1.5 + RUNG)
        lvl = np.max(lvl[None, :] - k_r * np.abs(ss_[:, None] - ss_[None, :]) * Lch, axis=1)   # 60-deg ramps between levels
        arm_s = []
        for j, d_ in enumerate(dirs):
            bn = unit(np.cross(d_, chd))
            for w_ in ws_: arm_s.append(unit(d_ * lvl[j] + w_ * bn) * float(np.linalg.norm(d_ * lvl[j] + w_ * bn)))
        R0 = float(np.linalg.norm(C0)); rL = R0 - 1.5; rA = R0 + 1.5 + RUNG          # spherical cam: lug shell [rL, rL + 3], arm tip over it
        arc = np.array([unit(uK * h_tip + (rc + w_) * (math.cos(a) * tK0 + math.sin(a) * bK0)) * rA for a in psi[1:] for w_ in ws_]) if len(psi) > 1 else np.zeros((0, 3))
        arm = np.concatenate([np.array(arm_s), arc]) if len(arc) else np.array(arm_s)
        e, f = S.frame_of(dR); dd = S.disc(5.0, 2.0); boss = PV + dd[:, :1] * e + dd[:, 1:] * f
        cr = unit(C0); rol_dn = C0 - 1.25 * cr; eK, fK_ = S.frame_of(cr); dr3 = S.disc(ROLL_R, 1.5)
        roller = np.concatenate([rol_dn + dr3[:, :1] * eK + dr3[:, 1:] * fK_, _ring(C0, ROLL_R, cr)])
        rolR = np.concatenate([_ring(C0 + z * cr, ROLL_R, cr) for z in (-1.25, 0.0, 1.25)])
        # ---- spherical cam synthesis on the K grid
        kgrid = np.radians(np.arange(0.0, max(math.degrees(dKmax), 5.0) + 1e-6, 0.25)); nk = len(kgrid)
        Rk = S.rotm(uK, sp * kgrid)                                       # link 1b -> link 1a: X_1a = Rk X_1b
        Rcg = S.rotm(dR, sig * kgrid / gg)
        Cg = np.einsum("nij,j->ni", Rcg, C0 - PV) + PV
        pac = np.zeros(nk); pah = np.zeros(nk); Qg = np.zeros((nk, 3)); ng = np.zeros((nk, 3)); lift = np.zeros(nk, bool)
        nprev = None
        for j in range(nk):
            C = Cg[j]; vC = (sig / gg) * np.cross(dR, C); vh = vH(C); vr = vC - vh; rh = unit(C)
            n = np.cross(rh, vr); nn = float(np.linalg.norm(n))
            n = n / nn if nn > 1e-9 else (nprev if nprev is not None else unit(vh))
            if nprev is None: n = n if float(n @ vh) >= 0 else -n
            else: n = n if float(n @ nprev) >= 0 else -n
            nprev = n; Q = C + ROLL_R * n; Qg[j] = Q; ng[j] = n
            pac[j] = _ang(n, vC); pah[j] = _ang(n, vH(Q))
            lift[j] = (float(n @ vC) <= 0) or (float(n @ vH(Q)) <= 0)
        # flank curvature (roller-centre path in link 1a's frame, K-plane chart)
        P1 = np.einsum("nij,nj->ni", Rk, Cg); N1 = np.einsum("nij,nj->ni", Rk, ng); Q1 = np.einsum("nij,nj->ni", Rk, Qg)
        x, y = P1 @ tK0, P1 @ bK0; nx, ny = N1 @ tK0, N1 @ bK0
        dx, dy = np.gradient(x, kgrid), np.gradient(y, kgrid); ddx, ddy = np.gradient(dx, kgrid), np.gradient(dy, kgrid)
        sp3 = np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); kap = (dx * ddy - dy * ddx) / sp3
        tx, ty = dx / np.maximum(np.hypot(dx, dy), 1e-12), dy / np.maximum(np.hypot(dx, dy), 1e-12)
        cxs = np.sign(kap) * (-ty); cys = np.sign(kap) * tx                 # toward the centre of curvature
        rho = 1.0 / np.maximum(np.abs(kap), 1e-9); horn_side = (cxs * nx + cys * ny) > 0
        flank_rho = np.where(horn_side, rho - ROLL_R, rho + ROLL_R)
        flank_bad = horn_side & (rho < ROLL_R + RHO_MIN)
        rQ = np.linalg.norm(Q1 - (Q1 @ uK)[:, None] * uK, axis=1)
        # clearances per K step (link 1b frame): arm / roller vs hub K, arm vs hub 2
        mem2, cen2, ax2 = self.cyl["hub2"]; r2 = self.cyl_r["hub2"]; memK, cenK, axK = self.cyl["hubK"]; rK = self.cyl_r["hubK"]
        armM = arm + 1.5 * unit(arm); armC = np.concatenate([armM, np.concatenate([_ring(dR * z, 5.0, dR) for z in np.linspace(zboss, zboss + SC.BOSS_H, 4)])])
        def farX(X, pad): w = X - cen2; return X[np.linalg.norm(w - (w @ ax2)[:, None] * ax2, axis=1) > r2 + pad]
        cK = np.zeros(nk); c2 = np.zeros(nk); cR = np.zeros(nk)
        for j in range(nk):
            XA = (armC - PV) @ Rcg[j].T + PV; XR = (rolR - PV) @ Rcg[j].T + PV
            cK[j] = float(self.sd_cyl(armM @ Rcg[j].T - PV @ Rcg[j].T + PV, cenK, axK, r=rK).min()) - S.T_LINK / 2
            cR[j] = float(self.sd_cyl(XR, cenK, axK, r=rK).min())
            XF = farX(XA, 6.5); c2[j] = float(self.sd_cyl(XF, cen2, ax2, r=r2).min()) - S.T_LINK / 2 if len(XF) else 99.0
        bad = {"pressure_crank": pac > PA_MAX + 1e-9, "pressure_horn": pah > PA_MAX + 1e-9, "liftoff": lift, "flank_cusp": flank_bad,
               "contact_off_lug": rQ < R_CMIN, "CRK-hubK": cK < 1.0, "ROLL-hubK": cR < 1.0, "CRK-hub2": c2 < 1.0}
        badany = np.zeros(nk, bool)
        for v in bad.values(): badany |= v
        jlim = int(np.argmax(badany)) if badany.any() else nk
        why_lim = [k_ for k_, v in bad.items() if v[jlim]][0] if jlim < nk else "law"
        jl = max(jlim - 1, 0); lim = float(kgrid[jl])
        # ---- the horn lug (link 1a, member 1), built from the flank over the used stroke [0, lim]
        def plane(X): return X / np.linalg.norm(X, axis=1)[:, None] * rL      # lug underside on the sphere |X| = |C0| - 1.5
        sel = np.arange(0, jl + 1); dsum = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(Q1[sel], axis=0), axis=1))])
        pick = [sel[0]]
        for jj, dsv in zip(sel, dsum):
            if dsv - dsum[list(sel).index(pick[-1])] >= 1.5: pick.append(jj)
        if pick[-1] != sel[-1]: pick.append(sel[-1])
        band = np.concatenate([plane(Q1[pick] + s * N1[pick]) for s in (0.3, 2.0, 4.0, LUG_BACK)])
        base = plane(Q1[pick[:1]] + np.array([0.3, 2.0, 4.0, LUG_BACK])[:, None] * N1[pick[0]][None])
        root = []
        for b in base:
            rb = float(np.linalg.norm(b - (b @ uK) * uK)); db = unit(b - (b @ uK) * uK)
            for r_ in np.arange(S.HUB_R + 0.5, rb, 2.0):
                x_ = uK * lvK + r_ * db; t_ = (r_ - S.HUB_R) / max(rb - S.HUB_R, 1e-6)
                root.append(unit(x_) * ((1 - t_) * float(np.linalg.norm(x_)) + t_ * rL))    # rises from the member level to the shell
        lug = np.concatenate([band, np.array(root)]) if root else band
        Pp = P1[sel]; dmin = cKDTree(Pp).query(lug + 1.5 * unit(lug))[0]
        lug = lug[dmin >= ROLL_R + 0.3 - 1e-6]
        if not len(lug): lug = plane(Q1[:1] + LUG_BACK * N1[:1])
        lugM = lug + 1.5 * unit(lug)
        # the low part of the arm vs the swinging lug (link 1b frame), per K step over the used stroke
        low = armM[np.linalg.norm(arm, axis=1) < rL + S.T_LINK + RUNG - 1e-6]
        cL = np.full(nk, 99.0)
        if len(low):
            for j in range(0, jl + 1):
                XL = (low - PV) @ Rcg[j].T + PV; XG = lugM @ Rk[j]           # Rk^T applied to rows: X_1b = Rk^T X_1a
                cL[j] = float(cKDTree(XG).query(XL)[0].min())
            badL = cL[: jl + 1] < 1.0
            if badL.any():
                jl2 = max(int(np.argmax(badL)) - 1, 0)
                if jl2 < jl: jl, lim, why_lim = jl2, float(kgrid[jl2]), "CRK-HORN"
        self._scg = dict(PV=PV, dR=dR, uK=uK, sp=sp, sig=sig, g=gg, kgrid=kgrid, dK_lim=lim, why_lim=why_lim, lowarm=low, lugM=lugM)
        self._sc = None
        # metal: crank (boss underside disc + arm underside), roller underside, horn lug underside
        self.rigid["crank"] = (9, np.concatenate([boss, arm]))
        self.rigid["roller"] = (9, roller)
        self.rigid["horn"] = (1, lug)
        for k_ in ("rod", "rodends", "rocker"): self.rigid.pop(k_, None)
        self._contact_only(); self._solids()
        cyl = np.concatenate([_ring(dR * z, 5.0, dR) for z in np.linspace(zboss, zboss + SC.BOSS_H, 4)])
        self.contact.append((9, np.concatenate([rolR, cyl, arm + S.T_LINK * unit(arm)])))
        self.contact.append((1, lug + S.T_LINK * unit(lug)))
        self.strap["ROD"] = (9, rolR)
        self.strap["CRK"] = (9, np.concatenate([cyl, armM]))
        self.strap["HORN"] = (1, lugM)
        self._crown_ok = True
        armPts = [PV + 1.5 * dR] + [d_ * (lvl[j] + 1.5) for j, d_ in enumerate(dirs)][1:] + [unit(uK * h_tip + rc * (math.cos(a) * tK0 + math.sin(a) * bK0)) * (rA + 1.5) for a in psi[1:]]
        lugPts = [unit(uK * lvK + (S.HUB_R + 0.5) * unit(Q1[0] - (Q1[0] @ uK) * uK)) * (np.linalg.norm(uK * lvK + (S.HUB_R + 0.5) * unit(Q1[0] - (Q1[0] @ uK) * uK)) + 1.5)] + \
                 [unit(Q1[j] + 3.0 * N1[j]) * R0 for j in pick]
        self._viz_rod = dict(rocker=PV, rockerAx=dR, rodA=C0, rodB=C0, armA=PV, armB=T3, roller=C0, armPts=armPts, lugPts=lugPts, sig=sig, g=gg)
        dKp = np.abs(np.asarray(self.dK, float)); taken = (np.asarray(self.kin_ok, bool)) & (dKp > 1e-9)
        kmax_t = float(dKp[taken].max()) if taken.any() else 0.0; jt = min(int(np.searchsorted(kgrid, min(kmax_t, lim))) + 1, nk)
        self._sc_info = dict(boss_level=round(zboss, 1), lev_L1b=round(lev, 1), arm_tip_level=round(float(np.linalg.norm(T3)), 1), g=round(gg, 3), sig=sig,
                             r_c=round(rc, 2), beta=round(float(P["beta"]), 2), arm_len=round(Lch + rc * abs(beta - psT), 1), arc_deg=round(math.degrees(abs(beta - psT)), 1) if abs(beta) > abs(psT) else 0.0,
                             rssr_closed=True, pa_crank_rest=round(float(pac[0]), 1), pa_horn_rest=round(float(pah[0]), 1),
                             vel_angle_rest=round(_ang((sig / gg) * np.cross(dR, C0), vH(C0)), 1),
                             pa_crank_max_taken=round(float(pac[:jt].max()), 1), pa_horn_max_taken=round(float(pah[:jt].max()), 1),
                             flank_rho_min=round(float(np.abs(flank_rho[:jl + 1]).min()), 1), contact_r=[round(float(rQ[0]), 1), round(float(rQ[jl]), 1)],
                             clear_hubK_min=round(float(cK[:jl + 1].min()), 2), clear_roll_hubK_min=round(float(cR[:jl + 1].min()), 2),
                             clear_lowarm_lug_min=round(float(cL[:jl + 1].min()), 2) if len(low) else None, n_lowarm=int(len(low)),
                             phi_max_taken=round(math.degrees(min(kmax_t, lim) / gg), 1),
                             crest_exact=round(float(P["r_lobe"]) + float(P["s_arm"]) * min(kmax_t, lim) / gg, 2),
                             dK_lim=round(math.degrees(lim), 1), why_lim=why_lim, law_dK_max=round(float(L_.get("dK_max", 0.0)), 1),
                             lug_r_max=round(float(np.linalg.norm(lug - (lug @ uK)[:, None] * uK, axis=1).max()), 1))
        self._rod_info = self._sc_info

    def collide(self, i):
        out = super().collide(i)
        g = getattr(self, "_scg", None)
        if g is None or not len(g.get("lowarm", [])): return out
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        XL = tf(9, g["lowarm"]); XG = tf(1, g["lugM"])
        c = float(cKDTree(XG).query(XL)[0].min())
        self.last_clear["CRKlow-HORN"] = round(c, 1)
        return min(out, c)


SC.SCModel = RFModel; SC._clamp = _clamp; SC.PARAMS = PARAMS
FL.G.KR.KB.KModel = RFModel; FL.FLModel_SC = RFModel


def _report(B, params):
    r, M = SC._report(B, params)
    d = r.get("drive") or {}
    info = getattr(M, "_sc_info", None) or {}
    if d and d.get("dK_taken_max", 99.0) < DK_IDLE:
        r["drive_idle"] = True; r["honest"] = False                   # the drive carries < 30 deg of K: a spare passive joint
    if info and info.get("dK_lim", 0.0) < DK_IDLE:
        r["cam_short"] = True                                          # kill gate: the flank works over < 30 deg of K
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360): return SC.frozen(P, nc, nw)
def frozen_held(P): return SC.frozen(P, -1, -1)
def frozen_flood(P, nc=110, nw=360): return SC.frozen_flood(P, nc, nw)


def viz_export(par):
    """the lead's exporter on this model + the drive geometry the preview draws: the bent arm polyline and the roller
    (link 1b frame at K = 0; the preview turns them about dR by phi = sig |dK| / g), the lug polyline (link 1a frame)"""
    FL._report = lambda B, p: SC._report(B, p)
    out = FL.viz_export(_clamp(dict(PARAMS, **par)))
    B = CB.Bench(n_clip=60, n_ws=160); r, M = SC._report(B, par); vr = M._viz_rod
    R = lambda v, n=3: [round(float(x), n) for x in v]
    out["G"].update(armPts=[R(x) for x in vr["armPts"]], lugPts=[R(x) for x in vr["lugPts"]], roller=R(vr["roller"]), rollerAx=R(unit(vr["roller"]), 5),
                    sig=float(vr["sig"]), g=round(float(vr["g"]), 4), dKlim=round(float(M._sc_info["dK_lim"]), 2))
    out["report"]["near1"] = r.get("gap_near1"); out["sidecar"] = M._sc_info
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "flood":
        t = time.time(); out = frozen_flood(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)[:3000]); sys.exit()
    if mode in ("frozen", "held"):
        t = time.time(); out = frozen(par) if mode == "frozen" else frozen_held(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out["fit_fast"], frozen=out["frozen"], why=out["why"], near1=a.get("gap_near1"), minmetal=a.get("near_touch_min_mm"),
                              ovh=a.get("overhead140"), parts=out.get("parts_ib14"), sidecar=out.get("sidecar"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), min_metal=r.get("min_metal_mm"), reach=r["reach"],
                          inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"), idle=r.get("drive_idle"), cam_short=r.get("cam_short"),
                          why=r.get("why"), ovh=r.get("overhead140"), drive=r.get("drive"), parts=r.get("parts_ib14"), clear=getattr(M, "last_clear", None),
                          secs=round(time.time() - t)), default=float))
