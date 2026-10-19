"""Adversarial verifier for raglan-knee-3r (2026-10-16). Re-measures one configuration through the morphology's own model
(a private copy: pin-knee rules + raglan-routed links) and adds:

  * every pin-knee verifier check (docs/concepts/verify/skin-normal-3r-pin-knee.py, run on THIS model): independent 3D
    closure per taken pose (hub 3 centre, J3 rotation axis, pin a, pin b, knee axes), knee link vs hub 3 above its lower
    plate (>= 1 mm, non-adjacent), the E boss vs hubs 1, 2 / link 1 (>= 1 mm) and link 2 (0.15 mm), J3 / pin spans, pad
    place on the arm;
  * screw rank at every taken pose: the 5 chain screws (J1, J2, J3, pin a, pin b, world frame) and the arm's 3 GH
    rotations; mobility = 8 - rank(all 8) must be 3 and rank(chain) must be 5 (no undetermined passive coordinate;
    the arm's twist inside the chain's span); the smallest chain singular value is reported (distance to a fold);
  * the routed links as bars: effective planform radius (the turn's tangent length is clipped at 45 % of each leg, so rc
    shrinks), turn angle, length, inner-edge radius of the 8 mm strap; the CROSS-WIDTH height difference of each link
    (the model fits every one of the 4 sample rows to the skin on its own, so a station can be higher on one edge than
    on the other: a bank / twist a constant-section bent bar cannot have) and the FLAT-BAR variant (every station of a
    link at the highest of its rows: the buildable constant section) scored on the same bench;
  * the model's audit (near-touch incl. walls / crowns / tops / edges, metal < 1 / 2 mm as contact, overhead >= 140) on
    the corrected set; the dilution-corrected gap (routed links weighted at their great-circle sample count).

    OMP_NUM_THREADS=1 nice -n 10 [CB_EXACT=1] python3 docs/concepts/verify/raglan-knee-3r.py <fast60|big> <out.json> ['<json params>'] [--flat]
      fast60: Bench(60,160) (fast grid, or exact with CB_EXACT=1), fitted on that bench
      big:    Bench(110,360), shape FROZEN from the Bench(60,160) FAST fit (lesson c); CB_EXACT=1 for the exact path
      --flat: the flat-bar links (buildable constant section) instead of the per-row skin-fitted ones
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m


RK = _load("raglan_for_verifier", os.path.join(REPO, "docs", "concepts", "models", "raglan-knee-3r.py"))
V = _load("pk_verifier_for_raglan", os.path.join(HERE, "skin-normal-3r-pin-knee.py"))
V.MK = RK.PK; V.S = RK.S                                     # the pin-knee verifier's checks, run on the routed model
PK, S = RK.PK, RK.S; unit = S.unit; D2R = math.pi / 180
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "raglan-knee-3r.json")))
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")


def link_rows(M, flat=False):
    """the model's finalize link heights, per sample row (copied from PK.Model.finalize); flat=True puts every station at
    the highest of its kept rows (one constant 8 x 3 section, no bank)"""
    D = M.D; keep = ~M.drop; u, c = D.u, D.c; k = math.tan(S.RAMP * D2R); F = list(M.f)
    rL = {nm: [r[keep].max(0) if keep.any() else r.max(0) for r in rows] for nm, rows in M.Lneed.items()}
    lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): S.UP, ("L2", 2): S.UP}; out = {}
    for lk in M.geo.links:
        rr = []
        for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
            r = r.copy(); Sx = sarc
            for kk, end in ((lk["ka"], 0), (lk["kb"], -1)):
                idx = np.nonzero(keep_s)[0]
                if not len(idx): continue
                j = idx[0] if end == 0 else idx[-1]
                cen = c[kk] + F[kk] * u[kk]; den = float(dv[j] @ u[kk])
                rc = (cen @ u[kk] + lvl[(lk["name"], kk)]) / max(den, 0.2)
                r = np.maximum(r, rc - k * np.abs(Sx - Sx[j]))
            r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
            rr.append(r)
        same = all(len(lk["rows"][j][2]) == len(lk["rows"][0][2]) and np.allclose(lk["rows"][j][2], lk["rows"][0][2]) for j in range(len(rr)))
        H = np.array(rr) if same else None
        if flat and H is not None:
            K = np.array([lk["rows"][j][1] for j in range(len(rr))])
            top = np.where(K, H, -np.inf).max(0); top = np.where(np.isfinite(top), top, H.max(0))
            rr = [top.copy() for _ in rr]; H = np.array(rr)
        out[lk["name"]] = dict(mem=lk["mem"], rows=lk["rows"], r=rr, H=H)
    return out


def bank_report(M):
    """cross-width height difference of each link (rows at -3, -1, 1, 3 mm: 6 mm apart), stations where all rows exist"""
    rep = {}
    for nm, L in link_rows(M).items():
        H = L["H"]
        if H is None: rep[nm] = "rows do not share stations"; continue
        K = np.array([L["rows"][j][1] for j in range(len(L["r"]))]).all(0)
        if not K.any(): rep[nm] = None; continue
        dH = np.ptp(H[:, K], axis=0); ang = np.degrees(np.arctan2(dH, 6.0))
        rep[nm] = dict(stations=int(K.sum()), dH_max_mm=round(float(dH.max()), 2), dH_p95_mm=round(float(np.percentile(dH, 95)), 2),
                       dH_mean_mm=round(float(dH.mean()), 2), bank_max_deg=round(float(ang.max()), 1), bank_p95_deg=round(float(np.percentile(ang, 95)), 1))
    return rep


class FlatModel(PK.Model):
    """the same model with flat-bar links: every station of a link at the highest of its rows (constant section)"""
    def finalize(self):
        PK.Model.finalize(self)
        LR = link_rows(self, flat=True); self.link_pts = {}
        for nm, L in LR.items():
            pts = [dv[ks] * r[ks][:, None] for (dv, ks, _), r in zip(L["rows"], L["r"])]
            self.link_pts[nm] = (L["mem"], np.concatenate(pts) if pts else np.zeros((0, 3)))
        self._contact_only(); self._solids()


def frozen_model(P, cls, nc=110, nw=360):
    """lesson (c): fit on Bench(60,160) FAST, wear the exact shape (heights, knee centre m) on Bench(nc, nw)"""
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    M1 = cls(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in KEYS}; fit["mode"] = B1.mode
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(cls):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_h12"):
                if hasattr(M1, a): setattr(self, a, getattr(M1, a))
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=nc, n_ws=nw); M = Frozen(B, P2)
    return M, B, fit, M1


def screw_rank(M, B, taken, Lc=50.0):
    """instantaneous mobility of the closed loop scapula-J1-J2-J3-pin a-knee-pin b-arm-GH(3R) at every taken pose"""
    D = M.D; u, c = D.u, D.c; sn = D.sn; fr = M.fr
    mob, rch, smin, s6 = [], [], [], []
    def scr(p, w): w = unit(w); return np.r_[w, np.cross(p, w) / Lc]
    for i in taken:
        R1, t1 = M.T(1, i); R2, t2 = M.T(2, i); R3, t3 = M.T(3, i); R5, t5 = M.T(5, i)
        ch = np.stack([scr(c[0], u[0]), scr(R1 @ c[1] + t1, R1 @ u[1]), scr(R2 @ c[2] + t2, R2 @ u[2]),
                       scr(R3 @ fr["A0"] + t3, R3 @ sn), scr(R5 @ fr["Bm"] + t5, R5 @ sn)], 1)
        gh = np.stack([scr(np.zeros(3), e) for e in np.eye(3)], 1)
        sv_c = np.linalg.svd(ch, compute_uv=False); sv_a = np.linalg.svd(np.c_[ch, gh], compute_uv=False)
        tol = 1e-6 * sv_a[0]
        mob.append(8 - int((sv_a > max(tol, 1e-4)).sum())); rch.append(int((sv_c > max(tol, 1e-4)).sum()))
        smin.append(float(sv_c[-1] / sv_c[0])); s6.append(float(sv_a[5] / sv_a[0]) if len(sv_a) > 5 else 0.0)
    if not taken: return None
    return dict(poses=len(taken), mobility=sorted(set(mob)), chain_rank=sorted(set(rch)),
                chain_sigma_min_rel=dict(min=round(min(smin), 4), p5=round(float(np.percentile(smin, 5)), 4), median=round(float(np.median(smin)), 4)),
                sixth_sigma_rel_max=float(f"{max(s6):.2e}"),
                note="rank(chain) 5 = no undetermined passive coordinate; mobility 3 = the loop follows the arm; the 6th "
                     "singular value of all 8 screws ~0 = one redundant constraint (overconstrained by 1: J1, J2 through GH, pins parallel to J3)")


def main():
    task, outp = sys.argv[1], sys.argv[2]
    args = [a for a in sys.argv[3:] if not a.startswith("--")]; flat = "--flat" in sys.argv
    P = RK.clean(json.loads(args[0]) if args else dict(ROW["best_params"]))
    cls = FlatModel if flat else PK.Model; t0 = time.time()
    if task == "big":
        M, B, fit, M1 = frozen_model(P, cls)
    else:
        B = CB.Bench(n_clip=60, n_ws=160); M = cls(B, dict(P)); fit = None; M1 = None
    r = M.run(); model = {k: r[k] for k in KEYS}; Mfit = M1 if M1 is not None else M
    why = {k: int((M.why == k).sum()) for k in ("fold", "slide", "flip", "closure", "skin", "parts", "contact")}
    pc = [M.last_pair.get(i) for i in range(len(B.idx)) if M.why[i] == "parts"]
    aud0 = PK.audit(M, B)
    ex, bad = V.extra_checks(M, B)
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    scr = screw_rank(M, B, taken)
    res0 = list(B.res)
    for i in bad: B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}
    aud = PK.audit(M, B)
    pib = M.part_inband(); ri = getattr(Mfit.geo, "route_info", None) or {}
    w = {k: v[2] for k, v in pib.items()}
    for k, inf in ri.items():
        if k in w and inf.get("n_great_circle"): w[k] = inf["n_great_circle"]
    ib_fix = sum(w[k] * pib[k][0] for k in w) / max(1, sum(w.values()))
    corrected["gap_fixed_n"] = CB.gap_of(ib_fix, rc["follow"], rc["reach"], rc["contact"]); corrected["inband14_fixed_n"] = round(float(ib_fix), 4)
    B.res = res0
    route = {k: {kk: (float(vv) if isinstance(vv, (np.floating, float)) else vv) for kk, vv in v.items()} for k, v in ri.items()}
    for k, v in route.items():
        if isinstance(v.get("rc"), float): v["inner_edge_r_mm"] = round(v["rc"] - S.W_LINK / 2, 1)
    out = dict(task=task, flat=flat, params=P, mode=B.mode, exact=os.environ.get("CB_EXACT") == "1", bench=[len(B.idx)],
               fit_fast=fit, model=model, why=why, parts_pairs={k: pc.count(k) for k in set(pc)}, parts_ib14=pib,
               model_audit=aud0, extra=ex, extra_bad=len(bad), screw=scr, route=route, bank=bank_report(Mfit),
               corrected=corrected, corrected_audit=aud, f=[round(float(x), 2) for x in M.f], tr=round(float(M.tr), 2),
               secs=round(time.time() - t0, 1))
    json.dump(out, open(outp, "w"), indent=1, default=float)
    print(json.dumps(dict(task=task, flat=flat, mode=B.mode, fit=fit, model=model, corrected=corrected, near1=aud["gap_near1"],
                          near_min=aud["near_touch_min_mm"], over=aud["overhead140"], screw=scr, bank=out["bank"],
                          extra={k: ex[k] for k in ("closure_max", "closure_bad_poses", "knee_vs_hub3_upper_bad", "boss_bad", "spans_deg", "pad")},
                          secs=out["secs"]), default=float), flush=True)


if __name__ == "__main__":
    main()
