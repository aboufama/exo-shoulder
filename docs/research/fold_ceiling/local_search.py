"""fold-ceiling step 3a: local search on the parking proxy (hub2_bound.multi_eval) from the best random designs: maximise
the fast-bench reach with every rigid part's in-band floor tau (default 0.8) and follow >= 0.95, J1 inside the user's
ruling (acromion top az 60-135 el >= 50, or back of the shoulder az -60..90 el 0..50). Reports kin360 / held kinematics.
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/fold_ceiling/local_search.py [tau] [iters]"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import hub2_bound as H  # noqa: E402
K = H.K
tau = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8; iters = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
res = json.load(open(os.path.join(HERE, "hub2_bound.json")))
starts = [r for r in res[f"best_strict_tau{tau}"]][:3] if f"best_strict_tau{tau}" in res else []
L0 = json.load(open(os.path.join(HERE, "lost_poses_roller-longdyad-knuckle-3r.json")))
starts.append(dict(az1=95.39, el1=67.90, d3=77.25, a3=-8.2, a1=L0["a1"], a2=L0["a2"], a1max=L0["a1max"], sg=-1.0))   # the leader (approx u3)
L = json.load(open(os.path.join(HERE, "lost_poses_roller-longdyad-knuckle-3r.json")))
KEYS = ("az1", "el1", "d3", "a3", "a1", "a2", "a1max", "bk1")
STEP = dict(az1=4, el1=4, d3=4, a3=5, a1=3, a2=3, a1max=3, bk1=1.5)
DK = float(os.environ.get("FC_DK", 25.0))      # K's a1e range (the leaders open 21 deg; a1max <= bk1 + bk2 - 5 <= 75)


def strict(x): return (x["el1"] >= 50 and 60 <= x["az1"] <= 135) or (-60 <= x["az1"] <= 90 and 0 <= x["el1"] < 50)


def score(x):
    if not strict(x) or x["a1max"] < x["a1"] or x["a1"] < 15 or x["a2"] < 20 or x["a1max"] > min(75.0, x["a1"] + DK) or not 24 <= x["bk1"] <= 34: return -1, None
    m = H.multi_eval(K.bvec(x["az1"], x["el1"]), K.wdir(x["d3"], x["a3"]), x["a1"], x["a2"], x["a1max"], x["sg"], taus=(tau,), bk1=x["bk1"], sK=x["sK"])
    e = H.design_eval(K.bvec(x["az1"], x["el1"]), K.wdir(x["d3"], x["a3"]), x["a1"], x["a2"], x["a1max"], x["sg"], F2_grid=[1e9])
    R = m[tau][0]
    return R + 0.25 * e["kin360"], dict(R160=R, follow=m[tau][1], ovh160=m[tau][2], kin360=e["kin360"], kinH=e["kinH"])


rng = np.random.default_rng(11); out = []
for s in starts:
    x = {k: float(s[k]) for k in KEYS if k in s}; x["sg"] = float(s["sg"]); x["bk1"] = 28.0; x["a1max"] = min(x["a1max"], 75.0, x["a1"] + DK)
    best = None
    for sK in (-1.0, 1.0):
        x["sK"] = sK; f, info = score(x)
        if best is None or f > best[0]: best = (f, info, dict(x))
    f, info, x = best
    for it in range(iters // max(1, len(starts))):
        y = dict(x)
        for k in rng.choice(KEYS, size=rng.integers(1, 4), replace=False): y[k] += rng.normal(0, STEP[k])
        g, inf2 = score(y)
        if g > f: x, f, info = y, g, inf2
    out.append(dict(x=x, f=f, **info)); print(json.dumps(out[-1]), flush=True)
json.dump(dict(tau=tau, results=out), open(os.path.join(HERE, f"local_search_tau{tau}.json"), "w"), indent=1, default=float)
