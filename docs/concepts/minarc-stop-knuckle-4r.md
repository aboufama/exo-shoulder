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
