# sidecar-parallelogram-knuckle-3r

Round 8, pick 1. The sidecar parallelogram K drive: a lateral horn on link 1a, a bell crank on link 1b, and an O3 rod
on two M2 ball links beside link 1b at strap level. It sits on the verified lead's chain, which is unchanged
(frontload-lobe-stopb-knuckle-3r: J1 on the acromion top, link 1a, K knuckle, link 1b, J2, link 2, J3, pin knee + cuff).
Only the K drive is rebuilt, and nothing crosses K's crown.

Model: `docs/concepts/models/sidecar-parallelogram-knuckle-3r.py`. Sweep: `docs/concepts/sweeps/sidecar-parallelogram-knuckle-3r.json`.
Row: `docs/concepts/rows/sidecar-parallelogram-knuckle-3r.json`. Preview: `docs/concepts/viz/concepts/sidecar-parallelogram-knuckle-3r.js`.

## Deeper-version prompt (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Not model the drive twice. Pick 4 (sidecar-longdyad) already built this exact drive on the lead's module: the
     per-pose RSSR closure, the honest crank stack, and the drive-range truncation. It also carries pick 1's cell as its
     control D. Two hand-built copies of one four-bar would disagree on metal and nobody would know which is right. So
     this row imports that core and adds only what pick 1 owns:
     - the lead's K dyad held unchanged (bk1 30.05 / bk2 37.57 / a1max 61.72);
     - the far-socket clearance rule;
     - a real ball-link envelope, with the all-metal fallback measured as its own cell;
     - the idle-drive rule.
   - Read the pressure-angle cap before seeding. tan pa = kK r_h / (i_rock r_lobe), so the judge's seed (kK 2.0 at
     r_h 15 / La 18 / s_arm 5 / r_lobe 7.5) is infeasible at t = 0. At r_h 15.5 it is 1.15 > 1. The cap there is
     kK <= 1.74.
   - Price the ball link as a catalogue part, not a sketch.
     - The RC-class M2 ball link is a steel ball O4.8 on an M2 stud in an acetal socket ~O7 x 7.
     - The all-metal GE4E-class spherical plain bearing (4 x 12 x 5) in a 1.5 mm eye has a socket radius of 7.5. Its
       horn must then sit at r_h >= HUB_R + 7.5 + 2 = 19.5, or the eye cuts hub K.
     - That changes the drive's gain and its in-band height, so it is measured, not assumed.
2. **Rawest material.**
   - The posed skin itself: the bench's signed-distance grids per pose, via `tools/concept_bench.py`.
   - The model's own per-pose K state (dK), th, m3e and msub.
   - The per-part minimum metal-to-skin distance over the taken poses.
   - The motion clips are used only through the bench's fit-clip frames. The held-out clips stay held out until the
     claim.
3. **Methods and tools.**
   - Per-pose spatial RSSR closure (phi grid + continuation). The rod and crank are separate bodies, members 8 and 9.
   - The drive-range truncation: transmission >= 30 deg, rod / crank >= 1 mm off hub 2 and link 1b.
   - A coarse LHS of 128 drive geometries on the farm at the D seats, with kK set to 0.75-1.0 of the pressure cap.
   - CMA-ES on the near-touch gap (`tools/concept_cma.py`, farm): 3 runs with the RC ends from three seeds (D's,
     the judge's and A1's), plus 1 run with the GE4E ends.
   - The frozen wear on Bench(110,360) exact, held out, and the continuity flood fill.
4. **What, other than me, shows the number is right.**
   - The bench (Bench(60,160) fast for the search, Bench(110,360) exact for the frozen claim).
   - The round's adversarial verifier, which re-runs the frozen claim.
   - A same-harness replication. Through this wrapper, pick 4's control D re-evaluates to 10.63 fast, identical to
     pick 4's own number.
   - A red-team pose list: the overhead poses, the poses with metal under 1 mm, and the drive-range end.
