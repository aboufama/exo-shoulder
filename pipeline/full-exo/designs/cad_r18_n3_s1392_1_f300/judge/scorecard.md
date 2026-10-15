# Scorecard: cad_r18_n3_s1392_1_f300

| | requirement | value | target | status | judge |
|---|---|---|---|---|---|
| R1 | Proximity: covered skin 2-14 mm from the metal while following (user 2026-10-15: pass at 14 mm, aim for 10) | 40.9% | >= 0.9 | **FAIL** | full-exo/score_design.py BAND_HI=14 (exact posed skin, 30 fps clips) |
| R1-aim | Aim: the same at 2-10 mm (the 1 cm rule) | 19.1% | >= 0.9 | **FAIL** | full-exo/score_design.py (exact posed skin, 30 fps clips) |
| R2 | No part enters the body, any frame of any clip | 24.87 mm | <= 0.5 mm | **FAIL** | judge/body_contact.py (exact signed distance) |
| R3 | Follows the arm (frames tracked, not held at a limit) | 79.8% | >= 0.95 | **FAIL** | full-exo/score_design.py |
| R4 | Overhead works (Raise overhead clip score) (14 mm band) | 28.9% | >= 0.8 | **FAIL** | full-exo/score_design.py |
| R5 | Shoulder-chain DOF from the scapula base to the arm, counted kinematically (cap 4; the user's scapula handler is a separate part) | 3 | <= 4 | **PASS** | design.json |
| R5-aim | Aim: exactly 3 DOF, the minimum (user 2026-10-15) | 3 | <= 3 | **PASS** | design.json |
| R6 | No interference between parts that move relative to each other | 0.29 mm | <= 0.15 mm | **FAIL** | judge/part_contact.py (geometry only) |
| R7 | Every custom part is one valid closed solid | True | == True | **PASS** | judge/part_validity.py (OCC BRepCheck on the exported STEP) |
| R8 | Custom-part mass budget (user: 500 g for the shoulder) | 233.8 g | <= 500 g | **PASS** | parts_full.json (mesh volume x density) |
| R9 | Strength: SF >= 1.5 at 25 N.m worst direction; deflection and fatigue bounded | - |  | **UNVERIFIED** | independent FEA (CalculiX) - only the in-house hex8 study exists (pipeline/conformal/thin_study) |
| R10 | Base rides the scapula on the user's scapula handler: worst GH-centre misalignment from the handler slipping over the bone (4 mm, confirmed) | 15.21 mm | <= 4.0 mm | **FAIL** | judge/base_mount.py + judge/base_slip.py (girdle mount: literature skin-slip model, central law; acromion-cluster vs bone errors Karduna 2001 / van Andel 2009 / Lempereur 2014, lever from the OpenSim Seth 2016 scapula; docs/research/base_slip_model.md). Thorax mounts keep the three-girdle-law check |
| R11 | Interface pressure, simulation part: worst mean cuff pressure the exo adds (incl. the arm parts' weight) over the MVP1 rolling-bearing cases, within the all-day budget and the ISO/TS 15066 upper-arm limits; the prototype pressure-film check remains | 0.781 kPa | <= 7.5 kPa and ISO/TS 15066 (150 N, 190 N/cm2 at 2x edge peak) == True | **PASS** | judge/dynamics.py (MuJoCo cuff force) -> judge/scorecard.py interface_pressure(): 7.5 kPa = 14 kPa sustained (Kermavnar; Van Vlerken 15 kPa) - 6.5 kPa strap preload; ISO/TS 15066 Annex A Table A.2; then pressure film / FSRs on a prototype |
| R12 | CAD standard: G2 surfaces, flat seats under every seat, no visible screws or seams | - |  | **PARTIAL** | zebra / curvature check (full-exo/parts.html) + user review |
| R13 | Manufacturable | - |  | **NOT DONE** | supplier DFM review + quote (CNC Ti / 7075, SLM AlSi10Mg) |
| R14 | Generalises: holds on motions and body shapes never used to design it | - |  | **NO DATA** | held-out OpenCap / AMASS clips and SMPL-X bodies (data/raw) |
| R15 | Works on real bodies | - |  | **NOT DONE** | printed prototype on the user + one very different body: OpenCap reach vs bare arm, zero skin-contact on FSR strips |
| R16 | Follows the functional everyday workspace (built design: chain closes, no body contact, no part interference) | 46.7% | >= 0.9 | **FAIL** | judge/workspace.py (L1 CAD over the functional workspace poses; user: 90 % range first) |
| R17 | Moves freely unpowered (MVP1): the arm drives the chain through every clip, peak <= 1 N.m about the shoulder, <= 5 N and <= 5 deg at the cuff, no stall, no undriven spare joint | True | == True | **PASS** | judge/dynamics.py (MuJoCo 3.16; rolling bearings mu 0.005; load-dependent friction; validated in judge/test_dynamics.py) |

6 of 19 requirements pass.

Notes:

- R10 (girdle mount, skin slip, central law): low 5.53 / high 23.14 mm; worst frame by elevation {'<= 60': 4.31, '<= 90': 6.78, '<= 100': 7.49, '<= 120': 9.63, '<= 150': 15.21, '<= 180': 15.21} mm; 40 % of frames over 4 mm; design-independent for a spherical chain (docs/research/base_slip_model.md)
- R11 (simulation part): worst 0.781 kPa from the exo (passive|mu0.002|t0.001|s2|hub, incl. 4.26 N of arm parts on 68.0 cm2), 7.281 kPa with the strap vs 14.0 kPa all-day; ISO/TS 15066 5.31 / 150.0 N, edge peak ~1.562 / 1900.0 kPa; aim 4.3 kPa (capillary) met; a plain-bearing build would reach 37.96 kPa; the prototype pressure-film check remains
