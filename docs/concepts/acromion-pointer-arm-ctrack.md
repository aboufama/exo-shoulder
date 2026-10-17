# acromion-pointer-arm-ctrack - gimbal at the shoulder + arm-fixed skin-shaped C-track for the humeral twist

Model: `docs/concepts/models/acromion-pointer-arm-ctrack.py` (shared kit + a carriage add-on). Sweep:
`docs/concepts/sweeps/acromion-pointer-arm-ctrack.json`. Row: `docs/concepts/rows/acromion-pointer-arm-ctrack.json`.
Preview: `docs/concepts/viz/concepts/acromion-pointer-arm-ctrack.js`. Round J1 (round 101) GATE 0 screen.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Measure the twist window the track
   must carry for EVERY allowed J1 seat before drawing anything (the class lives or dies on it), with the carriage
   angle in the pointing frame placed where the window is densest, on the workspace poses and the clip frames
   separately; treat J1's seat as the design's main variable (the spec's acromion seat sdir(40,0) is the WORST class
   of seat for this decomposition - measured below); refuse the spec's radial slide where it stands up (a skin-normal
   slide counts travel + block) and measure its travel instead of assuming it; fit the arm-fixed track on the arm's
   own skin only (a pose where the torso reaches an arm-fixed part is a contact pose, never a reason to lift the
   part); make the track the arm end itself (BOTTOM cut and merged), so no neck crosses the carriage's path.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (track,
   carriage, yoke and hubs all fitted and checked on it pose by pose), the scapula / humerus rotations of the 60 fit
   clip frames and the 160 (and 360) workspace poses (the twist window is computed from them, not from
   ring_travel.json or the catalogue's 311-353 deg digest), and the body_pose humerus frame (E = GH -> elbow).
3. **Methods and tools.** tools/concept_kit.py (K1 closure = the gimbal at 90/90 or skewed, K2 dense continuity, K3
   march, K4 O20 hubs, K5 straps, K6 collisions + `over`), a per-pose carriage riding the fitted track (add-on in the
   model), a circular sliding-window count for the twist window, CMA-ES / coarse grids on Bench(60, 160) fast, frozen
   wear on Bench(110, 360) exact.
4. **What shows the number is right besides me.** The bench (it scores every sample I hand it on its own skin
   distance, contact included), the kit audit (sampling, O20 hubs, pose locality), the adversarial verifier and the
   alignment auditor, and the red-team list: rest, overhead (elev >= 140), across-body, behind-the-back, the pose
   that ends the carriage's travel, the anteromedial track end against the chest, hub 1 when the arm comes nearest
   to the gimbal pole, and the radial slide's travel (the spec's hidden stand-up).

## Kinematics as built (spec fixes in **bold**)

- J1 axis a1 = scapula-fixed `bvec(az, el)` through GH; J2 axis u2 = `K.closure(a1, d, al12, al23, sigma)` (90/90 =
  the spec's orthogonal gimbal, u2 = sigma unit(a1 x d)); d = the GH -> elbow axis (body_pose humerus frame).
  Pointing frame r_ref = unit(u2 - (u2.d) d), t_ref = d x r_ref. The carriage sits at angle thc about d from r_ref;
  its place on the arm th_arm (0 lateral, +90 posterior) is the third active coordinate. Taken only if the gimbal is
  >= 5 deg (the user's fold margin, `K.FOLD_MARGIN`) from its fold/poles and the 24 mm carriage stays on the track.
- **The twist window is measured first, per J1 seat** (circular sliding window over the closing poses, best thc):

  | J1 seat (bvec az, el) | reach ceiling, W 103 | W 133 | W 176 | W 200 | note |
  |---|---|---|---|---|---|
  | (-50..-30, -10..0) posterior-medial | 0.69 | 0.84 | 0.97 (360 ws) | 0.99 | **not a seat**: the GH ray runs under the scapula into the trunk, hub 1 / link 1 park at 400 mm (k0-k3) |
  | (-20..0, -10..10) back of the shoulder | 0.65-0.675 | 0.78-0.81 | 0.92 (0, 0) | 0.94 | housable; (0, 0) flips 44 of 60 clip frames (reaching forward passes the pole) |
  | (30, 0) posterolateral | | | 0.886 | 0.914 | |
  | (90, 40) / (30, 40) / (0, 60) / **(30, 70) acromion top** (spec sdir(40, 0) ~ here) | | | 0.62-0.84 | 0.68-0.91 | the overhead arm swings the twist frame: the acromion seat is the WORST class |

  (W = the carriage's usable travel = track span - the carriage's own 27 deg; Bench(60, 160) ws unless noted; the
  spec's "311-353 deg for the functional workspace" is the 100 % number, the 90 % number is 148-200 deg.)
- **The arm's torso-free arc (the class limiter, measured on the raw posed skin).** Radial skin march from the humeral
  axis outward (3 mm window), every bench pose, stations s 25-240 mm: the share of poses in which the torso, the axilla
  or the folded forearm sits on that ray within 3 mm of the arm (an arm-fixed part there is in contact):

  | station s | arc with <= 1-2 % blocked (p95 skin radius sane) | blocked share beyond it |
  |---|---|---|
  | 25-90 (deltoid) | -55 .. +50 deg (105 deg) | 6-33 % anterior (-65..-111), 2-20 % posterior (+61..+118) |
  | 150 | -8 .. +84 (92 deg) | 3-30 % |
  | 200-240 (distal) | -20 .. +85 (105 deg) | 2-22 % (the forearm folds onto the anterior arm) |

  So an ARM-fixed C-track has the same wall as pointer-cslide's pointing-frame band: ~105 deg of clean arc at any
  station -> ~80 deg of carriage travel -> reach ceiling ~0.54 (W 78); every degree beyond it buys reach with torso
  contact on the track.
- **The spec's radial slide stands up.** The skin radius under the track spans 58-89 mm over the arc the carriage
  uses (track_R of the best configs); the slide-mode CMA optimum needs 20-34 mm of radial travel (+ 8 mm block) - a
  skin-normal passive slide that CLAUDE.md rules out at this size. **Screened build: `circ=1`** - the track's top is a
  circular race about the humeral axis (radius = its highest skin face + 3; the body under it skin-fitted, a saddle -
  pointer-cslide's lesson 2), the carriage is rigid on L2: 0 passive joints, 3 active. Cost: the carriage floats
  18-32 mm over the skin (race_float 23-26 mm median), in band 0.00.
- **Track fitted from the arm axis, not on GH rays** (pointer-cslide lesson 3, measured again here: GH rays at s 90
  run 100+ mm inside the arm and jump over the torso; 30-50 % of the track samples parked at 400 mm, contact 0.73).
  A pose where the torso reaches the arm-fixed track is a contact pose (the fit ignores blocked rays and takes the
  0.85-1.0 quantile of the arm's own skin).
- The track is the arm end (BOTTOM cut and merged into it): no K7 neck crosses the carriage's path.

## Sweep (Bench(60, 160) fast grid cache, K3 march, K2 dense, K6 + `over`, local niced, farm closed)

| stage | configs | best gap | note |
|---|---|---|---|
| k0-k3, early model versions (GH-ray track, posterior-medial J1) | 4 | 166.46 | superseded: track parked / hub 1 not seated |
| coarse grid: J1 (-20 / 0, -10 / 10), s_t 40 / 70, arc [-60, 55] / [-70, 75], circ 1 / 0 | 32 | 118.93 (slide) / **118.96 (race)** | thc = densest window |
| CMA-ES (own compact implementation), slide mode, from k15 | ~40 | 109.88 (k33) | stopped: the slide is not buildable (34 mm radial travel) |
| CMA-ES, race mode (two seeds) | see row | see row | 10 dims: az, el, s_t, tc, tw, dthc, qt, q, al12, al23 |
| single-shoe race: frozen wear k15 on Bench(110, 360) EXACT | 1 | **116.71** | reach 0.533, follow 0.845, ib14 0.417, 77 contact poses (track 58, link 1 24), overhead 2/28, min th margin 6.28 deg |
| **twin shoes** (2 shoes `twin` deg apart on L2, bridge along the race) | 6 | 89.55 (k132) | kinematic reach 0.54 -> 0.92-0.96 at the same 115-deg race |
| twin, frozen wear k132 on Bench(110, 360) EXACT | 1 | **93.65** | reach 0.728, follow 0.955, ib14 0.305, 75 contact poses (track 40, link 1 32, yoke 17, hub 2 15), overhead 5/28, min th margin 6.11 |
| **fork yoke** (shoe 2 on its own skin-fitted tine from hub 2, no bridge) | 2 + CMA | 80.15 (k159) | see row for the CMA result |

## Spec fixes and improvements made while modelling (each measured)

1. **J1 at the back of the shoulder, not on the acromion** (the twist window is 20-60 % narrower there; the user's J1
   ruling allows both). The densest-window seats (posterior-medial, az -60..-30) are not seats: their GH ray runs
   into the trunk (hub 1 at 400 mm, k0-k3).
2. **No radial slide**: the spec's carriage needs 20-34 mm of skin-normal travel (+ block); replaced by a circular race
   on a skin-fitted saddle body (0 passive joints). The spec's version scores 109.88 fast (k33) with that slide and
   is reported only.
3. **Twin shoes** (new, measured): two shoes rigid on L2, `twin` = 70-86 deg apart round the race: the open ring is
   held by whichever shoe is on it (an open ring bearing with a carriage pair spanning its gap; no new joint, no
   passive coordinate - both shoes ride the same circle about the humeral axis, so the pair never over-constrains).
   This breaks the window wall: 115 deg of torso-free race carries ~160-200 deg of twist (kinematic reach 0.54 ->
   0.92-0.96, clips 0.72 -> 0.98-1.0). Handover is continuous only if twin <= the single-shoe window (87.5 deg here):
   K2 dense rebuilds the chain every 2 deg and drops a frame whose path has a gap.
4. **Fork yoke** (new, measured): shoe 2 on its own tine from hub 2 (kit strap, skin-fitted) instead of a bridge along
   the race (which floats 30+ mm): +11.6 in-band points, gap 89.55 -> 80.15.
