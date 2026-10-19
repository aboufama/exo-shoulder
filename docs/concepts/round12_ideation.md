# Round 12 ideation: judge and red team (2026-10-17 ~15:20 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275)). The real target is gap 0, and 95
(gap 13.75) at low complexity. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered, exactly 3 active DOF.

Lead to beat: slipper-nose-knuckle-3r, verified 18.49 (score 93.28; Bench(110,360) exact frozen, margin 5, O20), held out
23.45, ledger WATCH. Its gap is reach 17.50 + in-band 0.45 + contact 0.54; 95 needs +18 workspace poses at its in-band.

Nine candidates came in from three lenses: the stretched wall (lens 1: 3), the overhead cone's non-fold losses (lens 2: 3)
and the spring-free, roller-free drive (lens 3: 3). All nine have 3 active joints and 0 passive translations, and every
joint maps to a catalogue or machinable part (MR117-2RS / MR63ZZ pairs, ISO 8734 dowels, M2 ball links, wire-EDM cams).
No candidate was rejected on hardware, translations or an undetermined coordinate: every K is slaved positively or held
on a stop by a spring, as in the lead. After merges, two measured kills and one judge kill, four are picked.

## Red-team checks made by the judge

Scripts, logs and JSON: `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge12/`.
Every check runs the design's own model or the proposer's own harness, imported unchanged, and reproduces its control
first.

### 1. The efficient dyad on the lead's flank drive (slipper-effdyad): the flank does not carry it

`eff_flank.py`, `grid_3446.log`, `grid_3646.log`, `eff_parts.py`, `eff_lift.log`. The slipper-nose model
(SN_CELL=lead) on the fit bench Bench(60,160); only the parent's bk1 clamp (26-32) is widened for the probe. Control: the
lead reads fit 16.47 and dK_lim 49.8 (pressure_horn), as on file.

- **The lead's drive on any longer dyad fails at rest.** With beta / r_c / g / lift unchanged, every dyad tried (28/40,
  30/42, 32/44, 32/46, 34/46, 34/48, 36/46) reads dK_lim 0: crank pressure angle at rest 60.3-81.4 deg against the
  38.03 cap. The proposal's "the flank re-synthesises automatically on the new uK" is true of the code, not of the
  drive: the crank, nose and flank must be re-placed for each dyad.
- **Re-seated (7 beta x 4 r_c x 4 g = 112 cells per dyad):** 9 cells at 34/46 and 7 at 36/46 open K >= 40 deg, and
  2 / 3 reach >= 46 (best 49.2 at beta -175, r_c 17.5, g 2.6). The kinematics do improve: fold losses on the fit bench
  fall from 31 to 24-28. **But every stroking cell has metal in the skin on 84-104 fit poses** (contact fraction
  0.48-0.59). Per part, at the best cell: horn lug under the skin on 79 taken poses (to -6.82 mm), crank on 28 (to
  -7.49 mm). With hub K moved ~10 mm medially, the lug (on the far side of hub K from hub 2) lands over the
  supraspinatus / trapezius ridge.
- **Lifting the lug does not save it:** lift 3 / 6 / 8 mm (lift_max 8, hl 3.15) clears the horn (+1.05-2.02 mm) but
  the flank re-synthesis then reads dK_lim 0 again, and the crank stays 7.9-8.9 mm deep on 12-22 poses.
- **History agrees:** roller-longdyad's co-fit (7236 configs) measured bk2 44 at 21.82 and bk2 46 as "drive idle"
  against 15.09 free, and every free stream walked to 26 / 38. The proposer read that as fit-bench blindness; the probe
  above is metal, not blindness.

Verdict: not picked. The efficient-dyad lever is real for the K window, but the flank family's output sits on link 1a
more than ~17 mm from K's axis, which roller-longdyad's own finding predicts meets the skin.

### 2. The efficient dyad on the in-band RSSR (spiral-lobe): the drive metal and the chain both bind

`ib_long.py`, `ib_long.log`, `ib_long_ghost.log`, `fz_*_ghost.json`. The real inband-rssr model (loaded unchanged) with
pick3's drive placement (eta, beta, gam, zc, clay 1, bl_c 2) and the candidate's dyad and gain: 34/48, a1max 76.5,
linear kK 2.8 (the base-PA-42 limit at g = La / r_h = 24 / 15.25), r_lobe 8.0, s_arm 4.0, smhi 19.46. The spiral law
is not in the model yet; the linear law at its base-PA limit closes 286 in the proposer's own harness (spiral 287).

Fit bench Bench(60,160):

| cell | fit gap | fold | knee slide | skin (chain) | contact (drive) | parts under the skin (taken poses, deepest) |
|---|---|---|---|---|---|---|
| pick3 control | 16.99 | 29 | 6 | 1 | 0 | L2 1 (-1.66) |
| 34/48 kK 2.8 | 131.56 | **19** | 7 | 9 | **18** | horn 13 (-4.97), rod ends 15 (-6.90), rod 6, crank 4, ear 3, hub 2 6 (-9.88), L2 6 (-15.29), L1b 3 |
| pick3, drive ghosted | 15.82 | 29 | 6 | 1 | 0 | L2 1 |
| 34/48, drive ghosted | 24.70 | 19 | 7 | **7** | 0 | hub 2 6 (-9.88), L2 6 (-15.29), L1b 3 (-0.86) |
| 34/48 smhi 14, ghosted | 20.68 | 23 | 7 | 3 | 0 | hub 2 1 (-3.22), L2 2 (-6.0) |

(The 34/48 row with its drive also fails clip follow overhead, 0.6, which is most of its 131.56.)

- The +10 closed fit poses are real (fold 29 -> 19), as the harness says.
- **Even with every drive part deleted, 7 of the 10 put hub 2 or link 2 into the skin** (hub 2 to -9.9 mm, link 2 to
  -15.3 mm). The proposer's gate-A parking (hub / link discs at the clip-frame level + 4 mm) cleared 19 of 26; the model,
  with its own fitted levels, clears about a third of them on the fit bench.
- With pick3's drive placement unrefit, horn, rod ends, rod and crank add 18 contact poses. That is the long-dyad report
  row's pattern (bench 20.44, 9 held-out contacts) and the longstroke ghost's (+10 law-only -> +5 taken, +5 contacts).

### 2b. The same, frozen exact Bench(110,360) with every drive part deleted (`fz_p3_ghost.json`, `fz_l48_ghost.json`)

The model's own frozen protocol (fit Bench(60,160), wear Bench(110,360) exact), IB_GHOST=all, so this is the chain's
ceiling before any drive metal is added:

| cell | frozen gap | reach (taken) | fold | slide | contact poses (depth summed / max) | contact by part | ib14 |
|---|---|---|---|---|---|---|---|
| pick3, drive ghosted | 18.32 | 0.7222 (260) | 88 | 10 | 2 (8.6 / 5.8 mm) | | 0.903 |
| 34/48 kK 2.8 smhi 19.46, drive ghosted | **18.84** | 0.7472 (269) | **64** | 13 | **14 (72.7 / 15.3 mm)** | hub 2 on 10, link 2 on 6, pad 2, hub K 2 | 0.901 |

- The kinematic gain is real and large on the claim bench: **24 fold poses** close (88 -> 64), taken th up to 120.5,
  K up to 65.4.
- They split **9 taken, 12 contacts, 3 knee slides**: the longstroke ghost's split again (+10 law-only -> +5 taken, +5
  contacts). With no drive metal at all the seed is 0.5 worse than pick3's ghost and 0.35 worse than the lead.
- **The binder past stage 1 is hub 2** (10 of 14 contact poses, up to 15 mm deep), then link 2: when K opens,
  link 1b swings hub 2 away from J1 and into the bunched deltoid, the recurring limiter. Lateral relief of drive parts
  (lens 1's lever) does not touch it; hub 2's level is fixed by the clip frames (F2 +4 mm takes 26 % of them out of
  band).
- So pick 1's new gate 0 is this ghost with a per-pose trade: choose the gain, onset and stop B so that the hub-2 / link-2
  contact poses become plain fold losses while the 9 takes stay (and the knee column takes the 3 slides). If the best
  ghost cell cannot reach <= 17.5 with <= 4 contact poses, no drive can save it.

### 3. The V-rocker's window estimate vs a law-only count

`vrocker_law.py`, `vrocker_law.log`. The lens-1 proposer's `lawprobe.py` harness (control: the lead 263 bench / 250
envsel, as on file), the lead's seats, a linear law kK 2.5 past the onset, K capped at the conjugate-lobe stroke, stop B
at bk1 + bk2 - 5.5.

| dyad | onset smhi | K cap 56 | K cap 60 | K cap 64 | envsel (cap 56 / 60 / 64) | knee fails |
|---|---|---|---|---|---|---|
| lead 26/38 (lin 2.15) | 16.84 | 263 (stroke 45.6) | | | 250 | 9 |
| 28/50 | 16.84 | 267 | 270 | 272 | 253 / 257 / 258 | 12-13 |
| 28/50 | 19.46 | 260 | 263 | 265 | 257 / 261 / 262 | 12-13 |
| 30/49 | 16.84 | 275 | 277 | 278 | 273 / 276 / 276 | 12-13 |
| 32/48 | 16.84 | 278 | 280 | 281 | 277 / 278 / 278 | 13 |
| 32/48 | 19.46 | 279 | 281 | 282 | 276 / 277 / 278 | 12-13 |

- The proposal's 283-291 is the K WINDOW interpolated, not the law. The law closes 278-282 at 32/48 (1-9 below the
  claim) and 260-272 at 28/50 (11-24 below): **28/50 is dead**, 32/48 is the cell.
- The robust conjugate cell (cap 56, 88 lobe pairs) reads 278 / 276; the knife-edge 64-deg cell (3 pairs at PA 37.9
  against 38.03) buys only +3 / +1.
- The knee fails rise from 9 to 12-13 on every long dyad: the knee is the second wall (conecut-longdyad's point).

### 4. The pinned horn's stroke, re-implemented, and carried to the long dyads

`inv_long.py`, `inv_long.log`. The proposer's `dsk/invslot.py` inv() re-written on the geometry read from the slipper
model built at each dyad (u2, uK, the crank axis dR by the parent's rule, fK, hl, lift).

- **Reproduced:** 76.75 deg at the lead's C0, g 2.39, 26/38 (mu 0.087: PA cap 38.03). The best over g 1.8-3.2,
  beta -230..-110, r_c 13-22 is 78.75 (g 2.0, r_c 21).
- **On long dyads the inversion still strokes**, but not at the lead's drive point (PA 78-82 at rest, dK 0 at 32/48,
  34/46 and 28/50). Re-seated: 32/48 78.5 (g 2.3, r_c 21.5), 34/46 78.25 (g 2.3, r_c 21), 28/50 78.5 (g 2.5, r_c 20.5);
  with the nose near the lead's r_c 14-16 the gain must rise to g 2.9-3.2 (75.5-77). The crank's reach dR -> uK grows
  from 23.3 deg to 31-35 deg.
- So stage 2 is not the V-rocker's binder. Its metal on a medial hub K is (section 1: the flank's lug at r_c 17.5 sat in
  the skin on 79 fit poses).

### 5. Complexity (tools/simplicity.py v2.2 --score on the lead's record convention)

| record | complexity |
|---|---|
| lead slipper-nose (row record today) | 18.25 |
| desmo-slipper as specified (sliding 2, rolling 0, springs 0, catalogue 13) | **15.75** |
| inband-rssr pick3 (row record today; its note still says 28.5 from before the knee-loop rule) | 24.5 |
| desmo-spiral-rssr (pick3 minus spring, roller -> groove pair, -1 bought part) | 22.25 |
| desmo-vrocker as specified (bodies 7, joints 9, loops 3, sliding 2) | 19.0 (17.0 with desmo-slipper's 5 bodies) |
| desmo-vrocker strict (the conjugate pair as 2 pairs + 1 loop) | 25.0 |

The records disagree on whether the knee's two bodies sit in moving_bodies (desmo-slipper's own note). Each modeller
writes the full record and scores it with the tool against the lead's record, like for like.

### 6. conecut-knee's measured numbers, read from its own logs

`cone/log_full_leadctl.txt` reproduces the lead exactly (18.49; fold 88, slide 9, contact 2). `cone/log_full_kw25stop.txt`:
18.36, fold 88, **j3stop 8**, contact 3 (237, 264 and the new 316: link 2 at -1.24 mm), reach 261 unchanged, ib14
0.8955 -> 0.8994. Held out 22.79 vs 23.45, j3stop 21, **14 contacts (64.6 mm summed) vs 10 (46.35 mm)**.

- No pose is newly taken. The 9 knee slides become 8 stops + 1 contact. The whole bench gain is the in-band of the
  longer E strap (+0.0039 = 0.39) less one contact (0.27): -0.13, a tie.
- The held-out gain (-0.66) comes with +4 contacts and T5 +18 mm: the auditor's T5 reason gets worse.
- Its real value is robustness (knee d-margin 0.33 -> 6.8 mm; robust to a 3 mm GH-centre error) and stacking: every
  long dyad above adds 3-6 knee fails (section 3) that this knee re-opens.
- The J3 stop acts on J3's own angle (a tab on link 2's hub-3 root against the E strap root: the two bodies J3
  connects), so it is a legal hard stop; it limits the wearer's internal rotation at those 8 / 21 poses, as the K and
  knee stops already do. Report what the wearer feels there (stop torque at the cuff).

### 7. conecut-seatswing (closed form)

At wd 78.87 the proposer's own a2 is 48.4 (lead 57.2). The stretched wall's top is a1e_max + a2 - 5: with the lead's
stroke (a1e 55.5) it falls from 106.6 to ~98.9 unless K strokes ~9 deg further, which the lead's flank cannot (49.8 cap)
and section 1 shows a longer flank cannot carry on a re-seated hub K either. The proposer's frozen check already reads
fit 99.2 and fold 122 with the lead's law; its best case (-1.1) is under the 1-point rule and seat re-fits are a closed
class for fit-bench selection.

## Verdicts, all nine

| # | candidate | verdict | reason |
|---|---|---|---|
| 1 | spiral-lobe-longdyad-knuckle-3r | **PICK 1** | The only candidate with the kinematic room for 95 (law-only 287 / 360; frozen ghost: 24 fold poses closed). Its ceiling (13.3) leaves out what binds in the real model (sections 2, 2b): hub 2 and link 2 at the K-open poses (ghost 18.84: +9 taken, +12 contacts) and the drive metal. Re-gated: the ghost trade first. |
| 2 | slipper-effdyad-knuckle-3r | not picked: judge-measured | The lead's flank re-placed on 34/46 / 36/46 strokes (<= 49.2) only where the horn lug sits in the skin on 79+ fit poses; lifting kills the stroke (section 1). |
| 3 | desmo-spiral-rssr-knuckle-3r | **merged into 1** (cell C) | The same chain, dyad and RSSR with the stage-1 lobe cut as a two-walled groove and the spring deleted. Law-only 280 / 281 (envsel 277-279), cx 22.25 vs 24.5. It is pick 1's answer to the reflected spring torque (0.42 N.m at the crest, 56-70 % of R17's 5 N) and to M5. |
| 4 | conecut-knee-knuckle-3r | **PICK 3** | Measured: 18.36 / 22.79 vs 18.49 / 23.45 (section 6). A tie on the bench and no pose taken, but the only knee that stays inside its window under a 3 mm GH error, and the column every long dyad needs. |
| 5 | conecut-longdyad-knuckle-3r | **merged into 1** (knee + J3-stop column) | Not a separate morphology: pick 3's knee worn on lens 1's cell. Its finding (10 of 37 stretched poses at th <= 130 fail the lead's knee) is a red-team correction to pick 1's estimate. |
| 6 | conecut-seatswing-knuckle-3r | not picked | Self-declared likely kill; a2 48.4 lowers the stretched wall by ~8 deg at the lead's stroke (section 7); best case under the 1-point rule; a closed class. Its rim table (wd +12 lifts hub 2's rim 2.4-9.7 mm on the cone poses) is recorded for the J3-seat lever. |
| 7 | desmo-slipper-knuckle-3r | **PICK 2** | The complexity lens's target, at the lead's stroke: cx 15.75 vs 18.25 (tool), spring-free (M5 gone), positive both ways. Standalone synthesis reproduces the model's cam tables and groove-desmo's verifier. |
| 8 | pinned-horn-desmo-knuckle-3r | **merged into 7** (cell B) | Same chain, stage 1, law and complexity; only the stage-2 higher pair is inverted. Its stroke (76.75, reproduced by the judge) is not used on the lead's dyad; its metal change (lug band deleted, slotted crank plate) is a column. |
| 9 | desmo-vrocker-longdyad-knuckle-3r | **PICK 4** | Reach at low complexity (cx ~17-19, no spring, roller, rod or ball link). Law-only 278-282 at 32/48 (judge; 28/50 dead), stage 2 strokes on the long dyad (section 4). Lowest confidence: conjugate lobes at PA 34.7-37.9 of 38.03, two stacked tracks unpacked, metal on a medial hub K unmeasured. |

## Ranking (expected gap reduction vs the lead x confidence x buildability)

All picks have 3 active joints and 0 passive translations, so buildability ties on translations and is decided by the
parts.

| rank | id | judge's expected frozen gap | confidence | complexity (tool, lead convention) | lead note |
|---|---|---|---|---|---|
| 1 | spiral-lobe-longdyad-knuckle-3r | 17-19.5 (the ghost seed is 18.84 with no drive metal; < 16.5 only if gate 0 sheds the hub-2 contact poses and keeps the takes) | low | 24.5 (cell C 22.25) | ghost trade first (gate 0 <= 17.5, <= 4 contact poses) |
| 2 | desmo-slipper-knuckle-3r | 18.3-19.5 (a paired tie is the target) | medium | **15.75** (lead 18.25) | stage-1 groove band to 46.3 |
| 3 | conecut-knee-knuckle-3r | 18.36 measured (two-sided stop est. ~18.1); held 22.79 | high (measured) | 18.25 | T5 held +18 mm |
| 4 | desmo-vrocker-longdyad-knuckle-3r | 16-20 at 32/48 if the lobes pack and the nose metal clears; dead at 28/50 | low | 19.0 (17.0) / 25.0 strict | 3-D lobe packing + nose metal |

The 95 arithmetic is unchanged: +18 workspace poses at the lead's in-band and contact. Picks 1 and 4 have the kinematic
room (+16-25 law-only; 24 fold poses closed frozen exact), and the judge's model checks say that room is spent by chain
metal (hub 2 on 10 of 14 contact poses, link 2 on 6) on the K-open poses before any drive is placed. Pick 1 ranks first
on the user's standing priority (reach) and because its gate 0 is a ~10-minute local run that also decides pick 4. Pick 2
is the complexity objective at the lead's reach; pick 3 is a measured tie that every reach pick should wear. By the
product alone, picks 1-3 are close (pick 1: ~0.5-1.5 points at low confidence; pick 3: 0.13 measured at high confidence;
pick 2: 0 points but -2.5 complexity).

## Notes for the modellers

- **Pick 1 (spiral-lobe):**
  - Gate 0 (new, ~10 min per cell, local): the model's ghost wear (IB_GHOST=all, CB_EXACT=1, frozen) of the seed
    against pick3's ghost (18.32). The judge's seed reads 18.84 (section 2b). Write the per-pose table of the newly
    closed poses (K, th, taken / contact / slide, part), then pick the gain, onset and stop B that turn the hub-2 /
    link-2 contact poses into plain fold losses and keep the takes; wear the conecut knee. Pass: <= 17.5 with <= 4
    contact poses. Only then gate A, with the real stage 1 + RSSR and every drive part sampled.
  - The chain binders are hub 2 and link 2 on the K-open poses. Lens 1's lateral relief does not touch them; re-placing
    hub 2's level or a2 is closed. So the search must keep the onset / gain where those poses are not opened (smhi 14
    halves them on the fit bench) and buy the stretched poses where hub 2 clears: report the trade per pose.
  - Reproduce the judge's two ghost runs first: `IB_GHOST=all CB_EXACT=1 python3
    docs/concepts/models/inband-rssr-knuckle-3r.py frozen "$(cat <params>)" out.json`, with <params> =
    `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge12/p3.json` (pick3) and
    `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge12/l48.json` (the seed).
  - Cells: A spiral 34/48 La 24; B 36/48; C (desmo-spiral-rssr) groove spiral, no spring. Column: pick 3's knee and
    J3 stop (conecut-longdyad), the knee as the second wall (12-15 fails on the long dyads vs 9).
  - Report the spring's reflected J2 torque at the crest (cells A / B) and the R17 margin.
- **Pick 2 (desmo-slipper):** gate drive-only first (both stages to dK >= 46.3 at mu 0.087, slop <= 0.25 deg, groove
  outer wall <= 11.5, law-only >= 272). Cell A: swept slot in link 1a around the crank's nose. Cell B (pinned-horn):
  nose on link 1a, slot in the crank tip; report the contact split at poses 237 / 264 and the 71 lug-lowest poses.
  Pre-register A or B on envsel. The swept-envelope slot sits at the relative pole over K 0-8 (the nose moves 0.18 mm
  in link 1a's frame): measure the slop and the jam check in the MODEL, crank held and crank free, both directions,
  including the reversal at the dwell exit.
- **Pick 3 (conecut-knee):** verify the measured columns (one-sided -105; two-sided -105 / +119.5); report T5 bench and
  held per pose, the paired CI vs the lead, the GH-offset liner share at 3 / 5 mm, and the stop torque the wearer feels at
  the 8 / 21 stopped poses. It stacks on picks 1 and 4 as their knee column.
- **Pick 4 (desmo-vrocker):** 32/48 only (28/50 is dead: 260-272). Gate in order: the conjugate pair to 56 deg with both
  tracks packed under hub 2's cap ring (3-D track-vs-pin check), the inverted stage 2 re-seated on 32/48 (judge: 78.5 at
  g 2.3 / r_c 21.5, or 75.5-77 at g 2.9-3.2 / r_c 14-16) with the nose boss and slotted plate sampled, then the ghost
  wear as pick 1's gate 0 (the chain is the same: if pick 1's gate 0 fails on 34/48 and 36/48, re-run it once on
  32/48 at kK 2.5 / caps 56-64; a fail there kills this row too), then law + metal >= 274 taken.

## Recorded, not catalogued

- The efficient-dyad finding stands as kinematics: dA/dK = sin bk1 sin bk2 sin psi / sin A at rest is 0.421 (26/38),
  0.556 (34/46), 0.581 (36/46); the law-only gain on a fixed stroke is real (section 3, run10 / run14 in the proposer's
  scratch). What kills it is where a medial hub K puts the link-1a output (section 1).
- The pinned-horn inversion (section 4) gives a PA-legal 75-78 deg stage 2 at the cost of one sliding pair, on every
  dyad tried. It is the lowest-complexity stage 2 on file for any long-stroke K drive.
