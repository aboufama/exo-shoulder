#!/bin/zsh
# build + animate both average-person designs (in parallel)
cd ${0:a:h}
build() {   # $1 dir  $2 design json  $3 subtitle
  ( cd ../shoulder-d4 && H_LEN=325 ROM_DIR=../avg DES_FILE=$2 R_I0=106 STUB=0 OUT_DIR=../full-exo/$1/shoulder ${PY:-python3} -W ignore build_shoulder_d4.py > ../full-exo/$1/shoulder.out 2>&1 )
  ${PY:-python3} -W ignore build_full_exo.py $1 > $1/full.out 2>&1
  ${PY:-python3} -u -W ignore make_clips_full.py $1 "$3" > $1/clips.out 2>&1
  echo done > $1/DONE
}
build designs/back10 opt_D_111_c4_p180_fp_back10_rin106.json "average adult · 1.75 m · ≤10 mm off the back" &
build designs/maxrange opt_D_111_c4_p180_fp_rin106.json "average adult · 1.75 m · maximum range" &
wait
