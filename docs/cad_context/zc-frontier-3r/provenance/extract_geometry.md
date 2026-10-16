# zc-frontier-3r: skeleton geometry export (notes for the writer)

Made by running the model on the verified configuration (no geometry derived by hand). Files in this folder:
`geometry.json` (everything below, machine-readable), `link_centrelines.csv` (strap centrelines, 1 mm spacing),
`skeleton_views.png` (three orthographic views at rest, no body), `scripts/fit_and_wear.py` + `scripts/export_geometry.py`.

## Which configuration, and does it reproduce?

- Params (the row's `best_params`): J1 seat bvec(az 109.3565, el 65.94), a1 36.7226, a2 69.0575, J3 seat wdir(wd 85.7423,
  wa -16.1921), sigma -1, inv2 0, inv3 1, q 0.978, end_extra 1.784. Fixed by the rules: O20 hubs (r 10, F to crown 12.25),
  fold margin 5 deg, 12 x 3 straps, 14 x 6 neck.
- Shape: the verifier protocol. Undersides fitted on Bench(60,160) fast, then frozen. The frozen profile's sha256 is
  `9576b98b979e304dcda0e78b0c3962e0c1bf9d5cc5afcda18958eb089ff4f35e`. Worn on Bench(110,360) EXACT in this run, it gives
  **gap 33.51** (reach 0.6167, follow 0.9364, in-band 14 0.8917, contact 0.0299, honest, audit empty, hub F 51.0 / 58.37 /
  71.0 mm). That matches the skeptic's verified 33.51 to the digit (365 s on this box). The exported metal is this frozen shape.
- The 31.04 claim uses a fit on Bench(110,360). That fast grid exists only on the farm, so that shape was not exported here.
  The two shapes have the same hub levels (F 51.0 / 58.37 / 71.0). They differ only in the strap undersides.

## Frame (one frame for every number)

The model's thorax frame at the rest pose: **origin GH (right glenohumeral centre), +x anterior, +y superior, +z lateral
(right)**, mm. It is right-handed (x cross y = z).

Rest pose = arm hanging: plane 0, elevation 0, axial rotation 0. The elbow angle does not affect the chain.

"As built" means the base (scapula) is held at its rest attitude. The key poses are given relative to the base, as a CAD
assembly would hold it. The base attitude at rest (scapula frame -> as-built) is in `frame.base_attitude_at_rest_RS`.

## The numbers that matter (all in geometry.json)

| joint | axis unit at rest (x, y, z) | F (mm, GH -> lower plate skin face) | lower plate (F .. F+3) | cap side (from F+3.15, crown F+12.25) |
|---|---|---|---|---|
| J1 | (0.135128, 0.913119, 0.384648) | 51.00 | base (scapula-handler side) | link 1 |
| J2 | (-0.482378, 0.824063, 0.297037) | 58.37 | link 1 | link 2 |
| J3 | (-0.278089, -0.074243, 0.957682) | 71.00 | link 2 | member 3 (arm-end plate + neck) - inv3 = 1 |

- **Hub:** each hub is a solid O20 disc on its axis, from F (the lower plate's skin face) outward to F + 12.25 (crown).
  The cap side always faces away from GH. Inside the stack: lower plate F..F+3, upper member's underside F+3.15, two
  MR117-2RS, crown 12.25. The hub centre is F x the axis unit.
- **inv3 = 1, concretely:** at J3, link 2 is the skin-side plate (F 71.0 .. 74.0). The arm-end plate + neck sits on the
  cap side, from 74.15 up. It must bridge over link 2 with at least 1 mm between them. At J2 the order is normal: link 1
  is below, link 2 above.
- **Links:** each link is a strap on the great circle between two axes, centred on GH. link 1 runs J1 -> J2 over a1 =
  36.72 deg. link 2 runs J2 -> J3 over a2 = 69.06 deg.
  - Section: 12 wide x 3 thick, thickness radially outward.
  - The underside is NOT one level. Every 2 mm sample has its own radius from GH (fitted, then frozen): link 1 49.0-58.37,
    link 2 58.0-71.0.
  - Each strap starts and ends ON the joint axes. Each end is held at the hub's F (lower member) or F + 3.15 (upper member)
    over 8 samples (11.5-11.7 deg).
  - The full sample grid (along x across) is in `links.*.model_sample_grid_underside`. The centreline (centre column,
    densified to <= 1 mm) is in the CSV.
  - sigma = -1 is the closure branch: the sign of J2 . (J1 x J3).
- **Member 3:** the hub-3 cap plate plus the neck, a 14 x 6 strap from the J3 axis to the direction of BOTTOM's bar
  start point. It is rigid with BOTTOM and the upper arm. Its underside is 72.4-101 mm from GH.
  - The model ends the neck on that direction at underside radius 88-101 mm. That is 15.5 mm further out than the K7 bar
    start point (78.47 mm from GH; H frame: 67.5 mm along WB (0, -0.0713, 0.9975) + 40 mm along DB (0, -0.9975, -0.0713)).
  - So the CAD must drop the neck onto BOTTOM. The repo's L2 CAD fuses it into BOTTOM's channel (one 5-axis part, BOTTOM
    cut), or uses 2x / 4x M3 countersunk through the web. Elbow-referenced bar stations are left out on purpose: they
    encode the arm length.
- **Joint angles for CAD:** theta = distal body relative to proximal body, right-hand about the axis unit.
  theta1 = q1, theta2 = q2, theta3 = -q3 (the model's q3 measures link 2 as seen from the arm).
  - Rest: theta = (175.57, -92.41, 155.96).
  - Forward kinematics: R1 = Rot(J1, dtheta1), R2 = R1 Rot(J2, dtheta2), R3 = R2 Rot(J3, dtheta3).
- **Ranges over the taken poses:** 222 workspace poses + 103 clip frames on Bench(110,360), with the verifier's take.

  | joint | range (deg) | relative to rest (deg) |
  |---|---|---|
  | theta1 | 48.1 .. 295.9 | -127.5 .. +120.3 |
  | theta2 | -147.98 .. -33.40 | -55.6 .. +59.0 |
  | theta3 | 55.4 .. 266.8 | -100.6 .. +110.9 |

  Per clip, and all frames of the 6 fit clips (kinematic only), are in `joint_ranges`.
- **Fold rule (5 deg in th):** th is the J1-J3 angle. The window is th 37.33 .. 100.78. As J2 angles:
  - cos th = cos a1 cos a2 + sin a1 sin a2 cos theta2.
  - J2 hard stops (a dowel in an arc slot between link 1 and link 2) at **theta2 = -24.39 (folded) and -147.99 (stretched)**.
  - Taken th is 41.17 .. 100.78. The minimum margin on the taken poses is 5.002 deg.
- **Swept clearance (red flag for the CAD):** near the folded stop, link 2 swings past hub 1.
  - At the folded stop the clearance is 0.26 mm. The 1 mm part-part rule holds only from theta2 <= -25.69 (th >= 37.84).
  - At the smallest taken th (41.17, theta2 -33.40) it is 5.42 mm.
  - So place the folded stop at theta2 <= -25.7, or relieve hub 1 / link 2 there.
  - The other minima over the whole window are all well clear: hub 3 to hub 1 25.1 mm, member 3 to hub 1 18.0 mm,
    link 1 to hub 3 32.6 mm.
- **Key poses** (theta, hub face and crown centres as built, axes): overhead (workspace plane 30 / elevation 165 / axial
  -60), across the body (plane 150 / elevation 60 / axial -60), behind the back (Reach back pocket, plane -80 /
  elevation 39 / axial 101). See `key_poses`.

## Self-checks (geometry.json `checks`, all pass)

- The three axes meet at GH: least-squares meet point 2.8e-10 mm from GH. Exported hub centres lie <= 9e-9 mm off their
  axis lines through GH.
- The strap centrelines start and end on the hub axes (<= 5e-5 mm off). Their levels equal F + dz (54.15 / 58.37 / 61.52
  / 71.0 / 74.15).
- The exported rest metal, moved by the FK above, matches the model's own sampled metal at the 3 key poses to **0.00019
  mm** (straps), with hub centres <= 8e-5 mm and axes <= 3e-8.

Privacy: no skin, scan or body data is exported. The clearance rules are given as numbers on the design's own geometry.

Rerun:
`python3 docs/cad_context/zc-frontier-3r/scripts/fit_and_wear.py DIR` (about 6 min), then
`python3 docs/cad_context/zc-frontier-3r/scripts/export_geometry.py DIR`.
