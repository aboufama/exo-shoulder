# twin-rail-one-hub - virtual J1 on a crown rail, virtual J3 on an arm rail, one hub

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Check the premise before the
   geometry: the travel of q1 and q3 is set by the arm's workspace and the 3R's axes, not by the rail, so scan the
   kinematics first (no skin) and measure how long each rail must be. The spec hopes for +-35 deg on the crown, but
   an arc rail is metal over its WHOLE arc in every pose. (b) Treat each rail as what a carriage can actually roll on:
   ONE constant section swept along a circle about the virtual axis (a surface of revolution). Its section may follow
   the skin across the band (per row), but along the arc it is set by the highest skin under that row ANYWHERE on the
   arc in ANY pose. Then place each rail where the raw S-frame / H-frame skin envelope is flat along a circle.
   (c) Put J2 beside the rail on the carriage's meridian, not "centred on the carriage's ray at the rail's level" (that
   annulus would cross the rail), and pick the side of the rail. (d) Fix the arm rail to BOTTOM at a rail END,
   beyond the carriage travel, with a K7 neck. A tab under the travel would block the carriage.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance. From it I
   built my own per-pose skin-radius maps in the scapula frame and in the humerus frame (6600 directions x 220
   poses, K3 march), instead of reading the atlas summary. Also the fit clips in time order (dense K2 along the
   slerped motion) and the everyday workspace poses. The skin-motion map and the proximity atlas serve only as
   cross-checks: S-fixed metal is good over the top and the back of the shoulder, H-fixed metal only on the upper arm.
3. **Methods and tools.** Closed-form spherical IK (K1 two-circle closure, residual reported); a kinematics-only scan
   of the axis sets (travel per rail); envelope lookups to place the rails; the shared kit (K3 march, K4 flat O20
   hub, K5 straps, K7 neck, K2 dense continuity, K6 collisions with the same-body pairs exempt); a coarse sweep, then
   CMA-ES on the cloud CPU farm until the convergence gate passes.
4. **What, other than me, shows the number is right.** tools/concept_bench.py on Bench(60,160) (same poses and
   metrics as every concept; champion 68.93), the kit's audit (honest flag), the swarm's adversarial verifier (exact
   path, Bench(110,360)), and the red-team pose list below: rest, overhead, across-the-body and behind-the-back, the
   pose that jams, the point that pinches.
