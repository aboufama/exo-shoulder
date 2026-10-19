"""Independent verifier (skeptic) of desmo-slipper-knuckle-3r (the verified lead slipper-nose-knuckle-3r with its clock
spring, stop A and stage-1 roller deleted: a crowned O1.5 pin in a groove under hub 2's cap ring + the O2.5 nose in a
two-walled swept-envelope slot, positive both ways).

The claim's model (docs/concepts/models/desmo-slipper-knuckle-3r.py) is loaded UNCHANGED, last (its chain patches the
shared kit modules). This harness re-uses the LEAD's verifier (docs/concepts/verify/slipper-nose-knuckle-3r.py: N1
pressure angle with friction at every taken pose, N2 conjugate validity, N3 relative pole, closure in the world, nose vs
lug, K sense, own-state th margin) retargeted at DSModel, plus the continuity flood, plus the per-pose dump in
tools/alignment_paired.py's format (T5 contact depth, paired comparison with the lead's dump on the same poses).

It ADDS:
  B1. THE BLENDED ONSET IN THE IK (--blend): the claim's groove leads the linear K law around the onset (a C1 quadratic
      over 'blend' deg of q2, up to blend * kK / 8 deg of K = 2.69 deg at blend 10), but the claim's IK uses the linear
      law. With --blend the design's IK carries the groove's real law: for th past th_law_blend(-blend/2) the pose is
      solved on the blended table (t, K) instead of stop A / the linear table, with the parent's own closure and fold
      margins (msub, m3e >= 5). The stage-1 cam calibration is restricted to the linear part of the law (|K| > hb + 0.5)
      so the groove geometry is the claim's. Fit and wear both use the blended IK (the shape a builder would fit).

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/desmo-slipper-knuckle-3r.py wear <bench|held> <out.json> [--blend] [--flood] [--dump PATH]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

os.environ.setdefault("SN_CELL", "lead")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import types                                                 # noqa: E402

BLEND = "--blend" in sys.argv


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


VS = _load("slipper_verifier_for_desmo_v", os.path.join(HERE, "slipper-nose-knuckle-3r.py"))          # the lead's verifier
H, LV = VS.H, VS.LV
DS = _load("desmo_claim_v", os.path.join(REPO, "docs", "concepts", "models", "desmo-slipper-knuckle-3r.py"))   # loaded LAST
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "desmo-slipper-knuckle-3r.json")))
BEST = ROW["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)
S = DS.S
import concept_kit as KIT                                    # noqa: E402
FLm = DS.FL
KRm = FLm.G.KR
D2R = math.pi / 180


def retarget(P):
    nr = float(DS._clamp(dict(DS.PARAMS, **P))["nose_r"])
    H.RF = types.SimpleNamespace(phi_of=DS.RF.phi_of, dphi_of=DS.RF.dphi_of, ROLL_R=nr, _ring=DS.RF._ring,
                                 RFModel=DS.DSModel, _clamp=DS._clamp, PARAMS=DS.PARAMS)
    H.SC, H.S, H.PK = DS.SC, DS.S, DS.PK
    H.ROLL_R = nr; H.BEST = dict(P)
    return nr


# ---------------------------------------------------------------------------------------------- B1: the blended IK law
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
    DS.DSModel._calib = _calib_linear


def wear(P, which="bench", flood=False, dump=None):
    nc, nw = (110, 360) if which == "bench" else (-1, -1)
    fit, M1, M, B, r = DS._frozen_model(dict(P), nc, nw)
    rep = {k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    aud = DS.PK.audit(M, B)
    ex = VS.extra_checks(M, M1, B)
    ws = np.array(B.kind) == "ws"; elev = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None else np.nan for j in range(len(B.idx))])
    ov = ws & (elev >= 140)
    info = getattr(M1, "_sc_info", None) or {}
    out = dict(fit_fast=fit, frozen=rep, mode=B.mode, n=len(B.idx), why=r.get("why"), parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"),
               audit=aud, extra=ex, l2=getattr(M, "_l2", None), overhead=dict(ws=int(ov.sum()), taken=int((ov & (mins >= 0)).sum())),
               desmo=info.get("desmo"), dK_lim=info.get("dK_lim"), why_lim=info.get("why_lim"), blend_ik=dict(_BL) if BLEND else None,
               contacts=[dict(i=int(j), kind=B.kind[j], elev=B.poses[j]["elev"], plane=B.poses[j]["plane"], axial=B.poses[j]["axial"], mm=round(float(mins[j]), 2))
                         for j in range(len(B.idx)) if not np.isnan(mins[j]) and mins[j] < 0])
    if dump:
        AP = _load("ap_for_desmo_v", os.path.join(REPO, "tools", "alignment_paired.py"))
        poses = AP._dump_bench(M, B)
        json.dump(dict(id=DS.ID + ("+blend" if BLEND else ""), wear=which, params=P, frozen=rep, report=B.report(), poses=poses,
                       recomputed=AP.gap_parts(poses), exact=os.environ.get("CB_EXACT") == "1", note="written by docs/concepts/verify/desmo-slipper-knuckle-3r.py"),
                  open(dump, "w"), default=float)
        out["dump"] = dict(path=dump, recomputed=AP.gap_parts(poses))
    if flood:
        MECH = _load("minarc_mech_for_desmo_v", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
        t = time.time(); out["connected"] = MECH.connected_report(M, B); out["connected"]["secs"] = round(time.time() - t, 1)
    return out


if __name__ == "__main__":
    P = dict(BEST)
    for i_, a_ in enumerate(sys.argv):                         # --set k=v (the fixed placement: --set a_s=9.75 --set psi=148)
        if a_ == "--set": k_, v_ = sys.argv[i_ + 1].split("=", 1); P[k_] = float(v_)
    retarget(P)
    if sys.argv[1] == "fast":
        old = os.environ.pop("CB_EXACT", None); B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
        r, M = DS._report(B, dict(P))
        cf = (((r.get("cam") or {}).get("desmo") or {}).get("slop") or {}).get("crank_free", {})
        print(json.dumps(dict(blend=BLEND, set={k: P[k] for k in ("a_s", "psi", "mu")}, dK_lim=(r.get("cam") or {}).get("dK_lim"), why_lim=(r.get("cam") or {}).get("why_lim"),
                              free_max=cf.get("max_deg"), gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), ib10=r.get("inband10"), l2=r.get("l2"), reach=r["reach"], follow=r["follow"], inband14=r["inband14"], contact=r["contact"], why=r.get("why"),
                              honest=r.get("honest"), desmo_fail=r.get("desmo_fail"), blend_ik=dict(_BL), secs=round(time.time() - t, 1)), default=float)); sys.exit()
    if sys.argv[1] == "wear":
        which, path = sys.argv[2], sys.argv[3]
        dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
        t = time.time(); out = wear(P, which, "--flood" in sys.argv, dump)
        out.update(wear=which, blend=BLEND, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", params=P)
        json.dump(out, open(path, "w"), indent=1, default=float)
        e = out["extra"]
        print(json.dumps(dict(wear=which, blend=BLEND, fit=out["fit_fast"], frozen=out["frozen"], why=out["why"], near1=out["audit"].get("gap_near1"),
                              minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["overhead"], blend_ik=out["blend_ik"], contacts=out["contacts"],
                              extra={k: e.get(k) for k in ("n_taken", "closure_max_mm", "poses_failing", "why_failing", "corrected", "th_margin", "wrong_sense",
                                                           "dK_taken_max_deg", "dK_lim_deg", "pa_rule", "at_pa45_friction", "nose")},
                              conn={k: v for k, v in (out.get("connected") or {}).items() if k != "static"}, secs=out["secs"]), default=float))
