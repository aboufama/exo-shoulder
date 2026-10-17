"""fold-ceiling step 2b': the skin requirement of a GH-ray hub in EVERY direction, every pose of Bench(60,160) (the fit /
search bench, fast signed-distance cache): req[p, g] = the K3 march (first t >= 15 mm with skin distance >= 2 mm and
>= 0 for the next 15 mm) along scapula-frame direction G[g] posed by RS[p]. A hub disc (O20, radius 10) on axis u needs
the max over its samples; reqD[p, g] = max of req over the grid directions within 8.5 deg of G[g] (radius 10 at ~65 mm).
Output .cache/fold_ceiling/req_map_60_160.npz (G, req, reqD, kind) - a cache, not committed.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/fold_ceiling/req_map.py
"""
import math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_bench as CB; import concept_kit as K  # noqa: E402
from scipy.spatial import cKDTree

N = int(os.environ.get("FC_NDIR", 6000))
i = np.arange(N) + 0.5; phi = np.arccos(1 - 2 * i / N); gold = math.pi * (1 + 5 ** 0.5)
G = np.stack([np.cos(gold * i) * np.sin(phi), np.cos(phi), np.sin(gold * i) * np.sin(phi)], 1)
B = CB.Bench(60, 160); assert B.grid is not None, "needs the Bench(60,160) fast cache"
F = K.frames(B); P = len(B.idx); t = time.time()
req = np.empty((P, N), np.float32)
for p in range(P):
    Dw = G @ F.RS[p].T
    r = K.requirement(B, np.full(N, p), Dw)
    req[p] = np.where(np.isfinite(r), r, 400.0)
    if p % 20 == 0: print(p, round(time.time() - t, 1), flush=True)
tree = cKDTree(G); nb = tree.query_ball_point(G, 2 * math.sin(math.radians(8.5) / 2))
reqD = np.stack([req[:, n].max(1) for n in nb], 1).astype(np.float32)
np.savez_compressed(os.path.join(REPO, ".cache", "fold_ceiling", "req_map_60_160.npz"), G=G, req=req, reqD=reqD,
                    kind=np.array(B.kind), idx=B.idx)
print("done", round(time.time() - t, 1))
