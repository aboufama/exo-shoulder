"""Scorecard: every requirement in judge/requirements.json against the judges' outputs for one design.
Runs nothing heavy itself; run the judges first (README "Judge a design"). Writes <design>/judge/scorecard.md + .json.
    python3 judge/scorecard.py <design dir|id>"""
import json, os, sys
from common import design_dir, REPO
dd = design_dir(sys.argv[1]); J = os.path.join(dd, "judge"); REQ = json.load(open(os.path.join(REPO, "judge", "requirements.json")))
def load(p):
    try: return json.load(open(p))
    except Exception: return None
src = dict(score=load(os.path.join(dd, "score.json")), score14=load(os.path.join(dd, "score_14mm.json")), body_contact=load(os.path.join(J, "body_contact.json")), part_contact=load(os.path.join(J, "part_contact.json")),
           part_validity=load(os.path.join(J, "part_validity.json")), base_mount=load(os.path.join(J, "base_mount.json")), design=load(os.path.join(dd, "design.json")), parts=load(os.path.join(dd, "parts_full.json")))
def metric(m):
    s, k = m.split(".", 1); d = src.get(s if s != "mass" else "parts")
    if d is None: return None
    if s in ("score", "score14") and k.startswith("clip:"): return next((c["score"] for c in d["clips"] if c["name"] == k[5:]), None)
    if s == "mass": return round(sum(p["mass_g"] or 0 for p in d["parts"] if p.get("material") != "user part"), 1)
    return d.get(k)
OPS = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, "==": lambda a, b: a == b}
rows = []
for rid, r in REQ.items():
    if rid.startswith("_"): continue
    if "metric" in r:
        v = metric(r["metric"]); st = "NOT RUN" if v is None else ("PASS" if OPS[r["op"]](v, r["value"]) else "FAIL")
        rows.append(dict(id=rid, name=r["name"], value=v, unit=r.get("unit"), target=f"{r['op']} {r['value']}{(' ' + r['unit']) if 'unit' in r else ''}", status=st, judge=r["judge"]))
    else: rows.append(dict(id=rid, name=r["name"], value=None, target="", status=r["status"], judge=r["judge"]))
fmt = lambda v, u=None: "-" if v is None else (f"{v} {u}" if u else (f"{100 * v:.1f}%" if isinstance(v, float) and 0 <= v <= 1.0 and not isinstance(v, bool) else str(v)))
md = [f"# Scorecard: {os.path.basename(os.path.normpath(dd))}", "", "| | requirement | value | target | status | judge |", "|---|---|---|---|---|---|"]
md += [f"| {r['id']} | {r['name']} | {fmt(r['value'], r.get('unit'))} | {r['target']} | **{r['status']}** | {r['judge']} |" for r in rows]
n_pass = sum(r["status"] == "PASS" for r in rows); md += ["", f"{n_pass} of {len(rows)} requirements pass."]
open(os.path.join(J if os.path.isdir(J) else dd, "scorecard.md"), "w").write("\n".join(md) + "\n"); json.dump(rows, open(os.path.join(J if os.path.isdir(J) else dd, "scorecard.json"), "w"), indent=1)
print("\n".join(md))
