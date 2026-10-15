# Joint hardware: v4 encoder joint (every shoulder joint)

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

## v5 joint concept (user decisions 2026-10-15: rolling bearings; cables are MVP2)

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
