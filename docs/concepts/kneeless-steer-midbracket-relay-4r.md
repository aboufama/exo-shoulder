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
* PHI 62 at the best seat: honest 16.28 (s0 -80). Reach stays 0.8028, the same 289 poses as PHI 58, and contacts go up
  17 -> 20. The relay-reachable set **saturates by PHI 58**. More travel only buys contact, so PHI 50 (dominated:
  PHI 54 < 58) and q2 95 (it only removes poses) were not run.

## Step 1 (the knee-less metal on the phi40 hardware; envsel exact, best cell)

The knee-less member 3, plus the shell (1.0 mm Ti, R_t 80.1-80.4), the 14 x 14 lean carriage, the lug coil, the
flange and the bump 1.2 with the 60-deg ramp. The carriage rests delta deg anterior of the old pad azimuth. E's end lies
+12.45 deg (s0 -80) / +8.8 deg (s0 -55) anterior of it.

| s0 | delta | gate gap (claim reading) | wear | reach | ib14 chain | contacts (chain / hw / both) | shell arc rel pad | what limits it |
|---|---|---|---|---|---|---|---|---|
| -80 | 12.45 (carriage under E's end) | 28.31 | 28.31 | 0.753 | 0.890 | 16 / 26 / 1 | [+4.9, +76.5] | the anterior shell end past the torso: 25 shell contacts at +69..+76.5 |
| **-80** | **3.5** | **22.39** | 20.88 | 0.767 | 0.882 | 16 / 13 / 1 | [-4.0, +67.6] | 9 un-relayed IR / behind-back poses on the anterior end (+67.5, up to 11.9 mm), 3 relayed cross-body poses on the zero end (-2.6..-4, 11.5-12 mm), 2 flange |
| -55 | 3.5 | 22.85 | 22.85 | 0.794 | **0.825** | 16 / 3 / 1 | [-4.0, +67.6] | clean shell, but the band at s0 -55 sits under hub 3 / L2: the 60-deg bump lifts them out of band |

**The metal costs 6.8-7.3 gap points over the proxy** at either station. Both station choices fail, for different
measured reasons:

* **s0 -80:** the shell end-clearance bins over ALL poses (not only taken ones) are clean only to **+48 deg**. Bin +48
  is 3.33 mm at pose 117, +50 is -0.48 and +66 is -11.9: arm at the side with internal rotation, shell end into the
  flank. The taken-pose bins read clean to +68 and are misleading: a shell end must be read over every pose, because a
  contact is not a lost pose. PHI 58 needs +67.6. The spec's "+51 cliff at -80" is confirmed on this kit to within
  3 deg.
* **s0 -55:** the shell is clean (3 hardware contacts). But the station is 47 mm from hub 3 (hub 3 at s -7.5), so the
  parent's bump band (s0 +- 8 + ramp) catches hub 3's skirt and L2. Chain-only in-band drops 0.882 -> 0.825.

No station in between was metal-read (time box). The proxy says s0 is nearly flat (15.60-15.93 over -80..-55). The
metal says the clean-shell side and the in-band side pull in opposite directions, so a middle station trades one
loss for the other.

## Red team (own best config)

* **The pose that jams:** none jammed. The jam list is empty at s0 -80 delta 3.5, with the widened rule (every chain
  part vs the shell / carriage sectors). The losses are contacts and stop-illegal poses, not jams.
* **The point that pinches:** pose 361 (plane -21, elev 90, axial +50, relayed phi 45.8), 7.7-8.3 mm deep on the
  chain (hub 2 class). Pose 377 (plane 29, elev 123, axial -14, phi 30.9) is 7.4 mm deep. Both are RELAYED: the stop
  steers the chain onto the relay, and the relayed frame drives hub 2 / L2 into the acromion-deltoid shoulder. The
  burial is shallower than phi40's (T5 48.5 mm over 17 poses in the proxy vs phi40's 74.93) but deeper than the
  lead's 20.24.
* **The optimistic numbers:** (1) the 'bracket' proxy (+1.4-3.5 points everywhere); (2) the 'ctr' cut (-0.2: E
  samples over the carriage); (3) the taken-pose shell-end bins (clean to +68 vs the all-pose truth of +48); (4) the
  carriage lug extension. At delta 3.5, E's end lands ~5.6 mm anterior of the carriage edge, and the ~6 mm lug joining
  them is not sampled. It sits at the bumped E height over the shell, so the omission is small, but it is metal.
* **Unmeasured:** R17 (CF strip 2 N vs gravity 0.79 N + mu 0.15-0.25 x normal load), flood continuity, th margin and
  Bench(110,360) / held-out. None were run, because the kill fired at step 0 and the held-out split stays untouched.

## Verdict

**Dead (pre-registered step-0 kill: every cell > 15.4 bracket-honest; best 15.60).** With the real metal it is 22.39
(s0 -80) / 22.85 (s0 -55). That is worse than the 3-joint lead (18.28) and the knee-less 3-joint best on file
(kneeless-roller 21.07), at 4 counted joints and complexity 51.75. Deleting the knee saves nothing on the v2.2 ruler,
because the knee is free there.

## New knowledge (beyond this morphology)

1. **The relay's reachable set saturates by PHI ~58 on the knuckle chain with own-angle stops.** PHI 62 adds 0 poses
   and +3 contacts at the best seat. The remaining reach loss (fold 49 + J3 stop 5 of 360) is not a travel problem.
   It sits in poses where no relay angle makes the stopped chain legal.
2. **An arm-fixed shell end must be read over ALL poses, not taken poses.** The taken-pose bins said clean to +68 at
   s0 -80; the all-pose bins say +48. A contact pose is not lost, so it never shows in the taken bins.
3. **The knee-less relay has a station dilemma.** Distal stations (s0 -80) hit the flank with the shell's anterior end
   on IR-at-the-side poses. Proximal stations (s0 -55) put the bump band under hub 3 / L2 and cost 0.06 chain in-band.
   The knee used to buy this freedom by letting the carriage sit 31 mm from the chain. The measured price of
   deleting it on the relay is ~6.8-7.3 gap points of metal, not the ~0.8-1.4 the step-0 proxies suggest.
4. **The proposer's 'bracket' proxy is systematically optimistic by 1.4-3.5 points** (the knee-side samples pad the
   in-band share). Every knee-less proxy on file that keeps knee-side samples should be re-read.

## Next

The open lever is not this station sweep. It is a relay whose shell does not need +67 deg of arm-fixed arc. Two
candidates: a two-segment shell (an anterior segment that is not arm-fixed past +48), or the distal ring (lever 2:
the GH-elbow line at s 0.65-0.8, where the arc spread is 4.0-4.4 mm). The reach saturation (finding 1) says the next
points come from making the stopped chain legal at the 54 stop-illegal poses (J3 groove / q2 slot shape), not from
travel.

## Audit (death refutation, 2026-10-19 ~03:30 UTC)

The auditor re-ran this model file with the same envsel exact path and seat (80, -15), stops q2 <= 100 and J3 [-100, 115],
and relay axis tilt 12 / taz 235. No bench, kit or parent file was changed. Raw readings:
`docs/concepts/verify/kneeless-steer-midbracket-relay-4r/audit_*`.

**Convergence gate.** The 45 proxy (lug) entries form a pre-registered grid, not a CMA. On that grid the gate is met:
gain 0.0 / 0.0 and top-5 within 0.09 points. The CLAIM number (metal), however, came from 3 reads, all at PHI 58. Those
3 reads are not a converged sweep. They also skipped the region the design's own data points to. The parent's PHI 41/42
were rejected for the same anterior shell end at +51.9. The spec says "PHI <= 50 by the +51 torso cliff" at s0 -80. This
row's all-pose bins say the shell is clean only to +48.

**What the audit measured (envsel exact, metal, same code):**

| cell | gate (claim reading) | plain wear | reach | ib14 gate | contacts (chain / hw) | overhead /26 | proxy (honest lug) |
|---|---|---|---|---|---|---|---|
| PHI 58, s0 -80, delta 3.5 (agent) | 22.39 | 20.88 | 0.767 | 0.882 | 16 / 13 (+1) | 6 | 15.60 |
| **PHI 40, s0 -80, delta 3.5 (audit)** | **19.50** | 17.65 | 0.761 | 0.882 | 13 / 2 | 4 | 18.38 |
| PHI 40, s0 -80, bump 0 (spec value) | 19.49 | 17.65 | 0.761 | 0.882 | 13 / 2 | 4 | - |
| PHI 58, s0 -55, bump 0 (spec value) | 22.84 | 22.84 | 0.794 | 0.825 | 16 / 3 (+1) | 6 | 15.93 |

* **The reported claim number was pessimistic by 2.9 points.** At PHI 40 the anterior shell end sits at +49.6, inside the
  clean bin. All 9 anterior-end contacts and the 3 zero-end contacts on the phi 55-57 relayed cross-body poses go away.
  Only the 2 flange contacts remain (poses 259 / 264, phi 0). The knee-less metal reads **19.50**, not 22.39.
* **The death still stands.** The proxy at PHI 40 is already 18.38. The ideal relay carries no hardware, so the metal
  cannot read below it. That is above the 3-joint lead (18.28). At PHI 58 the proxy floor is 15.60, and the
  arm-fixed shell end costs 6.8 points there. A middle PHI (44-50) interpolates between a proxy of ~17 and 3-5 extra
  anterior-end contacts, so by this data it lands at ~18.5-19.5. Even the best proxy cell (15.60) is above phi40's
  verified 14.06. A knee-less 4R that "scores way higher" (K1) is out of reach on this chain.
* **bump 0 (the spec's step-1 value; the agent used the parent's 1.2) changes nothing:** 19.49 vs 19.50 and 22.84 vs
  22.85. Not a cause.
* **Attribution correction at s0 -55.** The doc and row say the 60-deg bump lifts hub 3 / L2 and that "chain-only in-band
  drops 0.882 -> 0.825". That is wrong. The record's `chain_only_gap` at s0 -55 is 17.67, so the chain-only in-band is
  ~0.877. The 0.825 is the PLAIN in-band (shell / carriage samples included), and the gate takes min(plain, chain-only).
  bump 0 leaves it unchanged, which confirms the bump is not the cause. At s0 -55 the circular 1.0 mm shell floats out of
  band over the deltoid's non-circular section. Its own in-band is what costs the 5 points. (The row's `ib14_chain` field
  for s0_55 is really ib14_gate.)
* **No modelling bug found** in the parts read. The J2 stop reads q2 = `M.D.ik(Q)[0][:, 1]`, the same column as every other
  knuckle model. Stop-lost poses are counted lost, never taken. Contact poses count as reach-lost as well as contact, as
  in the bench for every row. The gate reading (min of plain and chain-only in-band) is the convention phi40's verified
  14.06 used.
* Not run (time box): PHI 58 s0 -65 bump 0 (the one middle station; stopped unread), PHI 44-50 metal, Bench(110,360),
  held-out.

**Audit verdict: the death stands. The claim number is corrected to 19.50 envsel (PHI 40, s0 -80).** One-line reason:
the knee-less relay's ideal bound at a clean-shell PHI (18.38 at PHI 40) is already above the 3-joint lead (18.28). A
PHI that beats it puts the arm-fixed shell end past the +48 deg torso cliff (6.8 points of metal at PHI 58), so no
station/PHI cell reaches the lead, let alone phi40's 14.06.
