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
