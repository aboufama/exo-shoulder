# offset-shortcar-relay-4r - proxtrack's one-sided relay, re-priced under the buildable pin-a stack

Round 106 (J6, track jump), lens A twoside-relay (the one-sided control), judge re-spec. Model:
`docs/concepts/models/offset-shortcar-relay-4r.py` (proxtrack-relay-knuckle-4r imported read-only THROUGH its buildability
verifier, so the verifier's stack rule `stackfix_amounts` is in every reading). Sweep: `docs/concepts/sweeps/offset-shortcar-relay-4r.json`.
Raw outputs: `docs/concepts/verify/offset-shortcar-relay-4r/`.

## Deeper-version answers (written before the first number)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the shell's two ends and the coil
   as the real design variables, not ds alone: the pose that binds (466-type posterior internal rotation) is a property of
   where arm-fixed metal sits over the posterior arm, so read the shell's skin margin per azimuth on the selection bench
   and place the zero end at the measured clean azimuth instead of at a pre-registered 4.5 deg. (b) Attribute every
   contact by part (chain / shell / carriage / bracket / flange / coil) at every config, so a hardware change can be
   seen to remove or add a specific contact rather than move a pooled number. (c) Sample the hardware the parent left out
   (T-nut retaining flange, constant-force coil) from the first reading, and put the coil on the JAM list (chain metal
   within 1 mm of it loses the pose), not only the contact list. (d) Check that a shorter carriage still carries the
   moment: the drawer rule L 14 > 2 mu d (7.5 mm) and the bracket's planform turn change the moment arm about the shell.
2. **Rawest material.** The posed skin itself through the bench's signed-distance field (every shell / coil / flange point
   is read against the posed scan at every pose, not against a summary radius); the fit-bench clip frames for the
   shell's p90 skin profile about the relay axis (the R_liner of the track); the envsel workspace draw (tools/env_bench.py,
   seed 2) as the only selection bench; the parent's per-pose dumps for the binders (466, 262, 206, 264).
3. **Methods and tools.** tools/concept_bench.py exact (libigl signed distance), the parent's relay solve / continuity
   flood (armarc), the verifier's buildable stack rule, the parent's rerecord with two hooks (part attribution, coil jam),
   envsel for every choice, one frozen exact Bench(110,360) claim wear + one held wear, T5 per-pose dumps
   (tools/alignment_paired.py format), AA.gravity_check for R17, tools/simplicity.py for cx.
4. **What other than me shows the number is right.** Three controls on one claim-bench prepare that must reproduce the
   verifier's 17.46 and the judge's 16.92 / 14.26 to 0.1 (a build check); the selection made on envsel only (the claim
   bench read once); the held-out bench paired against proxtrack's buildable held 21.46, freek 20.50 and the lead 22.38;
   the per-pose dumps on file for the auditor's T5 depth check; the red-team pose list below (posterior IR 466-type,
   folded-side relays 262 / 206, the elevation-0 alias at the anterior end, the near-jams at the 1 mm floor).

## Status

(filled in as the readings land)
