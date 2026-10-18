"""death audit 3: deltoid-crest-j3-3r selected on the representative envh fast bench (60 clip + 210 env ws, held-out-free)."""
import os, sys, json, time, importlib.util
os.environ["CB_FOLD_MARGIN"] = "5.0"
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
import numpy as np
import env_bench as EB
EB.install()
import concept_bench as CB
spec = importlib.util.spec_from_file_location("dcm", os.path.join(REPO, "docs/concepts/models/deltoid-crest-j3-3r.py"))
DC = importlib.util.module_from_spec(spec); sys.modules["dcm"] = DC; spec.loader.exec_module(DC)
K = DC.K
_B = {}
def envh():
    if "B" in _B: return _B["B"]
    E = json.load(open(os.path.join(REPO, "docs/research/freek_env_polish/envh.json")))
    B60 = K.bench(60, 160); assert B60.mode == "fast"
    cl = [i for i, k in enumerate(B60.kind) if k == "clip"]
    Benv = EB.bench("env", exact=True); ws_pos = E["env_ws_positions"]
    idx = np.r_[np.asarray(B60.idx)[cl], np.asarray(Benv.idx)[ws_pos]]; key = "envh-" + CB._key(idx); assert key == E["key"]
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]
    old = os.environ.get("CB_EXACT"); os.environ["CB_EXACT"] = "1"; os.environ["CB_QUIET_EXACT"] = "1"
    try: B = CB.Bench(20, 20)
    finally:
        if old is None: os.environ.pop("CB_EXACT")
        else: os.environ["CB_EXACT"] = old
    B.idx = idx; B.kind = ["clip"] * len(cl) + ["ws"] * len(ws_pos); B.clip = [str(names[c]) for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in Z["POSE"][idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.mode = "exact"; B.key = key
    d = os.path.join(CB.CACHE, key)
    B.meta = json.load(open(os.path.join(d, "meta.json"))); B.grid = np.load(os.path.join(d, "grid.npy"), mmap_mode="r")
    B._V = np.load(os.path.join(d, "skins.npy"), mmap_mode="r"); B.mode = "fast"
    hidx, _ = EB.held_idx(); assert not (set(idx.tolist()) & set(hidx.tolist())), "held-out pose in envh"
    _B["B"] = B; return B

def ev(p):
    B = envh(); t = time.time()
    try:
        pf, r = DC.evaluate(B, dict(p))
        return float(r["gap"]), {k: r.get(k) for k in ("gap", "near", "reach", "follow", "inband14", "contact", "honest", "in_box")}, time.time() - t
    except Exception as e:
        return 400.0, dict(error=repr(e)), time.time() - t

VG = dict(az=97.467, el=62.7844, a1=40.6347, a2=47.4415, wd=109.3974, wa=-1.1276, sigma=-1, inv2=0, inv3=1, q=0.9581, end_extra=8.0)
CL = dict(az=108.5603, el=64.4969, a1=40.4557, a2=45.9232, wd=104.4082, wa=-0.3864, sigma=-1, inv2=0, inv3=1, q=0.9572, end_extra=2.9522)
if __name__ == "__main__":
    for nm, p in (("vgap_s12_ee8", VG), ("claim_s10", CL)):
        g, r, s = ev(p); print(nm, round(g, 2), json.dumps(r, default=float), f"{s:.1f}s", flush=True)
