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
