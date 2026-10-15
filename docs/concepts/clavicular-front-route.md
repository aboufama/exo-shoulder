# clavicular-front-route: Front route, J1 on the bony acromio-clavicular front

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the front seat as a bone anchor
   only where the skin over it is quiet in the scapula frame in EVERY pose, including the ones where the arm, forearm
   or hand sweep across the front of the shoulder (across-the-body reach, comb hair): a scapula-fixed hub there must
   clear the arm, not just the skin under it. Pick the link arcs from the measured angle band between the J1 seat and
   the arm point over the bench poses (not round 60/60), try asymmetric arcs (short link 1 keeps J2 on the bony front,
   long link 2 reaches the arm), and check both closure branches - the fold side decides whether J2 overhead sits over
   the head/neck or over the deltoid. Count the bridge from the handler as metal (it is between the handler and the cuff).
2. **Rawest material.** The posed skin of every bench pose (the bench's signed-distance grids, `B.dist`), the fit-clip
   frames in time order, the per-pose K3 requirement of every member sample (which pose sets each member's height),
   `pipeline/conformal/analysis/skin_motion_map_14.json` and the proximity atlas field (docs/research/proximity_atlas.md).
3. **Methods and tools.** The shared kit (tools/concept_kit.py: K1 closure, K3 march, K4 flat O20 hubs with the real
   stack, K5 straps with climb limit, K7 neck, K2 dense continuity on every joint axis, K6 collisions, audit), a
   per-member/per-pose requirement diagnostic, the cloud CPU farm for every sweep (random coarse, then CMA-ES from the
   top until the convergence gate passes).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py, Bench(60,160), fast grid),
   the adversarial verifier on Bench(110,360) exact, and a red-team pose list: across-the-body at elevation 120-150 /
   plane 120-150 (the forearm over the front seat), comb hair, overhead flexion 150-165 (the fold), behind the back
   (plane <= -20), and the link-1 / bridge pinch at J1.

## Model

`docs/concepts/models/clavicular-front-route.py` (kit, all honesty checks on).
