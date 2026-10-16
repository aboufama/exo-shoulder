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

All Bench(60,160) numbers are fast (grid cache), every check on; frozen = the fit shape (hub levels, strap undersides)
of Bench(60,160) worn without refit on Bench(110,360) EXACT, K6 at 1 mm. near = metal < 1 mm counted as contact.
over = reach of the workspace poses at elevation >= 140 (12 on the small bench, 28 on the big one).

### 1. The O20 rebase (measurement change, not a design change)

| config | hubs | margin | fast gap | frozen exact gap | reach (frozen) | over (frozen) | near (frozen) |
|---|---|---|---|---|---|---|---|
| ideation k-A (its claim) | O15 J2-J4 | 10 | 19.18 | 22.36 | 0.750 | 0.393 | - |
| k-A, slim_control (attribution only) | O15 J2-J4 | 10 | 19.19 | - | - | - | - |
| k-A | O20 | 10 | 30.84 | 33.91 | 0.744 | 0.357 | 46.05 |
| k-A | O20 | 5 | 38.90 | 44.24 | 0.672 | 0.357 | 54.69 |

O20 costs 11.65 fast points at the ideation seats (hub 2 in band 1.00 -> 0.75 / 0.58, link 3 0.50 -> 0.36 / 0.33).

### 2. Search (farm): 200-config coarse sweep + 16 CMA-ES streams, 13383+ configurations

Coarse random sweep (200, margin 5, sides 0 / +-1, branch +-1): best 45.06 - worse than the start point; the
landscape is narrow (branch s1 +1 never below 81.9; one-sided springs worse than centred: at k-A side -1 43.47, +1 73.29).

| stream | start | objective | margin | tries | best fast | gate: gain 2nd half / last third / top-5 spread (score pts) |
|---|---|---|---|---|---|---|
| A5a | k-A | gap | 5 fixed | 1169 | 27.93 | 0.47 / 0.47 / 0.04 |
| A5b | k-A | gap | 5 fixed | 1033 | 25.31 | 0.50 / 0.24 / 0.14 |
| C5 | basin c | gap | 5 fixed | 1505 | 23.87 | 0.01 / 0.01 / 0.01 |
| A5n | k-A | near | 5 fixed | 1297 | 30.84 | 0.93 / 0.11 / 0.03 |
| A10 | k-A | gap | 10 fixed | 1057 | 17.47 | 0.04 / 0.04 / 0.01 |
| C10 | basin c | gap | 10 fixed | 905 | 23.85 | 0.20 / 0.09 / 0.05 |
| W1 | A10 | gap | free (>= 5) | 785 | 17.30 (m 10.07) | 0.06 / 0.06 / 0.03 |
| W2n | A10 | near | free | 1041 | 21.79 near / 18.41 plain (m 10.09) | 0.31 / 0.14 / 0.04 |
| **W3n** | C10 | near | free | 969 | **21.60 near / 19.32 plain (m 11.74)** | 0.87 / 0.27 / 0.03 |
| W4n | C5 | near | free | 1377 | 29.00 near (m 5.17) | 0.37 / 0.17 / 0.02 |
| W5l | A10, l3low | gap | free | 1025 | 16.31 (m 9.02) | 0.36 / 0.08 / 0.02 |
| W6 | A10, sigma 0.8 | gap | free | 1017 | 16.57 (m 10.09) | 0.21 / 0.19 / 0.02 |

Every stream passes the convergence gate (sigma collapsed in all). **The stop position is a design variable and its
optimum is 9-12 deg from the fold, not 5**: with the margin free, every stream moved it to 9-12 deg (W4n, started at 5,
stayed in the margin-5 basin at 29.0). The user's 5 deg is the lower bound for the stop; a 4R's spare takes over the
poses beyond it, so a wider stop gives up nothing the spring cannot pick up, while a stop at 5 deg admits near-fold
configurations whose links clash and whose hubs must ride higher.

### 3. Frozen on Bench(110,360) exact (the claim)

| config | margin | fast | fast near | **frozen gap** | frozen near | reach | follow | ib14 | ib10 | contact | over | min metal mm | crown-contact poses | spare on stop | defl p95 / max deg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **W3n (claim)** | 11.74 | 19.32 | 21.60 | **25.05** (score 90.9) | **29.29** (89.3) | 0.772 | 0.955 | 0.810 | 0.398 | 0.033 | 0.286 | 0.40 | 7 | 38 % | 77 / 130 |
| W3n | 10 | 20.90 | 24.31 | 24.94 | 30.25 | 0.775 | 0.955 | 0.806 | 0.393 | 0.030 | 0.286 | 0.11 | 5 | 35 % | 69 / 127 |
| W3n | 5 | 58.21 | 61.99 | 62.11 | 66.84 | 0.572 | 0.900 | 0.698 | 0.325 | 0.041 | 0.286 | 0.30 | 5 | 26 % | 70 / 160 |
| W6 (plain best) | 10.09 | 16.57 | 39.07 | 24.47 (91.1) | 38.02 | 0.761 | 1.000 | 0.860 | 0.479 | 0.066 | 0.214 | 0.01 | 16 | 28 % | 62 / 137 |
| W6 | 10 | 16.57 | 40.19 | 24.72 | 39.29 | 0.761 | 1.000 | 0.860 | 0.479 | 0.068 | 0.214 | 0.01 | 17 | 28 % | 62 / 136 |
| W6 | 5 | 42.21 | 59.14 | 51.04 | 67.67 | 0.586 | 0.900 | 0.839 | 0.479 | 0.086 | 0.214 | 0.01 | 14 | 23 % | 57 / 113 |
| W2n | 10.09 | 18.41 | 21.79 | 26.47 | 32.26 | 0.764 | 0.991 | 0.819 | 0.392 | 0.047 | 0.286 | 0.13 | 7 | 30 % | 73 / 141 |
| A10 | 10 | 17.47 | 57.34 | 27.27 | 58.34 | 0.739 | 0.973 | 0.856 | 0.470 | 0.068 | 0.143 | 0.02 | - | 25 % | - / 106 |
| W5l (l3low) | 9.02 | 16.31 | 56.28 | 42.93 | 72.08 | 0.589 | 0.936 | 0.872 | 0.470 | 0.076 | 0.143 | 0.01 | 8 | 23 % | 60 / 115 |
| C10 | 10 | 25.93 | - | 33.84 | 41.88 | 0.742 | 0.900 | 0.827 | 0.470 | 0.057 | 0.214 | 0.15 | - | 60 % | - / 138 |
| C5 | 5 | 28.79 | - | 34.95 | 59.43 | 0.625 | 1.000 | 0.855 | 0.463 | 0.029 | 0.250 | 0.00 | - | 12 % | - / 92 |

The claim is W3n, not W6: they tie on the plain frozen gap (25.05 vs 24.47, 0.6 apart) but W3n keeps its number when
near-touch counts (29.29 vs 38.02; min metal-skin 0.40 vs 0.01 mm; 7 vs 16 crown-contact poses). The plain-gap optima
(A10, W5l, W6) buy their fast numbers with metal skimming the skin (fast near 39-57) and lose 8-27 points frozen: the
fold tuned to the sample (lesson c) is visible here too (A10 17.47 -> 27.27, W5l 16.31 -> 42.93).

W3n best parameters: az 108.03, el 71.02 (J1 on the acromion top / back, inside the user's J1 seats), J4 wdir(76.20, -7.91),
a1 32.85, a2 72.97, a3 25.49 deg, pz4 104.0 (spring rest azimuth), stops at 11.74 deg from the J2 fold, centred
spring, q 0.98, end_extra 1.28, all O20 hubs (hub 4 + spring coil r 12). Fitted hub levels F 49 / 59 / 66 / 77 mm. In band per member
(fast): hub 1 1.00, hub 2 0.99, hub 3 0.88, **hub 4 0.51, link 3 0.32**, link 1 0.99, link 2 0.89, neck 0.74.

### 4. Controls

- J4 locked at the park seat (lim4 0): k-A 58.37 / 65.73 (m 5 / 10), A10 60.34, W3n 82.18 fast - the spare is worth
  40-60 fast points at its own seats.
- **Against the best 3R at O20, same protocol**: the polished pin knee H1 (3R + a flat two-pin knee, 0 passive
  translations, complexity 19.5) on the round-3 verifier protocol (fit Bench(60,160) fast, worn exact; margin 10) is
  28.21 plain / 33.77 near-touch (docs/concepts/skin-normal-3r-pin-knee.md); W3n here is **25.05 / 29.29** - the 4th
  joint is worth ~3 plain / ~4.5 near-touch points at O20, not the ideation's ~12 (most of that came from the slim O15
  hubs at J2-J4 the user ruled out). Price: complexity 32.25 (4 active) or 13.25 (J4 a sprung, sensed passive pin) vs
  19.5, and a spring the wearer feels on 26-38 % of poses. (The pin knee's 26.45 / 24.48 are on the polish protocol -
  fit on Bench(110,360) fast - not comparable to the numbers here.)

### 5. Overhead-weighted search (the user's priority)

Four more CMA streams with objective = gap + w * 100 * max(0, 0.9 - overhead reach) (w 0.3 / 0.6, plain, near-touch and
`l3low` starts; 4196 tries): three found no configuration that takes a single overhead workspace pose of Bench(60,160)
(stayed at their starts, overhead reach 0/12); the near-touch stream O2n took 2 of 12 at 23.90 near / 20.49 plain fast
(vs W3n 21.60 / 19.32). Frozen on Bench(110,360) exact, O2n is 26.65 plain / 31.99 near-touch with overhead reach
**0.39** (11 of 28) vs W3n 25.05 / 29.29 / 0.29: ~0.1 of overhead reach costs ~1.6 plain / ~2.7 near-touch points.
O2n's parameters: rows/arm-parked-knee-4r.json exact_frozen_others.O2n. The overhead loss is structural for this
morphology (red team below), not a search artefact.

## Red team (my own best, W3n)

- **The pose that jams.** Overhead across the body (plane 90-120, elev 150-165, axial -90 / -135): the J1-J4 angle
  leaves what the knee cone (a3 25.5) plus the J2 window can meet - fold (26 of the 31 lost poses on Bench(60,160) are
  fold/K2; across 26/36 taken, behind the back 14/19, rest 5/5, overhead 5/17). The spare widens the J1-J3 window but
  the knee cone is small; a longer link 3 (a3 up) moves link 3 and hub 4 off the deltoid (they are already the
  worst-banded parts).
- **The point that pinches.** Abduction overhead (plane 0, elev 150, axial 0): hub 2 is 6.3 mm and link 2 4.9 mm
  inside the skin bulge over the acromion / trapezius (hub 3 4.3 mm) - one rigid level per hub over all poses cannot
  clear it (proximity atlas: a rigid part must clear the highest skin it ever passes over). Taken poses: min metal-skin
  0.03 mm fast (#210, plane 135, elev 135, axial -45: across overhead) and 0.40 mm frozen; 7 crown/wall-contact poses on
  the big bench.
- **The number that is optimistic.** (a) Fast 19.32 -> frozen 25.05 (+5.7: the fold tuned to the sample; the plain-gap
  optima lose 8-27 points); (b) plain vs near-touch: +4.2 frozen; (c) the centred spring has TWO feasible arcs for the
  knee (|d| in [dlo, dhi] on either side): the model takes the low-energy arc pose by pose, but the J2 stops trap the
  physical knee on its arc - the preview loop shows 2 snaps (across -> rest at plane 56 / elev 39: J3 jumps 163 deg;
  behind -> rest at elev 16: 90 deg). On the bench's clips the dense K2 continuity check sees no flip (flips 0), but a
  workspace pose reached from the other side could find the knee on the other arc, spring wound past its rating. A
  third stop that confines the knee to one arc is the fix to try (it costs the poses that need the other arc).
  (d) The spring coil annulus (r 10-12) is skin-checked but not K6-checked against links 1 / 2.
- **The feel.** The spare sits on a J2 stop on 26-38 % of poses (overhead, across): the wearer then feels the spring,
  40 N.mm preload + 19 N.mm/rad x up to 130 deg = up to 83 N.mm about J4, comparable to the whole chain's measured drag
  (0.05-0.10 N.m). In park poses the 40 N.mm preload holds the spare against at most 18 N.mm (rolling bearings,
  nominal) / 29 N.mm (pessimistic friction) - the spare does not break away.

## Verdict

**Screened, converged, not the golden solution.** At O20 everywhere the arm-parked knee 4R scores 19.32 fast and
**25.05 frozen on Bench(110,360) exact (score 90.9; near-touch 29.29 = 89.3)** with 0 passive translations - it does
cross 90 frozen on the plain gap, and it beats the pin-knee 3R on the same protocol by ~3 plain / ~4.5 near-touch
points. But the spare's price is high for what it buys: complexity 32.25 (or 13.25 as a sprung sensed J4) against the
golden target's ~0, a felt spring on a third of the poses, a two-arc hysteresis, and the overhead still lost (0.29
frozen). The 4th joint does NOT open the overhead: what kills overhead is skin proximity at J2 (abduction) and the knee
window across the body, neither of which the spare removes.

## New knowledge (predicts beyond this morphology)

1. **The ideation's 4R advantage was mostly hub size.** At the same seats O15 -> O20 costs 11.65 fast points (19.19 ->
   30.84); after re-optimisation at O20 the 4R leads the 3R pin knee by ~3 frozen points, not ~12. Any slim-hub claim
   from before the 05:50 ruling should be expected to lose ~10 points at O20.
2. **With a spare, the J2 stop position is a design variable whose optimum is ~10-12 deg from the fold, not the
   5 deg minimum.** Every free-margin stream moved it to 9-12 deg; the same shapes at 5 deg are 26-37 frozen points
   worse (more near-fold configurations with link clashes and higher-riding hubs). The 5-deg ruling is a bound, not a
   target, whenever something else (a spring, a knee, a pin) takes over the poses beyond the stop.
3. **Near-touch must be in the objective, not only in the report.** Plain-gap CMA optima here put metal within 1 mm of
   skin on 15-20 % of poses (fast near-touch 39-57 vs plain 16-17) and lose 8-27 points frozen; the near-touch
   objective costs ~2 fast points and holds up frozen (25.05 plain / 29.29 near vs 24.47 / 38.02).
4. **A sprung spare needs ~40 N.mm preload, not 10 and not 100.** The self-motion collects friction through
   sum |dq_i/dd| = 1.8-3.2 (J1-J3), so the hold is 3-4x one joint's friction plus 3-7 N.mm of gravity. A preloaded
   return-to-centre torsion spring (wire 0.95, D 22, 6 coils) fits round an O20 housing at OD ~23 (r 12 keep-out).
5. **A centred spring under two stops is bistable by topology**: the feasible knee azimuths form two disjoint arcs;
   any pose-by-pose energy-minimum policy is path-blind and must be checked on continuous motion (preview loop: 2 snaps).
