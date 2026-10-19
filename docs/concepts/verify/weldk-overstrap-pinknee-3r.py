"""Independent verifier for weldk-overstrap-pinknee-3r (round 301, O1 overhead track).

Runs the model UNCHANGED through its own frozen() (fit Bench(60,160) fast, shape frozen, worn on Bench(110,360) with
CB_EXACT=1), then adds the checks the model does not make and removes every taken pose that fails one:

  V1 independent 3D closure per taken pose: hub-3 centre seen from link 2 and member 3, J3 axis, pin a seen from member 3
     and the knee link, pin b seen from the knee link and the arm, pin-axis parallelism (each <= 0.5 mm / 0.5 deg);
  V2 the INVERTED J3 stack (over=1): hub 3's LOWER plate (z 0 .. UP above the hub face) rides with LINK 2 (member 2), so
     the knee link (member 6) and the arm pad (member 5) are NOT adjacent to it -> >= 1 mm (the model scores the whole
     hub-3 cylinder as member 3 and lets the knee link run at the 0.15 mm pin-a rule against it);
  V3 the E boss solid (member 3) vs hubs 1-2 and link 1 (>= 1 mm, not in the model's collide) and vs link 2 (>= 0.15);
  V4 knee window margin, fold (th) margin in the kit's metric (J1-J3 angle vs [|a1 - a2|, a1 + a2]), hub levels <= 140;
  V5 the arm pad under kinv 1 sits ABOVE the knee link at pin b: the pad's leg to the cuff must clear the knee link's
     sweep about pin b (pad frame) - report the free sector at r 9-13 mm from pin b over the taken poses;
  V6 the workspace continuity flood fill (kinematic protocol of docs/concepts/verify/skin-normal-3r-pin-knee-continuity.py:
     full 1432-pose grid, 2-deg slerp edges, joint steps <= 10 deg in q1, q2, q3', pin a, pin b, no knee branch change,
     seeds at elevation 0) -> taken bench ws poses that are kinematic islands are removed.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/weldk-overstrap-pinknee-3r.py out.json ['<json params>']
"""
import importlib.util, json, math, os, sys, time
from types import SimpleNamespace
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation as Rot, Slerp

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB  # noqa: E402
_sp = importlib.util.spec_from_file_location("weldk_os_v", os.path.join(REPO, "docs", "concepts", "models", "weldk-overstrap-pinknee-3r.py"))
MD = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(MD)
S, PK = MD.S, MD.PK
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "weldk-overstrap-pinknee-3r.json")))


def rot_deg(a, b): return math.degrees(math.acos(max(-1.0, min(1.0, float(a @ b)))))


def lab(B, i): return dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])


def extra(M, B):
    D = M.D; P = D.p; u, c = D.u, D.c; sn = D.sn; fr = M.fr; tp = P["tp"]; h = S.T_LINK / 2
    zb, zk = M._lv(M.tr)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    ang = np.linspace(0, 2 * np.pi, 48, endpoint=False); e3, f3v = S.frame_of(u[2]); cen3 = c[2] + M.f[2] * u[2]; r3 = M.hr[2]
    low3 = np.concatenate([cen3 + z * u[2] + r3 * (np.cos(ang)[:, None] * e3 + np.sin(ang)[:, None] * f3v) for z in np.linspace(0, S.UP, 4)]
                          + [cen3 + (lambda dd: dd[:, :1] * e3 + dd[:, 1:] * f3v)(S.disc(r3, 1.0))])      # link 2's plate (member 2)
    e, f = S.frame_of(sn); angb = np.linspace(0, 2 * np.pi, 24, endpoint=False); dd = S.disc(PK.BOSS_R, 1.0)
    boss = np.concatenate([fr["A0"] + z * sn + PK.BOSS_R * (np.cos(angb)[:, None] * e + np.sin(angb)[:, None] * f) for z in (zb, zb + tp / 2, zb + tp)]
                          + [fr["A0"] + z * sn + dd[:, :1] * e + dd[:, 1:] * f for z in (zb, zb + tp)])
    clo = dict(hub3c=0.0, rot3_axis=0.0, pin_a=0.0, pin_b=0.0, knee_rot_axis=0.0)
    bad = {"closure": [], "knee-hub3low": [], "pad-hub3low": [], "boss": []}; lows = {"knee-hub3low": [], "pad-hub3low": [], "boss": []}
    a1, a2 = [float(x) for x in D.A[:2]]; th_m = []; kang = []; padsec = []
    for i in taken:
        R2, t2 = M.T(2, i); R3, t3 = M.T(3, i); R6, t6 = M.T(6, i); R5, t5 = M.T(5, i)
        v = [float(np.linalg.norm((R2 @ c[2] + t2) - (R3 @ c[2] + t3))), rot_deg(R2 @ u[2], R3 @ u[2]),
             float(np.linalg.norm((R3 @ fr["A0"] + t3) - (R6 @ fr["A0m"] + t6))), float(np.linalg.norm((R6 @ fr["Bm"] + t6) - (R5 @ fr["Bm"] + t5))),
             max(rot_deg(R3 @ sn, R6 @ sn), rot_deg(R6 @ sn, R5 @ sn))]
        for k, x in zip(clo, v): clo[k] = max(clo[k], x)
        if max(v) > 0.5: bad["closure"].append(i)
        bx = M._boxes_at_final(i)
        L3 = low3 @ R2.T + t2                                               # rides with link 2 (rotationally symmetric)
        for nm in ("knee", "pad"):
            cc, R, half = bx[nm]; d = float(M.sd_box(L3, cc, R, half).min()); lows[f"{nm}-hub3low"].append((d, i))
            if d < S.PART_CLEAR: bad[f"{nm}-hub3low"].append(i)
        bw = boss @ R3.T + t3
        cyl = {k: (M.T(m, i)[0] @ cc + M.T(m, i)[1], M.T(m, i)[0] @ ax) for k, (m, cc, ax) in M.cyl.items()}
        st = {k: X @ M.T(m, i)[0].T + M.T(m, i)[1] for k, (m, X) in M.strap.items()}
        vb = {"boss-hub1": float(M.sd_cyl(bw, *cyl["hub1"], r=M.hr[0]).min()), "boss-hub2": float(M.sd_cyl(bw, *cyl["hub2"], r=M.hr[1]).min())}
        if len(st["L1"]): vb["boss-L1"] = float(cKDTree(st["L1"]).query(bw)[0].min()) - h
        k = min(vb, key=vb.get); lows["boss"].append((vb[k], i))
        if vb[k] < S.PART_CLEAR: bad["boss"].append(i)
        # V7: E strap vs link 2 side by side (H1's kd test, link-2 samples off hub 3): the plan-view stacked test only
        # looks at |y| <= W/2 + 1; this catches a link 2 running beside the E at the E's own height (E dips to F3 + 0.5)
        Em = M.Emid[1] @ R3.T + t3; c3w, ax3 = cyl["hub3"]; w = st["L2"] - c3w
        farm = np.linalg.norm(w - (w @ ax3)[:, None] * ax3, axis=1) > M.hr[2] + 1
        dEL2 = float(cKDTree(st["L2"][farm]).query(Em)[0].min()) - 2 * h if farm.any() else 1e9
        lows.setdefault("E-L2kd", []).append((dEL2, i))
        if dEL2 < M.ADJ: bad.setdefault("E-L2kd", []).append(i)
        w3 = R2 @ u[2]; th = rot_deg(u[0], w3); th_m.append(min(th - abs(math.degrees(a1 - a2)), math.degrees(a1 + a2) - th))
        kang.append(float(M.K["ang"][i]))
        # V5: knee link box corners relative to pin b in the pad (arm) frame, plane angle
        cc, R, half = bx["knee"]; pb = R5 @ fr["Bm"] + t5
        corners = np.array([[sx * half[0], sy * half[1], 0.0] for sx in (-1, 1) for sy in (-1, 1)]) @ R.T + cc
        padsec.append((R5.T @ (corners - pb).T).T)
    out = dict(closure_max={k: round(x, 4) for k, x in clo.items()}, n_taken=len(taken))
    for k, L in lows.items():
        L.sort(); out[f"{k}_low"] = [dict(mm=round(d, 2), **lab(B, i)) for d, i in L[:5]]
    out["removed"] = {k: [int(i) for i in sorted(set(v))] for k, v in bad.items()}
    out["min_th_margin_taken"] = round(min(th_m), 3) if th_m else None
    am = float(P["ang_min"]); out["knee_window"] = dict(ang_min=am, taken_range=[round(min(kang), 2), round(max(kang), 2)],
                                                       margin=round(min(min(kang) - am, 180 - am - max(kang)), 2) if kang else None)
    out["hub_levels"] = dict(f=[round(float(x), 2) for x in M.f], tr=round(float(M.tr), 2), zb=round(float(zb), 2), zk=round(float(zk), 2), cap=140)
    # V5: free sector for a pad leg (3 mm post) at radius r from pin b in the pad plane (sa, st)
    sa, stv = D.sa, D.st; sec = {}
    if padsec:
        Cw = np.concatenate(padsec)        # knee box corners in the arm frame at home = pad frame
        # sample the knee box area (not only corners) in the pad frame per pose
        pts = []
        for i in taken:
            bx = M._boxes_at_final(i); cc, R, half = bx["knee"]; R5, t5 = M.T(5, i); pb = R5 @ fr["Bm"] + t5
            g = np.stack(np.meshgrid(np.linspace(-half[0], half[0], 19), np.linspace(-half[1], half[1], 7), [0.0], indexing="ij"), -1).reshape(-1, 3)
            pts.append((R5.T @ ((g @ R.T + cc) - pb).T).T)
        X = np.concatenate(pts); x2 = np.c_[X @ sa, X @ stv]
        for r in (9.0, 11.0, 13.0):
            angs = np.radians(np.arange(0, 360, 2)); post = r * np.c_[np.cos(angs), np.sin(angs)]
            dmin = cKDTree(x2).query(post)[0] - 1.5             # 3 mm post
            free = np.degrees(angs[dmin >= 0.15 + 0.5])         # + 0.5 sampling slack
            sec[f"r{int(r)}"] = dict(free_deg=int(len(free) * 2), of=360)
    out["pad_leg_free_sector"] = sec
    return out, set().union(*[set(v) for v in bad.values()])


def flood(P, m_fix, R_tol, D):
    Z = CB._poses_all(); names = list(Z["NAMES"]); ws_id = names.index("Workspace (envelope)")
    W = np.nonzero(Z["CID"] == ws_id)[0]; POSE = Z["POSE"][W]; HG = Z["HG"][W].astype(float)

    def kin(Q):
        q, ok, X1, X2, X3, s = D.ik(Q); K = D.knee(s)
        ok = ok & K["ok"] & (np.abs(s[:, 2]) <= R_tol)
        cc = (np.einsum("nij,nij->n", X3[0], Q) - 1) / 2; ok &= np.degrees(np.arccos(np.clip(cc, -1, 1))) < 0.5
        qq = np.degrees(np.c_[q[:, :2], q[:, 2] + K["phi"], K["qa"], K["qb"]])
        a = s[:, :2] - K["pa"]; b = K["B2"][None] - K["pa"]; sg = np.sign(a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])
        return ok, qq, sg
    ok, qq, sg = kin(HG); key = {(float(x[0]), float(x[1]), float(x[2])): i for i, x in enumerate(POSE)}
    vals = [sorted(set(POSE[:, k].tolist())) for k in range(3)]

    def nbrs(i):
        x = [float(POSE[i, 0]), float(POSE[i, 1]), float(POSE[i, 2])]
        for d in range(3):
            j = vals[d].index(x[d])
            for jj in (j - 1, j + 1):
                if d == 2 and jj == len(vals[2]) and vals[2][-1] == 180.0: jj = 1
                if d == 2 and jj == -1 and vals[2][0] == -180.0: jj = len(vals[2]) - 2
                if 0 <= jj < len(vals[d]):
                    y = list(x); y[d] = vals[d][jj]; t = key.get(tuple(y))
                    if t is not None: yield t
        if x[2] in (180.0, -180.0):
            t = key.get((x[0], x[1], -x[2]))
            if t is not None: yield t
    why = {"fold_or_window": 0, "jump": 0, "branch": 0}

    def edge(a, b):
        angd = np.degrees((Rot.from_matrix(HG[a]).inv() * Rot.from_matrix(HG[b])).magnitude())
        n = max(2, int(math.ceil(angd / 2.0)) + 1)
        Qs = Slerp([0, 1], Rot.from_matrix(np.stack([HG[a], HG[b]])))(np.linspace(0, 1, n)).as_matrix()
        o, q, s = kin(Qs)
        if not o.all(): why["fold_or_window"] += 1; return False
        if np.abs((np.diff(q, axis=0) + 180) % 360 - 180).max() > 10.0: why["jump"] += 1; return False
        if len(set(s.tolist())) > 1: why["branch"] += 1; return False
        return True
    elev = POSE[:, 1]; conn = np.zeros(len(W), bool); front = [i for i in range(len(W)) if ok[i] and elev[i] == 0]; conn[front] = True
    while front:
        nxt = []
        for a in front:
            for b in nbrs(a):
                if ok[b] and not conn[b] and edge(a, b): conn[b] = True; nxt.append(b)
        front = nxt
    gidx = {int(g): j for j, g in enumerate(W)}
    return dict(grid=len(W), kin_ok=int(ok.sum()), connected=int(conn.sum()), islands=int((ok & ~conn).sum()), refused=why,
                branch_signs=sorted(set(sg[ok].tolist()))), conn, gidx


def main():
    outp = sys.argv[1]; P = json.loads(sys.argv[2]) if len(sys.argv) > 2 else dict(ROW["best_params"]); t0 = time.time()
    res, M, B = MD.frozen(P)
    base = dict(res["frozen"]); out = dict(id=MD.ID, params=P, mode=B.mode, bench=[110, 360], model_frozen=base, fit_fast=res["fit_fast"],
                                          model_why=res["why"], model_parts_pairs=res["parts_pairs"], model_audit=res["audit"])
    ex, bad = extra(M, B); out["extra"] = ex
    fl, conn, gidx = flood(P, res["m_fix"], float(M.p["R_tol"]), M.D); out["flood"] = fl
    isl = [i for i in range(len(B.idx)) if B.kind[i] == "ws" and B.res[i] is not None and float(np.min(B.res[i])) >= 0
           and int(B.idx[i]) in gidx and not conn[gidx[int(B.idx[i])]]]
    out["flood"]["taken_bench_ws_islands"] = [lab(B, i) for i in isl]
    rm = sorted(bad | set(isl)); out["removed_total"] = len(rm); out["removed_poses"] = [lab(B, i) for i in rm]
    for i in rm: B.res[i] = None; M.why[i] = "verifier"
    r = B.report(); out["verified"] = {k: r[k] for k in KEYS}
    out["verified_audit"] = PK.audit(M, B)
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("model_frozen", "verified", "removed_total", "flood", "secs")}, default=float))
    print(json.dumps(out["extra"], default=float))


if __name__ == "__main__":
    main()
