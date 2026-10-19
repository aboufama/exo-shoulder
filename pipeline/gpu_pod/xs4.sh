# exo-gpu-bench3 xs4: the zero-complexity class's reach / in-band frontier - for each reach target R in 0.65 ... 0.85, CMA
# on 100 max(0, .90 - in-band14) + 1000 max(0, R - reach) + 100 max(0, .95 - follow) + 100 contact from the 5 best distinct
# rows of every earlier round (xs, xs2). Out: gpu/out/xs4/pareto.json
set -x
OUTA=/workspace/exo-farm/gpu/out/xs4; mkdir -p $OUTA; CODE=/workspace/exo-farm/gpu/code; X=/workspace/exo-farm/gpu/out
cd /root/repo && cp $CODE/tools/gpu_bench.py tools/gpu_bench.py
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 GB_EXACT_OUTSIDE=0
python3 tools/gpu_bench.py pareto $X/xs/cma_p0.json $X/xs/cma_p1.json $X/xs/screen_p0.json $X/xs/screen_p1.json $X/xs2/cma.json \
  $X/xs2/screen_p0.json $X/xs2/screen_p1.json --bench 110,360 --basins 5 --lam 12 --sigma0 0.6 --budget ${PAR_S:-1200} --chunk 144 \
  --seed 31 --out $OUTA/pareto.json 2>&1 | grep -v "^  group" | tee $OUTA/pareto.log
touch $OUTA/pareto.done
