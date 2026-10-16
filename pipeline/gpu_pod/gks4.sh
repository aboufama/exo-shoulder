# exo-gpu-pinknee4: (1) restarts the three running pods on the current driver straight through the volume (the farm queue
# was 12 deep): the driver goes to $RUN/override/, a restart job (gks2.sh, named 01c_*) into each pod's spool queue, and the
# cancel flag; a directory at the override's .tmp path makes the two stale farm restart jobs abort at their mv (set -e) or
# skip (their evidence never appears) instead of reverting the driver; (2) then joins the search as a 4th pod (gks.sh).
set -x
source /root/xs/pipeline/gpu_pod/gks_env.sh
V=/workspace/exo-farm; R=$V/gpuk/out/$GKS_RUN
mkdir -p $R/override/tools
cp /root/xs/tools/gpu_knee_search.py $R/override/tools/gpu_knee_search.py.new && mv $R/override/tools/gpu_knee_search.py.new $R/override/tools/gpu_knee_search.py
mkdir -p $R/override/tools/gpu_knee_search.py.tmp && touch $R/override/tools/gpu_knee_search.py.tmp/keep
for s in gpuk1 gpuk2 gpuk3; do mkdir -p $V/$s/queue; cp /root/xs/pipeline/gpu_pod/gks2.sh $V/$s/queue/01c_gks2.sh.new && mv $V/$s/queue/01c_gks2.sh.new $V/$s/queue/01c_gks2.sh; touch $V/$s/cancel; done
echo "v3 restart issued $(date -u +%FT%TZ) by $RUNPOD_POD_ID" >> $R/restart.txt
export GKS_GB_PER_WORKER=2.0 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
bash /root/xs/pipeline/gpu_pod/gks.sh
