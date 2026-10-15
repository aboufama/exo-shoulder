# seed-spm-3rrr - low-profile spherical parallel 3-RRR around the shoulder

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Not accept "every link at skin +
   clearance": in an SPM the nine links of three legs cross each other over the same patch of skin, so the real design
   problem is *layering* (which leg rides on which radial shell, Agile-Eye style nested spheres) and *where the legs
   live on the sphere* (keep each leg on its own patch so it never has to stack). They would also place the
   type-2 singularity surface outside the workspace by choosing the platform-axis triangle, not just check cond(J);
   and they would make the platform the *cuff itself* (axes fixed in the humerus) so no extra platform ring adds height.
2. **Rawest material.** The posed render skin of every bench pose (B.skin, ray-cast exactly from GH into a per-pose
   cube map of the first skin exit and the far side of the arm/trunk gap), the scapula and humerus rotations of every
   fit-clip frame and workspace pose (B.frames), the clip time order (B.clip_order) for continuity - not the digested
   skin-motion summaries. The skin-motion map (pipeline/conformal/analysis/skin_motion_map_14.json) only matters for a
   skin-riding part; here every part is rigid and rides on hubs, so the skin is used as an obstacle field per pose.
3. **Methods and tools.** Closed-form leg IK (intersection of two cones on the unit sphere, branch fixed per leg),
   the Gosselin SPM Jacobian J = B^-1 A with cond(J) <= 50 for both singularity types, slerp sub-steps between
   consecutive clip frames for continuity, rigid parts fitted to the q-quantile of the skin under each sample over the
   kinematically valid poses (the baseline's percentile idea), KD-tree part-part clearance >= 1 mm, the bench's signed
   distance (libigl / fast grid) for every metal sample at ~1 point / 4 mm2.
4. **What other than me shows the number is right.** tools/concept_bench.py (same poses, same signed distance, same
   metrics as the baseline), the adversarial verifier of the swarm, and a red-team pose list in this file (the poses
   where the best configuration jams, collides or pinches, with the measured part and distance).
