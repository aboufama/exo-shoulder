"""Merge the exhaustive GPU search outputs (exo-farm/gpu/out/xs/ brought back by `tools/gpu_pod.py fetch`) into
docs/research/golden/gpu_frontier.json: the screen certificate of each part, every CMA basin (start, converged best:
params, GPU plain / near-touch gap, reach, follow, in-band by member, contact, hub F), the CPU verification (fast fit
110/360, exact frozen wear 110/360 for both fit protocols) of the top 10 distinct configs.

    python3 pipeline/gpu_pod/xs_merge.py DIR [OUT.json]
"""
import glob, json, os, sys

KEYS = ("gap", "near", "reach", "follow", "inband14", "inband10", "contact", "honest", "hub_F", "inband_member")


def slim(r):
    return {k: r.get(k) for k in ("params",) + KEYS + ("v_gap", "v_near", "closure_k2", "collide", "outside", "sobol_i", "lbA", "lbB")
            if r.get(k) is not None}


def main():
    d = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else "docs/research/golden/gpu_frontier.json"
    res = dict(source="tools/gpu_bench.py screen + cma (pipeline/gpu_pod/xs.sh) on exo-gpu-bench (RTX PRO 4000) + exo-gpu-bench2 (RTX 5090)",
               objective="search: near-touch gap (metal < 1 mm = contact; CLAUDE.md rule), same-bench Bench(110,360) fast; claim: plain gap, frozen exact",
               screens=[], basins=[], verify=[])
    for f in sorted(glob.glob(os.path.join(d, "screen_p*.json"))):
        s = json.load(open(f)); rows = s.pop("rows")
        s["best_near"] = [slim(r) for r in rows[:10]]
        s["best_gap"] = [slim(r) for r in sorted(rows, key=lambda r: r.get("gap", 999))[:10]]
        s["n_rows"] = len(rows); s["n_honest"] = sum(1 for r in rows if r.get("honest"))
        s["file"] = os.path.basename(f); res["screens"].append(s)
    for f in sorted(glob.glob(os.path.join(d, "cma_p*.json"))):
        c = json.load(open(f))
        for b in c["basins"]:
            b["best"] = slim(b["best"]); b["part"] = os.path.basename(f); res["basins"].append(b)
        res.setdefault("cma", []).append({k: c.get(k) for k in ("t", "tag", "secs", "key", "lam", "evals", "meta")} | dict(file=os.path.basename(f)))
    res["basins"].sort(key=lambda b: b["best"].get("near", 999))
    pick = os.path.join(d, "verify_pick.json")
    picks = json.load(open(pick)) if os.path.exists(pick) else []
    for i, e in enumerate(picks):
        v = dict(rank=i, gpu=slim(e), src=e.get("src"))
        f = os.path.join(d, "verify", f"v{i:02d}.json")
        if os.path.exists(f):
            x = json.load(open(f))
            for prot in ("fit110", "fit60"):
                if prot in x:
                    v[prot] = dict(fit_fast=x[prot].get("fit"), wear_exact={k: x[prot]["wear"].get(k) for k in KEYS + ("audit", "min_metal_all_faces", "top_contact_poses")},
                                   attribution=x[prot].get("attribution"), wear_mode=x.get("wear_mode"), secs=x[prot].get("secs"))
        res["verify"].append(v)
    json.dump(res, open(out, "w"), indent=1, default=float)
    print(f"{out}: {len(res['screens'])} screens, {len(res['basins'])} basins, {len(res['verify'])} verified")


if __name__ == "__main__":
    main()
