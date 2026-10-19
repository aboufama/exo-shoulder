# sidecar-roller-flank-knuckle-3r

Rodless sidecar drive for the slaved knuckle. A bell crank sits on link 1b beside hub 2. Its short arm rides the hub-2
rim lobe. Its bent long arm carries an MR63ZZ roller, and the roller pushes a conjugate flank milled in a lateral horn
lug of link 1a at hub K. The chain is the verified lead's (J1, link 1a, K slaved and never read, link 1b, J2, link 2,
J3, pin knee, cuff). Round 8, strap-level drive lens.

Model: `docs/concepts/models/sidecar-roller-flank-knuckle-3r.py`. Sweep: `docs/concepts/sweeps/sidecar-roller-flank-knuckle-3r.json`.
Row: `docs/concepts/rows/sidecar-roller-flank-knuckle-3r.json`. Preview: `docs/concepts/viz/concepts/sidecar-roller-flank-knuckle-3r.js`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Treat the roller-flank pair as a spherical cam. The crank axis dR and K's axis uK both pass through GH, so the
     relative motion of the crank and link 1a is a rotation about GH. The roller's axis should be radial (through GH),
     and the flank is a ruled surface along radial lines. The planar picture (roller axis parallel to uK) is wrong by
     the cone angle; at r ~ 60 mm the cone half-angle over a 6 mm roller is ~3 deg, so a cylindrical MR63 is fine.
   - Choose the law, then cut the flank. A cam pair makes phi(dK) a free design function, unlike the rod's RSSR. Pick
     phi = |dK| / g, so the lobe gate is unchanged in form (lift = s_arm |dK| / g). Then synthesise the flank as the
     envelope of the roller circle in link 1a's frame, and gate it per K step: both pressure angles, the envelope's
     radius of curvature (no cusp or undercut), and the contact staying on the lug.
   - Check force closure at both contacts from the same numbers. The spring torque on K loads the flank. The crank
     then loads the lobe. Both stay closed iff the contact normal has a positive dot product with both contact-point
     velocities, which is pressure angle < 90 on both sides. The 45-deg gate is stricter, so it covers lift-off.
   - Sweep the bent arm, not its rest pose. The arc that clears hub K at rest moves up to La * phi (~10 mm) as the
     crank turns. Gate the arm's clearance to hub K's cylinder at every K step and end the drive range where it fails.
     That puts stop B there.
2. **Rawest material.** The bench's posed skin itself: the signed-distance grids of every bench pose, via
   `tools/concept_bench.py`. Also the per-pose K state, th, m3e and msub from the model's own IK, and the per-part
   minimum metal-to-skin distance over the taken poses. These are not the round's summaries. Held-out clips stay held out.
3. **Methods and tools.**
   - Spherical cam synthesis on a 0.25-deg K grid: roller-centre path in link 1a's frame, envelope offset, curvature,
     pressure angles from the two contact-point velocities.
   - The shared sidecar core (`sidecar-longdyad-knuckle-3r.py`): stacking rule, per-pose crank transforms, drive-range
     truncation, part pairs. Only the drive metal and the law-to-crank map are replaced.
   - CMA-ES on the near-touch gap, Bench(60,160) fast, on the farm (`tools/concept_cma.py`).
   - Then the frozen shape worn on Bench(110,360) exact.
4. **What other than me shows the number is right.**
   - The bench, Bench(60,160) fast for the search and Bench(110,360) exact for the frozen claim.
   - The round's adversarial verifier, re-running the frozen claim in its own harness.
   - Same-harness controls: the rod sidecar (sidecar-longdyad-knuckle-3r, 18.91 frozen self-measured) and the lead's
     verified 22.82.
   - A red-team pose list: the overhead poses, the poses where metal is under 1 mm, and the K step with the worst
     pressure angle.

## Model (what changed from the spec, and why)

Built as a drive variant on the shared sidecar core (`sidecar-longdyad-knuckle-3r.py`, itself on the verified lead's
`frontload-lobe-stopb-knuckle-3r.py`). The chain, the lobe law (per-t gated: rate, lobe pressure, lift-off, stop B, crest
<= 11.5), the stacking rule, the truncation of every pose past the drive's own range and every part pair are the core's.
This file replaces the rod and the RSSR with the cam pair:

- **Law.** phi = sig (|dK| / g)(1 + c |dK|). With c = 0 this is the spec's linear law. The lobe gate takes
  r_horn := s_arm and i_rock := g / max(1, 1 + 2 c K_DES), so the lift, lift rate and crest are evaluated at the
  steepest gain (conservative for c > 0). The crank sense sig is chosen so v_C . v_H > 0 at rest. The other sense puts
  the two velocities more than 90 deg apart, and then both pressure angles cannot be <= 45.
- **Spherical cam, not planar (spec corrected).** dR and uK both pass through GH and are 35-40 deg apart. A roller on
  the crank changes its height along uK by up to ~10 mm over the swing. A flat lug normal to uK (the proposer's
  picture) would lose the roller. The roller axis is radial, and the lug is a spherical shell at the roller's radius
  from GH: a 5-axis part from solid, as the CAD ruling allows (the flank is a ruled cone surface; wire-EDM with a
  tilting head, or 5-axis milling). The arm's arc portion rides on a shell 0.15 mm over the lug.
- **Flank synthesis per 0.25 deg of K.** Roller centre C(k); contact normal n in the tangent plane at C, perpendicular to
  v_C - v_H; contact point Q = C + 3 n. The gates are the pressure angles angle(n, v_C) and angle(n, v_H(Q)) <= 45,
  n . v > 0 on both sides (force closure, no lift-off), and no cusp: where the roller-centre path curves toward the
  horn, its radius must be >= 3 + 3.5. Contact radius >= 13. The arm and roller keep >= 1 mm (+1.5, the core's
  metric) off hub K's cylinder, and the arm keeps 1 mm off hub 2. The low part of the arm keeps 1 mm off the swinging
  lug. The first failing step ends the drive range; stop B goes there, and the core truncates every pose past it.
- **Lug built from the flank.** A 6 mm band behind the used flank, plus a radial root to hub K's rim (rising from the
  member level to the shell), minus the roller's swept path + 0.3 mm. Its metal is sampled like every other part.
- **Bent arm.** Straight from the boss (stacked on link 1b, the core's rule) to the tangent point on the circle r_c
  about uK, then the arc to the roller. Levels: link 1b's top + 0.15 where it overlaps link 1b's strap over the swing,
  else link 1b's level + zr; 60-deg ramps. The arc portion sits over the lug shell.
- **lift (new parameter, spec gap).** It raises the lug / roller / arm-tip layer above hub K's member level, 0-8 mm.
  It is needed because the flank is longer than the spec assumed (next section).

## Kill gate (lead note: both pressure angles <= 45 over >= 30 deg of K, and fast near-touch <= 14.0)

1. **Flank feasibility: passes, but not where the proposer put the lug.** At the proposer's seed (r_c 15-15.5,
   beta -85, g 1.8, the lead's seats) the velocity angle at rest is 62.5 deg. The horn pressure angle starts at 41.4
   and crosses 45 after **8.2 deg of K**. The reason is that v_C points 30 deg off the lug's radius, so the contact
   slides OUTWARD along the lug as K opens. That raises rho_h, so the speed ratio a = |v_C| / |v_H| falls below the
   window [1 / (cos t + sin t), cos t + sin t] (t = the velocity angle). Over 396 geometries (g 1.0-2.8, beta
   -170..160, r_c 15.5-21), the flank works over >= 30 deg of K only for beta -110..-170 at g 1.4-2.8. Those are lugs
   pointing away from hub 2, with the arm wrapping 40-116 deg around hub K. The flank then reaches 34-67 deg (horn
   pressure angle ends it in 122 of 196 farm configurations, crank pressure angle in 68, cusp in 5).
2. **The flank is long.** The contact slides 6-20 mm along the lug over the stroke (contact radius 16 -> 22-40). At hub
   K's member level, the lug's outer end goes 6-13 mm INTO the skin even at rest (beta -110: horn under the skin on 85
   of 185 taken poses). At the proposer's straight-arm, rod-law geometry this never showed. The `lift` parameter
   (6-7 mm) clears most of it, at the cost of in-band.
3. **Fast near-touch: the best is 21.90 (coarse farm sweep, 196 LHS configurations), not <= 14.0.** CMA follows.

## Search (Bench(60,160) fast, near-touch objective, farm)

- Local checks: 9 configurations of the current model (after the spherical-lug fix). The first lug version was flat and
  was replaced, and its numbers are not in the sweep.
- Farm coarse LHS, 196 configurations: best 21.90.
- Farm CMA-ES, popsize 8, 2 processes per stream: A1 / A2 / C from the coarse best, B from the second, and P1 / P2
  with the progressive-law coefficient c free.

| stream | tries | best fast near-touch | gate (2nd half / last third / top-5 spread, score pts) |
|---|---|---|---|
| A1 | 929 | 12.89 | 0.89 / 0.18 / 0.13 (converged) |
| A2 | 1409 | 12.70 | 0.35 / 0.20 / 0.03 (converged) |
| B | 1433 | 12.86 | 0.60 / 0.24 / 0.00 (converged) |
| C | 905 | 15.06 | 0.06 / 0.06 / 0.16 (converged) |
| P1 | 1233 | **11.73** | 2.31 / 1.59 / 0.12 (not converged: continued as P1c / P1d) |
| P2 | 793 | 14.38 | 1.08 / 0.68 / 0.13 |
| P1c (from P1, sigma 0.5 on half scales) | 881 | 11.73 | 0.00 / 0.00 / 0.24 |
| P1d (same, seed 23) | 929 | 11.25 | 0.06 / 0.05 / 0.03 |
| **P1 lineage (P1 + P1c + P1d)** | 3043 | **11.25** | **0.17 / 0.17 / 0.03 (converged)** |

The progressive law does not pay. Every stream drove c to about 0 (P1 0.021, P2 -0.046). Near the pitch point, any
crank acceleration bends the relative path into a cusp (c = 0.4 at the coarse best: cusp at K = 0).

The winning basin (P1) moved the lug to point straight away from hub 2 (beta -175). The arm wraps 130 deg around hub K
(51.5 mm developed). At rest the two contact velocities are only 3.2 deg apart, so the pair works near its pitch point:
pressure angles 6.3 / 8.0 deg, and the horn's angle rises to 41.5 over the taken stroke. The flank now covers the
law's whole range (dK_lim 56.2, ended by the law, not the flank). The CMA also dropped the lift to 1.4 mm and freed the
K dyad (bk1 27.7, bk2 35.7, a1max 56.6).

## Claim (self-measured, NOT verified): CMA P1 best, frozen shape worn on Bench(110,360) exact

| | this design (P1) | rod sidecar (sidecar-longdyad, self-measured) | verified lead (frontload) |
|---|---|---|---|
| fast Bench(60,160) near-touch | 11.73 (plain 11.73) | 10.30 | - |
| **frozen exact gap (plain)** | **20.08 (score 92.70)** | 18.91 | 22.82 |
| near-touch 1 mm / 2 mm | 21.17 / 46.82 | 20.00 / 34.03 | 24.46 / 44.08 |
| reach / follow / in-band14 / contact | 0.722 / 1.0 / 0.890 / 0.013 | 0.725 / 1.0 / 0.897 / 0.011 | 0.728 / 1.0 / 0.855 / 0.011 |
| overhead (elev >= 140) taken | 8/28 (in-band 0.868) | 8/28 | 8/28 |
| connected (flood fill) full / knn | 20.08 (0 dropped) / 22.90 (10) | 18.91 / 21.72 | 22.82 / 25.63 |
| lost workspace poses | fold 87, slide 8, contact 5 | fold 86, slide 7, contact 4, parts 2 | fold 86 |
| complexity (tools/simplicity.py) | **45.25** | 49.0 | 49.0 |

Best parameters: `docs/concepts/rows/sidecar-roller-flank-knuckle-3r.json` best_params. In short: g 2.28, beta -174.7,
r_c 15.67, lift 1.41, hl 1.35, zr 3.01, s_arm 4.44, r_lobe 8.14, kK 2.52, c 0.021, bk1 27.7, bk2 35.7, a1max 56.6.

Cam at the winner, per K step:

| K (deg) | crank (deg) | pa crank | pa horn | contact r (mm) | flank radius (mm) |
|---|---|---|---|---|---|
| 0 | 0 | 6.3 | 8.0 | 15.8 | 4.2 |
| 20 | 8.8 | 0.1 | 24.1 | 17.5 | 7.9 |
| 40 | 17.8 | 3.9 | 35.6 | 19.9 | 11.9 |
| 55 | 24.6 | 6.8 | 42.3 | 22.0 | 14.9 |

Other numbers at the winner: crest 9.97 (limit 11.5). Arm clearance to hub K's skirt >= 1.58 (core metric). Roller
clearance to hub K >= 2.47. Low arm to lug >= 14.6.

The fast-best configuration is P1d (11.25). Worn frozen on Bench(110,360) exact it scores 20.48 plain, 21.58 near-touch
and 39.94 at 2 mm, with fold losses of 91 against P1's 87. Its 0.48 fast gain is fold tuned to the 160-pose sample
(round-3 lesson c), so the claim stays on P1.

## Red team (own)

- **The pose that jams.** None jams inside the range: force closure holds to the end of the law (both n . v > 0). The
  drive stops at the law's dK_max (54.3) and stop B sits at 56.2. Past it the fold takes the pose, so nothing jams.
  At the proposer's lug azimuth (beta -85) the horn pressure angle hits 45 after 8 deg of K, which would make it a
  stall, not a jam.
- **The point that pinches.**
  - The horn lug comes 1.38 mm from the skin at clip pose 29 (plane 77, elevation 141, axial -67) and the crank arm
    1.62 mm at workspace pose 130 (fast bench).
  - Frozen minimum metal is 0.32 mm. 45 frozen poses have drive metal at 1-2 mm, so the 2 mm near-touch (46.82) is
    worse than the lead's (44.08).
  - The flank's tightest radius is 3.7-4.2 mm, convex, at the rest end: the pitch-point nose. Contact stress is
    small at the clock spring's ~2.5 N, but this is the edge to inspect on the part.
- **The optimistic number.**
  - Fast 11.73 becomes frozen 20.08 (+8.4). Every knuckle in this family loses 8-10 points between those two benches.
  - The flank uses the ideal envelope. The wire-EDM / 5-axis tolerance on a 4 mm nose, plus MR63 play (radial
    clearance ~5-10 um, O3 pin fit ~10 um), gives ~0.09 deg of K slop at the flank and ~0.6 deg through the lobe
    follower and crank pivot (0.02 mm over the 4.4 mm short arm, times g). This is below the lead's rod-end slop
    budget (<= 1.2 deg).
  - The spherical lug and the arm tip over it are 5-axis parts. The 130-deg arc arm (51.5 mm developed, 3 mm Ti) is
    the longest cantilever in the drive. Its stiffness under the ~2.5 N contact force is not modelled: a 0.1 mm tip
    deflection would read ~0.3 deg of K.
  - Held out was not run (the verifier's job). The lead lost ~4 points held out.
- **Lost poses.** Overhead: fast 2/12 taken (fold 7, slide 3); frozen 8/28 (fold 14, slide 3, contact 3). Across the
  body: 18/26 taken (fold 8). Behind the back: 21/24 taken (fold 3). Rest: 56/58 taken (fold 2). The fold walls are
  the lead's: the drive's metal moved the in-band and contact terms, not the fold.

## What next

- The verifier re-measures the P1 claim: frozen exact, held out, flood. The harness is the model's `frozen` / `flood`
  modes, and the verifier should use its own copy.
- **Merge with the rod sidecar's dyad.** sidecar-longdyad's frozen 18.91 came from the longer K dyad (bk2 39). P1 sits
  at bk2 35.7. A roller drive on the rod sidecar's dyad and seats is the cheapest next cell. It is the same model with
  chain free.
- **Shorter arm.** The 130-deg wrap is forced by the pitch-point geometry, which needs the lug pointing away from hub 2.
  A crank pivot placed on the far side of hub K (a pivot seat on link 1b past hub K) would put the roller's chord
  through K's axis with a short straight arm. That needs a new pivot-seat parameter in the core (dR is fixed at hub
  2's rim today).
- The fold walls are the lead's (87 vs 86 frozen fold losses). This drive changes the metal term, not the fold. The
  fold levers (a2 / bk1 + bk2 / J1 seat walk) stay open as in the round-8 plan.

## New knowledge (predicts beyond this morphology)

1. **A roller pushing a flank between two axes through GH is a spherical cam.** The roller centre's height along the
   follower's axis moves by roughly (chord) x sin(angle between the axes) x (crank swing): ~10 mm here. A flat lug
   loses the roller. The lug has to be a shell at the roller's radius from GH, and the flank a ruled cone.
2. **Pressure-angle window for any two-rotor cam contact.** Let t be the angle between the two contact-point
   velocities and a the ratio of their speeds. Both pressure angles stay <= 45 iff a lies in
   [1 / (cos t + sin t), cos t + sin t]. The window is widest at t = 45 ([0.71, 1.41]) and shrinks to a = 1 at t = 0
   and t = 90.
   - If the contact slides outward along the driven lug, a falls as K opens and the horn pressure angle ends the
     stroke. At the proposer's geometry that happens after 8 deg of K.
   - The workable geometry puts the contact near the pitch point: t ~ 3 deg, the lug pointing away from the crank
     pivot. That forces a long wrapped arm when the pivot sits on the other side of the driven hub.
3. **Progressive laws do not work near a pitch point.** The relative velocity there is small, so any crank
   acceleration turns into a tight curve of the relative path. That makes a cusp at the flank's nose (c = 0.4 cuts
   at K = 0). Every CMA stream drove c to ~0.
4. **The rodless swap is worth about the same as the rod.** Frozen 20.08 (roller) vs 18.91 (rod), at the same fold
   losses. The roller version costs 3.75 complexity points less (no rod, no ball links) and is 1.2 gap points worse:
   its metal runs closer at 2 mm, and its arm is longer.

## Verification (independent skeptic, 2026-10-16)

Harness: `docs/concepts/verify/sidecar-roller-flank-knuckle-3r.py` (the claim's model loaded unchanged; frozen fit-60 shape
worn on Bench(110,360) exact, on the farm). Outputs: `docs/concepts/verify/sidecar-roller-flank-knuckle-3r_v_{bench,held}_frozen{,_env}.json`.

**Verdict: VERIFIED (not refuted). v_gap 20.08 (score 92.70) on Bench(110,360) exact; champion 75.94 on the same bench.**

| | claim | verifier (claim's sampling + added checks) | verifier, real envelope (`--head`) |
|---|---|---|---|
| gap (plain) | 20.08 | **20.08** | 19.96 |
| reach / follow / in-band14 / in-band10 / contact | 0.722 / 1.0 / 0.890 / - / 0.013 | 0.722 / 1.0 / 0.890 / 0.513 / 0.013 | 0.722 / 1.0 / 0.892 / 0.517 / 0.013 |
| near-touch 1 mm / 2 mm, min metal | 21.17 / 46.82, 0.32 | 21.17 / 46.82, 0.32 | 21.05 / 46.82, 0.32 |
| overhead (elev >= 140) | 8/28 | 8/28 (fold 14, slide 3, contact 3), in-band 0.868 | 8/28 |
| flood fill full / knn | 20.08 / 22.90 | 20.08 (0 dropped) / 22.90 (10) | 19.96 / 22.78 |
| held out (frozen, exact) | not run | **22.35** (near-touch 25.41, min metal 0.17, reach 0.700) | 22.23 |

Checks added on every taken pose (370 bench, 868 held out); **0 poses fail any of them**:

1. Cam closure in the world: the roller centre carried by the crank (T9 C0) sits on the synthesised roller-centre path of
   link 1a's flank (T1 P1(|dK|)): max error 0.000 mm. The model's per-pose K sense matches the sense the flank was cut for.
2. K sense: the roller can only push. Taken poses: 185 with K opened in the drive's sense, 185 at K = 0, 0 the other way.
3. Roller vs lug in the world: the roller centre stays >= 4.02 mm from the sampled lug metal (roller radius 3), and every
   taken |dK| (max 51.7) is inside the flank's range (dK_lim 56.25, ended by the law).
4. Pressure angles at each taken pose's K: crank 6.3, horn 41.0 max (held out 6.5 / 41.7), <= 45. The real lobe pressure
   angle with the exact phi law is 31.1 deg. The drive carries 51.7 deg of K, so it is not idle (>= 30).
5. DOF: 3 active (J1, J2, J3). K is slaved through lobe -> crank -> roller -> flank, with force closure from K's clock
   spring. The crank is set by the lobe. The two knee pins close the cuff (sensed, as in the lead). No passive coordinate
   is left undetermined. 0 passive translations; no gears, pulleys, cables or rods.

Defects found (none changes the verdict):

- **Lug sampling.** The lug row 0.3 mm behind the flank is projected onto the shell. That shrinks its chord to the roller
  centre below ROLL_R + 0.3, so the removal step deletes the whole row, and the sampled lug starts 1-2 mm behind the real
  flank. The harness's `--head` mode re-adds that strip, together with the roller pin's retaining head (O5 x 0.8 under
  the MR63; the claim's lowest metal was the roller's own underside). That metal lies in band, so the number improves a
  little: 19.96 on the bench, 22.23 held out. The claim's 20.08 stands as the conservative value.
- **Running gap.** The arm's arc rides 0.15 mm over the lug shell. The two are concentric spheres about GH, so the gap
  stays constant, and it is accepted as the cam pair's running gap, not as a 1 mm clearance between non-adjacent parts.
  The CAD has to hold it: a 0.15 mm gap between two 5-axis spherical surfaces.
- **Held out.** 22.35. The rod sidecar is 22.67 and the lead 26.75 on the same protocol, so the ~2.3 bench-to-held-out
  drop is in line with the family's.
- **Grid-dependent continuity.** The bench-grid flood fill (the sparse neighbour graph) drops 118 forced poses (53.48). The
  full and knn grids drop 0 and 10. The rule's metric is the full grid, which agrees with the claim. The knn number
  (22.90) is the cautious one.

Rank among the verified 3-active designs on Bench(110,360) exact frozen: the rod sidecar is 18.91, the parallelogram
sidecar 19.13, **this design 20.08**, frontload 22.82. Its complexity, 45.25, is the lowest of the sidecars. The fold
(87 workspace poses, 14 of 28 overhead) is still the limiter, the same as in the lead.
