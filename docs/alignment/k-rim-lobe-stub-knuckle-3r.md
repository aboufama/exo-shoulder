# Alignment audit: k-rim-lobe-stub-knuckle-3r (verified, round 7 pick 2)

Hourly audit of 2026-10-19, 02:46-03:13 UTC. Ledger entry 2026-10-19T03:11:19Z (`by auditor`, run
`audit:k-rim-lobe-stub-knuckle-3r`, git 6d558f1).

- **Why it was due:** commit ec77d25 (simplicity v2.1, 2026-10-17 04:55) touched the row after the last ledger entry
  (skeptic, 2026-10-16 20:55, watch). That commit changed one field: `complexity` 34.0 -> 4.0.
- **What did not change:** the claim. Nothing in the model's import chain has changed since the verification
  (2026-10-16 16:42): the model (15:48), the geneva module (13:51), the minarc kit-rule module (10:10), the verifier
  (16:42), the pin-knee polish held bench (06:18), the minarc mechanism flood (09:23), `tools/concept_bench.py` (04:07)
  and `tools/concept_kit.py` (06:05).
- **Instrument note (tools/alignment_audit.py 2026-10-19.1, 702373b):** the type guard changes T5 only for readings
  from `*_paired*.json` files. This design is in no paired file, so T5 reads the same under 2026-10-19.1 as it did before
  702373b: before this audit, "no per-pose contact depths on file". After this audit T5 reads the new wear-probe
  files. That change comes from new data, not from the instrument.
- **What this audit touched:** no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and no score. It added
  one tool, `tools/alignment_wear_probe_krim.py`. That adapter wears the claim through the verifier's own harness
  (`docs/concepts/verify/k-rim-lobe-stub-knuckle-3r.py` frozen_wear(CorrModel, ...), unchanged) and wraps the
  pin-knee audit to record more. It was needed because `alignment_audit.py remeasure` would wear `mod.frozen()` =
  KB.frozen, whose attribute copy list predates the stub, and the model has no `frozen_held()`.
- **Compute:** local only (nice, OMP_NUM_THREADS=1, at most 2 processes) on a box at load 23-31 from other agents. No
  farm was used, because the CPU budget line is spent. Cost $0.

## Verdict: WATCH (ledger)

- **Claim:** verified v_gap **44.79** (score 83.71), frozen exact Bench(110,360). This audit's re-wear reproduces it to
  the digit (`remeasure/k-rim-lobe-stub-knuckle-3r_bench.json`).
- **Held out (new):** **51.47** (score 81.28), +6.68 over the bench claim. The fit bench is unchanged (30.79), and the
  frozen shape is worn on the 1154-pose held-out set (`remeasure/k-rim-lobe-stub-knuckle-3r_held.json`). That is over
  the tool's 6-point watch line and under its 10-point gamed line. The lead loses +4.10 on the same protocol
  (18.28 -> 22.38).
- **Rank:** 36th of 37 verified rows and 31st of 32 verified 3-active rows on the plain gap. It sits 26.51 points
  behind the 3-joint lead conecut-knee-knuckle-3r (18.28). Nobody calls it a contender, and its own record says so.
- **Complexity:** the row says 4.0. A schema-correct count gives **14.25** (finding G5).
- **Ledger reasons:** 10, all watch.
  - From the tool (4): `held_out` (+6.68), `fold_margin` (not on file in the files the tool reads), `sampling`,
    `reporting`.
  - From this judgement pass (6): G5, M2, R1, NEW-ff-mixed-metric, G1, M5.
  - Changes since the last entry (skeptic 2026-10-16, watch): `complexity` left the list because the row now equals
    the counter, which is finding G5. `held_out` changed from 'never worn off its bench' to a measured +6.68.
- **Why none is gamed:** no finding shows the number ranking this design above one that is better for the wearer
  under the same harness, and no hard rule is broken:
  - The fold margin in th holds: 7.64 deg minimum on the bench, with no taken pose under 5 (held out 5.59 deg, 0 under 5, 3 under 6).
  - It has 3 active DOF, 0 passive translations and O20 hubs.
  - K is slaved by the roller-lobe pair, not read or free, and it moves (24.47 deg).
  - The full continuity flood keeps every taken pose, bench (131 of 131 law poses) and held out (0 dropped).
  - The understated complexity does not move it past a better design on the score, the only ranking in force below
    score 95.

## What the wearer gets (measured)

| item | bench (Bench(110,360) exact) | held out | file (docs/alignment/remeasure/ unless stated) |
|---|---|---|---|
| plain gap / score | 44.79 / 83.71 | 51.47 / 81.28 | `k-rim-lobe-stub-knuckle-3r_bench.json`, `_held.json` |
| reach / follow / in-band14 / contact | 0.6222 / 0.8727 / 0.8256 / 0.0184 | 0.5893 / 0.8515 / 0.8211 / 0.0266 | same |
| overhead reach (elev >= 140), taken / total | 5 / 28 (0.179) | 12 / 71 (0.169) | `_probe_bench.json` ws_overhead140, `_probe_held.json` |
| why overhead poses are lost | fold 17, contact 3, slide 2, parts 1 | fold 41, slide 9, contact 7, parts 2 | `ws_overhead_why_not` |
| raised-arm reach (elev >= 90) | 31 / 113 (0.274): 90-120 18/51, 120-140 8/34, 140-160 3/13, 160+ 2/15 | 87 / 300 (0.290): 90-120 54/140, 120-140 21/89, 140-160 9/35, 160+ 3/36 | `ws_reach_by_elev` |
| taken poses with metal < 2 mm | 35 of 320 (10 < 1 mm, min 0.45 mm at (15, 90, 30)); 157 < 3 mm | 79 of 733 (28 < 1 mm, min 0.05 mm); 343 < 3 mm; near-touch 61.52 (1 mm), 77.81 (2 mm) | `_bench.json` deep |
| overhead floor | 3 of the 5 taken overhead workspace poses < 2 mm (1 < 1 mm); **6 of the 8 taken overhead clip frames < 1 mm** (0.53 mm at (30, 150, -60)) | **11 of the 12 taken overhead workspace poses < 2 mm** (6 < 1 mm); 11 of the 18 taken overhead clip frames < 1 mm | `ws_overhead140`, `clip_overhead140` |
| contact (penetration) | 6 workspace poses, sum 15.38 mm, 1 deeper than 3 mm; deepest **4.57 mm at (30, 165, -60), overhead**; then 2.75 (60, 150, -45), 2.53 (-60, 60, 105), 2.21 (45, 150, -45), 1.74, 1.58 | 20 workspace poses, sum 56.10 mm, 8 deeper than 3 mm, 7 overhead; deepest **6.97 mm at (60, 165, -30)**; 6.57 (-90, 60, 105), 6.29 (60, 120, -30), 5.65 (60, 165, -45) | `_probe_bench.json` contact_poses |
| contact vs the lead (T5) | conecut-knee 4 poses, sum 20.24 mm, deepest 8.93 mm: this design presses less in total | conecut-knee 14 poses, sum 60.97 mm, deepest 9.86 mm: x0.92, less in total, but 20 presses against 14 | tools/alignment_audit.py contact_depth |
| workspace in-band 2-14 (unscored) | 0.797 over taken workspace poses (20.1 % of samples over 14 mm, 6.2 % over 20 mm, max 35.07 mm); elev 90-140 0.737; overhead 0.860 | 0.799 (19.9 % over 14 mm, 6.1 % over 20 mm, max 36.67 mm); elev 90-140 0.779; overhead 0.831 | `ws_unscored`, `ws_elev90_140`, `ws_overhead140` |
| scored in-band 2-14 / band read 3-14 | 0.8256 / 0.8206 (gap 45.29 with the band at 3-14) | | `_bench.json` deep |
| out-of-band metal | the drive: lobe 0.00 in band (median 19.6 mm), stub strap LT 0.12 (21.4 mm), roller 0.18 (19.7 mm); 86 of 869 samples (9.9 %); hub 3 0.675, L2 0.776 | | verify `_corr_bench_frozen.json` parts_ib14 |
| fold margin in th (m3e) | min 7.64 deg (state A 7.64, law 8.17), 0 < 5, 0 < 6, 18 < 10; sub-dyad msub min 8.80 | min 5.59 deg (state A 5.59, law 8.18), 0 < 5, 3 < 6, 46 < 10; msub min 8.82 | `_probe_bench.json` fold_margin |
| K (the slaved spare) | on stop A for 138 taken poses, on the law for 182, up to 24.47 deg; closure residual max 0.015 deg | stop A 320, law 413 taken, up to 24.45 deg | `_probe_bench.json` k_slave, `_bench.json` coord_spans |
| roller-lobe transmission | pressure angle max 35.3 deg (gate 45), convex pitch radius >= rr + 1, undercut -0.001 mm | | row note, verify drive |
| knee window | [27.85, 152.15]; taken 80.10-148.67 deg (3.48 deg spare) | taken 80.10-149.02 deg (3.13 deg spare) | `_bench.json` coord_spans K.ang |
| part-part clearance | min 1.03 mm over taken poses (rule >= 1 mm non-adjacent) | | `_bench.json` min_clear_taken |
| knee hardware | stk 4.8534 mm, below the iglidur 5.0 and the MR63ZZ 6.0 | stk 6.0 (MR63ZZ pair), everything else unchanged: bench **44.94 (+0.15)**; in-band14 0.8241, in-band10 0.5526; reach, follow, contact and every why-count unchanged; 1 mm 53.67, 2 mm 71.85; held out 51.63 (+0.16), in-band14 0.8195 | `_stk6_bench.json` |
| springs / cuff twist | one clock spring (6 mm cap) holds K and closes the pair; no preload on file; R17 never run (no CAD) | | finding M5 |

For the wearer, this is the round-6 winner's chain with a cam-slaved K. The drive itself is honest:
- K moves 24.5 deg along a law whose closure error is 0.015 deg.
- The pressure angle stays at or under 35.3 deg, and the roller never cuts into the lobe.

It is not a better exo than the lead, though, and nothing claims it is:
- It reaches 5 of 28 overhead poses, against the lead's 8 on the same bench, and 31 of 113 raised-arm poses against
  the lead's 47 (`remeasure/conecut-knee-knuckle-3r_probe_bench.json`).
- The drive puts a 19-22 mm bump of lobe, stub and roller over link 1b at K.
- Most taken overhead clip frames carry metal under 1 mm from the arm.

## Findings (judgement pass)

Each finding is in `docs/alignment/k-rim-lobe-stub-knuckle-3r.findings.json` with its full measured reason. All are
watch.

1. **G5: complexity hidden by the count (the row's 4.0 is a parse artefact).**
   - Evidence: the row's mechanism record uses a schema `tools/simplicity.py` cannot read. `joints` is a list of 7
     joint dicts, and there is no `moving_bodies`, `passive_rot`, `springs_or_flexures` or `custom_parts` field. So the
     counter keeps one item, "1 closed loop x 4", and flags the record itself (topology flag, Kutzbach M -6).
   - The same mechanism in the counter's schema scores **14.25** under v2.2: K plus 2 knee pins, 6 bodies, 7 joints, 2
     loops with the knee's free loop, 1 clock spring, 14 made and 19 bought parts with the knee; the cuff knee scores 0.
   - geneva-tail-knuckle-3r, the same topology without the knee (a roller on a link-2 tail pushes a lug on link 1a, K on
     a clock spring), is counted 14.0.
   - ec77d25 set the row from 34.0 to the parse result 4.0. That turned the tool's complexity check from MISMATCH to
     "ok", and the dashboard now shows 4.0 with one item.
   - Why the exo is not simpler: K, its clock spring, the roller and the lobe-stub pair are real parts the wearer
     carries and the user would build. 4.0 would rank this design simpler than the lead (18.5) and than the rod drive's
     family (14-25.5).
   - Not gamed: complexity is not in the score, and below score 95 it ranks nothing.
   - Action (lead): rewrite the mechanism record in the counter's schema. Proposal 1 makes the check catch this.
2. **M2: knee pins below any real component.**
   - Evidence: stk 4.8534 mm, from the round-6 winner's seats (model line 56). The kit's own figures are 5.0 for an
     iglidur pin and 6.0 for an MR63ZZ pair, and the lead's 2026-10-17 build rule requires MR63ZZ pairs. The row still
     lists the knee as "iglidur pin, sensed".
   - Measured AS BUILT (stk 6.0 only, the same harness): bench **44.94 (+0.15)**, held out **51.63 (+0.16)**; in-band14 0.8241 / 0.8195; reach, follow, contact and every why-count unchanged.
   - Why not better: the claimed knee is 0.15-1.15 mm thinner than any hardware the build may use. The cost is small and
     the claim's ranking does not change.
   - Action: re-state the claim at stk 6.0.
3. **R1: stale records on a verified row.**
   - The verdict text (row and dashboard) still reads "SCREENED, FAILS ITS KILL GATE ... no frozen / verify run spent".
   - The row's `gap` 36.82 is the fast near-touch number. The dashboard's `gap` is the fast plain 30.79.
   - n_configs is 524 on the row and 512 on the dashboard.
   - The mechanism note says "complexity 34.0, not recomputed" next to complexity 4.0.
   - The knee is recorded as sensed iglidur pins, against user decisions 5 and 6.
   - The verified 44.79 itself is displayed correctly.
   - Action (lead): refresh the verdict and the mechanism record.
4. **NEW-ff-mixed-metric: the fast-to-frozen check compares a near-touch number with a plain one.**
   - The tool's `fast_frozen` reads +7.97 (36.82 -> 44.79). Like for like, the loss is **+14.00 plain** (30.79 -> 44.79)
     and **+16.69 near-touch** (36.82 -> 53.51). The near-touch loss is over the check's own 14-point watch line; the
     round-6 winner loses 6.8.
   - Cause: follow 0.933 -> 0.873. ROL-LOBE part losses go from 9 on the fit bench to 32 on Bench(110,360): in state A
     the stub swings back across the lobe on clip frames the fit bench did not sample.
   - Why it matters: the self-measured 36.82 (score 86.61) on the sweep line is a number the design does not hold. The
     verified number is honest.
   - Proposed catalogue entry: **R5. A like-for-unlike drop.** A self-measured near-touch gap is compared with a plain
     verified gap (or the reverse), which hides the fast-to-frozen loss. Detect: compare `gap_plain` with v_gap and the
     near-touch gap with `v_gap_near1`. Proposal 2.
5. **G1: metal hugging at 1-3 mm, overhead most of all** (report only: near-touch is not a gate, user 2026-10-17).
   - Bench: 35 of 320 taken poses < 2 mm, 10 < 1 mm, min 0.45 mm; 157 < 3 mm.
   - Overhead on the bench: 6 of the 8 taken overhead clip frames are < 1 mm.
   - Held out: 79 of 733 taken poses < 2 mm, 28 < 1 mm, min 0.05 mm. 11 of the 12 taken overhead workspace poses are
     < 2 mm.
   - Why not better: the few overhead poses it does reach have metal on a bulging arm.
6. **M5: one clock spring holds K and closes the cam, and nothing measures it.**
   - K sits on stop A for 138 of the taken bench poses (320 held out) and follows the law for 182 (413 held out), up to
     24.47 deg.
   - No preload is on file, no torque check against K's load in every posture, and no R17 / cuff twist. There is no
     CAD, so `judge/dynamics.py` never ran.
   - Why it matters: a spring-closed cam that lifts off lets K lag, and link 1b and everything distal leave their
     planned pose. pick1's 0.08 N.m K lagged 9.28 deg.
   - Action: only if the design is ever built.

The tool's own non-ok checks (`held_out` +6.68, `fold_margin` not on file, `sampling` lobe / LT / roller out of band
and the roller thin, `reporting`) are in the ledger as they stand. This audit measured the fold margin (bench 7.64,
held out 5.59: no breach), but the tool cannot read it there (proposal 3), so that watch stays as the tool computes
it.

## Patterns walked and not present

- **T3 fold margin on another angle:** the margin read in th (m3e, the kit's reading) is 7.64 deg minimum on the
  bench and 5.59 deg held out (0 poses under 5, 3 under 6, all in state A where K sits on stop A). The J2 stops act on the J2 / K angles of adjacent bodies (stop A, stop B, folded dowel). Not
  present. The tool's `fold_margin` watch is only "not on file": this audit puts the reading on file in
  `_probe_bench.json` / `_probe_held.json`, but the tool reads fold margins only from the row and the verifier files, never from
  `docs/alignment/remeasure/`. See proposal 3.
- **T4 search bound walking to a singular posture:** a1max (stop B) sits at the LHS lower bound 48.0. All of the top
  20 of 512 configs lie at 48.0-48.47. But that bound is the safe direction: a lower stop B keeps the K sub-dyad
  farther from its stretched fold at bk1 + bk2 = 73.1 deg (msub min 8.80 deg). The knee's ang_min 27.85 is the
  round-6 winner's seat and was not searched. Not present. Lowering the bound might gain a little, which would make
  the claim conservative, not optimistic.
- **T5 depth-blind contact:** measured for the first time (this audit's probes, both reproducing their claim). Bench: 6 presses summing 15.38 mm, deepest 4.57 mm overhead. Held out: 20 presses summing 56.10 mm, deepest 6.97 mm. Against the lead (20.24 / 60.97 mm) that is x0.76 and x0.92: not deeper (tool `contact_depth` ok). The deepest presses are at elev 150-165 with plane 45-60 and axial -30 to -60, plus a lateral cluster at plane -60 to -90, elev 60, axial 90-105. Not present as gaming, but 8 held-out presses deeper than 3 mm are metal a liner does not absorb.
- **S1 skewed sample / P1 in-sample tuning:** held out 51.47 vs bench 44.79 (+6.68, tool `held_out` watch). The loss is fold (311 of 1154 lost, 27 %), parts 65 (ROL-LOBE in state A), slide 25 and contact 20. In-band barely moves (0.8256 -> 0.8211), while reach 0.622 -> 0.589 and follow 0.873 -> 0.852 drop. The search never saw the held set (P2 below), so this is the sample's under-coverage of axial rotation (the known S1 cause), not leakage. It stays under the gamed line and is already carried by the tool's watch.
- **S3 unsampled bodies:** the lobe, the stub strap LT, the roller and its boss are all sampled and skin-checked
  (14 metal groups, every declared body). The roller is thin, with 9 samples (tool `sampling`). Not present beyond
  the tool's watch.
- **S5 static islands:** connected_full = static (131 of 131 law poses connected, 0 dropped). The knn flood loses
  1.69 (46.48). The bench-graph flood is 81.25, but that is a sparsity artefact of the 470-pose graph (127 dropped,
  24 with no taken neighbour), and the rule's flood is the full one. Held out the full flood also drops 0 (51.47).
  The knn flood there drops 98 poses (62.16), against 6 on the bench: the held set's denser pose graph exposes more
  thin bridges. That is a reading for the lead, not a rule breach. Not present.
- **M1 / M2 slim parts:** O20 hubs everywhere, MR52ZZ roller at O5 x 2.5 (+0.5 shim), boss O6. The knee stack is the
  exception: finding M2.
- **M3 unchecked clashes:** the claim checks the lobe against hub 2, hub 3, L1b, L2, LT, knee, pad and E, and the
  stub and roller against hub 1, hub K with its cap, hub 3, L1a, L1b, knee, pad and E. The verifier added lobe vs
  hub 1, and roller vs lobe inside the law. The lobe rides on K's housing (link 1a), so lobe vs hub K is the same
  body. Nothing unchecked was found.
- **M4 idle mechanism:** K spans 24.47 deg over the taken poses. The tool's "crank: declared moving, no span" is a
  name match with no crank in this design. Not present.
- **P2 held-out leakage:** the model and the sweep never import a held bench (the search ran on Bench(60,160) fast, the
  claim on Bench(110,360) frozen). Not present.
- **P3 re-measuring until lucky:** one verification wear, reproduced here to the digit. The top-5 spread of the 512
  sweep configs is 36.82-37.20. Not present.
- **P4 judge changed with the design:** no bench, judge or metric file was in the 3 commits that touched the row (tool
  `judge_change` ok).
- **R2 refuted records shown / R4 recomputed numbers:** the dashboard v_gap 44.79 equals the verified number, and
  v_contact 0.0184 is on the row. Not present.
- **G4 singular postures:** th margin >= 7.64, msub >= 8.80, knee 3.48 deg inside its window, pressure angle <= 35.3.
  Not present on the bench (held out the th margin falls to 5.59, still above the user's 5 deg, and the knee keeps 3.13 deg of spare).
- **G6 4th joint vs 3 active:** K is a 4th revolute in the shoulder chain, but it is cam-slaved with no free
  coordinate, unlike pick1's sensed, spring-held K. The DOF count of 3 stands (CLAUDE.md decision 1 covers sensed
  joints). Its cost is complexity, finding G5.

## Proposals (not applied; each is a measurement or reporting change for the lead / the user)

1. **Make the complexity check parse-aware.** `tools/alignment_audit.py` `complexity` should give watch when
   `tools/simplicity.py` flags the record (a topology flag, or a list-typed `joints`) or when no `moving_bodies` /
   `passive_rot` field exists. Today it compares the counter with a row that was set from the counter, so a parse
   failure reads "ok".
   - Measured effect on the verified rows: 2 rows change from ok to watch, k-rim-lobe-stub (4.0, honest ~14.25) and
     geneva-tail-knuckle-pinknee-3r (12.0, the same list schema and topology flag).
   - conecut-h2facet / conecut-l2jog (no mechanism fields, row 18.5) and lowarm-kphase (no complexity) would need a
     look of their own.
   - It moves no score.
2. **Read fast_frozen like for like.** Compare `gap_plain` with v_gap, and the near-touch fast gap with `v_gap_near1`,
   when the row's `gap` is a near-touch number. On this row the check moves from +7.97 (ok) to +14.00 plain / +16.69
   near-touch (watch). The effect on the other rows is not measured in this audit.
3. **Read the fold margin from the auditor's own re-wears.** The geneva and k-rim adapters write
   `fold_margin.th_margin_min` into `remeasure/<id>_probe_<wear>.json`, but `c_fold_margin` reads only the row and the
   verifier files.
   That would clear the `fold_margin` watch on this row: 7.64 bench, 5.59 held.
4. **Re-state the row (for the lead, not done here):** complexity 14.25 with a schema-correct mechanism record; the
   verdict text as verified; the knee pins as unsensed MR63ZZ pairs at stk 6.0 (bench 44.94, +0.15; held out 51.63, +0.16 at stk 6.0).

## What happens next

- The design is a closed branch: 26.5 points behind the lead, and the drive's out-of-band metal is structural (three
  layers at K).
- No action is needed on the claim.
- The two instrument proposals (1, 2) apply to every row and are the useful output.
- The lead's G5 re-count should be done for geneva-tail-knuckle-pinknee-3r too, the same schema.

## Skeptic (2026-10-19, 03:50-04:10 UTC)

Ledger entry 2026-10-19T04:05:12Z (`by skeptic`, run `skeptic:k-rim-lobe-stub-knuckle-3r`). Rulings are in
`docs/alignment/k-rim-lobe-stub-knuckle-3r.rulings.json`. This file replaces the 2026-10-16 rulings file, whose one
refuted key (`near_touch`) has read ok since tool 2026-10-17.2.

- **Method:** I re-derived every number from the auditor's re-wear files (`docs/alignment/remeasure/k-rim-lobe-stub-knuckle-3r_{bench,held,probe_bench,probe_held,stk6_bench,stk6_held}.json`), the row, the dashboard, `tools/simplicity.py` (re-run) and the model / verifier source.
- **Instrument check:** I loaded `tools/alignment_audit.py` at 702373b^ and at HEAD and ran `_depth_sources` on both versions (missed item 1).
- **What I did not do:** no new wear (the files reproduce the claim to the digit, 44.79 / 51.47). Local only, $0. Nothing edited except this section, the rulings file and the ledger line.

### Rulings

| key | ruling | evidence |
|---|---|---|
| held_out | upheld | 51.47 re-derived from `_held.json` frozen (7.89 + 9.85 + 31.07 + 2.66). +6.68 > TH held_watch 6.0 (< 10). Same harness as the lead: the verifier's frozen_wear with `held_bench()` = every pose in neither bench. The lead reads +4.10 on that set. Reach 0.622 -> 0.589 and follow 0.873 -> 0.852 are real losses for the wearer. |
| fold_margin | **refuted** | On file: `_probe_bench.json` fold_margin.th_margin_min 7.638, lt5 0; `_probe_held.json` 5.585, lt5 0 (3 < 6). The adapter reads the model's own `_m3e` = `dyad_margin(th, a1e, a2)`, the kit's th reading on the effective dyad (geneva-pinknee line 198, inherited unchanged). The model gates every pose on m3e >= 5 (line 200, PARAMS m3e 1). The watch is a reading-path gap (proposal 3), not a missing measurement. |
| sampling | upheld | `parts_ib14`: 0.8257 sample-weighted vs 0.7531 part-weighted (+7.25, between 3 and 8). lobe 0.00 / LT 0.12 / roller 0.18 in band at 19-22 mm, roller 9 samples. Without the 86 drive samples in-band is 0.9095: the out-of-band metal is the drive bump. Density not measured. |
| reporting | upheld | Row verdict opens "SCREENED, FAILS ITS KILL GATE" on a verified row; dashboard sweep_gap 36.82 vs v_gap 44.79 (7.97 > 5). |
| G5 | upheld | `simplicity.py` re-run gives 4.0, one item, a topology flag, Kutzbach -6, `joints` a list of 7 dicts. geneva-tail-knuckle-3r, the same drive, counts 14.0. The auditor's 14.25 record is not on file, so I did not re-derive it. |
| M2 | upheld | stk 4.8534 (model W, line 56), below 5.0 / 6.0 (pin-knee lines 19 / 54). At stk 6.0: 44.94 / 51.63 (`_stk6_*.json`). |
| R1 | upheld | Every field confirmed: verdict text, gap 36.82 vs 30.79, n_configs 524 vs 512, the "34.0 not recomputed" note, the knee recorded as sensed iglidur pins. |
| NEW-ff-mixed-metric | upheld | Row gap 36.82 = fit_fast.gap_near1. Plain like for like: 14.00, exactly at the 14.0 line, not over it. Near-touch like for like: 16.69 > 14, and the row's headline is the near-touch number. Cause: ROL-LOBE 9 -> 32, follow 0.933 -> 0.873. Correction: the round-6 winner's row reads 16.53 -> 23.57 = 7.04, not 6.8. |
| G1 | upheld | Counts reproduced: bench 10 / 35 of 320 taken poses < 1 / 2 mm, min 0.452 mm; held 28 / 79 of 733, min 0.053 mm; overhead clip frames < 1 mm on 6 of 8. The lead on the same probes: 3 / 33 of 372, overhead clip frames < 1 mm on 0 of 10 (bench) and 0 of 19 (held), 1 mm near-touch cost +1.64 against this design's +8.72. Level question for the lead: near_touch is report-only (2026-10-17.2), and the band read 3-14 costs only +0.50. |
| M5 | upheld | No preload, torque, R17 or dynamics on file (row, concept doc, verifier). kK is the law ratio, not a spring rate. No CAD for this id. |

### Missed (for the next audit; no effect on this verdict)

1. **The audit's T5 instrument note is wrong on the reference side.**
   - Measured: under 2026-10-18.1 (702373b^), `_depth_sources('conecut-knee-knuckle-3r')` raises AttributeError ('str' object has no attribute 'get', the desmo-geom paired file's `held: "missing dump"`). Under 2026-10-19.1 it returns the lead's per-pose dumps (bench 20.24 mm, held 60.97 mm).
   - This design's own depth sources (`_probe_bench/held.json`: 15.38 / 56.10 mm) read the same under both versions.
   - So T5 does read differently now. Before 702373b this design's contact_depth would have had no reference, which makes it vacuous. Now it compares x0.76 / x0.92 against the lead.
   - The note "T5 reads the same under 2026-10-19.1 ... the change comes from new data, not from the instrument" holds for the design's side only. The level is ok either way.
2. **The near-touch hugging is specific to this design, and the audit did not compare it with the lead.**
   - Taken poses under 1 mm: 3.1 % on the bench (10 / 320) against the lead's 0.8 % (3 / 372); 3.8 % held out (28 / 733) against 1.5 % (13 / 861).
   - Taken overhead clip frames under 1 mm: 6 / 8 against 0 / 10 on the bench, 11 / 18 against 0 / 19 held out.
   - Taken held overhead workspace poses under 1 mm: 6 / 12 against 1 / 18.
   - The 1 mm near-touch costs +8.72 here and +1.64 on the lead, so a larger share of this design's reach sits on sub-millimetre poses.
   - Sources: `remeasure/conecut-knee-knuckle-3r_{bench,held}.json` deep and `_probe_{bench,held}.json`.
3. **The held knn flood loses more than the family figure.**
   - It loses 10.69 points (51.47 -> 62.16, 98 dropped). docs/FINDINGS.md line 3816 gives the family as ~8.0-8.24.
   - The full flood, the reading in force, drops 0, so there is no breach. The number belongs to the open flood question (ALIGNMENT.md item 8).
4. **The selftest will catch the fold_margin ruling.**
   - With `fold_margin` refuted here, `tools/alignment_audit.py selftest` expects that check to read ok on this row. It cannot until `c_fold_margin` reads the remeasure probe files (proposal 3), the same situation as fold-sph3r.
   - This is the tool's reading path. The design is not affected.

### Final verdict (ledger): WATCH

1 of 10 reasons refuted (`fold_margin`). The other 9 stand at watch.
