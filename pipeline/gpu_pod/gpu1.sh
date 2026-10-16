# exo-gpu-bench job: torch check, local copies of both bench grids, packs, speed + parity (same-bench 110/360 and frozen 60/160 -> 110/360)
set -x
OUT=/workspace/exo-farm/gpu/out/gpu1; mkdir -p $OUT
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0)); x = torch.randn(64, device='cuda'); print((x*x).sum().item())" 2>&1 | tail -3
cd /root/repo
cp /workspace/exo-farm/gpu/code/tools/gpu_bench.py tools/gpu_bench.py
# bench grids on the pod's local disk (the 110/360 one built on the farm; the 60/160 one = the farm's CAS blob of the same cache)
mkdir -p /root/bench/14f156cb6fc8 /root/bench/0089c747c10f
[ -f /root/bench/14f156cb6fc8/grid.npy ] || cp /workspace/exo-farm/shared/bench/14f156cb6fc8/{grid.npy,meta.json} /root/bench/14f156cb6fc8/
[ -f /root/bench/0089c747c10f/grid.npy ] || { cp /workspace/exo-farm/cas/e9/e99c311e213cce4add4e68f1324545457eb4fc377983e88a24c02131db0f2aa3 /root/bench/0089c747c10f/grid.npy; cp /workspace/exo-farm/cas/c3/c3bb1497a4c905d44f5e3383b3217b7b1ca5018dfb471d5f9dc1f74d1040f41c /root/bench/0089c747c10f/meta.json; }
rm -rf .cache/concept_bench; mkdir -p .cache/concept_bench; ln -sfn /root/bench/14f156cb6fc8 .cache/concept_bench/14f156cb6fc8; ln -sfn /root/bench/0089c747c10f .cache/concept_bench/0089c747c10f
ls -la /root/bench/*/
export CB_QUIET_EXACT=1 OMP_NUM_THREADS=1
python3 tools/gpu_bench.py pack 60 160; python3 tools/gpu_bench.py pack 110 360
python3 tools/gpu_bench.py speed --n 96 --bench 110,360 --chunk 48 --out $OUT/speed_same110.json 2>&1 | tail -5
python3 tools/gpu_bench.py parity --n 50 --leaders --bench 110,360 --procs 40 --chunk 48 --out $OUT/parity_same110.json 2>&1 | tail -8
python3 tools/gpu_bench.py parity --n 50 --leaders --bench 110,360 --fit 60,160 --procs 40 --chunk 48 --out $OUT/parity_frozen.json 2>&1 | tail -8
python3 tools/gpu_bench.py speed --n 384 --bench 110,360 --chunk 64 --out $OUT/speed_same110_b.json 2>&1 | tail -3
nvidia-smi --query-gpu=name,memory.used,utilization.gpu --format=csv
