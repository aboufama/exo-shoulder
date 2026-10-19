"""crown-ring-3r adapter for tools/alignment_kitbuild_rewear.py (read-only on every claim; new file, the shared tool and the
model are unchanged). Two things differ from the plain kit builds that tool was written for:
  * the J1 seat is given as bvec(az1, el1) in the scapula frame (not sdir(j1lat, j1lon)), so seat() reads az1 / el1 and
    applies the same ruling-4 test (az -110..135, el -20..90, anterior <= 0.20);
  * the model's bench_eval() runs two passes when J1 is a ring (link 1's root placed at the ring's FITTED level h1). The
    row's best_params (sweep k154) store h1 = 60 (the seed) and no h1_used, so by default this adapter wears h1 = the
    row's ring1_F (113.0, the second pass: reproduces the claim 82.37 to the digit); `--h1 F` wears h1 = F instead
    (`--h1 60` = the row's params as recorded, one pass: 81.39, link 1's root then starts ~20 mm outside the ring) into a
    sub-folder, never over the claim's files.

    [CB_EXACT=1] OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_kitbuild_rewear_crownring.py fit60|bench|held [--h1 F]
        -> docs/alignment/remeasure/[crown-ring-3r_h1F/]crown-ring-3r_<wear>.json (+ _perpose.json), the shared tool's format
"""
import json, os, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_kitbuild_rewear as KR                           # noqa: E402

RID = "crown-ring-3r"


def seat(K, p):
    az, el = float(p["az1"]), float(p["el1"]); u = K.bvec(az, el)
    return dict(bvec=[az, el], az=round(az, 2), el=round(el, 2), anterior=round(float(u[0]), 4), up=round(float(u[1]), 4),
                lateral=round(float(u[2]), 4), az_ok=bool(-110.0 <= az <= 135.0), el_ok=bool(-20.0 <= el <= 90.0),
                ant_ok=bool(float(u[0]) <= 0.20), seat_ok=bool(-110.0 <= az <= 135.0 and -20.0 <= el <= 90.0 and float(u[0]) <= 0.20))


if __name__ == "__main__":
    a = sys.argv[1:]; wear = a[0]; alt = "--h1" in a
    row = json.load(open(os.path.join(KR.AA.ROWS, RID + ".json")))
    h1 = float(a[a.index("--h1") + 1]) if alt else float(row["ring1_F"])
    KR.seat = seat
    if True:                                                     # the row read with h1 replaced; every other param as recorded
        orig_load = KR.json.load
        def load(f, *k, **kw):
            d = orig_load(f, *k, **kw)
            if isinstance(d, dict) and d.get("id") == RID and "best_params" in d:
                d = dict(d); d["best_params"] = dict(d["best_params"], h1=h1)
            return d
        KR.json.load = load
        if alt: KR.AA.REM = os.path.join(KR.AA.REM, f"{RID}_h1{h1:g}")   # a sub-folder: never over the claim's wear
    KR.run(RID, wear)
