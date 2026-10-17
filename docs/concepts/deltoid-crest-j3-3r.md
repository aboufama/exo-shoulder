# deltoid-crest-j3-3r - Deltoid-crest J3 equal-arc 3R, re-measured at O20 / fold margin 5 (closing screen)

Round-4 pick, carried to round 14 as "a closing screen on the jump judge's forwarded O20 numbers ... doubles as lens 3's
no-knee control" (docs/concepts/ROUNDS.md, round 14 plan) and as the seed of lens plain-crest-j3-cap.

## Deeper version (answered before building)

1. **What a top mechanism designer would do that the spec does not ask for.** Not re-tune the seed: at O20 a spherical
   3R's hub 2 is ONE disc at ONE radius on an axis the closure moves, so the designer treats the spread of the J2-ray
   skin exits over the taken poses as the design objective, not a by-product, and reads the crest basin's fate from it
   directly (hub-2 level and in-band per config, and which poses set the level). They would open every free choice the
   class has at zero complexity - both branches, both stack orders at J2 and J3 (the inverted J3 stack is the spec's
   ask, but it is a variable, not a given), the underside quantile and the strap end hold - and search the basin
   globally (Sobol) before any local CMA, so a "basin" is not just the neighbourhood of a seed. They would drop the
   spec's base stub under link 1: the user ruled (CAD ruling 1, 2026-10-16) that the scapula handler carries the base
   directly at the J1 hub ring, so no base tab crosses link 1's annulus. And they would attribute every lost pose
   (fold folded / stretched, part-part, contact by member) before calling anything dead.
2. **Rawest material.** The posed render skin of every bench pose (concept_bench `B.skin(i)`, the rig's skin, signed
   distance by libigl on the exact path), the fit-clip frames (held-out Wave / Walking never loaded), the skin-motion
   map pipeline/conformal/analysis/skin_motion_map_14.json and the proximity atlas (docs/research/proximity_atlas.md:
   a rigid part must clear the highest skin it ever passes over) - not the round-4 digest's numbers, which were O15 /
   margin 10.
3. **Methods and tools.** The shared kit K1-K7 (closure, dense K2 continuity, K3 march, K4 O20 hubs, K5 straps with the
   60 deg climb, K6 at 1 mm radial, K7 neck) through docs/concepts/models/zc-frontier-3r.py's build UNCHANGED, whose
   objective already carries the spine-parked verifier's top_check (top faces, crowns and walls skin-checked,
   near-touch over all faces, closure residual, hub-axis accessibility F <= 140 mm); a Sobol coarse sweep over the
   crest box x branch x stack orders, then CMA-ES (tools/concept_cma.py) from the top configurations to the convergence
   gate; then the frozen-shape wear on Bench(110,360) exact (fit Bench(60,160) fast, every level frozen) with the
   per-pose loss attribution (zc-frontier-3r's `attribute`).
4. **What, other than me, shows the number is right.** The bench (the objective IS the verifier's plain gap with the
   top-face / crown checks, so a config cannot buy points by a face the verifier would reject), the frozen exact wear
   on the 360-pose verification bench, and a red-team pose list fixed before the search: overhead (elev >= 140),
   across the body (plane >= 100, elev >= 40), behind the back, the cap pole's binders (-75, 60, +60), (0..30, 150, 0),
   (0, 105, 0) and the crest binders the jump judge forwarded (30, 149, -59), (30, 124, -54), (30, 135, -45).

## Model

docs/concepts/models/deltoid-crest-j3-3r.py = zc-frontier-3r's build and checks with the search restricted to the
crest basin (clamped box): J1 bvec(az 30-120, el 48-80) inside ruling 4 (acromion top / cap pole; front / clavicle
seats rejected by `seat_ok`), J3 wdir(wd 95-120, wa -20..+20) - the deltoid crest, 10-35 deg higher on the arm than the
leaders' wd 82-86 -, arcs a1 34-64 / a2 38-70 (the spec's near-equal 45 / 50 inside), branch +-1, inv2 / inv3 0 / 1,
q 0.85-1.0, end_extra 0-6. Every part at its real size: three O20 v5 hubs (MR117-2RS pair, 12.25 mm stack), 12 x 3 Ti
straps, K7 14 x 6 neck to BOTTOM's bar. 3 active joints, 0 passive joints, 0 passive translations, complexity 0. MVP1:
no gears, pulleys or cables; every coordinate set by the three joints (nothing to sag).

Spec corrections (measured or ruled): O15 hubs -> O20 (ruling 2, "Keep O20 only"); fold margin 10 -> 5 (ruling 1); the
base stub under link 1 is not a part (CAD ruling 1: the handler carries the base at the J1 hub ring).

## Screen (2026-10-17, local, niced, <= 2 processes; farm closed)

Bench(60,160) fast, objective = the verifier's plain gap (zc-frontier checks). Sweep file:
docs/concepts/sweeps/deltoid-crest-j3-3r.json (every configuration in evaluation order, phase-tagged).

| step | configs | best gap (score) | reach / follow / ib14 / contact | where |
|---|---|---|---|---|
| seed A at O20 / margin 5 (round-4 26.35 at O15 / margin 10) | 1 | 71.21 (74.11) | 0.663 / 0.867 / 0.568 / 0.060 | hub 2 0.04 in band at F 76 mm |
| seed B | 1 | 69.65 | 0.681 / 0.883 / 0.542 / 0.053 | hub 2 0.03 at 78 mm |
| cap-pole crest cell bvec(55, 62) / wdir(98, 5) 50/58 (judge 62.80) | 1 | 60.39 | 0.756 / 0.883 / 0.545 / 0.039 | hub 2 0.00 at 94 mm |
| Sobol over the crest box x branch x inv2 x inv3 | 493 | 48.05 | 0.644 / 0.833 / 0.842 / 0.050 | short a1 38.9, inv2 1 / inv3 1 |
| CMA s1 from the Sobol best (sigma 0.5) | 441 | 39.94 (85.48) | 0.644 / 0.867 / 0.871 / 0.031 | a1 36.6 / a2 53.5, wd 102.0 |
| CMA s2 from the long-a1 cap basin (Sobol #2, 57.43) | 369 | 44.62 | 0.631 / 0.917 / 0.822 / 0.066 | pinned at the box edges a1 64, el 79 |
| CMA s3 from s1's best (sigma 0.3) | 289 | **37.90 (86.22)** | 0.656 / 0.867 / 0.879 / 0.031 | a1 38.1 / a2 51.5, wd 103.1 |

**Best (fast, Bench(60,160)): gap 37.90, score 86.22**, near-touch gap 69.09; J1 bvec(103.49, 65.82) (acromion top),
J3 wdir(103.08, -7.03) (crest), a1 38.12 / a2 51.49, branch -1, inv2 1 (link 1 on hub 2's cap plate, bridging over link
2), inv3 1 (inverted J3 stack), q 0.943, end_extra 3.0. Hub levels F 50.0 / 59.6 / 62.0 mm; in band per member hub 1
0.99, hub 2 1.00, hub 3 0.95, link 2 0.99, link 1 0.60, neck 0.87. 3 active, 0 passive, complexity 0.

### The basin's premise does not hold at O20 (measured over the 1227 honest configurations of the sweep)

| a1 (deg) | n | hub 2 in band (median) | hub 2 level F (median) | reach (median) | best gap |
|---|---|---|---|---|---|
| 34-40 | 506 | 0.95 | 61 mm | 0.637 | 37.90 |
| 40-46 | 110 | 0.07 | 69 mm | 0.600 | 49.76 |
| 46-52 (the spec's equal arcs) | 90 | 0.03 | 80 mm | 0.600 | 60.39 |
| 52-58 | 80 | 0.02 | 83 mm | 0.619 | 69.52 |
| 58-64 (cap pole, long a1 / short a2) | 441 | 0.76 | 67 mm | 0.631 | 44.62 |

| J3 seat wd (deg) | n | best gap | reach (median) |
|---|---|---|---|
| 95-100 | 356 | 40.30 | 0.637 |
| 100-105 | 603 | 37.90 | 0.637 |
| 105-110 | 108 | 45.19 | 0.606 |
| 110-115 | 82 | 60.39 | 0.581 |
| 115-120 | 78 | 77.06 | 0.562 |

* The round-4 basin (equal arcs 45 / 50, hub 2 0.82-0.997 in band) was an O15 / margin-10 artefact: at O20 / margin 5
  the equal arcs park hub 2 at 69-83 mm and 0.02-0.07 in band. Hub 2 lives in band only with a short first arc
  (a1 34-40: F ~60 mm, 0.95) - which is exactly the zc-frontier slice (a1 38 -> hub 2 1.00 at 60 mm; a1 46 -> 0.90 at
  64; a1 54 -> 0.06 at 86) - or at the cap pole with a long a1 / short a2 (0.76).
* The crest itself is a penalty: the best gap rises monotonically with the J3 seat above wd ~100 (37.90 -> 45.19 ->
  60.39 -> 77.06), and the global zero-complexity optimum (zc-frontier-3r, 15394 evaluations, all seats) sits BELOW the
  crest at wdir(85.7, -16.2) with 28.85 fast / 31.04 frozen exact. CMA s1 / s3 walked wd 105 -> 102-103 and s2 pinned
  at the box edges: the gradient points out of the morphology.
