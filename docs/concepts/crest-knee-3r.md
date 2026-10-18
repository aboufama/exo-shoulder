# crest-knee-3r: deltoid-crest seats on the pin-knee chain

Round-14 lens 3 (crest-pinknee-cx0), catalogue row crest-knee-3r (round-4 pick). A PLAIN O20 3R (three pins on bearing
pairs, no drive, no spring) with the two-pin MR63ZZ cuff knee (cx 0 under simplicity v2.2), moved from the verified
pin knee's back-of-shoulder seats (H1, k4598) to the deltoid-crest seats, with link 2 flying over the whole member 3
and an optional J3 own-angle stop. 3 active joints, 2 passive pins (cuff knee, outside the count), 0 passive
translations.

## Deeper-version answers (written first)

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
