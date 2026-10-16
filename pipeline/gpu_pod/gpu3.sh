# exo-gpu-bench job 2: parity (same-bench 110/360 and frozen 60/160 -> 110/360) with the fixed port, speed, then -
# only if parity holds (every config's gap within 1 point) - the GPU hill-climb on Bench(110,360) (same-bench, the
# golden search objective of zc-frontier-3r) for SEARCH_S seconds, frontier written incrementally
set -x
OUT=/workspace/exo-farm/gpu/out/gpu3; mkdir -p $OUT; free -g | head -2; cat /sys/fs/cgroup/memory.max 2>/dev/null; SEARCH_S=${SEARCH_S:-2400}
cd /root/repo && cp /workspace/exo-farm/gpu/code/tools/gpu_bench.py tools/gpu_bench.py
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1
python3 tools/gpu_bench.py parity --n 50 --leaders --bench 110,360 --procs 14 --chunk 54 --out $OUT/parity_same110.json 2>&1 | tee -a $OUT/log.txt | tail -4
python3 tools/gpu_bench.py parity --n 50 --leaders --bench 110,360 --fit 60,160 --procs 14 --chunk 54 --out $OUT/parity_frozen.json 2>&1 | tee -a $OUT/log.txt | tail -4
GB_PROF=1 python3 tools/gpu_bench.py speed --n 576 --bench 110,360 --chunk 96 --out $OUT/speed_same110.json 2>&1 | tee -a $OUT/log.txt | tail -8
GB_PROF=1 python3 tools/gpu_bench.py speed --n 576 --bench 110,360 --chunk 192 --out $OUT/speed_same110_c192.json 2>&1 | tee -a $OUT/log.txt | tail -8
python3 tools/gpu_bench.py speed --n 576 --bench 110,360 --fit 60,160 --chunk 96 --out $OUT/speed_frozen.json 2>&1 | tee -a $OUT/log.txt | tail -2
python3 tools/gpu_bench.py table $OUT/parity_same110.json $OUT/parity_frozen.json
if python3 -c "import json,sys; sys.exit(0 if all(json.load(open(f))['summary']['n_gap_diff_gt_1'] == 0 for f in sys.argv[1:]) else 1)" $OUT/parity_same110.json $OUT/parity_frozen.json; then
  python3 tools/gpu_bench.py search --bench 110,360 --chunk 144 --budget $SEARCH_S --n0 4096 --elites 16 --lam 18 --seed 1 --out $OUT/search_same110.json 2>&1 | grep -E "map|gen|Error|Traceback" | tail -40
else echo "PARITY FAILED: no search"; fi
