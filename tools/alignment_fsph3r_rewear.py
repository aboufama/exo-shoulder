"""Alignment re-wear for fold-sph3r (plain spherical 3R, kit template build), which tools/alignment_audit.py remeasure cannot
wrap (no pin-knee-style audit(M, B)) and tools/alignment_kit_rewear.py cannot call (no snap(), no fixed_prof). Read-only on
every claim: the model file docs/concepts/models/fold-sph3r.py runs UNCHANGED; only its extras(B, r) (the crown / wall /
near-touch / overhead report it already runs after K.evaluate) is wrapped to ALSO record, on the same worn bench:
  * alignment_audit.deep_audit (near-touch at 1 / 2 / 3 mm incl. the hub crowns / walls the model measures, clip metal
    histogram, band read 3-14 mm, overhead p10 floor) and alignment_wear_probe.analyse (unscored workspace in-band,
    overhead in-band, clearance floors, reach by elevation, contact poses with depth);
  * per part [in-band 2-14 over taken clip poses, median mm, samples per pose] (sliced from the bench's own B.res);
  * the J1-J3 fold margin th (tools/concept_kit.py lines 25-30) over the TAKEN poses;
  * a per-pose dump (kind, plane, elev, axial, evaluated, taken, min metal incl. crowns / walls, contact).

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_fsph3r_rewear.py claim
        Bench(60,160) fast (the screen's bench): the row's best (CMA F, q 0.98) and best_near_touch_clean (CMA G, q 1.0)
        -> docs/alignment/remeasure/fold-sph3r_claim.json + fold-sph3r_claim_bench_perpose.json (F) + _G_ variant
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_fsph3r_rewear.py bench|held [F|G]
        the model's own frozen() (fit Bench(60,160), freeze every underside, wear Bench(110,360) exact); held = the same
        with Bench(110,360) replaced by the held-out bench (poses disjoint from Bench(110,360), = tools/osn_polish.py
        held_bench) -> docs/alignment/remeasure/fold-sph3r_<wear>.json (+ _perpose)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import alignment_audit as AA                                     # noqa: E402
import alignment_wear_probe as WP                                # noqa: E402
import concept_bench as CB                                       # noqa: E402

RID = "fold-sph3r"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp)
    sys.modules[name] = m; sp.loader.exec_module(m); return m


class _M:
    def __init__(self, cmin): self.cmin = cmin


def held_bench(nc=110, nw=360):
    """= tools/osn_polish.py held_bench (copied, as tools/alignment_raglan_rewear.py does)"""
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


def read_bench(mod, B, p):
    """everything the score does not show, read from the worn bench after the model's own extras() ran"""
    K = mod.K; L = B._kit_last; ch, prof, pts = L["chain"], L["prof"], L["pts"]
    ev = [j for j in range(len(B.res)) if B.res[j] is not None]
    hubs = [m for m in ch.members if m.kind == "flat"]
    cmin = {}
    if ev:                                                        # the model's own crown / wall points (crown_points), as extras() does
        C = np.concatenate([mod.crown_points(m, prof[m.name])[ev] for m in hubs], 1)
        dc = K.dist_many(B, np.repeat(ev, C.shape[1]), C.reshape(-1, 3)).reshape(len(ev), C.shape[1])
        cmin = {int(j): float(dc[k].min()) for k, j in enumerate(ev)}
    deep = AA.deep_audit(_M(cmin), B)
    probe = WP.analyse(_M(cmin), B)
    tk = [j for j in ev if float(np.min(B.res[j])) >= 0]
    tkc = [j for j in tk if B.kind[j] == "clip"]
    parts, o = {}, 0
    for m in ch.members:                                          # B.res[j] = members' distances in ch.members order (K.evaluate)
        s = pts[m.name].shape[1]
        d = np.concatenate([B.res[j][o:o + s] for j in tkc]) if tkc else np.zeros(0); o += s
        parts[m.name] = [round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else 0.0, round(float(np.median(d)), 2) if len(d) else None, int(s)]
    J1, J3 = np.asarray(ch.joints["J1"], float), np.asarray(ch.joints["J3"], float)
    th = np.degrees(np.arccos(np.clip((J1 * J3).sum(-1) / np.linalg.norm(J1, axis=-1) / np.linalg.norm(J3, axis=-1), -1, 1)))
    a1, a2 = float(p["a1"]), float(p["a2"])
    marg = np.minimum.reduce([th - abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th])
    thm = dict(min_th_margin_taken_deg=round(float(marg[tk].min()), 2) if tk else None, fold_margin_param_deg=float(p["margin"]),
               n_taken_lt10=int((marg[tk] < 10 - 1e-6).sum()) if tk else 0, n_taken_lt5=int((marg[tk] < 5 - 1e-6).sum()) if tk else 0)
    poses = []
    for j in range(len(B.res)):
        e = B.res[j] is not None
        mm = min(float(np.min(B.res[j])), cmin.get(j, 1e9)) if e else None
        poses.append(dict(i=j, kind=B.kind[j], clip=B.clip[j], plane=B.poses[j]["plane"], elev=B.poses[j]["elev"], axial=B.poses[j]["axial"],
                          evaluated=e, taken=bool(e and float(np.min(B.res[j])) >= 0), min_mm=round(mm, 3) if mm is not None else None,
                          contact=bool(e and float(np.min(B.res[j])) < 0), th_margin=round(float(marg[j]), 2)))
    hubF = {m.name: round(float(prof[m.name][0]), 2) for m in hubs}
    return dict(deep=deep, probe=probe, parts_ib14=parts, th_margin=thm, hub_F=hubF, poses=poses)


def wear_claim(mod, P):
    """Bench(60,160) fast (the screen's bench): reproduce the row's number and read what it hides"""
    B = mod.K.bench(60, 160); t = time.time()
    p, r = mod.evaluate(B, dict(P))
    rep = {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "gap_near1", "min_metal_skin", "min_face_skin",
                                 "crown_contact_poses", "crown_min", "overhead", "honest", "audit", "inband_member", "mass_g", "min_margin", "q")}
    rb = read_bench(mod, B, p)
    return dict(params=p, report=rep, mode=B.mode, secs=round(time.time() - t, 1), **rb)


def main(a):
    mode = a[0]; which = a[1] if len(a) > 1 else "F"
    row = json.load(open(os.path.join(AA.ROWS, RID + ".json")))
    PF = dict(row["best_params"]); PG = dict(row["best_near_touch_clean"]["params"])
    mod = _load("afs_" + RID.replace("-", "_"), os.path.join(AA.MODELS, RID + ".py"))
    os.makedirs(AA.REM, exist_ok=True); git = AA._git("rev-parse", "--short", "HEAD")
    if mode == "claim":
        os.environ.pop("CB_EXACT", None)
        out = dict(id=RID, wear="claim-bench Bench(60,160) fast", git=git, source="tools/alignment_fsph3r_rewear.py claim: model unchanged (evaluate + extras)")
        for lab, P in (("F", PF), ("G", PG)):
            res = wear_claim(mod, P); poses = res.pop("poses")
            out[lab] = res
            dump = dict(id=RID, wear="bench", bench="Bench(60,160) fast (the screen's claim bench)", config=lab, plain=res["deep"]["plain"],
                        params=res["params"], git=git, poses=poses,
                        note="per-pose dump of the claim bench; contact = evaluated with metal < 0 mm (skin face or hub crown / wall)")
            fn = f"{RID}_claim_bench_perpose.json" if lab == "F" else f"{RID}_claimG_bench_perpose.json"
            json.dump(dump, open(os.path.join(AA.REM, fn), "w"), indent=1, default=float)
            print(lab, json.dumps(dict(report=res["report"], deep={k: v for k, v in res["deep"].items() if k != "coord_spans"},
                                       th=res["th_margin"], parts=res["parts_ib14"]), default=float), flush=True)
        json.dump(out, open(os.path.join(AA.REM, f"{RID}_claim.json"), "w"), indent=1, default=float)
        return
    P = PF if which == "F" else PG
    K = mod.K; kb = K.bench; cap = {}

    def bench(n_clip=60, n_ws=160):
        B = held_bench(n_clip, n_ws) if (mode == "held" and (n_clip, n_ws) == (110, 360)) else kb(n_clip, n_ws)
        cap[(n_clip, n_ws)] = B; return B
    ex0 = mod.extras; box = {}

    def extras(B, r):
        r = ex0(B, r)
        if len(B.idx) > 300: box["r"] = r; box["read"] = read_bench(mod, B, dict(mod.PARAMS, **P))
        return r
    K.bench = bench; mod.extras = extras
    tmp = os.path.join(AA.REM, f".{RID}_{mode}_{which}_frozen_tmp.json"); t0 = time.time()
    try:
        res = mod.frozen(dict(mod.PARAMS, **P), tmp)
    finally:
        K.bench = kb; mod.extras = ex0
    rd = box["read"]; poses = rd.pop("poses")
    fz = res["runs"]["frozen"]; fit = res["runs"]["fit"]
    keep = ("gap", "reach", "follow", "inband14", "inband10", "contact", "gap_near1", "min_metal_skin", "min_face_skin", "crown_contact_poses",
            "crown_min", "overhead", "honest", "audit", "inband_member", "min_margin")
    sfx = "" if which == "F" else "_G"
    out = dict(id=RID, wear=mode, config=which, params=res["params"], fit_fast=None, fit={k: fit.get(k) for k in keep},
               frozen={k: fz.get(k) for k in keep}, parts_ib14=rd["parts_ib14"], th_margin=rd["th_margin"], hub_F=rd["hub_F"],
               deep=rd["deep"], probe=rd["probe"], exact=os.environ.get("CB_EXACT") == "1", secs=round(time.time() - t0, 1), git=git,
               source=f"tools/alignment_fsph3r_rewear.py {mode} {which}: the model's own frozen() unchanged (extras wrapped to record more); "
                      f"fit Bench(60,160) {'exact' if os.environ.get('CB_EXACT') == '1' else 'fast'}, worn "
                      f"{'Bench(110,360)' if mode == 'bench' else 'held_bench(110,360) (poses disjoint from Bench(110,360))'}")
    json.dump(out, open(os.path.join(AA.REM, f"{RID}_{mode}{sfx}.json"), "w"), indent=1, default=float)
    json.dump(dict(id=RID, wear=mode, config=which, frozen=dict(gap=fz.get("gap")), git=git, poses=poses),
              open(os.path.join(AA.REM, f"{RID}_frozen{sfx}_{mode}_perpose.json"), "w"), indent=1, default=float)
    try: os.remove(tmp)
    except OSError: pass
    print(json.dumps(dict(frozen=out["frozen"], th=out["th_margin"], deep={k: v for k, v in rd["deep"].items() if k != "coord_spans"}), default=float))


if __name__ == "__main__":
    main(sys.argv[1:])
