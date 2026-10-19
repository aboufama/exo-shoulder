# exo-gpu-bench job 5: the posed skins next to both grids (the kit's exact path for points outside the grid box, now
# also used by the port), then parity (same-bench 110/360, frozen 60/160 -> 110/360), speed, and - only if parity
# holds for every config (gap within 1 point) - the GPU hill-climb on Bench(110,360) for SEARCH_S seconds
set -x
OUT=/workspace/exo-farm/gpu/out/gpu5; mkdir -p $OUT; SEARCH_S=${SEARCH_S:-2400}
ls -la /workspace/exo-farm/shared/bench/14f156cb6fc8/ | grep -v part_
[ -f /root/bench/14f156cb6fc8/skins.npy ] || cp /workspace/exo-farm/shared/bench/14f156cb6fc8/skins.npy /root/bench/14f156cb6fc8/ 2>/dev/null || echo "no assembled skins for 110/360: BP.posed per pose"
[ -f /root/bench/0089c747c10f/skins.npy ] || cp /workspace/exo-farm/cas/33/3305343863fd06d6e12e6c34d3d4a630f741c84a4cccd5a42a7e5e275a2379a1 /root/bench/0089c747c10f/skins.npy
cd /root/repo && cp /workspace/exo-farm/gpu/code/tools/gpu_bench.py tools/gpu_bench.py
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1
python3 tools/gpu_bench.py parity --n 50 --sane --leaders --bench 110,360 --procs 15 --chunk 96 --out $OUT/parity_same110.json 2>&1 | tee -a $OUT/log.txt | tail -4
python3 tools/gpu_bench.py parity --n 16 --sane --leaders --bench 110,360 --fit 60,160 --procs 15 --chunk 96 --out $OUT/parity_frozen.json 2>&1 | tee -a $OUT/log.txt | tail -4
GB_EXACT_OUTSIDE=0 GB_PROF=1 python3 tools/gpu_bench.py speed --n 576 --bench 110,360 --chunk 96 --out $OUT/speed_same110.json 2>&1 | tee -a $OUT/log.txt | tail -8
GB_EXACT_OUTSIDE=0 GB_PROF=1 python3 tools/gpu_bench.py speed --n 576 --bench 110,360 --chunk 192 --out $OUT/speed_same110_c192.json 2>&1 | tee -a $OUT/log.txt | tail -8
GB_EXACT_OUTSIDE=0 python3 tools/gpu_bench.py speed --n 576 --bench 110,360 --fit 60,160 --chunk 96 --out $OUT/speed_frozen.json 2>&1 | tee -a $OUT/log.txt | tail -2
python3 tools/gpu_bench.py table $OUT/parity_same110.json $OUT/parity_frozen.json | tee -a $OUT/log.txt
if python3 -c "import json,sys; sys.exit(0 if all(json.load(open(f))['summary']['n_gap_diff_gt_1'] == 0 for f in sys.argv[1:]) else 1)" $OUT/parity_same110.json $OUT/parity_frozen.json; then
  GB_EXACT_OUTSIDE=0 python3 tools/gpu_bench.py search --bench 110,360 --chunk 144 --budget $SEARCH_S --n0 4096 --elites 16 --lam 18 --seed 1 --out $OUT/search_same110.json 2>&1 | tee -a $OUT/log.txt | grep -E "map|gen|Error|Traceback" | tail -40
else echo "PARITY FAILED: no search" | tee -a $OUT/log.txt; fi
