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
