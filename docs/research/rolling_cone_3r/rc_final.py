import json, glob, collections, sys
S = __import__('os').environ.get('RC_LOGS', __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
files = ['rs_a', 'rs_b', 'rs_c', 'rs_d', 'rs_e', 'rs_f']
L = []
for f in files:
    try: L += [dict(json.loads(l), src=f) for l in open(f'{S}/{f}.jsonl')]
    except FileNotFoundError: pass
def score_of(ws): return 100 * (1 - 100 * max(0.0, 0.90 - ws / 160) / 275)
L.sort(key=lambda l: l['t'])                       # the order the configurations were evaluated
out = []
for k, l in enumerate(L):
    out.append(dict(k=k, t=l['t'], params=dict(family=l['fam'], **l['cell']), inband14=None, inband10=None, reach=None, follow=None,
                    contact=None, gap=None, kin_ws=l['ws'], kin_ws_n=160, kin_overhead=l['over'], kin_overhead_n=12,
                    kin_reach=round(l['ws'] / 160, 4), arcs_sun_planet_walk=l.get('arcs'), obj=l['obj'],
                    ghost='law-only kinematic ghost on Bench(60,160) ws poses (H1 seats; no metal): kin_* are upper bounds, not bench numbers'))
json.dump(out, open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'concepts', 'sweeps', 'rolling-cone-3r.json'), 'w'), indent=0)
# convergence gate per family (search order within each family, kinematic score points)
by = collections.defaultdict(list)
for l in L: by[l['fam']].append(l)
gate = {}
for fam, ls in by.items():
    if len(ls) < 3: gate[fam] = dict(n=len(ls), best_ws=max(x['ws'] for x in ls)); continue
    ob = [x['obj'] for x in ls]; ws = [x['ws'] for x in ls]; n = len(ls)
    bi = lambda m: max(range(m), key=lambda i: ob[i])
    b_all = ws[bi(n)]; b_half = ws[bi(n // 2)]; b_23 = ws[bi(2 * n // 3)]
    top = sorted(ls, key=lambda x: -x['obj'])[:5]
    gate[fam] = dict(n=n, best_ws=b_all, best_over=sorted(ls, key=lambda x: -x['obj'])[0]['over'],
                     gain_2nd_half=round(score_of(b_all) - score_of(b_half), 2), gain_last_third=round(score_of(b_all) - score_of(b_23), 2),
                     top5_spread=round(score_of(top[0]['ws']) - score_of(top[-1]['ws']), 2), best_cell=top[0]['cell'], arcs=top[0].get('arcs'))
print(json.dumps(gate, indent=1)); print('total configs', len(L))
json.dump(gate, open(f'{S}/gate.json', 'w'), indent=1)
