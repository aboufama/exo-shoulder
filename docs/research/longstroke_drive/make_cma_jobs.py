"""farm CMA jobs for longstroke-slipper-knuckle-3r (tools/concept_cma.py, Bench(60,160) fast, 2 mm near-touch objective).
    python3 docs/research/longstroke_drive/make_cma_jobs.py <batch-name> <budget_s>  -> farm/jobs_<batch-name>.json"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = "docs/research/longstroke_drive/farm"
name = sys.argv[1] if len(sys.argv) > 1 else "cma1"; budget = float(sys.argv[2]) if len(sys.argv) > 2 else 1500
MODEL = "docs/concepts/models/longstroke-slipper-knuckle-3r.py"
DY = {"bk1": 28.0, "bk2": 50.0, "a1max": 73.0}
RS_SC = {"La": 3.0, "s_arm": 0.5, "r_h": 2.0, "beta": 15.0, "gam": 15.0, "hl": 0.8, "zr": 1.0, "kK": 0.25, "r_lobe": 0.4,
         "bk1": 2.0, "bk2": 3.0, "a1max": 3.0, "smhi": 2.0}
CAM_SC = {"g": 0.3, "beta": 8.0, "r_c": 1.5, "lift": 0.8, "hl": 0.6, "zr": 1.0, "kK": 0.25, "s_arm": 0.5, "r_lobe": 0.4,
          "nose_r": 0.15, "bk1": 2.0, "bk2": 3.0, "a1max": 3.0, "smhi": 2.0}
RUNS = [
    ("rs1", "rssr", 1, dict(DY, La=17.5685, s_arm=4.0646, r_h=15.3454, beta=-126.3626, gam=26.7611, hl=2.5388, zr=3.4996, kK=1.7034, r_lobe=8.0629, smhi=16.8433)),
    ("rs2", "rssr", 2, dict(DY, La=22.4301, s_arm=4.6007, r_h=16.1034, beta=-145.2303, gam=51.0384, hl=0.3119, zr=3.2236, kK=1.6825, r_lobe=7.3108, smhi=16.8433)),
    ("rs3", "rssr", 3, dict(DY, La=20.0, s_arm=4.5, r_h=15.0, beta=-110.0, gam=10.0, hl=2.5, zr=3.0, kK=1.8, r_lobe=7.8, smhi=16.8433)),
    ("ns1", "nose", 4, dict(DY, g=2.9101, beta=-178.9001, r_c=17.1802, lift=2.329, hl=1.6266, zr=4.3117, kK=1.6356, s_arm=4.0108, r_lobe=7.7695, nose_r=1.0203, smhi=16.8433)),
]
jobs = []
for tag, drive, seed, x0 in RUNS:
    sc = RS_SC if drive == "rssr" else CAM_SC
    sc = {k: v for k, v in sc.items() if k in x0}
    lab = f"ls-{name}-{tag}"
    cmd = (f"mkdir -p {OUT} && python3 tools/concept_cma.py {MODEL} --x0 '{json.dumps(x0)}' --scales '{json.dumps(sc)}' "
           f"--sigma 0.5 --popsize 8 --jobs 2 --budget-s {budget:.0f} --max-gen 400 --seed {seed} --label {lab} "
           f"--out {OUT}/cma_{name}_{tag}.json > {OUT}/cma_{name}_{tag}.log 2>&1; tail -3 {OUT}/cma_{name}_{tag}.log")
    jobs.append(dict(tag=lab, cmd=cmd, out=[f"{OUT}/cma_{name}_{tag}*"], env={"OMP_NUM_THREADS": "1", "IGL_NUM_THREADS": "1", "LS_DRIVE": drive},
                     timeout=budget + 600))
json.dump(jobs, open(os.path.join(HERE, "farm", f"jobs_{name}.json"), "w"), indent=1)
print(len(jobs), "jobs ->", os.path.join(HERE, "farm", f"jobs_{name}.json"))
