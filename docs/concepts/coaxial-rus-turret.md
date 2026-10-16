# coaxial-rus-turret - a coaxial-input spherical parallel mechanism worn on the user: one seat, three stacked cranks

Lens: deployable structures and overconstrained / spherical linkage kinematics. Model:
`docs/concepts/models/coaxial-rus-turret.py`. It is the base 3-RUS model (`human-closed-crank-rods.py`) with five
explicit source patches; the loader asserts that each patch matches exactly once. The bench hooks, frozen wear and
red team come from `foldfree-rus-truss.py`. Sweep: `docs/concepts/sweeps/coaxial-rus-turret.json`.

## Depth answers (before modelling)

1. **What a top practitioner of this field would do here.** The parallel-kinematics answer to "the best seat for a
   crank axis is one place" is the coaxial-input spherical parallel mechanism (coaxial SPM; e.g. the Agile-Wrist
   family): all three input bearings sit on one common axis through the centre of rotation, and each leg has its own
   distal arc to the platform. On the user, the arm is the platform and the user's glenohumeral joint is the SPM's
   centre. Pairing it with the leg-fold theorem (docs/concepts/foldfree-rus-truss.md) gives this design.

   **The leg-fold theorem.** Each RUS leg is a spherical RRR with its own band:
   angle(c, Q_k) in [|beta_k - gamma_k|, beta_k + gamma_k].

   **Why one seat works.** ends.json shows that one crank axis is fold-free with MANY arm-stud directions. The axis is
   posterior-horizontal, bvec(-30, 8). Its hub band is 1.00, and its fold-free partners include wdir 45-75 / -90 and
   wdir 35 / -30..-42 among the 292 fold-free + in-band pairs. So all three legs can sit on that one axis, each with
   its own fold-free stud. What this buys over three separate hubs:
   - no base brackets;
   - one hub footprint on the quietest scapula skin;
   - for MVP2, three motors on one axis at one place, with one cable bundle;
   - an unlimited common rotation (a coaxial SPM can spin about its common axis).

   The new failure modes are the crank stack and the parallel singularity. A top designer prices both honestly. The
   stack: each crank gets its own bearing layer, and its whole profile is layered over the crank below it. The
   singularity is measured: the 3 x 3 moment-line determinant must stay >= 0.10.

   **Mobility.** On the bench, with GH fixed, the count is 3 x (R 1 + U 2 + S 3) + GH 3 - 3 x 6 = 3. The rod spins
   are killed by the U pitch pins, and the 3 crank angles are the only coordinates. There are 0 passive translations.
   Every joint is a catalogue part:
   - an O20 hub shaft with three bearing layers (3 mm Ti plate + 1.5 mm shoulder / iglidur thrust washer = 4.5 mm per
     layer, stack 21.25 mm);
   - O12 U-joint housings;
   - O12 rod ends on studs;
   - O5 Ti rods;
   - a 14 x 4 arm saddle.
2. **Rawest material.** The same inputs as foldfree-rus-truss:
   - the posed skin's signed distance per metal sample (fast grid for the screen, libigl exact for the claim);
   - the 10 fps fit clips for leg-branch continuity;
   - the fold-free pair scan docs/research/fold/ends.json.
3. **The instrument.** Closed-form RUS inverse kinematics per leg, the rod length by interval stabbing (each leg's band
   placed by construction), the moment-line determinant for the parallel singularity, K3 sphere tracing for every
   underside, and 1 mm point-cloud part clearance with the crank layering. The coarse sweep and CMA-ES run on the farm.
4. **The outside judge.** tools/concept_bench.py, on the same poses, metrics and contact rule as every row. The frozen
   shape is worn on Bench(110,360) exact, with near-touch < 1 mm counted as contact and the overhead split reported.
   The verifier re-measures next.

## Measured (Bench(60,160) fast, every model check on, full model): killed

`docs/concepts/sweeps/coaxial-rus-turret.json`. The seat's fold-free studs come from docs/research/rus/leg_bands.json.
For bvec(-24..-30, 4..8) they all sit on the posterior humeral head: s 0-20 mm, theta 90-150 deg.

| config | seat / studs / betas / branch | p | kin-valid | det ok ws | gap | reach | contact | why |
|---|---|---|---|---|---|---|---|---|
| informed-1 | (-30,8) / (10,120) (10,150) (20,105) / 70 65 60 / +1 | 100 | 0.38 | 0.50 | 320.51 | 0.006 | 0.57 | the parallel singularity on half the workspace (the studs cluster); every crank at the march ceiling (r_T 230-239); crank 0 / crank 1 collide in 69 poses |
| informed-2 | (-24,4) / (10,90) (10,150) (0,105) / 70 65 60 / -1 | 100 | 0.64 | 0.79 | 358.13 | 0.019 | 0.85 | cranks at the ceiling again (r_T 230-239); stacked cranks collide (crank 0/1 67, crank 1/2 29) |
| informed-3 | same, 90th-percentile fit | 90 | 0.68 | 0.81 | 275.0 (0 taken) | 0 | 0 | on the -1 branch each rod folds back over its own crank (crank 0 / rod 0 in 145 poses) |
| red-team ceiling | informed-3 with every part-part collision switched OFF | 90 | 0.68 | 0.81 | 280.01 | 0.30 | 0.61 | the optimistic bound (free routing): follow 0.18, in-band 14 0.07; crank 1 / 2 still at the 220 mm march ceiling (r_T 230 / 234.5) |

In the model, each leg alone is valid (closure + 15 deg transmission) on 0.93-0.98 of the workspace, so the fold
lever works per leg. The turret fails on everything else.

**Killed after the coarse screen.** The idea's premise was "one best seat, three fold-free legs". It contradicts
itself:
- a single crank axis is fold-free only with studs clustered on one patch of the arm, so the three moment lines
  T_k x Q_k are nearly coplanar and the turret is parallel-singular on 19-50 % of the workspace;
- each 60-70 deg crank still sweeps under the arm (crank-parking mid-span need p90 105-130 mm, against a seat skin
  radius of 93-102 mm);
- on the branch that keeps the cranks out of the trunk, the rods fold back over their own cranks.

Coaxial SPMs work in robotics because their platform is a rigid body with spread attachment points. On the user's
arm, the fold-free attachment points are not spread.

A farm coarse sweep (200 random seat / stud / branch configurations) was queued and cancelled: the farm queue stood at
107 jobs with 20 running, and the informed configurations above had already shown that the failure is structural.
The CMA streams were cancelled before they started. The convergence gate is not applicable (killed after the coarse
screen).

## Red team

* **Jam pose.** The parallel singularity (det < 0.10) covers 19-50 % of the workspace. There the three rods cannot
  resist one moment direction about GH: the unpowered turret is loose in that direction and MVP2 loses torque in it.
  Leg dead centres (transmission < 15 deg) sit at each leg's band floor and ceiling.
* **Pinch point.** On the trunk-free branch each rod passes back over its own crank (145 poses), and the stacked
  cranks shear past each other at 4.5 mm layer spacing (crank 0/1 collisions in 67-69 poses at p 100). Both would be
  finger traps on a real build.
* **The optimistic numbers.** The collision-off ceiling (280.01) is the most favourable reading, and the honest gap
  is worse. The 4.5 mm layer is a minimum: thin-section bearings stack 4-5 mm each, so a real stack is taller.
