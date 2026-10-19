"""Adapter for tools/alignment_drive_cap_wear.py: rows whose model imports the sidecar core as a module `SC` (e.g.
sidecar-parallelogram-knuckle-3r: `SC = sidecar-longdyad-knuckle-3r.py`, so the class is mod.SC.SCModel, not
mod.SCModel). It exposes mod.SC.SCModel as mod.SCModel and runs the drive-cap wear UNCHANGED (read-only; no score,
row, judge or model file is written).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice python3 tools/alignment_drive_cap_wear_sc.py <id> bench|held <cap_deg> '<params json>' <tag>
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alignment_drive_cap_wear as DCW                        # noqa: E402

_orig_load = DCW.AA._load


def _load(name, path):
    m = _orig_load(name, path)
    if getattr(m, "SCModel", None) is None and getattr(getattr(m, "SC", None), "SCModel", None) is not None:
        m.SCModel = m.SC.SCModel
    return m


DCW.AA._load = _load

if __name__ == "__main__":
    DCW.main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "{}", sys.argv[5] if len(sys.argv) > 5 else "cap")
