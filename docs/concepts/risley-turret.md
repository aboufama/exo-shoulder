# Risley turret: J1 and J2 as two overlapping flat ring bearings on top of the scapula

Model: `docs/concepts/models/risley-turret.py` (shared kit, `tools/concept_kit.py`). Sweep:
`docs/concepts/sweeps/risley-turret.json`. Row: `docs/concepts/rows/risley-turret.json`.

## Deeper version (answered before the work)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the two rings as ONE body problem:
   L1 is J1's upper race and J2's lower race, so machine them as one figure-8 race body bolted in the overlap lens
   instead of adding a plate; set the J2 ring's height from the exact stack geometry over J1 (not a fixed 16 mm);
   pick the ring bore/section from the skin curvature under the cap (a flat annulus on a 50 mm cap stands off by its
   sagitta, ~6 mm at r 24, so a thinner annulus is closer); and check the closure band first, because a 3R with a
   40 deg first link cannot close sep > A1 + A2 - margin at all: overhead and across-body need the band to contain the
   whole sep range or the turret is dead whatever the proximity.
2. **Rawest material.** The posed skin itself (the bench's signed-distance grid of every pose, marched per sample,
   not an envelope summary), the six fit clips frame by frame for continuity, the workspace poses for reach, and the
   per-pose scapula/humerus frames from the pose file (not the catalogue's quoted 91 % / 59 % closure shares, which I
   re-measure).
3. **Methods and tools.** Spherical-3R two-circle closure (K1) vectorised over all poses, flat-plate K4 fits of each
   ring along its own axis (every annulus sample marched from its true offset), a closed-form stack solve for ring 2
   over ring 1, K3 skin-fitted strap with the 60 deg climb limit, dense K2 continuity along interpolated motion,
   K6 part-part collisions, and a coarse-then-refined grid sweep over the parameters that move the band (A1, A2, W0,
   b, branch, margin, quantile).
4. **What, other than me, shows the number is right.** `tools/concept_bench.py` through the kit (march, dense
   continuity, collisions, audit -> `honest`), the adversarial verifier re-running the model on the exact path, the
   baseline row reproduced by the same kit (68.93), and a red-team pose list (overhead, across-body, behind-back,
   the jam pose and the pinch point) reported below with numbers.

## Result (Bench(60, 160), fast grid cache, kit `march` + dense K2 + K6, audit clean: `honest`)

| configuration | gap | reach | follow | in-band 14 | in-band 10 | contact | J1 / J2 level |
|---|---|---|---|---|---|---|---|
| spec start (b 32.55/80.56, W0 71.38/4.78, A1 40, A2 75, q 1.0) | 94.73 | 0.650 | 0.900 | 0.253 | 0.135 | 0.000 | 55 / 145 mm |
| best two-ring turret (k62: b 90/75, W0 71.38/4.78, A1 45, A2 75, q 0.95) | 75.79 | 0.719 | 0.917 | 0.467 | 0.324 | 0.110 | 48 / 82.5 mm |
| **best: J1 ring + J2 O20 hub (k42, same axes)** | **63.17** | 0.731 | 0.917 | **0.570** | 0.397 | 0.0995 | 48 / 72 mm |
| champion spherical 3R (rows/baseline-3r.json; 70.27 on the same kit checks) | 68.93 | 0.775 | 1.000 | 0.438 | 0.279 | 0.102 | |

66 configurations (`docs/concepts/sweeps/risley-turret.json`, in order): spec start, a kinematic + skin proxy pick of
24 axis sets, a focused grid on b / A1 / A2 / branch, then the J2-hub variant and two local refinements. Best per
member (k42): J1 ring 93.3 % in band, J2 hub 5.7 %, link 2 43.5 %, J3 hub 54.4 %, neck 79.2 %, L1 bridge 0 %
(it hangs between the J1 lug at 54 mm and the J2 hub at 72 mm). Ti mass 115 g (132 g with 5.5 mm straps). Closure
residual 0.0 deg, minimum band margin 5.09 deg, 0 flips, 0 collisions; min angle(p2, arm) 36.6 deg.

**What the morphology taught (new knowledge, predicts beyond it):**

1. *A flat ring bearing about a scapula-fixed axis near the top of the scapula is the closest-riding joint measured
   so far*: 93 % of its samples 2-14 mm from the skin at r 15-24 (b = bvec(90, 75)), 99.7 % at r 12-18. The S-frame
   skin requirement map over all 220 bench poses explains it: directions with el >= 70 deg (and el 50-60 at az 0-90)
   need 41-57 mm in EVERY pose (24.8 % of the S sphere). Any design can put its J1 there.
2. *Every spherical 3R needs its shorter link >= 38-43 deg, whatever its axes*: the closure band
   [|A2 - A1|, A1 + A2] has half-width min(A1, A2), and the smallest spread of angle(b, W) over the bench poses for
   ANY scapula-fixed b and humerus-fixed W (468 b x 600 W on a 10 x 5 deg / 7.5 x 15 deg grid) has half-width 37.4 deg (100 % of poses),
   32.6 deg (95 %), 29.1 deg (90 %); add the 5 deg singularity margin. The catalogue's "A1 30-45 keeps J2 on the cap"
   is therefore impossible: the spec's own start (A1 40) closes 72 % of poses.
3. *J2 cannot stay on stable skin*: a 40 / 45 / 50 deg circle around the best possible b keeps only 39 / 33 / 31 % of
   its points on skin that is <= 60 mm in every pose (67 / 54 / 44 % at the 95th percentile). So J2 floats, and a ring
   there (48 mm annulus) floats worse than an O20 hub: two-ring 75.79 vs ring + hub 63.17 on the same axes. The spec's
   claim "J2 stays >= 90 deg from the arm" is also wrong on this bench: 36.6-49.5 deg.

## Red team (best config, `python3 docs/concepts/models/risley-turret.py red`)

| pose class | n | taken | no closure (sep below / above the band) | contact |
|---|---|---|---|---|
| rest (elev < 40) | 85 | 96.5 % | 3 (0 / 3) | 0 |
| overhead (elev >= 120) | 41 | **39 %** | 13 (9 / 4) | 12 |
| across-body (plane >= 100) | 41 | 85.4 % | 6 (0 / 6) | 0 |
| behind-back (plane <= 0) | 52 | 76.9 % | 7 (0 / 7) | 5 |

- **Jam pose**: workspace elev 105, plane 120, axial -135 (reach across and up with internal rotation): angle(b, W) =
  150.5 deg vs the band [35, 115] - 35.5 deg outside; no 3R with A1 45 can take it. Overhead fails both ways (W
  swings within 35 deg of b: 9 poses).
- **Pinch points** (closest metal over the taken poses; the bench counts only < 0 mm as contact): link 2 touches at
  0.0 mm in a behind-back clip frame (elev 39, plane -80, axial 101); neck 0.23 mm (elev 30, plane 75, axial -135);
  J3 hub 0.36 mm overhead (elev 120); J2 hub 1.13 mm (elev 45, plane 0); J1 ring 1.31 mm (elev 105, plane 150). All
  come from q 0.95: the worst 5 % of poses per sample set the skin-fitted undersides, and the rest are contact poses
  (9.95 %). With q 1.0 nothing touches but J1 rises to 81 mm (a single extreme overhead pose, elev 165, bunches the
  skin under the top cap) and the gap is 91.49 - the top cap is stable for 95-97 % of poses, not all.
- Honesty: dense continuity on every joint axis incl. the rigid lug joins, K6 on (the link passes over J1, the
  bridge and the neck by >= 1 mm by construction), ring 2 / hub 2 stacked >= 1 mm over J1's footprint (solved in the
  ring pair's own frame, re-checked on the final fitted levels: `stack_ok`), every part sampled at 2 mm.

## Spec corrections (measured, said here so the verifier can check them)

- L1 is not a plate over the convex hull: at the stack level that keeps J2 >= 1 mm above J1 the two races overlap by
  only ~2 mm2 (the J2 plane is tilted A1 from J1's), so L1 is a 14 x 3 mm bridge strap between lugs on J1's upper
  race and J2's lower race (only rings with a >= 60 mm2 bolting lens would skip it; none did).
- The strap to W starts at a lug on the outer wall of J2's upper race (the rim toward W), not over the ring; the
  rigid lug joins are fake joints for K6 (exempt within 12 mm only) and are followed by K2.
- The catalogue's closure numbers (91 % clips / 59 % workspace) re-measure as 90 % / 65 % before continuity.

## Verdict

The two-ring turret is dead (best 75.79; ring 2 floats 80-150 mm because closure forces A1 >= ~40 deg). The
variant that removes that limiter - **J1 as a flat ring bearing on the scapula top cap, J2 and J3 as O20 hubs** - is
a spherical-3R subtype that beats the champion on the bench (63.17 vs 68.93; in-band 14 0.57 vs 0.44), so it is
worth a short GPU sweep (b, W0, A1, A2, ring radii, q; the J1 ring is not the limiter, J2's travel and overhead
closure are). Next lever for gap 0: overhead - 61 % of overhead poses fail (closure band or contact).

Sketch: `docs/concepts/img/risley-turret.png` (frontal view, rest and overhead, every metal sample by part).
