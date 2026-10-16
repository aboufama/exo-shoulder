# skin-normal-3r-pin-knee - the leader 3R closed by a flat two-pin knee (0 passive translations)

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the knee as a planar RRR dyad
   and size it from the drift it must absorb (the J3 line drift in hub 3's plane, measured per pose, not assumed),
   keeping the knee angle away from its two singular postures (straight: the closure loses in-plane stiffness;
   folded: the E arm hits the pad) with a hard 30-150 deg window. Put all three knee plates in ONE layer pair (E end
   boss and the arm pad at the same level, the knee link above both) so the stack is exactly the pin stack, nothing
   more. Check the swept knee against everything it can reach (hub 3, the neck/E strap, link 2), because a knee is a
   moving body where a slide stage was a fixed one. Ask whether the knee also re-tunes the axis seats (a free b3 now
   that no slide travel caps it), and price the pin stack honestly (iglidur pin 5 mm, MR63ZZ pair 6 mm, not 2 mm).
2. **Rawest material.** The posed skin of every bench pose (signed distance of every sampled metal point, fast grid
   and the exact libigl path), the fit clips at their full 10 fps (pipeline/conformal band poses through
   tools/concept_bench.py: HG / RS per frame) for the knee-branch continuity, the rest-pose skin mesh for the seat
   normals, and the per-pose J3 drift s = Q^T t3 itself (not the travel summary) to size the knee.
3. **Methods and tools.** Closed-form spherical IK of the axis directions (the leader's), the 2-slide closure theorem
   (J1/J2 on GH rays -> the arm-vs-member-3 drift is planar in hub 3's plane), a closed-form two-circle closure of the
   planar RRR (J3 centre, pin a, pin b), sphere tracing on the bench SDF to fit every underside, exact cylinder / box
   signed distances for part-part clearance, the cloud CPU farm (tools/cloud_run.py sweep) for the coarse sweep and
   tools/concept_cma.py (one farm job per CMA stream) for the refinement.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, metrics and contact rule as
   every row), the seed VModel checks the model inherits (closure residual, jam rule, 10 fps continuity, part
   clearance), the leader's verifier harness pattern (docs/concepts/verify/offset-skin-normal-3r.py: frozen shape worn
   on Bench(110,360) exact, near-touch, overhead split, crowns), and the red-team pose list at the end of this file.

