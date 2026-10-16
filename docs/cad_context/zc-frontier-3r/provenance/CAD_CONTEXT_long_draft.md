# CAD brief: zero-complexity 3R shoulder chain (design "zc-frontier-3r")

Attached data (same folder): `geometry.json` (all numbers below, machine-readable), `link_sketch_profiles.csv` (link
side-view profiles in their sketch planes), `link_centrelines.csv` (3-D strap centrelines, 1 mm spacing),
`derived.json` (sketch planes, clearances, BOTTOM frame), `skeleton_views.png` (three views of the skeleton at rest).
Everything is in mm and degrees, in ONE right-handed frame (section 2). You need nothing else.

---------------------------------------------------------------------------------------------------------------------

## 1. What this is

- A passive (unpowered) exoskeleton chain for a **right shoulder**. It is a kinematic proof of concept: it follows the
  arm on ball bearings; the owner adds rotation sensors later. No motors, gears, cables or springs.
- Three hinges J1, J2, J3 in series. **All three axes meet at one point, GH** (the centre of the shoulder joint), so
  the chain is a spherical mechanism: every part turns about GH.
- J1 sits on a base that the owner's scapula holder carries. J3's distal part ("member 3") is rigid with a plate on the
  upper arm (the owner's part "BOTTOM", not designed here).
- Every part must ride 2-14 mm off the skin (aim 10) and never touch it. **The skeleton below already guarantees
  that.** It was optimised and independently verified. Your CAD must keep to it: same axes, same hub levels, link
  undersides never closer to GH than the given profiles.

## 2. Frame, units, rest pose, data files

**Frame (every number in this brief):**

| item | definition |
|---|---|
| origin | GH, the centre of the right shoulder joint |
| +x | anterior (forward) |
| +y | superior (up) |
| +z | lateral, to the right (away from the body's midline) |
| handedness | right-handed, x cross y = z |
| units | mm, degrees |

- **Rest pose:** arm hanging at the side. Model the parts and the assembly here. The base never moves in this frame.
- **Joint angle theta:** rotation of the distal body relative to the proximal body, right-hand rule about the axis
  unit given in section 3. Rest: theta = (175.57, -92.41, 155.96). Angles are modulo 360; use **dtheta from rest**.
- **Forward kinematics (base fixed):** R1 = Rot(J1, dtheta1); R2 = R1 Rot(J2, dtheta2); R3 = R2 Rot(J3, dtheta3),
  with Rot = right-hand rotation about the REST axis unit through GH. Link 1 moves by R1; link 2, hub 2's upper parts
  and hub 3's lower parts by R2; member 3 (and BOTTOM, and the arm) by R3. This reproduces the key poses of section 3.6
  to 0.0001 mm.

**geometry.json, the keys you need:**

| key | content |
|---|---|
| `hubs.J1/J2/J3` | `axis_unit_rest`, `F_mm`, `face_centre_F`, `crown_centre`, which member is lower / upper |
| `hubs.hub_stack` | the hub envelope (O20, F to F+12.25) |
| `links.link1 / link2 / neck` | `model_sample_grid_underside`: the clearance surface (underside) as a grid of points, row-major (along outer, across inner); `section_width_x_thickness_mm`; `end_holds`; `hub_rim_crossings` |
| `fold` | fold window and J2 stop angles |
| `joint_ranges` | the joint ranges actually used (verified poses) |
| `key_poses` | theta, axes, hub face and crown centres at rest and 3 extreme poses |
| `bottom_interface` | where member 3 meets BOTTOM |
| `swept_clearances` | part-to-part clearances over the J2 window |

## 3. The kinematic skeleton (do not change)

### 3.1 Axes and hub levels

F = distance from GH, along the axis, to the skin-side face of the joint's lower plate. The hub's outward side (crown)
always faces away from GH.

| joint | axis unit at rest (x, y, z) | F | face centre at F (x, y, z) | crown centre at F + 12.25 (x, y, z) |
|---|---|---|---|---|
| J1 | (0.135128, 0.913119, 0.384648) | 51.00 | (6.892, 46.569, 19.617) | (8.547, 57.755, 24.329) |
| J2 | (-0.482378, 0.824063, 0.297037) | 58.37 | (-28.156, 48.101, 17.338) | (-34.066, 58.195, 20.977) |
| J3 | (-0.278089, -0.074243, 0.957682) | 71.00 | (-19.744, -5.271, 67.995) | (-23.151, -6.181, 79.727) |

- Fixed angles between axes: J1-J2 = **36.7226 deg** (link 1's arc), J2-J3 = **69.0575 deg** (link 2's arc).
- J3 to BOTTOM's landing direction (0.10906, -0.69697, 0.70876) = **45.5586 deg** (member 3's neck arc).

### 3.2 Stack order (which member is the lower plate)

| joint | lower member (skin side, plate F..F+3, carries the pin) | upper member (plate F+3.15..F+6.15, carries bearing bore + cap) |
|---|---|---|
| J1 | **link 1** | **base** (the scapula holder threads onto it) |
| J2 | link 1 | link 2 |
| J3 | link 2 | **member 3** (J3 upper plate + neck to BOTTOM) |

Note on J1: the kinematic model had link 1 on the upper level at J1. This brief uses the CAD standard instead (base on
top, so the holder can thread on from outside without crossing link 1's sweep). The only effect is that link 1's pad
sits 3.15 mm lower within 14 mm of the J1 axis. The hub disc already occupies that level, and the clearance surface
just beyond the pad (13.4-15.0 deg from J1) is at 50.7-49.0 mm, below the pad (52.4-52.8 mm). Treat it as expected
clear, and check it (section 7).

### 3.3 Link sketch planes

Each link lies in the plane through GH that contains its two axes. In each plane use 2-D coordinates: origin GH, x
along the start axis, y as given. A point at angle phi from the start axis and radius r from GH is
(r cos phi, r sin phi). The end axis is at phi = arc.

| member | start axis | plane x direction | plane y direction | plane normal | arc (deg) |
|---|---|---|---|---|---|
| link 1 | J1 | (0.135128, 0.913119, 0.384648) | (-0.987870, 0.154132, -0.018854) | (-0.076502, -0.377435, 0.922871) | 36.7226 |
| link 2 | J2 | (-0.482378, 0.824063, 0.297037) | (-0.113147, -0.394874, 0.911742) | (0.868625, 0.406195, 0.283719) | 69.0575 |
| neck (member 3) | J3 | (-0.278089, -0.074243, 0.957682) | (0.425471, -0.903389, 0.053514) | (0.861186, 0.422347, 0.282811) | 45.5586 |

### 3.4 Link underside profiles (the clearance surface)

The underside radius r(phi) is the **lowest the metal may go**. The full per-sample data is in
`link_sketch_profiles.csv` (r_underside, r_top, sketch x/y). Breakpoints:

**Link 1** (J1 -> J2), r in mm:

| phi | 0 - 11.7 | 13.4 | 15.0 | 16.7 | 18.4 | 20.0 | 21.7 | 23.4 | 25.0 - 36.7 |
|---|---|---|---|---|---|---|---|---|---|
| r | pad (sec. 4.3) | 50.69 | 49.00 | 50.00 | 50.37 | 51.00 | 51.44 | 54.91 | 58.37 (J2 lower pad) |

**Link 2** (J2 -> J3):

| phi | 0 - 9.9 | 11.5 - 14.8 | 16.4 | 18.1 | 21.4 | 24.7 | 28.0 | 31.2 | 34.5 | 39.5 | 42.7 | 46.0 | 49.3 | 51.0 - 54.3 | 55.9 | 57.5 - 69.1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r | 61.52 (J2 upper plate) | 62.37 | 58.91 | 58.37 | 59.37 | 60.00 | 61.00 | 61.37 | 62.00 | 63.00 | 64.00 | 64.37 | 65.37 | 66.00 | 67.54 | 71.00 (J3 lower pad) |

**Neck** (J3 -> BOTTOM), centre of the width:

| phi | 0 - 10.1 | 13.5 | 16.9 | 20.2 | 25.3 | 30.4 | 33.7 | 37.1 | 40.5 | 43.9 | 45.6 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| r | 74.15 (J3 upper plate) | 75.0 | 76.5 | 78.5 | 80.5 | 83.5 | 85.5 | 88.0 | 90.7 | 93.0 | 94.0 |

- The neck's clearance surface **tilts across its width**. It is flat at the root and rises toward the minus-normal
  side further out: 6.6 mm across 17 mm at phi 23.6, and 13 mm across 23 mm at the end. The across values are in
  `geometry.json` `links.neck.model_sample_grid_underside`, 8 points per row.
- In the model, the strap width is angular (12 mm at 70 mm from GH), so its true width is 8.7-10.0 mm on link 1 and
  10.5-12.2 mm on link 2. **An 8 mm wide bar fits inside it everywhere**; a 12 mm bar does not fit on link 1.

### 3.5 Joint ranges and stops

| joint | range used by the verified motions (dtheta from rest, deg) | stop |
|---|---|---|
| J1 | -127.5 .. +120.3 | none (free) |
| J2 | -55.6 .. +59.0 (theta2 -147.98 .. -33.40) | **hard stops at theta2 = -30.0 (folded side) and -147.9 (stretched side)** |
| J3 | -100.6 .. +110.9 | none (free) |

- The **fold rule**: the angle th between the J1 and J3 axes must stay in 37.33 .. 100.78 deg (5 deg from both
  singular folds). It depends only on J2: cos th = cos 36.7226 cos 69.0575 + sin 36.7226 sin 69.0575 cos theta2.
- The model's own stop was at theta2 = -24.39. There, link 2 passes **0.26 mm** from hub 1. It reaches 1 mm only at
  theta2 = -25.9 and 3.4 mm at -30.0. So this brief sets the folded stop at **-30.0** (th 39.64). No verified pose needs
  theta2 beyond -33.40, so this costs nothing.
- The stretched stop at -147.9 (th 100.75) keeps the 5 deg rule. It must not engage beyond -147.99.
- **Stop hardware:** one O2 m6 x 4 hardened dowel, pressed 2.6 mm into link 1's J2 pad top face, at 7.5 mm from the J2
  axis. It runs in an arc slot milled 1.5 mm deep into the underside of link 2's J2 plate: width 2.1, centre radius
  7.5, round ends.
  - Put the dowel at any angle psi_d about the J2 axis (as built at rest, measured in the J2 seat plane). The slot's
    dowel-centre path in link 2 then runs from psi_d - 62.41 deg (folded stop) to psi_d + 55.49 deg (stretched stop),
    right-hand about the J2 axis unit.
  - The slot stays inside r 6.45-8.55, so it clears the O11 bearing bore (r 5.5) and the O20 rim.

### 3.6 Key poses for an assembly motion check (base fixed)

| pose | dtheta from rest (deg) | th | J2 crown centre | J3 crown centre |
|---|---|---|---|---|
| rest | (0, 0, 0) | 74.75 | (-34.066, 58.195, 20.977) | (-23.151, -6.181, 79.727) |
| overhead (arm raised 165 deg) | (-61.09, +28.57, +110.87) | 57.81 | (-9.691, 68.785, -12.725) | (-52.960, 33.255, 54.954) |
| across the body | (+100.02, -14.68, +35.65) | 82.97 | (11.725, 34.860, 60.287) | (78.145, -11.492, 26.303) |
| behind the back | (+18.36, +2.33, -54.32) | 73.40 | (-32.960, 52.844, 33.292) | (4.561, -9.422, 82.589) |

J1's crown never moves: (8.547, 57.755, 24.329). The axes at each pose are in `key_poses` in the JSON.

## 4. Parts to design

### 4.1 The hub stack (the same at every joint)

Each hub is a preloaded back-to-back pair of **MR117-2RS** ball bearings (7 x 11 x 3), inside an O20 envelope from F
to F + 12.25. Below, z is measured along the axis from F (the skin face of the lower plate), outward.

| z | level |
|---|---|
| 0 - 3.00 | lower plate (lower member) |
| 3.15 - 6.15 | upper plate (upper member); 0.15 running gap |
| 3.15 - 3.65 | 0.5 lip in the upper member, bore O9.8; the pin collar O8.2 rises to 3.65 |
| 3.65 - 6.65 | bearing 1 |
| 6.65 - 7.25 | outer spacer (O11 x O9.8) and inner spacer (O8.2 x O7), both 0.6 |
| 7.25 - 10.25 | bearing 2 |
| 6.15 - 8.75 | O20 ring (upper member), R0.5 outer top edge |
| 8.75 - 10.22 | O18 spigot, M18x0.5 external thread, R0.3 top edge (0.03 below the cap flange) |
| 10.25 - 11.15 | ring nut on the pin |
| 8.80 - 12.25 | cap (skirt O20 from 8.80, crown apex 12.25) |

Absolute levels from GH:

| joint | lower plate | upper plate | ring top | cap flange | crown |
|---|---|---|---|---|---|
| J1 | 51.00-54.00 | 54.15-57.15 | 59.75 | 61.25 | 63.25 |
| J2 | 58.37-61.37 | 61.52-64.52 | 67.12 | 68.62 | 70.62 |
| J3 | 71.00-74.00 | 74.15-77.15 | 79.75 | 81.25 | 83.25 |

**Lower member features** (they belong to the link that is the lower member):
- An integral O7 pin, turned in one piece with the plate.
- Profile (radius, z): collar r 4.1 from z 1.5 (embedded 1.5 in the plate) to 3.65, then pin r 3.5 to 11.15.
- DIN 509 relief at the collar root, and an M7x0.5 thread at the top (z 10.25-11.15 at least).

**Upper member features:**
- The O20 ring, the O18 spigot and the bore.
- Bore: O9.8 lip from 3.15 to 3.65, then O11 (11 H7) from 3.65 through the spigot top.

**Loose parts:**

| part | geometry | material |
|---|---|---|
| ring nut | M7x0.5, O8.6 x 0.9, two O0.8 pin-spanner holes; bears on bearing 2's inner ring only | Ti-6Al-4V |
| outer spacer | O11 x O9.8 x 0.6, ground at assembly to stand 0.02-0.04 proud of the spigot top | 17-4PH |
| inner spacer | O8.2 x O7 x 0.6, then lapped about 0.005 shorter (this sets the preload) | 17-4PH |

**Cap:** one revolved profile of lines and tangent arcs (r, z):

| step | segment |
|---|---|
| 1 | (9.0, 8.80) to (10.0, 8.80) |
| 2 | wall up to (10.0, 10.60) |
| 3 | R1 knuckle arc, centre (9.0, 10.60), to (9.144, 11.590) |
| 4 | crown arc R63.63, centre on the axis at z -51.38, to the apex (0, 12.25) |
| 5 | down the axis to (0, 11.75): 0.5 crown |
| 6 | pocket O9 x 1.5: (4.5, 11.75) to (4.5, 10.25) |
| 7 | flange face (4.5, 10.25) to (9.0, 10.25): bears on bearing 2's outer ring only |
| 8 | M18x0.5 internal thread down to (9.0, 8.80) |

- No holes and no drive features. It is tightened with a soft-jaw cup, Loctite 222.
- Keep the O9 x 1.5 pocket empty: the owner's rotation sensor goes there.

**Designed clearances:**
- collar to lip: 0.8 radial;
- nut to cap pocket: 0.2 radial, 0.6 axial;
- cap skirt to ring top: 0.05.

**Assembly:**
1. Into the upper member's bore: bearing 1, outer spacer, bearing 2.
2. Pin up through the inner rings with the inner spacer between them.
3. Ring nut.
4. Cap last.

**Known limits (fine for this unpowered version):**
- The cap engages the M18x0.5 spigot over only about 1.47 mm (3 pitches).
- MR117-2RS static rating is about 0.28 kN. Estimated load is about 0.1 kN per bearing.

### 4.2 Base (J1 upper member), part 01

- **Function:** carries J1's outer rings. The owner's scapula holder threads onto its spigot in place of a cap.
- **Geometry:**
  - plain O20 seat disc at 54.15-57.15 from GH on J1;
  - O20 ring to 59.75;
  - O18 M18x0.5 spigot to 61.22;
  - bore O9.8 / O11 as in 4.1.
- **Nothing else.** No tab and no ears: link 1 sweeps every heading around J1. It is rotationally symmetric, so its
  clocking about J1 is free.
- **Interface to the holder** (the owner's part; given so you keep it free):
  - The holder must reproduce the cap's functional faces: M18x0.5 internal thread over 59.80-61.25, a flange face at
    61.25 bearing on bearing 2's outer ring (annulus r 4.5-9), and a pocket of at least O9 x 1.5 over the nut (nut top
    62.15).
  - It comes in from outside along +J1. Nothing may sit below 59.80 outside r 10, and nothing may enter link 1's or
    link 2's sweep: link 2 passes 3.4 mm from the O20 cylinder of hub 1 at the folded stop.
- **Material:** Ti-6Al-4V, 5-axis machined, bead blasted.

### 4.3 Link 1, part 02 (J1 lower member + J2 lower member)

- **Pads:** a flat 3.0 plate at each hub, in the seat plane (normal = the joint axis). Planform: the O20 hub circle
  plus the bar, joined by tangent arcs (R6 for a bent bar, R2 for a machined bar). The pad runs out to 14 mm from the
  axis (bent) or 11 mm (machined).
  - J1 pad: 51.00-54.00 along J1.
  - J2 pad: 58.37-61.37 along J2.
- **Pins:** an integral O7 pin at each pad (4.1). The J2 pad also takes the stop dowel hole (3.5).
- **Bar:**
  - section **8 wide x 3 thick**;
  - centre plane = link 1's sketch plane (3.3);
  - underside at or above the link 1 profile (3.4).
  - It leaves each pad parallel to the seat, then ramps at no more than 60 deg.
  - Expect to bridge the 49.0 dip at phi 15.0: a fair curve rides about 1.3 mm above it there, which is allowed.
- **Finish:** a 1.0 deep pocket on the outer face (1.5 rims, starting 4 mm from each end, round ends, 0.4 rounds) is
  optional. Use 0.5 rounds on sharp edges, but none on the pads' seat faces.
- **Material:** Ti-6Al-4V, bead blasted.

### 4.4 Link 2, part 03 (J2 upper member + J3 lower member)

- **J2 end:** the upper plate at 61.52-64.52 along J2, the O20 ring to 67.12, the M18 spigot to 68.59, and the bore.
  The stop slot goes in the plate underside (3.5).
- **J3 end:** a lower pad at 71.00-74.00 along J3 with an integral O7 pin to 82.15.
- **Bar:** 8 x 3, in link 2's sketch plane, underside at or above the link 2 profile.
  - It passes over link 1 at J2. Outside the 14 mm seat zone the model keeps 2.65 mm or more over the whole J2 range.
  - It passes under member 3's neck at J3.
- **Material:** Ti-6Al-4V, bead blasted.

### 4.5 Member 3: J3 upper member + neck, part 04

- **J3 end:** the upper plate at 74.15-77.15 along J3, the O20 ring to 79.75, the spigot to 81.22, and the bore.
- **Neck:**
  - section up to **14 wide x 6 thick** (the verified envelope; thinner is fine);
  - centre plane = the neck sketch plane (3.3);
  - underside at or above the neck clearance surface at every grid point it covers, including the cross tilt (3.4).
- **Recommended construction:**
  - a flat plate in J3's seat plane leaving the pad;
  - **one bend** about the line where that plane meets BOTTOM's top-face plane (the two planes are **25.4 deg** apart);
  - a flat end lying on BOTTOM (4.6);
  - planform turns as needed.
- Within 14 mm of J3, keep the neck top at or below 79.75 if you can, so a cup tool can still grip the cap.
- **Clearances in the model:**
  - Over the J3 range, the neck stays 2.57 mm or more from link 2 outside the J3 seat zone.
  - Inside it, the stacked pads keep the 0.15 running gap.
- **Material:** 7075-T6 if fused with BOTTOM (the owner's standard, 4.6), else Ti-6Al-4V. Bead blasted.

### 4.6 Interface to BOTTOM (fixed geometry: mate to it, do not design it)

BOTTOM is a straight C-channel bar on the lateral upper arm. It moves with member 3. Its local frame, **as built at
rest**:

| item | value |
|---|---|
| origin B0 (centre plane, reference station) | (9.891, -75.988, 62.052) |
| b, along the bar toward the shoulder | (0.008593, 0.971921, 0.235149) |
| c, across the bar | (-0.991231, -0.022731, 0.130173) |
| n, away from the arm | (0.131863, -0.234205, 0.963203) |

Section in (c, n), constant along b. The channel opens toward the arm.

| face | position |
|---|---|
| top face | n = +3.70 |
| web underside (channel floor) | n = +1.70 |
| skin-side flange faces | n = -2.79 |
| outer sides | c = +-15.0 |
| inner channel walls | c = +-12.0 |

Bosses and the cut:
- A cross rib fills the channel at b = +13.4 .. +17.4.
- It carries two O7 bosses at b = +15.4, c = +-8.75, each with an M4 tapped hole (O3.3) along n.
- BOTTOM continues toward the elbow (negative b). The owner's cuff screws are more than 100 mm away.
- **Cut BOTTOM square to b at b = +20.0**, keeping b <= +20.
- Over every joint range, BOTTOM's envelope up to b = +20 stays 26 mm or more from every other chain part.

Where the neck lands:
- The model's neck-end ray (direction (0.10906, -0.69697, 0.70876) from GH) crosses BOTTOM's top face at b = +10.25,
  c = 0, point (10.467, -66.895, 68.026), 96.0 mm from GH.
- It crosses the channel floor at b = +11.43 (93.7 mm) and the flange plane at b = +14.09 (88.4 mm).

**Joint rule (owner's standard): fused.**
- Member 3's neck ends as a lap on BOTTOM's top face, around b +2 .. +20 and c 0.
- It is **embedded 1.0 mm into BOTTOM** (underside at n = +2.70), never face-on-face.
- Keep |c| + half-width <= 14.6, and the lap top at n <= +7.2 (the model neck ends at b +11.3 with its underside at n +2.0 and its top at n +7.2).
- The owner unions it with the cut BOTTOM and makes one 5-axis 7075-T6 part.

**Fallback (separate Ti part), state which you used:**
- 2x M4 ISO 10642 countersunk screws, heads flush, through the lap into the existing M4 bosses at b +15.4, c +-8.75.
  This needs the lap 26 wide over b +11 .. +20. First check on the owner's STEP that those holes are through to the
  top face.
- Otherwise use 2x M3 ISO 10642 through BOTTOM's web into a tapped tongue in the channel at b < +13: O3.4 clearance,
  90 deg countersink O6.3 at n +3.70, holes at c +-6, 10 mm apart in b.

### 4.7 Bill of materials

| qty | item | type |
|---|---|---|
| 1 | P01 base (J1 upper member) | custom, Ti-6Al-4V |
| 1 | P02 link 1 (2 pads + 2 integral pins, dowel hole) | custom, Ti-6Al-4V |
| 1 | P03 link 2 (J2 ring + spigot + slot, J3 pad + pin) | custom, Ti-6Al-4V |
| 1 | P04 member 3 (J3 ring + spigot, neck, BOTTOM lap) | custom, 7075-T6 (fused) or Ti-6Al-4V |
| 3 | P05 cap (J2, J3, plus one for bench tests of J1) | custom, Ti-6Al-4V |
| 3 | P06 ring nut M7x0.5 | custom, Ti-6Al-4V |
| 3 | P07 outer spacer, 3x P08 inner spacer | custom, 17-4PH |
| 6 | MR117-2RS, 7 x 11 x 3, P5 recommended | catalogue |
| 1 | dowel ISO 8734, O2 m6 x 4 | catalogue, hardened steel |
| 0-2 | ISO 10642 M4 or M3 countersunk (fallback only) | catalogue, A2 stainless, polished |
| - | Loctite 222 (M18 and M7 threads) | - |

## 5. Rules

- **No lofts, ever. No splines, no twisted or variable-section sweeps, no surfaces fitted to point data.**
  - Use only sketches of lines and tangent arcs with set radii, then extrude, revolve, or sweep ONE constant section
    along a line/arc path.
  - Bends (an arc in the side view), planform turns and fillets are allowed.
  - Use the profile data as a target to fit lines and arcs to, never as a surface.
- **Bend radii:**
  - Bent 3 mm Ti bar: inner radius >= 15 mm (centreline >= 16.5).
  - Machined from solid (5-axis): centreline radius down to 3 mm (1.5 inner). State "machined" on the part.
  - Ramps: 60 deg or less near a hub.
- **One valid closed solid per part.**
  - Fused bodies overlap; they never touch face-on-face or tangentially. The pin collar is embedded 1.5 mm in its
    plate; the neck is embedded about 6 mm in its hub and 1 mm into BOTTOM.
  - Seats are exact planes. No rounds on a seat face, or on an upper plate's hub-circle top edge.
- **O20 hubs only**, the same stack at every joint. No smaller hubs.
- **Stacking:** a lower link thickens toward the skin, never up into the upper member. Stacked pads keep the 0.15
  running gap. Elsewhere, parts keep at least 1 mm apart over the whole motion.
- **Fits:**
  - bearing outer ring in 11 H7;
  - inner ring on 7 h5/js5 (recommended);
  - dowel O2 m6 in O2 H7;
  - threads modelled at major / minor diameter, no flanks.
- **Look:** smooth, constrained, accurate bodies. At most a screw or two, sunk flush; no visible screws on caps.
- **Materials and finish:**
  - Ti-6Al-4V and 7075-T6, bead blasted;
  - spacers 17-4PH;
  - screws A2 polished;
  - any polymer part iglidur orange;
  - **no black parts.**
- Drawings, if any, carry only threads and tight tolerances.

## 6. Deliverables

- One STEP per part, in the frame of section 2, **at the rest pose**. File names `ZCF3R-P01_base.step` ...
  `ZCF3R-P08_inner_spacer.step`. Catalogue parts as simple envelopes, named `ZCF3R-C01_MR117-2RS.step` and so on.
- `ZCF3R-ASM_rest.step`: the full assembly at rest, every part in place (2 bearings per hub, spacers, nuts, caps,
  dowel).
- The same assembly at the three key poses (3.6), as `ZCF3R-ASM_overhead.step`, `..._across.step` and
  `..._behind.step`.
- `ZCF3R-parts.csv`: part, qty, material, process, mass (g), bounding box.
- A short note covering:
  - the fillets and bend radii used;
  - bent or machined, per link;
  - the BOTTOM joint option chosen;
  - any deviation from this brief, with the reason.

## 7. Acceptance checks (run them on the output)

| # | check | pass |
|---|---|---|
| A1 | units and frame | mm; the joint axes meet at the origin within 0.1 mm |
| A2 | hub axes | each hub's revolve axis within **0.1 deg** of the axis unit in 3.1 |
| A3 | hub centres | face centre at F and crown centre within **0.1 mm** of 3.1; plate levels within 0.05 mm of 4.1 |
| A4 | stack | bore 11 H7, lip O9.8, pin O7, collar O8.2, 0.15 plate gap, cap flange at F+10.25 on bearing 2's outer ring, spigot top 0.03 below it |
| A5 | link section | bars **8 x 3** (+-0.05); neck at most 14 x 6 |
| A6 | link path | the bar's centre plane within **0.5 mm** of its sketch plane (3.3) |
| A7 | link underside | at every profile sample more than 14 mm from both axes, the underside radius is >= the profile - 0.1 mm (hard). Excess above the profile: target <= 0.5 mm where the profile is smooth, <= 3 mm at ramp feet and the link 1 dip. |
| A8 | neck underside | >= the neck grid - 0.1 mm at every grid point within the neck's width (includes the cross tilt) |
| A9 | bends | bent bars inner R >= 15; machined bars marked, R >= 1.5 inner; no ramp steeper than 60 deg |
| A10 | key poses | after applying the FK of section 2, J2 and J3 crown centres within 0.1 mm of 3.6 |
| A11 | interference | none at rest, at the key poses, or over a sweep: J2 theta2 -147.9 .. -30.0 (1 deg steps) x J3 dtheta3 -100.6 .. +110.9 (5 deg steps), J1 any. Rule: >= 1 mm between parts outside the 14 mm seat zones; 0.15 between stacked pads inside them |
| A12 | stops | J2 dowel stops theta2 at -30.0 +- 0.3 and -147.9 +- 0.08 |
| A13 | base | plain O20 disc + ring + spigot; nothing beyond r 10 |
| A14 | BOTTOM joint | lap embedded 1.0 mm in BOTTOM's top face; |c| + half-width <= 14.6; lap top n <= +7.2 |
| A15 | solids | one closed, valid, positive-volume solid per STEP; no self-intersection |
| A16 | no lofts | STEP faces only planes, cylinders, cones, spheres and tori (no B-spline surfaces); no splines in the history |
| A17 | BOM | matches 4.7 |

---------------------------------------------------------------------------------------------------------------------

**Provenance** (for the owner, not needed to build):
- Design zc-frontier-3r, verified configuration = row `docs/concepts/rows/zc-frontier-3r.json` `best_params`:
  az 109.3565, el 65.94, a1 36.7226, a2 69.0575, wd 85.7423, wa -16.1921, sigma -1, inv2 0, inv3 1, q 0.978,
  end_extra 1.784, margin 5, O20 hubs.
- Undersides: fitted on Bench(60,160) and frozen. Frozen profile sha256
  `9576b98b979e304dcda0e78b0c3962e0c1bf9d5cc5afcda18958eb089ff4f35e`.
- Re-worn on Bench(110,360) exact in this export, it gives gap 33.51 (score 87.81), the verifier's number to the digit:
  reach 0.6167, follow 0.9364, in-band 0.8917, contact 0.0299.
- The 31.04 claim uses a different shape (fit-110, same hub levels) that was not exported.
- Changes from the model, all outside every verified pose:
  - folded J2 stop moved from -24.39 to -30.0;
  - base on top at J1;
  - 8 mm bars (inside the model's width);
  - BOTTOM cut at b +20 (model metal clear by 26 mm or more).
- Scripts: `scripts/fit_and_wear.py`, `scripts/export_geometry.py`, `scripts/derive_brief.py`.
- No body data is in this folder: the profiles are the design's own clearance surfaces.
