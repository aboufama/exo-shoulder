# offset-arc-selfalign: skin-shaped offset arc + self-aligning cuff

## Deeper-version answers (written before the work)

1. **What a top mechanism designer would do that the spec does not ask for.** Size the stage from the measured
   offset error instead of guessing it. The J1/J3 offsets are chosen by a minimax LP that minimises the radial slide
   travel (the slide that squeezes the liner), in the spirit of the P0 offset-axis LP. The designer would also ask
   whether the arc's radius is even the limiter. If the 3R family loses on how high the rigid band has to sit over the
   skin it passes, a circle that is not centred at GH only helps where the skin envelope really is a circle with a
   different centre. Measure that before sweeping.
2. **Rawest material.** The posed skin itself per bench pose (the signed distance of every band sample to the posed
   render skin, B.dist), the full-rate fit clips (continuity and the arc's guide-azimuth range at 10 fps, not the 60
   sampled frames), and the skin-motion map `pipeline/conformal/analysis/skin_motion_map_14.json`. On that map the W axis
   (BOTTOM hub) moves 23.4 mm relative to the skin under it, and the b axis (base) only 1.8 mm. That is the size of
   the problem the stage must absorb at J3 and the reason the stage sits on the arm side.
3. **Methods and tools.** Exact composed-rotation kinematics (orientations do not depend on where the axes sit,
   only the end translation t_E does). Sphere tracing on the skin SDF for the lowest rigid height of each member over
   the poses it takes (the concept_baseline convention: the p-th percentile, poses above it count as contact). A
   minimax LP (scipy HiGHS) for the axis offsets. Box, annulus and cylinder SDFs for >= 1 mm part-part clearance. All of
   it runs on tools/concept_bench.py (fast SDF cache).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, the same poses and metrics
   as the 3R baseline at gap 68.93), the adversarial verifier that re-implements the chain, and the red-team pose list
   below (the poses that set each rigid height, the poses where a slide hits its stop, the worst part-part clearance).
