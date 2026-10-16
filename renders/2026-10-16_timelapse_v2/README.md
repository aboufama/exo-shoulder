# Effort time-lapse v2, 2026-10-16

`exo_effort_timelapse_v2.mp4` is the second cut of the effort film. It follows the user's brief of 2026-10-16 ~14:40 UTC: no colour,
the dashboard's look, only the basic motion previews and graphs (no detailed CAD at all), a short label per shot instead of
paragraphs, a faster pace, and an explainer of how the score is determined so the film tells a story. The first cut stays in
`renders/2026-10-16_timelapse/`.

- **Format:** 76.0 s, 1920x1080, 30 fps, H.264 yuv420p (crf 20, preset slow, faststart), 6.5 MB, no audio.
- **Contact sheet:** `contact_sheet.jpg`, 24 evenly spaced frames with their timecodes.
- **Snapshot:** every number on screen was read from the repo at **2026-10-16T14:45Z** (HEAD `d7f4bd2`, 821 commits;
  `snapshot.py` in the production folder). The search kept running while the film was made, so every count is a snapshot.

## Look

- **Theme:** the dashboard's own dark theme (`docs/dashboard/simple/index.html` + `docs/dashboard/dash.css`, colours sampled from
  its rendered page): panel `#1a1a19` as the canvas, cards `#0b0b0b`, text `#f0efec`, muted text `#898781`, hairlines `#313130`,
  meter fill `#c3c2b7`. Neutral greys only, no accent (the dashboard draws its best-so-far line in the text colour, so the film
  does too). Measured on every 10th frame: the largest R/G/B spread of any pixel is the theme's own warm grey (see the check below).
- **Fonts:** the Anthropic fonts are not installed on this machine. Serif titles and numbers use **Caladea** (closest installed
  book serif to Anthropic Serif); labels use **Inter** (closest to Anthropic Sans).
- **Mechanisms:** only the basic monochrome motion previews of `docs/dashboard/data/motion.json` (the dashboard's tiny motion
  graphics, drawn by `docs/concepts/viz/thumbs.mjs` from `docs/concepts/viz/concepts/<id>.js` on the primitive mannequin):
  shoulder faint, mechanism in the text colour, joints thicker, frames advanced on the dashboard's own timer (93 ms
  per frame). All 108 designs have one (108 of 108 at the snapshot). No Cycles stills, no
  user-style CAD, no glb renders.

## Segments

| time | segment | on screen |
|---|---|---|
| 0:00-0:03 | title | "Every design we tested"; four cards count up to 821 commits, 43.0 hours, 108 designs, 805,852 configurations scored. |
| 0:03-0:19 | how a design is scored | The leader's preview (minarc-stop-knuckle-4r) moves through its loop. Four measurements appear one at a time, each with a tiny graphic and a dashboard-style meter (target tick, shortfall outlined): in-band (metal 2-14 mm from the skin) 0.894, follow (clip frames tracked) 1.00, reach (workspace poses taken) 0.75, contact (metal inside the body) 0.028. The formula builds term by term: gap = 100 x [(0.90 - in-band)+ + (0.95 - follow)+ + (0.90 - reach)+] + 100 x contact = 0.59 + 0 + 15.00 + 2.81 = 18.40; score = 100 (1 - gap/275) = 93.31; 95 needs gap <= 13.75. Then three chips: frozen on Bench(110,360) -> re-measured by an independent verifier -> checked on held-out poses. |
| 0:19-0:27 | every design tested | The wall: all 108 designs in ideation order (12 x 9), tiles popping in, then all moving in sync; the counter counts the tiles. |
| 0:27-0:38 | montage | 10 hard cuts, 1.1 s each, one preview large with only its score and a one-word tag, lowest to highest: seed-spm-3rrr 29.66 (screen · dead), back-anchored-ring-3r 57.71 (screen · dead), fivebar-roll 67.59 (screen · dead), slotted-eccentric-j2-3r 73.09 (screen · refuted), baseline-3r 74.93 (screen), floating-centre-3r 78.85 (screen · refuted), raglan-routed-3r 84.47 (screen), zc-frontier-3r 88.47 (verified), skin-normal-3r-knuckle-cufflink 89.42 (verified), minarc-stop-knuckle-4r 92.89 (verified). |
| 0:38-0:44 | verdict | Back to the wall: dead / refuted / duplicate tiles dim, the 13 verified tiles get a hairline frame; header "13 verified (framed) · 11 refuted · 19 dead · 7 duplicates". |
| 0:44-0:52 | every configuration screened | All 270,718 timed concept-bench configurations in run order (score axis, 95 dashed), revealed left to right with a counter and the best-so-far staircase (97.75 at the end, labelled "refuted on re-measure"). |
| 0:52-0:58 | GPU search of the simplest class | 560,478 zero-complexity configurations bounded, 186,248 fully scored, verified ceiling 88.71; reach / in-band plot: the 154 CMA basin optima (hollow), the reach / in-band frontier (line), the score >= 95 zone (dashed), "cannot reach 95". |
| 0:58-1:04 | claims, re-measured | Dot plot of 30 designs: self-measured claim (hollow) -> independent verifier (filled), score axis, 95 dashed; "26 of 30 came in lower"; minarc "gap 15.42 claimed -> 19.54 verified"; "polish P5: +3.11 claimed -> +0.16 held out · refuted". |
| 1:04-1:12 | the verified leader | Step chart of the best independently verified score over time, 95 goal dashed, ending at 93.31 (gap 18.40) and "1.69 points to go". |
| 1:12-1:16 | end card | 821 commits in 43.0 hours; 108 designs, 13 verified; 805,852 configurations scored; verified leader 93.31 (gap 18.40); the goal 95 (gap 13.75); snapshot time; the leader's preview. |

Each segment fades from and to the background over 5 frames; segments join by hard cuts.

## Every on-screen number and its source

Scores: score = 100 (1 - gap/275), shown to 2 decimals, rounded half-up like the repo's own `v_score` / `polished_score`
fields (so pick1's gap 18.40 shows 93.31 as in `docs/concepts/rows/minarc-stop-knuckle-4r.json`). No shown score crosses
90 or 95 by rounding.

**Repo activity:** commits = `git log --format=%at | wc -l` = 821; hours = first commit 2026-10-14T19:45Z to last commit
2026-10-16T14:43Z = 43.0 (this repo only).

**Designs:** 108 = rows of `docs/dashboard/data/morphs.json`; statuses {"screened": 10, "ideated": 44, "refuted": 11, "verified": 13, "dead": 19, "duplicate": 7, "modelling": 4}. Wall order = `t_ideated`
(else `t_screened`). Montage score = the row's `v_gap` when the status is verified ("verified"), else its `gap` ("screen", plus the
status when dead / refuted); the montage draws from the 51 rows that have a preview and a score above 0 (not the 44 ideated, 7 duplicate and 4 modelling rows,
which have no screening number, nor foldfree-rus-truss and coaxial-rus-turret at gap 275 = score 0), 10 picked at evenly spaced
ranks from lowest to highest.

**How a design is scored:** formula = `tools/dash_build.py` line 37 (`gap = 100 * (max(0, 0.90 - inband14) + max(0, 0.95 - follow)
+ max(0, 0.90 - reach)) + 100 * contact`); the worked example is minarc pick1, `polished_bench.pick1` of
`docs/concepts/rows/minarc-stop-knuckle-4r.json` (in-band 0.8941, follow 1.0, reach 0.75, contact 0.0281,
gap 18.4, score 93.31); the script asserts the four terms add up to the recorded gap. The preview on screen is the
design's dashboard preview (its file's best configuration), the numbers are the polished pick1's.

**Configurations scored (805,852):** 270,718 timed concept-bench rows (every `docs/concepts/sweeps/*.json`
except files starting with `_`, including `skin-normal-3r-pin-knee@1.json` under the id before `@`; 270,737 rows in
57 files) + 535,134 GPU evaluations = 247,646 band-evaluator evaluations of the 87
searches in `docs/dashboard/data/gpu_searches.json` (Oct 14-15) + 186,248 zero-complexity full-bench evaluations
(`docs/research/golden/README.md`, results table: 2,252 + 5,396 + 108,768 + 27,016 + 42,816) + 101,240 pin-knee polish
evaluations (`docs/research/golden/gks1_digest.json` n_ok). The 560,478 bounded configurations are not in this sum
(a bound is not a full score).

**Every configuration screened:** x = run order (rows sorted by their timestamp `t`, 2026-10-15T15:48:57Z to 2026-10-16T13:45:00Z); y = screening
score (gap clipped to 0..275); ticks mark where each 6-hour UTC boundary falls in that order. Best-so-far staircase = running
minimum gap (6.19 = 97.75, minarc-stop-knuckle-4r, 2026-10-16T08:12:02Z). The 3,374 rows above
95 are one batch of minarc-stop-knuckle-4r variant-B CMA rows written at 08:12 UTC, the stream behind the
claim the independent verifier refuted at 09:45 / 09:49 UTC (the claimed reading needs J2 stops 1.4-2 deg from the fold, under
the 5-deg rule; `refuted_by_prior_claim_bd`, `v_gap_claim_stops_kit_rule`); hence the label "refuted on re-measure".

**GPU search of the simplest class:** 560,478 = 112,100 + 448,378 Sobol configs bounded, 186,248 fully scored
(`docs/research/golden/README.md`); dots = the best of each of the 154 CMA / polish / frontier basins in
`docs/research/golden/gpu_frontier.json` (`basins[].best`: reach, inband14; dots outside the plotted window are not drawn);
frontier line = the README's "Reach / in-band frontier" table (best in-band14 at reach >= R), drawn as a staircase because
each row holds from its R up to the next R (the last step carried to the furthest drawn basin; the first cut drew a polyline
through the table points, which put 8 of the 154 basin dots above the line, fixed by the independent check, `CHECK.md`); the score >= 95 zone =
(0.90 - reach)+ + (0.90 - in-band)+ <= 0.1375 (it assumes follow >= 0.95 and no contact, the best case); ceiling = the class's
verified 31.04 exact frozen = 88.71.

**Claims, re-measured:** every `docs/concepts/rows/<id>.json` with both a self-measured `gap` (the claimant's own screening bench) and an
independent `v_gap` (Bench(110,360) exact, frozen shape, a separate verifier); for minarc-stop-knuckle-4r the claim is its
`v_gap_claim_reading` 15.42 (its row `gap` 6.19 is the refuted screening reading). The 10 rows whose
verifier reproduced the claim to the digit are not drawn (no movement): acromial-rocker-3r, back-anchored-ring-3r, fivebar-roll, offset-arc-selfalign, scapula-halo-track, seed-2r-cring, seed-arc-rails, seed-pauldron-shells, seed-spm-3rrr, trombone-arc. P5 = the pin-knee
polish candidate (`v_p5_gain` 3.11 in sample, `v_p5_gain_held` 0.16 on 1154 held-out poses, `v_p5_refuted` true).

**The verified leader** (each step is the verifier's number on the protocol of that day; the protocols changed, e.g. the pin knee
re-measured 27.20 at the 5-deg margin at 08:17, which was not a new best and is not drawn). Three verifier numbers are left out
on purpose, so a viewer should read the chart as the leader under today's rules: spine-parked-j2-3r's 34.29 (87.53) at 03:39,
measured on O15 slim hubs that the user's "Keep O20 only" ruling (05:50) voided (its row now reads 41.00), and beaten by the pin knee 19 min later;
the H1 verifier's margin-5 reading 24.48 (91.10) at 06:30, drawn instead at its polish-protocol number 26.45 (90.38, the lower one);
and minarc variant B's 18.45 (93.29) at 09:45, a verifier's re-measure of a claim it refuted, before the buildable stop tolerance was
priced (BDp 19.54 is the first confirmed minarc claim).

| time (UTC) | design | gap | score | source |
|---|---|---|---|---|
| 2026-10-15 20:32 | seed-offset-3r-slides | 66.47 | 75.83 | events.jsonl 20:32 verified seed-offset-3r-slides |
| 2026-10-16 00:32 | offset-skin-normal-3r | 42.59 | 84.51 | events.jsonl 00:32 verified offset-skin-normal-3r k4216 |
| 2026-10-16 03:58 | skin-normal-3r-pin-knee | 30.35 | 88.96 | events.jsonl 03:58 verified skin-normal-3r-pin-knee |
| 2026-10-16 06:30 | pin-knee polish H1 | 26.45 | 90.38 | events.jsonl 06:30 VERIFIER H1 CONFIRMED (polish protocol, margin 10) |
| 2026-10-16 11:57 | minarc-stop-knuckle-4r BDp | 19.54 | 92.89 | rows/minarc-stop-knuckle-4r.json v_gap / v_t |
| 2026-10-16 13:58 | minarc pick1 (polished) | 18.40 | 93.31 | rows/minarc-stop-knuckle-4r.json polished_gap / polished_t |

## Checks done

- Contact sheet and frames from every segment looked at; re-rendered: an icon that spilled out of its box, a caption that
  collided with the formula, a label running off the right edge, two labels colliding at the end of the leader chart.
- Colour: largest per-pixel R/G/B spread over every 10th frame = 12 (the theme's warm greys: #f0efec spreads 4, #898781
  spreads 8, #c3c2b7 spreads 12): the only tint is the dashboard's own warm grey, nothing else carries a hue.
- No detailed CAD: the film reads only `motion.json`, the data files above and the fonts; no image from `renders/` or
  `pipeline/` is used.

- Independent check (frames at every number-bearing moment, every number recomputed from git at `d7f4bd2`, the user's brief
  point by point, ffprobe): `CHECK.md`.

## How it was made

Local CPU only (no RunPod, no Cycles). Each frame is an SVG written by Python and rasterised with cairosvg (the concept-bench
point cloud is a numpy density layer composited under the SVG); frames encoded with ffmpeg. Production scripts (scratchpad, not
committed): `snapshot.py` (numbers), `common.py` (theme, previews), `s1_title.py` ... `s6_end.py`, `run.py`, `assemble.py`.
