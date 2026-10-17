# desmo-conecut-knuckle-3r - Desmo-conecut knuckle with a pinned-horn stage 2 (round 13, the main track's knuckle lens)

desmo-slipper's spring-free, roller-free K drive worn on conecut-knee-knuckle-3r's knee and J3 dowel stop, with stage 2
inverted (cell B): the nose is a 440C dowel pressed into link 1a, the two-walled slot is cut in a small Ti plate on the
crank's tip. Cell A (the desmo stage 2 unchanged) is the measured control; cell C moves stage-1 ratio into stage 2 (g 2.6-2.8).
3 active DOF (J1, J2, J3), K slaved and never read, 0 passive translations, no springs, no gears / pulleys / cables.

## Deeper-version answers (written first, before any number)

1. **What a top mechanism designer would do that the spec does not ask for.**
   * Check where the inverted slot actually goes. The slot is the nose's path in the crank's frame. A 3.66 mm slot is
     short, but its direction decides whether the plate around it fits next to hub K's O20 stack (the plate sits at the
     arm-tip layer, inside the stack's 12.25 mm height). The spec gates the boss against hub K; I gate the plate too.
   * Treat the slot length as a design variable with a physical end. The slot's far end is a real stop B. Cut it to the
     stroke the taken poses need (bench 45.62, held 46.27 deg of K), not to the K law's full 64.5 deg.
   * Read the pressure angle on the built pocket (the union of nose discs), not on the centreline. At the closed end the
     nose sits at the crank / link-1a relative pole (0.68 mm/rad). There the contact normal comes from the pocket's
     shape, not the path's tangent.
   * Keep everything verified unchanged: the lead's seats, law and drive (beta / r_c / g), desmo's stage 1 at a_s 9.5 /
     psi 150, conecut's knee and dowel. Compare at equal samples (S6), because deleting a well-placed lug band reads
     as an in-band loss by sample weight alone.
2. **Rawest material.** The posed skin itself: the signed-distance cache behind Bench(60,160) and the exact path behind
   Bench(110,360). Also the model's own per-pose body transforms (the K, q2 and crank angles the drive must follow on
   every bench and held-out pose), and the drive geometry the verified lead was built on
   (docs/research/slipper_mechanism/geo_bench.npz) as a cross-check of the inverted-cam synthesis.
3. **Methods and tools.**
   * Exact spherical-cam synthesis per 0.25 deg of K (every axis passes through GH). Pressure angles are taken at the
     nose centre, because the contact force passes through it.
   * A morphological pocket check: the nose disc must stay inside the union of swept discs, with K bisected to
     0.005 deg and the crank held.
   * Per-K-step clearance of the plate against both hubs, using the kit's signed-distance cylinders.
   * The verified chain loaded unchanged (desmo-slipper -> slipper-nose -> roller-longdyad -> sidecar-roller-flank),
     tools/concept_bench.py, and the frozen-shape protocol for any claim.
   * Compute is local only: the farm window has closed, so I run at most 2 niced processes.
4. **What, other than me, shows the number is right.**
   * Cell A, reproduced exactly (13.18 fast, the proposer's number), as the control.
   * The bench (fast, then exact frozen).
   * The adversarial verifier and the alignment auditor (T5 depth, gate re-definitions).
   * The red-team list: rest, overhead, across the body, behind the back, the stretched-wall poses at dK ~46, the
     closed end of the slot (stop A) and the slot's far end (stop B).

## What was built

docs/concepts/models/desmo-conecut-knuckle-3r.py loads desmo-slipper-knuckle-3r.py (which loads the verified lead
slipper-nose-knuckle-3r, SN_CELL=lead) unchanged. It then adds three things:

* conecut's J3 dowel stop on q3' = q3 + knee phi;
* conecut's verified knee (lE 97.14, lc 24.35, phiE 0.75, phib -91.80, ang_min 25.22, MR63ZZ stk 6.0);
* a cell switch `stage2`.

**Cell A** (`stage2 "A"`) is desmo-slipper's drive unchanged: the lead's flank lug band plus desmo's outer wall, with the
nose on the crank. It reproduces the proposer's fast plain gap exactly: 13.18 (reach 0.775, ib14 0.8932, dK_lim 49.75,
pressure_horn).

**Cell B** (`stage2 "B"`, the claim cell) inverts stage 2:

* The parent's flank synthesis still builds the crank arm, the K grid and the crank-vs-hub clearances. Its flank-only
  gates are switched off (flank PA, lift-off, cusp, contact-off-lug, roller-vs-hub K). The flank lug band, desmo's outer
  wall and the crank-borne nose are deleted, both as metal and as contact / strap entries.
* The nose is pressed in a boss on link 1a at the drive's contact seat C0 (beta, r_c). The boss is an O(2 boss_r) x 3
  disc on the lug sphere, rooted to hub K's rim. Its path in the crank frame, Z = Rc^T Rk^T C0, is the slot. The slot
  is cut in a Ti plate at the crank's arm-tip layer (underside R0 + 1.65), as a stadium of half-width
  nose_r2 + c_slot2 + wall2 around Z.
* Gates, per 0.25 deg of K:
  * both pressure angles at the nose centre <= 43 - atan(mu) (`wall2B-pa`);
  * the slot is cut to `kslot`, and its far end is stop B (`slot-end`);
  * plate vs hub K and hub 2 >= 1.0 mm (`PLATE-hubK` / `PLATE-hub2`);
  * crank low arm vs boss >= 1.0 mm (`CRK-BOSS`, also checked per pose by the parent's collide());
  * boss vs hub K's O20: rK(C0) - boss_r >= 11 (`boss-hubK`).
* The built pocket is the union of nose discs (nose_r2 + 0.01) along the 0.02-deg path. With the crank held, K is
  bisected for the slop (gate 0.25 deg). The exit direction is the contact normal, so the pressure angles are read on
  the pocket itself (`pocket-pa`, gate 43 - atan(mu) for K0 >= 0.5; K0 = 0 is stop A and is reported).
* **Stage 1 is read on the BUILT blended groove** (`s1_read "built"`, the default in cell B). This is a measurement
  change for the auditor, made as the planner's gate (a) asks:
  * the forward (pin-side) pressure angle is gated wherever the pin moves (K > 0);
  * the cap side is gated outside the blend (x >= half-blend);
  * inside the blend the cap side is the dwell lock (up to 90 deg) and is reported, not gated.

  `s1_read "linear"` restores desmo-slipper's reading. Measured at the verified a_s 9.5 / psi 150 under that reading:
  stage 1's cap side is 35.25 deg at the dwell exit, which fails at mu 0.15 at K 0, for both cell A (sweep k 55) and
  cell B (k 59). At a_s 9.0 / psi 154, stage 1 passes the linear reading at mu 0.15, but cell A's flank then binds at
  dK 43.25 (fast plain 15.13, k 58; the proposer's number).

## Results (Bench(60,160) fast for the search, Bench(110,360) exact frozen for the claim)

| config | mu | fast plain | frozen exact Bench(110,360) | reach | ib14 | contact | overhead | dK lim / why |
|---|---|---|---|---|---|---|---|---|
| cell A (control, desmo stage 2, nose on the crank) | 0.087 | 13.18 (= proposer) | 18.87 (proposer; not re-run) | 0.7278 | 0.8941 | 4 | 8/28 | 49.75 flank PA |
| cell A at its verified a_s 9.5 / psi 150 | 0.15 | 86.67 (stage 1 linear cap side at K 0) | - | | | | | 0 s1-pa-cap |
| cell A at a_s 9.0 / psi 154 | 0.15 | 15.13 | - | 0.756 fast | | | | 43.25 flank PA |
| cell B, stock seat r_c 15.37 (O2 nose) | 0.087 | 86.77 | - | | | | | 0: plate vs hub K 0.12 mm |
| cell B, seat r_c 16.0, O1.5 nose, wall 0.8, glev -0.5 | 0.15 | 13.54 | **19.27** | 0.7278 | 0.8901 | 4 | 8/28 | 46.5 slot end |
| **cell B claim (k57, pre-registered)** | 0.15 | **13.31** | **19.04** (score 93.08) | 0.7278 | 0.8924 | 4 (0.0106) | 8/28 | 46.5 slot end |

The claim config (k57) is r_c 16.176, beta -177.169, nose O1.5 (nose_r2 0.75), c_slot2 0.01, wall2 0.9, boss_r 2.5,
kslot 46.5, glev -1.0, blend 10, a_s 9.529, psi 149.71, mu 0.15, s1_read built, plus conecut's knee / J3 stop and the
lead's seats and law.

* Frozen exact, near-touch: gap at 1 mm 20.68 (3 poses), at 2 mm 35.13. The closest metal over taken poses is 0.07 mm
  (pose 139, plane -60 / elev 60 / axial 105); then 0.26 mm (203) and 0.62 mm (379).
* Lost poses: fold 88, contact 4, j3stop 0. The takes and contacts are identical to conecut's (262 taken).
* Overhead (elev >= 140): taken 8 of 28, reach 0.286, ib14 0.895. Workspace in-band: all 0.863, elev 90-140 0.831,
  overhead 0.933.

**Equal-sample (S6) comparison.**
* Against conecut (same knee, E strap 164 samples): 19.04 vs 18.28. The whole +0.76 is in-band by sample weight. Takes
  and contacts are identical.
* Decomposition of that +0.76:
  * with the stage-1 ring sector removed (decomposition only; the ring is real metal), B reads 18.37, so the stage-2
    inversion itself costs +0.09;
  * desmo's stage-1 ring sector outside O20 costs +0.67 (19 samples at 0.54 in band, median 13.8 mm).
* At the lead's E-strap count (104 samples, desmo-slipper's): B reads 19.61, against desmo-slipper's 18.95 and conecut's
  18.67 at equal strap.

**Drive at mu 0.15 (both stages, claim config).**
* Stage 2 (inverted):
  * pressure angles on link 1a 24.7 and on the crank 14.6. On the built pocket: 25.5 / 32.0 (gate 34.47).
  * Its own PA stroke limit is 64.5 deg of K at mu 0.087-0.15 and 61.0 at 0.20. Cell A's flank stops at 43.25 at
    mu 0.15.
  * The slot is 3.72 mm long; the plate is 7.04 x 3.32 x 2.5. Plate clearance to hub K's O20 is 1.23 mm; crank low arm
    to the boss is 19.9 mm.
  * Boss vs hub K margin: 3.68 mm beyond the 10 mm rim.
  * Slop with the crank held: 0.04 deg. The closed end (stop A, the relative pole at 0.525 mm/rad) engages at 0.04 deg.
* Stage 1 on the built groove:
  * the forward (pin-side) pressure angle first exceeds 34.47 at K 47.50, 1.0 deg past the slot's end, and the cap side
    outside the blend at K 58.5;
  * inside the blend the cap side runs 28.5 -> 90 deg (the dwell lock);
  * crank-free slop 0.174 deg (0.261 at the worst-tolerance c 0.015: over 0.25), held + free 0.214.
* Groove centreline radius at the onset: 1.01, ridge 0.25 mm. Line-contact Hertz at 25 N: about 1.5 GPa with the
  O1.5 440C pin. Ti-6Al-4V yields at p0 ~1.4-1.5 GPa, so the pressed 440C ring insert stays the default (cx 16.5).
  Blend 24 lifts the ridge to 0.34 mm (~1.35 GPa) at an equal fast number (k128, 13.31). That is not enough to drop the
  insert.

**Search.** 146 configurations on Bench(60,160) fast, run locally because the farm window is closed:
* a coarse seat / hardware grid;
* a 74-point focused random grid at mu 0.15;
* a 32-point local refinement.

The best fast plain gap is 13.30 (k131 / k135), a tie with the pre-registered k57 (13.31). The convergence gate over
the 121 built-read cell-B rows (score points): gain over the second half 0.004 (< 1), over the last third 0.004 (< 0.5),
top-5 spread 0.004 (< 3). It **passes**.

Where the search space ends (measured):
* plate vs hub K binds below r_c ~16.0 with an O1.5 nose, or ~16.2 with O2;
* the inverted-cam PA fails at rest for r_c >= 17;
* stage 1's built forward PA binds below dK 46.3 when a_s / psi leave 9.4-9.6 / 149.5-150.5;
* the slot can be cut to 48-49.75 at r_c 16.4-16.5, but reach does not change (0.775 fast). The stroke past 46.5 is
  not what limits this family. Its fold wall is the seat cap, as round 12 found.

## Held out (the claim config, frozen, not refit)

| | held gap | reach | ib14 | contact | overhead | dK taken max |
|---|---|---|---|---|---|---|
| desmo-conecut cell B (k57) | **23.24** | 0.6922 | 0.8914 | 0.016 (14) | 18/71 | 46.27 (slot end 46.5) |
| conecut-knee-knuckle-3r | 22.38 | | | 14 | | |
| desmo-slipper-knuckle-3r | 23.90 | | | | | |
| slipper-nose (lead) | 23.45 | | | | | |

Lost poses: fold 260 and contact 14. Near-touch: gap at 1 mm 26.09; closest metal 0.33 mm. Held out, the knee never
slides (0, as on conecut; the lead slipper-nose slid on 32). The held stroke uses 46.27 of the 46.5 deg the slot allows.

## Red team (own best config, frozen exact Bench(110,360))

* **The pose that jams.** None within the stroke. Every drive gate holds at mu 0.15. The tightest margins:
  * stage 1's forward pressure angle on the built groove exceeds 34.47 at K 47.5, only 1.2 deg past the held stroke
    (46.27). A friction coefficient above 0.15 or a K overshoot meets stage 1 first. Stage 2 has 18 deg of margin.
  * the worst-tolerance crank-free slop (groove c 0.015) is 0.261 deg, over the 0.25 gate. Held + free nominal is 0.214.
* **The point that pinches.** The 4 contact poses are conecut's. The new metal appears in them:
  * pose 237: the crank arm reaches -9.42 and the tip plate -5.87;
  * pose 264: the hub-K / boss edge -1.17, the crank -1.02, the plate edge -0.37;
  * pose 205: hub 2 -4.28 and desmo's cap-ring sector -3.64;
  * pose 316.

  The closest taken pose is 139 at 0.07 mm (plane -60 / elev 60 / axial 105). The closest held-out metal is 0.33 mm.
* **The optimistic number.**
  * The stage-1 pressure angles are read on the built groove (cap side inside the blend reported, not gated). Under
    desmo-slipper's linear read the same placement fails at K 0 at mu 0.15. The auditor must rule on this reading.
  * The plate clears hub K's O20 by 1.23 mm. A crank-pivot position error of ~0.25 mm toward the K axis takes it to
    1.0.
  * The plate's sample count (8) is small, and its in-band (0.72) enters the bench at that weight. The S6 numbers
    above show the comparison at equal strap samples.
* **Named poses (claim config).**
  * Taken: rest (dK 4.6), overhead axial -135 (dK 5.8), across the body plane 120 / elev 90.
  * Not taken: overhead axial 0 is j3stop; overhead plane 90, behind the back, abduction 90 and across-body internal
    rotation are fold; extreme external rotation (plane 30 / elev 30 / axial 150) needs dK 62.1, past stop B.

## Verdict

**Screened, not a new lead. It is a complexity / friction frontier point at the lead's reach.**

Cell B is the first desmo-family drive that holds mu 0.15 on both stages: a nose fixed in link 1a and a 3.7 mm slot in
the crank's tip. It has no spring, no roller, no flank lug band and no outer wall.

| design | frozen exact Bench(110,360) | score | held | cx |
|---|---|---|---|---|
| desmo-conecut cell B (this) | 19.04 | 93.08 | 23.24 | 16.5 (16.0 without the groove insert) |
| conecut-knee-knuckle-3r | 18.28 | | 22.38 | 18.5 |
| desmo-slipper-knuckle-3r | 18.95 | | 23.90 | 15.75 |

* Against conecut: +0.76 on the bench and +0.86 held out, all in-band by sample weight. The takes are identical, and
  the contacts are identical on the bench.
* Against desmo-slipper: +0.09 on the bench and -0.66 held out. Desmo-slipper jams at mu 0.14; this one holds mu 0.15.
* The limiter is unchanged: the family's J2 fold (88 / 260 poses). The slot could be cut longer (49.75) and fast reach
  would not move, so the drive stroke is not this family's reach lever.

## Next

1. Verifier, on the claim config:
   * tools/alignment_paired.py dump against conecut and desmo-slipper (bench + held: T5 depths at 205 / 237 / 264 /
     316);
   * the continuity flood;
   * the dense groove scan (desmo-slipper-knuckle-3r_groove_scan.py) on this placement;
   * K play carried into th;
   * an envsel wear.
2. The auditor rules on the built-groove stage-1 reading. It is the condition for every desmo-family number at
   mu >= 0.12.
3. The in-band lever is desmo's cap-ring sector (+0.67). A ring that stays inside O20 at the lead's g fails forward PA
   (the proposer: no groove inside O20 passes 34.47 at g 2.39-3.0). Cell C's g 2.8 lowers and narrows it but is
   knife-edged on the seat (r_c 13.5; at g 2.39 the plate gate here binds below r_c ~16.0, so C at 13.5 likely fails it - measure first).
4. Cell C was not built inside the time box.

## Verification (independent skeptic, 2026-10-17 20:10-20:55 UTC)

**Verdict: VERIFIED at v_gap 18.98 (score 93.10)** on Bench(110,360), exact path, frozen shape, with the built groove's
blended law in the IK. The champion spherical 3R scores 75.94 on the same bench (the risley-turret verifier's checks, the
reference this family's verifications use; 66.97 through the offset-skin-normal verifier). No hard rule is broken. Not a
new lead: the lead is 18.49, the tie-ruled lowest verified row is conecut at 18.28.

Harness: `docs/concepts/verify/desmo-conecut-knuckle-3r.py`. It loads the claim's model unchanged and wears it through
its own frozen protocol, then adds the checks below. Dense groove scan:
`docs/concepts/verify/desmo-conecut-knuckle-3r_groove_scan.py`. Local only, at most 2 niced processes (the farm window
is closed).

| wear | gap | score | reach | ib14 | ib10 | contact | overhead | connected (full flood) |
|---|---|---|---|---|---|---|---|---|
| claim reproduced, linear-law IK, bench | 19.04 | 93.08 | 0.7278 | 0.8924 | 0.5625 | 4 poses (0.0106) | 8/28 | 19.04 (0 dropped) |
| **blended-law IK (verified), bench** | **18.98** | **93.10** | 0.7278 | 0.8930 | 0.5629 | 4 poses (0.0106) | 8/28 | 18.98 (0 dropped) |
| claim reproduced, linear-law IK, held out | 23.24 | 91.55 | 0.6922 | 0.8914 | 0.5617 | 14 poses (0.016) | 18/71 | 23.24 (0 dropped) |
| blended-law IK, held out | 23.19 | 91.57 | 0.6922 | 0.8919 | 0.5621 | 14 poses (0.016) | 18/71 | 23.19 (0 dropped) |

What was checked, and what it found:

1. **Active DOF and determinacy.** J1, J2 and J3 are the only active joints. K is slaved: the crank's angle is fixed by
   the stage-1 pin in the two-walled groove, and K is fixed by the nose in the two-walled slot. Nothing is left to a
   spring. There are no passive translations, gears, pulleys or cables. The knee pins are outside the count (user rule).
   The slot's far end is a real stop between the two bodies of that pair, like the lead's stop B. Poses that need more
   than 46.5 deg of K are counted as lost, not taken.
2. **The fit model's own gates (the frozen protocol never reads them).** `_desmo_fail` is empty. dK_lim is 46.5 at the
   slot end. Slot slop is 0.04 deg; the pocket pressure angles are 25.5 / 32.0 against a 34.47 gate. The plate clears
   hub K by 1.23 mm.
3. **Dense crank-free groove scan** (every 0.25 deg of K, 211 rows; the claim's own gate samples 9 points). Worst
   0.187 deg at K 44, so none over 0.25. Held plus free, nominal: 0.227 deg. At the worst-tolerance groove (c 0.015)
   this becomes 0.281 deg, over 0.25; the claim reported 0.261 from its 9 points.
4. **Pin on the groove (frame check).** With the claim's linear-law IK, the pin carried by the crank sits up to 0.162 mm
   off the built groove's centreline (93 of 184 fast poses beyond the 0.01 clearance, worst at K 0.74, inside the
   blend). The model's IK ignores the blend's lead of up to 2.69 deg of K. **Correction:** the IK now carries the blended
   law (desmo-slipper verifier B1, copied). Nine bench poses are re-solved on the blended table: 19.04 -> 18.98, takes
   and contacts unchanged. This is the verified number.
5. **New check, plate against horn as solids.** The claim's CRK-BOSS gate tests only the crank's low arm. The per-pose
   strap checks never pair the tip plate (ROD) with link 1a's boss and root (HORN). Per taken pose, in link 1a's frame:
   the plate underside sits at R 63.16 and the horn's highest top at R 63.01. The root dips toward hub K (underside
   58.18-60.01). The radial gap where they overlap is 0.150 mm at every pose, bench and held out: the designed running
   gap, never less. **Passes.**
6. **Own-state fold margin th.** Bench min 5.181 (0 of 372 under 5). The lowest is pose 313, forced at dK 45.62, where
   dth/dK = 0.405. The dense nominal K play of 0.227 deg moves th by about 0.09 deg there, so the margin still holds
   on the bench. Held out the min is 5.006 (0 of 861 under 5), at pose 1054, forced at dK 46.27 with dth/dK 0.403. The same play would take it to about 4.92: a WATCH item, as on desmo-slipper (T3), not a refutation (the nominal margin holds everywhere).
7. **Takes, contacts, contact depth (T5).** Taken and contact poses are identical to conecut's (372 / 4 on the bench:
   205, 237, 264, 316). Depths: 237 at -9.47 (conecut -8.93), 264 at -1.17 (conecut -5.80), 205 at -4.28, 316 at -1.23.
   Per-pose dumps: `docs/alignment/remeasure/desmo-conecut-knuckle-3r{,+blend}_{bench,held}_perpose.json`. Each one's
   recomputed gap matches the report to within 0.01.
8. **Continuity flood.** The full-envelope flood drops 0 poses (connected = static). The kNN graph reads 20.67 on the
   bench, against conecut's 19.97.
9. **Bench artefacts.** Every number is on the exact path. The fast fit is 13.31 (linear) and 13.27 (blended).

**The friction claim (mu 0.15), probed on the fast bench**
(`docs/concepts/verify/desmo-conecut-knuckle-3r_v_probe_fast.json`):

* **The score does not depend on the auditor's ruling.** At the family's standard mu 0.087, stage 1 read on the linear
  law gives the same 13.31 (slot end binds). Only the mu 0.15 claim rests on the built-groove reading. On the linear
  read at mu 0.15 the drive fails at K 0 (86.52).
* **At mu 0.15 the claim sits on a 0.07 mm cliff.**
  * a_s 9.60 (+0.07 mm): stage 1's built forward pressure angle binds at K 44.75, fast 14.56.
  * a_s 9.65: binds at 43.0, fast 15.17.
  * psi 150.2 (+0.5 deg): fast 13.94.
  * mu 0.17: 14.56.
  * The same a_s 9.60 and psi 149.3 are flat at mu 0.087 (13.31).
  * So the mu 0.15 margin is a placement tolerance below a machining tolerance. Read "holds mu 0.15" as nominal only.
* Seat tolerance: r_c 15.95 and 16.05 are flat (13.35 / 13.33).

**For the auditor and the lead.**
* The verified number uses the blended IK. The claim's 19.04 (linear IK) reproduces exactly.
* The stage-1 built-groove reading changes only the friction claim, not the score.
* Watch items carried from the family: G4 (m_sub at rest), T5 depths now on file, and K play into th held out.
* Complexity is unchanged at 16.5.
