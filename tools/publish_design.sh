#!/bin/bash
# copy a fair_cad build into the viewer/judge design dir: exo.glb, step/, parts_full.json; regenerate per-part GLBs
set -e; cd "$(dirname "$0")/.."; K=$1; PY=${PY:-python3}
S=pipeline/conformal/fair_cad/out_$K; D=pipeline/full-exo/designs/cad_$K; mkdir -p $D/step
cp $S/exo.glb $D/; cp $S/step/*.step $D/step/; cp $S/parts.json $D/parts_full.json
(cd pipeline/conformal/fair_cad && $PY -W ignore parts_export.py $K >/dev/null && echo "parts.html ready: designs/cad_$K/parts/")
