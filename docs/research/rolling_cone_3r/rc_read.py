"""read cells on Bench(110,360): ws / clip (continuity) / overhead, rim arcs, contact walk, attribution vs controls"""
import importlib.util, json, math, sys
import numpy as np
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', '..', 'tools'))
spec = importlib.util.spec_from_file_location('rc', __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'concepts', 'models', 'rolling-cone-3r.py'))
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
D2R = math.pi / 180
def arcs(G, t, ok):
    out = []
    for k, j in enumerate(G.j):
        if j.kind != 'roll': out.append(None); continue
        tk = t[ok, k]; x = tk / (1 + j.r); y = tk * j.r / (1 + j.r)
        R = 60.0
        out.append(dict(t=[round(float(np.degrees(tk.min())), 1), round(float(np.degrees(tk.max())), 1)],
                        sun_arc_deg=round(float(np.degrees(np.ptp(x))), 1), planet_arc_deg=round(float(np.degrees(np.ptp(y))), 1),
                        walk_mm_at_R60=round(float(R * math.sin(j.ga * D2R) * np.ptp(x)), 1),
                        sun_pitch_r_mm=round(R * math.sin(j.ga * D2R), 1), planet_pitch_r_mm=round(R * math.sin(j.gb * D2R), 1)))
    return out
if __name__ == '__main__':
    cells = [json.loads(l) for l in sys.argv[1:]]
    ctrl = {}
    for c in cells:
        res, X = rc.run(c)
        ok = X['ok']; ws = X['ws']; P = X['B'].poses
        res['arcs'] = arcs(X['G'], X['t'], ok)
        res['min_margin_taken'] = round(float(X['m'][ok].min()), 2)
        if not ctrl: ctrl = dict(ok=ok.copy())
        else:
            add = ok & ~ctrl['ok'] & ws; lost = ~ok & ctrl['ok'] & ws
            ax = np.array([p['axial'] for p in P]); el = X['elev']
            res['vs_first'] = dict(added=int(add.sum()), lost=int(lost.sum()),
                                   added_elev=[round(float(np.percentile(el[add], q)), 0) for q in (10, 50, 90)] if add.any() else None,
                                   added_axial=[round(float(np.percentile(ax[add], q)), 0) for q in (10, 50, 90)] if add.any() else None)
        print(json.dumps(dict(cell=c, **res)), flush=True)
