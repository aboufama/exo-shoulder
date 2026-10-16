# zc-frontier-3r: hardware and CAD-standard extract (input for the writer)

This file is working input for the person writing the CAD context document. It is not the deliverable. The deliverable
must restate every number below in plain mm and degrees. Repo paths appear here only as provenance, so the writer can
check a value; an outside reader does not need them.

Scope: every part except the user's BOTTOM plate. That means the base at the J1 ring, three O20 hub stacks, link 1,
link 2, member 3 (the arm end: hub-3 upper plate + neck), fasteners, and the interface to BOTTOM.

Units: mm and degrees. Every level along a joint axis is measured from GH (the glenohumeral centre, the origin) along
that axis.

---------------------------------------------------------------------------------------------------------------------

## 0. The configuration these numbers apply to (provenance)

- **Design:** zc-frontier-3r, a plain spherical 3R. Three active revolute joints J1, J2 and J3 have axes that all pass
  through GH. Each joint uses the O20 v5 hub with an MR117-2RS pair. There are no slides, springs, closed loops or
  sensed passive joints, so complexity is 0.
- **Verified configuration:** `best_params` in docs/concepts/rows/zc-frontier-3r.json:
  az 109.3565, el 65.94, a1 36.7226, a2 69.0575, wd 85.7423, wa -16.1921, sigma -1, inv2 0, inv3 1, q 0.978,
  end_extra 1.784. The rules fix the rest: fold margin 5, strap width 12, t_link 3, hub radius 10 at every joint.
- **Hub levels F** (from the verifier's report): hub1 51.0, hub2 58.37, hub3 71.0 mm.
  - F is the distance from GH along the joint axis to the skin-side face of the joint's lower member.
- **Verified number:** 33.51 (score 87.81). The harness was docs/concepts/verify/zc-frontier-3r-gpu-skeptic.py with
  the shape frozen from Bench(60,160) fast and worn on Bench(110,360) exact, at 2026-10-16T10:11:56Z.
  - The row records claim 33.51 against a re-measured 33.51 (diff 0.0) and honest = true.
  - Fitted on Bench(110,360) fast and worn exact, frozen, it scores 31.04 (score 88.71). The limiter is the fold.
  - This extract did not re-run the harness. Reproducing the number is the geometry-export task's job.
- **Stack order** (model docs/concepts/models/zc-frontier-3r.py, `build()`):
  - J2 normal (inv2 = 0): link 1 is the lower member, link 2 the upper.
  - J3 inverted (inv3 = 1): link 2 is the LOWER member on hub 3's lower plate. Member 3 (arm plate + neck) is the
    UPPER member and bridges over link 2.
  - J1: the model lifts link 1's strap end to F + 3.15 at hub 1, so link 1 is the UPPER member there and the base the
    lower. This conflicts with the CAD standard's base. See section 6 and flag F1.

## 1. The joint-local frame and the "hub level F" reference

- **Joint-local frame:** z runs along the joint axis, pointing away from GH (outward, away from the skin). The joint is
  a solid of revolution about the axis, and the axis passes through GH.
- **z = 0 is the plane at distance F from GH.** It is the skin-side face of the lower member's plate. "Hub level F" is
  measured from GH to this face.
- Every stack level below is z above that face. The absolute distance from GH is F + z.
- **Model envelope of a hub:** a disc of radius 10 (O20) from z 0 to z 12.25, which is the crown.
- **Strap ends** must sit at or above the hub's own level for the first and last 12 + end_extra = 13.78 mm, measured at
  a reference radius of 70 mm from GH:
  - at z 0 when the strap belongs to the lower member;
  - at z 3.15 when it belongs to the upper member.
  - In CAD this is the flat seat length: 14 mm from the axis on the bent-bar builds (L_SEAT), 11 mm on the machined
    builds (HUG_SEAT).

## 2. The v5 O20 joint stack (docs/HARDWARE.md "v5 joint"; built by param_build.py `joint_parts`, user_style.py)

### 2.1 Axial levels (z from the lower member's skin face)

| level | z (mm) | what is there |
|---|---|---|
| F | 0.00 | lower plate, skin-side face |
| S | 3.00 | lower plate top (the 3.0 plate) = lower seat; the integral pin's collar rises from here |
| U0 | 3.15 | upper member underside. The 0.15 running gap is set by the bearing stack, not by a thrust washer. |
| L1 | 3.65 | top of the 0.5 mm hub lip (bore O9.8) = top of the collar (O8.2). Bearing 1's outer ring sits on the lip and its inner ring on the collar (DIN 509 relief at the collar root). |
| B1 | 6.65 | bearing 1 top (MR117-2RS, 3 mm wide) |
| B2 | 7.25 | top of the 0.6 spacers (outer and inner) = bearing 2 bottom |
| H1 | 8.75 | top of the O20 ring (shoulder). The cap skirt floats 0.05 above it (skirt starts at 8.80). |
| SPIG | 10.22 | top of the O18 M18x0.5 spigot, 0.03 BELOW U1 (CLAMP_GAP, so the cap clamps the bearing and not the spigot) |
| U1 | 10.25 | bearing 2 top = cap flange face (bears on bearing 2's OUTER ring only) |
| N1 | 11.15 | top of the ring nut = top of the pin |
| top | 12.25 | cap crown |

Absolute levels for this design (mm from GH along each axis):

| joint | F | lower plate | upper plate | ring top H1 | spigot top | cap flange U1 | pin / nut top | crown |
|---|---|---|---|---|---|---|---|---|
| J1 | 51.00 | 51.00-54.00 | 54.15-57.15 | 59.75 | 61.22 | 61.25 | 62.15 | 63.25 |
| J2 | 58.37 | 58.37-61.37 | 61.52-64.52 | 67.12 | 68.59 | 68.62 | 69.52 | 70.62 |
| J3 | 71.00 | 71.00-74.00 | 74.15-77.15 | 79.75 | 81.22 | 81.25 | 82.15 | 83.25 |

### 2.2 Parts of one stack: dimensions, member, material, source

"Lower" is the member whose plate sits at z 0-3; it carries the pin and the inner rings. "Upper" is the member whose
plate sits at z 3.15-6.15; it carries the bore, the outer rings and the cap. MVP1 is unpowered, so there is no rotor or
stator; the two members are simply the two sides of the pin joint.

| # | part | member | geometry (mm; r = radius, z as in 2.1) | material / source |
|---|---|---|---|---|
| 1 | lower plate (pad) | lower | planform: an O20 hub circle plus the link strip, joined by tangent arcs (section 4.3); 3.0 thick, z 0-3 | part of the link, Ti-6Al-4V |
| 2 | integral pin | lower | turned on the lower plate (one part with it). Profile (r, z): collar r 4.1 (O8.2) from z 1.5 (embedded 1.5 mm in the plate) to L1 3.65; pin r 3.5 (O7) from 3.65 to N1 11.15. M7x0.5 external thread at the top under the nut (z 10.25-11.15 at least). DIN 509 undercut / relief at the collar shoulder. | Ti-6Al-4V, one part with its link |
| 3 | upper plate | upper | the same planform as 1, 3.0 thick, z 3.15-6.15 | part of the link / member, Ti-6Al-4V |
| 4 | O20 ring + spigot | upper | revolved on the upper plate. Ring r 10 from 6.15 to H1 8.75 with an R0.5 outer top corner; spigot r 9.0 (O18) from 8.75 to 10.22 with an R0.3 top corner, M18x0.5 EXTERNAL thread over its height (about 1.47 mm, about 3 pitches). Optional R1 concave fillet where the ring rises from the upper plate. | one part with the upper member, Ti-6Al-4V |
| 5 | bore through 3 + 4 | upper | r 4.9 (O9.8 lip) from z 3.15 to L1 3.65; r 5.5 (O11, bearing seat) from 3.65 through the spigot top | machined |
| 6 | bearing 1 | upper (outer ring) / lower (inner ring) | MR117-2RS, 7 x 11 x 3: r 3.5-5.5, z 3.65-6.65 | catalogue, bearing steel, 1.32 g |
| 7 | outer spacer | upper | O11 x O9.8 x 0.6: r 4.9-5.5, z 6.65-7.25 | 17-4PH, select-ground at assembly, 0.09 g |
| 8 | inner spacer | lower | O8.2 x O7 x (0.6 - delta): r 3.5-4.1, z 6.65-7.25. delta is the preload offset (about 5 um, from the supplier's preload table), not modelled. | 17-4PH (docs/HARDWARE.md), ground and lapped as a matched pair with 7 (flag F4) |
| 9 | bearing 2 | upper / lower | MR117-2RS, 7 x 11 x 3: r 3.5-5.5, z 7.25-10.25 | catalogue, 1.32 g |
| 10 | ring nut | lower | M7x0.5, O8.6 x 0.9: r 3.5-4.3, z 10.25-11.15. Bears on bearing 2's INNER ring only. 2 pin-spanner holes, Loctite 222. | Ti-6Al-4V, 0.08 g |
| 11 | cap | upper | see 2.3. Threads onto the spigot (M18x0.5, Loctite 222), tightened with a soft-jaw cup. No drive features, no holes, no visible screws. | Ti-6Al-4V, 2.12 g |

**Stack height:** 12.25 mm from F to the crown; 9.25 mm from the upper plate's underside to the crown.

**Two clamped stacks, so no play:**
- Outer: hub lip (L1) -> outer ring 1 -> outer spacer -> outer ring 2 -> cap flange at U1. The spigot top sits 0.03
  under U1, so the flange bears on the bearing and never on the spigot.
- Inner: pin collar (L1) -> inner ring 1 -> inner spacer -> inner ring 2 -> ring nut.
- Because the inner spacer is shorter by delta, the pair is preloaded back-to-back (DB). Pressure centres are about 6 mm
  apart, so the pair carries radial, axial and tilt loads.
- An alternative to the ground spacers is a factory DB-matched P5 pair.

**Designed clearances between the two members:**

| between | clearance (mm) |
|---|---|
| collar and lip bore | 0.8 radial (r 4.1 vs 4.9) |
| lower plate top and upper plate underside | 0.15 axial |
| cap pocket and nut | 0.2 radial (r 4.5 vs 4.3); 0.6 axial with no sensor PCB, 0.2 with one |
| cap skirt and ring shoulder H1 | 0.05 axial float |

**Assembly order:**
1. Into the upper member's bore from the top: bearing 1, outer spacer, bearing 2.
2. Pin up through the inner rings, with the inner spacer between them.
3. Torque the ring nut with a pin spanner while holding the lower member.
4. Thread the cap (or the handler bracket at J1) on last.

**Load check (docs/HARDWARE.md, not FEA):**
- MR117-2RS catalogue C is about 0.7 kN and C0 about 0.28 kN (to confirm with the supplier).
- MVP1 (unpowered: <= 1 N.m at the shoulder, about 0.5 N.m worst tilt at a joint) gives about 0.1 kN per bearing,
  under C0.
- MVP2's roughly 10 N.m would need the pair re-sized. Say so on the part; it is not a design input now.

### 2.3 Cap O20: torispherical dome, threaded M18x0.5 (user_style_minarc.py `cap_v5` / `_ts_dome`, used in gen-4 / 4b)

The cap is a revolved profile of lines and tangent arcs only. It replaces the spline dome of the older builds; there is
no spline. Profile (r, z), closed:

| step | segment |
|---|---|
| 1 | (9.0, 8.80) -> (10.0, 8.80): skirt bottom, 0.05 above H1 |
| 2 | (10.0, 8.80) -> (10.0, 10.60): skirt wall O20, continuing the ring wall (one hairline seam at 8.80) |
| 3 | knuckle arc R1.0 tangent to the wall at (10.0, 10.60), centre (9.0, 10.60), ending at the tangent point (9.144, 11.590) |
| 4 | crown arc R63.63, centre on the axis at z -51.383, tangent to the knuckle, to the apex (0, 12.25) |
| 5 | (0, 12.25) -> (0, 11.75): crown 0.5 thick on the axis |
| 6 | (0, 11.75) -> (4.5, 11.75) -> (4.5, 10.25): inner pocket O9 x 1.5 that clears the ring nut (the user's sensor goes here) |
| 7 | (4.5, 10.25) -> (9.0, 10.25): flange face, an annulus r 4.5-9.0 bearing on bearing 2's outer ring |
| 8 | (9.0, 10.25) -> (9.0, 8.80): M18x0.5 INTERNAL thread over z 8.80-10.25 |

- **Name in the builds:** "cap O20, torispherical dome R63.6 / R1 (tangent arcs), threaded M18x0.5 (Ti-6Al-4V)".
- **Alternative flat cap** (MINARC_CAP=flat): the same skirt and pocket, wall up to 11.75, an R0.5 crown corner and a
  flat crown at 12.25.
- **Sensing (MVP1, the user adds it):** keep the O9 x 1.5 pocket free for the user's sensor. Placeholder levels the
  repo used for a magnetic encoder (docs/HARDWARE.md, optional):
  - O4 x 2 diametric magnet in the pin top, z 8.30-10.30;
  - QFN 3x3 IC in a pocket, z 10.60-11.35;
  - O9 x 0.4 PCB under the cap ceiling, z 11.35-11.75.
  - The wire exit is the user's to design.

## 3. Which member carries what in THIS design

| joint | lower member (z 0-3: plate + integral O7 pin, inner rings, inner spacer, ring nut) | upper member (z 3.15-6.15 plate + O20 ring + M18 spigot + bore: outer rings, outer spacer, cap) |
|---|---|---|
| J1 (F 51.00) | link 1, as the CAD standard builds it. The model has link 1 at the upper level (flag F1). | **D8-01 base**, as the CAD standard builds it: the scapula handler's bracket threads onto this spigot in place of the cap. |
| J2 (F 58.37) | link 1 | link 2 (with the J2 cap) |
| J3 (F 71.00) | link 2 (inv3 = 1) | **member 3** (the arm end: upper plate + ring + spigot + bore + J3 cap, with the neck leaving the upper plate at z 3.15 and bridging over link 2) |

So:
- Link 1 has two lower-member pads with integral pins (J1 and J2).
- Link 2 has an upper-member ring at J2 and a lower-member pad with an integral pin at J3.
- Member 3 is an upper member: plate, ring, spigot and bore.
- Catalogue and loose parts per joint: 2x MR117-2RS, an outer spacer, an inner spacer and a ring nut. Caps on J2 and J3;
  at J1 the handler bracket takes the cap's place.

## 4. The link standard

### 4.1 Section and envelope

- **Verified model (this design):** 12 x 3 mm straps on the great circle between the two joint axes (concept_kit
  `strap_member` width 12, t 3). The underside follows the fitted profile (2 mm skin clearance, quantile q 0.978) and
  climbs at <= 60 deg. The neck (K7) is 14 x 6.
  - 12 x 3 is also the user's own link section (SHOULDER LINK OUTER / INNER: a 12 x 3 bar bent on one arc about the
    sphere centre, flat round pads, a 1 mm outer pocket, 0.5 mm rounds).
- **Repo's latest built standard** (user_style*.py, gen 2 to 4b): 8 x 3 Ti-6Al-4V bars. That was right for designs
  whose models used half-width 4. For this design, use **12 x 3** (the verified envelope) or anything inside it. Never
  wider, thicker, or lower toward the skin than the model's strap (flag F2).

### 4.2 Centreline and bends (user rulings 2026-10-16)

- The bar's side view is ONE sketch of lines and tangent arcs with set radii, drawn in the plane of the two joint axes
  (a great-circle plane through GH).
  - J3's axis also passes through GH in this model, so both links are in-plane.
  - The sketch is offset to the 3 mm thickness and extruded symmetric to the width, or swept as one constant rounded
    rectangle along the line/arc path with the binormal fixed to the sketch-plane normal.
  - Typical fits use 3-4 arcs; fewer bends are preferred.
- **Ramps:** <= 60 deg near a hub (the standard's old 35 deg was relaxed to 60 on 2026-10-16). The bar leaves its pad
  parallel to the seat, then ramps.
- **Bent 3 mm Ti-6Al-4V bar:** tangent bend arcs with inner radius >= 15 mm (5 t), i.e. centreline R >= 16.5.
- **Machined from solid (5-axis, or 3+2-axis / wire EDM for a one-profile bar):** bends may go down to centreline R3
  (1.5 inner, 4.5 outer, a 3 mm ball / bull-nose cutter). This is allowed only when stated on the part.
  - The gen-3b/4b links were machined this way so the bar hugs the model's strap within about 0.3 mm. Bent bars rode
    4-11 mm above the strap and lost R1 points.
  - A 2.5-D bar built from several side-by-side strips is 3+2-axis milling only; a wire cannot cut it.
- **Stacked joints:** the lower link thickens toward the skin, never up into the upper link. Over-relations in this
  design:
  - at J2, link 2 passes over link 1;
  - at J3, member 3 (the neck) passes over link 2.

### 4.3 Pads, pocket, rounds

| feature | bent bar | machined bar |
|---|---|---|
| pad at each hub, in the seat plane (normal = joint axis) | flat plate: the O20 hub circle plus a bar of the link width out to L_SEAT 14 from the axis, joined by tangent R6 arcs | seat L 11 from the axis, tangent R2 arcs |
| pad thickness and levels | 3.0; lower pad z 0-3, upper pad z 3.15-6.15 | same |

- **Pocket:** 1.0 mm deep on the OUTER face of every bar (away from the skin), with 1.5 mm rims, starting 4 mm from
  each end, round ends. Pocket edges get 0.4 rounds.
- **Rounds:** 0.5 mm on every sharp edge of bars and pads. Tangent edges are left alone. Machined bars carry R2 / R0.5
  in the profile.
- **Exact seats:** every seat is an exact plane, flat under the whole mating part, so the cap skirt and ring sit on a
  flat hub face.
  - Keep pad rounds off the face another body is glued to.
  - On an upper pad, keep rounds off the top edge of the hub circle, because the ring continues that cylinder.

## 5. Booleans, validity, construction (CAD_STANDARD.md "Construction rules")

- **One valid solid per part** (judge/part_validity.py; volume from the closed tessellation, not OCC Volume()).
- **Never let fused faces coincide or touch tangentially.** Embed instead:
  - the pin collar starts 1.5 mm inside the plate;
  - the neck starts about 6 mm inside the hub;
  - the riser goes 1 mm into BOTTOM.
- **Or** use a glue fuse for exactly shared end faces, as the link-to-pad joint does. Cutting tools cross faces
  transversally.
- **No lofts, ever** (user 2026-10-15). Allowed: line/arc sketches that are extruded, revolved, or swept as ONE
  constant section along a line/arc path; bends (an arc in the cross-section); planform turns; fillets.
  - Not allowed: lofts through sections, twisted or variable-section sweeps, surfaces fitted or shrink-wrapped to data,
    splines in profiles. The gen-1 lofted neck and the spline cap are both retired.
- **Outlines are sketches** of lines and tangent arcs with set radii, never a level set of a data field.
- **Look** (CAD_STANDARD.md):
  - smooth bodies;
  - no visible screws or seams beyond "a screw or two", super low profile and sunk flush;
  - parts must look constrained and accurately designed.
- **O20 hubs only** (user ruling 2026-10-16 "Keep O20 only"): the same v5 O20 stack at every joint. No O15, O17 or
  O12 slim hubs, and no press-fit slim caps.

## 6. The base: D8-01, at the J1 hub ring (user ruling 2026-10-16; user_style_pinknee.py `base_part`)

- **Ruling:** "the scapula handler can carry the base DIRECTLY at the J1 hub ring: no base tab running out from J1".
  The tab cost R1 0.68 -> 0.49 and caused the R6 / R16 / skin hits on user_osn_k4216.
- **D8-01 = the J1 upper member alone.** Built name: "D8-01 scapula base AT THE J1 RING: the J1 upper member alone (O20
  ring + seat disc + M18 x 0.5 spigot); the user's scapula handler bracket threads onto the spigot in place of the dome
  cap - no ears, no tab (Ti-6Al-4V, 5-axis machined)". It weighs 6.49 g in gen-4b.
- **Geometry (J1 axis, F 51.00):**
  - seat disc O20, z 3.15-6.15 (54.15-57.15 from GH), with no link strip: a plain disc;
  - O20 ring from 6.15 to 8.75 (to 59.75), R0.5 outer top corner;
  - O18 spigot with M18x0.5 external thread from 8.75 to 10.22 (59.75-61.22), R0.3 top corner;
  - bore O9.8 lip at z 3.15-3.65 and O11 above it;
  - it carries J1's outer rings and outer spacer.
- **Interface to the user's scapula handler** (the handler and its bracket are the user's parts):
  - The bracket threads onto the O18 M18x0.5 spigot in place of the cap.
  - It must replicate the cap's functional faces:
    - internal M18x0.5 thread over z 8.80-10.25;
    - flange face at z 10.25 (61.25 from GH), annulus r 4.5-9.0, bearing ONLY on bearing 2's outer ring (it retains
      the outer stack; the spigot top is 0.03 below);
    - a pocket of at least O9 x 1.5 above the ring nut (nut top at 62.15).
  - Loctite 222. The bracket approaches from outside (along +z of J1, away from the skin).
  - Link 1 (the J1 lower member) turns below the base, so nothing the handler adds may come below z 8.80 inside r 10,
    or anywhere link 1 sweeps.
- **No ears:** the gen-3 builder tried two M4-tapped ears in the seat plane. On gen-3 / 4 / 4b link 1 swept every ear
  heading (build.json "base": NO ears), so the spigot is the only interface.
  - An outside designer must not add tabs or ears unless they prove the ears stay clear of link 1's whole sweep and of
    the skin.
- **Flag F1, J1 member order:**
  - The verified model lifts link 1's strap end to F + 3.15 at hub 1, i.e. link 1 is the UPPER member at J1. The CAD
    standard (above) makes the base the upper member and link 1 the lower (pad at 51.00-54.00).
  - The gen-4 / 4b builds did the same while their model had link 1a at F + 3.15 at hub 1 (the minarc model). That is
    the precedent.
  - Consequence: within the pad (r <= about 11-14 from the J1 axis), link 1 sits 3.15 mm closer to the skin than the
    model's strap. That is the hub disc's own level, which the model already clears.
  - The writer must state which order the document uses. Recommended: the standard (base = upper, handler on the
    spigot from outside), so nothing on the handler side crosses link 1's sweep.
  - The geometry export must check link 1's ramp from the pad at F to its strap at >= F + 3.15 within 60 deg.

## 7. Member 3 (the arm end) and the BOTTOM interface

### 7.1 Member 3 in this design (inv3 = 1)

- The J3 UPPER member: an upper plate (z 3.15-6.15, 74.15-77.15 from GH) plus the O20 ring, M18 spigot and bore, the
  J3 outer rings, the outer spacer and the J3 cap. The J3 axis is wdir(85.7423, -16.1921) in the humerus frame.
- **The neck (kit K7):** a 14 x 6 strap, rigid in the humerus frame.
  - It leaves the J3 upper plate at z >= 3.15 (it starts on member 3's plate) and bridges over link 2, which sits on
    hub 3's lower plate at z 0-3.
  - It runs on the great circle from the J3 axis direction to the direction (0, -0.5698, 0.8218) in the humerus frame
    (concept_kit BAR0_H = 67.5 Wb + 40 Db), toward "the start of BOTTOM's bar".
  - The underside follows the fitted skin profile + 2 mm and climbs at <= 60 deg.
- **Build style for the neck:** lines + tangent arcs, planform turns, and at most ONE bend about the common line of
  two planes. Gen-1 (user_style.py `arm_end`): pad plane and channel plane 22 deg apart, a bend at centreline R4.5,
  planform turns R12 and R7.5. No loft and no twist. The pin and neck materials follow member 3: Ti-6Al-4V, or 7075-T6
  if merged with BOTTOM (7.3).

### 7.2 BOTTOM, the user's part (data/user_cad/RIGHT ARM SUBASSY.step, measured read-only; never edit it except the cut)

**BOTTOM's own bar frame** (pipeline/full-exo/bottom_frame.json): origin s = 0 at the centre of BOTTOM's own
elbow-end ring, which is a feature of the part.

| coordinate | meaning |
|---|---|
| s | along the bar, from the elbow toward the shoulder |
| y | across the bar |
| z | up = away from the arm |

The full bar runs from s -21 (elbow ring) to s 421 (old shoulder mount at s 406.4).

**Section** (constant along the straight bar; a C-channel open toward the arm):

| face | position |
|---|---|
| top (outer) face | z +3.70 |
| web underside = channel floor | z +1.70 (web 2.0 thick) |
| skin-side flange faces (the upper-arm cuff sits on them) | z -2.79, so the section is 6.49 tall |
| outer side faces | y +-15.0 (bar 30 wide) |
| inner channel walls | y +-12.0 (walls 3.0, channel 24 wide x 4.49 deep) |

**Tapped holes:** M4 (O3.30 tap drill, r 1.65), axis along z, each in an O7 boss with a 4 mm cross rib (s +-2) filling
the channel:
- stations s 94.25 / 124.25 / 154.25, y -8.72 / +8.78 (nominal +-8.75): the user's upper-arm cuff, 6x M4x6 ISO 10642
  countersunk from inside;
- stations s 280.4 / 310.4 / 340.4, same y: the user's original proximal cuff stations, removed by the repo's cuts at
  255 / 265.

**BOTTOM's frame in the humerus frame** (GH origin; the body_pose / canonical humerus frame the model's member 3 and
neck use):

| item | value |
|---|---|
| anchor: centre plane at s = 265, z = 0 | (0, -64.65, 74.45) |
| u (s direction, toward the shoulder) | (0, 0.9975, 0.0713): the bar tilts 4.09 deg outward from the humerus axis as it rises |
| v (y direction) | (-1, 0, 0) |
| z (away from the arm) | (0, -0.0713, 0.9975) |

- Humerus frame: +y proximal (GH -> elbow is -y), +z lateral (BOTTOM sits on the lateral side, centred on x = 0),
  +x anterior. Right-handed.
- The writer must cross-check this frame wording against the geometry export's frame statement.

**Points on the bar's centre plane (y = 0) in the humerus frame:**

| s | top face (z +3.70) | skin-side flange (z -2.79) |
|---|---|---|
| 255 | (0, -74.88, 77.43) | (0, -74.42, 70.96) |
| 265 | (0, -64.91, 78.14) | (0, -64.45, 71.67) |
| 277 | (0, -52.94, 79.00) | (0, -52.48, 72.52) |
| 284 | (0, -45.96, 79.50) | (0, -45.49, 73.02) |

**Where this model's neck meets BOTTOM:** the ray from GH along the neck's end direction (0, -0.5698, 0.8218) crosses
the bar's planes at:

| bar plane | z | s | distance from GH (r) |
|---|---|---|---|
| top face | 3.70 | 275.2 | 96.0 |
| channel floor | 1.70 | 276.4 | 93.7 |
| skin-side flange | -2.79 | 279.1 | 88.4 |

All three lie on y = 0. So the verified neck ends inside BOTTOM's bar section at s about 275-279, where a 6 mm-thick
neck at skin + 2 mm lands.

### 7.3 How the repo joins the arm end to BOTTOM (the rule an outside designer must mate to)

- **User ruling 2026-10-15** (user_style.py, CLAUDE.md): BOTTOM and the J3 member (the arm end) are ONE 5-axis part,
  "not bolted". BOTTOM is cut square to the bar and the arm end is fused to it.
  - Material: 7075-T6, bead blasted ("D6-04 BOTTOM + arm end, one 5-axis part (user's bar cut at s 255, strap fused
    into its channel; 7075-T6)").
  - Gen-3 / 4b: "D8-06 BOTTOM + arm pad + pad mount, one 5-axis part (... cut square to the arm ...; riser 1 mm into
    BOTTOM's underside; 7075-T6)".
- **The cut:** a plane square to the bar (normal = u) at s = S_CUT, keeping s <= S_CUT (the elbow side).
  - Used values: 255 (user_style, pinknee, minarc) and 265 (arm_end default).
  - pick1's cut was design-specific: 4.9 mm distal of its pad pin.
  - For THIS design, flag F3: the model's neck lands at s about 275-279, which is beyond a 255 / 265 cut.
- **Mating rule for the outside designer.** Design member 3 + neck as a separate solid that ends in BOTTOM's bar, so a
  boolean union gives one valid solid:
  - the neck's end overlaps the bar by >= 1 mm (embedded, never face-on-face; the repo's riser goes 1 mm into BOTTOM's
    underside = the channel floor at z +1.70);
  - it stays inside the bar's 30 mm width (|y| + half-width <= 14.6, the gen-1 assert);
  - it stays clear of the cuff screw bosses that remain.
  - Options, by geometry:
    - (a) a tongue in the channel, under the web (z -2.79 to +1.70, |y| <= 12), embedded 1 mm up into the web;
    - (b) a lap / riser onto the bar's end, embedded 1 mm.
- **Bolted fallback** (older builds; use only if a separate part is required, and state it):
  - 2 or 4 M3 ISO 10642 countersunk screws through BOTTOM's web into a tapped tongue. The heads are flush on BOTTOM's
    top face: O3.4 clearance, 90 deg countersink O6.3 at z +3.70.
  - Hole pattern (arm_end LAP_HOLES): s = S_CUT - 6 and S_CUT - 16, y = +0.06 +- 6.0.
  - The param_build variant used a 26 (along the bar) x 18 x 3 lap plate (R3 corners) centred at s = S_CUT - 11 on
    the bar top, with the same 4x M3.
- **Not ours:** the upper-arm cuff (AlSi10Mg, 6x M4x6 ISO 10642 into the s 94-154 stations), TOP, MIDDLE, the forearm
  cuff and their screws.

## 8. Materials and finishes (CAD_STANDARD.md, CLAUDE.md, gen-4b MATERIALS table)

| part | material |
|---|---|
| links, base, member 3, cap, ring nut, integral pins | Ti-6Al-4V, bead blasted |
| BOTTOM + arm end, if merged | 7075-T6, bead blasted (hard-anodise only where a running pin needs it, as on gen-4b's pad pin) |
| outer spacer (and inner spacer, per docs/HARDWARE.md) | 17-4PH |
| bearings | MR117-2RS, bearing steel, rubber seals |
| screws | A2 stainless, polished |
| dowels, if any were added (none in this design) | hardened steel, polished |
| any polymer part | iglidur orange |

- **No black parts.** That includes the bearing seals' visible faces in renders, and black oxide screws.
- Engineering drawings carry only threads and tight tolerances beyond the STEP, with no material or finish callouts
  (user rule).
- **Masses in gen-4b:** cap 2.12 g, MR117-2RS 1.32 g each, outer spacer 0.09 g, inner spacer 0.04 g, ring nut 0.08 g,
  D8-01 base 6.49 g; Ti density 4.43 g/cm3, 7075 2.81 g/cm3, steel 7.8 g/cm3.

## 9. Fits and tolerances

| interface | specification | source |
|---|---|---|
| MR117 outer ring in the O11 bore | 11 H7 | stated for the MR117 hub in docs/concepts/spine-parked-j2-3r.md |
| MR117 inner ring on the O7 pin | recommended 7 h5 / js5 (light fit, clamped stack) | the repo does not state it; mark "recommended" |
| bearing grade | P5 / ABEC-5 recommended (ring width tolerance 0/-40 um keeps the spacer grind window small; P0 is 0/-120) | docs/HARDWARE.md |
| spacers | outer spacer select-ground to the measured lip-to-spigot depth and ring widths, standing 0.02-0.04 proud of the spigot top; inner spacer ground in the same setup, then lapped delta (about 5 um) shorter | docs/HARDWARE.md |
| threads | M18x0.5 (spigot / cap, or handler bracket) and M7x0.5 (pin / ring nut), Loctite 222 on both; threads are modelled at their major / minor diameters, no flanks | docs/HARDWARE.md |
| running gaps | lower plate to upper plate 0.15 axial; cap skirt to ring shoulder 0.05 | docs/HARDWARE.md |
| integral pins | turned in the member's hub setup; the collar and lip are the datum faces both stacks start from | docs/HARDWARE.md |
| clearances | part-to-part clearance across the motion: radial 1 mm, lateral 1 mm (K6, verifier); skin: metal >= 0 mm from skin is "no contact", < 1 mm counts as near-touch, the model's undersides sit at skin + 2 mm | models |

Note the recommended inner-ring fit is industry practice, not a repo value.

## 10. Bill of catalogue and loose parts for this design

| qty | item |
|---|---|
| 6 | MR117-2RS deep-groove ball bearing, 7 x 11 x 3 (2 per joint), P5 recommended |
| 3 | outer spacer O11 x O9.8 x 0.6, 17-4PH (custom, ground) |
| 3 | inner spacer O8.2 x O7 x 0.6 - delta, 17-4PH (custom, ground, lapped) |
| 3 | ring nut M7x0.5, O8.6 x 0.9, Ti-6Al-4V, 2 pin-spanner holes (custom) |
| 2 | cap O20, torispherical R63.63 / R1, M18x0.5 internal, Ti-6Al-4V (custom; J2, J3). J1's cap function is the user's handler bracket. One extra cap makes a stand-alone J1 for bench tests. |
| 1 | base D8-01 (J1 upper member), Ti-6Al-4V (custom) |
| 1 | link 1 (two lower pads + integral O7 pins), Ti-6Al-4V (custom) |
| 1 | link 2 (J2 upper ring + J3 lower pad + integral O7 pin), Ti-6Al-4V (custom) |
| 1 | member 3 (J3 upper plate + ring + spigot + bore + K7 neck), Ti-6Al-4V or 7075-T6 merged with the cut BOTTOM (custom) |
| 0-4 | M3 ISO 10642 countersunk screws, A2 polished (only for the bolted fallback) |
| - | Loctite 222 |

## 11. Flags for the writer (state them in the document; do not resolve silently)

- **F1, J1 member order** (section 6): the model has link 1 upper at J1; the standard has the base upper. Recommend
  the standard.
- **F2, link section:** the model verified 12 x 3 straps; the repo's recent builds used 8 x 3. Use 12 x 3, or inside
  it.
- **F3, BOTTOM cut station:**
  - The verified neck ends on the ray GH -> (0, -0.5698, 0.8218), meeting BOTTOM's bar at s about 275-279 (r 88-96).
  - The repo's earlier cuts (s 255 / 265) end the bar 10-24 mm short of that. Either keep BOTTOM to about s 280-284
    (cut square there, keeping the s 280.4 station's boss and rib), or extend the neck along the bar's channel to a
    255 / 265 cut.
  - Both change geometry the verified model did not carry: BOTTOM beyond s 255 against link 2 / hub 3 sweep, or a
    longer neck. Mark it as an open check, not a verified fit.
- **F4, inner spacer material:** docs/HARDWARE.md says 17-4PH (matched, ground pair with the outer spacer); gen-4b's
  material table billed it Ti-6Al-4V (mass only, 0.04 g). Use 17-4PH: hardened against the bearing's inner ring, and Ti
  galls.
- **F5, thread engagement:** the cap / bracket on the spigot engages about 1.47 mm of M18x0.5 (about 3 pitches). That
  is enough for MVP1 with Loctite 222. Flag it for MVP2 loads.
- **F6, load rating:** MR117 C0 is about 0.28 kN (to confirm with the supplier). MVP1 is fine; MVP2 needs a re-size.
- **F7, cap spline:** older builds' `cap_shape` (param_build.py) uses a spline dome. Do not copy it. The torispherical
  R63.63 / R1 dome in 2.3 is the standard.
- **F8, sensing:** the user adds rotation sensing (MVP1). Keep the cap pocket free and do not design the encoder; the
  placeholder levels in 2.3 are optional.

Sources:
- docs/HARDWARE.md (v5 stack, preload, clearances, load check)
- docs/CAD_STANDARD.md (rules, 2026-10-16 rulings)
- pipeline/conformal/param_cad/param_build.py (LV levels, joint_parts profiles)
- pipeline/conformal/param_cad/user_style.py (pads, ring, bore, bars, pocket, rounds, arm_end, BOTTOM merge)
- pipeline/conformal/param_cad/user_style_pinknee.py (machined bars, base_part, arm side)
- pipeline/conformal/param_cad/user_style_minarc.py (torispherical cap, MATERIALS)
- pipeline/full-exo/designs/user_minarc_pick1/{parts_full.json, build.json, VERIFY.md}
- pipeline/full-exo/designs/cad_r18_n3_s1392_1_f300/parts_full.json (plain-3R arm end, merged BOTTOM + neck)
- pipeline/conformal/band_cad/arm_end.py (BOTTOM section, cut, LAP_HOLES)
- pipeline/full-exo/bottom_frame.json, arm_fit.json; BOTTOM measured from data/user_cad/RIGHT ARM SUBASSY.step
  (read-only)
- tools/concept_kit.py (HUB_R / STACK / CROWN, K5 strap, K7 neck, BAR0_H)
- docs/concepts/models/zc-frontier-3r.py, docs/concepts/rows/zc-frontier-3r.json
