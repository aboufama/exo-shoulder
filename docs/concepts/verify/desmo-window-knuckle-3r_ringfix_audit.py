"""audit: desmo-window-knuckle-3r with the stage-1 ring2 sector sampled at the kit's convention (2 mm x 2 mm = 1 pt / 4 mm2,
tools/concept_kit.py line 293) instead of 0.5 mm radial x 2 mm arc (1 pt / 1 mm2, 4x denser than every other member).
Keeps the sampled ring nearest the sector's mid radius (2 mm arc spacing, as the sampler builds it): conservative (it represents
>= the sector's true area). usage: ringfix.py check|wear <bench|held> <out> [--orig]"""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
argv = list(sys.argv); sys.argv = [argv[0]]
sp = importlib.util.spec_from_file_location("dwmod", os.path.join(REPO, "docs/concepts/models/desmo-window-knuckle-3r.py"))
MOD = importlib.util.module_from_spec(sp); sp.loader.exec_module(MOD)
sys.argv = argv
S = MOD.S; unit = S.unit
ORIG = "--orig" in argv
INFO = {}
_orig = MOD.WModel._desmo_build_B
def patched(self):
    _orig(self)
    if ORIG or "ring2" not in self.rigid: return
    m, X = self.rigid["ring2"]; dsm = self._desmo; u2 = unit(dsm["u2"])
    Xp = X - np.outer(X @ u2, u2); r = np.linalg.norm(Xp, axis=1)
    rings = np.unique(np.round(r, 3)); rmid = 0.5 * (S.HUB_R + float(dsm["r_out"]))
    rk = rings[np.argmin(np.abs(rings - rmid))]; keep = np.abs(r - rk) < 1e-3
    self.rigid["ring2"] = (m, X[keep])
    INFO.update(n_before=int(len(X)), n_after=int(keep.sum()), rings=[float(x) for x in rings], kept_ring=float(rk),
                r_out=float(dsm["r_out"]), area_mm2=None)
MOD.WModel._desmo_build_B = patched
cmd = argv[1]
if cmd == "check":
    P = json.loads(argv[2]) if len(argv) > 2 and not argv[2].startswith("--") else {}
    out, M, B = MOD.check(P); out["ringfix"] = dict(INFO, orig=ORIG); print(json.dumps(out, default=float))
elif cmd == "wear":
    which, path = argv[2], argv[3]; P = dict(MOD.BEST); P.update(dict(blend=8.0, a_s=9.9, psi=150.0))
    t = time.time(); res = MOD.VER.wear(P, which, False, path.replace(".json", "_dump.json"))
    fit, M1, M, B, r = MOD.VER.CAP["res"]
    res.update(id="desmo-window-knuckle-3r", audit="ring2 at the kit's 1 pt / 4 mm2 (ringfix.py)" if not ORIG else "orig",
               exact=os.environ.get("CB_EXACT") == "1", params=P, ringfix=dict(INFO, orig=ORIG), window_gates=MOD.gates(M1), secs_total=round(time.time() - t, 1))
    json.dump(res, open(path, "w"), indent=1, default=float)
    print(json.dumps({k: res.get(k) for k in ("frozen", "fit_fast", "why", "near1", "minmetal", "ringfix")}, default=float))
