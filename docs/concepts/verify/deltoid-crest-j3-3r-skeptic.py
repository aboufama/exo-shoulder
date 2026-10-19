"""Adversarial verifier for deltoid-crest-j3-3r (2026-10-17). Re-measures the claimed best configuration through the
zc-frontier-3r build and checks (kit K1-K7 + dense K2, 1 mm radial K6, the spine-parked verifier's top_check: top faces,
crowns, near-touch, closure residual, hub-axis accessibility F <= 140) WITHOUT the model file's crest-box snap, and adds:

  * the fold margin read in ONE metric (th = angle(J1, J3), concept_kit lines 25-30) recomputed from the joint axes over
    every taken pose, independently of K.closure's mask;
  * closure residual and J2 axis vs both arcs over the taken poses;
  * a workspace continuity flood (2-deg slerp edges between each taken ws pose and its 8 nearest taken ws poses by
    frame angle, closure at the 5-deg margin at every step, no joint axis stepping > 10 deg; seeds = taken poses at the
    lowest elevation level): static vs connected reach (a plain 3R needs no flood by the rule; reported as a stricter
    reading). Grid-neighbour edges alone under-connect on the sparse bench samples (kept as ws_connected_grid_edges);
  * a per-pose dump (tools/alignment_paired.py format: min metal per pose, taken, contact, clip band counts) whose own
    gap is recomputed and compared with the report (lead's T5 rule, bench and held out);
  * the Bench(60,160) EXACT refit (CB_EXACT=1) against the claimed 36.63 fast (fast-cache artefact check);
  * held out: the frozen shape worn on poses disjoint from Bench(110,360) (tools/osn_polish.py held_bench, exact).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/deltoid-crest-j3-3r-skeptic.py frozen|fit60|held OUT.json ['<json>']
"""
import importlib.util, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m


ZC = _load("dcv_zc", os.path.join(REPO, "docs", "concepts", "models", "zc-frontier-3r.py"))
K = ZC.K; CB = K.CB
import alignment_paired as AP                                                  # noqa: E402

ROW = os.path.join(REPO, "docs", "concepts", "rows", "deltoid-crest-j3-3r.json")
KEYS = ("gap", "near", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "hub_F", "hub_F_ok",
        "min_metal_all_faces", "top_contact_poses", "inband_member", "overhead", "flips", "closure", "collide")


def held_bench(nc=110, nw=360):
    """= tools/osn_polish.py held_bench: poses DISJOINT from Bench(110,360) (held-out clips still excluded), exact path"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; P = Z["POSE"]
    big, _, _, _ = CB._select(110, 360); bigs = set(big.tolist())
    fit_ids = [names.index(x) for x in CB.FIT]; ws_id = names.index("Workspace (envelope)")
    cl = np.array([i for i in np.nonzero(np.isin(cid, fit_ids))[0] if i not in bigs]); ws = np.array([i for i in np.nonzero(cid == ws_id)[0] if i not in bigs])
    cl = cl[np.linspace(0, len(cl) - 1, min(nc, len(cl))).round().astype(int)]; ws = ws[np.linspace(0, len(ws) - 1, min(nw, len(ws))).round().astype(int)]
    B = CB.Bench(20, 20); idx = np.r_[cl, ws]
    B.idx = idx; B.kind = ["clip"] * len(cl) + ["ws"] * len(ws); B.clip = [names[c] for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in P[idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.grid = None; B._V = None; B.mode = "exact"; B.key = "held"
    return B


def taken(B):
    return np.array([B.res[j] is not None and len(B.res[j]) and float(np.min(B.res[j])) >= 0 for j in range(len(B.res))], bool)


def extras(B, p):
    """independent fold margin / closure / J2 arcs over the taken poses + the continuity flood"""
    F = B._kitF; L = B._kit_last; ch = L["chain"]; tk = taken(B)
    p1 = K.unit(ch.joints["J1"]); p2 = K.unit(ch.joints["J2"]); p3 = K.unit(ch.joints["J3"])
    ang = lambda a, b: np.degrees(np.arccos(np.clip((a * b).sum(-1), -1, 1)))
    th = ang(p1, p3); a1, a2 = p["a1"], p["a2"]
    marg = np.minimum.reduce([th - abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th])
    e1 = np.abs(ang(p1, p2) - a1); e2 = np.abs(ang(p2, p3) - a2)
    # expected seats: J1 fixed in the scapula, J3 fixed in the humerus (band frame)
    s1 = ang(p1, K.unit(F.S(K.bvec(p["az"], p["el"])))); s3 = ang(p3, K.unit(F.HG(K.wdir(p["wd"], p["wa"]))))
    out = dict(n_taken=int(tk.sum()), th_margin_min_taken=round(float(marg[tk].min()), 3) if tk.any() else None,
               th_taken_range=[round(float(th[tk].min()), 2), round(float(th[tk].max()), 2)] if tk.any() else None,
               arc_err_max_deg=round(float(max(e1[tk].max(), e2[tk].max())), 6) if tk.any() else None,
               seat_err_max_deg=round(float(max(s1.max(), s3.max())), 6))
    # continuity flood over the ws grid
    n = len(B.kind); ws = [i for i in range(n) if B.kind[i] == "ws" and tk[i]]
    key = {(B.poses[i]["plane"], B.poses[i]["elev"], B.poses[i]["axial"]): i for i in ws}
    vals = [sorted({B.poses[i][k] for i in range(n) if B.kind[i] == "ws"}) for k in ("plane", "elev", "axial")]

    def nbrs(i):
        x = (B.poses[i]["plane"], B.poses[i]["elev"], B.poses[i]["axial"])
        for d in range(3):
            j = vals[d].index(x[d])
            for jj in (j - 1, j + 1):
                if 0 <= jj < len(vals[d]):
                    y = list(x); y[d] = vals[d][jj]; t = key.get(tuple(y))
                    if t is not None: yield t

    def edge(a, b):
        sub = K._slerp_frames(F, a, b, step_deg=2.0); m = len(sub.RS)
        c = ZC.build(B, sub, p)
        jmp = 0.0
        for ax in c.joints.values():
            ax = K.unit(np.asarray(ax, float).reshape(m, 3)); jmp = max(jmp, float(ang(ax[1:], ax[:-1]).max(initial=0)))
        return bool(np.all(c.ok) and jmp <= 10.0)

    from scipy.spatial.transform import Rotation as Rot
    Dm = np.array([[max(np.degrees(Rot.from_matrix(X[a].T @ X[b]).magnitude()) for X in (F.RS, F.RHG)) for b in ws] for a in ws]) if ws else None
    pos = {a: k for k, a in enumerate(ws)}

    def knn(i, k=8):                    # the bench samples the ws grid sparsely: most grid neighbours are missing,
        for t in np.argsort(Dm[pos[i]])[1:k + 1]: yield ws[t]   # so the grid flood under-connects; kNN-8 edges do not

    def flood(nb):
        conn = np.zeros(n, bool)
        if ws:
            e0 = min(B.poses[i]["elev"] for i in ws); front = [i for i in ws if B.poses[i]["elev"] == e0]
            for i in front: conn[i] = True
            while front:
                nxt = []
                for a in front:
                    for b in nb(a):
                        if not conn[b] and edge(a, b): conn[b] = True; nxt.append(b)
                front = nxt
        return conn
    nws = sum(1 for k in B.kind if k == "ws"); cg = flood(nbrs); conn = flood(knn)
    out.update(flood=dict(ws_taken_static=len(ws), ws_connected=int(conn.sum()), islands=len(ws) - int(conn.sum()),
                          ws_connected_grid_edges=int(cg.sum()), edges="kNN-8 by frame angle (grid-neighbour count kept for reference)",
                          reach_static=round(len(ws) / nws, 4), reach_connected=round(float(conn.sum()) / nws, 4),
                          island_poses=[[B.poses[i][k] for k in ("plane", "elev", "axial")] for i in ws if not conn[i]][:40]))
    return out


class _M:  # AP._dump_bench reads M.cmin only
    cmin = {}


def wear(B, p, prof, tag):
    t = time.time(); pb, rb = ZC.evaluate(B, dict(p), fixed_prof=prof)
    res = dict(mode=B.mode, report={k: rb.get(k) for k in KEYS}, verifier=rb.get("v"), v_near1=rb.get("v_near1"),
               secs_eval=round(time.time() - t, 1))
    poses = AP._dump_bench(_M, B); res["dump_recomputed"] = AP.gap_parts(poses); res["poses"] = poses
    try: res["attribution"] = ZC.attribute(B, pb, rb)
    except Exception as e: res["attribution"] = repr(e)                         # noqa: BLE001
    t = time.time(); res["extras"] = extras(B, pb); res["secs_extras"] = round(time.time() - t, 1)
    res["score"] = round(100 * (1 - float(rb["gap"]) / 275), 2)
    print(tag, B.mode, json.dumps({k: rb.get(k) for k in KEYS}, default=float), flush=True)
    print("extras", json.dumps({k: v for k, v in res["extras"].items() if k != "flood"}, default=float),
          json.dumps({k: v for k, v in res["extras"]["flood"].items() if k != "island_poses"}), flush=True)
    print("dump", json.dumps(res["dump_recomputed"], default=float), flush=True)
    return res


def main():
    task, out = sys.argv[1], sys.argv[2]
    row = json.load(open(ROW)); par = dict(row["best_params"])
    if len(sys.argv) > 3: par.update(json.loads(sys.argv[3]))
    p0 = ZC.snap(par)                                     # the frontier's snap: rules never loosened, NO crest-box clamp
    res = dict(task=task, params=p0, exact=os.environ.get("CB_EXACT") == "1", fold_margin=K.FOLD_MARGIN, t0=K.now(),
               seat_ok=ZC.seat_ok(p0["az"], p0["el"]))
    t0 = time.time()
    if task == "fit60":
        B = K.bench(60, 160); res["fit60"] = wear(B, p0, None, "fit60")
    else:
        ex = os.environ.pop("CB_EXACT", None)
        try: Bf = K.bench(60, 160)
        finally:
            if ex is not None: os.environ["CB_EXACT"] = ex
        pf, rf = ZC.evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
        res["fit"] = {k: rf.get(k) for k in KEYS}; res["fit"]["mode"] = Bf.mode
        print("fit", json.dumps(res["fit"], default=float), flush=True)
        Bb = K.bench(110, 360) if task == "frozen" else held_bench(110, 360)
        res["wear"] = wear(Bb, pf, prof, task)
    res["secs"] = round(time.time() - t0, 1)
    json.dump(res, open(out, "w"), indent=0, default=float)


if __name__ == "__main__":
    main()
