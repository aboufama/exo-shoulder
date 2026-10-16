"""Adversarial verifier for offset-skin-normal-3r (2026-10-16). Re-measures one configuration with the model's own
checks (S.VModel + the osn additions) plus the verifier's:

  * outer-face skin check: hub crown discs (hubs 1-3), strap TOPS (links 1-2, neck, bridge) and the stage box tops are
    checked for skin contact (the model checks only undersides, side walls and box edges);
  * link 2 vs member 3 (neck, bridge, carriage B): adjacent pair via J3, running clearance (0.15 mm, VModel.ADJ);
  * near-touch: lowest metal over the poses taken (incl. the contact-only samples), the gap with metal < 1 mm (and
    < 2 mm) counted as contact;
  * overhead split: reach and in-band over the poses with elevation >= 140 deg;
  * frozen shape (lesson c): fit on Bench(60,160) FAST (the claimed shape, every fitted height, slide ranges and stage
    centre frozen), worn on the big bench without refit.

    python3 docs/concepts/verify/offset-skin-normal-3r.py <task> <out.json> ['<json params>']
      task: osn60 | osnbig_refit | osnbig_frozen | champ60 | champbig_refit | champbig_frozen
      (CB_EXACT=1 in the environment for the exact path; the frozen fit bench is always the fast grid)
The champion = the seed VModel with slides=0: the champion's axis directions (r20 s1414 #4), arm-fixed hub-3 block +
8 x 25 neck, same part sizes, fitting, pose rules and checks.
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m


OSN = _load("osn_model", os.path.join(REPO, "docs", "concepts", "models", "offset-skin-normal-3r.py"))
S = OSN.S
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "offset-skin-normal-3r.json")))
CHAMP = dict(slides=0, vfix=1, jam_contact=1, drop=1)


def bench(nc, nw, fast=False):
    old = os.environ.get("CB_EXACT")
    if fast and old is not None: del os.environ["CB_EXACT"]
    try:
        return CB.Bench(n_clip=nc, n_ws=nw)
    finally:
        if fast and old is not None: os.environ["CB_EXACT"] = old


def model_cls(champ): return S.VModel if champ else OSN.Model


def frozen_model(champ, Bbig, P):
    """fit on Bench(60,160) fast, then wear that shape on Bbig without refit"""
    B1 = bench(60, 160, fast=True); M1 = model_cls(champ)(B1, dict(P)); r1 = M1.run()
    fitrep = {k: r1[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}; fitrep["mode"] = B1.mode
    P2 = dict(M1.p); P2["S_auto"] = 0
    Base = model_cls(champ)

    class Frozen(Base):
        def __init__(self, B, params):
            super().__init__(B, params)
            if not champ:                                         # osn: slide ranges + stage centre as fitted, kin re-gated
                self.p["S_a"], self.p["S_t"], self.p["R_r"] = M1.p["S_a"], M1.p["S_t"], M1.p["R_r"]; self.D.m = M1.D.m.copy()
                q, ok, X1, X2, X3, s = self.D.ik(self.Q); self.s = s
                self.why = np.array([""] * len(B.idx), dtype=object); okf = ok.copy(); self.why[~ok] = "fold"
                sok = self.D.slides_ok(s); self.why[ok & ~sok] = "slide"; okf &= sok
                cont = self.continuity(); self.why[okf & ~cont] = "flip"; okf &= cont
                bad = okf & (self.res_deg >= 0.5); self.why[bad] = "closure"; okf &= ~bad; self.kin_ok = okf

        def fit(self):
            for a in ("geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "contact", "cyl", "box", "strap", "cyl_surf",
                      "riser", "riser_h", "riser_pts", "box_strip", "Hneed", "Lneed"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact)
            self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    M = Frozen(Bbig, P2)
    return M, fitrep


def outer_samples(M, champ):
    """(member, points) of the outward faces: hub crown discs, strap tops, box tops"""
    D = M.D; u, c = D.u, D.c; F = M.f; out = []
    for k, mem in ((0, 0), (1, 1), (2, 5 if champ else 3)):
        e, f = S.frame_of(u[k]); d = S.disc(S.HUB_R, 2.0)
        out.append(("crown%d" % (k + 1), mem, c[k] + (F[k] + S.CROWN) * u[k] + d[:, :1] * e + d[:, 1:] * f))
    for nm, (mem, pts) in M.link_pts.items():
        if len(pts): out.append((nm + "top", mem, pts + S.T_LINK * S.unit(pts)))
    for nm in ("neck", "bridge"):
        if nm in M.rigid:
            mem, pts = M.rigid[nm]; out.append((nm + "top", mem, pts + S.T_LINK * D.u[2]))
    if not champ:
        cs = D.stage_c(); sa, st, sn = D.sa, D.st, D.sn; P = D.p; tr = M.tr; z1 = tr + S.RAIL_H + S.RUN
        def top(mem, L, W, z): r = S.rect(L, W); return (mem, cs + r[:, :1] * sa + r[:, 1:] * st + z * sn)
        for nm, (mem, X) in dict(carAtop=top(4, S.CAR_L, S.CAR_W + 2 * P["S_t"], z1 + S.CAR_H),
                                 striptop=top(4, S.CAR_L + 2 * P["S_a"], S.RAIL_W, z1 + S.CAR_H),
                                 carBtop=top(3, S.CAR_L, S.CAR_W, M.zb + S.CAR_H)).items():
            out.append((nm, mem, X))
    return out


def l2_vs_member3(M, i):
    """link 2 (member 2) vs member 3's neck / bridge / carriage B (adjacent via J3): clearance estimate (mm)"""
    D = M.D; R2, t2 = M.T(2, i); R3, t3 = M.T(3, i)
    mem, L2 = M.strap["L2"]; Pw = L2 @ R2.T + t2                           # strap mid-surface
    res = {}
    for nm in ("neck", "bridge"):
        if nm in M.rigid:
            m3, X = M.rigid[nm]; mid = (X + 0.5 * S.T_LINK * D.u[2]) @ R3.T + t3
            from scipy.spatial import cKDTree
            res["L2-" + nm] = float(cKDTree(mid).query(Pw)[0].min()) - S.T_LINK
    if getattr(M, "box", None) and "carB" in M.box:
        mb, cen, half = M.box["carB"]; Rst = np.stack([D.sa, D.st, D.sn], 1)
        res["L2-carB"] = float(M.sd_box(Pw, R3 @ cen + t3, R3 @ Rst, half).min()) - S.T_LINK / 2
    return res


def audit(M, B, r, champ):
    """the verifier's added checks on a run model M (B.res filled by M.run)"""
    taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
    out = {}
    # 1. outer faces vs skin
    OS = outer_samples(M, champ); hit = {}; low_outer = []
    for i in range(len(B.idx)):
        if not taken(i): continue
        worst = (1e9, None)
        for nm, mem, X in OS:
            d = float(B.dist(i, M.world(mem, i, X)).min())
            if d < worst[0]: worst = (d, nm)
        low_outer.append((worst[0], i, worst[1]))
        if worst[0] < 0: hit[i] = worst
    low_outer.sort()
    out["outer_low"] = [dict(mm=round(d, 2), part=nm, i=int(i), plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"]) for d, i, nm in low_outer[:6]]
    out["outer_contact_poses"] = len(hit)
    # 2. link 2 vs member 3 (osn only)
    adj = []
    if not champ:
        for i in range(len(B.idx)):
            if not taken(i): continue
            v = l2_vs_member3(M, i)
            if v: k = min(v, key=v.get); adj.append((v[k], i, k))
        adj.sort()
        out["L2_member3_low"] = [dict(mm=round(d, 2), pair=k, i=int(i), plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"]) for d, i, k in adj[:6]]
    jam = {i for d, i, k in adj if d < M.ADJ}
    out["L2_member3_jams"] = len(jam)
    # corrected report: outer contact -> contact, adjacent jam -> not taken
    res0 = list(B.res)
    for i in jam: B.res[i] = None
    for i, (d, nm) in hit.items():
        if B.res[i] is not None: B.res[i] = np.r_[B.res[i], d]
    rc = B.report(); out["corrected"] = {k: rc[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}
    # 3. near-touch on the corrected set: the lowest metal incl. contact-only and outer samples
    mins = []
    for i in range(len(B.idx)):
        if not taken(i): continue
        dmin = float(np.min(B.res[i]))
        dc = min(float(B.dist(i, M.world(m, i, Pc)).min()) for m, Pc in M.contact) if M.contact else 1e9
        do = min(float(B.dist(i, M.world(mem, i, X)).min()) for nm, mem, X in OS)
        mins.append((min(dmin, dc, do), i))
    mins.sort(); out["near_touch_min_mm"] = round(mins[0][0], 2) if mins else None
    out["near_touch_low"] = [dict(mm=round(d, 2), i=int(i), plane=B.poses[i]["plane"], elev=B.poses[i]["elev"], axial=B.poses[i]["axial"], kind=B.kind[i]) for d, i in mins[:6]]
    res1 = list(B.res)
    for thr in (1.0, 2.0):
        for d, i in mins:
            if d < thr: B.res[i] = np.r_[B.res[i], -1e-3]
        rn = B.report(); out[f"gap_near{int(thr)}"] = rn["gap"]; out[f"near{int(thr)}_poses"] = int(sum(1 for d, i in mins if d < thr))
        B.res = list(res1)
    # 4. overhead split (elev >= 140) on the corrected set
    el = np.array([p["elev"] for p in B.poses]); kind = np.array(B.kind)
    ws = np.nonzero((el >= 140) & (kind == "ws"))[0]; cl = np.nonzero((el >= 140) & (kind == "clip"))[0]; allh = np.nonzero(el >= 140)[0]
    tk = [i for i in allh if taken(i)]; d = np.concatenate([B.res[i] for i in tk]) if tk else np.zeros(0)
    tkc = [i for i in cl if taken(i)]; dc_ = np.concatenate([B.res[i] for i in tkc]) if tkc else np.zeros(0)
    out["overhead140"] = dict(ws=len(ws), ws_taken=int(sum(taken(i) for i in ws)), reach=round(float(np.mean([taken(i) for i in ws])), 4) if len(ws) else None,
                              clip=len(cl), clip_taken=len(tkc), follow=round(float(len(tkc) / len(cl)), 4) if len(cl) else None,
                              inband14_all=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None,
                              inband10_all=round(float(((d >= 2) & (d <= 10)).mean()), 4) if len(d) else None,
                              inband14_clip=round(float(((dc_ >= 2) & (dc_ <= 14)).mean()), 4) if len(dc_) else None,
                              why_not={k: int(sum(1 for i in allh if not taken(i) and M.why[i] == k)) for k in ("fold", "slide", "flip", "closure", "skin", "parts", "contact", "")})
    B.res = res0
    return out


def main():
    task, outp = sys.argv[1], sys.argv[2]
    P = json.loads(sys.argv[3]) if len(sys.argv) > 3 else dict(ROW["best_params"])
    champ = task.startswith("champ"); P = dict(CHAMP) if champ else P
    t0 = time.time(); out = dict(task=task, params=P, exact=os.environ.get("CB_EXACT") == "1")
    if task.endswith("60"):
        B = bench(60, 160); M = model_cls(champ)(B, dict(P))
    else:
        B = bench(110, 360)
        if task.endswith("frozen"): M, out["fit"] = frozen_model(champ, B, P)
        else: M = model_cls(champ)(B, dict(P))
    r = M.run(); out["mode"] = B.mode; out["bench"] = [len([k for k in B.kind if k == "clip"]), len([k for k in B.kind if k == "ws"])]
    out["model"] = {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "why", "parts_pairs", "parts_ib14", "f",
                                         "res_max", "min_clear_taken", "riser_h", "jam_fixed")}
    out["S"] = [M.p.get("S_a"), M.p.get("S_t"), M.p.get("R_r")]
    if not champ and M.kin_ok.any():
        out["slide_used"] = [round(float(np.abs(M.s[M.kin_ok][:, k] - M.D.m[k]).max()), 2) for k in range(3)]
        out["radial_span"] = round(float(np.ptp(M.s[M.kin_ok][:, 2])), 4)
    out["audit"] = audit(M, B, r, champ); out["secs"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(os.path.abspath(outp)), exist_ok=True)
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(task=task, mode=out["mode"], model={k: out["model"][k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")},
                          corrected=out["audit"]["corrected"], near1=out["audit"]["gap_near1"], secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main()
