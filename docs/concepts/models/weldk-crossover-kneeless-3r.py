"""Concept model weldk-crossover-kneeless-3r (round 301, O1 overhead track): the KNEELESS welded crossover 3R at cx 0.

  scapula handler -> J1 (O20 v5, ACTIVE R, acromion top, the lead's seat az 95.39 el 67.90, axis on the GH ray) ->
  link 1 (straight 8 x 3 Ti bent bar, a1 ~40.5 deg) -> J2 (O20 v5, ACTIVE R, axis on the GH ray, rest seat RE-SOLVED
  from (a1, a2, branch) on the two cones about J1 and J3) -> link 2 (a2 ~57.2 deg) on hub 3's LOWER plate [F3, F3 + 3]
  -> J3 (O20 v5, ACTIVE R, axis = the GH ray wdir(wd, wa), b3 = 0: its line passes through GH, NO J3 stop) -> member 3
  = ONE rigid Ti bracket: hub 3's UPPER member (F3 + 3.15) + the E leg, which leaves hub 3 ABOVE link 2 and must stay
  >= 0.15 mm over link 2's top wherever they overlap in plan view (stacked-pair rule, over every kept pose) + the former
  knee link re-made as the bracket's pad leg at the bracket level + the arm pad, bolted to BOTTOM (2x M3). No knee pins,
  no K, no drive, no stop dowel. 3 ACTIVE DOF, 0 passive DOF, 0 passive translations.

WHY THE KNEE CARRIES NOTHING (exact, asserted on every bench): J1, J2, J3 on GH rays -> the three hub lines meet at GH,
c3 = 0, the cuff drift s = 0 on every pose: member 3 moves with the arm (the plain spherical 3R with a rigid cuff,
the baseline-3r topology). The model asserts ptp(knee angle) < 0.5 deg and |s| < 0.05 mm over every kinematic pose
('knee_rigid'); a violation marks the result dishonest.

WHAT THIS FILE CHANGES against weldk-overstrap-pinknee-3r.py (loaded unchanged as its own module copy, with H1 under it):
  * b3 = 0 forced; knee window dropped (a rigid bracket has no knee angle; straight E + pad leg allowed);
  * the J2 rest seat (az2, el2) is solved from (a1, a2, br) exactly (cone intersection about the J1 and J3 rest axes);
  * boss, pad and the former knee link all sit at ONE bracket level tr (no pin stack), plate thickness 3.0 mm
    (stk = 2 T_LINK + RUN -> tp = 3.0), all sampled as skin-facing metal (underside fitted, edges and top contact-only);
  * the E-leg profile keeps H1's boss continuity (E may ramp down to the boss <= 60 deg) without the knee-link-over-E
    bound; the stacked-pair link-2 requirement is kept;
  * part pairs: knee-vs-E and pad-vs-E dropped (one body); bracket-vs-hub 3 >= 0.15 mm kept (link 2's half of hub 3
    turns over it); bracket vs hub 1 / hub 2 / L1 / L2 >= 1 mm as before; E-over-L2 stacked >= 0.15 mm.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/weldk-crossover-kneeless-3r.py [check] ['<json>']
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/weldk-crossover-kneeless-3r.py frozen|held '<json>' out.json
    python3 docs/concepts/models/weldk-crossover-kneeless-3r.py ghred '<json>'      (GH-offset misfit red team, K1 reading)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_sp = importlib.util.spec_from_file_location("weldk_overstrap_for_kneeless", os.path.join(HERE, "weldk-overstrap-pinknee-3r.py"))
WO = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(WO)
PK = WO.PK; S = PK.S; unit = S.unit; D2R = math.pi / 180; BOSS_R = PK.BOSS_R
ID = "weldk-crossover-kneeless-3r"
NAME = "Kneeless welded crossover 3R (rigid bracket over link 2, no knee, no K, no drive)"
KNEE_TOL_DEG, S_TOL_MM = 0.5, 0.05
BR_T = S.T_LINK

PARAMS = dict(WO.PARAMS)
PARAMS.update(az1=95.3929, el1=67.8974, wd=105.0, wa=10.0, b3=0.0, a1=40.5, a2=57.22, br=-1,
              lE=65.0, lc=80.0, phiE=-5.0, phib=-90.0, ang_min=0.0, stk=2 * S.T_LINK + S.RUN,
              rad1=10.0, rad2=10.0, rad3=10.0, over=1, dg=0.0, kinv=0, near1=1)

_REST = {}


def _rest():
    if not _REST:
        sp_ = importlib.util.spec_from_file_location("osn_for_kneeless_cross", os.path.join(HERE, "offset-skin-normal-3r.py"))
        OSN = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(OSN); _REST["Q0"] = OSN.rest()["Q0"]
    return _REST["Q0"]


def solve_j2(p):
    """J2 rest axis on the two cones: angle a1 to the J1 rest axis, a2 to the J3 rest axis (both GH rays); br picks the
    intersection side (sign of d2 . (d1 x d3)). -> (az2, el2, th_rest) or None (cones miss)"""
    Q0 = _rest(); d1 = S.bvec(p["az1"], p["el1"]); d3 = unit(Q0 @ S.w_dir(p["wd"], p["wa"]))
    c = float(d1 @ d3); n = unit(np.cross(d1, d3)); A1, A2 = math.radians(p["a1"]), math.radians(p["a2"])
    den = 1 - c * c; Aq = (math.cos(A1) - c * math.cos(A2)) / den; Bq = (math.cos(A2) - c * math.cos(A1)) / den
    p0 = Aq * d1 + Bq * d3; h2 = 1 - p0 @ p0
    if h2 < 0: return None
    d2 = p0 + float(np.sign(p.get("br", 1)) or 1) * math.sqrt(h2) * n
    el = math.degrees(math.asin(float(np.clip(d2[1], -1, 1)))); az = math.degrees(math.atan2(d2[2], -d2[0]))
    return az, el, math.degrees(math.acos(float(np.clip(c, -1, 1))))


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def clamp(p):
    p = dict(PARAMS, **p)
    p["b3"] = 0.0; p["b1"] = 0.0; p["b2"] = 0.0; p["ang_min"] = 0.0; p["kinv"] = 0; p["over"] = 1
    p["stk"] = 2 * S.T_LINK + S.RUN
    p["a1"] = _c(p["a1"], 36.0, 46.0); p["a2"] = _c(p["a2"], 50.0, 64.0)
    p["wd"] = _c(p["wd"], 95.0, 112.0); p["wa"] = _c(p["wa"], 0.0, 16.0)
    p["lE"] = _c(p["lE"], 25.0, 90.0); p["lc"] = _c(p["lc"], 15.0, 115.0)
    p["dg"] = _c(p.get("dg", 0.0), 0.0, 40.0)
    sj = solve_j2(p)
    if sj is not None: p["az2"], p["el2"] = round(sj[0], 4), round(sj[1], 4)
    p["_j2_ok"] = sj is not None
    return p


class KLDesign(PK.Design):
    def knee(self, s):
        K = super().knee(s)
        K["ok"] = np.ones(len(np.atleast_2d(s)), bool)              # a rigid bracket: no knee window, no reach limit
        return K


PK.Design = KLDesign                                             # this module's own copy of H1 (WO's PK)


class Model(WO.Model):
    def __init__(self, B, params=None, verbose=False):
        p = clamp(dict(params or {}))
        super().__init__(B, p, verbose)
        D = self.D; ok = self.kin_ok
        a1 = math.degrees(math.acos(float(np.clip(D.u[0] @ D.u[1], -1, 1)))) if hasattr(D, "u") else None
        sabs = float(np.abs(self.s).max()) if len(self.s) else 0.0
        ang = self.K["ang"]; kp = float(np.ptp(ang[np.isfinite(ang)])) if np.isfinite(ang).any() else 0.0
        self.knee_rigid = dict(knee_ptp_deg=round(kp, 4), s_max_mm=round(sabs, 4), ok=bool(kp < KNEE_TOL_DEG and sabs < S_TOL_MM),
                               a_deg=[round(math.degrees(a), 3) for a in D.A], c_mm=[round(float(np.linalg.norm(c)), 3) for c in D.c])
        self.fix = dict(self.fix); self.fix["knee_rigid"] = self.knee_rigid["ok"]

    def _lv(self, tr):
        return tr, tr                                           # boss, pad and pad leg: one bracket plate at tr

    def fit(self):
        """= the sibling's fit with the boss, pad and pad leg at ONE level (no pin stack)"""
        D = self.D; P = D.p
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        g = self._geo(); self.g = g
        order = ["hub1", "hub2", "hub3", "boss", "pad", "knee", "E"]
        items = [(g[n][0], g[n][1], np.broadcast_to(g[n][2], g[n][1].shape).copy(), 140.0) for n in order]
        res = dict(zip(order, self.needed(items, poses)))
        st = np.concatenate([res["boss"], res["pad"], res["knee"]], 1)
        H = {"hub1": res["hub1"], "hub2": res["hub2"], "h3": res["hub3"], "stack": st}
        self.Hneed, self.Lneed = H, {}; self._HE = res["E"]
        self.greedy_drop(links=False); keep1 = ~self.drop
        f1 = H["hub1"][keep1].max(); f2 = H["hub2"][keep1].max(); tr = H["stack"][keep1].max(); f3 = H["h3"][keep1].max()
        geo = PK._Geo(D, self.hr); geo.add_links(f1, f2, f3); self.geo = geo
        self._tr_fit = tr
        items, idx = [], []
        for lk in geo.links:
            avoid = ("knee", "pad") if lk["name"] == "L2" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        res = self.needed(items, poses); L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        L["E"] = [self._HE]; self.Lneed = L
        self.greedy_drop(keep0=keep1)
        self.finalize()

    def _E_profile(self, hE, f3, tr):
        """E underside per station: >= fitted need and the stacked-pair requirement over link 2, = F3 + UP at the rim,
        continuous with the bracket plate at the boss (<= 60 deg ramps both ways); no knee link rides over E here"""
        up = S.UP
        x = self._Ex; xs = np.unique(np.round(x, 6)); k = math.tan(S.RAMP * D2R)
        need = np.array([hE[np.isclose(x, v)].max() for v in xs])
        if getattr(self, "_req", None) is not None: need = np.maximum(need, self._req)
        lb = float(self.p["lE"]) - BOSS_R
        for _ in range(8):
            lo_b = tr - k * np.abs(xs - lb)
            r = np.maximum(need, np.maximum(f3 + up - k * np.abs(xs - self.hr[2]), lo_b))
            r = np.max(r[None, :] - k * np.abs(xs[:, None] - xs[None, :]), axis=1)
            r0 = r[0] - k * abs(xs[0] - self.hr[2]); r1 = r[-1] - k * abs(lb - xs[-1])
            ch = False
            if r0 > f3 + up + 0.15: f3 = r0 - up; ch = True
            if r1 > tr + 0.15: tr = r1; ch = True
            if not ch: break
        return xs, r, f3, tr

    def collide(self, i):
        """the sibling's checks with the same-body pairs removed: knee-E and pad-E (one bracket)"""
        out = WO.Model.collide(self, i)
        lc = dict(self.last_clear)
        for k in ("knee-E", "pad-E"): lc.pop(k, None)
        self.last_clear = lc
        adj_keys = ("E-L2stack", "knee-hub3")
        c = [v for k, v in lc.items() if k not in adj_keys]
        o = min(c) if c else 1e9
        if min(lc.get(k, 1e9) for k in adj_keys) < self.ADJ - 1e-6: o = min(o, -1.0)
        return o


def _report(B, params):
    p = clamp(dict(params or {}))
    if not p["_j2_ok"]:
        return dict(gap=999.0, reach=0.0, follow=0.0, inband14=0.0, inband10=0.0, contact=0.0, why={"j2": 1}, honest=True,
                    params=p), None
    M = Model(B, p)
    if not M.kin_ok.any():
        B.reset(); r = B.report(); r["why"] = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure")}
        r["honest"] = True; r["params"] = M.p; r["knee_rigid"] = M.knee_rigid; return r, M
    r = M.run(); D = M.D
    r["seats"] = dict(tilt_deg=D.seats["tilt_deg"], a_deg=[round(math.degrees(a), 2) for a in D.A],
                      offset_mm=[round(float(np.linalg.norm(c)), 1) for c in D.c], rest_err_deg=round(D.rest_err, 4),
                      az2=p["az2"], el2=p["el2"])
    r["knee_rigid"] = M.knee_rigid
    r["E_lift"] = dict(rim=round(M.f[2] + S.UP, 2), max_under=round(float(M._rE.max()), 2), req_tr=None if M.req_tr is None else round(M.req_tr, 2))
    r["tr"] = round(float(M.tr), 2)
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    src = M.p if M is not None else r["params"]
    p = {k: v for k, v in src.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    """fit on Bench(60,160) FAST, wear that exact shape (heights, E profile) on Bench(nc,nw) (CB_EXACT=1 -> exact
    distances) without refit; = the sibling's / H1's frozen() on this model. nc = nw = -1 -> held out"""
    P = clamp(dict(P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = Model(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(Model):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_h12", "_xsE", "_rE", "_req", "req_tr", "contact"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    if nc < 0:
        import osn_polish as OP; B = OP.held_bench(110, 360)          # the held-out clips + held-out workspace poses
    else: B = CB.Bench(n_clip=nc, n_ws=nw)
    M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    st = [M.stacked(i) for i in taken]
    return dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
                parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), f=[round(float(x), 2) for x in M.f], tr=round(float(M.tr), 2),
                E_profile=dict(rim=round(M.f[2] + S.UP, 2), xs=[round(float(v), 1) for v in M._xsE], under=[round(float(v), 2) for v in M._rE]),
                stacked_min_taken=round(min(st), 3) if st else None, knee_rigid=M.knee_rigid,
                seats=dict(az2=P["az2"], el2=P["el2"], a_deg=[round(math.degrees(a), 3) for a in M.D.A]),
                m_fix=P2["m_fix"]), M, B


def redteam_gh(par=None, nc=110, nw=360, mags=(3.0, 5.0, 10.0), liner=3.0):
    """GH-offset misfit (kneeless-roller-knuckle-3r.py redteam_gh, the K1 no-slide reading): the chain is spherical about
    the NOMINAL GH, the arm turns about the TRUE centre g; with the bracket bolted at rest the misfit is (I - R) g,
    R = Q Q0^T, over every pose of Bench(nc, nw) and 26 directions of g per magnitude; share within the liner budget,
    with one cuff slide along the humerus, and what a planar knee in hub 3's plane would leave"""
    P = clamp(dict(par or {})); D = KLDesign(P); u3 = D.u[2]
    Z = CB._poses_all(); B = CB.Bench(n_clip=nc, n_ws=nw); Q = Z["HG"][B.idx].astype(float); Q0 = _rest()
    dirs = np.array([[x, y, z] for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)], float)
    dirs /= np.linalg.norm(dirs, axis=1)[:, None]
    Rr = np.einsum("nij,kj->nik", Q, Q0); ax_arm = np.array([0.0, -1.0, 0.0]); out = {}
    for mg in mags:
        mis = np.einsum("nij,kj->nki", np.eye(3)[None] - Rr, dirs * mg)
        worst = np.linalg.norm(mis, axis=2).max(1)
        armf = np.einsum("nji,nkj->nki", Q, mis)
        perp = armf - (armf @ ax_arm)[..., None] * ax_arm; wp = np.linalg.norm(perp, axis=2).max(1)
        kn = np.abs(armf @ u3).max(1)
        out[f"{mg:g}mm"] = dict(median=round(float(np.median(worst)), 2), p90=round(float(np.percentile(worst, 90)), 2),
                                max=round(float(worst.max()), 2), within_liner=round(float((worst <= liner).mean()), 3),
                                slide_median=round(float(np.median(wp)), 2), slide_within_liner=round(float((wp <= liner).mean()), 3),
                                knee_equiv_median=round(float(np.median(kn)), 2), knee_equiv_within_liner=round(float((kn <= liner).mean()), 3))
    out["n_poses"] = int(len(Q)); out["liner_mm"] = liner
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode in ("frozen", "held"):
        t = time.time(); out, M, B = frozen(par, *((-1, -1) if mode == "held" else (110, 360))); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    if mode == "ghred":
        print(json.dumps(redteam_gh(par))); sys.exit()
    nc, nw = (110, 360) if "--big" in sys.argv else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    r, M = _report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], "knee", r.get("knee_rigid"),
          "f", r.get("f"), "seats", r.get("seats"), "E", r.get("E_lift"), "tr", r.get("tr"), f"{time.time() - t:.0f}s", B.mode)
    print("parts", r.get("parts_ib14"), r.get("parts_pairs"), "min clear", r.get("min_clear_taken"), "honest", r.get("honest"))
