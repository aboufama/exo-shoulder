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
