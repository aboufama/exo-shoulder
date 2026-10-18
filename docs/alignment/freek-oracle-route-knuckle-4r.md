# Alignment audit: freek-oracle-route-knuckle-4r, final polish pick1 (fe1-g10-7)

Audit of 2026-10-18 11:02-11:35 UTC, run because the final-polish workflow's independent verifier CONFIRMED pick1
(commit d196fc2; row `polished_*` fields; `docs/research/freek-oracle-route-knuckle-4r_final_polish.md`;
`docs/concepts/verify/freek-oracle-route-knuckle-4r/polish_verify/`). Reference: the 3-joint lead conecut-knee-knuckle-3r.
This replaces the auditor sections of the 08:29 audit (which ruled on the verified config, v_gap 16.20). The two earlier
skeptic sections below the rule are kept as written; they ruled on the verified config, not on this claim.

## Verdict: WATCH (ledger 2026-10-18T11:18:05Z), tool alone: WATCH

- **The claim the ledger records** is polished_gap **15.40** (score 94.40): pick1, fit Bench(60,160) fast -> Bench(110,360)
  exact, frozen, priced, one fold reading. Held out (1154 poses) the same protocol (the CAD shape) gives **20.50**; fitted on
  envh it gives 20.24 (the row's `polished_held_out_gap`).
- **Re-wear.** The claim is new, so the auditor re-wore it on its own path: the model's own `law` mode through
  `tools/alignment_remeasure_freek.py` (unchanged), with the row's recorded `polished_params_priced` laid over the model's own
  params (new adapter `tools/alignment_remeasure_freek_polish.py`; it does not use the polisher's pricing or harness). Bench:
  **15.40 reproduced exactly** (reach 0.7639, follow 1.0, in-band 0.9008, contact 0.0179, the same 7 contact poses), 348 s.
  Held: **20.50 reproduced exactly** on the claim's one reading (static; reach 0.7269, 29 contact poses), 446 s. Through
  the shared harness's own flood (the family reading) it reads 21.15, because that flood drops 6 overhead held poses (P4
  below). The dowel side reading from the same run is 21.54. The bench run of the adapter stopped at its side-reading step
  (a wrong method name, fixed before the held run); the bench side reading comes from `tools/alignment_freek_stop_refusal.py`.
  Outputs: `docs/alignment/remeasure/freek_polish_pick1/`. Local, niced, OMP_NUM_THREADS=1, at most 2 processes.
- **Why WATCH and not GAMED.** No finding has measured proof that the 15.40 ranks the design above one that is better for
  the wearer, and no hard rule is broken. The gain over the verified config is partly a better exo (half the contact depth,
  the overhead clip passage now clean) and partly a tighter dowel that stops the arm where the shape would press metal in
  (NEW-stop-refusal). On the side reading the bench gain is 0 and the CAD-shape held gain is under 1 point.
- **It is not the lead and must not be shown as one.** 4 counted joints, complexity 33.25 vs 18.5. The production
  headline keeps conecut-knee-knuckle-3r (measured with the page's own calcs), but the board table ranks this row #1 and
  shows the verified config's component numbers next to pick1's gap (R4).
- **The tool's 12 checks read the verified config, not this claim** (`tools/alignment_audit.py` audits v_gap 16.20's
  per-pose files). Its contact_depth x3.88 / x3.81, dominance +0.93 / -11.06 and held_out +6.47 are the earlier config's.
  pick1's own numbers are in the findings below (proposal G).

## Is the gain a better exo or a better score? (audit item 1)

Pose by pose against the verified config, Bench(110,360) (per-pose dumps; "stop" = refused by the J3 dowel):

| verified config -> pick1 | bench | held (CAD shape) |
|---|---|---|
| contact -> taken clean | 8 (6 overhead, incl. the 5 overhead clip frames 7-11) | 14 (13 overhead, incl. 8 clip frames) |
| contact -> stopped by the dowel | 0 | 1 |
| contact -> fold / slide refusal | 2 | 11 |
| contact -> contact | 5 | 21 |
| taken -> contact | 2 (431, 454, elev 30) | 4 |
| taken -> stopped by the dowel | 2 (316 at 1.12 mm, 396 at 0.75 mm) | 5 |
| taken -> fold / slide refusal | 7 | 18 |
| refused -> taken | 3 | 13 |
| refused -> contact | 0 | 4 |
| ws reach | 0.7778 -> 0.7639 | 0.7353 -> 0.7269 |
| follow | 0.9545 -> 1.0 | 0.9604 -> 1.0 |

**Both readings, measured on the auditor's own path** (`tools/alignment_freek_stop_refusal.py`;
`docs/alignment/remeasure/freek_polish_pick1/stoprefusal_*.json`):

| | pick1 plain | VER plain | gain | pick1 side (refused kit contacts = contacts) | VER side | gain |
|---|---|---|---|---|---|---|
| Bench(110,360) | 15.40 | 16.21 | 0.81 | 16.39 (4 of 6 refusals are kit contacts, 11.92 mm) | 16.45 (1 of 6, 2.89 mm) | **0.06** |
| held, CAD shape (fit60) | 20.51 | 21.89 | 1.38 | 21.55 (10 of 14, 34.76 mm) | 22.29 (4 of 19, 6.87 mm) | **0.74** |
| held, env fit (verifier) | 20.24 | 22.30 | 2.06 | 21.37 | 22.60 | 1.23 |

The verifier's and polisher's side numbers reproduce to 0.01. On the side reading pick1 still has fewer and shallower
contacts (bench 11 / 51.38 mm vs 16 / 81.44; held 39 / 162.68 vs 51 / 239.07).

**Which way the wearer is better off.** At the 10 held poses where pick1's dowel stops the arm and the shape would
otherwise press metal in (0.37-6.71 mm), the arm is overhead and internally rotated (elev 120-165, axial -75 to -105).
The 3-joint lead refuses all 10; the verified config stopped 6, touched 1 (-0.10 mm) and took 3 with metal at
0.45-1.14 mm. So pick1 blocks the arm where no measured design follows it cleanly. A hard stop is better for the skin than
1-7 mm of metal, and better than 0.5-1 mm on a real, bulging arm. But it is a range limit the wearer feels, and the
force the dowel puts into the cuff when the arm pushes on is unmeasured (M5). The polish trades reach for contact: bench
reach -1.4 points and held -0.8, against half the contact depth and a clean overhead clip passage. For the wearer, the
contact side is the bigger gain. For the score, the side reading says the bench gain is 0 and the held CAD-shape gain is
0.74, under the 1-point polish rule. The user decides that convention (proposal B is not a ruled gate).

## What the wearer gets (measured, pick1, frozen exact, one fold reading)

| | pick1 | verified config | lead conecut-knee-knuckle-3r | file |
|---|---|---|---|---|
| plain gap bench / held (CAD shape) | 15.40 / 20.51 | 16.21 / 21.89 | 18.29 / 22.38 | dumps |
| paired vs lead bench / held (P better) | -2.89 (0.985) / -1.87 (0.967) | -2.08 (0.745) / -0.49 (0.622) | | compare_sets |
| overhead reach taken (elev >= 140), bench / held | 8 / 28, 18 / 71 | 8 / 28, 15 / 71 | 8 / 28, 18 / 71 | dumps |
| raised-arm reach (elev >= 90), bench / held | 53 / 113, 125 / 300 | 52 / 113, 123 / 300 | 47 / 113, 123 / 300 | dumps |
| taken poses with metal < 2 mm, bench / held | 28 / 60 | 28 / 55 | 23 / 57 | dumps |
| near-touch 1 / 2 mm, bench | 17.53 / 45.45 | 21.01 / 46.22 | 19.92 / 34.84 | re-wears |
| near-touch 1 / 2 mm, held | 22.00 / 49.86 | 25.85 / 48.10 | 25.23 / 37.10 | re-wears; `verify/conecut-knee-knuckle-3r_v_held_frozen.json` |
| contact poses / summed depth, bench | 7 / 39.47 mm | 15 / 78.55 | 4 / 20.24 | dumps |
| deepest contact, bench | 12.61 mm at ws plane 15 elev 165 axial -60 | 20.88 mm, same pose | 8.93 mm, same pose | dumps |
| contact poses / summed depth, held | 29 / 127.92 mm (deepest 11.48 at 30 / 165 / -45) | 47 / 232.2 | 14 / 60.97 | dumps |
| overhead contacts bench / held (ws + clip) | 2 / 8 | 8 / 20 | 3 / 7 | dumps |
| overhead taken p10 metal, bench | 1.67 mm | 1.11 mm | 1.79 mm | re-wear |
| workspace in-band14 (taken clip frames) bench / held | 0.9008 / 0.8995 | 0.8977 / 0.8957 | 0.9012 / 0.9 | dumps |
| fold margin th, min over each state's moving chain | 5.59 bench (pose 306, state 1) / 5.58 held | 5.91 / 6.50 | | re-wear; verifier |
| continuity | kinematic flood, one reading (verifier): 0 dropped bench / held; shared-harness family flood (auditor): 0 bench, 6 held (all overhead) -> 21.15; contact-aware flood (verifier): 0 dropped | | | re-wears; verifier |
| counted joints / complexity | 4 (K sensed) / 33.25 | same | 3 / 18.5 | rows |

- **Springs, stops, cuff twist.** pick1 takes 89 bench / 222 held poses with J2 on its stop (the K spring reacted at the
  cuff) and 23 / 43 with J3 on its dowel. The dowel stops the arm on 6 bench / 14 held poses. R17, the dowel force, the K
  preload hold and the cuff twist have not been run for either config.
- **Not obtained.**
  - The unscored-workspace in-band and part-weighted in-band (`tools/alignment_wear_probe.py`): this model has no
    model-level `frozen()`, and the audit adapter reads the bench's own sets only.
  - Per-part sample counts (sampling check): no record exists.
  - pick1's rigid statics (cuff moment per unit spring torque): `tools/alignment_freek_state2_margin.py` builds the
    verified config only, and the box was at load 16-24.

## Findings (ledger reason items)

The tool's own checks (on the verified config, see above): held_out, contact_depth, dominance, fold_margin (FOLD_KEY
reads none of the names on file), sampling, and reporting (it reads v_gap 15.4 on the page against the verifier's 16.2 as
flattering; the polish confirmation is what moved it there) - all watch.

The judgement findings (`docs/alignment/freek-oracle-route-knuckle-4r.findings.json`), all watch:

1. **NEW-stop-refusal (watch).**
   - **Evidence.** The polish moved the J3 dowel from own angle 96.87 to 92.99. It now stops 4 bench / 10 held poses that
     the same shape would press into the arm without it (bench 1 / held 4 before). Side reading: bench gain 0.06, held
     CAD-shape gain 0.74 (table above).
   - **Why the exo is not as much better as the number says.** A refusal costs reach only, a contact costs reach and
     contact, so a tighter stop raises the score at poses the mechanism still cannot follow.
   - **Why only watch.** At those poses the lead also refuses, and the wearer meets a stop instead of 0.4-6.7 mm of metal.
   - **Action.** Quote the polish gain on both readings. The user rules on proposal B. Measure the dowel force (M5) before
     the stop is built.
2. **T5 depth-blind contact (watch).**
   - **Evidence.** Half the verified config's depth, but 1.95x the lead's on the bench (39.47 vs 20.24 mm) and 2.10x held
     (127.92 vs 60.97 mm). The deepest press is 12.61 mm, overhead (ws 15 / 165 / -60), where the lead presses 8.93.
   - **Where the lead over the 3-joint lead comes from.** It is reach (-3.61 bench, -3.47 held), paid with contact (+0.72,
     +1.54). Discordant contacts: 5 vs 2 on the bench, 19 vs 4 held.
   - **Action.** Report depth next to the gap. Do not call it cleaner than the lead.
3. **G1 metal hugging (watch, report only).** At 2 mm the design is 10.61 behind the lead on the bench (45.45 vs 34.84)
   and 12.76 behind held out (49.86 vs 37.10). At 1 mm it is now ahead on the bench (17.53 vs 19.92). Taken poses under 2 mm: 28 vs 23 on the bench, 60 vs
   57 held.
4. **G6 4th joint against 3 (watch).**
   - **The facts.** 4 counted joints, complexity 33.25 vs 18.5. It now beats the lead on the plain gap with significance
     (P 0.985 bench, 0.967 held). That makes it the strongest 4-joint case on file.
   - **Presentation.** The production headline (page calcs re-run) stays with the 3-joint lead. But the board table ranks
     this row #1 at 94.40, and the legacy page's summary calc has no DOF filter.
   - **Action.** Keep the headline 3-joint (user 2026-10-17). A leader_ruling "no lead: 4 joints" citing the skeptic entry
     would also take it out of contention on every page.
5. **R4 reporting (watch).** The board shows v_gap 15.4 with the verified config's v_reach 0.7778 / v_follow 0.9545 /
   v_contact 0.0375, which sum to 16.20; pick1's own are 0.7639 / 1.0 / 0.0179. This shows 1.4 more reach points than
   pick1 has. The board verdict text still describes 16.20, and gap / sweep_gap still read 9.56 (96.52). **Action:**
   proposal E.
6. **NEW-mixed-reading (watch).** The claim 15.40 is the CAD-shape protocol (fit Bench(60,160)), but `polished_held_out_gap`
   is 20.24 from the env-fit protocol. The like-for-like held number is 20.50: the gain over VER is +1.38 (P 0.89, CI
   crosses 0), not +2.06 (P 0.967). **Action:** proposal F.
7. **M5 springs, stops, cuff twist (watch, carried).** The cuff carries spring moment on 112 bench / 265 held taken poses
   (states 1 and 2), and the tighter dowel engages on 23 bench poses and stops the arm on 6 / 14. R17, the dowel force,
   the preload and the cuff twist have not been run.
8. **T4 toward the fold (watch).**
   - **The move.** The minimum th on each state's moving chain went 5.91 -> 5.59 bench and 6.50 -> 5.58 held. That is 0.09
     above the bench's 5.5-deg refusal floor and 0.59 above the user's 5-deg rule.
   - **Reading.** The family reading (a chain that does not move in state 2; settled 08:43) improves: 0.01 / 13 poses ->
     0.70 / 6 held.
   - **Action.** Red-team the feel near the fold edge in R17 (CLAUDE.md: fold margin 5).
9. **P1 in-sample tuning (watch, improved).**
   - **What improved.** The stop is now a search variable on envh, not placed from claim-bench binders. The picks were
     committed before the claims. The bench -> held drop is +5.10 (VER +5.69).
   - **What remains.** The verified-protocol bench gain over VER is +0.81 (P 0.73), and the CAD-shape held gain is
     +1.38 (P 0.89), so neither is significant. envh under-samples |axial| >= 150 (9.5 % vs 11.0 % held), the known
     polish-loss mechanism.
10. **P4 judge reading (watch, carried, now with a held-out effect).**
    - **The reading.** The claim's continuity uses the verifier's design-specific flood reading (`kin_nodes_model`,
      one reading per state's moving chain), which lives only in a verify file.
    - **Through the shared harness.** The auditor's re-wear with the shared flood (`RM.kin_nodes`, the family reading)
      reproduces the static numbers exactly and drops 0 bench poses. Held out it drops 6 poses, all overhead
      (elev 150-165, axial -75 to -45): held 20.50 -> 21.15, and overhead taken 18 -> 12 of 71 (the lead takes 18).
    - **Why watch.** The 08:43 skeptic measured the moving-chain reading to be the right one, so the claim's reading
      stands. But the held overhead count depends on a reading the shared harness does not apply.
    - **Action.** Proposal A of the 08:29 audit (a state-aware shared flood). On the family reading the held gain over the
      verified config is 1.52 (22.67 -> 21.15).


## Checked and clean

- **Search-bench hygiene (P2 / S1).** No envh pose is a held-out pose (verifier's `heldcheck.json`). The one envh pose
  1.66 deg (HG frame) from a held-out pose is held pose 779 (plane 75, elev 45, axial -105). pick1 and VER both take it
  clean on both fit protocols (2.15-2.57 mm vs 2.33-2.37 mm), so it moves the paired gain by 0. Dropping all 27 held poses
  within 3 deg of an envh pose raises the gain: +2.22 env fit, +1.52 CAD shape.
- **Continuity (S5).** On the claim's one reading the kinematic flood drops 0 poses on the bench and held out, and the verifier's contact-aware flood (bench poses not taken removed from the grid) drops 0 as well (8 / 32 nodes blocked). The shared harness's family flood drops 0 on the bench but 6 overhead poses held out (see P4). No static islands are taken on the claim's reading.
- **P3 / R3.** One claim per config. pick1 was rank 1 by the pre-registered search objective (picks committed 6086e09,
  09:43, before the first claim). The polish doc reports all three picks: bench 15.40 / 16.65 / 15.93, held CAD shape
  20.50 / 21.17 / 18.90. pick3, selected on held out, is not claimed.
- **G5 complexity.** `tools/simplicity.py` recomputes 33.25 = row. The polish moved parameters only.
- **M1-M4.** No new part. The dowel (ISO 8734 2 m6) is counted. K moves (dK 0-75.6 deg over taken bench poses).
- **T1 / T2.** Taken poses with metal < 1 mm: 2 bench (VER 8, lead 3). Band read as 3-14 mm: 15.89 (+0.49).

## Proposals (measurement changes, never inputs to this verdict)

- **B (kept, now measured on both configs).** Score a dowel refusal at a pose that is a contact without the dowel as that
  contact. Effect on this row: pick1 15.40 -> 16.39 bench, 20.51 -> 21.55 held (CAD shape); verified config 16.21 -> 16.45,
  21.89 -> 22.29. The polish gain falls from 0.81 / 1.38 to 0.06 / 0.74. No other row on file has a J3 dowel, so none
  should move (not measured).
- **E. Show one config per board row.** When `polished_bench` is flat (no pick key), `tools/dash_build.py` should take
  reach / follow / in-band / contact from it. Effect here: v_reach 0.7778 -> 0.7639, v_follow 0.9545 -> 1.0, v_inband14
  0.8977 -> 0.9008, v_contact 0.0375 -> 0.0179; v_gap unchanged at 15.40.
- **F. Carry the claim's own protocol in `polished_held_out_gap`.** Use the CAD-shape number (fit60: 20.50), with the
  env-fit 20.24 as a side note. Effect: bench -> held drop +5.10, held gain over VER +1.38 (P 0.89).
- **G. Let `tools/alignment_audit.py` audit the claim the ledger keys.** When `claim_of()` returns polished_gap, read the
  polish verifier's per-pose dumps. Effect here: contact_depth x3.88 / x3.81 -> x1.95 / x2.10 (still watch); dominance
  +0.93 / -11.06 -> +2.89 / -10.61; held_out +6.47 -> +5.10 (ok).
- **H. The legacy page's summary calc** (`docs/dashboard/core.js` line 12) should apply the production page's
  `active_dof <= 3` headline filter, or be retired. Today it would put this 4-joint row in the hero at 15.40.
- **Catalogue entry proposed: NEW-polish-component-mix (R5).** "A polished number shown with the base config's component
  fields. Detect: recompute the gap from the row's displayed v_* fields and compare with v_gap."

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
