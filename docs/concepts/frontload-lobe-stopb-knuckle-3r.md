# frontload-lobe-stopb-knuckle-3r

Front-loaded stretched lobe + stop B at the K dyad's 5-deg margin (winner re-cut, 2:1 rocker). Round 7, pick 4.
Kill gate (round-7 judge): a re-fitted fast near-touch gap < 16.0 on Bench(60,160). The winner measures 16.53.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the rocker as a real bell crank, not a ratio. A 2:1 rocker puts the rod end on a 10 mm arm, and that arm has
     to sit at the height where the rod can reach K's horn. The rod must pass over hub K's crown: its centre has to be
     at least the crown top + 2 mm wherever it is within HUB_R + 2 of K's axis. That height fixes the arm level. The
     spec does not ask for this, and the parent model never checks rod against hub K (same body).
   - Make the arm level a design variable (`arm_lo`, the fork's underside above link 1b) and let the crown rule raise it.
     The 2:1 rocker's metal is then priced at its true height, not at a convenient one.
   - Give the law a target, not just a shape. Next to the two-segment law (`seg`), the margin-tracking law (`track`)
     opens K by the least amount that keeps the effective dyad margin m3e = a1e + a2 - th >= smt. Its gain is clipped to
     the pressure-angle cap, it never closes K, and the law ends on stop B.
   - Clamp what the catalogue clamps:
     - horn >= 2.45 mm;
     - rocker ratio 1-2.5;
     - lobe base radius 7-8.1 mm;
     - lobe crest <= HUB_R + 1.5 (the winner's crest, 11.3 mm, passed the verifier);
     - a1max <= bk1 + bk2 - 5.
2. **Rawest material.**
   - The posed skin itself: the bench's signed-distance field of the posed body, metal sampled about 1 point per 4 mm2.
   - The motion clips and the workspace poses of Bench(60,160) for the fit, and Bench(110,360) exact for the frozen wear.
   - The winner's own per-part in-band numbers and lost-pose attribution, re-measured here, not copied:
     - stretched_kin;
     - why: fold / slide / contact;
     - the rocker, rod and rod-end samples.
3. **Methods and tools.**
   - The winner's verified model is loaded as its own module copy (docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py).
     Its `_ik_phys`, kit fold rule, VModel checks, capK cap, near-touch report and frozen() are reused unchanged.
   - Only `law()` and the rocker / rod metal change.
   - Searches on the farm (tools/cloud_run.py batch):
     - a 192-configuration LHS over the law, the rocker, stop B, smhi, bk1 / bk2 and the seats;
     - three CMA-ES runs (tools/concept_cma.py, popsize 16, 8 processes), one per law family: seg at i_rock about 2,
       seg at i_rock 1, and track.
   - The objective is the near-touch gap.
4. **What, other than me, shows the number is right.**
   - The bench (tools/concept_bench.py), at the same code path that reproduces the winner's 16.53 exactly with the
     control config (law_mode lin, i_rock 1).
   - The frozen exact wear on Bench(110,360), reported plain and near-touch.
   - The round's independent verifier, using the winner's harness.
   - A red-team pose list: the overhead stretched poses past the law's th_max, the rod against hub K's crown, and K's
     slop from rod-end play.

## Model

docs/concepts/models/frontload-lobe-stopb-knuckle-3r.py. The pressure angle is a function of the law's local gain:
tan(pa) = k(t) r_horn / (i_rock r(t)), where r(t) = r_lobe + r_horn |dK| / i_rock.

## Search

All on the farm, Bench(60,160) fast, objective = the near-touch gap. The CMA starts came from the LHS top.

| run | what moves | tries | best fast | gain 2nd half / last third / top-5 spread (score pts) |
|---|---|---|---|---|
| LHS | law (seg / track), i_rock 0.8-2.5, r_horn, r_lobe, a1max, smhi, bk1, bk2; seats on half | 192 | 17.83 | - |
| CMA A | seg law, i_rock free (2:1 class), seats | 2449 | 16.82 (i_rock 1.45) | 0.04 / 0.02 / 0.00 |
| **CMA B** | **seg law, i_rock = 1 (the 1:1 post), seats** | 1921 | **15.57** | 0.06 / 0.04 / 0.01 |
| CMA C | track law, i_rock free, seats | 945 | 17.23 (i_rock 1.85) | 0.13 / 0.01 / 0.03 |
| CMA D | the winner's linear law, i_rock free, a1max to 64 | 977 | 16.77 (i_rock 1.51) | 0.09 / 0.04 / 0.01 |
| CMA E (control) | the winner's own LINEAR law, i_rock 1, re-fit from B's seats | 2609 | **15.54** (kK 2.27, smhi 18.5) | 0.04 / 0.01 / 0.00 |

Every run passes the convergence gate. Combined over 8901 CMA tries: 0.10 / 0.01 / 0.01. The control E settles on the winner's
own linear law, re-fitted. It matches the front-loaded best fast (15.54 against 15.57), at reach 0.7875 and in-band
0.862.

Best (CMA B):
- Law and drive: law seg, kA 2.900, t1 6.94, kB 2.756, i_rock 1 (the follower post), r_horn 2.471, r_lobe 7.350 (crest
  10.26 mm).
- K's stops: a1max 61.72 (limit 62.62), bk1 30.054, bk2 37.571.
- Margins and seats: smhi 14.767, smlo 5.172, az1 95.359, el1 67.619, az2 42.749, el2 43.903, wd 63.526, wa -10.560,
  b3 0.3825, ang_min 27.861.
- Knee and capK as the winner.

Gates on this config:
- pressure angle 44.3 deg at its peak;
- the law ends on stop B at th 123.3 (dK 67.4);
- the poses taken use K only up to 44.7 deg;
- 71 stretched fit poses taken;
- min metal 1.07 mm.

## Numbers

| config | fast (near-touch = plain) | frozen exact Bench(110,360) | near-touch frozen | reach | in-band14 | contact | overhead | min metal |
|---|---|---|---|---|---|---|---|---|
| the winner (its own metal) | 16.53 | 23.37 (verified 23.57) | 25.01 | 0.7306 | 0.8463 | 0.0106 | 8/28 | 0.45 |
| the winner + the rod-over-crown rule | 16.63 | 23.47 | 25.11 | 0.7306 | 0.8453 | 0.0106 | 8/28 | 0.45 |
| **best (CMA B)** | **15.57** | **22.72 (score 91.74)** | **24.36** | 0.7278 | 0.8556 | 0.0106 | 8/28 | 0.30 |
| best, law made linear (kB = kA) | 16.20 | 22.73 | 24.37 | 0.7278 | 0.8555 | 0.0106 | 8/28 | 0.30 |
| control E: the winner's linear law re-fitted (1:1) | 15.54 | 22.92 | 24.01 | 0.7222 | 0.8619 | 0.0133 | 8/28 | 0.5 |
| best, a1max back to 58.36 | 15.57 | - | - | 0.7937 (fast) | 0.8559 (fast) | - | - | - |

Held out (every fit-clip frame and workspace pose in neither bench, exact; the verifier's held_bench), same frozen shapes:
- best: 26.65 (near-touch 29.29), reach 0.6922, in-band 0.8539, contact 0.0126, overhead 19/71, min metal 0.14 mm.
- winner + rule: 28.02 (near-touch 30.21), reach 0.6912, in-band 0.8435, contact 0.0149, overhead 19/71, min metal 0.21 mm. The verifier measured the claim at 28.12.
- control E (linear law re-fitted): 26.66 (near-touch 29.3), reach 0.687, in-band 0.8602.
- Held-out gain over the winner + rule: 1.37 gap points. Over control E: 0.01. Lost poses held out: best {'fold': 251, 'slide': 25, 'flip': 0, 'closure': 0, 'skin': 0, 'parts': 6, 'contact': 11}; winner {'fold': 252, 'slide': 29, 'flip': 0, 'closure': 0, 'skin': 0, 'parts': 0, 'contact': 13}.

Continuity flood fill on the frozen Bench(110,360) wear. This is the round-6 verifier's connected_report: 2-deg slerp edges, passive
jumps of at most 10 deg, seeds in state A.
- full grid: best 22.72 (0 dropped), winner + rule 23.47 (0 dropped).
- knn grid: best 25.53 (10 dropped), winner 26.0 (9 dropped).
- sparse bench grid: best 46.09, winner 46.55.
The order is the same on every grid.

Lost poses, frozen:
- best: fold 86, slide 7, parts 1, contact 4. Overhead: fold 15, slide 3, contact 2.
- winner + rule: fold 84, slide 8, parts 1, contact 4.

In band per part, frozen (best vs winner):
- hub K 0.976 vs 0.945;
- hub 3 0.598 vs 0.591;
- L2 0.776 vs 0.767;
- rod and rod ends 0.00 on both.

## Attribution

The best config passes the kill gate (15.57 < 16.0). The gain does not come from this morphology's levers. Controls on
the same seats:

- **Front-loaded law: worth 0.01 frozen.**
  - Making the law linear (kB = kA) costs 0.63 fast, which is one fit pose: reach 0.7937 -> 0.7875.
  - Frozen, the linear and the bent law differ by 0.01 (22.73 vs 22.72). The bend fits one Bench(60,160) pose
    (round-3 lesson c).
  - Front-loading harder costs points. kB 2.0 measures 17.25 fast. The margin-tracking law at a 1:1 rocker measures
    16.21-26.65 fast, at smt 14.7 down to 5.5.
  - Front-loading is capped by the LIFT-OFF gate: K cannot open faster than its self-motion slope at fixed th, or the
    spring could hold K at a smaller opening with q2 further on, and q2 would no longer give K. Every tracking law below
    smt 12 ends on lift-off.
- **Stop B raised to the K dyad's margin: worth 0.00.**
  - a1max 61.72 -> 58.36 gives an identical 15.57: the taken poses never use K past 44.7 deg.
  - Stretched fit poses at the best: 80. 59 are taken kinematically, 13 lie past the law's th_max (124-157 deg), and 6
    fail the m3e wall.
  - The law cannot reach those 6 faster because of the lift-off and pressure gates.
  - The raised stop only lengthens the law past th 117-123, where m3e < 5 already rejects the pose.
- **The 2:1 rocker: worse than 1:1, about 1.2 fast points.**
  - The rod must pass over hub K's crown to reach a horn 2.5 mm from K's axis. The long arm's clevis therefore sits
    9-12 mm over link 1b, and its underside is out of band (rocker in band 0.48-0.51 against 0.94).
  - The best 2:1-class configs: A 16.82 (1.45:1), C 17.23 (1.85:1), D 16.77 (1.51:1).
  - At 1:1 the horn >= 2.45 caps the gain at r_lobe / r_horn = 3.0. The optimum uses 2.90 (pa 44.3).
- **Control E settles the attribution.** CMA E re-fits the winner's own LINEAR law (1:1, a1max free) and reaches 15.54 fast,
  against 15.57 for the front-loaded best.
  - Frozen: 22.92 against 22.72 plain, but 24.01 against 24.36 near-touch.
  - Held out: 26.66 against 26.65.
  - The front-loaded lobe and the raised stop B are worth -0.35 to +0.20: noise.
- **What is left: a re-fit of the winner's seats.**
  - az1 +1.8 deg, smhi +1.1, bk1 -1.2, a1max +3.4 (inert), r_lobe 9.0 -> 7.35 (the lobe now sits inside the O20 skirt).
  - Hub K goes 0.945 -> 0.976 in band, and in-band rises 0.845 -> 0.856.
  - Frozen gain over the winner under the same rule: 0.75 gap points (0.85 against the verified 23.57). That is below
    the 1-point bar a polish needs to replace a config.

## Red team

1. **The winner's rod passes 2.6 mm into hub K's crown.** As modelled, its rod centre is 69.2 mm within HUB_R + 2 of K's
   axis, against a crown top of 70.27, so the rod underside is 2.57 mm below the crown. The round-6 verifier's
   correction 2 already found this. Here, the rod-over-crown rule raises the rod end until the rod centre is at least
   the crown top + 2, and that costs the winner 0.10 fast. This model still puts the horn at the cap's mid-height. The
   verifier's horn plate on the cap top would raise the rod further, which costs nothing in band: the rod is already
   0 % in band.
2. **The front-load's fast gain is one fit pose.** It is gone frozen (above).
3. **Min metal.** It drops to 0.30 mm frozen (winner 0.45), and the near-touch gap is 24.36. Three near-touch poses.
4. **Pressure angle 44.3 against a 45 gate**, and lobe crest 10.26 mm, 0.26 past the O20 radius (inside the
   HUB_R + 1.5 the winner's 11.3 already used).
5. **K slop.** At r_horn 2.47, 0.05 mm of rod-end play reads as 1.16 deg of K. That is no better than the winner's,
   because the 2:1 rocker that would halve it costs about 1.2 points.
6. **Force closure** (unilateral lobe contact plus K's clock spring) is the winner's, unchanged. The round-7 judge's
   note 6 stands.

## Verdict

**SCREENED: it passes its kill gate, but by a re-fit, not by its own levers.** The convergence gate passes in all five
runs. The levers were measured with controls:
- front-loaded law: 0.01 frozen;
- stop B: 0.00;
- 2:1 rocker: -1.2 fast.

These levers are dead. The best config is the winner's mechanism (1:1 post, near-linear law) with re-fitted seats:
- 15.57 fast;
- 22.72 frozen exact (score 91.74), 0.75 better than the winner under the same rod rule;
- held out 26.65, 1.37 better.

It is a candidate polish of the winner: 3 active DOF, 0 passive translations, the same complexity. It needs the independent
verifier with its corrected metal (horn plate on the cap top, rod vs hub K) before any claim.

Hand-off to the lead's env-bench polish:
- start from this row's best_params;
- add a1max to the free set, though it is inert here;
- carry the rod-over-crown rule.

New knowledge:
1. On a cam-slaved knuckle, the K opening rate is capped by the lift-off (self-motion) slope, not only by the pressure
   angle. Every margin-tracking law below smt 12 ends on lift-off at a 1:1 rocker. The seg optimum is nearly linear
   (kA / kB = 1.05), and a stronger bend (kB 2.0) costs 1.7 fast, partly through L2 in band (0.77 -> 0.69: a different
   K angle moves the links).
2. A small-horn (high-gain) drive must cross hub K's crown. Its rod and rocker arm sit at least 2 mm above the crown
   top, out of band by construction. The trade between gain and in-band is set by the horn radius, which has to be
   about 16 mm or more for a drive at strap level.
3. Raising stop B toward the K dyad's straight line buys nothing. The stretched losses are bounded first by m3e plus
   lift-off (6 fit poses), then by the dyad's straight-line wall (13 fit poses at th 124-157). Neither moves with a1max.
