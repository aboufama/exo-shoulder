# exo-gpu-pinknee* restart of the massive pin-knee polish on an already booted pod (queued by a farm job, then the running
# gks.sh job is cancelled): the current driver from $RUN/override/, same deadlines; the claims on the volume keep every
# finished chunk / basin, so the run resumes where it stopped. Then the final stage and the pod removes itself.
set -x
source /root/xs/pipeline/gpu_pod/gks_env.sh
K=/workspace/exo-farm/gpuk; RUN=$K/out/$GKS_RUN; L=$RUN/log_${RUNPOD_POD_ID}.txt
echo "restart $(date -u +%FT%TZ): $(ls -R $RUN/override | tr '\n' ' ')" >> $L
cp -r $RUN/override/. /root/repo/
cd /root/repo; export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 CB_FOLD_MARGIN=5 IGL_NUM_THREADS=1 GKS_GB_PER_WORKER=2.8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv >> $L
LEFT=$(( ${GKS_T_CMA%.*} + 600 - $(date +%s) ))
timeout $LEFT python3 tools/gpu_knee_search.py run --out $RUN >> $L 2>&1
cp -r $RUN/override/. /root/repo/
LEFT=$(( ${GKS_T_VERIFY%.*} + 240 - $(date +%s) ))
timeout $LEFT python3 tools/gpu_knee_search.py final --out $RUN >> $L 2>&1
echo "search ended $(date -u +%FT%TZ): removing the pod" >> $L
runpodctl remove pod $RUNPOD_POD_ID || runpodctl stop pod $RUNPOD_POD_ID
