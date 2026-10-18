"""Independent verifier (skeptic) of lowarm-halfring-knuckle-3r (cell B claim: desmo-conecut-knuckle-3r's chain with the
HALF RING (stage 1's dwell outer wall cut to an 18.9-deg lip, a crank stop pad on link 1b), the LOW ARM (zr 2.0) and the
LINK-2 ROOT LIFT h 1.5 / r_full 14 / L 9.836 on an R15-inner S-bend).

The claim's model (docs/concepts/models/lowarm-halfring-knuckle-3r.py) is loaded UNCHANGED (it loads and patches
desmo-conecut-knuckle-3r.py itself) and worn through its own frozen protocol (DS._frozen_model: fit Bench(60,160) fast ->
shape frozen -> worn on Bench(110,360) exact / held out). The _frozen_model call is wrapped only to keep (fit model M1,
worn model M, bench B). Checks copied from docs/concepts/verify/desmo-conecut-knuckle-3r.py (V1 fit gates, V2 plate vs horn
as solids, V3 own-state th margin + dth/dK, continuity flood, per-pose dump, B1 blended IK), plus:

  V4. TH MARGIN WITH THE CLAIM'S OWN K PLAY (the binding rule "th >= 5 including K play"): every taken pose's own-state
      margin minus play x |dth/dK|, with the dwell play the model itself measures for the hard pad
      (r['cam']['desmo']['lowarm']['dwell_K_play']['total'], 0.638 deg nominal / 0.292 tight) on dwell poses (dK = 0) and
      the parent's groove play (0.23 deg, the lead's T3 figure) on forced poses; poses that drop below 5 deg are removed
      from the taken set and Bench.report is re-run -> the corrected gap (nominal and tight).
  V5. THE LIFTED LINK 2 vs THE OTHER BODIES: the lifted bar's top copy vs the crank / tip plate / hub-2 stack crown in
      every taken pose (min distance across bodies), and the lift's root against hub 2's stack (does the lifted root still
      enter the stack, or float above it).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/lowarm-halfring-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--dump PATH] [--blend] [--cell A]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


LM = _load("lowarm_claim_v", os.path.join(REPO, "docs", "concepts", "models", "lowarm-halfring-knuckle-3r.py"))
DC = LM.DC                                                    # desmo-conecut, as patched by the claim's model
DS, S = LM.DS, LM.S
unit = S.unit
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "lowarm-halfring-knuckle-3r.json")))
BEST = ROW["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
BEST = dict(LM.CELL_B, **BEST)                                 # the row's best_params on top of the model's cell-B dict
if "--cell" in sys.argv and sys.argv[sys.argv.index("--cell") + 1] == "A": BEST = dict(LM.CELL_A)
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


TH_ROWS = []


def kplay_correct(M, B, plays):
    """V4: drop taken poses whose own-state th margin minus play x |dth/dK| < 5 deg; re-run Bench.report"""
    out = {}
    for name, (p_dw, p_fo) in plays.items():
        drop = [r[2] for r in TH_ROWS if r[0] - (p_fo if r[1] else p_dw) * abs(r[5]) < 5 - 1e-6]
        keep = {j: B.res[j] for j in drop}
        for j in drop: B.res[j] = None
        rr = B.report()
        for j, v in keep.items(): B.res[j] = v
        mins = [r[0] - (p_fo if r[1] else p_dw) * abs(r[5]) for r in TH_ROWS]
        out[name] = dict(play_dwell=p_dw, play_forced=p_fo, n_drop=len(drop), n_drop_dwell=int(sum(1 for r in TH_ROWS if r[2] in drop and not r[1])),
                         drop_ws=int(sum(1 for j in drop if B.kind[j] == "ws")), drop_clip=int(sum(1 for j in drop if B.kind[j] == "clip")),
                         min_margin_with_play=round(min(mins), 3) if mins else None,
                         report={k: rr[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")})
    dw = [r for r in TH_ROWS if not r[1]]
    out["dwell_rows"] = dict(n=len(dw), min_own=round(min(r[0] for r in dw), 3) if dw else None,
                             max_abs_dth_dK=round(max(abs(r[5]) for r in dw), 3) if dw else None)
    fo = [r for r in TH_ROWS if r[1]]
    out["forced_rows"] = dict(n=len(fo), min_own=round(min(r[0] for r in fo), 3) if fo else None,
                              max_abs_dth_dK=round(max(abs(r[5]) for r in fo), 3) if fo else None)
    return out


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
    TH_ROWS[:] = rows
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
    out = LM.frozen(dict(P)) if which == "bench" else LM.frozen_held(dict(P))
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
    lw = ((getattr(M1, "_sc_info", None) or {}).get("desmo") or {}).get("lowarm") or getattr(M1, "_lowarm", None) or {}
    res["lowarm_fit"] = lw
    try:
        pd = float(((lw.get("dwell_K_play") or {}).get("total")) or 0.638)
        res["v4_kplay"] = kplay_correct(M, B, {"nominal": (pd, 0.23), "tight": (0.292, 0.23), "parent_groove": (0.22, 0.23)})
    except Exception as e: res["v4_kplay"] = dict(error=repr(e)[:300])
    if dump:
        AP = _load("ap_for_lowarm_v", os.path.join(REPO, "tools", "alignment_paired.py"))
        poses = AP._dump_bench(M, B)
        json.dump(dict(id=LM.ID, wear=which, params=P, frozen=out["frozen"], report=B.report(), poses=poses, recomputed=AP.gap_parts(poses),
                       exact=os.environ.get("CB_EXACT") == "1", note="written by docs/concepts/verify/lowarm-halfring-knuckle-3r.py"),
                  open(dump, "w"), default=float)
        res["dump"] = dict(path=dump, recomputed=AP.gap_parts(poses))
    if flood:
        try:
            MECH = _load("minarc_mech_for_lowarm_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
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
                                                  "v1_fit_gates", "v2_plate_horn", "v3_th_margin", "v4_kplay", "secs")}
                         | {"conn": {k: v for k, v in (res.get("connected") or {}).items() if k != "static"}, "dump": res.get("dump")}, default=float))
