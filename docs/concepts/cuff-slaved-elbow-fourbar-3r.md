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
