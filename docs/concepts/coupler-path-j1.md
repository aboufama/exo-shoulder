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
