# seed-2r-cring: 2R spherical shoulder + C-ring axial bearing on the upper arm

## Deeper-version prompt, answered before the work

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the ring as what it is: the third
   joint of a spherical 3R whose last axis is the humerus long axis. So (a) choose u1 from the measured cloud of arm
   directions in the scapula frame so that d never comes near u1 or -u1 (the 2R's gimbal lock is the only singularity;
   it decides reach before any proximity question); (b) let the ring axis tilt a few degrees off the GH-elbow line so
   the circle is centred on the real arm cross-section at its level (the track must be a circle about an axis through
   GH, the arm is an oval that is not centred on that line); (c) put the C opening where the carriage never goes AND the
   torso is (measure both, do not assume "medial"); (d) hang the passive slide on BOTTOM's bar (it already runs down
   the arm, parallel to the slide) instead of adding a new body; (e) check the ring's outer face against the torso,
   not only its inner face against the arm.
2. **Rawest material.** The posed render skin of every bench pose through the signed-distance grid (not a digested
   radius table): the ring radius is fitted per azimuth and level directly on it; the fit-clip frames in time order for
   continuity; the arm-direction and carriage-azimuth clouds computed from the pose frames themselves.
3. **Methods and tools.** Spherical-linkage closure (two-cone intersection, branch kept by sign), singularity margin
   on the cone angles, K3 skin march for straps, a Lipschitz march on the signed distance for the ring radius, dense
   continuity along the slerped motion (K2), part-part clearance (K6) plus by-construction clearances for the
   ring / carriage / slide that the shell model of K6 cannot represent; the shared kit (tools/concept_kit.py) for all
   of it except the fixed-geometry ring.
4. **What shows the number is right, other than me.** tools/concept_bench.py (fast grid, Bench(60,160)), the
   adversarial verifier re-running on the exact path, and a red-team pose list (rest, overhead, across the body,
   hand behind the back, full axial rotation at 90 deg abduction) with the pose that jams and the point that pinches.
