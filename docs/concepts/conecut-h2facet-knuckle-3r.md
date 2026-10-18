# conecut-h2facet-knuckle-3r - hub 2 skin-side facet on the lead's frozen chain

Round 15 (main re-launch), lens C (conecut-sidestep-metal: tangent-plane metal moves on a frozen chain). Status: in work.

## Deeper-version answers (written first, before the model)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Make each cut ONE machining
   operation that a shop can quote: the bottom-edge cut is a 45-deg chamfer run by a chamfer mill along a sector of
   the edge (sector ends = the cutter's run-out, sampled as metal), the upper cut is a true PLANAR flat (one end-mill
   pass), not the spec's "r' = min(r, 10 - f)" cylindrical pocket with stepped sector faces - a flat of depth f has a
   natural half-width acos((10 - f)/10) (19.9 deg at f 0.6), no steps and less metal removed for the same clearance
   at its centre. (b) Sample the cut as a SOLID (face, top edge on the unchanged wall, wall above, bottom disc to
   r 10 - c, flat face and its two edges) at <= 0.5 mm spacing - the judge showed the min sits on the chamfer's top
   edge, which a sample move never sees. (c) Keep the uncut cylinder for part-vs-part collisions (a cut removes metal,
   so it can only add clearance: conservative) and say so. (d) Keep every frozen-chain coordinate bit-identical to the
   lead so any change in the bench is attributable to the cut alone (control = c 0, f 0 must reproduce the lead).
   (e) Price the wall over the MR117 OD 11 bearing (r 5.5): wall >= 3.0 means c, f <= 1.5.
2. **Rawest material.** The posed skin of the exact bench (CB.Bench(110,360) with CB_EXACT=1: the signed distance to
   the posed body mesh per pose), the lead's verified per-pose dump
   (docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json) and the judge's per-part binder dump at the
   six guard poses 139 / 203 / 205 / 237 / 264 / 316 (sample index, depth, skin gradient), not the round summaries.
3. **Methods and tools.** The lead's model loaded unchanged (docs/concepts/models/conecut-knee-knuckle-3r.py, its
   frozen claim protocol), a subclass that edits only hub 2's samples after the metal synthesis, exact signed-distance
   reads at the guard poses per config (fast: only six poses), a coarse grid + CMA (tools/concept_cma.py) on
   Bench(60,160) fast for the convergence gate, the frozen exact Bench(110,360) once, the held-out bench paired
   against the lead (tools/alignment_paired.py), kit density check (tools/sample_density.py).
4. **What, other than me, shows the number is right.** The exact bench itself, the round's verifier, the alignment
   auditor's T1 / T5 / probe checks, and a red-team pose list: 203 (the guard: >= 0.15 mm at +0.1 / +0.2 probes),
   205 (stays a contact: depth only), 237 / 264 (horn / crank: the cut cannot reach them on this chain), 316 (link 2:
   not hub 2), 139 (link 2 under K self-motion: unchanged by a hub-2 cut).
