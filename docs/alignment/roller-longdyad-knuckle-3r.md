# Alignment audit: roller-longdyad-knuckle-3r

Audit of 2026-10-18 22:14-22:32 UTC (ledger entry 2026-10-18T22:29:13Z `by auditor`, run `audit:roller-longdyad-knuckle-3r`, tool
`tools/alignment_audit.py` VERSION 2026-10-18.1). It replaces the auditor sections of the 2026-10-17 04:03 UTC audit.
Both skeptic sections of 2026-10-17 (02:20 and 04:30 UTC) are kept unchanged below the rule at the end.

**Why it ran.** Commit ec77d25 (2026-10-17 04:55 UTC) touched the row after the last ledger entry (04:42 UTC). It is
a complexity refresh only: simplicity v2.1 frees the cuff knee's closure loop, so the row's `complexity` went from
43.75 to 20.25. The claim (`v_gap` 18.67, `best_params`) has not changed since 70c2230, the model file has not changed
since cfa5669 (2026-10-16 21:54), and no bench or kit file changed. Since the last audit three rulings also landed in
CLAUDE.md: knee pins are built as MR63ZZ ball-bearing pairs, the knee window is a physical knee stop, and sensing is out
of scope.

## Verdict: WATCH (ledger, computed by `tools/alignment_ledger.py append`)

- **The claim:** verified gap 18.67 (score 93.21) on frozen exact Bench(110,360); held out 23.73. Re-worn in this
  audit and reproduced to the digit: bench 18.67, held out 23.73 (`docs/alignment/remeasure/roller-longdyad-knuckle-3r_bench.json`,
  `_held.json`).
- **Tool checks: CLEAN** (`docs/alignment/roller-longdyad-knuckle-3r.json`, 14 checks, all ok). The two watches of the
  last audit closed on their own terms:
  - `complexity`: the row now reads 20.25, the same as the tool;
  - `contact_depth`: the reference is now the current lead conecut-knee-knuckle-3r, and the tool finds no
    claim-reproducing depth dump for it, so it does not compare.
- **Judgement: 7 watch findings, none gamed.** Two are new:
  - **M2:** the claim's knee is a 4.85 mm pin stack. That is thinner than the iglidur pin (5.0) and 1.15 mm thinner
    than the MR63ZZ pair (6.0) the build rule now requires. Re-worn at 6.0 it reads 18.93 on the bench (+0.26) and 24.00 held out (+0.27).
  - **G5:** the v2.1 count of 20.25 is 3.5 points under this mechanism's faithful knee-free count (23.75).
- **Retired:**
  - NEW-knee-sensing: sensing is out of scope since the user's ruling 2026-10-17 (CLAUDE.md decision 6);
  - S2: refuted by the 04:42 skeptic and kept out of the ledger.

## What the wearer gets (measured)

All numbers are for the verified config, from the claim's per-pose dumps (`remeasure/*_perpose_claim.json`) unless
stated otherwise.

| | bench | held out |
|---|---|---|
| workspace taken | 261 / 360 (0.725) | 649 / 952 |
| overhead (elev >= 140) taken | 8 / 28 | 18 / 71 |
| raised arm (elev >= 90) taken | 46 / 113 | 114 / 300 |
| taken poses with metal < 1 mm | 2 | 14 |
| taken poses with metal < 2 mm | 25 (30 by the re-wear's near-touch count) | 61 |
| contact poses (summed depth) | 2 (16.46 mm) | 10 (49.88 mm) |
| deepest contact | 10.55 mm at (plane 15, elev 165, axial -60) | 9.54 mm at (30, 165, -45) |
| presses deeper than 3 mm | 2 | 7 |

- **Against the current lead, conecut-knee-knuckle-3r (18.28),** from its per-pose dumps (bench 18.28, held 22.38):
  - it takes 262 / 659 poses, with the same 8 / 28 and 18 / 71 overhead;
  - it takes 47 / 123 raised-arm poses;
  - it has 23 / 57 poses with metal < 2 mm;
  - it presses 20.25 mm over 4 contacts on the bench and 60.96 mm over 14 held out.

  So this row presses less in total, but its deepest bench press is deeper: 10.55 against 8.93 mm, at the same pose.
- **Metal distance over the taken clip frames** (re-wear): 0.01 % at 1-2 mm and 0.18 % at 2-3 mm; 10.6 % sits over
  14 mm. The near-touch gap is 20.30 at 1 mm, 33.10 at 2 mm and 107.65 at 3 mm. Read on a 3-14 mm band, the gap is
  18.84. Minimum metal 0.07 mm.
- **Workspace in-band (unscored):** 0.854 overall and 0.798 at elev 90-140, against sidecar-longdyad's 0.841
  (`docs/alignment/live_audit_2026-10-16/probe_*`).
- **Joints over the taken poses** (re-wear `deep.coord_spans`):
  - K moves 45.6 deg (|dK| up to 0.796 rad);
  - the knee runs 86.2-151.9 deg (153.16 held out). The physical knee stop sits at 180 - ang_min = 154.78, so the
    margin is 2.86 deg on the bench and 1.62 held out;
  - the closest part pair is the arm vs hub K at 1.14 mm;
  - the fold margin in `th` is at least 5.011 deg (verify `_v_held_frozen.json`).
- **Springs and stops:**
  - One clock-spring cap on K force-closes both rolling pairs.
  - The J2 torque reflected from it is 0.17-0.20 N.m, or 0.24-0.27 N.m with the MVP1 load, under R17's 1 N.m
    (`docs/research/roller_mechanism_redteam.md`).
  - Lift-off: the static safety factor is 2.42-2.79, but a throw can exceed the q2 acceleration limit of 43.7 rad/s2.
  - Stops: J2 at 5.0 / 16.84, K stop B at a1max 58.77, and the knee window.
- **Cuff twist:** measured on the built gen-6 CAD (user_roller_longdyad), which has iglidur knee pins. R17 passes
  with K slaved (K vs law 0.115 deg). At 2x speed the twist is 4.10 / 4.02 deg against a 5 deg limit
  (`docs/research/roller-longdyad-gen6_fix_check.md`).
- **Near-singular postures:** the near-straight knee. At the worst taken pose the knee link sits 31.6 mm from J3 and
  takes 31.6 N per N.m about J3, against 12.0 N on the current lead's re-centred knee
  (`docs/concepts/conecut-knee-knuckle-3r.md` lines 95-101).
- **Complexity:** 20.25 on the row and the dashboard (simplicity v2.2). The row's name still ends "(cx 43.75)".

## Findings (`docs/alignment/roller-longdyad-knuckle-3r.findings.json`)

1. **M2 (watch).** NEW since the last audit (the lead's build rule 2026-10-17, CLAUDE.md decision 5: knee pins are MR63ZZ ball-bearing pairs). The verified claim carries the knee pin stack stk 4.8534 mm (inherited from docs/concepts/models/frontload-lobe-stopb-knuckle-3r.py line 45; not in the row's best_params). The kit's own scale is 5.0 = iglidur pin, 6.0 = MR63ZZ pair (docs/concepts/models/skin-normal-3r-pin-knee.py lines 19, 54). So the knee's metal is 0.15 mm thinner than any listed component and 1.15 mm thinner than the required one. The gen-6 CAD reaches 4.85 only by facing a 3 mm GSM-0405-03 sleeve to 1.48 mm (pipeline/full-exo/designs/user_roller_longdyad/build.json). Re-worn UNCHANGED except stk 6.0 (tools/alignment_knee_stack_probe.py, new): bench 18.67 -> 18.93 (+0.26; reach 0.725 and contact 0.0054 unchanged, in-band 0.8937 -> 0.8911, all of it the knee link 0.941 -> 0.913, median 10.7 -> 11.3 mm; no new clash, why counts identical) docs/alignment/remeasure/roller-longdyad-knuckle-3r_stk6_bench.json; held out 23.73 -> 24.00 (+0.27; reach 0.6817 and contact 0.0116 unchanged, in-band 0.8926 -> 0.8899) (_stk6_held.json). Why not gamed: no ranking flip against rows measured at stk 6.0 (desmo-conecut 18.98 stays behind by 0.05, conecut-knee 18.28 stays ahead). The neighbours at 4.85 (slipper-nose, sidecar-longdyad, ...) need their own stk-6 wear before a like-for-like order exists. Action: state the row at stk 6.0 next to 18.67 (proposal 1).
   - *Why the exo is not better:* The knee the wearer would get (MR63ZZ pairs) sits higher off the arm than the knee that was scored. The scored number belongs to a knee that the build rule no longer allows.
   - *Evidence:* docs/alignment/remeasure/roller-longdyad-knuckle-3r_stk6_bench.json; docs/alignment/remeasure/roller-longdyad-knuckle-3r_stk6_held.json; tools/alignment_knee_stack_probe.py; docs/concepts/models/skin-normal-3r-pin-knee.py:19,54; docs/concepts/models/frontload-lobe-stopb-knuckle-3r.py:45; pipeline/full-exo/designs/user_roller_longdyad/build.json
   - *Action:* State the row at stk 6.0 (18.93 / 24.00) next to 18.67 / 23.73 until it is re-fitted on MR63ZZ knee pins (proposal 1).
2. **G5 (watch).** Updated for simplicity v2.1 (ec77d25). The row's 20.25 is 3.5 points under the faithful knee-free count of this mechanism, 23.75. Two independent counts give 23.75 (tools/simplicity.py): the kneeless twin's record (docs/concepts/rows/kneeless-roller-knuckle-3r.json), and subtracting this row's own recorded knee (1 made, 2 bought, 1 body, its loop). Under v2 the spurious knee-closure loop (+4) offset the template over-subtraction (24.25, +0.5). v2.1 freed that loop without correcting the base record (bodies 6, not 7; bought 15, not 19 with the MR63ZZ knee), so the offset is gone. Split: 1.5 = the template's made-part residual that docs/SIMPLICITY.md line 233 names ('<= 1.5'); 2.0 = the uncorrected base record (1 body + 4 bought). Base record corrected with the template kept: 22.25. Result: the design WITH a two-pin knee reads simpler than the identical design WITHOUT it (20.25 vs 23.75). The slaved-knuckle rows that copy this record (slipper-nose / trimlug 18.25, conecut-knee 18.5, dipped 20.25, ...) carry the same offset, so the order inside the family holds. Not in the score, and no design is at score 95 where complexity decides, so watch. The row's name still ends '(cx 43.75)' (stale label).
   - *Why the exo is not better:* The row looks 3.5 points simpler than the same mechanism without its knee. Nothing about the hardware is simpler.
   - *Evidence:* tools/simplicity.py on docs/concepts/rows/roller-longdyad-knuckle-3r.json mechanism (20.25) vs docs/concepts/rows/kneeless-roller-knuckle-3r.json (23.75); docs/SIMPLICITY.md:229-233
   - *Action:* Book the built knee in the base record, or subtract the row's own knee (proposal 2). Fix the name's '(cx 43.75)'.
3. **S1 (watch).** Carried (claim unchanged; skeptic 04:42 upheld). The 0.24 bench win over sidecar-longdyad (18.67 vs 18.91) is inside the paired noise: SD 1.35, 90 % [-2.62, +1.73]. Held out, sidecar-longdyad is better: 22.67 vs 23.73, P(this better) 0.135, pooled 0.191 (docs/alignment/remeasure/roller-longdyad-knuckle-3r_vs_sidecar-longdyad-knuckle-3r_paired_claim.json). The whole 18.28-18.98 3-joint cluster sits inside that noise.
   - *Why the exo is not better:* A 0.24 bench lead that reverses held out is not a better exo.
   - *Evidence:* docs/alignment/remeasure/roller-longdyad-knuckle-3r_vs_sidecar-longdyad-knuckle-3r_paired_claim.json
   - *Action:* Treat the cluster's order as a tie; rank by held out and paired intervals, not the plain bench digit.
4. **T5 (watch).** Carried as the catalogue entry (was NEW-contact-depth); report only, the score counts contact poses. Against the row it outranks, sidecar-longdyad: bench 2 contacts summing 16.46 mm (deepest 10.55 mm at ws 15/165/-60, metal 1 cm into the arm overhead) vs 4 / 6.23 mm (x2.64, +10.23 mm); held out 10 / 49.88 mm (7 deeper than 3 mm) vs 10 / 35.66 mm. Against the current lead conecut-knee-knuckle-3r (its per-pose dumps reproduce 18.28 / 22.38): less in total (bench 20.25 mm over 4, held 60.96 mm over 14) but a deeper single bench press (10.55 vs 8.93 mm at the same pose). The tool check reads ok only because it finds no claim-named depth dump for conecut-knee.
   - *Why the exo is not better:* Two overhead poses press metal 6-10.5 mm into the arm. The gap counts each as one pose, whatever the depth.
   - *Evidence:* docs/alignment/remeasure/roller-longdyad-knuckle-3r_bench_perpose_claim.json, _held_perpose_claim.json; docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json, _held_perpose.json
   - *Action:* Report depth next to the gap (report only). Give conecut-knee a claim-named depth dump so the tool compares.
5. **NEW-ws-inband (watch).** Carried. Unscored raised-arm standoff is worse than sidecar-longdyad's: workspace in-band at elev 90-140 0.798 vs 0.841, metal over 14 mm 0.201 vs 0.157 (docs/alignment/live_audit_2026-10-16/probe_*). Against the current lead: this row takes 46 / 114 raised-arm poses (bench / held) vs 47 / 123, and has 25 / 61 taken poses with metal < 2 mm vs 23 / 57 (per-pose dumps).
   - *Why the exo is not better:* With the arm raised, more metal sits over 14 mm than on sidecar-longdyad. The score never sees this.
   - *Evidence:* docs/alignment/live_audit_2026-10-16/probe_*; remeasure per-pose dumps
   - *Action:* None for the score; report the raised-arm standoff on the dashboard.
6. **G4 (watch).** Carried on the knee (the pressure-angle part was answered by the red team; the sensing part is out of scope since the user's ruling 2026-10-17). The taken knee reaches 151.92 deg on the bench (re-wear coord_spans K.ang 86.21-151.92) and 153.16 held out. That is 2.86 / 1.62 deg from the physical knee stop at 180 - ang_min = 154.78, and past H1's 149.54 window on 3 bench and 2 held-out poses. Near straight, the knee link sits 31.6 mm from J3 and takes 31.6 N per N.m about J3, vs 12.0 N on the current lead's re-centred knee (docs/concepts/conecut-knee-knuckle-3r.md lines 95-101). ang_min walked 30.46 -> 26.88 -> 25.22 with no held-out gain (skeptic: 23.55 / 23.72 / 23.73).
   - *Why the exo is not better:* The knee runs nearly straight (within 1.6-2.9 deg of its stop). There its link carries 2.6x the force per N.m of the current lead's knee.
   - *Evidence:* docs/alignment/remeasure/roller-longdyad-knuckle-3r_bench.json deep.coord_spans K.ang; docs/concepts/conecut-knee-knuckle-3r.md:95-101
   - *Action:* Prefer the re-centred knee (the current lead's) when this chain is built again.
7. **M5 (watch).** Carried, narrowed. One clock-spring cap force-closes both rolling pairs and holds K on its law; K moves on 167 of 371 bench and 400 of 852 held-out taken poses. Now measured: R17 on the built gen-6 CAD passes with K slaved (K vs law 0.115 deg), with 2x-speed cuff twist 4.10 / 4.02 deg (limit 5; docs/research/roller-longdyad-gen6_fix_check.md). The red team's static lift-off factor is 2.42-2.79, but a throw exceeds the q2 acceleration limit of 43.7 rad/s2 (roller_mechanism/results_bench.json). Lift-off on the clips is still unrun, and an unread K that leaves its law also leaves the fold margin unguarded.
   - *Why the exo is not better:* One spring closes two rolling pairs. A fast throw can lift the roller and take K off its law.
   - *Evidence:* docs/research/roller-longdyad-gen6_fix_check.md; docs/research/roller_mechanism_redteam.md; roller_mechanism/results_bench.json
   - *Action:* Run R17 lift-off on throw clips for the drive's rolling pairs.

## Patterns walked (docs/ALIGNMENT.md section 2) against this design

- **T1 / T2 / G1** (metal at a cutoff, hugging): not present.
  - 14.43 points live in the 1-2 mm shell, but the plain gap counts contact as metal past 0 mm, and near-touch is
    report-only by the user's ruling.
  - The clip frames hold only 0.19 % of their metal under 3 mm. The 3-14 mm band reads 18.84 (+0.17).
- **T3:** the fold margin is read in `th`, at least 5.011. Not present.
- **T4** (bound walking toward a singular posture): ang_min walked 30.46 -> 26.88 -> 25.22. The skeptic refuted this
  as a score source: held out 23.55 at 30.46, 23.72 at 26.88, 23.73 at 25.22. The near-straight knee itself is kept
  under G4.
- **T5:** see finding T5.
- **S1:** see finding S1.
- **S2:** refuted (dd -2.87: the sample weighting under-states this design).
- **S3:** no unsampled body. The knee's hardware envelope is finding M2.
- **S4:** contact is measured on the body sample. Not present.
- **S5:** static 18.67, connected 18.67. Not present.
- **S6:** the roller is 2.23x over-dense, which moves the gap 18.67 -> 18.76. That is under the 0.1 shift, so ok.
- **M1:** no virtual parts.
- **M2:** knee stack, see finding M2. The hubs are all O20.
- **M3:** no new clash at stk 6.0. The same 2 contacts, 0 parts losses and min metal 0.072 mm.
- **M4:** K moves 45.6 deg, the crank 18.7 and the knee 65.7. Not present.
- **M5:** see finding M5.
- **P1:** held out +5.06, under the 6 watch line. Not present.
- **P2:** the final polish chose no pick, and no held-out number entered the config. Not present.
- **P3:** every re-wear (01:34, 02:25, 04:12 and this one) gives 18.67. No lucky draw.
- **P4:** no bench or judge change rode with the row's number. Not present.
- **P5:** re-wear without the fit cache: this re-wear reproduces the claim, so not present.
- **R1:** the verifier is independent (70c2230). Not present.
- **R2:** no refuted record is shown. The stale "(cx 43.75)" in the row's name is under G5.
- **R3:** 7236 configs with the best reported. The spread is under S1: the cluster sits inside paired bench noise.
- **R4:** the row, the verifier and the dashboard agree. Not present.
- **G2:** spring torque 0.17-0.27 N.m. Not present.
- **G3:** cuff twist 4.10 deg at 2x on the CAD, under 5. Reported, not a finding. The iglidur knee is under M2.
- **G4:** see finding G4.
- **G5:** see finding G5.
- **G6:** 3 active DOF. Not present.

## Proposals (measurement changes; not applied, not verdict inputs)

1. **State every pin-knee claim at the knee the build rule requires.**
   - Re-wear each verified pin-knee row at stk 6.0 (MR63ZZ pairs) with `tools/alignment_knee_stack_probe.py`, and
     show both numbers until the row is re-fitted.
   - Measured on this row: bench 18.67 -> 18.93 (+0.26) and held out 23.73 -> 24.00 (+0.27). Every point of the loss comes from
     the knee link's in-band: 0.941 -> 0.913, median standoff 10.7 -> 11.3 mm.
   - No other row was re-worn in this audit's time box. FINDINGS line 2896 measured ~0.2 on another chain.
   - Rows that inherit stk 4.8534 from frontload (`docs/concepts/models/frontload-lobe-stopb-knuckle-3r.py` line 45)
     include slipper-nose, sidecar-longdyad, groove-desmo, kneeless-roller, frontload and geneva-tail. The conecut
     rows, desmo-conecut and crest-knee are already at 6.0.
   - Until this is done, the 18.28-18.98 cluster compares knees of two different sizes. The conecut-knee concept says
     so itself (`docs/concepts/conecut-knee-knuckle-3r.md` line 210).
2. **Subtract the knee the row actually booked.** Make the v2 knee subtraction faithful by either:
   - (a) booking the built knee in the base record (MR63ZZ pairs: +1 body and +4 bought on the slaved-knuckle
     records); or
   - (b) subtracting the row's own knee entry rather than the template.

   Measured where a kneeless twin exists: roller-longdyad 20.25 -> 23.75, sidecar-longdyad 25.5 -> 28.0. The other
   slaved-knuckle rows that copy this record (for example slipper-nose and trimlug at 18.25) would likely move by the
   same amount, but this was not measured row by row. The order within the family holds, and no complexity ranking
   across families flips on the rows checked.

## Numbers not obtained

- Stk-6.0 re-wears of the other verified pin-knee rows: 7-8 min each locally at the 2-process cap, beyond this time
  box. No farm batch: the CPU budget line is spent (CLAUDE.md decision 7).
- Contact depth of conecut-knee on its *claim* dump: the tool reads only dumps that reproduce the claim. Its
  `_bench_perpose.json` does reproduce 18.28 and is used above by hand, but the tool skips files without the `_claim`
  name.
- Roller lift-off on the clips under a throw: no R17 lift-off output exists. The red team's static factor is the only
  number.
- Sensing and determinacy: out of scope (user 2026-10-17). The old knee-sensing numbers are kept only in the 04:42
  skeptic section.

Local compute: 4 runs (bench and held re-wear, bench and held at stk 6.0), at most 2 of my processes, niced,
OMP_NUM_THREADS=1. Farm: none ($0).

---

_Earlier sections below this rule (rule dated 2026-10-18 22:30 UTC): the skeptics of 2026-10-17 02:20-02:30 UTC and 04:30-04:45 UTC, kept unchanged._

## Skeptic (2026-10-17 02:20-02:30 UTC, ledger entry 2026-10-17T02:29:27Z, `by skeptic`, run `skeptic:roller-longdyad-knuckle-3r`)

**Final verdict (computed by `tools/alignment_ledger.py skeptic`): WATCH.**
- 2 of the 9 reasons are refuted with measured evidence: `fold_margin` and `judgement:T4`.
- The other 7 stand at watch.
- Rulings: `docs/alignment/roller-longdyad-knuckle-3r.rulings.json`.

**New measurements.** No model, bench, row or score was changed.

The fit-bench grid cache (key 0089c747c10f, Bench(60,160)) was rebuilt locally at 01:59. That made the auditor's
"not obtained" paired comparison on the exact claim protocol possible.
- 4 farm dumps with `tools/alignment_paired.py` reproduce the claims to the digit:

  | design | bench | held out |
  |---|---|---|
  | this design | 18.67 | 23.73 |
  | the lead | 18.91 | 22.67 |

  Files: `remeasure/*_perpose_claim.json` and `remeasure/roller-longdyad-knuckle-3r_vs_sidecar-longdyad-knuckle-3r_paired_claim.json`.
- 2 held-out re-wears at the knee bounds ang_min 26.88 and 30.46:
  `remeasure/roller-longdyad-knuckle-3r_angmin{26.8823,30.46}_held_skeptic.json`.
- Farm cost: 6 jobs, about 860 worker-s, about $0.07.

### Rulings

**fold_margin: REFUTED.** The margin is on file 4 times, and every reading is at or above TH fold_min 5.0.
- `rows/roller-longdyad-knuckle-3r.json` `verification.th_margin_min`: bench 5.181, held 5.031, lt5 0.
- `verify/roller-longdyad-knuckle-3r_v_bench_frozen.json` `extra.th_margin`: min 5.181, n 371, lt5 0.
- `_v_held_frozen.json` `extra.th_margin`: min 5.031, n 851, lt5 0.
- The fit-fast reading is 5.011.
- Cause of the false watch: the tool's regex ends at `th_margin$`, so it skips `th_margin_min.*`. The dict
  `extra.th_margin` carries no plain number.

**judgement:S1: stands, and is now measured on the claim protocol.**
- Bench: difference -0.25, paired SD 1.35, 90 % interval [-2.62, +1.73], P(this design better) 0.605.
- Held out: +1.06. The reach term is +0.84, and the lead takes 29 workspace poses this design misses, against 21.
  The 90 % interval is [-0.47, +2.39], and P(better) is 0.135.
- Pooled: +0.69, 90 % interval [-0.56, +1.83], P(better) 0.191.
- The perturbed fit had given P 0.23 / 0.29, so it understated the lead's out-of-sample edge.
- My own bootstrap of the auditor's perturbed dumps reproduces his numbers: SD 1.39, P 0.58 on the bench and P 0.22
  held out.
- The 0.24 is noise.

**judgement:NEW-contact-depth: stands.** Per pose, on the claim protocol:

| set | design | contacts | depth sum | deepest | deeper than 3 mm |
|---|---|---|---|---|---|
| bench | this design | 2 | 16.46 mm | -10.55 mm | |
| bench | the lead | 4 | 6.23 mm | -4.61 mm | |
| held out | this design | 10 | 49.88 mm | -9.54 mm | 7 |
| held out | the lead | 10 | 35.67 mm | -8.37 mm | 5 |

One correction to the auditor: not every press is overhead. Held out, 4 of this design's 10 presses are below
elevation 150:
- -5.51, -3.49 and -1.60 mm at elevation 60 (planes -90 / -75, axial 105-120);
- -1.22 mm at elevation 105.

**judgement:NEW-ws-inband: stands.** From the probe files on the claim protocol:
- At elevation 90-140, workspace in-band is 0.7979 against 0.8409.
- The shortfall is metal standing off more than 14 mm (over14 0.2012 against 0.1565), so the raised-arm profile is
  bulkier.
- Taken poses with metal under 2 mm: 30 against 26 on the bench and 66 against 63 held out.

**judgement:S2: stands.** The envelope-corrected gap is 18.56 against 18.67 (in-band 0.8948 against 0.8937, with 9 head
points and 10 edge points). ROUNDS.md line 1208 prints 18.56 in the winner's row.

**judgement:G4: stands, and is tighter held out.**
- Held out (`_v_held_frozen.json` `extra`): pa_horn_max 43.0 = PA_MAX. dK_taken_max is 46.17 of the 46.25 limit, which
  is 0.08 deg from the cap; the bench figure was 45.62.
- At PA 45, no pose fails on either set.
- No force file exists.

**judgement:T4: REFUTED by re-wear.** The walked bounds do not buy the number.

| ang_min | bench | held out |
|---|---|---|
| 25.22 (claim) | 18.67 | 23.73 |
| 26.88 | 18.67 | 23.72 |
| 30.46 | 18.71 | 23.55 |

- K dyad: the largest a1e on a taken pose is 54.43, 9.61 deg short of stretch (bk1 + bk2 = 64.03).
- Stop B sits 0.27 inside the 5-deg guard (the lead sits at 0.00). The interior angle is 134.5 deg.
- The th margin is at least 5.031.

**judgement:M5: stands.** No spring-torque or closure-force output exists for this design. K moves on 167 of 371 taken
bench poses and 399 of 851 held out, so the cap is loaded on about 45 % of poses.

**judgement:G5: stands.** The mechanism record has 2 sensed_passive knee pins. If they count under the 2026-10-17 ruling,
the design reads 5 coordinates, over the 4-DOF cap. That is the user's question.

### Missed by the auditor (for the next audit; does not change this verdict)

1. **The pin knee runs closer to straight than the lead's, for no score.**
   - The knee window is [ang_min, 180 - ang_min] (`docs/concepts/models/skin-normal-3r-pin-knee.py` lines 14 and 55).
     Walking ang_min from 26.88 to 25.22 therefore also raised the straight-knee limit from 153.12 to 154.78 deg.
   - The taken knee reaches 151.92 deg on the bench and 153.16 held out (`remeasure/*_bench|held.json`
     `deep.coord_spans` K.ang). The lead reaches 146.14 and 150.86.
   - Held out, the claim uses 0.04 deg of window the lead does not have.
   - That walk is worth 0.00 on the bench and 0.01 held out. At H1's 30.46 window the gap is 18.71 / 23.55.
   - The auditor's "re-wear identical" was bench only.
   - Action for the polish or CAD: restore ang_min to at least 26.88 (better 30.46) at no measured cost.
2. **Below-shoulder presses held out.** 4 of the 10 held-out contacts (both designs) sit at elevation 60-105, at plane
   -90 / -75 with axial 105-120, which is the arm across the body and rotated. The "all overhead" reading hid them.
3. **The drive cap is tighter than reported.** Held out, dK reaches 46.17 of the 46.25 limit (0.08 deg from the cap),
   and the horn pressure angle reaches 43.0.
4. **The claim-protocol paired numbers** strengthen S1. Out of sample, P(this design better) is 0.135 (pooled 0.191).
   The auditor's perturbed-fit P was 0.23 / 0.29. Proposal A's held-out form ("the held-out gap under the same harness
   is not worse") blocks this lead change on the exact protocol: 23.73 against 22.67.
5. **Where the extra 1-2 mm poses come from.** On the claim protocol, taken poses with metal under 2 mm on the scored
   (in-band) samples are equal on the bench (25 against 25), and 61 against 58 held out. This design's extra
   near-touch poses (30 against 26 on the bench) come from the model's contact-only walls and crowns (`M.cmin`), which
   in-band never sees.

**Final verdict: WATCH.** The 0.24 round-9 win is a measured tie; the lead is likelier better out of sample. Not gamed.


---

## Skeptic (2026-10-17 04:30-04:45 UTC, metric-change audit; ledger entry 2026-10-17T04:42:07Z, `by skeptic`, run `skeptic:roller-longdyad-knuckle-3r`)

**Final verdict (computed by `tools/alignment_ledger.py skeptic`): WATCH.**
- 1 of the 10 reasons is refuted with evidence: `judgement:S2`.
- The other 9 stand at watch. 2 of them stand with their size or attribution corrected (G5, NEW-knee-sensing).
- Rulings: `docs/alignment/roller-longdyad-knuckle-3r.rulings.json`. None of the reasons is gamed. The ruling's
  premise holds for this row: the 3 hub encoders fix the pose.

**Re-measured.** No model, bench, row or score was changed.
- `tools/alignment_knee_sensing.py` was re-run on the bench and held out. It reproduces the auditor to the digit.
- Two new read-only tools. Both load the model unchanged and use the claim-protocol taken sets.
  - `tools/alignment_hub_injectivity.py` is a global check over all pairs of taken poses.
  - `tools/alignment_knee_encoder_value.py` asks what reading the knee pins, or K, adds to the hubs.
- Outputs: `remeasure/roller-longdyad-knuckle-3r_skeptic_{hub_injectivity,knee_encoder_value}_{bench,held}.json`.
- Local runs: about 8 of 10-60 s each, at most 2 processes. Farm: none ($0).

### Rulings

**contact_depth: stands.**
- Re-derived from `remeasure/*_perpose_claim.json`, taking the minimum of `min_mm` and `cmin` over the contact poses.
- Bench: 16.46 mm against 6.23 mm, x2.64 and +10.23 mm. Both pass TH `depth_ratio` 2 and `depth_floor_mm` 5.
- Held out: x1.40, under the ratio, as the tool says.
- Both designs were measured on the same frozen claim protocol.

**complexity: stands.**
- The v2 tool gives 24.25. The row's own `complexity` field is still 43.75, and its name still ends "(cx 43.75)".
- The dashboard computes the column live (`tools/dash_build.py` `complexity_of`), so it shows 24.25.
- The documented check fires on any mismatch. The stale field is the less flattering one, but the record is
  inconsistent.

**judgement:G5: stands, with its size corrected.** The auditor compared the template with the v1 *record's* knee.
Against this row's *actual* knee, the template matches on 5 of 6 items.

| item | template | this row's actual knee | source |
|---|---|---|---|
| bought | 6 | 6, plus 2 DIN 6799 e-clips | `docs/research/roller_mechanism_redteam.md` line 102: "iglidur GSM sleeve + 2 GTM washers per pin on integral Ti pins"; L1 `part_validity.json` |
| moving bodies | 2 | 2 | the knee frees member 3 (L1 tag l3) and adds the knee link (l4); in the kneeless twin, member 3 is arm-fixed |
| loops | 0 | 0 | see below |
| made | 4 | 1 (the knee link, with integral pins) | build spec |

- The v1 record carries only 6 bodies, 1 short. The topology rule L = J - B then charges the missing body as a
  "knee closure" loop (+4). That loop is the GH loop, which the anchor and skin-normal never charge.
- Measured with `tools/simplicity.py`:

  | count | complexity | topology flag |
  |---|---|---|
  | this row's own knee removed, its loop with it (= the kneeless twin) | **23.75** | none |
  | v2 as committed | 24.25 (+0.5, conservative today) | none |
  | the auditor's 27.75 (proposal A: loop kept) | 27.75 | "closed_loops 3 != joints 7 - moving_bodies 5" |
  | base record corrected (bodies 7, loops 2, bought 19), template kept | 22.25 (1.5 under the faithful 23.75) | |

- The real template error on this row is the made-part count only, worth at most 1.5 points, not 3.5.
- The round-9 tie-break keeps its direction under every count.

**judgement:NEW-knee-sensing: stands on GH drift; its encoder-error part is misattributed.**
- **Determinacy holds globally**, not just locally. Over all pairs of claim-taken poses, two arm orientations more than
  5 deg apart always differ by at least 4.09 deg (bench) or 2.25 deg (held out) in hub readings. The global
  amplification is at most 3.07 / 3.13 deg of arm per deg of hub reading, within the local 3.15. No hidden branch.
- **The 3.2x does not come from the knee.**
  - The raw sigma_min of 0.3172 equals 1 / (1 + kK) = 1 / 3.1534 exactly.
  - It sits at that floor on the forced poses: 167 of 371 on the bench and 399 of 851 held out.
  - It does not depend on the knee angle (correlation -0.015). It is the same with the knee at or below 149.54.
- **Reading the knee pins does not change it.** Reading the knee pins too (v1 sensing) gives 0.3180, and the
  amplification goes from 3.152 to 3.144 (3.146 to 3.144 held out). Reading K instead gives 0.574, or 1.74x.
- So the 3.2x is the unread slaved K's drive ratio, and it was already there in v1. The knee encoders never bought
  that precision. The same holds for the reference ordering: sidecar-longdyad's 0.378 is about 1 / (1 + 1.62).
- **The GH drift stands.** It is 1.79 / 1.87 deg per mm, equal to the pin knee the ruling cited (1.83). The pins are
  what would observe that drift. The user's question 3 is open.
- The tool's held-out set (852) comes from the non-claim dump. On the claim set (851) the minimum is the same (0.2455).

**judgement:S1: stands.** From `paired_claim.json`:
- Bench: -0.25, standard deviation 1.35, P(this design better) 0.605.
- Held out: +1.06, P 0.135. The lead takes 29 workspace poses this design misses, against 21 the other way.

**judgement:NEW-contact-depth: stands.**
- Bench: 16.46 mm against 6.23 mm. Held out: 49.88 mm against 35.66 mm, with 7 presses deeper than 3 mm against 5.
- The lead's own audit-compliant reading still presses 39.01 mm held out (`docs/research/roller-longdyad-knuckle-3r_final_polish.md`
  line 116).

**judgement:NEW-ws-inband: stands.** At elevation 90-140, workspace in-band is 0.7979 against 0.8409 (n 85 each), and
metal over 14 mm is 0.2012 against 0.1565. Both probes are exact on the frozen claim configs.

**judgement:S2: REFUTED.**
- The documented S2 detector reads ok, and its sign runs against the design. Tool check `sampling`: sample-weighted
  in-band 0.894 against part-weighted 0.922, so dd = -2.87. That does not pass TH `part_weight_watch` 3, and it means
  the sample weighting *under*-states this design.
- The heavily sampled parts are the worst ones: L2 at 0.736 with 124 samples, the crank at 0.797 with 129.
- No part is under 0.5 in band. The only thin part, L1a (8 samples), is 0.981 in band.
- The envelope correction added real metal that the model had left out, and that metal is in band. The roller is at
  least 5.76 mm off the skin on every taken pose (red team line 94).
- So the more real envelope reads 18.56, and the claim 18.67 is the conservative reading. ROUNDS.md line 1208
  headlines 18.67.

**judgement:G4: stands on the knee.**
- The taken knee reaches 151.92 deg on the bench and 153.16 held out. That is past H1's 149.54 window, on 3 bench and
  2 held-out claim poses.
- The hub-only sigma is lowest exactly there: 0.2497 / 0.2455, against 0.2934 / 0.2899 with the knee at or below
  149.54.
- The pressure-angle part is answered by the red team (`roller_mechanism/results_bench.json`, finding 4):
  - the moment arm about uK stays 15.0-15.2 mm over the whole stroke;
  - PA 45 is reached only at dK 51.05;
  - the binding stop is the q2 dowel at dK 46.25.

  So there is no transmission singularity at the 43 cap.

**judgement:M5: stands.** "No force file exists" is out of date.
- `roller_mechanism/results_bench.json` (commit 14cbe6c, 04:13) has:
  - `liftoff`: static safety factor 2.42-2.79, and a q2 acceleration limit of 43.7 rad/s2, which a throw exceeds;
  - `loads`: J2 torque 0.17-0.20 N.m, or 0.24-0.27 N.m with the MVP1 load.
- The red team itself requires R17 lift-off on the clips. No R17 output exists.

### Missed by the auditor (for the next audit; does not change this verdict)

1. **The hub-only error has a different cause.**
   - The 3.15x arm error per encoder error is 1 + kK. It applies on every forced pose (45 %), not "at the near-straight
     knee", and it is independent of the knee encoders (3.144 with them).
   - Proposal B's s8 gate therefore ranks rows by their drive ratio, not by what the knee encoders add.
   - The quantity that answers the ruling is the knee encoders' marginal value, sigma(hubs + pins) / sigma(hubs). It
     is 1.003 on this row (`tools/alignment_knee_encoder_value.py`).
   - For MVP1 tracking, an encoder on K (1.74x) or a 3x finer J2 encoder is what helps.
2. **The v1 record mis-books the knee**: 6 bodies instead of 7, knee bought parts 2 instead of 6, and a spurious
   "knee closure" loop. v2 is +0.5 today only because these errors cancel. Correcting the record without changing
   the template would make v2 understate by 1.5.
3. **A force file landed inside the audit window**, at 04:13: `docs/research/roller_mechanism_redteam.md` and
   `roller_mechanism/results_bench.json`.
   - G2 now has a number: the J2 torque reflected from the clock spring is 0.172-0.198 N.m, or 0.243-0.269 N.m with
     MVP1. That is under R17's 1 N.m (`geneva_rod_drive_redteam.md` line 170).
   - Lift-off on the clips is still unrun.
   - The red team's finding 6 matters under v2. Without the +0.5 deg K bias, the systematic K lag of -0.45 deg puts
     the held-out fold margin at about 4.98 deg (extrapolated). Hub-only sensing passes the K error 1:1 into the arm
     estimate (0.65 deg). The bias is not in the claimed config.
4. **The lead's audit-compliant reading of this config is 19.25 / 24.91**
   (`roller-longdyad-knuckle-3r_final_polish.md` lines 108-125).
   - It uses ang_min 26.88, smlo 5.5, a1max 58.53, PA_MAX 42 and margin 5.5. Its own doc says these numbers "belong on
     the row next to 18.67 / 23.73". The row still carries only 18.67.
   - The pricing includes tightenings (margin 5.5, PA 42), and sidecar-longdyad has no priced reading, so this is a
     measurement change, not a gap correction.
5. **The sensing tool reads the non-claim dump** (`_perpose.json`) before the claim dump. That adds pose 1054 held out.
   It has no effect here, but the tool should read `_perpose_claim.json` first.

### Questions for the user

1. The knee encoders add almost nothing to this row's pose estimate (3.152x -> 3.144x). The 3.15x comes from K being
   unread. Should MVP1 read K, or a 3x finer J2, rather than the knee?
2. Is the knee-free count this row's kneeless twin (23.75)? That count drops the "knee closure" loop, which is the GH
   loop through the wearer.

**Final verdict: WATCH.** The 3 hub encoders fix this row's pose without the knee encoders, so the ruling's premise
holds and nothing is gamed.

---

## Skeptic (2026-10-18, 23:00-23:25 UTC), on the 22:29 audit at the top of this file (ledger entry 2026-10-18T23:23:44Z, `by skeptic`, run `skeptic:roller-longdyad-knuckle-3r`)

**Final verdict: WATCH** (computed by `tools/alignment_ledger.py skeptic`). 1 of 7 reasons refuted with evidence (M5),
and 6 upheld at watch. The rulings are in `docs/alignment/roller-longdyad-knuckle-3r.rulings.json`. That file now holds
only these 7 judgement rulings. The 04:42 tool-check rulings (contact_depth upheld, S2 refuted, complexity resolved)
are still in git (a0c9ffd) and in the 04:30 skeptic section above. `alignment_audit.py selftest --ids
roller-longdyad-knuckle-3r` passes (verdict watch, TP 0 / FP 0 / FN 0), but it no longer replays those old checks on
this row.

**What I re-measured.**
- I re-ran the stk 6.0 bench wear myself: the probe's own `probe()`, written to scratch, CB_EXACT=1, nice, 1 process,
  git 8147f54, 127 s. It gave 18.93 (reach 0.725, inband14 0.8911, contact 0.0054, knee link 0.913 / 11.3 mm).
  Frozen, why, parts_ib14, params and every deep field match `remeasure/roller-longdyad-knuckle-3r_stk6_bench.json`
  bit for bit.
- I recomputed both complexity counts with `tools/simplicity.py`.
- I re-derived contact depth and the near-touch counts from the per-pose dumps of this row, sidecar-longdyad and
  conecut-knee.
- I read the raised-arm probes, including the lead's, which the audit did not use.
- I read the R17 output on the built gen-6 CAD field by field.

Farm $0.

### Rulings

1. **M2 (knee stack 4.85 mm, not the MR63ZZ 6.0): upheld.**
   - Reproduced: 18.93 on the bench (my run), 24.00 held out (the gap arithmetic on `_stk6_held.json`:
     1.01 + 21.83 + 1.16).
   - `stk_claim` 4.8534 comes from the model PARAMS (frontload WIN, line 45). best_params carries no stk.
   - New like-for-like neighbour since the audit: `remeasure/sidecar-longdyad-knuckle-3r_mr63knee_{bench,held}.json`
     (stk 6.0) reads 19.21 / 22.97 (+0.30 / +0.30).
   - With both knees at 6.0, the order is unchanged:
     - bench: 18.93 vs 19.21, this row ahead by 0.28;
     - held out: 24.00 vs 22.97, sidecar ahead by 1.03;
     - desmo-conecut (stk 6.0, 18.98) stays 0.05 behind; conecut-knee (stk 6.0, 18.28) stays ahead.
   - The scored knee is still not the build rule's knee (+0.26 / +0.27).
2. **G5 (3.5 points under the faithful knee-free count): upheld.**
   - simplicity v2.2 gives the row 20.25 and kneeless-roller 23.75.
   - The row minus its template is (bodies 4, joints 7, rot 3, loops 2, made 8, bought 9). The twin is (5, 7, 3, 2,
     11, 13). The difference is 1 body (1.0) + 3 made (1.5) + 4 bought (1.0) = 3.5.
   - The name still ends "(cx 43.75)".
3. **S1 (0.24 bench win inside paired noise, reversed held out): upheld.**
   - The paired claim file reproduces: bench diff -0.25 (SD 1.35, P 0.605); held +1.06 (SD 0.87, P 0.135).
   - At stk 6.0 on both, the held-out reversal persists (+1.03).
   - Note: the documented S1 detector (TH held_watch 6) reads +5.06, so this watch rests on the paired measurement,
     not on that threshold.
4. **T5 (depth-blind contact): upheld.**
   - Re-derived: this row presses 16.46 mm on the bench (2 poses, -10.55 at (15,165,-60)) and 49.88 mm held out.
   - sidecar-longdyad presses 6.23 mm (x2.64, +10.23 mm, past TH 2.0 / 5 mm).
   - Against the documented default reference (the current lead conecut-knee: 20.25 / 60.96 mm), the TH rule does
     **not** fire (0.81x / 0.82x).
   - It fires against the row this claim outranks, which is also the reference the instrument replays T5 rulings on
     (`tools/alignment_audit.py` line 307, `RULINGS_DEPTH_REF`).
   - The bench edge over sidecar comes from the contact term (paired split: contact -0.53 of a -0.25 total). That is
     fewer presses but deeper ones, the T5 case.
5. **NEW-ws-inband (raised-arm standoff): upheld, and stronger than stated.**
   - At elev 90-140: in-band 0.7979 / over 14 mm 0.2012, against sidecar's 0.8409 / 0.1565.
   - The lead's probe is on file (`remeasure/conecut-knee-knuckle-3r_probe_{bench,held}.json`):
     - lead: 0.8315 / 0.1676 on the bench, 0.8478 / 0.1492 held;
     - this row: 0.7979 / 0.2012 on the bench, 0.8185 / 0.1796 held;
     - so this row is worse than the lead too.
   - **Correction:** "25 / 61 vs 23 / 57 taken poses with metal < 2 mm" counts clip frames.
     - On ws poses this row has **22 / 54**, against the lead's 23 / 57 (fewer).
     - With cmin it is 25 / 58 vs 28 / 63.
     - The reversal is 3 / 7 clip hold frames at 1.99 mm here against 2.00 mm on the lead, at clip (30,150,-60).
6. **G4 (near-straight knee): upheld, with the force number corrected.**
   - The knee spans 86.21-151.92 deg on the bench and 153.16 held out. The stop is at 154.78, so the margins are
     2.86 / 1.62 deg.
   - The 31.6 N per N.m quoted is slipper-nose's (conecut-knee concept line 95, knee 152.2).
   - This row has the same knee (lE 67.832, lc 21.15):
     - bench: d_perp 31.93 mm, so 31.3 N per N.m;
     - held out: d_perp 30.63 mm, so 32.7 N per N.m;
     - that is 2.6-2.7x the re-centred knee's 12.0.
   - At ang_min 30.46 the wear reads 18.71 / 23.55 (files on record). So the claim's 25.22 window buys 0.04 on the
     bench, loses 0.18 held out, and lets the knee run to 1.62 deg from its stop.
7. **M5 (one spring force-closes two rolling pairs; "no lift-off run on the clips exists"): REFUTED.**
   - The run is on file: `pipeline/full-exo/designs/user_roller_longdyad/judge/dynamics.json` (R17,
     dynamics-2026-10-16, commit 3e2124c, 2026-10-17 10:13).
     - It is the same run whose 2x twist of 4.10 / 4.02 deg the reason cites.
     - `cases[*].clips[8].slaved.K` has closure "force", `liftoff_share_of_driven`, `lift_max_deg` and
       `law_err_driven_deg`. That is the run the red team asked for (`roller_mechanism_redteam.md` lines 116-118).
   - Every rolling-bearing case (mu 0.002 / 0.005, 1x and 2x, the MVP1 build) is clean:
     - `verdict.per_case` slaved_liftoff_share <= 0.0039;
     - lift_max_deg 0.0;
     - slaved_law_err_deg <= 0.225 (limit 5);
     - free = true.
   - The 43.7 rad/s2 q2 limit is the red team's static estimate for a throw that "everyday motion does not" reach
     (line 117). The 2x clips do not lift.
   - Lift-off appears only in the plain-bearing and constant-friction comparison cases (share 0.17-0.82). In those
     cases every hinge is plain and the whole build fails "free" on twist (12-90 deg), so they show no K-specific hold
     failure.

### Missed by the auditor (not in this verdict; for the next audit)

1. **Each judge takes the knee that suits it.**
   - The gap is scored on the 4.85 mm iglidur-faced knee stack (M2).
   - R17's nominal pass on the same gen-6 CAD models those iglidur knee pins at the rolling-bearing law.
     `dynamics.json` `chain.notes[1]` says so: "iglidur knee pins share it - an optimistic note for the plain-bearing
     pins".
   - So no single knee gets both 18.67 and the R17 pass. Under the build rule's MR63ZZ knee, the R17 law is right but
     the gap is 18.93. Under the iglidur knee, the gap is 18.67 but the R17 knee friction is optimistic.
   - CLAUDE.md decision 5 records that plain iglidur knee pins fail R17 (~10 deg twist, ~10 N).
   - The audit's "R17 passes on the built gen-6 CAD, which has iglidur knee pins" reads as if plain knee pins passed.
   - Not measured: R17 with plain friction on the two knee pins only.
   - Action: state the claim at stk 6.0 (proposal 1), or run R17 with plain knee pins.
2. **A stale missing-measurement watch was carried.**
   - The 04:42 skeptic's "no R17 output exists" looked in `l1_roller-longdyad/judge`.
   - The R17 slaved lift-off file landed in `user_roller_longdyad/judge` at 10:13 the same day. The audit cites that
     file for the twist but did not read its slaved fields.
   - Action: before carrying a "not measured" watch, grep the design's `judge/dynamics.json` for `slaved` and
     `liftoff`.
3. **A near-touch comparison decided on a 0.01 mm knife edge.**
   - The lead comparison (25 / 61 vs 23 / 57) reverses on the workspace poses (22 / 54 vs 23 / 57).
   - It is decided by repeated clip hold frames at 1.99 vs 2.00 mm.
   - Report only, but the direction printed in the "What the wearer gets" table is the less robust one.

Local compute: 1 exact bench wear, 1 process, niced, OMP_NUM_THREADS=1, output in scratch, no repo file overwritten.
Everything else was read from files on record. Farm $0.
