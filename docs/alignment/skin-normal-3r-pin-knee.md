# Alignment audit: skin-normal-3r-pin-knee

Audit of 2026-10-17 04:15-04:35 UTC (ledger entry `by auditor`, run `audit:skin-normal-3r-pin-knee`). This is the first
auditor report for this design; there is no earlier skeptic section to keep.

**Why it ran: a metric change, not a new claim.** Commit 3ceacea (03:40 UTC) put the user's ruling "if no encoders are
needed, it doesn't count as added complexity" into `tools/simplicity.py` v2. An unsensed two-pin cuff knee
(`mechanism.cuff_knee`) is now taken out of the count before scoring: 2 passive rotations, 2 bodies, 2 joints, 4 made
parts and 6 bought parts, the counts of this design's own doc (`docs/concepts/skin-normal-3r-pin-knee.md` line 584).
Its 2 encoders are dropped too (`sensed_passive` 2 -> 0). For this row complexity went from **19.5 to 0**. The bench gap
did not change.

This design is the source of the knee template and the only row where the hub-only sensing was measured before the
change. So this audit is also the calibration of the two sister audits (roller-longdyad, sidecar-longdyad).

## Verdict: WATCH (the ruling's premise holds in the model, at a fixed GH; the 0 is the user's to confirm)

- **The claim is unchanged:** verified v_gap **27.20** (score 90.11), H1 = H-g107-1, fit Bench(60,160) fast, shape
  frozen, worn on Bench(110,360) exact, fold margin 5, O20.
- **The claim was re-worn** because no re-wear was on file. Model unchanged, farm, CB_EXACT=1. It reproduces every
  figure to the digit: gap 27.20, reach 0.6583, follow 0.9636, in-band14 0.8953, contact 0.0256. Files:
  `docs/alignment/remeasure/skin-normal-3r-pin-knee_bench.json` and `_bench_perpose.json`. The per-pose dump recomputes
  27.20.
- **The ledger verdict is watch.** It comes from 4 tool checks (held_out, continuity, fold_margin, reporting) and
  8 judgement findings. None of them is gamed.
- **The three questions of the metric change, answered for this design:**
  1. **Faithfulness:** exact. The template is this row's own knee, item for item.
  2. **Determinacy:** holds in the model. With only J1, J2 and J3 read, the knee pins and the GH rotation are fixed at
     every taken pose. The smallest sigma is **0.3919** (worst condition 2.33) over 343 bench poses, which is the
     verifier's 0.3919 to the digit. Held out it is **0.3738** (condition 2.42) over 832 poses. The premise holds only
     with GH fixed: in-plane GH drift turns the J3 reading by 1.01 deg/mm (median) to 1.90 deg/mm (max), and the 3 hubs
     cannot see it. At R10's 4 mm that is up to about 7.6 deg of arm twist. The question is the user's.
  3. **Rankings:** the change moves this row onto the (gap, complexity) front. It was dominated there under v1, and it
     now replaces zc-frontier-3r at the zero end. It does not put any design that is better for the wearer behind it.

## What the wearer gets (measured, Bench(110,360) exact)

Sources: `remeasure/skin-normal-3r-pin-knee_probe.json`, `_bench_perpose.json` and `_bench.json`.

- **Reach:**
  - Workspace reach is 237 of 360 poses (0.658). Clip follow is 106 of 110 frames.
  - Overhead (elevation >= 140): **5 of 28 taken** (0.18) and 6 of 10 clip frames. The poses that are not taken fail
    on the fold (15), the knee window (7) and contact (1).
  - Raised arm (elevation >= 90): **32 of 113** taken. By band: 90-120 17/51, 120-140 10/34, 140-160 4/13,
    160-200 1/15.
- **Metal close to the skin (taken poses):**
  - Under 1 mm: 8 poses. The closest is 0.086 mm, at clip (30, 148, -60).
  - Under 2 mm: 27 poses. Under 3 mm: 92 poses.
  - Gap with metal under 1 / 2 / 3 mm counted as contact: 31.75 / 46.85 / 95.88, against 27.20 plain.
  - **Every one of the 5 overhead workspace poses that the design takes has metal under 2 mm** (3 of them under
    1 mm). So do 4 of the 6 taken overhead clip frames.
- **Contact:** 9 bench poses, depth sum 8.38 mm.
  - The deepest is **4.08 mm** at ws (15, 90, 30). The next are 2.45 mm at (30, 90, 30) and 1.13 mm at (-60, 60, 105).
  - The others, overhead included, are under 0.25 mm.
  - Held-out depths are not on file (see "Not measured").
- **Workspace in-band (unscored):** 0.8665 for 2-14 mm and 0.565 for 2-10 mm. At elevation 90-140 it is 0.877; overhead
  it is 0.948, over only 5 poses.
  - Part-weighted in-band14 is 0.917 against 0.895 sample-weighted.
  - Hub 3 is the outlier: 0.657 in band, standing proud at a median of 12.4 mm.
- **Fold margin:** at least 5.49 deg in th on taken poses, with no pose under the rule's 5
  (`docs/research/rebase/verify_pkH1_m5.json` windows).
- **Knee window:** [30.46, 149.54].
  - Taken knee angles run 103.0-147.3 on the bench. The smallest margin is 2.24 deg (verifier).
  - Held out the knee reaches **149.48, 0.06 deg from its limit**.
  - The window is a model rule. The model has no stop part for it.
- **Springs:** none. **Cuff twist:** not measured. The knee pins are passive, so nothing holds a planned state against
  the wearer.
- **Near-singular postures:**
  - J3 drive transmission is at least 0.46 (doc).
  - The hub-only sensing is weakest at the near-straight knee: sigma_min falls with knee angle (correlation -0.72 to
    -0.76).
- **Continuity:** 237 of 237 bench taken poses are connected and the full grid has 0 islands, so connected reach =
  static reach = 0.6583 (row `v_connected_reach`, doc check 5).
- **Complexity:** **0** under v2, which the dashboard shows. It was 19.5 under v1 and would be 9.5 with only the
  encoders taken out.

## (1) Faithfulness of the subtracted counts

The template was taken from this design, so it should match by construction. I checked it against the model header
(`docs/concepts/models/skin-normal-3r-pin-knee.py` lines 1-25) and the record's parts list:

| item | v2 subtracts | this row's knee (record notes + model header) |
|---|---|---|
| passive rotations | 2 | pins a, b (parallel to J3) |
| moving bodies | 2 | knee link + arm pad. Member 3 = hub-3 plate + E strap stays, as the spherical 3R's arm-end. |
| joints | 2 | pins a, b |
| made parts | 4 | knee link, arm pad, 2 Ti pins |
| bought parts | 6 | 2 x (GSM sleeve + 2 GTM washers) |
| closed loops | 0 | 0. The open chain is closed by GH, so nothing is left in. |

The subtraction is exact. Two side notes:
- The CAD build found the knee stack missing a top thrust washer and an e-clip per pin. Under v1 that was 0.5
  uncounted points; under v2 the knee scores 0 whatever hardware it carries (finding M3).
- The sister rows over-subtract by 2.5-3.5 points, because their own knees are smaller than this one. That is
  measured in `docs/alignment/{roller,sidecar}-longdyad-knuckle-3r.md`.

## (2) Determinacy without the knee encoders

Tool: `tools/alignment_knee_sensing.py`, which loads the model unchanged and builds it init-only with the knee centre
fixed from the Bench(60,160) fit, as in `frozen()`. At each pose it differentiates the model's own `ik` + `knee`
(h = 1e-4 rad about x, y, z through GH). It reads J1, J2, and J3 as the angle of member 3 against link 2 about u3. The
hub-only number is sigma_min of the hub rows of the orthonormal null space. This row has no knuckle, so the 8-row and
9-row forms are the same.

| set | poses | sigma_min (p5, median) | cond max | raw d(J1,J2,J3)/d(GH rot) sigma_min (cond max) | dJ3/dq3 | GH drift deg/mm max (median) |
|---|---|---|---|---|---|---|
| bench taken (per-pose dump) | 343 | **0.3919** (0.479, 0.583) | 2.33 | 0.555 (5.89) | 0.67-1.23 | 1.78 (1.01) |
| bench kinematic set | 359 | 0.3832 (0.470) | 2.38 | 0.550 (7.85) | 0.66-1.23 | 1.83 (1.01) |
| held out kinematic set | 832 | **0.3738** (0.472, 0.582) | 2.42 | 0.550 (8.27) | 0.65-1.27 | 1.90 (1.01) |
| verifier (rebase, same 343) | 343 | 0.3919 (0.479) | 2.3 | - | - | - |

Files: `docs/alignment/remeasure/skin-normal-3r-pin-knee_knee_sensing_{bench,held}.json`, with per-pose rows. Notes:
- The held set is the polish verifier's `held_bench()`. That model has no `frozen_held()`, so the kinematic set (a
  superset of the taken poses) is used.
- On every pose: no perturbed pose leaves the valid set, member 3's axis stays on u3 to within 0.016 deg, and
  dJ3/dq3 never changes sign. So there is one root and no hidden branch.
- The worst held-out pose is ws (60, 165, -45) with the knee at 149.48 deg. The worst bench pose is clip
  (30, 148, -60) at 147.2 deg.

**Reading.** With GH a fixed ball joint, which is all the bench models, the 3 hub encoders fix the knee pins at every
pose. The premise behind "no encoders are needed" is true here, with the largest margin of the three rows measured:
- this row: 0.392;
- sidecar-longdyad: 0.310 with K on its law;
- roller-longdyad: 0.250.

The premise is **not** true once GH translates.
- The two knee pins are exactly the two in-plane drift freedoms. The J3 reading then moves with no arm motion, by
  1.01 deg/mm (median) and up to 1.78-1.90 deg/mm.
- R10 (REQUIREMENTS.md, confirmed by the user) allows 4 mm of GH misalignment. That is up to about 7.1-7.6 deg of arm
  twist (median about 4 deg) that hub-only sensing cannot tell from real twist. Read knee pins would see it.
- SIMPLICITY.md lines 90-93 still say: "Sensing must also hold when the shoulder centre translates (R10)" and "Pins
  parallel to J3, whose angles add to the twist: 2. Example: the pin knee."

This is why the row's own verifier kept the 2 encoders. That is a question for the user, not a gamed finding: the
ruling is the user's, and the specified check passes.

## (3) Rankings and tie-breaks

`tools/simplicity.py` at 3ceacea^ (v1, on the 3ceacea^ records) against HEAD (v2), on every row with a mechanism
record. File: `docs/alignment/remeasure/skin-normal-3r-pin-knee_simplicity_v1v2.json`.

- **14 rows changed, not 13.** skinnormal-shortk-knuckle-4r (screened) took the cuff_knee key later, in f3e6e77 at
  04:03 UTC (42.0 -> 32.5).
  - 11 rows shift by exactly 19.5.
  - rim-lobe-arm-knuckle-3r shifts by 19.25 and coupler-path-j1 by 7.0; both are dead.
- **Within the pin-knee family no order changes:** the shift is uniform. The round-9 tie-break, roller-longdyad 24.25
  against sidecar-longdyad 29.5, keeps its 5.25.
- **This row moves onto the front.** Pareto front over the 51 verified rows (v_gap, complexity):
  - v1: zc-frontier-3r (0, 33.51), geneva-tail-knuckle-pinknee-3r (12.0, 23.57), kneeless-roller (23.75, 21.07),
    rim-lobe-arm (35.25, 20.57, dead), roller-longdyad (43.75, 18.67). This row (19.5, 27.20) was dominated by
    geneva-tail-knuckle-pinknee-3r.
  - v2: **skin-normal-3r-pin-knee (0, 27.20)**, geneva-tail-knuckle-pinknee-3r (12.0, 23.57), rim-lobe-arm
    (16.0, 20.57, dead), roller-longdyad (24.25, 18.67).
  - This row now sits at the zero end in place of zc-frontier-3r.
  - With only the encoders taken out (9.5), both would be on the front.
- **Order against the plain 3Rs.** This row now ranks simpler than 21 verified rows that were simpler than it under v1.
  It ties 4 plain 3Rs (zc-frontier-3r, spine-parked-j2-3r, risley-turret, posterior-max-margin-cardan), although it
  carries 2 more bodies, 2 more joints, 4 more made parts and 6 more bought parts than they do.
- **No design that is better for the wearer is put behind it on the gap axis.**
  - Every 0-complexity row has a worse gap.
  - geneva-tail-knuckle-pinknee-3r is better in gap (23.57) and at 2 mm (38.63 against 46.85), and it stays on the
    front.
  - Its 12.0 is a partial record: its counts are null and only its 3 loops score. So "this row is simpler than geneva"
    is likely true even under a faithful count.

## Findings (all watch)

1. **G5. Complexity hidden by the count (sensing premise).**
   - Evidence: the determinacy table above.
   - Why the exo is not better: complexity 0 says the wearer gets a 3R with nothing added. In fact the knee is 2 more
     bodies, 2 pins and 10 parts riding at 0.09-2 mm from the skin overhead. At a real, translating shoulder, hub-only
     sensing misreads arm twist by up to about 7.6 deg.
   - Action: the user answers questions 1 and 2 below. Until then, show "0 at a fixed GH" next to the number.
2. **NEW-caveat-dropped. A premise quoted without its caveat** (proposed catalogue entry R5).
   - The change cites this design's doc, lines 565-568, for "the 3 hub encoders fix the pose" (CLAUDE.md rule 5 and
     the SIMPLICITY.md change log).
   - Those lines read: "with GH known the knee pins need no encoder. The record keeps 2 sensed pins because
     SIMPLICITY.md requires sensing to hold when GH translates (R10) ... (9.5 if the user accepts hub-only sensing / a
     cuff IMU)."
   - The implementation took the condition as met. It also zeroed the knee's hardware, which is 9.5 more points than
     the 10 points of encoders the ruling names.
   - Action: show the user the cited lines whole (question 1).
3. **NEW-closure-as-cuff. A closure element counted as cuff alignment.**
   - The knee is this design's own closure at a fixed GH: J3's line misses GH.
   - SIMPLICITY.md lines 82-83 count such elements. offset-skin-normal-3r's 2 closure slides need no encoder at all,
     yet they still score 17.75.
   - Measured effect: this row moves from dominated onto the zero end of the front (section 3).
   - Action: question 3.
4. **P4. Judge changed with the design**, declared.
   - 3ceacea changed `tools/simplicity.py` and this row's record in one commit (19.5 -> 0). It carries a ruling,
     VERSION 2 and a change log, so the change is not hidden.
   - The audit tool's judge_change check still says "no metric file changed", because it follows only gap moves.
   - Action: proposal 4.
5. **G1. Metal hugging at 0-2 mm**, report-only by the user's near-touch ruling.
   - 27 taken poses have metal under 2 mm, and all 5 taken overhead workspace poses are among them.
   - Contact: 9 poses, deepest 4.08 mm.
   - Why the exo is not better: metal at 1-2 mm on the model is metal on a real, bulging arm. The overhead reach this
     design has (5 of 28) is bought with metal on the skin.
   - Action: none on the number. It is the overhead red-team's job.
6. **G4. Near-singular posture at the knee window edge.**
   - Held out, the knee runs to 0.06 deg of its 149.54 limit, and the hub-only sensing is weakest there (0.374).
   - The window is a rule in the model, not a stop part.
   - Action: the CAD needs a physical knee stop at 180 - ang_min. R16 / R17 should check it.
7. **M3. Unchecked clash.**
   - The knee stack leaves out the top thrust washer and e-clip: +1.4 mm, outward (doc check 3).
   - No skin number moves. The part-part check is left to the built CAD.
8. **R2. Displayed numbers that are not the verified state.**
   - The dashboard shows sweep_gap 19.72, the refuted in-sample GPU polish, 7.48 below the verified 27.20.
   - The row's verdict text is still the 03:32 k4598 screen (30.35).
   - Complexity 0 is shown with no fixed-GH note.
   - SIMPLICITY.md's worked example (21.5) and line 93 still describe v1.

Patterns checked and not found:
- **T1 / T2:** the band read at 3-14 mm gives 27.64 against 27.20 plain, so the 2 mm edge is worth 0.44.
- **T3:** the fold margin is 5.49 in th on taken poses.
- **T4:** the claim H1 keeps ang_min 30.46. The polish that walked the window to 21.9 (F7) was refuted and not adopted.
- **T5:** the depth sum is 8.38 mm, x1.35 the reference: below the tool's x2.
- **S1:** the claim is worn on Bench(110,360), outside its fit set. The polish-protocol held-out numbers are 28.55 and
  29.12 against 24.48 in-sample (+4.07, under the 6-point watch line). The fit-60 claim itself has no held-out wear.
- **S2 / S3:** the 2 mm grid covers every underside, and side walls, crowns and edges are checked. Part-weighted
  in-band is 0.917 against 0.895 sample-weighted.
- **S4:** contact is read on the skin mesh, as for every row.
- **S5:** connected reach = static reach.
- **M1 / M2:** O20 hubs, iglidur pins, stack from plate thicknesses.
- **M4:** pin b spans 40.6 deg and pin a 44.3 deg.
- **M5:** no springs. The sensing part is G5.
- **P1 / P2:** H1 was not chosen by its held-out number.
- **P3:** the re-wear and the verifiers agree to the digit.
- **R1:** v_gap comes from the verifier.
- **R3:** the rivals' spread is on the row (P5, C1, F2 / F5 / F7, all refuted out of sample).
- **R4:** the dashboard's v_gap = 27.20.
- **G2 / G3:** no spring, no spring-held coordinate.
- **G6:** 3 active joints, no 4th sensed.

## Not measured, and why

- **A held-out re-wear under the claim's own protocol** (fit-60, frozen, held set). The model has no `frozen_held()`
  and the remeasure tool needs one. The held-out numbers on file use the polish protocol, with the shape fitted on
  Bench(110,360): H1 28.55 (polish2 verifier) and 29.12 (exact fit). That is why the tool's held_out check stays watch.
- **Held-out contact depths and wear probe:** not measured, for the same reason.
- **Cuff twist and pin friction torque:** the bench is kinematic, and there is no R17 run of H1 on file.
- **The probe's own-state fold margin:** it errors on this model (no K axis). The verifier's 5.49 is used instead.

## Proposals (measurement changes, not inputs to the verdict)

1. **Read the ruling as "the encoders do not count".** The knee's encoders are dropped and its hardware is still
   counted.
   - Measured on every changed row (`..._simplicity_v1v2.json`, key `proposal_encoders_only_out`): this row and
     raglan-knee 9.5, cam-unfold 23.75, roller-longdyad 33.75, sidecar-roller-flank 35.25, frontload / sidecar-longdyad
     / sidecar-parallelogram 39.0, minarc 42.0.
   - Every changed row moves up by 9.5 from v2, except the dead rim-lobe-arm (9.25) and coupler-path (7.0). So no
     order changes inside the family.
   - zc-frontier-3r returns to the zero end of the front. This row stays on the front at (9.5, 27.20).
2. **Make the sensing exemption conditional on R10.** A knee counts unsensed only if the record names how it holds
   under the 4 mm of R10: a cuff IMU in the parts list, or a measured hub-only twist error under a stated bound.
   - For this row: 1.90 deg/mm x 4 mm = 7.6 deg. Under any bound below that, the 2 encoders come back (+10).
3. **Read the evidence that is already on file** (alignment_audit.py checks; for its maintainer).
   - held_out: read `v_polish2_h1_held_gap` and `v_p5_h1_held_gap`, tagged as a different fit protocol.
   - fold_margin: read the verifier's `windows.fold_margin_min_taken`.
   - continuity: read the scalar `v_connected_reach`.
   - Effect on this row: 3 tool watches -> ok. The ledger verdict stays watch because of the judgement findings.
4. **judge_change should also follow complexity moves.** It would flag every commit that changes
   `tools/simplicity.py` and a row's `mechanism` together. Effect: a declared P4 watch on all 14 changed rows for
   3ceacea.

## Questions for the user

1. Your ruling says "if no encoders are needed". The 3 hub encoders fix the knee only while the shoulder centre stays
   put. With the 4 mm of shoulder misalignment you confirmed for R10, the hubs can misread arm twist by up to about
   7.6 deg (about 4 deg typical), and read knee pins would not. Do you still want the knee to count as needing no
   encoders, and so as no added complexity?
2. Did you mean that only the 2 knee encoders stop counting (pin knee 9.5), or that the whole knee stops counting
   (2 pins, the knee link, the arm pad and their parts: pin knee 0, as implemented)?
3. offset-skin-normal-3r closes the same chain with two cuff slides. They need no encoder at all and still score 17.75.
   Should your ruling apply to them too, or only to pin knees?
4. The knee window (30.5-149.5 deg) is a rule in the model, and the held-out set runs the knee to 0.06 deg of it.
   Should the build carry a physical knee stop there, and should the model then check it like the J2 stops?

## Files

- Checks: `docs/alignment/skin-normal-3r-pin-knee.json` (12 checks, tool verdict watch).
- Findings: `docs/alignment/skin-normal-3r-pin-knee.findings.json`.
- Ledger: `docs/alignment/ledger.jsonl`.
- Re-wear and probe (model unchanged, farm, about $0.016 in all):
  - `docs/alignment/remeasure/skin-normal-3r-pin-knee_bench.json`
  - `docs/alignment/remeasure/skin-normal-3r-pin-knee_bench_perpose.json`
  - `docs/alignment/remeasure/skin-normal-3r-pin-knee_probe.json`
- Sensing: `docs/alignment/remeasure/skin-normal-3r-pin-knee_knee_sensing_{bench,held}.json`.
- Ranking: `docs/alignment/remeasure/skin-normal-3r-pin-knee_simplicity_v1v2.json`.
- New adapter, no model edits: `tools/alignment_pinknee_adapter.py`. It gives the model module PK = itself, so
  remeasure, dump and the wear probe can wrap its own `audit()`.
