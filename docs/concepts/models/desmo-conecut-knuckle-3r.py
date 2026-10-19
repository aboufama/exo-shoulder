"""desmo-conecut-knuckle-3r (round 13, the main track's knuckle lens): desmo-slipper's spring-free, roller-free K drive on
conecut-knee-knuckle-3r's knee and J3 dowel stop, with stage 2 INVERTED (cell B, the claim cell).

At rest the chain is conecut's (the verified lead's seats, dyad 26 / 38.03, law kK 2.1534, drive g / beta / r_c of the
lead): J1 -> link 1a -> K (plain O20, no clock spring, slaved, never read) -> link 1b -> J2 -> link 2 -> J3 (hard stop on
its own angle q3' in [J3MIN, J3MAX], 2 mm 440C dowel) -> member 3 -> E strap lE -> knee pin a -> knee link lc -> pin b ->
arm pad on BOTTOM. The K drive: a bell crank on link 1b (MR63ZZ pair on a 3 mm 440C pin), stage 1 = a crowned O1.5 440C
pin on the crank's short arm (a_s, psi) in a 1.52 x 1.5 groove under link 2's cap ring (desmo-slipper's, exact 3-D,
loaded and copied unchanged), stage 2 =

  * cell A (stage2 "A", the measured control): desmo-slipper's stage 2 unchanged (the lead's slipper nose O2.5 on the
    crank's tip in a two-walled slot = the lead's flank lug band + desmo's outer wall on link 1a);
  * cell B (stage2 "B", default): the nose is an ISO 8734 2 m6 440C dowel (nose_r2 1.0) pressed radially into an O(2 boss_r)
    x 3 Ti boss on LINK 1a at the lead's contact seat C0 (= the roller centre of the lead's synthesis, beta / r_c), the
    boss rooted to hub K's rim; the two-walled slot (width 2 (nose_r2 + c_slot2), wall2 each side) is wire-EDM'd in a Ti
    tip plate on the crank's long arm, at the arm-tip layer (underside R0 + 1.5 + 0.15). The slot's closed end is stop A.
    The parent's flank lug band, desmo's outer wall and the crank-borne nose are DELETED (metal and gates); the parent's
    flank-only gates (flank PA, liftoff, cusp, contact-off-lug, roller vs hub K) are replaced by:
      - the inverted cam per 0.25 deg of K: nose path X = Rk^T C0 (link 1b frame), relative velocity vs the crank point
        at X, wall normal n = X^ x v_rel; pressure angles at the nose centre (the contact force passes through it) on
        link 1a (pah) and on the crank (pac) <= 43 - atan(mu)  ('wall2B-pa');
      - the BUILT pocket = the union of nose discs (nose_r2 + c_slot2) along the 0.02-deg path in the crank frame; slop
        with the crank held (K bisected to 0.005 deg, both signs, K0 every 0.5 deg incl. the closed end, the relative pole)
        <= 0.25 deg ('slot-slop'), and the contact normal at engagement -> the pocket's pressure angles on both members,
        gated <= 43 - atan(mu) for K0 >= 0.5 ('pocket-pa'); K0 = 0 (stop A) is reported;
      - boss vs hub K's O20: rK(C0) - boss_r >= 11 ('boss-hubK', placement gate);
      - clearances per K step: tip plate vs hub K and hub 2 >= 1.0 ('PLATE-hubK' / 'PLATE-hub2'); the crank's low arm vs
        the boss + root >= 1.0 ('CRK-BOSS', and per pose through the parent's collide()).
    Metal (sampled like the baseline): boss underside disc + root strip (link 1a, rigid 'horn'), its top and edges
    (contact); the tip plate's two walls (one mid row each, every ~2 mm, rigid 'plate' on the crank) + slot edges, outer
    edges, end caps and the top (contact). The plate is crank body 9 on the strap / part checks ('ROD').
  * cell C: cell B with g 2.6-2.8 (the stage-1 ratio moved into stage 2); the nose seat re-placed with beta / r_c (param g;
    NOT screened in round 13's time box).
  Stage 1 (cell B) is read on the BUILT blended groove (s1_read "built", default): the forward / pin-side pressure angle is
  gated wherever the pin moves, the cap side outside the blend (inside it the cap side is the dwell lock, reported) - the
  planner's gate (a), a measurement change against desmo-slipper's linear read (s1_read "linear" restores it).

3 ACTIVE DOF (J1, J2, J3 encoded); K slaved, never read; crank pivot, both higher pairs and the knee pins are passive
rotations / higher pairs (no translation). 0 passive translations, no springs, no gears / pulleys / cables (MVP1).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/desmo-conecut-knuckle-3r.py [check] ['<json>']   ('"best"' = BEST)
    CB_EXACT=1 ... frozen|held|flood|redteam '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("desmo_for_desmoconecut", os.path.join(HERE, "desmo-slipper-knuckle-3r.py"))
DS = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(DS)
SN, SC, FL, RF, BM, PK, S, RL = DS.SN, DS.SC, DS.FL, DS.RF, DS.BM, DS.PK, DS.S, DS.RL
unit, _fold, _angv, _rot = DS.unit, DS._fold, DS._angv, DS._rot
R_LO, R_HI, DRIFT_MAX, GROOVE_W, RING_WALL, BORE_R, PIN_D, ARM_W = DS.R_LO, DS.R_HI, DS.DRIFT_MAX, DS.GROOVE_W, DS.RING_WALL, DS.BORE_R, DS.PIN_D, DS.ARM_W
C_GROOVE, SLOP_MAX, RC_MIN, RUNG = DS.C_GROOVE, DS.SLOP_MAX, DS.RC_MIN, RF.RUNG
ID = "desmo-conecut-knuckle-3r"
_DSBase = DS.DSModel

# conecut-knee-knuckle-3r's verified best_params (rows/conecut-knee-knuckle-3r.json: knee re-cut, MR63ZZ stk 6.0, J3 dowel)
CC_P = {"stk": 6.0, "lE": 97.1443, "lc": 24.3508, "phiE": 0.7526, "phib": -91.8041, "J3MIN": -111.9036, "J3MAX": 122.7417, "ang_min": 25.2189}
# desmo-slipper's verified stage-1 placement (a_s 9.5 / psi 150) + this file's stage-2 cell B hardware
DC = dict(a_s=9.5, psi=150.0, glev=-0.5, blend=10.0, nose_r=1.25, mu=0.087, stage2="B", nose_r2=1.0, c_slot2=0.01, wall2=1.0, boss_r=2.75,
          kslot=46.5, s2_gate=1, s1_read="built")
PARAMS = dict(DS.PARAMS); PARAMS.update(CC_P); PARAMS.update(DC)
# the claim config (sweep k57, pre-registered; frozen exact Bench(110,360) 19.04, held 23.24 at mu 0.15). The defaults above are the
# spec's base (the sweep rows' params are overrides of these defaults); the stock seat r_c 15.37 fails the plate gate (0.12 mm to hub K)
BEST = {"r_c": 16.176, "beta": -177.169, "nose_r2": 0.75, "wall2": 0.9, "boss_r": 2.5, "glev": -1.0, "blend": 10.0, "kslot": 46.5,
        "a_s": 9.529, "psi": 149.71, "mu": 0.15}


def wr(a): return (a + 180.0) % 360.0 - 180.0


def _c(v, lo, hi): return min(max(float(v), lo), hi)


_dsclamp = DS._clamp


def _clamp(p):
    j3min, j3max, bl = p.get("J3MIN", -111.9036), p.get("J3MAX", 122.7417), p.get("blend")
    q = _dsclamp(p)
    q["J3MIN"] = min(max(float(j3min), -180.0), -60.0); q["J3MAX"] = float(j3max)
    q["ang_min"] = max(float(q.get("ang_min", 25.2189)), 25.2189)
    q["lE"] = _c(q["lE"], 40.0, 110.0); q["lc"] = _c(q["lc"], 15.0, 45.0)
    if bl is not None: q["blend"] = _c(bl, 0.0, 30.0)
    q["stage2"] = "A" if str(q.get("stage2", "B")).upper().startswith("A") else "B"
    q["nose_r2"] = _c(q.get("nose_r2", 1.0), 0.75, 1.5); q["c_slot2"] = _c(q.get("c_slot2", 0.01), 0.005, 0.05)
    q["wall2"] = _c(q.get("wall2", 1.0), 0.8, 1.5); q["boss_r"] = _c(q.get("boss_r", 2.75), 2.5, 3.0)
    q["kslot"] = _c(q.get("kslot", 46.5), 30.0, 70.0)
    q["s1_read"] = "linear" if str(q.get("s1_read", "built")) == "linear" else "built"
    return q


_SLOPB_CACHE = {}


class DCModel(_DSBase):
    def __init__(self, B, params=None, verbose=False):
        super().__init__(B, params, verbose)
        P = self.p; lo = float(P.get("J3MIN", -111.9)); hi = float(P.get("J3MAX", 999.0))
        if hasattr(self, "K") and "phi" in self.K:                # conecut's J3 dowel stop on q3' = q3 + knee phi (J3's own angle)
            q3p = wr(np.degrees(self.q[:, 2] + self.K["phi"]))
            bad = self.kin_ok & ((q3p < lo) | ((q3p > hi) if hi < 180 else False))
            self.why[bad] = "j3stop"; self.kin_ok = self.kin_ok & ~bad; self.q3p = q3p

    def _cellB(self): return (not DS.CONTROL) and str(self.D.p.get("stage2", "B")) == "B"

    def _rod_metal(self):
        if not self._cellB():
            self._s2B = None; return super()._rod_metal()
        P = self.D.p; mu = float(P.get("mu", 0.087)); nr2 = float(P["nose_r2"])
        # the parent's synthesis (arm, crank boss, K grid, clearances) with its FLANK-only gates inert: the flank, its lug band
        # and the crank-borne nose are deleted below and replaced by the inverted slot's own gates
        sv = (RF.PA_MAX, RF.RHO_MIN, RF.R_CMIN, RF.ROLL_R)
        RF.ROLL_R = nr2; RF.PA_MAX, RF.RHO_MIN, RF.R_CMIN = 1e9, -1e9, -1e9
        try: RF.RFModel._rod_metal(self)
        finally: RF.PA_MAX, RF.RHO_MIN, RF.R_CMIN, RF.ROLL_R = sv
        g = self._scg; T = self._cam_table; kgrid = g["kgrid"]; nk = len(kgrid)
        bad = {"CRK-hubK": T["clear_hubK"] < 1.0, "CRK-hub2": T["clear_hub2"] < 1.0}
        bany = bad["CRK-hubK"] | bad["CRK-hub2"]
        if bany.any():
            j = int(np.argmax(bany)); lim0 = float(kgrid[max(j - 1, 0)]); why0 = [k for k, v in bad.items() if v[j]][0]
        else:
            lim0, why0 = float(kgrid[-1]), "law"
        info = self._sc_info
        info.update(nose_r=nr2, mu=mu, friction_deg=round(math.degrees(math.atan(mu)), 2), pa_kin_max=round(43.0 - math.degrees(math.atan(mu)), 2),
                    flank_deleted=True, dK_lim_parent_flank=info.get("dK_lim"), why_lim_parent_flank=info.get("why_lim"))
        for k in ("pa_crank_max_taken", "pa_horn_max_taken", "flank_rho_min", "clear_roll_hubK_min", "clear_lowarm_lug_min", "lug_r_max", "pa_crank_rest", "pa_horn_rest"):
            info.pop(k, None)
        # ---- delete the flank metal: crank-borne nose, the lug band (link 1a), their contact / strap entries
        C0 = np.asarray(self._viz_rod["roller"], float); R0 = float(np.linalg.norm(C0)); cr = unit(C0)
        self.rigid.pop("roller", None)
        assert self.contact[-1][0] == 1 and self.contact[-2][0] == 9, "parent contact layout changed"
        X9 = self.contact[-2][1]; d_ = X9 - C0; al = d_ @ cr; pe = np.linalg.norm(d_ - np.outer(al, cr), axis=1)
        X9 = X9[~((np.abs(al) <= 1.26) & (pe <= nr2 + 0.02))]                     # drop the nose rings, keep crank boss + arm top
        self.contact = self.contact[:-2] + [(9, X9)]
        # ---- link 1a's boss (O 2 boss_r x 3, underside on the lug sphere rL) + root strip from hub K's rim
        uK = g["uK"]; rL = R0 - 1.5; rb = float(P["boss_r"]); lvK = float(self.fK) + float(P["hl"])
        e1, f1 = S.frame_of(cr); dd = S.disc(rb, 1.0)
        bossT = C0 + dd[:, :1] * e1 + dd[:, 1:] * f1; boss = unit(bossT) * rL
        rim = np.array([C0 + rb * (math.cos(a) * e1 + math.sin(a) * f1) for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)])
        rim = unit(rim) * rL
        db = unit(C0 - (C0 @ uK) * uK); wb = unit(np.cross(uK, db)); rK0 = float(np.linalg.norm(C0 - (C0 @ uK) * uK))
        root = []
        for r_ in np.arange(S.HUB_R + 0.5, rK0 - rb + 1e-6, 2.0):
            for w_ in np.arange(-(rb - 0.5), rb - 0.5 + 1e-6, 2.0):
                x_ = uK * lvK + r_ * db + w_ * wb; t_ = (r_ - S.HUB_R) / max(rK0 - S.HUB_R, 1e-6)
                root.append(unit(x_) * ((1 - t_) * float(np.linalg.norm(x_)) + t_ * rL))
        root = np.array(root) if root else np.zeros((0, 3))
        bossU = np.concatenate([boss, root]); bossM = bossU + 1.5 * unit(bossU)
        self.rigid["horn"] = (1, bossU)
        self.contact.append((1, np.concatenate([rim, rim + 3.0 * unit(rim), bossU + S.T_LINK * unit(bossU)])))
        self.strap["HORN"] = (1, np.concatenate([bossM, rim + 1.5 * unit(rim)]))
        g["lugM"] = bossM
        g.update(dK_lim=lim0, why_lim=why0)
        self._viz_rod["lugPts"] = [unit(uK * lvK + (S.HUB_R + 0.5) * db) * (np.linalg.norm(uK * lvK + (S.HUB_R + 0.5) * db) + 1.5), C0]
        self._s2B = dict(C0=C0, R0=R0, rL=rL, rb=rb, rK0=rK0, lim0=lim0, why0=why0)
        self._desmo_build_B()

    def _desmo_build_B(self):
        """copy of DS.DSModel._desmo_build (desmo-slipper, verified) with stage 2 replaced by the inverted slot (cell B)"""
        D = self.D; P = D.p; g = self._scg; info = self._sc_info
        PV, dR, uK, sp, sig, gg, cc = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0)
        kgrid = g["kgrid"]; lim0 = float(g["dK_lim"]); why0 = g["why_lim"]
        mu = float(P.get("mu", 0.087)); PAC = 43.0 - math.degrees(math.atan(mu))
        nr = float(P["nose_r"]); cs = float(P["c_slot"]); u2 = D.u[1]
        lim, why = lim0, why0

        def cut(k_new, tag):
            nonlocal lim, why
            if k_new < lim - 1e-12:
                j = max(int(np.searchsorted(kgrid, k_new + 1e-12)) - 1, 0); lim, why = float(kgrid[j]), tag
        # ---- calibration
        s_th, q_on, q_lo, q_hi, rms, nmv = self._calib()
        # ---- stage 1: the pin
        a_s, psi = float(P["a_s"]), math.radians(float(P["psi"]))
        e1 = -unit(u2 - (u2 @ dR) * dR); e2 = np.cross(dR, e1); v = math.cos(psi) * e1 + math.sin(psi) * e2
        zc = float(PV @ u2); hmid = zc + 3.15 + float(P["glev"]); s0 = (hmid - a_s * float(v @ u2)) / float(dR @ u2)
        F0 = s0 * dR + a_s * v
        nk = len(kgrid); ph = sig * RF.phi_of(kgrid, gg, cc); dph = sig * RF.dphi_of(kgrid, gg, cc)
        RC = S.rotm(dR, ph); C = np.einsum("nij,j->ni", RC, F0)
        vF = dph[:, None] * np.cross(np.tile(dR, (nk, 1)), C); vcap = s_th * np.cross(np.tile(u2, (nk, 1)), C)
        vrel = vF - vcap; n1 = unit(np.cross(vrel, np.tile(u2, (nk, 1))))
        paF = _fold(_angv(n1, vF)); paC = _fold(_angv(n1, vcap))
        rho = np.linalg.norm(C - np.outer(C @ u2, u2), axis=1); z = C @ u2 - hmid
        # pin axis along u2 at the dwell (pressed in the short arm), turned with the crank: tilt across the groove
        ax_pin = np.einsum("nij,j->ni", RC, u2); tilt = np.degrees(np.arcsin(np.clip(np.abs(np.einsum("ni,ni->n", ax_pin, n1)), 0, 1)))
        # groove centreline in link 2's frame over the dwell + rise, the onset blended over 'blend' deg of q2 (C1 quadratic)
        bw = math.radians(float(P["blend"])); kK = float(P["kK"])
        sa = max(abs(s_th), 1e-6)
        x_lo = min((q_lo - q_on) / s_th, (q_hi - q_on) / s_th, 0.0) - math.radians(5.0) / sa
        x = np.arange(x_lo, lim0 + 1e-9, math.radians(0.25) / sa)            # K the linear law asks (negative in the dwell)
        qs = q_on + s_th * x
        if bw > 0:
            hb = bw / abs(s_th) / 2.0                                         # half-width in K units
            Kb = np.where(x <= -hb, 0.0, np.where(x >= hb, x, (x + hb) ** 2 / (4 * hb)))
        else:
            Kb = np.maximum(x, 0.0)
        Kb = np.minimum(Kb, lim0)
        Cq = np.einsum("nij,j->ni", S.rotm(dR, sig * RF.phi_of(Kb, gg, cc)), F0)
        G2 = np.einsum("nij,nj->ni", S.rotm(u2, -(qs - q_on)), Cq)          # link-2 frame (azimuth origin at the onset)
        k_shift = float(np.max(Kb - np.maximum(x, 0.0))) if len(x) else 0.0
        bx = unit(G2[0] - (G2[0] @ u2) * u2); by = np.cross(u2, bx); gx, gy = G2 @ bx, G2 @ by
        dx, dy = np.gradient(gx), np.gradient(gy); ddx, ddy = np.gradient(dx), np.gradient(dy)
        kap = (dx * ddy - dy * ddx) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); rc_line = 1.0 / np.maximum(np.abs(kap), 1e-9)
        # map the centreline radius back onto the K grid (rise part)
        rcK = np.full(nk, 99.0)
        for j in range(len(Kb)):
            if Kb[j] > 0: jj = min(int(np.searchsorted(kgrid, Kb[j])), nk - 1); rcK[jj] = min(rcK[jj], rc_line[j])
        rc_onset = float(rc_line[np.abs(x) <= max(hb if bw > 0 else 0.0, math.radians(2.0))].min()) if (np.abs(x) <= math.radians(2.0) + (hb if bw > 0 else 0)).any() else 99.0
        # stage-1 pressure angles on the BUILT blended groove (the milled centreline: K = Kb(x), x = the K the linear law asks):
        # pin side = the cap ring driving the pin (forward), cap side = the pin driving the cap ring (back-drive)
        hb_ = (bw / abs(s_th) / 2.0) if bw > 0 else 0.0
        xb = np.arange(-hb_ - math.radians(2.0) / sa, lim0 + 1e-9, math.radians(0.02) / sa)
        Kbb = np.where(xb <= -hb_, 0.0, np.where(xb >= hb_, xb, (xb + hb_) ** 2 / (4 * hb_))) if hb_ > 0 else np.maximum(xb, 0.0)
        dKb = np.gradient(Kbb, xb); Cb = np.einsum("nij,j->ni", S.rotm(dR, sig * RF.phi_of(Kbb, gg, cc)), F0)
        vpb = (dKb * sig * RF.dphi_of(Kbb, gg, cc))[:, None] * np.cross(np.tile(dR, (len(xb), 1)), Cb)
        vcb = s_th * np.cross(np.tile(u2, (len(xb), 1)), Cb); nb_ = unit(np.cross(vpb - vcb, np.tile(u2, (len(xb), 1))))
        mvb = np.linalg.norm(vpb, axis=1) > 1e-6
        pinb = np.where(mvb, _fold(_angv(nb_, np.where(mvb[:, None], vpb, nb_))), np.nan); capb = _fold(_angv(nb_, vcb))
        s1_read = str(P.get("s1_read", "built"))
        bpin = mvb & (Kbb > 0) & (pinb > PAC + 1e-9); bcap = (xb >= hb_) & (capb > PAC + 1e-9)
        built = dict(read=s1_read, half_blend_K_deg=round(math.degrees(hb_), 3),
                     pin_max_moving=round(float(np.nanmax(np.where(mvb & (Kbb > 0), pinb, np.nan))), 2) if (mvb & (Kbb > 0)).any() else None,
                     cap_max_outside_blend=round(float(capb[xb >= hb_].max()), 2) if (xb >= hb_).any() else None,
                     cap_inside_blend=[round(float(capb[(xb > -hb_) & (xb < hb_)].min()), 2), round(float(capb[(xb > -hb_) & (xb < hb_)].max()), 2)] if ((xb > -hb_) & (xb < hb_)).any() else None,
                     pin_first_fail_K=round(math.degrees(float(Kbb[int(np.argmax(bpin))])), 3) if bpin.any() else None,
                     cap_first_fail_K=round(math.degrees(float(Kbb[int(np.argmax(bcap))])), 3) if bcap.any() else None,
                     note="cap side gated for x >= half-blend (outside the blend); inside it the cap side is the dwell lock (reported) - a "
                          "re-reading of desmo-slipper's linear-law gate, stated for the auditor")
        self._s1_built = built
        if int(P.get("s1_gate", 1)):
            gates = {"s1-pitch": (rho < R_LO - 1e-9) | (rho > R_HI + 1e-9), "s1-drift": np.abs(z) > DRIFT_MAX + 1e-9}
            if s1_read == "linear":
                gates.update({"s1-pa-pin": paF > PAC + 1e-9, "s1-pa-cap": paC > PAC + 1e-9})
            for tag, bad in gates.items():
                if bad.any(): cut(float(kgrid[int(np.argmax(bad))]) - 1e-9 if np.argmax(bad) > 0 else 0.0, tag)
            if s1_read != "linear":
                for tag, bad in (("s1b-pa-pin", bpin), ("s1b-pa-cap", bcap)):
                    if bad.any():
                        kf = float(Kbb[int(np.argmax(bad))]); cut(max(kf - math.radians(0.25), 0.0), tag)
        jl = max(int(np.searchsorted(kgrid, lim + 1e-12)) - 1, 0)
        # ---- stage 1 metal: ring sector outside O20 (rigid, link 2) + whole ring / pin / short arm (contact)
        m2 = self.link_pts["L2"][0]; lvl_ring = hmid - 0.75
        used = Kb <= lim + 1e-12; Gu = G2[used]
        az = np.arctan2(Gu @ by, Gu @ bx); r_out = float(rho[: jl + 1].max()) + GROOVE_W / 2 + RING_WALL
        azs = np.unwrap(az); a0, a1 = float(azs.min()) - math.radians(3), float(azs.max()) + math.radians(3)
        ring_sk, ring_all = [], []
        for r_ in np.arange(S.HUB_R + 0.25, r_out + 1e-6, 0.5):
            for a_ in np.arange(a0, a1 + 1e-9, 2.0 / r_):
                ring_sk.append(u2 * lvl_ring + r_ * (math.cos(a_) * bx + math.sin(a_) * by))
        for r_ in np.arange(BORE_R, r_out + 1e-6, 1.0):
            for a_ in np.arange(a0, a1 + 1e-9, 2.0 / r_):
                ring_all.append(u2 * lvl_ring + r_ * (math.cos(a_) * bx + math.sin(a_) * by))
        ring_sk = np.array(ring_sk) if ring_sk else np.zeros((0, 3)); ring_all = np.array(ring_all)
        if len(ring_sk):
            if int(P.get("ring_rigid", 1)): self.rigid["ring2"] = (m2, ring_sk)
            self.contact.append((m2, ring_all))
        # pin (O1.5 x 2 above the arm) and the short arm (3 wide, from the crank axis to the pin) as crank metal (contact)
        ef, ff = S.frame_of(u2); dd = S.disc(PIN_D / 2, 0.5)
        pin = np.concatenate([F0 + zz * u2 + dd[:, :1] * ef + dd[:, 1:] * ff for zz in (-0.75, 0.75)])
        A0 = s0 * dR; seg = np.linspace(0, 1, 8); bn = unit(np.cross(dR, F0 - A0))
        arm_s = np.array([A0 + t_ * (F0 - A0) + w_ * bn - 1.0 * u2 for t_ in seg for w_ in (-ARM_W / 2, 0.0, ARM_W / 2)])
        self.contact.append((9, np.concatenate([pin, arm_s])))
        # ---- stage 2, cell B (inverted): the O2 nose fixed in link 1a at C0, the two-walled slot in the crank's tip plate
        sB = self._s2B; C0, R0 = sB["C0"], sB["R0"]
        nr2, cs2, wl2 = float(P["nose_r2"]), float(P["c_slot2"]), float(P["wall2"])
        X = np.einsum("nji,j->ni", S.rotm(uK, sp * kgrid), C0)                   # Rk^T C0: the nose in link 1b's frame
        Rcg = S.rotm(dR, sig * RF.phi_of(kgrid, gg, cc))
        vN = -sp * np.cross(np.tile(uK, (nk, 1)), X)
        vCx = (sig * RF.dphi_of(kgrid, gg, cc))[:, None] * np.cross(np.tile(dR, (nk, 1)), X)
        vrB = vN - vCx; nB = np.cross(unit(X), vrB); nnB = np.linalg.norm(nB, axis=1)
        for j in range(nk):
            nB[j] = nB[j] / nnB[j] if nnB[j] > 1e-12 else (nB[j - 1] if j else unit(vN[0]))
            ref = vN[0] if j == 0 else nB[j - 1]
            if float(nB[j] @ ref) < 0: nB[j] = -nB[j]
        pahB = _fold(_angv(nB, vN)); pacB = _fold(_angv(nB, vCx))
        if int(P.get("s2_gate", 1)):
            b2 = (pahB > PAC + 1e-9) | (pacB > PAC + 1e-9)
            if b2.any(): cut(float(kgrid[int(np.argmax(b2))]) - 1e-9 if np.argmax(b2) > 0 else 0.0, "wall2B-pa")
        cut(math.radians(float(P["kslot"])), "slot-end")                         # the slot is cut to kslot: its far end is stop B
        Z = np.einsum("nji,nj->ni", Rcg, X)                                        # Rc^T X: the nose path in the crank frame
        Lz = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(Z, axis=0), axis=1))])
        spd = np.linalg.norm(vrB, axis=1)
        fail_pl = []
        if sB["rK0"] - sB["rb"] < S.HUB_R + 1.0 - 1e-9: fail_pl.append("boss-hubK")
        # tip plate (crank frame, at the arm-tip layer): stadium of half-width nr2 + cs2 + wl2 around the path over [0, lim]
        jl2 = max(int(np.searchsorted(kgrid, lim + 1e-12)) - 1, 0)
        rPu = R0 + 1.5 + RUNG; hw_in, hw_out = nr2 + cs2, nr2 + cs2 + wl2

        def plate_pts(jend):
            Zs = Z[: jend + 1]; Ls = Lz[: jend + 1]; pick = [0]
            for j in range(1, len(Zs)):
                if Ls[j] - Ls[pick[-1]] >= 1.0: pick.append(j)
            if pick[-1] != len(Zs) - 1: pick.append(len(Zs) - 1)
            Zp = Zs[pick]; tg = np.gradient(Zp, axis=0) if len(Zp) > 1 else np.zeros_like(Zp)
            if len(Zp) == 1 or float(np.linalg.norm(tg[0])) < 1e-9: tg = np.tile(unit(nB[0] @ np.eye(3)), (len(Zp), 1)) if len(Zp) == 1 else tg
            mid, edge = [], []
            for j, z_ in enumerate(Zp):
                rh = unit(z_); t_ = unit(tg[j] - (tg[j] @ rh) * rh) if np.linalg.norm(tg[j]) > 1e-9 else unit(np.cross(rh, dR)); m_ = np.cross(rh, t_)
                for s_ in (-1, 1):
                    edge += [z_ + s_ * hw_in * m_, z_ + s_ * hw_out * m_]
                    if j % 2 == 0: mid.append(z_ + s_ * (hw_in + hw_out) / 2 * m_)
            for jj, sgn_ in ((0, -1.0), (len(Zp) - 1, 1.0)):                     # end caps (the closed end = stop A)
                z_ = Zp[jj]; rh = unit(z_); t_ = unit(tg[jj] - (tg[jj] @ rh) * rh) if np.linalg.norm(tg[jj]) > 1e-9 else unit(np.cross(rh, dR)); m_ = np.cross(rh, t_)
                for a_ in np.linspace(-math.pi / 2, math.pi / 2, 7):
                    d_ = sgn_ * math.cos(a_) * t_ + math.sin(a_) * m_
                    edge += [z_ + hw_in * d_, z_ + hw_out * d_]
                    if abs(a_) < 1e-9: mid.append(z_ + (hw_in + hw_out) / 2 * d_)
            sc = lambda A: unit(np.array(A)) * rPu
            return sc(mid), sc(edge), len(pick)
        plate_mid, plate_edge, _ = plate_pts(jl2)
        # clearances per K step over [0, lim]: plate vs hub K / hub 2 (crank turned by phi), crank low arm vs the boss + root
        memK, cenK, axK = self.cyl["hubK"]; rKc = self.cyl_r["hubK"]; mem2, cen2, ax2 = self.cyl["hub2"]; r2c = self.cyl_r["hub2"]
        plateC = np.concatenate([plate_edge, plate_edge + 2.5 * unit(plate_edge)])
        Rk_all = S.rotm(uK, sp * kgrid); low = g.get("lowarm", np.zeros((0, 3))); bossM = g["lugM"]
        cPK, cP2, cLB = np.full(nk, 99.0), np.full(nk, 99.0), np.full(nk, 99.0)
        for j in range(jl2 + 1):
            XP = plateC @ Rcg[j].T
            cPK[j] = float(self.sd_cyl(XP, cenK, axK, r=rKc).min()); cP2[j] = float(self.sd_cyl(XP, cen2, ax2, r=r2c).min())
            if len(low): cLB[j] = float(cKDTree(bossM @ Rk_all[j]).query(low @ Rcg[j].T)[0].min())
        for tag, arr in (("PLATE-hubK", cPK), ("PLATE-hub2", cP2), ("CRK-BOSS", cLB)):
            bb = arr[: jl2 + 1] < 1.0
            if bb.any(): cut(float(kgrid[max(int(np.argmax(bb)) - 1, 0)]), tag)
        # ---- the BUILT pocket (union of nose discs along the 0.02-deg path, crank held): slop + engagement pressure angles
        key = tuple(np.round(np.concatenate([C0, dR, uK, [sp, sig, gg, cc, nr2, cs2, lim, PAC]]), 6))
        if key not in _SLOPB_CACHE: _SLOPB_CACHE[key] = self._slopB(C0, dR, uK, sp, sig, gg, cc, nr2, cs2, lim, PAC)
        slopB = _SLOPB_CACHE[key]
        if int(P.get("s2_gate", 1)) and slopB["pocket_pa_fail_K0"] is not None:
            cut(math.radians(max(slopB["pocket_pa_fail_K0"] - 0.5, 0.0)), "pocket-pa")
        jl2 = max(int(np.searchsorted(kgrid, lim + 1e-12)) - 1, 0)
        plate_mid, plate_edge, n_pick = plate_pts(jl2)                             # rebuild over the final stroke
        self.rigid["plate"] = (9, plate_mid)
        self.contact.append((9, np.concatenate([plate_edge, plate_edge + 2.5 * unit(plate_edge)])))
        self.strap["ROD"] = (9, np.concatenate([plate_edge + 1.25 * unit(plate_edge)]))
        self._viz_rod["slot"] = [Z[0].tolist(), Z[jl2].tolist()]
        # crank FREE (link 2 fixed): the stage-1 pin play (desmo-slipper's, unchanged)
        er = unit(F0 - (F0 @ u2) * u2); vr0 = abs(float(np.cross(dR, F0) @ er))
        dwell_slop = float(np.degrees(gg * C_GROOVE / max(vr0, 1e-9)))
        lev1 = np.abs(np.einsum("ni,ni->n", n1, np.cross(np.tile(dR, (nk, 1)), C)))[: jl + 1]
        rise_slop = float(np.degrees(gg * C_GROOVE / max(float(lev1.min()), 1e-6)))
        corner = self._corner_slop(F0, dR, u2, sig, gg, cc, s_th, Kb, x, G2, lim)
        free_max = max(dwell_slop, rise_slop, corner["max"])
        fail = list(fail_pl)
        if slopB["slop_max"] > SLOP_MAX + 1e-9: fail.append("slot-slop")
        if free_max > SLOP_MAX + 1e-9: fail.append("groove-slop")
        self._desmo_fail = fail
        g.update(dK_lim=lim, why_lim=why)
        jt = int(np.searchsorted(kgrid, lim + 1e-12))
        dKp = np.abs(np.asarray(self.dK, float)); tk = np.asarray(self.kin_ok, bool) & (dKp > 1e-9)
        jtt = min(int(np.searchsorted(kgrid, min(float(dKp[tk].max()) if tk.any() else 0.0, lim))) + 1, nk)
        info["pa_crank_max_taken"] = round(float(pacB[:jtt].max()), 1); info["pa_horn_max_taken"] = round(float(pahB[:jtt].max()), 1)
        info["pa_eff_crank"] = round(info["pa_crank_max_taken"] + math.degrees(math.atan(float(P.get("mu", 0.087)))), 1)
        info["pa_eff_horn"] = round(info["pa_horn_max_taken"] + math.degrees(math.atan(float(P.get("mu", 0.087)))), 1)
        self._desmo = dict(F0=F0, s0=s0, u2=u2, bx=bx, by=by, hmid=hmid, s_th=s_th, q_on=q_on, r_out=r_out)
        lim_pa = {}
        for mu_ in (0.087, 0.12, 0.135, 0.15, 0.20):
            cap_ = 43.0 - math.degrees(math.atan(mu_)); bb = (pahB > cap_ + 1e-9) | (pacB > cap_ + 1e-9)
            lim_pa["%.3f" % mu_] = round(float(np.degrees(kgrid[max(int(np.argmax(bb)) - 1, 0)])), 2) if bb.any() else round(float(np.degrees(kgrid[-1])), 2)
        info.update(dK_lim=round(math.degrees(lim), 2), why_lim=why, dK_lim_parent=round(math.degrees(lim0), 2), why_lim_parent=why0,
                    desmo=dict(calib=dict(s_th=round(s_th, 4), inv_kK=round(1.0 / kK, 4), q_on_deg=round(math.degrees(q_on), 2),
                                          dwell_deg=[round(math.degrees(q_lo), 1), round(math.degrees(q_hi), 1)], fit_rms_deg=round(math.degrees(rms), 3), n=nmv),
                               stage1=dict(a_s=round(a_s, 3), psi=round(float(P["psi"]), 1), pitch=[round(float(rho[0]), 3), round(float(rho[:jt].max()), 3)],
                                           r_out=round(r_out, 2), pa_pin_max=round(float(paF[:jt].max()), 2), pa_cap_max=round(float(paC[:jt].max()), 2),
                                           pa_gate=round(PAC, 2), drift_max=round(float(np.abs(z[:jt]).max()), 3), tilt_max_deg=round(float(tilt[:jt].max()), 2),
                                           crown_needed=bool(float(tilt[:jt].max()) > 0.5), rc_min=round(float(rcK[:jt].min()), 2), rc_onset=round(rc_onset, 2),
                                           ridge_mm=round(float(rcK[:jt].min()) - GROOVE_W / 2, 3),
                                           blend_K_lead_deg=round(math.degrees(k_shift), 3), arm_from_axis=round(float(np.linalg.norm(F0 - (F0 @ dR) * dR)), 2),
                                           n_ring_rigid=int(len(ring_sk)), ring_az_deg=round(math.degrees(a1 - a0), 1),
                                           lim_by_gate={t: (round(float(np.degrees(kgrid[int(np.argmax(b))])), 2) if b.any() else None)
                                                        for t, b in (("pitch", (rho < R_LO - 1e-9) | (rho > R_HI + 1e-9)), ("pa_pin", paF > PAC + 1e-9),
                                                                     ("pa_cap", paC > PAC + 1e-9), ("drift", np.abs(z) > DRIFT_MAX + 1e-9), ("radius", rcK < RC_MIN))}),
                               stage1_built=self._s1_built,
                               stage2B=dict(nose_r=nr2, c_slot=cs2, wall=wl2, boss_r=sB["rb"], seat_rK=round(sB["rK0"], 2), seat_R=round(R0, 2),
                                            boss_hubK_margin=round(sB["rK0"] - sB["rb"] - S.HUB_R, 2), slot_len_mm=round(float(Lz[jl2]), 2),
                                            plate_len_mm=round(float(Lz[jl2]) + 2 * hw_out, 2), plate_w_mm=round(2 * hw_out, 2),
                                            rel_speed_rest_mm_per_rad=round(float(spd[0]) * 1.0, 3),
                                            pa_horn_max=round(float(pahB[:jt].max()), 2), pa_crank_max=round(float(pacB[:jt].max()), 2),
                                            dK_lim_pa_by_mu=lim_pa, clear_plate_hubK=round(float(cPK[: jl2 + 1].min()), 2),
                                            clear_plate_hub2=round(float(cP2[: jl2 + 1].min()), 2), clear_lowarm_boss=round(float(cLB[: jl2 + 1].min()), 2),
                                            n_plate_rigid=int(len(plate_mid)), n_boss_rigid=int(len(self.rigid["horn"][1]))),
                               slop=dict(slotB=slopB, crank_free=dict(c_mm=C_GROOVE, dwell_deg=round(dwell_slop, 3), rise_deg=round(rise_slop, 3), corner=corner,
                                                                      max_deg=round(free_max, 3), worst_tol_c015_deg=round(free_max * 1.5, 3),
                                                                      held_plus_free_deg=round(free_max + slopB["slop_max"], 3))),
                               fail=fail))
        self._rod_info = info

    @staticmethod
    def _slopB(C0, dR, uK, sp, sig, gg, cc, nr, cs, lim, PAC):
        """crank held at phi(K0): K bisected (0.005 deg) until the nose disc (nr, link 1a) leaves the BUILT pocket = the union
        of discs (nr + cs) along the 0.02-deg nose path in the crank frame; the exit direction is the contact normal ->
        pressure angles at engagement on link 1a (pah, vs the nose's K velocity) and on the crank (pac, vs dR x Z)"""
        kp = np.radians(np.arange(0.0, math.degrees(lim) + 1e-9, 0.02))
        Xp = np.einsum("nji,j->ni", S.rotm(uK, sp * kp), C0); Zp = np.einsum("nji,nj->ni", S.rotm(dR, sig * RF.phi_of(kp, gg, cc)), Xp)
        T = cKDTree(Zp); thc = np.radians(np.arange(0, 360, 2)); rows = []; worst = (0.0, None); fail_k0 = None; pa_max = [0.0, 0.0]; pole = []
        PAG = PAC
        for K0 in np.arange(0.0, math.degrees(lim) + 1e-9, 0.5):
            k0 = math.radians(K0); Rc0 = _rot(dR, sig * float(RF.phi_of(k0, gg, cc)))
            for sgn in (1, -1):
                def outside(dd):
                    k = k0 + sgn * math.radians(dd); Xk = _rot(uK, sp * k).T @ C0; Zk = Rc0.T @ Xk
                    rh = unit(Zk); e1 = unit(np.cross(rh, dR)); e2 = np.cross(rh, e1)
                    dirs = np.cos(thc)[:, None] * e1 + np.sin(thc)[:, None] * e2; d, _ = T.query(Zk[None] + nr * dirs)
                    return float(d.max()) > nr + cs + 1e-6, dirs[int(np.argmax(d))], Xk, Zk, Rc0
                lo, hi = 0.0, 0.01
                while hi < 3.0 and not outside(hi)[0]: lo, hi = hi, hi + 0.01
                for _ in range(2):
                    mid = (lo + hi) / 2
                    if outside(mid)[0]: hi = mid
                    else: lo = mid
                ok, nrm, Xk, Zk, Rc_ = outside(hi)
                vNk = Rc_.T @ (-sp * np.cross(uK, Xk)) * sgn; vCk = np.cross(dR, Zk)
                pah = math.degrees(math.acos(min(1.0, abs(float(nrm @ unit(vNk)))))); pac = math.degrees(math.acos(min(1.0, abs(float(nrm @ unit(vCk))))))
                rows.append((round(float(K0), 2), sgn, round(hi, 4), round(pah, 1), round(pac, 1)))
                if hi > worst[0]: worst = (hi, (round(float(K0), 2), sgn))
                if K0 <= 5.0: pole.append((round(float(K0), 2), sgn, round(hi, 4), round(pah, 1), round(pac, 1)))
                if K0 >= 0.5 - 1e-9:
                    pa_max = [max(pa_max[0], pah), max(pa_max[1], pac)]
                    if (pah > PAG + 1e-9 or pac > PAG + 1e-9) and fail_k0 is None: fail_k0 = float(K0)
        return dict(slop_max=round(worst[0], 4), slop_at=worst[1], pocket_pa_max_horn=round(pa_max[0], 1), pocket_pa_max_crank=round(pa_max[1], 1),
                    pocket_pa_gate=round(PAG, 2), pocket_pa_fail_K0=fail_k0, pole_rows=pole, n_rows=len(rows),
                    note="rows (K0 deg, sign, slop deg, pa link 1a, pa crank) at the built pocket; K0 0 sign -1 = stop A (the closed end)")


DS.PARAMS = PARAMS; DS._clamp = _clamp; DS.DSModel = DCModel
SC.SCModel = DCModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
FL.G.KR.KB.KModel = DCModel; FL.FLModel_SC = DCModel; BM.PARAMS = PARAMS

_report, evaluate, bench_eval, frozen, frozen_held, frozen_flood, redteam, viz_export = (
    DS._report, DS.evaluate, DS.bench_eval, DS.frozen, DS.frozen_held, DS.frozen_flood, DS.redteam, DS.viz_export)


def _report_dc(B, params):
    r, M = DS._report(B, params)
    s2 = getattr(M, "_s2B", None)
    r.setdefault("cam", {})["stage2"] = "B" if s2 else "A"
    return r, M


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if par == "best": par = dict(BEST)
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "redteam":
        out = redteam(par)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(dict(frozen=out["frozen"], why=out["why"], named={k: (v["status"], v["dK"], v["l2_clear"]) for k, v in out["named"].items()},
                              lowest=[(x["i"], x["mm"], x["parts"]) for x in out["lowest"][:5]],
                              lost=[(x["i"], x["why"], x["parts"]) for x in out["lost_to_metal"]]), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"), near2=a.get("gap_near2"),
                              minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), l2=out.get("l2"), dK_taken_max=out.get("dK_taken_max"),
                              connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report_dc(B, par)
    out = dict(stage2=r["cam"]["stage2"], gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), min_metal=r.get("min_metal_mm"),
               reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r.get("inband10"), contact=r["contact"], honest=r.get("honest"),
               why=r.get("why"), ovh=r.get("overhead140"), l2=r.get("l2"), parts=r.get("parts_ib14"),
               cam={k: (r.get("cam") or {}).get(k) for k in ("dK_lim", "why_lim", "dK_lim_parent", "why_lim_parent", "nose_r", "mu", "pa_eff_horn", "pa_eff_crank")},
               desmo=(r.get("cam") or {}).get("desmo"), desmo_fail=r.get("desmo_fail"), secs=round(time.time() - t, 1))
    if mode == "slop" and out["desmo"]: out = dict(cam=out["cam"], desmo=out["desmo"], secs=out["secs"])
    print(json.dumps(out, default=float))
