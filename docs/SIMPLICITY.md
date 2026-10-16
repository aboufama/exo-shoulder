# Complexity count (the "simplicity number"): lower = simpler

User, 2026-10-16: "it would be cool to have a simplicity score for each design impacted by degrees of freedom moving
parts, etc. I think thats a pretty major part and for now shouldn't impact overall score but should show in the
chart", and a minute later: "when score start capping out around 95+ over the night, prioritize lowering that
simplicity number".

So the number goes **down** as a design gets simpler:
- **0** is the simplest buildable 3-DOF exo: three revolute hubs (pins on bearing pairs), three moving links, no passive
  freedom, nothing to measure beyond the three hubs.
- Everything a design has beyond that **adds** explicit points. There is no cap.
- It is **not** part of the bench score or the gap. The dashboard shows it next to the score.
- CLAUDE.md makes it the second objective. Once verified scores plateau at 95 or more (gap 13.75 or less), the search
  minimises complexity subject to score >= 95.

Code: `tools/simplicity.py`. Run `python3 tools/simplicity.py` for the table, `--examples` for the item-by-item worked
examples below, `--json` for the dashboard, and `--check` for the self-test. Input: the `"mechanism"` record in each
`docs/concepts/rows/<id>.json` (schema in section 4). Version 1, 2026-10-16.

## 1. Method: four instruments, one points count

| instrument | what it contributes here |
|---|---|
| **Grübler-Kutzbach mobility** (spatial: M = 6(n - 1 - j) + Σf) | Counts loops and freedoms. It checks each record: loops = joints - moving bodies, and M with the wearer's shoulder as a ball joint. It also reports how many constraints the body must absorb (section 5). |
| **Boothroyd-Dewhurst design for assembly** (Boothroyd, Dewhurst & Knight, *Product Design for Manufacture and Assembly*, 3rd ed., 2011) | A part is essential only if it moves relative to the others, must be a different material, or must come apart for assembly or service. Every other part is a candidate for elimination, and each one costs handling and insertion time (DFA index = 3 x N_min / total assembly time). So: points for bodies, joints and parts beyond the theoretical minimum of the 3-DOF chain. |
| **Pahl & Beitz basic rules** (*Engineering Design*, 3rd ed., 2007: clarity, simplicity, safety) | Simplicity means few parts and simple shapes and motions. Clarity means one unambiguous relation between input and function. A passive coordinate that must be **measured** to know the arm's pose breaks clarity, so it scores more than a passive coordinate that the closure sets and nobody reads. |
| **The user's manufacturable-joint rule** (CLAUDE.md) | Rotations are cheap. One slider is cheap. Two crossed rails are bulky. Three translations never. Prefer 0 passive translations, then 1. |

Jarrassé & Morel ("Connecting a human limb to an exoskeleton", IEEE T-RO 28(3), 2012) explain the redundancy that
section 5 reports: a chain fixed to a limb is isostatic only when it carries n + p = 6 freedoms per loop.

## 2. The items and the weights

Each item adds its points once per count. The total is the sum.

| item | points | why this weight |
|---|---|---|
| active DOF beyond 3 | **25** each | MVP2 adds a motor, a cable run and an encoder. MVP1 adds a spare freedom that falls under its own weight (R17). The user: "the minimum possible solution is 3 dof", push for 3 before settling for 4. Set so that any 4-active-DOF chain (4R: 28.5) scores above the heaviest legal 3-DOF design, offset-skin-normal-3r with 2 crossed rails (25.75). |
| passive translation | **5** each | A guide is a rail, a block and end stops. It stands H + plate tall (5.5 mm for an RSR3M), its rail is longer than its stroke (12 + 2 x travel + 2 mm), and it is moment-limited (0.29 N·m for one block). The user ranks 0, then 1, then 2. |
| crossed rails (2 translations stacked) | **+5** | An adapter plus a second guide riding on the first: a 10.5-11.5 mm stack, a squareness tolerance, and the tilting moment carried through two blocks in series. The user: "bulky, must be shown to fit". |
| passive translation beyond 2 | **+20** each, and flagged **NOT BUILDABLE** | No compact component exists. A radial guide stands 25 mm tall (`docs/research/manufacturability_audit.md`). CLAUDE.md: never. |
| passive rotation | **2** each | A pin on a bearing pair is a cheap, sealed catalogue cartridge. It is still one more coordinate that must be determined (R17), one more keep-out, and one more source of play. |
| sensed passive coordinate | **5** each | An encoder without a motor: a magnet, an IC, a harness and a calibration. By the user's own DOF definition (REQUIREMENTS.md, 2026-10-15: a joint "position measured for all function to happen" counts), a sensed passive joint is half-way to an active DOF, so it scores half of one active DOF. |
| closed loop inside the mechanism | **4** each | Each loop is a closure tolerance chain: axes must meet or link lengths must match, or the loop binds. It needs fit-up at assembly and brings a branch or singularity to avoid. The one loop every exo closes through the wearer's shoulder is not counted. |
| moving body beyond 3 | **1** each | Boothroyd-Dewhurst: a body that moves is an essential part, but it is still one more swept volume to keep clear (R2, R6) and more mass. |
| joint beyond 3 | **1** each | Each pair adds play, friction and a keep-out. |
| track (sliding) pair | **2** each | A rail, carriage, arc track, sleeve on a rod or slot needs a track longer than its stroke, end stops, preload or play adjustment, and dirt protection. Stick-slip affects R17. A revolute runs in a sealed bearing, whether rolling or a plain iglidur bushing, and is the 0-point reference. |
| spring or flexure | **3** each | It needs a fatigue proof (R9), a centring force that the wearer feels (R17), and it brings hysteresis. |
| made part beyond the anchor's 7 | **0.5** each | A drawing, a machining set-up and a tolerance chain. |
| bought part beyond the anchor's 6 | **0.25** each | Handling and insertion (Boothroyd-Dewhurst). Fasteners and sensing parts are not counted (section 3). |

The structural weights (DOF, translations, rotations, sensing, loops) are an order of magnitude above the part
weights, which are estimates. Part counts move a total by a point or two. They can never outweigh a freedom.

**How robust the ranking is.** Each of the 13 weights was halved, then doubled, one at a time, over the 21 designs
that had a count on 2026-10-16. There are 210 design pairs.
- At most 8 of the 210 pairs swap order. The worst case is the passive-translation weight doubled.
- The anchor is 0 in every case.
- The 4R stays above the pin knee in every case except active x 0.5.
- The 4R falls below
  offset-skin-normal-3r when a stage weight is doubled (translations, crossed rails or track pairs x 2).
- The one close call is **pin knee against offset-skin-normal-3r** (21.5 against 25.75). It flips if sensing is
  weighted x 2, if translations are weighted x 0.5, or if rotations are weighted x 2 (a near-tie). The trade is real:
  two sensed pins against two crossed guides.

## 3. Scope and counting rules

- **What is counted:** everything from the scapula base (on the user's handler) to the arm-side end (the part fixed to
  the cuff or BOTTOM, merged with it or not).
- **What is not counted:** the user's own parts, which are the scapula handler, BOTTOM, MIDDLE, TOP and the forearm
  cuff.
- **The user's self-aligning cuff slides are not counted.** REQUIREMENTS.md puts them outside the DOF count, and every
  design needs some allowance for the shoulder's real translation (R10, about 15 mm).
  - A slide that the design's **own closure** needs is counted, because the design does not close without it even at a
    fixed shoulder centre. offset-skin-normal-3r's two slides are an example.
  - This is the caveat on the anchor's 0. If the user fits two crossed cuff slides under a spherical 3R's BOTTOM,
    that 3R carries 2 x 5 + 5 + 2 x 2 + 2 + 2 + parts, about 25 points. That is level with offset-skin-normal-3r, whose
    two slides do both jobs. The census record of baseline-3r says so.
- **moving_bodies:** rigid bodies that move relative to the base. Count the arm-side end once.
- **joints:** kinematic pairs, passive ones included. A U-joint is either one joint (its cross is not a body) or two
  pins (its cross is a body). Pick one, and loops = joints - bodies still holds. A trunnion pair on one axis is one joint.
- **sensed_passive** applies to a passive coordinate that enters the arm's orientation and is not fixed by the active
  angles through a loop inside the mechanism. Sensing must also hold when the shoulder centre translates (R10).
  - Slides that change no orientation: 0. Example: offset-skin-normal-3r.
  - Pins parallel to J3, whose angles add to the twist: 2. Example: the pin knee.
  - Spherical parallel and five-bar loops: 0, because their passive pins follow from the active angles.
  - A U-joint whose angles drift with shoulder translation: 2. Example: offset-pointer-slip-sleeve.
- **Part recipe**, used when a record leaves the counts out. Fasteners and sensing parts are left out.

  | | made parts | bought parts |
  |---|---|---|
  | base | 1 | - |
  | each moving body | 1 | - |
  | each revolute | 1 (shaft or pin) | 2 (bearing pair) |
  | each track pair | 1 (adapter or end stop) | 2 (rail + block) |
  | each other pair (rod end, ball stud, miniature U-joint) | - | 1 |

  The anchor comes out at 7 made and 6 bought, the census count of the champion (`rows/baseline-3r.json`).
  - The user-style L2 CAD carries a cap and a ring nut per hub (10 made), and thrust washers and a sleeve per hub
    (9 bought).
  - A design built in the same style carries the same per-hub overhead, so counting at the L1 level loses nothing.

## 4. The record (`docs/concepts/rows/<id>.json` -> `"mechanism"`)

`{active_dof, passive_trans, crossed_rails, passive_rot, moving_bodies, joints, closed_loops, sliding_pairs,
rolling_pairs, sensed_passive, springs_or_flexures, custom_parts, catalogue_parts, notes, source, confidence}`

- `source` names the file and lines the count came from.
- `confidence` is "counted" (from the model) or "estimated" (from the doc).
- The tool flags these inconsistencies:
  - loops != joints - bodies;
  - Kutzbach M > 3 with no spring (a spare freedom, R17);
  - crossed rails with fewer than 2 translations;
  - more pairs typed than joints;
  - fewer than 3 active DOF.

## 5. Reported, not scored: Kutzbach mobility and redundant constraints

M = (active + passive_trans + passive_rot) + 3 - 6 (closed_loops + 1). The wearer's shoulder counts as a ball joint
and the arm-side end as fixed to the cuff. The arm has 3 DOF, so:
- 3 - M is the number of constraint directions that must be taken by axis concurrency, the cuff liner or the user's
  cuff slides;
- M > 3 means a spare freedom.

| design | M | redundant | meaning |
|---|---|---|---|
| spherical 3R (anchor) | 0 | 3 | All three shoulder translations go to the cuff and the liner. This is what the R10 judge measures. |
| offset-skin-normal-3r, pin knee | 2 | 1 | The radial direction. The 2-slide closure theorem makes it exact; on a body the liner takes it. |
| closure-set-arc-knee-3r, knuckle cufflink, slip sleeve | 3 | 0 | Isostatic (Jarrassé & Morel n + p = 6). Paid for in sensed coordinates. |
| spherical parallel or five-bar loops | < 0 | > 3 | Spherical loops are overconstrained in space and are made exact by concurrent axes (a machining tolerance). |

This is not scored, for two reasons. The anchor itself is the most redundant chain, and the redundancy is a fit and
comfort question that R2, R10 and R17 already measure. Scoring it would count the bench twice.

## 6. Worked examples

Run `python3 tools/simplicity.py --examples`. Counts are census records unless marked "doc count".

**Champion spherical 3R** (`baseline-3r`, census record), **0 points**. 3 active O20 hubs (MR117 pairs), 3 moving
bodies (link 1, link 2, arm-end neck on BOTTOM), 3 joints, no loop, 7 made and 6 bought parts. Every item is at the
anchor. Kutzbach M 0, so 3 redundant constraints are left to the cuff (section 3 caveat).

**offset-skin-normal-3r** (census record), **25.75 points**. 3 active hubs, then two passive miniature guides crossed
in hub 3's plane (2 x RSR3M / MGN03C, inverted).

| points | item |
|---|---|
| 10 | 2 passive translations x 5 |
| 5 | crossed rails |
| 2 | 2 bodies beyond 3 (member 4 = along carriage + rail; member 5 = arm-fixed block) |
| 2 | 2 joints beyond 3 |
| 4 | 2 track pairs x 2 |
| 1.5 | 3 made parts beyond 7 |
| 1.25 | 5 bought parts beyond 6 (3 blocks incl. a double block for the moment, 2 rails) |

Nothing is sensed, because the slides change no orientation. M 2, redundant 1 (radial).

**skin-normal-3r-pin-knee** (doc count, `docs/concepts/models/skin-normal-3r-pin-knee.py:1-21`), **21.5 points**.
The same chain, with the slides replaced by a flat two-pin knee parallel to J3.

| points | item |
|---|---|
| 4 | 2 passive rotations x 2 |
| 10 | 2 sensed pins x 5 (the twist is q3 + qa + qb) |
| 2 | 2 bodies beyond 3 (knee link, arm pad) |
| 2 | 2 joints beyond 3 |
| 2 | 4 made parts beyond 7 |
| 1.5 | 6 bought parts beyond 6 (2 iglidur sleeves + 4 washers) |

It is 4.25 points simpler than the crossed rails. The translations and track pairs are gone, but most of the saving is
paid back in sensing. If an IMU on the cuff replaced the two pin encoders, the record would carry 0 sensed and the
pin knee would drop to about 11.5.

**closure-set-arc-knee-3r** (doc count, `docs/concepts/models/closure-set-arc-knee-3r.py:1-25`), **33 points**.

| points | item |
|---|---|
| 6 | 3 passive rotations x 2 (trunnion K and pins a, b) |
| 15 | 3 sensed x 5 (psi tilts J3's axis, so it enters the orientation; the pins add to the twist) |
| 3 | 3 bodies beyond 3 (yoke, cuff link, pad) |
| 3 | 3 joints beyond 3 |
| 3.5 | 7 made parts beyond 7 |
| 2.5 | 10 bought parts beyond 6 |

It is isostatic (M 3) and has no translation, and it is still the most complex of the four: every closure-set
coordinate has to be read.

**Calibration rows** (doc counts, in `EXAMPLES`):

| design | points | breakdown |
|---|---|---|
| 4R (anchor + a 4th active hub) | 28.5 | 25 + 1 + 1 + 1 + 0.5 |
| seed-spm-3rrr (spherical parallel 3-RRR) | 38 | 6 rotations 12, 2 loops 8, 4 bodies, 6 joints, recipe parts 8 |
| a 3-translation cuff stage | 56.5 | 3 x 5 + 5 crossed + 20 over the cap + bodies, joints, tracks and parts; flagged NOT BUILDABLE |

## 7. What lowers the number (levers for the minimise-complexity phase)

The search should take these only while the verified score stays at 95 or more.

| lever | saving |
|---|---|
| remove a sensed passive pin and its link | about 10 (2 + 5 + 1 + 1 + parts) |
| read the twist with one cuff IMU instead of N pin encoders | 5 per pin. This is a sensing change and must be judged against R10 drift. |
| replace two crossed slides with one slide | about 14 (5 + 5 crossed + 1 body + 1 joint + 2 track) plus parts |
| remove a slide entirely (exact closure without it, or the liner takes at most 3 mm) | 5 + 2 + 1 + 1 + parts |
| merge a body into its neighbour (no relative motion) | 1 + 0.5 |
| remove an internal loop | 4 + its joints and bodies |

A 4th active DOF is never a simplification: 25 points.
