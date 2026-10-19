"""metal-aware J2 search on H1's knee chain (Bench(60,160) fast): kinematic take AND both J2 bands (sun on link 1,
planet on link 2) clear of the skin at their ONE level (kit q 0.97 rule); objective = metal takes on ws + 20 x the
in-band shortfall of each band below 0.90. Random cells under the step-0 arc caps, then CMA-ES from the best."""
import importlib.util, json, math, os, sys, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('bands', os.path.join(H, 'rc_bands.py')); bd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bd)
spec = importlib.util.spec_from_file_location('srch', os.path.join(H, 'rc_search.py')); sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
rc, K, B, F, HG = bd.rc, bd.K, bd.B, bd.F, bd.HG
ws = np.array(B.kind) == 'ws'; elev = np.array([p['elev'] for p in B.poses]); over = ws & (elev >= 140)

def band_eval(D, Rm, Pi, q=0.97):
    Dw = np.einsum('pij,nj->pni', Rm, D); I = np.repeat(Pi, Dw.shape[1])
    R = K.requirement(B, I, Dw.reshape(-1, 3)).reshape(Dw.shape[:2]); miss = ~np.isfinite(R) | (R > 215)
    Rp = np.where(miss, -1, R).max(1); lvl = float(np.quantile(Rp, q))
    d = K.dist_many(B, I, (lvl * Dw).reshape(-1, 3)).reshape(Dw.shape[:2]); cp = (d < 0).any(1); dn = d[~cp]
    return lvl, cp, float(((dn >= 2) & (dn <= 14)).mean()) if len(dn) else 0.0

def ev(cell):
    G = rc.Ghost(cell); j = G.j[1]
    if abs(1 + j.r) < 0.25: return None
    ok, t, m, th = G.take(HG); Pi = np.nonzero(ok)[0]
    if len(Pi) < 20: return None
    x = t[Pi, 1] / (1 + j.r); y = t[Pi, 1] * j.r / (1 + j.r)
    sun, pl = math.degrees(np.ptp(x)), math.degrees(np.ptp(y)); walk = 60 * math.sin(math.radians(j.ga)) * np.ptp(x)
    T1 = G.j[0].T(t[Pi, 0]); T12 = T1 @ j.T(t[Pi, 1])
    Ds = bd.band_dirs(j.c, j.w, math.degrees(x.min()), math.degrees(x.max()), 1, j.ga)
    Dp = bd.band_dirs(j.m0, j.w, math.degrees(-y.max()), math.degrees(-y.min()), 1, j.gb)
    ls, cs, ibs = band_eval(Ds, F.RS[Pi] @ T1, Pi); lp, cpl, ibp = band_eval(Dp, F.RS[Pi] @ T12, Pi)
    keep = np.zeros(len(HG), bool); keep[Pi[~(cs | cpl)]] = True
    n = int((keep & ws).sum()); no = int((keep & over).sum())
    pen = 5 * (max(0, walk - 20) / 5 + max(0, sun - 120) / 20 + max(0, pl - 240) / 40)
    obj = n + 0.1 * no + 20 * min(0, ibs - 0.9) + 20 * min(0, ibp - 0.9) - pen
    return dict(kin=int((ok & ws).sum()), metal=n, over=no, ib_sun=round(ibs, 3), ib_planet=round(ibp, 3), R_sun=ls, R_planet=lp,
                arcs=[round(sun, 1), round(pl, 1), round(walk, 1)], obj=round(obj, 3))

if __name__ == '__main__':
    out = sys.argv[1]; nr = int(sys.argv[2]); nc = int(sys.argv[3]); f = open(out, 'a'); rng = np.random.default_rng(7); rec = []
    def run(cell):
        r = ev(cell); f.write(json.dumps(dict(t=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), cell=cell, **(r or {'obj': -1e3}))) + '\n'); f.flush()
        return -1e3 if r is None else r['obj']
    for c in [{'J2': dict(kind='roll', ga=25, gb=10, beta=30)}, {}]:
        run(c) if c else None
    for i in range(nr):
        x = rng.uniform(sr.LO, sr.HI); sg = (1 if rng.random() < 0.6 else -1,)
        c = sr.cell_of('J2', x, sg); rec.append((run(c), x, sg))
    rec.sort(key=lambda z: -z[0])
    for _, x0, sg in rec[:2]:
        sr.cma(lambda x, sg=sg: run(sr.cell_of('J2', x, sg)), x0, np.array([5.0, 5.0, 40.0]), nc)
