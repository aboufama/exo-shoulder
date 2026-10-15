# Joint hardware: v4 encoder joint, v5 preloaded ball-bearing joint

Source: `pipeline/conformal/fair_cad/joint_v4.py` (levels, parts), placed by `hardware.py` (`v4_lower_features`,
`v4_upper_features`, `v4_joint_parts`). Preview: `pipeline/full-exo/joint.html`.

O23 hub (HUB_R 11.5), **10.47 mm** above the lower member's skin face F. Axial levels from F (mm):

| level | mm | what |
|---|---|---|
| F | 0.00 | lower plate skin face |
| rec | 2.65 | washer A recess floor (0.35 deep) |
| S | 3.00 | lower plate seat (3.0 plate) |
| U0 | 3.15 | upper hub underside (washer A 0.15 proud) |
| U1 | 7.20 | upper hub top (4.05 hub, igus GSM-1012-04 sleeve) |
| B0 | 7.22 | washer B (0.02 float) |
| z0 | 7.72 | Ti ring nut M8x0.5, 18 x 1.0 (clamps the pin shoulder) |
| M0..M1 | 5.72..7.72 | O4 x 2 N52 diametric magnet in the pin stub |
| R1 | 8.72 | pin top |
| P0..P1 | 8.87..9.47 | O16 x 0.6 position PCB (sensor IC QFN 3x3 under it, 0.40 mm air gap to the magnet) |
| top | 10.47 | O22 G2 dome cap crown |

- Bearings: 2x igus iglidur GTM-1018-005 thrust washers (10 x 18 x 0.5), GSM-1012-04 sleeve, integral O10 h9 Ti pin
  stepping to an M8x0.5 stub. Placeholders for the encoder: the user said not to spend time on encoder integration -
  the kinematics are the goal; magnet + PCB are modelled for space.
- Cap: O22 G2 dome, 2x M1.6x3 ISO 10642 Ti, flush, on the line square to the arm (taps 2.7 deep).
- Materials: links Ti-6Al-4V; BOTTOM + neck + JN hub 7075-T6; cuff saddle AlSi10Mg (SLM); all bead blasted.
- Sizing (in-house FEA, `pipeline/conformal/thin_study/REPORT.md`): 25 N.m worst direction -> 5.5 mm link bodies
  (SF 1.5), the ring nut carries the 2.2 kN cap-screw pull of the earlier stack. R9 asks for an independent check.

## v5 joint: O20 hub, preloaded MR117-2RS pair, threaded G2 cap (built 2026-10-15)

User 2026-10-15: "We can go to 20mm hubs"; the v4 build "has loose bearings". Source:
`pipeline/conformal/fair_cad/joint_v5.py` (levels, parts, stand-alone demo + half section `out_joint_v5/section.png`),
placed by `hardware.py` (`v5_lower_features`, `v5_upper_features`, `v5_joint_parts`). Build switch: `JOINT=v5`
(`members.stack_levels` / `members.HUB_R` follow it; `armend_fair` gets it through the v4 names in `hardware.py`).
Matches the band evaluator's r20 geometry (`hub_r 10`, `stack 3.15`, `hub_up 7.1`, `cap_up 2.0`).

O20 hub (HUB_R 10), **12.25 mm** from the lower member's skin face F to the cap crown. Axial levels from F (mm):

| level | mm | what |
|---|---|---|
| F | 0.00 | lower plate skin face (a turned skin side may drop below it inside the pad, `members.Strap`) |
| S | 3.00 | lower plate seat; integral O7 Ti pin with a O8.2 collar rising from it |
| U0 | 3.15 | upper hub (boss) underside: 0.15 running gap, set by the bearing stack (no thrust washer) |
| L1 | 3.65 | top of the 0.5 hub lip (O9.8 bore, outer-ring face only) = collar top (inner-ring shoulder, DIN 509 relief) |
| B1 | 6.65 | bearing 1 (MR117-2RS, 7 x 11 x 3) top |
| B2 | 7.25 | 0.6 outer spacer (O11 x O9.8, 17-4PH) / inner spacer (O8.2 x O7, 0.6 - preload offset, ground) |
| H1 | 8.75 | boss top proper; the cap skirt seats over it (0.05 float) |
| U1 | 10.25 | bearing 2 top = top of the O18 threaded spigot (M18x0.5) = cap flange (clamps the upper outer ring) |
| N1 | 11.15 | Ti ring nut M7x0.5, O8.6 x 0.9 (on the inner ring only; 2 pin-spanner holes, Loctite 222) = pin top |
| M0..M1 | 8.30..10.30 | O4 x 2 N52 diametric magnet in the pin top (placeholder) |
| IC0..P0 | 10.60..11.35 | sensor IC QFN 3x3x0.75 in a O4.6 pocket of the pin stub, 0.3 air gap (placeholder) |
| P0..P1 | 11.35..11.75 | O9 x 0.4 PCB bonded under the cap ceiling (placeholder; wire exit to be designed by the user) |
| top | 12.25 | O20 G2 dome crown (0.5 Ti over the PCB; >= 0.38 over the pocket rim) |

- **No play, no loose bearing:** two stacks are clamped. Outer: hub lip -> outer ring 1 -> outer spacer -> outer ring 2
  -> cap flange (the cap threads onto the spigot and bottoms on U1). Inner: pin collar -> inner ring 1 -> inner spacer
  -> inner ring 2 -> ring nut. The inner spacer is ground shorter than the outer one by the preload offset (~5 um,
  not modelled) -> a back-to-back preloaded pair that carries radial, axial and tilt loads.
- **No visible screws:** the cap is one turned Ti part (O20 skirt continuing the boss wall, one hairline seam, G2 dome
  from the wall to the crown, zero curvature at both ends); it threads onto the spigot (M18x0.5, Loctite 222) and is
  tightened with a soft-jaw cup. No drive features, no holes.
- **Assembly:** bearing 1, outer spacer, bearing 2 into the boss from the top; pin up through the inner rings (inner
  spacer between); ring nut torqued (pin-spanner holes; the lower member held); magnet bonded; cap (PCB bonded inside)
  threaded on last.
- **Groups for R6** (parts turning with each member): lower = pin (integral), inner rings, inner spacer, ring nut,
  magnet; upper = boss, outer rings + seals, outer spacer, cap, PCB, IC. Designed clearances between the groups: collar
  vs lip 0.8 radial, seal lip vs inner-ring land 0.05, nut vs cap pocket 0.3 radial / 0.2 axial (to the PCB), IC vs
  pin pocket 0.18, lower seat vs boss 0.15.
- **Bearing load check (7 x 11 x 3 deep-groove: catalogue C ~ 0.7 kN, C0 ~ 0.28 kN; to confirm with the supplier):**
  a tilt moment M on the pair is carried by the two bearings' pressure centres, ~6 mm apart (3.6 mm centre spacing +
  the preload contact angle) -> ~M / 6 mm per bearing. MVP1 (unpowered, R17: <= 1 N.m about the shoulder, <= 5 N at
  the cuff; worst case 0.5 N.m of tilt at a joint) -> ~0.1 kN, under C0. MVP2's ~10 N.m assist, if a joint had to carry
  it as tilt, would be ~1.7 kN per bearing, 6x over C0: MVP2 needs this pair re-sized (or the moment kept about the
  joint axes); MVP1 does not. Not an FEA; R9 still needs CalculiX.
- Custom parts exported as STEP (R7): `J<n>-cap`, `J<n>-nut`, `J<n>-spacerO`, `J<n>-spacerI`.

### History: the v5 concept before it was built


MVP1 (user: "a kinematic proof of concept, with some basic bearings") uses the bearing part only; the cable groove
below is an MVP2 note - not designed now ("You should not design the gear ratios, or any of the pulley system").

Not yet built as CAD; the search parameters follow it. Per joint, at L1 keep-out level:
- **Bearings:** 2x 6700-2RS (10 x 15 x 4 mm deep-groove, pair spaced ~1 mm) inside the upper hub on the O10 Ti pin of
  the lower member - radial, axial and tilt loads; rolling friction ~0.002-0.005 replaces iglidur's 0.06-0.18 (the
  red team's self-locking threshold for the 3R designs is 0.22-0.30: ~50x margin). The plate gap stays (STACK 3.15);
  the upper hub grows from 4.05 to ~8.5 mm tall.
- **Cable drum:** a groove cut into the O23 upper-hub rim (cable pitch radius ~10.5 mm), not a separate larger drum.
  Design load (gravity-level assist, ~10 N.m peak) -> ~950 N cable tension at r 10.5 mm: O1.2 mm Dyneema/Technora
  (break > 1.5 kN) or 7x19 O1.2 mm stainless; the Bowden sheath stop sits on the lower member next to the hub.
- **Cost in proximity** (local evaluator, r14 3R, `pipeline/conformal/analysis/hub_sensitivity_v5.log`): bearings in
  a taller hub: 0.0 pts; a separate O26 drum (HUB_R 13): -5.2 pts score at 14 mm (more frames blocked by hub
  collisions) -> keep the drum inside the O23 hub. Steeper link ramps (60 deg) recover more than that (+5.6 pts).
