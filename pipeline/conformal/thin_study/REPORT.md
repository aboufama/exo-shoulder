# Thinner joints and links: FEA trade study (2026-10-14)

Scope: the v3 joint stack and the Ti-6Al-4V links/bases of band_cad designs 4c_best, 5r_thin and 4r_thin, plus parametric studies of the arm-end neck bracket and the sliding-cuff track. Everything ran on the local CPU with 2 threads. No CAD was modified: the generator was snapshotted to `snapshot/` and re-run read-only.

## 1. Bottom line
1. **The links are already over yield as built at the stated loads, so the link bodies cannot get thinner.**
   - Loads: D1 = 25 N.m joint moment in the worst direction; D2 = 200 N through the shoulder centre.
   - D1 alone gives 920–1150 MPa: a safety factor (SF) of 0.77–0.96 on 7 of 9 sound members. The exceptions are three members with 5.05 mm hubs at both ends, at SF 1.6.
   - At SF 1.5 the built sections carry 13–16 N.m.
   - Body stress scales as t^-1.9 ± 0.1. Link torsional stiffness scales as t^2.6–2.8.
2. **Strength lives in the link body; stack height lives in the washer-seat zones (r ≤ 9.5 mm).**
   - The seat zones run at 0.3–0.6× the body stress at the same thickness.
   - So the stack can drop about 3 mm per joint while the bodies grow about 1.5 mm outside r = 14 mm, where it adds no joint height.
3. **Recommended catalogued stack: 10.57 mm (10.07 with a 2.0 mm cap), down from 13.07.**
   - Lower plate 3.0 mm under the seat.
   - 2× igus GTM-1018-005 (0.5 mm) washers.
   - Upper hub 4.05 mm with an igus GSM-1012-04 sleeve.
   - 0.02 mm float and a 2.5 mm cap.
   - If the joint moment is ≤ 14 N.m: 8.57 mm (2.5 / 0.5 / 3.05 / 0.5 / 2.0).
4. **Six of ten built links have CAD defects** (section 6).
5. **Sliding cuff:** the MR84 wheel bearings (C0r 139 N) would see about 600 N each at 25 N.m.

## 2. Method
- **Geometry**
  - `link_geom.py` captures the generator's section parameters by monkey-patching its section builder and loft.
  - Each part is meshed as an O-grid hex mesh around each pin, plus a section stack along the ribbon.
  - The contoured skin side and approximate G2 edge rounds are kept.
  - Thickness variants come from the generator's own `T_LINK`, `T_LO`/`STACK`, `T_SEAT` and `T_W`.
  - Mesh volume matches BREP volume by sector to 1–3% where the BREP is sound.
- **Element** (`fe_core.py`): hex8 with incompatible modes, 4 layers through the thickness.
  - Against beam theory: bending stress within 0.0%, stiffness within 1%, torsion stress within 1–3%.
  - Torsional stiffness comes out 7% stiff because the ends are warping-restrained.
  - The old `fea_link.py` hex8 over-stiffens bending; it was not reused.
- **Joints** (`joint_model.py`), modelled as built:
  - iglidur washers and sleeve are elastic layers (E 7.8 GPa / t) to a rigid pin.
  - Lower hubs: the integral pin column is tied to the pin. The washer-B/cap path gets washer A's stiffness, so the tilt couple splits 50/50 as in a no-preload duplex.
  - Hub A is held through bonded washers (cantilever). Hub B is loaded through its own joint. No rigid inserts or point loads.
- **Loads**
  - D1 = 25 N.m, worst direction perpendicular to the joint axis.
  - D2 = 200 N through the shoulder centre, worst direction (11–18 N.m at the hubs).
  - "D1+D2" = pointwise von Mises sum, a conservative bound.
- **Stress reporting** (nodal-averaged von Mises):
  - Zones: body (r > 9.5 mm plus ribbon), seat (r ≤ 9.5), and the pin-root ring.
  - The pin-root ring starts 0.67 mm off the tied pin edge; the re-entrant corner itself is excluded.
  - Excluded zones: base bolt patches (4.5 mm), neck/track clamp edge (1.5 mm), and the wheel patches.
- **Allowables:** yield 880 MPa; about 500 MPa smooth endurance (≈0.85× when machined; Kf ≈ Kt).
  - M@1.5 = the moment at SF 1.5.
  - inf-life = the fully reversed moment at 500 MPa.

## 3. As built (ribbon 4.0, lower plate 3.5, upper hub 5.05)

| part | hubs | D1 body MPa | SF D1 | D1+D2 | SF | seat D1 | k soft/stiff N.m/deg | M@1.5 | g |
|---|---|---|---|---|---|---|---|---|---|
| 4c base | up 5.05 | 548 | 1.61 | 862 | 1.02 | 333 | 17.9/23.1 | 26.8 | 17.0* |
| 4c link 1 | low 3.5/up 5.05 | 984 | 0.89 | 1515 | 0.58 | 336 | 11.0/18.7 | 14.9 | 43.7 |
| 4c link 2 | low/low | 1147 | 0.77 | 1807 | 0.49 | 376 | 2.37/5.74 | 12.8 | 47.4 |
| 4c link 3 | up/up | 15984 (defect 6.3) | – | – | – | 404 | 0.66 | – | 18.7 |
| 5r base | low 3.5 | 1120 | 0.79 | 1630 | 0.54 | 732 | 7.3/10.9 | 13.1 | 15.8* |
| 5r link 1 | up/up | 1036 | 0.85 | 1580 | 0.56 | 341 | 9.4/22.2 | 14.2 | 22.9 (neck) |
| 5r link 2 | low/low | 1752 (p99.5 1133, step) | 0.50 | 2723 | 0.32 | 549 | 4.5/9.9 | 8.4 | 33.7 |
| 5r link 3 | up/low | 916 | 0.96 | 1455 | 0.60 | 325 | 9.2/15.1 | 16.0 | 29.3 |
| 5r link 4 | up/up | 987 (ramp; hubs 653) | 0.89 | 1657 | 0.53 | 341 | 6.0/13.2 | 14.9 | 26.4 |
| 4r base | low 3.5 | 1120 | 0.79 | 1680 | 0.52 | 733 | 7.4/11.0 | 13.1 | 17.0* |
| 4r link 1 | up/up | 534 | 1.65 | 822 | 1.07 | 328 | 12.9/20.6 | 27.5 | 18.8 (neck) |
| 4r link 2 | low/low | 2225 (p99.5 1060, step) | 0.40 | 3323 | 0.26 | 576 | 2.2/6.2 | 6.6 | 48.0 |
| 4r link 3 | up/up | 529 | 1.66 | 869 | 1.01 | 325 | 11.1/16.9 | 27.7 | 23.3 |

Notes on the table:
- Mass is BREP mass including the integral pins; \* = mesh mass.
- Peaks are at the G2 waist of the 3.5 mm lower-hub stub (r ≈ 15–17 mm) or at the plate-to-ribbon step.
- D2 alone gives SF 1.3–1.7, except the long low/low links at 0.8–1.3.
- No link reaches infinite life at 25 N.m; infinite-life moments are 6–24 N.m.

## 4. Trade curves (ribbon = lower plate = t, upper hub = t + 0.05, 0.5 mm washers)

D1 body stress in MPa, with (SF, k soft) and mesh mass.

| t | 4c link 2 (long, 63°) | 4c link 1 | 5r link 3 | 5r base | 4c base |
|---|---|---|---|---|---|
| 2.5 | 2181 (0.40, 0.77) 32 g | 2455 (0.36, 2.6) 22 g | 2243 (0.39, 2.2) 18 g | 2274 (0.39, 2.9) 11 g | 2252 (0.39, 3.0) 9 g |
| 3.0 | 1541 (0.57, 1.30) 37 g | 1685 (0.52, 4.2) 24 g | 1550 (0.57, 3.5) 21 g | 1528 (0.58, 4.9) 13 g | 1493 (0.59, 4.9) 10 g |
| 3.5 | 1152 (0.76, 2.0) 41 g | 1262 (0.70, 6.3) 27 g | 1145 (0.77, 5.3) 24 g | 1118 (0.79, 7.4) 15 g | 1117 (0.79, 7.3) 12 g |
| 4.0 | 896 (0.98, 2.9) 45 g | 978 (0.90, 8.7) 30 g | 877 (1.00, 7.5) 27 g | 844 (1.04, 10.7) 17 g | 854 (1.03, 10.3) 14 g |
| 5.0 | 626 (1.41, 5.4) 54 g | 644 (1.37, 14.9) 35 g | 577 (1.52, 13.3) 33 g | 527 (1.67, 19.8) 21 g | 545 (1.62, 18.4) 17 g |
| 6.0 | 514 (1.71, 8.9) 63 g | 454 (1.94, 23.1) 41 g | 413 (2.13, 21.0) 39 g | 361 (2.44, 32.3) 25 g | 386 (2.28, 29.3) 20 g |

From the power fits, the body thickness needed:
- **SF 1.5 under D1:** 4.8–5.3 mm.
- **SF 1.2 under D1+D2:** 5.1–6.0 mm.
- **Infinite life at 25 N.m:** 5.1–5.9 mm.

Width lever (4c link 2, 18 mm strip):
- At 4.0 mm: 732 MPa (SF 1.20), k 3.7 N.m/deg, 50 g.
- Compare 5.0 mm × 14 mm: 626 MPa, k 5.4, 54 g.

Seat zones vs their own thickness (D1, MPa):

| t | lower-hub pin-root ring (links) | upper hub (t + 0.05) | base seat |
|---|---|---|---|
| 2.5 | 504 (SF 1.75) | 1316–1462 | 1442 |
| 3.0 | 420 (SF 2.10) | 830–1002 | 988 |
| 3.5 | 354 | 614–730 | 725 |
| 4.0 | 301 | 481–555 (SF 1.6–1.8) | 556 |
| 5.0 | 225 | 317–353 | 381 |

Caveat on the lower-hub column: the pin's compression-only pull (2.2 kN) adds about 60–120 MPa analytically at 2.5–3.0 mm.

## 5. Recommendations (25 N.m at SF ≥ 1.5)

| part / zone | now | recommended | SF D1 / D1+D2 | stiffness | note |
|---|---|---|---|---|---|
| link body outside r = 14 mm (14 mm strip) | 4.0/3.5 | **5.5** (18 mm strip: 4.5) | ≥ 1.5 / 1.0–1.1 | long link k ≈ 7 (now 2.4) | raised stubs; adds no stack height |
| lower plate under the seat | 3.5 | **3.0** (2.5 if ≤ 20 N.m) | 2.1 / 1.4 | – | −0.5 mm |
| upper hub | 5.05 | **4.05** (GSM-1012-04) | 1.6 / ~1.0 | – | −1.0 mm; 3.05 only at ≤ 14 N.m |
| scapula base | 3.5 | seat 4.0, waist 5.0 | 1.5 / 1.0 | 18–20 | – |
| neck bracket (30 mm wide, 50–90 mm span) | 6.5 | **4.5** | 2.8 / 1.6–1.7 | 11 / 7.5 / 5.6 at 50/70/90 mm | 5.5 if ≥ 10 N.m/deg wanted at 90 mm; −22 g at 70 mm |
| track keel (8 mm wide) | 4 mm V-head | **total depth ≥ 10**, Ti or 17-4PH | Ti 2.4–2.6 / 1.47–1.58 | 12–20 | head alone SF 0.45; 17-4PH works at D 7 (SF 1.4); 7075 needs D 19 |

**Stack:** 3.0 + 0.5 + 4.05 + 0.5 + 0.02 + 2.5 = **10.57 mm**, or **10.07 mm** with a 2.0 mm cap.
- Hardware tilt stiffness rises from 199 to 267 N.m/deg with the 0.5 mm washers, which is negligible next to the links.
- Hardware mass saved: about 4.3 g per joint (17–21 g per design).
- Strong bodies add 7–15 g per long link, so **net mass rises at 25 N.m.** At the as-built mass the allowable is about 13–16 N.m.

Other hardware:
- **Screw:** the washer-B couple pulls the cap with 2.2 kN at 25 N.m. A2-70 M4 yields at 3.95 kN (preload marginal); A2-50 ULP yields at 1.84 kN. Use 10.9/12.9 steel.
- **Cap** (dome-profile FE): 261/271 MPa for the 2.5/2.0 mm cap, 456/518 at the clamp edge. Cap height is set by the screw head, not strength.
- **Pin root** (Ø9.2 relief, M4 tap, Kt ≈ 2.2): 448 MPa peak, SF 2.0 static, fatigue SF about 1.1.
- **Ø8 pin:** not useful. No stack gain (shortest sleeve 5 mm), washer edge pressure 82 MPa against an 80 MPa rating, pin-root peak 851 MPa.

## 6. CAD defects in band_cad
1. **Short links with non-overlapping hubs.**
   - Affected: 5r link 1 and 4r link 1 (centre distances 32.9 and 33.3).
   - Cause: `build_link_short` uses a union of the two discs only; at O26 these discs do not touch, so the sections fall back to 2 × 0.8 mm.
   - Result: a 1.6 mm neck, confirmed by BREP sector volumes. 4c link 3 has a 6.5 mm neck.
   - Fix: smooth union with the 14 mm strip.
2. **Folded long links.**
   - Affected: 4c link 1, 5r link 3, 4r link 3 (34–40 mm centre distance).
   - Cause: `sA > sB`, so the ribbon runs backwards.
   - Result: 25–55% of the mid-section is missing in the BREP.
   - Fix: use the blended (short) builder when `sA > sB − margin`.
3. **4c link 3 is a step, not a link.** The hub planes are 17 mm apart at a 25 mm centre distance, giving a ~76° wall about 1.2 mm thick. It needs a raised J4 boss or different joint placement.
4. **Plate-to-ribbon steps.** Up to 8.5 mm (5r link 4) and 2–3 mm in the long links. Ramp at ≤ 30° over ≥ 10 mm with sections normal to the path.
5. **Abrupt contour fade.** The contour fades only laterally, leaving near-vertical steps at the disc front and back.

## 7. Hardware options (per Ø10 joint)

| option | part | t | rating | mm saved | g saved | risk | verified |
|---|---|---|---|---|---|---|---|
| 0.5 mm thrust washers ×2 | igus GTM-1018-005 | 0.5 | 80 MPa; edge 48 MPa at 25 N.m | 1.0 | 0.3 | half the wear allowance | yes |
| 4 mm sleeve | igus GSM-1012-04 | 10/12 × 4 | 5 MPa | 1.0 | 1.9 | seat 555 MPa | yes |
| 3 mm sleeve | igus GSM-1012-03 | 10/12 × 3 | 6.7 MPa | 2.0 | 3.8 | ≤ 14 N.m only | yes |
| lower plate 3.0 (2.5) | machining | – | 420 (504) MPa | 0.5 (1.0) | 1 (2) | thick stub needed | FE |
| 2.0 mm cap | M4 ULP, 1.5 mm head (Fastenright, 10.9 offered) | 2.0 | 271/518 MPa | 0.5 | 0.4 | head strength unrated | head height **not verified** |
| retaining ring | Rotor Clip DSH-10 (DIN 471-10) | 1.1 groove + 0.6 | ring 4.0 kN; groove 1.0/2.4 kN (soft steel) | 0.8 | 2 | 0.10–0.16 mm lash | yes |
| E-clip | DE-8 | 1.0 | groove 1.25–1.42 kN | – | – | too weak | yes |
| spiral ring | Smalley / McMaster | – | no metric 8–10 mm size | – | – | – | yes |
| PTFE-fabric liner | Kaman KAron B/V | 0.25–0.38 | 207–551 MPa | ≈0.25/face | 0.2 | custom; hard counterface needed | **no** |
| GGB DU | WC08DU (10/20/1.5) | 1.5 | 250 MPa | none | – | thicker | yes |
| DLC counterface | Oerlikon BALINIT | 1–5 µm | 1500–2500 HV | 0 | – | eggshell on Ti | yes |
| nitriding / Nedox | – | – | – | – | – | 720–854 °C process; HCF loss; Nedox does not list Ti | partly |
| needle thrust | AXK1024 + 2× AS1024 | 4.0/side | 26 kN | −6.0 | −5 | taller | yes |
| cuff wheel bearing | NSK MR84ZZ | – | C0r 139 N vs ~600 N per wheel | – | – | brinelling | yes |

## 8. Files and limits
- **Scripts:** `fe_core.py`, `fe_validate.py`, `link_geom.py`, `joint_model.py`, `run_links.py`, `joint_hw.py`, `bracket_track.py`, `make_results.py`.
- **Data:** `links_fea.json`, `bracket_track.json`, `joint_hw.json`, `validate.json`, `results.json` (everything plus fits and recommendations), `tables.txt`.
- **Not done:**
  - Contact non-linearity (washers are linear, split fixed at 50/50).
  - Real neck and track CAD.
  - Bolt and lap checks of the neck on the aluminium bar.