#!/usr/bin/env python3
"""POLISH 2 of skin-normal-3r-pin-knee under the night rules (CLAUDE.md 2026-10-16: "Search on the near-touch gap, and
treat fold stops as a design variable", fold margin 5 = the lower bound, O20 hubs only, overhead clip frames kept).

Drives tools/knee_polish.py UNCHANGED (its verifier-corrected evaluation, its CMA-ES, its frozen protocols) and adds:

  * the J2 FOLD STOPS as design variables: m_lo / m_hi (deg) = hard stops at the two J2 window edges, the J1-J3 angle
    kept in [|a1 - a2| + m_lo, min(a1 + a2, 360 - a1 - a2) - m_hi]. Implemented as a wrapper on the model's spherical IK
    (seed-offset-3r-slides Design.ik, which already applies the kit rule FOLD_MARGIN = 5): the wrapper can only NARROW
    the window (m < 5 changes nothing), so the user's 5 deg stays the floor. Everything downstream (knee reference at mid
    drift over the taken poses, continuity, fit, audit) sees the narrowed window - a stop is a real J2 hard stop.
  * the overhead constraint: every Raise-overhead clip frame at elevation >= 140 followed. Objective = the near-touch gap
    (metal < 1 mm = contact, the verifier's corrected set) + OH_PEN per overhead clip frame lost (follow >= 0.95 makes
    such losses free in the gap; the constraint keeps them). Logged: gap, near-touch gap, overhead follow / reach, the
    knee's distance to its window edge over the overhead poses taken (the H1 red-team edge).

    python3 tools/knee_polish2.py cma  ... (tools/knee_polish.py cma options; FREE gains m_lo / m_hi)
    python3 tools/knee_polish2.py scan OUT 'LIST' [--jobs 2]
    python3 tools/knee_polish2.py claim PROTO OUT 'PARAMS'   PROTO fitbig | held | fit60: the polish-verifier harness
        (docs/concepts/verify/skin-normal-3r-pin-knee-polish.py, imported unchanged) with the stop wrapper installed
        on ITS model instance, plus overhead clip follow and the knee overhead edge. CB_EXACT=1 for the exact wear bench.
    python3 tools/knee_polish2.py log RUN1.json [...]          merge rows into the sweep log, stage polish2-m5-<stream>
"""
import importlib.util, json, math, os, sys, time, traceback
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import knee_polish as KP                                     # noqa: E402
import concept_bench as CB                                   # noqa: E402

STOP_FLOOR = 5.0          # the user's fold margin (2026-10-16 05:50 UTC): lower bound of every stop
OH_PEN = float(os.environ.get("KP2_OH_PEN", 2.0))           # gap points per overhead clip frame (elev >= 140) not followed
FREE2 = dict(KP.FREE)
FREE2["m_lo"] = (1.5, STOP_FLOOR, 20.0, "J2 hard stop at the small-angle window edge (deg past |a1 - a2|); >= 5 = the user's margin")
FREE2["m_hi"] = (1.5, STOP_FLOOR, 20.0, "J2 hard stop at the large-angle window edge (deg short of a1 + a2); >= 5 = the user's margin")


def install_stops(S):
    """wrap S.Design.ik (S = the seed module instance used by a loaded pin-knee model): narrow the fold window to the
    design's stops m_lo / m_hi. Idempotent."""
    if getattr(S.Design.ik, "_kp2", False): return
    orig = S.Design.ik

    def ik(self, Q):
        q, ok, X1, X2, X3, s = orig(self, Q)
        mlo = float(self.p.get("m_lo", STOP_FLOOR)); mhi = float(self.p.get("m_hi", STOP_FLOOR))
        if len(Q) and (mlo > S.SING + 1e-9 or mhi > S.SING + 1e-9):
            u1, u3 = self.u[0], self.u[2]; w = np.asarray(Q) @ u3
            th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
            a1, a2 = math.degrees(self.A[0]), math.degrees(self.A[1])
            ok = ok & (th >= abs(a1 - a2) + max(mlo, S.SING)) & (th <= min(a1 + a2, 360 - a1 - a2) - max(mhi, S.SING))
        return q, ok, X1, X2, X3, s
    ik._kp2 = True; S.Design.ik = ik


def _patch():
    V = KP.verifier(); install_stops(V.MK.S); return V


def knee_edge_overhead(M, B, P):
    """min distance (deg) of the knee angle to its window edges [ang_min, 180 - ang_min] over the taken poses with
    elevation >= 140 (None if none taken)"""
    tk = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0 and B.poses[i]["elev"] >= 140]
    if not tk: return None
    ang = M.K["ang"][tk]; am = float(P["ang_min"])
    return round(float(np.minimum(ang - am, 180 - am - ang).min()), 2)


def evaluate2(B, p):
    """tools/knee_polish.py evaluate (verifier-corrected set + audit), plus the overhead constraint and the stops"""
    _patch(); V = KP.verifier(); MK = V.MK; P = KP.base_params(); P.update(p)
    rep, M, aud = KP.evaluate(B, P)
    if aud is None:
        rep.update(oh_follow=0.0, oh_clip=None, oh_lost=None, oh_reach=0.0, oh_knee_edge=None, obj2=rep["gap_near1"] + 50.0)
        return rep
    # the verifier's corrected set again (KP.evaluate restores B.res): overhead split on it
    ex, bad = V.extra_checks(M, B); res0 = list(B.res)
    for i in bad: B.res[i] = None
    a2 = MK.audit(M, B); oh = a2["overhead140"]; edge = knee_edge_overhead(M, B, P)
    th_taken = None
    tk = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    if tk:
        D = M.D; w = M.Q[tk] @ D.u[2]; th = np.degrees(np.arccos(np.clip(w @ D.u[0], -1, 1)))
        a1, a2d = math.degrees(D.A[0]), math.degrees(D.A[1])
        lo, hi = abs(a1 - a2d), min(a1 + a2d, 360 - a1 - a2d)
        th_taken = dict(lo_margin=round(float(th.min() - lo), 2), hi_margin=round(float(hi - th.max()), 2), window=[round(lo, 2), round(hi, 2)])
    B.res = res0
    lost = int(round(oh["clip"] * (1 - (oh["follow"] or 0.0)))) if oh["clip"] else 0
    rep.update(oh_follow=oh["follow"], oh_clip=oh["clip"], oh_lost=lost, oh_reach=oh["reach"], oh_inband14=oh["inband14"], oh_knee_edge=edge,
               fold_taken=th_taken, m_lo=float(P.get("m_lo", STOP_FLOOR)), m_hi=float(P.get("m_hi", STOP_FLOOR)),
               obj2=round(float(rep["gap_near1"]) + OH_PEN * lost, 2))
    return rep


def _init2(nc, nw):
    os.environ.setdefault("OMP_NUM_THREADS", "1"); _patch(); KP._W["B"] = CB.Bench(nc, nw)


def _eval2(arg):
    tag, p, objk = arg; t0 = time.time()
    try:
        rep = evaluate2(KP._W["B"], KP.snap(p))
        obj = float(rep["obj2"]) if objk == "near1" else float(rep["gap"]) + OH_PEN * float(rep.get("oh_lost") or 0)
        return dict(tag=tag, params=p, report=rep, obj=obj, secs=round(time.time() - t0, 1))
    except Exception as e:                                                       # noqa: BLE001
        return dict(tag=tag, params=p, obj=400.0, error=repr(e), trace=traceback.format_exc()[-800:], secs=round(time.time() - t0, 1))


def use_kp2():
    """point tools/knee_polish.py's CMA / scan at this file's evaluation and free set"""
    KP.FREE = FREE2; KP._eval = _eval2; KP._init = _init2; _patch()


# ---------------------------------------------------------------------------------------------------------------------
# continuity rule (CLAUDE.md 2026-10-16): reach scored on the set a CONTINUOUS arm motion reaches from the rest region
def _kin(D, Q, R_tol):
    """kinematic feasibility of the chain + knee at arm orientations Q (n,3,3): fold window with the stops, knee window,
    radial drift <= R_tol, rotation closure < 0.5 deg; and the joint vector (q1, q2, q3' = q3 + phi, pin a, pin b) in deg"""
    q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s)
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol)
    c = (np.einsum("nij,nij->n", X3[0], Q) - 1) / 2; ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    qq = np.degrees(np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"]])
    return ok, qq


def connectivity(M, jump=10.0, step=2.0):
    """flood fill over the WHOLE workspace grid (1432 poses, 15 deg steps in plane / elevation / axial): a node is a
    kinematically feasible orientation; an edge joins grid neighbours when every <= 2-deg slerp frame between them is
    feasible and no joint (incl. the passive knee pins) steps > 10 deg (no branch change, no snap). Seeds: the feasible
    nodes at the lowest elevation (arm at the side). Returns {global pose index: connected} for every ws grid pose."""
    from scipy.spatial.transform import Rotation as Rot, Slerp
    D = M.D; Z = CB._poses_all(); names = list(Z["NAMES"]); ii = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
    HG = Z["HG"][ii].astype(float); P = Z["POSE"][ii]; R_tol = float(M.p["R_tol"])
    ok, qq = _kin(D, HG, R_tol)
    key = {}
    for j in range(len(ii)): key[(round(float(P[j, 0])), round(float(P[j, 1])), round(float(P[j, 2])) % 360)] = j
    edges = []
    for j in range(len(ii)):
        if not ok[j]: continue
        x = (round(float(P[j, 0])), round(float(P[j, 1])), round(float(P[j, 2])) % 360)
        for y in ((x[0] + 15, x[1], x[2]), (x[0], x[1] + 15, x[2]), (x[0], x[1], (x[2] + 15) % 360)):
            t = key.get(y)
            if t is not None and ok[t]: edges.append((j, t))
    frames, spans = [], []
    for a, b in edges:
        ang = np.degrees(Rot.from_matrix(HG[a].T @ HG[b]).magnitude()); n = int(max(2, math.ceil(ang / step) + 1))
        fr = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()
        spans.append((len(frames), len(frames) + n)); frames += list(fr)
    eok = np.zeros(len(edges), bool)
    if frames:
        F = np.array(frames); fok, fq = _kin(D, F, R_tol)
        for e, (s0, s1) in enumerate(spans):
            d = np.abs((np.diff(fq[s0:s1], axis=0) + 180) % 360 - 180)
            eok[e] = bool(fok[s0:s1].all() and (d.max() if len(d) else 0) <= jump)
    adj = {}
    for e, (a, b) in enumerate(edges):
        if eok[e]: adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    el = P[:, 1]; feas = np.nonzero(ok)[0]
    conn = np.zeros(len(ii), bool)
    if len(feas):
        lo = el[feas].min(); front = [j for j in feas if el[j] <= lo + 1e-6]
        for j in front: conn[j] = True
        while front:
            nxt = []
            for a in front:
                for b in adj.get(a, []):
                    if not conn[b]: conn[b] = True; nxt.append(b)
            front = nxt
    return {int(ii[j]): bool(conn[j]) for j in range(len(ii))}, dict(grid=len(ii), feasible=int(ok.sum()), connected=int(conn.sum()),
                                                                   edges=len(edges), edges_ok=int(eok.sum()), seed_elev=float(el[feas].min()) if len(feas) else None)


def connected_report(M, B, rc, aud):
    """the corrected report with reach on the CONNECTED set (static vs connected, the continuity rule)"""
    cmap, info = connectivity(M)
    taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
    ws = [i for i in range(len(B.idx)) if B.kind[i] == "ws"]
    st = [i for i in ws if taken(i)]; cn = [i for i in st if cmap.get(int(B.idx[i]), False)]
    reach_c = round(len(cn) / max(1, len(ws)), 4)
    gap_c = CB.gap_of(rc["inband14"], rc["follow"], reach_c, rc["contact"])
    near_c = round(aud["gap_near1"] + (gap_c - rc["gap"]), 2)
    islands = [dict(plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"]) for i in st if i not in cn][:8]
    return dict(reach_static=rc["reach"], reach_connected=reach_c, gap_connected=gap_c, gap_near1_connected=near_c,
                static_islands=len(st) - len(cn), islands=islands, graph=info)


# ---------------------------------------------------------------------------------------------------------------------
# claim: the polish verifier's harness (unchanged) with the stops installed on its own model instance
def claim(proto, outp, P):
    spec = importlib.util.spec_from_file_location("pin_knee_polish_verifier", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
    H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H); install_stops(H.MK.S)
    P = KP.snap(dict(P)); t0 = time.time()
    fitB = H.fast_bench(60, 160) if proto == "fit60" else H.fast_bench(110, 360)
    wearB = H.held_bench() if proto == "held" else CB.Bench(n_clip=110, n_ws=360)
    M, fit, M1 = H.frozen_on(fitB, wearB, P)
    r = M.run(); model = {k: r[k] for k in H.KEYS}
    ex, bad = H.V.extra_checks(M, wearB); res0 = list(wearB.res)
    for i in bad: wearB.res[i] = None
    rc = wearB.report(); corrected = {k: rc[k] for k in H.KEYS}
    aud = H.MK.audit(M, wearB); rt = H.redteam(M, wearB); edge = knee_edge_overhead(M, wearB, M.p)
    conn = connected_report(M, wearB, rc, aud)
    wearB.res = res0
    oh = aud["overhead140"]
    out = dict(protocol=proto, params=P, fit_mode=fitB.mode, wear_mode=wearB.mode, n_wear=len(wearB.idx), exact=os.environ.get("CB_EXACT") == "1",
               fold_margin_rule=H.KIT.FOLD_MARGIN, stops=dict(m_lo=float(P.get("m_lo", STOP_FLOOR)), m_hi=float(P.get("m_hi", STOP_FLOOR))),
               o20_only=H.KIT.O20_ONLY, fit=fit, model=model, extra=ex, bad_removed=len(bad), corrected=corrected, corrected_audit=aud,
               gap_near1=aud["gap_near1"], near1_poses=aud["near1_poses"], min_metal_mm=aud["near_touch_min_mm"],
               overhead_follow=oh["follow"], overhead_clip=oh["clip"], overhead_reach=oh["reach"], knee_edge_overhead_deg=edge,
               continuity=conn, redteam=rt, secs=round(time.time() - t0, 1))
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True); json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(protocol=proto, wear=wearB.mode, n=len(wearB.idx), stops=out["stops"], corrected=corrected, near1=aud["gap_near1"],
                          near1_poses=aud["near1_poses"], min_mm=aud["near_touch_min_mm"], overhead=oh, knee_edge_oh=edge, bad=len(bad),
                          continuity={k: conn[k] for k in ("reach_static", "reach_connected", "gap_connected", "gap_near1_connected", "static_islands", "graph")},
                          fold_min_taken=rt["fold_margin_min_taken_deg"], secs=out["secs"]), default=float), flush=True)


# ---------------------------------------------------------------------------------------------------------------------
def log_rows(files, write=True):
    """merge polish-2 rows into the sweep log (stage polish2-m5-<stream>); history + the METHOD.md gate on obj"""
    d = json.load(open(KP.SWEEP)); have = {r.get("tag") for r in d if str(r.get("stage", "")).startswith("polish2-m5")}
    k = max(r["k"] for r in d) + 1; base = KP.base_params(); new = []; rows = []
    for f in files: rows += json.load(open(f))
    stream = lambda r: r["tag"].rsplit("-", 2)[0]
    rows.sort(key=lambda r: (r.get("gen", 0), stream(r), r["tag"]))
    for r in rows:
        if r["tag"] in have: continue
        rep = r.get("report") or {}; p = KP.snap(dict(base, **r["params"]))
        row = dict(k=k, t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), stage="polish2-m5-" + stream(r),
                   bench="Bench(110,360) fast, shape fitted there, verifier checks (3D closure, knee vs hub 3 upper, E boss); "
                         "fold rule 5 + J2 stops m_lo / m_hi (design variables >= 5); O20 x 3",
                   params=p, **{m: rep.get(m) for m in ("inband14", "inband10", "reach", "follow", "contact")},
                   gap=rep.get("gap") if not r.get("error") else None, gap_near1=rep.get("gap_near1"), obj=r["obj"],
                   obj_def=f"near-touch gap + {OH_PEN} per overhead clip frame (elev >= 140) lost",
                   near_min=rep.get("near_min"), model_gap=rep.get("model_gap"), why=rep.get("why"), knee_ang=rep.get("knee_ang"),
                   j3_lever_min=rep.get("j3_lever_min"), hubs=rep.get("hubs"), oh_follow=rep.get("oh_follow"), oh_lost=rep.get("oh_lost"),
                   oh_reach=rep.get("oh_reach"), oh_knee_edge=rep.get("oh_knee_edge"), fold_taken=rep.get("fold_taken"),
                   honest=not r.get("error"), tag=r["tag"], gen=r.get("gen"), src="polish2-m5")
        if r.get("error"): row["error"] = r["error"]
        new.append(row); have.add(r["tag"]); k += 1
    if write and new:
        d += new; json.dump(d, open(KP.SWEEP + ".tmp", "w"), indent=1, default=float); os.replace(KP.SWEEP + ".tmp", KP.SWEEP)
    allp = [r for r in d if str(r.get("stage", "")).startswith("polish2-m5")] if write else new
    hist = [r["obj"] if r.get("obj") is not None else 400.0 for r in allp]
    return allp, KP.gate(hist), len(new)


def main():
    a = sys.argv[1:]
    if not a: raise SystemExit(__doc__)
    if a[0] == "claim":
        claim(a[1], a[2], json.loads(a[3]))
    elif a[0] == "log":
        allp, g, nn = log_rows(a[1:]); ok = [r for r in allp if r.get("gap") is not None]; ok.sort(key=lambda r: r["obj"])
        print(f"logged {nn} new rows; polish-2 history {len(allp)}; gate {g}")
        for r in ok[:10]: print(r["k"], r["tag"], "obj", r["obj"], "near1", r["gap_near1"], "gap", r["gap"], r["reach"], r["follow"], r["inband14"],
                                r["contact"], "oh", r.get("oh_follow"), r.get("oh_knee_edge"), {k: r["params"].get(k) for k in FREE2})
    elif a[0] in ("cma", "scan"):
        use_kp2(); sys.argv = [sys.argv[0]] + a; KP.main()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
