# Scorecard: cad_r13_n4_s1343_1

| | requirement | value | target | status | judge |
|---|---|---|---|---|---|
| R1 | Proximity: covered skin 2-10 mm from the metal while following | 45.9% | >= 0.9 | **FAIL** | full-exo/score_design.py (exact posed skin, 30 fps clips) |
| R2 | No part enters the body, any frame of any clip | - | <= 0.5 mm | **NOT RUN** | judge/body_contact.py (exact signed distance) |
| R3 | Follows the arm (frames tracked, not held at a limit) | 64.5% | >= 0.95 | **FAIL** | full-exo/score_design.py |
| R4 | Overhead works (Raise overhead clip score) | 18.8% | >= 0.8 | **FAIL** | full-exo/score_design.py |
| R5 | At most 4 DOF (3R + sliding cuff, or 4R) | 4 | <= 4 | **PASS** | design.json |
| R6 | No interference between parts that move relative to each other | - | <= 0.15 mm | **NOT RUN** | judge/part_contact.py (geometry only) |
| R7 | Every custom part is one valid closed solid | True | == True | **PASS** | judge/part_validity.py (OCC BRepCheck on the exported STEP) |
| R8 | Custom-part mass budget (proposed) | 244.6 | <= 300 g | **PASS** | parts_full.json (mesh volume x density) |
| R9 | Strength: SF >= 1.5 at 25 N.m worst direction; deflection and fatigue bounded | - |  | **UNVERIFIED** | independent FEA (CalculiX) - only the in-house hex8 study exists (pipeline/conformal/thin_study) |
| R10 | Base mounts to a thorax-fixed back plate; shoulder-centre misalignment bounded | - |  | **OPEN** | OpenSim (Seth 2016 thoracoscapular model): today the base is modelled scapula-fixed |
| R11 | Interface pressure under ISO/TS 15066 body-region limits | - |  | **NOT MEASURED** | coupled human-exo contact sim (MuJoCo/Drake) then pressure film / FSRs on a prototype |
| R12 | CAD standard: G2 surfaces, flat seats under every seat, no visible screws or seams | - |  | **PARTIAL** | zebra / curvature check (full-exo/parts.html) + user review |
| R13 | Manufacturable | - |  | **NOT DONE** | supplier DFM review + quote (CNC Ti / 7075, SLM AlSi10Mg) |
| R14 | Generalises: holds on motions and body shapes never used to design it | - |  | **NO DATA** | held-out OpenCap / AMASS clips and SMPL-X bodies (data/raw) |
| R15 | Works on real bodies | - |  | **NOT DONE** | printed prototype on the user + one very different body: OpenCap reach vs bare arm, zero skin-contact on FSR strips |

3 of 15 requirements pass.
