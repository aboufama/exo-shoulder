# rail-elbow - J2 as a curved rail on link 1, link 2 shrinks to a carriage beside the arm-end hub

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the rail for what it is: the
   locus, in link 1, of every place the carriage will ever be. All of it is metal in every pose, so the rail's radius is
   set by the worst skin under ANY part of it in ANY pose, not by the deltoid cap the carriage sits on. Measure that
   per rail station before believing the "constant radius over the round cap" argument. (b) Cut the rail to the carriage
   travel actually used (plus half a carriage, an end stop and a fixing tab) instead of +-15 deg, and attach strap 1 at
   the rail END (a carriage that grips both rail edges cannot pass a mid-span support - the spec's mid-point strap is
   wrong). (c) Pick the side of the hub the rail runs on (d_off sign) and its polar offset so the rail lies over the
   lowest skin, and if the constant radius is the limiter, try the variant that removes it: a cam track (radius varying
   along the rail, the carriage's radial position fixed by the track, so no undetermined coordinate).
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (the cached
   grid and the exact libigl path), the fit-clip frames in time order (B.clip_order, with the motion slerped between
   bench frames for continuity), the everyday-workspace envelope. The skin-motion map is a digest; it is only used to
   pick the low-motion W candidate (112, -15) the spec names.
3. **Methods and tools.** The shared kit (tools/concept_kit.py): exact two-circle closure of the spherical 3R
   (residual reported), K3 march for every skin-facing sample, flat O20 hubs with the 12.25 mm stack, 12 x 3 straps
   with the 60 deg climb limit, K7 neck to BOTTOM, dense K2 continuity along the slerped motion, K6 sampled-volume
   collisions; the rail + carriage as one constant-radius member (a rigid carriage on a rail about p2 can only run on
   a circle: constant polar angle AND constant distance from GH).
4. **What, other than me, shows the number is right.** tools/concept_bench.py on Bench(60, 160) (same poses and metrics
   as every concept, champion 68.93), the kit's audit (hub size, sampling density, pose locality), the swarm's
   adversarial verifier, and the red-team pose list below (rest, overhead, across-the-body, behind-the-back, the pose
   that sets the rail radius).
