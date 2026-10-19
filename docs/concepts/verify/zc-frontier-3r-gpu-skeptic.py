#!/usr/bin/env python3
"""Independent skeptic of the GPU golden search (tools/gpu_bench.py, docs/research/golden/gpu_frontier.json).

Not the claimant's harness: it drives the kit model (docs/concepts/models/zc-frontier-3r.py = spine-parked model checks
+ docs/concepts/verify/spine-parked-j2-3r.py top_check) directly, builds the benches itself (fit = fast grid, wear =
EXACT libigl, CB_EXACT forced on the wear bench only), re-derives the gap from its components with concept_bench.gap_of,
re-counts reach / overhead / near-touch from the per-pose residuals, and checks the rulings on the config itself.

    python3 docs/concepts/verify/zc-frontier-3r-gpu-skeptic.py frozen 'PARAMS' OUT.json [--fits fit110,fit60]
    python3 docs/concepts/verify/zc-frontier-3r-gpu-skeptic.py kitparity ROWS.json OUT.json [--bench 110,360] [--procs 4]
          ROWS = [{params, gap, near, reach, follow, inband14, inband10, contact}] carrying GPU numbers -> kit FAST numbers
    python3 docs/concepts/verify/zc-frontier-3r-gpu-skeptic.py pick OUT.json [--n 20] [--seed s]
          20 new configs: 10 perturbations around the claimed basin (all four stack orders) + 10 uniform draws over the
          zc box inside the J1 seat region (new seed; none from the claimant's parity sets)
"""
import argparse, importlib.util, json, math, multiprocessing as mp, os, sys, time
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
_W = {}
METRICS = ("gap", "near", "reach", "follow", "inband14", "inband10", "contact")


def model():
    if "M" not in _W:
        spec = importlib.util.spec_from_file_location("zc_skeptic_model", os.path.join(REPO, "docs", "concepts", "models", "zc-frontier-3r.py"))
        m = importlib.util.module_from_spec(spec); sys.modules["zc_skeptic_model"] = m; spec.loader.exec_module(m); _W["M"] = m
    return _W["M"]


def make_bench(nc, nw, exact):
    M = model(); old = os.environ.get("CB_EXACT")
    if exact: os.environ["CB_EXACT"] = "1"
    else: os.environ.pop("CB_EXACT", None)
    try:
        B = M.K.bench(nc, nw)
    finally:
        if old is None: os.environ.pop("CB_EXACT", None)
        else: os.environ["CB_EXACT"] = old
    return B


def rules(p_in):
    """the 2026-10-16 ~05:50 rulings checked on the config, not on the model's own snap"""
    M = model(); K = M.K; p = M.snap(p_in); u1 = K.bvec(p["az"], p["el"])
    clamp = {k: (p_in[k], p[k]) for k in ("az", "el", "a1", "a2", "wd", "q", "end_extra") if k in p_in and abs(float(p_in[k]) - p[k]) > 1e-9}
    return dict(seat_ok=M.seat_ok(p["az"], p["el"]), u1_anterior=round(float(u1[0]), 4), ant_max=M.ANT_MAX,
                hub_radii=[p["rad1"], p["rad2"], p["rad3"]], kit_HUB_R=K.HUB_R, kit_STACK=K.STACK, kit_CROWN=K.CROWN,
                margin=p["margin"], width=p["width"], t_link=p["t_link"], clamped_by_snap=clamp,
                o20_only=bool(K.HUB_R == 10.0 and K.CROWN == 12.25 and all(r == 10.0 for r in (p["rad1"], p["rad2"], p["rad3"]))),
                margin5=bool(p["margin"] == 5.0))


def per_pose(B, r):
    """re-count from the per-pose residuals (after the verifier's top faces were appended): reach, overhead, near"""
    M = model(); SP = M.SPM
    ws = np.array([k == "ws" for k in B.kind]); el = np.array([q["elev"] for q in B.poses])
    taken = np.array([SP._taken(B, j) for j in range(len(B.res))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.res))])
    tk = np.nonzero(taken)[0]; d = np.concatenate([B.res[j] for j in tk]) if len(tk) else np.zeros(0)
    tc = np.nonzero(taken & ~ws)[0]; dc = np.concatenate([B.res[j] for j in tc]) if len(tc) else np.zeros(0)
    over = ws & (el >= 140)
    return dict(n_ws=int(ws.sum()), n_clip=int((~ws).sum()), reach_recount=round(float(taken[ws].mean()), 4),
                follow_recount=round(float(taken[~ws].mean()), 4), overhead_n=int(over.sum()),
                overhead_taken=int((taken & over).sum()), overhead_reach=round(float(taken[over].mean()), 4) if over.any() else None,
                # the bench's in-band is over the taken CLIP frames only (concept_bench.report); the all-taken share
                # (workspace poses too) is reported beside it as a red-team number, not scored
                inband14_recount_clip=round(float(((dc >= 2) & (dc <= 14)).mean()), 4) if len(dc) else None,
                inband14_all_taken=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None,
                inband10_all_taken=round(float(((d >= 2) & (d <= 10)).mean()), 4) if len(d) else None,
                taken_min_res_mm=round(float(np.nanmin(mins[taken])), 3) if taken.any() else None,
                taken_poses_under_1mm=int(((mins < 1.0) & taken).sum()))


def report(B, p, r):
    import concept_bench as CB
    v = r.get("v") or {}; vn = r.get("v_near1") or {}
    re_gap = CB.gap_of(v.get("inband14", 0), v.get("follow", 0), v.get("reach", 0), v.get("contact", 0))
    re_near = CB.gap_of(vn.get("inband14", 0), vn.get("follow", 0), vn.get("reach", 0), vn.get("contact", 0))
    out = {k: r.get(k) for k in METRICS + ("honest", "audit", "hub_F", "hub_F_ok", "min_metal_all_faces", "top_contact_poses",
                                           "top_contact_who", "inband_member", "overhead", "crown_contact_poses", "mode")}
    out.update(gap_recomputed=re_gap, near_recomputed=re_near, bench_mode=B.mode, info=None)
    out["per_pose"] = per_pose(B, r)
    L = getattr(B, "_kit_last", None)
    if L is not None and getattr(L.get("chain"), "info", None): out["info"] = L["chain"].info
    return out


def cmd_frozen(a):
    M = model(); p = json.loads(a.params); res = dict(params=p, rules=rules(p), t0=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                                       host=os.uname().nodename, cpus=os.cpu_count())
    Bw = make_bench(110, 360, exact=True); res["wear_mode"] = Bw.mode
    fits = dict(fit110=(110, 360), fit60=(60, 160))
    for name in a.fits.split(","):
        nc, nw = fits[name]; t = time.time(); Bf = make_bench(nc, nw, exact=False)
        res[name] = dict(fit_bench=[nc, nw], fit_mode=Bf.mode)
        if Bf.mode == "exact" or "exact" in str(Bf.mode).lower():
            res[name]["note"] = "no fast cache for the fit bench here: the fit ran on the exact path (a different measurement)"
        pf, rf = M.evaluate(Bf, dict(p)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
        res[name]["fit"] = {k: rf.get(k) for k in METRICS + ("honest",)}
        pb, rb = M.evaluate(Bw, dict(p), fixed_prof=prof)
        res[name]["wear_exact"] = report(Bw, pb, rb); res[name]["secs"] = round(time.time() - t, 1)
        try:
            res[name]["attribution"] = M.attribute(Bw, pb, rb)
        except Exception as e:                                                # noqa: BLE001
            res[name]["attribution"] = repr(e)
        json.dump(res, open(a.out, "w"), indent=1, default=float)
        w = res[name]["wear_exact"]
        print(name, Bf.mode, "->", Bw.mode, json.dumps({k: w.get(k) for k in METRICS + ("honest", "gap_recomputed")}, default=float),
              json.dumps(w["per_pose"]), f"{res[name]['secs']} s", flush=True)


def _kit(arg):
    i, p, nb = arg; os.environ.setdefault("OMP_NUM_THREADS", "1")
    M = model()
    if "B" not in _W: _W["B"] = make_bench(*nb, exact=False)
    t = time.time()
    try:
        _, r = M.evaluate(_W["B"], dict(p))
        return i, dict({k: r.get(k) for k in METRICS + ("honest", "hub_F")}, mode=_W["B"].mode, secs=round(time.time() - t, 1))
    except Exception as e:                                                    # noqa: BLE001
        return i, dict(error=repr(e)[:300], gap=None, secs=round(time.time() - t, 1))


def cmd_kitparity(a):
    rows = json.load(open(a.rows)); rows = rows["rows"] if isinstance(rows, dict) else rows
    nb = tuple(int(x) for x in a.bench.split(",")); out = []; t = time.time()
    with mp.get_context("spawn").Pool(a.procs) as pool:
        for i, r in pool.imap_unordered(_kit, [(i, rw["params"], nb) for i, rw in enumerate(rows)]):
            g = rows[i]; d = {k: (None if r.get(k) is None or g.get(k) is None else round(abs(float(r[k]) - float(g[k])), 4)) for k in METRICS}
            out.append(dict(i=i, params=g["params"], gpu={k: g.get(k) for k in METRICS}, kit=r, absdiff=d))
            json.dump(dict(bench=list(nb), rows=out), open(a.out, "w"), indent=1, default=float)
            print(i, "gpu", g.get("gap"), "kit", r.get("gap"), r.get("mode"), r.get("secs"), "s", flush=True)
    md = {k: max([o["absdiff"][k] for o in out if o["absdiff"][k] is not None] or [None]) for k in METRICS}
    n1 = sum(1 for o in out if o["absdiff"]["gap"] is None or o["absdiff"]["gap"] > 1.0)
    S = dict(n=len(out), max_abs_diff=md, n_gap_diff_gt_1=n1, secs=round(time.time() - t, 1), bench=list(nb))
    json.dump(dict(summary=S, rows=out), open(a.out, "w"), indent=1, default=float); print(json.dumps(S))


def cmd_pick(a):
    M = model(); rng = np.random.default_rng(a.seed)
    base = dict(az=109.3565, el=65.94, a1=36.7226, a2=69.0575, wd=85.7423, wa=-16.1921, sigma=-1, inv2=0, inv3=1, q=0.978, end_extra=1.784)
    SC = dict(az=9.0, el=6.0, a1=6.0, a2=6.0, wd=6.0, wa=9.0, q=0.04, end_extra=2.0); out = []
    while len(out) < a.n // 2:
        p = dict(base)
        for k, s in SC.items(): p[k] = float(base[k] + s * rng.standard_normal())
        p["q"] = float(min(1.0, max(0.8, p["q"]))); p["end_extra"] = float(min(8.0, max(0.0, p["end_extra"])))
        p["inv2"] = int(len(out) % 2); p["inv3"] = int((len(out) // 2) % 2); p["sigma"] = -1 if rng.random() < 0.8 else 1
        if M.seat_ok(p["az"], p["el"]): out.append(dict(tag=f"basin{len(out)}", params=p))
    while len(out) < a.n:
        p = {k: float(rng.uniform(*M.BOUNDS[k])) for k in ("az", "el", "a1", "a2", "wd", "wa", "q", "end_extra")}
        p.update(sigma=int(rng.choice([-1, 1])), inv2=int(rng.random() < 0.5), inv3=int(rng.random() < 0.5))
        if M.seat_ok(p["az"], p["el"]): out.append(dict(tag=f"uni{len(out)}", params=p))
    json.dump(out, open(a.out, "w"), indent=1); print(len(out), "configs ->", a.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("frozen"); s.add_argument("params"); s.add_argument("out"); s.add_argument("--fits", default="fit110,fit60")
    s = sp.add_parser("kitparity"); s.add_argument("rows"); s.add_argument("out"); s.add_argument("--bench", default="110,360"); s.add_argument("--procs", type=int, default=4)
    s = sp.add_parser("pick"); s.add_argument("out"); s.add_argument("--n", type=int, default=20); s.add_argument("--seed", type=int, default=20261016)
    a = ap.parse_args()
    dict(frozen=cmd_frozen, kitparity=cmd_kitparity, pick=cmd_pick)[a.cmd](a)
