# gks10: the pod's earlier drivers survived every cancel (GNU timeout runs its child in its own process group, so the
# spool's group kill missed them; their GPU workers then held the memory and the new driver's workers died at init with
# CUDA out-of-memory). Kill every driver / pool worker on this pod, check the GPU is free, then run the current override
# driver (v4) under `timeout --foreground` (same group: the next cancel reaches it); the final stage; the pod removes itself.
set -x
source /root/xs/pipeline/gpu_pod/gks_env.sh
K=/workspace/exo-farm/gpuk; RUN=$K/out/$GKS_RUN; L=$RUN/log_${RUNPOD_POD_ID}.txt
echo "gks10 $(date -u +%FT%TZ): killing earlier drivers: $(pgrep -fc gpu_knee_search.py) drivers, $(pgrep -fc multiprocessing.spawn) workers" >> $L
pkill -f gpu_knee_search.py; pkill -f multiprocessing.spawn; sleep 6; pkill -9 -f gpu_knee_search.py; pkill -9 -f multiprocessing.spawn; sleep 4
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader >> $L
cp -r $RUN/override/. /root/repo/
cd /root/repo; export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 CB_FOLD_MARGIN=5 IGL_NUM_THREADS=1 GKS_GB_PER_WORKER=2.8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
LEFT=$(( ${GKS_T_CMA%.*} + 600 - $(date +%s) ))
timeout --foreground $LEFT python3 tools/gpu_knee_search.py run --out $RUN >> $L 2>&1
cp -r $RUN/override/. /root/repo/
LEFT=$(( ${GKS_T_VERIFY%.*} + 240 - $(date +%s) ))
timeout --foreground $LEFT python3 tools/gpu_knee_search.py final --out $RUN >> $L 2>&1
echo "search ended $(date -u +%FT%TZ): removing the pod" >> $L
runpodctl remove pod $RUNPOD_POD_ID || runpodctl stop pod $RUNPOD_POD_ID
