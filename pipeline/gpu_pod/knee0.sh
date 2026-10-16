# exo-gpu-pinknee boot + wait job (first job on the pod, spool exo-farm/gpuk): torch with Blackwell kernels, CPU-kit deps
# for the parity reference, the repo tree (exo-farm/gpu/repo.tar), both bench grids + skins on local disk, then WAIT for
# the pin-knee port's code tarball (exo-farm/gpuk/code/knee_code.tar, dropped by a farm job) and run its knee_run.sh
set -x
K=/workspace/exo-farm/gpuk; OUT=$K/out/knee; mkdir -p $OUT $K/code
pip install -q "torch==2.7.1" --index-url https://download.pytorch.org/whl/cu128 2>&1 | tail -2
pip install -q scipy==1.13.1 libigl==2.6.3 2>&1 | tail -2
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
mkdir -p /root/repo && tar xf /workspace/exo-farm/gpu/repo.tar -C /root/repo
mkdir -p /root/bench/14f156cb6fc8 /root/bench/0089c747c10f
cp /workspace/exo-farm/shared/bench/14f156cb6fc8/{grid.npy,meta.json} /root/bench/14f156cb6fc8/
cp /workspace/exo-farm/shared/bench/14f156cb6fc8/skins.npy /root/bench/14f156cb6fc8/ 2>/dev/null || echo "no skins for 110/360"
cp /workspace/exo-farm/cas/e9/e99c311e213cce4add4e68f1324545457eb4fc377983e88a24c02131db0f2aa3 /root/bench/0089c747c10f/grid.npy
cp /workspace/exo-farm/cas/c3/c3bb1497a4c905d44f5e3383b3217b7b1ca5018dfb471d5f9dc1f74d1040f41c /root/bench/0089c747c10f/meta.json
cp /workspace/exo-farm/cas/33/3305343863fd06d6e12e6c34d3d4a630f741c84a4cccd5a42a7e5e275a2379a1 /root/bench/0089c747c10f/skins.npy
cd /root/repo && rm -rf .cache/concept_bench && mkdir -p .cache/concept_bench
ln -sfn /root/bench/14f156cb6fc8 .cache/concept_bench/14f156cb6fc8; ln -sfn /root/bench/0089c747c10f .cache/concept_bench/0089c747c10f
ls -la /root/bench/*/; nproc; free -g | head -2; cat /sys/fs/cgroup/memory.max 2>/dev/null; nvidia-smi -L
echo "booted $(date -u +%FT%TZ)" >> $OUT/boot.txt
for i in $(seq 1 1440); do [ -f $K/code/knee_code.tar ] && break; sleep 5; done
ls -la $K/code/
tar xf $K/code/knee_code.tar -C /root/repo && cp $K/code/knee_code.tar $K/code/knee_code.used.tar && rm -f $K/code/knee_code.tar
bash /root/repo/pipeline/gpu_pod/knee_run.sh
