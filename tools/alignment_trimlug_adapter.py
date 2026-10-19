"""Adapter (new file, alignment audit 2026-10-17): wear docs/concepts/models/trimlug-k165-knuckle-3r.py (and any model of
the same shape: frozen(P, nc, nw) with nc == -1 = held out, its pin-knee audit reached as mod.SN.PK) through the three
audit instruments in ONE wear per bench, instead of three:
  * tools/alignment_audit.py remeasure  -> docs/alignment/remeasure/<id>_<wear>.json          (deep_audit: near 1/2/3 mm, ...)
  * tools/alignment_paired.py dump       -> docs/alignment/remeasure/<id>_<wear>_perpose.json  (per-pose dump, contact depth)
  * tools/alignment_wear_probe_model.py  -> docs/alignment/remeasure/<id>_probe_<wear>.json    (unscored ws in-band, overhead)
The model runs UNCHANGED: the loaded module only gets PK = its lead module's PK (the one its frozen() calls) and
frozen_held(P) = frozen(P, -1, -1); PK.audit is wrapped to capture (M, B) and the three readers run on that capture.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_trimlug_adapter.py trimlug-k165-knuckle-3r bench|held
    CB_EXACT=1 SN_CELL=lead OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_trimlug_adapter.py flood trimlug-k165-knuckle-3r
    python3 tools/alignment_trimlug_adapter.py paired trimlug-k165-knuckle-3r slipper-nose-knuckle-3r,sidecar-longdyad-knuckle-3r
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_audit as AA                                   # noqa: E402
import alignment_paired as AP                                  # noqa: E402
import alignment_wear_probe as W                               # noqa: E402
import alignment_wear_probe_model as WM                        # noqa: E402


def main(rid, wear):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json"))); P = dict(row.get("best_params") or {})
    mod = AA._load("atl_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SN", None), "PK", None)
    if pk is None or not hasattr(pk, "audit"): raise SystemExit(rid + ": no pin-knee-style audit to wrap")
    orig = pk.audit; box = {}

    def wrapped(M, B):
        a = orig(M, B)
        box["mode"] = B.mode
        box["deep"] = AA.deep_audit(M, B)                     # restores B.res itself
        box["poses"] = AP._dump_bench(M, B); box["report"] = B.report()
        box["probe"] = W.analyse(M, B); box["extras"] = WM.extras(M, B)
        return a
    pk.audit = wrapped; t = time.time()
    try:
        r = mod.frozen(P) if wear == "bench" else mod.frozen(P, -1, -1)
    finally:
        pk.audit = orig
    secs = round(time.time() - t, 1); ex = os.environ.get("CB_EXACT") == "1"; git = AA._git("rev-parse", "--short", "HEAD")
    os.makedirs(AA.REM, exist_ok=True)
    rem = dict(id=rid, wear=wear, params=P, frozen=r.get("frozen"), fit_fast=r.get("fit_fast"), why=r.get("why"), parts_ib14=r.get("parts_ib14"),
               audit=r.get("audit"), deep=box.get("deep"), mode=box.get("mode"), secs=secs, exact=ex, git=git,
               adapter="tools/alignment_trimlug_adapter.py", t5=r.get("t5"), overhead=r.get("overhead"))
    json.dump(rem, open(os.path.join(AA.REM, f"{rid}_{wear}.json"), "w"), indent=1, default=float)
    dmp = dict(id=rid, wear=wear, params=P, frozen=r.get("frozen"), report=box.get("report"), poses=box.get("poses"),
               recomputed=AP.gap_parts(box.get("poses") or []), secs=secs, exact=ex, git=git, adapter="tools/alignment_trimlug_adapter.py")
    json.dump(dmp, open(os.path.join(AA.REM, f"{rid}_{wear}_perpose.json"), "w"), default=float)
    a = r.get("audit") or {}
    prb = dict(design=rid, wear=wear, model_frozen=r.get("frozen"), fit_fast=r.get("fit_fast"),
               model_audit_near=dict(near1=a.get("gap_near1"), near2=a.get("gap_near2"), near2_poses=a.get("near2_poses"), min_mm=a.get("near_touch_min_mm")),
               probe=box.get("probe"), extras=box.get("extras"), secs=secs, exact=ex, adapter="tools/alignment_trimlug_adapter.py")
    json.dump(prb, open(os.path.join(AA.REM, f"{rid}_probe_{wear}.json"), "w"), indent=1, default=float)
    print(json.dumps(dict(id=rid, wear=wear, frozen=r.get("frozen"), recomputed=dmp["recomputed"],
                          deep={k: v for k, v in (box.get("deep") or {}).items() if k != "coord_spans"},
                          t5={k: (r.get("t5") or {}).get(k) for k in ("n", "sum_mm")}, secs=secs), default=float))


def flood(rid):
    """the continuity flood (rule 2026-10-16) of the frozen claim through the lead module's own frozen_flood() (the claim
    model patches the lead module's model class, clamp and params, so it wears the TRIMMED metal) -> <id>_flood_bench.json"""
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json"))); P = dict(row.get("best_params") or {})
    mod = AA._load("atlf_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    assert mod.SN.SNModel is mod.TLModel, "the lead module is not pointed at the claim's model class"
    t = time.time(); r = mod.SN.frozen_flood(P)
    out = dict(id=rid, wear="bench", params=P, frozen=r.get("frozen"), connected=r.get("connected"), model_class=mod.SN.SNModel.__name__,
               secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"),
               adapter="tools/alignment_trimlug_adapter.py flood")
    json.dump(out, open(os.path.join(AA.REM, f"{rid}_flood_bench.json"), "w"), indent=1, default=float)
    print(json.dumps(dict(frozen=out["frozen"], connected={k: v for k, v in (out["connected"] or {}).items() if k != "connected_full" or True}, secs=out["secs"]), default=float)[:3000])


def paired(rid, refs):
    """paired per-pose comparison (tools/alignment_paired.compare_sets, unchanged) of the claim's dumps against each
    reference's claim dumps (<ref>_<wear>_perpose_claim.json when on file, else <ref>_<wear>_perpose.json), with the
    contact depth of both -> <id>_vs_<ref>_paired_claim.json"""
    R = AA.REM

    def dfile(i, w):
        for f in (f"{i}_{w}_perpose_claim.json", f"{i}_{w}_perpose.json"):
            if os.path.exists(os.path.join(R, f)): return f
    def depth(P):
        c = [-p["min_mm"] for p in P if p["contact"]]
        return dict(n=len(c), sum_mm=round(sum(c), 2), max_mm=round(max(c), 2) if c else None, gt3=sum(1 for x in c if x > 3))
    out = {}
    for ref in refs:
        res = dict(A=rid, B=ref, note="diff = gap A - gap B (negative: A better); paired bootstrap over poses within kind (tools/alignment_paired.compare_sets)")
        pa_all, pb_all = [], []
        for wear in ("bench", "held"):
            fa, fr = f"{rid}_{wear}_perpose.json", dfile(ref, wear)
            if not fr or not os.path.exists(os.path.join(R, fa)): res[wear] = "missing dump"; continue
            da, db = json.load(open(os.path.join(R, fa))), json.load(open(os.path.join(R, fr)))
            r = AP.compare_sets(da["poses"], db["poses"], 4000)
            r["model_frozen"] = dict(A=(da.get("frozen") or {}).get("gap"), B=(db.get("frozen") or {}).get("gap"))
            r["depth"] = dict(A=depth(da["poses"]), B=depth(db["poses"])); r["files"] = [fa, fr]; res[wear] = r
            tag = lambda P, w: [dict(p, i=f"{w}:{p['i']}") for p in P]
            pa_all += tag(da["poses"], wear); pb_all += tag(db["poses"], wear)
        if isinstance(res.get("held"), dict) and isinstance(res.get("bench"), dict):
            res["pooled_bench_plus_held"] = AP.compare_sets(pa_all, pb_all, 4000)
        out[ref] = res
        json.dump(res, open(os.path.join(R, f"{rid}_vs_{ref}_paired_claim.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "flood": flood(sys.argv[2])
    elif sys.argv[1] == "paired": paired(sys.argv[2], sys.argv[3].split(","))
    else: main(sys.argv[1], sys.argv[2])
