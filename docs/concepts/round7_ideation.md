# Round 7 ideation: judge and red team (2026-10-16 ~15:33 UTC)

Target: bench score >= 90, i.e. gap <= 27.5 (score = 100 (1 - gap / 275), tools/concept_bench.py). The real target is
gap 0, and 95 (gap 13.75) at low complexity. Rules (CLAUDE.md "Manufacturable joints only"):

- every joint is a real component at its size;
- at most 2 passive translations (prefer 0, then 1);
- no undetermined passive coordinate;
- MVP1 unpowered, exactly 3 active DOF.

Leader to beat: geneva-tail-knuckle-pinknee-3r, rod embodiment. Verified at 23.57 on Bench(110,360) exact frozen
(score 91.43), held out 28.12. On the fit bench Bench(60,160) fast it scores 16.53. Its complexity is 42.5 by hand and
46.75 from a full tools/simplicity.py record.

## Red-team measurements made by the judge

The scripts are in the session scratchpad: `r7j_q2.py` and `r7j_chk.py`. They load the winner model
(docs/concepts/models/geneva-tail-knuckle-pinknee-3r.py) with the verified params from `ddk/w.json`.

1. **The direct-pair numbers reproduce to the digit.** On Bench(60,160) fast, with `tail=0` (drive metal deleted, law kept):

   | variant | gap | reach | in band | contact | dK max |
   |---|---|---|---|---|---|
   | winner law | 11.79 | 0.794 | 0.894 | 0.005 | 53.4 |
   | kK 0.6 / smhi 28 | 14.38 | 0.756 | 0.907 | 0 | 36.0 |
   | kK 1.0 / smhi 20 / a1max 50 | 13.76 | 0.775 | 0.887 | 0 | 31.3 |

   - The rod drive's metal costs 4.74 fast points (16.53 -> 11.79). That confirms the round-7 sample arithmetic.
   - The laws that a compact direct pair can carry cost 2.0-2.6 of those points back.
   - The lobe metal decides the rest. That part is not yet measured.
2. **The groove's dwell is large.** On the fit bench, the winner's q2 stops are 93.4 and -5.0 deg. The state-A poses it
   takes span q2 -3.6..91.5 deg, and the whole taken q2 span is 110 deg.
   - The groove's dwell arc (a circle of radius 14.3 about u2) must cover about 98 deg of q2.
   - The low-gain rise then adds about 60 deg of q2 travel (about 26 deg of plate).
   - The groove plate is therefore a flange sector of about 125 deg, about r 10.2-18.4 on the dwell and out to 28 mm on
     the rise. Its outer wall forces the lug one layer above the plate (+3 mm).
   - The precedent is cam-unfold's O30 flange, which scored about 3 points worse than its crown cam.
   - The roller embodiment has no dwell metal. Its lobe turns away from the roller in state A.
3. **The k-rim stub clashes with hub K.** The stub tip sits at L_stub 25 + rr 2.5 = 27.5 mm from u2. When it points at
   K it is 37.8 - 27.5 = 10.3 mm from uK, which is 0.3 mm off hub K's O20 rim. The part-pair rule is 1 mm.
   - The fix is L_stub <= 24.3 (L_stub + rr <= D - 11) or bk2 >= 39. Either fix moves the law, and the pressure angle is
     already 43.9 against the 45 gate.
4. **Split knuckle: "hub 2 does not move when K2 folds" is wrong.** With a1 fixed, shortening a2e keeps u2 at a1 from
   u1, but u2 rotates around J1 on that circle. Hub 2's level at the folded poses has to be measured.
   - The folded side holds only 23 of the 84 fold losses on the verify bench (8 on the fit bench), from the
     two-rise-lobe split. The folded relief can therefore add at most +0.064 reach.
5. **The front-load and stop-B numbers agree across two proposers.** Raising stop B to a1max 64 alone leaves 268
   workspace poses, in both frontload and long-a2-bilobe. The m3e wall holds 49 of the 61 stretched losses, so the
   ceiling is about +0.03 reach.
   - The only metal measurement is a loss: 17.11 against 16.53, seats not re-fitted.
   - At kK 6-9, r_horn 1.0-1.5 turns 0.05 mm of rod-end play into 2-3 deg of K slop, so the 2:1 rocker is mandatory.
6. **Force closure (roller embodiments).** K is held by a unilateral contact plus the clock spring. The cuff load as
   well as gravity can lift K off the law. The positive groove removes this question. Every spring embodiment carries a
   force-closure gate.

## Verdicts

| candidate | verdict | reason |
|---|---|---|
| two-rise-lobe-pinknee-3r | **dead** (kill gate fired, proposer's own measurement) | See note A. |
| frontload-lobe-stopb-knuckle-3r | **pick 4** | See note B. |
| split-knuckle-twosided-3r | **pick 3** | See note C. |
| rim-lobe-arm-knuckle-3r | **pick 1** (merged with groove-arm) | See note D. |
| k-rim-lobe-stub-knuckle-3r | **pick 2** | See note E. |
| groove-arm-knuckle-3r | **merged into pick 1** as the 'groove' embodiment | See note F. |
| long-a2-bilobe-knuckle-3r | **rejected: duplicate, already measured** | See note G. |
| recentred-knee-geneva-3r | **not picked: a parameter tweak of the winner** | See note H. |
| narrow-cone-j3-knuckle-3r | **not picked (rank 5): long shot** | See note I. |

**A. two-rise-lobe-pinknee-3r (dead).**
- The folded side holds 23 of 360 poses.
- msub at the folded onset is 2.14 deg, so 0 poses are taken under the winner's rules.
- With metal fitted, hub 2 needs 63-70 mm or has no valid level, against 60.2. The fit drops every folded pose, and the
  fast gap goes 16.53 -> 18.61.
- A 750-design re-seat scan gave a best metal fit of 33.46 fast.
- Rule question for the lead: is msub still needed for a cam-slaved K? It is moot here, because the metal kills the
  design.

**B. frontload-lobe-stopb-knuckle-3r (pick 4).**
- Real but small: +9 kinematic workspace poses at most (277 vs 268). The m3e wall caps it at about +0.03 reach.
- Its one metal fit went the wrong way (17.11 vs 16.53), and it keeps the rod drive.
- Picked as the in-family stretched-side control, with a hard gate: the re-fit must reach fast < 16.0.

**C. split-knuckle-twosided-3r (pick 3).**
- It is the only surviving folded-side lever. It moves the relief to link 2, where cam-unfold-4th took 18 folded fit
  poses and the link-1 versions took 0-1.
- The kinematic bound is +16 to +27 workspace poses.
- Complexity about 55 (+12). The folded ceiling is +0.064 reach. Hub 2 moves (judge red team, point 4).
- 15-min kill gate first.

**D. rim-lobe-arm-knuckle-3r (pick 1, merged with groove-arm).**
- It deletes the drive metal that is 0 % in band (4.74 fast points, re-measured).
- The low-gain law costs 2.6 points (re-measured: 14.38).
- The compact lobe is feasible only at kK <= 0.6 with an O5 roller.
- Complexity 34.0 (roller) or 30.75 (groove), against 46.75.
- Highest confidence × buildability.

**E. k-rim-lobe-stub-knuckle-3r (pick 2).**
- Best law-only number (13.76, re-measured). The big part rides the member that moves least.
- As proposed it fails the 1 mm part-pair rule against hub K (0.3 mm), and pa is 43.9 against the 45 gate.
- Same complexity as D, 34.0.

**F. groove-arm-knuckle-3r (merged into pick 1).**
- Same pair, same law and same lug as D.
- Its unique gains: no spring, no stop A, hub K 6 mm lower, positive determination with no lift-off and no force
  closure.
- The cost the judge measured: a dwell of about 98 deg of q2, which makes a flange sector of about 125 deg, with the lug
  a layer up.
- Its folded second rise is already measured dead (A).
- Screened as an embodiment switch inside D, not as its own row.

**G. long-a2-bilobe-knuckle-3r (rejected: duplicate, already measured).**
- Its mechanism is the two-rise lobe (A), and A's 750-design scan covered its long-a2 seats (a2 69-80): 36-79 folded
  poses kinematically, best metal fit 33.46 fast, hub 2 at 0.02-0.82 in band.
- Its stop-B half equals frontload (B), and its measurements agree with B's. The B row carries that half.
- a2 61-68 is untested, but A's kill (hub 2 into the body when K opens at the folded end) applies at every a2.

**H. recentred-knee-geneva-3r (not picked: a parameter tweak of the winner).**
- The knee losses are on the stretched side (d 92-101 against d_max 92.6). That is real.
- lc 34 / phib -75 gives +5 bench / +18 held-out workspace poses, kinematics only.
- The fit cost is 18.11-18.40 against 16.73, with contact up to 0.016. The upside is +2 of 28 overhead.
- Recommendation to the lead: add lc, phib, phiE and lE to the free set of the env-bench polish (tools/env_polish.py),
  where the knee-band poses enter the fit.

**I. narrow-cone-j3-knuckle-3r (not picked, rank 5: long shot).**
- The overhead-spread kinematics are real (ideal 19-21 of 28 one-sided).
- Every metal fit was bad: best 31.86, 37.34 at L2 0.40 in band, and 375 on parts at the J2 re-seat.
- Clip follow drops to 0.92.
- Keep it for a later round, after a proximity-atlas L2 height check.

## Ranking

Score = expected frozen gain against the leader 23.57 × confidence × buildability. Every pick has 0 passive
translations and 3 active DOF, so buildability ranks on complexity and feasibility margins.

| rank | id | expected frozen | confidence | complexity | first test (kill gate) |
|---|---|---|---|---|---|
| 1 | rim-lobe-arm-knuckle-3r (roller / groove) | 21.5-22.5 | medium-high | 34.0 / 30.75 | metal fast fit <= 15.5 near-touch, either embodiment |
| 2 | k-rim-lobe-stub-knuckle-3r | 21-22 | medium | 34.0 | stub >= 1 mm off hub K at every pose, pa <= 45; fast <= 15.5 |
| 3 | split-knuckle-twosided-3r | 19-21.5 (upper bound) | low-medium | ~55 | >= 6 of 8 fit / 15 of 23 verify folded poses with hub 2 / K2 / hub 3 within fit levels |
| 4 | frontload-lobe-stopb-knuckle-3r | 21-23 | low-medium | 46.75 | re-fitted fast near-touch < 16.0 |

Picks 1 and 2 are the complexity route: the same or a better score at 31-34 against 46.75. Picks 3 and 4 are the reach
route on the two sides of the fold.

None of the picks reaches 95 on its own. The arithmetic that remains:

- ib about 0.90 from the direct pair, plus reach 0.775, gives gap 13.75.
- That needs +16 workspace poses on the verify bench.
- The folded relief (pick 3) is capped at +23 and the stretched side (pick 4) at about +12 (more needs a longer a2,
  which parks hub 2 into the body).
- The likely path is a direct pair (1 or 2), then the folded K2 (3), then the 4.7-7 point fast-to-frozen loss in the
  lead's env-bench polish.

## Next

Screen the 4 picks in parallel, each kill gate first. The winner of 1 and 2 becomes the drive for 3's composition. The
lead's env-bench polish takes the recentred-knee parameters (H).
