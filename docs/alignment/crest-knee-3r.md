# Alignment audit: crest-knee-3r (joggled cuff knee, round 14 slice r14-A)

Auditor pass 2026-10-19 ~01:35-02:10 UTC, tool VERSION 2026-10-18.1, git 0e9df59. Why it was due: the row and its
verifier files were committed at 2026-10-18T12:06:18Z (73ac7c5, the round-3 skeptic's re-run of the FLAT cell), after
the last audit (09:14). That commit records v_gap 32.84 for the flat cell and keeps v_* at the verified joggle 31.50.

**The claim did not move.** The row still carries v_gap 31.50 (`v_params_key` best_params_joggle, kj=1). Its parameters
are identical to the 09:02 re-wear (`remeasure/crest-knee-3r_bench.json`). The model and both verifiers last changed at
08:57, before that re-wear. So the full frozen re-wear was not repeated: it would give the same numbers, 31.50 bench
and 28.45 held. Instead, this pass ran the round-3 skeptic's new checks on the joggle cell, which the 12:06 re-run had
applied to the flat cell only (see "New this pass").

## Verdict: WATCH (claim v_gap 31.50, score 88.55)

The ledger verdict is WATCH. There is no gamed reason (`python3 tools/alignment_ledger.py get crest-knee-3r`).

- **Checks:** 2 watch, from `docs/alignment/crest-knee-3r.json`.
  - continuity: a reading gap in the tool. The flood is on file, and the skeptic refuted this reason twice.
  - reporting.
- **Judgement findings:** 4 watch (NEW-tolcliff, G1, NEW-ws-inband, R2), all carried from 09:14 with corrected numbers.
- **Dropped:** M2 (the knee link must be machined), which the 09:15 skeptic refuted by measurement.

Nothing in the number ranks this design above a design that is better for the wearer. It is 31st of the 37 verified
rows, 4.30 behind H1 (27.20) and 13.22 behind the 3-joint lead conecut-knee-knuckle-3r (18.28). Its own flat cell,
re-verified at 12:06 (32.84, held 29.81), is also 31st.

| check | level | measured |
|---|---|---|
| held_out | ok | held 28.45 vs bench 31.50 (-3.05). Disjoint from the search sample: 29.28 by index, 29.40 by pose vector. With claim-bench copies also removed: 26.40 (`remeasure/crest-knee-3r_joggle_held_overlap.json`) |
| fast_frozen | ok | row fast 26.34 (the flat cell) -> 31.50. The joggle's own fast is 22.02 (+9.48) |
| near_touch | ok (report only) | plain 31.50; 34.08 at < 1 mm, 59.56 at < 2 mm, 88.99 at < 3 mm; band read 3-14 mm 32.91; 28.06 points live in the 1-2 mm shell |
| contact_depth | ok | bench: 5 poses, sum 5.15 mm, deepest 1.96 mm. Held: 2 poses, sum 2.04 mm, deepest 1.42 mm. The tool no longer finds a reproducing depth file for its reference (conecut-knee-knuckle-3r) this run; the 09:02 comparison read 20.24 / 60.97 mm for the lead |
| dominance | ok | vs conecut-knee-knuckle-3r (`--ref`): behind plain and at 2 mm (see below) |
| continuity | watch (tool reading gap) | the flood is on file under the row's `verification_joggle.continuity`: 974 / 974 connected, 0 islands, 0 bench and 0 held poses dropped, connected 31.49 / 28.45. `c_continuity` reads only a top-level `continuity` key or a verifier file with a `connected` dict |
| fold_margin | ok | min th 5.085 deg bench, 5.50 deg held (flat cell 6.23 / 5.33) |
| idle | ok | the knee moves 29.1 deg (K.ang 85.05-114.16) |
| sampling | ok | sample-weighted 0.872 vs part-weighted 0.882 |
| density | ok (not measured by the tool) | per-part nearest-neighbour spacing, measured here on the joggle cell: see "New this pass" |
| complexity | ok | 0.0 recomputed (the knee pins sit outside the count, user 2026-10-17) |
| reporting | watch | the verdict text reads as a screen; the dashboard sweep 22.02 (score 91.99) is 9.48 below the verified number |
| judge_change | ok | no bench, judge or metric file changed in the row's 7 commits |
| rules | ok | O20 hubs, margin >= 5, 0 passive translations, 3 DOF |

## New this pass: the round-3 checks on the cell v_* actually carry

The 12:06 re-run added refutation checks: the J2 fold window as one arc of J2's own angle, the J3 window on the true
link 2 -> member 3 rotation, the knee-pin rotations, per-part sample spacing, and the pin-a stack. It ran them on the
flat cell (`best_params`, 32.84), not on the joggle cell the row's v_* fields show (31.50). Its row record is titled
"RE-VERIFIED". `tools/alignment_crest_knee_v3jog.py` (a new file) runs the v3 verifier source unchanged except three
lines: JogModel, best_params_joggle, and output paths under `docs/alignment/remeasure/crest-knee-3r_v3jog_*`. The runs
were local, niced, 1 thread and 2 processes, on a box at load 13-16.

V3JOG_RESULTS

## What the wearer gets (measured, frozen joggle claim)

Numbers are Bench(110,360) exact, with held out in brackets. Recomputed here from the verifier's dumps
(`remeasure/crest-knee-3r-joggle_v_{bench,held}_perpose.json`, which give 31.49 / 28.45), using min(min_mm, cmin) as
the per-pose floor (the skeptic's correction).

- **Overhead (workspace, elevation >= 140):** the claim takes 7 of 28 (8 of 26). The flat cell took 5 of 28 (6 of 26).
  - Lowest metal on the taken poses: 0.71, 1.06, 1.18, 1.28, 1.36, 2.17 and 2.57 mm. Held: 0.55, 0.70, 0.84, 0.98,
    1.30, 1.34, 1.37 and 1.72 mm, all under 2 mm.
  - The 21 overhead poses it loses: fold 10, J3 stop 8, contact 3.
- **Overhead clip frames (Raise overhead):** 10 of 10 taken. Lowest metal 0.65, 0.65, 0.65, 0.77, 1.01, 1.79, 1.79,
  1.81, 1.85 and 1.87 mm: 4 under 1 mm and all 10 under 2 mm (held 4 and 8).
- **Raised arm (workspace, elevation >= 90):** 34 of 113 taken, 0.30 (37 of 112, 0.33).
- **Metal near the skin over all taken poses:** 6 poses under 1 mm, 34 under 2 mm and 75 under 3 mm (held 10, 37, 81).
- **Contact:** 5 bench poses, all workspace.
  - The deepest are 1.96 mm at plane 30 / elev 165 / axial -60, 1.68 mm at 30 / 75 / 15, then 0.82 at 75 / 165 / -75,
    0.36 at 45 / 75 / 15 and 0.34 at 15 / 165 / -60.
  - Held: 1.42 mm at 135 / 135 / -45 and 0.62 mm at -90 / 60 / 90.
  - None is deeper than 2 mm.
- **Workspace in-band (unscored):** 0.817 (0.794), with 18.2 % of the metal above 14 mm and a maximum of 29.95 mm. The
  scored clip in-band is 0.872 (0.871). The knee link is the furthest-out part, 0.656 in band.
- **Springs:** none. Every coordinate is fixed by closure: three O20 hubs and the two-pin MR63ZZ knee (closure residuals
  <= 0.023 deg).
- **Stops:**
  - The J3 own-angle dowel window: the closest taken pose is 1.33 deg from it (held 1.65). The 12:06 re-run showed that
    q3' equals the true relative angle on the flat cell; see "New this pass" for the joggle.
  - The knee window is [26.6, 153.4] deg. The taken knee angles are 85-114 deg, far from both ends.
- **Cuff twist:** none expected. The knee is closure-determined on bearing pairs, with no spring-held coordinate.
- **Near-singular postures:** min th margin 5.085 deg (5.50 held), at the user's 5 deg line.
- **Build tolerance:** the knee's underside clears the E-strap top near pin a by 0.200 mm at minimum. 25 bench poses are
  under 0.35 mm (finding 1).

## Findings (judgement pass; `docs/alignment/crest-knee-3r.findings.json`)

1. **NEW-tolcliff (watch, carried, unresolved): the joggle's gain is fitted at a 0.20 mm metal-to-metal running gap.**
   - **Evidence.** The pin-a stack rule in `JogModel.finalize` (commit 50c2357) sets the knee level to the lowest value
     that clears the strap: knee-to-strap minimum 0.200 mm. 1 pose is under 0.25 mm, 25 under 0.35 and 46 under 0.45.
   - **Strap-level error, metal-touch reading:**
     - +0.2 mm: 31.78 bench (1 pose), 28.45 held.
     - +0.3 mm: 34.31 (13 poses), 32.08 held (16).
     - The flat cell touches nothing up to +0.3 mm (32.84).
   - **Running-gap reading:** +0.2 mm gives 39.90 / 36.54.
   - **Why the exo is not better by 1.34.** At a 0.3 mm strap error, a normal tolerance for a Ti strap plus a bearing
     stack, the joggle's 1.34-point lead over its own flat cell becomes a 1.47-point deficit. At 0.2 mm the knee rubs.
   - **Why only watch.** The design's rank is held by its own verified flat cell (31st either way). The joggle at 34.31
     would be 32nd, behind zc-frontier-3r (33.51), but that row was never worn through a tolerance harness. So a design
     better for the wearer under the same harness cannot be shown.
   - **Action.** Measure the shimmed build (tr_a and tr_b raised by d after a strap error of d), or pocket the strap end
     under the knee's sweep. Until then, show 31.50 with its tolerance column.
   - Sources: `remeasure/crest-knee-3r_skeptic_joggle_checks.json` and `verify/crest-knee-3r-joggle_v_tolprobe_*.json`.
2. **G1 (watch, carried, floors corrected): overhead metal at the skin.**
   - **Evidence.**
     - All 10 overhead clip frames are under 2 mm, and 4 are under 1 mm.
     - 5 of the 7 overhead workspace poses taken are under 2 mm (all 8 held).
     - The 1-2 mm shell holds 28.06 points.
   - **Against its own flat cell** (12:06: 36.25 / 57.98 at 1 / 2 mm), the joggle is ahead plain and at 1 mm but
     behind at 2 mm, by 1.58.
   - **Why the exo is not better.** The overhead number is bought with metal that a bulging deltoid would touch.
   - **Why only watch.** Near-touch is report-only (user 2026-10-17), and against the lead the design is behind both
     plain and at 2 mm.
   - **Action.** None for the score. For the wearer, the overhead frames need 1-2 mm more standoff at the E strap and
     the seat.
3. **NEW-ws-inband (watch, carried).**
   - **Evidence.** Workspace in-band is 0.817 (0.794) against the scored clip in-band of 0.872. That is a 5.45-point
     shortfall, against 3.4 for the lead and 2.9 for H1 on the same harness. 18-20 % of the metal sits above 14 mm.
   - **Why only watch.** It ranks the design above no one. The wearer gets more standoff than the number shows.
4. **R2 (watch, carried, partly fixed): displayed numbers the design does not hold.**
   - **Fixed since 09:14:** the dashboard's alignment fields now carry 31.5, with alignment_stale false.
   - **Still open:**
     - `morphs.json` shows gap 26.34 (the flat cell's fast) and sweep_gap 22.02 (score 91.99, the joggle's in-sample
       fast best) next to v_gap 31.50.
     - The verdict text still opens "SCREENED ... 32.84" and calls the joggle "claimed, UNVERIFIED".
   - **New:** the 12:06 event and commit title read "verified crest-knee-3r ... v_gap 32.84". The row's v_gap is 31.50.
   - **No rank effect.**
   - **Action (lead or dashboard owner):** rewrite the verdict to the verified joggle cell, and show the fast numbers as
     fast.

### Patterns walked and not present

- **T1 / T2:** covered by G1 (report-only). The band read 3-14 mm costs 1.41 points.
- **T3:** th is the metric read, with a 5.085 deg minimum.
- **T4:** the knee's ang_min is 26.6 deg, against taken knee angles of 85-114 deg. The J3 stop acts on J3's own angle,
  and the poses past it are scored as lost.
- **T5:** shallow presses only: 5.15 mm summed, 1.96 mm deepest.
- **S1:** held out beats the bench by 3.05.
- **S2 / S3:** all 9 metal groups are sampled. Part-weighted in-band is 0.882.
- **S5:** the flood is on file and the skeptic confirmed it twice (974 / 974, 0 dropped).
- **S6:** see "New this pass".
- **M1:** no virtual parts.
- **M2:** refuted at 09:15. The bent-bar build was measured at 32.02, and a machined Ti knee link exists at this size.
  Only the JogModel docstring label "a bent 3 mm bar" remains.
- **M3:** the joggle verifier's sliced knee-vs-strap check, with no exemption near pin a, removes 0 poses. The only
  tight pair is finding 1.
- **M4:** the knee moves 29 deg.
- **M5 / G2 / G3:** no springs.
- **P1:** held is better than the bench.
- **P2:**
  - The held set holds 60 search poses by index and 32 claim-bench copies by pose vector.
  - The clean held reading is 26.40, so the reported 28.45 is not flattered.
- **P3:** every wear of each cell is deterministic and gives the same digits.
  - The joggle read 31.50 three times: the verifier at 08:57, the audit re-wear at 09:02 and the skeptic's wear.
  - The flat cell read 32.84 four times: 00:12, 01:32, 02:45 and 12:06.
  - No wear was repeated until it came out lucky.
- **P4:** the 12:06 commit touched only verify, remeasure, row, doc and event files. No bench, judge or kit changed.
- **R1:** the joggle verifier is independent (08:57), and the 12:06 re-run is a third harness. See "New this pass" for
  what it covered.
- **R3:** the claim is the fast best of 309 joggle tries (22.02). It drops 9.48 to 31.50 frozen, inside the 4.6-14
  drop seen over the verified rows. The spread is on file:
  - joggle cells worn frozen: 31.50 and 31.43 (J4);
  - flat cells worn frozen: 32.84, 33.23 and 37.40.
- **R4:** the dashboard's v_gap equals the verified 31.50.
- **S4:** not automatic. The 5 bench presses sit on the posed skin mesh at elevation 75-165, where nothing in this
  design's numbers points to a rig artefact.
- **G4:** the J3 stop margin is a search variable at 1.32 deg, above the box floor of 1.0. The held pose closest to the
  stop is 1.65 deg from it: a real dowel the wearer reaches, scored as lost beyond it.
- **G5 / G6:** complexity is 0 by the user's knee ruling (encoders cost 0, knee pins outside the count).

### Numbers not obtained

- **`tools/sample_density.py measure`:** not run. The box was at load 13-16 on 4 cores and the 2 process slots were
  taken. The v3 nearest-neighbour spacing stands in for it (see "New this pass").
- **The shimmed-build re-wear (finding 1):** not run. It needs an exact wear per error level, about 10 min each at this
  load.
- **The true held-out clips (data/raw/split.json):** not worn. The model and the verifiers have no wear path for them.
- **A full frozen re-wear:** not repeated, because the claim is unchanged (see the top).

## Proposals (not applied; measurement changes for the lead to decide)

1. **A re-verification targets the cell the row displays (proposed catalogue entry R5, "sibling-cell re-verification").**
   - **Looks like:** a row holds two verified cells. A later skeptic re-run with new refutation checks covers the cell
     that is NOT in v_*, and the row records "RE-VERIFIED". A reader of the row or event takes the new checks as
     covering the displayed number.
   - **Detect:** compare the re-run's `params_key` with the row's `v_params_key`.
   - **Effect on the verified rows:** this row only; it is closed here when the v3jog checks pass (see "New this
     pass").
2. **Carried: M6, a tolerance column for metal-to-metal fits.** Report the gap at +0.1 / +0.2 / +0.3 mm on the tightest
   adjacent pair, on both the running-gap and the metal-touch readings. Measured only here: the joggle reads
   31.78 / 31.78 / 34.31 on the touch reading, against 32.84 flat.
3. **Carried:** `c_continuity` should read nested floods (`verification*.continuity`). This is the third audit of this
   row with the same tool watch, refuted by measurement twice.
4. **Carried:** exclude held poses by pose vector from both the search bench and the claim bench. On this row, held goes
   from 28.45 to 26.40.

## Files

- `docs/alignment/crest-knee-3r.json`: the 14 checks (tool output, this pass).
- `docs/alignment/crest-knee-3r.findings.json`: the 4 findings above.
- `tools/alignment_crest_knee_v3jog.py`: new. It runs the round-3 v3 checks on the joggle cell.
- `docs/alignment/remeasure/crest-knee-3r_v3jog_{bench,held}.json` and `_perpose.json`: its output, if present (see
  "New this pass").
- Unchanged and still current: `remeasure/crest-knee-3r_{bench,held}.json` (deep re-wear of this claim, 09:02),
  `_probe.json`, `crest-knee-3r_skeptic_joggle_checks.json`, `crest-knee-3r_joggle_held_overlap.json`.
