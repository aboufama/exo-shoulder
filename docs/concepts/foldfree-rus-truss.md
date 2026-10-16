# foldfree-rus-truss - the fold lever of parallel spherical kinematics: three RUS legs closed by the wearer's GH

Lens: deployable structures and overconstrained / spherical linkage kinematics. Model:
`docs/concepts/models/foldfree-rus-truss.py` (imports the geometry, fitting, part checks and continuity of
`docs/concepts/models/human-closed-crank-rods.py`, the round-1 3-RUS model that was interrupted before screening).
Sweep: `docs/concepts/sweeps/foldfree-rus-truss.json`. Row: `docs/concepts/rows/foldfree-rus-truss.json`.

## Depth answers (before modelling)

1. **What a top practitioner of this field would do here.** A spherical-mechanism designer reads the 3R's J2 fold as
   the boundary of a serial spherical RRR's workspace: one leg, one band, angle(J1, J3) in [|a1 - a2|, a1 + a2]. The
   field's standard answer to a serial workspace boundary is to go parallel and give every leg its own boundary,
   placed outside the workspace, then check the one new failure mode parallel chains bring (the parallel or
   "type-II" singularity). Here the platform already exists: the user's humerus, and the user's glenohumeral joint is
   the passive spherical joint every spherical parallel manipulator (SPM) builds in at its centre. So the exo has no
   joint at GH. It is three RUS legs from the scapula to the arm:
   - an active crank hub on the scapula, with its axis c_k through GH;
   - a crank of arc beta_k;
   - a U-joint at the crank tip;
   - a thin rigid rod to a ball stud on the arm cuff.

   **The leg-fold theorem.** On the bench GH is fixed in S, so |T_k| (crank tip), |Q_k| (stud) and L_k are constant
   and the triangle GH-T-Q is rigid. Each leg is then a spherical RRR whose closure exists iff angle(c_k, Q_k) is in
   [|beta_k - gamma_k|, beta_k + gamma_k] (gamma_k = the T-Q angle set by the rod length). That is the same
   orientation-level band as the 3R, but there is one band PER LEG, and each leg can take a fold-free (c, q) pair from
   docs/research/fold/ends.json:
   - crank axis posterior-horizontal bvec(-30..-24, 4..8), hub on the back of the shoulder, hub band 100 %;
   - posterior arm stud;
   - fold-free on 100 % of the workspace at 65 / 65.

   The 3R cannot use these pairs, because its J2 hub and link 2 then float (docs/FINDINGS.md: the posterior plain 3R
   reaches 0.83 but has in-band 0.02). The truss has no J2: the rods take its place, and each rod is a thin body
   whose shape is fitted (bowed) over the skin.

   **Mobility, proven twice.** Grubler-Kutzbach on the bench (GH fixed): 3 legs x (R 1 + U 2 + S 3) + GH 3 = 21 joint
   freedoms, minus 3 loops x 6 = 18, gives 3. The 3 rod spins would be idle, but the U's pitch pin kills them. So the
   arm's 3 rotations map to the 3 crank angles, exactly 3, with no undetermined coordinate. Numerically, the leg
   constraint gradients are the moment lines m_k = T_k x Q_k, and a pose is taken only if
   |det[m1 m2 m3]| >= 0.10 (unit rows), i.e. the 3 x 3 Jacobian has full rank. The model counts the poses lost to
   this parallel singularity separately (`parallel_sing_ws`).

   **Every joint is a real component**, 0 passive translations:
   - O20 bearing hubs (12.25 stack);
   - O12 U-joint housings;
   - O12 rod ends on studs;
   - O5 Ti tubes;
   - 12 x 3 crank straps and base brackets;
   - a 14 x 4 arm saddle.
2. **Rawest material.** The posed skin of every bench pose: the signed distance of every metal sample, on the fast
   grid for the screen and on libigl's exact path for the claim. The fit clips at their full 10 fps: scapula and
   humerus rotations per frame, used for the leg-branch continuity (25 deg rule on every crank, U swivel and ball spin
   angle). The fold-free pair table docs/research/fold/ends.json, regenerated from the bench poses by the scan, not
   copied from a summary.
3. **The instrument.** These come from the field:
   - closed-form RUS inverse kinematics (A cos th + B sin th = C, branch fixed per leg);
   - the rod length set by interval stabbing (the L that maximises the share of poses with closure and >= 15 deg
     transmission), i.e. each leg's fold band placed by construction;
   - the screw / moment-line determinant for the parallel singularity;
   - K3 sphere tracing for every rigid part's underside;
   - point-cloud part-part clearance (1 mm, joint partners exempt only inside their housings).

   Runs: the farm (`tools/cloud_run.py sweep`) for the coarse sweep and CMA-ES for the refinement.
4. **The outside judge.** tools/concept_bench.py scores it with the same poses, metrics and contact rule as every row.
   The frozen shape is fitted on Bench(60,160) fast, then worn without refit on Bench(110,360) exact (lessons c, d,
   e: near-touch < 1 mm counted as contact, overhead >= 140 deg split out). The verifier's next step is an
   independent re-measure. The red team is at the end of this file.

## Second morphology (same lens): skin-normal skew-crank RSS truss - killed by kinematics before any parts

A Stewart-platform designer's first move would be RSS legs whose crank hubs sit FLAT on quiet skin. Their axes would
be the skin normals, not GH rays, which is the osn trick applied to every leg. A crank circle of radius rho centred at
O off GH only closes a leg when |Q - O| lies in a window at most 2 rho wide, and a stud on the moving arm sweeps
|Q - O| over a much wider range.

Measured with `skew_kin.py` (Bench(60,160) fast), over:
- 8 seats (the fold-free posterior seats, the top cap, the default dome points, the leader's J1 seat);
- 7 arm studs;
- the rod length chosen by stabbing.

Best single-leg workspace coverage:

| crank | best | median |
|---|---|---|
| skew, rho 15 mm | 0.49 | 0.38 |
| skew, rho 20 mm | 0.58 | 0.50 |
| skew, rho 30 mm | 0.73 | 0.65 |
| GH-centred spherical, beta 15 | 0.24 | 0.19 |
| GH-centred spherical, beta 20 | 0.43 | 0.32 |
| GH-centred spherical, beta 30 | 0.69 | 0.55 |
| GH-centred spherical, beta 50 | 0.975 | 0.86 |
| GH-centred spherical, beta 65 | 1.000 | 0.97 |

A truss needs all three legs at once, so a skew truss reaches at most about 0.58-0.73. Even a 60 mm crank circle
(rho 30) standing on its tangent plane, which already lifts 6-10 mm off the convex shoulder, misses 27 % of the
workspace on its best leg. That is >= 17 gap points from reach alone, before any part.

The kill is a closure theorem: only a crank circle on a sphere about GH turns the arm's large angular sweep into a
bounded angular band. Off-GH cranks turn it into a distance window that compact cranks cannot cover. This is the RUS
analogue of the osn finding that offsetting J1 / J2 off GH needs a radial slide.
