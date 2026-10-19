# Alignment audit: proxtrack-relay-knuckle-4r

Auditor run of 2026-10-18 ~21:30 UTC (hourly audit; due because this row had no ledger entry). The row is status
"screened", carries v_gap 17.46, and HANDOFF compares other designs against it as a peer of the verified rows.
Ledger entry: 2026-10-18T21:30:13Z, `python3 tools/alignment_ledger.py get proxtrack-relay-knuckle-4r`.

## Verdict: GAMED (tool alone: watch). Claim: v_gap 17.46

- **What the claim is.** v_gap 17.46 is the verifier's price of a buildable pin-a stack: frozen exact Bench(110,360),
  gate = chain-only in-band, score 93.65. Held out it is 21.46. The design's own claim, gate 14.40 / plain 14.02, was
  REFUTED as modelled: its bumped pin-a boss sits 5.05-5.08 mm inside the knee link at every fit pose.
- **The 17.46 reproduces exactly.** This audit re-wore it, bench 17.46 and held 21.46, recomputed from per-pose dumps.
- **Why the verdict is gamed.** It comes from the reporting, not from the 17.46. The row is still "screened", so the
  dashboard treats the refuted design as live. Its fast numbers then become the board's headline candidates:
  "best claimed row" 4.15 (score 98.49) and "best sweep configuration (live, unreviewed)" 4.25. Both lines rank it
  above two verified 4-joint designs that are better for the wearer.
- **Everything else is watch.** Deeper contact than the lead, metal hugging at 1-2 mm, an unmodelled stack fix, a
  spring with no hold check, relayed poses parked on the fold-margin floor, a shell lift parked at its search floor,
  in-band dilution on the plain number, and a pre-registered kill that the design outlived through a re-spec.

## What the wearer gets (measured, buildable stack, frozen exact)

Files: `docs/alignment/remeasure/proxtrack-relay-knuckle-4r_{bench,held}_probe.json` and
`..._{bench,held}_stackfix_perpose.json`, made by the new adapter `tools/alignment_wear_probe_proxtrack.py`. The
adapter runs the model and the buildability verifier's harness unchanged and only records.

| | bench Bench(110,360) | held out | lead conecut-knee (bench / held) |
|---|---|---|---|
| gap: gate / plain / near1 / near2 | 17.46 / 14.40 / 18.06 / 38.39 | 21.46 / 18.37 / 23.75 / 42.24 | 18.28 / 22.38; near2 34.84 bench |
| reach (ws taken / total) | 0.7917 (285 / 360) | 0.7689 (732 / 952) | 262 / 360, 659 / 952 |
| overhead taken (elev >= 140) | 8 / 28 | 18 / 71 | 8 / 28, 18 / 71 (the relay buys no overhead) |
| raised-arm reach (elev >= 90) | 62 / 113 | 163 / 300 | 47 / 113, 123 / 300 |
| taken poses with metal < 1 / 2 / 3 mm (all metal) | 7 / 57 / 145 of 395 | 26 / 132 / 319 of 934 | bench 3 / 33 / 105 |
| contact poses, summed depth, deepest | 13, 50.36 mm, 9.79 mm at (30, 135, 0), relayed at phi 11.3 | 47, 189.82 mm, 12.23 mm at (15, 135, -15), relayed at phi 18.5 | 4 / 20.24 mm; 14 / 60.97 mm |
| workspace in-band, chain metal only (taken ws) | 0.8316 (16.6 % over 14 mm) | 0.8344 | 0.8676 / 0.8712 |
| overhead in-band, chain only | 0.9039 | 0.9000 | 0.9359 bench |
| min th margin over taken poses | 5.000 (0 below 5; relayed poses at exactly 5.000) | 5.000 | - |
| jams / continuity | 5 jams; connected = static, 0 dropped | 17 jams; 0 dropped | - |

**Springs, stops and cuff.**
- The relay is a passive coordinate on a constant-force spring at 0.063 N.m preload. That covers gravity only.
- The spring has no part number and no sampled envelope.
- The stops are two ISO 8734 dowels on the relay's own angle, which is buildable.
- Cuff twist and an R17 dynamics run for this design are not on file, so they were NOT MEASURED.
- 3 bench poses are bistable: the relay has two feasible ranges.
- The folded-side relays are one-sided, and they are the deepest contacts.

**Remeasured as modelled.** gate 14.40 / plain 14.02 / near1 17.68, recomputed 14.40, which reproduces the claim and
both verifier lenses.

**Not obtained.**
- `tools/alignment_audit.py remeasure` and `tools/alignment_paired.py dump` do not support this model: it has no
  frozen() / PK.audit. The new adapter replaces them.
- Idle spans of K, the crank and the knee were not recorded. From the verifier's files instead:
  - K is forced (dK != 0) on 186 of 395 taken bench poses;
  - the relay phi runs 0 to 32.94 deg;
  - the knee link turns 38 deg relative to the carriage.
- No per-part in-band record.
- No skin-bulge check of the low shell.
- No cuff twist or R17.
- The held base (as modelled) was not re-worn by this audit; the verifier's held figures are used.

## Findings

1. **R2: a refuted record is displayed as a live candidate (GAMED).**
   - The row is status "screened" despite `refuted_by` and v_verdict "REFUTED as modelled".
   - `docs/dashboard/core.js` (lines 9-23) builds the hero's claim and sweep candidates from all live rows, with no
     refuted and no joint-count filter.
   - So the hero names this design twice: gap 4.15 "waiting for the verifier" and 4.25 "live, unreviewed". Those sit
     13.31 / 13.21 below its verified-buildable 17.46.
   - That ranks it above offset-shortcar-relay-4r and freek-oracle-route-knuckle-4r.
     - offset-shortcar-relay-4r: verified 14.76 / held 17.77, same complexity 52.5, paired better on held out by
       -1.73 (CI90 [-2.91, -0.81], P 1.00; `docs/concepts/verify/offset-shortcar-relay-4r/paired_held.json`).
     - freek-oracle-route-knuckle-4r: verified 15.40 / held 20.50.
   - **Why the exo is not better.** The displayed number belongs to the refuted, unbuildable model.
   - **Action (lead):** set the row's status to "refuted", or make core.js skip rows with `refuted_by` and apply the
     <= 3-joint filter on the claim / sweep lines. No score changes. The finding resolves when the hero no longer
     names this design.
2. **R1: peer comparison and the diluted plain number (watch).**
   - HANDOFF 11:15 headlined "14.02 plain (score 94.90)".
   - HANDOFF 15:00 lists proxtrack among the verified peers ("paired better than the lead, freek and proxtrack").
   - The row's v_gap_plain 14.40 is the buildable stack on the pooled in-band. It is the same number as the refuted
     as-modelled gate. Only v_gap 17.46 stands.
3. **NEW-inband-dilution (watch).**
   - The arm-fixed shell underside adds 303 samples per pose, 99.5 % in band, at about kit density.
   - They lift pooled ib14 from 0.8656 to 0.8962 on the buildable stack, which is 3.06 points: plain 14.40 against
     gate 17.46.
   - The chain itself rides further off the arm than the lead's: workspace chain in-band 0.8316 against 0.8676.
   - The claim's gate already excludes this metal. The plain number does not.
4. **T5: depth-blind contact (watch).**
   - Bench: 50.36 mm summed against the lead's 20.24 (x2.49).
   - Held out: 189.82 against 60.97 (x3.11), deepest 12.23 mm.
   - 9 of 13 bench and 32 of 47 held contacts are relayed poses.
   - **Instrument gap:** the tool's contact_depth printed these sums but did not find the lead's dumps as a reference.
5. **G1: hugging at 1-2 mm (watch, report only).**
   - 57 taken bench poses have metal under 2 mm, against the lead's 33.
   - 23.99 points of the gap live in the 1-2 mm shell, against the lead's 16.56.
   - Against the lead it is ahead plain by 3.88 and behind at 2 mm by 3.55.
6. **M3: the priced stack is a verifier's patch, not a checked part (watch).**
   - The lifted knee eye (5.69 mm over pin a) was checked only against the shell top.
   - It was not checked against the E strap, the MR63ZZ knee-pin stack or the pad.
7. **M5: the spring's hold is not shown (watch).**
   - The 0.063 N.m preload covers gravity only; carriage friction and hysteresis are not in it.
   - The spring has no part or envelope.
   - 3 bench poses are bistable, and the one-sided relays are the deepest contacts.
   - No R17 run and no cuff-twist number.
8. **G4: zero margin slack on every relayed pose (watch).**
   - 23 bench and 74 held relayed poses sit at exactly 5.000 deg of th.
   - The stop margin was not searched as a design variable (CLAUDE.md: 9-12 deg optimum where a passive coordinate
     takes poses past the stop).
   - The feel near the edge has not been red-teamed.
9. **T4: the optimum on its search floor, toward the skin (watch).**
   - rt_extra sits at the box edge 1.5, below the spec's 2-3.5. At 2.5 the gate reads 15.26 against 14.40.
   - The skin-bulge check the claim asked for is in neither verifier report.
10. **NEW-postreg-respec (watch).**
    - The pre-registered config was killed at 20.59 (kill line 17.5).
    - The bump spec was then revised (16.82 at the same config) and the config re-picked (14.40).
    - The verified buildable 17.46 sits 0.04 under the kill line, less than one ws pose (0.28 points).
    - No over-fit shows: bench -> held +4.00 against the lead's +4.10.

**Checked, not present.**
- P1 (held +4.00) and P2 (held read once, never searched).
- P4 (no bench, judge or metric file in the row's 5 commits).
- S5: connected = static on bench and held; the verifier's strict and contact-aware floods agree. The tool's
  continuity watch is an instrument gap: it does not read `*-remeasure_flood.json`.
- T3: th is read on the one metric.
- M4: the relay, K and the knee all move.
- G5 / G6: complexity 52.5 recomputed; 4 DOF, which is within the cap. The board does mark 4-joint designs, but the
  hero's candidate lines do not (finding 1).

## Proposals (proposals only, no input to the verdict)

- **Catalogue entry S7, in-band dilution by arm-fixed metal.**
  - Looks like: pooled in-band rises because a large, uniformly in-band part (a shell, a plate) adds samples. The
    moving chain's own in-band does not rise.
  - Detect: report chain-only and pooled in-band side by side, and give watch when they differ by more than 1 gap point.
  - Measured effect on the rows that carry both readings:
    - proxtrack: 3.06 points (buildable), 0.38 (as modelled);
    - offset-shortcar-relay-4r: its gate 14.76 against plain 13.74, 1.02 points.
  - The other verified rows have no chain-only / pooled split on file; their effect is NOT MEASURED, and would be 0 for rows with no arm-fixed part.
- **Catalogue entry P5, re-spec after a pre-registered kill.**
  - Looks like: a pre-registered config fails its kill, the spec is revised, and the design goes on.
  - Detect: an events.jsonl "KILL" reading followed by a screen pass on the same id.
  - Action: report the registered outcome next to the final one.
- **Instrument fixes (new readers, no metric change).**
  - contact_depth should resolve the lead's own perpose dumps as the reference.
  - continuity should read `docs/concepts/verify/<id>-remeasure_flood.json` and a row's `frozen_exact.continuity`.
  - near_touch should read a row's `frozen_exact.near1_gap / near2_gap`.
  - remeasure should accept models with an evaluate() / prepare + wear interface, as
    `tools/alignment_wear_probe_proxtrack.py` does.
- **Dashboard (lead's call):** the hero's claim and sweep lines should skip rows with `refuted_by` or status
  refuted, and apply the same <= 3-joint filter as the verified leader.

## Next

- The lead fixes the row status or the board filter (finding 1).
- The skeptic rules on R2.
- A future design pass models the lifted knee stack as one part and checks it against the E strap and the knee-pin
  stack.
- An R17 / cuff-twist run on the relay spring with carriage friction.

## Skeptic (2026-10-18 ~22:00 UTC): final verdict WATCH (was gamed)

The ledger computed the verdict: `python3 tools/alignment_ledger.py skeptic ...`, entry 2026-10-18T21:59:37Z.

- **Refuted (4):** near_touch, continuity, idle, judgement:R2.
- **Upheld (11):** every other reason.
- **Rulings file:** `docs/alignment/proxtrack-relay-knuckle-4r.rulings.json`.
- **New measurement:** `tools/alignment_skeptic_probe_proxtrack.py` re-ran the model unchanged through the
  buildability verifier's harness (buildable stack, frozen exact Bench(110,360); nice 10, 1 process, 344 s).
  - It reproduces gate 17.46 / plain 14.40.
  - Output: `docs/alignment/remeasure/proxtrack-relay-knuckle-4r_bench_skeptic.json`.

### Refuted

- **near_touch.** The numbers are on file; the tool did not read them.
  - Row: v_gap_near1 18.06, held_out_gap_near1 23.75, frozen_exact.near1_gap 17.68 / near2_gap 38.01.
  - Buildable stack: price_stackfix.json near1 18.06 / near2 38.39.
  - The tool's `_near_numbers` skips the top-level `v_gap_near1`.
  - Since 2026-10-17 near-touch is report only (level ok).
- **continuity.** remeasure_flood.json kin_strict: bench 285 -> 285, held 731 -> 731, 0 dropped, 0 branch changes.
  The contact-aware flood reads the same.
  - The buildable stack has the same relay solve (relayed 33 / 23 / 9 / 1, phi_max 32.94), and its
    probe.continuity shows 0 dropped.
  - Connected loss 0.00, under conn_watch 1.0.
- **idle.** Measured over the 395 taken poses:
  - K (dK) spans 46.29 deg and is forced on 186;
  - the relay phi spans 0-32.94 deg, nonzero on 23;
  - the knee link turns 38 deg (remeasure.md line 114).
  - All are far above idle_deg 2.0.
- **judgement:R2.** The facts reproduce, and the defect stays a watch under `reporting`. The gamed level does not stand:
  - **The facts.** On morphs.json v151 (21:50, after the audit), core.js's claim and sweep picks are still proxtrack
    4.15 / 4.25.
  - **No documented gamed level.** No threshold or code path gives gamed for a displayed number. Section 5 has no
    reporting threshold, and `c_reporting` sets dashboard defects to watch.
  - **Precedent.** All 21 earlier judgement:R2 ledger entries are watch. That includes underpass-bridge-relay-4r at
    20:52, the identical case.
  - **Not like for like.** The hero's claim / sweep lines take the lowest fast number of any live row. Verified 4-joint
    rows never enter the hero. Without proxtrack, the line would show minarc's 6.19 against its verified 18.40.
  - **What a gamed mark would block is already right.** The leader line is the <= 3-joint lead at 18.28, and
    morphs.json carries v_gap 17.46.
  - **The lead's action still stands:** set the status to refuted, or add a refuted_by filter in core.js.

### Upheld, re-derived from the raw files

- **sampling.** The relay spring coil is still unsampled: coil.json gives chain clearance only, with no skin distance
  and no part number. The flange was priced only as modelled.
  - A rigid-part record now exists (all taken poses, clip + ws). The lowest parts are hub3 0.58 and the lifted knee
    0.66.
- **reporting.** sweep_gap 4.25 against v_gap 17.46, 13.21 > 5.
- **R1.** HANDOFF lines 609-610 headline the pooled plain 14.02 over the pre-registered gate.
  - The 13:05 entry (lines 655-658) records the refutation.
  - Line 664 compares against the buildable held reading (paired_held.json gap_B 18.37), not against a verified
    number.
- **NEW-inband-dilution.** The pooled in-band reproduces exactly:
  (107910 x 0.8656 + 33330 x 0.9953) / 141240 = 0.8962.
  - Workspace chain in-band: 0.8316 against the lead's 0.8676.
- **T5.** Bench: 13 contacts summing 50.36 mm against the lead's 4 summing 20.24 (x2.49). Held: 47 summing 189.82
  against 14 summing 60.97 (x3.11).
  - **New:** the 4 phi-0 bench contacts are the lead's own 4, at identical depths. All +30.12 mm of the extra depth
    comes from relayed poses.
- **G1.** Report only. Shell 23.99 against 16.56, on the same pooled lens. This is c_dominance's watch pattern.
- **M3.** The lifted eye was checked only against the shell top. No E strap, MR63ZZ or pad check is on file.
- **M5.** The preload is gravity only, the spring has no part, 3 poses are bistable, and there is no R17 or cuff-twist
  run for this id.
- **G4.** Wording corrected, pattern stands. The 23 relayed taken poses sit at th 5.0001-5.0542 deg (median 5.0089),
  not "exactly 5.000". The 12 lowest of all 395 taken poses are relayed, and the minimum at phi 0 is 5.181.
- **T4.** rt_extra sits at its box edge 1.5. At 2.5 the gate reads 15.26: the low shell lowers the chain-only gate too.
  No bulge check is in the verifier docs.
- **NEW-postreg-respec.** The KILL at 20.59 is on file (events line 830; kill > 17.5). v_gap 17.46 sits 0.04 under the
  kill line. Held drift is +4.00 against the lead's +4.10.

### Missed by the audit (for the next audit; not counted in this verdict)

1. **Mixed lens on the row's near-touch numbers.** v_gap 17.46 is on the GATE lens (chain-only in-band), but
   v_gap_near1 18.06 and held_out_gap_near1 23.75 are POOLED.
   - Why pooled: PT.wear's near1 is pooled. price_flange.json near1 17.68 equals remeasure_bench.json
     mine.near1.gap_pooled 17.68, and the stackfix near1 18.06 goes with wear.inband14 0.8962 (pooled), not
     ib14_gate 0.8656.
   - On the v_gap lens, near1 is 17.68 + 100 x (0.90 - 0.8656) = 21.12 on the bench and about 26.8 held.
   - So the row shows near-touch costing +0.60 over v_gap when on the same lens it costs +3.66. It is report only, but
     anyone comparing near1 across rows is misled.
2. **All of the extra contact depth is the relay's.** The relayed poses add 9 bench contacts (30.12 mm), all on top of
   the lead's unchanged 4. Bench per-pose dumps of both designs: `docs/alignment/remeasure/
   proxtrack-relay-knuckle-4r_bench_stackfix_perpose.json` and `conecut-knee-knuckle-3r_bench_perpose.json`.
   - The score does charge these: a contact pose is neither reached nor free, so the relay pays for it in the gap.
   - The depth (9.79 mm deepest) is what it does not see.

**Final verdict: WATCH** (ledger 2026-10-18T21:59:37Z).
