# dipped-law-groove-knuckle-3r: alignment audit

Auditor pass, 2026-10-17 (discovery round 10, slice r10-A). Tool `tools/alignment_audit.py` VERSION 2026-10-17.2.
Reference row for the comparisons: the verified 3-active lead `roller-longdyad-knuckle-3r` (18.67).

## Verdict and claim

**Verdict: GAMED** (computed by `tools/alignment_ledger.py`, worst of the 12 checks and the judgement findings).

- **The claim:** `v_gap` 18.64 (score 93.22), frozen exact Bench(110,360), fit-60 shape frozen.
  - The dashboard (`docs/dashboard/data/morphs.json`) ranks it first among the 3-active rows, 0.03 ahead of the lead.
  - The row's own verdict calls it "level with the lead, not a lead change", which is the honest reading.
- **The re-wear reproduces it.** This audit re-wore the claim with the model unchanged:
  - bench 18.64 (`docs/alignment/remeasure/dipped-law-groove-knuckle-3r_bench.json`);
  - held out 24.07 (`..._held.json`).
  - The number is real. The question is what it buys.
- **Why gamed:** the claim exists only under a fold-margin reading that the design applied to itself. That reading is
  an open question for the user.
  - The family's reading fails 84 of 371 taken bench poses and 202 of 850 held-out poses. Their margin is 0.204 deg
    (bench) and 0.184 deg (held out), against the 5 deg rule.
  - The same cell without the dip needs no new reading (min 5.181 deg). It scores 19.33, which is behind the lead's
    18.67.

## What the wearer gets (measured)

All numbers are on Bench(110,360) exact, frozen, worn on the claim's own parameters. The bench probe is
`docs/alignment/remeasure/dipped-law-groove-knuckle-3r_bench_probe.json`. The lead's probe is
`docs/alignment/live_audit_2026-10-16/probe_roller-longdyad-knuckle-3r.json`, worn through the same harness.

| what the wearer feels | this design | the lead (roller-longdyad) |
|---|---|---|
| overhead reach (elev >= 140), taken / total | 8 / 28 | 8 / 28 |
| raised arm (elev 90-140), taken / total | 38 / 85 | 38 / 85 |
| taken poses with metal < 2 mm, bench (workspace + clip) | 34 (29 + 5) | 30 (25 + 5) |
| taken poses with metal < 3 mm, bench / held out | 147 / 334 | 133 / 274 |
| overhead taken poses with metal < 2 mm | 5 of 8 | 4 of 8 |
| contact poses, bench / held out | 4 / 17 | 2 / 10 |
| summed contact depth, bench | 21.87 mm | 16.46 mm |
| deepest contact, bench | 10.9 mm at workspace (15, 165, -60) | 10.55 mm at the same pose |
| new bench contacts | 4.52 mm at (0, 105, 15), 0.89 mm at (-15, 90, 45) | - |
| unscored workspace in-band 2-14 mm (all / elev 90-140) | 0.861 / 0.800 | 0.854 / 0.798 |
| scored clip in-band 2-14 mm | 0.8993 | 0.8937 |
| lowest metal, bench | 0.07 mm at (-60, 60, 105) | 0.07 mm, same pose |

Other numbers:
- **Springs:** one clock spring force-closes both rolling pairs (lobe follower and roller-flank). It now also has to
  close K below the old stop A, into a lobe dip 0.068 mm deep. No spring-torque or closure-force output exists for it.
- **Stops:** stop A moves to the dip floor. K is taken from -2.37 to 43.66 deg (`extras.dK_taken_max_deg` in the probe;
  `frozen.drive` in the row).
- **Knee:** the angle taken is 54.2-96.7 deg, inside its 20-160 window. The knee is not near its stops.
- **Cuff twist:** not measured. There is no R17 / dynamics run for this row.
- **Near-singular postures:**
  - The family's fold reading, min(m_sub, m_eff) wherever K is off its rest, is 0.204 deg on the bench. 84 taken poses
    are under 5 deg, all of them in the dip.
  - The verifier's coupled reading is 5.389 deg on the bench and 5.406 held out.
  - The horn pressure angle sits at its 43.0 deg cap (dK_lim 43.8, `why_lim` pressure_horn).
  - The bent arm clears hub K by 1.04 mm at the dip floor.

### Paired against its own D=0 control and the lead (re-measured here)

This audit dumped every pose of the claim and of its D=0 control (the same cell with `dipD` 0) on both wears:
- the tool is `tools/alignment_paired_params.py` (new), and the models ran unchanged;
- the dumps reproduce 18.64, 24.07, 19.33 and 22.97 to the digit;
- the comparison is in `docs/alignment/remeasure/dipped-law-groove-knuckle-3r_paired_controls.json`, using the paired
  bootstrap of `tools/alignment_paired.py`.

| comparison | wear | gap difference (negative: this design better) | 90 % interval | P(this better) | workspace poses taken only by this / only by the other | contact only here / only there / both |
|---|---|---|---|---|---|---|
| vs own D=0 control | bench | -0.70 | [-1.83, +0.36] | 0.80 | 1 / 1 | 0 / 2 / 4 |
| vs own D=0 control | held out | **+1.10** | **[+0.56, +1.82]** | **0.000** | **0 / 12** | 0 / 0 / 17 |
| vs the lead | bench | -0.03 | [-0.82, +1.18] | 0.41 | 1 / 1 | 2 / 0 / 2 |
| vs the lead | held out | +0.34 | [-0.53, +1.58] | 0.21 | 11 / 12 | **7 / 0** / 10 |

What the table shows:
- **On the bench**, the dip's gain is the two contact poses it removes (182 and 203). That gain is not significant.
- **Held out, the dip is strictly worse than no dip:**
  - it loses 12 workspace poses and gains none;
  - its contact poses are the same 17 poses (81.20 against 80.99 mm summed);
  - taken poses with metal under 3 mm rise from 293 to 334.
- **Against the lead, the gap is a tie on both wears.** Held out, though, this design touches the arm on 7 poses where
  the lead does not, and on none where the lead does and it does not. It has 17 contact poses against 10, and 81.20
  against 49.88 mm summed depth.

## Findings

Each finding gives the pattern, the evidence, why the exo is not actually better, and the action. The full text is in
`docs/alignment/dipped-law-groove-knuckle-3r.findings.json`, and the ledger entry is the last
`dipped-law-groove-knuckle-3r` line of `docs/alignment/ledger.jsonl`.

The tool's checks:
- `fold_margin` is **gamed**: 0.184 deg on file.
- `dominance` is watch: 0.03 better than the lead plain, 2.59 worse at 2 mm.
- The other ten checks are ok, including:
  - `held_out`: +5.43, under the 6-point line;
  - `contact_depth`: x1.33 bench and x1.63 held against the lead, under the 2x line;
  - `complexity`: 24.25, which agrees with the row.

**T3 (gamed): the fold margin is read on another angle.**
- **Evidence:**
  - The family's reading fails 84 of 371 taken bench poses and 202 of 850 held-out poses. Its minimum is 0.204 deg on
    the bench and 0.184 deg held out, and every failing pose is dipped. That reading is the lead verifier's: min(m_sub,
    m_eff) wherever K is off its rest. roller-longdyad passes it at 5.011 deg.
  - Sources: the bench probe (`extras.th_margin_own_state`) and `verify/..._v_held_frozen.json`.
  - The model drops msub on dipped poses (its "spec correction (2)"). The verifier accepts this with a new coupled
    reading: 5.389 deg on the bench and 5.406 held out.
- **Why this is not a better exo:**
  - CLAUDE.md says "A different reading is the user's call, not the model's".
  - msub for a K slaved from q2 has been on the user's open list since round 7.
  - Round 8 declined the same Jacobian argument for crank-rod and bighorn and parked them. Round 9's rule was "no msub-free
    positive drive".
  - The waiver is worth the whole lead:
    - the same cell with no dip passes the family reading (5.181 deg) and scores 19.33, behind the lead's 18.67;
    - with the waiver it scores 18.64, which the dashboard ranks first of the 3-active rows.
  - The coupled argument may be right for a K that is positively held. This K is held only by a spring against a
    0.068 mm dip (see M5).
- **Action:**
  - Show the row as "pending the msub ruling", with 19.33 as its rule-consistent number.
  - Put the question to the user together with crank-rod and bighorn (proposal B1).

**P1 (gamed): in-sample tuning.**
- **Evidence:**
  - The dip was aimed at poses 182 and 203 of the claim bench.
  - Measured pose by pose against its own D=0 control:
    - bench: -0.70, not significant (P 0.80);
    - held out: +1.10 worse, 90 % interval [+0.56, +1.82], P(dip better) 0.000.
  - Held out, the dip loses 12 workspace poses and gains none; its contacts are identical to the control's.
- **Why this is not a better exo:**
  - The stroke the dip spends (dK_lim 46.2 -> 43.8) costs reach on new poses. The two contacts it removes were two
    named bench poses.
  - The number ranks the dipped design above the identical mechanism without the dip. Off the bench, that mechanism is
    better for the wearer on every pose where the two differ.
- **Action:** do not carry the dip forward as a lever. The row itself already reads "the bench gain does not
  generalise". The side finding is worth more to the wearer: the centred-knee cell without the dip (22.97 held out)
  beats the lead held out (23.73).

**P4 (watch): the judge changed with the design.**
- **Evidence:** the msub waiver is in the design's own model (commit c177c28), and the coupled reading is in its
  verification commit (35afc38). No kit, bench or judge file changed, so `judge_change` cannot see it.
- **Action:** if the user adopts the coupled reading, land it in `tools/concept_kit.py` as its own commit, with the
  before / after of every verified row.

**NEW-contact-for-inband (watch): the board rewards touching more often.**
- **Evidence, against the lead on the same poses:**
  - On the bench, in-band is +0.56 points better (0.8993 against 0.8937) and contact is 0.53 points worse (4 poses
    against 2). The new contacts are 4.52 mm at (0, 105, 15) and 0.89 mm at (-15, 90, 45).
  - Held out, the contact poses are a strict superset of the lead's: 7 poses only here, 0 only there. That is 17
    against 10 contact poses and 81.20 against 49.88 mm summed depth.
  - The extra contacts come with kneewin's centred knee: the D=0 control has the same 17.
- **Why this is not a better exo:** "never touching" is the goal's first line. The score prices one contact pose like
  0.27 % of metal samples moved into the band.
- **Why watch and not gamed:**
  - the gap difference is a tie on both wears (P 0.41 and 0.21);
  - the score's weights are the user's ("the score stays as is").

**T1 (watch, report only): metal parked just past the 0 mm line.**
- **Evidence:**
  - The recovered pose 203 sits at 0.48 mm.
  - At 1 mm the dip recovers one pose: 20.81 against the control's 20.96.
  - 17.05 points of the gap live in the 1-2 mm shell.
  - Taken poses under 3 mm: 147 against the lead's 133 on the bench, and 334 against 273 held out.
  - 5 of the 8 taken overhead poses have metal under 2 mm.
- **Why this is not a better exo:** on a real, bulging arm, metal at 0.5 mm is metal on skin.

**M5 (watch): a spring that cannot be shown to hold.**
- **Evidence:**
  - One clock spring now has to close K below the old stop A into a 0.068 mm lobe dip. It also force-closes the
    roller-flank.
  - No torque, closure-force or R17 check exists for this row.
  - If the follower lifts on a dipped pose, K is free on a sub-chain 0.18-0.20 deg from its fold. K is never read.
- **Action:** run a spring-closure and R17 check before any CAD.

**NEW-sub-tolerance-feature (watch): the gain rides on a feature smaller than the shop can hold.**
- **Evidence:**
  - 10 um of lobe error is 0.35 deg of K, against a 2.37 deg dip floor (the verifier's issue 1).
  - With stop A moved to the dip floor, K's rest through the whole dwell sits on the drive chain's tolerance stack
    instead of a dowel stop.
- **Why this is not a better exo:** a feature the shop cannot hold may not exist on the built part, so the number
  measures a profile the wearer may never get.

**G4 (watch): the drive works at its limits.**
- **Evidence:**
  - The horn pressure angle is 43.0 deg, at its cap: K is taken to 43.66 deg of a dK_lim of 43.8.
  - The bent arm clears hub K by 1.04 mm at the dip floor, against the 1 mm rule.
- **Why this is not a better exo:** the wearer feels a drive at its transmission cap as stiffness or a jam.

**NEW-preview-not-claim (watch): the picture is not the claim.**
- **Evidence:** the dashboard preview was rendered at th_c 50 / w 8. The claimed configuration is th_c 53 / w 12
  (the verifier's issue 3).
- **Action:** re-render the preview from `best_params`.

**S5 (watch): continuity depends on the flood graph.**
- **Evidence:** the full flood gives 18.64 with 0 poses dropped. The knn flood gives 20.32, with 6 dropped (+1.68).
- This is the same as the lead (20.34), so it does not change the comparison with the lead.

**Patterns walked and not found:**
- T2: band read as 3-14 mm, 18.85.
- T4: the knee is taken at 54-97 deg inside its 20-160 window; no bound walked.
- S2: part-weighted in-band 0.925 against sample-weighted 0.899.
- S3: every declared body is sampled.
- M1 / M2: O20 everywhere, 0 passive translations.
- M3: no new part.
- M4: K spans 42.5 deg and the crank 17.7 deg.
- P2: held out was measured after the fit and never used to choose.
- P3 / R3: 14 configurations, with their spread reported.
- R1 / R2 / R4: the dashboard shows the verified 18.64.
- G2 / G3: no new spring; the cuff is not measured (see below).
- G5 / G6: complexity 24.25, the same parts as the lead.

**Proposed catalogue entries:**
- **M6. A feature below its manufacturing tolerance.**
  - Looks like: a gain that rides on a geometric feature smaller than the process holds (here a 0.068 mm cam dip).
  - Detect: report the score-relevant coordinate's sensitivity to a 10-25 um profile error, and re-wear with the
    feature at its tolerance.
- **R5. A preview of a configuration other than the claim.**
  - Detect: the preview's parameters equal the row's `best_params`.
- **G7. Contact traded for in-band inside the tie band.**
  - Looks like: a row ranked above another whose contact poses are a strict subset of its own.
  - Detect: paired contact discordance (only-here against only-there) next to every rank change inside 1 point.

## Proposals (not applied: measurement or rule changes for the user or the lead)

These are not applied. Each is a measurement or rule change for the user or the lead, with its measured effect.

**B1. Rule on msub for a K slaved from q2, then apply the ruling to every row.** The question has been open since
round 7. A sub-question: does a spring-closed slaving count like a positive one?
- **If "msub applies":**
  - this row's dip is inadmissible on 84 bench and 202 held-out poses;
  - its rule-consistent cell is the D=0 control, 19.33 bench and 22.97 held out;
  - the lead is unchanged (5.011 deg);
  - crank-rod and bighorn stay parked.
- **If "coupled reading":** this row keeps 18.64; crank-rod and bighorn reopen at complexity 36.
- No other verified row on file uses the waiver: roller-longdyad, kneeless-roller and kneeless-sidecar pass the family
  reading at 5.011, 5.091 and 5.007 deg.

**B2. If a coupled reading is adopted, require proof that the slaving holds.** A spring-closed slaving would need a
closure-force check at the worst arm load.
- Effect: this row needs a check that is not on file. Positively held drives are unaffected.

**B3. Mark ties on the dashboard.** Rows within 1 point of the lead show as "level with the lead" instead of being
ranked above it.
- Effect: this row (18.64), the lead (18.67), sidecar-longdyad (18.91) and sidecar-parallelogram (19.13) show as one
  tied group.
- This is a reporting change. No score moves.

**B4. Report contact discordance next to every rank change inside the tie band.** A row may rank above another only if
it touches no more poses (paired, held out).
- Effect: this row would rank behind the lead (7 / 0 held-out contact discordance).
- No other pair was measured here.
- This is a tightening, so it is the user's call.

## Not measured, and why

- **The farm was not used.** The session's permission policy refused the cloud batch, because CLAUDE.md requires the
  user's approval for paid compute. Every re-wear here ran locally, with at most 2 processes.
- **Held-out wear probe** (unscored workspace in-band held out, overhead floors held out): not run within the time
  box. The held-out contact depths and floors come from the per-pose dump instead.
- **Cuff twist and spring hold** (R17 / dynamics): this row has no dynamics run, so they were not measured.
- **Hub-only knee determinacy for kneewin's centred knee** (`tools/alignment_knee_sensing.py`): not run within the time
  box. It was measured for the lead's knee only.
- **The gap with the dip kept and msub enforced** (dipped poses counted as lost): this would need a changed model.
  The D=0 control, 19.33, stands in as the rule-consistent number.
- **Kneeless control cell:** not run, by the designer either.
