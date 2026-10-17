# A long-stroke K drive for the 3-active knuckle family (2026-10-17)

User, 2026-10-17: "i want higher scores! get to work and do it well!" The fold analysis (docs/research/fold_ceiling.md)
measured that the stretched fold wall of every leader is the K DRIVE'S STROKE: dK ~46 deg -> a1e 54.3 -> th 106.6. Its
exact one-level parking test prices a longer stroke on a re-seated K sub-dyad: 57.5 deg on 32 / 48 = reach 0.767 (~94.7),
**75 deg on 32 / 48 = 0.778 (~95.1)**, 28 / 50 at 75 = 0.775 (held out +0.067). The lead raised this task's target from
57.5-60 to ~75 deg (07:00 UTC).

The task: give K that stroke with every pressure angle <= 42 deg (friction included for sliding pairs), a closure that
holds K on its law, catalogue parts at real size and every part clear of the skin, then measure what it buys. MVP1 rules:
no gears, pulleys or cables; cams, linkages, rolling / sliding contacts only.

Files: model `docs/concepts/models/longstroke-slipper-knuckle-3r.py` (LS_DRIVE = nose | roller | rssr), scripts and data in
`docs/research/longstroke_drive/`, row `docs/concepts/rows/longstroke-slipper-knuckle-3r.json`.

## Depth answers (written before the work, kept as written; the measured answers are in the sections below)

1. **What a top mechanism designer would do here that the brief does not ask for.**
   - Recognise the measured stroke caps (rod RSSR 43, roller flank 46-57.5, nose 49.8) as the THEORY OF GEARING, not as
     a bad synthesis. A one-sided conjugate contact with a near-constant ratio is a single gear tooth. Its arc of action
     at pressure angle 0 -> alpha is bounded: for the involute, the driven member turns tan(alpha_max) - tan(alpha_min)
     rad, 0.90 rad = 52 deg for 0 -> 42 deg, and the contact walks out radially as it goes (round 9 measured exactly
     that: contact r 18 -> 30 mm, onto the deltoid). More stroke from one contact means a bigger, not a better, cam.
   - So change the PAIR, not the profile: a bilateral LINKAGE (a two-force rod or coupler) has no lift-off and its
     transmission angle can be PHASED to straddle 90 deg, so a 75 deg swing costs only about +-37.5 deg of pressure
     angle plus the rod's out-of-plane lean. That is Freudenstein / Burmester territory: the transmission-angle map is the
     design tool, the contact profile is not.
   - Separate the two stages' jobs. Stage 1 (hub-2 rim lobe -> crank) carries the DWELL (K on stop A) and the law's shape;
     stage 2 (crank -> link 1a) carries the GAIN g = dK / dphi. Choose g for conditioning of both stages: the lobe's
     crest must stay inside hub 2's O20 + 1.5 skirt (lift s_arm phi <= 11.5 - r_lobe) and its pressure angle
     tan(pa) = kK s_arm / (g r) <= tan 42, while stage 2 wants the swing straddling its 90 deg transmission.
   - Remove the chord's lean: a straight rod between members that turn about axes through GH leans out of each member's
     plane by ~half the arc it spans (10-30 deg here), which eats the pressure-angle budget. A SPHERICAL coupler (an arc on
     two radial pins, all four axes through GH) transmits force in each pin's tangent plane: no lean, fewer passive
     rotations than two ball links.
   - Check what the brief did not ask: the law itself (does the lobe law reach the new stroke at the poses that need it,
     or does the law become the wall?), the force closure (spring) vs a disturbance, and the tolerance neighbours.
2. **The rawest material.**
   - The K law table the slaved coordinate must follow: per pose, the law's |dK| from the fitted design's own IK on every
     workspace pose of Bench(110,360) and the 952 held-out poses (`stroke_curve.py`, `stroke_curve_*.json`, law_table).
   - The drive's own per-0.25-deg tables: crank angle phi(dK), both pressure angles, the rod's lean (`pa_map.py`).
   - The posed skin through the bench's exact signed distance (the frozen exact wear), per-pose contact depth.
   - The fold analysis' exact parking rows (`docs/research/fold_ceiling/parking_k_*.json`), not its summary.
3. **Methods and tools.**
   - Transmission-angle / pressure-angle maps per K step for each drive (the parents' spherical cam synthesis for the
     contacts; the RSSR closure by continuation for the rod; a spherical-4R closure for the coupler variant).
   - The involute arc-of-action bound for one-sided contacts; Freudenstein-style phasing for the linkage (horn arm
     perpendicular to the rod at mid-stroke, crank phase gam straddling the swing).
   - Latin-hypercube farm sweeps per drive (240 configs each, Bench(60,160) fast), then CMA-ES on the farm
     (`tools/concept_cma.py`, 2 mm near-touch objective) to the exo-screen convergence gate.
   - The fold analysis' exact one-level parking (`parking_k.py`) as the gate for the K dyad / stroke option.
   - The repo's frozen claim protocol: fit on Bench(60,160) fast, freeze the shape, wear on Bench(110,360) exact and on
     the 952 held-out poses.
4. **What, other than me, shows it is right.**
   - The frozen exact Bench(110,360) and the held-out bench (952 poses), worn with the shape frozen.
   - An independent verifier re-running the claim (commands at the end), and `tools/alignment_audit.py` on the row.
   - The fold analysis' parking estimate as an outside prediction (0.775-0.778 at 75 deg) that the real model either
     meets or misses.

__BODY__
