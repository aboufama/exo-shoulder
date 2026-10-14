# EXO shoulder

A shoulder exoskeleton whose whole mechanism rides **within ~1 cm of the skin** over the full range of motion
(overhead most of all), never touches the skin, has **at most 4 degrees of freedom**, and is built to the user's CAD
standard. Elbow, forearm link and forearm cuff are the user's existing design (`data/user_cad/`).

This repo is organised the way a field-leading wearable-robotics engineer would run the problem, not around the
scripts that happened to get written:

| question | where |
|---|---|
| What exactly must be true, as numbers? | [`REQUIREMENTS.md`](REQUIREMENTS.md) - R1-R15, each with a pass/fail threshold |
| What would an expert do that the brief doesn't ask for, from what raw material, with which tools? | [`docs/PLAN.md`](docs/PLAN.md) - the depth reframing and phases P0-P6 |
| How do we work? | [`docs/METHOD.md`](docs/METHOD.md) - altitude, depth, range (Felix Rieseberg's essay, applied) |
| What, other than the designer, shows it's right? | [`judge/`](judge/) - geometry judges + scorecard; ultimately a printed prototype on real bodies (R15) |
| What has been learned so far? | [`docs/FINDINGS.md`](docs/FINDINGS.md) |
| How do I run it? | [`docs/PIPELINE.md`](docs/PIPELINE.md), [`CLAUDE.md`](CLAUDE.md) for agents |

## Status (2026-10-14, evening)

Reference design: **`cad_r13_n4_s1343_1`** (4R, all axes through the GH centre). Full scorecard, first complete judge
run (R2, R6, R10 measured for the first time): 3 of 15 pass - R1 45.9 %, R2 24.4 mm, R3 64.5 %, R4 18.8 %, R6 18.5 mm,
**R10 25.3 mm** ([scorecard](pipeline/full-exo/designs/cad_r13_n4_s1343_1/judge/scorecard.md)).

**P0 answered the base question ([docs/P0_BASE_MOUNT.md](docs/P0_BASE_MOUNT.md)):** the base bolts to a thorax plate
but every design assumed it rides the scapula. On a thorax plate the reference base enters the body by 44 mm, and no
chain whose axes meet at one thorax-fixed point can hold the 2-10 mm band (>= 12.7 mm on the rig law). Offset axes help
on the rig law (3-DOF: 5.8 / 6.8 mm), but published girdle motion is 2-3x the rig's and 3-D
([docs/research/gh_translation_literature.md](docs/research/gh_translation_literature.md)): any rigid thorax-plate chain
within the cap misaligns >= 11-26 mm, plus +-7-12 mm that no arm-angle function follows; the red team
([pipeline/redteam/REPORT.md](pipeline/redteam/REPORT.md)) finds the same over the whole workspace and for a shrug.
**Waiting on the user:** base option A (3 DOF on a girdle-riding base) / B (thorax plate + passive girdle, 5 DOF) /
C (thorax plate + 3 rigid DOF, only if the user's girdle moves like the rig - the 1-minute ruler test in
[data/raw/README.md](data/raw/README.md) decides). Then P3 ([docs/P3_SEARCH_PLAN.md](docs/P3_SEARCH_PLAN.md)) with
L1 keep-out CAD (CAD_STANDARD.md scope) and the held-out split in `data/raw/split.json`.

## Quickstart

```bash
bash tools/setup.sh                                   # python deps (cadquery 2.5 / OCP 7.7, trimesh, scipy, torch)
bash tools/judge_all.sh cad_r13_n4_s1343_1 fast       # every judge + the scorecard for the reference design
cd pipeline/full-exo && python3 -m http.server 4198   # index.html?d=cad_r13_n4_s1343_1 (motion), parts.html (each part, zebra)
```

Rebuilding CAD, searching new kinematics and rendering: docs/PIPELINE.md. GPU search and renders run on RunPod
(`RUNPOD_API_KEY` in the environment; state cost before running).

## Layout

```
REQUIREMENTS.md   numbered requirements, thresholds, judges
docs/             PLAN (depth reframing, phases), FINDINGS, CAD_STANDARD, HARDWARE, PIPELINE
judge/            body_contact, part_contact, part_validity, scorecard, requirements.json
data/user_cad/    the user's STEP (source of truth, read-only except BOTTOM)
data/raw/         protocol for the raw inputs still to collect (scans, OpenCap, OpenSim, AMASS/SMPL-X)
tools/            setup, map cache, publish, judge_all
pipeline/         the working code: human rig (avg, arm-rom), scorer + viewers (full-exo), search + CAD + FEA
                  (conformal), G2 helpers (shoulder-d4), renders (joint-render)
```

History before this restructure: github.com/aboufama/exo-arm (archive).
