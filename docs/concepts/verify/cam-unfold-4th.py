"""Independent verifier (skeptic) for cam-unfold-4th (2026-10-16).

The model docs/concepts/models/cam-unfold-4th.py is imported UNCHANGED. This harness re-runs the frozen protocol (shape fitted on
Bench(60,160) FAST, worn without refit on Bench(110,360) EXACT, fold margin 5, O20 only) and adds checks written here,
independent of the model's closed form, on every taken pose of the worn bench:
  * per-joint rotation axes from the member frames: link 1 about u1, link 2a vs link 1 about u2, link 2b vs 2a about uK,
    member 3 vs 2b about u3, hub 3 centre carried by 2b = by member 3, knee pins a / b coincide, knee rotations about sn;
  * THE CAM LAW (R17, 3 active): q2 and dK are read back from the member frames; dK must equal sign(psiA) c(x(q2)) within
    0.1 deg (K is a single-valued function of J2's own angle, so the three joint readings determine the pose) and x(q2) must lie
    inside the J2 dowel slot (the window);
  * the effective-dyad fold margin re-computed from the frames: th = angle(J1 axis, J3 world axis), a2e = angle(u2, RK u3),
    min(th - |a1 - a2e|, a1 + a2e - th) >= 5; K's interior angle in [5, 175];
  * transmission: dth/dx at the pose by finite difference of the chain (own code) >= the model's floor gmin;
  * the cam's slope |dc/dx| at the taken poses and the pressure angle it implies for a crown ring of radius cam_r (reported).
Failing poses are knocked out and the bench re-scored. Near-touch (metal < 1 mm = contact) from the pin knee's audit.

Variants (hardware red team):
  claim : the claim's best_params as committed (crown cam: hub 2 crown +3 mm).
  hw    : the hardware the claim leaves out. (a) The O20 v5 crown is the UPPER member's cap (link 2a at J2), so a groove fixed to
          link 1 on the crown needs link 1's pin through the cap and the follower lever of 2a ABOVE the ring: ring 3 + lever 2
          = hub 2 crown +5 mm. (b) The 4-6 mm crank of link 2b sits inside hub K's O20 footprint, so it rides on hub K's cap with
          the rod eye: hub K crown +3 mm. Shape re-fitted with this hardware on Bench(60,160) fast, then frozen.

    CB_EXACT=1 CB_FOLD_MARGIN=5 OMP_NUM_THREADS=1 python3 docs/concepts/verify/cam-unfold-4th.py wear <claim|hw> out.json
"""
import importlib.util, json, math, os, sys, time
import numpy as np
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
import concept_kit as KIT                                    # noqa: E402

_sp = importlib.util.spec_from_file_location("camunfold_model_v", os.path.join(REPO, "docs", "concepts", "models", "cam-unfold-4th.py"))
CM = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CM)
S, PK, KB = CM.S, CM.PK, CM.KB
ROW = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "cam-unfold-4th.json")))
KEYS = ("gap", "reach", "follow", "inband14", "inband10", "contact")
D2R = math.pi / 180


class _CapV(tuple):
    pass


def cap_extra(Mo, name, dh):
    """verifier's own crown cap (hub `name` dh mm taller): part-part cylinder crown, crown samples, skin-contact rings"""
    if dh <= 0: return
    r0 = float(Mo.cyl_r[name]); crown0 = getattr(Mo.cyl_r[name], "crown", S.CROWN)
    r = CM._RC(r0); r.crown = crown0 + dh; Mo.cyl_r = dict(Mo.cyl_r); Mo.cyl_r[name] = r
    base = Mo.sd_cylr
    def sd_cyl(Pw, cen, ax, r=None):
        rr = max(Mo.hr) if r is None else r
        return base(Pw, cen, ax, rr, getattr(rr, "crown", S.CROWN))
    Mo.sd_cyl = sd_cyl
    mem, cen, ax = Mo.cyl[name]; e, f = S.frame_of(ax); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); H = r.crown
    pts = [cen + z * ax + r0 * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in np.linspace(0, H, 8)]
    dd = S.disc(r0, 4.0); pts.append(cen + H * ax + dd[:, :1] * e + dd[:, 1:] * f); Mo.cyl_surf = dict(Mo.cyl_surf); Mo.cyl_surf[name] = (mem, np.concatenate(pts))
    ang32 = np.linspace(0, 2 * np.pi, 32, endpoint=False); ring = r0 * (np.cos(ang32)[:, None] * e + np.sin(ang32)[:, None] * f)
    extra = [_CapV((mem, cen + z * ax + ring)) for z in np.linspace(crown0, H, 3)]
    dd2 = S.disc(r0, 2.0); extra.append(_CapV((mem, cen + H * ax + dd2[:, :1] * e + dd2[:, 1:] * f)))
    Mo.contact = [c for c in Mo.contact if not isinstance(c, _CapV)] + extra


def make_cls(dhK):
    class VCM(CM.CModel):
        pass
    if dhK > 0:
        run0 = CM.CModel.run
        def run(self, B=None):
            fit0 = self.fit
            def fit_k(): fit0(); cap_extra(self, "hubK", dhK)
            self.fit = fit_k
            return run0(self)
        VCM.run = run
    return VCM


def params_for(variant):
    P = dict(CM.PARAMS, **ROW["best_params"]); P["near"] = 1
    dhK = 0.0
    if variant == "hw": P["cam_h"] = 5.0; dhK = 3.0
    return P, dhK


def rot_axis_err(Rrel, ax):
    return math.degrees(math.acos(max(-1.0, min(1.0, float((Rrel @ ax) @ ax)))))


def signed_about(Rrel, ax):
    rv = Rot.from_matrix(Rrel).as_rotvec(); return float(np.degrees(rv @ ax))


def wrap180(a):
    return (a + 180.0) % 360.0 - 180.0


def chain_th(D, x):
    """own re-implementation: J1-J3 angle of the coupled chain at x (deg) from the cam law"""
    u1, u2, u3 = D.u; c = D._c(np.array([x]))[0]; dK = np.sign(D.psiA) * c * D2R
    v3 = Rot.from_rotvec(D.uK * dK).apply(u3); p = Rot.from_rotvec(u2 * (D.q2f + D.d * x) * D2R).apply(v3)
    return math.degrees(math.acos(max(-1, min(1, float(p @ u1)))))


def extra_checks(M, B):
    D = M.D; P = D.p; u, c = D.u, D.c; sn = D.sn; fr = M.fr; m = KIT.FOLD_MARGIN
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    mx = dict(j1=0.0, j2=0.0, k=0.0, j3=0.0, hub3c=0.0, pin_a=0.0, pin_b=0.0, knee_rot=0.0, cam_law=0.0)
    bad = {"close": [], "cam": [], "slot": [], "margin": [], "psi": [], "gain": []}
    eff_m, gains, slopes, xs_ = [], [], [], []
    a1 = D.a1
    for i in taken:
        R1, _ = M.T(1, i); R2a, _ = M.T(7, i); R2b, t2 = M.T(2, i); R3, t3 = M.T(3, i); R6, t6 = M.T(6, i); R5, t5 = M.T(5, i)
        e = dict(j1=rot_axis_err(R1, u[0]), j2=rot_axis_err(R1.T @ R2a, u[1]), k=rot_axis_err(R2a.T @ R2b, D.uK),
                 j3=rot_axis_err(R2b.T @ R3, u[2]), hub3c=float(np.linalg.norm((R2b @ c[2] + t2) - (R3 @ c[2] + t3))),
                 pin_a=float(np.linalg.norm((R3 @ fr["A0"] + t3) - (R6 @ fr["A0m"] + t6))),
                 pin_b=float(np.linalg.norm((R6 @ fr["Bm"] + t6) - (R5 @ fr["Bm"] + t5))),
                 knee_rot=max(rot_axis_err(R3.T @ R6, sn), rot_axis_err(R6.T @ R5, sn)))
        q2 = signed_about(R1.T @ R2a, u[1]); dK = signed_about(R2a.T @ R2b, D.uK)
        x = wrap180(q2 - D.q2f) * D.d
        if x < -90: x += 360.0                                   # x grid runs -60 .. 240
        dK_law = float(np.sign(D.psiA) * D._c(np.array([x]))[0])
        e["cam_law"] = abs(wrap180(dK - dK_law))
        for k, v in e.items(): mx[k] = max(mx[k], v)
        if max(e["j1"], e["j2"], e["k"], e["j3"], e["knee_rot"]) > 0.5 or max(e["hub3c"], e["pin_a"], e["pin_b"]) > 0.5: bad["close"].append(i)
        if e["cam_law"] > 0.1: bad["cam"].append(i)
        if not (D.win[0] - 0.05 <= x <= D.win[1] + 0.05): bad["slot"].append(i)
        w3 = R2b @ u[2]; th = math.degrees(math.acos(max(-1, min(1, float(w3 @ u[0])))))
        a2e = math.degrees(math.acos(max(-1, min(1, float((R2a.T @ R2b @ u[2]) @ u[1])))))
        me = min(th - abs(a1 - a2e), min(a1 + a2e, 360 - a1 - a2e) - th); eff_m.append(me)
        if me < m - 0.05: bad["margin"].append(i)
        psi = abs(math.degrees(D.psiA)) + float(D._c(np.array([x]))[0])
        if not (m - 0.05 <= psi <= 180 - m + 0.05): bad["psi"].append(i)
        g = (chain_th(D, x + 0.25) - chain_th(D, x - 0.25)) / 0.5; gains.append(g)
        if g < D.gmin - 1e-3: bad["gain"].append(i)
        cc = D._c(np.array([x - 0.1, x + 0.1])); slopes.append(abs(float(cc[1] - cc[0])) / 0.2); xs_.append(x)
    knock = sorted(set(sum(bad.values(), [])))
    smax = max(slopes) if slopes else 0.0
    # pressure angle of a radial groove follower on the crown ring: the 44.5-deg total K travel on a 4 mm crank = 3.1 mm of
    # follower travel; the ring (radius cam_r) leaves pitch radii 4.5-7.2 mm for an O3 pin (O7 pin core + 1.3 wall + 1.5 half-groove)
    ktravel = float(np.ptp(D.tc)) if len(D.tc) else 0.0
    follow_mm_per_rad = 4.0 * 1.0                         # 4 mm crank, 1:1 lever: mm of follower per rad of K
    pa = {f"rp{rp}": round(math.degrees(math.atan(follow_mm_per_rad * smax / rp)), 1) for rp in (5.0, 7.0, 12.0)}
    return dict(n_taken=len(taken), knocked=len(knock), knocked_by={k: len(v) for k, v in bad.items()},
                max_err={k: round(v, 4) for k, v in mx.items()}, min_eff_margin=round(min(eff_m), 2) if eff_m else None,
                min_gain=round(min(gains), 3) if gains else None, gmin=round(D.gmin, 3), cam_slope_max_taken=round(smax, 3),
                x_range_taken=[round(min(xs_), 1), round(max(xs_), 1)] if xs_ else None, window_x=[round(v, 1) for v in D.win],
                K_travel_deg=round(ktravel, 1), pressure_angle_deg_4mm_crank=pa), knock


def wear(variant, outp):
    t0 = time.time(); P, dhK = params_for(variant)
    old = os.environ.pop("CB_EXACT", None)
    try: B1 = CB.Bench(n_clip=60, n_ws=160)
    finally:
        if old is not None: os.environ["CB_EXACT"] = old
    Cls = make_cls(dhK)
    M1 = Cls(B1, dict(P)); r1 = M1.run(); fit = {k: r1[k] for k in KEYS}
    a1 = PK.audit(M1, B1); fit["gap_near1"] = a1["gap_near1"]
    P2 = dict(M1.p); P2["m_fix"] = [float(x) for x in M1.D.m]

    class Frozen(Cls):
        def fit(self):
            for a in ("g", "fr", "geo", "rigid", "link_pts", "f", "fK", "tr", "zb", "_tr_fit", "cyl", "box", "strap", "cyl_surf", "Emid",
                      "Hneed", "Lneed", "hEx", "_Ex", "_h12", "rod_pts"):
                if a in M1.__dict__: setattr(self, a, M1.__dict__[a])
            self.contact = list(M1.contact); self.poses_fit = np.nonzero(self.kin_ok)[0]; self.drop = np.zeros(len(self.poses_fit), bool)
    B = CB.Bench(n_clip=110, n_ws=360); M = Frozen(B, P2); r = M.run()
    model = {k: r[k] for k in KEYS}; aud0 = PK.audit(M, B)
    chk, knock = extra_checks(M, B)
    for i in knock: B.res[i] = None
    rc = B.report(); corrected = {k: rc[k] for k in KEYS}; aud = PK.audit(M, B)
    out = dict(variant=variant, bench=[110, 360], mode=B.mode, fold_margin=KIT.FOLD_MARGIN, fit_fast=fit, model_frozen=model,
               model_near1=aud0["gap_near1"], checks=chk, corrected=corrected, corrected_near1=aud["gap_near1"],
               near1_poses=aud["near1_poses"], min_metal_mm=aud["near_touch_min_mm"], near_low=aud["near_touch_low"],
               overhead140=aud["overhead140"], why={k: int(sum(1 for w in M.why if w == k)) for k in ("fold", "slide", "flip", "closure", "skin", "parts", "contact")},
               parts_pairs=r.get("parts_pairs"), parts_ib14=r.get("parts_ib14"),
               hub_crowns={k: round(float(getattr(v, "crown", S.CROWN)), 2) for k, v in M.cyl_r.items()},
               f=[round(float(x), 1) for x in M.f], fK=round(float(M.fK), 1), tr=round(float(M.tr), 1),
               score=round(100 * (1 - corrected["gap"] / 275), 2), secs=round(time.time() - t0, 1), params=P)
    json.dump(out, open(outp, "w"), indent=1, default=float); print(json.dumps({k: out[k] for k in ("variant", "mode", "fit_fast", "model_frozen", "corrected", "corrected_near1", "checks", "why", "hub_crowns", "secs")}, default=float))


if __name__ == "__main__":
    if sys.argv[1] == "wear": wear(sys.argv[2], sys.argv[3])
