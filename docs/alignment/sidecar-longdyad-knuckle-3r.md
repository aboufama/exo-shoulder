# Alignment audit: sidecar-longdyad-knuckle-3r (verified lead, round-8 winner)

Hourly audit, 2026-10-16 22:45 UTC, at git 5bc1adf onward. The audit wrote one new tool,
`tools/alignment_drive_cap_wear.py`. It edited no bench, judge, model, row or dashboard.

## Verdict: WATCH (ledger)

- **Claim:** verified v_gap **18.91**, score 93.12, frozen exact Bench(110,360).
- **Ledger reasons** (all watch):
  - two from the tool: near_touch and reporting;
  - five from the judgement pass: NEW-catalogue-drive, NEW-unpriced-stops, G1, M5 and R1.
- **The number reproduces to the digit.** Both re-wears ran on the farm with the row's best_params and the model
  unchanged:
  - bench: 18.91 / 1 mm 20.00 / 2 mm 34.03 / 3 mm 155.98;
  - held out: 22.67 / 25.75 / 37.24 / 163.09.

  Files: `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_bench.json` and `_held.json`. The 3 mm held-out wear is
  new; it was missing from the 20:26 audit.
- **The number describes a modelled drive, not yet a buildable one.** With the catalogue ball link and the build
  spec's stop B, the same harness measures:
  - bench: **19.76** (score 92.81) / 20.85 / 34.39;
  - held out: 23.53 / 26.63 / 37.95.

  The ranking order among the 3-active rows does not change, and nothing better for the wearer drops below it, so
  the verdict is watch, not gamed.

## What the wearer gets (measured)

| item | value | file |
|---|---|---|
| Overhead reach (elev >= 140), workspace | **8 / 28 taken** on the bench, 18 / 71 held out. Lost on the bench: fold 14, slide 4, contact 2 | `remeasure/..._bench.json` audit.overhead140; `_held.json` |
| Raised-arm reach by elevation (taken / total) | 0-60: 161/172; 60-90: 55/75; 90-120: 25/51; 120-140: 12/34; 140-160: 5/13; 160-200: **3/15** | `remeasure/..._probe.json` ws_reach_by_elev |
| Taken poses with metal < 2 mm | 26 of 371 on the bench (near2_poses), 63 of 859 held out. Overhead: **8 of 10 clip frames and 5 of 8 taken workspace poses** | `_bench.json` / `_held.json` deep; `_probe.json` clip_overhead140 / ws_overhead140 |
| Metal < 1 mm on taken poses | 2 on the bench, 14 held out. Min metal 0.28 mm on the bench, 0.14 mm held out. 10th-percentile overhead min metal 1.02 mm on the bench, **0.64 mm held out** | same |
| Contact (metal into skin, penalised) | 4 bench workspace poses (contact 0.0107 = 1.07 gap points). Deepest **-4.61 mm** at plane 30 / elev 165 / axial -60 (overhead); then -0.77 (plane 60 / elev 150), -0.74 (plane -60 / elev 60), -0.11 (plane 15 / elev 135). Held out: 10 poses | `_probe.json` contact_poses |
| Workspace in-band (unscored) | 2-14 mm: 0.874 over the 261 taken workspace poses (clips 0.897); 2-10 mm: 0.554; > 14 mm: 12.6 %; > 20 mm: 2.8 %. Overhead workspace 0.926 | `_probe.json` ws_unscored |
| Band read 3-14 mm | 19.22 on the bench (+0.31), 23.00 held out (+0.33). The band edge is not exploited | `_bench.json` / `_held.json` deep.gap_band3_14 |
| Fold margin (th, the one metric) | min 5.232 deg over taken poses (5.513 priced; 5.021 held out at r_h 15.5) | row final_polish; `docs/research/sidecar_mechanism_redteam.md` section 5 |
| Continuity | full flood 18.91 (0 dropped); knn flood 21.72 (10 dropped) | `verify/sidecar-longdyad-knuckle-3r_v_bench_frozen.json` |
| Springs | K clock spring 0.08 N.m preload (0.05 enough), 0.015 N.m/rad | red team table, section 2 |
| J2 step felt at drive onset | 0.13-0.20 N.m | red team finding 5 |
| Drive play | about 0.2 deg RSS of K. The cuff does not feel it: K is slaved and the 3 active joints close the chain | red team section 4 |
| Cuff twist, R17 | **not measured**: R17 with the slaved coupling has not run on this design (gen-6 L1 has build.json, no judge/ yet) | `pipeline/full-exo/designs/l1_sidecar-longdyad/` |
| DOF and complexity | 3 active, 0 passive translations, complexity 49 (recomputed). O20 hubs | `docs/alignment/sidecar-longdyad-knuckle-3r.json` |

## Findings

### NEW-catalogue-drive (watch): the verified number uses a ball-link eye smaller than the catalogue part

- **Evidence.**
  - The model samples an O7 socket at both rod ends.
  - The gen-6 red team found the real M2 ball link, igus KBRM-02 / KBLM-02 (head O9 x 4), comes within 0.87 mm of
    hub 2 at dK 36 and 0.07 mm at dK 40, and within 0.62 mm of hub K's O20 cylinder
    (`docs/research/sidecar_mechanism_redteam.md`, finding 2).
  - The taken K opening reaches 37.8 deg on the bench and 38.5 deg held out (coord_spans.dK in the re-wears).
- **The build spec's stop B at dK 35.4 was "counted, not measured".** Measured now with
  `tools/alignment_drive_cap_wear.py`: the model runs unchanged, and only its own drive-range truncation is capped at
  35.4 on every bench. With r_h 15.5:

| reading | bench plain | 1 mm | 2 mm | held out | held 1 mm | held 2 mm | poses lost |
|---|---|---|---|---|---|---|---|
| verified (O7 eye, r_h 14.87) | 18.91 | 20.00 | 34.03 | 22.67 | 25.75 | 37.24 | - |
| r_h 15.5, uncapped (control) | 18.92 | 20.01 | 34.03 | - | - | - | 0 |
| r_h 15.5, stop B at dK 35.4 (KBRM-02) | **19.76** | 20.85 | 34.39 | **23.53** | 26.63 | 37.95 | 3 bench / 10 held out, none overhead |

  Files: `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_rh155_bench.json`, `_rh155cap354_bench.json` and
  `_rh155cap354_held.json`.
- **Why the exo is not yet as good as 18.91 says.** The 0.85 points belong to a custom O7 x 3 crank-tip eye with a
  pressed iglidur cup, and to a horn eye that clears hub K's real dome by >= 1 mm. Neither has been built or judged.
  With catalogue parts, the design scores 19.76. That is behind the verified sidecar-parallelogram's 19.13 on the plain
  gap, though still far ahead of it at 2 mm (34.39 against 50.14). The 0.6 mm horn spacer the red team prices at about
  +0.2 fast is not in this wear.
- **Action.**
  1. Show the buildable reading next to 18.91 on HANDOFF and the dashboard: 19.76 with KBRM-02, or 18.91 if the custom
     eye passes the L1's R6 / R16 at 1 mm.
  2. Compare a challenger against the lead's buildable reading only when the challenger's own drive is priced the
     same way.

### NEW-unpriced-stops (watch): an unpriced verified number on a leaderboard of priced ones

- **Evidence.**
  - The verified reading has smlo 5.0, and a1max 63.1774 = bk1 + bk2 - 5 exactly. Its min th margin is 5.232.
  - Priced with the minarc judge's built-stop tolerance (+0.5, CB_FOLD_MARGIN 5.5), it reads 19.36 / 20.45 / 34.63,
    held out 23.29 (row final_polish.priced; `docs/research/sidecar-longdyad-knuckle-3r_final_polish.md` lines 174-175).
  - minarc pick1 (18.40) and BDp (19.54, of which +0.48 is priced) carry that pricing
    (`docs/research/minarc_final_polish.md` lines 96 and 140-142).
- **Why it matters.** HANDOFF says "the best 3-active design is now within 0.51" of the 4-active lead. Priced alike,
  the gap is 0.96. With the catalogue drive as well it is about 1.8; that is an estimate, as the combined wear was not
  run. The order is unchanged, so this is watch.
- **Action.** Rank only priced readings against priced readings (proposal P-b).

### G1 (watch): metal hugs the skin overhead

- **Evidence.**
  - 15.12 points of the bench gap live in the 1-2 mm shell (20.00 -> 34.03), and 11.49 held out (25.75 -> 37.24).
  - Overhead (elev >= 140), 8 of 10 clip frames and 5 of 8 taken workspace poses have metal < 2 mm, one < 1 mm.
  - The 10th-percentile overhead min metal is 1.02 mm on the bench and 0.64 mm held out.
- **Why not better.** On a real, bulging arm, metal at 1-2 mm overhead is metal on skin, and overhead is where the goal
  asks most.
- **Why watch, not gamed.**
  - It is below the 25-point line.
  - It beats every verified 3-active row at 2 mm: frontload 43.98, parallelogram 50.14, roller-flank 46.8 per the
    ledger.
- **Action.** Keep reporting 2 mm and the overhead floor. The overhead hub crowns are the next lever for the wearer
  (hub 3 in-band 0.60 and L2 0.75 are the out-of-band parts).

### M5 (watch): one spring holds the whole drive, and R17 has not judged it

- **Evidence.**
  - K's clock spring (0.08 N.m) keeps the train horn -> rod -> crank -> roller -> lobe in compression.
  - Lift-off above about 30 rad/s2 of q2 acceleration is gen-5's estimate.
  - The new R17 slaved coupling (commits 5d6b819 / 9f28755: force closure, lift-off switched off on a pull) has not run
    on this design. The gen-6 L1 is still building.
- **Why it matters.** The verified number assumes K exactly on its law in every pose.
- **Action.** Run R17 on l1_sidecar-longdyad with the slaved entry, and report K against the law, lift-off and cuff
  twist.

### R1 (watch): stale text on a verified row

- **Evidence.**
  - The row's and the dashboard's verdict text still opens "SCREENED, a candidate for the verifier. Best self-measured".
  - HANDOFF line 81 says "no polish, no CAD", but the polish closed at 22:03 with no replacement and gen-6 CAD is
    running.
  - The dashboard row still holds the CMA fast best (10.3, reach 0.80) in its gap / reach fields. It is labelled as a
    sweep, 8.61 below the verified number.
- **Action.** Refresh the verdict text and the HANDOFF line at the next dashboard refresh.

## Patterns checked and clean (with the measured reason)

| pattern | result |
|---|---|
| T2 (band edge) | the 3-14 mm read costs 0.31 / 0.33 |
| T3 (margin read on another angle) | th margin 5.232 on file in the one metric |
| T4 (search bound walks toward a singular posture) | a1max sits on its clamp bk1 + bk2 - 5, but stop B never binds: a1max -3 is identical in every gate cell (row limiter). The polish bounded ang_min at the verified 26.88 |
| S1 / P1 (in-sample tuning) | held out +3.76, under 6 |
| S2 (sparse sampling) | part-weighted in-band 0.923 >= sample-weighted 0.897. Rod (13 samples) and L1a (12) are thin but in band |
| S3 (unsampled bodies) | crank, rod and horn are sampled groups |
| S5 (static islands) | full flood drops 0 |
| M1 (virtual parts) | 0 passive translations |
| M2 (slim hubs) | O20 only |
| M3 (unchecked clash) | the verifier's RSSR closure, ball-link tilt and pressure-angle checks drop 0 poses. The O9 eye clash is NEW-catalogue-drive above |
| M4 (idle drive) | crank swings 31.6-33.2 deg |
| P2 (held-out leakage) | the polish picks were registered on envsel before the held-out claim, and none replaced the config |
| P3 / R3 (re-measuring until lucky; best of many without spread) | the number reproduced exactly 4 times. The polish reported all 3 picks and their spread |
| P4 (judge changed with the design) | no bench, judge or metric file in the row's 4 commits. The R17 coupling change is a judge change for slaved designs, but it has not touched this row's number |
| R2 / R4 (refuted records shown; recomputed number) | the dashboard shows the verifier's v_gap 18.91 (fixed in 448f6af) |
| G2 (stiff spring) | K preload 0.08 N.m, J2 step 0.13-0.20 N.m. Small, pending R17 |
| G3 (cuff twist) | not measured (R17 pending), listed under M5 |
| G5 / G6 (complexity hidden; 4th joint) | 49 recomputed. 3 active joints; K is slaved, not sensed |

## Proposals (not applied; each is a measurement or reporting change for the lead or the user)

- **P-a. Proposed catalogue entry "M6. A modelled component envelope smaller than the catalogue part".**
  - Looks like: a joint maps to a real part number, but the model samples a smaller envelope (here an O7 eye for an
    O9 x 4 igubal).
  - Detect: the CAD red team's part table against the model's sampled radii, then a capped or enlarged re-wear
    (`tools/alignment_drive_cap_wear.py`).
  - Here: this design, +0.85.
  - Effect on the verified rows: sidecar-longdyad 18.91 -> 19.76. Not measured for sidecar-parallelogram or
    roller-flank, which may carry the same M2 eyes; their drives were not red-teamed with KBRM-02.
- **P-b. Proposed catalogue entry "R5. Readings priced differently on one leaderboard".** Rank a verified number
  against another only when both carry the same build-tolerance pricing.
  - Measured effect: sidecar-longdyad 18.91 -> 19.36 (priced), and minarc pick1 / BDp unchanged (already priced).
  - Not measured: sidecar-parallelogram and roller-flank priced.
- **P-c. A held-out non-regression term for the A1 dominance gate.** A challenger replaces the lead only if it beats
  the lead on the plain gap and at 2 mm, and is not worse held out by more than 0.5.
  - Effect on past decisions: longdyad over frontload (held 22.67 against 26.75) still passes.
  - It would hold back the round-9 roller-longdyad claim if its verifier confirms the claim: 18.67 / 33.10 beats the lead
    on plain and at 2 mm, but its held out is 23.73 against 22.67 and its 1 mm reading 20.30 against 20.00 (the claim's
    own numbers, `docs/alignment/remeasure/roller-longdyad-knuckle-3r_*.json` are that design's audit).
  - Against the buildable lead (19.76 / 34.39 / held 23.53) roller-longdyad would pass, if its own drive is buildable
    as modelled.

## What happens next

1. **Gen-6 CAD** (wf_fe302450-e0e) should judge the horn eye against hub K's real dome, and the crank-tip eye against
   hub 2, at 1 mm.
2. **The re-wear that settles the drive.** If the custom O7 crank-tip eye passes those checks, 18.91 stands for the
   build. If not, 19.76 is the build's number. This audit's adapter re-wears either in about 3 min on the farm.
3. **R17 with the slaved entry** on l1_sidecar-longdyad: lift-off and cuff twist.
4. **Re-audit the lead** when any of these land, or when roller-longdyad's verifier reports.

Cost of this audit on the farm: about $0.07 (6 jobs).
