"""Knee pin stack probe: does a pin-knee claim stand on the knee hardware the build rule requires? (alignment audit)

CLAUDE.md, lead's build rule 2026-10-17: "the knee pins are built as MR63ZZ ball-bearing pairs (with plain iglidur pins
R17 fails: ~10 deg cuff twist, ~10 N)". The pin-knee model family carries the knee stack as the parameter `stk`
(docs/concepts/models/skin-normal-3r-pin-knee.py lines 19 and 54: 5.0 = iglidur pin over two plates, 6.0 = MR63ZZ pair;
tp = (stk - RUN) / 2 per plate). Rows fitted before the rule inherit whatever `stk` their parent's search left.

This tool re-wears a row's frozen claim UNCHANGED except for `stk` (the model's own frozen() / frozen_held(), the same
call tools/alignment_audit.py remeasure makes, with the model's audit() wrapped to also record near-touch / depth) and
writes docs/alignment/remeasure/<id>_stk<value>_<wear>.json. It never edits a model, a row, a bench or a score: the
output is a measurement for the auditor's report (a proposal input, never a verdict input on its own).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_knee_stack_probe.py <id> bench|held [stk=6.0]
"""
import json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import alignment_audit as AA                                  # noqa: E402


def probe(rid, wear, stk=6.0):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json")))
    P = dict(row.get("best_params") or {})
    mod = AA._load("ks_" + re.sub(r"\W", "_", rid), os.path.join(AA.MODELS, rid + ".py"))
    base_stk = (getattr(mod, "PARAMS", {}) or {}).get("stk")
    P["stk"] = float(stk)
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SC", None), "PK", None)
    if pk is None or not hasattr(pk, "audit"): raise SystemExit(f"{rid}: no pin-knee-style audit to wrap")
    orig = pk.audit; box = {}

    def wrapped(M, B):
        a = orig(M, B); box["deep"] = AA.deep_audit(M, B); box["mode"] = B.mode; return a
    pk.audit = wrapped
    t = time.time()
    try:
        r = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    finally:
        pk.audit = orig
    out = dict(id=rid, wear=wear, stk=float(stk), stk_claim=base_stk, params=P, frozen=r.get("frozen"), fit_fast=r.get("fit_fast"),
               why=r.get("why"), parts_ib14=r.get("parts_ib14"), audit=r.get("audit"), deep=box.get("deep"), mode=box.get("mode"),
               secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"))
    tag = ("%g" % float(stk)).replace(".", "p")
    path = os.path.join(AA.REM, f"{rid}_stk{tag}_{wear}.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps(dict(id=rid, wear=wear, stk=float(stk), stk_claim=base_stk, frozen=out["frozen"], secs=out["secs"], out=os.path.relpath(path, REPO)), default=float))
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2: raise SystemExit(__doc__)
    kw = dict(x.split("=", 1) for x in a[2:] if "=" in x)
    probe(a[0], a[1], float(kw.get("stk", 6.0)))
