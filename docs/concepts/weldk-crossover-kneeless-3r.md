# weldk-crossover-kneeless-3r - kneeless welded crossover 3R (cx 0, no knee)

Round 301 (O1, overhead track), lens drive-free-cone, minimum-parts branch. Model:
`docs/concepts/models/weldk-crossover-kneeless-3r.py` (loads the sibling `weldk-overstrap-pinknee-3r.py` - itself the
H1 pin-knee model loaded unchanged - and turns the knee into one rigid bracket). Sweep:
`docs/concepts/sweeps/weldk-crossover-kneeless-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Prove the knee is dead weight here
   before deleting it: with J1, J2, J3 all on GH rays the cuff drift s is identically 0, so the knee angle is constant;
   the model ASSERTS ptp(knee angle) < 0.5 deg and |s| < 0.05 mm on every bench pose (else dishonest) instead of
   assuming it. (b) Price the crossover where it is born - link 2 turns about J3 under the bracket's E leg, so the E
   underside is computed from link 2's measured top in member 3's frame over every kept pose (plan-view stacked-pair
   rule, +0.15 mm), not assumed flat. (c) Kill fast: the sibling (weldk-overstrap-pinknee-3r) died on the E strap's
   in-band (0.48 < 0.80) and on hub 3 diving into the bunched deltoid at the cone; measure both FIRST at this J3 ray
   (105, 10), which is higher and more posterior than the sibling's station, and stop if they repeat. (d) Read the
   rigid cuff honestly: the GH-centre misfit a rigid bracket pushes into the liner (no knee to absorb it) is a red-team
   number reported next to the bench (the K1 no-slide reading, 3 mm liner budget).
2. **Rawest material.** The posed skin itself (concept_bench exact signed distance on the posed body mesh, CB_EXACT=1
   for the claim), the 10 fps motion clips for q1..q3 continuity, the Bench(110,360) workspace poses (28 overhead,
   elev >= 140; 85 at elev 90-140) - not the ghost's digest (dfc2/park_wk.py is the prior only; the judge's H1 control
   puts its bias at +13 ws / +5 overhead).
3. **Methods and tools.** H1's exact closed-form spherical IK (three GH rays -> exact closure), the seed VModel honesty
   rules (closure, continuity, jam rule, 1 mm non-adjacent / 0.15 mm adjacent), sphere-traced skin heights on
   1 pt / 4 mm2 samples, <= 60 deg ramps, O20 v5 hubs, the kit fold margin (5 deg of th); a coarse LHS + CMA-ES on
   Bench(60,160) fast with the 1 mm near-touch objective (local, farm closed); the frozen-shape protocol (fit 60/160
   fast, wear on 110/360 exact) for the claim; the GH-offset misfit red team.
4. **What shows the number is right, other than me.** The bench (outside judge), the frozen exact read through the
   same code path that verified H1 (27.20) and reproduced the sibling, the knee-rigidity assertion, and a red-team pose
   list (the lead's 28 overhead poses by index, cone 209/210/211/236/237/238/263/264/265/292, the shell poses
   205/235/262, rest / across / behind groups) for the adversarial verifier.

## Results (2026-10-19, round 301 screen; local CPU only, farm closed, box load ~25 on 4 cores)

**Verdict: fails the judge's gate.** Best fast fit **31.83** on Bench(60,160) (sweep k82, CMA; near-touch 1 mm 34.18,
2 mm 48.36), worn FROZEN on Bench(110,360) exact: **37.42** (score 86.4; reach 0.6833, follow 0.9364, ib14 0.8129,
ib10 0.4343, contact 0.0568) against pass <= 27.20 and kill > 28.46. Near-touch: min metal 0.13 mm, gap with metal
< 1 mm as contact 41.96 (7 poses), < 2 mm 63.02 (33 poses; the lead 34.84). Overhead (elev >= 140, ws) **6/28** (the lead
8/28, H1 5/28): 2 of the 6 under 1 mm (289 at 0.13, 318 at 0.35), 3 in 1-2 mm (263 1.23, 371 1.32, 291 1.42), one at
2.82 mm (344) - overhead bought in the shell. Elev 90-140 band 43/85 (the lead 39/85). Not taken (470 poses): fold 93,
contact 21 (penetration sum 145.3 mm, max 27.15 mm - the T5 depth is x7 the lead's 20.24), part jams 7 (all L2-hub1).
Min th margin over taken poses 5.757 deg. Fast -> frozen +5.6 (deltoid-crest's basin over-read 11-14; this one less).
Complexity 0 (3 hubs, 3 bodies, no knee, no K, no drive, no stop), 0 passive DOF, 0 passive translations. Knee rigidity
asserted on every bench: knee angle ptp 0.000 deg, |s| max 0.000 mm (the three hub lines meet at GH, c = [0, 0, 0]).

| read | gap | reach | follow | ib14 | ib10 | contact | overhead /28 |
|---|---|---|---|---|---|---|---|
| fast fit Bench(60,160) k82 | 31.83 | 0.7438 | 0.9167 | 0.8152 | 0.4270 | 0.0440 | (fast 1/12) |
| frozen exact Bench(110,360) | **37.42** | 0.6833 | 0.9364 | 0.8129 | 0.4343 | 0.0568 | 6 |
| held out (frozen exact, tools/osn_polish.py held_bench(110,360): disjoint 110 clip frames + 360 ws) | 34.59 | 0.7000 | 0.9455 | 0.8093 | 0.4219 | 0.0507 | 4/26 (all in 1-2 mm) |

The held read is the disjoint-complement bench of tools/osn_polish.py, not the verifiers' held set with 71 overhead
poses (not run here). Held: min metal 0.11 mm, 1 mm 37.31, 2 mm 60.34, contact 19 poses (sum 126.8 mm, max 29.79),
min th margin 5.485 deg, elev 90-140 band 42/86.

### What limits it (measured)

1. **The abduction cone is a METAL wall here, not a fold.** Every cone pose of the lead's list closes kinematically at
   this J3 ray (th margin 6.5-39 deg at 209, 210, 211, 236, 237, 238, 264, 265, 292, 290, 317) and every one of them is a
   skin CONTACT worn frozen; only 263 is taken, at 1.23 mm. The re-aimed J3 opens the cone kinematically exactly as the
   ghost said; the real hub 3 / bracket metal at its fitted level does not clear the bunched deltoid there (the
   sibling weldk-overstrap-pinknee-3r measured the same wall per part: hub 3 at -7.9..-25.6 mm at these poses; the
   per-part split was not re-measured on this model).
2. **The fold ceiling.** Kinematic scan (closure + 5 deg th margin + continuity, no metal) over 54 seat cells
   (a1 39.5-40.5, a2 54.5-60, J3 ray d 100-109, a 4-14, J1 at the lead's seat) on Bench(110,360): best 277/360 ws
   (0.769), overhead 18-19/28, clip follow 0.95; the spec's cell (40.5, 57.22, 105, 10) 273/360, 18/28, clips 0.973.
   So even perfect metal leaves a reach gap >= 13.1 here; the frozen best takes 246/360 (93 fold incl. clips, 21 contact).
3. **Hub-3 obliquity (b3 0).** Hub 3 in band 0.78, hub 2 0.73 (parked over the pure-abduction poses; dg pre-drop 20.4
   mm is the design's explicit parking choice, dropped poses count as contact). E leg 0.78, L2 0.75.
4. **The rigid cuff (K1 no-slide reading, red team).** With the bracket bolted at rest, a constant 3 mm GH-centre
   error (tracking / humeral-head translation) gives a cuff misfit of median 3.40 mm, p90 4.83, max 5.90 over the 470
   poses: only **38.7 %** of poses within the 3 mm liner budget (one humeral slide: 40.2 %; a planar knee in hub 3's
   plane would leave median 2.44, 71.7 % within). At 5 mm: median 5.67, 17.7 % within. The knee deletion is free on
   the bench (s = 0 exactly) but it is NOT free on a real arm.

### What I built (and changed against the spec)

- Model: the sibling's crossover code path (H1 underneath, unchanged) with b3 = 0 forced, the knee window dropped, the
  boss / pad / former knee link at ONE bracket level (3.0 mm plate), knee-E and pad-E pairs dropped (one body),
  bracket-hub 3 >= 0.15 mm and E-over-link-2 stacked >= 0.15 mm kept (stacked minimum over taken poses 0.15 mm), the J2
  rest seat solved exactly from (a1, a2, branch -1) on the two cones (spec: az2 26.90 el2 45.80 reproduced).
- **Spec correction (measured): the "pad leg along the arm 60-110 mm" is wrong for a rigid bracket in hub 3's plane.**
  With b3 0 the plane is oblique to the arm and a pad 60-110 mm out sits 16-32 mm off the skin (pad in band 0.0 in all
  32 configurations with lc >= 12; knee leg 0.05-0.54). Moving the pad to the end of a long skin-following E leg
  (lE ~70-78, lc 1-8) took the same seats 50.26 -> 46.36 at once and the CMA to 31.83 (pad 0.82, leg 0.83 in band).
- The CMA left the spec's J3 ray: wd 108.6 / wa 6.1 (spec 105 / 10), a1 39.6, a2 52.6 (spec 40.5 / 57.22). At equal
  bracket the spec's ray read 47.62 fast vs 46.36.

### Search and gate

LHS 22 (two seeds; the first, spec-bounded, had pad legs to 110 mm) + CMA-ES (pop 8) 10 configurations (stopped to fix
the pad leg) + 2 direct pad-at-E-end checks + two CMA-ES runs of 5 generations (80), 114 configurations, Bench(60,160) fast, objective = the 1 mm near-touch gap. Gate on the plain fast gap: +1.40 score
points over the second half, +0.17 over the last third, top-5 spread 0.21 -> NOT converged (the second-half gain is the
pad-leg correction landing mid-sweep). On the near-touch objective: 0.97 / 0.50 / 0.27 (borderline). Status stays
"screened": the convergence rule forbids "dead", but the frozen read is 9 points over the kill line and the measured
ceilings (kinematic 0.769 reach, the cone a metal wall at 0 cone takes) say more tries in this cell will not reach 27.20.

### Red-team pose list (for the verifier)

Overhead takes in the shell: 289 (0.13 mm), 318 (0.35), 263 (1.23), 371 (1.32), 291 (1.42), 344 (2.82). Cone contacts:
209, 210, 211, 236, 237, 238, 264, 265, 290, 292, 317. Deepest contact 27.15 mm. Part jams: L2-hub1 x7. Claim files:
the row's `exact_frozen` / `held_frozen`; per-pose overhead list in the row (`exact_frozen.extras.overhead_poses`).

### What this predicts beyond this morphology

- A knee-less spherical 3R with every axis on a GH ray cannot put its cuff bracket in hub 3's plane far from hub 3: the
  plane is oblique to the arm, so a rigid bracket must follow the skin as a profiled leg and bolt close to hub 3.
- Re-aiming J3 opens the abduction cone kinematically (18-19/28 overhead closes at every cell scanned) but the cone is
  then lost to metal, not to fold: overhead needs a hub-3 / bracket that clears the bunched deltoid at elev 150-165,
  i.e. a metal-level lever, not another seat.
- Deleting the knee costs ~2x the liner misfit under a 3 mm GH-centre error (38.7 % vs 71.7 % of poses within 3 mm).

Next: no further search in this cell (recommend stop). The lever that survives is item 1: a cone-clear hub 3 (lower
stack or a hub-3 seat off the bunched deltoid at elev >= 150) on any 3R that already closes the cone kinematically.

## Verification (2026-10-19, independent verifier, local CPU)

Harness: `docs/concepts/verify/weldk-crossover-kneeless-3r.py` (the model's own `frozen()` run unchanged, then the
added checks V1-V7 and the continuity flood) and `docs/concepts/verify/weldk-crossover-kneeless-3r_el2.py` (an exact
E-leg / boss vs link-2 solid test). Results: `docs/concepts/verify/weldk-crossover-kneeless-3r_v_bench_frozen.json`,
`..._v_held_frozen.json`, `..._v_el2_bench.json`, `..._v_el2_held.json`; per-pose dumps
`docs/alignment/remeasure/weldk-crossover-kneeless-3r_bench_perpose.json` and `..._held_perpose.json`. In each dump,
`poses` is the model's frozen wear, which recomputes 37.42 / 38.52, and `verified_poses` is the wear after the kd removals.
The bench is Bench(110,360) exact (CB_EXACT=1); the shape is fitted on Bench(60,160) fast and then frozen.

**v_gap 37.42 (score 86.4)** reproduces the claim to the digit: reach 0.6833, follow 0.9364, ib14 0.8129, ib10 0.4343,
contact 0.0568. The per-pose dump also recomputes 37.42.

The champion scores 66.97 on the same bench with the same base checks. That is the offset-skin-normal-3r verifier's
champbig_frozen, the number H1 and the sibling's verifications used. It was not re-run: the box was at load 22-25.

**Not refuted.** No hard rule is broken, and the design beats the champion by 29.6 points. It still fails the round's
gates: the kill line 27.20, follow 0.95, and the track bar (the lead's 18.28).

**Held out (the verifiers' set).** This is `docs/concepts/verify/skin-normal-3r-pin-knee-polish.py` held_bench(): 202
clip frames and 952 ws poses, 71 of them overhead. It is not the claim's osn_polish set.
- Frozen reading: **38.52** (reach 0.6754, follow 0.9406, ib14 0.8086, contact 0.0598).
- Overhead: **14/71**, against the lead's 18/71. 11 of the 14 takes sit in the 0-2 mm shell (4 under 1 mm).
- 2 mm reading: 64.43 (the lead's 37.11).
- Contact: 53 poses, depth sum 309 mm, max 29.79 mm.
- Min th margin: 5.092 deg.

Checks added, each run over every taken pose (349 on the bench, 833 held):

- **ACTIVE DOF.** 3 (J1, J2, J3, all O20 v5), 0 passive, 0 passive translations. Nothing is left undetermined.
  - The three hub lines meet at GH (offsets c = 0, 0, 0 mm).
  - V1 rigid-cuff test: member 3 (the bracket), member 6 (the former knee link, now the pad leg) and member 5 (the
    pad on the arm) are ONE body to 0.024 deg / 0.000 mm on every taken pose, bench and held, and move with the arm
    pose to 0.024 deg.
  - The model's knee_rigid flag holds: ptp 0.000 deg, s 0.000 mm.
  - Hub-3 centre closure is 0.000 mm and the J3 axis agrees to 0.016 deg.
- **Inverted J3 stack (V2).** The pad leg and the pad clear hub 3's lower plate (link 2's half) by at least 53.0 mm
  and 50.0 mm.
- **Bracket boss vs hubs 1-2 and link 1 (V3).** These pairs are not in the model's collide. Minimum 7.23 mm on the
  bench (ws 184) and 7.21 mm held.
- **Margins and levels (V4).** Min th margin 5.757 deg on the bench and 5.092 held, in the kit metric. Hub levels are
  50.4 / 63.7 / 62.7 and the bracket sits at 53.4, all under the 140 cap. No pose is removed.
- **Continuity flood (V6).** Full 1432-pose grid, 2-deg slerp edges, 10-deg joint jumps, branch sign. All 1054 / 1054
  kinematic nodes are connected: 0 islands, one branch. Static reach equals connected reach.
- **E leg vs link 2 (V7 and the exact test).**
  - H1's kd test (1.5 mm spheres on mid-surfaces) reads below 0.15 mm on 13 taken bench poses (15 held): -0.23 mm at
    ws 208, -0.21 at 205, 0.13 at 257 / 184 / 259 / .... Removing them gives **41.23** on the bench (reach 0.6472)
    and 40.19 held. This is the conservative bound.
  - The kd test is pessimistic for two 3 mm plates that cross at an angle. Two plates stacked 0.15 mm apart and
    tilted by t read 1.65 cos t - 1.5 mm, i.e. 0.13 mm at 10 deg.
  - The exact solid test models the E leg as its fitted x-z profile extruded over |y| <= 4, plus the O12 boss
    cylinder. Link 2 is its fitted shell, extended to its true +-4 mm edges and densified to 0.1 x 0.2 mm, with top,
    underside and side faces.
  - Exact result: **0 clashes** on the bench. The minimum is 0.150 mm, the model's binding stacked rule; 4 poses read
    0.1499x, i.e. float equality. So 37.42 stands.
  - Held exact test: **0 clashes** too, so 38.52 stands there. The E leg's distal part (more than 10 mm past the
    hub-3 rim) sits at 0.150 mm over link 2 on held ws 392, 398, 457, 525 and 530, and at 0.17 mm on 453 and 440.

Red-team findings (none changes the verified number):

1. **The crossover is real here, and it is a 0.15 mm sliding fit 54 mm from the J3 bearing.** Unlike the sibling, the
   E does cross over link 2 on taken poses. The stacked minimum is 0.150 mm on 30+ poses at x ~ 11 mm, just past
   the hub-3 rim, where it is the designed running gap.
   - At ws 205 and 208 (plane 0, elev 105 / 135, axial 15) the E's distal end (x 54.3 mm) sits 0.150 mm over link 2.
     At ws 184 it is 0.171 mm at the boss.
   - A 0.15 mm gap between two bent 3 mm Ti plates 54 mm from a bearing pair is not a running gap. Bearing tilt play
     alone (~0.1-0.2 deg x 54 mm) and bend tolerance close it, so they would rub.
   - Reading E / boss vs link 2 more than 10 mm past the hub-3 rim as non-adjacent parts (>= 1 mm) drops 3 poses:
     **38.29** (reach 0.675). Held, the same reading drops 8 poses: 39.42.
2. **Parameter mismatch in the record.** The row's best_params say lc 6.28, but `clamp()` floors lc at 15.0, and every
   number above (claim and verification) was measured at lc 15.0. The pad leg is 15 mm, not 6. Not an exploit, since
   the stored config reproduces exactly, but the row and doc text should read lc 15.
3. **Overhead does not rise; it falls.** Bench 6/28 against the lead's 8/28, held 14/71 against 18/71.
   - 5 of the 6 bench overhead takes sit in the 0-2 mm shell: 289 at 0.13 mm, 318 at 0.35, 263 at 1.23, 371 at 1.32
     and 291 at 1.42.
   - The 2 mm reading is 63.02 on the bench and 64.43 held, against the lead's 34.84 / 37.11.
   - T5 contact depth: max 27.15 mm on the bench and 29.79 held, about 7x the lead's.
   - This misses the O1 track's aim (more overhead at <= 18.28).
4. **Rigid cuff.** I accept the claimant's GH-offset red team as measured: at a 3 mm GH-centre error, 38.7 % of poses
   stay within the 3 mm liner, against 71.7 % for a planar knee. A real arm's humeral-head translation loads the
   liner. This is not a bench rule. It is the K1 reading's open risk, and it matters more here than on a knee design.
5. **Hub-axis accessibility and sampling.**
   - Every hub axis is a GH ray, with levels 50-64 mm.
   - The E leg is sampled at 2 mm pitch (1 point per 4 mm2) on 4 rows inset 1 mm (H1's standard). Hub crowns, the
     E top, the boss and pad rings and the pad-leg box edges are contact-sampled.
   - No part is sampled near the skin only.
   - The kd test is the H1 family standard; it was replaced here only by an exact test, never by a looser one.

Verdict: **verified at 37.42** (kd bound 41.23, far-crossover bound 38.29), champion 66.97 on the same bench.

The claimant's recommendation to stop this cell stands, and the measured limiter is confirmed: the abduction cone
closes kinematically but is lost to hub-3 / bracket metal (11 cone contacts, only 263 taken), on top of the fold
(93 lost).
