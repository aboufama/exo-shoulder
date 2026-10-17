"""Alignment probe (a PROPOSAL measurement, never an input to a verdict or a score): does groove-desmo-knuckle-3r's
verified number survive its own verifier's fix 1 for the binding dowel?

The verifier (docs/concepts/verify/groove-desmo-knuckle-3r.py, groove block) finds that a straight ISO 8734 O1.5 dowel
tilts up to 4.2 deg across the near-radial rise groove: 0.108 mm of run-out over 1.5 mm of engagement against a 0.02-mm
clearance, so it binds; fix 1 is a 1.61-wide groove (1.59 at the cut stroke). The verified 22.64 is worn with the
1.52-wide groove's window [7.06, 8.44]. A wider groove narrows that window from both sides (R_LO = 6 + 0.3 + w / 2,
R_HI = 10 - 0.8 - w / 2), so stop B (where the true 3-D crest meets R_HI, the verifier's --truewin rule) comes earlier.

This file patches ONLY the module constants GROOVE_W / R_LO / R_HI of the claim's model in memory (the model file, the
verifier file, the bench and the kit are unchanged on disk) and wears the verifier's --truewin protocol.

    GD_CELL=lead CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_groove_width_probe.py <width_mm> bench|held
        -> docs/alignment/remeasure/groove-desmo-knuckle-3r_groove<width>_<wear>.json
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("GD_CELL", "lead")
import alignment_audit as AA                                  # noqa: E402

RID = "groove-desmo-knuckle-3r"


def main(w, wear):
    V = AA._load("al_v_groove_width", os.path.join(AA.VERIFY, RID + ".py"))
    GD = V.GD
    old = dict(GROOVE_W=GD.GROOVE_W, R_LO=GD.R_LO, R_HI=GD.R_HI)
    GD.GROOVE_W = w; GD.R_LO = GD.BOSS2_R + GD.BOSS_GAP + w / 2; GD.R_HI = GD.CAP_R - GD.WALL_OUT - w / 2
    new = dict(GROOVE_W=GD.GROOVE_W, R_LO=round(GD.R_LO, 4), R_HI=round(GD.R_HI, 4))
    t = time.time()
    out = V.wear(dict(V.BEST), wear, False, False, True)
    res = dict(id=RID, wear=wear, proposal="groove width = the verifier's fix 1 for the binding straight dowel", constants_before=old,
               constants_after=new, frozen=out["frozen"], corrected=out["corrected"], poses_failing=out["poses_failing"], why_failing=out["why_failing"],
               why=out.get("why"), audit=out.get("audit"), roller=out.get("roller"), groove=out.get("groove"), th_margin=out.get("th_margin"),
               corrected_overhead=out.get("corrected_overhead"), sc_info=out.get("sc_info"), secs=round(time.time() - t, 1),
               exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"))
    path = os.path.join(AA.REM, f"{RID}_groove{w:g}_{wear}.json")
    json.dump(res, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: res[k] for k in ("wear", "constants_after", "frozen", "corrected", "poses_failing", "roller", "secs")}, default=float))


if __name__ == "__main__":
    main(float(sys.argv[1]), sys.argv[2])
