"""Adapter (new file, alignment audit 2026-10-17): let tools/alignment_audit.py remeasure and tools/alignment_paired.py dump
wear docs/concepts/models/skin-normal-3r-pin-knee.py, whose audit(M, B) and frozen(P) live in the model module itself (no PK
attribute). The model runs UNCHANGED: the loaded module only gets PK = itself, so the tools wrap its own audit(), which
its own frozen() calls. Bench wear only (the model has no frozen_held()).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_pinknee_adapter.py remeasure|dump skin-normal-3r-pin-knee bench
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
    else:
        import alignment_paired as AP
        AP.dump(rid, wear)
