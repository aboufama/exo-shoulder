"""Alignment re-wear adapter for the slotted-eccentric kit models (slotted-eccentric-j2-3r and its pin-knee-seat child
slotted-eccentric-pin-knee-3r), which tools/alignment_audit.py remeasure cannot wrap (no pin-knee-style audit(M, B)) and
tools/alignment_kit_rewear.py cannot drive (no snap(), evaluate() has no fixed_prof). Read-only on every claim: the model
file runs UNCHANGED through its own frozen() (fit Bench(60,160) fast at the 1 mm part-part rule, every level frozen, worn
on Bench(110,360) - exact with CB_EXACT=1 - or on the held-out bench = tools/osn_polish.py held_bench(): poses disjoint
from Bench(110,360), held-out clips excluded). Only two things are wrapped, both pass-through:
  * concept_kit.bench: for the held wear, the big bench is swapped for the held bench (the fit bench is untouched);
  * the parent's build(): records, for the chain the worn bench keeps (B._kit_last['chain']), the per-pose th (J1-J3),
    the effective a2, the fold margin mg in th (the model's own geom(): distance to the dyad's fold at the effective a2),
    the knee transmission psi, the knee angle K and the roller coordinates on the track.
After the wear the bench is read by the audit's own instruments: alignment_audit.deep_audit (near-touch at 1 / 2 / 3 mm,
clip metal histogram, band read 3-14 mm) and alignment_wear_probe.analyse (unscored workspace in-band, overhead,
clearance floors, contact depths), plus a per-pose dump (min metal, kind, elev, taken, contact depth, th, mg, knee) so
the T5 contact-depth check can run.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_slotted_rewear.py <id> bench|held
        -> docs/alignment/remeasure/<id>_<wear>.json and <id>_<wear>_perpose.json
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
    """= tools/osn_polish.py held_bench (copied, not imported: that module loads a verifier on import)"""
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


class _M:            # deep_audit / analyse read M.cmin (no extra walls in the kit build)
    cmin = {}


def _span(a, sel):
    a = np.asarray(a, float)[sel]; a = a[np.isfinite(a)]
    return [round(float(a.min()), 3), round(float(a.max()), 3)] if len(a) else None


def run(rid, wear):
    row = json.load(open(os.path.join(AA.ROWS, rid + ".json"))); P = dict(row["best_params"])
    mod = _load("asr_" + rid.replace("-", "_"), os.path.join(AA.MODELS, rid + ".py"))
    SE = getattr(mod, "SE", mod); K = SE.K
    p0 = mod._clean(P) if hasattr(mod, "_clean") and mod is not SE else dict(SE.PARAMS, **P)
    rec = {}; ob = SE.build

    def build(B_, F, p):
        ch = ob(B_, F, p)
        try:
            p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"])); G = SE.geom(p1, p3, p)
            knee = K.axis_angle(G["K"], G["p2"], p3)
            rec[id(ch)] = dict(th=np.asarray(G["th"]), a2e=np.asarray(G["a2e"]), mg=np.asarray(G["mg"]), psi=np.asarray(G["psi"]),
                               knee=np.asarray(knee), q=np.asarray(ch.q))
        except Exception as e:                                        # the record is extra; never break the wear
            rec[id(ch)] = dict(err=str(e))
        return ch
    SE.build = build
    kb = K.bench; cap = {}

    def bench(n_clip=60, n_ws=160):
        B = held_bench(n_clip, n_ws) if (wear == "held" and (n_clip, n_ws) == (110, 360)) else kb(n_clip, n_ws)
        cap[(n_clip, n_ws)] = B; return B
    K.bench = bench
    tmp = os.path.join(AA.REM, f".{rid}_{wear}_frozen_tmp.json"); os.makedirs(AA.REM, exist_ok=True); t0 = time.time()
    try:
        SE.ID = rid; res = SE.frozen(p0, tmp)
    finally:
        SE.build = ob; K.bench = kb
    try: os.remove(tmp)
    except OSError: pass
    Bb = cap[(110, 360)]; L = Bb._kit_last; n = len(Bb.idx)
    g = rec.get(id(L["chain"]), {})
    take = np.asarray(L["take"], bool); kind = np.array(Bb.kind); el = np.array([p["elev"] for p in Bb.poses])
    deep = AA.deep_audit(_M, Bb)
    WP.kind, WP.el = kind, el
    try:
        probe = WP.analyse(_M, Bb)
    except Exception as e:
        probe = dict(err=str(e))
    mins = [None if Bb.res[i] is None else round(float(np.min(Bb.res[i])), 3) for i in range(n)]
    tk = [i for i in range(n) if Bb.res[i] is not None and float(np.min(Bb.res[i])) >= 0]
    cont = [i for i in range(n) if Bb.res[i] is not None and float(np.min(Bb.res[i])) < 0]
    sel = np.zeros(n, bool); sel[tk] = True
    kin = {}
    if "th" in g:
        kin = dict(th_taken=_span(g["th"], sel), a2e_taken=_span(g["a2e"], sel), knee_taken=_span(g["knee"], sel),
                   psi_taken=_span(np.minimum(g["psi"], 180 - g["psi"]), sel), fold_margin_th_min_taken=_span(g["mg"], sel),
                   q_spans_taken={f"q{j}": _span(g["q"][:, j], sel) for j in range(g["q"].shape[1])} if g["q"].ndim == 2 else None,
                   overhead_taken=int(sum(1 for i in tk if kind[i] == "ws" and el[i] >= 140)),
                   overhead_ws=int(sum(1 for i in range(n) if kind[i] == "ws" and el[i] >= 140)),
                   overhead_kin_ok=int(sum(1 for i in range(n) if kind[i] == "ws" and el[i] >= 140 and bool(np.asarray(L["ok"])[i]))))
    depth = sorted(((round(-float(np.min(Bb.res[i])), 3), i) for i in cont), reverse=True)
    rep = res["runs"]["frozen"]
    out = dict(id=rid, wear=wear, params=p0, fit_fast={k: res["runs"]["fit"].get(k) for k in ("gap", "reach", "follow", "inband14", "contact", "honest")},
               frozen={k: rep.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1", "min_metal_skin",
                                               "overhead", "inband_member", "closure", "collide", "post_lift", "audit", "th_need")},
               audit=dict(gap_near1=rep.get("gap_near1"), near_touch_min_mm=rep.get("min_metal_skin")),
               deep=deep, probe=probe, kin=kin,
               contact_depth=dict(n=len(cont), sum_mm=round(sum(d for d, _ in depth), 3), max_mm=depth[0][0] if depth else 0.0,
                                  over3mm=sum(1 for d, _ in depth if d > 3),
                                  deepest=[dict(i=i, mm=d, kind=str(kind[i]), clip=str(Bb.clip[i]) if hasattr(Bb, "clip") and Bb.clip else None,
                                                pose=Bb.poses[i]) for d, i in depth[:5]]),
               mode=Bb.mode, secs=round(time.time() - t0, 1), exact=os.environ.get("CB_EXACT") == "1", git=AA._git("rev-parse", "--short", "HEAD"),
               source=f"tools/alignment_slotted_rewear.py: model {rid}.py unchanged (its own frozen(): fit Bench(60,160) fast, frozen levels), "
                      f"worn {'Bench(110,360)' if wear == 'bench' else 'held_bench(110,360) = tools/osn_polish.py held_bench'}")
    path = os.path.join(AA.REM, f"{rid}_{wear}.json"); json.dump(out, open(path, "w"), indent=1, default=float)
    if "knee" in g: deep.setdefault("coord_spans", {})["dK_deg_abs"] = _span(g["knee"], sel)   # K = the slaved knee hub's joint angle (deg)
    out["parts_ib14"] = rep.get("inband_member")                                                 # fractions only (the kit records no counts)
    json.dump(out, open(path, "w"), indent=1, default=float)
    cs = set(cont); tks = set(tk)
    pp = dict(id=rid, wear=wear, frozen=dict(gap=rep.get("gap")), mode=Bb.mode, idx=[int(x) for x in Bb.idx],
              poses=[dict(i=i, kind=str(kind[i]), elev=float(el[i]), plane=float(Bb.poses[i]["plane"]), axial=float(Bb.poses[i]["axial"]),
                          min_mm=mins[i], taken=bool(i in tks), contact=bool(i in cs), take_model=bool(take[i]),
                          th=None if "th" not in g else round(float(g["th"][i]), 3), mg=None if "mg" not in g else round(float(g["mg"][i]), 3),
                          knee=None if "knee" not in g else round(float(g["knee"][i]), 3)) for i in range(n)])
    json.dump(pp, open(os.path.join(AA.REM, f"{rid}_{wear}_perpose.json"), "w"), default=float)
    print(json.dumps(dict(frozen=out["frozen"], deep={k: v for k, v in deep.items() if k != "coord_spans"}, kin=kin,
                          contact_depth={k: v for k, v in out["contact_depth"].items() if k != "deepest"}, secs=out["secs"], out=path), default=float))
    return out


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
