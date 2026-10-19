# Final board: "108 designs, one yardstick, 1.69 to go" (35.0 s preview film)

The judge's cut for the 30-40 s tech preview the user asked for on 2026-10-16 (~15:30 UTC): "the video is still shitty ... find out
what makes a compelling tech preview, the video should be like 30-40 seconds, less draggy. See what professionals do when showing
crazy research". The earlier brief still holds: greyscale in the dashboard theme, basic motion previews only (no detailed CAD), the
huge number of simple tests and the graphs, fewer subtitles, a faster pace, and how the score is determined, told as a story.

The judge is a research-teaser editor who made neither board. This document scores both boards, picks the spine, grafts shots from
the other board, and fixes five problems the judge measured in the repo (listed under "Corrections"). It is a board, not a film.
The film has not been rendered or judged yet: next come the animatic, three cold critics and a number checker.

**Cold takeaway the film must produce.** After one silent viewing on a phone, each outside critic writes one sentence. The cut
passes only if those sentences match this one: *"An automated search tried 108 exo designs and ~806 thousand configurations against
one score. An independent verifier marked most claims down. The verified best is 93.31 against a 95 target, still running."*

## Verdict

**Spine: Board 2, "the yardstick and the climb"** (49 / 60 against 43 / 60), with five shots or devices grafted from Board 1.

| criterion | Board 1 "scale of the search" | Board 2 "yardstick and climb" |
|---|---|---|
| hook | **8.** The wall of 108 is the most striking real asset and lands inside 1 s. But a 7x zoom plus a 108-tile ripple plus a counter in 2 s is three motions at once, and the first label, "shoulder exo", says nothing. | **7.** The leader is moving on frame 1 and the goal is stated, which is clear. But one thin line drawing is the least striking thing in the repo. The 2.2x punch-in in S2 also magnifies a primitive preview (drawn at the concept file's configuration, not pick1's) to show a clearance the preview cannot prove. |
| clarity of the score story | **6.** Two numbers for one idea: "gap 18.40", then a drain to "93.31". That makes six shots, and the meters carry no counts. Its contact shot is also wrong (see Corrections 1). | **9.** The four measurements are real counts drawn as pictures (0.89, 110/110, 270/360 with 7/28 overhead, 11 poses). They stack into one number that visibly lands below the dashed 95 before any digit says so. There is no equation. |
| sense of scale | **9.** 108 → 270,718 → 805,852 in the first 8 s, with one counter that never resets. But the cloud and its dashed 95 appear before the viewer knows what 95 means. | **8.** One Powers-of-Ten pull-back (leader → 108 → 270,718 → 805,852). It arrives after the yardstick, so the cloud can be read. The GPU work is drawn as an area, not as fake points. It starts late, at 12.5 s. |
| pace | **8.** 32 s, 26 shots, median 1.0 s. But 12 montage cuts of 0.5 s carry digits nobody can read. | **8.** 35 s, 21 shots, median 1.0 s. But Z1, Z2 and V2 are three 3-s shots inside 12 s, and S1 holds a single label for 2 s. |
| honesty | **6.** The montage is sorted by score, so it fakes a climb (its own red team says so). Three montage dots are drawn hollow at the claim although a verifier number exists: offset-pointer-slip-sleeve 78.58 (verifier 72.21), crossed-skin-tracks 65.62 (65.08), coupler-path-j1 88.90 (89.46). | **9.** 97.75 is struck within 15 frames. The montage runs in ideation order, the climb is on a true time axis, and contact is on screen. Two slips: V3 puts the "verified" mark on 88.71, which no independent check reproduced, and the montage takes the refuted designs' scores from morphs.json while V2 takes them from rows (Corrections 3 and 4). |
| feasibility with the real assets | **6.** Three shots wait on a new per-pose dump of pick1 behind a reproduction gate. The 12 picks include the three hollow claims above that already have verifier numbers. | **8.** Every picture is drawn from counts already on disk (`v_pick1_fit60_bench.json`), and v2's scripts cover the wall, cloud, claims and climb. Small fixes: V2's 40-100 axis clips a claim at 35.65, and there is the rows vs morphs.json mismatch. |
| **total** | **43** | **49** |

**Taken from Board 1:**
1. The wall of 108 as the cold open (H1). The style guide asks for it, it is the user's "huge amount of simple tests", and
   it is the most striking frame we own.
2. "13 verified" as the hero of the pull-back (Z1), because H1 has already said 108.
3. The meter rail with a target tick under each measurement (S3-S6). The outlined shortfall on the rail becomes the block that
   drops into the yardstick in S7.
4. The three-way dot code. Filled = independent verifier. Hollow = self-measured. Hollow with a slash = dead. Each tag
   appears only the first time its style is used.
5. The climax shows only the newest step's value. The first step, 75.83, also stays as a small muted label, so the final frame
   reads from 75.83 to 93.31.

**Left out of Board 1:**
- The gap bar and the thermometer drain: two numbers for one idea.
- The score-sorted montage: a fake climb.
- The cloud before the score is explained.
- The 12-cut montage, cut to 8.
- The per-pose dump, kept only as an optional upgrade.

**Left out of Board 2:**
- The 2.2x punch-in (S2).
- The 180 px previews riding the climax: about 36 px on a phone, and one more simultaneous change.
- "in 43 hours" on Z3.
- The montage scores taken from morphs.json.

## Corrections the judge measured (the number checker must confirm)

1. **Contact is 11 poses, not "about 13".** `docs/research/minarc_final_polish/verify/v_pick1_fit60_bench.json` gives:
   - `verifier.contact_raw.n` 11: all workspace poses, none on clips, the deepest at −13.17 mm.
   - `final.near1_poses` 13: Board 1 took this as the contact count, but it counts metal within 1 mm of the skin (the
     near-touch gap), not contact.
   - `why.contact` 11 and `tools/concept_bench.py` line 36: contact poses count as not taken. So the 11 are among the 90
     hollow dots in S5, and contact 0.0281 = 11 / 391 solved poses (270 + 11 workspace + 110 clip).
   - Board 2's S6 has this right.
2. **"26 of 30" stands, not "26 of 40".** All 10 rows whose `v_gap` equals their `gap` received both fields in the screener's own
   commit, so none is an independent re-measure:
   - seed-spm-3rrr `1fde39d`, fivebar-roll `b743bac`, back-anchored-ring-3r `c0c86d3`, seed-arc-rails `ba99c52`
   - acromial-rocker-3r `bf39219`, offset-arc-selfalign `988ed7b`, scapula-halo-track `2ce1c22`, seed-2r-cring `ed83f7f`
   - seed-pauldron-shells `8111f33`, trombone-arc `2f1fa30`

   Found with `git log -S'"v_gap"'` on each row up to `d7f4bd2`. Recomputed at `d7f4bd2`: 30 moving pairs, 26 lower, 4 higher.
3. **The class ceiling on screen is 87.81, not 88.71.**
   - 88.71 (gap 31.04) is the claimant's own exact-frozen reading on the fit-110 protocol (`docs/research/golden/README.md`,
     verification table, CPU CMA optimum row).
   - The independent skeptic did not re-measure that protocol ("not re-measured in the time box"), and its farm job never
     landed: there is no `skeptic/farm_frozen_v00.json`.
   - The skeptic did reproduce **33.51 = 87.81** to the digit on the verifier protocol: fit Bench(60,160) → frozen → worn
     Bench(110,360) exact.
   - That is the same protocol as the leader's 18.40 (`v_pick1_fit60_bench.json`: fit60, wear bench, exact). 87.81 is
     therefore both the independently checked number and the like-for-like one. A filled dot on 88.71 would be a self-measured
     number wearing the verified mark.
   - v2 labelled 88.71 "verified ceiling". The v3 README must note this as a correction.
4. **One source for every score: `docs/concepts/rows/<id>.json`.** At `d7f4bd2`, morphs.json and rows disagree on two refuted
   designs:

   | design | morphs.json `v_gap` (score) | rows `v_gap` (score) |
   |---|---|---|
   | floating-centre-3r | 135.93 (50.57) | 136.31 (50.43) |
   | slotted-eccentric-j2-3r | 112.84 (58.97) | 115.21 (58.11) |

   Board 2 used morphs.json for the montage and rows for V2, so the same design would show two verifier scores 10 s apart. The
   film uses rows everywhere, the same source as V2, the leader and v2's CHECK.md.
5. **V2's axis runs 30-100, not 40-100.** The lowest of the 60 plotted values is sliding-rivet-pauldron's claim, 35.65.

Also checked:
- The leader at HEAD `dd8ff06` is still pick1 at 18.40 (lowest `v_gap` / `polished_gap` in rows).
- `motion.json` at HEAD has 109 rows for 112 designs, so the render stays at the `d7f4bd2` snapshot (108 of 108 previews).
- "17 hours" = 20:32 → 13:58 = 17 h 26 min.

## The cut list

23 shots, 35.0 s = 1050 frames at 30 fps. Every cut is a hard cut on a 120 BPM beat (15 frames). The button lands on the bar line at
32.0 s. Verbs: HUGE, HONEST, CLOSE, WANT. A shot that serves none is cut.

| # | time (frames) | dur | picture | words on screen | verb | from |
|---|---|---|---|---|---|---|
| H1 | 0:00.0 (0-44) | 1.5 | wall of all 108 previews, moving in sync from frame 0 | 108 designs | HUGE | B1 S02 |
| H2 | 0:01.5 (45-89) | 1.5 | cut into the leader tile: minarc-stop-knuckle-4r at 900 px, arm rising overhead | goal: within 1 cm / never touching | WANT | B2 S1 |
| S3 | 0:03.0 (90-119) | 1.0 | in-band: 100 metal dots over the 2-14 mm band, 89 in; meter + tick | in-band 0.89 · 2 · 14 mm | CLOSE | B2 S3 + B1 meter |
| S4 | 0:04.0 (120-149) | 1.0 | follow: 110 frame cells fill; meter past its tick | follow 110/110 | CLOSE | B2 S4 + B1 meter |
| S5 | 0:05.0 (150-179) | 1.0 | reach: 360 pose dots, 270 filled, overhead row 7 of 28; meter, wide shortfall | reach 270/360 · overhead | CLOSE | B2 S5 + B1 meter |
| S6 | 0:06.0 (180-209) | 1.0 | contact: the 11 contact dots sink below a skin line; penalty meter | contact 11 poses | HONEST | B2 S6 + B1 meter |
| S7 | 0:07.0 (210-284) | 2.5 | the four shortfalls drop into one yardstick hanging from 100; it stops 71 px below the dashed 95 | score 93.31 · 95 · reach | CLOSE | B2 S7 |
| M1 | 0:09.5 (285-299) | 0.5 | seed-spm-3rrr, slashed ring | 29.66 dead | HUGE, HONEST | B2 M1 |
| M2 | 0:10.0 (300-314) | 0.5 | fivebar-roll, slashed ring | 67.59 | HUGE, HONEST | B2 M2 |
| M3 | 0:10.5 (315-329) | 0.5 | floating-centre-3r, ring 78.85 → filled dot | 50.43 refuted | HONEST | B2 M3, rows number |
| M4 | 0:11.0 (330-344) | 0.5 | crown-ring-3r, hollow ring | 70.05 self-measured | HUGE | new pick |
| M5 | 0:11.5 (345-359) | 0.5 | raglan-routed-3r, hollow ring | 84.47 | HUGE | B2 M4 |
| M6 | 0:12.0 (360-374) | 0.5 | skin-normal-3r-knuckle-cufflink, ring 91.10 → filled | 89.42 verified | HONEST | B2 M5 |
| M7 | 0:12.5 (375-389) | 0.5 | slotted-eccentric-j2-3r, ring 73.09 → filled | 58.11 | HONEST | B2 M6, rows number |
| M8 | 0:13.0 (390-404) | 0.5 | geneva-tail-knuckle-pinknee-3r, ring 93.99 → filled | 91.43 | HUGE, CLOSE | B1 S23 |
| Z1 | 0:13.5 (405-479) | 2.5 | leader card, then pull-back into the wall; dead / refuted / duplicate tiles dim, 13 get frames | 93.31 / 13 verified · of 108 | HUGE, HONEST | B2 Z1 + B1 S03 |
| Z2 | 0:16.0 (480-554) | 2.5 | pull-back continues: 270,718 configurations fill the score axis | 270,718 configurations · 95 | HUGE | B2 Z2 |
| Z3 | 0:18.5 (555-599) | 1.5 | the cloud becomes an area block; the GPU block slides in | 805,852 scored · GPU | HUGE | B2 Z3 + B1 S05 counter |
| V1 | 0:20.0 (600-659) | 2.0 | punch-in on the 08:12 batch above 95; 97.75 hollow, then struck | 97.75 · refuted · 95 | HONEST | B2 V1 |
| V2 | 0:22.0 (660-749) | 3.0 | 30 claims slide to the verifier's number, 26 down, 4 up | 26 of 30 / came in lower · claimed · verified · 95 | HONEST | B2 V2 + B1 S24 label |
| V3 | 0:25.0 (750-809) | 2.0 | 154 hollow basin bests of the simplest class; the top one drops to its verified 87.81, a bracket up to 95 | three plain pins / best 87.81 · 95 | HONEST, CLOSE | B2 V3, corrected |
| C1 | 0:27.0 (810-959) | 5.0 | the climax: verified leader on a true time axis, six steps, bracket to 95 | 75.83 … 93.31 (one hero at a time) · 17 hours · 1.69 to go · 95 | CLOSE | B2 C1 + B1 S25 value rule |
| B1 | 0:32.0 (960-1049) | 3.0 | button: leader moving at 900 px; result at full contrast; no fade | 93.31 → 95 / still running / snapshot 16 Oct 2026 · live dashboard | CLOSE, WANT | B2 B1 |

Structure:
- 0-3 s: the hook, motion with no title (IEEE VIS).
- 3-9.5 s: how the score is made, concrete before abstract.
- 9.5-20 s: scale, the montage plus one continuous pull-back.
- 20-27 s: the outside judge.
- 27-32 s: the single peak (AlphaFold-style climb against a threshold).
- 32-35 s: the button.

This is the Establisher / Initial / Peak / Release shape of professional data videos, compressed into a teaser.

## Visual grammar (held across the film)

1. **The yardstick.**
   - Every data shot (S7, M1-M8, Z1's card, Z2, V1, V2, V3, C1, B1) has a score axis.
   - The **dashed 95 line is pinned at y = 270 px**: text colour, 2 px, dash 12/10, "95" in 48 px. Only the scale below the
     line changes.
   - Cuts between data shots are match cuts on that line.
2. **Dots.**
   - Filled = the independent verifier's number. Hollow ring = self-measured. Hollow ring with a slash = dead.
   - Where a verifier number exists, the claim stays on screen as an unlabelled hollow ring with a hairline to the filled dot
     (Tufte: "compared to what?").
   - The number printed is always the verifier's when one exists.
3. **Greyscale hierarchy** (v2 palette, sampled from `docs/dashboard/simple/index.html` + `dash.css`):
   - Canvas `#1a1a19`. Takeaway `#f0efec`, always the biggest element. Context `#898781`. Structure `#313130`. Fill
     `#c3c2b7`. Dimmed tiles `#4a4947`.
   - The punchline is never muted.
   - Fonts: Caladea for numbers and heroes, Inter for labels.
4. **Type for a phone.**
   - Heroes 140-180 px. Labels 48-64 px. Secondary text 36-40 px. Nothing below 36 px.
   - Every frame must pass the 3-s glance test on a 390x219 downscale.
   - The subject fills at least 60 % of the frame, except the 220 px leader inset in S3-S6, which is context.
5. **Motion** (Material Design 1; Heer & Robertson):
   - Text enters in 7 frames with `cubic-bezier(0,0,0.2,1)` and exits in 6 frames with `cubic-bezier(0.4,0,1,1)`.
   - On-screen moves take 9 frames with `cubic-bezier(0.4,0,0.2,1)`.
   - A data transition is one stage of about 1 s, at most 2 stages per chart. Identical changes move together. No rotation.
   - Hard cuts only, never a dip to the background.
   - A hero settles in 5-7 frames and holds at least 25. The montage is exempt: there the dot's height is the read.
6. **Basic previews only.**
   - Previews come from `docs/dashboard/data/motion.json` with the `_shoulder` body, frames advanced on the dashboard's 93 ms
     timer, strokes re-weighted for 1080p (mechanism 3 px, joints 6 px, body 2 px at 35 %).
   - Nothing is read from `renders/` or `pipeline/`.

## Shot notes (only what differs from or adds to the source boards)

**H1 (f0-44), cold open.**
- Picture: the wall of 12 x 9 tiles at 118 px (1416 x 1062, left-aligned), all moving in sync on frame 0, in ideation order
  (`t_ideated`, else `t_screened`, as in v2). There is no ripple build: the wall is full on frame 0, so the first frame is the
  biggest one.
- The camera pushes slowly toward the leader's tile, 1.00 → 1.04 over 45 frames (standard).
- The hero "108" (Caladea 180 px) + "designs" (Inter 56 px) sits in the right margin. It enters at f6 and holds 31 frames.
- At f30 the leader's tile gets a 2 px hairline frame, in 7 frames. This is the match that sets up H2.
- Source: `motion.json` 108 of 108 at `d7f4bd2`; `morphs.json` 108 rows.

**H2 (f45-89), the goal.**
- Picture: a hard cut on the beat into that tile, now the preview at 900 px (83 % of frame height). It starts at the loop frame
  between forward raise and overhead, so the arm is overhead by about f80.
- Words: "goal: within 1 cm" (Caladea 120 px), entering at f50, and "never touching" (Inter 64 px, text colour), entering at f55.
- Source: CLAUDE.md "The goal" and REQUIREMENTS.md. The "goal:" prefix keeps it from reading as a claim met; S6 shows the 11
  poses where the leader does touch.

**S3-S6, the four measurements** (Board 2's pictures, plus Board 1's meter rail).
- A 1400 px meter rail sits at the bottom of each shot: fill `#c3c2b7`, a 3 px target tick with no digits, and the shortfall
  outlined in the text colour.
- S3 in-band. The meter fills to 0.894 against the 0.90 tick, leaving a sliver. 100 metal dots are drawn, 89 inside the
  hairline band: a proportion, not a map. Band ticks "2" and "14 mm" are muted at 40 px. Source: `polished_bench.pick1.inband14`
  0.8941 = `v_pick1_fit60_bench.json` `final.inband14`.
- S4 follow. 110 cells fill in 20 frames. The meter passes the 0.95 tick, with no outline, because the target is met. Source:
  Bench(110,360) `n_clip` 110, follow 1.0.
- S5 reach. 360 dots: the top row is the 28 overhead poses (7 filled), then 332 others (263 filled). The meter stops at 0.75
  against the 0.90 tick, with a wide outline. Source: `final.ws_taken` 270, `overhead140_ws` {28, 7}; lost poses `why` {fold 70,
  slide 9, contact 11}, which is not shown on screen.
- S6 contact. Match cut: the 11 contact dots, already hollow in S5, slide below a muted skin line in 9 frames. A penalty meter
  fills from the left to 0.028 against a tick at 0. Source: `verifier.contact_raw.n` 11; 0.0281 = 11 / 391.
- Optional upgrade from Board 1: a real pose map (x = plane of elevation, y = elevation) and a distance histogram. These need a
  local per-pose dump of pick1 that reproduces 0.8941 / 1.0 / 0.75 / 0.0281 to 4 decimals and the verifier's 270 taken poses.
  If it is not done by the animatic, ship the count pictures above; they claim only the counts.

**S7 (f210-284), four measurements → one number.**
- The axis has 100 at y = 60 and the dashed 95 at y = 270 (42 px per point).
- Stage 1, f218-247: the four outlined shortfalls leave their meters and stack down from 100, all at once:
  - in-band 0.59 → 9 px
  - follow 0 → nothing (its chip dims)
  - reach 15.00 → 229 px, labelled "reach" inside
  - contact 2.81 → 43 px
- The stack ends at 93.31, 71 px below the dashed 95.
- Stage 2, f250: the filled dot and "93.31" (Caladea 180 px) + "score" (Inter 48 px) enter and hold 34 frames.
- Source: `tools/concept_bench.py` `gap_of()`: 0.59 + 0 + 15.00 + 2.81 = 18.40; score = 100 (1 − 18.40/275) = 93.31.
- Fallback, only if the critics call the block heights unexplained: one muted 36 px line, "score = 100 − gap ÷ 2.75".

**M1-M8 (f285-404), montage.**
- Layout: the preview at 760 px on the left, playing from the loop's overhead key. A mini yardstick on the right with the 95
  line at y = 270. One number in Caladea 64 px. A tag in Inter 48 px, on the first card of each style only.
- Order: `t_ideated`, ties broken alphabetically, so the dot jumps around. The leader is not in the montage; it is Z1's card.
- Picks: 2 dead, 2 refuted, 2 self-measured, 2 verified. Every number is 100 (1 − g/275), rounded half-up, from rows at
  `d7f4bd2`:

  | cut | design | t_ideated | marks | number | source |
  |---|---|---|---|---|---|
  | M1 | seed-spm-3rrr | 15 Oct 14:54 | slashed ring | 29.66 | gap 193.44, dead |
  | M2 | fivebar-roll | 15 Oct 15:12 | slashed ring | 67.59 | gap 89.13, dead |
  | M3 | floating-centre-3r | 15 Oct 15:12 | ring 78.85 → filled | 50.43 | gap 58.17 → v_gap 136.31, refuted |
  | M4 | crown-ring-3r | 15 Oct 17:21 | ring | 70.05 | gap 82.37, screened (no verifier number) |
  | M5 | raglan-routed-3r | 16 Oct 01:20 | ring | 84.47 | gap 42.72, screened (no verifier number) |
  | M6 | skin-normal-3r-knuckle-cufflink | 16 Oct 01:35 | ring 91.10 → filled | 89.42 | gap 24.47 → v_gap 29.10, verified |
  | M7 | slotted-eccentric-j2-3r | 16 Oct 05:47 | ring 73.09 → filled | 58.11 | gap 74.0 → v_gap 115.21, refuted |
  | M8 | geneva-tail-knuckle-pinknee-3r | 16 Oct 12:11 | ring 93.99 → filled | 91.43 | gap 16.53 → v_gap 23.57, verified |

- M4 is the one new pick, since Board 2 had six cards. crown-ring-3r is a screened design with no verifier number, ideated
  between M3 and M5, so the dot drops before it climbs. It has a preview at `d7f4bd2`.
- Tags: M1 "dead", M3 "refuted", M4 "self-measured", M6 "verified".

**Z1 (f405-479), one design → 108.**
- f405-417: the leader's card, a filled dot at 93.31 with the number.
- f418-445: pull-back, scale 7.5 → 1.0 (standard).
- f446: one change only. Dead (19), refuted (11) and duplicate (7) tiles dim to `#4a4947`, and the 13 verified tiles get a 2 px
  frame (9 frames). At the same time, "13 verified" (hero) and "of 108" (muted) enter and hold 26 frames.
- Source: `morphs.json` statuses at `d7f4bd2`: 13 / 11 / 19 / 7 + 10 screened, 44 ideated, 4 modelling.

**Z2 (f480-554), 270,718 configurations.**
- The shot opens at scale 1.1 and settles in 15 frames, carrying Z1's pull-back.
- The density cloud reveals left to right, f483-527. x = run order, 15 Oct 15:48 → 16 Oct 13:45. y = score 0-100, with the 95
  line at y = 270.
- The 3,374 points above 95 appear as a fleck at 08:12, with nothing said about them until V1.
- The counter settles at f527 and holds 28 frames.
- Source: `docs/concepts/sweeps/*.json`: 57 files, 270,737 rows, 270,718 timed; files starting with `_` excluded; id = the stem
  before `@`.

**Z3 (f555-599), 805,852 scored.**
- The cloud shrinks to a block whose area is proportional to 270,718 (11 frames). A `#313130` block with a hairline outline
  slides in, its area proportional to 535,134 GPU evaluations.
- The counter continues from 270,718 to 805,852 without resetting (Board 1), f558-572, and holds 28 frames.
- Words: "805,852" (hero) + "scored" (48 px) + "GPU" on its block.
- Source: 270,718 + 247,646 (`gpu_searches.json`, 87 searches, the older band evaluator) + 186,248
  (`docs/research/golden/README.md`) + 101,240 (`gks1_digest.json` n_ok). The 560,478 bounded configurations are excluded. The
  README must say that the GPU block mixes the band evaluator with the full bench.

**V1 (f600-659), the verifier strikes the best reading.**
- Punch-in 4x on the 08:12 batch.
- f606: "97.75" enters as outlined numerals, hollow-styled.
- f621: a stroke strikes all 3,374 points above 95 (9 frames) and they dim to 25 %.
- f627: "refuted" (Inter 64 px, text colour). Held to f659.
- Source: sweep minimum gap 6.19 at 08:12:02Z = 97.75; refuted at 09:45 / 09:49 UTC in `docs/concepts/events.jsonl` (needs J2
  stops 1.4-2° from the fold, under the 5° rule).

**V2 (f660-749), claims re-measured.**
- 30 columns, sorted by claim, no row labels. The axis runs **30-100**, with 95 at y = 270.
- f660: hollow rings enter.
- f675-704: one 1-s stage. Filled dots slide to the verifier's number, leaving hairlines: 26 down, 4 up (coupler-path-j1,
  geneva-tail-knuckle-3r, j2-arc-sector-3r, sliding-rivet-pauldron).
- f708: "26 of 30" (Caladea 160 px, text colour) + "came in lower" (Inter 56 px, text colour) enter and hold 41 frames.
- The key "○ claimed ● verified" (Inter 36 px, muted) is on from f660.
- Source: rows `gap` (or `v_gap_claim_reading` 15.42 for minarc) vs `v_gap`. 10 rows were never independently re-measured
  (Corrections 2) and are not drawn.

**V3 (f750-809), the simplest design class has a measured best.**
- Axis 60-100, with 95 at y = 270. A strip of 154 hollow rings: the best of each CMA / polish / frontier basin of the
  zero-complexity class (three pins on bearing pairs). The top ring is at 89.51.
- f750: "three plain pins" (Inter 56 px) enters.
- f758-782: the top ring's filled verifier dot drops to **87.81**. The number counts from 89.51 to 87.81 and changes from hollow
  to filled style. A text-colour hairline marks the best, and a bracket spans the empty space up to the dashed 95. Held 26 frames.
- Words: "best 87.81". Not "ceiling": 560,478 configurations were bounded, but the best found is a measurement, not a proof.
- Source: `docs/research/golden/gpu_frontier.json` `basins[].best.gap`, minimum 28.85 = 89.51, for the same configuration the
  skeptic re-measured at 33.51 on the leader's protocol (`docs/research/golden/README.md`, skeptic table) = 87.81.
- This is the first shot to cut if the critics call the film long.

**C1 (f810-959), the climb.**
- Axes on the cut: x = true time, 15 Oct 20:32 → 16 Oct 13:58 UTC; y = 70-100, with 95 at y = 270. "17 hours" is muted under
  the axis span.
- A constant-speed playhead runs f825-915. Steps land at f825 / 846 / 863 / 876 / 905 / 915: 75.83, 84.51, 88.96, 90.38, 92.89,
  93.31.
- Each step draws a riser and tread in 6 frames, a filled dot, and its value as the hero (Caladea 140 px, 7 frames). The previous
  value fades to its dot alone, except 75.83, which stays as a 40 px muted label.
- f915-923: a bracket from 93.31 to the dashed 95. f924: "1.69 to go" (Caladea 160 px) enters and holds 35 frames.
- The true time axis shows the gains slowing near 95. The cuts stay on beats; the steps inside the shot follow the data.
- Source: v2 `leader_steps`:
  - `events.jsonl` 20:32 (66.47), 00:32 (42.59), 03:58 (30.35), 06:30 (26.45, polish protocol)
  - `rows/minarc-stop-knuckle-4r.json` `v_gap` 19.54 (11:57) and `polished_gap` 18.40 (13:58)
  - 95 − 93.309 = 1.69
- The README repeats v2's three disclosed omissions: 34.29 on O15 hubs, H1's margin-5 24.48, minarc B's 18.45.

**B1 (f960-1049), button.**
- Hard cut on the downbeat at the 32.0 s bar line. Right half: the leader's preview at 900 px, moving through overhead once more.
- Left half:
  - "93.31 → 95" (Caladea 180 px, text colour, a filled dot before 93.31)
  - "still running" (Inter 64 px, text colour)
  - "snapshot 16 Oct 2026 · live dashboard" (Inter 36 px, muted)
- No fade: the last frame holds at full contrast.
- Source: `polished_gap` 18.40, `polished_status` CONFIRMED; 95 = gap 13.75; the date from `snapshot.py`.

## The spec, planned (to be re-measured on the render)

| spec | target | this board | instrument |
|---|---|---|---|
| running time | 30-40 s, aim 35 | 35.0 s, 1050 frames | ffprobe |
| hook | motion within 3 s, no title | the full moving wall on frame 0 | first frames |
| shots | 20-30 | 23 | ffmpeg `select='gt(scene,0.3)',showinfo` (the 0.5 s montage cuts must all register) |
| median shot | ≤ 1.5 s | 1.0 s (8 × 0.5, 4 × 1.0, 3 × 1.5, 2 × 2.0, 3 × 2.5, 2 × 3.0, 1 × 5.0) | same |
| longest | ≤ 4 s; one climax ≤ 5 s | 3.0 s; C1 5.0 s | same |
| words | ≤ 60; ≤ 4 per label | 44 words (89 tokens counting numbers); the longest label is 4 words; the most tokens in one shot is 12 (montage, C1) | scene scripts |
| hero hold | ≥ 25 frames after settling | 26-41 frames (montage exempt) | frame numbers above |
| type | hero ≥ 140 px, labels ≥ 48 px, nothing < 36 px | as specified | glyph heights on frames; 390x219 downscale |
| colour | greyscale theme | v2 palette | `signalstats` SATMAX |
| numbers | 0 unsourced; filled = independent only | every number has a repo path; Corrections 1-5 applied | independent number checker, writing CHECK.md |
| detailed CAD | none | motion.json previews only | scripts read nothing from `renders/` or `pipeline/` |

Compared with v2: 76 s → 35 s. Non-montage median shot 6 s → 2 s. The score explainer goes from 16 s with an equation to 6.5 s
of pictures with no equation. The title card becomes the moving wall. The faded end card becomes a full-contrast button. Punchlines
go from 28 px muted to 120-180 px in the text colour.

Words per shot:

| shots | words |
|---|---|
| H1 | 1 |
| H2 | 5 |
| S3-S7 | 9 |
| M1-M8 | 4 |
| Z1-Z3 | 5 |
| V1 | 1 |
| V2 | 6 |
| V3 | 4 |
| C1 | 3 |
| B1 | 6 |

## Red team (where this cut can still fail)

- **"within 1 cm" vs the 2-14 mm band.** A sharp viewer may see "14 mm" in S3 three seconds after "1 cm". 14 mm is the user's
  pass line and 10 mm the aim (REQUIREMENTS.md). If a critic flags it, drop the S3 tick labels; the band stays drawn.
- **0.5 s montage digits are not readable.** That is by design: the dot's height against the fixed 95 is the read. If 2 of the 3
  critics cannot say "most fail, a few verified", go to 6 cuts × 0.67 s, ending at the same frame.
- **The wall twice (H1, Z1).** Each appearance has its own job: H1 is "lots", Z1 is the verdict ("13 verified"). If the critics
  call it repetition, Z1 opens on the dimmed wall directly and gives its 1 s to V2.
- **Three honesty shots in a row (V1-V3, 7 s).** Each uses the same visual verb, hollow → filled, so it reads as one beat. V3 is
  the first cut.
- **The preview is not pick1.** The leader's preview is drawn from its concept file's best configuration; the numbers are pick1's.
  Disclose this in the README, as v2 did.
- **"805,852 scored" mixes evaluators.** The GPU block stays visibly separate, and the README names which evaluator scored what.
- **Stale snapshot.** HEAD has 112 designs and 109 previews. Render at `d7f4bd2`, and re-snapshot only when every `morphs.json` id
  has a preview, so "every design has a basic CAD" stays true. Never mix the two snapshots.

**Cut order if the critics want it tighter:**
1. V3 (−2.0 s → 33.0 s; C1 moves to 25.0 s and B1 lands on the 30.0 s bar line).
2. One montage pair, M2 + M5 (−1.0 s).
3. Z3 (−1.5 s; 805,852 moves to B1 as muted context).

The film still lands at 30.5 s.

## Production and checks (local CPU only)

- **One command:** `make.py` in a new scratchpad folder `tl3/`. It reuses v2's `common.py` (theme, `Previews`) and `snapshot.py`
  (numbers), with one script per act. `snapshot.py` gains:
  - an assert that every `morphs.json` id has a preview
  - the rows-only score rule (Corrections 4)
  - the 87.81 source (Corrections 3)
  - the 8 montage picks

  Rendering is `nice -n 10`, at most 2 heavy processes, on the shared 4-core box. The command regenerates the film from the repo
  whenever the leader moves.
- **Animatic first:** one keyframe PNG per shot, assembled at the real durations. Then the 30 fps render (1050 frames, under half
  of v2's).
- **Sound (optional):** the film works with sound off. The pulse is a locally synthesised, licence-free 120 BPM track:
  - a kick on each bar and a tick on each beat
  - one tick per montage cut
  - a semitone rise per C1 step, with a held tone under "1.69 to go"
  - a hit at 32.0 s, then silence
- **Outside judges:**
  - Three critics who did not make the film watch it cold, without the README. Each writes the one-sentence takeaway and scores
    the cut against the spec table with measured values only.
  - A separate number checker re-derives every on-screen number from git at `d7f4bd2`, including Corrections 1-5.
