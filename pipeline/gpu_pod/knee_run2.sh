# exo-gpu-pinknee job 2 (port v2: + bit-identical CPU-side speed-ups - the rest-skin libigl trees built once for the seats,
# the batched IK - and raglan-knee-3r's routed links): parity again on the SAME configs (the CPU reference does not depend
# on the port: v1's CPU rows are reused, only new configs - raglan - run on the CPU), speed, then - only if every compared
# config's gap AND near-touch gap agree within 0.5 - the GPU FINAL POLISH (knee_polish's CMA, near-touch objective,
# Bench(110,360) fast, verifier checks) for SEARCH_S s from H1 / P5 / H1 wide / raglan; the pod terminates itself at the end.
set -x
OUT=/workspace/exo-farm/gpuk/out/knee; mkdir -p $OUT; SEARCH_S=${SEARCH_S:-2400}
cd /root/repo; export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 CB_FOLD_MARGIN=5
N=$(python3 -c "import os; print(len(os.sched_getaffinity(0)))")
CQ=$(awk '{ if ($1 == "max") print 0; else print int($1 / $2) }' /sys/fs/cgroup/cpu.max 2>/dev/null || echo 0)
[ "${CQ:-0}" -gt 0 ] && [ "$CQ" -lt "$N" ] && N=$CQ
W=$(( N - 2 )); [ $W -gt 14 ] && W=14; [ $W -lt 2 ] && W=2
echo "nproc $N gpu-workers $W"
python3 tools/gpu_bench_knee.py parity --n 50 --mix --leaders --bench 110,360 --workers $W --procs 2 --margin 5 --cpu-from $OUT/parity_same110.json --out $OUT/parity2_same110.json 2>&1 | tee -a $OUT/log2.txt | grep -v "^  " | tail -3
python3 tools/gpu_bench_knee.py parity --n 50 --mix --leaders --bench 110,360 --fit 60,160 --workers $W --procs 2 --margin 5 --cpu-from $OUT/parity_frozen.json --out $OUT/parity2_frozen.json 2>&1 | tee -a $OUT/log2.txt | grep -v "^  " | tail -3
python3 tools/gpu_bench_knee.py table $OUT/parity2_same110.json $OUT/parity2_frozen.json | tee -a $OUT/log2.txt
python3 tools/gpu_bench_knee.py speed --n 72 --bench 110,360 --workers $(( N - 1 )) --margin 5 --out $OUT/speed2_same110.json 2>&1 | tee -a $OUT/log2.txt | tail -1
python3 tools/gpu_bench_knee.py speed --n 18 --bench 110,360 --workers 1 --margin 5 --out $OUT/speed2_same110_w1.json 2>&1 | tee -a $OUT/log2.txt | tail -1
GBK_FAST_CPU=0 python3 tools/gpu_bench_knee.py speed --n 18 --bench 110,360 --workers 1 --margin 5 --out $OUT/speed1_same110_w1.json 2>&1 | tee -a $OUT/log2.txt | tail -1
python3 tools/gpu_bench_knee.py speed --n 36 --bench 110,360 --fit 60,160 --workers $(( N - 1 )) --margin 5 --out $OUT/speed2_frozen.json 2>&1 | tee -a $OUT/log2.txt | tail -1
nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv
if python3 -c "import json,sys; sys.exit(0 if all(json.load(open(f))['summary']['n_gap_diff_gt_05'] == 0 and json.load(open(f))['summary']['n_near1_diff_gt_05'] == 0 and json.load(open(f))['summary']['n_compared'] >= 50 for f in sys.argv[1:]) else 1)" $OUT/parity2_same110.json $OUT/parity2_frozen.json; then
  echo "PARITY OK: GPU polish $SEARCH_S s" | tee -a $OUT/log2.txt
  J=$(( (N - 1) / 4 )); [ $J -lt 2 ] && J=2
  RW=docs/concepts/rows/skin-normal-3r-pin-knee.json; RR=docs/concepts/rows/raglan-knee-3r.json
  H1=$(python3 -c "import json; print(json.dumps(json.load(open('$RW'))['best_params']))")
  P5=$(python3 -c "import json; print(json.dumps(json.load(open('$RW'))['rebase_polish_m5']['P5']['params']))")
  RX=$(python3 -c "import json; d=json.load(open('$RR'))['best_params']; ks='az1 el1 az2 el2 wd wa b3 lE lc phiE phib stk ang_min'.split(); print(json.dumps({k: d[k] for k in ks}))")
  RF=$(python3 -c "import json; d=json.load(open('$RR'))['best_params']; print(json.dumps({k: d[k] for k in ('r1t', 'r1d', 'r2t', 'r2d', 'rc')}))")
  python3 tools/gpu_bench_knee.py cma --x0 "$H1" --label G1 --out $OUT/cma_G1.json --sigma 0.5 --popsize 16 --jobs $J --budget-s $SEARCH_S --seed 11 --obj near1 > $OUT/cma_G1.log 2>&1 &
  python3 tools/gpu_bench_knee.py cma --x0 "$P5" --label G2 --out $OUT/cma_G2.json --sigma 0.5 --popsize 16 --jobs $J --budget-s $SEARCH_S --seed 12 --obj near1 > $OUT/cma_G2.log 2>&1 &
  python3 tools/gpu_bench_knee.py cma --x0 "$H1" --label G3 --out $OUT/cma_G3.json --sigma 1.5 --popsize 16 --jobs $J --budget-s $SEARCH_S --seed 13 --obj near1 > $OUT/cma_G3.log 2>&1 &
  python3 tools/gpu_bench_knee.py cma --x0 "$RX" --fixed "$RF" --label G4 --out $OUT/cma_G4.json --sigma 0.5 --popsize 16 --jobs $J --budget-s $SEARCH_S --seed 14 --obj near1 > $OUT/cma_G4.log 2>&1 &
  sleep 180; nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv | tee -a $OUT/log2.txt; uptime | tee -a $OUT/log2.txt
  wait; tail -2 $OUT/cma_G*.log | tee -a $OUT/log2.txt
  echo "search done $(date -u +%FT%TZ): terminating the pod" | tee -a $OUT/log2.txt
  runpodctl remove pod $RUNPOD_POD_ID || runpodctl stop pod $RUNPOD_POD_ID
else echo "PARITY FAILED: no search" | tee -a $OUT/log2.txt; fi
