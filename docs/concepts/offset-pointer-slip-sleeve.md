# Offset-centre 2R pointer with a sliding twist sleeve (offset-pointer-slip-sleeve)

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the rod line as a free design
   choice, not "the line O -> C": a straight O->C rod converges on O (deep inside the shoulder), so every mm of rod
   proximal of the sleeve sinks ~0.25 mm toward the arm axis - the rod's own travel buries it. They would check that
   first (a one-line geometric bound), then tilt/offset the prismatic axis so it lies along the arm surface (a
   Stanford-arm style offset P, still 6 coordinates for the cuff's 6 DOF), and shape the bar as a skin-fitted rigid
   body in ITS frame (it never follows axial rotation, so its underside must clear the arm at every axial angle).
2. **Rawest material.** The posed skin of every bench pose (the signed-distance grid of `B.skin(i)` per pose, not a
   summary), the fit-clip frames in time order (`B.clip_order()`, held-out clips untouched), the band humerus and
   scapula rotations from `pipeline/conformal/band_poses_wsf.b64`, and the skin-motion map
   `pipeline/conformal/analysis/skin_motion_map_14.json` to place the hubs where the skin moves least.
3. **Methods and tools.** Closed-form inverse kinematics of the pointer (J1, J2 from dh, slide from |C - O|, J3 and the
   two U angles from the cuff orientation); per-sample skin-fitted undersides by the kit's K3 march along rays from
   the joint centre O (not from GH, since link 1 and the bar rotate about O); K2 dense continuity along the slerped
   motion; K6-style pairwise clearance; vectorised over poses on the Bench(60,160) grid cache; coarse-then-refined
   sweep of |o|, its direction, a1, cuff station / azimuth, rod height and rod tilt.
4. **What shows the number is right, other than me.** `tools/concept_bench.py` (the same skin, poses and metric as
   the 68.93 champion), the adversarial verifier re-running the best config on the exact path, and a red-team pose
   list (rest, overhead 150-170 deg, across-the-body, behind-the-back, extreme axial rotation) with the worst pinch
   point and the pose that jams.
