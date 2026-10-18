# cap-nullspace-4r - cap-pole redundant 4R, null-space set by two torsion springs

Round 103 (J3, track jump), lens 2 (the low-complexity cell of the 4-DOF class). Model:
`docs/concepts/models/cap-nullspace-4r.py` (kit, `tools/concept_kit.py`; flood on `tools/spare_flood.py`'s 1432-node
envelope grid). Sweep: `docs/concepts/sweeps/cap-nullspace-4r.json`. Row: `docs/concepts/rows/cap-nullspace-4r.json`.
**4 joints counted (4-DOF, the user prefers 3), 0 passive translations.**

## Verdict: DEAD - closes the spring-set cap-pole null-space class (4-DOF; the user prefers 3)

**Claim cell (springs on J0 + J2 + J3, spring law exact at deflection <= 170 deg): 57.70 frozen exact Bench(110,360)**
(score 79.0; reach 0.744, follow 1.0, ib14 0.548, ib10 0.359, contact 0.069, overhead 11/28, near-touch 64.51, 1 flood
island dropped, min th margin 5.04, min J0-J1-J2 margin 5.00), 46.32 fast Bench(60,160). The plain cap 3R it replaces,
searched to the gate on the same kit: 60.61 frozen exact (54.15 fast). The redundancy buys 2.9 frozen points for a 4th
counted joint (+25 complexity) and three springs that must wind ~+-170 deg; the lead is 18.28. Gate on the claim-law
sweep: 0.27 / 0.11 / 0.12 score points (262 configs, seeded from 768 earlier ones; 1267 configs in all incl. the control).
Limiter: hub 2, fitted ~117-121 mm from GH, 0.00 in band in every searched cell.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat c-J1-J2-u3 as what it is - a
   spherical four-bar with a ground link that changes every pose - and fix its ASSEMBLY MODE: the two fold stops
   (J0-J1-J2 and J1-J2-J3) each pin one branch sign, so a real build can never jump between the two J2 branches. The
   proposer's psi grid let the pose-local state take either branch (6 of 201 taken poses on the "wrong" one, and those
   branch-mixed poses also shaped the fitted levels). Second: a spring-set null-space is a potential-energy problem,
   so the state is a path-tracked LOCAL minimum, not the global one - the claim must be the flood's, and the like-for-
   like control (the same cap 3R with J0 locked) must get the same search the 4R gets.
2. **The rawest material.** The posed skin itself (the signed-distance grid cache under `concept_bench`, exact path for
   the claim), the envelope grid of 1432 ws poses (`concept_bench._poses_all()`, the flood's transit nodes) and the
   training clips; the skin-motion map `pipeline/conformal/analysis/skin_motion_map_14.json` and the proximity atlas
   (`docs/research/proximity_atlas.md`) say hub 2 at the cap pole sits over the deltoid crest, the highest skin it
   passes over - the measured binder of every cap-pole cell (hub 2 in band <= 0.07).
3. **Methods and tools.** Kit model with every member at its real size (four O20 v5 hubs, 12 x 3 Ti straps, K7 neck),
   K3 march, dense K2 along the interpolated clips, K6 collisions; a full-grid continuity flood with path-tracked
   spring descent (2-deg HG slerps, a stop push <= 10 deg, no basin snap, symmetric neighbour edges); random search +
   coordinate refinement on Bench(60,160) fast, local niced (farm closed); the claim frozen on Bench(110,360) exact.
4. **What else shows the number is right.** The bench (`tools/concept_bench.py`) and its exact path, the like-for-like
   control on the same code and checks, the flood's dropped-island count, the red-team pose list below, and the round's
   adversarial verifier.

## The model (what was built, and where the spec was wrong)

`docs/concepts/models/cap-nullspace-4r.py` (kit; four O20 v5 hubs incl. hub 0 on the back seat, links 0-2 as 12 x 3 Ti
straps with link 1 over link 0 + hub 0 and link 2 over link 1 + neck + link 0 + hub 0, K7 neck; K3 march, dense K2, K6,
the kit audit clean on every claimed row). Per pose the null-space c-J1-J2-J3 is a spherical four-bar; the state is J0's
own angle q0 on a 1-deg grid. Three corrections to the proposer's scratch model (`ns4r.py`):

1. **Assembly mode fixed.** The psi-grid model chose J1 on branch sB but let J2 take either branch about the J1-J3
   plane; the q2 fold stop makes that branch a property of the metal. Measured: the proposer's sprung cell scored 70.36
   fast with both branches (6 of 201 taken poses on the "wrong" one; the proposer's 2-deg psi grid gave 69.80) and
   63.75 with sigma fixed to -1 (the mixed-branch poses had also shaped the fitted levels).
2. **Path-tracked spring, full-grid flood.** The pose-local state is the global energy minimum; a ws pose counts only
   if the 1432-node envelope flood (2-deg HG slerps, symmetric neighbour edges, the spring's local descent from the
   previous state, a stop push <= 10 deg, no basin snap > 10 deg) reaches its node in that state (+-2 deg, same
   branch). Islands dropped: 0 (proposer cell), 1 (best cell, frozen exact).
3. **J0 seat checked.** The J0 axis (on the scapula handler) must pass the same seat rule as J1 (back of the shoulder /
   acromion top).

## Measurements (score = 100 (1 - gap / 275); frozen = Bench(60,160) levels worn on Bench(110,360) exact, K6 at 1 mm)

| cell | fast Bench(60,160) | frozen exact Bench(110,360) | reach | ib14 | contact | overhead ws | hub 2 in band |
|---|---|---|---|---|---|---|---|
| plain cap 3R control, proposer config | 60.79 | 66.26 | 0.731 | 0.433 | 0.026 | 8/28 | 0.06 |
| sprung cell, proposer config, either J2 branch | 70.36 (proposer 69.80) | - | | | | | |
| sprung cell, proposer config, assembly mode fixed | 63.75 | 70.64 | 0.733 | 0.399 | 0.039 | 10/28 | 0.01 |
| plain cap 3R control, searched (198 configs, gate passed) | 54.15 (54.45 at K6 1 mm) | 60.61 | 0.756 | 0.459 | 0.021 | 10/28 | 0.06 |
| sprung 4R, search best 1 (397 configs) | 49.62 (51.71 at K6 1 mm) | 59.44 | 0.750 | 0.494 | 0.038 | 10/28 | 0.00 |
| sprung 4R, search best 2 (552 configs; springs J0 + J2 + J3) | 47.28 (47.33 with the flood; 48.77 at K6 1 mm) | 59.05 | 0.739 | 0.542 | 0.072 | 11/28 | 0.00 |
| sprung 4R, search best 3 (723 configs, still improving fast) | 45.47 (47.55 at K6 1 mm) | 57.87 | 0.739 | 0.549 | 0.067 | 10/28 | 0.00 |
| **sprung 4R, spring law exact (dmax 170), CLAIM CELL** (262-config sweep, gate passed) | 46.32 (46.97 at K6 1 mm + flood; near-touch 54.22) | **57.70** (near-touch 64.51) | 0.744 | 0.548 | 0.069 | 11/28 | 0.00 |
| sprung 4R, conservative springs (dmax 120), top 25 re-worn | 102.43 best | - | | | | | |
| ghost (bound only, oracle; proposer, in-sample, K2 off) | 44.97 quoted, 48.55 on file | not worn | | | | | |

Like-for-like (same kit, same checks, both searched to the gate on the same bench): the sprung 4R beats the plain cap
3R it replaces by 7.8 points fast (46.32 vs 54.15) but by **2.9 points frozen exact (57.70 vs 60.61)**, for one more
counted joint (+25 complexity, 4-DOF) and three springs. Against the lead (conecut-knee-knuckle-3r v_gap 18.28, 3
joints) it is 39.4 points behind.

## Limiter (measured)

**Hub 2.** At the best cell hub 2's fitted level is 121 mm from GH (skin under it ~55-75 mm): in band 0.00 (control
0.06), link 2 0.18, link 1 0.35; the springs place the spare so that hub 0 (1.00), link 0 (0.99) and hub 1 (0.99) sit in
band, which is what the search buys - a 1-D null-space serves one member set, and every searched cell spends it on
the cap-pole members, never on hub 2, because hub 2's axis at the cap pole crosses the deltoid crest / acromion edge
on > 2 % of the fit poses whatever the spare does (the proposer's step 0: J2-ray exit p95 96-107 mm). The frozen wear
then adds contact (0.072 at best 2, 0.038 at best 1): the plain-gap search buys fast points with metal close to the skin
that does not hold on 360 new poses (near-touch gap 56.28 fast / 66.40 frozen).

## Red team (best 2, Bench(60,160) fast, own script)

- **Lost ws poses (20 of 160):** 16 have no closing state even at 0.5-deg fold margins (the J0-J1 circle cannot meet
  J2's circle: the four-bar's own reach), 3 lose only to the 5-deg fold stops, 4 close only in the other J2 assembly
  mode (unreachable by the metal), 1 collides. Overhead (elev >= 140): 3 of 12 taken fast, 9 have no closing state.
- **The point that pinches:** 8 contact poses fast, deepest **-26.2 mm at plane -15 / elev 75 / axial -45** (across the
  body, internal rotation), then -13.7 mm at plane -15 / elev 105 / axial +45 and -7.0 mm at plane -90 / elev 60 /
  axial 135 (behind the back). Closest non-contact metal 0.12 mm at plane 45 / elev 165 / axial -90 (overhead).
- **The optimistic numbers:** fast -> frozen costs 10-12 points in every searched cell (best 1 49.62 -> 59.44, best 2
  47.28 -> 59.05); the fast search kept improving (best 49.62 -> 45.47) while the frozen number stayed flat
  (59.44 -> 59.05): the fast gains are bench-tuned contact, not design. The proposer's 69.80 was an any-branch number.
- **The springs' travel decides the cell:** at the taken poses the J2 spring winds -180 .. +172 deg from its rest and
  the J3 spring -123 .. +125 deg; J0 swings -57 .. +80 deg fast and -170 .. +149 deg frozen exact (a 25-deg bar sweeping
  ~320 deg about the back seat, over the acromion). The energy law is quadratic in the WRAPPED deflection, which equals
  a real spring's law only while |q_i - r_i| < 180 along the path; the model now takes `dmax` (states with a sprung
  deflection > dmax are infeasible). dmax 170 (the law exact; a 0.95-wire / D 22 / 6-coil double-leg spring at ~0.33
  N.mm/deg reaches ~96 N.mm at 170 deg with 40 N.mm preload, under a ~128 N.mm yield estimate) keeps the best cells at
  46-48 fast; **dmax 120 (a conservative torsion-spring range) collapses them to 102-191 fast** (best 2: 191.30, reach
  0.19, follow 0.15). The cell lives only with springs that wind ~+-170 deg.
- **Motion preview (claim cell, the viz loop's path-tracked spring):** 233 of 239 frames close in range; J0 snaps
  46 deg at frame 91 (a basin change the metal would feel as a jump), 4 frames have no closing state.
- **Feel:** with 40 N.mm preload per spring and the deflections above the centring torque reaches ~100-150 N.mm at the
  ends - ~1-1.5 N at a 100-mm cuff lever, felt as a pull toward rest on every pose.

## New knowledge

1. **Fix both branch signs in any null-space model.** Two fold stops pin the four-bar's assembly mode; a pose-local
   model that lets either J2 branch win misstates the design by ~7 fast points here (70.36 vs 63.75) and in the
   OPTIMISTIC or pessimistic direction depending on how the mixed poses shape the fitted levels.
2. **A spring-set null-space at the cap pole is worth ~1.6 frozen points over the plain 3R it replaces** (59.05 vs
   60.61, both searched to the gate on the same kit) - the redundancy is spent on the cap-pole members, not on hub 2,
   which is the binder. The class "spare at the cap pole" cannot reach the lead's region (18.28) with springs; only the
   oracle ghost (bound, 44.97-48.55 fast in-sample, K2 off) was ever better fast, and nothing in it is buildable unpowered.
3. **Fast-bench improvements of a spring cell decouple from the frozen number** after ~400 tries (fast -4.2, frozen
   -0.4): stop the fast search on a frozen plateau, not on the fast gate alone.
