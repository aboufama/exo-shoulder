"""Routed-link search driver: broad kinematic screen (no body), then body-routed evaluation of the best candidates.

    WORKERS=4 python3 routed_runner.py B|C|E [RMAX]
"""
import json, math, os, sys
import concurrent.futures as cf
import numpy as np
import design_search as D
import design_search_anat as A
import design_search_routed as R

fam = sys.argv[1]; RMAX = float(sys.argv[2]) if len(sys.argv) > 2 else 150.0
W = int(os.environ.get("WORKERS", 4))


def init(k):
    R.RMAX = RMAX; R.VX, R.ER, R.EC = R.voxels(); R.set_stride(k)


def kin(d): R.set_stride(3); return getattr(R, f"evaluate_{fam}")(d, kin_only=True)
def routed(d): return getattr(R, f"evaluate_{fam}")(d)
def routed_full(d): return getattr(R, f"evaluate_{fam}")(d, full_output=True)


def grid():
    out = []
    bases = A.bases(20, range(-20, 91, 15))
    if fam == "B":
        for az, el, b in bases:
            for alpha in (31, 35, 39, 43):
                for delta in (40, 55, 70, 90):
                    for waz in range(-90, 181, 30): out.append(dict(b=b, az=az, el=el, alpha=alpha, delta=delta, waz=waz))
    elif fam == "C":
        for az, el, b in bases:
            for a1 in (60, 75, 90, 105, 120):
                for a2 in (60, 75, 90, 105, 120):
                    for delta in (40, 55, 70, 90):
                        for waz in range(-90, 181, 30):
                            for br in (1, -1): out.append(dict(b=b, az=az, el=el, a1=a1, a2=a2, delta=delta, waz=waz, branch=br))
    else:
        bs = A.bases(30, (-15, 15, 45, 75))
        for i, (az1, el1, b1) in enumerate(bs):
            for az2, el2, b2 in bs[i + 1:]:
                sep = math.degrees(math.acos(max(-1, min(1, np.dot(b1, b2)))))
                if not 25 <= sep <= 110: continue
                for p_ in (50, 70, 90, 110):
                    for d_ in (50, 70, 90, 110):
                        for delta in (40, 55, 70, 90):
                            for waz in range(-90, 181, 45):
                                for m in ([1, -1], [-1, 1], [1, 1], [-1, -1]):
                                    out.append(dict(b1=b1, b2=b2, az1=az1, el1=el1, az2=az2, el2=el2, p=p_, d=d_, delta=delta, waz=waz, modes=m))
    return out


if __name__ == "__main__":
    G = grid(); print(f"{fam}: {len(G)} designs, kinematic screen", flush=True)
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(3,)) as ex:
        ks = list(ex.map(kin, G, chunksize=64))
    ks.sort(key=lambda r: -r["kin"])
    print("best kinematic:", [round(100 * r["kin"], 1) for r in ks[:10]], flush=True)
    cand = [{k: v for k, v in r.items() if k != "kin"} for r in ks[:28]]
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(8,)) as ex:
        rs = list(ex.map(routed, cand, chunksize=1))
    rs.sort(key=lambda r: -r["cov"])
    print("routed (1/8 poses):", [(round(100 * r["cov"], 1), round(100 * r["kin"], 1)) for r in rs[:8]], flush=True)
    top = [{k: v for k, v in r.items() if k in cand[0]} for r in rs[:6]]
    with cf.ProcessPoolExecutor(max_workers=W, initializer=init, initargs=(2,)) as ex:
        full = list(ex.map(routed_full, top, chunksize=1))
    full.sort(key=lambda r: -r["cov"])
    for r in full[:4]:
        print(f"  cov {100 * r['cov']:5.1f}%  kinematic {100 * r['kin']:.1f}%  " + "  ".join(f"{k} {v}" for k, v in r.items() if k in ('az', 'el', 'az1', 'el1', 'az2', 'el2', 'alpha', 'a1', 'a2', 'p', 'd', 'delta', 'waz', 'branch', 'modes', 'post_centre', 'radius')), flush=True)
    json.dump(full, open(f"design_search_routed_{fam}_{int(RMAX)}.json", "w"))
