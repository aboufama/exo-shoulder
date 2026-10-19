# exo-gpu-bench job 6: frozen-protocol parity (fit 60/160 -> wear 110/360) with the CPU reference fixed (it fell back to
# the same-bench run for configs whose FIT-bench gap was >= 200), then the GPU hill-climb on Bench(110,360) - gated on
# the same-bench parity of job 5 (54 configs, every metric identical)
set -x
OUT=/workspace/exo-farm/gpu/out/gpu6; mkdir -p $OUT; SEARCH_S=${SEARCH_S:-1800}
cd /root/repo && cp /workspace/exo-farm/gpu/code/tools/gpu_bench.py tools/gpu_bench.py
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1
python3 tools/gpu_bench.py parity --n 50 --sane --leaders --bench 110,360 --fit 60,160 --procs 15 --chunk 96 --out $OUT/parity_frozen.json 2>&1 | tee -a $OUT/log.txt | tail -3
if python3 -c "import json,sys; sys.exit(0 if json.load(open(sys.argv[1]))['summary']['n_gap_diff_gt_1'] == 0 else 1)" /workspace/exo-farm/gpu/out/gpu5/parity_same110.json; then
  GB_EXACT_OUTSIDE=0 python3 tools/gpu_bench.py search --bench 110,360 --chunk 192 --budget $SEARCH_S --n0 6144 --elites 24 --lam 16 --seed 1 --out $OUT/search_same110.json 2>&1 | tee -a $OUT/log.txt | grep -E "map|gen|Error|Traceback" | tail -60
else echo "PARITY FAILED: no search" | tee -a $OUT/log.txt; fi
