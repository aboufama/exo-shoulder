# remote-pole-fourbar-j2-3r - remote-pole spherical four-bar J2 at the cap pole

Round 102 (J2 track jump), lens 1 (virtual J2), PICK 1. Model: `docs/concepts/models/remote-pole-fourbar-j2-3r.py`.
Sweep: `docs/concepts/sweeps/remote-pole-fourbar-j2-3r.json`. Row: `docs/concepts/rows/remote-pole-fourbar-j2-3r.json`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask.** Treat the binder as a precision-position
   problem, not a sampling one: the judge drew 90000 random layouts and proxied 50; a designer would instead run a
   direct MINIMAX search of the worst skin level of the coupler pins, crank B and the coupler at the binder poses
   (W >= 85 and the binder poses inside the window as constraints), and then ask the next question the step-0 test
   cannot: where does the binder go when you push it off those four poses? A spherical four-bar's coupler pins ride
   circles about J3 in the humerus frame; their azimuth is set by one scalar (theta), so a layout that cools the
   overhead binders can heat the REST poses. Measure the requirement of each pin over every taken pose (median,
   p90, max), not only at four. Also price the layering the proxy ignores (cranks swinging over the J1 stack).
2. **Rawest material.** The posed skin itself through the K3 march (`K.requirement` on the fast grid cache of
   Bench(60,160), the exact libigl path for Bench(110,360)); the bench poses' J1-J3 angle th for the arm's real
   J3 axis (th110.npy = the planner's measurement); the four binder poses (-75,60,+60), (0,150,0), (30,150,0),
   (0,105,0) as the bench poses nearest them, read per pose, per pin. Not the proxy's weighted in-band share.
3. **Methods and tools.** Spherical four-bar closed-form closure (virtual-pole-4bar-j2.py `FourBar`, kit
   `K.closure`), the longest monotone th run with both transmission angles in [30, 150] (fold rule read in th, 5 deg
   margin), minimax (1+1)-ES with restarts on the binder objective (20 ms per layout), the honest kit evaluation
   (`K.evaluate`: K3 march, K2 dense continuity, K6 collisions, audit) inside a CMA-ES on the 1 mm near-touch gap,
   the numeric 3x3 rotation Jacobian for mobility, the frozen exact Bench(110,360) wear of the best shape.
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py) and the kit audit; the
   plain cap-pole O20 3R through the SAME kit and bench as the control (63.18 fast, cruciate-knuckle-3r's control);
   the frozen exact Bench(110,360) number; the per-pose binder table and the red-team pose list below; the
   adversarial verifier's harness when it re-runs the file.

## Model (what was built, and where the spec was corrected)

`docs/concepts/models/remote-pole-fourbar-j2-3r.py` (~150 lines on tools/concept_kit.py and the shared FourBar of
virtual-pole-4bar-j2.py): J1 O20 at the cap pole bvec(43.15, 59.93), J3 O20 humerus-fixed at wdir(92.03, -9.03); link 1
carries the ground pins A0 (ACTIVE, the J2 coordinate) and B0; cranks A and B; the coupler carries A1, B1 and J3; K7
neck to BOTTOM. Lens 1's near-isogram vector [th0, dA0, pA0, dA1, pA1, g, gam, eps, tw] (rp4 par.py geom) reproduces
lens 1's kinematics exactly (s1: window [31.9, 100.8] vs lens 1's [32.1, 100.8]; reach_kin 0.678). Fold rule in th:
longest monotone run of th(theta) with both transmissions in [30, 150], window = run - 5 deg each end (the stop is a
dowel on crank A's own angle). Six O20 v5 stacks, 3 mm x 12 Ti straps, kit K2 dense / K3 march / K6 / audit, honest.

Corrections to the spec, measured:
- **Cranks over the J1 stack.** The spec layered both cranks lowest. Each crank swings ~70-100 deg about its ground
  pin, 22 deg from J1, and passes over J1's 12.25 mm stack: hubJ1 vs crank A / crank B rejected 56 / 78 % of s1's
  closing poses (collide 1.00). The model lifts both cranks over hubJ1 (+1 mm), the honest layering; the remaining
  K6 rejections (crank B vs link 1, crank A vs crank B on tight layouts) are left to K6.
- **The step-0 binder test is necessary, not sufficient** (next section).

## Step 0: the binder test, as a minimax search (not random sampling)

Lead note: close the lens if no layout with W >= 85 keeps both coupler pins, crank B and the coupler <= 75 mm at
(-75,60,+60), (0,150,0), (30,150,0), (0,105,0) (judge: 90000 random cell / relaxed layouts, 50 proxied: none).
Instead of sampling, a (1+1)-ES with restarts MINIMISED the worst K3 skin level of A1, B1, crank B and the coupler at
those four bench poses, subject to W >= 85, all four poses inside the window, pin separations >= 22, crossing >= 8,
transmission >= 30 (rpf/bopt.py, 20 ms per layout, ~23000 layouts over the near-isogram and the general 9-pin box,
8 min x 2 niced processes).

| search | feasible restarts | best worst-binder level (A1, B1, crank B, coupler) | worst level of EVERY member at the binders |
|---|---|---|---|
| near-isogram box (lens 1's vector) | 47 | **67 mm** | **67 mm** (x = [30.2, 35.1, 167.1, 40.0, 94.3, 22.4, -84.0, -1.6, 7.6]: W 101.8, [28.1, 129.8]) |
| general 9-pin box | 49 | 62 mm | 112 mm (crank A / A0 inherit the binder: 133-202 mm) |

So **step 0 PASSES as written**: the judge's 90000 random layouts missed a cell a directed search finds in ~2 min;
the near-isogram layout above holds every pin and strap at 43-68 mm at all four binder poses, with W 101.8 and
kinematic reach 302/360 (0.839) on Bench(110,360) ws, overhead 15/28 (the plain cap 3R: 281/360).

**But the binder moves.** Read over every taken Bench(60,160) pose (pin centre rays, K3 march) that same layout has
J1 49-52, A0 52-68, B0 48-88, J3 50-67 mm, while **A1 reads p50 74 / p90 89 / max 400 (escapes the march at (15,150,0))
and B1 p50 94 / p90 126 / max 217 mm** - the coupler pins are cool at the four named binders and hot at rest-to-mid
elevations and across the body with strong internal rotation ((105,45,-165), (75,30,-135), (120,45,-165)). Through the
kit it scores 86.41 fast but NOT honest (crank A / link 1 / coupler fitted so far off the body that their samples are
8-11 mm apart: every moving member 0 % in band). The coupler pins ride circles about the humerus-fixed J3 axis at a
fixed arc; their azimuth about J3 is one function of theta, and J3 must also absorb the arm's axial rotation, so a
law that cools four poses heats others. The step-0 table is therefore a necessary test only; the gate-0 number below
is the decision.

## Step 0 generalised: the FULL-POSE binder test (new)

Same minimax, but over EVERY taken Bench(60,160) pose: minimise the worst K3 level (max over the taken poses) of the
pins A0, B0, A1, B1 and the crank / coupler / link-1 strap centre lines, subject to W >= 85 and kinematic reach
(Bench(110,360) ws) >= 0.75 (rpf/fbopt.py, ~0.3 s per layout, 1938 layouts, 8 min, seeds = lens 1's ES optima and
the step-0 layout).

**Best: x = [86.43, 23.97, -93.12, 72.58, -37.48, 22.24, -99.15, -0.74, 17.45], W 91.8, kinematic reach 0.794, every
four-bar member <= 76 mm over every taken pose** (max A0 58, B0 69, A1 76, B1 74, crank A 68, crank B 71, coupler 76,
link 1 66; p90 56-66). Four of the top five restarts land in the same cell (77-86 mm). So on centre lines the binder
IS escapable at all poses, against the judge's "expected to die at step 0": the cell is a COMPACT cluster - all four
pins within ~22-30 deg of J1 on the acromion top (dA0 20-29, dA1 73-80 from J3 with th0 85-90, i.e. A1 / B1 sit back
near J1), so the polycentric J2 is built where the skin is lowest and the coupler is a long arm (~73-80 deg) from the
cluster to J3. That is new knowledge for the virtual-J2 track: the cool place for a four-bar J2 at the cap pole is
next to J1, not near the J2 ray.

**Through the kit it dies on layering, not skin: 274.37** (collide 0.9948). K6 rejects 99.5 % of closing poses on crank A
vs link 1 next to the shared A0 stack (~17 mm from the A0 axis, both at ~87 mm): the cluster puts link 1, both cranks
and the coupler's root over the same ~25 deg patch, so four bodies must stack at one spot, and the O20 discs (hub levels
85-96 mm vs the 58-76 mm of their centre rays) and the coupler's lift over three stacks (152 mm) follow. The honest kit
CMA from the six best cluster layouts (sigma 0.06) has not yet found a cluster neighbour that both closes K6 and stays in
band (best 112.16, numbers below).

Kit note (measured, reported for the kit owner, not used for any number here): part of that K6 rejection is the kit's
single-pass `over` lift. `fit_profiles` runs ramps -> `_over` -> the climb limit once; `_over` judges "near" at the
member's pre-climb radius, the climb then raises link 1 into crank A's layer: at the hit samples link 1 sits at 87.5 mm
over crank A's 87.0 (top 90.0), and `K._over` re-run on the FINAL profile asks for 91.0 mm there. Orienting the pair
upper-first in K6 changes nothing (0.9948 both ways), so it is the pass order, not the pair orientation. A fixed-point
lift (ramps / over / climb until nothing rises) is a kit MEASUREMENT change that would touch every model using `over`;
this screen keeps the kit as it is. Side experiment (rpf/fixpt.py, the kit's own functions with the lift iterated to a
fixed point, not used for any claim): the cluster layout goes 274.37 -> **133.04** (collide 0.995 -> 0.272, reach 0.638,
follow 0.60, ib14 0.189), the best honest iso config is unchanged (90.59 both ways). So the kit quirk is real and worth
fixing, but it does not rescue the cluster: with a correct lift it is still 70 gap points behind the plain cap 3R
(63.18): four bodies stacked on one 25-deg patch put the coupler over three O20 stacks, in band 0.19.

## Gate 0: the honest kit on Bench(60,160) fast (the decision)

Kit checks on (K3 march, K2 dense continuity, K6 collisions, audit); objective = the 1 mm near-touch gap; 389 kit
evaluations (245 honest; the rest are non-assembling layouts at 275 or audit-flagged members fitted off the body):
lens 1's seeds and ES optima, the step-0 and full-pose minimax layouts, 13 proxy-ranked random layouts (2191 kin-valid
draws ranked by lens 1's proxy), and CMA-ES restarts (sigma 0.12 / 0.25 / 0.06 / 0.05 / 0.02) from the best.
Local only (farm closed), 2 niced processes, OMP_NUM_THREADS=1. Sweep: docs/concepts/sweeps/remote-pole-fourbar-j2-3r.json.

| configuration | gap fast | score | reach | follow | ib14 | contact | note |
|---|---|---|---|---|---|---|---|
| plain cap-pole O20 3R, same kit (control, cruciate-knuckle-3r) | 63.18 | 77.03 | 0.794 | | 0.375 | | the bar this lens must beat first |
| lens 1 s1 (proxy 33.67) | 245.81 | 10.6 | 0.05 | 0.017 | 0.225 | 0 | collide 0.945 |
| lens 1 s2 (proxy 35.72) | 170.09 | 38.2 | 0.338 | 0.483 | 0.228 | 0 | collide 0.561 |
| lens 1 s3 (proxy 34.25) | 275 | 0 | - | - | - | - | no valid window at the pin separations |
| step-0 minimax layout | 86.41 | - | 0.85 | | 0.163 | 0 | NOT honest: members fitted off the body (8-11 mm sample spacing) |
| full-pose minimax cluster | 274.37 | 0.2 | 0.006 | 0 | 0 | 0 | collide 0.995 (crank A vs link 1); 133.04 with a fixed-point lift (side experiment) |
| **best honest, sweep k298** | **90.11** | **67.23** | 0.769 | 0.883 | 0.197 | 0 | ib10 0.105, near-touch gap 90.11, min metal 2.0 mm |

Best (iso [th0, dA0, pA0, dA1, pA1, g, gam, eps, tw] = [101.107, 36.279, 96.125, 61.148, 31.223, 32.812, 28.934,
-7.652, 11.424]): th window [19.0, 110.0] (W 91.0), min th margin 6.909 deg over the taken poses (>= 5), min
transmission 41.1 deg on the taken poses (30.2 at the run ends behind the stops), pin separations >= 27.0 deg, closure
residual 0.0003 deg, collide 0.088, 0 flips, mass 250.2 g (six O20 stacks). Kinematic window on Bench(110,360): ws
286/360 (0.794; folded 14, stretched 60), clips 1.000, overhead (elev >= 140) 16/28 - so the four-bar's window IS wider
than the plain cap 3R's 281/360 [15.1, 105.5]: the reach lever exists, the metal is what fails. Taken overhead on
Bench(60,160): 4/12.

Fitted levels (mm) and per-member in band: J1 55 (1.00), A0 90 (0.00), B0 100 (0.00), **A1 127 (0.00)**, B1 86 (0.01),
J3 70 (0.66), **crank A 127 (0.00)**, crank B 100 (0.18), link 1 104 (0.00), **coupler 130 (0.05)**, neck 101 (0.74).
The binding member is **A1 / crank A / the coupler** (the coupler pin farther from J3 and the strap that carries it):
A1's centre ray reads p50 58 / p90 71 / max 113 mm, the max at the overhead binder (30,150,-60) and 101-105 mm at
(0,150,0) / (30,150,0) / (0,105,0) - lens 1's binder exactly; one pose sets a rigid O20 disc's level for all poses.

**Convergence gate** (honest gap, score points, 389 tries in time order): gain over the 2nd half 0.08, over the last
third 0.08, top-5 distinct configurations 90.11 / 90.32 / 90.59 / 92.28 / 97.57 = spread 2.71 -> **passes**.

## Red team (own best config)

- **The optimistic number is the best itself.** Ten perturbations of the 90.59 config by ~1-2 deg per pin coordinate
  (sweep src cma7:s0..s9) scored 90.32, 105.86, 121.72, 128.84, 129.99, 158.32, 174.14, 180.96, 212.04, 273.75: the
  optimum is a narrow spike (one rigid O20 disc's level is set by its single worst pose, and K6 is binary). A machined
  linkage with ~1 deg pin-position tolerance does not hold 90.
- **The proxy is optimistic by 130-240 points here.** Lens 1's proxy (K3 on hub rays and strap centre lines, no
  layering, no K6) put s1-s3 at 33.67-35.72; the kit puts them at 170-275. The centre-ray full-pose minimax put every
  member <= 76 mm; the kit fits the same layout at 85-152 mm (O20 discs, the coupler's lift over three stacks).
- **The pose that jams.** The run ends are toggles / folds: the rotation Jacobian's sigma_min / sigma_max falls to 0.005
  at the run ends (measured on the 90.59 neighbour) and stays >= 0.111 (median 0.455) inside the window; the 5-deg th stop on crank A's own angle keeps
  every taken pose off them (min th margin 6.909), transmission >= 41.1 on taken poses. An unpowered MVP1 would feel
  the stop near th 19 / 110 (arm stretched far across / folded overhead).
- **The point that pinches.** Min metal-skin distance over the taken poses 2.0 mm (no near-touch pose); the risk is
  the other way: metal 30-75 mm off the skin at most poses (in band 0.197).
- **K6 by construction is not a fixed point** (Kit note above): it costs the compact cluster layouts, not the best.

## Verdict

**DEAD at gate 0.** Best honest 90.11 fast on Bench(60,160) (score 67.23), 27 points WORSE than the plain cap-pole O20
3R through the same kit (63.18) and 72.6 points over the 17.5 bar; converged (gate above). No frozen exact
Bench(110,360) wear (the fast number is 5x the bar, as cruciate-knuckle-3r). What dies is the metal, not the
kinematics: the open four-bar's window reaches 286/360 on Bench(110,360) (W 91, overhead 16/28 kinematically), but its
six O20 stacks and layered straps sit 86-130 mm out, because a rigid O20 disc takes its level from its single worst
pose and the coupler-side pin always meets the J2 zone at one of the binder poses.

What this lens taught, measured:
1. The step-0 binder test as written (four poses) is passed by a directed minimax search (67 mm, W 101.8) that 90000
   random layouts missed - and is useless as a filter: that layout's coupler pins go to 94-126 mm (p50-p90) at rest /
   across-body poses and the kit rejects it as dishonest.
2. A FULL-POSE minimax on centre rays finds the cool cell: all four pins clustered within ~25-30 deg of J1 on the
   acromion top (<= 76 mm on every taken pose, W 91.8, reach_kin 0.794). It dies on stacking: four bodies on one
   ~25-deg patch (kit 274.37; 133.04 even with a fixed-point lift).
3. So a four-bar J2 at the cap pole has two cells and each has its own wall: spread out, the coupler pin meets the J2
   zone (A1 113 mm); clustered at J1, the layers pile up. The plain 3R's single O20 J2 is cheaper than either, so the
   J3 closer's ceiling statement for the cap seats stands with this lens closed.

Mechanism: 3 active (J1, A0, J3) + 3 passive pins (B0, A1, B1), 0 passive translations, 1 closed loop, complexity 16.0
(tools/simplicity.py v2.2: 3 passive rotations, 1 loop, 2 extra bodies, 3 extra joints, parts).

Files: model docs/concepts/models/remote-pole-fourbar-j2-3r.py (`check` / `jac` modes); sweep
docs/concepts/sweeps/remote-pole-fourbar-j2-3r.json; row docs/concepts/rows/remote-pole-fourbar-j2-3r.json; preview
docs/concepts/viz/concepts/remote-pole-fourbar-j2-3r.js (best config). Scratch scripts (not in the repo): binder
minimax bopt.py, full-pose minimax fbopt.py, kit search rs.py, kit side experiments asym.py / fixpt.py / k6why.py.
