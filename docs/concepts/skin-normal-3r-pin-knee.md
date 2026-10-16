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

### Deeper version, round-3 lead note (answered 02:05 UTC, before the resumed sweep)

* **What the expert does beyond the spec here.** (i) Test the one freedom the knee newly buys - b3 is no longer capped
  by slide travel - on the exact bench, not only fast; (ii) check what a knee adds that a slide stage did not: a MOVING
  body (the knee link sweeps up to lE + lc around hub 3), so the swept-link pairs (knee vs hub 3, knee vs the E strap,
  knee and pad vs link 2) are part-part checks at every pose (R16); (iii) write the MVP2 moment path: the knee link is
  a two-force member, so J3's torque reaches the arm as a force along the knee link - measure the transmission ratio per
  pose instead of assuming it; the out-of-plane (elevation) force crosses the pins as thrust + a tilting moment
  (lever = lc) that the miniature guides could not carry; (iv) attack the measured limiter (the J1-J3 axis-angle window,
  i.e. the J2 fold) directly before calling anything converged.
* **Rawest material.** The per-pose J1-J3 axis angle theta = angle(u1, Q u3) over the 360 workspace poses of
  Bench(110,360) (no digested reach number), the posed skin under hub 2 when its seat moves, the drift s = Q^T t3 per
  pose (knee sizing), the 10 fps fit clips (knee branch continuity).
* **Methods.** IK-only maps of the fold window (no distances, so cheap and exact), closed-form two-circle knee, the bench
  (fast grid for the search, CB_EXACT=1 for the claim), CMA-ES on the farm (tools/concept_cma.py, one job per stream,
  `--bench-cache`), the frozen-shape protocol (fit on Bench(60,160) fast, wear on Bench(110,360) exact).
* **Outside checks.** tools/concept_bench.py, the seed VModel rules, the `frozen` audit (near-touch incl. crowns,
  overhead split), the red-team pose groups below, and the round-3 verifier.

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



## Results (Bench(60,160) fit; Bench(110,360) exact frozen = the number that counts)

| config | what | Bench(60,160) | Bench(110,360) exact, frozen shape | reach / ib14 / contact (exact) |
|---|---|---|---|---|
| k10 | leader k4216 seats, knee posterior (phib -90), lE 30 / lc 25, 5 mm pin stack | 26.34 fast | 33.84 (score 87.69) | 0.619 / 0.845 / 0.003 |
| k264 | coarse-sweep best (az1 108, el1 66.8, az2 19.4, el2 56.1, b3 0.157, lE 35.6, lc 18.6) | 26.47 fast | **31.22 (score 88.65)** | 0.617 / 0.883 / 0.012 |
| k299 (D1) | CMA stream D (az1 87.1, el1 60.2, az2 14.4, el2 49.5, b3 0.362, lE 32.7, lc 28.0, phib -56) | 26.17 exact path / 25.87 fast | 31.96 (score 88.38) | 0.597 / 0.895 / 0.012 |
| reference | zero-passive spherical 3R at the leader's seats (round-3 judge) | - | 41.73 | |
| reference | 2-slide leader osn k4216, verified | 32.61 fast | 42.59 | |

The flat pin knee beats both references on the verification bench by ~10 gap points with 0 passive translations (the
2 crossed RSR3M guides, carriages and bridge are gone: a 5 mm pin stack replaces a 10.5 mm guide stack). It does NOT
cross score 90 on the verification bench: every config loses 28-30 gap points to reach alone.

**Freed b3 (lead-note test).** The knee removes the slide-travel cap on b3, but b3 also turns u3 and shrinks the J2-J3
arc a2, i.e. the fold window: at the k10 seats and knee, b3 0.23 -> 26.34; 0.40 -> 32.37 (fold 47 -> 50, a2 74.1 ->
71.0); 0.60 -> 136.84 (drift 33 x 37 mm, the knee link sweeps over the E strap: 98 jams); 0.80 -> 161.67. CMA streams
started at b3 0.45 / 0.5 / 0.65 end at 34.03 / 34.10 / 28.80 (b3 0.536, Bench(60,160) exact path). The free b3 does not
pay; the CMA's best sits at b3 0.16-0.36.

**The limiter, measured (IK only, Bench(110,360), 360 workspace poses).** theta = angle(u1, Q u3), the J1-J3 axis
angle, must lie in [|a1 - a2| + 10, a1 + a2 - 10]. At k10 (a1 40.3, a2 74.1) the window is [43.7, 104.4] = 60 deg; the
workspace needs 27-141 deg (5th-95th percentile, 6-175 in all): 62 poses fold low, 70 high, kinematic reach 0.633.
Overhead (elevation >= 140, 28 poses) needs theta 22-146 deg: 9 in the window, 9 below, 10 above. The window width is
2 min(a1, a2) - 20, so a1 (the angle between the two GH-ray hubs J1 and J2) sets reach: moving J2's seat down
(az2 / el2, IK only) gives a1 44 -> 0.683, 52 -> 0.733, 57 -> 0.811, 65 -> 0.889, 78 -> 0.939. **Proximity forbids it:**
on the bench at el2 45 (a1 52) hub 2 must sit 93 mm from GH (61 at k10) and the gap is 64.54; el2 40 (a1 58.5) 99.6 mm,
71.91; el2 20 (a1 78) 114.7 mm, hub 2 0 % in band, 79.55. Hub 2 rides on link 1 over the posterior shoulder; the lower
its GH ray, the more deltoid it must clear. Same result as the leader's fold-frontier study (offset-skin-normal-3r.md):
the knee changes the closure, not the GH-ray hub layout, so the fold frontier stays closed.

**Wide seat sweep with the knee (240 LHS configs on the farm, az1 80-118, el1 50-80, az2 -25-30, el2 28-58, wd 68-92,
wa -22 to -4, b3 0.05-0.6; k10 knee).** Best 36.26 (a1 43.7: fold 38 but 20 poses to skin, contact 0.110); median 76.87.
Every config that widens a1 past ~44 deg trades fold poses for skin poses (hub 2 / link 2), the same frontier as above.

**What score 90 on the verification bench needs.** gap = 100 (0.90 - reach) + ... <= 27.5 needs reach >= 0.625 with
in-band 0.90, follow 0.95 and zero contact; at the measured in-band (0.88-0.90) and contact (0.3-1.2 points), reach
>= ~0.65. The best frozen reach is 0.619. The remaining lever is a fold lever stacked on this closure (acromial-rocker-3r,
spine-parked-j2-3r, j2-arc-sector-3r), not more search here.

## Red team (k10, Bench(60,160) fast; k10 / D1 on Bench(110,360) exact frozen)

* **The pose that jams.** No knee jam at the CMA bests on the fit bench; on the big bench the frozen D1 knee is out of its
  window (`slide`) at 13 poses and jams 9 (knee vs E strap 5, E strap vs link 2 4). At b3 >= 0.6 the knee link sweeps
  the E strap at ~100 poses: the swept knee is a real R16 constraint, checked at every pose (knee-hub 3, knee-E, knee-L1/L2,
  pad-hub 3, pad-E, pad-L1/L2, E-L2 adjacent at J3).
* **The point that pinches.** Hub 2's crown/wall at 0.25 mm (scored underside 0.49 mm) at plane 0 / elev 75 / axial 45
  (flexion with external rotation): hub 2 on link 1 over the posterior acromion. Near-touch: k10 fast 3 poses < 1 mm ->
  29.95, 17 poses < 2 mm -> 49.80; k10 exact frozen min 0.2 mm, < 1 mm -> 35.58; D1 exact frozen min 0.1 mm (plane -15,
  elev 45, axial 60), 11 poses < 1 mm -> 38.45, 31 < 2 mm -> 52.82.
* **The optimistic number.** The fit-bench gap (25.87-26.47) is 5-7 points optimistic against the frozen big bench
  (31.2-33.8): the fold boundary is tuned to the 160 sampled workspace poses (lesson c) and the knee window to the fit
  drift. Overhead (elevation >= 140, exact frozen): reach 0.29 (k10 and D1), in-band 0.90 / 0.96 - the overhead loss is
  all fold.
* **Pose groups (k10 fast).** rest 5/5 taken, median 10.4 mm, ib14 0.73; overhead 7/17, 9.1 mm, 0.90; across the body
  24/36, 13.9 mm, 0.50 (metal high across the body); behind the back 14/19, 10.3 mm, 0.90. Every pose not taken is fold
  except 2 skin drops.

## MVP2 moment path (pins vs the miniature guides)

The knee link is a two-force member (pins a and b carry no torque), so J3's torque reaches the arm as a force along line
(a, b). Arm torque about the d3-parallel line through GH per unit J3 torque = dist(GH', ab) / dist(C, ab): measured over
the Bench(110,360) poses that close, k10 0.79-1.24 (median 1.20, lever of J3 on the knee force >= 27 mm), D1 0.46-1.38
(lever >= 17.7 mm) - J3 never loses its drive (the [30, 150] deg knee window keeps line ab off C). The in-plane reaction
goes to the GH joint through the cuff. The elevation drive (J1/J2) reaches the arm as a force along d3 at the pad (lever ~60 mm about GH, the pad's distance
along the humerus) plus whatever couple the pins pass in tilt: thrust on the GTM washers and a tilting moment ~F x lc
(25-28 mm) on pins a and b. MVP1 (unpowered, tracking loads < 1 N m [est], docs/research/passive_dof_hardware.md) puts
< ~0.5 N m on each pin: a 4 mm iglidur sleeve in the 5 mm stack carries it (the RSR3M it replaces is rated 0.29 N m
static). MVP2's 25 N m design moment needs ~400 N at the pad and ~10 N m of tilting moment per pin [est]: beyond a 4 mm
sleeve in a 5 mm stack. For MVP2 the knee pins become hub-sized bearing pairs (the O20 MR117 stack, 12.25 mm, or the
MGN12H-class alternative of the hardware note), i.e. the MVP2 knee costs ~7 mm more stack than the MVP1 knee measured
here - still no guide (none of the miniature guides carries it either, 10-80x short). The MR63ZZ pair (6 mm stack) was
33.53 vs 33.09 fast at the k4216 seats (phib +90): 1 mm of stack costs ~0.4 gap points.
