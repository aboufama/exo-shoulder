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

## 1. What a long stroke needs: the gate before any drive (measured)

**The option gate (the fold analysis' exact one-level parking, `docs/research/fold_ceiling/parking_k_*.json`):** at the
verified seats (stop A a1 37.55, a2 57.22), every modelled part at its clip max + 4 mm, the stroke cap fed through the K
sub-dyad law:

| K dyad, stroke | R_est +4 bench | held | parts in-band +4 | est. score |
|---|---|---|---|---|
| 26 / 38, 46.25 (today) | 0.722 (verified 0.725) | 0.695 (verified 0.682) | 0.768 | 93.2 |
| 28 / 50, 57.5 | 0.761 | 0.732 | 0.760 | ~94.6 |
| 28 / 50, 75 | 0.772 | 0.762 | 0.760 | ~95.0 |
| 32 / 48, 75 | 0.775 | - | 0.762 | ~95.1 |

So the lever is worth +0.05 reach (+18 poses) IF a drive turns K ~75 deg AND its own metal parks. The drive's metal is
not in that estimate; it is priced below with the real model (the full fast bench: every drive part sampled, skin, in
band, part pairs).

**Stage 1 becomes a wall at long stroke (measured, `stroke_curve.py`, law-only kinematics on Bench(110,360)).** The
hub-2 lobe gates the law itself: its crest r_lobe + s_arm phi must stay inside hub 2's O20 + 1.5 (11.5 mm) and its
pressure angle tan(pa) = kK s_arm / (g r) must stay <= tan 42 (the parents allowed 45; this row holds 42 everywhere).

- On the 28 / 50 dyad with a 77 deg drive, the linear law kK 1.96 closes 267 / 360 workspace poses (held 657 / 952) and
  takes nothing past th 115.5: the law, not the drive, ends it (10 poses at th 110-121 with law dK 53-68 fail closure
  at the 5 deg margin or the knee).
- kK 2.3 closes **272 / 360** (held 677); kK >= 2.7 kills the law at its base radius (lobe pressure > 42). The parking
  window at 28 / 50 / 75 holds 298: the remaining 26 are the knee, closure at the margin and the law's slope.
- A two-slope lobe (kA 1.8 to t 15, then kB 2.8): 269. The 'track' law (least opening holding m3e >= smt) is much worse
  (194-229): it opens too late for the poses between.

## 2. Candidate drives, least complexity first (priced on the 28 / 50 K dyad, a1max 73, the verified seats)

Every number is the real model's (`docs/concepts/models/longstroke-slipper-knuckle-3r.py`, Bench(60,160) fast, farm):
240-config Latin-hypercube sweeps per drive (`make_configs.py`, `res_coarse_*.json`), plus a focused 240-config sweep
of the phased rod (`make_configs75.py`, `res_rssr75.json`). "Stroke" = the drive's own range dK_lim: the first K step
(0.25 deg) where any pressure angle passes 42 (friction included), the pair lifts off, the flank cusps or the drive
metal comes within 1 mm of hub K / hub 2 / link 1b. Complexity by `tools/simplicity.py --score` (v2.2).

| # | drive (stage 2) | complexity | stroke at PA <= 42, max over the sweep | what ends it | drive metal | best fast plain |
|---|---|---|---|---|---|---|
| C1 | **slipper nose** (slipper-nose's hardened dowel sliding on the conjugate flank, mu 0.087: kinematic PA <= 37.03) | **22.25** | **46.5** | horn PA 93, crank PA 132, CRK-hubK 15 (of 240) | contact r 16.7-21.6 mm, lug to 24.7 mm | 39.43 (reach 0.706, contact 0.047) |
| C2 | **roller** (MR63ZZ on the flank, rolling: PA <= 42) | 24.25 | **51.8** | horn PA 97, crank PA 118, CRK-hubK 22 | the longest strokes run the contact out to r 18.5-31.4 mm, lug 34.3: on the skin (contact 0.49) | 53.44 |
| C3 | **RSSR rod** (O3 Ti rod + 2 M2 ball links from the crank tip to a horn lug of link 1a; transmission >= 48 = PA <= 42 at both ball ends; a two-force rod has no friction lean) | 30.5 (my count; 25.5 by the sidecar's earlier hand count of the same drive) | **77.2** (focused, phased); 59.8 in the blind LHS | transmission (198 of 240), law 38, ROD-hub2 4 | crank / rod / ball links over the band in the sweep (in-band 0.2-0.65; the verified sidecar RSSR sat 0.89-0.96, so it is a parking variable) | 28.24 (dK 60.5) / 29.91 (dK 70.0) |
| C4 | **spherical 4R coupler** (an arc on two radial pins, MR63ZZ pairs: all four axes through GH) | 28.0 | **78.5** kinematic on C3's 77-deg seats (`pa_map.py` sph4r) | horn PA | not modelled with metal | - |
| C5 | groove (two-walled slot, groove-desmo-knuckle-3r) | 18.25 | 41.2 (measured by that row) | horn PA once off the pole | - | - |

**Reading.**

- **One-sided contacts (C1, C2, C5) cannot give 75.** The measured caps (46.5 / 51.8 / 41.2) sit where the involute arc
  of action puts a single tooth (0.90 rad = 52 deg for PA 0 -> 42), and the only way past it (round 9's 64 at PA 43.1)
  is a bigger base circle, i.e. a contact walking out to r 30 mm: the deltoid.
- **A phased linkage does.** The rod's pressure-angle map (`pa_map_rssr77.json`): at rest the crank-tip PA is 33.6 and
  the horn's 34.8; both fall to a minimum near mid-stroke (horn 9.9 at dK 36, crank tip 27.0 at dK 33) and rise to 39.2
  / 39.7 at dK 75 and 42.0 at 77.2. The crank tip never goes under ~27: that is the rod's LEAN (its elevation over the
  crank's plane, 32 -> 17 deg as the rod swings), the chord's penalty.
- **C4 removes the lean.** The same seats with the rod made a spherical coupler: crank-tip PA 20.9 -> 0.15 (dK 34) ->
  14 (dK 54), horn 33.6 -> 0.6 (dK 36) -> 18 (dK 54); the PA-42 range is 78.5 and the swing is symmetric about the
  transmission's 90 deg, so a re-phased coupler has ~+-42 deg of budget for the whole stroke. It also needs 2 radial
  pins instead of 2 ball links (complexity 28.0 vs 30.5). It is the right CAD embodiment of C3 and the next row; it is
  priced here kinematically only (no metal), so it is a recommendation, not a claim.

__REST__

