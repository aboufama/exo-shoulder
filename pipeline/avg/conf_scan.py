"""random scan of D4 designs with J4 // elbow axis (flat BOTTOM), conformal links: coverage vs skin gap"""
import json, math, os, random, sys
import numpy as np
import concurrent.futures as cf
import conformal as CF
import design_search as D
FIX = json.load(open("fix_w_tea.json"))
def bvec(az, el): return [-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)]
def rnd(seed):
    r = random.Random(seed)
    while True:
        az, el = r.uniform(0, 360), r.uniform(-10, 90); b = np.array(bvec(az, el))
        if b[0] <= 0.3 and b[1] >= -0.2: break
    return dict(b=list(bvec(az, el)), az=round(az, 1), el=round(el, 1), a1=round(r.uniform(30, 110), 1), a2=round(r.uniform(30, 110), 1),
                a3=round(r.uniform(30, 110), 1), delta=FIX["delta"], waz=FIX["waz"], branch=r.choice([-1, 1]))
def run(seed):
    d = rnd(seed); out = []
    for keep in (0.85, 0.95):
        try: r = CF.evaluate(d, stride=4, q_step=12, keep=keep); out.append(r)
        except Exception as e: pass
    return out
if __name__ == "__main__":
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 160
    res = []
    with cf.ProcessPoolExecutor(4) as ex:
        for rr in ex.map(run, range(N), chunksize=2): res += rr
    res = [r for r in res if r["cov"] > 0.05]
    json.dump(res, open("conf_scan.json", "w"))
    res.sort(key=lambda r: -r["cov"])
    print("best coverage:"); [print(f"  cov {100*r['cov']:.1f}% p50 {r['gap_p50']:.1f} p90 {r['gap_p90']:.1f} within10 {100*r['within']:.0f}% az {r['az']} el {r['el']} a {r['a1']}/{r['a2']}/{r['a3']} br {r['branch']}") for r in res[:6]]
    res.sort(key=lambda r: r['gap_p90'])
    print("lowest p90 gap (cov > 5%):"); [print(f"  cov {100*r['cov']:.1f}% p50 {r['gap_p50']:.1f} p90 {r['gap_p90']:.1f} within10 {100*r['within']:.0f}% az {r['az']} el {r['el']} a {r['a1']}/{r['a2']}/{r['a3']} br {r['branch']}") for r in res[:6]]
