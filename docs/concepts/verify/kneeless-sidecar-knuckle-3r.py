"""Independent verifier (skeptic) of kneeless-sidecar-knuckle-3r (the verified lead sidecar-longdyad-knuckle-3r with J3
put on a GH ray, b3 0, and the two-pin knee replaced by ONE rigid bent 3 mm Ti bracket from hub 3's lower plate to the
arm pad).

The claim's model (docs/concepts/models/kneeless-sidecar-knuckle-3r.py) is loaded UNCHANGED (it patches its own copy of
the lead's module: the rigid-bracket drift refusal, the bracket plate at the pad level, E vs link 2 kept adjacent at
0.15 mm, the bracket plate vs hub 3 kept at 1 mm). The protocol is the claim's frozen one (fit on Bench(60,160) fast,
shape frozen, worn on Bench(110,360) exact). Checks ADDED here on every TAKEN pose of the worn bench:

  1. the lead verifier's drive checks (docs/concepts/verify/sidecar-longdyad-knuckle-3r.py extra_checks, unchanged):
     RSSR closure in the world, M2 ball-link tilt <= 30 deg, real lobe pressure angle <= 45 deg;
  2. RIGID BRACKET, measured from the transforms (not from the model's own knee report): member 3 (hub 3 + E + boss),
     member 6 (bracket plate) and member 5 (arm pad) must keep one relative pose over every taken pose - probe points
     (pin a, pad centre, plate centre) expressed in the pad frame; ptp > 0.5 mm fails the pose ('bracket');
  3. every taken pose re-collided: min non-adjacent clearance >= 1 mm, E vs link 2 >= 0.15 mm (adjacent at J3), the
     bracket plate vs hub 3 housing >= 1 mm (min over taken poses reported per pair; a pose failing is lost);
  4. the J1-J3 fold margin in the th metric over the taken poses (tools/sidecar_env_polish.py th_margin, copied);
  5. the continuity flood fill (connected_report, docs/concepts/verify/minarc-stop-knuckle-4r-mechanism.py).

    CB_EXACT=1 python3 docs/concepts/verify/kneeless-sidecar-knuckle-3r.py wear <bench|held|fitexact> <out.json> [--flood]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


KL = _load("kneeless_sidecar_claim_v", os.path.join(REPO, "docs", "concepts", "models", "kneeless-sidecar-knuckle-3r.py"))
LV = _load("sidecar_lead_verifier_for_kl", os.path.join(HERE, "sidecar-longdyad-knuckle-3r.py"))
SC, S, PK = KL.SC, KL.S, KL.PK
BEST = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "kneeless-sidecar-knuckle-3r.json")))["best_params"]


def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(a, b)), -1, 1))))


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def th_margin(M, B):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK; a1, a2 = math.degrees(D.a1) if D.a1 < 4 else D.a1, math.degrees(D.a2) if D.a2 < 4 else D.a2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]; rows = []
    dK = np.asarray(M.dK, float)
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(dK[i])) > 1e-6
        rows.append((min(_dm(th, b1, c), _dm(th, a1e, a2e)) if forced else _dm(th, a1, a2), forced))
    if not rows: return dict(min=None, n=0)
    own = [r[0] for r in rows]
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)), forced=int(sum(r[1] for r in rows)))


def bracket_and_clear(M, B):
    """checks 2 + 3 on the taken poses; returns the per-pair minima and the poses that fail"""
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    fr = M.fr; P = M.D.p; sn = M.D.sn; tr = float(M.tr); lc = float(P["lc"])
    probes = {3: np.array([fr["A0"] + tr * sn, fr["A0"] + (tr + 3.0) * sn]), 6: np.array([fr["A0m"] + (lc / 2) * fr["eK"] + tr * sn]),
              5: np.array([fr["Bm"] + tr * sn])}
    rel = {m: [] for m in (3, 6)}; mins = {}; bad = set()
    for i in taken:
        R5, t5 = M.T(5, i)
        for m in (3, 6):
            Rm, tm = M.T(m, i); w = probes[m] @ Rm.T + tm; rel[m].append((w - t5) @ R5)          # in the pad (arm) frame
        cmin = M.collide(i); lc_ = dict(getattr(M, "last_clear", {}) or {})
        for k, v in lc_.items():
            try: v = float(v)
            except (TypeError, ValueError): continue
            mins[k] = min(mins.get(k, 1e9), v)
        mins["_overall"] = min(mins.get("_overall", 1e9), float(cmin))
        if float(cmin) < 1.0 - 1e-9: bad.add(i)
    ptp = {}
    for m in (3, 6):
        a = np.array(rel[m]) if rel[m] else np.zeros((0, 1, 3))
        if len(a):
            d = np.linalg.norm(a - a[0][None], axis=2).max(1); ptp[m] = round(float(d.max()), 4)
            for j, dd in zip(taken, d):
                if dd > 0.5: bad.add(j)
    worst = sorted(((round(v, 2), k) for k, v in mins.items()))[:8]
    return dict(bracket_drift_mm={"member3_in_pad_frame": ptp.get(3), "plate6_in_pad_frame": ptp.get(6)},
                clear_min_taken=dict(worst=worst, E_L2=round(mins.get("E-L2", 1e9), 2), knee_hub3=round(mins.get("knee-hub3", 1e9), 2),
                                     overall=round(mins.get("_overall", 1e9), 2)), poses_failing=sorted(bad))


def frozen_wear(P, wear="bench", flood=False):
    P = SC._clamp(dict(SC.PARAMS, **P))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = SC.SCModel(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    fit["why"] = r1.get("why"); fit["audit"] = {k: v for k, v in PK.audit(M1, B1).items() if k in ("gap_near1", "gap_near2", "near_touch_min_mm")}
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    assert type(M1).__name__ == "KLModel", type(M1)

    class Frozen(SC.SCModel):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_rod_info", "_viz_rod", "_crown_ok", "_scg", "_sc_info"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self._sc = None
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
            self._truncate()
    if wear == "held":
        PV = _load("pk_polish_v_kl_v", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
    elif wear == "fitfast":
        B = B1
    elif wear == "fitexact":
        os.environ["CB_EXACT"] = "1"; B = CB.Bench(n_clip=60, n_ws=160)
    else:
        B = CB.Bench(n_clip=110, n_ws=360)
    M = Frozen(B, P2); r = M.run()
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    aud = PK.audit(M, B)
    ex = LV.extra_checks(M, B)
    bc = bracket_and_clear(M, B)
    K = M.K; ko = M.kin_ok
    knee = dict(knee_ptp=round(float(np.ptp(K["ang"][ko])), 4) if ko.any() else None, drift_max_mm=round(float(K.get("dev_max", 0.0)), 4))
    # corrected report: drive checks + bracket / clearance failures counted as lost
    bad = sorted(set(ex.get("poses_failing_ids", [])) | set(bc["poses_failing"]))
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    corr = {k: B.report()[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    B.res = res0
    th = th_margin(M, B)
    out = dict(fit_fast=fit, frozen=rep, corrected=corr, n_removed=len(bad), mode=B.mode, n=len(B.idx), why=r.get("why"),
               parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"), audit=aud, extra=ex, bracket=bc, knee=knee, th_margin=th,
               ws_inband=KL.ws_inband(B), sidecar=getattr(M1, "_sc_info", None), min_clear_taken=r.get("min_clear_taken"))
    if flood:
        MECH = _load("minarc_mech_for_kl_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
        t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "wear":
        wear, path = sys.argv[2], sys.argv[3]
        t = time.time(); out = frozen_wear(dict(BEST), wear, "--flood" in sys.argv)
        out.update(wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1")
        json.dump(out, open(path, "w"), indent=1, default=float)
        a = out["audit"]
        print(json.dumps(dict(wear=wear, fit=out["fit_fast"], frozen=out["frozen"], corrected=out["corrected"], near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=a.get("overhead140"), why=out["why"],
                              extra={k: v for k, v in out["extra"].items() if k != "poses_failing_ids"}, bracket=out["bracket"], knee=out["knee"],
                              th=out["th_margin"], ws_inband=out["ws_inband"], conn=out.get("connected"), secs=out["secs"]), default=float))
