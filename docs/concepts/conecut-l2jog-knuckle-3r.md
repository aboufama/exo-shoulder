# conecut-l2jog-knuckle-3r - link-2 mid-bar planform jog at pose 139 on the lead's frozen chain

Round 15 (main re-launch), lens C (conecut-sidestep-metal: tangent-plane metal moves on a frozen chain). Status: in work.

## Deeper-version answers (written first, before the model)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Move the bar's SECTION rigidly:
   a planform jog is a profile cut, so every row across the 6 mm bar must get the same displacement at the same
   station along the bar. The spec's weight w(distance from sample 13) would give a row 6 mm across a smaller weight
   than the binder's row (a shear, not a jog), so the station here is the per-row arc length from the binder's normal
   plane. (b) Use the S of two tangent arcs (a cosine run-out), not linear run-outs with kinks, and report its radius.
   (c) Try the variant that cannot hurt the far side: a one-sided WAIST (the edge the bar leaves moves dl, the far edge
   stays), because the spec's main risk is the far side of a jog meeting the skin elsewhere. Price its narrowing
   against the 6 mm bar. (d) Measure, as a separate, labelled variant, a local through-thickness JOGGLE (dz), because
   the judge found 29 % of the proposer's gain came from that component: a press-brake joggle in 3 mm Ti is a real,
   quotable operation if its radius meets the 5 t = 15 mm rule. Its in-band cost is read, not assumed. (e) Keep every
   other coordinate of the frozen chain bit-identical so the control (dl 0) reproduces the lead exactly and any change
   is the jog's alone.
2. **Rawest material.** The posed skin of the exact bench (CB.Bench(110,360) with CB_EXACT=1: signed distance to the
   posed body mesh per pose), the lead's own fitted link-2 samples (4 rows x 31, member 2) and their per-pose world
   transforms, the lead's verified per-pose dump (docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json),
   the judge's binder dump (scratchpad lc/lead4.npz: link-2 sample 13 at 0.072 mm at pose 139), the env / envsel fresh
   envelope draws (tools/env_bench.py) and the held-out bench for the paired test only.
3. **Methods and tools.** The lead's model loaded unchanged (conecut-knee-knuckle-3r.py and its frozen claim
   protocol); a subclass that moves only link 2's samples after the fit (underside, mid strap, top contact set); a
   PCA frame of the bar at the binder; a scan harness that wears the frozen lead ONCE per bench and re-reads only link
   2 on the poses where it is within 4 mm of the skin (exact on Bench(110,360) / envsel / env, fast on Bench(60,160) /
   envh); coarse grid + local refinement for the convergence gate; the frozen exact Bench(110,360) once (collisions
   re-checked there); held paired vs the lead (tools/alignment_paired.py); tools/sample_density.py.
4. **What, other than me, shows the number is right.** The exact bench, the round's verifier, the alignment auditor
   (T1 shell points, the +0.1 / +0.2 mm probes, T5 depth) and a red-team pose list: 139 (the target), 316 (link-2 root,
   must stay untouched: the jog's weight there must be 0), 203 / 205 / 237 / 264 (other parts: unchanged by
   construction), and every pose where the jogged stretch's FAR side or the run-outs come within 1 mm of the skin on
   any bench (envsel, held).
