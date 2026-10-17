# Gen-6 fix: R7 strip glue, link 1a's climb in the L1, the drive's working end, R17 at 2x, cleanups (2026-10-17)

Design: roller-longdyad-knuckle-3r (verified 18.67 / score 93.21, held out 23.72 at ang_min 26.88). Builds:
`pipeline/full-exo/designs/l1_roller-longdyad` (L1, `pipeline/concept_l1/build_roller_l1.py`) and
`user_roller_longdyad` (full CAD, `pipeline/conformal/param_cad/user_style_roller.py`). The fix list is the independent
check's (`pipeline/full-exo/designs/user_roller_longdyad/VERIFY.md`, `judge/vs_l1.json`): (a) R1 -1.0 vs the L1,
(b) R7 link 1b, (c) R17 twist at 2x clip speed, (d) no judged frame at the drive's working end, (e) link 2's stale
groove, (f) the lobe ring's wall, (g) the two pins, (h) link 1a under the model's strap in the dyad gap.


## 1. R7: the shared strip glue (design-side fix, regression-checked)

**Root cause (measured).** `user_style_minarc.profile_link_split` builds links 1b / 2 as 4 side-view strips glued side by
side. Where two neighbouring strips share a stretch of profile exactly, the exact glue (`US.glue`) leaves **zero-area
faces** on the strip plane: a face bounded by the same line and the same arc twice (gen-6 link 1b: 8 of them). They are
valid in memory (`isValid()` True, which is all the builder checked) and fail BRepCheck once the part is written to STEP
and read back (link 1b: 1-3 faces, the judge's R7 FAIL; gen-5 link 1a: 2 faces). The builder accepted on the wrong test.

**Fix (shared builder, `pipeline/conformal/param_cad/user_style_minarc.py`).**
- `step_bad_faces(s)`: R7's own test in memory (STEP write, read back, BRepCheck per face, solid count) + zero-area count.
- `glue_strips(parts)`: candidates exact glue -> fuzzy fuse 1e-4 -> 1e-3 mm (coincident strip edges merge into one edge);
  a candidate with zero-area faces is re-sewn without them (`drop_zero_faces`: sewing at 1e-4 closes the zero-width gap,
  kept only if one valid solid of the same volume to 0.1 %); the first candidate that passes the STEP round trip with no
  zero-area face wins, else the old one-profile fallback.
- `sliver_free(body)`: the same re-sew on a finished part (later fuses / cuts can leave one), gated by the STEP test.
- Effect on the geometry: <= 0.001 mm (fuzzy value); no profile, station or level changes.

**Regression (part_validity's own test on every link part; gen 4b / 5 run with glue v1 = exact / fuzzy candidates, before the
re-sew step was added - `strip_glue_regression_v1_*.json`; the committed `pipeline/conformal/param_cad/strip_glue_regression.py`
re-runs it on the final code, queued; gen 6 = the final code in the rebuilt CAD):**

| build | link 1a | link 1b | link 2 | before |
|---|---|---|---|---|
| gen 4b user_minarc_bdp | exact, 0 bad | fuzzy 1e-4, 0 bad | exact (+ re-sew), 0 bad | R7 PASS |
| gen 4b user_minarc_pick1 | fuzzy 1e-4 (was the one-profile fallback), 0 bad | one profile (as before: no glue holds), 0 bad | exact, 0 bad | R7 PASS |
| gen 5 user_geneva_rod | fuzzy 1e-4, 0 bad (**was R7 FAIL, 2 faces**) | fuzzy 1e-4, 0 bad | exact, 0 bad | R7 FAIL |
| gen 6 user_roller_longdyad | (chain, not strips) 0 bad | fuzzy 1e-3, 0 bad (**was 1-3 bad**) | exact + re-sewn, 0 bad | R7 FAIL |

pick1's link 1a now glues as 4 strips where it fell back to one profile: a geometry change for its next rebuild (closer to
the strap), stated. Results: `docs/research/roller-longdyad-gen6_fix/strip_glue_regression_v1_*.json`.

## 2. R6 on the L1 and link 1a's climb (DESIGN change, L1)

The L1 drew link 1a's strap as the model's fitted slab, whose hub-footprint lift rises INSIDE the base's J1 upper boss
(R6 0.98 mm, every frame). The full CAD already drew link 1a as a line/arc chain starting at J1's skirt. Now there is one
source: `build_roller_l1.link1a_path` (J1 seat at J1's skirt **+ 0.15** (was 0.2 in the full CAD), concave R2 bend, ramp
<= 60 deg (60.0 used), convex R2 bend onto the K pad plane, 0.2 run, K seat solved >= hr + 0.05), used by the L1's strap
keep-out (`link1a_strap_mesh`, the 8 x 3 section swept along it, 3 mm into each pad) and by `user_style_roller.link1a_path`.

| L1 (fast judges, farm, FEA skipped) | before | after |
|---|---|---|
| R1 | 81.9 % | 82.0 % |
| R1-aim | 48.5 % | 48.6 % |
| R4 | 74.4 % | 74.5 % |
| R6 | 0.98 mm FAIL | **0.0 PASS** |
| R7 / R16 / R17 / R11 | PASS / 64.2 % / PASS / 0.39 | same |
| passing | 7 / 19 | **8 / 19** |

(h) stays as a stated deviation: the chain runs up to 4.40 mm under the model's strap in the dyad gap (it climbs from
J1's level where the model's strap is lifted over J1's footprint). Both builds now carry it, so the judges see it.

RESULTS_PLACEHOLDER
