# Round 102 (J2, track jump) ideation: judge and red team (2026-10-17 ~21:35 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). The real target is gap 0, and 95 (gap 13.75) at
low complexity. Gate 0 bar for this round (docs/concepts/ROUNDS.md "Round 102 plan"): <= 17.5 frozen exact on
Bench(110,360) with <= 4 contacts (lens 1: reach >= 0.80 or gap <= 15); a cell worse than 17.5 dies with its number and
the binding part.

Lead to beat: conecut-knee-knuckle-3r, verified 18.28 (score 93.35), reach 0.7278 (262/360), ib14 0.9012, contact
0.0106, complexity 18.5, ledger WATCH. 95 needs 279/360 at the lead's ib14 (planner, corrected).

Nine candidates came in: two from lens 0 (the instrument), four from lens 1 (virtual J2), three from lens 2 (plain crest
J3). All nine have 0 passive translations and map every joint to a real part (O20 v5 hubs, MR63ZZ knee pairs, O2 dowel
stops). After the duplicate check, the track rule and the red team, **two are picked, both from lens 1**: the open
four-bar (merging lens 0's instrument-placed four-bar as a measured cell) and the slaved elbow (merging the base-tethered
variant). Neither is expected to pass the 17.5 bar; they are the formal gate-0 numbers lens 1 owes the J3 closer's
ceiling statement and the 4-joint question to the user. The one candidate with a credible number near the lead,
cap-plateau-knuckle-3r, is a knuckle-drive variant and is **routed to the main track** (track rule, section 6).

Scripts and logs for the judge's checks:
`/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge102/`
(`cellcheck.py` / `cellrelax.py` + `relax_3.log` / `relax_4.log`, `antip.py` + `antip_5.log` / `antip_6.log`, `ulaw.py`,
`slavechk.py`, `j2exit.py` + `j2exit_60.log` / `j2exit_110.log`). They reuse lens 1's proxy instrument unchanged
(`.../scratchpad/rp4/opt.py`, `anch.py`: K3 march on pin rays and strap centre lines, Bench(60,160) fast cache, hubs
weighted 79 samples; kinematic reach on Bench(110,360) ws at the 5-deg th margin and transmission >= 30). Proxy
calibration (lens 1): the plain cap-pole 3R reads 36.6 on this proxy and 56.40 frozen exact (T-0 control), so add about
20 to any proxy gap. Local only, niced, OMP_NUM_THREADS=1, <= 2 processes.

## 1. Red-team checks made by the judge

### 1.1 cap-cell-fourbar-j2-3r: the instrument's in-band cells cannot host the four-bar

The claim: two cells near the J2 axis are in band (link 1 toward J1, link 2 at 45 deg toward J3), the triangle bound
W <= 2 (d(J1, A0) + d(A1, J3)) = 124 >= 110 makes them "compatible" with the W110 window, so pins there keep the
ghost's 14.75.

- **The link-1 cell cannot hold two O20 pins.** A0 and B0 at 24-34 deg from J1 within +-20 deg of azimuth are at most
  **22.05 deg** apart, and only at opposite corners (24 / -20 vs 34 / +20). Two O20 discs side by side need
  2 asin(10 / r) = 22.2 / 20.6 / 19.2 deg at the 52 / 56 / 60 mm hub level; the model's PINSEP is 22.
- **The bound is necessary, not sufficient.** 30000 random four-bars with all four pins in the stated cells (a1 45-62,
  a2 52-68, home th 30-110, both closure branches; lens 1's `kin_g`): 26291 assemble with a window, **W max 98.1 (p90
  52.9)**, kinematic reach max 0.811, only 10 layouts >= 0.78 and **none with pin separations >= 22**. With separations
  >= 20: **one layout, W 30.4, reach 0.339**. Both cranks are constrained, so a short-pinned four-bar's window falls far
  below the triangle bound.
- **Relaxing the cells does not escape lens 1's binder.** Two more 30000-layout draws (azimuth +-45 / 22-36 deg from
  J1 / coupler pins 25-50 deg from J3 at 0-75 deg round; and +-60 / 22-40 / 22-55 at 0-90), separations >= 20 and
  crossing angle >= 8: 1537 / 3309 layouts, W max 85.8 / 91.3, one layout each at reach >= 0.78. Lens 1's skin proxy
  on the 25 best by reach of each draw: **best proxy gap 48.29** (reach 0.572, ib 0.745) and **42.86** (reach 0.711,
  ib 0.660), against lens 1's near-isogram ES best 33.67 and the plain cap 3R's 36.6. In every one of the 50, a
  coupler pin, crank B or the coupler reads 92-153 mm or escapes the 220 mm march (400). Examples: the 48.29 cell has
  B1 102 / crank B 97 / coupler 93 mm. The only reach-0.80 layout (W 91.3) has A0 109, B1 153 and coupler 142 mm, ib
  0.261, proxy 73.89.
- So the cap-cell placement is the measured-dead corner of lens 1's own search: the coupler pin farther from J3 (or
  crank B / the coupler strap) inherits the J2 zone's 96-124 mm skin, as lens 1 found in every near-isogram optimum.

### 1.2 antiparallel-medial-fourbar-3r: the kinematics reproduce, the metal has no skin to sit on

- th at J1 bvec(-35, 30), J3 wdir(40, 40) on Bench(110,360) ws: p0 / 5 / 50 / 95 / 100 = 86.6 / 107.0 / 140.5 / 166.1 /
  177.7. A 50/130 window [85, 175] closes **356/360 ws and 108/110 clips**: the proposer's kinematic claim reproduces.
- Four-bars with the proposal's pin cells (A0, B0 22-25 deg from J1; A1, B1 22-30 deg from J3; 20000 random): W max
  63.4 (50.5 with separations >= 20). Reach still reaches 0.817 because the th spread is narrow. Lens 1's proxy on the
  12 best: **79.95-89.44, ib 0.15-0.21**. Hub 1 reads 112 mm (0.56-0.91 in band), J3 94 mm (0.52-0.74). Every pin,
  crank and the coupler reads 149-400 mm (400: no skin within the 220 mm march, so the part's ray leaves the body).
- Wider cells (<= 40 deg from J1, <= 50 deg from J3): W up to 98.1 and kinematic reach up to 0.98, but proxy 62.20-76.36
  at ib 0.14-0.28. J3 itself reads 400 on those taken sets.
- Kinematic reach is not the limiter at any legal seat (a 90/90 dyad closes [5, 175]); the metal is. The seat passes the
  coded SEAT_OK (x = -0.71, posterior), but it is a medial supraspinous-fossa seat with hub 1 111-125 mm from GH.
  The th spread there also runs to 177.7 deg, next to the J1 / J3 antipodal gimbal lock, where joint rates diverge.

### 1.3 cap-plateau-knuckle-3r: the U-law kinematics reproduce; the hub-2 trade it reports does not beat the lead

- U-law a1 = clip(max(40, th - 62), 40, 62), a2 70, margin 5 (`ulaw.py`, Bench(110,360)). At wdir(90, 10):
  **295/360 ws (folded 33, stretched 32), 99/110 clips**, the proposer's numbers exactly. At wdir(92, -9) it is 285.
  The plain 50.2/60.3 reads 281 (the planner's number reproduced), and a fixed 60/70 reads 311-318.
- So the U-law spends ~23 kinematic poses against a fixed 60/70 dyad to pull hub 2 in (proposer: hub-2 p90 77 vs
  127 mm).
- The proposer's own trade, priced at the lead's terms:
  - Hub 2 at level 79: 271 ws clear but 52/394 in band. With hub 2 at ~10 % of samples, ib14 falls ~0.06 and reach is
    <= 0.753, so the gap is ~21 before any other metal.
  - Hub 2 at level 63-67: 0.69-0.70 in band but 206-235 ws clear, so the gap is >= 25.
- It beats 18.28 only if a J1 own-angle stop cuts hub 2's tail at < 10 lost ws. The planner's stop-box scan says no:
  a 12 mm band >= 0.8 keeps <= 100/360. So does crest-stopcarved's measurement: the tail is not separable in joint
  space.
- Honest expectation 19-23, confidence of beating the lead ~10 %, complexity unchanged (18.5). It is a knuckle law /
  flank variant and is routed to the main track (section 6).

### 1.4 The slaved-elbow seeds reproduce; "every part <= 75 mm" holds for one seed only

Re-evaluated with the proposer's `anch.py` unchanged (`slavechk.py`):

| seed | proxy (claim) | reach_kin | follow110 | ib | binding parts (level mm / in band) | (-75, 60, +60) closed |
|---|---|---|---|---|---|---|
| arm 1 | 41.84 (42.08) | 0.722 | 0.918 | 0.659 | all <= 75: A1 75 / 0.00, crank A 72 / 0.32, A0 62 / 0.43 | no |
| arm 2 | 48.36 (48.04) | 0.561 | 0.736 | 0.755 | A1 400, crank A 201, coupler 201 | no |
| tether 1 | 44.10 (44.07) | 0.672 | 0.918 | 0.687 | A1 143, B1 159, coupler 217 | yes |
| tether 2 | 47.61 (47.38) | 0.703 | 0.927 | 0.621 | B1 129, crank B 139, coupler 125 | yes |

- Arm 1 is the one structural novelty in lens 1: no part enters the J2 zone. Its in-band still equals the plain cap
  3R's 0.653, because A1 and crank A swing 0-0.32 in band. The elbow's per-pose spread sets ib, not a high binder.
- The arm cell loses the binder pose instead of serving it, so its reach is a closure question, not a skin question.
- The tether keeps the binder but puts its coupler pin B1 back in the J2 zone (129-159 mm), lens 1's binder again.

### 1.5 antcrest-pinknee-3r: the hub-2 tail reproduces on the fit bench

Plain closure at margin 5, J2-ray skin exit (kit K3 march, `j2exit.py`), Bench(60,160) fast:

| cell | ws closing | J2 exit p5 / 50 / 95 / max (ws) | > 75 mm ws | > 75 mm clips |
|---|---|---|---|---|
| cap control 50.2/60.3 | 128/160 | 51 / 60 / 96 / 116 | 20 (0.156) | 5/60 |
| antcrest A (55, 62) / wdir(98, 5) 50/58 | 136/160 | 50 / 59 / 77 / 140 | 9 (0.066) | 3/60 (max 165) |
| antcrest B (55, 62) / wdir(102, 18) 52.5/56 | 138/160 | 47 / 58 / 76 / 114 | 8 (0.058) | 0/60 (p95 66) |

The proposer's 8/160 and 51-66 clip spread reproduce. Bench(110,360) (exact path, the verification poses incl. the
|axial| >= 150 region Bench(60,160) under-samples: 2 closing poses there) is in `j2exit_110.log` (section 7).

## 2. Verdicts

| # | id | lens | active / passive / transl. | verdict | reason (measured) |
|---|---|---|---|---|---|
| 1 | **remote-pole-fourbar-j2-3r** | 1 | 3 / 3 / 0 | **PICK 1** (absorbs cap-cell-fourbar-j2-3r as the measured cell B) | The round's lens-1 mechanism (planner's id). Open spherical four-bar J2, six O20 pins, no metal on the J2 ray. Measured by its proposer on the proxy: 33.67-35.72 (reach_kin 0.68-0.79, ib 0.65-0.79) vs the plain cap 3R's 36.6, so ~50-56 frozen. The far coupler pin reads 96-124 mm at the binder poses. Picked for the formal gate-0 number with the 10-minute binder test first. |
| 2 | cap-cell-fourbar-j2-3r | 0 | 3 / 3 / 0 | **MERGED** into pick 1 as cell B, not to be modelled | Same mechanism, seats and model file as pick 1; differs only in the pin box. Judge (1.1): the link-1 cell holds two O20 pins only at its corners (22.05 deg max); in-cell W max 98, 1 of 30000 layouts with separations >= 20 (W 30); relaxed cells 42.86-48.29 proxy with the far coupler pin / crank B / coupler at 92-153 mm. |
| 3 | **cuff-slaved-elbow-fourbar-3r** | 1 | 3 / 3 / 0 | **PICK 2** (absorbs scapula-tether-elbow-3r as cell B) | The only lens-1 topology whose best seed keeps every part <= 75 mm (judge reproduced 41.84). Its deficit is closure (reach_kin 0.722, follow 0.918, binder pose lost) from a 3 x 420 s search with sparse random pools, so it is under-searched; a 20-min CMA is new knowledge. Expected ~58-62 frozen; low confidence. |
| 4 | scapula-tether-elbow-3r | 1 | 3 / 3 / 0 | **MERGED** into pick 2 as cell B | Same 4R-path-with-slave scaffold (`anch.py` mode 'tether'), slave crank grounded on the base. Reproduced 44.10 / 47.61; its coupler pin B1 sits back in the J2 zone (129-159 mm). |
| 5 | cap-plateau-knuckle-3r | 0 | 3 / 3 (K + knee) / 0 | **ROUTED to the main track** (track rule), not picked here | The lead's chain at the cap pole with a U-law; knuckle drive and law re-synthesis are the main track's (plan: "must not reuse the knuckle drives"). Judge reproduced 295/360 ws, 99/110 clips. Its own hub-2 trade prices at ~19-23 (1.3). Recommended as main round 14's seat cell, hub-2 tail gate first. |
| 6 | antiparallel-medial-fourbar-3r | 0 | 3 / 3 / 0 | **REJECTED on measurement** (survivor of the hardware check, ranked last) | Kinematics reproduce (356/360, 108/110), but four-bars in its pin cells read 62-89 on lens 1's proxy (ib 0.14-0.28): pins, cranks and coupler at 149-400 mm, hub 1 at 112 mm, J3 at 94-400 mm (1.2). Medial seat near the J1/J3 antipodal gimbal lock. |
| 7 | cap-crest-j3-plain-3r | 2 | 3 / 0 / 0 | **DUPLICATE** of the queued deltoid-crest-j3-3r (plan: "lens 2's seed, re-measure at O20") | Its numbers ARE that O20 re-measure: round-4 seeds 75.75 / 91.12 fast at O20 / margin 5 (vs 26.35 at O15 / margin 10), best crest cell 62.80 fast (hub 2 0.00 at 99 mm), hub 3 on the crest 0.00-0.27 in band. Forwarded to that entry's screen (section 6). |
| 8 | antcrest-pinknee-3r | 2 | 3 / 2 (cuff knee) / 0 | **DUPLICATE** of crest-knee-3r (round 4: H1's pin knee at the crest seats), at a new basin | Same morphology and model (skin-normal-3r-pin-knee.py at crest seats). Its fold gain (-12 to -16 of 220 vs H1) is real and the tail reproduces (1.5), but by its own arithmetic it cannot make the bar: H1 fast 23.64 - 5.5-7.3 = 16.3-18.1 at best before the tail (+2-5) and a knee re-fit (H1's knee collides 182-196/220). A possible complexity-0 point over H1's 27.2; forwarded to crest-knee-3r for the complexity phase. |
| 9 | crest-stopcarved-3r | 2 | 3 / 0 / 0 | **REJECTED on measurement** (the stop lever is closed twice) | Plain O20 3R + own-angle O2 dowel stops (real parts, legal own-angle stops). Measured on the real kit: 51.28 fast at best (J2 stop alone), 54.97 with three stops; the planner's stop-box scan closes the same lever at the cap pole (band >= 0.8 keeps <= 100/360). The high-exit poses are not separable by single-joint ranges. A formal run re-measures a known number. |

Hardware and determinacy (CLAUDE.md "Manufacturable joints only"):

- Every joint is a catalogue part at its size: MR117-2RS O20 v5 hub stacks (all pins, "Keep O20 only"), MR63ZZ pairs
  for the unsensed cuff knee (antcrest, cap-plateau), ISO 8734 O2 440C dowels in arc grooves for own-angle stops.
- **No passive translation anywhere.**
- No undetermined coordinate:
  - the four-bars' B0, A1 and B1 are set by the loop closure (spherical Grubler 3 for the chain, 1 for the loop);
  - the slaved elbow's coupler spin is the root of angle(B0', B1) = rho (arm cell) or angle(B0, B1) = rho (tether),
    and the 2R closure then fixes phi and A0;
  - the knuckle's K is slaved by the lead's verified drive;
  - the cuff knees are set by the host's closure.
- The five-bar tether has two assembly branches. Its connected() flood must reject a branch change, as must the slaved
  elbow's spin root (jump > 10 deg).

## 3. Ranking

Score = (expected gap reduction vs the champion 75.94) x (confidence) x (buildability: fewer passive translations first;
all nine have 0):

| rank | id | expected frozen exact | reduction x confidence | note |
|---|---|---|---|---|
| - | cap-plateau-knuckle-3r | 19-23 | ~55 x 0.5 = ~27 | routed to the main track (track rule) |
| 1 | **remote-pole-fourbar-j2-3r** (+ cap-cell) | ~50-56 (proxy 33.7-35.7 + ~20) | ~23 x 0.6 = ~14 | the round's lens-1 gate; cheapest decisive test on the real model |
| - | crest-stopcarved-3r | 51-55 (kit fast 51.28-54.97) | ~23 x 0.8 = ~18 | death already measured on the real kit; a run adds no knowledge |
| - | antcrest-pinknee-3r | 22-30 | ~50 x 0.3 = ~15 | duplicate (crest-knee-3r); cannot make the bar by its own arithmetic |
| 2 | **cuff-slaved-elbow-fourbar-3r** (+ tether) | ~58-62 (proxy 41.8 + ~20) | ~16 x 0.4 = ~6 | a structurally new lens-1 topology; its proxy comes from a sparse 3 x 420 s search |
| - | cap-crest-j3-plain-3r | 55-63 fast | - | duplicate (deltoid-crest-j3-3r, queued) |
| - | antiparallel-medial-fourbar-3r | ~80 (proxy 62-89) | ~0 | judge-measured dead |

The formula alone would put crest-stopcarved and antcrest above pick 2. They are not picked, for two reasons:

- crest-stopcarved's number is already a real-kit measurement of a lever closed twice (section 2, row 9).
- antcrest is a duplicate whose ceiling (>= 16.3 fast before its tail and knee costs) misses the bar by its own
  arithmetic.

Pick 2's value is information:

- it is the only lens-1 class whose binder is not the J2 zone;
- its single proxy number comes from a search its proposer calls sparse;
- the J3 closer's ceiling statement needs a real-model number for it.

## 4. Picks (appended to docs/concepts/catalogue.json, status "ideated")

1. **remote-pole-fourbar-j2-3r** (+ cap-cell as measured cell B). Lead note:
   - Run the 10-minute decisive test first. If no layout with W >= 85 keeps BOTH coupler pins, crank B and the coupler
     strap <= 75 mm at (-75, 60, +60), (0, 150, 0), (30, 150, 0) and (0, 105, 0), close the lens on that number.
     The judge drew 90000 cell and relaxed layouts and proxied the 50 best by reach; none kept all four parts
     <= 75 mm.
   - Otherwise run gate 0: a 20-min CMA on the near-touch gap from s1 / s2 / s3, then frozen exact Bench(110,360) with
     the flood, transmission >= 30 and the Jacobian rank.
   - Report overhead / 28, the min th margin (in the coupler's effective J1-J3 angle) and cx 15.0-16.0.
2. **cuff-slaved-elbow-fourbar-3r** (+ tether as cell B). Lead note:
   - The risk to test first is closure, not skin. A 20-min CMA must lift ws closure to >= 0.80 and follow to >= 0.95
     while every part stays <= 75 mm (only arm seed 1 does: 41.84, reach 0.722, follow 0.918, binder (-75, 60, +60)
     lost).
   - It must also raise A1 / crank A above 0.00 / 0.32 in band.
   - If the CMA cannot beat the plain cap 3R's proxy 36.6, close it on that number with the binder table.

## 5. What the picks are expected to show

Both are expected to die at gate 0. Each then closes a lens-1 class with a real-model number and its binding part:

- pick 1: the open four-bar, whose far coupler pin binds;
- pick 2: the slaved elbow, which loses closure.

With the planner's 668 revolute-J2 configs, this is the evidence the J3 closer needs to write the J2-on-axis bound to
FINDINGS as the 3R ceiling at legal seats and to put the 4-joint question to the user. If either passes, it is the first
non-knuckle number under the bar, at complexity 15-16 against the lead's 18.5.

## 6. Forwarded and routed (no new catalogue rows)

- **Main track, next planner <- cap-plateau-knuckle-3r** (complete proposal in this round's candidate list).
  - Judge reproduction: U-law 295/360 ws, 99/110 clips (wdir(90, 10)); 285 at wdir(92, -9).
  - Gate it on the hub-2 tail first: the share of taken poses with hub 2 within 12 mm of its fitted level must be
    >= 0.8 with <= 10 ws lost to a J1 own-angle stop.
  - The proposer's own trade prices it at ~19-23 without that.
- **deltoid-crest-j3-3r (queued) <- cap-crest-j3-plain-3r's numbers**, the O20 / margin-5 re-measure:
  - round-4 seeds 75.75 / 91.12 fast;
  - crest wdir(108, -15) 86.80, wdir(100, 15) lay 0 69.66;
  - best cap-pole crest cell bvec(55, 62) / wdir(98, 5) 50/58: 62.80 (hub 2 0.00 at 99 mm);
  - hub 3 on the crest 0.00-0.27 in band at wd 108-116;
  - hub 1 / hub 3 collisions at small th on 7-12 poses;
  - new crest binders (30, 149, -59), (30, 124, -54), (30, 135, -45), with the J2 ray off the body or at 133-218 mm.

  That screen should start from these numbers and expect to close on them.
- **crest-knee-3r (ideated) <- antcrest-pinknee-3r's basin** for the complexity phase, as the one cx-0 cell with a
  measured fold gain over H1:
  - seats J1 bvec(55, 62), J3 wdir(98-104, +5..+18);
  - fold loss 20-24 of 220 vs H1's 36;
  - hub-2 tail 8-9 / 160 ws (1.5);
  - H1's knee collides on 182-196 / 220 and must be re-fit.
- **FINDINGS (for the J3 closer)**:
  - Kinematic reach is never the limiter at a legal seat: the antiparallel seat closes 356/360 with a 50/130 dyad, and
    a 90/90 dyad closes everything.
  - The own-angle stop lever is closed (crest-stopcarved 51.28 / 54.97 fast; the planner's stop-box scan).
  - The instrument-cell four-bar is infeasible as stated (1.1).

## 7. Bench(110,360) J2-exit for the antcrest seats

(pending `j2exit_110.log`; appended when the exact-path run lands)
