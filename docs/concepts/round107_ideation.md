# Round 107 (J7, track jump) ideation: judge and red team (2026-10-18 ~18:30 UTC)

Target: bench score >= 90 (gap <= 27.5; score = 100 (1 - gap / 275)). The lead is already past it; the real targets are
gap 0, and 95 (gap 13.75) at low complexity. The plan is docs/concepts/ROUNDS.md "Round 107 plan" (40bf0ec). No bench,
judge or kit file changed since round 106: no number below moved because the measurement changed.

**Lead to beat:** conecut-knee-knuckle-3r, verified 18.28 (score 93.35), frozen exact Bench(110,360), held 22.38,
cx 18.5, 3 joints. **Best 4-joint (a user option, never a lead):** offset-shortcar-relay-4r 14.76 (94.63), held 17.77,
cx 52.5. **Champion** (the ranking's reference): spherical 3R 75.94 on Bench(110,360) exact.

**Candidates:** nine. Every joint maps to a real part (O20 / MR117-2RS hubs, MR63ZZ knee pairs, ISO 8734 dowels and
pins, a plain curved slide on a Ti shell, a constant-force strip); all nine have 0 passive translations and no
undetermined passive coordinate (K is slaved by its drive; the relay is spring-held on a dowel with an own-angle stop).

- Lens A (relay-95): underpass-bridge-relay-4r, lugcoil-lbracket-relay-4r, phi40-thinstack-relay-4r.
- Lens B (one-stage K drive): onetooth-slowlaw-knuckle-3r, onetooth-desmo-knuckle-3r, shortk-onetooth-knuckle-3r.
- Lens C (long dyad over the top): longtop-dyad-3r, longtop-farhub2-3r, longtop-gradedk-knuckle-3r.

**Outcome: four picks, two merges, one family closed by measurement.**

1. onetooth-slowlaw-knuckle-3r (lens B, 3 joints, cx 10.25-11.0), with onetooth-desmo merged as its spring-free cell D.
2. underpass-bridge-relay-4r (lens A, the route to 95 at 4 joints), re-specified at its supports; phi40's PHI 40 cell
   folded in.
3. phi40-thinstack-relay-4r (lens A fallback, run in parallel), with lugcoil-lbracket merged as its PHI 35 cell.
4. shortk-onetooth-knuckle-3r (lens B, re-seated K), its tooth-sweep scan as step 0.

The long-dyad family (all three lens-C rows) is dead at step 0 and is not given a slot: the proposer's ghosts and family
scan, plus the judge's frozen exact wear (section 1.6), put it far above the 27.20 kill line.

**The judge's main finding.** The under-pass's 14.59 (the ideal-relay bound on envsel) was read with the bridge
floating: its supports were never sampled. Measured here, the E strap sweeps +6.4..+49.0 deg (rel the pad) in the arm
frame at the relay station, so an anterior end block at the arc end is crossed by E, and a 4 mm posterior Ti block puts
metal into the posed skin of the 259 / 264 / 265 class. The design survives only with a <= 2 mm posterior support on a
soft pad, and the anterior support has no free place: outside E's envelope the raised shell meets the torso at envsel
119 (-1.39 mm, one contact), so it either pays that contact or cantilevers on a stiffened section (section 1.2-1.3).
Judge estimate 13.5-14.0 on the claim bench, against the 13.75 line.

## 1. Red-team checks made by the judge

All judge reads are on the fit bench and envsel (the selection bench); none on Bench(110,360) or held-out poses.
Scripts: /tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/r107j/ (eaz.py,
blocks.py, blocks2.py; outputs eaz.json, blocks.log, blocks2.log, longtop_frozen.json).

### 1.1 The proposers' relay numbers reproduce from their own logs

From /tmp/claude-0/-home-user-exo-shoulder/55c580fc-1103-56e5-9e17-3e425f438838/scratchpad/r107a/ (envsel exact, seed 2,
chain-only gate, lug coil, ds 31 / delta 4.5 / carw 14):

| reading | gate | ib14 chain / pooled | reach | contacts | jams |
|---|---|---|---|---|---|
| bump control, PHI 35 | 15.61 | 0.8898 / 0.9132 | 0.7861 | 13 | 0 |
| lever (b), per-pose window | 15.82 | 0.8877 | 0.7861 | 13 | 0 |
| band 8 + bump 1.2 + tsh 1.0 + lean (lugcoil) | 15.21 | 0.8938 / 0.9167 | 0.7861 | 13 | 0 |
| same, delta 5.0 | 15.68 | 0.8891 | 0.7861 | 13 | 0 |
| same, delta 6.0 | 93.84 | - | 0.4667 | 13 | **174** |
| PHI 40 full composite, delta 4.5 (phi40) | 14.54 | 0.8938 / 0.9157 | 0.7972 | 15 | 0 |
| PHI 40, delta 5.0 / 3.0 / 6.0 | 14.58 / 14.93 / 101.88 | - | - | 15 / 16 / 16 | 0 / 0 / **188** |
| PHI 45, old window | 15.41 | 0.8898 | 0.7972 | 17 | 0 |
| **under-pass, no bump, R_t 82.81** | **14.59** | **0.9012 / 0.9022** | 0.7861 | 13 | 0 |
| under-pass, R_t 83.81 (+1 mm) | 15.99 | 0.9012 / **0.886** | 0.7861 | 13 | 0 |

Two consequences the proposers did not draw:

- **Under-pass height window ~0.34 mm.** Pooled ib14 falls 0.016 per mm of shell height, so it crosses 0.90 about
  0.14 mm above the pick; E's 1.0 mm clearance is 0.2 mm below it. up_clr 1.5 is outside the window (predicted ~+0.5).
- **The over-pass delta gate.** The lens's cliff clause (delta + 1.5 deg within +0.5 of the pick, 0 jams) fails at
  delta 4.5 (6.0 reads 93.84 / 101.88), and delta 3.0 brings 259 back as a contact at PHI 40. The only legal picks are
  delta 3.5 (its +1.5 = 5.0 read clean) or 4.0 (5.5 not read). phi40's pick is pre-registered at delta 3.5 first.

### 1.2 Where the E strap runs at the relay station (judge, eaz.py)

The chain's arm-frame azimuth about a_r within |s - s0| <= 7 mm of the station (ds 31, PHI 35), over the 480 fit
kin_ok (phi 0) and envsel fresh workspace (relayed frames) poses. Only E enters the station (the boss and knee stay
distal of it at ds 31).

| part | samples | azimuth rel pad | in the posterior block window [-5.4, -1.9] | in the anterior block window [45.9, 49.4] |
|---|---|---|---|---|
| E strap | 13836 | **+6.4 .. +49.0** | 0 | **44 points on 5 frames, r up to 79.47** |

The shell arc is -1.9..+45.9. So:

- The posterior support is E-free.
- A block at the anterior end is crossed by E on 5 frames, inside a 4 mm block's radial span (77.3-81.3): 5 jams, and
  the lens's pass clause requires 0 jams. E's 0.19 % of samples beyond +45.9 are the relayed poses near phi 35, the
  reach the relay exists to take.
- No intermediate post can work either: E occupies every azimuth from +6.4 to +49.0 in some pose.
- A cantilever from the posterior support: a 1.5 x 8 (net) Ti strip over 69 mm deflects P L^3 / (3 E I) = 1.7 mm at
  4 N (I = 8 x 1.5^3 / 12 = 2.25 mm4, E 114 GPa), more than the 1.2 mm clearance; it needs a stiffer, taller section,
  which the pooled in-band window (1.1) does not have to give. Simply supported, the same strip deflects 0.11 mm (the
  proposer's check is right for a bridge, not for a cantilever).

### 1.3 The supports against the posed skin (judge, blocks.py / blocks2.py)

Arm-fixed Ti blocks, 12 mm in s, 4 mm along the arc, from R_liner - H up to the shell underside R_liner = 81.31
(R_t 82.81), sampled every 1 mm / 0.5 mm radially, signed distance to the posed skin on every evaluated envsel pose
(406), in the arm frame HG0 as the model's rerecord does for the shell:

| set | min mm | worst poses (ws, plane / elev / axial) | in the skin | < 1 mm |
|---|---|---|---|---|
| shell underside [-1.7, 45.7] | 2.45 | 264 (-69, 59, 114) 2.45; 259 (-56, 58, 113) 3.13; 265 3.77 | 0 | 0 |
| posterior block H 4 | **-1.71** | 264 -1.71; 259 -0.89; 265 -0.28 | **3** | 10 |
| posterior block H 3 | -0.72 | 264 -0.72; 259 0.11; 265 0.71 | 1 | 3 |
| posterior block H 2 | 0.28 | 264 0.28; 259 1.11; 265 1.70 | 0 | 1 |
| anterior block at the arc end [45.7, 48.6], H 2 / 3 / 4 | 2.63 | 119 (-64, 3, 151) | 0 | 0 (but E crosses it: 1.2) |
| shell extended to +52.3 (underside R 81.31) | **-1.39** | 119 -1.39; 162 (38, 1, 49) 2.75; 142 (-23, 9, 109) 4.14 | **1** | 1 |
| anterior block outside E's envelope [49.5, 52.3], H 2 / 4 | **-1.39** | 119 -1.39 (the torso meets the shell level, so H does not matter) | **1** | 1 |

Arm-fixed metal in the skin is a CONTACT in the model (it cannot refuse a pose):

- The proposer's 6 x 12 x 4 posterior block would add 3 contacts on envsel (~+0.74 gap at 0.246 per contact). At
  H <= 2 mm the posterior support is clean (0.28 mm at 264 is a near-touch, reported only); the rest of the height is
  a soft liner pad (compliance, stated as such).
- The anterior support has no free place: at the arc end E crosses it (5 jams); moved outside E's envelope the
  extended raised shell meets the torso at envsel 119 (behind-back ER, -1.39 mm: +1 contact, ~+0.25). The bump
  family's lower shell (top R 80.1) read 0.44 mm at +50.9 on the same pose, so the under-pass's PHI 40 cell (anterior
  end +50.9 at top R 82.8) is likely the same contact: read it per 2-deg bin before choosing PHI 40.
- What is left: (i) accept 119 as a contact with the support outside E, or (ii) a cantilever from the posterior
  support whose stiffening sits ABOVE the shell outside the carriage footprint (the model's pooled in-band counts only
  skin-facing relay samples; tops are contact / jam only), sampled at its real height, 4 N tip deflection <= 0.5 x
  up_clr. A plain thicker shell is not an option: +1 mm of shell height reads 15.99 (pooled 0.886).

### 1.4 The one-stage drive geometry (onetooth rows)

- Kennedy's theorem by the sine rule (the relative axis of link 1a vs link 2 divides the 38.03-deg uK-u2 arc with
  sin(a_K) / sin(a_2) = 1 / rho): rho 2.15 gives 11.8 / 26.2 deg (sin ratio 0.463 = 1 / 2.16); rho 0.8 gives ~21.3 /
  16.7 deg (1.26). Both of the proposer's pitch positions reproduce. For shortk (K 30 deg from u2), rho 1.1 puts the
  pitch axis ~15.7 deg from u2, consistent with its 16.6-19 mm contact path.
- The proposer's first proxy (os/onetooth_prox.py, 16:35) did not apply the RS frame and read 19-30 contact poses for
  horn and pin; the RS-correct allprox.py reads 0. The row carries the corrected numbers.
- **P1:** the pin start (21.5 mm, az +24) and the tooth level were chosen on Bench(110,360) taken poses (the claim
  bench). The rows must re-select them, and J3MIN, on envsel only and report the drift.
- Complexity re-scored with `tools/simplicity.py --score` (the lead's record minus the crank body, its pivot, one pair,
  one loop and the roller): 10.25-11.0 (11.0 if the flank insert counts as a made part); the spring-free cell 7.0-7.5.
  Both stay under the verified cx 12.0 frontier point (geneva-tail-pinknee 23.57).

### 1.5 shortk's own fold

a1max 58.77 against bk1 + bk2 = 64: the K sub-dyad sits 5.23 deg from its own fold at the stretched end, on the 5-deg
line. The row reports K's minimum sub-dyad margin over the taken poses like th, and its transmission there.

### 1.6 The long dyad over the top (lens C)

The proposer's ghosts (raglan-routed-3r's builder unchanged, Bench(60,160) fast): 158.66 (J1 posteromedial bvec(-45,
17.5), a1 132.5 / a2 47.5, branch -1), 196.57-336.52 with J1 own-angle stops, 164.42 for the far-end hub-2 realization;
hub 2 (or hub 3 / link 2) at the 400 mm never-clears cap in every case, and the audit's sparse-sampling flag fires on
the long links (so the true numbers are worse). Family scan: best proxy 56.6 / 67.0 / 75.3 / 81.7 by a1 bucket 95-110 /
110-120 / 120-130 / 130-141, getting worse as the dyad lengthens; the proxy is optimistic (raglan 33.7 vs the kit's
42.72). The knuckle bound (any K law, no drive metal): 4-part ib14 <= 0.2 at >= 63 % of fit poses kept.

Judge frozen exact wear (raglan-routed-3r.py frozen, CB_EXACT=1, fit Bench(60,160) with continuity, frozen on
Bench(110,360) exact), canonical long-top config: [LT_LINE]

Mechanism, measured: a 0.99 kinematic window needs J1 opposite the arm's workspace centre, 146+ mm from GH on the
curved back (or the long arc moves to link 2); the chain then spans 180 deg of the GH sphere, the long link turns ~320
deg about J1 and its great circle passes through the neck and trunk in > 10 % of poses, and a rigid hub must clear the
highest skin it ever passes over (proximity_atlas.md). No J1 stop, hub end or K law brings it into a 12 mm band.

## 2. Verdicts

| candidate | verdict | reason |
|---|---|---|
| onetooth-slowlaw-knuckle-3r | **PICK 1** | the only open 3-joint complexity lever; its step 0 is honest (the lens as written dies, the slow law survives with measured PA); P1 re-selection added |
| onetooth-desmo-knuckle-3r | **MERGED into pick 1 as cell D** | same law, pin, tooth and step 0; the spring-free groove is a closure variant (as desmo-slipper was of the lead), run only after the spring cell's built flank passes PA |
| underpass-bridge-relay-4r | **PICK 2 (re-specified)** | removes the relay's whole in-band term (14.59 = the ideal bound on envsel) but only with supports it never sampled: posterior <= 2 mm Ti on a pad; anterior outside E's +49.0 envelope (costs envsel 119 as a contact, -1.39) or a cantilever stiffened above the shell (1.2-1.3) |
| phi40-thinstack-relay-4r | **PICK 3 (fallback, parallel)** | the bump family's best measured composite (14.54); keeps the E-over-carriage cliff, so delta 3.5 is pre-registered first (1.1); the anterior end is a 0.44 mm near-touch |
| lugcoil-lbracket-relay-4r | **MERGED into pick 3 as its PHI 35 cell** | the same hardware at PHI 35; 15.21 envsel / ~13.84 claim is a coin flip, and its delta 4.5 pick fails the cliff gate |
| shortk-onetooth-knuckle-3r | **PICK 4** | a different morphology (re-seated K dyad) with the best PA margin; lives or dies on its tooth-sweep scan, which becomes step 0 on envsel |
| longtop-dyad-3r | **REJECTED (dead at step 0, measured)** | ghost 158.66 fast, hub 2 at the 400 mm cap; frozen exact above (1.6); kill line 27.20 |
| longtop-farhub2-3r | **MERGED with longtop-dyad-3r and rejected** | the far-end hub-2 realization of the same family: moves the floating part from hub 2 to link 2 / hub 3 (164.42 fast) |
| longtop-gradedk-knuckle-3r | **MERGED with longtop-dyad-3r and rejected** | the "with its own drive" clause as a bound: no K law gets the chain into band (ib14 <= 0.2 at >= 63 % kept); the drive gate (ghost <= 22) is never reached |

## 3. Ranking

Score = expected gap reduction vs the champion (75.94) x confidence x buildability (all 0 passive translations, so
buildability ties; 3 joints break ties per CLAUDE.md, "push for 3 before settling for 4"). Gain vs the lead (18.28) is
shown too.

| rank | candidate | expected frozen exact | vs champion | vs lead | confidence | product | joints / cx |
|---|---|---|---|---|---|---|---|
| 1 | onetooth-slowlaw-knuckle-3r (+ cell D) | 19-21 | 55-57 | -0.7..-2.7 (a cx 18.5 -> 10.25-11.0 Pareto point) | 0.5 (P(<= 23.5) ~0.6, P(pass <= 18.98) ~0.2) | ~28 | 3 / 10.25-11.0 |
| 2 | underpass-bridge-relay-4r (+ PHI 40) | 13.5-14.0 | 62-62.5 | +4.3..+4.8 | 0.4 (supports and a 0.34 mm window) | ~25 | 4 / ~53.5 |
| 3 | phi40-thinstack-relay-4r (+ lugcoil) | 13.2-13.6 | 62-63 | +4.7..+5.1 | 0.35 (cliff, anterior near-touch) | ~22 | 4 / ~51.25 |
| 4 | shortk-onetooth-knuckle-3r | 19.5-23 | 53-56 | -1.2..-4.7 | 0.3 (tooth-sweep scan) | ~16 | 3 / 10.25-11.0 |
| - | longtop family (3 rows) | > 150 | negative | negative | 0.95 dead | - | 3 / 0 |

## 4. Picks and gates (for the screen)

- **Pick 1, onetooth-slowlaw-knuckle-3r** (1 process, <= 90 min). Step 0 = the law-only ghost at rho 0.75 / 0.8 / 0.9
  on envsel then frozen exact (kill > 19.0 or ws takes < 258; a ghost < 18.28 is reported as a law lever for the
  lead). Select the pin start, tooth level, nose radius and J3MIN on envsel only. Pass <= 18.98 at cx <= 12; planner
  kill > 20.0 or held worse than the lead by > 1.0; a frozen reading in (20.0, 23.5] stops the row and is written down
  as the cx 10-11 frontier point, never as a pass. Cell D only after the spring cell's built flank passes PA.
- **Pick 2, underpass-bridge-relay-4r** (lens A, 2 processes, <= 120 min with pick 3). Supports sampled as arm-fixed
  metal: posterior H in {1.5, 2.0}; anterior as two pre-registered cells, (i) the shell extended so the block sits
  outside E's envelope (envsel 119 becomes a contact, -1.39; read per 2-deg bin) and (ii) a cantilever stiffened above
  the shell outside the carriage footprint, 4 N tip deflection <= 0.5 x up_clr, sampled at real height; never a block
  E crosses. PHI 40 only after its anterior end is read against 119. Cells PHI {35, 40} x delta {3, 4.5} x up_clr {1.0, 1.2}. Pass = chain-only gate
  (min of pooled and chain) <= 13.75, 0 jams, cliff margin >= 1.5 deg; kill > 14.76 or held > 18.27.
- **Pick 3, phi40-thinstack-relay-4r** (shares lens A's budget). Cells PHI {35 (lugcoil), 38, 40, 42} x delta {3.5,
  4.0}; pick = the lowest gate with 0 jams whose delta + 1.5 reads 0 jams within +0.5; new PHI 40 prepare and flood.
  Same gates.
- **Pick 4, shortk-onetooth-knuckle-3r** (1 process, <= 90 min). Step 0 on envsel: the ghost (kill > 19.0) and the
  PA-passing start scan (kill: no start with <= 4 tooth contact poses at <= R 64). Same pass / kill as pick 1.

Every pick: ONE frozen exact Bench(110,360) claim wear + held; `python3 tools/alignment_paired.py dump` for bench and
held (T5 depth on file); the continuity flood; min th margin; the 2 mm reading (reported only); the viz file +
`node docs/concepts/viz/test.mjs <id>` + `node docs/concepts/viz/thumbs.mjs`; commit after every step. Never place a
stop, margin or tie-break from Bench(110,360) binders; held-out stays held out.

## 5. What happens next

- The four slots fill the 4-core box (local only, nice 10, OMP 1; the main-track lowarm verifiers were idle at 17:28).
  Lens A's two rows race for the 95 line; lens B's two rows chase the cx 10-11 frontier at 3 joints.
- **FINDING for FINDINGS.md** (the lead writes it):
  - An under-pass relay (the chain under a raised arm-fixed bridge) removes the over-pass bump's whole in-band term
    (envsel 14.59 = the ideal-relay bound) but its height window is ~0.34 mm (pooled ib14 -0.016 per mm), and its
    supports are bounded by measurement: E sweeps +6.4..+49.0 deg rel the pad at the station, so the anterior support
    must sit outside that (where the raised shell meets the torso at envsel 119, -1.39 mm) or cantilever; posterior Ti
    must stay <= 2 mm over the 259 / 264 / 265 skin.
  - The long dyad over the top is dead at step 0 for every realization (hub 2 / link 2 at the never-clears cap; any K
    law <= 0.2 ib14): the take-bound table's "unmeasured" long-dyad line can be closed with section 1.6's numbers
    (docs/research/take_bound_3dof.md, the lead's edit).
- The user's 4-joint question stays open; a lens-A pass is reported as the 4-joint answer, never a lead change.
