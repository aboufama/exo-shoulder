"""focused RSSR sweep for the ~75 deg stroke target (lead, 2026-10-17 07:00): the horn phased so its arm is
perpendicular to the rod near mid-stroke (beta0 ~ -90 - 37.5 for K sense -1), the crank phase gam scanned so the
crank's in-plane pressure angle straddles 0 at mid-swing, g = La / r_h 1.1-2.0 (crank swing phi = dK / g within the
hub-2 lobe's skirt, lift s_arm phi <= 11.5 - r_lobe); both K dyads the fold analysis prices (28 / 50, 32 / 48).
    python3 docs/research/longstroke_drive/make_configs75.py [n] [seed]"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 240; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
SP = {"La": (16.0, 26.0), "s_arm": (4.0, 4.6), "r_h": (13.0, 17.0), "beta": (-150.0, -100.0), "gam": (-20.0, 70.0),
      "hl": (0.0, 3.15), "zr": (1.0, 5.0), "kK": (1.5, 2.3), "r_lobe": (7.0, 7.8)}
rng = np.random.default_rng(seed); keys = list(SP); m = len(keys)
U = (rng.permuted(np.tile(np.arange(n), (m, 1)), axis=1).T + rng.random((n, m))) / n
cf = []
for i in range(n):
    c = {k: round(SP[k][0] + U[i, j] * (SP[k][1] - SP[k][0]), 4) for j, k in enumerate(keys)}
    c.update({"bk1": 28.0, "bk2": 50.0, "a1max": 73.0} if i % 2 == 0 else {"bk1": 32.0, "bk2": 48.0, "a1max": 75.0})
    c["ball_low"] = 0; cf.append(c)
json.dump(cf, open(os.path.join(HERE, "cfg_rssr75.json"), "w")); print(len(cf))
