# Alignment audit: freek-oracle-route-knuckle-4r, final polish pick1 (fe1-g10-7), hourly re-audit

Audit of 2026-10-18 20:55-21:30 UTC. It ran because files were committed after the last audit (11:24:30Z):

- **be4c46e (11:33)** edited the row and the board after the 11:18 audit's R4 / E / F / H proposals.
- **b31b802 (12:17)** was a running agents' WIP commit. It added six `reverify_*` files from a re-dispatched verifier to
  `docs/concepts/verify/freek-oracle-route-knuckle-4r/`.

Reference: the 3-joint lead conecut-knee-knuckle-3r. This replaces the auditor sections of the 11:18 audit. The three
skeptic sections below the rule are kept as written.

## Verdict: WATCH (ledger 2026-10-18T21:05:09Z), tool alone: WATCH

- **The claim the ledger records** is polished_gap **15.40** (score 94.40). pick1 is fit on Bench(60,160) fast, then worn
  on Bench(110,360) exact, frozen, priced, on one fold reading. Held out (1154 poses) on the same protocol (the CAD shape)
  it gives **20.50**. The verified config (v_gap 16.20, held 21.89) stays on the row unchanged.
- **Did the WIP commit move the polished fields? No.**
  - b31b802 did not touch the row (`git show --name-status b31b802`). It added only `reverify_*` files.
  - be4c46e (11:33) changed two things in the row. First, `polished_bench.contact` went from `[7, 39.47]` (count, mm) to
    the fraction 0.0179, and pick1's own reach / follow / in-band (0.7639 / 1.0 / 0.9008) were added. Second, it added
    `polished_held_out_gap_fit60` 20.5 and a note.
  - Those components recompute to 15.40 (13.61 reach + 1.79 contact). They equal the auditor's own 11:18 re-wear.
  - polished_gap 15.4, polished_held_out_gap 20.24, polished_params_priced and v_gap 16.2 are byte-identical to d196fc2.
- **Re-wear, run again because the row's last commit (11:33) is newer than the re-wear files.**
  - The model, its imports, the harness and the benches have not changed since 06:27 (`git log -1` on each).
  - Bench (`tools/alignment_remeasure_freek_polish.py bench`, 149 s): **15.40 reproduced**. All 470 per-pose records are
    identical to the 11:18 re-wear and to the polish verifier's dump. The side reading is again 16.39.
  - Held (`... held`, 292 s): **20.50 reproduced** on the claim's one reading. All 1154 per-pose records are identical to
    the 11:18 re-wear. The shared family flood again reads 21.15 (6 overhead poses dropped), and the side reading is
    21.54.
  - Local only: niced, OMP_NUM_THREADS=1, at most 2 processes. The farm budget is spent.
- **Why WATCH and not GAMED.**
  - No finding has measured proof that 15.40 ranks the design above one that is better for the wearer. No hard rule is
    broken.
  - Nothing has moved since the 11:24 skeptic, apart from presentation fixes. The new evidence in this audit is either
    clean (the dowel reachability check) or about the instrument (the masked T5 check).
- **It is not the lead.**
  - It has 4 counted joints and complexity 33.25, against the lead's 3 and 18.5. The headline stays with the 3-joint lead
    by the user's 2026-10-17 ruling.
  - The board's verified ranking now has offset-shortcar-relay-4r (14.76, also 4 joints) first and this row second.

## What the wearer gets (measured, pick1, frozen exact, one fold reading)

| | pick1 | verified config | lead conecut-knee-knuckle-3r | file |
|---|---|---|---|---|
| plain gap bench / held (CAD shape) | 15.40 / 20.51 | 16.21 / 21.89 | 18.29 / 22.38 | dumps |
| overhead reach taken (elev >= 140), bench / held | 8 / 28, 18 / 71 | 8 / 28, 15 / 71 | 8 / 28, 18 / 71 | re-wear `overhead140`; dumps |
| raised-arm reach (elev >= 90), bench / held (static) | 53 / 113, 125 / 300 | 52 / 113, 123 / 300 | 47 / 113, 123 / 300 | re-wear `raised90`; dumps |
| taken poses with metal < 2 mm (tool's metal: min of min_mm and crown / wall cmin), bench / held | 48 / 102 | 43 / 86 | 33 / 71 | re-wear `deep.near2_poses`; skeptic 11:24 |
| near-touch 1 / 2 / 3 mm, bench | 17.53 / 45.45 / 155.15 | 22.19 / 45.89 / 140.21 | 19.92 / 34.84 / 86.16 | re-wear `deep` |
| contact poses / summed depth, bench | 7 / 39.47 mm | 15 / 78.55 | 4 / 20.24 | static dumps |
| deepest contact, bench | 12.61 mm at ws 237 (plane 15, elev 165, axial -60: overhead) | 20.88 mm, same pose | 8.93 mm, same pose | static dumps |
| contact poses / summed depth, held | 29 / 127.92 mm (deepest 11.48 at 30 / 165 / -45) | 47 / 232.2 | 14 / 60.97 | dumps |
| overhead taken p10 metal, bench | 1.67 mm | 1.11 mm | 1.79 mm | re-wear |
| workspace in-band14 (taken clip frames), bench / held | 0.9008 / 0.8995 | 0.8977 / 0.8957 | 0.9012 / 0.9 | dumps |
| fold margin th, min over each state's moving chain | 5.586 bench (ws 306, state 1) / 5.58 held; 0 under 5.5 | 5.91 / 6.50 | | re-wear `fold_margin_th` |
| continuity (one reading) | bench flood 1093 nodes, 0 islands, 0 dropped; held 0 dropped; family flood held drops 6 overhead | 0 / 0 | | re-wear `flood` |
| J3 dowel reached by a continuous K motion | bench 31 engaged, 6 refused, 0 skipped bands, 0 q3 reversals; held 66 / 14 / 0 / 0 | bench 47 / 6 / 0 / 0, held 100 / 19 / 0 / 0 | n/a | `freek_polish_pick1/skipcheck_pick1_*.json`; `verify/.../reverify_skip_*.json` |
| counted joints / complexity | 4 (K sensed) / 33.25 | same | 3 / 18.5 | rows |

- **Springs, stops, cuff twist.**
  - Spring: pick1 takes 89 bench / 222 held poses with J2 on its stop, where the K spring is reacted at the cuff.
  - Dowel: it takes 23 / 43 poses with J3 on its dowel, and the dowel stops the arm on 6 / 14.
  - Statics: the rigid state-2 cuff moment is 2.04-3.17 times the spring torque (skeptic 11:24). These are ratios, not
    forces.
  - Not run for either config: R17, the dowel force, the K preload hold and the cuff twist.
- **Not obtained.**
  - The unscored-workspace in-band and the per-part in-band. Neither `tools/alignment_wear_probe.py` nor
    `tools/sample_density.py measure` supports this model: it has no model-level `frozen()`, and the second fails with an
    AttributeError on `frozen`, measured this audit. A scratch probe of the frozen KModel found no rigid / link_pts part
    arrays under the kit's names, so no per-part counts exist.
  - Held-out depth of the lead on the env-fit protocol: not needed, because the CAD-shape protocol is like-for-like.

## Findings (ledger reason items)

The tool's own checks (they read the VERIFIED config, v_gap 16.20, not the keyed claim; proposal G):

- **held_out (watch).** +6.47 mixes two readings. Skeptics refuted it at 07:37, 08:43 and 11:24. On the claim's own
  reading it is +5.11.
- **dominance (watch).** +0.93 plain, -11.06 at 2 mm, run with `--ref conecut-knee-knuckle-3r` as at 11:18. With no
  `--ref` the tool prints "no reference" and ok.
- **fold_margin (watch).** FOLD_KEY does not read `one_min` (proposal C). The measured 5.586 passes.
- **sampling (watch).** No per-part record exists.
- **reporting (watch).** The tool reads v_gap 15.4 against the verifier's 16.2. That is the confirmed polish, not
  flattery. The sweep 9.56 is the self-measured fast number.
- **contact_depth (reads ok, wrongly; see finding 1).**

The judgement findings (`docs/alignment/freek-oracle-route-knuckle-4r.findings.json`) are all watch:

1. **NEW-instrument-masked-T5 (watch, new).**
   - **Evidence.** The tool's T5 check now prints "no bench depth of conecut-knee-knuckle-3r on file" and ok.
     - The cause is `docs/alignment/remeasure/desmo-geom-knuckle-3r_vs_conecut-knee-knuckle-3r_paired.json` (46af77e,
       11:37), which holds `"held": "missing dump"`, a string.
     - `_depth_sources()` calls `.get()` on it and raises AttributeError, and `ref_depths()` swallows the error as "not
       on file". The lead's depths are on file.
   - **Measured with that one file skipped** (scratch probe, tool unchanged): the check reads WATCH again.
     - Verified config: x3.88 bench, x3.81 held.
     - The keyed claim pick1: x1.95 bench, x2.10 held.
   - **It is not only this row.** Seven audit files written since 15:00, this one included, carry the masked "ok".
     - Two 4-joint rows flip to watch: offset-shortcar-relay-4r, the board's first verified row at 14.76 (13 contacts,
       46.18 mm, x2.28 bench), and phi40-thinstack-relay-4r (17 contacts, 74.92 mm, x3.70 bench).
     - The four 3-joint rows hit stay ok either way: conecut-h2facet x0.98 / x0.99, conecut-l2jog x1.0 / x0.95,
       lowarm-kphase-notch x0.77 / x0.66, lowarm-kstop x0.82 / x0.74.
   - **Why the exo is not better than it looks.** A design that presses 2-4 times deeper than the lead shows a clean T5
     line.
   - **Action.** Proposal I. Re-audit offset-shortcar-relay-4r and phi40-thinstack-relay-4r after the fix.
2. **T5 depth-blind contact (watch).**
   - **Evidence.** pick1 presses 39.47 mm over 7 bench contacts against the lead's 20.24 over 4 (x1.95). Held out it is
     127.92 mm over 29 against 60.97 over 14 (x2.10, over both thresholds).
   - **The deepest press** is overhead: 12.61 mm, where the lead presses 8.93.
   - **Where the lead over the 3-joint lead comes from.** It is reach (-3.61 bench / -3.47 held), paid with contact
     (+0.72 / +1.54).
   - **Action.** Report depth next to the gap. Do not call it cleaner than the lead.
3. **NEW-stop-refusal (watch).**
   - **The gain on the side reading.** On the stop-refusal reading (proposal B) the polish gain is 0.06 on the bench,
     re-measured this audit, and 0.74 held (CAD shape). That is under the 1-point polish rule.
   - **New: the side reading depends on the shape.** The re-dispatched verifier read "without the dowel" as the k33 kit's
     own fit (`reverify_side_bench.json`). For the verified config that gives 16.68: it counts 423 as a contact
     (-1.66 mm), where the same-shape reading refuses 423 on fold / slide. The same-shape reading gives 16.45. Proposal
     B's number depends by 0.23 on that choice.
   - **New and clean: no static island hides behind the stop.** The dowel is reached by a continuous K self-motion at
     every engaged pose. pick1 shows 0 skipped infeasible bands and 0 q3 reversals over 31 bench / 66 held engagements
     (`tools/alignment_freek_skipcheck_pick1.py`, new). The verified config shows the same over 47 / 100 (the
     reverifier).
   - **Why only watch.** The lead also refuses these poses, and a stop is better for the skin than 0.4-6.7 mm of metal.
   - **Action.** The user rules on proposal B and its shape. Measure the dowel force.
4. **G1 metal hugging (watch, report only).**
   - **At 2 mm** it is 10.61 behind the lead on the bench and 12.76 behind held out.
   - **Taken poses under 2 mm:** 48 vs 33 on the bench, 102 vs 71 held.
   - **The polished overhead clip passage** is taken at 1.70-1.80 mm, where the lead sits at 1.84-2.12.
5. **G6 4th joint against 3 (watch).**
   - **The facts.** 4 counted joints, complexity 33.25 vs 18.5.
   - **On the board.** Since be4c46e it is labelled "(4 joints)" and kept out of the leader KPI. offset-shortcar-relay-4r
     (4 joints) now ranks above it. leader_ruling is still empty.
   - **Action.** Keep the headline 3-joint.
6. **R4 reporting (watch, mostly resolved).**
   - **Fixed.** The board's components are now pick1's and recompute to 15.40 (proposal E done).
   - **Left: the sweep number.** gap / sweep_gap still show the fast 9.56.
   - **Left: frozen_gap.** The top-level `frozen_gap` 17.35 belongs to the verified config's mixed-reading flood, not to
     pick1. The page does not show `frozen_gap` for a verified row.
7. **NEW-mixed-reading (watch, reduced).** `polished_held_out_gap_fit60` 20.5 is now on the row and in the verdict text.
   But `polished_held_out_gap`, the field tools read, still holds the env-fit 20.24 (proposal F).
8. **M5 springs, stops, cuff twist (watch, carried).** R17, the dowel force, the preload and the cuff twist have not been
   run. The cuff carries spring moment on 112 bench / 265 held taken poses.
9. **T4 toward the fold (watch, carried).**
   - **The margin.** Min th is 5.586 bench / 5.58 held, 0.09 above the 5.5 refusal floor.
   - **The cap.** The CMA's a1max was clipped to the K-dyad cap (76.09 -> 72.67 -> priced 70.71). The K-dyad margin
     stays >= 7.56.
10. **P1 in-sample tuning (watch, carried).**
    - **The gain is not significant.** Over the verified config: +0.81 bench (P 0.73), +1.38 held CAD shape (P 0.89).
    - **The search bench.** envh under-samples |axial| >= 150 (9.5 % vs 11.0 % held).
11. **P4 judge reading (watch, carried).**
    - **The reading.** The one-reading flood lives only in verify scripts.
    - **Through the shared family flood** the held number is 21.15, and overhead taken falls to 12 / 71 (vs 18 / 71).

## Checked and clean

- **P4 / R2: the WIP commit and the reverifier.**
  - b31b802 changed no row field, no model and no harness file.
  - The re-dispatched verifier's `reverify_rerun_q3max86_bench.json` reproduces the verified config exactly: 16.20 static,
    17.35 on the claim's mixed-reading flood, 280 ws taken, 15 contacts.
  - Its result is not written to the row, so nothing on the page rests on it.
- **Search-bench hygiene (P2 / S1).** Unchanged since 11:18. No envh pose is a held-out pose. One pose is 1.66 deg away
  in the HG frame, and it moves the paired gain by 0.
- **Continuity (S5).** On the claim's reading 0 poses are dropped, on the bench and held out.
  - The dowel reachability check rules out a static island behind the stop (finding 3).
  - The tool's continuity line now cites `reverify_rerun_q3max86_bench.json`, a file whose flood says dropped 4
    (17.35). The tool reads only `islands` there, because its drop regex has no plain `dropped` key (proposal J). The
    "0 dropped" the tool prints is true of the claim's one reading but not of the file it cites.
- **P3 / R3.** One claim per config. The picks were committed before the claims. All three picks are reported.
- **G5 complexity.** `tools/simplicity.py` gives 33.25, equal to the row.
- **M1-M4.** No new part, and K moves (dK span 81.49 deg).
- **T1 / T2.** 4 taken poses under 1 mm on the bench (VER 9). Band read as 3-14 mm: 15.89 (+0.49).

## Proposals (measurement changes, never inputs to this verdict)

- **I (new). T5 must not read an exception as "not on file".**
  - **The fix.** In `tools/alignment_audit.py` `_depth_sources()`, skip a paired record whose wear entry is not a dict
    (`isinstance(d.get(w), dict)`). Have `ref_depths()` report an error instead of returning `{}`. Bump VERSION.
  - **Measured effect** (scratch probe, malformed file skipped):

    | row | T5 now | T5 after the fix | depth vs lead |
    |---|---|---|---|
    | freek-oracle-route-knuckle-4r | ok | watch | x3.88 / x3.81 verified config |
    | offset-shortcar-relay-4r | ok | watch | x2.28 bench |
    | phi40-thinstack-relay-4r | ok | watch | x3.70 bench |
    | conecut-h2facet, conecut-l2jog, lowarm-kphase-notch, lowarm-kstop | ok | ok | unchanged |

  - **Ledger verdicts.** Nothing else moves: all three flipped rows are already WATCH.
- **J (new). The continuity check should read a plain `dropped` key** and prefer a flood file whose static gap and
  reading are the claim's.
  - Read naively, this row's cited file (dropped 4, 17.35) would turn the check to watch (+1.15 > conn_watch 1.0).
  - The 08:43 skeptic ruled that the mixed reading is the wrong one. So J only helps together with the "claim's reading"
    rule.
- **B (kept).** Score a dowel refusal as the contact it replaces.
  - **Effect here:** the polish gain falls to 0.06 bench / 0.74 held.
  - **New sub-question for the user:** "without the dowel" can be read as the same frozen shape (16.45 for the verified
    config) or as the kit's own fit (16.68). The same frozen shape is the like-for-like reading.
- **F (kept).** Put the CAD-shape held number 20.50 into `polished_held_out_gap`. Effect: held gain +1.38 (P 0.89).
- **G (kept).** Have the tool audit the claim the ledger keys.
  - Effect on contact_depth: x3.88 / x3.81 -> x1.95 / x2.10.
  - Effect on dominance: +0.93 / -11.06 -> +2.89 / -10.61.
  - Effect on held_out: +6.47 -> +5.11 (ok).
- **C (kept).** FOLD_KEY should read `one_min` and `moving_chain_min_th.min`. Effect: fold_margin watch -> ok at 5.586.
- **Catalogue entry proposed: NEW-instrument-masked-check (R5).** "A check that reads an exception or a malformed input
  as 'not on file' and returns ok. Detect: the selftest mutates one reference file to a string and expects an error or
  the unchanged level, never ok."

## What happens next

- Nothing on this row needs the lead before the user's rulings on proposal B and the 4-joint question.
- The open physical checks before any CAD are R17 with the state-2 spring hold, the dowel force and the cuff twist.
- The hourly audit loop should re-audit offset-shortcar-relay-4r and phi40-thinstack-relay-4r once proposal I lands.
  Both had T5 masked.

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

---

## Skeptic (2026-10-18, 11:19-11:26 UTC, on the 11:18 audit of the polish claim 15.40)

Run by the audit's skeptic. I re-derived the numbers from the rawest files and changed nothing. The sources:

- the polish verifier's per-pose dumps (`polish_verify/pick1_fit60_{bench,held}_perpose.json`, `pick1_envh_held_perpose.json`);
- the auditor's re-wear dumps (`remeasure/freek_polish_pick1/*_{static,conn}_perpose.json`);
- the verified config's and the lead's dumps;
- recomputed with `tools/alignment_paired.py` (`gap_parts`, `compare_sets`, 4000 boots).

I re-ran the state-margin measurement from a scratch copy of `tools/alignment_freek_state2_margin.py`. The copy lays the row's
`polished_params_priced` over the model params and reads the auditor's pick1 static dumps. It wrote to the scratchpad only,
ran locally, niced, OMP_NUM_THREADS=1, 1 process, at $0.

The auditor's static dumps and the polish verifier's dumps match: 0 of 470 bench poses and 0 of 1154 held poses differ.
No model, bench, row, dashboard file or score was edited. Rulings: `docs/alignment/freek-oracle-route-knuckle-4r.rulings.json`;
ledger entry 2026-10-18T11:24:30Z, run `skeptic:freek-oracle-route-knuckle-4r`.

**Final verdict (computed by `tools/alignment_ledger.py skeptic`): WATCH.** I refuted 2 reasons with measurements (held_out,
fold_margin) and upheld 14. Every reason was at watch, so the verdict is watch.

| key | ruling | evidence |
|---|---|---|
| held_out | **refuted** | The +6.47 pairs the verified config's static v_gap 16.2 with its claim-flood held 22.67, two different readings (the same artefact was refuted at 07:37 and 08:43). On the claim's own readings: fit60 15.40 -> 20.51 (+5.11; row `polished_held_out_fit60.gap` 20.5); shared family flood 15.40 -> 21.16 (+5.76); env fit 20.24 (+4.84). The verified config on one reading: 16.21 -> 21.89 (+5.68). All are under TH held_watch 6.0. |
| contact_depth | upheld | On the claim, the bench ratio is x1.95 (39.47 vs 20.24 mm), under 2.0. Held out, the CAD shape is x2.10 (127.92 vs 60.97 mm, +66.95 mm) on the same fit protocol as the lead's held dump, so it is over both TH depth_ratio 2.0 and depth_floor 5 mm. The env fit is x2.21. |
| dominance | upheld | Plain gap: -2.89 (P 0.985). At 2 mm: 45.45 vs 34.84 bench, 49.86 vs 37.10 held. Taken poses under 2 mm on the tool's metal: 48 vs 33 bench, 102 vs 71 held. |
| fold_margin | **refuted** | On file: `polished_bench.th.one_min` 5.59, `polished_held_out_fit60.th.one_min` 5.58 and `polished_th_margin.held_envfit.one_min` 5.58, with one_lt5 0. Re-measured: `moving_chain_min_th.min` 5.59 bench / 5.58 held, >= TH fold_min 5.0. The family term is under 5 only on 6 held state-2 poses (min 0.70). There the moving dyad J1-K-J2 has th >= 10.36 and out-of-plane >= 39.62 deg, the reading settled at 08:43. The watch came from FOLD_KEY, which does not read `one_min`. |
| sampling | upheld | No per-part record exists for this row in the row file, the verify or remeasure directories, or `research/freek_env_polish`. |
| reporting | upheld | `morphs.json` (78385c0) still shows gap / sweep_gap 9.56 (score 96.52), and its verdict text still describes 16.20. The v_gap 15.4 on its own is the confirmed polish. |
| NEW-stop-refusal | upheld | `stoprefusal_*.json` reproduce: bench side 16.39 vs 16.45 (gain 0.06), held CAD shape side 21.55 vs 22.29 (gain 0.74). Kit contacts the dowel refuses: 4 / 11.92 mm on the bench, 10 / 34.76 mm held. No dowel force is on file. |
| T5 | upheld | Bench: 7 contacts / 39.47 mm, deepest 12.61 mm at pose 237, against the lead's 4 / 20.24 / 8.93 at the same pose. Held: 29 / 127.92 against 14 / 60.97. Split: reach -3.61 / -3.47, contact +0.72 / +1.54. Discordant contacts 5 vs 2 and 19 vs 4. Correction: the lead's held deepest (9.86) is at pose 683, not at pick1's pose 610. |
| G1 | upheld | 1 mm: 17.53 vs 19.92. 2 mm: 45.45 vs 34.84, held 49.86 vs 37.10. Report only. Count correction below (missed 1). |
| G6 | upheld | `morphs.json`: active_dof 4, complexity 33.25, first of the verified rows by v_gap (15.4 vs 18.28). P 0.985 / 0.967 re-run. |
| R4 | upheld | The board's v_* fields (0.7778 / 0.9545 / 0.8977 / 0.0375) recompute to 16.20. pick1's own are 0.7639 / 1.0 / 0.9008 / 0.0179. `dash_build.py` lines 416-422 look for a pick-keyed `polished_bench`, and this one is flat. |
| NEW-mixed-reading | upheld | `polished_gap` 15.4 is the fit-Bench(60,160) protocol; `polished_held_out_gap` 20.24 is "fit envh". The like-for-like held number is 20.51, paired -1.38 (P 0.892, CI90 [-3.71, 0.43]). |
| M5 | upheld | No R17, dowel force, preload or cuff twist is on file. Newly measured state-2 rigid statics for pick1 (the audit had these as not obtained): cuff 2.04 / 2.20 / 3.17 x the spring torque over 23 taken bench poses, 2.04 / 2.10 / 2.96 over 43 held; dowel 1.19-2.03 x. These are ratios, not forces. |
| T4 | upheld | Min th 5.59 / 5.58 re-measured. It also carries the T4 sign the audit did not cite (missed 3). |
| P1 | upheld | Bench vs VER -0.81 (P 0.727, CI90 [-5.54, 1.84]); held CAD shape -1.38 (P 0.892). Neither is significant. |
| P4 | upheld | `kin_nodes_model` exists only in the design's verify and polish-verify scripts and the polisher's `tools/freek_env_polish.py`, and none of them is in MEASURE_PATHS. On the shared flood, held reads 21.16 and overhead 12 / 71 (vs 18 / 71). |

### Missed by the audit (for the next audit; not in this verdict)

1. **The 2 mm shell counts understate the gap to the lead.**
   - The audit's "taken poses with metal < 2 mm 28 vs 23 bench, 60 vs 57 held" reads `min_mm` only.
   - The tool's own near-touch metal is min(min_mm, cmin), with the model's crowns and walls; it gives the
     `deep_static.near2_poses` 48 / 102. On that metal the counts are 48 vs 33 bench and 102 vs 71 held.
   - The difference is in the clip frames: 15 vs 5 bench and 32 vs 8 held.
2. **The "now clean" overhead clip passage sits in the 1-2 mm shell.**
   - Bench clip frames 6-12 (elev 138-150) are at 1.70-1.80 mm; held frames 12-21 (elev 146-150) at 1.70-1.72 mm.
   - The lead sits at 1.84-2.12 mm on the same frames.
   - The polish turned these frames from contact (-0.86 to -1.76 mm) into takes at 1.7 mm. Follow goes 0.9545 -> 1.0, but the
     metal is still on a real, bulging arm (ALIGNMENT.md section 1), about 0.14 mm closer than the lead.
3. **T4 sign: the search pushed K stop B into its own singularity cap.**
   - The CMA proposed a1max 76.09. `full()` clipped it to bk1 + bk2 - 5.51 = 72.67 (`picks/pick1.json` a1max 72.6719 =
     29.3309 + 48.851 - 5.51), and pricing took it to 70.71. VER sat 2.45 below its cap.
   - The polish doc's table (line 121) discloses this; the audit's T4 does not cite it.
   - The measured K-dyad margin stays >= 7.56 on taken poses.
4. **pick1's state-2 statics are now on file in this section** (M5 above). The cuff max (3.17) is slightly above VER's 3.11.
   Taken poses by state: 273 / 89 / 23 on the bench and 629 / 222 / 43 held.

### What happens next

- **fold_margin.** Proposal C (read `one_min` and `moving_chain_min_th.min` in FOLD_KEY) closes the instrument gap.
- **held_out.** Proposal G (audit the keyed claim's own dumps) removes the +6.47 artefact.
- **What stays open.**
  - Held contact depth x2.10 against the lead.
  - The dowel side reading (proposal B: 0.06 bench / 0.74 held).
  - The R17 / dowel force / cuff twist.
  - The 4-vs-3 DOF presentation on the board (R4, G6, proposal E / H).
- The row stays "not the lead".
