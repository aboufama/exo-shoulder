"""Knee-window singularity check for minarc-stop-knuckle-4r BDp vs the pin knee H1 (docs/research/knee-window-check.md).

The pin-knee GPU polish's held-out gain came entirely from a narrower knee window (ang_min 30.46 -> 21.93). BDp carries
ang_min 24.95. This script measures, with the verified BDp claim harness (docs/concepts/models/minarc-stop-knuckle-4r-kitrule-wear.py,
which imports the re-measure verifier docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.py UNCHANGED):

  wear <bench|held> <BDp|BDp30|H1> out.json [--conn conn.json]
        the harness' own wear() (fit Bench(60,160) fast -> frozen -> worn on Bench(110,360) / the held-out bench, CB_EXACT=1,
        CB_FOLD_MARGIN = the margin), with ONE addition: the extra checks also record, per wear pose, the knee's interior
        angle at pin a (ang; 180 = straight, 0 = folded: the planar RRR's two singular postures), J3's lever on the knee
        force dist(C, ab) = lE sin(ang), and GH's lever dist(GH', ab). Nothing else changes (the taken set is the harness').
        BDp = docs/concepts/verify/minarc-kitrule/params_floorBD5_phys_cap6.json; BDp30 = the same with ang_min 30.4611 (H1's);
        H1 = the verified H1 through the harness' H1 path.
  conn <BDp|BDp30|H1> out.json      the harness' continuity flood fill (fit60) for that config.
  stats out.json ...                 knee-angle statistics over the TAKEN (and connected) poses of wear outputs.
  feel  <BDp|H1> <wear_bench.json> out.json
        quasi-static Jacobian feel of the knee near its straight posture (the method of docs/research/fold_stop_feel.py):
        the six fit clips at 10 fps through the frozen design (m from the wear run), finite-difference joint rates,
        Coulomb torque T per O20 joint and per knee pin -> cuff force from the dissipated power; per pose the planar
        dyad's amplification 1/sin(ang) (pin rate per unit drift speed, x 1/l), J3's lever lE sin(ang), the knee force per
        unit J3 torque, the friction-circle jam test and the toggle (branch) test.

    OMP_NUM_THREADS=1 CB_EXACT=1 CB_FOLD_MARGIN=5 python3 docs/research/knee_window_check.py wear bench BDp30 out.json --conn conn.json
"""
import importlib.util, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, os.path.join(REPO, path)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


KW = _load("kitrule_wear_kw", "docs/concepts/models/minarc-stop-knuckle-4r-kitrule-wear.py")
VER = KW.VER
BDP = json.load(open(os.path.join(REPO, "docs/concepts/verify/minarc-kitrule/params_floorBD5_phys_cap6.json")))
H1_ANG_MIN = 30.4611


def config(name):
    if name == "H1": return "H1", None
    P = dict(BDP)
    if name == "BDp30": P["ang_min"] = H1_ANG_MIN
    elif name != "BDp": raise SystemExit(f"unknown config {name}")
    return "B", P


def knee_pose_data(M):
    """per wear pose: knee interior angle at pin a, J3's lever dist(C, ab), GH's lever dist(GH', ab) (plane coords rel. c3)"""
    D = M.D; K = M.K; s = np.asarray(M.s, float); C2 = s[:, :2]; pa = np.asarray(K["pa"], float); B2 = np.asarray(K["B2"], float)
    c3 = np.asarray(D.c[2], float); GH = np.array([-(c3 @ D.sa), -(c3 @ D.st)])
    e = B2[None] - pa; e = e / (np.linalg.norm(e, axis=1, keepdims=True) + 1e-12)
    def dist(X): w = X - pa; return np.abs(w[:, 0] * e[:, 1] - w[:, 1] * e[:, 0])
    return dict(ang=[round(float(x), 3) for x in K["ang"]], hC=[round(float(x), 3) for x in dist(C2)],
                hGH=[round(float(x), 3) for x in dist(np.broadcast_to(GH, C2.shape))], ang_min=float(M.p["ang_min"]),
                lE=float(M.p["lE"]), lc=float(M.p["lc"]), br=float(K["br"]))


_ckB = VER.extra_checks_B
def _ckB_knee(M, B):
    out, bad = _ckB(M, B); out["knee_window_check"] = knee_pose_data(M); return out, bad


_ckH = VER.V.extra_checks
def _ckH_knee(M, B):
    out, bad = _ckH(M, B); out["knee_window_check"] = knee_pose_data(M); return out, bad


VER.extra_checks_B = _ckB_knee
VER.V.extra_checks = _ckH_knee


# ---------------- statistics over taken poses ----------------
def stats(path):
    d = json.load(open(path)); kw = d["extra"]["knee_window_check"]; ang = np.array(kw["ang"]); hC = np.array(kw["hC"]); hGH = np.array(kw["hGH"])
    taken = np.array(d["taken"], bool)
    con = d.get("connected") or {}
    dropped = {(x["plane"], x["elev"], x["axial"]) for x in con.get("dropped", [])}
    keys = [tuple(k) for k in d["pose_key"]]
    tk = np.array([taken[i] and not (d["kind"][i] == "ws" and keys[i] in dropped) for i in range(len(taken))], bool)
    a = ang[tk]; amin = kw["ang_min"]; edge = 180 - amin
    f = d.get("connected") or d["corrected"]
    return dict(file=os.path.relpath(path, REPO), design=d["design"], wear=d["wear_bench"], margin=d["fold_margin"],
                ang_min=amin, lE=kw["lE"], lc=kw["lc"], gap=f["gap"], fit_gap=d["fit"]["gap"], reach=f["reach"], inband14=f["inband14"],
                contact=f["contact"], follow=f["follow"], gap_near1=f.get("gap_near1"), dropped_unconnected=con.get("dropped_unconnected"),
                taken=int(tk.sum()), ang_range=[round(float(a.min()), 2), round(float(a.max()), 2)],
                to_straight_min=round(float((180 - a).min()), 2), to_folded_min=round(float(a.min()), 2),
                at_edge_le1=int((a > edge - 1).sum()), at_edge_le3=int((a > edge - 3).sum()),
                beyond_H1_window=int((a > 180 - H1_ANG_MIN).sum()), beyond_H1_window_ws=int(sum(1 for i in np.nonzero(tk)[0] if d["kind"][i] == "ws" and ang[i] > 180 - H1_ANG_MIN)),
                beyond_H1_window_clip=int(sum(1 for i in np.nonzero(tk)[0] if d["kind"][i] == "clip" and ang[i] > 180 - H1_ANG_MIN)),
                amp_max=round(float((1 / np.sin(np.radians(a))).max()), 3), hC_min=round(float(hC[tk].min()), 2),
                ratio_GH_C=[round(float((hGH[tk] / hC[tk]).min()), 3), round(float((hGH[tk] / hC[tk]).max()), 3)],
                why=d["why"], score=d.get("score"))


# ---------------- feel ----------------
T_J = 3.0; T_PIN = 3.0          # N.mm per O20 joint (preloaded MR117-2RS pair) and per knee pin, as fold_stop_feel.py
MU_PIN, R_PIN = 0.25, 2.0       # iglidur sleeve on the O4 Ti pin (worst dry mu), radius mm -> friction circle mu r
MU_BRG, R_BRG = 0.005, 3.5      # MR117 ball pair on the O7 pin: J3's friction circle


def design_of(name, wear_json):
    W = json.load(open(wear_json)); which, P = config(name)
    if which == "H1":
        D = VER.MK.Design(dict(W["params"])); D.isB = False
    else:
        D = VER.KB.KDesign(dict(W["params"])); D.isB = True
    D.m = np.array(W["m"], float); D.m[2] = 0.0; D.tr = float(W["tr"])
    p = D.p; pe, pb = p["phiE"] * math.pi / 180, p["phib"] * math.pi / 180
    A0 = D.m[:2] + float(p["lE"]) * np.array([math.cos(pe), math.sin(pe)]); B2 = A0 + float(p["lc"]) * np.array([math.cos(pb), math.sin(pb)])
    D.r_cuff = float(np.linalg.norm(D.p3(B2, D.tr)[0]))
    return D, W


def wrap(a): return (a + np.pi) % (2 * np.pi) - np.pi


def kin_angles(D, W):
    """knee angle per wear pose: the in-harness record when present, else re-computed from the frozen design (ik + knee on the
    wear poses W["idx"]; the same closed forms the harness runs)"""
    kw = (W.get("extra") or {}).get("knee_window_check")
    if kw: return np.array(kw["ang"], float)
    Z = VER.CB._poses_all(); _, _, _, _, _, s = D.ik(Z["HG"][np.array(W["idx"])].astype(float)); return np.asarray(D.knee(s)["ang"], float)


def kinstats(name, wear_json):
    """knee angle over the taken poses of a stored wear run (no knee record needed)"""
    D, W = design_of(name, wear_json); ang = kin_angles(D, W); tk = np.array(W["taken"], bool); a = ang[tk]; amin = float(D.p["ang_min"])
    return dict(file=os.path.relpath(wear_json, REPO), design=name, taken=int(tk.sum()), ang_range=[round(float(a.min()), 2), round(float(a.max()), 2)],
                to_straight_min=round(float((180 - a).min()), 2), at_edge_le1=int((a > 180 - amin - 1).sum()), beyond_H1_window=int((a > 180 - H1_ANG_MIN).sum()))


def feel(name, wear_json, outp):
    from scipy.spatial.transform import Rotation as Rot
    CB = VER.CB; Z = CB._poses_all(); NAMES = list(Z["NAMES"]); CID = Z["CID"]; DT = 1.0 / float(Z["FPS"])
    D, W = design_of(name, wear_json); R_tol = float(D.p["R_tol"]); lE, lc, amin = float(D.p["lE"]), float(D.p["lc"]), float(D.p["ang_min"])
    rows = []; flips = 0; frames = 0; taken = 0
    for nm in CB.FIT:
        ii = np.nonzero(CID == NAMES.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]; Q = Z["HG"][ii].astype(float)
        q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s); ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol); frames += len(ii); taken += int(ok.sum())
        st = D._state.copy() if D.isB else np.zeros(len(ii), int); dK = D._dK.copy() if D.isB else np.zeros(len(ii))
        u1, u2, u3 = D.u; R1, R2 = X1[0], X2[0]; a1 = np.broadcast_to(u1, (len(ii), 3)); a3 = R2 @ u3
        a2 = (D._X1b[0] @ u2) if D.isB else (R1 @ u2); aK = (R1 @ D.uK) if D.isB else None
        q3p = q[:, 2] + K["phi"]; qq = np.c_[q[:, 0], q[:, 1], q3p, dK, K["qa"], K["qb"]]
        C2 = s[:, :2]; aa = C2 - K["pa"]; bb = K["B2"][None] - K["pa"]; sgn = np.sign(aa[:, 0] * bb[:, 1] - aa[:, 1] * bb[:, 0])
        for k in range(len(ii) - 1):
            if not (ok[k] and ok[k + 1]): continue
            if sgn[k] != sgn[k + 1]: flips += 1
            dq = wrap(qq[k + 1] - qq[k]); rv = Rot.from_matrix(Q[k + 1] @ Q[k].T).as_rotvec(); dth = float(np.linalg.norm(rv))
            if dth < 1e-6: continue
            forced = D.isB and (st[k] != 0 or st[k + 1] != 0)
            A = np.stack([a1[k], aK[k], a3[k]], 1) if forced else np.stack([a1[k], a2[k], a3[k]], 1)
            sg = np.sign(dq[[0, 3, 2]] if forced else dq[[0, 1, 2]]); sg[sg == 0] = 1
            tau = np.linalg.solve(A.T, T_J * sg)
            knee_P = T_PIN * (abs(dq[4]) + abs(dq[5])) / dth                                   # the two knee pins (J3' is in tau)
            ds = float(np.linalg.norm(s[k + 1, :2] - s[k, :2]))                                 # drift step, mm
            ang = float(max(K["ang"][k], K["ang"][k + 1]))
            rows.append(dict(clip=nm, k=int(k), ang=ang, to_straight=180 - ang, arm_dps=dth / DT * 180 / math.pi,
                             drift_mm_per_rad=ds / dth, pins_rate_per_arm=(abs(dq[4]) + abs(dq[5])) / dth,
                             F_sph=float(np.linalg.norm(tau)) / D.r_cuff, F_knee=knee_P / D.r_cuff,
                             F_total=(float(np.linalg.norm(tau)) + knee_P) / D.r_cuff, forced=bool(forced)))
    def pk(key, filt=lambda r: True):
        v = np.array([r[key] for r in rows if filt(r)])
        return dict(max=round(float(v.max()), 3), p99=round(float(np.percentile(v, 99)), 3), median=round(float(np.median(v)), 3), n=int(len(v))) if len(v) else None
    near = lambda r: r["to_straight"] < 35.0
    far = lambda r: r["to_straight"] >= 35.0
    # per-pose dyad Jacobian over the worn bench's taken poses (from the wear run's in-harness knee data)
    ang = kin_angles(D, W); tk = np.array(W["taken"], bool); a = ang[tk]
    sa = np.sin(np.radians(a)); hC = lE * sa
    edge = 180 - amin; sedge = math.sin(math.radians(amin))
    jam = dict(rho_J3_mm=round(MU_BRG * R_BRG, 4), rho_pin_mm=round(MU_PIN * R_PIN, 3), hC_min_mm=round(float(hC.min()), 2),
               hC_at_edge_mm=round(lE * sedge, 2),
               jam_needs_to_straight_deg=round(math.degrees(math.asin(min(1.0, (2 * MU_PIN * R_PIN + MU_BRG * R_BRG) / lE))), 3),
               note="a two-force knee link with friction circles rho at its pins jams J3 only if its force line passes within "
                    "rho_J3 + 2 rho_pin of J3's centre, i.e. lE sin(ang) < that sum")
    out = dict(design=name, wear_json=os.path.relpath(wear_json, REPO), T_joint_Nmm=T_J, T_pin_Nmm=T_PIN, r_cuff_mm=round(D.r_cuff, 1),
               lE=lE, lc=lc, ang_min=amin, knee_edge_deg=round(edge, 2), clip_frames=frames, clip_taken=taken, clip_pairs=len(rows),
               clip_knee_branch_flips=flips,
               clip_ang=[round(min(r["ang"] for r in rows), 2), round(max(r["ang"] for r in rows), 2)] if rows else None,
               clip_to_straight_min=round(min(r["to_straight"] for r in rows), 2) if rows else None,
               F_total=pk("F_total"), F_knee=pk("F_knee"), F_sph=pk("F_sph"), F_knee_near_straight_lt35=pk("F_knee", near), F_knee_far=pk("F_knee", far),
               pins_rate_per_arm=pk("pins_rate_per_arm"), pins_rate_near_lt35=pk("pins_rate_per_arm", near), drift_mm_per_rad=pk("drift_mm_per_rad"),
               F_knee_edge_bound=round(T_PIN * max(r["drift_mm_per_rad"] for r in rows) * (2 / lc + 1 / lE) / sedge / D.r_cuff, 3) if rows else None,
               F_knee_edge_bound_note="worst-case knee-pin friction force at the cuff if the clips' fastest drift (mm per rad of arm) "
                                      "happened with the knee AT its straight-side edge: pins <= v (2 / lc + 1 / lE) / sin(ang_min)",
               amp_1_over_sin=dict(max_taken=round(float((1 / sa).max()), 3), at_edge=round(1 / sedge, 3)),
               J3_lever_mm=dict(min_taken=round(float(hC.min()), 2), at_edge=round(lE * sedge, 2)),
               knee_force_per_J3_Nm_N=dict(max_taken=round(1000.0 / float(hC.min()), 1), at_edge=round(1000.0 / (lE * sedge), 1)),
               transmission_angle_min_deg=round(float(min(a.min(), 180 - a.max())), 2), jam=jam,
               worst=sorted(rows, key=lambda r: -r["F_knee"])[:3])
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in out.items() if k != "worst"}, default=float))


if __name__ == "__main__":
    a = sys.argv[1:]; cj = None
    if "--conn" in a: k = a.index("--conn"); cj = a[k + 1]; del a[k:k + 2]
    if a[0] == "wear":
        which, P = config(a[2]); VER.wear("fit60", a[1], which, a[3], P, cj)
    elif a[0] == "conn":
        which, P = config(a[1]); VER.conn("fit60", which, a[2], P)
    elif a[0] == "stats":
        for p in a[1:]: print(json.dumps(stats(p)))
    elif a[0] == "feel": feel(a[1], a[2], a[3])
    elif a[0] == "kinstats": print(json.dumps(kinstats(a[1], a[2])))
    else: raise SystemExit(__doc__)
