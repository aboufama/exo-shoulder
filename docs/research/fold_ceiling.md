# The fold ceiling of the 3-active knuckle family (2026-10-17)

User, 2026-10-17: "i want higher scores! get to work and do it well!". Every verified leader of rounds 6-10 loses
the same workspace poses at the J2 fold. Reach is stuck at 0.725 on Bench(110,360): 261 of 360 workspace poses,
overhead 8 / 28. In-band (~0.89) and follow (1.0) are near target, so reach at the fold is almost the whole gap to
score 95 (gap <= 13.75).

This note works from the raw per-pose data. It asks three questions:

1. Which poses are lost, and to which wall?
2. What can this family reach at most, under the 5-deg fold margin and with every part clearing the skin?
3. Which change moves that ceiling?

It changes no rule and no verified row. Scripts and data are in `docs/research/fold_ceiling/`.

## Depth answers (written before the work)

1. **What a top mechanism / rehab-exo designer would do here that the brief does not ask for.**
   - Stop treating "the fold" as one wall. Split every lost pose into folded side vs stretched side.
   - Find which coordinate actually ends the stretched side:
     - the dyad margin;
     - stop B (a1max);
     - the K-drive stroke (dK_lim);
     - the K sub-dyad margin.
   - Write the window as a closed form in the few parameters that matter.
   - Separate the three questions a linkage designer keeps apart:
     - reachability: does the chain close?
     - conditioning: is it at least 5 deg from the singularity?
     - realisability: does every rigid part clear the skin at ONE level?
   - Measure realisability with the exact skin per part, not with a summary gap.
   - Check that the clip frames, where in-band is scored, even visit the region in question.
2. **The rawest material.**
   - The verified config's per-pose verdicts (`docs/alignment/remeasure/<id>_{bench,held}_perpose_claim.json`).
   - The posed render skin of every pose through the bench's exact signed distance (libigl).
   - The pose set itself (HG rotations, `pipeline/conformal/band_poses_wsf.b64`).
   - The leader's own IK (`D.ik`: law, K, knee, slide), re-run per pose.
   - Not the summary gaps, not the judge's wall table.
3. **Methods and tools.**
   - The spherical dyad's closure law, th = angle(J1, J3) in [|a1e - a2| + 5, a1e + a2 - 5], and its window width
     W = a1 + a1e_max - 10 (a1 <= a2).
   - The K sub-dyad's arc law, cos a1e = cos bk1 cos bk2 + sin bk1 sin bk2 cos(psiA + dK).
   - Exact window counting over all ruled seat pairs (a 0.5 deg cumulative histogram, the winners re-counted exactly).
   - An exact-skin K3 march per rigid part. It is a brute 1 mm march in one libigl call per pose, and it equals
     `concept_kit.requirement` to 0.0 mm on 900 test rays.
   - A sampling-based relaxation over the family (all hubs and link samples at one level each). It was calibrated on
     the leader and then tested in a paired kit model.
4. **What, other than me, shows it is right.**
   - The exact counts are re-derivable from the frozen per-pose dumps. The fold split equals the verified `why`
     (fold 88, slide 9, contact 2).
   - Every claim is shown on both Bench(110,360) and the 952 held-out workspace poses.
   - The relaxation was checked against an independent instrument: the paired kit model. That model refuted the
     relaxation's optimum (section 5).
   - A verifier should re-run `lost_poses.py`, `parking.py bench|held` and `parking_k.py` (each under 5 min locally).

## 1. The lost poses, from the raw per-pose data

Config: roller-longdyad-knuckle-3r verified. Shape fitted on Bench(60,160) and frozen; IK re-run on every pose. Script:
`lost_poses.py`, data in `lost_poses_roller-longdyad-knuckle-3r.json`.

**Kinematics of the leader:**

| quantity | value |
|---|---|
| J1 | bvec(95.4, 67.9) |
| J2 at rest | bvec(53.8, 38.1) |
| J3 | wdir(77.3, -8.2) |
| a1 (stop A) | 37.55 |
| a2 | 57.22 |
| a1max (stop B) | 58.77 |
| K dyad | bk1 26.0 / bk2 38.03, both at the model's lower clamps |
| dK_lim (roller drive) | 46.25 |

Window with the 5-deg margin:

- Folded wall: |a1 - a2| + 5 = **24.67**.
- Stop-B wall: a1max + a2 - 5 = 111.0. **It is never reached.**
- The taken poses stop at th 106.3: a1e 54.3, dK 45.6 of 46.25.
- **The effective stretched wall is the K DRIVE's stroke**: th <= a1e(dK_lim) + a2 - 5 = 106.6.

| Bench(110,360) exact, 360 workspace poses | count |
|---|---|
| taken | 261 |
| fold, stretched side (th 107.4-176.0, median 131) | **73** (5 between the drive wall and stop B, 68 beyond stop B) |
| fold, folded side (th 7.7-22.0) | **15** |
| knee / slide (R_tol) | 9 |
| contact | 2 |

**Where the lost poses are:**

- **Stretched side: internal rotation across the body.** 64 of the 73 have axial <= -90 (internal rotation >= 90
  deg) AND plane >= 60. Their elevation spans 30-165.
- Internal rotation swings the humerus-fixed J3 (lateral, d ~ 77) to anterior-medial, away from J1 on the acromion.
- **Folded side: scapular-plane abduction overhead.** All 15 are plane -20..45, elevation 90-165, axial -60..0.

By region:

| region | poses | taken | lost |
|---|---|---|---|
| overhead (elev >= 140) | 28 | 8 | stretched 9, folded 5, knee 4, contact 2 |
| across the body (plane >= 100, elev >= 40) | 68 | 20 | 48, all stretched |
| behind the back | 25 | 19 | 6, all stretched |
| the rest | 245 | 214 | stretched 16, folded 10, knee 5 |

**Held out (952 workspace poses):**

- Taken 649.
- Fold 261: stretched 211, folded 50.
- 177 of the 211 stretched are internal rotation >= 90 across the body.
- Knee 32; in-window other 10.
- Overhead: 18 of 71 taken.

**The same poses on every leader.** Of the roller's 88 fold poses:

- sidecar-longdyad loses 80;
- kneeless-roller loses 86;
- the old pin knee loses 86.

**The clip frames never visit either side.** All 110 clip frames (and all 202 held out) have th 41.3-96.4. In-band
is scored on clip frames only, so a wider window costs in-band only through the LEVELS that the new workspace poses
force on the parts.

**Geometric, margin artefact or clearance trade?**

- **Geometric** at these arcs and this drive: all 88 lie outside the closable window.
- **The margin** accounts for 22 of them.
  - At margin 0, 19 stretched and 3 folded would close. Held out: 47 + 16.
  - The 5-deg margin is the user's rule; it is not an artefact to buy.
- **The folded side is a clearance trade.** Hub 2's disc clears only 4 of the 15 folded poses at the leader's
  fitted level F2 = 62.0 mm. Held out: 21 of 46. Their median need is 71 mm.
- **The stretched side is NOT a hub-2 clearance trade.** Script `parking.py`: exact skin, the most favourable J2 ray
  with a1e scanned to +15.
  - **47 of the 73** stretched-lost poses put hub 2 within the leader's own level, 62.0 mm (clip band 52-62).
  - 58 of 73 at +4 mm.
  - Held out: **142 of 211**, and 159 at +4 mm.
  - Raising F2 has a cliff: at +4 mm, 26 % of clip frames take hub 2 out of band; at +6 mm, 76 %.

## 2. The closed-form window and the kinematic ceiling

One-sided knuckle (every leader): K stays on stop A while th <= a1 + a2 - 5, then opens.

- **Window** = [a2 - a1 + 5, a1e_max + a2 - 5] (a1 <= a2).
- **Window width** W = a1 + a1e_max - 10. a2 only slides the window.
- **K's reach** a1e_max is set by the drive's stroke dK through the K sub-dyad:
  cos a1e = cos bk1 cos bk2 + sin bk1 sin bk2 cos(psiA + dK).
  - Leader: psiA 71.7, dK 46 -> a1e 54.3, W = 81.8.
  - Stop B (bk1 + bk2 - 5) is never reached.

**At the leader's seats** (`kin_ceiling.py`): best placement of a window of width W, share of workspace poses inside.

| W | bench 360 | held 952 |
|---|---|---|
| 86.3 | 0.797 | 0.766 |
| 90 | 0.808 | 0.786 |
| 95 | 0.825 | 0.808 |
| 100 | 0.850 | 0.826 |
| 105 | 0.872 | 0.848 |

- The leader's own window [24.67, 106.6] holds 272: 261 taken + 9 knee + 2 contact.
- At the leader's width, the 360-pose optimum is a2 ~ 62 (+10 poses). The 160-pose fit bench put it at 57.2: the
  winner's curse already measured in docs/research/reach_attribution.md.

**Over every seat pair the user's ruling allows** (J1 on the back of the shoulder or the acromion top; J3 anywhere on
the arm; 247,860 pairs):

- The best window of width >= 80 holds **0.99** of the 360. Held out on the same seats: 0.97-0.99.
- With J1 restricted to el >= 50 and J3 lateral (d 45-110, |a| <= 60): 0.964 at W 86.3.
- With the leader's J1 and J3 free on the lateral arm: 0.867 at W 86.3, with J3 at wdir(45, 10).
- **There is no kinematic bound below 95 anywhere in the family.** The ceiling is not kinematic. That was a
  conjecture before; it is now counted exactly.

## 3. Realisability: every rigid part at one level, exact skin (`parking_k.py`, Bench(110,360) exact)

**Method.**

- Parts:
  - hub K, hub 2 and hub 3 (O20 discs; hub 3 read on the J3 ray);
  - link 1a and link 1b at mid-arc;
  - link 2 at 1/3 and 2/3 (discs of radius 6 = a 12 mm strap).
- Each part sits at its clip-frame maximum + d (d = 0 / 4 / 8 mm).
- A workspace pose counts only if it closes AND every part clears it.
- In-band column: the parts' mean clip-frame in-band at that level.
- Law: the ideal slaved one (K opens just enough).
- Not modelled: drive metal, knee and part collisions. So R_est is an UPPER estimate.

| config (leader seats) | window | in window | R_est +0 / +4 / +8 | parts in-band +0 / +4 |
|---|---|---|---|---|
| leader arcs, K 26 / 38 (calibration; verified 0.725) | 24.7-111.3 | 279 | 0.661 / **0.739** / 0.750 | 0.923 / **0.768** |
| **K dyad 28 / 50 (a1max 73), same a1 / a2** | 24.7-125.2 | 301 | 0.681 / **0.778** / 0.797 | 0.921 / **0.760** |
| a1 42 / a2 66, K 26 / 42.2 (a1max 63.2) | 29.0-124.2 | 297 | 0.692 / 0.783 / 0.797 | 0.814 / 0.695 (hub 2 floats in a few clip frames: clip max 118 mm) |

**Calibration.** At +4 the estimate is 0.739 against the verified 0.725: the knee, drive and collision checks remove
5 more poses.

**The long K dyad buys +0.039 (+14 poses) at the same parts' in-band.** Of the 40 newly closed poses, at the clip
level:

- hub K clears 36;
- link 1a clears 31;
- hub 3 clears 40;
- hub 2 clears 17 (26 at +4);
- **link 1b (K -> J2) clears 9** (30 at +4). It is the binding part.

**The binding coordinate is K's rotation.**

- A 28 / 50 K dyad reaches a1e 73 only by turning K 88.7 deg from stop A (77.6 deg for a1e 70).
- The leader turns K 46 deg.
- The round-9 re-cut roller flank caps at 55-57.5 deg at pressure angle <= 43. With it, a 28 / 50 dyad reaches a1e
  63.1, so th_hi = 115.3, about +16 poses in the window.
- Round 9 measured why that flank cannot be worn: its boss sits on the deltoid (88-94 contact poses).

## 4. Is score 95 reachable inside the family?

**Score 95.**

- At the leader's in-band (0.894), follow (1.0) and contact (0.005), score 95 needs reach >= 0.774: +17-18
  workspace poses.
- In general it needs ib14 + reach - contact >= 1.6625 (follow >= 0.95).

**Not provably impossible.**

- Kinematics allows 0.99 (section 2).
- At the leader's seats, every modelled part at one level admits **+14 poses** (R_est 0.778) at the same parts'
  in-band with a K dyad of 28 / 50.
- That is 0.725 + 0.039 = **0.764**, gap ~14.8, score ~94.6. It is just under 95, before the drive.

**Not reached either.**

- No configuration reaching the hard goal (frozen reach >= 0.80, overhead >= 14 / 28) was MEASURED here.
- The lever needs a K drive with a 60-90 deg stroke at pressure angle <= 43, its metal parked off the deltoid.
- No such drive exists in the repo:
  - rod RSSR 43;
  - roller flank 46 / 55-57.5;
  - direct cam pair ~26.
- So, with the drives that exist, the family's ceiling is the drive-stroke wall: about the 0.725-0.75 measured.

**The bound, stated.** For this family at these seats, every workspace pose beyond th = a1e(dK_max) + a2 - 5 is lost.
a1e(dK) is the K sub-dyad law above. Every pose up to there that all rigid parts clear at their clip levels can be
taken.

| K drive stroke (dK_max, deg) | reach estimate | th_hi with the 28 / 50 K dyad |
|---|---|---|
| 46 | 0.725, measured | - |
| 57.5 | 0.76-0.77 | 115 |
| 75-90 | 0.78-0.80 | 120-125 |

The 75-90 deg row is still below the hard goal's 0.80 at the same in-band. **Above ~0.80 the family needs a wider
window on the folded side too**, and there hub 2 IS the wall: only 4 of 15 clear.

## 5. The family-wide relaxation, and why it is not a bound (red team of my own instrument)

**The relaxation.**

- `req_map.py` builds the K3 requirement in 6000 directions for every pose of Bench(60,160) (fast cache).
- `hub2_bound.py` and `local_search.py` put every hub and link sample at one level, 12 + the (1 - tau) quantile of its
  clip requirements. They drop the workspace poses that do not clear.

**Calibration.** It reproduces the leader's fast reach exactly: 0.775 at a part floor tau 0.7, the leader's own
weakest parts.

**Its optima** (20,000 random designs plus local search):

- Near the leader (J1 bvec(108, 67), J3 wdir(89, 3), a1 40.8, a2 62.6, a1max 65.8, K 26.7): fast 0.844 at tau 0.7.
- Balanced arcs with J3 pointing up the arm (a1 ~ a2 ~ 46, J3 d 107-118): 0.85-0.89 at tau 0.8.

**Refuted by the paired kit model** (`kit_paired.py`: same members, same fit, the leader's axes vs the candidate's,
Bench(60,160) fast):

- The candidate is worse under every fitting policy:
  - quantile 1.0 / 0.97 / 0.95;
  - clip-derived joint stops +-0 / 15 / 30 deg.
- Gap 42-106 against the control's 23-62. Hub 2 in band 0.0-0.87 against 0.66-0.99. Link 2 floats.
- **Why the relaxation is optimistic:**
  - It DROPS workspace poses that do not clear. A rigid chain cannot drop them: they are contact, about 0.49 gap
    each against 0.28 for a fold loss.
  - It samples link 2 and the neck coarsely.
- The kit control itself does not reproduce the leader (26-32 fast against 13.19): it has no pin knee, no tilted J3
  and no greedy fit. So the kit is a paired instrument only.
- **Lesson for any planner:** a per-part parking relaxation that drops uncleared poses is not a reach bound. The
  exact one-level test of section 3, every part clearing every closed pose, is the one that agrees with the verified
  leader.

## 6. Red team

| attack | result |
|---|---|
| Fold margin read on another angle | The walls use th, the user's ONE metric. The 5 "law" poses at th 107-110 are the drive wall (a1e 54.3 at dK 46), not a margin reading. |
| Optimistic sampling | Every kinematic optimum is re-counted on the 952 held-out poses at the same seats and window (0.97-0.99 / 0.766-0.848). The exact parking is on the frozen bench AND held out (142 / 211 against 47 / 73: the same share, 0.67 / 0.64). |
| The brute march | Equals `concept_kit.requirement` to 0.0 mm on 900 rays (3 poses). |
| Hub-2 parking optimism | The J2 ray is the BEST of a1e + 0 / 3 / 6 / 10 / 15 per pose. The real law opens on a fixed schedule, so 47 is an upper count. |
| Hub 3 read on the J3 ray | The leader's J3 is tilted (b3) and offset, so hub3_ray / link 2 are approximations. Hub 3 never binds in section 3. |
| The relaxation | Its optima fail the paired kit test (section 5). It is reported as an instrument failure, not as headroom. |
| The pose that jams | The long K dyad's extra poses all sit at a1e 59-73. There K turns 77-89 deg: a drive at pressure angle <= 43 over that stroke is the unbuilt part. Without it the chain stops at the drive wall, a stop, not a jam. |
| Bench artefact | The fold split equals the verified `why` (88 / 9 / 2) pose for pose. The clip frames never leave th 41-96 on either bench. |

__SHIFT__

## 7. For the round-11 planner

The fold is two walls with two different causes, and both are now measured.

**Stretched wall: 73 of the 88 bench fold losses, 211 of 261 held out.**

- These are internal rotation across the body.
- The wall is the K DRIVE'S STROKE: dK 46 -> a1e 54.3 -> th 106.6. It is not stop B, and it is not hub 2.
- Hub 2 clears 47 of the 73 at its current 62 mm level (142 of 211 held out).
- At the leader's seats, a K dyad of 28 / 50 with every modelled part at one level admits +14 poses at the same
  in-band (exact; reach ~0.764, score ~94.6), IF K can turn 60-90 deg.
- So round 11 should screen K DRIVES with a 60-90 deg stroke at pressure angle <= 43 whose metal stays off the
  deltoid. Candidates are a K-on-K four-bar or a two-stage roller.
- Gate every drive with `parking_k.py` plus its own metal, never with a per-part relaxation that drops poses
  (section 5).
- Separately, the leader's window is mis-placed for the 360 / held poses (a2 57 -> ~62 is worth +10 poses
  kinematically): the env-polish should find it.

**Folded wall: 15 bench, 50 held.**

- These are scapular-plane abduction overhead.
- It IS a hub-2 clearance trade: hub 2 clears 4 of 15 at 62 mm and needs a median 71 mm. Leave it.

**Above ~0.80 reach**, the family needs both walls moved. That is the point where a 4th joint (pick1-type) or a
different J1 / J3 seat pair stops being optional.

