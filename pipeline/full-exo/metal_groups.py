"""Which exo.glb groups are shoulder metal for the proximity judges (R1 / R1-aim / R4: score_design.py, r1_decompose.py).

Rule (2026-10-16, after the gen-4 verifier found score_design.py silently dropping the knuckle groups l1a / l1b and hub K):
  * every group the chain POSES (a key of the clips' per-frame G) is exo metal and is scored: base, l1..lN, split members
    (l1a, l1b, ...), cuff, S, and any member group a future builder adds - no name pattern decides it;
  * H (arm-fixed: the project's arm pad / pad mount / retainers and the user's BOTTOM etc.) rides the humerus and is
    scored within ARM_NEAR of the GH centre (the shoulder part of the arm-side metal), as before;
  * a glb group that is neither posed nor H must be listed in EXCLUDED with a reason, or the judge stops: a new group can
    never drop out of the score unnoticed.
"""

EXCLUDED = {
    "F": "forearm-fixed parts (the user's MIDDLE / FOREARM CUFF and their screws): ride the forearm segment, far outside the "
         "shoulder zone (> 110 mm from GH); the shoulder judges do not pose the forearm",
}
ARM_FIXED = "H"


def classify(glb_groups, clip_groups):
    """-> (scored list, excluded dict {group: reason}); raises ValueError naming any group the rule does not cover"""
    glb_groups, clip_groups = set(glb_groups), set(clip_groups)
    scored = sorted(g for g in glb_groups if g in clip_groups or g == ARM_FIXED)
    excluded = {g: EXCLUDED[g] for g in sorted(glb_groups) if g not in scored and g in EXCLUDED}
    unknown = sorted(glb_groups - set(scored) - set(excluded))
    if unknown:
        raise ValueError(f"metal_groups: exo.glb group(s) {unknown} are neither posed by clips.json (G) nor arm-fixed H nor listed "
                         f"in metal_groups.EXCLUDED with a reason - add them to the chain's clips or exclude them explicitly")
    clash = sorted(g for g in scored if g in EXCLUDED)
    if clash:
        raise ValueError(f"metal_groups: group(s) {clash} are posed by clips.json but listed as excluded - fix EXCLUDED")
    return scored, excluded


def clip_groups(C):
    """every group posed in any frame of a clips.json dict"""
    out = set()
    for c in C["clips"]:
        for f in c["frames"]:
            out.update(f["G"].keys())
    return out
