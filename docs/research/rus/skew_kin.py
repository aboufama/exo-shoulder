"""M2 kinematic screen: skin-normal (skew, off-GH) crank RSS legs vs GH-centred spherical cranks.
For a crank circle of centre O (S-fixed), radius rho, a leg closes iff |Q - O| in [dmin, dmax] of the circle
(<= 2 rho wide). Best rod length = best window (interval stabbing). Measures the share of bench workspace poses a leg
can close in, for compact skin-normal cranks (rho 15-30 mm, centre on the skin seat + 10 mm) vs the GH-centred crank."""
import sys, os, json, math, importlib.util, numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
spec = importlib.util.spec_from_file_location("hccr", REPO + "/docs/concepts/models/human-closed-crank-rods.py")
H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)
B = H.CB.Bench(60, 160); X = H.Ctx(B); ws = ~X.clip
I = np.arange(X.n); res = []
def skin_r(u):   # skin radius along S-direction u over ws poses (median of the K3 march from GH)
    d = np.einsum("nij,j->ni", X.RS, u)[:, None, :]
    req = X.march(I, 0 * d, d, 15.0, 220.0, 2.0)[:, 0]
    return float(np.median(req[np.isfinite(req)]))
seats = [(-30, 8), (-24, 4), (-24, 78), (84, 82), (60, 75), (-10, 40), (150, 40), (96, 64)]
studs = [(30, 75), (50, 75), (80, 45), (110, 45), (160, 20), (50, -20), (100, -15)]
for az, el in seats:
    u = H.bvec(az, el); rs = skin_r(u)
    for s, thd in studs:
        th0 = math.radians(thd); nq = np.array([-math.sin(th0), 0.0, math.cos(th0)])
        q = np.array([0.0, -s, 0.0]) + 50.0 * nq            # stud ~50 mm from the humerus axis (arm surface + saddle)
        Q = np.einsum("nij,j->ni", X.RH, q)
        for rho in (15.0, 20.0, 30.0):
            O = np.einsum("nij,j->ni", X.RS, (rs + 10.0) * u)          # skew crank centre: skin seat + 10 mm, axis = seat normal
            dist = np.linalg.norm(Q - O, axis=1)[ws]
            # circle of radius rho about O: |T-Q| in [sqrt(a^2+(b-rho)^2), sqrt(a^2+(b+rho)^2)], a = axial, b = radial offset of Q
            n = np.einsum("nij,j->ni", X.RS, u)[ws]; v = (Q - O)[ws]; a = (v * n).sum(1); b = np.linalg.norm(v - a[:, None] * n, axis=1)
            lo = np.sqrt(a * a + (b - rho) ** 2); hi = np.sqrt(a * a + (b + rho) ** 2)
            Ls = np.arange(5, 260, 1.0); cov = ((Ls[:, None] >= lo[None]) & (Ls[:, None] <= hi[None])).mean(1)
            # GH-centred spherical crank with the same tip angle beta = asin(rho / r_T) is NOT the comparison; the GH crank
            # with beta 50-65 (same leg seat / stud) is M1's own number (fold band share from leg_fold)
            res.append(dict(seat=[az, el], skin_r=round(rs, 1), stud=[s, thd], rho=rho, dist_range=[round(float(dist.min()), 1), round(float(dist.max()), 1)],
                            best_cover=round(float(cov.max()), 3), L=float(Ls[cov.argmax()])))
    print(az, el, round(rs, 1), max(r["best_cover"] for r in res if r["seat"] == [az, el]), flush=True)
# GH-centred: angular band share for beta, best gamma (orientation-level, as ends.json)
gh = []
for az, el in seats:
    c = np.einsum("nij,j->ni", X.RS, H.bvec(az, el))
    for s, thd in studs:
        th0 = math.radians(thd); q = np.array([0.0, -s, 0.0]) + 50.0 * np.array([-math.sin(th0), 0.0, math.cos(th0)])
        Qd = np.einsum("nij,j->ni", X.RH, H.unit(q)); ang = np.degrees(np.arccos(np.clip((c * Qd).sum(1), -1, 1)))[ws]
        for beta in (15, 20, 30, 50, 65):
            g = np.arange(0, 180, 1.0); lo = np.abs(beta - g) + 10; hi = np.minimum(beta + g, 360 - beta - g) - 10
            cov = ((ang[None] >= lo[:, None]) & (ang[None] <= hi[:, None])).mean(1)
            gh.append(dict(seat=[az, el], stud=[s, thd], beta=beta, cover=round(float(cov.max()), 3), gamma=float(g[cov.argmax()]), ang=[round(float(ang.min()), 1), round(float(ang.max()), 1)]))
out = dict(skew=res, gh=gh)
json.dump(out, open(REPO + "/docs/research/rus/skew_kin.json", "w"), indent=1)
for rho in (15.0, 20.0, 30.0):
    print("skew rho", rho, "best cover", max(r["best_cover"] for r in res if r["rho"] == rho), "median", float(np.median([r["best_cover"] for r in res if r["rho"] == rho])))
for beta in (15, 20, 30, 50, 65):
    print("GH beta", beta, "best cover", max(r["cover"] for r in gh if r["beta"] == beta), "median", float(np.median([r["cover"] for r in gh if r["beta"] == beta])))
