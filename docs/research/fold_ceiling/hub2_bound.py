"""fold-ceiling step 2c: the HUB-2 PARKING BOUND of the family, over seats and arcs.

Family: J1 scapula-fixed at u1 (the user's ruling: back of the shoulder or acromion top), J3 humerus-fixed at u3, J2 on a
GH ray, a knuckle that opens a1e on the stretched side from a1 (stop A) up to a1max (every leader's law, here the minimal
opening a1e = th - a2 + 5), branch sigma. Kinematics exact (th, closure); proximity = ONLY hub 2's O20 disc, read from the
per-pose requirement map (req_map.py, Bench(60,160) fast): a pose is taken iff it closes with the 5-deg margin and
req2(pose) <= F2 (hub 2 is one rigid disc at ONE level F2), a clip frame is followed iff the same, and hub 2 is in band on a
followed clip frame iff F2 - req2 <= 12 (its samples sit 2-14 mm off the skin). For every design the best F2 is chosen.
Everything else (hubs 1 / K / 3, links, drive, knee, part collisions) is FREE here, so the reach this script finds at a
given hub-2 in-band is an UPPER bound for the family (up to the map's resolution - checked against the leader).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/fold_ceiling/hub2_bound.py [n_designs]
"""
import json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); import concept_bench as CB; import concept_kit as K  # noqa: E402
from scipy.spatial import cKDTree

M = np.load(os.path.join(REPO, ".cache", "fold_ceiling", "req_map_60_160.npz"))
G, reqD, kind60 = M["G"], M["reqD"], M["kind"]; tree = cKDTree(G)
Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; ws_id = names.index("Workspace (envelope)")
Q60 = Z["HG"][M["idx"]].astype(float); clip60 = kind60 == "clip"; ws60 = ~clip60
b_idx = CB._select(110, 360)[0]; Q360 = Z["HG"][b_idx[cid[b_idx] == ws_id]].astype(float)
used = set(CB._select(110, 360)[0].tolist()) | set(CB._select(60, 160)[0].tolist())
QH = Z["HG"][np.array([i for i in np.nonzero(cid == ws_id)[0] if i not in used], int)].astype(float)
POSE60 = Z["POSE"][M["idx"]]; ov60 = ws60 & (POSE60[:, 1] >= 140)


def closure_v(b, w, a1e, a2, sigma):
    """two-circle closure with a per-pose a1e (deg): b, w (P, 3) unit"""
    c = np.clip((b * w).sum(-1), -1, 1); n = K.unit(np.cross(b, w)); A1, A2 = np.radians(a1e), math.radians(a2)
    den = 1 - c ** 2 + 1e-12; A = (np.cos(A1) - c * math.cos(A2)) / den; Bq = (math.cos(A2) - c * np.cos(A1)) / den
    p0 = A[:, None] * b + Bq[:, None] * w; h2 = 1 - (p0 * p0).sum(-1)
    return K.unit(p0 + sigma * np.sqrt(np.clip(h2, 0, None))[:, None] * n), h2 > 0


def law(th, a1, a2, a1max, m=5.0):
    """one-sided knuckle: a1e = a1 inside [|a1 - a2| + m, a1 + a2 - m], opened just enough beyond, up to a1max"""
    lo = abs(a1 - a2) + m; hi0 = min(a1 + a2, 360 - a1 - a2) - m; hi = min(a1max + a2, 360 - a1max - a2) - m
    a1e = np.where(th <= hi0, a1, th - a2 + m); ok = (th >= lo) & (th <= hi)
    return a1e, ok


def design_eval(u1, u3, a1, a2, a1max, sigma, F2_grid=None, detail=False):
    w = Q60 @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
    a1e, ok = law(th, a1, a2, a1max); u2, okc = closure_v(np.broadcast_to(u1, w.shape), w, a1e, a2, sigma); ok &= okc
    r2 = reqD[np.arange(len(w)), tree.query(u2)[1]]
    th360 = np.degrees(np.arccos(np.clip((Q360 @ u3) @ u1, -1, 1))); kin360 = law(th360, a1, a2, a1max)[1].mean()
    thH = np.degrees(np.arccos(np.clip((QH @ u3) @ u1, -1, 1))); kinH = law(thH, a1, a2, a1max)[1].mean()
    cand = np.unique(np.round(r2[ok & clip60], 1)) if F2_grid is None else F2_grid
    best = []
    for F2 in cand:
        fol = ok & clip60 & (r2 <= F2); follow = fol.sum() / clip60.sum()
        ib2 = float(np.mean(F2 - r2[fol] <= 12.0)) if fol.any() else 0.0
        R = (ok & ws60 & (r2 <= F2)).sum() / ws60.sum(); ovh = (ok & ov60 & (r2 <= F2)).sum()
        best.append((F2, follow, ib2, R, ovh))
    out = dict(kin160=float((ok & ws60).mean() / ws60.mean()), kin360=float(kin360), kinH=float(kinH), frontier=best)
    if detail: out.update(r2=r2, ok=ok, th=th)
    return out


def slerp(a, b, f):
    c = np.clip((a * b).sum(-1), -1, 1); om = np.arccos(c)[:, None] + 1e-9
    return K.unit((np.sin((1 - f) * om) * a + np.sin(f * om) * b) / np.sin(om))


def multi_eval(u1, u3, a1, a2, a1max, sigma, taus=(0.95, 0.9, 0.8, 0.7, 0.6), fmin=0.95):
    """ALL O20 hub discs (1, 2, 3) and link samples (link 1 at 1/2, link 2 at 1/3, 2/3 of its arc) as rigid parts at one
    level each: for a per-part in-band floor tau, part k's level can be at most F_k = 12 + the (1 - tau) quantile of its
    requirement over the followed clip frames (iterated to a fixed point); a pose is taken iff it closes and every part
    clears (req_k <= F_k). Returns {tau: (R160, follow, kin360, ovh160)}"""
    w = Q60 @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
    a1e, ok = law(th, a1, a2, a1max); U1 = np.broadcast_to(u1, w.shape); u2, okc = closure_v(U1, w, a1e, a2, sigma); ok &= okc
    dirs = [U1, u2, w, slerp(U1, u2, 0.5), slerp(u2, w, 1 / 3), slerp(u2, w, 2 / 3)]
    R_ = np.stack([reqD[np.arange(len(w)), tree.query(d)[1]] for d in dirs])            # (parts, P)
    res = {}
    for tau in taus:
        S = ok & clip60
        for _ in range(6):
            if not S.any(): break
            Fk = 12.0 + np.quantile(R_[:, S], 1 - tau, axis=1)
            S2 = ok & clip60 & (R_ <= Fk[:, None]).all(0)
            if (S2 == S).all(): break
            S = S2
        clear = (R_ <= Fk[:, None]).all(0) if S.any() else np.zeros(len(w), bool)
        fol = (ok & clip60 & clear).sum() / clip60.sum(); Rr = (ok & ws60 & clear).sum() / ws60.sum()
        res[tau] = (float(Rr) if fol >= fmin else 0.0, float(fol), int((ok & ov60 & clear).sum()))
    return res


def frontier_point(fr, tau, fmin=0.95):
    """max reach over the design's F2 choices with hub-2 in-band >= tau and follow >= fmin"""
    good = [(R, F2, ib, ovh) for F2, fol, ib, R, ovh in fr if ib >= tau and fol >= fmin]
    return max(good) if good else (0.0, None, None, None)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    L = json.load(open(os.path.join(HERE, "lost_poses_roller-longdyad-knuckle-3r.json")))
    u1L, u3L = np.array(L["u1"]), np.array(L["u3"])
    lead = design_eval(u1L, u3L, L["a1"], L["a2"], L["a1max"], -1.0)
    out = dict(leader=dict(kin160=lead["kin160"], kin360=lead["kin360"], kinH=lead["kinH"],
                           at={str(t): frontier_point(lead["frontier"], t) for t in (0.95, 0.9, 0.8, 0.6, 0.0)}))
    for sg in (1.0,):
        l2 = design_eval(u1L, u3L, L["a1"], L["a2"], L["a1max"], sg); out[f"leader_branch{int(sg)}"] = {str(t): frontier_point(l2["frontier"], t) for t in (0.95, 0.9, 0.8)}
    print("leader", json.dumps(out, default=float), flush=True)
    rng = np.random.default_rng(7); t0 = time.time(); rows = []
    for k in range(n):
        while True:
            az1, el1 = rng.uniform(-90, 135), rng.uniform(-20, 85)
            if az1 <= 90 or el1 >= 50: break
        d3, aa3 = rng.uniform(25, 125), rng.uniform(-100, 100)
        a1 = rng.uniform(20, 70); a2 = rng.uniform(30, 115); a1max = a1 + rng.uniform(0, 35); sg = rng.choice([-1.0, 1.0])
        u1 = K.bvec(az1, el1); u3 = K.wdir(d3, aa3)
        e = design_eval(u1, u3, a1, a2, a1max, sg, F2_grid=[1e9])
        if e["kin160"] < 0.6: continue
        mm = multi_eval(u1, u3, a1, a2, a1max, sg)
        rows.append(dict(az1=az1, el1=el1, d3=d3, a3=aa3, a1=a1, a2=a2, a1max=a1max, sg=sg, kin160=e["kin160"], kin360=e["kin360"], kinH=e["kinH"],
                         strict=bool((el1 >= 50 and az1 >= 60) or (-60 <= az1 <= 90 and 0 <= el1 < 50)),
                         **{f"R{t}": mm[t] for t in (0.95, 0.9, 0.8, 0.7, 0.6)}))
        if k % 2000 == 0: print(k, len(rows), round(time.time() - t0), flush=True)
    out["leader_multi"] = {str(t): v for t, v in multi_eval(u1L, u3L, L["a1"], L["a2"], L["a1max"], -1.0).items()}
    print("leader multi", out["leader_multi"], flush=True)
    for reg in ("all", "strict"):
        for t in (0.95, 0.9, 0.8, 0.7, 0.6):
            rr = [r for r in rows if reg == "all" or r["strict"]]
            top = sorted(rr, key=lambda r: -r[f"R{t}"][0])[:5]
            out[f"best_{reg}_tau{t}"] = top
            print(reg, "tau", t, [(round(r[f"R{t}"][0], 3), round(r["kin360"], 3), round(r["az1"]), round(r["el1"]), round(r["d3"]), round(r["a3"]), round(r["a1"]), round(r["a2"]), round(r["a1max"]), r["sg"]) for r in top[:3]], flush=True)
    out["n_designs"] = n; out["n_kept"] = len(rows)
    json.dump(out, open(os.path.join(HERE, "hub2_bound.json"), "w"), indent=1, default=float)
