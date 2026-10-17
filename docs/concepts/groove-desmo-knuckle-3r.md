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

