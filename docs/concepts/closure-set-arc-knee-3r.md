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

(CMA-ES, convergence gate, best configuration, frozen exact check and red team: below.)
