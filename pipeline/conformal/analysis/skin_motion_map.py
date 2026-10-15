"""Where can a rigid part ride close? For a part fixed in the humerus frame (BOTTOM's hub JN, the neck) or in the scapula
frame (the base hub J1), per direction of that frame: the radial motion of the skin under it over the fit clips' frames
(max - min of the evaluator's lower bound r1c - 1, frames with skin there) and the point ceiling - the share of frames in
which metal sitting at its lowest legal height (clear of the skin by 2 mm in every frame) is within G of the skin
(normal gap, slope-corrected as the evaluator does). A contoured underside can do no better on these clips; a flat hub
does worse. Only the fit clips (the held-out split stays out). Cached maps (.cache/maps_s1.pt), band_poses.b64.

    python3 skin_motion_map.py <cad input json> [G=14]   -> skin_motion_map_<G>.json (+ the design's own J1 / JN rows)"""
import json, math, os, sys, io, gzip, base64
import numpy as np, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "gpu")); import band_impl as BI
torch.set_num_threads(int(os.environ.get("THREADS", 2)))
SRC = json.load(open(sys.argv[1]))["results"][0]; G = float(sys.argv[2]) if len(sys.argv) > 2 else 14.0
FIT = SRC.get("fit_clips") or ["Raise overhead", "Drink from a cup", "Comb hair", "Reach a high shelf", "Wash opposite shoulder", "Reach back pocket"]
Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(HERE, "..", "band_poses.b64")).read()))), allow_pickle=False)
names = [str(x) for x in Z["NAMES"]]; keep = np.isin(np.array(names)[Z["CID"]], FIT); HG, RS = Z["HG"][keep], Z["RS"][keep]; pidx = np.nonzero(keep)[0]
M = torch.load(os.path.join(HERE, "..", "..", "..", ".cache", "maps_s1.pt")); S = BI.MH * BI.MW
if os.environ.get("FILL_HOLES", "1") == "1": import map_holes; M = map_holes.fill(M)     # the maps' pole holes (map_holes.py); FILL_HOLES=0: raw maps
def look(name, W):                                                               # W (F, N, 3) thorax dirs for frames pidx
    lon = np.arctan2(W[..., 2], W[..., 0]); lat = np.arcsin(np.clip(W[..., 1], -1, 1))
    j = np.floor((lon + math.pi) / (BI.MRES * BI.D2R)).astype(int) % BI.MW; i = np.clip(np.floor((lat - BI.LAT_LO * BI.D2R) / (BI.MRES * BI.D2R)).astype(int), 0, BI.MH - 1)
    flat = torch.from_numpy((pidx[:, None] * S + i * BI.MW + j).reshape(-1))
    return M[name].view(-1)[flat].float().numpy().reshape(W.shape[:-1])
def stats(D, frame):
    """D (N, 3) unit dirs in the part's frame -> per dir: motion (mm), ceiling share, skin share, lowest legal radius"""
    R = np.einsum("fij,fjk->fik", RS, HG) if frame == "humerus" else RS
    W = np.einsum("fij,nj->fni", R, D)
    r1, r1c, cs = look("r1", W), look("r1c", W), look("cs", W)
    sk = r1 > 1.0; LO = np.where(sk, r1c - 1.0, -np.inf); hmin = LO.max(0)
    lo_min = np.where(sk, LO, np.inf).min(0); motion = np.where(sk.any(0), hmin - lo_min, np.nan)
    cap = r1 + G / np.clip(cs, 0.35, None); inb = (hmin[None] <= cap + 1e-3) & sk
    ceil = np.where(sk.any(0), inb.sum(0) / np.maximum(sk.sum(0), 1), np.nan)
    return motion, ceil, sk.mean(0), hmin
def grid(frame):
    if frame == "humerus":                                                       # (delta from the humerus axis, azimuth) as the design's w
        A, B = np.meshgrid(np.arange(20, 161, 2.0), np.arange(-180, 180, 3.0), indexing="ij"); D = np.array([BI.w_dir(a, b) for a, b in zip(A.ravel(), B.ravel())])
    else:                                                                        # (azimuth, elevation) as the design's J1 axis b
        A, B = np.meshgrid(np.arange(-180, 180, 3.0), np.arange(-30, 90, 2.0), indexing="ij"); D = np.array([BI.bvec(a, b) for a, b in zip(A.ravel(), B.ravel())])
    return A, B, D
out = dict(G=G, fit_clips=FIT, frames=int(keep.sum()), filled_maps=os.environ.get("FILL_HOLES", "1") == "1")
for frame, own, lab in (("humerus", BI.w_dir(*SRC["w"]), "JN axis W (BOTTOM hub)"), ("scapula", BI.bvec(SRC["az"], SRC["el"]), "J1 axis b (base hub)")):
    A, B, D = grid(frame); mo, ce, sk, hm = [x.reshape(A.shape) for x in stats(D, frame)]
    o_mo, o_ce, o_sk, o_hm = [float(x[0]) for x in stats(np.array([own]), frame)]
    # a hub disc of the design's radius around a direction: the flat face sits at the max over the disc -> its ceiling
    def disc(d, r_hub=11.5, r_ref=None):
        d = np.asarray(d, float); r_ref = r_ref or float(stats(d[None], frame)[3][0])    # the disc at its own height
        t1 = np.cross(d, [0, 1, 0] if abs(d[1]) < 0.9 else [1, 0, 0]); t1 /= np.linalg.norm(t1); t2 = np.cross(d, t1)
        pts = [d]
        for rr, n in ((0.55 * r_hub, 8), (r_hub - 0.4, 16)):
            al = math.atan(rr / r_ref)
            for k in range(n): ph = 2 * math.pi * k / n; pts.append(math.cos(al) * d + math.sin(al) * (math.cos(ph) * t1 + math.sin(ph) * t2))
        P = np.array(pts); cosa = P @ d
        R = np.einsum("fij,fjk->fik", RS, HG) if frame == "humerus" else RS; W = np.einsum("fij,nj->fni", R, P)
        r1, r1c, cs = look("r1", W), look("r1c", W), look("cs", W); sk = r1 > 1.0
        face = (np.where(sk, r1c - 1.0, -np.inf) * cosa[None]).max()             # flat face (along the axis)
        cap = r1 + G / np.clip(cs, 0.35, None); inb = ((face / cosa)[None] <= cap + 1e-3) & sk
        return float(inb.sum() / max(1, sk.sum())), float(face)
    o_disc = disc(own)
    ok = np.isfinite(ce) & (sk > 0.95)
    order = np.argsort(-np.where(ok, ce, -1).ravel())[:int(os.environ.get("NCAND", 400))]          # best point ceilings, then the flat disc
    rows = [dict(a=float(A.ravel()[k]), b=float(B.ravel()[k]), ceiling=round(float(ce.ravel()[k]), 3), motion_mm=round(float(mo.ravel()[k]), 1), r_lowest=round(float(hm.ravel()[k]), 1),
                 disc_ceiling=round(disc(D[k])[0], 3)) for k in order]
    rows = sorted(rows, key=lambda r: -r["disc_ceiling"])[:15]
    out[frame] = dict(label=lab, own=dict(dir=[round(x, 4) for x in own], motion_mm=round(o_mo, 1), point_ceiling=round(o_ce, 3), disc_ceiling=round(o_disc[0], 3), face=round(o_disc[1], 1)),
                      share_dirs_ceiling_ge_90=round(float((ce[ok] >= 0.9).mean()), 3), median_motion_mm=round(float(np.nanmedian(mo[ok])), 1), best=rows,
                      grid=dict(a=A[:, 0].tolist() if frame == "humerus" else A[:, 0].tolist(), b=B[0].tolist(), ceiling=np.round(np.nan_to_num(ce, nan=-1), 3).tolist(), motion=np.round(np.nan_to_num(mo, nan=-1), 1).tolist()))
    print(f"{frame:8s} {lab}: own dir motion {o_mo:5.1f} mm, point ceiling {100 * o_ce:5.1f}%, O23 flat-disc ceiling {100 * o_disc[0]:5.1f}% (face {o_disc[1]:.1f} mm)")
    print(f"         directions with skin in >95% of frames: {int(ok.sum())}; point ceiling >= 90% in {100 * out[frame]['share_dirs_ceiling_ge_90']:.1f}% of them; median motion {out[frame]['median_motion_mm']} mm")
    for r in rows[:8]: print(f"         best: ({r['a']:6.1f}, {r['b']:6.1f}) ceiling {100 * r['ceiling']:5.1f}%  disc {100 * r['disc_ceiling']:5.1f}%  motion {r['motion_mm']:5.1f} mm  lowest r {r['r_lowest']}")
json.dump(out, open(os.path.join(HERE, f"skin_motion_map_{G:g}.json"), "w"))
