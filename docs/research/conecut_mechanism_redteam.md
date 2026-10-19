# J3 hard stop red team + build spec: conecut-knee-knuckle-3r (gen-8 winner)

2026-10-17. Subject: the one new mechanism in generation 8, the **J3 hard stop**. It is an ISO 8734 2 m6 440C dowel pressed into
hub 3's lower plate (member 3: pad + E strap) at r 7.5. The dowel runs in an arc groove cut under link 2's O20 boss. The stop
window is J3MIN -111.9036 / J3MAX 122.7417 on q3', the link 2 -> member 3 angle (verifier C1: J3's own angle). The re-centred
pin knee is covered only where it carries the stop's load. Its window, M5 and the knee drawing stay with the CAD build.

Scripts and outputs are in `docs/research/conecut_mechanism/`:

- `extract.py` takes the verified config (rows/conecut-knee-knuckle-3r.json best_params) through the claim's own model, loaded
  unchanged with SN_CELL=lead. It fits on Bench(60,160) fast; the fit reproduces 12.50 exactly. It then reads the frozen shape
  kinematically on the fit bench, Bench(110,360) and the held-out bench. That gives q3', the why-label and the joint axes per
  pose, the E-strap vs link-2 clearance as a function of q3' alone, and the CAD angles in hub 3's plane. Output:
  `stop_geo.json`. It takes 9 s locally.
- `stop.py` computes loads, stresses, J3 bearing loads, a 3-body impact model, the press fit, the groove vs the boss, the
  angular window, the tolerance stack and the CAD numbers. Output: `results.json`. Every number below comes from these two
  files.

Run them with `SN_CELL=lead OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/conecut_mechanism/extract.py && python3 docs/research/conecut_mechanism/stop.py`.

## Verdict

**The stop can be built at this size. The dowel and the groove are the strongest parts of the load path.** At the claim's
10 N.m sizing about J3, the dowel's shear factor is 2.6, its bending factor at the pad face 1.95, and the groove end's bearing
factor 1.66 (Ti-6Al-4V). At the judge's lock line (10 N.m at GH x s3 0.84 = 8.4 N.m about J3) the factors are 3.1 / 2.3 / 2.0.

**The weak link is J3's own bearing.** A stop at one point at r 7.5 cannot act as a pure couple. Its force F = M / 7.5 mm
returns through the J3 MR117 pair as a radial load: 155 N per N.m on bearing 1, against C0r ~280 N. So **J3's bearing 1 reaches
s0 = 1 at 1.81 N.m about J3.** In practice the moment that reaches J3 is limited by what the wearer notices (0.84 N.m) and by the
cuff slipping (1.06 N.m with a fabric liner at the strap preload). At those levels s0 = 1.7-2.2: fine for MVP1. A silicone
liner strapped to the 14 kPa budget (4.57 N.m) or a determined push to the lock line (8.4 N.m) dents the raceway, s0 0.40 /
0.22. That causes a notch in J3's feel at the stop angle, not a breakage.

The same limit already applies to every existing hard stop in this chain (J2 fold stops, K stops). With J3 stopped, the chain
passes the arm's moment to the base along u1 x u2. That loads each J1 / J2 MR117 with m / 6 mm of tilt, which reaches C0r at
1.68 N.m about GH. The J3 dowel is the strongest element in that path. **The cuff is the torque fuse.**

**The 0.74 deg held margin survives machining but not the wearer's fit.** The verified numbers hold for any lower stop in
(-112.49, -111.16). That interval is 1.33 deg (0.174 mm at r 7.5), set by held pose 392, which the stop must cut, and held pose
393, which it must take. -111.90 sits 0.585 deg from the outer end and 0.74 deg from the inner end. A machining stack held to
+-0.01 mm moves the stop by at most 0.21 inward / 0.25 outward (RSS 0.11), so it survives. At +-0.02 the worst case is 0.41,
which still fits. At ISO 2768-f (+-0.05) the worst case is 0.87, which fails both ends. A 3 mm GH-centre fit error moves phi by
~2 deg (proposer), which is larger than the whole window. The held number's stop margin is a property of the pose sample, not of
the metal.

Nothing here is unbuildable. The changes against the claim's text, each cheap:

1. **Dowel length.** No catalogue length gives the claim's 1.0 mm groove with a flush pin: 3.00 pad + 0.15 gap + 0.85
   engagement = 4.00, and most lists start d 2 at 4-5 mm with +-0.25-class length tolerance. **Buy 2 m6 x 5 (or x 4 where
   listed) and surface-grind it to 3.90 +-0.02.** Press it from the pad's upper face to a gauge: top 0.85 +-0.02 proud, bottom
   0.10 recessed in the skin face.
2. **Press fit.** H7/m6 is a transition fit, as the gen-7 nose found (-8 um at its loose end). **Ream to 2.000 -0.005 / 0 for
   2-13 um interference.** That gives hoop stress 74-480 MPa (factor >= 1.73 in the 1.5 mm ligament to the rim) and pull-out
   200-1970 N. The axial load is ~0, so this is ample.
3. **Positional tolerances.** Hold the hole and both groove ends to **true position 0.02 (+-0.01) tangential**, relative to the
   J3 bore and each part's own angular datum. **Accept the assembled stop at -112.40 <= J3MIN <= -111.25 and
   119.85 <= J3MAX <= 123.78**, read on the J3 encoder. Those bands are the windows that keep the verified bench and held
   numbers, minus 0.09 deg for the measurement.
4. **Order of operations.** Cut the groove before the finish-bore of bearing 1's seat. The groove's 0.95 mm inner wall runs
   beside the lowest 0.50 mm of that seat.

## 1. Load cases (moment about J3 at the stop)

There are two load paths.

- **Chain path.** J1 and J2 are free and J3 is on the stop. The moment about GH that the arm passes through the chain lies along
  u1 x u2, and its J3 share is s3 = |unit(u1 x u2) . u3|. Measured on the 35 stopped poses and the kinematically-OK poses within
  6 deg of J3MIN (bench, held, fit), s3 = **0.32-0.84**.
- **Cuff twist path.** The liner on the skin slips at mu p A r_arm (A 68 cm2 from the dynamics judge, r_arm 48 mm for the 185 cm
  wearer).

| case | M about J3 (N.m) | dowel F (N) | J3 brg 1 radial (N) / s0 | J1, J2 tilt per bearing (N), >= (M / 0.84) / 6 mm |
|---|---|---|---|---|
| felt: the dynamics judge's 1 N.m free-moment line at GH x s3 | 0.84 | 112 | 130 / **2.16** | 167 |
| cuff slip, fabric liner, strap preload (mu 0.5, 6.5 kPa) | 1.06 | 141 | 164 / **1.71** | 210 |
| cuff slip, mu 0.5 at 14 kPa / mu 1.0 at 6.5 kPa | 2.28 / 2.12 | 304 / 283 | 351 / 0.80; 326 / 0.86 | 452 / 421 |
| cuff slip, silicone liner at the 14 kPa budget (mu 1.0) | 4.57 | 609 | 706 / 0.40 | 907 |
| lock: the judge's 10 N.m lock line at GH x s3 0.84 | 8.40 | 1120 | 1297 / 0.22 | 1667 |
| claim's sizing: 10 N.m about J3 | 10.0 | 1333 | 1544 / 0.18 | 1985 |

Notes on the table:

- The J3 bearing load includes the knee link's force, M / d_perp = 12 N per N.m, added as an upper bound. The contact centroid
  sits at z 3.575, below bearing 1, so bearing 1 carries 1.06 x the total. The DB pair's pressure centres are taken at
  3.95 / 9.95, about 6 mm apart (docs/HARDWARE.md). MR117 7 x 11 x 3: C0r ~0.28 kN, Cr ~0.7 kN. These are catalogue values to
  confirm with the supplier.
- For s0 = 1 on J3's bearing 1 the limit is **1.81 N.m about J3**. For J1 / J2 tilt to reach C0r per bearing the limit is
  **1.68 N.m about GH**. The J1 / J2 limit is not new: the lead's J2 and K stops load the same path.

**Impact at the stop.** This is a 3-body torsion model about the J3 axis:

- the arm: bone + forearm + hand, elbow at 90, 0.065 kg m2;
- the tissue spring: 1.72 N.m/rad, 0.02 N.m.s/rad (the judge's Schiebl values);
- the pad group: arm pad + cuff + BOTTOM, 117.6 g on r 50, 2.9e-4 kg m2;
- the knee: E strap in-plane bending in series with the MR63ZZ pins, **465 N.m/rad**, i.e. 0.12 deg of member-3 lag per N.m;
- member 3 itself: 6.7e-5 kg m2;
- the stop: J3 pair radial ~10 N/um in series with dowel shear, contact and web, **460 N.m/rad**, unilateral.

In the model the arm drives into the stop at w0, the wearer reacts after 150 ms, and the arm stops over 100 ms.

| J3 speed at contact | peak stop moment (N.m) | metal-only spike (N.m) | cuff twist (deg) |
|---|---|---|---|
| 30 dps | 0.20 | 0.09 | 6 |
| 90 dps | 0.59 | 0.28 | 18 |
| 152.5 dps (fastest nominal-case clip J3 speed, Comb hair, user_slipper_nose dynamics) | **1.00** (J3 brg 1 s0 1.8) | 0.47 | 30 |
| 286 dps (the judge's all-joint peak) | 1.88 (slip-capped 1.75) | 0.87 | 57 |

- The peak comes from the arm loading the tissue, not from the metal knock. The 4347 dps entry in dynamics.json is the
  mu 0.37 plain-bearing stick-slip case, not a swing.
- **No fit-clip frame comes within 49 deg of the stop** (clips q3' -62.4..101.4). The stop is met only at the workspace edge:
  plane -15..15, elevation 90-165, axial +15..+75 on the low side; plane 60-105, elevation 150-165, axial -75..-105 on the high
  side. Those are slow, deliberate reaches.

## 2. Dowel, groove and press fit (440C dowel, Ti-6Al-4V pad and boss)

| at 10 N.m about J3 (claim's sizing) | engagement e 0.85 (groove 1.0, chosen) | e 1.35 (groove 1.5) | e 1.85 (groove 2.0, a stock x 5 pin, through) |
|---|---|---|---|
| dowel shear (MPa) / factor on 1.1 GPa | 424 / 2.60 | 424 / 2.60 | 424 / 2.60 |
| dowel bending at the pad face, arm 0.15 + e/2 (MPa) / factor on 1.9 GPa | 976 / **1.95** | 1401 / 1.36 | 1825 / 1.04 |
| groove end, projected (MPa) / factor on Fbry ~1.3 GPa | 784 / **1.66** | 494 / 2.63 | 360 / 3.61 |
| groove end, Hertz conformal (R 1.0 in R 1.05) p0 / b | 1387 / 0.72 mm (b ~ R: projected governs) | | |
| pad hole wall, force + couple (MPa) | 289 | | |
| groove floor vs bearing 1 seat overlap / boss section removed | 0.50 mm / 8.2 % | 1.00 / 12.4 % | 1.50 / 16.5 % |

**e 0.85 / groove 1.0 is the right choice.** A deeper groove buys bearing area but lengthens the dowel's bending arm, and it
digs deeper beside bearing 1's seat. At the realistic 1 N.m every factor is 16 or more. The groove end does not creep: 83 MPa at
1.06 N.m.

**Press fit.** Through hole in the 3.00 mm pad, 1.5 mm ligament to the rim (Lame with c = a + 1.5):

- H7/m6 can come out at -8 um (loose): **ream to 2.000 -0.005 / 0**, which gives 2-13 um interference;
- contact pressure 54-348 MPa, hoop 74-480 MPa (factor >= 1.73 on 830 MPa);
- pull-out 200-1311 N (mu 0.2) or 302-1966 N (mu 0.3);
- the axial load is ~0, because the contact force is tangential and the J3 pair is preloaded DB with no axial play. Upward, the
  groove floor caps the dowel at 0.15 mm.
- No Loctite is needed. Use it anyway if the reamer runs at the loose end (Loctite 648, as the gen-7 nose).

## 3. The groove vs link 2's boss (ring stiffness, height over the skin)

- **The groove sits at r 6.45-8.55** in the boss (r 5.5 bearing seat to r 10 rim, z U0 3.15 .. H1 8.75). It is 1.00 deep, from
  z 3.15 to 4.15, and runs **251.45 deg** including the two R 1.05 ends. That leaves a **108.55 deg web**.
- Walls: **0.95 to the bearing seat** and **1.45 to the rim**. The inner wall runs beside only the lowest 0.50 mm of bearing 1's
  3.0 mm seat. Below that, the boss lip (r 4.9-5.5, z 3.15-3.65) carries the outer-ring face untouched.
- The groove removes 8.2 % of the boss section over 251 deg, and only at its skin-side bottom. Link 2's bar joins the boss
  higher up (the ramps land at the hub level), so the bar-to-boss path never crosses the groove.
- Put the web centre under link 2's bar root, as specified in section 6. The full section then sits where the boss is joined.
- **Height over the skin: unchanged.** The dowel lives inside the 0.15 running gap plus the groove, so the stack stays at
  12.25. Its skin end is recessed 0.10 in the pad face. There is no new skin-facing metal, so R1 / in-band are untouched by
  construction (the claim's "no new metal" holds).
- **Never-touch check on the strap.** E strap vs link 2, from the frozen shape on q3' alone:
  - **0.63 mm at J3MIN**;
  - the model's 0.15 adjacent-jam line at -114.5;
  - **metal touch at -115.25**, 3.35 deg past the stop.
  The elastic give at the stop is 0.12 deg per N.m (460 N.m/rad), so the strap stays off link 2 up to ~25 N.m. The stop is the
  designed version of the E-L2 limit, as verifier C3 said. At J3MAX the strap is 7.3 mm clear, so the upper stop only cuts the
  3 held knee-E skin contacts (752 / 897 / 965).

## 4. Play stack and what it does (cuff, fold margin, the score)

**The stop window that keeps the verified numbers** (frozen shape, per pose q3'):

| side | must take (deepest kin-ok pose) | must stop (nearest stopped pose; metal if admitted) | band | nominal | margin in / out |
|---|---|---|---|---|---|
| low, held | 393 (-15, 90, 75) **-111.159** | 392 (-15, 90, 30) **-112.488** (-1.11 mm skin) | 1.33 deg = 0.174 mm | -111.904 | **0.74 / 0.585** |
| low, bench | 205 (0, 105, 15) -110.997 (a contact either way: hub 2 -4.28) | 182 (-15, 90, 45) -115.696 | 4.7 deg | | 0.91 / 3.79 |
| low, fit bench | 91 -98.43 | 92 -112.791 | (the fit's taken set is unchanged for J3MIN in (-112.79, -98.43)) | | |
| high, held | 683 (45, 165, -30) 119.752 (a contact; taken 1099 at 119.44) | 897 (90, 165, -75) **123.872** (-2.68 mm skin) | 4.1 deg | 122.742 | 2.99 / **1.13** |

**Machining stack** (deg at r 7.5, 0.00764 deg per um):

| contributor | random | bias |
|---|---|---|
| dowel hole true position in the pad, +-10 um tangential | +-0.076 | |
| groove end-arc centre position in the boss, +-10 um tangential | +-0.076 | |
| groove width 2.10 +0.02/0, so end radius 1.05-1.06 | | 0..+0.076 (stop later) |
| dowel m6 2.002-2.008, so radius +1..+4 um | | -0.031..-0.008 (stop earlier) |
| pin a bore +-0.02 at lE 97, member 3's angular datum | +-0.012 | |
| link 2's J2 / J3 bore relation +-0.02 over ~60 mm | +-0.019 | |
| J3 DB pair radial play | 0 (preloaded) | |
| **total** | **RSS +-0.11; worst 0.21 in / 0.25 out** | |

At +-0.02 per feature the worst case is 0.41, which still fits the 0.585 outer margin. At +-0.05 (ISO 2768-f) it is 0.87, which
fails. **Put +-0.01 (true position 0.02) on the drawing**, plus the acceptance bands from the verdict.

**Fit, not metal, is what is fragile.** A 3 mm GH-centre error is ~2 deg of phi (proposer). On the wearer, poses 392 / 393 can
swap sides. Losing 393 costs 1 / 952 of held reach. Admitting 392 puts metal 1.1 mm into tissue at plane -15 / elevation 90 /
axial 30, an extreme reach, as a pressure point and not a cut. Neither changes the build.

**Cuff and fold margin.**

- **Fold margin `th`: 0 effect.** `th` is the J1-J3 dyad angle's distance from the fold (tools/concept_kit.py lines 25-30). It
  depends on q2 and K, never on q3, so the J3 stop cannot move it. It stays at the lead's 5.181 bench / 5.006 held, with the
  gen-7 +0.75 deg K lead build rule.
- Member 3 vs the arm at the stop, per N.m:
  - knee + strap compliance 0.12 deg;
  - MR63ZZ play at pins a / b, 2 x (8 um clearance + 5 um fit) over d_perp 83.5, 0.018 deg.
- The tissue twists 33 deg per N.m (0.03 N.m/deg). **The metal adds < 0.5 % to the cuff twist.** The stop itself has no play,
  because it is a contact. Off the stop the dowel floats 0.046 mm per side in the groove, so it never rubs in normal motion. Keep
  the dowel's radial position within +-0.02 (concentric groove walls 0.02 to the J3 bore): that leaves >= 0.026 mm running
  clearance.
- **Spring / preload: none needed, none wanted.** The stop is unilateral and is held only while the wearer pushes into it at
  the workspace edge. Adding a spring would add a sprung coordinate (the continuity rule) for nothing. The J3 pair's zero play
  comes from the v5 ground spacers (docs/HARDWARE.md) and is unchanged.

## 5. Parts list (stop only)

| part | spec | qty | play / rating |
|---|---|---|---|
| stop dowel | **ISO 8734 (DIN 6325) 2 m6 x 5** (or x 4 where the supplier lists it), martensitic stainless 1.4125 (the 440C grade), >= 56 HRC with a cert; **surface-ground to 3.90 +-0.02**, edges re-broken; polished (render: polished steel) | 1 | d 2.002-2.008; shear 3.4 kN; at 10 N.m about J3: bending factor 1.95 |
| dowel hole (pad = hub 3 lower plate, member 3) | through **2.000 -0.005 / 0 reamed** (2-13 um interference), at r 7.500, true position 0.02, perpendicular to the J3 face 0.01; chamfer 0.1 x 45 on top; press from the top with an anvil and a height gauge: top 0.85 +-0.02 above S (3.00), skin end recessed 0.10 | (in the pad) | hoop <= 480 MPa (factor 1.73); pull-out >= 200 N |
| stop groove (link 2's O20 boss underside) | arc slot **2.10 +0.02/0 wide, 1.00 +0.05/0 deep** (z 3.15-4.15), centre radius 7.500, walls concentric to the J3 bore within 0.02, **full R 1.05 ends**; end-arc centres at true position 0.02 tangential (section 6 angles); 3+2-axis from below in the hub-3 setup with an O2.0 or O1.5 end mill (link 2 is machined from solid, ruling O4); **cut before the bearing-1 seat finish bore** | (in link 2) | end bearing 784 MPa at 10 N.m (factor 1.66), 83 MPa at 1.06 N.m |
| J3 bearings (unchanged) | 2 x MR117-2RS 7 x 11 x 3, P5, DB preloaded by the v5 ground spacers | 2 | C0r ~0.28 kN: **s0 = 1 at 1.81 N.m about J3 on the stop**; 1.7-2.2 at the realistic 0.84-1.06 N.m |
| cuff liner (the torque fuse, user's part) | brushed fabric liner (mu ~0.5 on skin), strap preload 6.5 kPa | - | the cuff twist slips at ~1.06 N.m about the humerus, which keeps the stop path under s0 1.7 |

Complexity: +0.25 over the lead (the claim's 18.5): one catalogue dowel, no body, joint, loop or spring. Unchanged.

## 6. Build spec for the CAD (`results.json` "cad"; frame = link 2 local, hub-3 axis a3 pointing pad -> cap)

- **Sense.** q3' increasing = member 3 turning right-handed about a3 relative to link 2 (`extract.py` sign check: 2e-5 mm
  residual).
- **Angles in hub 3's plane**, link 2's frame, measured from e = unit(a3 x x_local), f = a3 x e:
  - link 2 bar root at **+24.75 deg**;
  - E strap root at **-177.43 + q3'**. At J3MIN the E root is 45.9 deg from link 2's root (they are at different levels: E at the
    pad, link 2 above the boss).
- **Dowel (member 3).** In the pad at r 7.500, **+16.76 deg from the E strap's root centreline**, right-handed about a3. That is
  -160.67 deg in link 2's frame at q3' 0, and it puts the groove's web centred under link 2's bar root.
- **Groove (link 2).**
  - The dowel centre travels from **87.43 deg** (q3' = J3MIN) to **322.07 deg** (q3' = J3MAX), increasing through 180.
  - The end-arc centres sit 0.382 deg beyond the dowel-centre stop angles (R 1.05 end vs r 1.0 dowel): **87.044 and
    322.453 deg**, each with a full R 1.05 end.
  - Half-width 8.02 deg. Total arc 251.45 deg. Web 108.55 deg, centred on 24.75 deg.
- **Levels** from the pad's skin face F (v5 stack):
  - pad 0-3.00; dowel 0.10-4.00; running gap 3.00-3.15;
  - groove 3.15-4.15 (tip clearance 0.15);
  - bearing 1 3.65-6.65 (overlap with the groove 0.50 mm, wall 0.95).
- **Model it as** an extruded arc slot (a sketch of two concentric arcs and two tangent R 1.05 end arcs, extruded 1.00 into the
  boss underside). The dowel is a revolved O2 x 3.90 solid in the pad group, drawn as the press fit (overlapping its plate, same
  member). There are no lofts. Name the parts so R6 sees them as the lower (dowel) and upper (groove) groups of J3.
- **Drawing notes.**
  - "J3 stop: acceptance -112.40 <= J3MIN <= -111.25, 119.85 <= J3MAX <= 123.78 (read on the J3 encoder at assembly)".
  - "stop rated 1.8 N.m about J3 (J3 bearing s0 = 1); dowel / groove good to 10 N.m".
  - "groove before the bearing-1 seat finish bore".
  - "dowel recessed 0.10, never proud".
- **Judges the CAD should re-run on this feature.** R6 at J3, dowel vs groove floor and walls at every clip frame: the groove
  covers clip q3' -62.4..101.4 with 49 / 21 deg to spare, so 0 contacts are expected. R1 / in-band: unchanged (internal
  feature). R17: the dynamics judge has no J3 limit today; the stop is reached by no clip frame, so R17 is unaffected.

## 7. What this does not cover, and what next

- **The knee drawing** (the new window's physical knee stop +-0.02, MR63ZZ stk 6.0) and **M5 at mu 0.087 / 0.105 / 0.12**: these
  belong to the CAD build (task items D1-D3, O3, O4). The knee path enters here only as d_perp 83.5 (12 N per N.m) and its
  465 N.m/rad compliance.
- **MR117 C0r is a typical catalogue value** (docs/HARDWARE.md, "to confirm"). If the supplier's C0r is lower, the 1.81 N.m
  rating scales with it.
- **If the user wants the stop rated higher than the cuff fuse**, the cheapest lever is radius. A tab stop on link 2's bar root
  meeting the E root at r ~15 halves the bearing load (s0 = 1 at ~3.6 N.m), but it adds skin-facing metal at the hub rim, which
  the claim avoided. A full-complement 7 x 11 x 3 (C0 about +50 %) keeps the O20 stack. Neither is needed for MVP1.
- **A real FEA of the boss with the groove** (CalculiX, R9) would replace the section estimate here. It runs on the built CAD.
