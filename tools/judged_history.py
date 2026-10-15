"""Every judged design over time, for the dashboard: one row per design that has score.json + score_14mm.json
(+ design.json, <= 4 DOF), time = the commit that first added its score_14mm.json, values from the files as they are
now (the judges' current measurement). Columns are the requirement metrics (R1 14 mm, R1-aim 10 mm, R3 follow,
R4 overhead, R16 range, R6, R8, R17).   python3 tools/judged_history.py > judged.json"""
import json, os, subprocess, sys
REPO = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip(); D = os.path.join(REPO, "pipeline/full-exo/designs")
def load(p):
    try: return json.load(open(p))
    except Exception: return None
rows = []
for n in sorted(os.listdir(D)):
    dd = os.path.join(D, n); s, s14, dj = load(f"{dd}/score.json"), load(f"{dd}/score_14mm.json"), load(f"{dd}/design.json")
    if not (s and s14 and dj): continue
    if int(dj.get("dof", dj.get("n", 9)) or 9) > 4: continue
    t = subprocess.run(["git", "-C", REPO, "log", "--diff-filter=A", "--format=%cI", "--", f"pipeline/full-exo/designs/{n}/score_14mm.json"], capture_output=True, text=True).stdout.split()
    if not t: continue
    c = s14.get("clips", []); c = c if isinstance(c, list) else [dict(v, name=k) for k, v in c.items()]
    oh = next((x["score"] for x in c if x.get("name") == "Raise overhead"), None)
    ws = load(f"{dd}/judge/workspace.json") or {}; pc = load(f"{dd}/judge/part_contact.json") or {}; dy = load(f"{dd}/judge/dynamics.json") or {}
    pf = load(f"{dd}/parts_full.json") or {}
    mass = pf.get("custom_mass_g") if isinstance(pf, dict) else None
    lvl = "Full CAD" if n.startswith("cad_") or n == "final" else "Keep-out CAD"
    rows.append(dict(time=t[-1], design=n, level=lvl, dof=int(dj.get("dof", dj.get("n", 0)) or 0), r1_14=round(s14["in_band"], 4), r1_10=round(s["in_band"], 4),
                     follow=round(s["follow"], 4), overhead_14=round(oh, 4) if oh is not None else None, score_14=round(s14["overall"], 4),
                     range_r16=ws.get("share_passing"), parts_mm=pc.get("max_depth"), mass_g=mass,
                     moves_freely=(dy.get("verdict") or {}).get("moves_freely_nominal")))
rows.sort(key=lambda r: r["time"]); json.dump(rows, sys.stdout, indent=0)
