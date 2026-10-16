# closure-set-arc-knee-3r - hub 3 on a passive trunnion yoke whose tilt is set by the radial closure

Round 3 (2026-10-16). 3 active R + 3 passive R (knee trunnion, two cuff pins), **0 passive translations**.
Model: `docs/concepts/models/closure-set-arc-knee-3r.py` (on the osn model and its seed VModel checks).

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Write the closure equation of the knee
   in closed form before scanning it, to see WHEN the knee moves at all and what sets its stiffness (authority);
   find the regime where the knee is single-valued along real motion (track it at the full 10 fps, never "root
   nearest zero", and never let a pose take the root on the OTHER flank of the closure curve - that root is reached
   only through the closure's own fold); then price every new body (fork cheeks and arms round a tilting hub, an E arm
   that tilts with the yoke, the cuff link and pad bosses) at real size and check them against each other, because a
   tilting gimbal inside a 2-14 mm band is mostly a packaging problem. And compare with the obvious control: the same
   chain with the knee locked (= a zero-translation osn with a pin dyad instead of the 2 slides).
2. **Rawest material.** The posed render skin of each bench pose (signed distance per metal sample, fast grid; exact
   path for the frozen check), the six FIT clips at their full 10 fps (HG / RS in FI order, 356 frames) for root
   tracking and the continuity rule, the rest-pose skin mesh for the seat normals (osn seat code), and the GH
   translation sensitivity (R10) as the knee's conditioning number (deg of knee per mm of radial GH motion).
3. **Methods and tools.** Closed-form radial closure (below); spherical IK with a per-pose third axis RK(psi) u3
   (vectorised); 1 deg psi grid + linear root + exact re-evaluation (residual reported); planar RR dyad closure (law of
   cosines) for the pinned cuff; sphere tracing on the bench distance grid for every skin-facing underside (the seed
   VModel fit, greedy drop as contact); point / cylinder signed distances for part-part clearance (1 mm non-adjacent,
   0.15 mm adjacent); the cloud CPU farm (tools/cloud_run.py sweep) and tools/concept_cma.py for CMA-ES.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, metrics, contact rule as
   the 68.93 baseline), the osn / seed VModel checks inherited by subclassing (closure, jam rule, hub-strap and
   hub-hub clearance, fitted undersides), the frozen-shape protocol on Bench(110,360) exact (`frozen` mode in the
   model, the leader verifier's protocol), near-touch and the overhead split (`audit()` in the model), and the
   red-team list below.

## The closure in closed form (derived, then measured)

The pin dyad (J3, pin a, pin b, all parallel to u3) is a planar 3R in hub 3's plane: it takes the in-plane drift and
the in-plane rotation. The yoke must match the arm's u3 direction (2 equations) and the arm pad's height along u3
(1 equation: the RADIAL closure); unknowns q1, q2, psi. Writing the drift in the arm frame and dotting with u3, every
J3 and q3 term cancels and, **with J1's line through GH, the q1 terms cancel too**:

    F(q2, psi) = (hK + c3.u3)(cos psi - 1) + L sin psi + c2 . (R2(q2) - I) RK(psi) u3 - c0 = 0,
    L = c3 . (dK x u3)  (J3 line offset normal to the knee axis),   c2 = a point of J2's line.

So the knee is a **closure cam of the elbow: psi = g(q2)**, independent of q1, q3 and of the pose otherwise. With
c2 = d (cos chi m + sin chi n) normal to u2 (m toward u3, n = dK), the cam term is d sin a2 [cos(q2 - chi) - cos chi]:
a sinusoid of q2 whose phase chi is the direction of J2's line offset, and the J2 fold sits at fixed q2 (the two
coplanar postures). Consequences, each measured in `kin` mode (Bench(60,160), knee tracked at 10 fps):

* **J2 line through GH (osn leader subfamily, d = 0): the knee is inert** (psi = psi_rest at every pose, authority
  = L - hK sin psi only; at a level hub L ~ 5 mm/rad: 173 of 220 poses fail the 8 mm/rad conditioning rule). The
  catalogue's "judge reproduced 0.832" came from picking c0 per design and the root nearest 0 per pose.
* **The osn seats' own J2 offset (b2 > 0) points the cam the wrong way for most seats**: b2 0.3 -> 0.673 kin-ok,
  b2 0.6 -> 0.350 (leader locked fold-free 0.786).
* **An explicit cam (J2's line moved o2 mm off its seat line at angle chi2, new params o2 / chi2)** - and the FLANK
  RULE: F(psi) is a downward parabola in psi; a pose may only take the root on the rest root's flank (same sign of
  d F / d psi). The other flank is reached only through the closure fold (authority 0) - a branch the knee cannot
  take. Without this rule the scan's best cam read 0.841 kin-ok with 5 fold poses (chi2 180, o2 15, psi_rest 30); with
  it the same cam reads 0.377 (122 no-root). Every number below uses the flank rule.
* **Best honest cam in a 120-configuration kin scan** (nominal knee height, before the parts fit): o2 24.5, chi2 -79,
  psi_rest 25, b3 0.32 -> kin-ok 0.895 (ws 0.856, clip 1.000, elevation >= 140: 0.882), **0 J2-fold poses** (the
  leader: 47), 18 no-root (the closure's own fold), 4 dyad. The knee lever is real kinematically.

The cost is geometric and unavoidable: the knee axis sits at the hub, hK ~ 75-100 mm from GH, so a knee swing dpsi
moves hub 3 across the arm by ~hK sin(dpsi) - the dyad must absorb 70-90 mm of in-plane drift span for a 50-60 deg knee
range (measured at the cam anchors), and link 2's end pitches by the same angle about the trunnion line (the fork
ring 15 mm out lifts ~15 sin dpsi).

## Packaging (the parts, at real size)

Yoke = hub-3 housing (O20 x 12.25), fork cheeks 3 x 8 at +-(HUB_R + 0.25..3.25) along dK holding O4 trunnions (cheek
+-3 mm round the pin), fork half-ring at 15 mm joining the cheeks to link 2, E arm 8 x 3 strap + O10 eye, cuff link
8 x 3 with O10 eyes, arm pad O10 x 3 boss (arm-fixed). Three E-arm stackings, all modelled:

| E arm | where | cost measured |
|---|---|---|
| on hub 3's upper member (F + 3.15) | crosses the cheeks as J3 turns | fork-Earm 73 of 220 poses jam (leader seats, psi_rest 25) |
| over the cheek tops (`earm_over`) | F + toff + 4 | E arm 12 mm over the hub face |
| as hub 3's lower plate (`earm_under`, new) | F, cheeks at F + 7..13 | the dyad stack (pad 3 + cuff link 3 + gaps) lifts hub 3 itself: f3 +13 mm, hub 3 0 % in band; the tilting fork ring still reaches the E arm (32 jams) |

## Measured (Bench(60,160) fast, every model check on)

| configuration | gap | reach | follow | ib14 | ib10 | contact | notes |
|---|---|---|---|---|---|---|---|
| CONTROL knee locked (lock=1), leader seats, pin dyad lE 30 lc 25 | 31.32 | 0.706 | 0.967 | 0.792 | 0.380 | 0.012 | = the pin-knee family; fold 47 |
| coarse farm sweep, 253 knee configs (model v1: no flank rule, no cam) | best 76.84 | 0.563 | 0.817 | 0.644 | 0.298 | 0.041 | 45 no-root, 7 fold; 116 of 256 structurally invalid (pin b proximal / trunnion outside the housing) |
| best kin cam, full model, earm_over | 999 (79.44 before the pin-b rule) | 0.688 | 0.783 | 0.550 | 0.328 | 0.066 | knee refit to the real hub height (dh 20.6) brings 27 fold back; hub 2 lifted to 31.8 mm (0 % in band) by the 24 mm J2 line offset; pin b 10 mm proximal of hub 3 |

| CMA-ES local stream L (model v3: flank rule + cam, earm_over), 81 tries | **68.59** (k322) | 0.663 | 0.983 | 0.487 | 0.276 | 0.035 | o2 30 (cap), chi2 -72, psi_rest 19, b2 0.11, b3 0.17, lE 40 (cap), lc 37, beta0 114, dh 26.6 |

**Convergence gate (stream L, 81 tries): NOT converged** - +3.39 score points over the second half, +2.28 over the last
third, top-5 spread 2.06. Two parameters sit on their caps (o2 30 mm, lE 40 mm): the search wants a larger cam offset and
a longer E arm, i.e. more of exactly what costs proximity. Farm streams A-C (3 seeds, 1200 s each) were queued at
03:10 UTC behind ~110 jobs and write to `.cache/csak/cma{A,B,C}.json`; a v2-model cam sweep (no flank rule, so
optimistic) is also queued (`.cache/csak/cam_res.json`).

## Verdict (screened)

The closure-set arc knee is a **real kinematic lever and a proximity loss**. Closed form first: with J1 on a GH ray
the knee can only be moved by J2's line offset, and then it is a cam of the elbow q2; without that offset it is inert
(the catalogue's 0.832 / 0.836 came from per-pose root picking across both flanks). With an explicit J2 offset in the
fold plane and only rest-flank roots, the J2 fold disappears in the kinematics (0 of 220 poses vs the leader's 47,
overhead 0.88 closable). But every degree of knee moves hub 3 ~1.4 mm across the arm (hK ~ 80 mm), the pin dyad has to
absorb 70-90 mm of drift span over a curved arm, the fork ring pitches with link 2, and the cam offset lifts hub 2
out of band. Best honest 68.59 vs 31.32 for the identical chain with the knee locked: **the knee costs ~37 gap points
more than it buys.** Passive translations 0, so it would win ties - it is nowhere near a tie.

**What would remove the measured limiter (next lever, not tried in the time box):** source the cam offset from a
TILT of J2's axis about hub 2's own seat point (the hub stays on the skin; today the line is translated and the hub
follows it off the shoulder), and pick seats whose drift direction dK x u3 lies along the humerus (a flat dyad stays in
band along the arm, not around it). Upper bound on that lever: hub 2 back in band recovers at most its share of the
samples; the dyad / fork proximity loss stays - it does not reach the control's 31.

## Red team (own best)

* **Flank jump (fixed, measured):** root picking without the flank rule reported 0.841 kin-ok at a cam that is really
  0.377 - 122 poses take the other flank's root, reachable only through the closure fold. Built in as a rule.
* **Knee height:** a kin scan at a nominal knee height is optimistic; refitting the trunnion into hub 3's real housing
  (dh 8 -> 20-27 mm) brought 27 J2-fold poses back at the scan's best cam. Every reported number is refit.
* **E arm vs fork:** on hub 3's upper member the E arm crosses the cheeks (73 of 220 poses jam); under the housing
  the dyad stack lifts hub 3 out of band and the tilting fork ring still reaches it (32 jams); only over the cheek
  tops (12 mm above the hub face) is it clean - the in-band cost is part of every number above.
* **Pin b:** a pinned cuff whose pad sits proximal of hub 3 is not a cuff; configs with pin b < 20 mm distal score
  500+ (graded, never valid).
* **R10:** the knee is closure-set, so a radial GH translation moves it: at the bests 0.8-1.1 deg per mm (authority
  54-76 mm/rad); 15 mm worst rigid GH translation = 12-17 deg of knee - a jam risk near the closure fold.
* **Frozen Bench(110,360) exact** (lesson c), the 77.92 shape fitted on Bench(60,160) fast and worn without refit:
  **89.44** (reach 0.542, follow 0.873, ib14 0.535, ib10 0.365, contact 0.094); the new poses fail on the dyad's elbow
  range (78) and the closure fold (59) - the cuff dyad and the cam were tuned to the 160 workspace poses (lesson c
  again). Near-touch: 0.09 mm (exact) / 0.48 mm (fast); counting metal < 1 mm as contact: 92.38 / 80.39, < 2 mm:
  100.63 / 89.07. Overhead (elevation >= 140, exact): reach 0.39, follow 0.40, ib14 0.48 (15 contact poses) - the
  overhead does not hold. The 68.59 shape was not frozen-checked inside the time box.

## Verification (adversarial verifier, 2026-10-16) - REFUTED

Harness: `docs/concepts/verify/closure-set-arc-knee-3r.py` (result `docs/concepts/verify/closure-set-arc-knee-3r_big_frozen.json`).
The claimed best k322 is reproduced exactly on Bench(60,160) fast (68.59). The protocol was the frozen shape: fit on
Bench(60,160) fast with the trunnion refit to dh 26.59, then worn without refit on Bench(110,360) on the exact path.

| | gap | reach | follow | ib14 | ib10 | contact |
|---|---|---|---|---|---|---|
| claim, Bench(60,160) fast | 68.59 | 0.663 | 0.983 | 0.487 | 0.276 | 0.035 |
| **verified, Bench(110,360) exact, frozen, verifier checks** | **75.28** | 0.589 | 0.991 | 0.486 | 0.277 | 0.027 |
| champion, same bench, protocol and seed VModel / outer-face checks (osn verifier) | 66.97 | 0.700 | 0.918 | 0.575 | 0.356 | 0.113 |

The champion was measured by the osn verifier through the same seed VModel checks, outer-face audit and frozen
protocol that this harness uses. Under the risley-turret verifier's kit checks the champion scores 75.94. The verified
75.28 is 8.3 gap points worse than the champion under equal checks, so the claim is refuted.

What the verifier checked:
* **DOF (R5 / R17):** there are 3 active joints (J1, J2, J3). The knee and the two cuff pins are passive rotations set by
  the closure: the radial closure sets psi and the planar 3R dyad sets the pins. There are 0 passive translations and no
  undetermined coordinate in the rigid model. Caveat: the knee is only weakly determined. Conditioning is 0.84 deg per mm
  (p50) and 2.04 deg per mm (p95) of radial cuff or GH motion, so the <= 3 mm the rules give to the liner leaves the knee
  free by ~2.5 deg (p50) to ~6 deg (p95). It would sag inside the liner compliance. This was not scored, but it is an
  R10/R17 risk.
* **Strict knee tracking (added check):** the model resets its tracking reference after a no-root frame and continues
  on the jumped branch after a rejected jump. The verifier keeps the last followed state as the reference instead. At
  k322 this removed 0 frames and gave 0 different roots: at this configuration the leak is not exploited.
* **Outer faces (added check):** the strap tops of links 1 and 2 were checked against the skin, with 0 contact poses
  (lowest 2.66 mm). The model already checks hub walls and crowns, dyad tops and fork walls. Hub seats are 50, 110 and
  88 mm from GH, all within 140 mm.
* **Bench artefact (lesson c):** fast to exact with the shape frozen costs 6.7 gap points. Reach falls 0.663 -> 0.589
  on the new poses. Poses not taken: 72 no-root (the closure's own fold), 51 dyad elbow out of range, 15 J2 fold,
  9 contact, 1 parts (E arm vs cuff link).
* **Near-touch:** the minimum metal-to-skin distance is 0.10 mm. Counting metal < 1 mm as contact gives 78.18 (5 poses);
  < 2 mm gives 87.78 (21 poses).
* **Overhead (elevation >= 140):** reach 0.50 (28 workspace poses, of which 9 no-root and 3 fold), follow 1.00
  (10 clip frames), ib14 0.54, ib10 0.37, 2 contact poses.

Verdict: refuted on the number. The number is honest and the part sizes, closure and DOF are sound, but the
mechanism is worse than the zero-passive champion under the same checks. The knee-locked control (31.32 fast) remains
this family's best lead, and it has not been verified.
