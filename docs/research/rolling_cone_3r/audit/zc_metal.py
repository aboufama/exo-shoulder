"""audit probe: metal-aware rolling cells on the zc-frontier RIGID chain (J3 through GH, no knee), Bench(60,160) fast.
A ws pose counts if kinematic take AND every rolling band clear of the skin at its ONE level (q 0.97)."""
import importlib.util, json, math, sys, time
import numpy as np
SP = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
RR = "/home/user/exo-shoulder/docs/research/rolling_cone_3r"
def load(n, p):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
bd = load("bands", RR + "/rc_bands.py"); sr = load("srch", RR + "/rc_search.py"); zg = load("zg", SP + "/zc_ghost.py")
rc, K, B, F, HG = bd.rc, bd.K, bd.B, bd.F, bd.HG
ws = np.array(B.kind) == "ws"; elev = np.array([p["elev"] for p in B.poses]); over = ws & (elev >= 140)

def band_eval(D, Rm, Pi, q=0.97):
    Dw = np.einsum("pij,nj->pni", Rm, D); I = np.repeat(Pi, Dw.shape[1])
    R = K.requirement(B, I, Dw.reshape(-1, 3)).reshape(Dw.shape[:2]); miss = ~np.isfinite(R) | (R > 215)
    Rp = np.where(miss, -1, R).max(1); lvl = float(np.quantile(Rp, q))
    d = K.dist_many(B, I, (lvl * Dw).reshape(-1, 3)).reshape(Dw.shape[:2]); cp = (d < 0).any(1); dn = d[~cp]
    return lvl, cp, float(((dn >= 2) & (dn <= 14)).mean()) if len(dn) else 0.0

def ev(cell, discs=False):
    G = zg.ZGhost(cell)
    if any(j.kind == "roll" and abs(1 + j.r) < 0.25 for j in G.j): return None
    ok, t, m, th = G.take(HG); Pi = np.nonzero(ok)[0]
    if len(Pi) < 20: return None
    cum = [np.broadcast_to(np.eye(3), (len(Pi), 3, 3))]
    for k, j in enumerate(G.j): cum.append(cum[-1] @ j.T(t[Pi, k]))
    bad = np.zeros(len(Pi), bool); ibs = {}; pen = 0.0; arcs = {}
    for k, j in enumerate(G.j):
        if discs:
            Dc = K.cap_dirs(np.broadcast_to(j.w, (1, 3)), rad=10.0, step=2.0)[0]
            l, c, ib = band_eval(Dc, F.RS[Pi] @ cum[k], Pi); ibs[f"J{k+1}disc"] = [round(ib, 3), round(l, 1)]
        if j.kind != "roll": continue
        x = t[Pi, k] / (1 + j.r); y = t[Pi, k] * j.r / (1 + j.r)
        sun, pl = math.degrees(np.ptp(x)), math.degrees(np.ptp(y)); walk = 60 * math.sin(math.radians(j.ga)) * np.ptp(x)
        pen += 5 * (max(0, walk - 20) / 5 + max(0, sun - 120) / 20 + max(0, pl - 240) / 40); arcs[f"J{k+1}"] = [round(sun, 1), round(pl, 1), round(walk, 1)]
        Ds = bd.band_dirs(j.c, j.w, math.degrees(x.min()), math.degrees(x.max()), 1, j.ga)
        Dp = bd.band_dirs(j.m0, j.w, math.degrees(-y.max()), math.degrees(-y.min()), 1, j.gb)
        ls, cs, ib1 = band_eval(Ds, F.RS[Pi] @ cum[k], Pi); lp, cpl, ib2 = band_eval(Dp, F.RS[Pi] @ cum[k + 1], Pi)
        bad |= cs | cpl; ibs[f"J{k+1}"] = [round(ib1, 3), round(ib2, 3), round(ls, 1), round(lp, 1)]
    keep = np.zeros(len(HG), bool); keep[Pi[~bad]] = True
    n = int((keep & ws).sum()); no = int((keep & over).sum())
    obj = n + 0.1 * no - pen + sum(20 * min(0, v - 0.9) for kk, vv in ibs.items() if "disc" not in kk for v in vv[:2])
    return dict(kin=int((ok & ws).sum()), metal=n, over=no, bands=ibs, arcs=arcs, obj=round(obj, 3))

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "one":
        print(json.dumps(dict(cell=json.loads(sys.argv[2]), **ev(json.loads(sys.argv[2]), discs=True)))); sys.exit()
    fam = sys.argv[2]; out = open(sys.argv[3], "a"); nr, nc = int(sys.argv[4]), int(sys.argv[5]); rng = np.random.default_rng(int(sys.argv[6]) if len(sys.argv) > 6 else 11)
    js = {"J2": ["J2"], "J12": ["J1", "J2"], "J123": ["J1", "J2", "J3"], "J23": ["J2", "J3"]}[fam]
    def cell_of(x, sg):
        c = {"rigid": 1}
        for i, jn in enumerate(js):
            ga, gb, beta = np.clip(x[3 * i:3 * i + 3], sr.LO, sr.HI)
            if sg[i] < 0 and gb > ga - 3: gb = ga - 3
            c[jn] = dict(kind="roll", ga=round(float(ga), 3), gb=round(float(max(gb, 1.0)), 3), beta=round(float(beta), 3), sign=int(sg[i]))
        return c
    rec = []; t0 = time.time()
    def run(c):
        try: r = ev(c)
        except Exception as e: r = None
        out.write(json.dumps(dict(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), cell=c, **(r or {"obj": -1e3}))) + "\n"); out.flush()
        return -1e3 if r is None else r["obj"]
    for i in range(nr):
        x = rng.uniform(np.tile(sr.LO, len(js)), np.tile(sr.HI, len(js))); sg = tuple(1 if rng.random() < 0.6 else -1 for _ in js)
        rec.append((run(cell_of(x, sg)), x, sg))
    rec.sort(key=lambda z: -z[0]); print("random done", round(time.time() - t0), rec[0][0], file=sys.stderr, flush=True)
    for _, x0, sg in rec[:2]:
        sr.cma(lambda x, sg=sg: run(cell_of(x, sg)), x0, np.tile(np.array([5.0, 5.0, 40.0]), len(js)), nc)
