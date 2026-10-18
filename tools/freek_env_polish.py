#!/usr/bin/env python3
"""FINAL POLISH OF freek-oracle-route-knuckle-4r cell B (round-104 winner, VERIFIED 16.20 frozen exact Bench(110,360), held
21.89, the model's one fold reading) ON AN ENVELOPE SEARCH BENCH, run LOCALLY (the CPU farm is closed: CLAUDE.md (7)).

The verifier's harness is imported unchanged (docs/concepts/verify/freek-oracle-route-knuckle-4r-verify.py: VDesign with
OWN = False = the claim's stop reading q3 = cuff vs link 2; J3's own angle q3' = q3 + phi is reported for every config),
and the continuity flood reads ONE fold reading, the verified one (kin_nodes_model: state 2's moving chain is J1-K-J2).

Search bench 'envh' (stated as a measurement choice, docs/research/freek-oracle-route-knuckle-4r_final_polish.md):
the fast cache of tools/env_bench.py 'env' lives on the closed farm volume, and a full local rebuild (530 poses at ~12 s
each on the shared box) does not fit the 120-min box. envh = Bench(60,160)'s 60 clip frames (cached locally) + the
FIRST stride-2 pass of env's 420 fresh workspace poses (env positions 110, 112, ..., 528; draws are listed stratum by
stratum, so a stride keeps the strata), built locally pose by pose (.cache/envposes/env). The held-out split stays held
out (asserted: no envh pose is a held-out pose; env's draws keep >= 2 deg from every held-out pose).

Objective of a free-parameter set p (lower is better):
  P = k33 nominal (cand_k33.json) + q3max 86 + p; stops smhi / smlo >= 5.0; stop B a1max <= bk1 + bk2 - 5.51 (the K-dyad repair)
  P' = env_polish.priced(KR, P): J2 stops +0.5 (read at CB_FOLD_MARGIN 5.5), K stop B at the margin-5 rule cut
  a = fit P' on envh FAST, in-sample, continuity (the 1432-grid flood with the one reading + every fresh pose joined by a
      2-deg slerp edge to one of its 6 nearest connected grid nodes, same law) -> near-touch gap (metal < 1 mm = contact)
  b = fit P' on Bench(60,160) FAST (the verified protocol's fit), worn FROZEN on envh FAST, same continuity -> near-touch gap
  obj = (a + b) / 2 + claim-fit guard max(0, g60_near - a - 3) + depth guard 0.1 x max(0, depth_a - depth_a(verified))

    CB_FOLD_MARGIN=5.5 python3 tools/freek_env_polish.py envh-make            assemble the envh cache from the built poses
    CB_FOLD_MARGIN=5.5 python3 tools/freek_env_polish.py table                distribution table (grid / held / Bench / env / envh)
    CB_FOLD_MARGIN=5.5 python3 tools/freek_env_polish.py score OUT.json '[{"tag":..,"params":{..}}]' [--jobs 1]
    CB_FOLD_MARGIN=5.5 python3 tools/freek_env_polish.py cma --label L --out O.json [--popsize 8 --jobs 2 --budget-s 1800]
    python3 tools/freek_env_polish.py gate O.json | picks O.json --out DIR
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 python3 tools/freek_env_polish.py claim <env|fit60> <held|bench|envh> <VER|params.json> OUT.json
"""
import copy, importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("CB_FOLD_MARGIN", "5.5")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import env_bench as EB                                       # noqa: E402
EB.install()
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402
import env_polish as EP                                      # noqa: E402

ID = "freek-oracle-route-knuckle-4r"
_argv = sys.argv; sys.argv = [_argv[0]]
_sp = importlib.util.spec_from_file_location("freek_v_for_envpolish", os.path.join(REPO, "docs", "concepts", "verify", ID + "-verify.py"))
V = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(V); sys.argv = _argv
FO, KR, RM, PK = V.FO, V.KR, V.RM, V.PK
V.VDesign.OWN = False                                        # the claim's (verified) stop reading
KIN_FAMILY = RM.kin_nodes                                    # the shared harness's family reading (kept for the side report)
RM.kin_nodes = V.kin_nodes_model                             # ONE fold reading = the verified one (flood uses the module global)

OUTD = os.path.join(REPO, "docs", "research", "freek_env_polish")
POSED = os.path.join(REPO, ".cache", "envposes", "env")
ENVH_JSON = os.path.join(OUTD, "envh.json")
NOM = dict(json.load(open(os.path.join(REPO, "docs", "concepts", "verify", "skinnormal-shortk-knuckle-4r", "cand_k33.json"))), q3max=86.0)
KMARG = 5.5
FREE = {                                                     # (CMA step, lo, hi, note); J1 seat, knee geometry, stack, window, hubs FIXED
    "q3max": (3.0, 60.0, 120.0, "J3 dowel stop (model q3; own angle q3' = q3 + phi)"),
    "smhi": (1.0, 5.0, 20.0, "stretched J2 stop, th-margin metric (>= 5 = the user's floor; priced +0.5)"),
    "smlo": (1.0, 5.0, 20.0, "folded J2 stop (>= 5; priced +0.5)"),
    "a1max": (3.0, 40.0, 100.0, "K stop B (largest effective J1-J2 arc; capped at bk1 + bk2 - 5.51)"),
    "bk1": (3.0, 15.0, 70.0, "knuckle K -> J1 arc"),
    "bk2": (3.0, 15.0, 80.0, "knuckle K -> J2 arc"),
    "az2": (6.0, -40.0, 60.0, "J2 home seat azimuth"),
    "el2": (4.0, 20.0, 75.0, "J2 home seat elevation"),
    "wd": (4.0, 50.0, 110.0, "J3 seat on the arm, from the humerus axis"),
    "wa": (4.0, -45.0, 20.0, "J3 seat azimuth around the humerus"),
    "b3": (0.08, -0.3, 1.0, "J3 axis tilt toward the skin normal"),
}
FIXED_NOTE = ("fixed: J1 seat az1 / el1 (the verified seat sits in the user's J1 region: back of the shoulder + acromion top; no seat "
              "check tool exists, so it is not moved), the two-pin knee lE / lc / phiE / phib / stk and its window ang_min (built rules: "
              "MR63ZZ pairs, physical knee stop), O20 hubs rad1-3 = 10, route rA 0 (great circle), every model rule")


# ---------------------------------------------------------------------------------------------------------------------
# envh: Bench(60,160)'s clip frames + a stride pass of env's fresh workspace poses (local fast cache)
def _b60(): return RM.PV.fast_bench(60, 160)


def envh_make(ws_pos=None):
    B60 = _b60(); assert B60.mode == "fast"
    cl = [i for i, k in enumerate(B60.kind) if k == "clip"]
    Benv = EB.bench("env", exact=True)
    if ws_pos is None:
        ws_pos = [j for j in range(110, len(Benv.idx), 2) if os.path.exists(os.path.join(POSED, f"g{j:04d}.npy"))]
    idx = np.r_[np.asarray(B60.idx)[cl], np.asarray(Benv.idx)[ws_pos]]; key = "envh-" + CB._key(idx)
    d = os.path.join(CB.CACHE, key); os.makedirs(d, exist_ok=True); n = B60.grid.shape[1]; N = len(idx)
    g = np.lib.format.open_memmap(os.path.join(d, "grid.tmp.npy"), mode="w+", dtype=np.int8, shape=(N, n, n, n))
    for k, i in enumerate(cl): g[k] = B60.grid[i]
    for k, j in enumerate(ws_pos): g[len(cl) + k] = np.load(os.path.join(POSED, f"g{j:04d}.npy"))
    g.flush(); del g
    Vs = [np.asarray(B60._V[i], np.float32) for i in cl] + [np.load(os.path.join(POSED, f"v{j:04d}.npy")).astype(np.float32) for j in ws_pos]
    np.save(os.path.join(d, "skins.npy"), np.stack(Vs)); os.replace(os.path.join(d, "grid.tmp.npy"), os.path.join(d, "grid.npy"))
    meta = dict(bench="envh", poses=N, clips=len(cl), ws=len(ws_pos), h=CB.H_GRID, half=CB.HALF, q=CB.Q, env_ws_positions=ws_pos,
                created=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), built="local, tools/freek_env_polish.py envh-make (clips: Bench(60,160) cache)")
    json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
    os.makedirs(OUTD, exist_ok=True); json.dump(dict(key=key, clips_from="Bench(60,160)", env_ws_positions=ws_pos, n=N), open(ENVH_JSON, "w"), indent=1)
    print("envh", key, N, "poses:", len(cl), "clips +", len(ws_pos), "ws", flush=True)
    return key


_BH = {}


def bench_envh(exact=False):
    """the envh Bench (fast unless exact): kind 'clip' for the 60 Bench(60,160) frames, 'ws' for the fresh poses"""
    if not exact and "B" in _BH: return _BH["B"]
    E = json.load(open(ENVH_JSON)); B60 = _b60(); cl = [i for i, k in enumerate(B60.kind) if k == "clip"]
    Benv = EB.bench("env", exact=True); ws_pos = E["env_ws_positions"]
    idx = np.r_[np.asarray(B60.idx)[cl], np.asarray(Benv.idx)[ws_pos]]; key = "envh-" + CB._key(idx); assert key == E["key"]
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]
    old = os.environ.get("CB_EXACT"); os.environ["CB_EXACT"] = "1"; os.environ["CB_QUIET_EXACT"] = "1"
    try: B = CB.Bench(20, 20)
    finally:
        if old is None: os.environ.pop("CB_EXACT")
        else: os.environ["CB_EXACT"] = old
    B.idx = idx; B.kind = ["clip"] * len(cl) + ["ws"] * len(ws_pos); B.clip = [str(names[c]) for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in Z["POSE"][idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.grid = None; B._V = None; B.mode = "exact"; B.key = key
    d = os.path.join(CB.CACHE, key)
    if not exact:
        B.meta = json.load(open(os.path.join(d, "meta.json"))); B.grid = np.load(os.path.join(d, "grid.npy"), mmap_mode="r")
        B._V = np.load(os.path.join(d, "skins.npy"), mmap_mode="r"); B.mode = "fast"
    hidx, _ = EB.held_idx(); assert not (set(idx.tolist()) & set(hidx.tolist())), "a held-out pose in envh"
    if not exact: _BH["B"] = B
    return B


def table(outp=None):
    rows = EB.table(None); Z = CB._poses_all(); B = bench_envh(exact=True); ii = np.asarray(B.idx)[[i for i, k in enumerate(B.kind) if k == "ws"]]
    P = Z["POSE"][ii].astype(float); ax = np.abs(P[:, 2]); el = P[:, 1]; pl = P[:, 0]; reg = np.array([EB.region(p) for p in P])
    r = dict(n=len(ii), ax_ge150=np.mean(ax >= 150), ax_0_45=np.mean(ax < 45), ax_45_90=np.mean((ax >= 45) & (ax < 90)), ax_90_150=np.mean((ax >= 90) & (ax < 150)),
             ax_m90_m45=np.mean((P[:, 2] >= -90) & (P[:, 2] < -45)), overhead=np.mean(reg == "overhead"), across=np.mean(reg == "across"),
             behind=np.mean(reg == "behind"), el_lt45=np.mean(el < 45), el_45_90=np.mean((el >= 45) & (el < 90)), el_90_140=np.mean((el >= 90) & (el < 140)),
             pl_lt0=np.mean(pl < 0), pl_0_60=np.mean((pl >= 0) & (pl < 60)), pl_60_100=np.mean((pl >= 60) & (pl < 100)), pl_ge100=np.mean(pl >= 100),
             mean_axial=float(P[:, 2].mean()), mean_elev=float(el.mean()), mean_plane=float(pl.mean()))
    rows["envh_ws"] = {k: (round(float(v), 4) if isinstance(v, (float, np.floating)) else v) for k, v in r.items()}
    cols = ["n", "ax_ge150", "ax_m90_m45", "overhead", "across", "behind", "el_lt45", "el_90_140", "pl_ge100", "mean_axial"]
    print("| set | " + " | ".join(cols) + " |"); print("|---" * (len(cols) + 1) + "|")
    for nm, rr in rows.items(): print(f"| {nm} | " + " | ".join(str(rr.get(c)) for c in cols) + " |")
    if outp: json.dump(rows, open(outp, "w"), indent=1)
    return rows


# ---------------------------------------------------------------------------------------------------------------------
# objective
def full(p):
    P = dict(NOM); P.update({k: float(v) for k, v in (p or {}).items()})
    P["smhi"] = max(5.0, float(P["smhi"])); P["smlo"] = max(5.0, float(P["smlo"]))
    cap = float(P["bk1"]) + float(P["bk2"]) - KMARG - 0.01
    if float(P["a1max"]) > cap: P["a1max"] = cap
    return P


def priced(P):
    if os.environ.get("FP_NOPRICE") == "1": return dict(P), dict(why="unpriced")
    return EP.priced(KR, P)


def _key3(p): return (float(p["plane"]), float(p["elev"]), float(p["axial"]))


def conn_keys(D, p, B):
    """the verified one-reading flood on the 1432-pose grid + the fresh poses of B joined by edges -> set of (plane, elev, axial)"""
    Z, Wg, POSE, HG = RM.ws_grid(); R_tol = float(p["R_tol"]); _ = D.ik(HG[:2])
    okn, qq, sgn, st, own = RM.kin_nodes(D, HG, R_tol); seeds = okn & (POSE[:, 1] == 0) & (st == 0)
    cn, stats = RM.flood(POSE, HG, okn, seeds, D, R_tol)
    keys = {(float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])) for i in np.nonzero(cn)[0]}
    n0 = EB._ZX["n0"]; ii = [i for i in range(len(B.idx)) if B.kind[i] == "ws" and int(B.idx[i]) >= n0]; fresh = None
    if ii:
        HGx = CB._poses_all()["HG"][np.asarray(B.idx)[ii]].astype(float)
        c = EP.connect_extra(lambda Q: RM.kin_nodes(D, Q, R_tol), HGx, HG, cn, branch0=set(sgn[seeds].tolist()))
        keys |= {_key3(B.poses[i]) for i, v in zip(ii, c) if v}; fresh = dict(poses=len(ii), connected=int(c.sum()))
    return keys, dict(nodes=int(okn.sum()), connected=int(cn.sum()), islands=int((okn & ~cn).sum()), fresh=fresh,
                      refused=dict(rule=stats["refused_rule"], jump=stats["refused_jump"], branch=stats["refused_branch"]))


def score(M, B, keys):
    res0 = list(B.res); tk = RM.taken_list(B); drop = []
    if keys is not None:
        for i in tk:
            if B.kind[i] == "ws" and _key3(B.poses[i]) not in keys: B.res[i] = None; drop.append(i)
    rc = B.report(); nt = RM.near_touch(M, B)
    mins = [(i, float(np.min(B.res[i]))) for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i])]
    cp = [m for _, m in mins if m < 0]; tk2 = RM.taken_list(B); st = np.asarray(getattr(M, "kstate", np.zeros(len(B.idx))))
    el = np.array([p["elev"] for p in B.poses])
    out = dict(gap=rc["gap"], near=nt["gap_near1"], reach=rc["reach"], follow=rc["follow"], inband14=rc["inband14"], inband10=rc["inband10"],
               contact=rc["contact"], contact_poses=len(cp), depth=round(-float(sum(cp)), 2), near1_poses=nt["near1_poses"], min_mm=nt["min_mm"],
               ws_taken=sum(1 for i in tk2 if B.kind[i] == "ws"), dropped=len(drop), stop_engaged=int(sum(1 for i in tk2 if st[i] == 2)),
               overhead=[int(sum(1 for i in tk2 if B.kind[i] == "ws" and el[i] >= 140)), int(sum(1 for i in range(len(el)) if B.kind[i] == "ws" and el[i] >= 140))])
    B.res = res0
    return out


def obj_of(p, Bh, B60):
    P = full(p); Pp, pinfo = priced(P); out = dict(price={k: pinfo.get(k) for k in ("a1max_priced", "dK_cut", "why") if k in pinfo})
    t0 = time.time()
    M1 = FO.KModel(Bh, dict(Pp))
    if not M1.kin_ok.any(): out.update(obj=400.0, nothing_closes=True); return out
    M1.run(); ka, ca = conn_keys(M1.D, M1.p, Bh); a = score(M1, Bh, ka); out["a"] = a; out["conn_a"] = ca
    Mk, fit, M6, _ = RM.freeze(B60, Bh, dict(Pp), FO.KModel)
    g60 = score(M6, B60, None); out["g60"] = g60
    Mk.run(); kb, cb = conn_keys(Mk.D, Mk.p, Bh); b = score(Mk, Bh, kb); out["b"] = b; out["conn_b"] = cb
    dref = os.environ.get("FP_DEPTH_REF"); dpen = 0.1 * max(0.0, a["depth"] - float(dref)) if dref else 0.0
    out["claim_pen"] = round(max(0.0, g60["near"] - a["near"] - 3.0), 3); out["depth_pen"] = round(dpen, 3)
    out["obj"] = round(0.5 * (a["near"] + b["near"]) + out["claim_pen"] + dpen, 3); out["secs"] = round(time.time() - t0, 1)
    return out


_W = {}


def _init(plname=None):
    os.environ.setdefault("OMP_NUM_THREADS", "1"); _W["Bh"] = bench_envh(); _W["B60"] = _b60()
    assert _W["Bh"].mode == "fast" and _W["B60"].mode == "fast"
    assert KIT.FOLD_MARGIN == 5.5, "run at CB_FOLD_MARGIN=5.5 (the verified priced reading)"


def _eval(arg):
    import traceback
    tag, p = arg; t0 = time.time()
    try:
        r = obj_of(p, _W["Bh"], _W["B60"]); return dict(tag=tag, params=p, obj=r["obj"], xfit=r, secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-1500:], secs=round(time.time() - t0, 1))


class Plugin:
    FREE = FREE

    def base(self): return dict(NOM)


def run_cma(argv):
    import argparse
    import crossfit_polish as X
    X.PLUGINS["freek_env"] = Plugin; X._init = _init; X._eval = _eval
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--plugin", default="freek_env")
    ap.add_argument("--x0", default="{}"); ap.add_argument("--fixed", default="")
    ap.add_argument("--label", required=True); ap.add_argument("--out", required=True); ap.add_argument("--state", default="")
    ap.add_argument("--state-out", default=""); ap.add_argument("--sigma", type=float, default=0.5)
    ap.add_argument("--popsize", type=int, default=8); ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--budget-s", type=float, default=1800); ap.add_argument("--max-gen", type=int, default=400)
    ap.add_argument("--max-evals", type=int, default=400); ap.add_argument("--patience", type=int, default=10)
    ap.add_argument("--seed", type=int, default=1)
    X.cma(ap.parse_args(argv))


def score_list(outp, items, jobs=1):
    import multiprocessing as mp
    if jobs > 1:
        pool = mp.get_context("fork").Pool(jobs, initializer=_init); res = pool.map(_eval, [(it.get("tag", f"s{i}"), it["params"]) for i, it in enumerate(items)]); pool.close()
    else:
        _init(); res = [_eval((it.get("tag", f"s{i}"), it["params"])) for i, it in enumerate(items)]
    json.dump(res, open(outp, "w"), indent=1, default=float)
    for r in res: print(json.dumps({k: r.get(k) for k in ("tag", "obj", "secs", "error")}), json.dumps({k: (r.get("xfit") or {}).get(k) for k in ("a", "b", "g60", "price")})[:1500], flush=True)


# ---------------------------------------------------------------------------------------------------------------------
# convergence gate + picks
def load_rows(files):
    rows = []
    for f in files:
        for r in json.load(open(f)):
            r["_file"] = os.path.basename(f); rows.append(r)
    return rows


def gate(rows):
    ok = [r for r in rows if not r.get("error") and r["obj"] < 100]; n = len(rows)
    if n < 6: return dict(n=n, passes=False, why="too few tries")
    best_at = lambda m: min([r["obj"] for r in rows[:m] if not r.get("error")] or [400.0])
    b_all = best_at(n); g_half = best_at(n // 2) - b_all; g_third = best_at(2 * n // 3) - b_all
    top = sorted(r["obj"] for r in ok)[:5]; spread = top[-1] - top[0] if len(top) == 5 else None
    passes = g_half < 1.0 and g_third < 0.5 and spread is not None and spread <= 3.0
    return dict(n=n, ok=len(ok), best=b_all, gain_second_half=round(g_half, 3), gain_last_third=round(g_third, 3), top5=top, top5_spread=None if spread is None else round(spread, 3),
                passes=passes, x0=rows[0]["obj"] if rows else None)


def picks(rows, outdir, n=3, dist=1.0):
    ok = sorted([r for r in rows if not r.get("error") and r["obj"] < 100], key=lambda r: r["obj"]); chosen = []
    for r in ok:
        if r["tag"].endswith("-x0"): continue
        if all(max(abs(float(r["params"].get(k, NOM[k])) - float(c["params"].get(k, NOM[k]))) / FREE[k][0] for k in FREE) >= dist for c in chosen):
            chosen.append(r)
        if len(chosen) == n: break
    os.makedirs(outdir, exist_ok=True); out = []
    for k, r in enumerate(chosen, 1):
        P = full(r["params"]); json.dump(P, open(os.path.join(outdir, f"pick{k}.json"), "w"), indent=1)
        x = r["xfit"]; out.append(dict(pick=k, tag=r["tag"], obj=r["obj"], a_near=x["a"]["near"], a_gap=x["a"]["gap"], b_near=x["b"]["near"], b_gap=x["b"]["gap"],
                                       g60_near=x["g60"]["near"], depth_a=x["a"]["depth"], contact_a=x["a"]["contact_poses"],
                                       params={k2: r["params"].get(k2) for k2 in FREE}))
    json.dump(dict(VER=dict(params={k: NOM[k] for k in FREE}), picks=out), open(os.path.join(outdir, "picks.json"), "w"), indent=1)
    json.dump(dict(NOM), open(os.path.join(outdir, "VER.json"), "w"), indent=1)
    for o in out: print(json.dumps(o))
    return out


# ---------------------------------------------------------------------------------------------------------------------
# claim: fit FAST (envh or Bench(60,160)) -> wear EXACT (held out / Bench(110,360) / envh), frozen, priced, one reading
def margins(D, Q, tk):
    """fold margin in th over the taken poses: one reading (each state's moving chain, the audit's tool) + the family reading"""
    q, ok, X1, X2, X3, s = D.ik(Q); st = np.asarray(D._state).copy(); m3e = np.asarray(D._m3e, float); X1b = D._X1b[0]
    u1, u2, u3 = D.u; uK = D.uK; U1 = np.broadcast_to(u1, (len(Q), 3))
    jK = np.einsum("nij,j->ni", X1[0], uK); j2 = np.einsum("nij,j->ni", X1b, u2); j3 = np.einsum("nij,j->ni", X2[0], u3)
    ang, dm = RM.ang, RM.dmargin
    th = ang(U1, j3); a1e = ang(U1, j2); a2e = ang(j2, j3); b1 = ang(U1, jK); cK3 = ang(jK, j3); cK2 = ang(jK, j2)
    msub = dm(th, b1, cK3); kdy = dm(a1e, b1, cK2); dy = dm(th, a1e, a2e)
    one = np.where(st == 0, m3e, np.where(st == 1, np.minimum(msub, m3e), np.minimum(kdy, m3e)))
    fam = np.where(st != 0, np.minimum(msub, dy), dm(th, D.a1, D.a2))
    tk = np.asarray(tk, int)
    def mn(a): return round(float(a[tk].min()), 2) if len(tk) else None
    return dict(one_reading_min=mn(one), one_lt5=int((one[tk] < 5.0 - 1e-6).sum()), family_min=mn(fam), family_lt5=int((fam[tk] < 5.0 - 1e-6).sum()),
                state_counts={str(k): int((st[tk] == k).sum()) for k in (0, 1, 2)})


def stop_refusal(Mk, W, res_stop):
    """poses the J3 dowel refuses (no crossing on [|dK|, stop B]) and, worn with the SAME frozen shape without the dowel (the
    kit), whether they are contacts: the side reading counts those as contacts (audit proposal B)"""
    D = Mk.D; Q = Mk.Q
    q, ok, X1, X2, X3, s = KR.KRDesign._ik_phys(D, Q); js = D.j3stop2(Q, q, ok, s)
    refused = sorted(i for i, v in js.items() if v is None)
    if not refused: return dict(refused=0, kit_contacts=0, rows=[]), None
    W2 = copy.copy(W); W2.idx = np.asarray(W.idx)[refused]; W2.kind = [W.kind[i] for i in refused]; W2.clip = [W.clip[i] for i in refused]
    W2.poses = [W.poses[i] for i in refused]; W2.res = [None] * len(refused); W2._skin = {}; W2._ex = {}; W2._frames = {}
    if getattr(W, "grid", None) is not None: W2.grid = W.grid[refused]; W2._V = W._V[refused] if W._V is not None else None
    P2 = dict(Mk.p); P2.pop("q3max", None)
    Mkit = type(Mk)(W2, P2); Mkit.run()
    rows = []
    for k, i in enumerate(refused):
        r = W2.res[k]; m = None if r is None or not len(r) else float(min(np.min(r), Mkit.cmin.get(k, 1e9)))
        rows.append(dict(i=int(i), kind=W.kind[i], plane=W.poses[i]["plane"], elev=W.poses[i]["elev"], axial=W.poses[i]["axial"], kit_min_mm=None if m is None else round(m, 2)))
    kc = [r for r in rows if r["kit_min_mm"] is not None and r["kit_min_mm"] < 0]
    res1 = list(res_stop)
    for r in kc: res1[r["i"]] = np.array([r["kit_min_mm"]])
    return dict(refused=len(refused), kit_contacts=len(kc), rows=rows), res1


def claim(fit, wear, which, outp):
    import alignment_paired as AP
    t0 = time.time()
    P = dict(NOM) if which == "VER" else full(json.load(open(which)))
    Pp, pinfo = priced(P)
    FIT = bench_envh() if fit == "env" else _b60(); assert FIT.mode == "fast"
    W = RM.PV.held_bench() if wear == "held" else (bench_envh(exact=True) if wear == "envh" else CB.Bench(n_clip=110, n_ws=360))
    if os.environ.get("FP_SMOKE"):
        nn = int(os.environ["FP_SMOKE"]); sel = [i for i, k in enumerate(W.kind) if k == "clip"][:nn] + [i for i, k in enumerate(W.kind) if k == "ws"][::40][:nn]
        W.idx = np.asarray(W.idx)[sel]; W.kind = [W.kind[i] for i in sel]; W.clip = [W.clip[i] for i in sel]; W.poses = [W.poses[i] for i in sel]; W.res = [None] * len(sel)
    assert W.mode == "exact", f"wear bench not exact: {W.mode}"
    Mk, fitr, M1, _ = RM.freeze(FIT, W, dict(Pp), FO.KModel); rk = Mk.run(); nt = RM.near_touch(Mk, W); tk = RM.taken_list(W)
    static = dict({k: rk[k] for k in FO.KEYS}, near=nt["gap_near1"], near1_poses=nt["near1_poses"], min_mm=nt["min_mm"])
    poses = AP._dump_bench(Mk, W); gp = AP.gap_parts(poses)
    depth = round(-sum(p["min_mm"] for p in poses if p["contact"]), 2)
    oh = [int(sum(1 for i in tk if W.kind[i] == "ws" and W.poses[i]["elev"] >= 140)), int(sum(1 for i in range(len(W.idx)) if W.kind[i] == "ws" and W.poses[i]["elev"] >= 140))]
    stop = V.stop_report(Mk, W)
    mg = margins(Mk.D, Mk.Q, tk)
    res_stop = list(W.res)
    conn = V.flood_connected(Mk, W, tk)                      # RM.kin_nodes = the one reading
    ck = set(); dropped = set(conn["dropped_idx"])
    side, res1 = stop_refusal(Mk, W, res_stop)
    if res1 is not None:
        r0 = list(W.res); W.res = res1; rs = W.report(); W.res = r0; side["gap_refusals_as_contacts"] = rs["gap"]
    else: side["gap_refusals_as_contacts"] = static["gap"]
    out = dict(id=ID, fit=fit, wear=wear, which=which if which == "VER" else os.path.relpath(which, REPO), n=len(W.idx), fold_margin=KIT.FOLD_MARGIN,
               nominal={k: P[k] for k in FREE}, priced={k: Pp[k] for k in FREE}, price=pinfo, fit_report=fitr, static=static, recomputed=gp,
               contact_poses=gp["contact_poses"], contact_depth_mm=depth, overhead140_ws=oh, connected=conn, margins=mg, j3stop=stop,
               stop_refusal=side, gap=conn["gap"], near=conn["near"], secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    json.dump(dict(id=ID, fit=fit, wear=wear, which=out["which"], poses=poses, recomputed=gp), open(outp.replace(".json", "_perpose.json"), "w"), default=float)
    print(json.dumps({k: out[k] for k in ("fit", "wear", "which", "gap", "near", "contact_poses", "contact_depth_mm", "overhead140_ws", "margins", "stop_refusal", "secs")}, default=float)[:2500], flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: raise SystemExit(__doc__)
    if a[0] == "envh-make": envh_make()
    elif a[0] == "table": table(os.path.join(OUTD, "env_table.json"))
    elif a[0] == "score": score_list(a[1], json.loads(a[2]) if not os.path.exists(a[2]) else json.load(open(a[2])), int(a[a.index("--jobs") + 1]) if "--jobs" in a else 1)
    elif a[0] == "cma": run_cma(a)
    elif a[0] == "gate": print(json.dumps(gate(load_rows(a[1:]))))
    elif a[0] == "picks": picks(load_rows([x for x in a[1:] if x.endswith(".json") and x != a[a.index("--out") + 1]]), a[a.index("--out") + 1])
    elif a[0] == "claim": claim(a[1], a[2], a[3], a[4])
    else: raise SystemExit(__doc__)
