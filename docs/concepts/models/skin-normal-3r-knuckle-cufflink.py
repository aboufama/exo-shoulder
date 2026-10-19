"""Concept model: ALL-SKIN-NORMAL 3R CLOSED BY THREE PINS (id skin-normal-3r-knuckle-cufflink).

Chain: scapula -> J1 (O20 hub, ACTIVE R, square-ish on its skin seat, line off GH) -> link 1 -> J2 (O20 hub, ACTIVE R)
-> crank (lk mm flat plate on hub 2's rotor) -> knuckle pin k (PASSIVE R, parallel to J2) -> link 2b -> J3 (O20 hub,
ACTIVE R) -> rotor plate (hub 3 + E arm, one flat plate) -> pin a (PASSIVE R, parallel to J3) -> cuff link (flat plate)
-> pin b (PASSIVE R, parallel to J3) -> arm pad (on the user's cuff, BOTTOM) -> humerus; loop closed by GH.
Spatial Grubler: 7 bodies, 6 x 1-DOF joints + GH (3): M = 6 (7 - 1 - 7) + 6 + 3 = 3; 3 ACTIVE, 3 PASSIVE ROTATIONS,
0 passive translations. Every passive coordinate is set by the closure (R17):

* orientation: R1(q1) R2(q2 + ... ) R3(...) = arm, the spherical IK of the 3 axis DIRECTIONS (the verified seed's
  S.Design.ik; the knuckle and the cuff pins are parallel to J2 / J3, so they only add to those angles);
* radial (along J3's axis): the line offsets leave a drift sv of the virtual member 3 on the arm (S.Design.ik's s);
  the knuckle moves everything after it by Delta = R1 (Rot(u2, q2 - qk) - Rot(u2, q2)) e0 (e0 = the crank) and must
  make (sv + Q^T Delta) . sn = c0 (the cuff plane). Closed form: lk rho cos(Phi - qk) = c0 - s_n + lk rho cos(Phi),
  Phi = alk + q2 - chi (rho, chi = J3's normal seen in hub 2's plane): two roots, ONE kept (sign k_sk of sin = one
  assembly mode), authority lk rho |sin| >= `auth` mm/rad (away from toggle), |qk - k_mid| <= `kswing` deg;
* in-plane: J3's line pierces the cuff plane at d = (s'_a, s'_t); pin a = d + LE (cos, sin)(phE + psi) on the rotor,
  pin b fixed on the arm; |pin a - pin b| = lc: a two-circle intersection on ONE elbow sign, elbow angle kept `gmin`
  deg off straight / folded. psi = the rotor's turn (J3's actuator = q3 + psi), the link turns beta about pin b.
Design steps (from the fit set: fit clips at 10 fps + the bench poses, never the held-out clips): c0, the knuckle
branch and mid (most poses with a valid root inside +-kswing), the cuff's mid drift m (pin b = m + LE eE + lc eB).

Parts at real size (mm): O20 x 12.25 hubs (docs/HARDWARE.md v5, F -> crown), links 1 and 2b = 8 x 3 straps with the
verified seed's ray-fitted undersides and <= 60 deg ramps (as the controls 41.73 / 42.59 / 45.31, so the comparison is
like for like), crank 8 x 3 flat on hub 2's upper level (F2 + 3.15) out to an O12 knuckle boss (IGLIDUR-PIN: O4 pin in
a GSM sleeve, 2 thrust washers), link 2b laps over the crank (+3.15), rotor plate = hub 3's lower plate + the 8 x 3
E arm (one flat plate, one height), cuff link 8 x 3 flat with O12 bosses, over the E arm (+3.15) and over the pad
(+3.15), arm pad 16 x 16 x 3 flat. Skin-facing undersides sampled on a 2 mm grid (1 pt / 4 mm2); hub side walls and
crowns, plate tops, strap tops and pin heads are skin-checked (contact only). Part-part clearance: non-adjacent 1 mm,
adjacent members of one joint the 0.15 mm running gap (hub cylinders exact, plates / straps as mid-surfaces with
their half thickness).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/skin-normal-3r-knuckle-cufflink.py [check|redteam] ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("osn_for_knuckle", os.path.join(HERE, "offset-skin-normal-3r.py"))
OSN = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(OSN)
S = OSN.S
unit, rotm, frame_of, disc, rect = S.unit, S.rotm, S.frame_of, S.disc, S.rect
HUB_R, CROWN, UP, T_LINK, W_LINK, SP = S.HUB_R, S.CROWN, S.UP, S.T_LINK, S.W_LINK, S.SPACING
BOSS_R, PAD = 6.0, 16.0                                       # O12 pin bosses, arm pad 16 x 16
PIN_HEAD = 1.0                                                # pin head / washer above the top plate
D2R = math.pi / 180
ID = "skin-normal-3r-knuckle-cufflink"
NAME = "All-skin-normal 3R closed by three pins (J2 knuckle + pinned cuff link)"

PARAMS = dict(OSN.PARAMS)
PARAMS.update(az1=94.61, el1=60.68, b1=0.34, az2=24.06, el2=48.54, b2=0.42, wd=75.16, wa=-13.04, b3=0.21,  # snh k722 seats
              lk=30.0, alk=0.0, alk_off=90.0,   # crank length; direction (deg about J2 from the hub2 -> hub3 direction):
                                                 # alk None = circular median of (chi - q2) + alk_off over the fit set
                                                 # (alk_off +-90: the crank square to J3's normal at the median pose, max authority)
              LE=45.0, lc=30.0,           # E arm (J3 line -> pin a), cuff link (pin a -> pin b)
              phE=0.0, dB=90.0,           # E arm direction in hub 3's plane (deg from the along-arm axis), link direction rel. E arm at mid
              gmin=25.0, auth=5.0, kswing=35.0,
              crank_strap=0,              # 0: flat crank at the knuckle hub's upper level (spec); 1: skin-following strap to a flat boss
              kat=2,                      # knuckle site: 2 = on J2's rotor (spec), 1 = on J1's rotor (the scapula dome: a fixed skin circle)
              hub_lv=(50.0, 61.0, 73.0),  # nominal hub levels (mm along each axis) that set the crank's alk = 0 direction
              alk_auto=None, k_c0=None, k_sk=None, k_mid=None, cuff_m=None, cuff_sig=None,     # design-step outputs (auto when None)
              drop=1, jam_contact=1, slides=1, remote=1, ramp=1, vfix=1)
for k in ("S_a", "S_t", "R_r", "S_max", "centre", "R_tol", "inv", "S_auto", "neck"): PARAMS.pop(k, None)


def wrap(a): return (a + np.pi) % (2 * np.pi) - np.pi


class Design(OSN.Design):
    """OSN's seats (lines through skin seats, axes tilted to the skin normal by b_k) + knuckle and cuff geometry"""
    def __init__(self, params=None):
        P = dict(PARAMS); P.update(params or {}); P.setdefault("S_a", 0.0); P.setdefault("S_t", 0.0); P.setdefault("R_r", 0.0)
        super().__init__(P); self.p = P
        j = 0 if int(P.get("kat", 2)) == 1 else 1; self.kj = j
        ku = self.u[j]; e, f = frame_of(ku); self.ku = ku; self.kc = self.c[j]; lv = P.get("hub_lv") or (50.0, 61.0, 73.0)
        w = (self.c[j + 1] + lv[j + 1] * self.u[j + 1]) - (self.c[j] + lv[j] * self.u[j])    # this hub -> the next hub (q = 0 layout)
        w = w - (w @ ku) * ku; w = unit(w) if np.linalg.norm(w) > 1e-6 else e
        self.ke = w; self.kf = np.cross(ku, w)                          # knuckle frame: alk 0 = along the link toward the next hub
        if P.get("alk") is None or P.get("alk_auto"): P["alk_auto"] = True
        self.set_alk(P["alk"] if P.get("alk") is not None else 0.0)
        pe = P["phE"] * D2R; self.eE = math.cos(pe) * self.sa + math.sin(pe) * self.st
        pb = (P["phE"] + P["dB"]) * D2R; self.eB = math.cos(pb) * self.sa + math.sin(pb) * self.st

    def set_alk(self, alk):
        self.p["alk"] = alk; a = alk * D2R; self.ek = math.cos(a) * self.ke + math.sin(a) * self.kf; self.e0 = self.p["lk"] * self.ek

    def e0_at(self, th):
        """crank vector rotated by th about u2 (member-1 frame), (n, 3)"""
        a = self.p["alk"] * D2R + th; L = self.p["lk"]
        return L * (np.cos(a)[:, None] * self.ke + np.sin(a)[:, None] * self.kf)

    def knuckle_raw(self, Q, q, X1, s):
        """per pose: kap, Phi, lk*rho (the radial closure is lk rho cos(Phi - qk) = c0 - s_n + lk rho cos Phi)"""
        w = Q @ self.sn
        v = w if self.kj == 0 else np.einsum("nji,nj->ni", X1[0], w)      # J3's axis seen in the knuckle hub's stator frame
        ve, vf = v @ self.ke, v @ self.kf; rho = np.hypot(ve, vf); chi = np.arctan2(vf, ve)
        Phi = self.p["alk"] * D2R + q[:, self.kj] - chi
        return Phi, self.p["lk"] * rho, s[:, 2]

    def solve(self, Q):
        """full kinematics: q6 (n, 6) rad [J1, J2 = q2 - qk, J3 = q3 + psi, qk, qa, qb], ok, why codes, transforms"""
        P = self.p; q, okf, X1, X2, X3, s = self.ik(Q); n = len(Q)
        Phi, Lr, sn_ = self.knuckle_raw(Q, q, X1, s)
        c0, sk, kmid = P["k_c0"], P["k_sk"], P["k_mid"]
        kap = (c0 - sn_) / np.maximum(Lr, 1e-9) + np.cos(Phi)
        okk = np.abs(kap) <= 1.0; th = np.arccos(np.clip(kap, -1, 1))
        qk = wrap(Phi - sk * th); authv = Lr * np.sin(th)
        okk &= authv >= P["auth"]; okk &= np.abs(wrap(qk - kmid * D2R)) <= P["kswing"] * D2R
        R1, t1 = X1; qj = q[:, self.kj]
        dE = self.e0_at(qj - qk) - self.e0_at(qj)
        Delta = dE if self.kj == 0 else np.einsum("nij,nj->ni", R1, dE)
        dl = np.einsum("nji,nj->ni", Q, Delta)
        sv = np.stack([s[:, 0] + dl @ self.sa, s[:, 1] + dl @ self.st, s[:, 2] + dl @ self.sn], 1)
        # in-plane: two circles (J3 line d, radius LE) and (pin b, radius lc)
        LE, lc = P["LE"], P["lc"]; m = np.asarray(P["cuff_m"], float)
        pe, pb = P["phE"] * D2R, (P["phE"] + P["dB"]) * D2R
        Pb = m + LE * np.array([math.cos(pe), math.sin(pe)]) + lc * np.array([math.cos(pb), math.sin(pb)])
        d = sv[:, :2]; Dv = Pb[None] - d; Dn = np.linalg.norm(Dv, axis=1); u_ = Dv / np.maximum(Dn, 1e-9)[:, None]
        a_ = (LE ** 2 - lc ** 2 + Dn ** 2) / (2 * np.maximum(Dn, 1e-9)); h = np.sqrt(np.clip(LE ** 2 - a_ ** 2, 0, None))
        okc = (Dn > abs(LE - lc)) & (Dn < LE + lc)
        A = d + a_[:, None] * u_ + P["cuff_sig"] * h[:, None] * np.stack([-u_[:, 1], u_[:, 0]], 1)
        psi = wrap(np.arctan2(A[:, 1] - d[:, 1], A[:, 0] - d[:, 0]) - pe)
        beta = wrap(np.arctan2(A[:, 1] - Pb[1], A[:, 0] - Pb[0]) - (pb + np.pi))
        ca = np.einsum("ni,ni->n", d - A, Pb[None] - A) / (LE * lc); gam = np.degrees(np.arccos(np.clip(ca, -1, 1)))
        okc &= (gam >= P["gmin"]) & (gam <= 180 - P["gmin"])
        q6 = np.stack([q[:, 0] - (qk if self.kj == 0 else 0), q[:, 1] - (qk if self.kj == 1 else 0), q[:, 2] + psi, qk, beta - psi, beta], 1)
        ok = okf & okk & okc
        why = np.where(~okf, "fold", np.where(~okk, "knuckle", np.where(~okc, "cuff", "")))
        return dict(q=q, q6=q6, ok=ok, why=why, X1=X1, X2=X2, X3=X3, s=s, sv=sv, qk=qk, psi=psi, beta=beta, Delta=Delta,
                    Pb=Pb, gam=gam, auth=authv, kap=kap, okf=okf, Phi=Phi, Lr=Lr)


def design_step(D, Qd):
    """c0, knuckle branch and mid; cuff mid drift and elbow sign - from the fit set (fit clips 10 fps + bench poses)"""
    P = D.p; q, okf, X1, X2, X3, s = D.ik(Qd)
    if P.get("alk_auto"):
        D.set_alk(0.0)
        Phi0, _, _ = D.knuckle_raw(Qd[okf], q[okf], (X1[0][okf], X1[1][okf]), s[okf])     # Phi at alk 0 = q2 - chi
        if not len(Phi0): return False
        med = math.degrees(math.atan2(np.median(np.sin(-Phi0)), np.median(np.cos(-Phi0))))
        D.set_alk(round((med + P["alk_off"] + 180) % 360 - 180, 3))
    Phi, Lr, sn_ = D.knuckle_raw(Qd, q, X1, s)
    Phi, Lr, sn_ = Phi[okf], Lr[okf], sn_[okf]
    if not len(sn_): return False
    cands = []
    for c0 in np.linspace(sn_.min() - 1.6 * P["lk"], sn_.max() + 1.6 * P["lk"], 97):
        kap = (c0 - sn_) / np.maximum(Lr, 1e-9) + np.cos(Phi); okk = np.abs(kap) <= 1
        th = np.arccos(np.clip(kap, -1, 1)); okk &= Lr * np.sin(th) >= P["auth"]
        for sk in (1.0, -1.0):
            qk = wrap(Phi - sk * th)[okk]
            if not len(qk): continue
            qs = np.sort(np.degrees(qk)); j = np.searchsorted(qs, qs + 2 * P["kswing"], side="right")
            cnt = j - np.arange(len(qs)); a = int(np.argmax(cnt)); mid = qs[a] + P["kswing"]
            inw = (qs >= qs[a]) & (qs <= qs[a] + 2 * P["kswing"])
            lo, hi = qs[inw].max() - P["kswing"] + 0.01, qs[inw].min() + P["kswing"] - 0.01
            mid = float(np.clip(0.0, lo, hi)) if lo <= hi else mid                    # same poses, the window centred near 0
            cands.append((int(cnt[a]), float(np.percentile(np.abs(qs[inw]), 95)), float(c0), sk, float(mid)))
    if not cands: return False
    nmax = max(c[0] for c in cands); good = [c for c in cands if c[0] >= nmax - 0.01 * len(sn_)]
    c = min(good, key=lambda c: c[1]); best = (None, c[2], c[3], c[4])     # most poses, then the smallest knuckle swing |qk|
    P["k_c0"], P["k_sk"], P["k_mid"] = round(best[1], 3), best[2], round(best[3], 3)
    if P.get("cuff_m") is None:
        P["cuff_m"] = [0.0, 0.0]; P["cuff_sig"] = 1.0
        K = D.solve(Qd); ok = K["okf"] & (K["why"] != "knuckle")
        sv = K["sv"][ok][:, :2]
        m = 0.5 * (sv.max(0) + sv.min(0)) if len(sv) else np.zeros(2)
        P["cuff_m"] = [round(float(m[0]), 3), round(float(m[1]), 3)]
        pe, pb = P["phE"] * D2R, (P["phE"] + P["dB"]) * D2R
        eE = np.array([math.cos(pe), math.sin(pe)]); eB = np.array([math.cos(pb), math.sin(pb)])
        Pb = m + P["LE"] * eE + P["lc"] * eB; Dv = Pb - m
        P["cuff_sig"] = float(np.sign(Dv[0] * eE[1] - Dv[1] * eE[0]) or 1.0)
    return True


class Model(S.VModel):
    fix = dict(closure=True, hub3rail=True, bridge=True, jam=True, riser=True)
    ADJ = 0.15

    def __init__(self, B, params=None, verbose=False, frozen=None):
        self.B = B; self.v = verbose; self.frozen = frozen
        P = dict(PARAMS); P.update(params or {})
        self.D = Design(P); self.p = self.D.p
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)
        names = list(Z["NAMES"]); self.fit_ii = np.nonzero(np.isin(Z["CID"], [names.index(nm) for nm in CB.FIT]))[0]
        self.design_ok = True
        if self.p.get("k_c0") is None or self.p.get("cuff_m") is None:
            Qd = np.r_[Z["HG"][self.fit_ii].astype(float), self.Q]
            self.design_ok = design_step(self.D, Qd)
        self.why = np.array([""] * len(B.idx), dtype=object)
        if not self.design_ok:
            self.kin_ok = np.zeros(len(B.idx), bool); self.why[:] = "knuckle"; self.res_deg = np.zeros(len(B.idx))
            self.s = np.zeros((len(B.idx), 3)); return
        K = self.D.solve(self.Q); self.K = K
        self.q = K["q6"]; self.X = {1: K["X1"], 2: K["X2"], 3: K["X3"]}; self.s = K["sv"]
        okf = K["ok"].copy(); self.why[:] = K["why"]
        cont = self.continuity(); bad = okf & ~cont; self.why[bad] = "flip"; okf &= cont
        R123 = K["X3"][0]; c = (np.einsum("nij,nij->n", R123, self.Q) - 1) / 2
        self.res_deg = np.degrees(np.arccos(np.clip(c, -1, 1)))
        self.rad_res = np.abs(K["sv"][:, 2] - self.p["k_c0"])
        bad = okf & ((self.res_deg >= 0.5) | (self.rad_res >= 0.5)); self.why[bad] = "closure"; okf &= ~bad
        self.kin_ok = okf
        R3 = rotm(self.D.sn, K["psi"]); self.Rpsi = R3
        self.Rbeta = rotm(self.D.sn, K["beta"])
        self.Pb3 = self.D.c[2] + K["Pb"][0] * self.D.sa + K["Pb"][1] * self.D.st

    def continuity(self):
        """every fit clip at its full 10 fps: a frame fails if any of the 6 joint values jumps > 25 deg from the previous
        taken frame (a branch flip / toggle crossing), or the knuckle / cuff closure fails there"""
        Z = self.Z; names = list(Z["NAMES"]); cid = Z["CID"]; ok_at = {}; self.max_step = 0.0
        for nm in CB.FIT:
            ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            K = self.D.solve(Z["HG"][ii].astype(float)); q, ok = K["q6"], K["ok"]; prev = None
            for j, gi in enumerate(ii):
                good = bool(ok[j])
                if good and prev is not None:
                    dq = np.degrees(np.abs(wrap(q[j] - q[prev]))); self.max_step = max(self.max_step, float(dq.max()))
                    if dq.max() > S.JUMP: good = False
                ok_at[int(gi)] = good; prev = j if ok[j] else None
        return np.array([ok_at.get(int(gi), True) for gi in self.B.idx])

    # members: 0 base, 1 link 1 (+ hub 2 stator), 2 link 2b, 3 rotor (hub 3 plate + E arm), 4 crank, 5 arm (pad), 6 cuff link
    def T(self, m, i):
        D = self.D; K = self.K
        if m == 0: return np.eye(3), np.zeros(3)
        if m == 1: return K["X1"][0][i], K["X1"][1][i] + (K["Delta"][i] if D.kj == 0 else 0.0)
        if m == 2: return K["X2"][0][i], K["X2"][1][i] + K["Delta"][i]
        if m == 3:
            R, t = K["X3"][0][i], K["X3"][1][i] + K["Delta"][i]; Rp = self.Rpsi[i]; c3 = D.c[2]
            return R @ Rp, R @ (c3 - Rp @ c3) + t
        if m == 4:
            Rk = rotm(D.ku, K["q"][i, D.kj] - K["qk"][i])[0]; ck = D.kc
            if D.kj == 0: return Rk, ck - Rk @ ck
            R1, t1 = K["X1"][0][i], K["X1"][1][i]
            return R1 @ Rk, R1 @ (ck - Rk @ ck) + t1
        Q = self.Q[i]
        if m == 5: return Q, np.zeros(3)
        if m == 6: Rb = self.Rbeta[i]; return Q @ Rb, Q @ (self.Pb3 - Rb @ self.Pb3)
        raise ValueError(m)

    # ---- geometry (member-local rest coordinates; a group = base points B + height along N) ----
    def groups(self):
        D = self.D; u, c = D.u, D.c; P = self.p; sa, st, sn = D.sa, D.st, D.sn; G = []
        for k, mem in ((0, 0), (1, 1)):
            e, f = frame_of(u[k]); d = disc(HUB_R); B = c[k][None] + d[:, :1] * e + d[:, 1:] * f
            G.append(dict(name=f"hub{k + 1}", mem=mem, B=B, N=u[k]))
        e3, f3 = frame_of(sn); d = disc(HUB_R)
        G.append(dict(name="hub3", mem=3, B=c[2][None] + d[:, :1] * e3 + d[:, 1:] * f3, N=sn, sh="h3"))
        G.append(dict(name="Earm", mem=3, B=self.plate(c[2], D.eE, P["LE"], sn, start=HUB_R), N=sn))
        e2, f2 = frame_of(D.ku); n_r = int(2 * np.pi * BOSS_R / SP); ang = np.arange(n_r) * 2 * np.pi / n_r
        dd = np.r_[disc(BOSS_R), (BOSS_R - 0.25) * np.stack([np.cos(ang), np.sin(ang)], 1)]
        if P.get("crank_strap"): G.append(dict(name="crank", mem=4, B=D.kc + D.e0 + dd[:, :1] * e2 + dd[:, 1:] * f2, N=D.ku))   # the knuckle boss (flat, O12)
        else: G.append(dict(name="crank", mem=4, B=self.plate(D.kc, D.ek, P["lk"], D.ku, start=HUB_R), N=D.ku))           # flat crank + boss
        pa0 = self.Pb3 - P["lc"] * D.eB
        G.append(dict(name="clink", mem=6, B=self.plate(self.Pb3, -D.eB, P["lc"], sn, start=-BOSS_R), N=sn))
        r = rect(PAD, PAD); G.append(dict(name="pad", mem=5, B=self.Pb3[None] + r[:, :1] * sa + r[:, 1:] * st, N=sn))
        for g in G: g["N"] = np.broadcast_to(g["N"], g["B"].shape).copy()
        self._pa0 = pa0
        return G

    @staticmethod
    def plate(o, ev, L, n, start=0.0):
        """flat 8 mm strap in the plane normal to n from o + start ev to o + L ev, + an O12 boss at o + L ev (2 mm grid)"""
        ew = np.cross(n, ev); x = np.arange(start + SP / 2, L, SP); y = np.arange(-W_LINK / 2 + SP / 2, W_LINK / 2, SP)
        X, Y = np.meshgrid(x, y); pts = [o + X.ravel()[:, None] * ev + Y.ravel()[:, None] * ew]
        dd = disc(BOSS_R); n_r = int(2 * np.pi * BOSS_R / SP); ang = np.arange(n_r) * 2 * np.pi / n_r
        dd = np.r_[dd, (BOSS_R - 0.25) * np.stack([np.cos(ang), np.sin(ang)], 1)]      # + the boss rim (its wall is skin-checked)
        dd = dd[(dd[:, 0] > 0) | (np.abs(dd[:, 1]) > W_LINK / 2)]
        pts.append(o + (L + dd[:, :1]) * ev + dd[:, 1:] * ew)
        return np.concatenate(pts)

    def strap_rows(self, Ca, Cb, excl):
        """the seed's link strap: great-circle rows (4 across, 2 mm) between the directions of Ca and Cb at their mean
        radius; samples within an exclusion (line point, axis, radius) are left to the hub / boss"""
        da, db = unit(Ca), unit(Cb); R = 0.5 * (np.linalg.norm(Ca) + np.linalg.norm(Cb))
        ang = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db))
        n = max(4, int(R * ang / SP)); ts = (np.arange(n) + 0.5) / n
        dirs = np.array([unit(math.sin((1 - t) * ang) * da + math.sin(t * ang) * db) for t in ts]); rows = []
        for v in (-3.0, -1.0, 1.0, 3.0):
            dv = unit(dirs + (v / R) * bn); pts = R * dv; keep = np.ones(len(dv), bool)
            for (p0, ax, rr) in excl:
                w = pts - p0; keep &= np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > rr
            rows.append((dv, keep, ts * R * ang))
        return rows

    def fit(self):
        D = self.D; u, c = D.u, D.c
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        G = self.groups(); self.G = G
        res = self.needed([(g["mem"], g["B"], g["N"], 140.0) for g in G], poses)
        H = {g["name"]: r for g, r in zip(G, res)}
        H["h3"] = H["hub3"]
        self.Hneed = H; self.Lneed = {}; self.gnames = ["hub1", "hub2", "h3", "Earm", "crank", "clink", "pad"]
        self.greedy_drop(links=False); keep1 = ~self.drop
        hh = self._levels(keep1)
        j, ku, kc = D.kj, D.ku, D.kc; hn = ("hub1", "hub2")[j]; kb = kc + D.e0
        Kp = kb + (hh["crank"] + T_LINK + S.RUN * 0.3) * ku
        C1 = c[0] + hh["hub1"] * u[0]; C2 = c[1] + hh["hub2"] * u[1]; C3 = c[2] + hh["h3"] * u[2]
        Ku = kc + (hh[hn] + UP) * ku; Kb = kb + hh["crank"] * ku
        crankL = ([dict(name="crankL", mem=4, rows=self.strap_rows(Ku, Kb, [(kc, ku, HUB_R), (kb, ku, BOSS_R)]),
                        ends=[(kc, ku, UP, hn), (kb, ku, 0.0, "crank")])] if self.p.get("crank_strap") else [])
        if j == 1:
            self.links = crankL + [
                      dict(name="L1", mem=1, rows=self.strap_rows(C1, C2, [(c[0], u[0], HUB_R), (c[1], u[1], HUB_R)]),
                           ends=[(c[0], u[0], 0.0, "hub1"), (c[1], u[1], 0.0, "hub2")]),
                      dict(name="L2", mem=2, rows=self.strap_rows(Kp, C3, [(kb, ku, BOSS_R), (c[2], u[2], HUB_R)]),
                           ends=[(kb, ku, T_LINK + 0.15, "crank"), (c[2], u[2], UP, "h3")])]
        else:                                                   # J1 knuckle: link 1b laps over the boss, link 2 as the leader's
            self.links = crankL + [
                      dict(name="L1", mem=1, rows=self.strap_rows(Kp, C2, [(kb, ku, BOSS_R), (c[1], u[1], HUB_R)]),
                           ends=[(kb, ku, T_LINK + 0.15, "crank"), (c[1], u[1], 0.0, "hub2")]),
                      dict(name="L2", mem=2, rows=self.strap_rows(c[1] + (hh["hub2"] + UP) * u[1], C3, [(c[1], u[1], HUB_R), (c[2], u[2], HUB_R)]),
                           ends=[(c[1], u[1], UP, "hub2"), (c[2], u[2], UP, "h3")])]
        items, idx = [], []
        for lk in self.links:
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0)); idx.append((lk["name"], ri))
        res = self.needed(items, poses); L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        self.Lneed = L
        self.greedy_drop(keep0=keep1)
        self.finalize()

    def _levels(self, keep):
        H = self.Hneed; m = lambda k: float(H[k][keep].max()) if keep.any() else 0.0
        f1, f2, f3 = m("hub1"), m("hub2"), m("h3")
        fk = f1 if self.D.kj == 0 else f2
        zc = m("crank") if self.p.get("crank_strap") else max(fk + UP, m("crank")); zp = m("pad"); nl = max(m("clink"), zp + UP)
        zE = m("Earm")                                         # the E arm: its own flat level, a step (riser) at hub 3's rim
        fa = zE + self.p["k_c0"]                               # the E arm's level in the ARM frame (member 3 rides c0 along sn)
        zl = nl if nl <= fa - UP else max(nl, fa + UP)         # pin a: the cuff link passes under the E arm or over it
        return dict(hub1=f1, hub2=f2, h3=f3, Earm=zE, crank=zc, pad=zp, clink=zl)

    def greedy_drop(self, keep0=None, links=True):
        """the seed's greedy pose dropping (S.Model.greedy_drop), on this model's flat parts (each its own shared height)"""
        poses = self.poses_fit; kind = np.array([self.B.kind[i] for i in poses])
        ncl = sum(1 for k in self.B.kind if k == "clip"); nws = len(self.B.kind) - ncl
        H, L = self.Hneed, self.Lneed
        groups = [("g", H[k]) for k in self.gnames] + ([("s", r) for rows in L.values() for r in rows] if links else [])
        keep = np.ones(len(poses), bool) if keep0 is None else keep0.copy()
        for typ, M in groups: keep &= ~(M >= S.BIG / 2).any(1)
        def score(keep):
            if not keep.any(): return 1e9
            cl = keep & (kind == "clip"); inb = tot = 0
            for typ, M in groups:
                top = M[keep].max() if typ == "g" else M[keep].max(0); ex = top - M[cl]
                inb += float((ex <= 12.0).sum()); tot += ex.size
            ib = inb / max(tot, 1); fol = cl.sum() / ncl; rch = (keep & (kind == "ws")).sum() / nws
            return 100 * (max(0, .9 - ib) + max(0, .95 - fol) + max(0, .9 - rch)) + 100 * (~keep).sum() / len(keep)
        cur = score(keep)
        for it in range(60 if self.p.get("drop", 1) else 0):
            best, bk = cur, None
            for typ, M in groups:
                order = np.argsort(-np.where(keep, M.max(1), -1e9))
                for k in range(1, 9):
                    sel = order[:k]; sel = sel[keep[sel]]
                    if not len(sel): continue
                    k2 = keep.copy(); k2[sel] = False; sc = score(k2)
                    if sc < best - 1e-6: best, bk = sc, k2
            if bk is None: break
            keep = bk; cur = best
        self.drop = ~keep

    def finalize(self):
        keep = ~self.drop; D = self.D; u, c = D.u, D.c
        lv = self._levels(keep); self.lv = lv
        self.f = [lv["hub1"], lv["hub2"], lv["h3"]]; self.tr = lv["pad"]; self.zb = lv["clink"]
        rL = {k: [r[keep].max(0) for r in rows] for k, rows in self.Lneed.items()}
        kk = math.tan(S.RAMP * D2R); self.link_pts = {}
        for lk in self.links:
            pts_all = []
            for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
                r = r.copy(); Sx = sarc; idx = np.nonzero(keep_s)[0]
                if not len(idx): continue
                for end, (p0, ax, dz, lvn) in zip((0, -1), lk["ends"]):
                    j = idx[0] if end == 0 else idx[-1]
                    den = float(dv[j] @ ax); rc = (p0 @ ax + lv[lvn] + dz) / max(den, 0.2)
                    r = np.maximum(r, rc - kk * np.abs(Sx - Sx[j]))
                r = np.max(r[None, :] - kk * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
                pts_all.append(dv[keep_s] * r[keep_s][:, None])
            self.link_pts[lk["name"]] = (lk["mem"], np.concatenate(pts_all) if pts_all else np.zeros((0, 3)))
        hmap = dict(hub1=lv["hub1"], hub2=lv["hub2"], hub3=lv["h3"], Earm=lv["Earm"], crank=lv["crank"], clink=lv["clink"], pad=lv["pad"])
        self.rigid = {g["name"]: (g["mem"], g["B"] + hmap[g["name"]] * g["N"]) for g in self.G}
        self._contact_only(); self._solids(); self.riser = None; self.riser_h = 0.0

    def _contact_only(self):
        """hub side walls + crowns, plate / strap tops, pin bosses and heads: checked for skin contact (not scored)"""
        D = self.D; u, c = D.u, D.c; F = self.f; lv = self.lv; out = []
        ang = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        def cyl(mem, o, ax, r, z0, z1, cap=True):
            e, f = frame_of(ax); ring = r * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
            for z in np.linspace(z0, z1, max(2, int((z1 - z0) / 3) + 1)): out.append((mem, o + z * ax + ring))
            if cap: dd = disc(r, 2.0); out.append((mem, o + z1 * ax + dd[:, :1] * e + dd[:, 1:] * f))
        for k, mem in ((0, 0), (1, 1), (2, 3)): cyl(mem, c[k], u[k], HUB_R, F[k], F[k] + CROWN)
        sn = D.sn
        cyl(4, D.kc + D.e0, D.ku, BOSS_R, lv["crank"], lv["crank"] + 2 * T_LINK + 0.15 + PIN_HEAD)                   # knuckle pin
        pa = c[2] + self.p["LE"] * D.eE
        zl3 = lv["clink"] - self.p["k_c0"]                                                                            # link level in member 3's frame
        cyl(3, pa, sn, BOSS_R, min(lv["Earm"], zl3), max(lv["Earm"], zl3) + T_LINK + PIN_HEAD)                         # pin a
        lo, hi = min(lv["h3"], lv["Earm"]), max(lv["h3"], lv["Earm"]) + T_LINK                                       # E-arm riser at hub 3's rim
        if hi - lo > T_LINK + 0.5:
            ew = np.cross(sn, D.eE); g = np.stack(np.meshgrid(np.linspace(-W_LINK / 2, W_LINK / 2, 5), np.arange(lo, hi + 0.1, 2.0), indexing="ij"), -1).reshape(-1, 2)
            for x in (HUB_R, HUB_R + T_LINK): out.append((3, c[2] + x * D.eE + g[:, :1] * ew + g[:, 1:] * sn))

        cyl(5, self.Pb3, sn, BOSS_R, lv["pad"], lv["clink"] + T_LINK + PIN_HEAD)                                      # pin b (+ standoff)
        for nm in ("crank", "clink", "pad", "Earm"):
            mem, X = self.rigid[nm]; out.append((mem, X + T_LINK * self.G[[g["name"] for g in self.G].index(nm)]["N"]))
        for nm, (mem, X) in self.link_pts.items():
            if len(X): out.append((mem, X + T_LINK * unit(X)))
        self.contact = out

    def _solids(self):
        D = self.D; u, c = D.u, D.c; F = self.f
        self.cyl = {"hub1": (0, c[0] + F[0] * u[0], u[0]), "hub2": (1, c[1] + F[1] * u[1], u[1]), "hub3": (3, c[2] + F[2] * u[2], u[2])}
        self.box = {}
        self.strap = {nm: (mem, X + (T_LINK / 2) * unit(X)) for nm, (mem, X) in self.link_pts.items()}
        gi = {g["name"]: g for g in self.G}
        for nm in ("crank", "Earm", "clink", "pad"):
            mem, X = self.rigid[nm]; self.strap[nm] = (mem, X + (T_LINK / 2) * gi[nm]["N"])
        ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); self.cyl_surf = {}
        for nm, (mem, cen, ax) in self.cyl.items():
            e, f = frame_of(ax); pts = [cen + z * ax + HUB_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, CROWN, 5)]
            dd = disc(HUB_R, 4.0); pts.append(cen + CROWN * ax + dd[:, :1] * e + dd[:, 1:] * f)
            self.cyl_surf[nm] = (mem, np.concatenate(pts))

    # pairs: (a, b, required clearance); adjacent members of one joint get the running gap
    NONADJ = [("crankL", "hub1"), ("crankL", "hub3"), ("crankL", "Earm"), ("crankL", "clink"), ("crankL", "pad"), ("L2", "hub1"), ("L2", "hub2"), ("L2", "L1"), ("L2", "clink"), ("L2", "pad"),
              ("crank", "hub1"), ("crank", "hub3"), ("crank", "Earm"), ("crank", "clink"), ("crank", "pad"),
              ("hub3", "hub1"), ("hub3", "hub2"), ("Earm", "hub1"), ("Earm", "hub2"), ("Earm", "L1"), ("Earm", "pad"),
              ("clink", "hub1"), ("clink", "hub2"), ("clink", "hub3"), ("clink", "L1"),
              ("pad", "hub1"), ("pad", "hub2"), ("pad", "hub3"), ("pad", "L1"), ("hub3", "L1")]
    ADJP = [("L2", "Earm"), ("crank", "L1"), ("crankL", "L1"), ("L2", "crankL")]
    # J1 knuckle: the crank rides hub 1's rotor (adjacent to the scapula and to link 1b at the pin); everything else non-adjacent
    NONADJ1 = [("crankL", "hub2"), ("crankL", "L2"), ("crankL", "hub3"), ("crankL", "Earm"), ("crankL", "clink"), ("crankL", "pad"),
               ("crank", "hub2"), ("crank", "L2"), ("crank", "hub3"), ("crank", "Earm"), ("crank", "clink"), ("crank", "pad"),
               ("L2", "hub1"), ("L2", "L1"), ("L2", "clink"), ("L2", "pad"), ("hub3", "hub1"), ("hub3", "hub2"), ("Earm", "hub1"),
               ("Earm", "hub2"), ("Earm", "L1"), ("Earm", "pad"), ("clink", "hub1"), ("clink", "hub2"), ("clink", "hub3"), ("clink", "L1"),
               ("pad", "hub1"), ("pad", "hub2"), ("pad", "hub3"), ("pad", "L1"), ("hub3", "L1"), ("L1", "hub1"), ("hub2", "hub1")]
    ADJP1 = [("L2", "Earm"), ("L1", "crankL"), ("L1", "crank")]

    def collide(self, i):
        D = self.D
        def tf(m, P): R, t = self.T(m, i); return P @ R.T + t
        cylw = {k: (tf(m, cen[None])[0], self.T(m, i)[0] @ ax) for k, (m, cen, ax) in self.cyl.items()}
        cylw["knuckle"] = (tf(4, (D.kc + D.e0)[None])[0], self.T(4, i)[0] @ D.ku)
        surf = {k: tf(m, P) for k, (m, P) in self.cyl_surf.items()}
        sl = {k: tf(m, P) for k, (m, P) in self.strap.items()}
        h = T_LINK / 2
        # parts exempt near their shared joint: L1 / L2 / crank around hub 2's axis, L2 / E arm around hub 3's axis
        def away(P, k, r):
            cen, ax = cylw[k]; w = P - cen; return P[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > r]
        def clr(a, b):
            if any(x not in sl and x not in self.cyl for x in (a, b)): return 1e9      # part absent in this variant
            A = sl.get(a); Bp = sl.get(b)
            if a == "L2" and b in ("L1",): A = away(A, "hub2", HUB_R + 4); Bp = away(Bp, "hub2", HUB_R + 4)
            if (a, b) in (("crank", "L1"), ("crankL", "L1")): A = away(A, "hub2", HUB_R + 2); Bp = away(Bp, "hub2", HUB_R + 2)
            if (a, b) in (("L2", "crankL"), ("L1", "crankL"), ("L1", "crank")): A = away(A, "knuckle", BOSS_R + 2); Bp = away(Bp, "knuckle", BOSS_R + 2)
            if (a, b) == ("L1", "hub1"): A = away(A, "knuckle", BOSS_R + 2)
            if (a, b) == ("L2", "Earm"): A = away(A, "hub3", HUB_R + 2); Bp = away(Bp, "hub3", HUB_R + 2)
            if a in self.cyl and b not in self.cyl: a, b = b, a; A, Bp = sl.get(a), None
            if a in self.cyl and b in self.cyl:
                cen, ax = cylw[b]; return float(self.sd_cyl(surf[a], cen, ax).min())
            if b in self.cyl:
                if A is None or not len(A): return 1e9
                cen, ax = cylw[b]; return float(self.sd_cyl(A, cen, ax).min()) - h
            if A is None or Bp is None or not len(A) or not len(Bp): return 1e9
            return float(cKDTree(Bp).query(A)[0].min()) - 2 * h
        out = {}; na, ap = (self.NONADJ, self.ADJP) if D.kj == 1 else (self.NONADJ1, self.ADJP1)
        for a, b in na: out[f"{a}-{b}"] = clr(a, b)
        adj = {f"{a}-{b}": clr(a, b) for a, b in ap}
        self.last_clear = {k: round(v, 1) for k, v in {**out, **adj}.items()}
        m = min(out.values())
        if min(adj.values()) < self.ADJ: m = min(m, -1.0)
        return m

    def run(self, B=None):
        if not self.design_ok:
            self.B.reset()
            for i in range(len(self.B.idx)): self.B.record(i, None)
            r = self.B.report(); r["why"] = {"knuckle": len(self.B.idx)}; return r
        if not self.kin_ok.any():
            self.B.reset()
            for i in range(len(self.B.idx)): self.B.record(i, None)
            r = self.B.report(); r["why"] = {k: int((self.why == k).sum()) for k in ("fold", "knuckle", "cuff", "flip", "closure")}; return r
        r = S.VModel.run(self)
        r["why"] = {k: int((self.why == k).sum()) for k in ("fold", "knuckle", "cuff", "flip", "closure", "skin", "parts", "contact")}
        K = self.K; ok = self.kin_ok
        if ok.any():
            r["knuckle"] = dict(c0=self.p["k_c0"], sk=self.p["k_sk"], mid=self.p["k_mid"],
                                qk_deg=[round(float(np.degrees(K["qk"][ok]).min()), 1), round(float(np.degrees(K["qk"][ok]).max()), 1)],
                                auth_p1=round(float(np.percentile(K["auth"][ok], 1)), 1))
            r["cuff"] = dict(m=self.p["cuff_m"], sig=self.p["cuff_sig"], elbow_deg=[round(float(K["gam"][ok].min()), 1), round(float(K["gam"][ok].max()), 1)],
                             psi_deg=[round(float(np.degrees(K["psi"][ok]).min()), 1), round(float(np.degrees(K["psi"][ok]).max()), 1)],
                             drift_span=[round(float(np.ptp(K["sv"][ok][:, j])), 1) for j in range(3)])
            r["rad_res_max"] = round(float(self.rad_res[ok].max()), 4)
        r["levels"] = {k: round(v, 1) for k, v in self.lv.items()}
        r["max_step_deg"] = round(self.max_step, 1)
        r["seats"] = dict(tilt_deg=self.D.seats["tilt_deg"], a_deg=[round(math.degrees(a), 1) for a in self.D.A],
                          offset_mm=[round(float(np.linalg.norm(cc)), 1) for cc in self.D.c])
        r["passive_translations"] = 0
        return r


class Frozen(Model):
    """wear the shape fitted by model M1 (another bench) without refit: heights, link shapes, design-step values"""
    def __init__(self, B, M1):
        super().__init__(B, dict(M1.p)); self.M1 = M1

    def fit(self):
        M1 = self.M1
        for a in ("G", "links", "lv", "f", "tr", "zb", "rigid", "link_pts", "contact", "cyl", "box", "strap", "cyl_surf", "_pa0"):
            setattr(self, a, getattr(M1, a))
        self.riser = None; self.riser_h = 0.0
        self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)


def _report(B, params):
    M = Model(B, params); r = M.run(); return r, M


def evaluate(B, params):
    """tools/concept_cma.py hook: (params incl. design-step outputs, report)"""
    P = dict(PARAMS); P.update(params)
    for k in ("k_c0", "k_sk", "k_mid", "cuff_m", "cuff_sig"): P[k] = None
    if P.get("alk_auto"): P["alk"] = None
    P["lk"] = max(float(P["lk"]), HUB_R + BOSS_R + 1.0)          # the knuckle boss clears hub 2's cap
    P["LE"] = max(float(P["LE"]), HUB_R + BOSS_R + 2.0); P["lc"] = max(float(P["lc"]), 2 * BOSS_R + 2.0)
    for k in ("b1", "b2", "b3"): P[k] = min(1.2, max(-0.2, float(P[k])))
    r, M = _report(B, P)
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool, list)) or v is None}
    r["honest"] = True; r["audit"] = []
    return p, r


def bench_eval(B, params):
    """tools/concept_sweep.py hook"""
    p, r = evaluate(B, params); r.pop("params", None); r["design"] = {k: p.get(k) for k in ("k_c0", "k_sk", "k_mid", "cuff_m", "cuff_sig")}
    return r


def redteam(B, M, r):
    lab = lambda i: f"#{i} {B.kind[i]} {B.clip[i][:22]:22s} plane {B.poses[i]['plane']:6.1f} elev {B.poses[i]['elev']:6.1f} axial {B.poses[i]['axial']:6.1f}"
    taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
    print("-- poses not taken (why) --")
    for w in ("parts", "contact", "skin", "flip", "cuff", "knuckle", "closure"):
        ii = [i for i in range(len(B.idx)) if M.why[i] == w]
        if ii: print(f"  {w:8s} {len(ii):3d}: " + "; ".join(lab(i) + (f" [{M.last_pair.get(i)} {M.clear[i]:.1f}]" if w == "parts" else "") for i in ii[:4]))
    low = []
    for i in range(len(B.idx)):
        if not taken(i): continue
        cw = np.concatenate([M.world(m, i, Pc) for m, Pc in M.contact]); dc = B.dist(i, cw)
        low.append((min(float(np.min(B.res[i])), float(dc.min())), i))
    low.sort(); print("-- lowest metal over taken poses (incl. walls, crowns, tops, pin heads) --")
    for d, i in low[:6]: print(f"  {d:5.2f} mm  {lab(i)}")
    near1 = sum(1 for d, i in low if d < 1.0)
    res0 = list(B.res)
    for d, i in low:
        if d < 1.0: B.res[i] = np.r_[B.res[i], -1e-3]
    rn = B.report(); B.res = res0
    print(f"near-touch: min {low[0][0] if low else None:.2f} mm, {near1} poses < 1 mm -> gap {rn['gap']}")
    el = np.array([p["elev"] for p in B.poses]); pl = np.array([p["plane"] for p in B.poses]); kind = np.array(B.kind)
    groups = dict(rest=np.argsort(el)[:5], overhead140=np.nonzero(el >= 140)[0], across=np.nonzero((pl >= 100) & (el >= 40))[0],
                  behind=np.array([i for i in range(len(B.idx)) if "back" in B.clip[i].lower() or (pl[i] < -30 and el[i] > 20)], int))
    print("-- named groups: taken/total, reach(ws), median mm, ib14, ib10 --")
    out = {}
    for g, ii in groups.items():
        ii = list(ii); tk = [i for i in ii if taken(i)]; dd = np.concatenate([B.res[i] for i in tk]) if tk else np.array([np.nan])
        ws = [i for i in ii if kind[i] == "ws"]
        out[g] = dict(taken=len(tk), total=len(ii), reach=round(float(np.mean([taken(i) for i in ws])), 3) if ws else None,
                      ib14=round(float(((dd >= 2) & (dd <= 14)).mean()), 3), ib10=round(float(((dd >= 2) & (dd <= 10)).mean()), 3))
        print(f"  {g:12s} {len(tk)}/{len(ii)} reach {out[g]['reach']} median {float(np.nanmedian(dd)):.1f} ib14 {out[g]['ib14']} ib10 {out[g]['ib10']}  not: {[(int(i), M.why[i]) for i in ii if not taken(i)][:6]}")
    return dict(near_min=round(low[0][0], 2) if low else None, near1_poses=near1, gap_near1=rn["gap"], groups=out)


def frozen(par, out_path, nc=110, nw=360):
    """lesson (c): fit on Bench(60,160) FAST, wear the shape FROZEN (no refit) on Bench(nc, nw) (exact when CB_EXACT=1),
    red-team groups + near-touch on the frozen run; JSON to out_path"""
    t0 = time.time(); keys = ("gap", "reach", "follow", "inband14", "inband10", "contact"); out = dict(params=par)
    ex = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    p1, r1 = evaluate(B1, par); M1 = Model(B1, p1); r1b = M1.run()
    out["fit60_fast"] = {k: r1b[k] for k in keys}; out["fit60_fast"]["why"] = r1b["why"]
    out["design"] = {k: p1.get(k) for k in ("alk", "k_c0", "k_sk", "k_mid", "cuff_m", "cuff_sig")}; out["params_full"] = p1
    print("fit60", out["fit60_fast"], flush=True)
    B2 = CB.Bench(n_clip=nc, n_ws=nw); M2 = Frozen(B2, M1); r2 = M2.run()
    out["frozen_big"] = {k: r2[k] for k in keys}; out["frozen_big"].update(mode=B2.mode, why=r2["why"], parts=r2.get("parts_ib14"), pairs=r2.get("parts_pairs"),
                                                                          knuckle=r2.get("knuckle"), cuff=r2.get("cuff"))
    print("frozen", B2.mode, out["frozen_big"], flush=True)
    out["frozen_redteam"] = redteam(B2, M2, r2); out["secs"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    json.dump(out, open(out_path, "w"), indent=1, default=float); print("done", out["secs"], flush=True)
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "frozen":
        frozen(par, sys.argv[3]); sys.exit(0)
    nc, nw = (110, 360) if "--big" in sys.argv else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    p, r = evaluate(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, B.mode, f"{time.time() - t:.0f}s")
    print("why", r["why"], "\nknuckle", r.get("knuckle"), "\ncuff", r.get("cuff"), "\nlevels", r.get("levels"), "seats", r.get("seats"),
          "\nparts", r.get("parts_ib14"), "\npairs", r.get("parts_pairs"), "min clear", r.get("min_clear_taken"), "res", r.get("res_max"),
          "rad", r.get("rad_res_max"), "step", r.get("max_step_deg"))
    if mode == "redteam":
        M = Model(B, p); M.run(); redteam(B, M, r)
