"""conecut-knee-knuckle-3r (round 12, lens 2 'overhead cone' / the knee column every long-dyad pick wears): the verified lead
slipper-nose-knuckle-3r (SN_CELL=lead: drive, seats, K law, metal, near-touch rules loaded UNCHANGED) with two changes:

  (1) the two-pin knee RE-CENTRED on the arm-vs-member-3 drift cloud (kneewin proportions): lE 82, lc 27, phiE 3.8,
      phib -96.6 at the rule's ang_min 25.22 - over bench, held-out and every fit-clip frame the knee uses [44.5, 116.5]
      deg of its [25.22, 154.78] window (margins 19 / 38 deg) where the lead's runs to 152.2 (0.33 mm from straight);
  (2) a HARD STOP ON J3's OWN ANGLE q3' = q3 + phi (phi = member 3's knee rotation about the J3 axis, so q3' is the
      link 2 -> member 3 angle) at q3' >= J3MIN (default -105; optional q3' <= J3MAX). Built as an ISO 8734 2 m6 440C
      dowel pressed axially into hub 3's lower plate (member 3) at r 7.5 mm, running in a 2.1 x 1.0 mm arc groove under
      link 2's ring (member 2): inside the O20 x 12.25 stack (bearing OD 11 -> r 5.5 < 7.5 - 1.05; rim r 10), so it adds
      no skin-facing metal and no body (the spec's 3 x 2.5 x 2 tab on link 2's root is the alternative; the dowel is
      chosen because it needs no new metal outside the hub). Poses past the stop are not taken (why 'j3stop').

DOF: 3 ACTIVE (J1, J2, J3 encoded), K slaved and never read, knee pins a / b passive rotations (outside the count, user
2026-10-17), 0 passive translations. No gears / pulleys / cables. The stop adds no DOF (it bounds J3).

Extra reports (frozen / check): q3' range over the taken poses and clip frames, the stop's margin, the knee window
margin (deg and mm in d), the knee transmission arm d_perp = lE sin(knee angle) (J3 moment -> knee link force) and the
stop dowel force per N m of J3 moment.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/conecut-knee-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("SN_CELL", "lead")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("slipper_for_conecut", os.path.join(HERE, "slipper-nose-knuckle-3r.py"))
SN = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SN)
BM, RF, SC, FL, PK, S = SN.BM, SN.RF, SN.SC, SN.FL, SN.PK, SN.S
ID = "conecut-knee-knuckle-3r"
LEAD_ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "slipper-nose-knuckle-3r.json")))["best_params"]
KNEE = dict(lE=82.0, lc=27.0, phiE=3.8, phib=-96.6, ang_min=25.2189)
STOP = dict(J3MIN=-105.0, J3MAX=999.0)                       # J3MAX >= 180 = off
PARAMS = dict(SN.PARAMS); PARAMS.update(LEAD_ROW); PARAMS.update(KNEE); PARAMS.update(STOP)
DOWEL_R = 7.5                                                # stop dowel radius from the J3 axis (mm)


def wr(a): return (a + 180.0) % 360.0 - 180.0


def _clamp(p):
    j3min, j3max = p.get("J3MIN", -105.0), p.get("J3MAX", 999.0)
    p = SN._clamp(p)
    p["J3MIN"] = min(max(float(j3min), -180.0), -60.0); p["J3MAX"] = float(j3max)
    p["ang_min"] = max(float(p.get("ang_min", 25.2189)), 25.2189)    # the rule's lower bound (never below)
    p["lE"] = min(max(float(p["lE"]), 40.0), 110.0)               # E end boss stays above the cuff (cuff centre ~155 mm down the arm)
    p["lc"] = min(max(float(p["lc"]), 15.0), 45.0)
    return p


class CCModel(SN.SNModel):
    """the lead's model; J3 hard stop on q3' = q3 + knee phi (J3's own angle) applied before fit / run"""
    def __init__(self, B, params=None, verbose=False):
        super().__init__(B, params, verbose)
        P = self.p; lo = float(P.get("J3MIN", -105.0)); hi = float(P.get("J3MAX", 999.0))
        if hasattr(self, "K") and "phi" in self.K:
            q3p = wr(np.degrees(self.q[:, 2] + self.K["phi"]))
            bad = self.kin_ok & ((q3p < lo) | ((q3p > hi) if hi < 180 else False))
            self.why[bad] = "j3stop"; self.kin_ok = self.kin_ok & ~bad; self.q3p = q3p


SC.SCModel = CCModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
FL.G.KR.KB.KModel = CCModel; FL.FLModel_SC = CCModel; BM.PARAMS = PARAMS


def knee_report(M, B, taken=None):
    """per taken pose: knee angle, window margins (deg), d margin (mm), transmission arm d_perp = lE sin(ang), q3'"""
    P = M.p; lE, lc, amin = float(P["lE"]), float(P["lc"]), float(P["ang_min"])
    if taken is None:
        taken = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(B.idx))])
    ang = np.asarray(M.K["ang"], float); q3p = wr(np.degrees(M.q[:, 2] + M.K["phi"]))
    t = np.nonzero(taken)[0]
    if not len(t): return {}
    a = ang[t]
    def dofa(x): return math.sqrt(lE ** 2 + lc ** 2 - 2 * lE * lc * math.cos(math.radians(x)))
    dpp = lE * np.sin(np.radians(a))
    lo, hi = float(P.get("J3MIN", -105)), float(P.get("J3MAX", 999))
    return dict(n=int(len(t)), ang=[round(float(a.min()), 2), round(float(a.max()), 2)],
                margin_deg=[round(float(a.min() - amin), 2), round(float(180 - amin - a.max()), 2)],
                margin_mm=[round(dofa(float(a.min())) - dofa(amin), 2), round(dofa(180 - amin) - dofa(float(a.max())), 2)],
                d_perp_mm=[round(float(dpp.min()), 1), round(float(np.median(dpp)), 1)],
                knee_N_per_Nm_max=round(1000.0 / float(dpp.min()), 1),
                q3p=[round(float(q3p[t].min()), 2), round(float(q3p[t].max()), 2)],
                stop_margin_deg=round(float(q3p[t].min() - lo), 2),
                stop_hi_margin_deg=(round(float(hi - q3p[t].max()), 2) if hi < 180 else None),
                dowel_N_per_Nm=round(1000.0 / DOWEL_R, 1),
                j3stop=int((np.asarray(M.why) == "j3stop").sum()))


def clip_check(M):
    """every fit-clip frame (10 fps): q3' vs the stop and the knee window, on this model's design (no metal)"""
    Z = CB._poses_all(); names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
    q, okc, _, _, _, sc = M.D.ik(Z["HG"][ii].astype(float)); Kc = M.D.knee(sc)
    q3c = wr(np.degrees(q[:, 2] + Kc["phi"])); P = M.p; lo, hi = float(P["J3MIN"]), float(P["J3MAX"])
    o = okc & Kc["ok"]
    return dict(frames=int(len(ii)), closed=int(okc.sum()), knee_ok=int(o.sum()), q3p=[round(float(q3c[o].min()), 2), round(float(q3c[o].max()), 2)],
                cut_by_stop=int((o & ((q3c < lo) | ((q3c > hi) if hi < 180 else False))).sum()),
                ang=[round(float(np.asarray(Kc["ang"])[o].min()), 2), round(float(np.asarray(Kc["ang"])[o].max()), 2)])


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = SN._report(B, p)
    try: r["knee"] = knee_report(M, B)
    except Exception as e: r["knee"] = dict(err=str(e)[:120])
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def _frozen_model(P, nc, nw):
    """the claim protocol: fit on Bench(60,160) fast, freeze the shape (drive, metal), wear on Bench(nc, nw) (exact with
    CB_EXACT=1; nc == -1: the held-out bench)"""
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = CCModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(CCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if nc == -1:
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_conecut", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
        PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); B = PVm.held_bench()
    else:
        B = CB.Bench(n_clip=nc, n_ws=nw)
    M = Frozen(B, P2); r = M.run()
    return fit, M1, M, B, r


def frozen(P, nc=110, nw=360):
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    ov = ws & (elev >= 140)
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
               parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), split=BM.contact_split(M, B),
               overhead=dict(ws=int(ov.sum()), taken=int((ov & (mins >= 0)).sum()), why={k: int(((np.asarray(M.why) == k) & ov).sum()) for k in set(np.asarray(M.why)[ov])}),
               knee=knee_report(M, B, taken=np.isfinite(mins) & (mins >= 0)),
               contact_poses=[(int(j), [B.poses[j][k] for k in ("plane", "elev", "axial")], round(float(mins[j]), 2)) for j in range(len(B.idx)) if np.isfinite(mins[j]) and mins[j] < 0],
               stopped=[int(j) for j in range(len(B.idx)) if M.why[j] == "j3stop"],
               cam={k: (getattr(M1, "_sc_info", None) or {}).get(k) for k in ("dK_lim", "pa_crank_max_taken", "pa_horn_max_taken", "pa_kin_max", "pa_eff_horn")})
    try: out["clips"] = clip_check(M1)
    except Exception as e: out["clips"] = dict(err=str(e)[:120])
    if os.environ.get("CC_FULL_OUT"):                         # the full report next to tools/alignment_paired.py's per-pose dump
        json.dump(dict(out, params=P), open(os.environ["CC_FULL_OUT"], "w"), indent=1, default=float)
    return out


def frozen_held(P): return frozen(P, -1, -1)


def frozen_flood(P, nc=110, nw=360):
    os.environ["CB_EXACT"] = "1"
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    out = dict(frozen={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")})
    sp_ = importlib.util.spec_from_file_location("minarc_mech_for_conecut", os.path.join(REPO, "docs", "concepts", "verify", "minarc-stop-knuckle-4r-mechanism.py"))
    MECH = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(MECH)
    t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


def viz_export(par): return RF.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["row"] = ID; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(row=ID, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), knee=out.get("knee"),
                              clips=out.get("clips"), contacts=out.get("contact_poses"), stopped=out.get("stopped"),
                              connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(row=ID, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r.get("inband10"), contact=r["contact"], honest=r.get("honest"),
                          why=r.get("why"), ovh=r.get("overhead140"), knee=r.get("knee"), parts=r.get("parts_ib14"), secs=round(time.time() - t)), default=float))
