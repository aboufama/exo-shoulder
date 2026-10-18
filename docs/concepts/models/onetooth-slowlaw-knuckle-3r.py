"""onetooth-slowlaw-knuckle-3r (round 107, pick 1): the verified lead conecut-knee-knuckle-3r (loaded UNCHANGED: seats, dyad
26 / 38.03, knee, J3 dowel stop, O20 stacks, part pairs, near-touch rules) with its two-stage K drive (bell crank on link 1b,
hub-2 rim lobe, slipper nose on link 1a's flank lug) replaced by ONE higher pair: a crowned 440C pin on a horn of link 1a
pushed by one link-2 tooth flank, at a SLOWER law rho = dK / d(-q2) (lead 2.1534), held by the lead's clock spring + stop A.

THE LAW (a LAW change, not a metric change): the lead's per-t gated 'lin' law with kK := rho and the onset moved so the
stretched end state is the lead's: on K's stop-A curve cos th = A + R cos(x) (x = |q2 - q0|, D._q2c), the lead's onset
x_L = acos((cos th_hi_L - A) / R), the anchor K_ANCH = 45.62 deg is reached at x_end = x_L + K_ANCH / 2.1534, and the slow
onset is x_N = x_end - K_ANCH / rho -> th_hi_N = acos(A + R cos x_N) -> smhi = (a1 + a2) - th_hi_N (36.2 at rho 0.8; lead
16.84). No smhi clamp exists above FOLD_MARGIN in this stack (kit rule: smhi >= 5). The drive's own range (q2 dowel stop B)
stays the lead's dK_lim (DKLIM, 50.0 deg on the lead's fit) so the stretched wall is the lead's.

CELLS (env OT_CELL, one per process; the parents patch shared modules):
  * ghost (STEP 0, default): every drive part is DELETED - crank (member 9) metal and contact sets, roller / nose, the flank
    lug on link 1a ('horn', member 1), the ROD / CRK / HORN strap sets and their part pairs, the crank-side gates (cam PA,
    RSSR crest) - leaving the ideal slaved law. A ghost number is a BOUND for this morphology (its drive metal only removes
    takes and in-band), never a claim. rho = 2.1534 is the lead's own law with its drive deleted (the paired control).
  * spring / D: the pin + tooth metal and the per-K PA synthesis (written only if the ghost passes step 0's gate).

DOF: 3 ACTIVE (J1, J2, J3 encoded), K slaved (passive R, determined by the law), knee pins outside the count, 0 passive
translations. No gears / pulleys / cables (MVP1).

    OT_CELL=ghost OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/onetooth-slowlaw-knuckle-3r.py [check] ['<json>']
    ... wear <envsel|bench|held> '<json>' [out.json]    fit Bench(60,160) fast -> shape frozen -> worn (exact) on that bench
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("SN_CELL", "lead")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_sp = importlib.util.spec_from_file_location("conecut_for_onetooth", os.path.join(HERE, "conecut-knee-knuckle-3r.py"))
CC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CC)
SN, BM, RF, SC, FL, PK, S = CC.SN, CC.BM, CC.RF, CC.SC, CC.FL, CC.PK, CC.S
ID = "onetooth-slowlaw-knuckle-3r"
CELL = os.environ.get("OT_CELL", "ghost")
LEAD_K = 2.1534                                              # the lead's law dK / d(-q2)
K_ANCH = 45.62                                               # deg: the lead's end state the slow law is anchored to (spec)
LEAD_ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "conecut-knee-knuckle-3r.json")))["best_params"]
PARAMS = dict(CC.PARAMS); PARAMS.update(LEAD_ROW); PARAMS.update(rho=0.8, DKLIM=50.0)
_SMHI = {}


def smhi_for(P):
    """the slow onset (deg of th margin from the stretched fold) that keeps the lead's end state at K_ANCH"""
    rho = float(P["rho"])
    key = (round(rho, 6),) + tuple(round(float(P[k]), 6) for k in ("az1", "el1", "az2", "el2", "wd", "wa", "b3", "bk1", "bk2"))
    if key in _SMHI: return _SMHI[key]
    q = dict(P); q["kK"] = LEAD_K; q["smhi"] = SN.LEAD_BEST["smhi"]          # the lead's law and onset
    D = FL.G.KR.KB.KDesign(CC._clamp(dict(CC.PARAMS, **{k: v for k, v in q.items() if k not in ("rho", "DKLIM")})))
    A, R, q0 = D._q2c; s12 = min(D.a1 + D.a2, 360 - D.a1 - D.a2)
    xL = math.acos(max(-1, min(1, (math.cos(math.radians(D.th_hi)) - A) / R)))
    xN = xL + math.radians(K_ANCH / LEAD_K) - math.radians(K_ANCH / rho)
    th_on = math.degrees(math.acos(max(-1, min(1, A + R * math.cos(xN)))))
    out = dict(smhi=s12 - th_on, th_on=th_on, th_hi_lead=D.th_hi, a1=D.a1, a2=D.a2, xN=math.degrees(xN), xL=math.degrees(xL))
    _SMHI[key] = out; return out


def _clamp(p):
    rho = min(max(float(p.get("rho", 0.8)), 0.3), 4.0); dkl = min(max(float(p.get("DKLIM", 50.0)), 30.0), 62.0)
    p = CC._clamp(p); p["rho"] = rho; p["DKLIM"] = dkl
    p["kK"] = rho; p["kA"] = p["kB"] = rho                     # the law: |dK| = rho t (t = q2 travel past the slow onset)
    p["smhi"] = round(smhi_for(p)["smhi"], 6)
    p["t_end"] = max(float(p.get("t_end", 75.0)), dkl / rho + 2.0)
    return p


_CCModel = CC.CCModel


class OTModel(_CCModel):
    def _rod_metal(self):
        super()._rod_metal()
        if CELL == "ghost": self._ghost()

    def _ghost(self):
        """delete every drive part (metal, contact sets, strap sets, gates); keep the law and its drive range DKLIM"""
        lug = self.rigid.get("horn", (1, np.zeros((0, 3))))[1]
        lugC = lug + S.T_LINK * S.unit(lug) if len(lug) else lug
        for k in ("crank", "roller", "horn", "rod", "rodends", "rocker", "plate", "nose"): self.rigid.pop(k, None)
        keep = []
        for m, X in self.contact:
            if m in (8, 9): continue
            if m == 1 and len(lugC) and X.shape == lugC.shape and np.allclose(X, lugC): continue
            keep.append((m, X))
        self.contact = keep
        for k in ("ROD", "CRK", "HORN"): self.strap.pop(k, None)
        g = self._scg; g["lowarm"] = []; g["dK_lim"] = math.radians(float(self.D.p["DKLIM"]))
        i = self._sc_info
        i.update(dK_lim=float(self.D.p["DKLIM"]), why_lim="ghost:DKLIM", pa_crank_max_taken=0.0, pa_horn_max_taken=0.0, rssr_closed=True,
                 crest_exact=0.0, pa_eff_horn=0.0, pa_eff_crank=0.0, ghost=True)
        self._rod_info = i; self._crown_ok = True


CC.CCModel = OTModel; SC.SCModel = OTModel; FL.G.KR.KB.KModel = OTModel; FL.FLModel_SC = OTModel
SC._clamp = _clamp; CC._clamp_cc = CC._clamp


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = CC._report(B, p)
    L_ = M.D.law(); s = smhi_for(p)
    r["law"] = dict(rho=p["rho"], smhi=round(p["smhi"], 3), th_on=round(s["th_on"], 2), th_hi_lead=round(s["th_hi_lead"], 2),
                    why_end=L_.get("why_end"), dK_max=round(float(L_.get("dK_max", 0.0)), 2), th_max=L_.get("th_max"), DKLIM=p["DKLIM"],
                    dK_taken_max=round(float(np.degrees(np.abs(np.asarray(M.dK, float))[M.kin_ok]).max()), 2) if M.kin_ok.any() else None)
    r["cell"] = CELL
    return r, M


def evaluate(B, params):
    r, M = _report(B, params)
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def _bench(name):
    if name == "fit":
        os.environ.pop("CB_EXACT", None); return CB.Bench(n_clip=60, n_ws=160)
    if name in ("env", "envsel"):
        import env_bench as EB
        EB.install(); return EB.bench(name, exact=True)
    if name == "held":
        sp_ = importlib.util.spec_from_file_location("pk_polish_v_onetooth", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py"))
        PVm = importlib.util.module_from_spec(sp_); sp_.loader.exec_module(PVm); return PVm.held_bench()
    os.environ["CB_EXACT"] = "1"; os.environ["CB_QUIET_EXACT"] = "1"; return CB.Bench(n_clip=110, n_ws=360)


def wear(P, bench="envsel"):
    """the claim protocol on any bench: fit Bench(60,160) fast, freeze the shape (metal, law, drive range), wear on `bench`"""
    P = _clamp(dict(PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = OTModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    a1 = PK.audit(M1, B1); fit["near1"] = a1.get("gap_near1"); fit["near2"] = a1.get("gap_near2")
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    ATTR = ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
            "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info", "_wedge_info")

    class Frozen(OTModel):
        def fit(self):
            for a in ATTR:
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    B = _bench(bench); M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    kind = np.array(B.kind); ws = kind == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    taken = np.isfinite(mins) & (mins >= 0); ov = ws & (elev >= 140)
    a = PK.audit(M, B)
    dK = np.degrees(np.abs(np.asarray(M.dK, float)))
    out = dict(cell=CELL, bench=bench, mode=B.mode, fit_fast=fit, frozen=rep, why=r.get("why"), near1=a.get("gap_near1"), near2=a.get("gap_near2"),
               min_metal=a.get("near_touch_min_mm"), parts_ib14=r.get("parts_ib14"), parts_pairs=r.get("parts_pairs"),
               ws_taken=int((ws & taken).sum()), n_ws=int(ws.sum()), ws_contact=int((ws & np.isfinite(mins) & (mins < 0)).sum()),
               overhead=dict(ws=int(ov.sum()), taken=int((ov & taken).sum())),
               K_open=dict(taken_open=int((taken & (dK > 0.5)).sum()), taken=int(taken.sum()), dK_max=round(float(dK[taken].max()), 2) if taken.any() else None),
               law=dict(rho=P["rho"], smhi=P["smhi"], th_on=round(smhi_for(P)["th_on"], 2), DKLIM=P["DKLIM"]),
               contact_poses=[(int(j), [B.poses[j][k] for k in ("plane", "elev", "axial")], round(float(mins[j]), 2)) for j in range(len(B.idx)) if np.isfinite(mins[j]) and mins[j] < 0],
               split=BM.contact_split(M, B))
    try: out["knee"] = CC.knee_report(M, B, taken=taken)
    except Exception as e: out["knee"] = dict(err=str(e)[:120])
    if os.environ.get("OT_FULL_OUT"): json.dump(dict(out, params=P), open(os.environ["OT_FULL_OUT"], "w"), indent=1, default=float)
    return out, M, B


def viz_export(par): return CC.viz_export(_clamp(dict(PARAMS, **par)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "wear":
        bench = sys.argv[2]; par = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        t = time.time(); out, M, B = wear(par, bench); out["params"] = par; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 4: json.dump(out, open(sys.argv[4], "w"), indent=1, default=float)
        print(json.dumps({k: out[k] for k in ("cell", "bench", "fit_fast", "frozen", "why", "near1", "near2", "min_metal", "ws_taken", "n_ws", "ws_contact", "overhead", "K_open", "law", "secs")}, default=float))
        sys.exit()
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(cell=CELL, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), reach=r["reach"], follow=r["follow"],
                          inband14=r["inband14"], contact=r["contact"], honest=r.get("honest"), why=r.get("why"), ovh=r.get("overhead140"),
                          law=r.get("law"), cam=r.get("cam"), parts=r.get("parts_ib14"), secs=round(time.time() - t, 1)), default=float))
