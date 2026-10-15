# Render runbook: picked design(s) -> fair CAD -> judges -> free preview -> Blender (paid)

For the user's request of 2026-10-15 ("create a design from the best configuration (or a select few) and render them in
blender, should be done by 8:30am" = **12:30 UTC**). Dry run on `cad_r16_n3_s1373_1` (r16 seed 1373 rank 1, pure 3R,
no sliding cuff), 05:19-06:xx UTC; every timing below was measured in that run on this 4-core machine with the lead's
judges and the r17 search client running beside it (OMP_NUM_THREADS=2). Rules that apply (CLAUDE.md): cost + GPU type
stated and a yes before any paid job; a cheap motion preview approved before any paid render; workersMin back to 0
after; never print the key; never touch `crl-*` pods.

## 0. What each picked design needs first

- A **DETAIL** band_eval result (`band_eval` job with `detail: 1`) **on a payload whose first 451 poses are
  `band_poses.b64`'s 8 clips**: `band_poses_ws.b64` (what r16diag used) or `band_poses_wsf.b64`. The r17 search runs
  on `band_poses_fit_wsf20.b64` (6 fit clips, no Wave / Walking, indices shifted): its results cannot go into the CAD
  pipeline directly - re-evaluate the picks with DETAIL on `band_poses_ws.b64` (one GPU job; the r16diag job with 4
  designs took 612 s on a 24 GB MIG slice = ~$0.12). `make_input.py` below refuses a wrong payload.
- The job's `ramp_deg` (r17: 60) and `hw` if the job set one (r17 did not). `t_link` / `hub_r` / `stack` are in the result.
- `.cache/maps_s1.pt` (present; `tools/build_maps.py` otherwise).

## 1. Build the CAD (per design, ~3 min; two designs in parallel at most)

```bash
cd /home/user/exo-shoulder/pipeline/conformal/band_cad
python3 make_input.py ../gpu_client/<detail eval>.json <index> <key> --ramp-deg 60 --poses band_poses_ws.b64   # 1 s
cd /home/user/exo-shoulder
export OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 SKIP_SCORE=1
export ARM_SRC=$PWD/pipeline/full-exo/designs/cad_r13_n4_s1343_1/exo.glb ARM_SKIP="BOTTOM + neck,UPPER ARM CUFF,(upper cuff)"   # band_<key> proxy only
bash pipeline/conformal/fair_cad/fair_pipeline.sh <key> "<label>"        # writes designs/band_<key>/ and designs/cad_<key>/
bash tools/publish_design.sh <key>                                        # step/, parts_full.json, parts/ (76 s)
```

Key naming: `r17_n3_s<seed>_<rank>` (the lead's band designs are `band_r16_3r_...`; the CAD gets `cad_<key>`).
What to check in the output (dry-run values in brackets):

| stage | time | look for |
|---|---|---|
| band_to_design + make_cad_design | 3 s | no `WARNING band_to_design` / `REFUSED` (short link guard) |
| replan + members + verify (loop) | 52 s | `hard collisions in 0 of ...`, `valid members: 3`, `members clean after round 1` |
| `out_<key>/members_1.log` | - | `raised joint faces` of a few mm at most (a three-digit raise = bad skin map, see 5) |
| assemble | 77 s | `out_<key>/assemble.log`: every `featured valid True`, `BOTTOM merged valid True` with one solid |
| verify_armend | 5 s | `frames with any link/arm-end collision: 0` |
| publish_design.sh | 76 s | `parts.html ready` |

`fair_pipeline.sh` also writes `design.json` (R5 / R10 / R17 read it) and a `workspace.json` with the CAD's fixed base
frame (R16), both via `make_cad_design.py`. Without `SKIP_SCORE=1` it ends with an 8-min `score_design` run that
`judge_all.sh` repeats.

## 2. Judge (per design)

```bash
OMP_NUM_THREADS=2 bash tools/judge_all.sh cad_<key> fast    # JUDGE_TIME; scorecard -> designs/cad_<key>/judge/scorecard.md
```

## 3. Free motion preview (show it, get the go-ahead for the paid render)

```bash
cd /home/user/exo-shoulder/pipeline/full-exo
(python3 -m http.server 4199 >/dev/null 2>&1 &)
CLIPS="Raise overhead,Reach back pocket" FILM_OUT=designs/cad_<key>/film_preview.json \
  python3 film_plan.py "cad_<key>:<label>:<subtitle>" [ "cad_<key2>:...:..." ]      # 1 s; several designs swap mid-clip
cd /home/user/exo-shoulder
NODE_PATH=$(npm root -g) node tools/preview_film.mjs designs/cad_<key>/film_preview.json pipeline/full-exo/designs/cad_<key>/preview --every 0      # 12 stills, 30 s
NODE_PATH=$(npm root -g) node tools/preview_film.mjs designs/cad_<key>/film_preview.json pipeline/full-exo/designs/cad_<key>/preview --frames none --every 2 --w 960 --h 540   # MP4, MP4_TIME
```

`film.html` plays the same plan with the film's camera, a matte-black headless mannequin and the part materials
(the Blender film has a smooth faceless head instead). Chromium uses software WebGL (SwiftShader, ~2 cores). The
viewer is also live at `http://localhost:4199/index.html?d=cad_<key>` and `film.html?film=designs/cad_<key>/film_preview.json`.

## 4. Paid render on `exo-blender-cycles` (only after the yes)

Endpoint (audit 05:26 UTC, `python3 tools/runpod_guard.py audit`): id `dj3qfmtwrwy2pr`, Flash pool **ADA_24 = RTX 4090
24 GB**, workersMin 0, workersMax 4, idle 30 s, executionTimeoutMs 0 (no server-side kill: watch the jobs). Rate
(docs/RUNPOD_COSTS.md, published flex): **$0.00031/s = $1.12/h per worker**. Blender 4.2.3 is downloaded once per cold
worker. The repo holds **no measured render timings** (no logs); the per-frame numbers below are estimates for Cycles
OptiX on a 4090 at 1920x1080 - calibrate with the first chunk (`--only 1`) before the full film.

Film (mannequin + exo, the user's look: `render_film.py`):
```bash
cd /home/user/exo-shoulder/pipeline/full-exo
python3 film_plan.py "cad_<key>:<label>:<sub>" [...]          # -> designs/film.json (default clips: Raise overhead, Comb hair, Reach a high shelf, Wave)
FILM_RENDER=film_render/<name> GRID=0.4 python3 film_frames.py 12   # 71 s for 326 frames (dry run); chunks of 12 frames
cd ../joint-render
RUNPOD_API_KEY=$(cat ~/.runpod_key) ~/.local/share/uv/tools/runpod-flash/bin/python film_client.py film ../full-exo/film_render/<name> ../full-exo/film_render/<name>.mp4 --spp 128 --only 1   # calibration chunk
RUNPOD_API_KEY=$(cat ~/.runpod_key) ~/.local/share/uv/tools/runpod-flash/bin/python film_client.py film ../full-exo/film_render/<name> ../full-exo/film_render/<name>.mp4 --spp 128           # the rest (done chunks are skipped)
python3 /home/user/exo-shoulder/tools/runpod_guard.py enforce && python3 /home/user/exo-shoulder/tools/runpod_guard.py audit   # workersMin -> 0
```
Stills (exo only, three cameras on the shoulder, `render_stills.py`):
```bash
cd /home/user/exo-shoulder/pipeline/full-exo
python3 stills_plan.py designs/cad_<key> "Raise overhead" 0.45 ../joint-render/out_stills_cad_<key>/raise    # 1.4 s
cd ../joint-render
RUNPOD_API_KEY=$(cat ~/.runpod_key) ~/.local/share/uv/tools/runpod-flash/bin/python film_client.py stills out_stills_cad_<key>/raise/scene.glb out_stills_cad_<key>/raise/motion.json out_stills_cad_<key>/raise --spp 256
```

**Payload limit.** Each film job carries the whole designs GLB plus its chunk's mannequin (gzip + base64): 3.3 MB per
design at GRID 0.25 (2.1 MB at GRID 0.4) + 3.4 MB per 12-frame chunk = **6.7 MB for one design**; RunPod's `/run`
takes 10 MB. Two designs: GRID=0.4 (7.6 MB); three: GRID=0.4 and `film_frames.py 8` (8.6 MB). Stills: 2.6 MB.

**Cost and time** (estimate: 5-8 s per film frame and 12-15 s per 256-spp still on a 4090 incl. scene update; ~15 s
job setup; ~60 s cold start per worker; 4 workers):

| render | frames | GPU-s | cost | wall clock |
|---|---|---|---|---|
| calibration chunk | 12 | ~150 | ~$0.05 | ~3 min |
| preview plan (Raise overhead + Reach back pocket) | 326 | 2,100-3,100 | $0.65-0.95 | 10-14 min |
| default plan (4 clips), any number of designs | 712 | 4,400-6,300 | $1.35-1.95 | 20-28 min |
| stills, 3 cameras, one design | 3 | ~110 | ~$0.03-0.05 | ~2 min |
| worst case (15 s/frame), default plan | 712 | ~11,600 | ~$3.60 | ~50 min |

Order for the 12:30 deadline: picks at 08:00 -> detail re-eval (lead, GPU) -> build + publish (~5 min/design) ->
judges -> preview (~3 min) -> yes -> calibration chunk -> film + stills (~30 min) -> enforce/audit.

## 5. What broke in the dry run and how it was fixed

DRYRUN_NOTES
