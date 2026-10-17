# trimlug-k165-knuckle-3r: the slipper-nose lead with its horn lug trimmed / raised at the two elev-165 contacts

Lens: round 11, lens 3 lever c (overhead cone), run as a polish of the lead's T5 watch reason. Family: slaved-knuckle 3R
(pin knee). 3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, no gears / pulleys /
cables / rods. Model: `docs/concepts/models/trimlug-k165-knuckle-3r.py` (on the lead
`docs/concepts/models/slipper-nose-knuckle-3r.py`, SN_CELL=lead). Sweeps: `docs/concepts/sweeps/trimlug-k165-knuckle-3r.json`.
Row: `docs/concepts/rows/trimlug-k165-knuckle-3r.json`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do here that the spec does not ask for.**
   - Do not move the working surface if dead metal is what touches. The flank is a ruled cone through GH, and the nose
     only uses a 2.5 mm radial slice of it. Most of what dips into the skin at pose 264 is the lug's 6 mm back band and
     its outer end, not the flank face. The first fix is to remove metal the contact never uses. That means a
     trim at the farthest contact radius plus a wall, and a chamfer on the back band's underside that rises with the
     distance behind the flank. Neither touches the nose, the arm or the cam table, so neither can cost drive stroke
     or crank in-band. Only if that is not enough does the flank layer itself go up, and then the nose has to be
     lengthened and the arm raised with it.
   - Count what the lift really moves. Raising the lug's shell by dz raises its top too, so the arm tip that sweeps
     over it must rise by dz. The nose dowel must be dz longer to keep a full 2.5 mm contact line. That arm rise is the
     in-band risk the judge named, so it is modelled as metal, not assumed away.
   - Report contact as depth (T5), not only as a pose count. A 1 mm improvement that leaves the pose in contact is still
     real for the wearer: the drive presses less into the deltoid. Report the held-out depth too.
2. **Rawest material.** The posed skin itself: the bench's exact per-pose skin distance field, sampled at every lug,
   arm, nose and hub-cap point at poses 237 and 264 and over every taken pose. The motion clips, both bench and held
   out, with the held-out set only as a column. The lead's per-pose lost list
   (`docs/research/fold_ceiling/lost_poses_roller-longdyad-knuckle-3r.json`). The cam table: contact radius, pressure
   angles and lift-off per 0.25 deg of K. Not the round-11 summary numbers. Those are only the hypothesis to check.
3. **Specific methods and tools.**
   - The lead's spherical conjugate-cam synthesis, re-run when the lug layer changes. The flank is the same ruled
     surface, but the arm-over-lug clearance (CRK-HORN) and the lug's swept cut are re-checked.
   - Per-sample skin depth with r from K's axis and the distance behind the flank.
   - The lead's claim protocol: fit on Bench(60,160) fast, shape frozen, worn on Bench(110,360) exact and on the held-out
     bench.
   - The farm sweep over the trim / chamfer / lift / crank / cap parameters, and CMA-ES only if the coarse sweep is
     not flat. Drive law, beta, g, r_c and every seat stay fixed at the lead's verified values, as the spec says.
4. **What, other than me, shows the number is right.**
   - The bench (`tools/concept_bench.py`), exact path.
   - The lead's Frozen class, which reproduces 18.49 before any change.
   - The held-out bench.
   - The 1 / 2 mm near-touch audit.
   - A red-team pose list: every taken pose whose minimum metal falls by more than 0.5 mm, and the lowest metal over the
     cone set.
