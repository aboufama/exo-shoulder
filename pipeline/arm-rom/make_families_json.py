"""Collect the best anatomical design per family and shell radius for the viewer (families_anat.json)."""
import json, subprocess
KEYS = dict(B=("b", "alpha", "delta", "waz"), C=("b", "a1", "a2", "delta", "waz"), D=("b", "a1", "a2", "a3", "delta", "waz"), E=("b1", "b2", "p", "d", "delta", "waz"))
out = {}
for f, keys in KEYS.items():
    rows = json.load(open(f"design_search_anat_{f}.json")); out[f] = {}
    for R in (124, 136, 148):
        r = max((x for x in rows if x["R"] == R), key=lambda x: x["cov"])
        out[f][R] = dict(params={k: r[k] for k in keys}, cov=r["cov"], post_centre=r["post_centre"], branch=r.get("branch"), modes=r.get("modes"))
line = subprocess.run(["python3", "current_rescore_anat.py"], capture_output=True, text=True).stdout.strip().splitlines()[-1]
out["A"] = line.split(":")[1].split("%")[0].strip() + "%"
json.dump(out, open("families_anat.json", "w"), indent=1)
print(json.dumps({f: {R: round(100 * v["cov"], 1) for R, v in d.items()} if f != "A" else d for f, d in out.items()}))
