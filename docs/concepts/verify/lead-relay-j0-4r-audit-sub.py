"""Audit of lead-relay-j0-4r (2026-10-18). Run: OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/lead-relay-j0-4r-audit-sub.py
How much relay gain does the J0-J1-J3 sub-chain 5-deg margin cost? Fit bench, ghost + real, margin 5 / 0 / off, seats a0 10/45, 20/45."""
import importlib.util, json, os, sys, time, types
import numpy as np
REPO = "/home/user/exo-shoulder"; src = open(os.path.join(REPO, "docs/concepts/models/lead-relay-j0-4r.py")).read()
assert "F2 = F & (SUB >= 5.0)" in src
src = src.replace("F2 = F & (SUB >= 5.0)", "F2 = F & (SUB >= SUBMIN)")
L = types.ModuleType("lr2"); L.__file__ = os.path.join(REPO, "docs/concepts/models/lead-relay-j0-4r.py"); L.SUBMIN = 5.0
exec(compile(src.replace('if __name__ == "__main__":', 'if False:'), L.__file__, "exec"), L.__dict__)
t = time.time(); M1, P2, fit = L.fit_lead(); B = M1.B
for a0, azu in ((10.0, 45.0), (20.0, 45.0)):
    for sm in (5.0, 0.0, -1e9):
        L.SUBMIN = sm
        W = L.wear(B, M1, P2, a0, azu, log=lambda *x: None)
        rows = [(L.compose(B, W, lo, hi), L.compose(B, W, lo, hi, ghost=True), lo, hi) for lo, hi in L.windows(W)]
        r = min(rows, key=lambda x: x[0]["gap"]); g = min(rows, key=lambda x: x[1]["gap"])
        print(json.dumps(dict(a0=a0, azu=azu, submin=sm, cand=len(W["cand"]), real_best=r[0]["gap"], real_win=[r[2], r[3]], real_ib=r[0]["inband14"],
                              real_relay=[r[0]["relay_taken"], r[0]["relay_contact"]], ghost_best=g[1]["gap"], ghost_win=[g[2], g[3]],
                              ghost_relay=[g[1]["relay_taken"], g[1]["relay_contact"]], secs=round(time.time() - t))), flush=True)
