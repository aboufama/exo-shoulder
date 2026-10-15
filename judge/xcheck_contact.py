"""Outside check of the contact judges (R2 judge/body_contact.py, R6 judge/part_contact.py): re-measures the top entries
of a design's judge output at their worst frame with nothing from judge/sdist.py. Inside = winding number by signed ray
crossings (sum of sign(n . d) over the hits t > 0) along 3 random directions on the RAW glb tessellation (unwelded),
majority vote; ray parity is reported alongside (it differs where the posed body overlaps itself). Depth = exact closest
point by brute force over all triangles (inside points only, deepest first, pruned by the distance to the nearest vertex,
an upper bound). R2 entries of the merged BOTTOM are split into the user's bar (s < 265 along the bar, arm_fit.json) and
the new neck / arm end.
    python3 judge/xcheck_contact.py <design dir|id> [--top 8]  -> <design>/judge/xcheck_contact.json"""
import argparse, json, os
import numpy as np
from scipy.spatial import cKDTree
from common import design_dir, load_parts, PIPE
S_CUT = 265.0                                                                 # the user's BOTTOM is cut here (arm_end.py)


def closest_on_tri(P, A, B, C):
    """Ericson's closest point on a triangle, broadcasting over leading axes"""
    ab, ac, ap = B - A, C - A, P - A
    d1 = (ab * ap).sum(-1); d2 = (ac * ap).sum(-1)
    bp = P - B; d3 = (ab * bp).sum(-1); d4 = (ac * bp).sum(-1)
    cp = P - C; d5 = (ab * cp).sum(-1); d6 = (ac * cp).sum(-1)
    vc = d1 * d4 - d3 * d2; vb = d5 * d2 - d1 * d6; va = d3 * d6 - d5 * d4
    den = va + vb + vc; den = np.where(np.abs(den) < 1e-18, 1e-18, den)
    Q = A + ab * (vb / den)[..., None] + ac * (vc / den)[..., None]
    for m, X in (((va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0), B + (C - B) * ((d4 - d3) / np.maximum((d4 - d3) + (d5 - d6), 1e-18))[..., None]),
                 ((vb <= 0) & (d2 >= 0) & (d6 <= 0), A + ac * (d2 / np.maximum(d2 - d6, 1e-18))[..., None]),
                 ((vc <= 0) & (d1 >= 0) & (d3 <= 0), A + ab * (d1 / np.maximum(d1 - d3, 1e-18))[..., None]),
                 ((d6 >= 0) & (d5 <= d6), C), ((d3 >= 0) & (d4 <= d3), B), ((d1 <= 0) & (d2 <= 0), A)):
        Q = np.where(m[..., None], X, Q)
    return Q


def brute_dist(P, V, F, chunk=8192):
    T = V[F]; best = np.full(len(P), np.inf)
    for j in range(0, len(T), chunk):
        t = T[j:j + chunk][None]
        for i in range(0, len(P), 16):
            p = P[i:i + 16, None]; Q = closest_on_tri(p, t[:, :, 0], t[:, :, 1], t[:, :, 2])
            best[i:i + 16] = np.minimum(best[i:i + 16], np.linalg.norm(p - Q, axis=-1).min(1))
    return best


def ray_crossings(P, V, F, d, cell=2.0):
    """per point: (signed crossing sum = winding number, hit count) of the ray P + t d, t > 0; candidate triangles from a
    2D bucket grid of the triangles projected along d"""
    d = d / np.linalg.norm(d); u = np.cross(d, [1.0, 0, 0] if abs(d[0]) < 0.9 else [0, 1.0, 0]); u /= np.linalg.norm(u); v = np.cross(d, u)
    T = V[F]; sg = np.sign(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]) @ d)
    tu, tv = T @ u, T @ v; pu, pv = P @ u, P @ v; o = np.array([min(tu.min(), pu.min()), min(tv.min(), pv.min())]) - 1
    i0 = np.floor((tu.min(1) - o[0]) / cell).astype(int); i1 = np.floor((tu.max(1) - o[0]) / cell).astype(int)
    j0 = np.floor((tv.min(1) - o[1]) / cell).astype(int); j1 = np.floor((tv.max(1) - o[1]) / cell).astype(int)
    nj = int(max(j1.max(), np.floor((pv.max() - o[1]) / cell))) + 1
    ni_, nj_ = i1 - i0 + 1, j1 - j0 + 1; cnt = ni_ * nj_; tri = np.repeat(np.arange(len(F)), cnt)
    loc = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt); key = (i0[tri] + loc // nj_[tri]) * nj + (j0[tri] + loc % nj_[tri])
    o_ = np.argsort(key, kind="stable"); key, tri = key[o_], tri[o_]
    pk = np.floor((pu - o[0]) / cell).astype(int) * nj + np.floor((pv - o[1]) / cell).astype(int)
    a = np.searchsorted(key, pk, "left"); c = np.searchsorted(key, pk, "right") - a
    pi = np.repeat(np.arange(len(P)), c); tj = tri[np.repeat(a, c) + (np.arange(c.sum()) - np.repeat(np.cumsum(c) - c, c))]
    W = np.zeros(len(P)); H = np.zeros(len(P))
    for k0 in range(0, len(pi), 2_000_000):                                   # Moeller-Trumbore
        p, t = pi[k0:k0 + 2_000_000], tj[k0:k0 + 2_000_000]; A = T[t, 0]; e1 = T[t, 1] - A; e2 = T[t, 2] - A
        h = np.cross(d, e2); aa = (e1 * h).sum(1); ok = np.abs(aa) > 1e-14; f = np.where(ok, 1 / np.where(ok, aa, 1), 0)
        s = P[p] - A; uu = f * (s * h).sum(1); q = np.cross(s, e1); vv = f * (q @ d); tt = f * (e2 * q).sum(1)
        hit = ok & (uu >= 0) & (vv >= 0) & (uu + vv <= 1) & (tt > 0)
        W += np.bincount(p, weights=hit * sg[t], minlength=len(P)); H += np.bincount(p, weights=hit, minlength=len(P))
    return np.rint(W).astype(int), np.rint(H).astype(int)


def measure(P, V, F, seed=1):
    """deepest point of P inside (V, F): depth (mm), points inside (winding majority / parity majority), rays unanimous (%)"""
    if not len(P): return dict(depth=0.0, inside=0, inside_parity=0, rays_agree_pct=100.0)
    R = [ray_crossings(P, V, F, d) for d in np.random.default_rng(seed).normal(size=(3, 3))]
    Wd = np.stack([r[0] for r in R]); win = np.median(Wd, 0) >= 1; par = np.stack([r[1] % 2 for r in R]).sum(0) >= 2
    ub = cKDTree(V).query(P)[0]; ins = np.where(win)[0]; ins = ins[np.argsort(-ub[ins])]; best = 0.0
    for i0 in range(0, len(ins), 32):
        if ub[ins[i0]] <= best: break
        best = max(best, float(brute_dist(P[ins[i0:i0 + 32]], V, F).max()))
    return dict(depth=round(best, 2), inside=int(win.sum()), inside_parity=int(par.sum()), rays_agree_pct=round(100 * float((Wd == Wd[0]).all(0).mean()), 2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("--top", type=int, default=8); a = ap.parse_args()
    dd = design_dir(a.design); import scene_export as SE, body_pose as BP
    parts = {f"{g}|{n}": (g, V, F) for g, n, V, F in load_parts(dd)}; C = {c["name"]: c["frames"] for c in json.load(open(os.path.join(dd, "clips.json")))["clips"]}
    fit = json.load(open(os.path.join(PIPE, "full-exo", "arm_fit.json"))); CB, UB = np.array(fit["C_b"]), np.array(fit["u_b"])
    out = dict(method=__doc__.split("\n    python3")[0], r2=[], r6=[])
    bc = json.load(open(os.path.join(dd, "judge", "body_contact.json")))
    for k, v in sorted(bc["parts"].items(), key=lambda kv: -kv[1]["max_depth"])[:a.top]:
        if not v["worst"]: continue
        clip, fi = v["worst"][:2]; X, pose = SE.frame_xforms(C[clip][fi]); g, V0, _ = parts[k]; R, t = (np.asarray(x) for x in X[g])
        P = V0 @ R.T + t; Vb = BP.posed(pose); near = cKDTree(Vb).query(P, distance_upper_bound=25.0)[0] < 25.0
        r = dict(entry=k, frame=[clip, fi], judge=v["max_depth"], **measure(P[near], Vb, BP.F))
        if "BOTTOM" in k:
            s = (V0[near] - CB) @ UB; r["bar_s_lt_265"] = measure(P[near][s < S_CUT], Vb, BP.F)["depth"]; r["neck_arm_end"] = measure(P[near][s >= S_CUT], Vb, BP.F)["depth"]
        out["r2"].append(r); print(f"R2 {k[:60]:60s} {clip} {fi}: judge {v['max_depth']:6.2f}  check {r['depth']:6.2f} mm"
                                    + (f"  (bar {r['bar_s_lt_265']:.2f}, neck / arm end {r['neck_arm_end']:.2f})" if "BOTTOM" in k else ""), flush=True)
    pc = json.load(open(os.path.join(dd, "judge", "part_contact.json")))
    for k, v in sorted(pc["violations"].items(), key=lambda kv: -kv[1]["max_depth"])[:a.top]:
        clip, fi = v["worst"]; X, _ = SE.frame_xforms(C[clip][fi]); ka, kb = [s.strip() for s in k.split("  IN  ")]
        (ga, Va, _), (gb, Vb, Fb) = parts[ka], parts[kb]; Ra, ta = (np.asarray(x) for x in X[ga]); Rb, tb = (np.asarray(x) for x in X[gb])
        P = ((Va[::2] @ Ra.T + ta) - tb) @ Rb; m = np.all((P >= Vb.min(0) - 1) & (P <= Vb.max(0) + 1), 1)
        r = dict(entry=k, frame=[clip, fi], judge=v["max_depth"], **measure(P[m], Vb, Fb)); out["r6"].append(r)
        print(f"R6 {k[:100]:100s} {clip} {fi}: judge {v['max_depth']:6.2f}  check {r['depth']:6.2f} mm", flush=True)
    E = [abs(r["judge"] - r["depth"]) for r in out["r2"] + out["r6"]]; out["max_abs_diff_mm"] = round(max(E, default=0.0), 2)
    json.dump(out, open(os.path.join(dd, "judge", "xcheck_contact.json"), "w"), indent=1)
    print(f"xcheck: {len(E)} entries, max |judge - check| {out['max_abs_diff_mm']} mm")
