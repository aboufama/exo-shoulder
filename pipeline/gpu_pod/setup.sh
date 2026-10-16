# exo-gpu-bench setup job (runs on the pod, cwd = /workspace/exo-farm/gpu): a torch build with Blackwell (sm_120) kernels
set -x
nvidia-smi
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available())"
pip install -q --upgrade "torch==2.7.1" --index-url https://download.pytorch.org/whl/cu128 2>&1 | tail -3
python3 -c "import torch, time; print(torch.__version__, torch.cuda.get_device_name(0)); x = torch.randn(4096, 4096, device='cuda'); torch.cuda.synchronize(); t = time.time(); [x @ x for _ in range(20)]; torch.cuda.synchronize(); print('matmul TFLOPS', 20 * 2 * 4096**3 / (time.time() - t) / 1e12)"
ls -la /workspace/exo-farm/shared/bench/ /workspace/exo-farm/shared/bench/14f156cb6fc8/ 2>&1 | head -20
cat /workspace/exo-farm/shared/bench/14f156cb6fc8/meta.json
nproc; free -g | head -2; df -h /tmp | tail -1
