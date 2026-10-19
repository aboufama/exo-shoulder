# Round 104 (J4, track jump) ideation: judge and red team (2026-10-18 ~05:15 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). The real target is gap 0, and 95 (gap 13.75) at
low complexity. The plan is docs/concepts/ROUNDS.md "Round 104 plan" (commit 2616ae1).

Lead to beat: conecut-knee-knuckle-3r, verified 18.28 (score 93.35) frozen exact Bench(110,360), held 22.38. Reach 0.7278
(262/360), ib14 0.9012, contact 0.0106 (4 poses), complexity 18.5, ledger WATCH. **Every claim's bar is 18.28.** The
verify template still defaults to 68.93 / 75.94 / 30.35 (tools/workflows/exo-screen.js line 24), so each verifier states
18.28 by hand.

Nine candidates came in:

- lens A (guide-price-close): 3;
- lens B (second-wall-route): 3;
- lens C (low-cx-same-reach): 3.

All map their joints to real parts, and all have 0 or 1 passive translation. After the determinacy rule, the
duplicate / merge check, the hardware rules and the red team, **four are picked** (section 4). Two lens-B ideas are
merged into the lens-B instrument as conditional cells. The lens-A price control becomes step 0 of the lens-A
survivor. Two candidates are rejected.

Judge's data: every number below comes from a saved file.

- Proposers' outputs: `/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/lensa/`
  (`ring2_out.json`, `nok_out.json`, `nok_metal_out.json`, `kin_out.json`) and `.../scratchpad/r104/`
  (`k33_full.json`, `kscan3_c_k33_fit60_bench_params.json`).
- The lead's per-pose dump: `docs/alignment/remeasure/conecut-knee-knuckle-3r_bench_perpose.json`.
- The lead family's lost-pose file: `docs/research/fold_ceiling/lost_poses_roller-longdyad-knuckle-3r.json`.
- The gen-9 CAD scan: `pipeline/full-exo/designs/user_desmo_conecut/stage1_level_scan.json` + `VERIFY.md`.

No bench was run by the judge. The box was at load 12 with two niced gate-0 processes already running, which is the
round's process cap.

## 1. Red-team checks made by the judge

### 1.1 The arm-arc relay's kit numbers reproduce, but the kit's metal is generous

`ring2_out.json` reproduces the proposer's numbers exactly. The relay cases below are one-sided + (only increasing phi,
from 0 up to the bound), one-sided - (decreasing phi only), and two-sided +-.

| relay | relayed (kin = closed) | clean | contacts | under 1 mm |
|---|---|---|---|---|
| one-sided +20 | 18 | 18 | 0 | 0 |
| one-sided +30 | 27 | 27 | 0 | 0 |
| one-sided +45 | 38 | 38 | 0 | 0 |
| one-sided -30 | 9 | 4 | 5 | 1 |
| two-sided +-20 | 25 | 22 | 3 | 1 |
| two-sided +-30 | 36 | 31 | 5 | 1 |

At +30 the 27 relayed poses come from 23 stretched_stopB and 4 stretched_law losses. Their nearest parts are hub 1 13,
the kit's arm-side neck 13 and hub 3 1. Their minimum metal distances are 2.37-9.33 mm, median 7.57.

**The red-team point is the kit's metal level.** The kit CONTROL is fitted at q 1.0 (kit_paired.py line 33). The lead's
own taken poses sit much lower: min-distance percentiles p1 / p5 / p25 / p50 / p75 = 1.14 / 1.94 / 2.92 / 3.50 / 4.36 mm
(lead per-pose dump, 372 taken). These are different pose sets, so the ~4 mm difference between the medians is
indicative only.

Eight of the 27 relayed poses sit at <= 4 mm even on the kit's higher metal:

| pose (plane / elev / axial) | phi | kit min (mm) | part | lead wall | th |
|---|---|---|---|---|---|
| 306 (60 / 75 / -120) | 13 | 2.78 | neck | stretched_stopB | 117.2 |
| 333 (75 / 75 / -120) | 17 | 3.75 | neck | stretched_stopB | 120.4 |
| 336 (75 / 90 / -105) | 5 | 2.37 | neck | stretched_law | 110.3 |
| 340 (75 / 120 / -105) | 8 | 2.76 | hub 3 | stretched_stopB | 114.0 |
| 343 (75 / 150 / -105) | 10 | 2.59 | neck | stretched_stopB | 114.7 |
| 372 (90 / 165 / -90) | 7 | 3.48 | neck | stretched_stopB | 111.8 |
| 399 (105 / 165 / -90) | 19 | 3.21 | hub 1 | stretched_stopB | 120.0 |
| 426 (120 / 165 / -90) | 30 | 3.33 | hub 1 | stretched_stopB | 126.0 |

On the lead's real arm-side metal (E strap, knee, pad at 6-10 mm, median E 6.0) and its fitted hub 1, these are likely
contacts. The lead loses all of them, so its dump has no distances there (ev false), and only the model can say. Two
of them, 399 and 426, are overhead poses on hub 1. The relay cannot move hub 1; it only decides whether the pose is
evaluated.

### 1.2 A one-sided spring relay cannot choose its wall

The proposer's policy relays only stretched poses. Physically, a carriage held on its zero dowel by preload turns
whenever the arm demands a phi in (0, PHI] that closes the chain within its stops, and it turns at any wall: folded,
knee window or J3 stop.

The lead's lost ws poses are stretched_stopB 68, folded 15, knee 9, stretched_law 5 and in_window 2. With the lead's
wall in window (`nok_out.json`), the in-window count is 271 at phi 0, 309 at +30 and 325 at +45. That is 38 / 54
relayed, of which 27 / 38 are stretched (`ring2`). So **~11 (+30) / ~16 (+45) folded-side relays carry no metal check
at all**. At the folded wall the lead's limiter is hub-2 clearance (median need 71 vs 62 mm).

Each of those poses that ends in skin is a contact (~+0.27 gap). Each that ends in a part-part collision is a **jam**:
metal on metal between non-adjacent bodies, which the stop rule does not accept as a stop. Jams must be listed
separately.

Amendment to picks 1 and 2: the relay solve takes the least phi on every lost pose.

### 1.3 The track must be a circle of one radius about a GH-through axis

The spec sets `R_t(az)` = the skin radius at each azimuth. That makes a cam track, which moves the pad radially. At the
lateral azimuth the radial direction is about along J3. The knee's pins are parallel to J3, so they cannot absorb that
motion, and the closure fails.

The track must therefore be circular about an arm-fixed axis through GH. Concurrency then holds. The axis may tilt from
the humeral long axis, and the tilt is now a sweep parameter.

What the catalogue already measured for arm-fixed tracks:

- seed-2r-cring: "a circular track about any GH-through humerus-fixed axis hugs the arm only over its lateral +-60 deg".
  The GH-elbow line runs 3-8 mm under the skin at mid-arm.
- acromion-pointer-arm-ctrack: an arm-fixed track has a ~105-deg torso-free arc. A circular race at its highest skin
  radius floats 18-32 mm over a 133-200 deg arc.

Arc lengths of the picks against those limits:

| design | arc |
|---|---|
| pick 1, PHI 30 | ~58 deg |
| pick 1, PHI 45 | ~73 deg |
| pick 2, PHI 60 | ~88 deg |
| pick 2, PHI 75 | ~103 deg (at the torso-free limit) |

### 1.4 Determinacy needs the preload to beat gravity

The relay is the 1-D null-space of a 4-joint chain on a 3-DOF arm orientation. The spring and dowel determine it only
while the preload exceeds the generalised gravity torque along that null-space.

Order of magnitude: a chain of ~0.2 kg whose centre of mass moves ~50 mm per rad of null-space motion gives ~0.1 N.m.
That equals the proposed 0.06-0.12 N.m preload.

So preload is a determinacy variable, not "feel only". Picks 1 and 2 now set it from a per-pose gravity check (x1.5)
and report the felt axial torque past the wall.

### 1.5 The relay hardware

The proposal uses O8 V-grooved sleeves on MR63ZZ (O6) bearings. Under a 2 mm 90-deg V edge that leaves ~0.3 mm of wall
at the V root. Corrected to O10 sleeves (2 mm wall).

The constant-force spring (Lee Spring CF class) and the ISO 8734 dowels are catalogue parts. The relay is a counted 4th
joint (CLAUDE.md "Reach is the priority now": spring-centred + stops is a legal MVP1 determination). It adds +25 cx,
and it is a user-say item even at 95.

### 1.6 The plain-3R relay (kfree) reproduces

`nok_metal_out.json` (kit CONTROL with a1max = a1, hub K kept as metal):

| relay | relayed | clean | collide | contacts |
|---|---|---|---|---|
| one-sided +30 | 54 | 44 | 10 | 1 |
| one-sided +45 | 68 | 53 | 15 | 1 |
| one-sided +60 | 83 | 68 | 15 | 1 |

`nok_out.json`: the plain 3R has 216 poses in window. The one-sided relay raises that to 270 / 284 / 299 at +30 / +45 /
+60. The minus side gives 248 / 257 / 260.

The 15 collisions are folded-side relays: hub 1 at plane -15..45, elev 90-165. Under section 1.2 these are jams, not
stops, and the window has to design them out. The 1.1 and 1.3 caveats apply even more strongly, because the arc is
longer and the relay angle larger.

### 1.7 The free-K oracle: reproduced, but its rescues live in the 1 mm shell

`k33_full.json` reproduces the k33 kit:

- fit 12.18 fast;
- wear 18.61, reach 0.7694 (277), contact 0.0475;
- why: fold 55, slide 15, contact 19.

`kscan3` gives each binder's best clearance on the legal self-motion:

| pose | clearance | where |
|---|---|---|
| 117 | L2 +1.06 / hub 2 +2.34 | floor |
| 148 | L2 +0.46 | floor |
| 316 | L2 +0.39 | dK 60 |
| 369 | L2 +0.34 | dK 47 |
| 129 | L2 -2.56 / hub 2 +0.11 | floor; L2 needs the corridor's +0.90 |

**Only 117 clears 1 mm.** The oracle's rescues pass the plan's 0.2 mm gate, but under the near-touch objective they
are still contacts. That is the shell the lead's T1 WATCH already flags (16.56 points in 1-2 mm).

The pick reports both counts: clear by >= 0.2 mm and clear by >= 1 mm.

### 1.8 The two J3-split ideas: the insight holds, the stop values are in a private convention

The insight holds. In the lead, dK is a function of q2, and th is monotone in q2, so a1e is a function of th. No K law
of th, the lead's coupled K included, can serve the external-rotation group (117 / 129 / 148: wants the floor) and the
internal-rotation group (316 / 369 / 343: wants more K) at the same th. J3's angle separates them: at the kit K, q3 is
-52..-90 for the first group and +106..+116 for the second.

But `kscan3.py` line 51 measures q3 from an arbitrary reference, e = unit(u3 x [0.3, 0.5, 0.8]). So "q3max 88-92" and
"q30 ~ 0" are not in the model's J3 convention (the lead's stop is -111.90 / +122.74 in its own). The two groups'
separation of ~140 deg holds in any reference. The stop and the spring centre must be re-placed in the model's own q3.

Exposure of state-A poses to a J3 upper stop at k33: 12 state-A takes have axial <= -90 (37 at <= -75), against 48 / 60
K-open takes.

Both ideas are realisations bounded by the oracle, at 4 counted joints and cx 33-36, for an expected 16.5-18.0. They
are merged as cells B / C of the oracle, run only if the oracle's connected bound beats the lead by >= 0.5 (<= 17.78).

### 1.9 The desmo window: the 6 legal pins exist, but not at pitch <= 9.0

`stage1_level_scan.json` confirms the feasible pins (PA <= 34.47, groove rc >= 1.0) at each level:

| level (mm over hub 2's face) | 0.861 | 2.5 | 3.15 | 3.9 | >= 4.6 |
|---|---|---|---|---|---|
| feasible pins | 21 | 8 | 6 | 2 | 0 |

The reported best rows at 3.15 are rows [a_s, psi, PA, rc]:

- best rc: [9.9, 149, 33.15, 1.095], pitch 7.505-9.836;
- best PA: [9.7, 150, 29.82, 1.013], pitch 7.613-9.786.

The spec's "pitch <= 9.0 so the insert ends inside r 10.5" has no candidate among them. With a pitch high of ~9.8:

- the insert reaches r ~11.1 (pitch_hi + 1.26);
- the window reaches r ~10.9 (pitch_hi + 0.75 + 0.3).

Both are past the O20 rim (r 10). The window opens link 1b's J2 plate through its rim, leaving a C-section housing
with 0.8 mm over the O11 seat.

Fixes to the pick:

- drop the pitch cap and price the insert's real outer radius as metal;
- report the window's outer radius;
- the housing goes through M5 / FEA before any CAD.

The gen-9 skeptic's new finding also applies here (`VERIFY.md` section 5). The groove's rise and the slot both end at
dK_lim 46.5, before the J2 dowel engages (window -14.315, engagement -14.455), so the stop load goes through the drive.
The re-synthesised groove must put J2's stop engagement first, and the stop order is now a pass condition.

### 1.10 The straight guide is not "locked by the closure"

A rail in link 2 runs tangent to the sphere at hub 3, which is normal to J3. J3 and both knee pins are parallel to J3.
So rail + J3 + pin a + pin b form a planar 4-DOF group in the knee's plane, against 3 planar freedoms: **one
undetermined coordinate** (R17). The class closure stands anyway: th is identical to 0.000 deg on 470 poses
(`kin_out.json`), 0 fold takes, and the rail metal costs +0.6 / 1.1 / 1.6 gap at travel 0 / 10 / 20.

### 1.11 The polycentric slot J2 and the dog ring

- **slotguide-polycentric-j2-3r:** its own gate-0 check kills it. The union boss is fixed to link 1 and pays the
  highest skin it passes: 170 / 371 contact poses at 62 mm, and 158 of 270 boss points clear at no level <= 80. It
  also has an ACTIVE joint without the v5 O20 stack. Its 7.8 mm J2 stack against 12.25 is exactly the slim-hub gain the
  user ruled out ("Keep O20 only").
- **dogring-conecut-knuckle-3r:** priced dead at 18.25-23.0 cx against the 15.75 bar. A spring-free coaxial dog is
  impossible: no locking arc exists between coaxial bodies. Its on-file form is refuted at 97.83.

## 2. Verdicts

| candidate | lens | verdict | reason |
|---|---|---|---|
| guide-null-link2-knuckle-3r | A | MERGED into armarc-relay-knuckle-4r as step 0 (the lens-A closure to FINDINGS); rejected as a design | 0 fold takes by construction; +0.6..1.6 gap of rail; undetermined rail coordinate with the two-pin knee (1.10); radial column +7.3 |
| armarc-relay-knuckle-4r | A | **PICK 1** | the only survivor of lens A's rule (changes an axis direction, >= 17 clean takes on the kit, beats the free-K bound on paper); amended per 1.1-1.5 |
| kfree-armarc-relay-4r | A | **PICK 2** | the same relay with K, drive and drive metal deleted (cx ~31 vs ~50); reproduces (1.6); runs beside pick 1 on the same wrapper |
| freek-oracle-route-knuckle-4r | B | **PICK 3** (the instrument; bound, never a claim) | the plan's lens-B row; reproduces (1.7); merged cells B / C below |
| j3spring-split-knuckle-4r | B | MERGED into pick 3 as cell C (conditional) | bounded by the oracle; q30 in a private reference (1.8) |
| j3stop-relay-knuckle-4r | B | MERGED into pick 3 as cell B (conditional) | bounded by the oracle; q3max in a private reference (1.8) |
| slotguide-polycentric-j2-3r | C | REJECTED | O20 rule at an active joint + its own gate-0 union numbers (1.11); short-stroke fallback 26-29 at cx 8 is not a Pareto point over the cx-0 pin knee (27.20) |
| desmo-window-knuckle-3r | C | **PICK 4** | the only lens-C idea that moves the BUILT cx frontier (the gen-9 R6 stack conflict); amended per 1.9 |
| dogring-conecut-knuckle-3r | C | REJECTED | dead at the price gate (18.25-23.0 vs 15.75); a duplicate of dogring-draglink-knuckle-3r (refuted 97.83) |

## 3. Ranking

Score = (expected gap gain vs the lead 18.28) x (confidence) x (buildability). Buildability is 1.0 at 0 passive
translations with every joint a real part; all survivors qualify. The champion (spherical 3R, 75.94 frozen exact) is
beaten by every survivor by 55+ points, so the lead is the useful reference.

| rank | pick | judge's expected gap | gain vs 18.28 | confidence | buildability | score | why this rank |
|---|---|---|---|---|---|---|---|
| 1 | armarc-relay-knuckle-4r | 13-16 (paper 10.8) | +3.8 | 0.4 | 1.0 | 1.5 | the only route on file past the second wall; a real 95 if the kit's clean relays survive real metal |
| 2 | kfree-armarc-relay-4r | 15-20 (paper 14.7-16.1) | +1.3 | 0.3 | 1.0 | 0.4 | the same lever on a chain with no K or drive (cx ~31); longer arc, larger relay angles, 15 jams to design out |
| 3 | freek-oracle-route-knuckle-4r (+ cells B / C) | bound 16.7-18.1; B / C 16.5-18.0 | (bound) | 0.2 | 1.0 | 0.2 + closure | the plan's lens-B instrument: decides with a number whether any K lever at these seats can reach 95 |
| 4 | desmo-window-knuckle-3r | 18.6-19.3 (+0.3-0.7 priced) | -0.3..-1.0 | 0.4 | 1.0 (FEA open) | Pareto | the built frontier at cx 16.0-16.25 vs the lead's 18.5; fixes the gen-9 R6 blocker |

## 4. Picks (appended to docs/concepts/catalogue.json, status "ideated")

1. **armarc-relay-knuckle-4r** (lens A survivor, 4 counted joints, 0 passive translations, cx ~50).
   - Step 0 writes the length-changing-class closure to FINDINGS.
   - Gate 0 wears the lead + a one-sided circular arm-arc relay frozen exact.
   - Relay physics: least phi on every lost pose; jams listed separately.
   - Track: one radius about a GH-through axis, tilt swept.
   - Preload set by a gravity determinacy check.
   - **Kill above 17.5.**
2. **kfree-armarc-relay-4r** (4 counted joints, 0 passive translations, cx ~31).
   - The same relay on a plain O20 3R at the lead's seats, with no K or drive.
   - Fit over the relay and the a2 window shift.
   - **Kill above 17.5.**
3. **freek-oracle-route-knuckle-4r** (the lens-B bound, never a claim).
   - Cell A: oracle K + anterior link-2 corridor at k33, gated as the plan pre-registered, plus the >= 1 mm count.
   - Cells B (J3 upper stop) and C (J3-centring spring) run only if A's connected bound <= 17.78, with q3 in the model's
     own convention.
4. **desmo-window-knuckle-3r** (3 joints, 0 passive translations, cx 16.0-16.25).
   - Stage 1 into link 2's underside, a crank window in link 1b.
   - Out-of-rim insert priced, stop order checked, FEA on the open-rim housing.
   - **Kill above 19.45** or held paired worse than the lead by > 0.5.

## 5. What the picks are expected to show, and what comes next

- **Pick 1 is this round's only shot at 95.** If it lands at 13-16 frozen exact, it is the first design on file past
  the second wall. It is also a 4-joint answer the user must rule on (cx ~50 against the lead's 18.5). If it dies,
  the number names the binding part (arm-side metal over the deltoid, hub 1 overhead, or folded-side jams), and lens A
  closes completely.
- **Pick 2 answers whether the relay can replace K entirely.** A plain 3R + relay at <= 17.5 would beat the lead with
  no knuckle, no drive, no K play and no M5 path, at cx ~31.
- **Pick 3 puts the jump track's take-bound number on file.** Expected: the oracle fails the gate (129's hub 2 at +0.11
  at the floor, and contacts >= 5), which closes "any K lever at these seats with O20". Cells B / C then stay unrun.
- **Pick 4 makes the cx frontier buildable** (or proves the open-rim housing cannot carry the J2 moment). That decides
  whether the next generation-winner CAD can be a desmo.
- **Next:** the round's screen runs local and niced, <= 2 processes at a time: picks 1 and 3 first (the two bounds),
  then 2 and 4. Verify any pass at 18.28 by hand. The auditor writes the ledger entry for the round winner. Every
  screened morphology writes its docs/concepts/viz preview in the same task.
