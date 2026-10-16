# Scorecard: user_osn_k4216

| | requirement | value | target | status | judge |
|---|---|---|---|---|---|
| R1 | Proximity: covered skin 2-14 mm from the metal while following (user 2026-10-15: pass at 14 mm, aim for 10) | 49.0% | >= 0.9 | **FAIL** | full-exo/score_design.py BAND_HI=14 (exact posed skin, 30 fps clips) |
| R1-aim | Aim: the same at 2-10 mm (the 1 cm rule) | 22.3% | >= 0.9 | **FAIL** | full-exo/score_design.py (exact posed skin, 30 fps clips) |
| R2 | No part enters the body, any frame of any clip | 24.94 mm | <= 0.5 mm | **FAIL** | judge/body_contact.py (exact signed distance) |
| R3 | Follows the arm (frames tracked, not held at a limit) | 90.9% | >= 0.95 | **FAIL** | full-exo/score_design.py |
| R4 | Overhead works (Raise overhead clip score) (14 mm band) | 24.6% | >= 0.8 | **FAIL** | full-exo/score_design.py |
| R5 | Shoulder-chain DOF from the scapula base to the arm, counted kinematically (cap 4; the user's scapula handler is a separate part) | 3 | <= 4 | **PASS** | design.json |
| R5-aim | Aim: exactly 3 DOF, the minimum (user 2026-10-15) | 3 | <= 3 | **PASS** | design.json |
| R6 | No interference between parts that move relative to each other | 0.85 mm | <= 0.15 mm | **FAIL** | judge/part_contact.py (geometry only) |
| R7 | Every custom part is one valid closed solid | - | == True | **NOT RUN** | judge/part_validity.py (OCC BRepCheck on the exported STEP) |
| R8 | Custom-part mass budget (user: 500 g for the shoulder) | 240.2 g | <= 500 g | **PASS** | parts_full.json (mesh volume x density) |
| R9 | Strength at the MVP2 design load (arm gravity support + margin: 10 N.m about GH from a 50 N cuff force at 200 mm, worst direction; was 25 N.m): min yield SF over the load-path parts; fatigue (Goodman, 1e7 cycles, fully reversed) and chain deflection (sum of the parts' GH-point motion) within the 2 mm floor and the min skin gap | - | >= 1.5 SF and fatigue SF >= 1.0 and deflection within the floor == True and every load-path part analysed == True and joint hardware at the D1F tilt (bearing static s0 >= 1, pin / threads SF >= 1.5) == True and fall on the elbow (2 x D1F) below fracture >= 1.0 | **NOT RUN** | judge/fea.py (CalculiX 2.21 C3D10 on gmsh tet10 of the STEP parts, validated on a cantilever and a thick ring within 2 %: judge/fea_validation.json; t/2 + t/3 mesh-convergence pair per part; red team: worst direction, overhead, 2x fall, smallest section, joint bearings / pin / threads (hand calcs on the FE wrench); sizing by re-solving the mapped mesh: judge/fea_sizing.py) |
| R10 | Base rides the scapula on the user's scapula handler: worst GH-centre misalignment from the handler slipping over the bone (4 mm, confirmed) | - | <= 4.0 mm | **NOT RUN** | judge/base_mount.py + judge/base_slip.py (girdle mount: literature skin-slip model, central law; acromion-cluster vs bone errors Karduna 2001 / van Andel 2009 / Lempereur 2014, lever from the OpenSim Seth 2016 scapula; docs/research/base_slip_model.md). Thorax mounts keep the three-girdle-law check |
| R11 | Interface pressure, simulation part: worst mean cuff pressure the exo adds (incl. the arm parts' weight) over the MVP1 rolling-bearing cases, within the all-day budget and the ISO/TS 15066 upper-arm limits; the prototype pressure-film check remains | 0.921 kPa | <= 7.5 kPa and ISO/TS 15066 (150 N, 190 N/cm2 at 2x edge peak) == True | **PASS** | judge/dynamics.py (MuJoCo cuff force) -> judge/scorecard.py interface_pressure(): 7.5 kPa = 14 kPa sustained (Kermavnar; Van Vlerken 15 kPa) - 6.5 kPa strap preload; ISO/TS 15066 Annex A Table A.2; then pressure film / FSRs on a prototype |
| R12 | CAD standard: G2 surfaces, flat seats under every seat, no visible screws or seams | - |  | **PARTIAL** | zebra / curvature check (full-exo/parts.html) + user review |
| R13 | Manufacturable | - |  | **NOT DONE** | supplier DFM review + quote (CNC Ti / 7075, SLM AlSi10Mg) |
| R14 | Generalises: holds on motions and body shapes never used to design it | - |  | **NO DATA** | held-out OpenCap / AMASS clips and SMPL-X bodies (data/raw) |
| R15 | Works on real bodies | - |  | **NOT DONE** | printed prototype on the user + one very different body: OpenCap reach vs bare arm, zero skin-contact on FSR strips |
| R16 | Follows the functional everyday workspace (built design: chain closes, no body contact, no part interference) | 55.8% | >= 0.9 | **FAIL** | judge/workspace.py (L1 CAD over the functional workspace poses; user: 90 % range first) |
| R17 | Moves freely unpowered (MVP1): the arm drives the chain through every clip, peak <= 1 N.m about the shoulder, <= 5 N and <= 5 deg at the cuff, no stall, no undriven spare joint | False | == True | **FAIL** | judge/dynamics.py (MuJoCo 3.16; rolling bearings mu 0.005; load-dependent friction; validated in judge/test_dynamics.py) |

4 of 19 requirements pass.

Notes:

- R2 (rig body): this project's parts 24.94 mm, the user's own arm parts 24.87 mm; beyond the rig's own self-intersection (judge/body_regions.py): ours 7.55 mm (H|UPPER ARM CUFF (lines and arcs: flat land + inner R arc + outer arc, extruded; AlSi10Mg bead blasted)), the user's 24.0 mm (F|FOREARM CUFF)
- R11 (simulation part): worst 0.921 kPa from the exo (passive|mu0.002|t0.001|s2|hub, incl. 1.66 N of arm parts on 68.0 cm2), 7.421 kPa with the strap vs 14.0 kPa all-day; ISO/TS 15066 6.26 / 150.0 N, edge peak ~1.842 / 1900.0 kPa; aim 4.3 kPa (capillary) met; a plain-bearing build would reach 88.38 kPa; the prototype pressure-film check remains
