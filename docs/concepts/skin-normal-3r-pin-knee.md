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

## Spec corrections (said, then built)

* **Stack.** The judge's emulation thinned the leader's slide stage (rail/carriage heights 3/3); the real knee has no
  carriage B, no bridge and no riser, so it is modelled as its own parts: hub 3 (O20 x 12.25, its lower plate = member
  3), an 8 x 3 Ti E strap leaving that plate at hub 3's face and ramping (<= 60 deg, skin-fitted underside) to an O12
  E boss at the knee level tr, an O12 arm pad (on the cuff/BOTTOM) at tr, and the knee link (O12 ends, 10 wide) at
  tr + tp + 0.5 (tp = (stk - 0.5) / 2 per plate). Honest pin stack `stk` = 5.0 mm (iglidur GSM sleeve + 2 GTM washers on
  an integral O4 Ti pin over two 2.25 mm plates; tools/hardware_catalogue.json IGLIDUR-PIN "~4.5-5 mm") and 6.0 mm for an
  MR63ZZ pair (two 2.75 mm plates). If the E strap's fitted underside cannot meet hub 3's face or the boss level within
  0.15 mm, the hub face / knee level rises (never the skin).
* **The knee's reference.** The knee is built at the mid drift m (centre of the J3-line drift box over the bench +
  fit clips), E pointing phiE in hub 3's plane (0 = distal along the humerus), the knee link phib from pin a. The
  two-circle branch is the one that holds the build posture; it is tracked through the 10 fps clips (q1, q2,
  q3' = q3 + phi, pin a, pin b all continuous, step <= 25 deg) and the knee angle is held in [30, 150] deg (away from the
  straight and folded singular postures). A frozen shape keeps m (`m_fix`) when worn on another bench.
* **No pad offset k0.** The catalogue's "pad offset k0" is the same freedom as (phiE, lE, lc, phib) at fixed m; the model
  sweeps phiE instead (the E direction), which also moves the knee off the humerus line.

## Model (docs/concepts/models/skin-normal-3r-pin-knee.py)

Built on the leader's file (its Design: seats, closed-form spherical IK, J1/J2 on GH rays, J3 tilted b3) and the
seed's verified VModel (closure < 0.5 deg, jam rule, fitted undersides, greedy pose dropping recorded as contact).
Members: 0 scapula (hub 1), 1 link 1 (+ hub 2), 2 link 2, 3 hub 3 + E strap + E boss (rotates phi about d3 relative
to the arm), 5 the arm (pad), 6 the knee link. Part-part checks at every taken pose: link 2 vs hub 1, hub 3 vs hubs
1-2, link 1 vs hub 3, link 1 vs link 2, hub 1 vs hub 2 (static), knee link and pad vs hubs 1-2 and links 1-2 (1 mm),
pad vs hub 3 and the E strap (1 mm), E strap vs hubs 1-2 and link 1 (1 mm); adjacent (0.15 mm, else the pose jams): E
strap vs link 2 (J3), knee link vs hub 3 and vs the E strap away from pin a. Link 2 is fitted to fly over the knee and
pad boxes. Skin-checked but not scored: hub side walls and crown discs, strap tops, E top, boss and pad rings, pad top,
knee link edges and top. Scored: every underside (2 mm grid). Modes: `check`, `redteam`, `frozen` (fit on
Bench(60,160) fast, wear the shape on Bench(110,360) without refit; CB_EXACT=1 for the exact path).

