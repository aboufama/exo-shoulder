#!/usr/bin/env python3
"""FINAL POLISH OF sidecar-longdyad-knuckle-3r ON THE ENVELOPE BENCH (tools/env_bench.py 'env') + the claim wrapper that
wears a config through the verifier's own harness (docs/concepts/verify/sidecar-longdyad-knuckle-3r.py, imported unchanged,
benches swapped) with built-stop pricing.

CLAUDE.md rules carried: search on a representative envelope sample, claim on the held-out set; near-touch objective
(metal < 1 mm = contact); continuity (the verifier's full-grid flood fill, + every fresh env pose joined to the connected
grid by a 2-deg slerp edge to one of its 6 nearest connected grid nodes, same law); the 5-deg margin in the th metric with
stops as variables >= 5.0 and priced at +0.5; O20 (the model's hubs, concept_kit O20_ONLY); the held-out split stays held
out (env / envsel never touch it: tools/env_bench.py asserts).

PRICING (the judge's convention for minarc BDp, docs/research/minarc_final_polish.md): a J2 dowel is drawn s +0.5 / -0 deg
of J1-J3 margin; its worst built case (+0.5, the reach-losing side) is read with the all-state rule at 5.5 (CB_FOLD_MARGIN
5.5). In this family the J2 dowels are the FOLDED dowel at th_lo = |a1 - a2| + smlo (K on stop A) and the STRETCHED dowel at
the end of the slaved law's prefix, which the kit rule ends where m3e / msub reach the margin: so priced = smlo + 0.5 and
the whole reading at CB_FOLD_MARGIN 5.5. smhi is the lobe's onset (a cam feature, not a dowel): bounded >= 5.0, unpriced
(the 5.5 reading clamps it >= 5.5 anyway). K's stop B (a1max) is read at the K dyad's margin at the same 5.5: a1max' =
min(a1max, bk1 + bk2 - 5.5) (the model's k_ok refuses a1max > bk1 + bk2 - margin; the row measured stop B never binds:
every cell identical at a1max -3). The drive-range dowel (dK_lim, rod vs hub 2) sits beyond every taken K opening:
reported, not priced.
ENVP_NOPRICE=1 (with CB_FOLD_MARGIN=5) = the verified reading (nominal stops, margin 5).

Objective of a free-parameter set p (lower is better):
  P = BEST (the verified config) + p, stops smhi / smlo >= 5.0, knee window ang_min >= the verified 26.8823 (no widening of
  the knee window beyond what the verifier passed), law 'lin', gam 0 (the verified phase; the crank phase walked back)
  P' = priced(P);  fit P' on env FAST (in-sample; the cross-fit study measured in-fold = out-of-fold), knock out the
  continuity-unconnected workspace poses, the model's audit -> env near-touch gap (1 mm)            -> obj
  + the claim-fit guard: P' fitted on Bench(60,160) FAST (the verified protocol's fit), in-sample near-touch g60:
    obj += max(0, g60 - env_near1 - 3)
  + the 2-mm SHELL GUARD (user rulings 2026-10-16 ~21:05: report 2 mm on every claim; a polished pick replaces the verified
    config only if it also beats it at 2 mm): obj += max(0, env_near2 - REF_NEAR2), REF_NEAR2 = the verified config's
    in-sample env 2-mm number (computed once per CMA job before the pool forks): points bought by moving metal into the
    1-2 mm shell are paid back one for one
  + 100 if the model's report is dishonest (RSSR does not close, crest leaves the skirt) or a taken pose's own-state th
    margin is < the reading's margin (the kit rule should make this impossible; it is checked, not assumed)
  logged, not optimised: env plain gap; the env-fitted shape worn FROZEN on envsel (independent draw) -> sel_near1 / sel_near2
  / sel_gap = the pick-selection numbers.

    CB_FOLD_MARGIN=5.5 python3 tools/sidecar_env_polish.py cma --x0 '{}' --label L --out O.json [--sigma 0.4 --popsize 8 --jobs 2 ...]
    CB_FOLD_MARGIN=5.5 python3 tools/sidecar_env_polish.py score OUT.json '[{"tag":..,"params":{..}}]' [--jobs 2]
    python3 tools/sidecar_env_polish.py best O1.json [O2.json ..] [--k 15]
    python3 tools/sidecar_env_polish.py gate O1.json [O2.json ..]        the convergence gate per run and combined
  re-score (step 2): fit env FAST -> wear env EXACT (frozen), continuity with fresh-pose edges:
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 python3 tools/sidecar_env_polish.py rescore <BEST|params.json> OUT.json
  claim (the verifier's harness frozen_wear, unchanged, with the fit bench swapped for env when asked):
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 python3 tools/sidecar_env_polish.py claim <fit60|env> <bench|held> <BEST|params.json> OUT.json
"""
import importlib.util, json, math, os, sys, time, traceback
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import env_bench as EB                                       # noqa: E402
EB.install()                                                 # fresh poses appended BEFORE any model loads poses
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

HERE_V = os.path.join(REPO, "docs", "concepts", "verify")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


V = _load("sidecar_v_for_envpolish", os.path.join(HERE_V, "sidecar-longdyad-knuckle-3r.py"))    # the verifier's harness (loads the claim's model)
SC, PK, S = V.SC, V.PK, V.S
BEST = dict(V.BEST)
ANG_MIN_LO = 26.8823
CLAIM_TOL = 3.0
FROZEN_ATTRS = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info")
# free parameters: (CMA scale, lo, hi). Ranges = the model's own clamps where it has them; stops >= 5.0 (the user's floor)
FREE = {"bk1": (1.5, 15.0, 60.0), "bk2": (2.0, 20.0, 60.0), "a1max": (2.0, 40.0, 100.0), "kK": (0.2, 0.3, 4.0),
        "r_h": (1.0, 13.0, 22.0), "beta": (6.0, -180.0, 180.0), "La": (1.5, 12.0, 26.0), "s_arm": (0.3, 4.0, 6.0),
        "hl": (0.4, 0.0, 3.15), "zr": (0.5, 0.0, 6.0), "r_lobe": (0.3, 7.0, 8.5), "smhi": (1.5, 5.0, 30.0), "smlo": (0.5, 5.0, 15.0),
        "az1": (2.0, None, None), "el1": (1.0, None, None), "az2": (2.0, None, None), "el2": (1.0, None, None),
        "wd": (3.0, None, None), "wa": (1.5, None, None), "b3": (0.03, 0.2, 0.6), "ang_min": (1.0, ANG_MIN_LO, 45.0),
        "lc": (1.5, 15.0, 40.0), "phib": (5.0, None, None)}


def full(p):
    P = dict(BEST); P.update({k: float(v) for k, v in p.items() if k in FREE})
    P["smhi"] = max(5.0, float(P["smhi"])); P["smlo"] = max(5.0, float(P["smlo"])); P["ang_min"] = max(ANG_MIN_LO, float(P["ang_min"]))
    P["law_mode"] = "lin"; P["gam"] = 0.0
    return P


def priced(P):
    """the worst built pairing: the folded dowel smlo + 0.5 (+ the stretched dowel through the 5.5 reading, see the docstring)"""
    P2 = dict(P)
    if os.environ.get("ENVP_NOPRICE") == "1": return P2, dict(why="unpriced reading (nominal stops)", margin=KIT.FOLD_MARGIN)
    P2["smlo"] = round(max(5.0, float(P["smlo"])) + 0.5, 4)
    # K's stop B at the K dyad's margin read at the same 5.5 (the model's k_ok: a1max <= bk1 + bk2 - margin)
    P2["a1max"] = round(min(float(P["a1max"]), float(P["bk1"]) + float(P["bk2"]) - max(5.0, KIT.FOLD_MARGIN)), 4)
    return P2, dict(smlo_nominal=float(P["smlo"]), smlo_priced=P2["smlo"], smhi=float(P["smhi"]), a1max_nominal=float(P["a1max"]),
                    a1max_priced=P2["a1max"], margin=KIT.FOLD_MARGIN)


# ---------------------------------------------------------------------------------------------------------------------
# the own-state J1-J3 margin in the th metric, from the member frames (docs/concepts/verify/minarc-bdp-remeasure.py checks_B)
def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(a, b)), -1, 1))))


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def th_margin(M, B):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; a1, a2 = math.degrees(D.a1) if D.a1 < 4 else D.a1, math.degrees(D.a2) if D.a2 < 4 else D.a2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]; rows = []
    dK = np.asarray(M.dK, float)
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(dK[i])) > 1e-6
        m_plain = _dm(th, a1, a2); m_eff = _dm(th, a1e, a2e); m_sub = _dm(th, b1, c)
        rows.append((min(m_sub, m_eff) if forced else m_plain, forced, m_plain, m_eff, m_sub, i))
    if not rows: return dict(min=None, n=0)
    own = [r[0] for r in rows]; lo = min(rows)
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)), lt5p5=int(sum(1 for x in own if x < 5.5 - 1e-6)),
                min_stateA=round(min([r[2] for r in rows if not r[1]] or [1e9]), 3), min_forced=round(min([r[0] for r in rows if r[1]] or [1e9]), 3),
                forced=int(sum(r[1] for r in rows)), a_deg=[round(a1, 2), round(a2, 2)],
                lowest=dict(own=round(lo[0], 3), forced=bool(lo[1]), kind=B.kind[lo[5]], **{k: B.poses[lo[5]][k] for k in ("plane", "elev", "axial")}))


# ---------------------------------------------------------------------------------------------------------------------
# continuity: the verifier's full-grid flood (minarc-stop-knuckle-4r-mechanism.py flood(grid="full"), same law) + fresh-pose edges
def conn_full(Mw, B, passive_jump=10.0, active_jump=25.0, step_deg=2.0, k_nn=6):
    from scipy.spatial.transform import Rotation as Rot, Slerp
    n = len(B.kind); D = Mw.D; P = Mw.p; st = Mw.kstate; Q = Mw.Q
    take = np.array([B.res[j] is not None and float(np.min(B.res[j])) >= 0 for j in range(n)])
    ws = [i for i in range(n) if B.kind[i] == "ws" and take[i]]
    Z = Mw.Z; names = list(Z["NAMES"]); allw = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
    Qa = Z["HG"][allw].astype(float); q, oka, _, _, X3, s = D.ik(Qa); sta = D._state.copy(); Kn = D.knee(s)
    c = (np.einsum("nij,nij->n", X3[0], Qa) - 1) / 2; res = np.degrees(np.arccos(np.clip(c, -1, 1)))
    oka = oka & Kn["ok"] & (np.abs(s[:, 2]) <= P["R_tol"]) & (res < 0.5)
    Pz = Z["POSE"][allw]; keyf = {tuple(np.round(Pz[k, :3], 1)): k for k in range(len(allw)) if oka[k]}
    valsf = [sorted(set(np.round(Pz[:, d], 1))) for d in range(3)]

    def edge(Qa_, Qb_):
        R2 = Rot.from_matrix(np.stack([Qa_, Qb_])); ang = np.degrees((R2[0].inv() * R2[1]).magnitude())
        m = max(2, int(math.ceil(ang / step_deg)) + 1); Qs = Slerp([0, 1], R2)(np.linspace(0, 1, m)).as_matrix()
        q_, ok_, _, _, _, s_ = D.ik(Qs); dK_ = D._dK; K_ = D.knee(s_); ok_ = ok_ & K_["ok"] & (np.abs(s_[:, 2]) <= P["R_tol"])
        if not ok_.all(): return False
        qq = np.degrees(np.c_[q_[:, :2], q_[:, 2] + K_["phi"], dK_, K_["qa"], K_["qb"]])
        dq = np.abs(np.degrees(PK.wrap(np.radians(np.diff(qq, axis=0)))))
        return bool((dq[:, 3:] <= passive_jump).all() and (dq[:, :3] <= active_jump).all())
    connf = np.zeros(len(allw), bool); front = [k for k in range(len(allw)) if oka[k] and sta[k] == 0]
    for k in front: connf[k] = True
    while front:
        nxt = []
        for a in front:
            x = tuple(np.round(Pz[a, :3], 1))
            for d in range(3):
                j = valsf[d].index(x[d])
                for jj in (j - 1, j + 1):
                    if 0 <= jj < len(valsf[d]):
                        y = list(x); y[d] = valsf[d][jj]; b = keyf.get(tuple(y))
                        if b is not None and not connf[b] and edge(Qa[a], Qa[b]): connf[b] = True; nxt.append(b)
        front = nxt
    pos = {int(z): k for k, z in enumerate(allw)}; cg = np.nonzero(connf)[0]
    conn = np.zeros(n, bool); fresh = dict(poses=0, forced=0, connected=0)
    for i in ws:
        if st[i] == 0: conn[i] = True
        elif int(B.idx[i]) in pos: conn[i] = bool(connf[pos[int(B.idx[i])]])
        if int(B.idx[i]) not in pos:
            fresh["poses"] += 1
            if st[i] != 0:
                fresh["forced"] += 1
                if len(cg):
                    tr = np.einsum("ij,nij->n", Q[i], Qa[cg]); angs = np.degrees(np.arccos(np.clip((tr - 1) / 2, -1, 1)))
                    for kk in np.argsort(angs)[:k_nn]:
                        if edge(Q[i], Qa[cg[kk]]): conn[i] = True; break
            fresh["connected"] += int(conn[i])
    drop = [j for j in ws if not conn[j]]
    return conn, take, drop, dict(grid_ok=int(oka.sum()), grid_forced_ok=int((oka & (sta != 0)).sum()), grid_forced_connected=int((connf & (sta != 0)).sum()),
                                  forced_taken=int(sum(1 for j in ws if st[j] != 0)), dropped=len(drop), fresh=fresh)


def score(M, B, conn=True):
    """continuity knock-out + plain report + the model's audit (near-touch 1 / 2 mm) + th margin; B.res restored after"""
    res0 = list(B.res); out = {}
    if conn:
        _, _, drop, ci = conn_full(M, B); out["conn"] = ci
        for j in drop: B.res[j] = None
    rep = B.report(); au = PK.audit(M, B); out.update({k: rep[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")})
    out.update(near1=au["gap_near1"], near2=au["gap_near2"], min_metal=au["near_touch_min_mm"], ovh=au["overhead140"]); out["th"] = th_margin(M, B)
    B.res = res0
    return out


def frozen_on(M1, Bw):
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(SC.SCModel):
        def fit(self):
            for a in FROZEN_ATTRS:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    Bw.reset(); M = Frozen(Bw, P2); r = M.run(); return M, r


# ---------------------------------------------------------------------------------------------------------------------
_W = {}


def obj_of(p):
    Benv, Bsel, B60 = _W["B"]; P = full(p); Pp, pinfo = priced(P); out = dict(price=pinfo); t0 = time.time()
    Benv.reset(); r, M = SC._report(Benv, Pp)
    if not np.asarray(M.kin_ok).any(): out.update(obj=400.0, nothing_closes=True); return out
    honest = bool(r.get("honest", True)) and not r.get("sidecar_fail")
    e = score(M, Benv); out["env"] = e; out["drive"] = {k: (r.get("drive") or {}).get(k) for k in ("dK_taken_max", "why_end", "th_max", "pa_max_used")}
    out["sidecar"] = getattr(M, "_sc_info", None)
    Mf, _ = frozen_on(M, Bsel); sel = score(Mf, Bsel); out["sel"] = sel
    B60.reset(); r6, M6 = SC._report(B60, Pp); g60 = PK.audit(M6, B60)["gap_near1"] if np.asarray(M6.kin_ok).any() else 400.0
    out["g60_near"] = g60; out["claim_pen"] = round(max(0.0, g60 - e["near1"] - CLAIM_TOL), 3)
    ref2 = float(os.environ.get("ENVP_REF_NEAR2", "nan")); out["shell_pen"] = round(max(0.0, e["near2"] - ref2), 3) if ref2 == ref2 else 0.0
    marg_bad = e["th"].get("min") is not None and e["th"]["min"] < KIT.FOLD_MARGIN - 1e-6
    out["honest"] = honest; out["margin_bad"] = bool(marg_bad)
    out["obj"] = round(e["near1"] + out["claim_pen"] + out["shell_pen"] + (0.0 if honest else 100.0) + (100.0 if marg_bad else 0.0), 3)
    out.update(env_near1=e["near1"], env_near2=e["near2"], env_gap=e["gap"], sel_near1=sel["near1"], sel_near2=sel["near2"], sel_gap=sel["gap"],
               secs=round(time.time() - t0, 1))
    return out


def _benches():
    if os.environ.get("ENVP_SMOKE"):                         # local smoke test: exact, a few poses of each bench
        n = int(os.environ["ENVP_SMOKE"]); out = []
        for B in (EB.bench("env", exact=True), EB.bench("envsel", exact=True)):
            sel = [i for i, k in enumerate(B.kind) if k == "clip"][:n] + [i for i, k in enumerate(B.kind) if k == "ws"][::25][:n]
            B.idx = np.asarray(B.idx)[sel]; B.kind = [B.kind[i] for i in sel]; B.clip = [B.clip[i] for i in sel]; B.poses = [B.poses[i] for i in sel]
            B.res = [None] * len(sel); out.append(B)
        return tuple(out) + (CB.Bench(60, 160),)
    return (EB.bench("env"), EB.bench("envsel"), CB.Bench(60, 160))


def _init(plname=None):
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    if "B" not in _W: _W["B"] = _benches()
    if not os.environ.get("ENVP_SMOKE") and any(B.mode != "fast" for B in _W["B"]):
        raise RuntimeError("env / envsel / Bench(60,160) not on the fast grid (link: eval \"$(python3 tools/env_bench.py use env)\")")


def _eval(arg):
    tag, p = arg; t0 = time.time()
    try:
        r = obj_of(p)
        return dict(tag=tag, params=p, obj=r["obj"], xfit=r, secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-1500:], secs=round(time.time() - t0, 1))


class Plugin:
    name = "sidecar_env"; FREE = {k: (s, lo, hi, k) for k, (s, lo, hi) in FREE.items()}

    def base(self): return dict(BEST)


def run_cma(argv):
    import argparse
    X = _load("crossfit_polish_for_sidecar", os.path.join(REPO, "tools", "crossfit_polish.py"))
    X.PLUGINS["sidecar_env"] = Plugin; X._init = _init; X._eval = _eval
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--plugin", default="sidecar_env")
    ap.add_argument("--x0", default="{}"); ap.add_argument("--fixed", default="")
    ap.add_argument("--label", required=True); ap.add_argument("--out", required=True); ap.add_argument("--state", default="")
    ap.add_argument("--state-out", default=""); ap.add_argument("--sigma", type=float, default=0.4)
    ap.add_argument("--popsize", type=int, default=8); ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--budget-s", type=float, default=2400); ap.add_argument("--max-gen", type=int, default=400)
    ap.add_argument("--max-evals", type=int, default=700); ap.add_argument("--patience", type=int, default=12)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    _init()
    if "ENVP_REF_NEAR2" not in os.environ:                   # the verified config's in-sample env 2-mm number (the shell guard's reference)
        r0 = _eval(("ref-verified", {}))
        os.environ["ENVP_REF_NEAR2"] = str(r0["xfit"]["env_near2"]); print("[ref] verified env near1 / near2", r0["xfit"].get("env_near1"),
                                                                            r0["xfit"].get("env_near2"), r0["secs"], "s", flush=True)
    X.cma(a)


def score_list(outp, items, jobs):
    import multiprocessing as mp
    _init(); pool = mp.get_context("fork").Pool(jobs, initializer=_init); t = time.time()
    res = pool.map(_eval, [(it.get("tag", f"s{i}"), it["params"]) for i, it in enumerate(items)]); pool.close()
    json.dump(res, open(outp, "w"), indent=1, default=float)
    for r in res:
        x = r.get("xfit") or {}
        print(r["tag"], "obj", r["obj"], "env near1/near2/gap", x.get("env_near1"), x.get("env_near2"), x.get("env_gap"), "sel", x.get("sel_near1"), x.get("sel_near2"),
              x.get("sel_gap"), "g60", x.get("g60_near"), "th", (x.get("env") or {}).get("th", {}).get("min"), r.get("error", ""), r["secs"], "s", flush=True)
    print(f"scored {len(res)} in {time.time() - t:.0f}s")


def load_rows(files):
    rows = []
    for f in files:
        for r in json.load(open(f)):
            r["_file"] = os.path.basename(f); rows.append(r)
    return rows


def best(files, k=15):
    rows = [r for r in load_rows(files) if not r.get("error") and (r.get("xfit") or {}).get("sel_near1") is not None]
    rows.sort(key=lambda r: r["obj"])
    for r in rows[:k]:
        x = r["xfit"]; print(r["tag"], "obj", r["obj"], "env n1/n2/gap", x["env_near1"], x["env_near2"], x["env_gap"], "sel n1/n2/gap", x["sel_near1"], x["sel_near2"],
                             x["sel_gap"], "g60", x["g60_near"], "th", x["env"]["th"].get("min"))
    return rows[:k]


def picks(files, outdir, k_run=15, n=3, dist=0.5):
    """candidates = the best k_run rows by the objective of each run (no error, no penalty); a candidate may not be worse
    than the verified config at 2 mm on the independent envsel draw (the dominance gate's 2-mm half, read before any held-out
    number); ranked by the envsel near-touch (1 mm); the top n that differ from every kept pick by >= dist CMA scale units in
    some parameter. Writes outdir/pick<k>.json (nominal free params + the full config)."""
    allr = load_rows(files); ref = [r for r in allr if r["tag"].endswith("-g0-x0") and not r.get("error")]
    rs = ref[0]["xfit"] if ref else None
    cand = []
    for f in files:
        rr = [r for r in json.load(open(f)) if not r.get("error") and r["obj"] < 100 and (r.get("xfit") or {}).get("sel_near1") is not None]
        rr.sort(key=lambda r: r["obj"]); cand += [dict(r, _file=os.path.basename(f)) for r in rr[:k_run] if not r["tag"].endswith("-g0-x0")]
    ok2 = [r for r in cand if rs is None or r["xfit"]["sel_near2"] <= rs["sel_near2"] + 1e-9]
    pool = sorted(ok2, key=lambda r: (r["xfit"]["sel_near1"], r["obj"])) + sorted([r for r in cand if r not in ok2], key=lambda r: (r["xfit"]["sel_near1"], r["obj"]))
    keep = []
    for r in pool:
        if all(max(abs(float(r["params"].get(k, BEST[k])) - float(q["params"].get(k, BEST[k]))) / FREE[k][0] for k in FREE) >= dist for q in keep): keep.append(r)
        if len(keep) == n: break
    os.makedirs(outdir, exist_ok=True); out = []
    if rs: print("verified x0: obj", ref[0]["obj"], "env n1/n2/gap", rs["env_near1"], rs["env_near2"], rs["env_gap"], "sel n1/n2/gap", rs["sel_near1"], rs["sel_near2"], rs["sel_gap"], "g60", rs["g60_near"])
    for j, r in enumerate(keep, 1):
        x = r["xfit"]; d = dict(tag=r["tag"], file=r["_file"], obj=r["obj"], params=r["params"], full=full(r["params"]), xfit_summary={k: x.get(k) for k in (
            "env_near1", "env_near2", "env_gap", "sel_near1", "sel_near2", "sel_gap", "g60_near", "claim_pen", "shell_pen")}, sel_2mm_ok=r in ok2)
        json.dump(d, open(os.path.join(outdir, f"pick{j}.json"), "w"), indent=1, default=float); out.append(d)
        print(f"pick{j}", r["tag"], "obj", r["obj"], "env n1/n2/gap", x["env_near1"], x["env_near2"], x["env_gap"], "sel n1/n2/gap", x["sel_near1"], x["sel_near2"], x["sel_gap"],
              "g60", x["g60_near"], "2mm-ok", r in ok2)
    return out


def gate(rows):
    """convergence gate on a sequence of tries (eval order): best gained < 1 over the 2nd half, < 0.5 over the last third, top-5 within 3"""
    f = np.array([r["obj"] for r in rows], float); n = len(f)
    if n < 6: return dict(n=n)
    run = np.minimum.accumulate(f); h = n // 2; t = (2 * n) // 3; top5 = np.sort(f)[:5]
    g2, g3 = float(run[h - 1] - run[-1]), float(run[t - 1] - run[-1])
    return dict(n=n, best=round(float(run[-1]), 3), gain_2nd_half=round(g2, 3), gain_last_third=round(g3, 3), top5_spread=round(float(top5[-1] - top5[0]), 3),
                passes=bool(g2 < 1.0 and g3 < 0.5 and top5[-1] - top5[0] <= 3.0))


# ---------------------------------------------------------------------------------------------------------------------
def params_of(which):
    if which == "BEST": return dict(BEST)
    d = json.load(open(which)); return full(d.get("params", d))


def rescore(which, outp):
    """fit env FAST -> wear env EXACT (frozen), continuity with fresh-pose edges, priced"""
    assert os.environ.get("CB_EXACT") == "1"
    P = params_of(which); Pp, pinfo = priced(P); t = time.time()
    Bf = EB.bench("env", exact=False); assert Bf.mode == "fast"
    Bf.reset(); r1, M1 = SC._report(Bf, Pp); fit = score(M1, Bf)
    Bw = EB.bench("env", exact=True); assert Bw.mode == "exact"
    M, r = frozen_on(M1, Bw); wear = score(M, Bw)
    out = dict(which=which, params=P, priced=Pp, price=pinfo, fit_env_fast=fit, wear_env_exact=wear, why=r.get("why"), parts_pairs=r.get("parts_pairs"),
               sidecar=getattr(M1, "_sc_info", None), margin=KIT.FOLD_MARGIN, secs=round(time.time() - t, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(which=which, fit={k: fit[k] for k in ("gap", "near1", "near2")}, wear={k: wear[k] for k in ("gap", "near1", "near2", "reach", "inband14", "contact")},
                          th=wear["th"].get("min"), conn=wear.get("conn"), secs=out["secs"]), default=float), flush=True)


def claim(fit, wb, which, outp):
    """V.frozen_wear (the verifier's harness, unchanged) with the fit bench swapped when fit == 'env'; th margin added on
    every extra_checks call (the worn model's is the last); continuity = the harness's own connected_report (bench / knn / full)"""
    assert os.environ.get("CB_EXACT") == "1"
    P = params_of(which); Pp, pinfo = priced(P)
    orig = CB.Bench
    if fit == "env":
        FIT = EB.bench("env", exact=False); assert FIT.mode == "fast"

        def Bench2(n_clip=20, n_ws=20, *a, **k):
            if (n_clip, n_ws) == (60, 160): FIT.reset(); return FIT
            return orig(n_clip, n_ws, *a, **k)
        CB.Bench = Bench2
    ex0 = V.extra_checks; seen = {}

    def ex2(M, B):
        o = ex0(M, B); o["th_margin_own_state"] = th_margin(M, B); seen["n"] = seen.get("n", 0) + 1; return o
    V.extra_checks = ex2
    t = time.time()
    try: out = V.frozen_wear(dict(Pp), wb, flood=True)
    finally: CB.Bench = orig; V.extra_checks = ex0
    out.update(fit_protocol=fit, wear=wb, which=which, nominal=P, priced=Pp, price=pinfo, margin=KIT.FOLD_MARGIN, secs=round(time.time() - t, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    cr = out.get("connected") or {}
    print(json.dumps(dict(which=os.path.basename(which), fit=fit, wear=wb, n=out["n"], margin=KIT.FOLD_MARGIN, frozen=out["frozen"], corrected=out["extra"].get("corrected"),
                          near1=out["audit"]["gap_near1"], near2=out["audit"]["gap_near2"], minmetal=out["audit"]["near_touch_min_mm"],
                          th=out["extra"]["th_margin_own_state"].get("min"), knn=(cr.get("connected_knn") or {}).get("gap"), full=(cr.get("connected_full") or {}).get("gap"),
                          failing=out["extra"].get("poses_failing"), secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: raise SystemExit(__doc__)
    if a[0] == "cma": run_cma(a)
    elif a[0] == "score":
        jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 2
        score_list(a[1], json.loads(a[2]) if not os.path.exists(a[2]) else json.load(open(a[2])), jobs)
    elif a[0] == "best": best([x for x in a[1:] if x.endswith(".json")], int(a[a.index("--k") + 1]) if "--k" in a else 15)
    elif a[0] == "gate":
        fs = [x for x in a[1:] if x.endswith(".json")]; allr = []
        for f in fs:
            rr = [r for r in json.load(open(f))]; allr += [(r.get("gen", 0), i, r) for i, r in enumerate(rr)]; print(os.path.basename(f), gate(rr))
        allr.sort(key=lambda t: (t[0], t[1])); print("combined (by generation)", gate([t[2] for t in allr]))
    elif a[0] == "picks": picks([x for x in a[1:] if x.endswith(".json")], a[a.index("--out") + 1])
    elif a[0] == "rescore": rescore(a[1], a[2])
    elif a[0] == "claim": claim(a[1], a[2], a[3], a[4])
    else: raise SystemExit(__doc__)
