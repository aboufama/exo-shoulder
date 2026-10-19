# slotted-eccentric-j2-3r - eccentric J2 crank + slotted-lever cam on the zero-passive spherical 3R (O20)

## Deeper version (answered before modelling, 2026-10-16 06:10 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the slot as a *designed cam
   law*, not a given: the knee law a2e(th) is free, the slot is whatever curve the roller traces in link 2b's frame,
   so the real gate is not "d monotone" but the **pressure (lock) angle of the internal four-bar mode**: at a fixed arm
   pose the four GH-concurrent axes J1-J2-K-J3 form a spherical four-bar with one internal freedom, and the slot must
   cut across the roller's velocity in THAT mode (the spec's radial-only check ignores that K itself moves). I check
   that mode by finite differences on synthetic poses. (b) Solve the roller seat F1 per configuration by a grid
   (maximise the worst lock angle subject to roller-vs-knee and lever-vs-hub-2 clearance) instead of sweeping it.
   (c) Run the locked control through the identical code, at O20 (user ruling), at fold margin 5 AND 10.
   (d) Carry the lever as a real curved body: polyline along the slot, widened by its own deviation from the polyline.
2. **Rawest material.** The posed skin on the bench (signed-distance grid cache, exact path for the claim), the six
   training motion clips + workspace poses inside tools/concept_bench.py (held-out clips never loaded), the J1-J3
   angle distribution of those poses (th_need, from the poses themselves), docs/research/reach_attribution.md only as
   a cross-check.
3. **Methods and tools.** tools/concept_kit.py (K3 march, K2 dense continuity on every joint axis incl. K and the
   roller F, K6 with same-body exemption, honest post heights from dwell-fourbar-knee-3r.py), the farm
   (tools/cloud_run.py sweep), CMA-ES (tools/concept_cma.py) from the top configurations, the frozen-shape wear on
   Bench(110,360) exact.
4. **What shows the number is right besides me.** The bench (outside judge), the frozen exact run on Bench(110,360)
   (no refit), an adversarial verifier re-running the model, and a red-team pose list (overhead >= 140, across-body,
   behind-the-back, the near-touch list, the slot lock-angle minimum and where it happens).

## The spec was wrong in one place: the slot cannot sit on link 2b with the roller on link 1

Measured first, before any bench run (`python3 docs/concepts/models/slotted-eccentric-j2-3r.py gate`, synthetic poses
over the J1-J3 angle th, Amin 60 / Amax 90 / b 25 / c 72 / a1 38.09 / margin 5):

- Over the window the law opens (th 27-123 deg), the crank angle q2 (crank vs link 1 about J2) spans **200.8 deg**:
  the J2 interior angle runs 0 -> 180 deg across any wide fold window, and the knee offset does not cancel it.
- With the roller F fixed on link 1 and the slot in a lever on 2b (the spec), the cam is **singular whenever F, K and J2
  lie on one great circle**: there d/dq2 and d/dpsi move the roller along the same direction in 2b's frame, so the slot
  cannot hold the knee. That happens whenever the crank's azimuth about J2 passes the roller seat's (or its antipode):
  with a 200 deg crank sweep, for EVERY seat. Fine-sampled (0.02 deg in th): seat (38, -7.5) lock angle 2.46 deg at
  th 75.92 where q2 = -7.49 = the seat azimuth; seat (20, 0) 0.024 deg at q2 = -0.02. (A 0.5 deg sampling misses the
  dip and reads 37 deg - the gate now also tests the alignment angle directly.)
- **Inverted** (roller G on link 2b at polar (dG, gG) about K, the slot a curved track fixed to link 1 around hub 2) the
  singular set is G-K-J2 alignment, which depends on the knee angle alone (psi spans 57-134 deg here), so it can be
  placed out of the way. This is the model. Same parts, same mobility, same complexity.
- The inverted cam's lock angle (angle between the roller's velocity in the internal four-bar mode at a fixed arm pose
  and the slot tangent; >= 50 deg = pressure angle <= 40 deg, the spec's number) falls toward the fold edges: the
  internal mode of the J1-J2-K-J3 loop IS the fold mode, it changes the knee angle only in proportion to sin(J2 interior
  angle). Best seat at the default law: 41 deg over the whole window, >= 50 deg only over th 27-117.75 (the track
  ends there: a hard stop, poses beyond are not taken). The slot lock is a fold margin in disguise.
- The track is long: 106 mm of slot, 152 deg around J2 at 25-45 deg (27-49 mm) from its axis, i.e. a crescent of
  link 1 plate around hub 2 that reaches the trapezius / neck skin.

## Model (docs/concepts/models/slotted-eccentric-j2-3r.py)

Kit model on tools/concept_kit.py with dwell-fourbar-knee-3r.py's checks imported unchanged (same-body K6, honest post
heights, crowns + walls skin-checked, near-touch, overhead split, declared pins). O20 at J1 / J2 / J3 (user ruling),
fold margin 5 (ruling; 10 reported for the control), J1 seats from the leader family (back of the shoulder / acromion).

- Law: a2e(th) = soft clip of Ac + sl (th - Ac) into [Amin, Amax] (sl = 1 = the spec's clip(th)); J2 by the closure
  (a1, a2e), K by the closure (b, c) on branch sk = +1 (sk = -1: q2 not monotone, window 27-63 - dead), knee
  transmission psi in [15, 165].
- Slot (inverted): roller G = MR52ZZ on an O2 dowel in an O7 boss pressed into an arm of link 2b (dG, gG about K);
  track = a 2 mm slotted plate of link 1 around hub 2 (slot 2.6 between 1.95 mm walls), polyline along the slot (<= 10
  segments), widened by its own deviation, ends extended by roller + wall; a spoke from hub 2 joins it to link 1. The
  seat (dG, gG) is grid-solved per configuration (13 x 48 seats) to cover the most of th 26-141 with the lock >= 50 deg,
  normal gain >= 0.2 deg / deg, no G-K-J2 alignment within 10 deg, no self-overlap; wL / emax trade track length and
  radius (CMA-tuned). The track ENDS where the lock is lost: poses beyond are not taken.
- Members: hub1-3 (O20), knee pin K (MR63ZZ pair, O10, 6.5 stack, post raised to the highest strap end), stud G (O7,
  post = track 2 + 1 + arm 3), link 1, spoke, track segments, crank (over link 1 / spoke / track), link 2b and the arm
  (over all of those), the K7 neck. Bodies: link 1 + spoke + track; 2b + arm + stud.
- Control (lock = 1): the same seats, link 2 straight through K (the plain spherical 3R), same members and checks.
- Mechanism record (docs/SIMPLICITY.md, re-weighted 2026-10-16): 3 active, 0 passive translations, 1 passive rotation
  (K, slaved), 1 closed loop, 1 sliding (roller-in-track) pair, 4 moving bodies, 5 joints, 11 made + 5 catalogue parts
  -> **complexity 11.0** (tools/simplicity.py).

## Results (Bench(60,160) fast, O20, margin 5, slot lock >= 50 deg)

| run | configs | best gap | score | reach | follow | in-band 14 | in-band 10 | contact |
|---|---|---|---|---|---|---|---|---|
| CONTROL plain 3R (link 2 straight), D seats, margin 5 | 1 | 47.25 | 82.8 | 0.600 | 0.817 | 0.881 | 0.475 | 0.020 |
| CONTROL same, margin 10 | 1 | 45.01 | 83.6 | 0.588 | 0.850 | 0.883 | 0.545 | 0.020 |
| default (spec law clip(60, 90), b 25 / c 72) | 1 | 182.32 | 33.7 | 0.088 | 0.050 | 0.845 | 0.682 | 0.056 |
| coarse LHS (farm) | 228 | 87.17 (not honest: track samples > 140 mm) | | 0.763 | 0.917 | 0.248 | | 0.048 |
| CMA A (D seats) / B / C (LHS bests) | 649 / 81 / 89 | 149.77 / 177.17 / 189.82 | | | | | | |
| **CMA E (spec-law start, wL / emax free)** | 689 | **74.00** | **73.1** | 0.719 | 0.867 | 0.486 | 0.278 | 0.062 |

Best (E gen 13, flat for 73 generations): az 95.18, el 60.96, a1 41.12, wd 86.24, wa -14.13, Amin 61.04, Amax 92.66,
w 4.12, sl 0.973, b 22.09, c 75.07, q 0.963; seat solved dG 29, gG 7.5; track th 25-125.5 (need-cover 0.97), 116 mm,
154 deg around J2 at 24-49 deg, width 8.2 mm, lock 50.7 deg min (33.2 over the full run), q2 span 223 deg.
Red team on that config: min metal-skin 0.27 mm (gap 83.50 if metal < 1 mm counts as contact); overhead (elev >= 140)
0/17 taken (all K6: neck vs link 2b - the knee is thrown over the head line, pin K's requirement 207-400 mm at elev 150);
across-body 25/36, behind-the-back 17/19, rest 5/5 (in-band 0.44 at rest); reach loss over 160 ws poses: fold 18, K6 16,
contact 11. Per part in band: hub 1 0.90, hub 2 0.21, hub 3 0.72, pin K 0.77, stud 0.31, link 1 0.65, crank 0.26,
link 2b 0.05, arm 0.27, track 1-6 0.94-1.0, track 7-10 0.59 -> 0.02, neck 0.81. Kinematic reach of the law 0.89
(th_need p5 24.6 / p95 130.4) - the window works, the bodies do not.

Convergence gate (whole ordered history, 1730): best gained 4.79 score points over the second half, 0.00 over the last
third, top-5 spread 7.77 -> **NOT converged**; status stays "screened", not "dead". Round 2 was in flight on the farm at
report time: CMA F (from E, sigma 0.25), G (lock_min 35: what the spec's pressure-angle rule costs), H (locked-control
CMA from E's seats: the plain chain at the same seats, same code), and E's frozen shape worn on Bench(110,360) exact
(`CB_EXACT=1 ... frozen`). Outputs: .cache/se_cma/{cma_F,cma_G,cma_H,frozen_E}.json via tools/cloud_run.py batch.

## Verdict and what it teaches beyond this morphology

- A roller-in-slot cam between link 1 and link 2b cannot have the roller on link 1: the crank sweeps 200+ deg about J2
  over any wide fold window, so the roller-crank alignment singularity is unavoidable. Inverted, it works kinematically
  (lock >= 50 deg over th 25-125.5) - but **the internal mode the slot must lock is the fold mode itself**, so the cam's
  pressure angle degrades exactly where the window is being extended. Any "slaved knee" (slot, four-bar, relay) has
  this: its holding stiffness ~ sin(J2 interior angle).
- The slot law delivers the kinematic window (reach ceiling 0.89), but the knee that realises a2e up to ~93 deg sits
  off the arc between J2 and J3 and, overhead, lands where there is no skin within 220 mm of GH on its rays. The fold
  lever must not move a pin off the J2-J3 great circle overhead: the same failure as the dwell four-bar (verified 37.66)
  - only stronger, because the two-sided law bends the knee further.
- Next (if anyone continues): put the knee on the J1 side (a two-state a1 relay, round-5 plan), where the bent member
  stays over the scapula; or cap Amax at ~80 and let the law act only on the folded side (= the dwell, already measured).

## Verification (independent verifier, 2026-10-16 07:17 UTC) - REFUTED

Harness: `docs/concepts/verify/slotted-eccentric-j2-3r.py` (the model's own `frozen` protocol: fit on Bench(60,160)
fast, every underside / post frozen, worn on Bench(110,360) with `CB_EXACT=1`, K6 at 1 mm radial), plus corrections:

- K6 shared-joint exemption sized to the real joint: knee K (MR63ZZ, O10) 7 mm, roller stud G (O7 boss) 5.5 mm (the kit
  exempts 12 mm, sized for an O20 hub).
- Real roller: the model cuts a 2.6 mm slot (the O2 dowel's) for an MR52ZZ 2 x 5 x 2.5 roller; the slot must take the
  5 mm OD -> track width + 2.45 mm.
- Independent closure per pose: link 1 {J1, J2}, crank {J2, K}, link 2b {K, J3, G} keep their rest axis angles and
  handedness (max error 0.000 deg), and G in link 1's frame lies on the exact slot locus (max 0.0006 mm).
- Slot lock recomputed at every taken pose (internal four-bar mode vs slot tangent): min 53.6 deg; G-K-J2 alignment
  min 31.2 deg; no pose would back-drive. The determinacy claim (3 active, knee slaved, R17) holds.

| run (CMA E gen 13, O20) | bench | gap | reach | follow | ib14 | ib10 | contact | near-touch | overhead reach |
|---|---|---|---|---|---|---|---|---|---|
| claimed (K6 radial 0.5 mm) | (60,160) fast | 74.00 | 0.719 | 0.867 | 0.486 | 0.278 | 0.062 | 83.50 | 0/17 |
| own checks, K6 1 mm, fit | (60,160) fast | 124.83 | 0.438 | 0.650 | 0.506 | - | 0.092 | - | - |
| own checks, frozen | (110,360) exact | 119.31 | 0.450 | 0.673 | 0.516 | 0.296 | 0.082 | 127.98 | 0/28 |
| **verifier, margin 5** | (110,360) exact | **115.21** | 0.464 | 0.718 | 0.501 | 0.299 | 0.086 | 123.65 (min metal 0.0 mm) | 0/28 |
| verifier, margin 10 | (110,360) exact | 197.93 | 0.147 | 0.082 | 0.616 | 0.507 | 0.075 | 220.95 | 0/28 |
| locked control (plain 3R, same seats, a2 76.85), m5 | (110,360) exact | 46.60 | 0.603 | 0.918 | 0.799 | 0.418 | 0.036 | 57.15 | 4/28 |
| locked control, m10 | (110,360) exact | 49.23 | 0.581 | 0.882 | 0.824 | 0.452 | 0.029 | 56.38 | 3/28 |

Champion on the same protocol: 66.97 (offset-skin-normal verifier, kit checks) - 75.94 (risley-turret verifier).
Verdict: **refuted** - 115.21 is worse than the champion and 69 points worse than its own locked control through the
same code. The largest single correction is not mine but the honesty rule's: the screened 74.00 used the kit's 0.5 mm
radial part-part overlap; at the 1 mm rule the fit alone is 124.83 (the crank / link 2b / arm / track stack around hub
2 has no radial room). Per part in band (verifier, big bench): link 2b 0.05, arm 0.00, crank 0.26, hub 2 0.25, stud
0.31, track 8-10 0.02-0.12. The kinematic window is real (kin reach 0.856 vs the control's 0.689); the bodies that
build it cannot live in the band, and none of the overhead poses is taken. Not counted against it (as for dwell): the
O10 knee and O7 stud under the O20-only ruling.
