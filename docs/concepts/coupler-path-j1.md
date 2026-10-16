# coupler-path-j1: J2 carried along a spherical four-bar coupler curve (fold lever, no spring, no sensor)

Model: `docs/concepts/models/coupler-path-j1.py`. Sweeps: `docs/concepts/sweeps/coupler-path-j1.json`. Row:
`docs/concepts/rows/coupler-path-j1.json`.

## Depth answers (written before the first measurement)

**(1) What a top mechanism designer would do that the spec does not ask for.** The spec (written before the fold law)
synthesises the coupler curve for constant J2 skin relief. The fold law says what matters more: a 3R's J2 runs on the
circle angle(u1, p2) = a1, so the pose set it can close is the annulus th in [|a1 - a2| + m, a1 + a2 - m] (42-102 deg at
the pin knee), against the 26-140 deg the workspace needs. A coupler curve is any closed curve the spherical four-bar
can draw. A pose closes iff the circle C(p3, a2) crosses the curve TRANSVERSALLY: the chain is singular exactly where
the curve is tangent to that circle, because the pole of link 1, p2 and p3 are then coplanar. So a designer would:
(a) state the generalised fold rule as a crossing angle and calibrate it on the leader's own circle (the same m = 10 /
m = 5 count), so that a coupler and a circle are judged by one rule; (b) synthesise the curve for COVERAGE of the
workspace p3 set and J2 skin relief together, on the leader's own chain (the pin knee: its J1 and J2 are GH rays, so
the knee closure is unchanged when link 1 moves as a coupler); (c) treat the four-bar's own dead points (transmission
angle at B1 within [25, 155]) and the crank's single connected range as hard limits; (d) price the extra metal (base
hubs A0 and B0, crank, rocker, pins A1 and B1) only after the kinematics and the J2 relief show a gain worth paying for.

**(2) Rawest material.** The posed J3 axis of every bench pose in the scapula frame (Q_i u3, from the pose file
`pipeline/conformal/band_poses_wsf.b64` via `concept_bench._poses_all`, 360 + 110 poses of Bench(110,360)). The posed
skin itself, marched along the J2 axis of each taken pose (K3 march on the Bench(60,160) grid cache), not a digested
relief map. The leader's frozen verified parameters (`docs/concepts/verify/skin-normal-3r-pin-knee_big_frozen.json`).

**(3) Methods and tools.** Closed-form spherical four-bar (two-circle closure for B1, coupler frame at A1).
Root finding of g(t) = angle(p2(t), p3) - a2 on a 0.5-deg crank grid, then bisection to < 1e-6 deg. Crossing-angle
conditioning. CMA-ES (cma 4.5) on the farm for the synthesis. The pin-knee VModel (every verifier check) for the bench
number, with the four-bar replacing J1's rotation of link 1.

**(4) What, other than me, shows the number is right.** The bench (tools/concept_bench.py) on Bench(60,160) fast and
the frozen shape on Bench(110,360) exact. The calibration control: the leader's circle written as a degenerate coupler
(kr = 0, A0 = u1, alpha = a1) must reproduce the leader's own numbers through this code. The verifier harness
`docs/concepts/verify/skin-normal-3r-pin-knee.py`. A red-team pose list: rest, overhead (elevation >= 140), across the
body, behind the back, and the poses where the four-bar comes nearest its dead point.

## Mechanism (as modelled)

```
scapula base ==A0 (O20, ACTIVE crank)== crank ==A1 (pin)== coupler = link 1 ==J2 (O20, ACTIVE)== link 2 ==J3 (O20, ACTIVE)== member 3 -a- knee -b- arm pad
             ==B0 (pin)============== rocker ==B1 (pin)==/
```

All four-bar axes pass through GH (a spherical four-bar), so link 1 still rotates about GH and the pin knee's closure
theorem (J1, J2 on GH rays -> member 3 drifts in hub 3's plane) holds unchanged. DOF: 3 active (crank, J2, J3); the
rocker and the pins A1 / B1 are set by the loop (mobility 1 for the four-bar, no undetermined coordinate); pins a / b of
the knee as in the leader. 0 passive translations; 5 passive rotations (B0, A1, B1, a, b).

Changes from the spec, measured or reasoned:
* **Fold rule.** The spec's "within 10 deg of a fold" (crossing angle) does not reproduce the bench's 3R rule. I use the
  OSCULATING-CIRCLE rule: at the root, the kit's 3R rule th in [|a1 - a2| + m, min(a1 + a2, 360 - a1 - a2) - m] with u1
  replaced by the centre of the coupler curve's osculating circle and a1 by its radius. It is exact for a circle, and
  it is what makes the control below reproduce the leader to the last digit. (A plain crossing-angle threshold
  calibrated to the same count, X = 40 deg for m = 10 / X = 25 for m = 5, takes a different pose set: 24.58 vs 20.63.)
* **Body that carries J2.** With kr = 0 (J2 on the A1 axis) link 1 is the CRANK (a rotation about A0); with kr > 0 it is
  the coupler, rotation Rc(t) = E(t) E(t_h)^T.
* **J2's home** is the root of angle(p2(t), u3) = a2c at Q = I (the leader's home convention), so a2c is free.
* **Base seats** are searched relative to the leader's J1 seat (A0 = u1 moved dA at azimuth psiA).

## The control (calibration)

The leader's own circle written as a degenerate four-bar (`{"circle": 1}`: A0 = u1, alpha = a1, kr = 0) through this
code, Bench(60,160) fast, m = 10: **gap 20.63, reach 0.6937, follow 1.0, in-band 0.9033 / 0.5323, contact 0, fold 46,
slide 3** - identical on every metric to `skin-normal-3r-pin-knee.py check` with the verified frozen parameters.

## Stage 1 - the lead's question, by IK only (Bench(110,360), 360 workspace poses, m = 10, osculating rule)

Does a coupler curve cover th 26-140 better than the leader's 42-102 circle? `kin` / `kopt` modes; CMA-ES streams on the
farm (8 per family, 160-200 generations x 14). Zones are the leader's own: folded th < 42.2 (57 poses), window (227),
stretched th > 102.4 (76).

| curve (J3 seat = the leader's) | ws | overhead | across | behind | leader-folded zone | leader-stretched zone |
|---|---|---|---|---|---|---|
| leader circle (a1 40.1, a2 72.3) | 0.631 | 0.393 | 0.294 | 0.76 | 0.00 | 0.00 |
| best CIRCLE, no skin term (A0 23 deg off u1, a1 75, a2 75.5) | **0.978** | 1.00 | 0.94 | 1.00 | 0.97 | 0.95 |
| best COUPLER, no skin term (kr 33, a2 79.6) | 0.967 | 1.00 | 0.85 | 1.00 | 0.97 | 0.87 |
| best circle with the J2-relief proxy (a1 67.7, a2 84) | 0.906 | 1.00 | 0.88 | 1.00 | 0.56 | 0.91 |
| best coupler with the J2-relief proxy (kr >= 10) | 0.903 | 1.00 | 0.88 | 1.00 | 0.54 | 0.91 |

**Answer: yes, a coupler covers the workspace (0.97 of the 360 poses, overhead 1.00) - and so does a plain circle.**
Kinematically the window is set by the ARCS (a1 + a2 up to ~150 deg, |a1 - a2| small), not by the curve's shape: the
best circle (0.978) beats the best coupler (0.967). With the J2 relief proxy (the K3 march along J2's axis in every
taken Bench(60,160) pose) the coupler and the circle tie to the third decimal (proxy 5.29 both). The coupler's 8 extra
parameters buy nothing a re-seated, re-arced J1 does not.

Per pose (Bench(60,160), the 46 poses the leader loses to the fold): **44 of 46 (0.957) have SOME J2 axis on the
circle C(p3, a2) whose ray clears the skin below the leader's hub-2 level (60.9 mm)** (median lowest requirement 53 mm;
taken poses 42 mm). The stretched ones want that J2 73.5 deg from the leader's J1 seat (median), the folded ones 53.7.
So the J2 skin is not a per-pose barrier; what stops a J1 mechanism is that one rigid hub level and one 1-D path must
serve every pose, and the links that reach those J2 positions.
