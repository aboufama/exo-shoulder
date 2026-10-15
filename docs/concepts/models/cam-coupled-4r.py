"""Concept model: CAM-SCHEDULED 4R (id cam-coupled-4r), docs/concepts/catalogue.json.

A spherical 4R (every axis through the GH centre, O20 hubs) whose spare coordinate is not free: link 2 carries a
short tail with a roller pin that runs in a circular slot cut in an S-fixed plate on the base, so the slot schedules
the fold of the chain (J2) from J1 instead of letting it sag.
  scapula base (S) -> J1 (O20 hub, axis p1 fixed in the scapula) -> link 1 -> J2 (passive, scheduled) -> link 2
  (+ tail -> roller pin in the base slot) -> J3 -> link 3 -> J4 (O20 hub, axis W fixed in the humerus) -> arm-end neck
  -> the user's passive cuff slides (outside the count).

DOF: spherical mobility 3 x 4 bodies (links 1-3 + the arm) - 2 x 4 (J1-J4) - 1 (pin held on a curve) = 3. ACTIVE 3
(J1, J3, J4 need driving / sensing); PASSIVE 3 (J2, the pin's slide along the slot and the pin's roll: all set by
the closure). Nothing is an undriven spare: with the arm held, the 4R's self-motion moves the pin across the slot
(checked per pose: the 'hold' rate below).

Kinematics (the band evaluator's pin representation, pipeline/conformal/gpu/band_impl.py Band.chain, N = 4), in the
scapula frame: p1 = bvec(az, el); p2(q1) = cos a1 p1 + sin a1 (cos q1 e + sin q1 f) (e = unit(p1 x y), f = p1 x e);
p4 = HG W(w); p3 = the two-circle closure of p2 (arc a2) and p4 (arc a3) on the design's branch. The pin is fixed in
link 2: pi = cos(tail_r) p2 + sin(tail_r) (cos(tail_phi) u + sin(tail_phi) v), u = the direction of link 2 at p2
(towards p3), v = p2 x u (tail_phi 180 = the tail continues link 2 backwards past J2). The slot is the small circle
{x : x . n_s = cos beta_s} (n_s fixed in the scapula). IK per pose: G(q1) = pi(q1) . n_s - cos beta_s, scanned at
1 deg, sign changes refined by bisection (residual < 1e-9 rad, i.e. << 0.5 mm / 0.5 deg). A root's assembly mode is
(branch, sign of dG/dq1); the mode cannot change without passing a fold, which the hold check rejects.

The slot is parameterised by three KEY POSES (rest, overhead, behind the back) and the J1 angle the chain should have
at each: the pin's three positions there define the small circle (n_s, beta_s) - i.e. the slot interpolates a chosen
fold at three poses (equivalent to (n_s, beta_s) but searchable).

A pose is TAKEN iff: a root exists on the design's mode; J2 and J3 are >= sing_deg from their fold / stretch
singularities (tri_ok, as the band evaluator); the cam transmits (|cos| of the angle between the pin's J2 motion and
the slot normal >= pa_min); the slot holds the 4R's self-motion (cross-slot pin travel per radian of self-motion
>= hold_min); the pin is inside the slot's cut arc; along each fit clip the root is tracked at 10 fps with 3
substeps (HG slerped) and no joint (q1..q4, slot coordinate) jumps > JUMP deg per substep and the tracked root never
vanishes (a flip = a frame not followed; tracking re-acquires the nearest root after it); workspace poses are
reached by continuation along the slerp from the rest pose (2 deg steps); no two non-adjacent parts come within
1 mm (radial intervals [underside, top] of samples < 1.5 mm apart laterally; adjacent members share a joint and are
only exempt within hub radius + 2 mm of it, the tail / slot pair only within the pin pad); no metal inside the body.

Metal (tools/concept_baseline.py conventions): 8 mm straps (3 mm thick) on the great circles between consecutive
axes, sampled every ~2 mm along and across (arc_dirs, r_ref 70 mm); O20 hub discs (disc_dirs, 2.5 mm step) at every
axis; the arm-end neck (strap of neck_deg from p4 towards the humerus axis); link 2's tail (strap p2 -> pi, same
section) and a 10 mm pin pad at its end; the slot plate (S-fixed band slot_w = 14 mm wide over the cut arc + the pin
pad radius at both ends). Each member's radial profile is fixed in the member: the p-th percentile over the
kinematically valid poses of the outermost skin radius under the sample + 2 mm, + its level x (stack + t_link) =
6.15 mm (the baseline's stacking rule; 'levels' sets which member is on top at each joint: the tail rides one level
over the slot plate); link ends sit on their hubs (hub discs flat at their max). Skin radii come from a per-pose
radial map (0.5 deg nodes, sphere-traced on demand with B.dist, bilinear) - the final metric always uses B.dist on
the real points.

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/cam-coupled-4r.py [check|sweep|best|plot]
"""
import json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "cam-coupled-4r"
NAME = "Cam-scheduled 4R (pin-in-slot coupling of the spare)"
D2R = math.pi / 180
UP = 3.15 + 3.0                                              # baseline stack + link thickness (one level)
CROWN = 12.25                                                # O20 hub: lower face to cap crown (docs/HARDWARE.md v5)
JUMP = 15.0                                                  # max joint change per tracking substep (deg)
SUB = 3                                                      # tracking substeps between 10 fps frames

# defaults: the r13 4R (cad_r13_n4_s1343_1) with every arc >= 35 deg (short-link rule), slot keys from check()
PARAMS = dict(az=61.04, el=57.77, a=[35.0, 56.13, 35.0], w=[84.08, -10.84], branch=-1,
              tail_r=30.0, tail_phi=180.0, keys=[0.0, 60.0, -60.0], sigma=1,
              levels=[0, 1, 0, 1], pa_min=0.25, hold_min=0.1, sing_deg=10.0, hub_r=10.0, width=8.0, t_link=3.0,
              clear=2.0, neck_deg=25.0, slot_w=14.0, pin_r=5.0, pct=90)
SWEEP = dict(geometry="4R axes: az, el, a (each >= 35), w, branch", slot="keys = J1 angle at rest / overhead / behind-back",
             tail=dict(tail_r=[20, 30, 40], tail_phi=[120, 150, 180, 210, 240]), sigma=[1, -1],
             levels=[[0, 1, 0, 1], [0, 1, 2, 3]], pa_min=[0.15, 0.25, 0.35], pct=[60, 70, 80, 90, 95, 100])


# ---- small geometry ----------------------------------------------------------------------------------------------
def unit(x): x = np.asarray(x, float); return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)
def bvec(az, el): return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
def w_dir(d, a): return np.array([math.sin(d * D2R) * math.sin(a * D2R), -math.cos(d * D2R), math.sin(d * D2R) * math.cos(a * D2R)])
def dot(a, b): return (a * b).sum(-1)


def circ_int(c1, r1, c2, r2, sign):
    dd = np.clip(dot(c1, c2), -1, 1); n = unit(np.cross(c1, c2))
    den = 1 - dd ** 2 + 1e-12; a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - dot(p, p)
    return p + sign * np.sqrt(np.clip(h2, 0, None))[..., None] * n, h2 > 0


def tri_ok(x, y, a, b, sing):
    th = np.arccos(np.clip(dot(x, y), -1, 1))
    return (th >= abs(a - b) + sing) & (th <= min(a + b, 2 * math.pi - a - b) - sing)


def dihedral(c, a, b):
    """signed angle at axis c from the great circle c->a to c->b (rad)"""
    ta = unit(a - dot(a, c)[..., None] * c); tb = unit(b - dot(b, c)[..., None] * c)
    return np.arctan2(dot(np.cross(ta, tb), c), dot(ta, tb))


def slerp_R(R0, R1, n):
    """n rotations from R0 to R1 (inclusive of R1, exclusive of R0) along the geodesic"""
    from scipy.spatial.transform import Rotation as Rot
    rv = Rot.from_matrix(R0.T @ R1).as_rotvec()
    return [R0 @ Rot.from_rotvec(rv * (k / n)).as_matrix() for k in range(1, n + 1)]


# ---- chain ---------------------------------------------------------------------------------------------------------
class Chain:
    """kinematics of one design: q1 grid, pins, pin-in-slot roots"""
    def __init__(self, d):
        self.d = d; self.A = [x * D2R for x in d["a"]]
        self.p1 = bvec(d["az"], d["el"]); self.W0 = w_dir(*d["w"])
        e = unit(np.cross(self.p1, np.array([0.0, 1.0, 0.0]))); f = np.cross(self.p1, e); self.e, self.f = e, f
        self.sing = d["sing_deg"] * D2R; self.tr = d["tail_r"] * D2R; self.tp = d["tail_phi"] * D2R
        self.ns = None; self.cb = None

    def p2(self, q1):
        q1 = np.asarray(q1, float)[..., None]
        return math.cos(self.A[0]) * self.p1 + math.sin(self.A[0]) * (np.cos(q1) * self.e + np.sin(q1) * self.f)

    def state(self, q1, p4):
        """pins and pin position for J1 angles q1 (...,) and arm axes p4 (..., 3) (broadcast)"""
        p2 = self.p2(q1); p2, p4 = np.broadcast_arrays(p2, p4)
        p3, ok = circ_int(p2, self.A[1], p4, self.A[2], float(self.d["branch"]))
        ok = ok & tri_ok(np.broadcast_to(self.p1, p3.shape), p3, self.A[0], self.A[1], self.sing) & tri_ok(p2, p4, self.A[1], self.A[2], self.sing)
        u = unit(p3 - dot(p3, p2)[..., None] * p2); v = np.cross(p2, u)
        pi = math.cos(self.tr) * p2 + math.sin(self.tr) * (math.cos(self.tp) * u + math.sin(self.tp) * v)
        return p2, p3, pi, ok

    def set_slot(self, ns, cb):
        self.ns = unit(np.asarray(ns, float)); self.cb = float(cb)

    def slot_from_keys(self, HGk, q1k):
        """small circle through the pin positions of the key poses at the key J1 angles (deg)"""
        P = []
        for HG, q in zip(HGk, q1k):
            _, _, pi, ok = self.state(np.array(q * D2R), HG @ self.W0); P.append(pi)
        P = np.array(P); n = unit(np.cross(P[1] - P[0], P[2] - P[0])); cb = float(n @ P[0])
        if cb < 0: n, cb = -n, -cb
        self.set_slot(n, cb); return P

    def G(self, q1, p4):
        p2, p3, pi, ok = self.state(q1, p4); return dot(pi, self.ns) - self.cb, ok

    def roots(self, p4, step=1.0):
        """all roots q1 (rad) of the pin-in-slot closure for one arm axis p4 (3,), with slope sign and validity"""
        q = np.arange(-180, 180, step) * D2R; g, ok = self.G(q, p4[None])
        q2 = np.r_[q, q[0] + 2 * math.pi]; g2 = np.r_[g, g[0]]; ok2 = np.r_[ok, ok[0]]
        s = np.nonzero((np.sign(g2[:-1]) != np.sign(g2[1:])) & ok2[:-1] & ok2[1:])[0]
        if not len(s): return np.zeros(0), np.zeros(0)
        lo, hi = q2[s].copy(), q2[s + 1].copy(); glo = g2[s].copy()
        for _ in range(40):
            mid = 0.5 * (lo + hi); gm, _ = self.G(mid, p4[None]); same = np.sign(gm) == np.sign(glo)
            lo = np.where(same, mid, lo); glo = np.where(same, gm, glo); hi = np.where(same, hi, mid)
        r = 0.5 * (lo + hi); sl = np.sign(g2[s + 1] - g2[s])
        return (r + math.pi) % (2 * math.pi) - math.pi, sl

    def info(self, q1, p4, HG):
        """joint angles (deg), slot coordinate, transmission and hold of one configuration"""
        h = 1e-5
        p2, p3, pi, ok = self.state(np.array(q1), p4)
        _, _, pia, _ = self.state(np.array(q1 + h), p4); _, _, pib, _ = self.state(np.array(q1 - h), p4)
        dpi = (pia - pib) / (2 * h)                                  # pin velocity along the self-motion
        nt = self.ns - (self.ns @ pi) * pi; nn = np.linalg.norm(nt) + 1e-12
        t2 = np.cross(p2, pi)                                        # pin velocity per unit J2 at fixed J1
        pa = abs(t2 @ nt) / (np.linalg.norm(t2) * nn + 1e-12)
        hold = abs(dpi @ nt) / nn
        ref = HG @ unit(np.cross(self.W0, np.array([0.0, -1.0, 0.0])))  # humerus-fixed reference for J4
        q2 = dihedral(p2, self.p1, p3); q3 = dihedral(p3, p2, p4); q4 = dihedral(p4, p3, p4 + ref)
        sx = unit(np.cross(self.ns, np.array([0.0, 1.0, 0.0]))); sy = np.cross(self.ns, sx)
        psi = math.atan2(pi @ sy, pi @ sx)
        return dict(q=np.degrees([q1, q2, q3, q4]), psi=math.degrees(psi), pa=pa, hold=hold, ok=bool(ok),
                    pins=np.array([self.p1, p2, p3, p4]), pi=pi)


# ---- skin radius map (outermost skin crossing along each ray from GH, exact ray casting on the posed skin) ----------
RM_STEP, RM_LAT0, RM_LAT1, RM_RMAX = 0.5, -60.0, 90.0, 260.0      # deg, deg, deg, mm (the baseline's r_max)
RM_NLON, RM_NLAT = int(360 / RM_STEP), int((RM_LAT1 - RM_LAT0) / RM_STEP) + 1


def _lonlat(U):
    return np.degrees(np.arctan2(U[..., 1], U[..., 0])), np.degrees(np.arcsin(np.clip(U[..., 2], -1, 1)))


def build_rmap(V, F):
    """(RM_NLAT, RM_NLON) outermost skin radius (mm, <= RM_RMAX; 0 = no skin) on a lon / lat grid with the pole along
    +z (lateral). Every grid ray is intersected exactly (Moller-Trumbore) with the skin triangles whose lon / lat box
    (padded by one node) contains it."""
    r = np.linalg.norm(V, axis=1); keep = (r < RM_RMAX + 40)[F].any(1); F = F[keep]
    U = V / r[:, None]; lon, lat = _lonlat(U)
    Lo = lon[F]; La = lat[F]
    span = Lo.max(1) - Lo.min(1); wrap = span > 180; Lo = np.where(wrap[:, None] & (Lo < 0), Lo + 360, Lo)
    lo0, lo1 = Lo.min(1), Lo.max(1); la0, la1 = La.min(1), La.max(1)
    pole = la1 > 87.0; lo0 = np.where(pole, -180, lo0); lo1 = np.where(pole, 180 - RM_STEP, lo1); la1 = np.where(pole, 90, la1)
    i0 = np.floor((lo0 + 180) / RM_STEP).astype(int) - 1; i1 = np.ceil((lo1 + 180) / RM_STEP).astype(int) + 1
    j0 = np.maximum(np.floor((la0 - RM_LAT0) / RM_STEP).astype(int) - 1, 0); j1 = np.minimum(np.ceil((la1 - RM_LAT0) / RM_STEP).astype(int) + 1, RM_NLAT - 1)
    ok = j1 >= j0; F, i0, i1, j0, j1 = F[ok], i0[ok], i1[ok], j0[ok], j1[ok]
    ni, nj = i1 - i0 + 1, j1 - j0 + 1; cnt = ni * nj
    M = np.zeros((RM_NLAT, RM_NLON))
    CH = 200000; cs = np.cumsum(cnt)
    starts = np.r_[0, np.searchsorted(cs, np.arange(CH, cs[-1], CH))] if cs[-1] > CH else np.array([0])
    bounds = list(starts) + [len(F)]
    for a, b in zip(bounds[:-1], bounds[1:]):
        if b <= a: continue
        fi = np.repeat(np.arange(a, b), cnt[a:b]); k = np.arange(len(fi)) - np.repeat(cs[a:b] - cnt[a:b] - (cs[a] - cnt[a]), cnt[a:b])
        ii = i0[fi] + k % ni[fi]; jj = j0[fi] + k // ni[fi]
        lonn = (ii * RM_STEP - 180); latn = RM_LAT0 + jj * RM_STEP
        cl = np.cos(np.radians(latn)); D = np.stack([cl * np.cos(np.radians(lonn)), cl * np.sin(np.radians(lonn)), np.sin(np.radians(latn))], 1)
        A = V[F[fi, 0]]; E1 = V[F[fi, 1]] - A; E2 = V[F[fi, 2]] - A
        pv = np.cross(D, E2); det = dot(E1, pv); inv = 1.0 / np.where(np.abs(det) < 1e-12, 1e-12, det)
        tv = -A; u = dot(tv, pv) * inv; qv = np.cross(tv, E1); v = dot(D, qv) * inv; t = dot(E2, qv) * inv
        hit = (np.abs(det) > 1e-12) & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9) & (t > 0) & (t <= RM_RMAX)
        np.maximum.at(M, (jj[hit], ii[hit] % RM_NLON), t[hit])
    return M


def rmap_lookup(M, D):
    """bilinear outermost skin radius along unit directions D (..., 3)"""
    lon, lat = _lonlat(D)
    x = (lon + 180) / RM_STEP; y = np.clip((lat - RM_LAT0) / RM_STEP, 0, RM_NLAT - 1.000001)
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    x0 %= RM_NLON; x1 = (x0 + 1) % RM_NLON; y1 = y0 + 1
    return (M[y0, x0] * (1 - fx) * (1 - fy) + M[y0, x1] * fx * (1 - fy) + M[y1, x0] * (1 - fx) * fy + M[y1, x1] * fx * fy)
