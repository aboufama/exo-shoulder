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


PK.Model = Model                                              # PK._report / audit build this model


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
        "Emid", "Hneed", "Lneed", "hEx", "_Ex", "_h12")


def frozen(P, nc=110, nw=360, keep=False):
    """fit on Bench(60,160) FAST, wear that exact shape (heights, knee centre m, E profile, J3 window) on Bench(nc,nw)"""
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = Model(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    ji = getattr(M1, "j3stop_info", None)
    if P2.get("j3stop") and ji: P2["j3win"] = [ji["lo"], ji["width"]]

    class Frozen(Model):
        def fit(self):
            for a in COPY:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=nc, n_ws=nw); M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "j3stop", "skin", "parts", "contact")}
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=why, parts_pairs=r.get("parts_pairs"),
               parts_ib14=r.get("parts_ib14"), j3win=P2.get("j3win"), m_fix=P2["m_fix"], f=[round(float(x), 2) for x in M1.f], tr=round(float(M1.tr), 2),
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
