"""seed-spm-3rrr: low-profile spherical parallel 3-RRR wrapped around the shoulder (concept screen, idealised geometry).

Topology (Agile-Eye type, every joint axis through the GH centre):
  scapula base frame (fixed in S) -- 3 base hubs HB_i (axes u_i: back / top / front of the shoulder)
  leg i: HB_i -> proximal arc link P_i (arc a1 on the sphere) -> passive hub HW_i (axis w_i) -> distal arc link D_i
         (arc a2) -> passive hub HV_i (axis v_i, fixed in the humerus frame) on the platform ring PF (fixed to the arm)
Active DOF 3 (the base joints), passive 6 (HW_i, HV_i), all set by the loop closures (Grubler, spherical:
3*(8-1-9)+9 = 3); the arm drives everything when unpowered.

Model (mm, thorax frame of tools/concept_bench.py, origin = GH):
  * IK, closed form per leg: w_i on the intersection of the cone (a1 about u_i) and the cone (a2 about v_i); the
    branch sign br_i (side of u_i x v_i) is fixed for the whole run -> joint values are continuous wherever the
    pose is reachable; along each clip the path between consecutive bench frames is checked on 6 slerp sub-steps
    (cones must still intersect and the Jacobian stay conditioned); a failed path = the frame is not followed.
  * Singularity: J = B^-1 A (A rows (w_i x v_i), B = diag((u_i x w_i).v_i)) - pose not taken if cond(J) > 50
    (type-1 leg singularities and type-2 platform singularities alike).
  * Parts at their real size: 9 O20 hubs (12.25 mm from the lower member's skin face to the crown, upper member
    3.15 above the lower one: docs/HARDWARE.md v5 joint), links as 8 x 3 mm straps on the great-circle arcs between
    their two axes, base frame = 2 straps joining the 3 base hubs (C over the shoulder), platform = 2 straps joining
    the 3 platform hubs (C around the upper arm) + the arm end: a 25 deg strap from the middle platform hub toward the
    humerus axis, fixed to the arm (as the baseline's neck).
  * Shapes: every part is rigid in its own frame; its skin-face radius at each (s, t) sample is fitted over the
    kinematically valid poses: the q-quantile over those poses of the skin under that ray (the FIRST exit of the ray
    from GH, exact ray-triangle cube map, ~0.8 deg cells: a part may sit in a gap between arm and trunk; the baseline
    uses the outermost crossing) + `clear`; q < 1 lets the worst poses collide and lose them (the baseline's
    percentile sweep). Hub levels likewise: flat O20 discs at the max over the disc.
    A link leaves a hub at the hub's level (the upper member 3.15 above) and may ramp down to its own fitted
    profile at <= 45 deg outside a 2 mm land.
  * Taken pose: every leg closes (exact closed form, residual 0), cond(J) <= 50, clip path continuous, no two
    non-adjacent parts closer than 1 mm (straps as 2 mm-spaced mid-surfaces with their 1.5 mm half-thickness, hubs as
    cylinders); adjacent parts (sharing a hub) are also checked outside that hub's footprint. Contact: every metal
    surface (strap undersides + tops, hub faces, walls, crowns) via B.dist; recorded for in-band: the skin-facing
    surfaces (strap undersides outside the hub footprints + the hubs' lower faces), 2 mm grid = 1 point / 4 mm2.

    python3 docs/concepts/models/seed-spm-3rrr.py check        # a few poses, printed
    python3 docs/concepts/models/seed-spm-3rrr.py sweep [n]     # the sweep (writes sweeps/ and rows/)
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                        # noqa: E402
BP = CB.BP

ID = "seed-spm-3rrr"
HUB_R, HUB_H, STACK, T_LINK, HW = 10.0, 12.25, 3.15, 3.0, 4.0     # O20 v5 joint; 8 x 3 straps (r20 evaluator: t_link 3, hw 4)
PART_CLEAR = 1.0                                                  # >= 1 mm between non-adjacent parts
ADJ_GAP = 0.1                                                     # adjacent members of one joint: running gap (v5: 0.15)
COND_MAX = 50.0
SP = 2.0                                                          # sample spacing: 1 point / 4 mm2
LAND, SLOPE = 2.0, 1.0                                            # flat land outside a hub, then <= 45 deg ramp
NECK_DEG = 25.0                                                   # arm-end strap toward the cuff (the baseline's neck_deg)
R_SAMP = np.arange(14.0, 232.0, 4.0)                              # radial samples for the skin crossing

PARAMS = dict(b_th=60.0, b_ph=40.0, b_rho=55.0, b_psi0=0.0, b_psis=110.0,   # base: centre (deg from lateral, azimuth 0 = up, 90 = back),
                                                                          # 3 spots at b_rho deg around it, at b_psi0 + (-1, 0, 1) * b_psis
              p_cone=50.0, p_az=0.0, p_spread=80.0,               # platform axes: cone about the humerus, azimuths (0 = lateral, + anterior)
              perm=(0, 1, 2),                                     # leg i joins base spot i to platform axis perm[i]
              a1=80.0, a2=80.0, br=(1, 1, 1),                     # arc angles, branch per leg
              w_lower="P",                                        # which link is the lower member at HW_i
              lay_P=0.0, lay_D=4.0,                               # extra height of the proximal / distal links over their fitted profile (mm)
              clear=2.0, q=1.0, drop=1)                           # fit clearance (mm), fit quantile, platform drop strap to the cuff

PERMS = [(0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)]
SWEEP = dict(b_th=(20, 100), b_ph=(-60, 150), b_rho=(25, 75), b_psi0=(0, 360), b_psis=(60, 150),
             p_cone=(30, 80), p_az=(-180, 180), p_spread=(40, 140), a1=(45, 115), a2=(45, 115),
             br=[(s0, s1, s2) for s0 in (1, -1) for s1 in (1, -1) for s2 in (1, -1)], perm=PERMS,
             w_lower=("P", "D"), lay_P=(0.0, 4.0), lay_D=(0.0, 4.0, 8.0), clear=(2.0, 3.0), q=(0.6, 0.7, 0.8, 0.9, 0.95, 1.0))


def unit(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)


def rot(ax, deg):
    return BP.rot(ax, deg * math.pi / 180)


# ------------------------------------------------------------------------------------------------ pose data
class Rig:
    """per-bench pose data: S, H rotations, relative rotation, clip order"""
    def __init__(self, B):
        self.B = B; n = len(B.poses)
        self.S = np.array([B.frames(i)["S"][0] for i in range(n)]); self.H = np.array([B.frames(i)["H"][0] for i in range(n)])
        r = BP._rig(); L = r.L
        self.a_loc = unit(np.array(L["elbow"]))                   # humerus axis, H-local
        f0 = BP.segs(L, r.s, dict(plane=0, elev=0, axial=0, flex=0, pron=0))[0]; self.Hz = f0[2][0]
        h0 = self.Hz @ self.a_loc
        lat = np.array([0, 0, 1.0]) - h0[2] * h0; self.lat0 = unit(lat); self.ant0 = unit(np.cross(h0, self.lat0))
        if self.ant0[0] < 0: self.ant0 = -self.ant0
        self.h0 = h0
        self.Q = np.einsum("nji,njk->nik", self.S, self.H)        # humerus in the scapula frame
        self.order = B.clip_order(); self.prev = {}
        for c, js in self.order.items():
            for a, b in zip(js[:-1], js[1:]): self.prev[b] = a
        self.kind = np.array(B.kind)


def sph(th, ph):
    """direction th deg from lateral (+z), azimuth ph (0 = up, 90 = back, -90 = front)"""
    t, f = math.radians(th), math.radians(ph)
    return np.array([-math.sin(t) * math.sin(f), math.sin(t) * math.cos(f), math.cos(t)])


def axes(p, rig):
    """u_loc (3,3) in the scapula frame (= thorax frame at rest), v_loc (3,3) in the humerus frame; leg i = base spot i
    with platform axis perm[i]"""
    c = sph(p["b_th"], p["b_ph"])
    e1 = unit(sph(p["b_th"] + 1e-3, p["b_ph"]) - c); e2 = np.cross(c, e1)
    U = []
    for k in (-1, 0, 1):
        ps = math.radians(p["b_psi0"] + k * p["b_psis"]); d = math.cos(ps) * e1 + math.sin(ps) * e2
        U.append(rot(np.cross(c, d), p["b_rho"]) @ c)
    cb, sb = math.cos(math.radians(p["p_cone"])), math.sin(math.radians(p["p_cone"]))
    V0 = []
    for az in (p["p_az"] - p["p_spread"], p["p_az"], p["p_az"] + p["p_spread"]):
        a = math.radians(az); V0.append(cb * rig.h0 + sb * (math.cos(a) * rig.lat0 + math.sin(a) * rig.ant0))
    V = (rig.Hz.T @ np.array(V0).T).T[list(p["perm"])]
    return unit(np.array(U)), unit(V)


def ik(U, V, a1, a2, br):
    """U, V (..., 3, 3) axes per leg; returns W (..., 3, 3), disc (..., 3) (< 0: the leg cannot close)"""
    c1, c2 = math.cos(math.radians(a1)), math.cos(math.radians(a2))
    k = np.sum(U * V, -1); k = np.clip(k, -1 + 1e-9, 1 - 1e-9); den = 1 - k * k
    a = (c1 - k * c2) / den; b = (c2 - k * c1) / den
    disc = 1 - a * a - b * b - 2 * a * b * k
    n = np.cross(U, V); n = n / np.linalg.norm(n, axis=-1, keepdims=True)
    c = np.sqrt(np.maximum(disc, 0)) * np.asarray(br, float)
    W = a[..., None] * U + b[..., None] * V + c[..., None] * n
    return W, disc


def cond_J(U, W, V):
    A = np.cross(W, V); Bd = np.einsum("...i,...i->...", np.cross(U, W), V)
    with np.errstate(divide="ignore", invalid="ignore"):
        J = A / Bd[..., None]
    J = np.where(np.isfinite(J), J, 1e9)
    s = np.linalg.svd(J, compute_uv=False)
    return s[..., 0] / np.maximum(s[..., -1], 1e-12)


def slerp_R(R0, R1, t):
    """rotation matrices on the geodesic R0 -> R1"""
    D = R0.T @ R1; ang = math.acos(np.clip((np.trace(D) - 1) / 2, -1, 1))
    if ang < 1e-9: return [R0 for _ in t]
    ax = np.array([D[2, 1] - D[1, 2], D[0, 2] - D[2, 0], D[1, 0] - D[0, 1]])
    if np.linalg.norm(ax) < 1e-9:                                 # 180 deg: axis from the symmetric part
        w, v = np.linalg.eigh((D + np.eye(3)) / 2); ax = v[:, -1]
    ax = unit(ax); return [R0 @ BP.rot(ax, ang * tt) for tt in t]


def kinematics(p, rig, n_sub=6):
    """per pose: W (n,3,3) world, U, V world, kinematic ok (n,), reason codes"""
    Ul, Vl = axes(p, rig)
    US = np.broadcast_to(Ul, (len(rig.Q), 3, 3)); VS = np.einsum("nij,lj->nli", rig.Q, Vl)        # scapula frame
    WS, disc = ik(US, VS, p["a1"], p["a2"], p["br"])
    cj = cond_J(US, WS, VS)
    reach_ok = (disc > 1e-6).all(1) & (cj <= COND_MAX)
    path_ok = np.ones(len(rig.Q), bool)
    for j, i0 in rig.prev.items():                                # clip continuity: the path from the previous frame
        if not reach_ok[j] or not reach_ok[i0]: continue
        Rs = np.array(slerp_R(rig.Q[i0], rig.Q[j], np.linspace(0, 1, n_sub + 2)[1:-1]))
        vs = np.einsum("nij,lj->nli", Rs, Vl); us = np.broadcast_to(Ul, vs.shape)
        ws, dd = ik(us, vs, p["a1"], p["a2"], p["br"])
        if not ((dd > 1e-6).all() and (cond_J(us, ws, vs) <= COND_MAX).all()): path_ok[j] = False
    U = np.einsum("nij,nlj->nli", rig.S, US); W = np.einsum("nij,nlj->nli", rig.S, WS); V = np.einsum("nij,nlj->nli", rig.S, VS)
    return dict(U=U, V=V, W=W, disc=disc, cond=cj, kin=reach_ok & path_ok, reach_ok=reach_ok, path_ok=path_ok, Ul=Ul, Vl=Vl)


# ------------------------------------------------------------------------------------------------ skin ray map
CM_N, CM_RMAX = 112, 270.0                                        # cube-map cells per face edge (~0.8 deg), ray length (mm)
_FACES = [(np.array(a, float), np.array(b, float), np.array(c, float)) for a, b, c in
          [((1, 0, 0), (0, 1, 0), (0, 0, 1)), ((-1, 0, 0), (0, 0, 1), (0, 1, 0)), ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
           ((0, -1, 0), (1, 0, 0), (0, 0, 1)), ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (0, 1, 0), (1, 0, 0))]]


def raymap(V, F):
    """first skin exit along every cube-map direction from GH (6, N, N) mm (GH is inside the body: the first point
    where exits - entries = 1; inf = no exit within CM_RMAX) and the next hit beyond it (the far side of the gap a
    part may sit in, e.g. the trunk beyond the arm; inf = open). Exact ray-triangle hits: a ray from the origin hits a
    planar triangle iff its gnomonic projection lies in the projected triangle (great circles project to lines)."""
    keep = (np.linalg.norm(V, axis=1) < CM_RMAX)[F].all(1); T = F[keep]
    A, Bv, C = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]; Nn = np.cross(Bv - A, C - A); h = np.sum(Nn * A, 1)
    out = np.full((6, CM_N, CM_N), -1.0); sgn = np.zeros((6, CM_N, CM_N)); nxt = np.full((6, CM_N, CM_N), np.inf)
    g = (np.arange(CM_N) + 0.5) / CM_N * 2 - 1
    for f, (ax, e1, e2) in enumerate(_FACES):
        zA, zB, zC = A @ ax, Bv @ ax, C @ ax
        m = (zA > 1) & (zB > 1) & (zC > 1)
        if not m.any(): continue
        pa = np.stack([A[m] @ e1 / zA[m], A[m] @ e2 / zA[m]], 1); pb = np.stack([Bv[m] @ e1 / zB[m], Bv[m] @ e2 / zB[m]], 1)
        pc = np.stack([C[m] @ e1 / zC[m], C[m] @ e2 / zC[m]], 1)
        lo = np.minimum(np.minimum(pa, pb), pc); hi = np.maximum(np.maximum(pa, pb), pc)
        ok = (hi[:, 0] > -1) & (lo[:, 0] < 1) & (hi[:, 1] > -1) & (lo[:, 1] < 1)
        i0 = np.clip(np.ceil((lo[:, 0] + 1) / 2 * CM_N - 0.5), 0, CM_N - 1).astype(int); i1 = np.clip(np.floor((hi[:, 0] + 1) / 2 * CM_N - 0.5), 0, CM_N - 1).astype(int)
        j0 = np.clip(np.ceil((lo[:, 1] + 1) / 2 * CM_N - 0.5), 0, CM_N - 1).astype(int); j1 = np.clip(np.floor((hi[:, 1] + 1) / 2 * CM_N - 0.5), 0, CM_N - 1).astype(int)
        ni = np.maximum(i1 - i0 + 1, 0); nj = np.maximum(j1 - j0 + 1, 0); ok &= (ni > 0) & (nj > 0) & (ni * nj < 4000)
        idx = np.nonzero(ok)[0]; cnt = ni[idx] * nj[idx]
        tri = np.repeat(idx, cnt); off = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        ci = i0[tri] + off // nj[tri]; cj = j0[tri] + off % nj[tri]
        x, y = g[ci], g[cj]
        a_, b_, c_ = pa[tri], pb[tri], pc[tri]
        d = (b_[:, 1] - c_[:, 1]) * (a_[:, 0] - c_[:, 0]) + (c_[:, 0] - b_[:, 0]) * (a_[:, 1] - c_[:, 1])
        d = np.where(np.abs(d) < 1e-15, 1e-15, d)
        l1 = ((b_[:, 1] - c_[:, 1]) * (x - c_[:, 0]) + (c_[:, 0] - b_[:, 0]) * (y - c_[:, 1])) / d
        l2 = ((c_[:, 1] - a_[:, 1]) * (x - c_[:, 0]) + (a_[:, 0] - c_[:, 0]) * (y - c_[:, 1])) / d
        hit = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
        tri, ci, cj, x, y = tri[hit], ci[hit], cj[hit], x[hit], y[hit]
        dirs = ax[None] + x[:, None] * e1[None] + y[:, None] * e2[None]; dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
        mt = np.nonzero(m)[0][tri]
        nd = np.sum(Nn[mt] * dirs, 1); t = h[mt] / np.where(np.abs(nd) < 1e-12, 1e-12, nd)
        good = t > 0; ci, cj, t, nd = ci[good], cj[good], t[good], nd[good]
        o = np.lexsort((t, cj, ci)); ci, cj, t, nd = ci[o], cj[o], t[o], nd[o]
        lin = ci * CM_N + cj; start = np.r_[True, lin[1:] != lin[:-1]]
        dl = np.where(nd > 0, 1, -1); cs = np.cumsum(dl); base = np.maximum.accumulate(np.where(start, np.arange(len(cs)), 0))
        net = cs - np.r_[0, cs][base]                             # exits - entries so far within the cell (GH is inside: 1 = out)
        first = (net == 1) & (dl > 0)
        fi = np.nonzero(first)[0]; fl = lin[fi]; keep1 = np.r_[True, fl[1:] != fl[:-1]]
        out[f].flat[fl[keep1]] = t[fi[keep1]]; sgn[f].flat[fl[keep1]] = 1.0
        fn = fi[keep1] + 1; has = fn < len(lin); fn = fn[has]; same = lin[fn] == fl[keep1][has]   # the next hit after the first exit
        nxt[f].flat[lin[fn[same]]] = t[fn[same]]
    return np.where((out > 0) & (sgn > 0), out, np.inf).astype(np.float32), nxt.astype(np.float32)


def cm_lookup(M, D, I=None, low=False):
    """bilinear lookup of a cube map M (6, N, N) - or of maps M (n, 6, N, N) at pose indices I (m,) - at unit
    directions D (m, 3); inf where any corner is inf; low=True: the smallest corner instead (a conservative ceiling)"""
    D = np.asarray(D, float); ad = np.abs(D); k = np.argmax(ad, 1); sg = D[np.arange(len(D)), k] > 0
    face = np.where(k == 0, np.where(sg, 0, 1), np.where(k == 1, np.where(sg, 2, 3), np.where(sg, 4, 5)))
    out = np.empty(len(D))
    for f, (ax, e1, e2) in enumerate(_FACES):
        m = face == f
        if not m.any(): continue
        z = D[m] @ ax; x = (D[m] @ e1) / z; y = (D[m] @ e2) / z
        fx = np.clip((x + 1) / 2 * CM_N - 0.5, 0, CM_N - 1 - 1e-9); fy = np.clip((y + 1) / 2 * CM_N - 0.5, 0, CM_N - 1 - 1e-9)
        x0 = np.floor(fx).astype(int); y0 = np.floor(fy).astype(int); x1 = np.minimum(x0 + 1, CM_N - 1); y1 = np.minimum(y0 + 1, CM_N - 1)
        u = fx - x0; v = fy - y0
        if I is None: G = M[f]; c00, c10, c01, c11 = G[x0, y0], G[x1, y0], G[x0, y1], G[x1, y1]
        else: ii = I[m]; c00, c10, c01, c11 = M[ii, f, x0, y0], M[ii, f, x1, y0], M[ii, f, x0, y1], M[ii, f, x1, y1]
        if low: out[m] = np.minimum(np.minimum(c00, c10), np.minimum(c01, c11)); continue
        with np.errstate(invalid="ignore"): val = c00 * (1 - u) * (1 - v) + c10 * u * (1 - v) + c01 * (1 - u) * v + c11 * u * v
        out[m] = np.where(np.isfinite(c00) & np.isfinite(c10) & np.isfinite(c01) & np.isfinite(c11), val, np.inf)
    return out


class SkinMaps:
    """per-pose cube maps of the first skin exit from GH (built once per bench, cached in .cache/concept_models)"""
    def __init__(self, B, verbose=True):
        d = os.path.join(REPO, ".cache", "concept_models", ID); os.makedirs(d, exist_ok=True)
        path = os.path.join(d, f"raymap2_{B.key}_{CM_N}.npy")
        if not os.path.exists(path):
            t = time.time(); M = np.empty((len(B.poses), 2, 6, CM_N, CM_N), np.float32)
            Fi = np.asarray(BP.F)
            for i in range(len(B.poses)):
                M[i, 0], M[i, 1] = raymap(np.asarray(B._verts(i), float), Fi)
                if verbose and i % 20 == 0: print(f"  raymap {i}/{len(B.poses)} {time.time() - t:.0f} s", flush=True)
            np.save(path + ".tmp.npy", M); os.replace(path + ".tmp.npy", path)
        A = np.load(path); self.M = np.ascontiguousarray(A[:, 0]); self.N = np.ascontiguousarray(A[:, 1])

    def r(self, i, D):
        return cm_lookup(self.M[i], D)

    def ceil(self, i, D):
        return cm_lookup(self.N[i], D, low=True)

    def rm(self, I, D, ceil=False):
        """poses I (n,), directions D (n, m, 3) -> (n, m) first exit (or, ceil=True, the next hit beyond it)"""
        n, m = D.shape[:2]
        return cm_lookup(self.N if ceil else self.M, D.reshape(-1, 3), np.repeat(np.asarray(I), m), low=ceil).reshape(n, m)


# ------------------------------------------------------------------------------------------------ geometry
def skin_r_dist(B, i, D):
    """outermost skin crossing (mm from GH) along unit directions D (m, 3) for pose i (inf: the ray stays inside)"""
    d = B.dist(i, D[:, None, :] * R_SAMP[None, :, None])          # (m, K)
    ins = d < 0; any_in = ins.any(1)
    last = len(R_SAMP) - 1 - np.argmax(ins[:, ::-1], axis=1)     # last inside sample
    out = np.full(len(D), R_SAMP[0])
    m = any_in & (last < len(R_SAMP) - 1)
    l = last[m]; d0 = d[m, l]; d1 = d[m, l + 1]
    out[m] = R_SAMP[l] + (R_SAMP[l + 1] - R_SAMP[l]) * (-d0) / np.maximum(d1 - d0, 1e-9)
    out[any_in & (last == len(R_SAMP) - 1)] = np.inf
    return out


def arc_grid(alpha_deg, rho_nom):
    """(s, t) grid of a strap on an arc of alpha deg at nominal radius rho_nom: s in [0, 1], t across (mm)"""
    L = math.radians(alpha_deg) * rho_nom; ns = max(2, int(math.ceil(L / SP)))
    s = (np.arange(ns) + 0.5) / ns; t = np.arange(-HW + SP / 2, HW, SP)
    S, T = np.meshgrid(s, t, indexing="ij"); return S.ravel(), T.ravel()


def arc_dirs(A, Bv, s, t, rho_c):
    """directions of strap samples (s, t) on arcs A -> Bv (n, 3) each; rho_c (len s) centre radius for the offset"""
    ang = np.arccos(np.clip(np.sum(A * Bv, -1), -1, 1))[:, None]                  # (n, 1)
    sa = np.sin(ang); sa = np.where(sa < 1e-9, 1e-9, sa)
    w0 = np.sin((1 - s)[None, :] * ang) / sa; w1 = np.sin(s[None, :] * ang) / sa
    C = w0[..., None] * A[:, None, :] + w1[..., None] * Bv[:, None, :]           # (n, m, 3) on the great circle
    N = unit(np.cross(A, Bv))[:, None, :]
    return unit(C * rho_c[None, :, None] + t[None, :, None] * N), C, N


def disk_dirs(Ax, r_lvl, rad=HUB_R):
    """sample directions of an O(2 rad) disk on axis Ax (n,3) at radius r_lvl: 2 mm grid"""
    g = np.arange(-rad + SP / 2, rad, SP); X, Y = np.meshgrid(g, g); m = X ** 2 + Y ** 2 <= rad ** 2
    x, y = X[m], Y[m]
    e1 = unit(np.cross(Ax, np.where(np.abs(Ax[:, :1]) < 0.9, [[1.0, 0, 0]], [[0, 1.0, 0]])))
    e2 = np.cross(Ax, e1)
    P = r_lvl * Ax[:, None, :] + x[None, :, None] * e1[:, None, :] + y[None, :, None] * e2[:, None, :]
    return P, e1, e2


class Model:
    """one configuration: kinematics + fitted rigid shapes; metal(i) -> sample points or None"""
    def __init__(self, p, B, rig=None, maps=None, verbose=False):
        self.p = dict(PARAMS, **p); self.B = B; self.rig = rig or Rig(B); self.v = verbose
        self.maps = maps or SkinMaps(B)
        self.K = kinematics(self.p, self.rig)
        self.kin = self.K["kin"].copy()
        self.fit()

    # ---- parts: list of (name, kind, endpoints-getter, frame-fit poses)
    def _parts(self):
        K = self.K; p = self.p
        parts = []
        for i in range(3):
            parts.append((f"P{i}", "arc", lambda i=i: (K["U"][:, i], K["W"][:, i]), p["a1"]))
            parts.append((f"D{i}", "arc", lambda i=i: (K["W"][:, i], K["V"][:, i]), p["a2"]))
        Ub = K["U"]; Vb = K["V"]
        ab = lambda X, Y: float(np.degrees(np.arccos(np.clip(np.sum(X[0] * Y[0]), -1, 1))))
        parts.append(("BF0", "arc", lambda: (Ub[:, 0], Ub[:, 1]), ab(Ub[:, 0], Ub[:, 1])))
        parts.append(("BF1", "arc", lambda: (Ub[:, 1], Ub[:, 2]), ab(Ub[:, 1], Ub[:, 2])))
        parts.append(("PF0", "arc", lambda: (Vb[:, 0], Vb[:, 1]), ab(Vb[:, 0], Vb[:, 1])))
        parts.append(("PF1", "arc", lambda: (Vb[:, 1], Vb[:, 2]), ab(Vb[:, 1], Vb[:, 2])))
        if p.get("drop"):                                         # arm end toward the cuff, as the baseline's neck: NECK_DEG
            rig = self.rig; j = list(p["perm"]).index(1)          # from the middle platform hub toward the humerus axis
            vl = self.K["Vl"][j]; al = rig.a_loc
            ang = min(NECK_DEG, math.degrees(math.acos(np.clip(vl @ al, -1, 1))) - 5.0)
            if ang > 5:
                tl = unit(al - (al @ vl) * vl); dl = math.cos(math.radians(ang)) * vl + math.sin(math.radians(ang)) * tl
                Dc = np.einsum("nij,j->ni", rig.H, dl); Vm = Vb[:, j]
                parts.append(("PFd", "arc", lambda: (Vm, Dc), ang))
        return parts

    def fit(self):
        """hub levels and strap profiles over the kinematically taken poses"""
        B, K, p = self.B, self.K, self.p
        poses = np.nonzero(self.kin)[0]; self.fitposes = poses
        if not len(poses): self.ok = False; return
        q = p["q"]; agg = (lambda X: np.max(X, 0)) if q >= 1 else (lambda X: np.quantile(X, q, axis=0))
        # hub levels: disk at radius 60 (directions only), over the poses
        hubs = {}
        for nm, key, li in [(f"HB{i}", "U", i) for i in range(3)] + [(f"HW{i}", "W", i) for i in range(3)] + [(f"HV{i}", "V", i) for i in range(3)]:
            Ax = K[key][poses, li]; P, _, _ = disk_dirs(Ax, 60.0); D = unit(P)
            R = self.maps.rm(poses, D)                                                       # (np, m)
            R = np.where(np.isfinite(R), R, 400.0)
            hubs[nm] = float(np.max(agg(R))) + p["clear"]
        self.hub = hubs
        # strap profiles
        lv = self.levels()
        self.straps = {}
        for nm, kind, get, alpha in self._parts():
            A, Bv = get(); A, Bv = A[poses], Bv[poses]
            e0, e1 = lv[nm]
            rho_nom = 0.5 * (e0 + e1)
            for _len in range(4):                                     # arc sampled at 2 mm at its real mean radius
                s, t = arc_grid(alpha, rho_nom); rc = np.full(len(s), rho_nom)
                lenL = math.radians(alpha) * rho_nom; l0 = s * lenL; l1 = (1 - s) * lenL
                for _pass in range(2):                                # centre radius for the width offset
                    D, C, N = arc_dirs(A, Bv, s, t, rc)
                    R = self.maps.rm(poses, D)
                    R = np.where(np.isfinite(R), R, 400.0)
                    fitted = agg(R) + p["clear"] + (p["lay_P"] if nm[0] == "P" and nm[1].isdigit() else p["lay_D"] if nm[0] == "D" else 0.0)
                    rho = np.maximum.reduce([fitted, e0 - np.maximum(0, l0 - HUB_R - LAND) * SLOPE, e1 - np.maximum(0, l1 - HUB_R - LAND) * SLOPE])
                    rho = np.where(l0 < HUB_R + LAND, np.maximum(rho, e0), rho); rho = np.where(l1 < HUB_R + LAND, np.maximum(rho, e1), rho)
                    us, inv = np.unique(s, return_inverse=True)
                    rc = (np.bincount(inv, rho) / np.bincount(inv))[inv]
                new = float(np.mean(rho))
                if abs(new - rho_nom) <= 3: break
                rho_nom = new
            Aa, Ba = get(); Dall = arc_dirs(Aa, Ba, s, t, rc)[0]
            self.straps[nm] = dict(get=get, s=s, t=t, rho=rho, rc=rc, alpha=alpha, e=(e0, e1), len=math.radians(alpha) * rho_nom, D=Dall)
        self.ok = True

    def levels(self):
        """skin-face radius of each strap at its two ends (lower member = hub level, upper member = + STACK)"""
        h = self.hub; lo = self.p["w_lower"] == "P"
        lv = {}
        for i in range(3):
            lv[f"P{i}"] = (h[f"HB{i}"] + STACK, h[f"HW{i}"] + (0 if lo else STACK))
            lv[f"D{i}"] = (h[f"HW{i}"] + (STACK if lo else 0), h[f"HV{i}"] + STACK)
        lv["BF0"] = (h["HB0"], h["HB1"]); lv["BF1"] = (h["HB1"], h["HB2"])
        lv["PF0"] = (h["HV0"], h["HV1"]); lv["PF1"] = (h["HV1"], h["HV2"])
        j = list(self.p["perm"]).index(1); lv["PFd"] = (h[f"HV{j}"], 0.0)
        return lv

    def hub_axes(self, i):
        K = self.K
        return {f"HB{l}": K["U"][i, l] for l in range(3)} | {f"HW{l}": K["W"][i, l] for l in range(3)} | {f"HV{l}": K["V"][i, l] for l in range(3)}

    def strap_pts(self, nm, i):
        """underside points (m, 3), mid-surface (m, 3), tops (m, 3) of strap nm at pose i"""
        st = self.straps[nm]; D = st["D"][i]; rho = st["rho"]
        return D * rho[:, None], D * (rho + T_LINK / 2)[:, None], D * (rho + T_LINK)[:, None]

    def metal(self, i, detail=False):
        """skin-facing points (k, 3), all-metal points (k2, 3), or None if pose i cannot be taken"""
        if not self.ok or not self.kin[i]: return None
        ax = self.hub_axes(i); hub = self.hub
        hub_of = {f"HB{l}": ("BF", f"P{l}") for l in range(3)} | {f"HW{l}": (f"P{l}", f"D{l}") for l in range(3)} | {f"HV{l}": (f"D{l}", "PF") for l in range(3)}
        grp = lambda nm: nm[:2] if nm[:2] in ("BF", "PF") else nm
        under, mid, top = {}, {}, {}
        for nm in self.straps:
            u, m_, t_ = self.strap_pts(nm, i); under[nm], mid[nm], top[nm] = u, m_, t_
        # mask strap points inside their own hub footprints (hidden / the hub's own face) and for collision exclusion
        def near_hub(P, h, extra=0.0):
            a = ax[h]; z = P @ a; rr = np.linalg.norm(P - z[:, None] * a, axis=1); return rr < HUB_R + extra
        # ---- self-collision
        groups = {}
        for nm in self.straps: groups.setdefault(grp(nm), []).append(nm)
        gpts = {g: np.concatenate([mid[n] for n in ns]) for g, ns in groups.items()}
        gkeep = {}
        names = list(groups)
        shared = {}
        for h, (g1, g2) in hub_of.items(): shared.setdefault(frozenset((g1, g2)), []).append(h)
        trees = {g: cKDTree(P) for g, P in gpts.items()}
        thr = T_LINK + PART_CLEAR
        for a_ in range(len(names)):
            for b_ in range(a_ + 1, len(names)):
                g1, g2 = names[a_], names[b_]
                P1, P2 = gpts[g1], gpts[g2]
                hs = shared.get(frozenset((g1, g2)), [])
                th_ = thr
                if hs:                                            # adjacent: exclude the shared hubs' zones; they are the two
                    m1 = np.ones(len(P1), bool); m2 = np.ones(len(P2), bool)   # members of one v5 joint, stacked with its
                    for h in hs: m1 &= ~near_hub(P1, h, 4.0); m2 &= ~near_hub(P2, h, 4.0)   # 0.15 running gap: they may
                    P1, P2 = P1[m1], P2[m2]                       # overlap outside the hub but never interpenetrate
                    if not len(P1) or not len(P2): continue
                    t2 = cKDTree(P2); th_ = T_LINK + ADJ_GAP
                else: t2 = trees[g2]
                dd, _ = t2.query(P1, distance_upper_bound=th_)
                if np.isfinite(dd).any():
                    return ("collide", g1, g2) if detail else None
        # hubs vs straps of other groups
        for h, (g1, g2) in hub_of.items():
            a = ax[h]; r0 = hub[h]
            for g, P in gpts.items():
                if g in (g1, g2): continue
                z = P @ a - r0; rr = np.linalg.norm(P - (P @ a)[:, None] * a, axis=1)
                if np.any((z > -T_LINK / 2 - PART_CLEAR) & (z < HUB_H + T_LINK / 2 + PART_CLEAR) & (rr < HUB_R + PART_CLEAR)):
                    return ("hub-collide", h, g) if detail else None
        # hub vs hub: rims (3 levels) + axis points of each hub against every other hub's cylinder (+1 mm)
        hn = list(hub_of); Ax = np.array([ax[h] for h in hn]); R0 = np.array([hub[h] for h in hn])
        ring = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        E1 = unit(np.cross(Ax, np.where(np.abs(Ax[:, :1]) < 0.9, [[1.0, 0, 0]], [[0, 1.0, 0]]))); E2 = np.cross(Ax, E1)
        lev = np.array([0, HUB_H / 2, HUB_H])
        rim = (R0[:, None, None] + lev[None, :, None])[..., None] * Ax[:, None, None, :] + HUB_R * (np.cos(ring)[None, None, :, None] * E1[:, None, None, :] + np.sin(ring)[None, None, :, None] * E2[:, None, None, :])
        pts = np.concatenate([rim.reshape(len(hn), -1, 3), (R0[:, None] + np.linspace(0, HUB_H, 5)[None])[..., None] * Ax[:, None, :]], 1)    # (9, k, 3)
        z = np.einsum("akx,bx->abk", pts, Ax) - R0[None, :, None]
        rr = np.linalg.norm(pts[:, None] - np.einsum("abk,bx->abkx", z + R0[None, :, None], Ax), axis=-1)
        hit = ((z > -PART_CLEAR) & (z < HUB_H + PART_CLEAR) & (rr < HUB_R + PART_CLEAR)).any(-1); np.fill_diagonal(hit, False)
        if hit.any():
            a_, b_ = np.argwhere(hit)[0]; return ("hub-hub", hn[a_], hn[b_]) if detail else None
        # ---- metal samples
        face = []
        for nm in self.straps:
            u = under[nm]; m = np.ones(len(u), bool)
            for h, gs in hub_of.items():
                if grp(nm) in gs: m &= ~near_hub(u, h)
            face.append(u[m])
        extra = [top[nm] for nm in self.straps]
        for h in hub_of:
            P, e1, e2 = disk_dirs(ax[h][None], hub[h]); face.append(P[0])
            a = ax[h]; e1, e2 = e1[0], e2[0]
            th = np.linspace(0, 2 * np.pi, 32, endpoint=False); zz = np.arange(0, HUB_H + 0.01, 2.0)
            wall = (hub[h] + zz)[:, None, None] * a + HUB_R * (np.cos(th)[None, :, None] * e1 + np.sin(th)[None, :, None] * e2)
            extra.append(wall.reshape(-1, 3)); extra.append(disk_dirs(a[None], hub[h] + HUB_H)[0][0])
        return np.concatenate(face), np.concatenate(extra)


def quick(p, rig, maps, step=6.0):
    """stage-0 screen: kinematics (closure, cond(J), clip paths) + every part's fitted rigid radius vs the skin on a
    coarse grid (straps: centre line and both edges every ~6 mm; hubs: centre + rim), area-weighted in-band, contact
    (below the first exit or into the far side of a gap) and a coarse part-collision test between non-adjacent parts
    (strap centre lines closer than 9 mm across and 4 mm radially; hubs as 20 x 12.25 mm cylinders)"""
    p = dict(PARAMS, **p); K = kinematics(p, rig, n_sub=3); kin = K["kin"]; poses = np.nonzero(kin)[0]
    cl = rig.kind == "clip"; nul = dict(follow=0.0, reach=0.0, inband14=0.0, inband10=0.0, contact=0.0, gap=999.0)
    if len(poses) < 10: return nul
    U, W, V = K["U"][poses], K["W"][poses], K["V"][poses]; n = len(poses)
    def arc(A, Bv, rho=60.0):
        ang = np.arccos(np.clip(np.sum(A * Bv, -1), -1, 1)); L = float(ang.mean()) * rho; ns = max(3, int(L / step) + 1)
        s = np.linspace(0, 1, ns); a_ = ang[:, None]; sa = np.maximum(np.sin(a_), 1e-9)
        C = (np.sin((1 - s)[None] * a_) / sa)[..., None] * A[:, None] + (np.sin(s[None] * a_) / sa)[..., None] * Bv[:, None]
        N = unit(np.cross(A, Bv))[:, None]
        D = np.concatenate([C, unit(C * rho + 3.0 * N), unit(C * rho - 3.0 * N)], 1)
        return D, ns, L * 8.0
    def disc(Ax, rho=60.0):
        e1 = unit(np.cross(Ax, np.where(np.abs(Ax[:, :1]) < 0.9, [[1.0, 0, 0]], [[0, 1.0, 0]]))); e2 = np.cross(Ax, e1)
        th = np.linspace(0, 2 * np.pi, 6, endpoint=False)
        R = Ax[:, None] * rho + 8.0 * (np.cos(th)[None, :, None] * e1[:, None] + np.sin(th)[None, :, None] * e2[:, None])
        return np.concatenate([Ax[:, None], unit(R)], 1)
    q = p["q"]; agg = (lambda X: X.max(0)) if q >= 1 else (lambda X: np.quantile(X, q, axis=0))
    def fit(D, extra):
        R = maps.rm(poses, D); R = np.where(np.isfinite(R), R, 400.0); return agg(R) + p["clear"] + extra, R
    # hubs
    hubs = {}
    for nm, X in [(f"HB{i}", U[:, i]) for i in range(3)] + [(f"HW{i}", W[:, i]) for i in range(3)] + [(f"HV{i}", V[:, i]) for i in range(3)]:
        D = disc(X); f_, R = fit(D, 0.0); lvl = float(f_.max())
        hubs[nm] = dict(D=D, lvl=lvl, R=R, ax=X)
    lo = p["w_lower"] == "P"
    straps = {}
    for i in range(3):
        straps[f"P{i}"] = (U[:, i], W[:, i], p["lay_P"], hubs[f"HB{i}"]["lvl"] + STACK, hubs[f"HW{i}"]["lvl"] + (0 if lo else STACK))
        straps[f"D{i}"] = (W[:, i], V[:, i], p["lay_D"], hubs[f"HW{i}"]["lvl"] + (STACK if lo else 0), hubs[f"HV{i}"]["lvl"] + STACK)
    straps["BF0"] = (U[:, 0], U[:, 1], 0.0, hubs["HB0"]["lvl"], hubs["HB1"]["lvl"]); straps["BF1"] = (U[:, 1], U[:, 2], 0.0, hubs["HB1"]["lvl"], hubs["HB2"]["lvl"])
    straps["PF0"] = (V[:, 0], V[:, 1], 0.0, hubs["HV0"]["lvl"], hubs["HV1"]["lvl"]); straps["PF1"] = (V[:, 1], V[:, 2], 0.0, hubs["HV1"]["lvl"], hubs["HV2"]["lvl"])
    gaps, wts, bad = [], [], np.zeros(n, bool); cpts = {}
    for nm, h in hubs.items():
        g = h["lvl"] - h["R"]; gaps.append(g); wts.append(np.full(g.shape[1], 314.0 / g.shape[1]))
        bad |= (g < 0).any(1) | (h["lvl"] + HUB_H > maps.rm(poses, h["D"], ceil=True)).any(1)
    for nm, (A, Bv, lay, e0, e1) in straps.items():
        D, ns, area = arc(A, Bv); f_, R = fit(D, lay)
        s3 = np.tile(np.linspace(0, 1, ns), 3); L = area / 8.0
        f_ = np.maximum.reduce([f_, e0 - np.maximum(0, s3 * L - HUB_R - LAND), e1 - np.maximum(0, (1 - s3) * L - HUB_R - LAND)])
        g = f_[None] - R; gaps.append(g); wts.append(np.full(g.shape[1], area / g.shape[1]))
        bad |= (g < 0).any(1) | (f_[None] + T_LINK > maps.rm(poses, D, ceil=True)).any(1)
        cpts[nm] = (D[:, :ns] * f_[None, :ns, None], f_[:ns])
    # coarse collisions between non-adjacent parts (per pose, vectorised)
    grp = lambda nm: nm[:2] if nm[:2] in ("BF", "PF") else nm
    adj = {frozenset(x) for x in [("BF", "P0"), ("BF", "P1"), ("BF", "P2"), ("P0", "D0"), ("P1", "D1"), ("P2", "D2"), ("D0", "PF"), ("D1", "PF"), ("D2", "PF")]}
    names = list(cpts); coll = np.zeros(n, bool)
    for ia in range(len(names)):
        for ib in range(ia + 1, len(names)):
            ga, gb = grp(names[ia]), grp(names[ib])
            if ga == gb or frozenset((ga, gb)) in adj: continue
            Pa, ra = cpts[names[ia]]; Pb, rb = cpts[names[ib]]
            ua = Pa / ra[None, :, None]; ub = Pb / rb[None, :, None]
            ang = np.arccos(np.clip(np.einsum("nax,nbx->nab", ua, ub), -1, 1)); rm_ = 0.5 * (ra[:, None] + rb[None, :])
            dl = ang * rm_[None]; dr = np.abs(ra[:, None] - rb[None, :])[None]
            coll |= ((dl < 2 * HW + PART_CLEAR) & (dr < T_LINK + PART_CLEAR)).any((1, 2))
    hub_parts = {f"HB{i}": ("BF", f"P{i}") for i in range(3)} | {f"HW{i}": (f"P{i}", f"D{i}") for i in range(3)} | {f"HV{i}": (f"D{i}", "PF") for i in range(3)}
    for h, (g1, g2) in hub_parts.items():
        ax_ = hubs[h]["ax"]; lv = hubs[h]["lvl"]
        for nm, (P, r) in cpts.items():
            if grp(nm) in (g1, g2): continue
            ang = np.arccos(np.clip(np.einsum("nx,nax->na", ax_, P / r[None, :, None]), -1, 1)); dl = ang * lv
            inz = (r > lv - T_LINK - PART_CLEAR) & (r < lv + HUB_H + PART_CLEAR)
            coll |= ((dl < HUB_R + HW + PART_CLEAR) & inz[None]).any(1)
    hn = list(hubs)
    for ia in range(len(hn)):
        for ib in range(ia + 1, len(hn)):
            if set(hub_parts[hn[ia]]) & set(hub_parts[hn[ib]]): continue
            ang = np.arccos(np.clip(np.sum(hubs[hn[ia]]["ax"] * hubs[hn[ib]]["ax"], -1), -1, 1)); lv = 0.5 * (hubs[hn[ia]]["lvl"] + hubs[hn[ib]]["lvl"])
            if abs(hubs[hn[ia]]["lvl"] - hubs[hn[ib]]["lvl"]) < HUB_H + PART_CLEAR: coll |= ang * lv < 2 * HUB_R + PART_CLEAR
    G = np.concatenate(gaps, 1); Wt = np.concatenate(wts)
    okp = ~bad & ~coll; taken_cl = cl[poses] & okp
    g = G[taken_cl]
    if len(g):
        w = np.broadcast_to(Wt, g.shape); ib14 = float((w * ((g >= 2) & (g <= 14))).sum() / w.sum()); ib10 = float((w * ((g >= 2) & (g <= 10))).sum() / w.sum())
    else: ib14 = ib10 = 0.0
    tk = np.zeros(len(kin), bool); tk[poses[okp]] = True
    follow, reach = float(tk[cl].mean()), float(tk[~cl].mean()); contact = float((bad & ~coll).sum() / max(1, (~coll).sum()))
    return dict(follow=round(follow, 4), reach=round(reach, 4), inband14=round(ib14, 4), inband10=round(ib10, 4), contact=round(contact, 4),
                coll=round(float(coll.mean()), 4), gap=CB.gap_of(ib14, follow, reach, contact))


class ProxyBench:
    """the bench's bookkeeping with a cheap distance: the radial gap to the first skin exit (screening only)"""
    record = CB.Bench.record; report = CB.Bench.report
    def __init__(self, B, maps):
        self.B, self.maps, self.kind, self.poses, self.mode = B, maps, B.kind, B.poses, "proxy"; self.reset()
    def reset(self): self.res = [None] * len(self.kind)
    def dist(self, i, P):
        P = np.asarray(P, float); r = np.linalg.norm(P, axis=1); D = P / r[:, None]
        return np.minimum(r - self.maps.r(i, D), self.maps.ceil(i, D) - r)


def evaluate(p, B, rig=None, maps=None, verbose=False):
    """runs one configuration on the bench; returns the report + diagnostics"""
    t0 = time.time(); B.reset()
    M = Model(p, B, rig, maps)
    why = dict(kin_fail=int((~M.K["kin"]).sum()), reach_fail=int((~M.K["reach_ok"]).sum()), path_fail=int((~M.K["path_ok"]).sum()), collide=0, extra_contact=0)
    if not M.ok:
        r = B.report(); r.update(why=why, secs=round(time.time() - t0, 1)); return r, M
    for i in range(len(B.poses)):
        out = M.metal(i)
        if out is None:
            if M.kin[i]: why["collide"] += 1
            B.record(i, None); continue
        face, extra = out
        de = B.dist(i, extra)
        if de.min() < 0:
            why["extra_contact"] += 1; face = np.concatenate([face, extra[np.argmin(de)][None]])
        B.record(i, face)
    r = B.report(); r.update(why=why, secs=round(time.time() - t0, 1), hubs={k: round(v, 1) for k, v in M.hub.items()})
    return r, M


def diagnose(M):
    """histogram of why kinematically-taken poses fail (collision pairs)"""
    from collections import Counter
    c = Counter()
    for i in range(len(M.B.poses)):
        if M.kin[i]:
            r = M.metal(i, detail=True)
            if isinstance(r, tuple) and isinstance(r[0], str): c[(r[0],) + tuple(sorted(r[1:]))] += 1
    return c


def jsonable(p):
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in p.items()}


def detuple(p):
    return {k: (tuple(v) if isinstance(v, list) else v) for k, v in p.items()}


def rand_params(rng):
    p = {}
    for key, rg in SWEEP.items():
        if isinstance(rg, list) or len(rg) != 2 or isinstance(rg[0], str): p[key] = rg[rng.integers(len(rg))]
        else: p[key] = float(rng.uniform(*rg))
    return p


def perturb(p, rng, scale=0.12):
    """a neighbour of p: continuous parameters moved by scale x their range, a discrete one flipped now and then"""
    q = dict(p)
    for key, rg in SWEEP.items():
        if isinstance(rg, list) or len(rg) != 2 or isinstance(rg[0], str):
            if rng.random() < 0.08: q[key] = rg[rng.integers(len(rg))]
        else:
            lo, hi = rg; q[key] = float(np.clip(p[key] + rng.normal(0, scale * (hi - lo)), lo, hi))
    return q


def gap_of(r):
    return CB.gap_of(r["inband14"], r["follow"], r["reach"], r["contact"])


def sweep(n0=4000, n1=80, n2=40, n_ref=60, seed=1, n_clip=60, n_ws=160):
    """stage 0: n0 random configurations on the quick screen (kinematics + centre-line in-band, no collisions);
    stage 1: the best n1 on the full model with the cheap radial-gap distance (collisions, every surface);
    stage 2: the best n2 on the bench (B.dist), then n_ref neighbours of the running best on the bench."""
    B = CB.Bench(n_clip=n_clip, n_ws=n_ws); rig = Rig(B); maps = SkinMaps(B); PB = ProxyBench(B, maps)
    print("bench", B.mode, len(B.poses), flush=True)
    cdir = os.path.join(REPO, ".cache", "concept_models", ID); os.makedirs(cdir, exist_ok=True)
    f0 = os.path.join(cdir, f"stage0v2_{B.key}_{seed}_{n0}.json")
    if os.path.exists(f0): S0 = json.load(open(f0))
    else:
        rng = np.random.default_rng(seed); S0 = []; t = time.time()
        for n in range(n0):
            pp = rand_params(rng); r = quick(pp, rig, maps); S0.append(dict(r=r, p=jsonable(pp)))
            if n % 500 == 0: print(f"  stage0 {n}/{n0} {time.time() - t:.0f} s best {min(x['r']['gap'] for x in S0)}", flush=True)
        S0.sort(key=lambda x: x["r"]["gap"]); json.dump(S0[:1000], open(f0, "w"))
    print("stage0 best", S0[0], flush=True)
    f1 = os.path.join(cdir, f"stage1v2_{B.key}_{seed}_{n0}_{n1}.json")
    S1 = json.load(open(f1)) if os.path.exists(f1) else []
    t = time.time()
    for x in S0[len(S1):n1]:
        r, M = evaluate(detuple(x["p"]), PB, rig, maps); r.pop("hubs", None)
        S1.append(dict(r=r, p=x["p"], r0=x["r"])); json.dump(S1, open(f1, "w"))
        print(f"  stage1 {len(S1)}/{n1} {time.time() - t:.0f} s gap {r['gap']} (quick {x['r']['gap']}) why {r['why']}", flush=True)
    S1.sort(key=lambda x: x["r"]["gap"])
    for _ in range(150):                                          # the bench numbers come from the fast cache when it exists
        B = CB.Bench(n_clip=n_clip, n_ws=n_ws)
        if B.mode == "fast" or os.environ.get("CB_EXACT") == "1": break
        print("  waiting for the fast bench cache", flush=True); time.sleep(30)
    print("bench", B.mode, flush=True)
    out = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
    SW = json.load(open(out)) if os.path.exists(out) else []
    done = {json.dumps(e["params"], sort_keys=True) for e in SW}
    def bench(pp, stage):
        key = json.dumps(jsonable(pp), sort_keys=True)
        if key in done: return None
        r, M = evaluate(detuple(pp), B, rig, maps)
        e = dict(k=len(SW), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=jsonable(pp), inband14=r["inband14"], inband10=r["inband10"],
                 reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], stage=stage, mode=r["mode"], why=r["why"])
        SW.append(e); done.add(key); json.dump(SW, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"  bench {e['k']} [{stage}] gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} ib10 {e['inband10']} contact {e['contact']} why {r['why']} {r['secs']} s", flush=True)
        return e
    for x in S1[:n2]: bench(x["p"], "screen")
    rng = np.random.default_rng(seed + 100)
    for n in range(n_ref):
        best = min(SW, key=lambda e: e["gap"])
        bench(perturb(detuple(best["params"]), rng, 0.12 if n < n_ref // 2 else 0.05), "refine")
    best = min(SW, key=lambda e: e["gap"]); print("BEST", best, flush=True)
    return SW, best


def sketch(pp, path, B=None):
    """matplotlib sketch: the skin under the shoulder (first-exit radius from GH, Lambert equal-area map centred on the
    lateral direction, anterior to the right) with the mechanism's parts at rest and overhead"""
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    B = B or CB.Bench(n_clip=60, n_ws=160); rig = Rig(B); maps = SkinMaps(B, verbose=False)
    M = Model(detuple(pp), B, rig, maps)
    cl = [j for j, k in enumerate(B.kind) if k == "clip"]
    rest = min(cl, key=lambda j: B.poses[j]["elev"]); over = max([j for j in cl if B.clip[j] == "Raise overhead"], key=lambda j: B.poses[j]["elev"])
    def proj(D):
        D = unit(D); k = np.sqrt(2 / (1 + D[..., 2] + 1e-9)); return k * D[..., 0], k * D[..., 1]
    g = np.linspace(-1.8, 1.8, 260); X, Y = np.meshgrid(g, g); rr = X ** 2 + Y ** 2; m = rr < 3.99
    z = 1 - rr / 2; sn = np.sqrt(np.clip(1 - z ** 2, 0, 1)); nr = np.sqrt(rr) + 1e-12
    D = np.stack([X / nr * sn, Y / nr * sn, z], -1)
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
    col = dict(BF="#555555", PF="#c0392b", P="#1f77b4", D="#2ca02c")
    for ax, i in zip(axs, (rest, over)):
        R = np.full(X.shape, np.nan); R[m] = maps.r(i, D[m])
        im = ax.imshow(np.clip(R, 30, 150), origin="lower", extent=[g[0], g[-1], g[0], g[-1]], cmap="Greys_r", vmin=30, vmax=150)
        ax.contour(X, Y, np.where(np.isfinite(R), R, 999), levels=[50, 70, 100], colors=["#f5b041"], linewidths=0.6)
        if M.ok and M.kin[i]:
            out = M.metal(i, detail=True)
            for nm, st in M.straps.items():
                P = st["D"][i] * st["rho"][:, None]; x, y = proj(P)
                ax.plot(x, y, ".", ms=1.5, color=col["BF" if nm.startswith("BF") else "PF" if nm.startswith("PF") else nm[0]])
            for h, a in M.hub_axes(i).items():
                x, y = proj(a); ax.plot(x, y, "o", ms=9, mfc="none", mec="#f39c12", mew=1.5); ax.text(x + 0.04, y + 0.04, h, color="#f39c12", fontsize=7)
            Pf, _ = out if isinstance(out[0], np.ndarray) else (None, None)
            if Pf is not None:
                d = B.dist(i, Pf); ax.set_xlabel(f"metal 2-14 mm: {np.mean((d >= 2) & (d <= 14)):.0%}, 2-10 mm: {np.mean((d >= 2) & (d <= 10)):.0%}, min {d.min():.1f} mm")
            else: ax.set_xlabel(f"not taken: {out}")
        else: ax.set_xlabel("pose not reachable (closure / singularity / path)")
        h = B.frames(i)["H"][0] @ rig.a_loc; x, y = proj(h); ax.plot(x, y, "r*", ms=12)
        ax.set_title(f"{B.clip[i]} - elevation {B.poses[i]['elev']:.0f}, plane {B.poses[i]['plane']:.0f}, axial {B.poses[i]['axial']:.0f}", fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(im, ax=axs, shrink=0.7, label="skin radius from GH along the ray (mm)")
    fig.suptitle("seed-spm-3rrr best: view from lateral (centre), up = up, anterior = right; grey = base frame, blue = proximal, green = distal, red = platform + arm end, star = humerus axis", fontsize=8)
    fig.savefig(path, dpi=90, bbox_inches="tight"); plt.close(fig)


# ------------------------------------------------------------------------------------------------ staged sweep (v2)
def kscore(p, rig, maps):
    """kinematic + accessibility screen: share of clip / workspace poses where every leg closes with cond(J) <= 50 on a
    continuous path AND every one of the 9 hub axes points at skin that is within 140 mm of GH with >= 25 mm free above
    it (an axis pointing into the trunk or the arm-trunk gap cannot carry a hub)"""
    p = dict(PARAMS, **p); K = kinematics(p, rig, n_sub=3); kin = K["kin"]; n = len(kin); I = np.arange(n)
    acc = np.ones(n, bool)
    for key in "UWV":
        D = K[key]                                                        # (n, 3, 3)
        r = maps.rm(I, D); c = maps.rm(I, D, ceil=True)
        with np.errstate(invalid="ignore"): acc &= (np.isfinite(r) & (r < 140) & ~(c - r < 25)).all(1)
    ok = kin & acc; cl = rig.kind == "clip"
    return 0.5 * float(ok[cl].mean()) + 0.5 * float(ok[~cl].mean())


def sweep2(nA=500, n_start=6, n_hill=50, n_bench=18, n_ref=40, seed=3, n_clip=60, n_ws=160, budget_s=None):
    """A: random kinematic/accessibility screen; B: hill-climb on the quick screen from the best A configurations;
    C: the best distinct B configurations on the bench, then neighbours of the running best on the bench. Every bench
    evaluation is appended to sweeps/<id>.json as it finishes; each new best gap is logged to events.jsonl."""
    T0 = time.time()
    B = CB.Bench(n_clip=n_clip, n_ws=n_ws); rig = Rig(B); maps = SkinMaps(B, verbose=False)
    print("bench", B.mode, len(B.poses), flush=True)
    rng = np.random.default_rng(seed); A = []
    for n in range(nA):
        pp = rand_params(rng); A.append((kscore(pp, rig, maps), pp))
    A.sort(key=lambda x: -x[0]); print(f"A: {nA} in {time.time() - T0:.0f} s, best kin/acc {[round(a[0], 3) for a in A[:n_start]]}", flush=True)
    pool = []
    for k0, p0 in A[:n_start]:
        best = None
        for q in (0.9, 0.95, 1.0):
            pp = dict(p0, q=q); r = quick(pp, rig, maps); pool.append((r["gap"], pp, r))
            if best is None or r["gap"] < best[0]: best = (r["gap"], pp, r)
        for h in range(n_hill):
            pp = perturb(best[1], rng, 0.10 if h < n_hill // 2 else 0.04); r = quick(pp, rig, maps); pool.append((r["gap"], pp, r))
            if r["gap"] < best[0]: best = (r["gap"], pp, r)
        print(f"B: start kin {k0:.3f} -> quick {best[0]} {best[2]} ({time.time() - T0:.0f} s)", flush=True)
    pool.sort(key=lambda x: x[0])
    out = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
    SW = json.load(open(out)) if os.path.exists(out) else []
    ev = os.path.join(REPO, "docs", "concepts", "events.jsonl")
    state = dict(best=min([e["gap"] for e in SW], default=1e9))
    def bench(pp, stage):
        r, M = evaluate(pp, B, rig, maps)
        e = dict(k=len(SW), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=jsonable(pp), inband14=r["inband14"], inband10=r["inband10"],
                 reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], stage=stage, mode=r["mode"], why=r["why"])
        SW.append(e); json.dump(SW, open(out + ".tmp", "w"), indent=0); os.replace(out + ".tmp", out)
        print(f"  bench {e['k']} [{stage}] gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} ib10 {e['inband10']} contact {e['contact']} why {r['why']} {r['secs']} s", flush=True)
        if e["gap"] < state["best"]:
            state["best"] = e["gap"]
            with open(ev, "a") as f:
                f.write(json.dumps(dict(time=e["t"], kind="milestone", event=f"seed-spm-3rrr new best gap {e['gap']} (reach {e['reach']}, follow {e['follow']}, inband14 {e['inband14']}, inband10 {e['inband10']}, contact {e['contact']}; config {e['k']}, {stage})")) + "\n")
        return e
    seen = []
    for g, pp, r in pool:
        if len([x for x in seen]) >= n_bench: break
        if any(all(abs(pp[k] - s_[k]) < 1e-9 for k in ("b_th", "b_ph", "a1", "a2", "p_cone")) for s_ in seen): continue
        seen.append(pp); bench(pp, "screen")
    for n in range(n_ref):
        if budget_s and time.time() - T0 > budget_s: break
        best = min(SW, key=lambda e: e["gap"])
        bench(perturb(detuple(best["params"]), rng, 0.08 if n < n_ref // 2 else 0.03), "refine")
    best = min(SW, key=lambda e: e["gap"]); print("BEST", best, flush=True)
    return SW, best, dict(nA=nA, n_quick=len(pool))


def redteam(pp, B=None):
    """the red team on one configuration: the named poses (rest, overhead, across the body, behind the back) and, over
    every bench pose, why poses are lost (leg closure, singularity, path, which parts collide) and where the metal pinches
    (the part and pose with the least skin distance, the parts inside the body)"""
    from collections import Counter
    B = B or CB.Bench(n_clip=60, n_ws=160); rig = Rig(B); maps = SkinMaps(B, verbose=False)
    M = Model(detuple(pp), B, rig, maps); K = M.K; out = dict(lines=[])
    def why(i):
        if not K["reach_ok"][i]:
            d = K["disc"][i]; 
            if (d <= 1e-6).any(): return f"leg {int(np.argmin(d))} cannot close (cones apart)"
            return f"singular: cond(J) {K['cond'][i]:.0f} > {COND_MAX:.0f}"
        if not K["path_ok"][i]: return "path from the previous clip frame crosses a singularity / opens a leg"
        r = M.metal(i, detail=True)
        if isinstance(r, tuple) and isinstance(r[0], str): return f"{r[0]} {r[1]}-{r[2]}"
        worst = (1e9, None)
        for nm, st in M.straps.items():
            d = B.dist(i, st["D"][i] * st["rho"][:, None]); 
            if d.min() < worst[0]: worst = (float(d.min()), nm)
        for h, a in M.hub_axes(i).items():
            P, _, _ = disk_dirs(a[None], M.hub[h]); d = B.dist(i, P[0])
            if d.min() < worst[0]: worst = (float(d.min()), h)
        return f"taken, closest metal {worst[0]:.1f} mm ({worst[1]})" if worst[0] >= 0 else f"CONTACT {worst[0]:.1f} mm ({worst[1]})"
    cl = [j for j, k in enumerate(B.kind) if k == "clip"]
    named = dict(rest=min(range(len(B.poses)), key=lambda j: B.poses[j]["elev"]),
                 overhead=max(cl, key=lambda j: B.poses[j]["elev"]),
                 overhead_ws=max([j for j, k in enumerate(B.kind) if k == "ws"], key=lambda j: B.poses[j]["elev"]),
                 across_body=max([j for j in cl if B.clip[j] == "Wash opposite shoulder"], key=lambda j: B.poses[j]["plane"]),
                 behind_back=min([j for j in cl if B.clip[j] == "Reach back pocket"], key=lambda j: B.poses[j]["plane"]))
    for nm, i in named.items():
        ps = B.poses[i]; out["lines"].append(f"{nm} ({B.clip[i]}, plane {ps['plane']:.0f} elev {ps['elev']:.0f} axial {ps['axial']:.0f}): {why(i)}")
    c = Counter(); worst = []
    for i in range(len(B.poses)):
        w = why(i); c["taken" if w.startswith("taken") else "contact" if w.startswith("CONTACT") else w.split(" (")[0].split(": cond")[0]] += 1
        if w.startswith("CONTACT") or w.startswith("taken"):
            v = float(w.split()[3 if w.startswith("taken") else 1]); worst.append((v, i, w))
    out["lines"].append("over all poses: " + "; ".join(f"{k}: {v}" for k, v in c.most_common(10)))
    worst.sort()
    for v, i, w in worst[:4]:
        ps = B.poses[i]; out["lines"].append(f"pinch: {B.clip[i]} plane {ps['plane']:.0f} elev {ps['elev']:.0f} axial {ps['axial']:.0f}: {w}")
    out["hubs"] = {k: round(v, 1) for k, v in M.hub.items()}
    out["straps"] = {nm: dict(len=round(st["len"]), rho=np.percentile(st["rho"], [0, 50, 100]).round(1).tolist()) for nm, st in M.straps.items()}
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "check":
        B = CB.Bench(n_clip=20, n_ws=40); print(B.mode)
        r, M = evaluate({}, B); print(r)
        print("collisions:", diagnose(M).most_common(8))
        for nm, st in M.straps.items(): print(nm, "len", round(st["len"]), "rho", np.percentile(st["rho"], [0, 50, 100]).round(1))
    elif a and a[0] == "sketch":
        SW = json.load(open(os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")))
        sketch(min(SW, key=lambda e: e["gap"])["params"], os.path.join(REPO, "docs", "concepts", "img", f"{ID}.png"))
    elif a and a[0] == "redteam":
        SW = json.load(open(os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")))
        o = redteam(min(SW, key=lambda e: e["gap"])["params"]); print("\n".join(o["lines"])); print(o["hubs"]); print(o["straps"])
    elif a and a[0] == "sweep2":
        kw = dict(nA=int(a[1])) if len(a) > 1 else {}
        sweep2(**kw, budget_s=float(a[2]) if len(a) > 2 else None)
    elif a and a[0] == "sweep":
        kw = dict(n0=int(a[1])) if len(a) > 1 else {}
        sweep(**kw)
