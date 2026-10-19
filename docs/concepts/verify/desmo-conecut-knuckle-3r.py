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

  B1. THE BLENDED ONSET IN THE IK (--blend; desmo-slipper's verifier B1, copied): the built groove leads the linear K law around
      the onset (C1 quadratic over 'blend' deg of q2), the claim's IK uses the linear law; with --blend the IK carries the groove's
      real law and the stage-1 calibration is restricted to the linear part of the law.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/desmo-conecut-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--dump PATH] [--blend]
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


BLEND = "--blend" in sys.argv

# ---------------------------------------------------------------------------------------------- B1 (copied from docs/concepts/verify/desmo-slipper-knuckle-3r.py): the blended IK law
FLm = DS.FL; KRm = FLm.G.KR
import concept_kit as KIT  # noqa: E402
Base = FLm.G.KR.KB.KDesign
_BL = {}


class BlendDesign(Base):
    def _ik_phys(self, Q):
        q, ok, X1, X2, X3, s = super()._ik_phys(Q)
        P = self.p; bw = float(P.get("blend", 0.0))
        if not P.get("cam") or bw <= 0: return q, ok, X1, X2, X3, s
        L = self.law()
        if not L.get("ok"): return q, ok, X1, X2, X3, s
        u1, u2, u3 = self.u; uK = self.uK; n = len(Q); c3 = self.c[2]; m = KIT.FOLD_MARGIN; b1 = float(P["bk1"])
        sp = float(np.sign(self.psiA)) or 1.0; sg = self.q2sgn; q2hi = self._q2_at(self.th_hi, sg); s_q = float(L["s_q"])
        kK = float(P.get("kA", P.get("kK")))
        tb = math.radians(bw) / 2.0; hb = kK * tb
        tB = np.arange(-tb, float(L["ts"][-1]) + 1e-12, math.radians(0.02))
        x = kK * tB
        kab = np.where(x <= -hb, 0.0, np.where(x >= hb, x, (x + hb) ** 2 / (4 * hb)))

        def th_of(tt, kk):
            R = S.rotm(uK, sp * np.asarray(kk)); R2_ = S.rotm(u2, q2hi + s_q * np.asarray(tt))
            return np.degrees(np.arccos(np.clip(np.einsum("nij,nj->ni", R, np.einsum("nij,j->ni", R2_, u3)) @ u1, -1, 1)))
        thB = th_of(tB, kab); d = np.diff(thB); mono = int(np.argmax(d <= 0)) if (d <= 0).any() else len(d)
        tB, kab, thB = tB[: mono + 1], kab[: mono + 1], thB[: mono + 1]
        w = Q @ u3; th = np.degrees(np.arccos(np.clip(w @ u1, -1, 1)))
        sel = (th > thB[0]) & (th <= min(float(thB[-1]), float(L["th"][-1])) + 1e-9)
        _BL.update(th_start=round(float(thB[0]), 3), th_hi=round(float(self.th_hi), 3), lead_max_deg=round(math.degrees(float(np.max(kab - np.maximum(x, 0)))), 3),
                   mono_ok=bool(mono == len(d)), n_sel=int(sel.sum()), n_pre_onset=int((sel & (th <= self.th_hi)).sum()))
        if not sel.any(): return q, ok, X1, X2, X3, s
        idx = np.nonzero(sel)[0]; ths = th[idx]; Qs = Q[idx]; ws_ = w[idx]; ns = len(idx)
        tt = np.interp(ths, thB, tB); kk = np.interp(tt, tB, kab); dK = sp * kk; q2s = q2hi + s_q * tt
        Rq = S.rotm(u2, q2s); p = Rq @ u3; RK = S.rotm(uK, dK)
        q1 = S.sub1(u1, np.einsum("nij,nj->ni", RK, p), ws_)
        R1 = S.rotm(u1, q1); R12 = R1 @ RK @ Rq; vv = KRm.unit3(np.cross(u3, [0.3, 0.5, 0.8]))
        q3 = S.sub1(u3, np.broadcast_to(vv, (ns, 3)), np.einsum("nji,njk,k->ni", R12, Qs, vv))
        R3 = S.rotm(u3, q3); R123 = R12 @ R3
        t3 = np.einsum("nij,nj->ni", R12, c3[None] - R3 @ c3)
        a1e = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", RK, u2) @ u1, -1, 1)))
        cK = np.degrees(np.arccos(np.clip(p @ uK, -1, 1)))
        msub = np.minimum.reduce([ths - np.abs(b1 - cK), b1 + cK - ths, 360 - b1 - cK - ths])
        m3e = KRm.dyad_margin(ths, a1e, self.a2)
        okn = (msub >= m - 1e-6) & bool(self.k_ok) & bool(self.stops_ok)
        if P.get("m3e", 1): okn &= m3e >= m - 1e-6
        q = np.array(q, float); ok = np.array(ok, bool)
        q[idx] = np.stack([q1, q2s, q3], 1); ok[idx] = okn
        R1m = np.array(X1[0]); R1m[idx] = R1
        R2m = np.array(X2[0]); R2m[idx] = R12
        R3m = np.array(X3[0]); t3m = np.array(X3[1]); R3m[idx] = R123; t3m[idx] = t3
        X1 = (R1m, X1[1]); X2 = (R2m, X2[1]); X3 = (R3m, t3m)
        sv = np.einsum("nji,nj->ni", Qs, t3); s = np.array(s, float); s[idx] = np.stack([sv @ self.sa, sv @ self.st, sv @ self.sn], 1)
        X1b0 = np.array(self._X1b[0]); X1b0[idx] = R1 @ RK; self._X1b = (X1b0, self._X1b[1])
        self._dK = np.array(self._dK, float); self._dK[idx] = dK
        self._state = np.array(self._state); self._state[idx] = 1
        self._a1e = np.array(self._a1e, float); self._a1e[idx] = a1e
        self._msub = np.array(self._msub, float); self._msub[idx] = msub
        self._m3e = np.array(self._m3e, float); self._m3e[idx] = m3e
        self._camt = np.array(self._camt, float); self._camt[idx] = np.degrees(tt)
        self._q2now = q[:, 1]
        return q, ok, X1, X2, X3, s


def _calib_linear(self):
    """the claim's _calib restricted to the linear part of the law (|K| > hb + 0.5 deg), so the groove is the claim's"""
    D = self.D; u2 = D.u[1]; mL2 = self.link_pts["L2"][0]; mLb = self.link_pts["L1b"][0]
    hb = float(D.p.get("kK", 2.0)) * float(D.p.get("blend", 0.0)) / 2.0
    idx = np.nonzero(np.asarray(self.kin_ok, bool))[0]; th, kk = [], []
    for i in idx:
        Rb, tb = self.T(mLb, i); R2, t2 = self.T(mL2, i); Rr = Rb.T @ R2
        w = 0.5 * np.array([Rr[2, 1] - Rr[1, 2], Rr[0, 2] - Rr[2, 0], Rr[1, 0] - Rr[0, 1]])
        th.append(math.atan2(float(w @ u2), (float(np.trace(Rr)) - 1) / 2)); kk.append(abs(float(self.dK[i])))
    th = np.unwrap(np.array(th)); kk = np.array(kk); mv = kk > math.radians(max(0.5, hb + 0.5)); dw = kk < math.radians(1e-3)
    A = np.vstack([kk[mv], np.ones(mv.sum())]).T; (s_th, q_on), *_ = np.linalg.lstsq(A, th[mv], rcond=None)
    fit_rms = float(np.sqrt(np.mean((A @ np.array([s_th, q_on]) - th[mv]) ** 2)))
    dwv = th[dw] if dw.any() else np.array([q_on])
    _BL["calib"] = dict(s_th=round(float(s_th), 5), q_on_deg=round(math.degrees(float(q_on)), 3), rms_deg=round(math.degrees(fit_rms), 4), n=int(mv.sum()))
    return float(s_th), float(q_on), float(dwv.min()), float(dwv.max()), fit_rms, int(mv.sum())


if BLEND:
    FLm.G.KR.KB.KDesign = BlendDesign
    DC._DSBase._calib = _calib_linear


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
        e = 0.01; RKe = DC._rot(uK, math.radians(e) * (float(M._scg["sp"]) if getattr(M, "_scg", None) else 1.0))   # 3x3 (S.rotm gives (1,3,3))
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
        res.update(exact=os.environ.get("CB_EXACT") == "1", params=P, blend=BLEND, blend_ik=dict(_BL) if BLEND else None)
        json.dump(res, open(path, "w"), indent=1, default=float)
        print(json.dumps({k: res.get(k) for k in ("wear", "frozen", "fit_fast", "why", "overhead", "near1", "minmetal", "dK_taken_max", "n_taken", "contacts",
                                                  "v1_fit_gates", "v2_plate_horn", "v3_th_margin", "secs")}
                         | {"conn": {k: v for k, v in (res.get("connected") or {}).items() if k != "static"}, "dump": res.get("dump")}, default=float))
