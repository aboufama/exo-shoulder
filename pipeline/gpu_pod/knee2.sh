# exo-gpu-pinknee job 2: port v2 code, then knee_run2.sh
set -x
tar xf /workspace/exo-farm/gpu/code/.cache/gpu_knee/knee_code2.tar -C /root/repo
bash /root/repo/pipeline/gpu_pod/knee_run2.sh
