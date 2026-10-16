# zc-frontier-3r - the zero-complexity class, mapped globally under the 2026-10-16 rulings

Track "ZERO-COMPLEXITY FRONTIER" of the golden push (user, 2026-10-16 ~05:50 UTC: "The golden solution is something
95% plus with complexity at 0 (or near), please push this through, and get here by any means"). Model
`docs/concepts/models/zc-frontier-3r.py`, search `tools/zc_frontier.py`, data `docs/concepts/zc/`, hub-parking bound
`docs/research/zc/`, motion preview `docs/concepts/viz/concepts/zc-frontier-3r.js`, row `docs/concepts/rows/zc-frontier-3r.json`.

**Target, stated as reasonable:** score >= 95 = gap <= 13.75 on Bench(110,360) exact with the shape frozen from its
fit, at complexity 0. With follow ~1.0 and in-band ~0.90 that is reach >= 0.7625 (>= ~0.78 at in-band 0.88) and ~0
contact.

**Result: the class cannot get there. Measured ceiling: gap 28.85 on Bench(110,360) fast (score 89.5),
**31.04 frozen exact** (score 88.7; shape fitted on Bench(110,360) fast, worn on the exact mesh; 33.51 with the round-3 protocol); the frontier is a measured trade-off, not a search failure** - over 8828 full
evaluations on the verification bench no zero-complexity chain with reach >= 0.7625 has in-band above 0.445, and at
in-band >= 0.88 no chain reaches more than 0.633. The cap is hub 2: the arcs that open the fold window (shorter arc
>= ~45 deg) carry hub 2 over skin whose height along its axis varies by more than the 12 mm band.

## What the class is (complexity 0, tools/simplicity.py)

Three active pins whose axes meet at GH (each an MR117-2RS pair in the v5 O20 hub, 12.25 mm stack), three links
(12 x 3 Ti straps on great circles; member 3 = hub 3's plate + the K7 14 x 6 neck rigid on BOTTOM's bar), nothing
else: 0 passive translations, 0 passive rotations, no springs, no loops, no sensed passives. Every freedom a designer
has inside that class was open, globally:

| freedom | range searched | note |
|---|---|---|
| J1 seat ray bvec(az, el) | the back of the shoulder + the acromion top only (ruling 4): az -110..135, el -20..90, anterior component <= 0.20 | outside it a config is not evaluated |
| J3 seat ray wdir(wd, wa) | the whole sphere (wd 20-175, wa -180..180) | covers which END of the J3 line carries the hub |
| arcs a1, a2 | 12-168 deg | an arc > 90 is the hub on the far end of the J2 line ((u1, a1, a2, u3) == (u1, a1, 180 - a2, -u3) kinematically; the fold band is sign-invariant) |
| branch sigma | +-1 | |
| J2 / J3 stack order (inv2 / inv3) | normal or inverted | inv3 = the j3-neck-over stack: link 2 on hub 3's lower plate, member 3 on the cap plate bridging over it |
| underside quantile q, strap end hold | 0.8-1.0, 0-8 mm | as in the polishes |
| fixed by the rules | O20 at every joint (ruling 2), fold margin 5 deg (ruling 1), 12 x 3 straps, 1 mm radial K6 | never loosened |

Checks = the spine-parked model's (kit K1-K7 + dense K2, hub crown / wall skin check) + the spine-parked verifier's
`top_check` (top faces of every member, near-touch over all faces, closure residual, hub-axis accessibility F <= 140
mm), unchanged; the objective is the verifier's plain gap, the near-touch gap (metal < 1 mm = contact) is logged
beside it. Search bench = Bench(110,360) fast (the farm's grid cache 14f156cb6fc8), shape fitted there; claim = that
shape frozen and worn on Bench(110,360) EXACT, plus the round-3 verifier protocol (fit Bench(60,160) fast -> worn
Bench(110,360) exact) for comparison.

## 1. The global map

* **Fold law over the allowed seats (16384 Sobol configs, 360 workspace poses, margin 5):** 3560 (22 %) close >= 0.7625
  of the workspace kinematically - the J1 seat barely matters (21-23 % in every az / el band), the arcs do: with the
  effective shorter arc min(a1, a2, 180 - a1, 180 - a2) < 40 deg only 50 of 9652 configs reach 0.7625 (max 0.878),
  < 45 deg 209 of 10932; the kinematically viable configs have a median shorter arc of 63 deg (p5 44).
* **Proximity over the kinematically viable set (all 3560 + 700 below + 8 seeds evaluated on the verification bench,
  4268 configs):** 3639 have a hub whose axis line meets no skin within 170 mm (hub 2 in 2367, hub 3 in 2462, hub 1 in
  1126; the hub would float - prescreened, the same verdict the hub_F <= 140 rule gives); of the 235 kinematically viable
  configs with all three hubs on the body, in-band 14 is at most 0.669 (median 0.32; hub 2 median 0.06, link 2 0.09).
  The best random config scores 89.02; the seeds at the old leaders' seats score 39.01 (inv3) - 43.08 (normal).
* **Hub-parking bound (`docs/research/zc/hub2_bound.py`, 7130 configs with fold-law reach >= 0.5, Bench(60,160)
  fast):** a complexity-0 hub is one disc at one level on its axis line, so its centre can be in band only at poses
  whose skin exit lies within 12 mm below that level. Best single-level share for hub 2 among configs that reach
  >= 0.7625 kinematically: max 0.98, p99 0.88; all three hub centres >= 0.9 at once: 0 configs (>= 0.8: 2, both with
  hub 3 at 130-184 mm down the arm - the full model, with the disc rims, scores them 113-193: hub 3's tilted disc and
  link 2 never reach the band).

## 2. Multi-start CMA on Bench(110,360) fast (8 + 6 streams)

| stream | start | evals | best gap | where it went |
|---|---|---|---|---|
| A / A2 | local Bench(60,160) CMA best at the leader seats (27.25 fast small bench) | 297 / 121 | 32.76 / 34.55 | stays at a1 38-40 |
| Ainv0 | same, normal J3 stack | 489 | 37.01 | inv3 is worth ~8 here (link 2 0.74 -> 0.88 in band) |
| **Awide** | same seats, a1 forced to 52 | 977 | **28.85** | walked back to a1 36.7 (the wide window costs more in-band than it buys reach) |
| C | best wide-window sweep basin J1 (47, 66), a1 59 / a2 93 | 937 | 64.94 | reach 0.6-0.7, hub 2 out of band |
| D | J1 (48, 3), 68 / 80 (sweep reach 0.778) | 833 | 72.28 | |
| E | J1 (34, 10), 57 / 66 | 633 | 71.09 | |
| F | posterior-low J1 (-15, -12), 70 / 78 (the "kinematically best seats" family) | 273 | 74.06 | |
| R2A-R2F | convergence round from 28.85 (sigma 0.25-0.6, 6 seeds) | 1446 | 28.85 | no stream improved by 0.05 in 30 generations: **gate passed, converged** |

**Best: J1 bvec(109.36, 65.94) (acromion top), J3 wdir(85.74, -16.19) (lateral deltoid), a1 36.72, a2 69.06, branch
-1, inverted J3 stack, q 0.978, strap end hold 1.78 mm** -> 28.85 on Bench(110,360) fast (reach 0.633, follow 0.955,
in-band 14 0.890, contact 0.012; near-touch 38.14). Per member in band: hub 1 0.98, hub 2 1.00, hub 3 0.82, link 1
0.95, link 2 0.88, neck 0.81.

**The trade-off curve (Bench(60,160) fast, short CMA per fixed a1 from the same seats, `docs/concepts/zc/slice_a1.json`):**

| a1 (deg) | best gap | reach | in-band 14 | contact | hub 2 level F | hub 2 / link 1 in band |
|---|---|---|---|---|---|---|
| 38.2 (free) | 27.20 | 0.681 | 0.875 | 0.029 | 60 mm | 1.00 / 1.00 |
| 46 | 43.77 | 0.663 | 0.809 | 0.109 | 64 mm | 0.90 / 0.91 |
| 54 | 55.55 | 0.731 | 0.615 | 0.102 | 86 mm | 0.06 / 0.56 |
| 62 | 67.36 | 0.694 | 0.573 | 0.141 | 107 mm | 0.01 / 0.37 |

Every 8 deg of link-1 arc buys at most +0.05 of reach and costs 0.07-0.2 of in-band and 0.04-0.08 of contact: hub 2
must clear the highest skin its axis sweeps (60 -> 107 mm), so it floats over the rest.

**Frontier over all 8828 evaluations (sweep + round-1 CMA, Bench(110,360) fast; the 1446 convergence evaluations add nothing):** max reach at in-band >= 0.90 / 0.88 /
0.85 / 0.80 / 0.70 / 0.60 / 0.50 = 0.611 / 0.633 / 0.639 / 0.644 / 0.667 / 0.689 / 0.722; max in-band at reach >=
0.70 = 0.597, at reach >= 0.7625 = 0.445. On this frontier the gap is never below ~28.7 (in-band 0.88, reach 0.633),
which is what the CMA found.

## 3. The claim (frozen exact) and where it loses

| protocol | gap | score | reach | follow | in-band 14 / 10 | contact | near-touch gap | min metal (any face) |
|---|---|---|---|---|---|---|---|---|
| search: fit + wear Bench(110,360) fast | 28.85 | 89.5 | 0.633 | 0.955 | 0.890 / - | 0.012 | 38.14 | - |
| **claim: fit Bench(110,360) fast, frozen, worn Bench(110,360) EXACT** | **31.04** | **88.7** | 0.622 | 0.955 | 0.891 / 0.447 | 0.024 | 38.03 | 0.09 mm |
| round-3 protocol: fit Bench(60,160) fast, frozen, worn Bench(110,360) exact | 33.51 | 87.8 | 0.617 | 0.936 | 0.892 / 0.430 | 0.030 | 40.57 | 0.02 mm |

| out of sample: same frozen shape worn on ALL 1432 workspace-envelope poses + 110 clip frames, exact | 35.04 | 87.3 | 0.5957 | 0.9545 | 0.8911 / 0.4472 | 0.0372 | 42.94 | 0.04 mm |

Data `docs/concepts/zc/frozen_round1.json` (farm job zc-frozen-r1, 357 s) and `docs/concepts/zc/frozen_oos1432.json` (1072 of
the 1432 workspace poses never seen by the search; fold-law reach 0.6459, overhead 0.3796; the
spine-parked O15 polish read 36.82 on the same out-of-sample set). Honest, audit empty, hub levels F 51 / 58 /
71 mm (all accessible). Not yet re-measured by an independent verifier: the next step is the verifier run on these
params (the spine-parked verifier's checks with this build; the params are plain - inv3 is the only non-spine-parked
freedom).

**Every lost pose by first cause (claim run, Bench(110,360) exact; `attribute()` in the model):**

| region | n | taken | fold, folded side | fold, stretched side | jam (K2) | parts | contact (member) |
|---|---|---|---|---|---|---|---|
| workspace | 360 | 224 | 44 | 77 | 0 | 7 | 8 (link 2 3, hub 3 2, hub 2 2, neck 1) |
| clip frames | 110 | 105 | 0 | 5 | 0 | 0 | 0 |
| overhead (elev >= 140) | 28 | 6 | 7 | 11 | 0 | 0 | 4 |
| across the body | 68 | 19 | 0 | 49 | 0 | 0 | 0 |
| behind the back | 25 | 20 | 1 | 3 | 0 | 0 | 1 |

The fold takes 121 of the 136 lost workspace poses (89 %); the window is [37.3, 100.8] deg against a workspace
J1-J3 angle of 25.3-143.3 (5-95 %), kinematic reach 0.664 (overhead 0.357). In-band by member: hub 1 0.98, hub 2 1.00,
hub 3 0.82, link 1 0.95, link 2 0.88, neck 0.81 - hub 3, the neck and link 2 hold in-band at 0.89; the metal that
touches (2 top-face poses on hubs 1 / 2, one hub crown) sits at 0.09 mm.

## 4. The ceiling, and why (the input of the near-zero track)

* **Kinematics alone is not the cap.** Under the seat rule at margin 5, 22 % of the space closes >= 76 % of the
  workspace; the plain 3R can reach 1.0 kinematically from back / acromion-top seats.
* **Hub 2 is the cap.** Reach >= 0.7625 needs the shorter arc >= ~45 deg (fold-law map); at those arcs hub 2's axis
  (fixed by the closure, one rigid level) sweeps skin whose exit height spans far more than the 12 mm band (F 60 ->
  86 -> 107 mm as a1 goes 38 -> 54 -> 62), or leaves the body (2367 of 3560 viable configs). Link 1 follows it out
  of band (1.00 -> 0.56 -> 0.37).
* **The cap at the measured optimum (a1 ~37):** the fold. 121 of the 360 workspace poses fail the fold window
  (44 folded side, 77 stretched side - across the body 49 of 68 stretched), overhead is reached at 6 of 28 (7 folded, 11
  stretched, 4 contact). The members that cap in-band
  are hub 3 (0.82), the K7 neck (0.81) and link 2 (0.88).
* **So the zero-complexity class tops out at gap 28.85 fast / 31.04 frozen exact (score 88.7) on the verification
  bench**, ~6.6 points behind the complexity-19.5 pin knee's polished 24.48 (verified, margin 5). What 13.75 needs is reach
  +0.13 at the same in-band, i.e. a second fold window or a hub 2 that can change level: a two-state arc relay
  (kinematic 0.93-0.95) or a fourth joint, each judged by where hub 2 parks in the poses it rescues. A radial give at
  hub 2 (a slide along the J2 axis so the hub rides the skin) is NOT a way out: the level spread it would absorb is
  26-47 mm (F 60 -> 86 -> 107 mm), and a skin-normal slide stands up by its travel + block length (CLAUDE.md), which
  breaks the 1 cm envelope by itself.

## Deeper version (answered before modelling)

1. **What a top designer would do that the brief does not ask for.** Map the class kinematically first (cheap, the
   fold law), then spend the expensive bench only where the fold law allows 0.7625; prescreen the hubs whose axis has
   no skin exit (they float); hold every verifier check fixed; and test the "both ends of every axis line" and
   "stack order" freedoms explicitly, since they are free in complexity.
2. **The rawest material.** The posed skins of Bench(110,360) (signed-distance grid cache on the farm, exact libigl
   path for the claim), the 10 fps fit clips for dense K2.
3. **Instruments.** concept_kit K1-K7, the spine-parked verifier's top_check, Sobol (scipy.stats.qmc), CMA-ES on the
   farm (tools/cloud_run.py batch, <= 8 slots).
4. **Who else shows the number is right.** The bench; the verifier's checks (unchanged); the frozen exact run; an
   independent verifier re-run of the claim (requested, not done by this track).

## Red team

* **Far-end hubs at the optimum (`docs/concepts/zc/far_ends.json`, Bench(60,160) fast):** the same axis lines with the
  hub on the other end of the J2 line, the J3 line or both close exactly the same poses (fold-law reach 0.681 in all
  four) but the far-end hub has no skin within reach along its axis (F 400 mm sentinel: it would float on the chest /
  axilla side): 343.7 / 400.4 / 461.9 vs 30.04. The near ends are the only buildable ones here.
* **Link routing was not a continuous freedom here** (straps on great circles, underside fitted to the skin); the
  raglan measurement on the knee chain (docs/FINDINGS.md "Raglan routing") put routing at +0.4 real. Routing cannot
  move hub 2, which is the cap.

* The search bench and the claim bench are the same 470 poses (the shape is fitted on the fast grid, worn on the exact
  mesh): in sample. The round-3 protocol number (fit on Bench(60,160)) is reported beside it.
* The fold margin is 5 deg (the user's MVP1 rule): the added poses sit at sigma_min 0.21-0.25 (J2 4-5x faster than the
  arm through a 25-36 deg transmission angle) - soft J2 stops at the 5 deg line (docs/research/reach_attribution.md).
* The prescreen (a hub axis with no skin exit within 170 mm) removes configs from the search only, never from a claim;
  the hub_F <= 140 rule it anticipates is the verifier's.
* Hub-parking bound uses the hub CENTRE ray only: an upper bound; the full model (rims, tilt, links) is lower.
