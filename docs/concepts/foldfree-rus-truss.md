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

## Measured, step 1: every leg can be fold-free, but every fold-free crank sweeps the trunk or the arm

All data come from Bench(60,160) on the fast grid. The scripts and their JSON are in docs/research/rus/:
`leg_bands.py`, `crank_park.py`, `skew_kin.py`.

**1. Leg bands (`leg_bands.json`).** The scan covered 8 crank seats x 35 arm studs. A stud is set by s mm down the
humerus and theta deg about it (+ posterior), with the ball about 61 mm off the axis. For each pair the scan finds the
smallest crank arc beta, with its best rod angle gamma, whose band (10 deg margins) holds >= 98 % of the workspace
and every clip frame. 188 of the 280 pairs have such a leg with beta <= 90:

| seat | fold-free studs | beta / gamma (deg) |
|---|---|---|
| posterior-horizontal, bvec(-36..-24, 4..16) | humeral-head level, posterior-medial (s 0-20, theta 90-150) | 60-65 / 58-71: compact |
| top / dome seats (-24,78), (84,82), (60,75), (-10,40) | | 70-90 / 73-107: long cranks, long rods |

A stud is a point, not a line, so the leg uses the signed angle angle(c, Q). The 3R's J3 line can use either end:
(-24,4) vs wdir(80,-90) spans 10.9-119.3 deg for +w and 60.7-169.1 for -w. The posterior leg is the 3R's
fold-free 65 / 65 pair with the stud on the +w end.

**2. Crank parking (`crank_park.json`).** For 12 fold-free legs x 2 IK branches, every crank centreline ray (alpha
0..beta in 5 deg steps), at the crank angle the leg takes in each valid pose, was marched for the K3 skin requirement
(capped at 160 mm):

| leg | branch | crank radius need p50 / p90 (mm) | skin at the seat |
|---|---|---|---|
| posterior seat (all 6) | sigma +1 | >= 160 / 160 (the crank rays run through the trunk or the arm in most poses) | 93-102 |
| (-24,4), stud (10,90), beta 65 | sigma -1 | 93.1 / 106.7 (the best leg) | ~93 |
| other posterior legs | sigma -1 | 93-116 / 123-160 | 93-102 |
| top (-24,78), stud (0,120), beta 80 | sigma -1 | 60.4 / 85.3 | ~51 |
| top (84,82), stud (30,30), beta 70 | sigma +1 | 62.7 / 93.5 | ~45 |
| (-10,40), stud (0,150), beta 70 | sigma -1 | 82.8 / 159.7 | ~65 |

**The leg's fold band and its crank parking pull in opposite directions.** This is the same trade the 3R makes
between J1's band and hub parking (docs/FINDINGS.md):
- a fold-free leg needs a 60-85 deg crank;
- a 60-85 deg crank circle about a scapula-fixed axis sweeps the region the arm passes through (or the trunk on the
  other branch);
- so a rigid crank must stand 14-60 mm (p90) above the skin at its far end.

The truss has three such cranks, where the 3R has one J2 hub.

## Measured, step 2: the full model on the informed legs (Bench(60,160) fast, every model check on)

`docs/concepts/sweeps/foldfree-rus-truss.json`. Each evaluation takes 500-1100 s on the shared box: the rod and crank
marches leave the grid box and fall back to libigl's exact path.

| config | legs (seat / stud / beta / branch) | p | kin-valid ws | det ok ws | taken | gap | why |
|---|---|---|---|---|---|---|---|
| informed-1 | (-24,4)/(10,105)/65/+1, (-42,20)/(10,150)/65/+1, (-10,40)/(0,150)/70/+1 | 100 | 0.58 | 0.675 | 0 | 275.0 | cranks fitted at the 220 mm march ceiling (r_T 230 on all three legs), F 74-148; 125 collisions (bracket / hub vs crank 2, ball / ball) |
| informed-2 | (-24,4)/(10,90)/65/-1, (-36,16)/(10,120)/65/-1, (-24,78)/(0,120)/80/-1 | 100 | 0.705 | 0.80 | 0 | 275.0 | r_T 230 on all three legs again, rods 212-294 mm; 154 collisions (ball 1 / ball 2: the studs sat 10 mm apart, crank 0 / crank 1) |
| informed-3 | (-24,4)/(10,90)/65/-1, (-36,16)/(10,120)/65/-1, (-24,78)/(0,150)/85/-1 | 90 | 0.686 | 0.76 | 0 | 275.0 | the 90th-percentile fit lowers r_T to 112-153 (off the ceiling) and every leg is valid on 0.98, but all 151 kin-valid poses collide: the base brackets sit in the cranks' sweep (br/crank 136) |
| informed-4 | same + `crank_over` (each crank one strap layer over the brackets) | 90 | 0.659 | 0.725 | 0 | 275.0 | 145 collisions: the brackets climb to the 131 mm hub face of the (-36,16) seat and still cross the cranks; crank 0 / rod 0 in 32 poses (the rod folds back over its own crank) |
| informed-5 | same, p 95 | 95 | 0.682 | 0.756 | 0 | 275.0 | 150 collisions (bracket / crank) |
| red-team ceiling | informed-4 with every part-part collision switched OFF | 90 | 0.659 | 0.725 | reach 0.34 | 253.41 | the optimistic bound if every bracket, crank and rod could be routed around the others at no cost: follow 0.23, in-band 14 0.18, contact 0.53 |

Each leg's own validity in the model (closure + 15 deg transmission) is 0.93-0.96 of the workspace, so the fold
lever works per leg. The truss as a whole is limited by three things:
- the parallel singularity: det >= 0.10 holds on only 0.675-0.80 of the workspace when the fold-free studs cluster
  on the posterior humeral head;
- the cranks: every fold-free crank is fitted at or near the ceiling, because in a few % of the valid poses the
  crank's middle runs under the raised or extended arm (crank_park: mid-span need p50 65, p90 105-130 mm, against
  55-74 mm at the tip and 93-114 mm at the hub seat);
- part collisions between three legs that share the posterior shoulder.

## Verdict: killed after the coarse screen

Six full-model evaluations were run: five honest, one red-team ceiling with collisions off. None takes a single pose,
and the optimistic ceiling is gap 253.41 (score 7.9). The leader is skin-normal-3r-pin-knee: 26.34 fast, 33.84 frozen
exact.

**The idea is right per leg.** Each RUS leg closed by the user's GH has its own fold band, and fold-free legs
exist: 188 of the 280 seat-stud pairs, with legs valid on 0.93-0.98 in the model.

**It dies as a truss, for three measured reasons, each enough on its own:**
1. **Crank parking.** A fold-free leg needs a 60-85 deg crank. Its circle about a scapula-fixed axis sweeps the
   region the raised or extended arm occupies (mid-span need p90 105-130 mm), or the trunk on the other branch.
   This is the 3R's J1-band versus hub-parking trade, met three times instead of once.
2. **The parallel singularity.** The fold-free studs cluster on the posterior humeral head, so the moment lines are
   nearly coplanar: det >= 0.10 on only 0.675-0.80 of the workspace. That alone caps reach near 0.7, about 20 gap
   points.
3. **Part count.** About 15 rigid parts are each fitted to their own 90-95th-percentile pose set: 3 hubs, 2-3
   brackets, 3 cranks, 3 U housings, 3 rods, 3 saddles. With collisions off, 53 % of the kinematically valid poses
   still put some part inside the skin.

**Not done, and why.** The farm coarse sweep (240 random dome / BOTTOM-stud configurations) was queued, then
cancelled with 7 of 24 chunks running. The shared farm queue stood at 107 jobs with 20 running. The random layouts
are not fold-free by construction, so they could only score worse than the informed ones, and the informed ones
already showed the failure is structural. The 4 CMA streams were cancelled before they started. So:
- the convergence gate is not applicable (killed after the coarse screen);
- no frozen Bench(110,360) wear (nothing is taken to wear);
- near-touch and overhead splits are empty.

## Red team (the pose that jams, the point that pinches, the number that is optimistic)

* **Jam pose.** A leg at dead centre (the rod perpendicular to the crank-tip velocity; transmission < 15 deg) locks
  the arm on that leg's band edge. The model drops those poses. On the posterior legs they sit at the band floor (c-Q angle 4-9 deg over the
  workspace) and at the ceiling (115-155 deg). Which arm poses these are was not traced in this screen.
  The parallel singularity (det < 0.10) is a second jam set: 20-32 % of the workspace with clustered studs. There the
  three rods cannot resist one moment direction, so an MVP2 motor torque is lost.
* **Pinch point.** Between a rod and its own crank on the -1 branch, which keeps the cranks out of the trunk: the rod
  folds back over the crank (32-145 poses). Between the crank's mid-span and the posterior deltoid when the arm
  extends behind the back. And between ball studs 10 mm apart (informed-2: 64 poses).
* **The optimistic numbers.**
  - The kinematic leg scans used 10 deg band margins and 98 % coverage. The model's 15 deg transmission gives
    0.93-0.98: optimistic by 2-7 %.
  - The bench fixes GH in S. On the user GH translates a few mm. The truss is the one morphology here with no
    stiffness against GH translation (its 3 extra mobilities are the arm's translations), so the crank angles also
    read GH translation as rotation: sensing error ~ GH shift / (60-90 mm lever), about 2-3 deg for 3 mm.
  - For MVP2, the rod forces sum to a net force on the humeral head (Sigma F_k is not 0). A serial 3R reacts that
    force through its base instead.
  - The red-team ceiling (collisions off) is the honest upper bound and is still 253.

## What happens next (altitude)

* The fold lever has to come from ONE extra rotation that the arm sets. A parallel truss multiplies the parking
  problem by three instead of solving it once. So the levers left are a rocker (acromial-rocker-3r), a closure-set
  arc (closure-set-arc-knee-3r) and a virtual J2 (j2-arc-sector-3r, virtual-pole-4bar-j2). All are under test.
* Reusable result: docs/research/rus/crank_park.json gives the crank-parking need per station.
  - Tip p50 55-62 mm for posterior legs, against a hub seat at 93-114 mm: the far end of a posterior-horizontal arm
    lies on quiet skin; the middle does not.
  - A 3R J2 hub placed at the tip region of the posterior J1's 65 deg circle would sit at 55-74 mm (p50 / p90).
  - This is a parking check the posterior fold-free 3R (ends.json) has not had.
* Reusable tooling: the patch-on-load pattern (foldfree-rus-truss.py `load_base`, coaxial-rus-turret.py `PATCHES`).
  It lets a morphology variant change a verified model in a few asserted lines instead of a copy.
