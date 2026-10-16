# gks5 (farm job, through the volume): deploy driver v4 (dynamic deadlines from $R/deadlines.json, CMA resume after a
# restart, the terminated RTX 4090 pod's unfinished points re-run by a live pod) and restart the pods on it; budget
# schedule (lead, 10:08 UTC: balance $10.44, hold 11:40, the farm needs the rest): Sobol <= 10:38, CMA <= 10:58,
# verification <= 11:25 UTC.
V=/runpod-volume/exo-farm; R=$V/gpuk/out/gks1
for i in $(seq 1 60); do [ -f $R/restart.txt ] && break; sleep 5; done; cat $R/restart.txt
mkdir -p $R/override/tools
cp tools/gpu_knee_search.py $R/override/tools/gpu_knee_search.py.v4new && mv -f $R/override/tools/gpu_knee_search.py.v4new $R/override/tools/gpu_knee_search.py
grep -c "class Deadlines" $R/override/tools/gpu_knee_search.py
echo 3dt2e37357shr8 > $R/dead.txt
echo '{"sob": 1792147080, "cma": 1792148280, "ver": 1792149900}' > $R/deadlines.json.new && mv -f $R/deadlines.json.new $R/deadlines.json
for s in gpuk1 gpuk3; do mkdir -p $V/$s/queue; cp pipeline/gpu_pod/gks2.sh $V/$s/queue/03_gks2.sh.new && mv -f $V/$s/queue/03_gks2.sh.new $V/$s/queue/03_gks2.sh; touch $V/$s/cancel; done
echo "v4 restart of gpuk1 gpuk3 $(date -u +%FT%TZ)" >> $R/restart.txt
for i in $(seq 1 96); do grep -q booted $R/log_mueo1pc15i6vyk.txt 2>/dev/null && break; sleep 5; done
sleep 20; mkdir -p $V/gpuk4/queue; cp pipeline/gpu_pod/gks2.sh $V/gpuk4/queue/03_gks2.sh.new && mv -f $V/gpuk4/queue/03_gks2.sh.new $V/gpuk4/queue/03_gks2.sh; touch $V/gpuk4/cancel
echo "v4 restart of gpuk4 $(date -u +%FT%TZ)" >> $R/restart.txt
sleep 40
for s in gpuk1 gpuk3 gpuk4; do echo == $s; ls $V/$s/queue $V/$s/out; tail -3 $V/$s/pod.log; done
for f in $R/log_*.txt; do echo == $f; grep -v '^+' $f | grep -v '^  ' | tail -10 | cut -c1-300; done
ls $R; wc -l $R/sobol_*.jsonl $R/cma_*.jsonl 2>/dev/null; ls $R/claims | wc -l; cat $R/restart.txt
