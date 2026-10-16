# offset-skin-normal-3r - non-concurrent 3R on skin-normal hubs with a 2-slide self-aligning cuff

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Ask first which offset geometries a
   2-slide cuff can close at all, and prove it, instead of tolerating a "<= 3 mm radial residual" (that residual is
   skin compression under the cuff at every pose, not a closure). Then: put the slides where the drift lives (the
   plane of hub 3), and look at the stage's own geometry - an arm-fixed long rail is metal that the distal link must
   fly over at every slide position; turning the guide upside down (short carriage on the cuff, rail riding with the
   chain) removes that conflict for free. Price every passive slide in stack height, because each one lifts the
   distal chain off the arm.
2. **Rawest material.** The posed render skin of every bench pose (signed distance per sample, fast grid and exact
   libigl paths), the fit clips at full 10 fps (pipeline/conformal/band_poses_wsf.b64: FI order, HG / RS) for the
   radial-drift scan and the continuity check, the rest-pose skin mesh itself for the seat normals (area-weighted face
   normals within 10 mm of each seat), and the skin-motion map / proximity atlas only as a cross-check of where hub 2
   gets pushed up.
3. **Methods and tools.** Screw composition X = R x + t(q) and its closure condition (a 3-line proof, below);
   closed-form spherical IK of the axis directions (exact orientation, no iteration: residual 0.015 deg); sphere
   tracing on the bench signed-distance grid to fit every skin-facing underside (2 mm grid, <= 60 deg ramps); exact
   box / cylinder signed distances for part-part clearance; the cloud CPU farm for the coarse sweep and CMA-ES
   (tools/cloud_run.py, tools/concept_cma.py).
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, metrics and contact rule as
   the 68.93 baseline), the seed-offset-3r-slides VModel checks this model inherits (written by that model's
   adversarial verifier), the adversarial verifier that will re-run this model, and the red-team pose list below.

## Spec correction (proved, then measured)

With translations only, the end link moves as X(x) = R x + t(q), t = (I-R1)c1 + R1(I-R2)c2 + R1R2(I-R3)c3, where c_k is
a point of axis line k and R = R1R2R3 is exactly the arm's rotation (spherical IK of the axis directions). Two slides
spanning the plane normal to an arm-fixed n close the loop iff (R n).t = 0 for every arm orientation:

* term 3: n.(R3^T - I)c3 = 0 for every q3 -> n = d3 (the slide plane is hub 3's plane), or line 3 through GH;
* term 2: c2.(R2 - I)R3 n = 0 for every q2, q3 -> c2 parallel to d2 -> line 2 through GH;
* term 1: likewise -> line 1 through GH.

So a 2-slide cuff closes exactly iff J1 and J2 are concurrent at GH and the slides lie in hub 3's plane; J3's line is
free (position and skin-normal tilt). The spec's all-skin-normal chain does not close. Measured over the 10 fps fit
clips + the bench workspace (`python3 docs/concepts/models/offset-skin-normal-3r.py kin`, seats of the best
skin-normal-hubs-selfaligning configuration):

| hubs | axis-line offsets from GH (mm) | radial drift span | poses closable at +-0.5 mm | at the spec's +-3 mm | along / across travel |
|---|---|---|---|---|---|
| spec: all skin-normal (b 1, 1, 1) | 14.8 / 16.3 / 30.3 | 30.3 mm | 17.7 % | 41.5 % | 69 / 74 mm |
| half tilt (b .5, .5, .5) | 7.5 / 8.3 / 16.3 | 16.1 mm | 23.0 % | 65.6 % | 34 / 38 mm |
| J1 tilted 2 deg only (b1 .1) | 1.5 / 0.3 / 0.2 | 3.5 mm | 51.9 % | 100 % | 3.5 / 2.0 mm |
| **exact subfamily (b 0, 0, 1)** | 0 / 0 / 33.2 | **0.00 mm** | 100 % | 100 % | 66 / 66 mm |
| exact subfamily (b 0, 0, .6) | 0 / 0 / 20.5 | 0.00 mm | 100 % | 100 % | 40 / 41 mm |

Even a 2 deg tilt of hub 1 off the GH ray leaves half the poses unclosable. The model therefore builds the exact
subfamily: J1 and J2 on GH rays (their seats still free: that is a re-tuned spherical pair), J3 on a skin seat with its
axis tilted toward the local skin normal by b3 (b3 = 1 square on the skin), the 2 slides in hub 3's plane (along the
humerus, across it), and NO radial slide (R_r = the 0.5 mm closure tolerance). Loop mobility = 3: every slide is set by
closure.

## Stage geometry fix (measured)

With the seed model's arm-fixed long rail (8 x (20 + 2 S_a)) the member-3 neck and hub 3 slide over the rail: 81 and
103 of 220 poses jam (neck-rail, hub3-rail) at b3 0.6 and 0.2 (gap 132 / 143). The 3-slide relatives escape this only
because their radial slide lifts carriage B by R_r. The fix here (`inv=1`): the along guide upside down - its 20 x 20
carriage is fixed on the cuff, its rail rides with carriage A and follows member 3 along the arm, so its proximal end
stays at the neck end and nothing arm-fixed ever reaches under the neck. Same stack height. Jams: 0; gap 54.9 / 45.3.

## Model (docs/concepts/models/offset-skin-normal-3r.py)

* Kinematics: orientation = closed-form spherical IK of the three axis directions (closure residual 0.015 deg), the
  J3 line offset gives the drift t3(q), absorbed exactly by the two slides (s = Q^T t3, radial part identically 0 in
  this subfamily: measured span 0.000 mm). R_r = 0.5 mm (the closure tolerance), no radial slide in the stack.
* Seats: J1 / J2 on GH rays (bvec az, el in the scapula frame), the seat 2 mm off the rest-pose skin; J3 on the arm
  (w_dir wd, wa in the band humerus frame), axis = nlerp(GH ray, mean outward skin normal within 10 mm, b3).
* Parts at real size, inherited from the verified seed-offset-3r-slides VModel: O20 x 12.25 hubs, 8 x 3 straps with
  skin-fitted undersides (<= 60 deg ramps), member 3 = hub 3 + ramped neck + riser + bridge + carriage B, stage =
  inverted along guide (arm-fixed 20 x 20 x 4 carriage block; rail 8 x 4 x (20 + 2 S_a) + carriage A 20 x (20 + 2 S_t)
  x 4 riding together) + across guide; 0.5 mm running gaps; 2 mm sample grid on every skin-facing underside;
  side walls and box edges checked for contact; part-part clearance >= 1 mm (exact boxes / cylinders, the moving rail
  against hubs 1, 2 and links 1, 2 added here; hub 1 vs hub 2 static check).
* A pose is taken iff the IK closes >= 10 deg from the J2 fold, the slides are in range (S_auto + 0.5 mm, centred,
  cap 25 mm), no joint jumps > 25 deg between consecutive 10 fps clip frames, rotation closure < 0.5 deg, part
  clearance holds, and no metal is inside the skin (greedy skin-pose dropping recorded as contact, jam rule on).

## Results (Bench(60,160), fast grid; sweep log docs/concepts/sweeps/offset-skin-normal-3r.json)

| configuration (same model, same rules) | gap | score | reach | follow | in-band 2-14 | 2-10 | contact |
|---|---|---|---|---|---|---|---|
| bench baseline (champion spherical 3R, tools/concept_baseline.py) | 68.93 | 74.93 | 0.775 | 1.000 | 0.438 | 0.279 | 0.102 |
| seed's arm-fixed rail, b3 0.2 (k1) | 142.60 | 48.15 | 0.244 | 0.400 | 0.780 | 0.425 | 0.100 |
| inverted guide, skin-normal-hubs seats, b3 0 (spherical J3, k4) | 49.11 | 82.14 | 0.638 | 0.967 | 0.736 | | 0.064 |
| inverted guide, same seats, b3 0.2 (k3) | 45.31 | 83.52 | 0.663 | 1.000 | 0.725 | 0.305 | 0.041 |
| coarse farm sweep, 216 configs (random seats: best 47.90) | 45.31 | | | | | | |
| CMA stream A (481 tries, sigma collapsed) | 38.65 | 85.95 | 0.688 | 1.000 | 0.755 | 0.371 | 0.029 |
| CMA stream B (665 tries, collapsed) | 40.06 | 85.43 | 0.675 | 1.000 | 0.791 | 0.404 | 0.067 |
| CMA stream C (697 tries, collapsed), k1908 | 35.65 | 87.04 | 0.713 | 1.000 | 0.748 | 0.383 | 0.017 |
| control at k1908's seats, b3 0 (J3 on the GH ray) | 42.92 | 84.39 | 0.681 | | 0.713 | | 0.023 |
| CMA round 2, stream D (from C, sigma 0.3, 673 tries) | 34.45 | 87.47 | 0.688 | 0.967 | 0.791 | 0.404 | 0.023 |
| CMA round 2, stream E (from C, sigma 0.6, 673 tries) | 34.53 | 87.44 | 0.713 | 1.000 | 0.759 | 0.386 | 0.017 |
| **CMA round 2, stream F (from A, sigma 0.5, 873 tries) - best, k4216** | **32.61** | **88.14** | 0.706 | 0.967 | 0.779 | 0.389 | 0.012 |
| control at k4216's seats, b3 0 (J3 on the GH ray) | 46.71 | 83.01 | 0.681 | 0.917 | 0.709 | 0.319 | 0.024 |
| reference: skin-normal-hubs-selfaligning (3 slides, radial 6.7 mm), its sweep best at 22:37 | 35.86 | 86.96 | 0.656 | 1.000 | 0.803 | 0.349 | 0.018 |

Best configuration (k4216): J1 seat bvec(95.9, 65.2), J2 seat bvec(10.9, 54.7) (both on GH rays: link 1 40.3 deg,
link 2 74.1 deg), J3 seat w_dir(79.2, -13.4) tilted b3 0.23 toward the skin normal (26.6 deg between the GH ray and
the skin normal there; the J3 line misses GH by 7.0 mm), neck 16.8 mm; slide travel used +-5.8 along / +-7.0 across
(ranges 6.3 / 7.5); radial drift 0.000 mm. Faces f1 51.3, f2 61.2, f3 75.7 mm. In band 2-14 per part: hub 1 100 %,
hub 2 99.6 %, link 1 93 %, rail block 89 %, link 2 82 %, moving rail 70 %, carriage A 67 %, neck 62 %, hub 3 50 %
(median 14.0 mm), bridge 0 % (17.7 mm). The k1908 basin (C) as a b3 ladder: 0 -> 42.92, 0.1 40.76, 0.2 41.80,
0.3 38.82, 0.4 37.49, 0.5 45.36 (slide travel then exceeds what the stack can carry in band).

**What the morphology buys.** At the best seats, tilting J3 toward the skin normal (b3 0.23) with its line 7 mm off GH
buys 14.1 gap (46.71 -> 32.61; 7.3 at k1908's seats): fewer J2-fold poses (52 -> 47) because the J3 direction moves,
hub 3 and the stage lower, link 2 straighter. The re-tuned J1 / J2 seats are a spherical-family freedom (they could be
handed to the spherical GPU sweep). The 2-slide exact cuff scores better than the 3-slide
skin-normal-hubs-selfaligning on the same bench (32.61 vs its 35.86 at 22:37): **the radial slide is not needed on
this bench** - it adds an unguided stroke (the verifier's open hole in the seed) and 0.5 + R_r mm of stack.

**Convergence gate (binding), whole history in order (4523 tries: 220 coarse/controls, 1843 CMA round 1, 2356
round 2, 7 controls): NOT converged** - the best gained 1.11 score points over the second half and 0.67 over the last
third (round 2's restart from stream A's basin found 32.61); top 5 within 0.07. Each CMA stream converged on its own
(sigma collapsed to 0.02; per-stream gates: A +0.25 / +0.08 / 0.02, B +0.27 / +0.09 / 0.03, C +0.15 / +0.15 / 0.03),
so the landscape is multi-basin: restarts from a stream's optimum at larger sigma find new basins. Round 3 (G, H from
k4216 at sigma 0.3 / 0.7, I from D at 0.5) was submitted to the farm at 23:31 UTC (outputs .cache/osn/cma{G,H,I}.json).

## Red team (best configuration, k4216)

* **The pose that jams.** 47 poses are lost to the J2 fold (>= 10 deg margin): across-the-body 12 of 36, overhead 19
  of 41 (Raise overhead clip frames #3 and #7 among them: follow 0.967), behind-the-back 5 of 19; 2 more to the skin
  (plane -15, elev 90-105, axial 45-60, where hub 2's outward ray is blocked by the elevated arm). The fold window is
  |a1 - a2| + 10 to a1 + a2 - 10 of the J1-J3 axis angle (here 44-104 deg), which spans 13-156 deg over the bench (5-95 %
  30-124 deg). Margin sensitivity (at k3): 10 deg 173 / 220 poses close, 5 deg 183, 0 deg 191. No offset or slide can
  move the fold: the orientation IK is the spherical one with the same directions.
* **The point that pinches.** Over the poses taken the lowest metal is the arm-fixed guide block at **0.21 mm** (plane
  -90, elev 45, axial 120: behind the back), hub 2 at 0.49 mm (plane 0, elev 75, axial 45) and 0.76 mm (plane 15),
  hub 2 1.00 mm (plane 60, elev 135), the block 1.14 / 1.41 mm (plane 90-105, elev 30, axial -135). In the *Raise
  overhead* top frames hub 2 sits in the gap UNDER the elevated arm (the outward ray through hub 2 re-enters the arm,
  needed height unbounded: those frames were dropped from the fit but the metal clears, so the bench takes them) - a
  closing pinch between arm and acromion. (k1908 had link 2 at 0.01 mm at plane 60, elev 165.)
* **The optimistic number.** The bench takes a pose at metal >= 0 mm. Counting a taken pose as contact when its metal
  comes within 1 mm: gap 37.42 (4 poses); within 2 mm: 41.44 (8 poses, 1 clip frame). CMA pushes the fitted undersides
  to the edge of the envelope; the verifier should re-measure on Bench(110,360) exact, where the envelope holds more
  poses (the seed lost 6.8 gap that way).
* **Closure and slides.** Rotation residual max 0.015 deg; radial drift 0.000 mm over 514 clip + workspace poses (the
  subfamily is exact by construction); both slides set by closure, no flips between 10 fps clip frames; 0 part jams
  with the inverted guide (55-103 with the seed's arm-fixed rail).
* **Not modelled.** The inverted guide's rail overhangs carriage A by S_a (10 mm) at each end, cantilevered on a
  20 mm carriage (stiffness not checked); the slides' end stops and the user's sensing are not modelled; the bench has
  no GH translation, so the slides' R10 benefit (absorbing real GH-vs-scapula motion) is invisible here and the 2-slide
  cuff would have to absorb that translation's radial part too (it cannot: a real arm would need the third slide or
  soft-tissue compliance for R10 - test it on the R10 judge before choosing between 2 and 3 slides).

## Verdict

**Screened, a leader on the screening bench: gap 32.61 (score 88.14), Bench(60,160) fast, every verifier check of the
seed's VModel on; not yet converged by the whole-history gate.** It beats the 68.93 baseline by 36 and the 3-slide
skin-normal relative by 3. The morphology's own contribution is real and measured (J3 tilted toward the skin normal
with its line 7 mm off GH: 14.1 gap at the best seats, 7.3 at another basin's seats). The spec's version (all three
hubs skin-normal, 2 slides) cannot close (17.7 % of poses at +-0.5 mm); the exact form is J1 / J2 on GH rays + a free
J3 line + 2 slides in hub 3's plane, and the radial slide of the 3-slide relatives is unnecessary on this bench.

New knowledge (predicts beyond this morphology):
1. **Two-slide closure theorem.** A translational cuff with k slides closes an offset 3R exactly iff every axis line
   except the last passes through GH and the slides span the last hub's plane (k = 2) - any J1 / J2 offset needs the
   third (radial) slide. This applies to every "offset axes + passive cuff" concept in the catalogue
   (offset-axis-skin-hubs, offset-flex-aligner, seed-offset-3r-slides, skin-normal-hubs-selfaligning).
2. **An arm-fixed guide rail is metal the distal member must fly over.** With the seed's stage, every J3 offset that
   needs > ~5 mm of along-travel jams the neck on the rail (55-103 of 220 poses). Mounting the guide upside down (short
   carriage on the cuff, rail riding with the chain) removes the conflict at no height cost. The 3-slide models escape
   only because their radial slide lifts carriage B.
3. **The limiter left is the spherical J2 fold** (47 poses at 10 deg margin, window 44-104 deg vs 13-156 deg needed) -
   orientation-level, untouched by any offset or slide - and hub 3 + the stage at ~50-67 % in band (median 12-14 mm).

**Next (the loop):** let round 3 finish and append it (the gate); the adversarial verifier re-measures k4216 on
Bench(110,360) exact with 1 mm radial clearance; then the R10 judge with the real GH translation decides between 2 and
3 slides (on the real arm the GH-vs-scapula translation has a radial part that only a third slide or soft tissue can
take). The fold needs a morphology change (a 4th passive DOF at the J2 fold, or link angles a1 ~ a2 ~ 85 deg with
J2 parked where the arm is not), not more tuning.

## Verification (k4216) - adversarial verifier, 2026-10-16

**Verdict: verified, not 90+.** The claim reproduces exactly on its own bench, no hard rule is broken, and the frozen
shape beats the champion by 24.4 points on the large exact bench. But it degrades to **v_gap 42.59** (score 84.5) on
Bench(110,360), exact path, shape frozen from the Bench(60,160) fit. The loss is reach (0.706 -> 0.611): 136 of 470
poses fall in the J2 fold. Script: `docs/concepts/verify/offset-skin-normal-3r.py` (model checks + the checks below;
the champion runs through the same code).

| run | gap | reach | follow | in-band 2-14 | 2-10 | contact |
|---|---|---|---|---|---|---|
| claim, Bench(60,160), fast grid (reproduced exactly; sweep log k4216 = row = doc) | 32.61 | 0.706 | 0.967 | 0.779 | 0.389 | 0.012 |
| same + verifier checks (crowns, strap tops, link 2 vs member 3) | 32.61 | 0.706 | 0.967 | 0.779 | 0.389 | 0.012 |
| Bench(60,160), **exact** path (CB_EXACT=1), refit, verifier checks | 32.71 | 0.706 | 0.967 | 0.778 | 0.398 | 0.012 |
| **Bench(110,360), exact, FROZEN shape from the 60/160 fast fit, verifier checks (v_*)** | **42.59** | 0.611 | 0.964 | 0.784 | 0.398 | 0.021 |
| champion (seed VModel, slides 0: r20 s1414 #4 axes, arm-fixed hub-3 block), Bench(60,160) fast, same checks | 63.26 | 0.744 | 0.917 | 0.574 | 0.354 | 0.117 |
| champion, Bench(60,160), exact, refit, same checks | 63.19 | 0.744 | 0.917 | 0.574 | 0.356 | 0.117 |
| **champion, Bench(110,360), exact, frozen shape, same checks** | **66.97** | 0.700 | 0.918 | 0.575 | 0.356 | 0.113 |

The champion number is this verifier's own: the same VModel code, part sizes, fitting, pose rules and added checks.
It is not the risley-turret verifier's 75.94 (kit checks + 1 mm radial). Concept_baseline's own conventions give
73.80 on the same bench. Either way the margin is 24-33 points. On its own bench the exact path gives 32.71 against the
fast grid's 32.61 (+0.10): no grid artefact in the claim's favour. The Bench(110,360) refits (osn and champion) were
still running on the farm at commit time (`.cache/osn_verify/b_*.json`); the frozen number is the binding one (lesson
c). On the first try, every exact distance call rebuilt its trees (0.1 s each, ~50 calls per pose), so
the script now batches each pose's samples into one call. The numbers are identical on the fast grid.

What was checked:

1. **DOF.** 3 active (J1, J2, J3), 2 passive slides, both set by closure: s = (R3^T - I) c3, in hub 3's plane. The
   radial part is identically 0, since c1 = c2 = 0 (rest error 0.0001 deg). Measured radial span 0.000 mm and closure
   residual max 0.015 deg on both benches. No undetermined coordinate. **Pass.**
2. **Real size and sampling.** O20 x 12.25 hubs, 8 x 3 straps, neck 16.8 x 8 x 3 with no riser, bridge 6.3 x 8 x 3,
   and carriage B are all present. Member 3 is connected: hub 3 -> neck -> bridge -> carriage B. The stage parts
   (block, carriage A, rail strip) are sampled on a 2 mm grid (1 point / 4 mm2), with walls and edges contact-checked.
   **Added:** the outward faces (crown discs of hubs 1-3, the tops of links 1-2, neck and bridge, the stage box tops)
   are now skin-checked. No contact on either bench. The lowest is hub 2's crown at 1.12 mm (plane 60, elev 150,
   axial -45, under the raised arm). **Pass.**
3. **Pose-taking.** Fold margin 10 deg, slide ranges frozen at +-6.3 / +-7.5 (1 large-bench pose lost to the slide
   range), 10 fps continuity (0 flips), closure < 0.5 deg, part clearance >= 1 mm (min over the poses taken: 1.32 mm),
   jam rule. **Added: link 2 vs member 3** (neck, bridge, carriage B), adjacent via J3. This pair was unchecked; the
   minimum is 3.61 mm (link 2 over the neck at plane -15, elev 75, axial 90), so no pose is lost. **Pass.**
4. **Hardware (lesson a).** Every joint maps to a real part.
   * J1-J3 are the O20 v5 hub (docs/HARDWARE.md), modelled at full size.
   * Along: an inverted THK RSR3M / HIWIN MGN03C (H 4.0, block 8 x 12, rail 3 x 2.6), the block on the cuff.
     Travel +-5.8 is used of a +-6.3 range, so the real rail is 12 + 12.6 + 2 = 26.6 mm. Modelled: a 20 x 20 x 4
     block and an 8 x 4 x 32.6 rail.
   * Across: a second RSR3M / MGN03C, crosswise. Travel +-7.0 of +-7.5, so the real rail is 12 + 15 + 2 = 29 mm.
     Modelled: carriage A 20 x 35 x 4 plus carriage B 20 x 20 x 4.
   * Stack: real 1.5 + 4.0 + 1.0 + 4.0 = 10.5 mm, modelled 13.5 mm. The model is 3 mm taller and larger in
     footprint, so it is conservative.
   * 2 passive translations (the cap). Radial residual 0 on the bench. A real GH-vs-scapula translation's radial part
     must go to the cuff liner (<= 3 mm, stated compliance; not measured here: R10).
   * Soft notes. (i) The real inverted rail sits 2.9-5.5 mm above the cuff base, against 4.5-8.5 modelled, so its
     overhanging ends are 1.6-3 mm lower than modelled. They are not skin-checked at that height. (ii) An RSR3M block
     is rated MA 0.29 N.m (MGN03C 0.7 / 0.5), and the stage carries the arm's orientation torque. That is acceptable
     for the unpowered MVP1 [est] and short for MVP2.
   * No lofts: constant straps and boxes. **Pass.**
5. **Near-touch (lesson d)**, frozen, Bench(110,360) exact. Lowest metal over the poses taken is **0.64 mm** (the
   arm-fixed block, plane -75, elev 45, axial 120). Metal < 1 mm counted as contact: **gap 43.74** (2 poses). Metal
   < 2 mm counted as contact: **68.67** (40 poses). The fit pushes the undersides to the 2 mm target, so 40 of the
   poses taken sit within 2 mm somewhere. The champion on the same rules: 0.02 mm, 71.20 (< 1 mm), 78.34 (< 2 mm).
6. **Overhead (lesson e)**, elevation >= 140, frozen, Bench(110,360) exact.
   * osn: workspace reach **0.25** (7 / 28 poses; 19 lost to the J2 fold, 1 to the slide range, 1 to contact). Clip
     frames 10 / 10 taken. In-band 2-14 0.86 over all taken metal (clip only 0.79), 2-10 0.57.
   * Champion: reach 0.14 (4 / 28), follow 0.40, in-band 0.73.
   * Overhead is where osn's reach is lowest: the J2 fold (window 44-104 deg) cuts 3 in 4 overhead workspace poses.

Issues (not refuting):
* The fast 32.61 is optimistic by 10 points on the large bench. Almost all of it is reach (fold): 136 / 470 poses,
  versus 47 / 220 on the fit bench. In-band holds (0.784), so the shape transfers. The fold is the limiter, as the
  model doc says, and only a morphology change moves it (docs/FINDINGS.md fold frontier: arcs 50 / 50 keep 96 % of the
  workspace fold-free, against a1 / a2 = 40 / 74 here).
* 40 of the poses taken are within 2 mm somewhere. The 2 mm clearance target is the bench's own rule, but a liner
  plus real skin motion will eat that margin.
* The J1 / J2 GH-ray condition is exact only for a fixed GH. The real GH translation's radial part has no slide (R10
  open). The champion has the same exposure, with 0 slides.

**Next:** the 90+ bar (gap <= 27.5) needs about +0.29 reach on the large bench. Re-seed the J1 / J2 / J3 layout from
docs/research/fold/frontier.json (a1 + a2 >= 90, |a1 - a2| small). Check that the hub rays stay in band (proximity
atlas), and re-run this script on the result (frozen, Bench(110,360) exact).

## Fold-frontier seeds (2026-10-16)

**Verdict: the fold frontier does not carry over to this morphology. Best stays k4216 (gap 32.61 fast, 42.59 frozen
on Bench(110,360) exact). Every seed and every CMA stream from it returns to the k4216 basin. The whole-history gate
now passes (9869 tries).** The 2-slide closure theorem makes J1 and J2 hubs on GH rays. On the fold-free layouts, one
of those two rays runs where the deltoid or arm moves under a scapula- or link-1-fixed hub. The fold losses come back
as skin losses.

**Mapping** (`tools/osn_fold_seeds.py`).
* J1 seat ray = the frontier's J1 = bvec(az1, el1); its axis is the ray.
* J3 axis = the frontier's wdir(wd, wa). For b3 > 0, the seat ray is solved by fixed point so the skin-normal-tilted
  axis equals that direction. At b3 0.7 it fails for 14 of 48 configs (error > 5 deg): the skin normal is too far.
* J2 home direction = circle intersection of arc a1 around J1 with arc a2 around the rest-pose J3 axis, both branches;
  its seat ray is that direction.
* neck 13 mm (model default).
* Each config carries its orientation-level fold share, so a loss splits into fold vs geometry.

**Seeds** (Bench(60,160) fast, every model check on; sweep log stages `fold-seed-*`):

| seed set | n | best gap | fold losses | skin losses | what moved |
|---|---|---|---|---|---|
| k4216 itself | 1 | 32.61 | 47 | 2 | - |
| k4216, J1 az / el and arcs moved toward the frontier (J3 kept) | 100 | 32.61 (itself); next 38.51 (az1 110) | 24-55 | 6-30 | el1 55 + arcs 50 / 60: fold 47 -> 24, skin 2 -> 30, contact 0.012 -> 0.153, gap 51.14 |
| frontier top 24 layouts, a1 + a2 85-130, x 2 branches x b3 0 / 0.35 / 0.7 | 144 | **83.95** | 5-15 (median 8) | 34-73 (median 59) | 42 configs close no pose (38 of them b3 0.7) |
| joint frontier (fold-free share AND hub-1 band share, `tools/fold_rayblock.py`), top 8 x 2 x b3 0 / 0.35 | 32 | 72.82 | 6-13 | 31-118 | hub 1 in band, hub 2 out |

Best frontier seed: k4674 (layout a 55 / 55, J1 bvec(108, 32), J3 wdir(70, 0), b3 0.35, branch -1). Reach 0.725 with
only 8 fold poses. But in-band 0.45 and contact 0.186 (39 poses to skin).

In-band 2-14 per part at k4674, then the median over the 102 frontier seeds that close:

| part | k4674 | seed median |
|---|---|---|
| hub 1 | 13 % (median 24.9 mm) | 7 % (31.7 mm) |
| hub 2 | 0 % (31.8 mm) | 1 % (31.8 mm) |
| link 2 | 10 % | 12 % (23.8 mm) |
| bridge | 0 % | 0 % |
| hub 3 | 34 % | 27 % |
| moving rail strip | 73 % | 45 % |

The stage parts hold; the two GH-ray hubs and link 2 between them do not. Branch +1 (J2 anterior-inferior,
el2 -10 to -37) is worse: best 126.79. Branch -1 puts J2 posterolateral (el2 26-41).

**Where the hubs lose band** (`Model.Hneed`: the face height each pose needs; BIG = it would need to rise > 35 mm
above its rest height). Hub 1 and hub 2 rest seats are 45-56 mm from GH.

| layout | hub 1: lift above rest seat, p50 / p90; poses needing > 35 mm | hub 2: same | gap |
|---|---|---|---|
| k4216, J1 bvec(96, 65) | 5.6 / 8.0 mm; 0 | 4.7 / 10.0 mm; 4 | 32.61 |
| FS1 = k4674, J1 bvec(108, 32) | 8.1 / 20.8 mm; 15, all at elevation >= 120 (15 of 39 such poses) | 5.9 / 22.8 mm; 20 (elevation 60-90 with axial +45-75, planes 0-30) | 83.95 |
| FS2, J1 bvec(126, 32) | 9.0 / 20.2 mm; 25 (25 of 41 overhead poses) | 5.5 / 20.6 mm; 16 | 90.25 |
| k4216 moved: el1 55, arcs 50 / 60 | 6.7 / 11.7 mm; 1 | 5.5 / 13.9 mm; 11 | 51.14 |

On the body, the fold-free J1 is near-horizontal and anterolateral: the front of the acromion, over the anterior
deltoid. When the arm rises past 120 deg, the deltoid and the arm itself rise under that hub (*Raise overhead* and
*Comb hair* frames set it). The fitted hub-1 face ends 29-41 mm above its rest seat. Hub 2 (posterolateral, el2 26-41)
rides on link 1, and the abducted, externally rotated arm (elevation 60-90, axial 45-75) passes under it.

**Hub-1 band map** (`tools/fold_rayblock.py` -> docs/research/fold/rayblock.json, with the frontier rows joined). A
20 mm disc on each J1 ray of the frontier grid, need per pose on Bench(60,160): the share of poses ONE hub height
keeps within a 12 mm window (= in band 2-14 mm):

| J1 | rest need | lift p90 / max | one-height band share | overhead (elevation >= 120) |
|---|---|---|---|---|
| k4216 bvec(96, 64) | 46 mm | 4 / 42 mm | **0.982** | 0.902 |
| frontier best bvec(132, 16) | 52 mm | 44 / 124 mm | 0.691 | 0.024 |
| bvec(108, 32) | 52 mm | 26 / 112 mm | 0.809 | 0.122 |
| bvec(126, 52) | 44 mm | 20 / 52 mm | 0.823 | 0.098 |
| bvec(120, 60) (joint frontier) | | 10 mm | 0.927 | 0.610 |

490 of the 1140 J1 directions keep >= 95 % of poses in one band, but few of them are fold-free. The joint frontier
(fold-free ws share AND hub-1 band share) peaks at J1 bvec(120, 60) with arcs 60-65 / 60-65: fold-free 0.956-0.969,
hub-1 band 0.927. Built in osn on branch +1, hub 1 is then in band (100 %, median 8 mm), but hub 2 (on link 1) is out
(31.8 mm, 2-5 % in band). On branch -1, both hubs are out (hub 1 28 mm, hub 2 21-32 mm). Best joint seed: 72.82
(k5579, a 50 / 65, J1 bvec(108, 48), J3 wdir(80, 6), b3 0.35, branch -1).

**CMA** (`tools/concept_cma.py` on the farm, 2 processes per job, popsize 8; objective = the honest bench gap, every
model check on; stages `fold-cma-*`):

| stream | start | sigma | tries | best | where it ended |
|---|---|---|---|---|---|
| K | k4216 32.61 | 0.5 | 785 | 32.61 (no gain) | collapsed on k4216 |
| K2 | k4216 | 1.0 | 921 | 32.61 (no gain) | collapsed on k4216 |
| FS1 | frontier k4674 83.95 | 0.8 | 1073 | 42.65 (k7533) | J1 bvec(101, 63), J2 bvec(30, 43) |
| FS2 | frontier 90.25 | 0.8 | 777 | 37.62 (k8337) | J1 bvec(105, 66), J2 bvec(28, 51) |
| FM1 | k4216 move az1 110 38.51 | 0.5 | 553 | 33.48 (k8860) | J1 bvec(106, 66), J2 bvec(15, 58) |
| FM2 | k4216 move el1 55, a 50 / 60 51.14 | 0.5 | 961 | 32.94 (k9587) | J1 bvec(96, 65), J2 bvec(12, 54) |

The two frontier starts begin with J1 elevation 32 and climb back to 63-66, out of the fold-free region. The bench's
own metric prefers 47 fold poses with both hubs in band (98-100 %) to 8 fold poses with the hubs 25-32 mm up. Whole
history in order (9869 tries): best gained 0.0 score points over the second half and 0.0 over the last third, top 5
within 0.03: **converged**.

**Frozen, Bench(110,360) exact (lesson c).** The best shape is k4216, so its frozen big-bench number is the
verifier's, measured with the verifier's script on the same protocol: **v_gap 42.59** (reach 0.611, follow 0.964,
in-band 0.784, contact 0.021). Red team (section above):
* The pose that jams: 136 of 470 poses fold; overhead workspace reach 7 / 28.
* The point that pinches: 0.64 mm, the arm-fixed block at plane -75, elevation 45, axial 120.
* Near-touch: metal < 1 mm counted as contact gives 43.74.
* Overhead (elevation >= 140): reach 0.25, in-band 0.86.

The runner-up CMA shapes and the best fold seed were worn frozen on the same bench (`.cache/osn_fold/big_k*.json`):
Verifier script, task `osnbig_frozen`, on the farm. The shape is fit on Bench(60,160) fast, then frozen; checks
include crowns and strap tops, link 2 vs member 3, and near-touch.

| config | fast gap | **frozen big gap** | reach | follow | in-band 2-14 | contact | fold / contact poses (of 470) | min metal-skin | gap, metal < 1 mm as contact | overhead >= 140: ws taken, in-band |
|---|---|---|---|---|---|---|---|---|---|---|
| k4216 (verifier, above) | 32.61 | **42.59** | 0.611 | 0.964 | 0.784 | 0.021 | 136 / 7 | 0.64 mm | 43.74 | 7 / 28, 0.86 |
| k9587 (FM2) | 32.94 | 43.01 | 0.611 | 0.964 | 0.780 | 0.021 | 136 / 7 | 0.69 mm | 44.16 | 7 / 28, 0.85 |
| k8860 (FM1) | 33.48 | **42.39** | 0.611 | 1.000 | 0.783 | 0.018 | 133 / 6 | 0.10 mm (plane -60, elev 60, axial 105) | 49.07 (13 poses) | 7 / 28, 0.87 |
| k8337 (FS2) | 37.62 | 43.84 | 0.639 | 1.000 | 0.743 | 0.020 | 123 / 7 | 0.11 mm (hub-2 crown 0.84 mm, Raise overhead elev 150) | 49.75 | 7 / 28, 0.78 |
| k5579 (best joint fold seed) | 72.82 | 83.64 | 0.628 | 0.982 | 0.517 | 0.181 | **62 / 74** | 0.09 mm | 90.13 | **3 / 28 (4 fold, 21 contact)**, 0.43 |

The ranking by the frozen big bench is the same basin within 1.5 gap. k8860 is 0.2 better than k4216 there, but
13 of its poses come within 1 mm (gap 49.07 counted as contact, against k4216's 43.74). That is within the
optimism of the fit, so k4216 stays the pick.

The fold-free seed shows the mechanism on the big bench. Its fold losses halve (136 -> 62), but 74 poses go to
contact. Overhead, 21 of 28 workspace poses are lost to contact instead of 19 to the fold: the poses move from the
fold column to the skin column.

**New knowledge.**
1. In the exact 2-slide subfamily, J1 and J2 are hubs on GH rays. Their rays must avoid the moving deltoid and arm:
   one hub height must keep >= 90 % of poses in band. That pulls J1 up over the acromion (el 60-66), which is the
   opposite of the fold frontier (el 16-36). The fold limit and the band limit pull the J1 axis in opposite
   directions, and k4216 sits at the trade-off. Nothing better came from 1706 restarts at k4216 (sigma 0.5-1.0) or
   3364 from frontier seeds and moved k4216 seats.
2. A fold-free layout keeps hub 1 in band only at J1 bvec(120, 60) (arcs 60-65). Hub 2, on link 1, then swings over the
   abducted arm.
3. A 3R whose J1 / J2 metal sits on their axes cannot use the fold frontier on this body. The 90+ bar needs a
   morphology where J1 / J2 rotate about GH rays without metal on those rays: an arc guide or remote-centre carriage
   for J2 (seed-arc-rails, scapular-race-j2-carriage, meridian-goniometer families), whose track can follow the skin
   anywhere on the J2 circle. Moving J1 / J2 off GH needs the third (radial) slide: 3 passive translations, not
   allowed.

## Files

* model: docs/concepts/models/offset-skin-normal-3r.py (`check`, `kin`, `redteam [--png]`; built on
  seed-offset-3r-slides.py's VModel; ~3-8 s per configuration on the fast grid)
* sweep log: docs/concepts/sweeps/offset-skin-normal-3r.json (in order; `stage` = local-check, coarse-farm, cma-A/B/C,
  cma-L-local, control-b3-*, cma2-D/E/F, cma2-M-local, fold-seed-k4216moves / -frontier / -joint, fold-cma-K / K2 /
  FS1 / FS2 / FM1 / FM2; configurations where no pose closes are logged as gap 275)
* fold seeds: tools/osn_fold_seeds.py (frontier layout -> osn seats); hub-1 band map: tools/fold_rayblock.py ->
  docs/research/fold/rayblock.json (its frontier_rows = frontier.json rows + j1_ray_free (one-height band share) /
  j1_ray_free_overhead / j1_lift_p90)
* sketch: docs/concepts/img/offset-skin-normal-3r.png (rest and highest pose taken, k4216)
