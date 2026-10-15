"""Every judged design over time, for the dashboard (nothing re-run). One row per design dir that has at least one
judge output (score.json = R1-aim/R3; score_14mm.json = R1/R4; judge/workspace.json = R16; judge/part_contact.json =
R6; judge/dynamics.json = R17), complete or partial (column 'judges' lists which ran). Time = the commit that first
added its score.json, else the file's mtime (built and judged but not committed yet). <= 4 DOF only.
Also --evals: every band-evaluator DETAIL result (pipeline/conformal/gpu_client/band_eval_*.json) as a 'search
estimate' row (evaluator in-band at 14 mm, follow, workspace share, Raise overhead follow; measurement version noted).
    python3 tools/judged_history.py [extra designs dir ...] > judged.json
    python3 tools/judged_history.py --evals > evals.json"""
import datetime, glob, json, os, subprocess, sys
REPO = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
def load(p):
    try: return json.load(open(p))
    except Exception: return None
def first_commit(path):
    t = subprocess.run(["git", "-C", REPO, "log", "--diff-filter=A", "--format=%cI", "--", path], capture_output=True, text=True).stdout.split()
    return t[-1] if t else None
def mtime(p): return datetime.datetime.fromtimestamp(os.path.getmtime(p), datetime.timezone.utc).isoformat(timespec="seconds")
def designs(dirs):
    rows, seen = [], set()
    for D in dirs:
        for n in sorted(os.listdir(D)):
            dd = os.path.join(D, n)
            if n in seen or not os.path.isdir(dd): continue
            s, s14, dj = load(f"{dd}/score.json"), load(f"{dd}/score_14mm.json"), load(f"{dd}/design.json") or {}
            ws, pc, dy = load(f"{dd}/judge/workspace.json"), load(f"{dd}/judge/part_contact.json"), load(f"{dd}/judge/dynamics.json")
            if not any((s, s14, ws, pc, dy)): continue
            dof = int(dj.get("dof", dj.get("n", 0)) or 0)
            if not dof or dof > 4: continue
            seen.add(n); rel = os.path.relpath(f"{dd}/score.json", REPO)
            t = first_commit(rel) if dd.startswith(REPO) else None
            anyf = next(p for p in (f"{dd}/score.json", f"{dd}/score_14mm.json", f"{dd}/judge/workspace.json", f"{dd}/judge/part_contact.json", f"{dd}/judge/dynamics.json") if os.path.exists(p))
            t = t or mtime(anyf)
            oh = None
            if s14:
                c = s14.get("clips", []); c = c if isinstance(c, list) else [dict(v, name=k) for k, v in c.items()]
                oh = next((x["score"] for x in c if x.get("name") == "Raise overhead"), None)
            judges = [k for k, v in (("R1", s14), ("R1-aim/R3", s), ("R16", ws), ("R6", pc), ("R17", dy)) if v]
            lvl = "Full CAD" if (n.startswith("cad_") or n == "final") else "Keep-out CAD"
            rows.append(dict(time=t, design=n, level=lvl, dof=dof, complete=len(judges) == 5, judges=" ".join(judges),
                             r1_14=round(s14["in_band"], 4) if s14 else None, r1_10=round(s["in_band"], 4) if s else None,
                             follow=round(s["follow"], 4) if s else None, overhead_14=round(oh, 4) if oh is not None else None,
                             score_14=round(s14["overall"], 4) if s14 else None, range_r16=ws.get("share_passing") if ws else None,
                             parts_mm=pc.get("max_depth") if pc else None, moves_freely=((dy or {}).get("verdict") or {}).get("moves_freely_nominal")))
    rows.sort(key=lambda r: r["time"]); return rows
def evals():
    rows = []
    for f in sorted(glob.glob(os.path.join(REPO, "pipeline/conformal/gpu_client/band_eval_*.json"))):
        D = load(f) or {}; ver = str(D.get("version", ""))
        t = first_commit(os.path.relpath(f, REPO)) or mtime(f)
        for i, x in enumerate(D.get("results") or []):
            if x.get("err") or "envelope" not in x or not x.get("clips"): continue
            if int(x.get("n", 0)) > 4: continue
            e = x["envelope"]; ro = x["clips"].get("Raise overhead", {})
            filled = "fill_holes" in ver and bool(x.get("fill_holes", False))
            rows.append(dict(time=t, design=(x.get("_src") or os.path.basename(f))[:60], level="Search estimate", dof=int(x.get("n", 0)),
                             r1_14=round(x["in_band"], 4) if x.get("G", 14) == 14 else None, follow=round(x["follow"], 4),
                             range_r16=round(e["follow"], 4), overhead_follow=round(ro.get("follow", 0), 4),
                             stand_off=bool(x.get("zj4", 0) > 120), hub_r=x.get("hub_r"), measurement=("filled maps" if "fill" in ver else "raw maps")))
    rows.sort(key=lambda r: r["time"]); return rows
if __name__ == "__main__":
    if "--evals" in sys.argv: json.dump(evals(), sys.stdout, indent=0)
    else: json.dump(designs([os.path.join(REPO, "pipeline/full-exo/designs")] + [a for a in sys.argv[1:]]), sys.stdout, indent=0)
