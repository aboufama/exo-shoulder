# Independent verification of the pin-knee massive GPU polish claim (farm job, one harness run per job):
#   bash docs/research/verify_gpuknee/run.sh <config> <fitbig|fit60|held|kin|taken> <margin|claimed> <out tag>
# Bench(110,360) fast cache 14f156cb6fc8 copied from the farm volume (or assembled from its parts) to the worker's /tmp,
# CB_EXACT=1 for every wear bench, CB_FOLD_MARGIN = the margin, the harnesses imported unchanged.
set -e
C=$1; PR=$2; MG=$3; TAG=$4; D=docs/research/verify_gpuknee
mkdir -p .cache/concept_bench /tmp/vgk
S=/runpod-volume/exo-farm/shared/bench/14f156cb6fc8
if [ ! -f .cache/concept_bench/14f156cb6fc8/meta.json ]; then
  if [ -f $S/meta.json ]; then
    python3 -c "
import fcntl, os, shutil
d = '/tmp/vgk/14f156cb6fc8'; os.makedirs(d, exist_ok=True)
with open('/tmp/vgk.lock', 'w') as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    if not os.path.exists(d + '/.ok'):
        for f in ('grid.npy', 'skins.npy', 'meta.json'): shutil.copyfile('$S/' + f, d + '/' + f + '.tmp'); os.replace(d + '/' + f + '.tmp', d + '/' + f)
        open(d + '/.ok', 'w').write('ok')
"
    ln -sfn /tmp/vgk/14f156cb6fc8 .cache/concept_bench/14f156cb6fc8
  else
    python3 tools/osn_polish.py assemble 110 360 osnp/b110_360 /tmp/osnpb
  fi
fi
ls -la .cache/concept_bench/ .cache/concept_bench/14f156cb6fc8/
P=$(python3 -c "import json,sys; print(json.dumps(json.load(open('$D/params.json'))['params'][sys.argv[1]]))" $C)
if [ "$MG" = "claimed" ]; then MG=$(python3 -c "import json,sys; print(json.load(open('$D/params.json'))['margins'][sys.argv[1]])" $C); fi
echo "config $C proto $PR margin $MG params $P"
export CB_EXACT=1 CB_FOLD_MARGIN=$MG OMP_NUM_THREADS=1 IGL_NUM_THREADS=1
if [ "$PR" = "kin" ] || [ "$PR" = "taken" ]; then
  python3 docs/concepts/verify/skin-normal-3r-pin-knee-continuity.py $PR fitbig $D/$TAG.json "$P"
else
  python3 docs/concepts/verify/skin-normal-3r-pin-knee-polish.py $PR $D/$TAG.json "$P"
fi
