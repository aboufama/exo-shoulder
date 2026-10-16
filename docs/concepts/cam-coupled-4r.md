# cam-coupled-4r: a 4R whose spare is set by a roller in a scapula-fixed slot

Model: `docs/concepts/models/cam-coupled-4r.py`. Sweeps: `docs/concepts/sweeps/cam-coupled-4r.json`.
Row: `docs/concepts/rows/cam-coupled-4r.json`.

## Deeper version (answered before modelling)

1. **What a top mechanism designer would do that the spec does not ask for.**
   - Read the slot as what it really is. The pin is fixed in link 2, so its position depends on q1 and q2 only. The
     slot is therefore a law q2 = f(q1), and J3's axis runs along ONE scapula-fixed curve C (a cam-generated coupler
     curve). Followed through, the mechanism becomes "J3 on a curve C, then a 2R (J3, J4) to the arm".
   - Its fold window is the a3-band around C. A circle C gives the 3R's 2 min(a1, a2) window. A non-circular C can
     only shift the window per azimuth about J1.
   - The test before any metal is kinematic: does the a3-band around some C cover the workspace's J4 directions? This
     model measures it as the root share.
   - Model the circuit, not a branch. The 4-bar (J1, J2, J3, J4) crosses between the two J3-dyad branches at its dead
     points, where J1 reverses. That is not a singularity of the actuated map (J1 with J2 slaved, J3, J4). So the
     solver takes roots on both branches. The singular set is checked directly: the slaved J1 axis
     u1 + f'(q1) p2 against the plane of J3 and J4.
   - Seed the slot from the dwell. Fit a small circle by least squares to the pin positions of park4's dwell
     configuration (link 3 humerus-fixed). Then search offsets around that fit, so that every candidate slot passes
     near the configurations the free 4R preferred.
2. **The rawest material.** The posed skin itself, through the bench's signed-distance grid: every part sample is
   marched along its ray (K3), with crowns and walls checked on the hubs. The 6 fit motion clips at 10 fps are walked
   densely (K2, 2 deg slerp steps). The 160 / 360 workspace poses are used as sampled. Held-out clips are never loaded.
3. **Methods and tools.**
   - tools/concept_kit.py (K1-K7, K6 collisions with `over`, dense continuity, the honesty audit).
   - spine-parked-j2-3r.py's crown / wall check, near-touch and overhead split (lessons d, e).
   - A vectorised 1 deg root scan over q1 on both J3-dyad branches, with 40 bisections.
   - A least-squares plane fit for the slot (eigen-decomposition of the pin cloud).
   - Farm sweeps (tools/cloud_run.py sweep), then CMA-ES (tools/concept_cma.py) on the farm until the convergence
     gate passes.
   - The frozen-shape protocol on Bench(110,360) exact.
4. **What shows the number is right, other than me.**
   - The bench: K3 march, K2 dense, K6, and the kit's audit, which flags sparse sampling, missing hubs and builds that
     are not pose-local.
   - The adversarial verifier on Bench(110,360) exact with the frozen shape.
   - A red-team pose list: rest, overhead (elev >= 140), across the body and behind the back, with per-part in-band and
     the cause of every lost pose (`redteam` mode).

## Mechanism (as modelled)

- **Chain.** Scapula handler -> base -> J1 (O20, ACTIVE) -> link 1 (arc a1) -> J2 (O20, PASSIVE, slot-scheduled)
  -> link 2 (arc a2) -> J3 (O20, ACTIVE) -> link 3 (arc a3) -> J4 (O20, ACTIVE, humerus-fixed) -> K7 neck -> BOTTOM.
- **Tail and slot.** Link 2 carries a tail strap from J2 to an MR63 (3 x 6 x 2.5) roller on an M3 shoulder pin, at
  angle tr from J2 and azimuth tp from link 2.
  - The roller runs in a spherical groove plate fixed to the base: a band 14 mm wide (6.1 mm slot plus two 4 mm
    walls), 4 mm thick, at ONE radius ('cap'), along the small circle {x . n = cos beta}.
  - The cut arc is the pin's travel over the poses that close, trimmed to percentiles [pct_lo, pct_hi], plus a
    6 mm pad at each end.
- **DOF.**
  - Mobility = 4 x 3 - 4 x 2 - 1 = 3.
  - ACTIVE: J1, J3, J4. PASSIVE: J2, the pin's slide, the roller's roll, all set by the closure.
  - Passive translations: 0. Springs: 0. Sensed passives: 0. The arm orientation is a function of the three active
    readings, because q2 = f(q1).
- **Taken-pose rules on top of the kit.**
  - A root exists on the design's mode (circuit slope s3 dg/dq1).
  - Cam transmission: pa = cos(pressure angle) >= 0.25, and the cross-slot pin travel is >= 8 mm per rad of J2.
  - The actuated map is >= 5 deg from singular.
  - The pin is inside the cut arc.
  - The root nearest the dwell configuration is taken. Dense K2 drops any clip frame where that choice switches roots.

## Results

(filled in below as the sweeps land)
