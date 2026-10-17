# Alignment audit: slipper-nose-knuckle-3r

Auditor run 2026-10-17 15:03-15:12 UTC (the hourly audit). Ledger entry 2026-10-17T15:09:56Z, `by auditor`, run
`audit:slipper-nose-knuckle-3r`. Checks: `docs/alignment/slipper-nose-knuckle-3r.json` (13 checks). Findings:
`docs/alignment/slipper-nose-knuckle-3r.findings.json` (9).

This hour audits two things:
- **(A)** the lead's own bookkeeping commit 3d9dc71 (14:21): the complexity record fix, the dashboard's inferred
  v_contact, and the slipper row's new verdict text. The lead must not grade its own metric change.
- **(B)** whether the gen-7 full CAD user_slipper_nose carries the lead's 14:30 carry-overs, and whether any of its
  judges ran weaker than at L1. It was not re-judged; its own verifier runs later.

## Verdict: WATCH (ledger tool verdict watch; tool checks alone watch)

- **The claim:** v_gap 18.49 (score 93.28), frozen exact Bench(110,360), verified 06:22 UTC.
- **No re-wear.** 3d9dc71 changed only the row's verdict text, its `v_contact` and `mechanism.cuff_knee`.
  `best_params` and every measured field are unchanged since the 07:03 re-wear (bench 18.49, held out 23.45), so that
  re-wear still stands for the same configuration.
- **No gamed reason.**
  - The lead's complexity fix applies the v2.1 rule to the same knee topology. It does not flatter the leader.
  - The inferred v_contact reproduces the verifier's own contact on every row that has a verifier file.
  - The full CAD carries every carry-over, and its judges ran at the L1 steps.
- **One check moved, ok to watch:** complexity, "recomputed 18.25 vs row 22.25; MISMATCH". The lead freed the loop in
  the mechanism record but left the row's `complexity` field and its verdict text at 22.25.
- **One margin is newly measured on the build:** R17's forward-stroke cuff twist at mu 0.15 is 5.00 deg against the
  5.0 deg limit.

## (A) The lead's metric and display change, judged

### (A1) The knee closure loop on 5 rows

- **Each of the 5 rows has the same knee topology as the rows that already carry the key.**
  - slipper-nose and trimlug-k165 are roller-longdyad minus the roller: bodies 6 -> 5, joints 9 -> 8, loops 3 -> 3.
    roller-longdyad names its loops "drive, knee closure, K dyad stop".
  - dipped-law-groove (6 / 9 / 3) has roller-longdyad's own count.
  - inband-rssr names its 3 loops "the wearer loop, the lobe loop, the RSSR loop".
  - longstroke-slipper says "loops unchanged" from slipper-nose.
  - All 5 therefore charged the same loop that roller-longdyad, groove-desmo and sidecar-* freed in v2.1 at 04:55.
    That loop closes through the wearer's arm, and docs/SIMPLICITY.md section 4 says that loop is never counted.
    Freeing it removes a double count.
- **The fix is half applied.**
  - The dashboard computes complexity from the record and shows 18.25 / 18.25 / 20.25 / 24.5 / 26.5.
  - Each row's own `complexity` field still reads 22.25 / 22.25 / 24.25 / 28.5 / 30.5.
  - The slipper's verdict text still says "Complexity 22.25 vs 24.25" (it would now read 18.25 vs 20.25).
  - The audit tool reads the row field, hence its MISMATCH.
- **Is it uneven the other way?** Only on dead rows.
  - split-knuckle-twosided-3r lists its bodies without the arm pad, so its 5 loops are 4 drive loops plus the knee
    closure. It would read 45.0, not 49.0.
  - rim-lobe-arm-knuckle-3r has 2 loops by the same count (cam loop and knee closure). It would read 12.0, not 16.0.
  - Both are dead, so no live comparison moves.
  - cam-unfold-4th's one loop is its own cam-pushrod loop. minarc-stop-knuckle-4r, skinnormal-shortk-knuckle-4r,
    raglan-knee-3r and skin-normal-3r-pin-knee record 0 loops. All of these are correct without the key.
- **Ranking and headline:** unchanged. Complexity is shown and never scored.

### (A2) The dashboard's inferred v_contact

- **How it works.** tools/dash_build.py lines 433-439 infer v_contact as (v_gap minus the plain formula of v_inband14,
  v_follow and v_reach) / 100 for a verified row that has none. It accepts the result when it lies in
  [-0.0002, 0.3].
- **Rows affected:** 11 verified rows on today's board (inband-rssr's 0.0027 comes from its polished bench, not the
  inference).
- **10 of the 11 match the verifier's own contact exactly:**
  - from their `_v_bench_frozen` or `_corr_bench_frozen` files: dipped-law-groove 0.0107, dwell-fourbar 0.0087,
    geneva-tail 0.0106, groove-desmo 0.0056, j3-neck-over 0.0582, kneeless-roller 0.0262, kneeless-sidecar 0.0134,
    sidecar-longdyad 0.0107, sidecar-parallelogram 0.0107;
  - from the row's verification block: zc-frontier 0.0299.
- **1 cannot be checked:** seed-offset-3r-slides shows 0.0964 (v_gap 66.47, no verifier file). Its fast contact was
  0.11, so the value is plausible, and the row is far from any ranking.
- **Effect on rankings:** none. The board ranks by v_gap. Contact appears only in bench.js's tooltip and its sortable
  Contact column. Before the change, these rows showed 0.0 there (the fast bench's contact).
- **The hole that remains.** The accept band would silently turn a v_gap that is not the plain formula into "contact".
  Examples are a near-touch v_gap, a priced v_gap, or a connected-set reach under a static v_reach. For example, the
  slipper's 1 mm near-touch gap 20.12 would display as contact 0.0217 (7.8 poses) instead of 0.0054 (2 poses). No row
  does this today. Proposal P-A2 below.
- **Not a finding on this design:** the slipper row carries an explicit v_contact.

### (A3) The slipper row's new verdict text and v_contact

- **v_contact 0.0054** equals `frozen.contact` in docs/concepts/verify/slipper-nose-knuckle-3r_v_bench_frozen.json
  (gap 18.49, reach 0.725, follow 1.0, in-band 0.8955).
- **"held out 23.45"** equals `frozen.gap` in `_v_held_frozen.json` (reach 0.6828, in-band 0.8943, contact 0.0116).
- **"ledger WATCH"** was true at 14:21 and is still true.
- **What is stale:** the text's complexity numbers, as in (A1). The tool's reporting check no longer flags a
  self-measured screen.

## (B) The gen-7 full CAD user_slipper_nose: carry-overs and judge strength (not re-judged)

### Carry-overs (docs/HANDOFF.md section 9, lead 14:30)

All are present in pipeline/full-exo/designs/user_slipper_nose:
- **Verified flank:** build.json `fit.params.beta` -176.684, with the arc ending at -176.68. design.json fits: "keep
  the verified flank (beta -176.684, no beta step)".
- **+0.75 deg K lead:**
  - design.json fits: "lobe-ring key dowel at the onset phase + 0.35 deg of q2, J2 stop B slot end at q2 -15.47 (the
    CAD draws the nominal -15.82 = the loaded state)".
  - build.json lobe ring: "O1 dowel key at the onset phase + 0.35 deg of q2".
  - Assembly note: "K phase at the onset +0.75 +-0.3 deg, shim the key dowel".
- **Tolerance notes:** "nose hole / crank pivot / lobe profile +-0.02 mm true position, r_c +-0.1 mm".
- **Knee pins:** MR63ZZ pairs, 2 at pin a and 2 at pin b (build.json part list).
- **Knee stop:** `ang_stop` 154.7811 (= 180 - ang_min 25.2189). Checked on 27 poses with 0.0 deg error. One valid
  solid.

### Judge strength against L1

- **Same steps:** judge/vs_l1.json states the rule (R1 step 3, R2 6, R6 3, R16 12, R17 full; FEA skipped on both).
- **R2:** the same 24.87 mm headline (the user's forearm cuff).
  - The project's own parts now read 4.71 mm beyond the rig's self-intersection, where L1 read 0.0.
  - This is a relabel, not new metal. The 4.71 mm is the user's BOTTOM bar at the same frame (Comb hair, frame 162).
    At L1 that bar was a user part (BOTTOM 17.59 / 4.71 attributable). On the full CAD it is merged into D8-06 (BOTTOM
    + arm pad + pad mount), which is "ours".
  - The upper arm cuff is the project's own on every full CAD (user_roller_longdyad, user_minarc_*, user_geneva_rod*,
    ...), so it is not new here.
- **R17:** the same judge and cases.
  - Nominal: twist 4.04 deg (L1 4.01), M_GH 0.129 N.m (L1 0.127).
  - The same stale note ("knee stop (149.5 deg) is not in the CAD and not modelled; the knee pins are free") is in
    both, now with a 154.78 deg stop built.
- **R16:** 64.2 % = L1.
- **R1, R1-aim and R4 lose against L1:** R1 81.1 vs 82.0, R1-aim 47.4 vs 48.6, R4 73.1 vs 74.5. The builder's own file
  flags it (`loses_against_L1: ["R1"]`), and attribution is pending in its workflow.
- **No judge ran weaker than at L1.**

## What the wearer gets (measured)

Measured on Bench(110,360) exact, frozen, from the 07:03 re-wear and probe of the same configuration; held out in
brackets.

- **Overhead (elevation >= 140):** 8 of 28 workspace poses taken (18 of 71).
  - Full CAD R4: 73.1 % (FAIL against 80; L1 74.5).
- **Raised arm:** reach is 26/51 at elevation 90-120 and 12/34 at 120-140. Workspace reach in all is 0.725 (0.683).
  - R16 on the full CAD: 64.2 %.
- **Taken poses with metal under 2 mm:** 30 of 371 (66-67 of 852).
  - Under 1 mm: 3 (14).
  - The lowest is 0.072 mm at (-60, 60, 105).
- **Deepest contact:** 9.01 mm at (15, 165, -60) overhead, from the crank arm and flank lug; summed 14.75 mm over 2
  bench poses. Held out: 10 poses, summed 46.12 mm, deepest 9.05 mm at (30, 165, -45).
- **Workspace in-band (unscored):** 0.856 over all taken poses, and 0.800 at elevation 90-140 (0.199 of the metal above
  14 mm).
  - Full CAD R1 81.1 %, R1-aim (2-10 mm) 47.4 %.
- **Spring, cuff twist and arm load (R17 on the full CAD, MuJoCo, rolling bearings mu 0.005):**
  - Nominal: twist 4.04 deg against 5.0, M_GH 0.129 N.m, cuff force 0.58 N. K on its law to 0.139 deg, lift-off 0.000.
  - Return stroke at mu 0.087 / 0.12 / 0.15: 3.61 / 3.46 / 3.32 deg.
  - Forward-stroke bound at mu 0.12 / 0.15: **4.78 / 5.00 deg** (M_GH 0.158 / 0.166 N.m).
  - Plain-bearing cases (f 0.05 and up) fail as at L1. That is why the knee and hubs are rolling bearings.
- **Stops and fold margin:**
  - th margin minimum 5.181 bench (5.006 held out).
  - The +0.75 deg K lead that covers the as-built K lag is on the full CAD's drawing.
  - The knee stop is built at 154.78 deg.
- **Singular postures:** with K at rest, m_sub is under 1 deg on 50 of 371 bench poses. This is family-wide (G4), and
  B1 is open with the user.
- **DOF and complexity:** 3 active, 0 passive translations, O20 hubs. Complexity is 18.25 by the record and the
  dashboard, and 22.25 in the row field.

## Findings (each watch; none is gamed)

1. **M5: the spring holds, at the limit on the build at mu 0.15.**
   - **Evidence:** the builder ran the audit's forward-stroke bound on the full CAD
     (judge_m5/forward_bound_mu120/150.json, 15:00 UTC). Twist reads 4.78 / 5.00 deg against 5.0; L1 read 4.90 / 4.97.
   - **Why it matters:** R17 passes, but with 0.00 deg of margin at mu 0.15. The bench number does not depend on it.
   - **Action:** report R17 at mu 0.15 as "at the limit". Run the nose wear test to confirm mu stays at 0.12 or below.
     Keep the preload at 0.08 N.m or below.
2. **NEW-one-sided-proxy: carried, half fixed.**
   - **Evidence:** the build now runs both strokes. The L1 EVOLUTION row still shows only the return stroke, where
     twist falls as friction rises.
   - **Action:** close this when the gen-7 EVOLUTION row reports the forward stroke as the binding number.
3. **T3: the fold margin needs the K lead, which is now on the drawing.**
   - **Evidence:** held out 5.006 deg. The as-built K lag would put 1-2 held-out poses under 5. The K lead and its
     assembly note are in design.json fits.
   - **Action:** keep this at watch until a built part shows the K phase.
4. **NEW-synthesis-cliff: the tolerance is now on the drawing.**
   - **Evidence:** as built, the cliff is at r_c -0.4 to -0.5 mm (design-space scan -0.20). The build carries r_c
     +-0.1 mm and +-0.02 mm true position, and the verified beta.
   - **Why the exo is not worse:** the score does not stand on the cliff.
5. **T1: carried from the L1.**
   - **Evidence:** the 11 R16 step-1 body contacts are the claim's own scored contacts. The build adds 0.60-1.45 mm on
     8 of 12.
   - Full-CAD step-1 attribution is pending.
6. **G4: carried.** m_sub is under 1 deg on 50 of 371 bench poses with K at rest. B1 is open with the user.
7. **T5: carried.**
   - **Evidence:** 2 bench contacts, 14.75 mm summed, 9.01 mm deepest. That is 2.37x sidecar-longdyad's depth, which
     this design ranks above.
   - Mixed for the wearer: sidecar-longdyad is worse plain and at 2 / 3 mm.
8. **NEW-ws-inband: carried.**
   - **Evidence:** 0.800 in-band at elevation 90-140, and R1-aim 47.4 % on the full CAD.
   - The full CAD also loses R1 (-0.94), R1-aim (-1.22) and R4 (-1.39) against its own L1, as its builder already
     flags.
9. **NEW-stale-complexity-ruler: the lead's fix is right, but the row field and verdict text still read 22.25.**
   - **Evidence:** see (A1).
   - **Why the exo is not worse:** the stale field is reporting hygiene against the design, not for it.
   - **Action:** refresh `complexity` on the 5 rows. Fix the verdict's "22.25 vs 24.25". Record split-knuckle and
     rim-lobe-arm's knee loop the same way if they are ever revived.

The tool's other watch reasons are carried and unchanged:
- **idle:** the knee is asserted rigid by the model's honesty flag, but it moves as a free knee by design. This is the
  family's known wording.
- **reporting:** the sweep best is 13.0 fast against 18.49 verified. It is shown as a sweep, not as a claim.

## Patterns walked (each against this design and the goal)

- **T1 (metal just past a cutoff):** watch, finding 5. **T2 (near-touch):** check ok, 1 mm 20.12 / 2 mm 33.02 on file.
  **T3 (margin read on another angle):** watch, finding 3. **T4 (bound walking to a singular posture):** the synthesis
  cliff (finding 4) and G4.
- **S1-S5 (sampling):** check ok. Bench and held out are both re-measured; the held-out drop is +4.96 (family-typical).
- **M1-M5 (model):**
  - Components are real: O20 hubs, MR63ZZ knee pairs, an ISO 8734 nose dowel.
  - No zero-size part: the envelope-corrected value is 18.44, close to 18.49.
  - M5 (spring): finding 1.
- **P1-P4 (protocol):**
  - The polish adopted nothing, so there is no in-sample tuning in the claim.
  - The held-out split is untouched.
  - No re-measuring until lucky: one claim, verified once, re-worn once.
- **R1-R4 (reporting):**
  - The verdict text now says VERIFIED with its true numbers. Its complexity numbers are stale (finding 9).
  - The board's v_contact is now right for this row.
  - New pattern for the catalogue: the inferred-field hole (P-A2).
- **G1-G6 (gaming):**
  - The judge did not change with the design: 3d9dc71 touched only the display and the complexity record, and the
    judge_change check is ok.
  - Hidden complexity: the opposite holds here (the row field over-reads by 4).
  - Best-of-many: the convergence gate passes and the spread is on file.

## Proposals (not applied; each a reporting or catalogue change for the lead)

- **P-A1 (row hygiene):** refresh the stored `complexity` of every row whose record carries `cuff_knee.closed_loops`
  from tools/simplicity.py. Or drop the stored field and read the record, as the dashboard already does. Measured
  effect: 5 rows, 4.0 points each toward simpler. No score or rank moves.
- **P-A2 (inferred contact, reporting):** in tools/dash_build.py, mark an inferred v_contact as inferred (for example
  a `v_contact_src` field). Cross-check it against the row's `docs/concepts/verify/<id>_v_bench_frozen.json` when one
  exists, and warn when they differ by more than 0.0003. Measured effect today: 0 of the 10 checkable rows differ.
  seed-offset-3r-slides cannot be checked.
  - Proposed catalogue entry R6: "a display field derived from another field (inferred, not measured), shown as a
    measurement".
- **P-B1 (judge note):** judge/dynamics.py's note "knee stop (149.5 deg) is not in the CAD" is stale on every
  slipper-family build: the stop is built at 154.78. Either model the knee stop as a joint limit in the dynamics case,
  or update the note. This is a judge change, so it is the lead's and the user's call.
- **P-B2 (R2 attribution):** report the merged BOTTOM part's attributable depth with the source of each depth, user bar
  or project geometry, so a 0.0 -> 4.71 mm "ours" step that is only a relabel is not read as new metal.

## Numbers not obtained, and why

- **No new re-wear or probe:** the configuration is unchanged since the 07:03 re-wear (only verdict text, v_contact and
  the complexity record moved). The 07:03 numbers stand.
- **Full-CAD R16 step-1 attribution:** in progress in the builder's workflow. Not re-judged, by instruction.
- **The full CAD's forward-bound files** are the builder's uncommitted WIP (15:00 UTC). They are read as found and
  could still change.
- **seed-offset-3r-slides' true contact:** no verifier file in the repo.

---

## Skeptic (2026-10-17, ~07:15 UTC)

Every reason re-derived from the rawest file on disk (per-pose dumps, wear probes, the m_sub probe rows, the verifier's
frozen JSON, the model and row files, `tools/simplicity.py` v2.2). No re-wear was needed: every number the reasons
cite reproduced from the auditor's dumps, which themselves reproduce the claim (18.49 / held 23.45). No model, bench,
judge, row or score was touched. Rulings: `docs/alignment/slipper-nose-knuckle-3r.rulings.json`.

**Final verdict (ledger, `--by skeptic`): WATCH.** 2 reasons refuted with evidence (`idle`, `NEW-filler-metal`), 6 upheld.

### Rulings

- **`idle`: refuted (an instrument false positive).**
  - The claim runs the lead cell. The model's line 36 defaults `SN_CELL` to `lead`, and the verifier's line 34 sets the
    same default. The row records `frozen.cell 'lead'` and `mechanism.cuff_knee.pins 2`.
  - `knee_moved` is set only at `kneeless-roller-knuckle-3r.py:166`. The slipper model only reads it at line 136, and
    that text is what `c_idle` matched.
  - The 65.71 deg is the pin knee's designed motion: 151.92 - 86.21, inside its window of 25.22-154.78
    (`remeasure/..._probe_bench.json extras`).
  - The drives move: K 45.62 deg and the crank 19.3 deg, both far above the 2 deg idle threshold. This is the same
    ruling as groove-desmo's.
- **`reporting`: upheld.**
  - The row's verdict begins "screened -" while its status is verified. In `morphs.json`, sweep_gap 13.0 sits 5.49
    under v_gap 18.49, past the 5-point trigger.
  - Measured mitigation, which does not refute it: the dashboard's headline sweep best is minarc's 6.19, so this 13.0
    shows only in the row's own column, and the fast-to-frozen drop (+5.49) matches the lead's (+5.48).
  - The verdict text still says "Complexity 22.25 vs 24.25", using the lead's pre-v2.1 number.
- **`judgement:M5`: upheld (missing measurement).**
  - What is on file: only the row note's hand calculation (about 9 N normal force, Hertz about 340 MPa, drag
    0.01-0.02 N.m). There is no R17, lift-off or preload output for this design, and no CAD.
  - The verifier's `extra.pa_rule` is confirmed: crank 34.47 and horn 40.77 deg effective, friction 4.97 deg = atan(0.087).
  - The lead's lift-off safety factor (2.42-2.79, `docs/research/roller_mechanism/results_bench.json`) is for a rolling
    contact and does not carry over.
  - New: the hand calculation assumes a 3.5 mm convex flank. The verifier's own N3 check reads
    `extra.nose.flank_rho_min_mm` **1.285 at k 0.5 deg**, at the rest end of the stroke where the nose sits on 204 of 371
    bench poses, against a 1.18 mm nose. The check stores the magnitude only, so the sign is unknown. If that section is
    convex, the line-contact Hertz figure rises by about 20 %. The wear test should load that section.
- **`judgement:G4`: upheld.**
  - Recomputed from both probes' `rows`: max |m_sub difference| over the 371 shared poses is 0.0. 204 poses are at
    rest; m_sub is under 5 deg on 106 and under 1 deg on 50, with a minimum of 0.0 at pose 227.
  - 30 of the 50 poses under 1 deg are workspace poses at elevation 60-119: the ordinary raised arm, not an overhead
    corner.
  - The ruling on B1 is still open with the user.
- **`judgement:T5`: upheld.**
  - The per-pose dumps give 14.75 mm on the bench (9.01 + 5.74) against sidecar-longdyad's 6.23 (x2.37, +8.52 mm), past
    TH 2.0 / 5 mm. Both sides use the same claim protocol, and each dump reproduces its claim.
  - Held out it is 46.12 against 35.67 (x1.29). It is shallower than the lead (16.46 / 49.88).
- **`judgement:NEW-ws-inband`: upheld.**
  - Probe numbers confirmed: elevation 90-140 in-band 0.8004, over 14 mm 0.1987, max 30.8 mm. The lead reads 0.7979 and
    sidecar-longdyad 0.8409.
  - Floor at those poses: 19 under 3 mm against sidecar's 25. The comparison is mixed.
- **`judgement:NEW-stale-complexity-ruler`: upheld.**
  - `simplicity.score` v2.2: the row as recorded 22.25; the same record with `cuff_knee.closed_loops 1` 18.25; the lead
    20.25.
  - Otherwise the records differ only by the deleted roller (joints, bodies, passive rotations, rolling and sliding
    pairs). It is a real inconsistency in the records, even though it runs against the design.
- **`judgement:NEW-filler-metal`: refuted for this claim. The measurement is right; C1 stays in the catalogue.**
  - The numbers are confirmed: 21.18 to 20.12, hub 3 in band 0.505 to 0.799, 4.73 g added, a drop of 3.4 mm mean and
    7.61 mm max, and the crown at a median 21.9 mm in both columns.
  - Every wedge column is `cell 'kneeless'`. The claim is `frozen.cell 'lead'`, its params carry no wedge, and 18.49
    reproduces without one.
  - On the lead cell the wedge cannot exist. The design doc (lines 104-108) measured all 36 tilt-by-azimuth
    configurations at 0.0 mm of drop.
  - The wearer of the claimed exo carries none of that metal.

### Missed by the audit (not counted in this verdict; for the next audit)

1. **The dashboard shows the verified slipper as contact-free.**
   - The row has no `v_contact` field. `docs/dashboard/bench.js` line 5 (`contact: m.v_contact ?? m.contact`) therefore
     shows the screen's `contact` 0.0 under "evidence: verified".
   - The verified frozen contact is 0.0054 (`rows/...json verification.frozen.contact`): 2 poses, 9.01 + 5.74 mm.
   - The lead, with the same 2 contact poses, shows 0.0054. Side by side, the slipper looks contact-free and the lead
     does not.
   - The defect is pipeline-wide, not this design's doing: 12 verified rows in `morphs.json` lack `v_contact`, among them
     sidecar-longdyad, groove-desmo, the kneeless pair and dipped-law. It is an R-family reporting flatter that
     `c_reporting` does not read.
   - Proposal (instrument, no score moves): `c_reporting` should compare the dashboard's verified contact with the
     verifier's frozen contact, as it already does for v_gap. Effect on this row: the reporting watch gains a second
     reason. On the other 11 rows: not measured.
2. **The hand-calculated contact stress uses a flank radius the verifier did not find.** The note says "a convex 3.5 mm
   flank", but `verify _v_bench_frozen.json extra.nose.flank_rho_min_mm` is 1.285 at k 0.5 deg. This is part of M5's
   missing measurement. Before the wear test, report the signed flank curvature at rest.
3. **Small correction to the stated horn margin.**
   - The exact bench probe's `extras.sc_info` reads `pa_horn_max_taken` 36.1 and `pa_eff_horn` 41.1 deg. The audit
     quotes 35.8 and 40.77 from the verifier: 1.9 deg under the 43 cap, not 2.2.
   - The friction coefficient at the cap is then tan(43 - 36.1) = 0.121, which agrees with "holds to mu 0.12" and leaves
     no margin beyond it.

## Skeptic (2026-10-17, ~14:20 UTC, on the 14:03 hourly audit)

Final verdict (ledger tool, `alignment_ledger.py skeptic`): **WATCH**. 2 of 12 reasons refuted with evidence (idle,
NEW-synthesis-cliff); 10 upheld. Nothing the score counts was found wrong; one bound was found tighter than the audit wrote.

New measurement: the M5 forward-stroke bound with the clock-spring RATE de-rated as well as the preload (the audit
de-rated the preload only; judge/dynamics.py line 308 keeps K_RATES constant). Same judge unchanged on disk (rates set
in-process by a wrapper), same L1 copy, preload 0.0982, rates (0.015, 0.010)/0.815, local, niced, 1 process, 79 s:
**twist 4.97 deg** against the 5.0 limit (krate case 4.85), M_GH 0.165 N.m, cuff 0.75 N, K vs law 0.127 deg, lift-off 0.
R17 still passes, by 0.03 deg. File: docs/alignment/remeasure/slipper-nose-knuckle-3r_m5_forward_bound_rate.json.

Rulings (full evidence in docs/alignment/slipper-nose-knuckle-3r.rulings.json):

- **contact_depth - upheld.** Re-derived from the claim dumps: bench 2 contacts, 9.005 + 5.741 = 14.75 mm; the
  reference's claim dump (sidecar-longdyad _bench_perpose_claim.json, frozen 18.91) 6.23 mm over 4. x2.37 and +8.52 mm
  pass TH depth_ratio 2.0 and depth_floor_mm 5.0. Held out 46.12 vs 35.66 (x1.29). The K-lead variant presses the same.
- **idle - refuted.** Instrument false positive (model and verifier unchanged since 06:12): the lead cell is the
  default (model line 36), the model only reads `knee_moved` (line 136), the row records a two-pin knee; K.qa span
  65.71 deg inside the knee window [25.22, 154.78]; dK 45.61 deg and crank 19.3 deg are far above TH idle_deg 2.0.
- **reporting - upheld.** Row verdict still begins 'screened -'; dashboard sweep 13.0 vs v_gap 18.49 (5.49 > 5);
  dashboard v_contact null vs frozen 0.0054. A reader's label, measured right.
- **judgement:M5 - upheld, tighter.** Forward bound with rate de-rated: 4.97 deg (above). The six runs are linear in
  preload (about 49 deg per N.m). The nose is not in the judge.
- **judgement:NEW-one-sided-proxy - upheld, with a nuance.** The falling column (3.58/3.42/3.28 deg) is right physics for
  the return stroke, and the EVOLUTION row and commit 4a80fdf do say 'return stroke ... proxy, stated'. But the figures
  are whole-clip peaks under the return-stroke de-rating (lower bounds) printed beside 'R17 PASS at all three'; the
  forward bound at mu 0.15 is 4.90 (audit) / 4.97 (rate too): a 0.03 deg margin where the row suggests 1.72.
- **judgement:T3 - upheld.** Red-team table confirmed (held 4.998 (1) at -0.1, 4.966 (2) at -0.5, 4.950 (2) at -0.7).
  The lead's score effect is now on file (db95242): +0.75 deg K lead bench 18.46 (th 5.244, near1 20.09), held 23.43
  (th 5.068): the fix costs 0.03 bench points. Still upheld: the verified config and the judged L1 carry no lead, and
  asbuilt.json shows flank-side tolerance also breaks 5.0 held out (beta -0.25 deg 4.984 (1), lobe g +0.02 mm 4.975 (2),
  pivot e2 -0.05 mm 4.989 (1), r_c -0.2 mm 4.997 (1); 'stack lag' +-0.05 mm 4.936 (2)).
- **judgement:NEW-synthesis-cliff - refuted.** The as-built answer is on file (asbuilt.json, db95242): with the
  verified flank and an off-size crank the drive keeps its stroke (r_c -0.2 mm: stroke 49.65 vs 49.75, crank PA 34.79 <
  38.03, off-flank 0, no-push 0; r_c -0.5 / -1.0 mm: PA 39.0 / 43.59, stroke 49.51 / 49.36; g -0.02: stroke 50.17;
  beta -1: 48.77). 'Stroke 0' is the re-synthesis refusing PA > cap, not the built part; the physical PA cap sits at
  r_c about -0.45 mm, about 90x the +-5 um bore tolerance. The score steps (18.43-18.48) were already not a knife edge.
- **judgement:T1 - upheld, one number corrected.** All 11 model-side body contacts are scored contacts of the claim,
  and the build-only pose (-60,60,105) holds (0.53 mm in on the build, 0.072 mm off on the bench, taken). But 'the model
  depths match the dumps to 0.01 mm' holds on 4 of 11 only; on 7 the attribution file's model depth under-reads the
  claim's own depth by 0.15-1.07 mm (it evaluates the L1 builder's fit, a part list that still carries 'roller'). Against
  the claim's depth the build adds 0.60-0.73 mm on the 4 link-2 strap poses, 0.19-0.38 mm on 4 overhead drive poses and
  0.00 on 4: the commit's '11/12 model's own' is closer than the file's model_own 4.
- **judgement:G4 - upheld.** msub_rest_bench.json: lt1 50 of 204 rest poses, min 0.0 at (15,75,15). B1 open.
- **judgement:T5 - upheld.** Same depths; the L1 build shows 5.5-9.4 mm overhead presses; the K lead does not change them.
- **judgement:NEW-ws-inband - upheld.** probe ws_elev90_140 inband14 0.8004, over14 0.1987; reproduced by the K-lead claim
  (e90_140 0.8004 bench, 0.822 held).
- **judgement:NEW-stale-complexity-ruler - upheld.** Row and dashboard still 22.25 vs the lead's 20.25.

Missed by the audit (for the next audit; not counted in this verdict):

1. The M5 forward bound leaves the spring rate un-de-rated: with rate / eta too, twist is 4.97 deg at mu 0.15
   (margin 0.03 deg, not 0.10). The R17 pass at the friction edge is thinner than the audit reports; a preload or rate
   a few percent above nominal, or mu slightly above 0.15, fails it.
2. The R16 step-1 attribution (build_slipper_l1.py) compares the build with the L1 builder's own model fit, not with
   the verified claim's frozen metal; on 7 of 11 poses that fit is 0.15-1.07 mm shallower than the claim dump, so its
   'build excess' figures and its model_own 4 are instrument readings, not build facts. The fair comparison is with the
   per-pose claim dumps (done above).
3. The held-out fold margin is exposed to flank-side geometry, not only K lag: single tolerances of beta -0.25 deg,
   lobe g +0.02 mm or pivot e2 -0.05 mm each put 1-2 held-out poses under 5 deg (asbuilt.json). Whether the +0.75 deg
   lead covers a worst-case stack of K lag (-0.53 -0.24) plus flank-side error at the red team's +-5 um is not measured;
   at the +-0.02 mm stack the K error reaches -0.346 deg (asbuilt_extra.log), which the lead still covers by estimate
   (slope 0.08 deg of margin per deg of K), at +-0.05 mm (-0.83 deg) it would not.
4. Small: the wearer summary's '3 under 1 mm' on the bench reads 2 by the claim dump's min_mm (0.072, 0.749; next 1.017
   at (15,90,30)); the near-touch 20.12 implies 3, so the third is a sub-0.02 mm boundary pose.

Note on sources: asbuilt.json and the claim_klead075 files are committed (db95242); asbuilt_extra.log (r_c -0.3 .. -1.0 mm,
the stack cases) is the running agent's working-tree log (git-ignored), read not re-run; the refutation of
NEW-synthesis-cliff stands on the committed asbuilt.json cases alone (r_c -0.2 mm: PA 34.79, stroke 49.65, off-flank 0).

No gaming found. Final verdict: **WATCH**.

## Skeptic (2026-10-17, ~15:20 UTC, on the 15:03 hourly audit)

Final verdict (ledger tool, `alignment_ledger.py skeptic`, entry 2026-10-17T15:17:23Z): **WATCH**. 2 of 13 reasons
refuted with evidence (idle, NEW-synthesis-cliff); 11 upheld. Nothing the score counts was found wrong. One bound was
found to fail by the judge's own rule once the rounding is taken out.

**New measurement: the full CAD's mu 0.15 forward bound, read unrounded.**
- judge/dynamics.py rounds `twist_peak` to 2 decimals (line 903), then compares the rounded value with the 5.0 deg limit
  (line 1222). So "5.00 = the limit, PASS" could be any raw value up to 5.00499.
- Re-run on a scratch copy of user_slipper_nose: preload 0.0982, rates / 0.815, the judge unchanged on disk, an
  in-process wrapper that leaves the 2-decimal roundings raw. Local, nice, 1 process, about 60 s.
- Result: **twist 5.00081 deg** on Reach a high shelf (tracking 5.00503), M_GH 0.166 N.m, K vs law 0.126 deg,
  lift-off 0. It reproduces the builder's forward_bound_mu150.json to every displayed digit (5.0 / 5.01 / krate 4.89).
- By the judge's rule on the raw value, `free` = False: **over the limit by 0.0008 deg**.
  - Physically this is negligible. But the bound at mu 0.15 is a fail, not "at the limit, PASS".
  - Not affected: the krate 0.0123 case (4.887), mu 0.12 (4.78) and the official nominal R17 (4.04).
- File: docs/alignment/remeasure/slipper-nose-knuckle-3r_m5_forward_bound_fullcad_raw.json.

Rulings (full evidence in docs/alignment/slipper-nose-knuckle-3r.rulings.json):

- **contact_depth - upheld.**
  - Claim dumps: bench 9.005 + 5.741 = 14.75 mm against sidecar-longdyad's claim dump of 6.23 mm over 4 poses (x2.37,
    +8.52 mm). That is past TH 2.0 / 5 mm.
  - Held out: 46.12 against 35.66 mm.
  - The full CAD presses the same two poses: 9.06 and 9.32 mm from the bell crank.
- **idle - refuted (instrument false positive).**
  - The model defaults to the lead cell (line 36) and only reads `knee_moved` (line 136). That flag is set only in the
    kneeless models (kneeless-roller:166, kneeless-sidecar:150).
  - The knee moves through 86.21-151.92 deg, inside its window [25.22, 154.78]. dK 45.62 and the crank 19.3 deg are far
    above TH idle 2.0.
- **complexity - upheld.**
  - simplicity v2.2 on the row's record gives 18.25; the row field reads 22.25.
  - Four other rows are stale the same way: trimlug, dipped-law, inband-rssr and longstroke.
  - The field over-reads, which runs against the design. No rank moves.
- **reporting - upheld.**
  - morphs.json sweep_gap 13.0 against v_gap 18.49 (5.49 > 5).
  - The "screened -" verdict sub-trigger is gone: the verdict now begins "VERIFIED".
  - 17 verified rows trip the same sweep trigger, so this is a pipeline-wide label.
- **judgement:M5 - upheld, tighter.** At mu 0.15 the twist is 5.0008 deg raw (above). The pass is a rounding artefact.
- **judgement:NEW-one-sided-proxy - upheld, mostly fixed.**
  - Fixed: the gen-7 EVOLUTION row (line 52, committed after the audit) now reports the forward bound as "the thinnest
    number".
  - Still open: the full CAD's scorecard.json R17 reads PASS with no forward reading. The row lists the return-stroke
    "PASS at mu 0.087 / 0.12 / 0.15" first. Its "5.00 = the limit" is 5.0008 raw.
- **judgement:T3 - upheld, widened.**
  - The held-out fold margin is 5.006 deg. The red-team table gives 4.998 (1 pose) at -0.1 and 4.982 (1) at -0.3.
  - The drawing's assembly note "+0.75 **+-0.3** deg" is not in the red team's stack. The red team puts the worst build
    at -0.02 deg with the full +0.75 lead. At +0.45 the worst build is at -0.32 deg, about 4.98 held out.
- **judgement:NEW-synthesis-cliff - refuted.** asbuilt.json at the drawn r_c +-0.1 mm:
  - crank PA 32.74 / 7.6 against the 38.03 cap (margins 5.29 / 30.43 deg);
  - stroke 49.70 / 49.81 (nominal 49.75), off-flank 0, no-push 0, held-out fold 5.000 / 5.010 with none under 5.
  - The crank cliff (r_c -0.4 to -0.5 mm) is 4-5x outside the drawing.
- **judgement:T1 - upheld.**
  - The full-CAD step-1 attribution is now on file: 11 body-contact poses, all of them scored contact poses of the claim
    (2 bench, 9 held out).
  - Against the claim's own depth, the build presses deeper on 10 of the 11: by 0.27-0.52 mm on 9 and by 0.06 mm on 1.
    It is 0.21 mm shallower at (15,105,15).
  - The L1's build-only pose (-60,60,105) is gone.
- **judgement:G4 - upheld.** In msub_rest_bench.json, m_sub is under 1 deg on 50 of the 204 rest poses, with a minimum
  of 0.0 at (15,75,15). B1 is open with the user.
- **judgement:T5 - upheld.** The depths are the same as in contact_depth. On the full CAD, the bell crank presses
  9.06 / 9.32 mm and link 1a 5.68-7.59 mm at elevation 150-165. The comparison is mixed, as the reason says.
- **judgement:NEW-ws-inband - upheld.**
  - Probe at elevation 90-140: in-band 0.8004, 0.1987 over 14 mm; 0.8218 held out.
  - vs_l1.json: R1 -0.94, R1-aim -1.22, R4 -1.39. Its `loses_against_L1` lists only R1, because its rule covers R1 / R6 /
    R16 only.
- **judgement:NEW-stale-complexity-ruler - upheld.** The 5 row fields are still stale (above). The verdict text still
  says "22.25 vs 24.25".

Missed by the audit (for the next audit; not counted in this verdict):

1. **The R17 twist gate is decided on a rounded number.**
   - judge/dynamics.py line 903 rounds `twist_peak` to 0.01 deg before the `<= 5.0` test at line 1222. The same pattern
     applies to every rounded field the `free()` test reads (M_GH and force are rounded too).
   - On this build the mu 0.15 forward bound reads 5.0 / PASS but is 5.00081 / FAIL raw.
   - Proposal (a judge change, so a measurement change for the lead and the user): compare unrounded values and round
     only for display.
   - Measured effect: this design's mu 0.15 forward bound flips PASS to FAIL, by 0.0008 deg. Its nominal R17 is
     unchanged (4.04). Other designs' R17 runs were not re-read.
2. **The horn's friction ceiling is below the M5 action's "confirm mu <= 0.12".**
   - asbuilt.json nominal: `margin_horn_mu012` -0.37 deg. The horn's effective pressure angle passes the 43 deg rule at
     mu = tan(43 - 36.53) = 0.113, not at 0.12.
   - At the drawn r_c +0.1 mm, `margin_horn_mu087` is 1.18 and `mu012` is -0.69, so the ceiling falls to 0.108.
   - The claim's mu is 0.087 (margin 1.18-1.89 deg across the band), so the score is unaffected. But the wear-test pass
     line should be mu <= 0.105-0.11, not 0.12.
   - The red team already reads the worst-lead build at 43.3 deg held out at mu 0.12 (redteam line 69).
3. **The K-lead assembly tolerance is outside the red team's stack.**
   - design.json fits says "K phase at the onset +0.75 +-0.3 deg". At the low end, the worst build (-0.53 systematic,
     -0.24 random) nets -0.32 deg, about 4.98 held out with 1 pose under 5.
   - At the high end (+1.05 plus 0.24 random), the horn PA cost is past the red team's worst-lead case (+0.74 deg
     already 43.3 deg at mu 0.12).
   - Proposal: tighten the shim band to about +-0.1 deg, or measure both ends.
4. **Small: the full-CAD attribution file still reads `model_own` 4** (user_slipper_nose/judge_r16s1/body_attrib_step1.json)
   while all 11 are the claim's own scored contacts. It is the same model-fit instrument issue as at L1 (14:20 skeptic,
   missed 2). The EVOLUTION row's text ("every one the verified model's own contact") is right; the file field is not.

No gaming found. Final verdict: **WATCH**.
