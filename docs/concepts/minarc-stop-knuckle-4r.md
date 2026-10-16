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

## Results

(filled in as measured, below)
