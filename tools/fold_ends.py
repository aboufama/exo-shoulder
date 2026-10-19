"""tools/fold_ends.py (writes docs/research/fold/ends.json; OMP_NUM_THREADS=3 python3 tools/fold_ends.py, ~2 min).

Far-end hubs: a revolute axis is a LINE through GH; its hub may sit at either end (kinematics, incl. the fold band,
are invariant to the axis sign). Scan every J1 line (az 6 deg, el 0..88 / 4 = every line once, incl. the near-horizontal
lines the frontier grid skipped) x every J3 line (wd 15..165 / 5, wa +-90 / 6), and score
  fold  = share of bench ws poses (clips all) inside the fold band for (a1, a2)
  hub1  = best 12 mm window share of a scapula-fixed O20 hub on the line's BETTER end (fold_rayblock's need model)"""
import sys, os, json, time, numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
import concept_bench as CB, concept_kit as K
t0 = time.time()
B = CB.Bench(n_clip=60, n_ws=160); Z = CB._poses_all(); RS = Z["RS"][B.idx].astype(float); Q = Z["HG"][B.idx].astype(np.float32)
kind = np.array(B.kind); ws, cl = kind == "ws", kind == "clip"; el_p = np.array([p["elev"] for p in B.poses]); over = el_p >= 120
L1 = [(az, el) for az in range(-180, 180, 6) for el in range(0, 89, 4)]
U = np.array([K.bvec(az, el) for az, el in L1])
ends = np.concatenate([U, -U])                                    # hub at +u end, then at -u end
e1 = np.cross(ends, [0.0, 0.0, 1.0]); n = np.linalg.norm(e1, axis=1, keepdims=True); e1 = np.where(n > 1e-6, e1 / np.maximum(n, 1e-9), [1, 0, 0]); e2 = np.cross(ends, e1)
off = np.stack([np.zeros_like(ends), 10 * e1, -10 * e1, 10 * e2, -10 * e2], 1)
r = np.arange(20.0, 201.0, 2.0); need = np.zeros((len(ends), len(B.idx)))
for i in range(len(B.idx)):
    P = (off[:, :, None, :] + ends[:, None, None, :] * r[None, None, :, None]) @ RS[i].T
    d = B.dist(i, P.reshape(-1, 3)).reshape(len(ends), 5, len(r))
    bad = d < 2.0; last = np.where(bad.any(2), len(r) - 1 - np.argmax(bad[:, :, ::-1], 2), -1)
    nd = np.where(last >= len(r) - 1, 999.0, r[np.clip(last + 1, 0, len(r) - 1)]); need[:, i] = nd.max(1)
print("need done", round(time.time() - t0), "s", flush=True)
def window(nd):
    v = np.sort(nd[nd < 900])
    if not len(v): return 0.0, 0.0, None
    j = np.searchsorted(v, v + 12.0, side="right"); k = int(np.argmax(j - np.arange(len(v)))); F = float(v[min(j[k], len(v)) - 1])
    return float((j[k] - k) / len(nd)), float(((nd[over] <= F) & (nd[over] >= F - 12)).mean()), F
W = np.array([window(need[k])[:2] for k in range(len(ends))])      # (2N, 2)
N = len(L1); band_pos, band_neg = W[:N, 0], W[N:, 0]; best_end = np.where(band_neg > band_pos, -1, 1); band = np.maximum(band_pos, band_neg)
band_over = np.where(best_end > 0, W[:N, 1], W[N:, 1])
# fold histograms (sign-invariant): J1 lines x J3 lines
H3 = [(wd, wa) for wd in range(15, 166, 5) for wa in range(-90, 91, 6)]
u3 = np.array([K.wdir(wd, wa) for wd, wa in H3], np.float32); Wd = np.einsum("pij,kj->kpi", Q, u3)
nb = 181; Cw = np.zeros((N, len(H3), nb + 1), np.int32); Cc = np.zeros_like(Cw)
for i in range(N):
    th = np.degrees(np.arccos(np.clip(Wd @ U[i].astype(np.float32), -1, 1))); b = np.clip(np.rint(th).astype(np.int32), 0, nb - 1)
    for m, C in ((ws, Cw), (cl, Cc)):
        h = np.zeros((len(H3), nb), np.int32); bb = b[:, m]; np.add.at(h, (np.repeat(np.arange(len(H3)), bb.shape[1]), bb.ravel()), 1)
        C[i, :, 1:] = np.cumsum(h, 1)
print("fold hist done", round(time.time() - t0), "s", flush=True)
res = []
for a1 in range(35, 96, 5):
    for a2 in range(35, 111, 5):
        lo, hi = abs(a1 - a2) + K.FOLD_MARGIN, min(a1 + a2, 360 - a1 - a2) - K.FOLD_MARGIN   # kit rule (5 since 2026-10-16)
        if hi <= lo: continue
        l, h = int(np.ceil(lo)), int(np.floor(hi)) + 1
        rw = (Cw[:, :, h] - Cw[:, :, l]) / ws.sum(); rc = (Cc[:, :, h] - Cc[:, :, l]) / cl.sum()
        f = np.where(rc >= 0.999, rw, 0.0).max(1); j3 = np.where(rc >= 0.999, rw, -1).argmax(1)   # per J1 line: best J3 for fold
        sc = np.minimum(f, band)
        for i in np.argsort(-sc)[:3]:
            res.append(dict(a1=a1, a2=a2, az1=L1[i][0], el1=L1[i][1], hub1_end=int(best_end[i]), wd=H3[j3[i]][0], wa=H3[j3[i]][1],
                            fold_ws=round(float(f[i]), 3), hub1_band=round(float(band[i]), 3), hub1_band_over=round(float(band_over[i]), 3),
                            hub1_band_pos=round(float(band_pos[i]), 3), hub1_band_neg=round(float(band_neg[i]), 3)))
res.sort(key=lambda d: -min(d["fold_ws"], d["hub1_band"]))
out = dict(note=__doc__, rows=res, lines=[dict(az=a, el=e, band_pos=round(float(band_pos[k]), 3), band_neg=round(float(band_neg[k]), 3), band_over=round(float(band_over[k]), 3)) for k, (a, e) in enumerate(L1)])
json.dump(out, open(REPO + "/docs/research/fold/ends.json", "w"), indent=1)
print("done", round(time.time() - t0), "s")
for d in res[:15]: print(d)
print("lines with hub-1 band >= 0.9 at + end:", int((band_pos >= 0.9).sum()), " at - end:", int((band_neg >= 0.9).sum()), "of", N)
# the old best (frontier top + leader) for reference
for az, el in ((132, 16), (96, 64), (120, 28), (108, 20)):
    k = int(np.argmin([(a - az) ** 2 + (b - el) ** 2 for a, b in L1])); print("ref", L1[k], "band +end", round(band_pos[k], 3), "-end", round(band_neg[k], 3))
