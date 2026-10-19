"""random + CMA-ES search of rolling cells on the Bench(60,160) ws poses (kinematic takes), appending every config"""
import importlib.util, json, math, sys, time
import numpy as np
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', '..', 'tools'))
spec = importlib.util.spec_from_file_location('rc', __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'concepts', 'models', 'rolling-cone-3r.py'))
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
import concept_bench as CB
B = CB.Bench(60, 160); Z = CB._poses_all(); HG = Z['HG'][B.idx].astype(float); kind = np.array(B.kind)
elev = np.array([p['elev'] for p in B.poses]); ws = kind == 'ws'; HGw = HG[ws]; over = elev[ws] >= 140
FAM = {'J1': (['J1'], 0), 'J2': (['J2'], 0), 'J12': (['J1', 'J2'], 0), 'R3': (['J3'], 1), 'R23': (['J2', 'J3'], 1),
       'R123': (['J1', 'J2', 'J3'], 1), 'R0': ([], 1), 'R2': (['J2'], 1)}
LO = np.array([2.0, 2.0, -180.0]); HI = np.array([40.0, 40.0, 180.0])

def cell_of(fam, x, signs):
    js, rigid = FAM[fam]; c = {'rigid': 1} if rigid else {}
    for i, j in enumerate(js):
        ga, gb, beta = np.clip(x[3 * i:3 * i + 3], LO, HI)
        sg = signs[i]
        if sg < 0 and gb > ga - 3: gb = ga - 3
        c[j] = dict(kind='roll', ga=round(float(ga), 3), gb=round(float(max(gb, 1.0)), 3), beta=round(float(beta), 3), sign=int(sg))
    return c

WALK, SUN, PLAN = 20.0, 120.0, 240.0
def ev(cell):
    try:
        G = rc.Ghost(cell)
        if any(j.kind == 'roll' and abs(1 + j.r) < 0.25 for j in G.j): return 0, 0, -1e3, None
        ok, t, m, th = G.take(HGw)
        soft = float(np.clip(m[~ok] - 5, -20, 0).sum()) / 20.0 * 0.05 if (~ok).any() else 0.0
        pen = 0.0; ar = []
        for k, j in enumerate(G.j):
            if j.kind != 'roll' or not ok.any(): continue
            x = t[ok, k] / (1 + j.r); y = t[ok, k] * j.r / (1 + j.r)
            sun = math.degrees(np.ptp(x)); pl = math.degrees(np.ptp(y)); walk = 60 * math.sin(math.radians(j.ga)) * np.ptp(x)
            ar.append([round(sun, 1), round(pl, 1), round(walk, 1)])
            pen += 5 * (max(0, walk - WALK) / 5 + max(0, sun - SUN) / 20 + max(0, pl - PLAN) / 40)
        return int(ok.sum()), int((ok & over).sum()), int(ok.sum()) + 0.1 * int((ok & over).sum()) + soft - pen, ar
    except Exception as e:
        return 0, 0, -1e3, None

def cma(f, x0, s0, n_iter, lam=10, log=None):
    n = len(x0); mu = lam // 2; w = np.log(mu + .5) - np.log(np.arange(1, mu + 1)); w /= w.sum(); mueff = 1 / (w ** 2).sum()
    cc = (4 + mueff / n) / (n + 4 + 2 * mueff / n); cs = (mueff + 2) / (n + mueff + 5); c1 = 2 / ((n + 1.3) ** 2 + mueff)
    cmu = min(1 - c1, 2 * (mueff - 2 + 1 / mueff) / ((n + 2) ** 2 + mueff)); damps = 1 + 2 * max(0, math.sqrt((mueff - 1) / (n + 1)) - 1) + cs
    chiN = math.sqrt(n) * (1 - 1 / (4 * n) + 1 / (21 * n * n)); m = np.array(x0, float); sig = 1.0; C = np.diag(np.asarray(s0, float) ** 2)
    ps = np.zeros(n); pc = np.zeros(n); rng = np.random.default_rng(1); best = (-1e9, None)
    for it in range(n_iter):
        D2, Bm = np.linalg.eigh(C); D = np.sqrt(np.maximum(D2, 1e-20)); Z_ = rng.standard_normal((lam, n)); Y = Z_ * D @ Bm.T; X = m + sig * Y
        F = np.array([f(x) for x in X]); o = np.argsort(-F)
        if F[o[0]] > best[0]: best = (F[o[0]], X[o[0]].copy())
        yw = (w[:, None] * Y[o[:mu]]).sum(0); m = m + sig * yw
        Cih = Bm @ np.diag(1 / D) @ Bm.T; ps = (1 - cs) * ps + math.sqrt(cs * (2 - cs) * mueff) * Cih @ yw
        hs = np.linalg.norm(ps) / math.sqrt(1 - (1 - cs) ** (2 * (it + 1))) < (1.4 + 2 / (n + 1)) * chiN
        pc = (1 - cc) * pc + hs * math.sqrt(cc * (2 - cc) * mueff) * yw
        C = (1 - c1 - cmu) * C + c1 * np.outer(pc, pc) + cmu * (w[:, None, None] * np.einsum('ki,kj->kij', Y[o[:mu]], Y[o[:mu]])).sum(0)
        sig *= math.exp((cs / damps) * (np.linalg.norm(ps) / chiN - 1)); sig = min(sig, 3.0)
    return best

if __name__ == '__main__':
    fam = sys.argv[1]; out = sys.argv[2]; nrand = int(sys.argv[3]); ncma = int(sys.argv[4])
    js, rigid = FAM[fam]; nj = len(js); rng = np.random.default_rng(hash(fam) % 1000)
    f = open(out, 'a'); k = [0]; rec = []
    def logc(cell, r):
        f.write(json.dumps(dict(k=k[0], fam=fam, t=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), cell=cell, ws=r[0], over=r[1], obj=round(r[2], 3), arcs=r[3])) + '\n'); f.flush(); k[0] += 1
    if nj == 0:
        c = cell_of(fam, np.zeros(0), []); r = ev(c); logc(c, r); sys.exit()
    if len(sys.argv) > 5:                                   # seeded CMA: x0 / signs from a cell
        sc = json.loads(sys.argv[5]); x0 = np.concatenate([[sc[j]['ga'], sc[j]['gb'], sc[j]['beta']] for j in js]); sg = [sc[j].get('sign', 1) for j in js]
        def fobj(x, sg=sg):
            c = cell_of(fam, x, sg); r = ev(c); logc(c, r); return r[2]
        for sd in (1.0, 0.5):
            cma(fobj, x0, np.tile([5.0 * sd, 5.0 * sd, 40.0 * sd], nj), ncma)
        sys.exit()
    sign_sets = [tuple(s) for s in np.array(np.meshgrid(*[[1, -1]] * nj)).reshape(nj, -1).T]
    for i in range(nrand):
        x = np.concatenate([rng.uniform(LO, HI) for _ in range(nj)]); sg = sign_sets[rng.integers(len(sign_sets))]
        c = cell_of(fam, x, sg); r = ev(c); logc(c, r); rec.append((r[2], x, sg))
    rec.sort(key=lambda z: -z[0])
    for s0i in range(min(2, len(rec))):
        _, x0, sg = rec[s0i]
        def fobj(x, sg=sg):
            c = cell_of(fam, x, sg); r = ev(c); logc(c, r); return r[2]
        cma(fobj, x0, np.tile([5.0, 5.0, 40.0], nj), ncma)
