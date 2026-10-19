# gks6 (farm job): wait until the pin-knee search's verification is done (every job in verify_jobs.json has its output,
# or 11:36 UTC), then digest the run directory on the volume into docs/research/golden/gks1_digest.json (+ _all.npz)
V=/runpod-volume/exo-farm; R=$V/gpuk/out/gks1; END=$(date -d "11:36" +%s)
while [ $(date +%s) -lt $END ]; do
  if [ -f $R/verify_jobs.json ]; then
    n=$(python3 -c "import json,os; j=json.load(open('$R/verify_jobs.json'))['jobs']; print(sum(1 for x in j if not os.path.exists('$R/verify/'+x['id']+'.json')))")
    echo "$(date -u +%T) verify outputs missing: $n"; [ "$n" = "0" ] && break
  else echo "$(date -u +%T) no verify_jobs.json yet"; fi
  sleep 30
done
mkdir -p docs/research/golden
python3 tools/gpu_knee_search.py digest $R docs/research/golden/gks1_digest.json
ls -la docs/research/golden/gks1_digest*; cat $R/restart.txt; for f in $R/log_*.txt; do echo == $f; grep -v '^+' $f | grep -v '^  ' | tail -6 | cut -c1-300; done
