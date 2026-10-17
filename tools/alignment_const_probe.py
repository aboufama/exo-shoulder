"""Alignment what-if probe: wear a row's frozen claim with ONE module-level constant of its model overridden in memory.

Use: a design's number rests on a catalogue assumption that is a constant in its model (e.g. an M2 ball link's socket
cone, CONE = 30 deg in docs/concepts/models/inband-rssr-knuckle-3r.py). This probe asks how much of the number lives
in that assumption, by wearing the SAME frozen shape (the row's best_params, or --params) with the constant set to a
stricter catalogue value. The model file, the benches and the row are never edited; the override lives only in this
process. The result is a measurement for a PROPOSAL (docs/ALIGNMENT.md section 4), never an input to a score.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_const_probe.py <id> bench|held NAME=VALUE [--params p.json]
        -> docs/alignment/remeasure/<id>_<wear>_<NAME><VALUE>.json
"""
import importlib.util, json, os, re, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROWS = os.path.join(REPO, "docs", "concepts", "rows")
MODELS = os.path.join(REPO, "docs", "concepts", "models")
REM = os.path.join(REPO, "docs", "alignment", "remeasure")


def main():
    a = sys.argv[1:]
    if len(a) < 3 or "=" not in a[2]: raise SystemExit(__doc__)
    rid, wear, kv = a[0], a[1], a[2]
    name, val = kv.split("=", 1); val = float(val)
    P = dict(json.load(open(os.path.join(ROWS, rid + ".json"))).get("best_params") or {})
    if "--params" in a: P.update(json.load(open(a[a.index("--params") + 1])))
    sp = importlib.util.spec_from_file_location("cp_" + re.sub(r"\W", "_", rid), os.path.join(MODELS, rid + ".py"))
    mod = importlib.util.module_from_spec(sp); sp.loader.exec_module(mod)
    if not hasattr(mod, name): raise SystemExit(f"{rid}: model has no module constant {name}")
    old = getattr(mod, name); setattr(mod, name, type(old)(val) if isinstance(old, (int, float)) else val)
    t = time.time()
    r = mod.frozen(P) if wear == "bench" else mod.frozen_held(P)
    keep = ("frozen", "fit_fast", "why", "audit", "th_margin", "cam", "contact_depth", "overhead")
    out = dict(id=rid, wear=wear, override={name: [old, val]}, params=P, **{k: r.get(k) for k in keep},
               secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1",
               git=subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip())
    os.makedirs(REM, exist_ok=True)
    path = os.path.join(REM, f"{rid}_{wear}_{name}{val:g}.json")
    json.dump(out, open(path, "w"), indent=1, default=float)
    print(json.dumps(dict(id=rid, wear=wear, override=out["override"], frozen=out["frozen"], why=out["why"],
                          cam={k: (out["cam"] or {}).get(k) for k in ("dK_lim", "why_lim")}, secs=out["secs"], out=os.path.relpath(path, REPO)), default=float))


if __name__ == "__main__":
    main()
