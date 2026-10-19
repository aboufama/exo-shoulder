# Round 501 (G1, track golden) ideation: judge and red team (2026-10-19 02:39 UTC)

The user's request (relayed verbatim to this round): "Keep pushing, I want something better than 95 with very low
complexity". 95 = a verified plain gap <= 13.75 on frozen exact Bench(110,360) (score = 100 (1 - gap / 275)). The
plan is docs/concepts/ROUNDS.md "Round 501 plan (Round G1, track golden)" (942749c). No bench, judge or kit file
changed, so no number below moved because the measurement changed.

**Bars.**

- Lead (3 active): conecut-knee-knuckle-3r 18.28 (93.35), held 22.38, cx 18.5.
- Complexity ladder (verified, 3 active): cx 0 H1 skin-normal-3r-pin-knee 27.20; cx 12 geneva-tail 23.57;
  cx 15.75 desmo-slipper 18.95.
- Champion (the ranking's reference): spherical 3R, 75.94 on Bench(110,360) exact.

**Candidates:** nine, three per lens (A cx0-knee-frontier, B rod-dwell-lowcx, C rolling-j2). All nine have 3 active
joints, 0 passive translations, and no gears, pulleys or cables in the drive sense. Each candidate is red-teamed below
on the raw poses, with the judge's own scripts. The scripts are in
/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/r501judge/:

- rt_lensA.py: lens A kinematics and fold conditioning;
- rt_roll.py: lens C kinematics and conditioning;
- rt_roll_prox2.py: lens C J2-zone proximity at one level per part.

The tools/simplicity.py --score re-pricing is in the text.

**Outcome: three picks. Six candidates are merged into them, two of those as step-1 fallbacks that fail the price
gate. One proposed spec is refuted and kept only as a capped sweep cell.**

## Verdicts

| # | candidate | lens | verdict | why |
|---|---|---|---|---|
| 1 | isoceles-shortdyad-pinknee-3r | A | **PICK (rank 1)**, merged with #2 and #3 as seeds | the in-band top of the knee-class frontier at cx 0; highest confidence and buildability |
| 2 | posterior-slot-a47-pinknee-3r | A | MERGED into #1 (seed B) | same morphology and model as #1; the most kinematic headroom (286) and the best conditioning |
| 3 | pole-j1-lateral-hub2-pinknee-3r | A | MERGED into #1 (seed C) | same morphology; knee chain in band, but follow 0.836 kinematically |
| 4 | slowpole-slot-knuckle-3r | B | **PICK (rank 3)**, merged with #5 and #6 | the only lens-B drive inside the cx <= 12 gate when bodies and joints are counted |
| 5 | slowpole-rimroller-knuckle-3r | B | MERGED into #4 as a step-1 fallback | shares #4's ghost; prices 16.5, not 11.5, which is above the gate and above desmo-slipper's 15.75 |
| 6 | slowpole-coupler-knuckle-3r | B | MERGED into #4 as a step-1 fallback | shares #4's ghost; prices 15.5, not 10.75; it carries fourbar-longdyad's B1 risk |
| 7 | rollcone-hubspot-pinknee-3r | C | **PICK (rank 2)**, merged with #8 and #9 | kinematics reproduced exactly; the J2-zone gain survives the flat-level rule; the only path past the 275 takes a 95 needs; RULE-GATED |
| 8 | ringroll-farcentre-pinknee-3r | C | SPEC REFUTED; its internal sign kept as a capped cell of #7 | at one level per part, 59 of 158 ring / planet directions cannot clear the clip frames below 115 mm, so the ring floats at ~111 mm (in-band 0.013) |
| 9 | rollcam-dwell-pinknee-3r | C | MERGED into #7 as the law cell | same hardware class and model; it only changes the law (292 kinematic, half the sun metal) |

No joint lacks a real component. The rolling pair is a machined cone pair held by strip, the CORE / Rolamite form: it
is plausible, not catalogue, and it carries the rule questions below. No candidate leaves a passive coordinate
undetermined:

- the knee pins are set by closure;
- the slaved K is form-closed by the slot (or set by the spring plus the drive in the fallbacks);
- the rolling J2 is one joint.

## Lens A: the cx-0 knee-class frontier (picks #1, merged #2 and #3)

**The claim.** All three cells come from one bound on raw data, the per-pose O20-disc requirement map. It is
calibrated on H1 to one pose (bound 113/160 against the kit's 112/160).

- The bound's frontier, over 230,951 cells: the best min in-band over the chain parts is 0.900 up to take 0.72. At
  take >= 0.74 it falls to 0.535, with hub 2 binding.
- The isoceles cell tops that frontier: bound gap 17.50 on Bench(60,160), against 19.4 for H1's cell.

**Judge's measurements** (rt_lensA.py, Bench(110,360) poses):

| cell | a1 / a2 | window (5-deg th margin) | ws / clip / overhead (kinematic) | min abs(u1.(u2 x w)) over takes | takes below H1's worst |
|---|---|---|---|---|---|
| H1 (reference) | 41.0 / 68.3 | 32.2-104.3 | 263 / 110 / 13 | 0.233 | 0 |
| isoceles (seed A) | 40.5 / 44.9 | 9.4-80.3 | 263 / 110 / 17 | **0.110** | **19** (14 ws, 5 clip frames, th 10-20, none overhead) |
| posterior-slot (seed B) | 47.5 / 73.4 | 30.8-115.9 | 286 / 110 / 21 | 0.270 | 0 |
| pole-J1 (seed C) | 64.3 / 45.8 | 23.5-105.1 | 272 / **92** / 16 | 0.225 | 2 |

**What the red team found.**

- **Kinematics: reproduced exactly for all three cells.**
- **The isoceles folded edge is badly conditioned.**
  - At the 5-deg th margin, q2 is only 12.3 deg from the fold. H1 has 21.7 deg there.
  - The Jacobian volume is half of H1's worst.
  - Five clip frames, which are real motions, pass through it.
  - This is legal under the one-metric fold rule. It is a feel risk for the unpowered MVP1: J1 and J3 near-coaxial
    split one motion between q1 and q3.
  - The model must report it.
- **The proposer's real-kit check is not a reading of the cell.**
  - The 45.82 was run at b3 0.2 WITHOUT the az2 / el2 re-solve, so a2 was 43.8, not 44.9.
  - It read reach 0.619 fast (fold 40, parts 16, skin 9). H1 reads 0.700 on the same bench.
  - The cuff end and the window both need a refit before any number counts.
- **The frontier table excludes a cx-0 95.**
  - No knee cell holds take >= 0.74 with hub 2 in band.
  - So lens A's step-0 kill fires on the 95 question: no cell holds 266 takes with hub 2 in band.
  - What is left is a cx-0 Pareto pass over H1, the user's build base.
- **Seed B's best gap-metric neighbour is a breach, not a 95.** That cell (14.04) floats hub 2 at 105 mm, 0.08 in
  band, which breaks the 1 cm rule. The auditor watches for any CMA in this basin that buys reach that way.
- **Seed C's J1 seat needs a ruling.** bvec(137.6, 78.2) has an anterior component of 0.15. The auditor confirms it
  reads as acromion top and not clavicle (user ruling 4).

**Why one entry.** The three cells are one morphology, H1's. A single model runs them with a pre-registered pick
across seeds, which is also the knee-class frontier map the plan asks for.

**Expected.** 23-26 frozen exact.

- Pass: < 27.20.
- Kill: envsel ib14 < 0.85 at reach >= 0.70, or every seed's fit > 24.5.

## Lens B: the slow-pole knuckle (pick #4, merged #5 and #6)

**The claim.** The pin-flank drive closures came from the LEAD'S LAW, not from the drive class.

- A 40/40 K dyad needs a 30.3-deg stroke, against 45.6 deg for 26/38.
- It tolerates a slow law: msub 6.1 at rho 0.5, against 0.0 on 26/38.
- The slow law moves the relative pole to 13.3 deg from u2, inside hub 2's reach.

**What the red team found.**

- **The closed form reproduces** (slowlaw.py): stroke 30.3, dq2 60.5, onset th 57.2, msub min 6.1 at the onset,
  K 12.1 deg at th 78, pole 13.3 deg from u2.
- **This is the re-dyad of a dead row's untried cell.** The slot is onetooth-slowlaw-knuckle-3r's spring-free cell D
  on a new K dyad.
  - That row died at step 0 on the same ghost harness: rho 0.8 read 22.79 with 247 takes; rho 0.9 read 20.53 with
    255.
  - The cause was measured: msub < 5 rejected the first ~5 deg past the onset.
  - The 40/40 dyad removes that cause, so this is a new cell, not a re-screen.
- **The drive is at the edge.** The same row measured the one-pair drive range at <= 32.1 deg over 1773 pin
  placements, and 23.6 deg at rho 0.8.
  - 40/40 needs 30.3.
  - The proposer's planar pressure-angle lens spans 52-82 deg of q2 at r 13-14 mm, against the 60.5 needed.
  - Both are at the edge. The built-flank PA gate decides.
- **The plate was measured on the wrong body.**
  - The slot plate is on link 1a. The proposer's plate map used a ring fixed to link 1b.
  - Over the 30.3-deg stroke, hub 2 moves 2 sin(15.15) sin(40) x 61 = **20.5 mm** in link 1a's frame.
  - So the slot and plate need a ~20 mm tail along hub 2's path.
  - Their proximity at the K-open poses (overhead and IR, under the acromion) is unmeasured. The spec now requires it
    on link 1a.
- **The complexity is under-counted.** Re-priced with tools/simplicity.py --score, counting link 1b and K as a body
  and a joint (the planner's convention, which gives its 10.5):

  | drive | proposer | judge |
  |---|---|---|
  | slot | 7.0 | **10.75** |
  | rimroller | 11.5 | **16.5** |
  | coupler | 10.75 | **15.5** |

  - The proposer numbers come from desmo-slipper's record convention, which leaves link 1b and K out. The same
    convention prices the lead at 18.5.
  - The rimroller and the coupler fail lens B's cx <= 12 gate. Both also sit above desmo-slipper (15.75 at 18.95), so
    they are step-1 fallbacks only, reported as dominated unless < 18.95.
  - The coupler also carries fourbar-longdyad's B1 count over the window, where K is never on a stop.
- **Ceiling.** The free-K oracle bounds every K law at 17.69 on the lead's seats, so this row cannot reach 95. Its
  value is the lead's reach at ~60 % of its complexity.

**Expected.** Ghost 18.6-20.5; built 19.5-21.5.

- Pass: <= 18.95 at cx <= 12.
- Kill: ghost > 19.0 or < 258 takes; > 4 sweep contacts; drive in-band < 0.70; PA span < 60.5 deg of q2.

## Lens C: the rolling-cone J2 (pick #7, merged #9, the capped internal cell of #8)

**The claim.** A strap-held cone pair with its apex at GH replaces hub 2 on H1.

- Its instantaneous axis is the contact line. So the KINEMATIC J2 (virtual centres uK and v2) splits from the J2
  METAL (the contact zone).
- The dyad lengthens while the metal stays on the in-band hub-2 skin.
- The external cell 25/10/30 opens the window to 22.9-117.7 deg, against H1's 27.3-109.3.

**Judge's measurements.**

| cell | window | ws / clip / overhead | min abs(u1.(c x w)) | takes below H1's 0.233 | contact walk |
|---|---|---|---|---|---|
| rollcone 25/10/30 (pick) | 22.9-117.7 | **285** / 110 / 17 | 0.179 | 7 (278 kept) | 11.0 mm |
| rollcone beta 0 | 18.1-116.5 | 291 / 110 / 18 | 0.201 | 3 | 10.9 mm |
| rollcam r0 0.15 / r1 0.6 / W 50 | 17.0-117.6 | 292 / 110 / 18 | 0.214 | 1 | 8.2 mm |
| ringroll 30/15/180 (internal) | 8.1-141.7 | 329 / 110 / 25 | 0.194 | 3 | **40.0 mm** |
| ringroll 25/10/180 | 5.1-128.4 | 311 / 110 / 22 | 0.175 | 4 | 24.7 mm |

J2-zone proximity on Bench(60,160) uses the same crude ray rule for every row; only the relative numbers count:

| J2 metal | per-direction level (proposer) | one level per part (judge) |
|---|---|---|
| H1's O20 hub-2 disc (control) | 71 net ws, in-band 0.889 | 86 net, in-band 0.889 (R_lo 53-61) |
| rollcone bands 25/10/30 | 88 net, in-band 0.962 | **104 net, in-band 0.960** (R_lo 55-63) |
| ringroll ring 30/15/180 | 103 net, in-band 0.506 | in-band **0.013**: 59 of 158 directions infeasible below 115 mm, the feasible ones span 55-113 mm |

**What the red team found.**

- **Kinematics: reproduced exactly.**
- **The coupled-fold reading is not lenient.** The conditioning at the window edges is within ~25 % of H1's worst,
  and only 1-7 takes fall below it.
- **The flat-level rule is the right one for this joint, and the gain survives it.**
  - The proposer's rule gave every metal direction its own clip-clear radius. That is a skin-contoured band, the
    pattern that refuted floating-centre-3r.
  - A strap-held pair cannot be contoured: the straps run at one slant radius on both cones. Both 8-mm bands must
    cover that radius at every rolling position, which leaves <= 1.5 mm of edge freedom.
  - Read at one level per part, the rollcone's +17 net becomes +18. The gain is real.
- **The ringroll ring cannot sit in band.** Its 160-deg ring as proposed fails the 1 cm rule. Its internal sign stays
  only as a cell with the carrier span capped at <= 50 deg.
- **Arithmetic.** If the rest of H1's metal keeps its 0.90 take ratio, 285 kinematic gives ~257 takes, reach 0.714,
  gap ~21.7. Beta 0 (291) and rollcam (292) are the only cells of the whole round whose kinematics clear the 275 takes
  a 95 needs, at cx <= 6.5.

**Rule gate (it carries the rank).** This row cannot be called verified, a winner or a leader until the user answers
four questions. Earlier planners kept rolling-cone-3r closed:

- as a hubless joint, under "Keep O20 only" (ROUNDS.md round 7 and round 12 plans);
- as a "gear-class coupling", under MVP1's "no gears, pulleys or cables" (round 105 plan).

The questions for the user:

1. Is a hubless rolling J2 allowed under "the v5 O20 stack at every joint"?
2. Do strap-held pitch cones count under "no gears, pulleys or cables"? The straps carry no drive; they only hold the
   pair together.
3. Are the straps priced as flexures? That gives cx 6.5 with 2 straps and 10.0 with 3.
4. Which fold margin governs a coupled joint? Proposed: the coupled-fold th margin plus the kit dyad margin, with min
   abs(u1.(c x w)) reported.

**Mechanical risks.**

- GH apex coincidence is held by the straps and the contact alone. Generator sliding and band tilt need a CalculiX
  check.
- Strap fatigue at the 9.7 mm planet radius; rollcam's 4.3 mm radius needs NiTi.

**Expected.** 21-25 frozen exact.

- Pass: < 27.20 at cx <= 6.5, AND the user's rule yes.
- Kill: envsel ghost > 24; a band's in-band < 0.85 at one level; > 4 band contact poses over H1's.

## Ranking

Score = (expected gap reduction vs the champion 75.94) x (confidence) x (buildability: 0 passive translations for
all three, so buildability is the component and rule risk).

| rank | pick | cx | expected frozen | reduction | confidence | buildability | product | the one thing to test first |
|---|---|---|---|---|---|---|---|---|
| 1 | isoceles-shortdyad-pinknee-3r (+2 seeds) | 0 | 23-26 | ~51 | 0.5 | 1.0 | ~25 | the cuff end: refit the knee with the a2 re-solve at b3 before reading anything (the 45.82 read ran a2 43.8 and reach 0.619) |
| 2 | rollcone-hubspot-pinknee-3r (+ rollcam, capped internal) | 6.5 | 21-25 | ~53 | 0.4 | 0.5 | ~11 | the rule questions to the auditor and user; then one-level band R_lo with the common strap radius |
| 3 | slowpole-slot-knuckle-3r (+ 2 fallbacks) | 10.75 | 19.5-21.5 | ~56 | 0.3 | 0.65 | ~11 | the shared ghost (40/40, rho 0.5): kill > 19.0 or < 258 takes; then the slot PA span in built-flank mode on link 1a |

Picks 2 and 3 tie on the product. Pick 2 ranks above pick 3 for two reasons:

- its step-0 kinematics and its J2-zone gain both survived the judge's re-reads;
- it is the only family here with a path to the user's 95. Lens A is capped by its own frontier (take >= 0.74 forces
  hub 2 out of band), and lens B by the free-K oracle (17.69).

**On the user's ">95 with very low complexity":** none of the nine candidates is expected to verify at <= 13.75.

- The cx-0 knee class is now shown, from its own bound, to stop near take 0.72 with hub 2 in band.
- The slaved-K class stops at the oracle 17.69.
- The rolling J2 is the one lever left whose kinematics clear 275 takes at cx <= 6.5. Its metal and the user's rule
  answer decide whether it can.

## What happens next

The three picks run as modelling tasks inside the round-501 loop. Each runs on local CPU at nice 10 with
OMP_NUM_THREADS 1: lens A on 2 processes, lens C on 1 process (90 min), lens B on 2 processes.

- **Lens A:** step 0 bounds for the three seeds, then the knee CMA, then seats.
- **Lens C:**
  - the auditor gets the four rule questions now;
  - the lead takes them to the user as one batched question, because it needs the user;
  - the metal model is built meanwhile, read as a kinematic proof only.
- **Lens B:** the ghost first; its <= 30 min decides.

Every screened row writes its motion preview (docs/concepts/viz/concepts/<id>.js, test.mjs, thumbs.mjs). It reports
plain, near1 and the 2 mm reading, T5 dumps for bench and held, overhead /28 and /71, min th, and the cx record. The
alignment auditor audits each claim between Screen and Close.
