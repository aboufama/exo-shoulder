# exo-gpu-bench xs3: deep polish of the best basins found by xs (both pods' CMA + screens): every branch x stack order at
# each basin's best, then IPOP-style CMA restarts (lambda 24 / 24 / 48, sigma0 0.3 / 1.2 / 0.6, near-touch objective, the
# best plain gap tracked); then the CPU kit (frozen exact) on its top configs not verified by xs. Out: gpu/out/xs3/
set -x
PART=${PART:-0}; OUTA=/workspace/exo-farm/gpu/out/xs3; mkdir -p $OUTA; CODE=/workspace/exo-farm/gpu/code; IN=/workspace/exo-farm/gpu/out/xs
cd /root/repo && cp $CODE/tools/gpu_bench.py tools/gpu_bench.py
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 GB_EXACT_OUTSIDE=0
# near-touch objective (the CLAUDE.md search rule), then the plain gap (the golden claim's metric, near reported)
python3 tools/gpu_bench.py polish $IN/cma_p0.json $IN/cma_p1.json $IN/screen_p0.json $IN/screen_p1.json --bench 110,360 \
  --part $PART/2 --basins 4 --key near --budget $(( ${POL_S:-1200} / 2 )) --chunk 144 --seed $((PART + 11)) --out $OUTA/cma_p$PART.json 2>&1 \
  | grep -v "^  group" | tee $OUTA/polish_p$PART.log
python3 tools/gpu_bench.py polish $IN/cma_p0.json $IN/cma_p1.json $IN/screen_p0.json $IN/screen_p1.json --bench 110,360 \
  --part $PART/2 --basins 4 --key gap --budget $(( ${POL_S:-1200} / 2 )) --chunk 144 --seed $((PART + 21)) --out $OUTA/cmag_p$PART.json 2>&1 \
  | grep -v "^  group" | tee $OUTA/polishg_p$PART.log
touch $OUTA/cma_p$PART.done
for k in $(seq 120); do [ -f $OUTA/cma_p0.done ] && [ -f $OUTA/cma_p1.done ] && break; sleep 5; done
python3 $CODE/pipeline/gpu_pod/xs_verify.py $OUTA $PART 2 --top 6 --procs 3 --skip $IN/verify_pick.json 2>&1 | tee $OUTA/verify_p$PART.log
touch $OUTA/verify_p$PART.done
