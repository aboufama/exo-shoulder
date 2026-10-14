#!/bin/zsh
# $1 design dir, $2 subtitle, $3 CLIP_BACK_MAX (0 = none): 4 processes x 2 clips, then merge
cd ${0:a:h}; rm -f $1/clips_part_*.json
for part in 0,1 2,3 4,5 6,7; do
  CLIPS_ONLY=$part CLIP_BACK_MAX=$3 CLIP_KEYS=${CLIP_KEYS:-clip_keys.json} ${PY:-python3} -u -W ignore make_clips_full.py $1 "$2" > $1/clips_$part.out 2>&1 &
done
wait
${PY:-python3} - $1 <<'PY'
import json, sys, glob, os
d = sys.argv[1]; parts = sorted(glob.glob(os.path.join(d, "clips_part_*.json")), key=lambda p: int(p.split("_part_")[1].split("_")[0]))
J = [json.load(open(p)) for p in parts]; out = dict(J[0], clips=[c for j in J for c in j["clips"]])
json.dump(out, open(os.path.join(d, "clips.json"), "w"), separators=(",", ":")); print("merged", len(out["clips"]), "clips")
PY
cat $1/clips_*.out | grep -E "frames|Error"
echo done > $1/DONE
