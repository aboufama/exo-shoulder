"""rolling-cone-3r, step 0: LAW-ONLY kinematic ghost of strap-held conical rolling pairs (apex GH) at J1, J2 and / or J3
(catalogue id rolling-cone-3r; write-up docs/concepts/rolling-cone-3r.md). No metal: it asks whether rolling joints
can open the J2 fold window the 3R family is limited by, and WHICH joint's rolling buys the takes.

A rolling pair k (proximal cone axis c fixed in the proximal member, distal cone axis m0 in the distal member, half-angles
ga, gb, touching along the contact generator w at rest) moves the distal member by
    T_k(t) = R(c, x) R(m0, y),   x = t / (1 + r),  y = t r / (1 + r),   r = sin ga / sin gb   (external contact)
(internal contact: m0 on the same side as c, r < 0). Rolling without slip: the relative angular velocity c x' + m y'
lies on the contact line (checked numerically below), so the instantaneous axis of joint k is the contact line and it
walks about c by x as the joint turns. Equivalent: a 2R pair (c, m0) with a FIXED linear coupling y = r x - a knuckle
with a linear law, the one law family the K-law oracle never read with a moving J1 or J3.

Chains (H1 = skin-normal-3r-pin-knee H-g107-1 seats, the cx-0 build base; u1, u2 on GH rays, J3 tilted b3):
  knee type: J1 (roll | pin) -> J2 (roll | pin) -> J3 O20 pin + two-pin knee (J3's own angle and the knee absorb the
             rotation about J3, exactly as H1): the aim map T1(t1) T2(t2) d3 = Q u3 (2 equations, t1, t2).
  rigid type: J1 -> J2 -> J3 all rolling, J3's contact through GH (b3 = 0), cuff rigid on the arm: Q = T1 T2 T3 Q0.
Fold reading: the instantaneous dyad of the contact lines (w1, w2, d3 / w3): th' = angle(w1, w3), a1' = angle(w1, w2),
a2' = angle(w2, w3); margin = min(th' - |a1' - a2'|, a1' + a2' - th') >= 5 deg (the kit's FOLD_MARGIN; = the distance of
the 3x3 Jacobian [w1 w2 w3] from rank loss in the dyad's own angle) and the design's branch sign(w1 . (w2 x w3)).
A ws pose is taken kinematically if Newton from the 3R seed converges (< 0.01 deg) on the branch with margin >= 5; a clip
frame is followed if every 2-deg slerp sub-step from the previous followed frame does (warm-started, no joint step > 10
deg). Overhead = ws poses with elevation >= 140.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/rolling-cone-3r.py ghost '<json cell>'
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial.transform import Rotation as Rot, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as K                                      # noqa: E402

ID = "rolling-cone-3r"
D2R = math.pi / 180
H1 = dict(az1=101.1634, el1=63.8986, az2=30.153, el2=47.0108, wd=70.3931, wa=-8.1248, b3=0.2842)


def unit(x): return K.unit(x)


def rodr(k, a):
    """rotation matrices (..., 3, 3) about unit axes k (..., 3) by angles a (...) rad"""
    k = np.asarray(k, float); a = np.asarray(a, float)
    k, a = np.broadcast_arrays(k, a[..., None]); a = a[..., 0]
    Kx = np.zeros(k.shape[:-1] + (3, 3)); Kx[..., 0, 1] = -k[..., 2]; Kx[..., 0, 2] = k[..., 1]; Kx[..., 1, 0] = k[..., 2]
    Kx[..., 1, 2] = -k[..., 0]; Kx[..., 2, 0] = -k[..., 1]; Kx[..., 2, 1] = k[..., 0]
    s, c = np.sin(a)[..., None, None], np.cos(a)[..., None, None]
    return np.eye(3) + s * Kx + (1 - c) * (Kx @ Kx)


_AX = {}


def chain_axes(seats=H1):
    key = json.dumps(seats, sort_keys=True)
    if key not in _AX: _AX[key] = _chain_axes(seats)
    return _AX[key]


def _chain_axes(seats):
    """u1 (scapula), u2 (scapula, at rest), d3 (J3 direction at rest, scapula), u3 (J3 in the humerus frame), branch, a1, a2"""
    spec = importlib.util.spec_from_file_location("osn_rc", os.path.join(HERE, "offset-skin-normal-3r.py"))
    OSN = importlib.util.module_from_spec(spec); spec.loader.exec_module(OSN)
    P = dict(OSN.PARAMS); P.update(seats); P.update(b1=0.0, b2=0.0)
    D = OSN.Design(P); Q0 = OSN.rest()["Q0"]
    u1, u2, u3 = D.u
    return dict(u1=u1, u2=u2, u3=u3, d3=Q0 @ u3, Q0=Q0, branch=D.branch, A=np.degrees(D.A))


class Joint:
    """kind 'pin' (axis w) or 'roll' (contact w at rest, split plane angle beta about w, ga / gb deg, sign +1 external,
    -1 internal). Axes are expressed in the proximal member's rest frame (= the scapula frame at rest)."""
    def __init__(self, w, kind="pin", ga=0.0, gb=0.0, beta=0.0, sign=1, ref=None):
        self.kind = kind; w = unit(w); self.w = w
        if kind == "pin": return
        ref = unit(np.cross(w, ref if ref is not None else [0, 1, 0]))      # in-plane reference perpendicular to w
        n = unit(rodr(w, beta * D2R) @ ref)                                  # the c-m great circle direction at w
        bn = np.cross(w, n)                                                  # rotation axis carrying w toward n
        self.c = unit(rodr(bn, -ga * D2R) @ w)                               # proximal cone axis, ga back from w
        self.m0 = unit(rodr(bn, sign * gb * D2R) @ w)                        # distal cone axis, gb beyond w (external)
        self.r = sign * math.sin(ga * D2R) / max(math.sin(gb * D2R), 1e-9)
        self.ga, self.gb, self.beta, self.sign = ga, gb, beta, sign

    def T(self, t):
        """relative rotation(s) (..., 3, 3) of the distal member for joint values t (...) rad, proximal frame"""
        t = np.asarray(t, float)
        if self.kind == "pin": return rodr(self.w, t)
        x = t / (1 + self.r); y = t * self.r / (1 + self.r)
        return rodr(self.c, x) @ rodr(self.m0, y)

    def wnow(self, t):
        """instantaneous axis (contact line) in the proximal frame"""
        if self.kind == "pin": return np.broadcast_to(self.w, np.shape(t) + (3,)).copy()
        x = np.asarray(t, float) / (1 + self.r)
        return np.einsum("...ij,j->...i", rodr(self.c, x), self.w)


class Ghost:
    def __init__(self, cell, seats=H1):
        A = chain_axes(seats); self.A = A; self.cell = cell
        self.rigid = bool(cell.get("rigid", 0))
        mk = lambda k, w: Joint(w, **cell[k]) if cell.get(k) else Joint(w)
        # the 3R's reference configuration is Q = I (osn Design: u2 = circ_int(u1, a1, u3, a2) with u3 in the humerus
        # frame), so J3's direction in link 2's reference frame is u3 itself and the rigid cuff's reference is Q0 = I
        u3r = unit(A["u3"])
        if self.rigid:      # J3 through GH: the un-tilted J3 seat ray (b3 = 0)
            A0 = chain_axes(dict(seats, b3=0.0)); u3r = unit(A0["u3"]); self.u3h = A0["u3"]
            self.j = [mk("J1", A0["u1"]), mk("J2", A0["u2"]), mk("J3", u3r)]; self.branch = A0["branch"]
        else:
            self.u3h = A["u3"]; self.j = [mk("J1", A["u1"]), mk("J2", A["u2"])]; self.branch = A["branch"]
        self.d3 = u3r; self.Q0 = np.eye(3)

    # forward map, n joint values (P, n) rad
    def fk(self, t):
        T1 = self.j[0].T(t[:, 0]); T2 = self.j[1].T(t[:, 1]); M2 = T1 @ T2
        w1 = self.j[0].wnow(t[:, 0]); w2 = np.einsum("pij,pj->pi", T1, self.j[1].wnow(t[:, 1]))
        if self.rigid:
            T3 = self.j[2].T(t[:, 2]); M3 = M2 @ T3; w3 = np.einsum("pij,pj->pi", M2, self.j[2].wnow(t[:, 2]))
            return M3, w1, w2, w3
        return M2, w1, w2, np.einsum("pij,j->pi", M2, self.d3)

    def resid(self, t, Q):
        M, *_ = self.fk(t)
        if self.rigid: return Rot.from_matrix(np.einsum("pji,pjk->pik", M @ self.Q0, Q)).as_rotvec()   # (P, 3)
        return np.einsum("pij,j->pi", M, self.d3) - np.einsum("pij,j->pi", Q, self.u3h)

    def solve(self, Q, t0, iters=30):
        n = 3 if self.rigid else 2; t = t0.copy(); h = 1e-6
        for _ in range(iters):
            e = self.resid(t, Q); Jc = []
            for k in range(n):
                tp = t.copy(); tp[:, k] += h; Jc.append((self.resid(tp, Q) - e) / h)
            J = np.stack(Jc, -1)                                             # (P, 3, n)
            JTJ = np.einsum("pik,pil->pkl", J, J) + 1e-9 * np.eye(n); g = np.einsum("pik,pi->pk", J, e)
            dt = -np.linalg.solve(JTJ, g[..., None])[..., 0]
            dt = np.clip(dt, -0.3, 0.3); t = t + dt
            if np.abs(dt).max() < 1e-9: break
        e = self.resid(t, Q); err = np.degrees(np.linalg.norm(e, axis=1))
        return t, err

    def margin(self, t):
        _, w1, w2, w3 = self.fk(t)
        ang = lambda a, b: np.degrees(np.arccos(np.clip((unit(a) * unit(b)).sum(-1), -1, 1)))
        th, a1, a2 = ang(w1, w3), ang(w1, w2), ang(w2, w3)
        m = np.minimum.reduce([th - np.abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th])
        sgn = np.sign((w2 * np.cross(w1, w3)).sum(-1))
        return m, sgn, th

    def seed3r(self, Q):
        """the plain 3R's joint values on the design branch (closure), as the Newton seed (rad, total rolling angle)"""
        A = self.A; b = A["u1"] if not self.rigid else self.j[0].w
        u2r = self.j[1].w; d3r = self.d3; u3h = self.u3h
        w = np.einsum("pij,j->pi", Q, u3h)
        a1 = math.degrees(math.acos(float(np.clip(b @ u2r, -1, 1)))); a2 = math.degrees(math.acos(float(np.clip(u2r @ d3r, -1, 1))))
        p, ok, _ = K.closure(np.broadcast_to(b, w.shape), w, a1, a2, self.branch, margin_deg=-90)
        q1 = np.radians(K.axis_angle(b, u2r, p))
        R1 = rodr(b, q1); u3_1 = np.einsum("pji,pj->pi", R1, w)                # J3 direction in link 1's frame
        q2 = np.radians(K.axis_angle(u2r, d3r, u3_1))
        if not self.rigid: return np.stack([q1, q2], -1)
        R2 = R1 @ rodr(u2r, q2); G = np.einsum("pji,pjk->pik", R2, Q) @ self.Q0.T  # link2 -> arm residual about d3
        q3 = Rot.from_matrix(G).as_rotvec() @ d3r
        return np.stack([q1, q2, q3], -1)

    def take(self, Q, t0=None, margin_deg=5.0):
        if t0 is None: t0 = self.seed3r(Q)
        t, err = self.solve(Q, t0)
        m, sgn, th = self.margin(t)
        ok = (err < 0.01) & (m >= margin_deg) & (sgn == self.branch) & np.all(np.abs(np.degrees(t)) < 170, axis=1)
        return ok, t, m, th


def run(cell, nc=110, nw=360, seats=H1, margin_deg=5.0):
    B = CB.Bench(nc, nw); Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float); kind = np.array(B.kind)
    elev = np.array([p["elev"] for p in B.poses]); G = Ghost(cell, seats)
    ok, t, m, th = G.take(HG, margin_deg=margin_deg)
    ws = kind == "ws"; over = ws & (elev >= 140)
    # clip continuity: 2-deg slerp sub-steps from the previous followed frame, warm-started
    fol = np.zeros(len(HG), bool)
    for _, js in B.clip_order().items():
        prev = None
        for j in js:
            if prev is None:
                fol[j] = bool(ok[j]); prev = j if ok[j] else None
                continue
            ang = np.degrees(Rot.from_matrix(HG[prev].T @ HG[j]).magnitude()); n = int(max(2, math.ceil(ang / 2.0) + 1))
            S = Slerp([0, 1], Rot.from_matrix(np.stack([HG[prev], HG[j]])))(np.linspace(0, 1, n)).as_matrix()
            tc = t[prev:prev + 1].copy(); good = True
            for s in S[1:]:
                okk, tn, mm, _ = G.take(s[None], t0=tc, margin_deg=margin_deg)
                if not okk[0] or np.degrees(np.abs(tn - tc)).max() > 10: good = False; break
                tc = tn
            if good: fol[j] = True; t[j] = tc[0]; prev = j
    res = dict(ws=int((ok & ws).sum()), n_ws=int(ws.sum()), clip=int(fol[~ws].sum()), n_clip=int((~ws).sum()),
               over=int((ok & over).sum()), n_over=int(over.sum()),
               th_min=float(th[ok].min()) if ok.any() else None, th_max=float(th[ok].max()) if ok.any() else None,
               t_range_deg=[[round(float(np.degrees(t[ok, k]).min()), 1), round(float(np.degrees(t[ok, k]).max()), 1)]
                            for k in range(t.shape[1])] if ok.any() else None)
    res["kin_gap_reach"] = round(100 * max(0.0, 0.90 - res["ws"] / res["n_ws"]), 2)
    return res, dict(ok=ok, fol=fol, t=t, m=m, th=th, ws=ws, over=over, elev=elev, B=B, G=G)


def check_rolling():
    """numerical check: the relative angular velocity of a rolling pair lies on its contact line"""
    j = Joint(unit([0.3, 0.8, 0.5]), "roll", ga=25, gb=10, beta=30)
    for t in (0.0, 0.4, -0.9):
        h = 1e-6; W = (j.T(t + h) - j.T(t)) @ j.T(t).T / h
        om = np.array([W[2, 1], W[0, 2], W[1, 0]]); wn = j.wnow(t)
        print(f"t {t:+.2f}: angle(omega, contact) {np.degrees(np.arccos(abs(unit(om) @ wn))):.2e} deg, |omega| {np.linalg.norm(om):.4f}")


def export_viz(cell, seats=H1):
    """geometry for docs/concepts/viz/concepts/rolling-cone-3r.js: per joint the sun / planet cone axes, the contact at
    rest, the ratio r (all in the scapula frame at the reference configuration Q = I), the rest-pose joint values"""
    G = Ghost(cell, seats); spec = importlib.util.spec_from_file_location("osn_rc2", os.path.join(HERE, "offset-skin-normal-3r.py"))
    OSN = importlib.util.module_from_spec(spec); spec.loader.exec_module(OSN); Q0 = OSN.rest()["Q0"]
    ok, t, m, th = G.take(Q0[None])
    J = []
    for j in G.j:
        if j.kind == "pin": J.append(dict(kind="pin", w=[round(float(x), 5) for x in j.w]))
        else: J.append(dict(kind="roll", c=[round(float(x), 5) for x in j.c], m0=[round(float(x), 5) for x in j.m0],
                            w=[round(float(x), 5) for x in j.w], r=round(float(j.r), 5), ga=j.ga, gb=j.gb))
    return dict(J=J, rigid=int(G.rigid), u3h=[round(float(x), 5) for x in G.u3h], branch=G.branch,
                t_rest_deg=[round(float(x), 3) for x in np.degrees(t[0])], rest_ok=bool(ok[0]), rest_margin=round(float(m[0]), 2))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "ghost"
    if cmd == "checkroll": check_rolling(); sys.exit()
    if cmd == "viz": print(json.dumps(export_viz(json.loads(sys.argv[2])))); sys.exit()
    cell = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    t0 = time.time(); res, _ = run(cell); res["sec"] = round(time.time() - t0, 1)
    print(json.dumps(dict(cell=cell, **res)))
