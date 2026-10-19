"""fold-ceiling step 2a': the kinematic window ceiling restricted to seat regions where hubs have been parked in band
(J1 high: el >= 50 - acromion top / high back; J3 on the lateral arm d 45-110, |a| <= 60) vs the whole ruling.
Same exact counting as kin_ceiling.py (0.5 deg histogram, winner re-counted exactly), Bench(110,360) 360 ws poses,
held out = the SAME seats and window on the 952 held-out workspace poses."""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import importlib.util
sp = importlib.util.spec_from_file_location("kc", os.path.join(HERE, "kin_ceiling.py"))
src = open(os.path.join(HERE, "kin_ceiling.py")).read().split("# seat grids")[0]
G = {"__file__": os.path.join(HERE, "kin_ceiling.py")}; exec(compile(src, "kin_ceiling_head", "exec"), G)
K, QB, QH, th_of, lead = G["K"], G["QB"], G["QH"], G["th_of"], G["lead"]


def scan(A1, A3, Ws, tag):
    U1 = K.bvec(np.array([a for a, e in A1]), np.array([e for a, e in A1])); U3 = K.wdir(np.array([x for x, y in A3]), np.array([y for x, y in A3]))
    TH = th_of(QB, U1, U3); na, nb, P = TH.shape; nbin = 361
    bins = np.clip(np.floor(TH * 2).astype(np.int32), 0, nbin - 1).reshape(na * nb, P); del TH
    H = np.zeros((na * nb, nbin), np.int16)
    for j in range(P): H[np.arange(na * nb), bins[:, j]] += 1
    C = np.concatenate([np.zeros((na * nb, 1), np.int16), np.cumsum(H, 1, dtype=np.int16)], 1)
    res = {}
    for W in Ws:
        w2 = int(math.ceil(W * 2)) + 1; los = np.arange(10, nbin - w2 + 1)
        cnt = C[:, los + w2] - C[:, los]; best = cnt.max(1); k = int(np.argmax(best)); lo_b = los[np.argmax(cnt[k])] / 2.0
        ka, kb = divmod(k, nb)
        thb = th_of(QB, U1[ka][None], U3[kb][None])[0, 0]; thh = th_of(QH, U1[ka][None], U3[kb][None])[0, 0]
        res[str(W)] = dict(bench=round(float(((thb >= lo_b) & (thb <= lo_b + W)).mean()), 4), held=round(float(((thh >= lo_b) & (thh <= lo_b + W)).mean()), 4),
                           lo=lo_b, seat1=[float(x) for x in A1[ka]], seat3=[float(x) for x in A3[kb]])
        print(tag, W, res[str(W)], flush=True)
    return res


az = np.arange(-90, 136, 5.0); el = np.arange(50, 86, 5.0)
A1_high = [(a, e) for a in az for e in el]
A3_lat = [(x, y) for x in np.arange(45, 111, 5.0) for y in np.arange(-60, 61, 5.0)]
Ws = (86.3, 90, 95, 100, 105, 110)
out = dict(note="J1 el >= 50 (acromion top + high back), J3 d 45-110 |a| <= 60", high_lat=scan(A1_high, A3_lat, Ws, "J1 high, J3 lateral"))
# the leader's J1 seat fixed, J3 free on the lateral arm: how much does re-seating J3 alone buy at the leader's width?
u1L = np.array(lead["u1"]); el1 = math.degrees(math.asin(u1L[1])); az1 = math.degrees(math.atan2(u1L[2], -u1L[0]))
out["leaderJ1_J3free"] = scan([(az1, el1)], A3_lat, Ws, "leader J1, J3 lateral")
json.dump(out, open(os.path.join(HERE, "kin_ceiling_regions.json"), "w"), indent=1, default=float)
