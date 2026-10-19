"""verifier: the claim's final wear (k choice from the claim run, take-only) re-worn exact on Bench(110,360), then the
phi40 verifier's extended checks X1 (every chain set incl. crowns vs shell / carriage / bracket, non-adjacent < 1 mm ->
lost) + X2 (bracket top layer) on the SAME wear, re-scored (chain-only gate)."""
import importlib.util, json, os, sys, numpy as np
REPO = '/home/user/exo-shoulder'; OUT = sys.argv[1]; CHO = sys.argv[2]
os.environ['CB_EXACT'] = '1'
sp = importlib.util.spec_from_file_location('ikr_x', os.path.join(REPO, 'docs/concepts/models/ikring-thinstack-knuckle-4r.py'))
IK = importlib.util.module_from_spec(sp); sp.loader.exec_module(IK)
sp = importlib.util.spec_from_file_location('p40v', os.path.join(REPO, 'docs/concepts/verify/phi40-thinstack-relay-4r-verify.py'))
VV = importlib.util.module_from_spec(sp); sp.loader.exec_module(VV)
VV.OM, VV.OS, VV.PT, VV.AA, VV.CB, VV.BV = IK.P4, IK.OS, IK.PT, IK.AA, IK.CB, IK.BV      # same module instances as the wear
base = dict(IK.CLAIM); F = IK.fit(base); hw = dict(base)
Bf = IK.subbench(IK.CB.Bench(110, 360), np.arange(470)); nZ = len(IK.AA.Z0['HG'])
prev = json.load(open(CHO)); choice = prev['ik']['choice']; phiF = np.zeros(nZ)
for j, c in choice.items(): phiF[Bf.idx[int(j)]] = c['k']
FL = IK.ik_flood(F); nodes = FL['nodes']; ws = np.array(Bf.kind) == 'ws'; cmap = {}
for j in np.nonzero(ws)[0]:
    g = str(int(Bf.idx[j])); kk = float(phiF[Bf.idx[j]]); nd = nodes.get(g)
    cmap[int(g)] = bool(nd is not None and any(abs(kk - x) < 1e-6 for x in nd['conn']))
o, S = IK.wear_phi(F, Bf, phiF, hw, cmap=cmap)
sm = IK.P4.summary(o); print(json.dumps(dict(final=sm), default=float), flush=True)
try: thm = IK.BV.th_margin(S['M'], S['B'])
except Exception as ex: thm = dict(err=repr(ex)[:200])
pp = IK.P4.perpose(S); pp.update(id=IK.ID, wear='bench', params=base, exact=True, ik=True, verifier=True)
json.dump(pp, open(OUT.replace('.json', '_perpose.json'), 'w'), default=float)
x = VV.xcheck(S, hw, o)
print(json.dumps(dict(n_extra_jam=x['n_extra_jam'], lost_new=x['lost_new'], rescored=x['rescored'], margin={k: v for k, v in x['clearance_margin_taken'].items() if k != 'lowest'}), default=float), flush=True)
json.dump(dict(summary=sm, th_margin=thm, contacts=o['contacts'], xcheck=x, continuity={k: v for k, v in (o.get('continuity') or {}).items() if k != 'dropped'}), open(OUT, 'w'), indent=1, default=float)
print('done', flush=True)
