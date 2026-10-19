"""Adversarial verifier for crest-knee-3r (2026-10-18). The pin-knee 3R at deltoid-crest seats, link 2 flying over the
whole member 3, a frozen J3 own-angle window. Re-measures the claimed configuration, frozen-shape protocol (fit on
Bench(60,160) FAST, the shape - heights, knee reference m, E profile, J3 window - worn without refit on Bench(110,360)
and on the disjoint held-out bench; CB_EXACT=1 for the exact path), with:

  * the model's own checks (closure / R_tol 0.5 mm radial drift / knee window and triangle / fit-clip continuity /
    part-part clearances incl. the fly-over E box / contact-only walls and crowns);
  * the pin-knee verifier's extra checks UNCHANGED (docs/concepts/verify/skin-normal-3r-pin-knee.py extra_checks:
    independent 3D closure of hub 3 / pin a / pin b, knee vs hub 3 above its lower plate, the E boss vs hubs 1-2, L1, L2);
  * this verifier's crest checks: the J3 window (q3' of every taken pose inside the frozen window, its margin to the
    stops), the knee window [ang_min, 180 - ang_min], the fold margin th (tools/concept_kit.py metric) over taken poses,
    hub-centre distances from GH, the arm pad's place on the humerus, the radial drift span;
  * the continuity flood (CLAUDE.md "Reach must be reachable by moving"; the knee and the J3 window are walls): full
    1432-pose workspace grid, kinematic nodes (fold window with margin, knee window, R_tol, closure, J3 window), 2-deg
    slerp edges, no q1 / q2 / q3' / pin a / pin b step > 10 deg, no knee branch change; seeds at elevation 0. Bench ws
    poses taken but not connected are dropped -> the connected gap;
  * per-pose dumps in tools/alignment_paired.py format (docs/alignment/remeasure/crest-knee-3r_<wear>_perpose.json).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/crest-knee-3r.py wear <bench|held> <out.json>
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/crest-knee-3r.py flood <out.json> [bench_out.json]
"""
import importlib.util, json, math, os, subprocess, sys, time
import numpy as np
from scipy.spatial.transform import Rotation as Rot, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


CK = _load("crest_knee_v", os.path.join(REPO, "docs", "concepts", "models", "crest-knee-3r.py"))
PV = _load("pin_knee_verifier_for_crest", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
PK = CK.PK
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "crest-knee-3r.json")))
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")
REM = os.path.join(REPO, "docs", "alignment", "remeasure")
STEP, JUMP = 2.0, 10.0


def held_bench(nc=110, nw=360):
    """= tools/osn_polish.py held_bench: poses DISJOINT from Bench(110,360) (held-out clips still excluded), exact path"""
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


def fit_fast(P):
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = CK.Model(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in KEYS}; fit["mode"] = B1.mode
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    ji = getattr(M1, "j3stop_info", None)
    if P2.get("j3stop") and ji: P2["j3win"] = [ji["lo"], ji["width"]]
    return M1, P2, fit, ji


def worn(M1, P2, B):
    """= crest-knee-3r.py frozen(): the fit shape copied, no refit"""
    class Frozen(CK.Model):
        def fit(self):
            for a in CK.COPY:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    return Frozen(B, P2)


def taken_list(B): return [i for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) >= 0]


def crest_checks(M, B, P2):
    D = M.D; tk = taken_list(B); out = {}
    a1, a2 = [math.degrees(a) for a in D.A]
    w = np.einsum("nij,j->ni", M.Q, D.u[2]); th = np.degrees(np.arccos(np.clip(w @ D.u[0], -1, 1)))
    marg = np.minimum(th - abs(a1 - a2), min(a1 + a2, 360 - a1 - a2) - th)
    out["th_margin_min_taken"] = round(float(marg[tk].min()), 3) if tk else None
    lo, wid = P2["j3win"]; rel = (M.q3p - lo) % 360
    inwin = rel <= wid
    out["j3win"] = [lo, wid]; out["j3_taken_outside_window"] = int(sum(1 for i in tk if not inwin[i]))
    out["j3_margin_min_taken"] = round(float(min(min(rel[i], wid - rel[i]) for i in tk)), 2) if tk else None
    am = float(M.p["ang_min"]); ang = M.K["ang"]
    out["knee_window"] = [am, 180 - am]; out["knee_ang_taken"] = [round(float(ang[tk].min()), 2), round(float(ang[tk].max()), 2)] if tk else None
    out["knee_outside_window"] = int(sum(1 for i in tk if not (am <= ang[i] <= 180 - am)))
    out["radial_drift_taken_max_mm"] = round(float(np.abs(M.s[tk, 2]).max()), 3) if tk else None
    out["closure_res_deg_max_taken"] = round(float(M.res_deg[tk].max()), 4) if tk else None
    C = [D.c[k] + M.f[k] * D.u[k] for k in range(3)]
    out["hub_centre_from_GH_mm"] = [round(float(np.linalg.norm(x)), 1) for x in C]
    out["hub_f"] = [round(float(x), 2) for x in M.f]; out["tr"] = round(float(M.tr), 2)
    out["drift_span"] = M.drift_span; out["radial_span"] = M.radial_span
    return out, marg


def wear(which, outp):
    P = dict(ROW["best_params"]); t0 = time.time()
    M1, P2, fit, ji = fit_fast(P)
    B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else held_bench()
    M = worn(M1, P2, B); r = M.run(); model = {k: r[k] for k in KEYS}
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "j3stop", "skin", "parts", "contact")}
    aud0 = PK.audit(M, B)
    ex, bad = PV.extra_checks(M, B)
    cc, marg = crest_checks(M, B, P2)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}
    aud = PK.audit(M, B)
    # per-pose dump of the corrected set, tools/alignment_paired.py format
    import alignment_paired as AP
    poses = AP._dump_bench(M, B)
    for row in poses:
        i = row["i"]; row.update(why=str(M.why[i]), th_margin=round(float(marg[i]), 3), q3p=round(float(M.q3p[i]), 2), knee=round(float(M.K["ang"][i]), 2))
    try: git = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception: git = None
    dump = dict(id=CK.ID, wear=which, params=P, frozen=corrected, report=rc, poses=poses, recomputed=AP.gap_parts(poses),
                secs=round(time.time() - t0, 1), exact=os.environ.get("CB_EXACT") == "1", git=git,
                note="written by docs/concepts/verify/crest-knee-3r.py (verifier extra checks applied)")
    os.makedirs(REM, exist_ok=True); dpath = os.path.join(REM, f"{CK.ID}_{which}_perpose.json")
    json.dump(dump, open(dpath, "w"), default=float)
    contacts = [dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                     depth=round(float(np.min(B.res[i])), 2)) for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) < 0]
    el = np.array([p["elev"] for p in B.poses]); ax = np.array([p["axial"] for p in B.poses]); kind = np.array(B.kind); tk = set(taken_list(B))
    ab = np.nonzero((np.abs(ax) >= 150) & (kind == "ws"))[0]
    B.res = res0
    out = dict(wear=which, params=P, mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", fit_fast=fit, j3stop_fit=ji, model=model, why=why,
               model_audit=aud0, extra=ex, removed=sorted(int(i) for i in bad), crest=cc, corrected=corrected, corrected_audit=aud,
               contacts=contacts, contact_depth_sum=round(float(sum(c["depth"] for c in contacts)), 2),
               axial150=dict(total=int(len(ab)), taken=int(sum(1 for i in ab if i in tk))),
               dump=dict(path=os.path.relpath(dpath, REPO), recomputed=dump["recomputed"]), ws_taken=[int(i) for i in sorted(tk) if B.kind[i] == "ws"],
               ws_idx=[int(B.idx[i]) for i in range(len(B.idx)) if B.kind[i] == "ws"], secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(wear=which, mode=B.mode, fit=fit, model=model, corrected=corrected, removed=len(bad), near1=aud["gap_near1"],
                          crest=cc, extra={k: ex[k] for k in ("closure_max", "closure_bad_poses", "knee_vs_hub3_upper_bad", "boss_bad", "spans_deg", "pad")},
                          recomputed=dump["recomputed"], secs=out["secs"]), default=float), flush=True)


def kin(D, Q, R_tol, win):
    q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s)
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol)
    R123 = X3[0]; c = (np.einsum("nij,nij->n", R123, Q) - 1) / 2
    ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    q3p = np.degrees((q[:, 2] + K["phi"]) % (2 * np.pi))
    if win is not None: ok &= ((q3p - win[0]) % 360) <= win[1]
    qq = np.degrees(np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"]])
    C2 = s[:, :2]; a = C2 - K["pa"]; b = K["B2"][None] - K["pa"]
    sgn = np.sign(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])
    return ok, qq, sgn


def flood(outp, bench_json=None):
    P = dict(ROW["best_params"]); t0 = time.time()
    M1, P2, fit, ji = fit_fast(P)
    D = PK.Design(dict(P2)); D.m = np.array(P2["m_fix"], float); D.m[2] = 0.0
    R_tol = float(P2["R_tol"]); win = P2.get("j3win")
    Z = CB._poses_all(); names = list(Z["NAMES"]); ws_id = names.index("Workspace (envelope)")
    W = np.nonzero(Z["CID"] == ws_id)[0]; POSE = Z["POSE"][W]; HG = Z["HG"][W].astype(float)
    ok, qq, sgn = kin(D, HG, R_tol, win)
    key = {(float(x[0]), float(x[1]), float(x[2])): i for i, x in enumerate(POSE)}
    vals = [sorted(set(POSE[:, k].tolist())) for k in range(3)]

    def nbrs(i):
        x = [float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])]
        for d in range(3):
            j = vals[d].index(x[d])
            for jj in (j - 1, j + 1):
                if d == 2 and jj == len(vals[2]) and vals[2][-1] == 180.0: jj = 1
                if d == 2 and jj == -1 and vals[2][0] == -180.0: jj = len(vals[2]) - 2
                if 0 <= jj < len(vals[d]):
                    y = list(x); y[d] = vals[d][jj]; t = key.get(tuple(y))
                    if t is not None: yield t
        if x[2] in (180.0, -180.0):
            t = key.get((x[0], x[1], -x[2]))
            if t is not None: yield t
    why = {"fold_or_window": 0, "jump": 0, "branch": 0}; ne = [0, 0]

    def edge(a, b):
        R0, R1 = Rot.from_matrix(HG[a]), Rot.from_matrix(HG[b]); angd = np.degrees((R0.inv() * R1).magnitude())
        n = max(2, int(math.ceil(angd / STEP)) + 1); Qs = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()
        o, q, sg = kin(D, Qs, R_tol, win); ne[0] += 1
        if not o.all(): why["fold_or_window"] += 1; return False
        d = np.abs((np.diff(q, axis=0) + 180) % 360 - 180)
        if d.max() > JUMP: why["jump"] += 1; return False
        if len(set(sg.tolist())) > 1: why["branch"] += 1; return False
        ne[1] += 1; return True
    elev = POSE[:, 1]; conn = np.zeros(len(W), bool); front = [i for i in range(len(W)) if ok[i] and elev[i] == 0]; conn[front] = True
    while front:
        nxt = []
        for a in front:
            for b in nbrs(a):
                if ok[b] and not conn[b] and edge(a, b): conn[b] = True; nxt.append(b)
        front = nxt
    out = dict(params=P, j3win=win, fold_margin=KIT.FOLD_MARGIN, grid=dict(poses=len(W), kin_ok=int(ok.sum()), connected=int(conn.sum()),
               islands=int((ok & ~conn).sum())), edges=dict(tested=ne[0], passed=ne[1], refused=why),
               island_poses=[dict(plane=float(POSE[i, 0]), elev=float(POSE[i, 1]), axial=float(POSE[i, 2])) for i in np.nonzero(ok & ~conn)[0][:40]])
    if bench_json:                                            # drop the bench's taken ws poses that are not connected
        bj = json.load(open(bench_json)); wpos = {int(g): k for k, g in enumerate(W)}
        B = CB.Bench(n_clip=110, n_ws=360) if bj["wear"] == "bench" else held_bench()
        dp = json.load(open(os.path.join(REPO, bj["dump"]["path"])))
        import alignment_paired as AP
        poses = dp["poses"]; drop = []
        for row in poses:
            i = row["i"]
            if row["kind"] == "ws" and row["taken"]:
                k = wpos.get(int(B.idx[i]))
                if k is None or not conn[k]: drop.append(i)
        for row in poses:
            if row["i"] in drop: row.update(taken=False, ev=False, contact=False, min_mm=None)
        out["bench"] = dict(wear=bj["wear"], static=dp["recomputed"], connected=AP.gap_parts(poses), dropped=drop,
                            dropped_poses=[dict(i=i, plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"]) for i in drop])
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in out if k not in ("params", "island_poses")}, default=float), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "wear": wear(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "flood": flood(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
