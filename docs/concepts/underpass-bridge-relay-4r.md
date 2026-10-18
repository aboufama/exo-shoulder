# underpass-bridge-relay-4r - the E strap passes UNDER a raised arm-fixed bridge shell

Round 107 (J7, track jump). 4 counted joints (J1, J2, J3 + the relay): a user option, never a lead.
Model: `docs/concepts/models/underpass-bridge-relay-4r.py` (imports `offset-shortcar-relay-4r.py` read-only).
Verify dir: `docs/concepts/verify/underpass-bridge-relay-4r/`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Treat the bridge as a structure, not a
   strip of sampled points: it carries the pad load (~4 N) through the carriage, so either both ends are supported or
   one end carries a moment. Check the real section against that load (deflection must stay inside the under-pass
   clearance, here <= 0.5 x up_clr), and keep the underside fixed when the section is stiffened: a thicker shell only
   raises the TOP (and what rides on it: carriage, bracket, lug coil), so the in-band price is the bracket and coil, not
   the shell underside. The judge's "+1 mm shell reads 15.99" moved the UNDERSIDE (rt_extra +1), not the thickness, so it
   does not price a thicker cantilever. Second: freeze the bridge height at selection and wear it unchanged on the claim
   and held benches; an under-pass whose height is re-placed per bench would hide the E-envelope risk.
2. **Rawest material.** The posed skin itself (signed distance per pose, B.dist) on the envsel / claim / held benches; the
   fitted chain's sampled metal in the arm frame (HG0) and the carriage frame at every fit and envsel frame (the need
   scan, per 1-deg azimuth bin rel the pad); the judge's raw block readings (scratch r107j/blocks.log, blocks2.log,
   eaz.log) and the proposer's under-pass wear (r107a/underpass2.log), reproduced here rather than quoted.
3. **Methods and tools.** The verified parent's buildability path (offset-shortcar -> proxtrack buildability verifier ->
   proxtrack -> armarc relay solve, flood continuity), its sector jam rule extended to every support / extension sector,
   envsel exact for selection only (tools/env_bench.py), frozen exact Bench(110,360) for the claim, the held bench once,
   curved-cantilever beam theory (Castigliano: radial tip deflection P R^3 / (E I) (a/2 - sin 2a / 4)) for the
   bridge section, tools/simplicity.py for the complexity record.
4. **What, other than me, shows the number is right.** The bench itself (the parent's verified wear path, unchanged gate
   arithmetic), the controls (the proposer's 14.59 no-support reading must reproduce on this code before any support
   is priced), the independent verifier that will re-run the claim, and a red-team pose list (the posterior binder
   class 259 / 264 / 265, the anterior torso pose 119, E's highest pose in the footprint, every jam / near-touch pose).

## Pre-registered selection (written before any reading)

Selection on envsel exact only. Cells: PHI {35, 40} x {ant ii (cantilever, tshc 2.5) d4.5 u1.2 H2; ant i (extension +
block beyond E) d4.5 u1.2 H2; ii d4.5 u1.0 H2; ii d3 u1.2 H2; ii d3 u1.0 H2; ii d4.5 u1.2 H1.5}; carw 14, ds 31, lug coil
D12 L10, flange on. Pick = the lowest chain-only gate with 0 jams, pooled ib14 >= 0.90 and bridge deflection <= 0.5 x
up_clr; ties (within 0.05) broken by fewer taken poses with metal < 1 mm, then the thinner posterior block. The claim
is read ONCE (CB_EXACT=1, Bench(110,360), frozen, rl_fix / hiE frozen from envsel), then the held bench once.
Pass = gate <= 13.75 with 0 jams; kill = gate > 14.76 or held > 18.27.

Addendum written after cells 1-5 had read and BEFORE cell 6 (H 1.5) read: cells 1, 3, 4, 5 (all ant ii) tie at 14.59 with
15 near-touch poses and the same block height, so the pre-registered rule cannot separate them. Last tie-break, chosen
for robustness and not for a number: the larger E clearance (up_clr 1.2: the claim's E envelope is the main risk), then
the parent's verified delta 4.5. If cell 6 ties, the rule's own "thinner posterior block" picks it.
