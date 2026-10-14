#!/bin/bash
# one-time setup on a fresh machine / cloud session (Linux or macOS)
set -e; cd "$(dirname "$0")/.."
PY=${PY:-python3}
$PY -m pip install -q -r requirements.txt || $PY -m pip install -q --user -r requirements.txt
cp -n pipeline/avg/body_mesh.json pipeline/conformal/gpu/body_mesh.json 2>/dev/null || true   # the GPU-side rig reads its own copy (not in git)
mkdir -p .cache
$PY -c "import cadquery, OCP, trimesh, scipy, torch; print('deps ok: cadquery', cadquery.__version__)"
echo "next: python3 tools/build_maps.py  (only needed for fair_pipeline.sh / detail_local.py; slow on CPU)"
