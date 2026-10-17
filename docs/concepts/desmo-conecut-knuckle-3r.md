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

**Search.** 160+ configurations on Bench(60,160) fast, run locally because the farm window is closed:
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

