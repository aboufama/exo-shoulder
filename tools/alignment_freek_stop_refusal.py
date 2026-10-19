"""Auditor tool (new file, 2026-10-18): the stop-refusal side reading (audit proposal B) of freek-oracle-route-knuckle-4r,
for the verified config (VER, q3max 86) and the final-polish pick1 (the row's polished_params_priced), on the auditor's
own code path - without a full exact wear.

For one (config, wear): the model's own params (KR.PARAMS + the k33 priced file; pick1 = the row's recorded priced values
laid over them), fit on Bench(60,160) fast and frozen onto the wear bench by the model's own RM.freeze (nothing re-fitted
later); the model's own J3 dowel (ODesign.j3stop, the model's q3) lists the poses it refuses (no K crossing up to stop B);
only those poses are worn EXACT by the same frozen shape with the dowel removed (q3max dropped). The static per-pose
dump already on file for that (config, wear) supplies every other pose; each refused pose that is a contact without
the dowel is scored as that contact (ev true, contact true), and the gap is recomputed with tools/alignment_paired.gap_parts.
Dumps used: VER bench / held = docs/alignment/remeasure/freek-oracle-route-knuckle-4r_{bench,held}_static_perpose.json
(the 07:19 audit re-wear, = the verifier's dumps pose for pose); pick1 bench / held = the polish verifier's
docs/concepts/verify/freek-oracle-route-knuckle-4r/polish_verify/pick1_fit60_{bench,held}_perpose.json.
It never edits the model, a bench, a judge or a row.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_freek_stop_refusal.py VER|pick1 bench|held
        -> docs/alignment/remeasure/freek_polish_pick1/stoprefusal_<config>_<wear>.json
"""
import copy, json, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA  # noqa: E402
import alignment_paired as AP  # noqa: E402

RID = "freek-oracle-route-knuckle-4r"
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", RID + ".json")))
OUTD = os.path.join(AA.REM, "freek_polish_pick1")
DUMPS = {("VER", "bench"): os.path.join(AA.REM, f"{RID}_bench_static_perpose.json"),
         ("VER", "held"): os.path.join(AA.REM, f"{RID}_held_static_perpose.json"),
         ("pick1", "bench"): os.path.join(REPO, "docs/concepts/verify", RID, "polish_verify/pick1_fit60_bench_perpose.json"),
         ("pick1", "held"): os.path.join(REPO, "docs/concepts/verify", RID, "polish_verify/pick1_fit60_held_perpose.json")}


def main(cfg, wear):
    t0 = time.time()
    mod = AA._load("aa_freek_sr", os.path.join(AA.MODELS, RID + ".py")); RM, CB, KR = mod.RM, mod.CB, mod.KR
    P = mod.params({"q3max": 86.0}); P.pop("_seed", None)
    if cfg == "pick1": P.update(ROW["polished_params_priced"])
    mod.ODesign.SLOT55 = False; mod.ODesign.TAB = None            # the model's `law` mode (cell B, the real J2 slot)
    fitB = RM.PV.fast_bench(60, 160); B = RM.PV.held_bench() if wear == "held" else CB.Bench(n_clip=110, n_ws=360)
    Mk, fitr, M1, _ = RM.freeze(fitB, B, dict(P), mod.KModel)
    D = Mk.D; Q = Mk.Q
    q, ok, X1, X2, X3, s = KR.KRDesign._ik_phys(D, Q)
    js = D.j3stop(Q, q, ok); refused = sorted(i for i, v in js.items() if v is None)
    dmp = json.load(open(DUMPS[(cfg, wear)])); poses = dmp["poses"]; assert len(poses) == len(B.idx)
    base = AP.gap_parts(poses); rows = []
    if refused:
        W2 = copy.copy(B); W2.idx = np.asarray(B.idx)[refused]; W2.kind = [B.kind[i] for i in refused]; W2.clip = [B.clip[i] for i in refused]
        W2.poses = [B.poses[i] for i in refused]; W2.res = [None] * len(refused); W2._skin = {}; W2._ex = {}; W2._frames = {}
        if getattr(B, "grid", None) is not None:
            W2.grid = B.grid[refused]; W2._V = B._V[refused] if getattr(B, "_V", None) is not None else None
        P2 = dict(Mk.p); P2.pop("q3max", None); Mkit = type(Mk)(W2, P2); Mkit.run()
        for k, i in enumerate(refused):
            r = W2.res[k]; m = None if r is None or not len(r) else float(min(np.min(r), Mkit.cmin.get(k, 1e9)))
            rows.append(dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                             dump_ev=poses[i]["ev"], dump_taken=poses[i]["taken"], kit_min_mm=None if m is None else round(m, 2)))
    side = [dict(p) for p in poses]; kc = []
    for r in rows:
        if r["kit_min_mm"] is not None and r["kit_min_mm"] < 0 and not side[r["i"]]["taken"]:
            side[r["i"]].update(ev=True, contact=True, taken=False, min_mm=r["kit_min_mm"]); kc.append(r)
    out = dict(id=RID, config=cfg, wear=wear, tool="tools/alignment_freek_stop_refusal.py", dump=os.path.relpath(DUMPS[(cfg, wear)], REPO),
               params={k: P.get(k) for k in ROW["polished_params_priced"]}, fit_fast=fitr, plain=base, refused=len(refused),
               refused_not_in_dump_untaken=[r["i"] for r in rows if r["dump_taken"]],
               refused_kit_contacts=len(kc), refused_kit_contact_depth_mm=round(-sum(r["kit_min_mm"] for r in kc), 2),
               side=AP.gap_parts(side), side_depth_total_mm=round(-sum(p["min_mm"] for p in side if p["contact"]), 2),
               side_contact_poses=int(sum(p["contact"] for p in side)), refused_rows=rows, secs=round(time.time() - t0, 1))
    os.makedirs(OUTD, exist_ok=True)
    json.dump(out, open(os.path.join(OUTD, f"stoprefusal_{cfg}_{wear}.json"), "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k not in ("refused_rows", "fit_fast")}, default=float))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
