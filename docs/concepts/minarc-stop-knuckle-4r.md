# minarc-stop-knuckle-4r - Min-arc stop knuckle 4R

A plain spherical 3R whose link 1 is split by a fourth, passive, sensed O20 hub K. A clock spring holds K on stop A,
and J2 carries two hard stops on its interior angle. Inside the 3R window the chain is a rigid 3R. Past the window,
J2 lands on a stop and the arm opens K to the smallest J1-J2 arc that still closes.

Model: `docs/concepts/models/minarc-stop-knuckle-4r.py` (on tools/concept_kit.py, with the spine-parked crown, near-touch
and overhead extras). Sweep: `docs/concepts/sweeps/minarc-stop-knuckle-4r.json`. Row: `docs/concepts/rows/minarc-stop-knuckle-4r.json`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the knuckle as a **self-motion problem**, not a "relay". With J1 fixed in the scapula and J3 fixed in the
     humerus, the 4R has a 1-DOF self-motion at every arm pose. The spring plus the stops pick one point on it.
   - Check the **conditioning of the moving sub-chain** in the forced states. With J2 locked, the chain is J1-K-J3,
     and its own fold (J1, K, J3 coplanar) is the stop-relay-rocker failure. The model enforces that fold margin
     (>= the kit's FOLD_MARGIN) per pose. The spec only asserted psi 58-120.
   - Check the **spring against gravity** on the self-motion itself, by virtual work: tau = -dU/dpsi over every
     taken pose, for each state.
   - **Price the layer stack at K.** The 12 mm straps leave K at psi ~58 deg, and they still overlap 1-2 mm past the
     kit's 12 mm exempt zone. A bare 0.15 mm running stack collided in 196 of 212 poses. The model therefore carries a
     1.0 mm spacer, which is real metal height.
   - Run the **3R control at the same seats** (stop B = a1, so K never opens), so that the knuckle's gain is measured
     and not assumed. This is the rail-elbow lesson.
2. **Rawest material.**
   - The posed skin: the bench's signed-distance grids. These are the fast cache on Bench(60,160) and the exact libigl
     path on Bench(110,360).
   - The bench motion clips (fit clips only; held-out clips never loaded).
   - The workspace pose grid.
   - The kinematic reference from the round-5 proposer (`k4r_lib.minarc`) and the judge's per-ray re-score (rt_minarc).
     These are only cross-checks. Every number below comes from the kit's fitted members on the posed skin.
3. **Methods and tools.**
   - The kit: K1 closure with per-pose arc, K3 march, K4 flat O20 hubs at the real 12.25 mm stack, K5 straps,
     K6 collisions, K2 dense continuity on all four joint axes, and the K7 neck.
   - The spine-parked crown/wall check, the near-touch rule and the overhead split.
   - A Latin-hypercube coarse sweep on the cloud CPU farm, then CMA-ES streams (tools/concept_cma.py) on the farm
     until the convergence gate passes.
   - The frozen protocol: fit on Bench(60,160) fast, freeze every level, then wear on Bench(110,360) exact.
   - Quasi-static virtual work for the spring. The MuJoCo dynamics judge (judge/dynamics.py) needs the L1 meshes, so it
     is left to the L1 CAD step.
4. **What, other than me, shows the number is right.**
   - The bench report itself (concept_bench gap, honest flag, audit).
   - The 3R control at identical seats and metal.
   - The frozen Bench(110,360) exact wear.
   - The red-team pose list: rest, overhead, across-body, behind-back and the nearest-metal poses, all printed by the
     `redteam` mode.
   - The judge's contact-aware expectation (gap 18-24), which my number either meets or refutes.
   - The independent verifier of the next stage.

## The mechanism

- **Topology.** The chain runs scapula handler -> J1 (O20, active, on a GH ray) -> link 1a (arc b1) -> **K** (O20,
  passive, sensed) -> link 1b (arc b2) -> J2 (O20, active, with interior-angle hard stops) -> link 2 -> J3 -> arm.
  - K is set by a clock spring in its cap (preload 0.08 N.m onto stop A, about 0.03 N.m/rad) and a stop dowel in a
    milled arc slot (stops A and B).
  - J2's stops are a dowel in an arc slot.
  - There are 0 passive translations, and no gear, cable or pulley.
- **The min-arc law (R17: no undetermined coordinate).** With J1 fixed in the scapula and J3 fixed in the humerus, the
  4R has a 1-DOF self-motion, and on it the arc a1e = angle(J1, J2) changes monotonically with K's angle psi. The
  spring pushes psi down until a stop holds it:
  - Inside the window, K rests on stop A (a1e = a1) and the chain is a rigid 3R.
  - Past the window, J2 rests on its phi_hi stop (stretched) or its phi_lo stop (folded), and K sits at the smallest
    a1e >= a1 that closes. This is the root of A cos x + B sin x = cos th that is continuous with a1.
  - A pose is reachable only up to stop B (a1e <= a1max).
- **Two checks the spec did not ask for.** Both are in the model:
  - The forced sub-chain J1-K-J3 (J2 locked) keeps its own fold margin of at least FOLD_MARGIN = 5 deg. This is the
    stop-relay failure, measured and not assumed. On every configuration below the minimum is 6-20 deg.
  - The J2 stops are capped at [5, 175] deg.
  - Two readings of the user's fold-margin ruling are reported:
    - **Stop-guard** (the spec's 15/170). The hard stop keeps J2 off its fold, so the J2 dyad may run closer than
      5 deg of th to its fold.
    - **Margin-equivalent stops** (phi 22/148 at a1 41, a2 68). J2 is never within 5 deg of th of its fold; K opens
      exactly where the 3R's margin would have stopped it.
- **Complexity** (tools/simplicity.py weights):
  - Variant A: 13.5. Items: 1 passive rotation, 1 sensed passive, 1 spring, +1 body, +1 joint, about 3 made and
    4 bought parts over the anchor.
  - Variant B: about 34 (the pin knee's 21.5 + 12.5).

## Variant A - the plain spherical chain on the kit (`models/minarc-stop-knuckle-4r.py`)

All on Bench(60,160) fast with kit checks: march, dense K2 on all 4 axes, K6, crown/wall, O20 hubs and 12 x 3 straps.

| configuration | gap | reach | follow | in-band 14 | contact | note |
|---|---|---|---|---|---|---|
| catalogue seeds (J1 bvec(90.76, 65.50), J3 wdir(74.85, -10.5), 44/74, b 35/55, stop B 78) | 66.93 | 0.894 | 0.95 | 0.29 | 0.057 | hub 2 fitted at **123 mm**: overhead poses need 140-181 mm there |
| same seats, knuckle locked (3R control) | 62.57 | 0.769 | 0.95 | 0.47 | 0.063 | hub 2 is 2 % in band even without the knuckle: the seats set the band |
| catalogue spine-parked seed set | 86.59 | | | | | |
| **coarse LHS best (302 configs on the farm)** | **49.10** | 0.794 | 0.95 | 0.62 | 0.107 | J1 bvec(110.6, 62.4), J3 wdir(62.6, -10.7), 47.7/73.9, b 41.8/48.2, stop B 66.6 |
| same seats, knuckle locked | 52.98 | 0.756 | 0.95 | 0.61 | 0.092 | **the knuckle is worth 3.9 points here** |

Findings:
- In variant A the in-band is the limiter, not the fold. At the coarse best, link 2 is 27 % in band (level up to
  109 mm, riding over link 1a / 1b and the neck), hub 2 is 55 % and hub 3 is 66 %. A plain spherical 3R on the kit with
  O20 hubs lands at ~47-53 whatever the seats: spine-parked O20 is 47.41.
- The knuckle's forced poses mostly turn into contact, not into reach. At the coarse best, 10 forced workspace poses
  are stretched: 6 taken, 4 penetrating. At the seeds there are 20 forced poses: 14 taken, 6 penetrating.
- The 1.0 mm spacer at K is needed. Without it, links 1a and 1b collide in 196 of 212 poses: they part at psi
  58-70 deg and still overlap 1-2 mm past K6's 12 mm exempt zone at the 0.15 mm running stack.
- A kit asymmetry was found on the way. K6's arc distance uses the first member's radius, while `over` uses the raised
  member's radius, so `over` can leave a pair that K6 then flags (13.1 vs 13.3 mm here). This is noted for the kit owner.
- Spring vs gravity (quasi-static virtual work, thorax y up, kit straps, 10 g per O20 hub), at the seeds:
  - On stop A, gravity's opening torque is at most 0.041 N.m against the 0.08 preload.
  - In the stretched states it reaches 0.085 against a spring of 0.094-0.112 (worst margin -0.004 N.m). A
    **0.12 N.m preload** is needed there.

### Variant A CMA-ES (6 streams on the farm, 7886 tries, popsize 8, 12 coordinates)

| stream | start | tries | best gap | reach | follow | in-band 14 | contact |
|---|---|---|---|---|---|---|---|
| A | coarse #1 | 1097 | 24.95 | 0.831 | 1.0 | 0.800 | 0.081 |
| B | coarse #2 | 929 | 26.43 | 0.844 | 1.0 | 0.768 | 0.076 |
| C | coarse #3 | 1265 | 23.64 | 0.825 | 0.95 | 0.817 | 0.078 |
| D | coarse #5 | 1505 | 24.76 | 0.844 | 1.0 | 0.789 | 0.080 |
| **E** | coarse #6 | 1601 | **22.17** | 0.856 | 1.0 | 0.780 | 0.057 |
| F | coarse #1, sigma 0.5 | 1489 | 22.57 | 0.850 | 0.95 | 0.783 | 0.059 |

- **Convergence gate**, over the whole history in generation order: the best gained 0.49 score points over the second
  half and 0.31 over the last third, and the top 5 lie within 0.02. **Converged.**
- **The best (E).**
  - Configuration: J1 bvec(102.59, 65.67), J3 wdir(48.38, -6.80), a1 42.99, a2 70.31, b1 29.65, b2 49.38,
    stop B a1max 65.91, phi stops 29.06 / 166.89, q 0.951.
  - Score: 22.17 (score 91.9).
  - Per part in band: hub 1 0.99, hub K 1.00, hub 2 0.93 (F 62 mm), link 1a 1.00, link 1b 0.97, link 2 0.43,
    hub 3 0.70 (F 101 mm), neck 0.68.
  - Forced poses: 39 (19 %), all stretched. Of the 36 forced workspace poses, 32 are taken and 4 are contact.
  - The sub-chain fold margin is at least 13.7 deg; psi runs 64-112 deg.
- **Its 3R control at the same seats and metal** (stop B = a1) scores **45.91** (reach 0.61). At these seats the
  knuckle is worth **23.7 points**. The CMA left the 3R-viable seats (coarse: knuckle worth 3.9) for seats where the
  knuckle carries a fifth of the poses.
- **Near-touch (lesson d).** Lowest metal is 0.07 mm. Counting metal < 1 mm as contact, the gap is 41.79 (15 poses).
  q 0.95 lets the fitted undersides graze the skin. A near-touch CMA (objective = gap_near1, streams AN1 / AN2) is
  running.
- **Overhead (elevation >= 140):** reach 3 of 12, follow 5 of 5, in-band 0.81.
- **Named poses:** rest 5/5 (in-band 0.78); overhead 8/17; across-body 28/36; behind-back 16/19.
- **Spring vs gravity** at E: on stop A, at most 0.016 N.m; in the stretched states at most 0.018 N.m against a
  spring of 0.087-0.105. The 0.08 N.m preload holds with a 0.064 N.m margin.

## Variant B - the pin knee + the knuckle (`models/minarc-stop-knuckle-4r-pinknee.py`)

The spec ran this variant only if variant A's in-band fell below 0.88; it fell to 0.62.

- **How the model is built.** It subclasses the verified pin-knee model (the seed VModel rules: closure < 0.5 deg,
  10 fps continuity now including K, the jam rule, part-part clearance of 1 mm non-adjacent / 0.15 mm adjacent, walls,
  crowns and tops skin-checked).
- **What it adds.**
  - Hub K on link 1a. Hub 2 moves onto link 1b (a new member 7).
  - Straps L1a, L1b and L2, with every new part pair checked: hub K and L1a / L1b against all hubs, straps, the knee
    link, the pad and the E strap; L1a-L1b adjacent at K; L1b-L2 adjacent at J2.
- **The kinematics** are exact:
  - K's rotation carries link 1b, J2, link 2 and J3's offset line.
  - The spherical 3R (u1, RK u2, RK u3) is then solved in closed form.
  - The pin knee absorbs the drift as before.
  - The residual is 0.016 deg.

### Variant B measured (Bench(60,160) fast, VModel rules, the pin knee's current best seats)

| configuration | gap | reach | follow | in-band 14 | contact | note |
|---|---|---|---|---|---|---|
| the pin-knee model itself at these seats (margin 5) | 23.64 | 0.700 | 0.95 | 0.898 | 0.034 | reference |
| knuckle locked (stop B = a1) | 22.57 | 0.756 | 0.917 | 0.913 | 0.049 | stops [15, 170] as the J2 guard |
| bk 30/50, phi 15/170, a1max 70 | 19.12 | 0.813 | 0.917 | 0.913 | 0.070 | |
| bk 30/50, phi 15/170, a1max 75 | 18.46 | 0.819 | 0.917 | 0.912 | 0.070 | near1 24.08, min metal 0.12 mm |
| bk 30/50, margin-equivalent stops 22/148, a1max 70 | 20.31 | 0.788 | 0.917 | 0.913 | 0.057 | J2 never within 5 deg of its fold |
| **bk 36/44, stops 22/148, a1max 75** | **17.58** | 0.781 | 0.95 | 0.908 | 0.057 | near1 22.15; sub-chain margin >= 17 deg |
| bk 25/55, stops 22/148 | 25.43 | | | | | short link 1a |
| sK +1 | 73.11 | | | | | wrong knuckle branch |

Variant B at 17.58 (bk 36/44, margin-equivalent stops):
- **Per part in band:** hub 1 1.0, hub K 0.97, hub 2 1.0, hub 3 0.67, E 0.92, knee 0.93, L1a 0.97, L1b 0.97,
  L2 0.82.
- **Forced poses:** 13, all stretched. 9 are taken and 4 are skin contact.
- **Lost poses:**
  - 20 fold. The folded side has no closing chain with margin: th 16-32, where J1 and J3 nearly align and the J1-K-J3
    sub-chain folds too. The stretched side needs a1e 76-100 > stop B, at th 132-152.
  - 7 lost to the knee window.
  - 11 lost to skin.
- **Overhead:** reach 2 of 12, follow 2 of 5.
- **Spring vs gravity:** at most 0.007 N.m (8 mm straps, members 1a / 1b / 2 / 3 weigh 11 / 8 / 7 / 11 g). The
  0.08 N.m preload holds with a 0.073 margin.

### Variant B CMA-ES (4 streams on the farm, 6234 tries, popsize 10, 18 coordinates: the pin knee's 13 + the knuckle's 5)

| stream | setting | tries | best fast gap |
|---|---|---|---|
| BA | sK -1, stop-guard reading | 1181 | 7.27 |
| BB | sK -1, **mstop 1** (the J2 dyad keeps a 5 deg th-margin in state A) | 1421 | 9.43 |
| BC | sK +1 | 1781 | 28.73 (wrong knuckle branch, stalled) |
| **BD** | sK -1, sigma 0.5 | 1851 | **6.19** (score 97.7) |

- **Convergence gate:** gain 0.23 score points over the second half and 0.23 over the last third; top-5 spread 0.03.
  **Converged.**
- **BD best:**
  - J1 bvec(95.47, 67.70), J2 seat bvec(47.21, 39.89), J3 wd 59.82 / wa -9.03, b3 0.458.
  - Knee: lE 64.7, lc 30.4, phiE -1.5, phib -69.8, ang_min 25.0, stack 5.27.
  - Knuckle: bk1 30.16, bk2 47.01, a1max 66.16, J2 stops 12.3 / 162.7.
  - At this setting, 28 forced poses close and 27 of them are taken.

### THE CLAIM: frozen shape worn on Bench(110,360) EXACT

Protocol (lesson c): fit on Bench(60,160) fast, freeze every level and the knee centre, wear on Bench(110,360) with
CB_EXACT=1, using the pin knee's own frozen protocol. Farm jobs `.cache/minarc/frozen_*.json`.

| configuration | fast | **frozen exact** | score | reach | follow | in-band 14 | contact | metal < 1 mm = contact | min metal | overhead reach |
|---|---|---|---|---|---|---|---|---|---|---|
| FZ0: knuckle locked, pin knee's seats (the control) | 22.57 | 26.82 | 90.2 | 0.703 | 0.927 | 0.911 | 0.048 | 30.09 | 0.08 | 0.18 |
| FZ1: bk 30/50, margin-equivalent stops, a1max 75 | 21.28 | 25.68 | 90.7 | 0.739 | 0.927 | 0.911 | 0.073 | 29.40 | 0.13 | 0.18 |
| FZ2: bk 30/50, stops 15/170, a1max 75 | 18.46 | 24.00 | 91.3 | 0.761 | 0.927 | 0.910 | 0.078 | 28.71 | 0.11 | 0.18 |
| BB best (mstop 1: conservative fold-margin reading) | 9.43 | 21.40 | 92.2 | 0.753 | 0.936 | 0.905 | 0.053 | 24.05 | 0.10 | 0.25 |
| BA best | 7.27 | 17.98 | 93.5 | 0.756 | 1.000 | 0.901 | 0.035 | **21.37** | 0.76 | 0.29 |
| **BD best** | 6.19 | **15.42** | **94.4** | 0.769 | 1.000 | 0.899 | 0.023 | 22.17 | 0.05 | 0.29 |

For reference, the pin knee verified at 30.35. Its polish H1 verified at 26.45 (margin 10) / 24.48 (margin 5).

Reading:
- **The knuckle earns its place.**
  - At the pin knee's seats it is worth 2.8 frozen points: 26.82 locked against 24.00.
  - With seats re-tuned for it, the CMA bests wear at 15.4-18.0 frozen exact. That is 9-15 points better than every
    verified leader, at 0 passive translations.
  - The fast-to-frozen loss (6.2 -> 15.4) is the usual sample effect (lesson c): 56 fold-lost poses on 470, against
    15 on 220.
- **The conservative margin reading** (J2 never within 5 deg of its fold) costs 3.4-6 points (BB 21.40) and still beats
  every verified leader.
- **Near-touch.**
  - BD's lowest metal is 0.05 mm, on the overhead raise clip (plane 30, elevation 150). With metal < 1 mm counted as
    contact, the gap is 22.17.
  - BA keeps 0.76 mm and scores 21.37 under the same rule. BA is the more robust shape and the one to hand to the
    verifier alongside BD.
- **Still lost on the big bench (BD):**
  - 56 poses to the fold: the stretched side past stop B and the folded side with J1 close to J3.
  - 16 to the knee window.
  - 9 to contact.
  - Overhead reach is 8 of 28.

## Red team

1. **Forced sub-chain speed.** On the gallery loop, J1 swings 20-40 deg per frame on the last in-range frames before
   stop B (overhead), where the forced sub-chain J1-K-J3 nears its fold (minimum margin 7.3 deg at BD). The bench's
   10 fps clip continuity (25 deg) does not flag it.
   - Unpowered, this is where the wearer would feel the chain stiffen.
   - Next check: MuJoCo (judge/dynamics.py, after the L1 CAD) on the overhead clips, and a sub-chain margin of 10 deg
     as a CMA constraint.
2. **Preload.** Quasi-static virtual work (thorax y up, member masses from the fitted samples, 10 g per O20 hub)
   gives at most 0.007-0.008 N.m gravity torque opening K in any state. The 0.08 N.m preload holds with a margin of
   0.073 N.m (variant A: 0.064).
   - Arm-acceleration loads on a ~40 g chain are ~0.002 N.m.
   - Not yet run in MuJoCo, because the dynamics judge needs the L1 meshes.
3. **The pinch point.** Metal sits 0.05 mm from the skin on the overhead raise clip at BD. Use BA (0.76 mm), or a
   near-touch objective, for the build.
4. **The optimistic number.** The fast 6.19 is optimistic by 9.2 points (sample). The claim is the frozen 15.42
   (self-measured, not yet verified). The conservative-margin 21.40 is the floor if the J2 hard stop is not accepted
   as the fold guard.
5. **The stop-guard question for the judge.** With the phi stops at 12.3 / 162.7, the J2 dyad runs up to about 1 deg
   of th from its fold before the stop engages. The stop makes the fold unreachable, so no branch flip is possible,
   but the 3R near the stop has a poor transmission angle. The conservative reading (BB) prices this at 6 points.

## Verdict

**Screened, and the strongest self-measured result so far.** Variant B (the pin knee with a spring-held passive
knuckle in link 1 and J2 hard stops) wears its frozen shape at **15.42 on Bench(110,360) exact** (score 94.4). This
is self-measured and needs an independent verifier: VModel rules, 3 active DOF, 0 passive translations, 3 sensed
passive rotations, complexity 33.
- The conservative fold-margin reading gives 21.40 (score 92.2). The near-touch rule gives 21.37 at BA.
- The judge's prediction for the plain chain (18-24) was optimistic. Variant A on the kit converges at 22.17 fast
  (frozen pending: `.cache/minarc/frozen_FA.json`).
- The judge's expectation that the knuckle trades contact for reach holds only once the seats are re-tuned for it.

**Next:** an independent verifier on BD and BA (docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py frozen), then a
near-touch polish (objective gap_near1, sub-chain margin >= 10). After that, the L1 CAD and the MuJoCo spring check.

## Verification

Independent skeptic verifier, 2026-10-16. This lens covers the DOF count, the fold-margin metric and the champion on
the same bench. Two other verifiers also checked this claim: `verify/minarc-stop-knuckle-4r-remeasure.md` and
`verify/minarc-stop-knuckle-4r-mechanism.md`. Harness: `verify/minarc-stop-knuckle-4r-skeptic.py`, which imports the
model unchanged. Raw outputs: `verify/minarc-skeptic/`. All runs are local, one process each, and use the frozen
protocol: fit on Bench(60,160) fast, then wear on Bench(110,360) EXACT. O20 hubs, fold margin 5.

**Independent audit.** For every taken pose the harness recomputes the following from the bench's arm rotation Q
alone, not from the model's law:
- th = angle(J1, Q u3);
- the J1-J3 dyad margin;
- the rotation of member 3 from (q1, dK, q2, q3), checked against Q;
- that K stays one-sided;
- the margin of the forced J1-K-J3 sub-chain.

| reading (BD seats) | gap | score | reach | follow | ib14 | ib10 | contact | near-touch gap | min J1-J3 margin, K on stop A | state-A poses < 5 deg |
|---|---|---|---|---|---|---|---|---|---|---|
| claim: J2 stops phi 12.28 / 162.70 | 15.42 | 94.4 | 0.769 | 1.0 | 0.899 | 0.581 | 0.023 | 22.17 | **1.97 deg** | **25 (3 clip frames)** |
| **corrected: J2 stops at the 5-deg J1-J3 margin (phi 20.79 / 146.61)** | **18.45** | **93.3** | 0.747 | 1.0 | 0.889 | 0.583 | 0.021 | 24.26 | 5.12 deg | 0 |
| champion (seed VModel, slides 0), same bench and checks | 64.93 | 76.4 | 0.728 | 0.918 | 0.565 | 0.350 | 0.110 | - | - | - |

What holds in both readings:
- Closure is within 0.015 deg on every taken pose.
- dK is one-sided (0 to -58.7 deg) and stays inside stop B.
- The forced sub-chain keeps at least 7.4 deg of margin in the claim and 16.9 deg in the corrected reading.
- Overhead workspace reach is 8 of 28 poses.
- Minimum metal is 0.05 mm, on the overhead raise clip at plane 30 / elevation 150.
- In the corrected reading, 67 taken poses are forced, and 3 of them are clip frames.
- The champion scored 66.97 at margin 10 (`.cache/osn_verify/L_champbig_frozen.json`). At margin 5 it scores 64.93.

**Refuted as claimed, on two counts.**
1. **The fold margin.** The claimed 15.42 puts the J2 hard stops on the interior angle phi, 5 deg inside [0, 180].
   In the J1-J3 metric, which the kit's rule and every verified row use, those stops sit 1.37 / 1.88 deg from the
   fold. On the worn bench, 25 taken poses with K on stop A run inside the user's 5-deg margin; 3 of them are clip
   frames. That buys reach by shrinking the singularity margin, which needs the user's say. Moving the stops to the
   5-deg margin costs 3.03 points: **18.45**. This reproduces the mechanism verifier's `stops5` run to the digit.
2. **The active-DOF count.** The row records 3 active DOF with K as a "sensed passive". The user's counting rule
   (REQUIREMENTS.md, 2026-10-15) makes a joint ACTIVE when it must be position-measured for the device to work.
   - In every forced state J2 rests on its stop, so q2 is constant and q1 / q3 alone cannot give the arm's three
     rotations. K's angle has to be read.
   - In the corrected reading this also happens on 3 clip frames, not only on static workspace poses.
   - The MVP2 J2 motor cannot drive these states either: it would push against a stop while K is unpowered.
   - So this is a **4-active-DOF** chain. It meets the R5 cap of 4 but fails R5-aim and the brief's "exactly 3 ACTIVE
     DOF". This is the same ruling as for `short-a2-arc-slide-3r`'s sensed slide.

**What stands.** As a 4-active-DOF design with 0 passive translations, the honest figure is **v_gap 18.45** (score 93.3)
on Bench(110,360) exact, against the champion's 64.93 under the same bench and checks. It beats every verified 3-active
leader: H1 scores 24.48 at margin 5 (polish protocol) and 27.20 on this protocol.
- Continuity on the full envelope grid holds for this configuration: 64 of 64 forced poses are connected (mechanism
  verifier).
- The buildable form scores 17.32. It adds a physical q2 stop dowel and a 0.3 x 5 mm clock spring in a 6 mm taller K
  cap (mechanism verifier).

**Comparisons and next steps.**
- Compare this design with the four-dof lens (park4 at 22.36, self-measured), not with the 3R family.
- Open items:
  - a CMA run that holds the stops at the 5-deg margin, optimised on the near-touch gap;
  - the 0.05 mm overhead pinch;
  - in-band10 0.58 against the R1-aim of 0.90;
  - overhead reach of 8 of 28;
  - asking the user whether a sensed 4th joint is acceptable for the golden target.

## Kit-rule re-optimisation (Track A, 2026-10-16): physical J2 stop, every state >= 5 deg, real spring cap, near-touch search

Why: the claim (15.42) reproduces only in the model's own fold reading; its J2 stops sit 1.37 / 1.88 deg from the J1-J3
fold (`verify/minarc-stop-knuckle-4r-remeasure.md`), and its J2 "stop" acts on a virtual angle no dowel can stop
(`verify/minarc-stop-knuckle-4r-mechanism.md`). This section re-optimises the family under the rules as they stand.

**Model** (`models/minarc-stop-knuckle-4r-kitrule.py`, variant B; the claim's model is imported unchanged, every change is
an opt-in parameter):
* `kitrule` 1: the J2 stops are placed in the KIT's J1-J3 metric. `smhi` / `smlo` = the J1-J3 fold margin (deg) at which
  J2 meets its stretched / folded stop with K on stop A; both are design variables >= 5 (the user's ruling) and the
  search moves them. K therefore opens *before* the dyad can enter the forbidden band: no island can form.
* `phys` 1: the BUILDABLE stop - a dowel in an arc slot at J2 stops J2's own angle q2 (link 1b vs link 2). The q2 window
  is the state-A q2 at the two stop margins (closed form, cos th = A + R cos(q2 - q0)). Past it J2 is locked on the stop
  and K opens to the smallest rotation (spring direction, <= stop B) that closes J1 -> K -> (link 1b + link 2) -> J3:
  u1 . R(uK, dK) p = cos th with p = R(u2, q2_stop) u3 (Paden-Kahan; no scan, closure residual <= 0.02 deg).
* Fold margin in every state: state A the dyad (a1, a2); forced states the moving sub-chain J1-K-J3 (b1, arc(K, J3)) AND
  (`m3e` 1, the conservative reading) the effective dyad (a1e, a2), all >= 5 deg.
* `capK` 6: hub K's clock-spring cap 6 mm taller than the O20 12.25 stack (the real 0.3 x 5 mm 1.4310 strip): cylinder,
  crown samples and skin-contact rings run F .. F + 18.25, in the fit and in every worn copy.
* `near` 1: the CMA objective is the near-touch gap (metal < 1 mm = contact).

Variant A (`models/minarc-stop-knuckle-4r-a-kitrule.py`, the plain spherical chain + K, complexity 13.5): the same rules
(stops in the kit metric, physical q2 stop solved by a 0.25-deg scan + bisection on a1e, effective dyad and sub-chain
>= 5, hub K member 18.25 mm tall incl. its crown-skin samples, near-touch objective); its `frozen` mode carries the
continuity flood fill.

**Claim harness** (`models/minarc-stop-knuckle-4r-kitrule-wear.py`): the independent re-measure verifier
(`verify/minarc-stop-knuckle-4r-remeasure.py`) imported UNCHANGED with its model handle swapped: the same fit60 frozen
hand-over, the same extra checks (closure per axis, K one-sided within stop B, boss / knee clearances), the same held-out
bench (so H1 31.39 is comparable) and the same full-grid continuity flood fill (1432 workspace poses, 2-deg slerp edges,
no joint incl. dK > 10 deg per step, knee branch constant, seeds at elevation 0 with K on stop A). Under the physical
stop the verifier's phi check is relaxed to [5, 175] and replaced by J2's own q2 (from the member frames) inside the
slot; the kit margin of the effective dyad is re-checked on every taken pose (a failing pose is knocked out).

**Search** (Bench(60,160) fast, near-touch objective, popsize 8): local stream LB1 (variant B, from BD's seats with both
stops at the 5-deg margin = the judge's floor point, sigma 0.3; 417 evaluations, 52 generations) and LA1 (variant A,
from its screened best with the stops moved into the kit metric; 337 evaluations). Convergence gate (docs/METHOD.md):
LB1 gains 0.24 score points over the second half and 0.23 over the last third, top-5 spread 0.23 -> passes; LA1 0.97 /
0.40 / 0.66 -> passes. Both are single streams. Ten farm streams (PB1-6 variant B and PA1-3 variant A under the same
rules, K* / AK* under the virtual stop in the kit metric) were queued at 09:45-10:05 UTC and had not started by 10:55 (farm
queue 9 deep on 4 workers); they are not part of this claim.

**Result** (frozen: fit Bench(60,160) fast -> wear Bench(110,360) EXACT, fold margin 5 in every state, O20 x 4 with hub K's
cap +6 mm, continuity on the full 1432-pose grid; raw data `verify/minarc-kitrule/`):

| configuration (variant B unless stated) | fast fit | gap (connected) | score | reach | follow | in-band14 | contact | near-touch gap | min metal | held out (near-touch) |
|---|---|---|---|---|---|---|---|---|---|---|
| claim BD, virtual phi stops 1.37 / 1.88 deg from the fold (refuted) | 6.19 | 15.42 | 94.4 | 0.769 | 1.0 | 0.899 | 0.023 | 22.17 | 0.05 | 18.22 |
| judge's floor: BD, virtual stops at the 5-deg margin (not buildable) | 10.83 | 18.45 | 93.3 | 0.747 | 1.0 | 0.889 | 0.021 | 24.26 | 0.05 | 22.27 |
| **BDp = the claim**: BD seats, stops 5 / 5, **physical q2 stop + cap 6** (`params_floorBD5_phys_cap6.json`) | 12.25 | **19.06** | **93.07** | 0.725 | 1.0 | 0.895 | 0.011 | 26.15 | 0.05 | **23.24 (28.31)** |
| same, effective-dyad check off (`m3e` 0; forced poses down to 2.97 deg) | 10.17 | 20.91 | 92.40 | 0.725 | 1.0 | 0.895 | 0.029 | 27.34 | 0.05 | - |
| BB seats, virtual stops 5 / 5, no cap | 10.08 | 21.16 | 92.31 | 0.753 | 0.936 | 0.904 | 0.051 | 23.82 | 0.09 | - |
| LB1 best (near-touch CMA from BDp): physical q2 stop, cap 6, stops 5.00 / 7.27 (`params_B_LB1_g45_2.json`) | 11.22 | 19.63 | 92.86 | 0.761 | 0.945 | 0.900 | 0.053 | **22.88** | 0.02 | 24.59 (28.22) |
| variant A, LA1 best (`params_A_LA1_g40_2.json`, complexity 13.5) | 30.03 near / 28.92 | 41.14 | 85.04 | 0.778 | 1.0 | 0.706 | 0.095 | 44.72 | 0.26 | 45.72 (48.55), static = connected from any elevation-0 seed |
| H1 (verified pin knee), same harness | 27.20 fit60 | 27.20 | 90.11 | | | | | 31.75 | | 31.39 (34.66) |

**The claim: BDp** (variant B, `models/minarc-stop-knuckle-4r-kitrule.py` with `kitrule 1, phys 1, capK 6, m3e 1`, params
`verify/minarc-kitrule/params_floorBD5_phys_cap6.json` = the claim's BD seats with both J2 stops at the 5-deg kit margin).
It wins the official (plain) gap in-sample AND held out; the near-touch CMA's best (LB1) wins near-touch in-sample only
and ties it held out (28.22 vs 28.31) - its in-sample gain does not generalise (the polish lesson again).
* **Frozen exact Bench(110,360), continuity applied: 19.06 (score 93.07)**; reach 0.725, follow 1.0, in-band14 0.895,
  in-band10 0.597, contact 0.011; near-touch 26.15 (15 poses under 1 mm, min 0.05 mm on the overhead raise clip, as in
  the claim). Continuity: 1041 of 1041 grid nodes connected from the strict rest region (820 K on stop A, 221
  stretched), 0 islands, 1785 of 1785 edges pass; 0 of 261 taken bench workspace poses dropped.
* **Held out (the re-measure harness, 1154 disjoint poses): 23.24 (score 91.55)**, near-touch 28.31, 0 of 656 taken
  workspace poses unconnected; H1 under the same harness 31.39 (near-touch 34.66).
* **Fold margin**: every taken pose keeps >= 5.01 deg of J1-J3 margin in its own state (state A 5.12, stretched 5.01;
  held out 5.01); the moving sub-chain J1-K-J3 >= 16.9 deg (held out 17.0). J2's own slot q2 -24.98 .. 100.84 deg
  (125.8 deg of arc); K opens up to 33.95 deg of its 62.83 (stop B never reached on the bench). Verifier checks (closure
  per axis <= 0.022 deg, K one-sided within stop B, q2 inside the slot, boss / knee clearances) remove 0 poses.
* Arcs a1 38.07 / a2 58.75, knuckle bk1 30.16 / bk2 47.01, a1max 66.16; hubs O20 x 4, hub K 18.25 mm tall; f = 49.4 /
  62.1 / 81.6 mm, stack 88.3 mm. Lost poses (470): fold 85, knee window 10, contact 4. Overhead >= 140: workspace reach
  8 / 28, follow 10 / 10.
* Complexity 33 (`tools/simplicity.py` count of variant B; the dowel and the taller cap add no counted part). 4 revolutes,
  K sensed: the skeptic lens counts this as 4 ACTIVE DOF (K must be read in the forced states) - that ruling stands.

LB1 (the near-touch CMA best, for the record): 19.63 frozen exact (near-touch 22.88; 5 poses under 1 mm, min 0.02 mm on
overhead clips, so follow 0.945), held out 24.59; every taken pose >= 5.07 deg (sub-chain >= 5.06); the search moved
the stretched stop to 7.27 deg and used K's whole range (77.05 of 77.09 deg); 1154 of 1154 nodes connected.

What it means:
* Under every rule as it stands (5 deg in every state, a stop a dowel can make, a spring that exists, continuity), the
  knuckle beats H1 by 8.1 points in-sample (19.06 vs 27.20) and 8.2 held out (23.24 vs 31.39); it does not reach 95
  (13.75): 5.3 points short.
* Pricing the buildable stop and the spring cap costs 0.6 points over the judge's virtual floor at the same seats
  (18.45 -> 19.06; held out 22.27 -> 23.24). With the stops placed in the kit metric no forbidden band separates the
  states, so no island forms (the claim's stops kept under the kit rule gave 35.56 connected).
* The near-touch search buys 3.3 near-touch points in-sample (26.15 -> 22.88) for 0.6 plain points and none held out
  (28.31 -> 28.22, plain 23.24 -> 24.59): the Bench(60,160) objective does not see Bench(110,360)'s overhead clip
  frames, where LB1 moves metal to 0.02 mm. The next search wants a held-out-aware (cross-fit) objective.
* The effective-dyad check (`m3e`) is not what limits it: switching it off lets forced poses reach 2.97 deg of margin and
  the frozen gap gets WORSE (20.91), because the refit shape changes.
* Variant A (complexity 13.5) under the same rules stays at 41.14 frozen exact (in-band 0.71): not a contender at this
  budget. Its rest pose (elevation 0) is always in the stretched state (K open), so the strict seed rule (rest = K on
  stop A) seeds nothing; seeded at every elevation-0 pose, 1263 of 1263 nodes connect (static = connected).

## Full user-style CAD of BDp (generation 4, `user_minarc_bdp`, 2026-10-16)

Built by `pipeline/conformal/param_cad/user_style_minarc.py` (param dict in: the verified params + the judge's K stop-B fix
a1max 54.748) on the L1's frames and clips (`l1_minarc-bdp`; the fit is the kit-rule model's own frozen fit60 shape,
asserted equal: tr 88.30, knee centre m (-19.83, 3.63)). 86 parts; every custom part one valid closed solid (R7: 41 of 41
STEP parts); 176 g of custom parts + 63 g for BOTTOM fused with the pad mount.

What the CAD is (no lofts, no splines: line / tangent-arc sketches, extrudes, revolves, one constant-section sweep):
* **Hubs** J1 / K / J2 / J3: the v5 O20 stack only (MR117-2RS pair, 17-4PH outer spacer, ground inner spacer, M7x0.5 Ti
  ring nut). The gen-3 caps' spline dome is replaced by a torispherical dome of two tangent arcs (R63.6 crown, R1 knuckle).
* **Hub K** (passive, spring-held, sensed): cap 6 mm taller (crown F + 18.25 = the verified capK 6), threaded on link 1b's
  M18 x 0.5 spigot; inside, an O16 x 5.2 chamber round an O5 arbor (link 1a's integral O7 pin continued above the ring
  nut, 0.4 mm slit for the inner end); the clock spring as built: 0.3 x 5 mm 1.4310 +C1900 strip, 145.6 mm, nine tangent
  half-turns R2.75 + 0.6 mm per half-turn (a two-centre spiral, one constant-section sweep), R0.5 hook into a 0.8 mm slot
  in the chamber wall; O3 x 1.4 diametric magnet in the arbor tip, O11 x 1.1 sensor pocket in the crown (0.6 mm Ti wall,
  magnet to sensor ~1.5 mm) + a 1.6 x 0.8 flex groove for the user's angle sensor (the 4th encoder).
* **Stops** (the verified claim's buildable stop): ISO 8734 O3 m6 hardened dowels pressed 3 mm into the upper boss at
  r 7.75, running in 3.1 mm arc slots through the lower pad; slot ends are semicircles placed so the dowel touches 0.02 mm
  past the stop angle. **J2**: one dowel, q2 -24.98 .. 100.84 deg (the 5.0-deg drawn margin). **K**: an OPPOSED PAIR
  (homes 144 / 324 deg, stop A dK 0, stop B dK -34.47): two dowels 180 deg apart make the stop a couple, so K's bearings
  carry no radial stop load (the L1 red team: one dowel = 770 N radial at the 6 N.m jam push, s0 0.73 on the MR117
  pair). O3, not the spec's O2: the O2 fails bending at that push (SF 1.09, `l1_minarc-bdp/build.json` dowel_check).
  J2 keeps the single dowel (a 126-deg slot leaves no room for an opposed pair): its bearing pair still sees the stop
  force as a radial load at a jam push - open item.
* **Links 1a / 1b / 2**: NEW - each is ONE side-view sketch in the bar plane (the plane of its two hub axes; link 2 the
  plane of J2's axis and hub 3's centre, as gen 3), extruded 8 mm: the underside polyline runs THROUGH the model's strap
  stations (the L1 strap underside, max over the strap's columns, 0.1 mm above outside the hub footprints), the top is the
  underside offset 3 mm along its normals (miter), the vertices rounded with tangent arcs (R2 where the round moves metal
  away from the skin, R0.5 where it adds metal: <= 0.08 mm dip at a 60-deg turn, inside the 0.1 mm margin). A 2.5-D part:
  3+2-axis or wire-EDM from a Ti-6Al-4V plate, pads milled on. Ramps <= 60 deg (the ruling): where the model's strap
  steps steeper (link 2's 68-deg drop after J2's lifted footprint) the lower station is raised until the ramp is 59.5 deg.
  Why not the gen-3 hugging chains: link 1a is too short for one (J1 and K pads 11 mm each, 6.8 mm of rise over ~7 mm of
  free span: no chain of R >= 3 arcs at <= 60 deg exists, `hug_chain` infeasible at 2-5 segments), and on h1b the chains
  left 2.6 / 5.6 mm over the strap at the ramp feet.
* member 3 + E strap + E boss, the knee link, pins a / b (iglidur sleeves + thrust washers, DIN 6799-3.2 clips on the
  1.0 mm land), the arm pad + pad mount + cut BOTTOM as one 7075 part, the upper-arm cuff: `user_style_pinknee.py`
  unchanged. Base at the J1 hub ring (no tab): no ear heading clears link 1a's sweep (0-1 of 180 at every level), so the
  base is the J1 upper member alone and the scapula handler's bracket threads onto the M18 x 0.5 spigot.

Kinematics = the model's (`build.json` check, 9 fit-bench poses incl. the overhead raise peak (30, 150, -60) and the forced
K-open pose (105, 120, -90; dK -34.16, q2 on its -24.98 stop)): the model's hub discs, E boss and arm pad vs the posed
exo.glb (the judges' path) <= 0.144 mm; every exported vertex posed by the model's member transforms vs by frame_xforms
<= 1.2e-4 mm; both dowels inside their slots at every pose. Shape changes (reported, not kinematics): E strap 0.54 mm,
knee plate corners 1.40 mm (gen-3 parts). Links vs the model strap: in the bar plane the underside is 0.01 / 0.04 /
0.12 mm (mean) and <= 0.16 / 0.13 / 1.39 mm (max, outside the footprints) over the strap (1a / 1b / 2); in 3-D (every
strap sample, all columns) one bar edge sits 0.05-0.13 mm on the strap and the other 1.7-1.9 mm above it - the strap is
tilted across its width, the extruded bar is not (a twist would be needed; no twisted sweeps). No model strap sample is
inside a bar.

JUDGE_SECTION
