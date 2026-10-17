"""Fast-bench screen (Bench(60,160) fast cache) of the repackaging switches of inband-rssr-knuckle-3r around one config.
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/inband_drive/screen.py '<base params json>' '<list of overrides json>' out.jsonl
Each line: the override, the 2 mm objective gap, plain gap, reach / in-band / contact, why, the drive's range and the
per-part in-band [share, median mm, n] of the drive parts (and hub 2 / link 1b for reference)."""
import importlib.util, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
sp = importlib.util.spec_from_file_location("ib_model_screen", os.path.join(REPO, "docs", "concepts", "models", "inband-rssr-knuckle-3r.py"))
IB = importlib.util.module_from_spec(sp); sp.loader.exec_module(IB)

base = json.loads(sys.argv[1]); over = json.loads(sys.argv[2]); outp = sys.argv[3]
B = CB.Bench(n_clip=60, n_ws=160)
with open(outp, "a") as fo:
    for ov in over:
        t = time.time(); P = dict(base, **ov)
        try:
            r = IB.bench_eval(B, P)
            pr = r.get("parts_ib14") or {}
            row = dict(ov=ov, gap=r["gap"], plain=(r.get("plain") or {}).get("gap"), near1=r.get("gap_near1"), reach=r["reach"], inband14=r["inband14"],
                       contact=r["contact"], honest=r.get("honest"), why=r.get("why"),
                       dK_lim=(r.get("cam") or {}).get("dK_lim"), why_lim=(r.get("cam") or {}).get("why_lim"),
                       boss=(r.get("cam") or {}).get("boss_level"), lev=(r.get("cam") or {}).get("lev_L1b"),
                       parts={k: pr.get(k) for k in ("crank", "rod", "rodends", "horn", "ear", "hub2", "L1b")}, secs=round(time.time() - t, 1))
        except Exception as e:
            row = dict(ov=ov, error=repr(e)[:400])
        fo.write(json.dumps(row, default=float) + "\n"); fo.flush()
        print(json.dumps(row, default=float), flush=True)
