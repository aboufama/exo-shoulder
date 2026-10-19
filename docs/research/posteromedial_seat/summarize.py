"""summary of the stage-1 CMA files: per file, configs, honest count, best objective and its report (fit bench only)"""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for f in sorted(glob.glob(os.path.join(HERE, "cma_*.json"))):
    try: L = json.load(open(f))
    except Exception: continue
    ok = [e for e in L if "report" in e]; hon = [e for e in ok if e["report"].get("honest")]
    b = min(ok, key=lambda e: e["obj"]) if ok else None
    print(os.path.basename(f), "n", len(L), "honest", len(hon), "best obj", b and round(b["obj"], 2))
    if b:
        r = b["report"]; p = b["params"]
        print("  near1", r.get("gap_near1"), "plain", r.get("plain"), "why", r.get("why"))
        print("  seats", r.get("seats"))
        print("  drive", {k: p.get(k) for k in ("beta", "g", "r_c", "lift")}, "knee", {k: p.get(k) for k in ("lE", "lc", "phib", "J3MIN")})
