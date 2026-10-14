import json, os, sys, numpy as np, concurrent.futures as cf
import design_search_routed as R, family_G as G
RMAX = float(sys.argv[1]) if len(sys.argv) > 1 else 150.0
def init(k):
    R.RMAX = RMAX; R.VX, R.ER, R.EC = R.voxels(); R.set_stride(k)
def ev(d): return G.evaluate(d)
def evf(d): return G.evaluate(d, True)
if __name__ == "__main__":
    ks = json.load(open("family_G_kin.json"))[:10]
    cands = [dict({k: r[k] for k in ("b", "az", "el", "s")}, beta=be, gam=ga) for r in ks for be in (45, 60) for ga in (90, 180, 270, 0)]
    with cf.ProcessPoolExecutor(max_workers=int(os.environ.get("WORKERS", 4)), initializer=init, initargs=(8,)) as ex:
        rs = list(ex.map(ev, cands, chunksize=1))
    rs.sort(key=lambda r: -r["cov"])
    print("screen:", [(round(100 * r["cov"], 1), round(100 * r["kin"], 1), r["az"], r["el"], r["s"], r["beta"], r["gam"]) for r in rs[:8]], flush=True)
    top = [{k: r[k] for k in ("b", "az", "el", "s", "beta", "gam")} for r in rs[:4]]
    with cf.ProcessPoolExecutor(max_workers=4, initializer=init, initargs=(2,)) as ex:
        full = list(ex.map(evf, top, chunksize=1))
    full.sort(key=lambda r: -r["cov"])
    for r in full: print(f"  cov {100*r['cov']:.1f}%  kin {100*r['kin']:.1f}%  az {r['az']} el {r['el']} s {r['s']} beta {r['beta']} gam {r['gam']} radius {r.get('radius')}", flush=True)
    json.dump(full, open(f"family_G_routed_{int(RMAX)}.json", "w"))
