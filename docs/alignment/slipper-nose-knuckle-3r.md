# Alignment audit: slipper-nose-knuckle-3r

Auditor run 2026-10-17 14:03-14:12 UTC (the hourly audit of the lead's new claims since 07:15). Ledger entry
2026-10-17T14:09:14Z, `by auditor`, run `audit:slipper-nose-knuckle-3r`. Checks: `docs/alignment/slipper-nose-knuckle-3r.json`
(13 checks). Findings: `docs/alignment/slipper-nose-knuckle-3r.findings.json` (9). New measurement:
`docs/alignment/remeasure/slipper-nose-knuckle-3r_m5_forward_bound.json`.

## Verdict: WATCH (ledger tool verdict watch; tool checks alone watch)

- **The claim:** v_gap 18.49 (score 93.28), frozen exact Bench(110,360), verified 06:22 UTC. The row has not moved since
  (last row commit 06:23 UTC). The 07:08 re-wear (bench 18.49, held 23.45, 1 / 2 / 3 mm near-touch 20.12 / 33.02 / 83.15)
  is newer than the row, so it was not repeated.
- **What was audited this hour:**
  - the gen-7 L1 CAD (commit 4a80fdf, 8 of 19);
  - the final polish's crank-side cliff (commits e95a8aa and 5d1e186);
  - the red team's held-out fold margin (5.006).
- **No gamed reason.** The number is not bought by any of the three:
  - the L1 judges ran at the gen-6 settings;
  - the R16 attribution holds pose by pose;
  - a robust flank 2-4 deg of beta away scores within 0.06;
  - the fold margin needs a K lead that the full-CAD builder already carries.
- **Two things are newly measured.**
  - **The M5 action is a proxy, and only half of it was run.** It ran the return stroke and passes. The audit ran the
    forward stroke with the same judge, and it passes with 0.10 deg of cuff-twist margin at mu 0.15.
  - **The proxy as reported reads better as friction rises.** This is new finding NEW-one-sided-proxy.

## What the wearer gets (measured)

Measured on Bench(110,360) exact, frozen; held out in brackets. The L1 CAD's judges are named where they are used.

- **Overhead (elevation >= 140):** 8 of 28 workspace poses taken (18 of 71). The same as the lead. On the CAD, R4
  (Raise overhead clip) is 74.5 % (FAIL against 80), the same as gen 6.
- **Raised arm:** reach is 26/51 at elevation 90-120 and 12/34 at 120-140. Workspace reach in all is 0.725 (0.683).
  - CAD R16 functional workspace: 64.2 % at step 12 and 70.3 % at step 1.
  - Of the step-1 poses, 0.8 % fail on body contact and 0.0 % on parts.
- **Taken poses with metal under 2 mm:** 30 of 371 (66-67 of 852).
  - Under 1 mm: 3 (14).
  - The lowest is 0.072 mm at (-60, 60, 105). The L1 build puts 0.53 mm of metal into the arm at that same pose (R16,
    step 1).
- **Deepest contact:** 9.01 mm at (15, 165, -60) overhead, from the crank arm and flank lug; summed 14.75 mm over 2 bench
  poses. Held out: 10 poses, summed 46.12 mm, deepest 9.05 mm.
  - On the CAD the same overhead poses press 5.5-9.4 mm.
  - R2 reads 24.87 mm on every build (the rig's own self-intersection). The parts of this project read 0.0 mm.
- **Workspace in-band (unscored):** 0.856 over all taken poses. At elevation 90-140 it is 0.800, with 0.199 of the metal
  above 14 mm.
  - CAD R1 is 82.0 % and R1-aim (2-10 mm) 48.6 %, the same as gen 6. Half the covered skin sits farther than 10 mm from
    the metal.
- **Spring, cuff twist and arm load (R17, MuJoCo, rolling bearings mu 0.005):**
  - Nominal (0.08 N.m preload): twist 4.01 deg against 5.0, M_GH 0.127 N.m, cuff force 0.58 N. K stays on its law to
    0.137 deg, lift-off 0.0006.
  - Return-stroke proxy (the lead's judge_m5): twist 3.58 / 3.42 / 3.28 deg at mu 0.087 / 0.12 / 0.15.
  - Forward-stroke bound (this audit): twist **4.50 / 4.90 deg** at mu 0.087 / 0.15, M_GH 0.148 / 0.165 N.m, lift-off
    0.000. R17 passes in both directions.
  - Twist is set almost entirely by the spring preload (about 49 deg per N.m). A preload above about 0.10 N.m fails
    R17.
- **Stops and fold margin:**
  - th margin minimum 5.181 bench (5.006 held out).
  - With the drive's systematic K lag of -0.42 to -0.53 deg (red team), the held-out minimum falls to about 4.96, with
    1-2 poses under 5. The bench stays at 5.12 or above.
  - The +0.75 deg K lead in the full-CAD builder restores 5.003 or above.
  - The knee stop (154.78 deg) is built in the L1, but the dynamics judge leaves the knee pins free (a stale judge note
    still reads "149.5 deg, not in the CAD").
- **Singular postures:** with K at rest, the sub-chain margin m_sub is under 1 deg on 50 of 371 bench poses. This is
  family-wide (G4), and B1 is open with the user.
- **Drive transmission:** horn 36.1 + 4.97 = 41.1 deg effective against the 43 cap; crank 29.5 + 4.97 = 34.5 deg. The
  crank side is 0.2 mm of r_c from its synthesis cap (finding NEW-synthesis-cliff).
- **DOF and complexity:** 3 active, 0 passive translations, O20 hubs. Complexity reads 22.25 as recorded; written the
  lead's way it would be 18.25.

## Findings (each watch; none is gamed)

1. **M5: the spring holds, measured now by a proxy on both strokes.**
   - **Evidence:** the lead de-rated the clock-spring preload by the worst-PA efficiency (0.890 / 0.851 / 0.815) and
     re-ran R17. It passes, with K against its law 0.13 deg and lift-off 0.000-0.0006. That is the return stroke.
   - The audit ran the forward stroke with the same judge on the same build, with the spring up-rated to preload / eta
     (0.0899 / 0.0982 N.m). Twist reads 4.50 / 4.90 deg against the 5.0 limit, and M_GH 0.148 / 0.165 N.m.
   - **Why it matters:** the judge does not model the sliding nose ("drive bearing friction not modelled"). A static
     de-rating stands in for it. That is acceptable as a bound, but the cuff-twist margin at mu 0.15 is 0.10 deg.
   - **Action:** keep the preload at 0.08 N.m or below. Do the wear test before the full CAD, to confirm that mu stays
     at 0.12 or below.
2. **NEW-one-sided-proxy: the reported friction column improves as friction rises.**
   - **Evidence:** in the EVOLUTION row, twist goes 4.01 -> 3.58 -> 3.42 -> 3.28 deg and M_GH 0.127 -> 0.101 N.m as mu
     goes from 0 to 0.15. That is because the de-rated spring is applied to the whole clip, including the forward
     stroke, where friction should add load.
   - **Why it matters:** the ranking does not move, because R17 passes either way. But the reader is shown a 1.7 deg
     twist margin at mu 0.15 where the two-sided bound gives 0.10 deg.
   - **Action:** report both strokes' bounds; see proposal R5.
3. **T3: the held-out fold margin depends on K being on its law.**
   - **Evidence:** the J2 stop acts on J2's own angle, but th moves by about 0.08 deg per deg of K. At the red team's
     measured systematic lag (-0.42 to -0.53 deg), the held-out minimum is about 4.966, with 1-2 of 852 poses under 5.
     The bench holds at 5.12 or above at -0.7 deg.
   - **What depends on it:** the verified bench 18.49 does not. At most 2 held-out poses do, worth 0.21 held-out points
     or less.
   - **Status of the fix:** the red team's +0.75 deg K lead (the lobe-ring dowel advanced 0.35 deg of q2) is in the
     full-CAD builder (`pipeline/conformal/param_cad`). It is not in the judged L1.
   - **Not measured:** the lead's own effect on skin distance and on the score. A 0.2-0.75 deg K offset moves link 1b's
     far end by about 0.2-0.8 mm.
   - **Action:** before the gen-7 full CAD is called judged, re-wear the claim with K offset +0.25 / +0.5 / +0.75 deg
     (gap, 1 mm near-touch, th minimum).
4. **NEW-synthesis-cliff: the verified flank sits 0.2 mm from an immovable drive, but its score does not depend on that.**
   - **Evidence:** the final polish's robustness scan fails 3 of 6 neighbours. With beta -1 deg, r_c -0.25 mm or g
     -0.05, the crank PA rises past 38.03 deg (38.8 / 40.2 / 49.0), and the re-synthesised drive ends at dK 0 (fit 14.25
     -> 86.1). The finer scan puts the edge at r_c -0.20 mm and g -0.02. The CMA optimum sits against the crank-side
     transmission cap (T4-like).
   - **Why it is not a knife-edge score:** the flank-robustness agent's pre-registered beta steps read 18.48 / 18.46 /
     18.44 / 18.43 / 18.70 at beta +1 .. +5 deg on the verified protocol (unpriced; work in progress, not yet claims).
     beta +2, +3 and +4 pass all 6 neighbours. A robust flank therefore costs 0.03-0.06.
   - **Still open:** what the BUILT crank does when it is off by tolerance against a fixed flank. That agent's
     `asbuilt.py` is measuring it, and there is no output yet. This audit did not duplicate the run.
   - **Action:** the CAD should take the pre-registered robust pick if its paired held-out interval allows; that is the
     rule in `prereg.json`. A catalogue entry is proposed below (T6).
5. **T1: the CAD turns one near-touch pose into contact. The R16 attribution holds.**
   - **Evidence:** of the 12 step-1 R16 body contacts, 11 are poses where the verified model's own metal is 1.07-8.50 mm
     inside the arm at the same frame. Every one of the 11 is a scored contact pose in the claim's dumps (2 bench, 9
     held out), and the depths agree to 0.01 mm. So nothing the score counted as taken is excused.
   - The build adds 0.60-1.45 mm on 8 of the 12, at strap and lug edges that lie past the model's sample rows. One pose,
     (-60, 60, 105), fails on the build alone at 0.53 mm. On the bench that pose is taken with 0.072 mm of clearance.
   - The file summarises this as `model_own 4`; the commit says "11/12 the verified model's own". The commit wording
     hides the metal the build adds.
   - **Why it matters:** for the built exo, the 1 mm near-touch reading (20.12) is the closer measure.
   - **Action:** word the attribution as "11 model contacts, the build adds 0.6-1.45 mm on 8, plus 1 build-only".
6. **G4 (carried): a near-singular sub-chain at rest, family-wide.** m_sub is under 1 deg on 50 of the 371 bench poses.
   It is identical to the lead. B1 is open with the user.
7. **T5 (carried): contact depth.** The bench presses 14.75 mm summed against sidecar-longdyad's 6.23 mm. The comparison
   is mixed for the wearer. The L1 build confirms the same overhead presses.
8. **NEW-ws-inband (carried): raised-arm standoff.** In-band is 0.800 at elevation 90-140, with 0.199 of the metal above
   14 mm. R1-aim is 48.6 %.
9. **NEW-stale-complexity-ruler (carried, not yet fixed):** the dashboard still shows 22.25 against 20.25. Written the
   lead's way it is 18.25. This runs against the design.

**Tool reasons:**
- `contact_depth` watch: this is T5.
- `idle` watch: the instrument false positive the skeptic refuted at 07:15. The tool still fires because B-b is not
  applied.
- `reporting` watch, which stands:
  - the verdict text still reads "screened -";
  - the dashboard shows the sweep best 13.0;
  - the dashboard also has no `v_contact`, so the verified row shows contact 0.0 where the frozen contact is 0.0054
    (the skeptic's missed item 1; still true at 14:09).

## The three questions of this audit, answered

1. **Is a proxy standing in for the M5 action? Yes.**
   - The return-stroke action was run as asked, but as a static spring de-rating: the judge has no sliding contact.
   - It passes. With the forward-stroke bound added, it still passes, with twist up to 4.90 against 5.0 deg.
   - **R16 attribution:** it holds pose by pose (11 of 12 are scored model contacts). It does not hide CAD metal that
     the score counted, but the CAD does add 0.6-1.45 mm.
   - **Judge settings:** none is weaker than gen 6:
     - R1 / R4 at step 3;
     - R2 at step 6 (228 frames);
     - R6 at step 3 (451 frames);
     - R16 at step 12 (120 poses), plus step 1;
     - the dynamics run on the same 23 cases;
     - R9 and R10 NOT RUN in both generations.
   - R1, R1-aim, R4 and R16 equal gen 6's to 3-4 digits (0.8203 against 0.8198; 0.6417 against 0.6417), because the
     chain is the lead's.
2. **Is 18.49 a knife-edge optimum? No.**
   - The cliff is in the drive's re-synthesis, about 0.2 mm of r_c on the crank side. It is real, and the CAD should
     step off it.
   - The score beside it is flat: beta +1 .. +4 deg reads 18.43-18.48.
   - The as-built tolerance answer is pending in `docs/research/slipper_flank_robust/`.
3. **Does the verified number lean on a fold margin the built drive cannot hold? Not the bench number.**
   - The bench holds 5.12 or above at any measured lag.
   - Held out, 1-2 poses dip to about 4.95-4.97 without the K lead, worth 0.21 points or less. The full-CAD builder's
     +0.75 deg lead fixes it.
   - The lead's own effect on the gap has not been measured.

## Patterns walked (each against this design and the goal)

| pattern | this design | evidence |
|---|---|---|
| T1 metal past the cutoff | 14.53 points in the 1-2 mm shell; the L1 build turns the 0.072 mm pose into 0.53 mm contact (finding 5) | remeasure bench `deep`; judge_r16s1 |
| T2 band edge | clean: 2-3 mm share 0.0015; 3-14 band 18.64 | remeasure bench |
| T3 margin on another angle | th read on th; holds only with K on its law (finding 3) | red team section 4 |
| T4 search bound at the box edge | the crank side sits against the PA cap, 0.2 mm r_c (finding 4) | final polish lines 254-255 |
| T5 depth-blind contact | finding 7 | paired_claim |
| S1-S5 | as at 07:10: held-out drop +4.96; part-weighted in-band 0.924; all bodies sampled; flood = static | audit json |
| M1-M4 | O2.37 nose (stock O2.5 dowel verified, built as O2.5 ground to O2.368); O20; clashes checked (R6 0.0 mm on the L1, worst pair 0.098 mm boss / pin); drives move (K 45.6, crank 19.3 deg) | L1 build.json, EVOLUTION |
| M5 springs | finding 1 | m5_forward_bound |
| P1-P4 | final polish adopted nothing; the flank-robust pick rule was pre-registered (0761f77) before any claim; no judge changed with the design (judge_change ok) | prereg.json, audit json |
| R1-R4 | `reporting` watch; NEW-one-sided-proxy (finding 2); attribution wording (finding 5) | EVOLUTION, commit 4a80fdf |
| G1 hugging | nothing new | - |
| G2 / G3 stiff spring, cuff twist | twist 4.01 nominal, 4.90 at the mu 0.15 forward bound, against 5.0 (finding 1) | dynamics |
| G4 singular postures | finding 6 | msub probe |
| G5 / G6 complexity | overstated, not hidden (finding 9) | simplicity |

## Proposals (not applied; each a reporting, judge or catalogue change for the lead or the user)

- **R5 (catalogue, R-family): "A one-sided proxy".**
  - What it is: a stand-in that is applied only in the direction that helps, then reported as a pass at the worse
    condition.
  - How to detect it: a column that improves monotonically with a parameter that physically worsens it.
  - Here: R17 twist 4.01 -> 3.28 deg as mu goes from 0 to 0.15; the two-sided bound is 4.50 / 4.90.
  - Effect on verified rows: none. This is a reporting change, and the gen-6 roller has no friction column.
- **T6 (catalogue, T-family): "An optimum against a synthesis cliff".**
  - What it is: a parameter sits within manufacturing tolerance of a value at which a re-synthesised part stops
    working.
  - How to detect it: one-at-a-time tolerance neighbours (priced) on every drive or cam parameter; report the share that
    keep the drive, and the score of the nearest robust neighbour.
  - Here: 3 of 6 neighbours fail, and the nearest robust neighbour (beta +2 deg) scores 18.46 against 18.49.
  - Effect on other rows: not measured. The tool exists only for the slipper (`tools/slipper_env_polish.py robust`).
- **J1 (judge, measurement change): model the drive's sliding contact in `judge/dynamics.py`.**
  - What it would do: apply a Coulomb force at the nose with its sign set by the relative slip, in place of the joint
    equality that holds K on the law.
  - Until then: report both strokes' bounds.
  - Effect: not measured, because it is not built.
- **K-lead re-wear (claim hygiene):** wear the claim with the K offset the CAD builds (+0.25 / +0.5 / +0.75 deg) and
  report the gap, the 1 mm near-touch and the th minimum before the gen-7 full CAD is judged.

## Numbers not obtained, and why

- **The as-built crank tolerance against the fixed flank:** this belongs to the flank-robustness agent
  (`asbuilt.py`, running, no output). It was not duplicated.
- **Held-out readings of the beta steps:** they are still running in that agent's queue.
- **The score with the +0.75 deg K lead:** it needs a K-offset wear of the model. The model may not be edited, and an
  adapter was not built in this time box.
- **Dynamics with the knee stop:** the judge leaves the knee pins free (the 154.78 deg stop is built in the L1 and is
  not modelled), so its effect on twist and cuff force is not measured.
- **Farm:** $0. Two local runs of `judge/dynamics.py --quick` (niced, OMP 1, 1 process each, about 2 min).

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
