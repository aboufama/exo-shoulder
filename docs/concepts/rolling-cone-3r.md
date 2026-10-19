# rolling-cone-3r - hubless strap-held conical rolling pairs (apex GH)

Round 501 (G1, golden track), carried catalogue entry. Model: docs/concepts/models/rolling-cone-3r.py. Sibling pick (not
duplicated here): rollcone-hubspot-pinknee-3r (rolling J2 only, on H1). This row asks the question that pick does not:
**does rolling at J1 or J3 buy takes on top of the rolling J2?**

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat each rolling pair as what it is
   kinematically - a 2R pair (sun axis c, planet axis m0) with a fixed linear coupling y = r x - and ask which joint's
   coupling moves the fold. Rolling at J1 makes the J1-J2 arc a1 a function of q1 (the arm's azimuth about J1); rolling
   at J3 makes a2 a function of q3 (the arm's axial rotation). The lead loses 64 of its 88 fold poses at IR >= 90
   across the body - a coordinate only a J3-side law can see. So screen the three placements separately and in
   combination, as a law-only ghost first, before any metal. Second: a rigid-cuff variant (every contact through GH,
   no knee) because a rolling J3 kills the knee's planar closure (GH is a fixed point, so the knee would lock).
2. **Rawest material.** The posed humerus orientations of Bench(110,360) / Bench(60,160) (`concept_bench._poses_all()`
   HG, the band frames) and the clip frames with 2-deg slerp sub-steps; H1's seats taken from its own Design object
   (offset-skin-normal-3r.py `Design`, reference configuration Q = I), not from summaries. The skin enters only past
   step 0 (the rolling bands' one-level clearance from the posed skin, `concept_kit.requirement`).
3. **Methods and tools.** Batched Gauss-Newton IK on the coupled chain (residual < 0.01 deg), the instantaneous-dyad
   fold margin (contact lines w1, w2, w3: the Jacobian's rank-loss distance in the dyad's own angle, the kit's 5 deg),
   the design branch sign, warm-started clip continuation; numerical check that the rolling pair's relative angular
   velocity lies on its contact line (1e-4 deg); a sweep on Bench(60,160) ws poses, read on Bench(110,360) with clip
   continuity (do not tune the fold to the 160 poses).
4. **What, other than me, shows the number is right.** The ghost reproduces the judge's own reads to the pose: H1
   263 ws / 110 clip / 13 overhead, rollcone J2 25/10/30 285 / 110 / 17 (round501_ideation.md table). The verifier
   and the auditor re-run the same cells; the red-team pose list is the takes the rolling cell adds over its control
   (attributed by elevation / axial rotation), and the rule questions go to the user (hubless joint vs "O20 v5 at every
   joint"; strap-held cones vs "no gears, pulleys or cables").

## What was built (step 0: law-only ghost, then a one-level band check)

`docs/concepts/models/rolling-cone-3r.py` (scripts and raw reads in `docs/research/rolling_cone_3r/`).

- **Joint law.** Pair k = sun cone (axis c, half-angle ga, proximal member) + planet cone (axis m0, half-angle gb,
  distal member) touching along the generator w (the 3R's axis at the reference Q = I). Relative rotation
  `T(t) = R(c, t/(1+r)) R(m0, t r/(1+r))`, `r = +- sin ga / sin gb` (internal pair: r < 0). Checked numerically: the
  relative angular velocity lies on the contact line to 1e-4 deg (external and internal). Equivalently a 2R pair with
  a fixed linear coupling: a knuckle with a linear law whose axis walks about c by t/(1+r).
- **Spec corrections.** (1) The spec's equal-cone `R(c, phi) R(m0, phi)` is one cell of the general law above (r = 1).
  (2) A rolling J3 cannot keep the two-pin knee: with GH a fixed point the knee closure has isolated solutions (the
  round-501 class (c) result), so the all-rolling chain is a RIGID cuff with J3's contact through GH (b3 = 0) - as the
  catalogue spec says - while rolling J1 / J2 can sit on H1's knee chain unchanged.
- **Fold reading.** Instantaneous dyad of the contact lines w1, w2, w3: margin = min(th - |a1 - a2|, a1 + a2 - th) >= 5
  deg (kit FOLD_MARGIN) on the design's branch; it is the rank-loss distance of the Jacobian [w1 w2 w3].
- **Takes.** Gauss-Newton IK (< 0.01 deg) from the 3R seed; ws pose taken if on branch with margin >= 5; a clip frame
  is followed if every 2-deg slerp sub-step from the previous followed frame is (warm-started, <= 10 deg per step).
- **Calibration (outside numbers reproduced to the pose).** H1 263 ws / 110 clip / 13 overhead and the judge's J2 cell
  25/10/30 285 / 110 / 17 (round501_ideation.md), Bench(110,360).
- **Search.** 3141 configurations, random + CMA-ES on Bench(60,160) ws takes (+0.1 x overhead, soft margin), arc caps
  in the objective: contact walk <= 20 mm at R 60, sun arc <= 120 deg, planet arc <= 240 deg, |1 + r| >= 0.25 (the
  ringroll lesson: an internal pair with near-equal cones spins its carrier 10x and floats). Read on Bench(110,360).

## Results (kinematic, Bench(110,360): ws / 360, clip / 110, overhead / 28)

| cell | chain | ws | clip | overhead | rim arcs (sun / planet / walk) |
|---|---|---|---|---|---|
| H1 control (3 pins) | knee | 263 | 110 | 13 | - |
| judge's J2 25/10/30 (pick #2) | knee | 285 | 110 | 17 | 43.5 / 105.8 deg / 19.2 mm |
| J2 internal 28.75/6.12, beta -140.7 | knee | 289 | 110 | 18 | 40.7 / 183.4 / 20.5 |
| J1 alone 14.7/7.8 | knee | 268 | **100** | 12 | 101 / 190 / 26.8 |
| J1 + J2 (11.4/5.9 + 29.4/5.8 int.) | knee | **295** | 110 | 18 | J1 99 / 191 / 20.6; J2 41 / 199 / 20.9 |
| rigid control (3 pins, b3 0) | rigid | 265 | 110 | 12 | - |
| J3 alone 17.2/5.9 | rigid | 266 | **101** | 11 | 71 / 205 / 22.0 |
| J2 alone (internal cell) | rigid | 292 | 110 | 16 | 40 / 181 / 20.2 |
| **all three (spec), seeded CMA best** | rigid | **297** | 110 | 15 | J1 86/187/21; J2 40/205/21; J3 53/254/15 |

Where the takes come from (best knee cell vs H1): IR >= 90 45 -> 60 of 106, across-the-body 15 -> 21 of 46, behind the
back 46 -> 51 of 54, overhead 13 -> 18 of 28; the stretched-side losses fall 69 -> 49. Min th margin over taken poses
5.16-5.32 deg.

**The J2 pair carries the gain: ~27 of the all-rolling chain's +32 takes.** Rolling J1 or J3 alone adds 1-5 ws and
BREAKS clip continuity (100 / 101 of 110 followed; measured, cause not attributed); stacked
on a rolling J2 they add +5 to +6 ws (297 vs 292 rigid, 295 vs 289 knee) at full continuity - and on the Bench(60,160)
search sample J1 added only +1 (138 -> 139), so that +6 is a read on poses the search never saw, not a fitted gain.

## Metal at one level per part (Bench(60,160) fast, kit q 0.97 rule: worst 3 % of poses are contacts)

Bands 2.5 mm wall, 8 mm radial, sampled 2 mm along the used arc x 2 rows, ONE underside level per band (strap-held
pairs cannot be skin-contoured - the judge's flat-level rule); the same rule on H1's own kinematics puts the O20 hub-2
disc at in-band 0.964 (control).

| band (all-rolling best cell) | R_lo mm | in-band 14 | in-band 10 | contact poses / 201 |
|---|---|---|---|---|
| J1 sun (base) | 51 | 0.999 | 0.608 | 0 |
| J1 planet (link 1) | 51 | 1.000 | 0.756 | 1 |
| J1 O20 disc control | 51 | 0.998 | 0.627 | 0 |
| J2 sun (link 1) | 64 | 0.872 | 0.163 | 4 |
| **J2 planet (link 2)** | **135** | **0.003** | 0.002 | 6 |
| J3 sun (link 2) | 80 | 0.432 | 0.223 | 0 |
| J3 planet (member 3) | 81 | 0.492 | 0.283 | 0 |
| J3 O20 disc control | 82 | 0.361 | 0.167 | 0 |

- **J1 bands fit** the acromion top exactly as well as an O20 disc, ~4 mm lower crown (+8 vs +12.25).
- **J3 through GH is out of band** at one level (0.43 / 0.49; the O20 disc there 0.36): a rigid-cuff J3 on a GH ray
  over the arm cannot sit in the band - the reason the knee chains tilt J3 off GH (b3). This kills the spec's rigid
  all-rolling chain as a <= 14 mm design at these seats.
- **RED TEAM for pick #2 (rollcone-hubspot-pinknee-3r): the J2 PLANET band is lifted by the elevated arm root.** On
  the judge's own 25/10/30 cell (knee chain) the planet band's per-pose requirement is median 56, p95 64.3 mm, but 8 of
  194 taken poses (3 of them clip frames) need > 75 mm: elevation 149-150 at plane 0-30 and elevation 90-105 at plane
  -15. The overhead ones are the poses the rolling J2 is meant to add: 2 of its 6 overhead ws takes on Bench(60,160)
  and 3 overhead clip frames (elevation 149-150, plane 30). One level at q 0.97 sits at 135 mm (in-band 0.007); at
  q 0.95 it is 64 mm with those 8 poses as contacts. The sun band alone reproduces the judge's 0.96 (0.962); whether the
  judge's "bands 0.960" included the planet side is for the pick's modeller to check. The internal J2 cells
  that read best kinematically (289 vs 285) are worse in metal (sun band 0.56 vs 0.96).

## Verdict

**Dead as specified (three hubless pairs, rigid cuff); the lever it contains lives on in pick #2.**

1. Kinematically the three pairs reach 297 / 110 / 15 - above the 275 a 95 needs - but the J2 pair alone gives 292;
   the J1 and J3 pairs add 5 takes and two more rule-gated hubless joints with 187-254 deg planet arcs.
2. In metal, the rigid-cuff J3 through GH sits at in-band 0.43-0.49 at one level, and the J2 planet band is lifted to
   135 mm by the arm root in the overhead poses: the chain cannot reach in-band 0.90 at these seats.
3. Convergence gate (kinematic objective, score points): all-rolling seeded CMA gain 0.68 over the 2nd half, 0.23 over
   the last third, top-5 spread 0.23; J1 0 / 0 / 0; J3 0.23 / 0 / 0.23; J2 0.23 / 0.23 / 0.23 - converged.

Hand-offs:
- **To pick #2:** measure the planet band at one level on the overhead poses before any claim; try the planet on the
  J1 side (swap which member carries the small cone, beta + 180) so the arm root never passes under it.
- **J1 rolling on top of the J2 pair** (+6 kinematic on the 360, 0 lost, full continuity, both J1 bands in band at
  R 51) is the only extra pair worth a cell; it is another hubless joint for the user's rule question.
- **Rule questions for the user** (unchanged from the judge's list): hubless rolling joints vs "O20 v5 at every joint";
  strap-held cones vs "no gears, pulleys or cables"; strap pricing (pick #2: cx 6.5 with 2 straps; this chain's 3 pairs,
  rigid cuff: tools/simplicity.py v2.2 --score 19.5 with the 6 straps as flexures x 3, 1.5 if straps are not flexures).

No bench gap is claimed: this row is a law-only ghost plus a part-level band check; reach / follow are kinematic upper
bounds and are NOT bench numbers.
