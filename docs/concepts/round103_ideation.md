# Round 103 (J3, track jump) ideation: judge and red team (2026-10-18 ~01:45 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). The real target is gap 0, and 95 (gap 13.75) at
low complexity. This round's bars (docs/concepts/ROUNDS.md "Round 103 plan"):

- PASS (pre-registered): policy (ii) <= 15, or >= 279 taken with <= 4 contacts, at a0 <= 20 (J0 stackable inside J1's
  footprint), or at a larger a0 only with hub 2's orbit clearing J0's O20 stack + 5 mm.
- KILL: policy (i) > 17.5 at every a0.
- Gate 0: a cell worse than 17.5 frozen exact dies with its number and its binding part.

Lead to beat: conecut-knee-knuckle-3r, verified 18.28 (score 93.35), reach 0.7278 (262/360), ib14 0.9012, contact 0.0106
(4 poses), complexity 18.5, ledger WATCH. Every candidate this round has 4 counted joints. The user prefers 3.

Six candidates came in: three relay realisations under the lead's frozen chain (lens 1) and three cap-pole null-space
cells (lens 2). All six have 0 passive translations and map every joint to a real part (O20 v5 hubs on MR117-2RS pairs,
MR63ZZ knee pairs, ISO 8734 dowel stops, 0.95 mm wire torsion springs).

After the determinacy rule, the duplicate check and the red team, **four are picked**:

- the three relay realisations, each closing one clause of lens 1's PASS rule with a real-metal number;
- cap-nullspace-4r, which merges its sprung MVP1 cell as the claim and the split elbow as an optional cell C.

**None is expected to beat the lead.** This round is closure work, not a leader hunt. It turns the planner's two open
4-joint levers into measured numbers so the 4-joint question can go to the user like-for-like.

Judge's scripts and logs:
`/tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/judge103/`
(`seatgap.py` + `seatgap.log` / `seatgap.json`, `skinray.py`). They reuse the proposer's `relay/relaylib.py` unchanged:
the frozen lead fit on Bench(60,160) fast, worn on exact Bench(110,360). Run local, niced, OMP_NUM_THREADS=1, one
process.

## 1. Red-team checks made by the judge

### 1.1 The relay ghost reproduces, but its stop window was fitted on the claim bench

The proposer's `asym.py` on its four policy-(ii) outputs (`relay/ii_*.json`) reproduces every quoted number to 0.01:

| seat (a0 / azu) | best window | ws taken / 360 | contacts | new takes | gap |
|---|---|---|---|---|---|
| 20 / 45 | [-29, +18] | 275 | 9 | 13 | 15.90 |
| 30 / 0 | [-46, +7] | 278 | 12 | 16 | 15.78 |
| 60 / 0 | [-21, +4] | 277 | 12 | 15 | 16.06 |
| 60 / 330 (clash-free) | [-14, 0] | 268 | 9 | 6 | 17.88 |

The relayed classes at a0 20 / azu 45:

- stretched: 14 clear, 9 into the skin;
- folded: 1 clear, 5 into the skin;
- J3-stop: 1 clear.

Two cautions for the modeller:

- **In-sample window.** The window [lo, hi] is the best of all q0 pairs over the 30 relayed poses of the claim bench
  itself: two parameters fitted on the poses that are then scored. Pick it on Bench(60,160) or the envelope bench, and
  claim on Bench(110,360).
- **Contacts must stay contacts.** `relay/log_a20.txt` prints "ii ws taken 278 contacts 4 gap est 13.63". That count
  treats the relayed poses that put metal into the skin as merely lost. A spring-centred J0 cannot refuse a relay, so
  those poses are contacts. The 15.90 count (`asym.py`) is the honest one, and 13.63 must never be quoted.

Policy (ii) misses the PASS (<= 15) by 0.78-0.90. Policy (i) is about 13.35 (279/360, 4 contacts), so the KILL does not
fire. **Lens 1 is therefore decided by the metal**, which is the realisability step the planner listed after the PASS.

### 1.2 A real hub 0 at the ghost's own seat exists only floating 30 mm over the skin

The proposer's clash probe stepped the azimuth by 30 deg from 0 and printed no row when no underside <= 80 mm cleared.
It therefore never tested a0 20 / azu 45, the ghost's best seat. The judge's probe (`seatgap.py`, the same method)
fills that gap:

- the O20 disc must clear the skin by 2 mm on every fit-bench pose;
- the chain's samples must stay >= 1 mm from hub 0 on all 376 lead-valid Bench(110,360) poses;
- `skinray.py` adds the skin radius along c.

| a0 | azu | r0 underside (mm) | over the median skin on c | hub 0 to hub 1 | clash clip / ws | binder |
|---|---|---|---|---|---|---|
| 15 | 45 | 59.5 | 14.5 mm (in band on 42 % of clips) | -3.3 (overlap) | 28 / 113 | hub K 101, crank 28 |
| 15 | 60-120 | 87.5-93.5 | 43 mm (azu 60) | +24 to +30 | 0 / 0 | - |
| **20** | **45** | **76.5** | **30.0 mm (0 % in band)** | +14.3 | **0 / 1** | L2 1 |
| 20 | 60-105 | 88.0-108.5 | 42 mm (azu 60) | +26 to +46 | 0 / 0 | - |
| 25 | 45 | 83.0 | 35.0 mm | +23.2 | 0 / 2 | hub 3, E |
| 25 | 60-75 | 94.5-104.0 | - | +34 to +44 | 0 / 0-1 | - |
| 25 | 90-105 | none <= 110 | - | - | - | - |
| 15-25 | 120-210 | J1 seat rule fails | - | - | - | - |

The proposer's rows for a0 12-40 at azu 0 / 30 / 270-330 clash with L1a / hub K / the crank / hub 2 on 42-105 clip
frames, or overlap hub 1 (`relay/clash.json`).

Along c, the skin sits at a median of 45-48 mm and a maximum of 51-57 mm over the fit poses. The O20 disc must ride
25-55 mm higher than that, because its 10 mm rim reaches over the deltoid that bunches under the acromion in abduction.

So the proposer's "no legal seat" is too strong: one realisation exists. Hub 0 stands on a post from the scapula handler
with its underside at 76.5 mm (crown 88.75), 30 mm over the skin, above the chain's own sweep (hub 1 passes 14.3 mm
below it). Link 0 then descends about 25 mm over the 20-deg arc to J1's housing, near 51 deg and inside the 60-deg ramp
rule.

**Estimate.** Hub 0's 80 samples are 0 % in band and link 0 adds ~15 samples, mostly out of band:
ib14 = 884 / (981 + 95) = 0.822, which costs +7.8. That gives **~23.7 frozen** on the 15.90 ghost: worse than the
3-joint lead and over the 17.5 bar.

A hub 30 mm proud also breaks the user's 1 cm goal in letter, so even a better number would need the user's say.

### 1.3 The wobble cell dies by arithmetic, even at 100 % clearance

The lead's part table (`rows/conecut-knee-knuckle-3r.json` frozen.parts_ib14) pools 981 samples, 884 of them in band
(0.901). The proposer's 1061 is 981 plus hub 0's 80.

- Hub 1 lifted 12.25 mm leaves the band entirely: every sample was >= 2 mm, so each is now >= 14.25.
- L1a's 8 samples ride up with hub 1.
- Hub 0 enters at hub 1's old level, in band.
- In-band therefore falls to (884 - 80 - 8 + 80) / 1061 = **0.826, which costs +7.4**.

The best kinematic gain is 23 takes at a0 10. At 100 % clearance with 0 new contacts (285/360) the gap is
10.83 + 1.00 + 7.42 = **19.25, above the lead's 18.28**. At the measured ~50 % clear rate of the side-by-side cell
(12 takes, 274/360) it is ~22.3.

**PASS reading.** "At least 279 taken with at most 4 contacts" is the planner's 95 arithmetic at ib14 >= 0.90. A cell
whose in-band falls must pass on gap <= 15. This is the judge's reading, and the lead may overrule it.

**Hub K.** Hub 0's rim, 17-19 mm from J1's axis, overlaps hub K's footprint (inner edge 15.5 deg) at the same height.
The modeller must check whether the azimuth where the relays happen (the proposer's best, azu 90-120) also keeps hub 0's
offset inside the sector the chain never sweeps.

### 1.4 The backbridge cell: in-band arithmetic

- The ghost at the only clash-free seat (a0 60 / azu 330, Teff 17) reproduces at 17.88. That is above the PASS and above
  the 17.5 bar before any metal is added.
- Hub 0 sits at r0 76 mm, 16-20 mm over the resting skin. The bridge rides 18.4-29.5 mm over the skin at its 8 stations
  (`relay/clash2.json`).
- Together they add ~140 out-of-band samples: ib14 884 / 1121 = 0.789, which costs +11.1. That gives **~29**, or ~25 if
  link 0 is sampled as sparsely as L1b.
- r0 76-105 is set by the behind-back and extension poses, so hub 0 becomes a new pinch point in poses the lead
  already takes.

### 1.5 Cap null-space: the numbers on file, and the determinacy rule

Which of the proposer's numbers are actually saved:

- **The 44.97 ghost and the 59.90 split-elbow ghost are not in any saved file.** The saved search outputs
  (`ns/rs_0.jsonl`, `rs_1.jsonl`, `grid_0.jsonl`, `grid_1.jsonl`) top out at **48.55** (a0 30, bearing 330, sB +1:
  reach 0.8125, ib14 0.518).
- **The 60.79 control has no saved output either.** `ns/ctrlf.log` ends in `ModuleNotFoundError: concept_kit`, so the
  control came from an unsaved run.
- **The sprung numbers are on file.** `spr.log`: J0 + J3 springs give 69.80 (reach 0.781, follow 0.967, ib14 0.326,
  hub 2 0.00 in band, q0 [-82, 84]). `spr01.log`: J0 + J1 give 100.37 (follow 0.517, q0 -177..153, bistable).

The determinacy rule decides how the cells are filed:

- The ghost chooses the null-space coordinate per pose by reading the skin. In the unpowered MVP1 nothing sets that
  coordinate: it sags (R17). Under the hard rule (no undetermined passive coordinate), the ghost is a **bound**, not a
  design.
- The claimable design is the sprung cell, so **cap-nullspace-sprung-4r is merged into cap-nullspace-4r as its claim
  cell**.
- That claim cell (69.80) is 9 points worse than the plain cap 3R it replaces (60.79). The class is decided unless the
  frozen exact sprung wear beats the control.

**Simplicity, recomputed with tools/simplicity.py:** ghost 28.5 (proposer 28.0), sprung 34.5. Every relay cell is 50.75
(the lead's record + 1 active x 25, 1 body, 1 joint, 1 spring, 2 made + 5 bought parts), which matches the proposer.

## 2. Verdicts

| candidate | verdict | reason |
|---|---|---|
| lead-relay-j0-4r | **PICK 1** | The lens's own cell. The ghost reproduces (15.78-15.90) but misses the PASS. Its real hub 0 exists only floating 30 mm proud at the ghost's seat (section 1.2). That one wear decides lens 1. |
| lead-relay-backbridge-4r | **PICK 2** | Not a duplicate: different metal, and it closes the PASS's "larger a0" clause. Ghost 17.88 is already over the bar; in-band arithmetic gives ~25-29. One wear. |
| lead-relay-wobble-4r | **PICK 3** | Closes the "inside J1's footprint" clause. The arithmetic kill holds at 100 % clearance (19.25 > 18.28); the hub-K clash is the open check. ~10 min plus one wear. |
| cap-nullspace-4r | **PICK 4** (merged) | The ghost alone leaves a coordinate undetermined in MVP1, so it is filed as the bound. The claim is the sprung cell. Its quoted 44.97 / 60.79 must be reproduced first (section 1.5). |
| cap-nullspace-sprung-4r | merged into cap-nullspace-4r (claim cell) | Same metal. The plan's gate 0 asks for ghost and sprung together, and their difference is the unpowered price. |
| cap-split-elbow-4r | not picked (rank 5); optional cell C of cap-nullspace-4r | One hand-set ghost, 59.90 fast quoted (not on file), against the control's 60.79. J2a 0.27 in band and 15 % self-collision, and it needs the same spring determination that cost the main cell 24.8 points. Run only if the main ghost beats the control frozen. |

No candidate is rejected for hardware:

- every joint is an O20 v5 hub or an MR63ZZ pair;
- every stop is an own-angle dowel;
- every spring is a catalogue-size torsion spring;
- there are 0 passive translations.

The wobble's wedge plate is 5-axis machined from solid, and this must be stated on the part.

## 3. Ranking

Score = (expected gap reduction vs the champion 75.94) x (confidence) x (buildability). All six have 0 passive
translations, so buildability ties.

| rank | id | expected frozen exact | reduction x confidence | note |
|---|---|---|---|---|
| 1 | **lead-relay-j0-4r** | ~23-25 (ghost 15.9) | ~52 x 0.6 = ~31 | the decisive cell of lens 1 |
| 2 | **lead-relay-backbridge-4r** | ~25-29 (ghost 17.88) | ~49 x 0.6 = ~29 | arithmetic robust |
| 3 | **lead-relay-wobble-4r** | ~22 (best case 19.25) | ~54 x 0.5 = ~27 | hub-K clash may add part losses |
| 4 | **cap-nullspace-4r** (+ sprung) | sprung 75-85 (ghost bound 52-60) | ~20 (bound only) x 0.5 = ~10 | MVP1 number below the champion's level is unlikely |
| 5 | cap-split-elbow-4r | 60-70 ghost, ~70-80 sprung | ~5 x 0.3 = ~2 | carried as optional cell C |
| - | cap-nullspace-sprung-4r | - | - | merged (pick 4's claim) |

## 4. Picks (appended to docs/concepts/catalogue.json, status "ideated")

1. **lead-relay-j0-4r.** Lead note:
   - Wear the ghost's own seat (a0 20, azu 45) with a REAL O20 hub 0 first. The judge's probe finds it clears the chain
     only floating at r0 76.5 mm, 30 mm over the skin and 0 % in band. Expected ~23-24 frozen.
   - Pick the stop window on Bench(60,160), never on the claim bench.
   - Count relayed skin hits as contacts.
   - Close lens 1 if the result is > 17.5.
2. **lead-relay-backbridge-4r.** Lead note:
   - In-band first: hub 0 at r0 76 mm and the bridge at 18-30 mm are out of band on every clip frame (ib14 ~0.79,
     +11 on the 17.88 ghost).
   - Wear once with the metal and close if > 17.5.
3. **lead-relay-wobble-4r.** Lead note:
   - Arithmetic kill first: hub 1 lifted 12.25 mm leaves the band (ib14 0.826, +7.4), while 23 takes at 100 %
     clearance buy at most 6.4, so the best case is 19.25 > 18.28.
   - Check hub 0's rim against hub K at the relaying azimuth.
   - Close in <= 30 min.
4. **cap-nullspace-4r** (claim = sprung J0 + J3 cell; ghost = bound; optional cell C = split elbow). Lead note:
   - Reproduce the plain cap 3R control (60.79) and the ghost (44.97) on the repo model first. Neither is in a saved
     output: the search best on file is 48.55, and the control log crashed on its import.
   - Then wear the sprung cell (69.80 fast on file) frozen exact with the bidirectional flood.
   - If it stays above the control, close the cap-pole null-space class with both numbers and the unpowered price.

## 5. What the picks are expected to show, and what comes next

All four are expected to die at gate 0. Together they close both 4-joint levers the planner left open:

- **Relays under the lead.** The ghost's relay gain is 2.4 points (13 clear relays, 5 new contacts). Every real J0
  costs more than that in in-band:
  - floating side seat +7.8;
  - coaxial stack +7.4;
  - remote bridge +11.

  A spring-centred relay therefore cannot improve the 3-joint lead at these seats with O20 hardware. Expected numbers:
  ~23 / ~22 / ~27 frozen against 18.28.
- **Null-space at the cap pole.** The clearance ghost moves the binder from hub 2 to the back-seat J0 and the links.
  The realisable spring determination is worse than the plain 3R (69.80 vs 60.79 fast).

With these numbers on file, the 4-joint answer for the user is like-for-like:

- the best realisable 4-DOF rows stay minarc-stop-knuckle-4r (18.40 polished / 19.54 verified, cx 32.5) and
  arm-parked-knee-4r (26.71, cx 32.25);
- this round adds 4-DOF numbers of ~22-29 at cx 50.75, and the null-space at cx 34.5 is far behind;
- the 3-joint lead stays 18.28 at cx 18.5.

**For the next planner (not this round's lever).** The 95 line needs +17 takes at ib14 >= 0.90. The lead's 73 stretched
losses sit at the K drive's stroke wall (dK 52.6 of the 57 cap). A relay buys 13 of them at best, and only with
zero-size metal. The remaining reach on this chain is the knuckle drive's stroke inside the hubs it already has. That is
a main-track question (the knuckle drive closures stand on this track); the next planner should weigh it against the
measured caps.
