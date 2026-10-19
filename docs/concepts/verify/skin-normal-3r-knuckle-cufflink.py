"""Adversarial verifier for skin-normal-3r-knuckle-cufflink (2026-10-16). Re-measures one configuration, frozen-shape
protocol (fit on Bench(60,160) FAST, worn on Bench(110,360) without refit; CB_EXACT=1 for the exact path), with the
model's own checks plus the verifier's:

  * independent 3D closure per taken pose (not the closed form the model solves with): the knuckle pin as carried by
    the crank vs by link 1 (point + axis), J2's line as carried by link 1 vs link 2, J3's line by link 2 vs the rotor,
    pin a as carried by the rotor vs by the cuff link (in-plane point; the along-axis offset must stay constant), pin b
    by the cuff link vs the arm, the rotor's axis vs the arm's;
  * the three PIN POSTS (knuckle post on the crank, pin a post on the rotor, pin b post on the arm pad) and the E-arm
    riser as solids in the part-part check - the model only skin-checks them: each vs every non-adjacent part (hubs as
    exact cylinders, plates / straps with their half thickness, other posts) at >= 1 mm; the rotor's pin a post vs link 2
    (adjacent at J3) at the 0.15 mm running gap;
  * the adjacent pairs the model never checks: E arm vs cuff link (away from pin a) and cuff link vs arm pad (away
    from pin b), 0.15 mm running gap;
  * the arm pad's place on the arm (distance from GH, along-humerus position) and the passive spans (knuckle, rotor
    turn psi, cuff elbow) over the taken poses;
  * the model's own red team on the corrected set (near-touch incl. walls / crowns / tops / posts, metal < 1 mm as
    contact, overhead >= 140, across the body, behind the back).

    OMP_NUM_THREADS=1 nice -n 10 CB_EXACT=1 python3 docs/concepts/verify/skin-normal-3r-knuckle-cufflink.py <out.json> ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

_spec = importlib.util.spec_from_file_location("knuckle_model", os.path.join(REPO, "docs", "concepts", "models", "skin-normal-3r-knuckle-cufflink.py"))
MK = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(MK)
S = MK.S
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "skin-normal-3r-knuckle-cufflink.json")))
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")
BOSS_R, T, HEAD, HUB_R = MK.BOSS_R, MK.T_LINK, MK.PIN_HEAD, MK.HUB_R


def frozen_model(P, nc=110, nw=360):
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    p1, _ = MK.evaluate(B1, P); M1 = MK.Model(B1, p1); r1 = M1.run(); fit = {k: r1[k] for k in KEYS}; fit["mode"] = B1.mode; fit["why"] = r1["why"]
    B = CB.Bench(n_clip=nc, n_ws=nw); M = MK.Frozen(B, M1)
    return M, B, fit, M1, p1


def post(o, ax, r, z0, z1):
    """solid post surface (side wall rings every 1.5 mm, 24 per ring + both caps), member-local"""
    e, f = S.frame_of(ax); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); ring = r * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f)
    pts = [o + z * ax + ring for z in np.linspace(z0, z1, max(2, int((z1 - z0) / 1.5) + 1))]
    dd = S.disc(r, 1.5)
    for z in (z0, z1): pts.append(o + z * ax + dd[:, :1] * e + dd[:, 1:] * f)
    return np.concatenate(pts)


def rot_angle_vec(a, b): return math.degrees(math.acos(max(-1.0, min(1.0, float(a @ b)))))


def extra_checks(M, B):
    D = M.D; P = M.p; u, c = D.u, D.c; sn = D.sn; lv = M.lv; h = T / 2
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    # ---- posts (member-local) ----
    kb = D.kc + D.e0; pa = c[2] + P["LE"] * D.eE; zl3 = lv["clink"] - P["k_c0"]
    posts = {"kpost": (4, post(kb, D.ku, BOSS_R, lv["crank"], lv["crank"] + 2 * T + 0.15 + HEAD), kb, D.ku),
             "apost": (3, post(pa, sn, BOSS_R, min(lv["Earm"], zl3), max(lv["Earm"], zl3) + T + HEAD), pa, sn),
             "bpost": (5, post(M.Pb3, sn, BOSS_R, lv["pad"], lv["clink"] + T + HEAD), M.Pb3, sn)}
    lo, hi = min(lv["h3"], lv["Earm"]), max(lv["h3"], lv["Earm"]) + T
    if hi - lo > T + 0.5:
        ew = np.cross(sn, D.eE); g = np.stack(np.meshgrid(np.linspace(-S.W_LINK / 2, S.W_LINK / 2, 5), np.arange(lo, hi + 0.1, 1.5),
                                                          np.linspace(HUB_R, HUB_R + T, 3), indexing="ij"), -1).reshape(-1, 3)
        posts["riser"] = (3, c[2] + g[:, 2:3] * D.eE + g[:, :1] * ew + g[:, 1:2] * sn, None, None)
    # required clearance per pair (post, part): non-adjacent 1 mm, adjacent 0.15 mm; pairs absent from this list are adjacent through the post's own pin
    need = {"kpost": dict(hub2=1.0, hub3=1.0, L2=1.0, Earm=1.0, clink=1.0, pad=1.0, apost=1.0, bpost=1.0, riser=1.0),
            "apost": dict(hub1=1.0, hub2=1.0, L1=1.0, crank=1.0, crankL=1.0, pad=1.0, L2=0.15, bpost=1.0),
            "bpost": dict(hub1=1.0, hub2=1.0, hub3=1.0, L1=1.0, L2=1.0, crank=1.0, crankL=1.0, Earm=1.0, riser=1.0),
            "riser": dict(hub1=1.0, hub2=1.0, L1=1.0, crank=1.0, crankL=1.0, pad=1.0, clink=0.15)}
    clo = dict(knuckle_pt=0.0, knuckle_ax=0.0, J2_line=0.0, J2_ax=0.0, J3_line=0.0, J3_ax=0.0, pin_a=0.0, pin_b=0.0, arm_ax=0.0)
    a_off = []; bad_close, bad_post, bad_adj = set(), set(), set(); low_post, low_adj = [], []
    def line_err(p_a, ax_a, p_b):
        w = p_b - p_a; return float(np.linalg.norm(w - (w @ ax_a) * ax_a))
    for i in taken:
        Tm = {m: M.T(m, i) for m in range(7)}
        tf = lambda m, X: X @ Tm[m][0].T + Tm[m][1]
        R1, t1 = Tm[1]; R4, t4 = Tm[4]; R2, t2 = Tm[2]; R3, t3 = Tm[3]; R5, t5 = Tm[5]; R6, t6 = Tm[6]
        e = dict(knuckle_pt=float(np.linalg.norm((R4 @ kb + t4) - (R1 @ kb + t1))), knuckle_ax=rot_angle_vec(R4 @ D.ku, R1 @ D.ku),
                 J2_line=line_err(R1 @ c[1] + t1, R1 @ u[1], R2 @ c[1] + t2), J2_ax=rot_angle_vec(R1 @ u[1], R2 @ u[1]),
                 J3_line=line_err(R2 @ c[2] + t2, R2 @ u[2], R3 @ c[2] + t3), J3_ax=rot_angle_vec(R2 @ u[2], R3 @ u[2]),
                 arm_ax=rot_angle_vec(R3 @ sn, R5 @ sn))
        A3 = R3 @ pa + t3; A6 = R6 @ (M.Pb3 - P["lc"] * D.eB) + t6; ax = R5 @ sn
        e["pin_a"] = line_err(A6, ax, A3); a_off.append(float((A3 - A6) @ ax))
        e["pin_b"] = float(np.linalg.norm((R6 @ M.Pb3 + t6) - (R5 @ M.Pb3 + t5)))
        for k, v in e.items(): clo[k] = max(clo[k], v)
        if max(e["knuckle_pt"], e["J2_line"], e["J3_line"], e["pin_a"], e["pin_b"]) > 0.5 or max(e["knuckle_ax"], e["J2_ax"], e["J3_ax"], e["arm_ax"]) > 0.5:
            bad_close.add(i)
        # parts in world (scapula frame)
        cylw = {k: (Tm[m][0] @ cen + Tm[m][1], Tm[m][0] @ axx) for k, (m, cen, axx) in M.cyl.items()}
        sl = {k: tf(m, X) for k, (m, X) in M.strap.items() if len(X)}
        pw = {k: tf(m, X) for k, (m, X, _, _) in posts.items()}
        worst = (1e9, None)
        for pn, req in need.items():
            if pn not in pw: continue
            Pp = pw[pn]
            for other, rq in req.items():
                if other in M.cyl: d = float(M.sd_cyl(Pp, *cylw[other]).min())
                elif other in sl: d = float(cKDTree(sl[other]).query(Pp)[0].min()) - h
                elif other in pw: d = float(cKDTree(pw[other]).query(Pp)[0].min())
                else: continue
                if d - rq < worst[0]: worst = (d - rq, f"{pn}-{other}", d)
                if d < rq: bad_post.add(i)
        if worst[1]: low_post.append((worst[2], worst[0], i, worst[1]))
        # adjacent plates never checked by the model: E arm vs cuff link (away from pin a), cuff link vs pad (away from pin b)
        A3w, axw = A3, ax
        def away(X, p0, r):
            w = X - p0; return X[np.linalg.norm(w - (w @ axw)[:, None] * axw, axis=1) > r]
        Ea, Cl, Pd = sl.get("Earm"), sl.get("clink"), sl.get("pad")
        dd = {}
        if Ea is not None and Cl is not None:
            a1, b1 = away(Ea, A3w, BOSS_R + 2), away(Cl, A3w, BOSS_R + 2)
            if len(a1) and len(b1): dd["Earm-clink"] = float(cKDTree(b1).query(a1)[0].min()) - 2 * h
        Pbw = R5 @ M.Pb3 + t5
        if Cl is not None and Pd is not None:
            a1, b1 = away(Cl, Pbw, BOSS_R + 2), away(Pd, Pbw, BOSS_R + 2)
            if len(a1) and len(b1): dd["clink-pad"] = float(cKDTree(b1).query(a1)[0].min()) - 2 * h
        if dd:
            k = min(dd, key=dd.get); low_adj.append((dd[k], i, k))
            if dd[k] < M.ADJ: bad_adj.add(i)
    lab = lambda i: dict(i=int(i), kind=B.kind[i], plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"])
    low_post.sort(key=lambda x: x[1]); low_adj.sort()
    K = M.K; ok = np.array(taken, int)
    out = dict(closure_max={k: round(v, 4) for k, v in clo.items()}, closure_bad=len(bad_close),
               pin_a_axial_offset_span=round(float(np.ptp(a_off)), 4) if a_off else None,
               posts_low=[dict(mm=round(d, 2), margin=round(mg, 2), pair=pr, **lab(i)) for d, mg, i, pr in low_post[:6]], posts_bad=len(bad_post),
               posts_bad_pairs={}, adj_low=[dict(mm=round(d, 2), pair=k, **lab(i)) for d, i, k in low_adj[:5]], adj_bad=len(bad_adj),
               post_sizes={k: [int(v[0]), int(len(v[1]))] for k, v in posts.items()})
    if len(ok):
        out["spans_deg"] = dict(knuckle=[round(float(np.degrees(K["qk"][ok]).min()), 1), round(float(np.degrees(K["qk"][ok]).max()), 1)],
                                psi=[round(float(np.degrees(K["psi"][ok]).min()), 1), round(float(np.degrees(K["psi"][ok]).max()), 1)],
                                elbow=[round(float(K["gam"][ok].min()), 1), round(float(K["gam"][ok].max()), 1)])
        out["knuckle_auth_mm_per_rad"] = dict(p1=round(float(np.percentile(K["auth"][ok], 1)), 2), min=round(float(K["auth"][ok].min()), 2))
        out["liner_3mm_swing_deg_at_min_auth"] = round(math.degrees(3.0 / max(float(K["auth"][ok].min()), 1e-6)), 1)
    # arm pad on the arm: the humerus axis in the arm frame = the rest arm's GH -> elbow direction; pad centre position
    out["pad"] = dict(dist_from_GH=round(float(np.linalg.norm(M.Pb3)), 1), c3_dist_from_GH=round(float(np.linalg.norm(c[2])), 1),
                      levels=M.lv, pad_minus_c3_sa_st_sn=[round(float(x), 1) for x in (M.Pb3 - c[2]) @ np.stack([D.sa, D.st, sn], 1)])
    return out, bad_close | bad_post | bad_adj


def main():
    outp = sys.argv[1]; P = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {k: v for k, v in ROW["best_params"].items()}
    t0 = time.time(); M, B, fit, M1, p1 = frozen_model(P, int(os.environ.get("V_NC", 110)), int(os.environ.get("V_NW", 360)))
    print("fit60", fit, flush=True)
    r = M.run(); model = {k: r[k] for k in KEYS}; model["why"] = r["why"]; model["parts_pairs"] = r.get("parts_pairs"); model["parts_ib14"] = r.get("parts_ib14")
    print("frozen model", B.mode, model, flush=True)
    ex, bad = extra_checks(M, B)
    print("extra", json.dumps(ex, default=float), flush=True)
    for i in bad: B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}
    print("corrected", corrected, flush=True)
    aud = MK.redteam(B, M, rc)                                    # near-touch / overhead / groups on the corrected set
    out = dict(params=P, design={k: p1.get(k) for k in ("alk", "k_c0", "k_sk", "k_mid", "cuff_m", "cuff_sig")}, mode=B.mode,
               exact=os.environ.get("CB_EXACT") == "1", fit_fast=fit, model=model, extra=ex, removed=sorted(int(i) for i in bad),
               corrected=corrected, corrected_redteam=aud, secs=round(time.time() - t0, 1))
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(mode=B.mode, fit=fit, model=model, corrected=corrected, near1=aud["gap_near1"], near_min=aud["near_min"], secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main()
