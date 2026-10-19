#!/usr/bin/env python3
"""FINAL POLISH OF inband-rssr-knuckle-3r (the in-band RSSR K drive, screened 2026-10-17) ON THE ENVELOPE BENCH
(tools/env_bench.py 'env') + the claim wrapper that wears a config with the row's own frozen claim protocol
(docs/concepts/models/inband-rssr-knuckle-3r.py -> longstroke-slipper-knuckle-3r.py _frozen_model: fit FAST, shape frozen,
worn EXACT), with the fit bench swappable, built-stop pricing, the full-grid continuity flood and the per-pose dump.

Adapted from tools/roller_env_polish.py (same objective shape, same continuity law, same gate / picks rules); the row has
no verifier harness yet, so the claim runs the model's own frozen protocol (it reproduces the row's 18.87 / 23.21 when
read unpriced at margin 5: `claim fit60 bench PICK` with ENVP_NOPRICE=1 CB_FOLD_MARGIN=5).

WHY (docs/research/inband_drive.md section 6): every fit-bench search walked the K dyad back to 26 / 38 because
Bench(60,160) holds only 2.5 % of workspace poses with |axial| >= 150 (held out 11.0 %, env 9.3 %): it never sees the
stretched poses a long K dyad wins. So this polish searches on 'env' and starts CMA from the short-dyad pick AND from
long-dyad seeds (K dyad 28-32 / 47-50, kK 1.8-3.0), with the drive's metal real (crank on its ear, radial M2 crank stud).

CLAUDE.md rules carried: search on a representative envelope sample, claim on the held-out set; near-touch objective
(metal < 1 mm = contact; 2 mm report only); continuity (full-grid flood + every fresh env pose joined to the connected grid
by a 2-deg slerp edge to one of its 6 nearest connected nodes, same law); 5-deg margin in the th metric with stops as
variables >= 5.0 priced at +0.5 (smlo + 0.5, the whole reading at CB_FOLD_MARGIN 5.5, K's stop B at
a1max' = min(a1max, bk1 + bk2 - 5.5)); O20 (the model's hubs, unchanged); RSSR transmission >= 48 (PA <= 42 at both ball
ends) and the radial stud's socket cone <= 30 deg (the model's range scan); the knee window may not widen past the pick's
(ang_min >= 25.2189); kinematic only; the held-out split stays held out (env / envsel never touch it: env_bench asserts).

Objective of a free-parameter set p (lower is better):
  P = PICK + p; P' = priced(P)
  a = fit P' on env FAST, score env in-sample (continuity knock-out) -> near-touch gap (1 mm)
  b = fit P' on Bench(60,160) FAST, wear that shape FROZEN on env FAST (continuity knock-out) -> near-touch gap (1 mm)
  obj = (a + b) / 2 + claim-fit guard max(0, g60 - a - 3) + depth guard DEPTH_W * max(0, depth - REF_DEPTH)
        + 100 if dishonest (RSSR open, drive idle, knee moved) or a taken pose's own-state th margin < the reading's margin
  logged: both shapes worn FROZEN on envsel (independent draw) -> the pick-selection numbers.

    CB_FOLD_MARGIN=5.5 python3 tools/inband_env_polish.py cma --x0 '{..}' --label L --out O.json [--sigma .. --budget-s ..]
    CB_FOLD_MARGIN=5.5 python3 tools/inband_env_polish.py score OUT.json '[{"tag":..,"params":{..}}]' [--jobs 2]
    python3 tools/inband_env_polish.py gate O1.json [..] | best .. | picks .. --out DIR
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 python3 tools/inband_env_polish.py rescore <PICK|params.json> OUT.json
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 python3 tools/inband_env_polish.py claim <fit60|env> <bench|held> <PICK|ROBUST|params.json> OUT.json
    python3 tools/inband_env_polish.py claimjobs <picks dir> jobs_claim.json
    python3 tools/inband_env_polish.py robust <PICK|params.json ..> [--out O.json]   knife edge (+-1 deg / +-0.25 mm, one at a time, Bench(60,160))
  PICK = the row's leak-free pick cma3 p (docs/research/inband_drive/picks.json); ROBUST = its robust build (r_h +0.25, eta +1).
"""
import importlib.util, json, math, os, sys, time, traceback
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import env_bench as EB                                       # noqa: E402
EB.install()                                                 # fresh poses appended BEFORE any model loads poses
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


IB = _load("inband_for_envpolish", os.path.join(REPO, "docs", "concepts", "models", "inband-rssr-knuckle-3r.py"))
LS, RL, PK, S, SC = IB.LS, IB.RL, IB.PK, IB.S, IB.SC
PICK = dict(json.load(open(os.path.join(REPO, "docs", "research", "inband_drive", "picks.json")))["primary_cma3_p"]["params"])
BEST = dict(IB.PARAMS, **PICK)                               # the row's pick on the model's full parameter set
ANG_MIN_LO = float(BEST["ang_min"])                          # 25.2189: the knee window may not widen past the pick's
CLAIM_TOL = 3.0
DEPTH_W = float(os.environ.get("ENVP_DEPTH_W", "0.1"))
FROZEN_ATTRS = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info")
# free parameters: (CMA scale, lo, hi); ranges = the model's clamps (LS._clamp rssr, IB._clamp); stops >= 5.0 (the user's floor)
FREE = {"bk1": (1.0, 26.0, 34.0), "bk2": (2.0, 38.0, 56.0), "a1max": (2.0, 40.0, 85.0), "kK": (0.25, 0.8, 3.5),
        "La": (1.5, 12.0, 26.0), "s_arm": (0.3, 4.0, 6.0), "r_h": (0.8, 13.0, 22.0), "beta": (8.0, -180.0, 0.0), "gam": (8.0, -60.0, 60.0),
        "hl": (0.4, 0.0, 3.15), "zc": (0.4, 0.0, 3.15), "eta": (6.0, -60.0, 60.0), "r_lobe": (0.3, 7.0, 8.5),
        "smhi": (1.5, 5.0, 30.0), "smlo": (0.5, 5.0, 15.0),
        "az1": (2.0, None, None), "el1": (1.0, None, None), "az2": (2.0, None, None), "el2": (1.0, None, None),
        "wd": (3.0, None, None), "wa": (1.5, None, None), "b3": (0.03, 0.2, 0.6), "ang_min": (1.0, ANG_MIN_LO, 45.0),
        "lc": (1.5, 15.0, 40.0), "phib": (5.0, None, None)}
FIXED = dict(clay=1, bl_c=2, bl_h=0, zr=0.0, law_in="lin", chain="free", cprog=0.0, near2=1)


def full(p):
    P = dict(BEST); P.update({k: float(v) for k, v in p.items() if k in FREE}); P.update(FIXED)
    P["smhi"] = max(5.0, float(P["smhi"])); P["smlo"] = max(5.0, float(P["smlo"])); P["ang_min"] = max(ANG_MIN_LO, float(P["ang_min"]))
    P["a1max"] = min(float(P["a1max"]), float(P["bk1"]) + float(P["bk2"]) - 5.0)   # the model's own clamp (stop B at the K dyad's 5 margin)
    return P


def priced(P):
    """the worst built pairing: folded dowel smlo + 0.5, stop B at the K dyad's 5.5 margin, the reading at CB_FOLD_MARGIN 5.5"""
    P2 = dict(P)
    if os.environ.get("ENVP_NOPRICE") == "1": return P2, dict(why="unpriced reading (nominal stops)", margin=KIT.FOLD_MARGIN)
    P2["smlo"] = round(max(5.0, float(P["smlo"])) + 0.5, 4)
    P2["a1max"] = round(min(float(P["a1max"]), float(P["bk1"]) + float(P["bk2"]) - max(5.0, KIT.FOLD_MARGIN)), 4)
    return P2, dict(smlo_nominal=float(P["smlo"]), smlo_priced=P2["smlo"], smhi=float(P["smhi"]), a1max_nominal=float(P["a1max"]),
                    a1max_priced=P2["a1max"], margin=KIT.FOLD_MARGIN)


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
    """the claim protocol's frozen wear (LS._frozen_model's Frozen class, on this row's IBModel)"""
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(IB.IBModel):
        def fit(self):
            for a in FROZEN_ATTRS:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    Bw.reset(); M = Frozen(Bw, P2); r = M.run(); return M, r


def _rep(B, P):
    B.reset(); return IB._report(B, dict(P))


def cam_of(M, r):
    info = getattr(M, "_sc_info", None) or {}
    c = dict(r.get("cam") or {})
    c.update({k: info.get(k) for k in ("dK_lim", "why_lim", "trans_min_taken", "tilt_max_taken", "tilt_max_range", "rod_len", "phi_max_taken", "boss_level", "pivot_off_hub2_mm")})
    return c


# ---------------------------------------------------------------------------------------------------------------------
_W = {}


def _honest(r):
    return bool(r.get("honest", True)) and not (r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"))


def obj_of(p):
    Benv, Bsel, B60 = _W["B"]; P = full(p); Pp, pinfo = priced(P); out = dict(price=pinfo); t0 = time.time()
    r, M = _rep(Benv, Pp)
    if not np.asarray(M.kin_ok).any(): out.update(obj=400.0, nothing_closes=True); return out
    e = score(M, Benv); out["env"] = e; out["cam"] = cam_of(M, r)
    nosel = Bsel is None
    if not nosel: Mf, _ = frozen_on(M, Bsel); sel = score(Mf, Bsel); out["sel"] = sel
    r6, M6 = _rep(B60, Pp)
    if not np.asarray(M6.kin_ok).any(): out.update(obj=400.0, nothing_closes_60=True); return out
    g60 = PK.audit(M6, B60)["gap_near1"]; out["cam60"] = cam_of(M6, r6)
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
    if os.environ.get("ENVP_ROBUST") == "1" and honest and not marg_bad:
        rb = robust(Pp, B60); out["robust"] = {k: rb[k] for k in ("ok", "n_fail", "min_dK_lim", "dK_need")}
        rob_pen = float(os.environ.get("ENVP_ROBUST_W", "2")) * rb["n_fail"]
    out["robust_pen"] = rob_pen
    out["obj"] = round(0.5 * (a + b) + out["claim_pen"] + out["depth_pen"] + (0.0 if honest else 100.0) + (100.0 if marg_bad else 0.0) + rob_pen, 3)
    out.update(env_near1=a, env60_near1=b, env_gap=e["gap"], env60_gap=e60["gap"], env_near2=e["near2"], env60_near2=e60["near2"], secs=round(time.time() - t0, 1))
    if not nosel:
        out.update(sel_near1=sel["near1"], sel60_near1=s60["near1"], sel_gap=sel["gap"], sel60_gap=s60["gap"],
                   sel_depth=round(0.5 * (sel["depth"]["sum"] + s60["depth"]["sum"]), 3),
                   sel_mean_near1=round(0.5 * (sel["near1"] + s60["near1"]), 3), sel_worst_near1=max(sel["near1"], s60["near1"]))
    return out


# the knife edge of the row's red team: +-1 deg on the angles, +-0.25 mm on the lengths, one at a time (Bench(60,160) fit)
ROBUST_TOL = {"beta": 1.0, "gam": 1.0, "eta": 1.0, "La": 0.25, "r_h": 0.25, "s_arm": 0.25, "hl": 0.25, "zc": 0.25, "r_lobe": 0.25}


def robust(Pp, B, dK_need=None, jump=5.0):
    """every neighbour must close (honest, poses taken), keep a drive range >= the nominal's taken dK - 1 deg, and not lose
    more than `jump` near-touch points against the nominal on the fit bench (the r_h -0.25 'every pose lost' knife edge)"""
    r0, M0 = _rep(B, Pp); g0 = PK.audit(M0, B)["gap_near1"] if np.asarray(M0.kin_ok).any() else 400.0
    if dK_need is None:
        dK = np.degrees(np.abs(np.asarray(M0.dK, float))); tk = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
        dK_need = float(dK[tk].max()) if tk else 0.0
    rows = []; ok = True; mins = []
    for k, d in ROBUST_TOL.items():
        lo, hi = FREE[k][1], FREE[k][2]
        for s in (-1, 1):
            q = dict(Pp); q[k] = float(min(max(float(Pp[k]) + s * d, lo), hi))
            r, M = _rep(B, q); cam = cam_of(M, r); lim = float(cam.get("dK_lim") or 0.0)
            closes = bool(np.asarray(M.kin_ok).any()); g = PK.audit(M, B)["gap_near1"] if closes else 400.0
            good = _honest(r) and closes and lim >= dK_need - 1.0 and g <= g0 + jump
            ok &= good; mins.append(lim)
            rows.append(dict(k=k, d=s * d, dK_lim=round(lim, 2), why=cam.get("why_lim"), near1=g, tilt=cam.get("tilt_max_taken"), honest=_honest(r), ok=bool(good)))
    return dict(ok=bool(ok), n_fail=int(sum(not r["ok"] for r in rows)), min_dK_lim=round(min(mins), 2) if mins else None,
                dK_need=round(dK_need, 2), near1_nominal=g0, rows=rows)


def _benches():
    if os.environ.get("ENVP_SMOKE"):                         # local smoke test: exact, a few poses of each bench
        n = int(os.environ["ENVP_SMOKE"]); out = []
        for B in (EB.bench("env", exact=True), EB.bench("envsel", exact=True)):
            sel = [i for i, k in enumerate(B.kind) if k == "clip"][:n] + [i for i, k in enumerate(B.kind) if k == "ws"][::25][:n]
            B.idx = np.asarray(B.idx)[sel]; B.kind = [B.kind[i] for i in sel]; B.clip = [B.clip[i] for i in sel]; B.poses = [B.poses[i] for i in sel]
            B.res = [None] * len(sel); out.append(B)
        return tuple(out) + (CB.Bench(60, 160),)
    return (EB.bench("env"), None if os.environ.get("ENVP_NOSEL") == "1" else EB.bench("envsel"), CB.Bench(60, 160))


def _init(plname=None):
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    if "B" not in _W: _W["B"] = _benches()
    if not os.environ.get("ENVP_SMOKE") and any(B.mode != "fast" for B in _W["B"] if B is not None):
        raise RuntimeError("env / envsel / Bench(60,160) not on the fast grid (link: eval \"$(python3 tools/env_bench.py use env)\")")


def _eval(arg):
    tag, p = arg; t0 = time.time()
    try:
        r = obj_of(p)
        return dict(tag=tag, params=p, obj=r["obj"], xfit=r, secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-1500:], secs=round(time.time() - t0, 1))


class Plugin:
    name = "inband_env"; FREE = {k: (s, lo, hi, k) for k, (s, lo, hi) in FREE.items()}

    def base(self): return dict(BEST)


def run_cma(argv):
    import argparse
    X = _load("crossfit_polish_for_inband", os.path.join(REPO, "tools", "crossfit_polish.py"))
    X.PLUGINS["inband_env"] = Plugin; X._init = _init; X._eval = _eval
    assert abs(KIT.FOLD_MARGIN - 5.5) < 1e-9 or os.environ.get("ENVP_NOPRICE") == "1", "run the polish at CB_FOLD_MARGIN=5.5"
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--plugin", default="inband_env")
    ap.add_argument("--x0", default="{}"); ap.add_argument("--fixed", default="")
    ap.add_argument("--label", required=True); ap.add_argument("--out", required=True); ap.add_argument("--state", default="")
    ap.add_argument("--state-out", default=""); ap.add_argument("--sigma", type=float, default=0.4)
    ap.add_argument("--popsize", type=int, default=8); ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--budget-s", type=float, default=2400); ap.add_argument("--max-gen", type=int, default=400)
    ap.add_argument("--max-evals", type=int, default=900); ap.add_argument("--patience", type=int, default=12)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args(argv)
    _init()
    if "ENVP_REF_DEPTH" not in os.environ:                   # the pick's own (priced) env depth reading: the guard's reference
        r0 = _eval(("ref-pick", {}))
        os.environ["ENVP_REF_DEPTH"] = str((r0.get("xfit") or {}).get("depth_env", 1e9))
        print("[ref] pick obj", r0["obj"], "env near1 / env60 near1", (r0.get("xfit") or {}).get("env_near1"), (r0.get("xfit") or {}).get("env60_near1"),
              "depth", os.environ["ENVP_REF_DEPTH"], r0["secs"], "s", r0.get("error", ""), flush=True)
    X.cma(a)


def score_list(outp, items, jobs):
    import multiprocessing as mp
    _init(); pool = mp.get_context("fork").Pool(jobs, initializer=_init); t = time.time()
    res = pool.map(_eval, [(it.get("tag", f"s{i}"), it["params"]) for i, it in enumerate(items)]); pool.close()
    json.dump(res, open(outp, "w"), indent=1, default=float)
    for r in res:
        x = r.get("xfit") or {}
        print(r["tag"], "obj", r["obj"], "env n1 / env60 n1", x.get("env_near1"), x.get("env60_near1"), "sel n1 / sel60 n1", x.get("sel_near1"), x.get("sel60_near1"),
              "depth", x.get("depth_env"), x.get("sel_depth"), "g60", x.get("g60_near"), "th", (x.get("env") or {}).get("th", {}).get("min"),
              "dKlim", (x.get("cam") or {}).get("dK_lim"), r.get("error", ""), r["secs"], "s", flush=True)
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
            f"tilt {(g('cam') or {}).get('tilt_max_taken')} dKlim {(g('cam') or {}).get('dK_lim')}")


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


# ---------------------------------------------------------------------------------------------------------------------
def params_of(which):
    if which == "PICK": return full({})                      # the row's pick (cma3 p)
    if which == "ROBUST": return full({"r_h": float(BEST["r_h"]) + 0.25, "eta": float(BEST["eta"]) + 1.0})   # the row's robust build
    d = json.load(open(which)); return full(d.get("params", d))


def spring(dK_deg, kK):
    """the K clock spring felt at J2 (the lead's 0.08 N.m + 0.015 N.m/rad, through the law's ratio kK) vs R17 (<= 1 N.m, <= 5 N)"""
    t = float(kK) * (0.08 + 0.015 * math.radians(float(dK_deg)))
    return dict(kK=round(float(kK), 4), dK_taken_deg=round(float(dK_deg), 2), J2_Nm=round(t, 3), cuff_N_150=round(t / 0.150, 2), cuff_N_120=round(t / 0.120, 2),
                share_1Nm=round(t / 1.0, 3), share_5N=round(t / 0.120 / 5.0, 3))


def _fit_bench(fit):
    if fit == "env":
        B = EB.bench("env", exact=False); assert B.mode == "fast"; return B
    old = os.environ.pop("CB_EXACT", None)
    try: B = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    assert B.mode == "fast"; return B


def _wear_bench(wb):
    assert os.environ.get("CB_EXACT") == "1"
    if wb == "held":
        PV = _load("pk_polish_v_inband_env", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py")); return PV.held_bench()
    if wb == "env": return EB.bench("env", exact=True)
    return CB.Bench(n_clip=110, n_ws=360)


def rescore(which, outp):
    """fit env FAST -> wear env EXACT (frozen) and fit Bench(60,160) FAST -> wear env EXACT, continuity with fresh-pose edges, priced"""
    P = params_of(which); Pp, pinfo = priced(P); t = time.time()
    Bf = _fit_bench("env"); r1, M1 = _rep(Bf, Pp); fit = score(M1, Bf)
    Bw = _wear_bench("env"); M, r = frozen_on(M1, Bw); wear = score(M, Bw)
    B60 = _fit_bench("fit60"); r6, M6 = _rep(B60, Pp); Bw2 = _wear_bench("env"); M6w, r6w = frozen_on(M6, Bw2); wear60 = score(M6w, Bw2)
    out = dict(which=which, params=P, priced=Pp, price=pinfo, fit_env_fast=fit, wear_env_exact=wear, fit60_wear_env_exact=wear60, why=r.get("why"),
               why60=r6w.get("why"), cam=cam_of(M1, r1), cam60=cam_of(M6, r6), margin=KIT.FOLD_MARGIN, secs=round(time.time() - t, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    sm = lambda w: {k: w[k] for k in ("gap", "near1", "near2", "reach", "inband14", "contact")}
    print(json.dumps(dict(which=which, fit=sm(fit), wear=sm(wear), wear60=sm(wear60), depth=wear["depth"], depth60=wear60["depth"], th=wear["th"].get("min"),
                          conn=wear.get("conn"), secs=out["secs"]), default=float), flush=True)


def claim(fit, wb, which, outp):
    """the row's frozen claim protocol (fit FAST -> shape frozen -> worn EXACT) with the fit bench swappable; static and connected
    (full-grid flood + fresh-pose edges) readings, near-touch 1 / 2 mm, th margin (own state), contact depth, per-pose dump,
    raised-arm in-band, the RSSR's cone / transmission / range, the spring vs R17"""
    assert os.environ.get("CB_EXACT") == "1"
    P = params_of(which); Pp, pinfo = priced(P); t = time.time()
    FIT = _fit_bench(fit); r1, M1 = _rep(FIT, Pp)
    fitr = {k: r1.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "gap_near1", "gap_near2")}
    W = _wear_bench(wb)
    if os.environ.get("ENVP_SMOKE"):
        n = int(os.environ["ENVP_SMOKE"]); sel = [i for i, k in enumerate(W.kind) if k == "clip"][:n] + [i for i, k in enumerate(W.kind) if k == "ws"][::40][:n]
        W.idx = np.asarray(W.idx)[sel]; W.kind = [W.kind[i] for i in sel]; W.clip = [W.clip[i] for i in sel]; W.poses = [W.poses[i] for i in sel]; W.res = [None] * len(sel)
    M, r = frozen_on(M1, W)
    static = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    au0 = PK.audit(M, W)
    res0 = list(W.res); _, _, drop, ci = conn_full(M, W)
    for j in drop: W.res[j] = None
    rep = W.report(); au = PK.audit(M, W)
    final = {k: rep[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    final.update(gap_near1=au["gap_near1"], gap_near2=au["gap_near2"], min_metal_mm=au["near_touch_min_mm"])
    thm = th_margin(M, W); dep = depth_of(W); wsi = RL.ws_inband(W); dump = _dump_bench(M, W)
    why = r.get("why")
    ws = np.array(W.kind) == "ws"; elev = np.array([W.poses[j]["elev"] for j in range(len(W.idx))])
    tk = np.array([W.res[j] is not None and float(np.min(W.res[j])) >= 0 for j in range(len(W.idx))])
    dK = np.degrees(np.abs(np.asarray(M.dK, float))); dKt = float(dK[tk].max()) if tk.any() else 0.0
    cam = cam_of(M1, r1)
    out = dict(row=IB.ID, fit_protocol=fit, wear=wb, which=which, nominal=P, priced=Pp, price=pinfo, margin=KIT.FOLD_MARGIN, n=len(W.idx), fit_fast=fitr,
               static=static, static_near=dict(gap_near1=au0["gap_near1"], gap_near2=au0["gap_near2"]), final=final, conn=ci, why=why,
               overhead=dict(ws=int((ws & (elev >= 140)).sum()), taken=int((ws & (elev >= 140) & tk).sum())), th_margin=thm, depth=dep, ws_inband=wsi,
               cam=cam, dK_taken_max=round(dKt, 2), spring=spring(dKt, Pp["kK"]), split=RL.contact_split(M, W), secs=round(time.time() - t, 1))
    W.res = res0
    json.dump(out, open(outp, "w"), indent=1, default=float)
    json.dump(dict(id=IB.ID, which=which, fit=fit, wear=wb, params=Pp, frozen=final, poses=dump), open(outp.replace(".json", "_perpose.json"), "w"), default=float)
    print(json.dumps(dict(which=os.path.basename(which), fit=fit, wear=wb, n=out["n"], margin=KIT.FOLD_MARGIN, static=static["gap"], final=final,
                          depth={k: dep.get(k) for k in ("n", "sum", "max", "below90", "ovh140")}, th=thm.get("min"), conn=ci, why=why,
                          dK=[round(dKt, 2), cam.get("dK_lim"), cam.get("why_lim")], tilt=cam.get("tilt_max_taken"), trans=cam.get("trans_min_taken"),
                          spring=out["spring"], ws_inband=wsi, secs=out["secs"]), default=float), flush=True)


def claimjobs(picks_dir, outp, farm_dir="docs/research/inband_env_polish/farm"):
    """the ONE claim batch: the picks + the row's pick (PICK, priced) each fit env FAST -> held EXACT, fit Bench(60,160) FAST ->
    Bench(110,360) EXACT (the verified protocol) and fit Bench(60,160) -> held (the CAD shape's held-out number); plus the
    pick unpriced at margin 5 on the verified protocol and held out (must reproduce the row's 18.87 / 23.21) and the robust build"""
    pre = f'mkdir -p {farm_dir} && eval "$(python3 tools/env_bench.py use env)" && eval "$(python3 tools/env_bench.py use envsel)" && '
    whos = [("PICK", "PICK")] + [(os.path.basename(f)[:-5], os.path.join(picks_dir, f)) for f in sorted(os.listdir(picks_dir)) if f.startswith("pick") and f.endswith(".json")]
    jobs = []; envb = dict(OMP_NUM_THREADS="1", IGL_NUM_THREADS="2", CB_EXACT="1", CB_FOLD_MARGIN="5.5", CB_QUIET_EXACT="1")
    for nm, which in whos:
        for fit, wb in (("env", "held"), ("fit60", "bench"), ("fit60", "held")):
            o = f"{farm_dir}/claim_{nm}_{fit}_{wb}"
            jobs.append(dict(tag=f"ibc-{nm}-{fit}-{wb}", cmd=pre + f"python3 tools/inband_env_polish.py claim {fit} {wb} {which} {o}.json > {o}.log 2>&1; tail -c 1500 {o}.log",
                             out=[o + "*"], env=envb, timeout=3300))
    for fit, wb in (("fit60", "bench"), ("fit60", "held")):
        o = f"{farm_dir}/claim_PICKnominal_{fit}_{wb}"
        jobs.append(dict(tag=f"ibc-PICKnom-{fit}-{wb}", cmd=pre + f"python3 tools/inband_env_polish.py claim {fit} {wb} PICK {o}.json > {o}.log 2>&1; tail -c 1500 {o}.log",
                         out=[o + "*"], env=dict(envb, CB_FOLD_MARGIN="5", ENVP_NOPRICE="1"), timeout=3300))
    o = f"{farm_dir}/claim_ROBUST_fit60_held"
    jobs.append(dict(tag="ibc-ROBUST-fit60-held", cmd=pre + f"python3 tools/inband_env_polish.py claim fit60 held ROBUST {o}.json > {o}.log 2>&1; tail -c 1500 {o}.log",
                     out=[o + "*"], env=envb, timeout=3300))
    json.dump(jobs, open(outp, "w"), indent=1); print(len(jobs), "jobs ->", outp)


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
    elif a[0] == "claimjobs": claimjobs(a[1], a[2])
    elif a[0] == "classes": classes(a[1], a[2], a[3] if len(a) > 3 else None)
    elif a[0] == "robust":
        outp = a[a.index("--out") + 1] if "--out" in a else None; whos = [x for x in a[1:] if x != "--out" and x != outp]; res = []
        B = _fit_bench("fit60")
        for w in whos:
            Pp, _ = priced(params_of(w)); t = time.time(); rb = robust(Pp, B); rb.update(which=w, secs=round(time.time() - t, 1)); res.append(rb)
            print(json.dumps({k: rb[k] for k in ("which", "ok", "n_fail", "min_dK_lim", "dK_need", "near1_nominal", "secs")}),
                  [(r["k"], r["d"], r["dK_lim"], r["near1"], r["ok"]) for r in rb["rows"] if not r["ok"]], flush=True)
        if outp: json.dump(res, open(outp, "w"), indent=1, default=float)
    else: raise SystemExit(__doc__)
