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

Not one layout of 3980 meets any one of the three conditions at the same time as the other two; no layout reaches
closure 0.80 or follow 0.95 at all. **The kill test fails on all three counts.** (The plain cap 3R closes 281/360 =
0.781 at the same seats; the slave can only remove poses from the free 4R path, and here it removes more than it
saves.)

Where the arm cell loses its ws poses (best kill-test layout, Bench(110,360), first failing check): taken 248-256,
**loop has no root 53**, **the elbow 2R never closes on the whole sigma circle 43-49** (A1 rides a d1 ~ 68-74 deg
circle round J3 that never comes within d0 + L - 5 of J1: the 4R path's own th window), transmission < 30 4-6, loop
singular 3, root only on the other branch 1. Overhead (elev >= 140, 28 poses): taken 7-9, no root 9-11, 2R open 9.
The binder (-75, 60, +60) is lost on both readings (no root / transmission 27 deg).
