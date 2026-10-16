"""Fold-stop feel (docs/research/fold-stop-feel.md): quasi-static Jacobian analysis of the near-fold J2 stop of
minarc-stop-knuckle-4r variant B (as claimed, and with stops at the kit's 5-deg J1-J3 margin) against the pin knee H1.

Method (numpy, no dynamics engine): every chain is spherical about GH (J1, K, J2 on GH rays; J3's axis through GH, its
offset c3 absorbed by the knee), so member angular velocities and joint torques live in one 3-space (moments about GH).
  * clips: the six fit clips of the pose set at their stored frame rate (Z["FPS"] = 10 fps, the clip keyframes resampled
    at real duration); joint angles from each model's own ik; rates by finite differences between consecutive taken frames.
  * friction: Coulomb torque T per joint (O20 hub = preloaded MR117-2RS pair), T_PIN per knee pin. Cuff moment about GH
    from the statics of the moving joints: u_i . tau = T_i sgn(qdot_i) -> tau = A^-T f (A = world joint axes); the knee
    pins add their dissipated power. Cuff force = |tau| / |GH -> pin b (cuff pad)|.
  * K hold (B, state A): the opening torque the chain puts on K = s_open uK . (tau + G_K); worst over friction signs =
    T ||A^-1 uK||_1. The spring preload must exceed it (minus K's own friction) or K opens before J2 reaches its stop
    (the rate-independent quasi-static motion = the minimum of dissipation + spring/gravity power over the self-motion).
  * stop impact: at the J2 stop, the arm (prescribed motion) keeps its angular velocity; the chain jumps from the state-A
    joint rates (A^-1 w) to the J2-locked rates ([u1 uK u3]^-1 w): energy lost = 1/2 sum_b dw_b^T I_b dw_b (Carnot,
    plastic impact under a prescribed motion), I_b about GH from the sampled metal (Ti straps 8 x 3 mm, O20 stacks).
    H1 has no K: a J2 stop blocks the arm's th-component; chain-only and arm-included losses are reported.

    OMP_NUM_THREADS=1 python3 docs/research/fold_stop_feel.py [T_joint_Nmm] > docs/research/fold/stop_feel.json
"""
import importlib.util, json, math, os, sys
import numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
sp = importlib.util.spec_from_file_location("rm", os.path.join(REPO, "docs/concepts/verify/minarc-stop-knuckle-4r-remeasure.py"))
RM = importlib.util.module_from_spec(sp); sp.loader.exec_module(RM)
KB, MK, S, CB = RM.KB, RM.MK, RM.S, RM.CB
D2R = math.pi / 180; R2D = 180 / math.pi
Z = CB._poses_all(); FPS = float(Z["FPS"]); DT = 1.0 / FPS; NAMES = list(Z["NAMES"]); CID = Z["CID"]
T_J = float(sys.argv[1]) if len(sys.argv) > 1 else 3.0     # N.mm per O20 joint (preloaded MR117-2RS pair, contact seals)
T_PIN = T_J                                                 # N.mm per knee pin
MARGIN = 5.0
G = 9.81
RHO_TI = 4.43e-3                                            # g/mm3
STRAP_GMM = 8.0 * 3.0 * RHO_TI                              # g per mm of 8 x 3 mm Ti strap
# O20 v5 stack (docs/HARDWARE.md levels): lower = plate disc O20 x 3 + pin O7 x 8 + inner rings; upper = boss O20/O11 x 5.6
# + cap (skirt O20/O18 x 3.5 + 1 mm dome) + outer rings; MR117-2RS ~0.65 g each (split 0.25 inner / 0.40 outer)
HUB_LO = (math.pi / 4 * 400 * 3 + math.pi / 4 * 49 * 8) * RHO_TI + 2 * 0.25
HUB_UP = (math.pi / 4 * (400 - 121) * 5.6 + math.pi / 4 * (400 - 324) * 3.5 + math.pi / 4 * 400 * 1.0) * RHO_TI + 2 * 0.40 + 0.5
W = {k: json.load(open(os.path.join(REPO, "docs/concepts/verify/minarc-remeasure", f"wear_{k}_fit60_bench_m5.json"))) for k in ("B", "H1")}


def unit(x): x = np.asarray(x, float); return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)
def wrap(a): return (a + np.pi) % (2 * np.pi) - np.pi
def phi_of_th(th, a1, a2): return R2D * math.acos((math.cos(th * D2R) - math.cos(a1 * D2R) * math.cos(a2 * D2R)) / (math.sin(a1 * D2R) * math.sin(a2 * D2R)))


def make(which):
    if which == "H1":
        P = RM.params_for("H1"); D = MK.Design(P); D.m = np.array(W["H1"]["m"], float); D.isB = False
        D.a1, D.a2 = math.degrees(D.A[0]), math.degrees(D.A[1]); D.f = W["H1"]["f"]; D.tr = W["H1"]["tr"]
    else:
        P = RM.params_for("B")
        if which == "Bkit":
            D0 = KB.KDesign(P); a1, a2 = D0.a1, D0.a2
            P.update(phi_lo=phi_of_th(abs(a1 - a2) + MARGIN, a1, a2), phi_hi=phi_of_th(a1 + a2 - MARGIN, a1, a2))
        D = KB.KDesign(P); D.m = np.array(W["B"]["m"], float); D.isB = True; D.f = W["B"]["f"]; D.tr = W["B"]["tr"]
    D.name = which
    # cuff lever: GH -> pin b on the arm pad (knee B2 at pad height)
    P_ = D.p; pe, pb = P_["phiE"] * D2R, P_["phib"] * D2R; A0 = D.m[:2] + float(P_["lE"]) * np.array([math.cos(pe), math.sin(pe)])
    B2 = A0 + float(P_["lc"]) * np.array([math.cos(pb), math.sin(pb)]); D.pad = D.p3(B2, D.tr)[0]; D.r_cuff = float(np.linalg.norm(D.pad))
    D.bodies = bodies(D)
    return D


def arc_pts(Ca, Cb, n=40):
    da, db = unit(Ca), unit(Cb); R = 0.5 * (np.linalg.norm(Ca) + np.linalg.norm(Cb)); ang = math.acos(float(np.clip(da @ db, -1, 1)))
    ts = (np.arange(n) + 0.5) / n; dirs = np.array([unit(math.sin((1 - t) * ang) * da + math.sin(t * ang) * db) for t in ts])
    return R * dirs, R * ang


def bodies(D):
    """home-frame point masses (g, mm) of the members J2 swings and their neighbours: 1a, 1b (B) / 1 (H1), 2"""
    u = D.u; c = D.c; f = D.f; mid = 6.0                      # hub mass centre ~6 mm above F
    C1 = c[0] + (f[0] + mid) * u[0]; C2 = c[1] + (f[1] + mid) * u[1]; C3 = c[2] + (f[2] + mid) * u[2]
    out = {}
    def body(hubs, a, b):
        pts, L = arc_pts(a, b); m = np.full(len(pts), STRAP_GMM * L / len(pts))
        P = np.r_[pts, np.array([h for h, _ in hubs])]; M = np.r_[m, [w for _, w in hubs]]; return P, M
    if D.isB:
        fK = 0.5 * (f[0] + f[1]); CK = (fK + mid) * D.uK
        out["1a"] = body([(C1, HUB_UP), (CK, HUB_LO)], C1, CK)
        out["1b"] = body([(CK, HUB_UP), (C2, HUB_LO)], CK, C2)
    else:
        out["1"] = body([(C1, HUB_UP), (C2, HUB_LO)], C1, C2)
    out["2"] = body([(C2, HUB_UP), (C3, HUB_UP)], C2, C3)
    return out


def inertia(P, M, R=None):
    """about GH, kg m2, for points P (mm, home frame) rotated by R"""
    X = (P @ R.T if R is not None else P) * 1e-3; m = M * 1e-3
    return np.einsum("i,ij->j", m, X) * 0 + (np.eye(3) * (m * (X * X).sum(1)).sum() - np.einsum("i,ij,ik->jk", m, X, X))


def chain(D, Q):
    q, ok, X1, X2, X3, s = D.ik(Q); n = len(Q)
    K = D.knee(s); ok = ok & K["ok"] & (np.abs(s[:, 2]) <= D.p["R_tol"])
    u1, u2, u3 = D.u; R1 = X1[0]; R2 = X2[0]
    a1w = np.broadcast_to(u1, (n, 3)).copy(); a3w = R2 @ u3
    if D.isB:
        R1b = D._X1b[0]; aKw = R1 @ D.uK; a2w = R1b @ u2; dK = D._dK.copy(); st = D._state.copy(); Rb = {"1a": R1, "1b": R1b, "2": R2}
    else:
        aKw = np.full((n, 3), np.nan); a2w = R1 @ u2; dK = np.zeros(n); st = np.zeros(n, int); Rb = {"1": R1, "2": R2}
    w = Q @ u3; th = R2D * np.arccos(np.clip(w @ u1, -1, 1))
    a_ = a1w - np.einsum("ij,ij->i", a1w, a2w)[:, None] * a2w; b_ = a3w - np.einsum("ij,ij->i", a3w, a2w)[:, None] * a2w
    phi = R2D * np.arccos(np.clip(np.einsum("ij,ij->i", unit(a_), unit(b_)), -1, 1))
    marg = np.minimum(th - abs(D.a1 - D.a2), min(D.a1 + D.a2, 360 - D.a1 - D.a2) - th)
    return dict(q=q, ok=ok, a1=a1w, aK=aKw, a2=a2w, a3=a3w, dK=dK, st=st, qa=K["qa"], qb=K["qb"], th=th, phi=phi, marg=marg, R=Rb)


def s_open(D, C):
    m = C["ok"] & (C["st"] != 0) & (np.abs(C["dK"]) > 1e-6)
    return float(np.sign(np.median(C["dK"][m]))) if m.any() else -1.0


def statics(C, j, T=T_J, sg=None):
    """state-A cuff moment (N.mm) for friction signs sg (3,), and A^-1 uK"""
    A = np.stack([C["a1"][j], C["a2"][j], C["a3"][j]], 1)
    tau = np.linalg.solve(A.T, T * sg); return tau, A


SIGNS = np.array([[a, b, c] for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)], float)


def clips(D):
    rows = []; out = dict(frames=0, taken=0, pairs=0)
    so = s_open(D, chain(D, Z["HG"][np.nonzero(CID == NAMES.index("Workspace (envelope)"))[0]].astype(float))) if D.isB else 0
    Rs_all = Z["RS"]
    acc = []
    for nm in CB.FIT:
        ii = np.nonzero(CID == NAMES.index(nm))[0]; ii = ii[np.argsort(Z["FI"][ii], kind="stable")]
        Q = Z["HG"][ii].astype(float); C = chain(D, Q); out["frames"] += len(ii); out["taken"] += int(C["ok"].sum())
        qq = np.c_[C["q"], C["dK"], C["qa"], C["qb"]]
        prev = None; v2 = {}
        for k in range(len(ii) - 1):
            if not (C["ok"][k] and C["ok"][k + 1]): continue
            dq = wrap(qq[k + 1] - qq[k]); rv = Rot.from_matrix(Q[k + 1] @ Q[k].T).as_rotvec(); dth_arm = np.linalg.norm(rv)
            if dth_arm < 1e-6: continue
            wv = rv / DT                                         # rad/s, scapula frame
            j = k; stA = C["st"][k] == 0 and C["st"][k + 1] == 0
            if stA:
                sg = np.sign(dq[:3]); sg[sg == 0] = 1
                tau, A = statics(C, j, sg=sg)
                hold = None
                if D.isB:
                    x = np.linalg.solve(A, C["aK"][j]); hold = T_J * float(np.abs(x).sum())          # worst-sign K opening torque at this config
                    hold_now = so * float(C["aK"][j] @ tau)
                else: hold_now = None
                pins = T_PIN * (abs(dq[4]) + abs(dq[5])) / dth_arm
                along = (T_J * np.abs(dq[:3]).sum()) / dth_arm + pins
                F_full = (np.linalg.norm(tau) + pins) / D.r_cuff; F_along = along / D.r_cuff
            else:
                A = np.stack([C["a1"][j], C["aK"][j], C["a3"][j]], 1); sg = np.sign(dq[[0, 3, 2]]); sg[sg == 0] = 1
                tau = np.linalg.solve(A.T, T_J * sg); pins = T_PIN * (abs(dq[4]) + abs(dq[5])) / dth_arm
                F_full = (np.linalg.norm(tau) + pins) / D.r_cuff; F_along = ((T_J * (abs(dq[0]) + abs(dq[2]) + abs(dq[3]))) / dth_arm + pins) / D.r_cuff
                hold = hold_now = None
            v2[k] = dq[1] / DT
            rows.append(dict(clip=nm, k=int(k), stA=bool(stA), state=[int(C["st"][k]), int(C["st"][k + 1])], arm_dps=dth_arm / DT * R2D,
                             thdot=abs(C["th"][k + 1] - C["th"][k]) / DT, j2_dps=abs(dq[1]) / DT * R2D, ratio=abs(dq[1]) / dth_arm,
                             dK_dps=abs(dq[3]) / DT * R2D, F_full=F_full, F_along=F_along, hold=hold, hold_now=hold_now,
                             marg=float(min(C["marg"][k], C["marg"][k + 1])), phi=float(max(C["phi"][k], C["phi"][k + 1]))))
        for k in v2:
            if k + 1 in v2: acc.append(abs(v2[k + 1] - v2[k]) / DT * R2D)
    out["pairs"] = len(rows)
    def pk(key, filt=lambda r: True):
        v = np.array([r[key] for r in rows if r[key] is not None and filt(r)]); return (round(float(v.max()), 3), round(float(np.percentile(v, 99)), 3), round(float(np.median(v)), 3)) if len(v) else None
    out.update(arm_dps=pk("arm_dps"), thdot_dps=pk("thdot"), j2_dps=pk("j2_dps"), ratio=pk("ratio"), F_full=pk("F_full"), F_along=pk("F_along"),
               hold_worst=pk("hold"), hold_now=pk("hold_now"), j2_acc=(round(float(max(acc)), 1), round(float(np.percentile(acc, 99)), 1)) if acc else None,
               min_marg=round(min(r["marg"] for r in rows), 2), max_phi=round(max(r["phi"] for r in rows), 2),
               states=dict(A=sum(1 for r in rows if r["stA"]), forced=sum(1 for r in rows if not r["stA"])),
               transitions=[r for r in rows if r["state"][0] != r["state"][1]][:10])
    worst = sorted(rows, key=lambda r: -r["F_full"])[:3]; out["worst_F"] = worst
    return out


def stop_config(D, phi_stop, side=+1):
    """the chain exactly at the J2 stop (q1 = 0, K closed, q3 free): world axes + member rotations; uses ik on a synthetic arm"""
    u1, u2, u3 = D.u; a1, a2 = D.a1, D.a2
    th = R2D * math.acos(math.cos(a1 * D2R) * math.cos(a2 * D2R) + math.sin(a1 * D2R) * math.sin(a2 * D2R) * math.cos(phi_stop * D2R))
    # build: w at angle th from u1, on the side the model's branch uses: search the workspace for the taken pose nearest th
    return th


def analytic(D, phi):
    """state-A chain at J2 interior angle phi (K closed): rate ratio, worst friction cuff force, worst K-opening torque,
    impact energy per (rad/s)^2 of th-speed at the stop (B: K takes over; H1: the arm's th-component is blocked)"""
    u1, u2, u3 = D.u; a1, a2 = D.a1, D.a2
    # rotate J3's axis about u2 so the interior angle at J2 between arcs to u1 and to u3 is phi (home frame, q1 = 0)
    best = None
    for q2 in np.linspace(-np.pi, np.pi, 7201):
        R = S.rotm(u2, np.array([q2]))[0]; w = R @ u3
        a_ = unit(u1 - (u1 @ u2) * u2); b_ = unit(w - (w @ u2) * u2); ph = R2D * math.acos(float(np.clip(a_ @ b_, -1, 1)))
        if best is None or abs(ph - phi) < best[0]: best = (abs(ph - phi), q2, R, w)
    _, q2, R2, w = best
    A = np.stack([u1, u2, w], 1); Ainv = np.linalg.inv(A)
    th = R2D * math.acos(float(np.clip(w @ u1, -1, 1))); marg = min(th - abs(a1 - a2), a1 + a2 - th)
    ratio = float(np.linalg.norm(Ainv[1]))
    tau_w = max(float(np.linalg.norm(np.linalg.solve(A.T, T_J * sg))) for sg in SIGNS)
    out = dict(phi=round(phi, 2), th=round(th, 2), margin=round(marg, 2), ratio=round(ratio, 3), F_fric_worst=round((tau_w + 2 * T_PIN * ratio * 0) / D.r_cuff, 3),
               tau_fric_worst=round(tau_w, 2))
    # arm motion into the stop: the unit w that increases th (stretched) fastest
    om = unit(np.cross(w, u1)) * (-1 if True else 1)
    if (np.cross(om, w) @ u1) > 0: om = -om                     # d(w.u1)/dt = (om x w).u1 < 0 -> th increases
    if phi < 90: om = -om                                        # folded side: into the stop = th decreasing
    qd = Ainv @ om                                               # per rad/s of arm speed
    I = {k: inertia(P, M) for k, (P, M) in D.bodies.items()}
    if D.isB:
        I["2"] = inertia(*D.bodies["2"], R=S.rotm(u2, np.array([q2]))[0]) if False else I["2"]
        uK = D.uK; x = Ainv @ uK; out["K_open_torque_worst"] = round(T_J * float(np.abs(x).sum()), 2)
        As = np.stack([u1, uK, w], 1); qs = np.linalg.solve(As, om)
        w1a0, w1b0 = qd[0] * u1, qd[0] * u1; w20 = qd[0] * u1 + qd[1] * u2
        w1a1, w1b1 = qs[0] * u1, qs[0] * u1 + qs[1] * uK; w21 = w1b1
        # link 2 world inertia: home-frame points rotated by J2's q2 (q1 = 0, K closed)
        I2 = inertia(*D.bodies["2"], R=R2)
        E = 0.5 * ((w1a1 - w1a0) @ I["1a"] @ (w1a1 - w1a0) + (w1b1 - w1b0) @ I["1b"] @ (w1b1 - w1b0) + (w21 - w20) @ I2 @ (w21 - w20))
        out["K_rate_after"] = round(float(qs[1]), 3); out["sub_cond"] = round(float(np.linalg.cond(As)), 2)
        out["E_per_rad2"] = float(E); out["I2_about_u2"] = float(u2 @ I2 @ u2); out["E_simple_per_rad2"] = 0.5 * float(u2 @ I2 @ u2) * ratio ** 2
        out["opening_ok"] = True
    else:
        I2 = inertia(*D.bodies["2"], R=R2)
        # J2 locked: the arm keeps only the part of om in span(u1, w) (least-squares), th-component blocked
        As = np.stack([u1, w], 1); y = np.linalg.lstsq(As, om, rcond=None)[0]; om1 = As @ y
        w10, w20 = qd[0] * u1, qd[0] * u1 + qd[1] * u2; w11 = y[0] * u1; w21 = y[0] * u1
        E = 0.5 * ((w11 - w10) @ I["1"] @ (w11 - w10) + (w21 - w20) @ I2 @ (w21 - w20))
        out["E_per_rad2"] = float(E); out["I2_about_u2"] = float(u2 @ I2 @ u2); out["E_simple_per_rad2"] = 0.5 * float(u2 @ I2 @ u2) * ratio ** 2
        out["arm_blocked_frac"] = round(float(np.linalg.norm(om - om1)), 3)
    return out


def workspace(D):
    ii = np.nonzero(CID == NAMES.index("Workspace (envelope)"))[0]; Q = Z["HG"][ii].astype(float); C = chain(D, Q)
    ok = C["ok"]; A_ = ok & (C["st"] == 0); res = dict(n=len(ii), taken_kin=int(ok.sum()), stateA=int(A_.sum()), forced=int((ok & (C["st"] != 0)).sum()))
    rat, Fw, hold = [], [], []
    for j in np.nonzero(A_)[0]:
        A = np.stack([C["a1"][j], C["a2"][j], C["a3"][j]], 1); Ai = np.linalg.inv(A); rat.append(float(np.linalg.norm(Ai[1])))
        Fw.append(max(float(np.linalg.norm(np.linalg.solve(A.T, T_J * sg))) for sg in SIGNS) / D.r_cuff)
        if D.isB: hold.append(T_J * float(np.abs(Ai @ C["aK"][j]).sum()))
    res.update(min_margin_stateA=round(float(C["marg"][A_].min()), 2), ratio_max=round(max(rat), 3), F_worst_max=round(max(Fw), 3),
               F_worst_p99=round(float(np.percentile(Fw, 99)), 3), hold_max=round(max(hold), 2) if hold else None)
    if D.isB:
        F_ = ok & (C["st"] == 1)
        if F_.any():
            q2s = C["q"][F_, 1] * R2D; res["stretched_q2_span_deg"] = round(float(np.ptp(np.unwrap(q2s * D2R)) * R2D), 2)
            res["stretched_phi_span"] = [round(float(C["phi"][F_].min()), 2), round(float(C["phi"][F_].max()), 2)]
            res["dK_range"] = [round(float(C["dK"][F_].min() * R2D), 2), round(float(C["dK"][F_].max() * R2D), 2)]
    return res, C


def gravity_hold(D, C, ii):
    """K opening torque from the links' weight alone (N.mm), over the workspace state-A poses: |sum_{1b,2} r x m g| . uK in
    the opening sense, with the cuff moment closing J1..J3 (frictionless) - upper bound: the static moment of 1b + 2 about uK"""
    if not D.isB: return None
    up_world = np.array([0.0, 1.0, 0.0]); out = []
    for j in np.nonzero(C["ok"] & (C["st"] == 0))[0]:
        RS = Z["RS"][ii[j]].astype(float); g_s = RS.T @ (-up_world) * G * 1e-3       # N per g, scapula frame
        Gm = {}
        for k, Rk in (("1a", C["R"]["1a"][j]), ("1b", C["R"]["1b"][j]), ("2", C["R"]["2"][j])):
            P, M = D.bodies[k]; X = P @ Rk.T; Gm[k] = (np.cross(X, g_s[None] * M[:, None])).sum(0)   # N.mm
        A = np.stack([C["a1"][j], C["a2"][j], C["a3"][j]], 1)
        # distal sets: J1 {1a,1b,2}, J2 {2}, J3 {} ; K {1b, 2}; member 3 rides the arm (its weight goes to the cuff)
        f = -np.array([C["a1"][j] @ (Gm["1a"] + Gm["1b"] + Gm["2"]), C["a2"][j] @ Gm["2"], 0.0])
        tau = np.linalg.solve(A.T, f)
        out.append(float(C["aK"][j] @ (tau + Gm["1b"] + Gm["2"])))
    return out


if __name__ == "__main__":
    res = dict(T_joint_Nmm=T_J, T_pin_Nmm=T_PIN, fps=FPS, hub_lo_g=round(HUB_LO, 2), hub_up_g=round(HUB_UP, 2), strap_g_per_mm=round(STRAP_GMM, 4))
    wsi = np.nonzero(CID == NAMES.index("Workspace (envelope)"))[0]
    for which in ("B", "Bkit", "H1"):
        D = make(which); r = dict(a=[round(D.a1, 2), round(D.a2, 2)], r_cuff_mm=round(D.r_cuff, 1),
                                  masses_g={k: round(float(M.sum()), 1) for k, (P, M) in D.bodies.items()})
        if D.isB: r["phi_stops"] = [round(float(D.p["phi_lo"]), 2), round(float(D.p["phi_hi"]), 2)]
        else:
            r["phi_stops"] = [round(phi_of_th(abs(D.a1 - D.a2) + MARGIN, D.a1, D.a2), 2), round(phi_of_th(min(D.a1 + D.a2, 360 - D.a1 - D.a2) - MARGIN, D.a1, D.a2), 2)]
        r["stop_hi"] = analytic(D, r["phi_stops"][1]); r["stop_lo"] = analytic(D, r["phi_stops"][0])
        r["phi_sweep"] = [analytic(D, p) for p in np.linspace(90, r["phi_stops"][1], 6)]
        r["clips"] = clips(D)
        r["workspace"], C = workspace(D)
        gh = gravity_hold(D, C, wsi)
        if gh is not None:
            so = s_open(D, C); gv = np.array(gh) * so
            r["gravity_K_open_Nmm"] = dict(max=round(float(gv.max()), 2), p99=round(float(np.percentile(gv, 99)), 2), min=round(float(gv.min()), 2), s_open=so)
        res[which] = r
        print(which, json.dumps({k: r[k] for k in ("a", "r_cuff_mm", "masses_g", "phi_stops", "stop_hi")}, default=float), file=sys.stderr, flush=True)
    print(json.dumps(res, indent=1, default=float))
