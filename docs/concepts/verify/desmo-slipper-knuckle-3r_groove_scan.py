"""desmo-slipper-knuckle-3r verifier probe (fast-bench fit): the crank-FREE groove play scanned densely (every 0.25 deg of the K law,
both directions, union-of-discs groove = the claim's own _corner_slop test) + the centreline radius profile + a FRAME check (the pin carried
by the crank vs the groove centreline in link 2's frame on every kin_ok pose).  python3 <this> [--blend] [a_s=9.5 psi=150 ...] (the scan JSON lands next to this file)"""
import importlib.util, json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")); sys.path.insert(0, os.path.join(REPO, "tools"))
os.environ.pop("CB_EXACT", None); os.environ["SN_CELL"] = "lead"
import concept_bench as CB
sp = importlib.util.spec_from_file_location("dsv_probe", os.path.join(REPO, "docs/concepts/verify/desmo-slipper-knuckle-3r.py"))
VH = importlib.util.module_from_spec(sp); sp.loader.exec_module(VH); DS = VH.DS
S, RF = DS.S, DS.RF
row = json.load(open(os.path.join(REPO, "docs/concepts/rows/desmo-slipper-knuckle-3r.json"))); P = dict(row["best_params"])
for a in [a for a in sys.argv[1:] if "=" in a]:
    k, v = a.split("="); P[k] = float(v) if k not in ("wall_rows",) else v
CAP = {}
orig = DS.DSModel._corner_slop
def cap(F0, dR, u2, sig, gg, cc, s_th, Kb, x, G2, lim):
    CAP.update(F0=F0, dR=dR, u2=u2, sig=sig, gg=gg, cc=cc, s_th=s_th, Kb=Kb, x=x, G2=G2, lim=lim)
    return orig(F0, dR, u2, sig, gg, cc, s_th, Kb, x, G2, lim)
DS.DSModel._corner_slop = staticmethod(cap)
B = CB.Bench(n_clip=60, n_ws=160)
r, M = DS._report(B, P)
info = (r.get("cam") or {}).get("desmo") or {}
C = CAP; F0, dR, u2, sig, gg, cc, s_th, Kb, x, G2, lim = (C[k] for k in ("F0", "dR", "u2", "sig", "gg", "cc", "s_th", "Kb", "x", "G2", "lim"))
used = Kb <= lim + 1e-12
# centreline radius profile (link-2 frame, planar projection as the model)
bx = DS.unit(G2[0] - (G2[0] @ u2) * u2); by = np.cross(u2, bx); gx, gy = G2 @ bx, G2 @ by
dx, dy = np.gradient(gx), np.gradient(gy); ddx, ddy = np.gradient(dx), np.gradient(dy)
kap = (dx * ddy - dy * ddx) / np.maximum((dx ** 2 + dy ** 2) ** 1.5, 1e-12); rc = 1.0 / np.maximum(np.abs(kap), 1e-9)
ds = np.hypot(dx, dy)
prof = []
for j in np.nonzero(used)[0][::max(1, int(used.sum() // 80))]:
    prof.append((round(math.degrees(x[j]), 2), round(math.degrees(Kb[j]), 2), round(float(rc[j]), 3), round(float(ds[j]) / math.radians(0.25) * 180 / math.pi * 0 + float(ds[j]), 4)))
jmin = int(np.argmin(np.where(used, rc, 99)))
T = cKDTree(G2[used]); e1, f1 = S.frame_of(u2); thc = np.radians(np.arange(0, 360, 4))
Kof = lambda xx: float(np.interp(xx, x, Kb))
def play(x0, sgn):
    K0 = Kof(x0); Rq = DS._rot(u2, -(s_th * x0))
    def outside(dd):
        K = K0 + sgn * math.radians(dd)
        c = Rq @ (DS._rot(dR, sig * float(RF.phi_of(K, gg, cc))) @ F0)
        d, _ = T.query(c[None] + (DS.PIN_D / 2) * (np.cos(thc)[:, None] * e1 + np.sin(thc)[:, None] * f1))
        return float(d.max()) > DS.GROOVE_W / 2 + 1e-6
    lo, hi = 0.0, 0.01
    if outside(0.0): return 0.0, True
    while hi < 8.0 and not outside(hi): lo, hi = hi, hi + 0.01
    for _ in range(5):
        mid = (lo + hi) / 2
        if outside(mid): hi = mid
        else: lo = mid
    return hi, False
xs = np.arange(-6.0, math.degrees(lim) + 1e-9, 0.25)
rows = []; worst = (0, None)
for x0d in xs:
    x0 = math.radians(x0d); K0 = Kof(x0)
    pp, inside0 = play(x0, 1); pm, _ = play(x0, -1)
    one = pp if K0 <= 1e-9 else max(pp, pm)
    rows.append((round(x0d, 2), round(math.degrees(K0), 3), round(pp, 3), round(pm, 3)))
    if one > worst[0]: worst = (one, (round(x0d, 2), round(math.degrees(K0), 3), round(pp, 3), round(pm, 3)))
# frame check: the pin carried by the crank (member 9) vs the groove centreline in link 2's frame, every kin_ok pose
dm = M._desmo; F0w = dm["F0"]; q_on = dm["q_on"]; mL2 = M.link_pts["L2"][0]; mLb = M.link_pts["L1b"][0]
TG = cKDTree(G2[used]); dev = []
for i in np.nonzero(np.asarray(M.kin_ok, bool))[0]:
    k = abs(float(M.dK[i]))
    if k > lim + 1e-9: continue
    R9, t9 = M.T(9, i); Rb, tb = M.T(mLb, i); R2, t2 = M.T(mL2, i); Rr = Rb.T @ R2
    w = 0.5 * np.array([Rr[2, 1] - Rr[1, 2], Rr[0, 2] - Rr[2, 0], Rr[1, 0] - Rr[0, 1]]); th = math.atan2(float(w @ u2), (float(np.trace(Rr)) - 1) / 2)
    pin1b = Rb.T @ (R9 @ F0w + t9 - tb); g = DS._rot(u2, -(th - q_on)) @ pin1b
    dev.append((float(TG.query(g)[0]), math.degrees(k), int(i)))
dev = np.array(dev)
devrep = dict(n=len(dev), max_mm=round(float(dev[:, 0].max()), 4), n_over_c=int((dev[:, 0] > DS.C_GROOVE).sum()), n_over_0p05=int((dev[:, 0] > 0.05).sum()),
              worst_K_deg=round(float(dev[int(np.argmax(dev[:, 0])), 1]), 2), p95=round(float(np.percentile(dev[:, 0], 95)), 4))
big = [r_ for r_ in rows if max(r_[2], r_[3] if r_[1] > 1e-9 else 0) > 0.25]
print(json.dumps(dict(blend_ik=VH.BLEND, gap=r.get("plain"), pin_on_groove=devrep, params={k: P[k] for k in ("a_s", "psi", "glev", "blend")}, claim_corner=info.get("slop", {}).get("crank_free"),
                      rc_min=dict(rc=round(float(rc[jmin]), 3), x_deg=round(math.degrees(x[jmin]), 2), K_deg=round(math.degrees(Kb[jmin]), 2)),
                      dense_worst=worst, n_scan=len(rows), n_over_025=len(big), over_025=big[:40],
                      rc_profile_low=[p for p in prof if p[2] < 3.0]), default=float))
json.dump(dict(rows=rows, prof=prof), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "groove_scan_%s.json" % "_".join(sys.argv[1:]).replace("=", "")), "w"))
