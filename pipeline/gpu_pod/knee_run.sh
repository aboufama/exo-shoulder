# exo-gpu-pinknee job (run by knee0.sh once the code tarball lands): the pin-knee port's parity gate (same-bench
# Bench(110,360) and frozen fit Bench(60,160) -> wear Bench(110,360), 50 configs inside the rulings + H1, k4598, P5, GPU
# port vs the CPU kit itself on the pod's CPUs), speed, then - only if every compared config's gap AND near-touch gap
# agree within 0.5 - the GPU FINAL POLISH (knee_polish's CMA on the near-touch gap, Bench(110,360) fast, verifier checks)
# for SEARCH_S seconds from H1 / P5 / k4598, rows + state written incrementally; the pod terminates itself at the end.
set -x
OUT=/workspace/exo-farm/gpuk/out/knee; mkdir -p $OUT; SEARCH_S=${SEARCH_S:-2400}
cd /root/repo; export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 CB_FOLD_MARGIN=5
N=$(python3 -c "import os; print(len(os.sched_getaffinity(0)))")      # (GNU nproc honours OMP_NUM_THREADS=1)
CQ=$(awk '{ if ($1 == "max") print 0; else print int($1 / $2) }' /sys/fs/cgroup/cpu.max 2>/dev/null || echo 0)
[ "${CQ:-0}" -gt 0 ] && [ "$CQ" -lt "$N" ] && N=$CQ
free -g | head -2; cat /sys/fs/cgroup/memory.max 2>/dev/null
W=6; [ $N -lt 10 ] && W=3; P=$(( N - W - 1 )); [ $P -gt 14 ] && P=14; [ $P -lt 2 ] && P=2
echo "nproc $N gpu-workers $W cpu-procs $P"; nvidia-smi --query-gpu=name,memory.total --format=csv
python3 tools/gpu_bench_knee.py parity --n 50 --mix --leaders --bench 110,360 --workers $W --procs $P --margin 5 --out $OUT/parity_same110.json 2>&1 | tee -a $OUT/log.txt | grep -v "^  " | tail -3
python3 tools/gpu_bench_knee.py parity --n 50 --mix --leaders --bench 110,360 --fit 60,160 --workers $W --procs $P --margin 5 --out $OUT/parity_frozen.json 2>&1 | tee -a $OUT/log.txt | grep -v "^  " | tail -3
python3 tools/gpu_bench_knee.py table $OUT/parity_same110.json $OUT/parity_frozen.json | tee -a $OUT/log.txt
nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv
SW=$(( N - 2 )); [ $SW -gt 14 ] && SW=14
python3 tools/gpu_bench_knee.py speed --n 56 --bench 110,360 --workers $SW --margin 5 --out $OUT/speed_same110.json 2>&1 | tee -a $OUT/log.txt | tail -1
python3 tools/gpu_bench_knee.py speed --n 28 --bench 110,360 --workers 1 --margin 5 --out $OUT/speed_same110_w1.json 2>&1 | tee -a $OUT/log.txt | tail -1
if python3 -c "import json,sys; sys.exit(0 if all(json.load(open(f))['summary']['n_gap_diff_gt_05'] == 0 and json.load(open(f))['summary']['n_near1_diff_gt_05'] == 0 and json.load(open(f))['summary']['n_compared'] >= 50 for f in sys.argv[1:]) else 1)" $OUT/parity_same110.json $OUT/parity_frozen.json; then
  echo "PARITY OK: GPU polish $SEARCH_S s" | tee -a $OUT/log.txt
  J=$(( SW / 3 )); [ $J -lt 2 ] && J=2
  H1=$(python3 -c "import json; print(json.dumps(json.load(open('docs/concepts/rows/skin-normal-3r-pin-knee.json'))['best_params']))")
  P5=$(python3 -c "import json; print(json.dumps(json.load(open('docs/concepts/rows/skin-normal-3r-pin-knee.json'))['rebase_polish_m5']['P5']['params']))")
  K4=$(python3 -c "import json; d=json.load(open('docs/concepts/rows/skin-normal-3r-pin-knee.json'))['best_params_previous']; d.pop('neck', None); print(json.dumps(d))")
  python3 tools/gpu_bench_knee.py cma --x0 "$H1" --label G1 --out $OUT/cma_G1.json --sigma 0.5 --popsize 16 --jobs $J --budget-s $SEARCH_S --seed 11 --obj near1 > $OUT/cma_G1.log 2>&1 &
  python3 tools/gpu_bench_knee.py cma --x0 "$P5" --label G2 --out $OUT/cma_G2.json --sigma 0.5 --popsize 16 --jobs $J --budget-s $SEARCH_S --seed 12 --obj near1 > $OUT/cma_G2.log 2>&1 &
  python3 tools/gpu_bench_knee.py cma --x0 "$H1" --label G3 --out $OUT/cma_G3.json --sigma 1.5 --popsize 16 --jobs $J --budget-s $SEARCH_S --seed 13 --obj near1 > $OUT/cma_G3.log 2>&1 &
  sleep 120; nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv; uptime
  wait; tail -3 $OUT/cma_G*.log | tee -a $OUT/log.txt
  echo "search done $(date -u +%FT%TZ): terminating the pod" | tee -a $OUT/log.txt
  runpodctl remove pod $RUNPOD_POD_ID || runpodctl stop pod $RUNPOD_POD_ID
else echo "PARITY FAILED: no search" | tee -a $OUT/log.txt; fi
