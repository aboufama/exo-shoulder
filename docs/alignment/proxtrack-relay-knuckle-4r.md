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
