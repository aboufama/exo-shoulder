# deltoid-crest-j3-3r - Deltoid-crest J3 equal-arc 3R, re-measured at O20 / fold margin 5 (closing screen)

Round-4 pick, carried to round 14 as "a closing screen on the jump judge's forwarded O20 numbers ... doubles as lens 3's
no-knee control" (docs/concepts/ROUNDS.md, round 14 plan) and as the seed of lens plain-crest-j3-cap.

## Deeper version (answered before building)

1. **What a top mechanism designer would do that the spec does not ask for.** Not re-tune the seed: at O20 a spherical
   3R's hub 2 is ONE disc at ONE radius on an axis the closure moves, so the designer treats the spread of the J2-ray
   skin exits over the taken poses as the design objective, not a by-product, and reads the crest basin's fate from it
   directly (hub-2 level and in-band per config, and which poses set the level). They would open every free choice the
   class has at zero complexity - both branches, both stack orders at J2 and J3 (the inverted J3 stack is the spec's
   ask, but it is a variable, not a given), the underside quantile and the strap end hold - and search the basin
   globally (Sobol) before any local CMA, so a "basin" is not just the neighbourhood of a seed. They would drop the
   spec's base stub under link 1: the user ruled (CAD ruling 1, 2026-10-16) that the scapula handler carries the base
   directly at the J1 hub ring, so no base tab crosses link 1's annulus. And they would attribute every lost pose
   (fold folded / stretched, part-part, contact by member) before calling anything dead.
2. **Rawest material.** The posed render skin of every bench pose (concept_bench `B.skin(i)`, the rig's skin, signed
   distance by libigl on the exact path), the fit-clip frames (held-out Wave / Walking never loaded), the skin-motion
   map pipeline/conformal/analysis/skin_motion_map_14.json and the proximity atlas (docs/research/proximity_atlas.md:
   a rigid part must clear the highest skin it ever passes over) - not the round-4 digest's numbers, which were O15 /
   margin 10.
3. **Methods and tools.** The shared kit K1-K7 (closure, dense K2 continuity, K3 march, K4 O20 hubs, K5 straps with the
   60 deg climb, K6 at 1 mm radial, K7 neck) through docs/concepts/models/zc-frontier-3r.py's build UNCHANGED, whose
   objective already carries the spine-parked verifier's top_check (top faces, crowns and walls skin-checked,
   near-touch over all faces, closure residual, hub-axis accessibility F <= 140 mm); a Sobol coarse sweep over the
   crest box x branch x stack orders, then CMA-ES (tools/concept_cma.py) from the top configurations to the convergence
   gate; then the frozen-shape wear on Bench(110,360) exact (fit Bench(60,160) fast, every level frozen) with the
   per-pose loss attribution (zc-frontier-3r's `attribute`).
4. **What, other than me, shows the number is right.** The bench (the objective IS the verifier's plain gap with the
   top-face / crown checks, so a config cannot buy points by a face the verifier would reject), the frozen exact wear
   on the 360-pose verification bench, and a red-team pose list fixed before the search: overhead (elev >= 140),
   across the body (plane >= 100, elev >= 40), behind the back, the cap pole's binders (-75, 60, +60), (0..30, 150, 0),
   (0, 105, 0) and the crest binders the jump judge forwarded (30, 149, -59), (30, 124, -54), (30, 135, -45).

## Model

docs/concepts/models/deltoid-crest-j3-3r.py = zc-frontier-3r's build and checks with the search restricted to the
crest basin (clamped box): J1 bvec(az 30-120, el 48-80) inside ruling 4 (acromion top / cap pole; front / clavicle
seats rejected by `seat_ok`), J3 wdir(wd 95-120, wa -20..+20) - the deltoid crest, 10-35 deg higher on the arm than the
leaders' wd 82-86 -, arcs a1 34-64 / a2 38-70 (the spec's near-equal 45 / 50 inside), branch +-1, inv2 / inv3 0 / 1,
q 0.85-1.0, end_extra 0-6. Every part at its real size: three O20 v5 hubs (MR117-2RS pair, 12.25 mm stack), 12 x 3 Ti
straps, K7 14 x 6 neck to BOTTOM's bar. 3 active joints, 0 passive joints, 0 passive translations, complexity 0. MVP1:
no gears, pulleys or cables; every coordinate set by the three joints (nothing to sag).

Spec corrections (measured or ruled): O15 hubs -> O20 (ruling 2, "Keep O20 only"); fold margin 10 -> 5 (ruling 1); the
base stub under link 1 is not a part (CAD ruling 1: the handler carries the base at the J1 hub ring).

## Screen (2026-10-17, local, niced, <= 2 processes; farm closed)

Bench(60,160) fast, objective = the verifier's plain gap (zc-frontier checks). Sweep file:
docs/concepts/sweeps/deltoid-crest-j3-3r.json (every configuration in evaluation order, phase-tagged).

| step | configs | best gap (score) | reach / follow / ib14 / contact | where |
|---|---|---|---|---|
| seed A at O20 / margin 5 (round-4 26.35 at O15 / margin 10) | 1 | 71.21 (74.11) | 0.663 / 0.867 / 0.568 / 0.060 | hub 2 0.04 in band at F 76 mm |
| seed B | 1 | 69.65 | 0.681 / 0.883 / 0.542 / 0.053 | hub 2 0.03 at 78 mm |
| cap-pole crest cell bvec(55, 62) / wdir(98, 5) 50/58 (judge 62.80) | 1 | 60.39 | 0.756 / 0.883 / 0.545 / 0.039 | hub 2 0.00 at 94 mm |
| Sobol over the crest box x branch x inv2 x inv3 | 493 | 48.05 | 0.644 / 0.833 / 0.842 / 0.050 | short a1 38.9, inv2 1 / inv3 1 |
| CMA s1 from the Sobol best (sigma 0.5) | 441 | 39.94 (85.48) | 0.644 / 0.867 / 0.871 / 0.031 | a1 36.6 / a2 53.5, wd 102.0 |
| CMA s2 from the long-a1 cap basin (Sobol #2, 57.43) | 369 | 44.62 | 0.631 / 0.917 / 0.822 / 0.066 | pinned at the box edges a1 64, el 79 |
| CMA s3 from s1's best (sigma 0.3) | 289 | **37.90 (86.22)** | 0.656 / 0.867 / 0.879 / 0.031 | a1 38.1 / a2 51.5, wd 103.1 |
| CMA s4 / s5 from s3's best (sigma 0.25 / 0.4) | 257 + 311 | 37.90 (no gain) | | converged |

**Best (fast, Bench(60,160)): gap 37.90, score 86.22**, near-touch gap 69.09; J1 bvec(103.49, 65.82) (acromion top),
J3 wdir(103.08, -7.03) (crest), a1 38.12 / a2 51.49, branch -1, inv2 1 (link 1 on hub 2's cap plate, bridging over link
2), inv3 1 (inverted J3 stack), q 0.943, end_extra 3.0. Hub levels F 50.0 / 59.6 / 62.0 mm; in band per member hub 1
0.99, hub 2 1.00, hub 3 0.95, link 2 0.99, link 1 0.60, neck 0.87. 3 active, 0 passive, complexity 0.

### The basin's premise does not hold at O20 (measured over the 1227 honest configurations of the sweep)

| a1 (deg) | n | hub 2 in band (median) | hub 2 level F (median) | reach (median) | best gap |
|---|---|---|---|---|---|
| 34-40 | 506 | 0.95 | 61 mm | 0.637 | 37.90 |
| 40-46 | 110 | 0.07 | 69 mm | 0.600 | 49.76 |
| 46-52 (the spec's equal arcs) | 90 | 0.03 | 80 mm | 0.600 | 60.39 |
| 52-58 | 80 | 0.02 | 83 mm | 0.619 | 69.52 |
| 58-64 (cap pole, long a1 / short a2) | 441 | 0.76 | 67 mm | 0.631 | 44.62 |

| J3 seat wd (deg) | n | best gap | reach (median) |
|---|---|---|---|
| 95-100 | 356 | 40.30 | 0.637 |
| 100-105 | 603 | 37.90 | 0.637 |
| 105-110 | 108 | 45.19 | 0.606 |
| 110-115 | 82 | 60.39 | 0.581 |
| 115-120 | 78 | 77.06 | 0.562 |

* The round-4 basin (equal arcs 45 / 50, hub 2 0.82-0.997 in band) was an O15 / margin-10 artefact: at O20 / margin 5
  the equal arcs park hub 2 at 69-83 mm and 0.02-0.07 in band. Hub 2 lives in band only with a short first arc
  (a1 34-40: F ~60 mm, 0.95) - which is exactly the zc-frontier slice (a1 38 -> hub 2 1.00 at 60 mm; a1 46 -> 0.90 at
  64; a1 54 -> 0.06 at 86) - or at the cap pole with a long a1 / short a2 (0.76).
* The crest itself is a penalty: the best gap rises monotonically with the J3 seat above wd ~100 (37.90 -> 45.19 ->
  60.39 -> 77.06), and the global zero-complexity optimum (zc-frontier-3r, 15394 evaluations, all seats) sits BELOW the
  crest at wdir(85.7, -16.2) with 28.85 fast / 31.04 frozen exact. CMA s1 / s3 walked wd 105 -> 102-103 and s2 pinned
  at the box edges: the gradient points out of the morphology.

### Control: the crest vs the zero-complexity optimum through the same code today (Bench(60,160) fast, single changes)

| configuration | wd 85.74 | wd 95 | wd 100 | wd 103.08 | wd 110 |
|---|---|---|---|---|---|
| zc-frontier optimum (a1 36.7 / a2 69.1, J1 bvec(109.4, 65.9)) gap / near | **30.69** / 39.16 | 38.43 / 43.41 | 41.01 / 47.18 | 74.85 / 79.95 (hub 2 0.04) | 86.26 / 104.32 |
| this screen's best (a1 38.1 / a2 51.5) gap / near | 55.23 / 65.03 | 55.55 / 72.75 | 47.87 / 69.27 | **37.90** / 69.09 | 48.48 / 75.03 |

Moving the zc optimum's J3 up onto the crest costs 7.7 points at wd 95 and 10.3 at wd 100; re-optimised on the crest
(this screen, 1849 configs) it recovers to 37.90, still 7.2 gap points (2.6 score points) behind the zc optimum's 30.69
through the identical code, and its near-touch gap is 30 points worse (69.09 vs 39.16). Data:
the slice is reproducible with the model file (`ZC.evaluate` with `wd` replaced).

### Where the best loses (fast, Bench(60,160), `--attr`)

* Workspace 105 / 160 taken: fold stretched 37, folded 6, part-part 9, contact 3. Clips 52 / 60: stretched 6, contact 2.
* The fold window is [18.4, 84.6] deg (a1 + a2 - 5 = 84.6) against J1-J3 angles of 22.9-126.8 deg (p5-p95 over the
  workspace) at these seats: the crest J3 makes the stretched side the binder (37 of 55 lost ws poses).
* Overhead (elev >= 140): 0 of 12 ws poses (9 stretched, 3 part-part), 3 of 5 clip frames. Across the body 12 / 31
  (17 stretched). Behind 6 / 10.
* In band per member: hub 1 0.99, hub 2 1.00, hub 3 0.95, link 2 0.99, link 1 0.60 (inv2 puts link 1 on hub 2's cap
  plate, bridging over link 2: it rides ~3-5 mm higher), neck 0.87.
* Contacts: link 2 (4 poses), hub 2 (1).

## Red team (own best)

* **The optimistic number: the plain gap hides near-touch.** Near-touch gap 69.09 vs plain 37.90: q 0.943 sets every
  level at the 94th percentile of the fit poses, so metal sits < 1 mm from the skin on enough taken poses to cost 31
  points when near-touch counts. The min metal over all faces is 0.12 mm. The zc optimum pays 8.5 for the same.
* **The pose that jams:** none jam (K2 jam 0); the chain leaves the workspace on the stretched fold, a hard kinematic
  wall, overhead first (0 / 12). An unpowered MVP1 would hit J2's 5-deg margin stop there.
* **The point that pinches:** link 2's underside over the posterior-lateral acromion (4 of the 5 contact poses) and
  hub 2's rim once.
* **Abduction bulge under hub 3:** hub 3 sits at F 62 mm on the crest, 0.95 in band - the deltoid crest is not a bad
  seat for the hub; it is a bad seat for the KINEMATICS (it widens the J1-J3 angle range the dyad must span).

## Frozen exact on the verification bench (lesson c)

Fit Bench(60,160) fast, every level frozen, worn on Bench(110,360) EXACT (libigl), same checks
(docs/concepts/verify/deltoid-crest-j3-3r_frozen_exact.json; `CB_EXACT=1 python3 docs/concepts/models/deltoid-crest-j3-3r.py frozen '<best>' out.json`):

| | gap | score | reach | follow | ib14 | ib10 | contact | near-touch gap | min metal | overhead ws |
|---|---|---|---|---|---|---|---|---|---|---|
| fit, Bench(60,160) fast | 37.90 | 86.22 | 0.656 | 0.867 | 0.879 | 0.562 | 0.031 | 69.09 | 0.12 mm | 0 / 12 |
| **frozen, Bench(110,360) exact** | **47.88** | **82.59** | 0.578 (208/360) | 0.873 | 0.880 | 0.568 | 0.059 | 72.17 | 0.01 mm | 4 / 28 |

Losses on the big bench: workspace 208 / 360 taken - fold stretched 90, folded 15, part-part 32, contact 15 (link 2 9,
hub 2 7, hub 1 3). Clips 96 / 110 (stretched 10, contact 4). Overhead 4 / 28 (stretched 14, parts 5, contact 5); across
the body 16 / 68 (stretched 51); behind 17 / 25. J1-J3 angle p5-p95 20.3-143.0 deg against the window 18.4-84.6.
Kinematic closure 0.708 of the workspace (overhead 0.50). In band: hub 1 0.99, hub 2 1.00, hub 3 0.93, link 2 0.98,
link 1 0.61, neck 0.87.

Red-team pose list (nearest Bench(110,360) workspace pose; J2 exit = the K3 march along the J2 ray):

| asked (plane, elev, axial) | bench pose | result | J1-J3 | J2 exit vs hub 2 F |
|---|---|---|---|---|
| (-75, 60, +60) cap binder | (-75, 60, 60) | taken, min 2.01 mm | 42.7 | 53 vs 59.6 |
| (0, 150, 0) cap binder | (0, 150, -15) | part-part | 48.7 | 50 vs 59.6 |
| (30, 150, 0) cap binder | (30, 135, 0) | part-part | 32.4 | 54 vs 59.6 |
| (0, 105, 0) cap binder | (0, 105, 15) | part-part | 38.6 | 60 vs 59.6 |
| crest binders (30, 149, -59) / (30, 124, -54) / (30, 135, -45) | (30, 135, -60) | taken, min 2.03 mm | 54.6 | 55 vs 59.6 |

The short first arc fixes the cap pole's hub-2 problem (the J2 ray exits 50-60 mm at every binder, hub 2 is 1.00 in
band) - and pays for it with the fold: 90 stretched workspace poses. The binders that hub 2 used to lose are now lost to
part-part clearance (link 1 bridging over link 2 at the overhead poses).

## Late update: wide restarts s6 / s7 (2026-10-17 22:35-22:46 UTC)

| step | configs | best gap (score) | reach / follow / ib14 / contact | where |
|---|---|---|---|---|
| CMA s6, wide restart from 37.90 (sigma 0.7) | 221 | **36.63 (86.68)**, near-touch 57.59 | 0.650 / 0.900 / 0.864 / 0.031 | J1 bvec(105.50, 63.12), J3 wdir(103.38, +4.93), a1 38.69 / a2 44.11, inv2 1 / inv3 1, q 0.942, end_extra 2.55 |
| CMA s7 from 36.63 (sigma 0.3) | 145 | 36.63 (no gain) | | |

Hub levels 50.8 / 59.8 / 62.0 mm; in band hub 1 0.99, hub 2 1.00, hub 3 0.90, link 2 0.97, link 1 0.67, neck 0.83. The
shorter a2 (44 vs 51) narrows the window further (to [10.4, 77.8]) but buys follow (0.90) and 11.5 near-touch points.

**Convergence gate after s7 (n 2526, evaluation order): gain over the second half 1.204 (> 1), over the last third
0.462 (< 0.5), top-5 spread 0.422 (< 3): NOT formally passed** - the wide restart's +0.46 points landed in the second
half. Passing it in order needs ~900 more no-gain evaluations (not possible inside this box on the shared local CPU, the
farm is closed). So the row stays `screened`, with the death measured on the kill bar instead: the frozen exact of the
37.90 config is 47.88, 15.8 points above the spec's own bar (32.10) - a 0.46-point fast gain cannot close that.
**Frozen exact of 36.63 (Bench(110,360), docs/concepts/verify/deltoid-crest-j3-3r_frozen_exact_s6.json): 47.86 (score 82.6)** -
reach 0.575, follow 0.891, ib14 0.867, contact 0.062, near-touch 64.84, min metal 0.05 mm, overhead 4 / 28; ws losses
{"n": 360, "taken": 207, "fold_folded": 1, "fold_stretched": 96, "jam_K2": 0, "parts": 43, "contact": 13}. The 1.27-point fast gain did not transfer (37.90 -> 47.88, 36.63 -> 47.86).

## Pass 2: the normal J2 stack (2026-10-17 23:29 - 2026-10-18 00:30 UTC, local, niced, 2 processes)

Every CMA stream s1-s7 had fixed `inv2 = 1` (link 1 on hub 2's cap plate, bridging over link 2), inherited from the Sobol
best; the Sobol's 249 `inv2 = 0` configurations were never refined. The red team's own finding above (link 1 0.60-0.67
in band because inv2 = 1 makes it ride 3-5 mm higher) pointed straight at it. A categorical probe at the two best
configurations (14 configs, all sigma x inv2 x inv3, sweep phase `catprobe`):

| config | sigma -1, inv2 0, inv3 1 | sigma -1, inv2 1, inv3 1 (s1-s7) | inv3 0 (either inv2) | sigma +1 (any) |
|---|---|---|---|---|
| 36.63 (a2 44.1) | **33.07** (link 1 0.98 in band, ib14 0.908) | 36.63 | 51.08 / 83.79 | 90.6-103.1 |
| 37.90 (a2 51.5) | **35.80** | 37.90 | 51.31 / 85.68 | 82.3-99.9 |

The normal J2 stack wins by 3.6 / 2.1 points; the inverted J3 stack (the spec's ask) is confirmed (inv3 0 costs 15-50);
branch +1 is dead (follow 0.67-0.73). CMA then ran inside `inv2 0 / inv3 1 / sigma -1`:

| stream | configs | best fast gap (score) | note |
|---|---|---|---|
| s8 (inv2 1, sigma 0.45) | 25 | 36.63 | stopped: dominated once the probe read 33.07 |
| s9 (inv2 0, from the 36.63 config, sigma 0.35) | 193 | 29.85 (89.15) | J1 bvec(108.6, 63.8), J3 wdir(104.1, +1.6), a1 39.3 / a2 45.8 |
| s11 (inv2 0, from the 37.90 config, sigma 0.5) | 341 | 33.34 | stopped for the frozen wear; the a2 ~51 side stays worse |
| s10 (from s9's best, sigma 0.3) | 681 | **26.78 (90.26)** | sigma collapsed (0.03): stop |
| s12 (wide restart from 26.78, sigma 0.5, pop 12) | 1189 | 26.78 (no gain) | second basin 29.38 at J1 bvec(97.5, 62.8), J3 wdir(109.4, -1.1), end_extra 6.0 (box edge) |
| s13 (cap-pole cell bvec(55, 62) / wdir(98, 5) 50/58 at inv2 0, sigma 0.6, pop 12) | 697 | 47.48 | reach 0.794 (the highest of the screen) but hub 2 at F 86 mm, ib14 0.636: the cap pole's hub-2 problem is untouched by the stack order |
| s14 (from the 29.38 basin, sigma 0.35) + s15 (from 26.78, sigma 0.2), closing streams | S1415_N | S1415_BEST | |

**Best fast (Bench(60,160)): 26.78, score 90.26** - J1 bvec(108.56, 64.50) (acromion top), J3 wdir(104.41, -0.39)
(crest), a1 40.46 / a2 45.92, sigma -1, inv2 0, inv3 1, q 0.957, end_extra 2.95. Reach 0.700 (112 / 160 ws), follow
0.900, ib14 0.903, ib10 0.457, contact 0.018; near-touch gap 51.11, min metal 0.04 mm; overhead 0 / 12 ws (9 stretched
fold, 3 part-part), 3 / 5 clip frames. Hub levels F 51.0 / 60.3 / 62.0 mm; in band hub 1 0.98, hub 2 1.00, hub 3 0.93,
link 1 0.96, link 2 0.86, neck 0.85. Fast losses: ws stretched fold 34, part-part 12, contact 2; clips stretched 5,
contact 1. 3 active, 0 passive, 0 passive translations, complexity 0.

### Frozen exact (fit Bench(60,160) fast, every level frozen, worn Bench(110,360) exact) - the fast gain does not transfer

| fast best | fast gap | frozen exact gap (score) | reach | follow | ib14 | contact | near-touch | overhead ws | penalty |
|---|---|---|---|---|---|---|---|---|---|
| 36.63 (inv2 1, pass 1) | 36.63 | 47.86 (82.60) | 0.575 | 0.891 | 0.867 | 0.062 | 64.84 | 4 / 28 | +11.2 |
| 29.85 (s9) | 29.85 | 43.99 (84.00) | 0.594 | 0.882 | 0.913 | 0.066 | 61.06 | 4 / 28 | +14.1 |
| 28.63 (s10 g19) | 28.63 | 41.04 (85.08) | 0.603 | 0.891 | 0.909 | 0.054 | 60.01 | 5 / 28 | +12.4 |
| **26.78 (s10)** | 26.78 | **40.17 (85.39)** | 0.606 (218 / 360) | 0.891 | 0.905 | 0.048 | 59.75 | 6 / 28 (0.214) | +13.4 |

File: docs/concepts/verify/deltoid-crest-j3-3r_frozen_exact_s10.json. Big-bench losses of the 26.78 config: workspace
218 / 360 - stretched fold 88, folded 2, part-part 39, contact 13 (hub 2 6, link 2 4, hub 3 3, neck 2, hub 1 1); clips
98 / 110 (stretched 9, contact 3); overhead: the attribution counts 5 / 28 taken (stretched 14, parts 3, contact 6)
while the overhead reach metric reads 6 / 28 (0.214) - the same one-pose offset at 28.63 (4 vs 5); not resolved here,
the table quotes the metric; clip follow 0.6; across
the body 19 / 68 (stretched 48); behind 17 / 25. Min metal 0.05 mm. Red-team binders: (-75, 60, +60) taken at 1.75 mm;
(0, 150, -15), (30, 135, 0), (0, 105, 15) lost to part-part (link 1 / link 2 at hub 2 over the cap: J2 exits 49-58 mm
against hub 2 at 60.3); the crest binders (30, 135, -60) taken at 2.54 mm.

**New knowledge (measured): at the crest seats the fast bench over-reads by 11-14 gap points at EVERY optimum, five
to six times the zero-complexity optimum's own fast-to-frozen penalty (zc-frontier 28.85 -> 31.04, +2.2).** The
reach loss splits evenly: the stretched-fold share of the workspace rises 21.3 % -> 24.4 %, part-part 7.5 % -> 10.8 %,
contact 1.3 % -> 3.6 % from Bench(60,160) to Bench(110,360). The crest J3 puts the stretched fold wall (J1-J3 p5-p95 18.1-137.4
deg on Bench(110,360) vs the window [10.5, 81.4]; kinematic closure 0.75 of the workspace, 0.50 overhead) through the
densest part of the workspace, so which of the 160
poses fall on the taken side is a sample artefact the CMA exploits; the 9.85 fast points s9-s10 bought (36.63 ->
26.78) are worth 7.7 frozen. On the fast bench the crest now beats the zc optimum through the same code (26.78 vs
30.69) - on the verification bench it does not (40.17 vs 31.04): the pass-1 "dominated" claim stands on the bench
that counts, not on Bench(60,160).

## Verdict: VERDICT_HEAD

**Pass 2 (this update):** best fast 26.78 (score 90.26 on Bench(60,160)) with the normal J2 stack - the first crest
configuration to cross 90 on the fast bench - but frozen exact on Bench(110,360) it reads 40.17 (score 85.39; the
verifier re-measured the same config independently at 40.17, connected reach 0.589, contact depth to 23.4 mm at
(0, 165, +15) overhead). 8.1 over the spec's kill bar (32.10), 9.1 behind the zero-complexity optimum (31.04 frozen),
21.9 behind the lead (18.28). Convergence gate over the whole sweep (score points, evaluation order): GATE_LINE.

Pass 1 (kept for the record):

Convergence gate before the s6 wide restart (n 2160): 0.742 / 0.149 / 0.244 - passed then; after s6 / s7 (n 2526):
1.204 / 0.462 / 0.422 - not formally passed (above). s4 (257) and s5 (311) found nothing below 37.90; s7 (145) nothing
below 36.63.

Frozen exact 47.88 (score 82.59) against the spec's own kill bar (beat j3-neck-over-3r's 32.10 frozen), the
zero-complexity optimum's 31.04 frozen exact and the lead's 18.28. 2526 configurations on Bench(60,160) (493 Sobol over
the crest box x branch x both stack orders, CMA streams s1-s7); best fast 36.63 (frozen exact 47.86; 37.90 -> 47.88).

Limiter (measured): the deltoid-crest J3 seat widens the J1-J3 angle range the J2 dyad must span (p95 143 deg on the big
bench), so the plain spherical dyad loses the stretched side (90 / 360 workspace, 14 / 28 overhead, 51 / 68 across);
the only arcs that open the window (a1 >= 44) lift hub 2 to 69-83 mm (0.02-0.07 in band) at O20. The round-4 "crest
basin" (hub 2 0.82-0.997 at equal arcs) was an O15 / margin-10 artefact. The crest is dominated by the
zc-frontier optimum below it (wd 85.7) on the bench that counts: 40.17 vs 31.04 frozen exact (pass 2); on the fast
bench the pass-2 crest best now reads 26.78 vs the zc optimum's 30.69 through the same code (pass 1: 37.90), a
sample artefact worth 11-14 points at every crest optimum; the zc optimum moved up to wd 95 / 100 loses 7.7 / 10.3.

What this predicts beyond the morphology: for a plain spherical 3R at O20 the J3 seat height is a FOLD lever, not a
proximity lever - raising J3 toward the acromion widens the J1-J3 range the dyad must cover; any crest-seat design
needs a second fold window (knuckle, relay, 4th joint). As lens 3's no-knee control (crest-knee-3r): the knee must buy
> 30 points on the stretched side at these seats to matter.

Pass-2 lessons that predict beyond this morphology: (1) the J2 stack order is a first-order variable at O20 (3.6 /
2.1 points at fixed geometry, link 1 0.67 -> 0.98 in band): never let a CMA inherit a categorical from the Sobol
best - probe every stack order x branch at the incumbent before the local search. (2) The fast bench's error is
seat-dependent: 11-14 points at the crest vs 2.2 at the zc optimum. Where the stretched fold wall cuts the dense part
of the workspace, Bench(60,160) rewards the CMA for moving the wall between its 160 samples; judge such seats on the
frozen exact wear, never on the fast number (here the fast score crossed 90 while the frozen one sat at 85.4).

## Verification (adversarial verifier, 2026-10-18)

**Verdict: the claim stands - VERIFIED at v_gap 47.86 (score 82.60) on Bench(110,360) exact, frozen shape; not refuted
against the champion (75.94 on the same bench and checks). The design is still dead on the kill bar** (spec bar 32.10,
lead 18.28). Harness: `docs/concepts/verify/deltoid-crest-j3-3r-skeptic.py` (zc-frontier-3r's build and checks run
directly, without the model file's crest-box snap; every addition below is its own code).

| run (claimed config: J1 bvec(105.50, 63.12), J3 wdir(103.38, 4.93), a1 38.69 / a2 44.11, sigma -1, inv2 1 / inv3 1, q 0.942, end 2.55) | gap | score | reach | follow | ib14 | ib10 | contact | near-touch gap | min metal |
|---|---|---|---|---|---|---|---|---|---|
| claim, Bench(60,160) fast (reproduced) | 36.63 | 86.68 | 0.650 | 0.900 | 0.864 | 0.475 | 0.031 | 57.59 | 0.38 |
| Bench(60,160) **exact** refit (CB_EXACT=1) | 36.64 | 86.68 | 0.650 | 0.900 | 0.864 | 0.473 | 0.031 | 58.88 | 0.30 |
| **frozen, Bench(110,360) exact (v_*)** | **47.86** | **82.60** | 0.575 (207/360) | 0.891 | 0.867 | 0.479 | 0.062 | 64.84 | 0.05 |
| champion 3R, Bench(110,360) exact, kit checks + 1 mm radial (risley-turret verifier) | 75.94 | 72.39 | 0.742 | 0.927 | 0.413 | 0.256 | 0.091 | | |

What was checked:

1. **DOF (R5 / R17).** J1 (scapula-fixed axis, O20 hub, base carried by the handler at the J1 ring), J2 (K1 closure on
   a fixed branch) and J3 (humerus-fixed axis) are three active pins; member 3 is rigid on BOTTOM's bar. 3 active, 0
   passive, 0 passive translations, nothing undetermined. Seat residual of J1 / J3 vs their declared seats 1e-4 deg.
   J1 seat bvec(105.5, 63.1): anterior component 0.12 <= 0.20, inside ruling 4. Pass.
2. **Real size and sampling.** O20 v5 hubs (rad 10, 12.25 mm stack) at all three joints, 12 x 3 Ti links, K7 14 x 6
   neck, every member sampled over its whole face at the baseline density (kit audit clean, `honest` true); top faces,
   crowns and walls skin-checked (1 top-contact pose on the big bench, counted as contact). Pass.
3. **Pose-taking.** Closure: the J2 axis meets both arcs to 0.0 deg on every taken pose. Fold margin read in ONE metric
   (th = angle(J1, J3), recomputed from the axes, not from the closure mask): min 6.46 deg over the 305 taken poses of
   the big bench (5.38 on Bench(60,160)), th 23.2-76.3 deg. Dense K2: 0 flips. K6 at 1 mm radial (collide 0.117 of the
   closing poses). Hub-axis accessibility: F 50.8 / 59.8 / 62.0 mm (<= 140). Pass.
   **Continuity flood (added; a plain 3R needs none by the rule):** a grid-neighbour flood reads only 71 of 207 taken
   workspace poses connected - an artefact: the bench samples the workspace grid sparsely, so most grid neighbours are
   absent (312 grid edges for 263 closing poses). With kNN-8 edges (2-deg slerp, closure at the 5-deg margin at every
   step, no axis step > 10 deg) every closing workspace pose is connected (263 / 263 on Bench(110,360), 120 / 120 on
   Bench(60,160)): the fixed-branch closure set is one region, no islands. Static reach stands.
4. **Bench artefacts.** None: the exact Bench(60,160) refit equals the fast claim (36.64 vs 36.63).
5. **Contact depth (T5, lead's rule).** Per-pose dump `docs/alignment/remeasure/deltoid-crest-j3-3r_bench_perpose.json`
   (alignment_paired format; the tool itself cannot wrap this kit model - no pin-knee-style audit - so the harness
   writes the same rows through `alignment_paired._dump_bench` / `gap_parts`); its recomputed gap 47.87 reproduces
   47.86 within 0.05. 20 contact poses (13 workspace, 7 clip), depths 0.10-3.26 mm (median 0.99; 5 deeper than 2.5 mm).
6. **Losses (re-attributed, identical to the claim):** workspace 207 / 360 taken - fold stretched 96, folded 1,
   part-part 43, contact 13 (link 2 7, neck 5, hub 2 4, hub 1 3, hub 3 1 over clips + ws); overhead 4 / 28 (stretched
   15), across the body 19 / 68 (stretched 48). th p5-p95 19.3-131.2 deg against the window [10.4, 77.8].

Champion on the same bench: 75.94 (kit checks + 1 mm radial, Bench(110,360) exact). This harness adds the top-face /
crown skin check, which can only add contact, so the champion reads >= 75.94 here; its in-band 0.41 alone costs 49
gap points, so the margin-5 rebase cannot bring it below 47.86. Not refuted. No hard rule broken.

**Held out (same harness, `held`):** the frozen shape of the claimed config worn on 470 poses disjoint from
Bench(110,360) (tools/osn_polish.py held_bench, exact; held-out clips never loaded): **50.05** (score 81.80; reach 0.575,
follow 0.873, ib14 0.870, ib10 0.471, contact 0.068, near-touch 66.52, overhead 4 / 26). Fold margin min 5.31 deg in
th, 0 flips. Per-pose dump `docs/alignment/remeasure/deltoid-crest-j3-3r_held_perpose.json` (recomputed 50.05). Contact
depth: 22 poses, two DEEP overhead hits - (30, 165, -15) 10.5 mm and (0, 150, -30) 9.2 mm into the skin; the rest
<= 2.6 mm. They are scored as contact (plain gap), but the depth says the overhead skin binder is not a near miss.

**The model's later best (re-measured with this harness, since the screening agent kept searching after the claim):**
CMA s10's 26.78 fast config (J1 bvec(108.56, 64.50), J3 wdir(104.41, -0.39), a1 40.46 / a2 45.92, sigma -1, inv2 0 /
inv3 1, q 0.957, end 2.95; normal J2 stack) frozen on Bench(110,360) exact: **40.17** (score 85.39; reach 0.606 =
218/360, follow 0.891, ib14 0.905, ib10 0.463, contact 0.048, near-touch 59.75, overhead 5 / 28; fold margin min 5.50
deg in th; 0 flips; hub F 51.0 / 60.3 / 62.0). Fast-to-frozen penalty 13.4 points (the screen's 12-14 holds). Losses: ws
fold stretched 88, part-part 39, contact 13. Continuity flood over the TAKEN workspace poses (kNN-8): 212 / 218
connected; 6 islands at elevation 90 (planes -15..60, axial 15-45), so a connected-reach reading is 0.589 (gap +1.7).
Contact depth: 16 poses, two deep overhead hits (0, 165, +15) **23.4 mm** and (0, 165, -45) 11.6 mm. Still 21.9 over
the lead (18.28) and 8.1 over the spec's kill bar (32.10): the verdict (dead on the kill bar) stands for the morphology.
Files: `docs/concepts/verify/deltoid-crest-j3-3r_skeptic_{fit60,frozen,held,frozen_s10}.json`.
