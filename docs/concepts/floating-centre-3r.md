# Floating-centre 3R (floating-centre-3r)

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the float as what it really is:
   a 3-P stage whose coordinates are *outputs* of the closure (c = GH), so it can never improve the plain-bench
   geometry (the rig has GH fixed in the scapula frame: the float sits at 0 and only adds metal). The designer would
   (a) measure the float's cost honestly on the plain bench (plate + XY stage + normal slide at real size under J1,
   link 1 forced over the stage, K6 on the stage volume), (b) measure its benefit only where it exists - under the
   handler-slip law - comparing it with the parent's cuff slides on the SAME chain, and (c) ask which side of the
   slip carries the in-band metal: if most in-band metal rides the arm skin (the arm-end hub zone), the float is the
   right place for the slide; if it rides the scapula skin, the cuff is. (d) Size the travel from the slip law's
   tangent / normal split along J1's axis instead of a round 12 / 4 mm.
2. **Rawest material.** The posed skin of every bench pose (B.skin / the signed-distance grid), the fit clips in time
   order (B.clip_order, dense slerp between frames for continuity), the slip law's per-axis error angles and the
   Seth-2016 lever (judge/base_slip.py, literature numbers, not a fit), and the arm-skin vertex set BP.ARMV to say
   which skin each metal sample rides. Not the digested in-band summaries of the champion.
3. **Methods and tools.** tools/concept_kit.py (K1 closure, K3 march, K4 flat O20 hubs, K5 straps, K6 collisions,
   K2 dense continuity, audit), the champion chain decoded with the kit's bvec / wdir, a kit-style evaluator that
   adds the per-pose slip offsets to the samples before the K3 fit (ray origins shifted, so undersides are fitted to
   the skin they actually meet), scipy cKDTree for the skin class.
4. **What, other than me, shows the number is right.** The bench's own report (gap_of), the kit audit (`honest`),
   the parent reproduced on the same code (template numbers 69.29 at q 0.95), the adversarial verifier, and a
   red-team pose list (rest, highest overhead, most across-body, mid behind-back, and the pose of largest slip)
   with per-member minimum gaps.
