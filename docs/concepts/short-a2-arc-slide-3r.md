# short-a2-arc-slide-3r: short-link-2 3R with a spring-returned GH-concentric arc slide under J3

Round 5 pick (lens round5:reseat-for-union). Model: `docs/concepts/models/short-a2-arc-slide-3r.py`.

## Status (2026-10-16 ~08:05 UTC)

| | gap | score | reach | follow | in-band 14 | in-band 10 | contact | note |
|---|---|---|---|---|---|---|---|---|
| **best, Bench(60,160) fast** (CMA stream 3, sweep k4179) | **29.38** | **89.3** | 0.744 | 1.000 | 0.779 | 0.392 | 0.017 | honest (march, K2 dense, K6, clean audit) |
| same, metal < 1 mm counted as contact (lesson d) | 53.76 | 80.5 | 0.675 | 0.883 | 0.770 | | 0.115 | the near-touch number: optimistic by ~24 |
| FROZEN exact Bench(110,360) (fit shape frozen, K6 1 mm) | FROZEN_GAP | | | | | | | FROZEN_NOTE |
| plain 3R at the same seats (spine-parked-j2-3r.py, a2 = a2h) | 46.24 | 83.2 | 0.631 | 0.933 | 0.742 | | 0.019 | control |
| this model, slide locked (a2max = a2h) | 48.93 | 82.2 | 0.631 | 0.867 | 0.807 | | 0.044 | control: the relay is worth ~17-20 points here |
| the spec's seed S1 in the kit (O20, margin 5) | 69.23 | 74.8 | 0.713 | 0.950 | 0.424 | 0.167 | 0.028 | proxy estimate was 14.13 |
| S2 seed (bilateral, as one-sided) | 78.44 | | 0.569 | 0.800 | 0.618 | | 0.021 | |

Passive translations 0; passive rotations 1 (the slot = a rotation about n through GH, sensed, spring-returned);
complexity 14.75 (tools/simplicity.py: 1 passive rotation, 1 sensed, 1 spring, 1 sliding pair, 1 body + 1 joint, parts).
Fold margin 5 (the user's 2026-10-16 ruling, `K.FOLD_MARGIN`); stops at m_stop 5. At margin 10 (CB_FOLD_MARGIN=10,
m_stop 10) the coarse leader drops 49.91 -> 71.49 (reach 0.73 -> 0.59).

## The model (what changed against the spec, and why)

- **The relay is statics, not a window.** J2's stops are physical DIHEDRALS (mu_lo / mu_hi at the margin with
  a2 = a2h). In mode B the slide opens to the smallest a2 with th(mu_hi, a2) = th (the constant-force spring's energy
  minimum); the J2 dihedral stays on its stop. The reachable top is th(mu_hi, a2max), not the window estimate
  a1 + a2max - m: 92.5 vs 93.7 deg at S1 (m 5). On the fold side (mode C) the stop is nearly useless when a2h < a1
  (th(mu_lo, a2) barely falls as a2 grows: 0 poses in mode C at the best config).
- **The carriage folded into hub 3's lower member** (carr_t 0, CMA picked it): a flat sole with the two shoulder
  screws in the slot, F3 = rail + 3 + 0.15 instead of the spec's +5. The keeper runs in an underside groove of the rail
  (flush underside: nothing hangs below the rail).
- **Rail plate** laid out at its real 14 mm width at r_lay <= the fitted slot radius (CMA `--rlay rail_t`; a rail laid
  out at a larger radius than it sits would be too short: the audit flags it), root skin-fitted, the slot zone ONE GH
  radius (a cap), the root's end ramped to the slot level (one plate).
- **Layout 1 won**: the rail plate is the UPPER member at J2 (over link 1, the template's link-2 convention), not the
  spec's "rail bolted under hub 2" (layout 0: link 1 then has to climb over the rail near hub 2).
- **Kit finding (K6 vs `over`)**: the kit's `over` measures the shared-joint exempt zone at the member's pre-climb
  radius while K6 measures it at the final one, so an upper member just past the 12-mm zone can sit inside the lower
  member (measured: 17 % of S1 poses jammed link 1 in the rail root, 0.54 mm). The model gives link 1 a spacer (lift1)
  and a longer end zone (l1_end), both searched >= 0. Worth a kit fix (raise `over` after the climb, or test both).
- **Partners of the slide**: hub 3's sole slides on the rail at the 0.15 mm running gap, over the slot zone AND the
  root's end (one plate): both are K6 partners of the slide (joint `Sc`, axis = hub 3 / carriage centre); without the
  root's partnership the 1-mm K6 of the frozen protocol flagged 95 % of poses (fixed before the frozen claim).
- **Continuity**: K2 dense with a2 x4 in q (a > 6 deg slide step per 2-deg sub-step is a jump), every axis incl. the
  slide axis n, and a flood fill over the raw 1432-pose workspace grid (8 sub-frames per 15-deg edge, slide step <= 5,
  J2 axis step <= 25): at the best config 119 relay edges, 0 relay jams, 0 islands (S1: 311 edges, 4 jams).
- **Statics (R17)**: in mode A the chain has a 1-DOF self-motion (a2 with the arm fixed). Its gravity generalised
  force (link 1 + hub 2 + rail, fitted masses) is <= 0.016 N m/rad against a 1.5 N constant-force spring at the slot
  radius (0.099 N m) + slot friction (mu 0.15: 0.004 N m): the spring holds the home stop in every mode-A pose. Felt
  switch force ~1 N at 100 mm on the arm.
- **Two variants built to remove the measured limiter** (`side`): side 1 puts the slot at the ROOT of a long link 2
  (carriage carries link 2b to hub 3 at its own level; bilateral travel): coarse best 45.30 (plain 3R at the same seats
  52.93), only 3 poses open the slide; side 2 puts hub 3 BESIDE the rail (carriage bridge to hub 3's upper flange, neck
  back to J3's lower member): hub 3 in band 0.86 but the rail beside it climbs to 95 mm (in band 0) - SIDE2_NOTE

## Search (all Bench(60,160) fast, farm; docs/concepts/sweeps/short-a2-arc-slide-3r.json, in order)

SEARCH_TABLE

## Red team (best config, Bench(60,160) fast; frozen numbers above)

- **Overhead (elev >= 140): workspace 0/12 taken**, clip frames 5/5. The lost overhead poses are hub 3 BURIED: its
  disc requirement at plane 0-30, elev 150 is 125-400 mm (the acromion / deltoid fold closes over the lateral deltoid
  seat), so K6 / contact; the relay is not what loses them. The seats (wd ~103, hub 3 slightly above horizontal) are
  the price of keeping the slot zone in band.
- **Across the body**: 23/36 (13 lost to the fold: th past th_top 87.8). **Behind the back** 14/19. Rest 5/5.
- **Near-touch**: min metal-skin 0.0 mm (pose ws plane 75 elev 30 axial -135); counting metal < 1 mm as contact the gap
  is 53.76 (contact 0.115, follow 0.883) - the q 0.96 underside leaves ~10 % of poses within 1 mm. The polish stream with
  the near-touch objective (near 1) is the answer to that number: NEAR_NOTE
- **Per part in band**: hub 1 0.99, hub 2 0.99, link 1 0.99, slot zone 0.82, rail root 0.79, neck 0.64, **hub 3 0.31**
  (F3 = 69.15 on the slot at 66: the sole stack), so hub 3 + the neck (J3's upper member) carry the in-band loss.
- **The slide**: opens on 13 of 220 poses (10 ws, 3 clip; p95 5.45 deg, max 5.45 = full travel). CMA shrank the travel
  (a2h 45.5 -> a2max 51.1) because every degree of travel lengthens the constant-radius slot past hub 3.
- **Jam / snap**: 0 relay jams on the raw grid; 3 non-relay jams (closure fails mid-edge).

## Limiter (measured)

The stack of the slide under hub 3: hub 3 rides the slot (F3 = slot radius + 3.15), so hub 3 is 0.31 in band vs 0.87
for a plain 3R at the same seats, and the neck (now J3's upper member) 0.64 vs 0.83; the slot zone itself must be ONE
radius over its whole travel. The CMA answered by shortening the travel to 5.6 deg, which caps what the relay can add
(reach 0.63 -> 0.74). Overhead workspace poses are lost to hub 3's seat being buried at elev 150, not to the fold.

## What next

VERDICT_NEXT

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the relay as a force-closed
   statics problem, not a kinematic window: with J2 on a PHYSICAL dihedral stop (a pin on a fixed angle), the slide
   extends to the spring's energy minimum, so the reachable th at full travel is th(mu_stop, a2max), not a1 + a2max - m
   (the judge's window estimate). Model the stop as a dihedral, measure the difference. (b) Fold the carriage into
   hub 3's lower member (a flat sole with two shoulder screws in the slot) to cut the +5 mm stack to +3.15, and keep
   the rail underside flush (keeper plate in an underside groove) so nothing hangs below the rail. (c) Check the
   self-motion statics: in mode A the chain J1-J2-slide-J3 has a 1-DOF self-motion; the spring preload must beat the
   gravity generalized force of link 1 + hub 2 + rail along it plus slot friction (R17), and the felt switch force is
   the spring moment at the slot radius. (d) Continuity on the RAW 1432-pose workspace grid, not only bench samples.
2. **Rawest material.** The posed skin itself through the bench's signed-distance grid (fast cache for the search, the
   exact libigl path for the claim), the raw workspace grid of 1432 poses (`concept_bench._poses_all`) for the flood
   fill, the 6 fit clips frame by frame (follow), the skin-motion map `pipeline/conformal/analysis/skin_motion_map_14.json`
   for where hub 3 / the rail tail sit, not the proposer's proxy numbers.
3. **Methods and tools.** `tools/concept_kit.py` (K1 closure with per-pose a2, K2 dense continuity on every axis and
   the slide, K3 march, K4 O20 hubs, K5 straps, K6 collisions at 1 mm by construction + check, K7 neck), a cap member
   for the constant-radius rail travel zone, the farm (`tools/cloud_run.py sweep`) for the coarse sweep and
   `tools/concept_cma.py` CMA-ES jobs until the convergence gate passes, then a frozen exact Bench(110,360) wear.
4. **What other than me shows the number is right.** The bench (the outside judge), the frozen exact Bench(110,360)
   wear, an independent verifier re-running the model with its own checks, and the red-team pose list in this doc
   (rest, overhead, across-body, behind-back, the jam edges of the flood fill, the near-touch poses).
