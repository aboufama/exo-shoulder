#!/usr/bin/env python3
"""THREE-HUB BAND SCAN ("grading the pattern"): over plain spherical 3R layouts (J1 line x J3 line x arcs a1, a2 x
branch), with each hub free to sit at EITHER END of its axis line, the share of bench poses in which every hub can stay
in ONE 12 mm band (a q = 1 underside sits at the max need over poses: band = share of poses whose need >= max - 12;
`b97` drops the 3 % worst poses first), plus the closure share (margin 10 deg = outside the fold band).

  hub need (per pose) = the K4 rule: the height along the axis at which an O20 disc (centre + 4 rim points at 10 mm)
  clears the skin by 2 mm with a 15 mm free window (concept_kit.requirement, march mode, Bench(60,160) fast grid)

J1 lines and J3 directions are scanned on coarse grids; hub 2's need is marched per layout along +-p2 (centre ray only:
the scan ranks layouts, the kit model then measures them with the full disc).

    OMP_NUM_THREADS=1 python3 tools/hub_band_scan.py --slice i/n --out out.json [--h1min 0.85 --h3min 0.6]
"""
import argparse, json, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                                      # noqa: E402


def need_axis(B, F_map, U):
    """U (k, 3) local axis dirs -> need (k, P) of an O20 disc on that axis (centre + 4 rim points)"""
    P = len(B.idx); A = F_map(U)                                             # (P, k, 3)
    A = A.reshape(P, -1, 3); k = A.shape[1]
    e1 = np.cross(A, [0.0, 0.0, 1.0]); n = np.linalg.norm(e1, axis=-1, keepdims=True)
    e1 = np.where(n > 1e-6, e1 / np.maximum(n, 1e-9), np.array([1.0, 0, 0])); e2 = np.cross(A, e1)
    O = np.stack([np.zeros_like(A), 10 * e1, -10 * e1, 10 * e2, -10 * e2], 2)  # (P, k, 5, 3)
    D = np.broadcast_to(A[:, :, None, :], O.shape)
    I = np.broadcast_to(np.arange(P)[:, None, None], O.shape[:3])
    R = K.requirement(B, I.reshape(-1), D.reshape(-1, 3), O=O.reshape(-1, 3)).reshape(P, k, 5).max(2)
    return R.T                                                               # (k, P)


def band(N, sel, drop=0.0):
    """N (..., P) need; share of ALL poses that are in sel and within 12 mm below the (q = 1 - drop) max of sel"""
    Ns = np.where(sel, np.where(np.isfinite(N), N, 400.0), -np.inf)
    if drop > 0:
        v = np.where(sel, np.where(np.isfinite(N), N, 400.0), np.nan); top = np.nanquantile(v, 1 - drop, axis=-1)
    else:
        top = Ns.max(-1)
    ib = ((Ns >= top[..., None] - 12.0) & (Ns <= top[..., None]) & sel).sum(-1) / N.shape[-1]
    return np.where(np.asarray(top) >= 220.0, 0.0, ib), top                  # a hub that must clear an inf pose sits at 400 mm


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--slice", default="0/1"); ap.add_argument("--out", required=True)
    ap.add_argument("--h1min", type=float, default=0.85); ap.add_argument("--h3min", type=float, default=0.6)
    a = ap.parse_args(); si, sn = map(int, a.slice.split("/")); t0 = time.time()
    B = K.bench(60, 160); F = K.frames(B); P = len(B.idx); ALL = np.ones(P, bool)
    L1 = [(az, el) for az in range(-180, 180, 10) for el in range(0, 89, 8)]
    U1 = np.array([K.bvec(az, el) for az, el in L1]); E1 = np.concatenate([U1, -U1])
    N1 = need_axis(B, F.S, E1)                                               # (2 n1, P)
    b1, _ = band(N1, ALL); n1 = len(L1)
    L3 = [(wd, wa) for wd in range(10, 171, 10) for wa in range(-180, 180, 15)]
    U3 = np.array([K.wdir(wd, wa) for wd, wa in L3]); N3 = need_axis(B, F.HG, U3); b3, _ = band(N3, ALL)
    print(f"hub maps {time.time() - t0:.0f}s; J1 ends >= {a.h1min}: {(b1 >= a.h1min).sum()} / {2 * n1}; J3 dirs >= {a.h3min}: {(b3 >= a.h3min).sum()} / {len(L3)}", flush=True)
    j1 = [k for k in range(2 * n1) if b1[k] >= a.h1min][si::sn]; j3 = [k for k in range(len(L3)) if b3[k] >= a.h3min]
    rows = []
    arcs = [(x, y) for x in range(40, 111, 10) for y in range(40, 111, 10)]
    for k1 in j1:
        e1 = 1 if k1 < n1 else -1; u1 = E1[k1]; p1 = F.S(e1 * u1)               # kinematic axis = the line (sign-free)
        for k3 in j3:
            p3 = F.HG(U3[k3])
            for a1, a2 in arcs:
                for sg in (1, -1):
                    p2, ok, _ = K.closure(p1, p3, a1, a2, sg, margin_deg=10.0)
                    cl = ok.mean()
                    if cl < 0.6: continue
                    Pi = np.nonzero(ok)[0]; best = None
                    for e2 in (1, -1):
                        R = np.full(P, np.inf); R[Pi] = K.requirement(B, Pi, e2 * p2[Pi])
                        b2, top2 = band(R[None], ok[None]); b2q, _ = band(R[None], ok[None], 0.03)
                        if best is None or b2[0] > best[0]: best = (float(b2[0]), float(b2q[0]), e2, float(top2[0]))
                    h1 = float(band(N1[k1][None], ok[None])[0][0]); h3 = float(band(N3[k3][None], ok[None])[0][0])
                    rows.append(dict(az=L1[k1 % n1][0], el=L1[k1 % n1][1], e1=e1, wd=L3[k3][0], wa=L3[k3][1], a1=a1, a2=a2, sigma=sg,
                                     closure=round(float(cl), 3), hub1=round(h1, 3), hub2=round(best[0], 3), hub2_q97=round(best[1], 3),
                                     e2=best[2], hub2_F=round(best[3], 1), hub3=round(h3, 3),
                                     score=round(min(float(cl), h1, best[0], h3), 3)))
        print(f"J1 {k1} done {time.time() - t0:.0f}s rows {len(rows)}", flush=True)
    rows.sort(key=lambda r: -r["score"])
    json.dump(dict(slice=a.slice, n=len(rows), top=rows[:400], secs=round(time.time() - t0)), open(a.out, "w"))
    print("done", len(rows), round(time.time() - t0), "s"); [print(r) for r in rows[:5]]


if __name__ == "__main__":
    main()
