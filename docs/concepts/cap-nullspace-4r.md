# cap-nullspace-4r - cap-pole redundant 4R, null-space set by two torsion springs

Round 103 (J3, track jump), lens 2 (the low-complexity cell of the 4-DOF class). Model:
`docs/concepts/models/cap-nullspace-4r.py` (kit, `tools/concept_kit.py`; flood on `tools/spare_flood.py`'s 1432-node
envelope grid). Sweep: `docs/concepts/sweeps/cap-nullspace-4r.json`. Row: `docs/concepts/rows/cap-nullspace-4r.json`.
**4 joints counted (4-DOF, the user prefers 3), 0 passive translations.**

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
