# rail-elbow - J2 as a curved rail on link 1, link 2 shrinks to a carriage beside the arm-end hub

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the rail for what it is: the
   locus, in link 1, of every place the carriage will ever be. All of it is metal in every pose, so the rail's radius is
   set by the worst skin under ANY part of it in ANY pose, not by the deltoid cap the carriage sits on. Measure that
   per rail station before believing the "constant radius over the round cap" argument. (b) Cut the rail to the carriage
   travel actually used (plus half a carriage, an end stop and a fixing tab) instead of +-15 deg, and attach strap 1 at
   the rail END (a carriage that grips both rail edges cannot pass a mid-span support - the spec's mid-point strap is
   wrong). (c) Pick the side of the hub the rail runs on (d_off sign) and its polar offset so the rail lies over the
   lowest skin, and if the constant radius is the limiter, try the variant that removes it: a cam track (radius varying
   along the rail, the carriage's radial position fixed by the track, so no undetermined coordinate).
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (the cached
   grid and the exact libigl path), the fit-clip frames in time order (B.clip_order, with the motion slerped between
   bench frames for continuity), the everyday-workspace envelope. The skin-motion map is a digest; it is only used to
   pick the low-motion W candidate (112, -15) the spec names.
3. **Methods and tools.** The shared kit (tools/concept_kit.py): exact two-circle closure of the spherical 3R
   (residual reported), K3 march for every skin-facing sample, flat O20 hubs with the 12.25 mm stack, 12 x 3 straps
   with the 60 deg climb limit, K7 neck to BOTTOM, dense K2 continuity along the slerped motion, K6 sampled-volume
   collisions; the rail + carriage as one constant-radius member (a rigid carriage on a rail about p2 can only run on
   a circle: constant polar angle AND constant distance from GH).
4. **What, other than me, shows the number is right.** tools/concept_bench.py on Bench(60, 160) (same poses and metrics
   as every concept, champion 68.93), the kit's audit (hub size, sampling density, pose locality), the swarm's
   adversarial verifier, and the red-team pose list below (rest, overhead, across-the-body, behind-the-back, the pose
   that sets the rail radius).

## Morphology and model

Topology (scapula handler -> user's cuff), every joint axis through the GH centre: base -- **J1** O20 hub, axis b in the
scapula -> **link 1** = strap 1 (12 x 3) + a circular **rail** (8 wide x 5) at polar angle alpha = a2 + d_off about the
J2 axis p2 (p2 fixed in link 1 at a1 from b), at one distance from GH; no metal at p2's pole -- **J2** = a rolling
carriage (20 x 16, 9 radial) on the rail, its azimuth about p2 is the joint value -> **link 2** = carriage + a bridge
strap (12 x 3) to the J3 upper plate -- **J3** O20 hub, axis W in the humerus -> arm-end plate + neck (14 x 6) to
BOTTOM's bar. q1, q2, q3 all follow from the two-circle closure of b and W on branch sigma: **3 active DOF, 0 passive**.

Model: `docs/concepts/models/rail-elbow.py` on the shared kit (K3 march, flat O20 hubs with the 12.25 mm stack, K5
straps, K7 neck, dense K2 continuity along the slerped motion, K6 collisions). `python3 ... check [k=v ...]`,
`sweep tele2|refine|cam|rigid`. Task API `metal(pose, B, params)` after an evaluate on the same bench.

Spec changes (each stated, the first two measured):
* **strap 1 joins the rail at its END**, on a 12 mm fixing tab beyond the end stop, not at its mid-point: a carriage
  that grips both rail edges cannot pass a mid-span support. Strap 1 is exempt from K6 against the rail only within
  12 mm of that tab (pseudo-joint L1r); the carriage never comes within 13 mm of it.
* **rail extent** = the carriage travel over the closing bench poses (central share `cov`, + `tmarg` 5 deg) + half a
  carriage + a 3 mm end stop at each end (+ the tab), instead of +-15 deg. Computed in a design step outside `build`
  (so `build` stays pose-local); the J2 range is the rail (poses outside it are not taken).
* humerus axes in the band frame (`F.HG`), as the kit and the champion (the spec's RH is 12 deg off, KIT.md).
* K6 exemptions beyond the kit's shared-joint rule, all parts of one rigid body or the rail joint itself: bridge vs the
  rail member (the bridge is bolted to the carriage and meets the rail only at the carriage); in the variants, rail
  stage 1 vs stage 2 (the telescopic joint), carriage vs radial guide and rail vs carriage (the cam joint). Implemented
  by `collisions_same_body` (the kit's own pair test run on every other pair).

Variants (the spec's rigid rail, then the variants that remove its measured limiter):
* `tele=0` **rigid rail** (spec): one rail over the whole travel, rail + carriage overhang strips at ONE radius (kind
  `cap`, the spec's rho_T - 5).
* `tele=1` **2-stage geared telescopic rail**: stage 1 fixed on link 1 from the anchor (tab) over half the travel; stage
  2 rides beside it (8 + 8 mm side by side), driven at half the carriage travel by a cable loop (a determined
  coordinate, no sag); the carriage (8 + one 4 mm overhang on the hub side) rides stage 2. Metal exists only from the
  anchor to just past the carriage. Each stage is still a circle about p2 at one radius (rigid sliding arc).
* `cam=1` **cam-track rail**: one rail whose radius follows the skin per station (rigid section: max across its width;
  slope <= `cam_climb`), the carriage on the track per pose, link 2 taking the radius change in a radial guide (6 x 6
  foot beside the carriage reaching down to the carriage's lowest radius, height = the carriage's radial range + 9).
  Implemented by wrapping the kit's `fit_profiles` / `member_points` (the carriage's points are per pose).
* per-member underside quantiles `q_rail`, `q_hub3`, `q_bridge` (the rest at the global `q`): the rail can let its
  worst poses become contact poses without lowering every other member.

## Results (Bench(60, 160), fast grid cache, kit checks on: K3 march, dense K2, K6; champion spherical 3R = 68.93)

65 bench configurations (docs/concepts/sweeps/rail-elbow.json, in order; stages coarse / tele2 / refine / cam / rigid /
final-rlay). Entries 0-63 lay the rail parts out at the kit's 70 mm reference radius; at the fitted 125-145 mm that is
4.3 mm sampling, sparser than 1 pt / 4 mm2, which FLATTERS a member that is out of band. The best entry (k55, 69.51) was
therefore re-run with the rail parts laid out at their fitted radius (`r_lay` 142.5, 2 mm samples there, audit clean):

| variant | best config | gap | reach | follow | in-band 14 | in-band 10 | contact |
|---|---|---|---|---|---|---|---|
| **telescopic rail, honest sampling (the claim)** | champion axes, d_off -40, q 1.0, `r_lay` 142.5 (k64) | **71.15** | 0.906 | 1.000 | 0.189 | 0.117 | 0.000 |
| telescopic rail, rail sampled at 70 mm (flattering) | same (k55) | 69.51 | 0.906 | 1.000 | 0.205 | | 0.000 |
| rigid rail (spec), q 1 (check runs) | champion axes, d_off -25 / +20 | 77.69 / 92.22 | 0.875 / 0.825 | 1.0 / 0.917 | 0.17 / 0.17 | | 0.024 / 0.088 |
| rigid rail (spec), q 0.93 | d_off -25 / +20 (k62, k63) | 89.4 / 90.4 | 0.75 / 0.78 | 1.0 / 0.92 | 0.28 / 0.27 | | 0.12 |
| cam-track rail, q_rail 0.95, slope 45 deg | d_off -35 (k61) | 110.5 | 0.60 | 0.85 | 0.425 | | 0.230 |
| spec seed A (r18 s1392 #1 axes) | telescopic, d_off -25 (k44) | 75.1 | 0.95 | 1.0 | 0.158 | | 0.009 |
| spec seed B (W at the low-motion spot 112, -15) | telescopic (k53) | 85.5 | 0.91 | 1.0 | 0.064 | | 0.019 |

Best (k64): b az 2.43 el 80.68, a1 76.90, a2 66.75, W (86.33, 21.83) in the band humerus frame, sigma -1, 10 deg fold
margin; rail at polar alpha = a2 - 40 = 26.7 deg about p2, carriage travel 139 deg (129 over all closing poses + 5 deg each side), 2-stage
telescopic rail (stages 300 + 292 samples = 44 % of all metal samples), stage radii ~125-145 mm; closure residual 0.0,
min margin 10.1 deg, 0 flips, 0 collisions; Ti mass 152 g (177 g with 5.5 mm straps). In band 2-14 per member: hub 1
1.00, hub 3 0.15, strap 1 0.31, rail stage 1 **0.00**, stage 2 **0.00**, bridge 0.02, neck 0.42.

### Measured limiter
* **The rail is metal over the whole J2 travel in every pose.** The J2 travel of this 3R over the closing bench poses is
  139 deg (the b-W angle sweeps ~120+ deg over the workspace; J2 must follow it). Per pose, the rigid rail's need
  (champion axes, d_off -25, 151 mm of rail): p50 83 mm, p90 123, p95 208, max > 220 (some rail stations point INTO the
  body for 220 mm - the march finds no clearance). Split by where the station is in that pose: the stations between the
  rail's fixing end and the carriage need p50 62 / p90 69 / max 86 mm; the carriage's own station 59-76 mm; all the
  excess comes from the part of the rail BEYOND the carriage (p95 208, max > 220): the places the carriage will occupy
  in other poses lie, in this pose, over the arm, the armpit or the trunk. The worst poses: abduction 90-105 deg in
  the scapular plane (axial 0-15) and the arm hanging in front (plane 30, elev 3-15, axial -30) for d_off +20.
* **A rigid carriage forces a circle about p2: one radius over the whole rail.** Even after removing the beyond-carriage
  part (the 2-stage telescope), each stage is a rigid arc sliding along itself, so it has one radius = the max over its
  stations and poses: 116-145 mm here, over skin at 50-60 mm. Rail parts in band: <= 0.03 in every rigid / telescopic config with contact < 5 % (up to 0.19 only at a global q 0.9 that loses 15-50 % of the poses, gaps 100-155).
  With 44 % of the samples on them, in-band 14 is capped near 0.56 even if every other part were perfect; measured 0.19.
* **The variant that removes the constant radius (cam track) moves the cost into contact.** With the radius per station
  (quantile 0.95, slope <= 45 deg), the rail is 45 % in band, the carriage 59 %, the guide 70 % - the idea works where
  it is taken - but the far stations still run into the body in 23 % of the poses (contact 0.23, reach 0.60): the beyond-
  carriage problem again, now per pose instead of in the radius. A cam AND a telescope are incompatible (a rigid sliding
  stage cannot ride a varying-radius track).
* Lowering the rail quantile alone (q_rail 0.95-0.98) never helped: rail parts stay ~0-3 % in band and contact or
  collisions rise (k27-k53). The spec's W seed B (the low-motion spot 112, -15) is worse than the champion's W: hub 3 and
  the neck are never in band there (0.00).

### Red team (best config k64)
* Rest (57 poses with elevation < 20): 57 / 57 taken. Overhead (elevation >= 140, 17 poses): 14 taken; the 3 lost are
  closure failures (fold margin -5.6 to -18.5 deg) at elevation 150 in planes 90-120 with axial -135 - the 3R's own
  singularity, not the rail. Across the body (plane >= 90, elevation >= 45): 42 / 48, the 6 lost all closure failures
  (axial -135). Behind the back (plane <= -30 or internal rotation >= 60 below 50 deg): 29 / 34, the 5 lost all closure
  failures (plane -90 / -60 with axial 105-165).
* Where it pinches (closest metal over taken poses): rail stage 1 at 2.0 mm and stage 2 at 2.2 mm in pose 90 (plane -15,
  elev 75, axial -45: abduction just behind the scapular plane with internal rotation) - this pose sets the rail radius;
  the neck at 2.0 mm at elev 165; strap 1 at 2.05 mm at elev 165 (plane 45). The jam: no pose is lost to the rail travel
  (the travel covers every closing pose); every lost pose is a 3R fold.
* Not modelled (would make it worse): the stage-2 cable loop and its pulleys, roller housings on the stages, the
  cantilever stiffness of 140 deg of rail; the K6 same-body exemptions listed above.

### Verdict
**Dead** (best honest gap 71.15 vs the champion's 68.93; the spec's rigid rail 77.7-92.2). Not worth a GPU sweep:
the limiter is structural, not a parameter - a rail that realises the middle joint of a spherical 3R must be metal
over the whole J2 travel (~140 deg) on link 1, and a rigid carriage makes that metal a circle about p2 at one radius;
the two variants that remove one half of the limiter each (telescope: the beyond-carriage part; cam: the constant
radius) leave the other, and they cannot be combined. The bet ("a constant-radius band over the round deltoid cap stays
in band") holds only for the 20 mm under the carriage.

### What this predicts beyond this morphology
* Any rigid guide (rail, track, arc) that carries a moving contact is metal over the UNION of the contact's positions
  in every pose, so its skin-facing height is set by the worst skin under any part of that union in any pose. It can be
  in band only if that union sits over one skin patch that moves with the guide's frame (e.g. a track fixed on the
  scapula over scapula skin: scapula-halo-track, 80 % in band) - never when the guide is on an intermediate link whose
  contact sweeps over the arm and the trunk (this rail; seed-arc-rails' J2 rail at 171 mm). Expect the same of
  trombone / arc-chain / oval-track concepts whose guide lives on link 1.
* For a guide on link 1, the useful number to compute before any modelling is the per-pose requirement of the guide
  BEYOND the contact (here p95 208 mm vs 69 mm before it): it is the part a telescope removes and a cam cannot.
* W at (112, -15) (the "low-motion" deltoid spot of the skin-motion map) puts the J3 hub and the neck out of band on
  this bench (0.00 both); the champion's W (86, 22) stays the better arm-end spot for hub-based 3R variants.

## Audit

Adversarial re-check of the death (Bench(60,160), fast cache, same model file).

- Reproduced the claimed best exactly: gap 71.15 (reach 0.906, follow 1.00, inband14 0.189, contact 0), audit clean,
  residual 0, 0 flips, 0 collisions.
- No modelling bug or convention error found: closure, march, K2 continuity, K6 (same-body exemptions limited to parts of
  one rigid body or the rail joint itself), O20 hubs and sampling all go through the shared kit as in the baseline.
- Parameter range: the sweep stopped at d_off -45. Moving the rail closer to the J2 pole helps a little:
  d_off -48 / -50 / -52 read 73.19 / **69.43** / 69.73 (sweep entries k120-k122, honest, audit clean; best: inband14
  0.206, inband10 0.131, reach 0.906, follow 1.00, contact 0). Beyond -55 the strap and stage-2 sampling turns sparse
  (audit fails) and the gap rises again (73.2 at -60).
- Member split at d_off -50: rail 0.00 and stage 2 0.00 in band (their closest point is 122-135 mm from GH, over skin
  at 50-60 mm), bridge 0.01, hub3 0.15, neck 0.42, strap1 0.30, hub1 1.00.
- Verdict: **death stands**. The corrected best (69.43) is still behind the champion's 68.93, and the reason is the
  one claimed: the rail parts are metal over the whole J2 travel at one radius about p2 and are never in band in any
  pose set; moving the rail toward the pole does not bring it nearer the skin.
