"""R1 attribution for the gen-5 full CAD against its L1 (docs/research/geneva-rod-gen5_fix.md section 4): score a scratch copy
of a design with some parts removed from exo.glb (by group or by name prefix), with the judges' own score_design.py
(BANDS=10,14, step 3, the run tools/judge_all.sh does). The design dir in the tree is never written.

    python3 docs/research/geneva_rod_drive/r1_attr.py <design id> <out dir> [--drop-groups dk,dr] [--drop-names D9-01,...]
"""
import argparse, json, os, shutil, subprocess, sys
import trimesh
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
ap = argparse.ArgumentParser(); ap.add_argument("design"); ap.add_argument("out"); ap.add_argument("--drop-groups", default=""); ap.add_argument("--drop-names", default="")
a = ap.parse_args(); src = os.path.join(REPO, "pipeline", "full-exo", "designs", a.design); dst = os.path.abspath(a.out); os.makedirs(dst, exist_ok=True)
for f in ("clips.json", "design.json"): shutil.copy(os.path.join(src, f), dst)
dg = [g for g in a.drop_groups.split(",") if g]; dn = [n for n in a.drop_names.split(",") if n]
sc = trimesh.load(os.path.join(src, "exo.glb")); dropped = []
for node in list(sc.graph.nodes_geometry):
    g, n = node.split("|")[:2]
    if g in dg or any(n.startswith(p) for p in dn): sc.delete_geometry(sc.graph[node][1]); dropped.append(node)
sc.export(os.path.join(dst, "exo.glb"))
r = subprocess.run([sys.executable, "-W", "ignore", "score_design.py", dst, "3"], cwd=os.path.join(REPO, "pipeline", "full-exo"), env=dict(os.environ, BANDS="10,14"),
                   capture_output=True, text=True)
print(r.stdout[-3000:], r.stderr[-2000:])
S = json.load(open(os.path.join(dst, "score_14mm.json"))); S10 = json.load(open(os.path.join(dst, "score.json")))
json.dump(dict(design=a.design, dropped=dropped, R1=S["overall"], R1_aim=S10["overall"], groups_scored=S["groups_scored"],
               clips={c["name"]: dict(score=c["score"], min_gap=c["min_gap"], median_gap=c["median_gap"]) for c in S["clips"]}),
          open(os.path.join(dst, "attr.json"), "w"), indent=1)
print("R1", S["overall"], "R1-aim", S10["overall"], "dropped", len(dropped))
