"""Alignment auditor: hub-only determinacy of the UNSENSED pin knee on minarc-stop-knuckle-4r (simplicity v2 audit,
user ruling 2026-10-17 "if no encoders are needed, it doesn't count as added complexity").

minarc has 4 hub encoders (J1, K, J2, J3: K is a sensed, sprung O20 hub counted as the 4th active joint) and a two-pin
cuff knee (pins a, b) that v2 scores 0 because it carries no encoder. The question: with ONLY the 4 hub encoders read,
are the knee pins and the arm's GH rotation fixed at every taken pose?

Same method as tools/alignment_knee_sensing.py (finite differences of the model's OWN closure, model loaded unchanged,
no metal sampled), extended to the 4-DOF loop: the loop with GH as a ball joint has the arm's 3 rotations PLUS the spherical
4-bar self-motion J1-K-J2-J3 (K free). Columns of Z: d(coords)/d(GH rotation x, y, z) at fixed K, and d(coords)/d(dK) at
fixed arm. Coords: J1 = q1, J2 = q2 (link 2 vs link 1b), J3 = member 3 vs link 2 about u3, K = dK, pin a, pin b, GH x3.
N = Z (Z^T Z)^(-1/2); sensing number = sigma_min(N[hub rows]).
  * hub4   = rows J1, J2, J3, K (the encoders the CAD carries; K's encoder is the CAD's '4th encoder')
  * hub3_Kfree = rows J1, J2, J3 with K free (what it would be if K's encoder were dropped) - rank 3 of 4 = 0 by construction
  * law    = 3 columns from the model's own ik (K set by its spring / stop law, phys J2 stops), rows J1, J2, J3
The closure at a prescribed dK is the variant-B ik (docs/concepts/models/minarc-stop-knuckle-4r-pinknee.py KDesign.ik)
with its law() returning the a1e of that dK; it is checked against the model's own phys ik at the model's dK (q diff).

Pose sets: (a) the contact-aware TAKEN nodes of the full 1432-pose workspace grid (the verifier's conn_taken file, the
frozen shape's knee centre m from that file); (b) every pose of the pose library that the frozen design closes
kinematically (ik ok, knee ok, radial drift <= R_tol) - a superset of every taken bench / held-out / clip pose.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_knee_sensing_minarc.py [pick1|BDp] [out.json]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

VER = os.path.join(REPO, "docs", "research", "minarc_final_polish", "verify")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


R = _load("aks_minarc_remeasure", os.path.join(REPO, "docs", "concepts", "verify", "minarc-bdp-remeasure.py"))
KR = R.KR; KB = KR.KB; PK = KR.PK; S = KR.S
_LAW0 = KB.KA.law
# the variant-B design class itself (the kit-rule module rebinds KB.KDesign to its KRDesign, whose phys ik ignores law())
VB = [c for c in KR.KRDesign.__mro__ if c.__name__ == "KDesign" and c.__module__ == KB.__name__][0]


def wrap(a): return (np.asarray(a) + np.pi) % (2 * np.pi) - np.pi


def rotv(v):
    th = float(np.linalg.norm(v))
    if th < 1e-15: return np.eye(3)
    k = v / th; Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(th) * Kx + (1 - math.cos(th)) * Kx @ Kx


def rodr(ax, ang):
    ax = ax / np.linalg.norm(ax); ang = np.atleast_1d(ang); return np.stack([rotv(ax * a) for a in ang])


def a1e_of_dK(D, dK):
    b1, b2 = float(D.p["bk1"]) * np.pi / 180, float(D.p["bk2"]) * np.pi / 180
    psi = np.sign(D.psiA) * (np.asarray(dK, float) + D.psiA)
    return np.degrees(np.arccos(np.clip(math.cos(b1) * math.cos(b2) + math.sin(b1) * math.sin(b2) * np.cos(psi), -1, 1)))


def closure(D, Q, dK):
    """variant-B closure at a prescribed K rotation dK (n,) -> q (n,3), X2, s, dK used"""
    a1e = a1e_of_dK(D, dK)

    def law(p1, p3, p):
        th = np.degrees(np.arccos(np.clip((S.unit(p1) * S.unit(p3)).sum(-1), -1, 1)))
        return a1e.copy(), np.zeros(len(th), int), th
    KB.KA.law = law
    try: q, ok, X1, X2, X3, s = VB.ik(D, Q)
    finally: KB.KA.law = _LAW0
    return q, X2, s, np.asarray(D._dK, float).copy()


def coords(D, Q, q, X2, s, dK):
    """-> (n, 6): J1, J2, J3 (hub reading), dK, qa, qb; knee ok; axis err; phi"""
    Kn = D.knee(s); phi = np.asarray(Kn["phi"], float); u3 = D.u[2]; sn = D.sn
    M3 = np.einsum("nij,njk->nik", Q, rodr(sn, phi)); Rrel = np.einsum("nji,njk->nik", X2[0], M3)
    aerr = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", Rrel, u3) @ u3, -1, 1)))
    e = np.cross(u3, [0.3, 0.5, 0.8]); e /= np.linalg.norm(e); f = np.cross(u3, e)
    v = np.einsum("nij,j->ni", Rrel, e); j3 = np.arctan2(v @ f, v @ e)
    return np.c_[q[:, 0], q[:, 1], j3, dK, Kn["qa"], Kn["qb"]], np.asarray(Kn["ok"], bool), aerr, phi, np.asarray(Kn["ang"], float)


def sens(Zc, ncol_gh, hub_rows):
    """Zc (6, ncol): coordinate derivatives; GH rows appended (identity on the first ncol_gh columns)"""
    ncol = Zc.shape[1]; G = np.zeros((3, ncol)); G[:, :ncol_gh] = np.eye(3)
    if not np.isfinite(Zc).all(): return float("nan"), float("nan")
    Z = np.r_[Zc, G]; U, sz, _ = np.linalg.svd(Z, full_matrices=False)
    if sz[-1] < 1e-9 * sz[0]: return float("nan"), float("nan")   # degenerate column (closure did not move): not a sensing number
    N = U[:, :ncol]                                          # orthonormal basis of the loop's velocity null space (= Z (Z^T Z)^-1/2 up to rotation)
    sh = np.linalg.svd(N[hub_rows], compute_uv=False)
    return float(sh[-1]) if len(sh) >= ncol else 0.0, float(sh[0] / max(sh[-1], 1e-12)) if len(sh) >= ncol else float("inf")


def analyse(D, Qs, h=1e-4):
    n = len(Qs)
    q0, ok0, X10, X20, X30, s0 = D.ik(Qs); dK0 = np.asarray(D._dK, float).copy(); st0 = np.asarray(D._state).copy()
    c0, kok0, _, _, ang0 = coords(D, Qs, q0, X20, s0, dK0)
    # consistency: the prescribed-dK closure at the model's own dK reproduces the model's phys ik
    qc, X2c, sc, _ = closure(D, Qs, dK0)
    cc, _, aerr, _, _ = coords(D, Qs, qc, X2c, sc, dK0)
    cons = np.degrees(np.abs(wrap(cc - c0))).max(1)
    E = np.eye(3); cols = []
    for k in range(3):                                       # GH rotation at fixed K
        cp = [];
        for sg in (1, -1):
            Qp = np.einsum("ij,njk->nik", rotv(sg * h * E[k]), Qs); qp, X2p, sp_, _ = closure(D, Qp, dK0)
            cp.append(coords(D, Qp, qp, X2p, sp_, dK0)[0])
        cols.append(wrap(cp[0] - cp[1]) / (2 * h))
    cp = []
    for sg in (1, -1):                                       # K self-motion at fixed arm
        qp, X2p, sp_, dKu = closure(D, Qs, dK0 + sg * h); cp.append(coords(D, Qs, qp, X2p, sp_, dKu)[0])
    cols.append(wrap(cp[0] - cp[1]) / (2 * h))
    Zall = np.stack(cols, 2)                                 # (n, 6, 4)
    lawc = []                                                # the model's own law (K from spring / stop law, phys ik)
    for k in range(3):
        cp = []
        for sg in (1, -1):
            Qp = np.einsum("ij,njk->nik", rotv(sg * h * E[k]), Qs); qp, okp, X1p, X2p, X3p, sp_ = D.ik(Qp); dKp = np.asarray(D._dK, float).copy()
            cp.append(coords(D, Qp, qp, X2p, sp_, dKp)[0])
        lawc.append(wrap(cp[0] - cp[1]) / (2 * h))
    Zlaw = np.stack(lawc, 2)
    s4 = np.zeros(n); c4 = np.zeros(n); s3 = np.zeros(n); sl = np.zeros(n); cl = np.zeros(n); Jc = np.zeros(n); kf = np.zeros(n)
    for i in range(n):
        s4[i], c4[i] = sens(Zall[i], 3, [0, 1, 2, 3])
        s3[i], _ = sens(Zall[i], 3, [0, 1, 2])
        sl[i], cl[i] = sens(Zlaw[i][[0, 1, 2, 4, 5]], 3, [0, 1, 2])
        if not np.isfinite(Zall[i]).all(): Jc[i] = np.nan; continue
        sv = np.linalg.svd(Zall[i][:4], compute_uv=False); Jc[i] = sv[0] / max(sv[-1], 1e-12)
    # R10 caveat: arm-twist error of the hub reading per mm of in-plane GH drift (the knee absorbs the drift)
    hs = 0.01; gph = np.zeros(n)
    for a in range(2):
        dv = np.zeros(3); dv[a] = hs
        Kp = D.knee(s0 + dv); Km = D.knee(s0 - dv); gph += (wrap(np.asarray(Kp["phi"]) - np.asarray(Km["phi"])) / (2 * hs)) ** 2
    gph = np.degrees(np.sqrt(gph))
    return dict(s4=s4, c4=c4, s3=s3, sl=sl, cl=cl, Jc=Jc, cons=cons, aerr=aerr, st=st0, dK=np.degrees(dK0), ang=ang0, gph=gph, ok=ok0 & kok0, s=s0)


def summ(A, sel, poses=None):
    nonfinite = int((sel & ~(np.isfinite(A["s4"]) & np.isfinite(A["sl"]))).sum())
    sel = sel & np.isfinite(A["s4"]) & np.isfinite(A["sl"])
    def st(x): x = x[sel]; return dict(min=round(float(x.min()), 4), p5=round(float(np.percentile(x, 5)), 4), median=round(float(np.median(x)), 4)) if len(x) else None
    i4 = np.nonzero(sel)[0][int(np.argmin(A["s4"][sel]))] if sel.any() else None
    out = dict(n=int(sel.sum()), nonfinite_dropped=nonfinite, hub4_sigma_min=st(A["s4"]), hub4_cond_max=round(float(A["c4"][sel].max()), 2),
               hub4_raw_J_cond_max=round(float(A["Jc"][sel].max()), 2),
               hub3_Kfree_sigma_min_max=float(f"{A['s3'][sel].max():.2e}"),
               law_hub3_sigma_min=st(A["sl"]), law_cond_max=round(float(A["cl"][sel].max()), 2),
               forced=dict(n=int((sel & (A["st"] != 0)).sum()), hub4_sigma_min=round(float(A["s4"][sel & (A["st"] != 0)].min()), 4) if (sel & (A["st"] != 0)).any() else None,
                           law_sigma_min=round(float(A["sl"][sel & (A["st"] != 0)].min()), 4) if (sel & (A["st"] != 0)).any() else None),
               stateA=dict(n=int((sel & (A["st"] == 0)).sum()), hub4_sigma_min=round(float(A["s4"][sel & (A["st"] == 0)].min()), 4) if (sel & (A["st"] == 0)).any() else None),
               closure_vs_model_q_deg_max=float(f"{A['cons'][sel].max():.2e}"), member3_axis_err_deg_max=float(f"{A['aerr'][sel].max():.2e}"),
               knee_ang=[round(float(A["ang"][sel].min()), 2), round(float(A["ang"][sel].max()), 2)],
               corr_s4_knee_ang=round(float(np.corrcoef(A["s4"][sel], A["ang"][sel])[0, 1]), 3) if sel.sum() > 2 else None,
               gh_drift_twist_deg_per_mm=dict(max=round(float(A["gph"][sel].max()), 3), median=round(float(np.median(A["gph"][sel])), 3)))
    if poses is not None and i4 is not None: out["hub4_worst_pose"] = poses[i4]; out["hub4_worst_dK_deg"] = round(float(A["dK"][i4]), 2); out["hub4_worst_knee_ang"] = round(float(A["ang"][i4]), 2)
    return out


def main():
    cfg = sys.argv[1] if len(sys.argv) > 1 else "pick1"; outp = sys.argv[2] if len(sys.argv) > 2 else None; t0 = time.time()
    P = dict(KR.PARAMS, **json.load(open(os.path.join(VER, f"v_{cfg}_fit60_bench_params.json"))))
    ct = json.load(open(os.path.join(VER, f"v_{cfg}_fit60_bench_conn_taken.json")))
    D = KR.KRDesign(dict(P)); D.m = np.array(ct["m"], float); D.m[2] = 0.0
    Zg, W, POSE, HG = R.ws_grid(); HG = np.asarray(HG, float); _ = D.ik(HG[:2])
    keys = {tuple(round(float(x), 1) for x in k) for k in ct["connected_keys"]}
    gsel = np.array([(round(float(p[0]), 1), round(float(p[1]), 1), round(float(p[2]), 1)) in keys for p in POSE])
    gp = [dict(plane=float(p[0]), elev=float(p[1]), axial=float(p[2])) for p in POSE]
    Ag = analyse(D, HG)
    out = dict(id="minarc-stop-knuckle-4r", config=cfg, params_file=os.path.relpath(os.path.join(VER, f"v_{cfg}_fit60_bench_params.json"), REPO),
               knee_centre_m=ct["m"], sn_vs_u3_deg=round(float(np.degrees(np.arccos(min(1.0, abs(float(D.sn @ D.u[2])))))), 6))
    out["grid_taken"] = summ(Ag, gsel, gp); out["grid_taken"]["expected"] = ct["grid"]["nodes"]
    oh = gsel & (POSE[:, 1] >= 140); out["grid_taken_overhead140"] = summ(Ag, oh, gp) if oh.any() else None
    # (b) every pose of the library the frozen design closes kinematically
    Zl = CB._poses_all(); QL = np.asarray(Zl["HG"], float)
    Al = analyse(D, QL); kin = Al["ok"] & (np.abs(Al["s"][:, 2]) <= float(D.p["R_tol"]))
    out["library_kinematic"] = summ(Al, kin); out["library_kinematic"]["of"] = int(len(QL))
    out["secs"] = round(time.time() - t0, 1)
    out["note"] = ("hub4 sigma_min > 0 with a finite condition at every pose = the 4 hub encoders (J1, J2, J3, K) fix both knee pins and "
                   "the GH rotation (GH a ball joint; GH translation, R10, is not in the model: the pins absorb it, gh_drift_twist is the "
                   "hub-only arm-twist error per mm of that drift). hub3_Kfree = 0 means K's own encoder is required (it is in the CAD). "
                   "Calibration: skin-normal-3r-pin-knee 8-row 0.39 (docs/concepts/skin-normal-3r-pin-knee.md line 566), 0.383 re-run "
                   "with tools/alignment_knee_sensing.py.")
    if outp: json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(out, default=float))


if __name__ == "__main__":
    main()
