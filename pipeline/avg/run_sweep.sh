#!/bin/zsh
# average-person shoulder search: inner face radius x back-projection limit
export H_LEN=325 FP=1 FP_W=14 FP_HUB=34 CLEAR=4 POST_HALF=180 WORKERS=4
for RIN in 94 100 106; do
  for BACK in 10 0; do
    ROUT=$(python3 -c "print($RIN + 5.57)")
    FP_RIN=$RIN FP_ROUT=$ROUT BACK_MAX=$BACK TAG=_rin$RIN ${PY:-python3} -u -W ignore opt_D.py $((RIN + 5)) 14 > sweep_rin${RIN}_back${BACK}.out 2>&1
  done
done
echo ALLDONE > sweep.done
