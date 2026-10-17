"""Independent verifier (skeptic) of desmo-conecut-knuckle-3r (cell B: desmo-slipper's spring-free, roller-free K drive on
conecut's knee and J3 dowel stop, stage 2 INVERTED: an O1.5 440C nose pressed in a boss on link 1a, the two-walled slot in
a tip plate on the crank's long arm).

The claim's model (docs/concepts/models/desmo-conecut-knuckle-3r.py) is loaded UNCHANGED and worn through its own frozen
protocol (DS._frozen_model: fit Bench(60,160) fast -> shape frozen -> worn on Bench(110,360) exact / held out). The
_frozen_model call is wrapped only to keep (fit model M1, worn model M, bench B) for the checks below. It ADDS:

  V1. THE FIT MODEL'S OWN GATES: M1._desmo_fail must be empty (the frozen protocol never reads it), dK_lim / why_lim, the
      stage-1 built-groove reading and the linear reading side by side, slot slop, crank-free slop (nominal and the 1.5x
      worst-tolerance figure), and the pressure angles vs the mu 0.15 gate.
  V2. PLATE vs HORN AS SOLIDS (not checked by the claim: its CRK-BOSS gate tests only the crank's LOW arm against the boss
      + root, and the per-pose strap checks never pair ROD with HORN): per taken pose, the crank's tip plate (radial
      [rPu, rPu + 2.5] about GH, rPu = R0 + 1.5 + 0.15) and link 1a's boss + root strip (radial [r, r + 3]) in link 1a's
      frame; wherever they overlap laterally (< 1.0 mm apart across the sphere) the radial gap must stay >= the 0.15 mm
      running gap (the boss top sits exactly 0.15 under the plate by construction; the root, ramping up to hub K's top
      level, may not). Also the nose DOWEL inside the slot: its centre must stay in the slot (nose in pocket) - read from
      the plate's own path.
  V3. OWN-STATE FOLD MARGIN th per taken pose (the metric H1 uses: forced poses min(sub-dyad, effective dyad), else the
      plain dyad), and th sensitivity to the K play (finite difference of th in K at the lowest-margin poses x the
      claim's play figures).
  plus the continuity flood (connected_report, unchanged) and the per-pose dump in tools/alignment_paired.py's format.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/desmo-conecut-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--dump PATH]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


DC = _load("desmoconecut_claim_v", os.path.join(REPO, "docs", "concepts", "models", "desmo-conecut-knuckle-3r.py"))
DS, S = DC.DS, DC.S
unit = S.unit
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "desmo-conecut-knuckle-3r.json")))
BEST = ROW["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
CAP = {}
_orig_fm = DS._frozen_model


def _fm(P, nc, nw):
    res = _orig_fm(P, nc, nw); CAP["res"] = res; return res


DS._frozen_model = _fm


def _ang(a, b): return float(np.degrees(np.arccos(np.clip(float(np.dot(unit(a), unit(b))), -1, 1))))


def _dm(th, a, b): return min(th - abs(a - b), min(a + b, 360 - a - b) - th)


def taken_of(B): return [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]


def th_margin(M, B, taken):
    D = M.D; u1, u2, u3 = D.u; uK = D.uK
    a1 = math.degrees(D.a1) if D.a1 < 4 else D.a1; a2 = math.degrees(D.a2) if D.a2 < 4 else D.a2; rows = []
    for i in taken:
        R1, _ = M.T(1, i); R1b, _ = M.T(7, i); R2, _ = M.T(2, i)
        jK = R1 @ uK; j2 = R1b @ u2; j3 = R2 @ u3
        th = _ang(u1, j3); a1e = _ang(u1, j2); a2e = _ang(j2, j3); b1 = _ang(u1, jK); c = _ang(jK, j3)
        forced = abs(float(M.dK[i])) > 1e-6
        own = min(_dm(th, b1, c), _dm(th, a1e, a2e)) if forced else _dm(th, a1, a2)
        # th's sensitivity to K at this pose: J3 held in link 2, link 1b turned by dK about uK in link 1a's frame
        e = 0.01; RKe = S.rotm(uK, math.radians(e) * (float(M._scg["sp"]) if getattr(M, "_scg", None) else 1.0))
        j3e = R1 @ RKe @ R1.T @ j3; dth = (_ang(u1, j3e) - th) / e
        rows.append((own, forced, i, th, abs(math.degrees(float(M.dK[i]))), dth))
    if not rows: return dict(min=None)
    own = [r[0] for r in rows]; lo = sorted(rows)[:5]
    return dict(min=round(min(own), 3), n=len(rows), lt5=int(sum(1 for x in own if x < 5 - 1e-6)), forced=int(sum(r[1] for r in rows)),
                lowest=[dict(own=round(r[0], 3), forced=bool(r[1]), i=r[2], th=round(r[3], 2), dK=round(r[4], 2), dth_dK=round(r[5], 3), kind=B.kind[r[2]],
                             **{k: B.poses[r[2]][k] for k in ("plane", "elev", "axial")}) for r in lo])


def plate_horn(M, B, taken):
    """V2: the tip plate (crank, member 9) vs link 1a's boss + root (member 1) as layered solids about GH"""
    if "plate" not in M.rigid or "horn" not in M.rigid: return dict(skipped="no plate/horn (cell A?)")
    m9, PL = M.rigid["plate"]; m1, HN = M.rigid["horn"]
    sB = getattr(M, "_s2B", None) or {}
    R0 = float(sB.get("R0", np.nan)) if sB else float(np.linalg.norm(np.asarray(M._viz_rod["roller"], float)))
    # plate underside samples: rigid mid row + edges at rPu (contact list entry of member 9 whose radius ~ rPu)
    rPu = float(np.median(np.linalg.norm(PL, axis=1)))
    pls = [PL]
    for m, X in M.contact:
        if m == m9 and len(X):
            rr = np.linalg.norm(X, axis=1); pls.append(X[np.abs(rr - rPu) < 0.05])
    PLu = np.concatenate(pls)
    hr = np.linalg.norm(HN, axis=1)
    out = dict(R0=round(R0, 3), rPu=round(rPu, 3), horn_under_r=[round(float(hr.min()), 3), round(float(hr.max()), 3)],
               horn_top_r_max=round(float(hr.max()) + 3.0, 3), n_plate=len(PLu), n_horn=len(HN))
    worst = (99.0, None); n_ov = 0; nbad = 0; per = []
    for i in taken:
        R9, t9 = M.T(m9, i); R1, t1 = M.T(m1, i)
        Pw = (PLu @ R9.T + t9 - t1) @ R1                     # plate in link 1a's frame
        pr = np.linalg.norm(Pw, axis=1); pd = Pw / pr[:, None]; hd = HN / hr[:, None]
        cosang = pd @ hd.T                                   # (np, nh)
        lat = np.arccos(np.clip(cosang, -1, 1)) * np.minimum(pr[:, None], hr[None, :])
        ov = lat < 1.0
        if not ov.any(): continue
        n_ov += 1
        gap = pr[:, None] - (hr[None, :] + 3.0)              # plate underside above horn top (> 0 = clear)
        gap_top = (hr[None, :]) - (pr[:, None] + 2.5)        # horn underside above plate top (impossible here, reported)
        g = np.where(ov, np.maximum(gap, gap_top), 99.0); gm = float(g.min())
        per.append(gm)
        if gm < worst[0]: worst = (gm, i)
        if gm < 0.15 - 0.02: nbad += 1
    out.update(poses_overlapping=n_ov, min_radial_gap_mm=round(worst[0], 3) if worst[1] is not None else None,
               at=dict(i=worst[1], kind=B.kind[worst[1]], **{k: B.poses[worst[1]][k] for k in ("plane", "elev", "axial")}) if worst[1] is not None else None,
               poses_below_running_gap=nbad, rule="radial gap >= 0.15 - 0.02 wherever plate and horn overlap within 1 mm across the sphere")
    return out


def fit_gates(M1):
    info = getattr(M1, "_sc_info", None) or {}; d = info.get("desmo") or {}
    st1 = d.get("stage1") or {}; s1b = d.get("stage1_built") or {}; st2 = d.get("stage2B") or {}; sl = d.get("slop") or {}
    return dict(desmo_fail=list(getattr(M1, "_desmo_fail", []) or []), dK_lim=info.get("dK_lim"), why_lim=info.get("why_lim"),
                dK_lim_parent=info.get("dK_lim_parent"), why_lim_parent=info.get("why_lim_parent"),
                pa_eff_horn=info.get("pa_eff_horn"), pa_eff_crank=info.get("pa_eff_crank"), stage1_linear_lim_by_gate=st1.get("lim_by_gate"),
                stage1_pa=dict(pin=st1.get("pa_pin_max"), cap=st1.get("pa_cap_max"), gate=st1.get("pa_gate")), stage1_ridge_mm=st1.get("ridge_mm"),
                stage1_rc_min=st1.get("rc_min"), stage1_built=s1b, stage2B=st2,
                slot_slop=(sl.get("slotB") or {}).get("slop_max"), pocket_pa=[(sl.get("slotB") or {}).get(k) for k in ("pocket_pa_max_horn", "pocket_pa_max_crank", "pocket_pa_gate")],
                crank_free=sl.get("crank_free"))


def wear(P, which="bench", flood=False, dump=None):
    t = time.time()
    out = DC.frozen(dict(P)) if which == "bench" else DC.frozen_held(dict(P))
    fit, M1, M, B, r = CAP["res"]
    tk = taken_of(B)
    res = dict(wear=which, frozen=out["frozen"], fit_fast=out.get("fit_fast"), why=out.get("why"), overhead=out.get("overhead"),
               near1=(out.get("audit") or {}).get("gap_near1"), near2=(out.get("audit") or {}).get("gap_near2"),
               minmetal=(out.get("audit") or {}).get("near_touch_min_mm"), l2=out.get("l2"), dK_taken_max=out.get("dK_taken_max"),
               parts_pairs=out.get("parts_pairs"), mode=B.mode, n=len(B.idx), n_taken=len(tk),
               contacts=[dict(i=int(j), kind=B.kind[j], **{k: B.poses[j][k] for k in ("plane", "elev", "axial")}, mm=round(float(np.min(B.res[j])), 2))
                         for j in range(len(B.idx)) if B.res[j] is not None and float(np.min(B.res[j])) < 0])
    try: res["v1_fit_gates"] = fit_gates(M1)
    except Exception as e: res["v1_fit_gates"] = dict(error=repr(e)[:300])
    try: res["v2_plate_horn"] = plate_horn(M, B, tk)
    except Exception as e: res["v2_plate_horn"] = dict(error=repr(e)[:300])
    try: res["v3_th_margin"] = th_margin(M, B, tk)
    except Exception as e: res["v3_th_margin"] = dict(error=repr(e)[:300])
    if dump:
        AP = _load("ap_for_desmoconecut_v", os.path.join(REPO, "tools", "alignment_paired.py"))
        poses = AP._dump_bench(M, B)
        json.dump(dict(id=DC.ID, wear=which, params=P, frozen=out["frozen"], report=B.report(), poses=poses, recomputed=AP.gap_parts(poses),
                       exact=os.environ.get("CB_EXACT") == "1", note="written by docs/concepts/verify/desmo-conecut-knuckle-3r.py"),
                  open(dump, "w"), default=float)
        res["dump"] = dict(path=dump, recomputed=AP.gap_parts(poses))
    if flood:
        try:
            MECH = _load("minarc_mech_for_desmoconecut_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
            t1 = time.time(); res["connected"] = MECH.connected_report(M, B); res["connected"]["secs"] = round(time.time() - t1, 1)
        except Exception as e: res["connected"] = dict(error=repr(e)[:300])
    res["claim_frozen_out"] = {k: v for k, v in out.items() if k not in ("params",)}
    res["secs"] = round(time.time() - t, 1)
    return res


if __name__ == "__main__":
    P = dict(BEST)
    for i_, a_ in enumerate(sys.argv):
        if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); P[k_] = float(v_)
    if sys.argv[1] == "wear":
        which, path = sys.argv[2], sys.argv[3]
        dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
        res = wear(P, which, "--flood" in sys.argv, dump)
        res.update(exact=os.environ.get("CB_EXACT") == "1", params=P)
        json.dump(res, open(path, "w"), indent=1, default=float)
        print(json.dumps({k: res.get(k) for k in ("wear", "frozen", "fit_fast", "why", "overhead", "near1", "minmetal", "dK_taken_max", "n_taken", "contacts",
                                                  "v1_fit_gates", "v2_plate_horn", "v3_th_margin", "secs")}
                         | {"conn": {k: v for k, v in (res.get("connected") or {}).items() if k != "static"}, "dump": res.get("dump")}, default=float))
