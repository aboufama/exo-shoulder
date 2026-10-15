# skin-normal-hubs-selfaligning - skin-normal hubs + passive cuff translation stage (non-concurrent 3R)

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Make the morphology a continuous
   family that CONTAINS the verified state of the art, so the sweep can only lose to it by measurement, never by
   construction: each hub line goes through its skin seat with direction nlerp(seat ray, skin normal, beta), beta 0 =
   the line through GH (the spherical 3R), beta 1 = the hub square on its seat. Seat the champion's own axes first
   (J1 bvec(2.4, 80.7), J2 at its rest-pose axis bvec(30.6, 4.9), J3 wdir(86.3, 21.8)) and only then wander to the
   spec's acromion / supraspinous seats. Reuse the verifier-checked closure (seed-offset-3r-slides: orientation = the
   spherical IK of the axis DIRECTIONS, the line offsets become a drift of member 3 that 3 passive slides absorb
   exactly), and close the verifier's open hole in it (the member-3 bridge strap between the neck and the
   across-carriage, +1.7 gap there) instead of inheriting it. Price the stage: the drift grows with the line
   offsets (2 d sin(q/2)), so cap each slide (S_max) and let the bench see the metal.
2. **Rawest material.** The posed render skin of the rest pose (seat points and mean face normals within 10 mm, libigl
   exact distance - not the grid), the posed skin of every bench pose through the bench's signed distance, the fit
   clips at their full 10 fps for continuity (pipeline/conformal/band_poses_wsf.b64), and the skin-motion map
   (pipeline/conformal/analysis/skin_motion_map_14.json) / proximity atlas for where the hubs can sit.
3. **Methods and tools.** Paden-Kahan spherical IK on the axis directions + exact line-offset drift (screw
   composition X_k), Grubler-Kutzbach mobility of the loop scapula -> chain -> stage -> humerus -> GH, sphere tracing
   on the signed-distance grid for every underside, exact cylinder / box signed distances for part-part clearance,
   CMA-ES (pycma) on the cloud CPU farm from the top of a 239-configuration coarse design of experiments.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, same metrics as the
   baseline 68.93 and the verified leaders), the in-model references run in the same sweep (the champion seats at
   beta 0 = the seed-offset family's spherical control; slides 0 = no stage), the adversarial verifier, and the
   red-team list below (the pose that jams, the point that pinches, the optimistic number).
