#!/usr/bin/env python3
"""Fold-frontier seeds for offset-skin-normal-3r (osn): map a frontier layout (J1 = bvec(az1, el1), J3 = wdir(wd, wa),
arcs a1 / a2; docs/research/fold/frontier.json) to the osn model's parameters.

osn parameterises the chain by SEATS: J1 / J2 on GH rays bvec(az1, el1) / bvec(az2, el2) (their axes = the rays, the
2-slide closure theorem), J3 on the arm ray w_dir(wd, wa) with its axis tilted toward the local skin normal by b3. So:
  * J1 seat ray = the frontier J1 direction (axis = ray, b1 = 0);
  * J3: the frontier fixes the AXIS direction. For b3 = 0 the seat ray is that direction. For b3 > 0 the seat ray r is
    solved (fixed point, <= 12 steps) so that nlerp(r, n_skin(r), b3) = the frontier axis: the J3 line then misses GH by
    the seat's skin-normal offset while the orientation chain is exactly the frontier's;
  * J2 home direction = the circle intersection of the arc a1 around J1 with the arc a2 around the J3 axis at the rest
    pose, branch +1 or -1 (S.circ_int); its seat ray = that direction (b2 = 0).
Each config also carries the orientation-level fold shares of the realised axes (ws / clip poses of Bench(60,160)
inside [|a1 - a2| + 10, min(a1 + a2, 360 - a1 - a2) - 10]) so a bench loss can be split into fold vs geometry.

    OMP_NUM_THREADS=1 python3 tools/osn_fold_seeds.py frontier --out configs.json [--sum-lo 85 --sum-hi 130 --top 24]
    OMP_NUM_THREADS=1 python3 tools/osn_fold_seeds.py k4216 --out configs.json
"""
import argparse, importlib.util, json, math, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
_spec = importlib.util.spec_from_file_location("osn", os.path.join(REPO, "docs", "concepts", "models", "offset-skin-normal-3r.py"))
M = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(M)
S, CB, unit = M.S, M.CB, M.unit
D2R = math.pi / 180


def inv_bvec(d):
    d = unit(d); return math.degrees(math.atan2(d[2], -d[0])), math.degrees(math.asin(float(np.clip(d[1], -1, 1))))


def inv_wdir(w):
    w = unit(w); return math.degrees(math.acos(float(np.clip(-w[1], -1, 1)))), math.degrees(math.atan2(w[0], w[2]))


def j3_seat_for_axis(d3t, b3, iters=12):
    """seat ray r (scapula frame, rest) whose tilted axis nlerp(r, n_skin(r), b3) equals d3t"""
    r = unit(d3t)
    if b3 <= 0: return r, 0.0
    for _ in range(iters):
        _, ax, _, _ = M.seat(r, b3)
        e = unit(d3t) - ax
        if np.linalg.norm(e) < 1e-4: break
        r = unit(r + e)
    _, ax, _, _ = M.seat(r, b3)
    return r, float(np.degrees(np.arccos(np.clip(ax @ unit(d3t), -1, 1))))


_POSES = {}
def shares(params):
    """orientation-level fold shares of the realised osn axes (ws, clip) at the bench margin"""
    if not _POSES:
        B = CB.Bench(n_clip=60, n_ws=160); Z = CB._poses_all(); kind = np.array(B.kind)
        _POSES.update(Q=Z["HG"][B.idx].astype(float), ws=kind == "ws", cl=kind == "clip")
    D = M.Design(params); u1, u3 = D.u[0], D.u[2]; a1, a2 = (math.degrees(a) for a in D.A)
    th = np.degrees(np.arccos(np.clip((_POSES["Q"] @ u3) @ u1, -1, 1)))
    lo, hi = abs(a1 - a2) + M.S.SING, min(a1 + a2, 360 - a1 - a2) - M.S.SING   # the model's margin = tools/concept_kit.py FOLD_MARGIN
    inb = (th >= lo) & (th <= hi)
    return dict(ws=round(float(inb[_POSES["ws"]].mean()), 4), clip=round(float(inb[_POSES["cl"]].mean()), 4),
                a=[round(a1, 1), round(a2, 1)], band=[round(lo, 1), round(hi, 1)])


def layout_params(az1, el1, wd, wa, a1, a2, b3, branch, extra=None):
    R = M.rest(); Q0 = R["Q0"]
    d1 = unit(S.bvec(az1, el1)); d3t = unit(Q0 @ S.w_dir(wd, wa))
    r3, err3 = j3_seat_for_axis(d3t, b3)
    d2 = S.circ_int(d1, a1 * D2R, d3t, a2 * D2R, branch)
    az2, el2 = inv_bvec(d2); wds, was = inv_wdir(Q0.T @ r3)
    p = dict(az1=round(az1, 4), el1=round(el1, 4), az2=round(az2, 4), el2=round(el2, 4), wd=round(wds, 4), wa=round(was, 4),
             b3=b3, b1=0.0, b2=0.0)
    p.update(extra or {})
    return p, err3


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["frontier", "k4216"]); ap.add_argument("--out", required=True)
    ap.add_argument("--sum-lo", type=int, default=85); ap.add_argument("--sum-hi", type=int, default=130); ap.add_argument("--top", type=int, default=24)
    ap.add_argument("--rank", choices=["fold", "joint"], default="fold"); ap.add_argument("--b3", default="0,0.35,0.7")
    a = ap.parse_args(); cfgs = []
    if a.mode == "frontier":
        F = json.load(open(os.path.join(REPO, "docs", "research", "fold", "frontier.json")))
        rows = [r for r in F["rows"] if a.sum_lo <= r["a1"] + r["a2"] <= a.sum_hi]
        score = lambda r: min(r["ws_share"] / 0.90, r["clip_share"] / 0.95)
        if a.rank == "joint":                                             # fold-free share AND hub-1 band share (tools/fold_rayblock.py)
            band = {(g["az"], g["el"]): g["window12"] for g in json.load(open(os.path.join(REPO, "docs", "research", "fold", "rayblock.json")))["grid"]}
            score = lambda r: min(r["ws_share"], r["clip_share"], band.get((r["az1"], r["el1"]), 0.0))
        rows.sort(key=lambda r: (-score(r), r["a1"] + r["a2"]))
        picked = []                                                      # distinct layouts (J1 and J3 each >= 10 deg apart, or other arcs)
        for r in rows:
            u1 = S.bvec(r["az1"], r["el1"]); u3 = S.w_dir(r["wd"], r["wa"])
            if any(abs(q["a1"] - r["a1"]) < 1 and abs(q["a2"] - r["a2"]) < 1 for q in picked) and \
               any(np.degrees(np.arccos(min(1, float(u1 @ S.bvec(q["az1"], q["el1"]))))) < 10 and
                   np.degrees(np.arccos(min(1, float(u3 @ S.w_dir(q["wd"], q["wa"]))))) < 10 for q in picked):
                continue
            picked.append(r)
            if len(picked) >= a.top: break
        for li, r in enumerate(picked):
            for b3 in [float(x) for x in a.b3.split(",")]:
                for br in (1.0, -1.0):
                    p, err = layout_params(r["az1"], r["el1"], r["wd"], r["wa"], r["a1"], r["a2"], b3, br)
                    sh = shares(p)
                    cfgs.append(dict(p, _meta=dict(layout=li, score=round(score(r), 4), a1=r["a1"], a2=r["a2"], J1=[r["az1"], r["el1"]], J3=[r["wd"], r["wa"]],
                                                   branch=br, j3_axis_err_deg=round(err, 2), frontier_ws=r["ws_share"],
                                                   frontier_clip=r["clip_share"], fold=sh)))
    else:                                                                 # k4216's seats, only the arcs / J1 moved toward the frontier
        row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "offset-skin-normal-3r.json")))
        bp = {k: v for k, v in row["best_params"].items() if k not in ("S_a", "S_t", "R_r")}
        D = M.Design(bp); R = M.rest(); Q0 = R["Q0"]
        d3 = Q0 @ D.u[2]; br = D.branch; a10, a20 = (math.degrees(x) for x in D.A)
        wd3, wa3 = inv_wdir(D.u[2])                                       # the realised (tilted) J3 axis in the humerus frame
        for az1 in (bp["az1"], 110.0, 120.0, 132.0):
            for el1 in (bp["el1"], 55.0, 45.0, 35.0, 28.0):
                for (a1, a2) in ((a10, a20), (45.0, 65.0), (50.0, 60.0), (50.0, 50.0), (55.0, 55.0)):
                    d1 = unit(S.bvec(az1, el1)); d2 = S.circ_int(d1, a1 * D2R, d3, a2 * D2R, br); az2, el2 = inv_bvec(d2)
                    p = dict(bp, az1=round(az1, 4), el1=round(el1, 4), az2=round(az2, 4), el2=round(el2, 4))
                    sh = shares(p)
                    cfgs.append(dict(p, _meta=dict(move=dict(az1=az1, el1=el1, a1=round(a1, 1), a2=round(a2, 1)), branch=br, fold=sh)))
    json.dump([{k: v for k, v in c.items() if k != "_meta"} for c in cfgs], open(a.out, "w"), indent=1)
    json.dump([c["_meta"] for c in cfgs], open(a.out.replace(".json", "") + ".meta.json", "w"), indent=1)
    print(f"{len(cfgs)} configs -> {a.out} (+ .meta.json)")
    for c in cfgs[:: max(1, len(cfgs) // 30)]:
        m = c["_meta"]; print({k: c[k] for k in ("az1", "el1", "az2", "el2", "wd", "wa", "b3")}, m.get("fold"), m.get("j3_axis_err_deg"), m.get("move"))


if __name__ == "__main__":
    main()
