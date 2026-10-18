# Alignment audit: freek-oracle-route-knuckle-4r (cell B, J3 dowel stop, q3max 86 in the model's q3)

Audit of 2026-10-18 08:20-08:35 UTC, run because round 104 slice r104-B verified the row. Reference: the 3-DOF lead
conecut-knee-knuckle-3r. This replaces the auditor sections of the 07:27 audit. The 07:25-07:37 skeptic section below the
rule is kept as written; it ruled on the 07:27 audit, not on this one.

## Verdict: WATCH (ledger 2026-10-18T08:29:02Z), tool alone: WATCH

- **The claim the ledger records** is v_gap 16.20 (score 94.11): frozen exact Bench(110,360), static set = connected set
  under one fold reading, the model's. The verifier set this number at 07:41. Held out (1154 poses) the same reading gives
  21.89. The row still also carries frozen_gap 17.35 and held_out_gap 22.67, from the claim's own flood (the family reading).
- **Why the verdict moved from GAMED to WATCH.** The 07:27 GAMED rested on one measurement: on the claim-flood reading the
  design trails the lead held out (+0.29, P(better) 0.40). The skeptic upheld that and noted that the reversal depends on
  T3's reading. This audit measured the reading. The family term that drops poses in state 2 is the J1-K-J3 sub-chain
  margin. That chain does not move in state 2: J2 is free in its slot and J3 sits on its dowel, so the moving chain is
  J1-K-J2. In th, that chain's margin is at least 8.12 deg on the bench and 9.97 held, and the minimum over every state's
  moving chain is 5.91 bench / 6.50 held (`docs/alignment/remeasure/freek-oracle-route-knuckle-4r_{bench,held}_state_margins.json`,
  new tool `tools/alignment_freek_state2_margin.py`). On that reading the design leads the lead held out by 0.49 (P 0.62).
  The held-out loss that made it gamed is gone. What is left is a coin flip, not a measured loss, so P1 is **watch**.
- **It is still not a better exo than the lead.** It presses metal into the arm 3.9x deeper in sum, has one more counted
  joint, scores 33.25 on complexity against 18.5, and takes fewer overhead poses held out. The user's rule that the 3-joint
  leaders are the real leaders still applies (G6). None of these is a gate under the user's rulings, so all of them stay
  watch.
- **Re-wear.** Not repeated. The model (last commit 7a1bf07, 06:26) and the config (k33, cell B, q3max 86) have not changed
  since this audit's 07:19 / 07:27 re-wear. The row commits since then (048f21f verifier, 88c35ab part counts) changed no
  geometry. The verifier's independent per-pose dumps match the audit's pose for pose (0 differences over 470 / 1154 poses,
  skeptic). The 16.20 claim is the `frozen_static` of that re-wear (`remeasure/freek-oracle-route-knuckle-4r_bench.json`:
  16.2, recomputed from the static dump: 16.21). The farm is closed (budget line crossed), and the box was at load 14 on
  4 cores.

## What the wearer gets (measured, verified one reading, frozen exact)

| | this design | lead conecut-knee-knuckle-3r | file |
|---|---|---|---|
| plain gap bench / held | 16.20 / 21.89 | 18.28 / 22.38 | verify_onereading_*.json; verify_paired_vs_lead_static.json |
| paired diff bench / held (P better) | -2.08 (0.745) / -0.49 (0.622) | | verify_paired_vs_lead_static.json |
| overhead reach taken (elev >= 140), bench | 8 / 28 | 8 / 28 | remeasure/*_bench_static_perpose.json |
| overhead reach taken, held | 15 / 71 | 18 / 71 | remeasure/*_held_static_perpose.json |
| raised-arm reach (elev >= 90), bench / held | 52 / 113, 123 / 300 | 47 / 113, 123 / 300 | same dumps |
| taken poses with metal < 2 mm (not contact), bench / held | 46 / 91 | 33 / 71 | same dumps |
| near-touch gap 1 / 2 mm, bench | 21.01 / 46.22 | 19.92 / 34.84 | remeasure/*_bench.json deep_static |
| contact poses, summed depth, bench | 15, 78.55 mm | 4, 20.24 mm | alignment json contact_depth |
| deepest contact | 20.88 mm at ws plane 15 elev 165 axial -60 (held 19.91 mm at 30 / 165 / -45) | 8.93 mm, same bench pose | same |
| contact poses, summed depth, held | 47 (12 overhead), 232.2 mm | 14 (7 overhead), 60.97 mm | same |
| workspace in-band14 (taken clip frames, sample-weighted) | 0.8977 bench / 0.8957 held | | row v_inband14; remeasure |
| fold margin in th, min over each state's moving chain | 5.91 bench (state 1, pose 363) / 6.50 held | | *_state_margins.json |
| state-2 moving wrist J1-K-J2, out of plane | >= 35.99 deg bench / 37.56 held | | same |
| counted joints / complexity | 4 (K sensed) / 33.25 | 3 / 18.5 | rows |

- **Springs, stops and cuff twist.** Cell B adds a state in which the K clock spring loads the cuff. On 32 taken bench poses
  (14 of them clip frames; 61 held), J3 sits on its dowel with J1 and J2 free. Per unit spring torque, the cuff then carries
  a moment of 1.89-3.11x (median 1.93) and the dowel 1.13-2.00x (median 1.52). This is a rigid, frictionless statics model,
  `*_state_margins.json` `state2_statics`. At pick1's 0.04-0.08 N.m preload that is 0.08-0.25 N.m on the cuff, and 0.08 N.m
  twisted pick1's cuff 4.64 deg. R17, the dowel's contact force and the spring equilibrium with J2 free have not been run.
- **Not obtained.**
  - The unscored-workspace in-band and part-weighted in-band (`tools/alignment_wear_probe.py`): the probe needs a model-level
    `frozen()`, and this model runs through its `law` path (the audit adapter `tools/alignment_remeasure_freek.py` reads the
    bench's own sets only).
  - Per-part sample counts (the sampling check): no record exists.
  - The cuff twist in degrees: needs R17.

## Findings (17 reason items in the ledger, all watch)

The tool's own checks are all watch, never gamed:
- held_out +6.47: a mixed-reading artefact, see NEW-mixed-reading.
- contact_depth x3.88 / x3.81.
- dominance: at 2 mm (reported only).
- fold_margin: "none on file", because FOLD_KEY cannot read either the verifier's or this audit's names.
- sampling: no per-part record.
- reporting: the page still shows 9.56.

The judgement findings (`docs/alignment/freek-oracle-route-knuckle-4r.findings.json`):

1. **P1 in-sample tuning: watch, lowered from gamed.**
   - **Evidence.** The stop was placed from the claim bench's own binders (`binder_q3.json`, Bench(110,360) exact poses
     316 / 343 / 369 / 423), and the claim-bench oracle triggered the build.
   - **On the verified reading.**
     - The bench lead over the lead is -2.08 (CI90 [-4.99, +2.98]), and held out -0.49 (CI90 [-2.70, +2.13]): 24 % survives.
     - The gain over its own kit is 2.41 bench (18.61 -> 16.20) and 1.48 held (23.37 -> 21.89).
   - **Why not better.** The bench number over-states the held-out gain about four times. **Action:** quote 16.20 only with
     21.89 next to it.
2. **T3 margin on another angle: watch, settled on the measurement.**
   - **The measurement.** The state-2 moving chain is J1-K-J2. Its th margin is >= 8.12 (bench) and 9.97 (held). The
     family term (J1-K-J3, 0.14 / 0.01) belongs to a chain that does not move in state 2. In the statics, J1 and J2 are
     unloaded, so the cuff moment lies along u1 x J2 and depends on det(uK, u1, J2) only. The minimum over all states is
     5.91 / 6.50.
   - **What remains.** The tool cannot read the margin. The shared harness (`minarc-bdp-remeasure.py` kin_nodes) still
     applies the state-1 term in state 2.
3. **P4 judge changed with the design: watch.**
   - **The change.** After the GAMED audit, the verifier swapped the shared flood reading for a design-specific
     `kin_nodes_model`. This moved the row 17.35 / 22.67 -> 16.20 / 21.89 and flipped the held-out rank.
   - **Why watch, not gamed.** It was stated openly, and this audit's re-measure supports it.
   - **Why it is still a finding.** judge_change cannot see it (no harness file was edited), there is no change-log entry,
     and the verifier's wrist script was never committed (it ran from a scratch directory). It is now reproduced from the
     repo.
4. **NEW-mixed-reading: watch.** v_gap 16.20 (one reading) sits next to frozen_gap 17.35 and held_out_gap 22.67 (the family
   reading). The tool's held_out check therefore reads +6.47. The consistent drops are +5.69 (one reading) and +5.32 (claim
   flood). It goes against the design here, but the same mix can flatter another row. **Action:** the row should carry one
   reading for both, plus the other as a side note.
5. **NEW-stop-refusal: watch.**
   - **What happened.** Poses 343 and 423 were kit contacts at -2.67 / -1.66 mm. The dowel now refuses them, and the score
     counts a refusal as lost reach only.
   - **Effect.** Read as contacts, the claim is 16.68, so 0.48 of the 2.08 lead is these two poses. 16.68 still leads.
   - **For the wearer.** A stop is better than metal in the arm, but it is a range limit, not reach.
6. **M5 spring hold: watch.** The state-2 cuff moment is 1.9-3.1x the spring torque, and the dowel takes 1.1-2.0x. R17, the
   preload sweep and the dowel force have not been run.
7. **T5 depth-blind contact: watch.**
   - **Sizes.** Contact depth is x3.88 bench (+58.31 mm) and x3.81 held (+171.23 mm). The deepest press is 20.88 mm, overhead.
   - **Where the lead comes from.** The 2.08 bench lead is reach -5.00 bought with contact +2.69. In discordant contacts,
     13 poses touch only on this design and 2 only on the lead (held 37 vs 4).
8. **G1 metal hugging: watch (reported only).** The design trails the lead by 1.09 at 1 mm and 11.38 at 2 mm. Overhead p10
   metal is 1.08 mm bench and 0.18 mm held.
9. **G6 4th joint against 3: watch.** This is now the best v_gap of any 4-DOF row: pick1 is 19.54 and skinnormal-shortk
   18.58. It must not be read as a new lead: the user ruled that the 3-joint leaders are the real leaders, and it costs +14.75
   complexity.
10. **NEW-stop-angle-label: watch.**
    - **The label.** The headline says "J3 own-angle stop at q3max 86". That is the model's q3, the cuff against link 2,
      which are not adjacent bodies.
    - **The real angle.** The own angle is q3' = q3 + 10.87, so the groove goes at 96.87 (verifier). A groove cut at own
      angle 86 reads 11.22 fast, not 9.56.
    - **Risk.** The physics meets the stop rule, but a CAD built from the label would build the worse design.
11. **R4 reporting: watch, partly fixed.** The page now shows v_gap 16.2 and frozen_gap 17.35, but its `gap` and `sweep_gap`
    still read 9.56 (score 96.52, above the 95 line). 9.56 is the best of 8 fast fit-bench values.

## Proposals (measurement changes, never inputs to this verdict)

- **A (replaces the 07:27 proposal A). Make the shared flood reading state-aware.** In `kin_nodes`, apply each state's
  moving-chain margin:
  - state A: the dyad;
  - J2 on its stop: J1-K-J3 and m3e;
  - J3 on its stop: the J1-K-J2 dyad and m3e.

  Then the claim and the flood read one margin. Measured effect on this row: none against v_gap. It equals the verifier's
  one reading, 16.20 / 21.89, and the state-2 J1-K-J2 margin never binds (>= 8.12). Other rows: only designs with a J3
  stop have a state 2, and none is on file besides this one, so none should move (not measured).
- **B (kept). Re-score a stop refusal at a contact pose as that contact.** Effect here 16.20 -> 16.68. Not measured on
  other rows.
- **C. Let the fold_margin check read a re-measure's `moving_chain_min_th.min`.** Today it reads only the row and the
  verifier files, and FOLD_KEY matches neither the verifier's names nor this file's. Effect here: watch -> ok (5.91).
- **D. One reading per row.** When a verifier re-reads a number, it should also write the held-out number and the frozen
  number under the same reading, so v_gap, frozen_gap and held_out_gap agree. Effect here: held_out_gap 22.67 -> 21.89,
  and the tool's held_out check +6.47 (watch) -> +5.69 (ok, under the 6.0 line).
- **Catalogue entries proposed:**
  - **NEW-mixed-reading** (R5): "a row's verified, frozen and held numbers come from different readings of one rule; detect
    by comparing the reading named in each field's source file".
  - **NEW-stop-angle-label** (M6): "a stop quoted in a model convention other than the joint's own angle; detect by
    checking that the stop value equals the own-angle reading at the engaged poses".

---

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

---

## Skeptic (2026-10-18, 08:36-08:45 UTC, on the 08:29 audit)

Run by the audit's skeptic. The sources were the per-pose dumps (`remeasure/*_static_perpose`, `*_conn_perpose`, the
verifier's `*_perpose`, and the lead's `conecut-knee-knuckle-3r_*_perpose`), recomputed with `tools/alignment_paired.py`
(`gap_parts`, `compare_sets`, 4000 boots). I also re-ran the state-margin measurement from a scratch copy of
`tools/alignment_freek_state2_margin.py`. Models were unchanged. The copy adds a re-solve of J2's own angle through the
model's `free_solve` in state 2, and the state-1 statics. It writes only to the scratchpad and ran 2 s per wear. No model,
bench, row, dashboard file or score was edited. Rulings are in `docs/alignment/freek-oracle-route-knuckle-4r.rulings.json`;
ledger entry 2026-10-18T08:43:54Z, run `skeptic:freek-oracle-route-knuckle-4r`.

**Final verdict (computed by `tools/alignment_ledger.py skeptic`): WATCH.** 3 reasons refuted with measurements
(held_out, fold_margin, T3); 14 upheld. Every reason was at watch, so the verdict is watch.

| key | ruling | evidence |
|---|---|---|
| held_out | **refuted** | The +6.47 pairs the static v_gap with the claim-flood held number. Each reading against itself: static 16.21 -> 21.89 (+5.68; on file at `verify_onereading_{bench,held}.json:gap` 16.2 / 21.89); flood 17.35 -> 22.66 (+5.31). Both are under TH held_watch 6.0. The static dump and the verifier's dump differ in 0 of 470 and 0 of 1154 poses. The rank question is P1's. |
| contact_depth | upheld | Bench: 15 contacts, 78.55 mm, deepest 20.88 mm (pose 237), against the lead's 4, 20.24 mm, 8.93 mm at the same pose: x3.88. Held: 47 contacts, 232.2 mm, against 14, 60.97 mm: x3.81. Both exceed TH depth_ratio 2.0 and depth_floor 5 mm. |
| dominance | upheld | Static reading: +2.08 ahead on the plain gap, -11.38 behind at 2 mm (46.22 vs 34.84). Held at 2 mm: -10.99 (48.10 vs 37.11). The tool read the conn re-wear (+0.93 / -11.06). Either way the design loses at 2 mm. |
| fold_margin | **refuted** | Measured. The model's th margin (m3e, the J1-J3 angle th) has a minimum over all taken poses of 5.91 bench / 6.50 held. The min over each state's moving chain is also 5.91 / 6.50. Both are on file (`*_state_margins.json:moving_chain_min_th.min`; `verify_margins_bench.json:state1.m3e_min`) and are >= TH fold_min 5.0. The only sub-5 term, J1-K-J3 with J2 rigid, occurs only in state 2, where J2 is free and 28.18-83.82 deg (bench) / >= 29.45 deg (held) from its stop. The model itself sets `_msub = 99` there. The watch came from FOLD_KEY not reading these field names. |
| sampling | upheld | No `parts_ib14` / per-part record anywhere for this row. Not measured. |
| reporting | upheld | `morphs.json` (d3aac25, 08:29) shows gap / sweep_gap 9.56 (96.52) with held_out_gap null. Its note still says "Ledger GAMED". |
| judgement:P1 | upheld | Paired bootstrap re-run: bench -2.08 [-4.99, +2.98], P 0.745; held -0.49 [-2.70, +2.13], P 0.622. Kit to cell B: 18.61 -> 16.20 bench, 23.37 -> 21.89 held (`kit_k33_held.json:gap`). The stop was placed from claim-bench binders. |
| judgement:T3 | **refuted** | No moving dyad drops under 5 deg of th. The state-2 moving dyad J1-K-J2 has a th margin >= 8.12 / 9.97 and an out-of-plane angle >= 35.99 / 37.56 deg; the out-of-plane figure reproduces the verifier's `wrist_moving_min`. At all 7 bench / 13 held state-2 poses where the family term is under 5, J2 sits >= 28.18 / 29.45 deg from its stop. Where J2 nears its stop (313 at 1.35 deg, 340 at 1.66, held 116 at 0.97), the family term is 27.87 / 28.88 / 10.77. The residual items are the instrument's and go against the design. |
| judgement:P4 | upheld | The catalogue's P4 case, with the pick1-preload precedent. `kin_nodes_model` lives only in the verify file. judge_change reads only MEASURE_PATHS. `ALIGNMENT.md` section 6 has no entry. The uncommitted-script point is resolved: 35.99 / 37.56 reproduce from the repo tool. |
| judgement:NEW-mixed-reading | upheld | Row: v_gap 16.2 (static), frozen_gap 17.35 (conn), held_out_gap 22.67 (conn). The static held 21.89 is not in a row field. |
| judgement:NEW-stop-refusal | upheld | 343 and 423 have ev false. Read as contacts the gap is 16.68 (17 contacts), so 0.47 of the 2.08 lead comes from them. |
| judgement:M5 | upheld | State-2 statics reproduced: cuff 1.888-3.114 (bench) / 1.887-2.856 (held) x the spring torque; dowel 1.13-2.00 / 1.12-2.24. R17, preload and dowel force have not been run (`verification.not_run`). The scope is wider than reported; see missed item 2. |
| judgement:T5 | upheld | Split bench reach -5.00 / contact +2.69, held -4.31 / +3.39. Discordant contacts 13 vs 2 (held 37 vs 4). |
| judgement:G1 | upheld | 1 mm: 21.02 vs 19.92. 2 mm: 46.22 vs 34.84 (held 48.10 vs 37.11). Under 2 mm: 46 vs 33 (held 91 vs 71). Overhead taken p10: 1.11 / 0.25 mm vs the lead's 1.79 / 1.20 (the audit had 1.08 / 0.18; same direction). |
| judgement:G6 | upheld | 4 DOF / 33.25 vs 3 / 18.5. The dashboard complexity is now 33.25. Overhead held 15 vs 18 of 71. |
| judgement:NEW-stop-angle-label | upheld | The row summary and doc line 34 still read "own-angle ... q3max 86". Only `verification.j3_stop_reading` and doc line 272 give 96.87. At own angle 86 the gap is 11.22 fast (`verify_q3own_stop_fit60.json`). |
| judgement:R4 | upheld | Same evidence as reporting: the headline gap is still the best of 8 fast fit-bench runs. |

### Missed by the audit (for the next audit; not in this verdict)

1. **The 5 lost bench clip frames are one overhead contact run, and the follow term does not price them.**
   - **Bench.** Frames 7-11 (elev 148-150) are all in contact at -0.86 to -1.76 mm; the lead loses no clip frame.
     Follow is 0.9545 = 105/110, 0.5 frame above the 0.95 cutoff, so the follow term charges 0. On the recorded overhead
     motion, metal presses into the arm over a continuous stretch the score counts only as 5 contact shares.
   - **Held.** Frames 13-20 (8 of 202) are the same overhead passage, all in contact; the lead loses 0.
   - **Pattern.** This is the T-pattern "just past a cutoff" on the follow term. A next design that loses one more
     frame pays 0.45.
2. **M5's spring-to-cuff load is not only state 2.**
   - **State 1.** In state 1 (the kit's stretched state: J2 on its stop, J1 / J3 free), the K spring torque is also
     reacted at the cuff. The cuff moment w = lam (u1 x J3) is 1.887 / 2.137 / 2.631 x the spring torque over 70 taken
     bench poses, and 1.887 / 2.068 / 2.647 x over 173 held (rigid statics, same method).
   - **Scope.** The cuff carries spring moment on 102 / 385 bench and 234 / 894 held taken poses, not 32 / 61. State 1
     is the knuckle-4r family's (pick1, skinnormal-shortk), so the same applies to those rows' M5.
3. **Overhead contact counts are mixed in the audit's text.** Bench "8 overhead" counts ws + clip (3 + 5), but held
   "12 overhead" counts ws only.
   - **Consistent held count.** 20 (12 ws + 8 clip) vs the lead's 7 (7 + 0).
   - **The clip part.** Every overhead clip-frame contact, 5 bench and 8 held, belongs to this design only.
4. **J2 comes within 1 deg of its stretched stop in state 2.**
   - **Where.** Bench 313 at 1.35 deg and 340 at 1.66; held 116 at 0.97.
   - **What it is.** A double-stop corner (J3 on its dowel, J2 nearly on its stop) where the state choice rests on friction.
   - **Status.** Not a margin problem: the family term there is >= 10.77. It is a point for the R17 / equilibrium scan.
5. **The dashboard note is stale in the design's disfavour.** It still says "Ledger GAMED (P1)" (ledger: WATCH).
   Separately, the previous skeptic's missed item (complexity 32.5 on the page) is now fixed: 33.25.

### What happens next

- **fold_margin.** Proposal C closes the instrument gap: read `moving_chain_min_th.min` and the verifier's `m3e_min`.
- **Row readings.** Proposal D fixes NEW-mixed-reading and the held_out artefact.
- **What stays open.** The contact depth (x3.8-3.9), the overhead clip contact run (missed item 1), the spring-to-cuff
  load on 102 / 234 poses with no R17, and the 4-vs-3 DOF ruling. The row stays "screened", not a leader.
