# Manufacturability audit of the morphology catalogue (2026-10-15)

Trigger (user, 2026-10-15): "I do not think I am able to make a 3 dof translating passive device ... two is probably the
most I can make ... is there actually a component that can be designed which serves these degrees of freedom for the
size they are presented at?" Rule now in CLAUDE.md ("Manufacturable joints only"). The test is per joint: does a real
component give exactly that freedom at the size the model used? Rotations are cheap (pin or bearing pair, miniature
U-joint, ball and socket, rod end). One slider is cheap. Two crossed rails are bulky and have to be shown to fit. A
3-translation joint does not exist as a compact part. Ranking: 0 passive translations, then 1, then 2 (hard maximum).

Scope: every row in `docs/concepts/catalogue.json` and `docs/concepts/rows/` with passive DOF > 0, and every design
whose active joints are not plain revolute hubs (rails, carriages, telescopes, rolling contacts, tapes, scissors, open
rings). The required travel is the best configuration's, taken from the row, the sweep log and the model code. "Model
envelope" is what the code samples as metal (constants quoted from `docs/concepts/models/<id>.py`).

Sources for component envelopes:
- **THK RSR miniature LM guide** (catalogue PDF, extracted with pdftotext):
  - RSR3M: block height M 4, width W 8, length L 12. Rail 3 wide x 2.6 high. C 0.18 kN, C0 0.27 kN. MA 0.293 N.m for
    one block, 2.11 N.m for a double block. Standard rail up to 220 mm.
  - RSR2N: height 3.2, width 6, length 12.4.
  - THK has phased the RSR line out for the SRS line, so a replacement part number is to be confirmed.
- **IKO LWL2**: 3.2 high x 6 wide, rail 2 wide. **IKO LWLF2**: 2.5 high, rail 2, slide unit 5 wide (IKO / trade press).
- **igus drylin RJMP-01-06**: 6 mm bore, OD 12, length 19, iglidur J liner (distributor listing).
- **Not re-checked online this session.** These are standard metric sizes from the usual catalogues. They are marked
  "(cat.)" in the table, and `tools/hardware_catalogue.json` should confirm them:
  - Kaydon Reali-Slim KAA10XL0 (25.4 x 34.925 x 4.762), KAA15XL0 (38.1 x 47.625 x 4.762), KA020XP0 (50.8 x 63.5 x
    6.35), KA025XP0, KA030XP0, KA045XP0 (114.3 x 127 x 6.35).
  - Miniature ball bearings MR52 (2x5x2.5), MR63 (3x6x2.5), MR83 (3x8x3), MR85 (5x8x2.5), MR117 (7x11x3), 6700
    (10x15x4).
  - Linear ball bushing LM3UU (3x7x10). Cam follower IKO CF3 (D 10).
  - HIWIN MGN5C (H 6, W 12, L 16).
- The parallel track's `docs/research/passive_dof_hardware.md` and `tools/hardware_catalogue.json` did not exist when
  this audit was written. Where they disagree with the numbers here, they win.

## Five findings that cut across designs

1. **The radial (skin-normal) slide is the part that cannot be built at the modelled size.** The 3-slide models
   (seed-offset-3r-slides, skin-normal-hubs-selfaligning, offset-axis-skin-hubs) add only `R_r` mm to the stage height
   for the radial slide, and they model no guide for it. The seed's own verifier note says "radial-slide guide hardware
   still unmodelled". A real guide that stands normal to the skin is block length + full travel tall:
   - RSR3M: 12 + 2 x 6.7 = **25.4 mm**.
   - LM3UU on rods: 10 + 13.4 = 23.4 mm, plus the rod ends.

   That alone is twice the 14 mm pass band. The red team on skin-normal-hubs measured how sensitive the leader is to
   stage height:
   - raising the stage 3 mm: gap 35.86 -> 45.72
   - raising it 6.5 mm: 52.04
   - `rt_snh/metric/out_stage_*`

   A swing-link parallelogram that lies flat on MR bearings is the only compact radial joint. It stands up by about
   its travel + 4 mm. That is still the "+6.5 mm" case.
2. **The 2-translation version of every offset-axis 3R is known in closed form.** The proof is in
   `offset-skin-normal-3r.py`. A cuff with two slides closes exactly (residual < 0.5 mm) only under these conditions:
   - the J1 and J2 axis lines pass through GH;
   - the slide plane is hub 3's plane;
   - J3's line can then sit anywhere, square on its skin.

   Measured cost of dropping the radial slide:
   - **seed-offset-3r-slides**: 57.95 with 3P -> **65.41** with 2P (R3-only offsets, row control
     `r3_only_spec_2_slides`), both on Bench(60,160) fast.
   - **skin-normal-hubs-selfaligning**: 35.86 with 3P (k722) -> **45.31** with 2P (offset-skin-normal-3r k3/k9, the k722
     seats with b1 = b2 = 0; S 6.0 / 7.2 / 0.5).

   The 2P cuff fits as two crossed RSR3M-class guides (below), so the 2P versions are the buildable members of this
   family.
3. **Translations can be traded for rotations.** offset-pointer-slip-sleeve closes the loop with one sleeve (1 R + 1 P
   on one rod) and a Hooke joint (2 R): **1 passive translation absorbs all 3 GH translations** (Jarrasse & Morel's
   n + p = 6). Its best configuration (k306, o = 0) is the spherical case. There the slide is idle on the bench and on a
   body it takes GH translation along the rod. The orientation readout is exact only while the U angles stay constant.
   A 15 mm GH shift at the 189 mm rod station tilts the U by about atan(15/189) = 4.5 deg. That is a sensing error the
   user's encoders would see, so it has to be judged and not assumed away. This is the one family that answers "unless
   you have an idea how that could be possible" with a real component: a rod in a linear-rotary bushing plus a
   miniature U-joint.
4. **Every chain also needs a place for the real GH translation (R10, about 15 mm), and that counts against the same
   budget.**
   - A spherical chain with 0 internal translations gets the cuff's slides: at most 2 (along + across the arm). The
     radial component goes to the cuff liner's compliance, which has to be stated and measured.
   - A design with internal passive translations (breathing-hubs lifts, scapula-halo radial slide, crossed-track slide,
     tape and C-track carriage slides) adds those to the 2 cuff slides. Most of them then exceed 2.
5. **Load ratings.**
   - MVP1: R17 allows <= 1 N.m about the shoulder and <= 5 N at the cuff. The exo's own weight and inertia through the
     stage is about 0.2 kg x 80 mm = 0.16 N.m. A single RSR3M block (MA 0.29 N.m) is marginal, and a double block or
     two blocks per axis (2.11 N.m) is fine. Two blocks lengthen each rail by 12 mm.
   - MVP2: about 10 N.m of assist would pass through the slides as moment. That needs MGN9-class guides or a stage that
     carries no moment. MVP2 decides that, not MVP1.

## Table

Abbreviations: P = passive translation, R = passive rotation, act = active. "gap" = bench gap on Bench(60,160) fast
unless marked v_ (verified, Bench(110,360) exact). Champion spherical 3R: 68.93.

| id | status, gap | joints (passive translations) | required travel | model envelope | real component | verdict | change and expected effect |
|---|---|---|---|---|---|---|---|
| seed-offset-3r-slides | verified, 57.95 (v 66.47) | 3 act O20 hubs; **3P**: along, across, radial | +-13.0 / 9.2 / 6.7 | rail 8x4, carriages 20x(20+2S)x4, 0.5 gaps; radial = +6.7 mm height, **no guide** | along/across: RSR3M (H 4, W 8, L 12; rail L = 12 + 2S + 2 = 40 / 32); radial: none compact (25.4 mm tall guide) | NOT BUILDABLE (3P; radial slide has no component) | 2P version = R3-only offsets: measured 65.41 (+7.5 vs 57.95 same bench); with swing-link radial instead: about +7 mm stage, est. +10-16 gap |
| skin-normal-hubs-selfaligning | screened, unverified 35.86 | 3 act O20 hubs (skin-normal tilt beta 0.34/0.42/0.21); **3P** XYZ stage | centred +-7.8 / 8.1 / 6.7 (k722; drift 12.1 / 8.7 / 8.3 about mid; the brief's 18.6/16.4/6.0 is an older uncentred record, k250 64.73) | the seed's stage (above) + radial = height only | as above | NOT BUILDABLE (3P) | 2P version = offset-skin-normal-3r (J1/J2 through GH): 45.31 (+9.5). Red team: VModel checks at neck 5 -> 148.06 (123 part jams), at neck 13 -> 37.78 |
| offset-axis-skin-hubs | ideated (modelled), k1 37.78 (k722 lines), DOE 49.12 | 3 act hubs on free offset lines; **3P** | S_res 7.8 / 8.1 / 6.7 (k1), 5.4 / 5.0 / 7.3 (k59) | seed stage | as above | NOT BUILDABLE (3P) | its 2P subfamily is offset-skin-normal-3r; stop sweeping 3P offsets |
| offset-skin-normal-3r | screened 45.31 (CMA running) | J1, J2 hubs through GH, J3 skin-normal hub; **2P** in hub 3's plane; radial fixed at 0.5 mm closure tolerance | +-6.0 along, +-7.2 across | inverted along-guide: arm-fixed carriage 20x20x4, rail 8 x (20+2S) x 4, carriage A 4, across-carriage 4; carriage-B underside at rail + 9.5, top + 13.5 | 2x RSR3M crossed (inverted): block 4 + 1.5 adapter + block 4 = 9.5 + member-3 plate 2 = 11.5 (2 mm under the model); rails 26 / 28 mm | **BUILDABLE as modelled** (2P is the bulky maximum; real stack <= model) | use double blocks (L 24) on the along axis for moment: footprint +12 mm; radial GH translation goes to the cuff liner (state it, R10). Best buildable leader |
| offset-arc-selfalign | dead 133.12 | J1 ring, J2 Ti arc through a guide box, J3 hub; **3P** cuff stage | 25 / 10 / 5 | stage = 2 crossed LWL3/RSR3 (4 mm each) + radial 5 | radial: none | NOT BUILDABLE (3P) and dead | none (band tail is the limiter) |
| floating-centre-3r | refuted (v 136.31) | spherical 3R on a **3P** float under J1 (2 crossed roller slides +-8..12 + normal +-4) | slip law needs +-20 / 6-9 | XY stage 5.5 mm + 4 mm normal, plate slab 24.3 | crossed-roller slides are >= 8 mm tall each; normal: none | NOT BUILDABLE (3P) and refuted | none |
| offset-flex-aligner | ideated | 3 act hubs; **3P** flexure stage (0.5x10x60 Ti leaves +-12 / +-8, radial leaf pair +-4) | +-12 / 8 / 4 | 60 x 40 mm stage | leaf check: sigma = 3Et d/L^2 = 550 MPa (Ti, d 12); k = 24EI/L^3 = 1.3 N/mm per axis -> 15 N at 12 mm (R17 cap 5 N, spec <= 0.4 N/mm) | NOT BUILDABLE (3P; flexure too stiff for R17) | 2P version = offset-skin-normal-3r with RSR3M |
| offset-pointer-slip-sleeve | screened 58.90 (audit 76.42) | J1, J2 hubs; act J3 = spin of a sleeve on an O6 rod; **1P** sleeve slide + **2R** Hooke at the cuff | k306 o = 0: slide idle on the bench (GH translation only on a body); o > 0 needs 30-50 mm; U <= +-40 deg | rod O6, boss O12 x 10, sleeve O12 x 25, U ring RO 9 x 6 (2.5 section), cheeks 3 x 10 | drylin RJMP-01-06 (O12 x 19, slides and turns) or 2x MR bearings on a sliding sleeve; U: MR52-pinned gimbal ring or miniature cardan O10-12 | **BUILDABLE WITH CHANGES**: J3 encoder must read spin of a sliding sleeve (keyed magnet carrier on the rod); plain-bearing stick-slip under combined slide + spin | no stack change (RJMP fits the O12 x 25 envelope); ranks above 2P designs (1P). Open: U-angle readout error ~4.5 deg per 15 mm GH shift |
| cuff-sleeve-3r | ideated | spherical 3R, J3 = sleeve on rod; **1P** 5 mm axial float + 1 lateral cuff slide (**2P** total) | 5 + ~15 | sleeve O11 x 30, 2x MR85 | MR85 must not slide on its shaft (fretting): use RJMP-01-06 or a linear-rotary ball bushing | BUILDABLE WITH CHANGES | swap MR85 for a plain linear-rotary bushing (O12 vs O11: +0.5 mm radius) |
| breathing-hubs | modelling interrupted, no number | spherical 3R; **2P** radial lifts (J2, J3) on pinned parallelograms set by groove face cams + pushrod + bell crank | lift 8-15 mm | bars 3 mm, 4 mm apart, length Ls; cam O32 x 3; pushrod 1.5 | parallelogram on MR52/MR63 pins; cam custom; follower MR63 | NOT BUILDABLE as is (2 internal P + 2 cuff slides for GH and the 1.1-3.8 mm parasitic shift = 4 translations) | J2-only lift (1P) + 1 along-arm cuff slide = 2P; the 12-19 mm stack it needs is the +6.5 mm case above |
| crossed-skin-tracks | dead 94.55 (v 96.04) | act carriages on 2 tracks + swivel; **1P** radial slide on 2 rods along p2 | 0..Lmax 25 | stack 11 at L = 0 (A plate 2 + 6700 4 + B plate 2 + strip 3); slide beside the rail | 6700 (10x15x4) fine; radial rods: LM3UU 10 + travel -> rods stand 10 + L mm proud | NOT BUILDABLE at modelled height (radial slide) and dead | none |
| scapula-halo-track | dead 87.64 | act bogie on a closed non-circular Ti ring 8x5; passive pitch pivot (R) + **1P** 13 mm radial slide | radial 11-13 | carriage 20x16x9, no radial guide | custom track + CF3-class rollers; loop min turning radius 8.7 mm < 20 mm bogie | NOT BUILDABLE as modelled (radial slide; bogie cannot turn the loop) and dead | none |
| skin-cam-rails | ideated | 2 act rail carriages + act J2; **1P** ball-spline post along J2 (radial) | 0-15 | "one carriage stack + 0-15 mm of slide" | THK LT4-class ball spline: nut about O10 x 16 -> post 16 + 15 = 31 mm tall | NOT BUILDABLE (radial post) | keep crossed-muscle-rails (spherical, 0P) instead |
| seed-2r-cring | dead 129.98 | 2 hubs + act C-track carriage; **1P** slide along humerus | not reached (C-coverage limiter) | slide 40 x 10 x 6 | RSR5/MGN5-class (H 6, W 12) matches | BUILDABLE as modelled (1P), dead | none |
| seed-pauldron-shells | dead 79.46 | 2 shell-on-shell revolute slides + C-ring; **1P** cuff slide | static on bench | channel stack 7 (floor 2 + slider 2 + lips 2 + liner 1), carriage 25x12x6 | iglidur J liner sliders, custom shells | BUILDABLE WITH CHANGES (plain sliding shells, friction 0.1-0.2 on 250 deg tracks) | dead |
| seed-arc-rails | dead 73.0 | 3 act arc rails 8x4 + carriages 20x12x8 | R2 171 mm | as listed | no catalogue arc guide at 8x4 section / 60-170 mm radius; custom Ti arc + MR83 V-rollers | BUILDABLE WITH CHANGES (custom), dead | none |
| rail-elbow | refuted, 56.25 (v 64.7) | J1, J3 hubs; act J2 = carriage on a curved rail 8x5 on link 1 | psi -75..64 deg | carriage 20x16x9; best k1530/k2221 use `tele` = 2:1 cable telescope | custom Ti arc + 4-6 MR83 rollers (9 mm stack plausible) | rigid rail BUILDABLE WITH CHANGES (custom, 59.34 best); telescope NOT BUILDABLE in MVP1 (cable) | refuted by its own 3R control |
| scapular-race-j2-carriage | ideated (modelled), honest best 78.04 | act J1 = carriage on a scapula-fixed arc rail 10x4; O20 hub on it | 0-156 deg | carriage 26x22x8, hub plate = carriage top 3 mm | custom arc + MR83 rollers | BUILDABLE WITH CHANGES (custom race; play / preload by eccentric roller pins) | none measured |
| pointer-cslide | screened 69.84 | 2 donuts + act C-rail (custom caged-ball wire-race band 26x6, shoe 50-60 deg) | twist window 98 deg | band 26 x 6, 2 + 6 + 2 stack | Franke-type race wires in a custom Ti band + O3 balls + anti-creep cage; or plain iglidur arc (higher friction); KAA10XL0 donuts real | BUILDABLE WITH CHANGES (custom wire-race arc, cage creep) | reach-limited regardless |
| meridian-goniometer / twin-rail-one-hub / crossed-muscle-rails | ideated | 0P; act joints are arc carriages (wire-race or iglidur band, 6-8.5 mm) | - | 26 x 6 band / 10 x 5 rail | custom arcs; KAA15XL0 donut real | BUILDABLE WITH CHANGES (custom arcs) | prefer over P-carrying designs (0P) |
| deltoid-oval-track | modelling interrupted | act carriage on a closed arm-fixed oval 8x5 | unlimited | track 8 x 5 | custom closed track + bogie with pivoting roller pairs (min radius sets bogie length) | BUILDABLE WITH CHANGES | check min turning radius vs bogie (halo failed this) |
| magrace-arc-chain | modelling interrupted | 3 act arc races 12x2.5, O2 Si3N4 balls, magnet preload, no lips | - | stack 7 | 4x N52 O3x1.5 give a few N of hold-down; R17 allows 1 N.m of tilt -> races lift off | NOT BUILDABLE as modelled (no positive retention) | add lips or captive cage: +2-3 mm stack (9-10 mm) |
| trombone-arc | dead 88.29 | act swivel ring KAA15XL0 + act Ti band through a needle cam-follower guide 30x22x10 | arc 128 deg | as listed | KAA15XL0 real; CF3-class followers real | single stage BUILDABLE, dead; best 2-stage telescope NOT (2:1 cable) | none |
| sliding-rivet-pauldron | dead 176.96 | 3 joints as follower pairs in arc slots (O8x4 rollers), 2 mm plates | - | stack 8.5 | MR84 (4x8x3)-class rollers on pins | BUILDABLE WITH CHANGES (slot play), dead | none |
| fraction-pauldron | dead 101.68 (v 104.42) | 4 passive lame angles (R about one axis, cage-coupled by rolling) + act hub + act arm-arc carriage | - | lames 2 + gap 0.6 | rolling cage between lames is friction-coupled, not positive: fractions drift | NOT BUILDABLE as modelled (coupling needs a rack = gear, MVP1-illegal) | dead |
| pauldron-lame-telescope | ideated | 2 passive lame positions (curved P about a2, pin-in-slot or lazy-tongs coupling) + act stack extension | - | lames 24-40 x 3 | custom curved telescoping bands with edge rollers | BUILDABLE WITH CHANGES only as a custom curved telescope (hard) | prefer rigid alternatives |
| geodesic-strap-gimbal | ideated | act J1, J3 hubs; act J2 = strap extension (Bi-STEM NiTi tape 0.3 x 20 or telescoping arc); passive spool (R) + **1P** guide radial slide | - | strap 20 mm | a tape cannot hold link 2's orientation (no bending / torsion stiffness); Bi-STEM tapes are special-process parts | NOT BUILDABLE as specified | telescoping Ti arc variant = trombone family (dead) |
| tape-spool-humeral | ideated | act 2R pointer; act carriage on a NiTi tape 0.35 x 18; passive radial **1P** + yaw R + spool R | - | carriage 22x20x7, 4x MR52 | pre-shaped superelastic tape: not a stock part | NOT BUILDABLE as specified (tape) | replace the tape by a rigid arm-fixed track = acromion-pointer-arm-ctrack |
| acromion-pointer-arm-ctrack | ideated | act 2R pointer; act carriage on an arm-fixed skin-shaped C-track; **1P** radial + swivel R (+ optional along-arm float -> **2P**) | radial follows the track's radius change (arm skin 38-73 mm round the axis) | track +4 mm over skin | custom CNC Ti track + roller carriage; radial: RSR3M lying tangential is impossible (it is radial) -> swing link | BUILDABLE WITH CHANGES (radial as a swing link, ~travel + 4 mm) | GH translation: the along-arm float makes 2P, the cap |
| lone-helix-humeral | ideated | act 2R + act carriage on a helical, variable-radius rail; **2P** axial + radial | pitch + radius change | - | a non-planar track twists under the carriage: needs an extra passive R; radial again a swing link | NOT BUILDABLE as specified | - |
| scapular-skate-remote-j1 | ideated | puck on a ball cage: act in-plane rotation + **2P** in-plane translations (set by closure) | +-handler slip | plate 3 + puck | custom planar ball-cage sandwich (about 3 plate + 2 ball + 3 puck + 1.5 lip = 9.5 mm); cage creep | BUILDABLE WITH CHANGES (custom planar bearing, 2P) | GH translation normal to the plate has no slide (liner) |
| skin-stretch-scissor | modelling interrupted | spherical 3R, J2 = lazy-tongs N = 4; 12 pivots (R) + **2 pin-in-slot** (P) | - | two bar layers + O8 bosses = 5.5 | MR63/MR52 pivots, slots with a pin roller | BUILDABLE WITH CHANGES (pivot play x N: tip play grows with every cell; preloaded pivot pairs) | count the 2 slots as P |
| lazy-tongs-polar / lazy-tongs-j2 / tongs-tripod | modelling interrupted / ideated | scissors: 9-24 passive pivots (R), lazy-tongs-j2 + 2 end slots (P) | - | 6.5 mm two layers | MR pivots | BUILDABLE WITH CHANGES (play and compliance accumulate per cell) | - |
| rolling-fin-j2 / rolling-cone-elbow / core-cone-chain / rolling-cone-3r / rolling-cone-knee-3r | modelling interrupted / ideated | rolling-contact joints (act), held by 0.1 mm crossed bands; 0P | - | fins 6 tall, discs O14 x 4.5 | CORE / Jacob's-ladder joints exist, but in a serial chain each joint must carry tilt moment, which prises the rolling pair apart | NOT BUILDABLE as a serial joint at MVP1 loads | only inside a closed loop (rolling-elbow-fivebar) |
| rolling-elbow-fivebar | modelling interrupted | 5-bar loop: 2 rolling elbows + passive R at W; act A1, A2, D | - | link thickness 4 | bands in a loop see mainly in-plane load | BUILDABLE WITH CHANGES (band fatigue test) | - |
| cam-unfold-4th | modelling interrupted | 3 act hubs + passive cross-spring flexure knee (+-18 deg, 0.4 x 6 Ti leaves) slaved by a groove cam (MR52 follower, O2 pushrod) | +-18 deg | flexure 6 mm, cam 3 mm | leaf stress about E t theta / 2L <= 500 MPa needs L >= 14 mm; the knee also carries link 2's moment | BUILDABLE WITH CHANGES (MR117-pair pin instead of the flexure: +6 mm at the knee) | - |
| cam-coupled-4r | modelling interrupted | 4R, passive J2 + roller pin in a base slot (curved P + R) | - | - | MR63 roller in a milled slot | BUILDABLE | - |
| seed-rcm-parallelogram | interrupted, approx 275 | R1 + double parallelogram (passive pins) + C-ring + **1P** cuff slide | - | ring 82 mm | MR pins, custom ring | BUILDABLE WITH CHANGES (C-ring custom) | - |
| SPM / five-bar / four-bar family: seed-spm-3rrr (dead 193.44), spm-coaxial-turret, convergent-spm-twistleg, crown-cospm, coaxial-crown-spm, coaxial-spm-scapula, three-head-deltoid-spm, fivebar-roll (dead 89.13), five-bar-pointer-turret, scapular-five-bar-twist, fourbar-virtual-joint, coupler-path-j1, cruciate-knuckle-3r | mixed | 3-9 passive revolutes, 0P | - | P14 pins / O16-20 hubs / nested rings | MR117 / MR85 / 683 pin pairs; nested KA020-030XP0 rings (cat.) | BUILDABLE (rotations only) | ranked by the bench only |
| human-closed-crank-rods / rus-tripod-gh-centre / human-closed-telescopes / gh-tripod-telescoping-struts | modelling interrupted / ideated | U (2R) + S (3R) or U-P-U; act cranks or telescopes; 0 passive P | strut length ratio up to 1.56 | O5-10 tubes, O14 U / O8-10 balls | miniature cardans O10-14, rod ends / ball studs M3 (igubal-class), telescope on LM-bushing or drylin | BUILDABLE | readout depends on GH translation (about 4 deg per 10 mm): judge it |
| deltoid-strut-tripod / dome-telescope-tripod / base-rail-tripod / deltoid-trilateration / rotator-cuff-pair | modelling interrupted / ideated | act curved slides or curved telescopes + passive R pivots; 0P | - | 12 x 6.5 channels | curved caged-ball telescopes: custom, no catalogue part | BUILDABLE WITH CHANGES (custom curved telescopes, hard); strut tails as in trombone | - |
| annular-ring-3r / crown-ring-3r / risley-turret / back-anchored-ring-3r / lamellae-pauldron / armband-pointer | refuted / screened / dead / ideated | open-ring revolutes, 0P | - | ring + housing 8 mm (4.76 section) | KAA10/15XL0, KA020-045XP0 (cat.) | BUILDABLE as modelled | the rings lose on the bench, not on hardware |

## Notes per design (the ones with numbers)

**seed-offset-3r-slides (verified 66.47).** The radial slide (+-6.7 mm) is a height increment in the model,
`zb = tr + RAIL_H + RUN + CAR_H + RUN + R_r`, with no guide. Two consequences:
- The design has 3 passive translations, which the rule never allows.
- The verified number is optimistic by the missing guide.

The row's own controls give the 2P answer: R3-only offsets with 2 slides score 65.41 against 57.95 on the same bench.
With the spherical control at 58.79, **the offsets plus slides buy nothing a 2P design keeps**. Recommendation: retire
the 3P row and keep the spherical directions (hand d_el, d_wd, d_wa to the spherical sweep, as its verdict already
says).

**skin-normal-hubs-selfaligning (35.86, unverified; red team in `rt_snh/`).**
- The chain alone, scored without the stage, is 27.06.
- The stage drags the number up as it gets taller: +3 mm gives 45.72, +6.5 mm gives 52.04.
- Under the seed's verifier checks at neck 5, 123 poses jam on parts (148.06). Neck 13 restores 37.78.

Hardware:
- The XY part (+-7.8 / 8.1) fits two RSR3M guides.
- The radial +-6.7 needs a 25 mm-tall guide or a swing link. The swing link is about the +6.5 mm case: **an estimated
  ~52 with a real 3P stage, and never allowed anyway.**
- The 2P member with J1/J2 lines through GH is offset-skin-normal-3r at 45.31. Its J3 hub on a skin-normal seat (b3 0.2)
  keeps most of the gain over the champion's 68.93.

**offset-skin-normal-3r (45.31, CMA running): the buildable leader of the slide family.**
- Two crossed RSR3M (inverted, block on the cuff) stack 9.5 mm plus a 2 mm member-3 plate. That is 11.5 mm, against
  13.5 modelled.
- Rails are 26 mm (along, +-6.0) and 28 mm (across, +-7.2).
- A double block on the along axis is needed for the MVP1 moment. It adds 12 mm of rail, still within the modelled
  32 x 34 mm stage footprint.
- The radial closure is exact by construction. A real body's radial GH component (part of R10's ~15 mm) goes into the
  cuff liner. The base-slip judge should quantify it, and it has to be reported as liner compliance.
- It still sits at the 2P maximum the user called bulky. It wins only if it beats a 0P / 1P design by more than the
  bench noise.

**offset-pointer-slip-sleeve (58.90; audit 76.42).**
- The polished best has o = 0, so the rod points at GH and the slide only takes GH translation.
- The model's envelope is O12 x 25 for the sleeve and O6 for the rod. igus drylin RJMP-01-06 (O12 x 19, iglidur J)
  fits it and both slides and turns.
- The Hooke joint can be a gimbal ring on 4x MR52.
- The J3 encoder has to read the spin of a sleeve that also slides. A magnet carried by a key in a rod flat, with the
  sensor on the cuff bracket, does that.
- **1 passive translation for all of GH translation.** By the new ranking this beats every 2P design that does not
  clearly out-score it.
- Its limiters are proximity, not hardware: hub 2 and the bar float at about 32 mm. Its sensing error under GH
  translation (about 4.5 deg per 15 mm) needs a judge.

**rail-elbow (refuted; v 64.7).** The best numbers (k1530, k2221) use the 2:1 telescoping rail. That needs a cable loop,
which is MVP1-illegal. The legal rigid rail reaches 59.34 and is a custom arc with MR83 rollers. It is refuted by its
own spherical control either way.

**pointer-cslide (69.84), scapular-race-j2-carriage (78.04), the crossed / twin rails.** These are 0P designs whose
active joints are custom arcs. No catalogue curved guide comes near an 8 x 5 or 26 x 6 section at 45-170 mm radius.
The buildable form is a Ti arc with either ground race wires and caged balls, or V-edges and miniature-bearing rollers
(MR63 / MR83) on eccentric pins for preload. Machinable by the user, at the modelled height.

## What this changes in the loop (next)

1. Concept rows get a `hardware` field (`{"passive_trans": n, "components": [...], "buildable":
   "as_modelled|with_changes|no"}`), and `tools/concept_bench.py` reports passive_trans next to gap. A 3P row is not
   ranked. A 2P row is ranked behind any 0P / 1P row within the bench noise of about 3 gap.
2. The three 3P slide models get a switch `radial="swinglink"` that samples a real swing-link radial joint (travel + 4
   mm). Until then their numbers carry the label "3P, not buildable".
3. The verifier rejects any joint without a component in `tools/hardware_catalogue.json` once that file lands.
   Re-check this table against it.
4. Red team for the 2P leader (offset-skin-normal-3r): the pose that drives each RSR3M block to its end stop, the
   moment on the along block at the overhead peak, and how much the liner compresses radially under the R10 slip law.
