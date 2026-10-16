"""Concept model: ACROMIAL ROCKER 3R (id acromial-rocker-3r). Fold lever on the pin-knee leader
(skin-normal-3r-pin-knee k10, the leader's k4216 seats): J1 rides a PASSIVE acromial rocker whose angle the arm sets
through an S-U tie rod. Rotations only: 0 passive translations.

Chain: scapula -> J0 PASSIVE pin (pivot boss, axis c through GH) -> rocker (member 7) -> J1 ACTIVE (O20 hub, axis on a
GH ray, beta deg off c) -> link 1 -> J2 ACTIVE -> link 2 -> J3 ACTIVE -> member 3 (hub 3 + E strap) -> pin a -> knee
link -> pin b -> arm pad (the pin-knee closure, unchanged). Tie: rocker stud A -> ball link (3 rot) -> O4 Ti rod ->
miniature U-joint (2 rot) -> stud C on an arm-fixed bracket from the arm pad (member 5).

Kinematics (exact). The rod length L closes |R(c,q0) A0 - Q C0| = L: q0 = phi + s0 acos(x) in closed form (one
branch, the rest pose's). Taken only if |x| <= cos(trans) (transmission >= 25 deg, away from the rod's dead point),
|q0| <= cap (75 deg), ball-link tilt off its stud's normal plane <= `ball` deg and U-joint bend <= `uj` deg (stud / U
axes = the best FIXED mountings over the fit clips, bench independent). The 3R chain is the pin-knee leader's IK on
R0(q0)^T Q and every chain member is then rotated by R0: c passes through GH, so J1 and J2 stay on GH rays and the
pin-knee closure theorem (member 3 vs the arm = rotation about d3 + translation in hub 3's plane) holds unchanged.
Mobility: 3 active; the rocker (1), ball (3) and U (2) are all set by the rod closure; the U kills the rod's idle spin
(an S-S rod would leave it undetermined, R17). 10 fps continuity includes q0.

Parts at real size (added to the pin-knee's): pivot boss O14 (MR63ZZ pair, 9 mm crown) on the scapula base along c;
rocker straps 8 x 3 Ti (pivot -> hub 1 at hub 1's upper level f1 + UP; pivot -> stud A) at >= boss face + UP; ball
link at A and U-joint at C as O8 x 12 bodies (underside disc scored; walls / top contact-checked), their centres
held >= 9 mm over their plates (refit loop); arm bracket 8 x 3 from the arm pad to C; rod O4 sampled every 2 mm on its
skin side (2 rows, scored). Collisions: rod vs hubs 1-3, links 1-2, E, knee, pad, boss, rocker strap 1; ball / U
bodies vs hubs, links, E; rocker + boss vs hubs 2-3, link 2, E, knee, pad (1 mm) and link 1 (adjacent at J1, 0.15 mm
away from hub 1); bracket vs hubs 1-3, links, E (1 mm), knee (adjacent at pin b, 0.15 mm).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/acromial-rocker-3r.py [check|control|redteam|frozen] ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("pk_for_rocker", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
PK = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(PK)
S = PK.S; OSN = PK.OSN; unit = S.unit; D2R = math.pi / 180
ID = "acromial-rocker-3r"
NAME = "Fold lever on the pin-knee leader: J1 on a passive acromial rocker whose angle the arm sets through an S-U tie rod (rotations only)"
LEADER = dict(lE=30.0, lc=25.0, phiE=0.0, phib=-90, stk=5.0, ang_min=30.0, az1=95.8565, el1=65.2093, az2=10.8917,
              el2=54.698, wd=79.148, wa=-13.3653, b3=0.2282, neck=13.0)          # pin-knee k10 (rows/skin-normal-3r-pin-knee.json)
PARAMS = dict(PK.PARAMS); PARAMS.update(LEADER)
PARAMS.update(rocker=1,
              beta=30.0, psi=261.1,          # pivot axis c: beta deg off J1's home axis u1, toward azimuth psi (tangent frame of u1)
              gam=58.8, psiA=262.4,          # stud A direction: gam deg off c toward psiA
              dl=11.3, psiC=84.0,            # stud C direction: dl deg off hub 3's rest seat ray toward psiC (arm-fixed)
              q0r=-18.0,                     # rocker angle at rest (sets the rod length L)
              hA=12.0, hC=12.0,              # ball / U centre over the rest skin along its ray (radius = 2 mm level + h - 2;
                                             # rA / rC, when given, override; the refit loop raises them to plate + 9)
              cap=75.0, trans=25.0, ball=30.0, uj=40.0)
BALL_R, BALL_H, ROD_R, BASE_R = 4.0, 12.0, 2.0, 6.0
PIV_R, PIV_CROWN = 7.0, 9.0
ROCK = 7                                       # member id of the rocker


def tang(v):
    e1 = unit(np.cross(v, [0.3, 1, 0.1])); return e1, np.cross(v, e1)


def tilt(v, ang, psi):
    e1, e2 = tang(v); a = math.radians(ang); p = math.radians(psi)
    return unit(math.cos(a) * v + math.sin(a) * (math.cos(p) * e1 + math.sin(p) * e2))


def strap_rays(da, db, w=S.W_LINK, sp=S.SPACING, r_ref=60.0):
    """unit rays of an 8 mm strap from direction da to db (laid out at r_ref; placed at one radius)"""
    ang = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db)); n = max(3, int(r_ref * ang / sp))
    ts = (np.arange(n) + 0.5) / n
    dirs = unit(np.array([math.sin((1 - t) * ang) * da + math.sin(t * ang) * db for t in ts]))
    return np.concatenate([unit(dirs + (v / r_ref) * bn) for v in np.arange(-w / 2 + sp / 2, w / 2, sp)])


def disc_pts(n, r):
    e, f = S.frame_of(n); d = S.disc(r); return d[:, :1] * e + d[:, 1:] * f


def ring_pts(n, r, z0, z1, nz=4, top=True):
    ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); e, f = S.frame_of(n)
    rg = r * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
    out = [z * n + rg for z in np.linspace(z0, z1, nz)]
    if top: out.append(z1 * n + disc_pts(n, r))
    return np.concatenate(out)


class Design(PK.Design):
    def __init__(self, params=None):
        P = dict(PARAMS); P.update(params or {}); super().__init__(P); self.p = P
        self.rk = bool(P.get("rocker", 1))
        if not self.rk: return
        R = OSN.rest(); Q0 = R["Q0"]; u1 = self.u[0]
        d3r = unit(self.seats["P"][2])                                      # hub 3's rest seat ray (scapula frame)
        self.cp = tilt(u1, P["beta"], P["psi"])
        self.dA = tilt(self.cp, P["gam"], P["psiA"]); dC = tilt(d3r, P["dl"], P["psiC"])
        dA_rest = S.rotm(self.cp, np.array([math.radians(P["q0r"])]))[0] @ self.dA
        self.rA = float(P["rA"]) if P.get("rA") else float(np.linalg.norm(OSN.seat(dA_rest, 0.0)[0])) + P["hA"] - 2.0
        self.rC = float(P["rC"]) if P.get("rC") else float(np.linalg.norm(OSN.seat(dC, 0.0)[0])) + P["hC"] - 2.0
        self.A0 = self.rA * self.dA; self.C0 = Q0.T @ (self.rC * dC); self.dCh = unit(self.C0)
        c = self.cp; self.Ap = (c @ self.A0) * c; self.Aq = self.A0 - self.Ap; self.Ar = np.cross(c, self.Aq)
        qr = math.radians(P["q0r"]); Crest = Q0 @ self.C0
        self.L = float(np.linalg.norm(self.Ap + math.cos(qr) * self.Aq + math.sin(qr) * self.Ar - Crest))
        x, phi = self._x(Crest[None]); acr = math.acos(float(np.clip(x[0], -1, 1)))
        self.s0 = 1.0 if abs(((phi[0] + acr - qr) + np.pi) % (2 * np.pi) - np.pi) < 1e-6 else -1.0
        Z = CB._poses_all(); names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
        Qc = Z["HG"][ii].astype(float); q0, okc, rr, rl = self._rod(Qc)
        g = okc if okc.sum() > 3 else np.ones(len(Qc), bool)
        self.stud = np.linalg.svd(rr[g], full_matrices=False)[2][-1]; self.ubase = unit(rl[g].mean(0))

    def _x(self, C):
        k = 0.5 * (self.A0 @ self.A0 + np.einsum("ij,ij->i", C, C) - self.L ** 2)
        a = C @ self.Ap; xx = C @ self.Aq; yy = C @ self.Ar
        return (k - a) / np.maximum(np.hypot(xx, yy), 1e-9), np.arctan2(yy, xx)

    def _rod(self, Q):
        P = self.p; C = Q @ self.C0; x, phi = self._x(C)
        q0 = (phi + self.s0 * np.arccos(np.clip(x, -1, 1)) + np.pi) % (2 * np.pi) - np.pi
        ok = (np.abs(x) <= math.cos(math.radians(P["trans"]))) & (np.abs(np.degrees(q0)) <= P["cap"])
        cq, sq = np.cos(q0), np.sin(q0); c = self.cp
        A = self.Ap[None] + cq[:, None] * self.Aq[None] + sq[:, None] * self.Ar[None]; rod = unit(C - A)
        rr = (rod @ c)[:, None] * c + cq[:, None] * (rod - (rod @ c)[:, None] * c) - sq[:, None] * np.cross(c, rod)   # rocker frame
        rl = np.einsum("nji,nj->ni", Q, -rod)                                                                       # arm frame
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
        if not getattr(self, "rk", False) or not len(Q): return super().ik(Q)
        q0, okr, *_ = self.rocker(Q); R0 = S.rotm(self.cp, q0)
        q, ok, X1, X2, X3, s = super().ik(np.einsum("nji,njk->nik", R0, Q))
        rot = lambda X: (R0 @ X[0], np.einsum("nij,nj->ni", R0, X[1]))
        return q, ok & okr, rot(X1), rot(X2), rot(X3), s


PK.Design = Design


class Model(PK.Model):
    MINE = ("pvt", "rk1", "rk2", "ball", "ujt", "brk")

    def __init__(self, B, params=None, verbose=False):
        super().__init__(B, params, verbose)
        D = self.D
        if D.rk:
            q0, okr, A, C, tb, tu = D.rocker(self.Q); self.R0 = S.rotm(D.cp, q0); self.Arod, self.Crod = A, C
            self.q0deg, self.tb, self.tu, self.okr = np.degrees(q0), tb, tu, okr
            self.why[(self.why == "fold") & ~okr] = "rod"
        else:
            self.R0 = np.broadcast_to(np.eye(3), (len(B.idx), 3, 3)); self.okr = np.ones(len(B.idx), bool)

    def continuity(self):
        """the pin-knee's 10 fps check with the rocker angle q0 added to the joint vector"""
        Z = self.Z; names = list(Z["NAMES"]); cid = Z["CID"]; ok_at = {}; wrap = PK.wrap
        for nm in CB.FIT:
            ii = np.nonzero(cid == names.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            Qc = Z["HG"][ii].astype(float); q, ok, _, _, _, s = self.D.ik(Qc); K = self.D.knee(s); ok &= K["ok"]
            q0 = self.D.rocker(Qc)[0] if self.D.rk else np.zeros(len(ii))
            qq = np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"], q0]; prev = None
            for j, gi in enumerate(ii):
                good = bool(ok[j])
                if good and prev is not None and np.degrees(np.abs(wrap(qq[j] - qq[prev]))).max() > S.JUMP: good = False
                ok_at[int(gi)] = good; prev = j if ok[j] else None
        return np.array([ok_at.get(int(gi), True) for gi in self.B.idx])

    def T(self, m, i):
        if m == ROCK: return self.R0[i], np.zeros(3)
        return super().T(m, i)

    def _geo(self):
        g = super()._geo(); D = self.D
        if not D.rk: return g
        mem, Bp, ax = g["hub1"]; g["hub1"] = (ROCK, Bp, ax)
        u1, cp = D.u[0], D.cp
        bp = disc_pts(cp, PIV_R); g["pvt"] = (0, bp, cp)
        for nm, da, db, mm in (("rk1", cp, u1, ROCK), ("rk2", cp, D.dA, ROCK)):
            R_ = strap_rays(da, db); g[nm] = (mm, np.zeros_like(R_), R_)
        g["ball"] = (ROCK, disc_pts(D.dA, BALL_R), D.dA); g["ujt"] = (5, disc_pts(D.dCh, BALL_R), D.dCh)
        g["brk"] = (5, disc_pts(D.dCh, BASE_R), D.dCh)                       # U-joint base plate O12 x 3 on the cuff at C
        return g

    def fit(self):
        D = self.D; P = D.p
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        g = self._geo(); self.g = g; off_k = P["tp"] + S.RUN
        order = ["hub1", "hub2", "hub3", "boss", "pad", "knee", "E"] + (list(self.MINE) if D.rk else [])
        items = [(g[n][0], g[n][1], np.broadcast_to(g[n][2], g[n][1].shape).copy(), 140.0) for n in order]
        res = dict(zip(order, self.needed(items, poses)))
        H = {"hub1": res["hub1"], "hub2": res["hub2"], "h3": res["hub3"],
             "stack": np.concatenate([res["boss"], res["pad"], res["knee"] - off_k], 1)}
        self._mine = {n: res[n] for n in self.MINE if n in res}
        self.Hneed, self.Lneed = H, {}; self._HE = res["E"]
        self.greedy_drop(links=False); keep1 = ~self.drop
        for n, M in self._mine.items(): keep1 &= ~(M >= S.BIG / 2).any(1)          # a pose that buries a rocker part: dropped
        self.drop = ~keep1
        f1 = H["hub1"][keep1].max(); f2 = H["hub2"][keep1].max(); tr = H["stack"][keep1].max(); f3 = H["h3"][keep1].max()
        geo = S.Geometry.__new__(S.Geometry); geo.D = D; geo.groups = []; geo.add_links(f1, f2, f3); self.geo = geo
        self._tr_fit = tr
        items, idx = [], []
        for lk in geo.links:
            avoid = ("knee", "pad") if lk["name"] == "L2" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        res = self.needed(items, poses); L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        L["E"] = [self._HE]; self.Lneed = L
        self.greedy_drop(keep0=keep1)
        self.finalize()

    def finalize(self):
        super().finalize()
        D = self.D
        if not D.rk: return
        self.rigid["hub1"] = (ROCK, self.rigid["hub1"][1])
        self.contact = [(ROCK if m == 0 else m, Pc) for m, Pc in self.contact]       # hub 1 walls ride the rocker
        m, cen, ax = self.cyl["hub1"]; self.cyl["hub1"] = (ROCK, cen, ax)
        m, Pc = self.cyl_surf["hub1"]; self.cyl_surf["hub1"] = (ROCK, Pc)
        keep = ~self.drop
        def lvl(nm):
            h = self._mine[nm][keep]; h = h[(h < S.BIG / 2).all(1)] if len(h) else h; return float(h.max()) if len(h) else 200.0
        fb = lvl("pvt"); f1 = self.f[0]
        hk = {"pvt": fb, "rk1": max(lvl("rk1"), fb + S.UP, f1 + S.UP), "rk2": max(lvl("rk2"), fb + S.UP), "brk": lvl("brk")}
        hk["ball"] = max(lvl("ball"), hk["rk2"] + 3.0); hk["ujt"] = max(lvl("ujt"), hk["brk"] + 3.0)
        self.fmine = {k: round(v, 1) for k, v in hk.items()}
        g = self.g
        for nm in ("pvt", "rk1", "rk2", "brk"):
            mm, Bp, N = g[nm]; self.rigid[nm] = (mm, Bp + hk[nm] * np.broadcast_to(N, Bp.shape))
        # ball link / U-joint bodies: O8 x 12 centred on the stud ends (centre radius rA / rC), underside scored
        D_ = D; zA, zC = D_.rA - BALL_H / 2, D_.rC - BALL_H / 2
        self.rigid["ball"] = (ROCK, g["ball"][1] + zA * D_.dA); self.rigid["ujt"] = (5, g["ujt"][1] + zC * D_.dCh)
        self.stud_ok = dict(ball_under_minus_plate_top=round(zA - (hk["rk2"] + 3.0), 1), ball_under_minus_skin_need=round(zA - lvl("ball"), 1),
                            u_under_minus_plate_top=round(zC - (hk["brk"] + 3.0), 1), u_under_minus_skin_need=round(zC - lvl("ujt"), 1))
        self.contact += [(0, ring_pts(D.cp, PIV_R, fb, fb + PIV_CROWN)),
                         (ROCK, ring_pts(D.dA, BALL_R, zA, zA + BALL_H)), (5, ring_pts(D.dCh, BALL_R, zC, zC + BALL_H))]
        for nm in ("rk1", "rk2"):
            mm, Pp = self.rigid[nm]; self.contact.append((mm, Pp + S.T_LINK * unit(Pp)))
        self.contact.append((5, ring_pts(D.dCh, BASE_R, hk["brk"], hk["brk"] + 3.0, nz=2)))
        h = S.T_LINK / 2
        self.mid = {nm: (self.rigid[nm][0], self.rigid[nm][1] + h * unit(self.rigid[nm][1])) for nm in ("rk1", "rk2")}
        self.mid["brk"] = (5, ring_pts(D.dCh, BASE_R, hk["brk"], hk["brk"] + 3.0, nz=2))
        self.mid["pvt"] = (0, ring_pts(D.cp, PIV_R, fb, fb + PIV_CROWN, nz=3))
        self.mid["ball"] = (ROCK, ring_pts(D.dA, BALL_R, zA, zA + BALL_H, nz=3)); self.mid["ujt"] = (5, ring_pts(D.dCh, BALL_R, zC, zC + BALL_H, nz=3))

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
        h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        A, C = self.Arod[i], self.Crod[i]; d = C - A; L2 = d @ d
        def seg(X):
            t = np.clip((X - A) @ d / L2, 0, 1); return np.linalg.norm(X - (A + t[:, None] * d), axis=1) - ROD_R
        W = {nm: tf(*self.mid[nm]) for nm in self.mid}
        W.update({f"s{nm}": tf(*self.strap[nm]) for nm in ("L1", "L2") if len(self.strap[nm][1])})
        W["Em"] = tf(*self.Emid)
        half = {"rk1": h, "rk2": h, "brk": 0.0, "pvt": 0.0, "ball": 0.0, "ujt": 0.0, "sL1": h, "sL2": h, "Em": h}
        cyl = {nm: (self.T(m, i)[0] @ cen + self.T(m, i)[1], self.T(m, i)[0] @ ax) for nm, (m, cen, ax) in self.cyl.items()}
        bx = self._boxes_at_final(i)
        ex, adj = {}, {}
        def vcyl(X, nm, e): return float(self.sd_cyl(X, *cyl[nm]).min()) - e
        def vbox(X, nm, e): cen, R, hf = bx[nm]; return float(self.sd_box(X, cen, R, hf).min()) - e
        trees = {}
        def vpp(a, b):
            if b not in trees: trees[b] = cKDTree(W[b])
            return float(trees[b].query(W[a])[0].min()) - half[a] - half[b]
        # rod (body between the rocker and the arm): vs every part except its own ends
        for nm in ("hub1", "hub2", "hub3"): ex[f"rod-{nm}"] = float(seg(self.cyl_surf[nm][1] @ self.T(self.cyl_surf[nm][0], i)[0].T + self.T(self.cyl_surf[nm][0], i)[1]).min())
        for nm in ("sL1", "sL2", "Em", "pvt", "brk"): ex[f"rod-{nm}"] = float(seg(W[nm]).min()) - half[nm]
        r1 = W["rk1"]; ex["rod-rk1"] = float(seg(r1).min()) - h
        for nm in ("knee", "pad"):
            cen, R, hf = bx[nm]; tt = np.linspace(0, 1, 25); P = A[None] + tt[:, None] * d[None]
            ex[f"rod-{nm}"] = float(self.sd_box(P, cen, R, hf).min()) - ROD_R
        # rocker + boss + ball (scapula / rocker side) vs the chain beyond J1 and the arm side
        for a in ("rk1", "rk2", "pvt", "ball"):
            for nm in ("hub2", "hub3"): ex[f"{a}-{nm}"] = vcyl(W[a], nm, half[a])
            for b in ("sL2", "Em", "brk", "ujt"): ex[f"{a}-{b}"] = vpp(a, b)
            for nm in ("knee", "pad"): ex[f"{a}-{nm}"] = vbox(W[a], nm, half[a])
        for a in ("pvt", "ball"):
            ex[f"{a}-hub1"] = vcyl(W[a], "hub1", 0.0) if a == "pvt" else 1e9
        c1, ax1 = cyl["hub1"]
        def away(X, r):
            w = X - c1; return X[np.linalg.norm(w - (w @ ax1)[:, None] * ax1, axis=1) > r]
        L1f = away(W["sL1"], S.HUB_R + 2)
        for a in ("rk1", "rk2", "pvt", "ball"):
            Xa = W[a] if a != "rk1" else away(W[a], S.HUB_R + 2)
            if len(Xa) and len(L1f):
                v = float(cKDTree(L1f).query(Xa)[0].min()) - h - half[a]
                (ex if a == "pvt" else adj)[f"{a}-L1"] = v           # rocker parts are adjacent to link 1 at J1
        # arm side: bracket + U-joint vs the chain
        for a in ("brk", "ujt"):
            for nm in ("hub1", "hub2", "hub3"): ex[f"{a}-{nm}"] = vcyl(W[a], nm, half[a])
            for b in ("sL1", "sL2", "Em"): ex[f"{a}-{b}"] = vpp(a, b)
            adj[f"{a}-knee"] = vbox(W[a], "knee", half[a])
        self.last_clear.update({k: round(v, 1) for k, v in list(ex.items()) + list(adj.items())})
        out = min([out] + list(ex.values()))
        if adj and min(adj.values()) < self.ADJ: out = min(out, -1.0)
        return out


def _one(B, params):
    M = Model(B, params)
    if not M.kin_ok.any():
        B.reset(); r = B.report(); r["why"] = {k: int((M.why == k).sum()) for k in ("fold", "rod", "slide", "flip", "closure")}
        r["honest"] = True; return r, M
    return M.run(), M


def _report(B, params, iters=2):
    """fit; then (rocker) put the ball / U centres >= 9 mm over their fitted plates and over their own skin need
    (underside >= the fitted 2 mm level), refit (<= iters): the stud geometry the kinematics use is one the parts carry"""
    params = dict(params); r, M = _one(B, params); D = M.D; it = 0
    while D.rk and it < iters and getattr(M, "fmine", None):
        lv = M.fmine; rA = max(lv["rk2"] + 3.0, lv["ball"]) + BALL_H / 2; rC = max(lv["brk"] + 3.0, lv["ujt"]) + BALL_H / 2
        if rA <= D.rA + 0.3 and rC <= D.rC + 0.3: break
        params.update(rA=round(float(max(rA, D.rA)), 1), rC=round(float(max(rC, D.rC)), 1)); r, M = _one(B, params); D = M.D; it += 1
    r["stud_iters"] = it
    if not M.kin_ok.any(): r["params"] = M.p; return r, M
    r["seats"] = dict(a_deg=[round(math.degrees(a), 1) for a in D.A], offset_mm=[round(float(np.linalg.norm(c)), 1) for c in D.c])
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    r["why"] = {k: int((M.why == k).sum()) for k in ("fold", "rod", "slide", "flip", "closure", "skin", "parts", "contact")}
    tk = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    if D.rk:
        r["rocker"] = dict(L=round(D.L, 1), rA=D.rA, rC=D.rC, q0_taken=[round(float(M.q0deg[tk].min()), 1), round(float(M.q0deg[tk].max()), 1)] if tk.any() else None,
                           ball_tilt_max=round(float(M.tb[tk].max()), 1) if tk.any() else None, u_bend_max=round(float(M.tu[tk].max()), 1) if tk.any() else None,
                           levels=getattr(M, "fmine", None), stud=getattr(M, "stud_ok", None))
        nb = sum(len(X) for _, X in M.rigid.values()) + sum(len(X) for _, X in M.link_pts.values()); acc = []
        for i in range(len(B.idx)):
            if B.kind[i] == "clip" and tk[i]: acc.append(B.res[i][nb:nb + 2 * max(2, int(np.linalg.norm(M.Crod[i] - M.Arod[i]) / S.SPACING))])
        if acc: dd = np.concatenate(acc); r["parts_ib14"]["rod"] = [round(float(((dd >= 2) & (dd <= 14)).mean()), 3), round(float(np.median(dd)), 1)]
    r.update(PK.audit(M, B))
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    """lesson (c): fit on Bench(60,160) FAST (incl. the stud refit), wear that exact shape on Bench(nc,nw) without refit"""
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    r1, M1 = _report(B1, dict(P)); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    class Frozen(Model):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_h12", "mid", "fmine", "stud_ok", "_mine"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=nc, n_ws=nw); M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    return dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why={k: int((M.why == k).sum()) for k in ("fold", "rod", "slide", "flip", "closure", "skin", "parts", "contact")},
                parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), params_used=P2)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "frozen":
        t = time.time(); out = frozen(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    if mode == "control": par = dict(par, rocker=0)
    nc, nw = (110, 360) if "--big" in sys.argv else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    r, M = _report(B, par)
    print(json.dumps({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}), "why", r.get("why"), f"{time.time() - t:.0f}s", B.mode)
    print("parts", r.get("parts_ib14")); print("pairs", r.get("parts_pairs"), "min clear", r.get("min_clear_taken"), "res", r.get("res_max"))
    print("rocker", r.get("rocker")); print("overhead", r.get("overhead140"), "near-touch", r.get("near_touch_min_mm"), "gap_near1", r.get("gap_near1"))
    if mode == "redteam":
        lab = lambda i: f"#{i} {B.kind[i]} {B.clip[i][:22]:22s} plane {B.poses[i]['plane']:6.1f} elev {B.poses[i]['elev']:6.1f} axial {B.poses[i]['axial']:6.1f}"
        print("-- poses not taken --")
        for i in [i for i in range(len(B.idx)) if M.why[i]]:
            print(f"  {M.why[i]:7s} {lab(i)}" + (f" clear {M.clear[i]:.1f} ({M.last_pair.get(i)})" if M.why[i] == "parts" else ""))
        print("near-touch low", r.get("near_touch_low"))
        taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
        el = np.array([p["elev"] for p in B.poses]); pl = np.array([p["plane"] for p in B.poses])
        groups = dict(rest=np.argsort(el)[:5], overhead=np.nonzero(el >= 140)[0], across=np.nonzero((pl >= 100) & (el >= 40))[0],
                      behind=np.array([i for i in range(len(B.idx)) if "back" in B.clip[i].lower() or (pl[i] < -30 and el[i] > 20)], int))
        for gname, ii in groups.items():
            ii = list(ii); tk = [i for i in ii if taken(i)]; dd = np.concatenate([B.res[i] for i in tk]) if tk else np.array([np.nan])
            print(f"  {gname:9s} {len(tk)}/{len(ii)}  median {float(np.median(dd)):.1f} mm  ib14 {float(((dd >= 2) & (dd <= 14)).mean()):.3f}  ib10 {float(((dd >= 2) & (dd <= 10)).mean()):.3f}  not taken: {[(int(i), M.why[i]) for i in ii if not taken(i)][:10]}")
