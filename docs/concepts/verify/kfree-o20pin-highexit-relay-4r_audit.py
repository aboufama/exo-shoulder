"""audit of kfree-o20pin-highexit-relay-4r: one frozen wear, several R4 hardware variants (no sweep append)"""
import sys, os, json, importlib.util, numpy as np
os.environ["O20_APPEND"] = "0"
MP = "/home/user/exo-shoulder/docs/concepts/models/kfree-o20pin-highexit-relay-4r.py"
sp = importlib.util.spec_from_file_location("o20m", MP); O = importlib.util.module_from_spec(sp); sp.loader.exec_module(O)
ICB, K = O.ICB, O.K
CAP = {}
_g, _w, _r = O.r4_geometry, O.r4_wear, ICB.readings
def g(*a): CAP["g"] = a; return _g(*a)
def w(*a): CAP["w"] = a; return _w(*a)
def r(M, B, phi_b, **kw):
    if "res0" not in CAP: CAP["res0"] = [None if x is None else np.array(x) for x in B.res]
    return _r(M, B, phi_b, **kw)
O.r4_geometry, O.r4_wear, ICB.readings = g, w, r
which = sys.argv[1]; variants = sys.argv[2].split(",")
base = dict(PHI=75.0, tilt=55.0, taz=45.0, sgn=1.0, hw=1, drive=0, wd=84.0, wa=-15.0, b3=0.0, psi2=-14.0)
o = O.run(dict(base), which)
print("BASE", json.dumps({k: o["hw"][k] for k in ("gap", "reach", "follow", "inband14", "contact", "n_contact")}), "ideal", o["kneeless"]["gap"], flush=True)
AR, M1, B1, phi, ax, h0 = CAP["g"]; _, M, B, G0, phi_b, _ = CAP["w"]
nd = len(K.disc_xy(float(h0["boss_r"]), float(h0["step"])))
def score(G, mode):
    ex, jam, jwho = _w(AR, M, B, G, phi_b, ax); nb = len(G["boss"]); nr = len(G["bar"])
    for j, e in ex.items():
        db, dr = e["boss_d"], e["bar_d"]; extra = []
        if mode in ("walls", "perfectbar", "nobarcontact"):
            dwall = db[nd:]; db = db[:nd]
            if dwall.min() < 0: extra.append(float(dwall.min()))
        if mode == "perfectbar": dr = np.full(len(dr), 8.0)
        if mode == "nobarcontact": dr = np.maximum(dr, 2.0)
        lug = [e["lug"]] if e["lug"] < 0 else []
        e["d"] = np.r_[db, dr, extra, lug]
    B.res = [None if x is None else np.array(x) for x in CAP["res0"]]
    hw = _r(M, B, phi_b, extra=ex, jam=jam)["kneeless"]
    return {k: hw[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "n_contact", "near1", "near2", "overhead")}, G["rB"], len(jam) and sum(1 for v in jam.values() if v < 1)
res = {}
for v in variants:
    name, _, q = v.partition(":")
    h = dict(h0)
    if name.startswith("q"): h["q_boss"] = float(q); mode = "walls"
    elif name == "barlow": h["bar_low"] = 1; mode = "walls"
    else: mode = name
    G = G0 if h == h0 else _g(AR, M1, B1, phi, ax, h)
    s, rB, nj = score(G, mode); res[v] = dict(s, rB=rB, jams=nj)
    print("VAR", v, json.dumps(res[v]), flush=True)
json.dump(res, open(sys.argv[3], "w"), indent=0, default=float)
