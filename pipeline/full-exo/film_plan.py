"""Film plan (designs/film.json) shared by the web preview (film.html) and the Blender render: a montage of ADL clips;
inside each clip the design swaps mid-motion so every morphology is seen doing the same thing; slow camera orbit.

    python3 film_plan.py <design id>:<label>:<sub> [...]
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
designs = [dict(zip(("id", "label", "sub"), a.split(":", 2) + [""] * (3 - len(a.split(":", 2))))) for a in sys.argv[1:]]
C = json.load(open(os.path.join(HERE, "designs", designs[0]["id"], "clips.json")))["clips"]
names = [c["name"] for c in C]; pick = [names.index(n) for n in ("Raise overhead", "Comb hair", "Reach a high shelf", "Wave") if n in names]
shots = []; nd = len(designs); k = 0
for ci in pick:
    n = len(C[ci]["frames"]); parts = max(1, nd); cut = [round(n * j / parts) for j in range(parts + 1)]
    for j in range(parts):
        shots.append(dict(design=(k + j) % nd, clip=ci, f0=cut[j], f1=cut[j + 1] - 1))
    k += 1
NF = sum(s["f1"] - s["f0"] + 1 for s in shots)
keys = [((-0.95, 0.45, 0.70), (0.0, -0.06, 0.05), 26), ((-0.45, 0.35, 1.10), (0.0, -0.07, 0.05), 25), ((0.35, 0.32, 1.12), (0.0, -0.08, 0.05), 25),
        ((0.85, 0.42, 0.68), (0.0, -0.07, 0.05), 26), ((-0.25, 1.05, 0.50), (0.0, -0.05, 0.04), 28), ((-0.95, 0.45, 0.70), (0.0, -0.06, 0.05), 26)]
cam = [dict(f=round(i * (NF - 1) / (len(keys) - 1)), pos=list(p), target=list(t), fov=fv) for i, (p, t, fv) in enumerate(keys)]
json.dump(dict(fps=30, designs=designs, shots=shots, xfade=10, camera=cam), open(os.path.join(HERE, "designs", "film.json"), "w"), indent=1)
print(f"{len(shots)} shots, {NF} frames ({NF / 30:.1f} s)")
