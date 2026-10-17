"""desmo-slipper-knuckle-3r (round 12, judge pick 2): the verified lead slipper-nose-knuckle-3r (18.49 frozen exact) made
POSITIVE BOTH WAYS. No clock spring, no stop-A pin, no stage-1 roller. Same seats, dyad 26/38.03, law kK 2.1534, drive
g 2.3934 / beta -176.684 / r_c 15.374, pin knee, O20 stacks. Cell A only (the pinned-horn cell B is not built here).

  * K's clock spring and its 6 mm cap are deleted (capK 0, a plain O20 cap). The model's stop A had no metal, so its
    deletion changes no sample. The slot's end cap is the new stop A.
  * STAGE 1: the lobe roller becomes a crowned 440C O1.5 pin on the crank's short arm (a_s mm off the crank axis dR,
    azimuth psi). It runs in a 1.52 x 1.5 groove cut in the underside of hub 2's cap ring (link 2), at the level
    PV.u2 + 3.15 + glev. The cam is EXACT 3-D:
      - per 0.25 deg of K the pin turns sig phi(K) about dR (link 1b frame);
      - link 2 turns about u2 at the rate s_th per unit K, CALIBRATED by regression from the model's own pose
        transforms (R_L1b^T R_L2 on the fit bench's kin_ok poses), so the 'with' / 'against' sense is measured, not assumed;
      - checks per K step: pitch radius in [7.06, 9.94] (the lead's own O20 + 1.5 lobe skirt: outer wall = pitch + 0.76 +
        0.8 <= 11.5); both pressure angles (pin side, cap side) <= 43 - atan(mu); axial drift <= 0.6 mm; groove
        centreline radius >= 1.5 in link 2's frame (the onset corner blended over 4 deg of q2). The first failing
        step cuts the drive range dK_lim (stop B) like the parent's limiters;
      - the pin's across-groove tilt is reported (pin pressed along u2 at the dwell; crowned if > 0.5 deg);
      - metal: the ring sector OUTSIDE hub 2's O20 (r 10 -> pitch + 1.56) over the azimuths of the dwell plus the rise,
        at the ring's underside level, sampled as link-2 metal (rigid, ~1 pt / 4 mm2). The lead never sampled its
        lobe skirt, so this is metal the lead did not pay for. The whole ring, the pin and the short arm go on the
        contact list;
      - link 2's exit vs the short arm and pin (true 3-D, per taken pose, >= 1 mm, else the pose is lost: 'parts').
  * STAGE 2 (cell A): the verified flank (the parent's synthesis, nose_r, PA gate 43 - atan(mu)) plus an OUTER WALL. The
    slot is the swept envelope of the nose: path offsets -(nose_r + c_slot + s) n, s in 0.3 / 1.0 / 1.8, plus end caps
    and a filter that keeps only wall points >= nose_r + 0.3 off the path. The wall is sampled as horn metal (link 1a)
    and checked against the low arm per K step ('CRK-WALL'). The outer-wall pressure angle (the closing drive, now
    positive) is gated at 43 - atan(mu).
  * SLOP / JAM, measured with the crank HELD at phi(K0), K0 on a 0.5-deg grid (K0 = 0 is the dwell-exit reversal), both
    directions. K is bisected to 0.005 deg until the nose disc (nose_r + rho_e) leaves the union of path discs
    (nose_r + rho_e + c_slot) on the 0.02-deg path. rho_e 1.0 and 3.5 are the corner closings. The slop gate is one-sided
    <= 0.25 deg at rho_e 1.0. The contact normal at engagement gives the jam pressure angles. With the crank FREE, the
    stage-1 clearance adds g * c_groove / |n1 . (dR x C)| of K (reported).
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, no gears / pulleys / cables / springs.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/desmo-slipper-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen|held|flood|redteam '<json>' [out.json];  ... slop '<json>' (drive gate only)
    ... claims '[{"tag","mode","params"}]' outdir      (one farm job, claim columns in parallel)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
    DS_CONTROL=1: the desmo additions off (capK 6, no groove / wall): must reproduce the lead's 13.0 fast.
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

os.environ["SN_CELL"] = "lead"
_sp = importlib.util.spec_from_file_location("slipper_for_desmo", os.path.join(HERE, "slipper-nose-knuckle-3r.py"))
SN = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SN)
BM, RF, SC, FL, PK, S = SN.BM, SN.RF, SN.SC, SN.FL, SN.PK, SN.S
RL = SN.RL
unit = S.unit; D2R = math.pi / 180
ID = "desmo-slipper-knuckle-3r"
CONTROL = os.environ.get("DS_CONTROL") == "1"

# the verified lead's best_params (rows/slipper-nose-knuckle-3r.json, 18.49 frozen exact); nose_r 1.25 = the stock ISO 8734
# 2.5 m6 dowel the verifier measured 18.49 with
LEAD_V = {"g": 2.3934, "beta": -176.684, "r_c": 15.3739, "lift": 0.7882, "hl": 1.9442, "zr": 4.0293, "s_arm": 4.0, "r_lobe": 8.2661,
          "nose_r": 1.25, "az2": 45.8211, "el2": 41.0855, "lE": 67.832, "phiE": -2.7863, "lc": 21.1499, "phib": -58.8084,
          "a1max": 58.7678, "kK": 2.1534, "smhi": 16.8433, "bk1": 26.0, "bk2": 38.0336, "mu": 0.087}
# hardware: groove 1.52 +0.01/0 x 1.5 in the cap ring, O1.5 m6 pin (crowned), ring wall 0.8 beyond the groove, bore 6.3
PIN_D, GROOVE_W, RING_WALL, BORE_R, SKIRT_R = 1.5, 1.52, 0.8, 6.3, S.HUB_R + 1.5
R_LO = BORE_R + GROOVE_W / 2                                   # 7.06
R_HI = SKIRT_R - GROOVE_W / 2 - RING_WALL                      # 9.94
C_GROOVE = (GROOVE_W - PIN_D) / 2                              # one-sided pin play, nominal fit (0.01; worst tolerance 0.015 reported)
DRIFT_MAX, RC_MIN, ARM_W, CLEAR_L2 = 0.6, 1.5, 3.0, 1.0
SLOP_MAX = 0.25
DESMO = dict(capK=0.0, a_s=8.75, psi=154.0, glev=-0.5, c_slot=0.01, rho_e=1.0, blend=4.0, ring_rigid=1, s1_gate=1)
PARAMS = dict(SN.PARAMS, **LEAD_V, **({} if CONTROL else DESMO))
if CONTROL: PARAMS["capK"] = 6.0
REPORT_KEYS = ("plain", "gap_near1", "gap_near2", "min_metal_mm", "why", "cam", "desmo", "l2", "overhead140", "ws_inband", "parts_ib14")


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def _clamp(p):
    p = SN._clamp(p)
    if CONTROL: return p
    p["capK"] = 0.0
    p["a_s"] = _c(p.get("a_s", 8.625), 5.0, 12.0); p["psi"] = float(p.get("psi", 184.0)) % 360.0
    p["glev"] = _c(p.get("glev", 0.0), -1.0, 1.5); p["c_slot"] = _c(p.get("c_slot", 0.01), 0.005, 0.05)
    p["rho_e"] = _c(p.get("rho_e", 1.0), 0.5, 4.0); p["blend"] = _c(p.get("blend", 4.0), 0.0, 10.0)
    return p


def _fold(a): return np.minimum(a, 180.0 - a)


def _angv(a, b):
    c = np.einsum("ni,ni->n", a, b) / (np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1) + 1e-12)
    return np.degrees(np.arccos(np.clip(c, -1, 1)))


def _rot(u, a):
    u = np.asarray(u, float) / np.linalg.norm(u); K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


_SLOP_CACHE = {}


class DSModel(SN.SNModel):
    def _rod_metal(self):
        SN.SNModel._rod_metal(self)                                   # the lead's stage-2 synthesis (nose_r, mu), unchanged
        if CONTROL: self._desmo = None; return
        self._desmo_build()

    # ------------------------------------------------------------------ calibration: link 2 vs link 1b about u2 per unit K
    def _calib(self):
        D = self.D; u2 = D.u[1]; mL2 = self.link_pts["L2"][0]; mLb = self.link_pts["L1b"][0]
        idx = np.nonzero(np.asarray(self.kin_ok, bool))[0]; th, kk = [], []
        for i in idx:
            Rb, tb = self.T(mLb, i); R2, t2 = self.T(mL2, i); Rr = Rb.T @ R2
            w = 0.5 * np.array([Rr[2, 1] - Rr[1, 2], Rr[0, 2] - Rr[2, 0], Rr[1, 0] - Rr[0, 1]])
            th.append(math.atan2(float(w @ u2), (float(np.trace(Rr)) - 1) / 2)); kk.append(abs(float(self.dK[i])))
        th = np.unwrap(np.array(th)); kk = np.array(kk); mv = kk > math.radians(0.5)
        if mv.sum() >= 3:
            A = np.vstack([kk[mv], np.ones(mv.sum())]).T; (s_th, q_on), res, *_ = np.linalg.lstsq(A, th[mv], rcond=None)
            fit_rms = float(np.sqrt(np.mean((A @ np.array([s_th, q_on]) - th[mv]) ** 2)))
        else:
            s_th, q_on, fit_rms = 1.0 / float(D.p.get("kK", 2.0)), 0.0, float("nan")
        dw = th[~mv] if (~mv).any() else np.array([q_on])
        return float(s_th), float(q_on), float(dw.min()), float(dw.max()), fit_rms, int(mv.sum())

    def _desmo_build(self):
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
        if int(P.get("s1_gate", 1)):
            gates = {"s1-pitch": (rho < R_LO - 1e-9) | (rho > R_HI + 1e-9), "s1-pa-pin": paF > PAC + 1e-9, "s1-pa-cap": paC > PAC + 1e-9,
                     "s1-drift": np.abs(z) > DRIFT_MAX + 1e-9}
            for tag, bad in gates.items():
                if bad.any(): cut(float(kgrid[int(np.argmax(bad))]) - 1e-9 if np.argmax(bad) > 0 else 0.0, tag)
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
        # ---- stage 2: the slot's outer wall (link 1a, member 1), the swept envelope of the nose over [0, lim]
        C0 = np.asarray(self._viz_rod["roller"], float); R0 = float(np.linalg.norm(C0)); rL = R0 - 1.5
        kk = kgrid[: jl + 1]; Rk = S.rotm(uK, sp * kk); Rcg = S.rotm(dR, sig * RF.phi_of(kk, gg, cc))
        Cg = np.einsum("nij,j->ni", Rcg, C0 - PV) + PV
        ng = np.zeros_like(Cg); nprev = None; pah2 = np.zeros(len(kk)); pac2 = np.zeros(len(kk))
        for j in range(len(kk)):
            Cj = Cg[j]; vC = sig * float(RF.dphi_of(kk[j], gg, cc)) * np.cross(dR, Cj); vh = -sp * np.cross(uK, Cj); vr_ = vC - vh
            n = np.cross(unit(Cj), vr_); nn = float(np.linalg.norm(n)); n = n / nn if nn > 1e-9 else (nprev if nprev is not None else unit(vh))
            if nprev is None: n = n if float(n @ vh) >= 0 else -n
            else: n = n if float(n @ nprev) >= 0 else -n
            ng[j] = n; nprev = n
            Qo = Cj - nr * n                                                   # outer-wall contact point (closing drive)
            pac2[j] = float(_fold(_angv(n[None], vC[None]))[0]); pah2[j] = float(_fold(_angv(n[None], (-sp * np.cross(uK, Qo))[None]))[0])
        bad2 = (pac2 > PAC + 1e-9) | (pah2 > PAC + 1e-9)
        if bad2.any(): cut(float(kk[int(np.argmax(bad2))]) - 1e-9 if np.argmax(bad2) > 0 else 0.0, "wall2-pa")
        P1 = np.einsum("nij,nj->ni", Rk, Cg); N1 = np.einsum("nij,nj->ni", Rk, ng)

        def plane(X): return X / np.linalg.norm(X, axis=1)[:, None] * rL
        pick = [0]; acc = 0.0
        for j in range(1, len(kk)):
            acc += float(np.linalg.norm(P1[j] - P1[j - 1]))
            if acc >= 1.5: pick.append(j); acc = 0.0
        if pick[-1] != len(kk) - 1: pick.append(len(kk) - 1)
        rw = nr + cs
        wall = [plane(P1[pick] - (rw + s) * N1[pick]) for s in (0.3, 1.0, 1.5)]
        caps = []
        for jj in (0, len(kk) - 1):
            c_ = P1[jj]; cn = unit(c_); e_ = unit(N1[jj] - (N1[jj] @ cn) * cn); f_ = np.cross(cn, e_)
            for rad in (rw + 0.3, rw + 1.0, rw + 1.5):
                for a_ in np.linspace(0, 2 * math.pi, 24, endpoint=False): caps.append(c_ + rad * (math.cos(a_) * e_ + math.sin(a_) * f_))
        W = np.concatenate(wall + [plane(np.array(caps))])
        dpath = cKDTree(P1).query(W + 1.5 * unit(W))[0]; W = W[dpath >= nr + 0.3 - 1e-6]
        rax = np.linalg.norm(W - (W @ uK)[:, None] * uK, axis=1); W = W[rax >= S.HUB_R + 0.5]
        WM = W + 1.5 * unit(W)
        low = g.get("lowarm", np.zeros((0, 3))); cW = 99.0
        if len(low) and len(WM):
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
        # ---- slop / jam (crank held), cached on the drive geometry
        key = tuple(np.round(np.concatenate([C0, PV, dR, uK, [sp, sig, gg, cc, nr, cs, lim]]), 6))
        if key not in _SLOP_CACHE: _SLOP_CACHE[key] = self._slop(C0, PV, dR, uK, sp, sig, gg, cc, nr, cs, lim, PAC)
        slop = _SLOP_CACHE[key]
        # crank FREE (link 2 fixed): the stage-1 pin play. Dwell: g c / |(dR x F0) . e_r| (the dwell groove is a circle about u2);
        # rise: g c / |n1 . (dR x C)|; onset corner: the milled groove = union of O(2 x 0.76) discs along the blended centreline,
        # the pin disc O1.5 at (q fixed, K +- d) bisected until it leaves the groove (c = 0.01 nominal)
        er = unit(F0 - (F0 @ u2) * u2); vr0 = abs(float(np.cross(dR, F0) @ er))
        dwell_slop = float(np.degrees(gg * C_GROOVE / max(vr0, 1e-9)))
        lev1 = np.abs(np.einsum("ni,ni->n", n1, np.cross(np.tile(dR, (nk, 1)), C)))[: jl + 1]
        rise_slop = float(np.degrees(gg * C_GROOVE / max(float(lev1.min()), 1e-6)))
        corner = self._corner_slop(F0, dR, u2, sig, gg, cc, s_th, Kb, x, G2, lim)
        free_max = max(dwell_slop, rise_slop, corner["max"])
        fail = []
        if slop["slop_max"].get("1.0", 0.0) > SLOP_MAX + 1e-9: fail.append("slot-slop")
        if free_max > SLOP_MAX + 1e-9: fail.append("groove-slop")
        self._desmo_fail = fail
        g.update(dK_lim=lim, why_lim=why)
        jt = int(np.searchsorted(kgrid, lim + 1e-12))
        self._desmo = dict(F0=F0, s0=s0, u2=u2, bx=bx, by=by, hmid=hmid, s_th=s_th, q_on=q_on, r_out=r_out)
        info.update(dK_lim=round(math.degrees(lim), 2), why_lim=why, dK_lim_parent=round(math.degrees(lim0), 2), why_lim_parent=why0,
                    desmo=dict(calib=dict(s_th=round(s_th, 4), inv_kK=round(1.0 / kK, 4), q_on_deg=round(math.degrees(q_on), 2),
                                          dwell_deg=[round(math.degrees(q_lo), 1), round(math.degrees(q_hi), 1)], fit_rms_deg=round(math.degrees(rms), 3), n=nmv),
                               stage1=dict(a_s=round(a_s, 3), psi=round(float(P["psi"]), 1), pitch=[round(float(rho[0]), 3), round(float(rho[:jt].max()), 3)],
                                           r_out=round(r_out, 2), pa_pin_max=round(float(paF[:jt].max()), 2), pa_cap_max=round(float(paC[:jt].max()), 2),
                                           pa_gate=round(PAC, 2), drift_max=round(float(np.abs(z[:jt]).max()), 3), tilt_max_deg=round(float(tilt[:jt].max()), 2),
                                           crown_needed=bool(float(tilt[:jt].max()) > 0.5), rc_min=round(float(rcK[:jt].min()), 2), rc_onset=round(rc_onset, 2),
                                           blend_K_lead_deg=round(math.degrees(k_shift), 3), arm_from_axis=round(float(np.linalg.norm(F0 - (F0 @ dR) * dR)), 2),
                                           n_ring_rigid=int(len(ring_sk)), ring_az_deg=round(math.degrees(a1 - a0), 1),
                                           lim_by_gate={t: (round(float(np.degrees(kgrid[int(np.argmax(b))])), 2) if b.any() else None)
                                                        for t, b in (("pitch", (rho < R_LO - 1e-9) | (rho > R_HI + 1e-9)), ("pa_pin", paF > PAC + 1e-9),
                                                                     ("pa_cap", paC > PAC + 1e-9), ("drift", np.abs(z) > DRIFT_MAX + 1e-9), ("radius", rcK < RC_MIN))}),
                               wall2=dict(n=int(len(W)), pa_crank_max=round(float(pac2[:jt].max()), 2) if len(pac2) else None,
                                          pa_horn_max=round(float(pah2[:jt].max()), 2) if len(pah2) else None, clear_lowarm=round(cW, 2)),
                               slop=dict(slop, crank_free=dict(c_mm=C_GROOVE, dwell_deg=round(dwell_slop, 3), rise_deg=round(rise_slop, 3), corner=corner,
                                                               max_deg=round(free_max, 3), worst_tol_c015_deg=round(free_max * 1.5, 3),
                                                               held_plus_free_deg=round(free_max + slop["slop_max"].get("1.0", 0.0), 3))),
                               fail=fail))
        self._rod_info = info

    @staticmethod
    def _corner_slop(F0, dR, u2, sig, gg, cc, s_th, Kb, x, G2, lim):
        T = cKDTree(G2[Kb <= lim + 1e-12]); thc = np.radians(np.arange(0, 360, 4)); e1, f1 = S.frame_of(u2); rows = []; worst = 0.0
        sa = max(abs(s_th), 1e-9); Kof = lambda xx: float(np.interp(xx, x, Kb))
        for x0d in (-4.0, -2.0, -1.0, 0.0, 1.0, 2.0, 4.0, 8.0, 15.0):
            x0 = math.radians(x0d); K0 = Kof(x0); Rq = _rot(u2, -(s_th * x0)); res = []
            for sgn in (1, -1):
                def outside(dd):
                    K = K0 + sgn * math.radians(dd)
                    c = Rq @ (_rot(dR, sig * float(RF.phi_of(K, gg, cc))) @ F0)
                    d, _ = T.query(c[None] + (PIN_D / 2) * (np.cos(thc)[:, None] * e1 + np.sin(thc)[:, None] * f1))
                    return float(d.max()) > GROOVE_W / 2 + 1e-6
                lo, hi = 0.0, 0.02
                while hi < 5.0 and not outside(hi): lo, hi = hi, hi + 0.02
                for _ in range(4):
                    mid = (lo + hi) / 2
                    if outside(mid): hi = mid
                    else: lo = mid
                res.append(round(hi, 3))
            if K0 > 1e-9 or True:
                one = res[0] if K0 <= 1e-9 else max(res)                         # at K 0 the slot's end cap stops -K
                worst = max(worst, one)
            rows.append((x0d, round(math.degrees(K0), 3), res[0], res[1]))
        return dict(max=round(worst, 3), rows=rows, note="(x0 deg of the K law from the onset, K, +K play, -K play), deg of K")

    @staticmethod
    def _slop(C0, PV, dR, uK, sp, sig, gg, cc, nr, cs, lim, PAC):
        """crank held at phi(K0): bisect K (0.005 deg) until the nose disc (nr + rho_e) leaves the union of path discs
        (nr + rho_e + cs) along the 0.02-deg path in link 1a's frame; the contact normal at engagement -> jam PAs"""
        kp = np.radians(np.arange(0.0, math.degrees(lim) + 1e-9, 0.02))
        Cg = np.einsum("nij,j->ni", S.rotm(dR, sig * RF.phi_of(kp, gg, cc)), C0 - PV) + PV
        P1 = np.einsum("nij,nj->ni", S.rotm(uK, sp * kp), Cg); T = cKDTree(P1)
        thc = np.radians(np.arange(0, 360, 3))
        out = dict(slop_max={}, slop_at={}, pa_eng_max={}, k0_grid_deg=0.5)
        for rho_e in (1.0, 3.5):
            rne = nr + rho_e; worst = (0.0, None); pa_w = 0.0; rows = []
            for K0 in np.arange(0.0, math.degrees(lim) + 1e-9, 0.5):
                k0 = math.radians(K0); Cc = _rot(dR, sig * float(RF.phi_of(k0, gg, cc))) @ (C0 - PV) + PV
                for sgn in (1, -1):
                    def outside(dd):
                        k = k0 + sgn * math.radians(dd); Pc = _rot(uK, sp * k) @ Cc; rh = unit(Pc); e1 = unit(np.cross(rh, uK)); e2 = np.cross(rh, e1)
                        dirs = np.cos(thc)[:, None] * e1 + np.sin(thc)[:, None] * e2; d, _ = T.query(Pc[None] + rne * dirs)
                        return float(d.max()) > rne + cs + 1e-6, dirs[int(np.argmax(d))], k
                    lo, hi = 0.0, 0.02
                    while hi < 3.0 and not outside(hi)[0]: lo, hi = hi, hi + 0.02
                    for _ in range(3):
                        mid = (lo + hi) / 2
                        if outside(mid)[0]: hi = mid
                        else: lo = mid
                    ok, nrm, k = outside(hi)
                    n1b = _rot(uK, sp * k).T @ nrm; Qb = Cc + nr * n1b
                    vC = sig * float(RF.dphi_of(k0, gg, cc)) * np.cross(dR, Cc); vh = -sp * np.cross(uK, Qb)
                    pac = math.degrees(math.acos(min(1.0, abs(float(n1b @ unit(vC)))))); pah = math.degrees(math.acos(min(1.0, abs(float(n1b @ unit(vh))))))
                    rows.append((round(float(K0), 2), sgn, round(hi, 4), round(pac, 1), round(pah, 1)))
                    if hi > worst[0]: worst = (hi, (round(float(K0), 2), sgn))
                    pa_w = max(pa_w, min(pac, pah))
            out["slop_max"]["%.1f" % rho_e] = round(worst[0], 4); out["slop_at"]["%.1f" % rho_e] = worst[1]
            out["pa_eng_max"]["%.1f" % rho_e] = round(pa_w, 1)
            if rho_e == 1.0:
                out["rows_rho1_K0_0_10"] = [r for r in rows if r[0] <= 10.0]
                out["slop_K0_0"] = [r for r in rows if r[0] == 0.0]
        return out

    def l2_check(self, idx):
        """link 2's strap OUTSIDE hub 2's O20 + 1.5 vs the short arm and the pin (3-D, per pose): min distance minus the
        arm half width and half the strap thickness"""
        dm = self._desmo; out = []
        m2, X2 = self.link_pts["L2"]; c2, ax2 = self.cyl["hub2"][1], self.cyl["hub2"][2]
        w = X2 - c2; rr = np.linalg.norm(w - np.outer(w @ ax2, ax2) / max(float(ax2 @ ax2), 1e-12), axis=1); X2o = X2[rr > S.HUB_R + 1.5]
        if not len(X2o): return np.full(len(idx), 99.0)
        F0, s0, u2 = dm["F0"], dm["s0"], dm["u2"]; dR = self._scg["dR"]; A0 = s0 * dR
        arm = np.array([A0 + t_ * (F0 - A0) for t_ in np.linspace(0, 1, 10)] + [F0 + 0.75 * u2])
        X2s = np.concatenate([X2o, X2o + S.T_LINK * unit(X2o)])
        for i in idx:
            R9, t9 = self.T(9, i); R2_, t2_ = self.T(m2, i)
            Aw = arm @ R9.T + t9; Sw = X2s @ R2_.T + t2_
            out.append(float(cKDTree(Sw).query(Aw)[0].min()) - ARM_W / 2)
        return np.array(out)

    def run(self, B=None):
        r = super().run() if B is None else super().run(B)
        if CONTROL or not getattr(self, "_desmo", None): return r
        try:
            Bn = self.B; why = [str(w) for w in self.why]
            taken = [i for i in range(len(Bn.idx)) if why[i] == "" and Bn.res[i] is not None]
            if taken:
                cl = self.l2_check(taken); badi = [taken[j] for j in np.nonzero(cl < CLEAR_L2)[0]]
                for i in badi: Bn.res[i] = None; self.why[i] = "parts"
                self._l2 = dict(n=len(taken), clear_min=round(float(cl.min()), 2), lost=len(badi))
                if badi:
                    rep = Bn.report()
                    for k in ("gap", "reach", "follow", "inband14", "inband10", "contact"): r[k] = rep[k]
                    w = r.get("why") or {}; w["parts"] = w.get("parts", 0) + len(badi); r["why"] = w
        except Exception as ex_:
            self._l2 = dict(error=repr(ex_))
        return r


SC.SCModel = DSModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
FL.G.KR.KB.KModel = DSModel; FL.FLModel_SC = DSModel
BM.PARAMS = PARAMS


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = SN._report(B, p)
    info = getattr(M, "_sc_info", None) or {}
    for k in ("desmo", "dK_lim", "why_lim", "dK_lim_parent", "why_lim_parent"):
        if k in info: r.setdefault("cam", {})[k] = info[k]
    r["l2"] = getattr(M, "_l2", None)
    fl = getattr(M, "_desmo_fail", None)
    if fl: r["honest"] = False; r["desmo_fail"] = fl
    if r.get("l2") and r["l2"].get("lost") and r.get("gap_near2") is not None:
        r["gap_near2_note"] = "near-touch objective computed before the l2 losses; the plain gap includes them"
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved") or r.get("desmo_fail"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None)
    if not r.get("honest", True): r["gap_honest"] = r["gap"]; r["gap"] = max(float(r["gap"]), 275.0)
    return r


def _frozen_model(P, nc, nw):
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = DSModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    fit["l2"] = getattr(M1, "_l2", None)
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(DSModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info", "_desmo"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if nc == -1:
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_desmo", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
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
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
               parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), ws_inband=RL.ws_inband(B), split=RL.contact_split(M, B),
               overhead=dict(ws=int(ov.sum()), taken=int((ov & (mins >= 0)).sum())), l2=getattr(M, "_l2", None), crown=SN.crown_report(M, B),
               cam={k: info.get(k) for k in ("dK_lim", "why_lim", "dK_lim_parent", "why_lim_parent", "pa_crank_max_taken", "pa_horn_max_taken",
                                             "pa_kin_max", "pa_eff_horn", "pa_eff_crank", "flank_rho_min", "clear_hubK_min", "clear_lowarm_lug_min",
                                             "contact_r", "nose_r", "mu", "desmo")})
    dK = np.degrees(np.abs(np.asarray(M.dK, float))); tk = [j for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) >= 0]
    out["dK_taken_max"] = round(float(dK[tk].max()), 2) if tk else None
    return out


def frozen_held(P): return frozen(P, -1, -1)


def frozen_flood(P, nc=110, nw=360):
    os.environ["CB_EXACT"] = "1"
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    out = dict(frozen={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")})
    sp_ = importlib.util.spec_from_file_location("minarc_mech_for_desmo", os.path.join(REPO, "docs", "concepts", "verify", "minarc-stop-knuckle-4r-mechanism.py"))
    MECH = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(MECH)
    t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


def redteam(P, nc=110, nw=360):
    """the frozen wear's lowest-metal taken poses with their lowest parts, the parts behind each lost-to-metal pose, and
    the named poses (rest, overhead, across the body, behind the back, extreme rotations) with the drive state"""
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
    g = M._scg; res["named"] = {}
    for nm, (pl, el, ax) in named.items():
        i = near(pl, el, ax); w = str(M.why[i]) or "taken"; k = abs(float(M.dK[i]))
        res["named"][nm] = dict(i=i, pose=pose(i), status=w, dK=round(math.degrees(k), 1),
                                phi=round(math.degrees(float(RF.phi_of(k, g["g"], g.get("c", 0.0)))), 1),
                                l2_clear=round(float(M.l2_check([i])[0]), 2) if M._desmo else None,
                                parts=parts_at(i) if w in ("taken", "contact", "skin", "parts") else None)
    return res


def viz_export(par): return RF.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "claims":
        import subprocess
        od = sys.argv[3] if len(sys.argv) > 3 else "ds_out"; os.makedirs(od, exist_ok=True); procs = []
        for c in par:
            env = dict(os.environ, CB_EXACT="1", OMP_NUM_THREADS="1", IGL_NUM_THREADS="1", CB_QUIET_EXACT="1")
            if c.get("control"): env["DS_CONTROL"] = "1"
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
        print(json.dumps(dict(frozen=out["frozen"], why=out["why"], named={k: (v["status"], v["dK"], v["l2_clear"]) for k, v in out["named"].items()},
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
    r, M = _report(B, par)
    out = dict(control=CONTROL, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
               reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r.get("inband10"), contact=r["contact"], honest=r.get("honest"),
               why=r.get("why"), ovh=r.get("overhead140"), l2=r.get("l2"), parts=r.get("parts_ib14"),
               cam={k: (r.get("cam") or {}).get(k) for k in ("dK_lim", "why_lim", "dK_lim_parent", "why_lim_parent", "nose_r", "mu", "pa_eff_horn", "pa_eff_crank")},
               desmo=(r.get("cam") or {}).get("desmo"), desmo_fail=r.get("desmo_fail"), secs=round(time.time() - t, 1))
    if mode == "slop" and out["desmo"]: out = dict(cam=out["cam"], desmo=out["desmo"], secs=out["secs"])
    print(json.dumps(out, default=float))
