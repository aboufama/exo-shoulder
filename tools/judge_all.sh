#!/bin/bash
# run every judge on one design and print the scorecard. Usage: tools/judge_all.sh <design id> [fast]
set -e; cd "$(dirname "$0")/.."; ID=$1; PY=${PY:-python3}; S=2; P=4; [ "$2" == "fast" ] && S=6 && P=12
(cd pipeline/full-exo && $PY -W ignore score_design.py designs/$ID 3 | tail -1)
$PY -W ignore judge/part_validity.py $ID | tail -8
$PY -W ignore judge/body_contact.py $ID --step $S | head -6
$PY -W ignore judge/part_contact.py $ID --step $P | head -8
$PY -W ignore judge/base_mount.py $ID --step $((S + 1)) | tail -1
$PY judge/scorecard.py $ID
