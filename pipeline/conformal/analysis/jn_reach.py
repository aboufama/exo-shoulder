"""Can a pure 3R chain keep its range with the arm-fixed joint JN (axis W, humerus frame) on low-motion skin? Pure
kinematics, no skin maps: for the J1 axis b (scapula frame) and a candidate W, the angle theta between b and the posed
W over every pose of a payload; a 3R chain with arcs (a1, a2) closes at a pose iff theta lies in
[|a1 - a2| + s, min(a1 + a2, 360 - a1 - a2) - s] (s = the evaluator's sing_deg, 10). Reported per W: the theta range
over the workspace poses / fit clips and the share of poses inside the window of the best arcs >= min_arc (60).

    python3 jn_reach.py <cad input json> [W delta,az ...]"""
import base64, gzip, io, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "gpu")); import band_impl as BI
R = json.load(open(sys.argv[1]))["results"][0]; Ws = [tuple(float(x) for x in s.split(",")) for s in sys.argv[2:]] or [tuple(R["w"])]
Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(HERE, "..", "band_poses_wsf.b64")).read()))), allow_pickle=False)
names = [str(x) for x in Z["NAMES"]]; cid = Z["CID"]; HG = Z["HG"]
env = np.array([names[c] == "Workspace (envelope)" for c in cid]); fit = np.isin(np.array(names)[cid], R.get("fit_clips") or [])
b = np.array(BI.bvec(R["az"], R["el"])); S = 10.0; AMIN, AMAX = 60.0, 115.0
A = np.arange(AMIN, AMAX + 0.1, 1.0)
def best_arcs(th):
    best = (0, None)
    for a1 in A[::2]:
        for a2 in A[::2]:
            lo, hi = abs(a1 - a2) + S, min(a1 + a2, 360 - a1 - a2) - S; sh = float(((th >= lo) & (th <= hi)).mean())
            if sh > best[0]: best = (sh, (a1, a2))
    return best
th_of = lambda W: np.degrees(np.arccos(np.clip(np.einsum("pij,j->pi", HG, np.array(BI.w_dir(*W))) @ b, -1, 1)))
own = th_of(tuple(R["w"])); lo, hi = abs(R["a"][0] - R["a"][1]) + S, min(sum(R["a"]), 360 - sum(R["a"])) - S
print(f"design b (az {R['az']:.1f}, el {R['el']:.1f}), arcs {[round(x, 1) for x in R['a']]}: closure window [{lo:.0f}, {hi:.0f}] deg")
for W in Ws:
    th = th_of(W); wsh = ((th[env] >= lo) & (th[env] <= hi)).mean(); fsh = ((th[fit] >= lo) & (th[fit] <= hi)).mean()
    be, bf = best_arcs(th[env]), best_arcs(th[fit])
    print(f"W {W}: theta workspace {th[env].min():5.1f}-{th[env].max():5.1f} (p5-p95 {np.percentile(th[env], 5):5.1f}-{np.percentile(th[env], 95):5.1f}), fit clips {th[fit].min():5.1f}-{th[fit].max():5.1f};"
          f" design arcs close {100 * wsh:5.1f} % of workspace / {100 * fsh:5.1f} % of fit frames; best arcs {be[1]} close {100 * be[0]:5.1f} % of workspace (fit clips {100 * best_arcs(th[fit])[0]:5.1f} %)")
