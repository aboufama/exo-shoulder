# Alignment audit: weldk-overstrap-pinknee-3r (round 301, slice r301-A)

Auditor run 2026-10-19 (tool VERSION 2026-10-19.1, `python3 tools/alignment_audit.py audit weldk-overstrap-pinknee-3r
--ref conecut-knee-knuckle-3r`, then judgement and ledger).

## Verdict: WATCH (claim v_gap 45.96, score 83.3)

The ledger (`docs/alignment/ledger.jsonl`, `python3 tools/alignment_ledger.py get weldk-overstrap-pinknee-3r`) gives
**watch**, with 3 tool checks and 5 judgement findings, all at watch. There is no 'gamed' finding: the claim
reproduces, no hard rule is broken, and no finding moves the design's rank. The next verified rows are 44.79 above
and >= 60 below, at every reading below.

The claim stands as a number. It is not a better exo than its number suggests. One part of the number hides deep
contact (finding 1). The design is a stop on the verifier's word and on its own measured limiter: hub 3 sits inside the
bunched deltoid at the abduction cone.

## Re-wear (this audit, local CPU, exact path, frozen shape, models unchanged)

The model has no `frozen_held()`, and its `frozen()` returns a tuple, so the stock `remeasure` cannot wear it.
`tools/alignment_weldk_overstrap_adapter.py` is a new file. It gives the loaded model a `frozen_held()`: its own
`frozen()` with Bench(110,360) swapped for the H1-family held bench (`docs/concepts/verify/
skin-normal-3r-pin-knee-polish.py held_bench()`, the bench the lead's `frozen_held()` wears). It also captures the worn
(M, B) for the wear probe.

| wear | gap | reach | follow | ib14 | contact | <1 mm | <2 mm | <3 mm | band 3-14 | file |
|---|---|---|---|---|---|---|---|---|---|---|
| bench Bench(110,360) | **45.96** (reproduced) | 0.6306 | 0.9273 | 0.7415 | 0.009 | 53.04 (8) | 90.67 (49) | 123.47 (90) | 47.37 | `remeasure/weldk-overstrap-pinknee-3r_bench.json` |
| held out (1154 poses) | **51.09** (+5.13) | 0.6082 | 0.9208 | 0.7393 | 0.0292 | 57.54 (17) | 91.63 (83) | 123.45 (195) | 52.51 | `remeasure/weldk-overstrap-pinknee-3r_held.json` |

Held out sits +5.13 over the bench, under the 6-point watch line (held_out: ok). Wear probes are in
`remeasure/weldk-overstrap-pinknee-3r_{bench,held}_probe.json`. The jam-skin probe (new file
`tools/alignment_jam_skin_probe.py`) is in `remeasure/weldk-overstrap-pinknee-3r_{bench,held}_jamskin.json`; the
reference lead's run is in `remeasure/conecut-knee-knuckle-3r_bench_jamskin.json`.

## What the wearer gets (measured)

- **Overhead (ws elev >= 140): 7/28 taken on the bench, 11/71 held out.** Every bench take has metal at 0.29-2.61 mm
  (6 of 7 under 2 mm). All 10 overhead clip frames are taken, 8 under 2 mm and 5 under 1 mm. Held out, 9 of 11
  overhead takes are under 2 mm. In-band on the taken overhead poses is 0.91 (unscored).
- **Raised arm (ws elev 90-140): 37/85 taken (0.435)**, 11 of them under 2 mm. Held out: 74/229. Reach by elevation
  on the bench: 0-60 146/172, 60-90 37/75, 90-120 27/51, 120-140 10/34, 140-160 4/13, 160+ 3/15.
- **Taken poses with metal < 2 mm: 49 of 329** on the bench (8 under 1 mm, minimum 0.07 mm at ws 345) and 83 of 765
  held out.
- **Deepest contact.** Scored contacts on the bench are 3 poses summing 7.37 mm, the deepest 5.84 mm at ws (15 / 135 /
  -60). Held out: 23 poses summing 113.56 mm, the deepest 27.57 mm at ws (15 / 165 / 15) overhead; that is x1.86 the
  lead's 60.97 mm, just under the T5 2x line. **Unscored:** 14 bench poses scored as part jams have metal 2-33 mm
  inside the arm, mostly hub 3 at the cone: 209.13 mm summed, deepest 33.09 mm at ws 238 (15 / 165 / 0). Held out the
  count is 36 poses, 391.55 mm summed, deepest 33.14 mm. See finding 1.
- **Workspace in-band (unscored, taken ws poses): 0.711** bench and 0.711 held. The scored clip in-band is 0.7415.
  Part in-band: E 0.48, boss 0.19, pad 0.23, knee link 0.39, while the hubs and links are 0.87-0.99. The knee stack
  rides at 15-20 mm medians, and the part-weighted in-band is 0.662, 7.98 points below the sample-weighted figure
  (sampling: watch).
- **Springs, stops, cuff twist, singular postures.** There are no springs, no hub K, no drive and no J3 stop. The two
  knee pins are MR63ZZ pairs (stk 6.0) with a physical knee window. The knee is taken over 59.9-125.8 deg inside
  [31.2, 148.8], so the window margin is 23.0 deg and the knee moves (K.qb span 53.3 deg). The minimum th fold margin
  over taken poses is 5.262 deg. The minimum part clearance is 1.23 mm. Hubs are O20 at every joint. Continuity
  (verifier flood, 1432-pose grid): 1034 / 1034 connected, 0 islands, one knee branch. Cuff twist and R17 are not
  measured for this design: no dynamics judge has run, and none is due for a stopped design.
- Complexity 0.0 (recomputed), 3 active DOF, 0 passive translations.

## Findings

1. **NEW-jam-masks-contact (watch)**
   - **Evidence.** The H1 run loop (`skin-normal-3r-pin-knee.py` `_run_batched`) records a pose whose part clearance
     fails as not taken and never measures its skin distance. The bench counts contact only over measured poses
     (`concept_bench.py report()`). At this design's best config, 34 bench poses are part jams. 14 of them have metal
     inside the arm: all workspace, elev 90-165, 9 overhead, all `E-L2stack`. The deepest part is hub 3 on 11 of
     them. They sum 209.13 mm, and the deepest is 33.09 mm. Held out it is 36 of 78 jams, 391.55 mm.
   - **Why not better.** At those poses the exo blocks the arm while hub 3 presses 7-33 mm into the deltoid on the
     way there. The score charges only the lost reach. Read as contact, the bench gap is 49.97 (+4.01) and the held gap
     55.33 (+4.24).
   - The reference lead has 0 part jams on the same harness, so nothing is masked there.
   - The CMA neighbour reads 49.07 frozen with contact 0.0457, because the same cone poses are scored as contacts
     there. So the best's 3.11-point margin over its neighbour is about the 3.67 contact points the relabel removes,
     not shallower metal.
   - **Action.** Treat the 45.96 as "with 14 hidden presses". Any future pin-knee claim reports jam-skin.
2. **G1 (watch): metal hugs the skin overhead.** See the near-touch table and the overhead bullet above. The row's
   "overhead 7/28 (lead 8, H1 5)" compares takes that are all metal on skin on a real arm. This is report-only by the
   user's 2026-10-17 ruling.
3. **M4 (watch): the named feature is never exercised.** The E-over-link-2 crossover carries no taken pose: link 2 is
   under the E on 0 of 329. All 18 `E-L2stack` poses are jams, and the E ramps out of link 2's sector. The scored
   effects are a 3.15 mm rim lift and the jam relabel of finding 1. Complexity is 0 either way.
   - **Action.** Describe the design as H1's stack with the E ramped down. Do not carry "the crossover is free" as a
     lever without a pose that uses it.
4. **M3 (watch): a clash test was replaced by a narrower one.** The plan-view stacked test is blind to link 2 beside
   the E. The verifier priced it: the sharp edge reads 0.333 / 0.761 mm, and H1's kd bound gives 46.53 (+0.57). The E
   boss is 6.29 mm clear of hubs 1-2 and link 1.
5. **S3 (watch): the arm pad leg under kinv 1 is unsampled.** The inverted knee stack lifts the pad above the knee
   link. Its leg to the cuff (free sector 230 deg at 11 mm from pin b) is not sampled.

Tool checks at watch:
- **sampling**: part-weighted vs sample-weighted, see above.
- **reporting**: the verdict text reads as a screen; the dashboard's sweep best of 39.09 sits 6.87 below the verified
  number.
- **continuity**: this is an instrument miss, see proposal P-b. The verifier's flood is on file and clean.

Patterns walked and not present:
- T2: the band read 3-14 costs +1.41.
- T3: th is read in the kit metric, 5.262.
- T4: ang_min is 31.2, inside the searched 26.2-33.8 and above H1's 30.46.
- T5 scored: x0.36 bench, x1.86 held.
- S1/P1: held +5.13.
- S5: flood clean.
- M1/M2: O20, MR63ZZ, 0 translations.
- M5/G2/G3: no springs.
- G4: margins as above.
- G5/G6: complexity 0, 3 active.
- P2: no held import in the model or sweep.
- P3/R3: best and neighbour both reported, top-5 spread 0.33 fast.
- P4: no judge file in the row's 2 commits.
- R4: dashboard v_gap 45.96 matches.

## Proposals (proposals only; not inputs to the verdict)

- **P-a: count a part-jam pose with metal inside the skin as contact** (catalogue entry T6 "jam masks contact"). This
  is a measurement change for the H1-family run loop: still not taken, but recorded with its negative distance.
  Measured effect:
  - this row: bench 45.96 -> 49.97, held 51.09 -> 55.33;
  - conecut-knee-knuckle-3r: 0 jams, so no change.
  - Every other verified pin-knee or knuckle row is still to measure: `CB_EXACT=1 python3
    tools/alignment_jam_skin_probe.py <id> <out> [Class] [bench|held]` takes 10-40 s per wear.
  - Proposed catalogue entry: *T6. Jam masks contact. Looks like: few contacts, many part jams at the poses where the
    metal is deep in the skin. Why not better: the exo blocks the arm with metal already pressing into it. Detect:
    jam-skin probe; watch when the masked presses read as contact would move the gap > 2 points or the masked depth is
    > 2x the reference's scored depth.*
- **P-b (instrument): `continuity` should read a verifier's `flood` record** (`grid / kin_ok / connected / islands /
  taken_bench_ws_islands`, as in `verify/weldk-overstrap-pinknee-3r_v_bench_frozen.json`). Today it reports "no flood
  on file" for a clean 1034 / 1034 flood.
- **P-c (instrument): the `idle` check parses "no K / drive" in the row's name as a declared K and crank.** Here this
  is harmless, because the check is ok on the knee span.
