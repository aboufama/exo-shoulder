"""Adapter (new file, alignment audit 2026-10-17): let tools/alignment_audit.py remeasure and tools/alignment_paired.py dump
wear docs/concepts/models/skin-normal-3r-pin-knee.py, whose audit(M, B) and frozen(P) live in the model module itself (no PK
attribute). The model runs UNCHANGED: the loaded module only gets PK = itself, so the tools wrap its own audit(), which
its own frozen() calls. Bench wear only (the model has no frozen_held()).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_pinknee_adapter.py remeasure|dump skin-normal-3r-pin-knee bench
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_pinknee_adapter.py probe skin-normal-3r-pin-knee bench <out.json>
        (tools/alignment_wear_probe_model.py run(), same PK = module patch on its loader)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_audit as AA                                   # noqa: E402

_orig = AA._load


def _load(name, path):
    m = _orig(name, path)
    if not hasattr(m, "PK") and not hasattr(m, "SC") and hasattr(m, "audit") and hasattr(m, "frozen"): m.PK = m
    return m


AA._load = _load

if __name__ == "__main__":
    cmd, rid, wear = sys.argv[1], sys.argv[2], sys.argv[3]
    if cmd == "remeasure":
        AA.remeasure(rid, wear)
    elif cmd == "probe":
        import json, time
        import alignment_wear_probe as W, alignment_wear_probe_model as WPM
        _wl = W._load
        W._load = lambda name, path: (lambda m: (setattr(m, "PK", m) if not hasattr(m, "PK") and not hasattr(m, "SC") else None, m)[1])(_wl(name, path))
        t = time.time(); r = WPM.run(rid, wear); r["secs"] = round(time.time() - t, 1); r["exact"] = os.environ.get("CB_EXACT") == "1"
        json.dump(r, open(sys.argv[4], "w"), indent=1, default=float); print(json.dumps({k: v for k, v in r.items() if k != "probe"}, default=float))
    else:
        import alignment_paired as AP
        AP.dump(rid, wear)
