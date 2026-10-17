"""pinknee-scapular-relay-4r: the verified pin-knee 3R (docs/concepts/models/skin-normal-3r-pin-knee.py, H1) with its J1
seat carried by a spring-centred O20 J0 on bony scapula skin (a scapular relay; Keemink 2018-style redundant 4R).

Chain: scapula handler -> hub 0 (J0, counted joint, R about the GH ray c, O20, scapula-fixed housing; preloaded torsion
spring + own-angle dowel-in-slot stops |q0| <= T) -> link 0 (12 x 3 Ti strap on the c -> u1 great circle; it carries
hub 1's housing) -> J1 (ACTIVE R, O20) -> link 1 -> J2 (ACTIVE R, O20, own-angle stops at th margin m_lo / m_hi) ->
link 2 -> J3 (ACTIVE R, O20, axis tilted b3) -> member 3 (hub 3 lower plate + E strap) -> pin a -> knee link -> pin b ->
arm pad / BOTTOM (two-pin MR63ZZ knee, outside the DOF count). 4 joints (DOF cap 4), 0 passive translations.

Kinematics (exact): J0 is a rotation Rc = R(c, q0) about a GH ray, so the whole host chain is the host's own chain solved
for the relative arm rotation Q' = Rc^T Q and mapped back with Rc (every chain member: T'(m) = Rc T_host(m); the arm
pad: Rc Q' = Q, unchanged). hub 0 is the only scapula-fixed member (member 8). The host's knee window
[ang_min, 180 - ang_min], slide tolerance, closure residual and part checks run on EVERY pose incl. the relayed ones.

Determination (R17): clamp policy (tools/spare_flood.Cfg): q0 = least-|q0| state with J2 inside [lo, hi] (the spring's
preload holds q0 = 0 while J2 is strictly inside its stops = mode A = the verified host); while J2 is on a stop the
J0-J1-J3 sub-chain keeps margin >= m_sw. Clip frames: q0 path-tracked along the 10 fps clip (Cfg.step, push <= 10 deg);
ws poses: pose-local state + the full-grid flood (tools/spare_flood.flood, 1432 envelope nodes as transit only,
nodes restricted to those where the host chain closes WITH its knee window at the node's state); a relayed ws pose
counts only if the flood reaches its node within 2 deg of its q0.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/pinknee-scapular-relay-4r.py [check|redteam] ['<json>']
    CB_EXACT=1 ... frozen '<json>' --out R.json    (fit Bench(60,160) fast, wear frozen on Bench(110,360) exact)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import spare_flood as SF                                     # noqa: E402
_spec = importlib.util.spec_from_file_location("pk_for_relay", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
PK = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(PK)
S = PK.S; unit = S.unit; D2R = math.pi / 180
ID = "pinknee-scapular-relay-4r"
NAME = "Pin-knee 3R on a spring-centred scapular relay J0 (4 joints, 0 passive translations)"
H1 = {"rad1": 10.0, "rad2": 10.0, "rad3": 10.0, "az1": 101.1634, "el1": 63.8986, "az2": 30.153, "el2": 47.0108,
      "wd": 70.3931, "wa": -8.1248, "b3": 0.2842, "lE": 59.5534, "lc": 28.2401, "phiE": -5.8107, "phib": -54.914,
      "ang_min": 30.4611, "stk": 5.6815}
PARAMS = dict(PK.PARAMS); PARAMS.update(H1)
PARAMS.update(a0=35.0, phi=90.0, azu=None,           # J0 axis c = J1 rest axis tilted a0 about a normal turned phi (back cell)
              T=40.0, m_lo=5.0, m_hi=5.0, m_sw=5.0, policy=0, k2=4.0, W0=12.0, connect=1, kneeflood=1)
WS_JUMP = 10.0


def rot_mats(c, q_deg):
    """(n,3,3) rotations about the unit axis c by q (deg)"""
    a = np.radians(np.asarray(q_deg, float)); c = unit(c); Kx = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
    return np.eye(3)[None] + np.sin(a)[:, None, None] * Kx[None] + (1 - np.cos(a))[:, None, None] * (Kx @ Kx)[None]


def seat_ok(U):
    """J1 / J0 seat rule (CLAUDE.md: back of the shoulder + acromion top): az -110..135, el >= -20, x <= 0.2"""
    U = np.atleast_2d(U); el = np.degrees(np.arcsin(np.clip(U[:, 1], -1, 1))); az = np.degrees(np.arctan2(U[:, 2], -U[:, 0]))
    return (az >= -110) & (az <= 135) & (el >= -20) & (U[:, 0] <= 0.20)


def make_cfg(P, D):
    u1r = D.u[0]
    if P.get("azu") is not None:        # J0 axis at angle a0 from J1, azimuth azu about J1 (e = unit(u1 x y), f = u1 x e;
        e = unit(np.cross(u1r, [0.0, 1.0, 0.0])); f = np.cross(u1r, e); a, b = math.radians(float(P["a0"])), math.radians(float(P["azu"]))
        c = unit(math.cos(a) * u1r + math.sin(a) * (math.cos(b) * e + math.sin(b) * f))   # hub 2's orbit leaves azu 120-270 free)
    else: c = SF.tilt_pivot(u1r, float(P["a0"]), float(P["phi"]))
    a1, a2 = (math.degrees(x) for x in D.A)
    # T cut to the largest symmetric travel keeping J1 inside the seat rule (a design step, reported as T_eff)
    qs = np.arange(0.0, float(P["T"]) + 0.01, 0.5); Teff = float(P["T"])
    for sg in (1, -1):
        U = np.einsum("nij,j->ni", rot_mats(c, sg * qs), u1r); good = seat_ok(U)
        bad = np.nonzero(~good)[0]
        if len(bad): Teff = min(Teff, float(qs[max(0, bad[0] - 1)]))
    s = SF.Cfg(c, u1r, D.u[2], a1, a2, T=Teff, m=min(P["m_lo"], P["m_hi"]), m_lo=P["m_lo"], m_hi=P["m_hi"],
               m_sw=P["m_sw"], policy="energy" if int(P["policy"]) else "clamp", k2=P["k2"])
    s.Teff = Teff; s.c_seat_ok = bool(seat_ok(c)[0])
    return s


def static_q0(s, U3):
    """pose-local state for each u3 (rows) -> q0 (deg, nan = no state)"""
    out = np.full(len(U3), np.nan)
    for k, u3 in enumerate(U3):
        q = s.static_q(u3)
        if q is not None: out[k] = q
    return out


class Model(PK.Model):
    ADJ = 0.15

    def __init__(self, B, params=None, verbose=False):
        self.fix = dict(S.VModel.fix); params = dict(PARAMS, **(params or {}))
        self.B = B; self.D = PK.Design(params); self.p = self.D.p; self.v = verbose
        P = self.p; P["tp"] = (float(P["stk"]) - S.RUN) / 2
        self.hr = [round(float(P.get(f"rad{k + 1}", S.HUB_R)), 2) for k in range(3)]
        for r_ in self.hr:
            if r_ != S.HUB_R: raise ValueError("O20 only (user 2026-10-16)")
        self.cyl_r = {"hub1": self.hr[0], "hub2": self.hr[1], "hub3": self.hr[2], "hub0": S.HUB_R}
        Z = CB._poses_all(); self.Z = Z
        self.cfg = s = make_cfg(P, self.D)
        self.RS = Z["RS"][B.idx].astype(float); self.Qt = Z["HG"][B.idx].astype(float)
        # clip q0 states: path-tracked along every fit clip at 10 fps
        self.clipq = self._track_clips()
        U3 = self.Qt @ self.D.u[2]
        q0 = np.full(len(B.idx), np.nan)
        for i, gi in enumerate(B.idx):
            if B.kind[i] == "clip" and int(gi) in self.clipq:
                q0[i] = self.clipq[int(gi)][0] if self.clipq[int(gi)][1] else np.nan
            else: q0[i] = static_q0(s, U3[i:i + 1])[0]
        rel_ok = np.isfinite(q0); q0 = np.where(rel_ok, q0, 0.0); self.q0 = q0; self.rel_ok = rel_ok
        self.Rc = rot_mats(s.c, q0); self.Q = np.einsum("nji,njk->nik", self.Rc, self.Qt)
        q, ok, X1, X2, X3, sv_ = self.D.ik(self.Q)
        # knee reference (mid drift) over the bench poses + the fit clips, each at its own relay state
        ii = np.array(sorted(self.clipq)); qc = np.array([self.clipq[g][0] for g in ii]); okc0 = np.array([self.clipq[g][1] for g in ii])
        Qc = np.einsum("nji,njk->nik", rot_mats(s.c, np.nan_to_num(qc)), Z["HG"][ii].astype(float))
        _, okc, _, _, _, sc = self.D.ik(Qc); okc &= okc0
        sv = np.r_[sv_[ok & rel_ok], sc[okc]]
        if P.get("centre") and len(sv): self.D.m = 0.5 * (sv.max(0) + sv.min(0))
        if P.get("m_fix") is not None: self.D.m = np.array(P["m_fix"], float)
        self.D.m[2] = 0.0
        self.radial_span = round(float(np.ptp(sv[:, 2])), 3) if len(sv) else 0.0
        self.drift_span = [round(float(np.ptp(sv[:, k])), 1) for k in range(2)] if len(sv) else [0, 0]
        self.q, self.X, self.s = q, {1: X1, 2: X2, 3: X3}, sv_
        self.K = self.D.knee(sv_)
        self.why = np.array([""] * len(B.idx), dtype=object)
        self.why[~rel_ok] = "relay"
        okf = ok & rel_ok; self.why[rel_ok & ~ok] = "fold"
        kok = self.K["ok"] & (np.abs(sv_[:, 2]) <= P["R_tol"]); self.why[okf & ~kok] = "slide"; okf &= kok
        cont = self.continuity(); self.why[okf & ~cont] = "flip"; okf &= cont
        self.kin_ok = okf
        R123 = X3[0]; cc = (np.einsum("nij,nij->n", R123, self.Q) - 1) / 2
        self.res_deg = np.degrees(np.arccos(np.clip(cc, -1, 1)))
        bad = self.kin_ok & (self.res_deg >= 0.5); self.why[bad] = "closure"; self.kin_ok &= ~bad
        self.riser = None
        self.islands = 0; self.flood_info = None
        if P.get("connect", 1) and s.Teff > 0: self._flood_filter()

    def _track_clips(self):
        """{global pose index: (q0, ok)} along each fit clip (10 fps): q0 tracked by the clamp / twin step from q0 = 0
        at the clip's first frame; a frame without a state (jam / snap > 10 deg) restarts from its pose-local state"""
        s = self.cfg; Z = self.Z; names = list(Z["NAMES"]); cid = Z["CID"]; out = {}
        for nm in CB.FIT:
            ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            U3 = Z["HG"][ii].astype(float) @ self.D.u[2]; prev = None
            for j, gi in enumerate(ii):
                if prev is None: qn = s.static_q(U3[j]); okj = qn is not None
                else:
                    qn = s.step(U3[j], prev, jump=WS_JUMP); okj = qn is not None
                    if qn is None: qn = s.static_q(U3[j])
                out[int(gi)] = (float(qn) if qn is not None else np.nan, bool(okj))
                prev = qn
        return out

    def continuity(self):
        """10 fps fit clips: q0, q1, q2, q3' = q3 + phi, pin a, pin b; a step > JUMP or a relay snap breaks it"""
        Z = self.Z; names = list(Z["NAMES"]); cid = Z["CID"]; ok_at = {}; s = self.cfg
        for nm in CB.FIT:
            ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            q0 = np.array([self.clipq[int(g)][0] for g in ii]); okr = np.array([self.clipq[int(g)][1] for g in ii]) & np.isfinite(q0)
            Qc = np.einsum("nji,njk->nik", rot_mats(s.c, np.nan_to_num(q0)), Z["HG"][ii].astype(float))
            q, ok, _, _, _, sv = self.D.ik(Qc); K = self.D.knee(sv); ok &= K["ok"] & okr
            qq = np.c_[np.radians(np.nan_to_num(q0)), q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"]]; prev = None
            for j, gi in enumerate(ii):
                good = bool(ok[j])
                if good and prev is not None and np.degrees(np.abs(PK.wrap(qq[j] - qq[prev]))).max() > S.JUMP: good = False
                ok_at[int(gi)] = good; prev = j if ok[j] else None
        return np.array([ok_at.get(int(gi), True) for gi in self.B.idx])

    def _node_ok(self):
        """grid nodes (1432 envelope poses) where the host closes WITH its knee window and slide tolerance at the
        node's pose-local relay state (the flood's allowed transit set)"""
        s = self.cfg; q0 = static_q0(s, s.U3)
        okr = np.isfinite(q0); Qn = np.einsum("nji,njk->nik", rot_mats(s.c, np.nan_to_num(q0)), SF.HGrel)
        _, ok, _, _, _, sv = self.D.ik(Qn); K = self.D.knee(sv)
        return okr & ok & K["ok"] & (np.abs(sv[:, 2]) <= self.p["R_tol"])

    def _flood_filter(self):
        s = self.cfg; allowed = None
        if self.p.get("kneeflood", 1): allowed = np.nonzero(self._node_ok())[0]
        conn, states = SF.flood(s, seeds="modeA", nodes=allowed)
        drop = 0; miss = 0
        for i in range(len(self.B.idx)):
            if self.B.kind[i] != "ws" or not self.kin_ok[i] or abs(self.q0[i]) < 1e-9: continue
            j = SF.node_of(self.B.poses[i]["plane"], self.B.poses[i]["elev"], self.B.poses[i]["axial"])
            good = j is not None and any(abs(x - self.q0[i]) <= 2.0 for x in states.get(j, ()))
            if j is None: miss += 1
            if not good: self.kin_ok[i] = False; self.why[i] = "island"; drop += 1
        self.islands = drop; self.flood_info = dict(grid_conn=round(float(conn.mean()), 3), off_grid=miss,
                                                    allowed=None if allowed is None else int(len(allowed)))

    # members: 0 link 0 + hub 1 housing (rotates with J0), 1 link 1, 2 link 2, 3 member 3, 5 arm, 6 knee, 8 hub 0 (fixed)
    def T(self, m, i):
        if m == 8: return np.eye(3), np.zeros(3)
        R, t = super().T(m, i); Rc = self.Rc[i]
        return Rc @ R, Rc @ t

    def _l0_rows(self):
        """link 0 sample rows: the c -> u1 great circle, W0 wide, samples outside both hub radii"""
        c = self.cfg.c; u1 = self.D.u[0]; W = float(self.p["W0"]); SP = S.SPACING; R = 55.0
        ang = math.acos(float(np.clip(c @ u1, -1, 1))); bn = unit(np.cross(c, u1)); n = max(4, int(R * ang / SP)); ts = (np.arange(n) + 0.5) / n
        dirs = np.array([unit(math.sin((1 - t) * ang) * c + math.sin(t * ang) * u1) for t in ts]); rows = []
        for v in np.arange(-W / 2 + 1, W / 2, SP):
            dv = unit(dirs + (v / R) * bn)
            off0 = np.linalg.norm(np.cross(dv * R, c), axis=1); off1 = np.linalg.norm(np.cross(dv * R, u1), axis=1)
            rows.append((dv, (off0 > S.HUB_R) & (off1 > self.hr[0]), ts * R * ang))
        return rows

    def fit(self):
        e, f = S.frame_of(self.cfg.c); d = S.disc(S.HUB_R)
        self._h0base = d[:, :1] * e + d[:, 1:] * f
        self._l0 = self._l0_rows(); poses = np.nonzero(self.kin_ok)[0]
        items = [(8, self._h0base, np.broadcast_to(self.cfg.c, self._h0base.shape).copy(), 140.0)]
        items += [(0, np.zeros((len(dv), 3)), dv, 170.0) for dv, keep, sarc in self._l0]
        res = self.needed(items, poses)
        self._H0 = res[0]; self._L0need = res[1:]
        super().fit()

    def greedy_drop(self, keep0=None, links=True):
        if links and hasattr(self, "_L0need"):                              # link 0 + hub 0 join the drop groups
            self.Lneed = dict(self.Lneed); self.Lneed["L0"] = list(self._L0need); self.Lneed["H0"] = [self._H0]
        return super().greedy_drop(keep0=keep0, links=links)

    def finalize(self):
        L = {k: v for k, v in self.Lneed.items() if k not in ("L0", "H0")}; full = self.Lneed; self.Lneed = L
        try: super().finalize()
        finally: self.Lneed = full
        keep = ~self.drop; c = self.cfg.c; u1 = self.D.u[0]; k = math.tan(S.RAMP * D2R)
        f0 = float(self._H0[keep].max()) if keep.any() else float(self._H0.max()); self.f0 = f0
        F1 = self.f[0]; pts_all = []
        for (dv, keep_s, sarc), r in zip(self._l0, self._L0need):
            r = r[keep].max(0) if keep.any() else r.max(0); Sx = sarc; idx = np.nonzero(keep_s)[0]
            if not len(idx): continue
            for ax, F, j in ((c, f0, idx[0]), (u1, F1, idx[-1])):            # link 0 = upper plate of J0, rides over hub 1 (UP)
                rc = (F + S.UP) / max(float(dv[j] @ ax), 0.2); r = np.maximum(r, rc - k * np.abs(Sx - Sx[j]))
            r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
            pts_all.append(dv[keep_s] * r[keep_s][:, None])
        self.link_pts["L0"] = (0, np.concatenate(pts_all) if pts_all else np.zeros((0, 3)))
        self.rigid["hub0"] = (8, self._h0base + f0 * c)
        self._contact_only(); self._solids()
        e, f = S.frame_of(c); ang = np.linspace(0, 2 * np.pi, 32, endpoint=False); ring = S.HUB_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
        for z in np.linspace(f0, f0 + S.CROWN, 4): self.contact.append((8, z * c + ring))
        dd = S.disc(S.HUB_R, 2.0); self.contact.append((8, (f0 + S.CROWN) * c + dd[:, :1] * e + dd[:, 1:] * f))
        self.cyl["hub0"] = (8, f0 * c, c)
        pts = [z * c + S.HUB_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, S.CROWN, 5) for _ in [0]]
        self.cyl_surf["hub0"] = (8, np.concatenate([p + f0 * c for p in pts] + [(f0 + S.CROWN) * c + S.disc(S.HUB_R, 4.0)[:, :1] * e + S.disc(S.HUB_R, 4.0)[:, 1:] * f]))
        # hub 0 vs hub 1: constant (J0 is a rotation about c) - checked once
        C1 = self.D.c[0] + F1 * u1; Ph1 = self.cyl_surf["hub1"][1]
        self._h01 = float(self.sd_cylr(Ph1, f0 * c, c, S.HUB_R, S.CROWN).min())

    def collide(self, i):
        out = super().collide(i)
        h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k_, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k_] = (R @ cen + t, R @ ax)
        surf = {k_: tf(m, X) for k_, (m, X) in self.cyl_surf.items()}
        L0 = tf(*self.strap["L0"]); L1 = tf(*self.strap["L1"]); L2 = tf(*self.strap["L2"]); Em = tf(*self.Emid)
        bx = self._boxes_at_final(i)
        def vcyl(X, nm, extra=0.0): return float(self.sd_cylr(X, *cyl[nm], self.cyl_r[nm], S.CROWN).min()) - extra if len(X) else 1e9
        def vbox(X, nm, extra=0.0): cen, R, half = bx[nm]; return float(self.sd_box(X, cen, R, half).min()) - extra if len(X) else 1e9
        def kd(A, Bq): return float(cKDTree(Bq).query(A)[0].min()) - 2 * h if len(A) and len(Bq) else 1e9
        c = {"hub0-hub1": self._h01, "hub0-hub2": vcyl(surf["hub2"], "hub0"), "hub0-hub3": vcyl(surf["hub3"], "hub0"),
             "L1-hub0": vcyl(L1, "hub0", h), "L2-hub0": vcyl(L2, "hub0", h), "E-hub0": vcyl(Em, "hub0", h),
             "L0-hub2": vcyl(L0, "hub2", h), "L0-hub3": vcyl(L0, "hub3", h), "L0-L2": kd(L0, L2), "L0-E": kd(L0, Em)}
        for nm in ("knee", "pad"): c[f"{nm}-hub0"] = vbox(surf["hub0"], nm); c[f"{nm}-L0"] = vbox(L0, nm, h)
        cen1, ax1 = cyl["hub1"]; w = L1 - cen1; far1 = np.linalg.norm(w - (w @ ax1)[:, None] * ax1, axis=1) > self.hr[0] + 4
        adj = {"L0-L1": kd(L0, L1[far1])}
        self.last_clear.update({k_: round(v, 1) for k_, v in list(c.items()) + list(adj.items())})
        out = min([out] + list(c.values()))
        if min(adj.values()) < self.ADJ: out = min(out, -1.0)
        return out


def _report(B, params):
    M = Model(B, params)
    s = M.cfg
    base = dict(T_eff=s.Teff, c_seat_ok=s.c_seat_ok, c_azel=[round(float(np.degrees(np.arctan2(s.c[2], -s.c[0]))), 1),
                                                              round(float(np.degrees(np.arcsin(s.c[1]))), 1)])
    if not M.kin_ok.any():
        B.reset(); r = B.report(); r.update(base); r["honest"] = True; return r, M
    r = M.run(); D = M.D
    tk = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    rel = [i for i in tk if abs(M.q0[i]) > 1e-9]
    a1, a2 = (math.degrees(x) for x in D.A); U3 = M.Q @ D.u[2]
    th = np.degrees(np.arccos(np.clip(U3 @ D.u[0], -1, 1)))
    thm = np.minimum(th - abs(a1 - a2), min(a1 + a2, 360 - a1 - a2) - th)
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
    ov = np.nonzero((el >= 140) & (kind == "ws"))[0]
    r.update(base)
    r["why"] = {k: int((M.why == k).sum()) for k in ("relay", "fold", "slide", "flip", "closure", "island", "skin", "parts", "contact")}
    r["relay"] = dict(taken_relayed=len(rel), taken_ws_relayed=sum(1 for i in rel if B.kind[i] == "ws"),
                      q0_range=[round(float(M.q0[tk].min()), 1), round(float(M.q0[tk].max()), 1)] if tk else None,
                      islands=M.islands, flood=M.flood_info)
    r["th_margin_min"] = round(float(thm[tk].min()), 2) if tk else None
    r["overhead"] = f"{sum(1 for i in ov if i in set(tk))}/{len(ov)}"
    k = M.K["ang"][tk] if tk else np.array([])
    r["knee"] = dict(ang=[round(float(k.min()), 1), round(float(k.max()), 1)] if len(k) else None, window=[round(M.p["ang_min"], 1), round(180 - M.p["ang_min"], 1)],
                     relay_ang=[round(float(M.K["ang"][rel].min()), 1), round(float(M.K["ang"][rel].max()), 1)] if rel else None)
    r["f"] = [round(float(x), 1) for x in M.f] + [round(M.f0, 1)]
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def audit(M, B):
    return PK.audit(M, B)


def frozen(P, nc=110, nw=360):
    """fit on Bench(60,160) FAST, wear that exact shape on Bench(nc, nw) (CB_EXACT=1 -> exact); the relay states,
    the clip tracking and the full-grid flood are re-run on the big bench (they are kinematics, not shape)"""
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    r1, M1 = _report(B1, dict(P)); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(Model):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "f0", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_h12", "_h01", "_l0", "_h0base"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=nc, n_ws=nw); t0 = time.time()
    M = Frozen(B, P2); r = M.run()
    tk = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    rel = [i for i in tk if abs(M.q0[i]) > 1e-9]
    D = M.D; a1, a2 = (math.degrees(x) for x in D.A); U3 = M.Q @ D.u[2]
    th = np.degrees(np.arccos(np.clip(U3 @ D.u[0], -1, 1))); thm = np.minimum(th - abs(a1 - a2), min(a1 + a2, 360 - a1 - a2) - th)
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind); ov = np.nonzero((el >= 140) & (kind == "ws"))[0]
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    return dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], secs=round(time.time() - t0, 1),
                why={k: int((M.why == k).sum()) for k in ("relay", "fold", "slide", "flip", "closure", "island", "skin", "parts", "contact")},
                parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"), audit=audit(M, B),
                overhead=f"{sum(1 for i in ov if i in set(tk))}/{len(ov)}", th_margin_min=round(float(thm[tk].min()), 2) if tk else None,
                relay=dict(taken_relayed=len(rel), taken_ws_relayed=sum(1 for i in rel if B.kind[i] == "ws"), islands=M.islands, flood=M.flood_info,
                           q0_range=[round(float(M.q0[tk].min()), 1), round(float(M.q0[tk].max()), 1)] if tk else None),
                knee_ang=[round(float(M.K["ang"][tk].min()), 1), round(float(M.K["ang"][tk].max()), 1)] if tk else None,
                f=[round(float(x), 1) for x in M.f] + [round(M.f0, 1)], T_eff=M.cfg.Teff), M, B


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        t = time.time(); out, M, B = frozen(dict(PARAMS, **par)); out["params"] = par; out["secs_total"] = round(time.time() - t, 1)
        if "--out" in sys.argv: json.dump(out, open(sys.argv[sys.argv.index("--out") + 1], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    nc, nw = (110, 360) if "--big" in sys.argv else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    r, M = _report(B, par)
    print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r.get("why"), f"{time.time() - t:.0f}s", B.mode)
    print({k: r.get(k) for k in ("relay", "th_margin_min", "overhead", "knee", "f", "T_eff", "c_azel", "c_seat_ok")})
    print("parts", r.get("parts_ib14"), r.get("parts_pairs"), "min clear", r.get("min_clear_taken"))
