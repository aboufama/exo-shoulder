# Preview film: 108 designs, one yardstick, 1.69 to go (35 s)

`exo_preview.mp4`: 35.00 s, 1920x1080, 30 fps, H.264 yuv420p (crf 18, faststart), 8.31 MB, with an original
synthesised soundtrack (AAC 160 kb/s, -17.6 LUFS integrated, true peak -1.1 dBFS). The film is built to be read with the sound off; every claim is on screen.
Rendered locally from the repository at `d7f4bd2` (2026-10-16T14:43Z; 821 commits over 43.0 h), the last commit at which every
one of the 108 designs in `morphs.json` has a basic motion preview. Basic previews only: no CAD render, nothing read from `renders/` or `pipeline/`.

It answers the user's request of 2026-10-16 (~15:30 UTC): 30-40 s, less draggy, built the way research fast forwards and trailers are
(the final board, `docs/research/preview_film/final_board.md`, and its style guide). The brief that still stands: greyscale in the dashboard
theme, basic previews, many simple tests and the graphs, few words, faster, and how the score is made, told as a story.

**Intended cold takeaway** (to be tested by outside critics, not by the maker): *an automated search tried 108 exo designs and ~806 thousand
configurations against one score; an independent verifier marked most claims down; the verified best is 93.31 against a 95 target, still running.*

## Spec, planned vs measured on the encoded file

| spec | target | measured | instrument |
|---|---|---|---|
| running time | 30-40 s (aim 35) | 35.00 s | ffprobe |
| hook | motion within 3 s, no title | the full moving wall on frame 0 | frame 0 |
| shots | 20-30 | 23 | cut list |
| cuts the detector sees | all planned cuts | `gt(scene,0.3)`: 0 of 22 (0 detections); 0.05: 9 of 22 (30); 0.02: 17 of 22 (60). The instrument does not fit this footage (see below); the cut list is exact by construction | ffmpeg lavfi.scene_score |
| median shot | <= 1.5 s | 1.0 s | cut list |
| longest shot | <= 4 s, one climax <= 5 s | 3.0 s; climax 5.0 s | cut list |
| words on screen | <= 60 words, <= 4 per label | 48 words + numbers and axis ticks (149 tokens in all); longest label 3 words | scene scripts |
| type size | heroes >= 140 px, labels >= 48 px, nothing < 36 px | smallest text drawn 36 px (axis ticks, keys, the snapshot line); labels 48-64 px; heroes 140-180 px | the draw calls, every 5th frame |
| colour | greyscale theme | max channel spread 13 (of 255) over every 10th frame | numpy on the frames |
| numbers | 0 unsourced; filled = independent only | every number below has its repo path | this README; independent check pending |

**Why the scene detector misses the cuts.** ffmpeg's scene score is a whole-frame luminance difference. This film is thin light lines on a
dark canvas that is ~90 % empty, so even a full change of layout moves few pixels: the planned cuts score 0.0057 to
0.2488 (median 0.0378), while motion inside shots peaks at 0.0851
(median 0.00015). The montage cards and the pull-back are match cuts on the pinned 95 line by design, so they score lowest
(12.0 s: 0.0057). Shot counts and lengths therefore come from the frame numbers in the producer's cut list, which the
renderer uses directly; the per-cut scores are in `measure.json` of the producer folder.

A phone-scale sheet (each shot at 390 x 219, a 16:9 frame on a 390-pt-wide phone in portrait) was made for the critics; the type rule
above is the arithmetic behind it (36 px at 1080p is ~7 pt on that phone, 48 px ~10 pt, 140 px ~28 pt).

## Cut list (every cut a hard cut on a 120 BPM beat; 15 frames = 0.5 s)

| shot | time | s | picture | on screen | source (git at `d7f4bd2`) |
|---|---|---|---|---|---|
| H1 | 0:00.0-0:01.5 | 1.5 | Cold open, no title: the wall of all 108 basic motion previews (12 x 9, ideation order) moving in sync from frame 0; slow push (1.00 -> 1.04); the leader's tile gets a frame at 1.0 s | 108 designs | 108 designs; 108 previews (`docs/dashboard/data/motion.json`, `morphs.json` at `d7f4bd2`) |
| H2 | 0:01.5-0:03.0 | 1.5 | Hard cut into the framed tile: the leader (minarc-stop-knuckle-4r) preview large, arm rising from forward raise to overhead | goal within 1 cm never touching | goal from CLAUDE.md / REQUIREMENTS.md (pass at 14 mm, aim 10) |
| S3 | 0:03.0-0:04.0 | 1.0 | in-band: skin arc, 2-14 mm band, 100 metal dots, 89 inside (a proportion, not a map); meter to 0.894 against the 0.90 tick, shortfall outlined | in-band 0.89 2 14 mm | `docs/research/minarc_final_polish/verify/v_pick1_fit60_bench.json` final.inband14 0.8941 (= rows polished_bench.pick1) |
| S4 | 0:04.0-0:05.0 | 1.0 | follow: 110 clip-frame cells fill; meter passes the 0.95 tick | follow 110/110 | Bench(110,360): 110 clip frames, follow 1.0 |
| S5 | 0:05.0-0:06.0 | 1.0 | reach: 360 pose dots (top row = 28 overhead, 7 filled; 332 others, 263 filled; hollow = missed; positions are counts, not a pose map); meter to 0.75 against 0.90 | reach 270/360 overhead | final.ws_taken 270 / 360, overhead140_ws {'ws': 28, 'taken': 7}, reach 0.75 |
| S6 | 0:06.0-0:07.0 | 1.0 | contact: the 11 contact poses drop below a skin line; penalty meter to 0.028 against a tick at 0 | contact 11 poses | verifier.contact_raw.n 11 (deepest -13.17 mm); contact 0.0281 = 11 / 391 |
| S7 | 0:07.0-0:09.5 | 2.5 | The four shortfalls fly off their meters and stack down from 100 on one yardstick (score points): in-band 0.21, follow 0, reach 5.45, contact 1.02; the stack ends at 93.31, below the dashed 95. No equation | in-band follow reach contact 100 95 reach 93.31 score | `tools/concept_bench.py` gap_of: 0.59 + 0 + 15.0 + 2.81 = 18.4; score 100 (1 - 18.4/275) = 93.31 |
| M1 | 0:09.5-0:10.0 | 0.5 | Montage card 1/8 (ideation order): seed-spm-3rrr preview + mini yardstick, slashed ring (dead): 29.66, tag 'dead' | 25 50 75 95 29.66 dead | rows/seed-spm-3rrr.json gap 193.44, dead |
| M2 | 0:10.0-0:10.5 | 0.5 | Montage card 2/8 (ideation order): fivebar-roll preview + mini yardstick, slashed ring (dead): 67.59 | 25 50 75 95 67.59 | rows/fivebar-roll.json gap 89.13, dead |
| M3 | 0:10.5-0:11.0 | 0.5 | Montage card 3/8 (ideation order): floating-centre-3r preview + mini yardstick, ring at the claim 78.85 -> filled verifier dot: 50.43, tag 'refuted' | 25 50 75 95 50.43 refuted | rows/floating-centre-3r.json gap 58.17 -> v_gap 136.31, refuted |
| M4 | 0:11.0-0:11.5 | 0.5 | Montage card 4/8 (ideation order): crown-ring-3r preview + mini yardstick, hollow ring (self-measured, no verifier number): 70.05, tag 'self-measured' | 25 50 75 95 70.05 self-measured | rows/crown-ring-3r.json gap 82.37, screened |
| M5 | 0:11.5-0:12.0 | 0.5 | Montage card 5/8 (ideation order): raglan-routed-3r preview + mini yardstick, hollow ring (self-measured, no verifier number): 84.47 | 25 50 75 95 84.47 | rows/raglan-routed-3r.json gap 42.72, screened |
| M6 | 0:12.0-0:12.5 | 0.5 | Montage card 6/8 (ideation order): skin-normal-3r-knuckle-cufflink preview + mini yardstick, ring at the claim 91.10 -> filled verifier dot: 89.42, tag 'verified' | 25 50 75 95 89.42 verified | rows/skin-normal-3r-knuckle-cufflink.json gap 24.47 -> v_gap 29.1, verified |
| M7 | 0:12.5-0:13.0 | 0.5 | Montage card 7/8 (ideation order): slotted-eccentric-j2-3r preview + mini yardstick, ring at the claim 73.09 -> filled verifier dot: 58.11 | 25 50 75 95 58.11 | rows/slotted-eccentric-j2-3r.json gap 74.0 -> v_gap 115.21, refuted |
| M8 | 0:13.0-0:13.5 | 0.5 | Montage card 8/8 (ideation order): geneva-tail-knuckle-pinknee-3r preview + mini yardstick, ring at the claim 93.99 -> filled verifier dot: 91.43 | 25 50 75 95 91.43 | rows/geneva-tail-knuckle-pinknee-3r.json gap 16.53 -> v_gap 23.57, verified |
| Z1 | 0:13.5-0:16.0 | 2.5 | The leader's card (filled dot 93.31) pulls back into the wall; dead / refuted / duplicate tiles dim; the 13 verified tiles get a frame | 93.31 13 verified of 108 | morphs.json statuses at `d7f4bd2`: {'screened': 10, 'ideated': 44, 'refuted': 11, 'verified': 13, 'dead': 19, 'duplicate': 7, 'modelling': 4} |
| Z2 | 0:16.0-0:18.5 | 2.5 | Every timed concept-bench configuration as a density cloud: x = run order, y = score 0-100, dashed 95; counter to 270,718 | 270,718 configurations 25 50 75 95 | `docs/concepts/sweeps/*.json` at `d7f4bd2`: 57 files, 270,737 rows, 270,718 timed ('_' files excluded) |
| Z3 | 0:18.5-0:20.0 | 1.5 | The cloud shrinks to a block (area ~ 270,718); a GPU block (area ~ 535,134) slides in; the counter continues to 805,852 | 805,852 scored GPU 270,718 535,134 | 270,718 + 247,646 (gpu_searches.json, band evaluator) + 186,248 (docs/research/golden/README.md) + 101,240 (gks1_digest.json n_ok) = 805,852; the 560,478 bounded configurations are not counted |
| V1 | 0:20.0-0:22.0 | 2.0 | 4x punch-in on the 08:12 batch: the best screen reading 97.75 drawn as hollow numerals, struck through with all 3,374 readings above 95; "refuted" | 97.75 refuted 95 75 80 85 90 100 | sweep minimum gap 6.19 at 2026-10-16T08:12:02Z = 97.75; 3,374 readings >= 95, all minarc-stop-knuckle-4r 08:12:01-02; refuted 09:45 / 09:49 UTC in events.jsonl (needs J2 stops 1.4-2 deg from the fold, under the 5-deg rule) |
| V2 | 0:22.0-0:25.0 | 3.0 | 30 claims as hollow rings (axis 30-100, sorted by claim, no row labels); filled verifier dots slide to the re-measured scores in one 1-s stage: 26 down, 4 up | claimed verified 26 of 30 came in lower 95 40 60 80 100 | rows/*.json `gap` (minarc: v_gap_claim_reading 15.42) vs `v_gap` at `d7f4bd2`; 26 of 30 lower; the 10 rows whose v_gap equals the claim were written in the screener's own commit and are not drawn |
| V3 | 0:25.0-0:27.0 | 2.0 | The simplest class (three pins on bearing pairs, zero complexity): 154 hollow basin bests; the top one (89.51) drops to its independently re-measured 87.81; a bracket spans the gap to 95 | three plain pins best 87.81 95 70 80 90 100 | `docs/research/golden/gpu_frontier.json` basins[].best (top gap 28.85 = 89.51); skeptic re-measure 33.51 = 87.81 on the leader's protocol (golden/README.md verification table) |
| C1 | 0:27.0-0:32.0 | 5.0 | The climb: verified leader on a true time axis (15 Oct 20:32 -> 16 Oct 13:58 UTC, 17 hours), six steps landing as a constant-speed playhead passes their times; bracket to the dashed 95; "1.69 to go" | 75.83 84.51 88.96 90.38 92.89 93.31 17 hours 1.69 to go 95 70 80 90 100 | events.jsonl 20:32 (66.47), 00:32 (42.59), 03:58 (30.35), 06:30 (26.45, polish protocol); rows/minarc-stop-knuckle-4r.json v_gap 19.54 (11:57) and polished_gap 18.40 (13:58); 95 - 93.31 = 1.69 |
| B1 | 0:32.0-0:35.0 | 3.0 | Button, hard cut on the 32.0 s bar line: the leader moving at full size; "93.31 -> 95 / still running" at full contrast; snapshot date and a pointer to the dashboard; no fade | 93.31 → 95 still running snapshot 16 Oct 2026 · live dashboard | rows polished_gap 18.40, polished_status CONFIRMED; 95 = gap 13.75; snapshot `d7f4bd2` (2026-10-16T14:43Z) |

Structure: 0-3 s hook (motion, no title) · 3-9.5 s how the score is made (four real counts as pictures, then one number) · 9.5-20 s scale
(montage, then one pull-back 1 design -> 108 -> 270,718 -> 805,852) · 20-27 s the outside judge (struck reading, 26 of 30, the simplest
class) · 27-32 s the one peak (verified climb against the dashed 95) · 32-35 s the button.

## Visual grammar

- The dashed 95 line sits at y = 270 px in every data shot; only the scale below it changes.
- Filled dot = the independent verifier's number. Hollow ring = self-measured. Ring with a slash = dead. Where a verifier number exists, the
  claim stays as a hollow ring joined to the filled dot, and the number printed is the verifier's.
- Greys only (canvas #1a1a19, text #f0efec, context #898781, hairlines #313130, fill #c3c2b7, dimmed #4a4947; Caladea and Inter stand in
  for the dashboard's fonts). The takeaway is always the largest, brightest element.
- Motion: text enters in 7 frames on cubic-bezier(0, 0, 0.2, 1); moves use (0.4, 0, 0.2, 1); data transitions are one ~1-s stage; the
  pull-back zooms in log space; hard cuts only, no fades between shots.

## What the pictures do and do not claim (disclosures)

- **The previews are basic kinematic sketches** from `docs/dashboard/data/motion.json` on the primitive shoulder, each drawn at its concept
  file's configuration. The leader's preview is not drawn at pick1's polished parameters; the numbers on screen are pick1's.
- **S3-S6 are counts, not maps.** The in-band dots show 89 of 100 inside the band, not where on the skin the metal sits (which of the 11
  are too close or too far is not shown); the reach grid shows 7 of 28 overhead and 263 of 332 other poses taken, at arbitrary positions;
  the 11 contact poses are among the 90 missed (`why`: fold 70, slide 9, contact 11).
- **805,852 mixes evaluators.** 270,718 are concept-bench screens (CPU); 535,134 GPU evaluations combine 247,646 of the older band
  evaluator (87 searches, Oct 14-15) with 186,248 full-bench evaluations of the zero-complexity class and 101,240 of the pin-knee polish
  (gks1). The GPU block is drawn apart from the cloud for that reason. The 560,478 configurations that were only bounded are not counted.
- **97.75 is a screening reading, never a result.** It is drawn hollow and struck; the verified leader is 93.31.
- **26 of 30.** The 30 pairs are the rows whose `v_gap` differs from the claim. The 10 rows whose verifier number equals the claim
  (acromial-rocker-3r, back-anchored-ring-3r, fivebar-roll, offset-arc-selfalign, scapula-halo-track, seed-2r-cring, seed-arc-rails, seed-pauldron-shells, seed-spm-3rrr, trombone-arc) got both fields in the screener's own commit, so they are not independent re-measures and are not drawn.
- **The simplest class shows 87.81, not 88.71.** v2 labelled 88.71 (gap 31.04) the "verified ceiling"; that is the claimant's own reading on
  the fit-110 protocol, which the skeptic did not re-measure (its farm job never landed). The skeptic reproduced 33.51 = 87.81 to the digit on
  the verifier protocol (fit Bench(60,160) -> frozen -> worn Bench(110,360) exact), the same protocol as the leader's 18.40. This film shows
  87.81 and calls it "best", not "ceiling": 560,478 configurations were bounded, but the best found is a measurement, not a proof.
- **The climb** draws each step at the verifier's number on the protocol of that day. As in v2, three verifier numbers are left out on
  purpose: spine-parked-j2-3r's 34.29 (87.53) at 03:39 on O15 hubs that the "Keep O20 only" ruling voided; the H1 verifier's margin-5
  reading 24.48 (91.10) at 06:30, drawn at its polish-protocol 26.45 (90.38, the lower one); and minarc variant B's 18.45 (93.29) at 09:45, a
  re-measure of a claim the verifier refuted, before the buildable stop tolerance was priced.
- **Snapshot.** HEAD has moved on (more designs than previews at the time of rendering), so the film stays at `d7f4bd2`; re-run it only
  at a commit where every `morphs.json` id has a preview (`snap3.py` asserts this).

## Sound

Original, synthesised in numpy for this film (no samples, no licensed music): a low A/E drone, a kick on every 2-s bar and a soft tick on
every 0.5-s beat, a click on every cut, a low thud on the contact shot, one low hit when 97.75 is struck, a descending tick cluster as the
30 claims move, one bell per step of the climb rising a semitone each, a held tone under "1.69 to go", a rise into the button, and a hit on
the 32.0-s downbeat followed by silence. Loudness: ffmpeg loudnorm (target -16 LUFS, single pass) measured -17.6 LUFS integrated, true peak -1.1 dBFS. A silent encode exists for sound-off feeds (same picture).

## Rebuild

`python3 make3.py` in the producer folder (snap3.py -> render3.py -> audio3.py -> assemble3.py -> gen_readme3.py): snapshot from git, 1050
frames rendered with cairosvg on 2 niced processes (~5 min on the shared 4-core box), encode, contact sheet, measurements, this README.
The producer scripts live in the session scratchpad (`tl3/`), as v2's did; the repo keeps the film, this README and the contact sheet.

## Not done by the maker (next)

The maker does not grade the cut. Next: three critics who did not make it watch it cold without this README and each write the one-sentence
takeaway and score it against the spec table; a separate number checker re-derives every on-screen number from git at `d7f4bd2`
(including the five corrections in the final board) and writes CHECK.md. If the critics call it long, the board's cut order applies
(V3, then one montage pair, then Z3: 30.5 s).
