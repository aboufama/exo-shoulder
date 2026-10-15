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
