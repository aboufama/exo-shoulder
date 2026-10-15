# Verification: l1_seed-offset-3r-slides (L1 keep-out CAD of seed-offset-3r-slides k 403)

The skeptic re-measured the stage-2 claim (commit ea2cbd6) on 2026-10-15. It used its own scripts, single-threaded on
the local box, on a scratch copy of the design dir. It did not touch the farm judge or its finisher.

**Verdict: not refuted.** Every number the scorecard states reproduces within 0.5 points. Every PASS is a real PASS.
Two of the rows marked "pending" will FAIL when the farm returns: R6 part contact (0.81 mm) and R2 overall (24.87 mm
from the user's own forearm cuff, the same as the champion). Neither is a wrong claim, because neither was claimed.

## 1. Member frames vs the bench model

The model (VModel k 403, refitted on Bench(60,160) fast: gap 54.95, as in build.json) was posed at 6 clip frames. Its
metal samples were compared with the posed exo.glb (scene_export.frame_xforms, each part's own group). Script:
`kin_check.py` in the verifier scratchpad.

| pose | clip, frame | plane / elev / axial | model -> glb max | q diff | closure | model metal to skin |
|---|---|---|---|---|---|---|
| overhead peak followed | Raise overhead 48 | 30 / 107.2 / -51 | 0.000 mm | 0.0004 deg | 0.0001 deg | 0.83 mm |
| behind the back | Reach back pocket 72 | -80 / 39 / 101 | 0.000 mm | 0.0004 | 0.0001 | 2.63 mm |
| across the body | Wash opposite shoulder 81 | 145 / 46 / -69 | 0.000 mm | 0.0003 | 0.0002 | 2.58 mm |
| held out | Wave 48 | 15 / 92 / -60 | 0.000 mm | 0.0005 | 0.0001 | 1.48 mm |
| held out | Walking 0 | 90 / 4 / -90 | 0.000 mm | 0.0002 | 0.0001 | 2.71 mm |
| high elevation | Comb hair 105 | 78 / 143 / -67 | 0.000 mm | 0.0003 | 0.0002 | 2.09 mm |

All 9 model parts (hub1-3, neck, rail, carA, bridge, L1, L2) match the glb exactly at every pose. **Confirmed.** The
highest followed frame of Raise overhead is at elevation 107 deg; above it the chain is at the J2 fold, as the claim
says. The overhead peak puts metal 0.83 mm from the skin. That is out of band, but it is not contact.

## 2. Parts at real size; missing or parked parts

- Hubs: O20 keep-outs at HUB_R 10. The lower plate runs F..F+3 and the upper boss + cap F+3.15..F+12.25
  (docs/HARDWARE.md v5). **Real size.**
- Links: 8 x 3 mm straps, Ti. Rail: 8 x 4 x 45.6 mm. Carriage A: 20 x 39.8 x 4 mm. Carriage B: 20 x 20 x 4 mm. Rail
  mount: 4 mm slab, 12 x 33 mm. These are built and judged.
- **Missing (acknowledged in the claim):** the radial-slide guide (+-7.6 mm stroke) and the base tab. Carriage B is a
  plain 4 mm box with no guide. A real radial slide needs guide length of at least the stroke plus the bearing length
  along the skin normal, so it adds radial height on the outside, away from the skin. This is the largest honesty gap
  left in the L1 CAD. R1 is probably optimistic for carriage B / the bridge region, which is already 0 % in band
  (27 mm) per the build report.
- No parked parts: every keep-out part sits in its kinematic group (base, l1, l2, l3, l4, H).
- R7: part_validity.json covers the 12 non-H parts. The 2 H-group proxies (rail, rail mount) are watertight volumes per
  parts_full.json but are not in the validity file. The R8 mass sum covers all 14: **104.28 g, confirmed.**

## 3. Held-out clips

- `tools/concept_bench.py` excludes Wave and Walking from the bench poses (docstring, line 38). The CMA and the
  underside refit both use Bench(60,160), so the design was not fitted on held-out data.
- Both held-out clips are in clips.json and were judged: Wave 172 frames, Walking 109. **Confirmed.**
- Caveat (a project-wide convention, not this design's error): the clip builder holds a frame whose model metal enters
  the skin (18 Wave frames, -8.6 mm). R2 therefore never sees that contact; it shows up only as lost follow in R3. A
  real arm would push the cuff into the mechanism instead of waiting. The R3 loss on Wave (58.6 %) is the honest
  signal of that generalisation failure.

## 4. Judges re-run (local, scratch copy)

| row | claimed | re-measured | how | status |
|---|---|---|---|---|
| R1 (14 mm) | 53.7 % | per-clip follow identical (overhead 55.7, Wave 58.6, others 100 %); not re-run at 14 mm (box load 14) | score_design.py step 3 | consistent |
| R1-aim (10 mm) | pending | overhead 16.1 %, drink 20.4 %, comb 26.8 % (remaining clips running at the time of writing) | score_design.py step 3 | FAIL (far from 90 %) |
| R2 | pending | **this project's parts 0.0 mm** (attributable 0.0) over 228 frames. Overall max 24.87 mm: the user's FOREARM CUFF, the same part and value as the champion | judge/body_contact.py --step 6 | will be FAIL (user's part), ours clean |
| R3 | 88.7 % | 88.7 % at step 3; **88.26 %** at full 30 fps (1180 of 1337 frames) | clips.json held flags | confirmed (0.4 pt) |
| R4 | 36.4 % | Raise overhead follow 55.7 % x in-band, same as the 14 mm score file | score_14mm.json | confirmed |
| R6 | pending | **0.81 mm, FAIL** (target <= 0.15). Link 1 strap inside link 2 strap: 16 of 117 frames, worst at the followed overhead peak (Raise overhead 48) and Wave 120. Link 2 strap inside the J3 lower plate: 0.58 mm in every frame (static overlap at the J3 hub: the strap runs one station past the hub rim into the next member's plate) | judge/part_contact.py --step 12 | FAIL (champion 1.03 mm) |
| R5 / R5-aim | 3 / PASS | 3 revolute joints set the orientation (R123 = Q). The 3 slides take up the offset position, so nothing is undetermined | design.json + chain() | confirmed |
| R7 | PASS | 12 of 12 validity files OK, plus 2 watertight proxies | part_validity.json | confirmed |
| R8 | 104.3 g | 104.28 g | parts_full.json | confirmed |

One wording correction: score_design.py runs at step 3, which is 10 fps. It does not run at "30 fps". The 30 fps
follow share is 0.4 points lower than the stated R3.

The model's part-clearance check (collide, >= 1 mm) covers only non-adjacent pairs. The link 1 / link 2 crossing at
the overhead peak is between adjacent members (they share J2), so the clip builder could not see it. A rebuild should
check adjacent straps against the 0.15 mm rule, and start the link 2 strap at the J3 plate's rim instead of inside it.

## What this means for the loop

The stage-2 conclusion stands: the bench lead does not survive the built CAD. R1 ties the champion (53.7 vs 54.1 %),
and R3 and R4 are worse because of the CMA-made J2 fold. The next steps in the claim are the right ones:

1. Add an overhead / no-fold term to the bench gap.
2. Fit the undersides on all fit-clip frames.
3. Model the radial-slide guide.

To those, add:

4. An adjacent-strap clearance check in the builder (R6).
