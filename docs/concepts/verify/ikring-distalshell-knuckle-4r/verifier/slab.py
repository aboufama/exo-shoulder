"""verifier: the X2 bracket hits (knee member vs the bracket's 2 mm top layer) re-read EXACTLY. The L-lug bracket is a
2 x 10 Ti slab: underside r_u(s) = r_a + (r_b - r_a) u from the carriage edge s_a to the pad edge s_pe, top r_u + 2, at
the pad azimuth +- 5 mm (lbr 1). Every chain set's signed distance to that slab volume in (r, s, arc) - no sample
spacing allowance - on the claim's final wear (same choice, same flood cmap as vw.py). Adjacent pair (knee member, pinned
to the pad that the bracket carries): running gap 0.15 mm; non-adjacent 1.0 mm."""
import importlib.util, json, math, os, sys, time, numpy as np
REPO = '/home/user/exo-shoulder'; OUT = sys.argv[1]; CHO = sys.argv[2]
os.environ['CB_EXACT'] = '1'
sp = importlib.util.spec_from_file_location('ds_b', os.path.join(REPO, 'docs/concepts/models/ikring-distalshell-knuckle-4r.py'))
DS = importlib.util.module_from_spec(sp); sp.loader.exec_module(DS); IK = DS.IK; PT = IK.PT; AA = IK.AA
VD = os.path.join(REPO, 'docs/concepts/verify/ikring-distalshell-knuckle-4r/verifier'); IK.VDIR = VD
CL = os.path.join(REPO, 'docs/concepts/verify/ikring-distalshell-knuckle-4r/')
base = json.load(open(CL + 'ik_bench_fixk_perpose.json'))['params']; D2R = math.pi / 180
F = IK.fit(dict(base)); hw = dict(base)
Bf = IK.subbench(IK.CB.Bench(110, 360), np.arange(470)); nZ = len(AA.Z0['HG']); ws = np.array(Bf.kind) == 'ws'
prev = json.load(open(CHO)); phiF = np.zeros(nZ)
for j, c in prev['ik']['choice'].items():
    k = c['k'] if (c['k'] == 0 or c['takes']) else 0.0; phiF[Bf.idx[int(j)]] = k
FL = IK.ik_flood(F); cmap = {}
for j in np.nonzero(ws)[0]:
    g = str(int(Bf.idx[j])); nd = FL['nodes'].get(g); kk = float(phiF[Bf.idx[j]])
    cmap[int(g)] = bool(nd is not None and any(abs(kk - x) < 1e-6 for x in nd['conn']))
o, S = IK.wear_phi(F, Bf, phiF, hw, cmap=cmap); M, B = S['M'], S['B']; ax = S['ax']
rp = dict(S['rp']); rp.update({k: hw[k] for k in hw if k in PT.DEF}); G = PT.geometry(S['M1'], S['B1'], ax, rp); PT.relay_points(G, ax)
s0, Rt = G['s0'], G['R_t']; sg = 1.0 if G['s_pad'] > s0 else -1.0; s_a = s0 + sg * 0.5 * PT.CAR_L; s_b = G['s_pe']
r_a = Rt + G['h_c']; r_b = G['rpad']; hb = 5.0 / Rt / D2R; tm = G['th0_pad'] if G.get('lbr', 0) else None
assert tm is not None
lo_s, hi_s = min(s_a, s_b), max(s_a, s_b)
def slab_d(h):
    sv = h @ ax; rr = np.linalg.norm(AA._rad(h, ax), axis=1); az = np.degrees(np.arctan2(h @ G['f'], h @ G['e']))
    azr = (az - tm + 180.0) % 360.0 - 180.0
    u = np.clip((sv - s_a) / (s_b - s_a), 0, 1); ru = r_a + (r_b - r_a) * u; rt = ru + 2.0
    dr_out = np.maximum(rr - rt, ru - rr); ds_out = np.maximum(lo_s - sv, sv - hi_s); da_out = (np.abs(azr) - hb) * D2R * rr
    outside = np.sqrt(np.maximum(dr_out, 0) ** 2 + np.maximum(ds_out, 0) ** 2 + np.maximum(da_out, 0) ** 2)
    inside = np.maximum(np.maximum(dr_out, ds_out), da_out)       # <= 0 inside: minus the depth to the nearest face
    return np.where(outside > 0, outside, inside), rr - ru, sv
names = list(M.rigid) + list(M.link_pts); parts = list(M.rigid.values()) + list(M.link_pts.values())
sets = [(nm, m, X) for nm, (m, X) in zip(names, parts)] + [(f"c{k}:m{m}", m, Pc) for k, (m, Pc) in enumerate(M.contact) if len(Pc)]
pad_m = M.rigid['pad'][0]; knee_m = M.rigid['knee'][0]
per = {}; rows = []
for i in range(len(B.idx)):
    if B.res[i] is None or float(np.min(B.res[i])) < 0: continue
    RS, Qp = M.RS[i], M.Q[i]; worst = None
    for nm, m, X in sets:
        if m == pad_m: continue
        h = (M.world(m, i, X) @ RS) @ Qp; d, hgt, sv = slab_d(h); k = int(np.argmin(d)); dv = float(d[k])
        lim = 0.15 if m == knee_m else 1.0
        e = per.setdefault(nm, dict(min=1e9, i=None, n_lt_lim=0, lim=lim, adj=m == knee_m))
        if dv < e['min']: e.update(min=round(dv, 3), i=i, h_over_underside=round(float(hgt[k]), 3), s=round(float(sv[k]), 2))
        if dv < lim: e['n_lt_lim'] += 1
        if dv < lim and (worst is None or dv < worst[1]): worst = (nm, round(dv, 3), round(float(hgt[k]), 3))
    if worst: rows.append(dict(i=i, kind=B.kind[i], pose=[B.poses[i][q] for q in ('plane', 'elev', 'axial')], worst=worst))
lost = [r['i'] for r in rows]
for j in lost: B.res[j] = None
rr_ = B.report(); rep = {k: rr_[k] for k in ('gap', 'reach', 'follow', 'inband14', 'inband10', 'contact')}
out = dict(geom=dict(s_a=s_a, s_b=s_b, r_a=r_a, r_b=r_b, hb_deg=hb, th0_pad=tm), per_set={k: v for k, v in sorted(per.items(), key=lambda kv: kv[1]['min'])[:12]},
           n_jam=len(rows), n_jam_ws=sum(1 for r in rows if r['kind'] == 'ws'), rows=rows[:40], rescored=rep)
json.dump(out, open(OUT, 'w'), indent=1, default=float); print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, default=float), flush=True)
