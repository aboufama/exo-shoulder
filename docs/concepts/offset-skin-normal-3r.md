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

## Files

* model: docs/concepts/models/offset-skin-normal-3r.py (`check`, `kin`, `redteam [--png]`; built on
  seed-offset-3r-slides.py's VModel; ~3-8 s per configuration on the fast grid)
* sweep log: docs/concepts/sweeps/offset-skin-normal-3r.json (in order; `stage` = local-check, coarse-farm, cma-A/B/C,
  cma-L-local, control-b3-*, cma2-D/E/F, cma2-M-local; configurations where no pose closes are logged as gap 275)
* sketch: docs/concepts/img/offset-skin-normal-3r.png (rest and highest pose taken, k4216)
