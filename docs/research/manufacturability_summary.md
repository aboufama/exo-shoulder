# Can it be built? Passive joints against real parts (summary for the user, 2026-10-16)

You asked on 2026-10-15: "is there actually a component that can be designed which serves these degrees of freedom
for the size they are presented at?" This page is the short answer. The detail is in two research notes, written
separately, that reach the same verdict:
- `docs/research/passive_dof_hardware.md`, with part tables, sources and confidence marks. Its machine-readable
  companion is `tools/hardware_catalogue.json`.
- `docs/research/manufacturability_audit.md`, with one row for every catalogue design.

Conventions on this page:
- "Gap" is the bench's distance from the goal. Lower is better, and 0 means every requirement passes.
- "Fast" and "exact" are the two bench grids.
- Part sizes marked (cat.) were read from the manufacturer's PDF table. Sizes marked (mem.) are from memory and must be
  confirmed before CAD.

---

## 1. The direct answer: is there a real part for each freedom at the size we drew?

**You are right. Three passive translations at the cuff cannot be built at the sizes we modelled. Two can.**

The part that does not exist is the third slide, the one that moves the cuff toward or away from the skin
(the radial, skin-normal slide).
- The models gave that slide **zero height**: only its stroke lifted the carriage above it.
- A real linear guide stood on end is as tall as its block plus its full stroke. For the ±6.7 mm the models used, a
  THK RSR3M is 12 + 13.4 ≈ **25 mm** tall. That is outside the 14 mm pass band before anything else is stacked on it.
- Nothing else fits in 14 mm either:

| radial travel | guide on end (RSR3M) | flat parallelogram on pins | titanium leaf flexure | soft cuff liner |
|---|---|---|---|---|
| ±3 mm | 18 mm | ~10 mm | ~9 mm (30 mm leaves) | **6-8 mm foam / TPU lattice** |
| ±6 mm | 24-25 mm | ~16-17 mm | ~15 mm (42 mm leaves) | needs ≥ 12 mm: out of band |

The flexure and liner figures are calculated.

Per family, at the size each was presented:

| family (designs) | passive freedoms as drawn | real component and real height | buildable? |
|---|---|---|---|
| **Offset 3R + 3-slide cuff**: seed-offset-3r-slides, skin-normal-hubs-selfaligning, offset-axis-skin-hubs, floating-centre-3r, offset-arc-selfalign | 3 translations (e.g. ±13 along / ±9.2 across / ±6.7 radial) | along + across: 2 x THK RSR3M or HIWIN MGN03C (H 4.0 each, cat.) crossed = **10.5 mm**; radial: no part fits (25 mm guide) | **No.** It is over the 2-translation cap, and the radial slide has no part. |
| **Flexure aligner**: offset-flex-aligner | 3 translations ±12 / 8 / 4 in a 60 x 40 mm stage | Ti-6Al-4V leaves 0.2 mm thick need 48 mm for ±12 alone; ~1.3 N/mm gives 15 N at 12 mm, against the 5 N limit (R17) | **No**, at that size and stiffness. |
| **Offset 3R + 2-slide cuff**: offset-skin-normal-3r | 2 translations in hub 3's plane (±5.8 along, ±7.0 across used) | 2 x RSR3M / MGN03C crossed, inverted: **10.5-11.5 mm** (1.5 base + 4 + 1 adapter + 4), ~40 x 33 mm, ~10 g. The model carries 13.5 mm, which is conservative. | **Yes, for MVP1.** |
| **Champion spherical 3R + your cuff slides**: baseline / param_r20, the plain 3R at new axes | 0 in the chain; 2 cuff slides (along + across under BOTTOM) | 2 x RSR3M under BOTTOM, **~10.5 mm**; radial part of the shoulder's own slip goes to the liner | **Yes.** This is your original plan, within the cap. |
| **Slide + spin sleeve + U-joint**: offset-pointer-slip-sleeve, cuff-sleeve-3r | 1 translation + spin on one rod, + 2 U-joint rotations | igus drylin RJMP-01-06 (6 x 12 x 19, verified) or iglidur J sleeve Ø8 x 10-12 (mem.) on a Ø6 hard-coated rod; U-joint on MR52 / MR63 pins | **Yes.** The modelled Ø12 x 25 sleeve is larger than the real part. |
| **Radial lifts or radial slides elsewhere**: breathing-hubs, geodesic-strap-gimbal, lone-helix-humeral, acromion-pointer-arm-ctrack, tape-spool-humeral | 1-2 radial strokes | per the radial table above | **Only if the radial stroke is ≤ 3 mm** and taken by the liner; otherwise no. breathing-hubs reaches 4 translations with its cuff slides. |
| **Telescoping arcs**: rail-elbow and trombone-arc best scores | 2-stage telescope | it needs a 2:1 cable or rack to keep the stages in step, which is not allowed in MVP1 | Telescope **no**. A single rigid rail yes, but it scores worse. |
| **Rotation-only families**: rings, SPM, five-bars, closed tripods with rod ends | 0 translations | MR63 / MR85 / MR117 pin pairs (~5-6.5 mm), Kaydon KAA10/15XL0 (mem.), M3 rod ends, miniature U-joints | **Yes.** They lose on the bench, not on hardware. |
| **Odd ones**: magrace-arc-chain, fraction-pauldron, rolling-cone joints, crossed-skin-tracks, scapula-halo-track | various | magnets cannot hold against tilt; the friction cage drifts; a rolling pair prises open under moment; the radial post is 31 mm; the track turns tighter (8.7 mm) than a 20 mm bogie can follow | **No, as drawn.** All were already dead on the bench. |

**A structural point you will hit in MVP2.** In every "offset 3R + slide stage" design, the stage carries the arm's
whole orientation torque.
- Miniature guides are rated for about 0.3-2 N·m per block (RSR3M MA 0.29 N·m, or 2.1 with a double block; MGN05C 2.0;
  all cat.).
- That is enough for the unpowered MVP1, where tracking loads are under ~1 N·m (estimated).
- It is 10-80x short of the 25 N·m MVP2 design moment.
- For MVP2 the stage needs one of these:
  - an MGN12H (13 mm tall, 38 N·m);
  - two rails at least ~50 mm apart with two blocks each;
  - pins instead of slides (section 3).

## 2. What is buildable with at most 2 passive translations, and how good it is now

All of the following respect the cap and map onto stock parts:

| design | passive translations | real parts | best honest number now | bench | status |
|---|---|---|---|---|---|
| **offset-skin-normal-3r** k4216 | 2, both in hub 3's plane | 2 x RSR3M / MGN03C inverted (10.5-11.5 mm) | **gap 32.61** (score 88.14); **37.42** if metal within 1 mm of the skin counts as contact | Bench(60,160) fast | **Screening leader, not yet verified.** The verification on Bench(110,360) exact is owed; the 3-slide relative lost 6.8 points that way. |
| plain spherical 3R at the new CMA axes (from rail-elbow k1530 / k2221) | 0 in the chain + your 2 cuff slides | MR117 hubs + 2 x RSR3M under BOTTOM | **60.03** large bench (champion 75.94 on the same bench); 51.97 fast. Built L1 CAD `l1_3r-k2221`: R1 56.1 % vs 54.1 % for the built champion | Bench(110,360) exact, geometry frozen from (60,160) | **Verified, and built at L1.** It is the best number that has been both re-measured and turned into CAD. |
| offset-pointer-slip-sleeve k306 | 1 (+ spin, + 2 U rotations) | drylin RJMP-01-06 on a Ø6 rod, MR52 U-joint | 58.90 | Bench(60,160) fast | Screened; exact run owed. Hub 2 still floats ≥ 32 mm. |
| seed-offset-3r-slides, 2-slide version (offsets on J3 only) | 2 | 2 x RSR3M | 65.41 (its 3-slide form scored 57.95 on the same bench) | Bench(60,160) fast | Measured once. Its built L1 CAD failed R6 (0.81 mm). |

**The best honest score for a buildable design** depends on how strictly "honest" is read.
- On the screening bench it is **offset-skin-normal-3r at 32.61** (Bench(60,160) fast), unverified. It beats the
  3-slide design it replaces (35.86 there, and refuted at 45.76 on the large bench) without the slide that cannot be
  built. Removing the third slide cost nothing on this bench.
- The best number that has been verified and turned into CAD is **the plain spherical 3R at the CMA axes: 60.03 on
  Bench(110,360) exact**, against 75.94 for the current champion.

**Caveats on offset-skin-normal-3r:**
- The bench has no shoulder-blade slip. On a real arm, the shoulder joint's slip relative to the scapula has a radial
  part (up to ~15 mm in total, R10). The 2-slide cuff cannot take it, so the liner must, at ≤ 3 mm. That still has to
  be measured on the R10 judge.
- Remaining limiter: the J2 fold (47 of 220 poses). No slide or offset moves it. The fold frontier says 50 / 50 deg arcs
  keep 96 % of the workspace fold-free, and that search (fold-sph3r) is running.

## 3. Getting the freedom without a third slide

Ranked by what they cost in height:

1. **Restrict the offsets so that 2 slides are exact.**
   - Two-slide closure theorem: a translational cuff closes an offset 3R exactly with 2 slides if and only if the J1 and
     J2 axis lines pass through the shoulder centre, and the 2 slides lie in hub 3's plane. The J3 line is free and can
     tilt and offset.
   - This is offset-skin-normal-3r. Cost: 0 mm extra (10.5-11.5 mm stage).
2. **Planar RR: two passive pins parallel to J3, in place of the 2 slides.**
   - Same two in-plane freedoms. With 20 mm links it covers ±13 x ±9.2 mm and the elbow angle stays 48-134 deg, well
     away from folding flat.
   - **~6 mm tall**, ~48 x 20 mm swept, on MR63 / MR85 pairs or iglidur pins. That is 4.5 mm lower than crossed guides.
   - The pins also carry the tilting moment that miniature guides cannot, which matters for MVP2.
   - Costs:
     - two more pins;
     - the arm's twist reading becomes J3 + both pin angles, so the pins need magnet encoders, or an IMU on the cuff;
     - MVP2 torque path to be checked.
   - Next bench variant: `offset-skin-normal-3r` with `stage=rr`, links 15-25 mm.
3. **One translation as a flat parallelogram.** For a slide along the arm: 4 pins, links 40 mm, ±13 mm, **~6 mm tall**,
   with 2.2 mm of sideways drift over the stroke. The guide option is an RSR3M at 5.5 mm with plate, a 40 mm rail and
   ~3.5 g.
4. **Slide + spin on one rod.** An iglidur sleeve on a hard-coated rod (anodised 7075, TiN-coated Ti or 1.4034).
   - Real parts:
     - drylin RJMP-01-06, 6 x 12 x 19 mm;
     - iglidur J sleeve, about Ø8 x 10-12 mm in an Ø11-12 boss (mem.);
     - THK ST6 stroke bush, Ø12 x 19 (mem.), but that needs a hardened steel shaft.
   - Keep the sleeve length ≥ 1.5 x its bore so it does not jam like a drawer.
   - A ball spline (THK LT4X, Ø8 x 12, cat.) slides but does not spin. Use it only where the slide must carry twist.
5. **Trade translations for rotations.** A U-joint (2 rotations on MR52 pins) plus one sleeve slide absorbs the
   shoulder's translation, as in offset-pointer-slip-sleeve.
   - Rod ends (M3) or a ball stud (3 rotations) do the same in closed tripods.
   - The catch is the reading: the angle sensed drifts by about 4-4.5 deg per 10-15 mm of shoulder translation. A
     judge for that error is needed before relying on it.
6. **Liner compliance for the radial residual.** Up to ±3 mm in a 6-8 mm foam or printed TPU lattice cuff liner,
   stated as compliance and not counted as a joint. More than ±3 mm does not fit in band by any route.
7. **Flexures are centring springs (1-6 N), not free joints.**
   - Fixed-guided leaf length L = √(3·E·t·δ/σ).
   - Ti-6Al-4V 0.2 mm thick: 24 / 34 / 48 mm leaves for ±3 / ±6 / ±12 mm. Spring steel 0.1 mm: 20 / 28 / 39 mm.
   - A nested XY flexure stage is ~70 x 70 mm at ±6 mm.
   - They can serve MVP1 as a centring element, with a fatigue proof (R9). They cannot be a hidden third slide.

## 4. What changes in scoring from now on

The rule is in CLAUDE.md ("Manufacturable joints only"). These are the bench and verifier changes that follow from it.
Items 1-5 still have to go into code: `tools/concept_bench.py` and the verifier do not read the catalogue yet. That is
the next loop task.

1. **Every joint names a real part.** The model reads its envelope from `tools/hardware_catalogue.json`:
   - guide height H + 1.5 mm plate;
   - rail length = block length + 2 x stroke + 2 mm;
   - 1 mm adapter between crossed guides;
   - a radial slide stands up by block length + 2 x stroke.

   No zero-height stages. The verifier rejects a design with a joint that has no component.
2. **At most 2 passive translations; none is ranked with 3.** The 3-slide rows keep their numbers for the record, but
   they carry `manufacturability: NOT BUILDABLE` in `docs/concepts/rows/` and are not ranked.
3. **Fewer translations wins a tie.** The passive-translation count is shown next to the gap. Between equal benches the
   order is 0, then 1, then 2.
4. **The radial residual is counted.** Up to 3 mm goes to the liner, stated in the row. A design that needs more is
   rejected.
5. **Moment check.** Each stage's static moment rating must exceed the MVP1 tracking moment (≤ ~1 N·m), and is flagged
   against MVP2's 25 N·m.
6. **R10 decides between 0, 1 and 2 cuff slides.** Today's bench has no shoulder-blade slip, so a slide's real benefit
   is invisible. The R10 judge with real GH translation is the instrument for that choice.
7. **Bench gains are checked against the champion at the same axes**, as before. The slides of seed-offset-3r-slides
   were worth -0.84 against its own spherical control: the gain came from the axes, not from the slides.

Values marked (mem.) must be confirmed before L1 CAD: IKO LWL1 / LWLF2 / LWL3 sizes, iglidur JSM part numbers, THK ST /
LM sizes, MR63 / MR85 / 6700 / KAA10XL0, and Misumi / NB equivalents.
