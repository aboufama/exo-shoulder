"""groove-desmo-knuckle-3r (round 10, lens 3): the lead's roller-flank knuckle drive made POSITIVE BOTH WAYS, so K needs no
clock spring and no stop A:
  * at hub 2 the rim lobe becomes a closed TRACK GROOVE (1.52 +0.01/0 wide, 1.5 deep) in the underside of hub 2's cap ring
    (link 2's body), over a link-2 boss reduced to O12 on the crank side; an ISO 8734 1.5 m6 hardened dowel pressed into
    the crank's short arm rides in it at link 2's level (SLIDING pair);
  * at hub K the conjugate flank becomes a closed two-walled SLOT in link 1a's boss (outer wall 1.5 mm beyond the roller
    path), with an MR52ZZ roller (2 x 5 x 2.5) on an integral O2 stub of the crank arm captured in it;
  * K's clock-spring cap (capK 6) and stop A are deleted: the groove's base-circle dwell holds K both ways, its ends are
    stops A and B.
Two cells, chosen by GD_CELL at import (one per process: the parents patch their shared core modules):
  * GD_CELL=lead (default): roller-longdyad-knuckle-3r (pin knee, b3 tilt) loaded unchanged;
  * GD_CELL=kneeless: the control kneeless-roller-knuckle-3r (J3 on a GH ray, one rigid bracket) loaded unchanged.
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, no gears / pulleys / cables / rods.

WHAT THIS FILE CHANGES on the parent (everything else - the spherical cam synthesis per 0.25 deg of K, both pressure
angles, cusp, contact on the lug, arm / roller / lug clearances, drive-range truncation on every bench, per-pose metal,
O20 stacks, part pairs, kit fold rule, 2 mm near-touch objective - is the parent's code, loaded unchanged):
  * capK = 0 (plain O20 cap on K); RF.ROLL_R = 2.5 (MR52ZZ); the stub's retaining head O3.5 x 0.8 (O2 stub);
  * GATE 0 / GROOVE FIT (closed form, judge re-size): pitch radius window [R_LO, R_HI] = [6 + 0.3 + 0.76, 10 - 0.8 - 0.76]
    = [7.06, 8.44]; r_lobe is clamped into it and the drive's own range dK_lim is cut where the crest r_lobe + s_arm phi
    reaches R_HI (the groove end IS stop B: 'groove-fit' becomes a drive limiter like the parent's PA / clearance ones);
  * the slot's OUTER WALL as horn metal (link 1a, member 1): the roller-centre path offset by -(ROLL_R + s) n,
    s in 0.3 / 1.0 / 1.8, plus the two end caps, kept >= HUB_R + 0.5 off hub K's axis, on the lug's underside sphere; in
    rigid['horn'], the contact list (its top), strap HORN and the low-arm-vs-lug check (re-run per K step: 'CRK-WALL');
    both walls' convex radii >= RHO_MIN (the parent checks the inner wall; the outer wall is checked here: 'wall2_cusp');
    lift-off is not a failure mode of a slot, but with both pressure angles <= 43 it never occurs (n.v_C = n.v_H > 0);
  * the REAL groove pressure angle (not in the parent family's formula, which assumes a radially moving follower): the
    crank pivot sits d ~ 16-18 mm off hub 2's axis, so a dowel at pitch radius r with radial lever s_arm sits at
    theta_F = asin(s_arm / d) from the pivot side and moves mostly TANGENTIALLY (r - d cos theta_F per unit crank angle).
    Per K step: the dowel velocity v_F, the cam-frame relative velocity v_rel = v_F - omega_2 x F, the groove normal
    n _|_ v_rel, pa_groove = angle(n, v_F) <= PA_GROOVE (43 - atan(mu), mu 0.1 for a greased hardened dowel sliding in a
    hardened groove ring: 37.3); the arrangement sign sig * s_q decides it (dowel moving WITH the cap surface: ~30 deg;
    against it: ~78 deg, a jam); fails -> drive limiter 'groove-pa';
  * link 2's exit at hub 2 vs the crank's short arm and dowel at link 2's level (planform, hub 2's plane): over every
    TAKEN pose, the 10-wide link-2 strap (from r 6 out) vs the O1.5 dowel at (r_pitch, theta_F) and the 3-wide short arm
    from the dowel to the boss: clearance >= 1.0 mm, else the pose is lost ('parts');
  * the dowel (O1.5 x 2) and the short arm (3 x 3) sampled as crank metal (contact list: they sit inside hub 2's O20
    envelope / over link 1b's strap, never the lowest metal).
Mechanism record (tools/simplicity.py v2): lead cell 22.0, kneeless 21.5.

    GD_CELL=lead OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/groove-desmo-knuckle-3r.py [check] ['<json>']
    GD_CELL=... CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]
    ... claims '[{"tag","cell","mode","params"}]' outdir      (one farm job, claim columns in parallel)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "groove-desmo-knuckle-3r"
CELL = os.environ.get("GD_CELL", "lead")
# the parents' verified best_params (rows/roller-longdyad-knuckle-3r.json, rows/kneeless-roller-knuckle-3r.json, 2026-10-17)
LEAD_BEST = {"bk1": 26.0, "bk2": 38.0336, "a1max": 58.7678, "kK": 2.1534, "smhi": 16.8433, "smlo": 5.0, "g": 2.4696, "beta": -173.4638, "r_c": 15.2211, "lift": 1.027, "hl": 2.1535, "zr": 4.0242, "s_arm": 4.0484, "r_lobe": 8.2409, "az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lc": 21.1499, "phib": -58.8084, "ang_min": 25.2189, "cprog": 0.0, "chain": "free", "near2": 1, "law_mode": "lin"}
KNEELESS_BEST = {"az1": 94.353, "el1": 65.9804, "az2": 41.8875, "el2": 41.0083, "wd": 73.9288, "wa": -11.3645, "lE": 82.2602, "phiE": -2.4165, "lc": 29.9075, "phib": -89.2952, "a1max": 56.0143, "kK": 2.568, "smhi": 16.9881, "bk1": 27.4142, "bk2": 35.6795, "g": 2.2297, "beta": -171.0352, "r_c": 16.2968, "lift": 1.7772, "hl": 0.7328, "zr": 2.9178, "s_arm": 4.7677, "r_lobe": 8.4303, "stk": 4.8534, "b3": 0.0, "ang_min": 0.0, "chain": "free", "law_mode": "lin", "near2": 1, "cprog": 0.0}
if CELL == "kneeless":
    _sp = importlib.util.spec_from_file_location("kneeless_for_groove", os.path.join(HERE, "kneeless-roller-knuckle-3r.py"))
    BM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(BM); BaseModel = BM.KLModel; RL = BM.RL
    BEST = KNEELESS_BEST
else:
    _sp = importlib.util.spec_from_file_location("longdyad_for_groove", os.path.join(HERE, "roller-longdyad-knuckle-3r.py"))
    BM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(BM); BaseModel = BM.RLModel; RL = BM
    BEST = LEAD_BEST
RF, SC, FL, PK, S = BM.RF, BM.SC, BM.FL, BM.PK, BM.S
unit = S.unit; D2R = math.pi / 180

# ---- hardware (tools/hardware_catalogue.json class parts; docs/HARDWARE.md O20)
ROLL_R, HEAD_R, HEAD_T = 2.5, 1.75, 0.8                       # MR52ZZ 2x5x2.5 on an integral O2 stub, O3.5 x 0.8 head
DOWEL_D, GROOVE_W, CAP_R, WALL_OUT, BOSS2_R, BOSS_GAP = 1.5, 1.52, S.HUB_R, 0.8, 6.0, 0.3
R_LO = BOSS2_R + BOSS_GAP + GROOVE_W / 2                       # 7.06
R_HI = CAP_R - WALL_OUT - GROOVE_W / 2                         # 8.44
SLOT_WALL = 1.5
ARM_W = 3.0                                                     # the crank's short arm (3 x 3 Ti) at link 2's level
L2_HALF = S.W_LINK / 2                                          # link 2's strap half-width
CLEAR_L2 = 1.0
MU_GROOVE = 0.10
PA_GATE = 43.0
PA_GROOVE = PA_GATE - math.degrees(math.atan(MU_GROOVE))       # 37.29
CONTROL = os.environ.get("GD_CONTROL") == "1"                 # the parent itself through this file's protocol (MR63, capK 6, no slot)
if CONTROL: ROLL_R, HEAD_R = 3.0, 2.25
RF.ROLL_R = ROLL_R; RL.HEAD_R = HEAD_R; RL.HEAD_T = HEAD_T; RF.PA_MAX = PA_GATE

GROOVE = dict(capK=0.0, groove_gate=1)
PARAMS = dict(BM.PARAMS, **BEST, **({} if CONTROL else GROOVE))
if not CONTROL: PARAMS["r_lobe"] = R_LO


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def _clamp(p):
    if CONTROL: return BM._clamp(p)
    s_raw = float(p.get("s_arm", 4.0)); b_raw = float(p.get("beta", -170.0)); rc_raw = float(p.get("r_c", 16.0)); g_raw = float(p.get("g", 2.4))
    p = BM._clamp(p)
    # the slot's outer wall moves the roller off the relative-rotation pole: the drive search box is widened (RF's own limits)
    b_raw = b_raw - 360.0 if b_raw > 0 else b_raw
    p["beta"] = _c(b_raw, -215.0, -120.0); p["r_c"] = _c(rc_raw, 13.0, 22.0); p["g"] = _c(g_raw, 1.6, 3.2)
    p["i_rock"] = p["g"]; p["r_h"] = p["r_c"]
    p["capK"] = 0.0
    p["s_arm"] = _c(s_raw, 3.0, 4.6); p["r_horn"] = p["s_arm"]           # a dowel lever: any radial lever fits; window set by the groove
    p["r_lobe"] = _c(p.get("r_lobe", R_LO), R_LO, R_HI)
    return p


def _ang(a, b):
    c = float(a @ b) / max(float(np.linalg.norm(a) * np.linalg.norm(b)), 1e-12); return math.degrees(math.acos(max(-1.0, min(1.0, c))))


class GDModel(BaseModel):
    def _rod_metal(self):
        RF.ROLL_R = ROLL_R; RL.HEAD_R = HEAD_R; RL.HEAD_T = HEAD_T; RF.PA_MAX = PA_GATE
        super()._rod_metal()
        if CONTROL:
            self._groove = None; return
        D = self.D; P = D.p; g = self._scg; info = self._sc_info
        PV, dR, uK, sp, sig, gg, cc = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0)
        kgrid = g["kgrid"]; lim0 = float(g["dK_lim"]); why0 = g["why_lim"]
        s_arm = float(P["s_arm"]); rl0 = float(P["r_lobe"])
        lim, why = lim0, why0

        def cut(k_new, tag):
            nonlocal lim, why
            if k_new < lim - 1e-12:
                j = max(int(np.searchsorted(kgrid, k_new + 1e-12)) - 1, 0); lim, why = float(kgrid[j]), tag
        # (1) groove fit: crest r_lobe + s_arm phi(K) <= R_HI  (lin law: phi = K / g)
        kG = gg * (R_HI - rl0) / max(s_arm, 1e-9)
        cut(kG, "groove-fit")
        # (2) real groove pressure angle with the pivot geometry (hub 2's plane at the boss level)
        u2 = D.u[1]; zc = float(PV @ u2); dvec = PV - zc * u2; d = float(np.linalg.norm(dvec)); ex = dvec / d; ey = np.cross(u2, ex)
        L_ = D.law(); s_q = float(L_.get("s_q", 1.0)); kK = float(P.get("kK", P.get("kA", 2.0)))
        lam = kK / gg                                                       # crank radians per radian of q2 past the onset
        thF = -sig * math.asin(min(s_arm / d, 0.999))                       # the side on which the dowel lifts outward
        pag = np.zeros(len(kgrid)); rr = rl0 + s_arm * kgrid / gg
        omega_dir = 1.0                                                      # q2 measured about +u2, phi about dR ~ +u2
        for j, k in enumerate(kgrid):
            r = rr[j]; th = thF                                              # dowel azimuth drift ignored for the angle (small)
            vr = -d * math.sin(th); vt = r - d * math.cos(th)                # per unit crank angle (about +z)
            vF = sig * lam * np.array([vr, vt])                              # per unit t (q2 travel past the onset, sign s_q)
            vcam = np.array([0.0, s_q * omega_dir * r])
            vrel = vF - vcam; n = np.array([-vrel[1], vrel[0]])
            a = _ang(n, vF); pag[j] = min(a, 180.0 - a)
        bad = np.nonzero(pag > PA_GROOVE + 1e-9)[0]
        if len(bad): cut(float(kgrid[bad[0]]) - 1e-9 if bad[0] > 0 else 0.0, "groove-pa")
        # (3) the slot's outer wall (link 1a frame), over the used stroke [0, lim]
        C0 = np.asarray(self._viz_rod["roller"], float); R0 = float(np.linalg.norm(C0)); rL = R0 - 1.5
        jl = int(np.searchsorted(kgrid, lim + 1e-12)) - 1; jl = max(jl, 0)
        kk = kgrid[: jl + 1]
        Rk = S.rotm(uK, sp * kk); Rcg = S.rotm(dR, sig * RF.phi_of(kk, gg, cc))
        Cg = np.einsum("nij,j->ni", Rcg, C0 - PV) + PV
        ng = np.zeros_like(Cg); nprev = None
        for j in range(len(kk)):
            C = Cg[j]; vC = sig * float(RF.dphi_of(kk[j], gg, cc)) * np.cross(dR, C); vh = -sp * np.cross(uK, C); vr_ = vC - vh
            n = np.cross(unit(C), vr_); nn = float(np.linalg.norm(n)); n = n / nn if nn > 1e-9 else (nprev if nprev is not None else unit(vh))
            if nprev is None: n = n if float(n @ vh) >= 0 else -n
            else: n = n if float(n @ nprev) >= 0 else -n
            ng[j] = n; nprev = n
        P1 = np.einsum("nij,nj->ni", Rk, Cg); N1 = np.einsum("nij,nj->ni", Rk, ng)

        def plane(X): return X / np.linalg.norm(X, axis=1)[:, None] * rL
        pick = [0]; acc = 0.0
        for j in range(1, len(kk)):
            acc += float(np.linalg.norm(P1[j] - P1[j - 1]))
            if acc >= 1.5: pick.append(j); acc = 0.0
        if pick[-1] != len(kk) - 1: pick.append(len(kk) - 1)
        wall = [plane(P1[pick] - (ROLL_R + s) * N1[pick]) for s in (0.3, 1.0, 1.8)]
        caps = []
        for jj, sg_ in ((0, -1.0), (len(kk) - 1, 1.0)):                      # end caps around both stroke ends
            c = P1[jj]; cn = unit(c); e1 = N1[jj] - (N1[jj] @ cn) * cn; e1 = unit(e1); e2 = np.cross(cn, e1)
            for rad in (ROLL_R + 0.3, ROLL_R + 1.0, ROLL_R + 1.8):
                for a in np.linspace(0, 2 * math.pi, 24, endpoint=False):
                    caps.append(c + rad * (math.cos(a) * e1 + math.sin(a) * e2))
        W = np.concatenate(wall + ([plane(np.array(caps))] if caps else []))
        dpath = cKDTree(P1).query(W + 1.5 * unit(W))[0]
        W = W[dpath >= ROLL_R + 0.3 - 1e-6]
        rax = np.linalg.norm(W - (W @ uK)[:, None] * uK, axis=1); W = W[rax >= S.HUB_R + 0.5]
        # outer wall convexity (the parent checks the inner flank): centre of curvature on the outer wall's metal side
        x, y = P1 @ unit(np.cross(uK, ng[0])), P1 @ unit(np.cross(uK, np.cross(uK, ng[0])))
        w2_rho_min = None; w2_cusp_k = w2_bad_k = None
        if len(kk) > 4:
            dx, dy = np.gradient(x, kk), np.gradient(y, kk); ddx, ddy = np.gradient(dx, kk), np.gradient(dy, kk)
            kap = (dx * ddy - dy * ddx) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); rho = 1.0 / np.maximum(np.abs(kap), 1e-9)
            tx, ty = dx / np.maximum(np.hypot(dx, dy), 1e-12), dy / np.maximum(np.hypot(dx, dy), 1e-12)
            cxs, cys = np.sign(kap) * (-ty), np.sign(kap) * tx
            nx, ny = N1 @ unit(np.cross(uK, ng[0])), N1 @ unit(np.cross(uK, np.cross(uK, ng[0])))
            outer_side = (cxs * nx + cys * ny) < 0                            # centre of curvature on the -n (outer wall) side
            badw = outer_side & (rho < ROLL_R + RF.RHO_MIN)
            jcs = np.nonzero(outer_side & (rho < ROLL_R))[0]
            w2_cusp_k = [round(float(np.degrees(kk[jcs[0]])), 2), round(float(np.degrees(kk[jcs[-1]])), 2)] if len(jcs) else None
            jcv = np.nonzero(badw)[0]
            w2_bad_k = [round(float(np.degrees(kk[jcv[0]])), 2), round(float(np.degrees(kk[jcv[-1]])), 2)] if len(jcv) else None
            if badw[1:-1].any():
                jb = int(np.nonzero(badw[1:-1])[0][0]) + 1; cut(float(kk[jb - 1]), "wall2_cusp")
            w2 = np.where(outer_side, rho - ROLL_R, rho + ROLL_R); w2_rho_min = round(float(np.abs(w2[1:-1]).min()), 1) if len(w2) > 2 else None
        WM = W + 1.5 * unit(W)
        # low arm vs the outer wall over the stroke
        low = g.get("lowarm", np.zeros((0, 3))); cW = 99.0
        if len(low) and len(WM):
            tW = cKDTree(WM)
            for j in range(len(kk)):
                if kk[j] > lim + 1e-12: break
                XL = (low - PV) @ Rcg[j].T + PV; XG = WM @ Rk[j]
                c_ = float(cKDTree(XG).query(XL)[0].min()); cW = min(cW, c_)
                if c_ < 1.0: cut(float(kk[max(j - 1, 0)]), "CRK-WALL"); break
        if len(W):
            m1, lug = self.rigid["horn"]; self.rigid["horn"] = (m1, np.concatenate([lug, W]))
            self.contact.append((1, W + S.T_LINK * unit(W)))
            mH, XH = self.strap["HORN"]; self.strap["HORN"] = (mH, np.concatenate([XH, WM]))
            g["lugM"] = np.concatenate([g["lugM"], WM])
        # (4) the dowel and the short arm at link 2's level (crank, member 9; contact list)
        lvl2 = zc + S.HUB_UP if hasattr(S, "HUB_UP") else zc + 3.15
        F0 = u2 * lvl2 + rl0 * (math.cos(thF) * ex + math.sin(thF) * ey)
        e_, f_ = S.frame_of(u2); dd = S.disc(DOWEL_D / 2, 0.5)
        dowel = np.concatenate([F0 + z * u2 + dd[:, :1] * e_ + dd[:, 1:] * f_ for z in (0.0, 2.0)])
        Pb = u2 * lvl2 + (d - 5.0) * ex; seg = np.linspace(0, 1, 8)
        arm = np.array([F0 + t * (Pb - F0) + w * unit(np.cross(u2, Pb - F0)) for t in seg for w in (-ARM_W / 2, ARM_W / 2)])
        self.contact.append((9, np.concatenate([dowel, arm])))
        self._groove = dict(d=d, ex=ex, ey=ey, u2=u2, thF=thF, F0=F0, rl0=rl0, s_arm=s_arm, lvl2=lvl2)
        g.update(dK_lim=lim, why_lim=why)
        crest = rl0 + s_arm * float(RF.phi_of(lim, gg, cc))
        jt = int(np.searchsorted(kgrid, lim + 1e-12))
        info.update(dK_lim=round(math.degrees(lim), 1), why_lim=why, dK_lim_parent=round(math.degrees(lim0), 1), why_lim_parent=why0,
                    groove=dict(r_pitch=[round(rl0, 3), round(crest, 3)], window=[round(R_LO, 2), round(R_HI, 2)], s_arm=round(s_arm, 3),
                                pivot_d=round(d, 2), theta_F=round(math.degrees(thF), 1), sig=float(sig), s_q=s_q, lam=round(lam, 3),
                                arrangement="with" if sig * s_q < 0 else "against",
                                pa_groove_max=round(float(pag[:max(jt, 1)].max()), 1), pa_groove_gate=round(PA_GROOVE, 2),
                                pa_radial_formula=round(math.degrees(math.atan(s_arm * lam / rl0)), 1),
                                slop_K_deg=round(math.degrees(gg * (0.014 / s_arm) + 0.014 / max(float(P["r_c"]), 1.0)), 2)),
                    wall2=dict(n=int(len(W)), rho_min=w2_rho_min, cusp_K=w2_cusp_k, convex_lt_rhomin_K=w2_bad_k, clear_lowarm=round(cW, 2)), roll_r=ROLL_R)
        self._rod_info = info

    def l2_check(self, idx):
        """link 2's strap (10 wide, from r 6 out) vs the dowel (O1.5 at r_pitch(K), theta_F) and the 3-wide short arm, in hub
        2's plane at link 2's level, per pose: planform clearance (mm), the exit azimuth from the pivot side (deg)"""
        gd = self._groove; g = self._scg; out_c, out_a = [], []
        mh, cen2, ax2 = self.cyl["hub2"]; m3, cen3, _ = self.cyl["hub3"]
        for i in idx:
            R1, t1 = self.T(mh, i)
            c2 = R1 @ cen2 + t1; a2 = R1 @ ax2; a2 = a2 / np.linalg.norm(a2)
            R3, t3 = self.T(m3, i); c3 = R3 @ cen3 + t3
            Rb, tb = self.T(self.link_pts["L1b"][0], i)
            ex = Rb @ gd["ex"]; ex = ex - (ex @ a2) * a2; ex /= np.linalg.norm(ex); ey = np.cross(a2, ex)
            v = c3 - c2; v = v - (v @ a2) * a2; az = math.atan2(float(v @ ey), float(v @ ex))
            k = abs(float(self.dK[i])); r = gd["rl0"] + gd["s_arm"] * float(RF.phi_of(k, g["g"], g.get("c", 0.0)))
            phi = g["sig"] * float(RF.phi_of(k, g["g"], g.get("c", 0.0)))
            # the dowel turns about the pivot (d, 0) by phi
            F = np.array([r * math.cos(gd["thF"]), r * math.sin(gd["thF"])])
            Pp = np.array([gd["d"], 0.0]); Fr = Pp + np.array([[math.cos(phi), -math.sin(phi)], [math.sin(phi), math.cos(phi)]]) @ (F - Pp)
            Pb = np.array([gd["d"] - 5.0, 0.0])
            e = np.array([math.cos(az), math.sin(az)]); nrm = np.array([-e[1], e[0]])
            def strap_d(X):                                              # distance of a point to the strap (r >= 6 along e, |lat| <= 5)
                a_ = float(X @ e); l_ = abs(float(X @ nrm))
                if a_ < BOSS2_R: return math.hypot(BOSS2_R - a_, max(0.0, l_ - L2_HALF)) if l_ > L2_HALF else BOSS2_R - a_ + 0.0
                return l_ - L2_HALF
            cl = strap_d(Fr) - DOWEL_D / 2
            for t in np.linspace(0, 1, 9):
                X = Fr + t * (Pb - Fr); cl = min(cl, strap_d(X) - ARM_W / 2)
            out_c.append(cl); out_a.append(math.degrees(az))
        return np.array(out_c), np.array(out_a)

    def run(self, B=None):
        r = super().run() if B is None else super().run(B)
        try:
            Bn = self.B; why = [str(w) for w in self.why]
            taken = [i for i in range(len(Bn.idx)) if why[i] == "" and Bn.res[i] is not None]
            if taken and P_L2GATE and getattr(self, "_groove", None):
                cl, az = self.l2_check(taken); badi = [taken[j] for j in np.nonzero(cl < CLEAR_L2)[0]]
                for i in badi: Bn.res[i] = None; self.why[i] = "parts"
                self._l2 = dict(n=len(taken), clear_min=round(float(cl.min()), 2), az_abs_min=round(float(np.abs(az).min()), 1),
                                n_lt60=int((np.abs(az) < 60).sum()), lost=len(badi))
                if badi:
                    rep = Bn.report()
                    for k in ("gap", "reach", "follow", "inband14", "inband10", "contact"): r[k] = rep[k]
                    w = r.get("why") or {}; w["parts"] = w.get("parts", 0) + len(badi); r["why"] = w
        except Exception as ex_:                                          # never hide a failure: report it
            self._l2 = dict(error=repr(ex_))
        return r


P_L2GATE = True
SC.SCModel = GDModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
FL.G.KR.KB.KModel = GDModel; FL.FLModel_SC = GDModel
if CELL == "kneeless": BM.PARAMS = PARAMS; BM.RL.PARAMS = PARAMS; BM.SC.SCModel = GDModel
else: BM.PARAMS = PARAMS


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = BM._report(B, p)
    info = getattr(M, "_sc_info", None) or {}
    r.setdefault("cam", {})
    for k in ("groove", "wall2", "dK_lim_parent", "why_lim_parent", "roll_r", "dK_lim", "why_lim"):
        if k in info: r["cam"][k] = info[k]
    r["l2"] = getattr(M, "_l2", None)
    gq = info.get("groove") or {}
    if gq and gq.get("pa_groove_max", 0) > PA_GROOVE + 1e-6: r["honest"] = False; r["groove_pa_fail"] = True
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved") or r.get("groove_pa_fail"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); r["cell"] = CELL
    if not r.get("honest", True): r["gap_honest"] = r["gap"]; r["gap"] = max(float(r["gap"]), 275.0)
    return r


def _frozen_model(P, nc, nw):
    """the claim protocol (= SC.frozen): fit on Bench(60,160) fast, the shape frozen (drive, metal, groove copied), worn on
    Bench(nc, nw) (exact when CB_EXACT=1; nc == -1: the held-out bench); the l2 planform check runs on the worn bench too"""
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = GDModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    fit["l2"] = getattr(M1, "_l2", None)
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(GDModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_groove"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if nc == -1:
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_groove", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
        PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); B = PVm.held_bench()
    else:
        B = CB.Bench(n_clip=nc, n_ws=nw)
    M = Frozen(B, P2); r = M.run()
    return fit, M1, M, B, r


def frozen(P, nc=110, nw=360):
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    ov = ws & (elev >= 140); info = getattr(M1, "_sc_info", None) or {}
    out = dict(cell=CELL, fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
               parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), ws_inband=RL.ws_inband(B), split=RL.contact_split(M, B),
               overhead=dict(ws=int(ov.sum()), taken=int((ov & (mins >= 0)).sum())), l2=getattr(M, "_l2", None),
               cam={k: info.get(k) for k in ("dK_lim", "why_lim", "dK_lim_parent", "why_lim_parent", "pa_crank_max_taken", "pa_horn_max_taken",
                                             "flank_rho_min", "clear_hubK_min", "clear_roll_hubK_min", "clear_lowarm_lug_min", "groove", "wall2")})
    dK = np.degrees(np.abs(np.asarray(M.dK, float))); tk = [j for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) >= 0]
    out["dK_taken_max"] = round(float(dK[tk].max()), 2) if tk else None
    if CELL == "kneeless": out["knee_rigid"] = BM.knee_check(M)
    return out


def frozen_held(P): return frozen(P, -1, -1)


def frozen_flood(P, nc=110, nw=360):
    os.environ["CB_EXACT"] = "1"
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    out = dict(cell=CELL, frozen={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")})
    sp_ = importlib.util.spec_from_file_location("minarc_mech_for_groove", os.path.join(REPO, "docs", "concepts", "verify", "minarc-stop-knuckle-4r-mechanism.py"))
    MECH = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(MECH)
    t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


def redteam(P, nc=110, nw=360):
    """red team on the frozen exact wear: the 10 lowest-metal taken poses with their lowest parts, the parts behind every
    contact / skin / parts pose, the named poses (rest, overhead, across the body, behind the back, extreme rotations),
    the drive's per-pose groove / slot state (crank angle, pitch radius, link-2 planform clearance) at each named pose"""
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    res = {"frozen": {k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")}, "why": r.get("why")}
    mem_name = {}
    for nm, (m, X) in M.rigid.items(): mem_name.setdefault(m, []).append(nm)
    def parts_at(i):
        d = {}
        for nm, (m, X) in M.rigid.items():
            if len(X): d[nm] = round(float(B.dist(i, M.world(m, i, X)).min()), 2)
        for m, X in M.contact:
            if len(X):
                k = "edge/top m%d (%s)" % (m, "/".join(mem_name.get(m, ["?"]))); d[k] = min(d.get(k, 99.0), round(float(B.dist(i, M.world(m, i, X)).min()), 2))
        return dict(sorted(d.items(), key=lambda kv: kv[1])[:4])
    pose = lambda i: {k: B.poses[i].get(k) for k in ("plane", "elev", "axial")}
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    res["lowest"] = [dict(i=i, pose=pose(i), kind=B.kind[i], mm=round(float(np.min(B.res[i])), 2), parts=parts_at(i))
                     for i in sorted(taken, key=lambda i: float(np.min(B.res[i])))[:10]]
    res["lost_to_metal"] = [dict(i=i, pose=pose(i), why=str(M.why[i]), parts=parts_at(i)) for i in range(len(B.idx)) if str(M.why[i]) in ("contact", "skin", "parts")]
    ws = [i for i in range(len(B.idx)) if B.kind[i] == "ws"]
    def near(pl, el, ax):
        return min(ws, key=lambda i: abs(B.poses[i]["plane"] - pl) + abs(B.poses[i]["elev"] - el) + abs(((B.poses[i]["axial"] - ax + 180) % 360) - 180))
    named = {"rest (plane 0, elev 15)": (0, 15, 0), "overhead axial -135": (0, 150, -135), "overhead axial 0": (0, 150, 0),
             "overhead plane 90": (90, 150, -135), "across the body (plane 120, elev 90)": (120, 90, 0),
             "across the body, extreme internal rotation": (120, 60, -150), "behind the back (plane -60, elev 45, axial -120)": (-60, 45, -120),
             "abduction 90 over the deltoid crest": (0, 90, 0), "extreme external rotation (plane 30, elev 30, axial 150)": (30, 30, 150)}
    g = M._scg; gd = M._groove; res["named"] = {}
    for nm, (pl, el, ax) in named.items():
        i = near(pl, el, ax); w = str(M.why[i]) or "taken"; k = abs(float(M.dK[i]))
        cl, az = M.l2_check([i]) if gd else (np.array([np.nan]), np.array([np.nan]))
        res["named"][nm] = dict(i=i, pose=pose(i), status=w, dK=round(math.degrees(k), 1),
                                phi=round(math.degrees(float(RF.phi_of(k, g["g"], g.get("c", 0.0)))), 1),
                                r_pitch=round(gd["rl0"] + gd["s_arm"] * float(RF.phi_of(k, g["g"], g.get("c", 0.0))), 2) if gd else None,
                                l2_clear=round(float(cl[0]), 2), l2_az=round(float(az[0]), 1),
                                parts=parts_at(i) if w in ("taken", "contact", "skin", "parts") else None)
    return res


def viz_export(par): return RF.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "claims":
        import subprocess
        od = sys.argv[3] if len(sys.argv) > 3 else "gd_out"; os.makedirs(od, exist_ok=True); procs = []
        for c in par:
            env = dict(os.environ, GD_CELL=c.get("cell", "lead"), CB_EXACT="1", OMP_NUM_THREADS="1", CB_QUIET_EXACT="1")
            lg = open(os.path.join(od, c["tag"] + ".log"), "w")
            procs.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), c.get("mode", "frozen"), json.dumps(c.get("params", {})),
                                           os.path.join(od, c["tag"] + ".json")], env=env, stdout=lg, stderr=subprocess.STDOUT))
        for pr in procs: pr.wait()
        print("claims done", [pr.returncode for pr in procs]); sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "redteam":
        out = redteam(par)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(dict(frozen=out["frozen"], named={k: (v["status"], v["dK"], v["l2_clear"]) for k, v in out["named"].items()}), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(cell=CELL, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), cam=out.get("cam"),
                              l2=out.get("l2"), dK_taken_max=out.get("dK_taken_max"), connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(cell=CELL, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r.get("inband10"), contact=r["contact"], honest=r.get("honest"),
                          pa_fail=r.get("pa_fail"), groove_pa_fail=r.get("groove_pa_fail"), why=r.get("why"), ovh=r.get("overhead140"),
                          ws_inband=r.get("ws_inband"), cam=r.get("cam"), l2=r.get("l2"), parts=r.get("parts_ib14"),
                          knee=r.get("knee_rigid"), secs=round(time.time() - t)), default=float))
