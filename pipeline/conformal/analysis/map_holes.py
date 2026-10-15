"""Sampling holes in the evaluator's skin maps near the map pole (straight up from the GH centre, the top of the shoulder).

build_frame_maps (band_impl.py) bins skin samples (~0.8 mm apart) into 0.5 x 0.5 deg pixels and fills holes with the
1-ring only. A pixel spans 0.5 * cos(lat) deg of longitude, so above lat ~65 deg most pixels get no sample: r1 = 0
there ("no skin"), although every ray from the GH centre leaves the closed body. Effects on the evaluator: no clearance
constraint there (LO = r1c - 1 = -1, metal may sit inside the skin) and never in band (CAP = 0 + G / cs).

fill(M): per row, the first sheet r1 of a hole pixel = the min of the nonzero r1 within +-K(lat) longitude pixels
(K = ceil(1.5 / cos(lat)), the 1-ring's angular width at the equator scaled to the row), r1c = the max of the nonzero
r1c in the same window (conservative: the higher band start), cs and r2c untouched (cs is already 1 next to holes).
Pixels with no sample in their window stay holes. In memory only (the cached file is not changed).

    python3 map_holes.py            -> hole share by latitude before / after, over all 451 frames"""
import math, os, sys
import numpy as np, torch
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "gpu")); import band_impl as BI
from scipy.ndimage import minimum_filter1d, maximum_filter1d

def fill(M, lat_min=30.0):
    MH, MW = BI.MH, BI.MW; lat = BI.LAT_LO + (np.arange(MH) + 0.5) * BI.MRES
    r1 = M["r1"].float().view(-1, MH, MW).numpy(); r1c = M["r1c"].float().view(-1, MH, MW).numpy()
    K = np.ceil(1.5 / np.clip(np.cos(np.radians(lat)), 0.02, 1)).astype(int)
    out1, outc = r1.copy(), r1c.copy()
    for k in np.unique(K[lat >= lat_min]):
        rows = np.nonzero((K == k) & (lat >= lat_min))[0]
        if k <= 1 or not len(rows): continue
        a = r1[:, rows]; c = r1c[:, rows]; hole = a <= 0
        amin = minimum_filter1d(np.where(hole, np.inf, a), size=2 * k + 1, axis=2, mode="wrap")
        cmax = maximum_filter1d(np.where(hole, -np.inf, c), size=2 * k + 1, axis=2, mode="wrap")
        ok = hole & np.isfinite(amin)
        out1[:, rows] = np.where(ok, amin, a); outc[:, rows] = np.where(ok, cmax, c)
    M2 = dict(M); M2["r1"] = torch.from_numpy(out1.reshape(len(r1), -1)).half(); M2["r1c"] = torch.from_numpy(outc.reshape(len(r1), -1)).half()
    return M2

def hole_share(M, lats=(40, 50, 60, 65, 70, 75, 80, 85, 88)):
    MH, MW = BI.MH, BI.MW; lat = BI.LAT_LO + (np.arange(MH) + 0.5) * BI.MRES; R = M["r1"].float().view(-1, MH, MW)
    return {a: round(float((R[:, np.abs(lat - a) < 1.0] <= 0).float().mean()), 3) for a in lats}

if __name__ == "__main__":
    M = torch.load(os.path.join(HERE, "..", "..", "..", ".cache", "maps_s1.pt"))
    print("share of pixels with no skin, by latitude (deg), all frames:")
    print("  cached maps:", hole_share(M)); M2 = fill(M); print("  filled     :", hole_share(M2))
