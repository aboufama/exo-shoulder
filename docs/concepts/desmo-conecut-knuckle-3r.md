# desmo-conecut-knuckle-3r - Desmo-conecut knuckle with a pinned-horn stage 2 (round 13, the main track's knuckle lens)

desmo-slipper's spring-free, roller-free K drive worn on conecut-knee-knuckle-3r's knee and J3 dowel stop, with stage 2
inverted (cell B): the nose is a 440C dowel pressed into link 1a, the two-walled slot is cut in a small Ti plate on the
crank's tip. Cell A (the desmo stage 2 unchanged) is the measured control; cell C moves stage-1 ratio into stage 2 (g 2.6-2.8).
3 active DOF (J1, J2, J3), K slaved and never read, 0 passive translations, no springs, no gears / pulleys / cables.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask for.**
   * Check where the inverted slot actually goes. The slot is the nose's path in the crank's frame. A 3.66 mm slot is
     short, but its direction decides whether the plate around it fits next to hub K's O20 stack (the plate sits at the
     arm-tip layer, inside the stack's 12.25 mm height). The spec gates the boss against hub K; I gate the plate too.
   * Treat the slot length as a design variable with a physical end. The slot's far end is a real stop B. Cut it to the
     stroke the taken poses need (bench 45.62, held 46.27 deg of K), not to the K law's full 64.5 deg.
   * Read the pressure angle on the built pocket (the union of nose discs), not on the centreline. At the closed end the
     nose sits at the crank / link-1a relative pole (0.68 mm/rad). There the contact normal comes from the pocket's
     shape, not the path's tangent.
   * Keep everything verified unchanged: the lead's seats, law and drive (beta / r_c / g), desmo's stage 1 at a_s 9.5 /
     psi 150, conecut's knee and dowel. Compare at equal samples (S6), because deleting a well-placed lug band reads
     as an in-band loss by sample weight alone.
2. **Rawest material.** The posed skin itself: the signed-distance cache behind Bench(60,160) and the exact path behind
   Bench(110,360). Also the model's own per-pose body transforms (the K, q2 and crank angles the drive must follow on
   every bench and held-out pose), and the drive geometry the verified lead was built on
   (docs/research/slipper_mechanism/geo_bench.npz) as a cross-check of the inverted-cam synthesis.
3. **Methods and tools.**
   * Exact spherical-cam synthesis per 0.25 deg of K (every axis passes through GH). Pressure angles are taken at the
     nose centre, because the contact force passes through it.
   * A morphological pocket check: the nose disc must stay inside the union of swept discs, with K bisected to
     0.005 deg and the crank held.
   * Per-K-step clearance of the plate against both hubs, using the kit's signed-distance cylinders.
   * The verified chain loaded unchanged (desmo-slipper -> slipper-nose -> roller-longdyad -> sidecar-roller-flank),
     tools/concept_bench.py, and the frozen-shape protocol for any claim.
   * Compute is local only: the farm window has closed, so I run at most 2 niced processes.
4. **What, other than me, shows the number is right.**
   * Cell A, reproduced exactly (13.18 fast, the proposer's number), as the control.
   * The bench (fast, then exact frozen).
   * The adversarial verifier and the alignment auditor (T5 depth, gate re-definitions).
   * The red-team list: rest, overhead, across the body, behind the back, the stretched-wall poses at dK ~46, the
     closed end of the slot (stop A) and the slot's far end (stop B).

