# Alignment audit: conecut-h2facet-knuckle-3r

Auditor run 2026-10-18 ~16:00-16:35 UTC. Discovery round 15, slice r15-A. Reference: the lead conecut-knee-knuckle-3r.
Tool: tools/alignment_audit.py 2026-10-18.1. Checks: docs/alignment/conecut-h2facet-knuckle-3r.json. Findings:
docs/alignment/conecut-h2facet-knuckle-3r.findings.json. Ledger: `python3 tools/alignment_ledger.py get conecut-h2facet-knuckle-3r`.

## Verdict and claim

**Ledger verdict: WATCH.** No check and no finding is 'gamed'.

The claim is v_gap **18.28** (score 93.35) on exact Bench(110,360), frozen shape. Held out it reads 22.16.

- **What the design is:** the lead's chain, unchanged, plus a 1.4 mm x 45-deg chamfer on hub 2's skin-side bottom edge.
  The row also lists an upper flat, which is mis-framed and worth 0 (finding NEW-wrong-body-frame).
- **Against the lead, on the bench:** an exact tie, with the same 262 takes and the same 4 contacts.
- **Against the lead, held out:** 22.16 vs 22.38, a -0.22 edge that is one pose.
- **Is the exo better?** Yes, a little, and never worse. The chamfer only removes metal.
- **Does the number oversell it?** Yes, in two places:
  - every scored gain sits just past a cutoff (T1);
  - the board shows the design at complexity 0 when it is 18.5 (G5).

I re-measured both claim numbers with the models unchanged. Each reproduces exactly:

| wear | gap | reach | in-band14 | contacts | near1 | near2 | near3 | band 3-14 | file |
|---|---|---|---|---|---|---|---|---|---|
| bench re-wear (model's own frozen()) | 18.28 | 0.7278 | 0.9012 | 4 | 19.38 | 34.84 | 81.91 (lead 86.16) | 18.33 (lead 18.34) | remeasure/conecut-h2facet-knuckle-3r_bench.json |
| held re-wear (model's own frozen_held()) | 22.16 | 0.6933 | 0.900 | 13 | 25.23 | 36.89 | 79.60 (lead 83.12) | 22.32 (lead 22.55) | remeasure/conecut-h2facet-knuckle-3r_held.json |
| bench continuity flood (chamfer only) | static 18.28, full 18.28, knn 19.97, bench-graph 50.13 = the lead's flood | | | | | | | | remeasure/conecut-h2facet-knuckle-3r+chamferonly_flood_bench.json |
| bench wear probe | 18.28 | | | | | | | | remeasure/conecut-h2facet-knuckle-3r_probe_bench.json |

The chain's coordinate spans are bit-identical to the lead's re-wear:
- dK -0.796..0 rad;
- K.ang 59.27..105.94 deg;
- q3' -109.20..116.10 deg;
- msub 10.81..99.0 deg;
- a1e 37.55..54.26 deg.

## What the wearer gets (measured)

- **Overhead reach (elev >= 140):** 8 of 28 bench poses taken, the same as the lead. The 20 lost poses: fold 14,
  contact 3, J3 stop 3 (probe). Held: 18 of 71.
- **Raised-arm reach (elev >= 90):** 47 of 113 bench poses (0.416), the same as the lead. Held: 124 of 300 (the lead
  123 of 300); the one extra is pose 447.
- **Taken poses with metal under 2 mm:** 33 bench and 71 held, both equal to the lead. Under 3 mm: 99 vs 105 bench and
  206 vs 217 held, so the chamfer helps here. Under 1 mm: 2 vs 3 bench and 14 vs 13 held; held 447 joins this group at
  0.697 mm.
- **Lowest metal on a taken pose:** 0.072 mm at bench 139 (ws -60/60/105), on link 2. The chamfer cannot reach it.
- **Deepest contact:**
  - bench: 8.93 mm at ws 15/165/-60, on the crank / horn; 4 contact poses summing 19.86 mm (lead 20.24);
  - held: 9.86 mm at ws 45/165/-30; 13 contact poses summing 60.5 mm (lead 14 poses, 60.97 mm).
  - Pose 205 stays a contact at -3.90 mm (lead -4.28). It binds on hub 2 but would need 4.85 mm of radial cut, which
    runs into the bore.
- **Workspace in-band (unscored, bench):**
  - all taken workspace poses: 0.868 (13.0 % of the metal above 14 mm, max 30.74 mm);
  - elevation 90-140: 0.832;
  - overhead: 0.936 on 8 poses.
  - Every value equals the lead's. Only the scored clip frames read 0.901.
- **Clearance gain from the chamfer:** 21 bench and 45 held poses change, mean +0.57 / +0.60 mm, max +0.98. All of them
  sit at elevation 45-138, none overhead. The single drop is 234 at -0.05 mm, a measurement change from the denser
  sampling.
- **Springs, stops, cuff twist, singular postures:** all the lead's, with nothing added.
  - K clock spring and sliding-nose drive: R17 and cuff twist never measured on this chain (M5).
  - J3 own-angle dowel: the held number lives inside a 1.33 deg window (T3).
  - th fold margin: 5.181 bench, 5.006 held (T3).
  - m_sub near-singular at K rest: carried, not re-measured (G4).
  - The chamfer adds no joint, stop or load path. The wall to the O7 pin collar is 3.1 mm.

## Checks (tools/alignment_audit.py)

| check | level | reading |
|---|---|---|
| held_out | ok | 22.16 vs 18.28 (+3.88) |
| fast_frozen | ok | 12.5 -> 18.28 (+5.78) |
| near_touch | ok | 18.28 / 19.38 / 34.84; 16.56 points in the 1-2 mm shell (the lead's) |
| contact_depth | ok | bench 4 poses, 19.86 mm; held 13 poses, 60.5 mm |
| dominance | ok | vs the lead: +0.00 plain, +0.00 at 2 mm |
| continuity | watch | no flood in the verifier files. This audit measured the bench flood: full 18.28 = static (finding S5) |
| fold_margin | ok | 5.006 deg |
| idle | ok | knee moves; dK span 45.6 deg |
| sampling | ok | sample-weighted 0.901 vs part-weighted 0.925; L1a 8 samples (the lead's) |
| density | ok | roller 4.55x (the lead's) |
| complexity | watch | recomputed 0.0 vs row 18.5: the mechanism record is a delta (finding G5) |
| reporting | watch | the verdict reads as a screen; the dashboard's sweep best 12.5 sits 5.78 below the verified number |
| judge_change | ok | none |
| rules | ok | O20, margin >= 5, 0 passive translations, 3 active DOF |

## Findings

Each finding has its full numbers and files in the findings JSON.

1. **G5: complexity hidden by the record (watch).**
   - The cause: the row's mechanism block is a delta record (source + record_delta + complexity 18.5), so
     tools/simplicity.py scores it as the anchor, 0.
   - The board: tools/dash_build.py publishes that 0, and the user's score-vs-simplicity chart plots the design at
     (93.35, 0), the golden-solution corner. The lead it is built on plots at 18.5.
   - The measured effect: with the shown 0, this row dominates 33 of the other 36 verified rows. With its true 18.5 it
     dominates 12.
   - The same defect is on conecut-l2jog-knuckle-3r and lowarm-kphase-notch-knuckle-3r.
   - Why the exo is not better: complexity is the user's second objective, and this design adds nothing on that axis.
   - Why watch and not gamed: complexity is never scored, and the row's own complexity field is right.
   - Action: write the lead's full mechanism record into the row, with the +0 delta.
2. **T1: gains parked just past a cutoff (watch).**
   - Bench: near1 19.92 -> 19.38 comes from pose 203 at 1.122 mm, 0.12 mm past the 1 mm line.
   - Held: the -0.22 plain edge is pose 447, taken at 0.697 mm, so held near1 is identical (25.23 both). The near2 edge
     (36.89 vs 37.10) is pose 599, which moves 1.867 -> 2.094 mm.
   - The exo is genuinely better: 66 poses gain 0.04-0.98 mm, and only one pose loses (the -0.05 mm measurement
     change).
   - But a 0.4-0.9 mm gain is counted as a whole pose.
   - Action: report the held edge as one pose taken at 0.70 mm, not as a held lead.
3. **P1: chosen on the claim bench (watch).**
   - The search benches cannot see the cut: 122 configs read 12.5 / near1 13.66, so the convergence gate passes
     vacuously.
   - The cut is placed at exact-bench pose 203's binder sample and sized on six exact claim-bench guard poses. The
     bench-side gains (203, near1, the +0.35 probe, T5) are therefore in-sample.
   - Held confirms the sign but not the size.
4. **NEW-wrong-body-frame: the flat (watch).**
   - The upper flat is modelled on link 1b, but it cuts link 2's boss and cap, which turn -14..+91 deg at J2.
   - It is worth 0 here: fd 0 is identical pose for pose.
   - The row still advertises it: the name, best_params fd 0.6, and the 264 +0.26..+0.37 table that
     rows/lowarm-kphase-notch-knuckle-3r.json already cites as its enabler.
   - Action: set fd 0 in best_params (or mark the flat refuted), and re-measure the flat in link 2's frame before any
     row imports it.
5. **R1: screen strings on a verified row (watch).**
   - The verdict opens "SCREENED as a 0-cx ENABLER CELL". morphs.json shows gap / sweep_gap 12.5 (score 95.45, above
     the 95 line) and empty alignment.
   - Action: put the verified result and the chamfer-only config first.
6. **S5: no held flood (watch).**
   - The bench flood equals the lead's (measured here).
   - The one pose the design gains anywhere (held 447) has no flood, and neither does the lead's held wear.
7. **Carried from the lead's chain, all watch:** T3 (th 5.006 held; J3 dowel 1.33 deg window), M5 (K spring, R17 and
   cuff twist not measured), G4 (m_sub at rest, not re-measured), NEW-strap-dilution (equal-strap gap 18.67 / 22.68),
   NEW-ws-inband (workspace in-band 0.868, 0.832 at elevation 90-140, unscored), P2 (held leak in form from the lead's
   knee re-centring, zero measured effect).

Patterns walked and found absent:
- **T2:** clip in-band is unchanged, and the 3-14 mm band gap is 18.33 vs 18.34.
- **T4:** no bound moved.
- **T5:** depth is lower than the lead's on both wears.
- **S1:** held +3.88 is the lead's own drop.
- **S2 / S6:** the 3011 added samples are contact-only and so conservative. The 80 rigid in-band samples are kept, 6 of
  them clipped.
- **S3:** the cut is sampled as a solid, including the chamfer's top edge.
- **S4:** none.
- **M1 / M2:** the chamfer is a real machining feature on link 1b's lower plate, and the O20 bearing stack is untouched.
  The flat is the exception (finding 4).
- **M3:** part-vs-part collisions keep the uncut cylinder, which is conservative.
- **M4:** the knee spans 46.7 deg and dK 45.6 deg.
- **P3:** two wears (flat / chamfer only), identical.
- **P4:** no measurement file in the row's commits.
- **R2 / R4:** v_gap on the board equals the verifier's.
- **R3:** the c table is reported in full.
- **G2 / G3:** nothing new; see M5.
- **G6:** 3 active DOF.

## Held re-wear

I re-wore the held split through the model's own frozen_held() (docs/alignment/remeasure/conecut-h2facet-knuckle-3r_held.json).
It reproduces the verifier exactly:

| held reading | h2facet | lead (remeasure/conecut-knee-knuckle-3r_held.json) |
|---|---|---|
| gap | 22.16 | 22.38 |
| reach (taken) | 0.6933 (862 taken) | 0.6922 (861) |
| near1 | 25.23 (14 poses) | 25.23 (13) |
| near2 | 36.89 (71) | 37.10 (71) |
| near3 | 79.60 (207) | 83.12 (218) |
| band read as 3-14 mm | 22.32 | 22.55 |
| min metal on a taken pose | 0.325 mm | 0.325 mm |

The coordinate spans are bit-identical. The plain held edge (-0.22) and the 1 mm reading (0.00) differ only because
pose 447 is taken at 0.697 mm. The 3 mm reading (-3.52, 11 fewer poses under 3 mm) is the chamfer's real, wearer-side
gain.

## Proposals (proposals only; none feeds this verdict)

1. **Catalogue entry M6, "A feature modelled on a body it does not ride on."**
   - Looks like: a cut, pad or relief is placed in one member's frame while the metal it removes belongs to a member
     that turns relative to it (a boss or cap on the other side of a joint).
   - Detect: for each geometry edit, list the R6 group of the edited samples' member and of the physical part. Flag
     watch when they differ and the joint between them spans more than the feature's angular tolerance.
   - Here: the h2facet flat, worth 0 on its own chain, already cited by another row as an enabler.
   - Effect on verified rows: none measured. The only feature-edit rows are conecut-h2facet (0 change) and
     conecut-l2jog (a planform cut on link 2's own profile, the right body per its row).
2. **A record rule for delta rows** (a reporting fix, not a metric change). A row whose mechanism is
   `{source, record_delta}` should be expanded to the source's full record before tools/simplicity.py scores it. Until
   then, the complexity check should read a delta record's complexity as the source's.
   - Measured effect: 3 verified rows change their shown complexity (conecut-h2facet 0 -> 18.5, conecut-l2jog 0 -> 18.5,
     lowarm-kphase-notch 0 -> its source's). No gap changes.
3. **A vacuous-search flag for the convergence gate.** When every configuration of a search reads the same number
   (top-5 spread 0, n >= 20), the row should say "flat sweep: parameters chosen elsewhere" and name the bench they were
   chosen on.
   - Measured effect on verified rows: conecut-h2facet (122 flat configs). No gap changes.
