import importlib.util, json, sys
import numpy as np
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', '..', 'tools'))
spec = importlib.util.spec_from_file_location('rc', __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'concepts', 'models', 'rolling-cone-3r.py'))
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
cells = [json.loads(a) for a in sys.argv[1:]]
for c in cells:
    res, X = rc.run(c); P = X['B'].poses; ws = X['ws']; ok = X['ok']
    pl = np.array([p['plane'] for p in P]); el = np.array([p['elev'] for p in P]); ax = np.array([p['axial'] for p in P])
    cats = dict(rest=ws & (el <= 30), overhead=ws & (el >= 140), across=ws & (pl >= 110) & (el >= 45) & (el < 140),
                behind=ws & (pl <= -20), IRge90=ws & (ax <= -90), ERge60=ws & (ax >= 60))
    out = {k: f"{int((ok & m).sum())}/{int(m.sum())}" for k, m in cats.items()}
    # the fold side of each lost ws pose: stretched (th above the window) or folded
    lost = ws & ~ok; th = X['th']; mid = np.median(th[ok])
    out['lost_stretched'] = int((lost & (th > mid)).sum()); out['lost_folded'] = int((lost & (th <= mid)).sum())
    print(json.dumps(dict(cell=c, ws=res['ws'], clip=res['clip'], over=res['over'], cats=out)), flush=True)
