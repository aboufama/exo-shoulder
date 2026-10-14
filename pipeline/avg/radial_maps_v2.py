"""Radial skin maps from the current body rig (body_pose.py): trunk maps AND arm maps per elevation bin.

Same map semantics as radial_maps.py (r1 first exit from the GH centre, r2 re-entry, r1c / r2c the band >= 3 mm
from the skin, 0.25 deg pixels, lat -75..90), but:
  - skin posed with body_pose.posed (centre-of-rotation skinning, muscle bulging) instead of the legacy 2-weight blend
  - poses are twist-free (plane 30, elevation e, ISB axial -30)
  - the arm skin gets a map per elevation bin, in the canonical humerus frame (x_c = Rh^T x), so the deltoid
    bulge with elevation is in the maps
Also writes the GPU payload (posed vertices per bin, faces, arm mask, Rh per bin) for conformal/gpu.

    python3 radial_maps_v2.py      -> radial_maps_v2.npz, ../conformal/skin_posed_v2.b64
"""
import base64, gzip, io, json, math, os, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import minimum_filter, uniform_filter
import body_pose as BP

RES = 0.25; NW, NH = int(360 / RES), int(180 / RES); C = 3.0; KD_WORKERS = 4
LAT_LO, LAT_HI = -75.0, 90.0
ELEVS = list(range(0, 181, 15)); PLANE = 30.0
D2R = math.pi / 180

def Rh_of(plane, elev, axial):
    return BP.rot([0, 1, 0], plane * D2R) @ BP.rot([1, 0, 0], -elev * D2R) @ BP.rot([0, 1, 0], axial * D2R)

def samples(P, faces, R_MAX=480.0, seed=0):
    A, B, Cc = P[faces[:, 0]], P[faces[:, 1]], P[faces[:, 2]]
    rc = np.linalg.norm((A + B + Cc) / 3, axis=1); keep = rc < R_MAX; A, B, Cc, rc = A[keep], B[keep], Cc[keep], rc[keep]
    area = 0.5 * np.linalg.norm(np.cross(B - A, Cc - A), axis=1); spacing = np.maximum(0.25, rc * math.radians(RES) * 0.6)
    n = np.clip(np.ceil(area / spacing ** 2 * 2.0), 1, 4000).astype(int); out = []
    for lo in range(0, len(A), 20000):
        sl = slice(lo, lo + 20000); nn = n[sl]; idx = np.repeat(np.arange(len(nn)), nn)
        u = np.random.default_rng(seed + lo).random((len(idx), 2)); f = u.sum(1) > 1; u[f] = 1 - u[f]
        out.append(A[sl][idx] + u[:, :1] * (B[sl][idx] - A[sl][idx]) + u[:, 1:] * (Cc[sl][idx] - A[sl][idx])); out += [A[sl], B[sl], Cc[sl]]
    return np.concatenate(out)

def pix(Q):
    r = np.linalg.norm(Q, axis=1); lon = np.arctan2(Q[:, 2], Q[:, 0]); lat = np.arcsin(np.clip(Q[:, 1] / r, -1, 1))
    j = np.clip(((lon + math.pi) / math.radians(RES)).astype(int), 0, NW - 1); i = np.clip(((lat + math.pi / 2) / math.radians(RES)).astype(int), 0, NH - 1)
    return r, i, j

def ray_maps(P, faces, c=C):
    """r1, r2, r1c, r2c full maps (rows outside LAT_LO..LAT_HI: r1c 0 / r2c inf)"""
    Q = samples(P, faces); r, i, j = pix(Q)
    r1 = np.full((NH, NW), np.inf, np.float32); np.minimum.at(r1, (i, j), r.astype(np.float32))
    fin = np.isfinite(r1); mn = minimum_filter(np.where(fin, r1, 1e9), size=3, mode="wrap")
    hole = ~fin & (uniform_filter(fin.astype(float), size=3, mode="wrap") > 0.5); r1[hole] = mn[hole]
    beyond = r > r1[i, j] + 4.0
    r2 = np.full((NH, NW), np.inf, np.float32); np.minimum.at(r2, (i[beyond], j[beyond]), r[beyond].astype(np.float32))
    tree = cKDTree(Q); rows = np.arange(int((LAT_LO + 90) / RES), int((LAT_HI + 90) / RES))
    lat = (rows + 0.5) * math.radians(RES) - math.pi / 2; lon = (np.arange(NW) + 0.5) * math.radians(RES) - math.pi
    LA, LO = np.meshgrid(lat, lon, indexing="ij"); U = np.stack([np.cos(LA) * np.cos(LO), np.sin(LA), np.cos(LA) * np.sin(LO)], -1).reshape(-1, 3)
    R1 = r1[rows].ravel(); R2 = r2[rows].ravel(); steps = np.arange(0.0, 14.01, 0.25)
    def march(base, sign):
        idx = np.nonzero(np.isfinite(base))[0]; done = np.zeros(len(idx), bool); res = base[idx] + sign * 14.0
        for s in steps:
            td = ~done
            if not td.any(): break
            pts = U[idx[td]] * (base[idx[td]] + sign * s)[:, None]; d, _ = tree.query(pts, workers=KD_WORKERS)
            h = d >= c; k = np.nonzero(td)[0][h]; res[k] = base[idx[k]] + sign * s; done[k] = True
        return idx, res
    r1c = np.zeros_like(R1); r2c = np.full_like(R2, np.inf)
    ii, rr = march(R1, +1); r1c[ii] = rr; ii, rr = march(R2, -1); r2c[ii] = rr
    f1 = np.zeros((NH, NW), np.float32); f2 = np.full((NH, NW), np.inf, np.float32)
    f1[rows] = r1c.reshape(len(rows), NW); f2[rows] = r2c.reshape(len(rows), NW)
    return r1, r2, f1, f2

if __name__ == "__main__":
    t0 = time.time(); F = BP.F; ARMF = BP.ARMF
    out = {k: [] for k in ("t_r1", "t_r2", "t_r1c", "t_r2c", "a_r1", "a_r2", "a_r1c", "a_r2c")}
    payload = {"verts": {}, "rh": {}}
    for e in ELEVS:
        pose = dict(plane=PLANE, elev=e, axial=-PLANE, flex=30, pron=0); X = BP.posed(pose); Rh = Rh_of(PLANE, e, -PLANE)
        payload["verts"][f"e{e}"] = base64.b64encode(np.round(X * 10).astype(np.int16).tobytes()).decode(); payload["rh"][f"e{e}"] = Rh.tolist()
        for k, v in zip(("t_r1", "t_r2", "t_r1c", "t_r2c"), ray_maps(X, F[~ARMF])): out[k].append(v)
        for k, v in zip(("a_r1", "a_r2", "a_r1c", "a_r2c"), ray_maps(X @ Rh, F[ARMF])): out[k].append(v)   # arm skin in the canonical humerus frame
        print(f"elev {e}: {time.time() - t0:.0f}s", flush=True)
    out = {k: np.stack(v) for k, v in out.items()}
    np.savez_compressed(os.path.join(os.path.dirname(os.path.abspath(__file__)), "radial_maps_v2.npz"), res=RES, elevs=np.array(ELEVS), clear=C, plane=PLANE, **out)
    payload["idx"] = base64.b64encode(F.astype(np.uint32).tobytes()).decode(); payload["armf"] = base64.b64encode(ARMF.astype(np.uint8).tobytes()).decode()
    payload["elevs"] = ELEVS
    raw = gzip.compress(json.dumps(payload).encode())
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "conformal", "skin_posed_v2.b64"), "w").write(base64.b64encode(raw).decode())
    print("saved", {k: v.shape for k, v in out.items()}, f"payload {len(raw) / 1e6:.1f} MB gz", f"{time.time() - t0:.0f}s")
