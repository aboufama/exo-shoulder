# dipped-law-groove-knuckle-3r: alignment audit

Auditor pass, 2026-10-18 22:05-22:20 UTC (hourly re-check). Tool `tools/alignment_audit.py` VERSION 2026-10-18.1.
Ledger entry 2026-10-18T22:14:58Z, `by auditor`, run `audit:dipped-law-groove-knuckle-3r`.

Why this audit ran: the row was committed again in 8f69bd6 (2026-10-17 15:21) and 3d9dc71 (14:21), after the last audit
(06:48). Both commits changed only the complexity record: 24.25 -> 20.25, because the knee's closure loop is now free under
simplicity v2.1. That is a measurement change, not a design change. The claim (18.64) did not move. The model, its import
chain (roller-longdyad -> sidecar-roller-flank -> ... -> seed-offset-3r-slides), `tools/concept_bench.py`,
`tools/concept_kit.py` and the held-out split are all unchanged since the 2026-10-17 re-wear.

## Verdict and claim

**Verdict: GAMED** (the worst of the 12 checks and 13 judgement findings, computed by `tools/alignment_ledger.py`).
The flag still holds.

- **The claim:** `v_gap` 18.64 (score 93.22), frozen exact Bench(110,360), fit-60 shape frozen.
- **The re-wear reproduces it to the digit.** The model ran unchanged; the files are in `docs/alignment/remeasure/`.
  - Bench: 18.64 (`dipped-law-groove-knuckle-3r_bench.json`, 130 s).
  - Held out: 24.07 (`..._held.json`, 236 s).
  - Every deep number is identical to the 2026-10-17 run.
- **Why it is still gamed:**
  - **T3:** the number exists only under a fold-margin reading the design chose for itself. The family reading fails
    84 / 371 bench poses (min 0.204 deg) and 202 / 850 held-out poses (min 0.184 deg). B1 is still open with the user
    (HANDOFF section 7 item 3).
  - **P1:** the dip's bench gain is in-sample. Held out, the dip is strictly worse than the same cell without it. It is
    also significantly worse than lowarm-kstop, which it outranks on the bench (measured this audit).
- **Where it ranks now:** 8th of the verified 3-joint rows by v_gap, behind the lead conecut-knee-knuckle-3r (18.28).
  It still ranks above roller-longdyad (18.67), lowarm-kstop (18.69) and every row below them.
- **Pages:**
  - The public board (`docs/dashboard/public/index.html` line 278) shows it as "Flagged" and sinks it below the live
    rows.
  - HANDOFF section 3 says gamed.
  - No board or handoff page shows it as verified or as a leader.
  - Some records outside the board still read as an unflagged verified result: the concept doc and the row verdict
    (finding NEW-flag-not-on-doc).

## What the wearer gets (measured)

Bench numbers are Bench(110,360) exact, frozen, on the claim's own parameters: the probe
`docs/alignment/remeasure/dipped-law-groove-knuckle-3r_bench_probe.json`, the re-wear `_bench.json` and the per-pose
dump `_bench_perpose.json`. Held-out numbers come from `_held.json` and `_held_perpose.json`. The model is unchanged
since all of them were made.

| what the wearer feels | bench | held out |
|---|---|---|
| overhead reach (elev >= 140), taken / total | 8 / 28 | not probed held out (see "Not measured") |
| raised arm (elev 90-140), taken / total | 38 / 85 | - |
| reach by elevation (taken / total) | 0-60: 158/172, 60-90: 57/75, 90-120: 27/51, 120-140: 11/34, 140-160: 5/13, 160-200: 3/15 | - |
| taken poses with metal < 1 mm | 4 | 13 |
| taken poses with metal < 2 mm | 34 (29 workspace + 5 clip) | 72 |
| taken poses with metal < 3 mm | 147 | 334 |
| overhead taken poses with metal < 2 mm | 5 of 8 | - |
| contact poses | 4 | 17 |
| summed contact depth | 21.88 mm | 81.20 mm |
| deepest contact | 10.9 mm at workspace (15, 165, -60), overhead | 10.36 mm at workspace (45, 165, -30), overhead |
| presses deeper than 3 mm | 3 | 10 |
| lowest metal on a taken pose | 0.072 mm at (-60, 60, 105) | 0.331 mm |
| scored clip in-band 2-14 mm | 0.8993 | 0.8982 |
| unscored workspace in-band 2-14 mm (all / elev 90-140 / overhead) | 0.861 / 0.800 / 0.936 | - |

The four bench contacts are 10.9 and 5.56 mm (both overhead, elev 165), 4.52 mm at (0, 105, 15), and 0.89 mm at
(-15, 90, 45).

Other numbers:
- **Springs:** one clock spring force-closes the lobe follower and the roller-flank. It must now also close K below the
  old stop A, into a lobe dip 0.068 mm deep. No spring-torque, closure-force or R17 number exists for this row.
- **Stops:** stop A sits at the dip floor, and K is taken from -2.37 to 43.66 deg (dK_lim 43.8). The knee is taken
  over 54.2-96.7 deg, inside its 20-160 window.
- **Cuff twist:** not measured, because there is no R17 run.
- **Near-singular postures:**
  - The family reading, min(m_sub, m_eff) off rest, is 0.204 deg on the bench and 0.184 deg held out.
  - The verifier's coupled reading is 5.389 / 5.406 deg.
  - Under m_sub on every pose, 107 bench poses are under 5 deg, against the D=0 control's 106.
  - The horn pressure angle is 43.0 deg, at its 43 cap.
  - The bent arm clears hub K by 1.04 mm, against a 1 mm rule.
- **Complexity:** 20.25 (`tools/simplicity.py`, recomputed equal), the same as roller-longdyad. The change from 24.25 is a
  measurement change (knee loop freed, 3d9dc71).

### Paired comparisons (same poses; per-pose dumps reproduce every claim)

| comparison | wear | gap difference (negative: this design better) | 90 % interval | P(this better) | workspace taken only here / only there | contact only here / only there / both |
|---|---|---|---|---|---|---|
| vs own D=0 control | bench | -0.70 | [-1.83, +0.36] | 0.80 | 1 / 1 | 0 / 2 / 4 |
| vs own D=0 control | held out | **+1.10** | **[+0.56, +1.82]** | **0.000** | **0 / 12** | 0 / 0 / 17 |
| vs roller-longdyad | bench | -0.03 | [-0.82, +1.18] | 0.41 | 1 / 1 | 2 / 0 / 2 |
| vs roller-longdyad | held out | +0.34 | [-0.53, +1.58] | 0.21 | 11 / 12 | **7 / 0** / 10 |
| vs lowarm-kstop (new) | bench | -0.05 | [-0.64, +0.92] | 0.36 | 0 / 1 | 1 / 1 / 3 |
| vs lowarm-kstop (new) | held out | **+1.20** | **[+0.47, +2.24]** | **0.007** | **1 / 12** | 5 / 2 / 12 |

Sources: `docs/alignment/remeasure/dipped-law-groove-knuckle-3r_paired_controls.json` (first four rows, 2026-10-17) and
`docs/alignment/remeasure/dipped-law-groove-knuckle-3r_vs_lowarm-kstop-knuckle-3r_paired.json` (new; made with
`tools/alignment_paired.py compare`, 2000 bootstrap draws, from the dumps on file).

On the bench, this design ties all three. Held out, it is significantly worse than two of them, and it touches the
arm more often than all three.

## Findings

Each finding gives the pattern, the evidence, why the exo is not actually better, and the action. The full text is in
`docs/alignment/dipped-law-groove-knuckle-3r.findings.json`, and the ledger holds the entry.

The tool's checks:

| check | level | reason |
|---|---|---|
| held_out | ok | held out 24.07 vs bench 18.64 (+5.43), re-measured |
| fast_frozen | ok | self 15.39 -> verified 18.64 (+3.25) |
| near_touch | ok | plain 18.64, <1 mm 20.81, <2 mm 35.69, <3 mm 118.59; 17.05 points in the 1-2 mm shell (under the 25 line) |
| contact_depth | ok | bench 4 poses / 21.88 mm, held 17 / 81.20 mm; no depth of the new reference conecut-knee on file |
| dominance | ok | "no reference": the reference is now conecut-knee (18.28), which this row does not beat |
| continuity | ok | full flood 18.64, knn 20.32, bench graph 50.2 |
| **fold_margin** | **gamed** | min fold margin on file 0.184 deg (verify `_v_held_frozen.json` extra.th_margin.min) |
| idle | ok | K 42.5 deg, crank 17.7 deg, knee 42.5 deg spans |
| sampling | ok | sample- vs part-weighted in-band 0.899 vs 0.925; L1a has 8 samples |
| density | ok | roller sampled 2.22x the kit's density; at the kit's density bench 18.72, held 24.15 |
| complexity | ok | recomputed 20.25 = row |
| reporting | ok | row, verifier files and dashboard agree |
| judge_change | ok | no bench / judge / metric file in the 5 commits that touched the row |
| rules | ok | O20, margin >= 5 as recorded (the coupled reading), 0 passive translations |

The judgement findings:

1. **T3, gamed: the fold margin is read on the design's own terms.**
   - Evidence: the family reading fails 84 / 371 bench and 202 / 850 held-out poses at 0.204 / 0.184 deg, and every
     failing pose is dipped. The model waives m_sub on dipped poses, and the verifier's coupled reading (5.389 / 5.406)
     accepts the waiver. The D=0 control passes at 5.181.
   - Why the exo is not better: CLAUDE.md says "a different reading is the user's call, not the model's", and B1 is
     still open. The waiver still buys rank: it puts this row above roller-longdyad, which passes the family reading
     (5.181 / 5.031) and is better held out (23.73 vs 24.07; 10 vs 17 contacts).
   - Context, from the skeptic's measurement: under m_sub on every pose, this row and its control are alike (107 vs 106
     poses under 5 deg). The dip changes what holds K on those poses, from a dowel to a 0.068 mm spring-closed lobe dip;
     it does not change the geometry.
   - Action: the user's B1 ruling. Until then the row cannot be called verified, a winner or a leader.
2. **P1, gamed: the gain is in-sample, and the bench ranks this design above designs better on unseen poses.**
   - Evidence: held out, the dip is strictly dominated by its own D=0 control: 0 / 12 workspace discordance, the same
     17 contacts, +1.10 [+0.56, +1.82]. New this audit, against lowarm-kstop: a bench tie (-0.05), but +1.20 held out
     ([+0.47, +2.24], P 0.007), 12 workspace poses taken only by lowarm-kstop against 1, and 17 vs 14 contacts.
   - Action: no rank change on this number. If B1 rules for msub, the rule-consistent number is the D=0 control's
     (19.33 / 22.97).
3. **P4, watch:** the fold reading changed together with the design. The waiver is in the model (5d587f5 / c177c28),
   and the coupled reading is in the verifier (125be85 / 35afc38). The 8f69bd6 R17 gate change cannot touch this row,
   because it has no R17 run.
4. **G1, watch: the plain edge over roller-longdyad is metal moved toward the skin.**
   - Evidence: +0.03 plain against -2.59 at 2 mm (35.69 / 34 poses vs 33.10 / 30). Overhead under 2 mm: 5 of 8 vs 4 of
     8. Contact depth x1.33 bench and x1.63 held out.
   - Instrument note: the tool lost this comparison when its reference moved to the new lead. That is a change of
     reference, not of the design.
5. **NEW-contact-for-inband, watch: against roller-longdyad, the edge is +0.56 in-band points paid with -0.53 contact
   points.**
   - Held out, this row's contacts are a strict superset of the lead's: 7 / 0 / 10, with 10 vs 7 presses deeper than
     3 mm.
6. **T1, watch (report only):** re-worn and identical. 17.05 points live in the 1-2 mm shell. Near-2 is 35.69 bench and
   38.72 held out. Pose 203 sits at 0.477 mm, and the 0.07 mm pinch is unchanged.
7. **M5, watch: a spring-closed cam with no hold check.** No torque, closure force, friction or R17 number is on file,
   and no CAD exists for this row. The family pass line is mu ~0.15 (trimlug skeptic).
8. **NEW-sub-tolerance-feature, watch:** a 0.068 mm lobe dip, where 10 um of profile error moves K 0.35 deg (15 % of
   the floor). Through the dwell, K's rest rides on the drive chain's tolerance stack, not on a dowel.
9. **G4, watch:** the horn pressure angle is 43.0 against its 43 cap. The hub-K clearance is 1.04 mm against the 1 mm
   rule. The dip spends 2.4 deg of stretched stroke.
10. **NEW-preview-not-claim, watch: still unfixed after about 41 h.**
    - The preview module's `const P` has no dip parameters at all, and `law_mode` reads 'seg' against 'lin' in
      best_params. The motion graphic under this row's name is the D=0 mechanism.
    - Action: regenerate `docs/concepts/viz/concepts/dipped-law-groove-knuckle-3r.js` from best_params, then run
      `node docs/concepts/viz/test.mjs` and `thumbs.mjs`.
11. **S5, watch:** the knn flood costs +1.68 (20.32). This is family-wide.
12. **NEW-contact-cured-by-losing-pose, watch: half of the dip's bench contact gain is a pose it can no longer reach.**
    - Evidence: overhead pose 316 (60, 150, -105) is in contact on the control (-1.237 mm). The dip does not evaluate it
      at all, because the spent stroke truncates it. The contact share counts evaluated poses only, so not reaching an
      overhead pose scores 0.27 points better than reaching it touching. Neither is taken.
    - The dip also loses pose 313 (60, 120, -105), which the control takes in band, and target 182 stays in contact
      (-0.89 mm).
    - The skeptic raised this on 2026-10-17 as missed; it is confirmed here from the dumps.
13. **NEW-flag-not-on-doc, watch: verified text without the flag.**
    - The concept doc (line 166, linked from the dashboard row) says "Verdict: VERIFIED ... Level with the lead", with
      no ledger line. The row verdict also says "level with the lead", while the lead has been 0.36 ahead since
      2026-10-17 17:21.
    - HANDOFF section 3 shows complexity 24.25 (now 20.25).
    - The legacy `docs/dashboard/index.html` does not filter `alignment: gamed` before it gives its "verified" chip. It
      shows nothing for this row today, because the row is outside its top 6.
    - Action for the lead: add the ledger line to the doc's verdict and the row's verdict, refresh HANDOFF's
      complexity, and filter gamed rows on the legacy page (or retire that page).

### Proposed catalogue entries (new patterns)

- **T6. Contact cured by losing the pose.**
  - Looks like: a design's contact count falls against its reference because poses the reference reaches in contact
    are no longer evaluated here.
  - Why not better: the wearer still raises the arm there. Now the exo cannot follow, instead of touching.
  - Detect: paired dumps; count the reference's contact poses that are `ev` false in the design, and report them next
    to the contact share.
  - Here: pose 316 of this row against its D=0 control.
- **R5. A flagged record shown as verified outside the board.**
  - Looks like: the board shows "Flagged", but the concept doc, the row verdict or a legacy page still read "VERIFIED"
    or "level with the lead".
  - Detect: grep the concept doc and the row verdict of every ledger-gamed row for a ledger line.
  - Here: this row's doc line 166.

## Proposals (not applied; measurement or rule changes for the user or the lead)

- **B1 (carried): rule on m_sub for a K slaved from q2.**
  - If "msub applies": this row's dip is inadmissible on 84 bench and 202 held-out poses, and its rule-consistent
    number is the D=0 control's (19.33 / 22.97).
  - If "coupled reading": this row keeps 18.64, but it still loses held out to its control, to roller-longdyad and to
    lowarm-kstop (P1).
  - The skeptic's measurement says the physical question is B2, not the geometry.
- **B2 (carried):** if a coupled reading is adopted, a spring-closed slaving needs a closure-force check at the worst
  arm load. This row has none on file.
- **B4 (carried, a tightening, so the user's call):** inside the 1-point tie band, a row may rank above another only if
  it touches no more poses, paired, held out.
  - Effect measured here: this row would rank behind roller-longdyad (7 / 0) and lowarm-kstop (5 / 2).
  - Not measured on the other verified rows in this time box.
- **B6 (new, reporting only, no score moves):** every ledger-gamed row's concept doc and row verdict carry the ledger
  line, and the legacy page filters `alignment: gamed`. Effect: today, this row's doc and verdict text.
- **B7 (new, reporting only):** report the T6 count (reference contact poses not evaluated here) next to the contact
  share of every paired control comparison. Effect: this row 1 of the 2 bench contacts it removes; other rows not
  measured.

## Not measured, and why

- **Held-out wear probe** (overhead reach taken / total held out, unscored workspace in-band held out): not run. The
  probe's adapter for this row exists only for the bench wear. The held-out floors and contact depths come from the
  re-wear and the per-pose dump instead.
- **Cuff twist, spring hold, preload** (R17 / dynamics): not measured. This row has no CAD and no dynamics model, and
  building one is outside an audit.
- **The farm was not used.** The CPU budget line was crossed (CLAUDE.md decision 7), and every re-wear here took
  2-4 min locally, as 1 niced process.
- **The paired bootstrap against conecut-knee** (the current lead): not run. This row does not beat it on the bench,
  so it cannot rank above it.

---

## Skeptic (2026-10-17 06:20-06:50 UTC, ledger entry 2026-10-17T06:48:22Z, `by skeptic`, run `skeptic:dipped-law-groove-knuckle-3r`)

**Final verdict (computed by `tools/alignment_ledger.py`): GAMED.** All 12 reasons were upheld and none was refuted.
The rulings with their full evidence are in `docs/alignment/dipped-law-groove-knuckle-3r.rulings.json`.

How the skeptic worked:
- Every count was re-derived from the per-pose dumps and the verifier JSONs.
- One local re-run was added: `tools/alignment_msub_rest_probe.py` (new).
  - It loads the verifier and the model unchanged, and wraps `th_margin` to record m_sub on every taken pose, with K at
    rest as well as off it.
  - It ran on the claim and on its D=0 control: Bench(110,360) exact, frozen, CB_EXACT=1, OMP_NUM_THREADS=1, nice, 2
    processes.
  - It reproduces 18.64 and 19.33, and the fold minima 0.204 and 5.181.
  - Outputs: `docs/alignment/remeasure/dipped-law-groove-knuckle-3r_skeptic_msub_bench.json` and
    `..._D0control_skeptic_msub_bench.json`.
- No farm was used.

### Rulings

- **dominance (watch): upheld.**
  - The gap is 18.64 against 18.67 plain, and near-2 is 35.69 against 33.10, on the same harness.
  - Taken poses with metal under 2 mm: 34 against 30.
  - Overhead taken poses under 2 mm: 5 of 8 against 4 of 8.
- **fold_margin (gamed): upheld.**
  - The 0.184 (held out) and 0.204 (bench) readings are correct. The formula is the lead verifier's, copied unchanged,
    and TH `fold_min` 5 is applied to its minimum.
  - Measured context, which is not a refutation (see below): the dip does not create the near-fold geometry.
- **T3 (gamed): upheld.** Every number re-checks, and so does every rule citation. Two more points:
  - Round 10 itself killed the cam-slaved two-rise lobe on msub 2.14 (`round10_ideation.md` line 605). The family
    applied msub to a cam-slaved K in this very round.
  - Small corrections that change nothing:
    - the phrase "spec correction (2)" is not in the model file, but the waiver is in its docstring;
    - the coupled reading's code entered in the WIP commit 125be85, and its outputs in 35afc38.
- **P1 (gamed): upheld, and re-derived.**
  - The control differs only in dipD (1.0 against 0.0).
  - Held out: 12 workspace poses are taken only by the control and 0 only by the dip. The 17 contact poses are the same
    in both.
  - Several of the 12 lost held-out poses are in band on the control: 2.19-6.66 mm.
- **P4 (watch): upheld.** The waiver is in the model (5d587f5 / c177c28). The coupled code is in the verifier (125be85),
  with its outputs in 35afc38. No kit, bench or judge file changed.
- **NEW-contact-for-inband (watch): upheld.**
  - Contact: 4 against 2 on the bench, and 17 against 10 held out.
  - Held-out discordance: 7 only here, 0 only in the lead.
  - Summed depth held out: 81.20 against 49.88 mm.
- **T1 (watch): upheld.**
  - Pose 203 sits at 0.477 mm.
  - 17.05 points of the gap are in the 1-2 mm shell.
  - Taken poses under 3 mm: 147 / 334, against the lead's 133 / 273.
- **M5 (watch): upheld.** No closure-force, preload or R17 number is on file. One part of the reason is not specific to
  the dip: "free on a sub-chain 0.18-0.20 deg from its fold if the follower lifts". The control's K-at-rest poses go down
  to m_sub 0.0 with K held by the same spring.
- **NEW-sub-tolerance-feature (watch): upheld.**
  - The lobe dip is 0.068 mm, and K moves 0.35 deg per 10 um against a 2.37 deg floor.
  - Stop A is at -3.0 deg, so K's rest through the dwell rides on the lobe.
- **G4 (watch): upheld.**
  - The horn pressure angle is 43.0 against its 43 cap, and the hub-K clearance is 1.04 mm against 1 mm. Both are inside
    their rules, and the cap is family-wide (the control reads 42.7 and is also limited by `pressure_horn`).
  - The 2.5 deg of stroke the dip spends is a real cost: it is the 12 held-out poses and bench pose 316.
- **NEW-preview-not-claim (watch): upheld, and sharper than reported.** The preview module's parameters hold no dip at
  all (see the missed list).
- **S5 (watch): upheld.**
  - Full flood: 18.64, 0 poses dropped. Knn flood: 20.32, 6 dropped. Bench-graph flood: 50.2, 112 dropped.
  - The lead reads 18.67 / 20.34 / 50.29, so this is family-wide and does not separate the row from the lead.

### Measured context for proposal B1 (the msub ruling)

The sub-chain margin m_sub is already low on these poses before the dip, with K at rest on its stop.

| | the claim (dipped) | the D=0 control |
|---|---|---|
| taken bench poses with K at rest | 121; m_sub min 0.0, 23 under 5 deg | 204; m_sub min 0.0, median 4.77, 106 under 5 deg, 50 under 1 deg |
| dipped taken poses | 84; m_sub 0.204-4.86, median 1.42 | none |

- The control passes the family reading (5.181) only because that reading does not read m_sub while K sits on stop A.
- Of the 84 dipped bench poses:
  - 83 are taken by the control with K at rest, and m_sub is already under 5 deg there (min 0.205, median 1.675).
  - The dip lowers m_sub by only 0.00-0.33 deg (median 0.11).
- The lowest readings sit at the dip's edge. For example, m_sub is 0.204 at dK -0.008 deg, a pose 0.008 deg away from a
  rest pose that the family reading passes.
- So the dip does not move the wearer's arm toward a singular posture. What changes on those 84 poses is what holds K:
  a dowel stop A becomes a spring-closed, 0.068 mm lobe dip.
- What this means for the user's ruling:
  - The physical question is B2 (does the slaving hold under load), not the geometry.
  - Until the user rules, the claim still rests on a reading the design chose for itself, so the verdict stands.

### Missed by the auditor (for the next audit; not counted in this verdict)

1. **Half of the dip's bench contact gain is a pose it no longer reaches.**
   - The two contacts the dip "removes" against its control are:
     - pose 203 (0, 90, 45), cleared to 0.477 mm;
     - pose 316 (60, 150, -105), overhead. The control reaches it at -1.237 mm (contact). The dip does not evaluate it
       at all (`ev` false): the stroke it spends truncates the pose.
   - `CB.report()` takes the contact share over evaluated poses only. So losing an overhead pose scores better than
     reaching it with metal on the arm.
   - The dip also loses pose 313 (60, 120, -105), which the control takes at 3.77 mm, in band. That is the 1-for-1 swap
     of taken workspace poses: an in-band raised-arm pose for one at 0.48 mm.
   - Evidence: the `bench_perpose` dumps, poses 203, 313 and 316.
   - Proposed catalogue entry, "contact cured by losing the pose". Detect: paired, the poses that are in contact in the
     reference and not evaluated here.
2. **The dashboard motion preview shows no dip at all**, not th_c 50 / w 8.
   - In `docs/concepts/viz/concepts/dipped-law-groove-knuckle-3r.js`, `const P` (line 11) has no `dipD`, `dip_thc`,
     `dip_w` or `dip_ref`.
   - `dipOf()` (line 22) returns 0 when `P.dipD` is undefined.
   - `P` also carries `law_mode` 'seg' (`best_params` say 'lin'), and it lacks `g`, `beta`, `r_c` and `s_arm`.
   - The motion preview in `docs/dashboard/data/motion.json` is built from this module by `thumbs.mjs`, so it shows the
     D=0 mechanism under the dipped row's name.
3. **Of the dip's two named targets, only one clears.** Bench pose 182 (-15, 90, 45) is still in contact with the dip:
   -0.89 mm, against -1.675 mm for the control. Only pose 203 clears, and it ends at 0.477 mm.

### Not obtained by the skeptic

- The paired bootstrap was not re-run. The strict 0 / 12 discordance held out is enough for "strictly dominated".
- There is no held-out m_sub-at-rest probe; this audit covers the bench only.
- There is no spring-closure or R17 run.

## Skeptic (2026-10-18 22:55-23:20 UTC, ledger entry 2026-10-18T23:15:31Z, `by skeptic`, run `skeptic:dipped-law-groove-knuckle-3r`)

**Final verdict (computed by `tools/alignment_ledger.py`): GAMED.** All 14 reasons of the 22:14 audit were upheld and
none was refuted. The rulings with their full evidence are in `docs/alignment/dipped-law-groove-knuckle-3r.rulings.json`.

How the skeptic worked:
- Every number was re-derived from the rawest files on record: the verifier JSONs, the per-pose dumps, the re-wear
  `deep` blocks, the bench probe, the rows and the git history. The model, its verifier, `tools/concept_bench.py` and
  `tools/concept_kit.py` are unchanged since the dumps were made (git log), so no re-wear was needed.
- The paired bootstraps were re-run with `tools/alignment_paired.py` `compare_sets` on the dumps on file: two new
  seeds, 4000 draws each, against lowarm-kstop, the D=0 control and roller-longdyad. Output went to the scratchpad only;
  no remeasure file was rewritten.
- No farm, 1 niced local process, no file outside this report, its rulings and the ledger was written.

### Rulings

- **fold_margin (gamed): upheld.** `_v_held_frozen.json` extra.th_margin {min 0.184, lt5 202 of 850, all dipped,
  coupled 5.406}; bench {min 0.204, lt5 84 of 371, coupled 5.389}. TH `fold_min` 5.0 (tool line 64), gamed below 4.95
  (line 544), applied to the minimum reading on file. B1 is still open (HANDOFF line 326, ROUNDS.md line 5462).
- **T3 (gamed): upheld.** The numbers re-check, and the msub waiver is still in the model docstring (`git log -S` ->
  5d587f5). The D=0 control reads 5.181 / 0 under 5. roller-longdyad reads 5.181 / 5.031 and 23.73 held out (re-worn
  22:27 today). No user ruling on B1 is in CLAUDE.md.
- **P1 (gamed): upheld, re-run.**

  | vs | wear | diff (seed 1 / seed 7) | CI90 | P(this better) | ws taken only here / only there | contact here / there / both |
  |---|---|---|---|---|---|---|
  | lowarm-kstop | bench | -0.05 | [-0.62, 1.00] / [-0.65, 0.97] | 0.379 / 0.365 | 0 / 1 | 1 / 1 / 3 |
  | lowarm-kstop | held | **+1.20** | [0.50, 2.20] / [0.48, 2.22] | **0.004 / 0.005** | 1 / 12 | 5 / 2 / 12 |
  | own D=0 control | held | **+1.10** | [0.56, 1.83] / [0.56, 1.82] | **0.000** | 0 / 12 | 0 / 0 / 17 |

  Every dump reproduces its claim (dip 18.63 / 24.07, lowarm-kstop 18.69 / 22.88, control 19.33 / 22.98). The
  lowarm-kstop dumps are the per-pose worst of its sided play wears, so the comparison, if anything, handicaps the
  reference.
- **P4 (watch): upheld.** The waiver is in 5d587f5 / c177c28 and the coupled reading in 125be85 (then 1dbb353). Kit and
  bench last changed 2026-10-16 (17d6027). The row has 0 R17 hits.
- **G1 (watch): upheld.** Near-2 is 35.69 / 34 poses against 33.10 / 30 (roller re-worn 22:24 today), with plain
  +0.03. Contact depth recomputed from the claim dumps: 21.88 vs 16.46 mm on the bench, 81.20 vs 49.88 mm held out.
  Overhead under 2 mm: 5 of 8 (probe `ws_overhead140.poses_floor_lt2`).
- **NEW-contact-for-inband (watch): upheld.** Held out, contacts are 7 here / 0 there / 10 both. Presses deeper than
  3 mm: 10 vs 7 held out, 3 vs 2 on the bench.
- **T1 (watch, report only): upheld.** Pose 203 cmin 0.477 mm; lowest taken pose 139 at 0.072 mm; 17.05 points in the
  1-2 mm shell.
- **M5 (watch): upheld.** The row has 0 hits for r17 / torque / preload / friction / dynamics. Its "closure" hits are
  kinematic (closure_mm 0.0, lobe_cam_closure_deg 0.0).
- **NEW-sub-tolerance-feature (watch): upheld.** lobe_dip_mm 0.068, K_deg_per_10um 0.35, dip floor -2.37, dK_neg -3.0.
  No tolerance wear is on file (see missed item 1).
- **G4 (watch): upheld.** pa_horn_max_taken 43.0 (cap 43), clear_hubK_min 1.04 (rule 1 mm), dK_lim 43.75 against the
  control's 46.25.
- **NEW-preview-not-claim (watch): upheld.** The `.js` still has no dip keys and law_mode 'seg'. Its last commit is
  8a524ce (2026-10-17 04:42).
- **S5 (watch): upheld.** knn 20.32 / 6 dropped against full 18.64 / 0, over the 1-point watch line. The cost is
  family-wide.
- **NEW-contact-cured-by-losing-pose (watch): upheld, re-derived.**
  - Control contact poses: [182, 203, 205, 237, 264, 316]. Dip: [182, 205, 237, 264].
  - Pose 316 is ev false on the dip. Evaluated poses: 375 vs 377.
  - The contact share is 1.067 % vs 1.592 % (0.525 points). With 316 counted as contact it would be 1.330 %, so 316
    carries 0.263 points, half of the gain.
  - Pose 313 (control taken at 2.276 mm, in band) is lost as well.
- **NEW-flag-not-on-doc (watch): upheld.**
  - The concept doc line 166 reads "VERIFIED (not refuted) ... Level with the lead". `grep ledger|gamed|Flag` on it
    returns 0 hits.
  - HANDOFF line 127 shows complexity 24.25, while the row reads 20.25.
  - `docs/dashboard/leader.js` line 73 ranks by v_gap with no alignment filter, while morphs.json carries
    alignment 'gamed' for this row.

### Missed by the auditor (for the next audit; not counted in this verdict)

1. **The bench order over lowarm-kstop compares a nominal wear with a worst-of-tolerance wear.**
   - lowarm-kstop's 18.69 is the per-pose worst of its sided K-play wears. Its +0.264 deg side alone is 18.60, below
     this row's 18.64 (rows/lowarm-kstop-knuckle-3r.json step0 {plus_0264 18.60, minus_0210 18.68, worst 18.69}).
   - This row is worn nominal only. The row has 0 hits for 'play' or 'sided', although its own K rest moves 0.35 deg
     per 10 um of lobe error through the dip (verify extra.lobe_tol). That is more than the play lowarm-kstop wears.
   - So the 0.05 bench edge rests on the reference wearing its tolerance while this row does not.
   - Proposal (a measurement change, the lead's or the user's call): wear dipped-K rows at +-10 um of lobe, i.e.
     +-0.35 deg of K on dipped poses, and claim the per-pose worst, as lowarm-kstop does.
   - Not measured here: the model has no K-offset hook. Scaling dipD re-synthesises the drive, so it is not a
     tolerance.
2. **No held-out continuity flood.** `_v_held_frozen.json` has no `connected` key. The held 24.07 and every held
   paired comparison above are static-set numbers. This is family-wide, so it does not change any ordering here.
3. **The documented best config is not the claimed one.** The concept doc (Files, line 161-162) and the preview's
   header (line 7) say "dipD 1, th_c 50, w 8". The row's best_params read dip_thc 53, dip_w 12. This is a reporting
   mismatch on top of NEW-preview-not-claim.

### Not obtained by the skeptic

- A tolerance wear of the dip (missed item 1): it needs a K-offset hook in the model, which is outside an audit.
- A held-out flood, and any R17 or spring-hold number: no CAD or dynamics model exists for this row.
