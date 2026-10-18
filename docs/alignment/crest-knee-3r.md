# Alignment audit: crest-knee-3r (joggled cuff knee, round 14 slice r14-A)

Auditor pass 2026-10-18 ~09:05 UTC, tool VERSION 2026-10-18.1. The claim moved since the last audit: the verified flat
cell (32.84, audited 02:28, skeptic 02:45) was replaced by the joggled knee-link cell (kj=1, `best_params_joggle`,
verified 08:57).

## Verdict: WATCH (claim v_gap 31.50, score 88.55)

The ledger verdict is WATCH, from 7 watch reasons and no gamed one (`python3 tools/alignment_ledger.py get crest-knee-3r`).

The re-wear reproduces the claim to the digit: Bench(110,360) exact 31.50 and held out 28.45. The files are
`docs/alignment/remeasure/crest-knee-3r_bench.json` and `_held.json`, re-worn through
`tools/alignment_crest_knee_joggle_adapter.py` (a new file; the model runs unchanged and builds its own JogModel from
kj=1).

Nothing in the number ranks this design above a design that is better for the wearer. It is 25th of the 31 verified
rows, 4.30 behind H1 (27.20) and 13.22 behind the lead (18.28). The flat cell's 32.84 would also be 25th.

What is weaker than the number says:
- **NEW-tolcliff:** the 1.34-point gain over the flat cell sits on a 0.20 mm metal-to-metal running gap. A 0.2 mm
  build error turns it into a 7-point loss.
- **G1:** overhead metal sits at 0.5-2 mm.
- **NEW-ws-inband:** the in-band the score does not read (workspace poses) is 0.82, not the scored 0.87.
- **R2 / reporting:** the dashboard mixes two cells.
- **M2:** the knee link must be machined, not bent.

| check | level | measured |
|---|---|---|
| held_out | ok | held 28.45 vs bench 31.50 (-3.05, re-measured). Disjoint from the search sample: 29.28 by index, 29.40 by pose vector. With claim-bench copies also removed: 26.40 (`remeasure/crest-knee-3r_joggle_held_overlap.json`) |
| fast_frozen | ok | row fast 26.34 (the flat cell) -> 31.50. The joggle's own fast is 22.02 (+9.48) |
| near_touch | ok (report only) | plain 31.50; 34.08 at < 1 mm, 59.56 at < 2 mm, 88.99 at < 3 mm; band read 3-14 mm 32.91; 28.06 points live in the 1-2 mm shell |
| contact_depth | ok | bench: 5 poses, sum 5.15 mm, deepest 1.96 mm. Held: 2 poses, sum 2.04 mm, deepest 1.42 mm. The lead: 20.24 / 60.97 mm |
| dominance | ok | vs conecut-knee-knuckle-3r: -13.22 plain, -24.72 at 2 mm |
| continuity | watch (tool reading gap) | the flood is on file under `verification_joggle.continuity`: 974 / 974 connected, 0 islands, 803 / 803 edges passed, 0 bench and 0 held poses dropped, connected 31.49 / 28.45. The tool reads only a top-level key |
| fold_margin | ok | min th 5.085 deg bench, 5.50 deg held (flat cell: 6.23 / 5.33) |
| idle | ok | the knee moves 29.1 deg (K.ang 85.05-114.16) |
| sampling | ok | sample-weighted 0.872 vs part-weighted 0.882 |
| density | ok | not measured |
| complexity | ok | 0.0 recomputed (the knee pins sit outside the count, user 2026-10-17) |
| reporting | watch | the verdict text reads as a screen; the dashboard sweep 22.02 (score 91.99) is 9.48 below the verified number |
| judge_change | ok | no bench, judge or metric file changed in the row's 6 commits |
| rules | ok | O20 hubs, margin >= 5, 0 passive translations, 3 DOF |

## What the wearer gets (measured, frozen joggle claim)

Numbers are Bench(110,360) exact, with held out in brackets. Files: `remeasure/crest-knee-3r_{bench,held}_probe.json`,
`_{bench,held}.json` (deep), and the verifier's dumps `remeasure/crest-knee-3r-joggle_v_{bench,held}_perpose.json`.

- **Overhead (workspace, elevation >= 140):** the claim takes 7 of 28 (8 of 26). The flat cell took 5 of 28 (6 of 26).
  - Lowest metal on the taken poses: 0.71, 1.36, 1.68, 1.76, 2.17, 2.57 and 2.96 mm (held 0.55, 0.70, 0.84, 1.30,
    1.34, 1.37, 1.72 and 2.18 mm).
  - The 21 overhead poses it loses: fold 10, J3 stop 8, contact 3 (held: fold 11, J3 stop 7).
- **Overhead clip frames (Raise overhead, elevation 148-150):** all 10 are taken. On 4 of the 10 the lowest metal is
  under 1 mm, and on all 10 it is under 2 mm (held 4 and 8). The flat cell had 0 under 1 mm (all at 1.08-1.85 mm).
- **Raised arm (workspace, elevation >= 90):** 34 of 113 taken (0.30); held 37 of 112 (0.33). The flat cell: 32 and 35.
- **Metal near the skin over all taken poses:** 6 poses under 1 mm, 34 under 2 mm, 75 under 3 mm (held 10, 37, 81).
  The flat cell: 6, 34, 77.
- **Contact:** 5 poses (held 2), all on workspace poses.
  - The deepest is 1.96 mm at plane 30 / elev 165 / axial -60; next 1.68 mm at 30 / 75 / 15.
  - Held: 1.42 mm at 135 / 135 / -45.
  - Three of the five bench presses are at elevation 165. None is deeper than 2 mm (the lead's deepest is 8.93 mm).
- **Workspace in-band (unscored):** 0.817 (0.794), with 18.2 % (20.5 %) of the metal above 14 mm and a maximum of
  29.95 mm. The scored clip in-band is 0.872 (0.871). The knee link is the furthest-out part, 0.656 in band.
- **Springs:** none. Every coordinate is fixed by closure: three O20 hubs plus the two-pin MR63ZZ knee (closure
  residuals <= 0.023 deg, row `verification_joggle.bench.extra`).
- **Stops:**
  - The J3 own-angle dowel window is 245.1 deg wide. The closest taken pose is 1.33 deg from it (held 1.65 deg).
    `j3stop_margin` is a search variable (1.32 here; 1.0, the box floor, on the flat cell).
  - The knee window is [26.6, 153.4] deg, and the taken knee angles are 85-114 deg, far from both ends.
- **Cuff twist:** none expected. The knee is closure-determined on bearing pairs; there is no spring-held coordinate.
- **Near-singular postures:** min th margin 5.085 deg (5.50 held), at the user's 5 deg line. The flat cell had 6.23.
- **Build tolerance (the new thing):** the knee's underside rides 0.20 mm over the E-strap top near pin a, on every
  pose where the rule binds. The verifier's tolerance probe:

| strap-level error | joggle bench | joggle held | flat cell bench |
|---|---|---|---|
| 0 | 31.50 | 28.45 | 32.84 |
| +0.05 mm | 31.78 | 28.45 | 32.84 |
| +0.1 mm | 31.78 | 29.56 | 32.84 |
| +0.2 mm | 39.90 (25 jam) | 36.54 (24 jam) | 33.11 (1 jam) |
| +0.3 mm | 51.64 | 48.85 | 63.24 |

Source: `docs/concepts/verify/crest-knee-3r-joggle_v_tolprobe_{bench,held,flatcell_bench}.json`.

## Findings (judgement pass; `docs/alignment/crest-knee-3r.findings.json`)

1. **NEW-tolcliff (watch): the gain is fitted at a 0.20 mm metal-to-metal running gap.**
   - **Evidence.** The joggle's pin-a stack rule (commit 50c2357, `JogModel.finalize`) raises the knee's pin-a level
     only to the lowest value that clears the E strap by 0.15 + 0.05 mm. The claim's minimum clearance is therefore
     the rule's floor, 0.20 mm (held 0.203). The flat cell clears by 0.334 mm.
   - At +0.2 mm strap-level error the claim reads 39.90 (held 36.54), and the flat cell 33.11. The claimed cell is
     better at nominal and 6.79 points worse at a 0.2 mm error. The row's own lesson: the joggle is worth ~1.07, and
     the rest of its gain comes from the stack rule opening a seat region.
   - **Why the exo is not better by 1.34.** A Ti strap, a bent bar and a bearing stack each carry 0.1-0.2 mm. The
     score reads the nominal geometry only.
   - **Why only watch.**
     - The ranking does not move: 25th at 31.50, 32.84 or 33.11.
     - No other row has been worn through a tolerance probe, so "a design better for the wearer" cannot be shown under
       the same harness.
     - An assembly shim at pin a, or the verifier's fix (skim the strap top flush with the boss face inside the knee's
       sweep), would likely remove the cliff for a sub-mm standoff cost. Neither is measured.
   - **Action.** Measure the shimmed build: the frozen claim with tr_a and tr_b raised by d after a strap error of d.
     Until then, report 31.50 with its tolerance column.
2. **G1 (watch): overhead metal at the skin.**
   - **Evidence.** All 10 overhead clip frames are under 2 mm, and 4 are now under 1 mm (the flat cell had 0). Of the 7
     overhead workspace poses taken, 5 are under 2 mm. The 1-2 mm shell holds 28.06 points, past the old T1 'gamed'
     line of 25.
   - Against its own flat cell the joggle is ahead plain (by 1.34), at 1 mm (2.17) and at 3 mm (4.38), but behind at
     2 mm (by 1.58).
   - **Why only watch.** Near-touch is report-only (user 2026-10-17), and against the lead the design is behind both
     plain and at 2 mm.
   - **Action.** None for the score. For the wearer, the overhead frames need 1-2 mm more standoff at the seat or the
     strap.
3. **NEW-ws-inband (watch, carried, smaller).**
   - **Evidence.** On the poses the score does not read, the workspace in-band is 0.817 (0.794), against 0.872 on the
     scored clip frames, with 18-20 % of the metal above 14 mm. The flat cell read 0.793 / 0.775; H1 and the lead read
     0.867 / 0.868.
   - **Why it matters.** The joggle improved it, but the wearer still gets more 15-30 mm standoff than the number shows.
4. **R2 / reporting (watch): the dashboard mixes two cells.**
   - **Evidence.** v_gap is 31.50 (the joggle). gap 26.34 is the flat cell's fast best, and sweep_gap 22.02 (score
     91.99) is the joggle's in-sample fast best of 309 tries. The verdict text opens "SCREENED ... 32.84" and calls
     the joggle "claimed, UNVERIFIED". The alignment fields still carry the flat claim 32.84 (alignment_stale true).
   - No rank effect: the leaderboard ranks by v_gap.
   - **Action.** The lead or the dashboard owner: rewrite the verdict to the verified joggle cell and show sweep_gap
     next to the frozen number it wears.
5. **M2 (watch): the knee link has to be machined.**
   - **Evidence.** The model's docstring says "a bent 3 mm bar, one straight ramp <= 60 deg". The claimed step is
     3.19 mm over a 13.26 mm run, and a 3 mm bar at the user's 15 mm inner bend radius rises only 2.78 mm there
     (verifier: bent_bar_ok false). The re-dispatch record says "machined Ti knee link"; the mechanism record and the
     docstring do not.
   - A bent-bar build would lose 0.41 mm of step, twice the 0.20 mm running gap (finding 1). Not measured.
   - **Action.** State "machined from solid" on the part and in `mechanism.notes`, as the CAD ruling requires.

### Patterns walked and not present

- **T1 / T2:** covered by G1 (report-only). The band read 3-14 mm costs 1.41 points (32.91 against 31.50).
- **T3:** th is the metric read, 5.085 deg minimum.
- **T4:** the knee's ang_min is 26.6 deg against taken knee angles of 85-114 deg. The J3 stop is a stop on the joint's
  own angle, not a singularity, and the poses past it are scored as lost.
- **T5:** shallow presses only: 5.15 mm summed, deepest 1.96 mm.
- **S1:** held out beats the bench by 3.05, and the disjoint-from-search held set by 2.22. The search bench is
  Bench(60,160) fast, not the envelope bench (the cache is missing locally); this is a re-dispatch, not a final
  polish.
- **S2 / S3:** part-weighted in-band 0.882. All 9 metal groups are sampled (hub1-3, E, boss, pad, knee, L1, L2).
- **S5:** the flood is 974 / 974 connected, with 0 islands and 0 poses dropped.
- **M1:** no virtual parts. The knee link's six boxes follow the step law to 0.0 mm.
- **M3:** the joggle's sliced collision checks remove 0 poses. The only tight pair is knee to E at 0.20 mm (finding 1).
- **M4:** the knee moves 29 deg.
- **M5 / G2 / G3:** no springs.
- **P1:** held is better than the bench.
- **P2:** the held set holds 60 search poses by index (72 by vector) and 32 claim-bench copies.
  - Disjoint from the search: 29.28 / 29.40.
  - Clean (both removed): 26.40.
  - The reported 28.45 sits between them, so it is not flattered on the clean reading
    (`remeasure/crest-knee-3r_joggle_held_overlap.json`).
- **P3:** two joggle cells were worn frozen. The claimed one is the fast best (22.02 -> 31.50), not the better frozen
  one (J4: 23.31 -> 31.43), so it was not picked on the claim bench.
- **P4:** the model gained the pin-a stack rule in the same task. It is the design's own fit rule and more conservative
  (it raises the knee), not a bench or judge change.
- **R1:** the verifier is independent (`verify/crest-knee-3r-joggle.py`, 0 poses removed).
- **R3:** see R2.
- **R4:** the dashboard's v_gap of 31.50 equals the verified number.
- **G4:** see T3 / T4.
- **G5 / G6:** complexity is 0 by the user's knee ruling; the machined knee link adds no joint.

### Numbers not obtained

- **Density:** `tools/sample_density.py` was not run (time box). The tool level is ok.
- **The shimmed-build re-wear (finding 1):** not run. It needs a new adapter that offsets the frozen tr_a and tr_b,
  plus a 3-minute exact wear per error level.
- **The bent-bar build (finding 5):** not run. The step limited to 2.78 mm needs a JogModel re-fit with jog_max
  2.78, a parameter the model has.
- **The true held-out clips (data/raw/split.json):** not worn. The model and the verifier have no wear path for them.

## Proposals (not applied; measurement changes for the lead to decide)

1. **A tolerance column for metal-to-metal fits (proposed catalogue entry M6, "nominal-clearance fit").**
   - **Looks like:** a fit rule sets a running gap at its floor, so the claim's tightest metal-to-metal clearance
     equals the rule's minimum on every binding pose.
   - **Why not better:** the build carries 0.1-0.2 mm per part.
   - **Detect:** wear the frozen claim with the tight pair's level moved by +0.1 / +0.2 mm (as the verifier did here)
     and report the gap next to the claim. Flag watch when +0.2 mm costs more than the claim's margin over its next
     cell or rival.
   - **Effect on the verified rows:** measured only here (+8.40 bench at +0.2 mm on the joggle, +0.27 on the flat
     cell). The other rows' pin-knee stack rules use the same 0.15 mm ADJ and are unmeasured. Measuring them needs
     one exact wear per row per level. This is a measurement change, never an input to a verdict until the lead adopts
     it.
2. **The continuity check should read nested floods** (`verification*.continuity`). That is the second time on this
   row, and the skeptic refuted the tool's watch for the same reason on the flat cell.
3. **Carried from the flat-cell audit:** exclude held poses by pose vector from both the search bench and the claim
   bench. On this row that moves held from 28.45 to 26.40.

## Files

- `docs/alignment/crest-knee-3r.json`: the 12 checks (tool output).
- `docs/alignment/crest-knee-3r.findings.json`: the 5 findings above.
- `docs/alignment/remeasure/crest-knee-3r_{bench,held}.json`: deep re-wear of the joggle claim (near-touch 1 / 2 / 3,
  histogram, spans).
- `docs/alignment/remeasure/crest-knee-3r_{bench,held}_probe.json`: wear probe from the same worn bench.
- `docs/alignment/remeasure/crest-knee-3r_flatcell_{bench,held}{,_probe}.json`: the flat cell's re-wears from the
  02:28 audit, kept for comparison.
- `docs/alignment/remeasure/crest-knee-3r_joggle_held_overlap.json`: the held set split into search, claim-bench and
  unseen poses.
- `tools/alignment_crest_knee_joggle_adapter.py`: the re-wear adapter. It re-uses `tools/alignment_crest_knee_adapter.py`
  with the row's `v_params_key` parameters.

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
