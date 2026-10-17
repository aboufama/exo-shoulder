"""claim columns on the farm for longstroke-slipper-knuckle-3r (the model's own 'claims' mode: one process per column):
frozen exact Bench(110,360), held out (952), continuity flood, for the pick(s) and the controls.
    python3 docs/research/longstroke_drive/make_claim_jobs.py <name> '<[{"tag","drive","mode","params"}]>'"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = "docs/research/longstroke_drive/farm"
name = sys.argv[1]; cols = json.loads(sys.argv[2])
MODEL = "docs/concepts/models/longstroke-slipper-knuckle-3r.py"
jobs = []
for c in cols:
    lab = f"ls-{name}-{c['tag']}"
    one = json.dumps([dict(c, tag=c["tag"])]).replace("'", "'\\''")
    cmd = f"mkdir -p {OUT}/{name} && python3 {MODEL} claims '{one}' {OUT}/{name} > {OUT}/{name}/{c['tag']}.run.log 2>&1; tail -2 {OUT}/{name}/{c['tag']}.log"
    jobs.append(dict(tag=lab, cmd=cmd, out=[f"{OUT}/{name}/{c['tag']}*"], env={"OMP_NUM_THREADS": "1", "IGL_NUM_THREADS": "1"}, timeout=3600))
json.dump(jobs, open(os.path.join(HERE, "farm", f"jobs_{name}.json"), "w"), indent=1)
print(len(jobs), "jobs")
