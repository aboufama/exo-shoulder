"""Adapter: tools/alignment_paired.py dump with a parameter override, saved under its own label, so that a design can be
compared pose by pose with a sibling that differs only in a few parameters (its own control, e.g. a feature switched off).

New audit instrument (2026-10-17). The model runs UNCHANGED through its own frozen() / frozen_held(); only its
pin-knee-style audit(M, B) is wrapped (exactly as tools/alignment_paired.py dump does). The output is named
<label>_<wear>_perpose.json in docs/alignment/remeasure/, so `tools/alignment_paired.py compare <id> <label>` reads it.
Pick a label that does NOT start with "<id>_" (e.g. "<id>-D0control"): the contact-depth check globs "<id>_*perpose*".

    CB_EXACT=1 OMP_NUM_THREADS=1 nice python3 tools/alignment_paired_params.py <id> bench|held <label> '<json params>'
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_audit as AA                                  # noqa: E402
import alignment_paired as AP                                 # noqa: E402


def dump(rid, wear, label, over):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json")))
    P = dict(row.get("best_params") or {}); P.update(over)
    mod = AA._load("app_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    pk = getattr(mod, "PK", None) or getattr(getattr(mod, "SC", None), "PK", None)
    if pk is None or not hasattr(pk, "audit"): raise SystemExit(f"{rid}: model has no pin-knee-style audit to wrap")
    orig = pk.audit; box = {}

    def wrapped(M, B):
        a = orig(M, B); box["poses"] = AP._dump_bench(M, B); box["report"] = B.report(); return a
    pk.audit = wrapped; t = time.time()
    try:
        r = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    finally:
        pk.audit = orig
    res = dict(id=label, of=rid, override=over, wear=wear, params=P, frozen=r.get("frozen"), report=box.get("report"),
               poses=box.get("poses"), recomputed=AP.gap_parts(box.get("poses") or []), secs=round(time.time() - t, 1),
               exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"))
    path = os.path.join(AA.REM, f"{label}_{wear}_perpose.json"); os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(res, open(path, "w"), default=float)
    print(json.dumps(dict(id=label, of=rid, wear=wear, frozen=res["frozen"], recomputed=res["recomputed"], secs=res["secs"], out=path)))
    return res


if __name__ == "__main__":
    if len(sys.argv) < 5: print(__doc__); sys.exit(0)
    dump(sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4]))
