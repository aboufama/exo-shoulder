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
RUNS2 = [   # cma2: seeded from the focused ~75 deg sweep (res_rssr75.json), lead 2026-10-17 07:00: target stroke ~75
    ("r75a", "rssr", 11, dict(DY, La=21.623, s_arm=4.204, r_h=16.8264, beta=-132.0686, gam=10.2237, hl=2.8907, zr=2.1898, kK=1.7146, r_lobe=7.6066, smhi=16.8433)),
    ("r75b", "rssr", 12, dict(DY, La=24.4909, s_arm=4.1862, r_h=16.3269, beta=-138.8245, gam=16.0072, hl=2.4576, zr=4.7166, kK=1.9611, r_lobe=7.3765, smhi=16.8433)),
    ("r75c", "rssr", 13, dict(DY, La=18.6197, s_arm=4.1759, r_h=16.4402, beta=-123.2638, gam=13.3771, hl=2.1949, zr=1.0722, kK=1.7537, r_lobe=7.7126, smhi=16.8433)),
    ("r75d", "rssr", 14, dict(bk1=32.0, bk2=48.0, a1max=75.0, La=22.0352, s_arm=4.4924, r_h=16.0364, beta=-139.9978, gam=17.4855, hl=2.925, zr=1.5, kK=1.6, r_lobe=7.402, smhi=16.8433)),
]
# cma3: the same seeds held at a long stroke (LS_STROKE_MIN 65: a config whose drive range is shorter scores +100), on the
# round-9 2 mm objective and on the 1 mm one (LS_OBJ): cma1 showed the free search trades the stroke away
RUNS3 = [
    ("s65n2a", "rssr", 21, RUNS2[0][3], {"LS_STROKE_MIN": "65", "LS_OBJ": "near2"}),
    ("s65n2b", "rssr", 22, RUNS2[1][3], {"LS_STROKE_MIN": "65", "LS_OBJ": "near2"}),
    ("s65n2d", "rssr", 24, RUNS2[3][3], {"LS_STROKE_MIN": "65", "LS_OBJ": "near2"}),
    ("s65n1a", "rssr", 31, RUNS2[0][3], {"LS_STROKE_MIN": "65", "LS_OBJ": "near1"}),
    ("s65n1b", "rssr", 32, RUNS2[1][3], {"LS_STROKE_MIN": "65", "LS_OBJ": "near1"}),
]
# cma4 (ATTRIBUTION, never a claim): the drive's own metal deleted (LS_GHOST=1), stroke held >= 65: what the long stroke is
# worth on the real chain (hubs, links, knee, cuff, the greedy level fit) if the drive parked perfectly
RUNS4 = [
    ("g65a", "rssr", 41, RUNS2[0][3], {"LS_STROKE_MIN": "65", "LS_OBJ": "near2", "LS_GHOST": "1"}),
    ("g65d", "rssr", 44, RUNS2[3][3], {"LS_STROKE_MIN": "65", "LS_OBJ": "near2", "LS_GHOST": "1"}),
]
RUNS = [
    ("rs1", "rssr", 1, dict(DY, La=17.5685, s_arm=4.0646, r_h=15.3454, beta=-126.3626, gam=26.7611, hl=2.5388, zr=3.4996, kK=1.7034, r_lobe=8.0629, smhi=16.8433)),
    ("rs2", "rssr", 2, dict(DY, La=22.4301, s_arm=4.6007, r_h=16.1034, beta=-145.2303, gam=51.0384, hl=0.3119, zr=3.2236, kK=1.6825, r_lobe=7.3108, smhi=16.8433)),
    ("rs3", "rssr", 3, dict(DY, La=20.0, s_arm=4.5, r_h=15.0, beta=-110.0, gam=10.0, hl=2.5, zr=3.0, kK=1.8, r_lobe=7.8, smhi=16.8433)),
    ("ns1", "nose", 4, dict(DY, g=2.9101, beta=-178.9001, r_c=17.1802, lift=2.329, hl=1.6266, zr=4.3117, kK=1.6356, s_arm=4.0108, r_lobe=7.7695, nose_r=1.0203, smhi=16.8433)),
]
jobs = []
SEL = RUNS4 if name.startswith("cma4") else RUNS3 if name.startswith("cma3") else [r + ({},) for r in (RUNS2 if name.startswith("cma2") else RUNS)]
for tag, drive, seed, x0, xenv in SEL:
    sc = RS_SC if drive == "rssr" else CAM_SC
    sc = {k: v for k, v in sc.items() if k in x0}
    lab = f"ls-{name}-{tag}"
    cmd = (f"mkdir -p {OUT} && python3 tools/concept_cma.py {MODEL} --x0 '{json.dumps(x0)}' --scales '{json.dumps(sc)}' "
           f"--sigma 0.5 --popsize 8 --jobs 2 --budget-s {budget:.0f} --max-gen 400 --seed {seed} --label {lab} "
           f"--out {OUT}/cma_{name}_{tag}.json > {OUT}/cma_{name}_{tag}.log 2>&1; tail -3 {OUT}/cma_{name}_{tag}.log")
    jobs.append(dict(tag=lab, cmd=cmd, out=[f"{OUT}/cma_{name}_{tag}*"], env=dict({"OMP_NUM_THREADS": "1", "IGL_NUM_THREADS": "1", "LS_DRIVE": drive}, **xenv),
                     timeout=budget + 600))
json.dump(jobs, open(os.path.join(HERE, "farm", f"jobs_{name}.json"), "w"), indent=1)
print(len(jobs), "jobs ->", os.path.join(HERE, "farm", f"jobs_{name}.json"))
