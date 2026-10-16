# exo-gpu-bench: unpack the repo tree a farm job left on the volume, link the bench caches, CPU-kit deps for parity
set -x
mkdir -p /root/repo && tar xf /workspace/exo-farm/gpu/repo.tar -C /root/repo
mkdir -p /root/repo/.cache/concept_bench
ln -sfn /workspace/exo-farm/shared/bench/14f156cb6fc8 /root/repo/.cache/concept_bench/14f156cb6fc8
ln -sfn /workspace/exo-farm/gpu/bench/0089c747c10f /root/repo/.cache/concept_bench/0089c747c10f
ls -la /root/repo/.cache/concept_bench/*/
pip install -q scipy==1.13.1 libigl==2.6.3 2>&1 | tail -2
cd /root/repo && python3 -c "import sys; sys.path.insert(0,'tools'); import concept_bench as CB; B = CB.Bench(110,360); print(B.mode, B.key); B2 = CB.Bench(60,160); print(B2.mode)"
nproc; free -g | head -2
