# pointer-cslide - the user's split: 2R pointer + shoulder-side wire-race C-slide

Model: `docs/concepts/models/pointer-cslide.py` (shared kit). Sweep: `docs/concepts/sweeps/pointer-cslide.json`.
Row: `docs/concepts/rows/pointer-cslide.json`. Bench(60, 160), fast grid cache, K3 march, K2 dense, K6 on.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Measure the twist travel the C-slide
   must carry *before* drawing it (the whole design lives or dies on it), on the workspace poses and not only on the
   clips; choose the pointer pole and the branch from the raw arm directions (both singular cones +-a1 and the J1 hub's
   own footprint must stay clear of the arm), let the band's window and radius be fitted on the posed skin rather than
   picked, and try the inversions the spec hides: rail on the arm (the shoe on link 2 - this is seed-2r-cring, dead at
   129.98) versus rail on link 2 (the spec), A1/A2 off 90 deg (the pointer generalised to a spherical 3R whose last
   axis is the humerus), a tilted twist axis, and a donut (KAA10) versus the O20 hub.
2. **Rawest material.** The posed skin of every bench pose through the bench's own signed-distance grid (the band and
   shoe radii are marched radially from the twist axis on that skin, pose by pose), the humerus/scapula rotations of
   the 60 fit-clip frames and 160 workspace poses (the shoe-angle distribution is computed from them, not taken from
   ring_travel.json), and the proximity atlas's frame finding (a part in a swing frame - no twist - sees the skin turn
   under it; docs/research/proximity_atlas.md).
3. **Methods and tools.** tools/concept_kit.py (K1 closure 90/90 = the pointer, K2 dense continuity on values and axes,
   K3 march, K4 hubs, K5 straps, K6 collisions, K7 neck), a radial Lipschitz march for the circular band and the shoe,
   the cloud CPU farm for every sweep (tools/cloud_run.py sweep), Sobol coarse sampling then CMA-ES (pycma) from the
   top configurations until the convergence gate passes.
4. **What shows the number is right besides me.** The bench (it scores the metal I hand it, contact by its own skin
   distance), the kit audit (sampling density, hub size, pose locality, honest flag), the adversarial verifier
   (re-runs the row's best params), and a red-team list: rest, overhead (abduction 150+), across-body (plane >= 110),
   behind-the-back (extension + internal rotation), the pose that ends the shoe's travel, the band's open side
   against the chest, and the J1 hub when the arm comes nearest to the pole.

## Kinematics as built (spec fixes in **bold**)

- J1 axis a1 = S-fixed `bvec(az, el)` (spec pole p* = [0.36, 0.72, 0.60] = bvec(120, 46)); J2 axis p2 = K1 closure with
  cones A1 = angle(a1, p2), A2 = angle(p2, d3) (90/90 = the spec: p2 = sigma unit(a1 x d3)); d3 = the GH-elbow line
  (band humerus frame -y), tilt optional. Pointing frame P = [p2 x d3, d3 x (p2 x d3), d3]; q3 = the arm-fixed shoe's
  angle in P. Singular cones |angle(a1, d3) - 0/180| < `sing` rejected.
- **The shoe's travel window is fitted on the bench poses** (the smallest arc holding a share `cov` of the closing poses),
  not the spec's 60-90 deg: measured with p*, the shoe must travel **165 deg for 90 % of all bench poses, 193 deg for
  95 %** (clips alone: 65 / 112 deg - the spec's 67-87 deg came from clips only).
- Band, shoe and neck: see the model docstring (2 + 6 + 2 stack, band skin face at rho + 2, shoe lip at rho).
