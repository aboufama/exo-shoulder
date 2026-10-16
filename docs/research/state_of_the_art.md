# State of the art: shoulder exoskeletons and close-to-body shoulder mechanisms vs our design point

Research note, 2026-10-16 (time-boxed survey, 60 min). It answers the user's question: "would you say real progress has
been made compared to the state of the art of what exists today?" Sources are papers, datasheets and abstracts read
in this session. Only small paper PDFs were fetched, to the scratchpad. Nothing big was downloaded.

**Tags.**
- **[R]**: read in the source (table, figure or section named).
- **[S]**: from a search-engine summary or abstract excerpt of the cited page. The full text was not read.
- **[I]**: inferred here from a stated number.
- **[est.]**: estimated from a stated dimension; the method is given.
- **"-"**: not stated in anything read here.

Nothing was invented. Where a number was not reached, the table says so.

**Our design point**, simulated only. It is the verified leader `skin-normal-3r-pin-knee` k4598
(docs/concepts/skin-normal-3r-pin-knee.md):
- Mechanism: three pins whose axes meet at the GH centre, plus a flat two-pin knee at the cuff. That is 2 passive pins
  and 0 passive translations. The base rides the user's scapula handler.
- Status: unpowered MVP1.
- Score: worn frozen on Bench(110,360), exact libigl path, the gap is 30.35 (score 88.96).
- Of the metal points on the covered poses, 0.904 are 2-14 mm off the skin.
- Follow 1.0. Contact 0.009 of poses.
- Reach is 0.606 of the sampled functional workspace, and 0.25 overhead (elevation >= 140 deg).
- The limiter is the J2 fold (the spherical 3R's singular boundary).

---

## 1. Answer (short, blunt)

**On one axis, yes. On every axis that makes something a device, no, not yet.**

- **Where there is real progress: documented closeness to the skin at the minimum DOF.**
  - No surveyed device publishes how far its mechanism stands off the skin, let alone over its range of motion. The
    closest reported quantities are about something else:
    - reachable-workspace volume with vs without the device (CXD);
    - parasitic interaction forces (Harmony);
    - GH-centre misalignment (NESM-gamma, CAREX).
  - The compact remote-centre class cannot ride a 2-14 mm band over the shoulder cap. A concentric shell at the CXD
    radius (60 mm) is in band in only 37 % of cap directions at rest, and 75-83 % of directions lie inside the body
    overhead (section 3, computed here).
  - Our leader keeps 90 % of its sampled metal 2-14 mm off a posed skin. It does so with 3 rotations, 2 passive pins
    and no passive translation.
  - Every built device that handles girdle / GH translation uses more freedoms:
    - Harmony and MGA: active girdle DOF;
    - NESM-gamma: 6 passive DOF including a slider;
    - the ASU SPM: a 2-DOF slip with a translation;
    - CAREX: 3 uncontrolled translations.
  - As a simulated design point this combination appears new.
- **Where it is not progress (yet).**
  - **Range.**
    - Ours: 0.606 of the functional workspace, 0.25 overhead.
    - Harmony: 160 deg flexion and 170 deg abduction with external rotation [R].
    - CADEN-7: 99 % of the ADL joint ranges [R].
    - MGA: first GH joint +180 / -45 deg [R].
    - Overhead is exactly where we fail. It is also the user's own priority (CLAUDE.md, 2026-10-16: "max out reach").
  - **Hardware.** Every device in the table was built. Most were tested on people: Harmony, NESM-gamma, CXD and
    Myoshirt (10 participants), Proietti's soft wearable (10 people with ALS). Ours exists as a bench model and
    keep-out CAD.
  - **Actuation.** None. MVP1 is unpowered. Every rehab exo here is powered. Passive industrial exos deliver 6-13 N.m
    of assist [R, Ding 2023 Table 1].
  - **Validation.** One body model, with a girdle law that the literature contradicts by 2-3x in superior GH lift
    (docs/research/gh_translation_literature.md). There are no human trials and no measured stand-off.
  - **Mass.** Not yet computed.
- **Singularity handling is not ahead.**
  - Placing the 3R singularity at the edge of the workspace is standard practice:
    - MGA tilts its first axis 30 deg and sets J1-J3 at 135 deg at rest [R];
    - CADEN-7 parks it at hard-to-reach poses, movable in 15 deg steps [R];
    - Harmony uses acute 60 / 60 / 18 deg joint angles [R].
  - Our fold limits reach because our proximity constraint forbids the axis layouts those devices use. That trade
    appears new and is measured; the singularity itself is classical.

---

## 2. Survey table

Abbreviations:
- **act / pas**: active / passive DOF at the shoulder complex (girdle + GH).
- **GH tr.**: how girdle / GH-centre translation is handled.
- **Stand-off**: distance from the mechanism to the skin.

| Device (class) | Shoulder DOF act / pas | GH tr. handling | ROM (overhead?) | Stand-off from skin | Mass | Singularity handling | Built / validated | Ref |
|---|---|---|---|---|---|---|---|---|
| **Ours: skin-normal-3r-pin-knee k4598** (unpowered PoC, simulated) | 3 sensed pins (axes through GH) / 2 passive pins (cuff knee), 0 passive translations; base on the user's scapula handler (outside the count) | Scapula-handler base + planar two-pin knee that absorbs the J3 drift in hub 3's plane (2-slide closure theorem) | Reach 0.606 of the sampled functional workspace; overhead (elev >= 140) 0.25 | **0.904 of metal points 2-14 mm** on covered poses; contact 0.009 of poses (Bench(110,360), exact) | Not computed (5 mm pin stack, 12.25 mm hubs) | Not avoided: the J2 fold (window 2 min(a1, a2) - 20 ~ 60 deg vs 27-141 deg needed) is the limiter | Bench + L1 keep-out CAD only; no hardware, no subjects | concept doc |
| **Harmony** (UT Austin; rehab, bilateral) | 5 active (girdle: 1 revolute elevation + 1 parallelogram protraction; GH: 3 revolute) / 0 | Active 2-DOF girdle mechanism with a scapulohumeral-rhythm controller; girdle ROM 50 elev / 5 dep / 20 prot / 45 retr deg [R] | Abd 118 (170 with ER), flex 160, ext 45, ER 79, IR 80 deg (Table 3) [R]: **overhead yes**. With the girdle locked, the arm was "impeded to elevate above 80 deg" [R] | "-". Abduction limited by "interference between J5 and the head" [R], i.e. GH links ride above the shoulder [I] | 31.2 kg excluding the frame, bilateral (Table 1) [R] | Acute joint angles a = b = 60, g = 18 deg trade internal-rotation ROM against the J3-J4-J5 singularity (Fig. 4) [R] | Built; ROM and parasitic forces on users | [H1] |
| **ANYexo 2.0** (ETH; rehab) | "All relevant DOF of the human arm" incl. a controlled shoulder coupling [S]; exact count not read | Robot shoulder-girdle elevation joint coupled to humeral elevation, GED = -0.0053 theta^2 - 0.0162 theta + 20.5 deg (<= 96 deg), a 51 deg swing [R, earlier read, gh_translation_literature.md] | "Most ADLs" [S]; joint speeds 200 / 398 / 354 % of ADL needs at shoulder / elbow / wrist [S] | "-" | Not confirmed. A secondary source gives 12.98 kg for "ANYexo", version unclear [S] | "-" (full text rate-limited this session) | Built; motion capture with 2 participants for the coupling [R, earlier read] | [A1] |
| **MGA** (Maryland-Georgetown-Army; rehab) | 4 active (scapula 1 + GH 3) + elbow / passive fit adjustments | 1 active scapula elevation/depression joint, +30 / -30 deg; its axis is normal to the back (Table IV) [R] | GHR1 +180 / -45, GHR2 +90 / -65, GHR3 +210 / -30 deg (Table IV) [R]: overhead yes by joint range | "-"; GHR2 "located to the side and slightly beneath the shoulder" [R] | ~12 kg prototype [R] | Two GH singularities 180 deg apart "can be moved, but cannot be eliminated". J1 tilted 30 deg; J1-J3 at 135 deg at rest "to allow the arm to abduct further" [R] | Built (2 rapid prototypes + final) | [M1] |
| **CADEN-7 / EXO-UL7** (UW / UCLA; rehab, cable-driven) | 3 active GH / 0 | GH modelled as a fixed centre [R] | Table III title: "achieves 99 % of the ROMs required to perform daily activities" [R] | "-"; humeral rotation by an open semicircular rail (3 x 60 deg THK segments) [R, ring_and_shell_hardware.md] | Link 1 3.5 kg, links 2-7 6.3 kg [R] | J1-J3 singularity placed at "anthropometrically hard to reach" poses (ext 47.5 + abd 53.6, or flex 132.5 + add 53.6 deg); movable in 15 deg steps [R] | Built | [C1] |
| **ArmeoPower / ARMin III** (ETH / Hocoma; rehab, commercial) | 3 active shoulder + elbow / 0 | "Ergonomic shoulder actuation" that moves the humeral head, from a simplified shoulder model [S] | IE -90 to +90 deg [S, via ring_and_shell_hardware.md] | "-" | "-" | "-" | Commercial. Comfort study (20 subjects): only marginally better than a ball-and-socket design [S] | [AR1, AR2] |
| **NESM-gamma** (SSSA; rehab) | 4 active (3 shoulder + elbow) / **6 passive** self-alignment DOF (P1 vertical slider, P2-P4 lockable rotations, ...) [R] | Passive chain; median GH-COR deviation < 20 mm and shoulder RMSE < 5 deg with it unlocked (8 subjects) [S] | IE 116 deg [R]; elevation range not read | "-" | ~12.8 kg [R] | "-" | Built; 8 subjects | [N1, N2] |
| **Dampace / Limpact** (Twente; rehab) | 3 rotations, decoupled from passive translations [S] | Self-aligning: rotations decoupled from passive translations [S] | "-" | "-" | "-" | "-" | Built | [D1] |
| **ABLE** (CEA; rehab / haptics) | 3 active shoulder + elbow (4-axis) / 0 | None stated | One shoulder axis 110 deg, elbow 130 deg (Table I amplitudes) [R] | "-"; the 2nd joint is a circular guide, "free of singularity and not invasive" [R] | Table I: ~3.0 kg and ~10.0 kg (column assignment unclear in the text) [R] | Circular-guide joint (no 3R singularity at that axis) [R] | Built | [AB1] |
| **BONES** (UCI; rehab, pneumatic) | 3 shoulder + elbow (4 DOF) via a parallel mechanism with 2 passive sliding rods / 0 | None (fixed GH) [I] | Shoulder 105 / 80 / 100 deg about an arm-horizontal home (Table I) [R]: elevation not to full overhead [I] | "-" | 18.5 kg total incl. grounded actuators; 4.36 kg moved by the user [R] | ZYX singularity "not in the range of motion" [R] | Built | [B1] |
| **CAREX** (Columbia; rehab, cable-driven cuffs) | 3 rotations controlled via 7 cables / 3 GH translations "not controlled" [R] | GH centre estimated in real time from cable lengths (< 1.5 cm error, simulation) [R] | Not given ("as high as he can") [R] | Cuffs on the skin; cables in the air [I] | 1.32 kg incl. orthosis [R] | None (no serial chain) [I] | Built; 1 subject | [CX1] |
| **ASU SPM + slip** (Hunt, Artemiadis, Lee) | 3-DOF spherical parallel manipulator / 2-DOF passive slip (1 rot + 1 trans) [S] | Slip interface absorbs GH translation [S] | Spherical surface centred on the shoulder [S] | "-" | ~5.4 kg excl. power and controller (patent) [S] | Parallel (SPM) [S] | Built | [P1] |
| **CXD scissors shoulder** (Aalborg; compact remote centre) | 3 GH rotations (scissor SPM, serial-equivalent) + 1 elevation joint / 0 [R] | 1 shoulder-elevation DOF [R] | 0.236 m3 = 68.1 % of the full and 95.0 % of the protraction-locked reachable workspace (1 subject) [R]; IR / ER 46 / 58 deg [R] | Sphere radius **60 mm** (Table 2) [R]. On our body a 60 mm shell sits -11 / 12 / 20 mm (p10 / 50 / 90) off the cap at rest and is inside the body in 75-83 % of directions overhead [est., section 3] | "-" | "Practically singularity-free"; singular only fully folded / stretched, kept out by an 8 deg intrusive angle [R] | Built (3D-printed steel links); 1 subject | [X1] |
| **Double-parallelogram shoulder** (Christensen & Bai 2018) | 3 rotations about a remote centre [S] | None stated | Singularity-free in the shoulder workspace [S, via X1] | "Protrudes out of the shoulder region", "lack of compactness" [R, critique in X1] | "-" | Singularity-free [S] | Prototype | [X1, DP1] |
| **Passive industrial**: ShoulderX, AirFrame (Levitate), EksoVest, Ekso EVO, Skelex 360-XFR, Paexo (Ottobock), Hilti EXO-O1 / EXO-S | 1 assisted elevation axis + passive joints (typical) [I] | Passive alignment joints [I] | Overhead work is the use case; Ding 2023's own passive exo: flexion 150.7 +- 3.0 deg with the exo vs 155.2 +- 4.9 without (Table 2) [R] | "-" (none publish it) | ShoulderX 3.17, AirFrame 2.7, EksoVest 4.3, Skelex 360-XFR 2.5, PAEXO 1.9 kg (Table 1) [R]; Ekso EVO 4.1 kg (datasheet) [S]; Hilti EXO-O1 < 2 kg, EXO-S 2.4 kg [S]; Skelex 360 2.85 kg [S] | n/a (1 DOF) | Sold commercially; lab and field studies | [I1-I5] |
| **Soft: Harvard textile pneumatic shoulder** (2017; ALS 2023) | Textile actuators: abduction + horizontal flexion / extension [S] | Garment on the skin [I] | "-" | Folds flat under clothing when deflated [S]; the inflated bulk in the axilla is not stated | **150 g added per limb** (Proietti 2023 abstract) [S] | n/a | Built; 10 people with ALS [S] | [SF1, SF2] |
| **Soft: Myoshirt** (ETH; cable exosuit) | 1 assisted elevation (cable tendon) [S] | Garment [I] | "-" | Garment on the skin; actuator + control box carried off the arm [S] | Actuator + control box ~4 kg [S] | n/a | Built; 10 unimpaired + 2 impaired; fatigue onset +51.1 s (36.1 %), muscle activity -49.1 % [S] | [SF3] |

**Not reached in this session (no numbers given above):**
- EXO-UL8 (UCLA dual-arm successor of EXO-UL7);
- SUEFUL-7 (Gopura, Kiguchi);
- IntelliArm (Ren, Park, Zhang). A secondary source says it uses passive joints for girdle motion; this is not verified;
- MEDARM (curved shoulder track; geometry not found earlier, ring_and_shell_hardware.md).

---

## 3. A yardstick computed here: can a remote-centre (concentric-shell) mechanism hug the cap?

The compact class (CXD, SPMs, double parallelograms, curved RCM rails) puts its links on or near a sphere about the
GH centre. If the cap were a sphere, such a shell would be the ideal skin-hugger.

**Method.** `docs/research/sota_shell_standoff.py`, on the bench body, exact libigl path.
- Rays leave the posed GH centre over the cap: azimuth -90..180 deg, elevation -30..90 deg, 6 deg grid.
- On each ray, r_skin is the last radius at which the ray exits the skin.
- A shell of radius R then sits R - r_skin off the skin in that direction.

| Pose | r_skin p10 / 50 / 90 (mm) | R = 60 (CXD): stand-off p10 / 50 / 90; in 2-14 mm; inside body | R = 80 | R = 100 | R = 150 |
|---|---|---|---|---|---|
| lowest clip pose (elev 3 deg) | 40 / 48 / 71 | -11 / 12 / 20 mm; **0.37**; 0.21 | 9 / 32 / 40; 0.08; 0.06 | 29 / 52 / 60; 0.02; 0.03 | 79 / 102 / 110; 0.00; 0.02 |
| overhead (elev 150, plane 0) | 57 / 82 / 132 | -72 / -22 / 3; 0.13; **0.83** | -52 / -2 / 23; 0.20; 0.52 | -32 / 18 / 43; 0.12; 0.32 | 18 / 68 / 93; 0.04; 0.06 |
| overhead (elev 165, axial -45) | 46 / 79 / 163 | -103 / -19 / 14; 0.13; 0.75 | -83 / 1 / 34; 0.18; 0.48 | -63 / 21 / 54; 0.09; 0.31 | -13 / 71 / 104; 0.03; 0.14 |

**Reading.**
- The skin around GH spans 40-71 mm (p10-p90) at rest and 46-164 mm overhead. It is not a sphere.
- Any single shell radius is in band in at most 37 % of cap directions at rest and 13-22 % overhead.
- A shell large enough to clear the body overhead (R >= 150) stands 70-100 mm off at the median.
- This is the same conclusion as docs/research/proximity_atlas.md (the cap's skin moves with a graded fraction of the
  arm's swing), measured here on the geometry of the published compact designs.

**Caveats.**
- The ray set includes directions that point into the arm and the trunk. A real mechanism routes around them, so the
  "inside" share is an upper bound on what a real linkage must avoid.
- Real links have thickness. A link on a sphere of radius R has its underside at R - t.
- Only 3 poses are shown. Running the script over all poses is a cheap follow-up.

---

## 4. Closest prior art to our design point (3 rotations, all metal ~1 cm off the skin, overhead)

1. **CXD scissors shoulder mechanism** (Castro, Rasmussen, Andersen, Bai 2019) [X1].
   - The only device reached that explicitly optimises compactness around GH. Links lie on a 60 mm sphere, it is
     "practically singularity-free", and the scissor cells each turn a fraction of the motion: the atlas's "graded
     fraction" idea, built.
   - Differences:
     - it adds a separate shoulder-elevation DOF, so 4 DOF with the girdle;
     - its stand-off is set by one sphere, which the yardstick above shows cannot track the cap;
     - it keeps 68 % of the full reachable workspace (1 subject).
2. **MGA** [M1] and **CADEN-7** [C1]: serial 3R shoulders whose singularity is placed by axis tilt. This is the
   classical form of our fold problem, solved with big links far from the body.
3. **Harmony** [H1]: an anatomical shoulder with acute joint angles (60 / 60 / 18 deg) that trade singularity against
   ROM, the same window trade as our a1 / a2. It reaches overhead with 2 active girdle DOF and 31 kg.
4. **ASU SPM + slip** [P1] and **NESM-gamma** [N1]: passive interface freedoms that absorb GH translation, as our knee
   does. They use translations (slip / slider); we use two pins.
5. **Passive industrial exos** [I1]: the commercial reference for overhead support at 1.9-4.3 kg. Their bars run
   behind the back and along the upper arm. No stand-off is published.

---

## 5. Where we lead, where we trail

**Lead (simulated, single body model):**
- A measured stand-off distribution: 0.904 of metal 2-14 mm off a posed skin, contact 0.009. No surveyed paper
  publishes any stand-off number.
- Minimum freedom for girdle compliance: 3 rotations + 2 passive pins + 0 passive translations. Others use:
  - Harmony and MGA: active girdle DOF;
  - NESM-gamma: 6 passive DOF incl. a slider;
  - the ASU SPM: a slip with a translation;
  - CAREX: 3 free translations.
- An instrument: a proximity-scored design bench (posed skin SDF over clip + workspace poses, verifier re-measurement,
  frozen-shape protocol). The published evaluation instruments are reachable-workspace volume [X1], interaction forces
  [H1], COR deviation [N2] and ADL joint-range tables [C1, H1].

**Trail (blunt):**
- **Range and overhead.**
  - Ours: reach 0.606, overhead 0.25.
  - Harmony: flexion 160 deg and abduction 170 deg (with ER), on a real person.
  - CADEN-7: 99 % of ADL ranges.
  - MGA: J1 +180 deg.
  - CXD: 95 % of its constrained workspace.
  - The fold is the cause. Every rehab exo above avoids it by putting the singular direction where the arm rarely goes,
    which our 14 mm band forbids (hub 2 would sit 93-115 mm from GH).
- **Built hardware.** None. Every surveyed device exists.
- **Actuation.** None (MVP1). Rehab exos produce 18-92 N.m at the shoulder: ABLE 18 N.m, Harmony 34.4 N.m, MGA 92 N.m
  stall [R]. Passive industrial exos give 6-13 N.m [R]. Routing actuation into a 14 mm band is unsolved
  (docs/research/sim_to_real_gaps.md G1: cable tension 0.9-2.2 kN at a hub-radius pulley).
- **Validation.** One rig body. Its girdle law under-predicts GH lift 2-3x, with 26-51 mm vector error at 90-135 deg
  (gh_translation_literature.md). No human subjects. No loaded fit: under assist the cuff moves 11-27 mm
  (sim_to_real_gaps.md G4).
- **Mass and stiffness.** Not computed.

---

## 6. Claims that may be new (each needs a prior-art check before it is claimed outside the repo)

1. **The fold-versus-skin frontier.**
   - The window itself is classical spherical-mechanism geometry: the J1-J3 angle must lie in
     [|a1 - a2|, a1 + a2] (our 10 deg margins aside). Placing the singularity is standard: MGA, CADEN-7, Harmony and
     Lo & Xie (cited in X1).
   - What appears new is the measurement against a functional workspace distribution. The J1-J3 angle needed is
     27-141 deg (22-146 overhead) against a window of 2 min(a1, a2) - 20.
   - It is tied to the proximity cost of widening a1: hub 2 at 93-115 mm from GH, gap 64-80.
   - The result: a GH-ray-hub 3R cannot be fold-free and in band on this body (docs/FINDINGS.md, 2026-10-16).
   - No paper reached here couples singularity placement to a skin stand-off.
2. **The 2-slide closure theorem.**
   - Statement: a translational cuff with k slides closes an offset 3R exactly iff the axis-line condition holds. With
     J1 and J2 on GH rays, the arm-vs-member-3 drift is planar in hub 3's plane, so two pins or two slides close it.
   - Related general theory: kinematic-compatibility conditions for passive DOF (Schiele & van der Helm 2006; Stienen
     et al. 2009; Cempini et al. 2013, kinetostatic compatibility).
   - Not checked against Cempini 2013's full text. **Possibly new as a specific statement; unverified.**
3. **The two-pin planar knee as GH-translation absorber with 0 passive translations.**
   - The published absorbers use translations: NESM-gamma (slider), ASU (slip), Dampace (translations), CAREX (free).
   - Check against the ASU misalignment patent US 10,814,473 before claiming.
4. **The proximity-scored design bench** (skin-distance band, follow, reach and contact on posed skins, with an
   independent verifier). No prior instrument of this kind was found.
5. **The concentric-shell yardstick (section 3).** A remote-centre shell of the CXD radius on this body is in band in
   37 % of cap directions at rest, and 75-83 % of directions lie inside the body overhead.

---

## 7. Red team on this comparison

- **Units.**
  - Our "reach" is a share of sampled workspace poses taken without contact or fold. Published ROMs are joint-angle
    ranges reached on people. They are not the same unit; a 160 deg flexion device may still fail some of our poses.
  - Our in-band share is a share of sampled metal points, not a maximum stand-off. The worst point can be further off.
- **The body.**
  - Our numbers are on the rig, not the user's scan (data/raw), and the rig's girdle law is known to be wrong overhead.
  - A heavier girdle motion moves skin under the scapula-fixed hubs. The stand-off numbers are probably optimistic.
- **Hardware.** None of our parts exists. Others' numbers include real cuffs, real tolerances and real users.
- **This survey's coverage.**
  - It is limited by the time box and by access: ANYexo 2.0's full text was rate-limited, and IEEE and ResearchGate
    pages were not readable. Rows marked [S] rest on abstracts or search excerpts.
  - A device that does publish a stand-off may exist and was not found. Searches for "protrusion" / "profile" / "lateral
    offset" returned none.
- **The shell yardstick.** It treats a remote-centre mechanism as a full sphere. Real CXD links cover a small patch
  that can be placed where the cap is most spherical (e.g. over the lateral deltoid, where r_skin ~ 48 mm at rest). The
  37 % is the average over the cap, not the best patch.

---

## 8. Next (what would make the claim of progress stand)

1. **Reach.** Overhead reach >= 0.6 at the same stand-off is the gap to every rehab exo (round 4: fold levers,
   CLAUDE.md "max out reach").
2. **Re-measure on better data.** Run the leader on the user's own scan and on the literature girdle law (bone-pin
   chain); report how far in-band drops.
3. **Mass and stiffness.** Compute the leader's mass and stiffness from the L1 CAD so it can be put in the table.
4. **Build and measure.** A printed MVP1 on the user, with stand-off measured (feeler gauges or a depth camera) at
   rest, 90 deg and overhead. Measured stand-off is the number nobody publishes.
5. **Prior-art check.** Before any external claim: read Cempini 2013 (closure / compatibility), the ASU misalignment
   patent, ANYexo 2.0's full text and Lo & Xie on 3R singularity placement.

---

## References

Rehab / research exoskeletons
- [H1] Kim B, Deshpande AD (2017). An upper-body rehabilitation exoskeleton Harmony with an anatomical shoulder
  mechanism. *IJRR* 36(4):414-435. https://mahilab.rice.edu/sites/default/files/page-files/2017_IJRR_Kim.pdf
  (full text: Table 1, Table 3, Fig. 4, Fig. 13, sec. 3.2, 6.1-6.2)
- [A1] Zimmermann Y, Sommerhalder M, Wolf P, Riener R, Hutter M (2023). ANYexo 2.0. *IEEE T-RO* 39(3).
  https://ieeexplore.ieee.org/document/10008060/ ; https://research-collection.ethz.ch/handle/20.500.11850/584411
  (abstract [S]; coupling Eq. from the earlier full-text read in docs/research/gh_translation_literature.md).
  Secondary mass: https://arxiv.org/pdf/2503.10554 [S]
- [M1] Carignan C, Liszka M, Roderick S (2005). Design of an arm exoskeleton with scapula motion for shoulder
  rehabilitation. *ICAR 2005*. https://ssl.umd.edu/system/files/private/pub_full_text/SSL05-003.pdf (full text: Table IV,
  sec. III-A, III-B, VI)
- [C1] Perry JC, Rosen J, Burns S (2007). Upper-limb powered exoskeleton design. *IEEE/ASME T-Mech* 12(4).
  http://www.columbia.edu/~njr2121/JP_13.pdf (full text: Table III title, sec. III-D / Fig. 8, link masses)
- [AR1] Nef T, Guidali M, Riener R (2009). ARMin III. *Appl Bionics Biomech* 6(2). https://doi.org/10.1080/11762320902840179
  [S]
- [AR2] Comfort of two shoulder actuation mechanisms for arm therapy exoskeletons. https://boris.unibe.ch/43024 [S]
- [N1] Pan J et al. (2022). NESM-gamma. *IEEE RA-L*.
  https://iris.santannapisa.it/retrieve/7e718f08-a79e-455e-8520-bdd5244c9f2a/2022%20-%20Pan%20-%20NESM-gamma%20-%20RAL_final.pdf
  (full text: sec. II, mass, IE ROM)
- [N2] NESM-gamma self-alignment evaluation, *IEEE TNSRE* 2023. https://iris.santannapisa.it/retrieve/a32a5d97-6461-4df6-a2a0-174fe0f79685/Pan2023%20-%20TNSRE.pdf ;
  https://doaj.org/article/491c2eebb4e94b859c3096c733567bc3 [S]
- [D1] Stienen AHA, Hekman EEG, van der Helm FCT, van der Kooij H (2009). Self-aligning exoskeleton axes through
  decoupling of joint rotations and translations. *IEEE T-RO* 25(3). https://doi.org/10.1109/TRO.2009.2019147 [S]
- [AB1] Garrec P et al. (2008). ABLE, an innovative transparent exoskeleton for the upper-limb. *IROS 2008*.
  https://hal.archives-ouvertes.fr/cea-01588401 (full text: Table I, sec. II)
- [B1] Klein J, Spencer S, Allington J, Minakata K, Wolbrecht E, Smith R, Bobrow J, Reinkensmeyer D (2008). Biomimetic
  orthosis for the neurorehabilitation of the elbow and shoulder (BONES). *BioRob 2008*.
  https://jebobrow.eng.uci.edu/sites/default/files/EMBS_2008_Klien.pdf (full text: Table I, sec. II-C, mass)
- [CX1] Mao Y, Jin X, Agrawal SK (2014). Real-time estimation of glenohumeral joint rotation center with cable-driven arm
  exoskeleton (CAREX). https://pmc.ncbi.nlm.nih.gov/articles/PMC4023848 (full text: sec. 2-5)
- [P1] Hunt J, Artemiadis P, Lee H. Development of a novel shoulder exoskeleton using parallel actuation and slip
  interface. https://asu.elsevierpure.com/en/publications/development-of-a-novel-shoulder-exoskeleton-using-parallel-actuat ;
  US 10,800,031 https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10800031 ; US 10,814,473
  https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10814473 [S]

Compact / remote-centre mechanisms
- [X1] Castro MN, Rasmussen J, Andersen MS, Bai S (2019). A compact 3-DOF shoulder mechanism constructed with scissors
  linkages for exoskeleton applications. *Mech Mach Theory*. https://doi.org/10.1016/j.mechmachtheory.2018.11.007 ;
  accepted manuscript https://vbn.aau.dk/ws/files/290003429/scissors_shoulder_mechanism_vFiNAL_R1_MMT_mnc_RoMEOgreen.pdf
  (full text: abstract, Table 2, sec. 2.2, 3.1-3.2, 5)
- [DP1] Christensen S, Bai S (2018). Kinematic analysis and design of a novel shoulder exoskeleton using a double
  parallelogram linkage. *J Mech Robot* 10(4) (not read; via X1). Related DPL theses:
  https://honors.umaine.edu/thesis/an-upper-extremity-exoskeleton-utilizing-a-modified-double-parallelogram-linkage-mechanism-with-proximally-located-actuators/ [S]
- SPM shoulder background: https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2021.596958/pdf [S]

Passive industrial
- [I1] Ding S, Reyes Francisco A, Li T, Yu H (2023). A novel passive shoulder exoskeleton for assisting overhead work.
  *Wearable Technologies*. https://pmc.ncbi.nlm.nih.gov/articles/PMC10936402/ (Table 1 masses / torques; Table 2 ROM)
- [I2] Ekso EVO technical sheet: https://eksobionics.com/static/46a879fd6bdb04b7442754362c4e5e8d/Ekso-EVO-Technical-Sheet.pdf [S]
- [I3] Hilti EXO-O1: https://exoskeletonreport.com/product/exo-o1/ ; EXO-S:
  https://www.hilti.co.uk/c/CLS_HEALTH_SAFETY/CLS_CONSTRUCTION_EXOSKELETONS/r14012433 [S]
- [I4] Skelex 360: https://exoskeletonreport.com/product/skelex-360/ [S]
- [I5] Levitate AirFrame: https://www.thesafetymag.com/ca/products/ergonomics/airframe-exoskeleton/188617 [S] (mass from I1)

Soft
- [SF1] A soft wearable robot for the shoulder: design, characterization, and preliminary testing (ICORR 2017).
  https://www.iris.sssup.it/handle/11382/532181 ; https://biodesign.seas.harvard.edu/soft-inflatables [S]
- [SF2] Proietti T et al. (2023). Restoring arm function with a soft robotic wearable for individuals with ALS. *Sci
  Transl Med* 15(681). https://biodesign.seas.harvard.edu/publications/restoring-arm-function-soft-robotic-wearable-individuals-amyotrophic [S]
- [SF3] Georgarakis AM et al. (2022). Myoshirt. *Nat Mach Intell*. https://www.goodnewsnetwork.org/a-discreet-set-of-weable-muscles-restores-mobility-in-those-who-have-trouble-moving-their-arms/ ;
  https://research-collection.ethz.ch/bitstream/handle/20.500.11850/495456/1/Georgarakis2020ControlForGravityCompensation.pdf [S]

Repo
- docs/concepts/skin-normal-3r-pin-knee.md (our numbers), docs/FINDINGS.md (fold frontier, closure theorem),
  docs/concepts/offset-skin-normal-3r.md (closure theorem statement), docs/research/proximity_atlas.md,
  docs/research/gh_translation_literature.md, docs/research/sim_to_real_gaps.md,
  docs/research/ring_and_shell_hardware.md, docs/research/sota_shell_standoff.py (section 3).
