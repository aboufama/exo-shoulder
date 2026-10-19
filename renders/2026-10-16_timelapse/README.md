# Effort time-lapse, 2026-10-16

`exo_effort_timelapse.mp4` is a short film of every design variation the project tried between Oct 14 and Oct 16, 2026,
cut as a time-lapse. Its job is to show how much was explored, and to show it honestly.

- **Format:** 88.0 s (2640 frames), 1920x1080, 30 fps, H.264 yuv420p (crf 20, faststart), 13.9 MB, no audio.
- **Contact sheet:** `contact_sheet.jpg` holds 24 evenly spaced frames, each labelled with its timecode.
- **Numbers:** every number on screen comes from the repo snapshot **2026-10-16T05:11Z** (568 commits). The one
  exception is a single line on the end card, which is labelled "after the snapshot" and is described below. The search
  kept running while the film was made, so the counts are a snapshot, not a final tally.

## What the film shows

| time | segment | what is on screen |
|---|---|---|
| 0:00-0:04 | title | "Every design we tried". Three counters land on their true values: 33.4 hours, 568 commits, 94 morphologies catalogued. Behind them the real commit subjects from `git log --reverse` scroll past as faint texture (no author names). |
| 0:04-0:18 | 01 ORIGINS | Opens on a bar race of the 87 GPU searches (bar = that search's evaluations; orange = 3 DOF, metal = 4-6 DOF). The counter lands on 247,646 designs evaluated, 42.6 GPU-hours. Then come hard cuts through the first 16 builds in build order, all on one locked camera, while one "Raise overhead" motion plays across the cuts. Every design is shown at the same clip frame, so a cut shows how far each design lets the arm go. A gauge reads "arm reaches X deg of 150". |
| 0:18-0:36 | 02 THE SWARM | 97 morphology rows in the order they were ideated, each an animated schematic (83 real tiles, 14 text tiles), all moving in sync. The view zooms out to the full 13 x 8 wall for the verdict pass: dead, refuted and duplicate rows dim, and the 6 verified rows get an orange border. The leader, skin-normal-3r-pin-knee, pulses at "verified leader 88.96". |
| 0:36-0:51 | 03 THE SEARCH | All 94,085 timed concept-bench configurations plotted in run order. The y axis is gap on a log scale, lower is better. An orange best-so-far staircase steps down through 31 records, and the counter races to 94,085. The closing callouts separate the fast screening best (gap 20.63) from the verified number (gap 30.35 = score 88.96) and from the night's champion 3R on the same bench (75.65). |
| 0:51-1:07 | 04 THE BUILDS | The 8 most recent builds, one after another on the locked camera, each with its own achieved Raise overhead clip. The offset-skin-normal builds stop at 65.9 deg (the J2 fold) and the pin knee goes all the way to 150. A film strip of all 24 builds lights up as each one plays. |
| 1:07-1:22 | 05 THE WINNERS | A 3 s excerpt of the Oct 15 Cycles film of the night's final 3R. Cycles stills of the champion 3R in the user's style. The generation-2 winner (offset-skin-normal-3r k4216) as Cycles stills. Then the current verified leader, l1_skin-normal-3r-pin-knee, as a live viewer render: the arm rises to 150 deg and the camera orbits 70 deg. |
| 1:22-1:28 | end card | "The search so far": 568 commits in 33.4 hours, 94 morphologies (6 verified), 94,085 concept-bench configurations, 247,646 GPU-evaluated designs (87 searches, 42.6 GPU-hours), 24 designs built as 3D CAD, verified leader score 88.96 (gap 30.35). It also carries the after-the-snapshot line and "not done: ... the search is still running". |

Cuts: each segment fades in from the background (#0d0e10) over 6 frames and fades out over 6, and segments are joined
by hard cuts.

## Every on-screen number and its source

All scores use score = 100 x (1 - gap/275) and are truncated, never rounded up. 90 would need gap <= 27.5, and
nothing in the film crosses it.

### Snapshot numbers (2026-10-16T05:11Z)

**Repo activity**
- **commits 568:** the count of `git log --format=%at`.
- **hours 33.4:** from the first commit, 2026-10-14T19:45Z, to the last commit in the snapshot, 2026-10-16T05:11Z.
  This counts this repo only; the earlier archive (Oct 9-13) is not included.

**Morphologies**
- **94 catalogued:** `docs/concepts/catalogue.json`.
- **97 rows:** `docs/dashboard/data/morphs.json`, including baseline-3r.
- **Status counts:** 6 verified, 9 screened, 8 refuted, 17 dead, 7 duplicates, 4 modelling, 46 ideated.
- **80 animated schematics:** `docs/concepts/viz/concepts/<id>.js`, 80 files at the snapshot.

**Concept-bench configurations**
- **94,085:** the timestamped rows (of 94,097) in the 45 files `docs/concepts/sweeps/*.json`, with files starting with
  an underscore excluded. They run from 2026-10-15T15:48:57Z to 2026-10-16T05:09:13Z.
- **Best screening gap 20.63:** fast bench, skin-normal-3r-pin-knee.

**GPU era**
- **Source:** `docs/dashboard/data/gpu_searches.json`, from 2026-10-14T19:45:28Z to 2026-10-15T14:37:53Z, on RTX PRO
  6000 Blackwell MIG 1g/2g slices.
- **87 searches.**
- **247,646 evaluations:** the sum of `evals`.
- **42.6 GPU-hours:** the sum of `secs`.

**Built designs**
- **24:** the `exo.glb` files in `pipeline/full-exo/designs/*/`. The verifier's rebuild `_vfy_l1_rail-elbow` is
  excluded.
- **Build time:** the time git first added the file. `band_r20_n3_s1414_4` is git-ignored, so its time is the file
  mtime.
- **"Arm reaches X deg of 150":** the maximum `p[1]` of that design's `clips.json`, clip 0 "Raise overhead". This is the
  achieved pose.
- **"At its limit" chip:** shown on frames where the clip has `held = true`.

**Verified gaps** (`docs/dashboard/data/morphs.json` `v_gap`, Bench(110,360) exact, frozen shape)

| design | gap | score |
|---|---|---|
| skin-normal-3r-pin-knee (leader) | 30.35 | 88.96 |
| raglan-knee-3r | 31.52 | 88.54 |
| skin-normal-3r-knuckle-cufflink | 31.89 | 88.40 |
| spine-parked-j2-3r | 34.29 | 87.53 |
| offset-skin-normal-3r (generation-2 winner, k4216) | 42.59 | 84.51 |

- **seed-offset-3r-slides:** 75.33 in morphs.json. Its row file says 66.47, so this value appears only as a swarm tile
  label and never as a headline.
- **rail-elbow:** 64.70 is on Bench(60,160), so it is not shown as a score. Its status is refuted.

**Champion 3R (r20 s1414 #4)**
- **Gap 66.97, score 75.65:** run through the same checks on the same bench, with a frozen shape.
- **Source:** `docs/concepts/rows/offset-skin-normal-3r.json`, `champion_big_frozen_exact_same_checks`.

**Story clock**
- The bottom-right clock reads "Oct DD · HH:MM UTC · NNN commits". NNN is the number of commits up to that moment's
  story time.

### After the snapshot (end card only, labelled as such)

- **What it says:** "the leader's final polish, independently verified on the same bench and protocol: gap 28.21 =
  score 89.74 - still short of 90".
- **Source:** `docs/concepts/rows/skin-normal-3r-pin-knee.json`, fields `v_gap` (28.21) and `v_gap_protocol`. The
  verification is commit `fe73dc5`, 2026-10-16T06:30Z: "Verify skin-normal-3r-pin-knee polish H1 ... CONFIRMED".
- **Why 28.21:** this is the round-3 verifier's protocol, the one that gave 30.35, so the two numbers compare directly.
- **Not shown:** the polish protocol's 26.45 uses a different shape fit and is not comparable with the other rows, so it
  is not on screen.

## Honesty notes

- **Two benches:**
  - **Screening gap:** fast bench, Bench(60,160).
  - **Verified gap:** Bench(110,360) exact, frozen shape.
  - **On screen:** the film labels which is which. The headline numbers are always verified gaps.
- **No per-design requirement percentages.** The judges changed over the two days. For example, cad_r13_n4 reads
  80.2 % R1 in today's scorecard against 51.8 % in docs/EVOLUTION.md, so the scorecards are not comparable on one screen.
- **Not shown at all:** RunPod spend, because spend.json is partial, and judged-requirement row counts, because the
  dashboard rebuilds them live.
- **Build levels:** L1 builds are keep-out CAD (flat slabs at their real height), and they are labelled "L1 keep-out
  CAD". "Evaluator band" builds are evaluator geometry, not CAD.
- **Poses:** each build plays the Raise overhead that this design actually achieved, so a build that jams stops the arm
  where it jams. cad_r13_n4 stops at 55.6 deg and the offset-skin-normal builds at 65.9 deg.
- **Builds that look alike:** param_r20_n3_s1414_4, l1_3r-k2221 and l1_rail-elbow share their cuffs in this view and
  differ only in the small shoulder linkage. At film size they look alike, and that is what was built.
- **Cycles material** (segment 05) is from earlier generations:
  - the Oct 15 night's final 3R film
  - the champion 3R in the user's style
  - the generation-2 winner, using the current muscled-mannequin stills `hero_overhead_back.jpg` and
    `hero_overhead_chain.jpg`; the `first_pass_flat_mannequin` stills were not used
- **Leader shot:** the current leader is a live three.js viewer render of its L1 keep-out CAD. It is labelled "live
  viewer render (three.js), not Cycles".
- **Search plot x axis:** this is configuration run order, the row index in file order. Ticks mark where each UTC hour
  falls in that order. Many rows share one timestamp, because sweeps write in bursts, so a time axis would collapse them
  into stripes.
- **Swarm schematics:** 3 of the swarm's animated tiles are schematics whose files reached the repo at 05:12Z and 05:17Z,
  just after the snapshot: raglan-knee-3r, skin-normal-3r-knuckle-cufflink and stop-relay-rocker-3r. No schematic count
  is shown in that segment.
- **Search still running:** the search kept running while the film was made. Round 4 and the final polish added commits
  and verifications after 05:11Z. The film shows the snapshot, plus the one labelled update on the end card.

## How it was made

Everything was rendered locally, on the repo's own CPU box. There was no paid compute: no RunPod and no Cycles render
farm.

**Builds and schematics**
- **Builds:** rendered in headless Chromium driven by playwright, through a scratch copy of
  `pipeline/full-exo/film.html` (three.js). The mannequin is the viewer's matte black faceless mesh, and the exo parts
  are bead-blasted aluminium and iglidur orange.
- **Concept schematics:** the concept gallery `docs/concepts/viz/` (kin.js + concepts/<id>.js), rendered in the same
  headless browser with a dark film theme.

**Compositing and encoding**
- **Plots, counters, titles and compositing:** Python with PIL and numpy, using the Inter typeface.
- **Cycles material:** the existing renders in `renders/2026-10-15_final_3R`, `renders/2026-10-15_userstyle_r20_s1414_4`
  and `renders/2026-10-16_userstyle_osn_k4216`, re-cut with ffmpeg and PIL (Ken Burns push-ins).
- **Final encode:** PNG sequence to H.264 with ffmpeg (`-preset slow -crf 20 -pix_fmt yuv420p -movflags +faststart -an`).
- **Repo access:** the repo was read only during production. Nothing from `data/raw/private/` or any personal folder is
  in the film.


## Update 2026-10-16 ~07:10 UTC (end card only)

The end card's "after the snapshot" line now gives the independently verified polish of the pin knee (H1): gap 26.45 =
score 90.38 on Bench(110,360) exact at fold margin 10 (24.48 = 91.1 at the user's 5 deg margin; 28.21 on the round-3
protocol; rows/skin-normal-3r-pin-knee.json v_polish_*), the first verified design above 90. "designs built as 3D CAD"
became "designs built in 3D (14 as full CAD)" - 10 of the 24 builds are evaluator-band geometry (critic's note). Scores are
rounded to 2 decimals. The rest of the film is unchanged (repo snapshot 05:11Z).
