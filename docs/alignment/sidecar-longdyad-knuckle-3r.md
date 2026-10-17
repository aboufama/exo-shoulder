# Alignment audit: sidecar-longdyad-knuckle-3r (verified, round-8 lead, reference for round 9)

Audit of 2026-10-17 ~01:45-02:00 UTC, in the fresh session after the old one hit its usage limit. Ledger entry
2026-10-17T01:56:50Z (`by auditor`, run `audit:sidecar-longdyad-knuckle-3r`). It edited no bench, judge, kit, model,
row, dashboard or CLAUDE.md, and wrote no new tool. The earlier audit (2026-10-16 22:45 UTC, commit 67e8480) is
superseded by this one; its measurements are reused where the claim has not moved.

## Verdict: WATCH (ledger)

- **Claim:** verified v_gap **18.91**, score 93.12, frozen exact Bench(110,360), fit Bench(60,160); held out 22.67.
- **Ledger reasons** (all watch): two from the tool (near_touch, reporting) and seven from the judgement pass (S1,
  NEW-sensed-knee-pins, NEW-catalogue-drive, NEW-unpriced-stops, G1, M5, R1). None is gamed.
- **No re-wear this time, by the rule.** The row's last commit is b3d426a (2026-10-16 22:03 UTC); the re-wears in
  `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_*.json` were committed at 22:52 UTC and reproduced 18.91 /
  held 22.67 to the digit. `git diff 63167c0 HEAD` (the verification commit to now) shows no change to
  `tools/concept_bench.py`, `tools/concept_kit.py`, `tools/env_bench.py`, `pipeline/avg/body_pose.py`,
  `data/raw/split.json`, this model or its parent model. Only `judge/dynamics.py` changed (R17's slaved coupling), and
  R17 is not in the gap. So the number on file is the number the current bench gives.
- **What changed since the last audit is the rules, not the design.** The user retired the 2 mm dominance gate (A1) and
  ruled that a sensed joint is a joint (CLAUDE.md "User decisions 2026-10-17"). This audit re-reads every finding under
  those rules. No ledger reason of this design now cites A1 or 2 mm as a gate.

## The lead question (round 9): is roller-longdyad's 0.24 real?

Seen from this design's side, under the same harness (exact, 371 bench poses fit / 1154 held-out poses):

| design | plain | held out | held 1 mm | reach (bench) | in-band14 | contact poses | cx |
|---|---|---|---|---|---|---|---|
| roller-longdyad-knuckle-3r | **18.67** | 23.73 | 26.83 | 0.725 (261) | 0.8937 | 2 (deepest -10.55 mm) | 43.75 |
| sidecar-longdyad-knuckle-3r (this) | 18.91 | 22.67 | 25.75 | 0.725 (261) | 0.8966 | 4 (deepest -4.61 mm) | 49 |
| sidecar-parallelogram-knuckle-3r | 19.13 | **22.03** | **24.44** | 0.7194 (259) | 0.9049 | 4 | 49 |

Sources: rows (`v_gap`, `v_reach`, `v_inband14`, `held_out`); `docs/concepts/verify/*_v_held_frozen.json` (all three
n 1154, exact); `docs/alignment/roller-longdyad-knuckle-3r.md`; this design's `remeasure/..._probe.json`.

- **Not a bench artefact.** Both designs were verified on the same bench code (no measurement file changed between
  the two verifications, see above).
- **But not a better exo either.** One workspace pose is worth 0.278 gap points. The plain differences among the top
  three are 0.24 and 0.22, each under one pose, and held out reverses the whole order (22.03 < 22.67 < 23.73).
  Roller-longdyad's gain is 2 fewer contact poses, with the remaining contact 2.3x deeper.
- **The concurrent roller-longdyad audit's paired re-wear agrees** (`remeasure/roller-longdyad-knuckle-3r_vs_
  sidecar-longdyad-knuckle-3r_paired_exactfit.json`; an exact-fit variant, so its levels are 19.34 / 19.66, not the
  verified 18.67 / 18.91): on the bench each design takes 8 workspace poses the other does not, the difference is all
  contact (-0.53) against in-band (+0.21), and the paired bootstrap 90 % interval is [-2.62, +1.77]; pooled bench plus
  held out, roller-longdyad is better with probability 0.29.
- **This design's own lead was the same kind of number.** Its round-8 lead over sidecar-parallelogram is 0.22 plain
  (2 more workspace poses, less in-band), and it is 0.64 behind parallelogram held out (same reach 0.6901, in-band
  0.8947 vs 0.9031). That lead rested on the 2 mm column (34.03 vs 50.14), which the user has now retired.
- **Reading for the lead.** Under the user's rule (plain verified gap decides) roller-longdyad is the lead, and the
  rule is applied correctly. The three rows are a tie within one workspace pose; nothing in the bench number says one
  is better for the wearer than another. What does separate them for the wearer is outside the score: roller-longdyad
  is simpler (43.75) and keeps metal off the skin at 3 mm far better (133 vs 178 bench poses under 3 mm), but presses
  deeper where it touches; parallelogram generalises best but hugs at 1-2 mm; this design sits between.

## What the wearer gets (measured; files from the 2026-10-16 re-wears, unchanged claim)

| item | value | file |
|---|---|---|
| Overhead reach (elev >= 140), workspace | **8 / 28 taken** on the bench (lost: fold 14, slide 4, contact 2); 18 / 71 held out | `remeasure/..._bench.json` audit.overhead140; row held_out |
| Raised-arm reach by elevation (taken / total) | 0-60: 161/172; 60-90: 55/75; 90-120: 25/51; 120-140: 12/34; 140-160: 5/13; 160-200: **3/15** | `remeasure/..._probe.json` ws_reach_by_elev |
| Taken poses with metal < 2 mm | 26 of 371 bench, 63 of 859 held out. Overhead: 8 of 10 clip frames, 5 of 8 taken workspace poses | `_bench.json` / `_held.json` deep; `_probe.json` |
| Metal < 1 mm / < 3 mm | < 1 mm: 2 bench, 14 held out (min 0.28 / 0.14 mm). < 3 mm: 178 bench, 427 held out | same |
| Deepest contact | **-4.61 mm at plane 30 / elev 165 / axial -60** (overhead); then -0.77 (60, 150, -105), -0.74 (-60, 60, 105), -0.11 (15, 135, -60). Held out 10 contact poses. Which part presses: not measured | `_probe.json` contact_poses |
| Workspace in-band (unscored) | 2-14 mm 0.874 over 261 taken workspace poses; overhead 0.926; clips 0.897 | `_probe.json` ws_unscored |
| Fold margin (th) | min 5.232 deg over taken poses (no build tolerance on the stops) | row final_polish |
| Continuity | full flood 18.91 (0 dropped), knn 21.72 | `verify/..._v_bench_frozen.json` |
| Springs / stops | one K clock spring, 0.08 N.m preload; J2 stops smlo 5.0 / smhi 16.55; K stop B a1max 63.18 never binds | row best_params; red team |
| Cuff twist, K lag, lift-off | **not measured**: R17 with the slaved coupling has not run (no `judge/` under `pipeline/full-exo/designs/l1_sidecar-longdyad/`) | - |
| Near-singular postures | knee angle up to 146.1 deg bench (150.9 held out); crank swing 31.6-33.2 deg; transmission >= 30 gated | `_bench.json` coord_spans K.ang; verifier |
| DOF / complexity | 3 active (J1, J2, J3), K slaved and never read, 0 passive translations, pin knee with 2 sensed pins; complexity 49 (recomputed) | `docs/alignment/sidecar-longdyad-knuckle-3r.json` |

Numbers this audit could not get: cuff twist / K lag / lift-off (R17 not run on this design); which part makes each
contact (the probe records the pose, not the part; not re-run because the claim did not move and the local cache is
rebuilding); the priced-plus-catalogue-drive combined wear (never run).

## Findings

### S1 (watch): a sub-pose ranking that reverses held out

- **Evidence.** The table above. Plain margins 0.24 and 0.22 against 0.278 per pose; held out the order reverses
  (parallelogram 22.03, this design 22.67, roller-longdyad 23.73), and again at 1 mm held out (24.44 / 25.75 / 26.83).
- **Why the exo is not actually better.** Whichever of the three the plain gap puts first, the bench cannot tell them
  apart; the ranking is pose sampling. With A1 retired, nothing but sampling now separates this design from
  parallelogram.
- **Why watch.** No design that is clearly better for the wearer is ranked below this one: parallelogram wins held out
  but hugs at 1-2 mm (held-out 2 mm 48.71 vs 37.24).
- **Action.** Proposal P-1 below.

### NEW-sensed-knee-pins (watch): the knee's two encoder-read pins and the 2026-10-17 ruling

- **Evidence.** The mechanism record keeps the pin knee's 2 sensed pins as sensed passives outside the DOF count, as
  cuff-side self-aligning freedoms (CLAUDE.md, 2026-10-15). The user's 2026-10-17 ruling: "Sensed 4 joint does not count
  as passive obviously". ROUNDS.md round 6 already lists the asymmetry (sensed K counts active, sensed knee pins
  passive) as needing the user's say.
- **Measured effect if the knee pins counted as joints** (`tools/simplicity.py` on each record, sensed moved to
  active): every pin-knee row becomes 5 DOF, over the cap of 4, and complexity rises by 38. This design 49 -> 87,
  roller-longdyad 43.75 -> 81.75, parallelogram 49 -> 87, roller-flank 45.25 -> 83.25, frontload 49 -> 87. Only the
  kneeless rows (21.07 / 21.11, no sensed pins) would remain 3-joint designs within the cap.
- **Why watch, not gamed.** The cuff-side rule is an explicit user ruling and the 2026-10-17 quote names the
  shoulder-chain 4th joint. The order among the pin-knee rows does not change.
- **Action.** The lead should put the question to the user: do the two knee-pin encoders make the knee pins joints
  under the DOF cap? (A cuff IMU instead of the encoders is the alternative listed in round 6.)

### NEW-catalogue-drive (watch, still open)

- **Evidence.** With the catalogue M2 ball link (KBRM-02, O9 x 4) and the build spec's stop B at dK 35.4, the same
  harness gives 19.76 (score 92.81) / 1 mm 20.85, held out 23.53 / 26.63 (`remeasure/..._rh155cap354_*.json`). The
  gen-6 CAD still has no judge output, so the custom O7 crank-tip eye that would keep 18.91 is unjudged.
- **Why not better.** 0.85 of the number belongs to a part that has not been built or judged. On buildable readings
  roller-longdyad (envelope-corrected 18.56, ROUNDS round 9) is ahead by about 1.2, not 0.24.
- **Action.** Judge the gen-6 L1's crank-tip and horn eyes at 1 mm; then 18.91 or 19.76 is the build's number.

### NEW-unpriced-stops (watch)

- **Evidence.** smlo 5.0 and a1max 63.1774 = bk1 + bk2 - 5 exactly; min th margin 5.232; priced (+0.5 on the stops,
  CB_FOLD_MARGIN 5.5) 19.36 / held 23.29 (row final_polish.priced).
- **Change under the new rules.** minarc pick1 (priced) is now 4-active, so the "within 0.51" comparison is moot; the
  round-9 comparison with roller-longdyad (also smlo 5.0, unpriced) is like-for-like. The dashboard still mixes priced
  and unpriced verified numbers.
- **Action.** Show which verified numbers carry build-tolerance pricing (proposal P-b of the 22:45 audit, unchanged).

### G1 (watch): metal hugs the skin overhead (for the wearer, not a gate)

- **Evidence.** Overhead 8 of 10 clip frames and 5 of 8 taken workspace poses with metal < 2 mm; overhead p10 min
  metal 1.02 mm bench, 0.64 mm held out; 15.12 points in the 1-2 mm shell (11.49 held out).
- **Why not better.** On a real, bulging arm, 1-2 mm overhead is metal on skin. The user ruled 2 mm is not a gate, so
  this is reported for the wearer only.
- **Action.** Keep reporting the overhead floor; hub 3 (in-band 0.60) and L2 (0.75) are the out-of-band parts.

### M5 (watch): one spring holds the drive, R17 not run

- **Evidence.** K's 0.08 N.m clock spring keeps the whole drive train in compression; lift-off above ~30 rad/s2 of q2 is
  an estimate. No R17 output for this design.
- **Action.** Run R17 with the slaved entry on the gen-6 L1: K against its law, lift-off, cuff twist.

### R1 (watch): stale text

- **Evidence.** Row and dashboard verdict still open "SCREENED, a candidate for the verifier"; the dashboard row carries
  the fast 10.3 / reach 0.80 in its gap / reach fields; HANDOFF line 81 "no polish, no CAD", line 97 "within 0.51" of
  minarc pick1.
- **Action.** Refresh at the next dashboard / HANDOFF update.

## Patterns checked and clean

| pattern | result |
|---|---|
| T1 / T2 | contact line held at 1 mm; band read 3-14 mm costs 0.31 bench / 0.33 held out |
| T3 | th margin 5.232 on file in the one metric |
| T4 | a1max at its clamp, but stop B never binds (row limiter); polish kept ang_min at 26.88 |
| S2 / S3 | part-weighted in-band 0.923 >= sample-weighted 0.897; crank, rod and horn sampled (rod 13, L1a 12 samples, both in band) |
| S5 | full flood 0 dropped |
| M1 / M2 / M3 / M4 | 0 passive translations; O20 hubs; RSSR closure, ball-link tilt, pressure angle drop 0 poses; crank swings 31.6-33.2 deg |
| P1 (in-sample) / P2 / P3 / R3 | held out +3.76 (< 6); polish picks registered before the held-out claim; number reproduced 4 times exactly |
| P4 | no measurement file changed in the row's 4 commits, nor since the verification (only judge/dynamics.py, outside the gap) |
| R2 / R4 | dashboard shows v_gap 18.91 |
| G2 / G3 | K preload 0.08 N.m, J2 step 0.13-0.20 N.m (red team); twist unmeasured (M5) |
| G5 / G6 | complexity 49 recomputed; K is slaved, never read, so it is not a sensed 4th joint. The knee pins are NEW-sensed-knee-pins |

## Proposals (not applied; measurement / reporting changes for the lead or the user)

- **P-1. A lead change needs a margin of at least one workspace pose (0.28) on the plain verified gap, or no held-out
  loss.** This replaces the retired A1 gate's role with no near-touch term. Measured effect on the verified rows (exact
  bench, held out n 1154): roller-longdyad (18.67, held 23.73) would not replace this design (18.91, held 22.67): plain
  margin 0.24 < 0.28 and held out -1.06. This design would not have replaced parallelogram on these rules (0.22 < 0.28,
  held -0.64). frontload -> this design (3.91 plain, +4.08 held) passes. kneeless-roller (21.07 / 24.59) and
  kneeless-sidecar (21.11 / 25.34) are behind on both. This is a tightening of a rule, so it is the user's call.
- **P-2. Ask the user whether the knee's sensed pins are joints** (NEW-sensed-knee-pins). Effect: see the finding;
  every pin-knee row would leave the DOF cap.
- **P-3. ALIGNMENT.md wording** (for the lead, not edited by this audit, since other auditors run on the same file):
  mark A1 "RETIRED 2026-10-17 (plain verified gap decides; contact stays < 1 mm)"; in G1 "Detect", drop `dominance` as
  a gate and keep it as a report; in G5 / G6, state that minarc pick1 is 4-active by the user's ruling and that the
  knee-pin question (P-2) is open.

## Cost

No farm jobs, no local re-wear (claim unchanged). About 15 min of reading and table work.

## Skeptic (2026-10-17, 02:24-02:40 UTC, git e99f42f -> 0a574f3)

The skeptic was a separate agent. It edited no bench, judge, kit, model, row, dashboard page or CLAUDE.md, and changed
no score. It used local compute only: nice, OMP_NUM_THREADS=1, one process. A farm batch was tried, but this session's
permission policy refused it, so the farm was not used ($0).

**Final verdict (ledger, `stage skeptic`, 2026-10-17T02:32:17Z): WATCH.** None of the 9 reasons was refuted, and all
are watch. The claim is 18.91.

**Re-measured this session (model unchanged).**
- **Exact re-wear.** `tools/alignment_audit.py` `remeasure`, unchanged, with its output dir redirected to the scratchpad.
  CB_EXACT=1, HEAD e99f42f, 232 s.
  - Frozen: **18.91**, 1 mm 20.00, 2 mm 34.03, 3 mm 155.98; band 3-14 mm 19.22.
  - Poses: near1 2 (0.28 and 0.38 mm), near2 26, near3 178. Lost: fold 86, slide 7, parts 2, contact 4.
  - Overhead p10 min metal 1.02 mm; overhead lost: fold 14, slide 4, contact 2.
  - Spans: dK 0..37.80 deg; knee K.ang 88.7-146.1 deg.
  - The fit used the rebuilt fast cache (`.cache/concept_bench`, created 01:59 UTC); fit_fast 10.3 matches row.gap.
  - Every figure matches `remeasure/sidecar-longdyad-knuckle-3r_bench.json` to the digit.
- **Measurement files.** `git diff --stat 63167c0 HEAD` changes only judge/dynamics.py. The diff covered the bench,
  kit, env bench, simplicity, judge/, body_pose, split.json, the band poses, both verify helpers, this model, its
  frontload parent and the pin-knee model.

**Rulings** (also in `docs/alignment/sidecar-longdyad-knuckle-3r.rulings.json`):

| key | refuted | evidence |
|---|---|---|
| near_touch (watch) | no | **Measurement.** Re-worn: the numbers are reproduced to the digit (above). **Threshold.** TH shell2_watch 15.0 is applied to gap_near2 - plain = 15.12, the same quantity the section-5 calibration ("15-31") used. **Label correction.** 15.12 is the 0-2 mm shell. The strict 1-2 mm shell (gap_near2 - gap_near1) is **14.03**, under 15. The watch crosses the line by 0.12 only through the 2 poses under 1 mm (+1.09). Held out: 14.57 for 0-2 mm, 11.49 for 1-2 mm. Re-reading the shell is a measurement change, so it is not used. **Wearer cost.** It is real (section 1 item 1): 24 taken bench poses sit at 1-2 mm and 2 at 0.28 / 0.38 mm. |
| reporting (watch) | no | **After the 02:13 refresh (fc0f574).** morphs.json still has gap 10.3, sweep_gap 10.3, reach 0.8 and the verdict "SCREENED, a candidate for the verifier". 100 (1 - 10.3/275) = 96.25. **Row.** t_verified and v_contact are null, while verification.contact is 0.0107. |
| S1 (watch) | no | **Numbers confirmed.** v_gap 18.67 / 18.91 / 19.13. Held out, exact, n 1154: 23.73 / 22.67 / 22.03. Held 1 mm: 26.83 / 25.75 / 24.44. One pose = 100/360 = 0.278. **Paired file.** 8 / 8 discordant, CI90 [-2.62, +1.77], pooled P(roller better) 0.287. **New.** At 1 mm the bench order reverses again: this design 20.00, parallelogram 20.22, roller-longdyad 20.30. This strengthens the finding. |
| NEW-sensed-knee-pins (watch) | no | **Recomputed** with `tools/simplicity.py`, the 2 pins moved to active and out of passive_rot: 49 -> 87 at 5 DOF (89 if passive_rot is kept). roller-longdyad 81.75, parallelogram 87, roller-flank 83.25, frontload 87; kneeless 23.75 / 28.0 unchanged. **No ruling.** A grep of CLAUDE.md, REQUIREMENTS, HANDOFF and ROUNDS finds no user ruling on the knee pins, only proposals (HANDOFF 222; ROUNDS 527-528, 738). |
| NEW-catalogue-drive (watch) | no | **Confirmed.** `_rh155cap354_bench.json` 19.76 / 20.85, 368 taken. `_held.json` 23.53 / 26.63. Control `_rh155_bench.json` 18.92. **No judge.** l1_sidecar-longdyad has no judge/. **Correction.** "about 1.2 behind roller-longdyad" uses roller's envelope-corrected 18.56, which the roller audit's S2 says never to quote. Like-for-like, the gap is **1.09** (18.67). |
| NEW-unpriced-stops (watch) | no | **Stops.** smlo 5.0. a1max 63.1774 = 28.9414 + 39.236 - 5 exactly. min th 5.232. **Priced.** 19.36 / held 23.29, min th 5.513. **Roller-longdyad.** smlo 5.0, a1max 0.27 inside its rule, so the comparison is like-for-like within 0.3 deg. **Wearer.** A built stop at exactly 5 deg with +-0.5 tolerance reaches 4.5 deg of the fold. |
| G1 (watch) | no | **Probe.** clip overhead floor < 2 mm on 8/10 frames (all 10 < 3 mm); workspace overhead 5/8 (1 < 1 mm). **p10.** 1.02 bench (own re-wear), 0.64 held. **Under 3 mm.** near3 178 vs roller 133. **Correction.** The shell figures mix two definitions. Bench 15.12 is n2 - plain, but its own parenthesis "20.00 -> 34.03" is 14.03. Held 11.49 is n2 - n1. Like-for-like: 14.03 / 11.49 for 1-2 mm, or 15.12 / 14.57 for 0-2 mm. |
| M5 (watch) | no | **Missing measurement.** No R17 / dynamics output for this design or l1_sidecar-longdyad anywhere in judge/ or pipeline/. The red team doc only plans it. |
| R1 (watch) | no | **HANDOFF.** Lines 81 ("no polish, no CAD") and 97 ("within 0.51") are unchanged since 4e5b038 (22:15). The polish closed at 22:03. **Row and dashboard.** The verdict still opens "SCREENED". |

**Missed by the audit** (not counted in this verdict; for the next audit):
1. **The round-9 lead change reverses at the user's own contact line.**
   - CLAUDE.md says "contact stays metal < 1 mm". The plain v_gap counts only penetration (< 0 mm) as contact, so
     poses with metal at 0-1 mm count as clearance.
   - At 1 mm, the exact bench reads: this design **20.00**, parallelogram 20.22, roller-longdyad **20.30**
     (`remeasure/*_bench.json` deep.gap_near1). Held out at 1 mm: 25.75 / 24.44 / 26.83.
   - Roller-longdyad's plain 0.24 lead becomes a 0.30 deficit on the bench and 1.08 held out. It has 3 taken bench
     poses under 1 mm, the closest at **0.072 mm** (deep.min_metal_mm). This design has 2, at 0.28 / 0.38 mm.
   - This is T1 at the 0 mm line: the round-9 winner's gain lives where metal sits within 0.1 mm of the skin.
   - The finding bears on the lead decision, not on this design's verdict. Proposal (a rule question for the user, not
     applied): state which line the "plain verified gap" uses for contact, 0 mm as the verifier computes it or 1 mm as
     CLAUDE.md words it. Effect on the verified rows, from the files above: at 1 mm this design ranks first of the
     three on the bench (20.00 / 20.22 / 20.30); held out, parallelogram first (24.44 / 25.75 / 26.83).
2. **The ball links are not at their real size in any reading (M2 / M3).**
   - The model samples an O7 socket (`ER, ZB = 3.5, 3.0`, model line 43). The build spec uses catalogue KBRM-02 /
     KBLM-02 heads, O9 x 4, with the horn ball centre **3.6 mm** over the lug top (0.6 mm spacer;
     `docs/research/sidecar_mechanism_redteam.md` lines 166-170).
   - `tools/alignment_drive_cap_wear.py` changes only the dK cap ("Nothing else changes"), so the 19.76 catalogue
     reading still samples O7 heads at ZB 3.0.
   - The verifier's own fast ZB sensitivity is +0.39 at ZB 4.0 and +0.54 at 4.5 (row
     `verification.zb_sensitivity_fast`).
   - The real-size envelope wear (O9 heads, ZB 3.6, cap 35.4) has not been run. Neither 18.91 nor 19.76 is yet the
     built exo's number.

**Notes** (not gaming):
- **The per-pose floor peaks just above 2 mm.** In the paired exact-fit dump (`_bench_perpose.json`, gap 19.66, not the
  claim), 74 of 371 taken bench poses have their floor at 2.25-2.5 mm, against 10 at 2.0-2.25 mm.
  - Held out: 153 of 859.
  - Most are arm-low poses (median elevation 22.9 deg), and the model's crown / wall term `cmin` binds on 58 of the 74.
  - It is a fixed hub-crown standoff, not a search line: the objective was the 1 mm near-touch gap.
  - Roller-longdyad has 19 poses in the same bin.
  - It explains the 3 mm cliff (34.03 -> 155.98). A report of each hub's floor would show it (proposal A3).
- **The tool's near_touch label.** `c_near_touch` prints "points live in the 1-2 mm shell" for gap_near2 - plain, which
  is the 0-2 mm shell.
  - Proposal (reporting only; no threshold or score moves): print both shells, 0-2 mm and 1-2 mm, with their labels.
  - Effect on the verified rows on file:

    | design | 0-2 mm | 1-2 mm |
    |---|---|---|
    | this design | 15.12 | 14.03 |
    | parallelogram | 31.01 | 29.92 |
    | roller-longdyad | 14.43 | 12.80 |

**Cost:** one local exact re-wear (232 s, one process, nice), no farm, $0.
