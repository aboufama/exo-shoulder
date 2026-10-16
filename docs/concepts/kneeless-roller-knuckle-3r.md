# kneeless-roller-knuckle-3r - the roller-flank knuckle with J3 on a GH ray and the pin knee deleted

Round 9, lens 3 (simplest drive). Status: modelling (this file grows as the screen runs).

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do here that the spec does not ask for.** (a) Prove the knee is dead before
   deleting it: with J1, J2 and J3 all on GH rays the chain is a pure spherical 3R about GH, member 3 rotates with the
   arm and the drift s = Q^T t3 is identically 0, so the knee angle must be constant to machine precision on every pose
   of every bench - assert it (ptp < 0.5 deg), never assume it. (b) Do not just glue the old knee plate on: the knee
   link sat one pin stack (tp + RUN ~ 2.5 mm) above the boss / pad; as one bracket it drops to the boss level, so the
   whole arm-end bracket gets a fresh height fit (it can sit lower = more in band 2-10, or meet the skin). (c) Re-seat
   J3 freely: with b3 0 the J3 seat (wd, wa) and the bracket outline (lE, phiE, lc, phib) are the only things that move
   hub 3 off the deltoid; the planform may even shorten the bracket to a single strap (lc -> small). (d) Count the
   real cost of rigid closure: the scapula handler's tracking error and the humeral-head translation that the knee used
   to absorb now go into the cuff liner - red-team it with a GH offset of 3 / 5 / 10 mm instead of trusting the bench.
2. **The rawest material.** The posed skin itself (pipeline/avg body + bench signed-distance grids in
   .cache/concept_bench, the exact libigl path for claims), the motion clips (data/raw split, Bench(60,160) fit clips and
   the Bench(110,360) / held-out poses), the skin-motion map pipeline/conformal/analysis/skin_motion_map_14.json for
   where hub 3 can sit on the lateral arm, and the proximity atlas data (docs/research/proximity_atlas.md tables) for the
   hub-3 obliquity ceiling on a GH ray - not the round summaries.
3. **Methods and tools.** The verified roller-flank model loaded unchanged (spherical cam synthesis per 0.25 deg of K,
   pressure angles, lift-off, cusp, arm / roller / lug clearances, drive-range truncation, kit fold rule, O20 stacks)
   via the round-9 wrapper (PA <= 43, roller stub head, 2 mm near-touch objective, workspace in-band); this file only
   forces b3 0, turns the knee into one rigid bracket and asserts it never moves. Search: coarse farm sweep, then
   CMA-ES (tools/concept_cma.py) on the farm from the top configs until the convergence gate passes; frozen exact
   Bench(110,360), held out, flood fill, per-part split, tools/simplicity.py.
4. **What, other than me, shows the number is right.** The bench (tools/concept_bench.py) is the judge; the frozen
   exact Bench(110,360) wear of the fit shape is the claim protocol; an adversarial verifier re-runs it; the red-team pose
   list (overhead axial -135 / 0, hub 3 over the deltoid crest, bracket into the chest at extreme internal rotation,
   GH offset 3 / 5 / 10 mm) and the alignment audit against the lead (sidecar-longdyad-knuckle-3r) look for the
   optimistic number.

## Mechanism (as modelled)

scapula handler -> J1 (ACTIVE R, O20, acromion top, GH ray) -> link 1a (with the conjugate flank lug) -> K (PASSIVE R,
O20 + clock-spring cap, stop A / drive stop B, slaved, never read) -> link 1b -> J2 (ACTIVE R, O20, GH ray) -> link 2 ->
J3 (ACTIVE R, O20, **axis on a GH ray, b3 0**) -> **one rigid Ti bracket** (hub 3's lower plate + the E run + the former
knee link, 3 mm Ti-6Al-4V, 8-10 wide, bent from line / arc sketches) -> arm pad on BOTTOM -> arm.
Drive loop (unchanged from the verified roller-flank row): hub-2 rim lobe -> bell crank (MR63ZZ pair on link 1b) ->
bent long arm -> MR63ZZ roller -> conjugate spherical flank on link 1a; K's clock spring keeps both cam pairs closed.
3 active DOF, passive rotations K + crank + roller (all determined: K by the lobe / flank, the crank by the lobe, the
roller spins), 0 passive translations, 0 sensed passive coordinates (the pin knee's two encoders are gone).

**Why the knee carries nothing (exact; asserted on every bench).** J1, J2 (b1 = b2 = 0) and J3 (b3 = 0) all lie on GH
rays: c3 = 0, so t3 = R12 (c3 - R3 c3) = 0 and the drift s = Q^T t3 = 0 on every pose. Member 3 is rigid with the arm;
the planar knee closure at s = 0 is its rest configuration. The model asserts ptp(knee angle) < 0.5 deg and |s| < 0.05 mm
on every pose (measured: 0.0000 deg, 0.0000 mm, c3 = 0.00000 mm on the seed, every coarse config and every CMA config).

**Model** (`docs/concepts/models/kneeless-roller-knuckle-3r.py`): the round-9 roller wrapper
(roller-longdyad-knuckle-3r.py: PA <= 43, the roller's stub head as metal, 2 mm near-touch objective, workspace in-band,
per-part contact split) and under it the verified roller-flank model, loaded unchanged; this file forces b3 0, drops the
knee window (a rigid bracket has no knee angle), re-samples the former knee link at the bracket level tr (it no longer
sits one pin stack - tp + RUN ~ 2.5 mm - above the boss / pad; re-fitted against the skin), 3 mm thick, rebuilds its
contact-only edges / top and its part-pair box at that level, drops knee-vs-E and pad-vs-E (one body), keeps the
bracket >= 0.15 mm off hub 3's cylinder (link 2's half turns over it) and >= 1 mm off every other part. Spec deviation
(stated): the 'lead' chain of the parent would force the frontload dyad; chain 'free' with bk2 34-48 is used so the
roller row's own dyad (27.7 / 35.7) is the start point. PA_MAX is the round-9 43 deg (not the verified row's 45): the
seed's flank then ends at dK 49.0 (pressure_horn) instead of 56.2.
