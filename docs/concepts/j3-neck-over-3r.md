# j3-neck-over-3r - the inverted J3 stack, screened as the J3 side of the knuckle chain

Round-6 lens 3 (j3-side-band). Standalone, this morphology is a complexity-0 spherical 3R inside the verified zc ceiling
(31.04; the GPU search covered all four J2 / J3 stack orders), so the lead asked to screen it ONLY as the J3 side of
minarc variant A (plain spherical chain + spring knuckle K in link 1, complexity 13.5), whose in-band loss sits on the
J3 side alone: link 2 0.43, hub 3 0.70 (F 101 mm), neck 0.68.

Model: `docs/concepts/models/j3-neck-over-3r.py` (variant A kit rule `minarc-stop-knuckle-4r-a-kitrule.py` loaded
unchanged; only `build()` changes the J3 stack order, `lay` 1 = neck over link 2, `lay` 0 = variant A's order as the
control). Sweep: `docs/concepts/sweeps/j3-neck-over-3r.json`. Row: `docs/concepts/rows/j3-neck-over-3r.json`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Ask first WHY the J3 side is out of band before choosing a stack order. A stack order only moves 3.15 mm of
     metal between link 2 and the neck where they cross; it cannot fix a hub whose plate sits tilted on the arm.
     So: decompose hub 3's level into its per-pose requirement (median vs worst pose) and measure the plate's
     obliquity on the arm skin, then decide which lever can act.
   - Run the stack order as a paired control at identical seats and metal (lay 0 vs lay 1), so the stack's gain is
     measured, not assumed (the rail-elbow lesson).
   - Search the stack order TOGETHER with the J3 seat, because the seat sets hub 3's level and link 2's path
     (the lead's lens: deltoid-crest seats, q, neck width), and keep the knuckle's reach in the same objective
     (near-touch gap) so that band is never bought by giving the fold back.
2. **Rawest material.** The posed skin itself (the bench's signed-distance grids: the fast cache on Bench(60,160),
   the exact libigl path on Bench(110,360)), the fit motion clips and the workspace pose grid; the per-pose,
   per-sample march requirement of hub 3, link 2 and the neck (`K.requirement`), not the digested in-band
   fractions. Held-out clips never loaded.
3. **Methods and tools.** The kit (K1 closure, K2 dense continuity on J1 / K / J2 / J3, K3 march, K4 flat O20 hubs,
   K5 straps with 60-deg climb, K6 collisions, K7 neck) through minarc variant A's kit-rule model (stops in the J1-J3
   metric at >= 5 deg, physical q2 stop, hub K's +6 mm clock-spring cap, near-touch objective); a Latin-hypercube
   coarse sweep and CMA-ES streams (tools/concept_cma.py) on the cloud CPU farm; the frozen protocol (fit
   Bench(60,160) fast, wear Bench(110,360) exact) with the continuity flood fill.
4. **What, other than me, shows the number is right.** The bench report (honest flag, audit), the paired lay-0 control
   at the same seats, the frozen Bench(110,360) exact wear, the red-team pose list (the poses that set hub 3's level,
   the nearest-metal poses, overhead / across-body / behind-back), and the next stage's independent verifier.
