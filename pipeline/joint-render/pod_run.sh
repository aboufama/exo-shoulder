#!/bin/bash
# on the pod: install deps, render frames across all GPUs (one Blender per GPU, interleaved), encode the MP4
set -e
cd /workspace/job
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq && apt-get install -y -qq libxrender1 libxi6 libxkbcommon0 libsm6 libgl1 libxxf86vm1 libxfixes3 libegl1 ffmpeg >/dev/null
pip install -q bpy==4.2.0 >/dev/null
echo SETUP DONE
