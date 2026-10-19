"""Alignment re-wear adapter for the fold-sph3r-family kit models (raglan-routed-3r and any model whose frozen() is
docs/concepts/models/fold-sph3r.py frozen() with the model's own build / evaluate), which tools/alignment_audit.py
remeasure cannot wrap (no pin-knee-style audit(M, B)). Read-only on every claim: the model file runs UNCHANGED through
its own frozen path (fit Bench(60,160) fast, every underside level frozen, worn on Bench(110,360) - exact with
CB_EXACT=1 - or on the held-out bench = tools/osn_polish.py held_bench(): poses disjoint from Bench(110,360), held-out
clips excluded). Only one thing is wrapped, pass-through: concept_kit.bench, to capture the worn bench (and, for the held
wear, to swap the big bench for the held bench; the fit bench is untouched).

After the wear the bench is read by the audit's own instruments: alignment_audit.deep_audit (near-touch at 1 / 2 / 3 mm
incl. the model's crown / wall samples, clip metal histogram, band read 3-14 mm) and alignment_wear_probe.analyse
(unscored workspace in-band, overhead, clearance floors), plus: the per-pose fold margin in th (the model's own axes() ->
concept_kit.closure margin, the J1-J3 angle's distance from the dyad's fold), per-part sample counts / in-band / min
metal over taken poses, and a per-pose dump (kind, plane / elev / axial, taken, why not taken, face min, crown min,
contact depth, th margin) so the T5 contact-depth check can run.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_raglan_rewear.py <id> bench|held [--margin M]
        -> docs/alignment/remeasure/<id>_<wear>.json and <id>_<wear>_perpose.json
    --margin M wears the row's shape with the fold margin set to M (default: the row's own best_params margin); a
    different margin is a MEASUREMENT change (the user's rule is 5 deg in th), reported separately, never the claim.
"""
import importlib.util, json, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                     # noqa: E402
import alignment_wear_probe as WP                                # noqa: E402
import concept_bench as CB                                       # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


def held_bench(nc=110, nw=360):
    """= tools/osn_polish.py held_bench (copied, as tools/alignment_slotted_rewear.py does)"""
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


class _M:
    def __init__(self, cmin): self.cmin = cmin


def run(rid, wear, margin=None):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json"))); P = dict(row["best_params"])
    if margin is not None: P["margin"] = float(margin)
    mod = _load("arr_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    FS = mod.fs(); K = FS.K
    kb = K.bench; cap = {}

    def bench(n_clip=60, n_ws=160):
        B = held_bench(n_clip, n_ws) if (wear == "held" and (n_clip, n_ws) == (110, 360)) else kb(n_clip, n_ws)
        cap[(n_clip, n_ws)] = B; return B
    K.bench = bench
    tmp = os.path.join(AA.REM, f".{rid}_{wear}_frozen_tmp.json"); os.makedirs(AA.REM, exist_ok=True); t0 = time.time()
    try:
        res = FS.frozen(mod.clean(P), tmp)
    finally:
        K.bench = kb
    Bb = cap[(110, 360)]; L = Bb._kit_last; ch, prof, pts, take, ok, hit = L["chain"], L["prof"], L["pts"], L["take"], L["ok"], L["hit"]
    n = len(Bb.idx)
    # crown / wall minima (the model's own extras() samples), recomputed read-only for the near-touch floor
    hubs = [m for m in ch.members if m.kind == "flat"]; Pi = np.array([j for j in np.nonzero(take)[0]], int)
    cmin = np.full(n, np.inf)
    if len(Pi):
        C = np.concatenate([FS.crown_points(m, prof[m.name])[Pi] for m in hubs], 1)
        dc = K.dist_many(Bb, np.repeat(Pi, C.shape[1]), C.reshape(-1, 3)).reshape(len(Pi), C.shape[1]); cmin[Pi] = dc.min(1)
    M = _M({int(j): float(cmin[j]) for j in range(n) if np.isfinite(cmin[j])})
    deep = AA.deep_audit(M, Bb); probe = WP.analyse(M, Bb)
    # fold margin in th (the kit's closure margin: J1-J3 angle's distance from the dyad's fold), per pose
    F = Bb._kitF; p1, p2, p3, okc, mg = mod.axes(F, mod.clean(P))
    th = np.degrees(np.arccos(np.clip((p1 * p3).sum(-1), -1, 1)))
    taken = np.array([AA._taken(Bb, j) for j in range(n)])
    # per-part samples / in-band (clip and ws) / min metal over taken poses (res is the member concatenation, crowns appended)
    sizes = [(m.name, pts[m.name].shape[1]) for m in ch.members]; parts = {}; o = 0
    kind = np.array(Bb.kind); el = np.array([q["elev"] for q in Bb.poses])
    for name, s in sizes:
        rec = {"samples": int(s)}
        for kk in ("clip", "ws"):
            sel = [j for j in range(n) if taken[j] and kind[j] == kk]
            if sel:
                d = np.concatenate([Bb.res[j][o:o + s] for j in sel])
                rec[f"ib14_{kk}"] = round(float(((d >= 2) & (d <= 14)).mean()), 4); rec[f"over14_{kk}"] = round(float((d > 14).mean()), 4)
                rec[f"median_{kk}"] = round(float(np.median(d)), 2)
        mins = [float(np.min(Bb.res[j][o:o + s])) for j in range(n) if taken[j]]
        rec["min_mm"] = round(min(mins), 2) if mins else None; parts[name] = rec; o += s
    # per-pose dump
    rows = []
    for j in range(n):
        r_ = Bb.res[j]; face = float(np.min(r_[:o])) if r_ is not None else None
        why = None if taken[j] else ("fold/K2" if not ok[j] else ("K6" if hit[j] else "contact"))
        rows.append(dict(j=j, kind=Bb.kind[j], clip=Bb.clip[j], plane=Bb.poses[j]["plane"], elev=Bb.poses[j]["elev"], axial=Bb.poses[j]["axial"],
                         taken=bool(taken[j]), why=why, face_min=None if face is None else round(face, 3),
                         crown_min=None if not np.isfinite(cmin[j]) else round(float(cmin[j]), 3),
                         depth=None if r_ is None or float(np.min(r_)) >= 0 else round(-float(np.min(r_)), 3),
                         th=round(float(th[j]), 3), th_margin=round(float(mg[j]), 3) if np.isfinite(mg[j]) else None, closes=bool(okc[j])))
    tk = taken.copy()
    mgt = mg[tk & np.isfinite(mg)]
    fold = dict(rule_deg=K.FOLD_MARGIN, params_margin=P.get("margin"), min_th_margin_taken=round(float(mgt.min()), 3) if len(mgt) else None,
                p05_th_margin_taken=round(float(np.percentile(mgt, 5)), 3) if len(mgt) else None,
                taken_within_2deg_of_bound=int(((mgt - float(P.get("margin", K.FOLD_MARGIN))) < 2.0).sum()) if len(mgt) else None)
    cont = [r for r in rows if r["depth"] is not None]
    depth = dict(n=len(cont), sum_mm=round(sum(r["depth"] for r in cont), 3), max_mm=round(max([r["depth"] for r in cont], default=0.0), 3),
                 where=sorted(cont, key=lambda r: -r["depth"])[:5])
    ov = [j for j in range(n) if el[j] >= 140 and kind[j] == "ws"]
    raised = [j for j in range(n) if el[j] >= 90 and kind[j] == "ws"]
    reach_bands = {}
    for a, b in ((0, 45), (45, 90), (90, 120), (120, 140), (140, 200)):
        s = [j for j in range(n) if kind[j] == "ws" and a <= el[j] < b]
        reach_bands[f"{a}-{b}"] = [int(sum(taken[s])), len(s)]
    nt = {}
    for r in rows:
        if r["why"]: nt[r["why"]] = nt.get(r["why"], 0) + 1
    parts_ib14 = {k: [v.get("ib14_clip", 0.0), v.get("median_clip"), v["samples"]] for k, v in parts.items()}   # the audit's sampling check format
    out = dict(id=rid, wear=wear, params=P, frozen=res["runs"]["frozen"], fit_fast=res["runs"]["fit"], deep=deep, parts_ib14=parts_ib14, probe=probe, fold=fold,
               contact_depth=depth, parts=parts, overhead_ws=[int(sum(taken[ov])), len(ov)], raised_ws=[int(sum(taken[raised])), len(raised)],
               reach_by_elev=reach_bands, not_taken=nt, mode=Bb.mode, exact=os.environ.get("CB_EXACT") == "1", secs=round(time.time() - t0, 1),
               git=AA._git("rev-parse", "--short", "HEAD"), adapter="tools/alignment_raglan_rewear.py")
    tag = "" if margin is None else f"_m{margin:g}"
    path = os.path.join(AA.REM, f"{rid}_{wear}{tag}.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    json.dump(dict(id=rid, wear=wear, params=P, gap=res["runs"]["frozen"].get("gap"), poses=rows), open(os.path.join(AA.REM, f"{rid}_{wear}{tag}_perpose.json"), "w"), default=float)
    try: os.remove(tmp)
    except OSError: pass
    print(json.dumps(dict(id=rid, wear=wear, frozen={k: res["runs"]["frozen"].get(k) for k in ("gap", "reach", "follow", "inband14", "contact", "gap_near1", "min_metal_skin")},
                          deep={k: v for k, v in deep.items() if k != "coord_spans"}, fold=fold, depth={k: v for k, v in depth.items() if k != "where"},
                          overhead=out["overhead_ws"], raised=out["raised_ws"], not_taken=nt, secs=out["secs"]), default=float), flush=True)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]; mg = float(a[a.index("--margin") + 1]) if "--margin" in a else None
    run(a[0], a[1], mg)
