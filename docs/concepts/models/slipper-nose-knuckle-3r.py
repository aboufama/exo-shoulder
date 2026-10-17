"""slipper-nose-knuckle-3r (round 10, lens 3): the roller-flank drive's MR63ZZ roller DELETED - the crank's bent long arm ends
in a pressed, hardened, polished O3 440C nose (ISO 8734 3 m6 dowel) that SLIDES on the conjugate flank milled into link
1a's boss. Two cells, chosen by the environment variable SN_CELL at import (one cell per process: the two parents patch
their shared core modules):
  * SN_CELL=lead (default): the lead roller-longdyad-knuckle-3r (pin knee, b3 tilt) loaded unchanged;
  * SN_CELL=kneeless: the measured control kneeless-roller-knuckle-3r (J3 on a GH ray, one rigid bracket) loaded unchanged.
3 ACTIVE DOF (J1, J2, J3 encoded), K slaved and never read, 0 passive translations, no gears / pulleys / cables / rods.

WHAT CHANGES vs the parent (everything else - the spherical cam synthesis per 0.25 deg of K, lift-off, cusp, contact on
the lug, arm / tip / lug clearances, drive-range truncation on every bench, per-pose metal, O20 stacks, part pairs, kit
fold rule, 2 mm near-touch objective - is the parent's code, loaded unchanged):
  * nose radius nose_r (default 1.5): the flank is the nose-centre path offset by nose_r instead of 3 (RF.ROLL_R), the
    tip metal (end disc + rings, member 9) is the nose's O3 at the roller's old layer (+-1.25 mm about the lug mid layer);
    the roller's O3 stub and its O4.5 x 0.8 retaining head are gone (a pressed dowel has no head on the skin side);
  * FRICTION enters the pressure-angle budget: the contact force leans atan(mu) off the normal, so both kinematic
    pressure angles must stay <= PA_GATE - atan(mu) (PA_GATE 43 = the lead's budget, 2 deg under the 45 gate):
    mu 0.05 -> 40.14, mu 0.087 -> 38.03, mu 0.026 -> 41.51. The roller's own rolling friction was taken as 0.
  * optional hub-3 planar WEDGE skin face (wedge_tau > 0): hub 3's skin-side face is the plane tilted wedge_tau deg about
    the azimuth wedge_psi in hub 3's plane, under the unchanged bearing seat, crown and O20 planform; its offset is set
    by bisection on the FIT bench so the lowest wedge metal keeps >= wedge_clear (2.0) mm over every closing fit pose;
    the frozen protocol copies the fitted face (no re-fit on the worn bench). The crown does not move: the report gives
    the wedge's mean / max extra depth, its mass and hub 3's crown height above the skin next to the in-band number.

    SN_CELL=lead OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/slipper-nose-knuckle-3r.py [check] ['<json>']
    SN_CELL=... CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "slipper-nose-knuckle-3r"
CELL = os.environ.get("SN_CELL", "lead")
PA_GATE = 43.0
# the parents' verified best_params (rows/roller-longdyad-knuckle-3r.json, rows/kneeless-roller-knuckle-3r.json, 2026-10-17)
LEAD_BEST = {"bk1": 26.0, "bk2": 38.0336, "a1max": 58.7678, "kK": 2.1534, "smhi": 16.8433, "smlo": 5.0, "g": 2.4696, "beta": -173.4638, "r_c": 15.2211, "lift": 1.027, "hl": 2.1535, "zr": 4.0242, "s_arm": 4.0484, "r_lobe": 8.2409, "az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lc": 21.1499, "phib": -58.8084, "ang_min": 25.2189, "cprog": 0.0, "chain": "free", "near2": 1, "law_mode": "lin"}
KNEELESS_BEST = {"az1": 94.353, "el1": 65.9804, "az2": 41.8875, "el2": 41.0083, "wd": 73.9288, "wa": -11.3645, "lE": 82.2602, "phiE": -2.4165, "lc": 29.9075, "phib": -89.2952, "a1max": 56.0143, "kK": 2.568, "smhi": 16.9881, "bk1": 27.4142, "bk2": 35.6795, "g": 2.2297, "beta": -171.0352, "r_c": 16.2968, "lift": 1.7772, "hl": 0.7328, "zr": 2.9178, "s_arm": 4.7677, "r_lobe": 8.4303, "stk": 4.8534, "b3": 0.0, "ang_min": 0.0, "chain": "free", "law_mode": "lin", "near2": 1, "cprog": 0.0}
if CELL == "kneeless":
    _sp = importlib.util.spec_from_file_location("kneeless_for_slipper", os.path.join(HERE, "kneeless-roller-knuckle-3r.py"))
    BM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(BM); BaseModel = BM.KLModel; RL = BM.RL
    BEST = KNEELESS_BEST
else:
    _sp = importlib.util.spec_from_file_location("longdyad_for_slipper", os.path.join(HERE, "roller-longdyad-knuckle-3r.py"))
    BM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(BM); BaseModel = BM.RLModel; RL = BM
    BEST = LEAD_BEST
RF, SC, FL, PK, S = BM.RF, BM.SC, BM.FL, BM.PK, BM.S
REPORT_KEYS = ("plain", "gap_near1", "gap_near2", "min_metal_mm", "why", "cam", "overhead140", "ws_inband", "parts_ib14", "knee_rigid")
NOSE = dict(mu=0.05, nose_r=1.5, wedge_tau=0.0, wedge_psi=120.0, wedge_clear=2.0)
PARAMS = dict(BM.PARAMS, **BEST, **NOSE)


def pa_kin(mu): return PA_GATE - math.degrees(math.atan(float(mu)))


def _clamp(p):
    p = BM._clamp(p)
    p["mu"] = min(max(float(p.get("mu", 0.05)), 0.0), 0.3); p["nose_r"] = min(max(float(p.get("nose_r", 1.5)), 1.0), 3.0)
    p["wedge_tau"] = min(max(float(p.get("wedge_tau", 0.0)), 0.0), 40.0); p["wedge_psi"] = float(p.get("wedge_psi", 120.0)) % 360.0
    return p


class SNModel(BaseModel):
    def _rod_metal(self):
        P = self.D.p; mu = float(P.get("mu", 0.05)); nr = float(P.get("nose_r", 1.5))
        RF.ROLL_R = nr; RF.PA_MAX = pa_kin(mu)
        RF.RFModel._rod_metal(self)                                   # the parent's synthesis; no roller stub head (dowel)
        fr = math.degrees(math.atan(mu)); i = self._sc_info
        i.update(nose_r=nr, mu=mu, friction_deg=round(fr, 2), pa_kin_max=round(RF.PA_MAX, 2),
                 pa_eff_horn=round(i["pa_horn_max_taken"] + fr, 1), pa_eff_crank=round(i["pa_crank_max_taken"] + fr, 1))
        self._rod_info = i

    def fit(self):
        super().fit()
        tau = float(self.D.p.get("wedge_tau", 0.0))
        if tau > 0: self._wedge(tau, float(self.D.p.get("wedge_psi", 120.0)), float(self.D.p.get("wedge_clear", 2.0)))

    def _wedge(self, tau, psi, clear):
        m3, X = self.rigid["hub3"]; mc, cen, ax = self.cyl["hub3"]; u = ax / np.linalg.norm(ax)
        e1 = np.cross(u, [0, 0, 1.0]); e1 /= np.linalg.norm(e1); e2 = np.cross(u, e1); rel = X - cen
        xy = np.stack([rel @ e1, rel @ e2], 1)
        g = math.tan(math.radians(tau)) * np.array([math.cos(math.radians(psi)), math.sin(math.radians(psi))]); slope = xy @ g
        idx = np.nonzero(np.asarray(self.kin_ok, bool))[0]

        def dmin(c):
            s = np.maximum(0.0, -(c + slope)); Y = X - s[:, None] * u
            return min(float(self.B.dist(i, self.world(m3, i, Y)).min()) for i in idx)
        lo, hi = -40.0, 40.0
        for _ in range(20):
            c = (lo + hi) / 2
            if dmin(c) >= clear: hi = c
            else: lo = c
        s = np.maximum(0.0, -(hi + slope)); self.rigid["hub3"] = (m3, X - s[:, None] * u)
        self._wedge_info = dict(tau=tau, psi=psi, clear=clear, mean_drop=round(float(s.mean()), 2), max_drop=round(float(s.max()), 2),
                                mass_g=round(float(s.mean()) * math.pi * S.HUB_R ** 2 * 4.43e-3, 2))
        self._sc_info["wedge"] = self._wedge_info


SC.SCModel = SNModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS
FL.G.KR.KB.KModel = SNModel; FL.FLModel_SC = SNModel
if CELL == "kneeless": BM.PARAMS = PARAMS; BM.RL.PARAMS = PARAMS
else: BM.PARAMS = PARAMS


def crown_report(M, B):
    """hub 3's crown height above the skin (crown disc = cen + CROWN ax) and its underside's (rigid samples), median /
    min over the taken poses: the wedge fills under the crown, the crown does not move"""
    out = {}
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    if not taken or "hub3" not in getattr(M, "cyl_surf", {}): return out
    mem, Xc = M.cyl_surf["hub3"]; mc, cen, ax = M.cyl["hub3"]; u = ax / np.linalg.norm(ax)
    crown = Xc[np.abs((Xc - cen) @ u - S.CROWN) < 0.5] if len(Xc) else Xc
    m3, X3 = M.rigid["hub3"]
    dc = [float(B.dist(i, M.world(mem, i, crown)).min()) for i in taken] if len(crown) else []
    du = [float(B.dist(i, M.world(m3, i, X3)).min()) for i in taken]
    if dc: out["crown_mm"] = dict(median=round(float(np.median(dc)), 1), min=round(float(np.min(dc)), 1), max=round(float(np.max(dc)), 1))
    out["underside_min_mm"] = dict(median=round(float(np.median(du)), 1), min=round(float(np.min(du)), 1))
    return out


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = BM._report(B, p)
    info = getattr(M, "_sc_info", None) or {}
    for k in ("nose_r", "mu", "friction_deg", "pa_kin_max", "pa_eff_horn", "pa_eff_crank", "wedge"):
        if k in info: r.setdefault("cam", {})[k] = info[k]
    if info and (info.get("pa_crank_max_taken", 0) > RF.PA_MAX + 1e-6 or info.get("pa_horn_max_taken", 0) > RF.PA_MAX + 1e-6):
        r["honest"] = False; r["pa_fail"] = True
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); r["cell"] = CELL; return r


def _frozen_model(P, nc, nw, flood=False):
    """the claim protocol (= SC.frozen): fit on Bench(60,160) fast, the shape frozen (drive, metal, wedge face copied),
    worn on Bench(nc, nw) (exact when CB_EXACT=1; nc == -1: the held-out bench); returns the worn model too"""
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = SNModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(SNModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if nc == -1:
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_slipper", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
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
    info = getattr(M1, "_sc_info", None) or {}
    out = dict(cell=CELL, fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"),
               parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), ws_inband=RL.ws_inband(B), split=RL.contact_split(M, B),
               overhead=dict(ws=int(ov.sum()), taken=int((ov & (mins >= 0)).sum())), crown=crown_report(M, B),
               cam={k: info.get(k) for k in ("dK_lim", "why_lim", "pa_crank_max_taken", "pa_horn_max_taken", "pa_kin_max", "friction_deg",
                                             "pa_eff_horn", "pa_eff_crank", "flank_rho_min", "clear_hubK_min", "clear_roll_hubK_min",
                                             "clear_lowarm_lug_min", "arm_len", "contact_r", "nose_r", "mu", "wedge")})
    if CELL == "kneeless":
        kc = BM.knee_check(M); out["knee_rigid"] = kc
    return out


def frozen_held(P): return frozen(P, -1, -1)


def frozen_flood(P, nc=110, nw=360):
    os.environ["CB_EXACT"] = "1"
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    out = dict(cell=CELL, frozen={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")})
    sp_ = importlib.util.spec_from_file_location("minarc_mech_for_slipper", os.path.join(REPO, "docs", "concepts", "verify", "minarc-stop-knuckle-4r-mechanism.py"))
    MECH = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(MECH)
    t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


def viz_export(par): return RF.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "claims":
        # one farm job, the claim columns in parallel: argv[2] = [{"tag", "cell", "mode" (frozen|held|flood), "params"}],
        # argv[3] = out dir; each run = this file in its own process (SN_CELL per run, CB_EXACT=1 for the worn bench)
        import subprocess
        od = sys.argv[3] if len(sys.argv) > 3 else "sn_out"; os.makedirs(od, exist_ok=True); procs = []
        for c in par:
            env = dict(os.environ, SN_CELL=c.get("cell", "lead"), CB_EXACT="1", OMP_NUM_THREADS="1", CB_QUIET_EXACT="1")
            lg = open(os.path.join(od, c["tag"] + ".log"), "w")
            procs.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), c.get("mode", "frozen"), json.dumps(c.get("params", {})),
                                           os.path.join(od, c["tag"] + ".json")], env=env, stdout=lg, stderr=subprocess.STDOUT))
        for pr in procs: pr.wait()
        print("claims done", [pr.returncode for pr in procs]); sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(cell=CELL, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), cam=out.get("cam"),
                              crown=out.get("crown"), hub3=(out.get("parts_ib14") or {}).get("hub3"), connected=out.get("connected"),
                              secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(cell=CELL, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"),
                          pa_fail=r.get("pa_fail"), why=r.get("why"), ovh=r.get("overhead140"), ws_inband=r.get("ws_inband"), cam=r.get("cam"),
                          parts=r.get("parts_ib14"), crown=crown_report(M, B), secs=round(time.time() - t)), default=float))
