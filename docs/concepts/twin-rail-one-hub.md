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

## Morphology and model (docs/concepts/models/twin-rail-one-hub.py, shared kit)

Scapula handler -> **crown rail** (S-fixed band, W1 = 20 mm wide x 6 mm radial: the caged-ball wire-race C-slide of
docs/research/ring_and_shell_hardware.md option A) on a circle about the VIRTUAL axis a1 (no metal at the pole) at cone
ar1 -> **carriage 1** (shoe Lc >= 24 mm, 2 mm edge lips, roof 4 mm over the band; q1 = its azimuth about a1) ->
bridge strap 12 x 3 -> **J2 = the only hub** (O20, K4 flat disc, 12.25 mm stack) on a2, fixed in link 1 at cone a12
from a1 on the carriage's meridian, beside the rail (ar1 = a12 + d1) -> **link 2** strap 12 x 3 -> **carriage 3** on
the **arm rail** (H-fixed band, W3 = 20 x 6, about the VIRTUAL axis a3 at cone ar3; q3 = its azimuth) -> K7 neck
14 x 6 from the arm rail's END (a tab beyond the carriage travel) to BOTTOM's bar. Spherical 3R (a1, a2, a3; link
angles a12, a23), closed form (K1, residual 0.0 deg), branch sigma. **3 ACTIVE DOF, 0 PASSIVE.**

Honesty: K3 march on every skin-facing sample, K2 dense continuity (values and axes, incl. both carriage directions),
K6 collisions on every pair except the same-body / rolling-joint pairs (rail-carriage, carriage-bridge-hub, link 2 -
carriage 3, arm rail - neck), audit clean. Rail extents = the carriage travel over the closing bench poses (central
share `cov`) + half a shoe + 3 mm end stops (+ 8 mm neck tab on the arm rail), a design step cached per kinematics
and computed from all bench frames, so build() stays pose-local; poses beyond the rail are not taken. Rails are laid
out at their fitted radius (fix point, <= 2 re-runs), so a band is never narrower than its W. A rail that would close
on itself (> 330 deg) or a shoe that wraps > 120 deg of its circle is rejected (the configuration takes no pose).

Spec corrections (each measured or argued):
* **Rail length.** The spec hopes for +-35 deg on the crown patch. Measured (kinematics only, 5835 random axis sets,
  1640 with >= 85 % clip and >= 80 % workspace closure): the 95 %-central carriage travels sum to **>= ~300 deg**
  (best t1 + t3: 121 + 189, 182 + 129, 135 + 178 deg). No spherical 3R that follows the bench has both rails short;
  each rail spans 120-190 deg of travel plus the shoe.
* **J2 beside the rail.** A donut centred on the carriage's own ray at the rail's level is crossed by the rail; the
  hub sits on the carriage's meridian at cone offset d1 (|d1| >= ~20 deg so the O20 disc clears band + lips).
* **O20 hub** instead of the KAA15XL0 donut (r 19-26 mm, claimed 9 mm stack): smaller footprint, the swarm's honest
  12.25 mm stack.
* **Constant section per row**: the crown and arm rails are ONE section swept along a circle about their virtual
  axis (what a carriage can roll on; also the user's no-loft rule), but the section follows the skin across the band
  (per row, = max over the arc and the poses), instead of the spec's single radius for the whole band (variant a).
  Variant b (rail shaped per station, needs a radial float in carriage 1 = a cam follower) is `revolve=0`: an
  optimistic bound for the crown rail only.

## Raw measurement: where a long rail can lie (per-pose skin radius maps)

From the posed skin of all 220 bench poses I built per-pose K3 skin radii on 6600 directions in the scapula frame and
in the humerus (band) frame (scratch envmap.py; 2.5 deg grid). For every one of the 1640 kinematically valid axis
sets, I placed both rails at their 90 % travel and fitted them as constant sections:
* only **8 %** of the axis sets have a crown rail whose every row clears the skin within 250 mm (the arc runs into
  the neck / chest / arm in the rest); the best crown rail is **0.49** in band (2-14 mm), the median 0.
* the arm rail is best (0.5-0.79) when it degenerates into a **small ring (ar3 = 10 deg, radius 12-19 mm) around a
  lateral humeral pole on the deltoid cap**, i.e. a ring bearing at J3, not a rail along the arm. Arm rails on the
  lateral upper arm (a3 near the humerus axis, ar3 18-35 deg, the spec's intent) are <= 0.2 in band: the rail must
  span the humeral rotation range (210-320 deg with the shoe) round the arm.

## Coarse sweep (farm, 166 configurations, 243 s wall, $0.012)

Configurations: the prescreen's 80 best axis sets (by both rails' in-band share), each with two rail offsets and
widths, the spec's own family as far as the prescreen found any rail of it clear of the body (crown headband + arm
rail on the lateral arm, a3 within 35 deg of the humerus axis, ar3 >= 18 deg: 4 configurations), and 60
perturbations of the top 20. Only 38 of the 166 pass the open-arc and shoe-wrap
rules at all (the rest need a rail that closes on itself). Best honest (k64): **gap 122.14** (score 55.6): reach
0.563, follow 0.833, in-band 14 0.133, contact 0. Re-run with the layout fix point (rails at their fitted radius:
R1 94, R3 108 instead of the prescreen's 100 / 113): **gap 119.62**, reach 0.563, follow 0.85, in-band 14 0.141,
in-band 10 0.082. The spec's family (arm rail along the lateral arm: k102-105, and k134-135 with ar3 27-31 lower on
the arm) is never honest: in every one J2's axis finds no skin to sit on within 220 mm in some taken pose (hub level
400 = infinite), so hub 2 and link 2 float; best of them gap 211.8 (k104, dishonest).

## Red team (coarse leader k64, fix-pointed; `python3 ... redteam <params>`)

* **Named pose groups taken**: rest 54 / 57 (3 lost to closure), **overhead 2 / 17** (7 beyond the rails' travel, 5
  part collisions, 3 closure), **across the body 9 / 27** (10 beyond the rails, 4 closure, 2 continuity, 2 collisions),
  behind the back 15 / 21 (5 beyond the rails, 1 closure).
* **The pose that sets the crown rail**: plane 45, elevation 165, axial -90 (workspace): the elevated arm passes
  under the S-fixed arc. Its rows sit at 94-111 mm against a median skin requirement of **52 mm** along the arc, so
  the crown rail is **0.0 in band** in every pose. The arm rail is set by the arm at the side (plane -15, elev 0,
  axial -30): rows 107-124 mm against a median 88 mm; 0.26 in band.
* **The rail that cannot be long enough**: at cov 1.0 (every closing pose on the rail) the arm rail would span 420
  deg (it must cover the humeral rotation range plus the shoe): impossible. At cov 0.8: gap 133.1 (reach 0.49). The
  90 % cut is the trade, and it caps reach.
* **The point that pinches**: the K7 neck at 2.02 mm (plane -80, elev 39, axial 101, a clip frame: hand behind the
  back) and the arm rail at 2.06 mm (arm at the side, axial -75): taken by the bench rule, on the 2 mm edge.
* **The member that floats**: link 2 (0.0007 in band) and hub 2 (0.09; level 73 mm, 17.9 mm free above it, parking
  rule OK) - the same J2 / link 2 limiter as the spherical family: the rails replaced the poles, not the middle.
* **The variant that removes the crown-rail limiter** (`revolve=0`: crown rail shaped per station, a cam track with a
  radial float in carriage 1; an optimistic bound, the float's own height not charged): crown rail 0.64 in band,
  in-band 14 0.42, but **gap 97.64** (reach 0.54, follow 0.82, the same pose losses). Still 29 behind the champion.
