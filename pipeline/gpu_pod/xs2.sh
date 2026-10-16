# exo-gpu-bench3: the second, independent Sobol sweep of the zero-complexity class (scramble seed 12, ~10^6 configs,
# both halves on this pod), same exact lower bounds / full bench in bound order as xs.sh, then batched multi-start CMA
# (near-touch) from its 20 best distinct basins. Out: /workspace/exo-farm/gpu/out/xs2/
set -x
OUTA=/workspace/exo-farm/gpu/out/xs2; mkdir -p $OUTA; CODE=${CODE:-/root/xs}
cd /root/repo && cp $CODE/tools/gpu_bench.py tools/gpu_bench.py && cp -r $CODE/tools/. tools/ && cp -r $CODE/docs/. docs/
cp $CODE/pipeline/gpu_pod/zc_seeds.json /root/zc_seeds.json
nvidia-smi -L; nproc; free -g | head -2
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 GB_EXACT_OUTSIDE=0
for P in 0 1; do
  python3 tools/gpu_bench.py screen --bench 110,360 --n 400000 --part $P/2 --seed 12 --thr 35 --budget 2700 --stacks 2 \
    --chunk 144 --out $OUTA/screen_p$P.json 2>&1 | grep -v "^  group" | tee $OUTA/screen_p$P.log
done
touch $OUTA/screen.done
python3 tools/gpu_bench.py cma $OUTA/screen_p0.json $OUTA/screen_p1.json --bench 110,360 --part 0/1 --basins 20 --reserve 20 \
  --lam 12 --sigma0 0.6 --key near --budget 900 --chunk 144 --seed 5 --out $OUTA/cma.json 2>&1 | grep -v "^  group" | tee $OUTA/cma.log
touch $OUTA/cma.done
