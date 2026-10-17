# groove-desmo-knuckle-3r: a spring-free, positive K drive (groove at hub 2, two-walled roller slot at K)

Round 10, lens 3 (low complexity at the lead's reach). The lead (roller-longdyad-knuckle-3r) slaves the knuckle K to q2:
the hub-2 rim lobe drives a bell crank, which drives an MR63ZZ roller, which pushes a conjugate flank on link 1a. K's
clock spring keeps both cam pairs closed, and stop A holds K in the dwell.

This concept makes **both cam pairs positive**, so the spring, its 6 mm cap and stop A go:

- **At hub 2:** the lobe becomes a closed **track groove** (1.52 wide, 1.5 deep) in the underside of hub 2's cap ring.
  An ISO 8734 1.5 m6 dowel in the crank's short arm rides in it.
- **At K:** the flank becomes a closed **two-walled slot** in link 1a's boss. An MR52ZZ (2 x 5 x 2.5) roller is captured
  in it.

The cells are the lead (pin knee, b3 tilt) and the control, kneeless-roller. Both parents are loaded unchanged.
Model: `docs/concepts/models/groove-desmo-knuckle-3r.py`; choose the cell with `GD_CELL=lead|kneeless`.

## Deeper-version answers (written before modelling)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - **Check the follower geometry the whole family's lobe formula assumes away.** The bench's lobe pressure angle,
     atan(s_arm λ / r) with λ = dK/dq2 / g, treats the follower as moving radially. It does not. The crank pivot sits
     d ≈ 16 mm off hub 2's axis. A dowel with a 4 mm radial lever therefore sits about 14.6 deg round from the pivot
     side, and moves mostly tangentially (r - d cos θ_F per unit crank angle). The groove's real pressure angle depends
     on whether the dowel moves with the cap surface or against it. That is the sign of sig · s_q, a property of the
     chain, not a free choice:
     - moving with the cap, at λ ≈ r / (d - r), the rise is almost a radial slot in the cap frame and the angle is ~30
       deg;
     - moving against it, the angle is ~78 deg (a jam).

     I compute it per K step and gate it at 43 - atan(0.1) = 37.3 deg, which allows for a greased hardened dowel
     sliding in a hardened groove ring.
   - **Check the second wall, not only the first.** A slot is two offset curves of the roller-centre path. Wherever that
     path curves with a radius below ROLL_R toward the free side, the outer wall is undercut. Below ROLL_R + 3.5 it is a
     convex knife edge. The parent only checks the inner flank, because a spring keeps the roller on one wall.
   - **Make the groove-fit window a drive limiter, not a clamp.** The groove can only be cut up to the pitch radius
     R_HI = 8.44. Its end is stop B, so the crest limit cuts dK_lim, the same way the parent's pressure-angle and
     clearance limits do. Every bench then loses the poses beyond it.
   - **Check that the groove's ends and the short arm clear link 2.** Do this at link 2's own level, as a planform
     check on every taken pose of every bench. An azimuth-only number is not enough.
   - **State the materials.** Ti on steel galls when it slides. The groove ring has to be hardened steel (440C or
     17-4PH H900) or a DLC-coated Ti cap.
   - **Report the backlash.** Groove play is 0.014 / s_arm · g and slot play is 0.014 / r_c, about ±0.5 deg of K. Set
     that against the lead's 5.18 deg fold margin.
2. **The rawest material.**
   - The posed skin through the bench's exact signed distance (CB_EXACT=1) on every Bench(110,360) pose and every
     held-out frame.
   - The design's own IK per pose: q2, dK, the crank angle, and link 2's exit azimuth at hub 2.
   - The synthesised roller-centre path in link 1a's frame, its curvature per 0.25 deg of K, and the pole of the
     crank / link-1a relative rotation.
   - The catalogue envelopes: MR52ZZ 2 x 5 x 2.5, MR117 7 x 11 x 3, ISO 8734 1.5 m6.
   - Not the proposer's summary numbers.
3. **The specific methods and tools.**
   - The parents' model code, loaded unchanged: spherical cam synthesis, the kit fold rule, the O20 stacks, part pairs
     and the 2 mm near-touch objective.
   - A closed-form gate 0, run as drive limiters in the same cam loop.
   - Farm sweeps (`tools/cloud_run.py sweep`), then CMA-ES from the top configurations (`tools/concept_cma.py`).
   - The claim protocol: fit on Bench(60,160), shape frozen, worn on Bench(110,360) exact and on the held-out set.
4. **What, other than me, shows the number is right.**
   - The bench, frozen and exact on Bench(110,360), and the held-out set.
   - The verifier harness `docs/concepts/verify/roller-longdyad-knuckle-3r.py`. It closes the cam and checks the
     roller against the lug, the K sense and the pressure angles.
   - A red-team pose list: rest, overhead, across the body, behind the back, and the lowest-metal poses.
   - The lead itself through the same code, as a control (capK 6, MR63 roller, no slot wall). It separates what the
     groove changes from what the measurement changes.

## Gate 0 (geometry, before any bench search)

Gate 0 was measured at the lead's verified parameters, with r_lobe re-cut to 7.06 and the MR52 roller. The results are
the model's own drive report, from `check` mode.

| check | lead cell | kneeless cell (its verified params, s_arm clamped 4.77 -> 4.6) |
|---|---|---|
| groove fit (pitch 7.06-8.44) | 7.06 -> 8.44 at dK 48.2 (s_arm 4.05): fits | needs s_arm <= 3.85 |
| real groove pressure angle (gate 37.3) | **30.5** (dowel moves with the cap, λ 0.872; family formula 26.6) | **54.2** (λ 1.152): fails |
| link 2 vs short arm + dowel (>= 1 mm) | exit >= 80.6 deg, planform 2.47 mm, 0 poses lost | exit >= 69.3 deg, planform 0.85 mm, 1 pose lost |
| MR52 roller, inner flank (parent limit) | dK_lim 48.5 (was 46.2 with MR63): +2.3 deg | 49.0 |
| **slot outer wall** | **undercut for K 0-7 deg; convex < 3.5 mm up to K 24 deg** | not reached (groove pressure angle cut first) |

**The limiter, measured.** At rest the roller centre sits about 1.5 mm from the pole of the crank-vs-link-1a relative
rotation. Its path in link 1a's frame turns with a radius of 1.03-1.84 mm toward the free side over K 0-7 deg, and
reaches 6.0 (ROLL_R + RHO_MIN) only at K ≈ 24 deg.

- With a spring, that is harmless: the inner flank is concave there.
- With a slot, the outer wall cannot be cut. K is then held by nothing in the opening direction at rest, which breaks
  R17.

The lead's CMA put the roller near the pole on purpose. It keeps the flank short and the horn pressure angle low.

Worn at the lead's drive, the groove-desmo variant scores fast plain 86.2 (reach 0.34). The drive's own range collapses
to 0.

**The variant that removes it: move the roller off the pole.**

- **Single roller.** A drive-only map at the lead seats (`scratchpad polemap`: beta x r_c x g, 273 + 594 cells, plus the
  full 288-config LHS on the farm) finds a sharp boundary. Cells near the lead's drive (beta -171.5, r_c 15.6) still
  have the outer wall convex below 3.5 mm up to K 18.5 deg. One step further out (g 2.47, beta -170, r_c 16) the outer
  wall is concave or convex at >= 4.1 mm everywhere. The drive's own range then ends at the parent's horn pressure
  angle, at **dK_lim 41.2** instead of 46.2 (lead, MR63) or 48.5 (MR52, spring-loaded). The best cusp-free cells cluster
  at dK_lim 37-41 (horn pressure-angle limited). The wide LHS (drive box widened to RF's own limits: beta -215..-125,
  r_c 13-22, g 1.6-3.2) found nothing better: best 2 mm gap 44.9 (plain 34.3).
- **Kneeless control.** The same wall at its verified drive: cusp K 0-5.75, convex < 3.5 to K 22. The groove also needs
  kK / g <= ~0.9 (pressure angle 54 at its kK 2.57 / g 2.23). The best cusp-free cell is dK_lim 35.2 (g 2.23,
  beta -165, r_c 18, kK 2.0).
- **Conjugate return roller (geometry only, not benched).** At the lead's own drive (MR52, inner flank to dK 48.5), a
  second roller on the crank arm can carry the return wall: about 16 mm from the main roller (tangent-plane offset 13.5
  / -9), return wall concave everywhere, both pressure angles <= 35.4, 15 mm off hub K's axis. No point within 12 mm of
  the main roller qualifies. It would cost a second arm branch, a second bearing and a second flank on the deltoid,
  which is where the lead's flank boss already pays its contact poses. This is the only route found back to the
  spring-loaded 48.5-deg stroke.


## Control: the lead through this file's protocol

`GD_CONTROL=1` runs the parent itself through this file: MR63 roller, capK 6, no slot, no groove gates. It reproduces
the verified lead exactly, so the protocol adds nothing of its own. Same-protocol numbers:

| | fast plain / 2 mm | frozen exact Bench(110,360) | 1 mm / 2 mm | held out | workspace in-band all / elev 90-140 | overhead taken |
|---|---|---|---|---|---|---|
| lead (control) | 13.19 / 16.57 | **18.67** (reach 0.725, ib14 0.8937, contact 0.0054) | 20.30 / 33.10 | 23.73 | 0.854 / 0.798 | 8/28 |
| groove-desmo, interim (lead seats, g 2.47, beta -170, r_c 16) | 14.67 / 17.21 | **19.29** (reach 0.714, ib14 0.8986, contact 0.0054) | 20.94 / 33.68 | 24.96 | 0.853 / 0.781 | 8/28 |

## Red team of the interim configuration (frozen exact Bench(110,360), `redteam` mode)

- **Lowest metal: 0.07 mm** at ws (plane -60, elev 60, axial 105). It is the same pose and the same value as the lead,
  so it is not the drive. The next lowest are 0.75 mm (E strap / hub 3, across the body) and 1.02 mm (hub 2's crown
  edge, plane 15, elev 90).
- **Contact poses: 2**, both overhead at elevation 165: (15, 165, -60) and (30, 165, -60). The horn boss and the crank
  arm go 6-11 mm into the deltoid. These are the lead's own two contact poses; the slot's outer wall adds none.
- **Named poses:**
  - rest (dK 4.6, groove pitch 7.19) and overhead axial -135 (dK 5.8): taken. The lowest part is the horn boss at
    2.5-2.8 mm.
  - across the body: taken (dwell, link 2 clears the short arm by 3.42 mm).
  - overhead axial 0 / plane 90, extreme internal rotation, behind the back, abduction 90: lost to the fold or to the
    knee slide, as in the lead.
  - extreme external rotation: needs dK 62.1 (pitch 8.84 > 8.44, past the groove), lost to the fold.
- **Link 2 vs the short arm and dowel (planform, link 2's level):**
  - fit bench: min 2.47 mm;
  - Bench(110,360): min 1.22 mm;
  - held out: min 1.22 mm (834 taken poses);
  - exit azimuth >= 70.2 deg from the pivot side on every taken pose.

  The tightest is 0.28 mm at (0, 90, 0), a pose already lost to the fold. If a future fit takes it, it is the first
  pose this gate will cut.
- **Optimistic number:** fast -> frozen +4.62, and held out +5.67 over frozen. These are the lead's own deltas
  (+5.48 / +5.06): the drive change does not make the shape generalise worse.
- **Jams and pinches the bench does not see:**
  - **Onset corner.** The lin law kinks at the dwell's end. In the cap frame the groove turns from the base circle to
    an almost radial rise, because the dowel moves with the cap: about an 85-deg pitch corner. A real groove needs a
    blended onset (cycloidal over a few degrees of q2). That shifts K by < 1 deg near the onset, inside the 5.18-deg
    fold margin. Not modelled.
  - **Materials and friction.** The sliding dowel needs a hardened groove ring. Friction is in the groove's
    pressure-angle budget (mu 0.1).
  - **Backlash.** About ±0.54 deg of K (groove 0.014 / s_arm · g + slot 0.014 / r_c). The spring parent drifted
    4.1-7.7 deg with the thorax tilted (pick1's R17 note), so the positive hold is a real gain in R17 terms.

## Search (Bench(60,160), the 2 mm near-touch objective; files: `docs/concepts/sweeps/groove-desmo-knuckle-3r.json`)

1. **Gate-0 checks** at both parents' verified parameters (2 configs, above).
2. **Drive-only pole maps** at the lead seats and the kneeless seats. These cover 1,191 drive cells (beta x r_c x g)
   through the model's own cam loop, with no bench. They locate the cusp-free region.
3. **Wide LHS on the farm:** 288 configs, drive box widened to RF's own limits, plus kK, a1max and bk2. Best 2 mm gap
   44.9: the wide box is mostly infeasible (pressure_crank 112, pressure_horn 50, groove-pa 45, flank_cusp 28, CRK-hubK
   27, wall2_cusp 19).
4. **CMA-ES on the farm, lead cell.** Three streams, 2,595 evaluations, from the cusp-free cell (g 2.47, beta -170,
   r_c 16):
   - A: drive only (g, beta, r_c, lift, hl, zr, s_arm, r_lobe, kK, a1max);
   - B and C: drive plus seats (az2, el2, lc, phib, smhi, bk1, bk2, wd, wa, b3).

   No stream improved on the start point. Best 2 mm gap 17.21 in every stream; stream A's top 5 are distinct
   parameter sets at the same 17.21, a plateau. B found a reach-0.80 shape, but at in-band 0.867 (2 mm gap 26.2).
5. **Convergence gate** (score points = gap / 2.75), as gain over the 2nd half / gain over the last third / top-5
   spread:

   | stream | gain 2nd half | gain last third | top-5 spread | gate |
   |---|---|---|---|---|
   | A | 0.00 | 0.00 | 0.00 | passes |
   | B | 0.00 | 0.00 | 3.51 | fails on the spread (269 of 833 dishonest: the seats walk off the drive's feasible set) |
   | C | 0.00 | 0.00 | 1.09 | passes |
   | pooled | 0.00 | 0.00 | 0.00 | passes |

## Result (lead cell; best configuration = the lead's verified params with g 2.47, beta -170, r_c 16, r_lobe 7.06, capK 0, MR52)

| bench | gap (score) | reach | follow | in-band 14 | in-band 10 | contact | 1 mm / 2 mm | min metal |
|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fast, fit | 14.67 (94.67) | 0.756 | 1.0 | 0.897 | 0.526 | 0 | - / 17.21 | - |
| **Bench(110,360) exact, frozen** | **19.29 (92.99)** | 0.714 | 1.0 | 0.899 | 0.530 | 0.0054 | 20.94 / 33.68 | 0.07 mm |
| held out, frozen | 24.96 | 0.664 | 1.0 | 0.897 | 0.528 | 0.0107 | 27.64 / 37.04 | 0.33 mm |
| lead, same protocol | 18.67 / held 23.73 | 0.725 | 1.0 | 0.894 | 0.513 | 0.0054 | 20.30 / 33.10 | 0.07 mm |

- **Overhead (elev >= 140):** 8/28 taken, in-band 0.899. That is the lead's 8/28: nothing traded away.
- **Frozen losses:** fold 92, slide 9, contact 2 (the lead's: 88 / 9 / 2). The 4 extra fold poses are the 5 deg of
  drive stroke the outer wall costs: dK_lim 41.2 vs 46.2, dK taken 40.5 vs 45.6.
- **Flood:** full 19.29 (0 dropped), knn 21.52 (lead 20.34).
- **Workspace in-band** (unscored, taken poses): all 0.853 / elev 90-140 0.781, vs the lead's 0.854 / 0.798 through
  the same function. This is below the lead at elev 90-140 (pattern L2).
- **Complexity** (tools/simplicity.py v2.1): **18.25** vs the lead's 20.25. The clock spring goes (-3); the sliding
  dowel comes in (+1). 0 passive translations, 3 active DOF.
- **Hold (R17):** K is positively held at every pose, with slop about ±0.54 deg, where the spring parent drifted 4-8 deg
  with the thorax tilted. The dwell holds K with a radial groove normal, so the K torque puts no moment on J2.

## Verdict

**Screened: a complexity and hold Pareto point, not a lead change.**

The spring-free positive K drive exists:

- The **groove at hub 2** passes gate 0: it fits the cap, its real pressure angle is 30.5 deg, and link 2 clears the
  short arm by >= 1.22 mm on every taken pose of all three benches.
- The **two-walled slot at K** only works once the roller moves off the crank / link-1a relative-rotation pole. That
  costs 5 deg of drive stroke (41.2 vs 46.2).

The cost is +0.62 frozen and +1.23 held out against the lead through the same protocol, with overhead unchanged. The
gain is 2 complexity points (18.25 vs 20.25) and K held both ways (about ±0.5 deg of slop instead of the spring's 4-8
deg of tilted drift).

**Open lever, measured geometrically but not benched:** a conjugate return roller about 16 mm from the main roller. It
would restore the 48.5-deg MR52 stroke, at the price of a second flank on the deltoid.

**Kneeless control:** the same wall again. Its farm CMA (1,329 evaluations, from the cusp-free cell) reached a 2 mm gap
of 20.94: reach 0.775, in-band 14 0.893, contact 0.042 (plain about 17.5), against the lead cell's 17.21 / 14.67. Its
gate: 0.20 / 0.04 / 0.20, which passes. Worn frozen on Bench(110,360) exact it scores **24.0**: reach 0.711, follow 0.955, in-band 14 0.894, contact 0.045, and 17 contact plus 3 parts poses (the parent's part-pair clearances; link 2 vs the short arm loses none, planform >= 1.08 mm). Its parent kneeless-roller scores 21.07. The kneeless cell stays the worse cell, as its parent is.

The core's component clamp holds the short arm's radial lever at s_arm >= 4.0 in both cells. That is the parent's
4-6 limit, and the groove does not need it. The groove-fit limiter uses the value actually worn, so every claim
respects the window.

## Independent check (the round's roller-flank verifier, retargeted at this model)

Script: `docs/concepts/verify/sidecar-roller-flank-knuckle-3r.py`. It is retargeted the same way the lead's verifier
retargets it, at this model's class, clamp, params and roller radius 2.5.

Frozen exact Bench(110,360): **19.29, with 0 failing taken poses out of 367**:

- cam closure 0.0 mm;
- roller to lug metal (the slot's outer wall included) 2.805-3.312 mm, never inside;
- K sense always the drive's (0 wrong);
- pressure angles: crank 13.9, horn 42.6 (<= 43);
- real lobe pressure angle by the verifier's radial formula: 26.6. The groove's own off-axis value is 30.5.
- the drive is not idle (dK 40.5 of 41.25);
- corrected gap 19.29.

## Verification (independent skeptic, 2026-10-17)

Harness: `docs/concepts/verify/groove-desmo-knuckle-3r.py`. It loads the claim's model unchanged (GD_CELL=lead) and wears it
by the claim's own protocol: fit on Bench(60,160) fast, freeze the shape, wear it on Bench(110,360) exact or held out.
Outputs are in `docs/concepts/verify/groove-desmo-knuckle-3r_v_*.json`. All runs were on the CPU farm.

**Verdict: VERIFIED, not refuted.** The corrected gap is **22.64** (score 91.77). The champion scores 75.94 on the same
bench. The claimed 19.29 does not survive: +3.35.

### The finding: the groove does not fit its own window

The claim's groove-fit gate is planar and linear: crest = r_lobe + s_arm·K/g, which gives 8.24 at dK_lim 41.25. Two
things make the real path different:

- The crank turns about dR, a line through GH tilted **14.78 deg** from hub 2's axis.
- The dowel drifts **15.6 deg** in azimuth about hub 2 (from -14.6 to -30.2 deg) over the stroke.

So the dowel's real radial lever grows from 4.05 to about 8 mm/rad. Read from the worn frames (path vs frames 0.000 mm),
the true crest is **8.93 at K 41.25** and 8.89 on taken poses. The claim's own window is 8.44, set by a 0.8 mm outer
wall. At 8.93 that wall would be 0.31 mm.

The groove end is stop B, so stop B moves to **K 32.25 deg**, where the true crest meets 8.44. The claim's own limiter
was cutting at 48.2.

### Corrected numbers

| bench | claim (reproduced) | corrected | what changed |
|---|---|---|---|
| Bench(110,360) exact, frozen | 19.29 | **22.64** (reach 0.6806, follow 1.0, ib14 0.8986, ib10 0.5296, contact 0.0056) | the claim protocol re-run with stop B at 32.25 (`--truewin`): 0 failing poses. Dropping the 12 taken poses past the window gives the same 22.64 |
| 1 mm / 2 mm | 20.94 / 33.68 | 23.76 / 35.06 | |
| held out, frozen | 24.96 | **28.90** | 37 poses past the window dropped |
| flood full / knn | 19.29 / 21.52 | 22.64 / 24.04 | |
| envelope (`--env`) | 19.15 | 22.50 | the slot outer wall's first row and the lug edge strip, which the claim's chord filter deletes, restored: no new contact or parts pose |
| overhead (elev >= 140) | 8/28 | 8/28 | none of the cut poses is overhead |

Against the lead's 18.67 this is +3.97, not +0.62. The Pareto trade becomes 2 complexity points (18.25 vs 20.25) for
about 4 gap points.

### Checks that pass on every taken pose

- **Roller-flank** (the round's verifier, copied):
  - cam closure 0.0 mm;
  - roller to lug and slot 2.805-3.31 mm (2.798 with the envelope);
  - pressure angles: crank 13.9, horn 42.6 (39.0 at stop 32.25);
  - K sense always right.
- **Frames:** J2 and J3 axes and K agree to < 0.0001 deg.
- **Fold margin:** min 5.39.
- **Groove in 3-D:**
  - pressure angle 36.17 deg against the 37.29 gate (the claim's planar value was 30.5; margin now 1.1 deg);
  - the "with" arrangement confirmed from the frames (dq2/dK -0.464);
  - centreline self-clearance 2.40 mm (rule >= 2.02, so the channels do not merge);
  - dowel axial travel 0.23 mm.
- **Link 2 vs the true dowel and short arm** (3-D crank, boss point carried by the crank): >= 1.217 mm.

### Not on the bench, but corrects the claim

- **Dowel tilt binds a straight dowel.** The dowel axis tilts up to 4.2 deg against hub 2's axis, across the near-radial
  rise groove. Over the 1.5 mm engagement that is 0.108 mm of run-out, against a 0.02 mm clearance.
  - A straight O1.5 dowel binds.
  - Fix 1: a 1.61-wide groove. K slop is then about ±1.6-2.0 deg, not the claimed ±0.54. That is still better than the
    spring's 4-8 deg drift.
  - Fix 2: a crowned or ball-ended dowel.
- **Short arm vs link 1b's plate.** The dowel's base sits at link 2's boss underside (U0). The 3 mm short arm therefore
  runs in link 1b's plate levels inside hub 2's footprint and needs a pocket there. This is not modelled. The parent's
  rim-lobe follower has the same issue.

### Champion through the same bench

75.94 (Bench(110,360) exact, the risley-turret verifier). The checks added here apply only to the K drive and the
knuckle frames, which the plain spherical 3R does not have.
