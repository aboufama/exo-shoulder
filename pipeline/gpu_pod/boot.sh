# exo-gpu-bench boot job (first job on a fresh pod): torch with Blackwell kernels, CPU-kit deps for parity, the repo tree
# a farm job left on the volume, local copies of both bench grids, bench packs
set -x
pip install -q "torch==2.7.1" --index-url https://download.pytorch.org/whl/cu128 2>&1 | tail -2
pip install -q scipy==1.13.1 libigl==2.6.3 2>&1 | tail -2
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
mkdir -p /root/repo && tar xf /workspace/exo-farm/gpu/repo.tar -C /root/repo
mkdir -p /root/bench/14f156cb6fc8 /root/bench/0089c747c10f
cp /workspace/exo-farm/shared/bench/14f156cb6fc8/{grid.npy,meta.json} /root/bench/14f156cb6fc8/
cp /workspace/exo-farm/cas/e9/e99c311e213cce4add4e68f1324545457eb4fc377983e88a24c02131db0f2aa3 /root/bench/0089c747c10f/grid.npy
cp /workspace/exo-farm/cas/c3/c3bb1497a4c905d44f5e3383b3217b7b1ca5018dfb471d5f9dc1f74d1040f41c /root/bench/0089c747c10f/meta.json
cd /root/repo && rm -rf .cache/concept_bench && mkdir -p .cache/concept_bench
ln -sfn /root/bench/14f156cb6fc8 .cache/concept_bench/14f156cb6fc8; ln -sfn /root/bench/0089c747c10f .cache/concept_bench/0089c747c10f
cp /workspace/exo-farm/gpu/code/tools/gpu_bench.py tools/gpu_bench.py
CB_QUIET_EXACT=1 python3 tools/gpu_bench.py pack 60 160; CB_QUIET_EXACT=1 python3 tools/gpu_bench.py pack 110 360
nproc; nvidia-smi -L
