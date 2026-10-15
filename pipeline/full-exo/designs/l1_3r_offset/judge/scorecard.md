# Scorecard: l1_3r_offset

| | requirement | value | target | status | judge |
|---|---|---|---|---|---|
| R1 | Proximity: covered skin 2-14 mm from the metal while following (user 2026-10-15: pass at 14 mm, aim for 10) | - | >= 0.9 | **NOT RUN** | full-exo/score_design.py BAND_HI=14 (exact posed skin, 30 fps clips) |
| R1-aim | Aim: the same at 2-10 mm (the 1 cm rule) | 0.1% | >= 0.9 | **FAIL** | full-exo/score_design.py (exact posed skin, 30 fps clips) |
| R2 | No part enters the body, any frame of any clip | 24.94 mm | <= 0.5 mm | **FAIL** | judge/body_contact.py (exact depth; inside = winding number) |
| R3 | Follows the arm (frames tracked, not held at a limit) | 49.0% | >= 0.95 | **FAIL** | full-exo/score_design.py |
| R4 | Overhead works (Raise overhead clip score) (14 mm band) | - | >= 0.8 | **NOT RUN** | full-exo/score_design.py |
| R5 | Shoulder-chain DOF from the scapula base to the arm, counted kinematically (cap 4; the user's scapula handler is a separate part) | 3 | <= 4 | **PASS** | design.json |
| R5-aim | Aim: exactly 3 DOF, the minimum (user 2026-10-15) | 3 | <= 3 | **PASS** | design.json |
| R6 | No interference between parts that move relative to each other | 2.4 mm | <= 0.15 mm | **FAIL** | judge/part_contact.py (geometry only; exact depth, inside = winding number) |
| R7 | Every custom part is one valid closed solid | True | == True | **PASS** | judge/part_validity.py (OCC BRepCheck on the exported STEP) |
| R8 | Custom-part mass budget (proposed) | 172.8 g | <= 300 g | **PASS** | parts_full.json (mesh volume x density) |
| R9 | Strength: SF >= 1.5 at 25 N.m worst direction; deflection and fatigue bounded | - |  | **UNVERIFIED** | independent FEA (CalculiX) - only the in-house hex8 study exists (pipeline/conformal/thin_study) |
| R10 | Base rides the scapula on the user's scapula handler: worst GH misalignment from base slip over the bone (proposed) | 5.83 mm | <= 4.0 mm | **FAIL** | judge/base_mount.py (girdle mount: skin-slip model to build; the thorax-plate check stays for designs with a thorax base) |
| R11 | Interface pressure under ISO/TS 15066 body-region limits | - |  | **NOT MEASURED** | coupled human-exo contact sim (MuJoCo/Drake) then pressure film / FSRs on a prototype |
| R12 | CAD standard: G2 surfaces, flat seats under every seat, no visible screws or seams | - |  | **PARTIAL** | zebra / curvature check (full-exo/parts.html) + user review |
| R13 | Manufacturable | - |  | **NOT DONE** | supplier DFM review + quote (CNC Ti / 7075, SLM AlSi10Mg) |
| R14 | Generalises: holds on motions and body shapes never used to design it | - |  | **NO DATA** | held-out OpenCap / AMASS clips and SMPL-X bodies (data/raw) |
| R15 | Works on real bodies | - |  | **NOT DONE** | printed prototype on the user + one very different body: OpenCap reach vs bare arm, zero skin-contact on FSR strips |

4 of 17 requirements pass.
