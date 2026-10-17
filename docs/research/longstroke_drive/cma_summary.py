"""summarise farm CMA runs (tools/concept_cma.py outputs): per run the start / best objective (2 mm near-touch gap,
Bench(60,160) fast), best plain, the drive stroke, and the convergence gate (score points = gap / 2.75): gain over the
second half of the tries, over the last third, top-5 spread.
    python3 docs/research/longstroke_drive/cma_summary.py farm/cma_*.json"""
import json, sys
import numpy as np


def gate(objs):
    o = np.minimum.accumulate(np.asarray(objs, float)); n = len(o)
    if n < 6: return None
    g2 = (o[n // 2 - 1] - o[-1]) / 2.75; g3 = (o[(2 * n) // 3 - 1] - o[-1]) / 2.75
    top = np.sort(np.asarray(objs, float))[:5]; sp = (top[-1] - top[0]) / 2.75
    return dict(evals=n, gain_2nd_half_pts=round(float(g2), 2), gain_last_third_pts=round(float(g3), 2), top5_spread_pts=round(float(sp), 2),
                passes=bool(g2 < 1.0 and g3 < 0.5 and sp < 3.0))


allrows = []
for fn in sys.argv[1:]:
    R = json.load(open(fn)); objs = [r.get("obj", 400) for r in R]
    if not R: continue
    b = min(R, key=lambda r: r.get("obj", 400)); rep = b.get("report") or {}; c = rep.get("cam") or {}
    print(f"== {fn}: {len(R)} evals; start {R[0].get('obj')}; best {b.get('obj')} plain {(rep.get('plain') or {}).get('gap')} "
          f"reach {rep.get('reach')} ib {rep.get('inband14')} contact {rep.get('contact')} dK_lim {c.get('dK_lim')} ({c.get('why_lim')}) "
          f"trans {c.get('trans_min_taken')} honest {rep.get('honest')}")
    print("   gate", gate(objs))
    print("   best params", json.dumps({k: v for k, v in (b.get("params") or {}).items() if k in (
        "La", "s_arm", "r_h", "beta", "gam", "hl", "zr", "kK", "r_lobe", "bk1", "bk2", "a1max", "smhi", "g", "r_c", "lift", "nose_r", "mu", "law_in", "kA", "kB", "t1", "smt")}))
    allrows += R
if len(sys.argv) > 2:
    print("== combined gate (eval order within runs concatenated)", gate([r.get("obj", 400) for r in allrows]))
