# desmo-window-knuckle-3r - buildable desmo: stage 1 lifted into link 2's underside, the crank's arm through a window in link 1b

Round 104, lens C (the built complexity frontier). desmo-conecut-knuckle-3r cell B (verified 18.98 frozen exact with the built
groove's blended law in the IK, cx 16.5) with ONE change: the stage-1 stack at hub 2. The verified model's groove sits at
F2+0.11..1.61, inside link 1b's J2 plate layer (F2+0..3.0), and the gen-9 CAD crosses link 1b by 1.39-1.50 mm on all 451 frames
(R6 1.50 FAIL). Here the groove is cut in a 440C insert pressed into link 2's UNDERSIDE, and the crank is one part whose short
arm drops through a window milled in link 1b's J2 plate, with an integral crowned O1.5 pin rising into the groove.
3 active DOF (J1, J2, J3), K slaved and never read, 0 passive translations, no springs, no gears / pulleys / cables.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask for.**
   * Read the level the way the scan defines it. `level_scan` in pipeline/conformal/param_cad/user_style_desmo.py scans the
     groove's MID-plane over hub 2's face. A groove whose insert sits on link 2's underside at F2+3.15 has its mid-plane at
     F2+3.9, not 3.15. A mid-plane at 3.15 would put the insert's lower 0.75 mm inside link 1b's plate over the whole J2
     sweep. So the honest level is 3.9, where the CAD's scan found 2 legal pins, not 6. I scan both levels and run 3.15
     only as a labelled, illegal control.
   * Make the stop order a gate, not a note. The J2 dowel must engage before the drive's ends. So the drive (groove rise +
     stage-2 slot) is built and gated to kdrive, J2's window ends at kj2 = 46.5, and its engagement is 0.30 deg of K later.
     Pass needs drive end >= kj2 + 0.30 + 0.25 (the K lead). Then measure how far the slot can actually grow before its
     plate meets hub K.
   * Price the out-of-rim insert at its new level with the claim's own sampler (rigid from the O20 rim to
     pitch_hi + 0.76 + 0.8), and separate that cost from the pin's cost with controls: the claim's level with the claim's
     pin; the new pin alone; the new level alone.
   * Keep everything else verified and unchanged: seats, law, stage 2 cell B, the knee, the J3 dowel, the blended IK.
2. **Rawest material.**
   * The posed skin itself: the exact signed-distance path behind Bench(110,360) and the fast cache behind Bench(60,160).
   * The model's own per-pose body transforms: the K, q2 and crank angles the drive follows on every bench and held pose.
   * The gen-9 CAD's own records: build.json, stage1_level_scan.json and VERIFY.md section 5 (the stop order as built).
3. **Methods and tools.**
   * The verifier's DCModel with --blend, loaded unchanged and subclassed: docs/concepts/verify/desmo-conecut-knuckle-3r.py.
   * The model's own stage-1 synthesis at the new level: exact 3-D groove, built-groove pressure angles, pitch / drift
     gates and crank-free slop.
   * A vectorised pin scan (a_s 7-12 x psi 40-260) through the same formulas, extended to kdrive.
   * Swept-footprint geometry for the window: the arm in link 1b's frame over the crank's stroke.
   * The frozen-shape protocol: fit on Bench(60,160) fast, worn ONCE on Bench(110,360) exact and on the held-out set.
   * tools/alignment_paired.py per-pose dumps for a paired comparison against the lead and desmo-conecut.
   * Compute is local only: the farm is closed, so at most 2 niced processes.
4. **What, other than me, shows the number is right.**
   * The control cell at the claim's level, which reproduces desmo-conecut's fit exactly (fast plain 13.27).
   * The bench, then the adversarial verifier, the alignment auditor (T5 depth from the dumps) and the gen-9 CAD checker's
     stop-order reading.
   * The red-team list: rest, overhead, across the body, behind the back, the stretched-wall poses at dK ~46, stop A
     and stop B.

## The mechanism (as modelled)

* Chain, seats, law (kK 2.1534), stage 2 cell B (O1.5 nose on link 1a, slot in the crank's tip plate), the two-pin knee and
  the J3 dowel are desmo-conecut's verified ones, unchanged.
* **Stage 1, raised.**
  * The groove is 1.52 x 1.5, in a 440C insert pressed into link 2's J2 pad from below.
  * Insert underside F2+3.15, which is 0.15 over link 1b's plate top F2+3.0. Groove mid-plane F2+3.9.
  * The groove centreline comes from the model's own synthesis at that level (glev_eff 2.039: the claim's clamp
    [-1, 1.5] is bypassed, and that is stated here).
  * The insert sector out of the O20 rim is sampled as metal by the claim's own code: from r 10.25 to
    r_out = pitch_hi + 0.76 + 0.8.
* **Crank, one part (17-4PH H900).**
  * The boss sits on link 1b on a D3 pin with 2 x MR63ZZ.
  * The short arm is arm_w x 1.5 at F2+1.6..3.1, from the crank axis to the pin's foot.
  * The pin is integral, O1.5 crowned, and rises from F2+3.1 to 0.1 under the groove roof. Its arm and pin metal replace
    the claim's on the contact list.
* **Window.**
  * The arm's swept footprint (crank turned by phi(K) over the stroke) plus win_c a side is milled through link 1b's J2
    plate.
  * Link 1b samples in that band are deleted (21 at the best configuration).
  * Reported: the inner radius (wall left over the O11 MR117 seat), the outer radius (past the O20 rim) and the sector.
* **Stop order.** The drive is built to kdrive and J2's dowel window ends at kj2. Poses past kj2 are lost to 'j2stop'.

## Results

(filled in below as measured; every number is quoted from a saved file)

### Spec corrections (measured, stated for the verifier)

1. **The level.** `level_scan` scans the groove MID-plane (its docstring). An insert on link 2's underside at F2+3.15
   puts the mid-plane at F2+3.9. My scan reproduces the CAD's counts through the model's own stage-1 formulas, extended
   to the drive end K 47.5: 7 feasible at mid 3.15 (CAD 6), 2 at mid 3.9 (CAD 2). The legal pins at 3.9 are:
   * a_s 9.9 / psi 150: PA 32.88, groove rc 1.03, pitch 7.59-9.85, crank-free play 0.162;
   * a_s 9.8 / psi 150: PA 31.86, rc 1.024, pitch 7.68-9.90, play 0.165.

   A mid-plane at 3.15 is not buildable, because the insert's lower 0.75 mm would sit in link 1b's plate layer over the
   whole J2 sweep. It is run only as a labelled control (k18).
2. **No pin at either level meets pitch <= 9.0** (the lead's note confirmed). The insert reaches r_out 11.41
   (pitch_hi 9.85 + 0.76 + the model's 0.8 wall) against the O20 rim at r 10, so the out-of-rim sector is priced as
   metal: 29 rigid samples, against 19 at the claim's level. The spec's "+1.26" (0.5 wall) would be 0.3 mm smaller. I
   kept the verified model's 0.8, which matches the gen-9 CAD's insert (r 6.05..10.96 at pitch 9.4).
3. **The stop order is buildable only in a narrow band.**
   * With the claim's pin, extending the drive to 47.5 cuts it at 47.25: the built-groove forward PA reaches the gate at
     K 47.50, as the gen-9 red team said (ablation 'kdrive47.5-only'). 47.25 would clear the J2-first need (46.5 + 0.30
     engagement + 0.25 lead = 47.05) by only 0.2 deg, and that level is not buildable anyway (control k17 fails 4 pair
     gates).
   * With the re-placed pin, the groove's PA first fails at K 52.3, so stage 1 is not the limit. The stage-2 slot is:
     at kdrive 48.5 the longer tip plate comes within 1.0 mm of hub K's O20 at rest (PLATE-hubK at K 0: the drive is
     dead, k1/k3/k5/...).
   * At kdrive 47.5 every gate passes. J2's dowel window ends at 46.5 and engages at ~46.80, so the drive's end is 0.45
     deg of K past the engagement plus the 0.25 K lead. The J2 stop carries its own load (pass condition met, narrow).

### Fast sweep, Bench(60,160), frozen-shape fit (plain gap / near-touch gap: metal < 1 mm counted as contact)

| k | cell | lev | a_s / psi | blend | kdrive | plain | near-touch | reach | ib14 | drive end | r_out | K play | fails |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | grid | 3.9 | 9.9 / 150.0 | 10.0 | 47.5 | 14.73 | 20.59 | 0.775 | 0.8777 | 47.5 slot-end | 11.41 | 0.167 | - |
| 1 | grid | 3.9 | 9.9 / 150.0 | 10.0 | 48.5 | 101.12 | 110.62 | 0.3312 | 0.8743 | 0.0 PLATE-hubK | 11.41 | 0.167 | stop-order |
| 2 | grid | 3.9 | 9.9 / 150.0 | 6.0 | 47.5 | 14.75 | 20.61 | 0.775 | 0.8775 | 47.5 slot-end | 11.41 | 0.33 | groove-slop |
| 4 | grid | 3.9 | 9.9 / 150.0 | 8.0 | 47.5 | 14.68 | 20.52 | 0.775 | 0.8782 | 47.5 slot-end | 11.41 | 0.167 | - |
| 6 | grid | 3.9 | 9.9 / 150.0 | 12.0 | 47.5 | 14.72 | 20.58 | 0.775 | 0.8778 | 47.5 slot-end | 11.41 | 0.167 | - |
| 8 | grid | 3.9 | 9.8 / 150.0 | 10.0 | 47.5 | 14.73 | 20.59 | 0.775 | 0.8777 | 47.5 slot-end | 11.46 | 0.169 | - |
| 10 | grid | 3.9 | 9.8 / 150.0 | 6.0 | 47.5 | 14.75 | 20.61 | 0.775 | 0.8775 | 47.5 slot-end | 11.46 | 0.25 | - |
| 12 | grid | 3.9 | 9.8 / 150.0 | 8.0 | 47.5 | 14.67 | 20.51 | 0.775 | 0.8783 | 47.5 slot-end | 11.46 | 0.169 | - |
| 14 | grid | 3.9 | 9.8 / 150.0 | 12.0 | 47.5 | 14.72 | 20.58 | 0.775 | 0.8778 | 47.5 slot-end | 11.46 | 0.169 | - |
| 16 | arm_w 2.5 | 3.9 | 9.9 / 150.0 | 10.0 | 47.5 | 14.73 | 20.59 | 0.775 | 0.8777 | 47.5 slot-end | 11.41 | 0.167 | - |
| 17 | CONTROL claim level | 0.861 | 9.529 / 149.71 | 10.0 | 46.5 | 13.27 | 19.05 | 0.775 | 0.8923 | 46.5 slot-end | 10.96 | 0.174 | 4 pair gates (not buildable) |
| 18 | CONTROL mid 3.15 (illegal) | 3.15 | 9.8 / 150.0 | 10.0 | 47.5 | 14.62 | 20.49 | 0.775 | 0.8788 | 47.5 slot-end | 11.29 | 0.169 | insert in link 1b's plate |

(k1, 3, 5, 7, 9, 11, 13, 15: kdrive 48.5, all dead on PLATE-hubK.) The control k17 reproduces desmo-conecut's own fit exactly:
plain 13.27, reach 0.775, ib14 0.8923, the verifier's fit_fast. So the model's additions are neutral at the claim's level.

**Attribution (fast).**
* Reach is identical (0.775, fold 31) in every legal cell. Neither the K law nor the stop order loses a pose.
* The whole cost is in-band: ib14 0.8923 -> 0.8777-0.8783, i.e. +1.40 to +1.46 plain points.
* The new pin at the OLD level (ablation, not in the sweep file) cuts the drive at K 36.75 (s1b-pa-pin, reach 0.744). So
  the pin is only legal where it was re-placed.
* The new level with the OLD pin fails the pitch gate at K 0 (reach 0.331).
* The mid-3.15 control (2.29 mm up, r_out 11.29) costs +1.35. So the loss comes from LIFTING the out-of-rim insert
  sector, not from its extra 0.45 mm of radius: the samples rise out of the 14 mm band.
* The kdrive extension 46.5 -> 47.5 costs 0.00 (same numbers at 46.5 and 47.5 with the new pin).

### The claim wear: frozen exact Bench(110,360), worn ONCE (pre-registered config k4)

The config was picked by the spec's rule among the two legal pins: K play <= 0.25, rc >= 1.0, smallest pitch hi. That is
a_s 9.9 / psi 150, lev 3.9, blend 8, kdrive 47.5, kj2 46.5; near-touch fast 20.52, 0.01 off the best k12. The fit is on
Bench(60,160) fast, the shape is frozen, the blended IK is the 18.98 record's, and the per-pose dumps are written. Saved
outputs: docs/concepts/verify/desmo-window-knuckle-3r_v_{bench,held}_frozen.json and
docs/alignment/remeasure/desmo-window-knuckle-3r_{bench,held}_perpose.json.

| wear | gap | score | reach | ib14 | ib10 | contact | near-touch 1 mm | min metal (taken) | overhead | dK taken max | min th margin |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bench exact 360 | **20.43** | 92.57 | 0.7278 (262) | 0.8785 | 0.5622 | 0.0106 (4) | 22.07 | 0.07 mm | 8 / 28 | 45.62 | 5.181 |
| held out (861 ws taken) | **24.62** | 91.05 | 0.6922 | 0.8776 | 0.5614 | 0.016 (14) | 27.47 | 0.33 mm | 18 / 71 | 46.27 | 5.006 |

**Paired, per pose** (tools/alignment_paired.py compare, docs/alignment/remeasure/desmo-window-knuckle-3r_vs_*_paired.json).
The reach and contact poses are identical (0 discordant takes, the same 4 / 14 contacts).

| comparison | bench diff | 90 % CI | held diff | 90 % CI | P(window better) |
|---|---|---|---|---|---|
| vs conecut-knee-knuckle-3r, the lead (18.28 / 22.38) | +2.15 | [0.79, 2.36] | **+2.23** | [1.17, 2.31] | 0.000 |
| vs desmo-conecut-knuckle-3r with blend (18.98 / 23.19) | +1.45 | [0.79, 1.56] | +1.42 | [1.17, 1.51] | 0.000 |

The whole difference is in-band, on both sets.

**Where the 1.45 points go**, from the frozen run's per-part in-band (parts_ib14).
* ring2, the out-of-rim insert sector: 29 samples, mean 16.8 mm from the skin, 15.1 % in band. At the claim's level it
  was 19 samples at 54 % in band.
* Every other part is unchanged.
* Fast ablation with ring_rigid=0 (the sector's skin samples removed): ib14 0.9001 at the new level vs 0.8992 at the
  claim's. So the raised sector costs 2.19 fast points against the old sector's 0.69: +1.50, matching the +1.45 frozen.

## Verdict: DEAD (pre-registered kill, both conditions)

* Frozen exact Bench(110,360) is 20.43, above the 19.45 kill line and 2.15 above the lead's 18.28.
* Held out, paired, it is +2.23 worse than the lead, past the 0.5 kill line.
* The mechanism is buildable as specified, with three caveats from the red team below, at cx 16.25 with 0 passive
  translations.
* The stack fix itself costs nothing in reach, contact, the stop order or the drive's gates. It loses only in-band.
  Lifting stage 1 above link 1b's plate lifts the insert's out-of-O20 sector 3.04 mm. That sector cannot shrink: both
  legal pins have pitch hi 9.85-9.90 against the 34.47-deg PA gate, so r_out is 11.41-11.46 with the 0.8 wall. At its
  new height it sits 16.8 mm (mean) over the skin.
* So the built desmo frontier stays at 18.25-18.5 (the conecut / slipper builds), not 16.25 at <= 19.45.

**Convergence gate** (score points, near-touch objective, over the 18 legal rows of 32 tries in sweep order):
* best gain over the second half: 0.007;
* over the last third: 0.007;
* top-5 spread: 0.011.

The best near-touch is refine k26 (a_s 9.778 / psi 149.87, blend 12.3, kdrive 48.0): 20.49 near-touch, 14.65 plain. That
is 0.03 better than the worn k4, which cannot close the 0.98 to the kill line, so it was not re-worn.

The gate passes. The morphology's free parameters cannot move the limiter:
* the level is fixed by the stack (insert underside = plate top + 0.15);
* the pitch is fixed by the PA gate (2 legal pins);
* blend 6-12, kdrive, arm_w and win_c move the gap by <= 0.08.

## Red team (measured, best config)

* **Stop order: met, narrowly.**
  * The drive ends at K 47.5. J2's dowel window ends at 46.5 and engages at ~46.80, so the drive clears the engagement
    plus the 0.25 K lead (47.05) by 0.45 deg.
  * The slot can grow to 48.0 (kdrive probes k19-k21: drive end 47.75 / 48.0 / 48.0, gap unchanged). At 48.5 the longer
    tip plate comes within 1.0 mm of hub K's O20 at rest and the whole drive is dead (PLATE-hubK at K 0).
  * Stage 1 is not the limit: the re-placed pin's built-groove PA first fails at K 49.40 (blend 8).
* **The point that pinches (spec flaw).** The spec's arm layer F2+1.6..3.1 leaves the arm's top 0.05 mm under the
  insert's underside (F2+3.15), below the 0.15 running gap between the crank and link 2. Per taken fast pose, the arm's top
  line comes within 0.04 mm of link 2's metal (pose 60). Fix: drop the arm to F2+1.45..2.95. That metal is interior and
  off the skin-check list, so the bench is unaffected.
* **Window size (structural).**
  * The crank axis meets hub 2's plate layer 17.2 mm from hub 2's axis (azimuth 58.9). An arm kept at the plate layer
    all the way to the boss needs a window r 6.55..18.69 over a 48.1-deg sector. That is 8.7 mm past the O20 rim, not
    the ~0.9 the judge assumed.
  * The wall left over the O11 MR117 seat is 1.05 mm (>= 0.8: passes).
  * Link 1b's sampled plate keeps 42-86 mm of arc at r 7-10 against a 1.9-6.3 mm window there. Past the rim the window
    crosses link 1b's strap root.
  * If the arm instead climbs onto link 1b's top just past the insert (r ~11.7), the window shrinks to the judge's
    figure. The arm then shares the layer above F2+3.0 with link 2's J2 ring and strap, which is the crank-vs-link-2
    clearance above.
  * Either way the open-rim housing needs the M5 / FEA check before any CAD. That check was not run here.
* **K play.** Crank-free 0.167 deg nominal, 0.251 at worst tolerance (c 0.015), just over 0.25, like the parent's 0.261.
  The th margin is the parent's (5.181 bench / 5.006 held). 0.167 deg of play x dth/dK 0.403 takes the held margin to
  ~4.94 (the lead's T3 watch item, carried).
* **Pair checks.**
  * Insert vs link 1b's plate top: 0.15 by construction.
  * 32 link-1b-member samples inside the insert's slab are the O20 cylinder's side-wall ring (r 10.0, F2+4.08). The model
    attaches that ring to link 1b's member by convention; in the gen-9 stack that wall is link 2's J2 ring, the insert's
    own seat. So it is not an overlap, and the check now excludes the r = HUB_R ring. Rows k19-k21 carry the flag from
    before this fix.
  * Plate vs horn: min radial gap 0.15 on all 372 taken poses (V2).
* **Named poses** (the parent's, unchanged kinematics): rest taken; overhead 8 / 28 taken; across the body taken;
  behind the back, abduction 90 with internal rotation, and extreme external rotation (dK 62 past stop B) lost to the
  fold. Contacts: 205 (hub 2 -4.28), 237 (crank -9.47), 264 (-1.17), 316 (link 2 -1.23).

## What this teaches (beyond this morphology)

* For a groove drive at a J2 hub, the stage-1 stack level is a skin-band variable, not just a fit variable.
  * Metal outside the O20 rim pays for its height directly: 3.04 mm up cost 1.45 points at only 29 samples.
  * A buildable desmo must keep stage 1 inside the O20 footprint (pitch_hi + 1.56 <= 10, i.e. pitch <= 8.44) or below
    the plate top. At the verified law and drive no legal pin has pitch <= 9.7 at any level (CAD scan and this scan).
  * The next lever is the drive geometry: the crank axis dR, the ratio g, or the PA budget. The seat is not the lever.
* The J2-first stop order costs nothing in reach. It needs the stage-2 slot to run 0.55-1.0 deg of K past J2's window,
  and hub K's O20 caps that at ~48.0 at r_c 16.18.

## Audit (death audit, 2026-10-18)

The auditor's job was to try to refute the death. The death **stands**, but the measured cause is about 3.5x smaller than
the screen said. Most of the 1.45-point "lift cost" is a sampling-density artefact inherited from the parent's ring
sampler.

**Convergence gate.** Reproduced from the sweep at 0.007 / 0.007 / 0.011 score points (18 legal rows of 32). It passes.
The sweep is narrow (lev 3.9 in every legal row, a_s 9.7-9.98, psi 149.4-150.6), but the stack and the pin scan force
that narrowness: lev is pinned by link 1b's plate top + 0.15, and only 2 pins are legal at mid 3.9. No region was missed.

**Finding: ring2 is sampled 4x denser than every other member (new).**
* tools/concept_bench.py asks for skin-facing metal sampled evenly at ~1 pt / 4 mm2, and the kit's cell is 4.0 mm2
  (tools/concept_kit.py line 293). Hubs follow it: 80 samples on an O20 crown of 314 mm2.
* The stage-1 ring sector (docs/concepts/models/desmo-conecut-knuckle-3r.py lines 252-261, inherited unchanged) steps
  0.5 mm radially x 2.0 mm of arc, which is 1 pt / 1 mm2. At this design's r_out 11.41 that gives 29 samples (rings r
  10.25 / 10.75 / 11.25) on a sector of ~28 mm2. The kit's density gives ~7.
* in-band is a share of samples, so the 15 %-in-band sector weighs 4x in ib14.
* The honesty audit flags only sparse sampling (< 1 pt / 16 mm2), never over-dense sampling, so nothing caught it. The
  same check could be gamed the other way, by over-sampling well-placed metal.

**Measured at the kit's density.** ringfix keeps the sampled ring nearest the sector's mid radius at 2 mm of arc: 10
samples, which is still denser than the kit and so conservative. Reach, follow and contact are untouched, because only
the rigid in-band samples change.

| measurement | as screened | kit density |
|---|---|---|
| fast, worn k4, near-touch | 20.52 (ib14 0.8782) | 19.02 (ib14 0.8924) |
| frozen exact bench (re-weighting of the saved per-part in-band) | 20.43 | 19.01 (10 samples) / 18.80 (area-exact 7) |
| frozen exact held (re-weighting) | 24.61 | 23.20 / 23.00 |
| parent desmo-conecut+blend bench (re-weighting) | 18.99 | 18.57 / 18.49 |
| parent held | 23.18 | 22.76 / 22.68 |

Sources:
* docs/alignment/remeasure/desmo-window-knuckle-3r_ringfix_fast.json and _ringorig_fast.json;
* docs/alignment/remeasure/desmo-window-knuckle-3r_ringdensity_reweight.json;
* the full frozen exact re-wear (docs/concepts/verify/desmo-window-knuckle-3r_ringfix_audit.py `wear bench|held`) was
  started and then stopped. At load 18 it ran at ~1/3 of a core, which projects to ~55 min for the bench alone (1060 s at
  a full core). The frozen numbers above therefore come from the saved per-part in-band. That re-weighting is exact as
  long as the kept ring carries the sector's in-band share. The fast run checks it: the measured subsample moved the
  fast near-touch by 1.50 points, against 1.42 from the bench re-weighting (10 samples). The lead can run that
  command for the exact confirmation.

**What the correction changes.**
* **The lift cost.** Like for like with the parent at the kit's density, raising stage 1 by 3.04 mm costs +0.31..0.44 on
  the bench and +0.32..0.44 held, not +1.45 / +1.42.
* **The bench kill line passes.** The bench sits at 18.80-19.01, under the pre-registered 19.45.
* **The held kill line still fails, so the death stands.** Held is 23.00-23.20 against the lead's 22.38: +0.62..+0.82,
  past the 0.5 line. Takes and contacts are identical to the lead (0 discordant), so all of that gap is in-band. The
  window design sits at ib14 0.892-0.895 against the lead's 0.901 even after the fix.
* **The family moves too (a measurement change, not a design change).** The parent desmo-conecut (verified 18.98) would
  read 18.49-18.57 at the kit's density. desmo-slipper-knuckle-3r's model (line 283) and its descendants use the same
  sampler. The lead should re-wear those rows at the kit's density before ranking the desmo family against the lead.

**One-line reason.** The buildable stack loses on held-out in-band, +0.62..0.82 over the lead at the corrected density
(identical takes and contacts). The screen's 1.45-point lift cost was mostly ring2's 4x over-sampling: the true cost is
0.3-0.44.
