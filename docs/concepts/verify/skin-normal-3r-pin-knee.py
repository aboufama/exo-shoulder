"""Adversarial verifier for skin-normal-3r-pin-knee (2026-10-16). Re-measures one configuration, frozen-shape protocol
(fit on Bench(60,160) FAST, worn on Bench(110,360) without refit; CB_EXACT=1 for the exact path), with the model's own
checks plus the verifier's:

  * independent 3D closure per taken pose (not the closed form the model solves with): hub 3's centre as carried by
    link 2 vs by member 3, the link-2 -> member-3 rotation about J3's axis only, pin a as carried by member 3 vs by the
    knee link, pin b as carried by the knee link vs by the arm, both knee rotations about axes parallel to J3;
  * knee link vs hub 3 ABOVE its lower plate (that part rides with link 2: non-adjacent, >= 1 mm; the model counts the
    whole hub 3 as adjacent to the knee at 0.15 mm);
  * the E boss (O12 x tp at pin a, member 3) vs hub 1, hub 2, link 1 (>= 1 mm) and link 2 (adjacent at J3, 0.15 mm);
    the model checks the E strap but not its end boss;
  * J3 travel q3 = q3' - phi and the pin rotation spans over the taken poses (reported);
  * the arm pad's place on the arm (distance from GH along the humerus, height over the skin) - it must sit on the cuff;
  * the model's own audit (near-touch incl. walls / crowns / tops / edges, metal < 1 mm as contact, overhead >= 140).

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 python3 docs/concepts/verify/skin-normal-3r-pin-knee.py <out.json> ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_spec = importlib.util.spec_from_file_location("pin_knee_model", os.path.join(REPO, "docs", "concepts", "models", "skin-normal-3r-pin-knee.py"))
MK = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(MK)
S = MK.S
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "skin-normal-3r-pin-knee.json")))
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")


def frozen_model(P, nc=110, nw=360):
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = MK.Model(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in KEYS}; fit["mode"] = B1.mode
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(MK.Model):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_h12"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=nc, n_ws=nw); M = Frozen(B, P2)
    return M, B, fit, M1


def rot_angle(R): return math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2))))


def extra_checks(M, B):
    D = M.D; P = D.p; u, c = D.u, D.c; sn = D.sn; fr = M.fr; tr = M.tr; tp = P["tp"]; h = S.T_LINK / 2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    out = dict(axis_sn_vs_u3_deg=round(math.degrees(math.acos(min(1, abs(float(sn @ u[2]))))), 4))
    # hub 3 part above its lower plate (rides with link 2), home member-3 frame
    _, X = M.cyl_surf["hub3"]; cen3 = c[2] + M.f[2] * u[2]; zz = (X - cen3) @ u[2]; H3up = X[zz >= S.UP - 1e-6]
    # E boss solid surface (member 3)
    e, f = S.frame_of(sn); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); dd = S.disc(MK.BOSS_R, 1.0)
    boss = np.concatenate([fr["A0"] + z * sn + MK.BOSS_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in (tr, tr + tp / 2, tr + tp)]
                          + [fr["A0"] + z * sn + dd[:, :1] * e + dd[:, 1:] * f for z in (tr, tr + tp)])
    clo = dict(hub3c=0.0, rot3_axis=0.0, pin_a=0.0, pin_b=0.0, knee_rot_axis=0.0, arm_rot=0.0)
    bad_close, bad_kh3, bad_boss = [], [], []; low_kh3, low_boss = [], []
    q3, qa, qb = [], [], []
    for i in taken:
        R2, t2 = M.T(2, i); R3, t3 = M.T(3, i); R6, t6 = M.T(6, i); R5, t5 = M.T(5, i)
        e1 = float(np.linalg.norm((R2 @ c[2] + t2) - (R3 @ c[2] + t3)))
        Rr = R2.T @ R3; e2 = math.degrees(math.acos(min(1.0, float((Rr @ u[2]) @ u[2]))))
        A_m3 = R3 @ fr["A0"] + t3; A_k = R6 @ fr["A0m"] + t6; e3 = float(np.linalg.norm(A_m3 - A_k))
        B_k = R6 @ fr["Bm"] + t6; B_a = R5 @ fr["Bm"] + t5; e4 = float(np.linalg.norm(B_k - B_a))
        e5 = max(math.degrees(math.acos(min(1.0, float(((R3.T @ R6) @ sn) @ sn)))), math.degrees(math.acos(min(1.0, float(((R6.T @ R5) @ sn) @ sn)))))
        e6 = rot_angle((R2 @ Rr).T @ R3)           # trivially 0; arm rotation residual comes from the model's res_deg
        for k, v in zip(("hub3c", "rot3_axis", "pin_a", "pin_b", "knee_rot_axis"), (e1, e2, e3, e4, e5)): clo[k] = max(clo[k], v)
        if e1 > 0.5 or e3 > 0.5 or e4 > 0.5 or e2 > 0.5 or e5 > 0.5: bad_close.append(i)
        bx = M._boxes_at_final(i); kc, kR, kh = bx["knee"]
        d_kh3 = float(M.sd_box(H3up @ R3.T + t3, kc, kR, kh).min()); low_kh3.append((d_kh3, i))
        if d_kh3 < S.PART_CLEAR: bad_kh3.append(i)
        bw = boss @ R3.T + t3; cyl = {k: (M.T(m, i)[0] @ cc + M.T(m, i)[1], M.T(m, i)[0] @ ax) for k, (m, cc, ax) in M.cyl.items()}
        st = {k: X @ M.T(m, i)[0].T + M.T(m, i)[1] for k, (m, X) in M.strap.items()}
        v = {"boss-hub1": float(M.sd_cyl(bw, *cyl["hub1"]).min()), "boss-hub2": float(M.sd_cyl(bw, *cyl["hub2"]).min())}
        if len(st["L1"]): v["boss-L1"] = float(cKDTree(st["L1"]).query(bw)[0].min()) - h
        c3w, ax3 = cyl["hub3"]; w = st["L2"] - c3w; far = np.linalg.norm(w - (w @ ax3)[:, None] * ax3, axis=1) > S.HUB_R + 1
        vL2 = float(cKDTree(st["L2"][far]).query(bw)[0].min()) - h if far.any() else 1e9
        k = min(v, key=v.get); low_boss.append((min(v[k], vL2), i, k if v[k] <= vL2 else "boss-L2"))
        if v[k] < S.PART_CLEAR or vL2 < M.ADJ: bad_boss.append(i)
        q3.append(float(M.q[i, 2] - M.K["phi"][i])); qa.append(float(M.K["qa"][i])); qb.append(float(M.K["qb"][i]))
    out["closure_max"] = {k: round(v, 4) for k, v in clo.items()}; out["closure_bad_poses"] = len(bad_close)
    out["res_deg_max_taken"] = round(float(M.res_deg[taken].max()), 4) if taken else None
    low_kh3.sort(); low_boss.sort()
    lab = lambda i: dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])
    out["knee_vs_hub3_upper_low"] = [dict(mm=round(d, 2), **lab(i)) for d, i in low_kh3[:5]]; out["knee_vs_hub3_upper_bad"] = len(bad_kh3)
    out["boss_low"] = [dict(mm=round(d, 2), pair=k, **lab(i)) for d, i, k in low_boss[:5]]; out["boss_bad"] = len(bad_boss)
    span = lambda a: round(math.degrees(float(np.ptp(np.unwrap(np.array(a))))), 1) if a else None
    out["spans_deg"] = dict(q3=span(q3), pin_a=span(qa), pin_b=span(qb))
    # arm pad on the arm: pad centre in the humerus (arm) frame
    Bm = fr["Bm"]; Z = M.Z; i0 = taken[0] if taken else 0
    out["pad"] = dict(home_dist_from_GH=round(float(np.linalg.norm(Bm)), 1), tr=round(float(tr), 2),
                      c3_dist_from_GH=round(float(np.linalg.norm(c[2])), 1), pad_minus_c3=[round(float(x), 1) for x in (Bm - c[2]) @ np.stack([D.sa, D.st, sn], 1)])
    return out, set(bad_close) | set(bad_kh3) | set(bad_boss)


def main():
    outp = sys.argv[1]; P = json.loads(sys.argv[2]) if len(sys.argv) > 2 else dict(ROW["best_params"])
    t0 = time.time(); M, B, fit, M1 = frozen_model(P)
    r = M.run(); model = {k: r[k] for k in KEYS}
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "skin", "parts", "contact")}
    aud0 = MK.audit(M, B)
    ex, bad = extra_checks(M, B)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}
    aud = MK.audit(M, B)                                         # near-touch / overhead on the corrected set
    B.res = res0
    out = dict(params=P, mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", fit_fast=fit, model=model, why=why,
               model_audit=aud0, extra=ex, corrected=corrected, corrected_audit=aud, secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(mode=B.mode, fit=fit, model=model, corrected=corrected, near1=aud["gap_near1"], extra={k: ex[k] for k in ("closure_max", "closure_bad_poses", "knee_vs_hub3_upper_bad", "boss_bad", "spans_deg", "pad")}, secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main()
