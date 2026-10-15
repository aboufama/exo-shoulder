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
| morphs | Concept bench morphologies | docs/concepts/catalogue.json < families.json < rows/*.json, + best sweep config per id from sweeps/*.json | `morphs()` |
| sweeps | Concept bench sweeps | docs/concepts/sweeps/*.json (each configuration's `t`), with per-morphology `best_gap`, overall `record_gap`, `is_record` and `passed_over` (see Times and rules); a file gap >= 999 is the agent's failed-configuration marker (no gap) | `sweeps()` |
| cad | Built CAD judge results | tools/judged_history.py (score.json, score_14mm.json, judge/workspace.json, part_contact.json, dynamics.json) + judge/scorecard.json; thresholds judge/requirements.json | `cad()` |
| gpu_evals | GPU evaluator detail runs | pipeline/conformal/gpu_client/band_eval_*.json via `judged_history.py --evals` | `gpu_evals()` |
| gpu_searches | GPU band searches | pipeline/conformal/gpu_client/band_search_*.json | `gpu_searches()` |
| reqs | Requirement board | judge/scorecard.json files (3-DOF), judge/requirements.json, `cad` | `reqs()` |
| events | Event log | docs/concepts/events.jsonl + judged designs (first judge time) + built-CAD R1 records | `events()` |
| spend | GPU spend log | docs/RUNPOD_COSTS.md audit rows (the 'balance before -> after' column; a single balance is an audit with no spend) | `spend()` |
| cov3d | Arm reach in 3-D | tools/coverage3d.py (judge/workspace.json), newest 8 designs | `cov3d()` |
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
- The time axis is UTC throughout.
