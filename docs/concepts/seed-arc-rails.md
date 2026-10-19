# seed-arc-rails - three concentric arc rails about the GH centre

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat each rail as what it is
   kinematically: a revolute joint with a remote axis through GH, i.e. a circle about that axis. A circle about an axis
   through GH is at ONE distance from GH everywhere, so the only freedom per rail is its polar angle rho about the axis
   (rho = 90: the spec's great circle; rho -> 0: a hub) and its radius. The designer would (a) measure first whether a
   great circle can lie on the skin at all (it cannot: a 190-250 deg great circle about GH runs through the neck, trunk
   or arm), (b) not fix the third rail on the humerus long axis (a C-ring needs ~250-300 deg of ring because the
   carriage's azimuth around the arm couples swing and twist), but put it about the axis the best spherical 3R already
   found (86 deg from the long axis), and (c) sweep rho per rail to see whether any rail between "hub" and "great
   circle" sits closer to the skin than the champion's links.
2. **Rawest material.** The posed skin of every bench pose (the rig's render skin, via the bench's signed distance), the
   fit-clip motions at their native 10 fps (closure, rail range and branch continuity are checked on EVERY frame of the
   fit clips, not only the 60 bench samples), the everyday-workspace envelope. The skin-motion map
   (pipeline/conformal/analysis/skin_motion_map_14.json) is a digest; the bench skin is used directly.
3. **Methods and tools.** Exact two-circle closure of the spherical 3R (the band evaluator's, with its 10 deg fold
   margin); per-rail radius fitted by the baseline's percentile rule (sphere tracing on the bench's signed distance);
   every part at real size (rail 8 x 4, carriage 20 x 12 x 8, strap links 8 x 3) sampled on a 2 mm grid; part-part
   clearance by k-d tree on volume samples; the cached signed-distance grid Bench(60, 160).
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same metrics and poses as every other
   concept), the swarm's adversarial verifier, and a red-team pose list (rest, 170 deg overhead flexion/abduction,
   across-the-body adduction, hand behind the back) written below with the reason each fails or passes. The hub-like
   limit (rho ~ 12 deg) on the champion's own axes was run as a calibration against the baseline (68.9): it lands at
   72.7-81 (rev 3), the same family, which shows the model is not flattering itself.

## Morphology and model

Topology (scapula handler -> user's cuff): RAIL 1 fixed on the scapula handler, a circle about u1 (through GH) at polar
rho1 on the sphere R1 -> CARRIAGE 1 (20 x 12 x 8, its place on the rail = joint 1) -> LINK 1 (8 x 3 strap) -> RAIL 2, a
circle about u2 at rho2 on the sphere R2 -> CARRIAGE 2 (joint 2) -> LINK 2 -> CARRIAGE 3 -> RAIL 3 fixed on the cuff, a
circle about W (an axis fixed in the humerus through GH) at rho3 on the sphere R3 (joint 3). Every rail axis passes
through GH, so the chain is a spherical 3R: 3 ACTIVE DOF, each carriage driven along its rail. Passive DOF: 0 on the
bench (GH is fixed in the scapula frame there, so the chain closes exactly without the cuff slide the catalogue lists;
a slide would be an undetermined passive coordinate under R17 unless sprung - not modelled).

Spec changes, each measured (docs/concepts/sweeps/seed-arc-rails.json, stage tags):
* stage A, the catalogue spec (great-circle rails 1 and 2, C-ring about the humerus long axis): no finite radius
  exists - the rails' needed spans (190-270 deg) run into the trunk / neck / arm in every layout tried. Dead as specified.
* the third rail moved off the long axis to the champion's humerus-fixed axis (86.3 deg from the long axis, az 21.8);
  the C-ring needs ~300 deg of ring (swing-twist coupling of the carriage azimuth) and its medial part enters the trunk.
* the rails are crowns of polar rho1, rho2, rho3 about the champion's three axes (u1 az 2.43 el 80.68, a12 76.9, a23
  66.75, branch -1); rho -> 0 is the hub limit.

Model file: docs/concepts/models/seed-arc-rails.py (`check`, `sweep`; task API `metal(pose, frames, params)`).
Radii are refitted twice so carriage and strap footprints are at their real size at the fitted radius.

## Results (Bench(60, 160), fast grid; baseline spherical 3R = 68.93)

Best, CONVERGED (sweep k438 / k441, stage F, radius fit iterated 3-4 passes to a fixed point): **gap 73.0** -
reach 0.894, follow 1.000, inband14 0.186, inband10 0.097, contact 0.010, at p98. Worse than the baseline (68.93).
Geometry (PARAMS in the model): rails as small crowns (rho1 12, rho2 20, rho3 12 deg) about the champion's axes with the
base axis turned to az -30 (u_el 80.68, a12 76.9, a23 66.75, rail-3 axis 86.33 deg from the humerus long axis, az
21.83, branch -1); radii R1 61.6, R2 170.9, R3 74.7 mm; spans rail 1 360 deg (a full ring), rail 2 154, rail 3 ~300.
449 sweep entries (A spec, B crowns, C refine, D axes, E re-measure, F/G converged checks). Corrections, in order,
all found by red-teaming my own best: rev 1 left the links on the skin while their rail hung 17 cm out (reported 46.7 -
wrong); rev 2a joined links at rail level (they cut their own rail - every pose interfered); rev 3 with the default 2
radius passes reported 57.3 for this geometry (k369) but the radius fit was not converged (pass 2 sized the parts at
the p100 radii); iterated to a fixed point the same geometry scores 73.0, and the next three rev-3 geometries 78.9-89
(stage G; some diverge, R1 running to 130-160 mm). Only the converged numbers are claimed.

The converged best is worse than the baseline on inband (0.19 vs 0.44) and better on reach / contact (0.89 / 0.010 vs
0.775 / 0.10): the J2 rail and its carriage sit 17 cm from GH, more than 3 cm off the skin everywhere (rail 2,
carriage 2, link 1, link 2 = 57 % of the metal, ~0 % in band) - against the user's 1 cm rule in spirit as well.

### Measured limiter
* **The spec as written has no finite radius** (stage A, 30 entries): great-circle rails need 177-275 deg of arc about
  GH and run through the trunk, neck or arm at every radius up to 250 mm; the C-ring about the humerus long axis needs
  200-315 deg (the carriage's azimuth around the arm couples swing and twist) and its medial part enters the trunk.
* **Bigger rho is always worse** (stage B): rho1 12 -> 30 -> 50 pushes R1 from 59 to 88 to 117 mm (the crown runs over
  the trapezius / neck); rho3 12 -> 30 pushes R3 from 73 to 86. The best rail is the smallest crown, i.e. the hub limit:
  "arc rails" degenerate to the spherical 3R with ring bearings.
* **The J2 rail lands on the elevated arm.** Per-pose radius need of rail 2: median 62 mm, p90 89, p95 121, max 183.
  The large needs are all at 90-150 deg of abduction / scaption (plane 0-30), where the J2 axis points within ~26 deg
  of the humerus (u2 ~ (-0.16, 0.64, 0.75) in the thorax frame): the rail sits on the arm and must clear it radially.
  Lower percentiles bring R2 to 105-125 mm but put 5-13 % of the poses in contact. Turning the base axis to az -30
  helps (stage D) but does not remove it; a23 56 / 78, a12 68 / 86, W at 72 / 100 deg, W az 0 / 45 are all worse.
* Rail 1 is the one good rail: per-pose need spread 54.7-58.2 mm (3.5 mm over every valid pose), 69 % in band.

### Red team (best config, 2-pass radii = the k369 sizing; the converged radii differ by < 3.5 mm on rails 1 / 3)
* Rest, reach-back-pocket (plane down to -80, axial +101), across the body (plane 120-140, elev 59-75): taken.
* Jams: the fold singularity (10 deg margin) at across-the-body with deep internal rotation (plane 120, elev 90-105,
  axial -120 / -135) and at overhead (4 of 13 poses at elev >= 150). Elevation 0-30: 58/58 taken.
* Pinch: overhead (Raise overhead, elev 149-150): carriage 1 2.2 mm and rail 1 2.8 mm from the skin - the
  acromion / upper trapezius rises under the scapula rail when the arm is up; one workspace pose at elev >= 150 is in
  contact.
* Per part over taken clip frames (share 2-14 mm): rail 1 0.69, carriage 1 0.59, rail 3 0.13, carriage 3 0.24,
  rail 2 / carriage 2 / link 1 / link 2 0.00-0.01.

### Verdict
DEAD as a morphology - not worth a GPU sweep: the rail idea itself (rho > 12 deg) measured worse at every step, the
converged best (73.0) does not beat the hub baseline it degenerates to, and it only gets there by parking J2 far off
the body. What predicts beyond it: (1) a circle about an axis
through GH is at one distance from GH, so a rail can hug only skin that is itself near-spherical about GH and static in
the rail's body - the scapula rail over the acromion is (3.5 mm spread), the moving middle rail is not; (2) any
spherical chain whose middle axis comes within ~25 deg of the humerus at 90-150 deg abduction puts its J2 on the arm;
(3) the base-axis azimuth (-30 vs +2.4) mattered more than any rail parameter - worth a look in the hub family too.

Lesson for every model in the swarm: a percentile-fitted radius that sets its own parts' angular size must be iterated
to a fixed point before the number is quoted (here 2 passes flattered the gap by 16 points).

Files: docs/concepts/models/seed-arc-rails.py, docs/concepts/sweeps/seed-arc-rails.json,
docs/concepts/rows/seed-arc-rails.json, docs/concepts/img/seed-arc-rails.png (rest and highest taken pose, skin grey).

## Audit (2026-10-15T19:12:07Z)

I tried to refute the death on Bench(60, 160) fast, the same as the agent's bench.

- **Reproduced.** `seed-arc-rails.py check` (PARAMS) gives gap 73.0: reach 0.894, follow 1.000, inband14 0.186,
  inband10 0.097, contact 0.010, R1/R2/R3 61.5/170.9/74.7 mm. This matches sweep entries k436/k438/k441.
- **Conventions vs tools/concept_baseline.py.** The model uses the same bvec/w_dir, two-circle closure, 10 deg fold
  margin, 2 mm sampling and 2 mm clearance as the baseline. It differs from the baseline in three places:
  (a) A rail's radius is the p-th percentile of each pose's maximum over the whole rail. The baseline's flat hub takes
  the maximum over samples of each sample's percentile, which is a little more lenient. A rail has to be a single
  circle, so (a) is physics, not a bias, and the sweep over p (50-100) already covers that trade-off.
  (b) Top and edge samples also count toward contact. This rejects only 2 poses.
  (c) Continuity is checked at 10 fps. It produced 0 flips at the best configuration.
  None of these three is over-strict enough to move the gap by much.
- **Kinematics and sizing.** Closure is unchanged from the baseline (15 closure failures at the fold). The links join
  their parts' radii (rev 3), and the radius fit is iterated (the check gives the same result with 2 and 4 passes).
  I found no modelling bug.
- **Missed regions (6 configurations x 4 percentiles, 4 fixed-point passes, scratch only):**
  - Hub-limit crowns (rho 6-8), at the champion u_az 2.43 and at -30: gap 81-216. The cut that stops carriage 2
    before its rail-2 mount grows as 1/sin(rho), so a crown below about 10 deg leaves the carriage almost no travel
    ("off rail" 101-180 poses). A hub-sized rail is a ring bearing, which is the baseline's case.
  - Rail 2 turned with phi2 = 90 / -90 / 180: gap 85.4 at best. The other settings give no finite radius or make
    link 2 hit rail 2.
- **Verdict: the death stands.** The measured limiter is R2. Rail 2 has to clear the raised arm at 90-150 deg
  abduction, so its radius is 171 mm at p98 and inband14 is 0.19 (the baseline gets 0.44). Lower percentiles trade
  that for 5-13 % contact. Note that 73.0 is within 10 of 68.93, but the best design is the hub 3R with a different
  base azimuth. The thing to carry forward is u_az around -30 for the 3R family, not a GPU sweep for this morphology.
