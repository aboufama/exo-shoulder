# arm-parked-knee-4r - Arm-parked knee 4R (J4 torsion spring parks the knee hub on arm skin; J2 fold-margin stops)

Screened 2026-10-16 (round 4). Model `docs/concepts/models/arm-parked-knee-4r.py`, sweeps `docs/concepts/sweeps/arm-parked-knee-4r.json`,
row `docs/concepts/rows/arm-parked-knee-4r.json`, motion preview `docs/concepts/viz/concepts/arm-parked-knee-4r.js`.

## The deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Re-measure the ideation number under
   the user's 05:50 rulings before anything else: the 22.36 frozen crossing used slim O15 hubs at J2-J4 and a 10 deg
   fold margin; O20 everywhere is now the rule, so the first number is the O20 control at the same seats. (b) Treat the
   spare as a statics problem, not a policy: the knee azimuth is the energy minimum of the J4 spring under two unilateral
   stops, so check (i) the stop is always pushed (it is, by construction: the unconstrained minimum lies outside the
   window whenever a stop is touched), (ii) the spring preload against the friction and gravity the self-motion
   collects (virtual work through the self-motion Jacobian dq_i/dd, pose by pose), (iii) the coil's real envelope - a
   torsion spring that wraps an O20 housing has OD ~23 mm, so hub 4 is rad ~12, not 10. (c) Ask whether J4 must be a
   4th ACTIVE joint at all: in MVP1 every joint is an unpowered bearing pair; if J4 is a sprung, sensed passive pin the
   complexity drops 32.25 -> 13.25 (tools/simplicity.py), and the same bench number stands. (d) Use the spare for what
   it is worth - the J2 fold window - and measure the counterfactual (J4 locked at the park seat).
2. **The rawest material.** The posed skin itself through the bench's signed-distance grids (tools/concept_bench.py,
   Bench(60,160) fast, Bench(110,360) exact, held-out clips never used), the clip frames for continuity (dense K2 re-runs
   the spring policy between frames), the proximity atlas data and the skin-motion map
   (pipeline/conformal/analysis/skin_motion_map_14.json) only as a cross-check of where hub 4 / link 3 ride; the
   measured chain drag (judge/dynamics.py, docs/FINDINGS.md "Unpowered tracking": 0.05-0.10 N.m about the shoulder,
   rolling bearings tau0 1 N.mm + mu 0.005 |M_perp|).
3. **Methods and tools.** tools/concept_kit.py (K1 closure with the fold margin, K2 dense continuity, K6 part
   collisions at 1 mm / 0.15 mm adjacent, skin-fitted undersides, O20 hub, crown + wall skin check of
   spine-parked-j2-3r's verified extras, near-touch, overhead >= 140 split); the cloud CPU farm (tools/cloud_run.py:
   coarse sweep of 200 configurations, then 6 CMA-ES streams of tools/concept_cma.py - margin 5 and 10, two basins, a
   near-touch objective) with the convergence gate; frozen shape worn on Bench(110,360) exact; virtual work for the
   spring (self-motion Jacobian from the model's own kinematics); tools/simplicity.py for the mechanism record.
4. **What, other than me, shows the number is right.** The bench (Bench(60,160) fast for the search, Bench(110,360)
   exact with the frozen fit shape for the claim), the adversarial verifier of this round (it re-measures with its own
   harness, docs/concepts/verify/), the red-team pose list below (rest / overhead / across / behind the back: taken or
   not, why, min metal-skin distance), and the in-model controls (J4 locked; O15 control for attribution only).

## The model (improved over the spec, and why)

- **O20 at every joint** (user ruling 05:50): the spec's O15 J2-J4 is gone. `slim_control 1` re-creates the ideation
  hubs for ATTRIBUTION only (it reproduces the ideation 19.18 fast as 19.19 - the harness is the same).
- **Margin 5 deg** default (user ruling for MVP1); every claim is also measured at 10.
- **The spring has a real envelope.** A torsion spring that holds the spare (sizing below) has wire ~0.95 mm, mean
  coil D 22 mm round the O20 housing, 6 coils = 5.7 mm tall: it fits inside the 9.1 mm housing height above the lower
  member but its OD is ~23 mm, so hub 4's crown / wall skin check runs at r 12 (`spring_rad`), not 10 (the spec's "rad4
  10" is optimistic). K6 part clearance keeps the kit's O20 disc: the 2 mm coil annulus is a stated hole (link 1 / link 2
  never pass over hub 4 in the red-team poses; the spring legs bear on link 3 and the arm-end plate, J4's own members).
- **Verified checks**: spine-parked-j2-3r's crown + wall check of every hub, near-touch (metal < 1 mm counted as
  contact: `gap_near1`), the overhead split (elev >= 140), dense K2 continuity re-running the spring policy between
  clip frames (a bistable jump of the centred spring is a branch flip, not followed), K6 at 1 mm / 0.15 mm adjacent.
- **The stop is pushed, never pulled**, by construction: the policy is the energy minimum of (k/2)(d - dp)^2 under the
  window; a stop carries load only when the unconstrained minimum dp lies outside the window, and then the spring
  presses link 3's knee toward dp, i.e. into the stop. The stop is a dowel (O2 m6) in a ~100 deg slot of link 2's end
  plate at J2 with 0.8 mm PU bumpers, inside the strap end zone (no extra height).
- **Variant `l3low`**: link 3 as J4's lower member and the arm-end plate + neck on top (link 3 in band 0.33 -> 0.58,
  but K6 part hits 0.095 -> 0.145 at the k-A seats: 40.30 vs 38.90 fast at margin 5) - kept as a sweep dimension.

## The spring (R17 determinacy of the spare, virtual work)

Script: the self-motion Jacobian dq_i/dd (J1-J3 per degree of knee azimuth about J4) from the model's own kinematics on
every taken Bench(60,160) pose, friction per joint tau_f (rolling bearings: tau0 1 N.mm + 0.005 |M_perp|, so 3 N.mm
nominal, 6 N.mm pessimistic), gravity of the bodies that move with the spare (hubs 2, 3 at 9 g; links 12 x 3 Ti).
At the k-A seats (O20, margin 5), on the 157 parked poses (the spare not on a stop):

| | p50 | p95 | max |
|---|---|---|---|
| sum of dq_i/dd (J1-J3) | 1.8 | 2.7 | 3.8 |
| gravity along the spare, N.mm | 2.2 | 4.8 | 5.5 |
| friction reflected, tau_f 3 N.mm | 8.5 | 11.2 | 14.4 |
| hold needed, tau_f 3 N.mm | 11.2 | 14.1 | 17.8 |
| hold needed, tau_f 6 N.mm | 19.6 | 24.9 | 31.2 |
| spring deflection on the stop, deg (24 poses) | 29.5 | 82.7 | 96.1 |

So the proposer's 10 N.mm preload is too weak (below the p50 hold), and the judge's 50-100 N.mm estimate (the whole
chain drag about the shoulder) overstates what the spare collects: the spare needs a **preload of ~40 N.mm** (1.3x the
pessimistic max, 2.8x the nominal p95). A centred spring cannot carry a preload on its own: the design is a
**preloaded return-to-centre torsion spring** (both legs straddle a tab on link 3 and a tab on the arm-end plate; no
motion until the disturbance exceeds 40 N.mm), rate ~20 N.mm/rad: music wire 0.95 mm, D 22 mm, 6 coils
(k = E d^4 / (64 D N) = 19 N.mm/rad), preload wind 2.1 rad, at the max deflection 96 deg the torque is 40 + 32 = 72
N.mm (bending stress 32 M Ki / (pi d^3) = 950 MPa, A228 static allowable ~1000-1500 MPa). **The wearer feels 40-72
N.mm (0.04-0.07 N.m) on the arm about J4 whenever the spare is on a stop** (13-20 % of poses: overhead and across the
body) - comparable to the measured chain drag (0.05-0.10 N.m), stated as an R17 cost. Inertia along the spare (~60 g at
66 mm, 20 rad/s^2) adds ~5 N.mm.

## The 4th joint: active, or a sprung sensed passive pin?

MVP1 is unpowered: the four joints are the same bearing pairs + encoders either way, and the bench number is the same.
The difference is the count and MVP2. tools/simplicity.py: **4 active joints = 32.25**; **3 active + J4 a sprung,
sensed passive pin = 13.25** (1 passive rotation, 1 sensed, 1 spring, 1 body and 1 joint beyond 3, parts). In MVP2 any
serial 4-joint chain driven by 3 motors leaves one joint unactuated: with J4 sprung (preloaded centring + the J2 stops),
the arm's rotation about J4 is driven THROUGH the spring - a series-elastic axis, soft by 20 N.mm/rad beyond the 40 N.mm
preload. That is a real MVP2 design question (the user's call), not a bench number. Either reading is far from the
golden target's complexity ~0: the 4R is the honest upper bound of what a spare buys, not the golden solution.

## Results
