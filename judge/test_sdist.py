"""Validation of judge/sdist.py against brute force: the inside/outside sign against the generalized winding number
(Jacobson 2013; > 0.5 = inside, robust where ray parity is not) and ray parity (Moeller-Trumbore), the distance against
the exact closest point over all triangles. Cases: a cube (sharp edges and corners - where a nearest-face-normal sign
fails), a closed sphere, a real part (the J2 cap of the reference design, a welded glb tessellation with long facets -
where a 10-nearest-centroid search missed the closest triangle: the R6 false penetrations of 2026-10-15) and the posed
body mesh of the rig (the R2 judge's target; it self-intersects in deep poses, where inside is defined by the winding
number only). Also the same part as a RAW glb tessellation (unwelded: Mesh welds it) and two OPEN meshes - a sphere with
4 holes and the 3R design's BOTTOM + rail (holes / non-manifold edges after welding) - where one ray direction can pass
a hole: x-rays alone vs the x / y / z majority + generalized winding number. Also reports the old sign rule (the nearest
triangle's own normal over 10 centroids) for comparison.
    python3 judge/test_sdist.py"""
import os, sys, time
import numpy as np, trimesh
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "pipeline", "avg"))
import sdist


def ray_parity_inside(P, V, F, d=np.array([0.5773, 0.5774, 0.5775])):
    """inside if a ray from each point crosses the mesh an odd number of times (brute force)"""
    T = V[F]; e1 = T[:, 1] - T[:, 0]; e2 = T[:, 2] - T[:, 0]; d = d / np.linalg.norm(d); h = np.cross(d, e2); a = (e1 * h).sum(1)
    ok = np.abs(a) > 1e-12; f = np.where(ok, 1.0 / np.where(ok, a, 1), 0); out = np.zeros(len(P), bool)
    for i0 in range(0, len(P), 16):
        S = P[i0:i0 + 16, None, :] - T[None, :, 0]; u = f * (S * h).sum(-1); q = np.cross(S, e1[None]); v = f * (q @ d)
        t = f * (q * e2[None]).sum(-1); hit = ok & (u >= 0) & (u <= 1) & (v >= 0) & (u + v <= 1) & (t > 1e-9)
        out[i0:i0 + 16] = hit.sum(1) % 2 == 1
    return out


def winding_inside(P, V, F):
    """generalized winding number (sum of signed solid angles, Van Oosterom & Strackee) > 0.5"""
    T = V[F]; w = np.zeros(len(P))
    for i0 in range(0, len(P), 32):
        a, b, c = (T[None, :, q] - P[i0:i0 + 32, None] for q in range(3)); la, lb, lc = (np.linalg.norm(x, axis=-1) for x in (a, b, c))
        num = (a * np.cross(b, c)).sum(-1); den = la * lb * lc + (a * b).sum(-1) * lc + (a * c).sum(-1) * lb + (b * c).sum(-1) * la
        w[i0:i0 + 32] = np.arctan2(num, den).sum(1) / (2 * np.pi)
    return w > 0.5


def brute_dist(P, V, F):
    T = V[F]; best = np.full(len(P), np.inf)
    for j in range(0, len(F), 256):
        for q in range(min(256, len(F) - j)):
            t = T[j + q]; Q = sdist.closest_on_tri(P, *(np.broadcast_to(t[r], P.shape) for r in range(3))); best = np.minimum(best, np.linalg.norm(P - Q, axis=1))
    return best


def old_sign(P, V, F, k=10):
    T = V[F]; tree = cKDTree(T.mean(1)); _, J = tree.query(P, k=k); best = np.full(len(P), np.inf); sgn = np.ones(len(P))
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-18
    for c in range(k):
        j = J[:, c]; Q = sdist.closest_on_tri(P, T[j, 0], T[j, 1], T[j, 2]); dd = np.linalg.norm(P - Q, axis=1); b = dd < best - 1e-9
        best = np.where(b, dd, best); s = np.sign(((P - Q) * N[j]).sum(1)); s[s == 0] = 1; sgn = np.where(b, s, sgn)
    return sgn < 0


def check(name, V, F, P, dist=True):
    t0 = time.time(); truth = winding_inside(P, V, F); par = ray_parity_inside(P, V, F); sd = sdist.signed_distance(P, V, F); t1 = time.time() - t0
    new = sd < 0; old = old_sign(P, V, F); derr = float(np.abs(np.abs(sd) - brute_dist(P, V, F)).max()) if dist else float("nan")
    print(f"{name:40s} {len(P):5d} pts ({truth.mean() * 100:4.1f}% in; parity disagrees {100 * (par != truth).mean():4.1f}%): "
          f"new sign wrong {100 * (new != truth).mean():5.2f}%  old {100 * (old != truth).mean():5.2f}%  |d| err {derr:.1e} mm  ({t1:.0f}s)", flush=True)
    return float((new != truth).mean()), float((old != truth).mean()), derr


if __name__ == "__main__":
    rng = np.random.default_rng(0); res = {}
    box = trimesh.creation.box(extents=(40, 30, 20)); Vb, Fb = np.asarray(box.vertices, float), np.asarray(box.faces)
    Pc = rng.choice(Vb, 600) + rng.normal(0, 2.0, (600, 3)); E = Vb[Fb[:, [0, 1]]]; tt = rng.random((600, 1))
    Pe = (E[rng.integers(0, len(E), 600), 0] * tt + E[rng.integers(0, len(E), 600), 1] * (1 - tt)) + rng.normal(0, 1.5, (600, 3))
    res["cube corners"] = check("cube, near corners", Vb, Fb, Pc); res["cube edges"] = check("cube, near edges", Vb, Fb, Pe)
    sph = trimesh.creation.icosphere(subdivisions=3, radius=50); Vs, Fs = np.asarray(sph.vertices, float), np.asarray(sph.faces)
    Ps = Vs[rng.integers(0, len(Vs), 1500)] * (1 + rng.normal(0, 0.03, (1500, 1))); res["sphere"] = check("sphere, near the surface", Vs, Fs, Ps)
    from common import design_dir, load_parts
    cap = [(V, F) for g, n, V, F in load_parts(design_dir("cad_r13_n4_s1343_1")) if g == "l1" and "J2 cap" in n][0]
    m = trimesh.Trimesh(*cap, process=False); m.merge_vertices(digits_vertex=4); m.update_faces(m.nondegenerate_faces())
    Vc, Fc = np.asarray(m.vertices, float), np.asarray(m.faces); lo, hi = Vc.min(0) - 3, Vc.max(0) + 3
    near = rng.integers(0, len(Fc), 1500); w = rng.dirichlet((1, 1, 1), 1500); Pk = np.r_[(Vc[Fc[near]] * w[..., None]).sum(1) + rng.normal(0, 1.5, (1500, 3)), lo + rng.random((1500, 3)) * (hi - lo)]
    res["part"] = check("real part (J2 cap, welded glb)", Vc, Fc, Pk)
    M = sdist.Mesh(Vc, Fc).build_grid(); idx = np.c_[[rng.integers(0, M.gn[q], 4000) for q in range(3)]].T
    Pg = M.glo + M.g * idx; gw = winding_inside(Pg, Vc, Fc); gerr = float(((M.W[idx[:, 0], idx[:, 1], idx[:, 2]] >= 1) != gw).mean())
    cerr = float(((M.winding_at(Pk) >= 1) != winding_inside(Pk, Vc, Fc)).mean())
    md, _ = M.max_depth(Pk, 0.15); md_ref = float(max(0.0, -sdist.signed_distance(Pk, Vc, Fc).min()))
    print(f"  winding grid (g {M.g:.2f} mm): nodes wrong {100 * gerr:.2f}%; points (grid + segment crossings) wrong {100 * cerr:.2f}%; "
          f"max depth {md:.4f} vs exact {md_ref:.4f} mm", flush=True)
    res["grid"] = (gerr + cerr, 0.0, abs(md - md_ref))
    res["part raw"] = check("same part, RAW glb (unwelded; Mesh welds)", *cap, Pk)

    def open_case(name, V, F, P):
        """open mesh: truth = generalized winding number > 0.5 where it is clear (|w - round(w)| < 0.25; next to a hole
        inside / outside is not defined); x-ray grid alone vs the x / y / z majority (+ GWN where the rays disagree)"""
        w = sdist.winding_number(P, V, F); clear = np.abs(w - np.rint(w)) < 0.25; truth = w > 0.5
        M3 = sdist.Mesh(V, F).build_grid(); M1 = sdist.Mesh(V, F).build_grid(axes=(0,))
        e1 = float(((M1.winding_at(P) >= 1) != truth)[clear].mean()); e3 = float(((M3.winding_at(P) >= 1) != truth)[clear].mean())
        print(f"{name:40s} {len(P):5d} pts ({100 * truth.mean():4.1f}% in, {100 * (~clear).mean():.1f}% next to a hole, not counted; "
              f"closed {M3.closed}): x-rays only wrong {100 * e1:.2f}%, x/y/z majority + GWN wrong {100 * e3:.2f}%", flush=True)
        return e3, e1, 0.0
    keep = np.setdiff1d(np.arange(len(Fs)), [0, 97, 211, 640])                 # 4 holes of one ~11 mm facet each
    Po = np.r_[Ps, rng.uniform(-55, 55, (1500, 3))]; res["open sphere"] = open_case("sphere with 4 holes", Vs, Fs[keep], Po)
    bot = [(V, F) for g, n, V, F in load_parts(design_dir("cad_r13_n3_s1331_0")) if n.startswith("BOTTOM")][0]
    Vo, Fo = bot; lo, hi = Vo.min(0) - 3, Vo.max(0) + 3; near = rng.integers(0, len(Fo), 1500); w = rng.dirichlet((1, 1, 1), 1500)
    Pq = np.r_[(Vo[Fo[near]] * w[..., None]).sum(1) + rng.normal(0, 1.5, (1500, 3)), lo + rng.random((1500, 3)) * (hi - lo)]
    res["open part"] = open_case("open real part (3R BOTTOM + rail)", Vo, Fo, Pq)
    import body_pose as BP
    V = BP.posed(dict(plane=124, elev=32, axial=-79, flex=122, pron=0)); F = BP.F                 # the R2 judge's worst pose (Wash opposite shoulder)
    near = rng.integers(0, len(F), 1500); w = rng.dirichlet((1, 1, 1), 1500)
    Pb = (V[F[near]] * w[..., None]).sum(1) + rng.normal(0, 2.0, (1500, 3))
    res["body"] = check("posed body (Wash, the R2 worst pose)", V, F, Pb, dist=False)
    t0 = time.time(); Mb = sdist.Mesh(V, F, 2.0).build_grid(1.0, Pb.min(0) - 3, Pb.max(0) + 3); wb = Mb.winding_at(Pb) >= 1; tb = time.time() - t0
    berr = float((wb != winding_inside(Pb, V, F)).mean()); wmax = int(Mb.W.max())
    print(f"  body winding grid + segment crossings (the R2 / R10 inside test): wrong {100 * berr:.2f}% vs the generalized winding number "
          f"(grid max winding {wmax}: self-overlap), {tb:.0f}s", flush=True)
    res["body winding"] = (berr, 0.0, 0.0)
    bad = [k for k, (n, o, d) in res.items() if (n > 0.002 and k != "body") or d > 1e-6]
    print("PASS (body: the pseudo-normal sign is only reported, the mesh self-intersects; R2 uses the winding number)" if not bad else f"FAIL: {bad}")
