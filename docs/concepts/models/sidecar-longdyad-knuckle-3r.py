"""sidecar-longdyad-knuckle-3r: the verified lead's slaved knuckle (frontload-lobe-stopb-knuckle-3r: kit-rule B, pin knee,
physical q2 stop, near-touch objective, K slaved past the onset by a hub-2 rim lobe) with
  (1) the SIDECAR drive at strap level instead of the crown-high rod: a bell crank on an MR63ZZ pair stacked on link 1b
      beside hub 2 (short arm s_arm on the hub-2 rim lobe, long arm La lying sideways), an O3 Ti rod running beside
      link 1b to a lateral horn lug of link 1a at hub K (radius r_h, azimuth beta from link 1b's direction), M2 ball
      links at both rod ends. Gain: rod travel r_h dK = La phi, follower lift s_arm phi, so i_rock = La / s_arm and the
      parent's lobe gates hold (tan pa = k r_h / (i_rock r(t)) <= tan 45, crest r(t) <= HUB_R + 1.5);
  (2) a LONGER K dyad on link 1b (bk2 40-48), so stop B a1max <= bk1 + bk2 - 5 can rise from 62.6 to 66-75.
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations.

THE PER-POSE METAL (not the proposer's rest-only sampling): the rod (member 8) and the bell crank (member 9) are their
own bodies. Per bench pose the RSSR loop is closed in link 1b's frame: the horn ball (fixed to link 1a) sits at
R(uK, dK)^T H0, the crank tip turns about the crank axis dR by phi, |tip(phi) - H(dK)| = L_rod (rest length) is solved
on a phi grid with continuation from phi = 0, so the rod, its ball-link bodies and the crank arm are sampled where they
are in that pose (skin, in band, near-touch, part pairs). The real RSSR ratio dphi/ddK and the transmission angle are
reported and gated (transmission >= 30 deg over the taken range).

STACKING (honest, the proposer sampled the crank boss inside link 1b): the crank's pin is in link 1b, so the boss
(O10 x 6, two MR63ZZ) sits ON link 1b (underside at link 1b's top + 0.15 running gap); the long arm (3 thick, 6 wide)
leaves the boss at that level and may step down (60-deg joggle) to link 1b's own layer (zr >= 0 over link 1b's
underside) only where it is >= W_LINK / 2 + 1 mm clear of link 1b's strap over the whole swing. The horn lug of link 1a
sits hl above hub K's base level (hl 0..3.15: 3.15 = link 1a's own layer at K, flipped stack); a horn below link 1a's
layer must clear link 1b's strap (1 mm) in every pose (checked).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/sidecar-longdyad-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 python3 docs/concepts/models/sidecar-longdyad-knuckle-3r.py frozen '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("frontload_for_sidecar_longdyad", os.path.join(HERE, "frontload-lobe-stopb-knuckle-3r.py"))
FL = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(FL)
G, KR, KB, PK, S = FL.G, FL.KR, FL.KB, FL.PK, FL.S
unit = S.unit; D2R = math.pi / 180
ID = "sidecar-longdyad-knuckle-3r"
FL.I_ROCK_MAX = 8.0                                          # the bell crank's La / s_arm (the lead's clevis was capped at 2.5)
ER, ZB, BOSS_H, RUNG = 3.5, 3.0, 6.0, 0.15                   # M2 ball-link socket r, ball centre over the lug/arm top, boss, running gap
TRANS_MIN = 30.0

# the lead's seats (rows/frontload-lobe-stopb-knuckle-3r.json best_params) + the judge's seed for this row
LEAD = {"az1": 95.3594, "el1": 67.6187, "az2": 42.7487, "el2": 43.9031, "wd": 63.5262, "wa": -10.5604, "b3": 0.3825,
        "ang_min": 27.8606, "lE": 67.832, "lc": 25.8149, "phiE": -2.7863, "phib": -65.6717, "stk": 4.8534, "smhi": 14.7672,
        "smlo": 5.1723, "capK": 6.0, "tail": 1, "emb_mode": "rod"}
SEED = dict(LEAD, bk1=30.0, bk2=44.0, a1max=66.0, law_mode="lin", kK=2.0, r_h=15.0, beta=-112.0, hl=3.15, zr=1.5, La=20.0,
            s_arm=5.0, r_lobe=7.5)
PARAMS = dict(FL.PARAMS, **SEED)


def _clamp(p):
    """component limits (CMA has no bounds): bell crank La 12-26, s_arm 4-6 (i_rock = La / s_arm), horn r_h 13-22,
    lobe base 7-8.5, hl 0-3.15, zr >= 0, a1max <= bk1 + bk2 - 5; 'lin' = the parent's per-t gated law with kA = kB = kK"""
    p["La"] = min(max(float(p["La"]), 12.0), 26.0); p["s_arm"] = min(max(float(p["s_arm"]), 4.0), 6.0)
    p["r_h"] = min(max(float(p["r_h"]), 13.0), 22.0); p["r_lobe"] = min(max(float(p["r_lobe"]), 7.0), 8.5)
    p["hl"] = min(max(float(p["hl"]), 0.0), 3.15); p["zr"] = max(float(p["zr"]), 0.0)
    p["i_rock"] = p["La"] / p["s_arm"]; p["r_horn"] = p["r_h"]
    if p.get("law_mode", "lin") == "lin":
        p["kK"] = max(float(p["kK"]), 0.0); p["kA"] = p["kB"] = p["kK"]; p["t1"] = 6.0; p["law_mode_in"] = "lin"; p["law_mode"] = "seg"
    for k in ("kA", "kB"): p[k] = max(float(p[k]), 0.0)
    p["t1"] = max(float(p["t1"]), 0.5); p["smt"] = max(float(p.get("smt", 12.0)), 5.2)
    p["a1max"] = min(float(p["a1max"]), float(p["bk1"]) + float(p["bk2"]) - 5.0)
    return p


def _ring(c, r, axv, n=16):
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False); a, b = S.frame_of(axv)
    return c + r * (np.cos(ang)[:, None] * a + np.sin(ang)[:, None] * b)


class SCModel(FL.FLModel):
    def T(self, m, i):
        if m in (8, 9) and getattr(self, "_scg", None) is not None:
            if getattr(self, "_sc", None) is None or self._sc["n"] != len(self.dK): self._sc_pose()
            R7, t7 = super().T(7, i); Rb, tb = self._sc["X"][m]
            return R7 @ Rb[i], R7 @ tb[i] + t7
        return super().T(m, i)

    def fit(self):
        super().fit(); self._truncate()

    def _truncate(self):
        """poses whose K opening is past the drive's own range (dK_lim) are not reachable: J2's stop B dowel sits there"""
        g = getattr(self, "_scg", None)
        if g is None or "dK_lim" not in g or not len(self.poses_fit): return
        dk = np.abs(np.asarray(self.dK, float))[self.poses_fit]; bad = dk > g["dK_lim"] + 1e-9
        self._n_trunc = int(bad.sum())
        if not bad.any(): return
        for i in self.poses_fit[bad]: self.why[i] = "fold"
        keep = ~bad; self.poses_fit = self.poses_fit[keep]; self.drop = self.drop[keep]

    def _sc_pose(self):
        """per-pose transforms (link 1b frame) of the crank (9) and the rod (8) from the RSSR table phi(|dK|)"""
        g = self._scg; PV, dR, tip0, H0, uK, sp = g["PV"], g["dR"], g["tip0"], g["H0"], g["uK"], g["sp"]
        dKp = np.abs(np.asarray(self.dK, float)); n = len(dKp)
        php = np.interp(dKp, g["kgrid"], g["phig"])
        Rc = S.rotm(dR, php); tc = PV[None] - np.einsum("nij,j->ni", Rc, PV)
        tipp = np.einsum("nij,j->ni", Rc, tip0 - PV) + PV
        Hp = np.einsum("nji,j->ni", S.rotm(uK, sp * dKp), H0)    # R^T H0
        v0 = unit(H0 - tip0); v1 = (Hp - tipp) / np.linalg.norm(Hp - tipp, axis=1)[:, None]
        axr = np.cross(v0[None], v1); sn_ = np.linalg.norm(axr, axis=1); cs_ = v1 @ v0
        Rr = np.zeros((n, 3, 3))
        for j in range(n):
            Rr[j] = np.eye(3) if sn_[j] < 1e-9 else S.rotm(axr[j] / sn_[j], math.atan2(sn_[j], cs_[j]))[0]
        tr = tipp - np.einsum("nij,j->ni", Rr, tip0)
        self._sc = dict(n=n, X={9: (Rc, tc), 8: (Rr, tr)})

    def _rod_metal(self):
        D = self.D; P = D.p; u2, uK = D.u[1], D.uK; fK, f2 = self.fK, self.f[1]
        L1b = self.link_pts["L1b"][1]
        g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0); ax = unit(np.cross(u2, uK)); dR = unit(S.rotm(ax, g0)[0] @ u2)
        near = L1b[np.argsort(np.linalg.norm(unit(L1b) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max())
        tK0 = unit(dR - (dR @ uK) * uK); sK = unit(S.rotm(uK, float(P["beta"]) * D2R)[0] @ tK0); sR = unit(sK - (sK @ dR) * dR)
        sR = unit(S.rotm(dR, float(P.get("gam", 0.0)) * D2R)[0] @ sR)   # crank phase: pre-rotates the arm so the swing straddles 90 deg of transmission
        bnR = unit(np.cross(dR, sR)); La, RH = float(P["La"]), float(P["r_h"])
        zboss = lev + S.T_LINK + RUNG                               # crank boss / arm root underside: stacked on link 1b
        PV = dR * zboss
        # link 1b's planform (strap points) near the crank, for the arm's step-down rule
        L1d = unit(L1b); w_ok = S.W_LINK / 2 + 1.0
        rs = np.arange(0.0, La + 1e-6, 2.0); ws_ = np.array([-3.0, -1.0, 1.0, 3.0])
        # law range of the crank swing: one-sided, from a stacked-arm RSSR pass (the exact table is rebuilt below)
        L_ = D.law(); dKmax = math.radians(float(L_.get("dK_max", 0.0)) + 2.0) if L_.get("ok") else 0.2
        sp = float(np.sign(D.psiA)) or 1.0; zb_s = -1.0 if P.get("ball_low") else 1.0
        lvK = fK + float(P["hl"]); H0 = uK * (lvK + (S.T_LINK + ZB if zb_s > 0 else -ZB)) + RH * sK
        k = math.tan(S.RAMP * D2R)

        def arm_levels(phis):
            lvl = np.zeros(len(rs))
            for j, r_ in enumerate(rs):
                clear = r_ > 5.0
                for ph in phis:
                    if not clear: break
                    Rp = S.rotm(dR, ph)[0]
                    for w_ in ws_:
                        x = Rp @ (dR * zboss + r_ * sR + w_ * bnR)
                        if np.arccos(np.clip(L1d @ unit(x), -1, 1)).min() * zboss < w_ok: clear = False; break
                lvl[j] = lev + float(P["zr"]) if clear else zboss
            return np.max(lvl[None, :] - k * np.abs(rs[:, None] - rs[None, :]), axis=1)

        def tip_of(lvl): return dR * (lvl[-1] + (S.T_LINK + ZB if zb_s > 0 else -ZB)) + La * sR

        def phi_end(tip0):
            Lr = float(np.linalg.norm(H0 - tip0)); pg_ = np.radians(np.arange(-100.0, 100.0 + 1e-6, 0.1))
            TP = np.einsum("nij,j->ni", S.rotm(dR, pg_), tip0 - PV) + PV; H = S.rotm(uK, sp * dKmax)[0].T @ H0
            fv = np.linalg.norm(TP - H, axis=1) - Lr; sgn = np.nonzero(np.diff(np.sign(fv)) != 0)[0]
            return float(pg_[sgn][np.argmin(np.abs(pg_[sgn] - (RH * dKmax / La)))]) if len(sgn) else RH * dKmax / La
        lvl = np.full(len(rs), zboss); pe = phi_end(tip_of(lvl)); pe = phi_end(tip_of(arm_levels(np.linspace(0, pe, 7))))
        lvl = arm_levels(np.linspace(0, pe * 1.05, 9))
        arm = np.array([dR * lvl[j] + r_ * sR + w_ * bnR for j, r_ in enumerate(rs) for w_ in ws_])
        e, f = S.frame_of(dR); dd = S.disc(5.0, 2.0)
        boss = PV + dd[:, :1] * e + dd[:, 1:] * f
        tip0 = tip_of(lvl)                                          # ball centre on the arm tip (above its top, or below its underside)
        # horn lug of link 1a (member 1): from hub K's rim to r_h + 4 along sK, 6 wide, underside fK + hl
        bnK = unit(np.cross(uK, sK))
        horn = np.array([uK * lvK + r_ * sK + w_ * bnK for r_ in np.arange(S.HUB_R + 0.5, RH + 4.0 + 1e-6, 2.0) for w_ in (-3.0, -1.0, 1.0, 3.0)])
        Lrod = float(np.linalg.norm(H0 - tip0))
        # RSSR closure table phi(|dK|) in link 1b's frame (continuation from phi = 0)
        kgrid = np.radians(np.arange(0.0, max(math.degrees(dKmax), 5.0) + 1e-6, 0.25)); phig = np.zeros(len(kgrid)); trans = np.full(len(kgrid), 90.0)
        pg = np.radians(np.arange(-100.0, 100.0 + 1e-6, 0.05)); Rg = S.rotm(dR, pg); TPg = np.einsum("nij,j->ni", Rg, tip0 - PV) + PV
        prev = 0.0; okc = True
        for j, kk in enumerate(kgrid):
            H = S.rotm(uK, sp * kk)[0].T @ H0
            fval = np.linalg.norm(TPg - H, axis=1) - Lrod
            sgn = np.nonzero(np.diff(np.sign(fval)) != 0)[0]
            if not len(sgn): okc = False; phig[j:] = prev; trans[j:] = 0.0; break
            roots = pg[sgn] - fval[sgn] * (pg[sgn + 1] - pg[sgn]) / (fval[sgn + 1] - fval[sgn])
            ph = float(roots[np.argmin(np.abs(roots - prev))]); phig[j] = ph; prev = ph
            tp = S.rotm(dR, ph)[0] @ (tip0 - PV) + PV; rod = unit(H - tp)
            vt = unit(np.cross(dR, tp - PV)); vh = unit(np.cross(uK, H))     # crank tip / horn ball velocity directions
            # transmission angle = 90 - the worse pressure angle (rod force vs the velocity of the crank tip / horn ball)
            trans[j] = 90.0 - max(math.degrees(math.acos(min(1, abs(float(rod @ vt))))), math.degrees(math.acos(min(1, abs(float(rod @ vh))))))
        ratio = np.gradient(phig, kgrid) if len(kgrid) > 2 else np.ones(len(kgrid))
        self._scg = dict(PV=PV, dR=dR, tip0=tip0, H0=H0, uK=uK, sp=sp, kgrid=kgrid, phig=phig); self._sc = None
        dKp = np.abs(np.asarray(self.dK, float)); dKsave = self.dK
        # metal: crank (boss underside disc + arm underside + the tip's socket ring), rod (underside), ball-link sockets
        self.rigid["crank"] = (9, np.concatenate([boss, arm]))
        self.rigid["horn"] = (1, horn)
        nr = max(3, int(Lrod / S.SPACING)); sg = np.linspace(0, 1, nr)[:, None]
        rodc = tip0[None] * (1 - sg) + H0[None] * sg
        self.rigid["rod"] = (8, rodc - 1.5 * unit(rodc))
        endsB = np.concatenate([_ring(tip0 - ZB * dR, ER, dR), _ring(H0 - ZB * uK, ER, uK)]) if zb_s > 0 else \
            np.concatenate([_ring(tip0 - 3.5 * dR, ER, dR), _ring(H0 - 3.5 * uK, ER, uK)])
        self.rigid["rodends"] = (8, endsB)
        self.rigid.pop("rocker", None)
        self._contact_only(); self._solids()
        endsT = np.concatenate([_ring(tip0 + 3.5 * dR, ER, dR), _ring(H0 + 3.5 * uK, ER, uK)]) if zb_s > 0 else \
            np.concatenate([_ring(tip0 + ZB * dR, ER, dR), _ring(H0 + ZB * uK, ER, uK)])
        cyl = np.concatenate([_ring(dR * z, 5.0, dR) for z in np.linspace(zboss, zboss + BOSS_H, 4)])
        self.contact.append((8, np.concatenate([endsB, endsT, rodc + 1.5 * unit(rodc)])))
        self.contact.append((9, np.concatenate([cyl, arm + S.T_LINK * dR])))
        self.contact.append((1, horn + S.T_LINK * uK))
        self.strap["ROD"] = (8, np.concatenate([endsB, endsT, rodc]))
        self.strap["CRK"] = (9, np.concatenate([cyl, arm + 1.5 * dR]))
        self.strap["HORN"] = (1, horn + 1.5 * uK)
        self._crown_ok = True
        # THE DRIVE'S OWN RANGE (red team 18:45: a crank phase that buys transmission swings the rod into hub 2 at dK > 42,
        # which the fit bench never reached - 8 frozen / 24 held-out poses lost as ROD-hub2): on the RSSR table, the first
        # |dK| where the transmission < TRANS_MIN or the rod comes < 1 mm to hub 2's housing / link 1b, or the crank's
        # long arm < 1 mm to hub 2, ends the usable range; stop B (the q2 dowel) sits there, so every pose past it is lost
        # on EVERY bench (self._truncate after each fit)
        mem2, cen2, ax2 = self.cyl["hub2"]; r2 = self.cyl_r["hub2"]; L1bS = self.strap["L1b"][1]
        def farX(X, pad): w = X - cen2; return X[np.linalg.norm(w - (w @ ax2)[:, None] * ax2, axis=1) > r2 + pad]
        L1b_far = farX(L1bS, 4.0); treeL1b = cKDTree(L1b_far) if len(L1b_far) else None
        lim, why_lim = float(kgrid[-1]), "law"
        for j, kk in enumerate(kgrid):
            self.dK = np.array([sp * kk]); self._sc = None; self._sc_pose()
            Rr, trr = self._sc["X"][8]; Rc, tcc = self._sc["X"][9]
            XR = self.strap["ROD"][1] @ Rr[0].T + trr[0]; XC = self.strap["CRK"][1] @ Rc[0].T + tcc[0]
            dh2 = float(self.sd_cyl(XR, cen2, ax2, r=r2).min())
            dl1b = float(treeL1b.query(farX(XR, 4.0))[0].min()) - S.T_LINK / 2 if treeL1b is not None and len(farX(XR, 4.0)) else 99.0
            XCf = farX(XC, 6.5); dc2 = float(self.sd_cyl(XCf, cen2, ax2, r=r2).min()) - S.T_LINK / 2 if len(XCf) else 99.0
            bad = {"transmission": trans[j] < TRANS_MIN, "ROD-hub2": dh2 < 1.0, "ROD-L1b": dl1b < 1.0, "CRK-hub2": dc2 < 1.0}
            if any(bad.values()):
                lim = float(kgrid[max(j - 1, 0)]); why_lim = [k_ for k_, v in bad.items() if v][0]; break
        self.dK = dKsave; self._sc = None
        self._scg.update(dK_lim=lim, why_lim=why_lim)
        self._viz_rod = dict(rocker=PV, rockerAx=dR, rodA=tip0, rodB=H0, armA=PV, armB=tip0 - (S.T_LINK + ZB) * dR)
        taken = (np.asarray(self.kin_ok, bool)) & (dKp > 1e-9)
        kmax_t = float(dKp[taken].max()) if taken.any() else 0.0
        jt = int(np.searchsorted(kgrid, kmax_t)) + 1
        self._sc_info = dict(boss_level=round(zboss, 1), lev_L1b=round(lev, 1), arm_tip_level=round(float(lvl[-1]), 1), rod_len=round(Lrod, 1),
                             La=round(La, 1), r_h=round(RH, 1), i_rock=round(float(P["i_rock"]), 2), rssr_closed=bool(okc),
                             trans_min_taken=round(float(trans[:jt].min()), 1), ratio_range=[round(float(ratio[:jt].min()), 3), round(float(ratio[:jt].max()), 3)],
                             ratio_small_angle=round(RH / La, 3), phi_max_taken=round(math.degrees(float(np.interp(kmax_t, kgrid, phig))), 1),
                             crest_exact=round(float(P["r_lobe"]) + float(P["s_arm"]) * abs(float(np.interp(kmax_t, kgrid, phig))), 2),
                             dK_lim=round(math.degrees(lim), 1), why_lim=why_lim)
        self._rod_info = self._sc_info

    def collide(self, i):
        out = super().collide(i)                                     # parent: ROD vs hub1/hub3/L1a/L2/knee/pad/E
        if "CRK" not in self.strap: return out
        h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k_, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k_] = (R @ cen + t, R @ ax)
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
        def ss(A, Bq, extra): return float(cKDTree(Bq).query(A)[0].min()) - extra if len(A) and len(Bq) else 1e9
        def far(X, nm, pad): cc, ax = cyl[nm]; w = X - cc; return X[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > self.cyl_r[nm] + pad]
        RD = tf(*self.strap["ROD"]); CK = tf(*self.strap["CRK"]); HN = tf(*self.strap["HORN"]); c = {}
        st = {k_: tf(m, X) for k_, (m, X) in self.strap.items() if k_ in ("L1a", "L1b", "L2")}
        c["ROD-hubK"] = vcyl(RD, "hubK"); c["ROD-hub2"] = vcyl(RD, "hub2")
        c["ROD-L1b"] = ss(far(RD, "hub2", 4), far(st["L1b"], "hub2", 4), h)
        for hb in ("hub1", "hubK", "hub3"): c[f"CRK-{hb}"] = vcyl(CK, hb, h)
        c["CRK-hub2"] = vcyl(far(CK, "hub2", 6.5), "hub2", h)        # the short arm rides the lobe; boss + long arm keep 1 mm
        c["CRK-L1a"] = ss(CK, st["L1a"], 2 * h); c["CRK-L2"] = ss(CK, st["L2"], 2 * h)
        c["HORN-L1b"] = ss(far(HN, "hubK", 1.0), far(st["L1b"], "hubK", 1.0), 2 * h)
        c["HORN-hub2"] = vcyl(HN, "hub2", h); c["HORN-L2"] = ss(HN, st["L2"], 2 * h)
        bx = self._boxes_at_final(i)
        for nm in ("knee", "pad"):
            cen, R, half = bx[nm]; c[f"{nm}-CRK"] = float(self.sd_box(CK, cen, R, half).min()) - h; c[f"{nm}-HORN"] = float(self.sd_box(HN, cen, R, half).min()) - h
        Em = tf(*self.Emid); c["E-CRK"] = ss(Em, CK, 2 * h); c["E-HORN"] = ss(Em, HN, 2 * h)
        self.last_clear.update({k_: round(v, 1) for k_, v in c.items()})
        return min(out, min(c.values()))


FL.G.KR.KB.KModel = SCModel; FL.FLModel_SC = SCModel


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    a1lim = float(p["bk1"]) + float(p["bk2"]) - 5.0
    r, M = G._report(B, p)
    L_ = M.D.law(); info = getattr(M, "_sc_info", None) or {}
    if info and (not info.get("rssr_closed", True) or info.get("crest_exact", 0) > S.HUB_R + 1.5 + 0.25):
        r["honest"] = False; r["sidecar_fail"] = True               # the RSSR does not close / toggles / the real crest leaves the skirt
    if "drive" in r:
        r["drive"].update(law_mode=p.get("law_mode_in", p.get("law_mode")), i_rock=round(float(p["i_rock"]), 3), r_h=p["r_h"],
                          lobe_r_max=round(L_.get("lobe_r_max", 0.0), 2) if L_.get("lobe_r_max") else None,
                          m3e_law_min=round(L_["m3e_min"], 2) if L_.get("m3e_min") is not None else None,
                          dKB=round(L_.get("dKB", 0.0), 1) if L_.get("dKB") else None, a1max=round(p["a1max"], 2), a1max_lim=round(a1lim, 2),
                          sidecar=info, truncated=getattr(M, "_n_trunc", 0))
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    """= KB.frozen (fit on Bench(60,160) fast, the shape frozen, worn on Bench(nc, nw) exact) + the sidecar's geometry
    carried over (the per-pose RSSR transforms are rebuilt from the worn bench's own K states)"""
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = SCModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(SCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if nc == -1:
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_sidecar", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
        PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); B = PVm.held_bench()
    else:
        B = CB.Bench(n_clip=nc, n_ws=nw)
    M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    return dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
                parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), sidecar=getattr(M1, "_sc_info", None))


def frozen_held(P):
    return frozen(P, -1, -1)


def frozen_flood(P, nc=110, nw=360):
    """frozen exact wear + the continuity flood fill on the worn model (the round-6 verifier's connected_report,
    docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py): reach static and connected"""
    out = {}
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = SCModel(B1, dict(P)); M1.run(); P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(SCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    os.environ["CB_EXACT"] = "1"
    B = CB.Bench(n_clip=nc, n_ws=nw); M = Frozen(B, P2); r = M.run()
    out["frozen"] = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    sp_ = importlib.util.spec_from_file_location("minarc_mech_for_sidecar", os.path.join(REPO, "docs", "concepts", "verify", "minarc-stop-knuckle-4r-mechanism.py"))
    MECH = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(MECH)
    t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


def viz_export(par):
    """geometry of the fitted design (Bench(60,160)) for docs/concepts/viz/concepts/sidecar-longdyad-knuckle-3r.js (the
    lead's exporter on this model's report; rodA = crank-tip ball, rodB = horn ball at rest, horn = link 1a lug)"""
    FL._report = _report
    out = FL.viz_export(par)
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
                              ovh=a.get("overhead140"), parts=out.get("parts_ib14"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), min_metal=r.get("min_metal_mm"), reach=r["reach"],
                          inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"), why=r.get("why"), ovh=r.get("overhead140"),
                          drive=r.get("drive"), parts=r.get("parts_ib14"), clear=getattr(M, "last_clear", None), secs=round(time.time() - t)), default=float))
