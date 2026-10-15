# seed-pauldron-shells - nested sliding shells (pauldron) + arm ring

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat each "shell on shell" slide as
   what it really is: a large-diameter revolute about an axis through GH, i.e. a ring bearing (a T-slot channel at a
   colatitude g about the axis, slider inside, iglidur liner) whose stack (7 mm) replaces the O20 hub's 12.25 mm
   crown - and only build the ARC each slider actually travels (measured on the bench), not a full shell. The webs
   between the rings follow the skin (K3 undersides) instead of one sphere about GH; the arm ring axis may be tilted
   off the humerus axis (still through GH) so a circular track sits closer to a non-round arm.
2. **Rawest material.** The posed skin of every bench pose itself (signed-distance grid of the rig's render skin per
   pose, fit-clip frames + everyday workspace; held-out clips never loaded), the slider travel measured per pose from
   the closure (not a range from a summary), and the per-sample skin requirement marched along rays from GH.
3. **Methods and tools.** tools/concept_kit.py (K1 two-circle closure, K2 dense continuity along the interpolated
   motion, K3 march undersides, K6 part-part collisions, K7 neck to BOTTOM), tools/concept_bench.py Bench(60, 160) on
   the fast grid cache, vectorised over every pose; a coarse-then-refined grid sweep written incrementally.
4. **What, other than me, shows the number is right.** The bench (the same outside judge as the 3R champion,
   gap 68.93), the adversarial verifier re-running the model on the exact path / full bench, and a red-team pose list
   (rest, overhead, across the body, behind the back, plus the measured worst poses of the best config) in this file.
