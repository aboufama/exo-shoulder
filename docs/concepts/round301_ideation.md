# Round 301 (O1, track overhead) ideation: judge and red team (2026-10-19 01:30 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). The lead is already past it, so the real
targets are gap 0 and 95 (gap 13.75). The track goal is overhead: take more of the 28 overhead workspace poses
(elev >= 140) of Bench(110,360) and of the 71 held ones. Pass bar: a verified plain gap no worse than the lead's 18.28
with 3 joints, or a clearly labelled 4-joint option.

The plan is docs/concepts/ROUNDS.md "Round 301 plan" (284ff59), with its restart note (fd38c8d). No bench, judge or
kit file changed, so no number below moved because the measurement changed.

**Lead to beat (3 joints):** conecut-knee-knuckle-3r, verified 18.28 (93.35), held 22.38, cx 18.5, overhead 8/28
bench and 18/71 held.
**Best 4-joint:** phi40-thinstack-relay-4r, 14.06 / held 16.69, cx 51.25, overhead 9/28 and 22/71.
**cx-0 frontier:** skin-normal-3r-pin-knee (H1), 27.20, overhead 5/28.
**Champion** (the ranking's reference): spherical 3R, 75.94 on Bench(110,360) exact.

**Candidates:** nine, three per lens. Each one resubmits, refines or replaces the 9 unjudged ideas of the stopped run
(docs/concepts/ideas_restart/r301_unjudged_ideas.json).

- Lens A (abduction-cone): mirrork-kover-l2-knuckle-3r, foldlobe-conecut-knuckle-3r, conetilt-j1-knuckle-3r. All
  three were declared DEAD by their own proposers at step 0.
- Lens B (rocker-redundant-4r): ikring-thinstack-knuckle-4r, ikring-distalshell-knuckle-4r,
  ikring-mirrork-knuckle-4r.
- Lens C (drive-free-cone): weldk-overstrap-pinknee-3r, mirrork-stackhorn-overstrap-knuckle-3r,
  weldk-crossover-kneeless-3r.

Every joint maps to a real part:

- O20 v5 hubs on MR117-2RS pairs;
- MR63ZZ pairs at the knee pins and at the crank pivot;
- ISO 8734 dowels;
- a 1.0-1.5 mm slotted Ti shell with a 14 x 14 T-nut carriage on iglidur tape (phi40's verified J4 stack);
- bent 8 x 3 Ti-6Al-4V bars.

All nine have 0 passive translations and no gears, pulleys or cables. The K of the knuckle rows is slaved by the
lead's drive. The knee pins are closure-determined (H1 precedent). The ring J4 of lens B is an ACTIVE counted joint:
see "Determinacy" under pick 1.

**Outcome: four picks, one merge, four rejections.**

1. **ikring-thinstack-knuckle-4r** (lens B). phi40's verified hardware on the lead, with the coil deleted and J4 set
   by a proximity IK. PHI 40 is pre-registered as the primary cell (section 1.3).
2. **weldk-overstrap-pinknee-3r** (lens C). cx 0, 3 joints. Its projection is re-read with the judge's H1
   calibration (section 1.2).
3. **ikring-distalshell-knuckle-4r** (lens B). ikring-mirrork-knuckle-4r's ring hardware is merged into it. Its host
   is rejected with the mirror (section 1.1).
4. **weldk-crossover-kneeless-3r** (lens C). cx 0, no knee: the user's K1 preference, read as a 3-joint control.

Rejected:

- **mirrork-kover-l2-knuckle-3r**: dead, measured by its proposer.
- **foldlobe-conecut-knuckle-3r**: dead (the msub rule), and a duplicate of round 7's two-rise-lobe-pinknee-3r.
- **conetilt-j1-knuckle-3r**: dead (parking). Its variant b duplicates acroant-conecut-knuckle-3r.
- **mirrork-stackhorn-overstrap-knuckle-3r**: the judge's red team (section 1.1).

**The judge's main findings.**

1. **The mirrored K puts hub K on link 2's path.** Lens A's cone lever is the mirrored K, and three of the nine
   candidates carry it. On the overstrap ghost's own takes, hub K's axis lies within 14 deg of link 2's arc (plan-view
   overlap of the O20 hub K with the 8 mm link) on:
   - 68 of 105 clip takes;
   - 84 of 276 ws takes;
   - 5 of the 6 cone takes the mirror is meant to buy (median 7.7 deg).

   The lead never comes closer than 33.8 deg. No ghost checked this pair.
2. **The K-free ghost over-reads a verified K-free pin knee.** At H1's own seats it reads 250 ws / 10 overhead / 110
   clips. H1's verified numbers on the same bench are 237 / 5 / 106. The ghost's exact match on the lead (262 / 8 / 39)
   does not transfer to a K-free host. Both welded crossover projections fall by about 4-7 points.

## 1. Red-team checks made by the judge

The judge read kinematics and ghost parking on Bench(110,360), the shell roundness on the fit bench, and held numbers
only from the proposers' files on record. Nothing was selected on Bench(110,360) or on held (section 1.3 says how the
PHI cell was fixed).

- Judge scripts: /tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/r301j2/
  - mirror_l2k.py: hub K to link-2 arc on the ghost takes;
  - h1seat.py: effective J3 axis and arcs of H1, the lead and weldk;
  - park_wk_h1.py and anal_h1.py: the K-free ghost at H1's seats; output h1cal_0.npz.
- Proposer files re-read:
  - .../scratchpad/ring301/ (bench_t85.json, bench_t12.json, held_t85.json, held_t0.json, anal_park.py,
    shellaxis.py);
  - .../scratchpad/dfc2/ (park_w*_EZ0.json, park_w4_EZ50.json, maps_*.npz).

### 1.1 The mirrored K: hub K sits over link 2 (kills stackhorn and ikring-mirrork's host)

The measure is mirror_l2k.py, run in dfc2/. For each ghost take (maps_<cell>.npz okp, Bench(110,360)), it reads the
angle from uK to link 2's great-circle arc u2 -> w. At R 60-70, the O20 hub K plus its 1.5 mm skirt spans about 10 deg
and half the link width about 3.5 deg, so an angle under 14 deg means the two overlap in plan view.

| cell | takes | min / p10 / median deg | < 10 deg | < 14 deg |
|---|---|---|---|---|
| lead (sK -1), clips | 110 | 38.0 / 38.0 / 38.0 | 0 | 0 |
| lead (sK -1), ws | 262 | 33.8 / 38.0 / 38.0 | 0 | 0 |
| raisedj3 (sK +1), clips | 105 | 1.4 / 2.6 / 11.7 | 41 | 68 |
| raisedj3, ws | 268 | 0.3 / 5.0 / 21.8 | 57 | 79 |
| overstrap (sK +1), clips | 105 | 1.4 / 2.6 / 11.7 | 41 | 68 |
| overstrap, ws | 276 | 0.3 / 4.9 / 20.9 | 61 | 84 |
| overstrap, cone takes | 6 | 1.0 / 3.0 / 7.7 | 4 | 5 |
| conej3 (sK +1), ws | 263 | 0.1 / 5.1 / 26.3 | 50 | 66 |

This is the geometric cause behind the kover-l2 proposer's real-model run: 117 of 220 poses lost to parts, including
L2-hubK 33 and CRK-L2 42. It holds with K idle, because uK sits at bk2 from u2 on link 2's side whenever sK = +1.

**mirrork-stackhorn-overstrap-knuckle-3r** prices the mirrored drive against the skin. Its +6 mm lift is gated against
hub K, hub 2 and link 1b, but never against link 2. So its 271-take ghost still contains link 2 running through hub K
and the crank on a third of its takes, including the cone takes it claims. The only way through is the kover-l2
underpass: hub K and the drive rise 6-8 mm, at a priced cost of about +12 in-band against at most -3.9 reach. Verdict:
**rejected**.

**ikring-mirrork-knuckle-4r** has the same host. Its ring half is ikring-distalshell's ring, so that part is **merged**
into pick 3. The mirrored host returns only if a mirror-underpass row passes first: the kover-l2 model_spec, killed
unless fast near-1 <= 18.8.

Knowledge kept from the three mirror rows (none of it earns a slot this round):

- On the mirrored side only the far-side wrap transmits: beta +173.46 gives dK_lim 48.8. The lead's own synthesis
  closes there as-is (s_mirror.py).
- A one-pair involute on that side must be internal, with its link-2 tooth beyond hub K.
- Cone room for K exists only where link 2 sweeps (kover-l2's ring maps).
- **Machinery trap.** docs/concepts/models/roller-longdyad-knuckle-3r.py `_clamp`, line 64, maps beta > 0 to
  beta - 360 and clamps it to [-180, -150]. It is that model's documented search box (line 16), but any row that
  imports it to re-clock, mirror or re-seat a drive silently measures a clamped crank. acroant-conecut-knuckle-3r's
  "slipper drive fails beyond +6 (dK_lim 0, crank PA 44-53)" may be this clamp; re-check it before citing it.
- kover-l2's open instrument item: the lead stack never opens a mirrored K on a taken pose (dK_taken_max 0; law th_max
  96.3 vs the lead's 114.6). Every mirrored number from that stack is suspect until the onset side is fixed.

### 1.2 The K-free ghost over-reads a verified K-free pin knee (weldk-overstrap, weldk-kneeless)

Both welded crossover rows project from the one-level parking ghost: cone301/park.py, made K-free in dfc2/park_wk.py
(WELD=1). It is calibrated only on the lead, where it reproduces 262 / 8 / 39 exactly, and the lead has a K.

The judge ran the same ghost (park_wk_h1.py: u1 and a2 overridable, nothing else changed) at H1's verified seats:

- u1 = bvec(101.16, 63.90);
- effective J3 = (78.55, -5.34), from wd 70.39 / wa -8.12 / b3 0.284 through offset-skin-normal-3r's seat();
- a1 41.02, a2 68.26, branch -1, K welded, window [32.24, 104.28].

The judge's h1seat.py reproduces the lead's effective axis (77.25, -8.20) and the weldk cell's (104.37, 11.73), so the
seat function is right.

| reading (frozen exact Bench(110,360)) | ws takes | overhead /28 | clips /110 |
|---|---|---|---|
| ghost at H1's seats, station = wd/wa, EZ 0 or 50, DROP 5 | 250 | 10 | 110 |
| ghost at H1's seats, station = axis | 250 | 10 | 110 |
| **H1 verified (margin 5, v_rebase m5)** | **237** | **5** | **106** (follow 0.9636) |

The kinematic window holds 263 ws. H1 loses its extra 13 ws and 5 overhead to what the ghost has no metal or gate for:

- the knee's slide window (7 overhead);
- knee, E and pad contacts (contact 0.0256; 5 overhead);
- 4 clip frames.

Applied to weldk-overstrap's ghost (259 / 12 / 106), the same bias gives about 246 / 7 / 102:

| term | gap points |
|---|---|
| reach | 21.7 |
| follow 0.927 | 2.3 |
| H1-like contacts | ~2.5 |
| in-band | ~0.5 |
| **total** | **~27** |

With half the bias it is about 22.5. The judge's range for pick 2 is therefore **22.5-27**, not the proposer's 19-20.5.
That is still the only 3-joint lever this round with a positive expectation. It sits on the cx-0 frontier (H1 27.20),
it is G1-eligible (cx <= 6) and it adds overhead takes.

The kneeless row has no knee window, so part of the bias does not apply. It has two prior rows of its own instead:

- **deltoid-crest-j3-3r** (DEAD, v_gap 34.98, first frozen read 40.17): J3 on the deltoid crest wdir(104-109,
  -7..+1), the inverted-stack neck to BOTTOM, knee-less, arcs 40.5 / 45.9 (window [10.5, 81.4]). Its limiter was the
  stretched fold, and the fast bench over-read that basin by 11-14 points.
- **j3-neck-over-3r** (28.46, cx 8.5): the same inverted J3 stack as a lever, worth +1.95..+4.8 frozen, limited by
  hub-3 obliquity.

weldk-kneeless is the deltoid-crest morphology re-seated at the lead's J1 with the lead's a2 57.22 (window [21.7,
92.7]: +11 deg on the stretched side, where deltoid-crest lost 88). Its ghost (255 / 9 / 106) is a new measurement at
new seats. Its kill line is therefore j3-neck-over-3r's 28.46, and its pass line is H1's 27.20: a knee-less cx-0 3R
that beats every cx-0 design.

The other weldk numbers reproduce from park_w2 / park_w3 / park_w4:

- a1 40.5: hub 2 at level 66 (61 at a1 37.55); in-band proxy 0.760 (lead 0.758); clip 41 dropped;
- a1 41.5: hub 2 needs 400 mm;
- crossover off (EZ 50): 239 / 8.

a1 40.5 sits 1 deg from the hub-2 parking cliff, and follow 106 / 110 is 1 frame above 0.95 before the H1 bias.

### 1.3 The ring numbers reproduce; the IK rides the travel end (ikring-thinstack, ikring-distalshell)

The judge re-ran anal_park.py on the proposer's exact tables (no new parking). The frozen lead plus a ring about
8.5 / 243, window [0, 45], floor 0, reads:

- 301 static / **299 connected**;
- overhead **13/28**, elev 90-140 **63/85**;
- 39 new takes: 0 under 1 mm, 3 at 1-2 mm, median 4.40;
- 10 contact-only poses; estimate **9.33**.

At 12 / 235: 297 / 11 / 10.13. Held at 8.5 / 243: overhead 18 -> **32/71**, elev 90-140 105 -> 162/229. All of these
match the proposer to the digit.

New reads from the same tables:

- **The IK picks the travel end.** Of the 39 new bench takes, 21 choose k = 45 and 6 choose k = 40. Of the 71 new held
  takes, 35 choose k = 45. The end that the proximity IK wants is the anterior shell end, where phi40's hardware cliff
  is: held 211 (behind-back ER) touches at +48.9 deg, and behind-back ER caps anterior arm-fixed metal at about
  +49-51 deg relative to the pad (round 108 state). PHI 45 would put the shell end past that cap.
- **The overhead gain does not need PHI 45.** Static reads:

  | window | ws takes | overhead /28 | estimate |
  |---|---|---|---|
  | [0, 40] | 298 | 13 | 9.61 |
  | [0, 35] | 293 | 11 | 9.84 |

  Held at [0, 40]: 32/71 overhead, the same as [0, 45].

  **Pick 1 is therefore pre-registered at PHI 40, phi40's verified shell extent.** The reason is the hardware: the
  shell end stays inside the measured ER cap. It is not the bench read. PHI 45 is a secondary cell, read on envsel
  only.
- **The held shell.** 10 of the 71 new held takes sit under 2 mm, 6 of them under 1 mm. The 14 new held overhead takes
  clear 2.74-3.88 mm, and the new bench overhead takes (370, 399, 372, 343, 316) clear 2.33-3.84 mm. The overhead gain
  is not shell metal. The mid-band gain partly is on held.
- **Shell roundness reproduces** (shellaxis.py, fit bench, about 8.5 / 243):

  | station | clip-p90 defect | clip in-band | clip pokes |
  |---|---|---|---|
  | s 90 | 4.9 mm | 0.972 | 0/60 |
  | s 120 | 2.8 mm | 0.999 | 0/60 |

  The proposer did not report that the same read has 10 of 160 (s 120) and 11 of 160 (s 90) fit-bench ws poses
  poking, 18-49 mm deep, at plane 75-120 and elev 30-45: the torso across the generic [-41, +30] arc. phi40's real
  shell, a short arc at the pad azimuth, meets the torso on only 1 posterior-end pose (466). So each arc's end
  placement must be read per pose, and pick 3's posterior end (az_c - 12 >= -30) is its real gate.

**Determinacy (both ring picks).** J4 is a counted, sensed, ACTIVE joint. Its value is set per pose by the IK: a
self-motion, which in an unpowered MVP1 is held by nothing. This is the planner's lens B as written ("4th coordinate
chosen per pose by a proximity-optimal IK"). The precedent is freek-oracle-route-knuckle-4r (verified 16.20 as a
4-joint option). Both rows are labelled 4-joint options, never the lead, and are not G1-eligible.

Each claim also reports, on the same hardware:

- the spring-centred / least-phi reading (phi40's own mode at 8.5 / 243), as the unpowered control;
- the 1432-grid flood with the greedy |dk| <= 10 path, static vs connected.

This is not jump-track relay tuning, which the user paused 2026-10-18: there is no coil, no relay, and J4 is a new
counted joint for the overhead track.

### 1.4 Lens A's own kills, checked

- **mirrork-kover-l2**: the proposer's real-model runs and the judge's section 1.1 agree.
- **foldlobe**: at the 15 ghost inner-fold takes over 3 J3 seats, msub is 0.02-1.45 deg, against the 5-deg rule of
  minarc-stop-knuckle-4r-pinknee.py ik. Opening K just enough to close the inner fold makes the K, J1 and J3 axes
  nearly coplanar. This is round 7's two-rise-lobe-pinknee-3r kill (FINDINGS "0 folded poses under the winner's msub
  rule"), now with the geometric reason.
- **conetilt**: the parking ghost reads -1 ws and 0 to -1 overhead against the lead. Variant b (6 deg anterolateral)
  is within about 1 deg of acroant-conecut-knuckle-3r's +5, which is dead (a tie). Variant a (9 deg lateral-down) puts
  hub 1 on the deltoid origin, at the edge of user ruling 4 ("J1 seats back of the shoulder + acromion top only").

## 2. Every candidate: verdict and reason

| # | id | lens | verdict | reason |
|---|---|---|---|---|
| 1 | mirrork-kover-l2-knuckle-3r | A | **rejected (dead)** | Self-collision, measured in the real model: fast 143-203, parts 36-117 of 220. The underpass costs about +12 in-band against at most -3.9 reach. The judge confirms the kinematic cause on the ghost takes (1.1). Machinery traps kept (1.1). |
| 2 | foldlobe-conecut-knuckle-3r | A | **rejected (dead; duplicate)** | msub 0.02-1.45 deg on every inner take: 0 takes under the 5-deg rule. A duplicate of round 7's two-rise-lobe-pinknee-3r. |
| 3 | conetilt-j1-knuckle-3r | A | **rejected (dead; variant b duplicate)** | Ghost 261 / 7-8 overhead / cone 0 at both tilts. Hub 2 / K absorb the kinematic gain. Variant b = acroant (dead). Variant a is at the edge of seat legality. |
| 4 | ikring-thinstack-knuckle-4r | B | **PICK 1** | Reproduced to the digit: 299 / 13/28 / 9.33, held 32/71. Hardware is phi40's verified stack minus its coil. PHI 40 pre-registered (1.3). |
| 5 | ikring-distalshell-knuckle-4r | B | **PICK 3** | Same kinematics. A round shell distal of every mover (s 120: defect 2.8, in-band 0.999) removes phi40's bump and jam cliffs. Hangs on the short-knee re-centre. |
| 6 | ikring-mirrork-knuckle-4r | B x A | **merged into pick 3** (ring); host rejected | Its cone half needs the mirrored K, whose hub K sits on link 2's path on 5 of its 6 cone takes (1.1). Its ring is pick 3's. |
| 7 | weldk-overstrap-pinknee-3r | C | **PICK 2** | cx 0, 3 joints, overhead up from H1's 5. The judge's H1 calibration moves its projection to 22.5-27 (1.2). The only positive 3-joint lever this round. |
| 8 | mirrork-stackhorn-overstrap-knuckle-3r | C | **rejected** | The drive is priced against the skin, not against link 2. Hub K / crank lie on link 2's path on 84 ws + 68 clip takes of its host ghost, including 5 of the 6 cone takes (1.1). |
| 9 | weldk-crossover-kneeless-3r | C | **PICK 4** | cx 0, no knee. deltoid-crest-j3-3r re-seated (a2 +11 deg, the lead's J1). A knee-less control for pick 2 and the user's K1 preference. Kill at 28.46. |

## 3. Ranking

The rank is expected gap reduction vs the champion (75.94) x confidence x buildability. Every survivor has 0 passive
translations, so buildability is 1. The judge's expected gaps include the corrections of section 1.

| rank | id | joints | cx | judge expected gap | reduction | confidence | product |
|---|---|---|---|---|---|---|---|
| 1 | ikring-thinstack-knuckle-4r | 4 | ~48 | 10.5-12.5 (chain-only gate) | ~64.5 | 0.60 | 38.7 |
| 2 | weldk-overstrap-pinknee-3r | 3 | 0 | 22.5-27 | ~51 | 0.45 | 23.0 |
| 3 | ikring-distalshell-knuckle-4r | 4 | ~48 | 10-13 if the short knee holds >= 256 takes | ~64.5 | 0.35 | 22.6 |
| 4 | weldk-crossover-kneeless-3r | 3 | 0 | 24-29 | ~49 | 0.35 | 17.2 |
| - | mirrork-stackhorn (rejected) | 3 | 18.25 | >= 26 once the underpass is priced | ~50 | 0.10 | 5 |

Confidence reasons:

- **Pick 1:** the chain read reproduces exactly and the hardware is verified (phi40). The open items are the flood,
  the PHI 40 cell and the IK hindsight.
- **Pick 2:** the ghost bias is measured on H1, but the crossover E strap is unpriced, and so are a1 40.5 at 1 deg
  from the hub-2 cliff and follow at the line.
- **Pick 3:** the lead's knee was re-centred at lE 97 for a reason, and the s-120 shell is new hardware.
- **Pick 4:** the deltoid-crest basin died before. The a2 change is real, but it is a ghost.

## 4. Picks and their pre-registered gates (also in docs/concepts/catalogue.json)

1. **ikring-thinstack-knuckle-4r.**
   - Cells: primary PHI 40, axis 8.5 / 243, delta 3.5 (phi40's shell extent, coil deleted); control 12 / 235 PHI 40
     (phi40's own axis, IK mode); PHI 45 on envsel only.
   - Pass: <= 13.75 chain-only (95), with connected overhead >= 12/28 and held overhead >= 25/71.
   - Kill: > 16.0, connected overhead < 12/28, held overhead < 25/71, or more than 2 ring-added overhead takes under
     2 mm (the auditor's shell watch; the chain-only read has 0 of 5 under 2.33 mm).
   - Also report: least-phi at 8.5 / 243 (the unpowered control), the 2 mm reading vs the lead's 34.84 and phi40's
     47.16, T5, the dump, and the k-choice histogram.
2. **weldk-overstrap-pinknee-3r.**
   - Step 0: the H1 model re-seated with the crossover stack. Kill at step 0 if the E strap's own in-band (2-14 mm) on
     the taken fit poses falls below 0.80 once it clears link 2 by 0.15 mm wherever they overlap.
   - Pass: <= 26.0 frozen exact (beats H1 by > 1 at cx 0) with overhead >= 8/28 and follow >= 0.95.
   - Kill: > 27.20, or follow < 0.95.
   - Report the 2 mm shell of 205 / 235 / 262 by name.
3. **ikring-distalshell-knuckle-4r** (ikring-mirrork's ring hardware merged).
   - Step 1 kill: the short-knee psi = 0 wear loses > 6 of the lead's 262, or follow < 1.0.
   - Step 2 kill: shell clip in-band < 0.95, or > 2 shell-torso contacts on envsel at the chosen az_c.
   - Then pick 1's gates.
   - It imports pick 1's IK table and flood code; it does not rebuild them.
4. **weldk-crossover-kneeless-3r.**
   - Pass: <= 27.20 (beats every cx-0 design, with no knee).
   - Kill: > 28.46 (j3-neck-over-3r) or follow < 0.95.
   - Report the K1 reading: no cuff slides, redteam_gh misfit inside the 3 mm liner budget.

## 5. What happens next

- Picks 1 and 3 run in parallel; pick 3 waits only for pick 1's IK table code.
- Picks 2 and 4 share the crossover hub-3 stack. Pick 2's step 0 (the E-over-link-2 clearance) answers pick 4's first
  risk.
- Each claim gets a verifier and an alignment audit (shell counts, static vs connected, held overhead, unmodelled ring
  metal), as the planner's auditor watch asks.
- The loop's next round (302) is steered by whether PHI 40 holds 13/28 connected with ring metal. If it does, the
  ring's own Pareto question follows: the lowest-cx host under it, H1 + ring at cx ~25-30 (deltoid-ring-pinknee was
  measured at 8/28 on buildable axes, so the host must keep the lead's K window).
- The 3-joint cone is closed at the legal J1 by K-level levers (lens A, ideas 1-3 and 8): cone room for K exists only
  where link 2 sweeps. Only a K-free crossover (picks 2 and 4) touches it.
