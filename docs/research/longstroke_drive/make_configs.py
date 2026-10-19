"""coarse drive-pricing sweeps for longstroke-slipper-knuckle-3r: Latin-hypercube configs per drive at the 28 / 50 K dyad
(a1max 73), the lead's seats; one file per drive (LS_DRIVE nose / roller / rssr).
    python3 docs/research/longstroke_drive/make_configs.py [n] [seed]"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
n = int(sys.argv[1]) if len(sys.argv) > 1 else 240; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
DYAD = {"bk1": 28.0, "bk2": 50.0, "a1max": 73.0}
SPACE = {
    "cam": {"g": (1.3, 3.0), "beta": (-180.0, -60.0), "r_c": (13.0, 22.0), "lift": (0.0, 4.0), "hl": (0.0, 3.15), "zr": (0.0, 5.0),
            "kK": (1.6, 2.6), "s_arm": (4.0, 6.0), "r_lobe": (7.0, 8.5), "nose_r": (1.0, 1.5)},
    "rssr": {"La": (12.0, 26.0), "s_arm": (4.0, 6.0), "r_h": (13.0, 22.0), "beta": (-180.0, 180.0), "gam": (-60.0, 60.0),
             "hl": (0.0, 3.15), "zr": (0.0, 5.0), "kK": (1.6, 2.6), "r_lobe": (7.0, 8.5)},
}


def lhs(space, n, rng):
    keys = list(space); m = len(keys); U = (rng.permuted(np.tile(np.arange(n), (m, 1)), axis=1).T + rng.random((n, m))) / n
    return [dict(DYAD, **{k: round(space[k][0] + U[i, j] * (space[k][1] - space[k][0]), 4) for j, k in enumerate(keys)}) for i in range(n)]


for drive, sp in (("nose", "cam"), ("roller", "cam"), ("rssr", "rssr")):
    rng = np.random.default_rng(seed + {"nose": 0, "roller": 100, "rssr": 200}[drive])
    cf = lhs(SPACE[sp], n, rng)
    if drive == "rssr":
        for c in cf: c["ball_low"] = int(rng.random() < 0.3)
    json.dump(cf, open(os.path.join(HERE, f"cfg_coarse_{drive}.json"), "w"))
    print(drive, len(cf))
