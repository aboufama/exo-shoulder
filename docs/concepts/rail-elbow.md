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

## Polish (2026-10-15, convergence check of the "dead" verdict)

**Why.** The verdict above was taken at best 71.15 (score 74.1) with the best found on the sweep's last try, and the
sweep had only ever moved d_off, q, wd and a2 around the champion axes (the J1 axis b, a1 and W's elevation never
moved for the telescopic rail). A sweep is a sample of the parameter space; a best on the last try is a sign it was still
climbing, not a property of the mechanism.

**Method.** CMA-ES (popsize 6, sigma 0.6 in units of az 8 / el 4 / a1 4 / a2 4 / wd 6 / wa 6 / d_off 5 deg) on the 7
continuous parameters (az, el, a1, a2, wd, wa, d_off); fixed: telescopic rail, sigma -1, margin 10, q 1, cov 1, tmarg 5.
Model, honesty checks and geometry rules unchanged (K3 march, dense K2, K6, audit). One change of measurement: `r_lay`
(layout radius of the rail parts) is set per config to the fitted stage radius (fix point, <= 2 re-runs), as k64's 142.5
was for its own geometry; k64 re-laid at its fitted 128 mm reads **70.87** (was 71.15; measurement, not design).
Runs: from k64 (42 tries), k59 (43), seed A k44 (10 tries, all audit-dishonest: strap 1 / bridge / neck sampled at
10-11 mm because the straps get long; gaps 76-87; stopped), then a restart from the new best k130 at sigma 0.3 (24).
126 new configurations, k65-k190, stage "polish" in the sweep file. No range was widened (CMA is unbounded here).

**Best-so-far curve** (score = 100 (1 - gap/275), polish tries in order): 74.2 (try 1, k64 re-laid) - 74.6 (13) -
74.9 (25) - 75.1 (49) - 76.1 (61) - 76.2 (66, k130) - 76.8 (108, k172) - 76.8 (126).

**New best k172** (honest, audit clean): gap **63.72, score 76.8** (bar 74.9; the champion on honest kit geometry 76.3).
b az -13.11 el 83.79, a1 76.84, a2 64.04, W (93.25, 17.21), d_off -41.43, r_lay 105. Reach 0.888, follow 0.967,
in-band 14 0.275, in-band 10 0.156, contact 0.000, closure 0.927, flips 0, K6 collisions 2.0 % of closing poses, Ti 151 g.
Per member in band: hub 1 1.00, hub 3 0.36, strap 1 0.41, rail 0.003, stage 2 0.00, bridge 0.04, neck 0.51.
Top 5: 63.72, 64.02, 65.30, 65.34, 65.38 (scores 76.83-76.23).

**Convergence gate: NOT converged.** Gain of the best over the second half of the polish 0.69 pt (< 1: pass; over the
whole sweep 1.92: fail); best at try 108 of 126, inside the last third (fail); top 5 within 0.6 pt (pass). The restart
from k130 was still finding better points (k172, k185) at sigma 0.3; more tries around k172 should be run before the
number is final.

**Red team (k172).** Rest (elev < 20) 57/57. Overhead (elev >= 140) 11/17: 4 closure folds, 2 K6 collisions (plane
15-30, elev 150, flex 90) - worse than k64's 14/17, the gain is bought in in-band, not in overhead reach. Across the body
40/48 (8 folds). Behind the back 28/29 (1 fold). Closest metal over taken poses: strap 1 1.34 mm (plane 45, elev 165,
axial -90), neck 2.01, hub 3 2.11, stage 2 2.12, rail 2.35; no contact. **What limits it:** unchanged in kind - each rigid
rail stage is one radius about p2 (now ~100-105 mm, lower than k64's 116-125 because the new J1 axis moves the rail over
lower skin), still 0 % in band; the score rose through hub 3 (0.15 -> 0.36), strap 1 (0.31 -> 0.41) and the neck
(0.42 -> 0.51). Status moves from dead to **screened** (clears 74.9 and, narrowly, 76.3); the structural argument above
still caps it (rail stages ~40 % of the samples at ~0 % in band).

## Convergence and red team (2026-10-15, leader stage 1)

**Gate on the polish, recomputed from the sweep file: not converged.** Over the 123 polish tries, the best-so-far
gained 0.69 pt over the second half (< 1: pass), **0.60 pt over the last third (>= 0.5: fail)**, and the top 5 are
within 0.60 pt (pass).

**Method.** CMA-ES on the farm, one job per stream (`tools/concept_cma.py`: 8 processes on one 8-vCPU worker, a whole
generation per round, no per-generation round trip). Same 7 parameters and scales as the polish (az 8, el 4, a1 4,
a2 4, wd 6, wa 6, d_off 5 deg), popsize 8, telescopic rail, sigma -1, margin 10, q 1. Model file unchanged.
Two rules are now automatic instead of hand-run:
* `r_lay` = the fitted stage radius (min of the two stages' levels), as a fix point with at most 2 re-runs;
* a dishonest report (kit audit) costs +100 in the objective, and so does a layout radius above the fitted one.

Both streams started from k172: A at sigma 0.3 (seed 11, 141 generations, 1129 tries, 698 s) and B at sigma 0.6
(seed 12, 35 generations, 281 tries, 882 s). Farm cost $0.13. 1410 tries were appended to the sweep, stage `cma2-A` /
`cma2-B`, k191-k1600.

| stream | best | score | where | gate on the stream |
|---|---|---|---|---|
| A (sigma 0.3 -> 0.02, collapsed) | **57.19** (k1530) | **79.20** | az 0.65, el 76.82, a1 80.71, a2 62.93, W (93.82, -4.20), d_off -33.24, r_lay 109 | 2nd half +0.14, last third +0.06, top 5 within 0.01: **converged** |
| B (sigma 0.6 -> 0.32, budget hit) | 58.23 | 78.83 | az 27.0, el 84.4, a1 84.4, a2 66.9, W (93.6, 1.1), d_off -57.4, r_lay 131 | 2nd half +0.66, last third +0.27: a second basin, still descending when it stopped |

**Gate on the whole CMA history (polish + cma2, 1533 tries in order): converged.** The best gained 0.38 pt over the
second half and 0.08 pt over the last third, and the top 5 are within 0.01 pt (57.19-57.22, all in A's basin).
B's basin (58.23, sigma still 0.32) is being continued from its best (stream C, sigma 0.2). If it goes below 57.19,
the gate has to be re-run.

**New best k1530** (Bench(60,160), fast grid, kit checks; re-run locally: same 57.19, honest, audit clean):
* reach 0.894, follow 1.000, in-band 14 0.334, in-band 10 0.193, contact 0, closure 0.923, 0 flips, K6 0;
* closure residual 0.0 deg, min fold margin 10.4 deg, Ti 161 g;
* rail at polar 29.7 deg about p2, centreline radius 54 mm, span 176 deg including the stops and the tab.

Per member in band: hub 1 1.00, **hub 3 0.75** (k172: 0.36), strap 1 0.43, **neck 0.68** (0.51), bridge 0.13 (0.04),
rail **0.00**, stage 2 **0.00**. The whole gain over k172 (63.72 -> 57.19) comes from the arm-end parts. The
morphology's own part, the rail, still contributes nothing in band.

### The measured limiter (k1530; k172 the same)

The two rail stages are 40 % of the metal samples (rail 0.20, stage 2 0.20), and 0.0 % of them are in band. The
per-sample skin need under them (the K3 march over the 203 taken poses) has a median of 58-59 mm. A rigid stage has to
take the maximum over its stations and over every pose, though:

| stage | need p50 | p75 | p90 | p95 | max = level | poses that set it |
|---|---|---|---|---|---|---|
| rail | 64 | 70 | 82 | 87 | 109 | pose 89 (plane -15, elev 60, axial -15), pose 180 (plane 105, elev 45, axial -165), 105, 123, 130 (internal rotation 75-105) |
| stage 2 | 72 | 81 | 90 | 95 | 111 | pose 89, pose 126 (plane 30, elev 105), 180, 88, 76 |

(The need columns are per-pose maxima over the stage's stations.)

* Even a stage refitted in every pose would sit at 64-72 mm, while the median sample needs 58: the spread along one
  stage, within a single pose, already pushes most of it past the 12 mm band.
* The 5 % worst poses add 20-40 mm on top of that.
* No per-member quantile can bring the stages into band. At q 0.75 they would still be at 70-81 mm, about 12-23 mm
  over the median skin, and they would lose 25 % of the poses.

### The variant that attacks it, and why

The red team found the telescope illegal for MVP1 (below), so the variant has to be the MVP1-legal rail: the **rigid
single rail (`tele=0`) with the CMA free to move the rail toward the J2 pole**. A small polar angle gives a short,
local arc whose far stations stay over the skin near p2, and that is the only way a one-piece rail can avoid the
beyond-carriage stations that killed it at d_off -25.

Measured at k172's axes before the search (local, Bench(60,160) fast): the rigid rail needs **209 mm** (gap 72.99,
dishonest: strap 1 and the bridge ramp up to it, sampled at 4.8-4.9 mm).
* Its per-pose need: p50 70, p90 103, p95 121, max 209 mm.
* Laid out at 70 mm, some stations find no clearance at all (400).

**Result (stream R, farm, sigma 0.6, seed 21, d_off scale 8, 249 tries, $0.08, stage `cma2-R`, k1601-k1849): best
k1841, gap 59.34 (score 78.42).** That is honest, MVP1-legal, contact 0, reach 0.900, follow 1.000, in-band 14 0.307,
in-band 10 0.187. Parameters: az 6.88, el 77.46, a1 77.51, a2 65.87, W (94.73, 6.76), d_off -57.51, r_lay 145.

What the search did with the rail:
* It drove the rail almost onto the J2 pole. Polar alpha is 8.4 deg, so the rail is a ring 21 mm in radius around p2,
  sitting 145 mm from GH (about 87 mm off the skin).
* It is still 0 % in band, but it now carries only a small share of the samples.

In other words, the legal rail converges toward the champion's J2 hub. The stream is not converged: it gained 2.39 pt
over its second half and 1.51 pt over its last third, and its top 5 are within 0.48 pt.

### Control: the plain spherical 3R at the same axes (the decisive red-team test)

The kit's honest champion model is `docs/concepts/models/_template.py`: flat O20 hubs at J1, J2 and J3, 12 x 3 links,
K7 neck, q 1.0, dense K2, K6. It reproduces 65.05 at the champion's axes. Run at each rail-elbow configuration's own
b / W / a1 / a2 / sigma (local, Bench(60,160) fast), it is better every time:

| axes from | rail-elbow | plain 3R, same axes | 3R in band per member |
|---|---|---|---|
| k172 (polish best) | 63.72 | **59.46** (honest, contact 0) | hub3 0.35, link1 0.37, neck 0.49, hub2 0.00 |
| k1530 (CMA best, telescopic) | 57.19 | **51.97** (honest, contact 0, reach 0.888, follow 1.0, in-band 14 0.393, in-band 10 0.224) | hub3 0.75, link1 0.32, neck 0.68, link2 0.06, hub2 0.00 |
| k1841 (CMA best, rigid rail) | 59.34 | **55.40** (honest, contact 0) | hub3 0.49, link1 0.36, neck 0.58 |

**The rail costs 4-5 gap points against an O20 hub at the same axes.** Everything that put this morphology ahead of
the champion came from the axes the CMA found (J1 axis b, W, a1, a2), and those axes are worth more in the champion's
own topology: **51.97 (score 81.1) vs the champion's 65.05**, both on honest kit geometry. The 3R control at k1530's
axes on Bench(110,360), exact, 1 mm radial, is queued on the farm (`bigbench-3r-at-railA`).

### Red team

1. **The telescope's 2:1 drive is not allowed in MVP1.** Stage 2 has to run at half the carriage speed; the model
   names a cable loop for this, which needs pulleys. REQUIREMENTS.md, scope 2026-10-15: MVP1 has "no actuators,
   pulleys or gearing". The legal alternatives either cost or are not modelled:
   * a rack and pinion is gearing;
   * a floating stage 2 is an undriven coordinate (R17), and its worst-case envelope is the rigid rail's;
   * a crossed-roller cage (rolling elements only) makes the moving stage a part of link 2 that runs behind the
     carriage and past the anchor, across strap 1's path (not modelled);
   * the rigid rail at the same axes needs 209 mm (above).

   Until a legal 2:1 drive is modelled, **every telescopic number here (63.72, 57.19) is an MVP2 number, not an MVP1
   one.**
2. **The pose that jams.** Every pose lost at k1530 is a fold of the 3R (fold margin 2.1 to -28.8 deg), none to the
   rail travel or to K6:
   * rest 57/57;
   * overhead (elevation >= 140) 11/17: 6 folds, at elev 150 in plane 30 with axial 0, and in planes 90-120 with axial
     -90 to -135 (k172: 4 folds + 2 K6);
   * across the body (plane >= 90, elevation >= 45) 37/48, 11 folds;
   * behind the back (plane <= -30 or axial >= 60, elevation < 50) 29/29.

   The fold sits in the overhead / across-the-body corner with the arm internally rotated; on this bench that is the
   gap's remaining reach term.
3. **The point that pinches** (closest metal over the taken poses at k1530):
   * strap 1 at 2.01 mm (pose 123), neck 2.00 (pose 148), hub 3 2.25, rail 2.31, hub 1 2.45, stage 2 2.60; no contact.
   * Part-part gaps between parts that move relative to each other:
     * bridge over the neck (the J3 scissor) 2.2 mm at pose 102 (plane 0, elev 105), 29-31 mm over the skin. A finger
       pinch, not a skin one.
     * stage 2 over the neck 10.0 mm at pose 76 (plane -45, elev 45, axial 30), 9-16 mm over the skin. This is the one
       moving gap near the skin, and it is wider than the 8 mm a skin fold needs to be caught.
     * strap 1 vs stage 2 4.9 mm, 30 mm or more over the skin.
4. **The numbers that are optimistic.**
   * (a) Grid vs exact: the verifier measured k172 at 64.70 exact vs 63.72 on the grid (+0.98). k1530's exact number is
     in the queued large-bench job.
   * (b) The brief says rail-elbow "beats the champion on the same large bench" at v_gap 64.70. That 64.70 is
     **Bench(60,160)** exact, not Bench(110,360). The large-bench re-measure (k172 and k1530, exact, 1 mm radial part
     clearance, refit and frozen; `tools/concept_bigbench.py`) is queued on the farm.
   * (b2) **Measured on the farm: k172 on Bench(110,360), exact, 1 mm radial (`tools/concept_bigbench.py`).**
     * Its own (60,160) exact fit reproduces the verifier's 64.70.
     * **Frozen** (geometry fitted on (60,160), scored on the 470 poses): **gap 72.84** (score 73.51). reach 0.817,
       follow 0.991, in-band 14 0.265, in-band 10 0.153, contact 0.010, closure 0.885, K6 2.2 %, honest.
     * **Refit** on (110,360) is degenerate: 86.63, dishonest. At q 1.0, poses with no clearance push the bridge and
       the neck to 400 mm (11.5 mm sampling).
     * Against the champion's 75.94 (same bench and checks), k172 is still 3.1 points ahead on the large bench, but
       the large bench costs it 8.1 points over the brief's 64.70.
   * (c) The rail hardware:
     * The centreline radius is 54 mm at k1530 (40 mm at k172). docs/research/ring_and_shell_hardware.md finds no
       catalogue curved guide at 45-65 mm: THK HCR needs R >= 100, and the Hepco R12-93 is rated 1.25 N.m against the
       25 N.m needed.
     * The custom options there stack about 10 mm (wire race) to 10.4 mm (V-wheel), against the model's 9 mm
       carriage, and two of them side by side are needed for the telescope.
     * 176 deg of open arc is a curved cantilever on link 1 (twist not modelled).
   * (d) Not modelled, all of which would make it worse: the 2:1 drive and its parts, the roller housings, the stage-2
     end stops' strikers, and the 1 mm radial part clearance. The last costs nothing at k172 on Bench(60,160): K6 is
     1.96 % at both 0.5 and 1 mm.

### Update: stream C, the final gate, and k1530 on the large bench

**Stream C** continued B's basin from its best (sigma 0.2, seed 13, 393 tries, $0.02, stage `cma2-C`, k1850-k2242). It
collapsed at **k2221: gap 56.25 (score 79.55)**, honest, audit clean, r_lay 127 (fix point holds).
* Metrics: reach 0.900, follow 1.000, in-band 14 0.338, in-band 10 0.209, contact 0, K6 0.5 %, fold margin 10.1, 170 g.
* Parameters: az 28.66, el 80.93, a1 82.50, a2 65.43, W (94.18, -0.99), d_off -54.26.
* Rail stages are again 0 % in band; hub 3 0.68, neck 0.66.
* The plain 3R at these axes scores **51.33** (score 81.3; reach 0.894, in-band 14 0.393, in-band 10 0.240, contact 0).

**Final gate over all 1926 CMA tries** (polish, then A and B interleaved by generation, then C): the best gained
0.48 pt over the second half (< 1), 0.38 pt over the last third (< 0.5), and the top 5 are within 0.01 pt.
**Converged** at 56.25.

**k1530 on Bench(110,360), exact, 1 mm radial (farm, `tools/concept_bigbench.py`):**
* Its own (60,160) exact fit: 57.85 (grid 57.19, +0.66).
* **Frozen: 64.52** (score 76.54). reach 0.828, follow 1.000, in-band 14 0.334, in-band 10 0.195, contact 0.007,
  closure 0.877, K6 0.2 %, honest.
* Refit: 97.53, degenerate (q 1.0 with no-clearance poses, dishonest sampling).
* That is 11.4 points ahead of the champion's 75.94 on the same bench and checks. k2221's large-bench run was not made
  (the morphology is refuted by the control); the 3R control at k1530's axes on the large bench is in the farm queue.

### Verdict (stage 1)

**Refuted as a morphology; the axis search it triggered is the finding.**
* The sweep is converged: 56.25 at k2221 (57.19 at k1530 in the other basin), gate passed over 1926 CMA tries.
* That number needs a cable-driven telescope, which MVP1 forbids.
* The MVP1-legal rail reaches 59.34 (not converged) by shrinking into a hub.
* At the same axes, the plain spherical 3R beats every one of them by 4-5 points (51.33 / 51.97 / 55.40 / 59.46).

Do not take rail-elbow to L1 CAD. What should happen next (the loop):
1. CMA of the plain 3R (`_template.py`, or the champion's own builder) from k2221's and k1530's axes, with width, t_link and
   neck_deg free.
2. The Bench(110,360) exact re-measure of the converged 3R.
3. L1 keep-out CAD of that 3R (the champion pipeline: `pipeline/full-exo/designs/...`, `tools/judge_all.sh`).
4. The outside judges (R1 aim 2-10 mm >= 90 %).

The arm-end in-band (hub 3 0.75, neck 0.68) is where the new axes win, so the CAD should check those parts first.
