# closure-set-arc-knee-3r - hub 3 on a passive trunnion yoke whose tilt is set by the radial closure

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Write the closure equation of the knee
   in closed form before scanning it, to see WHEN the knee moves at all and what sets its stiffness (authority);
   find the regime where the knee is single-valued along real motion (track it at the full 10 fps, never "root
   nearest zero"); then price every new body (fork cheeks and arms round a tilting hub, an E arm that tilts with the
   yoke, the cuff link and pad bosses) at real size and check them against each other, because a tilting gimbal
   inside a 2-14 mm band is mostly a packaging problem. And compare with the obvious control: the same chain with the
   knee locked (= a zero-translation osn with a pin dyad instead of the 2 slides).
2. **Rawest material.** The posed render skin of each bench pose (signed distance per metal sample, fast grid; exact
   path for the frozen check), the six FIT clips at their full 10 fps (pose file: HG / RS in FI order, 356 frames) for
   root tracking and the continuity rule, the rest-pose skin mesh for the seat normals (osn seat code), and the GH
   translation sources (judge/base_stage.py) only as the R10 input to the knee's conditioning number.
3. **Methods and tools.** Closed-form radial closure rad(psi) = c3 . RK(psi) u3 + hK (cos psi - 1) + t2(q(psi)) . w;
   spherical IK with a per-pose third axis RK(psi) u3 (vectorised, no iteration) on a 1 deg psi grid + linear root +
   exact re-evaluation (residual reported); planar RR dyad closure (law of cosines) for the pinned cuff; sphere
   tracing on the bench distance grid for every skin-facing underside (the seed VModel's fit, greedy drop as contact);
   signed-distance cylinders / point clouds for part-part clearance (1 mm non-adjacent, 0.15 mm adjacent); the cloud
   CPU farm for the coarse sweep and CMA-ES rounds.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses, metrics, contact rule as
   the 68.93 baseline), the osn / seed VModel checks inherited by subclassing (closure, jam rule, hub-strap and
   hub-hub clearance, fitted undersides), the round-3 adversarial verifier (docs/concepts/verify/offset-skin-normal-3r.py
   style: frozen shape on Bench(110,360) exact, near-touch, overhead split), and the red-team list below.

## What the closure actually does (derived, then measured)

The pin dyad (J3, pin a, pin b all parallel to u3) is a planar 3R in hub 3's plane: it takes the in-plane drift and
the in-plane rotation. The yoke must match the arm's u3 direction (2 equations) and the arm pad's height along u3
(1 equation: the RADIAL closure); unknowns q1, q2, psi. With J1, J2 lines through GH (t2 = 0):

    rad(psi) = c3 . RK(psi) u3 + hK (cos psi - 1)          (no pose dependence)

so **psi is a constant on the osn leader's exact subfamily (b1 = b2 = 0): the knee is inert there**, and on any
seats the knee only moves through the J1/J2 line offsets (b1, b2 > 0) - the very drift the 2-slide proof forbids.
rad(psi) is a downward parabola (curvature hK, peak near psi = 0 for small c3): the authority |d rad / d psi| is
about c3 . (dK x u3) + hK sin psi, i.e. ~5 mm/rad at a level hub on the snh seats (c3 = 6.8 mm) and 27-33 mm/rad only
on a flank (pre-tilt psi_rest ~ +-25 deg). A pose whose radial drift lifts c0 above the parabola's peak has NO root
(the knee hits its closure fold - the "branch jump" of the prototype is the root vanishing at the peak and reappearing
on the other flank).

Measured (snh k722 seats, Bench(60,160), `kin` mode, knee tracked at 10 fps, all kinematic checks, no parts):

| knee | fold-free and closable (all / ws / clip) | notes |
|---|---|---|
| locked at psi 0 (plain 3R arcs) | 0.768 fold-free / 0.681 / 1.000 | radial drift span 16.7 mm - a locked knee does not close |
| closure-set, psi_rest 0 | 0.027 | 181 of 220 poses: no root (peak below c0), authority ~5 mm/rad |
| closure-set, psi_rest +25 | 0.550 / 0.463 / 0.783 | 79 no root, 13 fold; tracked 10 fps: 3 jumps > 25 deg, 22 > 10 deg in 293 pairs |
| closure-set, psi_rest -25 | 0.159 | 112 dyad out of range, 44 no root |

The prototype's 0.832 picked c0 per design over all poses and the root nearest psi 0 per pose (both flanks, branch
jumps allowed); tracked continuously, the same lever is worth less than the locked knee's fold-free share.

(Sweep, best configuration, red team and verdict: below, filled as measured.)
