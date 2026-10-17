"""Alignment auditor's determinacy check for an UNSENSED pin knee (simplicity v2, user ruling 2026-10-17 "if no encoders are
needed, it doesn't count as added complexity"): with ONLY the hub encoders read (J1, J2, J3; a slaved knuckle K known from
its drive law, never read), is every passive coordinate - K, knee pin a, knee pin b - and the arm's GH rotation fixed at
every taken pose?

Method (finite differences of the model's OWN closure, the model loaded unchanged, init only - no metal is sampled):
  * the design's ik(Q) at each taken pose Q and at Q rotated by +-h about the world x, y, z axes through GH (h = 1e-4 rad);
  * the encoder readings a real hub sees: J1 = q1 (link 1a vs base), J2 = q2 (link 2 vs link 1b), J3 = the angle of member 3
    vs link 2 about u3, member 3 being Q rot(sn, phi) (the model's T(3)) - so J3 = q3_ik + phi when sn || u3 (checked);
    the passive coordinates: dK (the model's _dK), pin a qa, pin b qb (the model's knee());
  * Z (rows x 3) = d(coordinates) / d(GH rotation); the loop's velocity null space is spanned by Z, so the orthonormal basis
    is N = Z (Z^T Z)^(-1/2) and the hub-only sensing number is sigma_min(N[hub rows]) - the same quantity as
    docs/research/rebase/verify_rebase_pinknee.py (8 rows: J1, J2, J3, pin a, pin b, GH x3) for skin-normal-3r-pin-knee
    (>= 0.39 there). Reported with 8 rows (K known from its law, not a row) and with 9 (K a row too);
  * raw: sigma_min / condition of J_h = d(J1, J2, J3)/d(GH rotation) (rad per rad), and the 1-D knee factor
    d(J3)/d(q3_ik) = 1 + dphi/dq3 (the only place the knee enters: member 3's hub centre drift depends on q3 alone).
  * also flags: poses where a perturbed ik is not ok (an edge of the taken set) are reported, not dropped.

Taken poses: docs/alignment/remeasure/<id>_<bench|held>_perpose.json ('taken'), else the kinematic set (kin_ok) of the init.

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/alignment_knee_sensing.py <id> [bench|held] [out.json]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def adapter(did):
    """-> (model class, clamp(params) -> params, default PARAMS, pin-knee module PK, kit S)"""
    mod = _load(did.replace("-", "_") + "_ks", os.path.join(REPO, "docs", "concepts", "models", did + ".py"))
    if hasattr(mod, "RLModel"):                               # roller-longdyad: RLModel patched into SC
        return mod.RLModel, mod._clamp, mod.PARAMS, mod.PK, mod.S
    if hasattr(mod, "SCModel"):
        return mod.SCModel, mod._clamp, mod.PARAMS, mod.PK, mod.S
    if hasattr(mod, "Model") and hasattr(mod, "Design"):      # skin-normal-3r-pin-knee (calibration)
        return mod.Model, (lambda p: p), getattr(mod, "PARAMS", {}), mod, mod.S
    raise SystemExit(f"no adapter for {did}")


def rotv(axis_vec):
    th = float(np.linalg.norm(axis_vec))
    if th < 1e-15: return np.eye(3)
    k = axis_vec / th; Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(th) * Kx + (1 - math.cos(th)) * Kx @ Kx


def rodr(ax, ang):
    ax = ax / np.linalg.norm(ax); ang = np.atleast_1d(ang); out = np.zeros((len(ang), 3, 3))
    for j, a in enumerate(ang): out[j] = rotv(ax * a)
    return out


def wrap(a): return (np.asarray(a) + np.pi) % (2 * np.pi) - np.pi


def readings(D, Q):
    """ik + knee at the stacked arm orientations Q (n,3,3) -> coords (n, 6): J1, J2, J3(hub), dK, qa, qb; ok; axis check"""
    q, ok, X1, X2, X3, s = D.ik(Q)
    dK = np.asarray(getattr(D, "_dK", np.zeros(len(Q))), float)
    Kn = D.knee(s); ok = ok & Kn["ok"]
    phi = np.asarray(Kn["phi"], float); u3 = D.u[2]; sn = D.sn
    R12 = X2[0]
    M3 = np.einsum("nij,njk->nik", Q, rodr(sn, phi))                           # member 3 = Q rot(sn, phi) (model T(3))
    Rrel = np.einsum("nji,njk->nik", R12, M3)                                  # member 3 in link 2's frame
    axis_err = np.degrees(np.arccos(np.clip(np.einsum("nij,j->ni", Rrel, u3) @ u3, -1, 1)))   # must be 0: a revolute about u3
    e = np.cross(u3, [0.3, 0.5, 0.8]); e /= np.linalg.norm(e); f = np.cross(u3, e)
    v = np.einsum("nij,j->ni", Rrel, e); j3 = np.arctan2(v @ f, v @ e)
    readings.ang = np.asarray(Kn["ang"], float)
    return np.c_[q[:, 0], q[:, 1], j3, dK, Kn["qa"], Kn["qb"]], ok, axis_err, q[:, 2]


def taken_set(did, wear, M):
    fp = os.path.join(REPO, "docs", "alignment", "remeasure", f"{did}_{wear}_perpose.json")
    if os.path.exists(fp):
        d = json.load(open(fp)); idx = [p["i"] for p in d["poses"] if p.get("taken")]
        return idx, os.path.relpath(fp, REPO)
    return [int(i) for i in np.nonzero(M.kin_ok)[0]], "kin_ok (no per-pose file)"


def main():
    did = sys.argv[1]; wear = sys.argv[2] if len(sys.argv) > 2 else "bench"; outp = sys.argv[3] if len(sys.argv) > 3 else None
    t0 = time.time()
    Mcls, clamp, PARAMS, PK, S = adapter(did)
    row = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", did + ".json")))
    best = row["best_params"]; best = json.loads(best) if isinstance(best, str) else best
    P = clamp(dict(PARAMS, **best))
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = Mcls(B1, dict(P))                                     # init only: the knee centre m is set here (as in frozen())
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]
    if wear == "held":
        PV = _load("pk_polish_ks", os.path.join(REPO, "docs", "concepts", "verify", "skin-normal-3r-pin-knee-polish.py")); B = PV.held_bench()
    else:
        B = CB.Bench(n_clip=110, n_ws=360)
    M = Mcls(B, dict(P2)); D = M.D
    taken, src = taken_set(did, wear, M)
    not_kin = [i for i in taken if not M.kin_ok[i]]
    sn_u3 = float(np.degrees(np.arccos(min(1.0, abs(float(D.sn @ D.u[2]))))))
    h = 1e-4; E = np.eye(3)
    rows = []
    for i in taken:
        Q0 = M.Q[i]
        Qs = [Q0] + [rotv(sg * h * E[k]) @ Q0 for k in range(3) for sg in (1, -1)]
        c, ok, aerr, q3ik = readings(D, np.stack(Qs))
        Zc = np.zeros((6, 3)); dq3 = np.zeros(3)
        for k in range(3):
            a, b = 1 + 2 * k, 2 + 2 * k
            Zc[:, k] = wrap(c[a] - c[b]) / (2 * h); dq3[k] = wrap(q3ik[a] - q3ik[b]) / (2 * h)
        Jh = Zc[:3]
        sJ = np.linalg.svd(Jh, compute_uv=False)
        res = {}
        for nm, sel in (("8row_K_from_law", [0, 1, 2, 4, 5]), ("9row_K_as_row", [0, 1, 2, 3, 4, 5])):
            Z = np.r_[Zc[sel], np.eye(3)]
            w, V = np.linalg.eigh(Z.T @ Z); N = Z @ V @ np.diag(w ** -0.5) @ V.T
            sh = np.linalg.svd(N[:3], compute_uv=False); res[nm] = (float(sh[-1]), float(sh[0] / max(sh[-1], 1e-12)))
        # 1-D knee factor: d(J3)/d(q3_ik) at fixed q1, q2 is (dJ3/dw) . (dw/dq3_ik); use the least-squares ratio on the 3 columns
        dj3 = Zc[2]; kf = float(dj3 @ dq3 / max(dq3 @ dq3, 1e-18)) if np.linalg.norm(dq3) > 1e-9 else float("nan")
        s0 = np.asarray(M.s[i], float); hs = 0.01                              # in-plane GH drift sensitivity of the J3 reading
        Kpm = D.knee(np.stack([s0 + [hs, 0, 0], s0 - [hs, 0, 0], s0 + [0, hs, 0], s0 - [0, hs, 0]]))
        ph = np.asarray(Kpm["phi"], float); gph = np.array([wrap(ph[0] - ph[1]), wrap(ph[2] - ph[3])]) / (2 * hs)
        rows.append(dict(i=int(i), kind=B.kind[i], gh_drift_twist_deg_per_mm=round(float(np.degrees(np.linalg.norm(gph))), 3), pose={k: round(B.poses[i][k], 1) for k in ("plane", "elev", "axial")},
                         state=int(np.asarray(getattr(D, "_state", np.zeros(7)))[0]) if hasattr(D, "_state") else 0,
                         dK_deg=round(float(np.degrees(c[0, 3])), 2), knee_ang=round(float(readings.ang[0]), 2), ok_all=bool(ok.all()), axis_err_deg=float(aerr.max()),
                         s8=res["8row_K_from_law"][0], c8=res["8row_K_from_law"][1], s9=res["9row_K_as_row"][0], c9=res["9row_K_as_row"][1],
                         Jh_smin=float(sJ[-1]), Jh_cond=float(sJ[0] / max(sJ[-1], 1e-12)), knee_factor=kf,
                         dK_dw=[round(float(x), 4) for x in Zc[3]]))
    if not rows: raise SystemExit("no taken poses")
    A = lambda k: np.array([r[k] for r in rows], float)
    s8, s9, js, jc, kf, ae = A("s8"), A("s9"), A("Jh_smin"), A("Jh_cond"), A("knee_factor"), A("axis_err_deg")
    w8 = rows[int(np.argmin(s8))]; wj = rows[int(np.argmin(js))]
    forced = [r for r in rows if abs(r["dK_deg"]) > 1e-6]
    out = dict(id=did, wear=wear, taken_source=src, n_taken=len(rows), taken_not_kinematic=len(not_kin), sn_vs_u3_deg=round(sn_u3, 6),
               member3_axis_err_deg_max=float(f"{ae.max():.2e}"), perturbed_not_ok=int(sum(1 for r in rows if not r["ok_all"])),
               forced_poses=len(forced),
               hubs_only_sigma_min_8row=dict(min=round(float(s8.min()), 4), p5=round(float(np.percentile(s8, 5)), 4), median=round(float(np.median(s8)), 4),
                                             cond_max=round(float(A("c8").max()), 2), worst=w8["pose"], worst_kind=w8["kind"], worst_dK=w8["dK_deg"]),
               hubs_only_sigma_min_9row=dict(min=round(float(s9.min()), 4), p5=round(float(np.percentile(s9, 5)), 4), cond_max=round(float(A("c9").max()), 2)),
               Jh=dict(sigma_min_min=round(float(js.min()), 4), sigma_min_p5=round(float(np.percentile(js, 5)), 4), cond_max=round(float(jc.max()), 2),
                       cond_p95=round(float(np.percentile(jc, 95)), 2), worst=wj["pose"], worst_dK=wj["dK_deg"]),
               knee_factor_dJ3_dq3=dict(min=round(float(np.nanmin(kf)), 4), max=round(float(np.nanmax(kf)), 4), sign_changes=bool(np.nanmin(kf) * np.nanmax(kf) <= 0)),
               forced_only=dict(n=len(forced), s8_min=round(min(r["s8"] for r in forced), 4) if forced else None,
                                Jh_cond_max=round(max(r["Jh_cond"] for r in forced), 2) if forced else None),
               knee=dict(ang_max=round(float(A("knee_ang").max()), 2), ang_min=round(float(A("knee_ang").min()), 2), window=[float(D.p["ang_min"]), round(180 - float(D.p["ang_min"]), 2)],
                         s8_min_knee_ge_145=round(float(s8[A("knee_ang") >= 145].min()), 4) if (A("knee_ang") >= 145).any() else None,
                         s8_min_knee_lt_145=round(float(s8[A("knee_ang") < 145].min()), 4) if (A("knee_ang") < 145).any() else None,
                         worst_s8_knee_ang=w8["knee_ang"], corr_s8_knee_ang=round(float(np.corrcoef(s8, A("knee_ang"))[0, 1]), 3)),
               gh_drift_twist_deg_per_mm=dict(max=round(float(A("gh_drift_twist_deg_per_mm").max()), 3), median=round(float(np.median(A("gh_drift_twist_deg_per_mm"))), 3),
                                              note="hub-only arm-twist error per mm of in-plane GH drift (the knee absorbs the drift; member 3 turns by dphi about J3, so the J3 reading moves with no arm motion)"),
               params_m_fix=P2["m_fix"], h=h, secs=round(time.time() - t0, 1),
               note="sigma_min > 0 and finite condition at every taken pose = the hub encoders (K from its law) fix every passive "
                    "coordinate and the GH rotation (GH as a ball joint; GH translation R10 is not in the model - the pins carry it)")
    if outp:
        out_full = dict(out, per_pose=rows); json.dump(out_full, open(outp, "w"), indent=1, default=float)
    print(json.dumps(out, default=float))


if __name__ == "__main__":
    main()
