# Independent check of the v2 effort film (2026-10-16, ~15:00-15:15 UTC)

The checker did not make the film. It re-measured the film against git at the stated snapshot (`d7f4bd2`, 14:43:57Z), using its own
recompute script rather than the producer's `snapshot.py`. It also checked the film against the user's 14:40 brief point by point,
and fixed one small error by re-running that step.

**Verdict: passes.** Every on-screen number reproduces from the repo. The score explainer matches the bench code exactly. Verified
and self-measured numbers are labelled correctly, and the brief is met. There was one fix, the frontier staircase (below). Three
choices in the leader chart are now disclosed in the README.

## 1. Numbers (frames pulled with ffmpeg at every number-bearing moment)

| on screen | recomputed from git `d7f4bd2` | |
|---|---|---|
| 821 commits, 43.0 hours | `git rev-list --count` 821; first 2026-10-14 19:45:28Z to last 2026-10-16 14:43:57Z = 42.97 h | ok |
| 108 designs | `docs/dashboard/data/morphs.json` 108 rows, no duplicate ids | ok |
| 805,852 configurations scored | 270,718 timed sweep rows (57 files, 270,737 rows) + 247,646 band evals (87 searches) + 186,248 zero-complexity (2,252 + 5,396 + 108,768 + 27,016 + 42,816, golden README) + 101,240 (`gks1_digest.json` n_ok) | ok |
| explainer: in-band 0.894, follow 1.00, reach 0.75, contact 0.028 | `rows/minarc-stop-knuckle-4r.json` `polished_bench.pick1`: 0.8941 / 1.0 / 0.75 / 0.0281 | ok |
| gap = 100 x [(0.90 - in-band)+ + (0.95 - follow)+ + (0.90 - reach)+] + 100 x contact | identical to `tools/concept_bench.py` `gap_of()` (line 54) and `tools/dash_build.py` | ok |
| = 0.59 + 0 + 15.00 + 2.81 = 18.40 | 0.59 + 0 + 15.00 + 2.81 = 18.40 = `polished_gap` | ok |
| score = 100 (1 - gap/275) = 93.31; 95 needs gap <= 13.75 | `tools/knee_polish.py` / `osn_polish.py` `score()`, dashboard `sc()`; 93.309; 275 x 0.05 = 13.75 | ok |
| meter targets 0.90 / 0.95 / 0.90, contact target 0 | same thresholds as `gap_of()` | ok |
| pick1 called "verified" | `polished_status` CONFIRMED by an independent verifier (events 13:46Z, reproduced to the digit) | ok |
| wall verdict: 13 verified, 11 refuted, 19 dead, 7 duplicates | morphs.json status counts 13 / 11 / 19 / 7 (+ 10 screened, 44 ideated, 4 modelling) | ok |
| montage, 10 scores and tags | every score = 100 (1 - g/275) of the row's `v_gap` (verified) or `gap` (else), all 10 reproduce to 0.01; "screen · dead / refuted" tags match status | ok |
| concept bench: 270,718; best 97.75 "refuted on re-measure" | min gap 6.19 (minarc, 08:12:02Z) = 97.75; all 3,374 rows above 95 are that one minarc file; refuted 09:45 / 09:49Z in events.jsonl | ok |
| GPU: 560,478 bounded, 186,248 fully scored, ceiling 88.71 | golden README 112,100 + 448,378; sum above; 31.04 exact frozen = 88.71 | ok |
| GPU plot: 154 basin dots, frontier table, score >= 95 zone | 154 basins with `best`; table (0.62, 0.890) ... (0.85, 0.420) matches the README; zone corners at 0.7625 measured on the frame | fixed (see below) |
| claims: 30 designs, "26 of 30 came in lower" | 30 rows with a moving claim / `v_gap` pair, 26 with `v_gap` > claim; 4 came in better (coupler-path-j1, geneva-tail-knuckle-3r, j2-arc-sector-3r, sliding-rivet-pauldron), all drawn that way | ok |
| minarc "gap 15.42 claimed -> 19.54 verified" | `v_gap_claim_reading` 15.42, `v_gap` 19.54 | ok |
| "polish P5: +3.11 claimed -> +0.16 held out · refuted" | `v_p5_gain` 3.11, `v_p5_gain_held` 0.16, `v_p5_refuted` true | ok |
| leader steps 75.83, 84.51, 88.96, 90.38, 92.89, 93.31; "1.69 points to go" | events.jsonl 20:32 (66.47), 00:32 (42.59), 03:58 (30.35), 06:30 (26.45), rows v_gap 19.54 (11:57), polished 18.40 (13:58); 95 - 93.309 = 1.69 | ok, choices disclosed |
| end card: 821 / 43.0 h, 108 / 13 verified, 805,852, 93.31 (gap 18.40), 95 (gap 13.75), snapshot 14:45 UTC | as above | ok |

**Leader chart choices.** These are not errors, but the chart reads "best independently verified score", so the README now
names the three verifier numbers it leaves out:

- spine-parked-j2-3r 34.29 (87.53) at 03:39. It was measured on O15 slim hubs, which the user's O20-only ruling voided, and the pin
  knee beat it 19 minutes later.
- H1's margin-5 reading 24.48 (91.10) at 06:30. The chart draws the lower polish-protocol number, 26.45 (90.38).
- minarc B's 18.45 (93.29) at 09:45. This was a re-measure of a refuted claim, before the stop tolerance was priced.

None of the three changes the end of the story (93.31, 1.69 to go).

## 2. The user's brief

| brief | finding |
|---|---|
| take away colour, match the main artifact's theme | Frames are measured from the encoded mp4 (ffmpeg signalstats, all 2280 frames). SATMAX is at most 6 on a 0-181 scale and SATAVG about 1. U is within 122-130 and V within 127-130 around 128. That is greyscale apart from the dashboard's own warm grey: the canvas is #1a1a19, and the largest R/G/B spread is 12, at #c3c2b7. Serif titles, sans labels, thin hairline axes, no accent colour. |
| no detailed CAD, just the basic ones | The production scripts read only `docs/dashboard/data/motion.json`, the data files and fonts; nothing comes from `renders/` or `pipeline/`. Every mechanism on screen is a monochrome motion preview: explainer, wall, montage and end card. |
| every design has a basic CAD | 108 of 108 morphs.json ids have a non-empty mechanism row in motion.json at `d7f4bd2`. The only extra row is `_shoulder`, the shared body. The wall at 0:43.5 shows 12 x 9 = 108 tiles. None is the "no preview" placeholder, and the 13 framed tiles match the 13 verified. |
| huge amount of simple tests, the graphs | The wall shows 108 designs, then a 10-cut montage. The graphs show 270,718 configurations, 154 basins and 30 claims. |
| less subtitles | There are no caption lines. The text is short labels: titles, axis names, and one tag per montage shot. The only sentence-length text is the formula and the three protocol chips, which the score story needs. |
| a bit faster paced | 76 s, down from v1's 88 s. 19 shots: the median shot is 1.1 s (the 10-cut montage), the median of the 9 non-montage shots is 6 s, and the mean is 4.0 s. The fully built formula holds about 2 s before the chips replace it; the same numbers return on the leader chart and the end card. |
| go over how the score is determined, to tell a story | 0:03-0:19: the four measurements with targets, the gap built term by term, the score, the 95 threshold, and the protocol chain (frozen, verifier, held out). The leader chart (1:04) closes the same story at 93.31, with 1.69 to go. |

## 3. File (ffprobe, after the fix)

`exo_effort_timelapse_v2.mp4`: H.264, yuv420p, 1920x1080, 30 fps, 76.000 s, 2280 frames (counted). It is 6,527,892 bytes
(6.5 MB) and has no audio. A full decode with `ffmpeg -f null` gives no errors.

## Fix made (re-ran the step)

- **GPU frontier drawn as a polyline.** The frontier table is a step function: each row is the best in-band at reach >= R, and holds
  until the next R. A straight line through its points put 8 of the 154 basin dots above the line labelled "frontier", at reach
  0.63-0.64, 0.72 and 0.83-0.84. The table itself has 0 violations. The checker redrew it as a staircase in `s4_graphs.py` (the
  original is kept as `s4_graphs.py.orig`), with the last step carried to the furthest drawn basin. It re-rendered only s4 frames
  240-419 (film 0:52-0:58) and re-assembled the film and contact sheet with the producer's `assemble.py`. All dots now sit on or
  under the line. Duration, frame count and every other frame are unchanged.

## Notes, no change

- The basic preview in the explainer is the design's dashboard preview. The numbers are pick1's, as disclosed in the README.
- The film is a 14:45Z snapshot and says so on the end card; the search has kept running since. The round-6 winner
  geneva-tail-knuckle-pinknee-3r (verified 23.57 at 14:30, score 91.43) is not a new leader, so it is drawn only in the claims chart.
  That chart uses its row (23.57), while the dashboard's morphs.json still reads 23.04, a known bookkeeping lag.
