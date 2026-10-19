# Independent check: user_minarc_bdp (the generation-4 winner's full CAD) and its 25 stills

Checker (a skeptic), 2026-10-16 15:20-16:05 UTC. Tested: the full CAD v2 (commits 7444067, a8cea51, 64c832e), its
builder `pipeline/conformal/param_cad/user_style_minarc.py`, and the stills in
`renders/2026-10-16_userstyle_minarc_bdp/` (commit e879836).

I re-measured everything below with my own scripts, kept in the session scratchpad `vfy/` and not committed:
- `kin_check.py`: kinematics, model metal against the posed CAD, clip provenance and skin clearance.
- `hw_check.py`: the fits of the spring, magnet and dowels.
- `hub_env.py`: hub heights against the model.
- `noloft_build.py`: a full rebuild with every loft and spline entry point trapped.

Where the judges ran:
- R1, R1-aim, R4, R6 and R16 ran on the farm with `--outdir` set to scratch, so no judge file in the tree was overwritten.
- R7 ran locally. Its output is byte-identical to the committed file.

I changed nothing in the design.

**Verdict: NOT REFUTED.** Every judged number reproduces exactly, and the CAD sits on the verified model's kinematics.
The corrections below change no requirement's status:
- **R1 measurement gap.** The R1 judge never counts link 1a, link 1b or hub K. With them counted, the full CAD reads R1
  80.0 % (not 71.7), R1-aim 51.0 % and R4 72.0 %, and its L1 reads 80.5 %. The "R1 below gen 3" story was mostly that
  blind spot (section 4).
- **R8 mass bug.** R8 really reads 202.6 g, not 239.1 g.
- **New red-team finding.** K's opposed second stop slot is cut through the root of link 1a's strap. Rotating the pair
  fixes it.

## 1. The posed parts reproduce the verified model

The fit is the kit-rule model's own frozen fit on Bench(60,160) fast, with `params_floorBD5_phys_cap6.json` and a1max
54.748. My re-run reproduces it:

| quantity | value |
|---|---|
| near-touch gap | 14.55 |
| plain gap | 12.25 |
| tr | 88.30 |
| knee centre m | (-19.83, 3.63) |
| hub levels f | 49.42 / 62.05 / 81.59 |
| fK | 56.22 |

I checked seven bench poses. Five follow clips and two are in the forced state (K open, J2 on its q2 stop). For each
one I took the model's OWN member transforms at its bench state. I did not swap in the builder's chain. I then compared
them with the frames the judges use (`build_minarc_l1.chain`, then `frame_dict`, then `scene_export.frame_xforms`).

| pose (plane, elev, axial) | state | dK (deg) | q2 (deg) | frames vs model | closest skin (our chain groups) |
|---|---|---|---|---|---|
| arm at side (-90, 0, 75) | A | 0 | -3.60 | 5e-5 mm | l1a 2.50 mm |
| highest taken (45, 165, -90) | A | 0 | 14.24 | 6e-5 mm | l1a 1.54 mm |
| overhead raise peak (30, 150, -60) | A | 0 | 76.95 | 6e-5 mm | **l2 0.038 mm**, l1b 0.22 mm, l1a 0.82 mm |
| behind the back (-90, 30, 105) | A | 0 | -16.51 | 7e-5 mm | l2 2.60 mm |
| across the body (150, 45, -60) | A | 0 | -19.53 | 4e-5 mm | l1a 6.22 mm |
| K most open (105, 120, -90) | forced | -34.16 (stop B -34.47) | -24.98 (on its stop) | 5e-5 mm | l1b 2.04 mm |
| K half open (-60, 45, 105) | forced | -13.84 | -24.98 (on its stop) | 6e-5 mm | l2 1.82 mm |

**Clip provenance.** The judged clips.json (identical to the L1's, md5 393d704b) matches a fresh chain solve within
max |dG| 5e-7 and |dT| 5e-5 mm. That covers 195 group frames, including Raise overhead frames 0, 36 and 78.

**Skin contact.** No part of our chain (base, l1a, l1b, l2, l3, l4) is inside the skin at any check pose. The hub-2
pinch at the overhead peak (0.038 mm) is the verified shape's own known weak spot, and it reproduces. The arm-fixed
part D8-06 (the user's BOTTOM fused with our pad mount) is inside the rig's skin by 1.9-4.0 mm at every pose, and by
25 mm across the body. That is the known R2 liner and rig-arm finding, the same as gen 3.

### Model metal against the posed CAD

All seven poses give the same numbers to 0.001 mm.

| model metal | how far it sits outside the CAD |
|---|---|
| hub skin discs J1 / K / J2 / J3 | 0.144 / 0 / 0 / 0 mm |
| E boss, arm pad | 0 mm |
| hub K / hub 2 discs in the stop-slot band | 1.42 mm (the real slot void) |
| **E strap** | **0.536 mm on 8 of 100 samples** (the claim checked only hubs, boss and pad) |
| **knee-link plate** | **1.397 mm on 4 of 105 samples, at the corners** |

The E strap and knee-plate overruns are less metal than the model, so they do not add contact. The builder disclosed
them as gen-3 part shape changes (0.54 and 1.40 mm). Both exceed the 0.5 mm line, so they are listed here.

**Hub heights.** The CAD tops reach F + 12.25 at J1 / J2 / J3 and F + 18.25 at K, equal to the model (CROWN 12.25,
capK 6). They are all O20.

### Bars against the model strap

Strap samples outside the hub zones, by unsigned distance to the bar's own group:

| link | samples | max | mean | share within 0.5 mm | samples inside the bar |
|---|---|---|---|---|---|
| L1a | 4 | 2.33 mm | 1.16 mm | 50 % | 0 |
| L1b | 44 | 0.61 mm | 0.33 mm | 75 % | 0 |
| L2 | 127 | **2.19 mm** | 0.36 mm | 72 % | 0 |

The means and shares are the claim's (1.16 / 0.33 / 0.36 mm; 50 / 75 / 72 %). The claim did not state the maxima. L2
reaches 2.19 mm where the 60-deg ramp limit lifts the lower station; that is the claim's +0.26 R4 point. No bar is
below the model strap.

## 2. Every part has real size and a real component

**Hubs.** All four are the v5 O20 stack with an MR117-2RS (7 x 11 x 3) pair. The ring nut (M7 x 0.5) and the caps'
M18 x 0.5 thread are machined.

**Hub K's clock spring.** It is modelled at its real size: a 0.3 x 5 strip, 145.6 mm long, 9 half-turns from R2.75 to
R7.55.

| fit | measured |
|---|---|
| spring to chamber wall | 0.10 mm |
| spring to arbor | 0.10 mm |
| spring to ring nut | 0.30 mm |
| magnet in its pocket | 0.024 mm |

Hand check with E = 190 GPa:
- rate = E b t^3 / (12 L) = 0.0147 N.m/rad, within the spec of 0.015 or less;
- the preload of 0.08 N.m needs about 307 deg of pre-wind;
- moment at stop B = 0.089 N.m, so the bending stress is 6M / (b t^2) = 1184 MPa;
- against +C1900 (Rm of 1900 MPa or more, allowable static stress about 1400-1500 MPa) the spring holds.

Wound solid onto the O5 arbor, the strip takes about 6.6 turns against 4.5 free. So the 1 turn of preload plus
travel fits before the coils go solid.

**Stops.** Each stop is an O3 dowel pressed line-to-line in the upper boss, running in a 3.1 mm arc slot.

| check | result |
|---|---|
| radial clearance, dowel in slot | 0.047 mm, every slot |
| J2 slot | -24.98 to 100.84 deg |
| K slots | an opposed pair, stop A at 0 and stop B at -34.47 |
| dowels inside their slots | yes, at all seven poses |
| bending at the 1.4 mm lever | 407 MPa (my hand calc) |
| bearing on the Ti slot end | 103 MPa |

**Knee, pins and sleeves.** These carry over from h1b, which was checked: the iglidur GSM-0405-03 sleeves, the
washers, and DIN 6799-3.2 clips. The groove is at the clip with a 0.7 mm land plus a 0.3 mm chamfer at the pin end (a
1.0 mm land).

**R7.** It reproduces: 41 of 41 custom parts are valid single solids, `all_ok` is True, and the output is identical
to the committed file.

## 3. No lofts

**Statically.** The builder imports `user_style_pinknee`, `user_style`, `param_build`, `sketch2d` and
`build_minarc_l1` / `build_pinknee_l1`. From `param_build` it calls only `revolved`, `axis_frame`, `disc_face` and
`Envelope`. `param_build`'s loft (`strap_solid`, `main`'s neck) and its spline (`cap_shape`) are never called.
`build_full_exo.py` (ThruSections) is not imported.

**Dynamically.** I rebuilt to scratch (1417 s) with these entry points trapped: `cq.Workplane.loft / spline /
splineApprox / interpPlate / parametricCurve / parametricSurface`, `cq.Solid.makeLoft`, `cq.Edge.makeSpline*` and
`BRepOffsetAPI_ThruSections`.
- **No loft call.** There are 0 calls to `loft`, `makeLoft` or `ThruSections`.
- **One spline call path, 4 calls, none exported.** `user_style.hardware` goes through `param_build.joint_parts` to
  `param_build.cap_shape`, whose G2 dome is a `.spline`, once per hub. `user_style_minarc.hubs` drops that cap (`if " cap
  " in n: continue`) and builds the torispherical line / arc cap instead. No exported part carries it: no part is named
  "G2 dome".
- **The waste is harmless, but build.json's "no splines" is not literally true** of the build run. Building the PB cap
  only when it is wanted would make it so.
- **The rebuild reproduces the claim's own check:** 9 poses, frames 1.2e-4 mm, joint features 0.144 mm, dowels inside
  their slots.

**The B-spline faces in the STEP files are blends, not fitted surfaces.** The STEP files of links 1b and 2 and of
D8-06 contain `B_SPLINE_SURFACE` entities (48 / 216 / 34). They come from OCC's rounds: the ring-root fillets on links
1b and 2, which the user's rules allow ("fillets"), and the user's own BOTTOM in D8-06. I did not attribute them face by
face.

**Sweeps.** The spring and the gen-3 E strap / cuff are single constant-section sweeps on line / arc paths. The caps
are revolved line / tangent-arc profiles. The links are extruded line / arc side profiles.

## 4. The judges re-run

| requirement | claimed | re-run | how |
|---|---|---|---|
| R1 (2-14 mm) | 71.7 % | **71.673 %** (score_14mm.json byte-identical) | farm, step 3, 543 s |
| R1-aim (2-10 mm) | 37.5 % | **37.482 %** (score.json byte-identical) | farm, 541 s |
| R4 (Raise overhead, 14 mm) | 70.0 % | **70.05 %** | same run |
| R6 | 0.0 mm | **0.0 mm** (1337 frames x 4064 pairs, 0 above 0.15 mm) | farm, step 1, 464 s |
| R16 | 73.5 % | **73.5 %** (358 poses; does not close 25.4 %, body 0.8 %, parts 0.3 %) | farm, step 4, 242 s |
| R7 | PASS | **PASS** (41 of 41) | local OCC |

**Measurement gap in R1.** `score_design.py` keeps only groups named `base`, `l<digits>` and `H`. Groups `l1a` and
`l1b` are dropped: hub K and its 6 mm taller cap, links 1a and 1b, and the K and J2 lower plates never count. I
re-measured with them included, as a measurement change and not a design change:

I used the same script with `g[1:].rstrip("ab").isdigit()`, on the farm at step 3:

| design | R1 (2-14 mm) | R1-aim (2-10 mm) | R4 (Raise overhead, 14 mm) |
|---|---|---|---|
| user_minarc_bdp, as judged (l1a / l1b dropped) | 71.67 % | 37.48 % | 70.05 % |
| **user_minarc_bdp, l1a / l1b counted** | **80.04 %** | **50.96 %** | **71.98 %** |
| l1_minarc-bdp (L1), l1a / l1b counted | 80.51 % | not run | 72.74 % |

What this changes, all of it in the measurement and none in the design:
- **The full CAD loses only 0.5 R1 points and 0.8 R4 points to its L1** once the knuckle groups count. It was 0.8 and
  1.3 points as judged.
- **The L1 / CAD gap to gen 3 was mostly the blind spot.** The L1's "R1 7.7 points below H1's L1, cause not
  attributed" (L1 issue 6) came from the judge ignoring link 1a, link 1b and hub K. With them counted, the L1 reads
  80.5 % against H1's 80.1 %, and the full CAD reads 80.0 % against the gen-3 CAD h1b's 76.7 %.
- **R1 and R4 still fail** (90 % and 80 % needed).
- **R1-aim moves the most** (37.5 to 51.0 %): link 1a and 1b sit mostly 2-10 mm off the skin.
- **The dashboard's R1 for every knuckle design (l1a / l1b) is understated** until `score_design.py` counts those
  groups. Report that fix as a measurement change.

## 5. The stills (all 25 looked at)

**The look holds:**
- The mannequin is matte black and faceless in every image.
- No part reads black: the dowels and E-clips are polished and darkened by the black skin they reflect.
- The iglidur shows only as the orange crescents in the clip gaps.
- No part of our chain goes through the skin. The J2 cap touches it in `hero_overhead_chain.jpg`, the known 0.04 mm.

**The design shown is this CAD:**
- `shots.json` points at `designs/user_minarc_bdp`.
- Each image shows four O20 hubs, the tall K cap with its flex groove, the 4-strip links, the opposed K slot pair, the
  single 125.8-deg J2 slot, the clock spring with its outer hook, and the arbor magnet.
- The K-open views show q2 on its stop.

**Fragile but correct today.** `render_stills.mat_for` picks materials by keywords in the object name. The full part
names contain "magnet" (link 1a: "O3 magnet pocket"), "dowel" (links 1b and 2: "dowel holes") and "sleeve" (the knee
link: "sleeve bores"). Matched on the full name, links 1a, 1b and 2 would render polished and the knee link iglidur
orange. They render correctly only because Blender cuts object names to 63 characters before the keyword appears. The
stills confirm it: the knee link is grey and the bars are blasted. Rename those features or match on a material tag.

**Disclosed by the render agent and confirmed:**
- the cuff rims' jagged notch;
- the forearm cuff 8.8 mm inside the mannequin;
- the torn mannequin armpit mesh at the overhead pose (in `hero_overhead_chain.jpg` and `kopen_hubK_macro.jpg`);
- the patchy strip facets.

## Corrections (none changes a requirement's status)

1. **Mass bug in `parts_full.json`.** The material is picked by keyword:
   - "magnet" in link 1a's name gives NdFeB at 7.5 g/cm3;
   - "dowel" in links 1b and 2 gives hardened steel at 7.85 g/cm3;
   - all three are Ti-6Al-4V (4.43).

   | | as judged | corrected |
   |---|---|---|
   | link 1a | 20.98 g | 12.39 g |
   | link 1b | 26.18 g | 14.77 g |
   | link 2 | 37.78 g | 21.32 g |
   | **R8** | 239.1 g | **202.6 g** |
   | build.json "custom" | 176.2 g | 139.7 g |

   R8 still passes. The fix is to match the material on a part tag, not on name keywords. `judge/fea.py`'s
   `material_for` falls back to Ti for these parts, so R9 would not inherit the bug.

2. **R1 never sees l1a / l1b.** With them counted, R1 reads 80.0 % (not 71.7), R1-aim 51.0 % (not 37.5) and R4
   72.0 % (not 70.05). The L1 reads 80.5 %. See section 4. The judge fix is a measurement change for every knuckle
   design.

3. **The strap-vs-bar maxima are 2.33 mm (L1a) and 2.19 mm (L2).** The claim gave means only.

4. **"or wire EDM" is not possible for these bars.** Four side profiles that differ across the width cannot be cut by
   one wire pass. Say 3+2-axis milling.

5. **"No splines" is not literally true of the build run.** The builder still calls `param_build.cap_shape`'s spline
   4 times through `user_style.hardware`, then discards the result. No exported part has a spline (section 3).
6. **Catalogue names.** ISO 8734 does not list a 3 x 5.65 dowel: take 3 x 6 and deepen the press hole 0.35 mm, or
   grind it. The magnet "O3 x 1.4" is not a stock size; use 3 x 1.5 diametric, which the 1.6 mm pocket takes.

## Red team: open items for the L2 drawings (not judged; flagged)

- **New: K's second (opposed) stop slot is cut through the root of link 1a.** Measured with `vfy/kslot.py`, in the K
  axis frame `frame2` the builder uses:
  - link 1a's strap leaves its O20 K pad between 280 and 325 deg (r 10.6-14, z < 3.5 above the joint face);
  - the two K slots span 109.5-144 deg and **289.5-324 deg** (dowel centre at r 7.75, slot r 6.2-9.3);
  - so the second slot lies inside the strap's root window.

  The strap's load reaches the integral K pin (collar r 4.1) only around the slot: a 0.7 mm ligament outside it (r 9.3
  to 10) and a 2.1 mm one inside (r 4.1 to 6.2).

  The single slot of the L1 was turned 123 deg away from the strap. Adding the opposed dowel for the bearing's sake
  moved one slot under the root.

  Fix (geometry only; the kinematics and the stops are unchanged): rotate the pair. With homes of about 15 and 195 deg,
  the sectors become 340.5-15 and 160.5-195, both 15 deg or more clear of the 280-325 root window. Then re-check the
  slots against the arbor slit. J2 is fine: its slot (178-304 deg) is about 100 deg from link 1b's strap root (35-80
  deg).
- **The dowel press holes leave about 0.75 mm walls** to the MR117 bore (r 5.5) and to the O20 rim (r 10). A pressed
  m6 dowel in a 0.75 mm Ti wall can distort the bearing seat. Use a slip fit with retaining compound, or move the
  dowel's press length below the bearing seat.
- **K's opposed pair is a couple only if both slot ends are true** to about 0.02 mm (about 0.15 deg at r 7.75).
  Otherwise one dowel takes the 770 N and the MR117 pair sees it radially (s0 0.73). Put the slot-end position
  tolerance on the drawing.
- **J2's single dowel still loads its MR117 pair radially at the 6 N.m jam push** (s0 0.73). This is open, as
  disclosed.
- **The knee stop at 149.5 deg is not in the CAD.** This is open, as disclosed.
- R9, R10, R11 and R17 were not run. `dynamics.py` needs a knuckle mode. These are open, as disclosed.

Spend: $0.047 on the farm for R1 / R1-aim / R4 / R6 / R16, plus $0.051 for the three R1 measurements with the
knuckle groups counted. That is about $0.10 in all, with no GPU.
