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

