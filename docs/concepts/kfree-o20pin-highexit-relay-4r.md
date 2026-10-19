# kfree-o20pin-highexit-relay-4r - O20 axis-exit pin relay at the high anterolateral exit (round 401, K1)

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** Measure the pin's price where it is paid
   before building it: (a) a relay about a GH-through line is kinematically a pure re-orientation of member 3, so the
   IDEAL bound (no R4 / bar / lug metal) on the lead-quality chain is the ceiling the hardware can only lose from; read it
   first and kill on it. (b) The R4 stack is coaxial with the relay line, so its disc is rotation-invariant: the boss
   cost is set by ONE number, the line's maximum skin exit over every pose (its standoff), and the spread of that exit
   (48-79 mm) is a direct in-band price. A designer would read that spread from the posed skin per pose before drawing
   the boss, and treat the boss as a flat O20 face (not a skin-fitted cap, which no bearing stack has). (c) Steering
   stops are real only inside the least-phi solve; check that the dowels are honoured there and not clamped after.
2. **Rawest material.** The posed skin itself through the bench's signed-distance field (K.requirement / dist_many
   along the relay line and along every bar / boss / lug sample ray per pose), the fit-clip frames and workspace poses
   of Bench(60,160) / envsel / Bench(110,360) exact (held-out untouched), the lead's own fitted metal (conecut's
   CCModel, frozen), and the 2-deg slerp continuity flood on the 1432-pose envelope grid - not the kit summaries
   (kit control 60.55).
3. **Methods and tools.** The lead-quality ideal path of docs/concepts/models/insertion-cband-relay-4r.py (kfree
   lead_eval: K welded, drive stripped, knee-side samples dropped, J3 seat asserted in M1.p), the least-phi relay
   solve of armarc-relay-knuckle-4r.py with the J2 / J3 own-angle dowels inside the gate, envsel for picks and ONE
   frozen exact Bench(110,360) per claim, AR.flood_relay for the continuity rule, explicit R4 / bar / lug sampled metal
   with a 1 mm non-adjacent jam check, th margin in the ONE metric (angle(J1, J3) vs the welded window).
4. **What, other than me, shows the number is right.** The bench (envsel pick, Bench(110,360) exact frozen claim), the
   adversarial verifier (re-runs the claim and the held-out), the alignment auditor (T1-T5: near-touch, th margin,
   contact depth vs the lead's 20.24 mm), and the red-team pose list below (relayed overhead poses, the az 50-55 chest
   cliff partners at the R4 / lug, folded-wall relays, link 2 over the bar).
