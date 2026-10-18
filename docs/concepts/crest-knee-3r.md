# crest-knee-3r: deltoid-crest seats on the pin-knee chain

Round-14 lens 3 (crest-pinknee-cx0), catalogue row crest-knee-3r (round-4 pick). A PLAIN O20 3R (three pins on bearing
pairs, no drive, no spring) with the two-pin MR63ZZ cuff knee (cx 0 under simplicity v2.2), moved from the verified
pin knee's back-of-shoulder seats (H1, k4598) to the deltoid-crest seats, with link 2 flying over the whole member 3
and an optional J3 own-angle stop. 3 active joints, 2 passive pins (cuff knee, outside the count), 0 passive
translations.

## Round-14 re-dispatch: the ANTCREST basin (2026-10-18, lead note)

The lead asked for the antcrest basin forwarded by the J2 judge (J1 bvec(55, 62), J3 wdir(98-104, +5..+18); fold loss
20-24 of 220 vs H1's 36), re-measured at O20 / margin 5 with the knee RE-FIT on the envelope bench and an |axial| >= 150
contact gate. The first screen (sections from "Deeper-version answers (first screen)" on) searched the CREST cells (J1
az 85-115) and never sat at J1 az 55; this section is that missing measurement.

### Deeper-version answers (written first, 2026-10-18 06:12 UTC)

1. **What a top mechanism designer would do that the spec does not ask for.** (a) Parameterise J2 by the axis angles
   a1 (J1-J2) and a2 (J2-J3 at rest) on the posterior branch and convert to bvec(az2, el2) at the rest pose, so every
   candidate closes at rest and the fold window 2 min(a1, a2) - 20 is a search coordinate, not an accident of az2 / el2
   (antcrest A a1/a2 50/58 -> J2 bvec(21.1, 17.9); B 52.5/56 -> bvec(35.7, 11.4): hub 2 sits LOW on the posterior
   deltoid, el 11-18, not over the supraspinatus). (b) Treat hub 2's level as the design variable it is: one radial
   level for a J2 ray whose skin exit spreads 50-77 mm (p5-p95) means hub 2 is in band only where the exit is within
   12 mm of the level; the levers are h2cap (drop the high-exit poses) and the J3 own-angle stop (the judge measured
   that the hub-2 tail separates on J3's angle, not J1's), and the kill line is hub 2 <= 0.5 in band. (c) Re-fit the
   knee on the representative envelope sample (|axial| >= 150 at 11 %, not Bench(60,160)'s 6 %) with an explicit
   |axial| >= 150 contact term in the objective, because H1's knee collides there. (d) Keep every rule bound as a hard
   box edge (ang_min >= 25.22, MR63ZZ stk 6.0, O20, fold margin 5, own-angle J3 stop frozen into the claim).
2. **Rawest material.** The posed skin through the signed-distance grids (Bench(60,160) fast cache 0089c747c10f; the
   envelope bench 'env' cache env-72d21f5aa2e5-env, BUILT LOCALLY this session with tools/env_bench.py part / assemble
   because the farm volume is closed; Bench(110,360) exact), the model's per-pose IK (q1-q3', knee angle, the hub-2
   level each pose needs = Hneed["hub2"]), the 10 fps fit clips for continuity, and the judge's raw J2-exit percentiles
   (round102_ideation 1.5), not the "fold 20-24 of 220" summary.
3. **Methods and tools.** The model file with its checks unchanged (pin-knee VModel rules, part-part clearances,
   contact-only walls / crowns, J3 window frozen); a new runner (a1 / a2 seat parameterisation, near-touch objective +
   2 points per |axial| >= 150 contact pose); random box, then own numpy CMA-ES, first on Bench(60,160) fast while the
   env cache builds, then on env; the claim wears the frozen shape on Bench(110,360) exact.
4. **What else shows the number is right.** tools/concept_bench.py (not this code); the antcrest A / B seeds through the
   same code at the judge's exact seats (73.12 / 82.31 fast before any knee re-fit: fold 23 / 20 of 220 as the judge
   measured, hub 2 0.09 / 0.05 in band at 76-77 mm); the first screen's crest cells and H1 (23.64) through the same
   code; the adversarial verifier (docs/concepts/verify/crest-knee-3r.py) that re-runs the claim.

### What was measured (antcrest, 2026-10-18 06:09-07:00 UTC, local, farm closed)

**Envelope bench: not available here, so the knee re-fit ran on Bench(60,160).** The env fast grid lives on the farm
volume (closed). A local build (tools/env_bench.py part / assemble, 1 niced process) reached 92 of 530 poses in 13 min
at box load 10-13, i.e. ~75 min for the whole bench, longer than the time box. It was stopped and the search ran on
Bench(60,160) fast, with the |axial| >= 150 contact gate in the objective (+2 points per contact pose there). The
verdict below does not hinge on the knee (next point), so the env re-fit could not change it. Whoever re-opens this
cell needs the env cache on the farm or ~75 local CPU-minutes first.

**1. The hub-2 trade at the judge's seat (knee-free, rawest number).** `h2need.py` (scratchpad ck2) reads, per closing
pose, the level hub 2 needs along its GH ray (the model's Hneed hub2). At antcrest A (J1 bvec(55, 62), a1/a2 50/58, J3
wdir(98, 5); J2 bvec(21.1, 17.9)) the fold loses 23 of 220 and the need is p5 / 50 / 95 = 52.5 / 61.0 / 91.3 mm. In
the table, "hub 2 in band" means <= 12 mm above its own 2 mm level (the model's proxy). "J3-stoppable" counts the
poses dropped above the cap whose q3' lies outside the kept poses' window:

| hub-2 level cap L (mm) | poses kept (ws of 160) | dropped (ws) | J3-stoppable | hub 2 in band |
|---|---|---|---|---|
| 60 | 90 (65) | 107 (72) | 15 | 0.91 |
| 63 | 124 (84) | 73 (53) | 14 | 0.86 |
| 66 | 146 (98) | 51 (39) | 14 | 0.70 |
| 70 | 156 (106) | 41 (31) | 13 | 0.35 |
| 74 | 163 (110) | 34 (27) | 11 | 0.11 |
| 78 | 168 (114) | 29 (23) | 11 | 0.04 |

Antcrest B (wdir(102, 18), 52.5/56) and two neighbours read the same shape:
- B's need is p95 86.1.
- At B, hub 2 is >= 0.5 in band only at L <= ~67, and nothing above L 63 is J3-stoppable.
- The hub-2 tail is NOT separable on J3 at the antcrest seats (0-16 of the dropped poses). The judge's "separates on J3"
  came from the crest cells C1 / C2 / C3.

A dropped pose that is not stopped is metal in the skin, i.e. CONTACT (the model's greedy-drop convention). So each mm
of cap that buys hub-2 in-band costs contact at 100 / 220 per pose, and the fold gain (23 vs H1's 36) is spent several
times over.

**2. A knee-free lower bound says the seats alone do not kill the basin; the links do.** `h2bound.py` takes 64 seat
cells (the 4 named cells + 60 uniform in az1 45-68, el1 54-70, a1 40-62, a2 45-70, wd 92-110, wa -4..24, b3 0-0.4).
For each cell it scores the fold plus hub 2 at its best level, assuming every other sample is in band and a perfect
J3 stop on every dropped pose. The bound is 3.1-43.6 (median 15.0). It correlates with the fold at r = 0.78. Its
minimum sits at L 90-100 mm with hub 2 ~0.01 in band: the bound lets hub 2 float far off the skin at only its 11.6 %
sample share. A real hub 2 carries the link ends: the wide-window seeds (fold 10 / 19) put hub 2 at 96.9 / 89.9 mm, and
link 2 went with it (0.03 in band), so hub 2 + L2 (26 % of the samples) are out of band. That alone costs >= 16
in-band points.

**3. The search (CMA on Bench(60,160) fast, near-touch objective + |axial| >= 150 gate).** 575 configurations (557
scored, 18 cut at the 40 s exact-fallback limit). All are in `docs/concepts/sweeps/crest-knee-3r.json` after the first
screen's 531, under run tags `ac-*` with `bench`, `obj`, `ax150_contact`:
- ac-A1: 17 random around the two judge cells.
- ac-C1: 303. Starts: antcrest A, A with cap 67, and (60, 66) with cap 70; 60 perturbations, then CMA, sigma 0.10.
- ac-C2: 73. Four starts at the best knee-free-bound seats (wide a1 / a2 55-59). Stopped: nothing beat its own seed
  68.41, with hub 2 at 90-97 mm.
- ac-C3: 81, CMA sigma 0.05 from the C1 best.
- ac-C4: 101, CMA sigma 0.04 from the C3 best.

| set (configs, gap < 150) | n | best plain gap | hub 2 level, median | hub 2 in band, median |
|---|---|---|---|---|
| fold 0-20 of 220 | 26 | 68.41 | 97.8 mm | 0.01 |
| fold 20-30 | 36 | 73.12 | 73.7 mm | 0.14 |
| fold 30-40 | 34 | 64.19 | 75.4 mm | 0.09 |
| fold 40-50 | 171 | **56.73** | 75.7 mm | 0.08 |
| fold 50-80 | 63 | 57.95 | 75.9 mm | 0.05 |
| hub 2 in band >= 0.5 (any fold) | 12 | 80.26 | | |

**The search leaves the basin.** The top 20 configurations all sit at J3 wd 92.0-94.6, at or near the box edge 92: back
at the first screen's crest J3 (wd 93), not the antcrest's 98-104. Their fold is 42-56 of 220, worse than H1's 36. The
fold gain that defined the basin (9-23 of 220) is reachable only with hub 2 at 74-98 mm, out of band, and with link 2
lifted along with it. Once member 3 and hub 2 must live near the skin, the CMA gives the whole fold gain back.

**4. Claim: the best shape frozen (fit Bench(60,160) fast), worn without refit, exact path, verifier checks on**
(`claim2.py` in scratchpad ck2: docs/concepts/verify/crest-knee-3r.py crest_checks + the pin-knee verifier's
extra_checks; per-pose dumps `docs/alignment/remeasure/crest-knee-3r-antcrest_{bench,held}_perpose.json`).

Best cell (ac-C4 k10): J1 bvec(49.9, 57.7), a1/a2 42.8/60.4 (J2 bvec(16.1, 22.5)), J3 wdir(93.0, 0.1), b3 0.302, lE
70.4, lc 33.6, phiE 7.0, phib -84.3, ang_min 26.89, h2cap 76.0, J3 stop window [291.2, +240.6], MR63ZZ knee pins
(stk 6.0), O20 hubs at 53.4 / 75.4 / 66.2 mm from GH.

| wear | gap | reach | follow | ib14 | ib10 | contact (poses, depth sum, deepest) | near-touch 1 mm | min th | ws overhead taken | ws \|axial\| >= 150 taken | why lost (fold / J3 stop / parts / contact) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Bench(60,160) fast (fit) | 56.73 | 0.6375 | 0.8667 | 0.722 | 0.4736 | 0.0435 | 57.98 | | | | 43 / 10 / 6 / 7 of 220 |
| **Bench(110,360) exact, frozen** | **61.12** | 0.5889 | 0.8636 | 0.7209 | 0.4768 | 0.0346 (11, -15.4 mm, -4.81) | 65.85 | 5.28 deg | 3 / 28 | 10 / 27 | 106 / 26 / 20 / 11 of 470 |
| held out, frozen | 64.60 | 0.5778 | 0.8545 | 0.7190 | 0.4757 | 0.0473 (15, -61.6 mm, -12.78) | 71.73 | 6.01 deg | 2 / 26 | 12 / 29 | 110 / 25 / 18 / 15 |

Earlier claims on the way: the C1 best frozen exact 66.98 (fast 64.19) and the C3 best 62.40 (fast 57.95). The
verifier's extra checks removed 0 poses on every wear: closure <= 0.023 deg, knee 77.9-96.7 inside [26.89, 153.11],
J3 window held, th margin >= 5.28. Parts in band (bench): hub 2 0.118, knee 0.685, E 0.713, boss 0.720, L1 0.775, L2
0.824, hub 3 0.863, pad 0.887, hub 1 1.0.

**Red team (own best).**
- **The optimistic number:** fast 56.73 becomes 61.12 frozen on the big bench and 64.60 held out.
- **The pose that jams:** |axial| >= 150, where every loss is fold (17 of 27). The antcrest seats do not open the
  rotation extremes either.
- **The point that pinches:** 15 held-out contact poses, deepest -12.78 mm. Overhead workspace: 3 of 28 taken.
- **The kill lines, both met:** hub 2 is 0.118 in band on taken poses (kill <= 0.5), and frozen exact 61.12 is far
  over 23.64.

**Convergence gate (search objective, score points, all 575 configurations in time order): NOT passed.** Gain over the
second half 3.61 (> 1), over the last third 1.59 (> 0.5), top-5 spread 1.24 (< 3). Plain gap: 2.71 / 1.59 / 1.06. The
small-step CMA was still descending, by ~1.25 gap points per 40 evaluations, when the time box ran out. So the basin
is not formally called dead. It sits 37 points over the kill line (fast) and the descent is slow. It would need
roughly 1000 more evaluations at that rate to reach the 23.64 kill line, and it is walking OUT of the basin (wd to 92, the crest J3) toward the first
screen's own optimum (26.34 fast / 32.84 frozen, verified).

### Verdict (antcrest re-dispatch)

**Screened, both kill lines met, gate not passed; the row's verified claim stays the crest cell (32.84 frozen exact,
held 29.81).**

- Best antcrest: frozen exact Bench(110,360) **61.12** (score 77.77), held 64.60, fast 56.73. That is 28 points worse
  than the same row's crest cell and 33.9 over H1's 27.20.
- Cx stays 0: 3 active, 2 knee pins outside the count, 0 passive translations.

What this teaches beyond the cell:
- **On a GH-ray J2, the J2 judge's "fold loss 20-24 of 220" is not a reach gain.** It holds only if hub 2 may sit at
  the high end of its ray's skin-exit spread. At the antcrest seats that spread is 52-91 mm (p5-p95) and is NOT
  separable on J3's own angle (0-16 of the dropped poses stoppable). Every config with hub 2 >= 0.5 in band scores
  >= 80 fast, and the fold-free configs need hub 2 at a median 97.8 mm.
- **A knee-free bound that scores hub 2 alone is too weak to kill a seat** (bound median 15, min 3.1). Hub 2 drags
  its link ends with it (link 2 0.03 in band at 97 mm), so any seat bound must carry hub 2 + L1 / L2 (~26 % of the
  samples).
- **For whoever plans next:** at J1 az ~50-55 the search's own optimum moves J3 back to the crest (wd 92-93). The
  pin-knee chain's fold lever is not a J1 / J3 seat move; seats only trade fold for hub-2 level (this run), or for J3
  stops and member-3 sweep (first screen).

Not run (time box / farm closed): the envelope-bench knee re-fit (env cache unavailable; see above) and the kNN
continuity flood (the cell is ~37 points over the bar). The motion preview stays at the row's best configuration (the
crest cell); the antcrest cell is not the best configuration.

## Deeper-version answers (first screen, crest cells)

1. **What a top mechanism designer would do that the spec does not ask for.** The spec says "run the pin-knee model
   unchanged at the crest seats". The literal antcrest seats (J1 bvec(55, 62)) are already measured dead (hub-2 need
   50-400 mm; 86.12 fast with E in the free sector, hub 2 at 192.8 mm; round14_ideation section 5). A designer would
   (a) let J1 / J2 / J3 move inside the crest basin jointly with the knee instead of fixing seats and tuning only the
   knee, because the knee's free sector, link 2's fly-over and hub 2's level are coupled; (b) treat link 2's crossing
   of member 3 as a real layer order (fly-over of the E strap + boss, not only knee + pad); (c) carry the J3 window as
   a physical dowel-in-slot stop on J3's own angle and freeze it from search to claim; (d) put the knee pins at their
   build stack (MR63ZZ pair, stk 6.0, the lead's build rule) and the knee window at >= 25.22 deg (rule edge) from the
   start; (e) pair everything against H1 run through the SAME code (23.64 fast here) so a gain is a seat gain, not a
   check change.
2. **Rawest material.** The posed skin itself through the bench's signed-distance grid (Bench(60,160) fast cache
   0089c747c10f; Bench(110,360) exact path), the 10 fps fit clips for continuity (CB.FIT), the per-pose dumps of the
   model's own IK (q1, q2, q3' = q3 + phi, knee angle, drift), and the J2-exit / skin-motion data of the antcrest
   basin (round-102 judge's j2exit, round14_ideation section 5) - not the digested "fold 20-24 of 220" summary.
3. **Methods and tools.** docs/concepts/models/skin-normal-3r-pin-knee.py unchanged (its Design / closed-form IK /
   two-circle knee / VModel rules / part-part clearances / contact-only walls and crowns) subclassed in
   docs/concepts/models/crest-knee-3r.py (fly-over E box, J3 window with a frozen claim path, frozen() that copies the
   whole fitted shape). Search: local CMA-ES (numpy, own implementation; the farm is closed) on Bench(60,160) fast with
   the near-touch gap as objective (scored samples < 1 mm on a taken pose count as contact), two independent starts
   (cells C1 and C3). Claim: frozen shape on Bench(110,360) exact; red team with the model's redteam pass (closest
   metal, contact-only walls, near-touch at 1 / 2 mm, rest / overhead / across / behind groups).
4. **What else shows the number is right.** The bench (tools/concept_bench.py, not this file's code), the H1 control
   through the same code (23.64 fast, matches the alignment re-measure), the frozen exact Bench(110,360) run, the
   round-14 judge's J3-stop control table (section 4: a stop gain that only relabels near-zero overhead touches at a
   0.5 deg band does not count), and the adversarial verifier (docs/concepts/verify/) that re-runs the claim.

## Model (what was built)

`docs/concepts/models/crest-knee-3r.py` subclasses the verified pin-knee model (skin-normal-3r-pin-knee.py, unchanged:
Design, closed-form IK, two-circle knee closure, VModel rules - closure < 0.5 deg, 10 fps continuity incl. the knee
branch, knee window [ang_min, 180 - ang_min] - part-part clearances >= 1 mm / 0.15 mm adjacent, contact-only walls,
crowns, tops and edges, 2 mm skin-facing sample grid). Changes, each because the crest seats need it:

- **Link 2 flies over the whole member 3** (`fly`): at the crest the J3 hub sits on the deltoid crest and link 2's free
  sector about J3 shrinks to 43-62 deg (H1 117.5), so link 2 crosses the E strap and E boss, not only the knee link and
  pad. The E strap is a box from hub 3's rim to the E boss at member 3's full height for link 2's avoid set.
- **J3 own-angle stop** (`j3stop`): a dowel in an arc slot between link 2 and member 3 on q3' = q3 + phi. Search: the
  window is the kept poses' q3' set minus its largest gap, shrunk by `j3stop_margin`. Claim: the window is FROZEN
  (`j3win`) from Bench(60,160) into Bench(110,360) (never refit on the claim bench).
- **Build-rule edges as box edges:** knee pins MR63ZZ pairs (stk 6.0), ang_min >= 25.22, O20 hubs only, fold margin 5
  deg (kit FOLD_MARGIN), `h2cap` (hub-2 level cap, a design choice: poses that need hub 2 higher are dropped).
- `frozen()` copies the whole fitted shape (incl. the fly-over E box levels and the J3 window) from the Bench(60,160)
  fit; the pin-knee's own frozen() would silently drop both.

Control through the same code: H1 (k4598 verified params, fly 0, no stop) reads **23.64** fast on Bench(60,160) (fold
36, slide 5, skin 6, parts 4), matching the "23.64 under the current checks" number; H1 + the same J3 stop reads 22.59
(the round-14 judge's relabel control).

## Search (local, farm closed)

Own numpy CMA-ES (no `cma` package on the box), objective = near-touch gap (scored samples < 1 mm on a taken pose count
as contact), Bench(60,160) fast, 16 free parameters: az1 85-115, el1 54-70, az2 5-35, el2 38-72, wd 88-116 (the crest:
wd < 88 drifts back to H1's seat wd 70), wa -28..18, b3 0-0.4, lE 30-95, lc 18-40, phiE / phib full circle, ang_min
25.22-40, h2cap 55-80 (79+ = none), j3stop on/off, margin 1-3, fly on/off; stk 6.0 fixed. Starts: proposer cells C1
(az1 100 / wd 92 / wa -5, 37.62 here) and C3 (az1 110 / wd 92 / wa -15, 34.38), perturbation rounds, then CMA (sigma
0.12, then 0.05 from the best). Evaluations that need metal outside the fast-cache box (far-off-skin configs: the
exact fallback takes minutes) are cut at 30 s and scored 400. Every evaluation is in
`docs/concepts/sweeps/crest-knee-3r.json` in time order (`run` = the process tag, `gap_nt` = near-touch gap).

## The measured trade: J3's azimuth on the crest buys fold poses and loses the knee

Binned over the 131 configs under gap 60 (sweep file), by J3's crest azimuth wa:

| wa (deg) | n | fold (of 220) min / median | J3-window stops median | knee link in band median |
|---|---|---|---|---|
| -28 | 3 | 59 / 71 | 3 | 0.77 |
| -24 | 5 | 51 / 61 | 5 | 0.66 |
| -20 | 21 | 36 / 48 | 5 | 0.52 |
| -16 | 41 | 34 / 39 | 10 | 0.54 |
| -12 | 31 | 28 / 35 | 15 | 0.52 |
| -8 | 12 | 23 / 31 | 14 | 0.40 |
| -4 | 8 | 20 / 24 | 16 | 0.38 |
| 0 | 8 | 16 / 24 | 17 | 0.43 |

- The crest's fold gain is real kinematically (fold 16-24 of 220 at wa -4..0 vs H1's 36), and it is the antcrest
  basin's 20-24.
- It is paid back pose for pose: the poses the J3 window stops are the ones where member 3 (E strap 67-75 mm, knee
  link, boss) would sweep into the skin over the crest (without the stop they are dropped as skin/contact). Total
  losses (fold + stop + skin + parts, of 220) are min 48-55 for every wa from -20 to +4, against H1's 51 (fold 36,
  slide 5, skin 6, parts 4) through the same code: the crest buys at most 3 takes.
- In-band pays the rest: the median ib14 falls from 0.83 (wa -16) to 0.74-0.77 (wa -8..+4). At the fold-free end the
  best cells read reach 0.70-0.71 and follow 1.0 on Bench(60,160) but ib14 0.78-0.79 (gap 32.8).
- **Why the in-band goes (the limiter at the fold-free end):** the E boss (member 3) and the arm pad sit at ONE knee
  level tr (the flat two-pin knee), and over the crest their skins are at different heights. The two best fold-free
  cells show it from both sides: wa -0.99 has the pad at 0.85 in band and the boss at 0.43; wa -0.72 has the boss at
  0.88 and the pad at 0.04. The knee link above them is 0.29-0.44 in band.
- The search therefore settles in the middle (wa -13 to -16): fold 34-41, stops 12-15, knee 0.73.

## Claims: frozen shape (fit Bench(60,160) fast) worn on Bench(110,360) exact

Same protocol as the pin knee's lesson (c): heights, knee centre m, E profile and the J3 window frozen from the fit;
`scratchpad ck/final.py` (claim harness, logged in this doc) adds near-touch (scored samples AND contact-only walls /
crowns / tops), min th margin (the H1 metric, J1-J3 angle vs the dyad's fold), overhead >= 140, |axial| >= 150 and a
per-pose dump. Held out was not touched.

| cell | fast Bench(60,160) plain / near-touch | frozen exact gap | reach | follow | ib14 | contact | near-touch 1 mm / 2 mm | min metal | min th | overhead taken | why (fold / J3 stop / parts / contact) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| best1 (wa -13.0, mid basin) | 27.63 / 31.29 | **33.23** | 0.6139 | 0.9545 | 0.8778 | 0.024 | 37.84 (8) / 70.48 (46) | 0.37 mm | 8.99 deg | 14 / 38 | 96 / 32 / 8 / 8 |
| best2 (wa -1.6, fold-free end) | 29.02 / 30.22 | 37.40 | 0.6278 | 0.9545 | 0.8416 | 0.043 | 40.44 (5) / 67.41 (37) | 0.04 mm | 6.24 deg | 9 / 38 | 77 / 29 / 18 / 15 |
| **best3 (wa -1.4, fold-free end; the claim)** | 26.34 / 28.74 | **32.84** | 0.6333 | 1.0 | 0.8529 | 0.0146 | 36.25 (6) / 57.98 (34) | 0.44 mm | 6.23 deg | 15 / 38 | 92 / 30 / 5 / 5 |

Reference: H1 (skin-normal-3r-pin-knee k4598) verified frozen exact **27.20** on the same bench (reach 0.6583, 237/360
ws taken, 9 contact poses; docs/alignment/remeasure/skin-normal-3r-pin-knee_bench_perpose.json).

## Red team (own best, frozen exact)

- **The optimistic number:** fast -> frozen exact costs +5.6 (best1) and +8.4 (best2) gap. The fold-free end's fast
  reach 0.706 is 0.628 on Bench(110,360): its extra fast takes were sample-tuned, as round-3 lesson (c) predicts. The
  J3 window fitted on 220 poses stops 29-32 of 470 on the big bench (15-17 on the search bench).
- **The pose that jams:** the fold still owns the large-axial region: |axial| >= 150 workspace poses 5 of 27 taken, all
  22 losses fold, on BOTH cells. The crest seats do not open internal / external rotation extremes.
- **The point that pinches:** best1's deepest contact is -1.81 mm at plane -75 / elev 60 / axial 120 (behind the back,
  internal rotation); best2 adds the Raise-overhead clip frames 7-11 (plane 30, elev 148-150, axial -60, -0.9 to -1.28
  mm), 264 (30 / 165 / -60, -3.82) and 281 (45 / 75 / 15, -4.10): the fold-free end parks member 3 over the overhead
  skin, the same overhead touches the round-14 judge's J3-stop control relabelled on H1.
- **Overhead (elev >= 140):** 14 / 38 (best1: lost to fold 11, J3 stop 10, contact 3), 9 / 38 (best2: fold 10,
  contact 11, J3 stop 8). H1-class overhead, not better.
- **Rules kept:** min th margin 8.99 / 6.24 deg (>= 5), knee angle 84.6-101.3 / 70.5-100.4 inside [ang_min, 180 -
  ang_min] with ang_min 25.22-25.92, O20 hubs, MR63ZZ knee pins (stk 6.0), J3 window frozen, 0 passive translations.
- Not run (time box): the kNN continuity flood (the knee pins are closure-determined and the 10 fps clip continuity of
  the VModel holds; the J3 window is a physical stop, not a passive coordinate), per-pose held-out dumps.

## Status

**Screened, below the lens bar; not called dead (gate not passed).** Best claimed frozen exact Bench(110,360)
**32.84** (score 88.06), best fast 26.34 (near-touch 28.74) on Bench(60,160), 531 configurations, cx 0, 0 passive
translations, 3 active O20 hubs + 2 MR63ZZ knee pins.

- Against the lens: bar <= 21.0 frozen exact, kill > 23.64. Every claimed cell is over the kill line (32.84, 33.23,
  37.40), and 5.6 over H1's verified 27.20 on the same bench and code family.
- Convergence gate (near-touch objective, score points): best gained 0.93 over the second half (< 1, passes), 0.62
  over the last third (> 0.5, FAILS by 0.12), top-5 spread 0.93 (< 3, passes). Plain gap: 0.72 / 0.72 / 1.08. The last
  gains came from the wa [-6, 8] run at the fold-free end, so a dead call waits for that run to flatten.
- What it teaches beyond this morphology: on the pin-knee chain, moving J3 along the crest moves losses between the
  fold and member 3's sweep over the crest (fold + J3 stops + skin + parts 48-55 of 220 for every wa), so a seat move
  alone does not buy reach; and a flat two-pin knee with ONE level for boss and pad cannot follow a crest whose two
  pin sites differ in skin height (boss / pad in band 0.43 / 0.85 or 0.88 / 0.04).
- Next (if anyone picks it up): a joggled knee link (pin a and pin b ends at their own levels, an R15 S-bend in the
  flat bar; MR63ZZ pairs unchanged), re-searched at wa -6..+8. Upside bounded by the fold-free end's fast reach
  0.70-0.71: ~21 fast if member 3 reached 0.90 in band, likely 25-27 frozen - under H1 at best, not the <= 21 bar.
  The lens's real 95 path is not here.

Files: model docs/concepts/models/crest-knee-3r.py, sweep docs/concepts/sweeps/crest-knee-3r.json (531 entries, time
order, `run` tag, `gap_nt`), row docs/concepts/rows/crest-knee-3r.json (exact_frozen + others, gate, H1 control),
preview docs/concepts/viz/concepts/crest-knee-3r.js at the claimed config. Claim harness and per-pose dumps (bench 470
poses each) were written to the session scratchpad (ck/final.py, ck/final{1,2,3}.json), not committed.

## Verification (independent verifier, 2026-10-18)

Harness `docs/concepts/verify/crest-knee-3r.py` (subclasses nothing new: it loads this model unchanged and the pin-knee
verifier's `extra_checks` unchanged). Protocol: fit on Bench(60,160) fast, shape frozen (heights, knee reference m, E
profile, J3 window [265.6, +239.54 deg]), worn without refit, exact path, on Bench(110,360) and on the disjoint held-out
bench. Run locally (farm closed), niced, one thread, 2 processes.

| wear | gap | reach | follow | ib14 | ib10 | contact (poses, depth sum, deepest) | near-touch 1 / 2 mm | min th | overhead ws taken | removed by checks |
|---|---|---|---|---|---|---|---|---|---|---|
| Bench(110,360) | **32.84** | 0.6333 | 1.0 | 0.8529 | 0.4431 | 0.0146 (5, 6.40 mm, -2.77) | 36.25 / 57.98 | 6.23 deg | 5 / 28 | 0 |
| held out | **29.81** | 0.6667 | 1.0 | 0.8521 | 0.4405 | 0.0169 (6, 4.80 mm, -1.63) | 35.39 / 54.71 | 5.33 deg | 6 / 26 | 0 |
| champion (spherical 3R), same bench + protocol, fold margin 5 | 64.93 | | | | | | | | | |

What was checked (each tried as a refutation; none removed a pose):

- **DOF.** 3 active O20 hubs (MR117-2RS pairs); the cuff knee is 2 MR63ZZ pin pairs parallel to J3, outside the count
  (user 2026-10-17). Closure: J1 and J2 on GH rays, the knee's planar RR absorbs the in-plane drift; the radial drift is
  0.0 mm on every taken pose (R_tol 0.5), so no passive coordinate is undetermined and nothing sags. 0 passive
  translations.
- **Closure, independently in 3D** (not the closed form the model solves): hub-3 centre, pin a, pin b 0.000 mm; J3 and
  knee-pin axes <= 0.023 deg; closure residual <= 0.017 deg.
- **Parts the model does not pair:** knee link vs hub 3 above its lower plate (rides with link 2, 1 mm rule) 0 bad;
  E boss vs hubs 1-2, link 1 (1 mm) and link 2 (0.15 mm, adjacent at J3) 0 bad. The fly-over E box is used only to size
  link 2; the actual E strap mid-surface is checked against link 2 on every pose by the model's collide (E-L2).
- **Stops and windows:** every taken pose has q3' inside the frozen J3 window (min margin 4.62 deg bench / 1.00 held);
  knee angle 80.2-103.8 deg inside [25.22, 154.78]; min th margin 6.23 / 5.33 deg (>= 5; no K, so no K play).
- **Continuity flood** (full 1432-pose workspace grid, 2-deg slerp edges, <= 10 deg joint steps incl. q3', pin a, pin
  b, no knee branch change, the J3 window and fold margin as walls, seeds at elevation 0): 959 kinematic nodes, 959
  connected, 0 islands; 0 taken bench or held poses dropped, so connected = static.
- **Per-pose dumps** (lead's rule): `docs/alignment/remeasure/crest-knee-3r_bench_perpose.json` (recomputed 32.83) and
  `..._held_perpose.json` (29.81), tools/alignment_paired.py format plus why / th margin / q3' / knee angle per pose.
- **Pad place:** pin b sits 79.6 mm from GH in hub 3's plane at level 61.2 mm (H1: 61.0 / 78.5), i.e. on the upper arm
  at H1's distance, not on the acromion.

Verdict: **verified at 32.84 (score 88.06), held 29.81; not refuted** (champion 64.93 on the same bench and protocol;
66.97 at fold margin 10 through the pin-knee verifier, 75.94 with the risley checks). It is not a leader or a round
winner: 5.64 behind H1's 27.20 and 14.56 behind the lead's 18.28 on the same bench, overhead workspace reach 5/28
(0.18), |axial| >= 150 workspace 5/27 (22 fold). The claim's own red team is accurate; the one framing to correct is
"overhead 15/38": that count mixes 10 overhead clip frames with 5 of 28 overhead workspace poses.
