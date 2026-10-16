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
| F1 (freed b3) | CMA stream F (b3 0.536, az1 98.9, el1 66.3, az2 11.1, el2 55.1, lE 30.3, lc 26.0, phib -82) | 28.80 exact path / 28.95 fast | 37.04 (score 86.53) | 0.594 / 0.851 / 0.015 |
| **k4598 (B2)** | CMA round 2 stream B (az1 105.8, el1 65.5, az2 17.7, el2 56.3, wd 76.5, wa -13.3, b3 0.325, lE 42.1, lc 24.9, phiE 1.5, phib -55.9) | **20.63 fast (score 92.50)**: reach 0.694, ib14 0.903, follow 1.0, contact 0 | **30.35 (score 88.96)** | 0.606 / 0.904 / 0.009 |
| k3326 (D2) | CMA round 2 stream D (az1 91.5, el1 60.3, az2 17.2, el2 47.9, wd 81.7, wa -12.7, b3 0.403, lE 25.4, lc 34.5, phiE 4.3, phib -50.0) | 21.33 fast | 31.35 (fold 112, knee out of window 23) | 0.603 / 0.899 / 0.015 |
| reference | zero-passive spherical 3R at the leader's seats (round-3 judge) | - | 41.73 | |
| reference | 2-slide leader osn k4216, verified | 32.61 fast | 42.59 | |

The flat pin knee beats both references on the verification bench by ~10 gap points with 0 passive translations (the
2 crossed RSR3M guides, carriages and bridge are gone: a 5 mm pin stack replaces a 10.5 mm guide stack). On the fit bench the converged
CMA (round 2, 8 farm streams, 6600 configs) crosses score 90: 20.63 = reach only (in-band 0.903, follow 1.0, contact 0).
It does NOT survive on the verification bench: worn frozen on Bench(110,360) exact it is 30.35 - reach 0.694 -> 0.606
(the fold boundary tuned to the 160 sampled poses, lesson c) costs 29.4 points, in-band holds (0.904), contact 0.9.

**Freed b3 (lead-note test).** The knee removes the slide-travel cap on b3, but b3 also turns u3 and shrinks the J2-J3
arc a2, i.e. the fold window: at the k10 seats and knee, b3 0.23 -> 26.34; 0.40 -> 32.37 (fold 47 -> 50, a2 74.1 ->
71.0); 0.60 -> 136.84 (drift 33 x 37 mm, the knee link sweeps over the E strap: 98 jams); 0.80 -> 161.67. CMA streams
started at b3 0.45 / 0.5 / 0.65 end at 34.03 / 34.10 / 28.80 (b3 0.536, Bench(60,160) exact path). The free b3 does not
pay; the CMA's best sits at b3 0.16-0.36. On the verification bench the freed-b3 best (F1, b3 0.536) wears to 37.04: it beats
the zero-passive spherical 41.73 but loses 5-6 points to the b3 0.16-0.36 knees (fold 130 vs 121-136, in-band 0.851).
Farm and local frozen runs of D1 agree to the digit (31.96).

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

## Verdict (2026-10-16 03:30 UTC)

**Screened, not dead - the best 0-passive-translation closure of the GH-ray 3R measured so far, but it does not reach
score 90 on the verification bench.** Bench(60,160) fast: 20.63 (score 92.50, k4598), converged (gate over 7199 logged
configs: gain 0.25 over the second half, 0.00 over the last third, top-5 spread 0.06 score points; CMA round 2 alone,
6600 configs: 0.25 / 0.00). Worn frozen on Bench(110,360) exact: 30.35 (score 88.96) - better than the zero-passive
spherical 3R at the leader's seats (41.73) and the 2-slide leader verified (42.59) by 11-12 points, with 2 cheap pins in
place of 2 crossed guides, carriages and a bridge. The whole remaining gap is reach (the J2 fold): in-band 0.90, follow
1.0 and contact ~0.01 on the verification bench.

**Limiter (measured).** The J1-J3 axis-angle window 2 min(a1, a2) - 20 deg (~60 deg at a1 ~40) against the 27-141 deg
the workspace needs (22-146 overhead): reach 0.69 on the 160 fit poses, 0.61 on the 360 verification poses, 0.25-0.29
overhead. Widening a1 moves hub 2 onto skin it cannot clear (93-115 mm off GH, measured; the wide LHS never beats 36).
The knee is the right closure; the fold needs a lever that does not ride on a GH ray: next, stack this knee on
acromial-rocker-3r / spine-parked-j2-3r / j2-arc-sector-3r (their fold levers) - the knee's ~10 points over the slides
should carry over, since it only touches member 3. For MVP2 the knee pins become hub-sized bearing pairs (~7 mm more
stack), see the moment path above.

**Knee-window variant (tested, small).** D2 loses 23 verification poses to the frozen knee window (knee near straight,
max 149 deg on the fit poses). Widening the window to [20, 160] deg (ang_min 20; J3's lever on the knee force falls
to lE sin 20 = 8.7 mm, a weaker MVP2 closure) gives fit 21.70, frozen exact 31.24 (out-of-window 23 -> 21): the losses
are the knee's span (|pb - C| beyond lE + lc - 1 on drifts the fit poses never reached), not its angle. A knee sized
over the full-ROM drift (IK only, a dense grid of the workspace, not a bench sample) is the next small lever (<= ~5
points at D2, an upper bound that ignores those poses' skin).

**Red-team items for the verifier.** Near-touch on the verification bench (k4598): min 0.02 mm at the arm-at-side poses
(plane -15 / 75, elevation 0), 16 poses < 1 mm -> 38.41, 47 poses < 2 mm -> 64.60 - the zero-contact fit is a
0-2 mm skim in places. Knee window: the frozen knee leaves its window at 4 big-bench poses (`slide`), E strap vs link 2
jams 2. Overhead (elevation >= 140): reach 0.25, in-band 0.94.

## Files

docs/concepts/models/skin-normal-3r-pin-knee.py (model), docs/concepts/sweeps/skin-normal-3r-pin-knee.json (7199
configs in order: early local checks, coarse farm sweep 256, CMA round 1 on the exact path (no bench cache on the farm
jobs: 9 evaluations per stream), wide seat LHS 240, CMA round 2 with the cache 6600), docs/concepts/rows/
skin-normal-3r-pin-knee.json.

## Verification (independent verifier, 2026-10-16 ~03:58 UTC)

Harness: `docs/concepts/verify/skin-normal-3r-pin-knee.py` (frozen-shape protocol: fit on Bench(60,160) fast, worn on
Bench(110,360) with CB_EXACT=1, no refit; the model's own checks plus the verifier's). Run locally as one niced process
(177 s; the farm sweep hook cannot run the frozen protocol or the added checks).

What was attacked and what it found:

| check | result |
|---|---|
| ACTIVE DOF / undetermined passives | 3 active (J1-J3), 2 passive pins parallel to J3, 0 translations. With J1/J2 on GH rays the link-2 -> arm motion is a planar rotation about the GH line parallel to d3; the planar RRR (J3, a, b) has 3 planar DOF, so q3, qa, qb are fixed by the closure on a fixed branch (knee angle kept in [30, 150], never singular). Nothing sags (R17). |
| independent 3D closure (per taken pose, from the member transforms, not the closed form) | hub-3 centre via link 2 vs via member 3 0.000 mm; pin a via member 3 vs via the knee 0.000 mm; pin b via the knee vs via the arm 0.000 mm; link-2 -> member-3 rotation off J3's axis <= 0.016 deg; knee rotations off the pin axes <= 0.022 deg; arm rotation residual <= 0.015 deg. 0 poses fail. |
| knee link vs hub 3's upper half (rides with link 2, so non-adjacent: 1 mm, the model used 0.15) | min 24.3 mm - no pose lost |
| E boss (O12 at pin a; the model checks the E strap only) vs hub 1, hub 2, L1 (1 mm) and L2 (0.15, adjacent at J3) | min 24.7 mm (boss-L2) - no pose lost |
| parts at real size / sampling | O20 x 12.25 hubs with crowns and walls, 8 x 3 straps, E strap + boss, knee link (lc + 12) x 10 x 2.25, pad O12, all undersides on the 2 mm grid; 5 mm pin stack = the catalogue's IGLIDUR-PIN (two ~2 mm plates + washer, 4.5-5 mm) |
| joint ranges | J3 travel 186.8 deg over the taken poses (O20 hub with an MR117 pair: full rotation, fine for MVP1; MVP2 cable routing must allow it), pin a 54.1 deg, pin b 47.9 deg |
| arm pad on the arm | pad centre ~50 mm distal of the J3 line foot in hub 3's plane (47.5 along, -17.2 across): on the lateral upper arm, like the champion's neck end and the leader's cuff rail (all arm-frame-fixed in the bench) |
| bench artefact (fast grid) | the claim is already the exact-path frozen number; reproduced to the digit |

**Verified numbers, Bench(110,360) exact, frozen k4598:** gap **30.35** (score 88.96): reach 0.6056, follow 1.000,
in-band 2-14 0.9043, in-band 2-10 0.5376, contact 0.0091 (why not taken: fold 133, knee window 4, parts 2, contact 3).
Near-touch: min metal 0.02 mm (arm at the side, elevation 0); metal < 1 mm as contact -> 38.41 (16 poses), < 2 mm ->
64.60 (47 poses). Overhead (elevation >= 140): reach 0.25 (fold 17, knee window 4 of 28), follow 1.0, in-band14 0.940.

**Champion on the same bench and checks** (offset-skin-normal-3r verifier, `champbig_frozen`, re-run now): 66.97
(reach 0.700, follow 0.918, in-band14 0.575, contact 0.113; metal < 1 mm as contact 71.20). The knee beats it by 36.6
points (32.8 with the 1 mm near-touch rule on both) and beats the verified 2-slide leader (42.59) with 0 passive
translations. **Verdict: VERIFIED, not refuted.** It does not reach score 90 on the verification bench (needs gap <=
27.5); the whole remaining gap is reach (the J2 fold, 0.25 overhead), and the near-touch at the arm-at-side poses
(0.02 mm) is the next red-team point for the L1 CAD: a 1 mm liner rule costs 8 points.

## L1 keep-out CAD (generation-3 winner, 2026-10-16 ~05:00 UTC)

Design `pipeline/full-exo/designs/l1_skin-normal-3r-pin-knee`, builder `pipeline/concept_l1/build_pinknee_l1.py` (derived
from build_osn_l1.py; the configuration is an INPUT: `--params`, `--params-file`, `--k`, default = the rows file's
best_params, per-joint hubs `--hubs 10,10,10` or rad1..rad3, so the polish run's config drops in), red team
`pipeline/concept_l1/redteam_pinknee_l1.py`.

**Shape = the verified one.** The fit is the frozen protocol's own (k4598 on Bench(60,160) fast: gap 20.63, reach 0.6937,
follow 1.0, ib14 0.9033, contact 0; faces 49.9 / 60.9 / 72.0 mm, knee level tr 78.51, knee centre m (-8.635, 2.252, 0)) -
the shape the verifier wore on Bench(110,360) exact. Parts at real size: O20 x 12.25 hub keep-outs (lower plate F..F+3,
upper boss + cap F+3.15..F+12.25), 8 x 3 straps through the fitted undersides, the E strap (fitted underside 72.0 -> 78.5
mm, 3 mm thick, thinning to the 2.25 mm boss thickness over its last 1.1 mm before the boss rim - a 3 mm strap there would
sit in the knee link, which rides 0.5 mm over the boss), the E boss and arm pad O12 x 2.25 at tr, the knee link a flat Ti
bar 36.9 x 10 x 2.25 at tr + 2.75 (pins 6 mm from its ends: the model's box), pin stack 2.25 + 0.5 + 2.25 = 5.0 mm
(IGLIDUR-PIN), and a 2.25 mm pad mount (proxy) from the pad to the proximal end of the user's BOTTOM bar (24.5 mm, at
61 deg from pin a's direction, outside the boss sweep: E boss / mount >= 3.85 mm over the followed frames). 13 parts,
72.4 g, each one closed single solid (R7: judge/part_validity.py all_ok).

**Built vs the model's metal (7 fit-bench poses: arm at the side, first, middle, the two highest (elev 165 / 150, knee
149.8 / 145.8 deg), behind the back (-90 / 30 / 105), across the body (150 / 45)).** Every rigid sample of the model
(hubs, E strap, E boss, arm pad, knee link) lies on the posed exo.glb within 0.0001 mm; the straps' samples outside the
hub zones 0.000 mm; inside the hub zones (r < R + 3) the built strap sits up to 1.91 mm (link 1, 12 of 36 samples) /
1.09 mm (link 2) ABOVE the model's sample - the stated R6 lift of build_osn_l1.py (the strap reaches its hub's member
level), away from the skin. Built-part frames vs the model's member transforms <= 1e-4 mm (scene_export.frame_xforms on
the clip frame = the judges' path).

**Clips (30 fps, the champion's 8 incl. the held-out Wave / Walking).** 1323 / 1337 frames followed (98.95 %): every
frame of Raise overhead (knee 94 -> 145.8 deg), Drink, Comb hair, high shelf, Wash opposite shoulder, back pocket and
Walking; Wave holds 14 (J2 fold 10, link 1 / link 2 built straps 4 - the only built-pair jam). The knee stays in
94-146 deg (window 30-150). Lowest metal over the followed frames 0.60 mm (Raise overhead). Workspace (1432 poses):
chain + knee close 61.8 %, + parts 60.7 % (the J2 fold, as on the bench).

**Outside judges (tools/cloud_run.py judge on the farm, full run: R6 at every frame; R7 local - the farm image has no
OCC): 9 of 19 pass, the most of any built design.** R1 84.2 % (2-14 mm) / R1-aim 47.2 % (2-10 mm) - the best built
proximity yet (the 2-slide leader's L1 78.7 / 42.0 %, the user-style champion 32.9 / 17.3 %); R3 follows 98.7 % PASS;
**R4 overhead 83.9 % PASS - the first built design to pass overhead** (the 2-slide leader 36.0 %: its guide stack and the
J2 fold held Raise overhead above ~66 deg; this knee follows every frame of it, knee 94 -> 146 deg); R5 / R5-aim 3 DOF;
R6 0.0 mm at all 1337 frames (1026 pairs, dense samples both ways); R7 every part one closed solid; R8 72.4 g; R11 0.22
kPa; R17 moves freely unpowered. Fails: R2 24.87 mm is the user's own forearm cuff in the rig's self-intersection (ours
0.0 mm, as every L1 build), R16 workspace 62.3 % (the J2 fold: 61.8 % of the 1432 poses close, the bench's reach).
Not run: R9 FEA (no STEP parts at L1), R10 base slip. Measurement unchanged from the 2-slide leader's L1 (same clips,
skin, judges).

**Red team (built meshes, exo.glb posed by clips.json, exact posed skin; redteam.json).**
* *The point that pinches:* the J1 / J2 lower plates on link 1, 0.60 / 0.77 mm from the trunk at Raise overhead frame 78
  (plane 30, elev 150, axial -60); metal < 1 mm in 3.8 / 4.3 % of the followed frames, < 2 mm in 4.7 / 11.2 %. Every other
  part keeps >= 1.57 mm.
* *Arm at the side (the verifier's 0.02 mm near-touch):* 126 poses (plane -30..90, elev 0-10, axial -60..90) through the
  design's chain: 112 close with the parts clear; the lowest built metal is hub 3's lower plate, 0.01 mm from the trunk at
  (-30, 0, -30) and (0, 0, -60) - the verifier's near-touch reproduced on the built part. At axial -60 with plane -15 / -30
  (internal rotation, arm at the side) hub 3's plate / link 2 go 4-14 mm INTO the trunk (4 poses): these poses are not
  taken (skin), as on the bench. A 1 mm liner rule costs ~8 gap points (verifier).
* *Posterior axillary fold* (trunk skin within 30 mm of the upper-arm region, behind the coronal plane through GH, below
  it; 409 vertices): link 2's strap comes nearest, 1.74 mm (Comb hair frame 96, 74 / 140 / -65); hub 3 / E strap 3.7 mm;
  the knee parts >= 7.7 mm. Not the limiter.
* *The knee near hub 3 (the pose that jams):* knee link vs hub 3's link-2 half >= 24.3 mm (the verifier's number, now on
  meshes), vs link 2 >= 32.5 mm; knee link vs E strap / E boss / pad mount = the 0.5 mm designed running gap at every
  frame; E strap vs J3 upper boss 0.13 mm (the 0.15 mm face gap at hub 3's rim, sampled); E strap vs link 2 >= 5.4 mm.
  The only jam on built meshes is link 1 / link 2 in Wave (4 frames; 0.25 mm at its closest on the followed frames).
* *The optimistic number:* the fit bench 20.63 vs the verification bench 30.35 (lesson c); the hub-zone strap lift
  (<= 1.9 mm) moves metal away from the skin, so the built R1 is if anything pessimistic there.

## Final polish (Bench(110,360))

**What ran (2026-10-16 04:10-06:20 UTC).** The FINAL POLISH of CLAUDE.md: a multi-start CMA-ES of every free parameter
directly on the verification bench Bench(110,360), fast grid for the search, exact path for the claim, on the CPU farm
(`tools/knee_polish.py`, new; 11 + 11 farm jobs, <= 12 slots, ~$1.9 at cpu3c). Grid cache: key 14f156cb6fc8,
assembled on each worker from the parts `tools/osn_polish.py buildpart` left on the farm volume (grid vs exact on 28 136
points within 20 mm of the skin: mean |error| 0.10 mm, p99 1.08, max 2.24, sign agreement 0.99996). Fast vs exact on
the same fitted shapes: k4598 30.02 vs 29.95, the polished H1 26.45 vs 26.45.

**One evaluation** = the model refit on Bench(110,360) fast + the round-3 verifier's own checks
(`docs/concepts/verify/skin-normal-3r-pin-knee.py` extra_checks: independent 3D closure, knee vs hub 3's upper half at
1 mm, the E boss vs hubs / links) knocking poses out + the model's audit. **Objective = the near-touch gap**: every
taken pose with ANY metal (scored undersides and hub walls, crowns, strap tops, boss / pad rings, knee edges) < 1 mm
off the skin counts as contact. The plain corrected gap is logged with every row. No check was loosened.

**Freed (13 continuous + 3 discrete), bounds keep every hard rule and the real envelopes:** az1 60-135, el1 35-80, az2
-40-60, el2 20-75, wd 50-110, wa -45-20 (axis seats; J1 / J2 on GH rays), b3 -0.3-1.0, lE 20-60 (round 2's HL stream:
-90), lc 14-50, phiE / phib periodic, ang_min 20-45 (the knee window stays >= 20 deg off both singular postures; J3's
lever on the knee force is logged per row), stk 4.5-6.0 (4.5 = two 2.0 mm Ti plates + washer on the iglidur pin,
catalogue IGLIDUR-PIN; 6.0 = MR63ZZ pair); hub radius per joint from the catalogue set only (O20 / O17 / O15, the same
MR117-2RS pair and 12.25 mm stack; **the model gained rad1-3**: disc, wall, crown, part-part cylinder, link-strap ends
and the L1-L2 / E-L2 exclusion zones follow the declared radius; default O20 reproduces k4598 to the digit, 20.63 fast
and 30.35 in the verifier). **Fixed, with the reason:** b1 = b2 = 0 (the knee is planar and closes the link-2 -> arm
motion exactly only with J1 / J2 on GH rays; a tilt makes the drift non-planar, which two pins parallel to J3 cannot
absorb), `neck` (not a parameter of this design: k4598 at neck 13 and 25 gives the same report), bosses / pad O12,
knee link 10 wide, straps 8 x 3, CLEAR 2 / PART_CLEAR 1 / ADJ 0.15 / ramp 60 deg, R_tol 0.5, fold margin 10 deg (the
rule in force when the streams ran).

**Hub sizes at k4598 first (27 combos, Bench(110,360) fast refit, corrected):** the plain gap hardly moves (30.37-31.78:
the knee was not hub-limited, unlike spine-parked's +17); the hubs move the NEAR-TOUCH: O20 J2 leaves 8-9 poses with
metal < 1 mm, O20 J3 4-5, O20 J1 1. O17 at all three: 0 near-touch poses, near-touch gap 36.75 -> 30.52, min metal
0.50 -> 1.12 mm. O15 at J3 adds 3 part jams. (Full table: the scan file below.)

**Streams (popsize 16, objective near-touch gap, Bench(110,360) fast):**

| stream | start | hubs | evals | best near-touch gap (= plain unless noted) |
|---|---|---|---|---|
| A | k4598 | O20 | 1281 | 29.74 |
| B | k4598 | O20 / O15 / O15 | 2609 | 28.40 |
| D | k10 | O20 | 1585 | 29.61 (plain 28.45) |
| E | D1 (k299) | O20 | 1617 | 29.04 |
| F | k5116 (sweep basin) | O20 | 2129 | 28.63 |
| G | k3326 (D2) | O20 | 2433 | 28.92 |
| H | k7076 (sweep basin J) | O20 | 2401 | **26.45** (H1 = H-g107-1) |
| R1 / R2 / R3 | k4598 + 1.5 / 2.0 sigma noise; uniform-random knee (x0 111.15) | O20 | 1217 / 2497 / 993 | 29.26 / **25.67** / 29.63 |
| W1 (weird) | k4598 knee flipped to the other two-circle branch (phiE -39.87, phib 17.53; x0 51.37) | O20 | 2545 | 28.97 |
| HW | H1, sigma 0.6 | O20 | 1633 | **25.58** (HW-g58-11) |
| H17 / R217 / B17 | H1 / R2 / B bests | O17 x 3 | 1553 / 817 / 1457 | **23.11** / 24.24 / 28.11 |
| HL | H1, lE up to 90 | O20 | running at 06:20 UTC | - |
| weird (Bench(60,160)) | J2 hub at the OTHER end of its axis line (az2 + 180, el2 -56.3) | O20 | 1 | dead: hub 2 face 184 mm off GH, gap 372.5 |

Every evaluation is logged in docs/concepts/sweeps/skin-normal-3r-pin-knee.json, stage `polish-big-<stream>` (26 767 rows,
k 7199-33965, with plain gap, near-touch gap, min metal, knee window, J3 lever, hubs).

**What moved and why.** J2's seat goes lower and further back (el2 56.3 -> 47.0 / 44.5, az2 17.7 -> 30.2 / 35.3 for
H1 / HW), J3's seat nearer the humerus axis and further round (wd 76.5 -> 70.4 / 70.9, wa -13.3 -> -8.1 / -5.7): arc a2
72.3 -> 68.3 / 63.4 with a1 ~41. The fold window [|a1 - a2| + 10, a1 + a2 - 10] keeps its ~60-62 deg width but SLIDES
5-10 deg toward small J1-J3 angles, where the 360 verification workspace poses sit that the 160 fit poses under-sampled
(lesson c, now used instead of suffered): fold losses 133 -> 116. The E strap lengthens (lE 42 -> 57-60: round 1 hit the
60 mm bound, hence HL) and the arm pad moves to 82 mm from GH (61): the knee closes the larger drift mid-window (knee
angle 104-149 deg, J3 lever >= 30.5 mm vs 25.3). The near-touch objective removed k4598's 13 poses with metal < 1 mm
(min 0.39 -> 1.38 mm exact). Price: hub 3 face +3.5 mm, knee level +6.3 mm (tr 78.4 -> 84.7), still in band (0.90);
and overhead gets WORSE (elevation >= 140: reach 0.25 -> 0.21 on the bench, 0.19 -> 0.12 held out) - the slide trades
overhead poses for everyday ones. The slimmer O17 hubs add ~2.5 fast points on top (H17 23.11) through near-touch and
skin clearance.

**Measured (H1 = H-g107-1, all hubs O20, fold margin 10; k4598 the same way):**

| protocol | k4598 | H1 (polished) |
|---|---|---|
| Bench(110,360) shape fitted there (fast), worn EXACT, verifier checks: plain gap | 29.95 (score 89.11) | **26.45 (score 90.38)**: reach 0.6472, follow 0.9636, ib14 0.9012, ib10 0.5126, contact 0.0117 |
| same, near-touch gap (metal < 1 mm = contact) / min metal / poses < 1 mm | 36.11 / 0.39 mm / 13 | **26.45 / 1.38 mm / 0** |
| same, fast (search number) | 30.02 | 26.45 |
| the verifier script unchanged (fit Bench(60,160) fast, worn Bench(110,360) exact) | 30.35 (near-touch 38.41) | 28.21 (near-touch 33.77): reach 0.6444, ib14 0.8994, contact 0.0259; 0 closure / knee-hub 3 / boss poses lost; pad 82 mm from GH |
| HELD-OUT exact bench (110 clip + 360 workspace poses disjoint from Bench(110,360); shape fitted on Bench(110,360) fast) | 31.37 (near-touch 36.81, min 0.24) | 28.40 (near-touch 29.56, min 0.82, 2 poses) |
| Bench(60,160) fast (screening bench) | 20.63 | 26.66 (near-touch 29.09) |

H1 params: az1 101.1634, el1 63.8986, az2 30.153, el2 47.0108, wd 70.3931, wa -8.1248, b3 0.2842, lE 59.5534, lc
28.2401, phiE -5.8107, phib -54.914, ang_min 30.4611, stk 5.6815, rad1-3 10 (O20). J1 seat: anterior component 0.085
(back / acromion-top region).

**Gate (docs/METHOD.md).** O20 history (20 331 evals, round 1 then round 2): gain 0.41 score points over the second
half, 0.34 over the last third, top-5 within 0.00 - **passed** (best 25.58, HW). Whole history with the O17 / O15
streams (26 767): 1.24 / 0.55 / 0.08 - **not passed**: H17 was still improving at its last generation (23.11).

**Verdict.** H1 gains 3.50 gap points on the polish protocol (29.95 -> 26.45, crosses score 90), 2.14 on the verifier's
unchanged fit-60 protocol and 2.97 held out, and removes every near-touch pose - but it is MY measurement with the
verifier's harness, not an independent verification: per the polish rule the CAD keeps k4598 until an independent
verifier confirms the >= 1 point gain. The optimistic number: 26.45 is in-sample (shape fitted on the same 470 poses);
held out it is 28.40, and overhead reach fell (0.12 held out). HW (25.58 fast, O20) is measured exact on the farm
(kpol-meas3 jobs, results to kpol/meas/HWb_*.json on the farm volume) but its numbers were not back when this section
was written; H17 (O17 hubs, 23.11 fast) could not be measured exact here because the shared model now refuses
non-O20 hubs (tools/concept_kit.py O20_ONLY, changed by another session at ~06:00 UTC; CB_ALLOW_SLIM=1 re-measures).
Next: re-measure H1 / HW / HL under the repository's current fold-margin default, let an independent verifier rule on
H1, and run the near-touch-objective polish again from HW / HL with the new rules in force.

## Verification (polish) (independent verifier, 2026-10-16 ~06:30 UTC)

Claim checked: the polished H1 = H-g107-1 (O20 x 3, fold margin 10) scores 26.45 on Bench(110,360) exact with the
verifier checks (shape fitted on Bench(110,360) fast), near-touch 26.45, min metal 1.38 mm, against k4598 29.95 the
same way. Harness: `docs/concepts/verify/skin-normal-3r-pin-knee-polish.py` (new; it imports the round-3 verifier
`docs/concepts/verify/skin-normal-3r-pin-knee.py` UNCHANGED - last edited 03:38 UTC, before the polish - and runs its
extra checks, then the model's audit on the corrected set; it adds only the fit bench as a choice, a held-out bench and
red-team numbers; raw outputs in `docs/concepts/verify/skin-normal-3r-pin-knee-polish.results.json`). Not `tools/knee_polish.py`: no code of the polish author drives the numbers below. 10 farm jobs
(exo-cpu1, 2 vCPU each, CB_EXACT=1 for every wear bench, ~$0.03 in all).

**Checks not loosened.** The model's diff since round 3 only adds rad1-3 (catalogue radii, O20 = the old code path); k4598
through the unchanged protocol reproduces 30.35 / near-touch 38.41 / 16 poses / 0.02 mm to the digit. Every verifier
check ran: independent 3D closure (hub-3 centre / pin a / pin b 0.000 mm, J3 and pin axes <= 0.022 deg, arm residual
<= 0.016 deg), knee vs hub 3's link-2 half at 1 mm, E boss vs hubs / links - 0 poses removed for either config on any
bench. Fold margin over the taken poses: min 10.06 deg at the 10 deg rule, 5.49 at the 5 deg rule (the rule holds).

**Measured (Bench(110,360) exact unless noted; gap / near-touch gap (metal < 1 mm = contact) / poses < 1 mm / min metal):**

| protocol | fold margin | k4598 | H1 | gain plain / near-touch |
|---|---|---|---|---|
| polish: fit Bench(110,360) fast, worn exact | 10 | 29.95 / 36.11 / 13 / 0.39 mm | **26.45 / 26.45 / 0 / 1.38 mm** (reach 0.6472, follow 0.9636, ib14 0.9012, ib10 0.5126, contact 0.0117) | **3.50 / 9.66** |
| round-3 verifier: fit Bench(60,160) fast, worn exact | 10 | 30.35 / 38.41 / 16 / 0.02 mm | 28.21 / 33.77 / 9 / 0.09 mm | 2.14 / 4.64 |
| HELD-OUT, mine: fit Bench(110,360) fast, worn exact on all 202 fit-clip frames + 952 workspace poses outside BOTH Bench(110,360) and Bench(60,160) (1154 poses; Wave / Walking excluded, asserted) | 10 | 32.97 / 39.61 / 32 / 0.24 mm | 30.73 / 32.61 / 8 / 0.05 mm | 2.24 / 7.00 |
| polish protocol | 5 (current rule) | 29.34 / 33.64 / 10 / 0.21 mm | 24.48 / 25.59 / 2 / 0.21 mm | 4.86 / 8.05 |
| round-3 verifier protocol | 5 | 29.54 / 34.98 / 12 / 0.31 mm | 27.20 / 31.75 / 8 / 0.09 mm | 2.34 / 3.23 |

The margin-5 rows are a MEASUREMENT change (the user's 05:50 UTC ruling), not a design change; H1 was searched at 10.

**Hardware bounds.** Hubs O20 at J1-J3 (the "Keep O20 only" rule holds). Pin stack 5.68 mm -> 2.59 mm Ti plates on the
iglidur pin (between IGLIDUR-PIN 5.0 and the MR63ZZ pair 6.0; thicker plates only lift the knee, so the envelope is
real). ang_min 30.46 (knee window stays >= 30 deg off both singular postures). lE 59.55 mm (at the round-1 bound 60), lc
28.24 mm. Arm pad 82.5 mm from GH, 66.6 mm distal of J3's line foot and 27.1 mm across: on the upper-arm cuff. J1 seat
direction (scapula frame) anterior 0.085 / up 0.898 / lateral 0.432: acromion top, rule (4) holds (k4598 anterior 0.113).
J3 travel 181.7 deg (MR117 pair, full rotation), pin a 45.4 deg, pin b 41.3 deg.

**Red team.**
* *Overhead, the optimistic part of the gain.* At margin 10, H1 follows only 6 of the 10 Raise-overhead clip frames at
  elevation >= 140 (overhead follow 0.60; k4598 1.00) on the polish and fit-60 protocols, 12 of 19 on the held-out set
  (k4598 19 of 19); overhead workspace reach 0.21 / 0.18 / 0.15 (k4598 0.25 / 0.25 / 0.21). The cause is the knee window:
  H1's knee reaches 149.2-149.3 deg against its stop at 149.54 (30.7 deg from the straight singular posture; k4598 stays
  at <= 143.4, 36.6 deg off), so "knee window" losses rise 4 -> 11 (overhead 4 -> 8). The reach gain is everyday
  workspace poses (fold losses 133 -> 116). At margin 5 (polish protocol) the refitted shape keeps every overhead frame
  (follow 1.0, reach 0.25) - this edge is fragile, not robust. k4598's L1 build was the first to pass R4 overhead
  (83.9 %): **R4 must be re-judged on H1's build before H1 is called better at overhead.**
* *Near-touch is partly in-sample.* The "0 poses < 1 mm, min 1.38 mm" holds on the 470 poses the shape and the
  parameters were fitted on. On the held-out poses H1 has 8 poses < 1 mm (min 0.05 mm at plane 60 / elev 75 / axial 30;
  0.11 mm at 15 / 75 / 60) and 9 on the fit-60 protocol (min 0.09 mm in Raise overhead, elev 148). It is still far
  better than k4598 there (32 poses, 0.24 mm held out), so the near-touch gain stands (7.00 held out).
* *Arm at the side (elevation <= 15).* H1: 0 poses with metal < 1 mm on every bench (lowest 1.06 mm held out, 1.77 mm on
  Bench(110,360), at plane 105-150 / axial -135..-180); k4598: 3 (0.39 mm) and 9 held out. The round-3 near-touch point
  is fixed.
* *The knee near hub 3 (the pose that jams).* Knee link vs hub 3's link-2 half >= 41.8 mm (k4598 24.3), E boss vs link 2
  >= 38.4 mm (25.0): the longer E strap moves the knee away from hub 3. No flips (10 fps continuity) and no closure
  failures on any bench.
* *Posterior axillary fold.* Not re-measured on meshes (H1 has no L1 build yet). On the bench every sampled metal point
  is checked against the posed skin at every pose, and H1's lowest points are at mid / high elevations, not with the arm
  low and extended; J2's seat moves lower and further back (el2 56.3 -> 47.0, az2 17.7 -> 30.2), toward the fold, so
  the L1 red team must re-check link 2 there (k4598's built link 2 came to 1.74 mm).
* *Contact.* On the fit-60 protocol H1's contact fraction is 0.0259 (k4598 0.0091): 9 contact poses, 5 of them overhead
  clip frames - the same overhead edge.

**Verdict: CONFIRMED, not refuted.** The gain is real and >= 1 gap point, plain and near-touch, on every protocol and at
both fold margins (smallest: 2.14 plain on the fit-60 protocol, 3.23 near-touch at margin 5); it holds held out (2.24 /
7.00). H1 replaces k4598 as the design's polished configuration (row: best_k H-g107-1, v_gap 28.21 on the comparable
fit-60 protocol, v_polish_gap 26.45 = score 90.38 on the polish protocol). Before the generation-3 CAD switches to H1:
re-judge R4 overhead on the H1 build (the knee-window edge above), and red-team link 2 at the posterior axillary fold.

## L1 keep-out CAD of the polished H1 (generation-3 winner, 2026-10-16 ~07:55 UTC)

Design `pipeline/full-exo/designs/l1_skin-normal-3r-pin-knee-h1` (snapshot `pipeline/evolution/l1_skin-normal-3r-pin-knee-h1/`),
builder `pipeline/concept_l1/build_pinknee_l1.py --out l1_skin-normal-3r-pin-knee-h1 --fit-bench 110,360` (params = the rows
file's best_params = H-g107-1; per-joint hubs from rad1..rad3 = O20 x 3), red team `pipeline/concept_l1/redteam_pinknee_l1.py`.
Built and red-teamed on the farm (the Bench(110,360) fast grid, key 14f156cb6fc8, lives there), judged there (`tools/cloud_run.py
judge`), R7 locally.

**Shape = the verified one.** The builder gained `--fit-bench`: H1 was verified on the polish protocol (fit on Bench(110,360)
FAST, worn exact), so the build fits there, at the repository's fold margin 5 (the user's ruling): fit gap 24.57, reach
0.6694, follow 1.0, ib14 0.8934, contact 0.0085 - the verifier's `H1_fitbig_m5` fit_gap 24.57 to the digit. Faces 51.7 /
61.3 / 76.3 mm, knee level tr 84.72, knee centre m (-10.03, 2.00, 0).

**What changed in the builder (all inputs, nothing hard-coded to H1).**
* *Pin stacks at their real envelope.* The model's stk (5.68 mm = 2.59 boss + 0.5 GTM washer + 2.59 knee bar) leaves out
  the top of each pin: a second O4 x O8 x 0.5 thrust washer and the retainer on the integral O4 Ti pin (DIN 6799 RS 3.2
  e-clip O7.3 x 0.6 + 0.3 mm pin end). Both are now O8 x 0.9 keep-outs 0.5 mm over the knee bar (pin a's on member 3,
  pin b's on the arm pad): full stack 7.08 mm over tr. Outward of the knee bar, so no skin number moves.
* *The pad mount meets the knee's sweep - fixed.* The first H1 build (the k4598 builder unchanged) held EVERY clip frame:
  the pad mount (pad -> nearest end of the user's BOTTOM bar, at 130 deg from the arm axis) lies inside the swept area of
  the E boss / E strap (90-165 deg around pin b, r 22-58 mm) - 1.18 mm interpenetration at every pose (workspace 0.0 %).
  H1's longer E strap and its knee orientation put pin a's arc exactly where k4598's mount ran. The builder now sweeps
  member 3 and the knee bar through the arm frame over every clip frame + workspace pose that closes (1161 poses, 4.2 M
  points), (a) cuts the user's BOTTOM square to the arm where it would meet that sweep (BOTTOM may be cut: 3.7 mm distal of
  pin b; its proximal 22 mm and the 2 x M3 tongue holes go - the knee bar's far end swept to 0.09 mm of them), (b) routes
  the mount as the shortest straight tp slab at the pad level clear of the sweep by >= 1 mm, with a riser into the bar
  (one solid): 62 deg from the arm axis, 23.4 mm, riser to tr + 4.41. k4598 at margin 5 through the same code: no cut
  needed (BOTTOM 8.8 mm from its sweep), mount at 42 deg.

**Built vs the model's metal (7 poses of the fit bench: arm at the side (-90 / 0 / 75), first, middle, the two highest
(45 / 165 / -75, 60 / 165 / -75; knee 142.1 / 143.3 deg), behind the back (-90 / 30 / 75), across the body (150 / 60 / -60)).**
Every rigid sample of the model (hubs, E strap, E boss, arm pad, knee bar) lies on the posed exo.glb within 0.0001 mm;
the straps' samples outside the hub zones 0.000 mm; inside the hub zones (r < R + 3) the built strap sits up to 1.85 mm
(link 1, 12 of 40 samples) / 1.26 mm (link 2, 15 of 139) ABOVE the model's sample - the stated R6 lift to the hub's member
level, away from the skin (not within 0.5 mm there, by design). Built-part frames vs the model's member transforms
<= 1e-4 mm on the judges' path (scene_export.frame_xforms); the J2 line check 0.0001 deg.

**Clips (30 fps, the champion's 8 incl. the held-out Wave / Walking).** 1323 / 1337 followed (98.95 %): every frame of
Raise overhead (knee 101 -> 144 deg: 5.4 deg inside its 149.54 stop at margin 5 - the margin-10 overhead edge does not
bite), Drink, Comb hair, high shelf, Wash, back pocket, Walking; Wave holds 14 (the model's part clearance). Lowest metal over
the followed frames 1.66 mm (k4598's L1: 0.60). Workspace (1432): chain + knee close 68.8 %, + parts 66.0 %. 15 parts,
77.2 g, each one closed single solid.

**Outside judges (farm; R7 local): 8 of 19 pass.** R1 80.1 % / R1-aim 42.3 % FAIL, R2 24.87 mm (the user's forearm cuff in
the rig's self-intersection; ours 0.0) FAIL, R3 98.7 % PASS, **R4 overhead 74.2 % FAIL**, R5 / R5-aim 3 PASS, R6 0.0 mm at
every frame PASS (BOTTOM cut included), R7 PASS, R8 77.2 g PASS, R11 0.35 kPa PASS, R16 67.9 % FAIL, R17 PASS. Not run: R9
(no STEP at L1), R10. (R7's judge skips every H-group part, so the arm pad, pad mount and pin b retainer are checked only
by the builder: closed, one piece.)

**Before / after, design vs measurement (the control).** k4598's L1 (9 of 19) was built at fold margin 10 with the old
mount. Same builder, margin 5, k4598 on its own verified protocol (fit-60) = design `l1_skin-normal-3r-pin-knee-k4598-m5`
(R1, R4, R3, R6 step 3, R16 judged; dynamics / body contact not run): R1 81.1 %, R1-aim 43.2 %, R3 99.6 %, R4 79.6 % FAIL,
R6 0.0, R16 66.5 %. So:

| built, margin 5, same builder | k4598 | H1 (polished) | design change |
|---|---|---|---|
| R1 2-14 mm / R1-aim 2-10 mm | 81.1 % / 43.2 % | 80.1 % / 42.3 % | -1.0 / -0.9 |
| R4 Raise overhead (14 mm band); its median skin gap | 79.6 %; 11.1 mm | 74.2 %; 12.1 mm | **-5.4** |
| R3 follows | 99.6 % (Wave holds 6) | 98.7 % (Wave holds 14) | -0.9 |
| R16 workspace | 66.5 % | 67.9 % | +1.4 |
| lowest metal over the followed frames | 0.60 mm | 1.66 mm | +1.06 |
| hub 3 face / knee level tr | 74.0 / 78.8 mm | 76.3 / 84.7 mm | +2.3 / +5.9 |

Measurement change (k4598 at margin 10, old mount -> margin 5, new builder): R1 84.2 -> 81.1, R4 83.9 -> 79.6, R16 62.3 ->
66.5 - the margin-5 refit lifts hub 3 by 2 mm and the newly followed frames sit wider. **The polish's verified bench gain
(2.3-4.9 gap points) does not reach the built proximity judges**: it bought reach (fold losses 115 -> 97) and removed
every near-touch pose by moving metal OUT (knee +5.9 mm), which the skin-coverage R1 / R4 pay for; R4 overhead fails by
5.8 points. H1 is still the verified bench winner and the safer build (no metal < 1.66 mm), but it is not the better
built design on R1 / R4. Next lever: the polish objective needs the judge's own coverage term (skin 2-14 / 2-10 mm from
metal, overhead weighted) or a cap on tr, not near-touch alone (polish 2, task 26).

**Red team (built meshes posed by clips.json, exact posed skin; redteam.json).**
* *The point that pinches:* none below 1 mm on any followed frame (k4598: 3.8-4.3 % of frames). Lowest: J1 lower plate
  1.66 mm (Raise overhead frame 78, 30 / 150 / -60, trunk), the pad mount 1.77 mm and link 2 1.80 mm (Reach back pocket
  frame 72, -80 / 39 / 101); < 2 mm in <= 3.8 % of frames per part.
* *Posterior axillary fold* (409 trunk vertices): link 2 nearest, 2.63 mm (Comb hair frame 105, 78 / 143 / -67; k4598's
  built link 2: 1.74 mm), E strap 4.29, hub 3's plate 4.79, the knee parts >= 22 mm. J2's lower / further-back seat did not
  bring link 2 closer to the fold.
* *The knee near hub 3 (the pose that jams):* knee bar vs hub 3's link-2 half >= 41.7 mm, vs link 2 >= 47.8 mm (k4598
  24.3 / 32.5); knee bar vs E strap / E boss / arm pad / pad mount / both retainers = the 0.5 mm designed running gap at
  every frame; E strap vs J3 upper boss 0.13 mm (the 0.15 face gap at hub 3's rim, sampled); BOTTOM (cut) vs knee bar
  >= 2.39 mm, vs E boss 3.93, vs pin a retainer 4.78. The only jam: Wave, 14 frames on the model's part clearance.
* *Arm at the side (the round-3 near-touch):* 104 of 126 neighbourhood poses (plane -30..90, elev 0-10, axial -60..90)
  close with the parts clear; at internal rotation (axial -60, plane -15 / -30) hub 3's plate / link 2 go 0.2-7.5 mm INTO
  the trunk (3 poses: not taken - skin - as on the bench); of the skin-clear ones one is < 1 mm (link 2 0.37 mm at
  -15 / 10 / -60), the rest >= 2.35 mm (E strap). The verifier's 0.02 mm point does not reproduce on H1.
* *The optimistic number:* the bench's 26.45 / 24.48 is a gap, not R1; built, H1's coverage is 1 point below k4598's.

## Verification (rebase to margin 5 / O20) (independent verifier, 2026-10-16 ~08:10 UTC)

Claim checked: the rebase track's "H1 (H-g107-1, O20 x3) 28.21 (margin 10) -> 27.20 (margin 5)" on the round-3 protocol
(fit Bench(60,160) FAST at the same margin, shape frozen, worn on Bench(110,360) EXACT), complexity 19.5, 0 passive
translations. Harness: `docs/research/rebase/verify_rebase_pinknee.py` (runs `docs/concepts/verify/skin-normal-3r-pin-knee.py`
unchanged and adds the checks below), plus `docs/concepts/verify/skin-normal-3r-pin-knee-continuity.py` (kin + taken).
Run on this box (nice, one process at a time), CB_EXACT=1, CB_FOLD_MARGIN=5, O20 only (the model refuses slim hubs).

**Verdict: CONFIRMED (not refuted).** The gap reproduces exactly, no rule is broken, and the complexity is not understated.

| | claim | re-measured |
|---|---|---|
| gap (Bench(110,360) exact, frozen) | 27.20 | **27.20** (fit 23.64 fast), score 90.11 |
| reach / follow / in-band14 / in-band10 / contact | 0.6583 / 0.9636 / 0.8953 / 0.5539 / 0.0256 | identical |
| near-touch gap (metal < 1 mm = contact) | 31.75 | 31.75 (8 poses < 1 mm, min metal 0.09 mm, clip frame 30 / 148 / -60) |
| overhead (elev >= 140) | - | ws reach 0.179 (5 / 28), clip follow 0.60, in-band14 0.916; not taken: fold 15, knee window 7, contact 5 |
| same harness at margin 10 (CB_FOLD_MARGIN=10) | 28.21 | **28.21** (near-touch 33.77): margin 10 -> 5 = -1.01, a measurement change |
| raglan-knee-3r (own verifier, `big`, margin 5) | 27.82 | **27.82** (dilution-corrected 28.56, near-touch 32.34) |

Checks the round-3 harness does not make:
1. **DOF / determinacy (screw rank, all 343 taken poses).** Loop scapula-J1-J2-J3-pin a-knee-pin b-arm-GH(3R): mobility
   3 and chain rank 5 at every pose (smallest chain singular value 0.064 of the largest, p5 0.081), 6th singular value of
   all 8 screws <= 1.6e-9: one redundant constraint (J1, J2 through GH - c1 = c2 = 0 - and pins parallel to J3). No
   undetermined passive coordinate.
2. **Sensing claim (null-space Jacobian).** The 3 hub rates fix the loop motion at every taken pose (sigma_min of the hub
   rows of the orthonormal null space >= 0.39, condition <= 2.3): with GH known the knee pins need no encoder. The record
   keeps 2 sensed pins because SIMPLICITY.md requires sensing to hold when GH translates (R10); the pins carry that in-plane
   drift. So 19.5 is the rule's count, not an understatement (9.5 if the user accepts hub-only sensing / a cuff IMU).
3. **Components at their envelope.** Hubs O20 (r 10) x 12.25 (F -> crown, upper member at F + 3.15) at J1-J3; knee pins:
   stack 5.68 = 2 x 2.59 mm Ti plates + 0.5 washer on an O4 integral pin in O12 bosses, knee bar (lc + 12) x 10. Caveat
   (found by the L1 CAD build, confirmed here from the model): the model's stack leaves out the top thrust washer +
   e-clip (+1.4 mm, outward of the knee bar) - no skin number moves; part-part over it is the built CAD's R16 job.
   J1 seat u1 = (ant 0.085, up 0.898, lat 0.432): acromion top, ruling 4 holds (anterior <= 0.20).
4. **Honest pose-taking.** 470 poses = 343 taken + 127 with a reason (fold 97, knee window 14, parts 7, contact 9); 0
   silent drops; the verifier's extra checks remove 0. Fold margin used >= 5.49 deg (0 poses under 5, 5 between 5 and
   10 - the newly admitted ones); knee angle >= 2.24 deg inside [30.46, 149.54]; radial drift 0.0 mm (R_tol 0.5);
   closure residual <= 0.015 deg; independent 3D closure <= 0.022 deg / 0.000 mm; J3 travel 181.5 deg (MR117 pair, full
   rotation), pin a 44.3, pin b 40.6 deg.
5. **Continuity (CLAUDE.md "reach must be reachable by moving").** Full 1432-pose workspace grid, 2-deg slerp edges, no
   joint jump > 10 deg, one knee branch sign: kinematic nodes 971 / 971 connected, taken nodes 913 / 913 connected (742
   edges, 0 refused), 0 islands; on the Bench(110,360) workspace 237 / 237 taken poses connected: connected reach =
   static reach = 0.6583. Out of sample (all 1432 grid poses) the taken reach is 0.638, 0.02 below the bench's.
6. **Complexity** (`tools/simplicity.py`, record checked against the model's members 1, 2, 3, 6, 5 and joints J1-J3,
   pin a, pin b): 2 passive rotations 2 + 2 sensed pins 10 + 2 bodies 2 + 2 joints 2 + 4 made parts 2 + 6 bought 1.5 =
   **19.5**. The iglidur pins are revolutes, not sliding pairs (SIMPLICITY.md); nothing is undercounted.

What it means: under the user's rulings the pin knee stays the verified leader at 27.20 (score 90.1), 13.45 points
short of 95 at complexity 19.5. Reach (0.658, overhead 0.18) is still the whole deficit, as the rebase track says.

## Verification (P5, margin 5) (independent verifier, 2026-10-16 ~08:22 UTC)

Claim checked: the rebase track's margin-5 re-polish candidate **P5 = HWm5-g23-5** (row field `rebase_polish_m5`,
self-measured polish protocol exact 21.79 / near-touch 22.34, held-out 24.87) beats the polished H1 (H-g107-1) by
>= 1 gap point. Harness: `docs/concepts/verify/skin-normal-3r-pin-knee-polish.py` (it imports the round-3 verifier
unchanged; no code of the search drives these numbers), CB_EXACT=1 on every wear bench, CB_FOLD_MARGIN=5, O20 only,
P5 and H1 in the SAME farm batch (exo-cpu1, 8 jobs, ~$0.08 shared). Continuity: a new flood fill,
`docs/concepts/verify/skin-normal-3r-pin-knee-continuity.py`. Raw outputs: `docs/research/verify_p5/`.

**Protocol note (measurement, not design).** The farm jobs had no link to the Bench(110,360) fast cache (14f156cb6fc8;
`tools/cloud_run.py` links only the local `.cache/concept_bench`), so the polish and held-out protocols fitted the shape
on Bench(110,360) EXACT instead of fast - for P5 and H1 alike. Effect on the polish protocol: P5 21.92 (self-measured
with the fast fit 21.79), H1 25.03 (24.48). The round-3 protocol (fit Bench(60,160) fast) ran with the fast fit, and
the local re-run reproduces it to the digit. H1 at margin 10 in the same batch: fit-60 28.21 / near-touch 33.77, the
verified numbers to the digit.

**Measured (fold margin 5; gap / near-touch gap (metal < 1 mm = contact) / poses < 1 mm / min metal):**

| protocol | H1 | P5 | gain plain / near-touch |
|---|---|---|---|
| polish: fit Bench(110,360) (exact), worn exact, 470 poses = the search's own poses | 25.03 / 26.14 / 2 / 0.20 mm (score 90.90) | **21.92 / 22.47 / 1 / 0.91 mm** (score 92.03; reach 0.7139, follow 1.0, ib14 0.8856, ib10 0.4963, contact 0.0187) | 3.11 / 3.67 |
| round-3 verifier: fit Bench(60,160) fast, worn exact | 27.20 / 31.75 / 8 / 0.09 mm | 24.88 / 31.95 / 11 / 0.06 mm (follow **0.9455**) | 2.32 / **-0.20** |
| HELD-OUT: fit Bench(110,360) (exact), worn exact on all 202 fit-clip frames + 952 workspace poses outside Bench(110,360) and Bench(60,160) (1154 poses; Wave / Walking excluded, asserted) | 29.12 / 31.85 / 12 / 0.04 mm (score 89.41) | 28.96 / 31.40 / 11 / 0.07 mm (score 89.47) | **0.16 / 0.45** |

The rebase track's "held-out 24.87" used `tools/knee_polish.py`'s own 470-pose disjoint bench and had no H1 number
beside it at margin 5; on the larger disjoint set, against H1, the gain is gone.

**Rules - all hold, nothing loosened.** Independent 3D closure on every taken pose (hub-3 centre / pins 0.000 mm, J3 and
pin axes <= 0.022 deg), knee vs hub 3's upper half, E boss vs hubs / links: 0 poses removed for P5 or H1 on any bench.
Fold margin over the taken poses >= 5.03 deg (P5, held out) at the 5 deg rule. O20 at J1-J3. Pin stack 5.54 mm ->
2.52 mm Ti plates on the iglidur pin (between IGLIDUR-PIN 5.0 and the MR63ZZ pair 6.0: a real envelope). Knee link lc
23.7 mm (>= two O12 bosses + 2), lE 59.6 mm. J1 seat anterior 0.089 / up 0.891 / lateral 0.444: acromion top, rule (4)
holds. J3 travel 177-195 deg (MR117 pair, full rotation), pins 54-63 deg. Arm at the side (elevation <= 15): 0 poses
< 1 mm on every bench (lowest 2.09 mm on the round-3 protocol). **Continuity** (full 1432-pose workspace grid, shape frozen, 2-deg slerp edges
from elevation 0, no joint of q1, q2, q3', pin a, pin b moving > 10 deg per step, knee branch sign constant): P5 1014
kinematically closed poses, all 1014 connected (0 islands; 843 of 844 edges pass, 1 refused at the fold window), one
knee branch; on Bench(110,360) connected reach = static reach. H1: 985 closed, 984 connected (1 island, not on the
bench), one knee branch. Neither design has a static-only island on the bench.

**Red team.**
* *Where the gain comes from, and why it does not travel.* P5 trades knee window for reach: ang_min 30.5 -> 35.9 but
  the knee runs 80-141 deg (H1 101-148), farther from the straight singular posture (sing. distance 39 vs 32 deg),
  and phib -55 -> -72 / lc 28.2 -> 23.7 move the knee. On the 470 search poses reach rises 0.669 -> 0.714 and overhead
  workspace reach 0.25 -> 0.32. Held out, reach is 0.657 vs 0.633 (+0.02) but in-band 14 drops 0.888 -> 0.884 and
  contact rises 0.012 -> 0.031 (26 contact poses vs 10): the extra reach lands metal on skin it was not fitted to.
* *Near-touch on the round-3 protocol is worse.* With the shape fitted on Bench(60,160), P5 has 11 poses with metal
  < 1 mm (min 0.06 mm) vs H1's 8 (0.09 mm), and follows 0.9455 of the clip frames (below the bench's 95 % follow
  target; H1 0.9636).
* *The knee stop is still the edge.* H1's knee reaches 149.5 deg against its 149.54 stop held out (0.04 deg); P5's
  reaches 142.8 against 144.07 (1.3 deg) - better, but both optima sit on the knee stop, so the stop (ang_min) is
  a live design variable, not a safety margin; whoever builds either must red-team the feel at that stop.
* *Overhead clip follow* (Raise overhead, elevation >= 140) is 1.0 for both at margin 5 on the polish and held-out
  protocols and 0.6 for both on the round-3 protocol (fit-60 shape) - no difference between them.

**Verdict: REFUTED.** P5's gain over H1 is >= 1 point only on the 470 poses it was searched on (3.11 plain / 3.67
near-touch); held out it is 0.16 / 0.45 and on the round-3 protocol the near-touch gain is -0.20. No rule is broken,
but the CLAUDE.md bar (a verified gain >= 1 gap point) is not met out of sample. **H1 stays** the polished configuration
(row: best_k H-g107-1 unchanged; `v_p5_*` fields hold these numbers) and the H1 CAD in progress stands. For polish 2:
search on a held-out-aware objective (e.g. the near-touch gap averaged over the polish bench AND a disjoint pose set,
or the fit-60 frozen protocol) - the 470-pose objective is now saturated and over-fitted, and the remaining slack is
the knee stop and the contact on unseen poses, not reach on the search bench.

## Full user-style CAD of the polished H1 (generation-3 winner, 2026-10-16 ~09:40 UTC)

Design `pipeline/full-exo/designs/user_pinknee_h1`. Builder `pipeline/conformal/param_cad/user_style_pinknee.py`; the parameter
dict and the per-joint hubs are inputs, nothing is hard-coded to H1:

    PK_EAR_DZ="" OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/conformal/param_cad/user_style_pinknee.py \
        --out user_pinknee_h1 --l1 l1_skin-normal-3r-pin-knee-h1 --shape .cache/pk_shapes/h1_b110_360_m5.pkl

**The verified shape, no refit.** H1 was verified on a shape fitted on Bench(110,360) FAST. That bench's fast grid cache
(key 14f156cb6fc8) exists only on the farm, and the farm has no OCC. So the farm fits the model and pickles the attributes
the verifiers hand over in their frozen-shape protocol, plus the fit's link rows. The command is
`pipeline/concept_l1/pinknee_shape.py --fit-bench 110,360`. The pickled fit gives gap 24.57, f [51.7, 61.308, 76.296],
tr 84.721 and m [-10.026, 1.995, 0.0], identical to the L1 to the digit. The CAD builder wears that shape on this box's
Bench(60,160) without refitting. The farm cost was $0.002 of job time. The wait in the farm's queue was 21 min, because
the queue held 15-31 jobs from other agents. A local build of the cache was measured at 22 s per pose, about 3 h for the
470 poses, so it was stopped.

**Parts.** All are at real size, and every custom part is one valid closed solid. Each is made only from sketches of
lines and tangent arcs, extruded, revolved, or swept with one section along a line/arc path, plus rounds. There are no lofts.

| part | how it is made | mass |
|---|---|---|
| J1, J2, J3 hubs | the v5 O20 stack from `user_style.py`: 2x MR117-2RS back to back, 17-4PH outer spacer, ground inner spacer, M7x0.5 Ti ring nut, threaded G2 dome cap, integral O7 Ti pins. J3 sits on its offset tilted line. | 2.0 g cap + 2.6 g bearings per hub |
| D8-01 scapula base | the J1 upper member: O20 ring, seat disc and M18x0.5 spigot. It has **no ears and no tab**. See "Base" below. | 6.5 g Ti-6Al-4V |
| D8-02 link 1 | 8 x 3 bar on a 3-arc line/arc chain (R -13 / -19 / 5), with the J1 and J2 pads (14 mm seats) and integral O7 pins. It is **5-axis machined from solid**: J2's face sits 9.6 mm above J1's, so the bar must climb 59.6 deg. No chain with every bend >= 15 mm inner radius stays above the L1 strap. | 14.0 g |
| D8-03 link 2 | a **bent 3 mm Ti-6Al-4V bar**: 4 arcs (R 45 / -17 / -17 / 25), every bend >= 15.5 mm inner radius, max climb 40.1 deg. It carries the J2 / J3 upper rings and the user-style pocket, and flies over the knee and the pad. | 19.8 g |
| D8-04 member 3 | the J3 disc plus integral O7 pin. The E strap is one side-view sketch: its underside is the upper hull of the model's fitted E profile (76.3 -> 84.7 mm), and its top steps to the boss. The E boss is O12 x 2.59, with pin a as an integral O4 Ti pin. | 11.8 g |
| D8-05 knee link | flat Ti plate 40.2 x 10 x 2.59 with R1 corners, O5.5 sleeve bores and O8 x 0.7 clip counterbores | 3.9 g |
| pins a, b | iglidur G sleeve igus GSM-0405-03 (4 x 5.5 x 3), faced to 1.89 mm. An iglidur thrust washer 4 x 8 x 0.5 sits in the 0.5 mm running gap (GTM-0408-005 class; **confirm the size**, else cut it from iglidur sheet). A DIN 6799-3.2 E-clip (A2, polished) sits in the counterbore, flush with the plate. Stack 5.68 mm, nothing above the knee plate. | 0.2 g each |
| D8-06 BOTTOM + arm pad + pad mount | one 5-axis 7075-T6 part. The user's BOTTOM is cut as the L1 cut it: square to the arm, 3.68 mm distal of pin b, removing 1807 mm3. The O12 arm pad has an integral O4 h9 pin b (hard-anodised). The pad mount is one line/arc planform on the L1's sweep-clear route (62 deg, 23.4 mm). Its last 6 mm are a riser 1 mm into BOTTOM's underside, fused into one solid. | 66.2 g |
| upper-arm cuff | one U sketch (flat 70 mm, R50 side arcs, 2 mm AlSi10Mg shell), extruded along BOTTOM. Both side arcs are trimmed to 10 deg, clear of the trunk over 451 clip poses; the limiting poses are across the body (plane 122-145, elevation 31-48). The cuff has 6x M4x6 ISO 10642 screws. | 36.7 g |

Custom mass is 112.7 g plus 66.2 g for BOTTOM + mount. The rest of the user's arm parts are unchanged.

**Base at the J1 ring (user ruling 2026-10-16), measured.** The first design put two short ears, each with one M4, on the
J1 ring, with headings chosen against the posed link 1 over every clip and workspace frame and against the
scapula-frame skin envelope. That cannot work for H1, because link 1 sweeps the ear zone:
- **Ears at the seat level:** 9 of 180 headings clear link 1 by >= 1 mm, but none of those clears the skin envelope. The
  best is 5.2 mm inside it.
- **Ears raised 1.3 mm:** 35 headings clear link 1 and 14 also clear the skin, but all 14 lie within 304-310 deg, so there
  is no pair 90-180 deg apart.

So the base is the J1 upper member alone. The handler's bracket threads onto the M18x0.5 spigot in place of the dome
cap, which retains the upper outer ring. Coming down axially over the crown is the one direction link 1 never occupies.
The posed link 1 stays 0.15 mm from the built base, which is the stack's designed running gap at the seat. The
anti-rotation feature of the bracket belongs to the handler, which is the user's part.

**Fixes found on the way, now in the builder:**
- The knee link's name mentions its clip counterbores, so the export classed it as hardware: no STEP, stainless density,
  and left out of the kinematic check. The iglidur sleeves were classed as bearing steel.
- Link 2's mesh was not closed in the judges' units. A T-junction crack in OCC's tessellation left 71 open edges in one
  8 x 6 mm patch. The builder now retries other tessellation tolerances.
- `pipeline/conformal/param_cad/fixup_pinknee_export.py` applied both fixes to this build in place. The geometry of every
  other part is the same file.
- A bar is now fitted with 3 or 4 arcs only. A 5-arc fit costs 3125 radius snaps, 10+ min each on this box.


**Kinematics = the verified model's.** I checked 11 poses, all followed:
- seven bench poses: arm at the side, first, middle, the highest (45 / 165 / -90), the second highest, behind the back
  (-90 / 30 / 105) and across the body (150 / 45 / -60);
- four real clip frames from the L1's `clips.json`: Raise overhead frame 78 at (30, 150, -60), above elevation 120;
  Walking with the arm at the side; the top of Comb hair; and Reach back pocket.

Results at every one of the 11 poses:
- **Member frames:** the judges' path (`scene_export.frame_xforms` on the L1's frames) and the model's own member
  transforms agree within **1e-4 mm**.
- **Rigid joint features** (hub 1-3 surfaces, E boss, arm pad): the model's metal samples lie within **0.144 mm** of the
  posed built parts. The 0.144 mm is the cap domes and the rounds.
- **E strap:** within 0.12 mm.
- **Knee link:** within 1.75 mm. These samples sit at the pin centres, inside the O5.5 / O8 bores that the pins (other
  members' parts) fill; the model's knee is a solid box.
- **Link straps:** the bars sit up to **4.13 mm (link 1) and 10.90 mm (link 2) above** the model's straps. This is a
  shape change, not a kinematic one. Link 2's 15 mm bends cannot follow the L1's steep hub-zone transition at J3. A
  machined link 2 (R >= 4) would hug the strap and is the next lever on R1 if the judges ask for it.


**Judged** (the fast scorecard, `pipeline/full-exo/designs/user_pinknee_h1/judge/scorecard.md`): **8 of 19 pass**, the
same count as its L1. Where the numbers come from:
- **Farm judge** (fast, $0.10): R1, R2, R4, R11 and R17.
- **This box, after the pin-a sleeve fix:** R6, R7 and R16.
- **R1 / R4 were measured before the sleeve fix.** That sleeve is a 0.16 g part that moved 10 mm within the knee link's
  footprint, so I did not re-run them.

The full CAD against its own L1, line by line:

| req | L1 `l1_skin-normal-3r-pin-knee-h1` | full CAD `user_pinknee_h1` | change |
|---|---|---|---|
| R1 (2-14 mm) | 80.1 % | **71.6 %** | **-8.5, lost** |
| R1-aim (2-10 mm) | 42.3 % | **33.1 %** | **-9.2, lost** |
| R2 | 24.87 mm (user's forearm cuff) | 24.87 mm (user's forearm cuff) | same; see note 1 |
| R3 | 98.7 % | 98.7 % | same |
| R4 overhead | 74.2 % | 69.0 % | -5.2 |
| R5 / R5-aim | 3 / 3 | 3 / 3 | same |
| R6 | 0.0 mm (full, every frame) | **0.0 mm** (fast, every 3rd frame; 451 frames x 2586 pairs) | kept (was 1.43 before the sleeve fix) |
| R7 | PASS (the L1 judge skips the H parts) | **PASS**: 28 STEP files, all valid single solids, 0 bad faces, the arm-side part and the knee link included | kept |
| R8 | 77.2 g | 178.9 g (112.7 custom + 66.2 BOTTOM / mount) | real parts; PASS |
| R11 | 0.349 kPa | 0.303 kPa | PASS |
| R16 | 67.9 % (full: step 4, 360 poses) | **61.7 %** (fast: step 12, 120 poses) | **same as the L1 at the same step: 61.7 %**; see note 2 |
| R17 | PASS | PASS | see note 3 |

Notes:
1. **R2.** "Ours" now shows 4.71 mm beyond the rig's self-intersection, but that is BOTTOM's own distal bar inside its
   own limb (Comb hair). The L1 counted the same bar as the user's, at 4.96 mm; fusing BOTTOM with our mount moved it to
   "ours". Our new parts add 0 mm: the trimmed cuff, the base and the mount are all 0.0 attributable.
2. **R16.** The L1 re-judged at step 12 on a scratch copy gives 61.7 %. Its part interference is 1.7 % against the CAD's
   0.8 %, and body contact is 4.2 % for both. The 67.9 % on the L1's card is the full-mode sample, a measurement
   difference.
3. **R17.** It passes even with link 2's open mesh, which the judge takes as its convex hull (139 g instead of 19.8 g).

**The full CAD loses R1 and R4 against its L1. These are design changes:**
- **The bars ride above the evaluator's straps.** Link 1 is on average 3.3 mm and at most 6.2 mm above the L1 strap.
  Link 2 is on average 2.6 mm and at most 9.4 mm above it, and up to 10.9 mm above the model's strap at J3.
- **The cuff side arcs are trimmed to 10 deg** clear of the trunk (the L1 carried the user's original cuff). H metal
  within 110 mm of GH counts in R1.

**Next levers, in order:**
1. Link 2 machined to hug the strap. The builder switch is ready (`PK_LINK2_MACHINED=1 ... --out user_pinknee_h1_m2`).
   The ruling allows it when stated on the part.
2. A cuff-trim rule over the FOLLOWED clip frames only (it now trims on every third clip frame).
3. Close link 2's tessellation crack: find the face pair in the glued bar.

Stills on the muscled mannequin and the independent verification are the next steps (task #19).

## Polish 2 (margin 5, near-touch) (2026-10-16 08:25-10:45 UTC, self-measured - not an independent verification)

**What ran.** The FINAL POLISH again under the night rules: fold rule 5 deg, O20 at J1-J3 only, near-touch objective,
the J2 fold stops as design variables, every overhead clip frame kept. Tool: `tools/knee_polish2.py` (drives
`tools/knee_polish.py` unchanged: the round-3 verifier's extra checks knock poses out, the model's audit counts metal
< 1 mm as contact). Free: the 13 continuous parameters of the H1 polish (az1 / el1 / az2 / el2, wd / wa, b3, lE 20-90,
lc, phiE, phib, ang_min 20-45, stk 4.5-6.0) + **m_lo / m_hi**, hard J2 stops at the two fold-window edges, 5-20 deg
(they can only narrow the window; 5 = the user's floor). Hubs fixed O20 x 3.

**Objective (new: KP2_VAL=1), and why.** The P5 verification measured the over-fit of the 470-pose objective (gain 3.11
on the search poses, 0.16 held out). So the objective adds a validation term: the shape fitted on Bench(110,360) (fast)
is worn FROZEN on Bench(60,160) (fast cache 0089c747c10f; 164 of its 220 poses are not in Bench(110,360)), and
obj = 0.5 x (near-touch gap on Bench(110,360) + frozen near-touch gap on Bench(60,160)) + 2 per overhead clip frame
(elevation >= 140) not followed. The verifier's held-out set is every pose OUTSIDE both benches, so it stays held out:
no held-out number entered the search or the choice of the claim (the claim is the best objective, fixed before the
held-out runs came back).

**Streams (Bench(110,360) fast, popsize 16 unless noted, farm exo-cpu1, <= 8 slots, ~$2.2 in all):**

| stream | start | sigma | evals | x0 obj -> best obj | best: near-touch Bench(110,360) / frozen on Bench(60,160) / stops m_lo, m_hi |
|---|---|---|---|---|---|
| P5 | P5 = HWm5-g23-5 (first) | 0.5 | 1105 | 22.44 -> 21.56 (P5-g64-11) | 23.26 / 19.86 / 5.06, 5.07 |
| H1 | H1 = H-g107-1 | 0.5 | 1121 | 25.35 -> **20.62 (H1-g69-4 = C1)** | 24.20 / 17.04 / 5.40, 5.12 |
| HW | HW-g58-11 | 0.5 | 721 | 23.91 -> 21.48 (HW-g45-8) | 25.25 / 17.70 / 6.33, 5.09 |
| HLx | HL's best (= H1: HL never beat its x0 in 689 evals) with lE 75 | 0.6 | 721 | 345 -> 23.25 (lE 80.5) | 25.28 / 21.21 / 6.07, 5.11 |
| K4598 | k4598 | 0.6 | 1329 | 32.23 -> 24.52 | 28.41 / 20.62 / 5.68, 5.55 |
| R2 | R2-g130-11 (polish-big basin) | 0.5 | 657 | 24.22 -> 24.20 | 26.08 / 22.32 / 6.52, 5.07 |
| rnd1 | best of 32 uniform-random configs (scan best 121.2) | 0.8 | 497 | 121.2 -> 34.36 | 37.72 / 31.00 (killed by the endpoint's 1 h limit; rows kept) |
| rnd2 | best of 16 x (P5 + 2 sigma noise) (scan best 59.3) | 0.7 | 369 | 59.3 -> 27.37 | 28.70 / 26.04 |
| H1b (wave 2) | C1, IPOP restart, popsize 32 | 0.4 | 801 | 20.62 -> 20.62 (no gain: C1 stays) | 24.20 / 17.04 / 5.40, 5.12 |
| HW resumed (wave 2) | HW stream state | - | 1489 in all | -> 20.81 (HW-g91-1) | 24.33 / 17.29 / 6.46, 5.13 |
| G (wave 2) | G-g133-10 (short-E basin, lE 21) | 0.6 | 849 | 26.80 -> 24.91 | 27.09 / 22.73 / 6.97, 6.21 |
| W1 (wave 2) | W1-g105-14 (the other knee branch) | 0.6 | 769 | 29.96 -> 26.31 | 28.95 / 23.68 / 6.18, 5.28 |
| rnd3 (wave 2) | best of 16 x (H1 + 2 sigma noise) (scan best 60.5) | 0.7 | 465 | 60.5 -> 34.67 | 39.59 / 29.75 |
| rnd4 (wave 2) | best of 32 uniform-random configs | 0.8 | - | killed by the endpoint's 1 h limit (queue + scan + budget); rows not retrieved | |

An earlier attempt of this track (07:30-08:20 UTC, objective near-touch + overhead only, no validation term; 8 streams,
10 360 evals) is logged too as `polish2-m5-r1*`: best r1P5-g72-6 near-touch 21.93 (r1Q5 22.27, r1R2m5 22.34, r1H1
25.31, r1W1 26.44, r1k4598 27.75). All 20 532 rows: docs/concepts/sweeps/skin-normal-3r-pin-knee.json, stages
`polish2-m5-<stream>` (with near-touch, plain, validation, overhead follow / knee edge, stops, fold margins taken).
**Gate (docs/METHOD.md) on the validation-objective history (10 172 evals, generation order): gain 0.00 score points
over the second half, 0.00 over the last third, top-5 within 0.08 - passed** (wave 1 alone: 0.29 / 0.29 / 0.11). The
IPOP restart from C1 (popsize 32, 801 evals) found nothing better; random restarts end 6.7-14 points behind; the G and
W1 basins stay 4-6 behind: the H1 / P5 / HW basin is the only competitive one in 20 532 evals at margin 5.

**Claim (fold rule 5 + C1's stops, O20; shape fitted on Bench(110,360) FAST, worn EXACT; `knee_polish2.py claim`,
which runs the polish verifier harness `docs/concepts/verify/skin-normal-3r-pin-knee-polish.py` imported unchanged;
H1 in the same protocol; gap / near-touch gap (metal < 1 mm = contact) / poses < 1 mm / min metal):**

| protocol | H1 (H-g107-1) | C1 (H1-g69-4) | gain plain / near-touch |
|---|---|---|---|
| polish: Bench(110,360), 470 poses (search poses) | 24.48 / 25.59 / 2 / 0.21 mm (score 91.10); reach 0.6694, follow 1.0, ib14 0.8943, contact 0.0085 | **23.04 / 24.15 / 2 / 0.04 mm (score 91.62)**; reach 0.6889, follow 1.0, ib14 0.8972, ib10 0.5591, contact 0.0165 | 1.44 / 1.44 |
| HELD-OUT: the verifier's set (202 fit-clip frames + 952 workspace poses outside both benches, 1154) | 28.55 / 31.06 / 11 / 0.11 mm; reach 0.6324, contact 0.0111 | 28.22 / 30.02 / 8 / 0.03 mm; reach 0.6460, contact 0.0239 | **0.33** / 1.04 |
| overhead (elev >= 140): clip follow, ws reach, knee distance to its stop | polish 10/10, 0.25, **1.14 deg**; held 19/19, 0.254, **0.01 deg** | polish 10/10, 0.25, 3.52 deg; held 19/19, 0.211, 3.31 deg | |
| round-3 verifier protocol: shape fitted on Bench(60,160) FAST, worn on Bench(110,360) EXACT | 27.20 / 31.75 / 8 / 0.09 mm; follow 0.9636, contact 0.0256, overhead follow 0.6 | 24.57 / 25.69 / 2 / 0.66 mm; reach 0.6806, follow 0.9727, ib14 0.8822, contact 0.0085, overhead follow 1.0 | 2.63 / 6.06 |
| continuity (1432-pose grid flood fill) | 0 static islands, connected reach = static (all three protocols) | 0 static islands, connected reach = static (all three protocols) | |

The H1 row reproduces the verified margin-5 polish numbers (24.48 / 25.59) to the digit. Held out it reads 28.55 here
against the P5 verifier's 29.12 - a MEASUREMENT difference (that batch fitted the shape on the exact path, these jobs on
the fast cache the polish protocol names). H1's round-3 protocol row reproduces its verified 27.20 / 31.75 to the digit.
Caveat on the round-3 row: both of its benches are inside C1's objective (the validation term IS Bench(60,160)), so its
2.63 / 6.06 gain is not out of sample for the parameters - P5, searched without that term, lost 0.20 near-touch there;
only the held-out row is.

**C1 hardware and rules.** az1 96.90, el1 64.72, az2 29.76, el2 45.53, wd 70.12, wa -6.26, b3 0.328, lE 59.79, lc 26.56,
phiE -5.45, phib -62.78, ang_min 29.63, stk 5.63 (2.56 mm Ti plates on the iglidur pin, between IGLIDUR-PIN 5.0 and the
MR63ZZ pair 6.0), m_lo 5.40 / m_hi 5.12 (J2 hard stops; fold margin over the taken poses >= 5.19 / 5.15 held out), O20 x 3.
J1 seat anterior 0.051 / up 0.904 / lateral 0.424 (acromion top, ruling 4). Knee 91.9-148.9 deg inside [29.6, 150.4].
Arm at the side: 0 poses < 1 mm (lowest 1.16 mm held out).

**Red team.**
* *The gain does not travel (again).* Plain held-out gain 0.33 < 1. The validation term fell 24.74 -> 17.04 (7.7
  points) on Bench(60,160) while held out moved 0.33: once a pose set is inside the objective it is fitted too, 690
  poses as much as 470. The search-to-held-out gap stays ~5 points (23.0 vs 28.2) for every polished config: it lives in
  the shape fit (link heights fitted to the very poses scored) and in contact on unseen poses, not in reach.
* *C1 buys reach with contact.* Held out C1 has 20 contact poses vs H1's 9 and 0 part jams vs 29 (stops and seats moved
  the parts apart and the links closer to the skin); min metal 0.03 mm held out. Near-touch held out still improves by
  1.04 (8 poses < 1 mm vs 11).
* *The knee stop overhead - the H1 edge - is bought back.* H1's knee reaches 0.01 deg from its stop on held-out overhead
  poses (1.14 on the bench); C1 keeps 3.3-3.5 deg with every overhead clip frame followed, at the price of overhead
  workspace reach held out (0.254 -> 0.211).
* *Stops.* The optimum puts both J2 stops at the floor (5.1-5.4 deg) in every stream except the random ones: at margin 5
  a wider stop costs reach and buys nothing on this design (no spring / relay takes poses past the stop).

**Verdict (self-measured).** No configuration from polish 2 clears the CLAUDE.md bar out of sample: C1 gains 1.44 on
the search poses and 2.63 / 6.06 on the round-3 protocol (whose poses its objective saw), but 0.33 plain held out
(1.04 near-touch). **H1 stays the polished configuration; the H1 CAD stands.**
C1 is recorded (row field `polish2_m5`) for an independent verifier only for its near-touch / knee-edge gains. Next, if
the knee is polished again: an objective in which no scored pose is a pose the shape was fitted on (2-fold cross-fit:
shape fitted on Bench(60,160) worn on Bench(110,360) + the reverse), a near-2 mm contact margin for unseen poses, or a
larger fast bench (e.g. Bench(220,720)) - more poses, not more streams; the parameter space itself is converged.

## Verification (polish 2) (independent verifier, 2026-10-16 ~10:50 UTC)

**Claim checked:** polish 2's best, **C1 = H1-g69-4**, at fold margin 5 with its J2 stops m_lo 5.40 / m_hi 5.12 and
O20 x3. It was self-measured at 23.04 / near-touch 24.15 on the polish protocol against H1's 24.48 / 25.59, and at
28.22 held out against 28.55. The claim's own conclusion is that C1 does not clear the bar out of sample and H1 stays.

**Harness.** `docs/concepts/verify/skin-normal-3r-pin-knee-polish2-stops.py` is new and was written by the verifier;
no code from `tools/knee_polish2.py` runs.
* It applies the J2 hard stops on the harness's own `MK.Design.ik`. The J1-J3 angle is taken from the SOLVED chain
  (u1 against the J3 axis carried by link 2, R12 u3), not from the arm orientation. The two angles differ by at most
  0.0000 deg on every closed pose.
* It then runs the polish harness `docs/concepts/verify/skin-normal-3r-pin-knee-polish.py` and the continuity flood
  fill `docs/concepts/verify/skin-normal-3r-pin-knee-continuity.py`, both imported unchanged.
* A smoke test on 3000 poses: this stop code and the claim's wrapper refuse the same 8 poses.
* Run settings: CB_EXACT=1 on every wear bench, CB_FOLD_MARGIN=5, O20 only.
* C1 and H1 ran in the same farm batch: exo-cpu1, 13 jobs, about $0.17.
* The Bench(110,360) fast cache (14f156cb6fc8) was assembled in each job, so the fit is fast, as the polish protocol
  names. Exact-fit re-runs were added as a robustness check.
* Raw outputs: `docs/research/polish2_m5/verify/`.

**Measured.** Fold margin 5. Each cell gives gap / near-touch gap (metal < 1 mm counted as contact) / poses < 1 mm /
min metal.

| protocol | H1 (H-g107-1) | C1 (H1-g69-4) | gain plain / near-touch |
|---|---|---|---|
| polish: fit Bench(110,360) fast, worn exact (470 poses, the search's own) | 24.48 / 25.59 / 2 / 0.21 mm (score 91.10) | **23.04 / 24.15 / 2 / 0.04 mm (score 91.62)**; reach 0.6889, follow 1.0, ib14 0.8972, ib10 0.5591, contact 0.0165 | **1.44 / 1.44** |
| same, shape fitted EXACT (robustness) | 25.03 / 26.14 / 2 / 0.20 mm | 23.39 / 24.50 / 2 / 0.06 mm | 1.64 / 1.64 |
| same, harness unchanged (no stops: window 5 at both edges) | 24.48 / 25.59 | 22.75 / 23.86 | 1.73 / 1.73 (the stops cost C1 0.29) |
| HELD-OUT: fit Bench(110,360) fast, worn exact on the 1154 poses outside both benches | 28.55 / 31.06 / 11 / 0.11 mm (score 89.62) | 28.22 / 30.02 / 8 / 0.03 mm (score 89.74); reach 0.646, contact 0.0239 | **0.33** / 1.04 |
| HELD-OUT, shape fitted EXACT (robustness; H1 = the P5 verifier's run of the same harness, docs/research/verify_p5/) | 29.12 / 31.85 / 12 / 0.04 mm | 28.61 / 30.41 / 8 / 0.18 mm | **0.51** / 1.44 |
| round-3 protocol: fit Bench(60,160) fast, worn exact | 27.20 / 31.75 / 8 / 0.09 mm | 24.57 / 25.69 / 2 / 0.66 mm | 2.63 / 6.06 (both benches inside C1's objective) |
| margin 10, polish protocol | 26.45 / 26.45 (verified H1 numbers) | 26.42 / 27.57 / 2 / 0.13 mm; follow 0.9545, overhead clip follow 0.9 (H1 0.6) | 0.03 / **-1.12** |

Every number the claim gives reproduces to the digit:
* C1 polish 23.04 / 24.15 / 0.04 mm, held out 28.22 / 30.02 / 0.03 mm, round-3 24.57 / 25.69.
* H1 24.48 / 25.59, 28.55 / 31.06, 27.20 / 31.75.

**Rules: all hold, nothing loosened.**
* **Verifier checks.** The independent 3D closure, knee-vs-hub-3 upper-half and E boss checks removed 0 poses for C1
  and H1 on every bench.
* **J2 stops are respected.** Over the taken poses the fold margin is 6.97 / 5.19 deg on the polish bench and 6.01 /
  5.15 deg held out (low / high edge), against stops of 5.40 / 5.12.
* **Part envelopes.** O20 at J1-J3. Pin stack 5.63 mm, the same envelope class as H1's 5.68: Ti plates on the iglidur
  pin, between IGLIDUR-PIN 5.0 and the MR63ZZ pair 6.0. Knee link lc 26.56 mm (>= two O12 bosses + 2). lE 59.79 mm.
  Knee window [29.63, 150.37]. b1 = b2 = 0, R_tol 0.5.
* **J1 seat:** anterior 0.051, up 0.904, lateral 0.424. That is the acromion top, so ruling (4) holds.
* **Travel:** J3 182-194 deg (MR117 pair), pins 52-57 deg.
* **Arm at the side** (elevation <= 15): 0 poses < 1 mm on every bench (lowest 1.16 mm held out).
* **Continuity.** Full 1432-pose grid, shape frozen from Bench(110,360) fast, 2-deg slerp edges from elevation 0, no
  joint (q1, q2, q3', pin a, pin b) stepping > 10 deg, knee sign constant, stops installed.
  * Taken nodes (frozen model worn exact on all 1432 poses): 956, all connected, 0 islands. 785 / 785 edges pass and
    the knee stays on ONE branch (sign +1).
  * Kinematic nodes: 985 / 985 connected.
  * On Bench(110,360), connected reach = static reach = 0.6889.

**Red team.**
* *The gain does not travel.*
  * C1 beats H1 by >= 1 point only on poses the search saw: the polish bench at 1.44 (1.64 exact-fit), and the round-3
    benches, which are its validation term.
  * Held out the plain gain is 0.33 (0.51 with the shape fitted exact). The near-touch gain of 1.04 (1.44 exact-fit)
    comes from 8 poses < 1 mm against 11.
  * Re-measured at margin 10, C1 is level with H1 plain (26.42 against 26.45) and 1.12 worse near-touch.
  * By the standard H1 itself was accepted on (>= 1 plain AND near-touch on every protocol), C1 fails on two
    protocols: held-out plain and margin 10.
* *Where the held-out points go.* C1 takes more poses held out (reach 0.646 against 0.632, 0 part-jam poses against 29)
  but lands metal on more of them: 20 contact poses against 9, contact 0.0239 against 0.0111, min metal 0.03 mm. The
  reach is bought with skin contact on poses the shape was never fitted to.
* *The knee stop.* C1 buys back H1's overhead edge: its knee stays 3.31 deg from its stop on held-out overhead poses,
  where H1's comes within 0.01 deg.
  * But over ALL held-out poses C1's knee reaches 148.9 deg against 150.37, a 1.45 deg margin.
  * Its kinematically closed workspace runs to 150.3 deg: the knee is still against its stop, just not on the overhead
    frames.
  * Overhead workspace reach held out drops 0.254 -> 0.211.
* *The stops are almost free.* The stops cost 0.29 points (22.75 without them, 23.04 with them). The optimum sits at the
  5-deg floor because nothing on this design takes poses past a stop.

**Verdict: CONFIRMED as claimed (not refuted), and C1 does not replace H1.**
* The measurement is reproduced exactly and no rule is broken.
* The >= 1-point gain reproduces on Bench(110,360) exact frozen at margin 5: 1.44 plain and near-touch.
* The gain is in-sample: held-out plain is 0.33, and at margin 10 the near-touch gain is -1.12.
* **H1 stays the polished configuration.** best_k H-g107-1 is unchanged, the `v_polish2_*` fields hold these numbers,
  and the H1 CAD stands.

For the next polish, one change is needed: score only poses the shape was NOT fitted on (a 2-fold cross-fit).
* Every polished config so far sits ~5 points worse held out than on its search bench: P5, C1 and H1 itself (24.5 vs
  28.6).
* The 690 poses of polish 2's objective were fitted as hard as the 470 of polish 1.

## Massive GPU polish (gpu-knee, tools/gpu_knee_search.py, 2026-10-16 ~09:50-11:40 UTC)

Run directory `exo-farm/gpuk/out/gks1`. Digest: `docs/research/golden/gks1_digest.json` (+ `_all.npz`, every evaluation).
Sweep log stages `gpu-knee-*`. Rows file key `gpu_knee_massive`. Pod jobs: `pipeline/gpu_pod/gks.sh` (boot + search),
`gks2.sh` (restart on an override driver), `gks4.sh` / `gks5.sh` (restarts through the volume), `gks6.sh` (digest).

**What was searched.**
* Objective: the near-touch gap (metal < 1 mm counts as contact) of the adversarial verifier's corrected set on
  Bench(110,360), same-bench (shape fitted there, fast grid), plus 100 x the clip frames lost. The penalty keeps every
  overhead clip frame followed.
* Evaluator: the GPU port `tools/gpu_bench_knee.py`. It is the CPU kit's own code with the per-pose loops batched on
  the device; parity with the kit is 0.0 on 54 configs x 2 protocols.
* Free: the 13 continuous parameters of `tools/knee_polish.py` FREE: the seats (az1 el1 az2 el2 wd wa b3), the knee
  (lE lc phiE phib), the knee window ang_min and the pin stack stk. Also free: **the fold margin**, >= 5 deg, set per
  evaluation on the IK's SING. That is the same global the CPU kit reads from CB_FOLD_MARGIN.
* Fixed by the rulings: O20 hubs; the J1 seat on the back / acromion top (anterior component <= 0.20, rejected before
  evaluation); b1 = b2 = 0; and the knee branch, a fixed sign with 10 fps continuity of q1, q2, q3', pin a and pin b
  inside the window [ang_min, 180 - ang_min].
* Raglan-knee-3r enters through its seats on straight links. The polish verifier has no route, so routed links stay out.

**How it ran.**
1. Seeds: H1, P5, HW, k4598, raglan's seats, and the in-sample GPU bests G2 and G3.
2. Sobol: 101,624 scrambled-Sobol points inside the rulings, in boxes around the leaders' basins and wide over the
   bounds:
   * G3: +-3 and +-1 x the polish's CMA scale.
   * H1, P5, k4598 and raglan: +-3.
   * G2 and HW: +-2.5.
   * All of these boxes sample margin 5-8.
   * 24,400 wide points over the bounds, with margin 5-12.

   Pods share the points in chunks of 512 through O_EXCL claim files on the farm volume. A traced sample outside the
   +-260 mm grid uses the bound d(clamped) - |offset|, which is never optimistic.
3. CMA: knee_polish's update, lambda 12, run in the best distinct points (> 2.5 CMA-scale units apart), lockstep per
   pod. Each run stops at convergence (sigma x max axis < 0.02, or no gain > 0.02 in 40 generations) or at the
   deadline.
4. Final: the top 30 distinct points are re-evaluated on the port's exact outside path. The top 10 that follow every
   clip frame, plus H1, go to the CPU kit, unpatched, on the pods' CPUs:
   `docs/concepts/verify/skin-normal-3r-pin-knee-polish.py` fitbig / fit60 / held (CB_EXACT=1, CB_FOLD_MARGIN = the
   config's margin), and the continuity flood fill (`skin-normal-3r-pin-knee-continuity.py` kin fitbig).

**What went wrong on the way.** The first launch gave each pod one GPU worker per vCPU, which meant 31 workers on a 32 GB
RTX PRO 4500. Each worker holds its own 1.06 GB int8 copy of the Bench(110,360) grid plus a CUDA context. Workers past
about 14 ran out of device memory, and their evaluations failed fast as CUDA errors: the log showed "77 evals/s", mostly
errors. The fix:
* the driver caps workers by device memory;
* a restarted pod re-runs its own CUDA-error rows first;
* the stages after Sobol use fresh marker names, so no stale state from the out-of-memory run leaks in.

The pods were restarted on the corrected driver at 10:28, 10:31 and 10:42 UTC. The first restart ran 14 workers per RTX
PRO 4500 and still ran out of memory, so the driver now allows 2.8 GB per worker, which gives 10 workers. The lead then
put the deadlines on the volume (final: Sobol 10:54, CMA 11:12, verification 11:36 UTC). It stopped the RTX 4090 pod for budget,
and also the fourth pod. Their CUDA-error rows were queued on a live pod, but not all of them ran before the Sobol
deadline. Next time, share one device grid per GPU
through CUDA IPC. GridDev already takes a shared tensor. Then every vCPU can run a worker.

**What it measured (self-measured: the search's own driver ran the CPU kit; not an independent verification).**

*Evaluations.* 221,042 rows were written. 165,927 are distinct evaluations: 101,631 seeds + Sobol and 64,296 CMA.
101,240 of them closed a report. The rest are mainly the 64,087 CUDA-error rows of the out-of-memory phase:
* 34,386 Sobol points were never re-run before the Sobol deadline, so 67,214 of the 101,624 Sobol points were scored.
* 29,701 rows were from the first, broken CMA.

The restarted CMA ran in 30 basins for 80 generations each (12 per generation). It was stopped by the deadline, not by
convergence: only b18 stopped on its own. Median 0.70 s per evaluation per worker; 13-14 evaluations/s per RTX PRO
4500 at 10-14 workers.

*Sobol finds nothing new.* No Sobol point beats the in-sample G3 (20.81). The best Sobol point is 23.31, in the +-1 box
around G3; 22 points of that box are below 25. The +-3 boxes around G3 / G2 / P5 / HW / H1 / k4598 / raglan's seats
have their best at 26.3-34.7. The 24,400 wide points over the bounds have their best at 59.2.

The basin is narrow. The +-1 x CMA-scale box around G3 holds 810 of its 5,301 scored points below 30. The +-3 box
holds 4 of 21,404.

*CMA ends in the same corner.* The 30 basin bests lie at 20.81-24.46, and 12 of them are below 22. Those 12 sit at
lE 65-80, lc 25-42 and ang_min 22-37. All 30 sit at az1 96-107, az2 30-40 and wd 60-69: G3's corner (a long E strap).
The margin over the 30 runs from 5.0 to 6.35, median 5.15.

The free margin ends at **5.0-5.4 deg** in every top-10 config: the user's floor binds, and a wider margin only costs
reach.

*Top 10 distinct, exact.* The table below is the CPU kit on the pods: fit Bench(110,360) fast, worn EXACT, at the
config's own margin. H1 was run in the same batch:

| config | search tag | margin | fitbig gap / near-touch | fit60 gap / near-touch | held gap / near-touch | reach / in-band 14 / contact (fitbig) | overhead >= 140 ws reach / clip follow | min metal mm | connected reach (static), full grid |
|---|---|---|---|---|---|---|---|---|---|
| F1 | G3 (in-sample GPU best) | 5.00 | 20.26 / 21.36 | 23.33 / 24.44 | 27.68 / 29.05 | 0.706 / 0.901 / 0.008 | 0.32 / 1.0 | 0.46 | 0.681 (0.682) |
| **F2** | cma-b16-g78-7 | 5.03 | **20.26 / 20.81** | 23.34 / 24.46 | 27.65 / 29.25 | 0.706 / 0.901 / 0.008 | 0.32 / 1.0 | 0.35 | 0.680 (0.680), 0 islands |
| F3 | cma-b13-g79-5 | 5.37 | 20.25 / 21.90 | 25.27 / 30.79 | 28.33 / 31.06 | 0.708 / 0.900 / 0.011 | 0.29 / 1.0 | 0.41 | 0.686 (0.687) |
| F4 | cma-b23-g78-3 | 5.00 | 20.33 / 21.43 | 24.44 / 28.25 | 28.71 / 30.09 | 0.706 / 0.897 / 0.006 | 0.32 / 1.0 | 0.32 | 0.673 (0.673) |
| F5 | cma-b20-g65-8 | 5.38 | 20.35 / 22.00 | 25.57 / 30.56 | 27.51 / 29.33 | 0.706 / 0.899 / 0.008 | 0.32 / 1.0 | 0.24 | 0.682 (0.682) |
| F6 | cma-b27-g60-5 | 5.00 | 20.63 / 21.18 | 24.14 / 29.65 | 27.62 / 29.89 | 0.708 / 0.896 / 0.011 | 0.29 / 1.0 | 0.71 | 0.687 (0.688) |
| **F7** | cma-b0-g77-1 | 5.10 | 20.81 / 21.91 | 25.57 / 30.56 | **27.22 / 29.04** | 0.703 / 0.900 / 0.011 | 0.29 / 1.0 | 0.70 | 0.687 (0.687) |
| F8 | cma-b24-g72-7 | 5.39 | 21.24 / 21.79 | 24.92 / 30.26 | 28.90 / 31.61 | 0.706 / 0.893 / 0.011 | 0.29 / 1.0 | 0.79 | 0.688 (0.689) |
| F9 | cma-b5-g78-9 | 5.16 | 20.68 / 21.23 | 24.04 / 29.36 | 28.77 / 30.80 | 0.711 / 0.896 / 0.014 | 0.32 / 1.0 | 0.54 | 0.702 (0.704) |
| F10 | cma-b4-g72-1 (from H1) | 5.05 | 20.96 / 21.51 | 24.03 / 25.15 | 28.33 / 29.92 | 0.703 / 0.896 / 0.008 | 0.32 / 1.0 | 0.39 | 0.679 (0.679) |
| H1 | the verified leader | 5.00 | 24.48 / 25.59 | 27.20 / 31.75 | 28.55 / 31.06 | 0.669 / 0.894 / 0.009 | 0.25 / 1.0 | 0.21 | 0.687 (0.688) |

All finalists keep:
* O20 hubs;
* the J1 seat with anterior component 0.055-0.097 (back / acromion top);
* every clip frame followed (follow 1.0, overhead clips too);
* the fold margin >= 5.0 deg on every taken pose;
* the knee at 75-157 deg, inside its window, on one branch sign.

The continuity flood fill (full 1432-pose grid, 2-deg slerp edges) leaves 0-3 static-only islands. Connected reach
equals static reach to within 0.002.

*The lesson.* The search bench gain is real but does not travel. Against H1 in the same batch:

| protocol | F2 gain, plain / near-touch | F1 gain, plain / near-touch | spread over the top 10, plain |
|---|---|---|---|
| fitbig (the search bench) | 4.22 / 4.78 | 4.22 / 4.23 | 3.2-4.2 |
| fit60 | 3.86 / 7.29 | 3.87 / 7.31 | |
| held-out (disjoint poses) | 0.90 / 1.81 | 0.87 / 2.01 | |

F7 (from the G3 seed's basin) is the best held out: 27.22 / 29.04, a gain of 1.33 / 2.02. F5 gains 1.04 / 1.73.

Searching the same bench again (G3's corner, lE 72-77) costs 7.4 points out of sample (F2 20.26 -> 27.65). H1 loses 4.1.
This is the polish-2 finding again, now on 10^5 points: a same-bench objective overfits the 470 poses. Only F7 and F5
clear the 1-point bar held out on the plain gap. On the held-out near-touch gap, F1 / F2 / F5 / F6 / F7 / F10 clear it
(1.1-2.0); F3 / F4 / F8 / F9 do not (-0.6 to 1.0).

*Candidates for the independent verifier* (CLAUDE.md FINAL POLISH: a polished config replaces the CAD's only after an
independent verifier confirms >= 1 gap point):
* F7: held-out 27.22, score 90.10 vs H1 89.62;
* F2: fitbig 20.26 / 20.81, score 92.63 vs H1 91.10;
* F5.

The next search should score poses the shape was not fitted on: a 2-fold cross-fit objective. The port takes any Bench
with a fast grid.

## Verification (massive GPU polish) (independent verifier, 2026-10-16 ~11:45 UTC)

**Claim checked:** the massive GPU polish (`gpu_knee_massive`). Its best, **F2** (cma-b16-g78-7, margin 5.0254), was
self-measured at 20.26 / near-touch 20.81 on the polish protocol against H1's 24.48 / 25.59, and at 27.65 held out. Its
best held out, **F7** (cma-b0-g77-1, margin 5.0956), was 27.22 / 29.04 against H1's 28.55 / 31.06. F5 was also checked.

**Harness.** No code from the search driver or the GPU port ran.
* The polish harness `docs/concepts/verify/skin-normal-3r-pin-knee-polish.py` (fitbig / fit60 / held) and the
  continuity flood fill `skin-normal-3r-pin-knee-continuity.py` (kin / taken), both imported unchanged.
* Driver `docs/research/verify_gpuknee/run.sh`: the Bench(110,360) fast cache 14f156cb6fc8 is copied from the farm
  volume to each worker, so the fit is fast as the polish protocol names; CB_EXACT=1 on every wear bench.
* CB_FOLD_MARGIN = the claimed margin, then 5, then 10 (the old rule, a measurement change). O20 only.
* Farm exo-cpu1, 38 jobs in 3 batches, about $0.23. F2 fit60 was also re-run on this box: same digits.
* Raw outputs and the parameter file: `docs/research/verify_gpuknee/`.

**Measured.** Each cell: gap / near-touch gap (metal < 1 mm = contact); gain over H1 plain / near-touch in brackets.

| protocol | H1 (margin 5) | F2 (5.0254) | F7 (5.0956) | F5 (5.3817) |
|---|---|---|---|---|
| polish: fit Bench(110,360) fast, worn exact (470) | 24.48 / 25.59 | 20.26 / 20.81 (4.22 / 4.78) | 20.81 / 21.91 (3.67 / 3.68) | 20.35 / 22.00 (4.13 / 3.59) |
| round-3: fit Bench(60,160) fast, worn exact | 27.20 / 31.75 | 23.34 / 24.46 (3.86 / 7.29) | 25.57 / 30.56 (1.63 / 1.19) | 25.57 / 30.56 (1.63 / 1.19) |
| **HELD OUT** (1154 poses outside both benches) | 28.55 / 31.06 | 27.65 / 29.25 (**0.90** / 1.81) | 27.22 / 29.04 (1.33 / 2.02) | 27.51 / 29.33 (1.04 / 1.73) |
| held out at margin exactly 5 | - | same | 27.11 / 28.92 (1.44 / 2.14) | 27.31 / 29.13 (1.24 / 1.93) |
| polish at margin 10 (old rule) | 26.45 / 26.45 | 28.10 / 28.68 (-1.65 / -2.23) | 28.97 / 29.54 (-2.52 / -3.09) | - |
| held out at margin 10 (old rule) | 30.73 / 32.61 | 32.58 / 33.99 (-1.85 / -1.38) | 32.43 / 34.76 (-1.70 / -2.15) | - |

Every number the claim gives reproduces to the digit, H1's included (its margin-10 rows reproduce the verified
26.45 and 30.73). F7 and F5 really do measure the same fit60 numbers (25.57 / 30.56, reach 0.6722): the two runs are
independent, so this is not a digest copy.

**Rules: none broken, nothing loosened.**
* The 3D closure, knee-vs-hub-3 and E boss checks removed 0 poses on every run. Closure residual is at most 0.022 deg.
* O20 x3. Pin stack 5.87 (F2) / 5.57 (F7) mm. J1 seat anterior component 0.0625 (F2) / 0.0809 (F7): the acromion top.
* Fold margin over the taken poses is >= 5.01 deg. Overhead clip follow is 1.0 on the polish and held-out benches.
  (The round-3 bench's overhead clip follow is 0.6 for F7, F5 and H1, and 1.0 for F2.)
* Arm at the side: 0 poses < 1 mm in-sample. F2 has 2 held out (0.02 mm and 0.63 mm), where H1 has 0.
* Continuity (taken nodes, full 1432-pose grid): F2 949 / 949 and F7 953 / 953 connected, 0 islands, one knee branch.
  Connected reach on the bench equals static reach (0.7056 / 0.7028). In kin mode F7 has 1 static-only island on the
  full grid; H1 has 1 too.

**Red team: where the gain comes from.**
* *The knee window.* The search moved the knee window ang_min from H1's 30.46 to 22.79 (F2) and 21.93 (F7), just
  above the polish bound of 20. Over the taken poses the knee now runs to 156.7 / 157.3 deg. That is 22.7-23.3 deg
  from the straight (singular) posture, against H1's 31.6 deg, and 0.5-0.8 deg from the knee's own stop.
* *Test.* I re-ran F2 and F7 with H1's ang_min (30.46) and everything else as claimed:

  | protocol | F2 at ang_min 30.46 | F7 at ang_min 30.46 |
  |---|---|---|
  | polish | 23.91 / 23.91 (gain 0.57) | 23.91 / 24.46 (gain 0.57) |
  | held out | 29.28 / 31.34 (gain **-0.73**) | 28.63 / 30.47 (gain **-0.08**) |

  So the whole held-out gain is the knee's singularity margin. CLAUDE.md says: never shrink the singularity /
  transmission margins to buy reach without a red-team and the user's say. This is that red-team.
* *The fold floor.* At the old 10-deg fold margin, F2 and F7 are 1.65-2.52 points worse than H1 on the polish
  protocol and 1.70-1.85 worse held out. Their gain lives on the 5-deg floor and the 22-deg knee window together.
* *Overfit.* The polish bench gives 4.22 for F2, and held out gives 0.90. The same-bench objective overfits again,
  as it did for polish 1, P5 and C1.

**Verdict: REFUTED as a replacement for H1. The measurement itself is confirmed.**
* The claimed best, F2, gains 0.90 plain held out, which is under 1.
* F7 clears 1 on all three margin-5 protocols, plain and near-touch. But all of that gain comes from a 22-deg knee
  window, against H1's 30.5. Taking it needs the user's ruling on the knee singularity margin.
* **H1 stays the polished configuration.** best_k is unchanged; these numbers are in the `v_gpuknee_*` fields.
* Next:
  * The cross-fit polish (`tools/crossfit_polish.py`) should keep ang_min >= 30 unless the user rules otherwise.
  * Ask the user whether a ~22-deg knee window is acceptable for the unpowered MVP1: F7 then gains 1.33-1.44 held out.
