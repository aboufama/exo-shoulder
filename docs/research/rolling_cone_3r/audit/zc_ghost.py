"""audit probe: rolling-cone-3r ghost at the zc-frontier rigid 3R seats (J3 through GH, rigid cuff)"""
import importlib.util, json, math, sys, time, os
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
spec = importlib.util.spec_from_file_location("rc", REPO + "/docs/concepts/models/rolling-cone-3r.py")
RC = importlib.util.module_from_spec(spec); spec.loader.exec_module(RC)
import concept_kit as K, concept_bench as CB
ZC = dict(az=109.3565, el=65.94, a1=36.7226, a2=69.0575, wd=85.7423, wa=-16.1921, sigma=-1)

def zc_axes(z=ZC, Qr=None):
    u1 = K.unit(K.bvec(z["az"], z["el"])); u3h = K.unit(K.wdir(z["wd"], z["wa"]))
    if Qr is None: Qr = np.eye(3)
    d3 = Qr @ u3h
    p, ok, m = K.closure(u1[None], d3[None], z["a1"], z["a2"], z["sigma"], margin_deg=-90)
    return u1, K.unit(p[0]), d3, u3h, Qr, float(m[0]), float(np.degrees(np.arccos(np.clip(u1 @ d3, -1, 1))))

class ZGhost(RC.Ghost):
    def __init__(self, cell, Qr=None, z=ZC):
        u1, u2, d3, u3h, Q0, m, th = zc_axes(z, Qr); self.cell = cell; self.rigid = True
        mk = lambda k, w: RC.Joint(w, **cell[k]) if cell.get(k) else RC.Joint(w)
        self.j = [mk("J1", u1), mk("J2", u2), mk("J3", d3)]; self.branch = z["sigma"]
        self.d3 = d3; self.u3h = u3h; self.Q0 = Q0; self.A = dict(u1=u1)
        self.ref_margin = m; self.ref_th = th

def run(cell, nc, nw, Qr=None, z=ZC):
    G = ZGhost(cell, Qr, z)
    orig = RC.Ghost
    RC_Ghost_init = RC.Ghost
    # reuse RC.run's machinery by monkeypatching the Ghost constructor
    RC.Ghost = lambda c, s: G
    try: res, d = RC.run(cell, nc, nw)
    finally: RC.Ghost = orig
    res["ref_margin"] = G.ref_margin; res["ref_th"] = G.ref_th
    return res, d

if __name__ == "__main__":
    cell = json.loads(sys.argv[1]); nc, nw = int(sys.argv[2]), int(sys.argv[3])
    Qr = None
    if len(sys.argv) > 4 and sys.argv[4] == "rest":
        spec2 = importlib.util.spec_from_file_location("osn", REPO + "/docs/concepts/models/offset-skin-normal-3r.py")
        OSN = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(OSN); Qr = OSN.rest()["Q0"]
    t0 = time.time(); res, d = run(cell, nc, nw, Qr); res["sec"] = round(time.time() - t0, 1)
    print(json.dumps(dict(cell=cell, **{k: v for k, v in res.items()})))
