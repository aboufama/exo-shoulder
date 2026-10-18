# proxtrack-relay-knuckle-4r - arm-fixed relay shell 16 mm proximal of the pad, zero lift, counted 4th R

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Price the relay's hardware where it costs
   - in the band. The ideal relay path never measured in-band (every dump carries the lead's 0.9012), so the first number
   is the frozen exact wear with the bump and the shell ON at the pre-registered config, read on the LOWER of pooled and
   chain-only in-band, before any tuning. Make the bump RIGID (one amount per sampled point of member 3 / knee link,
   the max over every fit pose and every relay angle the track can take under it), not a per-pose lift, and make the
   track's pre-arc obey its physical floor (carriage half-arc + stop dowel). Split the result into the bump's in-band
   cost (chain metal at every pose) and the relay's reach gain, so the lever that pays is visible.
2. **Rawest material.** The posed skin itself at every bench pose (the bench's signed distance on the exact path), the
   motion clips (fit-clip frames at 10 fps for the rigid bump and the skin radius profile about a_r), the lead's
   verified frozen shape (fit on Bench(60,160) at phi 0, frozen), the per-pose relay angle solved from the lead's own
   kinematic gates; not the step-0 window tables (they are re-derived inside the model).
3. **Methods and tools.** tools/concept_bench.py exact path, the armarc relay model (relay solve, flood continuity,
   gravity check) re-used by import, the kit's honesty checks through the lead's CCModel, tools/alignment_paired.py for
   the per-pose dump, an in-process hardware sweep (one fit + one relay solve per PHI, hardware re-recorded per config).
4. **Outside judge.** Bench(110,360) exact frozen read once at the pre-registered config (no selection on it), the
   adversarial verifier, the alignment auditor's T5 depth check on the per-pose dump, and a red-team list (the 4
   elevation-0 aliases at the anterior end, folded-side relays 262 / 206, the E strap over the moving carriage).

