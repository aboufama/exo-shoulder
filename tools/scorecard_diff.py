"""Scorecard before vs after: compare a design's judge/scorecard.json with the same file at a git revision.
    python3 tools/scorecard_diff.py <design id> [rev=HEAD]      (run judge_all.sh first so the working copy is current)
Prints a markdown table; a value that moved because the MEASUREMENT changed (a judge added or redefined) shows as
status NOT RUN/OPEN -> number - report those separately from design changes (CLAUDE.md)."""
import json, os, subprocess, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
des = sys.argv[1]; rev = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
rel = f"pipeline/full-exo/designs/{des}/judge/scorecard.json"
now = {r["id"]: r for r in json.load(open(os.path.join(REPO, rel)))}
try: old = {r["id"]: r for r in json.loads(subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=REPO, capture_output=True, text=True, check=True).stdout)}
except subprocess.CalledProcessError: old = {}
def fmt(r):
    if r is None: return "-"
    v = r.get("value")
    if v is None: return r["status"]
    s = f"{100 * v:.1f}%" if isinstance(v, float) and 0 <= v <= 1 and not isinstance(v, bool) else str(v)
    return f"{s} ({r['status']})"
print(f"| | requirement | before ({rev}) | after | |\n|---|---|---|---|---|")
for k, r in now.items():
    o = old.get(k); moved = fmt(o) != fmt(r)
    why = "" if not moved else ("measurement added" if o is None or o.get("value") is None and r.get("value") is not None else "changed")
    print(f"| {k} | {r['name'][:60]} | {fmt(o)} | {fmt(r)} | {why} |")
print(f"\npass: {sum(r['status'] == 'PASS' for r in old.values())} -> {sum(r['status'] == 'PASS' for r in now.values())} of {len(now)}")
