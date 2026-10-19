#!/bin/bash
# stage 1 (amendment 5): CMA on one cell's stage-0 seed. usage: stage1.sh <stage0 json> <tag>
cd /home/user/exo-shoulder
S=$1; TAG=$2
X0=$(python3 -c "
import json;d=json.load(open('$S'));s=d['seed'][0]
print(json.dumps(dict(wd=s['wd'],wa=s['wa'],d_a1=0.0,d_a2=0.0,beta=-176.684,g=2.3934,r_c=15.3739,lift=0.7882,lE=97.1443,lc=24.3508,phib=-91.8041,J3MIN=-111.9036)))")
BASE=$(python3 -c "
import json;d=json.load(open('$S'));s=d['seed'][0]
print(json.dumps(dict(az1=d['cell'][0],el1=d['cell'][1],br=s['br'])))")
SC='{"wd":6,"wa":12,"d_a1":4,"d_a2":4,"beta":6,"g":0.25,"r_c":1.5,"lift":0.8,"lE":8,"lc":4,"phib":10,"J3MIN":6}'
OMP_NUM_THREADS=1 nice -n 10 python3 tools/concept_cma.py docs/concepts/models/posteromedial-knuckle-3r.py --x0 "$X0" --scales "$SC" --base "$BASE" \
  --sigma 0.3 --popsize 8 --jobs 1 --budget-s ${3:-1200} --seed 1 --out docs/research/posteromedial_seat/cma_$TAG.json --label $TAG \
  > docs/research/posteromedial_seat/cma_$TAG.log 2>&1
