"""verifier red team: a PARTLY metal-aware IK state flood. Same as ik_flood (kinematic AA gates, |dk|<=10 per 2-deg frame,
passives <=10, actives <=25, self-motion inside a run) except that at every Bench(110,360) ws pose the IK had to move
(the 100 'need' poses, whose exact metal is known at all 17 k from the claim's own k-table), a (pose, k) state exists only
if that k TAKES the pose with metal (min metal >= 0, no jam). So no self-motion or path passes a bench pose through a
metal-contact / jammed / non-closing ring state. Other envelope nodes stay kinematic (their metal is unknown)."""
import importlib.util, inspect, json, os, sys, numpy as np
REPO = '/home/user/exo-shoulder'; OUT = sys.argv[1]
os.environ['CB_EXACT'] = '1'
sp = importlib.util.spec_from_file_location('ikr_v', os.path.join(REPO, 'docs/concepts/models/ikring-thinstack-knuckle-4r.py'))
IK = importlib.util.module_from_spec(sp); sp.loader.exec_module(IK)
V = os.path.join(REPO, 'docs/concepts/verify/ikring-thinstack-knuckle-4r/')
first = json.load(open(V + 'ik_bench.json')); ch = first['ik']['choice']
B = IK.CB.Bench(110, 360); idx = np.asarray(B.idx)
MASK = {}                                   # archive id -> set of metal-take k
for j, c in ch.items(): MASK[int(idx[int(j)])] = set(round(float(k), 3) for k in c['takes'])
src = inspect.getsource(IK.ik_flood)
a = "    okN, AN, PN, SN = table(Ha)\n"; assert a in src
src = src.replace(a, a + "    for _a in range(n):\n        _g = int(allw[_a])\n        if _g in MASK:\n            for _c in range(nk): okN[_a, _c] = okN[_a, _c] and (round(KS[_c], 3) in MASK[_g])\n")
src = src.replace('path = os.path.join(VDIR, key)', 'path = OUTP').replace('def ik_flood(', 'def ik_flood_m(')
IK.__dict__['MASK'] = MASK; IK.__dict__['OUTP'] = OUT
exec(compile(src, 'ik_flood_m', 'exec'), IK.__dict__)
F = IK.fit(dict(IK.CLAIM)); FL = IK.ik_flood_m(F); print(json.dumps(FL['stats']))
o = json.load(open(V + 'ik_bench_spec.json')); keep = []; drop = []
for t in o['ik']['new_list']:
    nd = FL['nodes'].get(str(t['g'])); ok = nd is not None and any(abs(t['k'] - x) < 1e-6 for x in nd['conn'])
    (keep if ok else drop).append([t['i'], t['g'], t['pose'], t['k'], t['mm']])
print(json.dumps(dict(kept=len(keep), dropped=drop)))
json.dump(dict(stats=FL['stats'], kept=keep, dropped=drop), open(OUT.replace('.json', '_verdict.json'), 'w'))
