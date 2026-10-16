# Shoulder exo chain: kinematic requirements (design "zc-frontier-3r")

Design the parts of this chain however you like. This brief gives only what the motion and the fit require. The
attached data files are listed at the end.

## 1. What it is

- A passive, unpowered chain on a **right shoulder** that follows the upper arm. It is a proof of concept: no motors,
  springs or cables.
- **Order:** base (held by the owner's scapula holder) -> J1 -> link 1 -> J2 -> link 2 -> J3 -> arm end. The arm end is
  rigidly fixed to "BOTTOM", the owner's plate on the upper arm, which is not part of this design.
- **Joints:** three revolute joints. **Their axes all pass through one point, GH, the centre of the shoulder joint**, so
  every part rotates about GH.
- The chain must ride close to the skin (2-14 mm, aim 10) and never touch it. The keep-out data in section 5 already
  encodes this.

## 2. Frame

- **Origin:** GH.
- **Axes:** +x anterior (forward), +y superior (up), +z lateral (to the right, away from the body). Right-handed.
- **Units:** mm, degrees.
- **Rest pose:** arm hanging at the side. All coordinates are at rest, with the base fixed in this frame.
- **Joint rotation:** right-hand rule about the axis units below; dtheta is measured from rest.
- **Forward kinematics** (all rotations about axes through GH, using the REST axis units):
  - R1 = Rot(J1, dtheta1) moves link 1;
  - R2 = R1 · Rot(J2, dtheta2) moves link 2;
  - R3 = R2 · Rot(J3, dtheta3) moves the arm end and BOTTOM.

## 3. Joints (fixed - do not change)

| joint | connects | axis unit at rest (x, y, z) | joint envelope along the axis |
|---|---|---|---|
| J1 | base -> link 1 | (0.135128, 0.913119, 0.384648) | 51.00 - 63.25 mm from GH |
| J2 | link 1 -> link 2 | (-0.482378, 0.824063, 0.297037) | 58.37 - 70.62 mm from GH |
| J3 | link 2 -> arm end | (-0.278089, -0.074243, 0.957682) | 71.00 - 83.25 mm from GH |

- **Fixed angles between axes:**
  - J1-J2 is **36.7226°** (set by link 1);
  - J2-J3 is **69.0575°** (set by link 2).
- **Joint envelope:** each joint's hardware (bearings, pins, caps) must fit inside a **Ø20 mm cylinder** coaxial with
  its axis, spanning the distances above. Nothing at a joint may come closer to GH than the start of its range
  (51.00 / 58.37 / 71.00).

## 4. Motion the chain must allow

| joint | required travel, dtheta from rest (deg) | limit |
|---|---|---|
| J1 | -127.5 to +120.3 | free (no stop needed) |
| J2 | -55.6 to +59.0 | **needs hard stops**, see below |
| J3 | -100.6 to +110.9 | free (no stop needed) |

- **J2 stops.** Let th be the angle between the J1 and J3 axes. It depends only on J2:
  - cos th = cos 36.7226 · cos 69.0575 + sin 36.7226 · sin 69.0575 · cos(theta2), with theta2 = dtheta2 - 92.41.
  - At rest, th = 74.75°.
  - th must stay within **37.33° to 100.78°**, 5° from the two singular (folded and straight) positions.
- **Where to put the stops.**
  - **Straight side:** at dtheta2 = -55.58° (th = 100.78°, exactly the 5° limit). The required travel reaches -55.57°.
  - **Folded side:** at dtheta2 = **+62.4° (th = 39.6°)**, not earlier than +59.0°.
  - Why the folded side needs care: at dtheta2 = +68° (th = 37.3), link 2 passes **0.26 mm** from J1's envelope
    cylinder. At +62.4° that clearance is 3.4 mm.
- **No collisions:** parts must not collide with each other anywhere in the travel above.

## 5. Where the parts may go (skin keep-out)

- **Link 1 and link 2** each run in the plane through GH that contains their two joint axes.
- In that plane, a point is (r, phi): r is the distance from GH, phi the angle from the link's first axis (J1 for link 1,
  J2 for link 2).
- **Hard requirement:** no part of a link may come closer to GH than the keep-out radius r_min(phi) below. The full
  table is in `kinematics_data.json`, `link_keepout`.
- **Target:** hug the keep-out. The verified design's links are 3 mm thick and lie right on it. Every mm further out
  moves metal away from the 2-14 mm band.
- **Off the plane:** the keep-out holds within about ±4 mm of the link plane. Route the links along these planes; there
  is no clearance data elsewhere.

**Link 1** (J1 at phi 0 -> J2 at phi 36.72): r_min =

| phi (deg) | 0-11.7 | 13.4 | 15.0 | 16.7 | 18.4 | 20.0 | 21.7 | 23.4 | 25.0-36.7 |
|---|---|---|---|---|---|---|---|---|---|
| r_min (mm) | 54.15 | 50.69 | 49.00 | 50.00 | 50.37 | 51.00 | 51.44 | 54.91 | 58.37 |

**Link 2** (J2 at phi 0 -> J3 at phi 69.06): r_min =

| phi (deg) | 0-9.9 | 11.5-14.8 | 16.4 | 18.1 | 21.4 | 24.7 | 28.0 | 31.2 | 34.5 | 39.5 | 42.7 | 46.0 | 49.3 | 51.0-54.3 | 55.9 | 57.5-69.1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r_min (mm) | 61.52 | 62.37 | 58.91 | 58.37 | 59.37 | 60.00 | 61.00 | 61.37 | 62.00 | 63.00 | 64.00 | 64.37 | 65.37 | 66.00 | 67.54 | 71.00 |

**Link plane directions** (in each plane, x = along the first axis, y as given):

| link | plane x | plane y | plane normal |
|---|---|---|---|
| link 1 | (0.135128, 0.913119, 0.384648) | (-0.987870, 0.154132, -0.018854) | (-0.076502, -0.377435, 0.922871) |
| link 2 | (-0.482378, 0.824063, 0.297037) | (-0.113147, -0.394874, 0.911742) | (0.868625, 0.406195, 0.283719) |

## 6. Interfaces

### Base -> scapula holder

- The base is the only part fixed to the owner's scapula holder, and the holder reaches it **from outside, along +J1**.
- Put the attachment on the J1 axis, outboard of the joint (beyond 63.25 mm from GH).
- Link 1 sweeps all the way around J1, so the base may not have arms or tabs off the axis.

### Arm end -> BOTTOM

- The arm end is fixed rigidly to BOTTOM. It leaves J3 and lands on BOTTOM's top face.
- BOTTOM is a straight C-channel bar on the outer upper arm. Its frame at rest:

| item | value |
|---|---|
| origin B0 | (9.891, -75.988, 62.052) |
| b, along the bar toward the shoulder | (0.008593, 0.971921, 0.235149) |
| c, across the bar | (-0.991231, -0.022731, 0.130173) |
| n, outward, away from the arm | (0.131863, -0.234205, 0.963203) |

- **Top face** at n = +3.70, 30 mm wide (c = ±15).
- **Two M4 tapped bosses** along n, at b = +15.4, c = ±8.75. Use them for screws, or fuse the arm end to BOTTOM.
- **BOTTOM is cut** square at b = +20: nothing of BOTTOM exists beyond it, toward the shoulder.
- **Suggested landing:** on the top face around b +2 to +20, c ≈ 0. The verified arm end lands near (10.47, -66.90,
  68.03), 96 mm from GH.
- **Arm end keep-out (hard):** between J3 and BOTTOM, its underside may not come closer to GH than 74 mm at J3,
  rising to about 94 mm at the landing. The full grid is in `kinematics_data.json`, `link_keepout.arm_end`; it tilts across the width.
- **Arm end height (target):** stay close to that keep-out, and within about 10 mm above BOTTOM's top face.

## 7. Check poses (base fixed)

Use these to check that your assembly moves correctly. A joint's "outer centre" is the point on its axis 12.25 mm
outboard of its envelope start: 63.25 mm from GH for J1, 70.62 for J2, 83.25 for J3.

| pose | dtheta (J1, J2, J3) | th | J2 outer centre | J3 outer centre |
|---|---|---|---|---|
| rest | (0, 0, 0) | 74.75 | (-34.066, 58.195, 20.977) | (-23.151, -6.181, 79.727) |
| arm overhead | (-61.09, +28.57, +110.87) | 57.81 | (-9.691, 68.785, -12.725) | (-52.960, 33.255, 54.954) |
| across the body | (+100.02, -14.68, +35.65) | 82.97 | (11.725, 34.860, 60.287) | (78.145, -11.492, 26.303) |
| behind the back | (+18.36, +2.33, -54.32) | 73.40 | (-32.960, 52.844, 33.292) | (4.561, -9.422, 82.589) |

J1's outer centre never moves: (8.547, 57.755, 24.329).

## Data file

`kinematics_data.json`, in the same frame: joint axes and envelopes, required travel, J2 stop window, link keep-out
profiles (phi, r_min) and the arm end's 3-D keep-out grid, the BOTTOM interface, and the check poses.
`skeleton_views.png` (optional) shows the skeleton at rest.
