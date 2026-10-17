# Alignment audit: sidecar-longdyad-knuckle-3r (verified, round-8 lead, round-9 tie with roller-longdyad)

This is the metric-change audit of 2026-10-17, 04:03-04:15 UTC. Ledger entry 2026-10-17T04:14:33Z (`by auditor`, run
`audit:sidecar-longdyad-knuckle-3r`). The audit is about commit 3ceacea (simplicity v2: an unsensed two-pin cuff knee
scores 0, and the 2 knee encoders are dropped). It does not re-check the bench claim. It edited no bench, judge, kit,
model, row, dashboard page or CLAUDE.md, and changed no score. It added one new tool,
`tools/alignment_knee_determinacy.py`. Local compute only: nice, OMP_NUM_THREADS=1, at most 2 processes. No farm, $0.
The earlier auditor sections (01:45-02:00 UTC) are replaced by this one. Their findings that the change did not touch
are carried over below. The skeptic's section is kept under the dated rule at the end.

## Verdict: WATCH (ledger)

- **Claim:** verified v_gap **18.91** (score 93.12), frozen exact Bench(110,360), held out 22.67. The claim did not
  move. Complexity moved from 49 to **29.5** (simplicity v2). The row's top-level `complexity` field still reads 49.0.
- **Ledger reasons** (all watch):
  - From the tool (2): complexity MISMATCH (row field 49.0 vs 29.5 recomputed; hand count), and reporting.
  - From this judgement pass (8): G5, NEW-law-dependent-sensing, S1, NEW-catalogue-drive, NEW-unpriced-stops, G1,
    M5, R1.
  - None is gamed.
- **What the user asked about the change, answered for this design:**
  1. **Faithfulness.** The standard knee subtraction does not match this row's own knee. It takes 2.5 points too much
     (bodies, made and bought parts) and leaves the knee's loop in (4 points). Net, the recorded 29.5 is **1.5 higher**
     than a faithful reading (28.0, its kneeless twin). The error does not flatter this design.
  2. **Determinacy.** The 3 hub encoders do fix the pose at every taken pose, as long as K follows its law:
     sigma_min 0.310 and condition 2.80 at worst, against the reference 0.39 / 2.3. With K off its law they do not
     (sigma 0). So the ruling's premise holds in the model. In the real exo it rests on one clock spring that R17 has
     never tested.
  3. **Ranking.** No flip for this design. The round-9 tie-break margin, roller-longdyad against this design, stays
     at 5.25 (v1 43.75 vs 49; v2 24.25 vs 29.5).

## Re-wear (by the rule: the row's last commit, 3ceacea 03:40 UTC, is newer than the remeasure file)

`CB_EXACT=1 tools/alignment_audit.py remeasure sidecar-longdyad-knuckle-3r bench`, model unchanged, 229 s. It
reproduces every figure to the digit:

- plain 18.91
- 1 mm 20.00, 2 mm 34.03, 3 mm 155.98
- min metal 0.278 mm
- near1 2 / near2 26 / near3 178 poses
- band 3-14 mm 19.22
- overhead p10 floor 1.02 mm

File: `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_bench.json`. No measurement file has changed since the
skeptic's re-wear: `git diff e99f42f HEAD` on bench, kit, env bench, judge/, body_pose, split, band poses and the
models shows only tools/simplicity.py and the audit tool. I did not re-run the held-out wear: the claim did not move
and no measurement file changed.

## (1) Faithfulness: does the standard knee match THIS row's knee?

The v2 rule subtracts the knee of skin-normal-3r-pin-knee (line 584): passive_rot 2, moving_bodies 2, joints 2,
custom_parts 4, catalogue_parts 6. It drops sensed_passive from 2 to 0 and keeps closed_loops. This design has a
kneeless twin, `kneeless-sidecar-knuckle-3r`. Its record says "knee link, 2 iglidur pins and 2 knee encoders deleted"
and "the knee loop is gone". The difference between the two records is this row's own knee:

| field | this row | kneeless twin | the knee by the twin | v2 subtracts | points (weight) |
|---|---|---|---|---|---|
| passive_rot | 6 | 4 | 2 | 2 | match |
| joints | 10 | 8 | 2 | 2 | match |
| moving_bodies | 7 | 6 | **1** | 2 | 1.0 over-subtracted |
| custom_parts | 16 | 14 | **2** | 4 | 1.0 over-subtracted |
| catalogue_parts | 16 | 12 | **4** | 6 | 0.5 over-subtracted |
| closed_loops | 3 | 2 | **1** | 0 | 4.0 left in |
| sensed_passive (v1) | 2 | 0 | 2 | 2 | match |

`tools/simplicity.py` on each record:

| reading | complexity |
|---|---|
| v1 | 49.0 |
| v2 as recorded | **29.5** |
| the twin's knee subtracted, loop kept | 32.0 |
| the twin's knee and its loop subtracted (= the kneeless twin) | **28.0** |

Read literally ("the knee adds no complexity"), the ruling makes this row equal to its kneeless twin, 28.0. v2 gives
29.5. The loop the rule leaves in outweighs the parts it over-subtracts. The same holds for roller-longdyad: 24.25
against kneeless-roller's 23.75 (twin delta bodies 1, made 1, bought 2, loops 1).

Which count is right? The built CAD (`pipeline/full-exo/designs/l1_sidecar-longdyad/parts_full.json`) has these knee
parts:
- the knee link (37.7 x 10 x 2.18 Ti), with a knee stop tooth and web that the standard count does not name;
- a separate arm pad (the pin b plate);
- the E boss (the pin a plate) on member 3;
- 2 pin retainers (DIN 6799 e-clip + GTM washer).

That supports the standard 4 made / 6 bought. The twin's hand count is the low one. Both records are hand counts
("confidence": "hand count") and neither is derived from the model. MR63ZZ pairs: the knee has none here (iglidur pins);
the MR63ZZ pair belongs to the bell crank and is not subtracted. Nothing is shared between the knee and another part,
except the E boss, which is merged into member 3's E strap; the standard count already treats it that way.

## (2) Determinacy without the knee encoders

New tool: `tools/alignment_knee_determinacy.py`. It loads the design's verifier and model unchanged and wears them on
the verifier's frozen protocol. At every taken pose it writes the loop J1 - K - J2 - J3 - pin a - pin b - GH(3R) as
unit screws (GH fixed, the arm a ball about it) and repeats the null-space Jacobian test of
docs/concepts/skin-normal-3r-pin-knee.md lines 565-568.

How the frames were checked:
- Each joint's axis and point is read from both members it joins. The largest disagreement is 5e-6 mm and 4e-7 in
  direction.
- K's law is regressed from the taken poses: dK = 1.6232 x q2 past the onset, which is exactly the row's kK; the fit
  residual is 0.0 deg. On stop A, K is held, so its rate is 0.

Output: `docs/alignment/remeasure/sidecar-longdyad-knuckle-3r_knee_determinacy_bench.json`. Exact Bench(110,360);
the frozen gap reproduces 18.91. 375 taken poses: 123 with K open, 252 with K on stop A.

| case | mobility | sigma_min of the hub rows (min / p5 / median) | condition (max) | poses < 0.05 |
|---|---|---|---|---|
| **K slaved by its law, J1 J2 J3 read** | 3 at every pose | **0.310** / 0.311 / 0.553 | **2.80** | **0** |
| K known (law or reading), J1 K J2 J3 | 4 | 0.332 / 0.445 / 0.520 | 2.87 | 0 |
| K free, only J1 J2 J3 read | 4 | **0** at every pose | inf | all |
| reference: skin-normal-3r-pin-knee | 3 | >= 0.39 | <= 2.3 | 0 |

- **The premise holds for this design.** With K on its law, the 3 hub encoders fix every passive coordinate (both
  knee pins and the 3 GH angles) at every taken pose. The knee pins cost no encoders here, as the ruling assumes.
- **Conditioning is a little worse than the reference.** The worst pose is workspace pose 345: K open 6.5 deg, q2
  -7.8 deg, knee angle 146.1 deg (the knee nearly straight, 7 deg inside its 153.1 stop). There, a hub-encoder error
  maps to up to 2.34 x that error in a knee pin (median 0.43), and up to 2.84 x into the passive coordinates as a
  whole.
- **The premise rests on K's law.** If K leaves its law (drive lift-off, K lag, the clock spring losing preload), the
  loop has a 4th freedom the hub encoders cannot see (sigma 0), and the arm pose read from the hubs is wrong by that
  error. Nothing else in the design measures it: K is never read and the knee encoders are gone. R17 (lift-off, K lag)
  has never run on this design (M5). So "no encoders needed" is proven kinematically, not for the spring-held drive.
- **Not checked: GH translation.** The pin knee exists because GH drifts (round-9 lesson). With GH translating, the
  knee pins take that drift, and hub-only sensing cannot separate it from arm rotation. This was the reason the
  verified pin-knee record kept its 2 sensed pins (SIMPLICITY.md, R10). The user's ruling accepts that. I did not
  quantify it.

## (3) Rankings and tie-breaks

| row | v_gap | held | v1 cx | v2 cx | twin-consistent cx |
|---|---|---|---|---|---|
| roller-longdyad-knuckle-3r | 18.67 | 23.73 | 43.75 | 24.25 | 23.75 |
| **sidecar-longdyad-knuckle-3r** | 18.91 | 22.67 | 49 | **29.5** | 28.0 |
| sidecar-parallelogram-knuckle-3r | 19.13 | 22.03 | 49 | 29.5 | - |
| sidecar-roller-flank-knuckle-3r | 20.08 | - | 45.25 | 25.75 | - |
| kneeless-roller-knuckle-3r | 21.07 | 24.59 | 23.75 | 23.75 | 23.75 |
| kneeless-sidecar-knuckle-3r | 21.11 | 25.34 | 28.0 | 28.0 | 28.0 |

Effect on this design:
- **Round-9 tie-break: no flip.** The tie-break is fewer passive translations, then complexity. Roller-longdyad
  stays ahead of this design by the same 5.25 points (4.25 twin-consistent).
- **This design's complexity order against every other row: unchanged.** It stays just behind its kneeless twin
  (29.5 vs 28.0).

What does flip:
- **roller-longdyad (24.25) is now simpler than kneeless-sidecar (28.0).** Under v1 it was 43.75 against 28.0.
  roller-longdyad now dominates kneeless-sidecar on gap and complexity together. kneeless-sidecar was already
  dominated by kneeless-roller, so the Pareto front of gap against complexity does not change.
- **ROUNDS.md round-9 lesson (1) no longer holds.** It says the kneeless bracket "halves complexity (49 -> 24-27)".
  Under v2 it saves 1.5 (sidecar) and 0.5 (roller), while costing ~2.2 gap points on the bench.

## What the wearer gets (measured)

| item | value | file |
|---|---|---|
| Overhead reach (elev >= 140) | **8 / 28 taken** workspace poses (lost: fold 14, slide 4, contact 2); 18 / 71 held out | `remeasure/..._bench.json`; row held_out |
| Raised-arm reach (taken / total) | 0-60: 161/172; 60-90: 55/75; 90-120: 25/51; 120-140: 12/34; 140-160: 5/13; 160-200: 3/15 | `remeasure/..._probe.json` |
| Taken poses with metal < 2 mm | **26 of 371** bench (2 < 1 mm, min 0.278 mm); 63 of 859 held out; 178 < 3 mm | `remeasure/..._bench.json` (re-worn today) |
| Deepest contact | **-4.61 mm at plane 30 / elev 165 / axial -60** (overhead); 4 contact poses on the bench, 10 held out (deepest 8.37 mm) | `_probe.json`; audit contact_depth |
| Workspace in-band (unscored) | 0.874 over 261 taken workspace poses; overhead 0.926 | `_probe.json` |
| Springs / stops | one K clock spring (0.08 N.m), J2 stops smlo 5.0 / smhi 16.55, K stop B 63.18 never binds, knee stop tooth at 153.1 deg | row; CAD parts_full |
| Sensing | 3 hub encoders; with K on its law they fix the pose (sigma_min >= 0.310, condition <= 2.80); with K off its law they cannot | `remeasure/..._knee_determinacy_bench.json` |
| Cuff twist, K lag, lift-off | **not measured** (R17 never run) | - |
| Near-singular postures | none in the loop (hub sigma_min >= 0.31); knee up to 146.1 deg, 7 deg inside its stop; fold margin >= 5.232 deg | determinacy file; row |

Numbers I could not get:
- cuff twist, K lag and lift-off: R17 has not run, and running it is the lead's L1 job;
- the arm-pose error per mm of GH drift with hub-only sensing: not built in this time box;
- the held-out determinacy: not run, because the bench and fit benches agree (0.310 / 0.310) and the time box was
  spent.

## Findings

### G5 (watch): the knee subtraction is a standard count, not this row's knee

- **Evidence.** Section (1). The subtraction over-subtracts 1 body, 2 made and 2 bought parts (2.5 points) and leaves
  the knee loop in (4 points). The net is +1.5 against the twin. The row's top-level `complexity` is still 49.0, while
  the dashboard shows 29.5.
- **Why it matters for the wearer.** It does not hurt them: the error costs this design 1.5 points. But the
  complexity order between pin-knee rows and their kneeless twins is now set by hand-count noise of 0.5-1.5 points.
- **Action.** Proposal P-1.

### NEW-law-dependent-sensing (watch): "no encoders needed" holds only while K follows its law

- **Evidence.** Section (2): sigma_min 0.310 with K slaved; 0 with K free.
- **Why the exo is not certainly better.** A drive that lifts off would make the arm pose read from the hubs wrong,
  with nothing to detect it.
- **Action.** Run R17 on the gen-6 L1 (M5) and report the K lag. Proposal P-2.
- **Proposed catalogue entry (ALIGNMENT.md section 2, G7 "sensing proven only kinematically").** A complexity credit
  for an unsensed coordinate is valid only if (a) the null-space test passes at every taken pose and (b) every slaved
  coordinate it relies on is shown to follow its law under load (R17). Detect: the null-space test with the slaved
  coordinates freed; if sigma drops to 0, list the springs or drives that hold the law.

### Carried over (claim unchanged; re-worn numbers identical)

- **S1 (watch).** The round-9 trio is within one workspace pose plain, and the order reverses held out and at 1 mm.
  The tie-break still picks roller-longdyad, now by a complexity margin of 5.25 that rests on hand counts.
- **NEW-catalogue-drive (watch).** The catalogue ball link with stop B at 35.4 reads 19.76 (held 23.53). The O9
  heads are unsampled.
- **NEW-unpriced-stops (watch).** The stops sit exactly on the rule. Priced, it reads 19.36 (held 23.29).
- **G1 (watch).** 26 poses < 2 mm. The overhead p10 floor is 1.02 mm (wearer only; not a gate).
- **M5 (watch).** One clock spring holds the drive, and R17 has not run. Under v2 this now carries the sensing claim
  too.
- **R1 (watch).** Stale records: row complexity 49.0, dashboard fast 10.3, verdict "SCREENED", ROUNDS round-9
  lesson (1).

## Patterns checked and clean (this pass)

| pattern | result |
|---|---|
| P4 (judge changed with the design) | 3ceacea changed tools/simplicity.py and 13 records' `mechanism` in one commit, but no gap moved and no design changed; it is a declared metric change with a change log (docs/SIMPLICITY.md) |
| G6 (DOF cap) | 3 active (J1, J2, J3); K slaved, never read; knee pins unsensed under v2, so they are not sensed joints. 3 DOF, within the cap |
| M4 (idle) | K opens 37.8 deg, crank 31.6 deg, knee pins 56.1 deg span (tool idle check) |
| T1-T4, S2-S5, M1-M3, P1-P3, R2-R4 | unchanged since the 01:56 audit (claim and measurement files unchanged; re-wear identical) |

## Proposals (not applied; for the lead or the user)

- **P-1. Derive the knee subtraction from each row's own kneeless twin (or its CAD part list), and decide whether the
  knee's closure loop is part of "the knee".** Measured effect on the rows with a twin:
  - this design 29.5 -> 28.0 if the loop goes, 32.0 if it stays;
  - roller-longdyad 24.25 -> 23.75 if the loop goes, 27.75 if it stays (twin delta bodies 1, made 1, bought 2);
  - no ranking among verified rows changes either way.
  This is a measurement change, the user's call.
- **P-2. Make the v2 credit conditional on a determinacy file** (null-space test on the frozen wear, sigma_min > 0
  at every taken pose with the slaved coordinates on their laws). For a slaved-K row, also require R17's K lag on
  file. Measured effect on this row: the first part passes (0.310); the second is missing, so the credit would be on
  hold until R17 runs.
- **P-3.** Fix the stale R1 items (row `complexity` 49.0 -> 29.5; ROUNDS round-9 lesson (1)).

## Questions for the user

1. Is the knee's closure loop part of the knee your ruling made free? Under v2 it still costs 4 points on every
   knuckle pin-knee row, while the simpler pin-knee record (skin-normal) never counted it.
2. Your ruling rests on "the 3 hub encoders fix the pose". For this design that is true only while the slaved K
   follows its law, which one clock spring holds. Do you accept that for MVP1, or should the knee-encoder credit wait
   for R17's K-lag measurement?
3. With GH drifting (the reason the knee exists), the hub encoders cannot tell GH drift from arm rotation. Is
   hub-only sensing acceptable to you under GH drift, or do you want a cuff IMU (round 6's alternative)?

## Cost

- One exact re-wear (229 s) and one exact determinacy wear (274 s), plus a fast debug pass.
- Local, nice, at most 2 processes. No farm, $0.

---

*Auditor sections above: 2026-10-17 04:15 UTC (metric-change audit of simplicity v2). Skeptic section below: 2026-10-17
02:24-02:40 UTC, made on the earlier auditor pass; kept unchanged.*

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
