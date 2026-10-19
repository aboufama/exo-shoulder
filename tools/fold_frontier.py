"""Fold frontier of a 3R orientation chain on the concept bench (orientation level: no geometry, no skin).

A 3R chain that reproduces the arm's rotation folds (J2 singular / branch switch) when the angle theta between the
scapula-fixed J1 axis u1 and the humerus-fixed J3 axis u3 leaves the band [|a1-a2| + m, min(a1+a2, 360-a1-a2) - m]
(a1, a2 = the link arcs J1-J2, J2-J3; m = the fold margin, 10 deg like the bench). This holds for ANY 3R chain,
offset axes included (orientation depends on the axis directions only), so it bounds reach for every 3R morphology.

For every (a1, a2) on a grid it finds the (u1, u3) pairs (u1 = K.bvec(az, el) in the scapula frame, u3 = K.wdir(wd, wa)
in the humerus frame, like the models' parameters) that keep the most bench workspace poses and clip frames in band,
and writes the top distinct pairs per (a1, a2) to docs/research/fold/frontier.json.

  python3 tools/fold_frontier.py [--margin M (default tools/concept_kit.py FOLD_MARGIN: 5 since 2026-10-16)] [--top 3]
"""
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import concept_bench as CB, concept_kit as K

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--margin", type=float, default=K.FOLD_MARGIN); ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--out", default=os.path.join(REPO, "docs", "research", "fold", "frontier.json")); a = ap.parse_args()
    t0 = time.time()
    B = CB.Bench(n_clip=60, n_ws=160); Z = CB._poses_all(); Q = Z["HG"][B.idx].astype(np.float32); kind = np.array(B.kind)
    ws, cl = kind == "ws", kind == "clip"
    H1 = [(az, el) for az in range(-180, 180, 6) for el in range(16, 91, 4)]
    H3 = [(wd, wa) for wd in range(15, 166, 5) for wa in range(-90, 91, 6)]
    u1 = np.array([K.bvec(az, el) for az, el in H1], np.float32); u3 = np.array([K.wdir(wd, wa) for wd, wa in H3], np.float32)
    W = np.einsum("pij,kj->kpi", Q, u3)                                       # J3 axis in the scapula frame, per pose
    # histogram of theta in 1 deg bins per (u1, u3) for ws and clip poses -> band shares for any (a1, a2) in O(1)
    nb = 181; Hw = np.zeros((len(H1), len(H3), nb), np.int16); Hc = np.zeros_like(Hw)
    for i in range(len(H1)):
        th = np.degrees(np.arccos(np.clip(W @ u1[i], -1, 1)))                 # (n3, P)
        b = np.clip(np.rint(th).astype(np.int32), 0, nb - 1)
        for m, H in ((ws, Hw), (cl, Hc)):
            bb = b[:, m]; r = np.repeat(np.arange(len(H3)), bb.shape[1])
            np.add.at(H[i], (r, bb.ravel()), 1)
    Cw = np.concatenate([np.zeros((len(H1), len(H3), 1), np.int32), np.cumsum(Hw, 2, dtype=np.int32)], 2)
    Cc = np.concatenate([np.zeros((len(H1), len(H3), 1), np.int32), np.cumsum(Hc, 2, dtype=np.int32)], 2)
    nw, nc = int(ws.sum()), int(cl.sum())
    out = dict(margin=a.margin, n_ws=nw, n_clip=nc, grid=dict(J1="K.bvec(az 6 deg, el 16-88 deg / 4)", J3="K.wdir(wd 15-165 / 5, wa +-90 / 6)"),
               note=__doc__.split("\n\n")[1], rows=[])
    for a1 in range(30, 96, 5):
        for a2 in range(30, 121, 5):
            lo, hi = abs(a1 - a2) + a.margin, min(a1 + a2, 360 - a1 - a2) - a.margin
            if hi <= lo: continue
            l, h = int(np.ceil(lo)), int(np.floor(hi)) + 1
            rw = (Cw[:, :, h] - Cw[:, :, l]) / nw; rc = (Cc[:, :, h] - Cc[:, :, l]) / nc
            sc = np.minimum(rw / 0.90, rc / 0.95)
            order = np.argsort(-sc, axis=None)[:4000]; picked = []
            for f in order:
                i, j = np.unravel_index(f, sc.shape)
                if any(np.degrees(np.arccos(min(1, float(u1[i] @ u1[p])))) < 15 and np.degrees(np.arccos(min(1, float(u3[j] @ u3[q])))) < 15 for p, q in picked):
                    continue
                picked.append((i, j))
                out["rows"].append(dict(a1=a1, a2=a2, band=[lo, hi], az1=H1[i][0], el1=H1[i][1], wd=H3[j][0], wa=H3[j][1],
                                        ws_share=round(float(rw[i, j]), 4), clip_share=round(float(rc[i, j]), 4)))
                if len(picked) >= a.top: break
    rows = out["rows"]
    out["best_by_sum"] = {}
    for s in sorted({r["a1"] + r["a2"] for r in rows}):
        r = max((r for r in rows if r["a1"] + r["a2"] == s and r["clip_share"] >= 0.999), key=lambda r: r["ws_share"], default=None)
        if r: out["best_by_sum"][s] = r
    os.makedirs(os.path.dirname(a.out), exist_ok=True); json.dump(out, open(a.out, "w"), indent=1)
    print(f"{len(rows)} rows in {time.time() - t0:.0f} s -> {os.path.relpath(a.out, REPO)}")
    for s, r in out["best_by_sum"].items():
        print(f"a1+a2 {s:3d} (a1 {r['a1']}, a2 {r['a2']}): ws {r['ws_share']:.3f} clip {r['clip_share']:.3f}  J1 bvec({r['az1']}, {r['el1']})  J3 wdir({r['wd']}, {r['wa']})")


if __name__ == "__main__":
    main()
