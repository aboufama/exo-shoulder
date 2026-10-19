"""local random sweep of virtual-j2-knee-3r around the gate's best pair (Bench(60,160) fast, every kit check on)"""
import importlib.util, json, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_kit as K   # noqa: E402
spec = importlib.util.spec_from_file_location("vj2", os.path.join(REPO, "docs/concepts/models/virtual-j2-knee-3r.py"))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 0); n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
base = dict(M.PARAMS, rhoP=28, psiP=30, rhoB=12, psiB=30, la=24, lk=24, hA=56, hB=70)
cfgs = [M.snap(base)]
for _ in range(n - 1):
    c = dict(base)
    c.update(a1=rng.uniform(44, 60), a2=rng.uniform(60, 88), rhoP=rng.uniform(14, 44), psiP=rng.uniform(-60, 120),
             rhoB=rng.uniform(8, 40), psiB=rng.uniform(-40, 140), la=rng.uniform(21, 40), lk=rng.uniform(21, 40),
             kb=rng.choice([-1, 1]), h0=rng.uniform(48, 66), hA=rng.uniform(48, 80), hB=rng.uniform(48, 90),
             az=109.36 + rng.normal(0, 8), el=65.94 + rng.normal(0, 6), wd=85.74 + rng.normal(0, 10), wa=-16.19 + rng.normal(0, 15),
             q=rng.uniform(0.9, 1.0))
    cfgs.append(M.snap(c))
B = K.bench(60, 160)
out = os.path.join(REPO, "docs/concepts/sweeps/virtual-j2-knee-3r.json") if len(sys.argv) <= 3 else sys.argv[3]
best, rows = K.sweep(B, M.build, cfgs, out, resume=True)
print(json.dumps(best, default=str)[:1500])
