# exo-gpu-bench3 xs5: the reach / in-band frontier refined - 7 reach targets, the 4 best distinct rows of every round (incl.
# xs4's frontier) per target, lambda 24, two step sizes per start. Out: gpu/out/xs5/pareto.json
set -x
OUTA=/workspace/exo-farm/gpu/out/xs5; mkdir -p $OUTA; CODE=/workspace/exo-farm/gpu/code; X=/workspace/exo-farm/gpu/out
cd /root/repo && cp $CODE/tools/gpu_bench.py tools/gpu_bench.py
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 GB_EXACT_OUTSIDE=0
python3 tools/gpu_bench.py pareto $X/xs4/pareto.json $X/xs/cma_p0.json $X/xs/cma_p1.json $X/xs2/cma.json $X/xs/screen_p0.json \
  $X/xs/screen_p1.json $X/xs2/screen_p0.json $X/xs2/screen_p1.json --targets 0.62,0.65,0.68,0.70,0.72,0.75,0.80 --bench 110,360 \
  --basins 4 --lam 24 --sigma0 0.5 --budget ${PAR_S:-900} --chunk 192 --seed 41 --out $OUTA/pareto.json 2>&1 | grep -v "^  group" | tee $OUTA/pareto.log
touch $OUTA/pareto.done
