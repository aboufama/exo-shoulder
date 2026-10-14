"""evolutionary search: conformal D4, J4 // elbow axis (flat BOTTOM, hub face Z_J4), hug-at-rest caps G mm.
    G=10 Z_J4=67.5 WORKERS=4 python3 opt_conf.py GENS  -> opt_conf_G{G}.json / .log"""
import json, math, os, random, sys
import numpy as np
import concurrent.futures as cf
import conformal as CF
import design_search as D
FIX = json.load(open("fix_w_tea.json")); G = float(os.environ.get("G", 10)); ZJ4 = float(os.environ.get("Z_J4", 67.5))
W = int(os.environ.get("WORKERS", 4)); LAM, MU = 24, 8
def bvec(az, el): return [-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)]
def design(g):
    az, el, a1, a2, a3, br, o1, o2, o3 = g
    return dict(b=bvec(az, el), az=round(az, 1), el=round(el, 1), a1=round(a1, 1), a2=round(a2, 1), a3=round(a3, 1),
                delta=FIX["delta"], waz=FIX["waz"], branch=int(br), order=(int(o1), int(o2), int(o3)))
def feasible(g):
    az, el, a1, a2, a3 = g[:5]; b = np.array(bvec(az, el))
    return -15 <= el <= 90 and all(25 <= a <= 120 for a in (a1, a2, a3)) and b[0] <= 0.35 and b[1] >= -0.25
def score(g, full=False, **kw):
    try:
        r = CF.evaluate_rest(design(g), G=G, z_j4=ZJ4, **kw)
        if r["cov"] <= 0: return (0.0, r) if full else 0.0
        worst = max(r["per_link_p50"])                       # the farthest link (median over the covered motion)
        s = r["cov"] * (1 - 0.6 * min(1.0, max(0.0, (worst - G) / 15))) * (1 - 0.3 * min(1.0, max(0.0, (r["gap_p90"] - 25) / 50)))
        return (s, r) if full else s
    except Exception as e:
        return (0.0, {}) if full else 0.0
def mutate(g, s):
    for _ in range(80):
        n = [(g[0] + random.gauss(0, 30 * s)) % 360, g[1] + random.gauss(0, 12 * s)] + [x + random.gauss(0, 10 * s) for x in g[2:5]]
        n += [g[5] if random.random() > 0.15 else -g[5]] + [b if random.random() > 0.15 else 1 - b for b in g[6:9]]
        if feasible(n): return n
    return g
def rand(r):
    while True:
        g = [r.uniform(0, 360), r.uniform(-15, 90), r.uniform(25, 120), r.uniform(25, 120), r.uniform(25, 120), r.choice([-1, 1]), r.randint(0, 1), r.randint(0, 1), r.randint(0, 1)]
        if feasible(g): return g
if __name__ == "__main__":
    GENS = int(sys.argv[1]) if len(sys.argv) > 1 else 30; random.seed(7); R = random.Random(11)
    seeds = [rand(R) for _ in range(int(os.environ.get("SEEDS", 240)))]
    for f in ("opt_conf_G10.json",):
        if os.path.exists(f) and os.environ.get("RESEED", "1") == "1":
            for r in json.load(open(f)):
                o = r.get("order", (1, 1, 0)); seeds.append([r["az"], r["el"], r["a1"], r["a2"], r["a3"], r["branch"], *o])
    TAG = os.environ.get("TAG", ""); log = open(f"opt_conf_G{int(G)}{TAG}.log", "w")
    with cf.ProcessPoolExecutor(W) as ex:
        sc = list(ex.map(score, seeds, chunksize=4)); pop = sorted(zip(sc, seeds), key=lambda t: -t[0])[:MU]; sig = 1.0
        print("gen 0", [round(100 * s, 1) for s, _ in pop], design(pop[0][1]), file=log, flush=True)
        for gen in range(1, GENS + 1):
            kids = [mutate(random.choice(pop)[1], sig) for _ in range(LAM)]
            ks = list(ex.map(score, kids, chunksize=2)); prev = pop[0][0]
            pop = sorted(pop + list(zip(ks, kids)), key=lambda t: -t[0])[:MU]; sig = max(0.25, sig * (0.88 if pop[0][0] <= prev else 1.0))
            print(f"gen {gen}", [round(100 * s, 1) for s, _ in pop], design(pop[0][1]), file=log, flush=True)
    full = [score(g, full=True, stride=1, q_step=6, q_rest_step=6)[1] for _, g in pop[:3]]
    for r in full: print("FULL", {k: v for k, v in r.items() if k not in ("caps", "cov_mask", "idx")}, file=log, flush=True)
    json.dump(full, open(f"opt_conf_G{int(G)}{TAG}.json", "w"))
