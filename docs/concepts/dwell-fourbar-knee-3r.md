# dwell-fourbar-knee-3r - a spherical Watt six-bar knee in link 2 of the zero-passive 3R (pins only, no spring)

## Deeper version (answered before modelling, 2026-10-16 04:58 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the loop as a coupler-curve design problem, not as "a knee": in link 1's frame the J3 axis traces a curve
     u3(s) on the sphere as the crank (q2) turns, and the only thing that matters for reach is the range of
     angle(u1, u3(s)) on ONE monotone, singularity-free arc of that curve. Measure that window per configuration
     (IK only, exact) before any skin evaluation, and gate every configuration on it.
   - Run the locked control in the same file and through the same checks (knee rigid, no P / Q / rocker): any gain must
     be the loop's, not the re-tuned seats' (the rail-elbow lesson).
   - Price the loop's real cost: three extra pin stacks (MR63ZZ pair, 6.5 mm) and a rocker layer that must pass over
     link 1 and L2a; model each body (link 1 + its P plate, L2a, L2b + its Q tail, the rocker) and exempt only parts of
     the same rigid body from each other.
   - Ask the R17 / tolerance question of a closed spherical 4R loop (J2, K, Q, P): with four pins it is overconstrained
     and binds unless the axes meet at GH within the bearings' tilt play; the generic fix is a rocker with one
     spherical end + one U end (mobility 1 for any axis error), priced in stack.
2. **Rawest material.** The posed skin of every bench pose (signed-distance grid, exact libigl path for the claim), the
   per-pose J1-J3 axis angle theta = angle(p1, p3) computed from the raw scapula / humerus frames of the 160 / 360
   workspace poses and the 10 fps fit clips (the window demand, not a reach summary), the skin-motion map
   pipeline/conformal/analysis/skin_motion_map_14.json and the proximity atlas for where pin Q (deltoid edge /
   posterior axillary fold) can live.
3. **Methods and tools.** Closed-form spherical loop closure (two-circle K1 closure for pin Q on a 0.25 deg crank grid,
   secant-refined per pose to < 1e-3 deg), the kit (tools/concept_kit.py: K3 march, K4 flat hubs, K5 straps, K6
   collisions, dense K2 along the 10 fps motion), the seed's crown / wall / near-touch / overhead audit
   (spine-parked-j2-3r extras), the farm (tools/cloud_run.py sweep for the coarse sweep, tools/concept_cma.py batch jobs
   for CMA-ES), the frozen-shape protocol (fit Bench(60,160) fast, wear on Bench(110,360) exact).
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, metrics, contact rule), the
   kit audit (`honest`), the locked control in the same file, the frozen Bench(110,360) exact run, and a red-team
   pose list (rest, overhead >= 140, across the body, behind the back, posterior axillary fold poses #92/#93/#115,
   closest metal incl. crowns of the pins).

## Spec corrections (said, then built)

* **Base chain.** The catalogue says "the pin-knee leader" in the lead note and "subclass spine-parked-j2-3r" in the
  model spec. The loop is spherical (every axis through GH), so it closes on the ARM exactly like the plain spherical
  3R: no cuff knee is needed. It is therefore built on the spine-parked chain (zero passive, slim O15 J2 / J3 hubs,
  K7 neck), and member 3 is hub 3's plate + the neck. A pin-knee cuff closure would add 2 more passive pins and buy
  nothing on this bench (no GH translation here).
* **Same-body exemption.** Link 1 and its plate to P, and L2b's strap to J3 and its tail to Q, are one machined part
  each. The kit's K6 only exempts parts that share a joint, so the model wraps K6 to skip SAME-BODY pairs, and nothing
  else (collisions_sb, same code path per pair).
* **Honest posts (the kit's stack rule is not enough here).** The kit only RAISES a strap end onto its joint (>= F, >=
  F + 3.15). With a rocker that must pass over hub 2, the rocker's end at P floats 10-35 mm above pin P. The model
  makes that joint's post as tall as the highest strap end on it (adjust_stacks: crown check, K6 and mass use the real
  height), fits twice so `over` sees the real posts, and applies the same rule to the locked control.
* **Over set.** "Every strap over the neck" (the spine-parked convention) lifts L2a, the rocker and L2b by 30-45 mm
  (the neck rises to 100 mm at BOTTOM's bar): seed 59.11 with the kit's stack rule, 126.39 with honest posts. The
  structural set (L2a over link 1; rocker over link 1, L2a and hub 2; L2b over link 1, rocker, L2a) leaves neck
  crossings to K6 (`ov` 1, the default): seed 45.79.
* **Pin sampling.** The O10 pin discs are sampled at 1.25 mm (a 2 mm grid on an O10 disc reaches only 4.24 mm, under
  the audit's rad - 0.5). Pins are a DECLARED component (PIN: MR63ZZ pair in an O10 Ti boss, 6.5 mm stack), checked like
  the slim hubs (cover >= 75 % of the declared disc, reach >= rad - 0.5).

## Model (docs/concepts/models/dwell-fourbar-knee-3r.py)

* In link 1's frame (u2 = z, u1 at arc a1 / azimuth 0): K = Rz(s) K0 (arc b from J2, azimuth chi off the J2-J3 circle),
  Q = the two-circle closure of (P, r) and (K, k) on the branch that holds the rest posture at s = sref, u3 = J3's
  fixed coordinates in L2b's (K, K -> Q) frame. The rocker arc r is set so the knee is straight at sref.
* Valid: Q closes, transmission angle at Q in [30, 150], at K in [20, 160]. The chain runs on ONE monotone valid arc of
  th(s) = angle(u1, u3(s)) (the one holding the rest posture); window = [th_min + 10, th_max - 10] (the jam margin at
  both ends, as the plain chain's).
* Per pose: th = angle(p1, p3) -> s (interpolated on a 0.25 deg grid, 3 secant steps: residual 0.019 deg) -> the
  rotation taking (u1, u3(s)) to (p1, p3) places J2, P, K, Q. q = [q1, s, knee, q3, rocker] for dense K2; the joint
  axes J1-J3, P, K, Q are all in Chain.joints (axis-jump check).
* Members: hub 1 (O20), hub 2 / hub 3 (O15 declared), pins P / K / Q (O10, 6.5 mm, declared), link 1 + plate to P, L2a,
  rocker C (8 x 3), L2b strap to J3 + tail to Q (12 x 3), the K7 neck. Crowns and walls of every hub and pin
  skin-checked; near-touch; overhead split.
* `lock=1` = the LOCKED CONTROL: the rocker, P, Q and the knee pin removed, link 2 rigid through K (the plain spherical
  3R through the same members and checks).

## Results (Bench(60,160) fast, kit checks, honest posts; 5892 configurations in docs/concepts/sweeps/dwell-fourbar-knee-3r.json)

| config | what | gap | reach | in-band 14 | contact | window (deg) |
|---|---|---|---|---|---|---|
| seed k21, every strap over the neck | ideation seed, kit stack rule | 59.11 | 0.738 | 0.514 | 0.043 | [22.9, 104.3] |
| seed k21, `ov` 1, honest posts | ideation seed | 45.79 | 0.706 | 0.664 | 0.028 | [22.9, 104.3] |
| **locked control** at the seed seats (spine-parked CMA-B) | knee rigid, no loop, same members / checks | 31.40 | 0.669 | 0.852 | 0.035 | [43.1, 104.4] |
| coarse best (k58 of 256 farm configs) | loop near the seed, seats jittered | 41.88 | 0.675 | 0.746 | 0.040 | [33.0, 104.7] |
| CMA A / B / C (from the coarse top 3) | 1313 / 1409 / 1297 tries | 28.50 / 28.46 / 31.84 | 0.71 / 0.71 / 0.66 | 0.81 / 0.83 / 0.84 | | [34.8, 103.1] / [31.6, 106.5] / [36.3, 101.2] |
| **CMA D best** (1601 tries from the seed, sigma 0.8) | az 97.75, el 65.29, a1 38.09, a2 74.27, wd 90.05, wa -9.20, b 40.79, chi 6.54, gP 22.44, phP 28.49, k 18.74, alq -141.0, sref 196.2, q 0.963 | **26.86 (score 90.23)** | 0.700 | 0.843 | 0.012 | [35.9, 102.5] |
| locked control at the CMA D seats | knee rigid | 47.11 | 0.594 | 0.887 | 0.052 | [46.2, 102.4] |
| reference: spine-parked-j2-3r converged plain chain | 6915 tries, same family | 28.49 | 0.663 | 0.876 | 0.024 | [~43, ~104] |

* The loop beats the converged plain chain by **1.6 fast points** (26.86 vs 28.49) and its own locked control at the
  same seats by 20 (47.11: those seats are tuned for the loop). Reach 0.700 vs 0.663, in-band 0.843 vs 0.876: the
  loop buys ~6 workspace poses at the low end of the window and pays ~3 in-band points for the rocker and pin Q.
* CMA D per-member in band: hub 1 1.00, hub 2 1.00, hub 3 0.88, pin P 1.00, knee K 0.95, pin Q 1.00, link 1 0.99,
  P plate 0.99, L2a 0.97, **rocker 0.41**, **L2b strap 0.69, L2b tail 0.69**, neck 0.82. Posts made honest: pin P
  +9.6 mm (the rocker leaves P above hub 2's crown), knee K +4.9, pin Q +3.5, hub 3 +4.0. Mass 118 g Ti.
* Lost poses (CMA D, 160 ws): fold 40, K6 6 (all neck vs the L2b strap: the strap crosses the neck near hub 3 in
  overhead / cross-body poses #104, #116, #152), contact 2. Overhead (elevation >= 140): 0 of 12 workspace poses; the
  5 overhead clip frames are followed (in-band 0.85).

## The measured limiter

1. **The dwell only moves the LOW end of the window.** The rocker shortens a2_eff (74.7 -> 70.9 at CMA D, 73.8 -> 61 at
   the seed) only on the folded side, so the window grows downward (46 -> 36 at the D seats) and the top end stays at
   a1 + a2 - 10 (102.5). On Bench(60,160) the demand theta = angle(J1, J3) spans p5-p95 23-131 deg: 21 workspace
   poses lie below the plain window and **23-25 above it**, untouched by any dwell on the folded side. On
   Bench(110,360): 59 below, **71 above** (seed: kinematic reach 0.639 -> 0.778, all from the low side).
2. **Every wider kinematic window found is unwearable.** A kinematic scan (1500 random loops per a2) reaches windows
   of [15, 110] (a2 73.8, kinematic reach 0.85), [11, 129] (a2 92, 0.92) and [11, 141] (a2 98, 0.95), i.e. the fold can
   be removed kinematically. On the bench these score 124-275: in-band 0.25-0.35, the pins, rocker and L2b float
   20-30 mm off the skin (hub 2 and the loop swing over the deltoid). Same frontier as the ideation's DP (a2_eff would
   have to run 22 -> 108 with hub 2 in band) and the pin knee's a1 study: the fold window and the band are coupled
   through hub 2's position, and a loop on link 2 does not decouple them.
3. **The rocker must cross hub 2.** Pin P sits 15-25 deg from J2 (farther and the rocker leaves the band), so the
   rocker passes over hub 2's 12.25 mm crown: rocker in band 0.08-0.41 across all bests, pin P's post 10-17 mm taller.
   A rocker that clears hub 2 laterally (>= 12.5 deg from J2 along its whole path) exists in only 55 of 25 000 random
   loops with a usable window (generated, not yet benched).
4. **Pin Q / L2b tail at the posterior axillary fold.** At the seed, pin Q is parked at F 80 by #93 / #92 / #115
   (ABER behind the frontal plane: requirement 108-119 mm) - in band 0.002. The CMA moved Q (alq -141, k 18.7) so it
   is 1.00 in band at D; the cost moved to the L2b strap / tail (0.69) and the neck crossing (6 K6 poses).

## Red team (own best, CMA D; Bench(60,160) fast)

* **The pose that jams.** No knee / loop jam: transmission angles stay >= 40.4 deg at Q and >= 22 deg at K over every
  taken pose (limits 30 / 20), 0 branch flips in the dense K2. The jam is part-part: the L2b strap vs the neck at 6
  poses (#104 elev 150, #116 elev 150, #152 elev 165 overhead; cross-body) - the strap crosses the neck near hub 3 and
  K6 drops the pose (over-raising it would cost every pose ~20 mm, measured: 126.39 at the seed).
* **The point that pinches.** min metal-skin 0.04 mm at ws #91 (plane -15, elevation 75, axial 90: flexion with
  external rotation, an underside face), 0.10 mm at #98 and #136; with metal < 1 mm counted as contact the gap is
  38.84 (lesson d). Crowns: 0 crown contact poses at D.
* **The optimistic number.** (i) 26.86 is a fit-bench number tuned by CMA to 160 workspace poses; the motion preview
  of the same configuration (docs/concepts/viz) leaves the window in 90 of 239 loop frames (across the body and
  overhead: the window top 102.5 deg is below the plain chain's 104.4 at the seed seats). (ii) The spherical four-pin
  loop is OVERCONSTRAINED in space (Kutzbach M = -3 with the wearer's GH, 6 redundant constraints vs the plain 3R's 3,
  tools/simplicity.py): four pins must meet at GH within the bearings' tilt play (MR63ZZ pair over a 6.5 mm stack:
  ~0.2 deg) or the loop binds - nothing on the bench models it. The generic fix is a rocker with one spherical end and
  one U end (spatial M = 1 for any axis error: e.g. a GE4E spherical plain bearing, O12 x 5, at P on link 1 where pin P
  sits 1.00 in band, and a cross pin at Q), which costs ~3 mm of post at P (not modelled). (iii) For MVP2 the knee and
  pins carry J2's torque split through the loop (rocker = two-force member): not sized here.

## Mechanism record (docs/SIMPLICITY.md)

3 active pins (J1 O20, J2 / J3 O15, MR117-2RS pairs), 3 passive pins (P, K, Q: MR63ZZ pairs, O10 bosses), 0 passive
translations, 0 sensed passive, 0 springs; moving bodies link 1 (+ P plate), L2a, L2b (+ Q tail), rocker C, arm-end
(hub-3 plate + neck): 5; joints 6; 1 closed loop (spherical four-bar J2-K-Q-P); custom parts 12 (base, link 1, L2a,
L2b, rocker, arm-end neck, 3 hub shafts, 3 pin shafts), catalogue 12 (3 MR117 pairs + 3 MR63ZZ pairs).
Complexity **19.0** (tools/simplicity.py --score: 3 passive rotations 6, 1 loop 4, +2 bodies 2, +3 joints 3, +5 made
parts 2.5, +6 bought 1.5); Kutzbach M -3 (6 redundant: the spherical loop relies on axis concurrency).
