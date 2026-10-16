#!/usr/bin/env python3
"""FINAL POLISH ON THE ENVELOPE BENCH (tools/env_bench.py 'env') + the claim wrapper that wears a config on 'env' / held out /
Bench(110,360) through the minarc judge's harness with the judge's built-stop pricing.

Objective of a minarc parameter set p (lower is better; tools/crossfit_polish.py's minarc plug-in for the model, the claim
harness's checks and the near-touch audit; its CMA-ES driver, patched to this objective):
  P  = the plug-in's full(p) (O20, stops smhi / smlo >= 5.0 = the user's floor, discrete snapping)
  P' = priced(P): the judge's built-stop pricing (docs/concepts/verify/minarc-bdp-judge.py): the J2 slot drawn
       s +0.5 / -0 deg of J1-J3 margin -> its worst built case s + 0.5, read with the all-state rule at 5.5 (CB_FOLD_MARGIN
       5.5, as the judge's m5p5 runs), and K's stop B drawn where the 5-deg rule cuts the stretched branch (the buildability
       lens: BDp dK 34.47) -> a1max' = min(a1max, a1max at the rule cut), the cut found at margin 5 with the nominal stops
  fit P' on env (FAST), the continuity flood fill on the 1432-pose grid (crossfit_polish.flood, the verifier's law) + every
  fresh env pose joined to the connected grid by a 2-deg slerp edge to one of its 6 nearest connected grid nodes (same law:
  every sample closes, no joint step > 10 deg, knee branch constant), the claim harness's knock-outs, the near-touch gap
  (metal < 1 mm = contact) in-sample on env                                             -> obj
  + the claim-fit guard: P' fitted on Bench(60,160) FAST (the verified protocol's fit) and scored in-sample there:
    obj += max(0, g60_near - env_near - 3)
  logged, not in the objective: env plain gap; the env-fitted shape worn FROZEN on envsel (an independent fresh draw)
  -> sel_near / sel_gap, the pick-selection number (CMA selects on the noise of its fixed pool; picks are ranked on envsel)

    CB_FOLD_MARGIN=5.5 python3 tools/env_polish.py cma --x0 '{..}' --label L --out O.json [--popsize 8 --jobs 8 --budget-s 1800 ...]
    CB_FOLD_MARGIN=5.5 python3 tools/env_polish.py score OUT.json '[{"tag":..,"params":{..}}]' [--jobs 2]
    python3 tools/env_polish.py best O1.json [O2.json ..] [--by sel|obj] [--k 12]
    python3 tools/env_polish.py price '<json params>'          the priced params (stops +0.5, stop B at the rule cut)
  claim (the judge's harness docs/concepts/verify/minarc-bdp-remeasure.py, imported unchanged, benches swapped):
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 python3 tools/env_polish.py claim <fit60|env> <bench|held|env> <BDp|H1|params.json> OUT.json
      fit60: fit Bench(60,160) FAST (the verified protocol); env: fit env FAST.  Wear EXACT on Bench(110,360) / the 1154
      held-out poses / env. BDp / a params file are priced as above (the file is the nominal design); H1 runs unpriced
      through the harness's H1 path. Continuity: the harness's own flood fill (fit-consistent) + the fresh-pose edges.
      ENVP_NOPRICE=1 (with CB_FOLD_MARGIN=5): the nominal reading, stops and stop B as designed.
"""
import json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import env_bench as EB                                       # noqa: E402
EB.install()                                                 # fresh poses appended BEFORE any model loads poses
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

D2R = math.pi / 180
CLAIM_TOL = 3.0
ANG_MIN_LO = 24.9512                                         # BDp's knee window (docs/research/knee_window: 30.46 changes nothing)


# ---------------------------------------------------------------------------------------------------------------------
# pricing (the judge's built stops)
def _rotm(ax, a):
    ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * (K @ K)


def stopB_cut(KR, P):
    """dK (deg) where the 5-deg rule first refuses the stretched branch (J2 on its stop, K opening) - the buildability lens'
    equilibrium scan (th 0..180 by 0.1 deg on synthetic arm orientations), at margin 5 with the nominal stops; None = no cut
    before stop B. Returns (dK_cut, a1max_at_cut, info)."""
    S = KR.S; save = (KIT.FOLD_MARGIN, S.SING); KIT.FOLD_MARGIN = 5.0; S.SING = 5.0
    try:
        D = KR.KRDesign(dict(P))
        if not (getattr(D, "stops_ok", True) and getattr(D, "k_ok", True)): return None, None, dict(why="stops / K dyad not ok")
        Z = EB._Z0(); D.ik(Z["HG"].astype(float))           # q2sgn / q2_stops as the claim's design sets them (original archive)
        u1, u2, u3 = D.u; e = np.cross(u3, u1); e /= np.linalg.norm(e); R0 = _rotm(e, math.acos(float(np.clip(u1 @ u3, -1, 1))))
        n_ = np.cross(u1, [0.3, 0.5, 0.8]); n_ /= np.linalg.norm(n_)
        ths = np.arange(0.0, 180.0, 0.1); Qs = np.array([_rotm(n_, t * D2R) @ R0 for t in ths])
        q, ok, *_ = D.ik(Qs); dK = np.degrees(np.abs(np.asarray(D._dK))); thc = np.degrees(np.arccos(np.clip((Qs @ u3) @ u1, -1, 1)))
        fs = np.nonzero(thc > D.th_hi)[0]; bad = [j for j in fs if not ok[j]]
        b1, b2 = float(D.p["bk1"]) * D2R, float(D.p["bk2"]) * D2R; cb, sb = math.cos(b1) * math.cos(b2), math.sin(b1) * math.sin(b2)
        cpsiB = (math.cos(float(D.p["a1max"]) * D2R) - cb) / sb; dKB = math.degrees(abs(math.acos(max(-1, min(1, cpsiB))) - abs(D.psiA)))
        if not bad: return None, None, dict(why="no cut", dK_stopB=round(dKB, 3))
        j = bad[0]; dKc = float(dK[j])
        if dKc < 1e-6 or dKc >= dKB - 1e-6: return None, None, dict(why="cut at stop B / no K opening", th=round(float(thc[j]), 2), dK_stopB=round(dKB, 3))
        a1c = math.degrees(math.acos(max(-1, min(1, cb + sb * math.cos(abs(D.psiA) + dKc * D2R)))))
        return dKc, a1c, dict(th_cut=round(float(thc[j]), 2), dK_cut=round(dKc, 3), dK_stopB=round(dKB, 3), psiA=round(math.degrees(D.psiA), 3))
    finally:
        KIT.FOLD_MARGIN, S.SING = save


def priced(KR, P):
    """the judge's worst built pairing: stops s + 0.5 (read at CB_FOLD_MARGIN 5.5), stop B at the margin-5 rule cut"""
    P2 = dict(P); dKc, a1c, info = stopB_cut(KR, P)
    if a1c is not None and a1c < float(P2["a1max"]): P2["a1max"] = round(a1c, 4)
    P2["smhi"] = round(max(5.0, float(P["smhi"])) + 0.5, 4); P2["smlo"] = round(max(5.0, float(P["smlo"])) + 0.5, 4)
    info["a1max_nominal"] = float(P["a1max"]); info["a1max_priced"] = float(P2["a1max"])
    return P2, info


# ---------------------------------------------------------------------------------------------------------------------
# continuity for the fresh (off-grid) poses
def connect_extra(kin, HGx, HGg, cg, branch0=None, k=6, step=2.0, jump=10.0):
    """bool per extra pose: a closed node joined by a slerp edge (<= step deg samples, every sample closes, no joint step >
    jump, knee branch constant and in branch0) to one of its k nearest CONNECTED grid nodes. kin(Q) -> (ok, qq, sgn, ...)"""
    from scipy.spatial.transform import Rotation as Rot, Slerp
    HGx = np.asarray(HGx, float); out = np.zeros(len(HGx), bool)
    if not len(HGx) or not cg.any(): return out
    r = kin(HGx); okx = r[0]
    ang = EB._geo(HGx, HGg); ang[:, ~cg] = np.inf; nn = np.argsort(ang, 1)[:, :k]
    E = [(e, g) for e in np.nonzero(okx)[0] for g in nn[e] if np.isfinite(ang[e, g])]
    if not E: return out
    Qs, lens = [], []
    for e, g in E:
        n = max(2, int(math.ceil(ang[e, g] / step)) + 1)
        Qs.append(Slerp([0, 1], Rot.from_matrix(np.stack([HGx[e], HGg[g]])))(np.linspace(0, 1, n)).as_matrix()); lens.append(n)
    Q = np.concatenate(Qs); lens = np.array(lens); st0 = np.r_[0, np.cumsum(lens)[:-1]]
    r = kin(Q); o, q, sg = r[0], r[1], r[2]
    allok = np.logical_and.reduceat(o, st0)
    dq = np.abs((np.diff(q, axis=0) + 180) % 360 - 180).max(1); dq = np.r_[dq, 0.0]; dq[np.cumsum(lens) - 1] = 0.0
    jmp = np.maximum.reduceat(dq, st0) <= jump
    sgc = np.maximum.reduceat(sg, st0) == np.minimum.reduceat(sg, st0)
    if branch0 is not None: sgc &= np.isin(sg[st0], list(branch0))
    good = allok & jmp & sgc
    for (e, g), gd in zip(E, good):
        if gd: out[e] = True
    return out


def env_keys(B):
    """(indices, (plane, elev, axial) keys) of the fresh workspace poses of a bench"""
    Z = CB._poses_all(); n0 = EB._ZX["n0"]
    ii = [i for i in range(len(B.idx)) if B.kind[i] == "ws" and int(B.idx[i]) >= n0]
    return ii, [(float(B.poses[i]["plane"]), float(B.poses[i]["elev"]), float(B.poses[i]["axial"])) for i in ii]


# ---------------------------------------------------------------------------------------------------------------------
# the objective (crossfit_polish's minarc plug-in + its CMA driver)
_W = {}


def _X():
    import crossfit_polish as X
    return X


class EnvMinarc:
    pass


def _plugin():
    X = _X()

    class P(X.MinarcPlugin):
        name = "minarc_env"

        def __init__(self):
            super().__init__(); f = dict(self.FREE); s, lo, hi, d = f["ang_min"]; f["ang_min"] = (s, ANG_MIN_LO, hi, d + f" (>= BDp's {ANG_MIN_LO})")
            self.FREE = f

        def full(self, p):
            P_ = super().full(p); P_["ang_min"] = max(ANG_MIN_LO, float(P_["ang_min"])); return P_
    return P


def conn_sets(pl, M1, benches):
    """grid flood (crossfit_polish.flood, the verifier's law) + the fresh poses of each bench joined by edges -> key set"""
    X = _X(); kin = pl.kin(M1)
    ck, nodes, ncn = X.flood(kin); G = X._ws_grid()
    cg = np.array([(float(x[0]), float(x[1]), float(x[2])) in ck for x in G["POSE"]])
    keys = set(ck); extra = {}
    for B in benches:
        ii, kk = env_keys(B)
        if not ii: continue
        HGx = CB._poses_all()["HG"][np.asarray(B.idx)[ii]].astype(float)
        c = connect_extra(kin, HGx, G["HG"], cg)
        keys |= {k for k, v in zip(kk, c) if v}; extra[B.key] = dict(fresh=len(ii), connected=int(c.sum()))
    return keys, dict(grid_nodes=nodes, grid_connected=ncn, fresh=extra)


def env_obj(pl, Bs, p):
    X = _X(); P = pl.full(p); Pp, pinfo = priced(pl.KR, P); out = dict(price=pinfo)
    Benv, Bsel, B60 = Bs; t0 = time.time()
    M1, r1 = pl.fit(Benv, Pp)
    if r1 is None: out.update(obj=400.0, nothing_closes=True); return out
    keys, cinfo = conn_sets(pl, M1, [Benv, Bsel]); out["conn"] = cinfo
    ins = X.score_on(pl, M1, Benv, keys); out["env"] = ins
    Mf = pl.frozen(M1, Bsel); Mf.run(); sel = X.score_on(pl, Mf, Bsel, keys); out["sel"] = sel
    M6, r6 = pl.fit(B60, Pp); g60 = 400.0 if r6 is None else X.score_on(pl, M6, B60, None)["gap_near1"]
    out["g60_near"] = g60; out["claim_pen"] = round(max(0.0, g60 - ins["gap_near1"] - CLAIM_TOL), 3)
    out["obj"] = round(ins["gap_near1"] + out["claim_pen"], 3); out["sel_near"] = sel["gap_near1"]; out["sel_gap"] = sel["gap"]
    out["env_gap"] = ins["gap"]; out["secs"] = round(time.time() - t0, 1)
    return out


def _benches():
    return (EB.bench("env"), EB.bench("envsel"), CB.Bench(60, 160))


def _init(plname=None):
    os.environ.setdefault("OMP_NUM_THREADS", "1"); _W["pl"] = _plugin()(); _W["B"] = _benches()
    if any(B.mode != "fast" for B in _W["B"]) and os.environ.get("ENVP_ALLOW_EXACT") != "1":
        raise RuntimeError("env / envsel / Bench(60,160) not on the fast grid (link: eval \"$(python3 tools/env_bench.py use env)\")")


def _eval(arg):
    import traceback
    tag, p = arg; t0 = time.time()
    try:
        r = env_obj(_W["pl"], _W["B"], p)
        return dict(tag=tag, params=p, obj=r["obj"], xfit=r, secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-1500:], secs=round(time.time() - t0, 1))


def run_cma(argv):
    import argparse
    X = _X(); X.PLUGINS["minarc_env"] = _plugin(); X._init = _init; X._eval = _eval
    assert KIT.FOLD_MARGIN == 5.5, "run the polish at CB_FOLD_MARGIN=5.5 (the judge's priced reading)"
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--plugin", default="minarc_env")
    ap.add_argument("--x0", default="{}"); ap.add_argument("--fixed", default="")
    ap.add_argument("--label", required=True); ap.add_argument("--out", required=True); ap.add_argument("--state", default="")
    ap.add_argument("--state-out", default=""); ap.add_argument("--sigma", type=float, default=0.4)
    ap.add_argument("--popsize", type=int, default=8); ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--budget-s", type=float, default=1800); ap.add_argument("--max-gen", type=int, default=400)
    ap.add_argument("--max-evals", type=int, default=700); ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    X.cma(a)


def score(outp, items, jobs):
    import multiprocessing as mp
    assert KIT.FOLD_MARGIN == 5.5
    pool = mp.get_context("fork").Pool(jobs, initializer=_init); t = time.time()
    res = pool.map(_eval, [(it.get("tag", f"s{i}"), it["params"]) for i, it in enumerate(items)]); pool.close()
    json.dump(res, open(outp, "w"), indent=1, default=float)
    for r in res:
        x = r.get("xfit") or {}
        print(r["tag"], "obj", r["obj"], "env gap", x.get("env_gap"), "sel near", x.get("sel_near"), "sel gap", x.get("sel_gap"), "g60", x.get("g60_near"),
              r.get("error", ""), r["secs"], "s", flush=True)
    print(f"scored {len(res)} in {time.time() - t:.0f}s")


def best(files, by="sel", k=12, top_obj=40):
    rows = []
    for f in files:
        for r in json.load(open(f)):
            if not r.get("error") and r.get("xfit", {}).get("sel_near") is not None: r["_file"] = os.path.basename(f); rows.append(r)
    rows.sort(key=lambda r: r["obj"]); pool = rows[:top_obj]
    if by == "sel": pool.sort(key=lambda r: (r["xfit"]["sel_near"], r["obj"]))
    for r in pool[:k]:
        x = r["xfit"]; print(r["tag"], "obj", r["obj"], "env gap", x["env_gap"], "sel near", x["sel_near"], "sel gap", x["sel_gap"], "g60", x["g60_near"],
                             "a1max'", x["price"].get("a1max_priced"))
    return pool[:k]


# ---------------------------------------------------------------------------------------------------------------------
# claim: the judge's harness (minarc-bdp-remeasure.py, unchanged) with the benches swapped and the fresh-pose continuity
def claim(fit, wb, which, outp):
    import importlib.util
    sp = importlib.util.spec_from_file_location("bdp_remeasure_env", os.path.join(REPO, "docs", "concepts", "verify", "minarc-bdp-remeasure.py"))
    R = importlib.util.module_from_spec(sp); sp.loader.exec_module(R)
    fast0, held0 = R.PV.fast_bench, R.PV.held_bench
    FIT = EB.bench("env", exact=False) if fit == "env" else fast0(60, 160)
    assert FIT.mode == "fast", f"fit bench {fit} not fast"
    WEAR = {"held": held0, "env": lambda: EB.bench("env", exact=True)}.get(wb)
    R.PV.fast_bench = lambda nc, nw: FIT                     # wear() and conn() fit on this bench
    if WEAR is not None:
        W = WEAR(); wbh = "held"
        if os.environ.get("ENVP_SMOKE"):                     # local smoke test: a few poses of the wear bench
            n = int(os.environ["ENVP_SMOKE"]); sel = [i for i, k in enumerate(W.kind) if k == "clip"][:n] + [i for i, k in enumerate(W.kind) if k == "ws"][::40][:n]
            W.idx = np.asarray(W.idx)[sel]; W.kind = [W.kind[i] for i in sel]; W.clip = [W.clip[i] for i in sel]; W.poses = [W.poses[i] for i in sel]; W.res = [None] * len(sel)
        R.PV.held_bench = lambda: W
    else: W = None; wbh = "bench"
    info = dict(fit=fit, wear=wb, fit_key=FIT.key, fit_mode=FIT.mode)
    if which != "H1":
        P = R.P_bdp() if which == "BDp" else dict(R.KR.PARAMS, **json.load(open(which)))
        if os.environ.get("ENVP_NOPRICE") == "1": Pp, pinfo = dict(P), dict(why="unpriced reading (nominal stops, stop B as designed)")
        else: Pp, pinfo = priced(R.KR, P)
        info.update(nominal=P, priced=Pp, price=pinfo)
        pf = outp.replace(".json", "_params.json"); json.dump(Pp, open(pf, "w"), indent=1); R.PFILE = pf
        conn0 = R.conn

        def conn2(o, taken_mode=False, P=None):
            out = conn0(o, taken_mode=taken_mode, P=P)
            if W is None: return out
            ii, kk = env_keys(W)
            if not ii: return out
            Z, Wg, POSE, HG = R.ws_grid(); fitB = R.PV.fast_bench(60, 160)
            M1 = R.KR.KModel(fitB, dict(P)); D = R.KR.KRDesign(dict(M1.p)); D.m = np.array(M1.D.m, float); D.m[2] = 0.0
            _ = D.ik(HG[:2]); R_tol = float(M1.p["R_tol"])
            ok, qq, sgn, st, own = R.kin_nodes(D, HG, R_tol); seeds = ok & (POSE[:, 1] == 0) & (st == 0)
            ck = {tuple(x) for x in out["connected_keys"]}; cg = np.array([(float(x[0]), float(x[1]), float(x[2])) in ck for x in POSE])
            HGx = CB._poses_all()["HG"][np.asarray(W.idx)[ii]].astype(float)
            c = connect_extra(lambda Q: R.kin_nodes(D, Q, R_tol), HGx, HG, cg, branch0=set(sgn[seeds].tolist()))
            out["connected_keys"] = out["connected_keys"] + [list(k) for k, v in zip(kk, c) if v]
            out["fresh"] = dict(poses=len(ii), connected=int(c.sum())); info["fresh_conn"] = out["fresh"]
            json.dump(out, open(o, "w"), indent=1, default=float)
            return out
        R.conn = conn2
        R.wear(wbh, "BDp", outp)
    else:
        R.wear(wbh, "H1", outp)
    d = json.load(open(outp)); d["env_claim"] = info; d["wear_bench"] = wb; d["fit_protocol"] = fit
    json.dump(d, open(outp, "w"), indent=1, default=float)
    f = d.get("final") or d.get("corrected")
    print(json.dumps(dict(claim=which if which in ("BDp", "H1") else os.path.basename(which), fit=fit, wear=wb, n=d["n_wear"], margin=d["fold_margin"],
                          gap=f["gap"], near=f.get("gap_near1"), reach=f["reach"], follow=f["follow"], ib14=f["inband14"], contact=f["contact"],
                          fresh=info.get("fresh_conn"), price=info.get("price"))), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: raise SystemExit(__doc__)
    if a[0] == "cma": run_cma(a)
    elif a[0] == "score":
        jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2
        score(a[1], json.loads(a[2]) if not os.path.exists(a[2]) else json.load(open(a[2])), jobs)
    elif a[0] == "best":
        by = a[a.index("--by") + 1] if "--by" in a else "sel"; k = int(a[a.index("--k") + 1]) if "--k" in a else 12
        best([x for x in a[1:] if x.endswith(".json")], by, k)
    elif a[0] == "price":
        X = _X(); pl = _plugin()(); P = pl.full(json.loads(a[1]) if len(a) > 1 else {}); print(json.dumps(priced(pl.KR, P), default=float))
    elif a[0] == "claim": claim(a[1], a[2], a[3], a[4])
    else: raise SystemExit(__doc__)
