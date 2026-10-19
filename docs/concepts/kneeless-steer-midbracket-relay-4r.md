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

## Step 0 (pre-registered kill test, bracket-honest proxy)

(filled in below as the cells land)
