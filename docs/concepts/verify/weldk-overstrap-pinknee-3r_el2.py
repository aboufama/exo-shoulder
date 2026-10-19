"""weldk-overstrap-pinknee-3r verifier, part 2: (a) the per-pose bench dump (tools/alignment_paired.py dump; the model's
frozen() returns (out, M, B), so it is wrapped to hand the dump tool its dict), and (b) a SHARP E-strap vs link-2
side-by-side test on every taken pose (the kd test V7 of weldk-overstrap-pinknee-3r.py treats each mid-surface sample as
a 1.5 mm sphere, which is pessimistic for two straps lying side by side): in member 3's frame, link 2's true edges
(outer sample row + 1 mm, extrapolated from rows +-3 / +-1) vs the E strap's footprint (|y| <= 4, x from the hub rim to
pin a, boss O12 at pin a) wherever their height ranges overlap; gap < 0.15 mm (adjacent at J3) = clash.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/weldk-overstrap-pinknee-3r_el2.py out.json
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_paired as AP  # noqa: E402

RID = "weldk-overstrap-pinknee-3r"; CAP = {}
_load0 = AP.AA._load


def _load(name, path):
    mod = _load0(name, path)
    if path.endswith(RID + ".py"):
        f0 = mod.frozen

        def frozen(P, *a, **k):
            out, M, B = f0(P, *a, **k); CAP.update(M=M, B=B); return out
        mod.frozen = frozen; CAP["mod"] = mod
    return mod


def side_by_side(M, B):
    S = CAP["mod"].S; PK = CAP["mod"].PK; fr = M.fr; D = M.D
    rows = M.geo.links[1]["rows"]; sizes = [int(k.sum()) for _, k, _ in rows]; cut = np.cumsum([0] + sizes)
    xs, rE = M._xsE, M._rE; x0, x1 = float(M.hr[2]), float(M.p["lE"]) - PK.BOSS_R
    A0 = fr["A0"] - D.c[2]; ax0, ay0 = float(A0 @ fr["eE"]), float(A0 @ fr["nE"])
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]; out = []
    for i in taken:
        x, y, h, _ = M._L2_in_m3(i)
        P = np.c_[x, y, h]; R = [P[cut[k]:cut[k + 1]] for k in range(4)]          # rows at lateral -3, -1, 1, 3
        edges = []
        for o, inn in ((0, 1), (3, 2)):
            if not len(R[o]) or not len(R[inn]): continue
            j = np.argmin(np.linalg.norm(R[o][:, None, :2] - R[inn][None, :, :2], axis=2), axis=1)
            edges.append(R[o] + 0.5 * (R[o] - R[inn][j]))
        pts = np.concatenate([np.concatenate(R)] + edges)
        # link-2 samples at the model's 2 mm pitch along its length (no densification: a crossing at angle t may read up to ~1 mm x sin t high)
        best = 1e9
        for X in [pts]:  # one pass
            px, py, ph = X[:, 0], X[:, 1], X[:, 2]
            # strap rectangle: plan distance outside |y| <= 4, x in [x0, x1]
            dx = np.maximum(np.maximum(x0 - px, px - x1), 0); dy = np.maximum(np.abs(py) - 4.0, 0); d_rect = np.hypot(dx, dy)
            d_boss = np.maximum(np.hypot(px - ax0, py - ay0) - PK.BOSS_R, 0)
            Eu = np.interp(np.clip(px, xs[0], xs[-1]), xs, rE)
            vo_r = (ph > Eu) & (ph - S.T_LINK < Eu + S.T_LINK)                     # link-2 [h-3, h] vs E [Eu, Eu+3]
            vo_b = (ph > M.zb) & (ph - S.T_LINK < M.zb + float(M.p["tp"]))
            dd = np.r_[d_rect[vo_r], d_boss[vo_b]]
            if len(dd): best = min(best, float(dd.min()))
        out.append((best, i))
    out.sort()
    lab = lambda i: dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])
    return dict(low=[dict(gap_mm=round(d, 3), **lab(i)) for d, i in out[:8]], clash=[lab(i) for d, i in out if d < 0.15],
                note="plan gap from link 2's true edge to the E footprint where heights overlap; 0 = overlapping in plan with heights overlapping")


if __name__ == "__main__":
    AP.AA._load = _load
    AP.dump(RID, "bench")
    M, B = CAP["M"], CAP["B"]; r = side_by_side(M, B)
    json.dump(r, open(sys.argv[1], "w"), indent=1, default=float); print(json.dumps(r, default=float))
