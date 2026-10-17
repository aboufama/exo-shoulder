"""longstroke-slipper-knuckle-3r (2026-10-17, the fold-ceiling lever): the verified slipper-nose-knuckle-3r (lead cell:
roller-longdyad-knuckle-3r chain, pin knee, b3 tilt) with the K SUB-DYAD RE-SEATED LONG (bk1 / bk2 ~28 / 50, stop B
a1max up to bk1 + bk2 - 5 ~73, as docs/research/fold_ceiling.md section 4b asks) and a K DRIVE whose stroke reaches
57.5-60+ deg with EVERY pressure angle <= 42 (friction included for sliding pairs). 3 ACTIVE DOF (J1, J2, J3 encoded), K
slaved and never read, 0 passive translations, no gears / pulleys / cables.

The drive is chosen by the environment variable LS_DRIVE at import (one drive per process: the parents patch their shared
core modules):
  * LS_DRIVE=nose (default): slipper-nose's sliding pair (hardened dowel nose on the conjugate flank, mu), synthesised by
    the parents' spherical cam code per 0.25 deg of K, both kinematic pressure angles <= 42 - atan(mu);
  * LS_DRIVE=roller: the lead's MR63ZZ roller (rolling, friction 0) on the same synthesis, the stub head sampled
    (roller-longdyad-knuckle-3r's _rod_metal), both pressure angles <= 42;
  * LS_DRIVE=rssr: the sidecar RSSR (sidecar-longdyad-knuckle-3r's per-pose rod: a bell crank on link 1b beside hub 2,
    an O3 Ti rod with M2 ball links to a horn lug of link 1a at hub K, closed per pose by continuation) with its
    transmission gate raised from 30 to 48 deg (PA <= 42 at BOTH ball ends; a two-force rod with ball ends has no
    sliding-friction lean), the crank phase gam free (pre-rotates the arm so the swing straddles 90 deg of transmission).
Everything else (lobe gate on hub 2, the law, drive-range truncation on every bench, per-pose metal, O20 stacks, part
pairs, kit fold rule, 2 mm near-touch objective, the frozen claim protocol) is the parents' code, loaded unchanged.

    LS_DRIVE=nose OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/longstroke-slipper-knuckle-3r.py [check] ['<json>']
    LS_DRIVE=... CB_EXACT=1 ... frozen|held|flood '<json>' [out.json]
    LS_DRIVE=... ... gate '<json>'                  (law + drive-range kinematic gate on Bench(110,360))
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

ID = "longstroke-slipper-knuckle-3r"
DRIVE = os.environ.get("LS_DRIVE", "nose")
CELL = "lead"
PA_GATE = 42.0                                               # the audit-compliant reading (brief 2026-10-17): every PA <= 42
TRANS_MIN_RSSR = 90.0 - PA_GATE
# slipper-nose's verified config (rows/slipper-nose-knuckle-3r.json best_params, CMA A) on the lead's seats
SN_BEST = {"bk1": 26.0, "bk2": 38.0336, "a1max": 58.7678, "kK": 2.1534, "smhi": 16.8433, "smlo": 5.0, "g": 2.3934, "beta": -176.684,
           "r_c": 15.3739, "lift": 0.7882, "hl": 1.9442, "zr": 4.0293, "s_arm": 4.0, "r_lobe": 8.2661, "nose_r": 1.1839, "mu": 0.087,
           "az1": 95.3929, "el1": 67.8974, "az2": 45.8211, "el2": 41.0855, "wd": 66.8662, "wa": -10.6559, "b3": 0.329, "lE": 67.832,
           "phiE": -2.7863, "lc": 21.1499, "phib": -58.8084, "ang_min": 25.2189, "cprog": 0.0, "chain": "free", "near2": 1, "law_mode": "lin"}
LONG_K = {"bk1": 28.0, "bk2": 50.0, "a1max": 73.0}            # fold_ceiling.md 4b: the 28 / 50 K dyad (a1max = bk1 + bk2 - 5)
RSSR_SEED = {"La": 20.0, "r_h": 15.0, "beta": -112.0, "gam": 0.0, "hl": 3.15, "zr": 1.5, "s_arm": 5.0, "r_lobe": 7.5}

_sp = importlib.util.spec_from_file_location("longdyad_for_longstroke", os.path.join(HERE, "roller-longdyad-knuckle-3r.py"))
BM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(BM)
RF, SC, FL, PK, S = BM.RF, BM.SC, BM.FL, BM.PK, BM.S
RL = BM
SCBase = RF.RFModel.__bases__[0]                             # the RSSR sidecar class (sidecar-longdyad-knuckle-3r.SCModel)
REPORT_KEYS = ("plain", "gap_near1", "gap_near2", "min_metal_mm", "why", "cam", "overhead140", "ws_inband", "parts_ib14")
NOSE = dict(mu=0.087, nose_r=1.1839)
if DRIVE == "rssr":
    PARAMS = dict(BM.PARAMS, **SN_BEST); PARAMS.update(RSSR_SEED); PARAMS.update(LONG_K)
    for k_ in ("g", "r_c", "lift", "nose_r", "mu"): PARAMS.pop(k_, None)
else:
    PARAMS = dict(BM.PARAMS, **SN_BEST); PARAMS.update(NOSE); PARAMS.update(LONG_K)
    if DRIVE == "roller": PARAMS.update(mu=0.0, nose_r=3.0)
PARAMS["pa_max"] = PA_GATE                                   # the hub-2 lobe stage too (parents: 45)


def pa_kin(mu): return PA_GATE - math.degrees(math.atan(float(mu)))


def _c(v, lo, hi): return min(max(float(v), lo), hi)


def _clamp_dyad(p):
    p["chain"] = "free"; p["law_mode"] = "lin"; p["cprog"] = 0.0
    p["bk1"] = _c(p["bk1"], 26.0, 34.0); p["bk2"] = _c(p["bk2"], 38.0, 56.0)
    return p


def _clamp(p):
    p = _clamp_dyad(p)
    if DRIVE == "rssr":
        # the sidecar's component limits (La 12-26, s_arm 4-6, r_h 13-22, lobe base 7-8.5, hl 0-3.15, zr >= 0), i_rock = La / s_arm
        p["La"] = _c(p["La"], 12.0, 26.0); p["s_arm"] = _c(p["s_arm"], 4.0, 6.0); p["r_h"] = _c(p["r_h"], 13.0, 22.0)
        p["r_lobe"] = _c(p["r_lobe"], 7.0, 8.5); p["hl"] = _c(p["hl"], 0.0, 3.15); p["zr"] = max(float(p["zr"]), 0.0)
        p["gam"] = _c(p.get("gam", 0.0), -60.0, 60.0)
        p["i_rock"] = p["La"] / p["s_arm"]; p["r_horn"] = p["r_h"]
        p["kK"] = max(float(p["kK"]), 0.0); p["kA"] = p["kB"] = p["kK"]; p["t1"] = 6.0; p["law_mode_in"] = "lin"; p["law_mode"] = "seg"
        p["smt"] = max(float(p.get("smt", 12.0)), 5.2)
        p["a1max"] = min(float(p["a1max"]), float(p["bk1"]) + float(p["bk2"]) - 5.0)
        return p
    p["g"] = _c(p["g"], 1.2, 3.0); p["r_c"] = _c(p["r_c"], 13.0, 22.0)
    p["lift"] = _c(p.get("lift", 0.0), 0.0, min(float(p.get("lift_max", 4.0)), 8.0))
    b = float(p["beta"]); b = b - 360.0 if b > 0 else b; p["beta"] = _c(b, -180.0, -120.0)
    p = RF._clamp(p)
    p["mu"] = _c(p.get("mu", 0.087), 0.0, 0.3); p["nose_r"] = _c(p.get("nose_r", 1.5), 1.0, 3.0)
    if DRIVE == "roller": p["mu"] = 0.0; p["nose_r"] = 3.0
    return p


class LSModel(BM.RLModel):
    """nose / roller: the parents' spherical cam synthesis at PA <= 42 - atan(mu); rssr: the sidecar's per-pose RSSR at
    transmission >= 48 (PA <= 42 at both ball ends)"""
    def _rod_metal(self):
        if DRIVE == "rssr":
            SC.TRANS_MIN = TRANS_MIN_RSSR
            SCBase._rod_metal(self); return
        P = self.D.p; mu = float(P.get("mu", 0.087)); nr = float(P.get("nose_r", 1.5))
        RF.ROLL_R = nr; RF.PA_MAX = pa_kin(mu)
        if DRIVE == "roller": BM.RLModel._rod_metal(self)        # roller + its stub head (rolling friction 0)
        else: RF.RFModel._rod_metal(self)                       # slipper nose: a pressed dowel, no head
        fr = math.degrees(math.atan(mu)); i = self._sc_info
        i.update(nose_r=nr, mu=mu, friction_deg=round(fr, 2), pa_kin_max=round(RF.PA_MAX, 2),
                 pa_eff_horn=round(i["pa_horn_max_taken"] + fr, 1), pa_eff_crank=round(i["pa_crank_max_taken"] + fr, 1))
        self._rod_info = i

    def _sc_pose(self):
        if DRIVE == "rssr": return SCBase._sc_pose(self)
        return RF.RFModel._sc_pose(self)


SC.SCModel = LSModel; SC._clamp = _clamp; SC.PARAMS = PARAMS; RF.PARAMS = PARAMS; BM.PARAMS = PARAMS
FL.G.KR.KB.KModel = LSModel; FL.FLModel_SC = LSModel


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    if DRIVE == "rssr":
        r, M = SC._report(B, p)
        r["plain"] = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "contact")} if "plain" not in r else r["plain"]
        r["ws_inband"] = RL.ws_inband(B)
        if M.kin_ok.any() and p.get("near2"):
            a = PK.audit(M, B); r["gap_near2"] = a.get("gap_near2"); r["gap_near1"] = a.get("gap_near1", r.get("gap_near1"))
            if r["gap_near2"] is not None: r["gap"] = r["gap_near2"]
        info = getattr(M, "_sc_info", None) or {}
        r["cam"] = {k: info.get(k) for k in ("dK_lim", "why_lim", "trans_min_taken", "ratio_range", "phi_max_taken", "crest_exact",
                                             "rod_len", "La", "r_h", "i_rock", "rssr_closed")}
        # no PA flag here: SC's range scan stops dK_lim at the first K step whose transmission < 48 (PA > 42 at either ball
        # end), and _truncate drops every pose past dK_lim on every bench, so every taken pose is inside the gate
        # (trans_min_taken is reported over the pre-truncation law range)
        return r, M
    r, M = BM._report(B, p)
    info = getattr(M, "_sc_info", None) or {}
    for k in ("nose_r", "mu", "friction_deg", "pa_kin_max", "pa_eff_horn", "pa_eff_crank", "contact_r", "lug_r_max"):
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
    r, M = _report(B, params); r.pop("params", None); r["drive_kind"] = DRIVE; return r


def gate(params, nc=110, nw=360):
    """law + drive-range kinematic gate: fit on Bench(60,160) fast, then the fitted design's own IK on every Bench(nc, nw)
    workspace pose; kinematic reach with the law alone and with the drive's own range |dK| <= dK_lim"""
    p = _clamp(dict(PARAMS, **params))
    B1 = CB.Bench(n_clip=60, n_ws=160); r1, M1 = _report(B1, p); D = M1.D
    B3 = CB.Bench(n_clip=nc, n_ws=nw); Z = CB._poses_all()
    k = np.array(B3.kind); ws = k == "ws"; Q = Z["HG"][B3.idx].astype(float)
    q, ok, X1, X2, X3, s = D.ik(Q); Kn = D.knee(s); dK = np.degrees(np.abs(np.asarray(D._dK, float)))
    kin = ok & Kn["ok"] & (np.abs(s[:, 2]) <= float(D.p["R_tol"]))
    lim = math.degrees(float(M1._scg["dK_lim"])); kinD = kin & (dK <= lim + 1e-6)
    th = np.degrees(np.arccos(np.clip((Q @ D.u[2]) @ D.u[0], -1, 1)))
    elev = np.array([B3.poses[i]["elev"] for i in range(len(B3.idx))]); ov = ws & (elev >= 140)
    L_ = D.law()
    return dict(kin_law=round(float(kin[ws].mean()), 4), kin=round(float(kinD[ws].mean()), 4), n_ws=int(ws.sum()),
                ov_law=f"{int(kin[ov].sum())}/{int(ov.sum())}", ov=f"{int(kinD[ov].sum())}/{int(ov.sum())}",
                th_max_taken=round(float(th[ws & kinD].max()), 1) if (ws & kinD).any() else None,
                dK_taken_max=round(float(dK[ws & kinD].max()), 1) if (ws & kinD).any() else None,
                lost_drive_wall=int((ws & kin & ~kinD).sum()), a1=round(D.a1, 2), a2=round(D.a2, 2),
                law=dict(why_end=L_.get("why_end"), dK_max=round(L_.get("dK_max", 0), 1), th_max=L_.get("th_max")),
                cam=r1.get("cam"), fast=dict(gap=r1["gap"], plain=r1.get("plain"), reach=r1["reach"], inband14=r1["inband14"],
                                             contact=r1["contact"], why=r1.get("why"), honest=r1.get("honest")))


def _frozen_model(P, nc, nw):
    """the claim protocol (= SC.frozen / slipper-nose): fit on Bench(60,160) fast, the shape frozen (drive and metal
    copied), worn on Bench(nc, nw) (exact when CB_EXACT=1; nc == -1: the held-out bench)"""
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = LSModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(LSModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if nc == -1:
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_longstroke", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
        PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); B = PVm.held_bench()
    else:
        B = CB.Bench(n_clip=nc, n_ws=nw)
    M = Frozen(B, P2); r = M.run()
    return fit, M1, M, B, r


def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(a, b)), -1, 1))))
def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def th_margin(M, B):
    """the lead verifier's own-state fold margin (docs/concepts/verify/roller-longdyad-knuckle-3r.py th_margin, copied
    verbatim): per taken pose the th distance from the dyad's fold, read on the effective arcs when K is forced"""
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; a1, a2 = math.degrees(D.a1) if D.a1 < 4 else D.a1, math.degrees(D.a2) if D.a2 < 4 else D.a2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]; rows = []
    dK = np.asarray(M.dK, float)
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(dK[i])) > 1e-6
        m_plain = _dm(th, a1, a2); m_eff = _dm(th, a1e, a2e); m_sub = _dm(th, b1, c)
        rows.append((min(m_sub, m_eff) if forced else m_plain, forced, m_plain, m_eff, m_sub, i, th))
    if not rows: return dict(min=None, n=0)
    own = [r[0] for r in rows]; lo = min(rows)
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)),
                forced=int(sum(r[1] for r in rows)), th_max_taken=round(max(r[6] for r in rows), 2),
                dK_taken_max=round(float(np.degrees(np.max(np.abs(dK[[r[5] for r in rows]])))), 2),
                lowest=dict(own=round(lo[0], 3), forced=bool(lo[1]), kind=B.kind[lo[5]], **{k: B.poses[lo[5]][k] for k in ("plane", "elev", "axial")}))


def frozen(P, nc=110, nw=360):
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    ov = ws & (elev >= 140)
    info = getattr(M1, "_sc_info", None) or {}
    # contact DEPTH (lead's rule 2026-10-17): per contact pose the deepest metal under the skin (mm), summed
    depth = [round(-float(mins[j]), 3) for j in range(len(B.idx)) if np.isfinite(mins[j]) and mins[j] < 0]
    try: thm = th_margin(M, B)
    except Exception as e: thm = dict(error=repr(e)[:300])
    out = dict(cell=CELL, drive=DRIVE, fit_fast=fit, frozen=rep, mode=B.mode, bench=[nc, nw], why=r.get("why"), parts_pairs=r.get("parts_pairs"), th_margin=thm,
               parts_ib14=r.get("parts_ib14"), audit=PK.audit(M, B), ws_inband=RL.ws_inband(B), split=RL.contact_split(M, B),
               overhead=dict(ws=int(ov.sum()), taken=int((ov & (mins >= 0)).sum())),
               contact_depth=dict(n=len(depth), sum_mm=round(float(np.sum(depth)), 3), max_mm=round(float(np.max(depth)), 3) if depth else 0.0, per_pose=depth),
               cam={k: info.get(k) for k in ("dK_lim", "why_lim", "pa_crank_max_taken", "pa_horn_max_taken", "pa_kin_max", "friction_deg",
                                             "pa_eff_horn", "pa_eff_crank", "flank_rho_min", "clear_hubK_min", "clear_roll_hubK_min",
                                             "clear_lowarm_lug_min", "arm_len", "contact_r", "lug_r_max", "nose_r", "mu",
                                             "trans_min_taken", "ratio_range", "rod_len", "La", "r_h", "crest_exact")})
    return out


def frozen_held(P): return frozen(P, -1, -1)


def frozen_flood(P, nc=110, nw=360):
    os.environ["CB_EXACT"] = "1"
    fit, M1, M, B, r = _frozen_model(P, nc, nw)
    out = dict(cell=CELL, drive=DRIVE, frozen={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")})
    sp_ = importlib.util.spec_from_file_location("minarc_mech_for_longstroke", os.path.join(REPO, "docs", "concepts", "verify", "minarc-stop-knuckle-4r-mechanism.py"))
    MECH = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(MECH)
    t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


def viz_export(par): return RF.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "claims":
        # one farm job, the claim columns in parallel: argv[2] = [{"tag", "drive", "mode" (frozen|held|flood|gate), "params"}]
        import subprocess
        od = sys.argv[3] if len(sys.argv) > 3 else "ls_out"; os.makedirs(od, exist_ok=True); procs = []
        for c in par:
            env = dict(os.environ, LS_DRIVE=c.get("drive", DRIVE), CB_EXACT="1" if c.get("mode", "frozen") != "gate" else "0",
                       OMP_NUM_THREADS="1", IGL_NUM_THREADS="1", CB_QUIET_EXACT="1")
            if c.get("mode") == "gate": env.pop("CB_EXACT", None)
            lg = open(os.path.join(od, c["tag"] + ".log"), "w")
            procs.append(subprocess.Popen([sys.executable, os.path.abspath(__file__), c.get("mode", "frozen"), json.dumps(c.get("params", {})),
                                           os.path.join(od, c["tag"] + ".json")], env=env, stdout=lg, stderr=subprocess.STDOUT))
        for pr in procs: pr.wait()
        print("claims done", [pr.returncode for pr in procs]); sys.exit()
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "gate":
        t = time.time(); out = gate(par); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(out, default=float)); sys.exit()
    if mode in ("frozen", "held", "flood"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held, "flood": frozen_flood}[mode](par); out["params"] = par
        out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(drive=DRIVE, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"), cam=out.get("cam"),
                              depth={k: v for k, v in (out.get("contact_depth") or {}).items() if k != "per_pose"}, th_margin=out.get("th_margin"),
                              connected=out.get("connected"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(drive=DRIVE, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"),
                          pa_fail=r.get("pa_fail"), why=r.get("why"), ovh=r.get("overhead140"), cam=r.get("cam"), drive_rep={k: v for k, v in (r.get("drive") or {}).items() if k != "sidecar"},
                          parts=r.get("parts_ib14"), secs=round(time.time() - t)), default=float))
