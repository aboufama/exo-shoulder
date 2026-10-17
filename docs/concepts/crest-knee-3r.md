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

## Status

(claim numbers below)
