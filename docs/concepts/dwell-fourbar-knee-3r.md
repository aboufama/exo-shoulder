# dwell-fourbar-knee-3r - a spherical Watt six-bar knee in link 2 of the zero-passive 3R (pins only, no spring)

## Deeper version (answered before modelling, 2026-10-16 04:58 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the loop as a coupler-curve design problem, not as "a knee": in link 1's frame the J3 axis traces a curve
     u3(s) on the sphere as the crank (q2) turns, and the only thing that matters for reach is the range of
     angle(u1, u3(s)) on ONE monotone, singularity-free arc of that curve. Measure that window per configuration
     (IK only, exact) before any skin evaluation, and gate every configuration on it.
   - Run the locked control in the same file and through the same checks (knee rigid, no P / Q / rocker): any gain must
     be the loop's, not the re-tuned seats' (the rail-elbow lesson).
   - Price the loop's real cost: three extra pin stacks (MR63ZZ pair, 6.5 mm) and a rocker layer that must pass over
     link 1 and L2a; model each body (link 1 + its P plate, L2a, L2b + its Q tail, the rocker) and exempt only parts of
     the same rigid body from each other.
   - Ask the R17 / tolerance question of a closed spherical 4R loop (J2, K, Q, P): with four pins it is overconstrained
     and binds unless the axes meet at GH within the bearings' tilt play; the generic fix is a rocker with one
     spherical end + one U end (mobility 1 for any axis error), priced in stack.
2. **Rawest material.** The posed skin of every bench pose (signed-distance grid, exact libigl path for the claim), the
   per-pose J1-J3 axis angle theta = angle(p1, p3) computed from the raw scapula / humerus frames of the 160 / 360
   workspace poses and the 10 fps fit clips (the window demand, not a reach summary), the skin-motion map
   pipeline/conformal/analysis/skin_motion_map_14.json and the proximity atlas for where pin Q (deltoid edge /
   posterior axillary fold) can live.
3. **Methods and tools.** Closed-form spherical loop closure (two-circle K1 closure for pin Q on a 0.25 deg crank grid,
   secant-refined per pose to < 1e-3 deg), the kit (tools/concept_kit.py: K3 march, K4 flat hubs, K5 straps, K6
   collisions, dense K2 along the 10 fps motion), the seed's crown / wall / near-touch / overhead audit
   (spine-parked-j2-3r extras), the farm (tools/cloud_run.py sweep for the coarse sweep, tools/concept_cma.py batch jobs
   for CMA-ES), the frozen-shape protocol (fit Bench(60,160) fast, wear on Bench(110,360) exact).
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, metrics, contact rule), the
   kit audit (`honest`), the locked control in the same file, the frozen Bench(110,360) exact run, and a red-team
   pose list (rest, overhead >= 140, across the body, behind the back, posterior axillary fold poses #92/#93/#115,
   closest metal incl. crowns of the pins).
