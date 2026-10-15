# Ring and shell hardware: humeral-rotation C-rail and nested-shell 2R hubs

Research note, 2026-10-14. Desk study of catalogues, datasheets and papers; no CAD or software was downloaded.
Every dimension and rating has a source tag ([S..], [E..], [P..], [R..]; list at the end). Numbers marked **est.** are
mine, with the calculation shown in section 1 or next to them. Everything else is quoted from the source. Where I could
only read a search-engine excerpt of a source (page blocked or PDF unreadable), the tag carries "(excerpt)".

Mechanism studied (from the brief and the repo):
- 2R pointing chain over the shoulder cap. Links are nested Ti-6Al-4V shells with 5.5 mm sections for 25 N.m at
  SF 1.5 [R2]. The v4 joint stack is 10.47 mm above the lower member's skin face [R1].
- Humeral rotation as a separate joint down the upper arm, on an open C-rail about the humerus axis.
  - Travel 120-160 deg; rail centreline radius 45-65 mm.
  - Radial budget: 10 mm target, 14 mm maximum, from skin to the outside of rail + carriage, including 2 mm clearance.
- Today's arm end [R3]:
  - V-wheel concept: Ø12 PEEK wheels on MR63ZZ, 13 mm wheel spacing along the arc, wheels at ±10.5 mm across the track.
  - Dovetail alternative: Ti rail ≥ 10 mm deep with a 26 x 18 saddle on 0.5 mm iglidur J liners.

---

## 0. Bottom line

1. **No catalogue curved guide fits.** Each one fails on at least one of three things: rail radius (THK HCR ≥ 100 mm,
   Rollon ≥ 120 mm, igus drylin W ≥ 75-100 mm), stack height (THK 18 mm, Hepco 17.7 mm), or moment capacity (Hepco R12:
   1.25 N.m against the 25 N.m needed).
   - The two families that do come at 45-65 mm radius are closed rings: Franke wire-race elements (5.9 x 5.9 mm) and
     Kaydon/RBC thin sections (6.35 mm).
   - The Hepco R12-93 flat ring is the exception, but it is the wrong orientation for this envelope (section 1.4).
2. **What decides the humeral joint is the wheelbase and the friction, not the catalogue.**
   - A 25 N.m moment on today's 13 mm x 12-21 mm carriage gives about 0.5-2 kN per contact, which matches the in-house
     ~600 N per wheel [R2].
   - V-wheels with radial axes take the roll moment **along their own axis**, which is their weak direction.
   - A plain liner reacting 25 N.m over a 24 mm rail width makes **about 7-31 N.m of friction torque** about the humeral
     axis (est.). That is as large as the load itself.
3. **The open rail is a curved cantilever, and it governs stiffness.**
   - A 24 x 4 mm Ti band carries 25 N.m at SF 1.5 but twists about 5 deg over 75 mm of arc (est.).
   - A hollow 26 x 6 mm Ti band (1.2 mm wall) twists about 2 deg at 45 g per 150 deg (est.).
4. **Recommended humeral joint, in order:**
   - **A** (if the ring must carry a real 25 N.m): custom caged-ball wire-race C-slide, about 10 mm stack, ~90 g at 150 deg.
   - **B** (if the carriage is the cuff, so the ring mainly carries a ~125-250 N force): plain iglidur C-band slide with a
     long shoe, 8.5-10.5 mm stack, ~75-90 g.
   - **C** (only up to about 20 N.m roll): long-wheelbase V-wheel carriage, about 10.4 mm stack, ~140 g.
5. **2R hubs:** the v4 plain hub (10.47 mm) is the thinnest proven stack. It pays an estimated **2.5-4.8 N.m friction
   torque** under a 25 N.m tilt (est.).
   - A 3/16 in four-point-contact thin section (Kaydon/RBC KAA15XL0: 38.1 x 47.6 x 4.76 mm, 18 g, 40 N.m static moment)
     or an IKO CRBT305A crossed-roller ring (30 x 41 x 5 mm, 20.7 g) fits in about **9 mm** (est.) with ~0.1 N.m friction.
   - The price is a Ø50 mm hub boss.
6. **Shell-on-shell spherical sliding** is a known principle: spherical plain bearings, hemispherical air bearings, and
   circular-arc RCM guides in surgical robots. It only works here if **the J1 and J2 axes intersect at the shell centre**.
   - Under a tilting moment the friction torque is about (4/π)·μ·M at any radius (est.), so a liner never beats rolling on
     friction.
   - Use it, if at all, as spherical **pads** at the overlap, not as two full conformal shells: the links follow the
     skin, so they are not spheres.

---

## 1. Loads and the physics of an open C-rail (all est., shown so they can be checked)

Design moment M = 25 N.m about an axis perpendicular to the humerus (brief). At the carriage, M splits into two parts:
- **Roll** about the local rail tangent. It is reacted by radial forces across the rail's axial width b.
- **Yaw** about the local radial direction. It is reacted by axial (along-the-arm) forces across the carriage's arc
  chord L.

The component about the humerus axis is the free DOF. Width along the arm and length along the arc cost no radial stack;
radial thickness is the only scarce dimension. **So make b and L large.**

### 1.1 Contact forces

| case | geometry | force | compare |
|---|---|---|---|
| roll, edge pair | b = 12 / 24 / 30 / 40 mm | M/b = 2083 / 1042 / 833 / 625 N per edge | |
| yaw, end pair | L = 13 / 26 / 40 / 58 mm | M/L = 1923 / 962 / 625 / 431 N | |
| V-wheels with radial axes, roll | b = 21, 2 wheels per side (today) | **595 N along the wheel axis** | DualVee size 0: axial working load L_A = 123 N [S4]; in-house ~600 N [R2] |
| same | b = 24, 4 per side / b = 40, 4 per side | 260 / 156 N along the wheel axis | → allowable roll ≈ 123 N x 40 mm x 4 ≈ **20 N.m** at b = 40 |
| V-wheels, yaw | L = 40 / 58 mm | 625 / 431 N in the wheel's radial direction | DualVee size 0: radial working load L_R = 650 N [S4] |

### 1.2 Plain liners: pressure

Linear pressure across the width gives p_max ≈ 6M/(L·b²) for roll. For yaw, the line load is q ≈ 6M/L² on a lip of
height h.

| shoe L x b | roll p_max | yaw (lip h) | iglidur J limit |
|---|---|---|---|
| 26 x 12 (today's dovetail saddle) | **40 MPa** | 74 MPa (h = 3) | 35 MPa [S13] |
| 58 x 24 (60 deg shoe at R55) | 4.5 MPa | 22 MPa (h = 2), 15 MPa (h = 3) | 35 MPa |
| 90 x 30 | 1.9 MPa | 9 MPa (h = 2) | 35 MPa |

So **today's 26 mm saddle is at or over the iglidur J limit at 25 N.m**. A 60 deg shoe is comfortable on pressure.

### 1.3 Friction torque about the humerus axis (the real problem for plain bearings)

The total normal load needed to react roll is N ≈ 2M/b (edge-concentrated) to 3M/b (linear). The friction torque is
μ·N·R, with R = 55 mm.

| b | iglidur, μ 0.06-0.18 (J vs steel [S13]) | rolling, μ 0.002-0.005 (est.: Koyo lists 0.0010-0.0020 for ball bearings [S17], doubled for 4-point/seal drag) |
|---|---|---|
| 24 mm | **6.9-31 N.m** | 0.2-0.9 N.m |
| 30 mm | 5.5-25 N.m | 0.2-0.7 N.m |

If instead the carriage *is* the cuff, the ring mostly carries the cuff force F ≈ 25 N.m / d. For d = 100-200 mm that is
F = 250-125 N, and a plain liner gives μ·F·R ≈ 1.0-2.1 N.m at μ = 0.15 (est.), which is acceptable. **The real moment at
the ring decides between rolling and plain.** That moment should come from the R10 base-mount / OpenSim load case, not
from the 25 N.m placeholder.

Side note: a force at the carriage with a component tangent to the rail is a torque about the humerus axis. A passive
humeral joint passes that torque to the user's rotator cuff.

### 1.4 Why the flat-ring products (Hepco PRT) do not fit

A PRT ring is a flat washer with V-edges on its inner and outer rims [S3]. Mounted coaxial with the humerus, its 12.4 mm
V-to-V width becomes *radial*, and it needs a bearing on both rims (Ø12.7 each). The radial stack is then about
12.7 + 12.4 + 12.7 ≈ 38 mm (est.).

The usable orientation for this envelope is the **cylindrical band**: a band that is wide along the arm, with guide
features at its two axial edges. Today's V-track [R3] and every recommendation below use it.

### 1.5 The rail as a curved cantilever (strength and twist)

A pure moment passes along a curved beam unchanged as a vector, so the band section between the rail's mount and the
carriage carries the full 25 N.m as bending plus torsion.

Allowables for Ti-6Al-4V (σy 880 MPa assumed, SF 1.5; G 44 GPa): σ = 587 MPa, τ = 339 MPa. Rectangular torsion factors
are from Roark. Twist is computed over 75 mm of arc.

| band (axial x radial) | weak-axis bending allowable | torsion allowable | twist at 25 N.m | mass per 150 deg at R55 |
|---|---|---|---|---|
| 24 x 3 solid | 21 N.m (fails) | 22 N.m (fails) | 12 deg | 46 g |
| 24 x 4 solid | 38 N.m | 39 N.m | **5.3 deg** | 61 g |
| 24 x 6 solid | 85 N.m | 83 N.m | 1.7 deg | 92 g |
| **26 x 6 hollow, 1.2 wall (SLM Ti)** | ≈ 73 N.m | 97 N.m | **2.1 deg** | **45 g** |

Ways to stiffen it:
- Use a closed (hollow) section.
- Fix the rail to link 2 at its middle, so the worst arm is half the arc.
- Better still, fix it at both ends so rail + link form a closed loop.

The in-house FEA asks for a Ti keel ≥ 10 mm deep for the narrow 8 mm keel [R2]. A wider, hollow band is the
lower-profile way to the same stiffness, but it needs its own FE run.

### 1.6 Arc bookkeeping

- With a short carriage on a long rail, the rail arc is the travel plus the carriage arc. For example, 150 + 60 = 210 deg;
  the opening is 150 deg, a chord of 106 mm at R55.
- Put the **long member on link 2** (exo side). Its opening then keeps a fixed direction relative to the torso while the
  short arm-side carriage turns with the humerus.
- With a caged rolling segment, the cage moves at half speed. Each raceway must therefore be at least the cage arc plus
  half the travel, and cage creep must be controlled, e.g. with IKO's rack-and-pinion anti-creep cage [S16].

---

## 2. Q1 - open curved-rail and partial-ring options

| option | smallest rail radius | section (height x width) | carriage | rated loads / moments | mass | material | open 120-160 deg arc? | friction / play | fits? |
|---|---|---|---|---|---|---|---|---|---|
| **THK HCR12A+60/100R** curved profile rail [S1, S2] | R 100 mm (smallest listed size-12 radius; "other radii available" [S1]) | total height M 18; rail W1 12 x M1 11; block width W 39 | L 44.6 mm | C 4.7 kN, C0 8.53 kN; MA = MB 40.9 N.m (1 block), 228 N.m (2 blocks in contact); MC 44.5 N.m | rail 0.83 kg/m (217 g per 150 deg at R100, est.); block 0.08 kg | bearing steel | rail made up to 60 deg (θ column [S1], my reading); longer arcs are jointed (CADEN-7 used 3 x 60 deg [E1]) | rolling; normal or light preload C1 [S1] | no: R ≥ 100 and 18 mm tall |
| **Hepco PRT R12-93 / R12-127** ring + FCP-12 carriage [S3] | **R 46.5 / 63.5 mm** (Ø93 / 127 hole circle) | flat ring 7.7 thick; V-apex width 12.37 (Ø80.63/105.37); assembled height 17.67 (dimension E, my reading of the drawing) | FCP-12-93 plate 55 x 40, 70 g; RSJ-13 bearings Ø12.7 | lubricated: L1 = L2 = 120 N, M = Mv = **1.25 N.m**, Ms 0.6 N.m; dry: 80 N, 0.8 / 0.4 N.m | ring 0.16 kg per 360 deg (67 g per 150 deg) | steel, zone-hardened V edges | stock 90 and 180 deg segments, any length to order [S3] | rolling; "zero play", eccentric adjustment [S3] | no: moment 20x too low; flat-ring orientation (1.4) |
| **Bishop-Wisecarver** DualVee / MinVee [S4] | curved: large-diameter ring guides only [S4]; MinVee track is straight | DualVee size 0 wheel Ø14.83 x 6.35, bore 4.0; MinVee assembled height 20.02 | MinVee plate 44.45 x 50.8 | size 0 wheel: L_R 650 N, L_A 123 N (working); MinVee steel: MP 7.9, MY 8.6, MR 6.2 N.m; L_A 540, L_R 490 N | wheel 5.1 g; MinVee 72-84 g | 52100 / 440C steel | no small curved track | rolling, eccentric preload | wheels only, as parts of option C |
| **igus drylin W curved** (size 06) [S5] | R 100 mm (75 mm concave/convex) | not on page | WWBCX-06-20-04, 3-point carriage | not on page | - | aluminium rail, iglidur sliders | semicircle available [S5] | plain; adjustable bearing points | no: radius |
| **Rollon Curviline** CKR/CVR 01-05 [S6] (excerpt) | R 120 mm, both sizes | rail width 16.5 (01) / 23 (05) | - | not found | - | steel | custom radii, standard segments | rolling | no: radius |
| **LM76** | no curved or ring product found | - | - | - | - | - | - | - | not found |
| **Franke LEL 1.5 wire-race element** [S7] | KK 70 mm (R 35 ball circle) to 150; KK 90 / 110 / 130 = R 45 / 55 / 65 | **5.9 x 5.9 mm** element (mounting space 5.9-20.9 across the LEL range) | sits in the customer's housing | KK 110: C0a 21, C0r 10, Ca 9, Cr 8 kN, **C0m 0.6 kN.m**; KK 90: C0m 0.4 kN.m | 0.04 kg (KK 90-110) | hardened steel wires, plastic cage | catalogued as full rings; open segments not catalogued (ask Franke) | rolling, "preloaded free from clearance" [S7] | closed as sold; basis for option A |
| **Kaydon / RBC Reali-Slim** thin section (closed) [S8, S9] | bore 101.6 (R 50.8) for KA040XP0; 3/16 in KAA section only up to 1.5 in bore | KA040XP0: 101.6 x 114.3 x **6.35** | - | static moment **310 N.m** (2740 lbf-in), dynamic 150 N.m; radial static 5.74 kN | 86 g | 52100 | **closed**: the arm must thread through; excluded by the open-ring rule | rolling, 4-point contact | benchmark only |
| **THK RAU 9008 / 11008** crossed roller (closed) [S10] | bore 90 / 110 | 8 mm wide, 16 mm section | - | C0 12.4 / 15 kN | 0.12 / 0.15 kg | steel | closed | rolling | benchmark only |
| **Custom V-wheel on a Ti / 17-4PH rail** (today's concept) [R3] | any (machined) | today: wheels Ø12 x 4 PEEK, rail head 12 wide | 13 mm wheelbase | ~600 N per wheel at 25 N.m against MR84 C0r 139 N [R2] | - | Ti rail (a poor rolling raceway; needs hardened inserts) | yes, machinable | rolling, eccentric bush | only with a long wheelbase and steel races (option C) |
| **Plain iglidur dovetail / C-band slide** (today's saddle) [R3] | any (machined) | dovetail 6 mm top half-width, 3 mm flank, 0.5 mm liners | 26 x 18 saddle | iglidur J 35 MPa, μ 0.06-0.18 vs steel, pv 0.34 MPa·m/s [S13] | - | Ti rail, liner J | yes | plain; gib preload; friction 1.3 | yes with a long shoe (option B) |

---

## 3. Q2 - how rehab and assistive exoskeletons do humeral (and forearm) rotation

| device | humeral-rotation solution | published numbers | note for us |
|---|---|---|---|
| **CADEN-7** (Perry, Rosen, Burns 2007) [E1] | "semicircular bearing design to allow users to don the device without strain"; "semicircular guides composed of three 60° curved rail bearing segments (THK)". The track is fixed to the proximal link: the paper's Fig. 3(b) "partial bearing where the bearing track is affixed to the proximal exoskeleton link" | links 2-7 weigh 6.3 kg; link 1 weighs 3.5 kg | the closest match to the user's idea. THK's 60 deg per-rail limit at R100 [S1] fits the 3 x 60 deg layout (my inference) |
| **Harmony** (Kim and Deshpande 2017) [E2] | GH as a 3R spherical chain. For axial rotation they reject curved rails: "this bearing is generally bulky and heavy, and could possibly restrict the ROM of the arm … close to the torso". Forearm: parallelogram + 1:1 timing belt | - | IKO crossed-roller (CRBH/CRBF) use is reported by IKO (excerpt only, **unverified**) [E10] |
| **MGA** (Carignan et al. 2005) [E3] | humeral rotation is the 3rd revolute of the GH triad: "A 'C'-shaped linkage fits over the upper arm"; harmonic drives | third axis at 135 deg to the first in prototype II | no curved bearing; uses a conventional joint |
| **NESM-γ** (Pan et al. 2022) [E4] | geared differential; proximal and distal **ring gears** around the arm, coupled through the upper and lower cuffs | "wide and symmetrical ROM (i.e. 116 deg)" | ring gears around the arm, actuated |
| **ARMin III / ArmeoPower** [E5] (excerpt) | internal/external rotation axis 3; an ARMin paper summary describes the family's approach as a serially mounted ring bearing with the actuator on the ring | IE ROM -90 to +90 deg; 102 deg/s max | vendor and section not found |
| **Dampace** (Stienen et al. 2009) [E6] (excerpt) | critique: open semicircular slider rails suffer from "the weight of the steel rail, the friction in the bend-around linear bearings, and the lack of stiffness"; proposes rotation-centre mechanisms built from rotational bearings | - | matches section 1 |
| **MEDARM** (Ball, Brown, Scott 2007) [E11] (excerpt) | shoulder "curved track mechanism driven by a cable transmission" | track geometry not found | - |
| Forearm devices (same problem at smaller radius) [E7, E8, E9] | Dežman 2019: C-shaped or full ring; "most … C-shaped … resulted in heavy and bulky structures"; their two-guided-rod substitute wandered ±7 mm about the axis. CEA ABLE: an open parallel mechanism replaces circular guides on mass, volume and friction; the CEA patent background notes an open semicircular guide "supported by a beam … of significant mass" (excerpt). IeCAT 2020: open semicircular ring, 150 g, 83 % of forearm range (excerpt) | Dežman Rw = 45 mm | stiffness is the recurring failure of open rings |

No source I could reach publishes the section height or moment rating of an exo's open humeral ring. The pattern is
consistent across them:
- Off-the-shelf curved rails (THK) on large, heavy stationary rehab robots.
- Wearable designs avoid them: Harmony, MGA, NESM, Dampace, ABLE.

A 10 mm-from-skin open ring would be new territory.

---

## 4. Q3 - 2R hub bearings and the shell-on-shell idea

### 4.1 Thin bearings for a 20-40 mm bore vs the v4 plain hub

| option | d x D x B (mm) | mass | rating | est. stack above F | tilt friction at 25 N.m | note |
|---|---|---|---|---|---|---|
| **v4 plain hub** (as built) [R1, R2] | pin O10 h9, GSM-1012-04 sleeve, 2 x GTM-1018-005 (10 x 18 x 0.5) | small | washer edge pressure 48 MPa at 25 N.m against an 80 MPa rating [R2] | **10.47** (with encoder and dome) | **2.5-4.8 N.m** (est. = (4/π)·μ·M, μ 0.08-0.15 for iglidur G vs steel [S14]; vs Ti not published) | thinnest proven stack |
| **Kaydon/RBC KAA15XL0** 4-point contact, 3/16 in section [S8] | 38.1 x 47.625 x **4.763** | 18 g | moment static 340 lbf-in (catalogue 40 N.m), dynamic 30 N.m; radial static 1.78 kN; 29 balls of 3/32 in | **≈ 9.0** (est.: 2.5 seat + 4.76 + 1.5 clamp + 0.2; encoder magnet and PCB inside the Ø38 bore) | ≈ 0.09 N.m (est.: P ≈ 2M/dp = 1.17 kN, M_f = ½·μ·P·d, μ 0.004) | static SF 1.6 at 25 N.m; zero play; needs a ~Ø52 boss |
| KAA10XL0 [S8] | 25.4 x 34.925 x 4.763 | 14 g | moment 170 lbf-in (20 N.m) | ≈ 9.0 | - | too weak for 25 N.m (SF 0.8) |
| **IKO CRBT305A** crossed roller [S11] (excerpt) | 30 x 41 x **5** | 20.7 g | C 1.77 kN, C0 1.97 kN; **M0 ≈ 35 N.m** (est. = C0·dp/2 from P0 = Fr + 2M/dp + 0.44Fa, dp ≈ 35.5) | ≈ 9.2 (est.) | ≈ 0.09 N.m (est.) | SF ≈ 1.4; IKO lists 5.5 mm section height and 5 mm width for CRBT |
| IKO CRBT205A [S11] (excerpt) | 20 x 31 x 5 | 14.8 g | C 1.40 kN, C0 1.29 kN; M0 ≈ 16 N.m (est.) | ≈ 9.2 | - | too weak for 25 N.m |
| **THK RA5008** (≈ IKO CRBS 508) [S10] | 50 x 66 x 8 | 80 g | C 5.10, C0 7.19 kN, dp 57; M0 ≈ 205 N.m (est.) | ≈ 12 (est.) | ≈ 0.1 N.m | only where 14 mm is allowed; overkill |
| Franke LEL 1.5, KK 70 [S7] | element 5.9 x 5.9, Ø70 ball circle | 30 g | C0m 0.2 kN.m | ≈ 9 (est.: 5.9 + housing lips) | low | large hub |
| igus PRT-04 (iglidur slewing ring) [S12] | D 60 (micro) / 80 (PRT-04-20); height not on page | - | micro: 786 lbf static, 224 lbf moving [S12] | unknown | plain | **0.25 mm radial and axial tolerance** [S12]: too much play |

Reading of the table:
- Height: the plain hub is already as thin as rolling hardware. A 0.5 mm iglidur washer beats any ball, the smallest
  being KAA's 4.76 mm section. Rolling gains about 1.5 mm only by moving the encoder into a hollow bore.
- What rolling buys is **friction** (≈ 0.1 vs 2.5-4.8 N.m at full tilt load) and **zero play with a predictable
  preload**.
- The 4/π·μ·M result does not depend on the washer radius. A bigger plain washer lowers the pressure, not the friction.

### 4.2 Shell-on-shell spherical sliding: known, but conditional

Where the principle is used:
- **Spherical plain bearings**, e.g. SKF GE..TXE-2LS with a steel/PTFE-fabric sliding layer, maintenance-free [P4].
- **Hemispherical air bearings** for attitude simulators: concentric spheres, machined and lapped; the Georgia Tech
  bearing is rated for 300 lbf with ±30 deg tilt [P2] (excerpt).
- **Circular-guided RCM mechanisms in surgical robotics**: circular guiding arcs are one of the standard RCM families,
  and Yip et al. switched from an open to a closed guiding arc to gain rigidity [P1].
- Shoulder-exo patents built on spherical geometry centred on the shoulder:
  - spherical parallel manipulator [P3] (excerpt);
  - curved scissor linkages sharing one RCM [P3] (excerpt).
  Neither uses nested sliding shells.

Conditions and consequences for the nested 2R (est. and reasoning):
1. **Kinematic compatibility.** If the J1 and J2 axes intersect at C, every point of both links moves on a sphere about C.
   Spherical surfaces centred on C then stay concentric, so a liner between them is compatible (redundant support, not
   over-constraint). If the axes do not intersect, for instance because the design offsets them to follow GH
   translation, concentric shells bind.
2. **The links are skin-conformal free-form shells, not spheres.** Sliding would need spherical lands or pads machined
   into the overlap zone of both links. Concentricity must hold to within the liner clearance (~0.1-0.2 mm, est.) on
   thin Ti shells that distort when machined. That tolerance is hard to hold.
3. **Friction.** A sliding annulus or cap reacting a tilting moment M carries a total normal load of about 4M/(π·ρ), so
   its friction torque is about (4/π)·μ·M whatever the radius ρ: about 3 N.m at μ 0.1 and 25 N.m (est.). It takes
   pressure and moment off the hubs and stiffens the overlap, but it does not reduce friction compared with the v4 hub.
   The hubs could then be pure locators.
4. **Stack.** A pad of iglidur tribo-tape is 0.5-1 mm plus 0.15-0.21 mm of adhesive [S15]. In the 14 mm overlap zone
   (2 + 5.5 + 5.5 + gap) it can replace the air gap at no extra height.

**Verdict:** worth trying as 3-4 spherical iglidur pads between link 1 and link 2, if the chain is a true spherical 2R. It
is not a replacement for the hub bearings.

---

## 5. Q4 - recommendations

### 5.1 Humeral-rotation joint (rail on link 2, carriage is the arm cuff; masses for a 150 deg rail at R55 = 144 mm of arc, est.)

| rank | option | build (est.) | radial stack, skin → outside | mass: 150 deg rail + 60 deg carriage (210 deg rail) | capacity at 25 N.m | friction torque at 25 N.m | when |
|---|---|---|---|---|---|---|---|
| **A** | **custom caged-ball wire-race C-slide** | Ti-6Al-4V SLM hollow band, 26 axial x 6 radial, 1.2 wall; two hardened steel race wires per edge (Franke principle [S7]); 60 deg Ti shoe with matching wires; 2 rows of ~10 balls Ø3 in a cage; anti-creep cage or end-stop re-centring [S16]; preload by an eccentric or gib | **2 + 6 + 2 = 10 mm** | 45 g band + 7 g wires + 34 g carriage ≈ **86 g** (≈ 107 g with a 210 deg rail) | roll at b ≈ 24: 1.04 kN per row, ≈ 100 N per ball. Per-ball static ≈ 155 N for 3/32 in balls (from KAA10XL0 thrust static 3.25 kN / 21 balls [S8]), ≈ 245 N scaled to Ø3 by D² → OK on paper | **0.2-0.9 N.m** | if the real moment at the ring is ≫ 5 N.m; needs a supplier (Franke) or in-house race grinding |
| **B** | **plain iglidur C-band slide, long shoe** (grown version of today's dovetail saddle) | Ti band 24-28 wide with dovetail edges (24 x 4 solid, or the hollow 26 x 6); shoe 60-90 deg (7075 or Ti) with 0.5 iglidur J liners and a tapered gib [R3] | **2 + 4 + 0.5 + 2 = 8.5 mm** (solid band) to **10.5 mm** (hollow band) | 58-61 g rail + 18-28 g shoe ≈ **76-89 g** (100-113 g with 210 deg) | pressure 4.5 MPa roll, 15-22 MPa yaw (L 58) vs 35 MPa → OK | **7-31 N.m** under a 25 N.m moment; **1-2 N.m** in the force-only cuff case | best if the carriage is the cuff and the ring carries force, not moment; simplest and thinnest |
| **C** | **long-wheelbase V-wheel carriage** (today's concept, grown) | rail with hardened steel V-edge inserts (Ti is not a raceway [R2]); 4 wheel pairs over 60 deg; DualVee size 0 class wheels (Ø14.83 x 6.35, 5.1 g [S4]) with radial axes beside the band | **2 + 6.35 + 2 ≈ 10.4 mm** | 61 g rail + ~80 g carriage (8 wheels, studs, plate) ≈ **140 g** (≈ 165 g) | yaw OK at L ≥ 40 mm (625 N vs 650 N); roll **≈ 20 N.m max** at b = 40, 4 wheels per side | ≈ 0.3-1 N.m | only if the roll moment is ≲ 15-20 N.m |

For all three, the rail section (section 1.5) is the critical member. Fix the rail to link 2 at its middle or at both ends,
and FE-check twist. A 24 x 4 open band twists ~5 deg at 25 N.m over 75 mm.

### 5.2 Nested-shell 2R hubs

| rank | option | stack above F | mass change per joint | why |
|---|---|---|---|---|
| 1 | **v4 plain hub** (keep) [R1] | 10.47 mm | 0 | proven; thinnest; friction 2.5-4.8 N.m at full tilt (est.). Check that against the assist budget |
| 2 | **KAA15XL0-class 4-point-contact thin section**, encoder in the bore [S8] | ≈ 9.0 mm (est.) | ≈ +10-20 g (est.: 18 g bearing + Ø52 boss, minus sleeve, washers and nut) | ~0.1 N.m friction; zero play; static SF 1.6 |
| 3 | **IKO CRBT305A crossed-roller ring** [S11] | ≈ 9.2 mm (est.) | ≈ +10-20 g (est.) | stiffer in tilt than balls; SF ≈ 1.4 (est. M0 35 N.m) |
| (opt.) | spherical iglidur pads between link 1 and link 2 | 0 extra in the 14 mm overlap | a few g | only if J1 ∩ J2 = shell centre; offloads the hubs (4.2) |

---

## 6. What to check next

1. The real moment at the humeral ring, from the R10 / OpenSim load case. It picks A or B (section 1.3).
2. In-house FE of the hollow band and its mount (twist, stress), the same way thin_study did the keel [R2].
3. Ask Franke about open-arc wire segments at KK 100-130 with a cage segment. Ask Kaydon/RBC for the KAA15XL0 moment-rating
   basis. Ask IKO for the CRBT305A tilting-moment rating. My M0 values are estimates.
4. Whether the 2R axes are designed to intersect. That decides whether the spherical pads are possible.
5. iglidur friction against bead-blasted or coated Ti is not in the igus data. Plan a coupon test before trusting μ.

---

## Sources

Catalogues and datasheets
- [S1] THK, R Guide Model HCR dimension table, catalogue p. A1-334: https://tech.thk.com/en/products/pdfs/en_a01_334.pdf
- [S2] THK HCR product page (model list): https://www.thk.com/jp/en/products/lm_guide/full_ball/hcr/hcr/
- [S3] HepcoMotion, "PRT ring slides and track system" catalogue (PRT 06 UK), pp. 10-17 and 24:
  https://www.albeco.com.pl/pl/katalog/preview/PRT-06-UK.pdf . PRT2 is the current range:
  https://www.hepcomotion.com/product/curved-rails-and-track-system-components/large-diameter-ring-guides-segments-and-track-systems/
- [S4] Bishop-Wisecarver DualVee / MinVee catalogue: https://crm.bwc.com/hubfs/Catalogs/DualVee-Bishop-Wisecarver-Catalog.pdf
- [S5] igus drylin W curved guides: https://www.igus.eu/product/22679
- [S6] Rollon Curviline datasheet (excerpt): https://www.usinenouvelle.com/expo/medias/2/0/7/000503702.pdf ;
  https://my.rollon.com/in/?p=4445
- [S7] Franke LEL wire-race bearing elements: https://www.franke-gmbh.com/bearings/wire-race-bearings-and-slim-bearings/lel/
- [S8] RBC (Kaydon-licensed numbering) thin-section 4-point contact X-type tables:
  https://www.rbcbearings.com/pdfs/aero/Rolling/089_143/TSBB_4PtCntct_Xtype.pdf ; KAA10XL0 sheet:
  https://pibsales.com/wp-content/uploads/pdf/KAA10XL0-KAYDON-Bearing-PIB.pdf
- [S9] Kaydon Reali-Slim part numbering (AA = 3/16 x 3/16 in section):
  https://cdn.skfmediahub.skf.com/api/public/0901d1968053c10b/pdf_preview_medium/0901d1968053c10b_pdf_preview_medium.pdf
- [S10] THK cross-roller rings RA / RAU / RA-C: https://tech.thk.com/en/products/pdfs/en_a18_032.pdf ;
  https://tech.thk.com/en/products/pdfs/en_a18_034.pdf
- [S11] IKO CRBT:
  - CRBT105A (10 x 21 x 5, C 1,120 N, C0 811 N): https://ikont.com/technical-resources/technology-blog/ultra-small-crossed-roller-bearings-help-shrink-automated-equipment-designs
  - CRBT205A (excerpt): https://www.industrybuying.com/special-bearing-iko-BEA.SPE.439184484
  - CRBT305A (excerpt): https://mx.misumi-ec.com/en/vona2/detail/221302297165
  - CRBT section 5.5 x 5 mm (excerpt): https://www.automate.org/robotics/news/industrial-robots-demand-versatile-crossed-roller-bearings/anc
- [S12] igus PRT-04: https://www.igus.ca/product/PRT_04_00 ; https://igus.eu/product/iglidur_PRT_04 ;
  https://www.igus.com/slewing-ring
- [S13] iglidur J datasheet (35 MPa, μ 0.06-0.18 vs steel, pv 0.34): https://nonprod.docs.rs-online.com/1033/0900766b80debd6c.pdf ;
  https://static.chipdip.ru/lib/262/DOC015262813.pdf
- [S14] iglidur G material data (μ 0.08-0.15 dry vs steel): https://igus.co.uk/info/plain-bearings-iglidur-g-material-data
- [S15] igus tribo-tape (0.5-1 mm, adhesive +0.15-0.21 mm): https://www.igus.ca/product/241
- [S16] IKO anti-creep cage crossed roller way (rack and pinion): https://ikont.com/technical-resources/technology-blog/keep-heavy-loads-moving-without-cage-creep/
- [S17] JTEKT/Koyo bearing friction coefficients: https://koyo.jtekt.co.jp/en/support/bearing-knowledge/8-4000.html

Exoskeleton literature
- [E1] Perry, Rosen, Burns, "Upper-limb powered exoskeleton design", IEEE/ASME T-Mech 12(4) 2007: http://www.columbia.edu/~njr2121/JP_13.pdf
- [E2] Kim, Deshpande, "An upper-body rehabilitation exoskeleton Harmony …", IJRR 36(4) 2017: https://mahilab.rice.edu/sites/default/files/page-files/2017_IJRR_Kim.pdf
- [E3] Carignan, Liszka, Roderick, "Design of an arm exoskeleton with scapula motion …", ICAR 2005: https://ssl.umd.edu/system/files/private/pub_full_text/SSL05-003.pdf
- [E4] Pan et al., NESM-γ, RA-L 2022: https://iris.santannapisa.it/retrieve/7e718f08-a79e-455e-8520-bdd5244c9f2a/2022%20-%20Pan%20-%20NESM-gamma%20-%20RAL_final.pdf
- [E5] ARMin III technical data (excerpt): https://www.researchgate.net/figure/Technical-data-of-the-ARMin-III-device_tbl3_305509642 ;
  ARMin family description (excerpt): https://www.researchgate.net/publication/224634507_ARMin_-_Toward_a_six_DOF_upper_limb_rehabilitation_robot
- [E6] Stienen et al., "Self-aligning exoskeleton axes through decoupling of joint rotations and translations", IEEE T-RO 2009 (excerpt): https://www.researchgate.net/publication/224402096_Self-Aligning_Exoskeleton_Axes_Through_Decoupling_of_Joint_Rotations_and_Translations
- [E7] Dežman et al., "Exoskeleton arm pronation/supination assistance mechanism with a guided double rod system", 2019: https://h2t.iar.kit.edu/pdf/Dezman2019.pdf
- [E8] Garrec, Verney, CEA ABLE (excerpt): https://hal-cea.archives-ouvertes.fr/cea-01144016 ; CEA forearm rotation patent US 8,460,222, background (excerpt): https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8460222
- [E9] IeCAT 2020 open-ring forearm actuator (excerpt): https://sciforum.net/paper/8511
- [E10] IKO CRBH/CRBF in Harmonic Bionics' Harmony (excerpt, **not confirmed** on the page): https://ikont.com/?p=2361
- [E11] MEDARM curved track (excerpt): https://qspace.library.queensu.ca/items/97316a90-d018-4dce-95f6-10ea7f4ed943

Spherical / RCM
- [P1] Yip et al., "A new circular-guided remote center of motion mechanism for assistive surgical robots", ROBIO 2014: https://research.polyu.edu.hk/en/publications/a-new-circular-guided-remote-center-of-motion-mechanism-for-assis/
- [P2] Georgia Tech spherical air-bearing simulator (excerpt): https://dcsl.gatech.edu/papers/aas01b.pdf ; https://raptor-scientific.com/products-category/air-bearings/
- [P3] Spherical parallel manipulator shoulder exo, US 10,800,031 (excerpt): https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10800031 ;
  scissor spherical shoulder mechanism, Aalborg (excerpt): https://vbn.aau.dk/ws/files/290003429/scissors_shoulder_mechanism_vFiNAL_R1_MMT_mnc_RoMEOgreen.pdf
- [P4] SKF GE..TXE-2LS, steel/PTFE-fabric, maintenance-free: https://acorn-ind.co.uk/p/ge50txe-2ls-skf

Repo
- [R1] `docs/HARDWARE.md` (v4 joint stack, 10.47 mm)
- [R2] `pipeline/conformal/thin_study/REPORT.md`:
  - 5.5 mm links;
  - track keel ≥ 10 mm deep;
  - MR84 C0r 139 N vs ~600 N per wheel;
  - washer 48 / 80 MPa;
  - DLC is an "eggshell on Ti".
- [R3] `pipeline/conformal/fair_cad/armend_fair.py` (`build_carriage`, `build_dovetail_track_neck`, `build_saddle`);
  constants in `pipeline/conformal/band_cad/build_band_cad.py` (`WHL_*`, `TRK_*`)
