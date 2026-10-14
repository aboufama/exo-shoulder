#!/bin/zsh
# drop-in BOTTOM: J4 on the user's post axis, shell at BOTTOM's boss (102 mm), links clear of the bar
while [ ! -f sweep.done ]; do sleep 30; done
export H_LEN=325 FP=1 FP_W=14 FP_HUB=34 CLEAR=4 POST_HALF=180 WORKERS=4 DROPIN=1 BAR_D=102 FIX_W=$PWD/fix_w.json
for BACK in 10 0; do
  FP_RIN=102 FP_ROUT=107.57 BACK_MAX=$BACK TAG=_rin102 ${PY:-python3} -u -W ignore opt_D.py 107 14 > sweep_dropin_back${BACK}.out 2>&1
done
echo DONE > dropin.done
