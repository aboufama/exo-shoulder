#!/usr/bin/env python3
"""Alignment re-wear adapter for lowarm-kstop-knuckle-3r (new file; the model, verifier and bench run UNCHANGED).

Why: tools/alignment_audit.py remeasure looks for mod.PK / mod.SC.PK, but this model builds its module chain fresh inside
_harness() on every frozen() call (T -> halfring verifier -> halfring model LM -> LM.SC.PK), so the audit's wrapper never
sees the PK that actually runs. This adapter wraps the model's _harness so the PK of THAT chain gets the audit's own
deep_audit() recorder (the same recorder the remeasure uses), plus alignment_paired._dump_bench for a per-pose dump.
The claim is the per-pose worst of two sided dwell wears (+0.264 / -0.210 deg of K); `merge` combines the two sides with the
claim's own combine rule (contact < not taken < taken by in-band share, then metal) and writes the remeasure file the audit
reads (docs/alignment/remeasure/<id>_<wear>.json): frozen = the per-pose worst, deep.gap_nearN read on the per-pose worst
(a taken pose whose metal incl. the model's extra walls is under N mm counted as contact), the clip histogram / band 3-14 /
coord spans from the wall-side (+0.264) wear, and each side's deep record kept under `sides`.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_remeasure_kstop.py side <bench|held> <delta> <out.json>
    python3 tools/alignment_remeasure_kstop.py merge <bench|held> <side_plus.json> <side_minus.json>
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RID = "lowarm-kstop-knuckle-3r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def side(wear, delta, outp):
    AA = _load("aa_for_kstop_rem", os.path.join(REPO, "tools", "alignment_audit.py"))
    AP = _load("ap_for_kstop_rem", os.path.join(REPO, "tools", "alignment_paired.py"))
    KM = _load("kstop_for_rem", os.path.join(REPO, "docs", "concepts", "models", RID + ".py"))
    row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", RID + ".json")))
    P = dict(row.get("best_params") or {}); box = {}
    oh = KM._harness

    def h():
        T, V, LM, DS, S, PLAY = oh()
        pk = getattr(LM, "PK", None) or getattr(getattr(LM, "SC", None), "PK", None)
        orig = pk.audit

        def wrapped(M, B):
            a = orig(M, B)
            box["deep"] = AA.deep_audit(M, B); box["poses"] = AP._dump_bench(M, B); box["report"] = B.report(); box["mode"] = B.mode
            dK = np.degrees(np.abs(np.asarray(getattr(M, "dK", []), float)))
            tk = [i for i in range(len(B.idx)) if AA._taken(B, i)]
            box["dK_taken_max"] = round(float(max([dK[i] for i in tk] or [0])), 3) if len(dK) == len(B.idx) else None
            box["dowel_would_cut"] = int(sum(1 for i in tk if len(dK) == len(B.idx) and dK[i] > KM.DOWEL_K + 1e-9))
            return a
        pk.audit = wrapped
        box["pk"] = pk.__name__ if hasattr(pk, "__name__") else str(pk)
        return T, V, LM, DS, S, PLAY
    KM._harness = h
    t = time.time()
    r = KM.frozen(P, delta) if wear == "bench" else KM.frozen_held(P, delta)
    out = dict(id=RID, wear=wear, delta=float(delta), params=P, frozen=r.get("frozen"), fit_fast=r.get("fit_fast"), why=r.get("why"),
               parts_ib14=r.get("parts_ib14"), audit=r.get("audit"), deep=box.get("deep"), mode=box.get("mode"), poses=box.get("poses"),
               recomputed=AP.gap_parts(box.get("poses") or []), dK_taken_max=box.get("dK_taken_max"), dowel_would_cut=box.get("dowel_would_cut"),
               pk=box.get("pk"), secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("wear", "delta", "frozen", "recomputed", "dK_taken_max", "dowel_would_cut", "secs")}
                     | {"deep": {k: v for k, v in (out["deep"] or {}).items() if k != "coord_spans"}}, default=float))


def merge(wear, paths):
    AP = _load("ap_for_kstop_merge", os.path.join(REPO, "tools", "alignment_paired.py"))
    D = [json.load(open(p)) for p in paths]
    eff = lambda r: None if r["min_mm"] is None else min(r["min_mm"], r["cmin"] if r["cmin"] is not None else 9e9)
    rk = lambda r: (0 if r["contact"] else (1 if not r["taken"] else 2), (r.get("nib", 0) / max(r.get("ns", 1), 1)) if r["taken"] else 0,
                    eff(r) if eff(r) is not None else 9e9)
    n = len(D[0]["poses"]); W = [dict(min([d["poses"][i] for d in D], key=rk)) for i in range(n)]
    base = AP.gap_parts(W); deep = dict(D[0]["deep"] or {})
    deep.update(plain=base["gap"], reach=base["reach"], follow=base["follow"], inband14=base["inband14"], contact=base["contact"])
    taken = [r for r in W if r["taken"]]
    deep["min_metal_mm"] = round(min(eff(r) for r in taken), 3) if taken else None
    for thr in (1.0, 2.0, 3.0):
        Q = []
        for r in W:
            q = dict(r)
            if r["taken"] and eff(r) is not None and eff(r) < thr: q["taken"] = False; q["contact"] = True
            Q.append(q)
        deep[f"gap_near{thr:g}"] = AP.gap_parts(Q)["gap"]; deep[f"near{thr:g}_poses"] = int(sum(1 for r in taken if eff(r) < thr))
    ov = [eff(r) for r in taken if (r.get("elev") or 0) >= 140]
    deep["overhead_min_metal_p10"] = round(float(np.percentile(ov, 10)), 2) if ov else None
    ws = [r for r in W if r["kind"] == "ws"]
    deep["overhead_taken"] = [int(sum(1 for r in ws if (r.get("elev") or 0) >= 150 and r["taken"])), int(sum(1 for r in ws if (r.get("elev") or 0) >= 150))]
    deep["near2_taken_poses"] = sorted([[r["i"], r["kind"], r.get("elev"), round(eff(r), 3)] for r in taken if eff(r) < 2.0], key=lambda x: x[3])
    deep["source_of_hist_band_spans"] = "wall-side (+0.264) wear: " + paths[0]
    out = dict(id=RID, wear=wear, params=D[0]["params"], frozen=dict(base, gap=base["gap"]), fit_fast=D[0].get("fit_fast"), why=D[0].get("why"),
               parts_ib14=D[0].get("parts_ib14"), audit=D[0].get("audit"), deep=deep, mode=D[0].get("mode"),
               sides={str(d["delta"]): dict(frozen=d.get("frozen"), recomputed=d.get("recomputed"), dK_taken_max=d.get("dK_taken_max"),
                                            dowel_would_cut=d.get("dowel_would_cut"), secs=d.get("secs"),
                                            deep={k: v for k, v in (d.get("deep") or {}).items() if k != "coord_spans"}) for d in D},
               secs=round(sum(d.get("secs") or 0 for d in D), 1), exact=all(d.get("exact") for d in D),
               note="per-pose worst of the sided dwell wears, re-worn by tools/alignment_remeasure_kstop.py (model unchanged; its "
                    "chain's PK.audit wrapped with alignment_audit.deep_audit)")
    p = os.path.join(REPO, "docs", "alignment", "remeasure", f"{RID}_{wear}.json")
    json.dump(out, open(p, "w"), indent=1, default=float)
    print(json.dumps(dict(path=p, frozen=out["frozen"], deep={k: v for k, v in deep.items() if k != "coord_spans"}), default=float))


if __name__ == "__main__":
    if sys.argv[1] == "side":
        side(sys.argv[2], float(sys.argv[3]), sys.argv[4])
    elif sys.argv[1] == "merge":
        merge(sys.argv[2], sys.argv[3:])
