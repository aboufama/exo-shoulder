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

