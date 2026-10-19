"""minimal CMA-ES (numpy) on the envh fast bench; DC.BOX end_extra opened to the rule bound 8; categorical fixed sigma -1 inv2 0 inv3 1"""
import sys, json, time, math
sys.path.insert(0, "/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/dca")
import numpy as np
import envh_eval as E
E.DC.BOX["end_extra"] = (0.0, 8.0)
start, seed, budget, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
x0p = E.VG if start == "vg" else E.CL
KEYS = ["az", "el", "a1", "a2", "wd", "wa", "q", "end_extra"]
SC = dict(az=6, el=3, a1=3, a2=3, wd=4, wa=4, q=0.015, end_extra=1.5)
FIX = dict(sigma=-1, inv2=0, inv3=1)
rng = np.random.default_rng(seed); n = len(KEYS)
m = np.zeros(n); sig = 0.5; C = np.eye(n); ps = np.zeros(n); pc = np.zeros(n)
lam = 8; mu = 4; w = np.log(mu + .5) - np.log(np.arange(1, mu + 1)); w /= w.sum(); mueff = 1 / (w ** 2).sum()
cs = (mueff + 2) / (n + mueff + 5); ds = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs
cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); c1 = 2 / ((n + 1.3) ** 2 + mueff); cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff))
chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n))
def par(z): return dict(FIX, **{k: float(x0p[k] + z[i] * SC[k]) for i, k in enumerate(KEYS)})
rows = []; t0 = time.time(); best = (1e9, None); gen = 0
g, r, _ = E.ev(par(m)); rows.append(dict(gen=0, params=par(m), gap=g, rep=r)); best = (g, par(m))
while time.time() - t0 < budget:
    gen += 1; D, B = np.linalg.eigh(C); D = np.sqrt(np.maximum(D, 1e-20))
    Z = rng.standard_normal((lam, n)); Y = Z @ np.diag(D) @ B.T; X = m + sig * Y
    f = []
    for x in X:
        g, r, _ = E.ev(par(x)); f.append(g); rows.append(dict(gen=gen, params=par(x), gap=g, rep=r))
        if g < best[0]: best = (g, par(x))
    o = np.argsort(f); yw = (Y[o[:mu]] * w[:, None]).sum(0); m = m + sig * yw
    Cih = B @ np.diag(1 / D) @ B.T
    ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * (Cih @ yw)
    hs = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs) ** (2 * gen)) < (1.4 + 2 / (n + 1)) * chiN
    pc = (1 - cc) * pc + hs * math.sqrt(cc * (2 - cc) * mueff) * yw
    C = (1 - c1 - cmu) * C + c1 * np.outer(pc, pc) + cmu * (Y[o[:mu]].T * w) @ Y[o[:mu]]
    sig *= math.exp((cs / ds) * (np.linalg.norm(ps) / chiN - 1))
    print(f"gen {gen} best_gen {min(f):.2f} best {best[0]:.2f} sig {sig:.3f} t {time.time()-t0:.0f}", flush=True)
    json.dump(dict(best=best, rows=rows), open(out, "w"), default=float)
json.dump(dict(best=best, rows=rows), open(out, "w"), default=float)
print("BEST", best[0], json.dumps(best[1]))
