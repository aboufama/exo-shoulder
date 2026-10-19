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
