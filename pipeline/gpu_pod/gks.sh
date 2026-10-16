# exo-gpu-pinknee* : the massive pin-knee polish (tools/gpu_knee_search.py) on one pod of several sharing the farm volume.
# Code travels IN the pod definition (gpu_pod.py create --payload, unpacked to /root/xs): no farm round trip. Boot = torch
# with Blackwell kernels + the CPU-kit deps (scipy / libigl, for the CPU verification too), the repo tree from the volume
# with this payload's current code over it, both bench grids on local disk. Then the search; then the pod removes itself.
set -x
source /root/xs/pipeline/gpu_pod/gks_env.sh
K=/workspace/exo-farm/gpuk; RUN=$K/out/$GKS_RUN; mkdir -p $RUN; L=$RUN/log_${RUNPOD_POD_ID}.txt
echo "boot $(date -u +%FT%TZ) $(nvidia-smi -L)" >> $L
pip install -q "torch==2.7.1" --index-url https://download.pytorch.org/whl/cu128 2>&1 | tail -2
pip install -q scipy==1.13.1 libigl==2.6.3 2>&1 | tail -2
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))" | tee -a $L
mkdir -p /root/repo && tar xf /workspace/exo-farm/gpu/repo.tar -C /root/repo
tar xf /workspace/exo-farm/gpu/code/.cache/gpu_knee/knee_code2.tar -C /root/repo     # the kit as of the port's parity run
cp -r /root/xs/. /root/repo/                                                        # + this payload (driver, port, rows, harnesses)
mkdir -p /root/bench/14f156cb6fc8 /root/bench/0089c747c10f
cp /workspace/exo-farm/shared/bench/14f156cb6fc8/{grid.npy,meta.json} /root/bench/14f156cb6fc8/
cp /workspace/exo-farm/shared/bench/14f156cb6fc8/skins.npy /root/bench/14f156cb6fc8/ 2>/dev/null || echo "no skins for 110/360"
cp /workspace/exo-farm/cas/e9/e99c311e213cce4add4e68f1324545457eb4fc377983e88a24c02131db0f2aa3 /root/bench/0089c747c10f/grid.npy
cp /workspace/exo-farm/cas/c3/c3bb1497a4c905d44f5e3383b3217b7b1ca5018dfb471d5f9dc1f74d1040f41c /root/bench/0089c747c10f/meta.json
cp /workspace/exo-farm/cas/33/3305343863fd06d6e12e6c34d3d4a630f741c84a4cccd5a42a7e5e275a2379a1 /root/bench/0089c747c10f/skins.npy
cd /root/repo && rm -rf .cache/concept_bench && mkdir -p .cache/concept_bench
ln -sfn /root/bench/14f156cb6fc8 .cache/concept_bench/14f156cb6fc8; ln -sfn /root/bench/0089c747c10f .cache/concept_bench/0089c747c10f
nproc; free -g | head -2; cat /sys/fs/cgroup/cpu.max /sys/fs/cgroup/memory.max 2>/dev/null; nvidia-smi --query-gpu=name,memory.total --format=csv
echo "booted $(date -u +%FT%TZ)" >> $L
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1 CB_FOLD_MARGIN=5 IGL_NUM_THREADS=1
LEFT=$(( ${GKS_T_VERIFY%.*} + 240 - $(date +%s) ))
timeout $LEFT python3 tools/gpu_knee_search.py run --out $RUN >> $L 2>&1
echo "search ended $(date -u +%FT%TZ): removing the pod" >> $L
runpodctl remove pod $RUNPOD_POD_ID || runpodctl stop pod $RUNPOD_POD_ID
