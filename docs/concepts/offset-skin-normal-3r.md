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
| **CMA stream C (697 tries, collapsed) - best, k1908** | **35.65** | **87.04** | 0.713 | 1.000 | 0.748 | 0.383 | 0.017 |
| control at k1908's seats, b3 0 (J3 on the GH ray) | 42.92 | 84.39 | 0.681 | | 0.713 | | 0.023 |

Best configuration (k1908): J1 seat bvec(105.3, 65.6), J2 seat bvec(25.9, 51.5) (both on GH rays: link 1 40.5 deg,
link 2 67.5 deg), J3 seat w_dir(77.0, -8.4) tilted b3 0.34 toward the skin normal (27.9 deg between the GH ray and the
skin normal there; the J3 line misses GH by 11.0 mm), neck 18.6 mm; slide travel used +-9.7 along / +-11.0 across
(ranges 10.2 / 11.5); radial drift 0.000 mm. Faces f1 49.6, f2 61.2, f3 74.8 mm. In band 2-14 per part: hub 1 99 %,
hub 2 97 %, link 1 90 %, rail block 89 %, link 2 82 %, moving rail 69 %, neck 62 %, carriage A 62 %, hub 3 51 %
(median 13.9 mm), bridge 12 % (16.9 mm). b3 ladder at these seats: 0 -> 42.92, 0.1 40.76, 0.2 41.80, 0.3 38.82,
0.4 37.49, 0.5 45.36 (slide travel then exceeds what the stack can carry in band).

**What the morphology buys.** At the best seats, tilting J3 toward the skin normal and letting its line miss GH by
~11 mm buys 7.3 gap (42.92 -> 35.65): fewer J2-fold poses (46 -> 43, the J3 direction moves) and hub 3 / stage lower.
The re-tuned J1 / J2 seats (a spherical-family freedom) are worth the rest of the gain over the baseline. The
2-slide exact cuff scores level with the 3-slide skin-normal-hubs-selfaligning (35.86 on the same bench, its radial
slide 6.7 mm): **the radial slide is not needed** - it buys nothing measurable and adds an unguided stroke (the
verifier's open hole in the seed) and 0.5 + R_r mm of stack.

## Red team (best configuration, k1908)

* **The pose that jams.** 43 poses are lost to the J2 fold (>= 10 deg margin) - across-the-body 12 of 36 lost, overhead 16
  of 41 (15 fold + 1 skin; Raise overhead elev 124-150, plane 30), behind-the-back 3 of 19. The fold window is
  |a1 - a2| + 10 = 37 deg to a1 + a2 - 10 = 98 deg of the J1-J3 axis angle, which spans 13-156 deg over the bench
  (5-95 % 30-124 deg): 20 poses fall below, 27 above (measured at k3). Margin sensitivity at k3: 10 deg 173 / 220
  poses close, 5 deg 183, 0 deg 191. No offset or slide can move this: the orientation IK is the spherical one.
* **The point that pinches.** Over the poses taken the lowest metal is link 2 at **0.01 mm** (plane 60, elev 165,
  axial -90), hub 1 at 0.52 mm (plane 45, elev 165) and 0.55 mm (plane 135, elev 135), hub 2 at 0.55 mm (plane 0,
  elev 75, axial 45), rail block 0.70 mm (plane -90, elev 45, axial 120), hub 1 0.76 mm in the *Raise overhead*
  clip top frames. In those top frames hub 2 sits in the gap UNDER the elevated arm (the outward ray through hub 2
  re-enters the arm: needed height unbounded, the pose was dropped from the fit, yet the metal clears by >= 0.76 mm,
  so the bench takes it) - a closing pinch between arm and acromion.
* **The optimistic number.** The bench takes a pose at metal >= 0 mm. Counting a taken pose as contact when its
  metal comes within 1 mm: gap 42.49 (8 poses, 3 clip frames); within 2 mm: 47.26 (12 poses). The 35.65 leans on
  ~7-12 points of near-contact that CMA pushed the fitted undersides into; the verifier should re-measure on
  Bench(110,360) exact where the envelope includes more poses.
* **Closure and slides.** Rotation residual max 0.015 deg; radial drift 0.000 mm over 514 clip + workspace poses (the
  subfamily is exact by construction); both slides set by closure, no flips between 10 fps clip frames; 0 part jams
  with the inverted guide (55-103 with the seed's arm-fixed rail).
* **Not modelled.** The inverted guide's rail overhangs carriage A by S_a (10 mm) at each end, cantilevered on a
  20 mm carriage (stiffness not checked); the slides' end stops and the user's sensing are not modelled; the bench has
  no GH translation, so the slides' R10 benefit (absorbing real GH-vs-scapula motion) is invisible here and the 2-slide
  cuff would have to absorb that translation's radial part too (it cannot: a real arm would need the third slide or
  soft-tissue compliance for R10 - test it on the R10 judge before choosing between 2 and 3 slides).
