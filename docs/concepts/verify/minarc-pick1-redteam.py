"""Red team of the minarc final-polish pick1 (envp-F7-g35-6) vs BDp, the open items of docs/research/minarc_final_polish.md
section 5: contact attribution on the held-out set, the clock spring at K's larger opening, the forced J1 swing and the feel.
Report: docs/research/minarc_pick1_redteam.md.

Both configs are priced like the judge (tools/env_polish.priced(): J2 stops built +0.5 read at CB_FOLD_MARGIN 5.5, K stop B at
the 5-deg rule cut) and worn through the judge's harness docs/concepts/verify/minarc-bdp-remeasure.py (imported unchanged).

    CB_EXACT=1 CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 python3 docs/concepts/verify/minarc-pick1-redteam.py attr <env|fit60> <BDp|pick1> OUT.json
        fit FAST -> frozen -> worn EXACT on the 1154 held-out poses; per held-out pose: status (not closed / knocked out /
        contact / taken) and, for every contact or near-touch (< 1 mm) pose, the signed skin distance PER PART (hub 1 / K / 2 / 3
        wall, crown, cap; links 1a / 1b / 2 underside + top; E strap, boss, pad, knee link), the body region under the deepest
        point, the K state, and the geodesic distance (deg, thorax-humerus) to the nearest daily-clip frame (all clips, held-out
        Wave / Walking included).
    CB_EXACT=1 CB_FOLD_MARGIN=5.5 LIFT='{"hub2": 2}' ... minarc-pick1-redteam.py verify <env|fit60> <held|bench> <BDp|pick1> OUT.json
        the independent verifier docs/concepts/verify/minarc-final-polish-verify.py, unchanged, with a CAD fix applied to the fit:
        LIFT adds mm to a part's fitted level (hub1 / hubK / hub2 / h3 / stack / E / L1a / L1b / L2) before the shape is frozen.
    CB_FOLD_MARGIN=5.5 OMP_NUM_THREADS=1 python3 docs/concepts/verify/minarc-pick1-redteam.py mech OUT.json
        both configs, shapes fitted on Bench(60,160): K on every clip (10 fps), spring demand along K's self-motion, strip stress,
        joint rates on the clips, the forced sub-chain's J1 / K gain on 2-deg slerp edges of the workspace grid, cuff friction
        force and the J2-stop impact (fold_stop_feel.py's method).
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial.transform import Rotation as Rot, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import env_polish as EP                                      # noqa: E402  (installs the fresh env poses before any model loads)
EB, CB, KIT = EP.EB, EP.CB, EP.KIT
D2R = math.pi / 180
PICK1 = os.path.join(REPO, "docs", "research", "minarc_final_polish", "picks", "pick1.json")
LIFT = json.loads(os.environ.get("LIFT", "{}") or "{}")


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def lifted(KR):
    """KR.KModel whose fit adds LIFT mm to the named parts' fitted levels (a CAD fix: raise that hub / strap) and refinalises"""
    base = KR.KModel

    class Lifted(base):
        def fit(self):
            base.fit(self)
            if not LIFT: return
            for k, dh in LIFT.items():
                if k in self.Hneed: self.Hneed[k] = self.Hneed[k] + float(dh)
                elif k == "E": self._HE = self._HE + float(dh)
                elif k in self.Lneed: self.Lneed[k] = [r + float(dh) for r in self.Lneed[k]]
                else: raise KeyError(k)
            self.finalize()
    return Lifted


STOPB = float(os.environ.get("STOPB_DK", "0") or 0)       # optional: K stop B moved to this opening (deg), below the priced cut


def params(R, which):
    P = R.P_bdp() if which == "BDp" else dict(R.KR.PARAMS, **{k: v for k, v in json.load(open(PICK1 if which == "pick1" else which)).items() if not k.startswith("_")})
    Pp, info = EP.priced(R.KR, P)
    if STOPB > 0:                                           # a1max whose stop B sits at dK = STOPB (closed form of the K dyad)
        b1, b2 = float(Pp["bk1"]) * D2R, float(Pp["bk2"]) * D2R; psiA = abs(float(info["psiA"])) * D2R
        a1 = math.degrees(math.acos(math.cos(b1) * math.cos(b2) + math.sin(b1) * math.sin(b2) * math.cos(psiA + STOPB * D2R)))
        if a1 < float(Pp["a1max"]): Pp["a1max"] = round(a1, 4); info["stopB_override_dK"] = STOPB; info["a1max_override"] = Pp["a1max"]
    return Pp, info


# ---------------------------------------------------------------- contact attribution
def part_samples(M):
    """{label: (member, points)}: skin-facing metal (rigid + link undersides) and the contact-only walls / crowns / tops / cap"""
    res = {}
    for nm, (mm, X) in M.rigid.items(): res[f"{nm} underside"] = (mm, X)
    for nm, (mm, X) in M.link_pts.items(): res[f"{nm} underside"] = (mm, X)
    labs = []
    for h in [h[0] for h in M._hubs()]: labs += [f"{h} wall"] * 4 + [f"{h} crown"]
    labs += [f"{nm} top" for nm, (mm, X) in M.link_pts.items() if len(X)] + ["E top", "boss wall", "boss wall", "pad wall", "pad wall", "pad top", "knee link wall", "knee top"]
    KR = sys.modules[type(M).__mro__[1].__module__] if False else None
    for j, (mm, X) in enumerate(M.contact):
        lab = "hubK cap" if type(M.contact[j]).__name__ == "_CapT" else (labs[j] if j < len(labs) else f"contact{j}")
        if lab in res: X = np.concatenate([res[lab][1], X])
        res[lab] = (mm, X)
    return res


def region(B, i, p):
    """body region under a thorax-frame point p (x anterior, y up, z right; origin GH): upper arm if it lies along the
    humerus beyond 25 mm from GH, else the torso region by position"""
    Hr = np.asarray(B.frames(i)["H"][0], float); down = Hr @ np.array([0.0, -1.0, 0.0])
    s = float(p @ down); rad = float(np.linalg.norm(p - s * down))
    if s > 25 and rad < 75: return "upper arm (deltoid / biceps / triceps)"
    x, y, z = p
    if z < -45 and y > 0: return "neck / trapezius"
    if y > 40: return "head / neck side" if z < -20 else "shoulder top (acromion)"
    if x > 25: return "chest (pectoral / anterior deltoid)"
    if x < -25: return "back (scapula)"
    if y < -40: return "side of the chest / axilla"
    return "shoulder cap"


def mode_attr(fit, which, outp):
    t0 = time.time(); assert KIT.FOLD_MARGIN == 5.5
    R = _load("rt_remeasure", os.path.join(HERE, "minarc-bdp-remeasure.py")); R.KR.KModel = lifted(R.KR)
    Pp, pinfo = params(R, which)
    FIT = EB.bench("env", exact=False) if fit == "env" else R.PV.fast_bench(60, 160); assert FIT.mode == "fast"
    if os.environ.get("WEAR") == "bench":                   # the verified protocol's wear bench Bench(110,360), exact
        W = CB.Bench(n_clip=110, n_ws=360); assert W.mode == "exact" and len(W.idx) == 470
    else: W = R.PV.held_bench(); assert len(W.idx) == 1154
    M, fitr, M1, keys = R.freeze(FIT, W, Pp, R.KR.KModel); M.run(); ex, bad, rows = R.checks_B(M, W)
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; HGall = Z["HG"].astype(float)
    clipsel = np.array([not (str(names[c]).startswith("Workspace") or str(names[c]).startswith("Envelope")) for c in cid]); HGc = HGall[clipsel]
    capmin = {i: r["cap_skin"] for i, r in rows.items()}
    D = M.D; HGw = HGall[np.asarray(W.idx)]; q, okk, X1, X2, X3, s = D.ik(HGw); st = np.asarray(D._state).copy(); dK = np.degrees(np.asarray(D._dK)).copy()
    th = np.degrees(np.arccos(np.clip((HGw @ D.u[2]) @ D.u[0], -1, 1)))
    out_pose = []; parts = part_samples(M); detail = []
    for i in range(len(W.idx)):
        r = W.res[i]; kin = bool(M.kin_ok[i])
        if r is None: status = "not closed" if not kin else ("dropped/parts" if M.why[i] else "none")
        elif i in bad: status = "knocked out"
        elif float(np.min(r)) < 0: status = "contact"
        else: status = "taken"
        low = None if r is None else min(float(np.min(r)), float(M.cmin.get(i, 1e9)), capmin.get(i, 1e9))
        out_pose.append(dict(i=i, g=int(W.idx[i]), kind=W.kind[i], plane=W.poses[i]["plane"], elev=W.poses[i]["elev"], axial=W.poses[i]["axial"],
                             status=status, why=str(M.why[i]) if M.why[i] else "", low=None if low is None else round(low, 2), state=int(st[i]), dK=round(float(abs(dK[i])), 2)))
        if r is None or not (status == "contact" or (status == "taken" and low < 1.0)): continue
        keysP = list(parts); Pw = [M.world(parts[k][0], i, parts[k][1]) for k in keysP]
        d = W.dist(i, np.concatenate(Pw)); o = 0; pm = {}; deep = None
        for k, X in zip(keysP, Pw):
            dd = d[o:o + len(X)]; j = int(np.argmin(dd)); pm[k] = round(float(dd[j]), 2)
            if deep is None or dd[j] < deep[0]: deep = (float(dd[j]), k, X[j])
            o += len(X)
        inside = sorted([(k, v) for k, v in pm.items() if v < 0], key=lambda x: x[1])
        g = Rot.from_matrix(HGc).inv() * Rot.from_matrix(np.repeat(HGw[i][None], len(HGc), 0)); gd = np.degrees(g.magnitude())
        jn = int(np.argmin(gd)); cl = np.nonzero(clipsel)[0][jn]
        detail.append(dict(i=i, kind=W.kind[i], plane=W.poses[i]["plane"], elev=W.poses[i]["elev"], axial=W.poses[i]["axial"], status=status, low=round(low, 2),
                           deepest_part=deep[1], deepest_mm=round(deep[0], 2), deepest_xyz=[round(float(x), 1) for x in deep[2]], region=region(W, i, deep[2]),
                           parts_inside=inside, parts_lt1=sorted([(k, v) for k, v in pm.items() if v < 1], key=lambda x: x[1])[:6],
                           state={0: "A", 1: "stretched", -1: "folded"}[int(st[i])], dK=round(float(abs(dK[i])), 2), th=round(float(th[i]), 1),
                           nearest_clip_deg=round(float(gd[jn]), 1), nearest_clip=str(names[cid[cl]]),
                           nearest_clip_pose=[round(float(x), 1) for x in Z["POSE"][cl][:3]]))
    fitlv = dict(f=[round(float(x), 2) for x in M.f], fK=round(float(M.fK), 2), tr=round(float(M.tr), 2))
    rep = W.report()
    out = dict(fit=fit, config=which, lift=LIFT, wear=os.environ.get("WEAR", "held"), price=pinfo, fit_report=fitr, levels=fitlv, held_report={k: rep[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
               knocked=len(bad), poses=out_pose, contact=detail, secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    con = [x for x in detail if x["status"] == "contact"]
    print(json.dumps(dict(config=which, fit=fit, wear=out["wear"], lift=LIFT, price=pinfo, levels=fitlv, held=out["held_report"], contact=len(con),
                          by_part={p: sum(1 for x in con if x["deepest_part"] == p) for p in sorted({x["deepest_part"] for x in con})},
                          by_region={p: sum(1 for x in con if x["region"] == p) for p in sorted({x["region"] for x in con})}, secs=out["secs"]), default=float), flush=True)


def mode_verify(fit, wb, which, outp):
    V = _load("rt_fpv", os.path.join(HERE, "minarc-final-polish-verify.py")); l0 = V._load

    def ld(name, path):
        m = l0(name, path)
        if path.endswith("minarc-bdp-remeasure.py"): m.KR.KModel = lifted(m.KR)
        return m
    V._load = ld
    pf = PICK1 if which == "pick1" else which
    V.main(fit, wb, pf, outp)
    d = json.load(open(outp)); d["lift"] = LIFT; json.dump(d, open(outp, "w"), indent=1, default=float)


# ---------------------------------------------------------------- mechanism: spring, speeds, swing, feel
def mech_one(R, MECH, which):
    Pp, pinfo = params(R, which)
    fitB = R.PV.fast_bench(60, 160); M1 = R.KR.KModel(fitB, dict(Pp)); M1.run(); D = M1.D
    Z = CB._poses_all(); names = list(Z["NAMES"]); cid = Z["CID"]; Q = Z["HG"].astype(float); fps = float(Z["FPS"])
    q, ok, X1, X2, X3, s = D.ik(Q); Kn = D.knee(s); ok = ok & Kn["ok"]
    st = np.asarray(D._state).copy(); dK0 = np.asarray(D._dK).copy()
    u1, u2, u3 = D.u; uK = D.uK; sp = float(np.sign(D.psiA))
    out = dict(config=which, price=pinfo, q2_stops=[round(x, 3) for x in D.q2_stops], th_hi=round(D.th_hi, 2))
    ws = cid == names.index("Workspace (envelope)"); fresh = np.array([str(names[c]).startswith("Envelope") for c in cid])
    out["dK_max_all_ok"] = round(float(np.degrees(np.abs(dK0[ok])).max()), 2); out["dK_max_ws_ok"] = round(float(np.degrees(np.abs(dK0[ok & ws])).max()), 2)
    # --- masses + spring demand along K's self-motion (buildability lens's method: MECH.kin at dK0 and dK0 + opening eps)
    mass = MECH.member_mass_model(M1); mass[7] = (mass[7][0] + 4.0, mass[7][1])
    MECH.M = R.KR.KB; eps = 0.2 * D2R

    def coms(dK):
        k = MECH.kin(D, Q, dK); Rm = {1: k["R1"], 7: k["R1"] @ k["RK"], 2: k["R12"], 3: k["R123"]}; t = {3: k["t3"]}
        return {mm: (gm, np.einsum("nij,j->ni", Rm[mm], c) + (t[mm] if mm in t else 0)) for mm, (gm, c) in mass.items() if mm in Rm}, k
    C0, k0 = coms(dK0); Cp, kp = coms(dK0 + sp * eps)
    q2err = np.degrees(np.abs(R.PK.wrap(k0["q"][:, 1] - q[:, 1])))
    grad = sum(gm * (Cp[mm][1] - C0[mm][1]) for mm, (gm, _) in Cp.items()) / eps
    tau_any = np.linalg.norm(grad, axis=1) * 9.81e-6
    dq = np.degrees(np.abs(R.PK.wrap(kp["q"] - k0["q"]))) / math.degrees(eps)
    okm = ok & (kp["g2"] > 0) & (k0["g2"] > 0) & (q2err < 0.5)
    dem = 2 * tau_any + 2e-3 * (1 + dq.sum(1))                  # 2 g any direction + 2 mN.m per sealed pair along the self-motion
    clip = ~ws & ~fresh
    out["masses_g"] = {str(m): round(g, 1) for m, (g, _) in mass.items()}
    out["demand"] = {nm: dict(n=int(sel.sum()), any_dir_2g_Nm=round(float(2 * tau_any[sel].max()), 4), demand_2g_fric2_Nm=round(float(dem[sel].max()), 4),
                              self_motion_ratio_max={j: round(float(dq[sel, k].max()), 2) for k, j in enumerate(("J1", "J2", "J3"))},
                              at_dK_max=round(float(np.degrees(np.abs(dK0[sel])).max()), 2) if sel.any() else None) if sel.any() else dict(n=0)
                     for nm, sel in (("stateA", okm & (st == 0)), ("forced", okm & (st != 0)), ("clip_frames", okm & clip), ("forced_dK_gt_34", okm & (np.degrees(np.abs(dK0)) > 34.5)))}
    # --- clips at 10 fps: K + joint rates, arm speed
    clips = {}; armmax = 0.0
    for c, nm in enumerate(names):
        if nm.startswith("Workspace") or nm.startswith("Envelope"): continue
        ii = np.nonzero(cid == c)[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
        qq_, okc, *_r = D.ik(Q[ii]); sc = _r[-1]; Kc = D.knee(sc); okc = okc & Kc["ok"]; dKc = np.degrees(np.asarray(D._dK)); stc = np.asarray(D._state)
        qq = np.c_[np.degrees(qq_[:, :3]), dKc, np.degrees(Kc["qa"]), np.degrees(Kc["qb"])]
        arm = np.degrees(np.array([np.arccos(np.clip((np.trace(Q[ii][j].T @ Q[ii][j + 1]) - 1) / 2, -1, 1)) for j in range(len(ii) - 1)])) * fps
        both = okc[:-1] & okc[1:]; armmax = max(armmax, float(arm.max()))
        rate = np.abs((np.diff(qq, axis=0) + 180) % 360 - 180)[both] * fps if both.any() else np.zeros((1, 6))
        clips[str(nm)] = dict(frames=len(ii), ok=int(okc.sum()), forced=int((okc & (stc != 0)).sum()), dK_max=round(float(np.abs(dKc[okc]).max()) if okc.any() else 0, 2),
                              arm_max_dps=round(float(arm.max()), 1), max_dps={j: round(float(rate[:, k].max()), 1) for k, j in enumerate(("J1", "J2", "J3", "K", "pin_a", "pin_b"))})
    out["clips"] = clips; out["clip_arm_max_dps"] = round(armmax, 1)
    # --- forced J1 swing: joint gain (deg joint / deg arm) on 2-deg slerp edges between neighbouring closed workspace grid poses
    POSE = Z["POSE"][ws].astype(float); HG = Q[ws]; okw = ok[ws]; stw = st[ws]
    key = {(x[0], x[1], x[2]): j for j, x in enumerate(map(tuple, POSE))}; vals = [sorted(set(POSE[:, k].tolist())) for k in range(3)]
    gains = []
    for a in np.nonzero(okw)[0]:
        x = list(POSE[a, :3])
        for dmn in range(3):
            j = vals[dmn].index(x[dmn])
            if j + 1 >= len(vals[dmn]): continue
            y = list(x); y[dmn] = vals[dmn][j + 1]; b = key.get(tuple(y))
            if b is None or not okw[b]: continue
            angd = np.degrees((Rot.from_matrix(HG[a]).inv() * Rot.from_matrix(HG[b])).magnitude()); n = max(2, int(math.ceil(angd / 2.0)) + 1)
            Qs = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()
            qs, oks, *_r = D.ik(Qs); dks = np.degrees(np.asarray(D._dK)); sts = np.asarray(D._state)
            if not oks.all(): continue
            dqs = np.abs((np.diff(np.c_[np.degrees(qs[:, :3]), dks], axis=0) + 180) % 360 - 180)
            darm = np.degrees(np.array([np.arccos(np.clip((np.trace(Qs[k].T @ Qs[k + 1]) - 1) / 2, -1, 1)) for k in range(n - 1)]))
            g = dqs / np.maximum(darm, 1e-6)[:, None]
            gains.append((int(sts.max() != 0 or sts.min() != 0), float(g[:, 0].max()), float(g[:, 3].max()), float(g[:, 1].max()), float(g[:, 2].max()), POSE[a, :3].tolist(), y))
    G = np.array([g[:5] for g in gains]) if gains else np.zeros((0, 5))
    sw = {}
    for nm, sel in (("stateA_edges", G[:, 0] == 0), ("forced_edges", G[:, 0] == 1)):
        if not sel.any(): sw[nm] = dict(n=0); continue
        sw[nm] = dict(n=int(sel.sum()), J1_gain_max=round(float(G[sel, 1].max()), 2), J1_gain_p95=round(float(np.percentile(G[sel, 1], 95)), 2),
                      K_gain_max=round(float(G[sel, 2].max()), 2), K_gain_p95=round(float(np.percentile(G[sel, 2], 95)), 2),
                      J3_gain_max=round(float(G[sel, 4].max()), 2),
                      J1_dps_at_clip_arm_max=round(float(G[sel, 1].max()) * armmax, 0), J1_deg_per_frame_at_clip_arm_max=round(float(G[sel, 1].max()) * armmax / fps, 1))
    worst = sorted(gains, key=lambda g: -g[1])[:5]
    sw["worst_J1_edges"] = [dict(forced=g[0], J1_gain=round(g[1], 2), K_gain=round(g[2], 2), a=g[5], b=g[6]) for g in worst]
    out["swing"] = sw
    # --- feel: cuff friction force (Coulomb T per moving joint + spring torque on K in the forced states) and the J2-stop impact
    T = 3.0e-3; rpad = float(np.linalg.norm(M1.fr["Bm"])) if hasattr(M1, "fr") and "Bm" in M1.fr else 120.0
    X1b = np.asarray(D._X1b[0]) if False else None
    q, ok2, X1, X2, X3, s = D.ik(Q); X1b = np.asarray(D._X1b[0]); st = np.asarray(D._state); dK0 = np.asarray(D._dK)
    a1w = np.broadcast_to(u1, (len(Q), 3)); aK = np.einsum("nij,j->ni", X1[0], uK); a2 = np.einsum("nij,j->ni", X1b, u2); a3 = np.einsum("nij,j->ni", X2[0], u3)
    def cuff(sel, kspring):
        F = []
        for i in np.nonzero(sel)[0]:
            if st[i] == 0: A = np.c_[a1w[i], a2[i], a3[i]]; extra = np.zeros(3)
            else: A = np.c_[a1w[i], aK[i], a3[i]]; extra = np.array([0, kspring[0] + kspring[1] * abs(dK0[i]), 0])
            if abs(np.linalg.det(A)) < 1e-6: continue
            Ai = np.linalg.inv(A); best = 0
            for sg in np.array(np.meshgrid([-1, 1], [-1, 1], [-1, 1])).T.reshape(-1, 3):
                f = T * sg + extra * (1 if st[i] == 0 else np.sign(sg[1]) * 0 + 1)
                tau = Ai.T @ f; best = max(best, float(np.linalg.norm(tau)))
            F.append((best / (rpad * 1e-3), float(np.linalg.norm(Ai, 2)), i))
        return F
    feel = dict(T_joint_Nm=T, r_pad_mm=round(rpad, 1))
    for nm, sel in (("stateA", ok2 & (st == 0)), ("forced", ok2 & (st != 0))):
        F = cuff(sel, (0.08, 0.015))
        if not F: feel[nm] = dict(n=0); continue
        f = np.array([x[0] for x in F]); g = np.array([x[1] for x in F])
        feel[nm] = dict(n=len(F), cuff_force_N_max=round(float(f.max()), 2), cuff_force_N_p95=round(float(np.percentile(f, 95)), 2), cuff_force_N_median=round(float(np.median(f)), 2),
                        transmission_norm_max=round(float(g.max()), 2))
    # stop impact: state-A rates vs J2-locked rates at the stretched-stop boundary, at the clip arm max speed, Carnot loss
    cen = {m: (gm, c) for m, (gm, c) in mass.items()}
    def inertia(m, i):
        gm, c = cen[m]; Rm = {1: X1[0][i], 7: X1b[i], 2: X2[0][i]}[m]; cw = Rm @ c * 1e-3
        return gm * 1e-3 * (float(cw @ cw) * np.eye(3) - np.outer(cw, cw)) + gm * 1e-3 * (0.01 ** 2) / 6 * np.eye(3)
    near = np.nonzero(ok2 & (st != 0) & (np.degrees(np.abs(dK0)) < 1.5))[0]
    E = []
    wmag = armmax * D2R
    for i in near:
        AA = np.c_[a1w[i], a2[i], a3[i]]; AF = np.c_[a1w[i], aK[i], a3[i]]
        if abs(np.linalg.det(AA)) < 1e-6 or abs(np.linalg.det(AF)) < 1e-6: continue
        best = 0
        for wd in np.eye(3).tolist() + [list(x) for x in Rot.random(24, random_state=1).apply([1, 0, 0])]:
            w = np.asarray(wd) * wmag; rA = np.linalg.solve(AA, w); rF = np.linalg.solve(AF, w)
            wA = {1: rA[0] * a1w[i], 7: rA[0] * a1w[i], 2: rA[0] * a1w[i] + rA[1] * a2[i]}
            wF = {1: rF[0] * a1w[i], 7: rF[0] * a1w[i] + rF[1] * aK[i], 2: rF[0] * a1w[i] + rF[1] * aK[i]}
            e = sum(0.5 * float((wF[m] - wA[m]) @ inertia(m, i) @ (wF[m] - wA[m])) for m in (1, 7, 2) if m in cen)
            best = max(best, e)
        E.append(best)
    feel["stop_impact"] = dict(n_boundary_poses=len(E), arm_speed_dps=round(armmax, 1), energy_mJ_max=round(1e3 * max(E), 3) if E else None,
                               energy_mJ_median=round(1e3 * float(np.median(E)), 3) if E else None)
    out["feel"] = feel
    return out


def mode_mech(outp):
    assert KIT.FOLD_MARGIN == 5.5
    R = _load("rt_remeasure_m", os.path.join(HERE, "minarc-bdp-remeasure.py"))
    MECH = _load("rt_mech", os.path.join(HERE, "minarc-stop-knuckle-4r-mechanism.py"))
    out = {w: mech_one(R, MECH, w) for w in ("BDp", "pick1")}
    # strip stress: 0.3 x 5 mm 1.4310, sigma = 6 M / (b t^2), M = preload + k dK; strip length L = EI / k
    b, t, E = 5.0, 0.3, 193e3; EI = E * b * t ** 3 / 12 * 1e-6
    tab = []
    for k in (0.005, 0.0075, 0.010, 0.015, 0.020, 0.030):
        for pre in (0.06, 0.08):
            row = dict(rate=k, preload=pre, L_mm=round(EI / k * 1e3, 0), turns_preload=round(pre / k / (2 * math.pi), 2))
            for lab, dk in (("BDp stop B 34.47", 34.47), ("pick1 max 56.55", 56.55), ("pick1 stop B 56.65", 56.65), ("pick1 as-designed stop B 60.42", 60.42)):
                M_ = pre + k * dk * D2R; row[lab] = dict(M_Nm=round(M_, 4), sigma_MPa=round(6 * M_ * 1e3 / (b * t * t), 0))
            tab.append(row)
    out["strip"] = dict(t_b_mm=[t, b], EI_Nm2=round(EI, 6), limits_MPa={"+C1700 0.7-0.8 Rm": [1190, 1360], "+C1900 0.7-0.8 Rm": [1330, 1520]}, table=tab,
                        annulus_O16_O5_mm2=round(math.pi / 4 * (16 ** 2 - 5 ** 2), 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    for w in ("BDp", "pick1"):
        o = out[w]; print(w, json.dumps(dict(dK=o["dK_max_ws_ok"], demand=o["demand"], swing={k: v for k, v in o["swing"].items() if k != "worst_J1_edges"}, feel=o["feel"],
                                              clipK={c: (v["dK_max"], v["max_dps"]) for c, v in o["clips"].items()}), default=float), flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "attr": mode_attr(a[1], a[2], a[3])
    elif a and a[0] == "verify": mode_verify(a[1], a[2], a[3], a[4])
    elif a and a[0] == "mech": mode_mech(a[1])
    else: raise SystemExit(__doc__)
