# pointer-cslide - the user's split: 2R pointer + shoulder-side wire-race C-slide

Model: `docs/concepts/models/pointer-cslide.py` (shared kit). Sweep: `docs/concepts/sweeps/pointer-cslide.json`.
Row: `docs/concepts/rows/pointer-cslide.json`. Bench(60, 160), fast grid cache, K3 march, K2 dense, K6 on.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Measure the twist travel the C-slide
   must carry *before* drawing it (the whole design lives or dies on it), on the workspace poses and not only on the
   clips; choose the pointer pole and the branch from the raw arm directions (both singular cones +-a1 and the J1 hub's
   own footprint must stay clear of the arm), let the band's window and radius be fitted on the posed skin rather than
   picked, and try the inversions the spec hides: rail on the arm (the shoe on link 2 - this is seed-2r-cring, dead at
   129.98) versus rail on link 2 (the spec), A1/A2 off 90 deg (the pointer generalised to a spherical 3R whose last
   axis is the humerus), a tilted twist axis, and a donut (KAA10) versus the O20 hub.
2. **Rawest material.** The posed skin of every bench pose through the bench's own signed-distance grid (the band and
   shoe radii are marched radially from the twist axis on that skin, pose by pose), the humerus/scapula rotations of
   the 60 fit-clip frames and 160 workspace poses (the shoe-angle distribution is computed from them, not taken from
   ring_travel.json), and the proximity atlas's frame finding (a part in a swing frame - no twist - sees the skin turn
   under it; docs/research/proximity_atlas.md).
3. **Methods and tools.** tools/concept_kit.py (K1 closure 90/90 = the pointer, K2 dense continuity on values and axes,
   K3 march, K4 hubs, K5 straps, K6 collisions, K7 neck), a radial Lipschitz march for the circular band and the shoe,
   the cloud CPU farm for every sweep (tools/cloud_run.py sweep), Sobol coarse sampling then CMA-ES (pycma) from the
   top configurations until the convergence gate passes.
4. **What shows the number is right besides me.** The bench (it scores the metal I hand it, contact by its own skin
   distance), the kit audit (sampling density, hub size, pose locality, honest flag), the adversarial verifier
   (re-runs the row's best params), and a red-team list: rest, overhead (abduction 150+), across-body (plane >= 110),
   behind-the-back (extension + internal rotation), the pose that ends the shoe's travel, the band's open side
   against the chest, and the J1 hub when the arm comes nearest to the pole.

## Kinematics as built (spec fixes in **bold**)

- J1 axis a1 = S-fixed `bvec(az, el)` (spec pole p* = [0.36, 0.72, 0.60] = bvec(120, 46)); J2 axis p2 = K1 closure with
  cones A1 = angle(a1, p2), A2 = angle(p2, d3) (90/90 = the spec: p2 = sigma unit(a1 x d3)); d3 = the GH-elbow line
  (band humerus frame -y), tilt optional. Pointing frame P = [p2 x d3, d3 x (p2 x d3), d3]; q3 = the arm-fixed shoe's
  angle in P. Singular cones |angle(a1, d3) - 0/180| < `sing` rejected.
- **The shoe's travel window is fitted on the bench poses** (the smallest arc holding a share `cov` of the closing poses),
  not the spec's 60-90 deg: measured with p*, the shoe must travel **165 deg for 90 % of all bench poses, 193 deg for
  95 %** (clips alone: 65 / 112 deg - the spec's 67-87 deg came from clips only).
- Band, shoe and neck: see the model docstring (2 + 6 + 2 stack, band skin face at rho + 2, shoe lip at rho).

## Measured on the raw posed skin (before any sweep)

**1. The twist travel the C-slide must carry** (shoe angle in the pointing frame P over the closing bench poses, pole
p*; the smallest arc holding a share of the poses):

| share of poses held | all 220 | 60 clip frames | 160 workspace poses |
|---|---|---|---|
| 0.5 | 64 deg | 16 | 88 |
| 0.7 | 109 | 32 | 125 |
| 0.8 | 130 | 48 | 146 |
| 0.9 | **165** | 65 | **178** |
| 0.95 | **193** | 112 | 201 |
| 1.0 | 255 | 123 | 255 |

The spec's 67-87 deg is the clip-only number. The workspace poses span humeral rotation -165..+165 (ISB axial), so for
the reach target (0.90 of the workspace) the band must carry ~180 deg of travel + the shoe's arc + stops, i.e.
~235 deg of band around the arm. This is intrinsic: ring_travel.json's "intrinsic twist spread" (59 deg among clip
frames with arm directions within 10 deg) is a floor for any 2R pointing law, and on the workspace it is far larger.

**2. Where a band fixed in the pointing frame P can live** (radial march from the twist axis at stations 80/120/160 mm,
per P-angle: median / p90 requirement and the share of poses where the ray is blocked by the torso or needs > 75 mm;
sigma -1; sigma +1 is the same map turned 180 deg):

- s 120: P-angles -60..+90 (150 deg) have <= 10 % blocked, median requirement 41-64 mm, p90 51-76 mm; the other
  210 deg are blocked in 25-60 % of the poses (the chest, the axilla, the head overhead).
- s 160: the free sector is -75..+105 (180 deg, <= 17 % blocked), median 40-63 mm.
- s 80 (deltoid): only -60..+60 is free, median 52-67 mm.

So **a ~235 deg band (needed for reach 0.9) cannot fit the ~150-180 deg torso-free sector of its own frame**: either
the band hits the chest / axilla in 25-60 % of the poses, or the travel window shrinks to ~110-130 deg and reach drops
to ~0.6-0.7. And inside the free sector the skin radius under the band still ranges 41 -> 76 mm across its arc (the arm
is eccentric about the GH-elbow line and turns under a band that does not turn with it - the proximity atlas's
"swing frame" finding), so a circular band at one radius floats 10-35 mm over most of its arc.

**3. The pointer pole.** Best two-sided pole margin over the bench arm directions (scapula frame): 31.4 deg at
bvec(120, 40) (the spec's p* = bvec(120, 46): 29-31 deg). The J1 hub sits on +a1 where the overhead arm comes within
31-39 deg: at a 50-55 mm arm radius that means the hub is either > ~100 mm out or inside the deltoid overhead (red team
below: hub 1 -8.5 mm, link 1 -11.9 mm in abduction 150 at q 0.9). The antipodal hub site (-a1 = bvec(300, -46),
posterior over the scapula, where the base is) is worse: the ray runs under the scapula over the chest wall, hub 1
sits 92 mm inside the body in abduction 90 (local red-team run).

## Spec fixes and improvements made while modelling (each measured)

- **Neck down the arm, not to BOTTOM's bar start.** The kit's K7 neck runs to BOTTOM's bar start at the lateral arm
  root (67.5 mm lateral, 40 mm down); with the band at s 100-160 it must cross back over the band and link 2
  (measured: band-neck and link2-neck K6 collisions at rest, abduction 90, across-body in every config). The spec's
  neck (shoe's distal wall -> along the arm to s = max(180, s + 40), BOTTOM cut / merged there) is used, fitted
  per sample by a radial march from the twist axis (a GH-ray fit of a strap that runs along the arm finds no clearance
  in 220 mm and parks it at 400 mm - measured, then replaced): neck in band 0.82-1.0.
- **Saddle band** (`saddle=1`): the band's body under its circular wire track is skin-fitted per sample (each sample at
  the max over the closing poses of its own radial requirement, q_ring ~ 1); the track and the shoe sit at the body's
  highest point. The spec's cylinder (one radius for the whole band, `saddle=0`) floats: rho 78-103 mm vs the
  41-64 mm median skin; band in band 0.00-0.09 in all 212 coarse configs. With the saddle: band in band 0.77-0.89.
  Cost: mass (the band body fills down to the skin: 690 g Ti for the best config, ~5x the champion's 125 g; MVP1 would
  print it).
- **The shoe cannot hug.** It rides the track at the band's highest point: 24-30 mm off the lateral arm in every
  config (in band 0.00). This is structural for a rotary C-slide in a swing frame: the track is a circle about the
  twist axis, its radius is set by the fattest skin it ever passes over.
- Window and radius fitted on the bench poses (not the spec's 60-90 deg), branch and pole swept (sigma -1 essential:
  with sigma +1 the J2 axis points into the neck / chest in > 5 % of the poses and hub 2 is parked at 400 mm).

## Sweep (Bench(60, 160), fast grid, K3 march, K2 dense, K6, outer faces contact-checked)

| stage | configs | where | best gap | note |
|---|---|---|---|---|
| coarse Sobol, spec cylinder band, K7 neck | 212 (k 0-211) | farm | 173.65 (honest best 177.73) | band floats 30 mm, rho 80-103 |
| local CMA, saddle band, neck down the arm | 30 (k 212-241) | local, 1 process (farm queue 12-19 jobs) | 115.84 | |
| local CMA restart from best, 13 dims | 112 (k 242-353) | local | **73.48** (k 341) | still improving |
| local CMA restart, step 0.07 | 125 (k 354-478) | local | **69.84** (k 375) | score 74.60 |
| focused farm batch (64, spec cylinder, K7 neck, v1 model) | queued 20+ min | farm | - | not recorded: superseded model version |

The farm queue held 12-19 jobs from other agents for the whole time box (a 212-config batch took 858 s wall for
265 s of compute), so the CMA ran locally as one niced process (~2-7 s per configuration).

## Result (best k 375, Bench(60, 160) fast grid, honest: march + K2 dense + K6 + clean audit)

| gap | score | reach | follow | in-band 14 | in-band 10 | contact | mass (Ti) |
|---|---|---|---|---|---|---|---|
| **69.84** | **74.60** | 0.500 | 0.933 | 0.674 | 0.521 | 0.056 | 741 g |
| spherical 3R champion, same bench | 74.93 | 0.775 | 1.000 | 0.438 | 0.279 | 0.102 | 125 g |

Per member in band: band 0.85, neck 0.99, link 2 0.67, link 1 0.19, hub 2 0.18, hub 1 0.02, shoe 0.00. Window
T = 98 deg centred at 27 deg in P, track radius 81.8 mm about the axis (tilted 11.9 deg toward tilt_a -90), station
s = 111 mm, pole bvec(120.4, 35.4), cones 89.6 / 87.4 deg, branch -1, shoe arc 39 deg at arm angle -18 deg.
Params: `docs/concepts/rows/pointer-cslide.json` best_params.

**Convergence gate: NOT passed** - score gain over the second half of the 479 tries 13.44 (needs < 1), over the last
third 5.68 (needs < 0.5), top-5 within 1.06 (ok). The design is not called dead. Next: `RUNPOD_API_KEY="$(cat
~/.runpod_key)" python3 docs/concepts/models/pointer-cslide.py farmcma '{}' 8 32` (CMA on the farm from the best saddle
config, appends to the sweep) until the gate passes; then the verifier on Bench(110, 360) exact.

## Red team (the best config, named poses; local run)

| pose | taken? | the worst metal |
|---|---|---|
| rest (clip) | yes | band 3.0 mm min / 6.1 median; shoe 26.7 mm (floats); hub 1 >= 31.7 |
| rest + internal rotation 75 | **no: twist 112 deg outside the 98 deg window** | |
| abduction 90 | yes | link 1 15-29 mm, shoe 29 mm |
| abduction 150 (overhead) | **contact: hub 1 -15.7 mm, link 1 -14.7 mm inside the deltoid** | the pole margin is 20.5 deg here |
| flexion 165 + IR 90 | **no: window (104 deg)** | |
| across-body 135 / 90 | yes | band 6.2 mm min; hub 2 21 mm |
| across-body low 120 / 45 | yes | band 3.6 mm |
| behind the back (-75 / 30, axial 165) | **no: window (-69 deg)** | |
| abduction 60 + IR 60 | **no: window (92 deg)** | |
| abduction 75 + ER 90 | **no: window (-55 deg)** | |

The optimistic numbers: in-band 14 0.67 is carried by the saddle band (0.85) and the neck (0.99) - the two parts that
are skin-fitted per sample; the parts with one level (hubs, shoe, track) are 0.00-0.18. The saddle's body is solid
from the skin to the track (741 g Ti); a printed body would change the mass, not the bench number. The band's
underside is fitted at q_ring 0.99 of its own requirement; the 4 poses whose torso reaches the band's outer face are
counted as contact (outer-face check), the 4 others are skin contacts.

## Verdict and what it teaches

The user's split works far better than the spec drawing of it suggests - **if the band is skin-fitted** (saddle):
gap 69.84 vs 173.65 for the spec's cylinder, level with the 3R champion on this bench, with the best in-band 14 of any
3R-family design screened so far on Bench(60, 160) (0.67 vs 0.44). It cannot reach the workspace: **reach 0.50 is set by
the twist window**, and the window is set by the torso: a C-band fixed in the pointing frame (the swing frame, no
twist) has a torso-free sector of only ~150-180 deg at s 110-160, so the band (window + shoe arc + stops) fits ~98 deg
of travel, while the workspace needs ~150-180 (intrinsic: arm directions within 15 deg differ by a median 135 deg of
twist). The 2R pointer half shows the pole problem the spec predicted: the J1 hub sits where the overhead arm comes
within 20-39 deg, so it is either inside the deltoid overhead or > 30 mm off the skin elsewhere.

New knowledge (predicts beyond this morphology):
1. Any C-slide / ring that carries humeral twist in a frame that does not twist (a swing or pointing frame) is limited
   by the torso-free sector of that frame (~150-180 deg at mid-arm), not by the ring's own travel: workspace reach
   above ~0.6 needs either a twist share on another joint (the 3R's way) or a ring that opens toward the torso in
   every pose (no fixed sector does).
2. A rotary track only has to be circular where the bearing runs: the body under it can be skin-fitted per sample
   (here +0.85 band in-band, gap 174 -> 70). The same trick applies to any arc rail or ring bearing in the catalogue.
3. A strap that runs ALONG the arm cannot be fitted on GH rays (the ray runs inside the arm and parks it at 400 mm):
   fit it radially from the arm axis.
4. The kit's K7 neck to BOTTOM's bar start (lateral arm root) crosses any part that sits on the upper arm below
   s ~ 60 mm; models with arm-mounted parts need the neck to run down the arm (BOTTOM cut there).
