"""Alignment probe adapter for minarc-stop-knuckle-4r (read-only on every claim; a NEW file, nothing else changed).

tools/alignment_audit.py remeasure cannot wear this design: it loads docs/concepts/models/minarc-stop-knuckle-4r.py
(variant A) with the row's best_params (variant B), while the verified numbers come from the kit-rule model
(docs/concepts/models/minarc-stop-knuckle-4r-kitrule.py) through the judge's harness with built-stop pricing. This adapter
wears the two verified configs exactly as their verifier did:

  * BDp   - the row's v_gap 19.54 (judge-priced: J2 stops +0.5 read at CB_FOLD_MARGIN 5.5, K stop B at the 5-deg cut);
  * pick1 - the row's polished_gap 18.40 (the ledger's claim; docs/research/minarc_final_polish/picks/pick1.json);

through docs/concepts/verify/minarc-final-polish-verify.py main('fit60', wear, cfg, out) UNCHANGED (fit Bench(60,160) fast
-> frozen -> wear Bench(110,360) exact or the 1154 held-out poses; it imports the judge harness minarc-bdp-remeasure.py
unchanged). Only the harness's near_touch(M, B, capmin) is wrapped, to capture the worn (M, B) and its hub-K cap samples at
the FINAL counted set (knocked-out poses, kinematic and contact-aware continuity drops removed). From that state it reports:
  * near-touch at 1 / 2 / 3 mm with the harness's own lowest-metal definition (bench samples, M.cmin, cap samples);
  * the gap with in-band read as 3-14 mm, and the clip metal histogram;
  * tools/alignment_wear_probe.py analyse(): unscored workspace in-band, overhead reach, per-pose floors < 1 / 2 / 3 mm,
    contact depths (with the cap samples merged into the floor);
  * K: the opening dK over taken poses (idle check) and which taken poses need K open, by elevation band.
It changes no score, no judge, no model and no row.

    CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_minarc.py <BDp|pick1> <bench|held> <out.json>
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
FPV_PATH = os.path.join(REPO, "docs", "concepts", "verify", "minarc-final-polish-verify.py")
PICK1 = os.path.join(REPO, "docs", "research", "minarc_final_polish", "picks", "pick1.json")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def gap_of(ib14, follow, reach, contact=0.0):
    return round(100 * (max(0.0, .90 - ib14) + max(0.0, .95 - follow) + max(0.0, .90 - reach)) + 100 * contact, 2)


def run(cfg, wear, outp):
    t0 = time.time()
    FPV = _load("al_minarc_fpv", FPV_PATH)
    W = _load("al_minarc_probe", os.path.join(REPO, "tools", "alignment_wear_probe.py"))
    cap = []; orig_load = FPV._load

    def load2(name, path):
        m = orig_load(name, path)
        if name == "fpv_bdp_remeasure":
            nt0 = m.near_touch

            def nt(M, B, extra_min=None):
                cap.append((M, B, dict(extra_min or {}), list(B.res)))
                return nt0(M, B, extra_min)
            m.near_touch = nt
        return m
    FPV._load = load2
    vout = outp.replace(".json", "_verifier.json")
    FPV.main("fit60", wear, "BDp" if cfg == "BDp" else (PICK1 if cfg == "pick1" else cfg), vout)
    d = json.load(open(vout))
    M, B, capmin, res_final = cap[-1]
    res_raw = list(B.res); B.res = list(res_final)
    n = len(B.idx); taken = [i for i in range(n) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    cmin = dict(getattr(M, "cmin", {}) or {})
    lows = sorted((min(float(np.min(B.res[i])), float(cmin.get(i, 1e9)), float(capmin.get(i, 1e9))), i) for i in taken)
    base = B.report()
    out = dict(design="minarc-stop-knuckle-4r", config=cfg, wear=wear, n_poses=n, n_taken=len(taken),
               final_verifier=d.get("final"), contact_aware_verifier=(d.get("verifier") or {}).get("contact_aware"),
               plain=base["gap"], reach=base["reach"], follow=base["follow"], inband14=base["inband14"], inband10=base.get("inband10"),
               contact=base["contact"], min_metal_mm=round(lows[0][0], 3) if lows else None)
    res0 = list(B.res)
    for thr in (1.0, 2.0, 3.0):
        for dd, i in lows:
            if dd < thr: B.res[i] = np.r_[B.res[i], -1e-3]
        out[f"gap_near{thr:g}"] = B.report()["gap"]; out[f"near{thr:g}_poses"] = int(sum(1 for dd, i in lows if dd < thr)); B.res = list(res0)
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
    for thr in (1.0, 2.0, 3.0):
        out[f"near{thr:g}_poses_by_kind"] = dict(clip=int(sum(1 for dd, i in lows if dd < thr and kind[i] == "clip")),
                                                 ws=int(sum(1 for dd, i in lows if dd < thr and kind[i] == "ws")),
                                                 overhead140=int(sum(1 for dd, i in lows if dd < thr and el[i] >= 140)))
    out["lowest5"] = [dict(mm=round(dd, 3), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                           cap=bool(capmin.get(i, 1e9) <= min(float(np.min(B.res[i])), float(cmin.get(i, 1e9))))) for dd, i in lows[:5]]
    cl = [i for i in taken if B.kind[i] == "clip"]
    dc = np.concatenate([B.res[i] for i in cl]) if cl else np.zeros(0)
    edges = [0, 1, 2, 3, 4, 6, 10, 14, 1e9]
    out["clip_metal_hist"] = {f"{a:g}-{b:g}" if b < 1e8 else f">{a:g}": round(float(((dc >= a) & (dc < b)).mean()), 4) if len(dc) else None
                              for a, b in zip(edges[:-1], edges[1:])}
    ib3 = float(((dc >= 3) & (dc <= 14)).mean()) if len(dc) else 0.0
    out["inband3_14"] = round(ib3, 4); out["gap_band3_14"] = gap_of(ib3, base["follow"], base["reach"], base["contact"])
    ov = [dd for dd, i in lows if el[i] >= 140]
    out["overhead_min_metal_p10"] = round(float(np.percentile(ov, 10)), 2) if ov else None
    # K: opening over taken poses, and which taken poses need K open, by elevation band
    dK = np.degrees(np.abs(np.asarray(getattr(M, "dK", np.zeros(n)), float))) if getattr(M, "dK", None) is not None else None
    if dK is not None and dK.shape[0] == n:
        tk = np.array(taken)
        out["K_open_deg_taken"] = dict(min=round(float(dK[tk].min()), 3), max=round(float(dK[tk].max()), 3),
                                       forced=int((dK[tk] > 1e-4).sum()), stateA=int((dK[tk] <= 1e-4).sum()))
        bands = {}
        for lo_, hi_ in ((0, 60), (60, 90), (90, 120), (120, 140), (140, 200)):
            for kd in ("clip", "ws"):
                s = [i for i in taken if lo_ <= el[i] < hi_ and kind[i] == kd]
                if s: bands[f"{kd} {lo_}-{hi_}"] = dict(taken=len(s), K_open=int(sum(1 for i in s if dK[i] > 1e-4)))
        out["K_open_by_elev"] = bands
        cls = [i for i in taken if kind[i] == "clip"]
        out["K_open_clip_frames"] = int(sum(1 for i in cls if dK[i] > 1e-4))
    # probe (cap samples merged into the floor; restored after)
    had = hasattr(M, "cmin"); old = getattr(M, "cmin", None)
    M.cmin = {i: min(float(cmin.get(i, 1e9)), float(capmin.get(i, 1e9))) for i in set(cmin) | set(capmin)}
    try:
        out["probe"] = W.analyse(M, B)
    finally:
        if had: M.cmin = old
        else: del M.cmin
    B.res = res_raw
    out["consistency"] = dict(plain_equals_verifier_final=abs(out["plain"] - (out["contact_aware_verifier"] or out["final_verifier"] or {}).get("gap", -1)) < 1e-6)
    out["secs"] = round(time.time() - t0, 1); out["exact"] = os.environ.get("CB_EXACT") == "1"; out["fold_margin_env"] = os.environ.get("CB_FOLD_MARGIN")
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k not in ("probe", "final_verifier")}, default=float), flush=True)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 4: raise SystemExit(__doc__)
    run(*sys.argv[1:])
