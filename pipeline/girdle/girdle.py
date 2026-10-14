"""Girdle kinematics shared by P0 (p0_base_mount.py) and the R10 judge (judge/base_mount.py).

Frame: thorax, mm, x anterior, y up, z right, origin = the right GH centre at rest (avg/body_pose.py). The rig moves the
GH centre relative to the thorax by lift(elev) (segs()) and rotates the scapula about the GH centre by scap(elev).

A serial chain on a thorax-fixed base, axes J1..J3 (directions from the spherical construction of band_impl: J1 = b in
the thorax, J3 = an arm-fixed direction w, J2 at arc a1 from J1 and a2 from J3, branch +-1). Axis directions fix every
link's rotation for a given arm orientation; the axis POSITIONS then only translate what the chain carries:

    p(t) = (I - R1(t)) o1 + (R1(t) - R2(t)) o2 + (R2(t) - RA(t)) o3          (linear in the axis points o_i)

p(t) = where the chain puts the arm's GH centre, R1, R2 = link rotations from the reference pose (arm hanging,
plane = elev = axial = 0), RA = the arm's rotation, o_i = a point on axis i at the reference pose. All o_i = 0 is the
spherical chain (p = 0: the GH centre can never move). Misalignment(t) = |p(t) - lift(t)|.
"""
import math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "avg"))
import body_pose as BP
D2R = math.pi / 180
HUMERUS = np.array([0.0, -1.0, 0.0])                                    # canonical humerus long axis (GH -> elbow)


def unit(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)
def Rh_of(pl, el, ax): return BP.rot([0, 1, 0], pl * D2R) @ BP.rot([1, 0, 0], -el * D2R) @ BP.rot([0, 1, 0], ax * D2R)
def bvec(az, el): return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
def w_dir(delta, az): d, a = delta * D2R, az * D2R; return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])
def azel(v): v = v / np.linalg.norm(v); return [math.degrees(math.atan2(v[2], -v[0])) % 360, math.degrees(math.asin(np.clip(v[1], -1, 1)))]
def delaz(v): v = v / np.linalg.norm(v); return [math.degrees(math.acos(np.clip(-v[1], -1, 1))), math.degrees(math.atan2(v[0], v[2]))]
def rot_angle(R): return math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2))))


class Motion:
    """poses (plane, elev, axial, flex, pron) -> GH lift (T,3), scapula rotation (T,3,3), humerus rotation (T,3,3), from the rig"""
    def __init__(self, poses, lift_fn=None):
        import json
        LS = json.load(open(os.path.join(HERE, "..", "avg", "body_mesh.json"))); self.L, self.S = LS["landmarks"], LS["scale"]
        self.P = np.asarray(poses, float)
        self.lift = np.array([BP.segs(self.L, self.S, dict(zip(["plane", "elev", "axial", "flex", "pron"], p)))[1] for p in self.P]) if lift_fn is None else lift_fn(self.P)
        self.RS = np.array([BP.scap(p[1]) for p in self.P]); self.RH = np.array([Rh_of(*p[:3]) for p in self.P])
        self.hdir = self.RH @ HUMERUS


def frame3(a, c): n = c - (a @ c) * a; n = n / np.linalg.norm(n); return np.c_[a, n, np.cross(a, n)]


def cone_int(b, a1, w, a2, sign):
    """unit c at angle a1 from b and a2 from each row of w (T,3); ok where the two cones meet"""
    dd = np.clip(w @ b, -1, 1); n = np.cross(np.broadcast_to(b, w.shape), w); nn = np.linalg.norm(n, axis=1, keepdims=True); n = n / (nn + 1e-12)
    den = 1 - dd ** 2 + 1e-12; ca = (math.cos(a1) - dd * math.cos(a2)) / den; cb = (math.cos(a2) - dd * math.cos(a1)) / den
    p = ca[:, None] * b + cb[:, None] * w; h2 = 1 - (p * p).sum(1)
    return unit(p + sign * np.sqrt(np.clip(h2, 0, None))[:, None] * n), (h2 > 0) & (nn[:, 0] > 1e-6)


class Chain3:
    """3R chain on a thorax-fixed base. prm = dict(b=(az, el), a1, a2 (deg), branch, w=(delta, az) | None -> humerus axis)"""
    def __init__(self, prm):
        self.prm = prm; self.b = bvec(*prm["b"]); self.w = HUMERUS.copy() if prm.get("w") is None else w_dir(*prm["w"])
        self.a1, self.a2, self.sg = prm["a1"] * D2R, prm["a2"] * D2R, (1 if prm.get("branch", 1) >= 0 else -1)
        self.coax = prm.get("w") is None                                  # J3 = humerus axis: an open ring round the upper arm

    def kin(self, M):
        """(A (T,3,9), singular margin deg (T), closes (T), R1, R2, RA) for the motion M"""
        Rref = Rh_of(0, 0, 0); W = M.RH @ self.w; w0 = Rref @ self.w
        c, ok = cone_int(self.b, self.a1, W, self.a2, self.sg); c0, ok0 = cone_int(self.b, self.a1, w0[None], self.a2, self.sg)
        th = np.degrees(np.arccos(np.clip(W @ self.b, -1, 1))); A1, A2 = math.degrees(self.a1), math.degrees(self.a2)
        margin = np.minimum(th - abs(A1 - A2), min(A1 + A2, 360 - A1 - A2) - th)          # deg from J1, J2, J3 coplanar
        if not ok0[0]: return None
        F10, F20 = frame3(self.b, c0[0]), frame3(c0[0], w0)
        R1 = np.einsum("tij,kj->tik", np.stack([frame3(self.b, ci) for ci in c]), F10)
        R2 = np.einsum("tij,kj->tik", np.stack([frame3(ci, wi) for ci, wi in zip(c, W)]), F20)
        RA = M.RH @ Rref.T; I = np.eye(3)[None]
        self.c, self.c0 = c, c0[0]
        return np.concatenate([I - R1, R1 - R2, R2 - RA], axis=2), margin, ok, R1, R2, RA

    def joint_travel(self, M):
        """J1 travel, J2 travel and J3 (ring) travel in deg over the motion"""
        A, mg, ok, R1, R2, RA = self.kin(M)
        def about(R, u, v):                                               # signed rotation angle of R about u (reference frame)
            Rv = R @ v; return np.degrees(np.arctan2(Rv @ np.cross(u, v), Rv @ v))
        def perp(u): v = np.cross(u, [1.0, 0, 0]) if abs(u[0]) < 0.9 else np.cross(u, [0, 1.0, 0]); return v / np.linalg.norm(v)
        q1 = about(R1, self.b, perp(self.b))
        R12 = np.einsum("tji,tjk->tik", R1, R2); q2 = about(R12, self.c0, perp(self.c0))
        R23 = np.einsum("tji,tjk->tik", R2, RA); w0 = Rh_of(0, 0, 0) @ self.w; q3 = about(R23, w0, perp(w0))
        rng = lambda q: dict(min=round(float(q.min()), 1), max=round(float(q.max()), 1), span=round(float(np.ptp(q)), 1))
        return dict(J1=rng(q1), J2=rng(q2), J3=rng(q3))


DIRS = unit(np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1], [1, 1, -1], [1, -1, 1], [-1, 1, 1], [1, 1, 0], [1, -1, 0], [1, 0, 1],
                      [1, 0, -1], [0, 1, 1], [0, 1, -1]], float)); DIRS = np.r_[DIRS, -DIRS]   # 26: polyhedral norm, >= 0.97 x Euclidean


def fit_minimax(A, y, coax=False, bound=60.0):
    """axis points minimising the worst-frame GH residual (26-direction polyhedral norm, exact LP); |o_i| <= bound mm per
    component. Returns (x (9,), residual (T,) Euclidean)."""
    from scipy.optimize import linprog
    A2 = A[:, :, :6] if coax else A; T, _, n = A2.shape
    G = np.einsum("dk,tkn->tdn", DIRS, A2).reshape(-1, n); h = np.einsum("dk,tk->td", DIRS, y).reshape(-1)
    c = np.r_[np.zeros(n), 1.0]; Aub = np.c_[G, -np.ones(len(G))]
    r = linprog(c, A_ub=Aub, b_ub=h, bounds=[(-bound, bound)] * n + [(0, None)], method="highs")
    x = r.x[:n] if r.success else np.zeros(n)
    x = np.r_[x, np.zeros(3)] if coax else x
    return x, np.linalg.norm(np.einsum("tij,j->ti", A, x) - y, axis=1)


def fit_lsq(A, y, coax=False, lam=1e-3):
    A2 = A[:, :, :6] if coax else A; T, _, n = A2.shape; Mx = A2.reshape(3 * T, n)
    x = np.linalg.solve(Mx.T @ Mx + lam * np.eye(n), Mx.T @ y.reshape(-1)); x = np.r_[x, np.zeros(3)] if coax else x
    return x, np.linalg.norm(np.einsum("tij,j->ti", A, x) - y, axis=1)


def residual(A, x, y): return np.linalg.norm(np.einsum("tij,j->ti", A, x) - y, axis=1)


# ------------------------------------------------------------------ a second girdle law: published data
# docs/research/gh_translation_literature.md section "literature law": GH displacement from the arm-hanging posture,
# bone-pin clavicle / scapula angles (Ludewig 2009) through a rigid chain (154 mm clavicle, Xu 2016), mm, thorax frame
# x anterior, y superior, z lateral; quadratics in elevation theta (deg) for planes 0 (abduction), 40 (scaption),
# 90 (flexion), linear in the plane between them, plane clamped to 0..90.
LIT = {0: ((-0.482, 0.00232), (0.456, -0.000385), (-0.285, 0.000453)),
       40: ((0.032, -0.00099), (0.441, -0.0005), (-0.086, -0.00055)),
       90: ((0.082, -0.00153), (0.177, 0.00102), (-0.045, -0.00082))}


def lift_literature(P):
    """(T,3) GH displacement vs the thorax for poses P (plane, elev, ...) from the literature law"""
    P = np.asarray(P, float); pl = np.clip(P[:, 0], 0, 90); th = np.clip(P[:, 1], 0, None); out = np.zeros((len(P), 3))
    ev = lambda p, k: LIT[p][k][0] * th + LIT[p][k][1] * th ** 2
    for k in range(3):
        a = np.where(pl <= 40, ev(0, k) + (ev(40, k) - ev(0, k)) * pl / 40, ev(40, k) + (ev(90, k) - ev(40, k)) * (pl - 40) / 50)
        out[:, k] = a
    return out
