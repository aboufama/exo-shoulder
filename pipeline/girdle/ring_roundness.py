"""Is the upper arm round enough for a humeral-rotation ring centred on the humerus axis? Rig skin (avg/body_pose.py),
arm hanging (plane = elev = axial = 0, canonical humerus frame = thorax: humerus axis -y through the GH centre),
elbow flexion 0..140 deg. Per station s (mm from GH along the humerus): the skin radius r(theta) about the humerus axis
(theta about -y, 0 = lateral +z, 90 = anterior +x), its envelope over flexion (the biceps bulge), and for a circular ring
of the best radius: the gap range a rail point sees as the arm turns under it by the ring travel (P0: ~120-160 deg).
    python3 ring_roundness.py  -> ring_roundness.json"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "avg")); import body_pose as BP
FLEX = [0, 30, 60, 90, 120, 140]; ST = list(range(60, 281, 20)); TH = np.arange(-180, 180, 5.0)
rig = BP._rig(); sk = rig.skin; Wt = np.zeros((sk["n"], 5)); np.add.at(Wt, (np.repeat(np.arange(sk["n"]), 4), sk["wi"].ravel()), sk["ww"].ravel())
arm = Wt[:, 2] > 0.5; R = {}                                                 # skin driven by the humerus only (not forearm / hand)
for fx in FLEX:
    X = BP.posed(dict(plane=0, elev=0, axial=0, flex=fx, pron=0))[arm]
    s = -X[:, 1]; th = np.degrees(np.arctan2(X[:, 0], X[:, 2])); r = np.hypot(X[:, 0], X[:, 2])
    for st in ST:
        m = (np.abs(s - st) < 3.0) & (r < 110); b = np.round((th[m] + 180) / 5).astype(int) % len(TH); rr = np.full(len(TH), np.nan)
        for k, v in zip(b, r[m]): rr[k] = v if np.isnan(rr[k]) else max(rr[k], v)       # outermost skin in the bin
        ok = np.isfinite(rr)
        if ok.sum() >= 8:                                                  # fill empty bins: circular linear interpolation
            xs = np.r_[TH[ok] - 360, TH[ok], TH[ok] + 360]; ys = np.r_[rr[ok], rr[ok], rr[ok]]; rr = np.interp(TH, xs, ys)
        R[(fx, st)] = rr
out = {}
for st in ST:
    A = np.array([R[(fx, st)] for fx in FLEX]); env = np.nanmax(A, 0); low = np.nanmin(A, 0)
    valid = np.isfinite(env)
    rec = dict(radius_min=round(float(np.nanmin(env)), 1), radius_max=round(float(np.nanmax(env)), 1),
               bulge_max=round(float(np.nanmax(env - low)), 1), bulge_at_theta=float(TH[np.nanargmax(env - low)]))
    # a ring arc on link 2 sees arm angles theta = psi - phi(t), phi spanning TRAVEL; for each travel, best circular
    # radius and the worst in-band spread (max - min skin radius over the swept theta, flexion envelope + relaxed)
    for trav in (90, 120, 160):
        best = None
        for c in TH:                                                       # centre of the swept window (deg)
            w = ((TH - c + 180) % 360 - 180); win = np.abs(w) <= trav / 2 + 15          # + carriage half-width ~15 deg
            if not valid[win].all(): continue
            spread = float(np.nanmax(env[win]) - np.nanmin(low[win]))
            if best is None or spread < best[0]: best = (spread, float(c), float(np.nanmax(env[win])))
        rec[f"travel_{trav}"] = None if best is None else dict(skin_spread_mm=round(best[0], 1), window_centre_deg=best[1], ring_radius_min=round(best[2] + 2, 1))
    out[str(st)] = rec
    t160 = rec["travel_160"]; t120 = rec["travel_120"]
    print(f"s {st:3d} mm: skin radius {rec['radius_min']:5.1f}-{rec['radius_max']:5.1f}, bulge <= {rec['bulge_max']:4.1f} mm (theta {rec['bulge_at_theta']:+.0f})  |  "
          f"spread seen by a ring: 120 deg travel {t120 and t120['skin_spread_mm']} mm, 160 deg {t160 and t160['skin_spread_mm']} mm (window centre {t160 and t160['window_centre_deg']})", flush=True)
json.dump(dict(note=__doc__.split(chr(10))[0], flex=FLEX, stations=out), open(os.path.join(HERE, "ring_roundness.json"), "w"), indent=1)
