"""Linear-elastic FEA of a spherical-shell link (Ti-6Al-4V) for sizing the D4 shoulder links.

Mesh: structured hex8 that follows the shell exactly. In-plane cells live on a gnomonic chart of the link's mid
direction; through-thickness layers are true spheres r0..r1. Cells are kept where the planform SDF (the same G2
outline the CAD uses) is negative and outside the bores; boundary nodes are snapped onto the outline so the edge is
smooth (no staircase stress peaks).
Loads: hub A held by a rigid insert (all nodes within RIG of its axis fixed); hub B loaded by a rigid-insert moment
(nodal forces f_i = M x d_i / sum|d_i|^2, d_i = offset from the axis point, which is exactly rigid-body consistent).
Three unit moments (radial / lateral / along-link at hub B) are solved with one factorisation; the worst direction
of a |M| moment is found per element by sampling the unit sphere of moment directions.

    python3 fea_link.py test        # cantilever check against beam theory
"""
import math, sys, time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

E, NU = 113.8e3, 0.342                      # Ti-6Al-4V, MPa
SY = 880.0


def smin(a, b, k):                          # cubic smooth minimum: C2, so the outline is curvature continuous (G2)
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h ** 3 * k / 6.0


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)


def arc_dist(p, A, B):
    """angular distance (rad) from unit vectors p (...,3) to the great-circle arc A->B"""
    n = unit(np.cross(A, B)); tot = math.acos(np.clip(A @ B, -1, 1))
    s = p @ n; q = unit(p - s[..., None] * n)
    a1 = np.arccos(np.clip(q @ A, -1, 1)); a2 = np.arccos(np.clip(q @ B, -1, 1))
    on = np.abs(a1 + a2 - tot) < 1e-6
    d_line = np.arcsin(np.clip(np.abs(s), 0, 1))
    d_end = np.minimum(np.arccos(np.clip(p @ A, -1, 1)), np.arccos(np.clip(p @ B, -1, 1)))
    return np.where(on, d_line, d_end)


class Planform:
    """link outline on the sphere: hub discs (radius rh, mm at r_ref) + strips (half width hw) + pads, cubic smooth union"""
    def __init__(self, hubs, strips, r_ref, k=10.0):
        self.hubs = [(unit(p), rh) for p, rh in hubs]; self.strips = [(unit(a), unit(b), hw) for a, b, hw in strips]
        self.r = r_ref; self.k = k
    def sdf(self, p):
        p = unit(p); d = None
        for P, rh in self.hubs:
            di = self.r * np.arccos(np.clip(p @ P, -1, 1)) - rh
            d = di if d is None else smin(d, di, self.k)
        for A, B, hw in self.strips:
            d = smin(d, self.r * arc_dist(p, A, B) - hw, self.k)
        return d


def chart(dirs):
    m = unit(np.sum([unit(d) for d in dirs], axis=0))
    ex = unit(np.cross(m, [0.0, 0.0, 1.0]) if abs(m[2]) < 0.9 else np.cross(m, [1.0, 0, 0])); ey = np.cross(m, ex)
    return m, ex, ey


# ------------------------------------------------------------------ hex8 element machinery
GP = np.array([[i, j, k] for i in (-1, 1) for j in (-1, 1) for k in (-1, 1)], float) / math.sqrt(3)
NODE_XI = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float)
def dN(xi):                                                   # (8,3) derivatives of the 8 shape functions at xi
    return 0.125 * NODE_XI * np.stack([(1 + NODE_XI[:, 1] * xi[1]) * (1 + NODE_XI[:, 2] * xi[2]),
                                        (1 + NODE_XI[:, 0] * xi[0]) * (1 + NODE_XI[:, 2] * xi[2]),
                                        (1 + NODE_XI[:, 0] * xi[0]) * (1 + NODE_XI[:, 1] * xi[1])], 1)
DN_GP = np.stack([dN(g) for g in GP]); DN_C = dN(np.zeros(3))
lam, mu = E * NU / ((1 + NU) * (1 - 2 * NU)), E / (2 * (1 + NU))
Dm = np.zeros((6, 6)); Dm[:3, :3] = lam; Dm[np.arange(3), np.arange(3)] += 2 * mu; Dm[3:, 3:] = np.eye(3) * mu


def bmat(Xe, dn):
    """Xe (n,8,3) element node coords, dn (8,3) -> B (n,6,24), detJ (n,)"""
    J = np.einsum("ai,naj->nij", dn, Xe); Ji = np.linalg.inv(J); dX = np.einsum("nij,aj->nai", Ji, dn)
    B = np.zeros((len(Xe), 6, 24))
    for a in range(8):
        B[:, 0, 3 * a] = dX[:, a, 0]; B[:, 1, 3 * a + 1] = dX[:, a, 1]; B[:, 2, 3 * a + 2] = dX[:, a, 2]
        B[:, 3, 3 * a] = dX[:, a, 1]; B[:, 3, 3 * a + 1] = dX[:, a, 0]
        B[:, 4, 3 * a + 1] = dX[:, a, 2]; B[:, 4, 3 * a + 2] = dX[:, a, 1]
        B[:, 5, 3 * a] = dX[:, a, 2]; B[:, 5, 3 * a + 2] = dX[:, a, 0]
    return B, np.linalg.det(J)


def assemble(X, H):
    Xe = X[H]; K = np.zeros((len(H), 24, 24))
    for g in range(8):
        B, dj = bmat(Xe, DN_GP[g])
        if (dj <= 0).any(): raise ValueError(f"{(dj <= 0).sum()} inverted elements")
        K += np.einsum("nki,kl,nlj,n->nij", B, Dm, B, dj)
    dof = (3 * H[:, :, None] + np.arange(3)).reshape(len(H), 24)
    r = np.repeat(dof, 24, 1).ravel(); c = np.tile(dof, (1, 24)).ravel()
    n = 3 * len(X); return sp.csc_matrix((K.ravel(), (r, c)), shape=(n, n))


def solve(X, H, fixed, loads):
    """fixed: node mask; loads: list of (n,3) nodal force arrays -> list of displacement arrays"""
    t0 = time.time(); K = assemble(X, H)
    free = np.repeat(~fixed, 3); Kf = K[free][:, free]
    lu = sla.splu(Kf.tocsc(), permc_spec="COLAMD")
    out = []
    for F in loads:
        u = np.zeros(3 * len(X)); u[free] = lu.solve(F.ravel()[free]); out.append(u.reshape(-1, 3))
    return out, time.time() - t0


DN_CORNER = np.stack([dN(x) for x in NODE_XI])
def stresses(X, H, U):
    """(n,8,6) stress at the 8 element corners (surface values for the outer layers)"""
    ue = U[H].reshape(len(H), 24); out = []
    for c in range(8):
        B, _ = bmat(X[H], DN_CORNER[c]); out.append(np.einsum("ij,nj->ni", Dm, np.einsum("nij,nj->ni", B, ue)))
    return np.stack(out, 1)


def vm(s):
    return np.sqrt(0.5 * ((s[..., 0] - s[..., 1]) ** 2 + (s[..., 1] - s[..., 2]) ** 2 + (s[..., 2] - s[..., 0]) ** 2) + 3 * (s[..., 3] ** 2 + s[..., 4] ** 2 + s[..., 5] ** 2))


def worst_vm(S3, Mmag, n_dir=600):
    """S3: list of 3 (n,6) stress fields for unit (1 N.mm) moments; worst von Mises over moment directions"""
    g = np.random.default_rng(1).normal(size=(n_dir, 3)); g /= np.linalg.norm(g, axis=1, keepdims=True)
    S = np.stack(S3, 0)                                                   # (3,n,8,6)
    best = np.zeros(S.shape[1]); arg = np.zeros(S.shape[1], int)
    for i in range(0, n_dir, 25):
        s = np.einsum("dk,kncj->dncj", g[i:i + 25], S) * Mmag; v = vm(s).max(2)
        m = v.max(0); a = v.argmax(0) + i; upd = m > best; best[upd] = m[upd]; arg[upd] = a[upd]
    return best, g[arg]


# ------------------------------------------------------------------ link mesh
def link_mesh(pf, pins, r0, r1, h=0.7, nl=6, bores=()):
    """pf Planform, pins: unit axes (for the chart), bores: [(axis, radius_mm)] through holes. Returns X (nodes, mm),
    H (hex connectivity), and the chart."""
    m, ex, ey = chart(pins); rm = 0.5 * (r0 + r1)
    # chart extents from hub/strip extents
    pts = []
    for P, rh in pf.hubs:
        g = P / (P @ m) * rm; pts.append(((g @ ex), (g @ ey), rh * (1 / (P @ m)) ** 2 + 4))
    x0 = min(p[0] - p[2] for p in pts); x1 = max(p[0] + p[2] for p in pts)
    y0 = min(p[1] - p[2] for p in pts); y1 = max(p[1] + p[2] for p in pts)
    xs = np.arange(x0, x1 + h, h); ys = np.arange(y0, y1 + h, h); nx, ny = len(xs), len(ys)
    GX, GY = np.meshgrid(xs, ys, indexing="ij")
    D = unit(m * rm + GX[..., None] * ex + GY[..., None] * ey)            # node directions (nx,ny,3)
    sd = pf.sdf(D)
    for ax, rb in bores: sd = np.maximum(sd, rb - rm * np.arccos(np.clip(D @ unit(ax), -1, 1)))
    cell = (sd[:-1, :-1] + sd[1:, :-1] + sd[1:, 1:] + sd[:-1, 1:]) / 4 < 0
    # snap boundary nodes (nodes used by active cells whose sdf > -h/2) onto the outline along the chart gradient
    used = np.zeros((nx, ny), bool); used[:-1, :-1] |= cell; used[1:, :-1] |= cell; used[1:, 1:] |= cell; used[:-1, 1:] |= cell
    gx, gy = np.gradient(sd, h, h); gn = np.sqrt(gx ** 2 + gy ** 2) + 1e-9
    mv = used & (np.abs(sd) < 0.5 * h)
    GX2 = GX - np.where(mv, sd * gx / gn ** 2, 0); GY2 = GY - np.where(mv, sd * gy / gn ** 2, 0)
    D2 = unit(m * rm + GX2[..., None] * ex + GY2[..., None] * ey)
    rr = np.linspace(r0, r1, nl + 1)
    X = (D2[..., None, :] * rr[None, None, :, None]).reshape(-1, 3)
    nid = lambda i, j, k: (i * ny + j) * (nl + 1) + k
    I, J = np.nonzero(cell); H = []
    for k in range(nl):
        H.append(np.stack([nid(I, J, k), nid(I + 1, J, k), nid(I + 1, J + 1, k), nid(I, J + 1, k),
                           nid(I, J, k + 1), nid(I + 1, J, k + 1), nid(I + 1, J + 1, k + 1), nid(I, J + 1, k + 1)], 1))
    H = np.concatenate(H)
    # orientation: make detJ positive
    _, dj = bmat(X[H[:1]], DN_C)
    if dj[0] < 0: H = H[:, [1, 0, 3, 2, 5, 4, 7, 6]]
    # undo the snap on any node of an element it inverted (or squashed), until none are left
    X0 = (D[..., None, :] * rr[None, None, :, None]).reshape(-1, 3)
    for _ in range(6):
        dj = np.min([bmat(X[H], DN_CORNER[c])[1] for c in range(8)], axis=0)
        _, dj0 = bmat(X0[H], DN_C)
        bad = dj < 0.2 * np.abs(dj0)
        if not bad.any(): break
        nb = np.unique(H[bad]); X[nb] = X0[nb]
    keep = np.unique(H); remap = -np.ones(len(X), int); remap[keep] = np.arange(len(keep))
    return X[keep], remap[H]


def rigid_moment(X, sel, c, M):
    """nodal forces on nodes sel equivalent to a rigid-insert moment M (N.mm) about point c"""
    c = X[sel].mean(0)                                                     # centroid: the forces are then a pure couple
    d = X[sel] - c; F = np.zeros_like(X)
    J = np.einsum("ni,ni->", d, d) * np.eye(3) - d.T @ d                   # 'inertia' of the node cloud
    w = np.linalg.solve(J, M); F[sel] = np.cross(w, d); return F


def analyse(pf, pA, pB, r0, r1, rig, Mmag, h=0.7, nl=6, bores=(), excl=None):
    """hub A fixed (rigid insert radius rig), unit moments at hub B. Returns dict with worst von Mises (outside the
    inserts + excl mm), tilt stiffness and the mesh/fields for plotting."""
    X, H = link_mesh(pf, [pA, pB], r0, r1, h, nl, bores)
    rn = np.linalg.norm(X, axis=1); Dn = X / rn[:, None]
    dA = (r0 + r1) / 2 * np.arccos(np.clip(Dn @ unit(pA), -1, 1)); dB = (r0 + r1) / 2 * np.arccos(np.clip(Dn @ unit(pB), -1, 1))
    fixed = dA < rig; selB = dB < rig
    cB = unit(pB) * (r0 + r1) / 2
    n_ = unit(pB); t_ = unit(np.cross(pB, pA)); l_ = np.cross(t_, n_)      # radial, lateral(normal to link plane), along link
    loads = [rigid_moment(X, selB, cB, e) for e in (n_, t_, l_)]
    U, dt = solve(X, H, fixed, loads)
    S3 = [stresses(X, H, u) for u in U]
    Xc = X[H].mean(1); Dc = Xc / np.linalg.norm(Xc, axis=1, keepdims=True); rc = (r0 + r1) / 2
    eA = rc * np.arccos(np.clip(Dc @ unit(pA), -1, 1)); eB = rc * np.arccos(np.clip(Dc @ unit(pB), -1, 1))
    ex_ = rig + (excl if excl is not None else 1.5)
    ok = (eA > ex_) & (eB > ex_)
    w, wd = worst_vm(S3, Mmag)
    # rotation of the loaded insert per unit moment (compliance matrix 3x3, rad / N.mm)
    C = np.zeros((3, 3))
    for k, u in enumerate(U):
        d = X[selB] - X[selB].mean(0); ub = u[selB]
        A_ = np.zeros((3 * len(d), 6)); A_[:, :3] = np.tile(np.eye(3), (len(d), 1))
        for i in range(len(d)):
            A_[3 * i:3 * i + 3, 3:] = -np.array([[0, -d[i, 2], d[i, 1]], [d[i, 2], 0, -d[i, 0]], [-d[i, 1], d[i, 0], 0]])
        sol = np.linalg.lstsq(A_, ub.ravel(), rcond=None)[0]; C[:, k] = sol[3:] @ np.c_[n_, t_, l_]
    return dict(vm_max=float(w[ok].max()), vm_p99=float(np.percentile(w[ok], 99.5)), where=Xc[ok][int(np.argmax(w[ok]))],
                dof=3 * len(X), elems=len(H), secs=dt, C=C, X=X, H=H, vm=w, ok=ok)


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "test":
    # straight-ish check: a long thin band on a big sphere (R = 5000 mm, nearly flat), w = 14, t = 4, rigid inserts
    R = 5000.0; L = 120.0; pA = np.array([0, 0, 1.0]); pB = unit([math.sin(L / R), 0, math.cos(L / R)])
    for t, nl in ((4.0, 4), (4.0, 6), (4.0, 8)):
        pf = Planform([(pA, 7.0), (pB, 7.0)], [(pA, pB, 7.0)], R, k=0.01)
        res = analyse(pf, pA, pB, R - t / 2, R + t / 2, 6.0, 25e3, h=0.7, nl=nl, excl=12.0)
        # beam theory at 25 N.m: flatwise 6M/(w t^2), torsion tau = M/(alpha w t^2) -> vm sqrt3 tau, edgewise 6M/(t w^2)
        print(f"t {t} layers {nl}: dof {res['dof']}, {res['secs']:.0f}s, worst vm {res['vm_max']:.0f} MPa (99.5% {res['vm_p99']:.0f}); "
              f"beam flatwise {6 * 25e3 / (14 * t * t):.0f}, torsion-vm {math.sqrt(3) * 25e3 / (0.2618 * 14 * t * t):.0f}")
