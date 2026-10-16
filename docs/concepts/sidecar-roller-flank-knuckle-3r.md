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
