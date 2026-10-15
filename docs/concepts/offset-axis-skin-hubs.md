# offset-axis-skin-hubs - off-sphere skin hubs + passive cuff stage (axis directions spherical, axis lines free)

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Not start from zero: two verified or
   screened relatives already ARE slices of this morphology (seed-offset-3r-slides: champion directions + small
   offsets; skin-normal-hubs-selfaligning: lines through skin seats, a 1-D offset per hub tied to the skin normal,
   best screened 35.86). Parameterise each axis line as a free direction + a free 2-D perpendicular offset (up to
   30 mm) so the family strictly CONTAINS both, seed it at their best lines (reproduced to 1e-5 mm), and spend the
   search on the freedom they did not have - the offset direction not tied to the normal, J1 pinned or not, the stage
   station down the arm, the travel cap. And before trusting any inherited number, run the inherited best under the
   verifier's full checks (the seed's VModel: closure residual, hub 3 / bridge vs rail, member-3 riser), because the
   relative that scores 35.86 was built on the screening Model, not the VModel.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (every
   underside fitted per sample, not a summary radius), the rest-pose render mesh (libigl exact distance) for the line
   seats, the fit clips at full 10 fps for branch continuity (pipeline/conformal/band_poses_wsf.b64), and the
   skin-motion map (pipeline/conformal/analysis/skin_motion_map_14.json) / proximity atlas for where a hub's face can
   sit; the slide travel per pose (s = Q^T t3) straight from the closure, not a travel estimate 2 e sin(q/2).
3. **Methods and tools.** Paden-Kahan spherical IK on the axis directions + exact screw composition of the offset
   lines (the drift of member 3, absorbed by 3 passive slides), Grubler-Kutzbach mobility of the loop
   scapula -> chain -> stage -> humerus -> GH, sphere tracing on the signed-distance grid for every underside, exact
   cylinder / box signed distances for part-part clearance, a 240-configuration design of experiments and then CMA-ES
   (pycma) on the cloud CPU farm (tools/cloud_run.py sweep) until the convergence gate passes.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses and metrics as the 68.93
   baseline and the verified leaders); the verifier's own check code (seed-offset-3r-slides VModel), reused unchanged;
   the in-model references in the same sweep log (k 0-1: the relative's best lines under these checks); the adversarial
   verifier on Bench(110, 360) exact; the red-team list below (the pose that jams, the point that pinches, the
   optimistic number).
