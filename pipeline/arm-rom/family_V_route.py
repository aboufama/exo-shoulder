import json, os, sys, numpy as np, concurrent.futures as cf
import design_search_routed as R, family_V as V
RMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 150.0
def init(k):
    R.RMAX = RMAX; R.VX, R.ER, R.EC = R.voxels(); R.set_stride(k)
def ev(d): return V.evaluate(d)
def evf(d): return V.evaluate(d, True)
if __name__ == "__main__":
    ks = json.load(open("family_V_kin.json"))
    seen, base = set(), []
    for r in ks:
        key = (r["az"], r["el"], r["a1"], r["a2"], r["branch"])
        if key in seen: continue
        seen.add(key); base.append(r)
        if len(base) >= 14: break
    cands = [dict({k: r[k] for k in ("b", "az", "el", "a1", "a2", "branch")}, beta=be, gam=ga) for r in base for be in (40, 60) for ga in (0, 90, 180, 270)]
    with cf.ProcessPoolExecutor(max_workers=int(os.environ.get("WORKERS", 4)), initializer=init, initargs=(8,)) as ex:
        rs = list(ex.map(ev, cands, chunksize=1))
    rs.sort(key=lambda r: -r["cov"])
    print("screen:", [(round(100 * r["cov"], 1), round(100 * r["kin"], 1), r["az"], r["el"], r["a1"], r["a2"], r["branch"], r["beta"], r["gam"]) for r in rs[:10]], flush=True)
    json.dump(rs, open(f"family_V_screen_{int(RMAX)}.json", "w"))
