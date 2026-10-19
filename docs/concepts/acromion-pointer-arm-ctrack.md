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
| **fork yoke** (shoe 2 on its own skin-fitted tine from hub 2, no bridge) | 2 | 80.15 (k159) | |
| CMA-ES, fork yoke, 11 dims (+ twin), broad (sigma 0.25) and local (0.035-0.07) starts | ~440 | **58.71 (k474)** | reach 0.825, follow 0.967, ib14 0.443, contact 0.055 (score 78.65); NOT converged (gate: +4.45 / +1.92 / 0.48) |
| **fork k474, frozen wear on Bench(110, 360) EXACT** | 1 | **65.66** | reach 0.783 (282/360), follow 0.982, ib14 0.440, ib10 0.291, contact 0.080 = 34 poses (track 19, link 1 13, hub 2 6), overhead 4/28, min th margin 5.89 deg, near-touch gap 75.41, deepest -17.4 mm |

Best configuration (k474): J1 a1 = bvec(-16.1, -20.0) (back of the shoulder, the CMA box's lower elevation bound),
al12 92.84, al23 97.38, branch +1; C-track at s 60.5 mm, arc 5.1 +- 55.7 deg (-50.6..60.8), circular race at the
arc's highest skin face (61-90 mm), two shoes 79.2 deg apart on a fork yoke (thc -74.3), q 0.983 (moving parts),
qt 0.987 (track). Score 78.65 on Bench(60, 160) fast; per member in band: hub 2 0.85, track 0.82, link 1 0.48,
tines 0.47 / 0.32, hub 1 0.02 (floats over the infraspinatus), shoes 0.00 / 0.06.

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

## Red team of the best (k474, Bench(60, 160), named poses)

Attribution of the 160 workspace poses: taken 132; both shoes off the race 11; gimbal within 5 deg of its fold 6;
link 1 into the deltoid 4; torso on the race 4; hub 2 2; hub 1 1. Clip frames 58 / 60 (2 shoes off the race).
abduction 150: link 1 -5.0 mm into the deltoid, hub 1 0.0 (contact); flexion 165 + IR 90: fold (-0.6 deg margin);
across the body (135 / 90): taken, link 1 1.7 mm (near-touch); behind the back: shoes off the race, the race -1.7 mm
into the back; abduction 60 + IR 60: taken, race 0.3 mm (near-touch); rest / rest + IR 75 / abduction 90 / abduction
75 + ER 90: taken (shoe 1 floats 29-32 mm, the tines 3.5-18 mm).

### Earlier red team (twin shoes on a bridge, k132)

Attribution of the 160 workspace poses: taken 119; torso on the arm-fixed track 14; both shoes off the race 12;
link 1 into the deltoid 12; yoke 2; gimbal fold 1. Clip frames: 58 / 60 (2 yoke contacts).

| pose | result | worst metal (mm to skin) |
|---|---|---|
| rest | taken | track 4.1, hub 1 7.4; shoe 1 floats 31.7, shoe 2 19.6 |
| rest + IR 75 | taken (shoe 1 at +13) | track 2.5 |
| abduction 90 | taken | hub 1 1.6 (near-touch), shoes 28-31 |
| **abduction 150 (overhead)** | **contact: link 1 -3.3, hub 1 -1.1** (the deltoid bunches under the back seat) | |
| flexion 165 + IR 90 | gimbal 1.2 deg from its fold (not taken); link 1 would be -14.7 | |
| **across the body (135 / 90)** | **contact: link 1 -7.0, hub 2 -4.6, yoke -2.7** | shoe 2 2.3 |
| across low (120 / 45) | taken | shoe 2 4.6 |
| **behind the back** | **both shoes off the race; the race itself -3.4 into the back** | |
| abduction 60 + IR 60 | contact: the torso on the race (-1.7) | |
| abduction 75 + ER 90 | taken (shoe 2 holds) | track 1.2 |

The optimistic numbers: the track's in-band (0.96) is a skin-fitted arm-fixed part (quiet-zone ballast in the
metal-centric score: 1100+ samples); the moving parts are 0.00-0.66. The circular race radius is the track's highest
skin face over its arc (q 0.95 of the arm's own skin) - a fatter arm (muscle bulge, other wearers) shifts it.

## Verdict (GATE 0, round J1)

**Dead with its number.** Best 58.71 on Bench(60, 160) fast (fork-yoke twin shoes, 0 passive joints; score 78.65),
65.66 frozen exact on Bench(110, 360) (reach 0.783, 34 contact poses, overhead 4/28) - far above the gate (<= 15,
dies above 17.5) and the lead (18.49). The sweep had not converged (last third +1.92 score points) but it is 41 gap
points short and its limiters are structural (below). The
user's own decomposition does not fail on kinematics (the twin-shoe race carries the twist for 0.92-0.96 of the
workspace with the gimbal >= 5 deg from its poles) - it fails on WHERE the metal can be: an arm-fixed track only has
~105 deg of arm that the torso never touches, the twist joint's shoes must ride a circle about the humeral axis over a
58-89 mm skin radius (18-32 mm of float), and the gimbal's L1 / yoke ride the swing frame over the deltoid (in band
0.27-0.66, link 1 into the deltoid overhead and across the body).

## New knowledge (predicts beyond this morphology)

1. **The arm's torso-free arc is ~105 deg at every station** (s 25-240, radial skin march from the humeral axis,
   <= 2 % of the bench poses blocked): -55..+50 deg on the deltoid, -20..+85 distally (0 lateral, +90 posterior). Any
   ARM-fixed part beyond it meets the torso, the axilla or the folded forearm in 5-30 % of poses. (pointer-cslide
   measured 150-180 deg for a band in the POINTING frame - the arm frame is the narrower one.)
2. **Twin shoes break a C-slide's window wall**: two shoes rigid on the moving member, `twin` apart (<= the single-shoe
   window), on one circular race of arc A carry A - shoe + twin of rotation with no extra joint or passive
   coordinate: reach ceiling 0.54 -> 0.92-0.96 here. The same trick applies to pointer-cslide's 98-deg band and to any
   open ring bearing on the arm (ARMin-type C-rings).
3. **The gimbal + humeral-twist decomposition prefers a BACK-of-shoulder J1** (bvec(-20..0, -10..10)): the twist
   window for 90 % of the workspace is 148-163 deg there vs 200-299 deg at the acromion top, because the overhead arm
   passes near an acromion pole and the pointing frame spins there. The densest seat (posterior-medial) is not a seat
   (its GH ray runs into the trunk).
4. **Fit arm-fixed parts radially from the humeral axis with a short window** (3 mm): GH rays at s 90 run 100+ mm
   inside the arm and the 15-mm-window march jumps the torso and parks the part at 400 mm (contact 0.73, k0-k3).
5. **The spec's skin-shaped track + radial slide** needs 20-34 mm of skin-normal travel at the CMA optimum - the
   slide stands taller than the float it removes; a circular race on a skin-fitted saddle is the buildable version.

## Audit (independent auditor, 2026-10-17 ~19:45 UTC): the death STANDS

Task: refute the GATE 0 death (a modelling bug, a wrong convention, a missed parameter region, an over-strict check,
or an unconverged sweep). Local only, niced, <= 2 processes. Scratch scripts under the auditor's scratchpad; the 70
CMA evaluations are appended to the sweep file (tag `audit cma s11`).

| check | measured | effect on the verdict |
|---|---|---|
| reproduce k474, Bench(60, 160) fast | **58.71** (reach 0.825, follow 0.967, ib14 0.443, contact 0.055), audit clean, collide 0.0 | exact |
| reproduce frozen wear, Bench(110, 360) EXACT | **65.66** (reach 0.7833 = 282/360, follow 0.982, ib14 0.440, ib10 0.291, contact 0.080 = 34 poses, overhead 4/28, min th margin 5.89, near-touch 75.41) | exact |
| convergence: CMA-ES continued from k474 (sigma 0.05, 70 configs) | best 60.46, no gain | fork-yoke gate now 2.16 / 0.00 / 0.48 (2nd half / last third / top-5): the last third has stopped improving |
| CMA box: every top-30 config sits on el = -20 | -20 is the project's J1 seat rule (tools/gpu_bench.py `seat_ok`: -20 <= el <= 90) | not a missed region; lower seats are outside the user's back / acromion-top ruling |
| GHOST bound: drop members from the scoring (same poses, same chain) | no shoes 51.48; no shoes + no hub 1 48.27; no shoes + hub 1 + tine 2 **44.53**; hubs + links only (no race, no shoes) 53.83 | even a weightless twist joint leaves link 1 (0.48 in band) and the yoke (0.47) in the swing frame over the deltoid: 27 points above the 17.5 line |
| modelling slip: `kin` / `car_local` size the 24 mm shoe at r = 50 mm (27.5 deg) while the race sits at ~94 mm, so the shoe is sampled ~45 mm long and the window loses ~13 deg | corrected (shoe at r 94): 59.86 at k474's thc, 60.53 / 62.58 / 61.65 at thc -77.3 / -71.3 / -70.0 | neutral: the wider window takes a few more race-end poses, where the torso reaches the arm-fixed race |
| K6 over-strictness | collide 0.0 at k474 (no pose lost to a part-part check) | none |
| convention vs concept_baseline | B.report() on every sampled skin face; O20 hubs 81 samples each; kit audit empty | none |

Note on the legacy refutation bar ("within 10 of the champion's 68.93 on Bench(60, 160)"): this row already sits
below it (58.71). The death is by round J1 GATE 0 (> 17.5 dies; lead 18.49), and nothing found here moves the number
by more than ~2 points either way.

**Measured reason (one line):** the gimbal's link 1 and yoke ride the swing frame over the rotating deltoid (in band
0.47-0.48 even with every shoe, race and hub-1 sample removed: ghost 44.53), and the circular race's shoes float 18-32
mm over a 61-90 mm skin radius - structural, not a bug; reproduced 58.71 / 65.66 exactly.
