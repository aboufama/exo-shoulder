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

## 3. The search (farm CMA-ES, `tools/concept_cma.py`, Bench(60,160) fast, 2 mm near-touch objective unless stated)

Free variables: the drive (La, s_arm, r_h, beta, gam, hl, zr, r_lobe; for the nose g, r_c, lift, nose_r), the lobe law
(kK, smhi) and the K dyad (bk1, bk2, a1max); the verified seats, stop A (a1 37.55) and a2 (57.22) are held.
Summaries: `python3 docs/research/longstroke_drive/cma_summary.py docs/research/longstroke_drive/farm/cma_<batch>_*.json`.

**cma1 / cma2 (free; 8 runs, 8,024 evaluations): the search gives the stroke back.** Started from the sweeps' long-stroke
points (dK 48-77), every run walked the drive range DOWN to 35.5-52 deg, and two of the four cma2 runs walked the K dyad
back to the parents' 26 / 38 clamp:

| run | start (2 mm) | best (2 mm) | best plain | reach | in-band | dK_lim | dyad | gate (2nd half / last third / top-5, pts) |
|---|---|---|---|---|---|---|---|---|
| cma1 ns1 (nose) | 54.11 | 19.03 | 17.84 | 0.744 | 0.903 | 35.5 (horn PA) | 26 / 47.4 | 0.45 / 0.00 / 0.11 pass |
| cma1 rs1 (rod) | 40.37 | 19.17 | 16.65 | 0.756 | 0.877 | 37.5 (trans.) | 26 / 47.3 | 0.08 / 0.05 / 0.00 pass |
| cma1 rs2 | 63.85 | 19.88 | 17.78 | 0.756 | 0.872 | 42.5 | 26.7 / 48.8 | 1.05 / 0.89 / 0.07 (not yet) |
| cma1 rs3 | 41.67 | 19.33 | 16.82 | 0.756 | 0.876 | 35.5 | 27.2 / 47.9 | 0.14 / 0.04 / 0.00 pass |
| cma2 r75a | 49.41 | **18.14** | 15.80 | 0.763 | 0.880 | 52.0 (ROD-hub2) | **26 / 38** | 0.67 / 0.23 / 0.15 pass |
| cma2 r75b | 45.06 | 18.53 | 14.90 | 0.775 | 0.876 | 48.2 | **26 / 38** | 1.10 / 0.23 / 0.07 (not yet) |
| cma2 r75c | 40.55 | 19.16 | 16.61 | 0.756 | 0.878 | 45.2 (law) | 26 / 47.3 | 0.37 / 0.15 / 0.04 pass |
| cma2 r75d | 123.36 | 19.36 | **14.53** | **0.788** | 0.867 | 48.8 | 26.5 / 47.6 | 0.00 / 0.00 / 0.11 pass |

Combined gate over each batch: 0.00 / 0.00 / 0.05-0.14, passes. Slipper-nose on the same objective: 16.47 (plain 13.00).

Why the search drops the stroke (measured on the best configs' per-part in-band, `parts_ib14`): the rod drive's bell
crank sits at a median 13.8-15.3 mm over the skin (in band 0.21-0.60) and its ball links at 12.1-15.2 mm (0.42-0.82).
The crank's long arm may joggle down to link 1b's layer only where it clears link 1b's strap over the WHOLE swing, and a
75 deg K stroke swings it 40-55 deg, over link 1b, so it stays stacked. Every extra degree of stroke costs crank in-band;
the extra stretched poses it buys are 7.5 % of the workspace on either bench (12 / 160 on the fit bench, 26 / 360 on the
claim bench, th 106.6-121.4), and under the 2 mm objective a pose that closes with metal near the skin costs more than a
pose lost to the fold.

**cma3 (stroke held >= 65: a config whose drive range is shorter scores +100; 5 runs, 5,149 evaluations).** The search
keeps the range but stops USING it:

| run | objective | best obj | plain | reach | in-band | dK_lim | K the taken poses use | dyad | gate |
|---|---|---|---|---|---|---|---|---|---|
| s65n2a | 2 mm | 26.37 | 18.26 | 0.775 | 0.859 | 65.2 | - | 27.1 / 48.1 | 0.09 / 0.04 / 0.00 pass |
| s65n2b | 2 mm | 20.16 | 17.74 | 0.763 | 0.860 | 68.0 | - | 27.8 / 39.3 | 0.25 / 0.10 / 0.01 pass |
| **s65n2d (the claim)** | 2 mm | **19.37** | **14.54** | 0.781 | 0.873 | 65.0 | **41.7** | 26.0 / 47.2 | 0.03 / 0.01 / 0.00 pass |
| s65n1a (alternative) | 1 mm | 15.76 | 14.59 | 0.788 | 0.867 | 65.5 | 47.1 | 27.7 / 42.6 | 0.27 / 0.16 / 0.03 pass |
| s65n1b | 1 mm | 16.20 | 15.05 | 0.794 | 0.866 | 65.8 | - | 27.3 / 43.7 | 0.38 / 0.35 / 0.04 pass |

**cma4 (ATTRIBUTION, never a claim: the drive's own metal deleted, LS_GHOST=1, stroke held >= 65; 2 runs, 1,034
evaluations).** What the long stroke is worth on the real chain (hubs, links, pin knee, cuff, the greedy level fit) if the
drive parked perfectly: best 2 mm 15.60, plain 12.23, reach 0.794, in-band 0.884, dyad 30.0 / 42.9, gate passes. On the
same objective slipper-nose is 16.47 / 13.00. So a perfect drive buys ~0.8 fast points; the real rod drive costs ~3.8.

## 4. Claim columns (frozen protocol: fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact / 952 held out)

The pick was committed before any frozen number (`picks.json`, 07:50 UTC): s65n2d, the 2 mm objective's best at stroke
>= 65; s65n1a reported alongside. Farm jobs in `docs/research/longstroke_drive/farm/claim{A..F}/`.

| config | drive range / K used | frozen exact Bench(110,360) | reach (overhead) | in-band | contact (poses, summed / max depth) | near 1 / 2 mm | min th margin | held out (952) |
|---|---|---|---|---|---|---|---|---|
| slipper-nose verified (reference) | 49.8 / 46 | **18.49** | 0.725 (8/28) | 0.8955 | 0.0054 (2) | 20.12 / 33.02 | 5.006 | **23.45** |
| control: slipper-nose's config through THIS model, every PA <= 42 | 49.8 / 46 | 18.49 (fold 88, slide 9, contact 2: identical) | 0.725 | 0.8955 | 0.0054 | 20.12 / 33.02 | - | - |
| **claim s65n2d (RSSR, 26.0 / 47.2)** | 65.0 / **41.6** | **21.27** (score 92.27) | 0.722 (7/28) | 0.873 | 0.008 (3, 18.5 / 12.8 mm) | 25.20 / 41.58 | 5.036 | **26.19** (0.682; contact 13, 54.3 / 12.4 mm) |
| s65n2d, r_h +0.25 (the knife-edge-robust build) | 64.5 / 41.6 | 21.27 | 0.722 | 0.873 | 0.008 (3, 18.7 / 12.9 mm) | 25.20 / - | - | 26.20 |
| alt s65n1a (RSSR, 27.7 / 42.6) | 65.5 / 47.1 | 22.07 | 0.725 (8/28) | 0.868 | 0.013 (5, 18.6 / 12.9 mm) | 23.70 / 42.34 | 5.389 | 24.86 |
| free cma2 r75d (RSSR, 26.5 / 47.6) | 48.8 / - | 22.65 | 0.722 | 0.867 | 0.016 (6) | 26.22 / 39.04 | - | 26.18 |
| free cma2 r75a (RSSR, 26 / 38) | 52.0 / - | 20.86 | 0.719 | 0.880 | 0.008 (3) | 21.94 / 35.39 | - | - |
| free cma1 rs1 (RSSR, 26 / 47.3) | 37.5 / - | 21.79 | 0.714 | 0.876 | 0.008 (3) | 25.72 / 42.65 | - | - |
| **ghost g65d (ATTRIBUTION: drive metal deleted, 30.0 / 42.9)** | 66.8 / 42.1 | 19.50 | 0.731 (8/28) | 0.885 | 0.011 (4, 11.7 / 7.1 mm) | 21.68 / 33.06 | 5.334 | **22.69** (0.698) |

Continuity flood on the claim: static 21.27 = connected full 21.27 (0 dropped), knn 24.08, bench grid 43.43 (slipper:
18.49 / 20.16 / 50.11).

**Reading.**

- **No long-stroke configuration beats the reference.** The best real one is 2.78 points worse on the frozen bench
  and 2.74 worse held out, at +8.25 complexity. Reach does not move (0.722 vs 0.725): the poses the stroke was for are
  not taken.
- **The stroke is idle.** Every searched optimum, free or held at >= 65, takes no workspace pose that needs more than
  42-49 deg of K (th <= 107-110). The parking estimate's window to th 121 never opens on the real chain.
- **Why (measured, `stroke_curve*.json`):** the next wall is the LAW. The hub-2 lobe caps its slope at
  kK <= tan(42) g r_lobe / s_arm (~2.0 at the searched seats); with kK <= 2 the stretched poses past th ~109 fail closure
  at the 5 deg dyad margin (on the 77-deg config: 10 poses at th 110-121 with law dK 53-68, all 'closure' or knee), and
  a steeper law (kK 2.7+) dies at the lobe's base circle. kK 2.3 would close 272 instead of 267, and is reachable only
  with r_lobe ~8.5, s_arm 4 and g ~1.8, where the crank swings more and sits higher.
- **The drive metal is the second cost.** At the CMA's own law slope (kK ~2) even the ghost lever (perfect parking) is
  +1.01 worse on the frozen bench (better held out: -0.76); with the law steepened it beats the reference (section 8). The real rod drive adds ~1.8 bench points: its bell crank (median 14.0 mm, in band 0.50)
  and ball links (0.67) sit over the band, and its horn / rod make the 3 bench contacts (max depth 12.8 mm).

## 5. Red team (the claim s65n2d)

| attack | result |
|---|---|
| **The pose that jams** | None inside the range: the RSSR range scan stops at transmission 48 (PA 42) before any dead centre. Over the K the taken poses use (0-41.6) the pressure angles peak at 28.5 (crank tip) / 25.2 (horn); at the range end (dK 65) 41.97 / 40.84. A two-force rod with ball ends has no friction lean. |
| **Lift-off under ~2.5 N at the cuff** | Stage 2 (the rod) is bilateral: it cannot lift off. Stage 1 (lobe follower) is held by K's clock spring as on the lead (0.08 N.m + 0.015 N.m/rad): static factor 0.08 / 0.033 (the exo's own weight about K) = 2.4. A force at the cuff cannot drive the chain's self-motion (K vs q2 at a fixed arm pose), so it never loads the closure statically. The spring's reflected J2 torque, kK x tau_K = 1.957 x 0.091 = 0.18 N.m, is felt as 1.2-1.5 N at a 120-150 mm cuff lever (1.3-1.6 N at the full 65 deg): under 2.5 N. |
| **The knife edge** (+-1 deg on beta / gam, +-0.25 mm on La, r_h, s_arm, hl, zr, r_lobe; 17 one-at-a-time + 16 corners, `res_tol_s65n2d.json`) | The STROKE is robust: every neighbour still synthesises 61.5-66.8 deg (>= the 41.7 used). The PARKING is not: **9 of 33 neighbours (r_h -0.25 and 8 corners) lose every pose to the ROD-hubK 1 mm part pair** - the claim parks the horn ball 0.25 mm from it - and 1 corner (r_lobe -0.25 with s_arm +0.25) kills the law at the lobe base circle. The robust build r_h +0.25 measures **identical** (21.27 / 26.20). |
| **Does the gain survive held out?** | There is no gain to survive: held out 26.19 vs slipper's 23.45. The ghost attribution is the only held-out improvement (22.69, -0.76), and it has no drive. |
| **The optimistic number** | The fold analysis' 0.775-0.778 at 75 deg: on the real chain the window it counts does not open (law + 5 deg closure + knee), so the parking estimate is an upper bound for this family, not a target. The cma3 constraint "stroke >= 65" was satisfied vacuously (range 65, use 42): a stroke constraint is not a reach constraint. |
| **Point that pinches** | 3 bench / 13 held contact poses: horn lug + hub K + rod / ball link (depth max 12.8 mm); near-touch at 2 mm 41.58 vs slipper's 33.02. |

`python3 tools/alignment_audit.py audit longstroke-slipper-knuckle-3r --ref slipper-nose-knuckle-3r`: **WATCH** (no
gamed finding): not verified yet; sample-weighted in-band 0.873 vs part-weighted 0.878; crank mostly out of band (0.50,
median 14.0 mm).

## 6. Verdict and what it means for the planner (revised after section 8)

- **Delivered:** a K drive that turns K 65-77 deg with every pressure angle <= 42 (the phased RSSR; its stroke is robust
  to +-1 deg / +-0.25 mm), and a spherical-4R reading of it with no chord lean (78.5 deg kinematically, complexity 28.0).
- **Not delivered:** a score gain with real metal. Best long-stroke claim with the real rod drive: 21.27 frozen / 26.19
  held (s65n2d) against slipper-nose's 18.49 / 23.45. The hard goal (reach >= 0.78, overhead >= 12/28, in-band >= 0.88,
  held out < 23.45) is not met by any measured config with drive metal.
- **The lever is real but the drive's metal is the blocker:** with the lobe law at its PA-42 limit (kK 3.0) and the
  drive's metal deleted, the long-dyad chain measures **18.25 frozen / 21.11 held** (fold 88 -> 77; held 2.34 better than
  the reference). Through the rod drive's real metal the same law is 25.83, and the steep-law CMA (cma5) cannot park the
  rod (in-band 0.85; section 8).
- **New knowledge.**
  1. One-sided contacts (nose, roller, groove) cap at 41-52 deg at PA 42: the involute arc of action. Long stroke needs a
     linkage (or a much bigger cam on the skin).
  2. A straight rod between members turning about axes through GH leans 10-30 deg out of their planes; a spherical
     coupler removes that lean.
  3. **After the stroke, the K LAW is the stretched wall.** Along a lobe law, th rises ~1.9 deg per q2 degree while a1e
     rises 1.5 -> 0.9 (the K sub-dyad's efficiency falls as K opens), so the 5 deg margin is lost at th ~109 (kK 2) /
     ~114 (kK 3.0, the lobe's PA-42 limit). The chain can use ~52-54 deg of K, not 75. The fold analysis' parking test
     assumes the ideal law (a1e = th - a2 + 5); a q2-driven lobe cannot follow it.
  4. Searching on the drive's stroke is not searching on reach: a stroke constraint was met vacuously (range 65, use 42).
- **Next (cheapest first):**
  (a) a drive whose metal PARKS under the steep law: the bell crank's arm kept at link 1b's level (the 40-55 deg crank
  swing keeps it stacked today, in band 0.5-0.6) - e.g. the spherical coupler at strap level, or the crank pivot moved
  off link 1b's strap; gate it with the ghost first (`LS_GHOST=1`: 18.25 / 21.11 is the ceiling to chase);
  (b) a law that steepens as K opens (the lobe's PA falls 40 -> 32 along the stroke, so there is room late; a two-slope
  law died at its slope jump, so the profile must be smooth);
  (c) the nose drive on the steep-law dyad (complexity 22.25) did not synthesise from the 28 / 50 seeds; it needs its own
  sweep, and its ~46-50 deg cap is close to the ~52 the chain uses.

## 7. What a verifier must re-run

```bash
# the claim (farm or local; LS_DRIVE=rssr, CB_EXACT=1 for the worn benches)
P="$(python3 -c "import json;print(json.dumps(json.load(open('docs/research/longstroke_drive/picks.json'))['claim_s65n2d']))")"
LS_DRIVE=rssr CB_EXACT=1 python3 docs/concepts/models/longstroke-slipper-knuckle-3r.py frozen "$P" out_bench.json   # 21.27
LS_DRIVE=rssr CB_EXACT=1 python3 docs/concepts/models/longstroke-slipper-knuckle-3r.py held "$P" out_held.json      # 26.19
LS_DRIVE=rssr python3 docs/concepts/models/longstroke-slipper-knuckle-3r.py flood "$P" out_flood.json               # 21.27 / 24.08 / 43.43
# the control (must reproduce slipper-nose's verified 18.49 through this model)
LS_DRIVE=nose CB_EXACT=1 python3 docs/concepts/models/longstroke-slipper-knuckle-3r.py frozen '{"bk1": 26.0, "bk2": 38.0336, "a1max": 58.7678}'
# the attribution (drive metal deleted) and the stroke / law tables
LS_GHOST=1 LS_DRIVE=rssr CB_EXACT=1 python3 docs/concepts/models/longstroke-slipper-knuckle-3r.py frozen "<cma4 g65d params from the row>"
LS_DRIVE=rssr python3 docs/research/longstroke_drive/stroke_curve.py "$P"; LS_DRIVE=rssr python3 docs/research/longstroke_drive/pa_map.py "$P"
# per-pose dump for the contact-depth check (lead's rule): tools/alignment_paired.py dump longstroke-slipper-knuckle-3r bench|held
```

Cost: exo-cpu1 only, never GPU: 6 sweeps, 4 CMA batches (15 runs), 6 claim batches. `tools/runpod_guard.py audit`
before (06:56 UTC, balance $30.55), after the main search (08:08, $29.45) and after the follow-up (08:49, $29.22;
workersMin 0, queue empty): $1.33 for every agent on the account in that window, so at most $1.33 for this task.

## 8. Follow-up (08:10-08:45 UTC): steepen the law, then re-wear the ghost and the real drive

Section 4 left one question open: is the law the wall, or the parking? The law table (`law_table.py`,
`law_table_ghost_k30.json`, the rawest material for this question) answers it. Along the lobe's law, per degree of q2
past the onset, th rises ~1.6-1.96 deg while a1e rises only 1.47 -> 0.90 deg (the K sub-dyad's efficiency
da1e / dK = sin bk1 sin bk2 sin psi / sin a1e falls as K opens). So the dyad margin m3e = a1e + a2 - th falls along the law
and crosses the 5 deg rule at th ~114 even at kK 3.0. The parking test's IDEAL law (a1e = th - a2 + 5) needs
da1e / dth = 1 the whole way: a law that gets steeper as K opens. The lobe allows some of that: its pressure angle FALLS
along the stroke (40.4 at the base circle -> 32.5 at the crest, kK 3.0), because its radius grows.

Law-only kinematics on the ghost config (g65d's dyad 30.0 / 42.9; `stroke_curve_ghost_*.json`):

| law | lobe | bench closable / 360 | held / 952 | th taken max |
|---|---|---|---|---|
| kK 1.98 (the CMA's) | s_arm 5.69, r_lobe 7.61 | 267 | 671 | 108.6 |
| kK 2.3 | s_arm 4.0, r_lobe 8.5 | 268 | 679 | 110.3 |
| **kK 3.0** (the lobe's PA-42 limit at its base circle) | s_arm 4.0, r_lobe 8.5 | **273** | **689** | 112.9 |
| kK 3.4 | same | law dies (lobe PA > 42 at t = 0) | - | - |
| two slopes kA 2.8 / kB 4.0 at 12 deg, kA 3.0 / kB 4.4 at 15 deg | same | 249 / 264 (the law ends at the slope jump: lobe PA) | 623 / 663 | 100-107 |
| 'track' (least opening holding m3e >= 5.5 / 9, gain clipped to the PA cap) | same | 221 / 258 | 555 / 645 | 93-103 |

Frozen exact (farm `claimG`), the same kK 3.0 config:

| | K used (bench / held) | frozen exact Bench(110,360) | reach | in-band | contact (poses, max depth) | held out |
|---|---|---|---|---|---|---|
| slipper-nose (reference) | 46 | 18.49 | 0.725 | 0.8955 | 0.0054 (2) | 23.45 |
| **ghost kK 3.0 (drive metal deleted, ATTRIBUTION)** | 51.8 / 54.0 | **18.25** | 0.739 (fold 77) | 0.897 | 0.018 (7, 7.1 mm) | **21.11** |
| real rod drive, kK 3.0, not re-searched | 51.8 | 25.83 | 0.719 | 0.859 | 0.037 (14, 14.7 mm) | - |

**Reading.** With the lobe at its pressure-angle limit the long-dyad chain DOES use more K (52-54 deg) and, with the
drive's metal deleted, beats the reference: -0.24 on the frozen bench and **-2.34 held out** (fold 88 -> 77 on the bench,
261 -> 228 held). So the lever is real once the law is steep; the part that does not exist yet is a drive whose METAL
parks: the same law through the rod drive's real metal is 25.83 (crank in band 0.62, ball links 0.59, 14 contacts).
And the stroke this chain can use is ~55 deg, not 75: the law, not the drive, sets it.

**cma5: the real rod drive re-searched with the law held steep** (LS_KK_MIN 2.7, stroke >= 55; 2 runs, 970 evaluations,
each run's gate passes: k27a 0.00 / 0.00 / 0.02, k27b 0.41 / 0.08 / 0.01): best 2 mm 20.44 (k27a), best 1 mm 15.51 =
plain (k27b; reach 0.794, in-band 0.851). The metal does not park under the steep law either: bell crank in band
0.51-0.62, rod 0.48-0.65, ball links 0.54-0.63. k27b worn frozen (farm `claimH`): **23.31** (reach 0.728, in-band 0.852,
contact 0.013 = 5 poses, max depth 13.0 mm; K used 44.4) and held out **27.67**. So: the lever is the ghost's
18.25 / 21.11; the rod drive turns it into 23-26.
