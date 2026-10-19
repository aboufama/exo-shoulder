# exo-gpu-pinknee job 1 (after knee0's boot; the first run was cancelled: GNU nproc read OMP_NUM_THREADS=1): fresh code, then knee_run.sh
set -x
tar xf /workspace/exo-farm/gpu/code/.cache/gpu_knee/knee_code.tar -C /root/repo
bash /root/repo/pipeline/gpu_pod/knee_run.sh
