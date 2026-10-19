"""Concept model weldk-overstrap-pinknee-3r (round 301, O1 overhead track): the welded-K crossover pin-knee 3R at cx 0.

The H1 pin-knee chain (docs/concepts/models/skin-normal-3r-pin-knee.py, loaded UNCHANGED as its own module copy) at the
lead's J1 seat with lens A's J3 re-aim, and ONE structural change - the J3 stack order is inverted:

  scapula handler -> J1 (O20 v5, ACTIVE R, acromion top, the lead's seat az 95.39 el 67.90, axis on the GH ray) ->
  link 1 (straight 8 x 3 Ti bent bar, a1 40.5 deg) -> J2 (O20 v5, ACTIVE R, axis on the GH ray, rest seat az2 / el2) ->
  link 2 (a2 57.3 deg) on hub 3's LOWER plate [F3, F3 + 3] -> J3 (O20 v5, ACTIVE R, station wd 95 / wa 8, axis tilted
  b3 0.6 toward the skin normal, eff (104.4, 11.7), line 10.2 mm off GH, NO J3 stop) -> member 3 = hub 3's UPPER member
  (underside F3 + UP = F3 + 3.15) + the E strap, which leaves hub 3 ABOVE link 2 and must stay >= 0.15 mm over link 2's
  top wherever the two overlap in plan view (the stacked-pair rule, over every taken pose: link 2 rotates about J3
  relative to member 3) -> pin a (PASSIVE R, MR63ZZ pair) -> knee link -> pin b (PASSIVE R, MR63ZZ pair) -> arm pad ->
  cuff. No hub K, no drive, no J3 stop dowel (the lead's K, crank, roller, slipper, lug and rim lobe are deleted).

What changes against H1 (everything else is H1's code: exact IK, two-circle knee closure, knee window [ang_min, 180 -
ang_min], 10 fps continuity incl. pin a / pin b, seed VModel rules, part checks, jam rule):
  1. link 2's level at J3 = F3 (lower plate) instead of F3 + UP;
  2. the E strap's rim level = F3 + UP instead of F3, and its underside profile is raised (<= 60 deg ramps) to clear
     link 2's top + ADJ (0.15) at every E station where any link-2 sample overlaps the E footprint (|y| <= W/2 + 1 mm,
     |x - x_station| <= 2 mm) in any kept fit pose; the E boss (O12 at pin a) clears link 2's top likewise (tr);
  3. collide(): the E-L2 'adjacent at J3' kd check is REPLACED by the same plan-view stacked-pair test (E underside
     minus link-2 top over the overlap, boss underside minus link-2 top within O12 + 1 mm), < 0.15 mm = jam;
  4. stk 6.0 (MR63ZZ pairs at both knee pins, the lead's build rule), O20 at every hub.
over=0 gives H1's stack order at the same seats (the control).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/weldk-overstrap-pinknee-3r.py [check|redteam] ['<json>']
    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/weldk-overstrap-pinknee-3r.py frozen '<json>' out.json
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_sp = importlib.util.spec_from_file_location("pinknee_for_weldk_overstrap", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
PK = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(PK)
S = PK.S; unit = S.unit; D2R = math.pi / 180; BOSS_R = PK.BOSS_R
ID = "weldk-overstrap-pinknee-3r"
NAME = "Welded-K crossover pin-knee 3R (E strap over link 2, no K, no drive, no J3 stop)"

PARAMS = dict(PK.PARAMS)
PARAMS.update(az1=95.3929, el1=67.8974, az2=28.93, el2=44.90, wd=95.0, wa=8.0, b3=0.6,       # catalogue spec seats
              lE=80.0, lc=28.24, phiE=-5.81, phib=-90.0, ang_min=30.46, stk=6.0,
              rad1=10.0, rad2=10.0, rad3=10.0, over=1, dg=0.0)


class Model(PK.Model):
    ADJ = 0.15

    def __init__(self, B, params=None, verbose=False):
        super().__init__(B, dict(PARAMS, **(params or {})), verbose)

    def greedy_drop(self, keep0=None, links=True):
        """H1's greedy drop, started (first pass) without the poses whose need on a hub / the knee stack exceeds that
        part's median over the fit poses by more than dg mm (dg 0 = off = H1). The greedy is local: at the spec seats
        3 abduction poses (elev 105, axial 0) park hub 2 27 mm above its median and no single move of <= 8 poses pays;
        dg is the design's explicit parking choice (the dropped poses are recorded as contact, as every drop)"""
        dg = float(self.p.get("dg", 0) or 0)
        if keep0 is None and dg > 0:
            keep0 = np.ones(len(self.poses_fit), bool)
            for nm in ("hub1", "hub2", "h3", "stack"):
                need = self.Hneed[nm].max(1); ok = need < S.BIG / 2
                if ok.any(): keep0 &= need <= np.median(need[ok]) + dg
        return super().greedy_drop(keep0=keep0, links=links)

    # ---- link 2 at hub 3's lower plate (over=1) ----
    def _links(self, f1, f2, f3, keep):
        D = self.D; u, c = D.u, D.c; k = math.tan(S.RAMP * D2R)
        rL = {nm: [r[keep].max(0) for r in rows] for nm, rows in self.Lneed.items()}
        l23 = 0.0 if int(self.p.get("over", 1)) else S.UP
        lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): S.UP, ("L2", 2): l23}; F = [f1, f2, f3]; self.link_pts = {}
        for lk in self.geo.links:
            pts_all = []
            for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
                r = r.copy(); Sx = sarc
                for kk, end in ((lk["ka"], 0), (lk["kb"], -1)):
                    idx = np.nonzero(keep_s)[0]
                    if not len(idx): continue
                    j = idx[0] if end == 0 else idx[-1]
                    cen = c[kk] + F[kk] * u[kk]; den = float(dv[j] @ u[kk])
                    rc = (cen @ u[kk] + lvl[(lk["name"], kk)]) / max(den, 0.2)
                    r = np.maximum(r, rc - k * np.abs(Sx - Sx[j]))
                r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
                pts_all.append(dv[keep_s] * r[keep_s][:, None])
            self.link_pts[lk["name"]] = (lk["mem"], np.concatenate(pts_all) if pts_all else np.zeros((0, 3)))

    def _L2_in_m3(self, i):
        """link 2's TOP surface samples in member 3's home frame, as plan (x along E, y across E) + height along sn,
        relative to the hub-3 centre c3"""
        D = self.D; m2, P2 = self.link_pts["L2"]
        top = P2 + S.T_LINK * unit(P2)
        R2, t2 = self.T(2, i); R3, t3 = self.T(3, i)
        X = (top @ R2.T + t2 - t3) @ R3 - D.c[2]
        fr = self.fr
        return X @ fr["eE"], X @ fr["nE"], X @ D.sn, X

    def _L2_req(self, poses):
        """per E station: the lowest E underside that stays ADJ over link 2's top where they overlap in plan view, and
        the boss requirement (E boss underside = tr) - max over the given poses"""
        xs = np.unique(np.round(self._Ex, 6)); req = np.full(len(xs), -1e9); req_tr = -1e9
        A0 = self.fr["A0"] - self.D.c[2]; ax0, ay0 = float(A0 @ self.fr["eE"]), float(A0 @ self.fr["nE"])
        wy = S.W_LINK / 2 + 1.0
        for i in poses:
            x, y, h, _ = self._L2_in_m3(i)
            m = np.abs(y) <= wy
            if m.any():
                xm, hm = x[m], h[m]
                d = np.abs(xs[:, None] - xm[None, :]) <= 2.0
                hh = np.where(d, hm[None, :], -1e9).max(1)
                req = np.maximum(req, hh + self.ADJ)
            b = np.hypot(x - ax0, y - ay0) <= BOSS_R + 1.0
            if b.any(): req_tr = max(req_tr, float(h[b].max()) + self.ADJ)
        return xs, req, req_tr

    def _E_profile(self, hE, f3, tr):
        """as H1's, with the E rim at F3 + UP (over=1) and the stacked-pair requirement folded into the need"""
        up = S.UP if int(self.p.get("over", 1)) else 0.0
        x = self._Ex; xs = np.unique(np.round(x, 6)); k = math.tan(S.RAMP * D2R)
        need = np.array([hE[np.isclose(x, v)].max() for v in xs])
        if getattr(self, "_req", None) is not None: need = np.maximum(need, self._req)
        lb = float(self.p["lE"]) - BOSS_R
        for _ in range(6):
            r = np.maximum(need, np.maximum(f3 + up - k * np.abs(xs - self.hr[2]), tr - k * np.abs(xs - lb)))
            r = np.max(r[None, :] - k * np.abs(xs[:, None] - xs[None, :]), axis=1)
            r0 = r[0] - k * abs(xs[0] - self.hr[2]); r1 = r[-1] - k * abs(lb - xs[-1])
            ch = False
            if r0 > f3 + up + 0.15: f3 = r0 - up; ch = True
            if r1 > tr + 0.15: tr = r1; ch = True
            if not ch: break
        return xs, r, f3, tr

    def finalize(self):
        D = self.D; P = D.p; keep = ~self.drop; g = self.g; off_k = P["tp"] + S.RUN; H = self.Hneed
        f1 = H["hub1"][keep].max(); f2 = H["hub2"][keep].max(); tr = H["stack"][keep].max(); f3 = H["h3"][keep].max()
        hE = self._HE[keep].max(0) if keep.any() else self._HE.max(0)
        poses = self.poses_fit[keep]; self._req = None; self.req_tr = None
        for it in range(5):
            self._links(f1, f2, f3, keep)
            if int(P.get("over", 1)):
                xs, req, rtr = self._L2_req(poses); self._req = req; self.req_tr = rtr
                tr = max(tr, rtr)
            xs, rE, f3n, trn = self._E_profile(hE, f3, tr)
            moved = f3n > f3 + 1e-6
            f3, tr = f3n, trn
            if not moved: break
        self.f = [f1, f2, f3]; self.tr = tr; self.zb = tr
        u = D.u; sn = D.sn
        hx = np.interp(self._Ex, xs, rE); self.hEx = hx; self._xsE, self._rE = xs, rE
        self.rigid = {"hub1": (0, g["hub1"][1] + f1 * u[0]), "hub2": (1, g["hub2"][1] + f2 * u[1]), "hub3": (3, g["hub3"][1] + f3 * u[2]),
                      "E": (3, g["E"][1] + hx[:, None] * sn), "boss": (3, g["boss"][1] + tr * sn), "pad": (5, g["pad"][1] + tr * sn),
                      "knee": (6, g["knee"][1] + (tr + off_k) * sn)}
        self._contact_only(); self._solids()

    def stacked(self, i):
        """E / boss underside minus link 2's top over their plan-view overlap at pose i (mm; 1e9 = no overlap)"""
        x, y, h, _ = self._L2_in_m3(i); out = 1e9
        xs, rE = self._xsE, self._rE
        m = (np.abs(y) <= S.W_LINK / 2 + 1.0) & (x >= xs[0] - 2.0) & (x <= xs[-1] + 2.0)
        if m.any(): out = min(out, float((np.interp(x[m], xs, rE) - h[m]).min()))
        A0 = self.fr["A0"] - self.D.c[2]; ax0, ay0 = float(A0 @ self.fr["eE"]), float(A0 @ self.fr["nE"])
        b = np.hypot(x - ax0, y - ay0) <= BOSS_R + 1.0
        if b.any(): out = min(out, float((self.tr - h[b]).min()))
        return out

    def collide(self, i):
        """H1's checks with the E-L2 adjacency replaced by the plan-view stacked-pair test (over=1)"""
        if not int(self.p.get("over", 1)): return PK.Model.collide(self, i)
        from scipy.spatial import cKDTree
        D = self.D; P = D.p; tp = P["tp"]; tr = self.tr; fr = self.fr; h = S.T_LINK / 2
        def tf(m, X): R, t = self.T(m, i); return X @ R.T + t
        cyl = {}
        for k, (m, cen, ax) in self.cyl.items(): R, t = self.T(m, i); cyl[k] = (R @ cen + t, R @ ax)
        surf = {k: tf(m, X) for k, (m, X) in self.cyl_surf.items()}
        strap = {k: tf(m, X) for k, (m, X) in self.strap.items()}
        Em = tf(*self.Emid)
        bx = self._boxes_at_final(i)
        def vcyl(X, nm, extra=0.0): return float(self.sd_cyl(X, *cyl[nm], r=self.cyl_r[nm]).min()) - extra if len(X) else 1e9
        def vbox(X, nm, extra=0.0): cen, R, half = bx[nm]; return float(self.sd_box(X, cen, R, half).min()) - extra if len(X) else 1e9
        c = {}
        c["L2-hub1"] = vcyl(strap["L2"], "hub1", h); c["hub3-hub1"] = vcyl(surf["hub3"], "hub1"); c["L1-hub3"] = vcyl(strap["L1"], "hub3", h)
        c["hub2-hub3"] = vcyl(surf["hub2"], "hub3"); c["hub1-hub2"] = self.hub12()
        cen2, ax2 = cyl["hub2"]
        def far(X, cc, ax, rr): w = X - cc; return np.linalg.norm(w - (w @ ax)[:, None] * ax, axis=1) > rr
        A, Bq = strap["L1"][far(strap["L1"], cen2, ax2, self.hr[1] + 4)], strap["L2"][far(strap["L2"], cen2, ax2, self.hr[1] + 4)]
        if len(A) and len(Bq): c["L1-L2"] = float(cKDTree(Bq).query(A)[0].min()) - 2 * h
        for nm in ("knee", "pad"):
            c[f"{nm}-hub1"] = vbox(surf["hub1"], nm); c[f"{nm}-hub2"] = vbox(surf["hub2"], nm)
            c[f"{nm}-L1"] = vbox(strap["L1"], nm, h); c[f"{nm}-L2"] = vbox(strap["L2"], nm, h)
        c["pad-hub3"] = vbox(surf["hub3"], "pad"); c["pad-E"] = vbox(Em, "pad", h)
        c["E-hub1"] = vcyl(Em, "hub1", h); c["E-hub2"] = vcyl(Em, "hub2", h)
        if len(strap["L1"]): c["E-L1"] = float(cKDTree(strap["L1"]).query(Em)[0].min()) - 2 * h
        adj = {"E-L2stack": self.stacked(i)}                                                # adjacent at J3 (stacked)
        adj["knee-hub3"] = vbox(surf["hub3"], "knee")                                      # adjacent at pin a
        pa = tf(3, fr["A0"][None])[0]
        Ef = Em[np.linalg.norm(Em - pa, axis=1) > BOSS_R + 0.5]
        adj["knee-E"] = vbox(Ef, "knee", h) if len(Ef) else 1e9
        self.last_clear = {k: round(v, 2) for k, v in list(c.items()) + list(adj.items())}
        out = min(c.values())
        if min(adj.values()) < self.ADJ - 1e-6: out = min(out, -1.0)
        return out


def _report(B, params):
    M = Model(B, params)
    if not M.kin_ok.any():
        B.reset(); r = B.report(); r["why"] = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure")}
        r["knee"] = None; r["honest"] = True; r["params"] = M.p; return r, M
    r = M.run(); D = M.D
    r["seats"] = dict(tilt_deg=D.seats["tilt_deg"], a_deg=[round(math.degrees(a), 2) for a in D.A],
                      offset_mm=[round(float(np.linalg.norm(c)), 1) for c in D.c], rest_err_deg=round(D.rest_err, 4))
    k = M.K["ang"][M.kin_ok]
    r["knee"] = dict(ang=[round(float(k.min()), 1), round(float(k.max()), 1)] if len(k) else None, br=M.K["br"],
                     drift_span=M.drift_span, radial_span=M.radial_span, tr=round(M.tr, 1), stk=M.p["stk"])
    r["E_lift"] = dict(rim=round(M.f[2] + S.UP, 2), max_under=round(float(M._rE.max()), 2), req_tr=None if M.req_tr is None else round(M.req_tr, 2))
    r["hubs"] = list(M.hr)
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    return r, M


def evaluate(B, params):
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360, wear_idx=None):
    """fit on Bench(60,160) FAST, wear that exact shape (heights, E profile, knee centre m) on Bench(nc,nw) (CB_EXACT=1 ->
    exact distances) without refit; = H1's frozen() on this model"""
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = Model(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(Model):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_h12", "_xsE", "_rE", "_req", "req_tr"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=nc, n_ws=nw); M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    st = [M.stacked(i) for i in taken]
    return dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
                parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), f=[round(float(x), 2) for x in M.f], tr=round(float(M.tr), 2),
                E_profile=dict(rim=round(M.f[2] + S.UP, 2), xs=[round(float(v), 1) for v in M._xsE], under=[round(float(v), 2) for v in M._rE]),
                stacked_min_taken=round(min(st), 3) if st else None,
                knee_ang=[round(float(M.K["ang"][M.kin_ok].min()), 1), round(float(M.K["ang"][M.kin_ok].max()), 1)] if M.kin_ok.any() else None,
                m_fix=P2["m_fix"]), M, B


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "frozen":
        t = time.time(); out, M, B = frozen(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    nc, nw = (110, 360) if "--big" in sys.argv else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    r, M = _report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], "knee", r["knee"],
          "f", r["f"], "seats", r["seats"], "E", r.get("E_lift"), f"{time.time() - t:.0f}s", B.mode)
    print("parts", r["parts_ib14"], r["parts_pairs"], "min clear", r.get("min_clear_taken"), "res", r.get("res_max"))
