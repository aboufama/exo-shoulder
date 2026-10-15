# fivebar-roll: spherical five-bar pointer plus an active arm roll

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the two elbows as the only metal
   that has to cross the cap and choose the two base axes so that each elbow's circle (cone a_k about u_k) lies over
   the LOW skin of the cap for the poses it is used in, instead of one fixed nominal; check the parallel singularity
   along the actual clips (dense continuity), not only at the frames; and make the two couplers short so that the
   rigid links never have to clear the highest skin they pass over. Also check the coaxial (rhombus) variant: one
   base hub instead of two removes a 12 mm crown over the scapula.
2. **Rawest material.** The posed skin of every bench pose (the signed-distance grid of the rig's render skin), the
   fit motion clips densely interpolated between bench frames, and pipeline/conformal/analysis/skin_motion_map_14.json
   (where on the arm skin moves least: W* = wdir(112,-15)) - not the screen numbers in the catalogue.
3. **Methods and tools.** Spherical kinematics (two-cone closure K1 per leg, Gruebler count), the shared kit
   (tools/concept_kit.py: K3 march skin-fitted undersides, K4 flat O20 hubs, K5 straps, K6 collisions, K2 dense
   continuity), a vectorised coarse-then-refined sweep over the base axes, arcs, W and branches.
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, Bench(60,160) on the fast
   grid cache, K3 march mode), the kit's audit (honest flag), the adversarial verifier on the exact path, and a
   red-team pose list (rest, overhead, across-body, behind-back, the pose with the least clearance on the best config).
