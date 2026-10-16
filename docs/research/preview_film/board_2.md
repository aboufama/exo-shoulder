# Board 2: "the yardstick and the climb" (35.0 s preview film)

Storyboard for the 30-40 s tech preview the user asked for on 2026-10-16 (~15:30 UTC): "the video is still shitty ... find out what
makes a compelling tech preview, the video should be like 30-40 seconds, less draggy. See what professionals do when showing crazy
research". The earlier brief still holds: greyscale in the dashboard's theme, basic motion previews only (no detailed CAD), the huge
number of simple tests and the graphs, fewer subtitles, a faster pace, and how the score is determined, told as a story.

**Angle.** Open on the goal: an exo that rides within 1 cm of the skin and never touches it. Build the yardstick from four
measurements into one number. Pull back from one design to 108 designs to 805,852 scored configurations in one continuous zoom-out.
Let the verifier catch the claims that read too high. End on the verified climb and what is left, 1.69 points.

**The cold takeaway the film must produce** (each outside critic writes it after one silent viewing; the cut passes when the
sentences match): *"An automated search scored 108 exo designs and about 806 thousand configurations against one 4-part score. An
independent verifier knocked most claims down. The verified best is 93.31 against a 95 target, 1.69 to go."*

**Four verbs.** Every shot serves at least one of them or is cut (Rieseberg: replace nouns with verbs): **HUGE** (the scale of the
search), **HONEST** (claims re-measured, failures on screen), **CLOSE** (93.31 against 95), **WANT** (the viewer opens the dashboard).

## The cut list

21 shots, 35.0 s = 1050 frames at 30 fps. Every cut lands on a 120 BPM beat (15 frames).

| # | time | dur | shot | words on screen | hero | verb |
|---|---|---|---|---|---|---|
| S1 | 0:00.0-0:02.0 | 2.0 | leader preview rising to overhead | goal: within 1 cm | within 1 cm | WANT |
| S2 | 0:02.0-0:03.0 | 1.0 | punch-in on the shoulder cap, overhead | never touching | never touching | WANT |
| S3 | 0:03.0-0:04.0 | 1.0 | in-band: 100 metal dots over a skin band | in-band 0.89 · 2 · 14 mm | 0.89 | HONEST |
| S4 | 0:04.0-0:05.0 | 1.0 | follow: 110-frame filmstrip fills | follow 110/110 | 110/110 | HONEST |
| S5 | 0:05.0-0:06.0 | 1.0 | reach: 360 pose dots, 270 filled | reach 270/360 · overhead | 270/360 | HONEST |
| S6 | 0:06.0-0:07.0 | 1.0 | contact: 11 dots sink under a skin line | contact 11 poses | 11 | HONEST |
| S7 | 0:07.0-0:09.5 | 2.5 | the four shortfalls stack into one yardstick | score 93.31 · 95 · reach | 93.31 | CLOSE |
| M1-M6 | 0:09.5-0:12.5 | 6 x 0.5 | montage: 6 designs on the same yardstick | one number + one tag each | the dot's height | HUGE, HONEST |
| Z1 | 0:12.5-0:15.5 | 3.0 | zoom-out 1: the leader's tile pulls back into the wall of 108 | 93.31 verified · 108 designs | 108 | HUGE |
| Z2 | 0:15.5-0:18.5 | 3.0 | zoom-out 2: 270,718 configurations fill the score axis | 270,718 configurations · 95 | 270,718 | HUGE |
| Z3 | 0:18.5-0:20.0 | 1.5 | zoom-out 3: + the GPU block, area to count | 805,852 scored · GPU · in 43 hours | 805,852 | HUGE |
| V1 | 0:20.0-0:22.0 | 2.0 | punch-in: the 97.75 screening reading is struck | 97.75 · refuted · 95 | 97.75 (struck) | HONEST |
| V2 | 0:22.0-0:25.0 | 3.0 | 30 claims slide to the verifier's number | 26 of 30 dropped · claimed · verified · 95 | 26 of 30 | HONEST |
| V3 | 0:25.0-0:27.0 | 2.0 | the simplest class hits its ceiling | simplest class · ceiling 88.71 · 95 | 88.71 | HONEST, CLOSE |
| C1 | 0:27.0-0:32.0 | 5.0 | the climb: verified leader over 17 hours | 6 step numbers · 17 hours · 1.69 to go · 95 | 1.69 to go | CLOSE |
| B1 | 0:32.0-0:35.0 | 3.0 | button: the leader moving, the result | 93.31 → 95 · still running · snapshot 16 Oct 2026 · live dashboard | 93.31 → 95 | CLOSE, WANT |

Structure: Amini et al.'s commonest professional data-video shape (Establisher S1-S2, Initial S3-S7, build Z1-V3, a single Peak C1,
Release B1) inside the trailer template: hook 0-3 s, core, escalation, end card in the last 3 s.

## Visual grammar held across the whole film

1. **The yardstick.** Every data shot (S7, M1-M6, Z1's first card, Z2, V1, V2, V3, C1) has a vertical score axis with the **dashed
   95 line pinned at the same screen height, y = 270 px**, in the text colour, 2 px, dash 12/10, labelled "95" in 48 px. Only the
   scale below it changes from shot to shot. Every cut between data shots is a match cut on that line. The viewer learns the line
   once in S7 and then reads every chart against it. This follows Tufte's "compared to what?" and gives the angle its name.
2. **Hollow ring = self-measured. Filled dot = the independent verifier's number.** The film introduces this in S7 (the filled
   93.31) and M3 (the first hollow-to-filled pair), keys it in V2, and keeps it to the end card. This is the honest-teaser rule: a
   self-measured number never wears the verified mark.
3. **Hierarchy in greyscale.** The canvas is `#1a1a19`. The takeaway is always the biggest element and is drawn in the text colour
   `#f0efec`. Context is muted `#898781` and structure is hairline `#313130`; meter and block fill is `#c3c2b7`. The punchline is
   never muted. These are the v2 theme values, sampled from `docs/dashboard/simple/index.html` + `docs/dashboard/dash.css`.
   Fonts: Caladea for numbers and heroes, Inter for labels.
4. **Type for a phone.** Hero numbers are 140-180 px (13-17 % of frame height). Labels are 48-64 px, secondary text is 36-40 px,
   and nothing is below 36 px. The subject fills at least 60 % of the frame, except the inset preview in S3-S6, which is context.
5. **Motion** (Material Design 1 curves; Heer & Robertson stage lengths):
   - Text enters in 7 frames (225 ms) with deceleration `cubic-bezier(0, 0, 0.2, 1)` and exits in 6 frames (195 ms) with
     acceleration `cubic-bezier(0.4, 0, 1, 1)`.
   - On-screen moves take 9 frames (300 ms), standard `cubic-bezier(0.4, 0, 0.2, 1)`. Camera pull-backs take 11-30 frames,
     standard.
   - Data transitions take one stage of about 30 frames (1 s), at most 2 stages per chart (axes, then data). Identical changes
     move together (common fate). There is no rotation.
   - Hard cuts only, on beats. The film never dips to the background between shots (v2 faded every segment).
   - A hero number settles in 5-7 frames and then holds at least 25 frames. Nothing sits more than 3 s without new motion.
6. **Basic previews only.** Mechanisms come from `docs/dashboard/data/motion.json`: the dashboard's monochrome previews, with the
   shoulder from the `_shoulder` row. Frames advance on the dashboard's own timer (93 ms per frame, 60-frame loop: rest → forward
   raise → overhead → abduction → across → behind; `docs/concepts/viz/kin.js` KEYS). Strokes are re-weighted for 1080p. There are
   no Cycles stills, no user-style CAD and no glb; nothing is read from `renders/` or `pipeline/`.

## Shot by shot

### S1 · 0:00.0-0:02.0 (f0-59) · hook: the goal
- **Picture:** the leader's preview (`minarc-stop-knuckle-4r`) on the primitive shoulder, 900 px tall (83 % of frame height),
  left of centre. It is already moving on frame 1: it starts at the preview frame between "forward raise" and "overhead", so the
  arm reaches overhead (elevation 152°) at about 1.2 s. There is no title, logo or setup.
- **On screen:** `goal: within 1 cm` (Caladea 120 px, text colour, right third).
- **Motion:** the label enters at f8 (7 frames, deceleration, rising 24 px). The camera pushes in slowly, 1.00 → 1.06 over 60
  frames (standard).
- **Data:** `docs/dashboard/data/motion.json` rows `minarc-stop-knuckle-4r` and `_shoulder`. The goal is the user's own rule:
  CLAUDE.md "The goal" and REQUIREMENTS.md (pass at 14 mm, aim for 10 mm, never touch).
- **Principles:** the hook is motion within 3 s, not a title slide (IEEE VIS "DO NOT include a title slide"; social-video 3-s
  hook). It is concrete before abstract (3Blue1Brown: the mechanism rides the shoulder before any score), with tight framing on
  the subject (Google ABCD). The label says "goal:" so it reads as the target, not a claim the leader meets; S6 shows the 11
  poses where it does not (red team).

### S2 · 0:02.0-0:03.0 (f60-89) · the hard part
- **Picture:** hard cut on the beat to a 2.2x punch-in on the shoulder cap at the overhead pose. The mechanism stroke arcs over
  the acromion, with the gap between metal and body visible. The preview keeps playing.
- **On screen:** `never touching` (Caladea 120 px).
- **Motion:** the label enters on the cut (5 frames, deceleration) and holds 25 frames.
- **Data:** same preview. The "never touch the skin" rule is in CLAUDE.md.
- **Principles:** at least 2 shots in the first 5 s (Google ABCD; S1-S4 give 4). One point per shot (Duarte glance test).

### S3 · 0:03.0-0:04.0 (f90-119) · measurement 1, in-band
- **Picture:** a skin arc 1500 px wide (muted, 3 px). Above it, the 2-14 mm band is drawn as a hairline-bounded strip (`#313130`
  at 40 %). 100 metal dots run along a link curve: 89 filled inside the band and 11 hollow outside it, on alternate edges.
  This shows the proportion only, not where the dots are; the verifier's record does not split above and below the band. The
  leader's preview keeps moving in a 220 px inset at top left, so the viewer knows what is being measured.
- **On screen:** `in-band 0.89` (hero 160 px) and band-edge ticks `2` and `14 mm` (Inter 40 px, muted).
- **Motion:** the hero is on screen from the cut (it settles by f95 and holds 25+ frames). The dots drop into place left to right
  over 18 frames (deceleration, 1-frame stagger).
- **Data:** in-band 0.8941 = `docs/concepts/rows/minarc-stop-knuckle-4r.json` `polished_bench.pick1.inband14`, which is the same
  as the verifier's `docs/research/minarc_final_polish/verify/v_pick1_fit60_bench.json` `final.inband14`. The band is
  `tools/concept_bench.py` (`(d >= 2) & (d <= 14)`, the share of metal points 2-14 mm from the skin).
- **Principles:** the four measurements appear as pictures before they become one number (style guide, structure). This is a
  unit picture of a share (small multiples are read more accurately than animation, Robertson et al. 2008).

### S4 · 0:04.0-0:05.0 (f120-149) · measurement 2, follow
- **Picture:** a filmstrip of 110 frame cells (12 px wide, 2 px gaps, 1540 px). A playhead sweeps across and every cell fills.
- **On screen:** `follow 110/110` (hero 160 px).
- **Motion:** the hero is on from the cut. The fill runs over 20 frames (standard easing).
- **Data:** follow 1.0 over the 110 fit-clip frames of Bench(110,360) (`tools/concept_bench.py` `Bench(n_clip=110, n_ws=360)`;
  `polished_bench.pick1.follow`).
- **Principles:** compared to what (110 out of 110, not "1.0"). One number per shot.

### S5 · 0:05.0-0:06.0 (f150-179) · measurement 3, reach
- **Picture:** 360 pose dots (r 11 px, 36 px pitch). The top row holds the 28 overhead poses (elevation ≥ 140°), 7 of them
  filled, with a hairline under the row. Below it are the other 332 poses, 263 of them filled. Hollow means not taken. Filled
  dots come first in each band, so this is a count picture, not a map.
- **On screen:** `reach 270/360` (hero 160 px) and `overhead` (Inter 40 px, muted, on the top row).
- **Motion:** the hero is on from the cut. The rows pop in top to bottom over 15 frames (deceleration, 2-frame stagger).
- **Data:** `v_pick1_fit60_bench.json`: `final.ws_taken` 270 of 360 (reach 0.75); `overhead140_ws` {ws 28, taken 7}. The 90 lost
  poses break down as `why` {fold 70, slide 9, contact 11} (reach attribution, not on screen).
- **Principles:** the overhead row puts the project's knowledge on screen as a picture rather than a footnote: reach, overhead
  most of all, is where the gap lives (CLAUDE.md "Reach is the priority").

### S6 · 0:06.0-0:07.0 (f180-209) · measurement 4, contact
- **Picture:** match cut. The 11 contact poses keep their screen positions from the S5 grid, then slide down 9 frames
  (standard) below a skin line (muted, 3 px), where they sit as metal dots inside the body.
- **On screen:** `contact 11 poses` (hero 160 px).
- **Data:** `v_pick1_fit60_bench.json` `verifier.contact_raw.n` 11 (all workspace poses, none on clips). contact 0.0281 = 11 / 391
  taken poses (281 workspace + 110 clip), `final.contact`.
- **Principles:** honest teaser. The leader's real failures are on screen right after the "never touching" goal (SIGGRAPH research
  guide: "fairly showing meaningful failure cases").

### S7 · 0:07.0-0:09.5 (f210-284) · four measurements → one number (the yardstick)
- **Picture:** on the right half, a vertical score axis: 100 at y = 60, 88 at y = 564 (42 px per point), and the dashed 95 at
  y = 270 drawn across the full frame. On the left, the four pictures from S3-S6 shrink to 160 px chips in a column. Each one
  drops its shortfall into a stack that hangs down from 100:
  - in-band 0.59: a 9 px sliver.
  - follow 0: no block; the chip shows "0" and dims.
  - reach 15.00: a 229 px block on the `#c3c2b7` fill, labelled `reach` inside in canvas colour.
  - contact 2.81: a 43 px block.

  The stack ends at 93.31, 71 px **below** the dashed 95. The miss is visible before any number says it.
- **On screen:** `score 93.31` (hero: "93.31" in Caladea 180 px, "score" in Inter 48 px), `95` on the dashed line (48 px), and
  `reach` inside its block. There is no equation.
- **Motion:** stage 1 (f218-247, 1 s, standard): the blocks fly in together (common fate). Stage 2 (f250): a filled dot (verified)
  at the stack bottom and the hero enter (7 frames) and hold to f284 (34 frames).
- **Data:** `tools/concept_bench.py` `gap_of()`:
  - gap = 100 × [(0.90 − 0.8941)⁺ + (0.95 − 1.0)⁺ + (0.90 − 0.75)⁺] + 100 × 0.0281 = 0.59 + 0 + 15.00 + 2.81 = 18.40.
  - score = 100 (1 − 18.40 / 275) = 93.31.
  - Each block is the term ÷ 2.75 in score points, so the stack height is exactly 100 − 93.31. 95 = gap 13.75.

  pick1 is the leader: `polished_gap` 18.40, `polished_status` CONFIRMED by an independent verifier, 13:58 UTC. The previews
  show the design's dashboard configuration and the numbers are pick1's, as disclosed in v2.
- **Principles:** the score becomes "4 measurements → 1 number" as a picture, never a two-line equation (style guide; v2 spent
  16 s on it). Heer & Robertson: at most 2 stages, each about 1 s. Compared to what: the dashed 95. **Assumption under test:** that
  the formula need not be spelled out. If the critics find the scale opaque, the fallback is one muted line under the axis,
  `score = 100 − gap ÷ 2.75` (36 px, 6 tokens). The critics decide; the maker does not.

### M1-M6 · 0:09.5-0:12.5 (f285-374) · montage: the same yardstick, many designs
- **Picture:** six hard cuts, one per beat (15 frames each). On the left, a design's preview at 760 px, playing from the loop's
  overhead key (the hardest pose). On the right, a mini yardstick (score 0-100, the dashed 95 at y = 270 as always) with the
  design's dot or dots and one number. The order is **ideation time** (`t_ideated`), not score, so the dot jumps up and down. The
  montage shows many tries, most failing, and does not fake a climb. The real climb is C1, on a true time axis.

  | cut | design | marks | number | tag | source (morphs.json at the snapshot) |
  |---|---|---|---|---|---|
  | M1 | seed-spm-3rrr | hollow | 29.66 | dead | gap 193.44, dead |
  | M2 | fivebar-roll | hollow | 67.59 | dead | gap 89.13, dead |
  | M3 | floating-centre-3r | hollow 78.85 → filled | 50.57 | refuted | gap 58.17 claimed, v_gap 135.93 |
  | M4 | raglan-routed-3r | hollow | 84.47 | screened | gap 42.72, screened only |
  | M5 | skin-normal-3r-knuckle-cufflink | filled | 89.42 | verified | v_gap 29.10, verified |
  | M6 | slotted-eccentric-j2-3r | hollow 73.09 → filled | 58.97 | refuted | gap 74.0 claimed, v_gap 112.84 |

  A refuted card shows its claim as an unlabelled hollow ring with a hairline down to the verifier's filled dot. The one number on
  the card is the verifier's. Dead rows stay hollow; the film does not assume their equal `v_gap` is an independent re-measure.
- **On screen:** one number (Caladea 64 px) and one tag (Inter 48 px) per card, 12 tokens in all.
- **Data:** `docs/dashboard/data/morphs.json` (status, gap, v_gap, t_ideated); previews from `motion.json`. Every score is
  100 (1 − g/275), rounded half-up.
- **Principles:**
  - Trailer cut rate: 0.5 s per montage cut, on beats.
  - Let the results speak: one caption each (Sora clips paired only with their prompt; Boston Dynamics videos without words).
  - Honest teaser: two dead and two refuted cards out of six. No cherry-picking (SIGGRAPH guide: "Picking only the top 5 is not
    representative").
  - The number is too short-lived to read at 0.5 s. The dot's height is what a glance reads; the number is there for a viewer who
    pauses.

### Z1 · 0:12.5-0:15.5 (f375-464) · zoom-out 1: one design → 108
- **Picture:**
  - f375-389: a seventh card, the leader, with its filled dot at 93.31 and the tag `verified`.
  - f390-419: the camera pulls back (scale 7.5 → 1.0, 30 frames, standard). The leader's card becomes one tile of the wall of all
    108 designs, 12 × 9 tiles of 118 px (1416 × 1062 px), every preview moving in sync on the dashboard's timer.
  - f420: the hero `108 designs` enters in the right margin.
  - f435: one change only (9 frames, standard). The dead, refuted and duplicate tiles dim to 30 %, and the 13 verified tiles
    get a hairline frame.
  - Hold to f464.
- **On screen:** `93.31` + `verified` (card), then `108 designs` (hero 160 px).
- **Data:** morphs.json, 108 rows at the snapshot: 13 verified, 11 refuted, 19 dead, 7 duplicate, 10 screened, 44 ideated, 4
  modelling. 108 of 108 have a preview in motion.json. Wall order is `t_ideated`, else `t_screened` (as in v2).
- **Principles:**
  - The search is shown as one continuous zoom-out. This is the board's own reference, Eames, *Powers of Ten* (1977), not from
    the research pack. Z1-Z3 are three takes joined by match cuts that carry the camera's speed across each cut, so each measured
    shot stays at 3 s or less.
  - Small-multiples wall (Tufte; Robertson 2008) with common fate (Heer & Robertson).
  - Honest: failures are dimmed, not hidden.

### Z2 · 0:15.5-0:18.5 (f465-554) · zoom-out 2: 270,718 configurations
- **Picture:** cut on the beat, still moving outward: the frame opens at scale 1.1 and settles to 1.0 over its first 15 frames,
  carrying Z1's pull-back. Full frame: the cloud of every timed concept-bench configuration, as a numpy density layer in the text
  colour.
  - x = run order, 15 Oct 15:48 → 16 Oct 13:45 UTC.
  - y = the yardstick, 0-100, with the dashed 95 at y = 270.
  - Points reveal left to right over 45 frames (standard). The counter rolls with the reveal, settles at f510 and holds 44
    frames.
  - The 3,374 points above 95 appear where they fall, a thin fleck above the line at 08:12. Nothing is said about them until V1.
- **On screen:** `270,718 configurations` (hero 160 px; "configurations" in Inter 48 px), `95`.
- **Data:** every `docs/concepts/sweeps/*.json` except files starting with `_` (57 files, 270,737 rows, 270,718 timed; id = stem
  before `@`). Score = 100 (1 − gap/275), clipped to 0-100. Already re-derived in `renders/2026-10-16_timelapse_v2/CHECK.md`.
- **Principles:** one graph per verb, here HUGE (v2 had two graphs saying "scale"). Axes first, then data (Heer & Robertson).
  The count carries its unit, so designs and configurations are never confused (Tufte).

### Z3 · 0:18.5-0:20.0 (f555-599) · zoom-out 3: + GPU = 805,852
- **Picture:**
  - f555-566 (11 frames, large-change 375 ms): the camera keeps pulling back and the cloud shrinks into a rectangle at the left
    whose **area is proportional to 270,718**.
  - A second rectangle slides in from the right, hairline outline with a flat `#313130` fill. Its area is proportional to
    535,134, the GPU evaluations. They are drawn as an area, not as points, because the per-evaluation GPU scores are not all on
    disk; the film does not fake a scatter.
  - f558-572: the counter rolls 270,718 → 805,852, then holds 27 frames.
- **On screen:** `805,852 scored` (hero 160 px), `GPU` (48 px, on the block), and `in 43 hours` (36 px, muted context).
- **Data:** 805,852 = 270,718 + 535,134. The 535,134 = 247,646 band-evaluator evaluations of the 87 searches in
  `docs/dashboard/data/gpu_searches.json` + 186,248 zero-complexity full-bench evaluations (`docs/research/golden/README.md`) +
  101,240 pin-knee polish evaluations (`docs/research/golden/gks1_digest.json` n_ok). The 560,478 bounded configurations are not
  counted (a bound is not a score). 43.0 h = first to last commit at the snapshot. All of these are in v2's CHECK.md.
- **Principles:** HUGE in one counter. The area-proportional picture is honest about what exists. Red team: "scored" mixes the
  older band evaluator with the full bench. The README must say so, and the GPU block stays visibly separate.

### V1 · 0:20.0-0:22.0 (f600-659) · the verifier catches the best reading
- **Picture:**
  - Hard cut back into the cloud, punched in 4x on the 08:12 batch above the dashed 95. The best-so-far point is a **hollow
    ring** (self-measured screening reading).
  - f606: the hero `97.75` enters, hollow-styled (outlined numerals, no fill).
  - f621, only 15 frames later so 97.75 never stands as a result: a horizontal stroke in the text colour strikes through all
    3,374 points above 95 (9 frames, standard), and they dim to 25 %.
  - f627: `refuted` enters (Inter 64 px, text colour). The struck number and the label hold to f659.
- **On screen:** `97.75`, `refuted`, `95`.
- **Data:** v2 `numbers.json` `sweep_best`: minarc-stop-knuckle-4r gap 6.19 at 2026-10-16T08:12:02Z = 97.75. `sweep_rows_ge95`
  3,374, all from that one minarc file. Refuted by the independent verifier at 09:45 / 09:49 UTC
  (`docs/concepts/events.jsonl`): the claimed reading needs J2 stops 1.4-2° from the fold, under the 5° rule.
- **Principles:** the outside judge on screen (Rieseberg: "Do not ask the model to judge itself"). Honest teaser: the most
  optimistic number in the repo is shown and struck, never left to read as a result (red team, style guide anti-patterns).

### V2 · 0:22.0-0:25.0 (f660-749) · claims, re-measured
- **Picture:**
  - 30 claim columns across the frame (48 px pitch, sorted by claim). The yardstick runs 40-100, dashed 95 at y = 270.
  - f660: 30 hollow rings at the self-measured claims (7 frames, deceleration).
  - f675-704 (one stage, 1 s, standard): filled dots slide from every ring to the independent verifier's number at once
    (common fate), each leaving a hairline. 26 go down and 4 go up; the 4 that rose are drawn too.
  - f708: the hero enters, then holds 41 frames.
- **On screen:** `26 of 30 dropped` (hero, Caladea 120 px, text colour, top left: the punchline is the brightest element, unlike
  v2's 28 px muted corner note). Key `○ claimed  ● verified` (Inter 36 px, muted, from f660). `95`.
- **Data:** `docs/concepts/rows/*.json`, comparing the self-measured `gap` (or `v_gap_claim_reading` for minarc, 15.42) with the
  independent `v_gap`. That gives 40 pairs: 26 lower, 4 higher (coupler-path-j1, geneva-tail-knuckle-3r, j2-arc-sector-3r,
  sliding-rivet-pauldron), and 10 identical to the digit, which are not drawn (listed in the v2 README).
- **Open question for the number checker (red team):** are the 10 identical rows true re-measures, or copied bookkeeping? If they
  are re-measures, draw all 40 and say `26 of 40 dropped`, the more conservative headline. If not, "26 of 30" stands, as v2's
  CHECK.md accepted.
- **Principles:** new knowledge as a beat, not a footnote (Rieseberg: produce new knowledge). Compared to what: every claim sits
  next to its re-measure (Tufte). One 1-s stage (Heer & Robertson).

### V3 · 0:25.0-0:27.0 (f750-809) · the simplest design class has a ceiling
- **Picture:** the yardstick (60-100, dashed 95 at y = 270) on the left 60 %.
  - 154 hollow rings in a strip plot (x-jittered): each one is the best of one CMA / polish / frontier basin of the
    zero-complexity class (three plain pins), self-measured. The top ring is 89.51.
  - f765-794 (1 s, standard): that top ring's filled verified reading drops to **88.71**. A solid hairline in the text colour (the
    class ceiling) draws across at 88.71, and a bracket marks the empty space up to the dashed 95.
- **On screen:** `simplest class` (Inter 56 px, text colour) and `ceiling 88.71` (hero 160 px). `95`.
- **Data:** `docs/research/golden/gpu_frontier.json` `basins[].best.gap` (154 basins, best 28.85 = 89.51). The ceiling is the
  class's verified 31.04, exact and frozen, reproduced by the skeptic (`docs/research/golden/README.md`): 100 (1 − 31.04/275) = 88.71.
- **Principles:**
  - New knowledge on screen: "the simplest class cannot reach 95".
  - The same visual verb as V2 (a hollow ring dropping to a filled dot), so the grammar is learned once and reused.
  - It explains why the leader is a 4-joint design.
  - It is the **first cut** if the critics call the film long; see the cut order below.

### C1 · 0:27.0-0:32.0 (f810-959) · the climb (climax, 5.0 s)
- **Picture:** a full-frame step chart.
  - x = **true time**, 15 Oct 20:32 → 16 Oct 13:58 UTC (17.4 h). y = the yardstick, 70-100, with the dashed 95 at y = 270
    (28.4 px per point).
  - The axes are already there on the cut (hard cut on the downbeat).
  - A playhead sweeps the time axis at constant speed from f825 to f915. Each verified leader drops in as the playhead reaches its
    time: a riser and tread (6 frames, standard), a filled dot, and its number as the hero (Caladea 140 px, entering in 7 frames).
    The previous number shrinks to a 40 px muted label beside its step.
  - Above the current step, that design's preview plays at 180 px, so the viewer sees the design change as the score climbs.
  - f915-923: a bracket draws from 93.31 up to the dashed 95. f924: the hero `1.69 to go` enters (Caladea 160 px) and holds to
    f959 (35 frames).

  | step lands | design (preview) | gap | score | source |
  |---|---|---|---|---|
  | f825 | seed-offset-3r-slides | 66.47 | 75.83 | events.jsonl 2026-10-15 20:32 verified |
  | f846 | offset-skin-normal-3r | 42.59 | 84.51 | events.jsonl 2026-10-16 00:32 verified (k4216) |
  | f863 | skin-normal-3r-pin-knee | 30.35 | 88.96 | events.jsonl 03:58 verified |
  | f876 | pin-knee polish H1 (pin-knee preview) | 26.45 | 90.38 | events.jsonl 06:30 VERIFIER H1 CONFIRMED |
  | f905 | minarc-stop-knuckle-4r BDp | 19.54 | 92.89 | rows/minarc-stop-knuckle-4r.json v_gap, 11:57 |
  | f915 | minarc pick1, polished (minarc preview) | 18.40 | 93.31 | rows/minarc-stop-knuckle-4r.json polished_gap, 13:58 |

- **On screen:** the six step numbers (one hero at a time), `17 hours` (36 px, muted, under the axis span), `1.69 to go`
  (hero), `95`.
- **Data:** v2 `numbers.json` `leader_steps`, re-derived in CHECK.md. The three verifier numbers the chart leaves out on purpose
  (O15-hub 34.29, H1's margin-5 24.48, minarc B's 18.45) are disclosed in the v2 README and must be repeated in the v3 README.
  95 − 93.309 = 1.69.
- **Principles:**
  - The AlphaFold reveal: one chart of the best result per round against a threshold stated in words.
  - The single Peak of the data-video structure. The one shot allowed up to 5 s.
  - A true time axis rather than equally spaced beats (Tufte, honesty): the gains slow as the score nears 95, and that is part of
    the story ("the last points are the hardest"). The cuts stay on beats; the in-shot events follow the data.
  - Do not over-promise: it ends below 95 (SIGGRAPH guide: "make sure it doesn't lead to disappointment").

### B1 · 0:32.0-0:35.0 (f960-1049) · button
- **Picture:** hard cut on the downbeat.
  - Right half: the leader's preview at 900 px, moving from rest through overhead once more.
  - Left half: `93.31 → 95` (Caladea 180 px, text colour, a filled dot before 93.31 and the dashed rule under 95). Below it,
    `still running` (Inter 64 px, text colour). Lowest, `snapshot 16 Oct 2026 · live dashboard` (Inter 36 px, muted).
  - No fade. The last frame holds to f1049 and the film ends on the final downbeat.
- **Data:** `polished_gap` 18.40 / `polished_status` CONFIRMED (rows/minarc-stop-knuckle-4r.json). 95 = gap 13.75. The snapshot
  date comes from `snapshot.py`. The dashboard is the live Dashboard artifact (`docs/HANDOFF.md`); the film points to it by name
  only, because a link is not clickable in a video and the page is private until the user shares it.
- **Principles:** an end card of at most 3 s at full contrast (v2 faded its end card to grey). One hero number and one line.
  A pointer to the full work (video-abstract guides). Film Editing Pro: "Last impressions are almost as important as first
  ones". End below 95, not "solved".

## Word budget (counted per shot; numbers counted as tokens)

| shot | tokens on screen | of which words |
|---|---|---|
| S1 | goal, within, 1, cm = 4 | 3 |
| S2 | never, touching = 2 | 2 |
| S3 | in-band, 0.89, 2, 14, mm = 5 | 2 |
| S4 | follow, 110/110 = 2 | 1 |
| S5 | reach, 270/360, overhead = 3 | 2 |
| S6 | contact, 11, poses = 3 | 2 |
| S7 | score, 93.31, 95, reach = 4 | 2 |
| M1-M6 | 6 numbers + 6 tags = 12 | 6 |
| Z1 | 93.31, verified, 108, designs = 4 | 2 |
| Z2 | 270,718, configurations, 95 = 3 | 1 |
| Z3 | 805,852, scored, GPU, in, 43, hours = 6 | 4 |
| V1 | 97.75, refuted, 95 = 3 | 1 |
| V2 | 26, of, 30, dropped, claimed, verified, 95 = 7 | 4 |
| V3 | simplest, class, ceiling, 88.71, 95 = 5 | 3 |
| C1 | 6 step numbers, 17, hours, 1.69, to, go, 95 = 12 | 3 |
| B1 | 93.31, 95, still, running, snapshot, 16, Oct, 2026, live, dashboard = 10 | 6 |
| **total** | **85 tokens** | **44 words** |

Words come to 44, inside the style guide's budget of 60. Counting every number and every repeated "95" gives 85 tokens. No shot
exceeds 12 tokens, and no single label exceeds 4 words. There are no sentences and no captions narrating the picture. If the
critics want fewer, cut in this order: `in 43 hours` (Z3, −3), `17 hours` (C1, −2), `overhead` (S5, −1).

## Measured against the spec (to fill in from the render, next to each target)

| spec | target | this board (planned) | how it is measured on the render |
|---|---|---|---|
| running time | 30-40 s, aim 35 | 35.0 s, 1050 frames | ffprobe |
| hook | motion within 2-3 s, no title | moving preview on frame 1, label at f8 | first frames |
| shots | about 20-30 in 35 s | 21 | ffmpeg `select='gt(scene,0.3)',showinfo` |
| median shot | ≤ 1.5 s | 1.0 s | same cut list |
| longest shot | ≤ 4 s, one climax ≤ 5 s | C1 5.0 s; all others ≤ 3.0 s | same |
| words | ≤ 60 words, ≤ 4 per label, ≤ 12 tokens per shot | 44 words, 85 tokens, max 12 per shot | word count from the scene scripts |
| hero hold | ≥ 25 frames after it settles | 25-44 frames (the montage is exempt: its read is the dot) | frame numbers above |
| type | hero ≥ 140 px, labels ≥ 48 px, nothing < 36 px | as specified | measured on frames; legible on a 390 × 219 downscale |
| colour | greyscale theme | v2 palette | ffmpeg signalstats SATMAX, as in v2's CHECK.md |
| sourced numbers | 0 unsourced | every number has a repo path above | an independent number checker re-derives them from git |
| detailed CAD | none | motion.json previews only | the scripts read no file from `renders/` or `pipeline/` |

Against v2: 76 s → 35 s; 19 shots → 21; median non-montage shot 6 s → 2 s; the score explainer goes from 16 s with about 60 words
and a two-line equation to 6.5 s with 17 tokens and no equation; title card → moving hook; faded end card → full-contrast button;
punchlines at 28 px muted → heroes at 120-180 px in the text colour.

## Sound (optional; the film is complete with sound off)

The track is a 120 BPM pulse synthesised locally (numpy → wav: a soft sine kick on each bar, a tick on each beat), so it is
licence-free (EG 2021: no copyrighted music). The structure:
- Cuts land on beats.
- The montage gets one tick per cut.
- In C1, each leader step gets a tick that rises one semitone per step, and a held tone sits under "1.69 to go".
- One downbeat hit on B1, and silence at f1049.

No claim depends on sound, because most feeds autoplay muted.

## Red team: where this board could drag or overclaim

- **Drag risk:** S7 (2.5 s), V2 (3 s) and C1 (5 s) are the long shots. Each has new motion at least every 1 s, and no frame sits
  still for more than 1.5 s (the longest hold is Z2's 44 frames).
- **"never touching" over a leader that touches on 11 poses:** the label is framed as the goal (`goal:` in S1), and S6 shows the
  11 contact poses 4 s later.
- **97.75:** shown hollow and struck within 15 frames, labelled `refuted`.
- **The montage could look like progress:** it is ordered by ideation time, so the dots jump; the only climb is C1, on a true time
  axis.
- **"805,852 scored" mixes two evaluators:** the GPU block is visibly separate and the README states which evaluator scored what.
- **"26 of 30":** pending the checker's answer on the 10 identical rows; "26 of 40" if those are true re-measures.
- **The yardstick scale hides 275:** if a critic calls the block heights unexplained, use the one-line fallback in S7.
- **The preview is not pick1's exact configuration:** disclosed in the README, as in v2. The numbers are pick1's.

**Cut order if the critics want it tighter:** V3 (−2.0 s, it doubles V2's verb), then S2 (−1.0 s; S1 carries both labels), then
Z3 (−1.5 s; Z2's counter then reads 270,718, and 805,852 moves to B1 as muted context). The film still lands at 30.5 s.

## Production (local CPU only, durable)

- **One command:** `make.py` in a new scratchpad folder `tl3/`. It reuses v2's `common.py` (theme, `Previews`) and `snapshot.py`
  (numbers), with one script per act. It regenerates the film from the repo, so the film updates whenever the leader moves
  (Rieseberg's altitude: build durable workflows).
- **Animatic first:** one keyframe PNG per shot at its real duration, under a minute of CPU. The critics pick between board 1 and
  board 2 on animatics. Only then is the 30 fps film rendered. 1050 frames is under half of v2's 2280. Use `nice -n 10` and at most
  2 heavy processes on the shared 4-core box.
- **Snapshot:** render at v2's snapshot (HEAD `d7f4bd2`, 2026-10-16T14:45Z), where CHECK.md already re-derived most numbers.
  - The checker must additionally re-derive, from git:
    - S5's 270/360, overhead 7/28, and the lost-pose split (fold 70, slide 9, contact 11);
    - S6's 11/391;
    - the M3 and M6 verifier scores, 50.57 and 58.97;
    - V3's top basin, 89.51;
    - C1's 17 hours.
  - At HEAD `b551444` (15:38Z) the verified leader is unchanged: 18.40 is still the lowest verified gap in `rows/`. But
    morphs.json now has 112 rows, and 4 round-7 picks have no preview yet: frontload-lobe-stopb-knuckle-3r,
    k-rim-lobe-stub-knuckle-3r, rim-lobe-arm-knuckle-3r and split-knuckle-twosided-3r. Re-snapshot with the same command once
    their previews land, so "every design has a basic preview" stays true.
- **Outside judges:** three critics who did not make the film watch it cold, without the README, and each writes the one-sentence
  takeaway. They score the cut against this spec and the user's brief, with measured values only (cut list, word counts,
  phone-scale legibility), not impressions. A separate number checker writes `CHECK.md`.
