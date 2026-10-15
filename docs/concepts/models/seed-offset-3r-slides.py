"""Concept model: NON-SPHERICAL OFFSET 3R + PASSIVE SELF-ALIGNING CUFF SLIDES (id seed-offset-3r-slides).

Chain: scapula base -> R1 -> link 1 -> R2 -> link 2 -> R3 -> carriage stack -> passive slides -> arm-fixed cuff rail.
The three revolute axes keep the champion's directions (the r20 s1414 #4 spherical 3R) but each axis line is moved
off the GH centre by an offset o_k (perpendicular to the axis, 2 numbers per axis: along / across its link).

SPEC CORRECTION (measured, see the doc): the catalogue's "2 passive slides (along + across the humerus)" cannot close
the loop. The arm moves about GH with 3 rotational DOF; a 3R + 2P chain has 5 DOF, and the loop scapula -> chain ->
humerus -> GH has mobility 5 + 3 - 6 = 2 (Grubler), so with non-concurrent axes the cuff can only be reached on a 2-D
subset of arm orientations (residual > 0.5 mm everywhere else). The minimum passive set is 3. Kept here as the
translations along the humerus, across it, and NORMAL to the carriage (a short radial slide); with translations only,
the chain's orientation is exactly the spherical IK of the axis directions (so q, branches and singularities are the
champion's) and the offsets show up as a pose-dependent drift t3(q) that the three slides absorb: s = Q^T t3. The
spec's 2-slide variant is the special case radial range <= 0.5 mm (= the residual tolerance). 3 ACTIVE DOF (R1-R3
set the arm's orientation; the slides are set by the loop closure, nothing is spare: the loop has mobility 3 + 6 - 6
= 3 = the arm's), 3 PASSIVE DOF.

Parts at real size (mm): O20 x 12.25 hubs (docs/HARDWARE.md v5 joint; lower plate face F, upper member from F + 3.15,
crown F + 12.25), links = 8 mm wide x 3 mm straps with a free-shaped underside (per sample, fitted to clear the skin
by 2 mm over every pose taken, <= 60 deg ramps from the hub levels - the band evaluator's rule), the cuff slide stack
under hub 3: arm-fixed rail 8 wide x 4 high x (20 + 2 S_a) long, along-carriage 20 x (20 + 2 S_t) x 4 carrying the
across rail, across-carriage 20 x 20 x 4 = hub 3's lower plate, riding a radial slide of +-R_r; 0.5 running gaps.
Skin-facing undersides are sampled at ~1 point / 4 mm2 (2 mm grid) and scored; side walls, crowns and carriage edges
are checked for skin contact only. Self-collision: non-adjacent parts >= 1 mm apart (hub cylinders and slide boxes
exact, straps as sampled mid-surfaces with their half-thickness).

A pose is taken iff the spherical IK has a solution on the design's branch >= 10 deg from the J2 fold (the band
evaluator's sing_deg), every slide is within its range, along each fit clip (tracked at the full 10 fps) no joint
jumps > 25 deg between consecutive frames, no two non-adjacent parts come within 1 mm, and the fitted shape clears the
skin (poses whose skin would force the fitted shape up are dropped greedily while that lowers the gap - those poses
are reported as NOT taken, reason "skin").

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/seed-offset-3r-slides.py [check|sweep|best]
"""
import json, math, os, sys, time, datetime
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
BP = CB.BP
ID = "seed-offset-3r-slides"
D2R = math.pi / 180

# ---- hardware (docs/HARDWARE.md v5 joint; catalogue spec) -----------------------------------------------------------
HUB_R, CROWN, UP = 10.0, 12.25, 3.15        # hub radius, F -> crown, F -> upper member underside
T_LINK, W_LINK, RAMP = 3.0, 8.0, 60.0       # strap thickness / width, ramp limit (deg)
RAIL_W, RAIL_H, CAR_L, CAR_W, CAR_H, RUN = 8.0, 4.0, 20.0, 20.0, 4.0, 0.5
CLEAR, PART_CLEAR, SPACING = 2.0, 1.0, 2.0  # skin clearance target, part-part clearance, sample grid (1 pt / 4 mm2)
BIG = 999.0
SING, JUMP = 10.0, 25.0                     # deg: J2 fold margin, largest joint step between 10 fps frames

# the seed: the current champion's axis directions (r20 s1414 #4, pipeline/conformal/band_cad/inputs/r20_n3_s1414_4_f300.json)
SEED = dict(az=2.4305071427308924, el=80.67633718429899, a=[76.90180446920043, 66.74921235407174],
            w=[86.32769021001913, 21.829657347343378], branch=-1)

PARAMS = dict(o1a=0.0, o1c=0.0, o2a=0.0, o2c=0.0, o3a=0.0, o3c=0.0,   # axis offsets (mm): along / across the link
              S_a=15.0, S_t=15.0, R_r=0.5,                            # slide half-ranges (mm); R_r 0.5 = the spec's 2 slides
              drop=1,                                                 # greedy pose dropping on the skin envelope (0/1)
              slides=1)                                               # 0: spherical reference (offsets ignored, arm-fixed hub 3)
SWEEP = dict(o1a=[-20, -10, 0, 10, 20], o1c=[-20, -10, 0, 10, 20], o2a=[-20, -10, 0, 10, 20], o2c=[-20, -10, 0, 10, 20],
             o3a=[-20, -10, 0, 10, 20], o3c=[-20, -10, 0, 10, 20], S_a=[10, 15, 25], S_t=[10, 15, 25], R_r=[0.5, 2, 5, 10])


# ---- small geometry ----------------------------------------------------------------------------------------------
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def rotm(u, a):
    """Rodrigues; u (3,), a (n,) -> (n, 3, 3)"""
    a = np.atleast_1d(np.asarray(a, float)); u = unit(u)
    K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    return np.eye(3)[None] + np.sin(a)[:, None, None] * K[None] + (1 - np.cos(a))[:, None, None] * (K @ K)[None]


def bvec(az, el): return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
def w_dir(d, az): return np.array([math.sin(d * D2R) * math.sin(az * D2R), -math.cos(d * D2R), math.sin(d * D2R) * math.cos(az * D2R)])


def circ_int(c1, r1, c2, r2, sign):
    dd = float(np.clip(c1 @ c2, -1, 1)); n = unit(np.cross(c1, c2)); den = 1 - dd ** 2 + 1e-12
    a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a * c1 + b * c2; return p + sign * math.sqrt(max(0.0, 1 - p @ p)) * n


def sub1(u, p, q):
    """angle th with rot(u, th) p = q (Paden-Kahan 1), batched p, q (n, 3)"""
    pp = p - (p @ u)[:, None] * u; qq = q - (q @ u)[:, None] * u
    return np.arctan2(np.einsum("ij,ij->i", np.cross(pp, qq), np.broadcast_to(u, pp.shape)), np.einsum("ij,ij->i", pp, qq))


def scap(el):
    n = np.array([math.cos(30 * D2R), 0, -math.sin(30 * D2R)])
    return rotm([0, 0, 1], 0.12 * el * D2R)[0] @ rotm(n, -0.36 * max(0, el - 20) * D2R)[0]


def humerus(p):
    return rotm([0, 1, 0], p[0] * D2R)[0] @ rotm([1, 0, 0], -p[1] * D2R)[0] @ rotm([0, 1, 0], p[2] * D2R)[0]


def pose_rots(POSE):
    """scapula Rs and relative arm rotation Q = Rs^T Rh (the band payload's HG) per pose row (plane, elev, axial, ...)"""
    RS = np.array([scap(float(p[1])) for p in POSE]); RH = np.array([humerus(p) for p in POSE])
    return RS, np.einsum("nji,njk->nik", RS, RH)


# ---- the design ----------------------------------------------------------------------------------------------------
class Design:
    def __init__(self, params=None):
        P = dict(PARAMS); P.update(params or {}); self.p = P
        s = SEED; self.branch = s["branch"]
        u1 = bvec(s["az"], s["el"]); u3 = w_dir(*s["w"]); A = [x * D2R for x in s["a"]]
        u2 = circ_int(u1, A[0], u3, A[1], self.branch)
        self.u = [unit(u1), unit(u2), unit(u3)]; self.A = A
        self.h0 = np.array([0.0, -1.0, 0.0])                      # humerus axis at rest (GH -> elbow)
        # offset basis per axis: 'a' = toward the neighbouring axis along the link, 'c' = across it
        nb = [self.u[1], self.u[2], self.u[1]]
        self.ea = [unit(nb[k] - (nb[k] @ self.u[k]) * self.u[k]) for k in range(3)]
        self.ec = [np.cross(self.u[k], self.ea[k]) for k in range(3)]
        self.c = [P[f"o{k + 1}a"] * self.ea[k] + P[f"o{k + 1}c"] * self.ec[k] for k in range(3)]
        if not P.get("slides", 1): self.c = [np.zeros(3)] * 3
        # the cuff slide frame (rest): normal = hub 3 axis, along = humerus axis projected, across = normal x along
        self.sn = self.u[2]; self.sa = unit(self.h0 - (self.h0 @ self.sn) * self.sn); self.st = np.cross(self.sn, self.sa)

    # -- kinematics: spherical IK of the axis directions + offset drift absorbed by the slides --
    def ik(self, Q):
        """Q (n,3,3) -> q (n,3) rad, ok_fold (n,), member transforms X1, X2, X3 as (R, t) arrays, slides s (n,3) [a, t, n]"""
        u1, u2, u3 = self.u; n = len(Q)
        w = Q @ u3; c12 = u1 @ u2
        M = np.array([[1, c12], [c12, 1]]); ab = np.linalg.solve(M, np.stack([w @ u1, np.full(n, u2 @ u3)]))
        al, be = ab; cr = np.cross(u1, u2); g2 = (1 - al ** 2 - be ** 2 - 2 * al * be * c12) / (cr @ cr)
        th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
        a1, a2 = np.degrees(self.A[0]), np.degrees(self.A[1])
        ok = (th >= abs(a1 - a2) + SING) & (th <= min(a1 + a2, 360 - a1 - a2) - SING) & (g2 > 0)
        best = None
        for sg in (1.0, -1.0):
            z = al[:, None] * u1 + be[:, None] * u2 + sg * np.sqrt(np.clip(g2, 0, None))[:, None] * cr
            q1 = sub1(u1, z, w); q2 = sub1(u2, np.broadcast_to(u3, z.shape), z)
            R1 = rotm(u1, q1) if n else np.zeros((0, 3, 3))
            p2 = R1 @ u2; br = np.sign(np.einsum("ij,ij->i", p2, np.cross(np.broadcast_to(u1, w.shape), w)))
            if best is None: best = [q1.copy(), q2.copy(), br]
            else:
                pick = br == self.branch; best[0][pick] = q1[pick]; best[1][pick] = q2[pick]
        q1, q2 = best[0], best[1]
        R1 = np.stack([rotm(u1, x)[0] for x in q1]) if n else np.zeros((0, 3, 3))
        R2 = np.stack([rotm(u2, x)[0] for x in q2]) if n else np.zeros((0, 3, 3))
        R12 = R1 @ R2; v = unit(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = sub1(u3, np.broadcast_to(v, (n, 3)), np.einsum("nji,njk,k->ni", R12, Q, v))
        R3 = np.stack([rotm(u3, x)[0] for x in q3]) if n else np.zeros((0, 3, 3))
        c1, c2, c3 = self.c
        t1 = c1 - R1 @ c1; X1 = (R1, t1)
        # explicit: X2 p = R1 (R2 (p - c2) + c2 - c1) + c1 = R12 p + [R1 (c2 - R2 c2 - c1) + c1]
        t2 = np.einsum("nij,nj->ni", R1, c2[None] - R2 @ c2 - c1[None]) + c1; X2 = (R12, t2)
        R123 = R12 @ R3
        t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3) + t2; X3 = (R123, t3)
        sv = np.einsum("nji,nj->ni", Q, t3)                       # carriage displacement on the arm (rest arm frame)
        s = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        return np.stack([q1, q2, q3], 1), ok, X1, X2, X3, s

    def slides_ok(self, s):
        P = self.p
        if not P.get("slides", 1): return np.ones(len(s), bool)
        return (np.abs(s[:, 0]) <= P["S_a"]) & (np.abs(s[:, 1]) <= P["S_t"]) & (np.abs(s[:, 2]) <= P["R_r"])


# ---- parts (member-local rest coordinates) ---------------------------------------------------------------------------
def disc(r, sp=SPACING):
    g = np.arange(-r + sp / 2, r, sp); X, Y = np.meshgrid(g, g); m = X ** 2 + Y ** 2 <= r * r
    return np.stack([X[m], Y[m]], 1)


def rect(L, W, sp=SPACING):
    a = np.arange(-L / 2 + sp / 2, L / 2, sp); b = np.arange(-W / 2 + sp / 2, W / 2, sp); X, Y = np.meshgrid(a, b)
    return np.stack([X.ravel(), Y.ravel()], 1)


def frame_of(n):
    e = unit(np.cross(n, [0.0, 0.0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0.0, 0.0])); return e, np.cross(n, e)


class Geometry:
    """samples: list of groups. A group = (member, base points B (m,3), directions N (m,3), shared height?, offsets).
    point_j(h) = B_j + (h + off_j) N_j in the member's rest frame; member 0 base (scapula), 1 link 1, 2 link 2,
    3 carriage B / hub 3 (X3), 4 carriage A (arm + s_a), 5 cuff rail (arm)."""
    def __init__(self, D):
        self.D = D; u = D.u; c = D.c; P = D.p
        self.groups = []
        # hubs 1, 2: disc underside at F_k = c_k + f_k u_k (f fitted, shared per disc)
        for k, mem in ((0, 0), (1, 1)):
            e, f = frame_of(u[k]); d = disc(HUB_R)
            B = c[k][None] + d[:, :1] * e + d[:, 1:] * f
            self.groups.append(dict(name=f"hub{k + 1}", mem=mem, B=B, N=np.broadcast_to(u[k], B.shape).copy(), shared=True,
                                    off=np.zeros(len(B)), axis=k))
        if not P.get("slides", 1):                                  # spherical reference: the champion's arm-fixed hub-3 block
            e, f = frame_of(u[2]); d = disc(HUB_R); B = c[2][None] + d[:, :1] * e + d[:, 1:] * f
            self.groups.append(dict(name="hub3", mem=5, B=B, N=np.broadcast_to(u[2], B.shape).copy(), shared="stack", off=np.zeros(len(B))))
            nk = rect(25.0, W_LINK); nk[:, 0] += HUB_R + 12.5          # + the neck to the cuff: 8 x 25 mm strap down the arm
            Bn = c[2][None] + nk[:, :1] * D.sa + nk[:, 1:] * D.st     # (concept_baseline.py's neck; the slide model's rail)
            self.groups.append(dict(name="neck", mem=5, B=Bn, N=np.broadcast_to(u[2], Bn.shape).copy(), shared="stack", off=np.zeros(len(Bn))))
            self.links = []; return
        # cuff stack along hub 3's axis: rail underside at t_r (fitted), carriage A underside at t_r + RAIL_H + RUN
        sa, st, sn = D.sa, D.st, D.sn; Sa, St = P["S_a"], P["S_t"]
        r = rect(CAR_L + 2 * Sa, RAIL_W); Br = c[2][None] + r[:, :1] * sa + r[:, 1:] * st
        ca = rect(CAR_L, CAR_W + 2 * St); ca = ca[np.abs(ca[:, 1]) > RAIL_W / 2]
        Bc = c[2][None] + ca[:, :1] * sa + ca[:, 1:] * st
        self.groups.append(dict(name="rail", mem=5, B=Br, N=np.broadcast_to(sn, Br.shape).copy(), shared="stack", off=np.zeros(len(Br))))
        self.groups.append(dict(name="carA", mem=4, B=Bc, N=np.broadcast_to(sn, Bc.shape).copy(), shared="stack",
                                off=np.full(len(Bc), RAIL_H + RUN)))
        self.links = []

    def add_links(self, f1, f2, f3):
        """link straps between the hub centres (needs the hub face heights for the rest-pose directions)"""
        D = self.D; u, c = D.u, D.c
        C = [c[0] + f1 * u[0], c[1] + f2 * u[1], c[2] + f3 * u[2]]
        out = []
        for li, (ka, kb, mem) in enumerate(((0, 1, 1), (1, 2, 2))):
            da, db = unit(C[ka]), unit(C[kb]); R = 0.5 * (np.linalg.norm(C[ka]) + np.linalg.norm(C[kb]))
            ang = math.acos(float(np.clip(da @ db, -1, 1))); bn = unit(np.cross(da, db))
            n = max(4, int(R * ang / SPACING)); ts = (np.arange(n) + 0.5) / n
            dirs = np.array([unit(math.sin((1 - t) * ang) * da + math.sin(t * ang) * db) for t in ts])
            rows = []
            for v in (-3.0, -1.0, 1.0, 3.0):
                dv = unit(dirs + (v / R) * bn)
                # keep samples outside both hub footprints (distance from the axis lines at radius R)
                pts = R * dv
                def off_axis(k): w = pts - c[k]; return np.linalg.norm(w - (w @ u[k])[:, None] * u[k], axis=1)
                keep = (off_axis(ka) > HUB_R) & (off_axis(kb) > HUB_R)
                rows.append((dv, keep, ts * R * ang))
            out.append(dict(name=f"L{li + 1}", mem=mem, ka=ka, kb=kb, rows=rows))
        self.links = out
        return out


# ---- the model: fit on a bench, then metal per pose -------------------------------------------------------------------
class Model:
    def __init__(self, B, params=None, verbose=False):
        self.B = B; self.D = Design(params); self.p = self.D.p; self.v = verbose
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)   # = concept_baseline.py's rotations
        q, ok, X1, X2, X3, s = self.D.ik(self.Q)
        self.q, self.X = q, {1: X1, 2: X2, 3: X3}; self.s = s
        self.why = np.array([""] * len(B.idx), dtype=object)
        okf = ok.copy(); self.why[~ok] = "fold"
        sok = self.D.slides_ok(s); self.why[ok & ~sok] = "slide"; okf &= sok
        cont = self.continuity()
        bad_c = okf & ~cont; self.why[bad_c] = "flip"; okf &= cont
        self.kin_ok = okf

    def continuity(self):
        """track every fit clip at its full 10 fps: a bench clip frame fails if its joint step from the previous
        full-rate frame exceeds JUMP (with the previous frame taken) - the GPU evaluator's continuity, spherical IK"""
        Z = self.Z; names = list(Z["NAMES"]); cid = Z["CID"]; ok_at = {}
        for nm in CB.FIT:
            ii = np.nonzero(cid == names.index(nm))[0]
            ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
            q, ok, _, _, _, s = self.D.ik(Z["HG"][ii].astype(float)); ok &= self.D.slides_ok(s)
            prev = None
            for j, gi in enumerate(ii):
                good = bool(ok[j])
                if good and prev is not None:
                    dq = np.degrees(np.abs((q[j] - q[prev] + np.pi) % (2 * np.pi) - np.pi))
                    if dq.max() > JUMP: good = False
                ok_at[int(gi)] = good
                prev = j if ok[j] else None
        return np.array([ok_at.get(int(gi), True) for gi in self.B.idx])

    # member transform (scapula frame) of member m at bench pose i
    def T(self, m, i):
        if m == 0: return np.eye(3), np.zeros(3)
        if m in (1, 2, 3): R, t = self.X[m]; return R[i], t[i]
        Q = self.Q[i]
        if m == 5: return Q, np.zeros(3)
        if m == 4: return Q, Q @ (self.s[i, 0] * self.D.sa)
        raise ValueError(m)

    def world(self, m, i, P):
        return self.scap_pts(m, i, P) @ self.RS[i].T

    # -- per-pose needed heights h_ij (sample j of a group, pose i) by sphere tracing along the sample direction --
    def needed(self, items, poses, iters=16, lift_max=35.0):
        """items: list of (member, base points Bp (m,3), directions N (m,3), start height, avoid boxes). Returns, per
        item, h (len(poses), m): the height along N (from Bp) at which the sample sits CLEAR mm off the skin in that
        pose and PART_CLEAR off the listed slide-stack boxes. Sphere tracing inward from outside (both distances are
        1-Lipschitz, so a step of (distance - target) never crosses the level), started lift_max above the sample's
        rest-pose height; a sample already inside the body there (the part would have to rise > lift_max, e.g. a ray
        through the torso or head) gets BIG: that pose cannot shape the part (it is dropped -> recorded as contact)."""
        sizes = [len(it[1]) for it in items]; cut = np.cumsum([0] + sizes)
        boxes_of = [it[4] if len(it) > 4 else () for it in items]
        def trace(i, h, active):
            for it_ in range(iters):
                Ps = [self.scap_pts(m, i, Bp + h[cut[k]:cut[k + 1], None] * N) for k, (m, Bp, N, *_) in enumerate(items)]
                d = self.B.dist(i, np.concatenate(Ps) @ self.RS[i].T) - CLEAR
                if it_ == 0 and active is not None: inside0 = d < -CLEAR                       # inside the body at the start
                step = np.where(active if active is not None else True, d - 0.05, 0.0); h = h - step
                if np.abs(step).max() < 0.05: break
            if any(boxes_of):                                       # slide-stack boxes: stay above them (exact ray / box slabs)
                bx = self._boxes_at(i)
                for k, names in enumerate(boxes_of):
                    m, Bp, N = items[k][:3]; R_, t_ = self.T(m, i); o = Bp @ R_.T + t_; n = N @ R_.T
                    for nm in names:
                        cen, R, half = bx[nm]; hh = half + PART_CLEAR + 0.6
                        ol = (o - cen) @ R; nl = n @ R; nl = np.where(np.abs(nl) < 1e-9, 1e-9, nl)
                        t1 = (-hh - ol) / nl; t2 = (hh - ol) / nl
                        tn = np.minimum(t1, t2).max(1); tf = np.maximum(t1, t2).min(1)
                        hit = tn <= tf
                        h[cut[k]:cut[k + 1]] = np.where(hit, np.maximum(h[cut[k]:cut[k + 1]], tf), h[cut[k]:cut[k + 1]])
            return h, (inside0 if active is not None else None)
        rest = min(poses, key=lambda i: self.B.poses[i]["elev"])
        h_rest, _ = trace(rest, np.concatenate([np.full(n, it[3]) for it, n in zip(items, sizes)]), None)
        H = np.empty((len(poses), cut[-1]))
        for a, i in enumerate(poses):
            h, ins = trace(i, h_rest + lift_max, np.ones(cut[-1], bool))
            H[a] = np.where(ins, BIG, h)
        return [H[:, cut[k]:cut[k + 1]] for k in range(len(items))]

    def scap_pts(self, m, i, P):
        R, t = self.T(m, i); return np.asarray(P) @ R.T + t

    def _boxes_at(self, i):
        """slide-stack boxes (centre, rotation, half sizes) in the scapula frame at pose i, from the current rail height"""
        D = self.D; P = D.p; tr = self._tr_fit; c = D.c; sa, st, sn = D.sa, D.st, D.sn; Rst = np.stack([sa, st, sn], 1)
        f3 = tr + RAIL_H + RUN + CAR_H + RUN + P["R_r"]
        spec = {"rail": (5, c[2] + (tr + RAIL_H / 2) * sn, np.array([(CAR_L + 2 * P["S_a"]) / 2, RAIL_W / 2, RAIL_H / 2])),
                "carA": (4, c[2] + (tr + RAIL_H + RUN + CAR_H / 2) * sn, np.array([CAR_L / 2, (CAR_W + 2 * P["S_t"]) / 2, CAR_H / 2])),
                "carB": (3, c[2] + (f3 + CAR_H / 2) * sn, np.array([CAR_L / 2, CAR_W / 2, CAR_H / 2]))}
        out = {}
        for nm, (m, cen, half) in spec.items():
            R, t = self.T(m, i); out[nm] = (R @ cen + t, R @ Rst, half)
        return out

    def fit(self):
        D = self.D
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        geo = Geometry(D); self.geo = geo
        # first pass: hubs + cuff stack (the link paths need the hub heights)
        items = [(g["mem"], g["B"], g["N"], 140.0) for g in geo.groups]
        res = self.needed(items, poses)
        H = {g["name"]: r - g["off"][None] for g, r in zip(geo.groups, res)}
        H["stack"] = np.concatenate([H[g["name"]] for g in geo.groups if g["shared"] == "stack"], 1)
        self.Hneed, self.Lneed = H, {}
        self.greedy_drop(links=False); keep1 = ~self.drop           # hub / stack heights without the outlier poses
        f1 = H["hub1"][keep1].max(); f2 = H["hub2"][keep1].max(); tr = H["stack"][keep1].max()
        f3 = self.f3_of(tr)                                         # hub 3 face
        geo.add_links(f1, f2, f3); self._tr_fit = tr
        items = []; idx = []
        for lk in geo.links:                                        # link 2 rides over the slide stack round hub 3
            avoid = ("rail", "carA") if lk["name"] == "L2" and D.p.get("slides", 1) else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        res = self.needed(items, poses)
        L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        self.Lneed = L
        self.greedy_drop(keep0=keep1)                               # only drops more: the stack never rises above _tr_fit
        self.finalize()

    def f3_of(self, tr):
        """hub 3 face: across-carriage underside at mid radial travel (slides), or the fitted arm-fixed disc (reference)"""
        return tr + RAIL_H + RUN + CAR_H + RUN + self.D.p["R_r"] if self.D.p.get("slides", 1) else tr

    def _heights(self, keep):
        H, L = self.Hneed, self.Lneed
        f1 = H["hub1"][keep].max(); f2 = H["hub2"][keep].max(); tr = H["stack"][keep].max()
        rL = {k: [r[keep].max(0) for r in rows] for k, rows in L.items()}
        return f1, f2, tr, rL

    def greedy_drop(self, keep0=None, links=True):
        """lower the shape below poses that force it up (-> those poses are recorded with metal inside the body =
        CONTACT and not taken, tools/concept_baseline.py's convention for its percentile profiles) while that lowers
        the approximate gap. Starts without the BIG poses; a move drops the k (1..8) poses that push one part highest.
        In-band proxy: a sample counts in band in pose i if it is <= 12 mm above its own 2 mm level there."""
        poses = self.poses_fit; kind = np.array([self.B.kind[i] for i in poses])
        ncl = sum(1 for k in self.B.kind if k == "clip"); nws = len(self.B.kind) - ncl
        H, L = self.Hneed, self.Lneed
        groups = [("g", H["hub1"]), ("g", H["hub2"]), ("g", H["stack"])] + ([("s", r) for rows in L.values() for r in rows] if links else [])
        keep = np.ones(len(poses), bool) if keep0 is None else keep0.copy()
        for typ, M in groups: keep &= ~(M >= BIG / 2).any(1)
        def score(keep):
            if not keep.any(): return 1e9, 0, 0, 0
            cl = keep & (kind == "clip"); inb = tot = 0
            for typ, M in groups:
                top = M[keep].max() if typ == "g" else M[keep].max(0)
                ex = top - M[cl]
                inb += float((ex <= 12.0).sum()); tot += ex.size
            ib = inb / max(tot, 1); fol = cl.sum() / ncl; rch = (keep & (kind == "ws")).sum() / nws
            con = (~keep).sum() / len(keep)                      # a dropped pose is recorded with its metal inside the body
            return 100 * (max(0, .9 - ib) + max(0, .95 - fol) + max(0, .9 - rch)) + 100 * con, ib, fol, rch
        cur = score(keep)[0]
        for it in range(60 if self.p.get("drop", 1) else 0):
            best, bk = cur, None
            for typ, M in groups:
                need = np.where(keep, M.max(1), -1e9)            # per pose: the highest requirement it sets on this part
                order = np.argsort(-need)
                for k in range(1, 9):
                    sel = order[:k]; sel = sel[keep[sel]]
                    if not len(sel): continue
                    k2 = keep.copy(); k2[sel] = False; sc = score(k2)[0]
                    if sc < best - 1e-6: best, bk = sc, k2
            if bk is None: break
            keep = bk; cur = best
        if not self.p.get("drop", 1):                            # no greedy: only the BIG poses are left out
            keep = np.ones(len(poses), bool) if keep0 is None else keep0.copy()
            for typ, M in groups: keep &= ~(M >= BIG / 2).any(1)
        self.drop = ~keep
        if self.v: print(f"  greedy drop: {int((~keep).sum())} poses, approx gap {cur:.1f}", flush=True)

    def finalize(self):
        poses = self.poses_fit; keep = ~self.drop
        f1, f2, tr, rL = self._heights(keep)
        D = self.D; geo = self.geo
        f3 = self.f3_of(tr)                                          # (the link paths keep the first pass's hub centres)
        self.f = [f1, f2, f3]; self.tr = tr
        # link shapes: lower bound from the envelope, raised to meet the hub levels with <= RAMP slopes
        u, c = D.u, D.c; k = math.tan(RAMP * D2R)
        lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): UP, ("L2", 2): UP}    # link 1 lower at J1, J2; link 2 upper at J2, J3
        F = [f1, f2, f3]; self.link_pts = {}
        for lk in geo.links:
            pts_all = []
            for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
                r = r.copy(); S = sarc
                # connection radius at the two hub rims (sample ray meets the hub face plane + level)
                for kk, end in ((lk["ka"], 0), (lk["kb"], -1)):
                    idx = np.nonzero(keep_s)[0]
                    if not len(idx): continue
                    j = idx[0] if end == 0 else idx[-1]
                    cen = c[kk] + F[kk] * u[kk]; den = float(dv[j] @ u[kk])
                    rc = (cen @ u[kk] + lvl[(lk["name"], kk)]) / max(den, 0.2)
                    r = np.maximum(r, rc - k * np.abs(S - S[j]))
                # slope limit: lift lower points under the steepest-descent cone of every sample
                r = np.max(r[None, :] - k * np.abs(S[:, None] - S[None, :]), axis=1)
                pts_all.append((dv[keep_s] * r[keep_s][:, None]))
            self.link_pts[lk["name"]] = (lk["mem"], np.concatenate(pts_all) if pts_all else np.zeros((0, 3)))
        # rigid samples
        self.rigid = {}
        for g in geo.groups:
            h = {"hub1": f1, "hub2": f2}.get(g["name"], tr)            # rail / carriage A / reference hub 3: the stack height
            self.rigid[g["name"]] = (g["mem"], g["B"] + (h + g["off"])[:, None] * g["N"])
        self._contact_only(); self._solids()

    def _contact_only(self):
        """side walls / crowns of hubs, carriage and rail edges (checked for skin contact, not scored)"""
        D = self.D; u, c = D.u, D.c; F = self.f; out = []
        ang = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        sl = D.p.get("slides", 1)
        for k, mem in ((0, 0), (1, 1), (2, 3 if sl else 5)):
            e, f = frame_of(u[k]); ring = HUB_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
            z0 = F[k] + (CAR_H if k == 2 and sl else 0.0)
            for z in np.linspace(z0, F[k] + CROWN, 4):
                out.append((mem, c[k] + z * u[k] + ring))
        sa, st, sn = D.sa, D.st, D.sn; P = D.p; tr = self.tr
        def box_edges(mem, L, W, z0, z1):
            pts = []
            for z in (z0, z1):
                for x in np.arange(-L / 2, L / 2 + 1e-6, SPACING): pts += [(x, -W / 2, z), (x, W / 2, z)]
                for y in np.arange(-W / 2, W / 2 + 1e-6, SPACING): pts += [(-L / 2, y, z), (L / 2, y, z)]
            a = np.array(pts); return (mem, c[2] + a[:, :1] * sa + a[:, 1:2] * st + a[:, 2:] * sn)
        if not sl: self.contact = out; return
        out.append(box_edges(5, CAR_L + 2 * P["S_a"], RAIL_W, tr, tr + RAIL_H))
        out.append(box_edges(4, CAR_L, CAR_W + 2 * P["S_t"], tr + RAIL_H + RUN, tr + RAIL_H + RUN + CAR_H))
        zb = F[2]                                                   # across carriage = hub 3 lower plate, F3 .. F3 + CAR_H
        out.append(box_edges(3, CAR_L, CAR_W, zb, zb + CAR_H))
        self.contact = out

    def _solids(self):
        """primitives for part-part clearance: cylinders (hubs), boxes (slide stack), strap mid-surfaces"""
        D = self.D; u, c = D.u, D.c; F = self.f; P = D.p; tr = self.tr; sa, st, sn = D.sa, D.st, D.sn
        sl = P.get("slides", 1)
        self.cyl = {"hub1": (0, c[0] + F[0] * u[0], u[0]), "hub2": (1, c[1] + F[1] * u[1], u[1]), "hub3": (3 if sl else 5, c[2] + F[2] * u[2], u[2])}
        self.box = {} if not sl else {"rail": (5, c[2] + (tr + RAIL_H / 2) * sn, np.array([(CAR_L + 2 * P["S_a"]) / 2, RAIL_W / 2, RAIL_H / 2])),
                    "carA": (4, c[2] + (tr + RAIL_H + RUN + CAR_H / 2) * sn, np.array([CAR_L / 2, (CAR_W + 2 * P["S_t"]) / 2, CAR_H / 2])),
                    "carB": (3, c[2] + (F[2] + CAR_H / 2) * sn, np.array([CAR_L / 2, CAR_W / 2, CAR_H / 2]))}
        self.strap = {}
        for nm, (mem, pts) in self.link_pts.items():
            dv = unit(pts); self.strap[nm] = (mem, pts + (T_LINK / 2) * dv)
        # surface samples of hubs (for hub-vs-anything checks)
        ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); self.cyl_surf = {}
        for nm, (mem, cen, ax) in self.cyl.items():
            e, f = frame_of(ax); pts = []
            for z in np.linspace(0, CROWN, 5):
                pts.append(cen + z * ax + HUB_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f))
            dd = disc(HUB_R, 4.0); pts.append(cen + CROWN * ax + dd[:, :1] * e + dd[:, 1:] * f)
            self.cyl_surf[nm] = (mem, np.concatenate(pts))

    def sd_cyl(self, Pw, cen, ax):
        w = Pw - cen; z = w @ ax; rr = np.linalg.norm(w - z[:, None] * ax, axis=1)
        dr = rr - HUB_R; dz = np.maximum(-z, z - CROWN)
        return np.where((dr > 0) | (dz > 0), np.hypot(np.maximum(dr, 0), np.maximum(dz, 0)), np.maximum(dr, dz))

    def sd_box(self, Pw, cen, R, half):
        w = (Pw - cen) @ R; q = np.abs(w) - half
        return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(1), 0)

    def collide(self, i):
        """min clearance (mm) between non-adjacent parts at pose i (scapula frame, rigid motion is enough)"""
        D = self.D
        def tf(m, P): R, t = self.T(m, i); return P @ R.T + t
        def frameR(m): R, _ = self.T(m, i); return R
        cyl = {k: (m, tf(m, cen[None])[0], frameR(m) @ ax) for k, (m, cen, ax) in self.cyl.items()}
        Rst = np.stack([D.sa, D.st, D.sn], 1)
        box = {k: (m, tf(m, cen[None])[0], frameR(m) @ Rst, half) for k, (m, cen, half) in self.box.items()}
        surf = {k: tf(m, P) for k, (m, P) in self.cyl_surf.items()}
        strap = {k: tf(m, P) for k, (m, P) in self.strap.items()}
        mins = []; names = []
        def vs_cyl(P, name, extra=0.0): m, cen, ax = cyl[name]; return float(self.sd_cyl(P, cen, ax).min()) - extra if len(P) else 1e9
        def vs_box(P, name, extra=0.0): m, cen, R, half = box[name]; return float(self.sd_box(P, cen, R, half).min()) - extra if len(P) else 1e9
        h = T_LINK / 2
        mins.append(vs_cyl(strap["L2"], "hub1", h)); names.append("L2-hub1")
        for b in (("rail", "carA", "carB") if box else ()):
            mins.append(vs_box(surf["hub1"], b)); mins.append(vs_box(strap["L1"], b, h)); mins.append(vs_box(surf["hub2"], b))
            names += [f"hub1-{b}", f"L1-{b}", f"hub2-{b}"]
        if box: mins.append(vs_box(strap["L2"], "rail", h)); mins.append(vs_box(strap["L2"], "carA", h))
        else: mins += [1e9, 1e9]
        mins.append(vs_cyl(surf["hub3"], "hub1")); mins.append(vs_cyl(strap["L1"], "hub3", h))
        names += ["L2-rail", "L2-carA", "hub3-hub1", "L1-hub3"]
        # link 1 vs link 2 away from joint 2
        P1, P2 = strap["L1"], strap["L2"]
        m, cen2, ax2 = cyl["hub2"]
        def far(P): w = P - cen2; return np.linalg.norm(w - (w @ ax2)[:, None] * ax2, axis=1) > HUB_R + 4
        A, Bq = P1[far(P1)], P2[far(P2)]
        if len(A) and len(Bq):
            d, _ = cKDTree(Bq).query(A); mins.append(float(d.min()) - 2 * h); names.append("L1-L2")
        self.last_clear = dict(zip(names, [round(x, 1) for x in mins]))
        return min(mins)

    def run(self, B=None):
        """fit, then record every bench pose; returns the bench report + reasons"""
        B = self.B; B.reset(); t0 = time.time()
        self.fit()
        valid = set(self.poses_fit.tolist()); dropped = set(self.poses_fit[self.drop].tolist())
        self.clear = np.full(len(B.idx), np.nan); self.last_pair = {}
        for i in range(len(B.idx)):                                 # every kinematically valid pose: part check, then the skin
            if i not in valid: B.record(i, None); continue
            cl = self.collide(i); self.clear[i] = cl; self.last_pair[i] = min(self.last_clear, key=self.last_clear.get)
            if cl < PART_CLEAR: self.why[i] = "parts"; B.record(i, None); continue
            d = B.record(i, self.metal_points(i))
            dc = min(float(B.dist(i, self.world(m, i, Pc)).min()) for m, Pc in self.contact)
            if dc < 0: B.res[i] = np.r_[d, dc]                     # side wall / edge inside the body: record as contact
            if min(dc, float(d.min())) < 0: self.why[i] = "skin" if i in dropped else "contact"
        r = B.report(); r["why"] = {k: int((self.why == k).sum()) for k in ("fold", "slide", "flip", "skin", "parts", "contact")}
        r["parts_ib14"] = self.part_inband()
        pc = [self.last_pair.get(i) for i in range(len(B.idx)) if self.why[i] == "parts"]
        r["parts_pairs"] = {k: pc.count(k) for k in set(pc)}
        r["s_abs_max"] = [round(float(np.abs(self.s[self.kin_ok][:, k]).max()), 1) if self.kin_ok.any() else None for k in range(3)]
        r["f"] = [round(x, 1) for x in self.f]; r["t"] = round(time.time() - t0, 1)
        return r

    def part_inband(self):
        """in-band 2-14 mm share per part over the clip frames taken (same samples as the bench's in-band)"""
        names = list(self.rigid) + list(self.link_pts); sizes = [len(X) for _, X in self.rigid.values()] + [len(X) for _, X in self.link_pts.values()]
        cut = np.cumsum([0] + sizes); acc = {n: [] for n in names}
        for i in range(len(self.B.idx)):
            d = self.B.res[i]
            if self.B.kind[i] != "clip" or d is None or float(np.min(d)) < 0: continue
            for k, n in enumerate(names): acc[n].append(d[cut[k]:cut[k + 1]])
        out = {}
        for n in names:
            if acc[n]: dd = np.concatenate(acc[n]); out[n] = [round(float(((dd >= 2) & (dd <= 14)).mean()), 3), round(float(np.median(dd)), 1), int(sizes[names.index(n)])]
        return out

    def metal_points(self, i):
        P = [self.world(m, i, X) for m, X in self.rigid.values()] + [self.world(m, i, X) for m, X in self.link_pts.values()]
        return np.concatenate(P)


_MODELS = {}
def metal(pose, frames, params, B=None, i=None):
    """bench API: metal sample points of the fitted design at bench pose i (or None if not taken).
    The design is fitted once per params on the bench (shape fit = the band evaluator's free underside)."""
    key = json.dumps(params, sort_keys=True)
    if key not in _MODELS:
        B = B or CB.Bench(n_clip=60, n_ws=160); M = Model(B, params); M.run(); _MODELS[key] = M
    M = _MODELS[key]
    if i is None:
        i = next(j for j, p in enumerate(M.B.poses) if p == pose)
    return None if M.B.res[i] is None else M.metal_points(i)


# ---- sweep driver -------------------------------------------------------------------------------------------------
def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def evaluate(B, params, log=None):
    M = Model(B, params); r = M.run(); r["params"] = dict(M.p)
    if log is not None:
        log.append(dict(k=len(log), t=now(), params=dict(M.p), inband14=r["inband14"], inband10=r["inband10"], reach=r["reach"],
                        follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], s_abs_max=r["s_abs_max"]))
    return r, M


def kin_scan(B, params):
    """kinematics only (no skin): share of clip / workspace poses the chain closes on within the slide ranges"""
    kind = np.array(B.kind); HG = CB._poses_all()["HG"][B.idx].astype(float)
    D = Design(params); q, ok, X1, X2, X3, s = D.ik(HG); sok = D.slides_ok(s)
    return dict(clip=round(float((ok & sok)[kind == "clip"].mean()), 3), ws=round(float((ok & sok)[kind == "ws"].mean()), 3),
                s_max=np.round(np.abs(s[ok]).max(0), 1).tolist(), s_p95=np.round(np.percentile(np.abs(s[ok]), 95, axis=0), 1).tolist())


SWEEP_FILE = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")


def sweep(B, budget=110, seed=7):
    """coarse (references, one offset at a time, random combinations) then coordinate refinement around the best"""
    os.makedirs(os.path.dirname(SWEEP_FILE), exist_ok=True)
    log = json.load(open(SWEEP_FILE)) if os.path.exists(SWEEP_FILE) else []
    done = {json.dumps(e["params"], sort_keys=True) for e in log}
    def run(par):
        P = dict(PARAMS); P.update(par); key = json.dumps(P, sort_keys=True)
        if key in done: return next(e for e in log if json.dumps(e["params"], sort_keys=True) == key)
        if len(log) >= budget: return None
        t = time.time(); r, M = evaluate(B, P, log); done.add(key)
        json.dump(log, open(SWEEP_FILE + ".tmp", "w"), indent=1); os.replace(SWEEP_FILE + ".tmp", SWEEP_FILE)
        print(f"[{len(log):3d}] gap {r['gap']:6.2f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} "
              f"ib10 {r['inband10']:.3f} contact {r['contact']:.3f} why {r['why']} {par} ({time.time() - t:.0f} s)", flush=True)
        return log[-1]
    # stage 0: references (the spherical chain with the champion's arm-fixed hub-3 block; zero offsets + the slide stack)
    run(dict(slides=0)); run(dict()); run(dict(S_a=5.0, S_t=5.0))
    # stage 1: one offset at a time. R3 offsets need no radial slide (their drift stays in the slide plane: s = (R3^T - I) c3);
    # R1 / R2 offsets need one (kinematics scan: with the spec's 2 slides, +-5 mm on R1 or R2 already loses > 40 % of poses)
    for k in ("o3a", "o3c"):
        for v in (-10, -5, 5, 10): run({k: v})
    for k in ("o1a", "o1c", "o2a", "o2c"):
        for v in (-10, -5, 5, 10): run({k: v, "R_r": 5.0})
        for v in (-10, 10): run({k: v, "R_r": 10.0})
    # stage 2: random small combinations (larger offsets run the slides out of range: dev scan, +-20 mm -> reach < 0.3)
    rng = np.random.default_rng(seed)
    for _ in range(40):
        par = {k: round(float(rng.uniform(-10, 10)), 1) for k in ("o1a", "o1c", "o2a", "o2c")}
        par.update(o3a=round(float(rng.uniform(-6, 6)), 1), o3c=round(float(rng.uniform(-6, 6)), 1), R_r=float(rng.choice([2.0, 5.0, 10.0])),
                   S_a=float(rng.choice([10.0, 15.0, 25.0])), S_t=float(rng.choice([10.0, 15.0, 25.0])))
        run(par)
    # stage 3: coordinate refinement around the best slide design (slides=1)
    steps = dict(o1a=2.5, o1c=2.5, o2a=2.5, o2c=2.5, o3a=2.5, o3c=2.5, R_r=2.0, S_a=5.0, S_t=5.0)
    lo = dict(R_r=0.5, S_a=5.0, S_t=5.0)
    for rnd in range(3):
        cand = [e for e in log if e["params"].get("slides", 1)]
        best = min(cand, key=lambda e: e["gap"]); improved = False
        for k, st in steps.items():
            for sg in (-1, 1):
                par = {kk: best["params"][kk] for kk in steps}; par[k] = max(lo.get(k, -40.0), par[k] + sg * st)
                e = run(par)
                if e is None: return log
                if e["gap"] < best["gap"] - 1e-9: improved = True
        if not improved: break
    return log


def sketch(M, path):
    """matplotlib sketch: skin near the shoulder (grey) and the metal by part, at rest and at the highest pose taken"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    B = M.B; taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    if not taken: return
    rest = min(taken, key=lambda i: B.poses[i]["elev"]); top = max(taken, key=lambda i: B.poses[i]["elev"])
    fig = plt.figure(figsize=(11, 5.2)); cols = dict(hub1="#d1495b", hub2="#edae49", rail="#00798c", carA="#30638e", hub3="#00798c", neck="#00798c", L1="#66a182", L2="#8d6a9f")
    for k, i in enumerate((rest, top)):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d"); V, F = B.skin(i); V = np.asarray(V)
        near = V[np.linalg.norm(V, axis=1) < 170][::9]; ax.scatter(near[:, 2], near[:, 0], near[:, 1], s=0.3, c="#bbbbbb", alpha=0.35)
        for nm, (m, X) in list(M.rigid.items()) + list(M.link_pts.items()):
            W = M.world(m, i, X); ax.scatter(W[:, 2], W[:, 0], W[:, 1], s=1.2, c=cols.get(nm, "k"), label=nm)
        p = B.poses[i]; ax.set_title(f"{'rest' if k == 0 else 'highest pose taken'}: plane {p['plane']:.0f}, elev {p['elev']:.0f}, axial {p['axial']:.0f}", fontsize=9)
        ax.view_init(elev=18, azim=-60 if k == 0 else -40); ax.set_xlabel("z lateral"); ax.set_ylabel("x anterior"); ax.set_zlabel("y up")
        ax.set_box_aspect((1, 1, 1)); lim = 150; ax.set_xlim(-60, lim); ax.set_ylim(-110, 100); ax.set_zlim(-90, 120)
        if k == 0: ax.legend(fontsize=7, markerscale=4, loc="upper left")
    fig.suptitle(f"{ID}: offset 3R + passive cuff slides, {json.dumps({k: v for k, v in M.p.items() if v})}", fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "kin":
        B = CB.Bench(n_clip=60, n_ws=160)
        for par in (dict(slides=0), dict(), dict(o3a=5), dict(o1a=5), dict(o1a=5, R_r=5.0), dict(o2c=5), dict(o2c=5, R_r=5.0)):
            print(par, kin_scan(B, par))
        sys.exit()
    nc, nw = (20, 40) if mode == "check" else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); print("bench", B.mode, len(B.idx), flush=True)
    if mode == "sweep":
        sweep(B, budget=int(sys.argv[2]) if len(sys.argv) > 2 else 110)
    else:
        r, M = evaluate(B, dict(PARAMS))
        print(json.dumps({k: v for k, v in r.items()}, default=str))
