#!/bin/bash
# run every judge on one design and print the scorecard. Usage: tools/judge_all.sh <design id> [fast]
# R6 (part_contact) frames: every frame (P=1) in the full run; every 3rd in fast (P=3, 10 per second of the 30 fps clips):
# a crossing that lasts >= 3 frames (0.1 s) is always sampled. The l1_offset-skin-normal-3r first build's link 1 / link 2
# crossing lasted 9 frames (Wave 71-79, 95-103, step 1); fast used to run every 12th frame on every other vertex and saw 0.0.
set -e; cd "$(dirname "$0")/.."; ID=$1; PY=${PY:-python3}; S=2; P=1; [ "$2" == "fast" ] && S=6 && P=3
(cd pipeline/full-exo && $PY -W ignore score_design.py designs/$ID 3 | tail -1 && BAND_HI=14 $PY -W ignore score_design.py designs/$ID 3 | tail -1)   # R1 pass band 2-14 mm, aim 2-10 (user 2026-10-15)
$PY -W ignore judge/part_validity.py $ID | tail -8
$PY -W ignore judge/body_contact.py $ID --step $S | head -6
$PY -W ignore judge/part_contact.py $ID --step $P | head -8   # R6: dense surface samples both ways (judge/test_part_contact.py)
$PY -W ignore judge/base_mount.py $ID --step $((S + 1)) | tail -1
[ -f pipeline/full-exo/designs/$ID/workspace.json ] && $PY -W ignore judge/workspace.py $ID --step $((S * 2)) | tail -1
$PY -W ignore judge/dynamics.py $ID | tail -1
[ -d pipeline/full-exo/designs/$ID/step ] && [ "$SKIP_FEA" != "1" ] && OMP_NUM_THREADS=2 $PY -W ignore judge/fea.py $ID $([ "$2" == "fast" ] && echo --fast) 2>&1 | tail -1   # R9 CalculiX FEA (RUNTIME; fast: t/2.5 mesh, no refinement check; SKIP_FEA=1 skips)
$PY judge/scorecard.py $ID
