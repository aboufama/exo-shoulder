#!/bin/bash
# full fair-CAD pipeline for one searched design: <key> (band_cad/inputs/<key>.json must exist)
K=$1; L=${2:-"CAD $1"}; cd "$(dirname "$0")"; FX=../../full-exo
${PY:-python3} -W ignore $FX/band_to_design.py ../band_cad/inputs/$K.json 0 band_$K "$L" > out_$K.b2d.log 2>&1 || { echo "band_to_design failed"; tail -5 out_$K.b2d.log; exit 1; }
grep -A4 "^WARNING band_to_design" out_$K.b2d.log
# refuses a link without a real arm (docs/FINDINGS.md "Short link"); ALLOW_SHORT_LINK=1 overrides, only with the user's OK
(cd ../band_cad && ${PY:-python3} -W ignore make_cad_design.py $K band_$K "$L") > out_$K.mcd.log 2>&1 || { echo "make_cad_design refused / failed:"; tail -8 out_$K.mcd.log; exit 1; }
grep "base tab" out_$K.mcd.log
mkdir -p out_$K; cp $FX/designs/cad_$K/clips.json out_$K/clips_before_replan.json; rm -f out_$K/exclude.json
for i in 1 2 3 4 5; do
  cp out_$K/clips_before_replan.json $FX/designs/cad_$K/clips.json
  OMP_NUM_THREADS=2 ${PY:-python3} -W ignore replan.py $K 2>&1 | grep "hard coll\|overall"
  OMP_NUM_THREADS=2 ${PY:-python3} -W ignore fair_build.py $K members 2>&1 | grep -c "solid valid True" | sed 's/^/valid members: /'
  out=$(OMP_NUM_THREADS=2 ${PY:-python3} -W ignore verify_members.py $K 2>&1 | tail -3); echo "$out"
  echo "$out" | grep -q "no member interpenetration" && { echo "members clean after round $i"; break; }
done
OMP_NUM_THREADS=2 ${PY:-python3} -W ignore verify_members.py $K 2>&1 | tail -2; ${PY:-python3} -W ignore hold_bad.py $K
OMP_NUM_THREADS=2 ${PY:-python3} -W ignore fair_build.py $K assemble 2>&1 | tail -2
cp out_$K/exo.glb $FX/designs/cad_$K/exo.glb
OMP_NUM_THREADS=2 ${PY:-python3} -W ignore verify_armend.py $K 2>&1 | tail -6
(cd $FX && ${PY:-python3} -W ignore score_design.py designs/cad_$K 3 | tail -1)
