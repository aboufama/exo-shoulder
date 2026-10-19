# kneeless-steer-midbracket-relay-4r

Round 401 (K1, kneeless track), lens A. Knee-less steered relay on the knuckle chain: phi40-thinstack-relay-4r without the
cuff knee. J3 sits on a GH ray (b3 0), re-seated at (wd, wa) ~ (84, -15). Own-angle dowel stops: q2 <= 100 and J3 in
[-100, 115]. Member 3 is ONE rigid body: the hub 3 lower plate, a bent 3 x 10 Ti bracket down E's fitted line, and a
14 x 14 T-nut carriage on a 1.0 mm slotted arm-fixed Ti shell at station s0. The relay is one-sided, PHI 50-58, on an
axis at tilt 12 / taz 235 through GH. 4 counted joints (J1, J2, J3, relay). K is slaved (slipper nose). No knee, no cuff
slides, 0 passive translations.

## Deeper-version prompt (written before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Treat the stops as the *steering*
   device they are: an own-angle stop decides which branch the redundant 4R takes, so the stop values belong in the same
   selection as s0 / PHI. They must be checked against the fold metric `th` (>= 5 deg in every state) and against the
   flood (no relay jump > 10 deg), not only against the static bench. (b) Bend the bracket along E's fitted polyline
   instead of drawing a new line. E is already skin-fitted and in band 0.947, so the honest move is to *truncate* E at
   the carriage lug and price only what is left. (c) Put the carriage under the bracket's end. The carriage centre should
   sit at E's end azimuth, not at the deleted pad's azimuth + delta. (d) Check the lug coil against the bracket: once the
   bracket is the carriage's own body, the bracket and the coil are rigid neighbours and must not overlap. (e) Widen the
   jam rule to every chain part vs the shell and the carriage. The parent checked only E / boss / hub3 / L2 / knee / pad,
   and a knee-less relayed chain moves hub 2 / L1b / crank / horn relative to the arm-fixed shell.
2. **Rawest material.** The posed skin itself (signed-distance per pose in tools/concept_bench.py), the motion clips
   (Z0 archive: the 110 fit-clip frames + the envsel / held-out workspace draws), the fitted E polyline in the HG frame
   (its per-sample station along the relay axis), the per-sample residual vectors of every pose (the slicing reads them
   directly, not per-part summaries), and the clip-p90 skin-radius profile about the relay axis at the station
   (geometry()).
3. **Methods and tools.** The phi40 relay stack (armarc solve_phi: least phi in [0, PHI] passing the lead's gates; the
   proxtrack / offset / thin-stack rerecord with shell, carriage, flange, lug coil, 60-deg bump ramp), env_bench envsel
   for selection (never the claim bench), the exact signed-distance path for the claim, the continuity flood
   (flood_relay, kinematic, cached per cell in this row's verify dir), BV.th_margin for the fold reading, and
   tools/simplicity.py for complexity.
4. **What, other than me, shows the number is right.** The bench (Bench(110,360) exact, frozen shape), the held-out bench
   (never used for selection), the adversarial verifier re-running this model file, the alignment auditor (T5 contact
   depth, the 2 mm reading, stop-engagement th), and the red-team pose list in this doc (rest, overhead, across-the-body,
   behind-the-back, and the relayed stretched poses where hub 2 used to bury under the acromion).

## Model (docs/concepts/models/kneeless-steer-midbracket-relay-4r.py)

phi40-thinstack-relay-4r is imported read-only. Its relay solve (least phi in [0, PHI] at which the lead's gates pass),
its thin stack (1.0 mm shell, lean carriage, lug coil 12 x 10, flange, band 8, bump 1.2, 60-deg ramp) and its envsel
selection bench are used as they are. This row changes:

* **Chain:** b3 0 (J3 on a GH ray), seat (wd, wa) a parameter.
* **Stops:** own-angle dowel stops as gates in the relay solve: J2 slot q2 <= Q2MAX (AA.gate wrapped) and J3 groove
  [J3MIN, J3MAX] (AA.LEAD before prepare). A pose with no phi in [0, PHI] that passes them is LOST, never taken
  (stop_lost: its residual is set to None).
* **Knee-less member 3:** boss / pad / knee samples and their contact entries are deleted. E is cut at the carriage lug
  (station >= s0 + CAR_L/2 along the relay axis, both E's underside and its top-face contact set). The parent's
  carriage -> pad L-lug bracket is deleted. E's own bump (the parent's ramped lift over the shell band) is the bracket's
  climb onto the carriage.
* **Jam rule widened:** EVERY chain part vs the shell sector and the carriage sector. The parent checked only E / boss /
  hub3 / L2 / knee / pad.
* **Flood:** the flood cache key carries neither the seat nor the stops, so the claim path writes one cache sub-dir per
  cell. phi40's flood files are never read.

Bug found and fixed on the way: the first contact-entry filter matched hub 3's own 4 x 32 crown sets as "boss tops".
The fixed re-read of PHI 58 (84, -15) is identical to the digit (those sets produced no contact-only negatives), so the
two cells read before the fix stand. They are flagged as lower bounds in the sweep.

## Step 0 (pre-registered kill test, bracket-honest proxy; envsel exact, ideal relay)

Three readings come from ONE prepare per cell: 'bracket' (the proposer's: every knee-side sample kept), 'deleted' (E /
boss / pad / knee dropped), and 'honest' (E kept proximal of the carriage lug at station s0; 'ctr' = cut at the
carriage centre, 7 mm more E, slightly optimistic because those samples sit over the carriage). Stops are q2 <= 100 and
J3 [-100, 115], relay axis tilt 12 / taz 235.

| PHI | seat (wd, wa) | bracket | deleted | honest lug (best s0) | honest ctr | reach | ib14 | contacts | overhead /26 |
|---|---|---|---|---|---|---|---|---|---|
| 54 | (84, -15) | 16.11 | 16.92 | 17.54 (-60) | 17.36 (-80) | 0.783 | 0.881 | 16 | 6 |
| 58 | (84, -15) | 15.25 | 16.07 | 16.67 (-60) | 16.50 (-80) | 0.792 | 0.881 | 16 | 7 |
| **58** | **(80, -15)** | 13.81 | 16.20 | **15.60 (-80)** | 15.39 (-80) | 0.803 | 0.882 | 17 | 6 |
| 58 | (78, -15) | 14.41 | 17.94 | 17.12 (-80) | 16.89 (-80) | 0.806 | 0.869 | 19 | 5 |
| 58 | (80, -13) | 14.47 | 18.22 | 17.27 (-80) | 17.01 (-80) | 0.808 | 0.855 | 15 | 6 |
| 58 | (80, -17) | 16.10 | 19.14 | 18.40 (-80) | 18.20 (-80) | 0.789 | 0.875 | 20 | 6 |
| 58 | (84, -18) | 82.37 | 85.92 | 84.21 | 84.00 | 0.453 | 0.861 | 8 | 11 |
| 58 | (86, -18) | 16.92 | 17.00 | 17.01 (-80) | 16.92 (-80) | 0.775 | 0.899 | 18 | 9 |

* The proposer's numbers reproduce exactly: (84, -15) PHI 58 gives bracket 15.25 and deleted 16.07. The judge's
  correction holds. The 'bracket' proxy is optimistic by 1.4-3.5 gap points at every seat (2.7 at (78, -15)),
  because the boss / pad / knee-link samples (in-band ~1.0) pad the in-band share.
* The best honest cell is (80, -15) PHI 58 s0 -80 at **15.60**. It is pinned on all four seat neighbours (78: +1.5,
  84: +1.1, wa -13: +1.7, wa -17: +2.8). The seat landscape is a narrow ridge: (84, -18) falls off a fit cliff
  (fold 212 lost poses, reach 0.45).
* The **pre-registered kill fires**: every cell is > 15.4 bracket-honest. The best is 0.20 over the pass line and 0.68
  under the 16.28 kill line. Only the 7-mm-longer 'ctr' cut (15.39) touches the line, and that cut is not
  buildable: those samples sit over the carriage.
* Where the best cell loses (honest lug, s0 -80): reach 0.803 (289/360 workspace poses, 9.7 gap points: fold 49 + J3
  stop 5 lost, 54 poses with no stop-legal relay angle), contact 0.041 (17 poses, 4.1 points: hub 2 6, L2 6, horn 3,
  E 1, crown 1; 13 of the 17 are RELAYED, mostly overhead at elevation 150-167), in-band 0.882 (1.8 points: hub 3
  0.636, L2 0.726). Contact depth: T5 sum 48.5 mm over 17 poses (lead 20.24, phi40 74.93), max 8.29 mm at pose 361
  (plane -21, elev 90, axial 50). Near-touch: 1 mm 22.78, 2 mm 34.93. Overhead 6/26 taken.
