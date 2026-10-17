#!/bin/bash
# one-time setup on a fresh machine / cloud session (Linux or macOS)
set -e; cd "$(dirname "$0")/.."
PY=${PY:-python3}
# cloud containers ship Python 3.13, which the pinned scipy 1.13 / cadquery-ocp 7.7 have no wheels for (scipy then tries a
# Fortran build and fails): use a uv-managed 3.12 venv (the farm's version) and put python3 / python wrappers first on PATH
if [ -z "$EXO_NO_VENV" ] && $PY -c 'import sys; sys.exit(sys.version_info < (3, 13))' && command -v uv >/dev/null && [ -x /usr/bin/python3.12 ]; then
  export UV_LINK_MODE=copy
  [ -x /opt/exo-venv/bin/python ] || uv venv -q -p /usr/bin/python3.12 /opt/exo-venv
  grep -v torch requirements.txt | sed 's/#.*//' | grep . > /tmp/exo_req.txt
  uv pip install -q --python /opt/exo-venv/bin/python -r /tmp/exo_req.txt libigl pip
  uv pip install -q --python /opt/exo-venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu
  mkdir -p "$HOME/.local/bin"   # a wrapper, not a symlink: a symlinked venv python loses its site-packages
  for n in python3 python; do printf '#!/bin/sh\nexec /opt/exo-venv/bin/python "$@"\n' > "$HOME/.local/bin/$n"; chmod +x "$HOME/.local/bin/$n"; done
  PY=/opt/exo-venv/bin/python
else
  $PY -m pip install -q -r requirements.txt || $PY -m pip install -q --user -r requirements.txt
  $PY -m pip install -q libigl
fi
cp -n pipeline/avg/body_mesh.json pipeline/conformal/gpu/body_mesh.json 2>/dev/null || true   # the GPU-side rig reads its own copy (not in git)
mkdir -p .cache
$PY -c "import cadquery, OCP, trimesh, scipy, torch; print('deps ok: cadquery', cadquery.__version__)"
echo "next: python3 tools/build_maps.py  (only needed for fair_pipeline.sh / detail_local.py; slow on CPU)"
