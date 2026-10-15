# Sliding-rivet pauldron (hubless nested plates, follower-in-slot joints)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Check that two rollers in two coaxial
   slots really make a revolute (they do only if the rollers are neither on one meridian nor 180 deg apart: the spec's
   layouts leave a first-order slide), give every roller its real stack (an O8 x 4 roller cannot hide in a 2 mm plate:
   it protrudes and needs a retaining flange, and J1's flanges face the skin), and treat the joint radius as free per
   plate (posts on L1 so the band sits at its own radius instead of lifting the whole top stack). Then ask the real
   question of the family: a plate that turns about an axis through GH keeps every point at a fixed radius, so it must
   clear the highest skin it sweeps over - plates make that worse than straps (more area under them), unless each
   plate's skin is itself nearly spherical about GH over the poses it rides.
2. **Rawest material.** The posed render skin of every bench pose (B.skin / B.dist: the radius of the local outer skin
   along every sample ray, pose by pose, not a digested envelope), the fit-clip frames at 10 fps for continuity, and the
   skin-motion map (pipeline/conformal/analysis/skin_motion_map_14.json) to read how far the skin under each plate rises
   and falls relative to GH across the range.
3. **Methods and tools.** Spherical 3R closure (two-circle intersection, the band evaluator's convention), exact
   per-sample skin radii by sphere tracing on the bench's signed-distance field, plate outlines from the slot spans
   (+ rim), member-to-member interference by point-in-solid tests in member coordinates, branch-flip test on every
   10 fps frame, coarse -> one-at-a-time -> local-random sweep on Bench(60, 160) (cached SDF grids).
4. **What else shows the number is right.** The common bench (tools/concept_bench.py, same poses / metrics as the
   3R baseline 68.93), the adversarial verifier that re-runs the model, and a red-team pose list (rest, overhead,
   across the body, behind the back + the worst pose for each limiter) with the per-pose reason a pose is not taken.
