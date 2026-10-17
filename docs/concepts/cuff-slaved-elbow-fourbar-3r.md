# cuff-slaved-elbow-fourbar-3r - cuff-slaved elbow (4R path with the elbow slaved to an arm-cuff pin) at the cap pole

Round 102 (J2 track jump), lens 1 (virtual J2), PICK 2; scapula-tether-elbow-3r merged as cell B.
Model `docs/concepts/models/cuff-slaved-elbow-fourbar-3r.py`, sweep `docs/concepts/sweeps/cuff-slaved-elbow-fourbar-3r.json`,
row `docs/concepts/rows/cuff-slaved-elbow-fourbar-3r.json`, preview `docs/concepts/viz/concepts/cuff-slaved-elbow-fourbar-3r.js`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask.** Treat the slave loop as a COUPLING LAW and
   read it first, before any skin: per pose the loop picks the coupler spin sigma (and so the elbow A0 and A1), so the
   only questions are (a) does the loop assemble at the poses the plain 3R loses (the folded / stretched th tails and
   the binder (-75, 60, +60)), and (b) is the root unique and far from a toggle along the real motion (a static bench
   cannot see a branch jump or a loop toggle; the dense K2 and the continuity flood can). A designer would also measure
   the transmission at both slave pins and the loop's own singularity |df/dsigma| on the taken set, and price the one
   thing a slave crank to the ARM adds: the arm-cuff pin B1 rides the deltoid in every pose, so its skin level is
   the lateral-arm level, and crank B spans the elbow-to-arm gap - the per-pose spread of that gap is what sets the
   band, not the binder poses.
2. **Rawest material.** The posed skin itself through the K3 march (`K.requirement`, fast grid cache of Bench(60,160),
   exact libigl path for Bench(110,360)), per member and per pose; the bench poses' J1-J3 angle for the arm's real J3
   axis; the four binder poses read per pose and per pin. Not the proxy's rigid-level in-band share (anch.py), which
   takes each part's level as the max over taken poses and weights hubs 79 samples.
3. **Methods and tools.** Closed-form spherical 2R closure (kit `K.closure`) inside a 1-D root solve in the coupler
   spin (2-deg bracket + bisection to < 0.01 deg, residual reported); the loop Jacobian |df/dsigma| and the two slave
   transmission angles as determinacy margins; the honest kit evaluation (`K.evaluate`: K3 march, K2 dense continuity
   on every joint axis, K6 collisions, audit) inside a (mu, lambda) CMA-style ES with restarts on the 1 mm near-touch
   gap plus a binder-pose term; the frozen exact Bench(110,360) wear of the best shape; the workspace continuity flood
   (2-deg slerp edges from rest, sigma jump <= 10 deg).
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py) and the kit audit
   (`honest` true); the plain cap-pole O20 3R through the SAME kit and bench as the control (63.18 fast,
   cruciate-knuckle-3r's control) and its proxy 36.6; the judge's reproduction of the seeds on lens 1's proxy
   (41.84 / 48.36 / 44.10 / 47.61); the frozen exact Bench(110,360) number; the binder table and the red-team pose list
   below; the adversarial verifier when it re-runs the file.

## Model (what was built, and where the spec was corrected)

`docs/concepts/models/cuff-slaved-elbow-fourbar-3r.py` (~170 lines on tools/concept_kit.py). J1 O20 at the cap pole
bvec(43.15, 59.93), J3 O20 humerus-fixed at wdir(92.03, -9.03). Per pose ONE unknown, the coupler spin sigma about J3:
A1 = arc d1 from J3 at sigma from the down-arm direction, A0 = the kit's closed-form 2R closure J1-A0-A1 (branch s2,
margin 5 deg read like th on the dyad J1-A0-A1), cell A: B0 = arc db from A0 at sb off the crank line (crank A is an
L-plate), B1 = arm-fixed at arc by / azimuth bx about J3; cell B: B1 on the coupler, B0 on the base. The loop equation
angle(B0, B1) = rho is solved by a 2-deg scan, slope branch sgn, the root nearest `home`, bisected to 0.004 deg
(residual <= 0.003 deg reported). Enforced per pose: the 2R margin >= 5, the loop slope |df/dsigma| >= sin 8 deg, the
two four-bar transmission angles >= 30 deg, pins >= 22 deg apart in every body. Six O20 v5 stacks, 3 x 12 Ti straps,
kit K2 dense (every joint value and every pin axis, 2-deg slerp), K3 march, K6, audit: every number below is `honest`.

Corrections to the spec, measured:
- **"Every part <= 75 mm" was a centre-ray reading.** Lens 1's proxy (anch.py) marched only the pin's centre ray. The
  kit's K4 marches every sample of the 20 mm O20 disc along its axis: on arm seed 1 hub A0 / A1 / B0 sit at
  **95 / 90 / 121 mm** (proxy 62 / 75 / 62). My kinematic instrument reproduces both readings (centre ray 62 / 75 / 62,
  disc edge 95 / 90 / 121): the disc edges ride the acromion / neck slope at the elevated poses.
- **Layering.** The spec's layers (crank B lowest, the rest unspecified) collided in 97 % of arm seed 1's closing
  poses (crank A vs link 1 137/154, hub B1 vs coupler 105/154, crank A vs coupler 85/154). Built by construction with
  the kit's `over`: link 1, crank B, the arm-end tab and the neck low; crank A over link 1 / crank B / the J1 stack /
  hub B1; link 1 over crank B / tab / hub A1; the coupler on top over everything it crosses incl. hubs A0, B0, J1, B1.
  The stack-ramp zone round each pin is 18 mm (kit 12): the upper member otherwise left its stack 12 mm from A0 and met
  the lower one 0.5 mm apart. Collisions fall to 0-3 % of closing poses; the price is height (the coupler rides
  89-93 mm).
- **Transmission angles.** The spec asked for transmission "at B0' / B1"; in the arm frame the loop is a spherical
  four-bar with ground J3-B1, so B1's angle is a ground angle. The model checks the two real transmission angles, at A1
  (coupler vs crank A) and at B0 (crank A vs crank B), plus the whole loop's slope |df/dsigma| (the spec's sin 8 deg,
  not anch.py's sin 8 / 2).

## The lead's kill test, read kinematically first (the risk is closure, not skin)

Instrument (`scratchpad/cse/kin.py`, ~0.4 s per layout): closure on the 360 Bench(110,360) ws poses with every model
margin; kinematic follow on the Bench(60,160) clips along the dense 2-deg slerp path (every substep closes, sigma
jumps <= 10 deg, pin axes <= 25 deg per step); rigid level of every pin (centre ray + the four O20 disc-edge samples
marched along the axis, K4) and every strap centre line = the max K3 march over the taken poses. Objective = the kill
test as a penalty (0 iff ws closure >= 0.80, follow >= 0.95, every part <= 75 mm), a (1+1)-ES with global restarts.

| cell | layouts | best ws closure (110) | best kinematic follow | layouts with every part <= 75 mm | their best closure / follow |
|---|---|---|---|---|---|
| A (arm-cuff slave) | 2727 | **0.789** (a part escapes the skin, 400 mm) | **0.833** | 42 | 0.678 / 0.733 |
| B (base tether) | 1253 | 0.489 | 0.783 | 33 | 0.481 / 0.783 |
| A, the other three assembly branches (s2, sgn) = (-1, 1) / (1, 1) / (1, -1) | 643 / 524 / 582 | 0.747 / 0.653 / 0.739 | 0.667 / 0.750 / 0.833 | | best kill-test layouts at closure 0.41 / 0.58 / 0.46 |

No layout of the 5729 reaches ws closure 0.80 or kinematic follow 0.95 at all, let alone with every part <= 75 mm.
**The kill test fails on all three counts.** (The plain cap 3R closes 281/360 =
0.781 at the same seats; the slave can only remove poses from the free 4R path, and here it removes more than it
saves.)

Where the arm cell loses its ws poses (best kill-test layout, Bench(110,360), first failing check): taken 248-256,
**loop has no root 53**, **the elbow 2R never closes on the whole sigma circle 43-49** (A1 rides a d1 ~ 68-74 deg
circle round J3 that never comes within d0 + L - 5 of J1: the 4R path's own th window), transmission < 30 4-6, loop
singular 3, root only on the other branch 1. Overhead (elev >= 140, 28 poses): taken 7-9, no root 9-11, 2R open 9.
The binder (-75, 60, +60) is lost on both readings (no root / transmission 27 deg).

## Honest kit numbers (Bench(60,160) fast, K3 march + K2 dense + K6 + audit, q 1.0)

| config | gap | score | reach | follow | ib14 | ib10 | contact | ws closure | note |
|---|---|---|---|---|---|---|---|---|---|
| plain cap-pole O20 3R (control, same kit; cruciate-knuckle-3r) | 63.18 | 77.0 | 0.794 | 1.0 | 0.375 | 0.192 | 0 | | the bar |
| arm seed 1 (judge's 41.84 proxy) | 119.23 | 56.6 | 0.731 | 0.617 | 0.210 | | 0 | 0.731 | final layering (181.18 with the spec's layering) |
| arm seed 2 (48.36 proxy) | 171.13 | 37.8 | 0.313 | 0.450 | 0.276 | | 0 | 0.463 | |
| tether seed 1 / 2 (44.10 / 47.61 proxy) | 216.14 / 239.82 | | 0.225 / 0.194 | 0.083 / 0.083 | 0.280 / 0.075 | | 0 | 0.35 / 0.25 | |
| cell B (tether) best, 143 configs | 132.86 | 51.7 | 0.300 | 0.750 | 0.371 | | 0 | 0.456 | B1 / crank A / coupler 0-0.17 in band |
| **cell A (arm) best** | **110.11** | **59.96** | 0.750 | 0.683 | 0.216 | | 0 | 0.738 | near-touch gap 110.11, min metal 1.16 mm |

Best params (cell A): d0 29.78, L 30.37, d1 73.61, sb 43.49, db 45.0, rho 60.82, bx -170.87, by 22.0, home 89.21, s2 -1,
sgn -1. Per member in band: hub J1 1.00, hub J3 0.69, neck 0.76, hub B1 0.34, tab 0.31; hub A0 0.00, hub A1 0.00,
hub B0 0.04, crank A 0.00, link 1 0.00, coupler 0.00, crank B 0.09. Kit hub levels: J1 54, A0 97, A1 112, B0 130,
B1 68, J3 70 mm. Mass 243 g Ti. Every elbow part is a rigid body whose level is the highest skin it passes over across
the taken poses, and the elbow wanders over the whole shoulder dome: **the elbow's per-pose spread sets in-band, as the
judge said; the binder poses are lost, not served**.

## Frozen exact on the verification bench (lesson c)

The 110.11 shape (every underside fitted on Bench(60,160) fast, frozen) worn on Bench(110,360), exact libigl path,
K2 dense + K6 rebuilt there (`scratchpad/cse/frozen.py`): **gap 117.71 (score 57.20)**, reach 0.689, follow 0.673,
ib14 0.2175, ib10 0.091, contact 0.0062 (min metal **-2.86 mm**: 3 poses penetrate), near-touch gap 117.71, ws closure
0.733, K2 flips 32, collide 0.044, **overhead (elev >= 140) 7 / 28**. The plain cap 3R through the same protocol reads
56.40 frozen exact (T-0 control): this cell is 61 points behind it.

Binder table (Bench(110,360) nearest ws pose, frozen best):

| binder | bench pose | closes | K2 | collides | taken |
|---|---|---|---|---|---|
| (-75, 60, +60) | (-75, 60, 60), idx 128 | yes | yes | **yes** | no |
| (0, 150, 0) | (0, 150, -15), idx 209 | **no** | | | no |
| (30, 150, 0) | (30, 135, 0), idx 262 | **no** | | | no |
| (0, 105, 0) | (0, 105, 15), idx 205 | yes | yes | **yes** | no |

## Red team (my own best config)

- **The motion that jams** (dense K2 on the best, first failing check): Raise overhead 11/11 and Drink / Comb 10/10, 9/9
  are followed, but **Reach a high shelf loses 5 of 9** transitions - from (72, 71, -72) toward (78-82, 105-132,
  -78..-82) the slave loop has NO ROOT 16-18 deg into the motion (an internally rotated climb); **Wash opposite shoulder
  loses 7 of 9** - from (42, 8, -37) toward the cross-body (120-145, 30-60) the root vanishes 18-28 deg in; **Reach back
  pocket loses 3 of 8** within 4 deg of (-63, 36, 75) -> (-80, 39, 101). Two more transitions are a root SWITCH (J1
  jumps 166-167 deg, the A0 axis 59 deg in one 2-deg step). A static bench cannot see these; the dense K2 does.
- **The point that pinches**: fast min metal 1.16 mm over the taken poses (near-touch gap = plain gap); frozen on the
  big bench three poses penetrate to -2.86 mm.
- **The optimistic numbers**: (1) the proxy's "every part <= 75 mm" (centre rays; the O20 disc edges are 90-130 mm);
  (2) the proxy's follow 0.918 (static closure of the clip frames; continuity along the motion is 0.68-0.83 kinematic,
  0.62-0.70 honest); (3) the judge's +20 calibration (proxy 41.84 -> honest 119.23 for the same seed: +77, because the
  proxy has no layering, no disc edges and no continuity).
- **Loads** (not measured, stated): crank B is a two-force member that carries the wearer's moment about J3 between the
  arm cuff and the elbow plate; at the 30-deg transmission floor its force is 2x the tangential load. The arm-end tab
  makes the cuff part of the loop, so cuff slip on the arm moves B1 and with it the elbow (the self-aligning slides must
  sit below BOTTOM, outside the loop).

## Search and convergence (Bench(60,160) fast, honest kit, objective = the 1 mm near-touch gap)

Honest sweep `docs/concepts/sweeps/cuff-slaved-elbow-fourbar-3r.json`, in time order: the entries tagged `model: v1`
ran before the layering fix (more collisions, every one of them worse); the gate is read on the `v2` entries (final
model). Runs (local, niced, <= 2 processes; the farm is closed): the kinematic kill-test ES (5729 layouts over the
four assembly branches (s2, sgn) and the tether cell, `scratchpad/cse/kin*.json`), then honest (mu, lambda)-ES runs
from the kill-test elite (16 layouts), from the four seeds, from the best two layouts of each other branch and a
restart from the honest top 4 twice. Branches: (s2, sgn) = (-1, -1) holds every good layout (kin obj 27.1; the others
49-99, honest 135.42 at best); cell B (tether) honest best 132.86.

GATE_PLACEHOLDER

## Verdict

**DEAD at gate 0.** Best honest 107.61 fast (score 60.87) against the plain cap-pole 3R's 63.18 through the same kit
(round gate bar 17.5 frozen exact); frozen exact Bench(110,360) of the 110.11 shape 117.71 against the control's 56.40.
The lead's kill test fails on all three counts over 5729 layouts (ws closure max 0.789 < 0.80, kinematic follow max
0.833 < 0.95, every part <= 75 mm only at closure <= 0.68). Binding, measured: (1) the slave loop's ROOT vanishes along
internally rotated climbs, cross-body and behind-back motions (dense K2), and on 53 ws poses; (2) the 4R path's own
window (the elbow 2R never closes on 43-49 ws poses); (3) the elbow parts (A0, A1, B0, crank A, link 1, coupler) are
0-4 % in band at 76-130 mm because they roam the shoulder dome.

## New knowledge (beyond this morphology)

1. **A slave crank grounded on the arm cuff cannot follow internal rotation.** The loop's root exists only while the
   arm-fixed pin B1 stays within reach of the crank-A pin; an internally rotated climb (Reach a high shelf) or a
   cross-body sweep carries B1 round J3 out of that reach and the root disappears mid-motion. Any 1-DOF coupling loop
   closed THROUGH the arm inherits the arm's axial rotation in its root existence - a bench that scores poses one by
   one cannot see it (proxy follow 0.918 vs dense 0.62-0.83).
2. **Centre-ray hub levels are 15-60 mm optimistic for pins that roam the dome.** The O20 disc edge (K4) reads A0 95 /
   A1 90 / B0 121 where the centre ray reads 62 / 75 / 62. Any proxy that marches only pin centres (anch.py, lens 1's
   opt.py) overstates in-band for every moving pin; the "every part <= 75 mm" screens of round 102 lens 1 were made
   that way.
3. **The proxy -> honest calibration (+20) does not hold for loop mechanisms**: +77 on arm seed 1 (41.84 -> 119.23):
   the proxy has no layering (the spec's layering collided in 97 % of closing poses), no disc edges, no continuity.
4. **A virtual J2 must make its extra pins move LESS than the J2 axis would, not just stay off the J2 ray**: here the
   elbow pins wander as far as a plain J2 hub (97-130 mm at the best), so the 3R's hub-2 problem comes back in three
   pins instead of one.

## What next

Lens 1's slaved-elbow branch is closed with these numbers; the J3 closer's ceiling statement can cite: no 1-DOF slave
(arm-grounded or base-grounded) of a cap-pole 4R path closes >= 0.80 of Bench(110,360) ws with continuous motion. The
remaining J2 lever named by the planner (a J2 with no metal on its axis) is now down to the open four-bar
(remote-pole-fourbar-j2-3r, pick 1, running) - and finding 2 applies to its pins too.
