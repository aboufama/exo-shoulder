"""Concept model: FAR-END POSTERIOR 3R (id far-end-posterior-3r).

Plain spherical 3R (3 active pins on O20 bearing hubs, 0 passive DOF) on the fold-free POSTERIOR J1 line found by the
far-end scan (J1 = bvec(-24, 4): a horizontal line pointing straight back from GH; J3 on the posterior arm, wdir(80, -90);
arcs 65 / 65; fold band [10, 120] deg holds on 100 % of workspace and clip poses), with the hub of EACH axis free to sit
at either end of its line (e1, e2, e3 = +1 / -1: e1 = -1 puts hub 1 on the FRONT of the shoulder, e3 = -1 hub 3 on the
anterior arm, e2 = -1 hub 2 across GH from its closure direction) and raglan-routed links (one planform turn per link,
fixed in the link). The builder is the raglan-routed-3r builder (docs/concepts/models/raglan-routed-3r.py, same parts,
same checks); this file only sets the layout and its sweep space.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/far-end-posterior-3r.py [check|map] ['<json params>']
"""
import importlib.util, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("raglan_routed_3r", os.path.join(HERE, "raglan-routed-3r.py"))
R = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(R)
K = R.K
ID = "far-end-posterior-3r"
NAME = "Far-end posterior 3R (fold-free posterior J1 line, hubs at either end of their axis lines, raglan-routed links)"
PARAMS = dict(R.PARAMS, az=-24.0, el=4.0, a1=65.0, a2=65.0, wd=80.0, wa=-90.0, sigma=1, e1=1, e2=1, e3=1, q=0.95)
build = R.build


def evaluate(B, params):
    p = dict(PARAMS); p.update(params or {}); return p, K.evaluate(B, build, p)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = dict(PARAMS); par.update(json.loads(sys.argv[2]) if len(sys.argv) > 2 else {})
    B = K.bench(60, 160); t0 = time.time()
    if mode == "map":
        M = R.raglan_map(B, par); M["params"] = par
        M["routes"] = {k: [R.best_route(M, k, "top"), R.best_route(M, k, "ceiling")] for k in ("link1", "link2")}
        print(json.dumps(M["routes"])); json.dump(M, open(sys.argv[3] if len(sys.argv) > 3 else "/dev/stdout", "w")); sys.exit()
    r = K.evaluate(B, build, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "inband_member", "link_span_deg", "mass_g", "honest", "audit")}, f"{time.time() - t0:.0f}s")
