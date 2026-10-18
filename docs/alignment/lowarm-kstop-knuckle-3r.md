# Alignment audit: lowarm-kstop-knuckle-3r

Audited 2026-10-18 (~15:58-16:35 UTC) for discovery round 15, slice r15-A. Reference: the 3-active lead
conecut-knee-knuckle-3r. Instrument: `tools/alignment_audit.py` (VERSION 2026-10-18.1). Re-wear adapter (new file):
`tools/alignment_remeasure_kstop.py`. Findings: `docs/alignment/lowarm-kstop-knuckle-3r.findings.json`.
Checks: `docs/alignment/lowarm-kstop-knuckle-3r.json`.

## Verdict: WATCH. Claim v_gap 18.69 (score 93.20); held out 22.876

The ledger tool printed WATCH (see "Ledger" below). The number is real. This audit re-wore it with the model unchanged
and got 18.69 again, the per-pose worst of the two sided dwell wears. The +0.264 deg wear reads 18.60 and the -0.210 deg
wear reads 18.68, both bit-identical to the claim and the verifier. Held: HELD_LINE.

Nothing in the number ranks this design above a design that is better for the wearer. It sits behind the lead on every
reading:

| reading | lowarm-kstop | conecut-knee (lead) |
|---|---|---|
| plain bench | 18.69 | 18.29 |
| 1 mm near-touch | 20.86 | 19.92 |
| 2 mm near-touch | 34.84 | 34.84 |
| held | 22.876 | 22.38 |

So no finding reaches 'gamed'. The watch items are about whether the row should be alive at all. It passed its own round's
gates by hairlines: 0.008 mm at pose 203, 0.002 on the held kill line, and 0.036 mm from a pitch cliff. It also carries
compliance the model does not wear, a raised part that the sample weighting hides, and family items (T3, G4, S5).

## What the wearer gets (measured)

Bench is frozen exact Bench(110,360), the per-pose worst of +0.264 / -0.210 deg of dwell K. Sources: this audit's re-wear
`docs/alignment/remeasure/lowarm-kstop-knuckle-3r_bench.json` and the verifier's per-pose dumps
`docs/alignment/remeasure/lowarm-kstop-knuckle-3r_{bench,held}_perpose.json`.

**Reach.**

| | bench | held | lead |
|---|---|---|---|
| overhead (elev >= 150) taken | 8 / 28 | 18 / 71 | same |
| raised arm (elev >= 90) taken | 47 / 113 | 123 / 300 | same |

Every taken and lost pose is the lead's. The paired test shows 0 discordant takes and 0 discordant contacts. The 98 lost
workspace poses are fold 88, J3 stop 6 and contact 4, the parent's and the lead's attribution.

**Near-touch** (report-only, user decision 3).

| | bench | held | lead bench | lead held |
|---|---|---|---|---|
| taken poses with metal < 1 mm | 4 | 13 | 3 | 13 |
| taken poses with metal < 2 mm | 33 | 73 | 33 | 71 |
| taken poses with metal < 3 mm | 104 | 219 | 105 | 217 |
| gap at 1 mm | 20.86 | 25.73 | 19.92 | 25.23 |
| gap at 2 mm | 34.84 | 37.34 | 34.84 | 37.11 |
| gap at 3 mm | 85.66 | 83.14 | 86.16 | 82.52 |

- The bench's closest metal: pose 139 at 0.072 mm (link 2, forced pose, K 30.97) and pose 203 at 0.158 mm (hub 2's c10
  ring, at the wall-side play). On the lead, 203 reads 0.263.
- The sided play moves pose 230 from 1.045 to 0.948 mm, under 1 mm.
- Overhead taken poses: the 10th percentile of their min metal is 1.63 mm.
- Clip frames: 0 % of metal is under 2 mm, 0.21 % at 2-3 mm and 10.3 % beyond 14 mm. In-band 2-14 is 0.8968; read as
  3-14 it is 0.8947, which gives a gap of 18.81.

**Contact depth.**

| | contacts | summed depth | deepest |
|---|---|---|---|
| bench | 4 | 16.62 mm (lead 20.24) | 9.64 mm at pose 237 (plane 15, elev 165, axial -60, overhead) |
| held | 14 | 44.95 mm (lead 60.97) | 10.62 mm at pose 683 (plane 45, elev 165, axial -30) |

Five held contacts are deeper than 3 mm. The deep contacts are overhead, as on the lead.

**Workspace in-band.** NOT obtained. `tools/alignment_wear_probe.py` supports only the longdyad, parallelogram and
frontload families. The per-pose dumps carry in-band for clip frames only. Clip in-band is 0.896 bench and 0.895 held.

**Per part** (bench, re-measured `parts_ib14`).

| part | in band | median metal |
|---|---|---|
| ring2 (link 2's raised 440C stage-1 ring insert) | 0.179 | 15.6 mm |
| plate | 0.715 | 12.3 mm |
| L2 | 0.732 | |
| hub3 | 0.742 | |
| crank | 0.815 | |

Sample-weighted in-band is 0.897 and part-weighted 0.861. The lead reads 0.901 / 0.925.

**Mechanism.**

- Springs: none. Dwell K is held between metal on both sides: the inner groove wall blocks +K (drho/dK -0.0606 mm/deg)
  and stop A (K's own lug and set screw inside hub K) blocks -K.
- The +K wall load reaches the chain through the crank's 41 mm long arm. Its compliance is unmodelled: 0.06-0.22 mm at
  pose 203 per 0.05 N.m.
- Stops: K-own A and B, the J2 low-end dowel at K-eq 46.35, the J3 dowel and the knee window. The dowel cuts 0 poses.
  The largest taken K is 45.615 on bench and 46.268 on held, which is 0.08 deg under the dowel.
- Cuff twist: knee pins on MR63ZZ pairs, with no spring-held lag. R17 was not run on this row.
- Singular postures:
  - th, dwell: min 5.317 (held) and 5.34 (bench).
  - th, forced: min 5.006 at held pose 1054, about 4.92 with the stated 0.23 deg groove play. That play is not worn.
  - m_sub (the K sub-dyad) is under 1 deg on 100 held dwell poses.
- DOF and parts: 3 active (J1, J2, J3 on O20 v5) and 0 passive translations. Complexity 16.75 (tools/simplicity.py
  recomputes 16.75; the lead is 18.5).

## Findings

There are 9 findings, all watch. The ledger also carries the tool's non-ok checks.

1. **NEW-hairline-gates (watch).** The row is alive on gates that each pass by less than the design's own unmodelled error.
   - Pose 203 reads 0.158 mm against the round's 0.15 floor. The long-arm compliance is 0.06-0.22 mm per 0.05 N.m, 8-28x
     that margin.
   - The held paired difference is +0.4977 against the 0.5 kill line. Kit density was not measured; the parent's shift
     is +0.08, 40x the margin.
   - The stage-1 pin sits 0.036 mm inside the skirt pitch limit. At a_s 9.7 the drive is dead (dK_lim 0).
   - The held max K is 0.08 deg under the J2 dowel.
   - P5 bearings were chosen after P0 failed both sided gates (203 0.118; e- 0.408 > 0.29).

   Why the exo is not better than it reads: none of these margins is priced in v_gap. A real build at the soft end of
   the arm's stiffness puts 203 in contact (+0.54, the +0.2 probe reading's step). Action: price the hold's compliance
   (proposal A) and report borderline gates as such (proposal B).
2. **S2 (watch).**
   - Stage 1 at the buildable F+3.9 raises link 2's ring insert to a median 15.6 mm off the skin (0.179 in band), on 6
     samples per frame, 0.6 % of the weight.
   - Part-weighted in-band is 0.861 against 0.925 for the lead. Sample-weighted it is 0.897 against 0.901.
   - The parent, with the clash, had ring2 at 0.859 / 12.7 mm.

   Why the exo is not better: the wearer has a raised ring bump over hub 2 that the in-band number barely sees. Action:
   measure the row at kit density (`tools/sample_density.py measure lowarm-kstop-knuckle-3r`) and report ring2's
   envelope height in the CAD.
3. **M5 (watch).** The dwell hold is rigid in the model and compliant in the build (the crank's 41 mm long arm, 27-77 N/mm
   by the judge's beam estimate). The claim calls this "the number most likely to be optimistic". Action: model or
   measure the arm's stiffness and wear e+ plus deflection.
4. **T3 (watch).** The forced-pose th is 5.006 on the law value and about 4.92 with the stated 0.23 deg groove play, which
   is not worn. This is the family item the lead shares. Action: wear the groove play on forced poses (or rule it in
   the build tolerance).
5. **G4 (watch).** m_sub is under 1 deg on 100 held dwell poses. This is the lead's G4 item and is with the user.
6. **S5 (watch).**
   - The flood ran on the +0.264 bench wear only: full 18.60 (0 dropped), kNN 20.29, bench graph 50.45.
   - It did not run on the -0.210 wear, on the per-pose worst, or on held.
   - The parent's held kNN flood lost 8.14 points (22.64 -> 30.78).

   Action: run the held flood.
7. **M3 (watch).** The family's GAMED M3 is closed here by build specs the model does not carry:
   - a pocket in link 1b's plate, which cuts about 30-35 % of the bar root section; the swept arm metal reaches r 10.14
     against the pocket spec's r 10;
   - a 1.38 mm arm tip, against the CAD's 1.5 mm;
   - the stop-A set-screw bore, which has zero thread wall to the boss underside.

   The bench effect is 0: V-ARM changed 0 poses, and stop A sits inside the O20. Action: FEA of the pocketed root, and
   the bore fix in the CAD.
8. **G5 (watch).** The 1.75-point simplicity edge over the lead does not count what the hold needs: ISO P5 J2 bearings, an
   assembly-set thread-locked set screw, and a groove placed 0.036 mm from a cliff. Action: proposal C.
9. **R1 (watch).**
   - The dashboard shows the screen's self-measured verdict text ("the claim is the combined cell ... not yet measured").
     The row is verified for the cell alone, and the combined cell is still unmeasured.
   - The verifier's JSON outputs live in a session scratchpad, not in docs/concepts/verify. Before this audit's re-wear,
     6 of the tool's 12 checks read "missing".
   - The dashboard's plain gap reads 18.68, the row's 18.69.

   Action: commit the verifier outputs and replace the verdict text.

**Checked and not present.**

- **P1:** no search ran (step 0), and held - bench = +4.19, the lead's +4.09.
- **P2:** one config was worn on held, used as a kill line and not for selection.
- **P3:** every corner is reported (P0 18.72 included), and the worst corner is the claim.
- **P4:** no bench, judge or metric file is in the row's commits.
- **R2 / R3 / R4:** no refuted record, no best-of-many, and the number is not recomputed.
- **M1 / M2:** O20 everywhere, 0 passive translations, every joint a catalogue part.
- **M4:** K spans 0-45.6 deg.
- **T4:** no search bound.
- **T5:** depth is under the lead.
- **S3:** the short arm's underside was unsampled in the claim. The verifier sampled it, with 0 effect.
- **S4:** none.
- **S6:** not measured. ring2 is likely over-dense, which would *lower* this row's gap.
- **G1:** shared with the lead (33 / 33 poses under 2 mm). Report-only.
- **G2 / G3:** no spring.
- **G6:** not applicable.
- **T1:** report-only (user decision 3). Its one design-specific part, 203 sitting just past the round's 0.15 gate, is in
  finding 1.

## Numbers I could not get, and why

- **Workspace in-band:** the wear probe does not support this family.
- **Held continuity flood:** the verifier did not run it. The adapter does not run the flood, and adding it to a held
  wear was beyond the time box.
- **Kit-density gap:** `tools/sample_density.py measure` would take two more ~8-14 min exact wears. The farm budget is
  spent, and the local limit is 2 processes.
- **Cuff twist (R17):** not run on this row.
- **Long-arm stiffness:** there is no model of it anywhere in the repo.

## Proposals (not applied; none feeds the verdict)

- **A. Wear the hold's compliance.** For a dwell held through a compliant member, wear e+ plus the member's deflection
  at a stated wearer torque, e.g. 0.05 N.m. Effect today:
  - This row: the soft end (+0.55 deg) reads 203 at -0.06 mm, so 18.69 -> about 19.23 (the probe's 203 step, +0.54).
  - The stiff end (+0.14 deg) reads 203 at about 0.10 mm, so no change.
  - No other verified row wears a dwell play, so no other row moves.
- **B. Borderline gates are reported as borderline.** A gate passed by less than a stated unmodelled error of the same
  quantity is reported "borderline (unresolved)", not "pass". This is reporting only, and no number moves. Today it
  touches this row's 203 / held-line / pitch-cliff gates.
- **C. A precision line in the simplicity record.** Add a field listing the precision classes and assembly adjustments
  the design needs (P5 bearings, set-at-assembly screws), shown beside the complexity number. It is not scored. No
  number moves.
- **D. Catalogue entry T7, "Hairline gate stack"** (from NEW-hairline-gates).
  - Looks like: a candidate passes each of its round's kill gates by a margin smaller than an error source it names
    itself.
  - Detect: for each gate on the row, the margin against the claim's own stated unmodelled errors.
  - Here: this row (0.008 mm vs 0.06-0.22 mm, 0.002 vs 0.08, 0.036 mm to a pitch cliff).
- **E. Instrument note for catalogue R4 / the verifiers.** Under a worn play, checks that classify dwell poses by
  `dK != 0` misfile them:
  - the claim's V3 read th min 0.0 with 106 poses under 5;
  - V4 read 60.76 with 108 poses dropped;
  - `play_info` keeps only the last IK batch.

  The verifier's V3b fixed the th reading. Proposal: every play wear carries an explicit dwell mask, and a play-aware
  check refuses to run without it. No number moves.
