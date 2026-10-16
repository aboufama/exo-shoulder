# Preview film v4: 108 designs, one yardstick, 1.69 to go (31 s)

`exo_preview.mp4`: 31.00 s, 1920x1080, 30 fps, H.264 yuv420p (crf 18, faststart), 15.37 MB, with an original
synthesised soundtrack (AAC 160 kb/s, -15.6 LUFS integrated, true peak -1.3 dBFS). Built to be read with the sound off: every claim is on screen.
Rendered locally from the repository at `d7f4bd2` (2026-10-16T14:43Z; 821 commits over 43.0 h), the last commit at which every
one of the 108 designs has a basic motion preview. Basic kinematic previews only: no CAD render, nothing read from `renders/` or `pipeline/`.

This is the recut of v3 (35 s, `a72bf22`) on the three outside critics' notes (scores 4, 5 and 6 of 10). It answers the user's request of
2026-10-16 (~15:30 UTC: 30-40 s, less draggy, built the way research fast forwards and trailers are) and the brief that still stands
(greyscale in the dashboard theme, basic previews, many simple tests and the graphs, few words, how the score is made, told as a story).

**Intended cold takeaway** (to be tested by outside critics, not by the maker): *an automated search tried 108 shoulder-exo designs and ~806
thousand configurations against one score; an independent verifier marked most claims down; the verified best is 93.31 against a 95 target, still running.*

## What changed from v3, note by note

| critics' note (v3) | v4 |
|---|---|
| the subject is never named; the mannequin reads as "a pot with loose sticks" | "shoulder-exo designs" at 0.7 s; the mannequin drawn as filled silhouettes (viewer.js primitives: torso, head, both arms; the moving arm a shade lighter); the mechanism at 5-7 px; a 1-cm halo round the arm makes "within 1 cm" a picture; text clear of the drawing |
| previews step at 10 fps (every 3rd frame), the wall strobes | every preview re-solved at film resolution: 168 frames per 5.6-s loop (one per film frame) from the same `d7f4bd2` viz sources and camera (`hires.mjs`), 0.1-unit coordinates instead of integers; one clock for the whole film, so the arm moves through the cuts |
| score explainer is a strobe: four chart types in 4 s, jargon, settles 0.4 s before each cut; the yardstick reads upside down | one 2 x 2 shot in one grammar (plain labels, %, a target tick each, a check or an outlined shortfall), then a score column that starts full at 100 and loses its bites, reach the big one, landing at 93.31 under "95 target" (6.5 s -> 4.5 s) |
| montage: 8 two-decimal numbers, 20-px glyphs, tags on 4 of 8 cards, previews at 25 % of the frame | every card tagged (64 px), integer scores at 180 px on one anchor, glyphs 40 px, the mannequin filling the frame, one framing and one clock (one arm cycling through designs) |
| the leader's dot touches the 95 line on the card | the leader's card has no axis; the gap is shown only where it can be read (the climax zoom) |
| the wall orbits, tiles clipped at the frame edge, a tile's links explode into its neighbours, the wall appears twice | each preview clipped to its cell, wall inside the safe margin at 87 % of the frame width, the second appearance is the payoff (statuses resolve in one wave, "13 verified") |
| V3 "three plain pins" (jargon, a second climb, a self-measured number in hero type) | cut |
| Z3 area blocks (an empty grey "GPU" square, the unit changes mid-count) | cut: the counter runs on over the cloud on a jump-zoom, one label throughout ("configurations scored"), the GPU part named in a sub-line |
| V1 strike overhangs the numerals by ~290 px; ticks on the data; muted outline hero | the strike spans the numerals exactly, drawn left to right; numerals solid muted, "refuted" in full contrast; ticks in a left gutter clear of the data; a continuous zoom keeps the cloud's context |
| the ending is the stillest part: empty axes, a 1-s flat in the climb, six heroes flashing, "1.69 to go" and "93.31 -> 95" repeat for 4.4 s; the audio dies after 32 s | axes and first step on the cut; one step per beat (eased playhead, true time kept); one hero at a time; a y-zoom turns 1.69 into a 370-px bracket; 4 frames of silence, then the button lands on a hit and a chord that rings to the last frame |
| back half drags: still holds of 0.8-1.0 s in 7 of the last 16 s | every data shot has a slow push about the pinned 95 line; measured below: no run of 8 or more near-still frames anywhere |
| hero number moves on almost every cut | one anchor for every data shot (right-aligned at x = 1824, baseline y = 600) |
| counters jitter (proportional digits); "best88.04" collisions | tabular figures right-aligned to a fixed label |
| "95" never called the target | "95 target" at its first use (the score column) and in the climax |
| no "crazy research" signal | "automated search · 43 hours" on the button |
| flat 2-s audio loop | three acts: sparse pulse (hook, score), a kick on every card and denser hats (montage to honesty), a kick per beat and a riser under the climb, silence, the hit |

## Spec, target vs measured on the encoded file

| spec | target | measured | instrument |
|---|---|---|---|
| running time | 30-40 s | 31.00 s | ffprobe |
| hook | motion within 3 s, no title | the full moving wall on frame 0; the subject named at 0.7 s | frame 0 |
| shots | ~20-30 | 20 | cut list |
| median shot | <= 1.5 s | 1.5 s | cut list |
| longest shot | <= 4 s, one climax <= 5 s | 4.0 s (the climax) | cut list |
| near-still runs | nothing still > ~0.5 s | runs of >= 8 frames with < 0.05 % of a 480 x 270 grey frame changing by > 6 levels: 0 | numpy on the frames |
| words on screen | <= 60, <= 4 per label | 60 words (166 tokens with numbers and ticks); longest label 3 words + a number | scene scripts |
| type size | heroes >= 160 px, labels >= 48 px, nothing < 32 px | one hero per shot at 150-240 px, except S (four values at 130 px, one per small multiple) and H2b (its 2-word line at 110 px); labels 52-72 px; context 40-48 px; smallest 36 px (the snapshot line) | the draw calls, every 5th frame |
| colour | greyscale theme | max channel spread 13 of 255 | numpy, every 10th frame |
| size | <= 20 MB | 15.37 MB | ffprobe |
| cuts the detector sees | all planned cuts | `gt(scene,0.3)`: 0 of 19; 0.1: 5; 0.05: 10; the producer's own detector (`cutdetect.py`): 9 | ffmpeg lavfi.scene_score |
| numbers | 0 unsourced; filled = independent only | every number below has its repo path | this README; independent check pending |

**The scene detector.** ffmpeg's scene score is a whole-frame luminance difference. A dark greyscale canvas (the dashboard theme the user
asked for) keeps it low even at a full change of layout: v3's cuts scored 0.006-0.25; v4's brighter silhouettes and full-frame compositions
raise the planned cuts found at 0.1 from 2 of 22 (v3) to 5 of 19, and the match cuts (montage cards on one framing, the
pinned 95 line) are low by design. The cut list is exact by construction (the renderer draws from it).

Phone scale: each shot was checked at 390 x 219 (a 16:9 frame on a 390-pt-wide phone in portrait): the heroes (~35 pt), the tags and the
labels read; the meter targets (40 px, ~8 pt) and the snapshot line (36 px) are context.

## Cut list (hard cuts on a 120 BPM grid: every shot a multiple of 0.5 s; 15 frames = one beat)

| shot | time | s | picture | on screen | source (git at `d7f4bd2`) |
|---|---|---|---|---|---|
| H1 | 0:00.0-0:02.0 | 2.0 | Cold open, no title: all 108 designs as a 14 x 8 wall (ideation order), every preview moving on one clock at 30 fps; slow push. At 0.5 s the wall dims under the count | 108 shoulder-exo designs | 108 designs in `morphs.json`, 108 with a preview (`motion.json` at `d7f4bd2`) |
| H2 | 0:02.0-0:03.5 | 1.5 | The goal as a picture: the leader (minarc-stop-knuckle-4r) on the mannequin, filled silhouettes, the arm rising to overhead; a 1-cm halo round the arm brightens as the words land | within 1 cm | goal from CLAUDE.md / REQUIREMENTS.md (~1 cm; pass at 14 mm, aim 10) |
| H2b | 0:03.5-0:05.0 | 1.5 | Punch-in on the shoulder, same clock (the arm keeps moving through the cut): the mechanism large inside its halo | never touching | as H2 |
| S | 0:05.0-0:07.0 | 2.0 | The four measurements of the leader as one grammar, 2 x 2: label, value, a meter with its target tick, all four building at once (one 0.9-s stage); a check on the one that passes, the shortfall outlined on the three that miss (reach thickest) | near the skin 89 % 90 % follows the arm 100 % 95 % reaches the poses 75 % 90 % never touches 11 poses 0 | `docs/research/minarc_final_polish/verify/v_pick1_fit60_bench.json` final: inband14 0.8941 (89 %), follow 1.0 (Bench(110,360): 110 clip frames), reach 0.75 (270 of 360 poses), contact 0.0281 = 11 poses (verifier.contact_raw.n) of 391; targets from `tools/concept_bench.py` gap_of (0.90 / 0.95 / 0.90 / 0) |
| Y | 0:07.0-0:09.5 | 2.5 | Four measurements -> one number: a score column full to 100 loses its three bites (in score points: near the skin 0.21, reach 5.45, touching 1.02; follow costs 0) in one 1-s stage and stops at 93.31, below the dashed line labelled '95 target' (its first use). No equation | 100 95 target near the skin reach touching 93.31 score | gap_of: 0.59 + 0 + 15.0 + 2.81 = 18.4 gap points; score 100 (1 - 18.4/275) = 93.31; a bite is gap points / 2.75 |
| M1 | 0:09.5-0:10.0 | 0.5 | Card 1/8 (ideation order), same framing and clock as H2 (one arm cycling through designs): seed-spm-3rrr; slashed ring (dead) on a 25-100 axis; integer score and tag 'dead' | 25 50 75 95 30 dead | rows/seed-spm-3rrr.json gap 193.44 = 29.66, dead |
| M2 | 0:10.0-0:10.5 | 0.5 | Card 2/8 (ideation order), same framing and clock as H2 (one arm cycling through designs): fivebar-roll; slashed ring (dead) on a 25-100 axis; integer score and tag 'dead' | 25 50 75 95 68 dead | rows/fivebar-roll.json gap 89.13 = 67.59, dead |
| M3 | 0:10.5-0:11.0 | 0.5 | Card 3/8 (ideation order), same framing and clock as H2 (one arm cycling through designs): floating-centre-3r; ring at the claim 78.85 -> filled verifier dot on a 25-100 axis; integer score and tag 'refuted' | 25 50 75 95 50 refuted | rows/floating-centre-3r.json gap 58.17 -> v_gap 136.31 = 50.43, refuted |
| M4 | 0:11.0-0:11.5 | 0.5 | Card 4/8 (ideation order), same framing and clock as H2 (one arm cycling through designs): crown-ring-3r; hollow ring (self-measured, no verifier number) on a 25-100 axis; integer score and tag 'self-measured' | 25 50 75 95 70 self-measured | rows/crown-ring-3r.json gap 82.37 = 70.05, screened |
| M5 | 0:11.5-0:12.0 | 0.5 | Card 5/8 (ideation order), same framing and clock as H2 (one arm cycling through designs): raglan-routed-3r; hollow ring (self-measured, no verifier number) on a 25-100 axis; integer score and tag 'self-measured' | 25 50 75 95 84 self-measured | rows/raglan-routed-3r.json gap 42.72 = 84.47, screened |
| M6 | 0:12.0-0:12.5 | 0.5 | Card 6/8 (ideation order), same framing and clock as H2 (one arm cycling through designs): skin-normal-3r-knuckle-cufflink; ring at the claim 91.10 -> filled verifier dot on a 25-100 axis; integer score and tag 'verified' | 25 50 75 95 89 verified | rows/skin-normal-3r-knuckle-cufflink.json gap 24.47 -> v_gap 29.1 = 89.42, verified |
| M7 | 0:12.5-0:13.0 | 0.5 | Card 7/8 (ideation order), same framing and clock as H2 (one arm cycling through designs): slotted-eccentric-j2-3r; ring at the claim 73.09 -> filled verifier dot on a 25-100 axis; integer score and tag 'refuted' | 25 50 75 95 58 refuted | rows/slotted-eccentric-j2-3r.json gap 74.0 -> v_gap 115.21 = 58.11, refuted |
| M8 | 0:13.0-0:13.5 | 0.5 | Card 8/8 (ideation order), same framing and clock as H2 (one arm cycling through designs): geneva-tail-knuckle-pinknee-3r; ring at the claim 93.99 -> filled verifier dot on a 25-100 axis; integer score and tag 'verified' | 25 50 75 95 91 verified | rows/geneva-tail-knuckle-pinknee-3r.json gap 16.53 -> v_gap 23.57 = 91.43, verified |
| Z1 | 0:13.5-0:16.0 | 2.5 | The leader's card ('93.31 leader') pulls back into its tile; the statuses resolve in one left-to-right wave (dead / refuted / duplicate tiles dim, the 13 verified tiles get a frame); '13 verified' lands in the wall's 2 x 2 gap | 93.31 leader 13 verified | morphs.json statuses at `d7f4bd2`: {'screened': 10, 'ideated': 44, 'refuted': 11, 'verified': 13, 'dead': 19, 'duplicate': 7, 'modelling': 4} |
| Z2 | 0:16.0-0:17.5 | 1.5 | Every timed concept-bench configuration as a density cloud (x = run order, y = score 0-100, dashed 95); the count runs with the reveal to 270,718 (tabular figures, fixed label) | 270,718 configurations scored 25 50 75 95 | `docs/concepts/sweeps/*.json` at `d7f4bd2`: 57 files, 270,718 timed rows ('_' files excluded; id = stem before '@') |
| Z2b | 0:17.5-0:19.0 | 1.5 | Jump-zoom on the beat (the 95 line stays pinned): the count runs on to 805,852 while '+ 535,134 on GPU' names what is added; the GPU evaluations are a number, not drawn as points | 805,852 configurations scored + 535,134 on GPU 25 50 75 95 | 270,718 + 247,646 (gpu_searches.json, band evaluator) + 186,248 (docs/research/golden/README.md) + 101,240 (gks1_digest.json n_ok) = 805,852; the 560,478 bounded configurations are not counted |
| V1 | 0:19.0-0:21.0 | 2.0 | The camera zooms 4x into the 08:12 batch, the only readings above 95: the best one, 97.75, in muted numerals, struck through left to right; all readings above 95 dim; 'refuted' in full contrast | 97.75 refuted 95 80 85 90 100 | sweep minimum gap 6.19 at 2026-10-16T08:12:02Z = 97.75; 3,374 readings >= 95, all minarc-stop-knuckle-4r 08:12:01-02; the claim built on this search (15.42 frozen exact) was refuted at 09:45 / 09:49 UTC (events.jsonl): it needs J2 stops 1.4-2 deg from the fold, under the 5-deg rule |
| V2 | 0:21.0-0:24.0 | 3.0 | 30 claims as hollow rings (sorted, no row labels, axis 30-100); filled verifier dots slide to the re-measured scores in one 1-s stage: 26 down, 4 up | claimed verified 26 of 30 came in lower 95 40 60 80 100 | rows/*.json `gap` (minarc: v_gap_claim_reading 15.42) vs `v_gap` at `d7f4bd2`: 26 of 30 lower; the 10 rows whose v_gap equals the claim were written in the screener's own commit and are not drawn |
| C1 | 0:24.0-0:28.0 | 4.0 | The climb: the verified leader on a true time axis (15 Oct 20:32 -> 16 Oct 13:58 UTC); the playhead eases between step times so one step lands on every beat (0.5 s); only the newest value is the hero; then the y axis zooms (95 pinned) until the 1.69 gap is a 370-px bracket: '1.69 to go' | 75.83 84.51 88.96 90.38 92.89 93.31 1.69 to go 17 hours 95 target 70 80 90 | events.jsonl 20:32 (66.47 = 75.83), 00:32 (42.59 = 84.51), 03:58 (30.35 = 88.96), 06:30 (26.45 = 90.38, polish protocol); rows/minarc-stop-knuckle-4r.json v_gap 19.54 (11:57, 92.89) and polished_gap 18.40 (13:58, 93.31); 95 - 93.31 = 1.69 |
| B1 | 0:28.0-0:31.0 | 3.0 | Button, hard cut on the downbeat after 4 frames of silence: '93.31 -> 95', 'still running', 'automated search · 43 hours' at full contrast, the leader moving on the mannequin, the snapshot date and the dashboard address; no fade | 93.31 → 95 still running automated search · 43 hours snapshot 16 Oct 2026 · claude.ai/artifact/AMhjuE83FBhGXxu8vQBN7r | rows polished_gap 18.40, polished_status CONFIRMED; 95 = gap 13.75; 43.0 h = first commit to the snapshot commit (821 commits, `d7f4bd2`, 2026-10-16T14:43Z); dashboard address from docs/DASHBOARD.md |

Structure: 0-5 s hook and goal (motion, no title) · 5-9.5 s how the score is made (four measurements, one number) · 9.5-19 s scale
(montage, then one pull-back 1 design -> 108 -> 270,718 -> 805,852) · 19-24 s the outside judge (struck reading, 26 of 30) · 24-28 s the one
peak (the verified climb against the dashed 95) · 28-31 s the button.

## Visual grammar

- The dashed 95 line sits at y = 270 px in every data shot; zooms and pushes scale about it, so it never moves.
- Filled dot = the independent verifier's number. Hollow ring = self-measured. Ring with a slash = dead. Where a verifier number exists, the
  claim stays as a hollow ring joined to the filled dot, and the number printed is the verifier's.
- Greys only (canvas #1a1a19, text #f0efec, context #898781, hairlines #313130, fill #c3c2b7, dimmed #4a4947, body #302f2c, moving arm #43423e;
  Caladea and Inter stand in for the dashboard's fonts). The takeaway is always the largest, brightest element.
- Motion: text enters in 6-7 frames on cubic-bezier(0, 0, 0.2, 1) and leaves in 5 on (0.4, 0, 1, 1); moves use (0.4, 0, 0.2, 1); data
  transitions are one ~1-s stage; zooms run in log space; hard cuts only, no fades between shots.

## What the pictures do and do not claim (disclosures)

- **The previews are basic kinematic sketches**, re-solved for the film by `hires.mjs` from the viz sources at `d7f4bd2` (the same loop,
  camera, parts and IK as `docs/dashboard/data/motion.json`, sampled 168 times per loop instead of 60, coordinates to 0.1 unit). Each design is
  drawn at its concept file's configuration; the leader's preview is not drawn at pick1's polished parameters; the numbers are pick1's.
- **The mannequin** is the gallery's primitive mannequin (viewer.js: lofted torso, neck, head, both arms) drawn as filled convex silhouettes.
  The halo is the outline of the arm (deltoid, upper arm, elbow) offset by 10 mm: for an orthographic camera and convex primitives the
  projected offset surface is exactly the silhouette widened by 10 mm, so the band is to scale. It illustrates the goal; the band the bench
  scores is 2-14 mm.
- **S shows counts, not maps**, rounded to whole percent (in-band 0.8941 -> 89 %). The contact meter is drawn 6x longer than to scale so
  that 2.8 % reads; its value is the count, 11 poses.
- **805,852 mixes evaluators.** 270,718 are concept-bench screens (CPU, drawn as points); 535,134 GPU evaluations (247,646 of the older
  band evaluator, Oct 14-15; 186,248 full-bench evaluations of the zero-complexity class; 101,240 of the pin-knee polish, gks1) are added
  to the count on screen and named ("+ 535,134 on GPU"), not drawn. The 560,478 configurations that were only bounded are not counted.
- **97.75 is a fast-screen reading, never a result.** It is drawn muted and struck. "refuted" is the verifier's verdict on the claim this
  search produced (09:45 / 09:49 UTC); the verified leader is 93.31.
- **26 of 30.** The 30 pairs are the rows whose `v_gap` differs from the claim. The 10 rows whose verifier number equals the claim
  (acromial-rocker-3r, back-anchored-ring-3r, fivebar-roll, offset-arc-selfalign, scapula-halo-track, seed-2r-cring, seed-arc-rails, seed-pauldron-shells, seed-spm-3rrr, trombone-arc) got both fields in the screener's own commit, so they are not independent re-measures and are not drawn.
- **The simplest class (v3's "three plain pins, best 87.81") is cut** on the critics' notes. The correction v3 recorded stands: v2's
  "verified ceiling 88.71" is the claimant's fit-110 reading; the skeptic reproduced 33.51 = 87.81 on the leader's protocol.
- **The climb** draws each step at the verifier's number on the protocol of that day; the playhead's speed varies between steps (the
  step times on the x axis are true). As in v2 and v3, three verifier numbers are left out on purpose: spine-parked-j2-3r's 34.29 (87.53)
  at 03:39 on O15 hubs voided by the "Keep O20 only" ruling; the H1 verifier's margin-5 reading 24.48 (91.10) at 06:30, drawn at its
  polish-protocol 26.45 (90.38, the lower one); minarc variant B's 18.45 (93.29) at 09:45, a re-measure of a refuted claim.
- **"automated search · 43 hours"**: 43.0 h is the span from the first commit to the snapshot commit (821 commits). The search ran
  as agent loops; the user gave rulings during it (CLAUDE.md), so "automated" describes the search, not an absence of people.
- **Snapshot.** HEAD has moved on (more designs than previews), so the film stays at `d7f4bd2`; `snap4.py` asserts that every
  `morphs.json` id has a preview before it writes the numbers.

## Sound

Original, synthesised in numpy for this film (no samples, no licensed music), 120 BPM, events at the film's own frame numbers. Act 1 (hook,
score): a low A/E drone, a kick every 2-s bar, quiet hats, bells as the count, the goal and the score land. Act 2 (montage to honesty): a
kick on every card, denser hats, clicks on the cuts, a rising sweep under the counter, one low hit on the strike, a descending tick cluster
as the 30 claims move. Act 3 (the climb): a kick on every beat, one bell per step a semitone up, a noise riser. Then 4 frames of silence, a
hit on the button's downbeat and a chord that rings to the last frame. Loudness (ffmpeg loudnorm, one pass): -15.6 LUFS integrated, true peak -1.3 dBFS.
A silent encode exists for sound-off feeds (same picture).

## Rebuild

`python3 make4.py` in the producer folder (`tl4/` in the session scratchpad): `hires.mjs` (film-resolution previews from a `git archive
d7f4bd2 docs/concepts/viz` copy) -> `snap4.py` (every number from git at the snapshot) -> `render4.py` (930 frames, cairosvg, 2 niced
processes, ~2.5 min on the shared 4-core box) -> `audio4.py` -> `assemble4.py` (encode, contact sheet, phone sheet, measurements) -> this README.

## Not done by the maker (next)

The maker does not grade the cut. Next: three critics who did not make it watch it cold without this README, write the one-sentence
takeaway and score it against the spec table and the user's brief; a separate number checker re-derives every on-screen number from git at
`d7f4bd2` and writes CHECK.md.
