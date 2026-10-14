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
| What, other than the designer, shows it's right? | [`judge/`](judge/) - geometry judges + scorecard; ultimately a printed prototype on real bodies (R15) |
| What has been learned so far? | [`docs/FINDINGS.md`](docs/FINDINGS.md) |
| How do I run it? | [`docs/PIPELINE.md`](docs/PIPELINE.md), [`CLAUDE.md`](CLAUDE.md) for agents |

## Status (2026-10-14)

Reference design: **`cad_r13_n4_s1343_1`**, 4 revolute joints, base on top/back of the shoulder, v4 encoder joints,
swept-band Ti links, BOTTOM + neck + J4 hub as one 7075 part, conformal AlSi10Mg saddle cuff on the upper arm.
Scorecard: [`pipeline/full-exo/designs/cad_r13_n4_s1343_1/judge/scorecard.md`](pipeline/full-exo/designs/cad_r13_n4_s1343_1/judge/scorecard.md).

What it means in one paragraph: the CAD is collision-free and buildable-looking, but the design only covers about a
third of the goal (honest score ~30 %, overhead far from usable), and three things outrank more polishing - the base is
modelled as riding the scapula although it bolts to a thorax back plate (R10, the likely reason overhead is so hard),
the human model has measurable artifacts (R14 / P2), and nothing has been checked by an independent solver, a supplier
or a real body yet (R9, R13, R15). **Next: phase P0** in docs/PLAN.md.

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
