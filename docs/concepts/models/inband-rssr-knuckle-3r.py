"""inband-rssr-knuckle-3r (2026-10-17): longstroke-slipper-knuckle-3r's phased RSSR K drive (bell crank on link 1b beside
hub 2, O3 Ti rod, two M2 ball links, horn lug of link 1a at hub K) REPACKAGED so its metal lies in the 2-14 mm band
instead of over it, on the steep lobe law (kK ~2.7-3.0) that the long K dyad needs (docs/research/inband_drive.md).

The chain, the K dyad, the hub-2 lobe law and its gates, the RSSR closure per pose (continuation), the transmission gate
(>= 48 deg = PA <= 42 at both ball ends), the drive-range truncation on every bench, the part pairs and the frozen claim
protocol are the long-stroke row's (docs/concepts/models/longstroke-slipper-knuckle-3r.py, loaded unchanged with
LS_DRIVE=rssr). What this row changes is WHERE the drive's metal sits (every switch at its default reproduces the
long-stroke row's geometry exactly - the control):

  * eta (deg, default 0): the crank pivot's azimuth about hub 2's axis, measured from link 1b's direction toward hub K. The
    pivot stays 16 mm (HUB_R + 6) from hub 2's axis, so the short arm still reaches the hub-2 rim lobe and stage 1 (the
    lobe law, its pressure angle and crest) is unchanged; |eta| ~40+ puts the O10 crank boss off link 1b's strap.
  * clay (0 | 1, default 0): 0 = the crank boss stacked ON link 1b (its underside at link 1b's top + 0.15, the parent);
    1 = the crank on an EAR of link 1b: a 3 mm tab from link 1b's hub-2 eye to the pivot, joggled one layer down (its top
    = the crank's underside - 0.15), so the crank boss and arm lie at link 1b's own layer (+ zc >= 0) beside the strap.
    The ear is link 1b metal (member 7), sampled like every part (underside in the band, top as contact-only), and the
    arm still climbs one layer wherever its swing passes over link 1b's strap (the parent's planform rule).
  * bl_c / bl_h (0 | 1, default 0): the M2 ball link's ball ABOVE (0, the parent) or BELOW (1) the crank arm tip / the horn
    lug: a ball below puts the rod 6 mm lower at that end (stud pointing to the skin; its socket's lower ring sampled).
  * the catalogue parts are unchanged: O3 Ti rod, M2 ball links (socket O7, ball centre 3 mm off the arm face), crank on
    an MR63ZZ pair (boss O10 x 6), 3 mm Ti links.
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, no gears / pulleys / cables.

IB_GHOST (attribution only, never a claim): a comma list of drive parts whose metal is deleted (crank, rod, rodends,
horn, ear; or 'all'); the kinematics, law, range and truncation are kept.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/inband-rssr-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]          (the long-stroke row's frozen protocol)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

os.environ["LS_DRIVE"] = "rssr"                               # this row is the RSSR drive only
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("longstroke_for_inband", os.path.join(HERE, "longstroke-slipper-knuckle-3r.py"))
LS = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(LS)
SC, FL, PK, S, RL, BM = LS.SC, LS.FL, LS.PK, LS.S, LS.RL, LS.BM
SCBase = LS.SCBase
unit = S.unit; D2R = math.pi / 180
ID = "inband-rssr-knuckle-3r"
DRIVE = "rssr"
REPORT_KEYS = LS.REPORT_KEYS
DRIVE_LABELS = {}                                            # id(contact array) -> [(part, n), ...] (attribution)
GHOST = [g for g in os.environ.get("IB_GHOST", "").split(",") if g]
if GHOST == ["all"]: GHOST = ["crank", "rod", "rodends", "horn", "ear"]
IB_DEFAULTS = dict(eta=0.0, clay=0, zc=0.0, bl_c=0, bl_h=0)
STUD = 3.5                                                   # M2 ball stud: ball centre beyond the end face it screws into (mm)
CONE = 30.0                                                  # M2 ball link: socket tilt off its stud's normal plane (deg)
PARAMS = dict(LS.PARAMS, **IB_DEFAULTS)
_ls_clamp = LS._clamp


def _clamp(p):
    p = _ls_clamp(p)
    p["eta"] = min(max(float(p.get("eta", 0.0)), -120.0), 120.0)
    p["clay"] = 1 if float(p.get("clay", 0)) >= 0.5 else 0
    p["zc"] = min(max(float(p.get("zc", 0.0)), 0.0), 3.15)
    for k in ("bl_c", "bl_h"): p[k] = int(min(max(round(float(p.get(k, 0))), 0), 2))
    return p


def _ring(c, r, axv, n=16): return SC._ring(c, r, axv, n)


class IBModel(LS.LSModel):
    def _rod_metal(self):
        SC.TRANS_MIN = LS.TRANS_MIN_RSSR
        self._ib_rod_metal()
        if GHOST: self._ib_ghost(GHOST)

    def _ib_ghost(self, parts):
        """ATTRIBUTION ONLY: the named drive parts' metal deleted (rigid, contact-only, part-pair straps)"""
        for k_ in parts: self.rigid.pop(k_, None)
        keep = []
        for m, X in self.contact:
            lab = DRIVE_LABELS.get(id(X))
            if lab is None: keep.append((m, X)); continue
            k0 = 0; sel = []
            for nm, n in lab:
                if nm not in parts: sel.append(np.arange(k0, k0 + n))
                k0 += n
            if sel:
                Y = X[np.concatenate(sel)]; DRIVE_LABELS[id(Y)] = [(nm, n) for nm, n in lab if nm not in parts]; keep.append((m, Y))
        self.contact = keep
        smap = {"crank": "CRK", "horn": "HORN", "ear": "EAR"}
        for k_ in parts:
            if k_ in smap: self.strap.pop(smap[k_], None)
        if "rod" in parts and "rodends" in parts: self.strap.pop("ROD", None)
        if "CRK" not in self.strap: self.strap.pop("ROD", None); self.strap.pop("HORN", None)   # the parent's collide needs CRK
        self._sc_info["ghost"] = list(parts)

    def _ib_rod_metal(self):
        """SCBase._rod_metal (sidecar-longdyad-knuckle-3r) with the pivot azimuth eta, the crank layer clay / zc and the
        per-end ball sides bl_c / bl_h; at eta 0, clay 0, bl_c = bl_h = 0 it is the parent line for line"""
        D = self.D; P = D.p; u2, uK = D.u[1], D.uK; fK, f2 = self.fK, self.f[1]
        L1b = self.link_pts["L1b"][1]
        g0 = (S.HUB_R + 5.0 + 1.0) / max(f2, 30.0); ax = unit(np.cross(u2, uK)); dR0 = unit(S.rotm(ax, g0)[0] @ u2)
        eta = float(P.get("eta", 0.0)); dR = unit(S.rotm(u2, eta * D2R)[0] @ dR0) if abs(eta) > 1e-9 else dR0
        near = L1b[np.argsort(np.linalg.norm(unit(L1b) - dR, axis=1))[:6]]; lev = float(np.linalg.norm(near, axis=1).max())
        tK0 = unit(dR - (dR @ uK) * uK); sK = unit(S.rotm(uK, float(P["beta"]) * D2R)[0] @ tK0); sR = unit(sK - (sK @ dR) * dR)
        sR = unit(S.rotm(dR, float(P.get("gam", 0.0)) * D2R)[0] @ sR)
        bnR = unit(np.cross(dR, sR)); La, RH = float(P["La"]), float(P["r_h"])
        clay = int(P.get("clay", 0)); zstack = lev + S.T_LINK + SC.RUNG
        zboss = zstack if clay == 0 else lev + float(P.get("zc", 0.0))     # crank underside: stacked on link 1b | on the ear
        PV = dR * zboss
        L1d = unit(L1b); w_ok = S.W_LINK / 2 + 1.0
        rs = np.arange(0.0, La + 1e-6, 2.0); ws_ = np.array([-3.0, -1.0, 1.0, 3.0])
        L_ = D.law(); dKmax = math.radians(float(L_.get("dK_max", 0.0)) + 2.0) if L_.get("ok") else 0.2
        sp = float(np.sign(D.psiA)) or 1.0
        mc, mh = int(P.get("bl_c", 0)), int(P.get("bl_h", 0))
        if P.get("ball_low"): mc = mh = 1
        zc_s = -1.0 if mc == 1 else 1.0; zh_s = -1.0 if mh == 1 else 1.0
        lvK = fK + float(P["hl"])
        # ball centre: 0 = on a stud above the lug / arm (+T_LINK + ZB), 1 = below (-ZB), 2 = on a RADIAL stud screwed into the
        # lug's / arm's end face (ball centre in its mid-plane, STUD mm beyond the end face; the M2 ball link's socket axis is
        # then the stud's, so the rod's tilt off the plane normal to the stud is the socket's cone, gated at CONE)
        H0 = uK * (lvK + S.T_LINK / 2) + RH * sK if mh == 2 else uK * (lvK + (S.T_LINK + SC.ZB if zh_s > 0 else -SC.ZB)) + RH * sK
        k = math.tan(S.RAMP * D2R)
        lvl_clear = (lev + float(P["zr"])) if clay == 0 else zboss

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
                if clay == 0: lvl[j] = lvl_clear if clear else zboss
                else: lvl[j] = zboss if (clear or r_ <= 5.0) else max(zboss, zstack)
            return np.max(lvl[None, :] - k * np.abs(rs[:, None] - rs[None, :]), axis=1)

        def tip_of(lvl):
            if mc == 2: return dR * (lvl[-1] + S.T_LINK / 2) + La * sR
            return dR * (lvl[-1] + (S.T_LINK + SC.ZB if zc_s > 0 else -SC.ZB)) + La * sR

        def phi_end(tip0):
            Lr = float(np.linalg.norm(H0 - tip0)); pg_ = np.radians(np.arange(-100.0, 100.0 + 1e-6, 0.1))
            TP = np.einsum("nij,j->ni", S.rotm(dR, pg_), tip0 - PV) + PV; H = S.rotm(uK, sp * dKmax)[0].T @ H0
            fv = np.linalg.norm(TP - H, axis=1) - Lr; sgn = np.nonzero(np.diff(np.sign(fv)) != 0)[0]
            return float(pg_[sgn][np.argmin(np.abs(pg_[sgn] - (RH * dKmax / La)))]) if len(sgn) else RH * dKmax / La
        lvl = np.full(len(rs), zboss); pe = phi_end(tip_of(lvl)); pe = phi_end(tip_of(arm_levels(np.linspace(0, pe, 7))))
        lvl = arm_levels(np.linspace(0, pe * 1.05, 9))
        arm = np.array([dR * lvl[j] + r_ * sR + w_ * bnR for j, r_ in enumerate(rs) for w_ in ws_ if mc != 2 or r_ <= La - STUD + 1e-6])
        e, f = S.frame_of(dR); dd = S.disc(5.0, 2.0)
        boss = PV + dd[:, :1] * e + dd[:, 1:] * f
        tip0 = tip_of(lvl)
        bnK = unit(np.cross(uK, sK))
        hend = RH - STUD if mh == 2 else RH + 4.0
        horn = np.array([uK * lvK + r_ * sK + w_ * bnK for r_ in np.arange(S.HUB_R + 0.5, hend + 1e-6, 2.0) for w_ in (-3.0, -1.0, 1.0, 3.0)])
        tilt = np.zeros((len(np.radians(np.arange(0.0, max(math.degrees(dKmax), 5.0) + 1e-6, 0.25))), 2))
        Lrod = float(np.linalg.norm(H0 - tip0))
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
            vt = unit(np.cross(dR, tp - PV)); vh = unit(np.cross(uK, H))
            trans[j] = 90.0 - max(math.degrees(math.acos(min(1, abs(float(rod @ vt))))), math.degrees(math.acos(min(1, abs(float(rod @ vh))))))
            axc = S.rotm(dR, ph)[0] @ sR if mc == 2 else dR; axh = S.rotm(uK, sp * kk)[0].T @ sK if mh == 2 else uK
            tilt[j] = [math.degrees(math.asin(min(1, abs(float(rod @ axc))))), math.degrees(math.asin(min(1, abs(float(rod @ axh)))))]
        ratio = np.gradient(phig, kgrid) if len(kgrid) > 2 else np.ones(len(kgrid))
        self._scg = dict(PV=PV, dR=dR, tip0=tip0, H0=H0, uK=uK, sp=sp, kgrid=kgrid, phig=phig); self._sc = None
        dKp = np.abs(np.asarray(self.dK, float)); dKsave = self.dK
        self.rigid["crank"] = (9, np.concatenate([boss, arm]))
        self.rigid["horn"] = (1, horn)
        nr = max(3, int(Lrod / S.SPACING)); sg = np.linspace(0, 1, nr)[:, None]
        rodc = tip0[None] * (1 - sg) + H0[None] * sg
        self.rigid["rod"] = (8, rodc - 1.5 * unit(rodc))
        # ball-link sockets (O7 rings): the lower ring of each end is skin-facing metal, the upper ring contact-only
        def ends(c, ax_, s_):
            return (_ring(c - SC.ZB * ax_, SC.ER, ax_), _ring(c + 3.5 * ax_, SC.ER, ax_)) if s_ > 0 else \
                   (_ring(c - 3.5 * ax_, SC.ER, ax_), _ring(c + SC.ZB * ax_, SC.ER, ax_))
        def ends_radial(c, st_, up_):
            # socket body O7 x 7 on a radial stud: rings about the stud axis at the ball centre and +-3 along it; its
            # skin-facing half (below the mid-plane) is metal in the band, the rest contact-only
            R3 = [_ring(c + o * st_, SC.ER, st_) for o in (-3.0, 0.0, 3.0)]; A = np.concatenate(R3); lo = (A - c) @ up_ <= 0.01
            return A[lo], A[~lo]
        bC, tC = ends_radial(tip0, sR, dR) if mc == 2 else ends(tip0, dR, zc_s)
        bH, tH = ends_radial(H0, sK, uK) if mh == 2 else ends(H0, uK, zh_s)
        endsB = np.concatenate([bC, bH]); endsT = np.concatenate([tC, tH])
        self.rigid["rodends"] = (8, endsB)
        self.rigid.pop("rocker", None)
        # the ear (clay 1): link 1b metal from its hub-2 eye (r >= HUB_R from hub 2's axis) to around the pivot, one layer down
        ear = np.zeros((0, 3))
        if clay == 1:
            zear = zboss - SC.RUNG - S.T_LINK                       # ear underside
            c2 = u2 * zear; v = unit(dR * zear - c2); v = unit(v - (v @ dR) * dR); bv = unit(np.cross(dR, v))
            pts = [dR * zear + x * e + y * f for x, y in S.disc(6.0, 2.0)]
            dist2 = np.linalg.norm(np.cross(dR * zear - c2, u2))     # pivot's distance from hub 2's axis (~16 mm)
            for s_ in np.arange(0.0, dist2 + 1e-6, 2.0):
                for w_ in (-4.0, -2.0, 0.0, 2.0, 4.0):
                    pts.append(dR * zear - s_ * v + w_ * bv)
            ear = np.array(pts)
            w = ear - (ear @ u2)[:, None] * u2; ear = ear[np.linalg.norm(w, axis=1) >= S.HUB_R + 0.5]
            self.rigid["ear"] = (7, ear)
        self._contact_only(); self._solids()
        cyl = np.concatenate([_ring(dR * z, 5.0, dR) for z in np.linspace(zboss, zboss + SC.BOSS_H, 4)])
        rodtop = rodc + 1.5 * unit(rodc)
        c8 = np.concatenate([endsB, endsT, rodtop]); DRIVE_LABELS[id(c8)] = [("rodends", len(endsB) + len(endsT)), ("rod", len(rodtop))]
        c9 = np.concatenate([cyl, arm + S.T_LINK * dR]); DRIVE_LABELS[id(c9)] = [("crank", len(c9))]
        c1 = horn + S.T_LINK * uK; DRIVE_LABELS[id(c1)] = [("horn", len(c1))]
        self.contact.append((8, c8)); self.contact.append((9, c9)); self.contact.append((1, c1))
        if len(ear):
            c7 = ear + S.T_LINK * dR; DRIVE_LABELS[id(c7)] = [("ear", len(c7))]; self.contact.append((7, c7))
        self.strap["ROD"] = (8, np.concatenate([endsB, endsT, rodc]))
        self.strap["CRK"] = (9, np.concatenate([cyl, arm + 1.5 * dR]))
        self.strap["HORN"] = (1, horn + 1.5 * uK)
        if len(ear): self.strap["EAR"] = (7, ear + 1.5 * dR)
        self._crown_ok = True
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
            bad = {"transmission": trans[j] < SC.TRANS_MIN, "ROD-hub2": dh2 < 1.0, "ROD-L1b": dl1b < 1.0, "CRK-hub2": dc2 < 1.0,
                   "cone": (mc == 2 and tilt[j, 0] > CONE) or (mh == 2 and tilt[j, 1] > CONE)}
            if len(ear):                                         # the rod and its sockets keep 1 mm off the ear (same body as link 1b)
                bad["ROD-ear"] = float(cKDTree(ear).query(XR)[0].min()) - S.T_LINK / 2 < 1.0
            if any(bad.values()):
                lim = float(kgrid[max(j - 1, 0)]); why_lim = [k_ for k_, v in bad.items() if v][0]; break
        self.dK = dKsave; self._sc = None
        self._scg.update(dK_lim=lim, why_lim=why_lim)
        self._viz_rod = dict(rocker=PV, rockerAx=dR, rodA=tip0, rodB=H0, armA=PV, armB=tip0 - (S.T_LINK + SC.ZB) * dR * zc_s)
        taken = (np.asarray(self.kin_ok, bool)) & (dKp > 1e-9)
        kmax_t = float(dKp[taken].max()) if taken.any() else 0.0
        jt = int(np.searchsorted(kgrid, kmax_t)) + 1
        self._sc_info = dict(boss_level=round(zboss, 1), lev_L1b=round(lev, 1), arm_tip_level=round(float(lvl[-1]), 1), rod_len=round(Lrod, 1),
                             La=round(La, 1), r_h=round(RH, 1), i_rock=round(float(P["i_rock"]), 2), rssr_closed=bool(okc),
                             trans_min_taken=round(float(trans[:jt].min()), 1), ratio_range=[round(float(ratio[:jt].min()), 3), round(float(ratio[:jt].max()), 3)],
                             ratio_small_angle=round(RH / La, 3), phi_max_taken=round(math.degrees(float(np.interp(kmax_t, kgrid, phig))), 1),
                             crest_exact=round(float(P["r_lobe"]) + float(P["s_arm"]) * abs(float(np.interp(kmax_t, kgrid, phig))), 2),
                             dK_lim=round(math.degrees(lim), 1), why_lim=why_lim, eta=round(eta, 2), clay=clay, bl_c=int(zc_s < 0), bl_h=int(zh_s < 0),
                             ear_pts=int(len(ear)), pivot_off_hub2_mm=round(float(np.linalg.norm(np.cross(PV, u2))), 2),
                             tilt_max_taken=[round(float(tilt[:jt, 0].max()), 1), round(float(tilt[:jt, 1].max()), 1)],
                             tilt_max_range=[round(float(tilt[:max(int(np.searchsorted(kgrid, lim)) + 1, 1), 0].max()), 1),
                                             round(float(tilt[:max(int(np.searchsorted(kgrid, lim)) + 1, 1), 1].max()), 1)])
        self._rod_info = self._sc_info

    def collide(self, i):
        out = super().collide(i)
        if "EAR" not in self.strap: return out
        h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        EA = tf(*self.strap["EAR"]); c = {}
        # the crank's arm over its own ear (and over link 1b's strap) is a stacked running fit, as in the parent: not a pair
        if "ROD" in self.strap: c["ROD-EAR"] = float(cKDTree(EA).query(tf(*self.strap["ROD"]))[0].min()) - 2 * h
        st = {k_: tf(m, X) for k_, (m, X) in self.strap.items() if k_ in ("L1a", "L2")}
        for k_, X in st.items(): c[f"EAR-{k_}"] = float(cKDTree(X).query(EA)[0].min()) - 2 * h
        cyl = {}
        for k_, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k_] = (R @ cen + t, R @ ax)
        for hb in ("hub1", "hubK", "hub3"): c[f"EAR-{hb}"] = float(self.sd_cyl(EA, *cyl[hb], r=self.cyl_r[hb]).min()) - h
        bx = self._boxes_at_final(i)
        for nm in ("knee", "pad"):
            cen, R, half = bx[nm]; c[f"{nm}-EAR"] = float(self.sd_box(EA, cen, R, half).min()) - h
        if c: self.last_clear.update({k_: round(v, 1) for k_, v in c.items()}); out = min(out, min(c.values()))
        return out


# route every parent hook through this row's model class and clamp
LS.LSModel = IBModel; LS._clamp = _clamp; LS.PARAMS = PARAMS
SC.SCModel = IBModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; LS.RF.PARAMS = PARAMS; BM.PARAMS = PARAMS
FL.G.KR.KB.KModel = IBModel; FL.FLModel_SC = IBModel
_report = LS._report; gate = LS.gate; _frozen_model = LS._frozen_model; th_margin = LS.th_margin
frozen = LS.frozen; frozen_held = LS.frozen_held; frozen_flood = LS.frozen_flood; viz_export = LS.viz_export
KK_MIN = float(os.environ.get("LS_KK_MIN", "0")); STROKE_MIN = float(os.environ.get("LS_STROKE_MIN", "0")); OBJ = os.environ.get("LS_OBJ", "near2")


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    if STROKE_MIN > 0 and float((r.get("cam") or {}).get("dK_lim") or 0.0) < STROKE_MIN: r["honest"] = False; r["stroke_short"] = True
    if OBJ == "near1" and r.get("gap_near1") is not None: r["gap"] = r["gap_near1"]
    info = getattr(M, "_sc_info", None) or {}
    r.setdefault("cam", {}).update({k: info.get(k) for k in ("eta", "clay", "bl_c", "bl_h", "boss_level", "lev_L1b", "arm_tip_level", "pivot_off_hub2_mm", "tilt_max_taken", "tilt_max_range")})
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); r["drive_kind"] = DRIVE
    info = getattr(M, "_sc_info", None) or {}
    r.setdefault("cam", {}).update({k: info.get(k) for k in ("eta", "clay", "bl_c", "bl_h", "boss_level", "lev_L1b", "arm_tip_level", "tilt_max_taken", "tilt_max_range", "trans_min_taken")})
    return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "claims":
        import subprocess
        od = sys.argv[3] if len(sys.argv) > 3 else "ib_out"; os.makedirs(od, exist_ok=True); procs = []
        for c in par:
            env = dict(os.environ, CB_EXACT="1", OMP_NUM_THREADS="1", IGL_NUM_THREADS="1", CB_QUIET_EXACT="1")
            for k_, v_ in (c.get("env") or {}).items(): env[k_] = str(v_)
            lg = open(os.path.join(od, c["tag"] + ".log"), "w")
            if c.get("mode") == "attr":
                cmd = [sys.executable, os.path.join(REPO, "docs", "research", "inband_drive", "attribute.py"), json.dumps(c.get("params", {})),
                       c.get("which", "bench"), os.path.join(od, c["tag"] + ".json"), os.path.abspath(__file__)]
            else:
                cmd = [sys.executable, os.path.abspath(__file__), c.get("mode", "frozen"), json.dumps(c.get("params", {})), os.path.join(od, c["tag"] + ".json")]
            procs.append(subprocess.Popen(cmd, env=env, stdout=lg, stderr=subprocess.STDOUT))
        for pr in procs: pr.wait()
        print("claims done", [pr.returncode for pr in procs]); sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "gate":
        t = time.time(); out = gate(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["row"] = ID; out["ghost"] = GHOST; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(row=ID, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), cam=out.get("cam"),
                              depth={k: v for k, v in (out.get("contact_depth") or {}).items() if k != "per_pose"}, th_margin=out.get("th_margin"),
                              parts=out.get("parts_ib14"), connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    info = getattr(M, "_sc_info", None) or {}
    print(json.dumps(dict(row=ID, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"), why=r.get("why"),
                          ovh=r.get("overhead140"), cam=r.get("cam"), sc=info, parts=r.get("parts_ib14"), clear=getattr(M, "last_clear", None),
                          secs=round(time.time() - t)), default=float))
