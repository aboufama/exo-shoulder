# shortk-onetooth-knuckle-3r - re-seated short-K one-tooth knuckle (round 107, cell B)

**Status: in progress (step 0).**

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do here that the spec does not ask for.** The parent row
   (onetooth-slowlaw-knuckle-3r) died on two counts: the slow law's ghost, and the lantern-gear rule (a PA-passing pin
   sits next to the fixed relative pole, so over a long stroke it crosses the pole and the flank undercuts). Re-seating K
   moves the pole; it does not remove it. So the first check is the built flank on the NEW dyad, on a fine K grid
   (0.05 deg - the proposer's PA reading used 61 samples over 44 deg, 0.74 deg apart, the same grid that stepped over the
   parent's pole spike), over every pin start on the sphere around hub 2 (r 4-45 mm, all azimuths), at mu 0.087 and at
   mu 0 (a rolling pin), and at rho up to 2. The second check is the law-only ghost with the drive range the built pair
   can actually carry (DKLIM = its built range), not only the ideal full stroke - that is the buildable bound. Third: the
   lead's parent clamps bk1 to [26, 32] and bk2 to [38, 48] (an old search box): a naive re-seat silently runs 32 / 38,
   not 34 / 30, so the dyad is restored after the clamp and asserted. Fourth: anchor the law on the lead's END STATE
   (a1e 54.27 at th 106.3, read from the lead's own kinematics), not on the lead's K value (45.62 on the old dyad is
   a1e 57.33 on the new one).
2. **Rawest material.** The posed-skin signed-distance fields of every bench and the motion clips, through
   tools/concept_bench.py on the exact path (Bench(110,360) exact for the frozen wear; envsel,
   docs/research/minarc_final_polish/env_poses.npz, for selection only). The lead's verified model code itself
   (docs/concepts/models/conecut-knee-knuckle-3r.py), loaded unchanged, for the chain and its exact kinematics. Not the
   proposer's proxy numbers (scratch shortk*.py: re-solved poses at a hand-placed patch, no fold rule, no re-fit).
3. **Specific methods and tools.** Exact spherical kinematics of the one pair (all axes through GH): the pin centre path
   in link 2's frame, the kinematic normal through the relative pole (Kennedy), contact points X - rn F, the built flank
   as the union-of-discs boundary (undercut where a contact point falls inside the pin disc of another K), both pressure
   angles vs 43 - atan(mu); a vectorised scan of 2,000+ pin starts per rho. Then the parent's ghost harness (every drive
   part deleted) on the frozen protocol: fit Bench(60,160) fast, freeze the shape, wear exact.
4. **What, other than me, shows the number is right.** The bench (Bench(110,360) exact, frozen) and a paired control
   that cancels harness error (the parent's control: the lead's own law in the same ghost harness reproduces the
   verified 18.28 / 262 takes exactly). The built-flank check is independent of the bench (pure kinematics, any reader
   can re-run `flank` mode). The red-team list gives the poses lost with th and dK and why.
