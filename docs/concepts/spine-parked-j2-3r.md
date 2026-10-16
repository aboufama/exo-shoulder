# spine-parked-j2-3r - zero-passive spherical 3R at the leader's seats, slim O15 J2 / J3 hubs

Lens "round3: zero-passive spherical chain", family "spherical 3R". Model: `docs/concepts/models/spine-parked-j2-3r.py`.
Sweep log: `docs/concepts/sweeps/spine-parked-j2-3r.json`. Row: `docs/concepts/rows/spine-parked-j2-3r.json`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Settle the model split before tuning anything: the same chain cannot be worth both 33.40 and 45.01.
     The split is a measurement problem, not a design problem.
   - Treat the J2 fold as the enemy. A pure spherical 3R closes only while angle(J1, J3) stays inside
     [|a1 - a2| + margin, a1 + a2 - margin], and a short link 1 narrows that window. So sweep a1 / a2 jointly with the
     seats, and report what the fold costs: the reach lost to "no closure" alone.
   - Use the hub size as a design variable that maps to real parts: O20 (v5), O17 (2.75 mm wall), O15 (2.0 mm wall),
     all the same MR117-2RS pair. Give credit only where a part exists.
   - Hold the strap end at its hub's level as far as the collision check exempts it. A shorter ramp would be an
     unchecked zone, not a gain.
2. **The rawest material.**
   - The posed skin itself: `concept_bench` distance grids, with CB_EXACT for the exact mesh.
   - The fit clips at their full 10 fps (`CB._poses_all`) for continuity.
   - The proximity atlas data (`docs/research/proximity_atlas.md`: rigid metal must clear the highest skin it ever
     passes over).
   - `pipeline/conformal/analysis/skin_motion_map_14.json` for where skin moves under a rigid part.
   - Digested summaries are used only as pointers.
3. **Methods and tools.**
   - The kit (`tools/concept_kit.py`: K1 closure, K3 march, K4 flat hubs, K5 straps, K6 collisions, dense K2).
   - The crown / wall skin check, near-touch rule and overhead split (fold-sph3r's, here per hub radius).
   - The farm sweep (`tools/cloud_run.py sweep`), then CMA-ES (`tools/concept_cma.py`) as farm batch jobs until the
     convergence gate passes.
   - The frozen-shape run on Bench(110,360) exact (lesson c).
   - Diagnostics on each check separately (per-pair K6, fold vs K2 vs contact) to explain every lost pose.
4. **What other than me shows the number is right.**
   - The bench (`concept_bench`, an outside judge).
   - The kit audit (honest flag).
   - The verifier's frozen Bench(110,360) exact run.
   - The judge's VModel reference at the same seats (41.73 exact).
   - A red-team pose list: rest, overhead >= 140, across the body, behind the back, the q-dropped poses with the arm
     on hub 2, and the closest metal over taken poses.

(Results below.)
