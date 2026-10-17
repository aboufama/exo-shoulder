"""fold-ceiling step 2b: is the fold loss a CLEARANCE TRADE? Hub-2 parking on the exact skin.

Every design of the family carries hub 2 (the O20 disc, radius 10, on the J2 ray through GH) at ONE level F2 on its link:
a pose is taken only if F2 >= req2(pose) (the K3 march of every disc sample, +2 mm clearance), and hub 2 is in band on a
clip frame only if F2 - req2(frame) <= 12. This script measures req2 on Bench(110,360) EXACT for
  * the leader's own IK (clip frames and taken workspace poses): the level its hub 2 lives at;
  * every fold-lost workspace pose, with the J2 ray a hypothetical wider-window sibling would need (same seats u1 / u3,
    same a2, same branch): stretched side a1e = th - a2 + 5 (K opened just enough: the J2 ray nearest the leader's), and
    a1e up to +15 deg further (the minimum req over those is kept: optimistic for the lever); folded side a1e = a2 - th + 5
    (a K that also opens on the folded side) and the same +15 scan.
Hub K and the links are NOT charged here (a lower bound on the parking cost = an upper bound on what the lever buys).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/fold_ceiling/parking.py [bench|held]
"""
import importlib.util, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_bench as CB; import concept_kit as K  # noqa: E402

ID = "roller-longdyad-knuckle-3r"; WHICH = sys.argv[1] if len(sys.argv) > 1 else "bench"
L = json.load(open(os.path.join(HERE, f"lost_poses_{ID}.json")))
sp = importlib.util.spec_from_file_location("lead_model", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
MOD = importlib.util.module_from_spec(sp); sp.loader.exec_module(MOD)
P = MOD._clamp(dict(MOD.PARAMS, **L["params"]))
B1 = CB.Bench(n_clip=60, n_ws=160); r1, M1 = MOD._report(B1, P); D = M1.D
F2_fit = float(M1.f[1]); FK_fit = float(M1.fK)
if WHICH == "held":
    pv = importlib.util.spec_from_file_location("pkpol", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
    PV = importlib.util.module_from_spec(pv); pv.loader.exec_module(PV); B = PV.held_bench(); rows = L["held"]
else:
    os.environ["CB_EXACT"] = "1"; B = CB.Bench(n_clip=110, n_ws=360); rows = L["bench"]
F = K.frames(B); Z = CB._poses_all(); Q = Z["HG"][B.idx].astype(float)
q, ok, X1, X2, X3, s = D.ik(Q); X1b = np.asarray(D._X1b[0], float)
u1, u2, u3 = D.u; a1, a2 = D.a1, D.a2
w = Q @ u3                                                            # J3 in the scapula frame
u2_lead = np.einsum("nij,j->ni", X1b, u2)                             # J2 ray of the leader's own IK (scapula frame)
uK_lead = np.einsum("nij,j->ni", np.asarray(X1[0], float), D.uK)
xy = K.disc_xy(10.0, 2.0)


def req_disc(I, Ks):
    """hub disc requirement (max over the disc's samples, +2 mm clearance) along world axes Ks (n, 3) in poses I (n,)"""
    if not len(I): return np.zeros(0)
    k = K.unit(Ks); A, Bv = K.plane_frame(k); m = len(xy)
    O = (xy[None, :, :1] * A[:, None, :] + xy[None, :, 1:] * Bv[:, None, :]).reshape(-1, 3)
    Dd = np.repeat(k, m, 0); II = np.repeat(np.asarray(I), m); R = np.empty(len(II))
    for c in np.unique(np.asarray(I)) if True else []:                # pose by pose: the exact-skin cache holds 24 poses
        sel = II == c; R[sel] = K.requirement(B, II[sel], Dd[sel], O=O[sel])
    R = R.reshape(len(I), m)
    return np.where(np.isfinite(R), R, 400.0).max(1)


def world(i, v): return F.RS[i] @ v


out = dict(id=ID, bench=WHICH, F2_fit=round(F2_fit, 2), FK_fit=round(FK_fit, 2), a1=a1, a2=a2, a1max=L["a1max"], poses=[])
kind = np.array(B.kind); taken = np.array([r["taken"] for r in rows]); wall = np.array([r["wall"] for r in rows]); th = np.array([r["th"] for r in rows])
# 1) the leader's own hub-2 / hub-K requirement on every taken pose (clip and ws)
I_t = np.nonzero(taken & ok)[0]
r2_t = req_disc(I_t, np.stack([world(i, u2_lead[i]) for i in I_t]))
rK_t = req_disc(I_t, np.stack([world(i, uK_lead[i]) for i in I_t]))
# 2) fold-lost workspace poses: the hypothetical J2 ray, a1e scanned over the minimal opening .. +15
I_l = np.nonzero((kind == "ws") & ~taken & np.isin(wall, ["stretched_stopB", "stretched_law", "folded", "stretched_drive"]))[0]
r2_l = np.full(len(I_l), np.inf); a_l = np.full(len(I_l), np.nan); dirs = {}
for j, i in enumerate(I_l):
    a_min = th[i] - a2 + 5.0 if wall[i] != "folded" else a2 - th[i] + 5.0
    cands = []
    for da in (0.0, 3.0, 6.0, 10.0, 15.0):
        ae = a_min + da
        p, okc, mg = K.closure(u1[None], w[i][None], ae, a2, D.branch, margin_deg=5.0 - 1e-6)
        if okc[0]: cands.append((ae, world(i, p[0])))
    if cands:
        rr = req_disc(np.full(len(cands), i), np.stack([c[1] for c in cands]))
        k = int(np.argmin(rr)); r2_l[j] = rr[k]; a_l[j] = cands[k][0]
for j, i in enumerate(I_l):
    out["poses"].append(dict(i=int(i), plane=rows[i]["plane"], elev=rows[i]["elev"], axial=rows[i]["axial"], th=rows[i]["th"], wall=rows[i]["wall"],
                             a1e_need=round(float(a_l[j]), 2) if np.isfinite(a_l[j]) else None, req2=round(float(r2_l[j]), 2)))
ck = kind[I_t] == "clip"
out["leader"] = dict(req2_clip=np.percentile(r2_t[ck], [0, 10, 50, 90, 100]).round(2).tolist(),
                     req2_ws=np.percentile(r2_t[~ck], [0, 10, 50, 90, 100]).round(2).tolist(),
                     reqK_clip=np.percentile(rK_t[ck], [0, 10, 50, 90, 100]).round(2).tolist(),
                     reqK_ws=np.percentile(rK_t[~ck], [0, 10, 50, 90, 100]).round(2).tolist(),
                     n_taken=int(len(I_t)), n_clip=int(ck.sum()))
lvl = float(np.max(r2_t)); out["leader"]["req2_max_taken"] = round(lvl, 2)
fin = np.isfinite(r2_l)
st = np.isin(wall[I_l], ["stretched_stopB", "stretched_law", "stretched_drive"])
for nm, m in (("stretched", st), ("folded", ~st)):
    out[nm] = dict(n=int(m.sum()), closable=int((m & fin).sum()),
                   req2_pct=np.percentile(r2_l[m & fin], [0, 10, 25, 50, 75, 90, 100]).round(1).tolist() if (m & fin).any() else None,
                   le_F2fit=int((m & (r2_l <= F2_fit)).sum()),
                   le_F2fit_plus={d: int((m & (r2_l <= F2_fit + d)).sum()) for d in (2, 4, 6, 8, 12, 20, 40)})
# the in-band price of raising F2: share of the leader's clip frames whose hub 2 leaves 2-14 (F2 - req2 > 12)
rc = r2_t[ck]
out["price"] = {f"F2+{d}": dict(F2=round(F2_fit + d, 1), hub2_clip_out_of_band=round(float(np.mean(F2_fit + d - rc > 12)), 3),
                                  stretched_parkable=int((st & (r2_l <= F2_fit + d)).sum()), folded_parkable=int((~st & (r2_l <= F2_fit + d)).sum()))
                for d in (0, 2, 4, 6, 8, 10, 15, 20)}
json.dump(out, open(os.path.join(HERE, f"parking_{WHICH}.json"), "w"), indent=1, default=float)
print(json.dumps({k: out[k] for k in ("F2_fit", "FK_fit", "leader", "stretched", "folded", "price")}, default=float))
