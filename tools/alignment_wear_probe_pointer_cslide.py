"""Alignment probe for pointer-cslide (read-only): the model runs UNCHANGED from docs/concepts/models/pointer-cslide.py with
the row's best_params. Fit = its own bench_eval on Bench(60,160) fast (the shape it derives from the bench poses - the
J3 window (c, T), the band radius rho, the saddle profile and the neck profile - is cached by the model under the
params key, so a later call on another bench reuses that shape: the frozen-shape protocol, no refit). Then the frozen
shape is worn on Bench(110,360) (exact with CB_EXACT=1) and on the disjoint held-out pose bench (exact).

For each wear it records what the score does not show:
  * the scored report (as the model's bench_eval returns it, outer-face contact included);
  * per-member sample counts, per-member in-band (clip frames, as the kit computes it), sample- vs part-weighted in-band;
  * near-touch gaps (min metal incl. the band outer face / shoe crown < 1 / 2 / 3 mm counted as contact);
  * contact depths per pose and the member that is deepest;
  * tools/alignment_wear_probe.py analyse(): unscored workspace in-band, overhead reach, clearance floor histogram;
  * raised-arm reach (elev >= 90, all poses), the singular-margin floor over taken poses, the J3 window.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_pointer_cslide.py <fast|bench|held|all> <out_dir>
    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_wear_probe_pointer_cslide.py cf <out_dir>   # saddle 1 vs 0, same params
"""
import importlib.util, json, os, sys, time, types
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import alignment_wear_probe as W                             # noqa: E402

ID = "pointer-cslide"


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


MOD = _load("pointer_cslide_probe_model", os.path.join(REPO, "docs", "concepts", "models", f"{ID}.py"))
K = MOD.K
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", f"{ID}.json")))
P = dict(MOD.PARAMS, **ROW["best_params"])
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")


def held_bench(nc=110, nw=360):
    """= docs/concepts/verify/crest-knee-3r.py held_bench (= tools/osn_polish.py): poses DISJOINT from Bench(110,360),
    held-out clips still excluded, exact path"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; Pz = Z["POSE"]
    big, _, _, _ = CB._select(110, 360); bigs = set(big.tolist())
    fit_ids = [names.index(x) for x in CB.FIT]; ws_id = names.index("Workspace (envelope)")
    cl = np.array([i for i in np.nonzero(np.isin(cid, fit_ids))[0] if i not in bigs]); ws = np.array([i for i in np.nonzero(cid == ws_id)[0] if i not in bigs])
    cl = cl[np.linspace(0, len(cl) - 1, min(nc, len(cl))).round().astype(int)]; ws = ws[np.linspace(0, len(ws) - 1, min(nw, len(ws))).round().astype(int)]
    B = CB.Bench(20, 20); idx = np.r_[cl, ws]
    B.idx = idx; B.kind = ["clip"] * len(cl) + ["ws"] * len(ws); B.clip = [names[c] for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in Pz[idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.grid = None; B._V = None; B.mode = "exact"; B.key = "held"
    return B


def outer_min(B, Pi):
    """min distance of the band outer face / shoe crown per taken pose (the same points as the model's outer_contact)"""
    F = B._kitF; a1, p2, d3, xP, yP, E1, E2, th, ok, margin = MOD.kin(F, P)
    Dd = MOD.design(B, P); c, T, rho = Dd["c"], Dd["T"], Dd["rho"]; band_ang, shoe_off = MOD.angles(P, c, T, rho); s = P["s"]
    lip = 0.0 if "prof" in Dd else MOD.LIP
    Xb = MOD.ring_pts(None, xP[Pi], yP[Pi], d3[Pi], s + np.array([-MOD.BAND_W / 2, 0.0, MOD.BAND_W / 2]), band_ang, rho + lip + MOD.BAND_T)
    Xs = MOD.ring_pts(None, E1[Pi], E2[Pi], d3[Pi], s + np.array([-MOD.BAND_W / 2, 0.0, MOD.BAND_W / 2 + 2]), P["phi_s"] + shoe_off,
                      rho + lip + MOD.BAND_T + MOD.CAP)
    Y = np.concatenate([Xb, Xs], 1); m = Y.shape[1]; nb = Xb.shape[1]
    d = K.dist_many(B, np.repeat(Pi, m), Y.reshape(-1, 3)).reshape(len(Pi), m)
    return d[:, :nb].min(1), d[:, nb:].min(1), margin, th


def near_gap(B, floor, x):
    res0 = list(B.res)
    for i in range(len(B.res)):
        if B.res[i] is not None and floor.get(i, 1e9) < x: B.res[i] = np.append(B.res[i], -1.0)
    r = B.report(); B.res = res0
    return {k: r[k] for k in KEYS}


def wear(B, label):
    t0 = time.time()
    if getattr(B, "_kitF", None) is None: B._kitF = K.frames(B)
    rep = MOD.bench_eval(B, P)
    L = B._kit_last; ch = L["chain"]; pts = L["pts"]; take = L["take"]; Pi = np.nonzero(take)[0]
    sizes = {m.name: int(pts[m.name].shape[1]) for m in ch.members}
    ob, os_, margin, th = outer_min(B, Pi) if len(Pi) else (np.zeros(0), np.zeros(0), None, None)
    per_min = {}; floor = {}; deep = []
    names = [m.name for m in ch.members]; ntot = sum(sizes.values())
    for j, i in enumerate(Pi):
        r = np.asarray(B.res[i])[:ntot]; o = 0; mins = {}
        for nm in names:
            mins[nm] = float(r[o:o + sizes[nm]].min()); o += sizes[nm]
        mins["band_outer"] = float(ob[j]); mins["shoe_crown"] = float(os_[j])
        per_min[int(i)] = mins; floor[int(i)] = min(mins.values())
        if floor[int(i)] < 0:
            w = min(mins, key=mins.get)
            deep.append(dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                             depth_mm=round(floor[int(i)], 2), member=w, members_below0={k: round(v, 2) for k, v in mins.items() if v < 0}))
    deep.sort(key=lambda r: r["depth_mm"])
    # in-band per member over clip frames with no contact (= the kit's per-member reading)
    clip = np.array([B.kind[i] == "clip" for i in Pi], bool); good = np.array([floor[int(i)] >= 0 for i in Pi], bool)
    per_ib = {}; o = 0
    for nm in names:
        if (clip & good).any():
            dm = np.concatenate([np.asarray(B.res[i])[o:o + sizes[nm]] for i, c_, g_ in zip(Pi, clip, good) if c_ and g_])
            per_ib[nm] = dict(n_samples=sizes[nm], inband14=round(float(((dm >= 2) & (dm <= 14)).mean()), 4),
                              median_mm=round(float(np.median(dm)), 1), p10_mm=round(float(np.percentile(dm, 10)), 1), p90_mm=round(float(np.percentile(dm, 90)), 1))
        o += sizes[nm]
    sw = rep["inband14"]; pw = round(float(np.mean([v["inband14"] for v in per_ib.values()])), 4) if per_ib else None
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
    ok = lambda j: B.res[j] is not None and float(np.min(B.res[j])) >= 0.0
    ra = np.nonzero(el >= 90)[0]; ohw = np.nonzero((el >= 140) & (kind == "ws"))[0]
    tk_ok = [int(i) for i in Pi if ok(i)]
    # why the overhead workspace poses are not taken
    Dd = MOD.design(B, P); F = B._kitF
    a1, p2, d3, xP, yP, E1, E2, th_all, ok0, marg_all = MOD.kin(F, P)
    win = np.abs(MOD.wrap(th_all - Dd["c"])) <= Dd["T"] / 2 + 1e-9
    def why(i):
        if ok(i): return "taken"
        if not (marg_all[i] >= P["sing"]): return "singular"
        if not win[i]: return "window"
        if not L["ok"][i]: return "K2"
        if L["hit"][i]: return "collide"
        return "contact"
    oh_why = {}
    for i in ohw: oh_why[why(i)] = oh_why.get(why(i), 0) + 1
    all_why = {}
    for i in range(len(B.idx)): all_why[why(i)] = all_why.get(why(i), 0) + 1
    M = types.SimpleNamespace(cmin={int(i): float(min(ob[j], os_[j])) for j, i in enumerate(Pi)})
    out = dict(wear=label, mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", n=len(B.idx),
               report={k: rep[k] for k in KEYS}, outer_contact_poses=rep.get("outer_contact_poses"), honest=rep.get("honest"), audit=rep.get("audit"),
               shape=dict(c=Dd["c"], T=Dd["T"], rho=Dd["rho"], saddle="prof" in Dd),
               sample_counts=sizes, inband_member=per_ib, inband_sample_weighted=sw, inband_part_weighted=pw,
               near_touch={f"gap_near{x}": near_gap(B, floor, x) for x in (1, 2, 3)},
               taken_floor_lt={f"{x}mm": int(sum(1 for i in tk_ok if floor[i] < x)) for x in (1, 2, 3)}, n_taken=len(tk_ok),
               taken_floor_lt_by_member={f"{x}mm": {nm: int(sum(1 for i in tk_ok if per_min[i][nm] < x)) for nm in names + ["band_outer", "shoe_crown"]}
                                         for x in (1, 2, 3)},
               raised_arm_reach=[int(sum(ok(i) for i in ra)), int(len(ra))], overhead_ws140=[int(sum(ok(i) for i in ohw)), int(len(ohw))],
               overhead_ws140_why_not=oh_why, all_why=all_why,
               singular_margin_min_taken=round(float(np.min(marg_all[tk_ok])), 2) if tk_ok else None,
               singular_margin_p05_taken=round(float(np.percentile(marg_all[tk_ok], 5)), 2) if tk_ok else None,
               j3_window_edge_min_deg=round(float(np.min(Dd["T"] / 2 - np.abs(MOD.wrap(th_all[tk_ok] - Dd["c"])))), 2) if tk_ok else None,
               contact_poses=deep, contact_depth_sum_mm=round(float(-sum(r["depth_mm"] for r in deep)), 2),
               probe=W.analyse(M, B), secs=round(time.time() - t0, 1))
    return out


def counterfactual(out_dir):
    """the saddle's share of the number, same params, same fast bench: saddle=1 (the claim) vs saddle=0 (the spec's
    one-radius band; the track and the shoe still at a radius from the same radial march), and the claim's band body
    thickness and outer-face standoff (the faces the in-band does not read)"""
    old = os.environ.pop("CB_EXACT", None)
    try: B = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    B._kitF = K.frames(B); out = {}
    for sd in (1, 0):
        p = dict(P, saddle=sd); rep = MOD.bench_eval(B, p); D = MOD.design(B, p)
        L = B._kit_last; tk = L["take"]; Pi = np.nonzero(tk)[0]
        clip = np.array([B.kind[i] == "clip" for i in Pi], bool)
        F = B._kitF; a1, p2, d3, xP, yP, E1, E2, th, ok, margin = MOD.kin(F, p)
        c, T, rho = D["c"], D["T"], D["rho"]; band_ang, shoe_off = MOD.angles(p, c, T, rho); s = p["s"]
        lip = 0.0 if "prof" in D else MOD.LIP
        rows = s + np.arange(-MOD.BAND_W / 2, MOD.BAND_W / 2 + 1e-6, 2.0)
        Pc = Pi[clip]
        Xo = MOD.ring_pts(None, xP[Pc], yP[Pc], d3[Pc], rows, band_ang, rho + lip + MOD.BAND_T)      # band outer face (track top)
        Xc = MOD.ring_pts(None, E1[Pc], E2[Pc], d3[Pc], rows, p["phi_s"] + shoe_off, rho + lip + MOD.BAND_T + MOD.CAP)   # shoe crown
        do = K.dist_many(B, np.repeat(Pc, Xo.shape[1]), Xo.reshape(-1, 3)); dc = K.dist_many(B, np.repeat(Pc, Xc.shape[1]), Xc.reshape(-1, 3))
        e = dict(report={k: rep[k] for k in KEYS}, inband_member=rep["inband_member"], mass_g=rep.get("mass_g"), rho=round(rho, 2),
                 T=round(T, 1), c=round(c, 1), outer_contact_poses=rep.get("outer_contact_poses"),
                 band_outer_face_mm=dict(p10=round(float(np.percentile(do, 10)), 1), median=round(float(np.median(do)), 1), p90=round(float(np.percentile(do, 90)), 1)),
                 shoe_crown_mm=dict(p10=round(float(np.percentile(dc, 10)), 1), median=round(float(np.median(dc)), 1), p90=round(float(np.percentile(dc, 90)), 1)))
        if "prof" in D:
            tb = rho + MOD.BAND_T - np.asarray(D["prof"]).ravel()
            e["band_body_thickness_mm"] = dict(min=round(float(tb.min()), 1), p10=round(float(np.percentile(tb, 10)), 1), median=round(float(np.median(tb)), 1),
                                               p90=round(float(np.percentile(tb, 90)), 1), max=round(float(tb.max()), 1))
        out[f"saddle{sd}"] = e
    json.dump(out, open(os.path.join(out_dir, f"{ID}_saddle_counterfactual.json"), "w"), indent=1, default=float)
    print(json.dumps(out, default=float))


def main(which, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    if which == "cf": return counterfactual(out_dir)
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    fit = wear(B1, "fit_fast")                                      # fills MOD._CACHE: the shape is frozen from here
    json.dump(fit, open(os.path.join(out_dir, f"{ID}_fit_fast.json"), "w"), indent=1, default=float)
    print("fit", fit["report"], flush=True)
    for w in (["bench", "held"] if which == "all" else [] if which == "fast" else [which]):
        key0 = MOD._key(P); shape0 = dict(MOD._CACHE[key0])
        B = CB.Bench(n_clip=110, n_ws=360) if w == "bench" else held_bench()
        r = wear(B, w); r["fit_fast"] = fit["report"]
        assert MOD._CACHE[key0] is not None and MOD._CACHE[key0]["T"] == shape0["T"] and MOD._CACHE[key0]["rho"] == shape0["rho"], "shape refit"
        r["frozen_shape_check"] = "design cache unchanged (c, T, rho, profiles from the fast fit)"
        json.dump(r, open(os.path.join(out_dir, f"{ID}_{w}.json"), "w"), indent=1, default=float)
        print(w, r["report"], "near2", r["near_touch"]["gap_near2"]["gap"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
