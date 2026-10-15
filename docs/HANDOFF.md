# Handoff - 2026-10-15 ~16:00 UTC (read this first, after CLAUDE.md)

The previous session (account ab3233) stopped because the user's weekly Claude limit was hit mid-swarm. Nothing is
running now: no agents, no workflows, no local jobs, no paid GPU work. Everything that existed is committed on branch
`claude/exo-shoulder-mechanism-wy35fx`. This file is the full state; CLAUDE.md holds the rules and the user's decisions
(read its "Ambition rules" and "Never idle" sections - they are the user's explicit instructions from today).

## 1. What the user wants right now (their words, 2026-10-15)

- **3 ACTIVE DOF only** ("lets focus on 3dof ... don't even worry about 4"). Passive arm-driven elements (a cuff slide
  set by the chain's closure) do not count; an undriven spare coordinate that sags unpowered is not allowed (R17).
- **A wide tree of unique morphologies**, each screened quickly, instead of tuning one family: "after a pretty specific
  morphology is picked, its hard to optimize too much within the type, and we'd benefit more from more unique
  morphologies". Massive agent swarms; each agent gets a quick result for its morphology (CPU bench, GPU only if it
  helps). Winners -> short GPU sweep per subtype -> L1 CAD -> outside judges.
- **Speed**: "the goal of this project is to iterate as quick as possible ... don't ever waste time like this again".
  Never idle, never wait on infrastructure that can be built in parallel (CLAUDE.md).
- **Chat: big updates only** (a new leader, a requirement newly passing, a blocker).
- **RunPod only when cheap and a big speed-up.**
- **Dashboard**: blank-slate redesign so "its obvious when winners show up", keep "optimization over time" graphs,
  updated more often (section 6).
- Felix Rieseberg's essay is the method (docs/METHOD.md, CLAUDE.md "Ambition rules").

## 2. Numbers that stand

| What | Value | Where |
|---|---|---|
| Best judged CAD, 3R strap links + joint v5 (cad_r20_n3_s1414_4) | R1 35.0 % (2-14 mm), R1-aim 17.5 %, R3 follow 98.2 % | .cache logs lost; score in pipeline/full-exo/designs/cad_r20_n3_s1414_4/score_14mm.json |
| Rendered 3R final (cad_r18_n3_s1392_1_f300) | full scorecard | pipeline/full-exo/designs/cad_r18_n3_s1392_1_f300/judge/scorecard.md |
| R16 workspace (best, c1) | 78.3 % (target 90) | docs/FINDINGS.md |
| R10 base slip | 15.2 mm (target 4) - FAIL, design-independent for a spherical chain | judge/base_slip.py |
| R11 cuff pressure | PASS | judge/scorecard.py |
| **Concept-bench baseline** (the swarm's bar: the champion 3R idealised) | **gap 68.93** = reach 0.775, follow 1.000, in-band 14 0.438, in-band 10 0.279, contact 0.102 (profile p95; p100 gives reach 0.86 / in-band 0.23) | docs/concepts/rows/baseline-3r.json, tools/concept_baseline.py |

gap = 100*(max(0,.90-inband14) + max(0,.95-follow) + max(0,.90-reach)) + 100*contact, lower is better, 0 = all bench
targets met. The real limit of the 3R family is proximity: rigid links must clear the highest skin they ever pass over.

GPU searches today: r21 detail evals (no pick beats r20; the 20-deg search over-estimated workspace 0.74-0.78 vs 0.55-0.65
on 15-deg poses) - pipeline/conformal/gpu_client/band_eval_det21d*.json; r22a search (jn_low link) finished,
band_search_r22a.json, NOT yet detail-evaluated.

## 3. The morphology swarm - state and how to resume

- **Catalogue**: docs/concepts/catalogue.json - 79 entries (72 distinct, 7 marked `duplicate_of`), each with topology,
  DOF reasoning, description, why_better, main_risk, unpowered/MVP2 notes, a full `model_spec` and `sweep_params`.
  Sources: 6 lead seeds + ideation lenses serial-topology, remote-centre, closed-loop, literature, weird-compliant,
  overhead-first, biomimetic-girdle, hardware-unlocks, distributed-dof. Lenses never finished (limit hit):
  skin-data-driven, robot-wrists, body-hugging, plus the planned dedup + completeness-critic pass.
- **Status** field per entry: `modelling-interrupted` (38: a partial, UNVERIFIED model file exists in
  docs/concepts/models/<id>.py - read it before reusing, it may be half-written), `ideated` (34: nothing built yet),
  `duplicate` (7). **No morphology has a screened number yet.** The only sweep that ran (seed-rcm-parallelogram, 12
  configs, docs/concepts/sweeps/) reached best gap ~275 - far worse than the baseline.
- **Fast bench**: tools/concept_bench.py (needs `python3 -m pip install libigl`). Exact path = libigl (identical to
  judge/sdist to 1e-4 mm, ~10x faster per pose call). Grid cache path: build once with
  `nice python3 tools/concept_bench.py --build 60 160 --jobs 3` (.cache/ is git-ignored, so a new container must
  rebuild: ~15 min on an idle 4-core box, 70 min on today's overloaded one), then a 220-pose x 2000-point score takes
  ~0.5 s. Validation: p99 error 1.05 mm, max 1.94 mm in the 0-20 mm band (coarser than the 0.3 mm goal: use the grid for
  sweeps, CB_EXACT=1 for verification). Also: `B.clip_order()` for branch-continuity checks, `B.dist(i, P)` batches,
  `report()` returns gap.
- **Workflow scripts** (copies in docs/handoff/workflows/): `screen2.js` = per morphology: model + small sweep, then an
  adversarial verifier re-measures on the full bench; args `{slice, baseline_gap: 69, verify_margin: 10,
  items: [{id, name}]}` (the agent reads the spec from catalogue.json). `ideation_b.js` / `ideation_a.js` = lens
  ideation prompts; `tracks.js` = generic do + verify tracks; `merge_ideation.py` merges a workflow journal into the
  catalogue; `seeds.json` the 6 seeds; `concept_brief.md` the original brief.
- **Lessons (cost and capacity)**: each screening agent used 150-600 k tokens and the swarm of ~48 agents exhausted the
  weekly limit in ~1.5 h. On the 4-core box the swarm drove load to ~70 and memory to 13/15 GB. A workflow runs at most
  min(16, CPUs-2) agents at once (2 here), so parallelism came from many workflows. Next time: (1) first build ONE
  shared modelling kit (several ideation specs already define it as "K0-K7": circ_int/tri_ok numpy ports, branch
  continuity, skin-fitted undersides by ray-marching B.dist, O20 hub disc, strap, part-part collision, record) so each
  morphology model is ~100 lines and cheap; (2) screen in priority order with ~6-8 agents at a time; (3) run the bench
  sweeps on the cloud farm once it works or in separate cloud sessions (own CPUs).
- **Known modelling caveat**: the evaluator's N=3 "cuff" mode (rotational cuff slide around the arm) leaves the base
  joint angle as a free spare coordinate -> R17 risk (sags unpowered). A translational slide along the humerus does not.

## 4. Interrupted work tracks (files committed as WIP at handoff)

- **R9 strength (FEA)**: judge/fea.py (CalculiX + gmsh, validated earlier: judge/fea_validation.json) modified,
  judge/fea_sizing.py new, judge/scorecard.py + judge/requirements.json modified, cad_r18_n3_s1392_1_f300 scorecard
  updated. Not verified. Goal: SF >= 1.5 at ~10 N.m worst direction; wire into tools/judge_all.sh.
- **Final-standard linkage** (user: "non sloppy ... loose bearings"; 20 mm hubs allowed): pipeline/conformal/fair_cad/
  joint_v5.py and members.py modified, docs/HARDWARE.md updated, input band_cad/inputs/r20_n3_s1414_4_s10.json (a
  replan). Goal: strap links that follow the fitted shape (strap R1 35 % vs fair links ~41-58 %), preloaded bearing
  stack with no axial play, mass <= 250 g. Build with `cd pipeline/conformal/fair_cad && JOINT=v5 LINK_STYLE=strap
  HUB_DEPTH_MAX=3.65 FIELD_MODE=fair FAIR_LAM=300 SKIP_SCORE=1 ./fair_pipeline.sh ...` (must run from that directory).
- **R10 / R2 red team**: find a passive (no active DOF) way to cut the 15.2 mm base-slip misalignment to <= 4 mm; R2 on
  the user's body (BODY_FIT=user). Partial notes in docs/FINDINGS.md.
- **Cloud CPU farm** (pipeline/cloud/, tools/cloud_run.py, docs/CLOUD_RUN.md): deploy of endpoint `exo-cpu1` failed with
  "NetworkVolume undeploy is not yet supported" - the flash state file pipeline/cloud/.flash/resources.pkl records the
  volume at size 10 while farm_worker.py says 20. Fix: set the size back to 10 in farm_worker.py (the real volume stays
  20 GB) or drop the NetworkVolume entry from resources.pkl, then redeploy. Facts: RunPod worker quota is 10 across all
  endpoints (exo-blender-cycles holds 4, exo-band23 now 2); flash CPU serverless exists only in EU-RO-1 (cpu3c 2/4/8
  vCPU = $0.072/0.144/0.288 per h); use max_concurrency ~5 per worker with asyncio.to_thread; the GitHub repo is
  private, so workers get files by content-addressed upload to volume exo-farm-cas (id u9gf22x1a2, 20 GB EU-RO-1,
  ~$1.40/month); cadquery-ocp==7.7.2 must be pip-installed at runtime; FEA on a worker needs calculix-ccx + GL libs.
- **RunPod state**: balance ~$37; exo-band23 = the GPU band evaluator (code band-2026-10-15o, workersMin 0, max 2);
  every older exo-band* endpoint is at 0/0 and listed in tools/runpod_guard.py OLD; `python3 tools/runpod_guard.py
  audit` shows all. The key comes from RUNPOD_API_KEY (never print it).

## 5. Operational lessons from today (apply them)

- An interrupt of the lead stops its background Agent-tool agents; check what still runs after one.
- A SendMessage to an agent that a workflow is running started a SECOND copy of it (two farm agents collided).
  Brief agents fully up front.
- The auto-mode classifier blocks committing other agents' in-progress files and pausing (SIGSTOP) judge processes.
- A stuck RunPod endpoint (unhealthy workers, queue not moving) must be retired at once (band18, band21 today); a
  python-3.11 deploy broke band20 (the worker image is 3.12: `flash deploy --python-version 3.12`).
- The dashboard artifact is owned by the old account: a new account may not be able to edit it.

## 6. Dashboard

- Live (old design): https://claude.ai/artifact/29VvXieSTJVQsQgWaBx1mH (Dashboard type; page in the store at
  files/index.html; datasets are uploaded JSON files: builds, spend, events, history, judged, evals, cov3d).
- **Redesign (not published)**: docs/handoff/dashboard_redesign/index.html (+ part_*.js sources, shoot.sh, harness
  build/probe/shot scripts; the harness also needs d3.min.js 7.9.0 and the kit's app.css, not committed). Data comes
  from `python3 tools/dash_build.py` (datasets morphs, sweeps, judged, events, reqs, cov3d). Tabs: Swarm (leader hero,
  record over time, reach vs in-band scatter, per-morphology optimisation curves, table, funnel), Built CAD (judged
  history by DOF / CAD level, requirement board, 3-D arm coverage), Log. Round-1 review (docs/handoff/dashboard_redesign/
  builder_and_review_r1.json) found majors still open: the baseline appears twice (dash_build reads both
  rows/baseline-3r.json and families.json - dedupe on is_baseline), cov3d is a stale copy (regenerate with
  tools/coverage3d.py), time ticks pile up on a short span, the tuning chart can mislead. Fix, then publish with
  ArtifactData (dash/meta, datasets/<id> with uploaded files, files/index.html).

## 7. Next steps, in order

1. `python3 -m pip install libigl`; rebuild the bench cache; check `python3 tools/concept_baseline.py --n-clip 60 --n-ws 160`
   reproduces gap ~68.9.
2. Build the shared modelling kit (section 3), then screen the catalogue in priority order (start with the
   `modelling-interrupted` entries whose model files look complete), 6-8 agents at a time, each with a verifier.
   Write rows to docs/concepts/rows/<id>.json and sweeps to docs/concepts/sweeps/<id>.json; append events to
   docs/concepts/events.jsonl.
3. Fix the cloud farm deploy (section 4) so sweeps and judges leave the 4-core box.
4. Winners (verified gap below the baseline's): short GPU sweep per subtype (the band evaluator only knows spherical
   chains - new families need their own evaluator or CPU sweeps), then L1 keep-out CAD and tools/judge_all.sh.
5. Publish the redesigned dashboard; refresh it on every result.
6. Finish the R9 FEA, linkage and R10/R2 tracks.
