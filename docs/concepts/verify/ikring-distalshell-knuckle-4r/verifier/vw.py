"""verifier (skeptic) for ikring-distalshell-knuckle-4r: (1) the IK continuity flood REBUILT with this design's knee
(lE 69.52 / ang_min 25.64; the claim dir's flood file is byte-identical to pick 1's, built on the lead's lE 97 knee);
(2) the claim's final k choice (ik_bench_fixk_choice.json, take-only rule) re-worn exact frozen on Bench(110,360) with the
rebuilt flood's cmap; (3) the phi40 verifier's extra checks X1 (every chain set incl. crowns vs shell / carriage /
bracket, non-adjacent < 1 mm -> lost) + X2 (bracket top layer) on the SAME wear, re-scored; per-pose dump + th margin."""
import importlib.util, json, os, sys, time, numpy as np
REPO = '/home/user/exo-shoulder'; OUT = sys.argv[1]; CHO = sys.argv[2]
os.environ['CB_EXACT'] = '1'
sp = importlib.util.spec_from_file_location('ds_v', os.path.join(REPO, 'docs/concepts/models/ikring-distalshell-knuckle-4r.py'))
DS = importlib.util.module_from_spec(sp); sp.loader.exec_module(DS); IK = DS.IK
VD = os.path.join(REPO, 'docs/concepts/verify/ikring-distalshell-knuckle-4r/verifier')
IK.VDIR = VD                                                   # flood cache -> rebuilt here with THIS knee
sp = importlib.util.spec_from_file_location('p40v', os.path.join(REPO, 'docs/concepts/verify/phi40-thinstack-relay-4r-verify.py'))
VV = importlib.util.module_from_spec(sp); sp.loader.exec_module(VV)
VV.OM, VV.OS, VV.PT, VV.AA, VV.CB, VV.BV = IK.P4, IK.OS, IK.PT, IK.AA, IK.CB, IK.BV
CL = os.path.join(REPO, 'docs/concepts/verify/ikring-distalshell-knuckle-4r/')
base = json.load(open(CL + 'ik_bench_fixk_perpose.json'))['params']
t0 = time.time(); F = IK.fit(dict(base)); hw = dict(base); print(json.dumps(dict(fit=F['fit'])), flush=True)
Bf = IK.subbench(IK.CB.Bench(110, 360), np.arange(470)); nZ = len(IK.AA.Z0['HG']); ws = np.array(Bf.kind) == 'ws'
prev = json.load(open(CHO)); choice = {}
for j, c in prev['ik']['choice'].items():
    c = dict(c)
    if c['k'] != 0 and not c['takes']: c.update(k=0.0, reverted=True)
    choice[int(j)] = c
phiF = np.zeros(nZ)
for j, c in choice.items(): phiF[Bf.idx[j]] = c['k']
FL = IK.ik_flood(F); nodes = FL['nodes']; print(json.dumps(dict(flood=FL['stats'])), flush=True)
old = json.load(open(CL + 'ikflood_PHI40_t8.5_a243_k2.5.json'))['nodes']
cmap = {}; cmap_old = {}; diff = []
for j in np.nonzero(ws)[0]:
    g = str(int(Bf.idx[j])); kk = float(phiF[Bf.idx[j]])
    nd = nodes.get(g); no = old.get(g)
    cmap[int(g)] = bool(nd is not None and any(abs(kk - x) < 1e-6 for x in nd['conn']))
    cmap_old[int(g)] = bool(no is not None and any(abs(kk - x) < 1e-6 for x in no['conn']))
    if cmap[int(g)] != cmap_old[int(g)]: diff.append(dict(i=int(j), g=int(g), k=kk, new=cmap[int(g)], old=cmap_old[int(g)],
                                                          feas_new=nd['feas'] if nd else None, conn_new=nd['conn'] if nd else None))
print(json.dumps(dict(cmap_diff=diff)), flush=True)
o, S = IK.wear_phi(F, Bf, phiF, hw, cmap=cmap)
sm = IK.P4.summary(o); print(json.dumps(dict(final=sm), default=float), flush=True)
try: thm = IK.BV.th_margin(S['M'], S['B'])
except Exception as ex: thm = dict(err=repr(ex)[:200])
pp = IK.P4.perpose(S); pp.update(id=DS.ID, wear='bench', params=base, exact=True, ik=True, verifier=True)
json.dump(pp, open(OUT.replace('.json', '_perpose.json'), 'w'), default=float)
st = dict(stations=DS.stations(S['M'], S['B']))
print(json.dumps(st), flush=True)
x = VV.xcheck(S, hw, o)
print(json.dumps(dict(n_extra_jam=x['n_extra_jam'], lost_new=x['lost_new'], rescored=x['rescored'],
                      margin={k: v for k, v in x['clearance_margin_taken'].items() if k != 'lowest'}), default=float), flush=True)
json.dump(dict(summary=sm, th_margin=thm, contacts=o['contacts'], cmap_diff=diff, flood=FL['stats'], stations=st, xcheck=x,
               continuity={k: v for k, v in (o.get('continuity') or {}).items() if k != 'dropped'}, secs=round(time.time() - t0, 1)),
          open(OUT, 'w'), indent=1, default=float)
print('done', round(time.time() - t0, 1), flush=True)
