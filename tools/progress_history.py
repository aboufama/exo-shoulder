"""Progress over time, from the git history of the judges' outputs (nothing re-run): at every commit that touched a
design's score / judge files, the best value of each tracked metric across all designs committed at that point, plus
the reference design's contact depths and the cumulative RunPod spend (docs/RUNPOD_COSTS.md). One row per metric
change. Only designs with a design.json and <= 4 DOF count (the legacy dirs predate today's scorer and rules). Measurement changes (judge or band changes) are listed as events so a jump is never read as design progress.
    python3 tools/progress_history.py > progress.json"""
import json, re, subprocess, sys
REPO = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
git = lambda *a: subprocess.check_output(["git", "-C", REPO, *a], text=True, stderr=subprocess.DEVNULL)
D = "pipeline/full-exo/designs/"; REF = "cad_r13_n4_s1343_1"
def show(c, p):
    try: return json.loads(git("show", f"{c}:{p}"))
    except Exception: return None
def clip(s, name):
    c = s.get("clips", []); c = c if isinstance(c, list) else [dict(v, name=k) for k, v in c.items()]
    return next((x["score"] for x in c if x.get("name") == name), None)
commits = [l.split() for l in git("log", "--first-parent", "--reverse", "--format=%H %cI", "--", D, "judge/requirements.json").splitlines()]   # the branch's own line
METRICS = {"best_score_10": "Best score, 2-10 mm", "best_score_14": "Best score, 2-14 mm (pass line)", "best_3dof_10": "Best 3-DOF score, 2-10 mm",
           "best_3dof_14": "Best 3-DOF score, 2-14 mm", "best_follow": "Best share of frames followed", "best_inband_10": "Best skin share within 2-10 mm",
           "best_overhead_10": "Best overhead score, 2-10 mm", "ref_body_mm": "Reference: worst body penetration (mm)", "ref_parts_mm": "Reference: worst part interference (mm)"}
rows, last = [], {}
for c, t in commits:
    names = sorted({p[len(D):].split("/")[0] for p in git("ls-tree", "-r", "--name-only", c, D).splitlines() if p.endswith("score.json") or p.endswith("score_14mm.json")})
    snap = {}
    for n in names:
        s, s14, dj = show(c, D + n + "/score.json"), show(c, D + n + "/score_14mm.json"), show(c, D + n + "/design.json") or {}
        dof = dj.get("dof") or dj.get("n_joints"); cand = []
        if not dj or dof is None or dof > 4: continue                      # legacy dirs (no design.json, older metrics) and > 4 DOF: not comparable
        if s: cand += [("best_score_10", s["overall"]), ("best_follow", s["follow"]), ("best_inband_10", s["in_band"]), ("best_overhead_10", clip(s, "Raise overhead"))]
        if s14: cand += [("best_score_14", s14["overall"])]
        if s and dof == 3: cand += [("best_3dof_10", s["overall"])]
        if s14 and dof == 3: cand += [("best_3dof_14", s14["overall"])]
        for m, v in cand:
            if v is not None and (m not in snap or v > snap[m][0]): snap[m] = (float(v), n)
    bc, pc = show(c, D + REF + "/judge/body_contact.json"), show(c, D + REF + "/judge/part_contact.json")
    if bc and bc.get("max_depth") is not None: snap["ref_body_mm"] = (float(bc["max_depth"]), REF)
    if pc and pc.get("max_depth") is not None: snap["ref_parts_mm"] = (float(pc["max_depth"]), REF)
    for m, (v, n) in snap.items():
        if last.get(m) != (round(v, 4), n):
            rows.append(dict(time=t, commit=c[:7], metric=m, label=METRICS[m], value=round(v, 4), design=n)); last[m] = (round(v, 4), n)
# RunPod spend: balance after each logged row (start 56.71)
try:
    txt = open(REPO + "/docs/RUNPOD_COSTS.md").read(); start = 56.71
    rows.append(dict(time="2026-10-15T00:33:00+00:00", commit="", metric="gpu_spend", label="GPU spend this session ($)", value=0.0, design=""))
    for line in txt.splitlines():
        m = re.match(r"\| 10-15 (\d\d:\d\d)(?:-(\d\d:\d\d))? \|", line); b = re.search(r"(\d+\.\d\d) -> (\d+\.\d\d)", line)
        if m and b:
            rows.append(dict(time=f"2026-10-15T{m.group(2) or m.group(1)}:00+00:00", commit="", metric="gpu_spend", label="GPU spend this session ($)", value=round(start - float(b.group(2)), 2), design=""))
except OSError: pass
json.dump(rows, sys.stdout, indent=1)
