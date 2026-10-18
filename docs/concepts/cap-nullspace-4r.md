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

