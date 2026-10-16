# Board 1: "the scale of the search" (32.0 s preview film)

Storyboard for the 30-40 s preview film that replaces the 76 s v2 cut (`renders/2026-10-16_timelapse_v2/`). This is
angle 1 of two competing boards. The hook is the sheer volume: one design multiplies into 108, and then into 805,852
scored configurations. After that comes the yardstick, which shows how one number is made in 7.5 s of pictures and
no formula. The search then runs past on that yardstick, the claims are re-measured, and the verified leader climbs to
93.31 against the dashed 95. Critics who did not make this board judge it. Its maker does not.

**The job, as verbs** (Rieseberg: replace nouns with verbs). In 32 s, make a busy stranger, with the sound off and on a
phone, believe that this search is **HUGE** (108 designs, 805,852 configurations), **HONEST** (dead tiles stay on
screen, 26 of 30 claims came in lower) and **CLOSE** (93.31 against 95). Then make them **WANT** to open the
dashboard. Every shot below names the verb it serves. A shot that serves none gets cut.

**Takeaway test** (altitude): after one viewing, a cold critic should be able to write "an automated search tried 108
exo designs and ~806k configurations; outside checks cut most claims; the verified best is 93.31 of a 95 target and it
is still running." The cut passes only if the critics' sentences match this one.

## Snapshot and sources

- Numbers come from the snapshot checked in v2's `CHECK.md`: HEAD `d7f4bd2`, 2026-10-16T14:43:57Z, 821 commits.
  `morphs.json` there has 108 rows and `motion.json` has 108 of 108 previews. The producer must re-run `snapshot.py`
  at render time, and the number-checker re-derives everything from git.
- **Preview gap at today's HEAD (`49c90fc`):** `morphs.json` now has 112 rows, but only 108 have a preview. The
  missing ones are the four Round-7 picks: `frontload-lobe-stopb-knuckle-3r`, `k-rim-lobe-stub-knuckle-3r`,
  `rim-lobe-arm-knuckle-3r` and `split-knuckle-twosided-3r`. The user's brief is "make sure every design actually has
  a basic cad", so the wall must show N of N. There are two ways to do that. One is to draw the four previews first
  (`docs/concepts/viz/README.md`: concept file, `node docs/concepts/viz/test.mjs <id>`, `node
  docs/concepts/viz/thumbs.mjs`). The other is to hold the `d7f4bd2` snapshot. A partial wall is never acceptable.
- The leader is minarc-stop-knuckle-4r **pick1**: `docs/concepts/rows/minarc-stop-knuckle-4r.json`,
  `polished_bench.pick1` = in-band 0.8941, follow 1.0, reach 0.75, contact 0.0281, gap 18.40, score 93.31. Its
  `polished_status` is CONFIRMED by an independent verifier. The 95 target is gap 13.75. The formula is
  `tools/concept_bench.py` `gap_of()` (line 53): score = 100 (1 - gap/275).
- **Verified vs self-measured:** a filled dot means an independent verifier's number. A hollow dot means the
  claimant's own screening number. A hollow dot with a slash means a design whose status is dead. The same coding is
  used in every shot.

## Look (unchanged from v2, which the user accepted)

- Greyscale in the dashboard theme. Canvas `#1a1a19`. Takeaway text `#f0efec`. Context `#898781`. Hairlines `#313130`.
  Dimmed tiles `#4a4947`. No accent colour.
- Fonts: Caladea for numbers, Inter for labels.
- Only the basic motion previews from `docs/dashboard/data/motion.json` (60 frames, advanced on the dashboard's own 93
  ms timer). No CAD, no Cycles, nothing from `renders/` or `pipeline/`.
- **Type for a phone** (derived: a 1920x1080 frame on a 390-pt phone held upright shows at scale 0.20, and the iOS
  floor is 11 pt):

  | element | size |
  |---|---|
  | hero numbers | 180 px Caladea (17 % of frame height) |
  | labels | 56 px Inter |
  | secondary text | 40 px, muted colour |
  | anything | 36 px minimum |

  The takeaway is always the biggest and brightest element. The punchline is never in the muted colour.
- **Scale of the previews:** a hero preview fills at least 60 % of the frame height (about 700 px). Strokes are set in
  screen px rather than scaled with the drawing:

  | part | stroke |
  |---|---|
  | mechanism | 3 px `#f0efec` |
  | joints | 6 px |
  | body | 2 px at 35 % |
- **One shared score axis:** up is always better, and the dashed 95 line sits at the same screen height (y = 250 px)
  in every chart shot (S04, S11, the montage ruler, S24, S25). The line the film is about never moves. It answers
  Tufte's "compared to what?" in every shot.
- **Cuts:** hard cuts only, on the beat of 120 BPM (one beat = 15 frames at 30 fps). There are no fades through the
  background. v2's 5-frame dips read like a slide deck.
- **Motion curves** (Material):

  | motion | curve | duration |
  |---|---|---|
  | enter | cubic-bezier(0, 0, 0.2, 1) | 225 ms |
  | exit | cubic-bezier(0.4, 0, 1, 1) | 195 ms |
  | on-screen move | cubic-bezier(0.4, 0, 0.2, 1) | 300 ms |
  | full-frame change | (same as on-screen move) | 375 ms |

  A data transition is one stage of about 1 s with slow-in slow-out (Heer & Robertson). There is no rotation. Changes
  that are the same happen together (common fate), and different changes are staggered.

## The board

Times are film time, and frames are at 30 fps. "Words" counts every on-screen token, with each number counted as one
word.

### Act 1: HUGE (0:00-0:08)

| # | time (frames) | picture | words on screen | motion | data source | principles |
|---|---|---|---|---|---|---|
| S01 | 0:00.0-0:01.0 (0-30) | The leader's preview, alone and huge (~700 px tall), centred on the canvas, arm rising. No title card. | "shoulder exo" (56 px, enters at frame 6). 2 words. | Preview plays from frame 1 at the dashboard timer, starting at the 11-frame window of its 60-frame loop with the largest mechanism displacement (the raise). Label fades up over 225 ms. | `motion.json` row `minarc-stop-knuckle-4r` + `_shoulder` body | Hook is motion on frame 1 with no title slide (IEEE VIS; Meta 3-s hook). Concrete before abstract (3B1B): the thing before any number. Subject fills ≥ 60 % of the frame. **Verb: WANT.** |
| S02 | 0:01.0-0:03.0 (30-90) | The same preview turns out to be one tile of a 12 x 9 wall of all 108 designs. Tiles are laid out in ideation order (`t_ideated`). The leader sits at row 9, column 9. | "108" (180 px) + "designs" (56 px). 2 words. | The camera zooms out from the leader's tile, scale 7x to 1x over 1.0 s on the standard curve, so it is one global change. The other tiles pop in as a ripple outward from the leader, by distance, 225 ms enter each, staggered over 1.1 s. The counter runs 1 → 108 in step with the pops. Everything has settled by frame 65, and "108" then holds 25 frames. All tiles animate in sync. | `motion.json` (108 previews), `morphs.json` (`t_ideated`, ids) | "One design multiplying" is the angle's hook. Small multiples, not one animated chart (Robertson 2008, Tufte). Common fate. A hero number holds ≥ 25 frames after it settles (Netflix minimum event). **HUGE.** |
| S03 | 0:03.0-0:04.5 (90-135) | The same wall, still moving. Dead (19), refuted (11) and duplicate (7) tiles dim to `#4a4947`. Then the 13 verified tiles get a 2 px `#f0efec` frame. Screened, ideated and modelling tiles stay as they are. | "13 verified" (180 px). 2 words. | On beat 1 (frame 90), the dimming happens as one 300 ms change. On beat 2 (frame 105), the frames draw on with 225 ms enter, and the hero enters at the same time. The hero holds 30 frames. | `morphs.json` status counts at the snapshot: 13 verified, 11 refuted, 19 dead, 7 duplicates | An honest teaser keeps failures on screen (SIGGRAPH research guide; the critiques of Boston Dynamics edits). Two staggered stages, not one compound change (Heer). One number. The label is "108 designs", never "108 tested": at the snapshot, 44 are only ideated. **HONEST.** |
| S04 | 0:04.5-0:06.5 (135-195) | Hard cut on the beat to the cloud. Every concept-bench configuration is one point: x is run order, y is score (0-100). The cloud is drawn as a grey density layer (`#898781` rising to `#f0efec` where points are dense), with a dashed 95 line. The 3,374 rows above 95 (one minarc variant-B batch from 08:12 UTC) are drawn in `#4a4947` with a hairline outline, and tagged. | "270,718" (180 px) + "screened" (56 px) + "95" on the dashed line (40 px) + "refuted" beside the grey patch (40 px). 4 words. | The points fill left to right in run order over 33 frames on the standard curve. The counter rises with the fill, and it settles and holds 27 frames. There is no best-so-far line, so nothing above 95 can read as a result. | `docs/concepts/sweeps/*.json` (57 files, 270,718 timed rows, files starting with `_` excluded, id = stem before `@`), y = 100 (1 - clip(gap, 0, 275)/275). Refuted batch: `events.jsonl` 09:45 / 09:49 UTC, v2 `CHECK.md` | "Huge amount of simple tests", from the user's brief. Compared to what: the dashed 95. Never let the refuted 97.75 read as a result (honest teaser). One graph for this verb (v2 had two scale graphs within 12 s). **HUGE.** |
| S05 | 0:06.5-0:08.0 (195-240) | The cloud compresses into a horizontal bar, sized for 270,718 at the scale where 805,852 = 1,600 px. Three more segments slide in from the right, one per eighth note, with hairline gaps between them: 247,646 band-evaluator evaluations, 186,248 simplest-class full-bench evaluations, and 101,240 pin-knee polish evaluations. | "805,852" (180 px) + "configurations scored" (56 px) + "GPU" over the three new segments (40 px). 4 words. | The cloud collapses into the bar in one 375 ms move. Segments enter 225 ms each, 7 or 8 frames apart. The counter continues from 270,718 to 805,852 without resetting. Everything has settled by frame 215, and the hero holds 25 frames. | 270,718 as above. `docs/dashboard/data/gpu_searches.json` (87 searches, 247,646). `docs/research/golden/README.md` (2,252 + 5,396 + 108,768 + 27,016 + 42,816 = 186,248). `docs/research/golden/gks1_digest.json` n_ok 101,240. The 560,478 bounded configurations are **not** in the sum, because a bound is not a score. | One hero number per shot (Duarte, Gallo). Each count carries its unit: configurations, not designs (Tufte). The counter continues so the viewer reads one growing number, not two. **HUGE.** |

### Act 2: the yardstick, "how one number is made" (0:08-0:15.5, pictures only, no formula)

These four shots use the same layout, so the eye learns it once. Each has a large picture (top 70 % of the frame), a
label at the top left, and one **meter** rail at the bottom. The meter fills to the value, a 3 px tick marks the
target, and the shortfall between them is outlined. No digits are shown, because the meters do the work. All four
pictures are pick1 on Bench(110,360) (the producer's dump, below).

| # | time (frames) | picture | words on screen | motion | data source | principles |
|---|---|---|---|---|---|---|
| S06 | 0:08.0-0:09.0 (240-270) | A histogram of pick1's metal-to-skin distances, 0-30 mm, with one overflow bar. The 2-14 mm band is a `#313130` panel behind the bars. Bars inside the band are `#f0efec` and bars outside are `#898781`. | "2–14 mm from skin". 4 words. | The bars rise together over 0.4 s with deceleration. The band panel fades in 225 ms. The meter fills to 0.894, next to the tick at 0.90, so the shortfall sliver is tiny. | The dump's per-sample distances over taken clip frames, which is the population the in-band metric uses (`concept_bench.py` `report()`). It must reproduce in-band14 0.8941. | Concrete before abstract: the measurement as a picture before it is a number (3B1B). One idea per figure (SIGGRAPH guide). Label ≤ 4 words. **CLOSE.** |
| S07 | 0:09.0-0:10.0 (270-300) | A filmstrip of 110 clip frames, drawn as 110 slim upright cells across the frame. | "follows the arm". 3 words. | The cells light left to right over 0.5 s, and all 110 end up lit. The meter fills past its tick at 0.95. | Bench(110,360): n_clip 110. pick1 follow 1.0, so 110 of 110. This is an exact count and needs no dump. | Same as S06. A met target looks met, with no outline. **CLOSE.** |
| S08 | 0:10.0-0:11.0 (300-330) | 360 workspace poses as dots. x is the plane of elevation and y is the arm elevation, so overhead is at the top. 270 dots are taken and filled. 90 are missed, drawn as hollow muted rings, and they cluster overhead. | "reaches the pose". 3 words. | The dots enter as one 225 ms stage. The taken dots then fill as a second 0.6 s stage, and the hollow dots stay. The meter fills to 0.75 against the tick at 0.90, so the shortfall outline is wide. | The dump's taken mask over the bench's 360 workspace poses, with angles from `_select(110, 360)`. Cross-check: `docs/research/minarc_final_polish/verify/v_pick1_fit60_bench_conn_taken.json` `bench110_360` = ws 360, connected 270. | The shortfall is visible here, because reach is where the gap lives (CLAUDE.md "the gap IS reach"). It is set up for S10's "mostly reach". At most 2 stages (Heer). **CLOSE.** |
| S09 | 0:11.0-0:12.0 (330-360) | The same dot field, plus S07's filmstrip as a thin row under it. The poses where metal goes inside the body get a 4 px × mark, about 13 of them (the exact count comes from the dump). | "touches skin". 2 words. | This is a match cut: the dots do not move. The × marks pop in on one beat (225 ms) and pulse once. The meter is a penalty bar from the left end: a short fill to 0.028 against a target tick at 0. | The dump's min distance < 0 over all solved poses, clip plus workspace (`report()` contact). It must reproduce contact 0.0281. | Honest: the leader does touch the skin on a few extreme poses (the pick1 red team found that contact is structural there), and the film shows it rather than hiding it. Match cut. **HONEST.** |
| S10 | 0:12.0-0:14.0 (360-420) | The four meters return stacked as small multiples. Each row starts with a tiny icon taken from its picture (histogram, filmstrip, dot, ×) and has no words. The outlined shortfalls then slide out and join end to end into one bar: in-band 0.59, follow 0, reach 15.00, contact 2.81. | "gap 18.40" (180 px) + "mostly reach" (56 px, `#f0efec`; this is the insight, not context). 4 words. | The rows enter together in 6 frames. Then all three shortfalls move as a single 0.9 s stage on the standard curve, and the joined bar draws its total. Everything has settled by frame 393, and the hero holds 27 frames. | `polished_bench.pick1`. `gap_of()` gives 0.59 + 0 + 15.00 + 2.81 = 18.40. The terms are drawn to scale, so reach is 82 % of the bar. | The formula as a picture: "4 measurements → 1 number", never a two-line equation (style guide A). One data stage of ~1 s (Heer). Small multiples for the comparison. **CLOSE.** |
| S11 | 0:14.0-0:15.5 (420-465) | Hard cut. A vertical 0-100 score bar (a thermometer) on the shared axis, filled to the top, with the dashed 95 across it. The gap drains from the top as 18.40 / 2.75 = 6.69 points, leaving the bar at 93.31, capped by a filled dot. | "93.31" (180 px) + "score" (56 px) + "95" on the dashed line (40 px). 3 words. | The drain is one 0.6 s stage with slow-in slow-out, a single bar shortening. After it, the hero holds 27 frames. The empty sliver between 93.31 and 95 is left showing, and nothing labels it yet: it is the climax's job. | `polished_score` 93.31 and `polished_gap` 18.40 in the row. 95 = gap 13.75. | Compared to what (Tufte): the 95 is always beside the score. The score axis becomes the ruler the rest of the film keeps. **CLOSE.** |

### Act 3: the search runs on that yardstick (0:15.5-0:24)

**S12-S23: montage, 0:15.5-0:21.5 (frames 465-645), 12 hard cuts of 0.5 s (15 frames) each, cut on every beat.** One preview fills the left two
thirds of the frame (~700 px tall, moving). S11's thermometer stays fixed at the right edge as a 0-100 ruler with the
dashed 95. Only the dot on the ruler and the 120 px score next to it change. Across the cuts the dot climbs, so the eye
stays in one place.

- **Picks:** this is the anti-cherry-pick rule. Of the 50 snapshot rows with a preview and a score above 0 (excluding
  ideated, duplicate and modelling rows), take **12 at evenly spaced ranks**, lowest to highest. **The leader is left
  out**, because it is S11's example and S25's star. Showing its row value of 92.89 here, after S11's 93.31, would
  show two scores for one design.
- **Score:** a verified row uses its `rows/<id>.json` `v_gap`. Any other row uses its `gap`, the claimant's own
  screening number.
- **Tags:** a tag appears only the first time each dot style appears, so the legend is taught by first use:
  - "dead" in S12
  - "self-measured" in S13
  - "verified" in S22

  After that the dot style speaks for itself.

| # | time | design (preview) | score on screen | dot | tag | source |
|---|---|---|---|---|---|---|
| S12 | 0:15.5-0:16.0 | seed-spm-3rrr | 29.66 | hollow, slashed | "dead" | morphs.json gap 193.44, status dead |
| S13 | 0:16.0-0:16.5 | acromial-rocker-3r | 54.24 | hollow | "self-measured" | gap 125.84, screened |
| S14 | 0:16.5-0:17.0 | crossed-skin-tracks | 65.62 | hollow, slashed | none | gap 94.55, dead |
| S15 | 0:17.0-0:17.5 | scapula-halo-track | 68.13 | hollow, slashed | none | gap 87.64, dead |
| S16 | 0:17.5-0:18.0 | seed-arc-rails | 73.45 | hollow, slashed | none | gap 73.00, dead |
| S17 | 0:18.0-0:18.5 | baseline-3r | 74.93 | hollow | none | gap 68.93, screened |
| S18 | 0:18.5-0:19.0 | offset-pointer-slip-sleeve | 78.58 | hollow | none | gap 58.90, screened |
| S19 | 0:19.0-0:19.5 | cam-coupled-4r | 81.57 | hollow | none | gap 50.67, screened |
| S20 | 0:19.5-0:20.0 | geneva-tail-knuckle-3r | 85.69 | hollow, slashed | none | gap 39.36, dead |
| S21 | 0:20.0-0:20.5 | coupler-path-j1 | 88.90 | hollow, slashed | none | gap 30.52, dead |
| S22 | 0:20.5-0:21.0 | raglan-knee-3r | 89.88 | filled | "verified" | v_gap 27.82, verified |
| S23 | 0:21.0-0:21.5 | geneva-tail-knuckle-pinknee-3r | 91.43 | filled | none | rows v_gap 23.57 at `d7f4bd2` |

S23 note: `morphs.json` still read 23.04 (91.62) at the snapshot, a known bookkeeping lag recorded in v2's `CHECK.md`.
The film uses the row's verifier number.

- **Motion:** the preview plays at the dashboard timer, starting each cut on the window with the most motion. The dot
  moves to its new height in 6 frames on the standard curve, and the digits change on the cut. The ruler, the 95 line
  and the dot style never change position.
- **Words:** 12 numbers + 3 tags = 15. Each cut carries at most 2 tokens.
- **Which rows:** 6 dead, 4 self-measured, 2 verified. Failures make up half the montage, so it is honest and not a
  highlight reel.

**Principles:** the cut rate is in a trailer's range (0.5-0.8 s; Bourne 0.78 s). Each clip is paired only with its
number, like Sora's clip-plus-prompt pairing and Boston Dynamics' "understood by looking". The fixed ruler gives the eye
one place to look (SIGGRAPH guide: "help the reader understand where to look"). Showing evenly spaced ranks rather than
the top results follows "picking only the top 5 is not representative". **Verb: HUGE, and HONEST.**

| # | time (frames) | picture | words on screen | motion | data source | principles |
|---|---|---|---|---|---|---|
| S24 | 0:21.5-0:24.0 (645-720) | Claims re-measured. There are 30 columns, one per design with both a self-measured claim and an independent re-measure, sorted by verified score, on the shared score axis with the dashed 95. Each column starts as a hollow dot at the claim. There are no row labels: v2's 30 labels, about 120 words, failed the glance test. | "26 of 30" (180 px) + "came in lower" (56 px, `#f0efec`) + legend "claimed" and "verified" (40 px, beside a hollow and a filled dot). 8 words. | 0-0.5 s: the hollow dots enter as one stage. 0.5-1.5 s: every dot snaps to its verifier's number as one 1.0 s stage (common fate). 26 dots fall, leaving a hairline stick from claim to verified, and 4 rise. 1.5-2.5 s: the hero enters and holds 30 frames. | `docs/concepts/rows/*.json` with both `gap` and `v_gap`, where the two differ. For minarc the claim is `v_gap_claim_reading` 15.42 (its row `gap` 6.19 is the refuted screening reading). The 10 rows that reproduced the claim to the digit are left out. Counted in v2's `CHECK.md`: 30 pairs, 26 lower, 4 better. | Produces new knowledge on screen as a beat, not a footnote (style guide A, "challenge what you know"). Outside judge, not self-assessment (Rieseberg). Gravity reads as "lower" without a word. The punchline is the biggest, brightest element (hierarchy). **HONEST.** |

### Act 4: CLOSE, and the button (0:24-0:32)

| # | time (frames) | picture | words on screen | motion | data source | principles |
|---|---|---|---|---|---|---|
| S25 | 0:24.0-0:29.0 (720-870), the one 5-s climax | The verified leader over time. The score axis runs 70-100, with the dashed 95 at the same screen height as S24, so this is a match cut on the line. x is time from 15 Oct 20:32 to 16 Oct 13:58 UTC, with no tick labels and a muted "17 hours" span under the axis. A filled-dot staircase has 6 steps: 75.83, 84.51, 88.96, 90.38, 92.89, 93.31. | Only the newest step's value is shown (120 px; the earlier ones fade to the dots alone), "95" (40 px), "17 hours" (40 px muted), then "1.69 to go" (180 px). At most 6 tokens visible at once. | 0-0.5 s: the axis and the time span draw (the 95 line is already there). 0.5-3.5 s: one step per beat, 6 beats. On each, the line runs right and then up in 300 ms on the standard curve, the dot enters in 225 ms, and the value swaps. 3.5-4.0 s: a bracket draws between 93.31 and the dashed 95, and "1.69 to go" enters. 4.0-5.0 s: hold for 30 frames. | Six verifier numbers, as in v2's README table: `events.jsonl` 20:32 (66.47), 00:32 (42.59), 03:58 (30.35), 06:30 (26.45, polish protocol), `rows/minarc-stop-knuckle-4r.json` `v_gap` 19.54 (11:57) and `polished_gap` 18.40 (13:58). The three omissions are carried over and disclosed in the film's README as v2 did: 34.29 on O15 hubs, H1's margin-5 24.48, and minarc B's 18.45. 95 - 93.309 = 1.69. | AlphaFold reveal: the best result per round against a threshold stated in words. One hero number. Steps on beats, with each step a single simple change. It does not over-promise: the film ends below 95 and never says "solved" (SIGGRAPH guide: "make sure it doesn't lead to disappointment"). **CLOSE.** |
| S26 | 0:29.0-0:32.0 (870-960) | The button. The leader's preview is moving again, large, filling the left 55 % of the frame, and the film ends where it began. On the right is the result in full contrast. | "93.31 → 95" (180 px `#f0efec`), "still running" (56 px `#f0efec`), "dashboard · 16 Oct 2026" (40 px muted). 8 words. | A hard cut on the downbeat brings in the closing hit. The text enters in 225 ms and then holds. There is **no fade-out**, and the last frame stays at full contrast until 0:32.0. | Same as S11 and S25. The date is the snapshot date. | "Last impressions are almost as important as first ones" (Film Editing Pro). The end card is ≤ 3 s with one hero number and one line pointing to the full work (Editage, JCB). It fixes v2's low-contrast fade-out. **WANT.** |

## The spec this board commits to, measured

| target (style guide) | this board |
|---|---|
| 30-40 s (35 ideal) | **32.0 s**: 960 frames, 64 beats, 16 bars at 120 BPM. Every cut is on a beat, and Act 1, Act 2, the climax and the end land on bar lines (0, 8, 24 and 32 s) |
| hook within 3 s, motion, no title slide | frame 0 is a moving preview, and the wall multiplies by 1.0 s |
| ~20-30 shots | **26 shots** |
| median shot ≤ 1.5 s | **1.0 s** (12 × 0.5, 5 × 1.0, 3 × 1.5, 3 × 2.0, 1 × 2.5, 1 × 3.0, 1 × 5.0) |
| no shot over 4 s except one climax ≤ 5 s | longest non-climax shot 3.0 s (S26); climax 5.0 s (S25) |
| nothing static > 3 s | every shot has new motion at least every 1.5 s, and the previews never stop |
| ≤ 4 words per label | yes (longest: "2–14 mm from skin", "configurations scored", "dashboard · 16 Oct 2026") |
| one hero number per shot | yes; S25's step values replace each other, so only one shows at a time |
| ≤ 12 words on screen per shot (this brief) | max 8 (S24, S26); S25 never shows more than 6 at once |
| total words | **76 tokens** = 36 numbers + 40 words. The 40 words are inside the ≤ 60 budget. Counting numbers too, it is over, mainly because of the 12 montage digits and S25's 6 step values (one visible at a time); the critics decide whether the digits stay. |
| type on a phone | hero 180 px → 36 px at 390 px wide; labels 56 px → 11.4 px (the 11-pt floor); nothing under 36 px |
| verified vs self-measured always distinct | filled / hollow / slashed in S04 (refuted patch), the montage, S24, S25 and S26 |
| 0 unsourced numbers | every number has its source in the tables above; the number-checker re-derives them from git |

## What the board leaves out, and why

- **Title card, formula text, and the protocol chips** ("frozen → verifier → held out"): fast forwards are not meant
  to dive into technical details. v2's 16 s explainer is now 7.5 s of pictures.
- **821 commits / 43.0 h:** these measure effort, not the search, and a second scale number would compete with 805,852.
  They stay in the README.
- **GPU simplest-class plot** (560,478 bounded, ceiling 88.71, "cannot reach 95"): it is a strong new-knowledge beat,
  but it is a second scale graph, and its axes (reach against in-band) need a legend. **Alternative cut** if the
  critics miss it: replace S14-S15 (1.0 s) with a 1.5 s ruler beat. That beat is a wall at 88.71 on the shared score
  axis, labelled "simplest class" and "ceiling", below the dashed 95. Source: `docs/research/golden/README.md`,
  verified 31.04 exact frozen.
- **The refuted 97.75:** it appears only as the dimmed, tagged patch in S04 and is never on a dot, a staircase or a
  label.

## How the producer builds it (one command, durable)

1. `snapshot.py`, extended: everything in v2, plus the 12 montage picks by the rule above, the leader's ideation slot,
   and an assert that every `morphs.json` id has a non-empty preview.
2. `dump_pick1.py` (new, local, `nice -n 19`, one process). It builds `docs/concepts/models/minarc-stop-knuckle-4r.py`
   with `docs/research/minarc_final_polish/picks/pick1.json` and wears it frozen on `Bench(110, 360)` exact, the same
   way the verifier did: `docs/concepts/verify/minarc-final-polish-verify.py` with env `CB_EXACT=1`,
   `CB_FOLD_MARGIN=5.5`, `OMP_NUM_THREADS=1`, as in `verify/jobs_verify.json`. It saves, per pose, the kind
   (clip / ws), the pose angles, whether the pose was taken, the minimum distance, and the metal distances.
   - **Gate:** `report()` must reproduce 0.8941 / 1.0 / 0.75 / 0.0281 / 18.40 to 4 decimals, and the 270 taken
     workspace poses must match the verifier's `bench110_360`.
   - **If the gate fails,** S06, S08 and S09 fall back to unit charts. These are 100 cells with 89 lit, 360 dots with
     270 filled in a 20 x 18 grid, and the × count, all laid out as counts and not as maps. That is honest, because a
     unit chart claims only the count.
3. `b1_*.py` scene scripts, one per act, using v2's `common.py` theme and preview drawing. Strokes are set in screen px.
   Each frame is an SVG rendered with cairosvg, and the cloud is a numpy density layer, as in v2.
4. `assemble.py`: hard cuts, no fades. The optional audio is a locally synthesised 120 BPM pulse, made with numpy:
   - a kick on each bar
   - a tick on each beat
   - a rising tone on each S25 step
   - one hit at 0:29.0, then a ring-out
   - no licensed music

   The film must work with the sound off, because no claim depends on audio.
5. Run it with `python3 run.py --board 1` (frames → mp4 → contact sheet → measured spec table). When the leader moves,
   re-run it and the film updates.

## Checks (the maker does not grade the cut)

- **Instruments:**
  - ffmpeg `select='gt(scene,0.3)',showinfo` for the shot count, median and longest shot.
  - Words per shot counted from the scene scripts.
  - Glyph heights measured in px on frames.
  - Every frame downscaled to 390x219 for the 3-s glance test.
  - `signalstats` for greyscale (SATMAX as in v2).
- **Critics:** three critics who did not make the film watch it cold, first without the README. Each writes the
  one-sentence takeaway and scores the cut against this spec and the user's brief. One of them is a red team.
- **Number-checker:** a separate checker re-derives every on-screen number from git at the snapshot, as in v2's
  `CHECK.md`.

## Red team on this board (where it can fail)

- **The montage reads as progress over time.** It is sorted by score, not time, so a viewer may think the search got
  better cut by cut. S25 is the true timeline. If the critics read the montage as chronology, re-sort it by
  `t_ideated` and keep the ruler, so the dot jumps around honestly. That gives a weaker crescendo but makes no false
  claim.
- **0.5 s cuts with digits.** About 5 characters at 120 px for 15 frames is under Netflix's 25-frame minimum for text,
  so critics may not read every number. The design bet is that the dot's height carries the score and the digits are
  texture. If 2 of the 3 critics cannot read them, switch to 10 cuts × 0.6 s (18 frames, cut on the beat plus 3
  frames) or drop the digits.
- **"touches skin"** makes the leader look like a failure on the user's own rule ("never touching"). That is the true
  state: contact 0.0281 is part of the 18.40 gap. Hiding it would be the Boston Dynamics edit.
- **S10's "mostly reach"** is the only interpretive label. It is true by construction: 15.00 of 18.40 = 82 %.
- **A two-numbers trap:** the leader's row `v_gap` 19.54 (92.89, BDp) and the polished pick1 18.40 (93.31) are the same
  design. The board shows only 93.31 for the leader, and S25 shows 92.89 as the earlier step "minarc BDp", labelled by
  its position in time only.
- **The preview is not pick1.** The leader's preview is drawn at its concept file's best configuration, while the
  numbers are pick1's. Disclose this in the README, as v2 did.
- **Stale counts.** HEAD has moved since `d7f4bd2` (112 designs, 832 commits). Either re-snapshot after the four missing
  previews are drawn, or render at `d7f4bd2`. Never mix the two snapshots.
