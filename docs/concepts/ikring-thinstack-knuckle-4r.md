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

## Model (docs/concepts/models/ikring-thinstack-knuckle-4r.py)

phi40-thinstack-relay-4r.py imported read-only (its offset-shortcar / proxtrack / armarc parents: relay geometry, ring
metal, rigid local bump, jam rule, chain-only gate, buildable knee-over-boss stack). Changes, all hardware or controller:

* **Coil deleted** (`coil: none`): no constant-force strip, no lug; J4 is driven (a counted, ACTIVE joint).
* **Pre-registered cell** (the judge's, a hardware reason, not a bench read): PHI 40, delta 3.5, axis tilt 8.5 toward
  taz 243 (through GH), ds 31, tsh 1.0, carw 14, band 8, bump 1.2, lean, L-lug bracket. Measured geometry at this axis:
  R_t 76.75 (phi40 at 12 / 235: 80.1 - the spec expected +0.4 mm; the shell sits 3.35 mm LOWER here), shell arc
  [-4.34, +49.85] deg rel the pad azimuth, bracket ramp 28.9 deg (phi40 24.1).
* **k-table with ring metal**: the frozen lead (fit Bench(60,160) fast at k = 0: 12.50, the lead's own fit, reproduced)
  worn exact on Bench(110,360) at every k in 0, 2.5, ..., 40 with the arm-side frame turned k about a_r and the
  shell / carriage / bracket / flange metal and the jam rule in every reading (the proposer's table was chain-only).
* **Lead-first proximity IK** (the spec): psi = 0 where k = 0 takes the pose; else the k with the largest min metal
  among the k that take it (ties -> smaller k); a pose no k takes stays at psi 0. Clip frames: psi 0.
* **One final wear** at the chosen psi per pose (every number below and the per-pose dump come from it).
* **IK state flood** (continuity rule): 1432 envelope nodes x 17 k; a node's states are its contiguous feasible-k runs
  (self-motion of the active J4 at a fixed arm pose, every 2.5-deg step checked: K / knee pins <= 10, actives <= 25);
  an edge from a state is valid if a greedy k path (nearest feasible k, ties -> smaller) along the 2-deg slerp keeps
  |dk| <= 10, K / knee pins <= 10 and actives <= 25; a relayed take counts only if its node's reached runs hold the IK's k.
  Seeds: the spec's "k = 0 state-A nodes at elev 0" set is EMPTY (all 171 elev-0 nodes close at k = 0, none in state A:
  the hanging arm sits outside the stop-A window), so the flood seeds the verified convention (every k = 0 state-A node,
  AA.flood_relay / the lead's / phi40's floods, 513 seeds) and, as a second reading, every k = 0 node at elev 0 (171).

### A spec gap found and closed while modelling

The first claim-bench run (`IK_RULE=closest-contact`, docs/concepts/verify/ikring-thinstack-knuckle-4r/ik_bench.json)
closed a pose no k takes at its least-deep CONTACT k. That turned 9 poses the lead loses to the fold / J3 stop
(206, 233, 260, 262, 263, 454, 457, 459, 466) into ring-made contacts, up to 15.4 mm deep (263 at k 40; T5 76.2 mm):
the controller would be driving metal into the arm to "close" a pose. The spec's rule (the ring moves only for a take)
leaves those poses at psi 0, i.e. lost exactly as the lead loses them; it is now the model's default
(`IK_RULE=take-only`). Its numbers are the first run's per-pose dump with those 9 poses set to their k = 0 state (all
9 are lost at k = 0: none is in the k = 0 contact list) - ik_bench_specrule.json / ik_bench_specrule_perpose.json -
exact because every ws pose is worn independently and clip frames are at psi 0 in both. The model's `rechoose` mode
re-wears it in one pass for the verifier.
