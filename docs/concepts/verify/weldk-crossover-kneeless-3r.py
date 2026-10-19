"""Independent verifier for weldk-crossover-kneeless-3r (round 301, O1 overhead track).

Runs the model UNCHANGED through its own frozen() (fit Bench(60,160) fast, shape frozen, worn with CB_EXACT=1 on
Bench(110,360) or on the verifiers' held set docs/concepts/verify/skin-normal-3r-pin-knee-polish.py held_bench() - the
71-overhead held set the lead's row uses, NOT the claim's osn_polish held_bench), then adds the checks the model does
not make and removes every taken pose that fails one:

  V1 independent closure per taken pose: hub-3 centre seen from link 2 and member 3, the J3 axis, and the RIGID-CUFF
     test - member 3 (bracket + hub-3 upper member), member 6 (the former knee link = pad leg) and member 5 (pad on the
     arm) must be ONE rigid body (rotation <= 0.5 deg, translation <= 0.5 mm apart) and member 5 must turn with the arm
     (rotation vs the bench pose Q <= 0.5 deg); the model's own knee_rigid flag is re-read;
  V2 the inverted J3 stack: hub 3's LOWER plate (z 0 .. UP above the hub face) rides with LINK 2; the pad leg and the
     pad are member 3 (adjacent to link 2 through J3) -> >= 0.15 mm running gap (reported, and >= 1 mm reported too);
  V3 the bracket boss solid (member 3, at pin a's old place) vs hubs 1-2 and link 1 (>= 1 mm; the model's collide has
     no boss term) - the boss vs link 2 is the model's plan-view stacked test (>= 0.15);
  V4 the fold margin in the kit's metric (J1-J3 angle vs [|a1 - a2|, a1 + a2]) >= 5 deg, hub levels <= 140 mm;
  V7 E strap vs link 2 SIDE BY SIDE (kd test on link-2 samples off hub 3): the plan-view stacked test only looks at
     |y| <= W/2 + 1, this catches link 2 running beside the E at the E's own height (>= 0.15);
  V6 the workspace continuity flood fill (full 1432-pose grid, 2-deg slerp edges, joint steps <= 10 deg, no branch
     change, seeds at elevation 0) -> taken bench ws poses that are kinematic islands are removed (bench wear only).
Writes the per-pose dump (tools/alignment_paired.py format) of the model's frozen wear and of the verified wear.

    CB_EXACT=1 OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/weldk-crossover-kneeless-3r.py bench|held out.json ['<json params>']
"""
import importlib.util, json, math, os, sys, time, types
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB  # noqa: E402


def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


MD = _load("weldk_kl_v", os.path.join(REPO, "docs", "concepts", "models", "weldk-crossover-kneeless-3r.py"))
SIB = _load("weldk_os_vv", os.path.join(HERE, "weldk-overstrap-pinknee-3r.py"))          # its flood() is reused unchanged
S, PK = MD.S, MD.PK
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "weldk-crossover-kneeless-3r.json")))


def rot_deg(a, b): return math.degrees(math.acos(max(-1.0, min(1.0, float(a @ b)))))


def rot_ang(R): return math.degrees(math.acos(max(-1.0, min(1.0, (float(np.trace(R)) - 1) / 2))))


def lab(B, i): return dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])


def taken_of(B): return [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]


def extra(M, B):
    D = M.D; P = D.p; u, c = D.u, D.c; sn = D.sn; fr = M.fr; tp = P["tp"]; h = S.T_LINK / 2; ADJ = M.ADJ
    zb, zk = M._lv(M.tr)
    taken = taken_of(B)
    Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float)
    ang = np.linspace(0, 2 * np.pi, 48, endpoint=False); e3, f3v = S.frame_of(u[2]); cen3 = c[2] + M.f[2] * u[2]; r3 = M.hr[2]
    low3 = np.concatenate([cen3 + z * u[2] + r3 * (np.cos(ang)[:, None] * e3 + np.sin(ang)[:, None] * f3v) for z in np.linspace(0, S.UP, 4)]
                          + [cen3 + (lambda dd: dd[:, :1] * e3 + dd[:, 1:] * f3v)(S.disc(r3, 1.0))])      # link 2's plate (member 2)
    e, f = S.frame_of(sn); angb = np.linspace(0, 2 * np.pi, 24, endpoint=False); dd = S.disc(PK.BOSS_R, 1.0)
    boss = np.concatenate([fr["A0"] + z * sn + PK.BOSS_R * (np.cos(angb)[:, None] * e + np.sin(angb)[:, None] * f) for z in (zb, zb + tp / 2, zb + tp)]
                          + [fr["A0"] + z * sn + dd[:, :1] * e + dd[:, 1:] * f for z in (zb, zb + tp)])
    clo = dict(hub3c=0.0, rot3_axis=0.0, m3_m5_rot=0.0, m3_m5_tr=0.0, m3_m6_rot=0.0, m3_m6_tr=0.0, m5_vs_Q=0.0)
    bad = {"closure": [], "knee-hub3low": [], "pad-hub3low": [], "boss": [], "E-L2kd": [], "th": []}
    lows = {"knee-hub3low": [], "pad-hub3low": [], "boss": [], "E-L2kd": []}
    a1, a2 = [float(x) for x in D.A[:2]]; th_m = []
    for i in taken:
        R2, t2 = M.T(2, i); R3, t3 = M.T(3, i); R6, t6 = M.T(6, i); R5, t5 = M.T(5, i)
        v = [float(np.linalg.norm((R2 @ c[2] + t2) - (R3 @ c[2] + t3))), rot_deg(R2 @ u[2], R3 @ u[2]),
             rot_ang(R3.T @ R5), float(np.linalg.norm(t3 - t5)), rot_ang(R3.T @ R6), float(np.linalg.norm(t3 - t6)),
             rot_ang(R5.T @ M.Q[i])]
        for k, x in zip(clo, v): clo[k] = max(clo[k], x)
        qb = rot_ang(M.Q[i].T @ HG[i]); clo["Q_vs_bench_HG_report_only"] = max(clo.get("Q_vs_bench_HG_report_only", 0.0), qb)
        if max(v) > 0.5: bad["closure"].append(i)
        bx = M._boxes_at_final(i)
        L3 = low3 @ R2.T + t2                                               # rides with link 2 (rotationally symmetric)
        for nm in ("knee", "pad"):
            cc, R, half = bx[nm]; d = float(M.sd_box(L3, cc, R, half).min()); lows[f"{nm}-hub3low"].append((d, i))
            if d < ADJ: bad[f"{nm}-hub3low"].append(i)
        bw = boss @ R3.T + t3
        cyl = {k: (M.T(m, i)[0] @ cc + M.T(m, i)[1], M.T(m, i)[0] @ ax) for k, (m, cc, ax) in M.cyl.items()}
        st = {k: X @ M.T(m, i)[0].T + M.T(m, i)[1] for k, (m, X) in M.strap.items()}
        vb = {"boss-hub1": float(M.sd_cyl(bw, *cyl["hub1"], r=M.hr[0]).min()), "boss-hub2": float(M.sd_cyl(bw, *cyl["hub2"], r=M.hr[1]).min())}
        if len(st["L1"]): vb["boss-L1"] = float(cKDTree(st["L1"]).query(bw)[0].min()) - h
        k = min(vb, key=vb.get); lows["boss"].append((vb[k], i))
        if vb[k] < S.PART_CLEAR: bad["boss"].append(i)
        Em = M.Emid[1] @ R3.T + t3; c3w, ax3 = cyl["hub3"]; w = st["L2"] - c3w
        farm = np.linalg.norm(w - (w @ ax3)[:, None] * ax3, axis=1) > M.hr[2] + 1
        dEL2 = float(cKDTree(st["L2"][farm]).query(Em)[0].min()) - 2 * h if farm.any() else 1e9
        lows["E-L2kd"].append((dEL2, i))
        if dEL2 < ADJ: bad["E-L2kd"].append(i)
        w3 = R2 @ u[2]; th = rot_deg(u[0], w3); tm = min(th - abs(math.degrees(a1 - a2)), math.degrees(a1 + a2) - th); th_m.append(tm)
        if tm < 5.0 - 1e-6: bad["th"].append(i)
    out = dict(closure_max={k: round(x, 4) for k, x in clo.items()}, n_taken=len(taken), knee_rigid=M.knee_rigid)
    for k, L in lows.items():
        L.sort(); out[f"{k}_low"] = [dict(mm=round(d, 2), **lab(B, i)) for d, i in L[:5]]
        out[f"{k}_n_lt1mm"] = int(sum(d < 1.0 for d, _ in L))
    out["removed"] = {k: [int(i) for i in sorted(set(v))] for k, v in bad.items()}
    out["min_th_margin_taken"] = round(min(th_m), 3) if th_m else None
    out["hub_levels"] = dict(f=[round(float(x), 2) for x in M.f], tr=round(float(M.tr), 2), zb=round(float(zb), 2), zk=round(float(zk), 2), cap=140,
                             ok=bool(max(list(M.f) + [float(M.tr)]) <= 140))
    out["dims"] = dict(T_LINK=S.T_LINK, W_LINK=S.W_LINK, tp=float(tp), BOSS_R=PK.BOSS_R, PAD_R=PK.PAD_R, KNEE_W=PK.KNEE_W,
                       hub_r=[round(float(x), 2) for x in M.hr], UP=S.UP, RUN=S.RUN, lE=float(P["lE"]), lc=float(P["lc"]))
    return out, set().union(*[set(v) for v in bad.values()])


def overhead(B, M):
    ws = np.array(B.kind) == "ws"; el = np.array([B.poses[j]["elev"] for j in range(len(B.idx))])
    mins = np.array([float(np.min(B.res[j])) if B.res[j] is not None and len(B.res[j]) else np.nan for j in range(len(B.idx))])
    ov = ws & (el >= 140); mid = ws & (el >= 90) & (el < 140); tk = np.isfinite(mins) & (mins >= 0)
    sh1 = tk & (mins < 1); sh2 = tk & (mins >= 1) & (mins < 2)
    why = np.asarray(M.why)
    return dict(ws=int(ov.sum()), taken=int((ov & tk).sum()), shell_lt1=int((ov & sh1).sum()), shell_1_2=int((ov & sh2).sum()),
                why={k: int(((why == k) & ov).sum()) for k in sorted(set(why[ov].tolist()))},
                mid_90_140=dict(ws=int(mid.sum()), taken=int((mid & tk).sum())),
                contact_poses=int((np.isfinite(mins) & (mins < 0)).sum()),
                contact_depth_sum_mm=round(float(-mins[np.isfinite(mins) & (mins < 0)].sum()), 2),
                contact_depth_max_mm=round(float(-mins[np.isfinite(mins) & (mins < 0)].min()), 2) if (np.isfinite(mins) & (mins < 0)).any() else 0.0,
                near1_taken=int(sh1.sum()), near2_taken=int((sh1 | sh2).sum()), min_taken_mm=round(float(mins[tk].min()), 3) if tk.any() else None)


def main():
    wear = sys.argv[1]; outp = sys.argv[2]; P = json.loads(sys.argv[3]) if len(sys.argv) > 3 else dict(ROW["best_params"]); t0 = time.time()
    import alignment_paired as AP
    if wear == "held":
        PV = _load("pk_polish_v_kl", os.path.join(HERE, "skin-normal-3r-pin-knee-polish.py"))
        sys.modules["osn_polish"] = types.SimpleNamespace(held_bench=lambda *a, **k: PV.held_bench())   # the verifiers' held set
        res, M, B = MD.frozen(P, -1, -1)
    else:
        res, M, B = MD.frozen(P)
    base = dict(res["frozen"]); out = dict(id=MD.ID, wear=wear, params=P, mode=B.mode, n_poses=len(B.idx), model_frozen=base, fit_fast=res["fit_fast"],
                                          model_why=res["why"], model_parts_pairs=res["parts_pairs"], model_audit=res["audit"],
                                          model_overhead=overhead(B, M), model_stacked_min_taken=res.get("stacked_min_taken"))
    pre = AP._dump_bench(M, B); out["model_recomputed"] = AP.gap_parts(pre)
    ex, bad = extra(M, B); out["extra"] = ex
    isl = []
    if wear == "bench":
        fl, conn, gidx = SIB.flood(P, res["m_fix"], float(M.p["R_tol"]), M.D); out["flood"] = fl
        isl = [i for i in taken_of(B) if B.kind[i] == "ws" and int(B.idx[i]) in gidx and not conn[gidx[int(B.idx[i])]]]
        out["flood"]["taken_bench_ws_islands"] = [lab(B, i) for i in isl]
    rm = sorted(bad | set(isl)); out["removed_total"] = len(rm); out["removed_poses"] = [lab(B, i) for i in rm]
    for i in rm: B.res[i] = None; M.why[i] = "verifier"
    r = B.report(); out["verified"] = {k: r[k] for k in KEYS}
    out["verified_overhead"] = overhead(B, M)
    out["verified_audit"] = PK.audit(M, B)
    post = AP._dump_bench(M, B); out["verified_recomputed"] = AP.gap_parts(post)
    out["secs"] = round(time.time() - t0, 1)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    dp = os.path.join(REPO, "docs", "alignment", "remeasure", f"{MD.ID}_{wear}_perpose.json")
    json.dump(dict(id=MD.ID, wear=wear, params=P, frozen=base, report=r, poses=pre, verified_poses=post, recomputed=AP.gap_parts(pre),
                   verified_recomputed=AP.gap_parts(post), exact=os.environ.get("CB_EXACT") == "1", secs=out["secs"],
                   note="poses = the model's frozen wear (reproduces model_frozen); verified_poses = after the verifier's removals"),
              open(dp, "w"), default=float)
    print(json.dumps({k: out.get(k) for k in ("model_frozen", "model_recomputed", "verified", "verified_recomputed", "removed_total", "flood", "secs")}, default=float))
    print(json.dumps(out["extra"], default=float))
    print(json.dumps(out["verified_overhead"], default=float))


if __name__ == "__main__":
    main()
