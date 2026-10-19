"""Independent verifier (skeptic) of the minarc final-polish claim (docs/research/minarc_final_polish.md): pick1 =
envp-F7-g35-6 vs BDp, both priced like the judge (J2 stops built +0.5 read at CB_FOLD_MARGIN 5.5, K stop B at the 5-deg
rule cut).

This verifier wires the benches itself (it does NOT call tools/env_polish.py claim). It uses:
  * the judge's harness docs/concepts/verify/minarc-bdp-remeasure.py, imported unchanged (frozen hand-over by __dict__ diff,
    per-pose member-frame checks incl. the own-state J1-J3 margin, near-touch, kinematic flood fill, contact-aware flood fill);
  * tools/env_polish.priced() for the built-stop pricing, cross-checked here against the judge's own priced BDp file
    (docs/concepts/verify/minarc-bdp-judge/params_BDp_stopB34.47.json) - must agree to 1e-3;
  * tools/env_bench.py for the 'env' fit bench (fast cache on the farm volume).
Adds, per run: the CONTACT-AWARE continuity (the harness's conn(taken_mode=True): nodes = grid poses the frozen shape takes
worn exact on all 1432 grid poses) applied on top of the kinematic one; the knee window (pin-knee interior angle from the frozen
design's ik on every counted pose vs [ang_min, 180 - ang_min] and vs H1's 30.46); held-out integrity asserts (1154 poses, no
fresh env pose, none of Bench(110,360) / Bench(60,160)).

    CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 python3 docs/concepts/verify/minarc-final-polish-verify.py <env|fit60> <held|bench> <BDp|params.json> OUT.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import env_polish as EP                                      # noqa: E402  (installs the fresh poses before any model loads)
EB, CB, KIT = EP.EB, EP.CB, EP.KIT

JUDGE_PRICED = os.path.join(HERE, "minarc-bdp-judge", "params_BDp_stopB34.47.json")
H1_ANG_MIN = 30.4611


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def main(fit, wb, which, outp):
    t0 = time.time(); assert KIT.FOLD_MARGIN == 5.5, "run at CB_FOLD_MARGIN=5.5 (the judge's priced reading)"
    R = _load("fpv_bdp_remeasure", os.path.join(HERE, "minarc-bdp-remeasure.py"))
    n0 = EB._ZX["n0"]
    # ---- pricing (+ cross-check vs the judge's priced BDp)
    P = R.P_bdp() if which == "BDp" else dict(R.KR.PARAMS, **{k: v for k, v in json.load(open(which)).items() if not k.startswith("_")})
    Pp, pinfo = EP.priced(R.KR, P)
    xchk = None
    if which == "BDp":
        J = json.load(open(JUDGE_PRICED)); dif = {k: (J[k], Pp.get(k)) for k in J if isinstance(J[k], (int, float)) and abs(float(J[k]) - float(Pp.get(k, 1e9))) > 1e-3}
        xchk = dict(judge_file=os.path.relpath(JUDGE_PRICED, REPO), differs=dif)
        # the judge priced stops at +0.5 via its own m5p5 reading; its file may carry the nominal stops -> record, do not assert on smhi / smlo
    pf = outp.replace(".json", "_params.json"); json.dump(Pp, open(pf, "w"), indent=1); R.PFILE = pf
    # ---- benches
    fast0, held0 = R.PV.fast_bench, R.PV.held_bench
    FIT = EB.bench("env", exact=False) if fit == "env" else fast0(60, 160)
    assert FIT.mode == "fast", f"fit bench {fit} not fast"
    R.PV.fast_bench = lambda nc, nw: FIT
    cap = {}
    ck0 = R.checks_B

    def checks_cap(M, B, eq_scan=True):
        out = ck0(M, B, eq_scan=eq_scan); cap.setdefault("wear", (M, B, out[1], out[2])); return out
    R.checks_B = checks_cap
    held_info = None
    if wb == "held":
        W = held0(); used = set(CB._select(110, 360)[0].tolist()) | set(CB._select(60, 160)[0].tolist())
        idx = np.asarray(W.idx); held_info = dict(n=len(idx), fresh_in_held=int((idx >= n0).sum()), bench_overlap=len(set(idx.tolist()) & used))
        assert len(idx) == 1154 and held_info["fresh_in_held"] == 0 and held_info["bench_overlap"] == 0, held_info
        R.PV.held_bench = lambda: W
    R.wear(wb, "BDp", outp)                                  # kinematic continuity inside (harness's own flood fill)
    d = json.load(open(outp)); M, B, bad, rows = cap["wear"]
    if wb == "bench": assert int(np.max(np.asarray(B.idx))) < n0 and len(B.idx) == 470
    import traceback
    ca = cj = knee = marg = contact = None; err = None
    try:
        # ---- contact-aware continuity (same fit, same priced params)
        R.checks_B = ck0
        cj = R.conn(outp.replace(".json", "_conn_taken.json"), taken_mode=True, P=Pp)
        ckT = {tuple(x) for x in cj["connected_keys"]}
        ckK = {tuple(x) for x in json.load(open(outp.replace(".json", "_conn.json")))["connected_keys"]}
        res_raw = list(B.res)                                    # wear() restored the raw model results
        for i in bad: B.res[i] = None
        tk = R.taken_list(B); key = lambda i: (float(B.poses[i]["plane"]), float(B.poses[i]["elev"]), float(B.poses[i]["axial"]))
        dropK = [i for i in tk if B.kind[i] == "ws" and key(i) not in ckK]
        dropT = [i for i in tk if B.kind[i] == "ws" and key(i) not in ckT and key(i) in ckK]
        for i in dropK + dropT: B.res[i] = None
        capmin = {i: r["cap_skin"] for i, r in rows.items()}
        rc = B.report(); nt = R.near_touch(M, B, capmin)
        ca = dict(dropped_kinematic=len(dropK), dropped_contact_aware_extra=len(dropT), **{k: rc[k] for k in R.KEYS}, gap_near1=nt["gap_near1"],
                  near1_poses=nt["near1_poses"], min_mm=nt["min_mm"], score=round(100 * (1 - rc["gap"] / 275), 2))
        # ---- knee window + own-state margin on the counted poses (member frames: checks_B rows)
        cnt = R.taken_list(B)
        HG = CB._poses_all()["HG"][np.asarray(B.idx)[cnt]].astype(float)
        q, ok, X1, X2, X3, s = M.D.ik(HG); K = M.D.knee(s); ang = np.asarray(K["ang"], float); amin = float(M.p["ang_min"])
        win = np.minimum(ang - amin, 180 - amin - ang)
        knee = dict(ang_min=round(amin, 4), ang_range=[round(float(ang.min()), 3), round(float(ang.max()), 3)], window_margin_min=round(float(win.min()), 3),
                    outside_window=int((win < -1e-6).sum()), outside_H1_window=int(((ang < H1_ANG_MIN) | (ang > 180 - H1_ANG_MIN)).sum()), knee_ok_false=int((~np.asarray(K["ok"])).sum()))
        own = [rows[i]["own"] for i in cnt if i in rows]
        marg = dict(min_own=round(min(own), 3) if own else None, lt5=sum(1 for x in own if x < 5.0), lt5p5=sum(1 for x in own if x < 5.5 - 1e-6), n=len(own))
        # contact attribution of counted-out poses with metal inside the skin
        B.res = res_raw
        con = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) < 0]
        contact = dict(n=len(con), clip=sum(1 for i in con if B.kind[i] == "clip"), ws=sum(1 for i in con if B.kind[i] == "ws"),
                       by_clip={}, deepest=sorted([dict(mm=round(float(np.min(B.res[i])), 2), kind=B.kind[i], clip=B.clip[i], plane=round(B.poses[i]["plane"], 1),
                                                         elev=round(B.poses[i]["elev"], 1), axial=round(B.poses[i]["axial"], 1)) for i in con], key=lambda r: r["mm"])[:8])
        for i in con: contact["by_clip"][B.clip[i]] = contact["by_clip"].get(B.clip[i], 0) + 1
    except Exception:                                        # noqa: BLE001
        err = traceback.format_exc()[-2500:]; print(err, flush=True)
    d["verifier"] = dict(fit=fit, wear=wb, config=which if which == "BDp" else os.path.basename(which), fit_key=FIT.key, price=pinfo, price_xcheck_judge=xchk,
                         held=held_info, contact_aware=ca, contact_aware_grid=(cj or {}).get("grid"), post_error=err, knee=knee, own_margin_counted=marg, contact_raw=contact,
                         secs=round(time.time() - t0, 1))
    json.dump(d, open(outp, "w"), indent=1, default=float)
    f = d["final"]
    print(json.dumps(dict(config=d["verifier"]["config"], fit=fit, wear=wb, n=d["n_wear"], gap=f["gap"], near=f.get("gap_near1"), reach=f["reach"],
                          contact=f["contact"], ib14=f["inband14"], ib10=f["inband10"], ca=ca,
                          own=marg, knee=knee, price=pinfo, xchk=xchk, held=held_info, ex_margin=d["extra"]["th_margin_own_state"]["min"],
                          knocked=d["extra"]["knocked_out"], secs=d["verifier"]["secs"]), default=float), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) != 4: raise SystemExit(__doc__)
    main(*a)
