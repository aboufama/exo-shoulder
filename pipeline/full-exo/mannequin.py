"""Display-mannequin head and neck for the film (film_frames.py -> render_film.py) and its free preview (film.html).

Why: the rig's render skin (pipeline/avg/body_mesh.json, BP.F) carries the scanned face (nose, eyes, lips, ears), and
its neck has a SEAM RING at y = 109 S = 115.1 mm: build_body.py cut the decimated body skin and the full-resolution head
by the same plane and joined the two cut loops with a zipper strip (anatomy-build/rig.py replace_head) that lies IN
that plane - 423 flat, folded, near-zero-area triangles whose normals point straight up or down (49 of them exactly
zero area). Smooth shading bends every seam vertex normal toward them: the jagged dark ring around the neck in the
film. The judges use the rig as it is; only the film's mannequin is rebuilt here.

What: everything above the plane y = Y_STITCH (lower neck, below the old seam) is replaced by one new surface.
  * head: the rig's own head as a radial function about a cranium centre (first exit of rays cast from inside it).
    The face (eyes, nose, mouth) and the ears are masked out and filled, and the whole function is smoothed, by one
    thin-plate solve on the sphere -> a smooth featureless head with the rig's own cranium, jaw line and chin;
  * neck: the rig's own neck (signed distance to the render skin, Gaussian-smoothed), no seam;
  * the two fields are blended across a band along the jaw-occiput line (BAND); one marching-cubes surface, relaxed
    and projected back onto the field;
  * stitch: the body is cut exactly on y = Y_STITCH (new vertices on its edges) and zipped to the new surface's bottom
    loop GAP mm above it, on the same surface (no in-plane zipper).
Every new vertex follows the posed body: its displacement from rest is the inverse-distance blend of its 4 nearest
rig vertices (the cut vertices: exact edge interpolation), so the neck rides the trapezius as the rig's skin does.

    python3 mannequin.py [--glb out.glb]      # -> mannequin_head.json (read by film_frames.py and film.html)
    import mannequin as MQ; M = MQ.Mannequin(); M.F (faces), M.verts(BP.posed(pose)) (compact vertex array, mm)
"""
import base64, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "avg"))
OUT = os.path.join(HERE, "mannequin_head.json")
b64 = lambda a: base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
unb64 = lambda s, t: np.frombuffer(base64.b64decode(s), t)
CACHE = os.environ.get("MQ_CACHE")                    # dir: keep the slow stages (rays, neck distance field) while tuning


def cached(name, fn):
    p = os.path.join(CACHE, name + ".npy") if CACHE else None
    if p and os.path.exists(p): return np.load(p)
    a = fn()
    if p: os.makedirs(CACHE, exist_ok=True); np.save(p, a)
    return a


# --------------------------------------------------------------------------------------------- mesh helpers
def cut_below(V, F, yc):
    """clip (V, F) by the plane y = yc, keep the part below. Returns kept whole faces (mask), the pieces of the cut
    faces as faces over [V, new], and the new vertices as (a, b, t): V[a] + t (V[b] - V[a])."""
    inside = V[:, 1] < yc; ni = inside[F].sum(1); new = {}; ab = []; pieces = []
    def cross(a, b):
        key = (min(a, b), max(a, b))
        if key not in new:
            t = (yc - V[key[0], 1]) / (V[key[1], 1] - V[key[0], 1]); new[key] = len(V) + len(ab); ab.append((key[0], key[1], t))
        return new[key]
    for f in F[(ni == 1) | (ni == 2)]:
        poly = []
        for k in range(3):
            a, b = f[k], f[(k + 1) % 3]
            if inside[a]: poly.append(a)
            if inside[a] != inside[b]: poly.append(cross(a, b))
        for k in range(1, len(poly) - 1): pieces.append((poly[0], poly[k], poly[k + 1]))
    return ni == 3, np.array(pieces, int).reshape(-1, 3), np.array(ab, float).reshape(-1, 3)


def boundary_loops(F):
    e = np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]; es = np.sort(e, 1)
    _, inv, cnt = np.unique(es, axis=0, return_inverse=True, return_counts=True)
    b = e[cnt[inv.ravel()] == 1]; nxt = {int(a): int(c) for a, c in b}; loops = []; seen = set()
    for a in list(nxt):
        if a in seen: continue
        lp = [a]; seen.add(a); x = nxt[a]
        while x != a and x not in seen and x in nxt: lp.append(x); seen.add(x); x = nxt[x]
        loops.append(np.array(lp))
    return loops


def zip_loops(A, B, PA, PB):
    """triangle strip between two closed horizontal loops of one surface, A below (body cut) and B above (new surface),
    running in opposite directions. B's vertices are matched to A by their nearest point on A's polyline seen from
    above (rig.py's arc-length matching folded the strip where the coarse body loop and the fine new loop differ)."""
    def match(B, PB):
        Q = np.r_[PA, PA[:1]][:, [0, 2]]; seg = np.diff(Q, axis=0); La = np.linalg.norm(seg, axis=1); cum = np.r_[0, np.cumsum(La)]
        pb = PB[:, [0, 2]]; t = np.clip(((pb[:, None] - Q[None, :-1]) * seg[None]).sum(-1) / np.maximum(La ** 2, 1e-12)[None], 0, 1)
        d = np.linalg.norm(Q[None, :-1] + t[..., None] * seg[None] - pb[:, None], axis=2); k = d.argmin(1)
        return (cum[k] + t[np.arange(len(pb)), k] * La[k]) / cum[-1]
    B = B[::-1]; PB = PB[::-1]; sb = match(B, PB)
    if (((np.diff(np.r_[sb, sb[:1]]) + 0.5) % 1.0) - 0.5).sum() < 0: B = B[::-1]; PB = PB[::-1]; sb = sb[::-1]   # same direction: undo
    j0 = int(np.argmin(sb)); B = np.roll(B, -j0); sb = np.roll(sb, -j0)
    sb = np.maximum.accumulate(np.where(np.diff(np.r_[0.0, sb]) < -0.5, sb + 1, sb))   # monotone (small back-steps flattened)
    na, nb = len(A), len(B); seg = np.linalg.norm(np.diff(np.r_[PA, PA[:1]], axis=0), axis=1)
    ua = np.r_[0, np.cumsum(seg)] / seg.sum(); ub = np.r_[sb, 1.0 + sb[0]]; i = j = 0; out = []
    while i < na or j < nb:
        if j >= nb or (i < na and ua[i + 1] <= ub[j + 1]): out.append((A[(i + 1) % na], A[i % na], B[j % nb])); i += 1
        else: out.append((A[i % na], B[j % nb], B[(j + 1) % nb])); j += 1
    return np.array(out, int)


def neighbours(F, n):
    from scipy.sparse import coo_matrix
    i = np.r_[F[:, 0], F[:, 1], F[:, 2], F[:, 1], F[:, 2], F[:, 0]]; j = np.r_[F[:, 1], F[:, 2], F[:, 0], F[:, 0], F[:, 1], F[:, 2]]
    A = coo_matrix((np.ones(len(i)), (i, j)), shape=(n, n)).tocsr(); A.data[:] = 1; return A


def vnormals(V, F):
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]]); N = np.zeros_like(V)
    for k in range(3): np.add.at(N, F[:, k], fn)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


# --------------------------------------------------------------------------------------------- the build
def build(verbose=True):
    import body_pose as BP, trimesh
    from scipy import ndimage, sparse
    from scipy.sparse.linalg import spsolve
    from scipy.spatial import cKDTree
    from skimage.measure import marching_cubes
    t0 = time.time(); log = (lambda *a: print(f"[{time.time() - t0:5.1f} s]", *a, flush=True)) if verbose else (lambda *a: None)
    J = json.load(open(os.path.join(HERE, "..", "avg", "body_mesh.json"))); S = J["scale"]; hm = np.array(J["head"]["mid"])
    V0, F0 = BP.V0.astype(float), BP.F.astype(int); nb = len(V0)
    zc = hm[2]
    Y_STITCH = hm[1] - 111 * S                      # 96 mm: lower neck, above the trapezius flare, below the old seam (115)
    GAP = 5.0 * S                                   # body cut loop -> new surface loop
    C = np.array([hm[0] - 48 * S, hm[1] + 2 * S, zc])   # cranium centre: every head and upper-neck point is seen from it
    def s_band(x, y): return y - (hm[1] - 105 * S + 0.46 * (hm[0] - 16 * S - x))   # height over the jaw-occiput line (front: chin-throat corner, back: occiput)
    B0, B1 = -10 * S, 5 * S                         # neck field below B0, head field above B1
    L_CRANIUM, L_JAW = float(os.environ.get("MQ_LC", 13)), float(os.environ.get("MQ_LJ", 18))
    # ---- 1. head: radial function about C, first exit along rays cast from inside
    import torch
    torch.set_num_threads(2)
    NPH, NTH = 180, 360; dA = math.pi / NPH
    ph = (np.arange(NPH) + 0.5) * dA; th = np.arange(NTH) * dA
    PH, TH = np.meshgrid(ph, th, indexing="ij")
    D = np.stack([np.sin(PH) * np.cos(TH), np.cos(PH), np.sin(PH) * np.sin(TH)], -1).reshape(-1, 3)   # phi from +y, theta from +x (anterior) toward +z
    sel = V0[F0].min(1)[:, 1] > Y_STITCH - 60 * S
    def cast():
        T = torch.tensor(V0[F0[sel]], dtype=torch.float64)
        v0 = T[:, 0]; e1 = T[:, 1] - v0; e2 = T[:, 2] - v0; sv = torch.tensor(C) - v0; q = torch.cross(sv, e1, dim=1); te = (e2 * q).sum(1)
        R = np.full(len(D), np.inf); Dt = torch.tensor(D)
        for a in range(0, len(D), 96):
            d = Dt[a:a + 96]; p = torch.cross(d[:, None, :].expand(-1, len(e2), -1), e2[None].expand(len(d), -1, -1), dim=2)
            det = (e1[None] * p).sum(-1); inv = 1.0 / torch.where(det.abs() < 1e-12, torch.full_like(det, 1e-12), det)
            u = (sv[None] * p).sum(-1) * inv; v = (d[:, None, :] * q[None]).sum(-1) * inv; t = te[None] * inv
            ok = (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6); t = torch.where(ok, t, torch.full_like(t, np.inf)); R[a:a + 96] = t.min(1).values.numpy()
        return R
    R = cached("rays", cast)
    log("rays", len(D), "x", int(sel.sum()), "triangles")
    Ph = C + D * np.where(np.isfinite(R), R, 0)[:, None]
    ele = 90 - np.degrees(PH.ravel()); azi = np.degrees((TH.ravel() + math.pi) % (2 * math.pi) - math.pi)   # elevation, azimuth (0 = anterior, +90 = right)
    data = np.isfinite(R) & (R < 230 * S) & (s_band(Ph[:, 0], Ph[:, 1]) > B0 - 6 * S)
    def box(a, a0, a1, e, e0, e1_, soft=6.0):
        sm = lambda x: np.clip(x / soft, 0, 1)
        return sm(a - a0) * sm(a1 - a) * sm(e - e0) * sm(e1_ - e)
    face = box(azi, -50, 50, ele, -46, 15)                                   # eyes (to the outer corners), nose, mouth; keeps forehead, chin, jaw
    ears = np.maximum(box(azi, 62, 128, ele, -36, 22), box(azi, -128, -62, ele, -36, 22))
    w = data * (1 - np.maximum(face, ears))
    Rd = np.where(data, R, 0.0)
    log(f"data {data.mean():.2f}, face {(face > 0.5).sum()}, ears {(ears > 0.5).sum()} directions masked")
    # thin-plate on the sphere: min sum w A (r - d)^2 + lam sum A (Lap r)^2  (finite volumes on the lat-long grid)
    n = NPH * NTH; idx = np.arange(n).reshape(NPH, NTH); s_c = np.sin(ph); s_n = np.sin(ph - dA / 2); s_s = np.sin(ph + dA / 2)
    rows, cols, vals = [], [], []
    def add(r_, c_, v_): rows.append(r_.ravel()); cols.append(c_.ravel()); vals.append(np.broadcast_to(v_, r_.shape).ravel())
    I = idx; up = np.roll(idx, 1, 0); dn = np.roll(idx, -1, 0); lf = np.roll(idx, 1, 1); rt = np.roll(idx, -1, 1)
    cn = (s_n / (s_c * dA * dA))[:, None] * np.ones((1, NTH)); cn[0] = 0
    cs = (s_s / (s_c * dA * dA))[:, None] * np.ones((1, NTH)); cs[-1] = 0
    ct = (1 / (s_c * dA) ** 2)[:, None] * np.ones((1, NTH))
    add(I, up, cn); add(I, dn, cs); add(I, lf, ct); add(I, rt, ct); add(I, I, -(cn + cs + 2 * ct))
    Lap = sparse.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))
    Ar = np.repeat(s_c * dA * dA, NTH); lc = lambda l: 1.0 / (l * (l + 1)) ** 2   # SH degree at half attenuation
    jaw = np.clip((-25 - ele) / 15, 0, 1) * (s_band(Ph[:, 0], Ph[:, 1]) > B1)    # jaw line and chin: finer (sharper) than the cranium
    lam = lc(L_CRANIUM) + jaw * (lc(L_JAW) - lc(L_CRANIUM))
    M = sparse.diags(w * Ar) + Lap.T @ sparse.diags(lam * Ar) @ Lap
    r_s = spsolve(M.tocsc(), w * Ar * Rd).reshape(NPH, NTH)
    if os.environ.get("MQ_DEBUG"): np.savez(os.environ["MQ_DEBUG"], R=R.reshape(NPH, NTH), r_s=r_s, w=w.reshape(NPH, NTH), data=data.reshape(NPH, NTH), C=C)
    log(f"thin-plate head, l_c {L_CRANIUM}/{L_JAW}: r {r_s.min():.0f}..{r_s.max():.0f} mm, data residual p95 {np.percentile(np.abs(r_s.ravel() - R)[w > 0.99], 95):.1f} mm")
    nod = (~data).reshape(NPH, NTH)                 # rays that leave below the band (down the neck): the head's closure stays inside
    r_s[nod] = np.maximum(r_s[nod], np.minimum(R.reshape(NPH, NTH)[nod], 400.0))
    rpad = np.c_[r_s, r_s[:, :1]]
    def f_head(P):
        d = P - C; rr = np.linalg.norm(d, axis=1); u = d / (rr[:, None] + 1e-12)
        fi = np.arccos(np.clip(u[:, 1], -1, 1)) / dA - 0.5; tj = (np.arctan2(u[:, 2], u[:, 0]) % (2 * math.pi)) / dA
        return rr - ndimage.map_coordinates(rpad, [np.clip(fi, 0, NPH - 1), tj], order=1, mode="nearest")
    # ---- 2. neck: signed distance to the rig's skin on a grid, smoothed (old seam and facets gone)
    h = 1.5 * S; lo = np.array([hm[0] - 205 * S, Y_STITCH - 10 * S, zc - 135 * S]); hi = np.array([hm[0] + 95 * S, hm[1] + 135 * S, zc + 135 * S])
    shape = np.ceil((hi - lo) / h).astype(int) + 1; ax = [lo[k] + h * np.arange(shape[k]) for k in range(3)]
    G = np.stack(np.meshgrid(*ax, indexing="ij"), -1).reshape(-1, 3)
    def sdf():
        fsel = np.flatnonzero(V0[F0].max(1)[:, 1] > Y_STITCH - 40 * S); sub = trimesh.Trimesh(V0, F0[fsel], process=False)
        Ps, fi_ = trimesh.sample.sample_surface(sub, 600000, seed=3); Ns = sub.face_normals[fi_]
        near = s_band(G[:, 0], G[:, 1]) < B1 + 14 * S
        dist, j = cKDTree(Ps).query(G[near], workers=2, distance_upper_bound=85 * S); miss = j >= len(Ps); j[miss] = 0   # deepest neck point ~65 mm
        sgn = np.sign(((G[near] - Ps[j]) * Ns[j]).sum(1)); sgn[sgn == 0] = 1; sgn[miss] = 1; dist[miss] = 85 * S
        SD = np.full(len(G), 20.0); SD[near] = sgn * dist; return SD.reshape(*shape)
    SD = cached("neck_sdf", sdf)
    yy = ax[1][None, :, None]; gm = np.clip((yy - (Y_STITCH + 8 * S)) / (14 * S), 0, 1)
    SDs = (1 - gm) * ndimage.gaussian_filter(SD, 1.2 * S / h) + gm * ndimage.gaussian_filter(SD, 3.0 * S / h)   # light at the stitch, 3 mm above
    log("neck SDF", tuple(shape))
    def f_neck(P): return ndimage.map_coordinates(SDs, list(((P - lo) / h).T), order=1, mode="nearest")
    def field(P):
        b = np.clip((s_band(P[:, 0], P[:, 1]) - B0) / (B1 - B0), 0, 1); b = b * b * (3 - 2 * b)
        out = np.empty(len(P)); m0 = b < 1; m1 = b > 0
        fn = np.zeros(len(P)); fh = np.zeros(len(P))
        if m0.any(): fn[m0] = f_neck(P[m0])
        if m1.any(): fh[m1] = f_head(P[m1])
        return (1 - b) * fn + b * fh
    Fv = field(G).reshape(*shape)
    Fv[:, 0, :] = np.maximum(Fv[:, 0, :], 1.0)       # open bottom: closed below, cut away later
    vv, ff, _, _ = marching_cubes(Fv, 0.0, spacing=(h, h, h), step_size=2, allow_degenerate=False)
    vv = vv + lo
    log("marching cubes", len(vv), "verts", len(ff), "faces")
    # orientation: outward normals
    m = trimesh.Trimesh(vv, ff, process=False)
    if m.volume < 0: ff = ff[:, ::-1]
    # keep the component that holds the head
    cc = trimesh.graph.connected_components(trimesh.Trimesh(vv, ff, process=False).face_adjacency, nodes=np.arange(len(ff)))
    big = max(cc, key=len); ff = ff[np.sort(big)]
    # ---- 3. relax (tangential) + project back onto the field
    def grad(P, e=0.3 * S):
        g = np.zeros_like(P)
        for k in range(3):
            dv = np.zeros(3); dv[k] = e; g[:, k] = (field(P + dv) - field(P - dv)) / (2 * e)
        return g
    def project(P, it=3):
        for _ in range(it):
            f = field(P); g = grad(P); P = P - (f / np.maximum((g * g).sum(1), 1e-6))[:, None] * g
        return P
    A = neighbours(ff, len(vv)); deg = np.asarray(A.sum(1)).ravel(); bnd = np.zeros(len(vv), bool)
    for lp in boundary_loops(ff): bnd[lp] = True
    P = vv.copy()
    for it in range(8):
        Nn = vnormals(P, ff); L_ = (A @ P) / np.maximum(deg, 1)[:, None] - P; L_ -= (L_ * Nn).sum(1, keepdims=True) * Nn
        P[~bnd] += 0.6 * L_[~bnd]; P = project(P, 2)
    P = project(P, 2)
    log(f"relaxed; |f| p99 {np.percentile(np.abs(field(P)), 99):.3f} mm")
    # ---- 4. cut the body at Y_STITCH (moved by < 2 mm so that no rig vertex lies within reach of the plane: no
    #         sliver pieces), the new surface GAP above; zip the two loops
    col = np.hypot(V0[:, 0] - (hm[0] - 40 * S), V0[:, 2] - zc) < 160 * S
    cand = Y_STITCH + np.linspace(-2, 2, 81) * S
    yb = cand[np.argmax([np.abs(V0[col, 1] - c).min() for c in cand])]
    keep_h, pc_h, ab_h = cut_below(P * [1, -1, 1], ff, -(yb + GAP))            # keep ABOVE: mirror y
    Ph_ = np.r_[P, P[ab_h[:, 0].astype(int)] + ab_h[:, 2:3] * (P[ab_h[:, 1].astype(int)] - P[ab_h[:, 0].astype(int)])] if len(ab_h) else P
    Fh_ = np.r_[ff[keep_h], pc_h]
    cc = trimesh.graph.connected_components(trimesh.Trimesh(Ph_, Fh_, process=False).face_adjacency, nodes=np.arange(len(Fh_)))
    Fh_ = Fh_[np.sort(max(cc, key=len))]
    used = np.zeros(len(Ph_), bool); used[Fh_.ravel()] = True; remap = -np.ones(len(Ph_), int); remap[used] = np.arange(used.sum()); Ph_, Fh_ = Ph_[used], remap[Fh_]
    keep_b, pc_b, ab_b = cut_below(V0, F0, yb)
    nab = len(ab_b); Pab = V0[ab_b[:, 0].astype(int)] + ab_b[:, 2:3] * (V0[ab_b[:, 1].astype(int)] - V0[ab_b[:, 0].astype(int)])
    far = np.hypot(V0[F0[~keep_b]][:, :, 0].mean(1) - (hm[0] - 40 * S), V0[F0[~keep_b]][:, :, 2].mean(1) - zc)
    assert far.max() < 160 * S, f"body faces above the stitch outside the neck column ({far.max():.0f} mm)"
    # combined index space: [body 0..nb) [cut nb..nb+nab) [new nb+nab..); the cut pieces reference body and cut ids
    lb = [l for l in boundary_loops(np.r_[F0[keep_b], pc_b]) if (l >= nb).all()]
    assert len(lb) == 1, f"body cut loops: {len(lb)}"; lb = lb[0]
    lh = max(boundary_loops(Fh_), key=len); off = nb + nab
    Pall = np.r_[V0, Pab, Ph_]
    Z = zip_loops(lb, lh + off, Pall[lb], Pall[lh + off])
    Fp = np.r_[pc_b, Fh_ + off, Z]
    log(f"stitch: body loop {len(lb)} verts at y {yb:.2f} (min vertex distance {np.abs(V0[col, 1] - yb).min():.2f} mm), new loop {len(lh)} at {yb + GAP:.1f}; zipper {len(Z)} faces")
    # ---- 6. per-vertex displacement weights (rest -> posed): cut vertices exact, new vertices IDW over 4 rig vertices
    Wi = np.zeros((len(Pall) - nb, 4), int); Ww = np.zeros((len(Pall) - nb, 4))
    Wi[:nab, 0] = ab_b[:, 0]; Wi[:nab, 1] = ab_b[:, 1]; Ww[:nab, 0] = 1 - ab_b[:, 2]; Ww[:nab, 1] = ab_b[:, 2]
    dk, jk = cKDTree(V0).query(Pall[off:], k=4); wk = 1.0 / np.maximum(dk, 0.5) ** 2; wk /= wk.sum(1, keepdims=True)
    Wi[nab:], Ww[nab:] = jk, wk
    # sizes (reported)
    Hn = Pall[off:]; hd = Hn[Hn[:, 1] > hm[1] - 40 * S]
    log(f"head: width {np.ptp(hd[:, 2]):.0f} mm, depth {np.ptp(hd[:, 0]):.0f} mm, chin-crown {Hn[:, 1].max() - (hm[1] - 108 * S):.0f} mm (approx); patch {len(Pall) - nb} verts, {len(Fp)} faces")
    out = dict(note="film mannequin head/neck patch (pipeline/full-exo/mannequin.py)", nb=int(nb), nf=int(len(F0)),
               keep=b64(np.packbits(keep_b)), pv=b64(Pall[nb:].astype(np.float32)), wi=b64(Wi.astype(np.uint32)), ww=b64(Ww.astype(np.float32)),
               pf=b64(Fp.astype(np.uint32)), npv=int(len(Pall) - nb), npf=int(len(Fp)), y_stitch=float(Y_STITCH))
    return out


class Mannequin:
    """the film mannequin: rig skin below the stitch + the new head/neck; compact vertex numbering"""
    def __init__(self, path=OUT):
        J = json.load(open(path)); nb, nf = J["nb"], J["nf"]
        import body_pose as BP
        F0 = BP.F.astype(np.int64); self.V0 = BP.V0.astype(float)
        keep = np.unpackbits(unb64(J["keep"], np.uint8))[:nf].astype(bool)
        self.pv = unb64(J["pv"], np.float32).reshape(-1, 3).astype(float); self.wi = unb64(J["wi"], np.uint32).reshape(-1, 4).astype(np.int64)
        self.ww = unb64(J["ww"], np.float32).reshape(-1, 4).astype(float); pf = unb64(J["pf"], np.uint32).reshape(-1, 3).astype(np.int64)
        Fall = np.r_[F0[keep], pf]; n = nb + len(self.pv); used = np.zeros(n, bool); used[Fall.ravel()] = True
        remap = -np.ones(n, np.int64); remap[used] = np.arange(used.sum()); self.F = remap[Fall]
        self.body = np.flatnonzero(used[:nb]); self.new = np.flatnonzero(used[nb:]); self.nv = int(used.sum())

    def verts(self, P):
        """posed rig skin (BP.posed, N x 3 mm) -> mannequin vertices (nv x 3 mm), same frame"""
        dP = P - self.V0; pn = self.pv[self.new] + np.einsum("nk,nkc->nc", self.ww[self.new], dP[self.wi[self.new]])
        return np.r_[P[self.body], pn]


if __name__ == "__main__":
    out = build(); json.dump(out, open(OUT, "w"), separators=(",", ":")); print("wrote", OUT, f"{os.path.getsize(OUT) / 1e6:.1f} MB")
    if "--glb" in sys.argv:
        import trimesh, body_pose as BP
        M = Mannequin(); V = M.verts(BP.V0.astype(float)); trimesh.Trimesh(V * 1e-3, M.F, process=False).export(sys.argv[sys.argv.index("--glb") + 1])
