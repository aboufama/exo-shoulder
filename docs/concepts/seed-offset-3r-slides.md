# seed-offset-3r-slides - non-spherical offset 3R with passive self-aligning slides

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Count the loop's mobility before
   modelling (Grubler on scapula -> chain -> cuff -> humerus -> GH): the spec's 3R + 2 slides cannot close on a 3-DOF
   arm once the axes are offset, so fix the passive set first. Then use the offsets for the one thing they can buy - a
   rigid link sweeps a surface of revolution about its OWN axis line, so move each axis line until that surface matches
   the skin it passes over (scapula / acromion / deltoid are not spheres about GH) - and price the slide stack's height
   honestly, because every passive slide under hub 3 lifts the whole distal chain off the arm.
2. **Rawest material.** The posed render skin of every bench pose (signed distance per point, not a summary), the fit
   clips at their full 10 fps for continuity (pipeline/conformal/band_poses_wsf.b64: FI order, HG / RS rotations), and
   the skin-motion map (pipeline/conformal/analysis/skin_motion_map_14.json) for where skin rises under a link.
3. **Methods and tools.** Closed-form spherical IK of the axis directions (Paden-Kahan subproblems) + exact offset drift
   t3(q) absorbed by the slides (s = Q^T t3); Grubler-Kutzbach mobility; sphere tracing on the bench's signed-distance
   grid to fit each rigid underside to the envelope of the skin over the poses it takes (the band evaluator's free
   underside with <= 60 deg ramps); exact cylinder / box signed distances for part-part clearance; a coarse-then-
   coordinate sweep of the 6 offsets and the slide ranges on the common bench.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, same metrics, same contact
   rule as tools/concept_baseline.py's spherical 3R: 68.93), the adversarial verifier that re-runs the model, and the
   red-team pose list below (the pose that jams, the point that pinches), plus the slide-travel histogram per pose.

