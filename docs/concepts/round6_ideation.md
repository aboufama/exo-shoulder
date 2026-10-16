# Round 6 ideation: judge and red team (2026-10-16 ~12:10 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275), tools/concept_bench.py); gap 0 is the real
target. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered with exactly 3 active DOF. Under the round-5 skeptic ruling, a sensed passive joint that must be read
  to know the arm pose counts as ACTIVE.

References on Bench(110,360) exact, frozen, margin 5, O20 hubs:

| design | gap | active | complexity |
|---|---|---|---|
| skin-normal-3r-pin-knee H1 (3 active) | 24.48 (polish protocol) / 27.20 (round-3 protocol) | 3 | ~21.5 |
| minarc BDp (verified) | 19.54 | 4 (K sensed) | 33 |
| zc-frontier-3r (complexity-0 ceiling) | 31.04 | 3 | 0 |

The one lever that lifted frozen reach above 0.74 at in-band >= 0.88 is the knuckle. The open question for this round
is how to keep that lever at 3 active, with K determined by the three readings.

## Red-team measurements made by the judge

The scripts are in the session scratchpad `r6judge/`. They are the proposer's `camB.py` and `camBfrozen.py`, with a
switch `GEN=1` that swaps the linear law for the Geneva contact law. Bench(60,160) fast takes ~6 s per eval.

### 1. The cam claims ran a folded-side lobe that the description denies

`camB.py` applies the cam on BOTH forced states: `kK = kK_hi` on the stretched side and `kK_lo` on the folded side. Every
claimed run set `kK_lo = kK_hi`. That includes the 13.70 fast / 20.16 frozen headline at kK 6 and the 13.89 / 21.77 at
kK 3. A folded-side drive is a second tooth that the tail cannot reach: in the folded state link 2 itself lies back
over link 1b, and the tail points away.

At LB1 with kK_hi 6 and smhi 8:

| folded side | fast gap | reach | stretched poses taken | folded poses taken |
|---|---|---|---|---|
| kK_lo 6 (as claimed, two lobes) | 13.70 | 0.800 | 41 | 1 |
| kK_lo 0 (one tooth, as described) | **14.34** | 0.794 | 41 | 0 |

The honest one-tooth figure is 0.64 fast points worse. The 20.16 frozen headline is therefore slightly optimistic; the
re-measured one-tooth frozen figure is in section 4.

### 2. The real one-tooth Geneva law is not linear, and the result holds

A roller on a crank of arc L_t, passing at distance d from K's axis, drives a radial flank by dK = atan(L_t * t / d),
with t the q2 travel past the onset. The ratio starts at L_t/d = kK and falls as dK grows. That is not the linear
kK * t of the claim. Re-run with that law (`GEN=1`, one tooth, smhi 8):

| kK = L_t/d | fast gap | reach | in-band14 | contact |
|---|---|---|---|---|
| 6 | **13.79** | 0.794 | 0.902 | 0.032 |
| 8 | 14.37 | 0.794 | 0.899 | 0.037 |
| 10 | 14.38 | 0.794 | 0.899 | 0.037 |

The real tooth law is at least as good as the linear one: 13.79 against 14.34. The idea survives its first honest law.

### 3. Pressure angle and tail geometry

- **Pressure angle.** The measured dK_max is 51.7 deg (kK 6, LB1). For a radial flank driven by a near-straight roller
  path, the pressure angle grows to about dK. At 51.7 deg it is past the 45-deg gate. The proposer's 36 deg at dK 45
  is optimistic: about 45 deg is the honest figure. So the flank must be curved, or stop B must cap dK at <= 45 deg.
  Both belong in the search.
- **Tail length.** J2-K is bk2 = 46.7 deg at LB1. For the roller to pass d = 6-8 mm from K's axis (about 6-8 deg at
  strap level), L_t is about 39-41 deg. The proposed 36 deg falls short, so L_t is derived from bk2, not free.
- **Tail metal.** The tail's metal is NOT in any figure above. The proposer's own sweep calc puts its tip over
  p90 69 / max 140 mm of skin, against hub 2's p90 59, so this is the first thing to measure.

### 4. Frozen check of the honest law

One tooth, exact Geneva law, kK 6, smhi 8, LB1, frozen exact Bench(110,360): see the result line at the end of this
file. It was run by the judge, not the proposer.

## Verdicts

| # | candidate | verdict | reason |
|---|---|---|---|
| 1 | geneva-tail-knuckle-pinknee-3r | **PICK 1** (lobe-rocker merged in as its fallback embodiment) | 3 active with no K sensor. Its law is the only measured route to a 3-active design below H1: one tooth with the exact law gives 13.79 fast. Every joint is real: MR63ZZ roller, O20 hubs, dowel stops, clock spring. 0 translations. Risks: tail metal sweep, pressure angle (curve the flank), complexity 35.5. |
| 2 | geneva-tail-knuckle-3r | **PICK 2**, merged with knuckle-crest-hub3-4r's crest-basin J3 seat | The low-complexity (~16) sensor-free knuckle; the golden direction (score >= 90, then 95, at low complexity). The law cost is only 1.2 fast points against a sensed K at LA1. Its limiter is the J3 side (frozen ~41 at LA1). The crest-basin hub-3 map from knuckle-crest-hub3 (all-fit 0.85 at wdir(94,-15) against 0.61 at wd 48) is the measured lever. Kill gate: the coarse LHS must find hub 2 / K / hub 3 >= 0.8 with reach >= 0.72. |
| 3 | lobe-rocker-pushrod-knuckle-3r | MERGED into pick 1 (duplicate law) | Same determined law, different metal. The lobe inside O20 caps kK at ~3-3.5 by pressure angle (kK 3 measured 21.77 frozen with two lobes). The rocker cylinder (O10 x 9) and the M3 rod-end heads (~O10 x 5) over link 1b add height on the strip that is already the band-critical one. Complexity 42.5 on the pin-knee carrier. It is the fallback if the tail fails the band. |
| 4 | alignment-free-knuckle-4r | REJECTED (not a pick) | K is sensed, so it is 4 active. Measured 45.93 fast; hub 2 0.00 and link 2 0.065 in band at the distal J3 seats. Recorded lesson: J1 on the acromion top plus a J3 axis 38-48 deg off the humerus keeps th(J1,J3) >= 38 deg, so the J1-J3 alignment set leaves the workspace (kinematic 0.953, overhead 26/28). The body (J3 side) refuses it. |
| 5 | alignment-free-swivel-4r | REJECTED | The swivel is sensed (4 active), and no kit is built. Same J3-side limiter (hub 2 one-level 0.13-0.20 proxy, link 2 0.05-0.08). A 41-deg swivel arm rides over the acromion and trapezius under hub 1's sweep. |
| 6 | across-end-knuckle-4r | REJECTED | K is sensed (4 active). The raw kit measures 53.5-61.9 fast, with link 2 at 0.05-0.08 in band. Recorded: across-body 67/68 kinematic at J1 bvec(100,60) / J3 wdir(42,15), with hub 2 and K parked at 0.97. |
| 7 | knuckle-crest-hub3-4r | MERGED into pick 2 (its seat basin); rejected as a stand-alone | K is sensed (4 active). Quick crest tries scored 57-71, with hub 2 0.03-0.57, contradicting deltoid-crest-j3-3r's hub 2 of 0.82-0.997 (unresolved: a convention or an O15 effect). Its hub-3 seat map is the useful new knowledge and goes into pick 2's search. |
| 8 | link2-servo-saver-4r | REJECTED | Best 49.79 fast; hub K is 0.03-0.27 in band at every split. A two-sided preloaded K risks a branch jump through centre, and K is sensed (4 active). |
| 9 | knuckle-q3-gate-4r | REJECTED | It measured only losses: 27.09 at best against 22.26 without the gate, because the stop takes back exactly the reach the knuckle buys. A firm J3 twist stop is also felt at the cuff. |

## Ranking: expected gap reduction x confidence x buildability

All the survivors have 0 passive translations.

1. **geneva-tail-knuckle-pinknee-3r.**
   - Expected frozen 19-23 against H1's 24.48 / 27.20 at 3 active: -2 to -6.
   - Confidence about 0.55, because of the tail sweep.
   - Buildable: rollers, dowels, a clock spring.
2. **geneva-tail-knuckle-3r (+ crest basin).**
   - Expected 25-35 frozen, at complexity ~16 against H1's 21.5.
   - Confidence about 0.3.
   - Buildable: 4 hubs, one roller.

Lead order for the modeller (pick 1):

1. one tooth (kK_lo 0) and the exact contact law;
2. the tail metal, measured BEFORE any CMA;
3. a pressure angle above 45 deg counted as not taken (a curved flank);
4. L_t derived from bk2.

## Judge frozen check (section 4 result)

Run: one tooth (kK_lo 0), exact Geneva law atan(6 t), smhi 8, LB1 seats, `camBfrozen.py` (fit Bench(60,160) fast, worn
on Bench(110,360) exact). Law only: the tail metal is not modelled.

| | gap | score | reach | in-band14 | follow | contact | near-touch | overhead | min metal |
|---|---|---|---|---|---|---|---|---|---|
| frozen, judge | **21.32** | 92.2 | 0.731 | 0.902 | 0.946 | 0.039 | 24.11 | 7/28 | 0.02 mm |
| proposer's claim (two lobes, linear law) | 20.16 | 92.7 | 0.750 | 0.899 | | 0.046 | 22.80 | | |

Lost poses, frozen: fold 78, slide 7, parts 3, contact 15. The honest figure is 1.16 points worse than the headline.
It still beats H1's 24.48 / 27.20 at 3 active, before the tail metal.

The decisive unknown is now the tail metal. It must cost < ~3 points for this design to lead the 3-active class.

Also open: the 0.02 mm overhead pinch inherited from LB1. A near-touch CMA has to move it.
