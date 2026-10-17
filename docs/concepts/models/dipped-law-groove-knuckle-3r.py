"""dipped-law-groove-knuckle-3r (round 10, lens 3): the lead's slaved knuckle (roller-longdyad-knuckle-3r: J1 acromion
top, link 1a with the flank boss, K slaved by the hub-2 lobe -> bell crank -> roller -> flank drive and never read, link
1b, J2, link 2, J3, the two-pin knee and the cuff) with a DIPPED K law. In the mid-folded band (th_c +- w) the lobe lets
the clock spring close K BELOW the old stop A: the effective first link a1e shortens by up to dipD deg, and hub 2 rides
up toward hub 1, off the bunched deltoid. K reopens to the old rest before the folded wall and rises on the stretched
side exactly as before. Stop A moves to the dip floor, and the lobe holds K at its old rest angle through the dwell.
3 ACTIVE DOF (J1, J2, J3), 0 passive translations, no gears / pulleys / cables.

THE LAW (state A of the design's own ik: KB.KDesign.ik through the min-arc law; the design's closure branch, not an
elevation rule):
    a1e(th) = a1 - dipD * b(x),  x = (th - th_c) / w,  b = max(0, 1 - x^2)^2   (dip_shape 1, C1: zero slope at the edges)
                                                       b = max(0, 1 - x^2)     (dip_shape 0, the spec's parabola: kinks)
    psi_e = arccos((cos a1e - cos bk1 cos bk2) / (sin bk1 sin bk2)),  dK = sign(psiA) psi_e - psiA   (negative = closing)
  The spec's parabola has a slope discontinuity of 2 dipD / w deg/deg at both band edges. A cam cannot follow that
  without an acceleration spike at the follower, so the default is the C1 bump with the same peak.

WHAT IS CHECKED ON TOP OF THE LEAD'S MODEL (everything else is the lead's code, loaded unchanged):
  * the cam reads q2, not th. On a 0.25-deg th grid over the band, q2(th) on the design's q2 half-turn must stay strictly
    monotone with dq2/dth <= RATE_MAX (3.45), and the lobe's pressure angle atan(|dr/dq2| / r) must stay <= PA_MAX (43),
    where r = r_lobe + s_arm (k - k_floor) / g. The lobe pitch curve's tightest concave radius is reported (follower fit);
  * the fold margin: the kit dyad margin m3e(th, a1e, a2) >= 5 on every pose (the folded wall moves up by the dip). The
    forced sub-chain margin msub (J1-K-J3) is NOT required on dipped poses: it is the stretched law's rule for J2 parked on
    its stop with K the moving joint (state-A poses sit at msub ~0.2-0.6). In the dip, J2 moves and K follows q2; the
    determinacy check is the cam's own (th(q2) monotone, rate <= 3.45);
  * the drive is synthesised over the closing range too (_rf_rod_metal_dip, the roller-flank synthesis with the K grid
    extended to the dip floor - 1 deg): the flank, both pressure angles, lift-off, cusp, contact on the lug, arm / roller
    vs hub K, arm vs hub 2, the low arm vs the swinging lug. The horn lug is built over the whole used stroke
    [dK_neg, dK_lim]. Stop A sits at the last good negative step (dK_neg); dipped poses past it are lost (_truncate);
  * the crank's per-pose transform uses the SIGNED opening (it swings backward in the dip), so its metal, the roller and
    the lug are skin- and part-checked at the dipped K on every pose;
  * the lobe crest grows by s_arm |k_floor| / g (the old rest is lifted by the dip): it enters the law's skirt rule and
    the sidecar's crest_exact gate.

CELLS: 'lead' = the lead's verified params + kneewin's centred knee (lE 82, lc 27, phiE 3.8, phib -96.6, ang_min 20);
dipD 0 is the control (reproduces kneewin's 19.33 frozen, and the lead's 18.67 with the lead's own knee: cell 'leadknee').

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/dipped-law-groove-knuckle-3r.py [check|split|band] ['<json>']
    CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("roller_longdyad_for_dip", os.path.join(HERE, "roller-longdyad-knuckle-3r.py"))
RL = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(RL)
RF, SC, FL, PK, S = RL.RF, RL.SC, RL.FL, RL.PK, RL.S
G = FL.G; KR, KB, KIT = G.KR, G.KB, G.KIT
unit = S.unit; D2R = math.pi / 180
phi_of, dphi_of, _ring, _ang = RF.phi_of, RF.dphi_of, RF._ring, RF._ang
ROLL_R, RHO_MIN, R_CMIN, LUG_BACK, RUNG = RF.ROLL_R, RF.RHO_MIN, RF.R_CMIN, RF.LUG_BACK, RF.RUNG
RATE_MAX = G.RATE_MAX
ID = "dipped-law-groove-knuckle-3r"

LEAD_BEST = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "roller-longdyad-knuckle-3r.json")))["best_params"]
KNEEWIN = {"lE": 82.0, "lc": 27.0, "phiE": 3.8, "phib": -96.6, "ang_min": 20.0}
DIP0 = {"dipD": 0.0, "dip_thc": 53.0, "dip_w": 12.0, "dip_shape": 1}
PARAMS = dict(RL.PARAMS, **LEAD_BEST); PARAMS.update(KNEEWIN); PARAMS.update(DIP0)


def dip_bump(th, thc, w, shape=1):
    x = (np.asarray(th, float) - float(thc)) / max(float(w), 1e-6); b = np.clip(1.0 - x * x, 0.0, None)
    return b * b if int(shape) else b


def _clamp(p):
    p = RL._clamp(p)
    p["dipD"] = min(max(float(p.get("dipD", 0.0)), 0.0), 14.0); p["dip_thc"] = min(max(float(p.get("dip_thc", 53.0)), 35.0), 75.0)
    p["dip_w"] = min(max(float(p.get("dip_w", 12.0)), 4.0), 30.0); p["dip_shape"] = 1 if int(p.get("dip_shape", 1)) else 0
    return p


assert KB.KDesign is FL.FLDesign, "the lead's design class is expected at KB.KDesign"


class DipDesign(FL.FLDesign):
    def _D(self): return max(float(self.p.get("dipD", 0.0)), 0.0)

    def dip_of(self, th):
        P = self.p
        return self._D() * dip_bump(th, P.get("dip_thc", 53.0), P.get("dip_w", 12.0), P.get("dip_shape", 1)) if self._D() > 0 else np.zeros(np.shape(th))

    def kopen_of(self, a1e):
        """signed K opening (rad, + = the drive's opening sense, - = closing below the old stop A) for an effective a1e (deg)"""
        b1, b2 = float(self.p["bk1"]) * D2R, float(self.p["bk2"]) * D2R
        c = (np.cos(np.asarray(a1e, float) * D2R) - math.cos(b1) * math.cos(b2)) / (math.sin(b1) * math.sin(b2))
        return np.arccos(np.clip(c, -1, 1)) - abs(self.psiA)

    def dip_floor(self): return float(self.kopen_of(self.a1 - self._D())) if self._D() > 0 else 0.0

    def dip_kneg(self): return self.dip_floor() - math.radians(1.0) if self._D() > 0 else 0.0

    def law(self):
        if getattr(self, "_law", None) is not None: return self._law
        P = self.p
        if self._D() <= 0: return super().law()
        lift = float(P["s_arm"]) * abs(self.dip_floor()) / float(P["g"])       # mm: the old rest lifted off the dip floor
        r0 = float(P["r_lobe"]); P["r_lobe"] = r0 + lift
        try: L = super().law()
        finally: P["r_lobe"] = r0
        L["dip_lift_mm"] = lift
        return L

    def dip_table(self):
        """the dip as a cam on q2 (needs q2sgn): th grid 0.25 deg over the band, q2 on the design's half-turn, rate, lobe
        pressure angle and the pitch curve's tightest concave radius"""
        if getattr(self, "_dipT", None) is not None: return self._dipT
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; sp = float(np.sign(self.psiA)) or 1.0
        if self._D() <= 0 or self.q2sgn is None:
            self._dipT = dict(ok=True, n=0); return self._dipT
        thc, w = float(P["dip_thc"]), float(P["dip_w"])
        th = np.arange(max(thc - w, getattr(self, "th_lo", 0.0)), min(thc + w, getattr(self, "th_hi", 180.0)) + 1e-9, 0.25)
        a1e = self.a1 - self.dip_of(th); k = self.kopen_of(a1e); dK = sp * k
        RK = S.rotm(uK, dK); u1b = np.einsum("nji,j->ni", RK, u1)                  # u1 in link 1b's frame
        A = (u1b @ u2) * float(u2 @ u3); Bc = u1b @ u3 - A; Cs = u1b @ np.cross(u2, u3)
        R = np.hypot(Bc, Cs); q0 = np.arctan2(Cs, Bc)
        q2 = q0 + self.q2sgn * np.arccos(np.clip((np.cos(th * D2R) - A) / R, -1, 1))
        dq = np.diff(q2); dth = np.diff(th) * D2R; rate = np.abs(dq) / dth
        mono = bool(np.all(np.sign(dq) == np.sign(dq[0]))) if len(dq) else True
        r = float(P["r_lobe"]) + float(P["s_arm"]) * (k - self.dip_floor()) / float(P["g"])
        dr = np.gradient(r, q2) if len(q2) > 2 else np.zeros(len(q2)); ddr = np.gradient(dr, q2) if len(q2) > 2 else np.zeros(len(q2))
        pa = np.degrees(np.arctan(np.abs(dr) / r))
        kap = (r * r + 2 * dr * dr - r * ddr) / np.maximum((r * r + dr * dr) ** 1.5, 1e-12)
        conc = kap < 0; rconc = float((1.0 / np.abs(kap[conc])).min()) if conc.any() else None
        ok = mono and (rate.max() <= RATE_MAX + 1e-9 if len(rate) else True) and (pa.max() <= RF.PA_MAX + 1e-9)
        self._dipT = dict(ok=bool(ok), n=int(len(th)), mono=mono, rate_max=round(float(rate.max()), 3) if len(rate) else None,
                          pa_lobe_max=round(float(pa.max()), 1), r_concave_min=round(rconc, 2) if rconc is not None else None,
                          k_floor=round(math.degrees(self.dip_floor()), 2), a1e_min=round(float(a1e.min()), 2),
                          q2_span=round(float(np.degrees(abs(q2[-1] - q2[0]))), 1), lobe_dip_mm=round(float(r.max() - r.min()), 3))
        return self._dipT

    def _ik_phys(self, Q):
        """G.GDesign._ik_phys (geneva-tail-knuckle-pinknee-3r.py) with state A on the dipped law (marked DIP)"""
        if not self.p.get("cam"): return super()._ik_phys(Q)
        P = self.p; u1, u2, u3 = self.u; uK = self.uK; n = len(Q); c3 = self.c[2]; m = KIT.FOLD_MARGIN
        b1 = float(P["bk1"])
        w = Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
        Dd = self._D(); law0 = KB.KA.law; me = self

        def law_dip(p1, p3, lp):                                            # DIP: state A follows a1e(th) = a1 - dip(th)
            a1e, state, th_ = law0(p1, p3, lp)
            a1e = np.array(a1e, float); sel = (np.asarray(state) == 0) & np.isfinite(a1e)
            a1e[sel] = a1e[sel] - me.dip_of(th_[sel])
            return a1e, state, th_
        save = (P["phi_lo"], P["phi_hi"], P["a1max"]); P["phi_lo"], P["phi_hi"] = S.SING, 180 - S.SING
        if Dd > 0: KB.KA.law = law_dip
        try: qA, okA, X1A, X2A, X3A, sA = super(KR.KRDesign, self).ik(Q)      # the variant-B closure (K on stop A / the dip)
        finally:
            P["phi_lo"], P["phi_hi"], P["a1max"] = save; KB.KA.law = law0
        dKA = self._dK.copy(); stA = np.asarray(self._state).copy(); msubA = np.asarray(self._msub, float).copy()
        dipA = (stA == 0) & (self.dip_of(th) > 1e-9) if Dd > 0 else np.zeros(n, bool)   # DIP: K driven below the old stop A
        isA = (np.abs(dKA) < 1e-9) | dipA
        A, R, q0 = self._q2c
        rel = np.degrees(PK.wrap(qA[:, 1] - q0))
        if self.q2sgn is None:
            sel = okA & (np.abs(dKA) < 1e-9) & (np.abs(rel) > 1)
            self.q2sgn = float(np.sign(np.median(rel[sel]))) if sel.any() else 1.0; P["q2sgn"] = self.q2sgn
        sg = self.q2sgn
        q2hi, q2lo = self._q2_at(self.th_hi, sg), self._q2_at(self.th_lo, sg)
        self.q2_stops = (math.degrees(q2lo), math.degrees(q2hi))
        inA = okA & isA & (np.sign(rel) == sg) & (th >= self.th_lo - 1e-6) & (th <= self.th_hi + 1e-6)
        if Dd > 0:                                                          # DIP: the cam on q2 must exist (monotone, rate, lobe pa)
            T = self.dip_table()                                            # (msub, the J1-K-J3 sub-chain margin, is the stretched
            inA &= ~dipA | bool(T["ok"])                                    # law's free-K rule; here J2 moves and K follows q2)
        L = self.law()
        st = np.where(th > self.th_hi, 1, np.where(th < self.th_lo, -1, 0)); st = np.where(inA, 0, st)
        if L.get("ok"):
            thL = L["th"]; tt = np.interp(th, thL, L["ts"]); inlaw = (st == 1) & (th <= thL[-1] + 1e-9)
            dKf = np.interp(tt, L["ts"], L["dK"]); q2s = q2hi + L["s_q"] * tt
        else:
            inlaw = np.zeros(n, bool); dKf = np.zeros(n); q2s = np.full(n, q2hi); tt = np.zeros(n)
        q2s = np.where(st == 1, q2s, q2lo); dK = np.where(inlaw, dKf, 0.0)
        Rq = S.rotm(u2, q2s) if n else np.zeros((0, 3, 3)); p = Rq @ u3
        RK = S.rotm(uK, dK) if n else np.zeros((0, 3, 3))
        q1 = S.sub1(u1, np.einsum("nij,nj->ni", RK, p), w)
        R1 = S.rotm(u1, q1) if n else np.zeros((0, 3, 3))
        R12 = R1 @ RK @ Rq; vv = KR.unit3(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, vv))
        R3 = S.rotm(u3, q3) if n else np.zeros((0, 3, 3)); R123 = R12 @ R3
        t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        fA = st == 0; fa = fA[:, None]; fa3 = fA[:, None, None]
        q = np.where(fa, qA, np.stack([q1, q2s, q3], 1))
        R1m = np.where(fa3, X1A[0], R1); R2m = np.where(fa3, X2A[0], R12); R3m = np.where(fa3, X3A[0], R123); t3m = np.where(fa, X3A[1], t3)
        RKA = S.rotm(uK, dKA) if n else np.zeros((0, 3, 3))                 # DIP: K's own angle in state A (identity off the dip)
        RKm = np.where(fa3, RKA, RK); dKm = np.where(fA, np.where(dipA, dKA, 0.0), dK)
        a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RKm, u2) @ u1, -1, 1)))
        cK = np.degrees(np.arccos(np.clip(p @ uK, -1, 1)))
        msub = np.minimum.reduce([th - np.abs(b1 - cK), b1 + cK - th, 360 - b1 - cK - th])
        m3e = KR.dyad_margin(th, a1e, self.a2)
        ok = np.where(fA, inA, inlaw & (msub >= m - 1e-6)) & bool(self.k_ok) & bool(self.stops_ok)
        if P.get("m3e", 1): ok &= m3e >= m - 1e-6
        Z0 = np.zeros((n, 3)); X1 = (R1m, Z0); X1b = (R1m @ RKm, Z0); X2 = (R2m, Z0); X3 = (R3m, t3m)
        sv = np.einsum("nji,nj->ni", Q, t3m); s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        self._X1b, self._dK, self._state, self._a1e = X1b, dKm, st, a1e
        self._msub = np.where(fA, np.where(dipA, msubA, 99.0), msub); self._m3e = m3e; self._dipA = dipA & fA
        self._camt = np.where(st == 1, np.degrees(tt), 0.0); self._q2now = q[:, 1]
        return q, ok, X1, X2, X3, s


KB.KDesign = DipDesign; G.KR.KB.KDesign = DipDesign


class DipModel(RL.RLModel):
    def _sc_pose(self):
        """RF's per-pose crank transform on the SIGNED opening (the crank swings backward in the dip)"""
        g = self._scg; ks = g["sp"] * np.asarray(self.dK, float); n = len(ks)
        php = g["sig"] * phi_of(ks, g["g"], g.get("c", 0.0))
        Rc = S.rotm(g["dR"], php); tc = g["PV"][None] - np.einsum("nij,j->ni", Rc, g["PV"])
        self._sc = dict(n=n, X={9: (Rc, tc), 8: (Rc, tc)})

    def _truncate(self):
        """poses whose K is past the drive's own range on either side are lost: stop B at dK_lim, stop A at dK_neg"""
        g = getattr(self, "_scg", None)
        if g is None or "dK_lim" not in g or not len(self.poses_fit): return
        ks = g["sp"] * np.asarray(self.dK, float)[self.poses_fit]
        bad = (ks > g["dK_lim"] + 1e-9) | (ks < float(g.get("dK_neg", 0.0)) - 1e-9)
        self._n_trunc = int(bad.sum())
        if not bad.any(): return
        for i in self.poses_fit[bad]: self.why[i] = "fold"
        keep = ~bad; self.poses_fit = self.poses_fit[keep]; self.drop = self.drop[keep]

    def _rod_metal(self):
        self._rf_rod_metal_dip()
        # RL.RLModel._rod_metal's addition (copied): the roller's retaining stub head, skin side of the roller
        C0 = np.asarray(self._viz_rod["roller"], float); cr = unit(C0); e, f = S.frame_of(cr); dd = S.disc(RL.HEAD_R, 1.5)
        head = C0 - (1.25 + RL.HEAD_T) * cr + dd[:, :1] * e + dd[:, 1:] * f
        ring = SC._ring(C0 - (1.25 + RL.HEAD_T) * cr, RL.HEAD_R, cr)
        m, X = self.rigid["roller"]; self.rigid["roller"] = (m, np.concatenate([X, head]))
        self.contact.append((9, np.concatenate([head, ring])))
        mR, XR = self.strap["ROD"]; self.strap["ROD"] = (mR, np.concatenate([XR, ring]))
        self._sc_info["stub_head"] = [RL.HEAD_R * 2, RL.HEAD_T]

    def _rf_rod_metal_dip(self):
        """RF.RFModel._rod_metal (sidecar-roller-flank-knuckle-3r.py) copied, with the K grid extended to the dip's closing range
        [kneg, 0) (marked DIP): the flank, both pressure angles, lift-off, cusp, contact on the lug and the arm / roller / lug
        clearances are synthesised and checked on the negative side too; stop A sits at the last good negative step."""
        kneg = self.D.dip_kneg()                                            # DIP: rad, <= 0 (dip floor - 1 deg)
        D = self.D; P = D.p; u2, uK = D.u[1], D.uK; fK, f2 = self.fK, self.f[1]
        L1b = self.link_pts["L1b"][1]
        g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0); ax = unit(np.cross(u2, uK)); dR = unit(S.rotm(ax, g0)[0] @ u2)
        near = L1b[np.argsort(np.linalg.norm(unit(L1b) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max())
        tK0 = unit(dR - (dR @ uK) * uK); bK0 = unit(np.cross(uK, tK0))
        beta = float(P["beta"]) * D2R; rc = float(P["r_c"]); gg = float(P["g"]); cc = float(P.get("cprog", 0.0))
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
        phis = sig * phi_of(np.linspace(kneg, dKmax, 9), gg, cc)          # DIP: the backward swing too
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
        kpos = np.radians(np.arange(0.0, max(math.degrees(dKmax), 5.0) + 1e-6, 0.25))
        kng = -np.radians(np.arange(0.25, -math.degrees(kneg) + 1e-6, 0.25))[::-1] if kneg < 0 else np.zeros(0)
        kgrid = np.concatenate([kng, kpos]); nk = len(kgrid); j0 = len(kng)            # DIP: kgrid[j0] = 0 (rest)
        Rk = S.rotm(uK, sp * kgrid)                                       # link 1b -> link 1a: X_1a = Rk X_1b
        Rcg = S.rotm(dR, sig * phi_of(kgrid, gg, cc))
        Cg = np.einsum("nij,j->ni", Rcg, C0 - PV) + PV
        pac = np.zeros(nk); pah = np.zeros(nk); Qg = np.zeros((nk, 3)); ng = np.zeros((nk, 3)); lift = np.zeros(nk, bool)
        nprev = None
        for j in list(range(j0, nk)) + list(range(j0 - 1, -1, -1)):           # DIP: seed at rest, then up, then down
            if j == j0 - 1: nprev = ng[j0]
            C = Cg[j]; vC = sig * float(dphi_of(kgrid[j], gg, cc)) * np.cross(dR, C); vh = vH(C); vr = vC - vh; rh = unit(C)
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
        bad = {"pressure_crank": pac > RF.PA_MAX + 1e-9, "pressure_horn": pah > RF.PA_MAX + 1e-9, "liftoff": lift, "flank_cusp": flank_bad,
               "contact_off_lug": rQ < R_CMIN, "CRK-hubK": cK < 1.0, "ROLL-hubK": cR < 1.0, "CRK-hub2": c2 < 1.0}
        badany = np.zeros(nk, bool)
        for v in bad.values(): badany |= v
        jlim = j0 + int(np.argmax(badany[j0:])) if badany[j0:].any() else nk          # DIP: first bad step above rest
        why_lim = [k_ for k_, v in bad.items() if v[jlim]][0] if jlim < nk else "law"
        jl = max(jlim - 1, j0); lim = float(kgrid[jl])
        jneg = (int(np.nonzero(badany[:j0])[0].max()) + 1) if badany[:j0].any() else 0   # DIP: last good step below rest
        why_neg = [k_ for k_, v in bad.items() if v[jneg - 1]][0] if jneg > 0 else None
        # ---- the horn lug (link 1a, member 1), built from the flank over the used stroke [0, lim]
        def plane(X): return X / np.linalg.norm(X, axis=1)[:, None] * rL      # lug underside on the sphere |X| = |C0| - 1.5
        sel = np.arange(jneg, jl + 1); dsum = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(Q1[sel], axis=0), axis=1))])
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
            for j in range(jneg, jl + 1):
                XL = (low - PV) @ Rcg[j].T + PV; XG = lugM @ Rk[j]           # Rk^T applied to rows: X_1b = Rk^T X_1a
                cL[j] = float(cKDTree(XG).query(XL)[0].min())
            badL = cL[j0: jl + 1] < 1.0
            if badL.any():
                jl2 = max(j0 + int(np.argmax(badL)) - 1, j0)
                if jl2 < jl: jl, lim, why_lim = jl2, float(kgrid[jl2]), "CRK-HORN"
            badN = cL[jneg: j0] < 1.0                                              # DIP: the low arm vs the lug, closing side
            if badN.any(): jneg = jneg + int(np.nonzero(badN)[0].max()) + 1; why_neg = "CRK-HORN"
        self._cam_table = dict(k=np.degrees(kgrid), phi=np.degrees(phi_of(kgrid, gg, cc)), pa_crank=pac, pa_horn=pah, contact_r=rQ, flank_rho=flank_rho,
                               clear_hubK=cK, clear_roll_hubK=cR, clear_hub2=c2, lift=lift, cusp=flank_bad)
        self._scg = dict(PV=PV, dR=dR, uK=uK, sp=sp, sig=sig, g=gg, c=cc, kgrid=kgrid, dK_lim=lim, why_lim=why_lim, j0=j0, dK_neg=float(kgrid[jneg]), why_neg=why_neg, lowarm=low, lugM=lugM)
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
        self._viz_rod = dict(rocker=PV, rockerAx=dR, rodA=C0, rodB=C0, armA=PV, armB=T3, roller=C0, armPts=armPts, lugPts=lugPts, sig=sig, g=gg, c=cc)
        ks = sp * np.asarray(self.dK, float); taken = np.asarray(self.kin_ok, bool)                    # DIP: signed opening
        kmax_t = float(ks[taken & (ks > 1e-9)].max()) if (taken & (ks > 1e-9)).any() else 0.0; jt = min(int(np.searchsorted(kgrid, min(kmax_t, lim))) + 1, nk)
        kmin_t = float(ks[taken & (ks < -1e-9)].min()) if (taken & (ks < -1e-9)).any() else 0.0
        ja = max(min(int(np.searchsorted(kgrid, max(kmin_t, float(kgrid[jneg])))) - 1, j0), jneg)
        self._sc_info = dict(boss_level=round(zboss, 1), lev_L1b=round(lev, 1), arm_tip_level=round(float(np.linalg.norm(T3)), 1), g=round(gg, 3), sig=sig,
                             r_c=round(rc, 2), beta=round(float(P["beta"]), 2), arm_len=round(Lch + rc * abs(beta - psT), 1), arc_deg=round(math.degrees(abs(beta - psT)), 1) if abs(beta) > abs(psT) else 0.0,
                             rssr_closed=True, pa_crank_rest=round(float(pac[0]), 1), pa_horn_rest=round(float(pah[0]), 1),
                             vel_angle_rest=round(_ang((sig / gg) * np.cross(dR, C0), vH(C0)), 1),
                             pa_crank_max_taken=round(float(pac[ja:jt].max()), 1), pa_horn_max_taken=round(float(pah[ja:jt].max()), 1),
                             pa_crank_dip_max=round(float(pac[ja:j0 + 1].max()), 1), pa_horn_dip_max=round(float(pah[ja:j0 + 1].max()), 1),
                             dK_neg=round(math.degrees(float(kgrid[jneg])), 2), why_neg=why_neg, dK_dip_taken=round(math.degrees(kmin_t), 2),
                             flank_rho_min=round(float(np.abs(flank_rho[jneg:jl + 1]).min()), 1), contact_r=[round(float(rQ[jneg]), 1), round(float(rQ[jl]), 1)],
                             clear_hubK_min=round(float(cK[jneg:jl + 1].min()), 2), clear_roll_hubK_min=round(float(cR[jneg:jl + 1].min()), 2),
                             clear_lowarm_lug_min=round(float(cL[jneg:jl + 1].min()), 2) if len(low) else None, n_lowarm=int(len(low)),
                             phi_max_taken=round(math.degrees(float(phi_of(min(kmax_t, lim), gg, cc))), 1), cprog=round(cc, 3),
                             crest_exact=round(float(P["r_lobe"]) + float(P["s_arm"]) * float(phi_of(min(kmax_t, lim) - float(kgrid[jneg]), gg, cc)), 2),   # DIP: base at the dip floor
                             dK_lim=round(math.degrees(lim), 1), why_lim=why_lim, law_dK_max=round(float(L_.get("dK_max", 0.0)), 1),
                             lug_r_max=round(float(np.linalg.norm(lug - (lug @ uK)[:, None] * uK, axis=1).max()), 1))
        self._rod_info = self._sc_info

SC.SCModel = DipModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS; RL.PARAMS = PARAMS
FL.G.KR.KB.KModel = DipModel; FL.FLModel_SC = DipModel; KB.KModel = DipModel


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = RL._report(B, p)
    D = M.D; info = getattr(M, "_sc_info", None) or {}
    if D._D() > 0:
        T = D.dip_table(); ko = np.asarray(M.kin_ok, bool); dA = getattr(D, "_dipA", np.zeros(len(ko), bool))
        n_d = int((dA & ko).sum()) if len(dA) == len(ko) else None
        r["dip"] = dict(T, D=round(D._D(), 2), th_c=p["dip_thc"], w=p["dip_w"], shape=p["dip_shape"], n_dip_taken=n_d,
                        dK_neg=info.get("dK_neg"), why_neg=info.get("why_neg"), dK_dip_taken=info.get("dK_dip_taken"),
                        pa_crank_dip_max=info.get("pa_crank_dip_max"), pa_horn_dip_max=info.get("pa_horn_dip_max"),
                        lift_mm=round(float(D.law().get("dip_lift_mm", 0.0)), 3))
        if not T.get("ok"): r["honest"] = False; r["dip_fail"] = True
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("dip_fail"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360): return SC.frozen(_clamp(dict(PARAMS, **P)), nc, nw)
def frozen_held(P): return SC.frozen(_clamp(dict(PARAMS, **P)), -1, -1)
def frozen_flood(P, nc=110, nw=360): return SC.frozen_flood(_clamp(dict(PARAMS, **P)), nc, nw)
def viz_export(par): return RF.viz_export(_clamp(dict(PARAMS, **par)))


def part_min(M, B, i):
    """per-part minimum signed skin distance (mm) of pose i: rigid samples by name, contact-only samples by member"""
    out = {}
    for nm, (m, X) in M.rigid.items():
        if len(X): out[nm] = round(float(B.dist(i, M.world(m, i, X)).min()), 2)
    mem = {}
    for m, X in M.contact:
        if len(X): mem[m] = min(mem.get(m, 99.0), float(B.dist(i, M.world(m, i, X)).min()))
    out.update({"m%d" % m: round(v, 2) for m, v in mem.items()})
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"), near2=a.get("gap_near2"),
                              minmetal=a.get("near_touch_min_mm"), ovh=a.get("overhead140"), parts=out.get("parts_ib14"),
                              connected=out.get("connected"), sidecar=out.get("sidecar"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"),
                          idle=r.get("drive_idle"), cam_short=r.get("cam_short"), pa_fail=r.get("pa_fail"), why=r.get("why"),
                          ovh=r.get("overhead140"), ws_inband=r.get("ws_inband"), cam=r.get("cam"), dip=r.get("dip"), parts=r.get("parts_ib14"),
                          pairs=r.get("parts_pairs"), split=RL.contact_split(M, B) if mode == "split" else None,
                          secs=round(time.time() - t)), default=float))
