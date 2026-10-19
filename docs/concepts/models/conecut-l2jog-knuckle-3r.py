"""conecut-l2jog-knuckle-3r (round 15, lens C 'conecut-sidestep-metal'): the verified lead conecut-knee-knuckle-3r
(docs/concepts/models/conecut-knee-knuckle-3r.py imported UNCHANGED, at its verified best_params: slipper-nose K drive,
conecut knee, J3 own-angle dowel stop, O20 hubs, metal, near-touch rules) with ONE profile change on link 2 (member 2,
the 3 mm Ti-6Al-4V bar J2 -> J3): a local S-JOG of its planform about the sample that grazes the skin at bench pose 139
(link-2 sample 13, row 0 = the bar's edge row, 69.6 mm from GH; 0.072 mm on the lead, the only pose that flips at the
lead's +0.1 / +0.2 mm probes).

GEOMETRY (all in link 2's own frame, applied to the FITTED shape right after the lead's fit, so the frozen claim protocol
copies it; equal sample count, every L2 copy moved together):
  * the bar's local frame at the binder from a PCA of the L2 samples within 8 mm (sv ~19.8 / 10.7 / 2.0): axis a,
    width w (unit(n x a), signed so +w points from the binder's edge row 0 toward row 3), plate normal n (signed AWAY
    from GH, i.e. toward the skin is -n). JUDGE CORRECTION kept: the jog direction is the bar's WIDTH direction
    lat = sgn * (cos(rot) w + sin(rot) a), |rot| <= 10 deg (in the plate's plane only) - never the tangent-to-GH skin
    gradient (that slides samples along a bar that does not move and lifts it through its thickness).
  * station s along the bar = per-row arc length from the row's crossing of the binder's normal plane (each row of the
    4 x 31 underside is a polyline; so a row 6 mm across the bar gets the SAME weight as the binder: the section moves
    rigidly - a planform jog, not a shear).
  * profile: w(s) = 1 for |s - cs| <= Lf / 2, then a cosine run-out to 0 over T (the S of two tangent arcs; min radius of
    the planform S = 2 T^2 / (pi^2 dl), 20 mm at T 10, dl 1: a profile cut, no bend).
  * displacement: dl * w(s) * f_row * lat + dz * w(s) * n, f_row = 1 - (1 - ff) * (row position across the bar, 0 at the
    edge the bar moves away from, 1 at the far edge). ff = 1: JOG (the spec: the whole section shifts dl). ff < 1: WAIST
    (the far edge stays at ff * dl: the bar is narrowed by (1 - ff) dl locally - the far side cannot come closer to the
    skin than the lead's far edge). dz > 0: a local JOGGLE of the bar through its thickness (a press-brake joggle; bend
    radius 2 T^2 / (pi^2 dz) must be >= 15 mm = 5 t, the CAD rule) - NOT in the spec (it says 'no lift'); measured as an
    explicit variant with its in-band cost, default 0.
  * moved sets: link_pts['L2'] (underside, scored), strap['L2'] (mid surface, part-vs-part collisions), the L2 top
    contact-only set (underside + 3 mm radial, member 2). Nothing else moves.

DOF: unchanged from the lead - 3 ACTIVE (J1, J2, J3), K slaved and never read, knee pins a / b passive rotations outside
the count, 0 passive translations, no gears / pulleys / cables. Complexity 18.5 (a profile change of an existing made
part, +0).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/conecut-l2jog-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen|held '<json>' [out.json]
    ... scan '<json list of jog dicts>' <bench: fit|envh|bench|envsel|env|held> [out.json]
        (the lead's frozen chain worn ONCE on that bench, then every jog re-read on the poses where link 2 is within 4 mm
        of the skin: per config the bench report with the jogged L2 samples, probes, near1, pose minima; collisions are
        re-checked only by the frozen protocol)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("conecut_for_l2jog", os.path.join(HERE, "conecut-knee-knuckle-3r.py"))
CC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CC)
CB, S, SN, PK, SC, FL, RF, BM = CC.CB, CC.S, CC.SN, CC.PK, CC.SC, CC.FL, CC.RF, CC.BM
ID = "conecut-l2jog-knuckle-3r"
LEAD = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "conecut-knee-knuckle-3r.json")))["best_params"]
BASE = CC._clamp(dict(CC.PARAMS, **LEAD))                    # the verified lead, every parameter
JOG = dict(dl=0.0, Lf=14.0, T=10.0, cs=0.0, rot=0.0, sgn=1, ff=1.0, dz=0.0)
PARAMS = dict(BASE, **JOG)
JB = 13                                                       # pose 139's binder: link_pts['L2'] sample 13 (row 0)
XB_REF = np.array([-28.79, 11.22, 62.31])                     # its local coordinates on the lead's fit (check)
T_TOP = 3.0                                                   # L2 top = underside + 3 mm radial (contact-only set)
GUARD = (139, 203, 205, 237, 264, 316)
S_LO, S_HI = -15.0, 38.8                                      # allowed station span of the jog (see _clamp)


def _clamp(p):
    p = dict(p)
    for k, lo, hi in (("dl", 0.0, 1.6), ("Lf", 4.0, 24.0), ("T", 4.0, 16.0), ("cs", -6.0, 6.0), ("rot", -10.0, 10.0),
                      ("ff", 0.0, 1.0), ("dz", 0.0, 0.8)):
        p[k] = min(max(float(p.get(k, JOG[k])), lo), hi)
    p["sgn"] = 1 if float(p.get("sgn", 1)) >= 0 else -1
    # the moved span stays off link 2's root stretch that binds radially at 316 (stations -22.2 .. -16.3 from the binder,
    # r_J2 13.5 - 19.4: the spec keeps it untouched) and >= 2 mm inside hub 3's rim (station 40.8): S_LO / S_HI
    for _ in range(2):
        lo_end = p["cs"] - p["Lf"] / 2 - p["T"]; hi_end = p["cs"] + p["Lf"] / 2 + p["T"]
        if lo_end < S_LO: p["T"] = max(4.0, p["T"] - (S_LO - lo_end)); p["Lf"] = max(4.0, min(p["Lf"], 2 * (p["cs"] - S_LO - p["T"])))
        if hi_end > S_HI: p["T"] = max(4.0, p["T"] - (hi_end - S_HI)); p["Lf"] = max(4.0, min(p["Lf"], 2 * (S_HI - p["cs"] - p["T"])))
    p["dz"] = min(p["dz"], 2 * p["T"] ** 2 / (math.pi ** 2 * 15.0))     # joggle bend radius >= 15 mm (5 t, the CAD rule)
    return CC._clamp(p)


def _unit(v): return v / np.linalg.norm(v)


def l2_rows(M):
    """row sizes of link_pts['L2'] (the 4 rows of the bar's underside, in order)"""
    lk = [l for l in M.geo.links if l["name"] == "L2"][0]
    return [int(np.asarray(keep).sum()) for (dv, keep, sarc) in lk["rows"]]


def jog_frame(X, rows):
    """binder, axis a, width w (+ toward the far rows), outward normal n, per-sample station s and across-bar position y01"""
    jb = JB if np.linalg.norm(X[JB] - XB_REF) < 0.5 else int(np.argmin(np.linalg.norm(X - XB_REF, axis=1)))
    xb = X[jb]; nb = np.linalg.norm(X - xb, axis=1) < 8.0; Pc = X[nb] - X[nb].mean(0)
    _, sv, Vt = np.linalg.svd(Pc, full_matrices=False); a, n = Vt[0], Vt[2]
    if n @ _unit(xb) < 0: n = -n                              # outward (away from GH)
    w = _unit(np.cross(n, a)); a = np.cross(w, n)
    cut = np.cumsum([0] + rows); rid = np.repeat(np.arange(len(rows)), rows)
    far = X[(rid == len(rows) - 1) & nb]
    if len(far) and float(((far - xb) @ w).mean()) < 0: w = -w; a = -a
    s = np.zeros(len(X))
    for r in range(len(rows)):
        Xr = X[cut[r]:cut[r + 1]]; A = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(Xr, axis=0), axis=1))]
        pr = (Xr - xb) @ a; k = int(np.argmin(np.abs(pr)))
        k2 = k + 1 if (k + 1 < len(pr) and np.sign(pr[k]) != np.sign(pr[k + 1])) else max(k - 1, 0)
        a0 = A[k] if pr[k2] == pr[k] else A[k] + (A[k2] - A[k]) * (0 - pr[k]) / (pr[k2] - pr[k])
        s[cut[r]:cut[r + 1]] = A - a0
    y = (X - xb) @ w
    return dict(jb=jb, xb=xb, a=a, w=w, n=n, s=s, y=y, rid=rid, sv=sv)


def jog_disp(X, rows, P, fr=None):
    """the displacement field (local frame) of every L2 underside sample"""
    fr = fr or jog_frame(X, rows)
    dl, Lf, T, cs, rot, sgn, ff, dz = (float(P[k]) for k in ("dl", "Lf", "T", "cs", "rot", "sgn", "ff", "dz"))
    lat = sgn * (math.cos(math.radians(rot)) * fr["w"] + math.sin(math.radians(rot)) * fr["a"])
    u = np.abs(fr["s"] - cs) - Lf / 2
    wt = np.where(u <= 0, 1.0, np.where(u >= T, 0.0, 0.5 * (1 + np.cos(np.pi * np.clip(u, 0, T) / T))))
    yl = fr["y"] * sgn                                        # across-bar position along the move direction
    y01 = (yl - yl.min()) / max(yl.max() - yl.min(), 1e-9)    # 0 at the edge the bar moves away from
    frow = 1.0 - (1.0 - ff) * y01
    D = dl * (wt * frow)[:, None] * lat[None] + dz * wt[:, None] * fr["n"][None]
    info = dict(binder=int(fr["jb"]), n_moved=int((wt > 1e-6).sum()), wmax_row=[round(float(wt[fr["rid"] == r].max()), 3) for r in range(len(rows))],
                lat=[round(float(v), 4) for v in lat], n=[round(float(v), 4) for v in fr["n"]], sv=[round(float(v), 2) for v in fr["sv"]],
                width_mm=round(float(np.ptp(fr["y"][np.abs(fr["s"]) < 3])), 2),
                narrowing_mm=round((1 - ff) * dl, 3),
                planform_Rmin_mm=(round(2 * T ** 2 / (math.pi ** 2 * dl), 1) if dl > 0 else None),
                joggle_Rmin_mm=(round(2 * T ** 2 / (math.pi ** 2 * dz), 1) if dz > 0 else None),
                s_span=[round(float(fr["s"][wt > 1e-6].min()), 1), round(float(fr["s"][wt > 1e-6].max()), 1)] if (wt > 1e-6).any() else None)
    return D, info


def apply_jog(M, P):
    """move link 2's underside, mid (strap) and top (contact-only) samples by the jog field (idempotent per fit)"""
    mL2, X = M.link_pts["L2"]; X = np.asarray(X, float)
    if getattr(M, "_jog_src", None) is X: return M._jog_info
    rows = l2_rows(M); D, info = jog_disp(X, rows, P)
    Xn = X + D; M.link_pts["L2"] = (mL2, Xn)
    ms, Xs = M.strap["L2"]; Xs = np.asarray(Xs, float)
    assert len(Xs) == len(X) and np.allclose(np.linalg.norm(Xs - X, axis=1), S.T_LINK / 2, atol=1e-6), "strap L2 is not underside + 1.5"
    M.strap["L2"] = (ms, Xs + D)
    top = [ci for ci, (m, Xc) in enumerate(M.contact) if m == mL2 and len(Xc) == len(X) and np.allclose(np.linalg.norm(np.asarray(Xc) - X, axis=1), T_TOP, atol=1e-6)]
    assert len(top) == 1, ("L2 top contact set not found", top)
    M.contact[top[0]] = (mL2, np.asarray(M.contact[top[0]][1], float) + D)
    info.update(top_set=top[0], dmax_mm=round(float(np.linalg.norm(D, axis=1).max()), 3))
    M._jog_src = Xn; M._jog_info = info
    return info


class JogModel(CC.CCModel):
    def fit(self):
        super().fit()
        apply_jog(self, {k: self.D.p.get(k, JOG[k]) for k in JOG})
        try: self._sc_info["jog"] = self._jog_info
        except Exception: pass


# the lead's module and its parents build models through these names: point them at JogModel (the frozen protocol's
# Frozen class subclasses CC.CCModel at call time and COPIES the fitted, jogged link_pts / strap / contact from M1)
CC.CCModel = JogModel; SN.SNModel = JogModel; SC.SCModel = JogModel; FL.G.KR.KB.KModel = JogModel; FL.FLModel_SC = JogModel


def probe(M, B, thrs=(0.1, 0.2, 0.35)):
    """tolerance probe (round-15 rule): every taken pose whose lowest metal (scored or contact-only) is under thr counted as
    contact; also the 1-2 mm shell count (T1)"""
    taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
    cm = getattr(M, "cmin", {}) or {}
    mins = [(min(float(np.min(B.res[i])), cm.get(i, 1e9)), i) for i in range(len(B.idx)) if taken(i)]
    res0 = list(B.res); out = {}
    for t in thrs:
        for d, i in mins:
            if d < t: B.res[i] = np.r_[B.res[i], -1e-3]
        out[f"gap_probe{t:g}"] = B.report()["gap"]; out[f"probe{t:g}_poses"] = int(sum(1 for d, i in mins if d < t)); B.res = list(res0)
    out["shell12_poses"] = int(sum(1 for d, i in mins if 1.0 <= d < 2.0))
    return out


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = CC._report(B, p)
    try: r.update(probe(M, B))
    except Exception as e: r["probe_err"] = str(e)[:100]
    r["jog"] = getattr(M, "_jog_info", None)
    return r, M


def evaluate(B, params):
    """objective = the 1 mm near-touch gap (CLAUDE.md search rule); r['plain'] keeps the plain gap"""
    r, M = _report(B, params)
    if r.get("gap_near1") is not None: r["plain"] = r.get("plain", r["gap"]); r["gap"] = r["gap_near1"]
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def _frozen_out(P, nc, nw):
    """CC.frozen's report (re-run through this module so the jog is applied) + probes + the jog's own minima"""
    P = _clamp(dict(PARAMS, **P)); out = CC.frozen(P, nc, nw)
    return out


def frozen(P, nc=110, nw=360): return _frozen_out(P, nc, nw)


def frozen_bench(P): return _frozen_out(P, 110, 360)


def frozen_held(P): return _frozen_out(P, -1, -1)


def viz_export(par): return CC.viz_export(_clamp(dict(PARAMS, **par)))


# ------------------------------------------------------------------------------------------------------------------
# scan: the lead's frozen chain worn ONCE per bench; each jog re-read on the poses where link 2 is near the skin
def _bench(name):
    if name == "fit":
        os.environ.pop("CB_EXACT", None); return CB.Bench(n_clip=60, n_ws=160)
    if name == "envh":
        sp_ = importlib.util.spec_from_file_location("acro_for_l2jog", os.path.join(HERE, "acroant-conecut-knuckle-3r.py"))
        A = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(A); return A.bench_envh()
    if name in ("env", "envsel"):
        import env_bench as EB
        EB.install(); return EB.bench(name, exact=True)
    if name == "held":
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_l2jog", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
        PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); return PVm.held_bench()
    os.environ["CB_EXACT"] = "1"; os.environ["CB_QUIET_EXACT"] = "1"; return CB.Bench(n_clip=110, n_ws=360)


class Scan:
    """control wear (jog 0) of the lead's frozen chain on one bench, then per jog config the L2 samples re-read. The
    control wear is cached (pickle: per-pose scored distances, contact-only minima, member-2 transforms of the near
    poses) so later config batches on the same bench cost one distance call per near pose"""
    def __init__(self, bench, near=None, cache=None):
        # near: link-2 re-read radius (mm). The bench's IN-BAND (2-14 mm per sample over clip frames) moves wherever the
        # jogged samples sit near 2 or 14 mm, so a radius re-read is exact for contact / probes / near-touch only;
        # default: every scored pose on the fast benches (exact in-band), 4 mm on the exact benches (in-band read by the
        # frozen protocol)
        if near is None: near = float(os.environ.get("L2JOG_NEAR", 1e9 if bench in ("fit", "envh") else 4.0))
        import pickle, types
        self.name = bench; self.B = B = _bench(bench)
        if cache and os.path.exists(cache):
            C = pickle.load(open(cache, "rb")); self.__dict__.update(C); self.M = types.SimpleNamespace(cmin=dict(self.cmin0), why=self.why0); self.base = self.read_many([dict(dl=0.0, dz=0.0)])[0]; return
        P0 = _clamp(dict(PARAMS, dl=0.0, dz=0.0))
        old = os.environ.pop("CB_EXACT", None)
        try: B1 = CB.Bench(n_clip=60, n_ws=160)
        finally:
            if old is not None: os.environ["CB_EXACT"] = old
        M1 = JogModel(B1, dict(P0)); M1.run(); P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
        ATTR = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info")

        class Frozen(JogModel):
            def fit(self):
                for a in ATTR:
                    if hasattr(M1, a): setattr(self, a, getattr(M1, a))
                self._sc = None
                self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
                self._truncate()
        t = time.time(); M = Frozen(B, P2); r0 = M.run(); self.secs_wear = round(time.time() - t, 1)
        self.r0 = {k: r0.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
        self.res0 = [None if x is None else np.asarray(x, float).copy() for x in B.res]; self.cmin0 = dict(M.cmin); self.why0 = np.asarray(M.why).copy()
        mL2, X = M.link_pts["L2"]; self.mL2 = mL2; self.X = np.asarray(X, float); self.rows = l2_rows(M1); self.fr = jog_frame(self.X, self.rows)
        self.nmetal = sum(len(x) for _, x in M.rigid.values()) + sum(len(x) for _, x in M.link_pts.values())
        self.top = [ci for ci, (m, Xc) in enumerate(M.contact) if m == mL2 and len(Xc) == len(self.X)][0]
        self.Xtop = np.asarray(M.contact[self.top][1], float)
        self.poses = []; self.c_other = {}; self.l2min0 = {}; self.T2 = {}
        for i in range(len(B.idx)):
            if self.res0[i] is None: continue
            d = self.res0[i][:self.nmetal]; dL = d[self.nmetal - len(self.X):]
            sets = [M.world(m, i, Xc) for ci, (m, Xc) in enumerate(M.contact) if ci != self.top and len(Xc)]
            n_o = sum(len(x) for x in sets); dd = B.dist(i, np.concatenate(sets + [M.world(mL2, i, self.Xtop)]))
            self.c_other[i] = float(dd[:n_o].min()); dT = dd[n_o:]; self.l2min0[i] = (float(dL.min()), float(dT.min()))
            if min(float(dL.min()), float(dT.min())) < near:
                self.poses.append(i); E = M.world(mL2, i, np.vstack([np.zeros(3), np.eye(3)]))     # world() is affine: P @ A.T + b
                b = E[0]; A = (E[1:] - b).T; assert np.allclose(self.X @ A.T + b, M.world(mL2, i, self.X), atol=1e-6)
                self.T2[i] = (A.copy(), b.copy())
        self.secs_init = round(time.time() - t, 1)
        if cache:
            keep = ("r0", "res0", "cmin0", "why0", "mL2", "X", "rows", "fr", "nmetal", "top", "Xtop", "poses", "c_other", "l2min0", "T2", "secs_wear", "secs_init")
            pickle.dump({k: getattr(self, k) for k in keep}, open(cache, "wb"))
        self.M = types.SimpleNamespace(cmin=dict(self.cmin0), why=self.why0)
        self.base = self.read_many([dict(dl=0.0, dz=0.0)])[0]

    def read_many(self, plist):
        """bench reports with the jogged L2 for every config (one distance call per near pose for all configs)"""
        B = self.B; nX = len(self.X); Ds = []; infos = []
        for P in plist:
            D, info = jog_disp(self.X, self.rows, dict(JOG, **P), self.fr); Ds.append(D); infos.append(info)
        dist = {}
        for i in self.poses:
            R, t = self.T2[i]; pts = np.concatenate([np.concatenate([self.X + D, self.Xtop + D]) for D in Ds]) @ R.T + t
            dist[i] = B.dist(i, pts).reshape(len(Ds), 2, nX)
        outs = []
        for k, P in enumerate(plist):
            res = list(self.res0); cmin = dict(self.cmin0); l2 = {}
            for i in self.poses:
                dL, dT = dist[i][k]; d = self.res0[i][:self.nmetal].copy(); d[self.nmetal - nX:] = dL
                dc = min(self.c_other[i], float(dT.min())); cmin[i] = dc
                res[i] = np.r_[d, dc] if dc < 0 else d; l2[i] = (round(float(dL.min()), 3), round(float(dT.min()), 3))
            taken = [i for i in range(len(B.idx)) if res[i] is not None and float(np.min(res[i])) >= 0]
            l2t = [min(l2.get(i, self.l2min0[i])) for i in taken if i in self.l2min0]
            mins = {int(i): round(min(float(np.min(res[i])), cmin.get(i, 1e9)), 3) for i in self.poses}
            self.M.cmin = cmin; B.res = list(res); rep = B.report(); a = PK.audit(self.M, B); B.res = list(res); pr = probe(self.M, B)
            B.res = list(self.res0); self.M.cmin = dict(self.cmin0)
            out = dict(gap=rep["gap"], reach=rep["reach"], follow=rep["follow"], inband14=rep["inband14"], inband10=rep.get("inband10"),
                       contact=rep["contact"], near1=a.get("gap_near1"), near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"),
                       l2_min_taken=round(min(l2t), 3) if l2t else None, **pr, jog=infos[k])
            out["pose_min"] = mins; out["l2"] = {int(i): v for i, v in l2.items()}
            outs.append(out)
        return outs


def scan_main(plist, bench, outp=None):
    t = time.time(); SC_ = Scan(bench, cache=os.environ.get("L2JOG_CACHE"))
    rows = SC_.read_many([_clamp(dict(PARAMS, **P)) for P in plist])
    for r, P in zip(rows, plist): r["params"] = {k: _clamp(dict(PARAMS, **P))[k] for k in JOG}
    o = dict(row=ID, bench=bench, mode=SC_.B.mode, n_near=len(SC_.poses), wear_secs=SC_.secs_wear, control={k: SC_.r0.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
             base={k: v for k, v in SC_.base.items() if k not in ("pose_min", "l2")}, base_pose_min=SC_.base["pose_min"], rows=rows, secs=round(time.time() - t, 1))
    if outp: json.dump(o, open(outp, "w"), indent=1, default=float)
    return o, SC_


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "scan":
        o, _ = scan_main(par if isinstance(par, list) else [par], sys.argv[3] if len(sys.argv) > 3 else "bench", sys.argv[4] if len(sys.argv) > 4 else None)
        print(json.dumps(dict(bench=o["bench"], mode=o["mode"], n_near=o["n_near"], control=o["control"], wear_secs=o["wear_secs"]), default=float))
        for r in o["rows"]:
            print(json.dumps(dict(p=r["params"], gap=r["gap"], near1=r["near1"], p01=r["gap_probe0.1"], p02=r["gap_probe0.2"], p035=r["gap_probe0.35"],
                                  shell=r["shell12_poses"], ib14=r["inband14"], l2min=r["l2_min_taken"], p139=r["pose_min"].get(139) if o["bench"] == "bench" else None), default=float))
        sys.exit()
    if mode in ("frozen", "held"):
        t = time.time(); out = {"frozen": frozen_bench, "held": frozen_held}[mode](par); out["params"] = par
        out["row"] = ID; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(row=ID, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"),
                              contacts=out.get("contact_poses"), stopped=out.get("stopped"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(row=ID, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r.get("inband10"), contact=r["contact"], honest=r.get("honest"),
                          why=r.get("why"), probe={k: r.get(k) for k in ("gap_probe0.1", "gap_probe0.2", "gap_probe0.35", "probe0.1_poses", "probe0.2_poses", "shell12_poses")},
                          jog=r.get("jog"), parts_L2=(r.get("parts_ib14") or {}).get("L2"), secs=round(time.time() - t)), default=float))
