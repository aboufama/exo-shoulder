# Alignment audit: phi40-thinstack-relay-4r (round 107, lens A fallback, slice r107-B)

Auditor run 2026-10-18 ~21:21-21:55 UTC, after the row turned verified (commit 36a87d4, 21:09). The tool is
tools/alignment_audit.py version 2026-10-18.1, run with reference conecut-knee-knuckle-3r (the verified 3-active lead).
The earlier audit of the screened claim (21:05, same day) is replaced by this one. Ledger:
`python3 tools/alignment_ledger.py get phi40-thinstack-relay-4r`.

## Verdict: WATCH (verified v_gap 14.06, score 94.89; held 16.69)

- The claim is v_gap 14.06 on frozen exact Bench(110,360) (chain-only buildable gate, plain 13.52), read once at the
  pre-registered envsel pick PHI 40 / delta 3.5. Held out it reads 16.69 (plain 16.02). It misses the 95 line (13.75)
  by 0.31.
- The verifier (docs/concepts/verify/phi40-thinstack-relay-4r-verify.py) reproduces 14.06 / 16.69 and adds X1-X3 with 0
  new jams and 0 new contacts.
- Three per-pose dumps exist: the row's, this auditor's re-wear and the verifier's. They are identical pose for pose:
  470 bench and 1154 held poses, 0 differences in the taken / contact / evaluated flags, max metal difference 0.000 mm.
  The verifier imports the claim model unchanged, so this agreement shows a deterministic re-run, not a second
  implementation (see proposal A4).
- No hard rule is broken: O20 hubs, fold margin min 5.000 deg in th (0 of 400 taken bench poses and 0 of 952 held
  below 5), 0 passive translations, 4 DOF (at the cap). Complexity recomputes to 51.25.
- Nothing here shows the number ranking this design above a design that is better for the wearer under a gate the user
  keeps, so nothing is gamed. The verdict is watch: 3 tool items and 7 judgement findings.

## Re-wear

- No new re-wear was run. The verification commit changed no parameter: the row diff only adds the v_* fields, the
  status and the verifier's text, and the claim is unchanged at 14.06. Re-wearing the same configuration would repeat
  the 20:56 / 21:03 re-wears (docs/alignment/remeasure/phi40-thinstack-relay-4r_{bench,held}.json, gate 14.06 / 16.69
  reproduced to 0.00). Those re-wears now agree with the verifier's dumps to the bit.
- In their place this audit ran one new diagnostic, the thin shell's share (finding M2): the claim model unchanged, its
  own exact Bench(110,360) prepare, and the pick worn at tsh 1.5 and at tsh 1.0 as the control
  (docs/alignment/remeasure/phi40-thinstack-relay-4r_tsh.json; numbers in M2). One niced process with OMP_NUM_THREADS=1. The machine was at load
  ~10 from other agents' re-wears.

## Tool checks (docs/alignment/phi40-thinstack-relay-4r.json)

Three of the 14 checks read watch. The other 11 read ok.

- **dominance (watch):** the row beats conecut-knee-knuckle-3r by 4.76 plain and loses to it by 12.32 at 2 mm. The A1
  gate is retired, so this is report-only.
- **continuity (watch):** this is a gap in the instrument, not in the design. The tool reads "no flood on file", but
  the PHI 40 flood is on file in claim_phi40.json and held.json (pick.continuity). The verifier re-ran it: 0 relayed
  poses dropped, 0 phi-0 poses not connected, static gap = plain on both benches (verifier_claim.log and
  verifier_held.log, conn).
- **reporting (watch):** the row's `verdict` field still reads "SCREENED ... Needs an independent verifier", but its
  status is verified and v_gap is set. The dashboard row (docs/dashboard/data/morphs.json) carries the same stale text,
  and its alignment_reasons still show the old "held_out: no verified bench gap". The stale text understates the row,
  so it flatters nothing. The row's owner should update it.
- **held_out (now ok):** held 16.69 against bench 14.06, +2.63, under the 6.0 watch line.

## What the wearer gets (measured)

Sources: docs/alignment/remeasure/phi40-thinstack-relay-4r_{bench,held}.json and _perpose.json. These are identical to
docs/concepts/verify/phi40-thinstack-relay-4r/verifier_{claim,held}_perpose.json.

| | bench | held |
|---|---|---|
| Overhead taken (elev >= 140) | 9 / 28 | 22 / 71 |
| Raised arm taken (elev >= 90) | 67 / 113 | 176 / 300 |
| Elev >= 160 taken | 3 / 15 | 9 / 36 |
| Workspace taken | 290 / 360 | 750 / 952 |
| Taken poses with metal < 1 / 2 / 3 mm | 9 / 50 / 136 (overhead 0 / 3 / 8) | 32 / 123 / 305 (overhead 4 / 9 / 20) |
| Min metal on a taken pose | 0.072 mm | 0.10 mm |
| Overhead metal, 10th percentile | 1.80 mm | 0.62 mm |
| Contact poses / summed depth / deeper than 3 mm | 17 / 74.92 mm / 7 | 48 / 198.11 mm / 23 |
| Deepest contact | 15.37 mm at ws (30, 150, -30), relay phi 39.7 | 13.89 mm at ws (45, 150, -15), phi 35.2 |
| In-band 2-14 chain-only / pooled | 0.8946 / 0.9169 | 0.8933 / 0.9160 |
| Gap at metal < 1 / 2 / 3 mm (deep basis) | 18.18 / 47.16 / 100.73 | 22.99 / 47.92 / 97.52 |

For comparison, the 3-active lead conecut-knee-knuckle-3r takes 8 / 28 overhead on the bench (18 / 71 held) and
47 / 113 raised (123 / 300). Its contacts are 4 / 20.24 mm on the bench and 14 / 60.97 mm held, recomputed here from
docs/alignment/remeasure/conecut-knee-knuckle-3r_{bench,held}_perpose.json, which reproduce 18.29 / 22.38.

**Springs, stops, cuff, singular postures**

- The relay is a constant-force coil (12 x 10) on the carriage lug. Its margin over gravity plus tape friction is
  0.22-0.62 N on 2.0 N. Return, hysteresis and cuff twist are not on file (M5).
- The J2 stops hold th at 5.000 deg minimum. The 5 lowest taken poses sit at 5.000-5.003 deg (verifier_claim.json
  pick.th_margin), so the stops are in use.
- The relay travels up to phi 39.88 deg (bench: 41 relayed poses, 28 taken, 13 contacts, 0 jams). The cuff knee moves
  46.7 deg.
- Internal clearances (verifier X1, taken poses):
  - The E strap rides over the carriage at 1.200 mm, 0.2 mm above the 1 mm non-adjacent rule. 255 of 400 bench and
    578 held taken poses sit under 1.5 mm.
  - The knee crown sits 0.52 mm from the L-lug bracket (read as an adjacent pair).
  - Both are looser than the verified parent's (E over carriage 1.002 mm, crown vs bracket 0.216 mm, 182 bench poses
    under 1.2 mm; docs/concepts/verify/offset-shortcar-relay-4r/verifier_claim.json). This row raised the margin, so it
    is not a finding.
  - Note: the verifier's text calls the parent's crown clearance 1.4 mm, but the parent's own verifier file reads
    0.216 mm. The error runs against this row, not for it.

## Findings

1. **T5, contact depth (watch).**
   - Bench: 17 contacts, 74.92 mm summed, against the lead's 4 / 20.24 mm (x3.70).
   - Held: 48 contacts, 198.11 mm, against 14 / 60.97 mm (x3.25).
   - The PHI 35 -> 40 band turns 4 relay-stop poses into presses: 15.37 mm at an overhead scapular-plane raise, 13.78,
     1.27 and 0.95 mm, summed 31.36 mm.
   - Since this audit the depths are verified depths: three identical dumps.
   - Why this is not a better exo: the score charges these poses no more than a lost pose plus a contact share. The
     wearer gets a 15 mm press where PHI 35 gives a stop.
   - Action: a skin-aware relay stop near phi 37, or price the band's contacts before calling PHI 40 a reach gain.
2. **G1, metal hugging in the PHI band (watch).**
   - PHI 40 against PHI 35 on the same hardware and harness: plain -0.21, 1 mm +0.27, 2 mm +1.08.
   - Of the 8 bench poses the band evaluates, 4 are contacts, and 3 of the 4 takes are under 2 mm (0.21 / 1.08 /
     1.74 mm).
   - Held: every overhead take the row adds over the lead and the parent sits at 0.10-0.62 mm.
   - Against the parent the row is ahead plain and behind at 1 mm and 2 mm.
   - This is report-only under the 2026-10-17 ruling.
3. **S3, the coil strip (watch).**
   - The verified number stands only for a free steel strip that sags 2.49 mm into the 4 mm cuff liner (r 76.61
     against R_liner 79.1). It passes 1.30-1.90 mm from the skin on 4 held poses (800, 865, 793, 929, phi 33-38) and
     at 1.94 mm on 1 bench pose.
   - Guiding the strip instead loses 326 / 417 bench and 776 / 1000 held poses (172.40 / 175.85).
   - The liner groove is in neither the model nor the mechanism record, the strip is not sampled in the in-band, and
     its liner friction is not in the spring budget.
   - Action: put the strip and its liner relief in the model (sampled as metal) and in the mechanism record, then
     re-wear.
4. **M5, return spring (watch).** The margin is 0.22-0.62 N on 2.0 N. The coil is on a new lug, the travel is now
   40 deg, and strip-on-liner friction (S3) is not budgeted. Action: a return / hysteresis / cuff-twist test on this
   hardware.
5. **M2, the 1.0 mm slotted shell (watch).** The thin shell carries a third of the row's gain over its parent, and its stiffness is not shown.
   - This audit's diagnostic (docs/alignment/remeasure/phi40-thinstack-relay-4r_tsh.json) wore the pick twice on its
     own exact Bench(110,360) prepare, with the claim model unchanged:
     - tsh 1.5 (the parent family's shell) reads **14.30**: chain-only in-band 0.8922, pooled 0.9150.
     - The control, tsh 1.0, reads **14.06**: 0.8946 / 0.9169, which reproduces the verified number to 0.00.
     - Plain 13.52, reach 0.8056, 17 contacts, 0 jams, near1 18.18 and near2 38.82 are the same in both.
   - So the 1.0 mm shell is worth 0.24 of the row's 0.70 over offset-shortcar-relay-4r (14.76), all of it chain
     in-band. The E strap and knee link ride 0.5 mm lower: R_b falls from 83.2 to 82.7 mm.
   - Stiffness: the verifier estimates that the two 4 x 1 mm lips deflect about 0.6 mm at 5 N mid-span when
     unsupported. Checked here: F L^3 / 48 E I with E 114 GPa, I 2 x (4 x 1^3 / 12) mm^4 and L 75 mm gives 0.58 mm.
     The liner carries inward loads only.
   - The E strap clears the carriage by 1.200 mm, 0.2 mm above the 1 mm rule. On 255 of 400 bench and 578 held taken
     poses the clearance is under 1.5 mm. An outward cuff load of a few newtons, lifting the carriage on its lips,
     would take those poses under the rule.
   - Why watch and not gamed: a 1.0 mm Ti sheet is a real part, the margin is better than the parent's, and the row
     misses 95 at either thickness.
   - Action: build the shell section as L1 CAD and run a CalculiX check of the lips under an outward carriage load (or
     state a liner bond or a back-up strap) before the 0.24 is counted as real.
   - This diagnostic is a seventh reading of the claim bench (14.30). It is worse than the claim and changes no pick.
6. **G6, 4th joint (watch).**
   - The 4.22-point lead over the 3-active lead comes from a counted 4th joint: complexity 51.25 against 18.5.
   - The overhead it adds is skin-hugging: bench +1 take at 1.08 mm, held +4 at 0.10-0.62 mm.
   - The real gain is the raised arm, 67 against 47 of 113.
   - The count is honest. Never display this row as the overall leader.
7. **P1, forward (watch).**
   - The claim bench has now been read at six configurations of this hardware: 14.06 (claim), 13.67 (delta 5.0),
     13.55 (lean 0), 14.02 (delta 6.0, 5 jams), 14.28 (PHI 35) and 14.01 (the verifier's delta 3.0 red team).
   - The two best readings sit under the 95 line, and the row's next step plans exactly those levers.
   - Action: that row must claim on held or on a fresh bench, never on Bench(110,360).

Checked and not present:
- **T1, T2:** covered by G1. The band read as 3-14 mm leaves 13.52 / 16.02 unchanged.
- **T3:** the margin is read on th, 5.000.
- **T4:** the no-jam delta window on the claim bench is at least [3.0, 5.5] (verifier post0 14.01). The pick has
  0.5 deg of margin below and about 2 deg above before jams.
- **S1:** held is +2.63 over the bench.
- **S2:** part-weighted in-band is 0.926 against sample-weighted 0.917.
- **S4:** contact is read on min_mm and cmin of every set, crowns included.
- **S5:** the verifier's flood drops 0 poses.
- **S6:** per-part density was not run (time box).
- **M1:** hubs are O20.
- **M3:** X1 / X2 check every chain set, crowns included, against every relay body, and the clearances listed above
  hold.
- **M4:** K, the knee and the relay all move.
- **P2:** held was read once at the pick.
- **P3 / R3:** the pick was pre-registered on envsel. The spread is on file: 9 readings, top-5 spread 0.41.
- **P4:** no bench, judge or kit file is in the row's 4 commits.
- **R1:** the number shown is verified, and only the verdict text is stale (the tool's reporting item).
- **R2:** nothing is refuted.
- **R4:** the dashboard v_gap 14.06 equals the verified number, and v_contact is set.
- **G2 / G3:** inside M5.
- **G4:** min th is 5.000, and no T4 walk is seen.
- **G5:** complexity recomputes to 51.25.

## Proposals (measurement changes, not applied, not used in the verdict)

- **A1. A band-end column for travel levers.** A row that extends a relay or stop travel reports the takes and
  contacts the extension adds, with metal and depth for each. Measured on this row: PHI 35 -> 40 adds 8 evaluated
  bench poses, 4 of them contacts (31.36 mm), and 3 of the 4 takes are under 2 mm. Of the verified rows, only
  offset-shortcar-relay-4r has such a lever, and its PHI 35 was never compared with a shorter travel.
- **A2. Depth-weighted contact as a reported column, not in the score.** Measured, in mm per evaluated pose: this row
  74.92 / 417 = 0.180, the parent 46.18 / 409 = 0.113, the lead 20.24 / 376 = 0.054. This is the reverse of their gap
  order.
- **A3. The strip / tendon rule.** A spring strip, cable or tendon is sampled as metal along its path in the claim
  model. Measured on this row: 14.06 with the chord, 172.40 with a guide. No other verified row carries a strip.
- **A4. A verifier recomputes at least one reading outside the claim's code.** For example, it recomputes skin
  distance from the posed meshes for the taken poses, or rebuilds the relay geometry from the mechanism record. Here
  the row, the auditor and the verifier all import the same model, and their dumps agree to 0.000 mm. A shared bug
  would pass all three. The proposal changes no number on any verified row. It adds a check whose cost is one extra
  wear per verification.
- **Tool fixes (for the tool owner):** continuity and contact_depth should read `<verify>/<id>/*.json` (pick.continuity)
  and the reference's remeasure dumps.

## Numbers this audit could not get

- **R17 return, friction, hysteresis and cuff twist:** no judge exists for this hardware.
- **Shell lip stiffness by FEA:** the verifier gives a hand estimate only (M2). No CalculiX run was made within the
  time box.
- **PHI 35 held on the same hardware:** it needs a held prepare, ~15-25 min at the current load, and no slot was free.
- **The th distribution between 5 and 6 deg:** only the min and the 5 lowest are on file.
- **Per-part density (tools/sample_density.py):** not run, time box.

Files from this audit:
- docs/alignment/phi40-thinstack-relay-4r.json
- docs/alignment/phi40-thinstack-relay-4r.findings.json
- docs/alignment/phi40-thinstack-relay-4r.md
- docs/alignment/ledger.jsonl
- docs/alignment/remeasure/phi40-thinstack-relay-4r_tsh.json (the M2 diagnostic)
