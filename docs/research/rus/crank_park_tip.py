"""crank parking for fold-free RUS legs: for each (seat c, arm stud q, beta, gamma-by-stabbing, branch sigma), the crank
centreline rays (alpha 0..beta from c, at the crank angle the leg takes in each valid bench pose) are marched for the
skin requirement (K3: first t >= 15 with dist >= 2 and >= 0 over the next 15 mm, up to 160 mm). Reports the leg's
valid share, the crank-radius need p50 / p90 / max and the share of valid poses where some crank ray never clears
(runs through the trunk or the raised arm within 160 mm)."""
import sys, math, json, importlib.util, numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
spec = importlib.util.spec_from_file_location("hccr", REPO + "/docs/concepts/models/human-closed-crank-rods.py")
H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)
B = H.CB.Bench(60, 160); X = H.Ctx(B); ws = ~X.clip
legs = [((-30, 8), (10, 120), 65), ((-30, 8), (10, 150), 60), ((-30, 8), (10, 105), 65), ((-24, 4), (0, 105), 60),
        ((-24, 4), (10, 90), 65), ((-36, 16), (0, 150), 60), ((-36, 16), (10, 120), 65), ((-30, 12), (20, 120), 65),
        ((-10, 40), (0, 150), 70), ((-24, 78), (0, 120), 80), ((60, 75), (0, 60), 85), ((84, 82), (30, 30), 70)]
out = []
for (az, el), (s, th), beta in legs:
    for sg in (1, -1):
        c = H.bvec(az, el); e1, e2 = H.perp(c); t = math.radians(th)
        q = np.array([0.0, -s, 0.0]) + 61.0 * np.array([-math.sin(t), 0.0, math.cos(t)])
        rT = 100.0
        L, sc = H.stab_L(c, e1, e2, beta, rT, q, sg, X.RS, X.RH, X.w, 15.0)
        D = dict(c=[c] * 3, e1=[e1] * 3, e2=[e2] * 3, beta=[beta] * 3, rT=[rT] * 3, q=[q] * 3, L=[L] * 3, sigma=[sg] * 3)
        K = H.kin(D, X.RS, X.RH, 15.0); ok = K["okk"][:, 0]; I = np.nonzero(ok)[0]
        al = np.radians(np.arange(0, beta + 0.1, 5.0))
        dS = np.cos(al)[:, None] * c + np.sin(al)[:, None] * e1                      # reference crank (theta 0)
        R = H.crank_rot(D, 0, K["th"][I, 0], X.RS[I])
        dd = np.einsum("nij,mj->nmi", R, dS)
        req = X.march(I, 0 * dd, dd, 15.0, 160.0, 2.0)
        mx = np.where(np.isfinite(req), req, 999).max(1); tipn = np.where(np.isfinite(req[:, -1]), req[:, -1], 999); midn = np.where(np.isfinite(req[:, len(al)//2]), req[:, len(al)//2], 999)
        o = dict(seat=[az, el], stud=[s, th], beta=beta, sigma=sg, L=L, leg_valid_ws=round(float(ok[ws].mean()), 3),
                 need_p50=round(float(np.median(mx)), 1), need_p90=round(float(np.percentile(mx, 90)), 1),
                 never_clears=round(float((mx >= 999).mean()), 3), tip_p50=round(float(np.median(tipn)), 1), tip_p90=round(float(np.percentile(tipn, 90)), 1), mid_p50=round(float(np.median(midn)), 1), mid_p90=round(float(np.percentile(midn, 90)), 1), argmax_alpha_p50=round(float(np.degrees(np.median(al[np.argmax(np.where(np.isfinite(req), req, 999), 1)]))), 1))
        out.append(o); print(o, flush=True)
json.dump(out, open("/home/user/exo-shoulder/docs/research/rus/crank_park_tip.json", "w"), indent=1)
