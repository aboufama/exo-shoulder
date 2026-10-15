# Sliding-rivet pauldron (hubless nested plates, follower-in-slot joints)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Check that two rollers in two coaxial
   slots really make a revolute (they do only if the rollers are neither on one meridian nor 180 deg apart: the spec's
   layouts leave a first-order slide), give every roller its real stack (an O8 x 4 roller cannot hide in a 2 mm plate:
   it protrudes and needs a retaining flange, and J1's flanges face the skin), and treat the joint radius as free per
   plate (posts on L1 so the band sits at its own radius instead of lifting the whole top stack). Then ask the real
   question of the family: a plate that turns about an axis through GH keeps every point at a fixed radius, so it must
   clear the highest skin it sweeps over - plates make that worse than straps (more area under them), unless each
   plate's skin is itself nearly spherical about GH over the poses it rides.
2. **Rawest material.** The posed render skin of every bench pose (B.skin / B.dist: the radius of the local outer skin
   along every sample ray, pose by pose, not a digested envelope), the fit-clip frames at 10 fps for continuity, and the
   skin-motion map (pipeline/conformal/analysis/skin_motion_map_14.json) to read how far the skin under each plate rises
   and falls relative to GH across the range.
3. **Methods and tools.** Spherical 3R closure (two-circle intersection, the band evaluator's convention), exact
   per-sample skin radii by sphere tracing on the bench's signed-distance field, plate outlines from the slot spans
   (+ rim), member-to-member interference by point-in-solid tests in member coordinates, branch-flip test on every
   10 fps frame, coarse -> one-at-a-time -> local-random sweep on Bench(60, 160) (cached SDF grids).
4. **What else shows the number is right.** The common bench (tools/concept_bench.py, same poses / metrics as the
   3R baseline 68.93), the adversarial verifier that re-runs the model, and a red-team pose list (rest, overhead,
   across the body, behind the back + the worst pose for each limiter) with the per-pose reason a pose is not taken.

## Model (docs/concepts/models/sliding-rivet-pauldron.py)

Spherical 3R (axes b, p2, W through GH, two-circle closure on the design branch) built from 2 mm Ti spherical plates:
S cap (S-fixed, about b), L1 guide disc, L2 band (circle at polar A1 about p2) + arm-end disc about W + ramped strap,
H saddle + BOTTOM stub (25 deg, the baseline's neck convention). Every joint is two O8 x 4 needle followers (O10 x 1.5
flange) in 8.2 mm slots; rollers, flanges and posts are modelled at real size and checked for interference
(non-adjacent members >= 1 mm). Taken = closure + every roller inside its slot + no 10 fps branch flip along each fit
clip + no interference + no metal inside the body. Plate radii: percentile `pct` over the valid poses of the per-pose
maximum local-outer skin radius under the plate + 2 mm (pct 100 = clear every pose; lower = trade contact for
in-band).

Spec corrections (all in the model): (1) the spec's follower layouts (180 deg apart on J1/J3, one meridian on J2) leave
a first-order slide - a roller only blocks motion normal to its slot, so the two rollers must sit at azimuths neither
equal nor opposite (here 90 deg / D2 apart); (2) an O8 x 4 roller protrudes from a 2 mm plate and needs a flange,
J1's flanges face the skin; (3) the band can stand on posts (`top=post`) instead of lifting the S cap and L1 with it;
(4) the spec's 40 mm stub along a sphere about GH runs into the arm (rays near the humerus axis never leave the arm):
cut to the baseline's 25 deg; (5) a J3 / J1 slot spanning > 330 deg becomes a full ring track (annulus, island
dropped) - the workspace's axial rotation needs 355-372 deg of J3.

## Results (Bench(60, 160), fast path; 40 configurations in docs/concepts/sweeps/sliding-rivet-pauldron.json)

Best: k 35, gap 177.0 (baseline 3R 68.93): reach 0.469, follow 0.583, in-band 2-14 0.337, 2-10 0.160, contact 0.409.
Params: r20 axes (b_az 2.43, b_el 80.68, w_d 86.33, w_az 21.83, A1 76.90, A2 66.75), pct 80, cov_ws 0.95, top post,
n1 1, n3 1 (ring track), s1 0. Radii: S cap 59.5, band 152 (!), saddle 65.3 mm.

**Measured limiter: the band's tail.** The L2 band slides through L1's rollers at b, so it keeps one radius about GH
and must store the change of the b-W angle (phig 40 -> 120 deg over the fit clips, ~80 deg) past b. Per band-azimuth
bin, the local-outer skin radius is 43-60 mm on the part between W and b but >= 150 mm (inside the neck / trapezius
fold, or inside the elevated arm) on the tail in every pose with phig < ~70 (elevation 120-135 deg, also plane -30 /
elev 60). Per-pose band requirement: p50 99 mm, p80 >= 150 mm. So the band either sits at 152 mm (out of band
everywhere) or cuts the neck / arm in 25-40 % of poses.

Variants tried to remove it (all in the sweep): trimming the J2 range (trim2 25-30: shorter tail but 53 frames lost to
the J2 limit), moving the J2 rollers onto an L1 arm toward W (s1 20-50: the band shifts toward W, but the strap /
L1 arm then hits the stub, saddle and arm-end disc: 100+ interference poses), post-mounted band (S cap back to 56-61
mm), ring tracks for J1 / J3, the champion vs the bench baseline's axes. None gets under 177.

## Red team (own best config)

- Jam: elevated poses with phig 61-69 (fit clip plane 61 / elev 123, workspace plane 75 / elev 135): the band tail
  past b enters the neck - the pose is lost (contact) at any pct < 100.
- Pinch: the J2 posts / arm-end disc pair (`interference armend/j2post0`, 7 poses) where the band end passes over the
  saddle region when W comes close to b.
- Range: J3 needs a full ring track to cover the workspace's axial rotation (355 deg); J1 slot 311 deg.

## Verdict

Dead - not worth a GPU sweep. Plates at one radius about GH are a worse fit than the baseline's straps (more area at a
radius set by the highest skin), and the trombone layout's tail is intrinsic: rigid plates cannot store ~80 deg of
excess band travel anywhere that is not over the neck (past b) or over the arm (past W). What would beat it is a member
that is not one-radius over its travel (flexible / telescoping in two stages with their own radii, or a chain whose
middle axis is not swept over the trapezius).
