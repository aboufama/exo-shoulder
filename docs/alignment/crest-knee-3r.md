# Alignment audit: crest-knee-3r (joggled cuff knee, round 14 slice r14-A)

Auditor pass 2026-10-19 ~01:35-01:55 UTC, tool VERSION 2026-10-18.1, git 0e9df59. Why it was due: the row and its
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
| dominance | ok | vs conecut-knee-knuckle-3r (`--ref`): behind by 13.22 plain and by 24.72 at 2 mm |
| continuity | watch (tool reading gap) | the flood is on file under the row's `verification_joggle.continuity`: 974 / 974 connected, 0 islands, 0 bench and 0 held poses dropped, connected 31.49 / 28.45. `c_continuity` reads only a top-level `continuity` key or a verifier file with a `connected` dict |
| fold_margin | ok | min th 5.085 deg bench, 5.50 deg held (flat cell 6.23 / 5.33) |
| idle | ok | the knee moves 29.1 deg (K.ang 85.05-114.16) |
| sampling | ok | sample-weighted 0.872 vs part-weighted 0.882 |
| density | ok (tool: not measured) | measured here on the joggle cell: every part on the kit's 2.0 mm grid, worst gap 3.1 mm on link 2 (`remeasure/crest-knee-3r_v3jog_bench.json`) |
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

All five checks pass on the joggle cell, so the joggle claim now carries the same refutation set as the flat cell.
The sources are `docs/alignment/remeasure/crest-knee-3r_v3jog_{bench,held}.json` and the per-pose dumps
`_v3jog_{bench,held}_perpose.json`. The runs took 516 s and 511 s.

| check | bench (Bench(110,360) exact) | held out |
|---|---|---|
| reproduces the claim | 31.50 (dump recomputes 31.49), 0 poses removed | 28.45, 0 removed |
| J2: one arc of J2's own angle | 336 / 0 taken poses on one side of the fold (q2 fold 79.0, stretch -101.0); kinematic set 359 / 0; th from q2 = model th to 0.000 deg | 344 / 0 |
| J3 window on the true link 2 -> member 3 rotation | axis deviation <= 0.0005 deg, q3_true - q3' spread 0.0000 deg, 336 / 336 inside [269.19, +245.09] | <= 0.0026 deg, 0.0000, 344 / 344 |
| knee pins (MR63ZZ pairs) | pin a -16.0..+13.1 deg, pin b -14.4..+14.8 deg, about the pin axis (<= 0.0001 deg) | -16.0..+10.0, -12.4..+14.8 |
| closure | <= 0.023 deg, 0 bad poses; knee vs hub 3 upper 0; boss 0 | <= 0.022 deg, 0 / 0 / 0 |
| sample spacing | every part on a 2.0 mm grid (nearest-neighbour median 1.84-2.0 mm; worst gap 3.1 mm on link 2), 25 contact-only wall / crown sets | same |
| pin-a stack | knee underside 69.325 mm, strap top within 8.5 mm of pin a 69.125 mm: 0.200 mm clearance (finding 1's number, from the body geometry) | same |
| fold margin (th) | 5.085 deg | 5.502 deg |

The fold window is therefore one J2 dowel stop, and the J3 window is a real dowel-in-slot stop between the two bodies J3
connects. Sampling is at the kit's density (about 1 pt / 4 mm2 on a 2 mm grid), so S6 has no over-dense part to
re-weight. The one tight number is still the 0.20 mm pin-a running gap (NEW-tolcliff). The sibling-cell gap
(proposal 1) is closed for this row.

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
- **Near-singular postures:** min th margin 5.085 deg (5.50 held), at the user's 5 deg line. All taken poses are on one
  arc of J2's own angle, so a single J2 dowel realises it.
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

- **`tools/sample_density.py measure`:** not run. The box was at load 13-28 on 4 cores and both process slots held the
  v3jog wears. The v3 nearest-neighbour spacing stands in for it: every part is on the kit's 2 mm grid, so no part is
  over-dense.
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
   - **Effect on the verified rows:** this row only, and it is closed here: every v3 check passes on the joggle cell
     (see "New this pass"). No number moves.
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
- `docs/alignment/remeasure/crest-knee-3r_v3jog_{bench,held}.json` and `_v3jog_{bench,held}_perpose.json`: its output
  (31.50 / 28.45 reproduced, all checks pass).
- Unchanged and still current: `remeasure/crest-knee-3r_{bench,held}.json` (deep re-wear of this claim, 09:02),
  `_probe.json`, `crest-knee-3r_skeptic_joggle_checks.json`, `crest-knee-3r_joggle_held_overlap.json`.

*The sections below the rules are kept from earlier passes. Their rulings were made on the claims named in each
heading (flat 32.84 at 02:45, joggle 31.50 at ~09:15); the auditor pass above (2026-10-19) does not rewrite them.*

---

*Below this rule: the skeptic of the earlier, flat-cell audit (claim 32.84, 2026-10-18 02:45 UTC). Its rulings were
made on the flat cell, not on the joggle claim above.*

## Skeptic (2026-10-18)

Re-measured from the per-pose dumps, the verifier files, the tool code, and two new runs (models and verifier unchanged,
imported; local, niced, at most 2 processes):

- an exact re-wear of the frozen claim through the verifier's own `fit_fast` / `worn` / `extra_checks`, with no dump
  written (`docs/alignment/remeasure/crest-knee-3r_skeptic_wear.py`). It gives 32.84 again.
- a stricter continuity flood (`docs/alignment/remeasure/crest-knee-3r_skeptic_flood.py`).

Rulings: `docs/alignment/crest-knee-3r.rulings.json`. Numbers: `docs/alignment/remeasure/crest-knee-3r_skeptic_checks.json`.

**Final verdict (ledger): WATCH.** 4 reasons upheld (reporting, G1, NEW-ws-inband, R2), 2 refuted with measurements
(continuity, P2).

- **continuity: refuted.** The flood is on file:
  - `rows/crest-knee-3r.json` `verification.continuity`: bench_dropped 0, held_dropped 0, grid 959 / 959 connected,
    0 islands (171 elevation-0 seeds + 788 passed edges = 959).
  - `_v_flood_{bench,held}.json`: connected = static (32.83 / 29.81).
  - A stricter re-run seeded from ONE rest pose and tested every edge, including the elevation-0 ring. It also connects
    959 / 959 with 0 islands and drops 0 bench and 0 held poses.
  - All 171 rest nodes are kin-ok and on one knee branch.
  - The tool's watch is a reading gap: it looks for a top-level `continuity` key.
- **reporting: upheld.** `morphs.json` shows sweep_gap 26.34 against v_gap 32.84. The 6.50 difference is past the
  5-point trigger (`c_reporting`), and 26.34 reads as a score of 90.42. The row's verdict still opens "SCREENED" while
  its status is verified.
- **G1: upheld.** Re-derived from the dumps and again from the independent re-wear:
  - Overhead workspace: 5 / 28 taken, at 0.59, 0.96, 1.23, 1.72 and 2.10 mm (held 6 / 26, at 0.02-1.45 mm).
  - Overhead clips: 10 / 10 taken, at 1.08-1.85 mm.
  - Near-touch gap: 36.25 / 57.98 / 93.37 at 1 / 2 / 3 mm.
  - The 1-2 mm shell is 25.14 points, past shell2_watch 15. Near-touch is report-only, so the level is watch.
  - Caveat: 7 of the 10 held overhead clip frames are pose-vector copies of bench frames. Only the held workspace
    readings are independent.
- **NEW-ws-inband: upheld.** The re-wear gives a workspace in-band of 0.7931, with 20.5 % of the metal over 14 mm
  (max 27.7 mm), against 0.8529 on the clip frames.
  - On the same exact probe harness this is the lowest workspace in-band of the 18 audited bench probes (next lowest
    0.843; H1 0.867, the lead 0.868).
  - Its shortfall to the clip in-band is the largest: 6.0 points on the bench and 7.8 held, against 2.3-4.9 for the
    others.
  - No documented threshold exists for this pattern. The level rests on this measured outlier.
- **P2: refuted.** The overlap is real, but on the clean reading the held number is not flattered:
  - Index match: 60 search poses in the held set. Pose-vector match: 72. Removing either set gives 30.88 (reproduced).
  - The held set also holds 32 clip frames that are pose-vector copies of the CLAIM bench Bench(110,360) (0 by
    index). Their clip in-band is 0.79.
  - Removing every frame shared with either bench leaves 383 poses at 28.13. That is 1.68 better than the reported
    29.81, not 1.07 worse.
  - No documented line is crossed either way.
- **R2: upheld.** The 26.34 is the fast, in-sample number of the same shape that wears 32.84 frozen exact. The three
  frozen cells keep the same order fast and exact (26.34 / 27.63 / 29.02 -> 32.84 / 33.23 / 37.40), so the claim was
  not picked on the claim bench. No rank effect. It overlaps with `reporting`.

### Missed (for the next audit; not counted in this verdict)

1. **The held-out bench copies the claim bench.**
   - `held_bench()` (= `tools/osn_polish.py`) excludes Bench(110,360) by index, but 32 of its 110 clip frames are
     identical by 5-D pose vector to claim-bench frames. They come from Comb hair, Drink, Raise overhead, Reach high
     shelf, Reach back pocket and Wash opposite shoulder.
   - Another 12 clip frames are identical to search frames beyond the 60 index overlap.
   - So a part of every "held out" number made this way repeats the bench. That includes 7 of the 10 held overhead
     clip frames, whose clearances match the bench's to 0.01 mm.
   - Proposal (a measurement change): exclude by pose vector from both benches. On this row that moves held from
     29.81 to 28.13.
2. **The held J3-stop proximity is a search pose.** The 1.0 deg "closest held pose to the J3 stop" is held i 234 (ws
   15 / 135 / -45), which is a Bench(60,160) search pose.
   - The window edge sits at that pose's q3' plus j3stop_margin 1.0, the floor of the CMA box.
   - The nearest held pose the search never saw is 2.42 deg from the stop (bench 4.62 deg).
   - So the stop is fitted to the search sample's extreme pose with the minimum allowed margin. A real wearer at that
     pose is 1 deg from a hard stop.
3. **Not measured (a limitation, not a finding).** The flood treats part-clash and contact poses as passable nodes.
   The bench has 5 workspace clash poses and 5 workspace contact poses (held 3 and 6). A flood with clash walls would
   need the full grid evaluated through `M.run`.

---

## Skeptic of the joggle audit (2026-10-18 ~09:15 UTC, claim 31.50)

Re-measured with the models and both verifiers unchanged (imported; local, niced, at most 2 processes):

- an independent exact re-wear of the joggle claim through the joggle verifier's own `fit_fast` / `worn` /
  `extra_checks` / `joggle_checks`, with no dump written (`docs/alignment/remeasure/crest-knee-3r_skeptic_joggle_wear.py`,
  not the auditor's adapter). It gives 31.50 bench and 28.45 held again, and it also records the knee-to-strap clearance
  of every taken pose;
- the same wear for a bent-bar build (`JOG_MAX=2.78`, the model's own `jog_max`);
- a stricter continuity flood (`crest-knee-3r_skeptic_joggle_flood.py`).

Rulings: `docs/alignment/crest-knee-3r.rulings.json`. Numbers: `docs/alignment/remeasure/crest-knee-3r_skeptic_joggle_checks.json`.

**Final verdict (ledger): WATCH.** 5 reasons upheld (reporting, NEW-tolcliff, G1, NEW-ws-inband, R2), 2 refuted with
measurements (continuity, M2).

- **continuity: refuted.** The flood is on file: row `verification_joggle.continuity` has 974 / 974 connected, 0 islands,
  803 / 803 edges, and 0 bench and 0 held poses dropped. `verify/crest-knee-3r-joggle_v_flood_{bench,held}.json` give
  connected = static. A stricter re-run seeded from ONE rest pose, testing every edge including the elevation-0 ring,
  also connects 974 / 974 and drops 0 / 0. The tool's watch comes from a reading gap: `c_continuity` does not read
  `verification_joggle.continuity`.
- **reporting: upheld.** `morphs.json` shows sweep_gap 22.02 against v_gap 31.50. That is 9.48 apart, past the 5-point
  trigger in `c_reporting`. The row's verdict still opens "SCREENED ... 32.84".
- **NEW-tolcliff: upheld, with its size corrected.**
  - The verifier's probe reproduces to the digit: 31.78 / 31.78 / 34.31 / 39.90 / 51.64 bench at +0.05 / 0.1 / 0.15 /
    0.2 / 0.3 mm.
  - The clearance is 0.20 mm only at its minimum: 1 bench pose is under 0.25 mm, 25 are under 0.35 mm and 46 under
    0.45 mm.
  - "Jam" in that probe means the 0.15 mm running gap is lost. Under a metal-touch reading, +0.2 mm touches 1 bench
    pose (31.78) and 0 held poses. The cliff comes at +0.3 mm: 13 / 16 poses touch, giving 34.31 / 32.08, while the
    flat cell touches nothing up to +0.3 mm (32.84).
  - So the 1.34-point lead becomes a 1.47-point deficit at a 0.3 mm strap error on either reading. At 0.2 mm the lead
    holds only if a running gap under 0.15 mm is accepted. The wearer cost is real: the knee rubs or binds on the strap.
- **G1: upheld.**
  - Near-touch reproduced from the verifier's dumps and from the independent re-wear: 34.08 / 59.56 / 88.99 at
    1 / 2 / 3 mm (held 33.28 / 55.91 / 88.99). The shell is 28.06 points, past shell2_watch 15. Near-touch is
    report-only, so the level is watch.
  - Overhead workspace: 7 / 28 taken, 5 of them under 2 mm. Overhead clips: 10 / 10 taken, 4 under 1 mm and all under
    2 mm.
  - Correction, against the design: the auditor's floor list is the dump's `cmin` column. The true per-pose floors are
    0.71, 1.06, 1.18, 1.28, 1.36, 2.17 and 2.57 mm. For example, pose 90 / 150 / -60 is at 1.18 mm, not 2.96.
- **NEW-ws-inband: upheld.** The re-wear gives a workspace in-band of 0.8174 (held 0.794), with 18.2 % of the metal over
  14 mm (max 29.95 mm), against 0.8719 on the clip frames. That is a 5.45-point shortfall. On the same probe harness the
  lead's shortfall is 3.4 and H1's 2.9.
- **R2: upheld.** `morphs.json` puts gap 26.34 (the flat cell's fast number) and sweep_gap 22.02 (the joggle's fast
  number) next to v_gap 31.50, and alignment_claim is still 32.84. No rank effect.
- **M2: refuted.**
  - The claimed part exists at this size: a machined Ti knee link. The concept doc already says so
    (`docs/concepts/crest-knee-3r.md` lines 581-583), and so does the row's re-dispatch record.
  - The feared bent-bar build was measured. With jog_max 2.78 and the levels re-solved by the model's own LP, then
    frozen and worn exact, it reads 32.02. That is +0.52 on the claim and still ahead of the flat cell's 32.84.
  - The 0.41 mm does not come out of the running gap. The stack rule holds tr_a at 66.075 and the pad rises instead
    (tr_b 62.89 -> 63.295), so the knee-to-strap minimum stays 0.200 mm with the same 25 poses under 0.35 mm.
  - What remains is a label: the `JogModel` docstring still says "a bent 3 mm bar".

### Missed (for the next audit; not counted in this verdict)

These are measurement and reporting slips. None of them moves a rank.

1. **The overhead floor list was optimistic.** The audit's G1 text lists the overhead floors from the dump's `cmin`
   column, not min(min_mm, cmin). Three of the seven values are 0.4-1.8 mm too high. The counts under 1 / 2 mm were
   right. The next probe or audit should read min(min_mm, cmin).
2. **The tolerance probe reports running-gap loss as "jam".** Proposal M6 should carry both readings:
   - running gap lost (clearance < 0.15 + d): 25 poses at +0.2 mm;
   - metal touch (clearance < d): 1 pose at +0.2 mm, 13 at +0.3 mm.
   It should also drop the phrase "0.20 mm on every binding pose": only 1 bench pose is under 0.25 mm.
3. **The concept doc's buildability line is stale.** `docs/concepts/crest-knee-3r.md` line 138 gives a "1.16 mm step"
   over a "12.3 mm ramp run" as too short for a bent bar. The claim's step is 3.19 mm over 13.26 mm, and a 1.16 mm step
   could be bent in 12.3 mm (it allows 2.38 mm of rise). The conclusion (machined) is right; the reason on file is wrong.
4. **The joggle's real worth depends on the build.** The row's lesson says the joggle is worth about 1.07 against the
   flat + stack-rule control (32.50). Built as a bent bar (32.02) it is worth 0.48. With a 0.3 mm strap error it is
   worth less than nothing against the flat cell.

---

## Skeptic of the 2026-10-19 audit (2026-10-19 ~02:20-02:30 UTC, claim 31.50)

Re-measured with the model and both verifiers unchanged (imported; local, nice 10, 1 thread, 2 processes, box at
load ~22):

- an independent exact re-wear of the joggle claim through the joggle verifier's own `fit_fast` / `worn` /
  `extra_checks` / `joggle_checks` (`remeasure/crest-knee-3r_skeptic_joggle_wear.py`, unchanged, no dump written,
  206 s). It gives 31.50 again (fit_fast 22.02), with the knee-to-strap clearance of every taken pose;
- the strict one-seed continuity flood (`remeasure/crest-knee-3r_skeptic_joggle_flood.py`, unchanged);
- a re-derivation of overhead, near-touch and contact from the per-pose dumps. The auditor's new
  `_v3jog_{bench,held}_perpose.json` and the joggle verifier's `-joggle_v_{bench,held}_perpose.json` agree on every
  field of all 470 + 470 poses.

Rulings: `docs/alignment/crest-knee-3r.rulings.json`. Numbers: `docs/alignment/remeasure/crest-knee-3r_skeptic_2026-10-19.json`.

**Final verdict (ledger): WATCH.** 5 reasons upheld (reporting, NEW-tolcliff, G1, NEW-ws-inband, R2), 1 refuted with
a measurement (continuity).

- **continuity: refuted (third time).** The flood is on file: row `verification_joggle.continuity` has 974 / 974
  connected, 0 islands, 803 / 803 edges, 0 bench and 0 held poses dropped. `verify/crest-knee-3r-joggle_v_flood_*.json`
  give connected = static (31.49 / 28.45). Re-run this pass from ONE rest seed with every edge tested: 974 / 974,
  0 islands, all 171 elevation-0 nodes on one knee branch, 0 / 0 dropped. The watch comes from `c_continuity`
  (lines 461-487), which does not read `verification_joggle.continuity` or a flood file's nested `bench.connected`.
- **reporting: upheld.** `morphs.json` shows sweep_gap 22.02 (score 91.99) against v_gap 31.50: 9.48 apart, past the
  documented 5-point trigger. The row verdict opens "SCREENED". The re-wear confirms 22.02 is the same shape's
  in-sample fast number. The leader card does not show it (22.02 > the 18.28 lead), but the table's "Sweep best gap"
  column does.
- **NEW-tolcliff: upheld, comparison corrected.**
  - The re-wear reproduces the clearance: min 0.200 mm, 1 pose under 0.25, 25 under 0.35, 46 under 0.45.
  - Running-gap reading: 31.78 / 34.31 / 39.90 / 51.64 at +0.1 / 0.15 / 0.2 / 0.3 mm.
  - Metal-touch reading: 31.50 up to +0.15 mm, then 31.78 (1 pose) at +0.2 and 34.31 (13 poses) at +0.3.
  - Correction: on the running-gap reading the flat cell is not a tolerant fallback. At +0.3 mm it jams 77 poses and
    reads 63.24, against the joggle's 46 poses and 51.64 (`verify/crest-knee-3r-joggle_v_tolprobe_flatcell_bench.json`).
    The flat cell's minimum clearance is 0.334 mm. The "1.47 deficit on either reading" holds on the touch reading
    only. Both cells sit on a strap-tolerance cliff; the joggle's starts 0.134 mm earlier.
- **G1: upheld.** Re-derived from both dumps and from the re-wear:
  - Near-touch: 34.08 / 59.56 / 88.99 at 1 / 2 / 3 mm (held 33.28 / 55.91 / 88.99).
  - Overhead workspace: 7 / 28 taken, at 0.71, 1.06, 1.18, 1.28, 1.36, 2.17 and 2.57 mm. The 21 lost poses are fold
    10, J3 stop 8 and contact 3.
  - Overhead clips: 10 / 10 taken, 4 under 1 mm and all 10 under 2 mm.
  - Contact: 5 poses, 5.15 mm summed, deepest 1.96 mm.
  - Shell (near2 - plain): 28.06, above shell2_watch 15. Near-touch is report-only, so the level is watch.
  - Label note: 2.58 of those 28.06 points come from the 0-1 mm shell. The 1-2 mm shell alone is 25.48.
- **NEW-ws-inband: upheld.** The re-wear gives a workspace in-band of 0.8174 against 0.8719 on the clips, a
  5.45-point shortfall (held 7.73). Over all 34 probe files on file, the four crest cells have the four largest
  shortfalls (5.45-7.75). Next is groove-desmo at 4.92, then the lead at 3.36 and H1 at 2.88.
- **R2: upheld.**
  - `morphs.json` shows gap 26.34 (the flat cell's fast number) and sweep_gap 22.02 next to v_gap 31.50.
  - The row verdict opens "SCREENED ... 32.84" and still calls the joggle "claimed, UNVERIFIED".
  - The alignment fields are fixed (31.5, not stale).
  - No rank effect.

### Missed (for the next audit; not counted in this verdict)

1. **The tolerance comparison flips with the reading.** The audit and both earlier skeptics wrote that at a 0.3 mm
   strap error the joggle trails its flat cell "on either reading", and that the design's rank "is held by its own
   flat cell under any error up to 0.3 mm". On the verifier's own running-gap reading (clearance < 0.15 + d) the flat
   cell jams 77 bench poses and reads 63.24 at +0.3 mm, worse than the joggle's 51.64
   (`verify/crest-knee-3r-joggle_v_tolprobe_flatcell_bench.json` rows[4]). The fallback holds on the metal-touch
   reading only. This cuts against the design, not for it: on the running-gap reading neither cell keeps its number at
   +0.3 mm. Proposal M6 should require the tolerance column for both cells on both readings, plus the held flat cell,
   which is not on file.
2. **The J3 stop's contact-to-stop trade was not re-measured on the joggle cell.**
   - The 02:28 audit measured on the flat cell that the J3 window buys 1.14 points (33.97 without it, 32.83 with it)
     by turning 4 contact presses into stops; on the search bench those presses were up to 7.21 mm deep
     (`remeasure/crest-knee-3r_bench_noj3win.json`).
   - The joggle claim stops 24 bench and 28 held poses, including 8 of its 21 lost overhead poses. In the dumps these
     poses are `ev` False, so they sit outside the contact term, as do the 18 bench part-clash poses.
   - No no-window wear of the joggle cell is on file, so how much of 31.50 the stop buys this way is unknown.
   - The window is fitted as the kept poses' q3' set minus its largest gap, shrunk by j3stop_margin 1.32
     (`models/crest-knee-3r.py` lines 11-12, 90-100). It spans 335.9 deg, and its dowel or slot is not sampled as
     metal.
3. **The shell label.** `c_near_touch` reports near2 - plain as "points in the 1-2 mm shell". Since contact became
   metal < 0 mm, that difference also holds the 0-1 mm shell: here 2.58 of the 28.06 points. No threshold changes on
   this row (25.48 > 15).

**Final verdict (ledger): WATCH.**
