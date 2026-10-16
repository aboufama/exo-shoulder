# Progress dashboard

**URL**: https://claude.ai/artifact/AMhjuE83FBhGXxu8vQBN7r (Dashboard artifact type, private to the user).

The user asked for "a dashboard artifact to track progress in each benchmark over time". It is the main place to watch
the project. Chat carries only the big updates. Every benchmark the project has is on it, each plotted over time:
the concept bench (morphology swarm), the built-CAD outside judges, the GPU search evaluator, the requirement board,
the event log and GPU spend.

Sources in the repo:

| What | Where |
|---|---|
| Page (the artifact's `files/index.html` + part files) | `docs/dashboard/index.html`, `dash.css`, `core.js`, `leader.js`, `bench.js`, `cad.js`, `board.js`, `reach3d.js`, `main.js` (each <= 256 KB) |
| Datasets (attached JSON files) | `docs/dashboard/data/<id>.json` |
| Manifest (id, title, description, file, sha256, rows, bytes, updated) | `docs/dashboard/manifest.json` |
| Builder | `tools/dash_build.py` |
| Local harness (the type's real runtime, offline) | `docs/dashboard/harness/serve.py`, `docs/dashboard/harness/shot.mjs` |

## Tabs: what each shows and the decision it serves

### Leader: is there a new winner?

- **Header sentence**: the current concept-bench leader (verified if one exists, else the best unverified evidence),
  its gap against the 3R baseline, the best built 3-DOF R1, and how many requirements pass. The dot beside "data
  gathered" is green while the data is under 30 min old, amber after that, and red if a source fails to load.
- **Concept bench leader (hero)**: the best *verified* morphology (re-measured by the verifier). Its gap is a large
  serif number in the accent colour when it beats the baseline. When nothing is verified yet, the hero says so, and
  dashed boxes show the best unverified evidence (the best sweep configuration, and the best claimed row when it is
  below the baseline). A scale runs from target 0 to the baseline. The side list shows every morphology below the
  baseline now, with its evidence type. *Decision: which morphology goes to the verifier, then to a GPU sweep and CAD.*
- **Headline figures**: morphologies ideated / modelled, screened / verified, how many are below the baseline, the best
  built R1 (red until it reaches 90 %), and requirements passing on the best design.
- **Concept bench record over time**: a step line of the best gap any configuration has reached so far, over all
  morphologies. It turns to the accent colour below the baseline. Each new record is a dot; the current record holder
  is named; faint dots are single configurations; diamonds are verified results. Configurations above the top of the
  scale (1.6 x baseline) are counted in the key. *A new leader shows up as a step down plus a colour change.*
- **Built CAD record: R1 over time**: the best 3-DOF R1 so far (a step line), each judged design as a dot (filled =
  full CAD, hollow square = keep-out CAD, faded = judged before that requirement's judging rule changed), and the 90 %
  pass line.

### Concept bench: where is each morphology going?

- **Optimisation over time, per morphology**: each line is one morphology's best gap so far against time, as its
  agent measured it. Lines below the baseline get one series colour each. Lines at or above it are muted, and
  dropped/refuted ones are dashed. The scale is symlog (compressed above ~30) so that a 300-gap start and a 40-gap
  finish fit in one chart, and the ticks show real values. Each line has an end label (hidden under 520 px, where
  tapping a line names it). *Decision: is a morphology still improving, or has it plateaued and should it be dropped?*
- **Reach vs in-band 14 mm**: one dot per morphology at its best evidence (filled = verified, ring = claimed, small dot
  = best sweep configuration), the shaded target corner (both >= 90 %) and the baseline diamond. *Which target is each
  morphology short on?*
- **Pipeline**: the funnel ideated -> modelled -> screened -> verified -> GPU -> CAD. The biggest drop between steps is
  in the critical colour. *Where is the swarm stuck?*
- **Every morphology**: a sortable, searchable table of all morphologies with gaps side by side (sweep best, claimed,
  verified), plus reach, in-band, follow, contact, configuration count, family, lens and last activity. The default
  order is by best evidence, with dropped rows last. The baseline row is shaded and sits at its gap position.

### Built CAD: how do the real judges score the built designs?

- **Each judged requirement over time**: small multiples on one shared time axis: R1, R1-aim, R3, R4, R16 (one shared
  0-100 % scale), then R2, R6, R8, R9, R10, R11. Each shows its pass threshold (dashed), the best 3-DOF value so far
  (a step line), the latest and best values, and every judged design as a dot. R7 and R17 (yes/no) are chip strips.
  4-DOF designs are hidden by default (the user: "focus on 3 dof"). The toggle shows them as muted dots, never joined
  to the 3-DOF line. *Decision: which requirement blocks the build next?*
- **GPU search evaluator**: the band evaluator's own estimates. These are search numbers, not judge numbers: in-band
  14 mm and workspace followed for every detail evaluation, and each search job's final fitness, each with its
  best-so-far line.
- **Where your arm can go with the exo on**: the 3-D R16 pose cloud of the newest built designs (`cov3d`, rebuilt by
  `tools/coverage3d.py`).

### Requirements: the board

One card per requirement: R1-R17 plus R1-aim and R5-aim (19 in all). Each card shows the latest state on **the best
judged 3-DOF design**: pass / fail / partial / not measured / needs the user. The best design is the 3-DOF design whose
scorecard passes the most requirements, ties broken by R1. Each card also gives the value, the threshold, the judge,
and the best value any 3-DOF design reached under the current judging rules. A note marks a requirement whose judging
rule changed.

### Log

Events, newest first, with a filter by kind: records, milestones, judged designs, measurement changes, infrastructure.
Below them, cumulative GPU spend at each logged cost audit.

## Metric definitions

- **gap** (concept bench, lower is better, 0 = every bench target met):
  `gap = 100 * (max(0, 0.90 - inband14) + max(0, 0.95 - follow) + max(0, 0.90 - reach)) + 100 * contact`.
  Bench and baseline: `tools/concept_bench.py`, `tools/concept_baseline.py`. The **3R baseline** is gap **68.93**:
  the champion 3R (r20 s1414 #4) idealised on the same bench, with reach 0.775, follow 1.000, in-band 14 0.438,
  in-band 10 0.279 and contact 0.102. It comes from `docs/concepts/rows/baseline-3r.json`, and the builder keeps
  exactly one baseline row.
- **reach**: the share of the bench's functional workspace poses the mechanism reaches.
- **follow**: the share of the clip frames it tracks, rather than being held at a limit.
- **in-band 14 / in-band 10**: the share of the covered skin that lies 2-14 mm (2-10 mm) from the metal.
- **contact**: the share of samples where metal enters the skin (it adds to the gap at 100 x).
- **claimed** = the morphology agent's own row (`docs/concepts/rows/<id>.json`). **verified** = the verifier's
  re-measured numbers (`v_*` fields; status verified / gpu / cad). **sweep best** = the best configuration in
  `docs/concepts/sweeps/<id>.json` so far (live, unreviewed).
- **Requirements** (thresholds from `judge/requirements.json`, the judge named on each board card; full text in
  REQUIREMENTS.md):

| R | Measures | Pass | Judge |
|---|---|---|---|
| R1 | covered skin 2-14 mm from the metal while following | >= 90 % | full-exo/score_design.py BAND_HI=14 |
| R1-aim | the same at 2-10 mm | >= 90 % | full-exo/score_design.py |
| R2 | deepest part penetration into the body | <= 0.5 mm | judge/body_contact.py |
| R3 | frames followed | >= 95 % | score_design.py |
| R4 | Raise-overhead clip score (14 mm band) | >= 80 % | score_design.py |
| R5 / R5-aim | shoulder-chain DOF | <= 4 / exactly 3 | design.json |
| R6 | interference between moving parts | <= 0.15 mm | judge/part_contact.py |
| R7 | every custom part one valid solid | all | judge/part_validity.py |
| R8 | custom-part mass | <= 500 g | parts_full.json |
| R9 | strength min safety factor (FEA) | >= 1.5 | judge/fea.py (CalculiX) |
| R10 | base slip, GH-centre misalignment | <= 4 mm | judge/base_mount.py + base_slip.py |
| R11 | pressure the exo adds on the cuff | <= 7.5 kPa | judge/dynamics.py -> scorecard |
| R12 | CAD standard (G2, no visible screws) | user review | zebra check + user |
| R13 | manufacturable | supplier yes | supplier DFM + quote |
| R14 | generalises to held-out motions/bodies | held-out data | data/raw held-out |
| R15 | works on real bodies | prototype | printed prototype |
| R16 | everyday workspace poses reached | >= 90 % | judge/workspace.py |
| R17 | moves freely unpowered | yes | judge/dynamics.py (MuJoCo) |

## Datasets: id -> sources -> builder function

Each dataset is an attached JSON file (an array of row objects). Time-series rows carry an ISO UTC time (`t` or `time`).

| id | Title | Sources | `tools/dash_build.py` |
|---|---|---|---|
| morphs | Concept bench morphologies | docs/concepts/catalogue.json < families.json < rows/*.json, + best sweep config per id from sweeps/*.json, + the complexity count of each row's `mechanism` record (tools/simplicity.py `score()`): `complexity` (points, lower = simpler, 0 = three pins on bearing pairs and three links; null without a record), `complexity_items` (where the points come from, "item = points; ...", a NOT BUILDABLE flag first), `passive_trans` (passive translations; > 2 = not buildable), `mechanism_confidence` (the record's own: counted / estimated). Never part of the gap or the score | `morphs()`, `complexity_of()` |
| sweeps | Concept bench sweeps | docs/concepts/sweeps/*.json (each configuration's `t`), with per-morphology `best_gap`, overall `record_gap`, `is_record` and `passed_over` (see Times and rules); a file gap >= 999 is the agent's failed-configuration marker (no gap) | `sweeps()` |
| cad | Built CAD judge results | tools/judged_history.py (score.json, score_14mm.json, judge/workspace.json, part_contact.json, dynamics.json) + judge/scorecard.json; thresholds judge/requirements.json | `cad()` |
| gpu_evals | GPU evaluator detail runs | pipeline/conformal/gpu_client/band_eval_*.json via `judged_history.py --evals` | `gpu_evals()` |
| gpu_searches | GPU band searches | pipeline/conformal/gpu_client/band_search_*.json | `gpu_searches()` |
| reqs | Requirement board | judge/scorecard.json files (3-DOF), judge/requirements.json, `cad` | `reqs()` |
| events | Event log | docs/concepts/events.jsonl + judged designs (first judge time) + built-CAD R1 records | `events()` |
| spend | GPU spend log | docs/RUNPOD_COSTS.md audit rows (the 'balance before -> after' column; a single balance is an audit with no spend) | `spend()` |
| cov3d | Arm reach in 3-D | tools/coverage3d.py (judge/workspace.json), newest 8 designs | `cov3d()` |
| motion | Motion previews | docs/concepts/viz/thumbs.mjs (node) from the concept kinematics (kin.js + concepts/*.js): one row per concept `{id, kind: "mechanism", n, still, view, closes, body: "", mech, joint, note: ""}`, one shared row `{id: "_shoulder", kind: "shoulder", body}`, and a row `{kind: "skipped", note: <reason>}` keyed by the file name for a module that threw, registered nothing or registered an id other than its file name; `mech` / `joint` / `body` hold one SVG path per frame, frames separated by `\|`, `=` = the same as the frame before | `motion()`: re-runs thumbs.mjs (niced, 5-15 s) when motion.json is missing, older than kin.js / thumbs.mjs / any concepts/*.js (thumbs.mjs stamps the file with the newest mtime of its sources, each stat'ed before it is read, so a concept saved after thumbs.mjs read it is newer), has no row for a concept file, or has a row whose file is gone (rows are keyed by file name; a file registering another id gets a skipped row, so this does not re-run on every build); otherwise takes the file as written (bytes unchanged, so no re-upload). Skipped modules are warned about on every build (meta) |
| meta | Data build info | the build itself (built_at, commit, warnings) | `main()` |

Calculations the page defines (`dash.calc`; their formulas are visible in the dashboard's Sources):

- `summary`: the headline numbers.
- `funnel`: the stage counts.
- `cad_record`: the steps of the built-CAD R1 record, one record per judging-rule epoch (`rules` older / current): values judged before a rule change are never compared with current ones, so the Leader chart draws the older record dashed grey and the current one in the accent colour; the CAD tab's small multiples do the same.
- `cov3d_share`: the share of poses reached per design.

Times:

- Sweep configurations and events carry the time their agent wrote.
- A judged design's time is the earliest of: the commit that added its score.json, the file's mtime, and the first
  commit whose docs (docs/*.md, README.md) name the design id. Score files are often committed hours later in a
  batch (7c94de2 at 13:33 carried builds reported in the docs from 05:52 on); the docs mention bounds the judge time.
- Passed-over configurations: a sweep configuration measured before its morphology's claimed row (rows/<id>.json,
  `t_screened`) and better than the claim was seen and rejected by its agent. It stays in `sweeps` with
  `passed_over: true`, drawn as a hollow ring, and counts for no best and no record. Two real cases: the 80
  seed-offset-3r-slides configurations scored under a jam-contact metric hole (best 49.15 vs the claimed 57.95), and
  the seed-arc-rails rev-1 entries whose links were not joined to the rails (46.67, "which was wrong").
- A value found only in a scorecard takes the scorecard's last commit, or its mtime while uncommitted.
- GPU files take the commit that added them: a batch committed together shares one time. Each dataset's description
  says so.

## Refresh procedure and cadence

1. `python3 tools/dash_build.py` (about 6 s). It rewrites `docs/dashboard/data/*.json` and `docs/dashboard/manifest.json`
   and prints `CHANGED` beside each dataset whose sha256 differs from the last manifest. The output is deterministic
   (rows sorted, no timestamps except `meta.built_at`), so an unchanged source gives an unchanged file.
2. The lead uploads only the changed files as assets of the artifact. For each one it updates
   `datasets/<id>` with `source.url` (the upload's `/_blob/...` url), `source.name` and `updated: {at, by}`. It uses
   the manifest's title and description for a new dataset. `meta` changes on every build, which is how the header
   knows how fresh the data is.
3. Page changes: write `files/<name>` = `{text}` for each changed page file (index.html first).

Cadence: rebuild and upload after every result (a new sweep best, a verifier verdict, a judged design) and at least
every 15 min while the swarm runs (the lead's watchdog). The header turns amber when the data is over 30 min old.

## Public copy for viewers who are not signed in (2026-10-16)

The production dashboard is an Artifact made from the Dashboard type: its page and data live in the artifact's own
store, and a viewer who is not signed in to claude.ai may not be able to load it even when it is shared with anyone
with the link (user report 2026-10-16). The public copy, https://claude.ai/artifact/5dan8agUow4XR81Pr91XhF, is a plain
page with no store and no capabilities: `tools/dash_public.py` wraps the same page (docs/dashboard/simple/index.html) in
a small stand-in for the type's `dash` API (data / calc / onData / colors), writes out the type's theme tokens (light
and dark), loads d3 7.9.0 from cdnjs, and fetches the same dataset files (docs/dashboard/data/<id>.json) published
beside it as data/<id>.json. The refresh (scratchpad dash_refresh2.sh) prints a PUBLIC line with the files that
changed; republish docs/dashboard/public/index.html with those files, then mark them published
(`tools/dash_public.py <state.json> --mark`).

## Local harness

```
python3 tools/dash_build.py
node docs/dashboard/harness/shot.mjs <out dir> [--widths 1280,400] [--themes light,dark] [--tabs leader,bench,cad,reqs,log] [--status loading|error]
python3 docs/dashboard/harness/serve.py --port 8765   # then open http://127.0.0.1:8765/#bench
```

`serve.py` serves the type's own host page, `app.js` and `app.css`, reading them at run time from the type's files.
These are never copied into git; set `DASH_RUNTIME=<dir with index.html and artifact-type/>`. It adds one script, a
stand-in for the platform's `window.claude` (a Firestore-like `db` holding `dash/meta`, `datasets/<id>` and
`files/<name>`, plus `user`). It also serves each dataset at `/_blob/<hash>`. The page therefore runs in the real
runtime exactly as published: script loading, `dash.data`/`onData`/`calc`, marks, the toolbar and themes.

`shot.mjs` screenshots each tab and prints, per shot, the console and page errors and any horizontal overflow.
`--status loading|error` makes every dataset hang or fail, so the designed loading and error states can be checked.
The only console message filtered out is the platform's serif web font. It is served from `/_runtime/` on claude.ai
and cannot load offline, so the harness renders the serif in a fallback face.

## Known limits

- Times on GPU files are commit times, not run times.
- A built design judged before its commit and never named in the docs shows its commit time (or an earlier mtime).
  Of the seven designs committed together at 13:33 UTC on Oct 15, six are dated by their first docs mention;
  cad_r16_n3_s1373_1_fair300 (built in the same pre-11:55 fair-field series) is not named in any doc and still counts
  as 'current rules' (it is the R1-aim 'best, current rules' value, 34.5 %). A judge-time field in the score files
  would end this.
- A configuration an agent rejects while still sweeping (before it files its claimed row) counts until the claim
  arrives; `rev` fields in sweep files are not read (their values are not uniform).
- The best-sweep-configuration evidence is the agent's own measurement on the fast (grid) bench. Only `v_*` values
  are verified.
- docs/FINDINGS.md tables are not parsed: they are prose tables without a stable schema. Their GPU numbers reach the
  page through the `band_eval_*` / `band_search_*` result files they cite.
- The spend log has only the audit rows written so far (the last audit is Oct 15 02:22 UTC). Spend after that is
  not shown until docs/RUNPOD_COSTS.md gets new rows.
- `morphs` maps the catalogue status `modelling-interrupted` to `ideated` (with a note), because a partial model file
  is not a modelled morphology. A morphology counts as modelled once its sweep file exists.
- The data carry ISO UTC times; the published page draws every axis, tick and event time in US Eastern time
  (America/New_York: EDT in summer, EST in winter; user, 2026-10-15: "put times in EST"), shifting each date to New
  York wall-clock time before d3's UTC scales (`et()` in the page's first script).

## The published page is the one-page summary (user, 2026-10-15: "very confusing ... needs to be very easily digestible")

The artifact now shows `docs/dashboard/simple/index.html` - one page read top to bottom: the leader in one sentence
and three numbers (best design with its simplicity, today's 3-hinge chain = the bar, the goal 0), "two ways to fail" (each design as a dot:
moves with the arm vs stays 2-14 mm from the skin, the goal corner), "score vs simplicity" (see below), the leaderboard (a tiny motion preview, score, simplicity, close-to-skin / follows /
reaches meters against their targets, status: checking / verified / sweeping / dead end) with a plain-words glossary of
the joint names, the best gap over time, the latest events and the built prototype's 19 requirements as chips. It
reads six datasets (morphs, sweeps, events, reqs, cad, motion; the calcs board / leader / reqsum are defined in the page).
The detailed multi-tab page above (docs/dashboard/*.js) stays in the repo for deeper dives; it is not published.
Refresh: the lead's watchdog runs tools/dash_build.py and uploads only the datasets the page reads (morphs, sweeps,
events, reqs, cad, motion) when their sha256 changes.

### Simplicity: the complexity count beside the score (user, 2026-10-16: "it would be cool to have a simplicity score for each design impacted by degrees of freedom moving parts, etc. I think thats a pretty major part and for now shouldn't impact overall score but should show in the chart", then "when score start capping out around 95+ over the night, prioritize lowering that simplicity number")

The number is the complexity count of docs/SIMPLICITY.md (`tools/simplicity.py`): points, **lower = simpler**, 0 = the
simplest buildable 3-DOF chain (three pins on bearing pairs, three links); every extra active DOF, passive freedom,
sensed coordinate, closed loop, slider, spring, body, joint and part adds points. It comes from each design's
`"mechanism"` record in `docs/concepts/rows/<id>.json` (written by the mechanism census), is computed by
`tools/dash_build.py` into the `morphs` fields `complexity`, `complexity_items`, `passive_trans`,
`mechanism_confidence`, and is carried by the `board` calc (and `leader`: the best design's number) unchanged. It never
enters the gap, the score, the board order or the leader choice: a design's score is the same with or without it.

- **Leaderboard column "Simplicity" (caption "lower = simpler")**: the points (one decimal, trailing zero dropped) and a
  tiny bar on a fixed 0-60 scale (to the largest count if one is above 60), muted; the tooltip (`title`) lists where the
  points come from. A design with three passive translations (not buildable, CLAUDE.md) shows its number and bar in the
  fail colour. A design without a record shows "–" ("Not counted yet").
- **"Score vs simplicity" chart** (below "Two ways to fail"): one dot per counted design, x = its bench score (scale 50-100;
  designs under 50 sit on the left edge, the tick reads "≤50"), y = its points. The strip right of the dashed score-95
  line is shaded: the goal is the bottom-right corner (score 95+, fewest points), where per the user simplicity becomes
  the next objective. Dot colours as in "Two ways to fail" (verified, live, dead/refuted muted, the bar to beat in the
  text colour); an x marks a not-buildable design. The bar to beat and the five best live designs (three below 480 px)
  are labelled, placed beside their dot without overlap (a tick joins a label moved off its dot's line). Hover: name,
  score, state, points and items. The note under it counts the designs counted so far.
- **Narrow screens**: the board was already full between 640 and 760 px. Below 860 px the board's meters shorten to
  36 px, the simplicity bar goes (the number stays), its caption wraps and a two-word status pill wraps. Below 520 px
  close-to-skin is hidden like follows / reaches below 640 px: on a phone the board keeps score and simplicity, the two
  numbers that do not follow from each other, and all three score parts stay in the "Two ways to fail" chart. Measured
  (the table's scrollWidth vs its box): 400 px 334/334, 521 445/445, 641 559/559, 1280 1066/1066 (before: 400 px 324/334;
  360 px overflowed by 27 px before and by 23 now, inside the table's own scroller).
- Test (2026-10-16): the harness as below, 1280 and 400 px, light and dark: zero console / page errors, no page overflow.

### Motion previews in the leaderboard (user, 2026-10-15: "small next to each design on the leaderboard just a tiny preview of motion not the whole human needed, just the shoulder maybe and no color or anything flashy")

The leaderboard's first column is a 56 px (44 px at <= 520 px width) animated line drawing per design, from the
`motion` dataset (its `<th>` is marked `data-source="motion" data-field="mech"`; the table's row key `id` joins it, so
each cell cites that design's row; a design with no concept module gets an empty, unmarked cell).

Tap / click a preview (or focus it and press Enter) to enlarge it (user, 2026-10-16: "pressing on a preview should
enlarge it so its easier to see"): a `<dialog>` with the same animation at up to 526 px, the design's name, score, reach,
follow, close-to-skin, simplicity and status; Esc, the x button or a tap on the backdrop closes it. The shared preview
timer animates it; a board redraw keeps it animating.

- What is drawn (docs/concepts/viz/thumbs.mjs): each concept runs as the gallery runs it (KIN.run over KIN.motion(240),
  the IK warm-started frame to frame), over two laps so the warm start carries across the loop's wrap (lap 2 is drawn;
  seed-offset-3r-slides drifted onto another IK branch during lap 1 and jumped back at every repeat). The loop (rest ->
  forward raise -> overhead -> abduction -> across the body -> hand behind the back -> rest) is sampled at 60 frames
  spaced by equal TRAVEL, not equal time: KIN.motion holds at each key pose and moves fast in between, so equal-time
  frames jumped up to half the thumbnail in one tick (round-1 review: 46 units of 100 on abduction -> across). Each key
  pose is shown twice (one short hold); the frames between two keys spread evenly over the distance moved, per loop step
  the larger of the upper arm's (its end 200 mm down and four points 40 mm around it, 160 mm down) and the mechanisms'
  (the 90th percentile over all concepts of the largest move of any hub / link end / carriage: near overhead ->
  abduction a spherical 3R swings its hubs ~2.5x as far as the arm end, and with arm travel alone 6 leaderboard rows
  jumped > 15 units in the same tick, round-2 review); a frame between two loop frames is solved there, warm-started
  from the loop frame before. Measured on screen (2026-10-16, 30 leaderboard rows): the arm moves at most 10.2 units of
  100 per tick; the largest part move per tick is 10.7 units for the median row (round 2, 56 frames by arm travel
  alone: 14.6), 8 rows exceed 15 units once (round 2: 14, 6 of them in the same tick) and no tick has more than 2. What still jumps is in the concepts' own IK (`--stats` lists part moves > 15 units
  and > 2.5x the arm's): clavicular-front-route (J2 at its fold, 31 units), crossed-skin-tracks (a branch flip and back),
  seed-spm-3rrr, rail-elbow. ONE
  orthographic camera for every design: from the front-right (45 deg between anterior and lateral) and 12 deg above,
  direction (1, 0.3, 1) in the rig frame, so the overhead arm points up the thumbnail (77 % of its length on screen; the
  round-1 camera from 30 deg above showed 48 % and overhead read as a ring over a circle), forward raise and abduction
  72 % each. The frame is 436 mm wide around a point 25 mm right / 12 mm below GH on screen, fitted so every
  leaderboard design (30 on 2026-10-16) stays inside the frame in every frame, about a unit from the edge at the closest;
  offset-axis-skin-hubs (its cuff stage reaches 224 mm down the arm) spans the full height and sets the size. Three
  concepts not on the leaderboard (septum-barrel-arm-link, cuff-sleeve-3r, armband-pointer) are clipped at the arm end
  in some poses (`node docs/concepts/viz/thumbs.mjs --stats --out <scratch file>` prints the counts and the closest
  approach to the edge per concept).
- Layers, monochrome: the shoulder (faint, `--color-fg-muted` at 55 % opacity, 85 % on the dark theme, 1 px): deltoid
  circle, the upper arm clipped 200 mm down the arm, a shoulder line to the neck that drops with `ctx.lift`; the
  mechanism (`--color-fg`, 1.2 px): links, arcs, rails, the cuff and rings as ellipses, plate / carriage outlines;
  joints (`--color-fg`, 2.4 px round caps, 2.1 px in the 44 px cells; 3 px tied the compact designs into knots): hubs
  as short bars along their axis (a dot when the axis faces the camera), slider blocks, telescope splits, and the
  rolling-contact axes of rolling cones / fins (a link named "contact ...": the moving joint line, not metal). Hubs
  wider than 18 mm (sleeves around the arm) are drawn as their ring. Not drawn: point markers and construction geometry
  (a part named "construction line", "not metal" or "trace", or a link / arc / rail of radius under 0.75 mm:
  skin-normal-hubs-selfaligning's three hub-axis lines, coupler-path-j1's trace). Parts whose points are not finite are
  left out (the gallery hides them too). Roles are not distinguished. Frames where a concept's chain does not close
  (`closes` = 0) are drawn like the others; the gallery flags them.
- Size: integers in a 0..100 viewBox, relative path commands, Ramer-Douglas-Peucker at 0.45 units measured to the
  SEGMENT between a run's ends (a ring is an open chain whose ends are neighbours on the circle: measured to the
  infinite line through them, an edge-on cuff collapsed to a 3-unit dash at the behind-the-back pose in 69 of 74
  concepts, round-2 review; thumbs.mjs warns when any part comes out under half its projected size, `--stats` prints
  the census), `=` for a frame identical to the one before; ~16 KB per concept, 1.18 MB for 74 concepts on 2026-10-16
  (the dataset limit is 8 MB).
- Rows are keyed by the concept FILE name: a file that registers an id other than its name (or an id another file
  registers too), registers nothing or throws gets a `skipped` row with the reason in `note`, so tools/dash_build.py
  sees files and rows agree and does not re-run on every build; it warns about skipped rows on every build.
- Page: one shared timer at ~10 frames/s (5600 ms / n per frame, so the loop takes ~5.6 s) animates only the
  thumbnails on screen (IntersectionObserver) and stops while none is visible or the tab is hidden;
  `prefers-reduced-motion: reduce` shows one still frame (`still`: the arm on its way up to overhead, where arm and cuff
  are both clear of the shoulder), not moving. Every thumbnail shows the same arm pose at the same moment. While the
  dataset loads or fails, or for a design without a preview, the cells stay empty. The parsed frames are memoised on a
  fingerprint of the rows (the runtime calls onData ~11 times on a load with a new array each time: 1 parse). The
  sections below the leaderboard (progress, events, requirements and the detail charts, ~46k SVG dots) carry
  `content-visibility: auto`: off-screen they are not rendered, so a tick repaints only what is on screen. Chrome trace
  of the renderer main thread, 5 s with the board in view on the loaded 4-core box: 438-539 ms (round 2, every chart in
  each paint: 1191-1349 ms, Layerize + PaintArtifactCompositor::Update ~570 ms of it; reduced motion: 0). Chart
  tooltips flip above / left of the pointer near the chart's edge, because the section clips at its card.
- Test: the local harness with the type's runtime (serve.py) serving this page as `index.html` (a scratch folder with
  `harness/serve.py`, `index.html` -> docs/dashboard/simple/index.html, `manifest.json` and `data/`), screenshots at 1280
  and 400 px, light and dark, a 3x crop and a frame sequence; zero console/page errors and no runs document (nothing
  flagged; a deliberately wrong `data-field` is flagged, so the check is live).
