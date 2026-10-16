# Round 3 ideation: judge and red team (2026-10-16)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275)); gap 0 is the real target. Rule: every joint
is a real component at its size, at most 2 passive translations (prefer 0), no undetermined passive coordinate,
exactly 3 active DOF, MVP1 unpowered.

Reference numbers: champion spherical 3R 68.93 (Bench(60,160) fast) / 75.94 (Bench(110,360) exact).
offset-skin-normal-3r (osn) k4216: 32.61 fast, verified 42.59 exact (frozen shape). The ~10-point fast-to-exact
inflation is the first thing to remember when a candidate claims "27.9 = score 89.9".

## Red-team measurements made by the judge

All runs on the leader's own model (docs/concepts/models/offset-skin-normal-3r.py, k4216, every VModel check on).
Scripts: scratchpad `r3judge/` (knee.py, sph0.py, c2c.py, knuckle continuity) and the farm job `.cache/r3judge/kx.py`.

| emulation (stage layer heights RAIL_H = CAR_H) | Bench(60,160) fast | Bench(110,360) exact |
|---|---|---|
| 4.0 (control: the 2 crossed RSR3M, osn as built) | 32.61 (reproduced) | 43.36 (reach 0.611, in-band 0.779, contact 0.024) |
| 3.0 (honest pin stack: IGLIDUR-PIN 4.5-5 / MR63ZZ pair 6 mm) | 30.11 (in-band 0.804) | 41.58 (reach 0.614, in-band 0.791, contact 0.021) |
| 2.0 (the proposer's number) | 27.89 (in-band 0.826) | 39.14 (reach 0.614, in-band 0.816, contact 0.021) |
| slides 0 (spherical reference, same seats and d3) | 33.40 (reproduced; hub 3 0.225 in band) | 41.73 (reach 0.617, in-band 0.784, contact 0.018) |

0. **Exact bench, headline (farm, 4 jobs, $0.17).** At k4216 on Bench(110,360) exact, the leader's offset and
   2 slides buy nothing over its own zero-passive spherical reference: osn 43.36, spherical reference 41.73,
   honest pin knee 41.58, 2 mm pin knee 39.14. The verifier's frozen-shape run gave 42.59; this control froze
   S_a 6.3 / S_t 7.5 and lands 0.8 higher. Reach is 0.611-0.617 in every variant, which is 28.3-28.9 gap points
   on its own. The fast bench's 0.79-point "offset gain" (33.40 vs 32.61) reverses on the exact bench. Under the
   tie-break the zero-passive spherical chain therefore ranks first. The pin knee's remaining case is b3 > 0.23,
   which slides could not afford (hub 3 is 0.507 in band with the knee vs 0.31 spherical).
1. **Pin knee / pinned cuff link.** The 27.89 claim reproduces exactly, but 2.0 mm layers are thinner than any real
   pin joint: two plates plus an iglidur sleeve and thrust washers stand 4.5-5 mm, an MR63ZZ pair 6 mm. The honest
   emulation is 3.0, giving 30.11 (score 89.1). The pin knee alone at k4216 does not cross 27.5 on the fast bench;
   it needs the re-CMA, and the exact bench (column 3) is what counts. Sensitivity: ~1.2 gap per mm of stage height.
2. **Knuckle cuff link.** The radial-closure root of the J2 knuckle is single-branch and continuous: over 350
   consecutive fit-clip frame pairs (snh seats, osn Design.ik), |dqk| p99 1.5 deg, max 2.0 deg, 0 pairs > 5 deg.
   Swing 9..35 deg, authority p1 26.5 mm/rad, 525 of 576 poses close (claims confirmed). The weak point is the
   premise: snh's in-band 0.891 comes from an unverified sweep record (under audit for skin-contoured plates).
3. **Closure-set arc knee.** 0.832 / 0.836 fold-free-and-closable at hK 75 / 90 reproduced, and the psi-free upper
   bound 0.973. But the prototype picks the root nearest psi = 0 independently per pose. Along the clips the root
   jumps 50-55 deg between consecutive frames in 4 of 41 pairs (hK 75) and 3 of 46 (hK 90) (p50 1 deg). These are
   branch switches a real knee cannot make, so the follow number is optimistic. Authority p5 10-13 mm/rad and p50
   29-33 mm/rad, i.e. 2-5.7 deg of knee per mm of radial GH translation or liner compression. R10's real GH
   translation (15 mm worst, rigid) can swing it by tens of degrees, so judge R10 before L1.
4. **Spherical reference.** The same zero-passive morphology at the same axes scores 33.40 in osn's VModel and 45.01
   in the kit (spine-parked-j2-3r's own run). One of the two models is ~12 points off. The verifier must settle this
   before any zero-passive number is quoted (column 3, last row, gives the VModel side on the exact bench).
5. **Fold.** Every candidate that does not touch the J2 fold keeps reach at 0.706 fast / 0.611 exact, i.e. 19-29
   gap points. **On the exact bench, gap <= 27.5 is impossible for any fold-untouched osn-seat design.** Even with
   in-band and follow perfect, reach 0.611 alone costs 28.9. A 90+ on the verifier's bench needs a fold lever
   (arc knee, rocker, arc-sector J2, frontier seeds) stacked on the best arm end.

## Verdicts

| # | candidate | verdict | reason |
|---|---|---|---|
| 1 | skin-normal-3r-pin-knee | **PICK 2** (merged with 2 and 6) | 0 passive translations; same exact closure as osn (planar RRR spans R + 2P), 4-5 mm lower stack; measured 30.11 fast at the honest stack, 27.89 at 2 mm; exact 41.58 (honest) vs the spherical reference 41.73: a tie at k4216, so it ranks behind the zero-passive chain unless b3 > 0.23 pays. |
| 2 | skin-normal-3r-pinned-cufflink | merged into pick 2 | Same mechanism (J3 + 2 pins parallel to J3, closing through GH). Its 45/30 link sizing, b3 freedom and triad elbow margins go into pick 2's sweep. |
| 3 | skin-normal-3r-knuckle-cufflink | **PICK 3** | 0 P, generic loop with M = 3, knuckle root continuous (measured). It is the buildable form of snh, but that premise is unverified and reach is lower at snh seats. |
| 4 | closure-set-arc-knee-3r | **PICK 4** | The only rotations-only lever on the fold with a measured upper bound (0.973). Downgraded for branch jumps (measured) and R10 conditioning. |
| 5 | spine-parked-j2-3r | **PICK 1** (merged with 7 and 8) | 0 passive. On the exact bench its VModel form (41.73) ties or beats every passive arm end measured at k4216, so it takes rank 1 by the tie-break. Does not cross 27.5 alone (reach ~0.61-0.64). |
| 6 | whitworth-j3-cuff | merged into pick 2 as fallback | Same planar closure with 1 translation and a taller stack (9 mm vs 4.5-6). It is strictly dominated under the tie-break, and is kept only if the pins fail the MVP2 out-of-plane moment. Its theorem (one slider suffices, a sleeve never closes, two offset axes sag) is new knowledge and is recorded here. |
| 7 | tilted-spherical-follower-slide | merged into pick 1 (bench) + R10 track | Its bench design is osn's spherical reference (33.40, reproduced). The horizontal base follower slide (15.2 -> 8.4 mm fit / 6.6 held-out) is an R10 option and belongs to judge/base_stage.py, not to the morphology ranking. The follower pad on skin over the acromion still has to be shown to set the slide within its stroke. |
| 8 | slim-hub-spine-parked-3r | merged into pick 1 | O15 slim J2/J3 is a joint-size lever (+2 gap, inside bench noise) and applies to every design; carried as rad2/rad3 in pick 1 and as a lever in pick 2. O15 wall: MVP1 only. |
| 9 | whitworth-j2-fold | not picked (rank 7, reserve) | 1 P. The proposer's own map caps hub 2 at 0.70 in band at a 20 mm offset (net ~-2 gap), and a 45-60 mm straight rail floats d^2/2R off the cap. Keep its 30-min kill test (a1 50 must beat 33.4) for when a slot is idle. |
| 10 | acromial-rocker-3r | **PICK 5** (S-U rod required) | Rotations only, a fold lever stackable on picks 1 and 2 (J1's line stays on GH). An S-S rod has an idle spin, which is an undetermined passive coordinate, so one end must be a miniature U-joint. Low confidence: proxy break-even, no gain at the leader's seats. Proceed under its kill test. |
| 11 | cap-rocker-3r | **rejected** | The kit already refuted the per-point proxy at these exact cap seats (102-107 / 63-72 vs 75.5 / 56.6). Unconstrained travel is a crank (+-140 deg) with dead points (follow 0.80-0.85), and there is a rod pinch at the acromion edge. Expected 35-60, by the proposer's own account. |
| 12 | j2-arc-sector-3r | **PICK 6** | 0 passive; a kit-measured fold gain (reach 0.82, closure 0.90 in the hub version) whose limiter (hub 2 / link 1 at 0.01-0.05) the off-axis arc rail moves to ~0.97 by centre rays. Link 2 (0.10-0.71) is unsolved. It needs the hub control (rail-elbow lesson). |

## Ranking (expected gap reduction vs the champion x confidence x buildability)

| rank | id | P trans | expected gap | confidence | role |
|---|---|---|---|---|---|
| 1 | spine-parked-j2-3r | 0 (0 passive at all) | 41.73 exact measured (VModel reference at k4216); kit 43-45 fast | high (measured exact) | ties the pin knee on exact with no passive joint: the base to stack a fold lever on |
| 2 | skin-normal-3r-pin-knee | 0 | 41.58 exact / 30.11 fast at the honest stack, k4216; better only if b3 > 0.23 pays after re-CMA | high | the arm end if the offset ever pays |
| 3 | skin-normal-3r-knuckle-cufflink | 0 | 26-32 snh seats, 15-25 with frontier seeds (claimed, fast) | medium-low | in-band ceiling with tilted J1/J2 |
| 4 | closure-set-arc-knee-3r | 0 | 25-45 | low-medium | the fold lever with the biggest bound |
| 5 | acromial-rocker-3r | 0 | leader +-5 | low | fold lever on pick 1 (kill test) |
| 6 | j2-arc-sector-3r | 0 | 35-50, below 27.5 only if link 2 routes | low | fold lever at J2 placement |
| reserve | whitworth-j2-fold | 1 | 30-40 | low | kill test only |

## What happens next (the loop)

1. The fold levers are where the 90 is: on the exact bench, reach 0.61 alone costs 28.6. Run picks 4, 5 and 6 in
   parallel, each with its kill test, on the zero-passive spherical base (pick 1). Port the winner onto it.
2. Pick 2 (pin knee): build the real model at the honest pin stack and run a farm CMA with b3 0.23-0.8 freed. Keep it
   only if the exact bench beats pick 1 by more than noise.
3. Pick 1 settles the VModel-vs-kit split (VModel 33.40 fast / 41.73 exact vs kit 45.01 fast) by running the kit
   model on the exact bench too.
4. The exact numbers in the table above come back from the farm (`.cache/r3judge/out_*.json`). Append them to
   docs/concepts/events.jsonl.

## Round 4

The round-4 judge (2026-10-16 ~05:45 UTC) is in docs/concepts/round4_ideation.md.
