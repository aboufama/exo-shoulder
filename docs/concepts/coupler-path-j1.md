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
conditioning. CMA-ES on the farm: cma 4.5 for the stage-1 proxy, tools/concept_cma.py for the bench. The pin-knee VModel (every verifier check) for the bench
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
  calibrated to the same count - X = 40 deg for m = 10, X = 25 for m = 5 on the 360 poses - takes a different pose set:
  with it and the coupler as link 1 the control read 24.58, with the osculating rule 21.47, with both fixed 20.63.)
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

## Stage 2 - the bench (pin-knee VModel, every verifier check; Bench(60,160) fast, m = 10)

Full-bench CMA-ES on the farm (`tools/concept_cma.py`, 8 x 8 per generation, every configuration in
`sweeps/coupler-path-j1.json` with its stream label). Free: the four-bar (dA, psiA, alpha, dAB, psiB, beta, c, kr, kg,
a2c), J3's seat (wd, wa, b3) and the knee (lE, lc, phiE, phib). BOUND = stage 2a: the crank, the rocker and the pins
B0 / A1 / B1 are not yet metal (optimistic on in-band, contact and part clearance).

| stream | start | evals | best (bound) | reach | follow | in-band 14 / 10 | contact | A0-B0 apart | gate (2nd half / last third / top-5, score pts) |
|---|---|---|---|---|---|---|---|---|---|
| circB (control: re-seated circle, kr = 0) | the proxy's best circle (A0 17 deg off, a1 54) | 1161 | 23.73 | 0.669 | 1.0 | 0.901 / 0.561 | 0.006 | - | 0.44 / 0.23 / 0.00 |
| cplC (coupler, s4 +1) | leader-equivalent, kr 5 | 1865 | 21.26 | 0.700 | 1.0 | 0.887 / 0.477 | 0 | 2.2 mm | 0.41 / 0.18 / 0.05 |
| **cplE** (coupler, s4 -1) | leader-equivalent, kr 5 | 2185 | **20.58** | 0.700 | 0.967 | 0.900 / 0.539 | 0.006 | 0.9 mm | 0.68 / 0.12 / 0.00 |
| cplD (coupler, s4 +1) | the proxy's kr >= 30 best | 1273 | 25.17 | 0.663 | 0.95 | 0.898 / 0.559 | 0.012 | 4.1 mm | 0.00 / 0.00 / 0.01 |
| leader (control, this code) | - | - | 20.63 | 0.694 | 1.0 | 0.903 / 0.532 | 0 | - | - |

Every stream passed the convergence gate (sigma collapsed; gain < 1 score point over the second half, < 0.5 over the last
third, top-5 within 3). **Every coupler stream drove the rocker pivot B0 ONTO the crank pivot A0 (0.9-4.1 mm apart;
two real hubs need >= 17 mm: O20 + O12 + 1).** With B0 = A0 the loop A0-A1-B1 is a rigid triangle, the coupler turns
rigidly with the crank, and link 1 is a plain revolute about A0: the search on the honest bench dissolved the four-bar
into the leader's J1 (effective a1 41.7 vs 40.1, kr 5.9 deg). The best bound, 20.58, ties the leader (20.63) within
one pose, and the re-seated circle that the J2-relief proxy liked (64.05 at the proxy pick) converges back to the
leader's seats (A0 3 deg off u1, a1 44.9) at 23.73.

Why the proxy's kinematic gain dies on the bench (measured at the proxy picks, `local` stage in the sweep): the fold
loss drops from 46 to 6-24 poses, but J2's hub has to be fitted at 80-95 mm instead of 61 (its ray passes over the
raised deltoid / trapezius in poses the circle never used), 18-40 poses become skin contacts, the knee runs out of range
in 8-41 more (slide) and in-band falls to 0.53-0.59.

## Pricing the four-bar's metal (the lead's second question)

`price4bar`: on the bound's fitted shape, add the crank strap A0 -> A1(t) on top of the A0 hub, the B0 pin boss (O12,
MR63ZZ pair / iglidur stack 6 mm), the rocker strap B0 -> B1(t) on it, the A1 / B1 pin bosses, and raise link 1 (the
coupler) by plate + pin stack over the crank at its base end (tapering to 0 at J2). Each new part's level is REFIT (K3
march, max over the taken poses), so it adds no contact, only metal out of band.

| configuration | bound | priced | in-band 14 bound -> priced | levels (mm: A0 hub face, B0, crank, rocker) |
|---|---|---|---|---|
| near-circle coupler (kr 3, default B side) | 48.36 | 67.43 | 0.893 -> 0.702 | 49.9, 54.0, 62.2, 67.0 |
| cplE (best bound) | 20.58 | 34.77 | 0.900 -> 0.758 | 51.1, 51.1, 63.3, 57.1 |
| cplC | 21.26 | 53.62 | 0.887 -> 0.564 | 49.8, 49.8, 62.1, 107.0 |
| cplD | 25.17 | 61.60 | 0.898 -> 0.579 | 51.7, 51.7, 71.0, 80.0 |

**The four-bar's own metal costs 14-36 gap points** (the rocker rides over the moving deltoid / trapezius edge, and link
1 must climb a pin stack over the crank). Searching the PRICED objective directly (CMA on the farm, 2 streams,
1329 + 1257 evaluations, both converged: gate 0.35 / 0.35 / 0.24 and 0.25 / 0.12 / 0.03) gives **30.52** (prcG: reach
0.675, follow 0.967, in-band 0.826 / 0.454, contact 0.006) and 33.28 (prcF) - and again B0 collapses onto A0 (3.3-3.7 deg,
~3 mm apart, where two hubs need >= 17 mm). No configuration with real, separate base hubs comes near the leader: the best
bound with A0-B0 >= 19.5 deg (hubs that fit) is 28.42 BEFORE its metal is priced (sweep k3257; its transmission angle
dips to 26.3 deg, 1.3 deg from the toggle limit).

## Frozen shape on the verification bench (lesson c)

The best bound (cplE, B0 0.9 mm from A0, i.e. a rigid crank) fitted on Bench(60,160) fast and worn FROZEN on
Bench(110,360) EXACT (farm, m = 10): **26.02** (score 90.54; reach 0.650, follow 0.973, in-band 0.899 / 0.538, contact
0.009; fold 117, slide 7, parts 2, contact 3). Near-touch: min metal 0.09 mm over taken poses; gap 34.77 if metal < 1 mm
counts as contact, 57.44 if < 2 mm. Overhead (elevation >= 140): reach 6 of 28 (0.214), in-band 0.872. This is NOT a
four-bar result: with B0 on A0 the loop is rigid, and its plain-3R equivalent (J1 = A0, a1 41.70, a2 73.26, the same
J3 seat and knee; sweep entry "plain-3R equivalent") scores 21.22 fast against the bound's 20.58. It is a re-seat of the
pin knee (A0 2.5 deg off the leader's J1, a2 73.3, J3 wd 66.6 / wa -9.5 / b3 0.30, knee lE 50.3 / lc 17.8 / phiE -4.2 /
phib -66.5) in the territory the pin-knee polish already holds (H1 verified 26.45 at m = 10). It goes to the polish as a
seed, not to the leaderboard as a coupler.

Frozen exact through this code, Bench(110,360), m = 10 (farm): the leader control **30.35** (= the verified k4598,
to the digit: the frozen path is right) and the **plain-3R equivalent 25.87 (score 90.59)**: reach 0.650, follow 0.964,
in-band 0.902 / 0.544, contact 0.009 - 4.5 points better than k4598 under the same protocol, 0.6 better than the polish's
H1 (26.45, m = 10), with zero extra parts (complexity 21.5, the pin knee's). SELF-MEASURED, not verified. In the pin-knee
model's own parameters (reproduces 21.22 fast exactly through `skin-normal-3r-pin-knee.py`):

    {"lE": 50.2799, "lc": 17.8289, "phiE": -4.2338, "phib": -66.4684, "stk": 5.0, "ang_min": 30.0, "az1": 99.7847, "el1": 65.0641, "az2": 23.7454, "el2": 48.5131, "wd": 66.6237, "wa": -9.5334, "b3": 0.3041, "neck": 13.0}

This is the coupler search's one useful by-product: a full-bench CMA that was free to move J1, the arcs, J3's seat and
the knee together found a pin-knee basin with J1 2.5 deg off the leader's, a2 73.3, J3 10 deg nearer the arm axis
(wd 66.6 vs 76.5) and a longer E strap / shorter knee link (lE 50.3 / lc 17.8 vs 42.1 / 24.9).

## Red team (Bench(60,160) fast, m = 10)

* **The pose that jams.** Overhead: the best bound takes 1 of 12 workspace poses at elevation >= 140 (9 fold, 2 knee
  range), the best buildable four-bar (k3257) 0 of 12. The coupler did not buy the overhead it was meant to buy.
* **The point that pinches.** Lowest metal 0.25 mm (cplE: plane 120 / elev 30 / axial -135, across the body), 0.21 mm
  (k3257: the fit clip at elevation 149). Gap with metal < 1 mm as contact: 30.51 (cplE), 32.35 (k3257).
* **The number that is optimistic.** The bound leaves the crank, rocker and three pins out; pricing them costs 14-36 gap
  points (table above), and the bound optimum is not buildable (B0 inside A0's hub). The four-bar's toggle: the best
  buildable layout's transmission angle reaches 26.3 deg (limit 25) inside the taken set.
* **The proxy was optimistic too.** The J2-relief proxy (centre ray, Bench(60,160)) predicted a hub-2 level of 63 mm
  at its best re-seated circle; the bench fitted 80.7 mm (disc edges, poses the circle never used, the knee and links).

## Verdict

**Dead (measured, converged).** The coupler-path J1 is a fold lever only on paper: by IK alone a coupler covers 0.967 of
the 360 big-bench poses (overhead 1.00), but a plain circle with wider arcs covers 0.978 - the window is set by the
arcs, not by the curve. On the full bench every CMA stream (6 streams, 8 9xx evaluations in all, every gate passed)
dissolves the four-bar into a rigid crank (B0 onto A0), i.e. the leader's plain J1; the best bound ties the leader
(20.58 vs 20.63 fast), and the honest priced optimum is 30.52 fast (+10 over the leader) with hubs that overlap.
The limiter is not the J2 path but everything a wider path drags along: J2's hub level (61 -> 80-95 mm), the knee's
range, the links over the raised deltoid / trapezius, and the four-bar's own metal (rocker over the moving shoulder edge,
link 1 one pin stack higher).

## New knowledge (beyond this morphology)

1. **The osculating-circle fold rule** generalises the kit's 3R margin to any J2 path (coupler curve, cam, rocker): the
   chain is singular exactly where the path is tangent to the circle C(p3, a2); the margin is the 3R rule with u1 ->
   the osculating centre, a1 -> the osculating radius. It reproduces the 3R exactly (the control).
2. **The fold window is an arc property, not a path property.** Over 360 big-bench poses: best circle 0.978, best
   coupler 0.967 (no skin); with a J2-relief term they tie (0.906 / 0.903).
3. **Per pose, the J2 skin is not the barrier**: 44 of the 46 poses the leader loses to the fold have a J2 axis on
   C(p3, a2) whose ray clears the skin below the leader's hub-2 level (median 53 mm vs 61). What fails is ONE rigid
   hub level + ONE path + the links serving every pose. A lever that changes a1 per pose must also keep J2's HEIGHT
   - i.e. the next lever is in the radial direction (or a2), not in the path's shape.
4. **A four-bar base on this chain costs 14-36 points of in-band** for its own metal, so any closed-loop J1 (rocker,
   relay, coupler) has to pay that back in reach before it pays at all.

## Audit (2026-10-16, independent auditor)

Verdict: **the death stands** (refuted = false). The four-bar adds nothing over a plain crank; every number it reaches is the
pin-knee chain it carries.

- **Convergence gate**, recomputed from docs/concepts/sweeps/coupler-path-j1.json per stream (score points: gain over the
  2nd half / last third / top-5 spread): circB 0.44/0.23/0.00, cplC 0.41/0.18/0.05, cplE 0.68/0.12/0.00,
  cplD 0.00/0.00/0.01, prcF 0.35/0.35/0.24, prcG 0.25/0.12/0.03. All converged.
- **Model bug, lenient side:** `price4bar` has no A0-B0 hub-overlap check, so the priced optimum (prcG 30.52 fast) sits with B0
  ~3 mm from A0, where two O20 hubs need ~17 mm. The honest priced number is worse than 30.52. No constrained
  (A0-B0 >= 19.5 deg) priced stream was run. The 189 buildable samples score at best 28.42 bound and 45.73 priced. Every free
  stream drives B0 onto A0, so a constrained stream would sit against the constraint, and its result would be no better
  than 28.42 + the metal price.
- **The by-product does not reproduce.** The bound optimum's plain pin-knee re-seat (params in the row) was worn frozen
  through `skin-normal-3r-pin-knee.py` itself on Bench(110,360) exact. Script: docs/concepts/verify/coupler-path-j1-audit.py.
  Outputs: `..._reseat_big_frozen.json` and `..._control_big_frozen.json`.

  | config | fast (60,160) | frozen exact (110,360) | reach | in-band14 | follow | contact |
  |---|---|---|---|---|---|---|
  | re-seat (claimed 21.22 / 25.87) | 24.09 | **28.98** | 0.678 | 0.841 | 0.991 | 0.008 |
  | leader k4598, same current code | 22.88 | 29.54 | 0.636 | 0.877 | 1.000 | 0.009 |

  The re-seat gains 0.56 gap points over the leader in the same code, below the 1-point bar. It trades in-band
  (0.877 -> 0.841) for reach (0.636 -> 0.678). The leader itself drifted from its verified 30.35 to 29.54 in the current
  code: that is a measurement/code change, not a design change. The polished H1 (round-3 protocol 28.21) stays ahead.
- **One-line reason:** a closed-loop J1 on the pin-knee chain collapses to a rigid crank under every honest search. Its own
  metal costs 14-36 gap points of in-band, and the fold window is set by the arcs, not by the J2 path.
