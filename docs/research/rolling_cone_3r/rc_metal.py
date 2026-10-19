"""metal-aware search of rolling cells on H1's knee chain (Bench(60,160) fast): a ws pose counts only if it is a
kinematic take AND every rolling band (sun on the proximal member, planet on the distal) is clear of the skin at its
ONE level (kit q 0.97 rule); objective = metal takes + 0.1 x overhead + 20 x each band's in-band shortfall below 0.90
- arc-cap penalty. Family J2 or J12; seeded CMA-ES from a cell (argv 5) or random + CMA."""
import importlib.util, json, math, os, sys, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('bands', os.path.join(H, 'rc_bands.py')); bd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bd)
spec = importlib.util.spec_from_file_location('srch', os.path.join(H, 'rc_search.py')); sr = importlib.util.module_from_spec(spec); spec.loader.exec_module(sr)
spec = importlib.util.spec_from_file_location('mj2', os.path.join(H, 'rc_metal_j2.py')); mj = importlib.util.module_from_spec(spec); spec.loader.exec_module(mj)
rc, K, B, F, HG = bd.rc, bd.K, bd.B, bd.F, bd.HG
ws, over = mj.ws, mj.over

def ev(cell):
    G = rc.Ghost(cell)
    if any(j.kind == 'roll' and abs(1 + j.r) < 0.25 for j in G.j): return None
    ok, t, m, th = G.take(HG); Pi = np.nonzero(ok)[0]
    if len(Pi) < 20: return None
    cum = [np.broadcast_to(np.eye(3), (len(Pi), 3, 3))]
    for k, j in enumerate(G.j): cum.append(cum[-1] @ j.T(t[Pi, k]))
    bad = np.zeros(len(Pi), bool); pen = 0.0; ibs = []; arcs = []
    for k, j in enumerate(G.j):
        if j.kind != 'roll': continue
        x = t[Pi, k] / (1 + j.r); y = t[Pi, k] * j.r / (1 + j.r)
        sun, pl = math.degrees(np.ptp(x)), math.degrees(np.ptp(y)); walk = 60 * math.sin(math.radians(j.ga)) * np.ptp(x)
        arcs.append([round(sun, 1), round(pl, 1), round(walk, 1)])
        pen += 5 * (max(0, walk - 20) / 5 + max(0, sun - 120) / 20 + max(0, pl - 240) / 40)
        Ds = bd.band_dirs(j.c, j.w, math.degrees(x.min()), math.degrees(x.max()), 1, j.ga)
        Dp = bd.band_dirs(j.m0, j.w, math.degrees(-y.max()), math.degrees(-y.min()), 1, j.gb)
        for D, Rm in ((Ds, F.RS[Pi] @ cum[k]), (Dp, F.RS[Pi] @ cum[k + 1])):
            lvl, cp, ib = mj.band_eval(D, Rm, Pi); bad |= cp; ibs.append(round(ib, 3)); pen -= 20 * min(0, ib - 0.9)
    keep = np.zeros(len(HG), bool); keep[Pi[~bad]] = True
    n = int((keep & ws).sum()); no = int((keep & over).sum())
    return dict(kin=int((ok & ws).sum()), metal=n, over=no, inband=ibs, arcs=arcs, obj=round(n + 0.1 * no - pen, 3))

if __name__ == '__main__':
    fam, out, nr, nc = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); js = sr.FAM[fam][0]
    f = open(out, 'a'); rng = np.random.default_rng(11); rec = []
    def run(cell):
        r = ev(cell); f.write(json.dumps(dict(t=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), fam=fam, cell=cell, **(r or {'obj': -1e3}))) + '\n'); f.flush()
        return -1e3 if r is None else r['obj']
    if len(sys.argv) > 5:
        sc = json.loads(sys.argv[5]); x0 = np.concatenate([[sc[j]['ga'], sc[j]['gb'], sc[j]['beta']] for j in js]); sg = [sc[j].get('sign', 1) for j in js]
        run(sc)
        for sd in (1.0, 0.5): sr.cma(lambda x: run(sr.cell_of(fam, x, sg)), x0, np.tile([5.0 * sd, 5.0 * sd, 40.0 * sd], len(js)), nc)
    else:
        for i in range(nr):
            x = np.concatenate([rng.uniform(sr.LO, sr.HI) for _ in js]); sg = tuple(1 if rng.random() < 0.6 else -1 for _ in js)
            c = sr.cell_of(fam, x, sg); rec.append((run(c), x, sg))
        rec.sort(key=lambda z: -z[0])
        for _, x0, sg in rec[:2]: sr.cma(lambda x, sg=sg: run(sr.cell_of(fam, x, sg)), x0, np.tile([5.0, 5.0, 40.0], len(js)), nc)
