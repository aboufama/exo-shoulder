"""Concept model crest-knee-3r: the verified pin-knee 3R (skin-normal-3r-pin-knee, cx 0 under simplicity v2.2) moved to
the deltoid-crest seats, with link 2 flying over the WHOLE member 3 (E strap + E boss + knee + pad) and an optional J3
own-angle stop (dowel in an arc slot between link 2 and member 3). 0 passive translations, 2 passive pins (the cuff
knee, MR63ZZ pairs, outside the DOF count), 3 active O20 hubs.

Built on docs/concepts/models/skin-normal-3r-pin-knee.py UNCHANGED (its Design / IK / two-circle knee closure / VModel
rules / part-part clearances / near-touch / contact-only walls and crowns). What this file adds:
  * fly=1   link 2's avoid set includes the E strap and boss (the crest seats put link 2's free sector about J3 at 43-62
            deg vs H1's 117.5, so link 2 must cross over member 3, not only over the knee and pad); the E strap is then a
            box from hub 3's rim to the E boss at member 3's full height (f3 .. top + T_LINK) for the fly-over check.
  * j3stop=1  a J3 OWN-angle stop: q3' = q3 + phi (member 3 vs link 2). Search: the window is the kept poses' q3' set
            minus its largest gap, shrunk by j3stop_margin. Claim: the window is FROZEN (j3win = [lo, width]) from the
            search bench into Bench(110,360) / held out (round-14 judge rule: explicit window, fitted on search, frozen).
  * kj=1   JOGGLED knee link (JogModel): pin a's E boss and pin b's arm pad at their own levels tr_a / tr_b, the knee
            link a bent bar stepping between them (<= 60 deg ramp); kinematics unchanged. kj=0 (default) = the flat knee.
  * frozen(): wears the search-bench shape (heights, knee centre m, E profile, J3 window) on Bench(nc, nw) without refit.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/crest-knee-3r.py check|redteam '<json params>' [--big]
    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 python3 docs/concepts/models/crest-knee-3r.py frozen '<json params>' out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_sp = importlib.util.spec_from_file_location("pinknee_for_crest", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
PK = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(PK)
S = PK.S; D2R = math.pi / 180
ID = "crest-knee-3r"
NAME = "Deltoid-crest seats on the pin-knee chain: the flat two-pin knee replaces the long neck"

# crest seats (round-14 proposer cell C1, the best measured crest cell; J1 back-of-acromion top, J3 on the deltoid crest)
PARAMS = dict(PK.PARAMS)
PARAMS.update(az1=100.0, el1=62.0, az2=19.64, el2=47.82, wd=92.0, wa=-5.0, b3=0.28,
              lE=70.0, lc=28.0, phiE=10.0, phib=-100.0, ang_min=26.0, stk=6.0,   # MR63ZZ knee pins (lead's build rule)
              h2cap=64.0, fly=1, j3stop=1, j3stop_margin=1.0)
ANG_MIN_RULE = 25.22                                          # knee window rule (ROUNDS.md round 14: hard search-box edge)


class Model(PK.Model):
    def __init__(self, B, params=None, verbose=False):
        P = dict(PARAMS); P.update(params or {})
        super().__init__(B, P, verbose)
        self.q3p = np.degrees((self.q[:, 2] + self.K["phi"]) % (2 * np.pi))
        win = self.p.get("j3win")
        if win is not None:                                   # frozen J3 window: poses outside it are STOPPED (not taken)
            lo, wid = float(win[0]), float(win[1]); rel = (self.q3p - lo) % 360
            stop = self.kin_ok & ~(rel <= wid)
            self.why[stop] = "j3stop"; self.kin_ok &= ~stop; self.j3stop_info = dict(lo=lo, width=wid, stopped=int(stop.sum()))

    def _boxes_at(self, i):
        out = super()._boxes_at(i)
        if not self.p.get("fly"): return out
        D = self.D; P = D.p; fr = self.fr; lE = float(P["lE"]); r3 = self.hr[2]
        f3 = getattr(self, "_f3_fit", None); tr = self._tr_fit
        if f3 is None: return out
        top = max(f3, tr, getattr(self, "_hEmax", f3)) + S.T_LINK
        x0, x1 = r3 + 1.0, lE + PK.BOSS_R
        Rk = np.stack([fr["eE"], fr["nE"], D.sn], 1)
        ck = D.c[2] + 0.5 * (x0 + x1) * fr["eE"] + 0.5 * (f3 + top) * D.sn
        R, t = self.T(3, i)
        out["E"] = (R @ ck + t, R @ Rk, np.array([0.5 * (x1 - x0), max(S.W_LINK / 2, PK.BOSS_R), 0.5 * (top - f3)]))
        return out

    def fit(self):
        D = self.D; P = D.p
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        g = self._geo(); self.g = g; off_k = P["tp"] + S.RUN
        order = ["hub1", "hub2", "hub3", "boss", "pad", "knee", "E"]
        items = [(g[n][0], g[n][1], np.broadcast_to(g[n][2], g[n][1].shape).copy(), 140.0) for n in order]
        res = dict(zip(order, self.needed(items, poses)))
        H = {"hub1": res["hub1"], "hub2": res["hub2"], "h3": res["hub3"],
             "stack": np.concatenate([res["boss"], res["pad"], res["knee"] - off_k], 1)}
        self.Hneed, self.Lneed = H, {}; self._HE = res["E"]
        self.greedy_drop(links=False); keep1 = ~self.drop
        if P.get("h2cap"): keep1 &= H["hub2"].max(1) <= float(P["h2cap"]); self.drop = ~keep1
        f1 = H["hub1"][keep1].max(); f2 = H["hub2"][keep1].max(); tr = H["stack"][keep1].max(); f3 = H["h3"][keep1].max()
        geo = PK._Geo(D, self.hr); geo.add_links(f1, f2, f3); self.geo = geo
        self._tr_fit = tr; self._f3_fit = f3; self._hEmax = float(self._HE[keep1].max())
        items, idx = [], []
        for lk in geo.links:
            avoid = (("knee", "pad", "E") if P.get("fly") else ("knee", "pad")) if lk["name"] == "L2" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        res = self.needed(items, poses); L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        L["E"] = [self._HE]; self.Lneed = L
        self.greedy_drop(keep0=keep1)
        if P.get("j3stop") and P.get("j3win") is None:
            q3p = self.q3p[poses]; keep = ~self.drop
            a = np.sort(q3p[keep]); gg = np.diff(np.r_[a, a[0] + 360]); k = int(np.argmax(gg)); hi = a[k]
            m = float(P.get("j3stop_margin", 1.0))
            rel = (q3p - hi) % 360
            ing = (rel > m) & (rel < gg[k] - m)                 # inside the empty arc (with margin) -> the stop blocks it
            stop = self.drop & ing
            lo_win = (hi + gg[k] - m) % 360; wid = 360 - gg[k] + 2 * m   # the ALLOWED window [lo_win, lo_win + wid]
            self.j3stop_info = dict(lo=round(float(lo_win), 2), width=round(float(wid), 2), gap_deg=round(float(gg[k]), 1),
                                    stopped=int(stop.sum()), dropped=int(self.drop.sum()))
            for i in poses[stop]: self.why[i] = "j3stop"
            self.poses_fit = poses[~stop]; self.drop = self.drop[~stop]
            for kk in list(self.Hneed): self.Hneed[kk] = self.Hneed[kk][~stop]
            self.Lneed = {kk: [r[~stop] for r in rows] for kk, rows in self.Lneed.items()}
            self._HE = self._HE[~stop]
        self.finalize()


class JogModel(Model):
    """kj=1: JOGGLED knee link. Pin a's E boss (member 3) and pin b's arm pad (cuff) sit at their OWN radial levels tr_a /
    tr_b; the knee link (a bent 3 mm bar, flats over the two O12 pin ends, one straight ramp between them <= RAMP 60 deg)
    steps from tr_a + tp + RUN at pin a to tr_b + tp + RUN at pin b. The pins stay parallel (planar knee): kinematics,
    closure and the knee window are unchanged; only where the metal sits along the pin axis changes. Lever measured as
    the first screen's limiter: one level for boss and pad over skins of different height (boss 0.43 / pad 0.85 in band).
    Levels: the least tr_a + tr_b with boss <= tr_a, pad <= tr_b, every knee sample's underside >= its need and the step
    <= tan(RAMP) x the ramp run (lc - 2 BOSS_R) - a 2-variable LP (scipy HiGHS). kj=0 is the flat knee (Model)."""

    def _knee_w(self):
        lc = float(self.p["lc"]); fr = self.fr
        s = (self.g["knee"][1] - fr["A0m"]) @ fr["eK"]                # position along the knee link from pin a
        a0, b0 = PK.BOSS_R, max(lc - PK.BOSS_R, PK.BOSS_R + 1e-6)
        w = np.clip((b0 - s) / (b0 - a0), 0.0, 1.0)                  # weight of tr_a in the underside level
        smax = math.tan(S.RAMP * D2R) * max(lc - 2 * PK.BOSS_R, 0.0)
        return w, smax

    def _levels(self, keep, tra_min=None):
        from scipy.optimize import linprog
        w, smax = self._knee_w(); H = self.Hneed
        bn = float(H["boss_n"][keep].max()); pn = float(H["pad_n"][keep].max()); kn = H["knee_n"][keep].max(0)
        if tra_min is not None: bn = max(bn, tra_min)
        A = [[-1, 0], [0, -1], [1, -1], [-1, 1]] + [[-wj, -(1 - wj)] for wj in w]
        b = [-bn, -pn, smax, smax] + [-float(k) for k in kn]
        r = linprog([1, 1], A_ub=np.array(A), b_ub=np.array(b), bounds=[(None, None)] * 2, method="highs")
        if not r.success: t = max(bn, pn, float(kn.max())); return t, t
        return float(r.x[0]), float(r.x[1])

    def fit(self):
        D = self.D; P = D.p
        poses = np.nonzero(self.kin_ok)[0]; self.poses_fit = poses
        g = self._geo(); self.g = g; off_k = P["tp"] + S.RUN
        order = ["hub1", "hub2", "hub3", "boss", "pad", "knee", "E"]
        items = [(g[n][0], g[n][1], np.broadcast_to(g[n][2], g[n][1].shape).copy(), 140.0) for n in order]
        res = dict(zip(order, self.needed(items, poses)))
        w, _ = self._knee_w(); ka = w >= 0.5
        kn = res["knee"] - off_k
        H = {"hub1": res["hub1"], "hub2": res["hub2"], "h3": res["hub3"],
             "stack": np.concatenate([res["boss"], kn[:, ka]], 1), "stack_b": np.concatenate([res["pad"], kn[:, ~ka]], 1),
             "boss_n": res["boss"], "pad_n": res["pad"], "knee_n": kn}
        self.Hneed, self.Lneed = H, {}; self._HE = res["E"]
        self.greedy_drop(links=False); keep1 = ~self.drop
        if P.get("h2cap"): keep1 &= H["hub2"].max(1) <= float(P["h2cap"]); self.drop = ~keep1
        f1 = H["hub1"][keep1].max(); f2 = H["hub2"][keep1].max(); f3 = H["h3"][keep1].max()
        tra, trb = self._levels(keep1)
        geo = PK._Geo(D, self.hr); geo.add_links(f1, f2, f3); self.geo = geo
        self._tr_fit = tra; self._trb_fit = trb; self._f3_fit = f3; self._hEmax = float(self._HE[keep1].max())
        items, idx = [], []
        for lk in geo.links:
            avoid = (("knee", "pad", "E") if P.get("fly") else ("knee", "pad")) if lk["name"] == "L2" else ()
            for ri, (dv, keep, sarc) in enumerate(lk["rows"]):
                items.append((lk["mem"], np.zeros((len(dv), 3)), dv, 170.0, avoid)); idx.append((lk["name"], ri))
        res = self.needed(items, poses); L = {}
        for (nm, ri), r in zip(idx, res): L.setdefault(nm, []).append(r)
        L["E"] = [self._HE]; self.Lneed = L
        self.greedy_drop(keep0=keep1)
        if P.get("j3stop") and P.get("j3win") is None:
            q3p = self.q3p[poses]; keep = ~self.drop
            a = np.sort(q3p[keep]); gg = np.diff(np.r_[a, a[0] + 360]); k = int(np.argmax(gg)); hi = a[k]
            m = float(P.get("j3stop_margin", 1.0))
            rel = (q3p - hi) % 360
            ing = (rel > m) & (rel < gg[k] - m)
            stop = self.drop & ing
            lo_win = (hi + gg[k] - m) % 360; wid = 360 - gg[k] + 2 * m
            self.j3stop_info = dict(lo=round(float(lo_win), 2), width=round(float(wid), 2), gap_deg=round(float(gg[k]), 1),
                                    stopped=int(stop.sum()), dropped=int(self.drop.sum()))
            for i in poses[stop]: self.why[i] = "j3stop"
            self.poses_fit = poses[~stop]; self.drop = self.drop[~stop]
            for kk in list(self.Hneed): self.Hneed[kk] = self.Hneed[kk][~stop]
            self.Lneed = {kk: [r[~stop] for r in rows] for kk, rows in self.Lneed.items()}
            self._HE = self._HE[~stop]
        self.finalize()

    def greedy_drop(self, keep0=None, links=True):
        """the seed's greedy drop with the joggle's second rigid level (pad + knee half b) as its own group"""
        H = self.Hneed; sb = H.get("stack_b")
        if sb is None: return super().greedy_drop(keep0, links)
        poses = self.poses_fit; kind = np.array([self.B.kind[i] for i in poses])
        ncl = sum(1 for k in self.B.kind if k == "clip"); nws = len(self.B.kind) - ncl; L = self.Lneed; BIG = S.BIG
        groups = [("g", H["hub1"]), ("g", H["hub2"]), ("g", H["stack"]), ("g", sb)] + ([("g", H["h3"])] if "h3" in H else []) + ([("s", r) for rows in L.values() for r in rows] if links else [])
        keep = np.ones(len(poses), bool) if keep0 is None else keep0.copy()
        for typ, M in groups: keep &= ~(M >= BIG / 2).any(1)
        def score(keep):
            if not keep.any(): return 1e9
            cl = keep & (kind == "clip"); inb = tot = 0
            for typ, M in groups:
                top = M[keep].max() if typ == "g" else M[keep].max(0)
                ex = top - M[cl]; inb += float((ex <= 12.0).sum()); tot += ex.size
            ib = inb / max(tot, 1); fol = cl.sum() / ncl; rch = (keep & (kind == "ws")).sum() / nws
            con = (~keep).sum() / len(keep)
            return 100 * (max(0, .9 - ib) + max(0, .95 - fol) + max(0, .9 - rch)) + 100 * con
        cur = score(keep)
        for it in range(60 if self.p.get("drop", 1) else 0):
            best, bk = cur, None
            for typ, M in groups:
                need = np.where(keep, M.max(1), -1e9); order = np.argsort(-need)
                for k in range(1, 9):
                    sel = order[:k]; sel = sel[keep[sel]]
                    if not len(sel): continue
                    k2 = keep.copy(); k2[sel] = False; sc = score(k2)
                    if sc < best - 1e-6: best, bk = sc, k2
            if bk is None: break
            keep = bk; cur = best
        self.drop = ~keep

    def finalize(self):
        D = self.D; P = D.p; keep = ~self.drop; g = self.g; off_k = P["tp"] + S.RUN
        H = self.Hneed
        f1 = H["hub1"][keep].max(); f2 = H["hub2"][keep].max(); f3 = H["h3"][keep].max()
        tra, trb = self._levels(keep)
        hE = self._HE[keep].max(0) if keep.any() else self._HE.max(0)
        xs, rE, f3, tra2 = self._E_profile(hE, f3, tra)
        if tra2 > tra + 1e-9: tra, trb = self._levels(keep, tra_min=tra2)
        self.f = [f1, f2, f3]; self.tr = tra; self.tr_b = trb; self.zb = tra
        w, _ = self._knee_w(); self._kw = w; klev = tra * w + trb * (1 - w)
        u, c = D.u, D.c; k = math.tan(S.RAMP * D2R); rL = {nm: [r[keep].max(0) for r in rows] for nm, rows in self.Lneed.items()}
        lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): S.UP, ("L2", 2): S.UP}; F = [f1, f2, f3]; self.link_pts = {}
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
        sn = D.sn
        hx = np.interp(self._Ex, xs, rE); self.hEx = hx
        self.rigid = {"hub1": (0, g["hub1"][1] + f1 * u[0]), "hub2": (1, g["hub2"][1] + f2 * u[1]), "hub3": (3, g["hub3"][1] + f3 * u[2]),
                      "E": (3, g["E"][1] + hx[:, None] * sn), "boss": (3, g["boss"][1] + tra * sn), "pad": (5, g["pad"][1] + trb * sn),
                      "knee": (6, g["knee"][1] + (klev + off_k)[:, None] * sn)}
        self._contact_only(); self._solids()

    def _contact_only(self):
        """the flat knee's contact-only set with the pad ring at tr_b and the knee link's edges / top on the joggle"""
        super()._contact_only()
        D = self.D; P = D.p; tp = P["tp"]; fr = self.fr; sn = D.sn; tra, trb = self.tr, self.tr_b
        ang = np.linspace(0, 2 * np.pi, 32, endpoint=False); e, f = S.frame_of(sn)
        out = [(m, X) for (m, X) in self.contact if m not in (5, 6)]          # rebuild the pad (5) and knee (6) entries
        ring = PK.PAD_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
        for z in (trb, trb + tp): out.append((5, fr["Bm"] + z * sn + ring))
        out.append((5, self.rigid["pad"][1] + tp * sn))
        lc = float(P["lc"]); Lk = lc + 2 * PK.BOSS_R; W = PK.KNEE_W; a0, b0 = PK.BOSS_R, max(lc - PK.BOSS_R, PK.BOSS_R + 1e-6)
        def lev(x): return tra * np.clip((b0 - x) / (b0 - a0), 0, 1) + trb * (1 - np.clip((b0 - x) / (b0 - a0), 0, 1))
        pts = []
        for dz in (0.0, tp):
            for x in np.arange(-PK.BOSS_R, lc + PK.BOSS_R + 1e-6, S.SPACING): pts += [(x, -W / 2, lev(x) + tp + S.RUN + dz), (x, W / 2, lev(x) + tp + S.RUN + dz)]
            for y in np.arange(-W / 2, W / 2 + 1e-6, S.SPACING):
                for x in (-PK.BOSS_R, lc + PK.BOSS_R): pts += [(x, y, lev(x) + tp + S.RUN + dz)]
        a = np.array(pts)
        out.append((6, fr["A0m"] + a[:, :1] * fr["eK"] + a[:, 1:2] * fr["nK"] + a[:, 2:] * sn))
        out.append((6, self.rigid["knee"][1] + tp * sn))
        self.contact = out

    def _boxes_at(self, i):
        out = super()._boxes_at(i)
        D = self.D; P = D.p; tp = P["tp"]; fr = self.fr; lc = float(P["lc"])
        tra = self._tr_fit; trb = getattr(self, "_trb_fit", tra)
        if "knee" in out:                                           # one box over the whole joggle (conservative)
            lo = min(tra, trb) + tp + S.RUN; hi = max(tra, trb) + 2 * tp + S.RUN
            Rk = np.stack([fr["eK"], fr["nK"], D.sn], 1); ck = fr["A0m"] + (lc / 2) * fr["eK"] + 0.5 * (lo + hi) * D.sn
            R, t = self.T(6, i); out["knee"] = (R @ ck + t, R @ Rk, np.array([lc / 2 + PK.BOSS_R, PK.KNEE_W / 2, 0.5 * (hi - lo)]))
        if "pad" in out:
            Rp = np.stack([D.sa, D.st, D.sn], 1); cp = fr["Bm"] + (trb + tp / 2) * D.sn
            R, t = self.T(5, i); out["pad"] = (R @ cp + t, R @ Rp, np.array([PK.PAD_R, PK.PAD_R, tp / 2]))
        return out

    def _boxes_at_final(self, i):
        a0, b0 = self._tr_fit, getattr(self, "_trb_fit", None); self._tr_fit = self.tr; self._trb_fit = self.tr_b
        try: return self._boxes_at(i)
        finally: self._tr_fit = a0; self._trb_fit = b0


_FlatModel = Model


def _factory(B, params=None, verbose=False):
    P = dict(PARAMS); P.update(params or {})
    return (JogModel if P.get("kj") else _FlatModel)(B, params, verbose)


PK.Model = _factory                                           # PK._report / audit build this model (kj picks the knee)


def report(B, params):
    r, M = PK._report(B, params)
    r["j3stop"] = getattr(M, "j3stop_info", None)
    r["why"] = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "j3stop", "skin", "parts", "contact")}
    return r, M


def evaluate(B, params):
    r, M = report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = report(B, params); r.pop("params", None); return r


COPY = ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "_f3_fit", "_hEmax", "cyl", "box", "strap", "cyl_surf",
        "Emid", "Hneed", "Lneed", "hEx", "_Ex", "_h12", "tr_b", "_trb_fit", "_kw")


def frozen(P, nc=110, nw=360, keep=False):
    """fit on Bench(60,160) FAST, wear that exact shape (heights, knee centre m, E profile, J3 window) on Bench(nc,nw)"""
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    Base = JogModel if dict(PARAMS, **P).get("kj") else _FlatModel
    M1 = Base(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    ji = getattr(M1, "j3stop_info", None)
    if P2.get("j3stop") and ji: P2["j3win"] = [ji["lo"], ji["width"]]

    class Frozen(Base):
        def fit(self):
            for a in COPY:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=nc, n_ws=nw); M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "j3stop", "skin", "parts", "contact")}
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=why, parts_pairs=r.get("parts_pairs"),
               parts_ib14=r.get("parts_ib14"), j3win=P2.get("j3win"), m_fix=P2["m_fix"], f=[round(float(x), 2) for x in M1.f], tr=round(float(M1.tr), 2),
               tr_b=round(float(getattr(M1, "tr_b", M1.tr)), 2),
               knee_ang=[round(float(M.K["ang"][M.kin_ok].min()), 1), round(float(M.K["ang"][M.kin_ok].max()), 1)] if M.kin_ok.any() else None,
               audit=PK.audit(M, B))
    if keep: return out, M, B
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        t = time.time(); out = frozen(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    nc, nw = (110, 360) if "--big" in sys.argv else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    r, M = report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], "knee", r["knee"],
          "f", r.get("f"), "j3stop", r["j3stop"], f"{time.time() - t:.0f}s", B.mode)
    print("parts", r.get("parts_ib14"), r.get("parts_pairs"), "min clear", r.get("min_clear_taken"), "res", r.get("res_max"))
