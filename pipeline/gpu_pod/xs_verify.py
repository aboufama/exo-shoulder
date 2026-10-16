"""exo-gpu-bench exhaustive search, last step (runs on each pod's CPUs, the CPU kit = the outside judge of the GPU port):
merge both pods' CMA basins (and the screens' best rows), take the 10 best DISTINCT configs by the GPU plain gap, and run
`tools/zc_frontier.py frozen` on this pod's share (index % nparts == part): the shape fitted on Bench(110,360) FAST
(= the CPU fast number) worn on Bench(110,360) EXACT (CB_EXACT=1), plus the verifier protocol (fit Bench(60,160) fast ->
wear Bench(110,360) exact) - the zc model's checks + docs/concepts/verify/spine-parked-j2-3r.py top_check at O20 / margin 5.

    python3 pipeline/gpu_pod/xs_verify.py OUTDIR PART NPARTS [--top 10] [--procs 5]
"""
import json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

REPO = "/root/repo"
sys.path.insert(0, os.path.join(REPO, "tools"))


def main():
    out, part, nparts = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 10
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv else 5
    import gpu_bench as GB
    rows = []
    for k in range(nparts):
        f = os.path.join(out, f"cma_p{k}.json")
        if os.path.exists(f):
            for b in json.load(open(f))["basins"]:
                r = dict(b["best"]); r["src"] = f"cma_p{k}/basin{b['basin']}"; rows.append(r)
        f = os.path.join(out, f"screen_p{k}.json")
        if os.path.exists(f):
            for r in json.load(open(f))["rows"][:200]:
                rows.append(dict(r, src=f"screen_p{k}"))
    rows = [r for r in rows if r.get("params") and r.get("honest")]
    E = GB.distinct(rows, top, key="gap")
    json.dump(E, open(os.path.join(out, "verify_pick.json"), "w"), indent=1, default=float)
    mine = [(i, e) for i, e in enumerate(E) if i % nparts == part]
    vd = os.path.join(out, "verify"); os.makedirs(vd, exist_ok=True)
    env = dict(os.environ, CB_EXACT="1", OMP_NUM_THREADS="1", CB_QUIET_EXACT="1",
               IGL_NUM_THREADS=str(max(1, (os.cpu_count() or 8) // max(1, len(mine)))))
    env.pop("GB_EXACT_OUTSIDE", None)

    def run(ie):
        i, e = ie; p = {k: e["params"][k] for k in ("az", "el", "a1", "a2", "wd", "wa", "sigma", "inv2", "inv3", "q", "end_extra")}
        t = time.time(); o = os.path.join(vd, f"v{i:02d}.json")
        r = subprocess.run([sys.executable, "tools/zc_frontier.py", "frozen", json.dumps(p), o], cwd=REPO, env=env,
                           capture_output=True, text=True)
        open(os.path.join(vd, f"v{i:02d}.log"), "w").write(r.stdout[-6000:] + "\n" + r.stderr[-6000:])
        print(f"verify {i}: gpu gap {e.get('gap')} near {e.get('near')} -> rc {r.returncode} ({time.time() - t:.0f} s)", flush=True)
        print(r.stdout[-1500:], flush=True)

    with ThreadPoolExecutor(min(procs, max(1, len(mine)))) as ex:
        list(ex.map(run, mine))


if __name__ == "__main__":
    main()
