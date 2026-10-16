# short-a2-arc-slide-3r: short-link-2 3R with a spring-returned GH-concentric arc slide under J3

Round 5 pick (lens round5:reseat-for-union). Model: `docs/concepts/models/short-a2-arc-slide-3r.py`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the relay as a force-closed
   statics problem, not a kinematic window: with J2 on a PHYSICAL dihedral stop (a pin on a fixed angle), the slide
   extends to the spring's energy minimum, so the reachable th at full travel is th(mu_stop, a2max), not a1 + a2max - m
   (the judge's window estimate). Model the stop as a dihedral, measure the difference. (b) Fold the carriage into
   hub 3's lower member (a flat sole with two shoulder screws in the slot) to cut the +5 mm stack to +3.15, and keep
   the rail underside flush (keeper plate in an underside groove) so nothing hangs below the rail. (c) Check the
   self-motion statics: in mode A the chain J1-J2-slide-J3 has a 1-DOF self-motion; the spring preload must beat the
   gravity generalized force of link 1 + hub 2 + rail along it plus slot friction (R17), and the felt switch force is
   the spring moment at the slot radius. (d) Continuity on the RAW 1432-pose workspace grid, not only bench samples.
2. **Rawest material.** The posed skin itself through the bench's signed-distance grid (fast cache for the search, the
   exact libigl path for the claim), the raw workspace grid of 1432 poses (`concept_bench._poses_all`) for the flood
   fill, the 6 fit clips frame by frame (follow), the skin-motion map `pipeline/conformal/analysis/skin_motion_map_14.json`
   for where hub 3 / the rail tail sit, not the proposer's proxy numbers.
3. **Methods and tools.** `tools/concept_kit.py` (K1 closure with per-pose a2, K2 dense continuity on every axis and
   the slide, K3 march, K4 O20 hubs, K5 straps, K6 collisions at 1 mm by construction + check, K7 neck), a cap member
   for the constant-radius rail travel zone, the farm (`tools/cloud_run.py sweep`) for the coarse sweep and
   `tools/concept_cma.py` CMA-ES jobs until the convergence gate passes, then a frozen exact Bench(110,360) wear.
4. **What other than me shows the number is right.** The bench (the outside judge), the frozen exact Bench(110,360)
   wear, an independent verifier re-running the model with its own checks, and the red-team pose list in this doc
   (rest, overhead, across-body, behind-back, the jam edges of the flood fill, the near-touch poses).
