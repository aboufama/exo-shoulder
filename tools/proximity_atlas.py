"""Proximity atlas: where can RIGID metal ride 2-14 mm from the skin, and how must it move to do so?

Raw material: the posed skin of every bench pose (tools/concept_bench.py, same grid distance as every screened number).
No mechanism is modelled. For a rigid part that rotates about the GH centre with a frame F (per pose a rotation F_i),
a point of the part in direction u (frame coordinates) sits at radius rho(u) = its lowest legal height (2 mm clear of
the skin in EVERY bench pose, the K3 rule: first radius with distance >= 2 mm and nothing inside for 15 mm beyond).
Its CEILING is the share of fit-clip poses in which that point is 2-14 mm from the skin (exact bench distance). A
skin-fitted underside can do no better than the ceiling on these poses; a real mechanism does worse (hubs, closure,
collisions). Frames compared:
  S        fixed to the scapula (a base part, J1's hub)
  H        fixed to the humerus (an arm part, the arm-end hub)
  swing t  S * swing(S^T H)^t: rotates by the fraction t of the arm's pointing motion, no humeral twist (t = 0 .. 1)
  geo t    the geodesic fraction t of the full rotation S -> H (pointing and twist)
Output: per frame and direction, ceiling, radial motion (max - min of the skin height under the point), rho; summaries
per region; the best fraction per direction (which intermediate rotation keeps that skin quiet).

    python3 tools/proximity_atlas.py heights      # skin height per pose x direction -> .cache/proximity_atlas/heights.npz
    python3 tools/proximity_atlas.py ceilings     # frames S, H, swing/geo fractions -> docs/research/proximity_atlas.json
"""
import json, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                                   # noqa: E402

OUT = os.path.join(REPO, ".cache", "proximity_atlas"); os.makedirs(OUT, exist_ok=True)
RES = 2.0                                                                    # direction grid (deg), thorax frame
LON = np.deg2rad(np.arange(-180, 180, RES) + RES / 2); LAT = np.deg2rad(np.arange(-90, 90, RES) + RES / 2)
T0, T1, DT, CLEAR, RUN = 10.0, 220.0, 2.0, 2.0, 15.0                         # march (mm), K3 clearance and run length


def dirs_of(lat, lon):
    """unit directions (thorax: x anterior, y up, z right) for lat/lon arrays (rad)"""
    return np.stack([np.cos(lat) * np.cos(lon), np.sin(lat), np.cos(lat) * np.sin(lon)], -1)


def heights(B):
    """h[i, a, o]: K3 lowest legal radius along thorax direction (LAT[a], LON[o]) in pose i; nan = no skin within T1"""
    la, lo = np.meshgrid(LAT, LON, indexing="ij"); D = dirs_of(la, lo).reshape(-1, 3)
    t = np.arange(T0, T1 + 1e-9, DT); P = D[:, None, :] * t[None, :, None]           # (n, s, 3)
    k = int(round(RUN / DT)) + 1
    H = np.full((len(B.idx), len(D)), np.nan, np.float32)
    for i in range(len(B.idx)):
        d = B.dist(i, P)                                                              # (n, s)
        # min of d over the next k samples (incl. this one): nothing inside the body for RUN mm beyond
        pad = np.concatenate([d, np.full((len(D), k), 99.0)], 1)
        run = np.min(np.stack([pad[:, j:j + d.shape[1]] for j in range(k)], 0), 0)
        ok = (d >= CLEAR) & (run >= 0.0)
        j = np.argmax(ok, 1); has = ok[np.arange(len(D)), j]
        # refine: linear crossing of CLEAR between sample j-1 and j
        jm = np.maximum(j - 1, 0); d0 = d[np.arange(len(D)), jm]; d1 = d[np.arange(len(D)), j]
        f = np.where((j > 0) & (d0 < CLEAR) & (d1 > d0), (CLEAR - d0) / np.maximum(d1 - d0, 1e-6), 1.0)
        h = t[jm] + f * (t[j] - t[jm])
        H[i] = np.where(has, h, np.nan)
        if i % 20 == 0: print(f"  heights {i}/{len(B.idx)}", flush=True)
    return H.reshape(len(B.idx), len(LAT), len(LON))


def lookup(H, i, W):
    """skin height of pose i along thorax directions W (..., 3), nearest grid cell"""
    lat = np.arcsin(np.clip(W[..., 1], -1, 1)); lon = np.arctan2(W[..., 2], W[..., 0])
    a = np.clip(((lat + np.pi / 2) / np.deg2rad(RES)).astype(int), 0, len(LAT) - 1)
    o = (((lon + np.pi) / np.deg2rad(RES)).astype(int)) % len(LON)
    return H[i, a, o]


def rot_log(R):
    """axis-angle vector of rotation matrices R (..., 3, 3)"""
    c = np.clip((np.trace(R, axis1=-2, axis2=-1) - 1) / 2, -1, 1); th = np.arccos(c)
    v = np.stack([R[..., 2, 1] - R[..., 1, 2], R[..., 0, 2] - R[..., 2, 0], R[..., 1, 0] - R[..., 0, 1]], -1)
    s = np.sin(th); k = np.where(s[..., None] > 1e-9, v / (2 * np.maximum(s[..., None], 1e-12)), 0.0)
    return k * th[..., None]


def rot_exp(w):
    th = np.linalg.norm(w, axis=-1, keepdims=True); k = w / np.maximum(th, 1e-12); th = th[..., 0]
    K = np.zeros(w.shape[:-1] + (3, 3)); K[..., 0, 1], K[..., 0, 2], K[..., 1, 2] = -k[..., 2], k[..., 1], -k[..., 0]
    K[..., 1, 0], K[..., 2, 0], K[..., 2, 1] = k[..., 2], -k[..., 1], k[..., 0]
    I = np.broadcast_to(np.eye(3), K.shape)
    return I + np.sin(th)[..., None, None] * K + (1 - np.cos(th))[..., None, None] * (K @ K)


def swing_of(R, axis=np.array([0.0, -1.0, 0.0])):
    """swing part of R: the minimal rotation taking `axis` (the humerus long axis, down the arm) to R @ axis"""
    b = R @ axis; c = float(np.clip(axis @ b, -1, 1)); v = np.cross(axis, b); s = np.linalg.norm(v)
    return rot_exp((v / max(s, 1e-12)) * np.arctan2(s, c)) if s > 1e-9 else np.eye(3)


def frames_for(B, kind, t=None):
    """per-pose rotation of a part frame (len(B.idx), 3, 3)"""
    S = np.array([B.frames(i)["S"][0] for i in range(len(B.idx))]); Hm = np.array([B.frames(i)["H"][0] for i in range(len(B.idx))])
    if kind == "S": return S
    if kind == "H": return Hm
    rel = np.einsum("pji,pjk->pik", S, Hm)                                         # S^T H
    if kind == "geo": return S @ rot_exp(t * rot_log(rel))
    if kind == "swing": return S @ np.array([rot_exp(t * rot_log(swing_of(r))) for r in rel])
    raise ValueError(kind)


def ceilings(B, H, F, U, clip_only_rho=False):
    """for part directions U (n, 3) in frame F: rho, ceiling (clip poses), motion, contact share, skin share"""
    n = len(U); P_all = len(B.idx); clip = np.array([k == "clip" for k in B.kind])
    W = np.einsum("pij,nj->pni", F, U)                                               # (p, n, 3) thorax dirs
    h = np.stack([lookup(H, i, W[i]) for i in range(P_all)], 0)                       # (p, n)
    use = clip if clip_only_rho else np.ones(P_all, bool)
    hm = np.where(np.isfinite(h) & use[:, None], h, -np.inf); rho = hm.max(0) + 0.5
    skin = np.isfinite(h)
    rho = np.where(np.isfinite(rho), rho, np.nan)
    d = np.full((P_all, n), np.nan)
    ok = np.isfinite(rho)
    for i in range(P_all):
        if ok.any(): d[i, ok] = B.dist(i, W[i, ok] * rho[ok, None])
    # one correction pass: raise each point by its worst deficit below the 2 mm clearance, then re-measure
    lim = np.where(use[:, None], d, np.inf); deficit = np.clip(CLEAR - np.nanmin(lim, 0), 0, None)
    deficit = np.where(np.isfinite(deficit), deficit, 0.0); rho = rho + deficit
    for i in range(P_all):
        if ok.any(): d[i, ok] = B.dist(i, W[i, ok] * rho[ok, None])
    inb = (d >= 2) & (d <= 14); inb10 = (d >= 2) & (d <= 10)
    cs = clip[:, None] & skin
    ceil = np.where(cs.sum(0) > 0, (inb & cs).sum(0) / np.maximum(cs.sum(0), 1), np.nan)
    ceil10 = np.where(cs.sum(0) > 0, (inb10 & cs).sum(0) / np.maximum(cs.sum(0), 1), np.nan)
    hmin = np.where(np.isfinite(h) & use[:, None], h, np.inf).min(0)
    motion = np.where(np.isfinite(hmin) & np.isfinite(rho), rho - 0.5 - deficit - hmin, np.nan)
    contact = np.nanmean(np.where(use[:, None] & ok[None], d < 0, np.nan), 0)
    return dict(rho=rho, ceil=ceil, ceil10=ceil10, motion=motion, contact=contact, skin=skin[clip].mean(0))


def bvec(az, el):
    az, el = np.deg2rad(az), np.deg2rad(el)
    return np.stack([-np.cos(el) * np.cos(az), np.sin(el), np.cos(el) * np.sin(az)], -1)


def wdir(dl, a):
    dl, a = np.deg2rad(dl), np.deg2rad(a)
    return np.stack([np.sin(dl) * np.sin(a), -np.cos(dl), np.sin(dl) * np.cos(a)], -1)


def summary(r, mask=None):
    c = r["ceil"]; m = np.isfinite(c) & (r["skin"] >= 0.5)
    if mask is not None: m &= mask
    if not m.any(): return {}
    return dict(n=int(m.sum()), share_ceil_ge_90=round(float((c[m] >= 0.9).mean()), 4), share_ceil_ge_50=round(float((c[m] >= 0.5).mean()), 4),
                mean_ceil=round(float(c[m].mean()), 4), mean_ceil10=round(float(np.nanmean(r["ceil10"][m])), 4),
                median_motion_mm=round(float(np.nanmedian(r["motion"][m])), 2), contact_free=round(float((r["contact"][m] == 0).mean()), 4))


def main():
    a = sys.argv[1:]; B = CB.Bench(60, 160); print("bench", B.mode, len(B.idx), "poses")
    hp = os.path.join(OUT, f"heights_{B.key}_{RES:g}.npz")
    if not a or a[0] == "heights" or not os.path.exists(hp):
        t0 = time.time(); H = heights(B); np.savez_compressed(hp, H=H, LAT=LAT, LON=LON, idx=B.idx)
        print(f"heights {H.shape} in {time.time() - t0:.0f} s -> {hp}; skin present {np.isfinite(H).mean():.3f}")
        if a and a[0] == "heights": return
    H = np.load(hp)["H"]
    res = {}
    # 1) cross-check with pipeline/conformal/analysis/skin_motion_map_14.json (same parametrisations, rho over fit clips)
    A, Bq = np.meshgrid(np.arange(-180, 180, 3.0), np.arange(-30, 90, 2.0), indexing="ij"); US = bvec(A.ravel(), Bq.ravel())
    A2, B2 = np.meshgrid(np.arange(20, 161, 2.0), np.arange(-180, 180, 3.0), indexing="ij"); UH = wdir(A2.ravel(), B2.ravel())
    t0 = time.time()
    rS = ceilings(B, H, frames_for(B, "S"), US, clip_only_rho=True); rH = ceilings(B, H, frames_for(B, "H"), UH, clip_only_rho=True)
    res["crosscheck_clip_rho"] = dict(scapula=summary(rS), humerus=summary(rH),
                                      reference=dict(scapula_share_dirs_ceiling_ge_90=0.38, scapula_median_motion_mm=34.7,
                                                     humerus_share_dirs_ceiling_ge_90=0.275, humerus_median_motion_mm=30.0))
    print("crosscheck", json.dumps(res["crosscheck_clip_rho"]), f"{time.time() - t0:.0f} s", flush=True)
    # 2) every frame on one common direction set: the shoulder region seen from GH (thorax directions at rest)
    la, lo = np.meshgrid(np.deg2rad(np.arange(-40, 90, 3.0)), np.deg2rad(np.arange(-180, 180, 3.0)), indexing="ij")
    U = dirs_of(la, lo).reshape(-1, 3)
    fr = [("S", None), ("H", None)] + [("swing", t) for t in (0.25, 0.5, 0.75)] + [("geo", t) for t in (0.25, 0.5, 0.75)]
    per = {}
    for kind, t in fr:
        name = kind if t is None else f"{kind}{t:g}"; t0 = time.time()
        r = ceilings(B, H, frames_for(B, kind, t), U); per[name] = r
        res[name] = summary(r); print(name, json.dumps(res[name]), f"{time.time() - t0:.0f} s", flush=True)
    names = list(per); C = np.stack([np.nan_to_num(per[k]["ceil"], nan=-1) for k in names], 0)
    best = C.argmax(0); bestc = C.max(0); valid = per["S"]["skin"] >= 0.5
    res["best_of_frames"] = dict(share_ceil_ge_90=round(float((bestc[valid] >= 0.9).mean()), 4),
                                 mean_ceil=round(float(bestc[valid].mean()), 4),
                                 winner_share={k: round(float((best[valid] == j).mean()), 4) for j, k in enumerate(names)})
    print("best_of_frames", json.dumps(res["best_of_frames"]), flush=True)
    np.savez_compressed(os.path.join(OUT, "ceilings.npz"), U=U, names=np.array(names), C=C, valid=valid,
                        **{f"motion_{k}": per[k]["motion"] for k in names}, **{f"rho_{k}": per[k]["rho"] for k in names})
    os.makedirs(os.path.join(REPO, "docs", "research"), exist_ok=True)
    json.dump(res, open(os.path.join(REPO, "docs", "research", "proximity_atlas.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
