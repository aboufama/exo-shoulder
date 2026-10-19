# cam-coupled-4r: a 4R whose spare is set by a roller in a scapula-fixed slot

Model: `docs/concepts/models/cam-coupled-4r.py`. Sweeps: `docs/concepts/sweeps/cam-coupled-4r.json`.
Row: `docs/concepts/rows/cam-coupled-4r.json`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Read the slot as what it really is. The pin is fixed in link 2, so its position depends on q1 and q2 only. The
     slot is therefore a law q2 = f(q1), and J3's axis runs along ONE scapula-fixed curve C (a cam-generated coupler
     curve). Followed through, the mechanism becomes "J3 on a curve C, then a 2R (J3, J4) to the arm".
   - Its fold window is the a3-band around C. A circle C gives the 3R's 2 min(a1, a2) window. A non-circular C can
     only shift the window per azimuth about J1.
   - The test before any metal is kinematic: does the a3-band around some C cover the workspace's J4 directions? This
     model measures it as the root share.
   - Model the circuit, not a branch. The 4-bar (J1, J2, J3, J4) crosses between the two J3-dyad branches at its dead
     points, where J1 reverses. That is not a singularity of the actuated map (J1 with J2 slaved, J3, J4). So the
     solver takes roots on both branches. The singular set is checked directly: the slaved J1 axis
     u1 + f'(q1) p2 against the plane of J3 and J4.
   - Seed the slot from the dwell. Fit a small circle by least squares to the pin positions of park4's dwell
     configuration (link 3 humerus-fixed). Then search offsets around that fit, so that every candidate slot passes
     near the configurations the free 4R preferred.
2. **The rawest material.** The posed skin itself, through the bench's signed-distance grid: every part sample is
   marched along its ray (K3), with crowns and walls checked on the hubs. The 6 fit motion clips at 10 fps are walked
   densely (K2, 2 deg slerp steps). The 160 / 360 workspace poses are used as sampled. Held-out clips are never loaded.
3. **Methods and tools.**
   - tools/concept_kit.py (K1-K7, K6 collisions with `over`, dense continuity, the honesty audit).
   - spine-parked-j2-3r.py's crown / wall check, near-touch and overhead split (lessons d, e).
   - A vectorised 1 deg root scan over q1 on both J3-dyad branches, with 40 bisections.
   - A least-squares plane fit for the slot (eigen-decomposition of the pin cloud).
   - Farm sweeps (tools/cloud_run.py sweep), then CMA-ES (tools/concept_cma.py) on the farm until the convergence
     gate passes.
   - The frozen-shape protocol on Bench(110,360) exact.
4. **What shows the number is right, other than me.**
   - The bench: K3 march, K2 dense, K6, and the kit's audit, which flags sparse sampling, missing hubs and builds that
     are not pose-local.
   - The adversarial verifier on Bench(110,360) exact with the frozen shape.
   - A red-team pose list: rest, overhead (elev >= 140), across the body and behind the back, with per-part in-band and
     the cause of every lost pose (`redteam` mode).

## Mechanism (as modelled)

- **Chain.** Scapula handler -> base -> J1 (O20, ACTIVE) -> link 1 (arc a1) -> J2 (O20, PASSIVE, slot-scheduled)
  -> link 2 (arc a2) -> J3 (O20, ACTIVE) -> link 3 (arc a3) -> J4 (O20, ACTIVE, humerus-fixed) -> K7 neck -> BOTTOM.
- **Tail and slot.** Link 2 carries a tail strap from J2 to an MR63 (3 x 6 x 2.5) roller on an M3 shoulder pin, at
  angle tr from J2 and azimuth tp from link 2.
  - The roller runs in a spherical groove plate fixed to the base: a band 14 mm wide (6.1 mm slot plus two 4 mm
    walls), 4 mm thick, at ONE radius ('cap'), along the small circle {x . n = cos beta}.
  - The cut arc is the pin's travel over the poses that close, trimmed to percentiles [pct_lo, pct_hi], plus a
    6 mm pad at each end.
- **DOF.**
  - Mobility = 4 x 3 - 4 x 2 - 1 = 3.
  - ACTIVE: J1, J3, J4. PASSIVE: J2, the pin's slide, the roller's roll, all set by the closure.
  - Passive translations: 0. Springs: 0. Sensed passives: 0. The arm orientation is a function of the three active
    readings, because q2 = f(q1).
- **Taken-pose rules on top of the kit.**
  - A root exists on the design's mode (circuit slope s3 dg/dq1).
  - Cam transmission: pa = cos(pressure angle) >= 0.25, and the cross-slot pin travel is >= 8 mm per rad of J2.
  - The actuated map is >= 5 deg from singular.
  - The pin is inside the cut arc.
  - The root nearest the dwell configuration is taken. Dense K2 drops any clip frame where that choice switches roots.

## Results (Bench(60,160) fast unless stated)

### 1. Kinematics first: the slot law has no reach problem

All numbers below are local kinematic scans: closure, cam transmission and singularity only, with no metal, skin or
continuity check.

| slot | root / taken share (ws) | overhead (elev >= 140) | slot arc |
|---|---|---|---|
| plane fit to park4's dwell pins, one J3-dyad branch (the spec's IK) | 0.12-0.36 | - | 38-280 deg |
| same, both branches (the 4-bar circuit) | 0.27-0.72 | - | 120-350 deg |
| random slots, both branches (731 configurations) | **1.00** | **1.00** | 340 deg |
| eccentric J1 groove (n = J1 tilted by ecc <= 15 deg, beta 18-27 deg) | 0.99 | 0.92 | 225 deg |

- **Branches.** Fixing the J3-dyad branch (the spec's single-branch IK) loses 60-80 % of the roots. The 4-bar
  (J1, J2, J3, J4) crosses between the two branches at its dead points, where J1 reverses. The actuated map (J1 with
  J2 slaved, J3, J4) is not singular there; the model checks that directly.
- **The plane fit.** The dwell pins of park4 (link 3 humerus-fixed) are a 2-D cloud: plane-fit RMS 1.7-15 deg. One
  slot cannot reproduce the free 4th. It can only hand each pose ONE configuration on the circuit.
- **The full-ring slot.** Any slot with a 260-350 deg cut covers almost every pose kinematically, but it is a ring
  around J1 that runs over the neck and torso. The K3 march finds no skin window there, so the one-radius plate goes
  to the 400 mm fallback and every part stacked on it follows (first coarse sweep: 320 configurations, best 126.87,
  every top configuration dishonest).
- **The eccentric J1 groove.** This version keeps the ring compact: 150-195 mm of groove 14 mm wide around hub 1, an
  MR63 roller on a tail of link 2 that lies along link 1.

### 2. Metal: where the band is lost (best coarse configuration, gap 93.63, honest)

The red team (`redteam` mode) on this configuration found:

- **Fold / K2.** reach 0.7375 and follow 0.917. Of the 47 poses not taken, 43 are lost to the fold or to K2 (no root
  of the mode, or the dwell-nearest root switching along a clip) and 4 to part collisions.
- **In-band 14 is 0.16.** By part: hub 1 0.99, neck 0.76, hub 4 0.56, hub 3 0.17, hub 2 0, slot plate 0, link 1 0,
  tail 0, link 2 0.04, link 3 0.01.
- **The groove plate rides the bunched deltoid.** The S-fixed ring around J1 (beta 27.5 deg about an axis 4.3 deg off
  J1) must clear the highest skin it passes in ANY pose. With the arm overhead, the deltoid bunches against the
  acromion under it, so the plate's one radius is 97 mm against hub 1's 52 mm. Link 1 (a full level over the plate,
  103.6), the tail (107.6, over link 1) and hub 2 all stack on top, about 30 mm above the skin in rest poses.
- **Hubs 2 and 3 roam.** Hub 2 (level 103.6) is set by the elev 165 / axial -90 workspace poses. Hub 3 (115) is set by
  comb hair and across-body poses. With the slot fixing the spare, J3 is no longer humerus-fixed (as in park4's
  dwell): it slides around the a3-cone of J4. Its flat hub therefore clears the highest skin of all those places.
- **Cam health is fine everywhere taken.** Transmission cos >= 0.94, cross-slot travel >= 21 mm/rad of J2, the
  actuated map >= 11 deg from singular, roller pin 10 mm long.

Kit note (measured): `over` did not keep the tail clear of link 1, or link 1 clear of the groove plate. K6 flagged
68 % and 30 % of the closing poses. The tail samples 14-15 mm from J2 stayed at 109.5 mm against link 1's 109-112.
The model now lifts both explicitly with ramps: the tail one full level over link 1, and link 1 one level over the
plate at the fixed distance band from J1 where it crosses the ring. This is conservative: K6 itself never missed a
collision.

### 3. Search: farm sweeps and CMA-ES

| stage | configurations | best gap (Bench(60,160) fast) | note |
|---|---|---|---|
| coarse, plane-fit slot | 320 | 126.87 (honest 152.79) | slot ring over the neck: 400 mm fallback |
| coarse, eccentric groove (before the level fixes) | 400 | 121.96 | tail / link 1 / plate collisions (kit `over` gap) |
| proxy-guided, eccentric groove | 300 | 93.63 | proxy = kinematics + hub-centre K3 levels, local, ~3 configs/s |
| CMA round 1, 4 streams | 6468 | **41.66** (reach 0.869, ib14 0.539, follow 1.0) | **refuted by the red team, see below** |
| CMA round 2 under the housing rule, 4 streams | 4116 | 50.67 (reach 0.90, follow 0.95, ib14 0.40, contact 0.010) | |

**Red team: the optimistic number (41.66).** The round-1 optimum puts the groove 14.1 deg from an axis 5.8 deg off J1.
At r 50 mm its inner edge is 0.2 mm from J1's axis plus the 3 mm slot half-width, so it cuts through J1's O20 bearing
housing (the MR117 pair's 5.5 mm bore and its wall out to 10 mm). The bench cannot see this: the groove plate and
hub 1 are the same body, and K6 exempts joint partners within 12 mm of J1.
- The model now enforces the housing. If the groove's inner edge is closer than HUB_R + 1 mm to J1's axis, measured
  at r 50 (the conservative side), the plate becomes a flange ON hub 1's crown at F1 + 12.75. Link 1, the tail and
  everything above them stack over it.
- The same configuration then scores 176.8. Round 2 re-optimised under the rule. Every stream's best still chose the
  flange: inner edge 3-6 mm, groove beta 17-28 deg, eccentricity 3-14 deg.

**Best honest configuration (round 2, stream B, gap 50.67, score 81.6).** Red team on Bench(60,160):
- **Reach and follow.** Reach 0.90, follow 0.95. Overhead (elev >= 140): workspace 4 of 12, clips 2 of 5, in-band
  0.69 on what it takes. Of the 19 poses not taken, 14 are fold / K2, 3 are part collisions and 2 are contact.
- **In-band by part.** Hub 1 1.00, neck 0.76, hub 4 0.66, groove flange 0.63, hub 3 0.15, link 3 0.09, link 2 0.03,
  link 1 0.02, hub 2 0, tail 0.
- **The limiter: hubs 2 and 3 roam.**
  - Hub 2's flat level (87.8 mm) is set by the elev 150-165 workspace poses; it sits 30+ mm above the skin
    elsewhere.
  - Hub 3's level (114 mm) is set by comb hair and the elev 165 / axial -90 poses. With the slot fixing the spare,
    J3 slides around J4's a3-cone and is no longer humerus-fixed (park4's dwell kept it humerus-fixed on 80 % of
    poses).
  - Every strap stacked on these hubs inherits their levels.
- **The pinch: the roller post is 29.8 mm long.** The tail rides over link 1, which rides over the flange on hub 1's
  crown, and the roller runs in the flange. A 30 mm cantilevered M3 post under the cam load is a stiffness and wear
  risk that the bench does not price.
- **Near-touch.** Minimum metal-skin distance 0.25 mm. Counting metal < 1 mm as contact gives 57.37.
- **Cam health.** Transmission cos >= 0.59, cross-slot pin travel >= 22 mm/rad of J2, the actuated map >= 8 deg
  from singular.
