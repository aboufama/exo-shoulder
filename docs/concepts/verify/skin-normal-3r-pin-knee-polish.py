"""Independent verification of the skin-normal-3r-pin-knee FINAL POLISH claim (2026-10-16): re-measures a configuration
with the round-3 adversarial verifier (docs/concepts/verify/skin-normal-3r-pin-knee.py, imported UNCHANGED: its
extra_checks knock poses out, the model's audit gives near-touch / overhead) under three frozen-shape protocols:

  fit60  : the round-3 verifier's own protocol - fit on Bench(60,160) FAST, worn on Bench(110,360) (CB_EXACT=1 -> exact)
  fitbig : the polish protocol - fit on Bench(110,360) FAST, worn on Bench(110,360) (CB_EXACT=1 -> exact)
  held   : fit on Bench(110,360) FAST, worn EXACT on a bench DISJOINT from both Bench(110,360) and Bench(60,160)
           (every remaining fit-clip frame + every remaining workspace pose; the held-out clips Wave / Walking stay out)

plus the verifier's own red-team numbers: the J1-J3 fold margin and the knee angle over the poses taken (distance to the
fold and to the knee's singular postures), the arm-at-side near-touch (elevation <= 15 deg), the J1 seat direction
(anterior component, rule (4): back of the shoulder + acromion top), the hub radii actually used, and the fold margin in
force (CB_FOLD_MARGIN; tools/concept_kit.py FOLD_MARGIN).

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 [CB_FOLD_MARGIN=10] python3 docs/concepts/verify/skin-normal-3r-pin-knee-polish.py \
        <fit60|fitbig|held> <out.json> '<json params>'
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_spec = importlib.util.spec_from_file_location("pin_knee_verifier", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
V = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(V)
MK, S, KEYS = V.MK, V.S, V.KEYS


def fast_bench(nc, nw):
    old = os.environ.pop("CB_EXACT", None)
    try: B = CB.Bench(n_clip=nc, n_ws=nw)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    return B


def held_bench():
    """every fit-clip frame and workspace pose NOT in Bench(110,360) or Bench(60,160); exact path"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; P = Z["POSE"]
    used = set(CB._select(110, 360)[0].tolist()) | set(CB._select(60, 160)[0].tolist())
    fit_ids = [names.index(x) for x in CB.FIT]; ws_id = names.index("Workspace (envelope)")
    cl = np.array([i for i in np.nonzero(np.isin(cid, fit_ids))[0] if i not in used], int)
    ws = np.array([i for i in np.nonzero(cid == ws_id)[0] if i not in used], int)
    old = os.environ.get("CB_EXACT"); os.environ["CB_EXACT"] = "1"
    try: B = CB.Bench(20, 20)
    finally:
        if old is None: os.environ.pop("CB_EXACT")
        else: os.environ["CB_EXACT"] = old
    idx = np.r_[cl, ws]
    B.idx = idx; B.kind = ["clip"] * len(cl) + ["ws"] * len(ws); B.clip = [names[c] for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in P[idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.grid = None; B._V = None; B.mode = "exact"; B.key = "held-v"
    assert not (set(idx.tolist()) & used)
    held_clip_ids = {names.index(x) for x in ("Wave", "Walking arm swing")}
    assert not any(int(c) in held_clip_ids for c in cid[idx])
    return B


def frozen_on(fitB, wearB, P):
    """the round-3 verifier's frozen_model with the fit bench as an argument (same attribute hand-over, no refit)"""
    M1 = MK.Model(fitB, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in KEYS}; fit["mode"] = fitB.mode
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(MK.Model):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_h12"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    M = Frozen(wearB, P2)
    return M, fit, M1


def redteam(M, B):
    D = M.D; taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    out = {}
    # J1-J3 fold margin over the taken poses (same law as the model's ik; independent re-computation)
    u1, u3 = D.u[0], D.u[2]; a1, a2 = math.degrees(D.A[0]), math.degrees(D.A[1])
    w = M.Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
    marg = np.minimum(th - abs(a1 - a2), min(a1 + a2, 360 - a1 - a2) - th)
    out["fold_margin_rule_deg"] = KIT.FOLD_MARGIN
    out["fold_margin_min_taken_deg"] = round(float(marg[taken].min()), 2) if taken else None
    out["fold_window_deg"] = [round(abs(a1 - a2), 2), round(min(a1 + a2, 360 - a1 - a2), 2)]
    out["a_deg"] = [round(a1, 2), round(a2, 2)]
    ang = M.K["ang"]; out["knee_ang_taken"] = [round(float(ang[taken].min()), 1), round(float(ang[taken].max()), 1)] if taken else None
    out["knee_sing_dist_min_deg"] = round(float(np.minimum(ang[taken], 180 - ang[taken]).min()), 1) if taken else None
    # arm at the side: elevation <= 15
    low = [i for i in taken if B.poses[i]["elev"] <= 15]
    mm = sorted((min(float(np.min(B.res[i])), M.cmin.get(i, 1e9)), i) for i in low)
    lab = lambda i: dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=round(B.poses[i]["elev"], 1), axial=B.poses[i]["axial"])
    elev = np.array([p["elev"] for p in B.poses])
    out["arm_side"] = dict(poses=int((elev <= 15).sum()), taken=len(low), lt1=sum(1 for d, _ in mm if d < 1), lt2=sum(1 for d, _ in mm if d < 2),
                           low=[dict(mm=round(d, 2), **lab(i)) for d, i in mm[:4]])
    # J1 seat (scapula-frame bvec: x anterior when az 180; rule (4) back + acromion top)
    b = KIT.bvec(D.p["az1"], D.p["el1"]); out["j1_seat"] = dict(anterior=round(float(b[0]), 4), up=round(float(b[1]), 4), lateral=round(float(b[2]), 4))
    out["hubs"] = list(M.hr); out["stk"] = M.p["stk"]; out["tp"] = round(float(M.p["tp"]), 3); out["ang_min"] = M.p["ang_min"]
    out["tr"] = round(float(M.tr), 2); out["f"] = [round(float(x), 2) for x in M.f]
    out["why"] = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "skin", "parts", "contact")}
    return out


def main():
    proto, outp, P = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
    t0 = time.time()
    fitB = fast_bench(60, 160) if proto == "fit60" else fast_bench(110, 360)
    wearB = held_bench() if proto == "held" else CB.Bench(n_clip=110, n_ws=360)
    M, fit, M1 = frozen_on(fitB, wearB, P)
    r = M.run(); model = {k: r[k] for k in KEYS}
    aud0 = MK.audit(M, wearB)
    ex, bad = V.extra_checks(M, wearB)
    rt0 = redteam(M, wearB)
    res0 = list(wearB.res)
    for i in bad: wearB.res[i] = None
    rc = wearB.report(); corrected = {k: rc[k] for k in KEYS}
    aud = MK.audit(M, wearB); rt = redteam(M, wearB)
    wearB.res = res0
    out = dict(protocol=proto, params=P, fit_mode=fitB.mode, wear_mode=wearB.mode, n_wear=len(wearB.idx), exact=os.environ.get("CB_EXACT") == "1",
               fold_margin=KIT.FOLD_MARGIN, o20_only=KIT.O20_ONLY, fit=fit, model=model, model_audit=aud0, extra=ex, bad_removed=len(bad),
               corrected=corrected, corrected_audit=aud, redteam=rt, redteam_model=rt0, secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(protocol=proto, wear=wearB.mode, n=len(wearB.idx), margin=KIT.FOLD_MARGIN, fit=fit, corrected=corrected,
                          near1=aud["gap_near1"], near1_poses=aud["near1_poses"], min_mm=aud["near_touch_min_mm"], overhead=aud["overhead140"],
                          bad=len(bad), redteam=rt, secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main()
