# skin-normal-3r-knuckle-cufflink - all-skin-normal 3R closed by three pins (J2 knuckle + pinned cuff link)

## Deeper version (answered before modelling, 2026-10-16 01:55 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** Solve both passive sub-loops in closed
   form instead of by grid + secant, so branch, authority and toggle are explicit: the knuckle's radial closure is a
   single sinusoid in qk (lk rho cos(Phi - qk) = c0 - s_n + lk rho cos Phi, two roots, keep one sign of sin = one
   assembly mode, authority lk rho |sin| >= 5 mm/rad keeps it away from toggle), and the cuff link is a two-circle
   intersection (E-arm circle about J3's line, link circle about the arm pin) on a fixed elbow sign with the elbow
   angle kept 25 deg off straight / folded. Choose c0 and the knuckle mid AUTOMATICALLY from the fit set (maximise
   poses with a valid root inside +-35 deg), and centre the cuff on the mid in-plane drift, so the sweep searches
   seats, not bookkeeping. Keep the family a strict superset of the verified controls: b1 = b2 = 0 makes the knuckle
   idle (constant radial) and the design collapses to the zero-passive spherical 3R at those seats (41.73 exact) plus
   the pinned cuff instead of the 2 guides (45.31 / 42.59). Make the cuff parts one flat rotor plate (hub 3 + E arm)
   and flat pinned plates: no skin-shaped plates on the new parts.
2. **Rawest material.** The posed render skin of every bench pose through the bench's signed distance (grid, then the
   exact libigl path for the frozen check), the rest-pose skin and its face normals for the seats (libigl exact), the
   fit clips at their full 10 fps for continuity of all 6 joint values (q1, q2 - qk, q3 + psi, qk, qa, qb) and for
   the design steps (c0, mid drift), pipeline/conformal/band_poses_wsf.b64 for the rotations. Not the snh sweep
   record (its in-band premise is the risk under test).
3. **Specific methods and tools.** Paden-Kahan spherical IK of the axis directions + exact screw drift of the line
   offsets (the verified seed: S.Design.ik), closed-form knuckle and two-circle cuff closure, Grubler-Kutzbach mobility
   (7 bodies, 6 x 1-DOF joints + GH: M = 3, no redundancy), sphere tracing on the signed-distance grid for every
   underside (S.Model.needed), exact cylinder signed distances + mid-surface kd-trees for part-part clearance,
   tools/concept_sweep.py / tools/concept_cma.py on the cloud CPU farm.
4. **What, other than me, shows the number is right.** tools/concept_bench.py (same poses as the baseline 68.93 and
   the controls), the in-model controls (b1 = b2 = 0 at the leader seats), the frozen-shape wear on Bench(110,360)
   exact (lesson c), the adversarial verifier, and the red-team list below (the pose that jams, the point that
   pinches, the optimistic number).

