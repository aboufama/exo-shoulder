# arm-parked-knee-4r - Arm-parked knee 4R (J4 torsion spring parks the knee hub on arm skin; J2 fold-margin stops)

Screened 2026-10-16 (round 4). Model `docs/concepts/models/arm-parked-knee-4r.py`, sweeps `docs/concepts/sweeps/arm-parked-knee-4r.json`,
row `docs/concepts/rows/arm-parked-knee-4r.json`, motion preview `docs/concepts/viz/concepts/arm-parked-knee-4r.js`.

## The deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Re-measure the ideation number under
   the user's 05:50 rulings before anything else: the 22.36 frozen crossing used slim O15 hubs at J2-J4 and a 10 deg
   fold margin; O20 everywhere is now the rule, so the first number is the O20 control at the same seats. (b) Treat the
   spare as a statics problem, not a policy: the knee azimuth is the energy minimum of the J4 spring under two unilateral
   stops, so check (i) the stop is always pushed (it is, by construction: the unconstrained minimum lies outside the
   window whenever a stop is touched), (ii) the spring preload against the friction and gravity the self-motion
   collects (virtual work through the self-motion Jacobian dq_i/dd, pose by pose), (iii) the coil's real envelope - a
   torsion spring that wraps an O20 housing has OD ~23 mm, so hub 4 is rad ~12, not 10. (c) Ask whether J4 must be a
   4th ACTIVE joint at all: in MVP1 every joint is an unpowered bearing pair; if J4 is a sprung, sensed passive pin the
   complexity drops 32.25 -> 13.25 (tools/simplicity.py), and the same bench number stands. (d) Use the spare for what
   it is worth - the J2 fold window - and measure the counterfactual (J4 locked at the park seat).
2. **The rawest material.** The posed skin itself through the bench's signed-distance grids (tools/concept_bench.py,
   Bench(60,160) fast, Bench(110,360) exact, held-out clips never used), the clip frames for continuity (dense K2 re-runs
   the spring policy between frames), the proximity atlas data and the skin-motion map
   (pipeline/conformal/analysis/skin_motion_map_14.json) only as a cross-check of where hub 4 / link 3 ride; the
   measured chain drag (judge/dynamics.py, docs/FINDINGS.md "Unpowered tracking": 0.05-0.10 N.m about the shoulder,
   rolling bearings tau0 1 N.mm + mu 0.005 |M_perp|).
3. **Methods and tools.** tools/concept_kit.py (K1 closure with the fold margin, K2 dense continuity, K6 part
   collisions at 1 mm / 0.15 mm adjacent, skin-fitted undersides, O20 hub, crown + wall skin check of
   spine-parked-j2-3r's verified extras, near-touch, overhead >= 140 split); the cloud CPU farm (tools/cloud_run.py:
   coarse sweep of 200 configurations, then 6 CMA-ES streams of tools/concept_cma.py - margin 5 and 10, two basins, a
   near-touch objective) with the convergence gate; frozen shape worn on Bench(110,360) exact; virtual work for the
   spring (self-motion Jacobian from the model's own kinematics); tools/simplicity.py for the mechanism record.
4. **What, other than me, shows the number is right.** The bench (Bench(60,160) fast for the search, Bench(110,360)
   exact with the frozen fit shape for the claim), the adversarial verifier of this round (it re-measures with its own
   harness, docs/concepts/verify/), the red-team pose list below (rest / overhead / across / behind the back: taken or
   not, why, min metal-skin distance), and the in-model controls (J4 locked; O15 control for attribution only).

## Results

(filled in below as the sweeps land)
