"""spiral-lobe-longdyad-knuckle-3r (round 12, pick 1): inband-rssr-knuckle-3r's in-band RSSR K drive on an efficient long K
dyad (34/48 or 36/48), loaded UNCHANGED from docs/concepts/models/inband-rssr-knuckle-3r.py, with:

  (1) the K dyad un-clamped: bk1 26-40, bk2 38-56, stop B a1max <= bk1 + bk2 - 5.5 (stop B within 5.5 of the stretch is dead);
  (2) two hub-2 lobe laws on the parents' rocker convention (follower lift s = r_h |dK| / i_rock, i_rock = La / s_arm, lobe
      radius r(t) = r_lobe + s, pressure angle tan(pa) = k r_h / (i_rock r), k = d|dK|/dq2; t = q2 travel past the onset):
        * law_in 'spiral': the constant-pressure-angle (log-spiral) lobe, |dK|(t) = (i_rock r_lobe / r_h)(exp(tan(pa_s) t) - 1),
          the steepest law the lobe allows at every radius (the catalogue entry's law);
        * law_in 'tsp' (NEW, from the gate-0 per-pose table): the LEAST opening that holds the J1-J3 dyad margin
          m3e >= smt (frontload's 'track' law), integrated with the spiral's radius-dependent gain cap
          k <= i_rock r(t) tan(pa_s) / r_h instead of the base-radius cap, plus an optional linear floor |dK| >= kf t.
          Why: the seed's linear law opens K early (K 29-42 at th 94-104), and those over-openings put hub 2 and link 2 into
          the skin (12 of 14 contact poses); the base-cap track law sheds every one of them but its margin collapses to 0 at
          th >= 106 (gain-capped at 2.83), so 21 stretched takes fold. The spiral cap lets the late law catch up.
      Every law keeps the parents' per-t gates (th monotone, rate <= RATE_MAX, lobe PA <= pa_max, lift-off, stop B, skirt
      r <= HUB_R + 1.5) and the drive's own range truncation (RSSR transmission >= 48 at both ball ends);
  (3) the knee column (conecut-knee-knuckle-3r): the re-centred two-pin knee (lE, lc, phiE, phib params) and a physical J3
      stop q3' = q3 + knee phi >= J3MIN (env SL_J3MIN, default off; 'none' = off): poses past it are not taken (why j3stop).
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, no gears / pulleys / cables.

    IB_GHOST=all CB_EXACT=1 ... python3 docs/concepts/models/spiral-lobe-longdyad-knuckle-3r.py frozen '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("inband_for_spiral", os.path.join(HERE, "inband-rssr-knuckle-3r.py"))
IB = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(IB)
LS, SC, FL, S = IB.LS, IB.SC, IB.FL, IB.S
D2R = math.pi / 180
ID = "spiral-lobe-longdyad-knuckle-3r"
_j3 = os.environ.get("SL_J3MIN", "none")
J3MIN = None if _j3 in ("", "none") else float(_j3)
# the judge's seed (round12_ideation.md section 2: pick3's drive placement on 34/48, a1max 76.5, r_lobe 8.0, s_arm 4.0, La 24)
SEED = {"bk1": 34.0, "bk2": 48.0, "a1max": 76.5, "kK": 2.8, "La": 24.0, "s_arm": 4.0, "r_h": 15.25, "beta": -140.3619, "gam": 11.9079,
        "hl": 3.15, "zc": 0.8878, "eta": -11.1256, "r_lobe": 8.0, "smhi": 19.4639, "smlo": 5.0333, "az1": 95.3275, "el1": 67.6601,
        "az2": 46.3741, "el2": 41.5718, "wd": 66.0692, "wa": -10.7812, "b3": 0.3246, "ang_min": 25.2189, "lc": 21.5474, "phib": -57.916,
        "clay": 1, "bl_c": 2, "bl_h": 0}
PARAMS = dict(IB.PARAMS, **SEED); PARAMS.update(law_in="lin", pa_s=41.9, smt=8.0, kf=0.0, thx=0.0)
_ib_clamp = IB._clamp
GHOST = IB.GHOST


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def _clamp(p):
    want = {k: p.get(k) for k in ("bk1", "bk2", "a1max", "law_in", "pa_s", "smt", "kf", "thx")}
    law_in = want["law_in"] or "lin"
    if law_in in ("spiral", "tsp"): p["law_in"] = "track"     # the parents' clamp sets their track bookkeeping; the law is ours
    p = _ib_clamp(p)
    p["bk1"] = _c(want["bk1"] if want["bk1"] is not None else p["bk1"], 26.0, 40.0)
    p["bk2"] = _c(want["bk2"] if want["bk2"] is not None else p["bk2"], 38.0, 56.0)
    a1m = float(want["a1max"]) if want["a1max"] is not None else float(p["a1max"])
    p["a1max"] = min(a1m, p["bk1"] + p["bk2"] - 5.5)
    p["law_in"] = law_in
    p["pa_s"] = _c(want["pa_s"] if want["pa_s"] is not None else 41.9, 30.0, float(p.get("pa_max", 42.0)) - 0.1)   # the cap rides 0.1 under the gate
    p["kf"] = max(float(want["kf"] or 0.0), 0.0); p["thx"] = max(float(want["thx"] or 0.0), 0.0)
    if law_in in ("spiral", "tsp"):
        p["law_mode"] = law_in; p["law_mode_in"] = law_in
        p["smt"] = 99.0 if law_in == "spiral" else max(float(want["smt"] if want["smt"] is not None else 8.0), 5.2)
    return p


class SLDesign(FL.FLDesign):
    def law(self):
        P = self.p
        mode = P.get("law_mode")
        if mode not in ("spiral", "tsp") or P.get("emb_mode") != "rod": return super().law()
        if getattr(self, "_law", None) is not None: return self._law
        KR = FL.G.KR
        u1, u2, u3 = self.u; uK = self.uK; sp = float(np.sign(self.psiA)) or 1.0
        sg = self.q2sgn; q2hi = self._q2_at(self.th_hi, sg)
        def th3(q): return math.degrees(math.acos(max(-1, min(1, float(u1 @ (S.rotm(u2, q)[0] @ u3))))))
        s_q = 1.0 if th3(q2hi + 0.01) > th3(q2hi - 0.01) else -1.0
        ir = min(max(float(P["i_rock"]), 1.0), FL.I_ROCK_MAX); rh = max(float(P["r_horn"]), FL.R_HORN_MIN); rl0 = float(P["r_lobe"])
        tps = math.tan(float(P["pa_s"]) * D2R)
        dt = 0.1; ts = np.radians(np.arange(0.0, float(P.get("t_end", 75.0)) + 1e-6, dt)); q2t = q2hi + s_q * ts
        cpsiB = (math.cos(float(P["a1max"]) * D2R) - math.cos(float(P["bk1"]) * D2R) * math.cos(float(P["bk2"]) * D2R)) / (
            math.sin(float(P["bk1"]) * D2R) * math.sin(float(P["bk2"]) * D2R))
        dKB = abs(math.acos(max(-1, min(1, cpsiB))) - abs(self.psiA))

        def th_of(tt, kk):
            R = S.rotm(uK, sp * np.asarray(kk)); R2_ = S.rotm(u2, q2hi + s_q * np.asarray(tt))
            return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", R, np.einsum("nij,j->ni", R2_, u3)) @ u1, -1, 1)))

        def a1e_of(kk):
            return np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", S.rotm(uK, sp * np.asarray(kk)), u2) @ u1, -1, 1)))

        smt = float(P["smt"]); kf = float(P.get("kf", 0.0))
        if mode == "tsp":
            kgrid = np.radians(np.arange(0.0, math.degrees(dKB) + 0.2, 0.2)); nk = len(kgrid)
            a1g = a1e_of(kgrid); TT = np.repeat(ts, nk); KK = np.tile(kgrid, len(ts))
            thg = th_of(TT, KK).reshape(len(ts), nk); m3g = KR.dyad_margin(thg, a1g[None, :], self.a2); okg = m3g >= smt
            first = np.where(okg.any(1), np.argmax(okg, 1), nk - 1); kneed = kgrid[first]
            thx = float(P.get("thx", 0.0))
            if thx > 0:                                           # LOOK-AHEAD: open early just enough that the capped gain
                thn = th_of(ts, kneed); use = okg.any(1) & (thn <= thx)   # still meets the margin at every th <= thx
                kb = np.where(use, kneed, 0.0)
                for j in range(len(ts) - 2, -1, -1):
                    r_n = rl0 + rh * kb[j + 1] / ir
                    kb[j] = max(kb[j], kb[j + 1] - ir * r_n * tps / rh * dt * D2R)
                kneed = np.maximum(np.where(use, kneed, kneed), kb)
        else:
            kneed = np.full(len(ts), np.inf)
        kabs = np.zeros(len(ts))
        for j in range(1, len(ts)):
            r_prev = rl0 + rh * kabs[j - 1] / ir
            cap = ir * r_prev * tps / rh                              # the spiral's gain at this radius (PA = pa_s)
            want = max(kabs[j - 1], kneed[j], kf * ts[j])
            kabs[j] = min(want, kabs[j - 1] + cap * dt * D2R)
        dK = sp * kabs; th = th_of(ts, kabs); a1e = a1e_of(kabs)
        lift_mm = rh * kabs / ir; r_t = rl0 + lift_mm
        k_t = np.gradient(kabs, ts)
        pa = np.degrees(np.arctan(k_t * rh / (ir * r_t)))
        dth = np.gradient(th, ts); dk = np.gradient(kabs, ts)
        h = 1e-4
        a_t = (th_of(ts + h, kabs) - th_of(ts - h, kabs)) / (2 * h); b_k = (th_of(ts, kabs + h) - th_of(ts, kabs - h)) / (2 * h)
        sC = -a_t / np.where(np.abs(b_k) < 1e-12, 1e-12, b_k)
        lift = (sC > 1e-9) & (sC < dk - 1e-9)
        rate = 1.0 / np.maximum(np.radians(dth), 1e-12)
        skirt = r_t <= S.HUB_R + 1.5 + 1e-9
        good = (dth > 0) & (rate <= FL.RATE_MAX) & (pa <= float(P["pa_max"]) + 1e-9) & ~lift & (kabs <= dKB + 1e-9) & skirt
        good[0] = True
        nval = int(np.argmin(good)) if not good.all() else len(good)
        why_end = None
        if nval < len(good):
            j = nval
            why_end = ("rate" if not (dth[j] > 0 and rate[j] <= FL.RATE_MAX) else "pressure" if pa[j] > float(P["pa_max"]) + 1e-9 else
                       "liftoff" if lift[j] else "stopB" if kabs[j] > dKB + 1e-9 else "skirt" if not skirt[j] else "sign")
        m3_law = KR.dyad_margin(th, a1e, self.a2)
        self._law = dict(ok=nval > 1, side=0.0, Lt=0.0, p0=u2.copy(), ts=ts[:nval], q2t=q2t[:nval], dK=dK[:nval], th=th[:nval],
                         pa=pa[:nval], r_c=np.zeros(nval), rate=rate[:nval], emb="rod", q2hi=q2hi, s_q=s_q, why_end=why_end, s_m=1.0,
                         dK_max=float(np.degrees(kabs[:nval].max())) if nval else 0.0, t_max=float(np.degrees(ts[nval - 1])) if nval else 0.0,
                         th_max=float(th[nval - 1]) if nval else None, phi_t=None, dKB=float(np.degrees(dKB)),
                         lobe_r_max=float(r_t[:nval].max()) if nval else rl0, lift_max=float(lift_mm[:nval].max()) if nval else 0.0,
                         m3e_min=float(m3_law[:nval].min()) if nval else None, k_max=float(k_t[:nval].max()) if nval else 0.0,
                         pa_max_law=float(pa[:nval].max()) if nval else 0.0)
        return self._law


FL.G.KR.KB.KDesign = SLDesign

Base = IB.IBModel


class SLModel(Base):
    """the inband RSSR model; with SL_J3MIN set, conecut-knee's physical J3 stop q3' >= J3MIN (poses past it not taken)"""
    def __init__(self, B, params=None, verbose=False):
        super().__init__(B, params, verbose)
        if J3MIN is not None and hasattr(self, "K") and "phi" in self.K:
            q3p = np.degrees(self.q[:, 2] + self.K["phi"]); q3p = (q3p + 180) % 360 - 180
            bad = self.kin_ok & (q3p < J3MIN); self.why[bad] = "j3stop"; self.kin_ok = self.kin_ok & ~bad; self.q3p = q3p


# route every parent hook through this row's clamp and model (the inband row's own patch lines, one level up)
LS.LSModel = SLModel; LS._clamp = _clamp; LS.PARAMS = PARAMS
SC.SCModel = SLModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; LS.RF.PARAMS = PARAMS; LS.BM.PARAMS = PARAMS
FL.G.KR.KB.KModel = SLModel; FL.FLModel_SC = SLModel
IB._clamp = _clamp; IB.PARAMS = PARAMS
_report = LS._report; gate = LS.gate; frozen = LS.frozen; frozen_held = LS.frozen_held; frozen_flood = LS.frozen_flood
viz_export = LS.viz_export; evaluate = IB.evaluate; bench_eval = IB.bench_eval


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["row"] = ID; out["ghost"] = IB.GHOST; out["J3MIN"] = J3MIN; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(row=ID, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), cam=out.get("cam"),
                              depth={k: v for k, v in (out.get("contact_depth") or {}).items() if k != "per_pose"},
                              th_margin=out.get("th_margin"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    info = getattr(M, "_sc_info", None) or {}
    print(json.dumps(dict(row=ID, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), reach=r["reach"], inband14=r["inband14"],
                          contact=r["contact"], honest=r.get("honest"), why=r.get("why"), ovh=r.get("overhead140"), cam=r.get("cam"),
                          law={k: v for k, v in M.D.law().items() if isinstance(v, (int, float, str)) or v is None}, secs=round(time.time() - t)), default=float))
