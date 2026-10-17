"""Independent verifier (skeptic) of slipper-nose-knuckle-3r (the lead roller-longdyad-knuckle-3r with its MR63ZZ flank
roller deleted: a pressed, hardened O2.37 nose on the crank's bent long arm SLIDES on a conjugate flank re-cut for the
nose radius; friction enters the pressure-angle budget as PA_kin <= 43 - atan(mu), mu 0.087).

The claim's model (docs/concepts/models/slipper-nose-knuckle-3r.py, SN_CELL=lead) is loaded UNCHANGED. This harness
re-uses the lead's verifier (docs/concepts/verify/roller-longdyad-knuckle-3r.py = the round's roller-flank verifier
docs/concepts/verify/sidecar-roller-flank-knuckle-3r.py + the own-state th margin): frozen protocol fit Bench(60,160)
fast -> shape frozen -> worn on Bench(110,360) exact / held out; cam closure in the world, nose vs lug, K sense,
pressure angles at each taken pose, real lobe pressure angle, drive-idle rule, th margin, continuity flood - retargeted
at the claim's model class, clamp, params, best config and NOSE RADIUS (the parent harness hard-codes the roller's 3 mm).
It ADDS, for the sliding nose:

  N1. PRESSURE ANGLE WITH FRICTION at every taken pose: kinematic PA (crank and horn, the claim's per-0.25-deg table read
      at the pose's |dK|) + atan(mu) <= 43 (the claim's own rule) and <= 45 (the judge's gate);
  N2. CONJUGATE VALIDITY (undercut / interference): every synthesised flank contact point Q(k) over the used stroke must
      stay >= nose_r - 0.02 mm from the nose centre at EVERY other K step (else the nose cuts that flank point away at
      another K, the flank the model scores does not exist there, and K is not determined at that pose). The parent
      deletes lug samples within ROLL_R + 0.3 of the centre path, which would hide an undercut; this reads the flank itself.
  N3. RELATIVE POLE: the nose centre's sliding speed |v_C - v_H| per unit |dK| over the taken stroke (0 = the nose sits on
      the crank / link-1a relative pole, where the contact normal and both pressure angles are undefined), and the
      flank's smallest radius (concave pocket vs the nose radius) with its K.
  N4. CATALOGUE NOSE: the shape re-worn with the stock ISO 8734 dowel radii (O2.5 r 1.25, O2 r 1.0) and at mu 0.12
      (--set nose_r=1.25 etc.; the flank is re-cut for the nose by the claim's own synthesis, drive params unchanged).
  --edge: envelope correction without a head (a pressed dowel has none): the lug's flank-edge strip that the parent
      sampling deletes, re-added at nose_r + 0.1 from the nose-centre path.

    SN_CELL=lead CB_EXACT=1 python3 docs/concepts/verify/slipper-nose-knuckle-3r.py wear <bench|held> <out.json> [--flood] [--edge] [--set k=v ...]
    SN_CELL=lead python3 docs/concepts/verify/slipper-nose-knuckle-3r.py cam [--set k=v ...]      (fit bench only: N2 / N3)
"""
import importlib.util, json, math, os, sys, time, types
import numpy as np
from scipy.spatial import cKDTree

os.environ.setdefault("SN_CELL", "lead")
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


LV = _load("rl_verifier_for_slipper_v", os.path.join(HERE, "roller-longdyad-knuckle-3r.py"))      # the lead's verifier (+ H)
H = LV.H
SN = _load("slipper_claim_v", os.path.join(REPO, "docs", "concepts", "models", "slipper-nose-knuckle-3r.py"))   # loaded LAST
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "slipper-nose-knuckle-3r.json")))
BEST = ROW["best_params"]
if isinstance(BEST, str): BEST = json.loads(BEST)


def retarget(P):
    nr = float(SN._clamp(dict(SN.PARAMS, **P))["nose_r"])
    H.RF = types.SimpleNamespace(phi_of=SN.RF.phi_of, dphi_of=SN.RF.dphi_of, ROLL_R=nr, _ring=SN.RF._ring,
                                 RFModel=SN.SNModel, _clamp=SN._clamp, PARAMS=SN.PARAMS)
    H.SC, H.S, H.PK = SN.SC, SN.S, SN.PK
    H.ROLL_R = nr; H.BEST = dict(P)
    return nr


def nose_checks(Mfit, kmax_deg, nr):
    """N2 / N3 on the fitted (frozen) cam over [0, min(kmax_taken, dK_lim)]"""
    g = Mfit._scg; tab = Mfit._cam_table
    PV, dR, uK, sp, sig, gg, cc = g["PV"], g["dR"], g["uK"], g["sp"], g["sig"], g["g"], g.get("c", 0.0)
    C0 = np.asarray(Mfit._viz_rod["roller"], float)
    kgrid = np.radians(np.arange(0.0, min(kmax_deg, math.degrees(g["dK_lim"])) + 1e-9, 0.05))
    Rk = H.S.rotm(uK, sp * kgrid); Rcg = H.S.rotm(dR, sig * SN.RF.phi_of(kgrid, gg, cc))
    Cg = np.einsum("nij,j->ni", Rcg, C0 - PV) + PV
    vr_n, Ns = [], []; nprev = None
    for j in range(len(kgrid)):
        C = Cg[j]; vC = sig * float(SN.RF.dphi_of(kgrid[j], gg, cc)) * np.cross(dR, C); vh = -sp * np.cross(uK, C); vr = vC - vh
        vr_n.append(float(np.linalg.norm(vr)))
        n = np.cross(H.S.unit(C), vr); nn = float(np.linalg.norm(n)); n = n / nn if nn > 1e-12 else nprev
        if nprev is None: n = n if float(n @ vh) >= 0 else -n
        else: n = n if float(n @ nprev) >= 0 else -n
        nprev = n; Ns.append(n)
    Ns = np.array(Ns); P1 = np.einsum("nij,nj->ni", Rk, Cg); N1 = np.einsum("nij,nj->ni", Rk, Ns); Q1 = P1 + nr * N1
    # N2: every flank point vs every nose-centre position (spherical cam: distances in 3D, the nose is a radial cylinder,
    # so the in-shell distance of the centre path to the flank point is what the nose covers)
    tree = cKDTree(P1); d, jj = tree.query(Q1, k=1)
    pen = nr - d                                                   # > 0: the nose at step jj[i] covers flank point i
    ibad = np.nonzero(pen > 0.02)[0]
    k_tab = np.asarray(tab["k"]); fr = np.asarray(tab["flank_rho"]); lim_j = int(np.searchsorted(k_tab, min(kmax_deg, math.degrees(g["dK_lim"]))))
    jr = int(np.argmin(np.abs(fr[: lim_j + 1])))
    return dict(nose_r=nr, n_steps=len(kgrid), k_range_deg=round(math.degrees(float(kgrid[-1])), 2),
                undercut_points=int(len(ibad)), undercut_max_mm=round(float(pen.max()), 4) if len(pen) else None,
                undercut_k_deg=[round(math.degrees(float(kgrid[i])), 2) for i in ibad[:20]],
                vrel_min_mm_per_rad=round(float(min(vr_n)), 3), vrel_min_k_deg=round(math.degrees(float(kgrid[int(np.argmin(vr_n))])), 2),
                vrel_at_0=round(vr_n[0], 3), vrel_at_end=round(vr_n[-1], 3),
                flank_rho_min_mm=round(float(np.abs(fr[: lim_j + 1]).min()), 3), flank_rho_min_k_deg=round(float(k_tab[jr]), 2),
                path_len_mm=round(float(np.sum(np.linalg.norm(np.diff(P1, axis=0), axis=1))), 2),
                flank_len_mm=round(float(np.sum(np.linalg.norm(np.diff(Q1, axis=0), axis=1))), 2))


_extra0 = LV._extra0               # the roller-flank verifier base checks (closure, nose vs lug, sense, PA, lobe, idle)


def extra_checks(M, Mfit, B):
    P = Mfit.D.p; mu = float(P.get("mu", 0.05)); fr = math.degrees(math.atan(mu)); nr = float(P.get("nose_r", 1.5))
    H.ROLL_R = nr
    H.PA_MAX = 43.0 - fr                                            # N1, the claim's rule: kinematic PA + friction <= 43
    try: out = _extra0(M, Mfit, B)
    finally: H.PA_MAX = 43.0
    out["pa_rule"] = dict(mu=mu, friction_deg=round(fr, 2), cap_kin=round(43.0 - fr, 2),
                          pa_eff_horn_max=round(out["pa_horn_max"] + fr, 2) if out.get("pa_horn_max") is not None else None,
                          pa_eff_crank_max=round(out["pa_crank_max"] + fr, 2) if out.get("pa_crank_max") is not None else None)
    H.PA_MAX = 45.0 - fr                                            # N1 at the judge's 45 gate
    try: out["at_pa45_friction"] = {k: _extra0(M, Mfit, B)[k] for k in ("poses_failing", "why_failing", "corrected")}
    finally: H.PA_MAX = 43.0
    try: out["th_margin"] = LV.th_margin(M, B)
    except Exception as e: out["th_margin"] = dict(error=repr(e)[:300])
    try: out["nose"] = nose_checks(Mfit, float(out.get("dK_taken_max_deg") or 0.0), nr)
    except Exception as e: out["nose"] = dict(error=repr(e)[:300])
    out["cam_claim"] = {k: (getattr(Mfit, "_sc_info", None) or {}).get(k) for k in ("dK_lim", "why_lim", "pa_crank_max_taken", "pa_horn_max_taken",
                                                                                     "pa_eff_horn", "pa_eff_crank", "pa_kin_max", "flank_rho_min",
                                                                                     "clear_hubK_min", "clear_roll_hubK_min", "nose_r", "mu")}
    return out


def add_edge(M):
    """envelope correction for a headless dowel nose: the lug's flank-edge strip (the parent deletes every lug sample within
    ROLL_R + 0.3 of the centre path, so the sampled lug starts behind the flank); re-added at nose_r + 0.1 from the path"""
    nr = float(H.ROLL_R); C0 = np.asarray(M._viz_rod["roller"], float); Pp = H.flank_path(M); R0 = float(np.linalg.norm(C0)); rL = R0 - 1.5
    m1, lug = M.rigid["horn"]; mid = lug + 1.5 * H.S.unit(lug); d, j = cKDTree(Pp).query(mid)
    sel = d < nr + 2.6
    E = Pp[j[sel]] + (nr + 0.1) * H.S.unit(mid[sel] - Pp[j[sel]])
    E = E[cKDTree(Pp).query(E)[0] >= nr + 0.05]
    edge = H.S.unit(E) * rL
    M.rigid["horn"] = (m1, np.concatenate([lug, edge]))
    M.contact.append((1, edge + H.S.T_LINK * H.S.unit(edge)))
    M._env_info = dict(head_pts=0, edge_pts=len(edge))


H.extra_checks = extra_checks
H.add_envelope = add_edge


def _params(argv):
    P = dict(BEST)
    for a in argv:
        if a.startswith("--set="): a = a[6:]
        else: continue
        k, v = a.split("=", 1); P[k] = float(v)
    return P


if __name__ == "__main__":
    # both spellings: '--set=k=v' and the docstring's '--set k=v' (alignment skeptic 2026-10-17 16:25: the spaced form was
    # silently ignored and the run measured the nominal config; arg parsing only, no measurement changes)
    sets = [a for a in sys.argv if a.startswith("--set=")] + ["--set=" + sys.argv[i + 1] for i, a in enumerate(sys.argv[:-1]) if a == "--set"]
    P = _params(sets); nr = retarget(P)
    if sys.argv[1] == "cam":
        old = os.environ.pop("CB_EXACT", None)
        B1 = CB.Bench(n_clip=60, n_ws=160); t = time.time()
        M1 = SN.SNModel(B1, SN._clamp(dict(SN.PARAMS, **P))); r1 = M1.run()
        ex = extra_checks(M1, M1, B1)
        print(json.dumps(dict(params=P, fit={k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
                              why=r1.get("why"), extra=ex, secs=round(time.time() - t, 1)), default=float)); sys.exit()
    if sys.argv[1] == "wear":
        wear, path = sys.argv[2], sys.argv[3]
        t = time.time(); out = H.frozen_wear(dict(P), wear, "--flood" in sys.argv, "--edge" in sys.argv)
        out.update(wear=wear, secs=round(time.time() - t, 1), exact=os.environ.get("CB_EXACT") == "1", params=P, sets=sets)
        json.dump(out, open(path, "w"), indent=1, default=float)
        print(json.dumps(dict(wear=wear, sets=sets, edge=out["head"], fit=out["fit_fast"], frozen=out["frozen"], near1=out["audit"].get("gap_near1"),
                              near2=out["audit"].get("gap_near2"), minmetal=out["audit"].get("near_touch_min_mm"), ovh=out["audit"].get("overhead140"),
                              why=out["why"], extra=out["extra"], conn=out.get("connected"), env=out.get("env"), secs=out["secs"]), default=float))
