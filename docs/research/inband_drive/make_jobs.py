"""farm job files for docs/research/inband_drive (tools/cloud_run.py batch).
    python3 docs/research/inband_drive/make_jobs.py attr|cma|claim <name> [budget_s]  -> docs/research/inband_drive/farm/jobs_<name>.json
attr : per-part attribution (attribute.py) of the reference configs, bench + held, one job each
cma  : tools/concept_cma.py runs of inband-rssr-knuckle-3r (Bench(60,160) fast, 2 mm near-touch objective, law held steep)
claim: the frozen claim columns (frozen exact Bench(110,360), held out, flood, attribution) of the picks (picks.json)"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = "docs/research/inband_drive/farm"
kind = sys.argv[1]; name = sys.argv[2]; budget = float(sys.argv[3]) if len(sys.argv) > 3 else 1500
MODEL = "docs/concepts/models/inband-rssr-knuckle-3r.py"; LSM = "docs/concepts/models/longstroke-slipper-knuckle-3r.py"
K30 = dict(La=25.7026, s_arm=4.0, r_h=15.491, beta=-147.3923, gam=22.4633, hl=2.929, zr=2.091, r_lobe=8.5, bk1=30.0377, bk2=42.9378,
           a1max=67.9755, smhi=15.2738, kK=3.0)
K27B = dict(La=22.8723, s_arm=4.0, r_h=15.9448, beta=-149.8132, gam=29.1695, hl=2.27, zr=1.5851, kK=2.7, r_lobe=8.4846, bk1=28.7724,
            bk2=41.9799, a1max=60.8797, smhi=13.4632)
ENV = {"OMP_NUM_THREADS": "1", "IGL_NUM_THREADS": "1", "LS_DRIVE": "rssr", "CB_QUIET_EXACT": "1"}
jobs = []
if kind == "attr":
    for tag, P in (("k30", K30), ("k27b", K27B)):
        for which in ("bench", "held"):
            o = f"{OUT}/{name}/attr_{tag}_{which}.json"
            cmd = (f"mkdir -p {OUT}/{name} && CB_EXACT=1 python3 docs/research/inband_drive/attribute.py '{json.dumps(P)}' {which} {o} {LSM} "
                   f"> {OUT}/{name}/attr_{tag}_{which}.log 2>&1; tail -c 1500 {OUT}/{name}/attr_{tag}_{which}.log")
            jobs.append(dict(tag=f"ib-{name}-{tag}-{which}", cmd=cmd, out=[f"{OUT}/{name}/attr_{tag}_{which}*"], env=ENV, timeout=2400))
elif kind == "cma":
    runs = json.load(open(os.path.join(HERE, "farm", f"runs_{name}.json")))
    for r in runs:
        lab = f"ib-{name}-{r['tag']}"
        sc = r["scales"]
        cmd = (f"mkdir -p {OUT} && python3 tools/concept_cma.py {MODEL} --x0 '{json.dumps(r['x0'])}' --scales '{json.dumps(sc)}' "
               f"--base '{json.dumps(r.get('base', {}))}' --sigma {r.get('sigma', 0.5)} --popsize 8 --jobs 2 --budget-s {budget:.0f} --max-gen 400 --seed {r['seed']} --label {lab} "
               f"--out {OUT}/cma_{name}_{r['tag']}.json > {OUT}/cma_{name}_{r['tag']}.log 2>&1; tail -3 {OUT}/cma_{name}_{r['tag']}.log")
        jobs.append(dict(tag=lab, cmd=cmd, out=[f"{OUT}/cma_{name}_{r['tag']}*"], env=dict(ENV, **r.get("env", {})), timeout=budget + 600))
elif kind == "claim":
    cl = json.load(open(os.path.join(HERE, "farm", f"claims_{name}.json")))
    for c in cl:
        o = f"{OUT}/{name}"
        cmd = (f"mkdir -p {o} && python3 {MODEL} claims '{json.dumps([c])}' {o} > {o}/{c['tag']}.run.log 2>&1; tail -c 2500 {o}/{c['tag']}.log")
        jobs.append(dict(tag=f"ib-{name}-{c['tag']}", cmd=cmd, out=[f"{o}/{c['tag']}*"], env=ENV, timeout=3000))
os.makedirs(os.path.join(HERE, "farm"), exist_ok=True)
json.dump(jobs, open(os.path.join(HERE, "farm", f"jobs_{name}.json"), "w"), indent=1)
print(len(jobs), "jobs ->", os.path.join(HERE, "farm", f"jobs_{name}.json"))
