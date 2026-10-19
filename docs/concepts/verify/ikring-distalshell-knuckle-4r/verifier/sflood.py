"""verifier red team: a SHELL-AWARE IK flood. The slotted shell is ARM-FIXED, so where it sits in the torso the arm cannot
be at that pose with the exo on, at ANY ring angle. Step 1: the shell's min skin distance (exact) at all 1432 envelope-grid
nodes (Bench(1,1432) exact; the 360 bench ws nodes cross-check the claim's shellall.json). Step 2: the IK flood (pick 1's
code, this design's knee) with every node whose arm-fixed shell is in the skin (< 0 mm) removed at every k; then every
claimed take is checked for a connected state at its IK k. Edges between nodes stay unchecked (partial)."""
import importlib.util, inspect, json, os, sys, time, numpy as np
REPO = '/home/user/exo-shoulder'; OUT = sys.argv[1]
os.environ['CB_EXACT'] = '1'
sp = importlib.util.spec_from_file_location('ds_s', os.path.join(REPO, 'docs/concepts/models/ikring-distalshell-knuckle-4r.py'))
DS = importlib.util.module_from_spec(sp); sp.loader.exec_module(DS); IK = DS.IK; PT = IK.PT; AA = IK.AA; CB = IK.CB
CL = os.path.join(REPO, 'docs/concepts/verify/ikring-distalshell-knuckle-4r/')
base = json.load(open(CL + 'ik_bench_fixk_perpose.json'))['params']
t0 = time.time(); F = DS.fit(dict(base)); rp = dict(F['rp']); rp.update({k: base[k] for k in base if k in PT.DEF})
G = PT.geometry(F['M1'], F['B1'], F['ax'], rp); arm, car = PT.relay_points(G, F['ax'])
B = CB.Bench(1, 1432); Z = AA.Z0; ws = np.nonzero(np.array(B.kind) == 'ws')[0]
RS = Z['RS'][B.idx].astype(float); Q0 = Z['HG'][B.idx].astype(float); shell = {}
part = OUT.replace('.json', '_shell.json')
if os.path.exists(part): shell = {int(k): v for k, v in json.load(open(part)).items()}
for n, i in enumerate(ws):
    g = int(B.idx[i])
    if g in shell: continue
    wa = (arm @ Q0[i].T) @ RS[i].T; shell[g] = round(float(np.min(B.dist(i, wa))), 3)
    B._skin.pop(i, None); B._ex.pop(i, None)
    if n % 100 == 0:
        json.dump(shell, open(part, 'w')); print(json.dumps(dict(n=n, secs=round(time.time() - t0, 1))), flush=True)
json.dump(shell, open(part, 'w'))
BAD = set(g for g, v in shell.items() if v < 0)
sa = json.load(open(CL + 'shellall.json'))['poses']; Bb = CB.Bench(110, 360)
chk = [abs(shell[int(Bb.idx[o['i']])] - o['shell_mm']) for o in sa if o['kind'] == 'ws']
print(json.dumps(dict(nodes=len(shell), in_skin=len(BAD), xcheck_max_abs=round(max(chk), 3))), flush=True)
src = inspect.getsource(IK.ik_flood)
a = "    okN, AN, PN, SN = table(Ha)\n"; assert a in src
src = src.replace(a, a + "    for _a in range(n):\n        if int(allw[_a]) in BAD: okN[_a, :] = False\n")
src = src.replace('path = os.path.join(VDIR, key)', 'path = OUTP').replace('def ik_flood(', 'def ik_flood_s(')
IK.__dict__['BAD'] = BAD; IK.__dict__['OUTP'] = OUT.replace('.json', '_flood.json')
exec(compile(src, 'ik_flood_s', 'exec'), IK.__dict__)
FL = IK.ik_flood_s(F); print(json.dumps(FL['stats']), flush=True)
cho = json.load(open(CL + 'ik_bench_fixk_choice.json'))['ik']['choice']; pp = json.load(open(CL + 'ik_bench_fixk_perpose.json'))['poses']
lost = []; kept = 0
for p in pp:
    if p['kind'] != 'ws' or not p['taken']: continue
    g = str(int(Bb.idx[p['i']])); c = cho.get(str(p['i'])); k = 0.0 if c is None else float(c['k'])
    nd = FL['nodes'].get(g); ok = nd is not None and any(abs(k - x) < 1e-6 for x in nd['conn'])
    if ok: kept += 1
    else: lost.append(dict(i=p['i'], g=int(g), pose=[p['plane'], p['elev'], p['axial']], k=k, mm=p['min_mm'], shell=shell[int(g)]))
print(json.dumps(dict(kept=kept, lost=lost)), flush=True)
json.dump(dict(stats=FL['stats'], in_skin_nodes=len(BAD), xcheck_max_abs=max(chk), kept=kept, lost=lost,
               shell_hist=dict(lt0=len(BAD), lt1=sum(1 for v in shell.values() if v < 1), lt2=sum(1 for v in shell.values() if v < 2)),
               secs=round(time.time() - t0, 1)), open(OUT, 'w'), indent=1)
print('done', round(time.time() - t0, 1), flush=True)
