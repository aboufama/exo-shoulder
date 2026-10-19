import importlib.util, json, math, sys
import numpy as np
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', '..', 'tools')); sys.argv += []
spec = importlib.util.spec_from_file_location('bands', __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'rc_bands.py'))
bd = importlib.util.module_from_spec(spec); spec.loader.exec_module(bd)
rc, K, B, F, HG = bd.rc, bd.K, bd.B, bd.F, bd.HG
for cell in [json.loads(a) for a in sys.argv[1:]]:
    G = rc.Ghost(cell); ok, t, m, th = G.take(HG); Pi = np.nonzero(ok)[0]; j = G.j[1]
    T1 = G.j[0].T(t[Pi, 0]); T12 = T1 @ j.T(t[Pi, 1]); y = t[Pi, 1] * j.r / (1 + j.r); x = t[Pi, 1] / (1 + j.r)
    for name, Rm, D in (('planet', F.RS[Pi] @ T12, bd.band_dirs(j.m0, j.w, math.degrees(-y.max()), math.degrees(-y.min()), 1, j.gb)),
                        ('sun', F.RS[Pi] @ T1, bd.band_dirs(j.c, j.w, math.degrees(x.min()), math.degrees(x.max()), 1, j.ga))):
        Dw = np.einsum('pij,nj->pni', Rm, D); R = K.requirement(B, np.repeat(Pi, Dw.shape[1]), Dw.reshape(-1, 3)).reshape(Dw.shape[:2])
        R = np.where(np.isfinite(R), R, 999); Rp = R.max(1)
        el = np.array([B.poses[i]['elev'] for i in Pi]); pl = np.array([B.poses[i]['plane'] for i in Pi]); kd = np.array([B.kind[i] for i in Pi])
        hi = Rp > 75
        ovw = (kd == 'ws') & (el >= 140); print('  overhead ws taken', int(ovw.sum()), 'of which band > 75 mm', int((ovw & hi).sum()))
        print(name, list(cell), 'Rp pct 50/80/90/95/99', [round(float(np.percentile(Rp, q)), 1) for q in (50, 80, 90, 95, 99)],
              'n>75', int(hi.sum()), 'of', len(Rp), 'clip', int((hi & (kd == 'clip')).sum()), 'elev', el[hi].round().tolist()[:12], 'plane', pl[hi].round().tolist()[:12])
