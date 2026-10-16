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
    **[Red team: overreach.]** This holds only for links on one constant-radius sphere. It was tested on a full
    shell, not on a link patch that moves with the arm. Our own leader is also a concurrent-axis (remote-centre) 3R.
    See "Red team (independent re-check)", B5.
  - Our leader keeps 90 % of its sampled metal 2-14 mm off a posed skin. It does so with 3 rotations, 2 passive pins
    and no passive translation. **[Red team.]** In the user's 2-10 mm aim band the share is 0.538.
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
  - **Actuation.** None. MVP1 is unpowered. Every rehab exo here is powered. Passive industrial exos deliver
    **5.5-13 N.m** of assist [R, Ding 2023 Table 1; red team corrected from "6-13": Comau MATE gives 5.5 N.m].
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
| **Ours: skin-normal-3r-pin-knee k4598** (unpowered PoC, simulated) | 3 sensed pins (axes through GH) / 2 passive pins (cuff knee), 0 passive translations; base on the user's scapula handler (outside the count) | Scapula-handler base + planar two-pin knee that absorbs the J3 drift in hub 3's plane (2-slide closure theorem) | Reach 0.606 of the sampled functional workspace; overhead (elev >= 140) 0.25 | **0.904 of metal points 2-14 mm** on covered poses; contact 0.009 of poses (Bench(110,360), exact). In the user's 2-10 mm aim band: **0.538** [red team; concept doc, verified numbers] | Not computed (5 mm pin stack, 12.25 mm hubs) | Not avoided: the J2 fold (window 2 min(a1, a2) - 20 ~ 60 deg vs 27-141 deg needed) is the limiter | Bench + L1 keep-out CAD only; no hardware, no subjects | concept doc |
| **Harmony** (UT Austin; rehab, bilateral) | 5 active (girdle: 1 revolute elevation + 1 parallelogram protraction; GH: 3 revolute) / 0 | Active 2-DOF girdle mechanism with a scapulohumeral-rhythm controller; girdle ROM 50 elev / 5 dep / 20 prot / 45 retr deg [R] | Abd 118 (170 with ER), flex 160, ext 45, ER 79, IR 80 deg (Table 3) [R]: **overhead yes**. With the girdle locked, the arm was "impeded to elevate above 80 deg" [R] | "-". Abduction limited by "interference between J5 and the head" [R], i.e. GH links ride above the shoulder [I] | 31.2 kg excluding the frame, bilateral (Table 1) [R] | Acute joint angles a = b = 60, g = 18 deg trade internal-rotation ROM against the J3-J4-J5 singularity (Fig. 4) [R] | Built; ROM and parasitic forces on users | [H1] |
| **ANYexo 2.0** (ETH; rehab) | "All relevant DOF of the human arm" incl. a controlled shoulder coupling [S]; exact count not read | Robot shoulder-girdle elevation joint coupled to humeral elevation, GED = -0.0053 theta^2 - 0.0162 theta + 20.5 deg (<= 96 deg), a 51 deg swing [R, earlier read, gh_translation_literature.md] | "Most ADLs" [S]; joint speeds 200 / 398 / 354 % of ADL needs at shoulder / elbow / wrist [S] | "-" | Not confirmed. A secondary source gives 12.98 kg for "ANYexo", version unclear [S] | "-" (full text rate-limited this session) | Built; motion capture with 2 participants for the coupling [R, earlier read] | [A1] |
| **MGA** (Maryland-Georgetown-Army; rehab) | 4 active (scapula 1 + GH 3) + elbow / passive fit adjustments | 1 active scapula elevation/depression joint, +30 / -30 deg; its axis is normal to the back (Table IV) [R] | GHR1 +180 / -45, GHR2 +90 / -65, GHR3 +210 / -30 deg (Table IV) [R]: overhead yes by joint range | "-"; GHR2 "located to the side and slightly beneath the shoulder" [R] | ~12 kg prototype [R] | Two GH singularities 180 deg apart "can be moved, but cannot be eliminated". J1 tilted 30 deg; J1-J3 at 135 deg at rest "to allow the arm to abduct further" [R] | Built (2 rapid prototypes + final) | [M1] |
| **CADEN-7** (UW; rehab, cable-driven; EXO-UL7 is its later UCLA successor and is not the source of these numbers [red team]) | 3 active GH / 0 | GH as a fixed ball-and-socket (3 orthogonal axes at the humeral-head centre), justified for activities up to 90 deg elevation (sec. II-D) [R] | Table III title: "achieves 99 % of the ROMs required to perform daily activities" [R] | "-"; humeral rotation by an open semicircular rail (3 x 60 deg THK segments) [R, ring_and_shell_hardware.md] | Link 1 3.5 kg, links 2-7 6.3 kg [R] | J1-J3 singularity placed at "anthropometrically hard to reach" poses (ext 47.5 + abd 53.6, or flex 132.5 + add 53.6 deg); movable in 15 deg steps [R] | Built | [C1] |
| **ArmeoPower / ARMin III** (ETH / Hocoma; rehab, commercial) | 3 active shoulder + elbow / 0 | "Ergonomic shoulder actuation" that moves the humeral head, from a simplified shoulder model [S] | IE -90 to +90 deg [S, via ring_and_shell_hardware.md] | "-" | "-" | "-" | Commercial. Comfort study (20 subjects): only marginally better than a ball-and-socket design [S] | [AR1, AR2] |
| **NESM-gamma** (SSSA; rehab) | 4 active (3 shoulder + elbow) / **6 passive** shoulder self-alignment DOF: P1 vertical slider; P2-P4, three planar pins "allowing free translation and rotation on the horizontal plane"; P5-P6 ball joints on the trunk link. A 7th, P7, is a forearm linear guide [R, red team re-read sec. II] | Passive chain; median GH-COR deviation < 20 mm and shoulder RMSE < 5 deg with it unlocked; up to 50 mm when locked (8 subjects) [R, red team re-read of the TNSRE abstract; was S] | IE 116 deg [R]; elevation range not read | "-" | ~12.8 kg, **movable part only** [R] | "-" | Built; 8 subjects | [N1, N2] |
| **Dampace / Limpact** (Twente; rehab) | 3 rotations, decoupled from passive translations [S] | Self-aligning: rotations decoupled from passive translations [S] | "-" | "-" | "-" | "-" | Built | [D1] |
| **ABLE** (CEA; rehab / haptics) | 3 active shoulder + elbow (4-axis) / 0 | None stated | One shoulder axis 110 deg, elbow 130 deg (Table I amplitudes) [R] | "-"; the 2nd joint is a circular guide, "free of singularity and not invasive" [R] | Table I: ~3.0 kg and ~10.0 kg (column assignment unclear in the text) [R] | Circular-guide joint (no 3R singularity at that axis) [R] | Built | [AB1] |
| **BONES** (UCI; rehab, pneumatic) | 3 shoulder + elbow (4 DOF) via a parallel mechanism with 2 passive sliding rods / 0 | None (fixed GH) [I] | Shoulder 105 / 80 / 100 deg about an arm-horizontal home (Table I) [R]: elevation not to full overhead [I] | "-" | 18.5 kg total incl. grounded actuators; 4.36 kg moved by the user [R] | ZYX singularity "not in the range of motion" [R] | Built | [B1] |
| **CAREX** (Columbia; rehab, cable-driven cuffs) | 3 rotations controlled via 7 cables / 3 GH translations "not controlled" [R] | GH centre estimated in real time from cable lengths (< 1.5 cm error, simulation) [R] | Not given ("as high as he can") [R] | Cuffs on the skin; cables in the air [I] | 1.32 kg incl. orthosis [R] | None (no serial chain) [I] | Built; 1 subject | [CX1] |
| **ASU SPM + slip** (Hunt, Artemiadis, Lee) | 3-DOF spherical parallel manipulator / 2-DOF passive slip (1 rot + 1 trans) [S] | Slip interface absorbs GH translation [S] | Spherical surface centred on the shoulder [S] | "-" | ~5.4 kg excl. power and controller (patent) [S] | Parallel (SPM) [S] | Built | [P1] |
| **CXD scissors shoulder** (Aalborg; compact remote centre) | 3 GH rotations (scissor SPM, serial-equivalent) + 1 elevation joint / 0 [R] | 1 shoulder-elevation DOF [R] | 0.236 m3 = 68.1 % of the full and 95.0 % of the protraction-locked reachable workspace (1 subject) [R]; IR / ER 46 / 58 deg [R] | Sphere radius **60 mm** (Table 2) [R]. On our body a 60 mm shell sits -11 / 12 / 20 mm (p10 / 50 / 90) off the cap at rest and is inside the body in 75-83 % of directions overhead [est., section 3] | "-" | "Practically singularity-free"; singular only fully folded / stretched, kept out by an 8 deg intrusive angle [R] | Built (3D-printed steel links); 1 subject | [X1] |
| **Double-parallelogram shoulder** (Christensen & Bai 2018) | 3 rotations about a remote centre [S] | None stated | Singularity-free in the shoulder workspace [S, via X1] | "Protrudes out of the shoulder region", "lack of compactness" [R, critique in X1] | "-" | Singularity-free [S] | Prototype | [X1, DP1] |
| **Passive industrial**: ShoulderX, AirFrame (Levitate), EksoVest, Ekso EVO, Skelex 360-XFR, Paexo (Ottobock), Hilti EXO-O1 / EXO-S | 1 assisted elevation axis + passive joints (typical) [I] | Passive alignment joints [I] | Overhead work is the use case; Ding 2023's own passive exo: flexion 150.7 +- 3.0 deg with the exo vs 155.2 +- 4.9 without (Table 2) [R] | "-" (none publish it) | ShoulderX 3.17, AirFrame 2.7, EksoVest 4.3, Skelex 2.5 (Table 1 does not name the model; "360-XFR" removed by red team), PAEXO 1.9, Comau MATE 3.5 kg (Table 1) [R]; assist 5.5 (MATE) to 13 N.m (EksoVest) [R, red team]; Ekso EVO 4.1 kg (datasheet) [S]; Hilti EXO-O1 < 2 kg, EXO-S 2.4 kg [S]; Skelex 360 2.85 kg [S] | n/a (1 DOF) | Sold commercially; lab and field studies | [I1-I5] |
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
  stall [R]. **[Red team.]** These mix ratings: Harmony's 34.4 is continuous torque (Table 1), MGA's 92 is stall torque
  (Table IV). ABLE's 18 could not be re-checked (HAL bot wall); its abstract states ~40 N continuous at the hand.
  Passive industrial exos give **5.5-13 N.m** [R, Ding 2023 Table 1; red team corrected from 6-13]. Routing actuation into a 14 mm band is unsolved
  (docs/research/sim_to_real_gaps.md G1: cable tension 0.9-2.2 kN at a hub-radius pulley).
- **Validation.** One rig body. Its girdle law under-predicts GH lift 2-3x, with 16-51 mm vector error at 90-135 deg
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

---

## Red team (independent re-check, 2026-10-16)

Written by a reviewer who did not write the survey above. It took a 40 min time box. Sources were re-read in full
where they could be fetched: Harmony, MGA, CADEN-7, NESM-gamma (RA-L and TNSRE), BONES, CXD, Ding 2023 (Europe PMC
XML) and Jarrasse & Morel 2010. Pages that could not be fetched were read through search excerpts or patent pages,
marked [S]. Corrections made above are marked "red team" in place.

### A. Numbers re-checked at the source (32 checked)

**Confirmed [R].**
- **Harmony** [H1].
  - Table 1: 31.2 kg excluding the frame; 34.4 N.m continuous at the shoulder.
  - Table 3: abduction 118 (170), flexion 160, extension 45, ER 79, IR 80 deg.
  - Sec. 6.1: girdle 50 / 5 / 20 / 45 deg.
  - Sec. 3.2: a, b, g = 60 / 60 / 18 deg. The Fig. 4 caption ties smaller a, b to the internal-rotation singularity.
  - Sec. 6.2: girdle locked -> "impeded to elevate above 80 deg"; abduction limited by "J5 and the head".
- **MGA** [M1].
  - Table IV: GHR1 +180 / -45, GHR2 +90 / -65, GHR3 +210 / -30, scapula +30 / -30 deg; 92 N.m stall.
  - Sec. III-B: J1 tilted 30 deg; 135 deg J1-J3 angle at rest.
  - Sec. VI: "about 12 kg".
- **CADEN-7** [C1].
  - Table III title: 99 % of ADL ranges.
  - Sec. III-D: 3.5 / 6.3 kg; GH modelled as a ball and socket "up to 90 deg of arm elevation".
  - Sec. IV-D: singularity at 47.5 + 53.6 deg and 132.5 + 53.6 deg; movable in 15 deg steps.
  - Sec. IV-B: three 60 deg THK curved-rail segments.
- **NESM-gamma** [N1, N2].
  - Sec. II: 12.8 kg ("the movable part"); P1 slider; P2-P4 planar pins; P5-P6 ball joints; IE 116 deg.
  - TNSRE abstract: 8 subjects; RMSE < 5 deg; median GH-CoR deviation < 20 mm; up to 50 mm when locked.
- **BONES** [B1].
  - Table I: 105 / 80 / 100 deg.
  - Sec. II-D: 18.5 kg total; 4.359 kg moved (3438 + 921 g); the ZYX singularity "is not in the range of motion".
- **CAREX** [CX1].
  - 1.32 kg including the orthosis; 7 cables controlling 4 DOF.
  - GH centre error < 1.5 cm, in simulation only; translations "not controlled"; one subject.
- **CXD** [X1].
  - Table 2: R 60 mm, alpha 35 deg, beta 8 deg, pitch 32-136 deg.
  - Sec. 3: ER / IR 58 / 46 deg; 5 DOF in total (elevation + 3 SSM + elbow).
  - Sec. 4: 0.236 m3 = 68.09 % / 94.97 %; one subject.
- **Ding 2023** [I1].
  - Table 1 masses: ShoulderX 3.17, AirFrame 2.7, EksoVest 4.3, Skelex 2.5, Paexo 1.9 kg.
  - Table 2: flexion 150.72 +- 2.97 deg with the exo vs 155.16 +- 4.88 deg without.
- **Our own row** (docs/concepts/skin-normal-3r-pin-knee.md, "Verified numbers").
  - 30.35 / 88.96, reach 0.6056, in-band 0.9043, contact 0.0091.
  - Window [43.7, 104.4] = 60 deg; needed 27-141 deg (22-146 overhead).
  - Hub 2 at 93-115 mm, gap 64.54-79.55.
  - Cable tension 0.87-2.2 kN (sim_to_real_gaps.md).

**Confirmed [S]** (search excerpts or patent pages):
- ASU: 5.4 kg excluding batteries and controller (US 10,800,031). Its slip is one passive cuff joint, 1 rotation + 1
  translation: an inner cuff sliding axially in an outer cuff (US 10,814,473, Google Patents page).
- Myoshirt: +51.1 s (36.1 %) to fatigue onset; -49.1 % muscle activity in the functional task; actuator + box 4 kg;
  10 + 2 participants.
- Proietti 2023: 150 g per limb; 10 people with ALS.
- Ekso EVO: 4.1 kg on the maker's sheet. Retailer listings give 4.3 and 7.8 kg.
- Hilti EXO-S: 2.4 kg.

**Wrong or unsupported (corrected or flagged in place):**
1. **Passive industrial assist "6-13 N.m" (also "6.1-13").** Wrong lower bound. Ding 2023 Table 1 lists Comau MATE at
   5.5 N.m, so the commercial range is **5.5-13 N.m**; with research devices (Rossini 3 N.m) it is 3-13. Corrected in
   sections 1 and 5 and in the table.
2. **"Skelex 360-XFR 2.5 kg (Table 1)".** Table 1 says "Skelex (de Vries et al., 2019)" and names no model. Corrected.
   MATE (3.5 kg) was added; it was missing.
3. **"Rehab exos 18-92 N.m".** This mixes Harmony's continuous rating (34.4) with MGA's stall rating (92). ABLE's
   "18 N.m" could not be re-checked: HAL returned a bot wall to curl and to the fetcher. ABLE's abstract gives
   "around 40 N continuous effort at the hand". Flagged in place.
4. **NESM-gamma "~12.8 kg".** This is the movable part only (sec. II). "6 passive DOF" is right for the shoulder, but
   the device carries a 7th passive DOF, P7, a forearm linear guide, so it has 2 passive translations in all. Three
   of its passive joints, P2-P4, are pins that absorb planar translation. That bears on novelty claim 3.
5. **"CADEN-7 / EXO-UL7".** Every number comes from the 2007 CADEN-7 paper. EXO-UL7 is the later UCLA device.
   Relabelled.
6. **Omitted number (optimistic framing).** The survey reports only the 2-14 mm share (0.904). In the user's 2-10 mm
   aim band the verified share is **0.538**. Added in sections 1 and 2.
7. **"The compact remote-centre class cannot ride a 2-14 mm band by geometry".** Unsupported as worded; see B5.
   Flagged in place.
8. **ANYexo 2.0 mass (12.98 kg, secondary).** Still unconfirmed. The ETH full text is over 15 MB and was not
   downloaded.

### B. Novelty claims, attacked

1. **Fold-versus-skin frontier: weakened.** Coupling singularity placement to clearance from the body is published:
   - **Harmony** [H1, sec. 3.2, Fig. 4] trades J4's clearance from the shoulder and head against the J3-J4-J5
     singularity through the same axis angles. It says that body-surface interactions are "impossible to model
     accurately" and settles the trade with 3D-printed mock-ups.
   - **Carmichael & Liu 2015** (Springer STAR 105:245-258, doi 10.1007/978-3-319-07488-7_17) [S]: a genetic algorithm
     maximises the shoulder exo's ROM "whilst taking into account collisions and kinematic singularities".
   - **Keemink et al. 2018** (IEEE TNSRE 26(4):817-829, doi 10.1109/TNSRE.2018.2811503) [S]: a non-orthogonal
     redundant 4R shoulder that avoids the 3R's singularities "and collisions with the human head, arm and trunk".
     **Lo & Xie 2014** (Robotica) [S] analyse the 3R's ROM loss near singularity and optimise a redundant 4R over 89
     workspace positions.
   - What survives is the two-sided version. It has an upper bound on stand-off (14 mm), not only "no collision". It
     gives a quantitative frontier (window 60 deg vs 27-141 deg needed; hub 2 at 93-115 mm) on one body.
   - It is a negative result for the GH-ray-hub 3R. It does not cover the redundant non-orthogonal 4R, which the
     field uses to escape the fold. The 4R fits the user's cap ("or 4 joints"), though the user prefers 3 DOF.
2. **2-slide closure theorem: weakened.** **Jarrasse & Morel** give the general constructive rank / isostaticity
   condition for passive fixations (RSS 2010, p15; journal version IEEE T-RO 2012, "Connecting a human limb to an
   exoskeleton", not re-read).
   - For an exo ball joint at M1, the arm fixation must generate 3 independent velocities at M1. They name the
     options: three translations, or "two pivot joints perpendicular to the arm main axis and one translation joint
     collinear" with it [R, RSS 2010 sec. III].
   - Our statement is a special case: J1 and J2 on GH rays make the drift planar, so 2 freedoms suffice. It may be new
     as that special case. It should be stated as a corollary of the isostaticity condition, not as a theorem.
   - Caveat: with 2 freedoms instead of 3, the loop is isostatic only while the drift stays exactly planar. Real
     scapular motion and soft tissue break that; the knee-window losses (23 poses) hint at it.
3. **Two-pin planar knee, 0 passive translations: weakened.**
   - Pins that absorb translation are published:
     - Jarrasse & Morel: two pivots perpendicular to the arm at the cuff, plus one slide.
     - NESM-gamma: P2-P4, three planar pins "allowing free translation ... on the horizontal plane".
     - Harmony: a pin parallelogram that translates the GH centre (active).
   - The ASU patent US 10,814,473 does **not** anticipate the knee. Its slip is a translational cuff (1 rotation + 1
     translation) [S, Google Patents page; the USPTO PDF is a scan].
   - What survives: the specific layout, two pins in hub 3's plane with no slide, closing a GH-ray-hub 3R. It was not
     found in this time box.
4. **Proximity-scored bench: weakened.** Collision-aware design optimisation on human-body models is established:
   - Carmichael & Liu 2015.
   - Keemink 2018.
   - A human-centred kinematic optimisation from HIT (human-device geometric constraints, MOPSO) [S].
   - Offset-from-scan design at 2-5 mm with intersection checks, standard in custom protective gear and orthoses
     (e.g. US 11,826,632) [S].
   - What survives: a per-point, two-sided skin-distance band on posed skins over clip and workspace poses, re-measured
     by an independent verifier under a frozen-shape protocol. No direct prior was found.
   - It is a methods contribution, not a device result. Nobody else optimises this metric, so leading on it shows
     difference, not progress, until the band is shown to matter to wearers (comfort, clothing, snag).
5. **Concentric-shell yardstick: holds as a number, but the conclusion overreaches.**
   - It tests a full sphere of rays, including rays into the arm and the trunk. A real CXD-type mechanism occupies a
     patch that moves with the arm, and at rest 37 % of directions are in band, so a patch could exist.
   - Our own leader is also a remote-centre (concurrent-axis) 3R. What differs is that its links are not on one
     constant-radius sphere.
   - The comparison is not like for like. Ours is a share of metal points; the shell's is a share of directions.
   - The supportable statement: links of one constant radius around GH cannot stay in band over the cap. That is
     the CXD and scissor-SPM subclass, not "the compact remote-centre class".

### C. Prior art the survey missed

- Jarrasse N, Morel G. RSS 2010, "On the kinematic design of exoskeletons and their fixations with a human member"
  (https://roboticsproceedings.org/rss06/p15.pdf) [R]. Journal version: IEEE T-RO 28(3), 2012 (not re-read). This is
  closure / isostaticity theory, with a worked 4-DOF shoulder-elbow example.
- Naf MB et al. "Misalignment compensation for full human-exoskeleton kinematic compatibility: state of the art and
  evaluation". *Appl Mech Rev* 70(5) [S]. A review in 9 categories; the right yardstick for claim 3.
- Keemink AQL, van Oort G, Wessels M, Stienen AHA (2018). Redundant non-orthogonal 4R shoulder. *IEEE TNSRE*
  26(4):817-829 [S]. It handles singularity and body collision together, inside a 4-joint cap.
- Lo HS, Xie SQ (2014). "Optimization and analysis of a redundant 4R spherical wrist mechanism for a shoulder
  exoskeleton". *Robotica* [S]. Section 6 cites "Lo & Xie (cited in X1)" but this paper was not reached.
- Carmichael MG, Liu DK (2015). Biomechanical-model-based optimal design of a shoulder exo (ROM vs collisions vs
  singularities) [S].
- suitX (US Bionics) US 12,029,699 B2, priority 2020-03-19 [S]: a passive remote-centre shoulder joint whose stated aim
  is that it "minimizes the profile of the device" throughout its range of motion. Low profile over ROM is therefore
  already an explicit commercial design objective, though unquantified.
- AssistOn-SE (Ergin & Patoglu, ICRA 2012) [S]: a self-aligning shoulder-elbow exo that uses passive GH-centre
  translations. Harmony cites it.
- Awad et al.: a 3-PRR double-layered elbow interface, +-15 deg and 30 mm self-alignment [S]. A published
  self-aligning cuff closure.
- Ding 2023 Table 1 entries left out of the table: Comau MATE (3.5 kg, 5.5 N.m), Hyundai H-VEX (2.5 kg, 10 N.m) and
  H-PULSE (5 kg, 5.5 N.m) [R].
- **A published protrusion number exists, though not peer reviewed.** A Northern Arizona University capstone shoulder
  exo (2022) set "cannot protrude more than 10 cm from the body" and reports 4.5 in at maximum [S]. Hilti publishes the
  EXO-S envelope as 450 x 250 mm [S]. "Nobody publishes stand-off" should read "no peer-reviewed shoulder exo found
  reports a measured stand-off distribution".

### D. Bottom line

Real progress against the state of the art has not yet been shown. What exists is a new simulated design point on one
axis: metal held 2-14 mm off a posed skin (0.904, but only 0.538 at the user's 10 mm aim) with 3 pins and 2 passive
pins, on one rig body. Its enabling ideas have close prior art: singularity vs body clearance (Harmony, Carmichael &
Liu, Keemink), pin-based fixation closure (Jarrasse & Morel, NESM-gamma), collision-aware optimisation on body models,
and low profile over ROM (suitX). On range (0.25 overhead), hardware, actuation and validation it trails every built
device. For the claim to hold:
- build MVP1 and measure stand-off on the user at rest, 90 deg and overhead, with in-band >= 0.9 and zero contact;
- lift overhead reach to >= 0.6 (test the non-orthogonal redundant 4R inside the 4-joint cap alongside the round-4
  fold levers);
- re-measure on the user's scan and the literature girdle law;
- read Jarrasse & Morel 2012 and Cempini 2013 in full before calling the closure or the knee new.
