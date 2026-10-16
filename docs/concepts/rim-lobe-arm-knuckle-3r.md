# rim-lobe-arm-knuckle-3r - direct-pair knuckle (K's follower arm on a link-2 lobe plate)

Round 7, lens direct-drive-knuckle (a), groove-arm-knuckle-3r merged in as the 'groove' embodiment.
Model: docs/concepts/models/rim-lobe-arm-knuckle-3r.py (on the verified winner geneva-tail-knuckle-pinknee-3r, rod
embodiment, with its rocker / pushrod / rod ends / horn deleted and replaced by a lug on link 1a, a follower and a
cam plate on link 2).

## Deeper-version prompt (answered before modelling, 2026-10-16 15:45 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the LAYER STACK as the design,
   not the cam law. The pair (lug on link 1a, plate on link 2) lives between two hub stacks that already put link 1b
   at hub 2's floor and link 2 one layer up; whichever of lug / roller / plate is stacked on top of the other two sits
   ~2 layers (6-7 mm) above the floor and leaves the 2-14 mm band - that is exactly why the rod drive was 0 % in band.
   So (a) put the lug at the BOTTOM layer, skin-fitted like a link and run beside link 1b (a0 off the K-J2 line), with
   the roller standing up from it into link 2's own layer, so the plate is just link 2's ring widened - no extra layer
   at all; (b) keep the spec's 'lug above the plate' as the control; (c) compute the pair exactly on the sphere
   (pressure angle from the relative velocity, pitch curvature, undercut / lap check over every q2 the bench visits),
   not with tan(pa) = kK r_horn / r_lobe; (d) size the K spring for force closure before claiming the roller.
2. **Rawest material.** The posed skin itself (the signed-distance cache behind tools/concept_bench.py: every metal
   sample of lug / roller / plate is sphere-traced against the skin of every bench pose, not a digested clearance
   map), the fit clips at 10 fps (continuity of q1, q2, q3, K and both knee pins), the 160 / 360 workspace poses, and
   the verified winner's own per-part in-band numbers (verify/geneva-tail-knuckle-pinknee-3r_corr_bench_frozen.json)
   as the baseline the drive must beat part by part.
3. **Methods and tools.** tools/concept_bench.py Bench(60,160) fast cache for the search, CB_EXACT=1 Bench(110,360)
   frozen for the claim; the winner's model (kit-rule B, phys q2 stop, near-touch objective, VModel checks) loaded as a
   module copy; exact spherical cam synthesis (pitch curve C(t) = R(u2,-q2(t)) R(uK,-dK(t)) p_arm in link 2's frame);
   the cloud CPU farm (tools/cloud_run.py) for the coarse sweep and CMA (tools/concept_cma.py) on the near-touch gap.
4. **What other than me shows the number is right.** The bench (an outside judge), the adversarial verifier
   (docs/concepts/verify/geneva-tail-knuckle-pinknee-3r.py protocol: frozen exact, held out, continuity flood fill),
   and a red-team pose list: rest, overhead (elev >= 140), across-the-body, behind-the-back, the law's last valid t
   (stop B), the onset (roller touching the lobe start), and the plate's sweep over hub K and link 1b at every q2.

