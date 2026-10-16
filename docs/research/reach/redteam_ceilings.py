"""Red team of the reach ceilings (2026-10-16): own random + local search of the plain-3R fold ceiling on the 360 workspace
poses of Bench(110,360), free seats vs seats inside the user's J1 ruling (back of the shoulder + acromion top), and the
160-vs-360 sampling bias for random seats (is the fast-to-frozen reach loss the CMA tuning the window to 160 poses, or a
bias of the 160-pose sample that every seat sees?). No code shared with ceilings.py / attribute.py.

Seat regions (stated, approximate): J1 'allowed' = bvec az in [-120, 120] (not over the front / clavicle) and el in
[-10, 90]; J3 'arm side' = wdir d in [45, 110] (between down-the-arm and a little above horizontal), a in [-120, 120]
(not the medial face against the trunk). 'Free' = anywhere on the sphere.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/reach/redteam_ceilings.py [out.json]
"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

rng = np.random.default_rng(7)


def bv(az, el):
    az, el = np.radians(az), np.radians(el)
    return np.stack([-np.cos(el) * np.cos(az), np.sin(el), np.cos(el) * np.sin(az)], -1)


def wd(d, a):
    d, a = np.radians(d), np.radians(a)
    return np.stack([np.sin(d) * np.sin(a), -np.cos(d), np.sin(d) * np.cos(a)], -1)


def share(U1, U3, a1, a2, Q, m=10.0):
    """U1 (k,3), U3 (k,3) paired seats -> in-window share (k,) on poses Q (n,3,3)"""
    lo, hi = abs(a1 - a2) + m, min(a1 + a2, 360 - a1 - a2) - m
    W = np.einsum("nij,kj->kni", Q, U3)
    th = np.degrees(np.arccos(np.clip(np.einsum("kni,ki->kn", W, U1), -1, 1)))
    return ((th >= lo) & (th <= hi)).mean(1)


def strict_ok(az, el): return ((az <= 90) | (el >= 50)) & (az >= -90) & (az <= 135) & (el >= 0)


def sample(k, region):
    if region == "free":
        x = rng.normal(size=(k, 3)); u1 = x / np.linalg.norm(x, axis=1, keepdims=True)
        x = rng.normal(size=(k, 3)); u3 = x / np.linalg.norm(x, axis=1, keepdims=True)
        return u1, u3, None
    if region == "strict":                                    # back of the shoulder (az -90..90) or acromion top (az 90..135, el >= 50)
        az1 = rng.uniform(-90, 135, 4 * k); el1 = np.degrees(np.arcsin(rng.uniform(0, 1, 4 * k)))
        keep = np.nonzero(strict_ok(az1, el1))[0][:k]; az1, el1 = az1[keep], el1[keep]
        d3 = rng.uniform(45, 110, k); a3 = rng.uniform(-100, 100, k)
        return bv(az1, el1), wd(d3, a3), np.stack([az1, el1, d3, a3], 1)
    az1 = rng.uniform(-120, 120, k); el1 = np.degrees(np.arcsin(rng.uniform(math.sin(math.radians(-10)), 1, k)))
    d3 = rng.uniform(45, 110, k); a3 = rng.uniform(-120, 120, k)
    return bv(az1, el1), wd(d3, a3), np.stack([az1, el1, d3, a3], 1)


def search(a1, a2, Q, region, n=60000, top=12, steps=400):
    u1, u3, par = sample(n, region)
    s = np.concatenate([share(u1[i:i + 2000], u3[i:i + 2000], a1, a2, Q) for i in range(0, n, 2000)])
    best = []
    for j in np.argsort(-s)[:top]:
        if region == "free":
            x1, x3, sc = u1[j].copy(), u3[j].copy(), s[j]
            for t in range(steps):
                sig = 0.15 * (1 - t / steps) + 0.01
                c1 = x1 + rng.normal(scale=sig, size=(16, 3)); c1 /= np.linalg.norm(c1, axis=1, keepdims=True)
                c3 = x3 + rng.normal(scale=sig, size=(16, 3)); c3 /= np.linalg.norm(c3, axis=1, keepdims=True)
                cs = share(c1, c3, a1, a2, Q); k = int(np.argmax(cs))
                if cs[k] >= sc: x1, x3, sc = c1[k], c3[k], cs[k]
            best.append(dict(share=round(float(sc), 4), u1=np.round(x1, 4).tolist(), u3=np.round(x3, 4).tolist()))
        else:
            p, sc = par[j].copy(), s[j]
            lo = np.array([-120, -10, 45, -120]); hi = np.array([120, 90, 110, 120])
            if region == "strict": lo = np.array([-90, 0, 45, -100]); hi = np.array([135, 90, 110, 100])
            for t in range(steps):
                sig = 8.0 * (1 - t / steps) + 0.5
                C = np.clip(p + rng.normal(scale=sig, size=(16, 4)), lo, hi)
                cs = share(bv(C[:, 0], C[:, 1]), wd(C[:, 2], C[:, 3]), a1, a2, Q)
                if region == "strict": cs = np.where(strict_ok(C[:, 0], C[:, 1]), cs, -1.0)
                k = int(np.argmax(cs))
                if cs[k] >= sc: p, sc = C[k], cs[k]
            best.append(dict(share=round(float(sc), 4), az1=round(float(p[0]), 1), el1=round(float(p[1]), 1), wd=round(float(p[2]), 1), wa=round(float(p[3]), 1)))
    best.sort(key=lambda r: -r["share"])
    return best[:3]


def main_strict(out):
    Z = CB._poses_all(); HG = Z["HG"].astype(float)
    idx, *_ = CB._select(110, 360); Q360 = HG[idx[110:]]
    idx60, *_ = CB._select(60, 160); Q160 = HG[idx60[60:]]
    res = {}
    for a1, a2 in ((40, 73), (45, 70), (50, 50), (55, 57)):
        res[f"strict_{a1}_{a2}"] = search(a1, a2, Q360, "strict", n=30000, top=8, steps=250); print("strict", a1, a2, res[f"strict_{a1}_{a2}"][0], flush=True)
    u1, u3, _ = sample(20000, "strict"); n = len(u1)
    s160 = np.concatenate([share(u1[i:i + 2000], u3[i:i + 2000], 40, 73, Q160) for i in range(0, n, 2000)])
    s360 = np.concatenate([share(u1[i:i + 2000], u3[i:i + 2000], 40, 73, Q360) for i in range(0, n, 2000)])
    good = s360 >= 0.5; d = s160 - s360
    res["bias_160_vs_360_strict"] = dict(n=n, mean_diff_all=round(float(d.mean()), 4), mean_diff_s360_ge_0_5=round(float(d[good].mean()), 4) if good.any() else None,
                                         n_good=int(good.sum()), top100_by_160_mean_diff=round(float(d[np.argsort(-s160)[:100]].mean()), 4))
    print("bias strict", res["bias_160_vs_360_strict"], flush=True)
    json.dump(res, open(out, "w"), indent=1)


def main(out):
    Z = CB._poses_all(); HG = Z["HG"].astype(float)
    idx, *_ = CB._select(110, 360); Q360 = HG[idx[110:]]
    idx60, *_ = CB._select(60, 160); Q160 = HG[idx60[60:]]
    res = {}
    for a1, a2 in ((40, 40), (45, 45), (50, 50), (40, 73)):
        res[f"free_{a1}_{a2}"] = search(a1, a2, Q360, "free"); print("free", a1, a2, res[f"free_{a1}_{a2}"][0], flush=True)
    for a1, a2 in ((40, 73), (50, 50), (55, 57), (45, 70), (60, 60)):
        res[f"allowed_{a1}_{a2}"] = search(a1, a2, Q360, "allowed"); print("allowed", a1, a2, res[f"allowed_{a1}_{a2}"][0], flush=True)
    # 160 vs 360 sampling bias over random allowed seats at the leaders' arcs (40 / 73)
    u1, u3, _ = sample(20000, "allowed")
    s160 = np.concatenate([share(u1[i:i + 2000], u3[i:i + 2000], 40, 73, Q160) for i in range(0, 20000, 2000)])
    s360 = np.concatenate([share(u1[i:i + 2000], u3[i:i + 2000], 40, 73, Q360) for i in range(0, 20000, 2000)])
    good = s360 >= 0.5
    d = s160 - s360
    res["bias_160_vs_360"] = dict(n=20000, mean_diff_all=round(float(d.mean()), 4), mean_diff_s360_ge_0_5=round(float(d[good].mean()), 4),
                                  p10_p90_s360_ge_0_5=[round(float(np.percentile(d[good], q)), 4) for q in (10, 90)],
                                  n_good=int(good.sum()),
                                  top100_by_160_mean_diff=round(float(d[np.argsort(-s160)[:100]].mean()), 4))
    print("bias", res["bias_160_vs_360"], flush=True)
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--strict": main_strict(os.path.join(HERE, "redteam_ceilings_strict.json"))
    else: main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "redteam_ceilings.json"))
