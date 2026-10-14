"""Continuous evolutionary refinement of the 4-pivot shoulder (family D) at a FIXED shell radius, against the corrected
anatomical body (design_search_anat.eval_D). Thin links / post travel via the CLEAR and POST_HALF env vars.

    CLEAR=4 POST_HALF=180 WORKERS=4 python3 opt_D.py R GENERATIONS
"""
import json, math, os, sys, random, glob
import concurrent.futures as cf
import numpy as np
import design_search as D
import design_search_anat as A

R = float(sys.argv[1]) if len(sys.argv) > 1 else 148.0
MULTI = os.environ.get("MULTI") == "1"; RLO = 96.0; FP = os.environ.get("FP") == "1"
GENS = int(sys.argv[2]) if len(sys.argv) > 2 else 15
W = int(os.environ.get("WORKERS", 4)); LAM, MU = 16, 6


def bvec(az, el): return [-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)]
FIXW = json.load(open(os.environ["FIX_W"])) if os.environ.get("FIX_W") else None   # J4 axis fixed (drop-in BOTTOM)
def design(g):
    az, el, a1, a2, a3, de, wz = g[:7]
    if FIXW: de, wz = FIXW["delta"], FIXW["waz"]
    d = dict(R=R, b=bvec(az, el), az=round(az, 1), el=round(el, 1), a1=round(a1, 1), a2=round(a2, 1), a3=round(a3, 1), delta=round(de, 1), waz=round(wz, 1))
    if MULTI: d["Rs"] = [round(x, 1) for x in g[7:10]]
    return d
def feasible(g):
    az, el, a1, a2, a3, de, wz = g[:7]
    ok = -20 <= el <= 90 and all(35 <= a <= 120 for a in (a1, a2, a3)) and (FIXW is not None or 30 <= de <= 95) and D.base_ok(np.array(bvec(az, el)))
    return ok and (not MULTI or all(RLO <= x <= R for x in g[7:10]))
def init(k, q): A.set_stride(k, q)
def score(g):
    try: return (A.eval_D_fp if FP else A.eval_Dm if MULTI else A.eval_D)(design(g))["cov"]
    except Exception: return 0.0
def mutate(g, s):
    for _ in range(60):
        az, el, a1, a2, a3, de, wz = g[:7]
        n = [(az + random.gauss(0, 25 * s)) % 360, el + random.gauss(0, 10 * s), a1 + random.gauss(0, 8 * s), a2 + random.gauss(0, 8 * s),
             a3 + random.gauss(0, 8 * s), de + random.gauss(0, 7 * s), ((wz + random.gauss(0, 25 * s) + 180) % 360) - 180]
        if MULTI: n += [x + random.gauss(0, 5 * s) for x in g[7:10]]
        if feasible(n): return n
    return g


if __name__ == "__main__":
    random.seed(13); seeds = []
    for f in glob.glob("opt_D_*.json") + glob.glob("design_search_anat_D*.json"):
        for r in json.load(open(f)):
            s0 = [r["az"], r["el"], r["a1"], r["a2"], r["a3"], r["delta"], r["waz"]]
            seeds.append(s0 + ([min(R, x) for x in r.get("Rs", [R - 4, R - 4, R - 4])] if MULTI else []))
    seen, uniq = set(), []
    for s in seeds:
        k = tuple(round(x) for x in s)
        if k not in seen and feasible(s): seen.add(k); uniq.append(s)
    seeds = uniq[:30]
    tag = f"{int(R)}_c{os.environ.get('CLEAR', '9')}_p{os.environ.get('POST_HALF', '90')}" + ("_multi" if MULTI else "") + ("_fp" if FP else "") + (f"_back{int(A.BACK_MAX)}" if A.BACK_MAX else "") + ("_dropin" if A.DROPIN else "") + os.environ.get("TAG", "")
    log = open(f"opt_D_{tag}.log", "w")
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(3, 10)) as ex:
        sc = list(ex.map(score, seeds, chunksize=1))
        pop = sorted(zip(sc, seeds), key=lambda t: -t[0])[:MU]; sig = 1.0
        print("gen 0", [round(100 * s, 1) for s, _ in pop], design(pop[0][1]), file=log, flush=True)
        for gen in range(1, GENS + 1):
            kids = [mutate(random.choice(pop)[1], sig) for _ in range(LAM)]
            ks = list(ex.map(score, kids, chunksize=1)); prev = pop[0][0]
            pop = sorted(pop + list(zip(ks, kids)), key=lambda t: -t[0])[:MU]
            sig = max(0.3, sig * (0.85 if pop[0][0] <= prev else 1.0))
            print(f"gen {gen}", [round(100 * s, 1) for s, _ in pop], design(pop[0][1]), file=log, flush=True)
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(1, 5)) as ex:
        full = list(ex.map(A.eval_D_fp if FP else A.eval_Dm if MULTI else A.eval_D, [design(g) for _, g in pop[:4]], chunksize=1))
    full.sort(key=lambda r: -r["cov"])
    for r in full: print("FULL", round(100 * r["cov"], 1), r, file=log, flush=True)
    json.dump(full, open(f"opt_D_{tag}.json", "w"))
