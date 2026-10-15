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

## Status (2026-10-15, morning)

**Final design of the night, built and rendered: `cad_r18_n3_s1392_1_f300`** - a 3-joint chain (the user's 3-DOF
minimum) from the range-first GPU search r18, full fair CAD with smooth fair-field links (FAIR_LAM 300), the scapula
base on the user's handler, unpowered (MVP1, rolling bearings). Scorecard:
[pipeline/full-exo/designs/cad_r18_n3_s1392_1_f300/judge/scorecard.md](pipeline/full-exo/designs/cad_r18_n3_s1392_1_f300/judge/scorecard.md);
film and stills: [renders/2026-10-15_final_3R/](renders/2026-10-15_final_3R/).

- Moves freely unpowered (R17), 3 DOF (R5), every part one valid solid (R7), 234 g of custom parts (R8).
- Follows 80 % of motion frames (R3); Raise overhead to 138 deg of elevation (scapular plane), then holds; Comb hair,
  Drink, Reach a high shelf, Wash opposite shoulder and Walking 100 %; Reach back pocket 22 %, Wave 40 %.
- Proximity is the big gap: 41 % of the covered skin within 14 mm (R1, target 90 %), 19 % within 10 mm.
- No design reaches the 90 % range target: the best compact designs cover 65-75 % of the functional workspace in the
  evaluator, the built CAD 47 % (R16; link 2 meets the arm-end neck in half the poses outside the clips).

What the night established (docs/FINDINGS.md): range first makes the search hold joints off the skin (stand-off
designs, now flagged by the builder); joint size is worth ~20 points of workspace (O17 vs the O23 the CAD builds);
the fair CAD's links ride 3-7 mm above the fitted shape (fair-field links recover part of it). Next levers: a smaller
joint stack (needle bearings, O17 hub), the neck clearance over the whole workspace, links that follow the fitted
shape.

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
