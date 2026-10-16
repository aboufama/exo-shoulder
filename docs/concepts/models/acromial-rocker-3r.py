"""Concept model: ACROMIAL ROCKER 3R (id acromial-rocker-3r). Fold lever on the zero-passive spherical 3R at the leader's
seats (offset-skin-normal-3r k4216, slides 0 = round-3 pick 1).

Chain: scapula base -> J0 PASSIVE pin (pivot boss on the acromion, axis c through GH) -> rocker plate -> J1 ACTIVE
(O20 hub, axis through GH, beta deg off c) -> link 1 -> J2 -> link 2 -> J3 -> arm (hub 3 + neck arm-fixed).
Tie: rocker stud A -> ball link (3 rot) -> O4 Ti rod -> miniature U-joint (2 rot) -> stud C on a bracket off hub 3.
The rocker angle q0 is set by the rod length: |R(c,q0) A0 - Q C0| = L, closed form q0 = phi + s0 acos(x); taken only
if |x| <= cos(trans) (transmission >= 25 deg, no dead point), |q0| <= cap (75), the ball link tilt <= `ball` deg off
its stud's normal plane and the U-joint bend <= `uj` deg (stud / U axes = the best fixed mounting over the fit clips,
bench independent). The chain is the leader's IK on R0(q0)^T Q, every member then rotated by R0 (the pivot passes
through GH, so no translation). 3 ACTIVE DOF; passive: pin 1 + ball 3 + U 2, all set by the closure (S-U: no idle
rod spin); 0 passive translations.

SPEC FIX: slides 0 with c3 != 0 (the judge's 'spherical reference' at b3 0.228) puts hub 3 off its own axis line
(link 2's hub-3 end and the arm's hub 3 disagree by 2|c3| sin(q3/2)); here every line goes through GH (c = 0), so the
plain-3R control (rocker=0) in this file is an exact spherical chain.

Parts at real size: the leader's O20 x 12.25 hubs, 8 x 3 straps, neck; + pivot boss (O14, base plate + MR63ZZ pair +
rocker = 9 mm crown), rocker tabs (8 x 3, pivot -> hub 1 and pivot -> A, at >= hub 1's upper level and the boss's
rocker level), ball link and U-joint (O8 x 12 each: underside disc scored, side walls contact-checked), bracket hub 3 ->
C (8 x 3), rod O4 sampled on its skin side every 2 mm (2 rows). Collisions (>= 1 mm, adjacent 0.15): rod vs hubs 1-3,
links 1-2, boss, rocker tab 1; rocker tabs vs link 2, hubs 2-3, link 1 away from J1; boss vs links 1-2, hubs 2-3.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/acromial-rocker-3r.py [check|control|redteam] ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("osn_for_rocker", os.path.join(HERE, "offset-skin-normal-3r.py"))
O = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(O)
S = O.S; unit = S.unit
ID = "acromial-rocker-3r"
NAME = "Fold lever on the pin-knee leader: J1 on a passive acromial rocker whose angle the arm sets through an S-U tie rod (rotations only)"
D2R = math.pi / 180
LEADER = {'inv': 1, 'b1': 0.0, 'b2': 0.0, 'az1': 95.8565, 'el1': 65.2093, 'az2': 10.8917, 'el2': 54.698, 'wd': 79.148,
          'wa': -13.3653, 'b3': 0.2282, 'neck': 16.8348, 'S_max': 25.0, 'centre': 1, 'R_tol': 0.5, 'remote': 1, 'ramp': 1,
          'S_auto': 1, 'jam_contact': 1, 'drop': 1, 'slides': 0, 'vfix': 1}
PARAMS = dict(O.PARAMS); PARAMS.update(LEADER)
PARAMS.update(rocker=1,
              beta=30.0, psi=18.7,          # pivot axis c: beta deg off J1's home axis, toward azimuth psi
              gam=73.7, psiA=286.3,         # stud A: gam deg off c toward psiA (scapula side, on the rocker)
              dl=5.5, psiC=107.6,           # stud C: dl deg off hub 3's rest direction toward psiC (arm side)
              q0r=-29.6,                    # rocker angle at rest (sets the rod length)
              hA=9.0, hC=9.0,               # ball / U centre above the 2 mm skin level at rest (3 mm plate + 6 mm to the centre)
              cap=75.0, trans=25.0, ball=30.0, uj=40.0)
BALL_R, BALL_H, ROD_R = 4.0, 12.0, 2.0
BOSS_R, BOSS_CROWN = 7.0, 9.0


def tang(v):
    e1 = unit(np.cross(v, [0.3, 1, 0.1])); return e1, np.cross(v, e1)


def tilt(v, ang, psi):
    e1, e2 = tang(v); a = math.radians(ang); p = math.radians(psi)
    return unit(math.cos(a) * v + math.sin(a) * (math.cos(p) * e1 + math.sin(p) * e2))


def rodr(c, q):
    """Rodrigues about unit c by angles q (n,) -> (n,3,3)"""
    return S.rotm(c, q)


class Design(O.Design):
    def __init__(self, params=None):
        super().__init__(dict(PARAMS, **(params or {})))
        P = self.p
        if not P.get("slides", 1): self.c = [np.zeros(3)] * 3          # exact spherical chain: every line through GH
        self.rk = bool(P.get("rocker", 1))
        if not self.rk: return
        R = O.rest(); Q0 = R["Q0"]; u1 = self.u[0]; d3r = Q0 @ self.u[2]
        self.cp = tilt(u1, P["beta"], P["psi"])                          # pivot axis (scapula frame, through GH)
        dA = tilt(self.cp, P["gam"], P["psiA"]); dC = tilt(d3r, P["dl"], P["psiC"])
        self.rA = float(P["rA"]) if P.get("rA") else float(np.linalg.norm(O.seat(dA, 0.0)[0])) + P["hA"]   # ball centre
        self.rC = float(P["rC"]) if P.get("rC") else float(np.linalg.norm(O.seat(dC, 0.0)[0])) + P["hC"]   # (default: rest 2 mm level + 9)
        self.dA, self.dC = dA, dC
        self.A0 = self.rA * dA; self.C0 = Q0.T @ (self.rC * dC)          # A in the rocker frame (q0 = 0), C in the home arm frame
        c = self.cp; self.Ap = (c @ self.A0) * c; self.Aq = self.A0 - self.Ap; self.Ar = np.cross(c, self.Aq)
        Z = CB._poses_all(); j = R["j"]
        qr = math.radians(P["q0r"]); Crest = Z["HG"][j].astype(float) @ self.C0
        self.L = float(np.linalg.norm(self.Ap + math.cos(qr) * self.Aq + math.sin(qr) * self.Ar - Crest))
        x, phi = self._x(Crest[None]); acr = math.acos(float(np.clip(x[0], -1, 1)))
        self.s0 = 1.0 if abs(((phi[0] + acr - qr) + np.pi) % (2 * np.pi) - np.pi) < 1e-6 else -1.0
        # fixed mountings, bench independent: ball stud axis = least-variance normal of the rod directions in the rocker
        # frame, U base axis = mean rod direction in the arm frame, both over every fit-clip frame (full rate)
        names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
        Qc = Z["HG"][ii].astype(float); q0, okc, rr, rl = self._rod(Qc)
        g = okc if okc.sum() > 3 else np.ones(len(Qc), bool)
        self.stud = np.linalg.svd(rr[g], full_matrices=False)[2][-1]; self.ubase = unit(rl[g].mean(0))

    def _x(self, C):
        k = 0.5 * (self.A0 @ self.A0 + np.einsum("ij,ij->i", C, C) - self.L ** 2)
        a = C @ self.Ap; xx = C @ self.Aq; yy = C @ self.Ar
        return (k - a) / np.hypot(xx, yy), np.arctan2(yy, xx)

    def _rod(self, Q):
        P = self.p; C = Q @ self.C0; x, phi = self._x(C)
        q0 = (phi + self.s0 * np.arccos(np.clip(x, -1, 1)) + np.pi) % (2 * np.pi) - np.pi
        ok = (np.abs(x) <= math.cos(math.radians(P["trans"]))) & (np.abs(np.degrees(q0)) <= P["cap"])
        cq, sq = np.cos(q0), np.sin(q0); c = self.cp
        A = self.Ap[None] + cq[:, None] * self.Aq[None] + sq[:, None] * self.Ar[None]; rod = unit(C - A)
        rr = (rod @ c)[:, None] * c + cq[:, None] * (rod - (rod @ c)[:, None] * c) - sq[:, None] * np.cross(c, rod)
        rl = np.einsum("nji,nj->ni", Q, -rod)
        return q0, ok, rr, rl

    def rocker(self, Q):
        """q0 (n,) rad, ok (n,), A (n,3), C (n,3), ball tilt, U bend (deg)"""
        q0, ok, rr, rl = self._rod(Q); P = self.p
        tb = np.degrees(np.arcsin(np.clip(np.abs(rr @ self.stud), 0, 1))); tu = np.degrees(np.arccos(np.clip(rl @ self.ubase, -1, 1)))
        ok = ok & (tb <= P["ball"]) & (tu <= P["uj"])
        cq, sq = np.cos(q0), np.sin(q0)
        A = self.Ap[None] + cq[:, None] * self.Aq[None] + sq[:, None] * self.Ar[None]
        return q0, ok, A, Q @ self.C0, tb, tu

    def ik(self, Q):
        if not getattr(self, "rk", False):
            q, ok, X1, X2, X3, s = super().ik(Q); return np.c_[q, np.zeros(len(Q))], ok, X1, X2, X3, s
        q0, okr, *_ = self.rocker(Q); R0 = rodr(self.cp, q0)
        q, ok, X1, X2, X3, s = super().ik(np.einsum("nji,njk->nik", R0, Q))
        rot = lambda X: (R0 @ X[0], np.einsum("nij,nj->ni", R0, X[1]))
        return np.c_[q, q0], ok & okr, rot(X1), rot(X2), rot(X3), s


def strap_rays(da, db, w=S.W_LINK, sp=S.SPACING, r_ref=60.0):
    """unit rays of an 8 mm strap between two directions (laid out at r_ref; fitted radially)"""
    ang = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db)); n = max(3, int(r_ref * ang / sp))
    ts = (np.arange(n) + 0.5) / n; dirs = np.array([unit(math.sin((1 - t) * ang) * da + math.sin(t * ang) * db) for t in ts]) / max(math.sin(ang), 1e-9)
    dirs = unit(dirs); out = [unit(dirs + (v / r_ref) * bn) for v in np.arange(-w / 2 + sp / 2, w / 2, sp)]
    return np.concatenate(out)


def disc_pts(n, r):
    e, f = S.frame_of(n); d = S.disc(r); return d[:, :1] * e + d[:, 1:] * f


class Geometry(S.Geometry):
    def __init__(self, D):
        super().__init__(D)
        if not getattr(D, "rk", False): return
        for g in self.groups:
            if g["name"] == "hub1": g["mem"] = 6                       # hub 1 rides on the rocker
        u1 = D.u[0]; cp = D.cp; Q0 = O.rest()["Q0"]; d3h = D.u[2]; dCh = Q0.T @ D.dC
        def add(name, mem, Bp, N): self.groups.append(dict(name=name, mem=mem, B=Bp, N=N, shared="own", off=np.zeros(len(Bp))))
        Bb = disc_pts(cp, BOSS_R); add("boss", 0, Bb, np.broadcast_to(cp, Bb.shape).copy())
        for nm, da, db in (("rk1", cp, u1), ("rk2", cp, D.dA)):
            R_ = strap_rays(da, db); add(nm, 6, np.zeros_like(R_), R_)
        R_ = strap_rays(d3h, unit(dCh)); add("brk", 5, np.zeros_like(R_), R_)


S.Geometry = Geometry
O.Design = Design              # this module's private copy of the leader's model builds the rocker design


class Model(O.Model):
    MINE = ("boss", "rk1", "rk2", "brk")

    def __init__(self, B, params=None, verbose=False):
        super().__init__(B, params, verbose)
        D = self.D
        if D.rk:
            q0, okr, A, C, tb, tu = D.rocker(self.Q); self.R0 = rodr(D.cp, q0); self.Arod, self.Crod = A, C
            self.q0deg, self.tb, self.tu = np.degrees(q0), tb, tu
            bad = ~okr & (self.why == "fold"); self.why[bad] = "rod"           # poses lost to the rod (dead point / cap / rod ends)
        else: self.R0 = np.broadcast_to(np.eye(3), (len(B.idx), 3, 3))

    def T(self, m, i):
        if m == 6: return self.R0[i], np.zeros(3)
        return super().T(m, i)

    def finalize(self):
        super().finalize()
        D = self.D
        if not D.rk: return
        keep = ~self.drop; H = self.Hneed
        def lvl(nm):
            h = H[nm][keep]; h = h[(h < S.BIG / 2).all(1)] if len(h) else h; return float(h.max()) if len(h) else 200.0
        fb = lvl("boss"); f1 = self.f[0]
        hk = {"boss": fb, "rk1": max(lvl("rk1"), fb + S.UP, f1 + S.UP), "rk2": max(lvl("rk2"), fb + S.UP), "brk": max(lvl("brk"), self.f[2] + S.UP)}
        self.fmine = {k: round(v, 1) for k, v in hk.items()}
        for g in self.geo.groups:
            if g["name"] in self.MINE: self.rigid[g["name"]] = (g["mem"], g["B"] + (hk[g["name"]] + g["off"])[:, None] * g["N"])
        # ball link (rocker, at A) and U-joint (arm, at C): O8 x 12 bodies centred on the stud ends, underside scored
        A0 = D.A0; Ch = D.C0; nA = unit(A0); nC = unit(Ch)
        self.rigid["ball"] = (6, A0 + (-BALL_H / 2) * nA + disc_pts(nA, BALL_R))
        self.rigid["ujoint"] = (5, Ch + (-BALL_H / 2) * nC + disc_pts(nC, BALL_R))
        self.stud_ok = dict(ball_over_plate=round(float(np.linalg.norm(A0) - BALL_H / 2 - (hk["rk2"] + 3.0)), 1),
                            u_over_bracket=round(float(np.linalg.norm(Ch) - BALL_H / 2 - (hk["brk"] + 3.0)), 1))
        ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        def ring(n, cen, r, z0, z1):
            e, f = S.frame_of(n); rg = r * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
            return np.concatenate([cen + z * n + rg for z in np.linspace(z0, z1, 4)] + [cen + z1 * n + disc_pts(n, r)])
        self.contact = list(self.contact)
        for k in range(len(self.contact)):                             # hub 1 walls ride the rocker
            m, Pc = self.contact[k]
            if m == 0: self.contact[k] = (6, Pc)
        self.contact += [(0, ring(D.cp, np.zeros(3), BOSS_R, fb, fb + BOSS_CROWN)),
                         (6, ring(nA, np.zeros(3), BALL_R, np.linalg.norm(A0) - BALL_H / 2, np.linalg.norm(A0) + BALL_H / 2)),
                         (5, ring(nC, np.zeros(3), BALL_R, np.linalg.norm(Ch) - BALL_H / 2, np.linalg.norm(Ch) + BALL_H / 2))]

    def _solids(self):
        super()._solids()
        if not self.D.rk: return
        m, cen, ax = self.cyl["hub1"]; self.cyl["hub1"] = (6, cen, ax)
        m, P = self.cyl_surf["hub1"]; self.cyl_surf["hub1"] = (6, P)

    def rod_pts(self, i, under=True):
        A, C = self.Arod[i], self.Crod[i]; L = np.linalg.norm(C - A); n = max(2, int(L / S.SPACING))
        t = (np.arange(n) + 0.5) / n; P = A[None] + t[:, None] * (C - A)[None]
        if not under: return P
        d = unit(C - A); rad = unit(P); lat = unit(np.cross(d, rad)); rad = unit(rad - (rad @ d)[:, None] * d)
        return np.concatenate([P - ROD_R * rad + s * lat for s in (-1.0, 1.0)])

    def metal_points(self, i):
        P = super().metal_points(i)
        if not self.D.rk: return P
        return np.concatenate([P, self.rod_pts(i) @ self.RS[i].T])

    def collide(self, i):
        out = super().collide(i)
        if not self.D.rk: return out
        def tf(m, P): R, t = self.T(m, i); return P @ R.T + t
        A, C = self.Arod[i], self.Crod[i]; d = C - A; L2 = d @ d
        def seg(P):
            t = np.clip((P - A) @ d / L2, 0, 1); return np.linalg.norm(P - (A + t[:, None] * d), axis=1) - ROD_R
        h = S.T_LINK / 2; ex = {}
        for nm in ("hub1", "hub2", "hub3"):
            m, P = self.cyl_surf[nm]; ex[f"rod-{nm}"] = float(seg(tf(m, P)).min())
        for nm in ("L1", "L2"):
            m, P = self.strap[nm]
            if len(P): ex[f"rod-{nm}"] = float(seg(tf(m, P)).min()) - h
        for nm in ("boss", "rk1"):
            m, P = self.rigid[nm]; Pw = tf(m, P)
            if nm == "rk1": Pw = Pw[np.linalg.norm(Pw - A, axis=1) > 10]
            if len(Pw): ex[f"rod-{nm}"] = float(seg(Pw).min()) - (h if nm != "boss" else 0)
        RK = np.concatenate([tf(6, self.rigid[nm][1]) for nm in ("rk1", "rk2")]); BS = tf(0, self.rigid["boss"][1])
        for nm in ("hub2", "hub3"):
            mc, cen, ax = self.cyl[nm]; R, t = self.T(mc, i); cw, aw = R @ cen + t, R @ ax
            ex[f"rocker-{nm}"] = float(self.sd_cyl(RK, cw, aw).min()) - h; ex[f"boss-{nm}"] = float(self.sd_cyl(BS, cw, aw).min())
        from scipy.spatial import cKDTree
        tr = cKDTree(np.concatenate([RK, BS])); adj = None
        for nm in ("L1", "L2"):
            m, P = self.strap[nm]; Pw = tf(m, P)
            if nm == "L1":                                            # adjacent at J1: away from hub 1 only
                mc, cen, ax = self.cyl["hub1"]; R, t = self.T(mc, i); w = Pw - (R @ cen + t); ax = R @ ax
                Pw = Pw[np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > S.HUB_R + 2]
            if len(Pw):
                v = float(tr.query(Pw)[0].min()) - 2 * h
                if nm == "L1": adj = v                                   # J1's two members: running gap only
                else: ex[f"rocker-{nm}"] = v
        self.last_clear.update({k: round(v, 1) for k, v in ex.items()})
        out = min([out] + list(ex.values()))
        if adj is not None:
            self.last_clear["rocker-L1(adj)"] = round(adj, 2)
            if adj < self.ADJ: out = min(out, -1.0)
        return out


def _report(B, params, iters=3):
    """fit; then (rocker) put the ball / U centres on their fitted plates (plate level + 3 + 6 mm) and refit, up to
    `iters` times: the stud geometry the kinematics use must be the one the parts can carry"""
    params = dict(params); M = Model(B, params); r = M.run(); D = M.D
    for it in range(iters if D.rk else 0):
        lv = getattr(M, "fmine", None)
        if not lv: break
        rA, rC = lv["rk2"] + 3.0 + BALL_H / 2, lv["brk"] + 3.0 + BALL_H / 2
        if abs(rA - D.rA) < 1.0 and abs(rC - D.rC) < 1.0: break
        params.update(rA=round(float(max(rA, D.rA)), 1), rC=round(float(max(rC, D.rC)), 1)); M = Model(B, params); r = M.run(); D = M.D
    r["stud_iters"] = it + 1 if D.rk else 0
    r["seats"] = dict(a_deg=[round(math.degrees(a), 1) for a in D.A], offset_mm=[round(float(np.linalg.norm(c)), 1) for c in D.c])
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    r["why"]["rod"] = int((M.why == "rod").sum())
    if D.rk:
        tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
        r["rocker"] = dict(L=round(D.L, 1), rA=round(D.rA, 1), rC=round(D.rC, 1), q0_taken=[round(float(M.q0deg[tk].min()), 1), round(float(M.q0deg[tk].max()), 1)] if tk.any() else None,
                           ball_tilt_max=round(float(M.tb[tk].max()), 1) if tk.any() else None, u_bend_max=round(float(M.tu[tk].max()), 1) if tk.any() else None,
                           levels=getattr(M, "fmine", None), stud=getattr(M, "stud_ok", None))
        nb = sum(len(X) for _, X in M.rigid.values()) + sum(len(X) for _, X in M.link_pts.values()); acc = []
        for i in range(len(B.idx)):
            d = B.res[i]
            if B.kind[i] == "clip" and d is not None and float(np.min(d)) >= 0: acc.append(d[nb:nb + 2 * max(2, int(np.linalg.norm(M.Crod[i] - M.Arod[i]) / S.SPACING))])
        if acc: dd = np.concatenate(acc); r["parts_ib14"]["rod"] = [round(float(((dd >= 2) & (dd <= 14)).mean()), 3), round(float(np.median(dd)), 1)]
    el = np.array([p["elev"] for p in B.poses]); tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    ws = np.array([k == "ws" for k in B.kind]); oh = ws & (el >= 140)
    r["overhead140"] = dict(ws_taken=f"{int(tk[oh].sum())}/{int(oh.sum())}", why={k: int((M.why[oh] == k).sum()) for k in set(M.why[oh]) if k})
    mins = [float(np.min(B.res[i])) for i in range(len(B.idx)) if tk[i]]
    r["near_touch_min_mm"] = round(min(mins), 2) if mins else None
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "control": par = dict(par, rocker=0)
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}), "why", r["why"], f"{time.time() - t:.0f}s")
    print("parts", r["parts_ib14"]); print("pairs", r["parts_pairs"], "min clear", r.get("min_clear_taken"), "res", r.get("res_max"))
    print("rocker", r.get("rocker")); print("overhead", r["overhead140"], "near-touch", r["near_touch_min_mm"])
