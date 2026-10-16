"""Workspace continuity flood fill for skin-normal-3r-pin-knee (CLAUDE.md "Reach must be reachable by moving", 2026-10-16),
written by the P5 verifier (2026-10-16). The model scores every workspace pose on its own; its J1/J2 IK branch and its
knee branch (sign br of the planar RRR C - pin a - pin b) are FIXED constants, so a static pose can still be an island
that no continuous arm motion reaches (walled off by the J1-J3 fold window, the knee window [ang_min, 180 - ang_min],
the knee's triangle limits or the in-plane closure tolerance). This harness checks it on the FULL workspace grid
(1432 poses: 17 planes x 12 elevations x 25 axial, envelope only), shape frozen from the fit bench:

  nodes : workspace poses that are TAKEN (protocol 'taken': the frozen model worn EXACT on all 1432 workspace poses,
          the round-3 verifier's extra_checks applied, B.res >= 0) or kinematically closed (protocol 'kin': fold window
          with the margin in force, knee window + triangle, |radial drift| <= R_tol, closure residual < 0.5 deg);
  edges : grid neighbours (one step in plane, elevation or axial; axial +-180 joined); the humerus (HG, scapula frame)
          is slerped in <= 2 deg steps and EVERY step must close kinematically, with no joint value among q1, q2,
          q3' = q3 + phi, pin a, pin b moving > 10 deg in a step and the knee's signed angle never changing sign
          (no branch change); contact along an edge is not checked (as in stop-relay-rocker-3r.py connected());
  seeds : nodes at elevation 0 (arm at the side, the rest region).

Reports static vs connected counts on the full grid and on the Bench(110,360) workspace poses (connected reach), the
poses that are static-only islands, and the knee branch sign over every node.

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 CB_FOLD_MARGIN=5 python3 docs/concepts/verify/skin-normal-3r-pin-knee-continuity.py \
        <kin|taken> <fitbig|fit60> <out.json> '<json params>'
"""
import importlib.util, json, math, os, sys, time
from types import SimpleNamespace
import numpy as np
from scipy.spatial.transform import Rotation as Rot, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_spec = importlib.util.spec_from_file_location("pin_knee_polish_v", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py"))
PV = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(PV)
V, MK = PV.V, PV.MK
STEP, JUMP = 2.0, 10.0


def frozen_m(P, fit):
    """the frozen knee reference m of the fit bench (Model.__init__ sets it from the fit bench's poses; kinematics only)"""
    nc, nw = (110, 360) if fit == "fitbig" else (60, 160)
    idx = CB._select(nc, nw)[0]
    M1 = MK.Model(SimpleNamespace(idx=np.asarray(idx)), dict(P))
    return np.array(M1.D.m, float), M1.p


def kin(D, Q, R_tol):
    """(n,) kinematic closure + the joint vector (n,5) deg + knee signed angle"""
    q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s)
    ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol)
    R123 = X3[0]; c = (np.einsum("nij,nij->n", R123, Q) - 1) / 2
    ok &= np.degrees(np.arccos(np.clip(c, -1, 1))) < 0.5
    qq = np.degrees(np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"]])
    C2 = s[:, :2]; a = C2 - K["pa"]; b = K["B2"][None] - K["pa"]
    sgn = np.sign(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])          # knee branch: sign of the angle at pin a
    return ok, qq, sgn, K["ang"]


def main():
    mode, fit, outp, P = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4]); t0 = time.time()
    Z = CB._poses_all(); names = list(Z["NAMES"]); ws_id = names.index("Workspace (envelope)")
    W = np.nonzero(Z["CID"] == ws_id)[0]; POSE = Z["POSE"][W]; HG = Z["HG"][W].astype(float)
    m, p = frozen_m(P, fit); D = MK.Design(dict(P)); D.m = m.copy(); D.m[2] = 0.0
    R_tol = float(p["R_tol"])
    ok, qq, sgn, ang = kin(D, HG, R_tol)
    nodes = ok.copy(); taken_src = "kinematic closure"
    if mode == "taken":                                       # frozen model worn EXACT on every workspace pose
        fitB = PV.fast_bench(*((110, 360) if fit == "fitbig" else (60, 160)))
        old = os.environ.get("CB_EXACT"); os.environ["CB_EXACT"] = "1"
        try: B = CB.Bench(20, 20)
        finally:
            if old is None: os.environ.pop("CB_EXACT")
            else: os.environ["CB_EXACT"] = old
        B.idx = W.copy(); B.kind = ["ws"] * len(W); B.clip = ["Workspace (envelope)"] * len(W)
        B.poses = [dict(plane=float(x[0]), elev=float(x[1]), axial=float(x[2]), flex=float(x[3]), pron=float(x[4])) for x in POSE]
        B.res = [None] * len(W); B._skin = {}; B._ex = {}; B._frames = {}; B.grid = None; B._V = None; B.mode = "exact"; B.key = "wsall-v"
        M, fitr, M1 = PV.frozen_on(fitB, B, P); assert np.allclose(M.D.m, m), (M.D.m, m)
        M.run(); ex, bad = V.extra_checks(M, B)
        for i in bad: B.res[i] = None
        nodes = np.array([B.res[i] is not None and float(np.min(B.res[i])) >= 0 for i in range(len(W))])
        taken_src = f"frozen model worn exact on all {len(W)} workspace poses, verifier extra_checks ({len(bad)} removed)"
        assert not (nodes & ~ok).any(), "a taken pose the kinematic check rejects"
    key = {(float(x[0]), float(x[1]), float(x[2])): i for i, x in enumerate(POSE)}
    vals = [sorted(set(POSE[:, k].tolist())) for k in range(3)]

    def nbrs(i):
        x = [float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])]
        for d in range(3):
            j = vals[d].index(x[d]); cand = [j - 1, j + 1]
            for jj in cand:
                if d == 2 and jj == len(vals[2]) and vals[2][-1] == 180.0: jj = 1      # 180 -> -165 (180 == -180)
                if d == 2 and jj == -1 and vals[2][0] == -180.0: jj = len(vals[2]) - 2
                if 0 <= jj < len(vals[d]):
                    y = list(x); y[d] = vals[d][jj]; t = key.get(tuple(y))
                    if t is not None: yield t
        if x[2] in (180.0, -180.0):                                                # the same orientation, other label
            t = key.get((x[0], x[1], -x[2]))
            if t is not None: yield t

    n_edge = [0, 0]; why = {"fold_or_window": 0, "jump": 0, "branch": 0}

    def edge(a, b):
        R0, R1 = Rot.from_matrix(HG[a]), Rot.from_matrix(HG[b]); angd = np.degrees((R0.inv() * R1).magnitude())
        n = max(2, int(math.ceil(angd / STEP)) + 1); Qs = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()
        o, q, sg, _ = kin(D, Qs, R_tol); n_edge[0] += 1
        if not o.all(): why["fold_or_window"] += 1; return False
        d = np.abs((np.diff(q, axis=0) + 180) % 360 - 180)
        if d.max() > JUMP: why["jump"] += 1; return False
        if len(set(sg.tolist())) > 1: why["branch"] += 1; return False
        n_edge[1] += 1; return True

    elev = POSE[:, 1]; conn = np.zeros(len(W), bool); front = [i for i in range(len(W)) if nodes[i] and elev[i] == 0]
    conn[front] = True
    while front:
        nxt = []
        for a in front:
            for b in nbrs(a):
                if nodes[b] and not conn[b] and edge(a, b): conn[b] = True; nxt.append(b)
        front = nxt
    isl = np.nonzero(nodes & ~conn)[0]
    # Bench(110,360) workspace poses
    bidx = np.asarray(CB._select(110, 360)[0]); bws = [int(np.nonzero(W == g)[0][0]) for g in bidx if g in set(W.tolist())]
    oh = POSE[:, 1] >= 140
    out = dict(mode=mode, fit=fit, params=P, fold_margin=KIT.FOLD_MARGIN, o20_only=KIT.O20_ONLY, m=[round(float(x), 4) for x in m],
               nodes_from=taken_src, step_deg=STEP, jump_deg=JUMP,
               grid=dict(poses=len(W), kin_ok=int(ok.sum()), nodes=int(nodes.sum()), connected=int(conn.sum()), islands=int(len(isl)),
                         static_reach=round(float(nodes.mean()), 4), connected_reach=round(float(conn.mean()), 4),
                         overhead140=dict(poses=int(oh.sum()), nodes=int((nodes & oh).sum()), connected=int((conn & oh).sum()))),
               bench110_360=dict(ws=len(bws), nodes=int(nodes[bws].sum()), connected=int(conn[bws].sum()),
                                 static_reach=round(float(nodes[bws].mean()), 4), connected_reach=round(float(conn[bws].mean()), 4)),
               knee_branch_signs=sorted(set(sgn[nodes].tolist())), knee_ang_nodes=[round(float(ang[nodes].min()), 1), round(float(ang[nodes].max()), 1)],
               edges=dict(tested=n_edge[0], passed=n_edge[1], refused=why),
               island_poses=[dict(plane=float(POSE[i, 0]), elev=float(POSE[i, 1]), axial=float(POSE[i, 2])) for i in isl[:40]],
               secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("mode", "fit", "fold_margin", "grid", "bench110_360", "knee_branch_signs", "knee_ang_nodes", "edges", "secs")}, default=float), flush=True)


if __name__ == "__main__":
    main()
