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
