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
