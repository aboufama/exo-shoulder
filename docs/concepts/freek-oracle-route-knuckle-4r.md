# freek-oracle-route-knuckle-4r - Free-K oracle bound with an anterior link-2 corridor (round 104, lens B, an INSTRUMENT, never a claim)

## Deeper-version answers (written first, 2026-10-18 05:33 UTC)

1. **What a top mechanism designer would do that the spec does not ask.** Before building any K determination (cells B / C),
   bound it: a per-pose oracle that picks the best K on the legal self-motion is the ceiling of EVERY K law, spring, stop or
   sensed 4th joint at these seats. The designer would also ask which lost poses the oracle can reach at all: K's stop B is
   the same for the oracle as for the kit, so a pose refused for the fold (K past stop B) stays refused - the oracle can only
   turn CONTACT (and near-touch) poses into takes. So the bound is "kit takes + rescued contacts", and the 95 arithmetic
   (+17 takes) is out of reach unless the corridor also clears metal-parked stretched poses. Second thing not asked: score
   the oracle's pick on the FULL model checks (part-part pairs, knee, band), not on skin distance alone, because max-min skin
   distance can push link 2 into member 3 or out of the band.
2. **Rawest material.** The posed skin itself through the bench's exact signed distance (`W.dist`, CB_EXACT=1) per pose and
   per K sample, the motion clips' frames (Bench(110,360) clip frames for follow and in-band), the 1432-pose workspace grid
   for continuity; not the proposer's interpolated (s, v) clearance field (field2.npz) - that field is used only to choose
   the corridor's sweep range.
3. **Methods and tools.** The verified k33 harness unchanged (minarc kitrule + skinnormal-shortk pricing, frozen hand-over
   by __dict__ diff from docs/concepts/verify/minarc-bdp-remeasure.py), a closed-form free-K self-motion (J2 off its stop:
   K angle -> a1e on the K dyad -> the (a1e, a2) dyad closure, same assembly branch), exact skin distance per sample,
   then ONE composed run of the frozen model with the per-pose K table so every check of the model applies; corridor as a
   planform offset of link 2's rows on the sphere, refitted by the model's own needed() + ramp profile.
4. **Who else shows the number is right.** The bench (Bench(60,160) fast for the sweep, Bench(110,360) exact frozen for
   the bound), the round's adversarial verifier and the alignment auditor; a red-team list (the binder poses 117 / 127 /
   129 / 139 / 148 / 316 / 343 / 369 / 423 / 119 with hub 2, L1b, L2, hub K distances at the oracle's pick) is on file so
   any reader can re-measure it.
