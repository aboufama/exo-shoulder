"""Per-group swap attribution of the gen-5 full CAD's R1 loss against its L1 (docs/research/geneva-rod-gen5_fix.md section 4):
start from the full CAD WITHOUT its drive metal (groups dk / dr, every D9-* / "drive ..." part), then replace ONE member group's
parts by the L1's parts of the same group (the L1's own drive keep-outs left out too) and score with the judges' own
score_design.py (BANDS=10,14, step 3, the run tools/judge_all.sh does). Both builds pose every chain group by the same
frames (the CAD's clips.json = the L1's + dk / dr), so a swapped group sits exactly where the L1 put it. The tree is never
written: every variant is a scratch design dir.

    python3 docs/research/geneva_rod_drive/r1_swap.py <out dir> <variant> [<variant> ...]
variants: nodrive (the CAD minus drive metal), swap:<g> (one group from the L1), l1nodrive (every member group from the L1)
"""
import json, os, shutil, subprocess, sys, time
import trimesh
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DES = os.path.join(REPO, "pipeline", "full-exo", "designs"); CAD, L1 = "user_geneva_rod", "l1_geneva-rod"
drive_like = lambda g, n: g in ("dk", "dr") or n.startswith("D9-") or n.lower().startswith("drive ")


def parts(design):
    sc = trimesh.load(os.path.join(DES, design, "exo.glb")); out = []
    for node in sc.graph.nodes_geometry:
        T_, gn = sc.graph[node]; m = sc.geometry[gn].copy(); m.apply_transform(T_); g, n = node.split("|")[:2]; out.append((g, n, m))
    return out


def variant(name, cad, l1, out):
    swap = set(name.split(":")[1].split("+")) if name.startswith("swap:") else (set(g for g, n, m in l1) - {"H", "F"} if name == "l1nodrive" else set())
    keep = [(g, n, m) for g, n, m in cad if not drive_like(g, n) and g not in swap] + [(g, n, m) for g, n, m in l1 if g in swap and not drive_like(g, n)]
    d = os.path.join(out, name.replace(":", "_").replace("+", "_")); os.makedirs(d, exist_ok=True)
    for f in ("clips.json", "design.json"): shutil.copy(os.path.join(DES, CAD, f), d)
    sc = trimesh.Scene()
    for k, (g, n, m) in enumerate(keep): nn = f"{g}|{n}|{k}"; sc.add_geometry(m, node_name=nn, geom_name=nn)
    sc.export(os.path.join(d, "exo.glb")); t = time.time()
    r = subprocess.run([sys.executable, "-W", "ignore", "score_design.py", d, "3"], cwd=os.path.join(REPO, "pipeline", "full-exo"), env=dict(os.environ, BANDS="10,14"),
                       capture_output=True, text=True)
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:]); return None
    S = json.load(open(os.path.join(d, "score_14mm.json"))); S10 = json.load(open(os.path.join(d, "score.json")))
    res = dict(variant=name, swapped=sorted(swap), parts=len(keep), R1=S["overall"], R1_aim=S10["overall"], secs=round(time.time() - t),
               clips={c["name"]: dict(score=c["score"], min_gap=c["min_gap"]) for c in S["clips"]})
    json.dump(res, open(os.path.join(d, "attr.json"), "w"), indent=1); print(json.dumps(res), flush=True); return res


if __name__ == "__main__":
    out = os.path.abspath(sys.argv[1]); cad, l1 = parts(CAD), parts(L1); res = []
    for v in sys.argv[2:]: res.append(variant(v, cad, l1, out))
    json.dump(res, open(os.path.join(out, f"swap_{int(time.time())}.json"), "w"), indent=1)
