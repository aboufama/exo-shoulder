"""Common quick benchmark for mechanism CONCEPTS (the wide-tree stage before any GPU search), so different families
are compared on the same body, the same poses and the same two numbers. Idealised geometry is fine here (no CAD):
a concept supplies, per pose, the 3-D sample points of its metal (skin-facing surfaces at their real height, hubs at
their real size and stack) or None when it cannot take the pose (chain does not close / joint limit / self-collision).

    import sys; sys.path.insert(0, "tools"); import concept_bench as CB
    B = CB.Bench(n_clip=60, n_ws=160)                 # poses: fit-clip frames (held-out clips excluded) + everyday workspace
    for i, pose in enumerate(B.poses):                # pose = dict(plane, elev, axial, flex, pron) (deg), + B.kind[i] 'clip'/'ws'
        P = my_concept_metal_points(pose, B.frames(i))   # (k, 3) mm in the thorax frame, or None
        B.record(i, P)
    print(B.report())                                  # reach (share of workspace poses taken), follow (share of clip frames
                                                       # taken), in-band 2-14 / 2-10 (share of metal samples), contact (any < 0)
    # sweeps: B.reset() between configurations; B.dist(i, P) also takes a batch (m, k, 3) -> (m, k)
Frame (pipeline/avg/body_pose.py): thorax mm, x anterior, y up, z right, origin = right GH centre (the trunk moves by
-lift with elevation, the arm rotates about GH). B.frames(i) gives the humerus / forearm rotation (H, F) and the
scapula rotation S of pose i, so a concept can attach parts to the upper arm or to the scapula. The skin of pose i is
B.skin(i) (vertices V, faces F of the rig's posed render skin) and B.dist(i, P) the signed distance of points P to it
(< 0 = inside the body). B.clip_order() gives, per clip, the bench indices of its frames in time order (to check that
joint values stay continuous between consecutive frames: a branch flip is a frame not followed).

SPEED (2026-10-15). Three paths, same numbers:
  * FAST (default when the cache exists): per pose a precomputed signed-distance grid (4 mm voxels, int8 at 0.25 mm,
    box +-260 mm around GH, exact values within ~45 mm of the skin, clamped to +-31.75 mm beyond), trilinear
    interpolation; points outside the box fall back to the exact path. Build once: python3 tools/concept_bench.py
    --build 60 160 [--jobs 3] (cache in .cache/concept_bench/, shared read-only by every process via np.memmap).
  * EXACT-FAST (no cache, or CB_EXACT=1): libigl - exact unsigned distance to the posed skin (AABB tree on the skin
    within 340 mm of GH, which holds the closest point of anything within 260 mm) + the fast generalised winding number
    on the whole closed skin for the sign (inside = winding > 0.5, so self-overlapping body parts count as inside).
  * the original judge/sdist.py Mesh (CB_SDIST=1): ~1500x slower, kept for reference.
  Validation: python3 tools/concept_bench.py --validate (fast vs exact, numbers in the cache's meta.json).
Metrics (the judges' definitions, simplified):
  reach   = share of everyday-workspace poses the concept takes with no metal inside the body (R16's idea);
  follow  = share of fit-clip frames taken (R3's idea);
  inband14 / inband10 = over the clip frames taken, the share of metal sample points whose distance to the skin is
            2-14 mm / 2-10 mm (a metal-centric proxy of R1: sample the skin-facing surfaces evenly, ~1 point / 4 mm2);
  contact = share of taken poses with any metal point < 0 mm (inside the body) - those poses count as NOT taken.
  gap     = 100*(max(0, .90-inband14) + max(0, .95-follow) + max(0, .90-reach)) + 100*contact (lower is better).
Held-out clips (Wave, Walking) are never used here.
"""
import base64, gzip, hashlib, io, json, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "pipeline", "avg")); sys.path.insert(0, os.path.join(REPO, "judge"))
import body_pose as BP                                      # noqa: E402

FIT = json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["fit"]
CACHE = os.path.join(REPO, ".cache", "concept_bench")
H_GRID, HALF, Q = 4.0, 260.0, 0.25                          # voxel mm, box half-size mm, int8 step mm (+-31.75 mm)
R_SUB = 340.0                                               # skin kept for the unsigned-distance tree (mm from GH)


def gap_of(inband14, follow, reach, contact=0.0):
    return round(100 * (max(0.0, .90 - inband14) + max(0.0, .95 - follow) + max(0.0, .90 - reach)) + 100 * contact, 2)


class _Exact:
    """exact signed distance to one posed skin with libigl (unsigned on the shoulder-region submesh, sign from the
    fast winding number of the whole closed skin)"""
    def __init__(self, V):
        import igl
        self.igl = igl; self.V = np.ascontiguousarray(V, float); self.F = np.ascontiguousarray(BP.F, np.int64)
        keep = np.linalg.norm(self.V, axis=1) < R_SUB; fk = keep[self.F].any(1)
        self.Fs = self.F[fk]

    def __call__(self, P):
        P = np.ascontiguousarray(P, float).reshape(-1, 3)
        if not len(P): return np.zeros(0)
        far = np.linalg.norm(P, axis=1) > HALF * 1.7
        U = np.empty(len(P))
        if (~far).any(): U[~far] = self.igl.signed_distance(P[~far], self.V, self.Fs, sign_type=self.igl.SIGNED_DISTANCE_TYPE_UNSIGNED)[0]
        if far.any(): U[far] = self.igl.signed_distance(P[far], self.V, self.F, sign_type=self.igl.SIGNED_DISTANCE_TYPE_UNSIGNED)[0]
        W = self.igl.fast_winding_number(self.V, self.F, P)
        return np.where(W > 0.5, -np.abs(U), np.abs(U))


def _poses_all():
    Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(REPO, "pipeline", "conformal", "band_poses_wsf.b64")).read()))))
    return Z


def _select(n_clip, n_ws):
    Z = _poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; P = Z["POSE"]
    fit_ids = [names.index(n) for n in FIT]; ws_id = names.index("Workspace (envelope)")
    clip_idx = np.nonzero(np.isin(cid, fit_ids))[0]; ws_idx = np.nonzero(cid == ws_id)[0]
    clip_idx = clip_idx[np.linspace(0, len(clip_idx) - 1, min(n_clip, len(clip_idx))).round().astype(int)]
    ws_idx = ws_idx[np.linspace(0, len(ws_idx) - 1, min(n_ws, len(ws_idx))).round().astype(int)]
    idx = np.r_[clip_idx, ws_idx]
    return idx, names, cid, P


def _key(idx):
    return hashlib.sha1((",".join(map(str, idx)) + f"|{H_GRID}|{HALF}|{Q}|v1").encode()).hexdigest()[:12]


class Bench:
    def __init__(self, n_clip=110, n_ws=360, seed=0):
        idx, names, cid, P = _select(n_clip, n_ws)
        self.idx = idx; nc = int(np.isin(cid[idx], [names.index(n) for n in FIT]).sum())
        self.kind = ["clip"] * nc + ["ws"] * (len(idx) - nc)
        self.clip = [names[c] for c in cid[self.idx]]
        self.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in P[self.idx]]
        self.res = [None] * len(self.idx); self._skin = {}; self._ex = {}; self._frames = {}
        self.key = _key(self.idx); self.grid = None; self.mode = "sdist" if os.environ.get("CB_SDIST") == "1" else "exact"
        d = os.path.join(CACHE, self.key)
        if os.environ.get("CB_EXACT") != "1" and self.mode != "sdist" and os.path.exists(os.path.join(d, "meta.json")):
            self.meta = json.load(open(os.path.join(d, "meta.json")))
            self.grid = np.load(os.path.join(d, "grid.npy"), mmap_mode="r")
            self._V = np.load(os.path.join(d, "skins.npy"), mmap_mode="r") if os.path.exists(os.path.join(d, "skins.npy")) else None
            self.mode = "fast"

    # ---- poses -------------------------------------------------------------------------------------------------
    def frames(self, i):
        """dict(T=(R, t) thorax, S=(R, t) scapula, H=(R, t) humerus, F=(R, t) forearm, lift) of pose i (body_pose.segs)"""
        if i not in self._frames:
            r = BP._rig(); (T, S, H, Fa, Pr), lift = BP.segs(r.L, r.s, self.poses[i]); self._frames[i] = dict(T=T, S=S, H=H, F=Fa, lift=lift)
        return self._frames[i]

    def clip_order(self):
        """{clip name: [bench indices in time order]} for the clip frames (the bench samples frames evenly in file order)"""
        out = {}
        for j, (k, c) in enumerate(zip(self.kind, self.clip)):
            if k == "clip": out.setdefault(c, []).append(j)
        return out

    def _verts(self, i):
        if getattr(self, "_V", None) is not None: return np.asarray(self._V[i], float)
        if i not in self._skin:
            if len(self._skin) > 24: self._skin.clear()
            self._skin[i] = BP.posed(self.poses[i])
        return self._skin[i]

    def skin(self, i):
        return self._verts(i), BP.F

    # ---- distance ----------------------------------------------------------------------------------------------
    def _exact(self, i, P):
        if self.mode == "sdist":
            from sdist import Mesh
            if i not in self._ex:
                if len(self._ex) > 8: self._ex.clear()
                self._ex[i] = Mesh(self._verts(i), BP.F, 2.0).build_grid(2.5, np.array([-320.0] * 3), np.array([320.0] * 3))
            M = self._ex[i]; d = np.abs(M.closest(P)[0]); return np.where(M.winding_at(P) >= 1, -d, d)
        if i not in self._ex:
            if len(self._ex) > 24: self._ex.clear()
            self._ex[i] = _Exact(self._verts(i))
        return self._ex[i](P)

    def dist(self, i, P):
        """signed distance (mm) of points P (k, 3) - or a batch (m, k, 3) - to the posed skin of pose i; < 0 = inside"""
        P = np.asarray(P, float); shp = P.shape[:-1]; P = P.reshape(-1, 3)
        if self.grid is None: return self._exact(i, P).reshape(shp)
        g = (P + HALF) / H_GRID; n = self.grid.shape[1]
        inside = np.all((g >= 0) & (g <= n - 1 - 1e-9), axis=1)
        out = np.empty(len(P))
        if inside.any():
            gi = g[inside]; i0 = np.floor(gi).astype(np.int64); f = gi - i0; G = self.grid[i]
            x0, y0, z0 = i0.T; x1, y1, z1 = x0 + 1, y0 + 1, z0 + 1; fx, fy, fz = f.T
            c = lambda a, b, cc: G[a, b, cc].astype(np.float32)
            v = (c(x0, y0, z0) * (1 - fx) * (1 - fy) * (1 - fz) + c(x1, y0, z0) * fx * (1 - fy) * (1 - fz) + c(x0, y1, z0) * (1 - fx) * fy * (1 - fz)
                 + c(x0, y0, z1) * (1 - fx) * (1 - fy) * fz + c(x1, y1, z0) * fx * fy * (1 - fz) + c(x1, y0, z1) * fx * (1 - fy) * fz
                 + c(x0, y1, z1) * (1 - fx) * fy * fz + c(x1, y1, z1) * fx * fy * fz)
            out[inside] = v * Q
        if (~inside).any(): out[~inside] = self._exact(i, P[~inside])
        return out.reshape(shp)

    # ---- scoring -----------------------------------------------------------------------------------------------
    def reset(self):
        self.res = [None] * len(self.idx)

    def record(self, i, P):
        """P: (k, 3) metal sample points in the thorax frame for pose i, or None (pose not taken)"""
        if P is None or not len(P): self.res[i] = None; return None
        d = self.dist(i, P); self.res[i] = d; return d

    def report(self):
        ws = [j for j, k in enumerate(self.kind) if k == "ws"]; cl = [j for j, k in enumerate(self.kind) if k == "clip"]
        ok = lambda j: self.res[j] is not None and float(np.min(self.res[j])) >= 0.0
        taken = [j for j in cl if ok(j)]; d = np.concatenate([self.res[j] for j in taken]) if taken else np.zeros(0)
        nz = [j for j in range(len(self.kind)) if self.res[j] is not None]
        r = dict(reach=round(float(np.mean([ok(j) for j in ws])), 4), follow=round(float(np.mean([ok(j) for j in cl])), 4),
                 inband14=round(float(np.mean((d >= 2) & (d <= 14))), 4) if len(d) else 0.0,
                 inband10=round(float(np.mean((d >= 2) & (d <= 10))), 4) if len(d) else 0.0,
                 contact=round(float(np.mean([float(np.min(self.res[j])) < 0 for j in nz])), 4) if nz else 0.0,
                 poses=dict(clip=len(cl), ws=len(ws)), mode=self.mode)
        r["gap"] = gap_of(r["inband14"], r["follow"], r["reach"], r["contact"]); return r


# ---- cache build -------------------------------------------------------------------------------------------------
def _grid_pose(args):
    pose, path, j, n = args
    V = BP.posed(pose); ex = _Exact(V)
    ax = -HALF + H_GRID * np.arange(n)
    hc = 4; axc = ax[::hc]                                   # coarse grid (16 mm) on the same lattice: where to compute
    Xc = np.stack(np.meshgrid(axc, axc, axc, indexing="ij"), -1).reshape(-1, 3)
    dc = ex(Xc).reshape(len(axc), len(axc), len(axc))
    G = np.empty((n, n, n), np.int8)
    from scipy.interpolate import RegularGridInterpolator
    near = RegularGridInterpolator((axc, axc, axc), np.abs(dc), bounds_error=False, fill_value=None)
    sgn = RegularGridInterpolator((axc, axc, axc), dc, method="nearest", bounds_error=False, fill_value=None)
    X = np.stack(np.meshgrid(ax, ax, ax, indexing="ij"), -1).reshape(-1, 3)
    m = near(X) < 45.0
    d = np.empty(len(X)); d[m] = ex(X[m]); d[~m] = np.where(sgn(X[~m]) < 0, -99.0, 99.0)
    G[...] = np.clip(np.round(d / Q), -127, 127).astype(np.int8).reshape(n, n, n)
    mm = np.load(path, mmap_mode="r+"); mm[j] = G; mm.flush(); del mm
    return j, float(m.mean()), V.astype(np.float32)


def build(n_clip, n_ws, jobs=2):
    from multiprocessing import Pool
    B = Bench(n_clip, n_ws); B.grid = None
    d = os.path.join(CACHE, B.key); os.makedirs(d, exist_ok=True)
    if os.path.exists(os.path.join(d, "meta.json")): print("cache exists", d); return d
    n = int(round(2 * HALF / H_GRID)) + 1; N = len(B.poses)
    tmp = os.path.join(d, "grid.tmp.npy"); np.lib.format.open_memmap(tmp, mode="w+", dtype=np.int8, shape=(N, n, n, n)).flush()
    t = time.time(); Vs = [None] * N; fr = []
    with Pool(jobs) as pool:
        for j, frac, V in pool.imap_unordered(_grid_pose, [(B.poses[j], tmp, j, n) for j in range(N)]):
            Vs[j] = V; fr.append(frac)
            if len(fr) % 20 == 0: print(f"  {len(fr)}/{N} poses, {time.time() - t:.0f} s", flush=True)
    np.save(os.path.join(d, "skins.tmp.npy"), np.stack(Vs)); os.replace(os.path.join(d, "skins.tmp.npy"), os.path.join(d, "skins.npy"))
    os.replace(tmp, os.path.join(d, "grid.npy"))
    meta = dict(n_clip=n_clip, n_ws=n_ws, poses=N, h=H_GRID, half=HALF, q=Q, exact_share=float(np.mean(fr)), secs=round(time.time() - t, 1),
                created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    json.dump(meta, open(os.path.join(d, "meta.tmp.json"), "w"), indent=1); os.replace(os.path.join(d, "meta.tmp.json"), os.path.join(d, "meta.json"))
    print("built", d, meta); return d


def validate(n_clip, n_ws, n_poses=20):
    B = Bench(n_clip, n_ws)
    if B.grid is None: print("no cache for", n_clip, n_ws); return
    rng = np.random.default_rng(1); errs = []; sg = []; t_fast = t_ex = 0.0
    for i in rng.choice(len(B.poses), min(n_poses, len(B.poses)), replace=False):
        V = np.asarray(B._V[i], float); near = V[np.linalg.norm(V, axis=1) < 240]
        nrm = near - near.mean(0); P = near[rng.choice(len(near), 1500)] + rng.normal(0, 1, (1500, 3)) * rng.uniform(0, 18, (1500, 1))
        t = time.time(); a = B.dist(i, P); t_fast += time.time() - t
        t = time.time(); b = B._exact(i, P); t_ex += time.time() - t
        sel = (np.abs(b) <= 20); errs.append(np.abs(a - b)[sel]); far = np.abs(b) > 1; sg.append((np.sign(a) == np.sign(b))[far])
    e = np.concatenate(errs); s = np.concatenate(sg)
    out = dict(points=int(len(e)), max_err_0_20mm=round(float(e.max()), 3), p99=round(float(np.percentile(e, 99)), 3), mean=round(float(e.mean()), 4),
               sign_agree_beyond_1mm=round(float(s.mean()), 5), fast_s=round(t_fast, 2), exact_s=round(t_ex, 2))
    d = os.path.join(CACHE, B.key); m = json.load(open(os.path.join(d, "meta.json"))); m["validation"] = out
    json.dump(m, open(os.path.join(d, "meta.tmp.json"), "w"), indent=1); os.replace(os.path.join(d, "meta.tmp.json"), os.path.join(d, "meta.json"))
    print(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--build":
        jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2
        build(int(a[1]), int(a[2]), jobs)
    elif a and a[0] == "--validate":
        validate(int(a[1]) if len(a) > 1 else 60, int(a[2]) if len(a) > 2 else 160)
    else:                                                    # self-check: a shell 8 mm off the rest skin around the shoulder, fixed to the thorax
        B = Bench(n_clip=20, n_ws=20)
        V0 = BP.posed(B.poses[0]); sel = np.linalg.norm(V0, axis=1) < 90
        for i in range(len(B.poses)):
            Vi = B._verts(i); N = Vi[sel] / (np.linalg.norm(Vi[sel], axis=1, keepdims=True) + 1e-9)
            B.record(i, Vi[sel][::7] + 8.0 * N[::7])
        print(B.report())
