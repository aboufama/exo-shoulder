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
