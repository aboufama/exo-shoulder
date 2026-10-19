"""audit: law-only J1-J3 window of the knuckle 4R per K-dyad (bk1, bk2) at the skinnormal seats: folded-side min th and
stretched-side max th reachable with J2 locked on its stops, K turning in its opening direction (one-way, <= stop B at the
5.5 cap) or either way (two-way), every kit margin >= 5.5."""
import importlib.util, json, math, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("sk4r", os.path.join(REPO, "docs/concepts/models/skinnormal-shortk-knuckle-4r.py"))
M = importlib.util.module_from_spec(sp); sp.loader.exec_module(M)
KR = M.KR; S = KR.S; D2R = math.pi / 180
B = M.CB.Bench(n_clip=6, n_ws=10)
def window(par):
    P, info = M.full(par); P = dict(P); P["a1max"] = float(P["bk1"]) + float(P["bk2"]) - 5.51
    Mod = KR.KB.KModel(B, dict(P)); D = Mod.D
    if not (D.k_ok and D.stops_ok): return None
    sg = D.q2sgn or 1.0; u1, u2, u3 = D.u; uK = D.uK; b1 = float(P["bk1"]); a2 = D.a2
    cps = (math.cos(P["a1max"] * D2R) - math.cos(b1 * D2R) * math.cos(float(P["bk2"]) * D2R)) / (math.sin(b1 * D2R) * math.sin(float(P["bk2"]) * D2R))
    dKB = math.degrees(abs(math.acos(max(-1, min(1, cps))) - abs(D.psiA))); s = np.sign(D.psiA)
    out = dict(a1=round(D.a1, 2), a2=round(a2, 2), thlo=round(D.th_lo, 2), thhi=round(D.th_hi, 2), dKB=round(dKB, 1))
    for lab, q2s in (("fold", D._q2_at(D.th_lo, sg)), ("str", D._q2_at(D.th_hi, sg))):
        p = S.rotm(u2, np.array([q2s]))[0] @ u3; cK = math.degrees(math.acos(np.clip(p @ uK, -1, 1)))
        d = np.radians(np.arange(-180, 180.01, 0.5)); R = S.rotm(uK, d); th = np.degrees(np.arccos(np.clip((R @ p) @ u1, -1, 1)))
        a1e = np.degrees(np.arccos(np.clip((R @ u2) @ u1, -1, 1)))
        ms = np.minimum.reduce([th - abs(b1 - cK), b1 + cK - th, 360 - b1 - cK - th]); m3 = np.minimum.reduce([th - abs(a1e - a2), a1e + a2 - th, 360 - a1e - a2 - th])
        ok = (ms >= 5.5) & (m3 >= 5.5); one = ok & (np.degrees(d) * s >= 0) & (np.abs(np.degrees(d)) <= dKB)
        # connected from dK = 0 (the reachable branch: K turns continuously from stop A)
        def conn(mask):
            i0 = 360; 
            if not mask[i0]: 
                # state A boundary pose itself may sit just under margin: allow start within 1 deg
                pass
            lo = hi = i0
            while hi + 1 < len(mask) and mask[hi + 1]: hi += 1
            while lo - 1 >= 0 and mask[lo - 1]: lo -= 1
            return lo, hi
        f = np.min if lab == "fold" else np.max
        out[lab + "_cK"] = round(cK, 1)
        out[lab + "_one"] = round(float(f(th[one])), 1) if one.any() else None
        out[lab + "_two"] = round(float(f(th[ok])), 1) if ok.any() else None
    return out
base = {}
print("seed", window(base))
for bk1 in (20, 25, 29.65, 35, 40):
    for bk2 in (20, 25, 30, 35, 40.7, 48, 56):
        try: w = window(dict(bk1=bk1, bk2=bk2))
        except Exception as e: w = repr(e)[:80]
        print(bk1, bk2, w)
