"""deltoid-strut-tripod: three arc struts on the paths of the three deltoid heads (spherical 3-RPR parallel), concept screen.

Topology (docs/concepts/catalogue.json, id deltoid-strut-tripod). Three legs in parallel, scapula frame S -> humerus H,
every joint axis through the GH centre:
    S -> passive SWIVEL about the radial axis b_i (O20 v5 hub) -> GUIDE (30 x 22 mm, radial [R_i-3, R_i+7]) through which
    STRUT i slides (ACTIVE: a Ti arc 8 wide x 4 radial on the great circle through b_i and W_i, centre GH, constant
    radius R_i where it passes the guide; the slide = a rotation d_i about the strut-plane normal) -> passive HINGE
    about the radial axis W_i (O20 v5 hub) on a humerus-fixed Ti SADDLE (3 mm, covering the three hinges + 8 mm) -> H.
DOF: active d1, d2, d3 (d_i = angle(b_i, W_i)); passive: 3 swivels + 3 hinges, each set by closure (the strut's frame
is (W_i, n_i)), so no spare. 3 ACTIVE, 6 PASSIVE. Singular where the three plane normals n_i = b_i x W_i are coplanar.

Model (thorax mm, origin = GH; S / H frames from the bench's pose file, as tools/concept_baseline.py):
  * kinematics exact (closed form, residual 0): W_i = HG w_i, d_i = acos(b_i . W_i). A pose is kinematically valid iff
    |det J| >= det (J rows n_i, unit) and every d_i lies in the strut's range [d_lo_i, d_hi_i] = quantiles q_lo / 1-q_hi
    of d_i over the det-valid bench poses (the strut length is fixed by d_hi: strut from the hinge to
    d_hi + (15 + 2) mm / R past the guide centre -> at d_i the TAIL sticks out d_hi - d_i past the anchor).
  * parts at their real size: strut band 8 x 4; guide box 30 x 22 x 10 (spec); O20 v5 hubs (disc r 10, 12.25 from
    the lower member's skin face to the crown, upper member face 3.15 above it, docs/HARDWARE.md); saddle 3 mm (the v5
    lower plate; spec said 2) over the three hinges + 8 mm margin; BOTTOM stub 14 x 6 x 25 deg from the lateral hinge
    toward the elbow (the baseline's neck); BASE BRACKETS (spec improvement: the spec left the scapula side
    unconnected) = 8 x 3 straps joining the three anchors (the two shortest great-circle edges), S-fixed.
  * swivel stacking (spec was vague: "hub at b_i (envelope) + a guide box at R_i"): 'under' = the hub under the guide
    (bracket end = hub lower member at F_b = R_i - 3 - 0.15 - 12.25), 'over' = the guide hangs under the hub (guide
    top = hub lower member, bracket = upper member at R_i + 7.15, the cap above): the guide jaw then rides the skin.
  * strut ROOT (spec improvement, `root` = 1): the part of a strut that never enters the guide (psi < d_lo - 16 mm / R)
    need not be at constant radius: it follows its own fitted profile (it rides the hinge boss at F + 3.15 and must
    clear the saddle). root = 0: the whole strut at R_i, the hinge hub on a pedestal (spec).
  * radii (the baseline's rule): every rigid part's skin-face radius = the p-th percentile, over the kinematically
    valid bench poses, of the OUTERMOST skin crossing under that sample (exact ray-triangle cube map, ~0.8 deg cells,
    built here) + clear; a constant-radius part (strut guided section + its guide, all poses) takes the percentile of
    the per-pose maximum. Crossing struts are layered (`layer` mm radial offset) when their footprints overlap.
  * taken iff: kinematically valid; along each fit clip at its full 10 fps no joint (d_i, swivel and hinge angles)
    jumps > 30 deg between followed frames (a flip = not followed); no two non-adjacent parts within 1 mm (radial
    shells sampled at 2 mm, lateral tolerance 1.5 mm; adjacent = strut/own guide, guide/own swivel inside the swivel
    zone, strut/saddle inside its hinge disc); then the bench's contact rule on every metal sample.
  * scored metal (bench in-band): the skin-facing faces sampled on a 2 mm grid (1 point / 4 mm2), as the baseline:
    strut undersides, guide undersides, saddle, stub, brackets, hub lower faces where they face the skin ('under');
    faces covered by another part of the same joint (hinge boss over its seat, 'over' swivel cap over its guide) are
    not counted. Contact-only: strut / guide / hub tops and rims (one appended when inside).

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/deltoid-strut-tripod.py maps 60 160   # skin cube maps (cached)
    ... deltoid-strut-tripod.py check                                                             # Bench(20, 40), a few poses
    ... deltoid-strut-tripod.py sweep                                                             # Bench(60, 160) sweep
"""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402
BP = CB.BP

ID = "deltoid-strut-tripod"
NAME = "Deltoid-strut tripod: three arc struts on the paths of the three deltoid heads (spherical 3-RPR parallel)"
D2R = math.pi / 180
ST_W, ST_T = 8.0, 4.0                       # strut band: width, radial thickness (spec)
GL, GW, G_LO, G_HI = 30.0, 22.0, 3.0, 7.0   # guide box: along, across, below / above the strut's skin face (spec)
HUB_R, HUB_UP, HUB_TOP, RUN = 10.0, 3.15, 12.25, 0.15   # O20 v5: disc r, upper member face, crown, running gap
SAD_T, SAD_M = 3.0, 8.0                     # saddle plate (v5 lower plate), margin around the hinge hubs
BR_W, BR_T = 8.0, 3.0                       # base brackets between the anchors
STUB_W, STUB_T, STUB_DEG = 14.0, 6.0, 25.0  # BOTTOM stub toward the cuff
SP = 2.0                                    # sample spacing (1 point / 4 mm2)
GAP = 1.0                                   # mm between non-adjacent parts
LAT_TOL = 1.5                               # lateral tolerance of the shell collision test (2 mm grids)
FLIP = 30.0                                 # deg per 10 fps frame
G_SWEEP = math.hypot(GL / 2, GW / 2)        # radius swept by the guide about its swivel axis (18.6 mm)
Y_ARM = np.array([0.0, -1.0, 0.0])

PARAMS = dict(b1=(80.0, 300.0), b2=(40.0, 160.0), b3=(35.0, 275.0),       # S anchors (lat, lon): lon 0 lateral, 90 anterior
              w1=(75.0, 60.0), w2=(75.0, 0.0), w3=(75.0, -60.0),          # arm anchors (delta from the humerus axis, azimuth)
              det=0.1, q_lo=0.0, q_hi=0.0, p=100.0, clear=2.0, swivel="under", layer=5.0, root=0)
SWEEP = dict(b_top_lat=(60, 90), b_post=((20, 45), (250, 320)), b_ant=((35, 50), (140, 170)), w_delta=(60, 85), w_spread=(40, 70),
             pairing="permutations of (b, w)", det=(0.05, 0.15), q_lo=(0, 0.2), q_hi=(0, 0.2), p=(80, 100), swivel=("under", "over"),
             layer=(5, 8), root=(0, 1), clear=(2.0, 3.0))


def unit(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)


def dS(lat, lon):
    la, lo = lat * D2R, lon * D2R
    return np.array([math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)])


def wdir(d, az):
    d, a = d * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def perp(u):
    a = np.array([1.0, 0.0, 0.0]) if abs(u[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    e1 = unit(a - (a @ u) * u); return e1, np.cross(u, e1)


def wrapd(x):
    return (np.asarray(x) + 180.0) % 360.0 - 180.0


# ------------------------------------------------------------------------------------------------ skin cube maps
CM_N, CM_RMAX = 112, 270.0
_FACES = [(np.array(a, float), np.array(b, float), np.array(c, float)) for a, b, c in
          [((1, 0, 0), (0, 1, 0), (0, 0, 1)), ((-1, 0, 0), (0, 0, 1), (0, 1, 0)), ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
           ((0, -1, 0), (1, 0, 0), (0, 0, 1)), ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (0, 1, 0), (1, 0, 0))]]


def raymap_outer(V, F):
    """skin crossings along every cube-map direction from GH (2, 6, N, N) mm: [0] the FIRST exit, [1] the OUTERMOST
    crossing = the last hit of the ray within CM_RMAX if it is an exit (outward normal), else inf (the ray is still
    inside the body there). Exact ray-triangle
    hits via the gnomonic projection (the cube-map construction of docs/concepts/models/seed-spm-3rrr.py raymap(),
    which keeps the FIRST exit; a rigid part at constant radius needs the outermost one, as the baseline's sphere
    tracing)."""
    keep = (np.linalg.norm(V, axis=1) < CM_RMAX)[F].all(1); T = F[keep]
    A, Bv, C = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]; Nn = np.cross(Bv - A, C - A); h = np.sum(Nn * A, 1)
    out = np.full((2, 6, CM_N, CM_N), np.inf, np.float32)
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
        lin = ci * CM_N + cj; o = np.lexsort((t, lin)); lin, t, nd = lin[o], t[o], nd[o]
        last = np.r_[lin[1:] != lin[:-1], True]                   # last (outermost) hit per cell
        fl, tl, nl = lin[last], t[last], nd[last]
        out[1, f].flat[fl] = np.where(nl > 0, tl, np.inf)
        start = np.r_[True, lin[1:] != lin[:-1]]                  # first exit: exits - entries reaches 1 (GH inside)
        dl = np.where(nd > 0, 1, -1); cs = np.cumsum(dl); base = np.maximum.accumulate(np.where(start, np.arange(len(cs)), 0))
        net = cs - np.r_[0, cs][base]; first = (net == 1) & (dl > 0)
        fi = np.nonzero(first)[0]; f1 = lin[fi]; k1 = np.r_[True, f1[1:] != f1[:-1]]
        out[0, f].flat[f1[k1]] = t[fi[k1]]
    return out


def cm_lookup(M, D, I=None):
    """bilinear lookup of a cube map M (6, N, N) - or maps M (n, 6, N, N) at pose indices I (m,) - at unit directions
    D (m, 3); inf where any corner is inf (seed-spm-3rrr's lookup)"""
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
        with np.errstate(invalid="ignore"): val = c00 * (1 - u) * (1 - v) + c10 * u * (1 - v) + c01 * (1 - u) * v + c11 * u * v
        out[m] = np.where(np.isfinite(c00) & np.isfinite(c10) & np.isfinite(c01) & np.isfinite(c11), val, np.inf)
    return out


def map_path(key):
    return os.path.join(REPO, ".cache", "concept_models", ID, f"rmap2_{key}_{CM_N}.npy")


def build_maps(n_clip, n_ws):
    B = CB.Bench(n_clip, n_ws); path = map_path(B.key)
    if os.path.exists(path): print("exists", path); return path
    os.makedirs(os.path.dirname(path), exist_ok=True); t = time.time()
    M = np.empty((len(B.poses), 2, 6, CM_N, CM_N), np.float32); Fi = np.asarray(BP.F)
    for i in range(len(B.poses)):
        M[i] = raymap_outer(np.asarray(B._verts(i), float), Fi)
        if i % 20 == 0: print(f"  map {i}/{len(B.poses)} {time.time() - t:.0f} s", flush=True)
    np.save(path + ".tmp.npy", M); os.replace(path + ".tmp.npy", path); print("saved", path, round(time.time() - t)); return path




class SkinMaps:
    def __init__(self, B):
        path = map_path(B.key)
        if not os.path.exists(path): raise SystemExit(f"no skin maps for bench {B.key}: run '{ID}.py maps <n_clip> <n_ws>'")
        self.M = np.load(path, mmap_mode="r")

    def r(self, I, D, which=0):
        """poses I (n,), thorax unit directions D (n, m, 3) -> skin crossing radius (n, m): which 0 = first exit, 1 = outermost"""
        n, m = D.shape[:2]
        return cm_lookup(self.M[:, which], D.reshape(-1, 3), np.repeat(np.asarray(I), m)).reshape(n, m)


# ------------------------------------------------------------------------------------------------ kinematics
def kin(b, w, HG):
    """b (3, 3) S anchors, w (3, 3) arm anchors, HG (N, 3, 3) -> per pose: W (N, 3, 3) arm anchors in S, d (N, 3) rad,
    t (at W toward b), g (at b toward W), nrm (strut-plane normal, a(psi) = cos psi W + sin psi t), det J (rows
    n_i = unit(b_i x W_i)), sw / hg (N, 3) swivel / hinge angles deg"""
    W = np.einsum("nij,kj->nki", HG, w)
    c = np.clip((W * b[None]).sum(-1), -1, 1); d = np.arccos(c)
    t = unit(b[None] - c[..., None] * W); g = unit(W - c[..., None] * b[None]); nrm = np.cross(W, t)
    J = unit(np.cross(b[None], W)); det = np.linalg.det(J)
    tA = np.einsum("nji,nkj->nki", HG, t)
    sw = np.zeros(d.shape); hg = np.zeros(d.shape)
    for k in range(3):
        e1, e2 = perp(b[k]); sw[:, k] = np.arctan2(g[:, k] @ e2, g[:, k] @ e1)
        f1, f2 = perp(w[k]); hg[:, k] = np.arctan2(tA[:, k] @ f2, tA[:, k] @ f1)
    return dict(W=W, d=d, t=t, g=g, nrm=nrm, det=det, sw=sw / D2R, hg=hg / D2R)


# ------------------------------------------------------------------------------------------------ sampled shapes (unit dirs)
def arc_band(W, t, nrm, psi, c_mm, R):
    """band on the great circle a(psi) = cos psi W + sin psi t (W, t, nrm (..., 3)), psi (m,) rad, offsets c_mm across
    at radius R -> (..., m, nc, 3)"""
    A = np.cos(psi)[:, None] * W[..., None, :] + np.sin(psi)[:, None] * t[..., None, :]
    return unit(A[..., :, None, :] + (np.asarray(c_mm, float) / R)[:, None] * nrm[..., None, None, :])


def rect(u, a, R, L=GL, Wd=GW):
    """L x Wd rectangle centred on u (..., 3), long side along the unit tangent a (..., 3), on the sphere of radius R
    -> (..., ns, nc, 3)"""
    s = np.linspace(-L / 2, L / 2, int(round(L / SP)) + 1); c = np.linspace(-Wd / 2, Wd / 2, int(round(Wd / SP)) + 1)
    m = np.cross(u, a)
    return unit(u[..., None, None, :] + (s[:, None, None] * a[..., None, None, :] + c[None, :, None] * m[..., None, None, :]) / R)


def rect_rim(D):
    return np.concatenate([D[..., 0, :, :], D[..., -1, :, :], D[..., 1:-1, 0, :], D[..., 1:-1, -1, :]], axis=-2)


def disc(u, rr, R, step=SP):
    g = np.arange(-rr, rr + 1e-6, step); X, Y = np.meshgrid(g, g); k = X ** 2 + Y ** 2 <= rr ** 2 + 1e-9
    e1, e2 = perp(u)
    return unit(u[None] + (X[k][:, None] * e1 + Y[k][:, None] * e2) / R)


def ring(u, rr, R, step=SP):
    n = max(8, int(math.ceil(2 * math.pi * rr / step))); a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    e1, e2 = perp(u)
    return unit(u[None] + rr * (np.cos(a)[:, None] * e1 + np.sin(a)[:, None] * e2) / R)


def seg_dist(U, a, b):
    """angular distance (rad) of unit vectors U (m, 3) to the great-circle segment a -> b"""
    n = unit(np.cross(a, b)); ab = math.acos(np.clip(a @ b, -1, 1))
    pr = unit(U - (U @ n)[:, None] * n)
    t1 = np.arccos(np.clip(pr @ a, -1, 1)); t2 = np.arccos(np.clip(pr @ b, -1, 1))
    inside = np.abs(t1 + t2 - ab) < 1e-6
    dl = np.arcsin(np.clip(np.abs(U @ n), 0, 1))
    de = np.minimum(np.arccos(np.clip(U @ a, -1, 1)), np.arccos(np.clip(U @ b, -1, 1)))
    return np.where(inside, dl, de)


def saddle_dirs(w, R, rho_mm):
    """arm-frame unit directions within rho_mm of the arcs joining the hinge axes (sorted by azimuth), 2 mm grid at R"""
    az = np.arctan2(w[:, 0], w[:, 2]); o = np.argsort(az); dl = np.arccos(-w[:, 1])
    rho = rho_mm / R
    d0, d1 = dl.min() - rho - 0.02, dl.max() + rho + 0.02
    out = []
    for de in np.arange(d0, d1, SP / R):
        sd = max(math.sin(de), 0.05); a0, a1 = az.min() - (rho + 0.02) / sd, az.max() + (rho + 0.02) / sd
        A = np.arange(a0, a1, SP / (R * sd))
        out.append(np.stack([math.sin(de) * np.sin(A), np.full(len(A), -math.cos(de)), math.sin(de) * np.cos(A)], 1))
    U = np.concatenate(out)
    dist = np.min([seg_dist(U, w[o[k]], w[o[k + 1]]) for k in range(len(o) - 1)], axis=0)
    return U[dist <= rho]


def shells_hit(A, Bs, tol=LAT_TOL, gap=GAP):
    """A, Bs = (U (m, 3) unit dirs, lo (m,), hi (m,)): True if some samples overlap laterally (within tol mm at their
    radius) and radially (closer than gap)"""
    UA, loA, hiA = A; UB, loB, hiB = Bs
    if not len(UA) or not len(UB): return False
    cA, cB = unit(UA.mean(0)), unit(UB.mean(0))
    spA = np.arccos(np.clip(UA @ cA, -1, 1)).max(); spB = np.arccos(np.clip(UB @ cB, -1, 1)).max()
    rmin = max(20.0, min(loA.min(), loB.min()))
    if math.acos(np.clip(cA @ cB, -1, 1)) > spA + spB + tol / rmin: return False
    if loA.min() - hiB.max() >= gap or loB.min() - hiA.max() >= gap: return False
    M = cKDTree(UA).sparse_distance_matrix(cKDTree(UB), tol / rmin, output_type="coo_matrix")
    if not M.nnz: return False
    i, j, dd = M.row, M.col, M.data
    lat = dd * np.minimum(hiA[i], hiB[j])
    rad = np.maximum(loA[i] - hiB[j], loB[j] - hiA[i])
    return bool(np.any((lat < tol) & (rad < gap)))


def pct(x, q, axis=0):
    return np.percentile(x, q, axis=axis, method="higher")


C5 = np.linspace(-ST_W / 2, ST_W / 2, 5)                  # strut across offsets (2 mm)
C3 = np.array([-ST_W / 2, 0.0, ST_W / 2])                  # (fit)


# ------------------------------------------------------------------------------------------------ design
class Design:
    def __init__(self, p, B, HG, RS, maps, cs=None):
        self.p = p = dict(PARAMS, **p); self.B = B; self.HG = HG; self.RS = RS; self.maps = maps; self.n = len(HG)
        self.b = np.array([dS(*p[k]) for k in ("b1", "b2", "b3")]); self.w = np.array([wdir(*p[k]) for k in ("w1", "w2", "w3")])
        self.K = kin(self.b, self.w, HG); self.over = p["swivel"] == "over"; self.q = float(p["p"]); self.clear = float(p["clear"])
        self.R = np.full(3, 65.0); self.dead = ""
        self.ranges(); self.fit_arm()
        for _ in range(2):
            self.fit_struts()
            if self.dead: return
            self.ranges()
        self.fit_arm(); self.fit_struts()
        if self.dead: return
        self.layering(); self.fit_root(); self.fit_brackets()
        self.status = cs(self) if cs is not None else {}

    # ---- strut ranges / kinematic validity ---------------------------------------------------------------------
    def ranges(self):
        p = self.p; K = self.K; d = K["d"] / D2R
        self.okdet = np.abs(K["det"]) >= p["det"]
        if self.okdet.sum() < 5: self.dead = "det"; self.valid = self.okdet; self.dlo = self.dhi = np.zeros(3); return
        geo = (GL / 2 + HUB_R + GAP + 1) / self.R / D2R               # the guide may not reach the hinge hub
        self.dlo = np.maximum(np.quantile(d[self.okdet], p["q_lo"], axis=0), geo)
        self.dhi = np.maximum(np.quantile(d[self.okdet], 1 - p["q_hi"], axis=0), self.dlo + 1)
        self.valid = self.kin_ok(K)

    def kin_ok(self, K):
        d = K["d"] / D2R
        return (np.abs(K["det"]) >= self.p["det"]) & np.all((d >= self.dlo - 1e-9) & (d <= self.dhi + 1e-9), axis=1)

    def psi_ext(self, k, R=None):
        """root / guided boundary and strut end (rad) for strut k at radius R"""
        R = self.R[k] if R is None else R
        return self.dlo[k] * D2R - (GL / 2 + 1) / R, self.dhi[k] * D2R + (GL / 2 + 2) / R

    # ---- arm side: saddle + stub (humerus-fixed), fitted to the first skin exit ---------------------------------
    def fit_arm(self):
        I = np.nonzero(self.valid)[0]; RH = self.RS[I] @ self.HG[I]; Rs = 50.0
        for _ in range(2):
            U = saddle_dirs(self.w, Rs, HUB_R + SAD_M)
            rs = self.maps.r(I, np.einsum("nij,mj->nmi", RH, U))
            prof = pct(rs, self.q) + self.clear
            fin = np.isfinite(prof); Rs = float(np.median(prof[fin])) if fin.any() else 50.0
        self.F = np.zeros(3); self.seat = []
        for k in range(3):
            sel = np.arccos(np.clip(U @ self.w[k], -1, 1)) <= (HUB_R + 1) / Rs
            self.F[k] = prof[sel].max() if sel.any() else np.inf; prof[sel] = self.F[k]; self.seat.append(sel)
        self.sadU, self.sadR, self.Rs = U, prof, Rs
        self.sad_tree = cKDTree(U)
        az = np.arctan2(self.w[:, 0], self.w[:, 2]); kl = int(np.argmin(np.abs(az))); wl = self.w[kl]
        e = unit(Y_ARM - (Y_ARM @ wl) * wl); n = np.cross(wl, e)
        s0 = (HUB_R + SAD_M + 1) / Rs; s1 = max(STUB_DEG * D2R, s0 + 10 / Rs)
        Ust = arc_band(wl, e, n, np.arange(s0, s1 + 1e-9, SP / Rs), np.linspace(-STUB_W / 2, STUB_W / 2, 8), Rs).reshape(-1, 3)
        rs = self.maps.r(I, np.einsum("nij,mj->nmi", RH, Ust))
        self.stubU, self.stubR = Ust, pct(rs, self.q) + self.clear

    def arm_heights(self, k):
        """top of the arm body under each saddle sample, as seen by strut k: plate top, other hinges' crowns"""
        h = self.sadR + SAD_T
        for l in range(3):
            if l != k: h = np.where(self.seat[l], self.F[l] + HUB_TOP, h)
        return h

    def over_saddle(self, I, k, U, R):
        """per pose (n,) x samples: arm body top + GAP under strut-k samples U (n, m, 3) S frame, -inf where none"""
        UA = np.einsum("nji,nmj->nmi", self.HG[I], U)
        dd, jj = self.sad_tree.query(UA.reshape(-1, 3), distance_upper_bound=LAT_TOL / self.Rs)
        h = self.arm_heights(k); ok = np.isfinite(dd)
        out = np.full(len(dd), -np.inf); out[ok] = h[jj[ok]] + GAP
        hz = np.arccos(np.clip(np.einsum("nmi,ni->nm", U, self.K["W"][I, k]), -1, 1)) * R <= HUB_R + 1.5
        out = out.reshape(U.shape[:2]); out[hz] = -np.inf                   # the strut's own hinge zone
        return out

    # ---- struts: constant radius over the guided section + tail ------------------------------------------------
    def fit_struts(self):
        I = np.nonzero(self.valid)[0]; n = len(I); K = self.K
        if n < 5: self.dead = "range"; return
        for k in range(3):
            R = self.R[k]
            for _ in range(2):
                pg, pe = self.psi_ext(k, R)
                start = pg if self.p["root"] else 0.0
                psi = np.arange(start, pe + 1e-9, SP / R)
                U = arc_band(K["W"][I, k], K["t"][I, k], K["nrm"][I, k], psi, C3, R)             # (n, m, 3, 3)
                need = self.maps.r(I, np.einsum("nij,nmcj->nmci", self.RS[I], U).reshape(n, -1, 3)).max(1) + self.clear
                G = rect(np.broadcast_to(self.b[k], (n, 3)), K["g"][I, k], R - G_LO).reshape(n, -1, 3)
                need = np.maximum(need, self.maps.r(I, np.einsum("nij,nmj->nmi", self.RS[I], G)).max(1) + self.clear + G_LO)
                if not self.over:
                    Ud = disc(self.b[k], HUB_R, R - G_LO - HUB_TOP)
                    need = np.maximum(need, self.maps.r(I, np.einsum("nij,mj->nmi", self.RS[I], Ud)).max(1) + self.clear + G_LO + HUB_TOP)
                Uc = U[:, :, 1, :]
                need = np.maximum(need, self.over_saddle(I, k, Uc, R).max(1))
                if not self.p["root"]:
                    need = np.maximum(need, self.F[k] + HUB_UP)                # pedestal: at least the seat + the hinge gap
                R = float(pct(need, self.q))
                if not np.isfinite(R) or R > 200: self.dead = f"strut {k + 1} no radius"; self.R[k] = R; return
            self.R[k] = R

    def strut_dirs(self, I, k, psi, C=C5):
        K = self.K; return arc_band(K["W"][I, k], K["t"][I, k], K["nrm"][I, k], psi, C, self.R[k])

    def layering(self):
        I = np.nonzero(self.valid)[0]; o = np.argsort(self.R); self.layered = []
        for a_, b_ in itertools.combinations(range(3), 2):
            ka, kb = (o[a_], o[b_])
            Ua = self.strut_dirs(I, ka, np.arange(0, self.psi_ext(ka)[1], SP / self.R[ka]), C3)
            Ub = self.strut_dirs(I, kb, np.arange(0, self.psi_ext(kb)[1], SP / self.R[kb]), C3)
            hit = 0
            for j in range(len(I)):
                A = Ua[j].reshape(-1, 3); Bv = Ub[j].reshape(-1, 3)
                dd = cKDTree(A).query(Bv, distance_upper_bound=LAT_TOL / min(self.R))[0]
                hit += bool(np.isfinite(dd).any())
            if hit / max(len(I), 1) > (100 - self.q) / 100 + 1e-9:
                self.R[kb] = max(self.R[kb], self.R[ka] + self.p["layer"]); self.layered.append((int(ka), int(kb), hit))

    def fit_root(self):
        """the strut profile r (m, 5) per sample along psi; root = fitted, guided section = R_k"""
        I = np.nonzero(self.valid)[0]; n = len(I); self.psi = []; self.sr = []
        for k in range(3):
            R = self.R[k]; pg, pe = self.psi_ext(k); psi = np.arange(0, pe + 1e-9, SP / R)
            r = np.full((len(psi), len(C5)), R)
            if self.p["root"]:
                mr = psi < pg; hz = psi * R <= HUB_R + 1.5
                if mr.any():
                    U = self.strut_dirs(I, k, psi[mr])                                       # (n, m, 5, 3)
                    rs = self.maps.r(I, np.einsum("nij,nmcj->nmci", self.RS[I], U).reshape(n, -1, 3)).reshape(n, mr.sum(), len(C5))
                    prof = pct(rs, self.q) + self.clear
                    sad = np.stack([self.over_saddle(I, k, U[:, :, c, :], R) for c in range(len(C5))], -1)
                    prof = np.maximum(prof, pct(sad, self.q))
                    r[mr] = prof
                r[hz] = self.F[k] + HUB_UP
            self.psi.append(psi); self.sr.append(r)
        self.hinge_lvl = np.array([self.sr[k][0, 0] for k in range(3)])     # strut underside on its hinge boss

    def zone(self, k):
        """angular radius (rad) of anchor k's swivel zone: the guide's sweep + 3 mm, at the guide's skin face"""
        return (G_SWEEP + 3.0) / (self.R[k] - G_LO)

    # ---- base brackets (S-fixed): the two shortest anchor-anchor edges --------------------------------------------
    def fit_brackets(self):
        I = np.nonzero(self.valid)[0]; n = len(I); K = self.K
        ang = {(a, c): math.acos(np.clip(self.b[a] @ self.b[c], -1, 1)) for a, c in itertools.combinations(range(3), 2)}
        self.edges = sorted(ang, key=ang.get)[:2]; self.brU = []; self.brR = []; self.br_end = []
        for a, c in self.edges:
            Rb = float(np.mean(self.R[[a, c]]))
            for _ in range(2):
                ta = unit(self.b[c] - (self.b[a] @ self.b[c]) * self.b[a]); na = np.cross(self.b[a], ta)
                psi = np.arange(0, ang[(a, c)] + 1e-9, SP / Rb); psi[-1] = ang[(a, c)]
                U = arc_band(self.b[a], ta, na, psi, C5, Rb).reshape(-1, 3)
                rs = self.maps.r(I, np.einsum("nij,mj->nmi", self.RS[I], U))
                prof = pct(rs, self.q) + self.clear
                da = np.arccos(np.clip(U @ self.b[a], -1, 1)); dc = np.arccos(np.clip(U @ self.b[c], -1, 1))   # rad
                for kk, dk in ((a, da), (c, dc)):
                    if self.over:
                        prof = np.where(dk <= self.zone(kk), np.maximum(prof, self.R[kk] + G_HI + RUN), prof)
                    else:
                        prof = np.where(dk <= (HUB_R + 1) / (self.R[kk] - G_LO - HUB_TOP), self.R[kk] - G_LO - HUB_TOP, prof)
                if self.over:                                                          # stay above the own struts' passage
                    tree = cKDTree(U); need = np.full((n, len(U)), -np.inf)
                    for kk in (a, c):
                        psi_k = np.arange(0, self.psi_ext(kk)[1], SP / self.R[kk]); Us = self.strut_dirs(I, kk, psi_k, C3)
                        for j in range(n):
                            hits = tree.query_ball_point(Us[j].reshape(-1, 3), LAT_TOL / Rb)
                            idx = np.unique(np.concatenate([np.asarray(h, int) for h in hits])) if len(hits) else np.zeros(0, int)
                            if len(idx): need[j, idx] = np.maximum(need[j, idx], self.R[kk] + ST_T + GAP)
                    prof = np.maximum(prof, pct(need, self.q))
                fin = np.isfinite(prof); Rb = float(np.median(prof[fin])) if fin.any() else Rb
            self.brU.append(U); self.brR.append(prof)
            self.br_end.append((da * prof <= HUB_R) | (dc * prof <= HUB_R))

    # ---- one pose ----------------------------------------------------------------------------------------------
    def parts(self, i):
        """per body: list of shells (U S-frame, lo, hi); scored faces (thorax), contact-only points (thorax)"""
        K = self.K; HGi = self.HG[i]; face = []; other = []; bodies = {}
        Ua = self.sadU @ HGi.T; Ust = self.stubU @ HGi.T
        A = [(Ua, self.sadR, self.sadR + SAD_T), (Ust, self.stubR, self.stubR + STUB_T)]
        face += [Ua * self.sadR[:, None], Ust * self.stubR[:, None]]
        other += [Ust * (self.stubR + STUB_T)[:, None]]
        for k in range(3):
            if not self.p["root"] and self.R[k] - HUB_UP > self.F[k] + SAD_T:            # hinge pedestal
                Up = disc(self.w[k], HUB_R, self.F[k]) @ HGi.T; lo = np.full(len(Up), self.F[k]); hi = np.full(len(Up), self.R[k] - HUB_UP)
                A.append((Up, lo, hi)); Ur = ring(self.w[k], HUB_R, self.F[k]) @ HGi.T; other.append(Ur * ((self.F[k] + self.R[k]) / 2))
        bodies["A"] = A
        for k in range(3):
            U = arc_band(K["W"][i, k], K["t"][i, k], K["nrm"][i, k], self.psi[k], C5, self.R[k]); r = self.sr[k]
            hz = (self.psi[k] * self.R[k] <= HUB_R + 1.5)
            sc = np.broadcast_to(~hz[:, None], r.shape)
            face.append((U * r[..., None])[sc].reshape(-1, 3))
            other += [(U[:, [0, -1]] * (r[:, [0, -1]] + ST_T / 2)[..., None]).reshape(-1, 3), (U[-1] * (r[-1] + ST_T / 2)[:, None])]
            lv = self.hinge_lvl[k]; Ub = disc(self.w[k], HUB_R, lv) @ HGi.T
            boss = (Ub, np.full(len(Ub), lv), np.full(len(Ub), lv + HUB_TOP - HUB_UP))
            other.append(ring(self.w[k], HUB_R, lv) @ HGi.T * (lv + (HUB_TOP - HUB_UP) / 2)); other.append(Ub * (lv + HUB_TOP - HUB_UP))
            bodies[f"T{k}"] = [(U.reshape(-1, 3), r.reshape(-1), r.reshape(-1) + ST_T), boss]
            bodies[f"T{k}_free"] = [(U[~hz].reshape(-1, 3), r[~hz].reshape(-1), r[~hz].reshape(-1) + ST_T)]
            Rk = self.R[k]; G = rect(self.b[k], K["g"][i, k], Rk - G_LO); Gf = G.reshape(-1, 3)
            face.append(Gf * (Rk - G_LO)); other += [rect_rim(G) * (Rk + (G_HI - G_LO) / 2), Gf * (Rk + G_HI)]
            gb = [(Gf, np.full(len(Gf), Rk - G_LO), np.full(len(Gf), Rk + G_HI))]
            if not self.over:
                Fb = Rk - G_LO - HUB_TOP; Ud = disc(self.b[k], HUB_R, Fb)
                gb.append((Ud, np.full(len(Ud), Fb + HUB_UP), np.full(len(Ud), Rk - G_LO)))
            bodies[f"G{k}"] = gb
        S = []
        for U, r, end in zip(self.brU, self.brR, self.br_end):
            S.append((U, r, r + BR_T)); face.append(U[~end] * r[~end, None])
        for k in range(3):
            Rk = self.R[k]
            if self.over:
                Ud = disc(self.b[k], HUB_R, Rk + G_HI + RUN); S.append((Ud, np.full(len(Ud), Rk + G_HI + RUN), np.full(len(Ud), Rk + ST_T + HUB_TOP)))
                other.append(Ud * (Rk + ST_T + HUB_TOP))
            else:
                Fb = Rk - G_LO - HUB_TOP; Ud = disc(self.b[k], HUB_R, Fb); S.append((Ud, np.full(len(Ud), Fb), np.full(len(Ud), Fb + SAD_T)))
                face.append(Ud * Fb); other.append(ring(self.b[k], HUB_R, Fb) * (Fb + HUB_TOP / 2))
        bodies["S"] = S
        RSi = self.RS[i]
        return bodies, np.concatenate(face) @ RSi.T, np.concatenate(other) @ RSi.T

    def collide(self, i, bodies):
        K = self.K
        def hit(LA, LB):
            return any(shells_hit(a, b) for a in LA for b in LB)
        for k in range(3):
            for l in range(k + 1, 3):
                if hit(bodies[f"T{k}"], bodies[f"T{l}"]): return f"strut{k + 1}/strut{l + 1}"
            for l in range(3):
                if l != k and hit(bodies[f"T{k}"], bodies[f"G{l}"]): return f"strut{k + 1}/guide{l + 1}"
            if hit(bodies[f"T{k}"], bodies["S"]): return f"strut{k + 1}/base"
            Wk = K["W"][i, k]
            Aex = [(U[keep], lo[keep], hi[keep]) for U, lo, hi in bodies["A"] for keep in [np.arccos(np.clip(U @ Wk, -1, 1)) * lo > HUB_R + 1.5]]
            if hit(bodies[f"T{k}_free"], Aex): return f"strut{k + 1}/saddle"
            for l in range(k + 1, 3):
                if hit(bodies[f"G{k}"], bodies[f"G{l}"]): return f"guide{k + 1}/guide{l + 1}"
            if hit(bodies[f"G{k}"], bodies["A"]): return f"guide{k + 1}/saddle"
            Sex = [(U[keep], lo[keep], hi[keep]) for U, lo, hi in bodies["S"] for keep in [np.arccos(np.clip(U @ self.b[k], -1, 1)) > self.zone(k) - 1e-9]]
            if hit(bodies[f"G{k}"], Sex): return f"guide{k + 1}/base"
        if hit(bodies["S"], bodies["A"]): return "base/saddle"
        return None

    def metal(self, i):
        if self.dead: return None, self.dead
        if not self.valid[i]:
            return None, "det" if not self.okdet[i] else "range"
        if self.B.kind[i] == "clip":
            ok, why = self.status.get(int(self.B.idx[i]), (False, "missing"))
            if not ok: return None, why
        if not (np.all(np.isfinite(self.sadR)) and np.all(np.isfinite(self.stubR)) and all(np.all(np.isfinite(r)) for r in self.sr)
                and all(np.all(np.isfinite(r)) for r in self.brR)):
            return None, "no radius"
        bodies, face, other = self.parts(i)
        w = self.collide(i, bodies)
        if w: return None, "interference " + w
        do = self.B.dist(i, other)
        if do.min() < 0: face = np.r_[face, other[np.argmin(do)][None]]
        return face, ""


# ------------------------------------------------------------------------------------------------ clip continuity
class ClipStatus:
    def __init__(self):
        Z = CB._poses_all(); self.names = list(Z["NAMES"]); self.cid = Z["CID"]; self.HG = Z["HG"].astype(float); self.FI = Z["FI"]

    def __call__(self, D):
        st = {}
        for nm in CB.FIT:
            ix = np.nonzero(self.cid == self.names.index(nm))[0]; ix = ix[np.argsort(self.FI[ix])]
            K = kin(D.b, D.w, self.HG[ix]); ok = D.kin_ok(K)
            q = np.concatenate([K["d"] / D2R, K["sw"], K["hg"]], 1); last = None
            for k, jj in enumerate(ix):
                if not ok[k]: st[int(jj)] = (False, "det" if abs(K["det"][k]) < D.p["det"] else "range"); continue
                if last is not None and np.abs(wrapd(q[k] - last)).max() > FLIP: st[int(jj)] = (False, "flip"); continue
                st[int(jj)] = (True, ""); last = q[k]
        return st


def run(p, B, HG, RS, maps, cs):
    t = time.time(); D = Design(p, B, HG, RS, maps, cs); B.reset(); why = {}
    for i in range(len(B.poses)):
        P, w = D.metal(i)
        if P is None: why[w] = why.get(w, 0) + 1; B.record(i, None)
        else:
            d = B.record(i, P)
            if d.min() < 0: why["contact"] = why.get("contact", 0) + 1
    r = B.report(); r["why"] = why; r["secs"] = round(time.time() - t, 1)
    tail = [round(float(D.dhi[k] - D.dlo[k]), 1) for k in range(3)] if not D.dead else None
    r["shape"] = dict(R=[round(float(x), 1) for x in D.R], dlo=[round(float(x), 1) for x in D.dlo], dhi=[round(float(x), 1) for x in D.dhi], tail_max_deg=tail,
                      F=[round(float(x), 1) for x in getattr(D, "F", np.zeros(3))], layered=getattr(D, "layered", None),
                      kin_valid=round(float(D.valid.mean()), 3), det_ok=round(float(D.okdet.mean()), 3), dead=D.dead)
    return r, D


SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")
_CTX = {}


def context(B):
    if B.key not in _CTX:
        Z = CB._poses_all(); _CTX.clear()
        _CTX[B.key] = (Z["HG"][B.idx].astype(float), Z["RS"][B.idx].astype(float), SkinMaps(B), ClipStatus())
    return _CTX[B.key]


def metal(pose, frames, params, _cache={}):
    """task API: metal samples (k, 3) for one bench pose, or None. params['_bench'] = the Bench."""
    B = params["_bench"]; prm = {k: v for k, v in params.items() if not k.startswith("_")}
    key = json.dumps(prm, sort_keys=True, default=list)
    if key not in _cache:
        HG, RS, maps, cs = context(B); _cache.clear(); _cache[key] = Design(prm, B, HG, RS, maps, cs)
    i = next(j for j, q in enumerate(B.poses) if q == pose)
    return _cache[key].metal(i)[0]


def sweep(configs, B, out=SWEEP_OUT, tag="", log=print):
    HG, RS, maps, cs = context(B)
    rows = json.load(open(out)) if os.path.exists(out) else []
    for p in configs:
        p = dict(PARAMS, **p)
        try: r, D = run(p, B, HG, RS, maps, cs)
        except Exception as e:
            import traceback; traceback.print_exc(); log(f"ERR {p} {e}"); continue
        row = dict(k=len(rows), t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), params=p, inband14=r["inband14"], inband10=r["inband10"],
                   reach=r["reach"], follow=r["follow"], contact=r["contact"], gap=r["gap"], why=r["why"], shape=r["shape"], mode=r["mode"], stage=tag)
        rows.append(row)
        if out:
            os.makedirs(os.path.dirname(out), exist_ok=True); json.dump(rows, open(out + ".tmp", "w"), indent=0, default=list); os.replace(out + ".tmp", out)
        log(f"[{row['k']}] gap {r['gap']:.1f} reach {r['reach']:.3f} follow {r['follow']:.3f} ib14 {r['inband14']:.3f} ib10 {r['inband10']:.3f} "
            f"contact {r['contact']:.3f} | {r['why']} | {r['shape']} | {r['secs']} s | {tag} | "
            + " ".join(f"{k}={p[k]}" for k in p if k not in ('w1', 'w2', 'w3', 'b1', 'b2', 'b3')) + f" b={p['b1']},{p['b2']},{p['b3']} w={p['w1']},{p['w2']},{p['w3']}")
    return rows


def random_cfg(rng, **fix):
    """a random configuration inside the morphology's stable-anchor regions (the S-frame skin map: top cap lat >= 60,
    posterior lat 20-45 / lon 250-320, anterior lat 35-60 / lon 80-150; the spec's anterior-medial lon 140-170 sits
    over the neck once the scapula rotates)"""
    top = (round(rng.uniform(60, 88), 1), round(rng.uniform(0, 360), 1)); post = (round(rng.uniform(20, 45), 1), round(rng.uniform(250, 320), 1))
    ant = (round(rng.uniform(35, 60), 1), round(rng.uniform(80, 150), 1))
    dl = round(rng.uniform(60, 88), 1); spr = round(rng.uniform(40, 70), 1); c0 = round(rng.uniform(-15, 15), 1)
    perm = list(rng.permutation(3)); bs = [ant, top, post]
    cfg = dict(b1=bs[perm[0]], b2=bs[perm[1]], b3=bs[perm[2]], w1=(dl, c0 + spr), w2=(dl, c0), w3=(dl, c0 - spr),
               q_lo=round(rng.uniform(0, 0.3), 2), q_hi=round(rng.uniform(0, 0.5), 2), p=float(rng.choice([85, 90, 95])),
               swivel="over", root=1, layer=5.0, det=0.1, clear=2.0)
    cfg.update(fix); return cfg


def screen(B, n, seed=0, log=print, **fix):
    """cheap pre-screen: build the design only (radii / ranges), no pose loop; returns [(cfg, alive, kin_valid, R)]"""
    HG, RS, maps, cs = context(B); rng = np.random.default_rng(seed); out = []
    for _ in range(n):
        c = random_cfg(rng, **fix)
        try: D = Design(c, B, HG, RS, maps, None)
        except Exception as e: log(f"ERR {e}"); continue
        out.append((c, not D.dead, float(D.valid.mean()), [round(float(x), 1) for x in D.R], D.dead))
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "maps":
        build_maps(int(a[1]), int(a[2])); sys.exit(0)
    if not a or a[0] == "check":
        B = CB.Bench(n_clip=20, n_ws=40)
        extra = json.loads(a[1]) if len(a) > 1 else {}
        sweep([dict(PARAMS, **extra)], B, out="", tag="check")
