"""Adversarial verifier for rollcone-hubspot-pinknee-3r (round 501, G1, 2026-10-19). The claim: k 4-es32-202 (strap-held
external rolling-cone J2 at H1's hub-2 spot, rho 0.565), fit on Bench(60,160) FAST and worn frozen on Bench(110,360)
exact = 22.16 (no held-out read in the claim).

The model file is the claimant's (a rolling J2 exists nowhere else); this harness loads its own instance of it, wears the
claimed shape frozen (fit fast, no refit; the band sectors frozen at the fit y span) on Bench(110,360) exact and on the
disjoint held-out bench, and adds checks the model does not make:

  * independent 3D closure per taken pose: hub 3 centre via link 2 vs member 3, the link-2 -> member-3 rotation about
    J3 only, pin a via member 3 vs the knee link, pin b via the knee link vs the arm, both knee rotations parallel to sn;
  * the rolling pair: the contact generator as carried by the sun band (link 1) and by the planet band (link 2) must be
    one world line, and the relative angular velocity of link 2 on link 1 must lie on that line (no slip; finite
    difference, own implementation); the contact must sit inside both frozen band sectors;
  * parts the model leaves out or exempts: the E boss vs hub 1, both bands, link 1 (1 mm) and link 2 (0.15 mm, adjacent at
    J3); the knee link vs hub 3 above its lower plate (1 mm); link 1 vs the planet band, link 2 vs the sun band and link 1
    vs link 2 with NO exclusion zone round the contact line (members 1 and 2 are adjacent at J2: 0.15 mm); the sun band
    vs hub 1 and the planet band vs hub 3 (pose-invariant, reported);
  * the fold in the kit's metric (th distance to the rolling segment's extremum and the instantaneous dyad margin over
    taken poses), where the frozen band ends (the J2 own-angle stops) sit in th, the conditioning |u1 . (c x w)|;
  * band_lift (a link arriving above its band top would float: an air gap the model reports but does not build);
  * the user / lead rules: J1 seat (ruling 4: anterior <= 0.20), O20 at hubs 1 / 3, MR63ZZ knee stack 6, ang_min >= 25.22;
  * the continuity flood (CLAUDE.md continuity rule): the 1432-pose workspace grid, 2-deg slerp edges, no q1 / y /
    q3' / pin a / pin b step > 10 deg, no knee branch change, y inside the frozen sectors; seeds at elevation 0; taken
    bench ws poses not connected are dropped -> the connected gap;
  * per-pose dumps (tools/alignment_paired.py format) in docs/alignment/remeasure/<id>_v_<wear>_perpose.json (T5 rule).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/rollcone-hubspot-pinknee-3r.py wear <bench|held> <out.json>
    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/rollcone-hubspot-pinknee-3r.py flood <out.json> <wear_out.json>
"""
import importlib.util, json, math, os, subprocess, sys, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation as Rot, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
ID = "rollcone-hubspot-pinknee-3r"
_sp = importlib.util.spec_from_file_location("rollcone_for_verifier", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
MOD = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(MOD)
CB, PK, S = MOD.CB, MOD.PK, MOD.S
KIT = MOD.KIT
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")
REM = os.path.join(REPO, "docs", "alignment", "remeasure")
D2R = math.pi / 180
P = {"alpha_s": 12.8114, "alpha_p": 7.2019, "beta": 45.1638, "bh": 6.3368, "az1": 96.5609, "el1": 67.5273, "az2": 30.7025,
     "el2": 46.4626, "wd": 73.46, "wa": -6.8255, "b3": 0.3205, "lE": 61.569, "lc": 28.2303, "phiE": -3.2574, "phib": -60.3692}
STEP, JUMP = 2.0, 10.0


def held_bench(nc=110, nw=360):
    """= tools/osn_polish.py held_bench (docs/concepts/verify/crest-knee-3r.py): poses DISJOINT from Bench(110,360),
    held-out clips still excluded, exact path"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; PO = Z["POSE"]
    big, _, _, _ = CB._select(110, 360); bigs = set(big.tolist())
    fit_ids = [names.index(x) for x in CB.FIT]; ws_id = names.index("Workspace (envelope)")
    cl = np.array([i for i in np.nonzero(np.isin(cid, fit_ids))[0] if i not in bigs]); ws = np.array([i for i in np.nonzero(cid == ws_id)[0] if i not in bigs])
    cl = cl[np.linspace(0, len(cl) - 1, min(nc, len(cl))).round().astype(int)]; ws = ws[np.linspace(0, len(ws) - 1, min(nw, len(ws))).round().astype(int)]
    B = CB.Bench(20, 20); idx = np.r_[cl, ws]
    B.idx = idx; B.kind = ["clip"] * len(cl) + ["ws"] * len(ws); B.clip = [names[c] for c in cid[idx]]
    B.poses = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2]), flex=float(p[3]), pron=float(p[4])) for p in PO[idx]]
    B.res = [None] * len(idx); B._skin = {}; B._ex = {}; B._frames = {}; B.grid = None; B._V = None; B.mode = "exact"; B.key = "held"
    return B


COPY = ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
        "Hneed", "Lneed", "hEx", "_Ex", "Rb", "band_mid", "band_lift")


def fit_fast(par):
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = MOD.Model(B1, dict(par)); r1 = M1.run(); fit = {k: r1[k] for k in KEYS}; fit["mode"] = B1.mode
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]; P2["y_fix"] = list(M1.yspan)
    return M1, P2, fit


def worn(M1, P2, B):
    class Frozen(MOD.Model):
        def fit(self):
            for a in COPY:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    return Frozen(B, P2)


def taken_list(B): return [i for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) >= 0]


def rot_angle(R): return math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2))))


def Rm(u, a): return S.rotm(S.unit(np.asarray(u, float)), np.atleast_1d(a))[0]


def angd(a, b): return math.degrees(math.acos(max(-1.0, min(1.0, float(a @ b)))))


def extra_checks(M, B):
    D = M.D; Pm = D.p; u, c = D.u, D.c; sn = D.sn; fr = M.fr; tr = M.tr; tp = Pm["tp"]; h = S.T_LINK / 2; hb = MOD.WALL / 2
    tk = taken_list(B); out = {}
    _, X = M.cyl_surf["hub3"]; cen3 = c[2] + M.f[2] * u[2]; zz = (X - cen3) @ u[2]; H3up = X[zz >= S.UP - 1e-6]
    e, f = S.frame_of(sn); an = np.linspace(0, 2 * np.pi, 24, endpoint=False); dd = S.disc(PK.BOSS_R, 1.0)
    boss = np.concatenate([fr["A0"] + z * sn + PK.BOSS_R * (np.cos(an)[:, None] * e + np.sin(an)[:, None] * f) for z in (tr, tr + tp / 2, tr + tp)]
                          + [fr["A0"] + z * sn + dd[:, :1] * e + dd[:, 1:] * f for z in (tr, tr + tp)])
    clo = dict(hub3c=0.0, rot3_axis=0.0, pin_a=0.0, pin_b=0.0, knee_rot_axis=0.0, contact_line_deg=0.0, noslip_deg=0.0)
    bad = {k: [] for k in ("closure", "rolling", "boss", "knee_hub3up", "L1_planet", "L2_sun", "L1_L2", "sector")}
    low = {k: [] for k in ("boss", "knee_hub3up", "L1_planet", "L2_sun", "L1_L2")}
    sun_x = (sorted((D.rho * M.yspan[0], D.rho * M.yspan[1])))
    for i in tk:
        R1, t1 = M.T(1, i); R2, t2 = M.T(2, i); R3, t3 = M.T(3, i); R6, t6 = M.T(6, i); R5, t5 = M.T(5, i)
        e1 = float(np.linalg.norm((R2 @ c[2] + t2) - (R3 @ c[2] + t3)))
        Rr = R2.T @ R3; e2 = angd(Rr @ u[2], u[2])
        e3 = float(np.linalg.norm((R3 @ fr["A0"] + t3) - (R6 @ fr["A0m"] + t6)))
        e4 = float(np.linalg.norm((R6 @ fr["Bm"] + t6) - (R5 @ fr["Bm"] + t5)))
        e5 = max(angd((R3.T @ R6) @ sn, sn), angd((R6.T @ R5) @ sn, sn))
        # rolling pair: contact generator via the sun (link 1) and via the planet (link 2); no slip by finite difference
        y = float(M.q[i, 1])
        cs = R1 @ (Rm(D.uK, D.rho * y) @ D.cK); cp = R2 @ (Rm(D.v2h, -y) @ D.cK); e6 = angd(cs, cp)
        def rel(yy): return Rm(D.uK, D.rho * yy) @ Rm(D.v2, yy) @ D.R2r
        hh = 1e-4; Rd = rel(y + hh) @ rel(y - hh).T; w = np.array([Rd[2, 1] - Rd[1, 2], Rd[0, 2] - Rd[2, 0], Rd[1, 0] - Rd[0, 1]])
        w = w / np.linalg.norm(w); e7 = math.degrees(math.acos(min(1.0, abs(float(w @ (Rm(D.uK, D.rho * y) @ D.cK))))))
        # link 2 relative to link 1 must be exactly the rolling map at this y
        e8 = rot_angle((R1.T @ R2).T @ rel(y))
        for k, v in zip(("hub3c", "rot3_axis", "pin_a", "pin_b", "knee_rot_axis", "contact_line_deg", "noslip_deg"), (e1, e2, e3, e4, e5, e6, e7)):
            clo[k] = max(clo[k], v)
        clo["rel_map_deg"] = max(clo.get("rel_map_deg", 0.0), e8)
        if max(e1, e3, e4) > 0.5 or max(e2, e5) > 0.5: bad["closure"].append(i)
        if max(e6, e7, e8) > 0.1: bad["rolling"].append(i)
        yd = math.degrees(y)
        if not (M.yspan[0] - 1e-6 <= yd <= M.yspan[1] + 1e-6): bad["sector"].append(i)
        # parts
        bx = M._boxes_at_final(i); kc, kR, kh = bx["knee"]
        dk = float(M.sd_box(H3up @ R3.T + t3, kc, kR, kh).min()); low["knee_hub3up"].append((dk, i))
        if dk < S.PART_CLEAR: bad["knee_hub3up"].append(i)
        bw = boss @ R3.T + t3
        cyl = {k: (M.T(m, i)[0] @ cc + M.T(m, i)[1], M.T(m, i)[0] @ ax) for k, (m, cc, ax) in M.cyl.items()}
        st = {k: X_ @ M.T(m, i)[0].T + M.T(m, i)[1] for k, (m, X_) in M.strap.items()}
        bd = {k: X_ @ M.T(m, i)[0].T + M.T(m, i)[1] for k, (m, X_) in M.band_mid.items()}
        v = {"boss-hub1": float(M.sd_cyl(bw, *cyl["hub1"], r=10.0).min()),
             "boss-sun": float(cKDTree(bd["sun"]).query(bw)[0].min()) - hb, "boss-planet": float(cKDTree(bd["planet"]).query(bw)[0].min()) - hb}
        if len(st["L1"]): v["boss-L1"] = float(cKDTree(st["L1"]).query(bw)[0].min()) - h
        c3w, ax3 = cyl["hub3"]; ww = st["L2"] - c3w; far = np.linalg.norm(ww - (ww @ ax3)[:, None] * ax3, axis=1) > S.HUB_R + 1
        vL2 = float(cKDTree(st["L2"][far]).query(bw)[0].min()) - h if far.any() else 1e9
        k = min(v, key=v.get); low["boss"].append((min(v[k], vL2), i, k if v[k] <= vL2 else "boss-L2"))
        if v[k] < S.PART_CLEAR or vL2 < M.ADJ: bad["boss"].append(i)
        # members 1 / 2 across J2 with no exclusion zone (adjacent: 0.15 mm)
        a = float(cKDTree(bd["planet"]).query(st["L1"])[0].min()) - h - hb; low["L1_planet"].append((a, i))
        b = float(cKDTree(bd["sun"]).query(st["L2"])[0].min()) - h - hb; low["L2_sun"].append((b, i))
        cc_ = float(cKDTree(st["L2"]).query(st["L1"])[0].min()) - 2 * h; low["L1_L2"].append((cc_, i))
        if a < M.ADJ: bad["L1_planet"].append(i)
        if b < M.ADJ: bad["L2_sun"].append(i)
        if cc_ < M.ADJ: bad["L1_L2"].append(i)
    out["closure_max"] = {k: round(v, 5) for k, v in clo.items()}
    lab = lambda i: dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])
    out["low"] = {k: [dict(mm=round(t[0], 2), **lab(t[1]), **({"pair": t[2]} if len(t) > 2 else {})) for t in sorted(vv)[:4]] for k, vv in low.items()}
    out["bad_counts"] = {k: len(vv) for k, vv in bad.items()}
    # pose-invariant pairs: sun band vs hub 1 (rotates about u1 with link 1), planet band vs hub 3 (rotates about u3)
    _, X1c = M.cyl_surf["hub1"]; m1, cen1, ax1 = M.cyl["hub1"]; m3, cen3c, ax3c = M.cyl["hub3"]
    out["static"] = dict(sun_vs_hub1=round(float(M.sd_cyl(M.band_mid["sun"][1], cen1, ax1, r=10.0).min()) - hb, 2),
                         planet_vs_hub3=round(float(M.sd_cyl(M.band_mid["planet"][1], cen3c, ax3c, r=10.0).min()) - hb, 2))
    # fold reading, band-end stops in th, conditioning
    fd = M.fold; tkl = list(tk)
    out["fold"] = dict(min_mseg_taken=round(float(fd["mseg"][tkl].min()), 3) if tkl else None,
                       min_mdy_taken=round(float(fd["mdy"][tkl].min()), 3) if tkl else None,
                       min_jac_taken=round(float(fd["jac"][tkl].min()), 4) if tkl else None,
                       jac_below_h1_0p233=int(sum(1 for i in tkl if fd["jac"][i] < 0.233)),
                       th_window=[round(float(D.th_tab.min()), 2), round(float(D.th_tab.max()), 2)], seg_ext=list(D.seg_ext))
    ys = D.ys; th_tab = D.th_tab
    th_end = [float(np.interp(yv, ys, th_tab)) if ys[0] < ys[-1] else float(np.interp(yv, ys[::-1], th_tab[::-1])) for yv in M.yspan]
    out["stops"] = dict(y_fix=[round(v, 2) for v in M.yspan], th_at_stops=[round(v, 2) for v in th_end],
                        margin_to_extremum=[round(min(t - th_tab.min(), th_tab.max() - t), 2) for t in th_end],
                        y_taken=[round(float(np.degrees(M.q[tkl, 1]).min()), 2), round(float(np.degrees(M.q[tkl, 1]).max()), 2)] if tkl else None)
    out["band_lift_mm"] = float(M.band_lift); out["Rb"] = [round(float(x), 2) for x in M.Rb]; out["bh"] = float(Pm["bh"])
    d1 = S.bvec(Pm["az1"], Pm["el1"])
    out["rules"] = dict(j1_anterior=round(float(d1[0]), 4), j1_ok=bool(d1[0] <= 0.20), hubs=list(M.hr), o20=all(r == 10.0 for r in M.hr),
                        stk=Pm["stk"], ang_min=Pm["ang_min"], knee_ok=bool(Pm["stk"] == 6.0 and Pm["ang_min"] >= 25.22), rho=round(D.rho, 4),
                        alpha=[Pm["alpha_s"], Pm["alpha_p"]], sgn=Pm["sgn"], pitch_r_mm=[round(float(M.Rb[0]) * math.sin(Pm["alpha_s"] * D2R), 2), round(float(M.Rb[1]) * math.sin(Pm["alpha_p"] * D2R), 2)])
    allbad = set()
    for vv in bad.values(): allbad |= set(vv)
    return out, allbad


def wear(which, outp):
    t0 = time.time()
    M1, P2, fit = fit_fast(dict(P))
    B = CB.Bench(n_clip=110, n_ws=360) if which == "bench" else held_bench()
    M = worn(M1, P2, B); r = M.run(); model = {k: r[k] for k in KEYS}
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "skin", "parts", "contact")}
    aud0 = PK.audit(M, B)
    ex, bad = extra_checks(M, B)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}
    aud = PK.audit(M, B)
    import alignment_paired as AP
    poses = AP._dump_bench(M, B)
    for row in poses:
        i = row["i"]; row.update(why=str(M.why[i]), y=round(float(np.degrees(M.q[i, 1])), 2), knee=round(float(M.K["ang"][i]), 2),
                                 mseg=round(float(M.fold["mseg"][i]), 2) if np.isfinite(M.fold["mseg"][i]) else None, removed_by_verifier=bool(i in bad))
    try: git = subprocess.run(["git", "-C", REPO, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception: git = None
    dump = dict(id=ID, wear=which, params=P, frozen=corrected, report=rc, poses=poses, recomputed=AP.gap_parts(poses),
                secs=round(time.time() - t0, 1), exact=os.environ.get("CB_EXACT") == "1", git=git,
                note="written by docs/concepts/verify/rollcone-hubspot-pinknee-3r.py (verifier extra checks applied)")
    os.makedirs(REM, exist_ok=True); dpath = os.path.join(REM, f"{ID}_v_{which}_perpose.json"); json.dump(dump, open(dpath, "w"), default=float)
    contacts = [dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"],
                     depth=round(float(np.min(B.res[i])), 2)) for i in range(len(B.idx)) if B.res[i] is not None and len(B.res[i]) and float(np.min(B.res[i])) < 0]
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind); tk = set(taken_list(B))
    oh = np.nonzero((el >= 140) & (kind == "ws"))[0]
    B.res = res0
    out = dict(wear=which, params=P, P2={k: v for k, v in P2.items() if isinstance(v, (int, float, str, list)) and k not in ("unresolved",)},
               mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", fit_fast=fit, model=model, why=why, model_audit=aud0, extra=ex,
               removed=sorted(int(i) for i in bad), corrected=corrected, corrected_audit=aud, contacts=contacts,
               contact_depth_sum=round(float(sum(c["depth"] for c in contacts)), 2),
               overhead=dict(total=int(len(oh)), taken=int(sum(1 for i in oh if i in tk))),
               dump=dict(path=os.path.relpath(dpath, REPO), recomputed=dump["recomputed"]), secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(wear=which, mode=B.mode, fit=fit, model=model, corrected=corrected, removed=len(bad), near1=aud.get("gap_near1"),
                          extra=ex, overhead=out["overhead"], recomputed=dump["recomputed"], contacts=contacts, secs=out["secs"]), default=float), flush=True)


def kin(D, Q, R_tol, yfix):
    q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s)
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol)
    c = (np.einsum("nij,nij->n", X3[0], Q) - 1) / 2
    ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    yd = np.degrees(q[:, 1]); ok &= (yd >= yfix[0]) & (yd <= yfix[1])
    qq = np.degrees(np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"]])
    C2 = s[:, :2]; a = C2 - K["pa"]; b = K["B2"][None] - K["pa"]
    return ok, qq, np.sign(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])


def flood(outp, wear_json):
    t0 = time.time(); wj = json.load(open(wear_json))
    M1, P2, fit = fit_fast(dict(P))
    D = MOD.Design(dict(P2)); D.m = np.array(P2["m_fix"], float); D.m[2] = 0.0
    R_tol = float(P2["R_tol"]); yfix = P2["y_fix"]
    Z = CB._poses_all(); names = list(Z["NAMES"]); ws_id = names.index("Workspace (envelope)")
    W = np.nonzero(Z["CID"] == ws_id)[0]; POSE = Z["POSE"][W]; HG = Z["HG"][W].astype(float)
    ok, qq, sgn = kin(D, HG, R_tol, yfix)
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
        R0, R1 = Rot.from_matrix(HG[a]), Rot.from_matrix(HG[b]); ang = np.degrees((R0.inv() * R1).magnitude())
        n = max(2, int(math.ceil(ang / STEP)) + 1); Qs = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()
        o, q, sg = kin(D, Qs, R_tol, yfix); ne[0] += 1
        if not o.all(): why["fold_or_window"] += 1; return False
        if np.abs((np.diff(q, axis=0) + 180) % 360 - 180).max() > JUMP: why["jump"] += 1; return False
        if len(set(sg.tolist())) > 1: why["branch"] += 1; return False
        ne[1] += 1; return True
    elev = POSE[:, 1]; conn = np.zeros(len(W), bool); front = [i for i in range(len(W)) if ok[i] and elev[i] == 0]; conn[front] = True
    while front:
        nxt = []
        for a in front:
            for b in nbrs(a):
                if ok[b] and not conn[b] and edge(a, b): conn[b] = True; nxt.append(b)
        front = nxt
    out = dict(params=P, y_fix=yfix, fold_margin=KIT.FOLD_MARGIN, grid=dict(poses=len(W), kin_ok=int(ok.sum()), connected=int(conn.sum()),
               islands=int((ok & ~conn).sum())), edges=dict(tested=ne[0], passed=ne[1], refused=why),
               island_poses=[dict(plane=float(POSE[i, 0]), elev=float(POSE[i, 1]), axial=float(POSE[i, 2])) for i in np.nonzero(ok & ~conn)[0][:40]])
    wpos = {int(g): k for k, g in enumerate(W)}
    B = CB.Bench(n_clip=110, n_ws=360) if wj["wear"] == "bench" else held_bench()
    dpath = os.path.join(REPO, wj["dump"]["path"]); dp = json.load(open(dpath))
    import alignment_paired as AP
    poses = dp["poses"]; drop = []
    for row in poses:
        i = row["i"]
        if row["kind"] == "ws" and row["taken"]:
            k = wpos.get(int(B.idx[i]))
            if k is None or not conn[k]: drop.append(i)
    for row in poses:
        if row["i"] in drop: row.update(taken=False, ev=False, contact=False, min_mm=None)
    out["bench"] = dict(wear=wj["wear"], static=dp["recomputed"], connected=AP.gap_parts(poses), dropped=drop,
                        dropped_poses=[dict(i=i, plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"]) for i in drop])
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in out if k not in ("params", "island_poses")}, default=float), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "wear": wear(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "flood": flood(sys.argv[2], sys.argv[3])
