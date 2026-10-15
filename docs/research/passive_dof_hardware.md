# Passive DOF hardware: what real parts give a passive translation at exo scale

Research note, 2026-10-15. It answers the user's question of the same day: "is there actually a component that can be
designed which serves these degrees of freedom for the size they are presented at?" The machine-readable companion is
`tools/hardware_catalogue.json`. Models and verifiers should read their envelopes from it.

Where the numbers come from:
- **[cat]**: read from the manufacturer's PDF table today. These are the THK A1 pages for RSR and RSX, the HIWIN MG
  catalogue GW-11-5-EN-2207, the igus drylin N section and the THK LT / LT-X ball splines. URLs are at the end.
- **[dist]**: from a distributor or trade page. Confirm before CAD.
- **[mem]**: from memory, not checked. Confirm before CAD.
- **[est]**: my own calculation. The formula is given next to it.

---

## 0. Bottom line

1. **The user is right: a 3-translation passive stage is not buildable at the sizes we modelled.** The two in-plane
   slides are fine. The models gave them 4 + 4 mm layers, and real miniature guides are 4.0 mm tall (THK RSR3M,
   HIWIN MGN03C [cat]). **The radial (skin-normal) slide is the part that does not exist.**
   - The models gave the radial slide **zero height**: only its range lifted carriage B.
   - A real radial guide stands up by its block length plus its travel. For ±6.7 mm that is 12 + 13.4 ≈ **25 mm**
     with RSR3M.
   - The most compact all-revolute alternative, a near-flat parallelogram, still needs **~16-17 mm** [est].
   - Both are outside the 14 mm pass band before anything else is stacked on top.
   - So `seed-offset-3r-slides` (radial ±6.7), `skin-normal-hubs-selfaligning` (radial ±6.0-6.7) and
     `offset-flex-aligner` cannot be built as modelled.
2. **Two in-plane translations are buildable.** Two RSR3M / MGN03C guides stacked crosswise come to about
   **10.5 mm** including an adapter and a base plate. For ±13 x ±9 mm of travel the footprint is about
   40 x 33 mm and the guides weigh about 10 g. A model that carries this envelope is honest.
   - `offset-skin-normal-3r` has 2 slides in hub 3's plane and no radial slide. It is the translation design that
     maps onto real hardware.
3. **Rotations are cheap and translations are expensive.** This holds for every design.
   - A passive pin (MR63 / MR85, or an iglidur liner) is about 5-6.5 mm tall and needs no rail length.
   - Two pins parallel to J3 (a planar RR) give the same two in-plane translations as two slides, in about 6 mm of
     height. The cost is extra pins, and the arm's twist becomes q3 + qa + qb.
   - A slide plus spin about one axis is one plain iglidur sleeve on a rod, about Ø8-12 mm.
4. **A new structural fact for MVP2.** In every "offset 3R + stage" design the stage carries the arm's full
   orientation torque, because the 3R sets the arm's orientation through it.
   - Miniature guides are rated for **0.3-2 N·m** of static moment per block (RSR3M 0.29, MGN05C 2.0 [cat]).
   - That is fine for the unpowered MVP1, where tracking loads are well under 1 N·m [est]. It is **10-80x short** of
     the 25 N·m design moment for MVP2.
   - For MVP2 the stage needs one of these:
     - a single MGN12H block: 13 mm tall, M0X 38 N·m [cat];
     - two rails at least ~50 mm apart, with two blocks per rail;
     - revolute pins, which take tilting moments in a hub-sized boss.
5. **Answers, in brief** (details in section 4):
   - **(a) 1 translation along the arm:** RSR3M or MGN03C. 4.0 mm guide + 1.5 mm plate = **5.5 mm** tall, rail
     length = 12 + 2 x travel + 2 (40 mm for ±13 mm), ~3.5 g. Ball guide, so the arm can drive it.
   - **(b) 2 in-plane translations at the cuff:** two of those stacked, **~10.5 mm** and ~40 x 33 mm. The revolute
     alternative is a planar RR, **~6 mm** tall and ~48 x 20 mm swept.
   - **(c) radial ±3 mm:** **no guide.** Take it in the cuff liner's compliance (stated as such), or use a ~9-10 mm
     near-flat parallelogram or Ti leaf pad.
   - **(c) radial ±6 mm:** **nothing real fits in 14 mm.**
   - **(d) slide + spin:** an **iglidur sleeve** on a 6 mm hard-coated rod (Ø8 x 10-12 sleeve in a Ø11-12 boss
     [mem]), or a THK ST stroke bush Ø12 x 19 on a hardened rod [mem].

---

## 1. Miniature linear guides (rolling, buy)

What the model has to carry for each guide:
- the height **H** above its mounting face, plus a mounting plate (at least 1.0-1.5 mm);
- a rail of width W_r and length L_block + 2·travel + ~2 mm end margin;
- a block of W x L that rides on the rail.

Rails can be cut to any length; the holes fall at the pitch F.

| part | H | block W x L | rail W x H (pitch) | C / C0 (N) | static moment N·m (1 block) | mass block / rail per 100 | conf |
|---|---|---|---|---|---|---|---|
| IKO LWL1 | 2.5 | ? | 1 wide | tens of N | - | - | [dist] H, rest [mem] |
| IKO LWLF2 | 2.5 | 5 x ? | 2 | ~100 class [mem] | - | 0.21 g / 2 g | [dist] |
| IKO LWL2 | 3.2 | 6 x ? | 2 x 2 | 211 / - | - | - | [dist] |
| THK RSR2N | 3.2 | 6 x 12.4 | 2 x 2 (8) | 214 / 384 | MA 0.56, MC 0.44 | 0.8 g / 2.9 g | [cat] |
| HIWIN MGN02C | 3.2 | 6 x 12.5 | 2 x 2.0 | 220 / 400 | M0X 0.4, M0Y 0.6 | 1 g / 3 g | [cat] |
| **THK RSR3M** | **4.0** | **8 x 12.0** | **3 x 2.6 (10)** | 180 / 270 | MA 0.29 (2 blocks 2.1), MC 0.45 | 1.1 g / 5.5 g | [cat] |
| THK RSR3N | 4.0 | 8 x 16.0 | 3 x 2.6 | 300 / 440 | MA 0.73 (2 blocks 4.3) | 1.6 g / 5.5 g | [cat] |
| **HIWIN MGN03C** | **4.0** | **8 x 11.3** | **3 x 2.6 (10)** | 290 / 440 | M0X 0.7, M0Y 0.5 | 1 g / 5 g | [cat] |
| IKO LWL3 | 4 [mem] | 8 [mem] | 3 | 353 / 587 | - | - | [dist] |
| THK RSX5M | 6.0 | 12 x 16.9 | 5 x 3.5 (15) | 370 / 530 | MA 0.79 (2: 5.8), MC 1.38 | 2 g / 13.6 g | [cat] |
| HIWIN MGN05C | 6.0 | 12 x 16.0 | 5 x 3.6 (15) | 540 / 840 | M0X 2.0, M0Y 1.3 | 8 g / 15 g | [cat] |
| HIWIN MGN05H | 6.0 | 12 x 19.0 | 5 x 3.6 | 670 / 1080 | M0X 2.6, M0Y 2.3 | 10 g / 15 g | [cat] |
| THK RSX7M | 8.0 | 17 x 23.4 | 7 x 5 (15) | 1160 / 1540 | MA 3.3 (2: 23.1), MC 6.0 | 8 g / 22.7 g | [cat] |
| HIWIN MGN07C | 8.0 | 17 x 22.5 | 7 x 4.8 (15) | 980 / 1245 | M0X 4.7, M0Y 2.8 | 10 g / 22 g | [cat] |
| HIWIN MGN12H | 13.0 | 27 x 45.4 | 12 x 8 | 3720 / 5880 | M0X 38.2, M0Y 36.3 | 50 g / 65 g | [cat] |
| igus drylin N17 (NW-02-17 on NS-01-17), **plain** | 6.0 | 9.6 x 20 | 17 x 5.5 | Fz 50 static | Mx 0.31, My 0.18 | 1.7 g / 15 g | [cat] |
| IKO CRWM1 crossed-roller way (rail pair) | 4.5 | 17 wide (pair) | 2 x 8.5 [mem] | 125 / 120 | - | - | [dist] |

Notes:
- **THK RSR5M-15M** no longer appear on the RSR pages of THK's current A1 catalogue, which list only
  RSR2N/3M/3N/3WM/3WN/14WVM. THK's 5-15 mm stainless miniature is now RSX (same envelope class).
- **Misumi and NB** sell the same envelope class: Misumi SSEBZ / SSE2BZ and NB SEB/SEBS 5-7 are about H 6-8 [mem].
  They are not separate options in height.
- **Friction (R17).** Ball guides run at μ ≈ 0.002-0.005 [mem]. Under a moment M on a block of length L, the contact
  force is about 2M/L. With 1 N·m on a 12 mm block that is ~170 N, which is a sliding resistance of about 0.5-1 N on
  balls but **~25 N on a plain liner** (μ 0.15). Plain guides such as drylin N or a home-made iglidur dovetail are
  fine only where the stage carries no moment. Under moment they also jam unless L/W ≥ 1.5 (the drawer effect).
- **Can the user make or buy them?** Buy all of them. RSR3M and MGN03C are stock items; MGN02/03 are sold only
  mounted on their rail. The user makes only the adapter plate (Ti or 7075, 1-1.5 mm, M1.6 / M2 screws).
- **Crossed-roller ways** have no recirculation, so the stroke is about half the rail length minus the cage. Both
  carriers are self-made. They are stiffer than a miniature ball guide under moment, but **not lower**
  (4.5 mm per axis plus carriers) and wider (17 mm). They are not a better answer here.

## 2. Slide + spin, slide-only with torque, and rotary bearings

| part | does | envelope (d x D x L) | friction | conf |
|---|---|---|---|---|
| iglidur J sleeve, e.g. JSM-0608-10 | slide + spin | 6 x 8 x 10 | plain, μ 0.06-0.2 on a hard shaft | [mem] |
| igus drylin R RJUM-01-08 | slide + spin | 8 x 16 x 25 | plain; C 960 N | [dist] |
| THK ST6 stroke bush (ball cage, finite stroke) | slide + spin | 6 x 12 x 19 | rolling; **hardened shaft (≥ HRC 58), not Ti** | [mem] |
| THK LM4 ball bushing | slide (spin not rated) | 4 x 8 x 12 | rolling; hardened shaft | [mem] |
| THK LT4 ball spline | slide only, carries torque | 4 x Ø10 nut x 16 | rolling | [cat] |
| THK LT4X miniature ball spline | slide only, carries torque | 4 x Ø8 x 12 (14.4 sealed) | rolling | [cat] |
| MR63ZZ / MR85ZZ / MR117-2RS | pin | 3x6x2.5 / 5x8x2.5 / 7x11x3 | rolling | [mem] / [cat repo] |
| 6700ZZ thin deep-groove | pin with a Ø10 bore | 10 x 15 x 4 | rolling | [mem] |
| Kaydon KAA10XL0 / KAA15XL0 | large-bore pin | 25.4x34.9x4.76 / 38.1x47.6x4.76 (18 g, 40 N·m) | rolling 4-point | [mem] / [repo] |
| IKO CRBT305A | large-bore pin, high moment | 30 x 41 x 5 (20.7 g) | rolling | [repo] |

- **The most compact slide + spin** is a plain iglidur sleeve on a ground, hard-coated rod. Suitable rods are hard
  anodised 7075, TiN-coated Ti or 1.4034 steel. Ball parts, the stroke bush and the ball bushing, need a hardened steel
  shaft and grow to Ø12.
- **A ball spline is the answer to a different question.** It is the part for a translation that has to transmit
  torque about its own axis, for example an along-arm slide that also carries humeral rotation (`seed-2r-cring`).
- **A passive pin with no encoder** is two 2.5-3 mm plates on an MR63 or MR85 pair, about **5-6.5 mm** [est]. The plain
  version is two 2 mm plates on an iglidur sleeve, about **4.5-5 mm**. Compare the 12.25 mm of the O20 encoder hub.

## 3. Translations without a slide

### 3.1 Flexure stages (make: wire EDM from plate, or shim + clamps)

A fixed-guided leaf obeys σ = 3·E·t·δ / L², so **L = √(3·E·t·δ / σ_allow)** [est]. The allowable stresses below are
fatigue design stresses (my choice), not datasheet values:

| leaf | ±3 mm | ±6 mm | ±12 mm | 2-leaf centring force at 6 mm (b = 6) |
|---|---|---|---|---|
| Ti-6Al-4V, t 0.2 (σ 350, E 114 GPa) | 24 | 34 | 48 | 1.6 N |
| Ti-6Al-4V, t 0.3 | 30 | 42 | 59 | 3.0 N |
| β-Ti 15-3, t 0.2 (σ 500, E 95 GPa) | 19 | 26 | 37 | 3.1 N |
| spring steel 1.4310, t 0.1 (σ 450) | 20 | 28 | 39 | 0.7 N |
| POM, t 1.0 (σ 25, E 2.8 GPa) | 32 | 45 | 64 | 2.2 N |

- **In-plane flexure (leaves standing on edge, b = plate thickness).** The stage is as tall as the plate (~5-6 mm),
  but it needs a large footprint.
  - A nested XY stage needs about 2 x 2L per side. That is ~70 x 70 mm at ±6 mm and ~110 x 110 mm at ±12 mm in
    Ti 0.2.
  - **`offset-flex-aligner`'s 60 x 40 mm stage cannot give ±12 / 8 / 4 mm**: one ±12 mm Ti leaf alone is 48-59 mm long.
- **Radial flexure (leaves lying along the skin, flexing normal to it).** The stack is about 2δ + 2t + 2-3 mm of frame.
  That is **~9 mm for ±3** (30 mm leaves) and **~15 mm for ±6** (42 mm leaves).
- **A flexure is a spring, not a free DOF.** The arm drives it against 1-6 N (R17), and its fatigue life has to be
  shown (R9). It suits MVP1 as a centring element. It is not a 3rd "slide".

### 3.2 All-revolute linkages (make: plates + MR bearings or iglidur pins)

| linkage | travel | envelope | notes |
|---|---|---|---|
| Parallelogram, pins skin-normal (swings in the skin plane) | ±13 with l 40 (±19 deg) | **~6 mm tall** (one pin stack), 40 x ~14 mm | Curved path: 2.2 mm parasitic across the travel (l 30: 3.0 mm). 4 pins. |
| Parallelogram, pins parallel to skin, links near-flat (radial) | ±3 with l 20 (±8.6 deg) | **~10 mm** (2δ + ~4 mm boss), ~28 x 10 mm | 0.23 mm parasitic; ±6: ~16-17 mm tall, 0.9 mm parasitic |
| Sarrus (straight-line radial) | ±3 with 8 mm links | 8.5 mm collapsed to 14.5 mm extended, knees ±7.5 mm | 6 pins; no better than the parallelogram |
| Scissor lift | ±3 | collapses to ~6-7 mm | Needs a sliding foot (a prismatic joint anyway). Singular near flat (foot force F/tan φ): jams when pushed from collapsed. |
| **Planar RR (two pins parallel to J3)** | ±13 x ±9.2 with l1 = l2 = 20 | **~6 mm tall**, ~48 x 20 mm swept | Elbow stays 48-134 deg, at least 46 deg from fold or stretch (l 15: 76-152 deg). Same 2 in-plane DOF as two slides in J3's plane; arm twist = q3 + qa + qb. |
| Lazy tongs (planar) | large ratio | 2 bar layers + pins, ~5-6.5 mm | Many pins and stacked backlash. Only worth it for long travel. |

- **The planar RR is the all-revolute version of the 2-slide cuff.** Mobility is unchanged and the loop is still
  determinate away from fold and stretch.
- **Its costs:**
  - two more pins;
  - the arm twist is the sum of three angles, so put magnet encoders on the passive pins too, or read the twist from
    an IMU;
  - in MVP2 the RR passes J3's torque to the arm only as a force along link a, which acts on GH's lever arm. This has
    to be checked before power.
- **Its benefit:** the pins carry tilting moments in a hub-sized boss, which miniature guides cannot.

## 4. The four questions, with numbers

### (a) One translation along the arm (±13 mm in `seed-offset-3r-slides`; R10 GH/handler slip up to ~15 mm)

**THK RSR3M or HIWIN MGN03C.**
- Envelope: H 4.0 + 1.5 mm plate = **5.5 mm**; block 8 x 12; rail 3 x 2.6 x **40 mm** (12 + 26 + 2); ~3.5 g; balls.
- Lower options:
  - IKO LWLF2 / LWL1 at H 2.5, but their loads are tens of N: a knock breaks them.
  - RSR2N / MGN02C at H 3.2 and C0 ~400 N.
- Cheap plain option: igus drylin N17, H 6 and 17 mm wide. Use it only where there is no moment.
- Rated for MVP1 only. For MVP2's 25 N·m use two MGN05C rails, two blocks each, at least ~50 mm apart (one pair at
  30 mm reaches C0 at 25 N·m, a static SF of 1), or an MGN12H at H 13.
- All-revolute alternative: a parallelogram flat on the skin, l 40, ~6 mm tall, with 2.2 mm of parasitic motion across
  the arm.

### (b) Two in-plane translations at the cuff

**Two RSR3M / MGN03C stacked crosswise.**
- Height: 1.5 base + 4.0 + 1.0 adapter + 4.0 = **10.5 mm**.
- Footprint: ±13 along x ±9.2 across → **~40 x 33 mm**, ~10 g.
- The model's 4 + 0.5 + 4 + 0.5 = 9 mm stack is close to this. Its 20 x 20 blocks are larger than the real 8 x 12
  (conservative in footprint). It omits the 1.5 mm base, so add it.
- MGN05C / RSX5M stacked is **13-14.5 mm**, which uses the whole pass band by itself.
- All-revolute alternative: a **planar RR** on passive pins, **~6 mm** tall, ~48 x 20 mm swept. It is 4.5 mm lower than
  the stacked guides and handles moments better, at the cost of two more angles to sense.

### (c) Radial (skin-normal) translation

| | miniature guide standing up | near-flat parallelogram | Ti leaf pad | cuff liner compliance |
|---|---|---|---|---|
| ±3 mm | 12 + 6 = **18 mm** (RSR3M); LWLF2 ~13-15 [mem] | **~10 mm**, 28 x 10 | **~9 mm**, 30 mm leaves | 6-8 mm foam / TPU lattice [est] |
| ±6 mm | **24 mm** | **~16-17 mm** | **~15 mm**, 42 mm leaves | ≥ 12 mm liner: out of band |

- **±3 mm:** do not make a joint. Put it in the cuff liner and **state it as compliance**, which the CLAUDE.md rule
  allows. If it has to be a mechanism, use a near-flat parallelogram or a leaf pad, and accept ~9-10 mm, which is the
  whole 10 mm aim.
- **±6 mm: not buildable at the size modelled.** Every real option is 15 mm or more, before the hub or carriage that
  sits on it.

### (d) Slide + spin about one axis

**An iglidur J sleeve on a 6 mm hard-coated rod.**
- Sleeve Ø8 x 10-12 [mem part no., confirm] in an Ø11-12 boss; keep L/d ≥ 1.5. Plain bearing.
- `offset-pointer-slip-sleeve`'s Ø12 x 25 sleeve on a Ø6 rod is real and conservative.
- Rolling option: THK ST6 stroke bush, Ø12 x 19 on a hardened rod [mem].
- A ball spline does not spin.

## 5. Designs in the catalogue, against real hardware

"Translations" counts passive translations only. The rule allows at most 2.

| design | passive translations as modelled | real component | verdict |
|---|---|---|---|
| seed-offset-3r-slides (verified 66.47) | 3: ±13.0 along / ±9.2 across / ±6.7 radial; radial at 0 height | along + across: 2 x RSR3M (10.5 mm); radial: none fits (≥ 16 mm) | **Not buildable as modelled**; over the translation cap |
| skin-normal-hubs-selfaligning (unverified 35.86) | 3: brief ±18.6 / 16.4 / 6.0; doc k722 centred ±7.8 / 8.1 / 6.7 | same as above; radial ±6-6.7 does not exist in band | **Not buildable as modelled**; drop the radial slide → becomes offset-skin-normal-3r |
| offset-skin-normal-3r (screened 45.31) | 2 in hub 3's plane + 0.5 mm radial tolerance (spec ≤ 3) | 2 x RSR3M / MGN03C inverted (~10.5 mm), or planar RR (~6 mm); radial ≤ 3 → liner compliance | **Buildable for MVP1**; MVP2 needs spaced rails or the RR |
| offset-pointer-slip-sleeve (v 76.42) | 1 (rod slide) + spin + 2 U-joint pins | iglidur sleeve on a Ø6 rod; U on MR63 / MR52 pins | **Buildable as modelled** |
| floating-centre-3r (refuted) | 3 (XY float ±8 + Z) | as above | Over the cap; dead anyway |
| offset-arc-selfalign (dead) | 3 | - | Over the cap |
| offset-flex-aligner (ideated) | 3: Ti leaf stage ±12 / 8 / 4 in 60 x 40 | leaves for ±12 alone are 48-59 mm (Ti) | **Not buildable at that size**; over the cap |
| offset-axis-skin-hubs (ideated) | 3 | - | Over the cap; reduce to 2 in-plane |
| breathing-hubs | 2 radial lifts up to 15 mm (cam-set) | near-flat parallelogram lift: ~4-5 mm folded under each hub, l ≥ 30 for 15 mm | Count OK; adds ≥ 4-5 mm to each hub at rest: re-measure |
| geodesic-strap-gimbal | 2: strap through guide + radial slide | strap roller guide is real; radial slide as in (c) | Count OK; the radial slide's height must be carried |
| lone-helix-humeral | 2: along + radial on the carriage | along: RSR3M; radial: (c) | Count OK; radial travel decides it |
| acromion-pointer-arm-ctrack | 1 radial + swivel | (c) | Buildable only if radial ≤ ~3 mm |
| tape-spool-humeral | radial slide + yaw pivot + tape | (c) | Radial travel unknown: measure it |
| cuff-sleeve-3r | 2: sleeve float + one cuff slide | 2 x MR85 floating on a Ø5 rod = plain slide + spin; slide: RSR3M | Buildable |
| seed-2r-cring | 1 along-arm slide | RSR3M, or LT4X if it must carry twist torque | Buildable (dead on the bench anyway) |
| champion spherical 3R / rail-elbow | 0 on the bench; real GH / handler slip ~15 mm (R10) | 2 x RSR3M along + across under BOTTOM (~10.5 mm, ~40 x 40 mm), radial → liner | **Buildable**: this is the user's original cuff-slide plan, within the 2-translation cap |
| human-closed-telescopes, dome-telescope-tripod, base-rail-tripod | 3 telescopes or rails | - | Over the cap unless the telescopes are the actuated DOF |

## 6. What the models and the verifier must change

1. **Every slide gets a real part from `tools/hardware_catalogue.json`.**
   - Use the part's H plus a 1.5 mm plate. The rail is W_r x (L_block + 2·travel + 2) and the block is W x L. The two
     cross guides need a 1 mm adapter between them.
   - A radial slide stands up by L_block + 2·travel.
   - No zero-height ranges.
2. **The radial residual (≤ 3 mm) is liner compliance, stated as such and counted.** A design that needs more is
   rejected.
3. **At most 2 passive translations.** Prefer pins: the planar RR in place of the 2-slide stage is a new model variant
   worth a bench run (`offset-skin-normal-3r` with `stage=rr`, l 15-25).
4. **Check moments.** The stage's static moment rating must exceed the tracking moment (MVP1) and is flagged against
   25 N·m (MVP2).

## Sources

- THK RSX-M (RSX5M/7M rows, rail and load table): https://tech.thk.com/en/products/pdfs/en_a01_264.pdf
- THK RSR2N/3M/3N: https://tech.thk.com/en/products/pdfs/en_a01_268.pdf
- HIWIN MG series catalogue (tables 3.76, 3.79, 3.81):
  https://damencnc.com/userdata/file/3455-3_HIWIN_MGN_and_MGW_Product_Catalog_2023.pdf
- igus drylin N section (N17 system and carriage tables):
  https://www.igus.com/contentData/Product_Files/Download/pdf/6-4%20DryLin%20N%202016%20Section.pdf
- IKO LWLF2 (2.5 mm height, 2 mm rail, 5 mm slide, 0.21 g, 2 g / 100 mm):
  https://www.automate.org/products/iko-international-inc/iko-lwlf2-miniature-linear-guides
- IKO LWL2 (H 3.2, rail 2 x 2, C 211 N): https://www.astbearings.com/catalog/miniature_linear_way_series/LWL2
- IKO LWL3 (rail 3, C 353 N, C0 587 N): https://kr.rs-online.com/web/p/linear-guides/9175945
- IKO CRWM1-30 (4.5 mm, 17 mm, C 125 N): https://qualitybearingsonline.ca/crwm1-30
- THK LT ball spline: https://tech.thk.com/en/products/pdfs/en_a03_082.pdf; LT-X:
  https://tech.thk.com/en/products/pdfs/en_a03_086.pdf
- igus RJUM-01-08: https://uk.rs-online.com/web/p/linear-bearings/6174602
- Repo: docs/HARDWARE.md (MR117 v5 hub), docs/research/ring_and_shell_hardware.md (KAA15XL0, CRBT305A).
- To confirm [mem]: LWL1 / LWLF2 block length and loads, LWL3 / LWL5 H, iglidur JSM part numbers, THK ST / LM sizes,
  MR63 / MR85 / 6700 / KAA10XL0 dimensions, Misumi / NB equivalents.
