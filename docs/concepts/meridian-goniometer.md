# meridian-goniometer - J2 as an arc rail beside the arm's elevation path (no J2 hub)

Model: `docs/concepts/models/meridian-goniometer.py` (shared kit). Sweep: `docs/concepts/sweeps/meridian-goniometer.json`.
Row: `docs/concepts/rows/meridian-goniometer.json`. Bench(60, 160), fast grid cache, K3 march, K2 dense, K6 on.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Notice that the spec's rail cannot be
   skin-fitted along its length: a carriage of 30-50 deg of arc is a rigid body, so its track must be a true circle
   about the virtual axis a2 (any radius varying with phi breaks the rotation about a2). The free choice is WHERE that
   circle sits (its cone angle alpha off a2, the side, the radius fitted on the skin), not its shape. Then decouple the
   rail from the pointer: the virtual-axis rail replaces a J2 hub in ANY spherical 3R, so try it both on the spec's
   pointer + humeral C-slide (whose J3 twist window is the measured reach ceiling 0.50 of pointer-cslide) and on the
   general 3R whose third axis is an arm-fixed hub (the champion's hub 2 floats at 105 mm and is never in band - the
   rail is the lever that removes exactly that part). Let the carriage lead or lag the arm (dphi) so it sits on the
   lowest skin, and cut the rail's q2 range from the posed data (a share of the closing poses), not from a guess.
2. **Rawest material.** The posed skin of every bench pose through the bench's signed-distance grid (the rail and
   carriage radii are K3-marched per sample per pose, the max taken because the track is one circle), the scapula and
   humerus rotations of the 60 fit-clip frames and 160 workspace poses (the q2 window and the carriage's path come from
   them), and the proximity atlas per-direction ceilings (where a scapula-fixed vs a swing-frame part can be in band).
3. **Methods and tools.** tools/concept_kit.py (K1 closure, K2 dense continuity on values and axes, K3 march, K4 hubs,
   K5 straps + `over`, K6 collisions, K7 neck, audit), 'cap' members for the circular rail and carriage (one radius:
   a surface of revolution about a2), pointer-cslide's band/shoe/neck for the spec's J3, Sobol coarse sampling then
   CMA-ES (pycma) on the cloud CPU farm (tools/cloud_run.py sweep) until the convergence gate passes.
4. **What shows the number is right besides me.** The bench (it scores the metal I hand it), the kit audit (sample
   density, pose locality, honest flag), the adversarial verifier re-running the best params, and a red-team list:
   rest, overhead abduction 150-160, overhead flexion, across-body (plane >= 110), behind-the-back (extension +
   internal rotation), the pose at each end of the rail's q2 window, the rail's sweep over the head/neck at large q1,
   and the bridge crossing the rail.

## Kinematics as built (spec fixes in **bold**)

- J1: O20 hub on a1 = S-fixed `bvec(az, el)`. J2: the virtual axis a2 = K1 closure(a1, p3, A1, A2, sigma); A1 = A2 = 90
  with p3 = the humerus axis is the spec's pointer (a2 = unit(a1 x t)). q2 = the angle about a2 from a1 to p3.
- **The rail is a circle about a2, not a skin-following curve.** The spec's Rr(phi) = ENV + 2 would move the carriage
  radially as it travels, so link 2 would not rotate about a2 (the 30-50 deg shoe is rigid). The rail is a spherical
  zone (one radius Rr, a surface of revolution about a2) between cone angles alpha +- 13 mm about side * a2, over the
  q2 window + dphi +- (Lc/2 + 3 mm stop); Rr = max over its samples of the K3 march (quantile q over the fit poses).
  26 x 6 mm rail, carriage Lc deg x 26 mm at Rr + 6.15 (0.15 running gap), 3 mm thick, centred at q2 + dphi.
- J3, two variants: `j3='cslide'` = the spec (pointer + pointer-cslide's humeral C-slide: band, shoe, neck, its
  fitted twist window, reused from docs/concepts/models/pointer-cslide.py); `j3='hub'` = **the rail on a general
  spherical 3R** (J3 an arm-fixed O20 hub on `HG(wdir(wd, wa))`, the K7 neck) - the rail is meant to replace the
  champion's floating hub 2, so it is tested there too.
- Root (12 x 3 strap hub 1 -> the rail's end nearest a1, one part with the rail), bridge (12 x 3 strap carriage ->
  J3, over the rail, root and neck). Straps and rail laid out at the rail's own fitted radius (fixed point), so every
  member is sampled <= 4 mm (audit clean).
- **Honesty flag added**: a rail sample whose K3 march finds no skin clearance within 220 mm in a fit pose gets the
  kit's 400 mm fallback; a rail "fitted" there is not a design (it passes through the body), so such configurations
  are marked `honest: false` (119 of the 194 Sobol configurations; they read as low as 89.79 because a rail parked at
  400 mm is simply out of band, not in contact).

## Measured on the raw posed skin (rail requirement along its arc, before any sweep)

K3 march of every rail sample over the closing bench poses, q95 over poses, max over the rail's width:

| variant | rail end near the pole (overhead) | middle | rail end near rest | no clearance in 220 mm |
|---|---|---|---|---|
| hub, champion axes, side +1, alpha 45 | 57 mm (phi -16) | 67 mm (phi -85) | **137 mm** (phi -154) | ws (30, 90, 15), (-15, 60, -15), (45, 90, 15), (30, 105, 0), (60, 90, 15) at the rest end |
| hub, side -1 | 400 (blocked) | 400 | 400 | the whole rail in >= 5 % of poses |
| spec (pointer, p* pole), side +1, alpha 40 | 93 mm | 117 mm | **150 mm** | - (worst: across-body ws (90-150, 30-45, -30..-60) 156-169 mm) |
| spec, side -1 | 85 mm | 95 mm | 400 (blocked) | across-body (135, 75-135, -45) |

The median requirement of the same samples is 52-79 mm (hub) / 59-119 mm (spec): a rigid circle has to sit at the
WORST pose's height over its WHOLE arc, so it rides 30-80 mm over the skin in the median pose. This is the proximity
atlas rule (a rigid part must clear the highest skin it ever passes over) at its most extreme: the rail is the
longest rigid arc of any J2 (125-150 deg of arc + the carriage) and it is swept by q1 around the whole shoulder.

## Sweep (Bench(60, 160), fast grid, honest kit checks)

195 configurations: 1 local check + 194 on the cloud CPU farm (Sobol: 128 rail-on-3R with an arm hub J3 over az, el,
A1, A2, wd, wa, sigma, side, alpha 8-85, dphi +-60, Lc 25-50, qcov 0.4-1.0, q 0.85-1.0; 64 spec pointer + C-slide over
az, el, side, alpha, dphi, Lc, qcov, q, s, phi_s, cov; 2 seeds). 119 park the rail at the fallback radius (flagged
dishonest, see above).

| | gap | score | reach | follow | in-band 14 | in-band 10 | contact | rail radius | rail / carriage in band |
|---|---|---|---|---|---|---|---|---|---|
| best honest (k0: champion axes, rail alpha 45, side +1) | **102.5** | 62.7 | 0.775 | 0.917 | 0.115 | 0.077 | 0.082 | 153 mm | 0.00 / 0.00 |
| 2nd (k18: alpha 51, sigma +1) | 103.23 | 62.5 | 0.688 | 0.833 | 0.209 | | 0.012 | 139 mm | 0.0002 / 0.00 |
| ring-like rail (k5: alpha 12, the rail ~ a big hub about a2) | 125.08 | | 0.525 | 0.717 | 0.399 | | 0.142 | 89 mm | 0.015 / 0.00 |
| spec (k1: pointer p*, C-slide, alpha 40) | 112.24 | 59.2 | 0.463 | 0.833 | 0.385 | 0.317 | 0.053 | 131 mm | 0.0002 / 0.00 |

Reference: champion spherical 3R 68.93 (same bench), pointer-cslide (the spec's J2 as a hub) 69.84.

**Convergence gate: NOT passed** (2nd-half gain 0.0, last-third gain 0.0, top-5 spread 5.81 score points > 3). CMA-ES
from k0 is running on the farm and appends to the sweep (the loop to continue:
`RUNPOD_API_KEY="$(cat ~/.runpod_key)" python3 docs/concepts/models/meridian-goniometer.py farmcma '{}' 6 24 0.2 hub`;
`... farmcma '{}' 6 24 0.2 cslide` for the spec). The farm queue was 13+ minutes per batch during this screen (uploads
of 600 MB by concurrent agents), so the gate could not be run to the end inside the time box.

## Red team (k0)

| pose | result |
|---|---|
| rest (0, 4, 0) | taken; hub1 3.1 mm, hub3 8.9, neck 5.2; rail / carriage / bridge > 31 mm (beyond the grid) |
| overhead abduction (0, 150, 0) | taken; rail 20.3 mm at its nearest, carriage 15.7, bridge 18.7 - none in band |
| overhead flexion (90, 165, -90) | **contact**: hub3 -2.8 mm, neck -3.7 mm |
| across-body (135, 90, -45) | taken; rail / carriage > 31 mm |
| behind-the-back (-75, 30, 165) | **singular** (closure margin 8.3 deg < 10) |
| abduction 75 ER 90 (-15, 75, 90) | **singular** (margin 1.3 deg) |
| abduction 60 IR 60 (0, 60, -60) | taken; **root 1.7 mm** from the skin (pinch under the 2 mm rule) |
| abduction 90 / extension 45 | the rail comes down to 8.4 mm of the skin at one point, its median stays > 31 mm |

The optimistic number: none found in the rail (it is pessimistic by construction: one radius); the bench counts the
carriage at its real height over the rail (rail + 6.15), not at the rail's skin face.

## Verdict and what it teaches

Screened, not converged, but the limiter is structural and measured: **a virtual-axis arc rail is the worst place
for J2's metal, not the best.** A rail is one circle about a2 (the rigid carriage forbids any other shape), it spans
the whole elevation travel (q2 window 100-115 deg for 90-95 % of the closing poses, + the carriage + stops = 125-150
deg of arc), and it is swept by q1 around the shoulder; so it must clear the highest skin under ANY of its points in
ANY pose. Measured: q95 requirement 57 mm at the overhead end vs 137 mm at the rest end; the fitted rail rides
116-173 mm from GH, 0-6 % of its samples in band in every honest configuration, and in 61 % of the coarse configs
some rail sample has no clearance at all (its rest end passes through the arm or torso at mid elevation). Shrinking
the arc (alpha -> 10 deg, the rail becomes a large ring bearing about a2) brings it to 89 mm but costs reach (0.53) -
that is a hub, i.e. the champion's floating hub 2 again. On the spec's pointer the C-slide's twist window still caps
reach at 0.46 (pointer-cslide's measured limiter).

**New knowledge (predicts beyond this morphology):** a rigid curved guide for a revolute joint costs the joint's full
travel + its shoe in arc length at one radius; under the proximity rule its height is the max of the skin's
requirement over that whole arc and every pose, so a guide can only beat a hub when the joint's travel is short
(< ~40 deg of arc) or when the guide rides in a frame in which the skin under it barely moves (scapula-fixed near the
J1 pole, or arm-fixed along the humerus). J2 (elevation, 100+ deg) is the worst candidate for a rail; humeral twist
(arm-fixed band) and a short scapula-side arc are the only places rails have scored (rail-elbow's stages are also
0 % in band at 109/111 mm for the same reason).
