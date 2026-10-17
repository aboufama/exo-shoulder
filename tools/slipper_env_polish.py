#!/usr/bin/env python3
"""FINAL POLISH OF slipper-nose-knuckle-3r (round-10 winner, the verified LEAD) ON THE ENVELOPE BENCH (tools/env_bench.py
'env') + the claim wrapper that wears a config through the verifier's own harness (docs/concepts/verify/
slipper-nose-knuckle-3r.py, imported unchanged: the lead family's frozen_wear retargeted at SNModel + the nose radius;
benches swapped only when asked) with built-stop pricing.

Adapted from tools/roller_env_polish.py (the same family's polish; its lessons: the env-FIT gain is a fit-protocol
artifact unless the Bench(60,160)-fit shape travels too, so the objective scores BOTH shapes; summed-depth guards on a
360-pose draw are too noisy; the flank sits on a synthesis knife edge) and with the inband-rssr audit's three rulings
(docs/alignment/inband-rssr-knuckle-3r.md): (i) every config is claimed at BOTH readings, priced (smlo +0.5, margin 5.5,
K stop B at bk1 + bk2 - 5.5) AND unpriced (nominal stops, margin 5 - the reading of the lead's on-file 18.49 / 23.45),
and compared like-for-like; (ii) the single CAD pick is PRE-REGISTERED by `prereg` (a committed rule on the envsel draw)
before any claim number exists, the other picks are report-only; (iii) bench AND held out are both compared.

CLAUDE.md rules carried: search on a representative envelope sample, claim on the held-out set; near-touch objective
(metal < 1 mm = contact); continuity (the verifier's full-grid flood + every fresh env pose joined to the connected grid
by a 2-deg slerp edge to one of its 6 nearest connected grid nodes, same law); the 5-deg margin in the th metric with
stops as variables >= 5.0 priced at +0.5; O20 (the model's hubs, unchanged); kinematic only; held-out split held out.

FIXED (not polish variables): mu 0.087 (a material property: the honest friction of the claim) and nose_r 1.1839 (the
verified nose; the verifier's N4 re-wears catalogue dowels). The transmission cap is the model's own rule in BOTH
readings: kinematic PA <= 43 - atan(mu) (38.03 deg), itself 2 deg under the 45 gate with friction added.
The knee window ang_min is free, bounded below by the verified 25.2189.

Objective of a free-parameter set p (lower is better):
  P = BEST + p; P' = priced(P)
  a = fit P' on env FAST, score env in-sample (continuity knock-out) -> near-touch gap (1 mm)
  b = fit P' on Bench(60,160) FAST, wear that shape FROZEN on env FAST (continuity knock-out) -> near-touch gap (1 mm)
  obj = (a + b) / 2 + claim-fit guard max(0, g60 - a - 3) + depth guard 0.1 x max(0, depth - verified's own)
      + 100 if dishonest (drive idle, PA over the cap, knee moved) or a taken pose's own-state th margin < the reading's
  logged, not optimised: both shapes worn FROZEN on envsel (independent draw) -> the pick-selection numbers.

    CB_FOLD_MARGIN=5.5 python3 tools/slipper_env_polish.py cma --label L --out O.json [...]
    python3 tools/slipper_env_polish.py gate O1.json [..] | picks O1.json .. --out DIR | prereg DIR
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 python3 tools/slipper_env_polish.py rescore <BEST|params.json> OUT.json
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 python3 tools/slipper_env_polish.py claim <fit60|env> <bench|held> <BEST|params.json> OUT.json
      (ENVP_NOPRICE=1 CB_FOLD_MARGIN=5: the unpriced reading = the verified one)
    python3 tools/slipper_env_polish.py claimjobs <picks dir> jobs_claim.json
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


os.environ.setdefault("SN_CELL", "lead")
V = _load("slipper_v_for_envpolish", os.path.join(HERE_V, "slipper-nose-knuckle-3r.py"))      # the verifier's harness (loads the claim's model)
SN = V.SN; RL = SN.RL; H = V.H; SC, PK, S = SN.SC, SN.PK, SN.S
assert SN.CELL == "lead"
ANG_MIN_LO = 25.2189                                         # the verified knee window (LEAD_BEST ang_min)
FIXED = {"mu": 0.087, "nose_r": float(V.BEST["nose_r"])}       # material friction + the verified nose: not polish variables
CLAIM_TOL = 3.0
DEPTH_W = float(os.environ.get("ENVP_DEPTH_W", "0.1"))       # gap points per mm of summed penetration over the reference
FROZEN_ATTRS = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_cam_table", "_wedge_info")
# free parameters: (CMA scale, lo, hi). Ranges = the model's own clamps (RL._clamp / RF._clamp); stops >= 5.0 (the user's floor)
FREE = {"bk1": (1.0, 26.0, 32.0), "bk2": (1.5, 38.0, 48.0), "a1max": (2.0, 40.0, 80.0), "kK": (0.2, 0.3, 4.0),
        "g": (0.15, 1.8, 3.0), "beta": (3.0, -180.0, -150.0), "r_c": (0.8, 14.5, 19.5), "lift": (0.5, 0.0, 4.0),
        "hl": (0.4, 0.0, 3.15), "zr": (0.5, 0.0, 6.0), "s_arm": (0.3, 4.0, 6.0), "r_lobe": (0.3, 7.0, 8.5),
        "smhi": (1.5, 5.0, 30.0), "smlo": (0.5, 5.0, 15.0),
        "az1": (2.0, None, None), "el1": (1.0, None, None), "az2": (2.0, None, None), "el2": (1.0, None, None),
        "wd": (3.0, None, None), "wa": (1.5, None, None), "b3": (0.03, 0.2, 0.6), "ang_min": (1.0, ANG_MIN_LO, 45.0),
        "lc": (1.5, 15.0, 40.0), "phib": (5.0, None, None)}
# the verified config in full: the row's best_params over the model's PARAMS (smlo, az1, el1, wd, wa, b3, ang_min, law,
# chain come from the lead's LEAD_BEST inside SN.PARAMS, exactly as the verifier's frozen_wear merges them)
BEST = {k: SN.PARAMS[k] for k in list(FREE) + ["law_mode", "chain", "cprog", "near2"] if k in SN.PARAMS}
BEST.update(V.BEST); BEST.update(FIXED)


def pa_read():
    return SN.pa_kin(FIXED["mu"])                           # the model's own rule in both readings (SNModel._rod_metal sets it)


def set_pa():
    SN.RF.PA_MAX = pa_read()


def full(p):
    P = dict(BEST); P.update({k: float(v) for k, v in p.items() if k in FREE}); P.update(FIXED)
    P["smhi"] = max(5.0, float(P["smhi"])); P["smlo"] = max(5.0, float(P["smlo"])); P["ang_min"] = max(ANG_MIN_LO, float(P["ang_min"]))
    P["law_mode"] = "lin"; P["chain"] = "free"; P["cprog"] = 0.0; P["near2"] = 1
    return P


def priced(P):
    """the worst built pairing: folded dowel smlo + 0.5, stop B at the K dyad's 5.5 margin, the reading at CB_FOLD_MARGIN 5.5;
    the transmission cap stays the model's own (43 - atan(mu))"""
    P2 = dict(P); set_pa()
    if os.environ.get("ENVP_NOPRICE") == "1": return P2, dict(why="unpriced reading (nominal stops)", margin=KIT.FOLD_MARGIN, pa_max=round(SN.RF.PA_MAX, 3))
    P2["smlo"] = round(max(5.0, float(P["smlo"])) + 0.5, 4)
    P2["a1max"] = round(min(float(P["a1max"]), float(P["bk1"]) + float(P["bk2"]) - max(5.0, KIT.FOLD_MARGIN)), 4)
    return P2, dict(smlo_nominal=float(P["smlo"]), smlo_priced=P2["smlo"], smhi=float(P["smhi"]), a1max_nominal=float(P["a1max"]),
                    a1max_priced=P2["a1max"], margin=KIT.FOLD_MARGIN, pa_max=round(SN.RF.PA_MAX, 3))


# ---------------------------------------------------------------------------------------------------------------------
def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(a, b)), -1, 1))))


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def th_margin(M, B):
    """own-state J1-J3 margin in the th metric from the member frames (= tools/sidecar_env_polish.py th_margin)"""
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
                forced=int(sum(r[1] for r in rows)), a_deg=[round(a1, 2), round(a2, 2)],
                lowest=dict(own=round(lo[0], 3), forced=bool(lo[1]), kind=B.kind[lo[5]], **{k: B.poses[lo[5]][k] for k in ("plane", "elev", "axial")}))


def depth_of(B):
    """contact DEPTH (the alignment_paired dump's reading: a contact pose has min metal < 0; depth = -min), by elevation"""
    d = []
    for i in range(len(B.idx)):
        r = B.res[i]
        if r is not None and len(r) and float(np.min(r)) < 0: d.append((-float(np.min(r)), float(B.poses[i]["elev"]), B.kind[i], i))
    if not d: return dict(n=0, sum=0.0, max=0.0, below90=0, ovh140=0)
    return dict(n=len(d), sum=round(sum(x[0] for x in d), 3), max=round(max(x[0] for x in d), 3), below90=int(sum(1 for x in d if x[1] < 90)),
                ovh140=int(sum(1 for x in d if x[1] >= 140)), deepest=[dict(mm=round(x[0], 2), elev=x[1], kind=x[2], **{k: B.poses[x[3]][k] for k in ("plane", "axial")})
                                                                   for x in sorted(d, reverse=True)[:5]])


# ---------------------------------------------------------------------------------------------------------------------
# continuity: the verifier's full-grid flood (same law) + fresh-pose edges (= tools/sidecar_env_polish.py conn_full)
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
    """continuity knock-out + plain report + the model's audit (near-touch 1 / 2 mm) + th margin + depth + ws in-band"""
    res0 = list(B.res); out = {}
    if conn:
        _, _, drop, ci = conn_full(M, B); out["conn"] = ci
        for j in drop: B.res[j] = None
    rep = B.report(); au = PK.audit(M, B); out.update({k: rep[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")})
    out.update(near1=au["gap_near1"], near2=au["gap_near2"], min_metal=au["near_touch_min_mm"], ovh=au["overhead140"]); out["th"] = th_margin(M, B)
    out["depth"] = depth_of(B); out["ws_inband"] = RL.ws_inband(B)
    B.res = res0
    return out


def frozen_on(M1, Bw):
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(SN.SNModel):
        def fit(self):
            for a in FROZEN_ATTRS:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    Bw.reset(); M = Frozen(Bw, P2); r = M.run(); return M, r


# ---------------------------------------------------------------------------------------------------------------------
_W = {}


def _honest(r):
    return bool(r.get("honest", True)) and not (r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"))


def obj_of(p):
    Benv, Bsel, B60 = _W["B"]; P = full(p); Pp, pinfo = priced(P); out = dict(price=pinfo); t0 = time.time()
    Benv.reset(); r, M = SN._report(Benv, Pp)
    if not np.asarray(M.kin_ok).any(): out.update(obj=400.0, nothing_closes=True); return out
    e = score(M, Benv); out["env"] = e
    out["cam"] = r.get("cam"); out["drive"] = {k: (r.get("drive") or {}).get(k) for k in ("dK_taken_max", "why_end", "th_max")}
    nosel = Bsel is None
    if not nosel: Mf, _ = frozen_on(M, Bsel); sel = score(Mf, Bsel); out["sel"] = sel
    B60.reset(); r6, M6 = SN._report(B60, Pp)
    if not np.asarray(M6.kin_ok).any(): out.update(obj=400.0, nothing_closes_60=True); return out
    g60 = PK.audit(M6, B60)["gap_near1"]
    M6e, _ = frozen_on(M6, Benv); e60 = score(M6e, Benv); out["env60"] = e60
    if not nosel: M6s, _ = frozen_on(M6, Bsel); s60 = score(M6s, Bsel); out["sel60"] = s60
    a, b = e["near1"], e60["near1"]; out["g60_near"] = g60; out["claim_pen"] = round(max(0.0, g60 - a - CLAIM_TOL), 3)
    dep = 0.5 * (e["depth"]["sum"] + e60["depth"]["sum"]); out["depth_env"] = round(dep, 3)
    ref = float(os.environ.get("ENVP_REF_DEPTH", "nan")); out["depth_pen"] = round(DEPTH_W * max(0.0, dep - ref), 3) if ref == ref else 0.0
    honest = _honest(r) and _honest(r6)
    mins = [x["th"].get("min") for x in (e, e60) if x["th"].get("min") is not None]
    marg_bad = bool(mins) and min(mins) < KIT.FOLD_MARGIN - 1e-6
    out["honest"] = honest; out["margin_bad"] = bool(marg_bad)
    rob_pen = 0.0
    if os.environ.get("ENVP_ROBUST") == "1" and honest and not marg_bad:      # flank synthesis-robustness margin: ROBUST_W per failing neighbour
        rb = robust(Pp, B60, float((r6.get("drive") or {}).get("dK_taken_max") or 0.0)); out["robust"] = {k: rb[k] for k in ("ok", "n_fail", "min_dK_lim", "dK_need")}
        rob_pen = float(os.environ.get("ENVP_ROBUST_W", "5")) * rb["n_fail"]   # soft (graded, so CMA can walk out of the knife edge); picks need n_fail 0
    out["robust_pen"] = rob_pen
    out["obj"] = round(0.5 * (a + b) + out["claim_pen"] + out["depth_pen"] + (0.0 if honest else 100.0) + (100.0 if marg_bad else 0.0) + rob_pen, 3)
    out.update(env_near1=a, env60_near1=b, env_gap=e["gap"], env60_gap=e60["gap"], secs=round(time.time() - t0, 1))
    if not nosel:
        out.update(sel_near1=sel["near1"], sel60_near1=s60["near1"], sel_gap=sel["gap"], sel60_gap=s60["gap"],
                   sel_depth=round(0.5 * (sel["depth"]["sum"] + s60["depth"]["sum"]), 3),
                   sel_mean_near1=round(0.5 * (sel["near1"] + s60["near1"]), 3), sel_worst_near1=max(sel["near1"], s60["near1"]))
    return out


ROBUST_TOL = {"beta": 1.0, "r_c": 0.25, "g": 0.05}          # flank cut tolerance: deg / mm / ratio (one at a time, +-)


def robust(Pp, B, dK_need=None):
    """SYNTHESIS-ROBUSTNESS of the flank (the beta -178 knife edge: 22 / 27 nearby cuts failed synthesis): re-fit the priced
    config with each flank parameter moved by +-ROBUST_TOL (one at a time) on bench B; every neighbour must synthesise
    (honest, drive not idle, pressure angles under the read cap) AND keep a drive range >= the nominal's taken dK - 1 deg
    (the poses the nominal takes stay drivable by a toleranced cut). Returns dict(ok, n_fail, min_dK_lim, rows)."""
    if dK_need is None:
        B.reset(); r0, _ = SN._report(B, Pp); dK_need = float((r0.get("drive") or {}).get("dK_taken_max") or 0.0)
    rows = []; ok = True; mins = []
    for k, d in ROBUST_TOL.items():
        lo, hi = FREE[k][1], FREE[k][2]
        for s in (-1, 1):
            q = dict(Pp); q[k] = float(min(max(float(Pp[k]) + s * d, lo), hi))
            B.reset(); r, M = SN._report(B, q); cam = r.get("cam") or {}
            lim = float(cam.get("dK_lim") or 0.0); good = _honest(r) and bool(np.asarray(M.kin_ok).any()) and lim >= dK_need - 1.0
            ok &= good; mins.append(lim)
            rows.append(dict(k=k, d=s * d, dK_lim=round(lim, 2), why=cam.get("why_lim"), pa_horn=cam.get("pa_horn_max_taken"),
                             pa_crank=cam.get("pa_crank_max_taken"), honest=_honest(r), ok=bool(good)))
    return dict(ok=bool(ok), n_fail=int(sum(not r["ok"] for r in rows)), min_dK_lim=round(min(mins), 2) if mins else None,
                dK_need=round(dK_need, 2), rows=rows)


def _benches():
    if os.environ.get("ENVP_SMOKE"):                         # local smoke test: exact, a few poses of each bench
        n = int(os.environ["ENVP_SMOKE"]); out = []
        for B in (EB.bench("env", exact=True), EB.bench("envsel", exact=True)):
            sel = [i for i, k in enumerate(B.kind) if k == "clip"][:n] + [i for i, k in enumerate(B.kind) if k == "ws"][::25][:n]
            B.idx = np.asarray(B.idx)[sel]; B.kind = [B.kind[i] for i in sel]; B.clip = [B.clip[i] for i in sel]; B.poses = [B.poses[i] for i in sel]
            B.res = [None] * len(sel); out.append(B)
        return tuple(out) + (CB.Bench(60, 160),)
    # ENVP_NOSEL=1: no envsel cache here (the local run, the farm launch was refused) - the selection draw is not scored
    return (EB.bench("env"), None if os.environ.get("ENVP_NOSEL") == "1" else EB.bench("envsel"), CB.Bench(60, 160))


def _init(plname=None):
    os.environ.setdefault("OMP_NUM_THREADS", "1"); set_pa()
    if "B" not in _W: _W["B"] = _benches()
    if not os.environ.get("ENVP_SMOKE") and any(B.mode != "fast" for B in _W["B"] if B is not None):
        raise RuntimeError("env / envsel / Bench(60,160) not on the fast grid (link: eval \"$(python3 tools/env_bench.py use env)\")")


_MEMO = {}                                                   # the verified config's ref eval is re-used as the CMA's x0 (same full params)


def _key(p): return json.dumps({k: round(float(v), 4) for k, v in full(p).items() if isinstance(v, (int, float))}, sort_keys=True)


def _eval(arg):
    tag, p = arg; t0 = time.time()
    try:
        k = _key(p)
        if k in _MEMO: return dict(tag=tag, params=p, obj=_MEMO[k]["obj"], xfit=_MEMO[k], secs=0.0, memo=True)
        r = obj_of(p); _MEMO[k] = r
        return dict(tag=tag, params=p, obj=r["obj"], xfit=r, secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-1500:], secs=round(time.time() - t0, 1))


class Plugin:
    name = "slipper_env"; FREE = {k: (s, lo, hi, k) for k, (s, lo, hi) in FREE.items()}

    def base(self): return dict(BEST)


def run_cma(argv):
    import argparse
    X = _load("crossfit_polish_for_slipper", os.path.join(REPO, "tools", "crossfit_polish.py"))
    X.PLUGINS["slipper_env"] = Plugin; X._init = _init; X._eval = _eval
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--plugin", default="slipper_env")
    ap.add_argument("--x0", default="{}"); ap.add_argument("--fixed", default="")
    ap.add_argument("--label", required=True); ap.add_argument("--out", required=True); ap.add_argument("--state", default="")
    ap.add_argument("--state-out", default=""); ap.add_argument("--sigma", type=float, default=0.4)
    ap.add_argument("--popsize", type=int, default=8); ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--budget-s", type=float, default=2400); ap.add_argument("--max-gen", type=int, default=400)
    ap.add_argument("--max-evals", type=int, default=700); ap.add_argument("--patience", type=int, default=12)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    _init()
    if "ENVP_REF_DEPTH" not in os.environ:                   # the verified config's own (priced) env depth reading: the guard's reference
        r0 = _eval(("ref-verified", {}))
        os.environ["ENVP_REF_DEPTH"] = str(r0["xfit"]["depth_env"])
        print("[ref] verified obj", r0["obj"], "env near1 / env60 near1", r0["xfit"].get("env_near1"), r0["xfit"].get("env60_near1"),
              "depth", r0["xfit"]["depth_env"], r0["secs"], "s", flush=True)
    X.cma(a)


def score_list(outp, items, jobs):
    import multiprocessing as mp
    _init(); pool = mp.get_context("fork").Pool(jobs, initializer=_init); t = time.time()
    res = pool.map(_eval, [(it.get("tag", f"s{i}"), it["params"]) for i, it in enumerate(items)]); pool.close()
    json.dump(res, open(outp, "w"), indent=1, default=float)
    for r in res:
        x = r.get("xfit") or {}
        print(r["tag"], "obj", r["obj"], "env n1 / env60 n1", x.get("env_near1"), x.get("env60_near1"), "sel n1 / sel60 n1", x.get("sel_near1"), x.get("sel60_near1"),
              "depth", x.get("depth_env"), x.get("sel_depth"), "g60", x.get("g60_near"), "th", (x.get("env") or {}).get("th", {}).get("min"), "cam", x.get("cam"),
              r.get("error", ""), r["secs"], "s", flush=True)
    print(f"scored {len(res)} in {time.time() - t:.0f}s")


def load_rows(files):
    rows = []
    for f in files:
        for r in json.load(open(f)):
            r["_file"] = os.path.basename(f); rows.append(r)
    return rows


def _line(r):
    x = r["xfit"]; g = x.get
    return (f"{r['tag']} obj {r['obj']} env n1 {g('env_near1')} env60 n1 {g('env60_near1')} | sel n1 {g('sel_near1')} sel60 n1 {g('sel60_near1')} "
            f"(mean {g('sel_mean_near1')}) | depth env {g('depth_env')} sel {g('sel_depth')} | g60 {g('g60_near')} th {(g('env') or {}).get('th', {}).get('min')} "
            f"pa {(g('cam') or {}).get('pa_horn_max_taken')} dKlim {(g('cam') or {}).get('dK_lim')}")


def _ok(r): return not r.get("error") and r["obj"] < 100 and (r.get("xfit") or {}).get("env_near1") is not None


def _selkey(x):
    """the pick-selection number: the envsel near-touch mean over the two fits when envsel was scored, else the objective"""
    return x["sel_mean_near1"] if x.get("sel_mean_near1") is not None else x["obj_"]


def best(files, k=15):
    rows = [r for r in load_rows(files) if _ok(r)]
    rows.sort(key=lambda r: r["obj"])
    for r in rows[:k]: print(_line(r))
    return rows[:k]


def picks(files, outdir, k_run=15, n=3, dist=0.5):
    """candidates = the best k_run rows by the objective of each run (no error, no penalty); a candidate may not be deeper
    than the verified config (envsel depth when scored, else the env depth reading) - the depth watch, read before any
    held-out number; ranked by the envsel near-touch mean over the two fits (else by the objective); the top n that differ
    from every kept pick by >= dist CMA scale units in some parameter. Writes outdir/pick<k>.json."""
    allr = load_rows(files); ref = [r for r in allr if r["tag"].endswith("-g0-x0") and not r.get("error")]
    rs = ref[0]["xfit"] if ref else None
    dkey = "sel_depth" if (rs or {}).get("sel_depth") is not None else "depth_env"
    cand = []
    for f in files:
        rr = [r for r in json.load(open(f)) if _ok(r)]
        rr.sort(key=lambda r: r["obj"]); cand += [dict(r, _file=os.path.basename(f)) for r in rr[:k_run] if not r["tag"].endswith("-g0-x0")]
    for r in cand: r["xfit"]["obj_"] = r["obj"]
    okd = [r for r in cand if rs is None or r["xfit"][dkey] <= rs[dkey] + 1e-9]
    pool = sorted(okd, key=lambda r: (_selkey(r["xfit"]), r["obj"])) + sorted([r for r in cand if r not in okd], key=lambda r: (_selkey(r["xfit"]), r["obj"]))
    keep = []
    for r in pool:
        if all(max(abs(float(r["params"].get(k, BEST[k])) - float(q["params"].get(k, BEST[k]))) / FREE[k][0] for k in FREE) >= dist for q in keep): keep.append(r)
        if len(keep) == n: break
    os.makedirs(outdir, exist_ok=True); out = []
    if rs: print("verified x0:", _line(ref[0]))
    for j, r in enumerate(keep, 1):
        x = r["xfit"]; d = dict(tag=r["tag"], file=r["_file"], obj=r["obj"], params=r["params"], full=full(r["params"]), xfit_summary={k: x.get(k) for k in (
            "env_near1", "env60_near1", "env_gap", "env60_gap", "sel_near1", "sel60_near1", "sel_mean_near1", "sel_gap", "sel60_gap", "depth_env", "sel_depth",
            "g60_near", "claim_pen", "depth_pen", "cam")}, depth_key=dkey, depth_ok=r in okd, n_candidates=len(cand), n_depth_ok=len(okd))
        json.dump(d, open(os.path.join(outdir, f"pick{j}.json"), "w"), indent=1, default=float); out.append(d)
        print(f"pick{j}", _line(r), "depth-ok", r in okd)
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
    if which == "BEST": return full({})                      # the verified config AS VERIFIED
    d = json.load(open(which)); return full(d.get("params", d))


def rescore(which, outp):
    """fit env FAST -> wear env EXACT (frozen) and fit Bench(60,160) FAST -> wear env EXACT, continuity with fresh-pose edges, priced"""
    assert os.environ.get("CB_EXACT") == "1"
    P = params_of(which); Pp, pinfo = priced(P); t = time.time()
    Bf = EB.bench("env", exact=False); assert Bf.mode == "fast"
    Bf.reset(); r1, M1 = SN._report(Bf, Pp); fit = score(M1, Bf)
    Bw = EB.bench("env", exact=True); assert Bw.mode == "exact"
    M, r = frozen_on(M1, Bw); wear = score(M, Bw)
    old = os.environ.pop("CB_EXACT", None)
    try: B60 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    B60.reset(); r6, M6 = SN._report(B60, Pp); Bw2 = EB.bench("env", exact=True); M6w, r6w = frozen_on(M6, Bw2); wear60 = score(M6w, Bw2)
    out = dict(which=which, params=P, priced=Pp, price=pinfo, fit_env_fast=fit, wear_env_exact=wear, fit60_wear_env_exact=wear60, why=r.get("why"),
               why60=r6w.get("why"), cam=r1.get("cam"), cam60=r6.get("cam"), margin=KIT.FOLD_MARGIN, secs=round(time.time() - t, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    sm = lambda w: {k: w[k] for k in ("gap", "near1", "near2", "reach", "inband14", "contact")}
    print(json.dumps(dict(which=which, fit=sm(fit), wear=sm(wear), wear60=sm(wear60), depth=wear["depth"], depth60=wear60["depth"], th=wear["th"].get("min"),
                          conn=wear.get("conn"), secs=out["secs"]), default=float), flush=True)


def _dump_bench(M, B):
    """= tools/alignment_paired.py _dump_bench (the per-pose dump format of the alignment auditor)"""
    n = len(B.idx); cmin = getattr(M, "cmin", {}) or {}; out = []
    for i in range(n):
        p = B.poses[i]; r = B.res[i]; e = r is not None
        mm = float(np.min(r)) if e and len(r) else None
        row = dict(i=i, kind=B.kind[i], plane=p.get("plane"), elev=p.get("elev"), axial=p.get("axial"), ev=bool(e),
                   min_mm=None if mm is None else round(mm, 3), cmin=None if i not in cmin else round(float(cmin[i]), 3),
                   taken=bool(e and mm is not None and mm >= 0), contact=bool(e and mm is not None and mm < 0))
        if B.kind[i] == "clip" and row["taken"]:
            d = np.asarray(r, float); row["ns"] = int(len(d)); row["nib"] = int(((d >= 2) & (d <= 14)).sum())
        out.append(row)
    return out


def ghoff(M, B, mags=(3.0, 5.0), liner=3.0):
    """GH-offset within-liner share (kneeless-roller-knuckle-3r.py redteam_gh, logic copied; u3 = the worn design's hub-3 axis)"""
    OSN = _load("osn_for_slipper_polish", os.path.join(REPO, "docs", "concepts", "models", "offset-skin-normal-3r.py")); Q0 = OSN.rest()["Q0"]
    u3 = np.asarray(M.D.u[2], float); Z = CB._poses_all(); Q = Z["HG"][np.asarray(B.idx)].astype(float)
    dirs = np.array([[x, y, z] for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)], float)
    dirs /= np.linalg.norm(dirs, axis=1)[:, None]; Rr = np.einsum("nij,kj->nik", Q, Q0); ax_arm = np.array([0.0, -1.0, 0.0]); out = {}
    for mg in mags:
        mis = np.einsum("nij,kj->nki", np.eye(3)[None] - Rr, dirs * mg); worst = np.linalg.norm(mis, axis=2).max(1)
        armf = np.einsum("nji,nkj->nki", Q, mis); perp = armf - (armf @ ax_arm)[..., None] * ax_arm; wp = np.linalg.norm(perp, axis=2).max(1)
        kn = np.abs(armf @ u3).max(1)
        out[f"{mg:g}mm"] = dict(within_liner=round(float((worst <= liner).mean()), 3), slide_within_liner=round(float((wp <= liner).mean()), 3),
                                knee_equiv_within_liner=round(float((kn <= liner).mean()), 3), knee_equiv_median=round(float(np.median(kn)), 2),
                                knee_equiv_max=round(float(kn.max()), 2))
    out["n_poses"] = int(len(Q)); out["liner_mm"] = liner; out["u3"] = [round(float(x), 4) for x in u3]
    return out


def claim(fit, wb, which, outp):
    """H.frozen_wear (the verifier's harness, unchanged) with the fit bench swapped when fit == 'env'; th margin, the per-pose
    dump (contact depth), the workspace in-band and the GH-offset share read from the worn model on the worn bench"""
    assert os.environ.get("CB_EXACT") == "1"
    P = params_of(which); Pp, pinfo = priced(P); V.retarget(Pp)
    orig = CB.Bench
    if fit == "env":
        FIT = EB.bench("env", exact=False); assert FIT.mode == "fast"

        def Bench2(n_clip=20, n_ws=20, *a, **k):
            if (n_clip, n_ws) == (60, 160): FIT.reset(); return FIT
            return orig(n_clip, n_ws, *a, **k)
        CB.Bench = Bench2
    ex0 = H.extra_checks; seen = {}

    def ex2(M, Mfit, B):
        o = ex0(M, Mfit, B); seen["n"] = seen.get("n", 0) + 1
        o["th_margin_own_state"] = th_margin(M, B)
        if seen["n"] == 2:                                    # the worn bench (the first call is the fit bench)
            seen["dump"] = _dump_bench(M, B); o["depth"] = depth_of(B); o["ws_inband"] = RL.ws_inband(B)
            try: o["ghoff"] = ghoff(M, B)
            except Exception as e: o["ghoff"] = dict(error=repr(e)[:300])  # noqa: E701
        return o
    H.extra_checks = ex2
    t = time.time()
    try: out = H.frozen_wear(dict(Pp), wb, flood=True)
    finally: CB.Bench = orig; H.extra_checks = ex0
    out.update(fit_protocol=fit, wear=wb, which=which, nominal=P, priced=Pp, price=pinfo, margin=KIT.FOLD_MARGIN, secs=round(time.time() - t, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    if seen.get("dump"):
        json.dump(dict(id="slipper-nose-knuckle-3r", which=which, fit=fit, wear=wb, params=Pp, frozen=out["frozen"], poses=seen["dump"]),
                  open(outp.replace(".json", "_perpose.json"), "w"), default=float)
    cr = out.get("connected") or {}; ex = out["extra"]
    print(json.dumps(dict(which=os.path.basename(which), fit=fit, wear=wb, n=out["n"], margin=KIT.FOLD_MARGIN, pa=pinfo.get("pa_max"), frozen=out["frozen"],
                          corrected=ex.get("corrected"), near1=out["audit"]["gap_near1"], near2=out["audit"]["gap_near2"], minmetal=out["audit"]["near_touch_min_mm"],
                          depth={k: (ex.get("depth") or {}).get(k) for k in ("n", "sum", "max", "below90", "ovh140")}, ws_inband=ex.get("ws_inband"),
                          th=ex["th_margin_own_state"].get("min"), knn=(cr.get("connected_knn") or {}).get("gap"), full=(cr.get("connected_full") or {}).get("gap"),
                          failing=ex.get("poses_failing"), pa_taken=[ex.get("pa_crank_max"), ex.get("pa_horn_max")], dK=[ex.get("dK_taken_max_deg"), ex.get("dK_lim_deg"), ex.get("why_lim")],
                          ghoff={k: (ex.get("ghoff") or {}).get(k) for k in ("3mm", "5mm")}, secs=out["secs"]), default=float), flush=True)


def _cls(r):
    el, pl, ax = float(r["elev"]), float(r["plane"]), float(r["axial"])
    reg = "overhead" if el >= 140 else "across" if (pl >= 100 and el >= 40) else "behind" if (pl < -30 and el > 20) else f"el{int(min(el, 139.9) // 35) * 35}"
    axb = "|ax|>=150" if abs(ax) >= 150 else "ax>=0" if ax >= 0 else "ax<0"
    return reg, axb


def classes(dump_a, dump_b, outp=None):
    """which workspace pose classes a config regains / loses vs another on the same worn bench (per-pose dumps of claim):
    state per pose = taken (metal >= 0) / contact (metal < 0) / lost (not evaluated: fold, slide, continuity)"""
    A = json.load(open(dump_a))["poses"]; Bd = json.load(open(dump_b))["poses"]; assert len(A) == len(Bd)
    st = lambda r: "taken" if r["taken"] else "contact" if r["contact"] else "lost"
    tab = {}
    for ra, rb in zip(A, Bd):
        if ra["kind"] != "ws": continue
        assert abs(ra["elev"] - rb["elev"]) < 1e-6 and abs(ra["plane"] - rb["plane"]) < 1e-6
        for key in (_cls(ra)[0], _cls(ra)[1], "all"):
            t = tab.setdefault(key, dict(n=0, a_taken=0, b_taken=0, a_contact=0, b_contact=0, a_lost=0, b_lost=0, gained=0, lost_new=0))
            t["n"] += 1; sa, sb = st(ra), st(rb); t["a_" + sa] += 1; t["b_" + sb] += 1
            t["gained"] += int(sa != "taken" and sb == "taken"); t["lost_new"] += int(sa == "taken" and sb != "taken")
    for k, t in sorted(tab.items()):
        print(f"{k:10s} n {t['n']:4d} | taken {t['a_taken']:4d} -> {t['b_taken']:4d} | contact {t['a_contact']:3d} -> {t['b_contact']:3d} | "
              f"lost {t['a_lost']:4d} -> {t['b_lost']:4d} | gained {t['gained']:3d} newly lost {t['lost_new']:3d}")
    if outp: json.dump(dict(a=dump_a, b=dump_b, classes=tab), open(outp, "w"), indent=1)
    return tab


def claimjobs(picks_dir, outp, farm_dir="docs/research/slipper_env_polish/farm", protos="env:held,fit60:bench", readings="p,u", who=""):
    """the ONE claim batch (task step 4): the picks + the verified config, each fit env FAST -> held-out EXACT and fit
    Bench(60,160) FAST -> Bench(110,360) EXACT (the verified protocol), at BOTH readings (p = priced: smlo +0.5, margin 5.5,
    stop B at bk1 + bk2 - 5.5; u = unpriced: nominal stops, margin 5 = the verified reading)"""
    pre = f'mkdir -p {farm_dir} && eval "$(python3 tools/env_bench.py use env)" && '
    whos = [("BEST", "BEST")] + [(os.path.basename(f)[:-5], os.path.join(picks_dir, f)) for f in sorted(os.listdir(picks_dir))
                                 if f.startswith("pick") and f.endswith(".json") and "robust" not in f]
    if who: whos = [w for w in whos if w[0] in who.split(",")]
    jobs = []
    for nm, which in whos:
        for pr in protos.split(","):
            fit, wb = pr.split(":")
            for rd in readings.split(","):
                o = f"{farm_dir}/claim_{nm}_{fit}_{wb}_{rd}"
                env = dict(OMP_NUM_THREADS="1", IGL_NUM_THREADS="2", CB_EXACT="1", SN_CELL="lead", CB_FOLD_MARGIN="5.5" if rd == "p" else "5")
                if rd == "u": env["ENVP_NOPRICE"] = "1"
                jobs.append(dict(tag=f"snc-{nm}-{fit}-{wb}-{rd}", cmd=pre + f"python3 tools/slipper_env_polish.py claim {fit} {wb} {which} {o}.json > {o}.log 2>&1; tail -1 {o}.log",
                                 out=[o + "*"], env=env, timeout=3300))
    json.dump(jobs, open(outp, "w"), indent=1); print(len(jobs), "jobs ->", outp)


PREREG_RULE = ("the single CAD pick = the highest-ranked pick (picks: depth-ok on envsel, ranked by the envsel 1 mm mean over the two fits) "
               "whose flank passes the synthesis-robustness check (robust: beta +-1, r_c +-0.25, g +-0.05 on Bench(60,160), priced) - "
               "if none passes, pick1; fixed BEFORE any claim number exists; the other picks are report-only")


def prereg(picks_dir):
    """PRE-REGISTER the single pick (the inband-rssr audit's ruling (ii)) from the picks' envsel ranking + flank robustness"""
    pk = sorted(f for f in os.listdir(picks_dir) if f.startswith("pick") and f.endswith(".json") and "robust" not in f)
    rb = {}
    fr = os.path.join(picks_dir, "robust_picks.json")
    if os.path.exists(fr):
        for r in json.load(open(fr)): rb[os.path.basename(r["which"])] = r
    chosen = None
    for f in pk:
        if rb.get(f, {}).get("ok"): chosen = f; break
    chosen = chosen or (pk[0] if pk else None)
    out = dict(rule=PREREG_RULE, picks=pk, robust={k: {kk: v.get(kk) for kk in ("ok", "n_fail", "min_dK_lim", "dK_need")} for k, v in rb.items()},
               chosen=chosen, chosen_params=json.load(open(os.path.join(picks_dir, chosen)))["params"] if chosen else None,
               t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    json.dump(out, open(os.path.join(picks_dir, "prereg.json"), "w"), indent=1, default=float); print(json.dumps(out, default=float)); return out


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
    elif a[0] == "claimjobs":
        opt = lambda k, d: a[a.index(k) + 1] if k in a else d
        claimjobs(a[1], a[2], protos=opt("--protos", "env:held,fit60:bench"), readings=opt("--readings", "p,u"), who=opt("--who", ""))
    elif a[0] == "prereg": prereg(a[1])
    elif a[0] == "classes": classes(a[1], a[2], a[3] if len(a) > 3 else None)   # classes <dump A> <dump B> [out.json]
    elif a[0] == "robust":                                     # robust <BEST|BEST_am|params.json ...> [--out O.json]: the flank tolerance check on Bench(60,160)
        outp = a[a.index("--out") + 1] if "--out" in a else None; whos = [x for x in a[1:] if x != "--out" and x != outp]; set_pa(); res = []
        assert os.environ.get("CB_EXACT") != "1"
        B = CB.Bench(60, 160)
        for w in whos:
            Pp, _ = priced(params_of(w)); t = time.time(); rb = robust(Pp, B); rb.update(which=w, secs=round(time.time() - t, 1)); res.append(rb)
            print(json.dumps({k: rb[k] for k in ("which", "ok", "n_fail", "min_dK_lim", "dK_need", "secs")}), [(r["k"], r["d"], r["dK_lim"], r["why"], r["ok"]) for r in rb["rows"]], flush=True)
        if outp: json.dump(res, open(outp, "w"), indent=1, default=float)
    else: raise SystemExit(__doc__)
