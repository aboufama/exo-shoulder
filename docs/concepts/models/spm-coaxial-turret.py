"""spm-coaxial-turret: coaxial 3-RRR spherical parallel 'turret' (concept screen, idealised geometry).

Topology (docs/concepts/catalogue.json, id spm-coaxial-turret). Every joint axis passes through the GH centre:
  scapula S (on the user's handler) -> turret housing T (S-fixed, a thin annular cap on the posterior-top dome)
  carrying three NESTED thin-section ring bearings on ONE axis A (ring centre-line diameters ~O17 / O28 / O40)
  -> leg k: crank C_k (a 10 x 3 strap on the meridian of A, from its ring out to the elbow, arc a1 from A)
  -> elbow pin E_k (passive, P14: single MR126, disc r 7, crown 8 mm over the lower member's skin face)
  -> distal link D_k (12 x 3 strap on the great arc e_k -> v_k, arc a2: a two-force member)
  -> platform pin V_k (passive, P14, arm-fixed axis v_k) on one arm-fixed SADDLE (4 mm plate covering the three pins
     + 8 mm) -> neck toward the user's BOTTOM bar (the baseline's 25 deg arm-end strap).
DOF: 8 bodies (S, C1-3, D1-3, arm), 9 revolutes, spherical Gruebler 3(8-1-9)+9 = 3. ACTIVE = the three coaxial ring
angles (sensed in MVP1, cable-driven in MVP2, all on S). PASSIVE = 3 elbows + 3 platform pins, each set by closure:
given the arm pose, v_k is known and e_k is the intersection of the cone a1 about A with the cone a2 about v_k on the
design's branch, so nothing can sag. Cuff slides (outside the count) handle GH translation, as for the baseline.

Model (thorax mm, origin GH; S / humerus rotations RS, HG from the bench's pose file, as tools/concept_baseline.py):
  * kinematics: exact closed form (residual 0). A pose is kinematically taken iff every leg closes with >= 8 deg
    margin from its fold / stretch (type-1) singularity, the platform is >= 0.10 from the type-2 singularity
    (|det[n_0; n_1; n_2]|, n_k = unit(e_k x v_k)) WITH THE SAME SIGN as at rest (same assembly mode), the three elbows
    are >= 17 deg apart; along each fit clip the path from the previous frame (4 slerp sub-steps) keeps all of that
    (no branch / assembly flip, so the ring angles and passive angles are continuous).
  * parts at their real size; every rigid part's skin face is fitted in its own frame: the q-quantile, over the
    kinematically taken poses, of the skin radius under that sample (first skin exit from GH, exact ray-triangle cube
    map, ~0.8 deg cells - the seed-spm-3rrr maps) + `clear`; then the joint levels:
      - turret T: annulus from ring 1's inner edge to ring 3's outer edge (bearing housing), fitted underside, ring j
        seat level L_j = max(underside over ring j's 4 mm annulus) + 4.5 (thin-section ring height); the S-side
        handler mount is outside the count (as the baseline's base hub sits on the handler).
      - crank on ring j starts on its rotating race (underside = L_j) and must clear every outer ring and that ring's
        crank root: lvl_3 = L_3, lvl_2 = max(L_2, lvl_3 + LIFT), lvl_1 = max(L_1, lvl_2 + LIFT) (LIFT = 3 mm strap +
        1 mm clearance; the spec said +5), held to the turret edge + 2 mm, then a <= 45 deg ramp down to its profile.
      - elbow pins P14: flat disc r 7 at the max of the fitted profile under it; lower member (crank or distal,
        `el_low`) at that level, the upper member 3.15 above it (0.15 running gap), crown + 8.
      - saddle (humerus-fixed, 4 mm): fitted underside, flat under each platform pin; distal straps ride on top
        (+4.15 at their pin, >= saddle top + 1 mm over the rest of the saddle - the max over the taken poses).
      - each leg's distal / crank strap can be raised by whole layers (`lay_D`, `lay_C`, 4 mm each) to pass over
        other members; collisions are checked per pose anyway.
  * taken pose: kinematically taken, no two non-adjacent parts closer than 1 mm (radial intervals along matched
    directions: lateral centre distance < 3 mm on the 2 mm sample grid and radial intervals within 1 mm; adjacent
    parts share a joint and are exempt only inside that joint's footprint), then the bench's contact rule.
  * scored metal (bench in-band): skin-facing faces on a 2 mm grid at their real radius (1 point / 4 mm2), as the
    baseline: turret underside, crank / distal undersides (not where they lie over the turret, the saddle or their own
    pin disc: that face looks at the other part, not the skin), pin lower discs, saddle underside, neck. Contact-only
    (an inside point is appended so the pose counts as contact): strap tops, pin walls and crowns.

    OMP_NUM_THREADS=1 nice -n 5 python3 docs/concepts/models/spm-coaxial-turret.py kin        # kinematic screen
    ... spm-coaxial-turret.py check                                                         # Bench(20, 40), per member
    ... spm-coaxial-turret.py sweep                                                         # Bench(60, 160) sweep
"""
import itertools, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                 # noqa: E402
BP = CB.BP

ID = "spm-coaxial-turret"
NAME = "Coaxial 3-RRR spherical parallel 'turret': nested dome rings, force-only legs to one arm saddle"
D2R = math.pi / 180
SP = 2.0                                     # sample grid (mm): 1 point / 4 mm2
T_STRAP = 3.0                                # strap thickness (crank 10 wide, distal 12 wide)
W_C, W_D, W_N = 10.0, 12.0, 8.0              # crank, distal, neck widths
PIN_R, PIN_UP, PIN_TOP = 7.0, 3.15, 8.0      # P14 pin: disc r, upper member face over the lower one, crown
RING_W, RING_T = 4.0, 4.5                    # thin-section ring: radial section, height
LIFT = T_STRAP + 1.0                         # crank stacking per outer ring crossed (strap + 1 mm clearance)
SAD_T, SAD_M = 4.0, 8.0                      # saddle plate, margin around the platform pins
NECK_DEG = 25.0                              # arm end toward the cuff bar (the baseline's neck_deg)
CLR = 1.0                                    # part-to-part clearance
LAND, SLOPE = 2.0, 1.0                       # flat land after a joint, then a <= 45 deg ramp
MARGIN, DET_MIN, EL_SEP = 8.0, 0.10, 17.0    # leg singularity margin (deg), |det| type-2, elbow separation (deg)

PARAMS = dict(A_az=-40.0, A_el=40.0,         # turret axis A = bvec(az, el) in the scapula frame
              a1=60.0, a2=120.0,             # crank / distal arcs
              wc_d=60.0, wc_az=30.0,         # platform centre Wc = w_dir(delta, az) in the humerus frame
              gamma=20.0, psi=0.0,           # platform pins on a cone gamma about Wc, triangle twist psi
              br=(1, 1, 1),                  # elbow branch per leg
              ring_of=(0, 1, 2),             # leg k sits on ring ring_of[k] (0 = inner)
              ring_r=(8.5, 14.0, 20.0),      # ring centre-line radii (mm): O17 / O28 / O40
              el_low=("C", "C", "C"),        # lower member at each elbow
              lay_C=(0, 0, 0), lay_D=(0, 0, 0),
              clear=2.0, q=0.9)


def bvec(az, el):
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def w_dir(delta, az):
    d, a = delta * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(x):
    x = np.asarray(x, float); return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def rodr(ax, ang):
    ax = unit(ax); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


def circ_int(c1, r1, c2, r2, sign):
    """point on the unit sphere at angle r1 from c1 and r2 from c2 (rad), on side `sign` of c1 x c2"""
    dd = np.clip((c1 * c2).sum(-1), -1, 1); n = unit(np.cross(c1, c2))
    den = 1 - dd ** 2 + 1e-12; a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
    return p + np.asarray(sign, float)[..., None] * np.sqrt(np.clip(h2, 0, None))[..., None] * n, h2


# ------------------------------------------------------------------------------------------------ pose data
class Rig:
    """per-bench pose data (the evaluator's convention, as tools/concept_baseline.py): RS (scapula -> thorax),
    HG (humerus in the scapula frame), clip order and kinds"""
    def __init__(self, B):
        self.B = B; Z = CB._poses_all()
        self.HG = Z["HG"][B.idx].astype(float); self.RS = Z["RS"][B.idx].astype(float)
        self.kind = np.array(B.kind); self.n = len(B.idx)
        self.order = B.clip_order(); self.prev = {}
        for c, js in self.order.items():
            for a, b in zip(js[:-1], js[1:]): self.prev[b] = a
        self.rest = int(np.argmin([B.poses[j]["elev"] + (0 if B.kind[j] == "clip" else 1000) for j in range(self.n)]))


def slerp(R0, R1, ts):
    D = R0.T @ R1; ang = math.acos(np.clip((np.trace(D) - 1) / 2, -1, 1))
    if ang < 1e-9: return np.array([R0 for _ in ts])
    ax = np.array([D[2, 1] - D[1, 2], D[0, 2] - D[2, 0], D[1, 0] - D[0, 1]])
    if np.linalg.norm(ax) < 1e-9:
        w, v = np.linalg.eigh((D + np.eye(3)) / 2); ax = v[:, -1]
    return np.array([R0 @ rodr(ax, ang * t) for t in ts])


def platform(p):
    """the three platform pin axes v_k (3, 3) and the centre Wc in the humerus frame"""
    Wc = w_dir(p["wc_d"], p["wc_az"]); down = np.array([0.0, -1.0, 0.0])
    t = unit(np.cross(Wc, down)); v0 = rodr(t, p["gamma"] * D2R) @ Wc
    v0 = rodr(Wc, p["psi"] * D2R) @ v0
    return np.array([rodr(Wc, 2 * math.pi * k / 3) @ v0 for k in range(3)]), Wc


def legs(A, V, p):
    """A (3,), V (..., 3, 3) scapula frame -> elbows E (..., 3, 3), ok (...,), det (...,) (signed)"""
    a1, a2 = p["a1"] * D2R, p["a2"] * D2R
    Ab = np.broadcast_to(A, V.shape)
    E, h2 = circ_int(Ab, a1, V, a2, np.broadcast_to(np.asarray(p["br"], float), V.shape[:-1]))
    th = np.arccos(np.clip((Ab * V).sum(-1), -1, 1)); m = MARGIN * D2R
    ok = ((th >= abs(a1 - a2) + m) & (th <= min(a1 + a2, 2 * math.pi - a1 - a2) - m)).all(-1)
    n = unit(np.cross(E, V)); det = np.linalg.det(n)
    c = lambda i, j: (E[..., i, :] * E[..., j, :]).sum(-1)
    sep = math.cos(EL_SEP * D2R)
    ok &= (c(0, 1) <= sep) & (c(0, 2) <= sep) & (c(1, 2) <= sep)
    return E, ok, det


def kinematics(p, rig, n_sub=4):
    """per pose (scapula frame): elbows, platform axes, kinematic flags"""
    A = bvec(p["A_az"], p["A_el"]); V0, Wc = platform(p)
    V = np.einsum("nij,kj->nki", rig.HG, V0)
    E, ok, det = legs(A, V, p)
    s0 = np.sign(det[rig.rest]) if abs(det[rig.rest]) > 1e-9 else 1.0
    reach_ok = ok & (det * s0 >= DET_MIN)
    path_ok = np.ones(rig.n, bool)
    ts = np.linspace(0, 1, n_sub + 2)[1:-1]
    for j, i0 in rig.prev.items():
        if not (reach_ok[j] and reach_ok[i0]): continue
        Rs = slerp(rig.HG[i0], rig.HG[j], ts); Vs = np.einsum("nij,kj->nki", Rs, V0)
        _, oks, dets = legs(A, Vs, p)
        if not (oks & (dets * s0 >= DET_MIN)).all(): path_ok[j] = False
    phi = None
    return dict(A=A, V0=V0, Wc=Wc, V=V, E=E, det=det, s0=s0, kin=reach_ok & path_ok, reach_ok=reach_ok, path_ok=path_ok)


def kin_score(p, rig):
    K = kinematics(p, rig); cl = rig.kind == "clip"
    return float(K["kin"][cl].mean()), float(K["kin"][~cl].mean()), K


# ------------------------------------------------------------------------------------------------ skin ray map
# first skin exit from GH along each cube-map direction (exact ray-triangle hits, ~0.8 deg cells): the same maps as
# docs/concepts/models/seed-spm-3rrr.py (copied functions; the cached files are reused when present). Used only to FIT
# the rigid parts' skin faces; every score comes from the bench's own signed distance.
CM_N, CM_RMAX = 112, 270.0
_FACES = [(np.array(a, float), np.array(b, float), np.array(c, float)) for a, b, c in
          [((1, 0, 0), (0, 1, 0), (0, 0, 1)), ((-1, 0, 0), (0, 0, 1), (0, 1, 0)), ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
           ((0, -1, 0), (1, 0, 0), (0, 0, 1)), ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (0, 1, 0), (1, 0, 0))]]


def raymap(V, F):
    keep = (np.linalg.norm(V, axis=1) < CM_RMAX)[F].all(1); T = F[keep]
    A, Bv, C = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]; Nn = np.cross(Bv - A, C - A); h = np.sum(Nn * A, 1)
    out = np.full((6, CM_N, CM_N), -1.0); sgn = np.zeros((6, CM_N, CM_N))
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
        net = cs - np.r_[0, cs][base]
        first = (net == 1) & (dl > 0)
        fi = np.nonzero(first)[0]; fl = lin[fi]; keep1 = np.r_[True, fl[1:] != fl[:-1]]
        out[f].flat[fl[keep1]] = t[fi[keep1]]; sgn[f].flat[fl[keep1]] = 1.0
    return np.where((out > 0) & (sgn > 0), out, np.inf).astype(np.float32)


def cm_lookup(M, D, I=None):
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


class SkinMaps:
    def __init__(self, B, verbose=True):
        d = os.path.join(REPO, ".cache", "concept_models", ID); os.makedirs(d, exist_ok=True)
        path = os.path.join(d, f"raymap1_{B.key}_{CM_N}.npy")
        other = os.path.join(REPO, ".cache", "concept_models", "seed-spm-3rrr", f"raymap1_{B.key}_{CM_N}.npy")
        if not os.path.exists(path) and os.path.exists(other): path = other
        if os.path.exists(path): self.M = np.load(path, mmap_mode="r"); return
        t = time.time(); M = np.empty((len(B.poses), 6, CM_N, CM_N), np.float32); Fi = np.asarray(BP.F)
        for i in range(len(B.poses)):
            M[i] = raymap(np.asarray(B._verts(i), float), Fi)
            if verbose and i % 20 == 0: print(f"  raymap {i}/{len(B.poses)} {time.time() - t:.0f} s", flush=True)
        np.save(path + ".tmp.npy", M); os.replace(path + ".tmp.npy", path); self.M = np.load(path, mmap_mode="r")

    def rm(self, I, D):
        """poses I (n,), directions D (n, m, 3) -> first-exit radius (n, m); inf -> 400"""
        n, m = D.shape[:2]; R = cm_lookup(self.M, D.reshape(-1, 3), np.repeat(np.asarray(I), m)).reshape(n, m)
        return np.where(np.isfinite(R), R, 400.0)


# ------------------------------------------------------------------------------------------------ part templates
def grid_t(width):
    return np.arange(-width / 2 + SP / 2, width / 2 - 1e-9, SP)


def perp(a):
    a = unit(a); e1 = unit(np.cross(a, np.where(abs(a[..., :1]) < 0.9, [1.0, 0, 0], [0, 1.0, 0])))
    return e1, np.cross(a, e1)


def disc_xy(rad):
    g = np.arange(-rad + SP / 2, rad, SP); X, Y = np.meshgrid(g, g); m = X ** 2 + Y ** 2 <= rad ** 2
    return X[m], Y[m]


def seg_dist(P, a, b):
    """distance of 2-D points P (m, 2) to the segment a-b"""
    ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab + 1e-12), 0, 1); return np.linalg.norm(P - a - t[:, None] * ab, axis=1)


def tri_region(V2, P):
    """distance (mm) of plane points P (m, 2) to the filled triangle V2 (3, 2); 0 inside"""
    d = np.minimum.reduce([seg_dist(P, V2[i], V2[(i + 1) % 3]) for i in range(3)])
    s = [np.cross(V2[(i + 1) % 3] - V2[i], P - V2[i]) for i in range(3)]
    inside = ((s[0] >= 0) & (s[1] >= 0) & (s[2] >= 0)) | ((s[0] <= 0) & (s[1] <= 0) & (s[2] <= 0))
    return np.where(inside, 0.0, d)


def ramp_floor(level, dist, hold):
    """a joint level held over `hold` mm, then a <= 45 deg ramp down"""
    return level - np.maximum(0.0, dist - hold) * SLOPE


# ------------------------------------------------------------------------------------------------ the model
RUN = 0.15                                   # running gap between stacked members at a joint
BODIES = ["T", "C0", "C1", "C2", "D0", "D1", "D2", "H", "EP0", "EP1", "EP2", "PP0", "PP1", "PP2"]
BI = {b: i for i, b in enumerate(BODIES)}
EXEMPT = np.zeros((14, 14), bool)
for k in range(3):
    for a, b in ((("T", f"C{k}")), (f"C{k}", f"EP{k}"), (f"D{k}", f"EP{k}"), (f"D{k}", "H"), (f"D{k}", f"PP{k}"), ("H", f"PP{k}")):
        EXEMPT[BI[a], BI[b]] = EXEMPT[BI[b], BI[a]] = True
    for j in range(3): EXEMPT[BI[f"PP{k}"], BI[f"PP{j}"]] = True
np.fill_diagonal(EXEMPT, True)


class Model:
    """one configuration: kinematics + every rigid part fitted in its own frame; metal(i) -> (scored, extra, labels)"""
    def __init__(self, p, B, rig, maps, K=None):
        self.p = p = dict(PARAMS, **p); self.B, self.rig, self.maps = B, rig, maps
        self.K = K if K is not None else kinematics(p, rig)
        self.kin = self.K["kin"].copy(); self.valid = np.nonzero(self.kin)[0]
        self.ok = len(self.valid) >= 5
        self.RS = rig.RS; self.RH = np.einsum("nij,njk->nik", rig.RS, rig.HG)
        if self.ok: self.build()

    def agg(self, R):
        q = self.p["q"]; return R.max(0) if q >= 1 else np.quantile(R, q, axis=0)

    def fit(self, D):
        """D (n, m, 3) thorax directions for every pose -> fitted first-exit radius (m,) over the taken poses"""
        v = self.valid; return self.agg(self.maps.rm(v, D[v]))

    # ---- part geometry (directions per pose)
    def turret_dirs(self, rho):
        A = self.K["A"]; e1, e2 = perp(A); ro = self.p["ring_r"][2] + RING_W / 2; ri = self.p["ring_r"][0] - RING_W / 2
        g = np.arange(-ro + SP / 2, ro, SP); X, Y = np.meshgrid(g, g); r = np.hypot(X, Y); m = (r >= ri) & (r <= ro)
        x, y, r = X[m], Y[m], r[m]
        DS = unit(rho * A + x[:, None] * e1 + y[:, None] * e2)
        return np.einsum("nij,mj->nmi", self.RS, DS), r

    def crank_frame(self, k):
        A = self.K["A"]; E = self.K["E"][:, k]; u = unit(E - (E @ A)[:, None] * A); N = np.cross(A, u)
        return A, u, N

    def crank_dirs(self, k, rho, th0):
        A, u, N = self.crank_frame(k); a1 = self.p["a1"] * D2R
        ns = max(2, int(math.ceil((a1 - th0) * rho / SP))); s = th0 + (np.arange(ns) + 0.5) / ns * (a1 - th0)
        t = grid_t(W_C); S, T = np.meshgrid(s, t, indexing="ij"); S, T = S.ravel(), T.ravel()
        C = np.cos(S)[None, :, None] * A + np.sin(S)[None, :, None] * u[:, None, :]
        DS = unit(C * rho + T[None, :, None] * N[:, None, :])
        return np.einsum("nij,nmj->nmi", self.RS, DS), S, T

    def distal_dirs(self, k, rho):
        E = self.K["E"][:, k]; V = self.K["V"][:, k]; a2 = self.p["a2"] * D2R
        ns = max(2, int(math.ceil(a2 * rho / SP))); s = (np.arange(ns) + 0.5) / ns * a2
        t = grid_t(W_D); S, T = np.meshgrid(s, t, indexing="ij"); S, T = S.ravel(), T.ravel()
        N = unit(np.cross(E, V)); u = np.cross(N, E)                    # tangent at e toward v
        C = np.cos(S)[None, :, None] * E[:, None, :] + np.sin(S)[None, :, None] * u[:, None, :]
        DS = unit(C * rho + T[None, :, None] * N[:, None, :])
        return np.einsum("nij,nmj->nmi", self.RS, DS), S, T

    def epin_dirs(self, k, rho):
        A, u, N = self.crank_frame(k); E = self.K["E"][:, k]; a1 = self.p["a1"] * D2R
        f1 = -math.sin(a1) * A + math.cos(a1) * u; x, y = disc_xy(PIN_R)
        DS = unit(rho * E[:, None, :] + x[None, :, None] * f1[:, None, :] + y[None, :, None] * N[:, None, :])
        return np.einsum("nij,nmj->nmi", self.RS, DS)

    def saddle_plane(self, rho):
        Wc = self.K["Wc"]; down = np.array([0.0, -1.0, 0.0]); g1 = unit(down - (down @ Wc) * Wc); g2 = np.cross(Wc, g1)
        V0 = self.K["V0"]; V2 = rho * np.stack([V0 @ g1, V0 @ g2], 1) / (V0 @ Wc)[:, None]
        return Wc, g1, g2, V2

    def to_plane(self, DH, rho):
        Wc, g1, g2, _ = self.saddle_plane(rho); z = DH @ Wc
        with np.errstate(divide="ignore", invalid="ignore"):
            P = rho * np.stack([DH @ g1, DH @ g2], -1) / z[..., None]
        return np.where((z > 0.3)[..., None], P, 1e4)

    def saddle_dirs(self, rho):
        Wc, g1, g2, V2 = self.saddle_plane(rho)
        lo = V2.min(0) - SAD_M; hi = V2.max(0) + SAD_M
        gx = np.arange(lo[0] + SP / 2, hi[0], SP); gy = np.arange(lo[1] + SP / 2, hi[1], SP); X, Y = np.meshgrid(gx, gy)
        P = np.stack([X.ravel(), Y.ravel()], 1); P = P[tri_region(V2, P) <= SAD_M]
        DH = unit(rho * Wc + P[:, :1] * g1 + P[:, 1:] * g2)
        return np.einsum("nij,mj->nmi", self.RH, DH), P, DH

    def neck_dirs(self, rho_s, rho):
        Wc, g1, g2, V2 = self.saddle_plane(rho_s); a = NECK_DEG * D2R
        ns = max(2, int(math.ceil(a * rho / SP))); s = (np.arange(ns) + 0.5) / ns * a; t = grid_t(W_N)
        S, T = np.meshgrid(s, t, indexing="ij"); S, T = S.ravel(), T.ravel()
        DH = unit((np.cos(S)[:, None] * Wc + np.sin(S)[:, None] * g1) * rho + T[:, None] * g2)
        keep = tri_region(V2, self.to_plane(DH, rho_s)) > SAD_M
        DH = DH[keep]
        return np.einsum("nij,mj->nmi", self.RH, DH), DH

    # ---- fitting
    def build(self):
        p = self.p; cl = p["clear"]
        # turret
        rho = 60.0
        for _ in range(2):
            D, r = self.turret_dirs(rho); prof = self.fit(D) + cl; rho = float(np.mean(prof))
        self.T = dict(D=D, r=r, lo=prof, rho=rho)
        L = [float(np.max(prof[np.abs(r - rr) <= RING_W / 2])) + RING_T for rr in p["ring_r"]]
        lvl = [0.0, 0.0, 0.0]; lvl[2] = L[2]; lvl[1] = max(L[1], lvl[2] + LIFT); lvl[0] = max(L[0], lvl[1] + LIFT)
        ring_lvl = np.array([L[int(np.argmin(np.abs(np.array(p["ring_r"]) - x)))] for x in r])
        self.T["hi"] = np.maximum(prof + RING_T, ring_lvl); self.L, self.lvl = L, lvl
        th_out = math.atan((p["ring_r"][2] + RING_W / 2) / rho)
        # saddle
        rs = 60.0
        for _ in range(2):
            D, P2, DH = self.saddle_dirs(rs); prof = self.fit(D) + cl; rs = float(np.mean(prof))
        _, _, _, V2 = self.saddle_plane(rs); Sk = []
        for k in range(3):
            m = np.linalg.norm(P2 - V2[k], axis=1) <= PIN_R + SP / 2; Sk.append(float(prof[m].max()) if m.any() else float(prof.max())); prof[m] = Sk[-1]
        self.H = dict(D=D, P2=P2, DH=DH, lo=prof, hi=prof + SAD_T, rho=rs, V2=V2, tree=cKDTree(P2)); self.Sk = Sk
        # neck
        rn = rs
        for _ in range(2):
            D, DH = self.neck_dirs(rs, rn)
            if not D.shape[1]: break
            prof = self.fit(D) + cl; rn = float(np.mean(prof))
        self.N = dict(D=D, lo=prof if D.shape[1] else np.zeros(0))
        # elbow pins
        self.Ek = []; self.EP = []
        for k in range(3):
            rr = 60.0
            for _ in range(2):
                D = self.epin_dirs(k, rr); lev = float(self.fit(D).max()) + cl; rr = lev
            self.Ek.append(lev); self.EP.append(dict(D=D, lo=np.full(D.shape[1], lev), hi=np.full(D.shape[1], lev + PIN_TOP)))
        # cranks
        self.C = []
        for k in range(3):
            j = p["ring_of"][k]; th0 = math.atan(p["ring_r"][j] / self.T["rho"])
            low = p["el_low"][k] == "C"; el_lvl = self.Ek[k] + (0.0 if low else PIN_UP)
            rc = 0.5 * (lvl[j] + el_lvl)
            for _ in range(2):
                D, S, Tt = self.crank_dirs(k, rc, th0)
                prof = self.fit(D) + cl + 4.0 * p["lay_C"][k]
                fT = ramp_floor(lvl[j], np.maximum(0, S - th_out) * rc, LAND)
                fE = ramp_floor(el_lvl, (p["a1"] * D2R - S) * rc, PIN_R + LAND)
                lo = np.maximum.reduce([prof, fT, fE]); rc = float(np.mean(lo))
            over_T = S <= th_out; in_pin = np.hypot((p["a1"] * D2R - S) * rc, Tt) < PIN_R
            self.C.append(dict(D=D, S=S, T=Tt, lo=lo, hi=lo + T_STRAP, score=~(over_T | in_pin), rho=rc))
        # distal links
        self.Dl = []
        for k in range(3):
            low = p["el_low"][k] == "C"; el_lvl = self.Ek[k] + (PIN_UP if low else 0.0); pp_lvl = self.Sk[k] + SAD_T + RUN
            rd = 0.5 * (el_lvl + pp_lvl)
            for _ in range(2):
                D, S, Tt = self.distal_dirs(k, rd)
                prof = self.fit(D) + cl + 4.0 * p["lay_D"][k]
                a2 = p["a2"] * D2R
                fE = ramp_floor(el_lvl, S * rd, PIN_R + LAND)
                fV = ramp_floor(pp_lvl, (a2 - S) * rd, PIN_R + LAND)
                fS = self.saddle_floor(D, k, (a2 - S) * rd)
                lo = np.maximum.reduce([prof, fE, fV, fS]); rd = float(np.mean(lo))
            in_pins = (np.hypot(S * rd, Tt) < PIN_R) | (np.hypot((a2 - S) * rd, Tt) < PIN_R)
            self.Dl.append(dict(D=D, S=S, T=Tt, lo=lo, hi=lo + T_STRAP, score=~in_pins, rho=rd))

    def saddle_floor(self, D, k, dist_v):
        """floor of distal k's samples over the saddle (top + 1 mm) and over the other platform pins (crown + 1 mm),
        max over the taken poses; inside its own pin's hold zone the joint level rules"""
        v = self.valid; H = self.H
        DH = np.einsum("nji,nmj->nmi", self.RH[v], D[v]); P = self.to_plane(DH, H["rho"])           # (nv, m, 2)
        d = tri_region(H["V2"], P.reshape(-1, 2)).reshape(P.shape[:2])
        _, idx = H["tree"].query(P.reshape(-1, 2)); top = H["hi"][idx].reshape(P.shape[:2]) + CLR
        f = np.where(d <= SAD_M + 1.0, top, -np.inf)
        for j in range(3):
            if j == k: continue
            near = np.linalg.norm(P - H["V2"][j], axis=-1) < PIN_R + CLR + SP / 2
            f = np.where(near, np.maximum(f, self.Sk[j] + PIN_TOP + CLR), f)
        f = f.max(0); return np.where(dist_v < PIN_R + LAND, -np.inf, f)

    # ---- per pose
    def parts(self, i):
        """[(body, dirs (m,3) thorax, lo, hi, scored mask)] at pose i"""
        out = [("T", self.T["D"][i], self.T["lo"], self.T["hi"], np.ones(len(self.T["lo"]), bool))]
        for k in range(3):
            c = self.C[k]; out.append((f"C{k}", c["D"][i], c["lo"], c["hi"], c["score"]))
        for k in range(3):
            d = self.Dl[k]; DH = self.RH[i].T @ d["D"][i].T
            over = tri_region(self.H["V2"], self.to_plane(DH.T, self.H["rho"])) <= SAD_M
            out.append((f"D{k}", d["D"][i], d["lo"], d["hi"], d["score"] & ~over))
        H = self.H; lo = np.r_[H["lo"], self.N["lo"]]; Dh = np.concatenate([H["D"][i], self.N["D"][i]]) if len(self.N["lo"]) else H["D"][i]
        out.append(("H", Dh, lo, lo + SAD_T, np.ones(len(lo), bool)))
        for k in range(3):
            e = self.EP[k]; out.append((f"EP{k}", e["D"][i], e["lo"], e["hi"], np.ones(len(e["lo"]), bool)))
        for k in range(3):
            m = np.linalg.norm(H["P2"] - H["V2"][k], axis=1) <= PIN_R
            out.append((f"PP{k}", H["D"][i][m], np.full(m.sum(), self.Sk[k]), np.full(m.sum(), self.Sk[k] + PIN_TOP), np.zeros(m.sum(), bool)))
        return out

    def collide(self, i, parts=None, detail=False):
        parts = parts or self.parts(i)
        D = np.concatenate([x[1] for x in parts]); lo = np.concatenate([x[2] for x in parts]); hi = np.concatenate([x[3] for x in parts])
        lab = np.concatenate([np.full(len(x[2]), BI[x[0]]) for x in parts])
        r0 = 60.0; tr = cKDTree(D * r0); pr = tr.query_pairs(3.0 * r0 / 35.0, output_type="ndarray")
        if not len(pr): return None
        a, b = pr[:, 0], pr[:, 1]; la, lb = lab[a], lab[b]
        keep = ~EXEMPT[la, lb]
        # crank k vs distal k: adjacent, exempt inside the elbow's footprint
        E = self.RS[i] @ self.K["E"][i].T                                                          # (3, 3) columns
        adj = ((la >= 1) & (la <= 3) & (lb == la + 3)) | ((lb >= 1) & (lb <= 3) & (la == lb + 3))
        if adj.any():
            k = np.where(la <= 3, la, lb) - 1; ek = E[:, k].T
            ang = lambda idx: np.arccos(np.clip(np.sum(D[idx] * ek, 1), -1, 1)) * lo[idx]
            near = (ang(a) < PIN_R + CLR + SP) | (ang(b) < PIN_R + CLR + SP)
            keep &= ~(adj & near)
        a, b = a[keep], b[keep]
        if not len(a): return None
        tang = np.arccos(np.clip(np.sum(D[a] * D[b], 1), -1, 1)) * np.minimum(lo[a], lo[b])
        hit = (tang < 3.0) & (lo[a] < hi[b] + CLR) & (lo[b] < hi[a] + CLR)
        if not hit.any(): return None
        h = np.nonzero(hit)[0][0]
        return (BODIES[lab[a[h]]], BODIES[lab[b[h]]]) if detail else True

    def metal(self, i, detail=False):
        """(scored points, extra contact-only points, per-point part labels of the scored set) or None"""
        if not self.ok or not self.kin[i]: return None
        parts = self.parts(i)
        c = self.collide(i, parts, detail)
        if c is not None: return ("collide",) + tuple(c) if detail else None
        sc, lab, ex = [], [], []
        for b, D, lo, hi, m in parts:
            sc.append(D[m] * lo[m, None]); lab += [b[0] if b[0] in "TCDH" else "E" if b.startswith("EP") else "P"] * int(m.sum())
            if b[0] in "CD": ex.append(D * hi[:, None])
            if b.startswith("EP") or b.startswith("PP"):
                ex.append(D * hi[:, None])
        for k, lev in ((k, self.Ek[k]) for k in range(3)):                       # elbow pin walls
            e = self.RS[i] @ self.K["E"][i, k]; f1, f2 = perp(e); th = np.linspace(0, 2 * np.pi, 24, endpoint=False)
            for z in (lev + 2, lev + 5, lev + PIN_TOP):
                ex.append(z * e + PIN_R * (np.cos(th)[:, None] * f1 + np.sin(th)[:, None] * f2))
        return np.concatenate(sc), np.concatenate(ex), np.array(lab)


def evaluate(p, B, rig, maps, K=None, per_member=False):
    t0 = time.time(); B.reset(); M = Model(p, B, rig, maps, K)
    why = dict(kin_fail=int((~M.kin).sum()), reach_fail=int((~M.K["reach_ok"]).sum()), path_fail=int((~M.K["path_ok"]).sum()), collide=0, extra_contact=0)
    mem = {}
    if M.ok:
        for i in range(len(B.poses)):
            out = M.metal(i)
            if out is None:
                if M.kin[i]: why["collide"] += 1
                B.record(i, None); continue
            sc, ex, lab = out
            de = B.dist(i, ex)
            if de.min() < 0:
                why["extra_contact"] += 1; sc = np.concatenate([sc, ex[np.argmin(de)][None]]); lab = np.r_[lab, "x"]
            d = B.record(i, sc)
            if per_member and B.kind[i] == "clip" and d.min() >= 0:
                for b in np.unique(lab): mem.setdefault(b, []).append(d[lab == b])
    r = B.report(); r.update(why=why, secs=round(time.time() - t0, 1))
    if per_member:
        r["members"] = {b: dict(n=int(sum(len(x) for x in v)), ib14=round(float(np.mean((np.concatenate(v) >= 2) & (np.concatenate(v) <= 14))), 3),
                                ib10=round(float(np.mean((np.concatenate(v) >= 2) & (np.concatenate(v) <= 10))), 3),
                                med=round(float(np.median(np.concatenate(v))), 1)) for b, v in mem.items()}
    if M.ok: r["levels"] = dict(L=[round(x, 1) for x in M.L], crank=[round(x, 1) for x in M.lvl], Ek=[round(x, 1) for x in M.Ek], Sk=[round(x, 1) for x in M.Sk], turret_rho=round(M.T["rho"], 1))
    return r, M
