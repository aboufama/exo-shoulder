"""Audit of pinknee-scapular-relay-4r: host alone, relay with NO hub 0 / link 0 metal (ghost) = upper bound of what the relay can add, and real metal.
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/pinknee-scapular-relay-4r-audit.py host|ghost|real '[{...params}]' [--noseat]"""
import importlib.util, json, os, sys, time
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")); sys.path.insert(0, REPO + "/tools")
import numpy as np
spec = importlib.util.spec_from_file_location("rm", REPO + "/docs/concepts/models/pinknee-scapular-relay-4r.py")
RM = importlib.util.module_from_spec(spec); spec.loader.exec_module(RM)
PK = RM.PK; CB = RM.CB
NOSEAT = "--noseat" in sys.argv
if NOSEAT: RM.seat_ok = lambda U: np.ones(len(np.atleast_2d(U)), bool)

class Ghost(RM.Model):
    def fit(self): PK.Model.fit(self)
    def greedy_drop(self, keep0=None, links=True): return PK.Model.greedy_drop(self, keep0=keep0, links=links)
    def finalize(self): PK.Model.finalize(self); self.f0 = 0.0
    def collide(self, i): return PK.Model.collide(self, i)

RM.Model_orig = RM.Model
which = sys.argv[1]
if which == "ghost": RM.Model = Ghost
B = CB.Bench(n_clip=60, n_ws=160)
for par in json.loads(sys.argv[2]):
    t = time.time()
    if which == "host":
        r, M = PK._report(B, dict(RM.H1, **par)); extra = {}
    else:
        r, M = RM._report(B, par); extra = {k: r.get(k) for k in ("relay", "overhead", "T_eff", "c_azel", "c_seat_ok", "th_margin_min")}
    print(json.dumps(dict(which=which, noseat=NOSEAT, par=par, **{k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
                          why=r.get("why"), parts=r.get("parts_pairs"), f=r.get("f"), secs=round(time.time() - t, 1), mode=B.mode, **extra), default=float), flush=True)
