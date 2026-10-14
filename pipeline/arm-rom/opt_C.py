"""Evolutionary search for a 3-pivot (serial spherical 3R) shoulder with body-routed links, post travel limited only by
real contact (POST_HALF, default 180), against the BodyParts3D skin. Elitist (mu + lambda) with Gaussian mutation.

    POST_HALF=180 WORKERS=4 python3 opt_C.py RMAX GENERATIONS
"""
import json, math, os, sys, random
import concurrent.futures as cf
import numpy as np
import design_search as D
import design_search_routed as R

RMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 150.0
GENS = int(sys.argv[2]) if len(sys.argv) > 2 else 12
W = int(os.environ.get("WORKERS", 4)); LAM = 16; MU = 6


def init(k):
    R.RMAX = RMAX; R.VX, R.ER, R.EC = R.voxels(); R.set_stride(k)


def bvec(az, el):
    return [-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)]


def design(g):
    az, el, a1, a2, de, wz, br = g
    return dict(b=bvec(az, el), az=round(az, 1), el=round(el, 1), a1=round(a1, 1), a2=round(a2, 1), delta=round(de, 1), waz=round(wz, 1), branch=int(br))


def feasible(g):
    az, el, a1, a2, de, wz, br = g
    return -20 <= el <= 90 and 35 <= a1 <= 135 and 35 <= a2 <= 135 and 25 <= de <= 110 and D.base_ok(np.array(bvec(az, el)))


def score(g):
    try: return R.evaluate_C(design(g))["cov"]
    except Exception as e: return 0.0


def mutate(g, s):
    az, el, a1, a2, de, wz, br = g
    for _ in range(50):
        n = [(az + random.gauss(0, 25 * s)) % 360, el + random.gauss(0, 12 * s), a1 + random.gauss(0, 12 * s), a2 + random.gauss(0, 12 * s),
             de + random.gauss(0, 10 * s), ((wz + random.gauss(0, 30 * s) + 180) % 360) - 180, br if random.random() > 0.1 else -br]
        if feasible(n): return n
    return g


if __name__ == "__main__":
    random.seed(7)
    seeds = []
    for f in ("design_search_routed_C_150.json", "design_search_anat_C.json", "design_search_pivots.json"):
        if os.path.exists(f):
            for r in json.load(open(f))[:12]:
                seeds.append([r["az"], r["el"], r["a1"], r["a2"], r["delta"], r["waz"], r.get("branch", -1)])
    seeds += [[random.uniform(0, 360), random.uniform(20, 85), random.uniform(50, 120), random.uniform(50, 120), random.uniform(35, 95), random.uniform(-180, 180), random.choice([1, -1])] for _ in range(24)]
    seeds = [s for s in seeds if feasible(s)]
    log = open(f"opt_C_{int(RMAX)}.log", "w")
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(8,)) as ex:
        sc = list(ex.map(score, seeds, chunksize=1))
        pop = sorted(zip(sc, seeds), key=lambda t: -t[0])[:MU]
        print("gen 0", [round(100 * s, 1) for s, _ in pop], file=log, flush=True)
        sig = 1.0
        for gen in range(1, GENS + 1):
            kids = [mutate(random.choice(pop)[1], sig) for _ in range(LAM)]
            ks = list(ex.map(score, kids, chunksize=1))
            prev = pop[0][0]
            pop = sorted(pop + list(zip(ks, kids)), key=lambda t: -t[0])[:MU]
            sig = max(0.3, sig * (0.85 if pop[0][0] <= prev else 1.0))
            print(f"gen {gen}", [round(100 * s, 1) for s, _ in pop], "best", design(pop[0][1]), file=log, flush=True)
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(2,)) as ex:
        full = list(ex.map(R.evaluate_C, [design(g) for _, g in pop[:3]], [True] * 3))
    for r in sorted(full, key=lambda r: -r["cov"]):
        print(f"FULL cov {100 * r['cov']:.1f}%  kin {100 * r['kin']:.1f}%  az {r['az']} el {r['el']} arcs {r['a1']}/{r['a2']} delta {r['delta']} waz {r['waz']} br {r['branch']} pins {r['r_pins']}", file=log, flush=True)
    json.dump(sorted(full, key=lambda r: -r["cov"]), open(f"opt_C_{int(RMAX)}.json", "w"))
