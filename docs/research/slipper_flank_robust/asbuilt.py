"""Question A of the slipper flank-robustness task: is the crank-side cliff physical or a synthesis artefact?

The flank is HELD FIXED as synthesised for the verified (nominal) config (the model's own spherical cam construction,
re-run here on a 0.005-deg K grid from the extracted geometry docs/research/slipper_mechanism/geo_bench.npz, the
verified config worn through the claim's model). Then the CRANK is built with an as-built error and the real contact is
solved: for each crank angle phi (set by the lobe), K settles where the spring closes link 1a onto the nose, i.e. at the
smallest K >= 0 (stop A) whose nose circle clears the fixed flank (signed clearance 0). Nothing is re-synthesised.

As-built errors (one at a time):
  r_c    : the nose centre moved radially from K's axis by +-0.1 / +-0.2 mm (nose hole position on the crank);
  beta   : the nose centre rotated about K's axis by +-0.25 / +-1 deg (+-0.067 / +-0.27 mm at r_c 15.37);
  pivot  : the crank pivot (and the whole crank with it) moved +-0.05 mm, along the arm (e1) and across it (e2);
  g      : the lobe lifts the follower for ratio g' = g +- 0.02 (the flank stays conjugate to g: the crank turns
           phi = dK_law / g', K = flank(phi)); physically a 0.84 % lobe-lift / follower-arm error (0.034 mm on the
           model's s_arm 4.0, 0.055 mm on the real a_s 6.5 follower arm).
Per case: K error over the law (deg), K at rest (the crank floats back up to 0.9 deg on the follower's 0.1 mm dwell
gap), the drive stroke (K at the q2 stop B and the K where the as-built PA first passes its cap), crank and horn PA
(kinematic, at the real contact normal) against 38.03 and 43 - atan(mu) at mu 0.087 / 0.12, and the per-pose fold
margin th (the red team's exact re-solve on the slaved law, drive.py fold_rows, with the as-built K(law) instead of a
constant offset), bench and held out.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/research/slipper_flank_robust/asbuilt.py [out.json]
"""
import json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
GEO = os.path.join(REPO, "docs", "research", "slipper_mechanism")
Z = np.load(os.path.join(GEO, "geo_bench.npz")); g = {k: Z[k] for k in Z.files}
ZH = np.load(os.path.join(GEO, "geo_held.npz")); gh = {k: ZH[k] for k in ZH.files}
D, R_ = math.degrees, math.radians


def unit(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)


def rotm(ax, a):
    ax = ax / np.linalg.norm(ax); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def rotms(ax, a):
    a = np.asarray(a, float); ax = ax / np.linalg.norm(ax); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3)[None] + np.sin(a)[:, None, None] * K[None] + (1 - np.cos(a))[:, None, None] * (K @ K)[None]


def ang(a, b): return D(math.acos(max(-1.0, min(1.0, float(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))))))


u1, u2, u3, uK, dR, PV, C0 = g["u1"], g["u2"], g["u3"], g["uK"], g["dR"], g["PV"], g["C0"]
sp, sig, gg, cc = float(g["sp"]), float(g["sig"]), float(g["gg"]), float(g["cc"])
HUB_R, UP, T_LINK, CROWN, RUN, W_LINK, bk1, bk2, a1max, kK, r_c, beta, s_arm, r_lobe, hl, lift, g_, zr, ang_min, NR, MU = [float(x) for x in g["consts"]]
dK_lim = D(float(g["dK_lim"])); R0 = float(np.linalg.norm(C0))
CAP = 43.0 - D(math.atan(0.087)); CAP12 = 43.0 - D(math.atan(0.12))
assert abs(cc) < 1e-12


def vH(X): return -sp * np.cross(uK, X)


# ---------------- the nominal flank (the model's construction), K from -4 to 54 deg, both directions from rest ----------------
STEP = 0.005
kg = np.radians(np.arange(-4.0, 54.0 + 1e-9, STEP)); nk = len(kg); j0 = int(round(4.0 / STEP))
phi = kg / gg; dphi = 1.0 / gg
Rk = rotms(uK, sp * kg); Rc = rotms(dR, sig * phi)
Cg = np.einsum("nij,j->ni", Rc, C0 - PV) + PV
ng = np.zeros((nk, 3)); pac = np.zeros(nk); pah = np.zeros(nk)


def _norm_at(j, nprev):
    C = Cg[j]; vC = sig * dphi * np.cross(dR, C); vr = vC - vH(C); n = unit(np.cross(unit(C), vr))
    if nprev is None: n = n if n @ vH(C) >= 0 else -n
    else: n = n if n @ nprev >= 0 else -n
    return n, vC


for rng in (range(j0, nk), range(j0, -1, -1)):
    nprev = None
    for j in rng:
        n, vC = _norm_at(j, nprev); nprev = n; ng[j] = n
        pac[j] = ang(n, vC); pah[j] = ang(n, vH(Cg[j] + NR * n))
P1 = np.einsum("nij,nj->ni", Rk, Cg); N1 = np.einsum("nij,nj->ni", Rk, ng); F = P1 + NR * N1     # link 1a frame
kdeg = D(1) * kg
BUILT = (0.0, 51.75)                                      # the built flank (red team: dK 0 -> dK_lim + 2 deg run-out)
TREE = cKDTree(F)


def clearance(X):
    """signed clearance of nose circles centred at X (link 1a frame, n x 3) to the fixed flank: 0 = touching, < 0 = overlap"""
    Xs = unit(X) * R0                                      # radial ruled flank: compare on the mid shell
    d, j = TREE.query(Xs)
    s = -np.einsum("ni,ni->n", Xs - F[j], N1[j])            # = NR when X sits on the nominal centre path
    c = np.where(s >= 0, d, -d) - NR
    return c, j


def crank_C(phi_rad, dC=np.zeros(3), dP=np.zeros(3), dbeta=0.0, dr=0.0):
    """as-built nose centre (link 1b frame) at crank angle phi: nose moved radially dr / about uK dbeta, pivot moved dP"""
    C0b = C0.copy()
    if dr:
        rad = unit(C0b - (C0b @ uK) * uK); C0b = C0b + dr * rad
    if dbeta: C0b = rotm(uK, R_(dbeta)) @ C0b
    C0b = C0b + dC + dP; PVb = PV + dP
    Rp = rotms(dR, sig * np.atleast_1d(phi_rad))
    return np.einsum("nij,j->ni", Rp, C0b - PVb) + PVb, PVb


def solve(case, phis_deg, Kscan=np.arange(-2.0, 60.0 + 1e-9, 0.02)):
    """K(phi) by continuation: the smallest K >= 0 at which the nose clears the fixed flank, tracked from the float end"""
    out = []
    Kp = None
    for ph in phis_deg:
        C, PVb = crank_C(R_(ph), **case)
        C = C[0]
        X = np.einsum("nij,j->ni", rotms(uK, sp * np.radians(Kscan)), C)
        c, jj = clearance(X)
        # crossings - -> + (the spring closes K down to the first K whose clearance is >= 0 from above)
        ok = c >= 0
        if ok[0] and Kscan[0] < 0:
            pass
        # physical K: largest K below which every K... = the first index from the high end where clearance turns negative, + 1
        neg = np.nonzero(~ok)[0]
        if not len(neg): Kst = Kscan[0]
        else:
            jn = neg[neg <= (np.searchsorted(Kscan, Kp + 3.0) if Kp is not None else len(Kscan) - 1)]
            jn = jn.max() if len(jn) else neg.min()
            if jn + 1 >= len(Kscan): Kst = np.nan
            else:
                a, b = Kscan[jn], Kscan[jn + 1]
                for _ in range(30):
                    m = 0.5 * (a + b); cm, _ = clearance((rotm(uK, sp * R_(m)) @ C)[None])
                    if cm[0] >= 0: b = m
                    else: a = m
                Kst = b
        Kphys = max(0.0, Kst) if np.isfinite(Kst) else np.nan
        on_stop = np.isfinite(Kst) and Kst <= 0.0
        Kp = Kphys
        row = dict(phi=ph, K=Kphys, Kfree=Kst, on_stop=bool(on_stop))
        if np.isfinite(Kphys) and not on_stop:
            Xc = rotm(uK, sp * R_(Kphys)) @ C
            cm, j = clearance(Xc[None]); j = int(j[0])
            Xs = unit(Xc) * R0; n1 = unit(F[j] - Xs)                       # contact normal (link 1a), from the nose centre to the flank
            nb = rotm(uK, sp * R_(Kphys)).T @ n1                            # link 1b frame
            vC = sig * np.cross(dR, C - PVb); Q = C + NR * nb
            row.update(pa_crank=ang(nb, vC), pa_horn=ang(nb, vH(Q)), k_contact=float(kdeg[j]), off_flank=bool(not (BUILT[0] - 1e-9 <= kdeg[j] <= BUILT[1])),
                       push=bool(nb @ vC > 0 and nb @ vH(Q) > 0))
        out.append(row)
    return out


# ---------------- fold margin per taken pose with an as-built K(law): drive.py fold_rows, offset -> function of |dK_law| ----------------
def dm(th, a, b): return np.minimum(th - np.abs(a - b), np.minimum(a + b, 360 - a - b) - th)
def angv(a, B_): return np.degrees(np.arccos(np.clip(B_ @ a, -1, 1)))


def fold_rows(Zx, efun):
    tk_, dK_ = Zx["taken"], np.asarray(Zx["dK"], float)
    a1d, a2d = (D(float(Zx["a1"])) if float(Zx["a1"]) < 4 else float(Zx["a1"])), (D(float(Zx["a2"])) if float(Zx["a2"]) < 4 else float(Zx["a2"]))
    R2 = Zx["R2"]; b1 = ang(u1, uK)
    tsL, dKL, q2L = Zx["law_ts"], Zx["law_dK"], Zx["law_q2t"]
    tf = np.linspace(0, float(tsL[-1]), 4001); dKf = np.interp(tf, tsL, dKL); q2f = np.interp(tf, tsL, q2L)
    U3 = np.einsum("nij,j->ni", rotms(u2, q2f), u3); cf = angv(uK, U3)
    e = np.where(tf > 0, np.radians(efun(np.degrees(np.abs(dKf)))), 0.0)
    RK = rotms(uK, dKf + sp * e)
    J2 = RK @ u2; J3 = np.einsum("nij,nj->ni", RK, U3)
    thf = angv(u1, J3); a1e = angv(u1, J2); a2e = np.degrees(np.arccos(np.clip(np.einsum("ni,ni->n", J2, J3), -1, 1)))
    mf = np.minimum(dm(thf, b1, cf), dm(thf, a1e, a2e))
    own = []
    for i in np.nonzero(tk_)[0]:
        j3 = R2[i] @ u3; th_i = ang(u1, j3)
        if abs(dK_[i]) <= 1e-6:
            own.append(float(dm(np.array([th_i]), a1d, a2d)[0])); continue
        t_i = float(np.interp(abs(dK_[i]), np.abs(dKL), tsL))
        w = np.nonzero(np.abs(tf - t_i) <= R_(6.0))[0]; jj = w[int(np.argmin(np.abs(thf[w] - th_i)))]
        own.append(float(mf[jj]))
    own = np.array(own)
    return dict(min=round(float(own.min()), 3), lt5=int((own < 5 - 1e-6).sum()), lt5p5=int((own < 5.5 - 1e-6).sum()), n=int(len(own)))


# ---------------- run ----------------
if __name__ == "__main__":
    outp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "asbuilt.json")
    sel = np.arange(j0, nk); ktk = 46.3
    jt = sel[kdeg[sel] <= ktk]
    nominal_syn = dict(pa_crank_rest=round(float(pac[j0]), 2), pa_crank_max_taken=round(float(pac[jt].max()), 2), pa_horn_max_taken=round(float(pah[jt].max()), 2),
                       cap_kin=round(CAP, 2), dK_lim=dK_lim, R0=round(R0, 3), nose_r=NR, g=gg, r_c=r_c, beta=beta, kK=kK)
    e1 = unit((C0 - PV) - ((C0 - PV) @ dR) * dR); e2 = np.cross(dR, e1)
    CASES = {"nominal": ({}, gg)}
    for d in (-0.2, -0.1, -0.05, -0.02, 0.02, 0.05, 0.1, 0.2): CASES[f"r_c {d:+g} mm"] = (dict(dr=d), gg)
    for d in (-1.0, -0.5, -0.25, 0.25, 0.5, 1.0): CASES[f"beta {d:+g} deg"] = (dict(dbeta=d), gg)
    for d in (-0.05, 0.05):
        CASES[f"pivot e1 {d:+g} mm"] = (dict(dP=d * e1), gg); CASES[f"pivot e2 {d:+g} mm"] = (dict(dP=d * e2), gg)
    for d in (-0.02, 0.02): CASES[f"g {d:+g} (lobe)"] = ({}, gg + d)
    phis = np.r_[np.arange(-0.9, 0.0, 0.1), np.arange(0.0, 22.0 + 1e-9, 0.05)]
    res = dict(nominal_synthesis=nominal_syn, note=__doc__.split("\n\n")[0], cases={})
    for name, (case, gl) in CASES.items():
        rows = solve(case, phis)
        ph = np.array([r["phi"] for r in rows]); K = np.array([r["K"] for r in rows])
        # the law: |dK_law| = k; the lobe sets phi = k / g' (float at rest: phi in [-0.9, 0])
        rest = [r for r in rows if r["phi"] < 0]
        K_rest = float(np.nanmin([r["K"] for r in rest] + [K[ph == 0][0]]))
        kl = np.arange(0.0, dK_lim + 1e-9, 0.05)
        Kact = np.interp(kl / gl, np.radians(ph) * 0 + ph * math.pi / 180 * 0 + ph / 1.0 * 1.0 * (math.pi / 180) / (math.pi / 180), K) if False else np.interp(np.degrees(np.radians(kl) / gl), ph, K)
        err = Kact - kl
        tk = kl <= ktk
        on = [r for r in rows if r["phi"] >= 0 and "pa_crank" in r]
        # PA over the law's taken stroke (K_act <= taken max) and the K where the as-built PA first passes the cap
        pa_c = np.array([r["pa_crank"] for r in on]); pa_h = np.array([r["pa_horn"] for r in on]); Kon = np.array([r["K"] for r in on])
        inr = Kon <= ktk + 0.75
        over = (pa_c > CAP) | (pa_h > CAP)
        k_cap = float(Kon[np.argmax(over)]) if over.any() else None
        offf = [r for r in on if r.get("off_flank")]
        nopush = [r for r in on if not r.get("push")]
        efun = (lambda kk, kl=kl, err=err: np.interp(kk, kl, err))
        rr = dict(K_rest=round(K_rest, 3), K_at_phi0=round(float(K[ph == 0][0]), 3),
                  dead_band_phi=round(float(ph[(ph >= 0) & (K > 0)].min()), 2) if ((ph >= 0) & (K > 0)).any() else None,
                  K_err_taken=dict(min=round(float(err[tk].min()), 3), max=round(float(err[tk].max()), 3), at_5=round(float(np.interp(5, kl, err)), 3),
                                   at_20=round(float(np.interp(20, kl, err)), 3), at_45=round(float(np.interp(45, kl, err)), 3)),
                  stroke_at_stopB=round(float(np.interp(np.degrees(np.radians(dK_lim) / gl), ph, K)), 2),
                  pa_crank_max=round(float(pa_c[inr].max()), 2) if inr.any() else None, pa_horn_max=round(float(pa_h[inr].max()), 2) if inr.any() else None,
                  pa_crank_first=round(float(pa_c[0]), 2) if len(pa_c) else None,
                  margin_crank=round(CAP - float(pa_c[inr].max()), 2) if inr.any() else None,
                  margin_horn_mu087=round(CAP - float(pa_h[inr].max()), 2) if inr.any() else None,
                  margin_horn_mu012=round(CAP12 - float(pa_h[inr].max()), 2) if inr.any() else None,
                  K_where_pa_over_cap=k_cap, off_flank_rows=len(offf), no_push_rows=len(nopush),
                  k_contact_range=[round(float(min(r["k_contact"] for r in on)), 2), round(float(max(r["k_contact"] for r in on)), 2)] if on else None,
                  fold_bench=fold_rows(g, efun), fold_held=fold_rows(gh, efun),
                  table=[dict(phi=round(r["phi"], 2), K=round(r["K"], 3), pa_c=round(r.get("pa_crank", float("nan")), 2), pa_h=round(r.get("pa_horn", float("nan")), 2),
                              kc=round(r.get("k_contact", float("nan")), 2)) for r in rows[::20]],
                  err_law=dict(k=[round(float(x), 2) for x in kl[::20]], err=[round(float(x), 4) for x in err[::20]]))
        res["cases"][name] = rr
        print(f"{name:20s} Krest {rr['K_rest']:.3f} dead {rr['dead_band_phi']} err[{rr['K_err_taken']['min']:+.3f},{rr['K_err_taken']['max']:+.3f}] "
              f"@5 {rr['K_err_taken']['at_5']:+.3f} @45 {rr['K_err_taken']['at_45']:+.3f} stroke {rr['stroke_at_stopB']} "
              f"PAc {rr['pa_crank_max']} PAh {rr['pa_horn_max']} capK {k_cap} off {len(offf)} nopush {len(nopush)} kc {rr['k_contact_range']} "
              f"th b {rr['fold_bench']['min']} ({rr['fold_bench']['lt5']}) h {rr['fold_held']['min']} ({rr['fold_held']['lt5']})", flush=True)
    json.dump(res, open(outp, "w"), indent=1, default=float)
