"""posteromedial_seat driver (pre-registered in docs/research/posteromedial_seat.md): for each cell 'az,el' given, stage 0
(kinematic J3-seat seed on the FIT bench + both branches evaluated fast) then stage 1 (tools/concept_cma.py, near-1
objective, popsize 8, jobs 1, budget 360 s). Fit bench only; no claim-bench or held-out pose is read here.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/posteromedial_seat/run_cells.py -52.5,17.5 0,0 ...
"""
import importlib.util, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
MP = os.path.join(REPO, "docs", "concepts", "models", "posteromedial-knuckle-3r.py")
sp = importlib.util.spec_from_file_location("pm_model", MP); PM = importlib.util.module_from_spec(sp); sp.loader.exec_module(PM)
import concept_bench as CB
B = CB.Bench(n_clip=60, n_ws=160)
FREE = ("wd", "wa", "b3", "d_a1", "d_a2", "lE", "lc", "phib", "J3MIN", "a1max", "kK")
SCALES = dict(wd=6, wa=12, b3=0.1, d_a1=4, d_a2=4, lE=8, lc=4, phib=10, J3MIN=6, a1max=3, kK=0.3)
for cell in sys.argv[1:]:
    az, el = (float(x) for x in cell.split(",")); tag = f"az{az:g}_el{el:g}"; t0 = time.time()
    sd = PM.seed(az, el, top=3); best = None; evals = []
    top = sd[0]
    for br, ok in zip((1.0, -1.0), top["br_ok"]):
        if not ok: continue
        par = dict(az1=az, el1=el, wd=top["wd"], wa=top["wa"], br=br)
        B.reset(); p, r = PM.evaluate(B, par)
        e = dict(br=br, obj=r["gap"] + (0 if r.get("honest") else 100), near1=r.get("gap_near1"), plain=r.get("plain"), honest=r.get("honest"),
                 why=r.get("why"), seats=r.get("seats"))
        evals.append(e)
        if best is None or e["obj"] < best[0]: best = (e["obj"], par)
    json.dump(dict(cell=[az, el], seed=sd, evals=evals, start=best[1] if best else None, secs=round(time.time() - t0, 1)),
              open(os.path.join(HERE, f"seed_{tag}.json"), "w"), indent=1, default=float)
    print(tag, "seed", json.dumps(evals, default=float)[:600], flush=True)
    if best is None: continue
    x0 = {k: float(dict(PM._clamp(dict(PM.PARAMS, **best[1])))[k]) for k in FREE}
    base = dict(az1=az, el1=el, br=best[1]["br"])
    cmd = ["python3", os.path.join(REPO, "tools", "concept_cma.py"), MP, "--x0", json.dumps(x0), "--scales", json.dumps(SCALES),
           "--base", json.dumps(base), "--sigma", "0.3", "--popsize", "8", "--jobs", "1", "--budget-s", "360", "--seed", "1",
           "--out", os.path.join(HERE, f"cma_{tag}.json"), "--label", tag]
    subprocess.run(cmd, check=False, stdout=open(os.path.join(HERE, f"cma_{tag}.log"), "w"), stderr=subprocess.STDOUT)
    print(tag, "cma done", round(time.time() - t0), flush=True)
