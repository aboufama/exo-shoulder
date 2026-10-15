# scapular-race-j2-carriage - J1 is a rail on the bony rim, J2 rides its carriage

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the rail as what it is: a
   scapula-fixed part that is metal in EVERY pose along its whole length. Its radius is set by the highest skin under
   any station in any pose, so the rail may only be laid over stations whose skin never rises - choose the rail extent
   from the measured per-station requirement, not from a fixed phi window (design step `travel()`: the contiguous run
   of "quiet" stations, requirement <= `rmax`, that holds the most closing poses). (b) Make the carriage honest: a
   rolling carriage about a1 can only run on a surface of revolution about a1, so the rail is one circle at ONE
   distance R; V-rollers hang beside the rail head down to R; the J2 O20 lower plate IS the carriage plate, riding
   0.5 mm over the rail top (F = R + 4.5). (c) Check that the one moving strap L2 can be in band at all - the proximity
   atlas says a closure-frame link crosses skin that moves ~40 mm under it - and if it is the limiter, look for J3
   placements that make L2 short.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (cached grid,
   K3 march per sample ray), the fit-clip frames in time order (`B.clip_order`, slerped between frames for K2), the
   everyday-workspace envelope. The skin-motion map and the atlas are digests; they only guided where to look (the
   scapula-fixed quiet zone: top cap el > ~65 deg plus a posterior lobe, docs/research/proximity_atlas.md).
3. **Methods and tools.** The shared kit (tools/concept_kit.py): exact two-circle closure (a1, p3; arcs gamma, alpha23),
   K3 march for every skin-facing sample, flat O20 hubs with the 12.25 mm stack (J2 on the carriage, J3 on the arm),
   12 x 3 strap L2 with the 60 deg climb limit and `over` the race and the neck, K7 neck to BOTTOM, dense K2
   continuity along the slerped motion, K6 collisions. Sweeps on the cloud CPU farm (tools/cloud_run.py sweep), coarse
   random then CMA-ES from the top configurations until the convergence gate passes.
4. **What, other than me, shows the number is right.** tools/concept_bench.py on Bench(60, 160) (same poses and metrics
   as every concept; champion 68.93), the kit's audit (hub size, sampling density, pose locality), the swarm's
   adversarial verifier, and the red-team list below (rest, overhead, across the body, behind the back, the pose that
   sets the rail radius, part-part clearance re-checked in true 3D).

## Morphology and model

(results below are filled in as the sweep runs)
