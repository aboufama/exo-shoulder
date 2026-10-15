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

## Results

(written at the end of the sweep)
