# Alignment audit: offset-shortcar-relay-4r (round 106, slice r106-A)

Auditor run, 2026-10-18 ~15:07 UTC. The tool is tools/alignment_audit.py version 2026-10-18.1, run with reference
conecut-knee-knuckle-3r. Ledger: `python3 tools/alignment_ledger.py get offset-shortcar-relay-4r`.

## Verdict: WATCH (claim v_gap 14.76)

- The claim is v_gap 14.76: frozen exact Bench(110,360), chain-only buildable gate. That is score 94.63. The plain
  reading is 13.74 and held out is 17.77.
- This audit re-wore the claim with the model unchanged. The re-wear reproduces gate 14.76, plain 13.74, 13 contacts
  and 0 jams to 0.00. That is the third independent reproduction, after the claim and the verifier.
- No hard rule is broken: O20 hubs, fold margin min 5.000 deg in th (0 of 396 taken poses below 5), 0 passive
  translations, 4 DOF. Complexity recomputes to 52.5.
- No finding shows the number ranking this design above a design that is better for the wearer under the same
  harness, so nothing is gamed.
- The ledger verdict is watch: 2 tool checks plus 7 judgement findings.

## What the wearer gets (measured)

Sources: the re-wear in docs/alignment/remeasure/offset-shortcar-relay-4r_bench.json, and the verifier's per-pose dumps
docs/concepts/verify/offset-shortcar-relay-4r/verifier_{claim,held}_perpose.json.

**Reach**

| | bench | held |
|---|---|---|
| Overhead taken (elev >= 140) | 8 / 28 | 19 / 71 |
| Raised arm taken (elev >= 90) | 63 / 113 | 168 / 300 |
| Workspace taken | 286 / 360 | 740 / 952 |
| Same counts for the 3R lead (overhead, raised, workspace) | 8 / 28, 47 / 113, 262 / 360 | 18 / 71, 123 / 300, 659 / 952 |

- Bench, by elevation: elev >= 120 takes 25 / 62 and elev >= 160 takes 3 / 15.
- The relay takes 24 bench poses the lead loses (81 held) and loses none. All 24 are at elev 30-135.

**Near-touch**

- Taken poses with metal < 2 mm: 47, of which 40 are workspace poses and 2 are overhead. 8 taken poses have metal
  < 1 mm. The minimum metal on a taken pose is 0.072 mm.
- Counting only taken non-contact poses with the crown sets included: 56 bench and 135 held (the lead: 33 and 71).
- The overhead poses' 10th-percentile metal is 1.83 mm, the same as the lead's.

**Contact**

| | contact poses | summed depth | deepest |
|---|---|---|---|
| bench | 13 | 46.18 mm | 9.79 mm at ws (30, 135, 0), hub 2, a relayed pose |
| held | 43 | 173.02 mm | 12.24 mm at (15, 135, -15) |

- Bench: 9 of the 13 contacts are relayed poses, and 1 is the arm-fixed coil (466, -2.95 mm).

**In-band**

- Chain-only in-band is 0.8898 (pooled 0.9132), and 0.9098 with the band read as 3-14 mm.
- The clip-frame metal histogram has 0.06 % of samples at 1-2 mm and 0.34 % at 2-3 mm, so nothing sits on the band
  edge.
- Per part: hub3 0.742, L2 0.731 and crank 0.801 are the lowest. The relay's skin-facing hardware is 0.98 in band on
  344 samples per frame. That is why the claim is the chain-only gate and not the pooled 13.74, which would read
  score 95.00.

**Springs, stops, cuff, singular postures**

- The relay is a constant-force coil. R17 is inherited from proxtrack: 0.063 N.m, F >= 0.79 N. Friction and the
  carriage's return are not measured (finding M5).
- The J2 stops hold the th margin at min 5.000 deg. How many taken poses sit within 5-6 deg of th is not on file.
- Cuff twist is not measured: no R17 posture sweep has been run on this hardware.
- The two-pin cuff knee moves 46.7 deg (K.ang 59.3-105.9). The relay moves up to 32.94 deg (33 relayed bench poses,
  110 held).
- Continuity: flood on file (verifier_claim.json pick.continuity) with 0 relayed poses dropped. 153 of 154 relayed
  env poses are connected, and 21 phi-jump edges are refused.

## Findings

1. **T5, contact depth (watch).**
   - Bench: summed 46.18 mm against the lead's 20.24 mm (x2.28, +25.94 mm).
   - Held: 173.02 mm against 60.97 mm (x2.84, +112.05 mm).
   - Every new contact is a pose the lead loses to the fold (9 bench, 29 held). The score charges these poses, so it
     does not reward them. The wearer, though, gets hub 2 pressed 9.8 mm into the arm on a plain scapular-plane raise
     to 135 deg, where the lead gives a stop.
   - Action: price these relayed contacts before calling the relay a reach gain on that arc.
2. **G1, metal hugging (watch).**
   - The design is +4.54 ahead of the lead plain, but 11.24 behind at 2 mm (46.08 vs 34.84, both measured with
     deep_audit). It is still ahead at 1 mm (17.91 vs 19.92).
   - Held with the model's own near2: 41.29 vs 37.10.
   - 8 of the 24 new takes have metal < 2 mm.
   - This is report-only under the user's 2026-10-17 ruling.
3. **NEW-clearance-floor (watch).**
   - The E strap rides 1.002 mm over the carriage, 0.002 mm past the 1 mm jam rule, on the everyday clip frames.
   - 112 taken poses are below 1.1 mm.
   - A 0.2 mm build margin costs +0.12 (bump 1.2 reads 14.88).
   - Action: quote 14.88 as the toleranced number next to 14.76.
4. **T4, cliff pick (watch).**
   - delta 5.0 reads 27.53 (37 jams), only 0.5 deg (0.7 mm) from the pick. ds 34 at delta 4.5 reads 47.80.
   - The offset itself is worth 0.03 (envsel 15.64 -> 15.61).
   - Action: read the pick at ± build tolerance, or move delta inward from the cliff (delta 0 costs about 0.03).
5. **M5 / G2 / G3, return spring (watch).**
   - The inherited R17 covers chain gravity only. Tape friction against the 0.79 N coil under cuff load, and the 3
     bistable relay poses, are unmeasured.
   - Action: run a return / hysteresis test on this hardware.
6. **G6, 4th joint (watch).**
   - The 3.52-point lead over the 3R lead comes from a counted 4th joint (complexity 52.5 vs 18.5) and buys no
     overhead (8/28 = 8/28).
   - The count is honest.
   - Action: never display this row as the overall leader.
7. **P1, claim-bench informed selection (watch).**
   - ds 31 was read on the claim bench (14.26) before the envsel selection. Envsel then broke ties of 0.04 and 0.03.
   - The held-out result shows no over-fit (+3.01, below proxtrack's +4.0 and the lead's +4.10).
   - The planned lug-coil re-claim would be chosen on the claim bench (14.23), because envsel ties the two coils
     (15.61 / 15.61). Label it P1 and claim it held.

Checked and not present:
- T2: the band read as 3-14 mm leaves 13.74 unchanged.
- T3: the margin is read on th, 5.000 deg.
- S1: held +3.01.
- S2 / S3: part-weighted in-band 0.924 against sample-weighted 0.913, and all 15 groups are sampled. L1a is thin at
  8 samples per frame.
- S5: 0 dropped.
- M1 / M2: every part is a real component at O20.
- M3: the verifier's X1 / X2 checks add 0 jams. The coil's missing mount is priced at 0.00 with a shell tab.
- M4: K moves 46.3 deg, the knee 46.7 deg, the relay 32.9 deg.
- P2: held read once per config.
- P3 / R3: claim read once; the envsel spread is on file.
- P4: no bench or judge file in the row's 2 commits.
- R1 / R2 / R4: the row, verifier and dashboard agree on 14.76.
- G5: complexity recomputes to 52.5.

## Tool readings that are gaps of the instrument, not of the design (proposals for the tool owner)

- **continuity (watch).** It reads "no flood on file", but the flood is on file at
  docs/concepts/verify/offset-shortcar-relay-4r/verifier_claim.json and verifier_held.json under
  pick.continuity (dropped_relayed 0). Proposal: also read `<verify>/<id>/*.json:*.continuity`.
- **T5 against the lead is blind.** `_depth_sources` raises on
  docs/alignment/remeasure/desmo-geom-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json, where held is the string
  "missing dump" (commit 46af77e, 11:37). Because of that, every audit against conecut-knee-knuckle-3r since then has
  printed "no bench depth of conecut-knee-knuckle-3r on file". Proposal: skip any wear entry that is not a dict.
  Measured effect on this row: T5 goes from silent to watch (x2.28 bench).
- **Relay-family numbers missed.** Before this audit's re-wear, near_touch, idle and sampling read "not on file". The
  data were in the row (`frozen_exact.near1` / `near2`) and in the verifier dumps under keys the tool does not read.
  The adapter tools/alignment_wear_offset_relay.py, a new file, now re-wears this family.

## Proposals (measurement changes, not applied, not used in the verdict)

- **A1. A tolerance column.** When a claim's part-to-part clearance sits within 0.2 mm of a jam floor, the claim also
  reports the reading at floor + 0.2 mm.
  - Measured on this row: 14.76 -> 14.88 (+0.12).
  - Other verified rows: not measured. The bump floor exists only in the proxtrack relay family.
- **A2. A cliff read.** The verifier reads every hardware parameter of the pick at ± its build tolerance (0.5 deg /
  0.5 mm) and reports the worst reading as a column, never as the score.
  - Measured on this row: delta +0.5 deg -> 27.53.
  - Other verified rows: not measured.
- **A3. T5 split by the reference's fate.** Contact poses that the reference loses to the fold get their own count and
  depth, so a relay or a 4th joint that turns stops into presses is visible.
  - Measured on this row: 9 / 13 bench and 29 / 43 held.

## Numbers this audit could not get

- **The held re-wear, and so held near-touch at 2 / 3 mm on the deep_audit basis.** The 4-core box was at load ~12
  and the held prepare plus wear takes about 15 min. The farm budget is spent (CLAUDE.md, 15:49 status). Held depths
  and takes come from the verifier's dump instead, which reproduces held plain 16.64.
- **R17 friction / return and cuff twist.** No judge exists for this hardware.
- **The th distribution near 5 deg.** Only min, n and lt5 are on file.
- **Per-part density** (tools/sample_density.py): not run, time box.

Files from this audit:
- docs/alignment/offset-shortcar-relay-4r.json
- docs/alignment/offset-shortcar-relay-4r.findings.json
- docs/alignment/remeasure/offset-shortcar-relay-4r_bench.json
- docs/alignment/remeasure/offset-shortcar-relay-4r_bench_perpose.json
- tools/alignment_wear_offset_relay.py
