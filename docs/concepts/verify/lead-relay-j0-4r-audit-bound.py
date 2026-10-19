"""Audit of lead-relay-j0-4r (2026-10-18). Run: OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/lead-relay-j0-4r-audit-bound.py out.json
Optimistic bound per (a0, azu, r0): the lead's fit-bench records with (a) every taken pose where hub 0 comes within 1 mm of a
chain sample LOST (the bench's part rule), (b) hub 0's underside disc (1 / 4 mm2) appended to every pose's metal record
(link 0 omitted = optimistic), (c) hub 0 into the skin on a pose = contact. No relay gain (subtract the best measured ghost
gain, 4.48 on the fit bench, for the bound)."""
import importlib.util, json, math, os, sys, time
import numpy as np
REPO = "/home/user/exo-shoulder"
sp = importlib.util.spec_from_file_location("lr", os.path.join(REPO, "docs/concepts/models/lead-relay-j0-4r.py"))
L = importlib.util.module_from_spec(sp); sp.loader.exec_module(L)
import concept_kit as CK
t = time.time(); M1, P2, fit = L.fit_lead()
B = M1.B; u1 = M1.D.u[0]
mem = {k: m for k, (m, X) in list(M1.cyl_surf.items()) + list(M1.rigid.items()) + list(M1.strap.items())}
base = list(B.res)
tk = [i for i in range(len(B.idx)) if base[i] is not None and float(np.min(base[i])) >= 0]
P = {i: [(X, h) for k, X, h in L.member_pts(M1, i) if mem.get(k) != 0] for i in tk}
P0 = [(X, h) for k, X, h in L.member_pts(M1, tk[0]) if mem.get(k) == 0]
dxy = CK.disc_xy(L.HUB_R, 2.0)
out = []; GHOST_GAIN = 12.50 - 8.02
for a0 in (10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0):
    for azu in np.arange(0, 360, 15.0):
        c = L.relay_axis(u1, a0, azu)
        if not bool(L.seat_ok(c)[0]): continue
        e, f = L.frame_of(c); und = dxy[:, :1] * e + dxy[:, 1:] * f
        for r0 in np.arange(44.0, 92.0, 2.0):
            if min(float(L.sd_cyl(X, r0 * c, c).min()) - h for X, h in P0) < 1.0: continue
            U = r0 * c + und
            res = []
            for i in range(len(B.idx)):
                r = base[i]
                if r is None: res.append(None); continue
                if i in P and min(float(L.sd_cyl(X, r0 * c, c).min()) - h for X, h in P[i]) < 1.0: res.append(None); continue
                d = B.dist(i, U @ M1.RS[i].T); res.append(np.r_[r, d])
            B.res = res; rep = B.report(); B.res = base
            out.append(dict(a0=a0, azu=float(azu), r0=float(r0), gap=rep["gap"], bound=round(rep["gap"] - GHOST_GAIN, 2), reach=rep["reach"], follow=rep["follow"],
                            ib14=rep["inband14"], contact=rep["contact"]))
    print(a0, len(out), round(time.time() - t), flush=True)
json.dump(out, open(sys.argv[1], "w"), indent=1)
out.sort(key=lambda r: r["gap"])
for r in out[:20]: print(r)
