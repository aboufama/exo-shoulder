# Sim-to-real gaps: how the exo could pass in simulation and still fail on a person

Red team, 2026-10-15. The question (user): "is there anything else from the simulation to real like this that could
affect actual feasibility? if so, you need to make sure these are not missed!", and earlier: "if there's some slight
friction perhaps it will be hard for a linkage to pass over another because it's pressing from a bad action angle ...
It needs to actually work".

What this covers: the target design. That is an exactly-3-DOF serial chain (a 4R as the comparison) of thin
Ti-6Al-4V links whose axes pass through the GH centre. It rides 2-14 mm off the skin (aim 10). The base is a saddle
over the acromion / scapular spine on the user's scapula handler. The arm end is BOTTOM + cuff, and the forearm uses the
user's parts. The joints are v4 iglidur plain stacks (docs/HARDWARE.md).

How it was done:
- Desk study of the exo literature. Every source has a URL at the end; "(excerpt)" means only a search-engine excerpt
  was read.
- Reading the judges, to see what each one actually measures.
- Four small local CPU checks, whose numbers are tagged **[new]**. The scripts are listed in section 5.

What was not done: nothing was downloaded, no GPU or RunPod was used, no CAD or user part was touched, and no design was
changed. No scorecard number moves because of this document.

---

## 0. Bottom line

1. **The judges assume a world that holds still.** The exo is a rigid body, the arm is a rigid body, the two are
   welded together at the cuff, and their pivots coincide. R1 asks the metal to stay in a 12 mm wide band (2-14 mm), with
   a 2 mm floor. On a real person, at least ten effects move the metal relative to the skin. None of them is in any
   judge, and several are each larger than the whole band (section 2).
2. **Top 5 killers, in order:**
   1. The actuators and their transmission have nowhere to go.
   2. The assist reaction has no acceptable path at the scapula saddle.
   3. An exactly-3-DOF chain with a rigid cuff is over-constrained: the error in where the GH centre is assumed to be
      has nowhere to go but the skin.
   4. The arm interface is soft. Under assist the cuff moves 11-27 mm, and humeral rotation barely transmits.
   5. The 2 mm floor has no stiffness behind it, so both link deflection and everyday pushes close it.
3. **The user's friction worry is real, and now it has a number [new].**
   - In a plain bearing, friction grows with the tilting load the joint carries. Under that model, the six 3R search
     winners (r14 and r15) self-lock when the joints' effective friction coefficient reaches **0.22-0.30** (worst frame,
     always "Wash opposite shoulder"), and the r14 4R at **0.12**.
   - The v4 joint sits at about 0.06-0.18 while its thrust washers carry the tilt. It reaches about 0.37 if wear lets the
     sleeve carry it, and at 0.37, 18-38 % of 3R frames lock.
   - The margin today is 1.2-3.7x. Motors hide the problem while powered. They do not hide it with the power off, or in
     how the exo feels in the hand.
4. **Mechanical end stops cannot keep a powered 3R inside the human range of motion [new].**
   - The tightest per-joint stops that still pass the 8 clips allow 5-12 % of the reachable box to lie more than 20 deg
     outside a generous everyday ROM, and up to 52-67 deg outside.
   - Safety at the ROM limits is therefore software-only.
5. **19 of the 20 gaps need something from the user**: data, a decision or an approval. The ones that block real
   work are G1-G5, G8 and G9. The list is in section 4.

---

## 1. The top 5 killers (2-minute read)

**1. There is no motor in the model.**
- A powered exo needs three torque sources. Each joint must supply up to the full assist moment: 6-10 N.m in commercial
  overhead exos, and 25 N.m is the design load here.
- The joint was designed as a 23 mm x 10.5 mm plain-bearing puck. The smallest off-the-shelf actuators of that torque are
  far bigger:
  - CubeMars AK70-10 (8.3 N.m rated, 24.8 N.m peak): 89 mm across, 50 mm thick, 521 g.
  - Harmonic Drive CSD-17 gear set alone (11 N.m rated): a 43 mm pitch-circle gear at 0.1 kg, before the motor,
    bearing and housing. That is already about twice the hub's diameter.
  - The AK70-10 is about 70 times the hub's volume and stands 40-50 mm off the skin.
- Moving the motors to the back and pulling cables brings its own problems:
  - Cable tension at the hub radius is 0.9 kN at 10 N.m and 2.2 kN at 25 N.m, per joint.
  - A cable that does not pass along a joint axis changes length as that joint turns (about 28 mm over J3's travel at a
    10 mm offset). The Ø10 pin is solid.
  - Bowden sheaths lose about 20 % or more to friction.
- Until the actuator and its transmission have a keep-out in the L1 CAD, every R1 number describes an unpowered shell.
  Adding the keep-out changes R1 and R2 for every design so far.

**2. The base cannot push back.**
- Whatever moment the exo puts on the arm, it puts the opposite moment on its base.
- The base rides the scapula on a handler that must let the scapula move freely. A free joint carries no load along the
  direction it is free to move.
- The scapula's main motion during elevation (upward rotation, up to 58 deg on the rig) is about nearly the same axis
  as the elevation-assist reaction. So that reaction goes into the skin over the acromion and spine.
- A rigid saddle on soft tissue that reacts 10 N.m peaks at about **100 kPa** if it is 60 x 100 mm. Healthy people
  report discomfort from sustained pressure at about **14 kPa** and pain at about 53 kPa.
- Staying under 14 kPa needs a saddle about **230 mm long at 10 N.m, or 370 mm at 25 N.m**. That is longer than the
  bony region that tracks the scapula. The saddle cannot be small enough to track the bone and large enough to spread
  the load.
- The same moment also rotates the saddle on the skin. That adds load-induced misalignment on top of the kinematic skin
  slip that R10 plans to model.
- This must be settled against the user's handler design before any further skin-hug tuning.

**3. The exo's pivot is never exactly at the shoulder's pivot.**
- A 3-DOF rotation chain turns about one fixed point on its base. The arm turns about its own GH centre. With a rigid cuff
  the two are locked together, so any distance e between those points becomes a forced shift.
- Over the clips the humerus turns up to 97.5 deg relative to the scapula. So the arm end of the exo is dragged by up to
  **1.5 e** relative to the arm **[new]**: 15 mm for a 10 mm error, 22 mm for 15 mm.
- If the skin absorbs it, that is **30-68 N per 10 mm of error**.
- No skin-surface method finds the GH centre better than about 11-17 mm (functional methods); regression rules are about
  30 mm off. The humeral head also translates 3-4 mm in the glenoid, and the saddle slips 4-20 mm.
- Keeping the arm end within 4 mm of where the judges put it needs e <= 2.7 mm over the whole motion.
- The field's answer (Jarrassé & Morel; Stienen 2009) is passive self-aligning DOFs at the fixations. That collides with
  the user's DOF counting rule, so it is a user decision.

**4. The arm is soft.**
- The one published measurement of an upper-arm exo interface found here (21 adults, overhead posture) moves:
  - 2.1 N/mm along the arm and about 4.5 N/mm across it;
  - 0.2 N.m/deg in tilt;
  - **0.03 N.m/deg** in twist about the arm's long axis.
- Pushing the arm up with 10 N.m through a cuff 0.2 m out therefore moves the cuff about **11 mm** relative to the
  bone, and 25 N.m moves it about **27 mm**. The arm end of the exo leads the bone by 3-8 deg. The red team found the
  push lands on the knit band, which is softer still.
- In twist the interface is almost slack. Driving the 3R designs by the arm needs 0.9-2.7 N.m about the humerus per
  N.m of joint friction **[new]**. So every 0.1 N.m of friction leaves the exo about **9 deg behind** the arm in rotation.
  Skin also misses 20-48 % of true humeral rotation.
- None of this is in any judge. Every judge welds the exo to the bone.

**5. Two millimetres is not a gap you can hold.**
- The thin links carry the assist moment mostly by bending through their thickness. The in-house FEA gives a long 5.5 mm
  link about 7 N.m/deg (2.4 N.m/deg at the as-built 4 mm).
- That puts the arm-end hub of the 3R chain up to about **7 mm** off its unloaded position at 10 N.m, and about 17 mm at
  25 N.m (worst direction, estimate).
- Separately, the shell is held off the skin only by the soft mounts at its two ends (2-5 N/mm). A **4-10 N** push
  closes a 2 mm gap. A bag strap, a seat belt, a chair back, the other hand, or lying on that side all push that hard.
- "Never touches the skin" is only true with nothing touching the exo. The user must decide whether, under load, a
  designed liner may touch, and the strength judge (R9) must move geometry, not just report stress.

---

## 2. The clearance budget: what moves the metal relative to the skin, against a 2-14 mm band

| effect | size | source | in a judge today? |
|---|---|---|---|
| GH-centre fitting error (functional methods 11-17 mm; ISB regression ~30) carried through the clips (shift <= 1.5 e) | 16-45 mm at the arm end | GH-centre accuracy studies + `rt_misalign.py` **[new]** | no |
| GH translation inside the glenoid during elevation | 2.9-4.3 mm | Dal Maso 2015 bone pins (gh_translation_literature.md section 5) | no |
| saddle skin slip over the scapula (orientation error x 46 mm AC-GH lever) | 4-8 mm below 100-120 deg, ~20 mm above | Karduna 2001, van Andel 2009 (same note, section 7) | R10 NOT RUN (model to build) |
| saddle rotation under the assist reaction (assumed 1-3 N.m/deg; arm cuff measures 0.1-0.34) | 2.7-8 mm at 10 N.m | estimate from Schiebl 2025 | no |
| cuff migration under assist (4.5 N/mm across, 203 mm lever) | ~11 mm at 10 N.m, ~27 mm at 25 N.m | Schiebl 2025; red team `cuffload.json` lever | no |
| chain deflection (in-house link stiffness) | up to ~7 mm at 10 N.m, ~17 mm at 25 N.m | thin_study REPORT; estimate in G5 | no (R9 is stress only, UNVERIFIED) |
| force that closes the 2 mm floor (mount stiffness x 2 mm) | 4-10 N | Schiebl 2025 | no |
| muscle thickening under load (~10 % of a 15-25 mm deltoid) | 1.5-2.5 mm and more where it bunches | ultrasound, rectus femoris 23.4 -> 25.7 mm at MVC (excerpt) | rig: <= 0.6 mm **[new]** |
| breathing (trunk skin near the axilla / chest) | 1-2 mm tidal, up to ~6-11 mm deep breath (4-7 cm chest expansion) | chest-expansion norms (excerpt) | no |
| clothing between skin and metal | 0.5-1 mm (T-shirt) to 3-6 mm (sweater), estimate | - | no |
| worn joint play (sleeve clearance / sleeve length x lever) | 0.1-2 mm per link | estimate, G17 | no |
| body-shape spread, 5th-95th percentile arm radius | about +-7-8 mm | ANSUR II flexed biceps circumference SD (from memory, verify) | R14 NO DATA |

These do not all point the same way at the same time. Still, the fitting error is fixed for each donning, and cuff
migration and deflection follow the load direction. Each of those can use up the band by itself, so a design that
passes R1 in the rig has no margin left on a person.

---

## 3. The register, ranked by how likely each gap is to kill feasibility

| # | gap | caught by a judge today? | proposed judge / test | needs the user |
|---|---|---|---|---|
| G1 | actuators + transmission have no keep-out | no (R8 counts custom metal only) | R16 actuation fits: torque / speed / power per joint + transmission keep-outs in L1, MuJoCo tendons | **decision**: actuation concept, assist spec, motor location, whole-system mass |
| G2 | assist reaction at the scapula saddle (pressure; load-induced slip) | no (R10 NOT RUN, R11 not measured) | R17 reaction path: handler wrench space (screw theory) + saddle pressure (Winkler / CalculiX) + load-induced R10 | **data**: scapula-handler CAD + DOFs; 5-min stiffness test |
| G3 | hyperstatic loop: GH-centre error, GH-in-glenoid, slip, no self-alignment | no (exo centre = rig GH by construction) | R18 kinematic compatibility: (I-R)e shift + interface force, MuJoCo / Drake spring fixations | **decision**: passive fixation DOFs?; how the GH centre is located at fitting |
| G4 | soft arm interface: cuff migration, axial-rotation lag, skin artefact | not on the scorecard (`judge/dynamics.py` in progress models the cuff spring) | R19 loaded fit: assist wrench through a measured 6x6 interface stiffness, re-run R1/R2/R6; axial-lag judge | **decision**: how the assist is applied, where humeral rotation is sensed; 10-min stiffness test |
| G5 | 2 mm floor vs link deflection and external pushes | no (R9 stress only, UNVERIFIED) | R20 loaded clearance: CalculiX deflected parts -> R2/R6; external-load cases | **decision**: may a liner touch under external load?; target assist torque |
| G6 | load-dependent friction self-locks the chain; backdrivability; rotator-cuff load | partly (transmission.py and judge/dynamics.py: constant friction only) | R21 no self-locking: alpha* >= 20 deg every frame + force term; bench breakaway test | approval to buy igus parts + print a test joint |
| G7 | pinch, shear, crush; other hand, hair, head | no (R2/R6 see interpenetration only) | R22 pinch: closing gaps 4-25 mm with force behind them (coal / FCL distance over trajectories) | **decision**: safety standard (ISO 13482 vs IEC 80601-2-78), covers allowed? |
| G8 | joint stops cannot hold the arm in its ROM | no | R23 safe ROM: stop box vs the wearer's measured ROM; software limits + overpowerable torque | **data**: the wearer's max-ROM trials (OpenCap) |
| G9 | real motion faster / wider than the 8 clips; workspace boundary; singularity | partly (R3/R4 on 8 clips, red-team grid) | R14 on OpenCap + AMASS, plus 2-3x time-scaled clips; actuator speed and power | **data**: OpenCap; AMASS / SMPL-X licences |
| G10 | skin does not deform like the rig: bulge, folds, breathing, head / neck | partly (rig activation, P2 planned) | scans relaxed / loaded / overhead / deep breath -> R1/R2; head-neck sweep | **data**: extra scan poses |
| G11 | body-shape spread: one rig, one size | no (R14 NO DATA) | SMPL-X shape sampling; per-user fit from scan | **decision**: one-off for the user or a product; licences |
| G12 | clothing, hair, donning | no | garment offset layer in R1/R2; donning-time test on the prototype | **decision**: worn over skin / base layer / under clothes; who dons it |
| G13 | sensor / power wires across rotating joints | no | wire-path keep-out per joint (hollow pin or spiral flex), flex-life test | decision: joint sensing required? |
| G14 | interface pressure over hours: R11 cites a collision standard | no (R11 NOT MEASURED) | R11 threshold rewritten for sustained wear; pressure film / FSR on prototype | decision: wear duration per session |
| G15 | judges sample time too coarsely (tunnelling) | the judges themselves | continuous collision or adaptive sub-steps (<= 0.5 mm motion per step) | approval to install coal / FCL (pip) |
| G16 | worn mass and inertia not budgeted | partly (R8, custom parts only) | R8 -> whole worn system + exo inverse dynamics at real speeds | decision: whole-system mass budget |
| G17 | joint play, wear, tolerances | no | per-joint play-vs-cycles model; R2/R6 at the worn limit; bench wear | - |
| G18 | fatigue and the real material process | no (R9 UNVERIFIED) | CalculiX fatigue on a measured load spectrum, process-specific S-N | decision: CNC billet vs LPBF (R13) |
| G19 | materials against sweat and skin (7075-T6, galvanic, nickel) | no | material / finish review at L2; sweat / salt test | decision: anodise vs bare finish |
| G20 | the wearer's own shoulder differs from the healthy average | no | everything above re-run on the wearer's OpenCap and scans | **data**: OpenCap of the wearer |

---

### G1. Actuators and transmission have no keep-out (rank 1)

- **Mechanism.**
  - A powered 3-DOF chain needs three torque sources (the user's "less actuators" counts one per joint).
  - In a chain whose axes all pass through GH, joint i must supply tau_i = u_i . M, which is up to |M|, the whole assist
    moment, at every joint.
  - The geometry every judge sees has no motor, gearbox, pulley, cable, sheath, electronics or battery.
- **Evidence.**
  - Assist level: commercial overhead exos give about 6.1 N.m (Skelex) to 10 N.m (ShoulderX, 3.17 kg)
    [PMC10936402]. The design load here is 25 N.m (R9).
  - Motors on the joint:
    - CubeMars AK70-10: 8.3 N.m rated / 24.8 N.m peak, Ø89 x 50.25 mm, 521 g [CubeMars].
    - Harmonic Drive CSD-17-50-2A gear set: 11 N.m rated / 23 N.m peak, 0.1 kg [HD], with the motor, bearing,
      encoder and housing still to add. Size 17 is a 1.7 in (43 mm) pitch-circle gear.
    - The v4 hub is Ø23 x 10.47 mm (docs/HARDWARE.md). The AK70-10 is about 70 times its volume; the gear set alone is
      already about twice its diameter.
    - Three on-joint actuators weigh about 1.5 kg and stand 40-50 mm off the skin, against the 14 mm band.
  - Motors on the back, driving the joints through cables or tendons:
    - Cable tension is T = tau / r: 870 N at 10 N.m and 2.2 kN at 25 N.m for a pulley at the hub radius (11.5 mm),
      each way.
    - A bigger pulley breaks the hub keep-out.
    - Bowden transmission efficiency: at best 78.7 %, measured on a knee exosuit, and it depends on bending and length
      [PMC9352506].
    - A cable offset d from a joint axis changes length by d x dq: 27-28 mm at d = 10 mm over J3's 152-163 deg stop span
      **[new, rt_jointbox.py]**. That couples the joints unless every cable crosses every joint on its axis, and the
      Ø10 pin is solid.
  - Reflected rotor inertia J_m N^2 adds to what the wearer feels in fast moves (G16).
- **Caught by:** nothing. R8 counts custom metal only: 110.9 g on `l1_r14_3r_s1351_1`.
- **Proposed judge R16 "actuation fits".**
  - (a) Per joint and per clip, tau(t) = U(t)^T M(t), with M from arm gravity plus a payload. Use OpenSim inverse dynamics
    (Seth 2016 or MoBL-ARMS, already approved), with joint rates from `transmission.py`. This gives p99 torque, peak
    speed, RMS torque (continuous rating) and peak power.
  - (b) Actuator and transmission keep-outs in L1 CAD:
    - on-joint: a motor cylinder;
    - remote: a pulley of radius r_p, a sheath path at >= 10x sheath diameter bend radius, and sheath stops.
  - (c) Re-run R1/R2/R6 with the keep-outs.
  - (d) MuJoCo spatial tendons with wrap sites for cable length vs joint angle (coupling) and tension.
  - Thresholds:
    - every joint meets its p99 torque and peak speed with SF 1.5 at the transmission's efficiency;
    - the keep-outs pass R2/R6;
    - total worn mass is within the user's budget.
- **Needs from the user (decision):**
  - which joints are powered;
  - continuous / peak assist torque and its directions;
  - where motors may sit (on the back, on the handler);
  - whether actuators and cables must obey the 1 cm rule;
  - a mass budget for the whole worn system.

### G2. The assist reaction has no acceptable path at the scapula saddle (rank 2)

- **Mechanism.**
  - The moment on the humerus is reacted on the base.
  - The base must follow the scapula (3 rotations, cm of translation) on a handler that the plan requires to be
    torque-free (docs/P0_BASE_MOUNT.md decision 8).
  - A passive joint transmits nothing along its own motion: the wrenches a mechanism can carry are reciprocal to its
    twists. So the handler cannot carry a moment about any axis the scapula is free to turn about.
  - Elevation assist is reacted mainly about the anteroposterior axis, which is close to the scapula's upward-rotation
    axis (58 deg on the rig). That share of the reaction goes through the saddle into the skin over the acromion and
    scapular spine.
  - Physiology: the scapular stabilisers then carry the reaction exactly as they carry the deltoid's. The exo unloads the
    GH muscles, not the scapular ones.
- **Evidence.**
  - Peak pressure under a rigid saddle (length L, width w) reacting a moment on a linear (Winkler) foundation is
    p ~ 6M/(wL^2):
    - M = 10 N.m, w = 60 mm: 100 kPa at L = 100 mm, 44 kPa at L = 150 mm.
    - Sustained-compression discomfort in healthy adults is 13.7 kPa (continuous), and pain is 52.9 kPa [Kermavnar,
      knee cuff; excerpt]. Cuff algometry gives 20-42 kPa painful for healthy controls [UL review; excerpt].
    - Staying at or below 14 kPa with w = 80 mm needs L >= 230 mm at 10 N.m and L >= 370 mm at 25 N.m.
  - Only the acromion / spine region tracks the scapula (gh_translation_literature.md section 7). The reference base part
    is 23 x 22 x 33 mm (`redteam/results/skinmotion.json`).
  - Load-induced slip:
    - The measured upper-arm interface turns at 0.10-0.34 N.m/deg [Schiebl 2025].
    - A saddle on bone 3-10x stiffer (1-3 N.m/deg, an assumption) still turns 3-10 deg at 10 N.m. That is 2.7-8 mm at the
      GH centre over the 46 mm AC-to-GH lever.
    - This comes on top of the kinematic skin slip R10 plans to model.
- **Caught by:** nothing.
  - R10 reports NOT RUN for girdle mounts (`judge/base_mount.py`), and its planned model is kinematic skin slip only.
  - R11 is not measured.
  - The red team's pressure work covered the arm saddle, not the base.
- **Proposed judge R17 "reaction path".**
  - (a) From the handler's kinematics, the wrench space it transmits (screw theory).
  - (b) Per frame, the base wrench: assist + cuff force + exo weight + actuator reactions.
  - (c) The part of (b) outside (a) goes into the skin: a pressure map over the saddle footprint. Use a Winkler
    foundation with measured tissue stiffness, then CalculiX contact with a hyperelastic tissue layer over the scapula
    (rig or OpenSim geometry).
  - (d) R10 extended with load-induced rotation, using a measured saddle stiffness.
  - Threshold: peak sustained pressure <= 14 kPa (Kermavnar), and R10 <= 4 mm including the loaded rotation.
- **Needs from the user (data):**
  - the scapula handler's CAD and its DOFs: which motions are free, which sprung or powered, and where it grounds to the
    trunk;
  - the assist magnitude;
  - a 5-minute test: torque wrench and protractor on the saddle strapped to the user.

### G3. Exactly 3 DOF + a rigid cuff = an over-constrained loop; GH-centre error has nowhere to go (rank 3)

- **Mechanism.**
  - A 3-DOF rotation chain fixes a rotation centre c' on its base; the humerus turns about its own centre c.
  - With rigid fixations the human-exo loop is hyperstatic. Jarrassé & Morel give the method for freeing DOFs in the
    fixations to make it isostatic [RSS 2010; T-RO 2012]. Schiele & van der Helm 2006 trace the internal forces to the
    misalignment.
  - For e = c' - c, every arm-end point of the exo moves by (I - R)e relative to the arm, where R is the humerus rotation
    in the base frame since fitting. The shift is uniform over the arm end, with |(I - R)e| <= 2|e| sin(theta/2).
- **Evidence [new, `rt_misalign.py`].** Fitted with the arm hanging, the humerus turns up to 97.5 deg relative to the
  scapula over the clips (Wash 97.5, Comb 95.4, Shelf 93.8, Raise 90.7).

  | centre error e | arm-end shift, worst | median | force if the skin takes it (2-4.5 N/mm) |
  |---|---|---|---|
  | 2.7 mm | 4.1 mm | 2.3 mm | 8-18 N |
  | 10 mm | 15.0 mm | 8.6 mm | 30-68 N |
  | 15 mm | 22.5 mm | 12.8 mm | 45-101 N |
  | 30 mm | 45.1 mm | 25.7 mm | 90-203 N |

  Where e comes from:
  - GH-centre localisation from the skin: 11-17 mm (five functional methods, Lempereur); 14.7-20.7 mm (helical axis /
    SCoRE, Nikooyan); 20.6-21.9 mm (IMU functional); about 30 mm (ISB regression) [PMC5359843].
  - GH translation in the glenoid during elevation: 2.9-4.3 mm (Dal Maso 2015).
  - Saddle slip: G2 and section 2.
  - Cuff migration: G4.
  - Holding the arm-end shift at or below 4 mm (the R10 logic) needs e <= 2.7 mm over the whole motion. That is 4-10x
    tighter than any non-imaging method achieves.
- **Caught by:** nothing for the arm end. Every judge places the exo's centre exactly at the rig's GH centre by
  construction. R10's planned model covers only saddle slip.
- **Proposed judge R18 "kinematic compatibility".**
  - Per frame, sample the misalignment budget: fitting error +-e_fit; GH-in-glenoid from Dal Maso / OpenSim; saddle slip
    from R10; cuff migration from R19.
  - Shift the arm-end parts by (I - R)e and the base by its slip, then re-run R1/R2/R6.
  - Compute the interface force from spring fixations at both ends: MuJoCo weld constraints with solref stiffness matched
    to Schiebl 2025, or a Drake quasi-static solve.
  - Thresholds: shift <= 4 mm, and parasitic force <= 20 N. 20 N leaves room for the assist itself under the 14 kPa
    comfort limit on a 60-80 cm^2 cuff.
  - Second part: a judge of the fitting procedure itself, i.e. the error of the chosen GH-localisation method (for
    example functional calibration using the exo's own encoders).
- **Needs from the user (decision), one of:**
  - (a) allow passive self-aligning DOFs in the fixations (Jarrassé & Morel; Stienen 2009) outside the 3-DOF count;
  - (b) accept soft-tissue absorption, with the forces above;
  - (c) fit from imaging (personal data stays in `data/raw/private/`).
  - In every case: how the GH centre is located when the exo is fitted.

### G4. The arm interface is soft: cuff migration, axial-rotation lag, skin artefact (rank 4)

- **Mechanism.** The cuff grips muscle and fat over the humerus. Under the assist force F = M/d it moves relative to the
  bone. In twist about the long axis the interface is about 7x softer, and the skin does not follow the bone's rotation
  anyway.
- **Evidence.**
  - Measured interface [Schiebl 2025]: 21 adults, overhead posture, pneumatic cuff at 65 mbar.
    - Translation: 2.1 N/mm along the arm and about 4.5 N/mm across (range 1.1-7.0).
    - Rotation: 0.2 N.m/deg perpendicular to the arm (0.10-0.34) and 0.03 N.m/deg about the long axis (0.01-0.06).
    - Valid up to about 30 mm / 30 deg; the tissue is non-linear.
  - Cuff migration: at the red team's 203 mm lever, 10 N.m means 49 N and about 11 mm; 25 N.m means 123 N and about
    27 mm. The arm end of the exo then leads the bone by 3-8 deg about GH.
  - The red team (finding 6) found that 0 % of the elevation push lands on the rigid saddle; the knit band carries it.
    The band is unmeasured and certainly softer than a pneumatic cuff.
  - Interface compliance has to be modelled even to predict the loads: Harmony's sensorized-cuff study [Yousaf 2021].
  - Axial rotation **[new, `rt_wedge.py`]**: driving the 3R designs by the arm needs a moment about the humerus of
    0.9 N.m (median), 2.7 (p95) or 3.7 (max) per N.m of joint friction. At 0.03 N.m/deg, every 0.1 N.m of friction leaves
    the exo about 9 deg (4.5-27) behind the arm.
  - Skin-based humeral axial rotation is underestimated by 20-48 % (Cutti 2005), or up to 35 % [Warner & Heller 2025].
  - Under an assist load (G6 friction of about 1 N.m per joint) the cuff simply turns on the arm. A powered exo then
    has to drive its joints from a measurement of humeral rotation, and skin does not deliver that.
- **Caught by:** not on the scorecard. R3 "follow" is kinematic closure with the exo welded to the bone.
  - `judge/dynamics.py` (in progress, untracked when this was written) puts a 6-axis Schiebl spring at the cuff in
    MuJoCo. Once it is on the scorecard it will report the interaction wrench and the axial lag.
  - It does not move the parts for R1/R2/R6. That is part (b) below.
- **Proposed judge R19 "loaded fit".**
  - (a) Apply the per-frame assist wrench at the cuff through a 6x6 interface stiffness: Schiebl's values until the
    user's are measured.
  - (b) Move the arm-end parts by the resulting displacement (plus chain compliance from G5), then re-run R1/R2/R6 with
    `score_design.py`, `body_contact.py` and `part_contact.py`.
  - (c) Axial lag: humeral-axis driving moment / 0.03 N.m/deg <= 5 deg at p95.
  - Instrument: MuJoCo (weld with solref / solimp tuned to the stiffness) or Drake.
  - Bench: a spring scale and ruler on the user's arm in the cuff (50 N in 3 directions, 1 N.m twist).
- **Needs from the user:**
  - decision: how the assist is applied (a rigid underside pad or the knit band);
  - decision: whether humeral rotation is sensed and driven through the elbow hinge and forearm (the user's own parts,
    which see rotation when the elbow is bent) instead of the upper-arm cuff;
  - data: a 10-minute stiffness measurement.

### G5. The 2 mm floor has no stiffness behind it: link deflection and everyday pushes (rank 5)

- **Mechanism.** The links are curved strips on a sphere about GH. Each joint passes on the moment components that are
  perpendicular to its own axis, and the strips carry those as bending through their thickness and as torsion, so hubs
  move normal to the shell, toward or away from the skin. Separately, a push on the shell from outside is resisted only
  by the soft mounts at the two ends.
- **Evidence.**
  - In-house hex8 FEA (`pipeline/conformal/thin_study/REPORT.md`), link rotational stiffness:
    - 2.4 N.m/deg for a long link as built (4 mm);
    - about 7 N.m/deg for a long link at 5.5 mm (5.4 at 5.0 mm, 8.9 at 6.0 mm);
    - neck 7.5 N.m/deg at 70 mm span; base 18-20; joint hardware 199-267.
  - Estimate for the r14 3R (link arcs 72 + 55 deg, chords about 82 / 65 mm at R 70; stiffness scaled with arc length):
    - at 10 N.m: link 1 tilts about 1.6 deg (its far hub moves about 2.4 mm), link 2 about 1.25 deg, base about 0.5 deg;
    - J3 moves up to 0.5 deg x 150 mm + 1.6 deg x 140 mm + 1.25 deg x 65 mm, about 7 mm;
    - at 25 N.m: about 17 mm;
    - at 4 mm thickness: 2.5-3x more.
  - These are upper bounds: the tilts are summed as if parallel and the load is in the worst direction. CalculiX must
    give the real field.
  - External push: closing 2 mm against 2-5 N/mm takes 4-10 N. Everyday sources: shoulder bag strap, seat belt (it
    crosses exactly this region), chair back, leaning on a wall, the other hand, lying on that side.
- **Caught by:** nothing. R9 is stress only (UNVERIFIED), and R2/R6 use rigid parts.
- **Proposed judge R20 "loaded clearance".**
  - CalculiX static on the L1 parts, as an assembly with the joint stiffnesses.
  - Loads: the per-frame wrench from G1/G4, plus the force through GH (thin_study D2: 200 N gives 11-18 N.m at the hubs).
  - Export the deflected meshes, then re-run R2/R6 on them.
  - Thresholds: body clearance >= 0.5 mm and inter-part clearance >= 0.5 mm at the design assist.
  - External-load cases (20 N normal at any point of the shell; 50 N lying on the side) may make contact only through a
    designed liner at <= 14 kPa.
- **Needs from the user (decision):**
  - is "never touches the skin" required under external loads (then the shell needs its own support) or only in free
    motion (then the liner is a designed contact surface)?
  - the target assist torque;
  - which external loads the exo must tolerate (backpack, seat belt, sleeping).

### G6. Friction that grows with load can self-lock the chain (the user's "bad action angle")

- **Mechanism.**
  - In a plain bearing the friction torque grows with the tilt couple the joint carries:
    tau_f,i = tau0 + mu_eff |M_perp,i|.
  - A joint that must turn while the driving moment is nearly perpendicular to its axis cannot be driven at any force:
    it wedges, like a drawer pulled at its corner.
  - The condition is about action angles. With alpha* = the best achievable worst action angle over the moving joints,
    the chain self-locks iff tan(alpha*) <= mu_eff.
  - `transmission.py` used constant Coulomb friction (amplification <= 4.8x). It computes an action angle but does not
    report it.
- **Evidence [new, `rt_wedge.py`]**, same designs, poses and joint paths as `transmission.py`, 10 fps:

  | design | self-locks at mu_eff >= (worst frame / p5) | worst clip | frames locked at mu_eff 0.30 / 0.37 |
  |---|---|---|---|
  | r14 n3 s1351 rank 0 | 0.296 / 0.342 | Wash opposite shoulder | 0.7 % / 20 % |
  | r14 n3 s1351 rank 1 (the L1 build `l1_r14_3r_s1351_1`) | 0.215 / 0.270 | Wash | 14 % / 38 % |
  | r15 s1361-1364 (four 3R) | 0.216-0.254 / 0.29-0.31 | Wash | 2-13 % / 18-29 % |
  | 4R s1354 (evaluator's path) | **0.120** / 0.234 | Reach back pocket | 44 % / 81 % |

  What the joints actually have:
  - v4 joint: mu_eff ~ mu = 0.06-0.18 (iglidur against steel, igus; static friction higher) while the thrust washers
    carry the tilt.
  - Once wear opens the 0.02 mm washer float, the 4.05 mm sleeve carries the tilt: mu_eff ~ 2 mu r_pin / L = 0.37 at
    mu 0.15.
  - The counterface is Ti-6Al-4V, which is not in igus's test data.
  - The force passing through GH adds tilt at the hubs (R x F; thin_study D2) without adding driving torque. That eats
    part of the 1.2-3.7x margin.
  - The 4R value uses the evaluator's chosen joint path. A real passive 4R may find an easier path, but has no guarantee
    of one.
  - Powered joints overcome this, but three costs stay:
    - (i) with the power off or after a fault, a geared actuator plus wedging can hold the arm overhead;
    - (ii) the load-proportional friction (mu_eff x 10 N.m = 0.6-1.8 N.m per joint) is hard to compensate, and the wearer
      feels it through the 3-5x amplification;
    - (iii) its component about the humerus (p95 2.7 N.m per N.m) loads the rotator cuff.
- **Caught by:** partly, and neither part is on the scorecard.
  - `transmission.py` uses constant friction.
  - `judge/dynamics.py` (in progress) uses MuJoCo `frictionloss`, which is a constant torque per joint. It will show
    inertia and soft-cuff effects but cannot show wedging.
  - The fix inside that judge: update each hinge's `frictionloss` every step to tau0 + mu_eff |M_perp|, with M_perp
    read from the joint's constraint wrench (`mj_rnePostConstraint` / `cfrc_int`), and sweep mu_eff over 0.06-0.37.
- **Proposed judge R21 "no self-locking".**
  - alpha* per frame (`rt_wedge.py`) with the R x F term added, over the clips, held-out data and the workspace grid.
  - Threshold: tan(alpha*) >= 2 mu_eff,max, i.e. alpha* >= 20 deg at mu_eff,max 0.18, every frame. The 2x covers static
    friction and contamination.
  - A power-off back-drive test.
  - Bench: a printed joint with the real igus washers and sleeve on a Ti pin. Measure breakaway torque vs applied tilt
    moment (this gives mu_eff): dry, after sweat exposure, and after 10^5 cycles.
  - Instrument: MuJoCo's joint `frictionloss` is constant, so it cannot show this effect. Use Drake (contact-modelled
    joint) or the model above.
- **Needs from the user:** approval to buy the igus parts (a few tens of euros) and print a test joint.

### G7. Pinch, shear and crush points

- **Mechanism.**
  - Links scissor over each other at the 3.15 mm stack gap.
  - Link edges sweep 2-14 mm above skin that folds and bulges.
  - The arm can crush exo parts against the chest and axilla.
  - The other hand, hair, ears and the head are in no judge.
  - A powered joint pushes a link edge with tau / r = 140-360 N at 70 mm (10-25 N.m).
- **Evidence.**
  - ISO 13854:2017 minimum gaps to avoid crushing (commonly quoted: finger 25 mm, hand 100 mm, arm 120 mm; verify in the
    standard). It does not cover shearing.
  - The 2-14 mm band sits inside the finger range.
  - Red team finding 7: the upper-cuff edge is -0.07 mm from the chest at cross-body poses in a rig with no contact
    model, so a real arm squeezes harder.
  - Everyday: the left hand rubbing or holding the right shoulder, a bag strap, hair hanging on the shoulder, tilting the
    head to the right.
- **Caught by:** nothing. R2/R6 test interpenetration, not gaps that open and close.
- **Proposed judge R22 "pinch".**
  - Per frame (continuous, G15), measure the minimum distance between every pair of relatively moving parts, and between
    parts and body, with its closing rate and the force behind it (actuator torque / lever).
  - Flag any gap that closes through 4-25 mm with force behind it. Threshold: wherever a gap closes, it is either >= the
    ISO 13854 body-part gap or too small for the body part to enter.
  - The unavoidable ones get transient force limits and a hazard analysis under ISO 13482 (physical assistant robots), or
    IEC 80601-2-78 if the device is medical (rehabilitation).
  - Instrument: coal / FCL distance queries along the trajectories.
- **Needs from the user (decision):** which safety standard applies; whether covers or shrouds are allowed (they add
  height).

### G8. Mechanical end stops cannot hold the arm inside its range of motion

- **Evidence [new, `rt_jointbox.py`].**
  - Method: per 3R design, the tightest per-joint stops that let all 8 clips through (spans 137-143 / 74-88 / 152-163
    deg). Map a 26^3 grid over that box forward, then measure each reachable humerus orientation's distance to the red
    team's plausible everyday workspace (generous: +-90 deg humeral rotation at every arm direction).
  - Result: 5.2-11.6 % of the box is > 20 deg beyond, 2-6 % is > 30 deg beyond, and the worst is **51.6-67.2 deg**
    beyond.
  - Anatomical limits are coupled (the rotation range depends on elevation) and personal. So the only thing between a
    10-25 N.m actuator and an over-rotated shoulder is software, plus whatever the wearer can resist.
- **Caught by:** nothing.
- **Proposed judge R23 "safe ROM".**
  - The share of the stop box outside the wearer's measured ROM; report it, and use it as a search objective (choose the
    axes so that the clips' box maps inside the ROM).
  - Require software limits to a functional-safety level under ISO 13482.
  - Require a torque limit the wearer can overpower (for example <= 50 % of their isometric strength).
  - Require a power-off state in which the arm can be lowered.
- **Needs from the user (data):** the wearer's maximal-ROM trials (add to OpenCap item 2), and the safety-class decision
  (G7).

### G9. Real motion is faster, wider and less tidy than the 8 clips

- **Evidence [new, `rt_simreal_misc.py`].**
  - The clips join keyframes at constant speed (p95 = max): 58-175 deg/s.
  - A natural minimum-jerk reach of the same duration peaks at 1.875x its mean speed (Flash & Hogan 1985), so about
    200 deg/s for "Raise overhead".
  - Faster or unplanned motions are absent: catching a fall, swatting, reaching to a back seat.
  - The 3R closes only while the angle between J1's axis and the arm-fixed axis stays within [|a1-a2|, a1+a2]: [17.5, 127]
    deg for r14 (`reach3r.py`). Outside that window the arm is blocked.
  - Red team: the 3R's singular margin drops to 12.4 deg on held-out walking, where a joint must turn at 645 deg/s for
    100 deg/s of arm motion. That saturates any actuator.
- **Caught by:** partly. R3/R4 run on the 8 clips (2 held out); the red-team grid is not on the scorecard.
- **Proposed judge (R14 made concrete).** On OpenCap and AMASS: closure, sigma >= 0.3, and joint speed and power within
  the actuator's limits. Plus a "brisk" variant of every clip (min-jerk profile, time-scaled 2-3x) for R2/R6 and
  actuator power.
- **Needs from the user (data):** OpenCap at natural and brisk pace; AMASS / SMPL-X licences.

### G10. The skin does not deform the way the rig does

- **Evidence.**
  - **[new, `rt_simreal_misc.py`]** From all muscles relaxed (activation 0.06) to the shoulder and elbow flexors fully
    active, the rig moves skin within 120 mm of GH by at most 0.7-1.4 mm (outward from GH by at most 0.6 mm). The rig has
    almost no load-dependent deltoid bulge.
  - Real muscle thickens about 10 % at maximal contraction (rectus femoris 23.4 -> 25.7 mm by ultrasound; excerpt): about
    1.5-2.5 mm on a 15-25 mm deltoid, more where the muscle shortens and bunches.
  - Not modelled at all:
    - skin and upper trapezius bunch over the acromion overhead and in a shrug;
    - chest expansion of 4-7 cm circumference at maximum (about 6-11 mm in radius; tidal breathing much less) affects
      parts near the axilla and chest;
    - the head, neck and trunk are static in the rig, while lateral neck flexion brings the ear and jaw toward the base
      and J1 hub.
  - Known rig artefacts (FINDINGS): a 25-30 mm biceps envelope, and the arm passing through the chest.
- **Caught by:** partly (rig activation; P2 scan registration is planned).
- **Proposed judge.**
  - P2 registration of extra scans: relaxed; holding 2-3 kg at 90 deg abduction and flexion; overhead; a deep breath.
  - R1/R2 recomputed against the loaded-pose skin.
  - A head and neck sweep (lateral flexion 0-40 deg, rotation +-70 deg) against the base and hub keep-outs.
  - +-5 mm of radial breathing motion on trunk skin within 30 mm of any part.
- **Needs from the user (data):** the extra scan poses (an extension of data/raw item 3).

### G11. Body-shape spread: one rig, one size

- **Evidence.**
  - The band is 12 mm wide.
  - ANSUR II (from memory; verify against the public CSV) gives a flexed biceps circumference SD of about 27-30 mm, i.e.
    an arm-radius SD of about 4.5-5 mm, and a biacromial breadth SD of about 18-19 mm. The 5th-95th percentile spread is
    then about +-7-8 mm of arm radius.
  - The P3 proxy (uniform scale 0.92-1.08) changes size but not shape (fat vs muscle, BMI).
  - Within one person: weight change, training, post-exercise pump.
- **Caught by:** nothing (R14 NO DATA).
- **Proposed judge.** SMPL-X shape sampling (P3 section 4). For production, a made-to-measure fit from the wearer's scan.
  Report the size range each design fits.
- **Needs from the user:** a decision (one-off for the user or a product for others), and the SMPL-X / AMASS licences.

### G12. Clothing, hair and donning

- **Mechanism and evidence.**
  - Anything between skin and metal uses up the band: a T-shirt about 0.5-1 mm, a sweater 3-6 mm (estimate).
  - Rotating links drag fabric and hair into the 3.15 mm stack gaps.
  - Donning alone means aligning a GH centre the wearer cannot see (G3) and opening a chain that wraps the shoulder.
- **Caught by:** nothing.
- **Proposed judge.** A garment-thickness offset of the skin (0.5 / 1 / 3 mm) in R1/R2. Prototype tests: worn over a
  shirt; donning time.
- **Needs from the user (decision):** worn on skin, over a base layer, or under clothes; who puts it on.

### G13. Sensor and power wiring across rotating joints

- **Evidence.**
  - Every hub carries an encoder PCB (docs/HARDWARE.md), so wires must cross J1-J3, whose stop spans are 74-163 deg
    (G8).
  - The Ø10 pin is solid.
  - A service loop outside the shell snags (G12).
  - Off-axis wires change length (G1).
- **Caught by:** nothing.
- **Proposed judge.** A wire-path keep-out per joint in L1 (a hollow pin, or a spiral flex under the cap), plus a
  flex-life test (10^6 cycles at the joint span); or wireless joint sensors, with the battery counted in R8.
- **Needs from the user (decision):** the user said encoder integration is a placeholder, but a powered exo needs joint
  angles. Is joint sensing required, and where?

### G14. Interface pressure over hours: R11 cites a collision standard

- **Evidence.**
  - R11 references ISO/TS 15066. Its Annex A gives pain-onset limits for transient and quasi-static robot contact, of
    order 10^2 N/cm^2 (about 1 MPa; verify).
  - Sustained-wear discomfort sits at about 14 kPa [Kermavnar], roughly 100x lower.
  - Red team: the arm saddle is at 18.1 kPa mean at 25 N.m and 7.3 kPa at 10 N.m. The knit band's area is unknown.
  - Shear from misalignment sliding (G3) adds, and sweat changes skin friction.
- **Caught by:** nothing (R11 NOT MEASURED).
- **Proposed judge.** Rewrite R11 as: sustained peak <= 14 kPa, and <= 4.3 kPa (capillary reference, red team) where
  contact lasts hours.
  - Predict with MuJoCo / Drake soft contact or CalculiX.
  - Measure with pressure film / FSRs on the prototype.
- **Needs from the user (decision):** the wear duration per session.

### G15. The judges sample time too coarsely

- **Evidence.**
  - `tools/judge_all.sh` runs R2 every 2nd frame (15 Hz) and R6 every 4th (7.5 Hz); the fast mode runs 5 Hz and 2.5 Hz.
  - Joints turn at up to 1.4x arm speed (`transmission.py`) and the clips peak at 175 deg/s. A link at 70 mm from GH
    then moves about 300 mm/s: about 40 mm between R6 checks (120 mm in fast mode), and about 100 mm for arm-end parts at
    250 mm.
  - 5.5 mm parts can pass through each other between checks, and the depth reported is the depth at the sampled frame,
    not the worst depth.
  - Real motion is faster still (G9).
- **Caught by:** the gap is in the judges themselves.
- **Proposed judge.** Continuous collision detection (coal / FCL CCD, or conservative advancement) between checked
  frames, or adaptive sub-steps so that no vertex moves more than 0.5 mm per step.
- **Needs from the user:** approval to pip-install coal or python-fcl.

### G16. Worn mass and inertia nobody budgets

- **Evidence.**
  - R8 counts custom metal parts (110.9 g on `l1_r14_3r_s1351_1`).
  - The worn system adds actuators (about 1.5 kg if on the joints, G1), electronics, battery, the handler and the band.
    The passive ShoulderX is 3.17 kg.
  - The exo's own weight adds to the G2 and G4 loads.
  - Reflected rotor inertia J_m N^2 can match the upper arm's own inertia about GH at typical gear ratios. Compute it once
    the actuator is chosen.
- **Caught by:** partly (R8, custom parts only).
- **Proposed judge.** R8 becomes total worn mass and its distribution, plus the exo's inverse dynamics at real speeds
  (Drake / MuJoCo) as an interaction torque.
- **Needs from the user (decision):** a whole-system mass budget.

### G17. Joint play, wear and tolerances

- **Evidence.**
  - The v4 washer float is 0.02 mm.
  - A pressed iglidur sleeve on an h9 pin typically runs about 0.03-0.12 mm clearance (verify with igus tolerance data).
  - Washer edge pressure reaches 80 MPa at 25 N.m, which is the iglidur rating (thin_study). So wear and creep will
    open the float.
  - Once the sleeve carries the tilt, the play is about c / L = 0.1 / 4 rad, i.e. about 1.4 deg per joint or about 2 mm
    at 80 mm, and mu_eff rises toward 0.37 (G6).
  - Axis-intersection manufacturing error: 0.5 deg at R 70 is 0.6 mm.
- **Caught by:** nothing.
- **Proposed judge.** A per-joint play-vs-cycles model, R2/R6 run at the worn limit, and a bench wear test (shared with
  G6).
- **Needs from the user:** nothing.

### G18. Fatigue and the real material process

- **Evidence.**
  - thin_study: no link reaches infinite life at 25 N.m (infinite-life moments are 6-24 N.m), and the pin root has a
    fatigue SF of about 1.1.
  - LPBF Ti-6Al-4V runs out at 200-500 MPa at 10^7 cycles depending on defects [ASM 2026 abstract], against the 500 MPa
    assumed.
  - Duty cycle: about 10^5-10^6 cycles per year (assumption: 500-3,000 assisted reaches a day; measure it).
- **Caught by:** nothing (R9 UNVERIFIED).
- **Proposed judge.** R9 in CalculiX with a load spectrum from OpenSim over a measured day, process-specific S-N data
  (machined wrought vs LPBF + HIP + machined), and a safety factor on life.
- **Needs from the user (decision):** CNC billet or LPBF (with the R13 supplier).

### G19. Materials against sweat and skin

- **Evidence (engineering handbook knowledge; verify with the supplier).**
  - 7075-T6 (BOTTOM + neck + JN hub) has poor stress-corrosion resistance in chlorides. T73 / T7351 tempers or anodising
    address it.
  - Bare aluminium touching titanium in sweat forms a galvanic couple.
  - Stainless screws that can touch skin must meet the EU nickel-release limit for prolonged skin contact.
  - iglidur takes up moisture, which changes clearances.
- **Caught by:** nothing.
- **Proposed check.** A material and finish review at L2 (clear anodising keeps the bead-blasted look) and a sweat / salt
  exposure test.
- **Needs from the user (decision):** anodised or bare finish, given "bead blasted metal".

### G20. The wearer's own shoulder

- Everything is fitted to one average healthy rig and to published healthy girdle laws (the remaining ~6.5 mm
  disagreement between those laws is in P0 section 8b).
- A particular wearer's GH and scapular motion can differ by more than the band. For example, scapular kinematics change
  measurably with impingement symptoms (Ludewig & Cook 2000).
- Only the wearer's own OpenCap recordings and scans settle it.
- **Needs from the user (data):** OpenCap of the wearer.

---

## 4. What needs the user

| type | item | gaps |
|---|---|---|
| decision | actuation concept: powered joints, motor location, assist torque spec, whole-system mass | G1, G16 |
| data | scapula-handler CAD + DOFs (free / sprung / powered, where it grounds) | G2 |
| decision | passive self-aligning fixation DOFs outside the count, or soft absorption, or imaging-based fit; how the GH centre is located at fitting | G3 |
| decision | how the assist is applied (rigid pad vs knit band); where humeral rotation is sensed | G4 |
| decision | "never touches skin" under external load, or a designed liner contact; which external loads | G5 |
| data | 10-15 min on the user: cuff and saddle stiffness (spring scale, ruler, torque wrench, protractor) | G2, G4 |
| approval | buy igus washers / sleeves + print a test joint (bench friction and wear) | G6, G17 |
| decision | safety standard (ISO 13482 vs IEC 80601-2-78); covers allowed | G7, G8 |
| data | OpenCap: natural + brisk pace, max-ROM trials (extends data/raw item 2) | G8, G9, G20 |
| data | extra scans: loaded poses, overhead, deep breath (extends item 3) | G10 |
| licence | AMASS / SMPL-X (already listed, item 4); product vs one-off | G9, G11 |
| decision | clothing layer; who dons it; wear duration per session | G12, G14 |
| approval | pip install coal or python-fcl for continuous collision | G15 |
| decision | finish (anodise vs bare), process (CNC vs LPBF) | G18, G19 |

---

## 5. New numbers from this pass (scripts and outputs)

All run locally on CPU in seconds to a minute, and are read-only on the rest of the repo. Re-run them from
`pipeline/redteam/`.

| script | output | what it measures |
|---|---|---|
| `rt_wedge.py` | `results/wedge.json` | self-locking threshold mu_crit = tan(alpha*) per frame with load-dependent plain-bearing friction; humeral-axis driving moment per N.m of joint friction |
| `rt_misalign.py` | `results/misalign.json` | arm-end shift (I - R)e and interface force for a GH-centre error e over the 8 clips (scapula frame) |
| `rt_jointbox.py` | `results/jointbox.json` | per-joint stop box that passes the clips, and how far it reaches beyond the plausible ROM |
| `rt_simreal_misc.py` | `results/simreal_misc.json` | clip speed profile (constant-speed keyframes); the rig's skin motion from muscle activation near the shoulder |

**The loop this should become** (docs/METHOD.md, altitude): a **perturbed-world judge**.
- For every design, draw the effects in section 2 from their distributions:
  - fitting error and GH-in-glenoid translation;
  - saddle slip and its loaded rotation;
  - cuff migration through the interface stiffness;
  - CalculiX deflection under the per-frame assist;
  - garment layer, muscle and breathing offsets.
- Apply them to the posed exo and skin, then re-run R1 / R2 / R6 with continuous collision.
- Report the 95th-percentile clearance and P(contact) next to today's nominal numbers.
- A design that passes only in the nominal world is not a design.

---

## Sources

Exoskeleton kinematics and interfaces
- Jarrassé N, Morel G. On the kinematic design of exoskeletons and their fixations with a human member. RSS 2010:
  https://roboticsproceedings.org/rss06/p15.html; journal version: Connecting a human limb to an exoskeleton, IEEE T-RO
  28(3), 2012.
- Schiele A, van der Helm FCT. Kinematic design to improve ergonomics in human machine interaction. IEEE TNSRE 14(4):
  456-469, 2006: https://research.utwente.nl/en/publications/kinematic-design-to-improve-ergonomics-in-human-machine-interacti/
- Stienen AHA et al. Self-aligning exoskeleton axes through decoupling of joint rotations and translations. IEEE T-RO
  25(3):628-633, 2009: https://unpaywall.org/10.1109%2FTRO.2009.2019147
- Schiebl J et al. Quantification of the mechanical properties in the human-exoskeleton upper arm interface during
  overhead work postures. Sensors 25(15):4605, 2025: https://pmc.ncbi.nlm.nih.gov/articles/PMC12349243/
- Yousaf et al. 2021 (Harmony, sensorized cuff; interface compliance needed to predict loads) (excerpt):
  https://reneu.robotics.utexas.edu/sites/default/files/uploaded_media/2021_AIM_Yousaf_2_0.pdf
- Shoulder exo torque / mass table (Skelex 6.1 N.m, ShoulderX 10 N.m, 3.17 kg): https://pmc.ncbi.nlm.nih.gov/articles/PMC10936402/
- Rosen J et al. 2005, human arm kinematics and dynamics during daily activities (gravity dominates) (excerpt):
  https://dsp.tecnalia.com/items/127be0cf-61ef-4208-be0a-05f3ba1c5055

Human measurement
- GH-centre estimation accuracy vs MRI (functional 11-17 mm Lempereur, 14.7-20.7 mm Nikooyan, IMU 20.6-21.9 mm, ISB
  regression ~30 mm): https://pmc.ncbi.nlm.nih.gov/articles/PMC5359843/ ; Lempereur et al. (functional methods):
  https://salford-repository.worktribe.com/output/1383256/in-vivo-estimation-of-the-glenohumeral-joint-centre-by-functional-methods-accuracy-and-repeatability-assessment
- Humeral axial rotation soft-tissue artefact, Cutti et al. 2005 (Gait Posture 21:341-349, 20-48 %), cited with "up to
  35 %" in Warner & Heller 2025 (J Biomech) (excerpt): https://eprints.soton.ac.uk/505073
- Dal Maso 2015, Karduna 2001, van Andel 2009, Lempereur 2014, Matsui 2006: via docs/research/gh_translation_literature.md
- Kermavnar T et al., simulated circumferential soft-exoskeleton compression at the knee (discomfort 13.7-30.4 kPa,
  pain 52.9-60.6 kPa) (excerpt): https://pure.ul.ie/en/publications/the-effect-of-simulated-circumferential-soft-exoskeleton-compress/ ;
  cuff pressure algometry review (excerpt): https://pure.ul.ie/en/publications/cuff-pressure-algometry-in-patients-with-chronic-pain-as-guidance/
- Rectus femoris thickness 2.34 -> 2.57 cm at MVC (excerpt): https://www.physoc.org/?p=59693
- Chest expansion in healthy adults, tape method, mean 5.5 cm (excerpt): https://cjrt.ca/article/81356.pdf
- ANSUR II public data (for G11, not downloaded): https://ph.health.mil/topics/workplacehealth/ergo/Pages/Anthropometric-Database.aspx
- Flash T, Hogan N. The coordination of arm movements. J Neurosci 5:1688-1703, 1985 (minimum-jerk peak = 1.875 x mean).
- Ludewig PM, Cook TM. Alterations in shoulder kinematics and associated muscle activity in people with symptoms of
  shoulder impingement. Phys Ther 80:276-291, 2000.

Hardware, materials, standards
- CubeMars AK70-10 (8.3 / 24.8 N.m, Ø89 x 50.25 mm, 521 g) (excerpt): https://www.cubemars.com/goods.php?id=1031
- Harmonic Drive CSD-17-50-2A (11 N.m rated, 23 N.m peak, 0.1 kg): https://www.harmonicdrive.net/products/component-sets/cup-type/csd-2a/csd-17-50-2a-r
- Bowden cable force-transmission efficiency on a body-worn exosuit (78.7 % optimum): https://pmc.ncbi.nlm.nih.gov/articles/PMC9352506/
- LPBF Ti-6Al-4V runout 200-500 MPa at 10^7 depending on imperfections (excerpt): https://asm.confex.com/asm/imat2026/webprogram/Paper65732.html
- ISO 13854:2017 minimum gaps to avoid crushing (scope; values to verify in the text): https://ccn-scc.ca/standardsdb/standards/8165818
- ISO 13482:2014 (personal care robots, incl. physical assistant robots); IEC 80601-2-78:2019 (medical rehabilitation
  robots); ISO/TS 15066:2016 (collaborative robots, Annex A body-region limits) - not read here; to obtain.
- In-repo: `pipeline/conformal/thin_study/REPORT.md` (link stiffness, washer pressure, fatigue), `pipeline/redteam/REPORT.md`
  (cuff load path, pressure, singular margins), `docs/research/ring_and_shell_hardware.md` (iglidur friction, plain vs
  rolling), `docs/research/gh_translation_literature.md`, `docs/P0_BASE_MOUNT.md`, `docs/HARDWARE.md`.
