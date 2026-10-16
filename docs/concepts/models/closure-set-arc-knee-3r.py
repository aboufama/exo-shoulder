"""Concept model: CLOSURE-SET ARC KNEE 3R (id closure-set-arc-knee-3r).

Chain: scapula -> J1 (O20 hub, ACTIVE R) -> link 1 -> J2 (O20 hub, ACTIVE R) -> link 2 ending in a FORK -> K (PASSIVE R:
two coaxial trunnion pins, axis dK = u2 x u3 through hub 3's housing) -> yoke = hub-3 housing -> J3 (ACTIVE R, line
offset from GH) -> E arm -> pin a (PASSIVE R, axis // u3) -> cuff link -> pin b (PASSIVE R, axis // u3) -> arm pad on the
cuff (arm-fixed). 0 passive translations, 3 passive rotations. Loop mobility (Grubler, arm closed by the GH ball):
6 (7 - 1 - 7) + 6 + 3 = 3 = the arm's DOF; psi (knee), pa, pb are set by the closure, none sags (R17).

How the closure sets the knee (derived here, measured in `kin`): the pin dyad J3-a-b is a planar 3R in the plane
normal to u3, so it absorbs the in-plane drift and the in-plane rotation; the yoke must match the arm's u3 direction
(2 equations) and the arm pad's height along u3 (1 equation, the RADIAL closure): 3 equations for q1, q2, psi.
rad(psi) = c3 . RK(psi) u3 + hK (cos psi - 1) + t2(q(psi)) . w, with t2 the J1/J2 line-offset drift. If lines 1 and 2
pass through GH (t2 = 0, the osn leader's exact subfamily b1 = b2 = 0) rad does not depend on the pose and psi is a
CONSTANT: the knee is inert. The knee only moves through the J1/J2 offsets (b1, b2 > 0), at an authority
d rad / d psi = c3 . (dK x u3) (the J3 line's offset toward J2) at psi 0.

Built on the osn model (docs/concepts/models/offset-skin-normal-3r.py: its seats, its S.VModel checks: closure, jam rule,
hub-hub and hub-strap clearance, fitted undersides with <= 60 deg ramps, greedy drop as contact) with slides=0 (no stage)
and these members added at real size: yoke = hub-3 housing (O20 x 12.25, tilting with psi), fork cheeks on link 2
(3 x 8 x 12.25 at +-13 mm along dK, the trunnions MR63ZZ pairs / O4 pins in IGLIDUR sleeves), E arm (8 x 3 strap from the
hub boss to pin a + O10 eye), cuff link (8 x 3 strap pin a -> pin b, O10 eyes, under the E arm at pin a), arm pad boss
(O10 x 3 under the cuff link at pin b, arm-fixed). Stack at pin a: cuff link under the E arm (0.15 running gap); at pin
b: pad boss under the cuff link; the E arm leaves hub 3's upper member at >= F + 3.15.

Knee root per pose: 1 deg psi grid over +-pmax + linear root + exact re-evaluation (closure residual reported, < 0.5 mm /
0.5 deg required). FIT clips are TRACKED at their full 10 fps from the clip's first frame (root nearest the previous
frame; a step > JUMP deg of psi, q1, q2, q3, pa or pb = a branch jump the knee cannot make -> frame not followed);
workspace poses take the root nearest psi_rest (the rest pose's knee). ok also needs: fold-free (>= 10 deg) at the
root, |d rad / d psi| >= auth_min mm/rad (conditioning), |psi| <= pmax - 0.5, dyad elbow in [bmin, 180 - bmin].

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/closure-set-arc-knee-3r.py [check|kin|redteam] ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("osn_for_csak", os.path.join(HERE, "offset-skin-normal-3r.py"))
OSN = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(OSN)
S = OSN.S; unit = S.unit; rotm = S.rotm; D2R = math.pi / 180
ID = "closure-set-arc-knee-3r"
NAME = "Closure-set arc knee: hub 3 on a passive trunnion yoke set by the radial closure, pinned cuff dyad"
HUB_R, CROWN, UP, T_LINK, W_LINK = S.HUB_R, S.CROWN, S.UP, S.T_LINK, S.W_LINK
EYE_R, PAD_T, GAP, CHEEK, ARM_R, PINB_MIN = 5.0, 3.0, 0.2, 3.0, HUB_R + 5.0, 20.0   # GAP: stack gap (>= the 0.15 running clearance)

PARAMS = dict(OSN.PARAMS)
PARAMS.update(slides=0, remote=0, ramp=0, inv=0, vfix=1, jam_contact=1, drop=1,
              az1=94.61, el1=60.68, b1=0.34, az2=24.06, el2=48.54, b2=0.42, wd=75.16, wa=-13.04, b3=0.21,  # snh k722 seats
              dh=8.0,          # K line height above hub 3's seat point (mm along u3; mid-stack ~ face + 6.1)
              psi_rest=0.0,    # knee angle at the rest pose (deg) - sets the arm pad height c0
              pmax=40.0, auth_min=8.0,
              lE=22.0, lc=22.0, phiE=0.0, beta0=90.0, bmin=20.0,   # dyad: E arm, cuff link (mm), rest E-arm direction
              jumpk=25.0, toff=6.1, earm_over=0,
              o2=0.0, chi2=0.0,   # CAM: extra offset of J2's line (mm, normal to u2) and its direction (deg from the u2-u3 plane);
                                  #   with J1 through GH the radial closure is F(q2, psi) = 0: the knee is a cam of the elbow q2
              earm_under=0,    # 1: the E arm IS hub 3's lower plate (F..F+3, J3's output), the yoke = the upper housing with the
                               #    trunnions at F + toff >= F + 7 so the cheeks clear the E arm by 1 mm (no stack lifted)
              lock=0)          # 1: CONTROL - knee locked at psi_rest (hub 3 rigid on link 2, no fork): a 3R + pin dyad, the
                               #    radial closure must hold by itself (|rad - c0| < 0.5 mm, exact iff b1 = b2 = 0)                                # toff: trunnion axis height above hub 3's face (mm)                                          # (deg, 0 = distal along the humerus), rest elbow (deg)


def rodrigues(U, a):
    """per-row axis U (n,3), angle a (n,) -> (n,3,3)"""
    U = unit(U); K = np.zeros((len(U), 3, 3))
    K[:, 0, 1], K[:, 0, 2], K[:, 1, 0], K[:, 1, 2], K[:, 2, 0], K[:, 2, 1] = -U[:, 2], U[:, 1], U[:, 2], -U[:, 0], -U[:, 1], U[:, 0]
    s, c = np.sin(a)[:, None, None], np.cos(a)[:, None, None]
    return np.eye(3)[None] + s * K + (1 - c) * (K @ K)


class Design(OSN.Design):
    def __init__(self, params=None):
        self._knee = False
        P0 = dict(PARAMS, **(params or {}))                          # clamp to the buildable ranges (CMA steps outside)
        for k, lo, hi in (("b1", 0, 1), ("b2", 0, 1), ("b3", 0, 1), ("lE", 12, 40), ("lc", 12, 40), ("beta0", 35, 145),
                          ("toff", 1.5, CROWN - 1.5), ("pmax", 20, 60), ("psi_rest", -50, 50), ("o2", 0, 30)):
            P0[k] = float(min(hi, max(lo, P0[k])))
        if P0.get("earm_under"): P0["toff"] = float(min(CROWN - 1.5, max(T_LINK + 1.0 + CHEEK, P0["toff"])))
        super().__init__(P0)
        P = self.p; u1, u2, u3 = self.u
        self.dK = unit(np.cross(u2, u3))
        R = OSN.rest(); Q0 = R["Q0"]
        if P.get("o2", 0.0):                                         # CAM: J2's line moved o2 mm off its seat line, normal to u2,
            m = unit(u3 - (u3 @ u2) * u2)                            # at chi2 from the u2-u3 plane; J3's line re-seated after it
            self.c[1] = self.c[1] + P["o2"] * (math.cos(P["chi2"] * D2R) * m + math.sin(P["chi2"] * D2R) * self.dK)
            _, _, _, X2, _, _ = S.Design.ik(self, Q0[None]); R12, tt2 = X2[0][0], X2[1][0]
            self.c[2] = OSN.foot(R12.T @ (self.seats["P"][2] - tt2), u3)
        _, _, _, X2, _, _ = S.Design.ik(self, Q0[None]); R12, tt2 = X2[0][0], X2[1][0]
        P3h = R12.T @ (self.seats["P"][2] - tt2); self.h_seat = float(P3h @ u3)
        self.hK = self.h_seat + P["dh"]; self.cK = self.c[2] + self.hK * u3
        self._knee = True; self.c0 = 0.0; self.flank = 0.0
        rad0 = self.rad_at(Q0[None], np.array([P["psi_rest"] * D2R]))
        self.c0 = float(rad0[0])
        rr = self.rad_at(np.repeat(Q0[None], 2, 0), np.array([P["psi_rest"] - 0.5, P["psi_rest"] + 0.5]) * D2R)
        self.flank = float(np.sign(rr[1] - rr[0])) if np.all(np.isfinite(rr)) else 0.0
        # dyad rest layout in the (sa, st) plane of the virtual frame
        e = lambda a: np.array([math.cos(a * D2R), math.sin(a * D2R)])
        self.a0 = P["lE"] * e(P["phiE"]); self.gam0 = P["phiE"] + 180.0 - P["beta0"]
        self.b0 = self.a0 + P["lc"] * e(self.gam0)
        k = self.core(Q0[None], np.array([P["psi_rest"] * D2R]))
        self.s_rest = np.array([k["s"][0] @ self.sa, k["s"][0] @ self.st])
        v0 = self.b0; self.sig = float(np.sign(((P["phiE"] - math.degrees(math.atan2(v0[1], v0[0])) + 180) % 360) - 180) or 1.0)

    def ik(self, Q):
        if not self._knee: return S.Design.ik(self, Q)
        raise RuntimeError("use core()")

    def core(self, Q, psi):
        """per pose (Q, psi): spherical IK with axis 3 = RK(psi) u3, member transforms, drift s (arm-home frame)"""
        u1, u2, u3 = self.u; n = len(Q); A1 = self.A[0]
        RK = rotm(self.dK, psi) if n else np.zeros((0, 3, 3)); U3 = RK @ u3
        w = Q @ u3; c12 = u1 @ u2; c23 = U3 @ u2
        M = np.array([[1, c12], [c12, 1]]); al, be = np.linalg.solve(M, np.stack([w @ u1, c23]))
        cr = np.cross(u1, u2); g2 = (1 - al ** 2 - be ** 2 - 2 * al * be * c12) / (cr @ cr)
        th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1))); a1 = math.degrees(A1); a2 = np.degrees(np.arccos(np.clip(c23, -1, 1)))
        ok = (th >= np.abs(a1 - a2) + S.SING) & (th <= np.minimum(a1 + a2, 360 - a1 - a2) - S.SING) & (g2 > 0)
        q1 = q2 = None
        for sg in (1.0, -1.0):
            z = al[:, None] * u1 + be[:, None] * u2 + sg * np.sqrt(np.clip(g2, 0, None))[:, None] * cr
            a = S.sub1(u1, z, w); b = S.sub1(u2, U3, z)
            p2 = rotm(u1, a) @ u2; br = np.sign(np.einsum("ij,ij->i", p2, np.cross(np.broadcast_to(u1, w.shape), w)))
            if q1 is None: q1, q2 = a.copy(), b.copy()
            else: pick = br == self.branch; q1[pick] = a[pick]; q2[pick] = b[pick]
        R1 = rotm(u1, q1); R2 = rotm(u2, q2); R12 = R1 @ R2; Ry = R12 @ RK
        v = unit(np.cross(u3, [0.3, 0.5, 0.8])); tv = np.einsum("nji,njk,k->ni", Ry, Q, v)
        q3 = S.sub1(u3, np.broadcast_to(v, (n, 3)), tv); R3 = rotm(u3, q3)
        c1, c2, c3 = self.c; cK = self.cK
        t1 = c1 - R1 @ c1
        t2 = np.einsum("nij,nj->ni", R1, c2[None] - R2 @ c2 - c1[None]) + c1
        ty = np.einsum("nij,nj->ni", R12, cK[None] - RK @ cK) + t2
        Rf = Ry @ R3; tf = np.einsum("nij,nj->ni", Ry, c3[None] - R3 @ c3) + ty
        s = np.einsum("nji,nj->ni", Q, tf)
        cres = (np.einsum("nij,nij->n", Rf, Q) - 1) / 2; res_deg = np.degrees(np.arccos(np.clip(cres, -1, 1)))
        return dict(q=np.stack([q1, q2, q3], 1), ok=ok, X1=(R1, t1), X2=(R12, t2), Xy=(Ry, ty), Xf=(Rf, tf), s=s,
                    rad=s @ u3, res_deg=res_deg, g2=g2)

    def rad_at(self, Q, psi):
        k = self.core(Q, psi); r = k["rad"].copy(); r[k["g2"] <= 0] = np.nan; return r

    def roots(self, Q):
        """psi grid scan: candidate roots (npsi-1, n) as psi (rad, nan where no crossing) and authority (mm/rad)"""
        P = self.p; ps = np.arange(-P["pmax"], P["pmax"] + 1e-9, 1.0) * D2R; n = len(Q); m = len(ps)
        r = self.rad_at(np.tile(Q, (m, 1, 1)), np.repeat(ps, n)).reshape(m, n) - self.c0
        f0, f1 = r[:-1], r[1:]; cr = np.isfinite(f0) & np.isfinite(f1) & (f0 * f1 <= 0) & (f0 != f1)
        dps = ps[1] - ps[0]
        with np.errstate(invalid="ignore", divide="ignore"):
            pr = ps[:-1, None] + f0 / (f0 - f1) * dps; au = (f1 - f0) / dps        # SIGNED slope d rad / d psi (mm/rad)
        cr &= np.sign(au) == self.flank                              # FLANK RULE: only roots on the rest root's flank of the closure
        return np.where(cr, pr, np.nan), np.where(cr, np.abs(au), np.nan)   # curve; the other flank is reached only through the
                                                                     # closure fold (auth 0, no root nearby) = a branch the knee cannot take

    def dyad(self, s):
        """in-plane dyad: s (n,3) drift (arm-home) -> phi (E arm, deg), gam (cuff link, deg), elbow beta (deg), ok"""
        P = self.p; lE, lc = P["lE"], P["lc"]
        sip = np.stack([s @ self.sa, s @ self.st], 1)
        vb = self.b0[None] + self.s_rest[None] - sip; d = np.linalg.norm(vb, axis=1)
        cb = (lE ** 2 + lc ** 2 - d ** 2) / (2 * lE * lc); beta = np.degrees(np.arccos(np.clip(cb, -1, 1)))
        ca = (lE ** 2 + d ** 2 - lc ** 2) / (2 * lE * np.maximum(d, 1e-9)); al = np.degrees(np.arccos(np.clip(ca, -1, 1)))
        phi = np.degrees(np.arctan2(vb[:, 1], vb[:, 0])) + self.sig * al
        pa = lE * np.stack([np.cos(phi * D2R), np.sin(phi * D2R)], 1)
        gam = np.degrees(np.arctan2(vb[:, 1] - pa[:, 1], vb[:, 0] - pa[:, 0]))
        ok = (np.abs(cb) <= 1) & (beta >= P["bmin"]) & (beta <= 180 - P["bmin"])
        return phi, gam, beta, ok, pa, vb


def pick(pr, au, ref):
    """root nearest ref per pose -> psi, authority, has"""
    dd = np.abs(pr - ref[None]); dd = np.where(np.isfinite(dd), dd, np.inf); j = dd.argmin(0); a = np.arange(pr.shape[1])
    has = np.isfinite(dd[j, a]); return np.where(has, pr[j, a], np.nan), np.where(has, au[j, a], np.nan), has


def wrap(x): return (x + 180.0) % 360.0 - 180.0


class Model(OSN.Model):
    def __init__(self, B, params=None, verbose=False):
        self.fix = dict(S.VModel.fix)
        self.B = B; self.D = Design(params); self.p = self.D.p; self.v = verbose; D = self.D; P = self.p
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)
        self.p["S_a"] = self.p["S_t"] = 0.0; self.p["R_r"] = 0.0
        # 1. track the FIT clips at their full 10 fps
        names = list(Z["NAMES"]); trk = {}; self.jumps = []; self.track_stats = dict(frames=0, pairs=0, jumps=0, jumps10=0, noroot=0)
        rest_ref = P["psi_rest"] * D2R
        for nm in CB.FIT:
            ii = np.nonzero(Z["CID"] == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            Qc = Z["HG"][ii].astype(float)
            if P.get("lock"): pr = np.full((1, len(ii)), rest_ref); au = np.full((1, len(ii)), 1e9)
            else: pr, au = D.roots(Qc)
            prev = None; prevq = None
            for j, gi in enumerate(ii):
                ref = rest_ref if prev is None else prev
                psi, a, has = pick(pr[:, j:j + 1], au[:, j:j + 1], np.array([ref]))
                self.track_stats["frames"] += 1
                if not has[0]: trk[int(gi)] = (np.nan, False); self.track_stats["noroot"] += 1; prev = None; prevq = None; continue
                k = D.core(Qc[j:j + 1], psi); ph, gm, bt, dok, _, _ = D.dyad(k["s"])
                qv = np.degrees(np.r_[k["q"][0, :2], k["q"][0, 2] + (ph[0] - P["phiE"]) * D2R, psi[0]])
                qv = np.r_[qv, ph[0], gm[0]]
                good = True
                if prev is not None and prevq is not None:
                    self.track_stats["pairs"] += 1; dq = np.abs(wrap(qv - prevq)); mx = float(dq.max())
                    self.jumps.append(mx)
                    if mx > 10: self.track_stats["jumps10"] += 1
                    if mx > P["jumpk"]: good = False; self.track_stats["jumps"] += 1
                trk[int(gi)] = (float(psi[0]), good); prev = float(psi[0]); prevq = qv
        self.trk = trk
        # 2. bench poses: tracked root (clip frames) or root nearest psi_rest (workspace)
        if P.get("lock"): pr = np.full((1, len(self.Q)), rest_ref); au = np.full((1, len(self.Q)), 1e9)
        else: pr, au = D.roots(self.Q)
        psi, auth, has = pick(pr, au, np.full(len(self.Q), rest_ref))
        cont = np.ones(len(self.Q), bool)
        for a, gi in enumerate(B.idx):
            if B.kind[a] == "clip" and int(gi) in trk:
                ps, good = trk[int(gi)]; cont[a] = good
                if np.isfinite(ps):
                    m = np.abs(pr[:, a] - ps) < 1e-9
                    psi[a] = ps; auth[a] = float(au[m, a][0]) if m.any() else auth[a]; has[a] = True
                else: has[a] = False
        psi0 = np.where(has, psi, 0.0); k = D.core(self.Q, psi0); self.k = k
        self.psi, self.auth = psi0, np.where(has, auth, 0.0)
        ph, gm, bt, dok, pa, vb = D.dyad(k["s"]); self.phi, self.gam, self.beta, self.pa, self.vb = ph, gm, bt, pa, vb
        rad_err = np.abs(k["rad"] - D.c0)
        self.q = k["q"]; self.X = {1: k["X1"], 2: k["X2"], 3: k["Xy"]}; self.Xf = k["Xf"]; self.s = k["s"]
        self.why = np.array([""] * len(B.idx), dtype=object)
        okf = has.copy(); self.why[~has] = "noroot"
        b = okf & ~k["ok"]; self.why[b] = "fold"; okf &= k["ok"]
        b = okf & (self.auth < P["auth_min"]); self.why[b] = "auth"; okf &= ~b
        b = okf & (np.abs(psi0) > (P["pmax"] - 0.5) * D2R); self.why[b] = "knee"; okf &= ~b
        b = okf & ~dok; self.why[b] = "dyad"; okf &= ~b
        b = okf & ~cont; self.why[b] = "flip"; okf &= ~b
        self.res_deg = k["res_deg"]; self.rad_err = rad_err
        b = okf & ((self.res_deg >= 0.5) | (rad_err >= 0.5)); self.why[b] = "closure"; okf &= ~b
        self.kin_ok = okf
        self.radial_span = 0.0

    def continuity(self): return np.ones(len(self.B.idx), bool)

    # members: 0 scapula, 1 L1, 2 L2 (+ fork), 3 yoke (hub-3 housing), 4 E arm, 5 arm pad (arm), 6 cuff link
    def T(self, m, i):
        if m == 0: return np.eye(3), np.zeros(3)
        if m in (1, 2, 3): R, t = self.X[m]; return R[i], t[i]
        if m == 5: return self.Q[i], np.zeros(3)
        D = self.D; Rf, tf = self.Xf[0][i], self.Xf[1][i]; u3 = D.u[2]; c3 = D.c[2]
        if m == 4:
            Rl = rotm(u3, (self.phi[i] - self.p["phiE"]) * D2R)[0]; tl = c3 - Rl @ c3
        elif m == 6:
            Rl = rotm(u3, (self.gam[i] - D.gam0) * D2R)[0]
            A0 = c3 + D.a0[0] * D.sa + D.a0[1] * D.st; A1 = c3 + self.pa[i, 0] * D.sa + self.pa[i, 1] * D.st
            tl = A1 - Rl @ A0
        else: raise ValueError(m)
        return Rf @ Rl, Rf @ tl + tf

    def _ip(self, xy): return self.D.c[2][None] + xy[:, :1] * self.D.sa + xy[:, 1:2] * self.D.st

    def _strap_xy(self, p0, p1, r0=0.0, eye=True):
        """8 mm strap from p0 to p1 (in-plane mm), starting r0 from p0, + an O10 eye at p1; 2 mm grid"""
        d = p1 - p0; L = float(np.linalg.norm(d)); e = d / max(L, 1e-9); nrm = np.array([-e[1], e[0]])
        xs = np.arange(r0 + 1.0, L, S.SPACING); ys = np.arange(-W_LINK / 2 + 1, W_LINK / 2, S.SPACING)
        X, Y = np.meshgrid(xs, ys); pts = p0[None] + X.ravel()[:, None] * e + Y.ravel()[:, None] * nrm
        if eye: dd = S.disc(EYE_R); pts = np.r_[pts, p1[None] + dd]
        return pts

    def fit(self):
        D = self.D; P = self.p; u = D.u; c = D.c
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        geo = S.Geometry.__new__(S.Geometry); geo.D = D; geo.groups = []; geo.links = []
        for k, mem in ((0, 0), (1, 1)):
            e, f = S.frame_of(u[k]); d = S.disc(HUB_R); Bk = c[k][None] + d[:, :1] * e + d[:, 1:] * f
            geo.groups.append(dict(name=f"hub{k + 1}", mem=mem, B=Bk, N=np.broadcast_to(u[k], Bk.shape).copy(), off=np.zeros(len(Bk))))
        e, f = S.frame_of(u[2]); d = S.disc(HUB_R); B3 = c[2][None] + d[:, :1] * e + d[:, 1:] * f
        geo.groups.append(dict(name="hub3", mem=3, B=B3, N=np.broadcast_to(u[2], B3.shape).copy(), off=np.zeros(len(B3))))
        a0, b0 = D.a0, D.b0
        BE = self._ip(self._strap_xy(np.zeros(2), a0, r0=HUB_R + 0.5))
        BC = self._ip(self._strap_xy(a0, b0, r0=EYE_R + 0.5))
        BC = np.r_[BC, self._ip(S.disc(EYE_R) + a0[None])]
        BP_ = self._ip(S.disc(EYE_R) + (b0 + D.s_rest)[None]) + D.c0 * u[2]
        for nm, mem, Bk in (("Earm", 4, BE), ("clink", 6, BC), ("pad", 5, BP_)):
            geo.groups.append(dict(name=nm, mem=mem, B=Bk, N=np.broadcast_to(u[2], Bk.shape).copy(), off=np.zeros(len(Bk))))
        # fork cheeks on link 2: 3 x 8 plates at +-(HUB_R + GAP + 1.5) along dK, bottom face at hK - CROWN/2 (+ the fit)
        dK = D.dK; ex = unit(np.cross(dK, u[2])); g = []
        for sgn in (-1, 1):
            for x in np.arange(-W_LINK / 2 + 1, W_LINK / 2, S.SPACING):
                for y in (-0.75, 0.75): g.append(c[2] + sgn * (HUB_R + 0.25 + 1.5 + y) * dK + x * ex)
        bh = c[1] + 60.0 * u[1] - c[2]; bh = unit(bh - (bh @ u[2]) * u[2]); dK2 = dK - (dK @ bh) * bh   # base direction (toward J2)
        for ang in np.arange(-90.0, 90.0 + 1e-6, 2.0 / ARM_R / D2R):                       # arms: half ring at ARM_R round the hub
            for y in (-0.75, 0.75):
                v = math.cos(ang * D2R) * bh + math.sin(ang * D2R) * unit(dK2)
                if abs(ang) < 70: g.append(c[2] + (ARM_R + y) * v)
        Bf = np.array(g)
        if not P.get("lock"): geo.groups.append(dict(name="fork", mem=2, B=Bf, N=np.broadcast_to(u[2], Bf.shape).copy(), off=np.zeros(len(Bf))))
        self.geo = geo
        items = [(gq["mem"], gq["B"], gq["N"], 140.0) for gq in geo.groups]
        res = self.needed(items, poses)
        H = {gq["name"]: r for gq, r in zip(geo.groups, res)}
        self.Hneed, self.Lneed = H, {}
        self._greedy(links=False); keep1 = ~self.drop
        f1 = H["hub1"][keep1].max(); f2 = H["hub2"][keep1].max(); f3 = H["hub3"][keep1].max()
        geo.add_links(f1, f2, f3)
        for lk in geo.links:                                        # link 2 ends at the fork base, clear of the tilting hub
            if lk["name"] != "L2": continue
            rows = []
            for dv, keep, sarc in lk["rows"]:
                R_ = 0.5 * (np.linalg.norm(c[1] + f2 * u[1]) + np.linalg.norm(c[2] + f3 * u[2])); pts = R_ * dv
                w = pts - c[2]; off = np.linalg.norm(w - (w @ u[2])[:, None] * u[2], axis=1)
                rows.append((dv, keep & (off > (HUB_R if P.get("lock") else HUB_R + 3.0)), sarc))
            lk["rows"] = rows
        items = []; idx = []
        for lk in geo.links:
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, ())); idx.append((lk["name"], ri))
        res = self.needed(items, poses); L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        self.Lneed = L
        self._greedy(keep0=keep1)
        self.finalize()

    def _greedy(self, keep0=None, links=True):
        H = self.Hneed
        H["stack"] = np.concatenate([H[n] for n in ("Earm", "clink", "pad", "fork") if n in H], 1)   # proxy group for the drop score
        H["h3"] = H["hub3"]
        S.Model.greedy_drop(self, keep0=keep0, links=links)

    def _levels(self, keep):
        H = self.Hneed; P = self.p
        f1 = H["hub1"][keep].max(); f2 = H["hub2"][keep].max(); f3 = H["hub3"][keep].max()
        zE, zc, zp = H["Earm"][keep].max(), H["clink"][keep].max(), H["pad"][keep].max()
        zc = max(zc, zp + PAD_T + GAP); zp = zc - PAD_T - GAP
        zf = max(H["fork"][keep].max(), self.D.hK - CHEEK) if "fork" in H else None           # cheek: trunnion pin O4 at hK, 3 mm of cheek round it
        if P.get("earm_under") and not P.get("lock"):            # E arm = hub 3's lower plate: one level for both
            f3 = max(f3, zE, zc + T_LINK + GAP); zE = f3
            return f1, f2, f3, zE, zc, zp, zf
        zE = max(zE, f3 + UP, zc + T_LINK + GAP, (self.D.hK + CHEEK + 1.0) if P.get("earm_over") and not P.get("lock") else 0.0)   # earm_over: E arm over the cheek tops
        return f1, f2, f3, zE, zc, zp, zf

    def _heights(self, keep):
        f1, f2, f3, zE, zc, zp, zf = self._levels(keep)
        rL = {k: [r[keep].max(0) for r in rows] for k, rows in self.Lneed.items()}
        return f1, f2, 0.0, rL

    def f3_of(self, tr, keep=None):
        keep = keep if keep is not None else ~self.drop
        if self.p.get("earm_under") and not self.p.get("lock"): return float(self._levels(keep)[2])
        return float(self.Hneed["hub3"][keep].max())

    def finalize(self):
        keep = ~self.drop
        f1, f2, f3, zE, zc, zp, zf = self._levels(keep)
        self.lv = dict(f1=f1, f2=f2, f3=f3, zE=zE, zc=zc, zp=zp, zf=zf)
        self.Hneed["stack"] = np.zeros((len(self.poses_fit), 1)); self.Hneed.pop("h3", None)
        S.Model.finalize(self)                                      # links (ramps to the hub levels) + rigid hub1/2/3
        m2, P2 = self.link_pts["L2"]; c3, u3 = self.D.c[2], self.D.u[2]; w = P2 - c3
        offa = np.linalg.norm(w - (w @ u3)[:, None] * u3, axis=1)
        if not self.p.get("lock"): self.link_pts["L2"] = (m2, P2[offa > ARM_R + 0.5])
        D = self.D; g = {x["name"]: x for x in self.geo.groups}
        for nm, z in (("Earm", zE), ("clink", zc), ("pad", zp), ("fork", zf)):
            if nm not in g: continue
            self.rigid[nm] = (g[nm]["mem"], g[nm]["B"] + z * g[nm]["N"])
        self.f = [f1, f2, f3]
        self.trunnion_off = round(float(D.hK - (f3 + self.p["toff"])), 2)  # K line vs its target height in hub 3's housing (mm)
        self.trunnion_in = 1.5 <= D.hK - f3 <= CROWN - 1.5
        if zf is not None and zf > D.hK - 2.0: self.trunnion_in = False   # skin pushed the cheeks above the pin: no fork
        self._contact_only(); self._solids()

    def _contact_only(self):
        D = self.D; u, c = D.u, D.c; F = self.f; out = []
        ang = np.linspace(0, 2 * np.pi, 32, endpoint=False); dd = S.disc(HUB_R, 3.0)
        for k, mem in ((0, 0), (1, 1), (2, 3)):
            e, f = S.frame_of(u[k]); ring = HUB_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
            for z in np.linspace(F[k], F[k] + CROWN, 4): out.append((mem, c[k] + z * u[k] + ring))
            out.append((mem, c[k] + (F[k] + CROWN) * u[k] + dd[:, :1] * e + dd[:, 1:] * f))       # crown disc
        lv = getattr(self, "lv", None)
        if lv:                                                       # tops of the dyad parts and the fork cheeks' walls
            g = {x["name"]: x for x in self.geo.groups}
            out.append((4, g["Earm"]["B"] + (lv["zE"] + T_LINK) * g["Earm"]["N"]))
            out.append((6, g["clink"]["B"] + (lv["zc"] + T_LINK) * g["clink"]["N"]))
            if "fork" in g:
                for z in np.linspace(lv["zf"], self.D.hK + CHEEK, 4): out.append((2, g["fork"]["B"] + z * g["fork"]["N"]))
        self.contact = out

    def _solids(self):
        D = self.D; u, c = D.u, D.c; F = self.f
        self.cyl = {"hub1": (0, c[0] + F[0] * u[0], u[0]), "hub2": (1, c[1] + F[1] * u[1], u[1]), "hub3": (3, c[2] + F[2] * u[2], u[2])}
        self.box = {}; self.strap = {}
        for nm, (mem, pts) in self.link_pts.items(): self.strap[nm] = (mem, pts + (T_LINK / 2) * unit(pts))
        for nm in ("Earm", "clink"): m, Pt = self.rigid[nm]; self.strap[nm] = (m, Pt + (T_LINK / 2) * u[2])
        m, Pt = self.rigid["pad"]; self.strap["pad"] = (m, Pt + (PAD_T / 2) * u[2])
        if "fork" in self.rigid:
            m, Pt = self.rigid["fork"]; top = self.D.hK + CHEEK - self.lv["zf"]
            self.strap["fork"] = (m, np.concatenate([Pt + z * u[2] for z in np.linspace(0, max(top, 0.0), 4)]))
        ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); self.cyl_surf = {}
        for nm, (mem, cen, ax) in self.cyl.items():
            e, f = S.frame_of(ax); pts = [cen + z * ax + HUB_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, CROWN, 5)]
            dd = S.disc(HUB_R, 4.0); pts.append(cen + CROWN * ax + dd[:, :1] * e + dd[:, 1:] * f)
            self.cyl_surf[nm] = (mem, np.concatenate(pts))

    def collide(self, i):
        base = OSN.Model.collide(self, i)                           # seed pairs (L2-hub1, hub3-hub1/2, L1-hub3, L1-L2) + hub1-hub2
        def tf(m, P): R, t = self.T(m, i); return P @ R.T + t
        cyl = {}
        for k, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k] = (m, R @ cen + t, R @ ax)
        W = {k: tf(m, P) for k, (m, P) in self.strap.items()}
        hw = dict(L1=T_LINK / 2, L2=T_LINK / 2, Earm=T_LINK / 2, clink=T_LINK / 2, pad=PAD_T / 2, fork=0.75)
        ex, adj = {}, {}
        def vs_cyl(a, hub): _, cen, ax = cyl[hub]; return float(self.sd_cyl(W[a], cen, ax).min()) - hw[a] if a in W and len(W[a]) else 1e9
        def vs_pts(a, b): return float(cKDTree(W[b]).query(W[a])[0].min()) - hw[a] - hw[b] if a in W and b in W and len(W[a]) and len(W[b]) else 1e9
        for a in ("Earm", "clink", "pad", "fork"):
            for hub in ("hub1", "hub2"): ex[f"{a}-{hub}"] = vs_cyl(a, hub)
        for a in ("clink", "pad"): ex[f"{a}-hub3"] = vs_cyl(a, "hub3")
        for a, b in (("Earm", "L1"), ("Earm", "L2"), ("clink", "L1"), ("clink", "L2"), ("pad", "L1"), ("pad", "L2"),
                     ("pad", "Earm"), ("fork", "Earm"), ("fork", "clink"), ("fork", "pad"), ("fork", "L1")):
            ex[f"{a}-{b}"] = vs_pts(a, b)
        # adjacent pairs: running gap (yoke vs link 2 and its cheeks through the trunnions; dyad stack)
        _, cen3, ax3 = cyl["hub3"]
        if "fork" in W:                                              # (lock: hub 3 is rigid on link 2 - one body)
            adj["hub3-L2"] = float(self.sd_cyl(W["L2"], cen3, ax3).min()) - hw["L2"] if len(W["L2"]) else 1e9
            adj["hub3-fork"] = float(self.sd_cyl(W["fork"], cen3, ax3).min()) - hw["fork"]
        P3 = tf(*self.cyl_surf["hub3"])
        m, Pc = self.rigid["clink"]; Pc = tf(m, Pc + (T_LINK / 2) * self.D.u[2]); m, Pe = self.rigid["Earm"]; Pe = tf(m, Pe + (T_LINK / 2) * self.D.u[2])
        A_ = tf(4, (self.D.c[2] + self.D.a0[0] * self.D.sa + self.D.a0[1] * self.D.st)[None])[0]
        farA = lambda X: np.linalg.norm(X - A_, axis=1) > EYE_R + 1.0
        if farA(Pc).any() and farA(Pe).any(): adj["Earm-clink"] = float(cKDTree(Pe[farA(Pe)]).query(Pc[farA(Pc)])[0].min()) - T_LINK
        self.last_clear.update({k: round(v, 1) for k, v in ex.items()}); self.last_clear.update({k: round(v, 1) for k, v in adj.items()})
        out = min([base] + list(ex.values()))
        if adj and min(adj.values()) < S.VModel.ADJ: out = min(out, -1.0)
        return out

    def run(self, B=None):
        if not self.kin_ok.any():                                    # nothing closes: every pose not taken
            self.B.reset(); [self.B.record(i, None) for i in range(len(self.B.idx))]; r = self.B.report()
            r["why"] = {k: int((self.why == k).sum()) for k in ("noroot", "fold", "auth", "knee", "dyad", "flip", "closure")}
            r["knee"] = dict(trunnion_off=None, track=self.track_stats); r["f"] = []; r["levels"] = {}; r["parts_ib14"] = {}; r["parts_pairs"] = {}
            self.trunnion_in = True; return r
        r = S.VModel.run(self)
        r["why"] = {k: int((self.why == k).sum()) for k in ("noroot", "fold", "auth", "knee", "dyad", "flip", "closure", "skin", "parts", "contact")}
        ok = self.kin_ok
        r["knee"] = dict(psi_range_deg=[round(float(np.degrees(self.psi[ok].min())), 1), round(float(np.degrees(self.psi[ok].max())), 1)] if ok.any() else None,
                         auth_p5=round(float(np.percentile(self.auth[ok], 5)), 1) if ok.any() else None,
                         auth_p50=round(float(np.median(self.auth[ok])), 1) if ok.any() else None,
                         deg_per_mm_p50=round(float(np.degrees(1 / np.median(self.auth[ok]))), 2) if ok.any() else None,
                         deg_per_mm_p95=round(float(np.degrees(1 / np.percentile(self.auth[ok], 5))), 2) if ok.any() else None,
                         elbow=[round(float(self.beta[ok].min()), 1), round(float(self.beta[ok].max()), 1)] if ok.any() else None,
                         c0=round(self.D.c0, 2), hK=round(self.D.hK, 1), trunnion_off=getattr(self, "trunnion_off", None),
                         res_mm=round(float(self.rad_err[ok].max()), 4) if ok.any() else None,
                         track=self.track_stats, jump_p50=round(float(np.median(self.jumps)), 2) if self.jumps else None,
                         jump_max=round(float(np.max(self.jumps)), 1) if self.jumps else None)
        r["levels"] = {k: round(float(v), 1) for k, v in getattr(self, "lv", {}).items() if v is not None}
        return r


def _report(B, params):
    P = dict(params or {}); M = Model(B, P); r = M.run()
    for it in range(2):                                              # put the trunnion axis at toff above hub 3's face
        off = r["knee"]["trunnion_off"]
        if off is None or abs(off) <= 1.5: break
        P2 = dict(P); P2["dh"] = round(float(M.p["dh"]) - off, 2)
        M2 = Model(B, P2); r2 = M2.run(); r2["dh_refit"] = P2["dh"]
        if r2["knee"]["trunnion_off"] is None or abs(r2["knee"]["trunnion_off"]) > abs(off): break
        r, M, P = r2, M2, P2
    r["pinb_along_mm"] = round(float((M.D.b0 + M.D.s_rest)[0]), 1)   # pin b's pad must sit on the cuff, distal of hub 3
    r["trunnion_in_housing"] = bool(getattr(M, "trunnion_in", False)) or bool(M.p.get("lock"))
    # structurally invalid -> gap >= 500 (never a valid number), graded so a search can climb out: 500 + the would-be gap
    # + 2 per mm pin b sits proximal of PINB_MIN + 50 if the trunnion is outside hub 3's housing
    bad = 0.0
    if r["pinb_along_mm"] < PINB_MIN: bad += 2.0 * (PINB_MIN - r["pinb_along_mm"]) + 1.0
    if not r["trunnion_in_housing"]: bad += 50.0
    if bad: r["gap_reported"] = r["gap"]; r["gap"] = round(500.0 + r["gap"] + bad, 2); r["invalid"] = True
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    r["passive_translations"] = 0
    return r, M


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def kin(par):
    """fold-free-and-closable shares (no parts), tracked vs nearest-root, and the plain 3R at psi fixed"""
    B = CB.Bench(60, 160); M = Model(B, par); D = M.D; clip = np.array([k == "clip" for k in B.kind])
    k0 = D.core(M.Q, np.full(len(M.Q), M.p["psi_rest"] * D2R))
    print(f"arcs {np.degrees(D.A).round(1)} hK {D.hK:.1f} c0 {D.c0:.2f}; knee locked at psi_rest: fold-free {k0['ok'].mean():.3f} "
          f"(ws {k0['ok'][~clip].mean():.3f}, clip {k0['ok'][clip].mean():.3f}); radial drift span locked {np.nanmax(k0['rad']) - np.nanmin(k0['rad']):.1f} mm")
    ok = M.kin_ok; print(f"knee closure-set, all kin checks: {ok.mean():.3f} (ws {ok[~clip].mean():.3f}, clip {ok[clip].mean():.3f}) why",
                         {w: int((M.why == w).sum()) for w in set(M.why) if w}, "track", M.track_stats,
                         "jump p50/p99/max", np.percentile(M.jumps, [50, 99, 100]).round(1) if M.jumps else None)


def _bench(nc, nw, fast=False):
    old = os.environ.get("CB_EXACT")
    if fast and old is not None: del os.environ["CB_EXACT"]
    try: return CB.Bench(n_clip=nc, n_ws=nw)
    finally:
        if fast and old is not None: os.environ["CB_EXACT"] = old


def audit(M, B):
    """red team on a run model: near-touch (lowest metal incl. hub walls / crowns and dyad tops over the taken poses), the
    gap with metal < 1 / 2 mm counted as contact, the overhead split (elevation >= 140)"""
    taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
    mins = []
    for i in range(len(B.idx)):
        if not taken(i): continue
        cm = float(B.dist(i, np.concatenate([M.world(m, i, Pc) for m, Pc in M.contact])).min()) if M.contact else 1e9
        mins.append((min(float(np.min(B.res[i])), cm), i))
    mins.sort(); out = dict(near_touch_min_mm=round(mins[0][0], 2) if mins else None,
                            near_touch_low=[dict(mm=round(d, 2), plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"], kind=B.kind[i]) for d, i in mins[:5]])
    res1 = list(B.res)
    for thr in (1.0, 2.0):
        for d, i in mins:
            if d < thr: B.res[i] = np.r_[B.res[i], -1e-3]
        out[f"gap_near{int(thr)}"] = B.report()["gap"]; out[f"near{int(thr)}_poses"] = int(sum(1 for d, i in mins if d < thr)); B.res = list(res1)
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind); hi = np.nonzero(el >= 140)[0]
    ws = [i for i in hi if kind[i] == "ws"]; cl = [i for i in hi if kind[i] == "clip"]; tk = [i for i in hi if taken(i)]
    d = np.concatenate([B.res[i] for i in tk]) if tk else np.zeros(0)
    out["overhead140"] = dict(ws=len(ws), reach=round(float(np.mean([taken(i) for i in ws])), 4) if ws else None,
                              clip=len(cl), follow=round(float(np.mean([taken(i) for i in cl])), 4) if cl else None,
                              inband14=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None,
                              inband10=round(float(((d >= 2) & (d <= 10)).mean()), 4) if len(d) else None,
                              why_not={k: int(sum(1 for i in hi if not taken(i) and M.why[i] == k)) for k in set(M.why[hi]) if k})
    return out


def frozen(par):
    """lesson (c): fit on Bench(60,160) FAST (the claimed shape: every level, link path, fork, dyad, c0 and hK frozen), then
    wear it on Bench(110,360) (exact with CB_EXACT=1) without refit; the knee is re-solved and re-tracked per pose"""
    B1 = _bench(60, 160, fast=True); r1, M1 = _report(B1, par)
    P2 = {k: v for k, v in M1.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    B = _bench(110, 360)

    class Frozen(Model):
        def fit(self):
            for a in ("geo", "rigid", "link_pts", "f", "lv", "contact", "cyl", "box", "strap", "cyl_surf", "Hneed", "Lneed", "trunnion_off", "trunnion_in"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    M = Frozen(B, P2); r = M.run()
    keys = ("gap", "reach", "follow", "inband14", "inband10", "contact")
    out = dict(fit60_fast={k: r1[k] for k in keys}, big={k: r[k] for k in keys}, mode=B.mode, why=r.get("why"), knee=r.get("knee"),
               parts_pairs=r.get("parts_pairs"), audit_big=audit(M, B), audit_60=audit(M1, B1))
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "kin": kin(par); sys.exit()
    if mode == "frozen":
        out = frozen(par); print(json.dumps(out, default=float))
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        sys.exit()
    B = CB.Bench(60, 160); t = time.time()
    r, M = _report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], f"{time.time() - t:.0f}s",
          {k: r.get(k) for k in ("gap_reported", "pinb_along_mm", "trunnion_in_housing", "dh_refit")})
    print("knee", r["knee"]); print("levels", r["levels"], "f", r["f"]); print("parts", r["parts_ib14"], r["parts_pairs"], "min clear", r.get("min_clear_taken"))
