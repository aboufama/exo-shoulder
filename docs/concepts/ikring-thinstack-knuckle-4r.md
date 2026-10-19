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

## Results - Bench(110,360) exact, frozen lead (fit Bench(60,160) fast at k = 0 = 12.50, the lead's own)

| reading | gate (chain-only ib) | plain | 1 mm | 2 mm | reach (ws /360) | overhead /28 | elev 90-140 /85 | contacts (T5 mm) |
|---|---|---|---|---|---|---|---|---|
| verified lead conecut-knee-knuckle-3r (reference) | - | 18.28 | - | 34.84 | 0.7278 (262) | 8 | 39 | 4 (20.24) |
| this row, ring PARKED at psi 0 (ring metal on) | 20.37 | 19.38 | 30.21 | 56.49 | 0.7222 (260) | 8 | 39 | 6 (2 shell / bracket: 127 -0.15, 139 -0.48) |
| unpowered CONTROL: least-phi relay, coil deleted, same axis / hardware | 14.46 | 13.47 | 25.79 | 55.46 | 0.8083 (291) | 10 | - | 18 (77.49; 263 -14.94, 459 -14.47) |
| IK, first-run rule (no-take poses closed at the least-deep contact k) | 11.87 | 10.88 | 21.66 | 48.75 | 0.8222 (296) | 13 | 60 | 13 (76.2; 263 -15.36 at k 40) |
| **IK, spec rule (ring moves only for a take) - the claim** | **9.75** (score 96.45) | **8.75** | 19.65 | 47.00 | **0.8222 (296)** | **13 connected** | **60** | **4 (19.48; max 8.93: 139, 205, 237, 264)** |

Claim details (spec rule): follow 1.000, ib14 pooled 0.9034 / chain-only 0.8901 (the lead 0.9012: the 1.2 mm bump of
the E strap and knee link over band 8 costs 0.011), ib10 0.5381; min th margin 5.083 deg over 406 taken poses (0 under
5); no jams; continuity: 0 relayed takes dropped (the IK flood connects 1214 of 1215 feasible envelope nodes and 179 of
the 180 nodes only the ring makes feasible, under both seed sets; the least-phi flood at this axis: 179 of 181).

**The lead note's test, answered:** with ring metal at PHI 40, connected overhead is **13/28** (>= 12) and the ring adds
**1** overhead take under 2 mm (370 at 1.70 mm, chain metal; the other four: 316 3.50, 343 3.70, 372 3.27, 399 3.14) -
inside the "no more than 2" clause. Pre-registered gates: pass <= 13.75 chain-only (9.75) with connected overhead
>= 12/28 (13) - and held overhead >= 25/71 (below).

**The 36 new takes** (over the parked 260): 5 overhead, 21 at elev 90-140, 10 lower (IR / behind-the-back flexion with
the posterior shell end, 306-464); clearance: 1 under 1 mm (127 at 0.10 mm, the BRACKET at k 2.5 - a single-k take),
4 at 1-2 mm (182 1.31, 354 1.71, 370 1.70, 448 1.78), median 3.59 mm. k chosen: 14 of 36 at the travel end k = 40, 3 at
37.5, 6 at 32.5 (the IK wants the end of the slot, as the proposer saw: 27 of 39 at k >= 40 with PHI 45 in the chain-only
table). The anterior shell end is NOT the near-touch: its 2-deg bins clear >= 4.89 mm on every taken pose (+36..+48 deg).
The POSTERIOR shell end (az -4.3 rel the pad) is: 127 shell 1.15 / bracket 0.10, 139 contact (bracket -0.48, flange
-0.07), and 306 / 330 / 354 / 357 take with the shell at 1.71-2.75 mm.

**What actuation buys over the unpowered relay (control):** 14.46 -> 9.75 gate, +5 takes, +3 overhead, -14 contacts
(T5 77.49 -> 19.48): the least-phi relay closes poses wherever the gates pass, including 12 ring-made contacts (263 and
459 at ~-14.5 mm); the proximity IK only moves the ring for a take.

### Red team (my own best config)

* **The IK is an oracle.** psi is chosen on the exact posed skin per pose. A real controller needs psi*(arm pose): over the
  176 pairs of grid-adjacent taken bench poses (15 deg apart) psi* jumps > 10 deg on 4 and > 20 deg on 3 (max 32.5). The
  flood shows a kinematic path exists (the ring sweeps inside one feasible run), but the skin along that sweep is not
  checked - the near-touch of the intermediate psi is unmeasured.
* **Fragile takes:** 2 of the 36 new takes are taken at ONE k only (127 at 2.5, 354 at 40); 12 have a taking-k run
  narrower than 10 deg (median width 15 deg). A 2.5-deg controller error loses them.
* **Travel end:** 14 of 36 new takes sit on the k = 40 slot-end stop; PHI 45 would move the shell's anterior end onto the
  behind-back ER cliff (phi40's held 211) - not tried (envsel only, never Bench(110,360)).
* **Near-touch (reported, not a gate):** the 2 mm reading is 47.00 vs the lead's 34.84 (phi40 47.16). The parked ring
  alone puts metal within 2 mm of the skin on 9 of 110 fit-clip frames (7 under 1 mm; the lead: 0) and on 63 of 296 ws
  takes (the lead: 23 of 262) - the bracket / flange at the pad azimuth and the posterior shell end. At this axis the
  shell sits 3.35 mm LOWER than at 12 / 235 (R_t 76.75 vs 80.1) and the bracket ramps 28.9 deg (24.1): spec risk (d)
  showed up as near-touch, not as contact.
* **Unmodelled:** J4's holding torque into the cuff (shoulder slip), the drive of J4 itself (MVP1 is kinematic: no motor
  model), the skin along the J4 self-motion between psi values, iglidur friction in the slot.
* **Determinacy (R17):** J4 is a counted active joint whose value the IK sets: in an unpowered MVP1 it is a self-motion
  nothing holds (a brake or the motor holds it) - a labelled 4-joint option, never the lead.

**Where the overhead still goes (claim, 15 of 28 lost):** the abduction cone 0 / 10 unchanged (209 / 210 / 211 / 236 /
238 / 263 / 265 / 292 fold or J3 stop, 237 / 264 the lead's drive contacts at -8.93 / -5.80 - the ring about a_r does not
reach the cone: the round-301 lens C measurement, a J1 / J2 seat-level wall); 5 stretched-fold IR poses at plane 105-120,
axial -120..-150 (397, 398, 424, 425, 426) that no k in [0, 40] closes. Whole bench: 64 ws lost = fold 55, J3 stop 5,
contact 4.
