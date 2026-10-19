# exo-gpu-bench exhaustive search of the zero-complexity class (one pod = one part of 2; PART set by the submitted copy):
# a small parity check incl. the near-touch metric (CPU kit on the pod, background), the Sobol screen with exact lower
# bounds (stage A closure + K2, stage B hub levels + hub skin, then the full bench in bound order), then batched
# multi-start CMA-ES (near-touch objective) over the 50 best distinct basins of BOTH pods' screens, converged starts
# replaced from a reserve. Everything lands in /workspace/exo-farm/gpu/out/xs/ (shared by both pods).
set -x
PART=${PART:-0}; OUTA=/workspace/exo-farm/gpu/out/xs; mkdir -p $OUTA; CODE=${CODE:-/workspace/exo-farm/gpu/code}
SCREEN_S=${SCREEN_S:-2400}; CMA_S=${CMA_S:-2400}; NS=${NS:-60000}
cd /root/repo && cp $CODE/tools/gpu_bench.py tools/gpu_bench.py
[ -d $CODE/docs ] && cp -r $CODE/tools/. tools/ && cp -r $CODE/docs/. docs/        # the CPU kit + zc model + verifier, current
cp $CODE/pipeline/gpu_pod/zc_seeds.json /root/zc_seeds.json
nvidia-smi -L; nproc; free -g | head -2
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 GB_EXACT_OUTSIDE=0
( python3 tools/gpu_bench.py parity --n 4 --sane --extra /root/zc_seeds.json --bench 110,360 --procs 8 --chunk 16 \
    --out $OUTA/parity_p$PART.json > $OUTA/parity_p$PART.log 2>&1 & )
python3 tools/gpu_bench.py screen --bench 110,360 --n $NS --part $PART/2 --seed 11 --thr 45 --budget $SCREEN_S --stacks 2 \
  --chunk 144 --extra /root/zc_seeds.json --out $OUTA/screen_p$PART.json 2>&1 | grep -v "^  group" | tee $OUTA/screen_p$PART.log
touch $OUTA/screen_p$PART.done
for k in $(seq 90); do [ -f $OUTA/screen_p0.done ] && [ -f $OUTA/screen_p1.done ] && break; sleep 5; done
python3 tools/gpu_bench.py cma $OUTA/screen_p0.json $OUTA/screen_p1.json --bench 110,360 --part $PART/2 --basins 50 --reserve 40 \
  --lam 12 --sigma0 0.6 --key near --budget $CMA_S --chunk 144 --seed $((PART + 1)) --extra /root/zc_seeds.json \
  --out $OUTA/cma_p$PART.json 2>&1 | grep -v "^  group" | tee $OUTA/cma_p$PART.log
touch $OUTA/cma_p$PART.done
for k in $(seq 120); do [ -f $OUTA/cma_p0.done ] && [ -f $OUTA/cma_p1.done ] && break; sleep 5; done
# the outside judge: the CPU kit on this pod's CPUs, top 10 distinct configs of both pods (this pod's share), frozen exact
python3 $CODE/pipeline/gpu_pod/xs_verify.py $OUTA $PART 2 --top 10 --procs 5 2>&1 | tee $OUTA/verify_p$PART.log
touch $OUTA/verify_p$PART.done
