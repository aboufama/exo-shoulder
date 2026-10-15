# GH-centre translation relative to the thorax: what published data say

Research note, 2026-10-14. It answers "how wrong is the rig's girdle law?" (`pipeline/avg/body_pose.py` `segs()` / `scap()`)
and gives a second, independent girdle model for sensitivity runs (R10, PLAN P0). Nothing here was downloaded except
paper text, abstracts and two figure images. No model files and no datasets were downloaded.

**Conventions.** Rig/ISB thorax frame, right shoulder, mm: **x anterior, y superior, z lateral (right)**. theta =
humerothoracic elevation (deg). p = plane of elevation, ISB convention, the same as the rig's `plane`: **0 = abduction
(frontal), 40 = scapular plane ("scaption"; 40 deg is assumed, as defined by Karduna 2001), 90 = forward flexion**. Displacements are measured from the arm-hanging posture.
Tags: **[R]** number read in the source; **[F]** read off a published figure (about +-1 deg); **[I]** inferred or computed
here. Computations are in the scratchpad scripts listed at the end. Nothing in the repo was changed except this file.

---

## 1. Verdict on the rig law (short)

Rig law: GH moves only superiorly, lift = 0.2 x 1.056 x max(0, theta - 30) mm. That gives 0 / 6.3 / 12.7 / 19.0 / 25.3 mm
at 30 / 60 / 90 / 120 / 150 deg, with no anterior-posterior or medial-lateral component and no dependence on the plane.

| Aspect | Rig | Literature | Verdict |
|---|---|---|---|
| Direction | superior only | superior is dominant, **plus posterior and medial** | partly supported |
| Superior slope | 0.21 mm/deg | 0.35-0.45 mm/deg in scaption and abduction from bone-pin angles [I]; 0.35-1.1 mm/deg from skin-marker studies [I from R] | **contradicted**: about 2-3x too small |
| Superior at 90 / 120 deg | 12.7 / 19.0 | 35 / 46 (scaption), 38 / 49 (abduction), 25 / 34 (flexion) [I]; 46-59 / 63-79 from skin-marker studies [I from R] | under-predicts by 13-25 mm at 90 deg and 15-30 mm at 120 deg (bone-pin chain) |
| Onset | 0 below 30 deg | Scaption and abduction: the clavicle and scapula move from the first data point (15 deg), and the scapula is already moving below it [F, R]. Flexion: little GH motion below about 30 deg [I]. The only source with a 30 deg dead zone is Klopčar & Lenarčič (skin markers) [R]. | contradicted for abduction and scaption; roughly right for flexion |
| Anterior-posterior | 0 | posterior 24 mm by 90 deg in abduction (plateau after about 60 deg); 5-12 mm in scaption; about 0 in flexion until 105 deg, then 15-20 mm [I] | missing |
| Medial-lateral | 0 | **medial** 10-22 mm at 90 deg and 17-28 mm at 120 deg [I]; 26 / 37 mm in skin-marker data [I from R] | missing |
| Plane dependence | none | at 90 deg, abduction vs flexion differ by about 22 mm (AP), 12 mm (superior) and 12 mm (ML) [I] | missing |
| Scapular rotation | upward rotation 0.36 deg/deg above 20 deg; tilt 0.12 deg/deg | upward rotation +38 deg and posterior tilt +16-18 deg from rest to 120 deg (bone pins) [F]. Rig: 36 deg and 14 deg at 120 deg. | **magnitudes supported** (within about 15%); the onset lags (data rotate from 0 deg) |
| Scapula pivot | about the GH centre | about the AC joint, carried by the clavicle; that chain is what moves the GH centre | modelling error (it is why lift had to be bolted on separately) |

**Total vector error** |literature (bone-pin chain) - rig|, computed [I]:

| Plane | at 90 deg | at 120 deg | worst, 0-135 deg |
|---|---|---|---|
| abduction | 41 mm | 48 mm | 51 mm |
| scaption | 26 mm | 35 mm | 40 mm |
| flexion | 16 mm | 27 mm | 36 mm |

Against the skin-marker studies the error is larger. All of these errors exceed the 10 mm skin band the design is judged on. The
rig's overhead girdle is therefore not a reliable basis for judging the 1 cm rule, and a thorax-fixed base sees 2-3x the GH
motion the rig assumes, in a direction the rig does not model.

---

## 2. Summary table: GH displacement vs elevation, per source (mm, ant / sup / lat; negative = posterior / inferior / medial)

| Source (method, n) | Plane | 30 deg | 60 deg | 90 deg | 120 deg | 150 deg |
|---|---|---|---|---|---|---|
| **Rig** `segs()` | any | 0 / 0 / 0 | 0 / 6.3 / 0 | 0 / 12.7 / 0 | 0 / 19.0 / 0 | 0 / 25.3 / 0 |
| **Bone-pin chain** [I]: Ludewig 2009 angles [F] + clavicle 154 mm [R, Xu 2016] + rig AC-to-GH vector | abduction | -13.5 / 12.7 / -7.9 | -20.5 / 26.9 / -15.7 | -23.5 / 37.7 / -21.8 | -24.3 / 49.4 / -27.9 | -25.2 / 59.6 / -34.0 * |
| same | scaption | 0.5 / 12.7 / -3.3 | -2.7 / 25.6 / -7.8 | -4.8 / 34.8 / -11.8 | -11.7 / 45.8 / -18.4 | -17.1 / 59.6 / -28.7 * |
| same | flexion | -2.9 / 2.1 / -2.5 | -1.2 / 14.8 / -5.6 | -1.6 / 25.3 / -10.3 | -14.6 / 33.5 / -17.4 | -31.2 / 47.4 / -27.2 * |
| **Zhang et al. 2020** (Vicon skin markers plus scapula cluster, 12 men, 16 planes averaged), polynomials [R] x d0 = 190.6 mm [I] | mean of all planes | 0.2 / 12.8 / -8.2 | -7.9 / 29.0 / -16.8 | -17.1 / 46.4 / -26.3 | -24.4 / 62.8 / -37.0 | -30.9 / 76.0 / -49.3 |
| **Klopčar & Lenarčič 2006** (optoelectronic, 10 subjects, 4 planes), piecewise law [R, as reproduced by Zhang 2020] on rig SC-to-GH 170.5 mm [I] | all planes | 0 / 0 / 0 | 2.5 / 31.5 / -6.0 | -1.4 / 58.9 / -25.4 | -2.3 / 78.8 / -54.3 | 6.0 / 88.2 / -85.7 |
| Rettig et al. 2015 (IJ-to-functional-GH vector, 8 subjects, **bilateral** abduction) | abduction | - | - | - | max girdle elevation 32 deg (SD 6) vs 4.5 deg (SD 3.3) minimum [R]; on a 190 mm lever, about +85 mm [I] | - |
| Carignan et al. 2005 (video data via Moeslund et al.) | abduction to 180 deg | vertical displacement "far greater than" horizontal, with a sharp rise once the arm passes horizontal [R, qualitative only; numbers only in their Fig. 3] | | | | |
| ANYexo 2.0 coupling (Zimmermann et al. 2023, motion capture, 2 participants) | elevation | robot SC-elevation joint: GED = -0.0053 theta^2 - 0.0162 theta + 20.5 deg for theta <= 96, -30.5 deg above [R], i.e. a 51 deg swing [I] | | | | |

\* Beyond the last bone-pin data point (132-138 deg): linear extrapolation [I].

The ANYexo angle is a robot joint fitted for control. Its lever arm is not given, so it cannot be converted to mm. On a
150-170 mm lever, 51 deg would be implausible as anatomical GH motion; read it as a robot fit, not as anatomy.

**Two families disagree by about 1.6x at high elevation.**

- *Bone-pin and MRI angles* (Ludewig 2009, Sahara 2007, McClure 2001), pushed through a rigid chain [I], give about 35-38 mm
  superior at 90 deg in scaption and abduction.
- *Skin-marker / functional-GH studies* (Zhang 2020, Klopčar 2006, Rettig 2015) give 46-59 mm at 90 deg and 63-88 mm at
  120-150 deg [I from R].

Skin-based methods overestimate scapular upward rotation with an acromion cluster (Karduna 2001 [R]) and degrade above
100-120 deg (section 7). Both biases push GH upward. Take the bone-pin chain as the central estimate and the skin-marker
family as an upper bound. Neither family supports the rig's 25 mm at 150 deg.

How the bone-pin chain was built [I]: GH(theta) = SC + R_clav(theta) (0, 0, L) + R_ST(theta) R_ST(rest)^T (GH - AC)_rest.

- Inputs: ISB Y-X-Z angles read from Ludewig 2009 Fig. 5-A/5-C per plane; L = 154 mm; (GH - AC)_rest = (16.2, -34.9, 24.5) mm,
  taken from the rig's own bones (lateral end of the clavicle mesh vs the humeral-head sphere fit, which lands on the rig origin).
- In scaption, from 15 to 120 deg, the clavicle alone moves GH by (-27, +17, -21) mm. The scapula rotating about the AC adds
  (+15, +23, +4) mm.
- Sensitivity at 120 deg in scaption: L = 131-177 mm and |AC-to-GH| x0.75-1.25 give superior 31-48 mm, AP -4 to -20 mm and
  ML -13 to -21 mm.
- Not included: AC translation (1-2 mm by 4D CT, per search summary only) and GH translation within the glenoid. The glenoid
  term is +1-2 mm superior in imaging studies, and up to +4.7-12.4 mm "upward/longitudinal" with bone pins (Dal Maso 2014/2015
  [R]); it would add to the superior total.

---

## 3. Clavicle angles vs elevation (Question 2)

Ludewig et al. 2009: transcortical pins, n = 12 (n = 11 for the clavicle). ISB angles relative to the thorax, read from
Fig. 5-A [F], mean of raising.

| theta (deg) | Retraction: abduction / scaption / flexion | Clavicle elevation: abduction / scaption / flexion |
|---|---|---|
| relaxed standing (Table I) [R] | 19.2 +- 2 (SE) | 5.9 +- 1 (SE) |
| 15 | 27 / 23.5 / 19 | 12.5 / 10.5 / 10.5 |
| 30 | 31 / 25 / 21 | 14 / 12 / 10 |
| 60 | 37 / 29 / 23 | 17 / 14.5 / 12.5 |
| 90 | 41 / 32 / 25.5 | 18.5 / 15.5 / 14 |
| 120 | 44 / 36.5 / 32 | 19.5 / 17 / 14.5 |
| end of range (132-138) | 45 / 39 / 34.5 | 19.5 / 17.5 / 15.5 |

Text values [R]:

- Sternoclavicular, scaption: retraction 23 -> 39 deg (+16) and elevation 11 -> 17 deg (+6). Posterior axial rotation 0 -> 31 deg
  (rotation about the long axis does not move the AC).
- "Little clavicular elevation occurred."
- Plane effects: abduction is more retracted and flexion less retracted than scaption at all angles, with up to 15 deg between
  flexion and abduction at mid-range. Abduction is more elevated than flexion by 4 deg on average.
- Scapulothoracic: internal rotation in flexion is +7 deg and in abduction -7.5 deg vs scaption. Upward rotation in abduction is
  +3 deg at 90-120 deg.
- Variability: the SE bars of about 2-3 deg at n = 11 imply an inter-subject SD of about 7-10 deg in absolute angle [I]. The
  standard error of measurement across two trials was 1.4-1.7 deg [R].

Other clavicle sources:

- Sahara et al. 2007 (vertically open MRI, 7 subjects / 14 shoulders, coronal abduction, so no skin artifact): clavicle
  retraction 30.6 deg, elevation 7.3 deg, posterior axial rotation 33.2 deg over the abduction range [R].
- Scapula (McClure et al. 2001, pins, n = 8, scaption): upward rotation 50 deg (SD 4.8), posterior tilt 30 deg (SD 13), external
  rotation 24 deg (SD 12.8) [R].
- Clavicle length (SC-AC):
  - 154 mm (SD 23), n = 14 (Xu et al. 2016) [R]
  - 155.4 mm (SD 13.1), n = 12 (Gonçalves 2021, MSc) [R]
  - the rig: 156.4 mm, resting at 32 deg retraction and 6.4 deg elevation [I, from `body_mesh.json` bones]. The rig is more
    retracted at rest than Ludewig's 19 deg.
- Inman et al. 1944: the oft-quoted "4 deg of clavicle elevation per 10 deg of arm elevation" **could not be traced to a
  readable source in this session**; treat it as unverified. It is also 3-5x larger than modern bone-pin and MRI values.

Rule of thumb, scaption at 90 deg [I]. Per degree of clavicle angle, GH moves:

- per degree of retraction: 2.2 mm posterior and 1.4 mm medial
- per degree of clavicle elevation: 2.6 mm superior
- per degree of scapular upward rotation: 0.7 mm superior
- per degree of scapular internal rotation or posterior tilt: about 0.5 mm anterior and 0.5 mm medial

So **GH translation is driven mainly by clavicle retraction (AP/ML) and by clavicle elevation plus scapular upward rotation
(superior)**.

---

## 4. Onset (Question 3)

- Bone pins (Ludewig 2009) [F]:
  - Scaption and abduction: the clavicle is already retracting and elevating between 15 and 30 deg (scaption: retraction +1.5 deg,
    elevation +1.5 deg; abduction: +4 deg and +1.5 deg).
  - Scapular upward rotation runs at about 0.3 deg/deg from 15 deg. Relaxed standing (5.4 deg) to 15 deg (10.5 deg) continues
    the same slope [I].
  - Flexion: clavicle elevation is flat (10.5 -> 10 deg) until about 30 deg and retraction is small.
  - Caveat: the jump from Table I's relaxed standing to the 15 deg value in clavicle elevation (5.9 -> 10.5 deg) is unexplained
    in the paper. It may be a static-vs-dynamic trial difference. The chain therefore anchors 0 deg by extrapolating the 15-30
    deg slope [I].
- Zhang 2020 [R]: the superior polynomial has a non-zero linear term at 0 deg (1.819e-3 d0 per deg). With d0 = 190.6 mm that
  is 0.35 mm/deg [I]. Motion starts immediately.
- Klopčar & Lenarčič 2006 [R, via Zhang 2020]: girdle elevation is 0 for 0-30 deg, then 0.36 theta - 10.8 deg. Retraction is 0
  for 0-70 deg, then -0.22 theta + 15.4 deg. Girdle length is (-1.6e-5 theta^2 + 3e-4 theta + 1) d0.
  - The rig's 30 deg dead zone matches this law.
  - The rig's slope does not: Klopčar's law implies about 1.07 mm/deg on a 170 mm girdle [I], 5x the rig's 0.21.
- The "setting phase" (Inman; first about 30 deg of abduction, scapula variable) appears only in secondary sources here.
- **Conclusion:** in scaption and abduction the GH centre moves from about 0 deg at about 0.4 mm/deg [I]. In flexion there is a
  quasi-dead zone to about 30 deg [I]. A hard 30 deg dead zone in all planes is not supported by bone-pin data.

---

## 5. Plane of elevation and axial rotation (Question 4)

- **Plane: large effect on AP and ML** (section 2 table) [I]:
  - abduction retracts the clavicle 15-20 deg more than flexion [F]
  - GH at 90 deg: abduction is 22 mm more posterior, 12 mm more superior and 12 mm more medial than flexion
- Grewal & Dickerson 2013 (n = 28; 0-180 deg; planes 0 / 45 / 90; maximum internal, neutral and maximum external axial
  rotation) [R, abstract]:
  - "Axial rotation of the humerus did not influence scapular retraction/protraction."
  - "Plane of elevation did not influence clavicular elevation."
  - Elevation angle was the largest contributor to scapular lateral rotation, posterior tilt and all clavicular angles. Plane was
    the largest contributor to scapular protraction.
  - Effects of axial rotation on the other angles exist, but their size was not obtained (the paper's coefficients were not
    read).
- Dal Maso et al. 2015 (pins, 2 subjects), GH translation *relative to the scapula* during elevation [R]:
  - arm internally rotated: 3.6 / 2.9 mm
  - neutral: 4.2 / 3.7 mm
  - externally rotated: 4.3 / 4.3 mm
  - so axial rotation changes it by about 1 mm.
- **Conclusion:** plane matters (about 20 mm AP at mid-range). For axial rotation no thorax-frame GH number exists. Indirect
  evidence suggests a few mm at most, but it is unquantified: put it in the data-collection list.

---

## 6. How much of GH translation is NOT a function of arm orientation (Question 5)

| Component | Size | Source |
|---|---|---|
| Inter-subject: shoulder-rhythm regressions vs measured clavicle angles | RMSE >= 5 deg for every angle and every rhythm. Best: clavicle protraction 7.1 deg, clavicle elevation 7.2 deg; worst up to 21.4 / 13.7 deg | Xu et al. 2016 (6 rhythms, 14 subjects, 118 postures) [R] |
| same, in mm at the AC | 7 deg x 154 mm = **about 19 mm RMS** per axis, which includes static posture offsets | [I] |
| Other regression rhythms | validation RMSE 6.6-11.1 deg (Xu 2014); 5.05-10.8 deg (Gonçalves 2021) | [R] |
| Inter-subject spread of the *change* from rest (offsets removed) | 1 SD at 90 deg: AP 10, sup 7, ML 7 mm. At 120 deg: 12 / 10 / 10 mm | [I] Monte Carlo on the chain with **assumed** SDs of angle change (retraction 5, elevation 3, upward rotation 5, tilt 8, internal rotation 6 deg; L SD 15 mm; AC-to-GH SD 15%). The upward rotation and tilt SDs are informed by McClure 2001 (4.8 / 13 deg). |
| Trial-to-trial, same subject | SEM 1.4-1.7 deg (Ludewig) -> about 4 mm | [R] / [I] |
| Same subject, between days | acromion-cluster waveform error 2.7-3.4 deg upward rotation, 1.3-2.3 deg tilt, 3.9-7.3 deg internal rotation (Warner 2015) | [R] |
| Raising vs lowering | Ludewig: only retraction at 120 deg differs (1.2 deg), tilt +2 deg on lowering. Zhang: ratio difference 0.04 (AP) and 0.076 (sup) at 150 deg, i.e. **8-14 mm** | [R] / [I] |
| Hand load | de Groot 1999 (0-2.9 kg, frontal plane, palpation): **no significant effect**. Pascoal 2000 (0-4 kg, 30 subjects, electromagnetic tracking): load **does** change scapular protraction, lateral rotation and tilt, most in abduction. de Groot & Brand 2001: external force direction is a significant covariate. | [R] |
| Shrug (voluntary or passive) | Cadaver passive shrug: clavicle elevation +25 deg (SD 5), retraction +17 deg (SD 5), scapular lateral rotation +26 deg (SD 4) (Peeters 2023) [R]. That gives **about +80 mm superior, -27 mm posterior, -24 mm medial** at GH [I]. Live sternoclavicular range is at least 25 deg elevation and at least 35 deg retraction (Irshad 2026, IMU) [R]. The girdle's voluntary angular range is largest with the arm down and "halves in humerus maximal elevated position" (Klopčar 2006) [R]. | |

**Take-away [I]:**

- The arm-orientation-predictable mean curve carries most of the motion (35-50 mm by 90-120 deg).
- The residual within a population is about 7-12 mm (1 SD), and the residual within one person is about 4-8 mm.
- Load, raising vs lowering, and especially shrugging add up to several cm on top.
- Offset joint axes can absorb only the mean curve. The residual is the same size as the 10 mm band, so the base or cuff needs
  compliance or per-user fitting. A deliberate shrug exceeds the band by far.

---

## 7. Skin-mounted plate on the acromion: how well it tracks the scapula (Question 6)

| Study | Result |
|---|---|
| Karduna et al. 2001 (electromagnetic sensor fixed on the acromion vs bone pins, n = 8) [R] | RMS errors, acromial method: posterior tilt 6.6-8.6 deg; upward rotation 4.4-6.3 deg (2.0-4.1 after their linear correction); external rotation 6.2-11.4 deg, growing "up to 25 degrees at maximal elevation". Clavicle angles derived from it: 1.1-2.6 deg. Similar to pins "especially below 120 degrees of elevation". The acromial method *overestimates* upward rotation. |
| van Andel et al. 2009 (acromion marker cluster vs scapula locator) [R] | maximum mean difference 8.4 deg in extreme positions; 6 deg or less in flexion and abduction; "elevation of the humerus should not exceed 100 degrees". The cluster under-estimates scapular motion. |
| Lempereur et al. 2014 (systematic review, 19 articles) [R] | Acromion marker cluster with calibration at rest: about 5 deg (flexion) and 7 deg (abduction) accurate below 90-100 deg. Above that, a second calibration at 90 or 120 deg, or multiple calibrations. |
| Warner et al. 2015 [R] | valid up to 120 deg; above 120 deg "the measurement error becomes too large" (they cite this from prior studies) |
| Matsui et al. 2006 (MRI, 9 men, translation of skin markers vs bone) [R] | The acromion marker "deviated least". The abstract prints "39 +/- 1 mm" (full elevation) and "15 +/- 1 mm" (hand behind back), yet says medial-border markers were "on the order of 8 mm". These are inconsistent; most likely 3.9 / 1.5 mm with the decimal points lost. **Verify in the full text.** McQuade & Smidt reported 4.2 mm skin slippage for an acromial module (cited by Matsui and Zhang). |

**Implication for a plate [I]:** a plate strapped over the flat acromion follows the *position* of the AC and acromion to within a
few mm, and the clavicle direction to 1-3 deg. Its *orientation* error of 5-10 deg below 100-120 deg becomes about 4-8 mm at the
GH centre over the 46 mm AC-to-GH lever. Above 120 deg it degrades: external-rotation error reaches 25 deg, about 20 mm at the GH.
A scapula-tracking plate is credible up to about 100-120 deg and is not credible overhead without an extra reference (for
example a second calibration, as the review recommends).

---

## 8. OpenSim: Seth 2016 / thoracoscapular model (Question 7). Not downloaded; needs the user's permission.

**What exists [R]:**

- **Seth, Matias, Veloso & Delp 2016** (PLoS One 11:e0141028):
  - Scapulothoracic joint with 4 DOF: abduction-adduction and elevation-depression on a thoracic ellipsoid, upward rotation
    about the surface normal, and winging (internal rotation lifting the medial border).
  - Sternoclavicular joint: universal (protraction-retraction, elevation-depression; no axial rotation).
  - Acromioclavicular joint: ball joint, handled as a constraint that removes 3 translations.
  - Glenohumeral joint: ISB gimbal (plane of elevation, elevation, axial rotation).
  - Validation: bone-pin data of **one** subject (Ludewig lab: flexion, abduction, internal/external rotation at 90 deg
    abduction), marker RMS about 1.9 mm (worst 2.4 mm). The GH marker RMS is 1.0-2.4 mm.
  - Built as an OpenSim 3.2 plugin.
  - Distribution: Stanford Digital Repository https://purl.stanford.edu/br087nj9017 ("experimental bone-pin data, models, and
    methods"), licence **CC BY-NC-SA 3.0**; also https://simtk.org/home/scapulothoracic.
- **Seth et al. 2019** (Front. Neurorobot. 13:90), "thoracoscapular" model for OpenSim 4.0:
  - Same scapulothoracic joint with scapular muscles. Scapular motion is deliberately **not** coupled to the humerus, so that
    shrugging is possible.
  - Data: 1 woman, trakSTAR sensors (T1, acromion, distal humerus); shrug, flexion and abduction, each with and without 2 kg,
    3 trials (18 trials).
  - SimTK project https://simtk.org/projects/thoracoscapular: `ThoracoscapularShoulderPaperMaterials.zip` ("model, experimental
    data and simulation results"), **CC BY 4.0** use agreement.

**Consequence:** the model is a *joint model, not a rhythm*. It produces GH-in-thorax trajectories only when driven by measured
scapular kinematics, from its two single-subject datasets or from the user's own data. To compare against a population, the
clavicle and scapula coordinates have to be driven with a rhythm (sections 3 and 9).

**How to extract GH-in-thorax, after permission [I]:**

1. Load the 2019 model in OpenSim 4.x and the provided inverse-kinematics `.mot`, or run IK on the provided marker/sensor files.
2. For each frame, call `humerus.findStationLocationInAnotherFrame(state, Vec3(0), thorax)`, or run the PointKinematics
   analysis on point (0,0,0) of `humerus` expressed in `thorax`.
3. Express the result in the ISB thorax frame and subtract the rest frame.

To verify on download:

- The coordinate names. Expected, but not confirmed here: `scapula_abduction`, `scapula_elevation`, `scapula_upward_rot`,
  `scapula_winging`, `plane_elv`, `shoulder_elv`, `axial_rot`.
- Whether the clavicle coordinates are independent or solved from the AC constraint. The paper's DOF count (2 SC + 3 AC
  constraints + 4 ST) needs checking.
- The model's own clavicle length and AC-to-GH vector, which should replace the rig-derived vector used in this note.

---

## 9. Recommended second girdle model for sensitivity runs

### L1, central estimate (bone-pin chain [I])

d(theta, p) = (ant, sup, lat) in mm, from the arm-hanging posture. Quadratic fits through the origin, valid for 0-135 deg. "Max
residual" is the largest fit error against the chain.

| Plane | ant (mm) | sup (mm) | lat (mm) | max residual |
|---|---|---|---|---|
| abduction, p = 0 | -0.482 theta + 0.00232 theta^2 | 0.456 theta - 0.000385 theta^2 | -0.285 theta + 0.000453 theta^2 | 1.8 mm |
| scaption, p = 40 | 0.032 theta - 0.00099 theta^2 | 0.441 theta - 0.00050 theta^2 | -0.086 theta - 0.00055 theta^2 | 2.3 mm |
| flexion, p = 90 | 0.082 theta - 0.00153 theta^2 | 0.177 theta + 0.00102 theta^2 | -0.045 theta - 0.00082 theta^2 | 4.6 mm |

- **Plane:** interpolate the coefficients linearly in p between 0, 40 and 90. Clamp outside 0-90; flag horizontal adduction
  (p > 90) and extension (p < 0) as extrapolation.
- **Above 135 deg:** continue with the slope at 135 deg (no data beyond 132-138 deg).
- **Body scale:** multiply by S_clav = clavicle length / 154 mm. For the rig, 156/154, so about 1.0.

Lookup values, if a table is preferred (ant / sup / lat):

| theta | abduction | scaption | flexion |
|---|---|---|---|
| 15 | -6.9 / 6.2 / -3.5 | 0.2 / 6.2 / -1.4 | -1.4 / 0.9 / -1.0 |
| 30 | -13.5 / 12.7 / -7.9 | 0.5 / 12.7 / -3.3 | -2.9 / 2.1 / -2.5 |
| 45 | -18.1 / 19.8 / -12.1 | -0.9 / 19.8 / -5.4 | -1.2 / 9.2 / -3.8 |
| 60 | -20.5 / 26.9 / -15.7 | -2.7 / 25.6 / -7.8 | -1.2 / 14.8 / -5.6 |
| 75 | -22.6 / 32.0 / -19.0 | -3.6 / 30.8 / -9.8 | -1.9 / 21.3 / -8.2 |
| 90 | -23.6 / 37.7 / -21.8 | -4.8 / 34.8 / -11.9 | -1.6 / 25.4 / -10.3 |
| 105 | -24.0 / 43.6 / -24.5 | -6.5 / 39.0 / -13.9 | -3.7 / 30.8 / -13.1 |
| 120 | -24.3 / 49.4 / -27.9 | -11.7 / 45.8 / -18.4 | -14.6 / 33.5 / -17.4 |
| 135 | -24.6 / 54.3 / -30.3 | -13.6 / 52.4 / -22.9 | -21.4 / 41.8 / -21.5 |

**Variability band [I]:** inter-subject 1 SD is about +-(10, 7, 7) mm at 90 deg and +-(12, 10, 10) mm at 120 deg. Scale
linearly with theta/120 below 120 deg.

Extra terms:

- Raising vs lowering: +-5 mm.
- Optional shrug term: s x (-27, +80, -24) mm x (1 - 0.5 theta/180), with s in [-0.2, 1]. The 0.5 factor encodes "range halves
  at max elevation" (Klopčar).
- GH-in-glenoid: 0 to +10 mm along the humeral long axis (Dal Maso).

### L2, upper bound (skin-marker family; Zhang 2020 polynomials [R] x d0 = |IJ - GH| = 190.6 mm in the rig [I]; mean of 16 planes)

- ant = -2.087e-7 theta^4 + 8.148e-5 theta^3 - 1.0616e-2 theta^2 + 0.25769 theta
- sup = -1.351e-5 theta^3 + 3.0934e-3 theta^2 + 0.34670 theta
- lat = -2.438e-6 theta^3 - 2.676e-5 theta^2 - 0.26989 theta

The constant terms are removed so that d(0) = 0. The axes follow from their Eq. 1: x = (IJ-PX) x (C7-PX) points right,
z = IJ/C7 midpoint minus PX/T8 midpoint points up, y = z x x points anterior. This assumes right arms (the paper does not state
the side).

### L3, Klopčar & Lenarčič 2006 [R], as an alternative skin-marker law

Girdle S->G vector (rig: SC to GH, d0 = 170.5 mm):

- elevated by phi_ed = max(0, 0.36 theta - 10.8) deg about the horizontal axis perpendicular to the girdle
- protracted by phi_pr = min(0, -0.22 theta + 15.4) deg about the vertical axis (negative = retraction)
- scaled by (-1.6e-5 theta^2 + 3e-4 theta + 1)

This law shortens the girdle by 31% at 150 deg (86 mm medial). Treat it as the least physical of the three.

---

## 10. Data to collect to settle it

1. **OpenSim Seth 2016 and 2019 runs** (ask before downloading).
   - Extract GH-in-thorax from the bundled bone-pin trials (1 subject) and the trakSTAR trials (shrug, flexion, abduction,
     +-2 kg).
   - Drive the model with the section 3 clavicle and scapula curves, to check L1's geometry (clavicle length, AC-to-GH vector)
     against a validated model.
   - Report per plane at 30 / 60 / 90 / 120 deg.
2. **OpenCap of the user** (two phones).
   - Motions, 3 slow repetitions up and down each:
     - arm raises in planes 0 / 40 / 90 deg to maximum
     - the same at 90 deg elevation with full internal and full external rotation, for the axial-rotation question
     - shrugs at 0, 90 and maximum elevation
     - with and without 1-2 kg in the hand
     - the 8 ADL clips
   - Keep Wave and Walking held out, as now.
   - Use the triangulated shoulder / acromion keypoints relative to thorax keypoints directly. **To check:** whether OpenCap's
     default model has any scapula or clavicle DOF. If its shoulder is a ball joint, IK output will not show girdle translation.
   - Video keypoint accuracy at the acromion is not validated in anything read here.
3. **Cheap physical check of the scale.**
   - Acromion sticker and ruler against a wall: vertical and AP acromion displacement at 0 / 90 / maximum in the 3 planes.
   - L1 predicts about 35-38 mm superior at 90 deg in scaption and abduction. The rig predicts 13 mm. L2 predicts about 46 mm.
     A 1-minute measurement separates them.
4. **Acromion-plate test** (if the scapula-tracking base option is pursued): an IMU or AprilTag plate on the acromion vs skin
   landmarks, checked against the 100-120 deg validity limit above.

---

## Sources

Numbers are tagged in the text. "Abstract" means only the abstract was read.

- Ludewig PM, Phadke V, Braman JP, Hassett DR, Cieminski CJ, LaPrade RF (2009). Motion of the shoulder complex during
  multiplanar humeral elevation. *J Bone Joint Surg Am* 91(2):378-389. https://pmc.ncbi.nlm.nih.gov/articles/PMC2657311/
  (text, Table I, Fig. 5-A/5-C images. The per-angle appendix tables were not reachable: the supplementary PDF sits behind a
  captcha.)
- Seth A, Matias R, Veloso AP, Delp SL (2016). A biomechanical model of the scapulothoracic joint to accurately capture scapular
  kinematics during shoulder movements. *PLoS One* 11(1):e0141028. https://pmc.ncbi.nlm.nih.gov/articles/PMC4712143/ ; data
  and model https://purl.stanford.edu/br087nj9017 ; https://simtk.org/home/scapulothoracic
- Seth A et al. (2019). Muscle contributions to upper-extremity movement and work from a musculoskeletal model of the human
  shoulder. *Front Neurorobot* 13:90. https://www.frontiersin.org/articles/10.3389/fnbot.2019.00090/full ;
  https://simtk.org/projects/thoracoscapular
- Zhang C, Dong M, Li J, Cao Q (2020). A modified kinematic model of shoulder complex based on Vicon motion capturing system:
  generalized GH joint with floating centre. *Sensors* 20(13):3713. https://pmc.ncbi.nlm.nih.gov/articles/PMC7374450/
- Klopčar N, Lenarčič J (2006). Bilateral and unilateral shoulder girdle kinematics during humeral elevation. *Clin Biomech*
  21 Suppl 1. https://doi.org/10.1016/j.clinbiomech.2005.09.009 (abstract; equations as reproduced in Zhang 2020)
- Klopčar N, Tomšič M, Lenarčič J (2007). A kinematic model of the shoulder complex to evaluate the arm-reachable workspace.
  *J Biomech* 40(1):86-91. https://doi.org/10.1016/j.jbiomech.2005.11.010 (abstract)
- de Groot JH, Brand R (2001). A three-dimensional regression model of the shoulder rhythm. *Clin Biomech* 16(9).
  https://doi.org/10.1016/s0268-0033(01)00065-1 (abstract; coefficients not obtained)
- Xu X, Dickerson CR, Lin JH, McGorry RW (2016). Evaluation of regression-based 3-D shoulder rhythms. *J Electromyogr Kinesiol*
  29:28-33. https://uwspace.uwaterloo.ca/handle/10012/17860 (full text)
- Xu X, Lin JH, McGorry RW (2014). A regression-based 3-D shoulder rhythm. *J Biomech*.
  https://doi.org/10.1016/j.jbiomech.2014.01.043 (abstract)
- Grewal TJ, Dickerson CR (2013). A novel three-dimensional shoulder rhythm definition that includes overhead and axially rotated
  humeral postures. *J Biomech* 46(3):608-611. https://doi.org/10.1016/j.jbiomech.2012.09.028 (abstract); Grewal thesis
  https://uwspace.uwaterloo.ca/handle/10012/6373
- Gonçalves G (2021). A three-dimensional regression model of the shoulder rhythm in a wide-ranging envelope of humeral postures.
  MSc extended abstract, IST Lisbon.
  https://fenix.tecnico.ulisboa.pt/downloadFile/281870113705781/(Submit)ExtendedAbstract_GilGoncalves_79054.pdf
- Sahara W, Sugamoto K, Murai M, Yoshikawa H (2007). Three-dimensional clavicular and acromioclavicular rotations during arm
  abduction using vertically open MRI. *J Orthop Res*. https://doi.org/10.1002/jor.20407 (abstract)
- McClure PW, Michener LA, Sennett BJ, Karduna AR (2001). Direct 3-dimensional measurement of scapular kinematics during dynamic
  movements in vivo. *J Shoulder Elbow Surg*. https://doi.org/10.1067/mse.2001.112954 (abstract)
- Karduna AR, McClure PW, Michener LA, Sennett B (2001). Dynamic measurements of three-dimensional scapular kinematics: a
  validation study. *J Biomech Eng* 123:184-190. https://pages.uoregon.edu/biomech/obl/articles/2001_karduna_jbiomecheng.pdf
  (full text, Table 1)
- van Andel C, van Hutten K, Eversdijk M, Veeger D, Harlaar J (2009). Recording scapular motion using an acromion marker cluster.
  *Gait Posture*. https://doi.org/10.1016/j.gaitpost.2008.07.012 (abstract)
- Lempereur M, Brochard S, Leboeuf F, Rémy-Néris O (2014). Validity and reliability of 3D marker based scapular motion analysis:
  a systematic review. *J Biomech*. https://doi.org/10.1016/j.jbiomech.2014.04.028 (abstract)
- Warner MB, Chappell PH, Stokes MJ (2015). Measurement of dynamic scapular kinematics using an acromion marker cluster to
  minimize skin movement artifact. *J Vis Exp* 96:51717. https://pmc.ncbi.nlm.nih.gov/articles/PMC4354629
- Matsui K, Shimada K, Andrew PD (2006). Deviation of skin marker from bone target during movement of the scapula. *J Orthop
  Sci*. https://doi.org/10.1007/s00776-005-1000-y (abstract)
- Dal Maso F, Raison M, Lundberg A, Arndt A, Begon M (2014). Coupling between 3D displacements and rotations at the glenohumeral
  joint during dynamic tasks in healthy participants. *Clin Biomech*. https://doi.org/10.1016/j.clinbiomech.2014.08.006
  (abstract)
- Dal Maso F, Raison M, Lundberg A, Arndt A, Allard P, Begon M (2015). Glenohumeral translations during range-of-motion
  movements, activities of daily living, and sports activities in healthy participants. *Clin Biomech*.
  https://doi.org/10.1016/j.clinbiomech.2015.06.016 (abstract)
- de Groot JH, van Woensel W, van der Helm FC (1999). Effect of different arm loads on the position of the scapula in abduction
  postures. *Clin Biomech*. https://doi.org/10.1016/s0268-0033(98)90094-8 (abstract)
- Pascoal AG, van der Helm FF, Pezarat Correia P, Carita I (2000). Effects of different arm external loads on the
  scapulo-humeral rhythm. *Clin Biomech*. https://doi.org/10.1016/s0268-0033(00)00055-3 (abstract)
- Peeters I, Braeckevelt T, Palmans T, Van Tongel A, De Wilde L (2023). Kinematic analysis of scapulothoracic movements in the
  shoulder girdle: a whole cadaver study. *JSES Int*. https://doi.org/10.1016/j.jseint.2022.09.014 (abstract)
- Irshad TB, Pascoletti G, Zanetti EM (2026). Biomechanics of the sternoclavicular joint: an experimental and computational
  study. *J Shoulder Elbow Surg*. https://doi.org/10.1016/j.jse.2026.07.025 (abstract)
- Rettig O, Krautwurst B, Maier MW, Wolf SI (2015). Definition of anatomical zero positions for assessing shoulder pose with 3D
  motion capture during bilateral abduction of the arms. *BMC Musculoskelet Disord*.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4673792/
- Zimmermann Y, Sommerhalder M, Wolf P, Riener R, Hutter M (2023). ANYexo 2.0: a fully actuated upper-limb exoskeleton for
  manipulation and joint-oriented training in all stages of rehabilitation. *IEEE T-RO* 39(3).
  https://doi.org/10.3929/ethz-b-000584411 (full text, Eq. 3-4)
- Carignan C, Liszka M, Roderick S (2005). Design of an arm exoskeleton with scapula motion for shoulder rehabilitation. *ICAR
  2005*. https://ssl.umd.edu/system/files/private/pub_full_text/SSL05-003.pdf (full text, qualitative)

Sources that gave no usable numbers:

- Kim B, Deshpande AD (2017) Harmony, *IJRR* 36(4): full text not accessible. ANYexo 2.0 states that Harmony couples
  shoulder-girdle rotation to elevation with a predefined rhythm (Kim & Deshpande, ICORR 2015).
- Schiele A, van der Helm FCT (2006), *IEEE TNSRE* 14(4) https://doi.org/10.1109/tnsre.2006.881565 : abstract only (9-DOF arm
  model including the girdle).
- Nef T, Guidali M, Riener R (2009), ARMin III, *Appl Bionics Biomech* 6(2): not accessible.
- Mao Y, Jin X, Agrawal SK (2014), CAREX GH-centre estimation, https://pmc.ncbi.nlm.nih.gov/articles/PMC4023848 : one subject,
  inertial frame, no numbers.
- Inman VT, Saunders JB, Abbott LC (1944): not read.

Computation scripts (scratchpad, not in the repo), under
`/tmp/claude-0/-home-user-exo-shoulder/83445525-dbfd-5a74-afa6-eaabc370b170/scratchpad/calc/`:

- `rig_geom.py`: rig bone landmarks
- `gh_lit.py`: chain and digitised Ludewig curves
- `compare.py`: all source models vs the rig
- `fit_mc.py`: fits, Monte Carlo, shrug
