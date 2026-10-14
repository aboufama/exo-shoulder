#!/bin/zsh
# design json (one design dict: az el a1 a2 a3 branch order [G]) -> envelope -> full assembly -> clips -> viewer
set -e
cd ${0:a:h}; DESIGN=$1; NAME=${2:-final}; G=${3:-10}
${PY:-python3} -W ignore - $DESIGN $G <<'PY'
import json, sys, math, os
sys.path.insert(0, "../avg"); os.chdir("../avg"); os.environ["H_LEN"] = "325"
import conformal as CF, design_search as D
d = json.load(open(sys.argv[1])); G = float(sys.argv[2]); fix = json.load(open("fix_w_tea.json"))
def bvec(az, el): return [-math.cos(el * D.D2R) * math.cos(az * D.D2R), math.sin(el * D.D2R), math.cos(el * D.D2R) * math.sin(az * D.D2R)]
dd = dict(b=bvec(d["az"], d["el"]), az=d["az"], el=d["el"], a1=d["a1"], a2=d["a2"], a3=d["a3"], delta=fix["delta"], waz=fix["waz"], branch=d["branch"], order=tuple(d["order"]))
r = CF.export_envelope(dd, G=G, out="../conformal/envelope_final.json")
print("envelope: cov %.1f%% gap p50 %.1f p90 %.1f per-link %s q_rest %.0f" % (100 * r["cov"], r["gap_p50"], r["gap_p90"], [round(x, 1) for x in r["per_link_p50"]], r["q_rest"]))
PY
${PY:-python3} -u -W ignore build_full_conformal.py envelope_final.json out_$NAME > build_$NAME.out 2>&1; tail -3 build_$NAME.out
D=../full-exo/designs/$NAME; rm -rf $D; mkdir -p $D; cp -r out_$NAME/exo.glb out_$NAME/shoulder $D/; cp out_$NAME/full_exo.step out_$NAME/bottom_mod.step $D/
cd ../full-exo; ./run_clips_split.sh designs/$NAME "average adult · 1.75 m · conformal shoulder" 0 > designs/$NAME/split.out 2>&1; cat designs/$NAME/split.out
