import sys, time, os, json, numpy as np
sys.path.insert(0, "tools"); import concept_bench as CB
from sdist import Mesh
B = CB.Bench(60, 160); rng = np.random.default_rng(1)
poses = [0, 30, 59, 60, 140, 219]
out = []
for i in poses:
    V, F = B.skin(i); V = np.asarray(V, float)
    near = V[np.linalg.norm(V, axis=1) < 160]
    # metal-like points: skin vertices pushed outward along the GH ray by 0-30 mm, plus a few inside
    P = near[rng.choice(len(near), 2000)]; P = P + (P / np.linalg.norm(P, axis=1, keepdims=True)) * rng.uniform(-3, 30, (2000, 1))
    # (a) judge/sdist (reference)
    t0 = time.perf_counter(); M = Mesh(V, F, 2.0).build_grid(2.5, np.array([-320.0] * 3), np.array([320.0] * 3)); ta_set = time.perf_counter() - t0
    t0 = time.perf_counter(); da = np.abs(M.closest(P)[0]); da = np.where(M.winding_at(P) >= 1, -da, da); ta_q = time.perf_counter() - t0
    # (b) libigl exact
    t0 = time.perf_counter(); E = CB._Exact(V); tb_set = time.perf_counter() - t0
    t0 = time.perf_counter(); db = E(P); tb_q = time.perf_counter() - t0
    # (c) grid
    t0 = time.perf_counter(); dc = B.dist(i, P); tc_q = time.perf_counter() - t0
    m = np.abs(da) <= 20
    inb = lambda d: (d >= 2) & (d <= 14)
    r = dict(pose=i, load=os.getloadavg()[0], sdist_setup=ta_set, sdist_query=ta_q, igl_setup=tb_set, igl_query=tb_q, grid_query=tc_q,
             igl_maxerr=float(np.max(np.abs(db - da)[m])), grid_p99=float(np.percentile(np.abs(dc - da)[m], 99)), grid_max=float(np.max(np.abs(dc - da)[m])),
             sign_err_igl=int(((db < 0) != (da < 0)).sum()), sign_err_grid=int(((dc < 0) != (da < 0)).sum()),
             band_flip_grid=float(np.mean(inb(dc) != inb(da))), band_flip_igl=float(np.mean(inb(db) != inb(da))))
    out.append(r); print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}), flush=True)
med = lambda k: float(np.median([r[k] for r in out]))
a = med("sdist_setup") + med("sdist_query"); b = med("igl_setup") + med("igl_query"); c = med("grid_query")
print("PER POSE (setup+2000 pts): sdist %.3fs  igl %.4fs  grid %.5fs" % (a, b, c))
print("SPEEDUP igl vs sdist %.0fx, grid vs sdist %.0fx, grid vs igl %.0fx" % (a / b, a / c, b / c))
print("query only: sdist %.3fs igl %.4fs grid %.5fs" % (med("sdist_query"), med("igl_query"), c))
json.dump(out, open(sys.argv[1], "w"), indent=1)
