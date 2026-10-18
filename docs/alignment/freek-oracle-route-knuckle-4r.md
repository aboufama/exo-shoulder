# Alignment audit: freek-oracle-route-knuckle-4r (cell B, J3 own-angle stop at q3max 86)

Auditor run 2026-10-18 ~07:30 UTC (tool 2026-10-17.6, `tools/alignment_audit.py audit ... --ref conecut-knee-knuckle-3r`;
re-wear by the new adapter `tools/alignment_remeasure_freek.py`, which runs the model's own `law` path unchanged).

## Verdict: GAMED (ledger), tool alone: WATCH

- **The claim.** Row status "screened", not verified. Its headline `gap` is 9.56, the best of 8 q3max values on Bench(60,160)
  fast, which is also the fit bench. The ledger reads that as the claim, because v_gap is null. The number the design holds is
  **17.35** frozen exact Bench(110,360), connected (static 16.20), score 93.69. That is 0.93 under the verified 3-DOF lead
  conecut-knee-knuckle-3r (18.28).
- **The re-wear reproduces it.** Bench 17.35 connected / 16.20 static (the dump recomputes 17.35). Held out 22.67 connected /
  21.89 static (the dump recomputes 22.66). Files: `docs/alignment/remeasure/freek-oracle-route-knuckle-4r_bench.json` and
  `_held.json`.
- **Why gamed.** Its bench lead over the lead is a coin flip: P(better) 0.56, CI90 [-4.08, +4.09]. That lead was built on the
  claim bench's own failing poses, and it reverses held out: +0.29 worse, P(better) 0.40. Pooled, the two designs tie (-0.08).
  On every wearer-side reading the lead is better: about 4x less contact depth, more overhead reach, one joint fewer and
  complexity 18.5 against 33.25. This is the same pattern as lowarm-halfring-knuckle-3r's P1, which the skeptic upheld as gamed.

## What the wearer gets (measured, cell B q3max 86, frozen exact)

| reading | cell B bench | lead bench | cell B held | lead held |
|---|---|---|---|---|
| plain gap (connected) | 17.35 | 18.28 | 22.67 | 22.38 |
| workspace reach taken | 276 / 360 | 262 / 360 | 693 / 952 | 659 / 952 |
| overhead (elev >= 140) taken | **5 / 28** (static 8) | 8 / 28 | **8 / 71** (static 15) | 18 / 71 |
| raised arm (elev >= 90) taken | 48 / 113 | 47 / 113 | 116 / 300 | 123 / 300 |
| contact poses | 15 (8 overhead) | 4 | 47 (20 overhead) | 14 |
| summed / deepest penetration | 78.55 mm / **20.88 mm** (pose 237, plane 15 elev 165 axial -60) | 20.24 / 8.93 mm (same pose) | 232.2 / 19.9 mm | 60.97 / 9.86 mm |
| taken poses with metal < 1 / 2 mm | 9 / 43 | 3 / 33 | 17 / 86 | 13 / 71 |
| near-touch gap 1 / 2 mm | 22.19 / 45.90 | 19.92 / 34.84 | 26.22 / 47.88 | 25.23 / - |
| scored-clip in-band 2-14 (3-14) | 0.8977 (0.8937) | 0.9012 (0.8994) | 0.8957 (0.8917) | 0.900 |
| fold margin th, model reading (m3e) | min 5.91 (J3-stop poses 9.60) | | min 6.50 | |
| fold margin, family reading (flood's) | 4 taken clip frames 0.76-4.28 deg | | 6 taken clip frames 0.32-4.28 deg | |
| K span / J3-stop engaged | dK 0-81.5 deg / 32 taken poses | | dK 0-77.6 / 61 | |

- **Springs and stops.** The K clock spring holds K. In cell B the J3 dowel reacts that spring on 32 bench poses, with J2 off
  its stop. No R17 lag check, preload sweep or dowel-force check has been run.
- **Cuff and singular postures.** Cuff twist is not measured. The flood finds 0 islands, 0 jump refusals (dK included) and 0
  branch changes. Its edges are symmetric: they are cached per unordered pair and the model has no state. The state-2 wrist
  singularity (J1-K-J2 with J3 locked) is not measured by any reading.

Sources: `remeasure/freek-oracle-route-knuckle-4r_{bench,held}{.json,_conn_perpose.json,_static_perpose.json,_familymargin.json}`,
`remeasure/conecut-knee-knuckle-3r_{bench,held}_perpose.json`, `remeasure/freek-oracle-route-knuckle-4r_conn_vs_conecut-knee-knuckle-3r_paired.json`.

## Findings

The full text and numbers are in `freek-oracle-route-knuckle-4r.findings.json`.

1. **P1 in-sample tuning: GAMED.**
   - The J3 stop was placed from the claim bench's own failing poses: `binder_q3.json` lists Bench(110,360) poses 316, 343,
     369 and 423.
   - The build was triggered by the per-pose free-K oracle, which also ran on the claim bench.
   - q3max was picked on the fast fit bench, then worn on the claim bench at 80 and 86 only.
   - Cell B's gain over its own kit halves held out: 1.26 on the bench, 0.70 held out.
   - Paired against the lead it is -0.93 on the bench (P 0.56) and +0.29 held out (P 0.40).
   - The lead's advantage is contact, not reach. This design has 13 bench contact poses the lead does not; the lead has 2 this
     design does not (held out: 37 and 4).
   - **Action:** claim the held number, or record a leader_ruling "not a lead". Do not re-wear the bench.
2. **T3, fold margin read two ways: watch.**
   - The model's own reading holds (min 5.91).
   - The flood behind the connected claim uses the family reading min(m_sub, m_eff). It drops 4 workspace poses (3 of them
     overhead poses the lead takes), but it never tests clip poses.
   - Under that reading, 4 taken bench clip frames sit at 0.76-4.28 deg (6 held out at 0.32-4.28).
   - Read consistently with the flood, the design scores 20.68 bench and 24.56 held, both behind the lead.
   - Read consistently with the model, it is nearer the static 16.20.
   - **Action:** the verifier rules on one reading. It also measures the state-2 wrist singularity and reports the minimum th
     per state.
3. **NEW-stop-refusal: watch.**
   - Poses 343 and 423 (overhead internal rotation) were 0.2-1.3 mm contacts in the kit. Cell B refuses them at the J3 dowel.
   - Read as the contacts they were, the design scores 17.83 instead of 17.35. So 0.48 of the 0.93 lead is the arm being
     stopped rather than touched.
   - The doc says the same: cell B beats the oracle "ceiling" only because a stop may refuse a pose.
4. **T5, contact depth: watch.** Summed penetration is x3.9 the lead's on the bench (+58.3 mm) and x3.8 held out (+171 mm).
   The deepest press is 20.9 mm, overhead.
5. **G1, metal hugging: watch, reported only.**
   - 43 taken poses sit under 2 mm, against the lead's 33.
   - The plain lead turns into a deficit of 2.27 at 1 mm and 11.06 at 2 mm.
   - The overhead poses it takes sit at 1.1-2.1 mm.
6. **M5, spring hold: watch.** The K spring is held by the new J3 dowel, which takes about 1.5x the spring torque about the arm
   axis. No hold, lag, cuff-twist or dowel-force check exists.
7. **G6, 4th counted joint: watch.** K is counted honestly as 4 DOF with complexity 33.25. But a coin-flip bench lead over the
   3-DOF lead is not grounds for a 4-DOF lead under the user's "push for 3".
8. **R4, reporting: watch.**
   - The dashboard shows the row at 9.56, a score of 96.52. That is the fast in-sample best, shown with frozen_gap null.
   - The cause: `tools/dash_build.py` does not read the row's `frozen_gap` key.
   - The ledger's claim reads 9.56 for the same reason.

Not findings (checked):
- **The free-K oracle.** It is cell A, a bound. The claim path sets `ODesign.TAB = None` (law mode), so no per-pose K selection
  enters 17.35.
- **The J3 stop.** It acts on the model's q3, the rotation between link 2 and member 3 about u3, which is J3's own angle in the
  model. The concurrent verifier's note reads q3' = q3 + phi(q3) through the knee and is checking that the mapping is monotone.
- **Other items.** O20 hubs are used and the dowel is a catalogue part (ISO 8734 2 m6). K is not idle (span 81.5 deg) and the
  knee moves (qb span 40.8). No bench, judge or metric file changed with the row (P4). Held-out hygiene holds: there is one held
  wear per configuration and no selection on it (P2).

## Proposals (measurement changes, never inputs to this verdict)

- **A. Apply the flood's node rule to clip poses.** One fold-margin reading per claim, so a pose the flood would refuse is never
  scored taken. Measured effect on this row: 17.35 -> 20.68 bench, 22.67 -> 24.56 held. Other rows: only designs with a forced
  K state (the knuckle-4R family) can move. The verified 3R rows read the same margin in every state and should not move; that
  is not measured here.
- **B. Price a stop refusal at a contact pose as that contact.** Proposed catalogue entry **NEW-stop-refusal**: "A stop added
  where the design touches converts contact into a refused pose. The bench drops it from the contact denominator, and its reach
  was already lost, so the gap gains about 100/N_eval per pose while the wearer is jammed instead of grazed. Detect: diff the
  why-counts of the design against its no-stop parent, and re-score the refused poses as contacts." Effect here: 17.35 -> 17.83.
  It is not measured on other rows.
- **C. tools/dash_build.py should also read `frozen_gap`.** The ledger's `claim_of` should also prefer a frozen exact number
  over a fast `gap`. Effect: this row shows 17.35 (score 93.69), not 9.56 (96.52).

## Skeptic (2026-10-18, 07:25-07:37 UTC)

Run by the audit's skeptic. I re-derived the numbers from the raw files and changed nothing: the paired per-pose dumps
(`remeasure/*_conn_perpose`, `*_static_perpose`, the verifier's `*_perpose`, and the lead's `conecut-knee-knuckle-3r_*_perpose`),
the proposer's and verifier's JSONs, the sweep rows, `tools/simplicity.py` on the row's record, `morphs.json` and
`tools/dash_build.py`. I recomputed every gap with my own copy of the bench formula. No new wear was run, and no model,
bench, row or dashboard file was edited. Rulings: `docs/alignment/freek-oracle-route-knuckle-4r.rulings.json`. Ledger entry:
2026-10-18T07:37:23Z, run `skeptic:freek-oracle-route-knuckle-4r`.

**Final verdict (computed by `tools/alignment_ledger.py skeptic`): GAMED.** P1 is upheld. 12 reasons upheld, 1 refuted
(held_out).

Cross-check: the auditor's static dump and the concurrent verifier's `_bench_perpose.json` / `_held_perpose.json` match
pose for pose (0 differences over 470 / 1154 poses). Two independent wears give the same numbers.

| key | ruling | evidence |
|---|---|---|
| held_out (watch) | **refuted** | The measurement is on file. 17.35 frozen exact connected appears three times: the proposer's `cellB_q3max86_bench.json:connected.gap`, the auditor's `_bench.json:frozen.gap` and the verifier's `verify_repro_q3max86_bench.json:connected.gap`. Held 22.67 is in `cellB_q3max86_held.json:connected.gap`. I recomputed 17.35 / 22.66 from the dumps. The drop is +5.32, under TH held_watch 6.0, on every reading (static +5.69, family-consistent +3.88). The rank question belongs to P1. |
| dominance (watch) | upheld | At 2 mm: 45.89 vs 34.84 on the bench (-11.05). It **also holds out**: the lead's held 2 mm is on file (`verify/conecut-knee-knuckle-3r_v_held_frozen.json:audit.gap_near2` 37.1, recomputed 37.11), against this row's 47.88 (-10.77). Taken poses under 2 mm: 43 vs 33 on the bench, 86 vs 71 held. |
| fold_margin (watch) | upheld | Both readings are on file, and they disagree on pass or fail. The model's m3e gives min 5.91 bench / 6.50 held (`_bench.json:fold_margin_th.all.min_margin_th`; `verify_margins_*.json:state1.m3e_min`). The flood's family reading gives min 0.14 bench / 0.01 held on taken poses (`verify_margins_*.json:state2.family_own_min`), and 0.76 / 0.32 on the connected set's taken clip frames. Under TH fold_min one reading is ok and the other is gamed, so this waits on T3. The tool's FOLD_KEY regex reads none of these field names. |
| sampling (watch) | upheld | No `parts_ib14` anywhere for this row: not in the row, the verify directory or the remeasure files. |
| complexity (watch) | upheld | `simplicity.py` gives 32.5. The record's part counts (14 / 16) leave out the J3 dowel and groove; at 15 / 17 the tool gives 33.25, which equals the row. The mismatch does **not** only go against the design: `morphs.json` (983ed3e, 07:31) shows **32.5**, 0.75 under the row's own count. |
| judgement:P1 (gamed) | **upheld** | Everything reproduces: bench 17.35 vs 18.29, held 22.66 vs 22.38, and the same discordant sets. `binder_q3.json` is keyed by claim-bench indices. Rows k61-68 are all Bench(60,160) fast, and 80 / 86 are the only exact cell-B wears. Caveats, none of which refutes: (1) the fit protocol is apples to apples with the lead (both fast-fit), unlike the lowarm precedent; the claim-bench leak is the stop placed from binders and the oracle trigger. (2) The documented held_out threshold reads ok, so "gamed" is a judgement on the rank. (3) **The reversal depends on T3's reading.** Model-consistent (static): held 21.89 beats 22.38 (-0.49, P 0.62, `verify_paired_vs_lead_static.json`), and overhead ties 8/28. Family-consistent: 20.68 / 24.56, behind on both. The claim as filed (connected) leads on the bench by a coin flip and trails held out. The wearer-side cost holds on every reading: 15 vs 4 contacts and 78.55 vs 20.24 mm on the bench; 47 vs 14 and 232.2 vs 60.97 mm held; one more counted joint. |
| judgement:T3 (watch) | upheld | Flood drops 291 / 315 / 317 / 344. Clip frames 12 / 47 / 49 / 52 are all state 2, at 0.76-4.28 deg. The consistent reading recomputes to 20.68 / 24.56, with refused frames left out of the contact denominator as the bench does. The verifier's `state2.wrist_moving_min` 35.99 / 37.56 may be the state-2 wrist, but no code on file defines it. |
| judgement:NEW-stop-refusal (watch) | upheld | 343 / 423 are `ev` false. Read as contacts, the gap is 17.84. **Correction (stronger):** at the kit's own K they were -2.67 / -1.66 mm (`wear3_r0.json:binders`), and every legal K sample is a contact. The audit's -0.19 / -1.33 are the best legal-K values. |
| judgement:T5 (watch) | upheld | Bench: 15 contacts / 78.55 mm / deepest 20.88 / 6 deeper than 3 mm / 8 overhead, vs 4 / 20.24 / 8.93 / 3 / 3 (x3.88). Held: 47 / 232.2 vs 14 / 60.97 (x3.81). The contacts are the same on the static set. |
| judgement:G1 (watch) | upheld | Near-touch at 1 / 2 / 3 mm: 22.19 / 45.89 / 140.21 vs 19.92 / 34.84 / 86.16. Overhead poses taken sit at 1.12-2.14 mm, vs the lead's 1.71-3.03 mm. Held 2 mm: 47.88 vs 37.11. Report only. |
| judgement:M5 (watch) | upheld | The doc says "Not run". No R17, preload, dowel-force or equilibrium output exists in any of this design's files. |
| judgement:G6 (watch) | upheld | Factual: 4 vs 3 DOF, 33.25 (shown as 32.5) vs 18.5, P 0.56 on the bench, reversed held out on the claim's reading. |
| judgement:R4 (watch) | upheld | The current `morphs.json` (after the audit) still shows gap 9.56 / sweep_gap 9.56 with frozen_gap null. `dash_build.py` 444-447 never reads `frozen_gap`, and `frozen_exact` has no top-level gap. |

### Missed by the audit (for the next audit; not in this verdict)

1. **The dashboard understates complexity in the design's favour.** `morphs.json` shows complexity 32.5, while the row says
   33.25. The cause is that the mechanism record's `custom_parts` 14 / `catalogue_parts` 16 were not raised for the J3 dowel
   (ISO 8734 2 m6) and its groove. With 15 / 17, `tools/simplicity.py` gives 33.25. The audit's G6 says "the mismatch goes
   against the design, nothing hidden". That is true of the row, not of the page the user reads.
2. **The fold_margin check cannot see either reading on file.** FOLD_KEY in `tools/alignment_audit.py` matches none of
   these names: the adapter's `fold_margin_th.*.min_margin_th`, the verifier's `m3e_min` and `family_own_min`. So the
   check reports "missing" while two readings are on file. One of them, the family reading at min 0.32 on a taken held clip
   frame, would fire `gamed` under TH fold_min. The T3 split is invisible to the tool. Proposal: read these keys, report
   both readings, and keep the worst until T3 is ruled on.

### Corrections to the audit's numbers (none changes a level)

- **P1 and the overhead count depend on the reading.** "8 vs 5 overhead" and "held +0.29" are connected-set results. Under
  the model-consistent (static) reading, overhead ties 8 / 28 on the bench (15 vs 18 of 71 held), and cell B beats the lead
  held out by 0.49 (P 0.62). Under the family-consistent reading it trails on both benches. The contact count and depth
  readings are the same under every reading.
- **The lead's held 2 mm near-touch was obtainable** (37.1 on file, 37.11 recomputed), so the dominance deficit is
  confirmed held out at -10.77.
- **NEW-stop-refusal.** The poses the stop refuses were pressed at -2.67 / -1.66 mm at the kit's own K, not -0.19 / -1.33.

### What happens next

- The verifier now running (`docs/concepts/verify/freek-oracle-route-knuckle-4r-verify.py`, its q3' own-angle re-pick, and
  `kin_nodes_model` with one fold reading) should rule on T3's reading first. Under the model reading the held rank
  flips to a non-significant lead (P 0.62). Under the family reading the design trails everywhere.
- Either way the contact depth (x3.8-3.9) and the M5 dowel-and-spring hold stay open.
- P1 resolves as the audit says: claim the held number, or record a leader_ruling "not a lead".
