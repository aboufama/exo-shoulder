# ikring-thinstack-knuckle-4r - the lead + an ACTIVE one-sided J4 ring on phi40's verified shell (coil deleted)

Round 301 (O1, track overhead), lens rocker-redundant-4r. A LABELLED 4-JOINT OPTION (4 active joints), never the lead.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat J4 as what it is - a redundant
   joint of a 4R chain - and price the IK as a *controller*, not as a per-pose oracle: the continuity flood has to be over
   (pose, psi) STATES, with psi's self-motion at a fixed arm pose allowed only inside a contiguous feasible-psi run (the
   joint moves the chain through every intermediate psi), and a relayed take counts only if the IK's psi is in a reached
   run. (b) Ask the inverse question to the proposer's: not "how many poses does the IK buy" but "how much of the buy
   is at the TRAVEL END" - the IK riding psi = 40 on most new takes means the joint is a two-position switch, and a
   switch is a stop pair, not a ring; the k-choice histogram says which. (c) Wear the ring metal at EVERY k of the
   table, not only at the chosen one: the IK must choose among takes that include the shell / carriage / bracket /
   flange (the proposer's table was chain-only). (d) Report the unpowered least-phi control on the same hardware: it
   prices what actuation buys over phi40's spring.
2. **Rawest material.** The posed skin of every bench pose (tools/concept_bench.py exact path, libigl distance +
   winding sign) - no p90 summaries for the claim; the motion archive's humerus frames (Z0 HG, envelope grid 1432
   nodes, the fit clips); the lead's own fitted geometry (frozen at k = 0, docs/concepts/verify/conecut-knee-knuckle-3r.py
   BEST) and phi40's arm-frame shell profile (the p90 skin radius about a_r over the fit clips) for the shell radius.
3. **Methods and tools.** phi40-thinstack-relay-4r.py imported read-only (offset-shortcar / proxtrack / armarc machinery:
   relay_geometry, relay_points, rerecord, jam rule, chain-only gate, stackfix bump); a k-table of frozen exact wears
   (k = 0..PHI step 2.5) with the ring hardware in each; the lead-first max-clearance IK; one final wear at the chosen
   psi per pose; the IK state flood (module docstring); BV.th_margin; tools/alignment_paired.py per-pose dump; the
   unpowered least-phi control (PT.prepare + AA.flood_relay at the same axis).
4. **What other than me shows the number is right.** Bench(110,360) exact frozen (the claim bench) and the held-out
   bench (report only), the k = 0 reading reproducing the verified lead's 262 / 8 of 28 with the ring parked, the
   adversarial verifier (phi40's verifier harness docs/concepts/verify/phi40-thinstack-relay-4r-verify.py is the
   template), the alignment auditor's T1 / T3 / T5 checks (per-pose dump on file), and a red-team pose list: the
   anterior shell end (held 211 at +48.9 deg, behind-back ER), the posterior end (466 / held 977 / 225), the abduction
   cone (237 / 264 drive contacts), the new takes under 2 mm.

## Model

(results below are written as the runs land)
