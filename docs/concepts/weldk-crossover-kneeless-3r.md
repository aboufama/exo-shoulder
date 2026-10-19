# weldk-crossover-kneeless-3r - kneeless welded crossover 3R (cx 0, no knee)

Round 301 (O1, overhead track), lens drive-free-cone, minimum-parts branch. Model:
`docs/concepts/models/weldk-crossover-kneeless-3r.py` (loads the sibling `weldk-overstrap-pinknee-3r.py` - itself the
H1 pin-knee model loaded unchanged - and turns the knee into one rigid bracket). Sweep:
`docs/concepts/sweeps/weldk-crossover-kneeless-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Prove the knee is dead weight here
   before deleting it: with J1, J2, J3 all on GH rays the cuff drift s is identically 0, so the knee angle is constant;
   the model ASSERTS ptp(knee angle) < 0.5 deg and |s| < 0.05 mm on every bench pose (else dishonest) instead of
   assuming it. (b) Price the crossover where it is born - link 2 turns about J3 under the bracket's E leg, so the E
   underside is computed from link 2's measured top in member 3's frame over every kept pose (plan-view stacked-pair
   rule, +0.15 mm), not assumed flat. (c) Kill fast: the sibling (weldk-overstrap-pinknee-3r) died on the E strap's
   in-band (0.48 < 0.80) and on hub 3 diving into the bunched deltoid at the cone; measure both FIRST at this J3 ray
   (105, 10), which is higher and more posterior than the sibling's station, and stop if they repeat. (d) Read the
   rigid cuff honestly: the GH-centre misfit a rigid bracket pushes into the liner (no knee to absorb it) is a red-team
   number reported next to the bench (the K1 no-slide reading, 3 mm liner budget).
2. **Rawest material.** The posed skin itself (concept_bench exact signed distance on the posed body mesh, CB_EXACT=1
   for the claim), the 10 fps motion clips for q1..q3 continuity, the Bench(110,360) workspace poses (28 overhead,
   elev >= 140; 85 at elev 90-140) - not the ghost's digest (dfc2/park_wk.py is the prior only; the judge's H1 control
   puts its bias at +13 ws / +5 overhead).
3. **Methods and tools.** H1's exact closed-form spherical IK (three GH rays -> exact closure), the seed VModel honesty
   rules (closure, continuity, jam rule, 1 mm non-adjacent / 0.15 mm adjacent), sphere-traced skin heights on
   1 pt / 4 mm2 samples, <= 60 deg ramps, O20 v5 hubs, the kit fold margin (5 deg of th); a coarse LHS + CMA-ES on
   Bench(60,160) fast with the 1 mm near-touch objective (local, farm closed); the frozen-shape protocol (fit 60/160
   fast, wear on 110/360 exact) for the claim; the GH-offset misfit red team.
4. **What shows the number is right, other than me.** The bench (outside judge), the frozen exact read through the
   same code path that verified H1 (27.20) and reproduced the sibling, the knee-rigidity assertion, and a red-team pose
   list (the lead's 28 overhead poses by index, cone 209/210/211/236/237/238/263/264/265/292, the shell poses
   205/235/262, rest / across / behind groups) for the adversarial verifier.
