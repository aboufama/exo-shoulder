"""R10 for a girdle base WITH PASSIVE ELEMENTS between the user's scapula handler and J1 (and at the cuff): the
misalignment the chain actually sees. Design-side extension of judge/base_slip.py: the handler's slip (base_slip's
central / low / high laws, its lever, its error angles) is used UNCHANGED - only the mechanism that turns it into a
chain-centre error changes. Every source of error is an independent zero-mean vector (RSS, as base_slip's central
law); a translation of unknown direction is three orthogonal components of |d| / sqrt(3) (for the identity map this
gives |d|^2, base_slip's own rule). The seen error is LINEAR in the sources, so each mechanism is a set of 3x3 maps:
    seen = sum_j M_j v_j      ->   RSS = sqrt(sum_j |M_j v_j|^2)

Sources (scapula ISB frame, per frame of the clips' "want" poses):
  handler  v_UR, v_IR, v_PT = (R(axis, theta) - I) r and the 4.2 mm slip d (base_slip.angles, base_slip.lever)
  brace    the arm-side reference: the user's elbow stack / forearm cuff, hinged on the elbow (bony epicondyles), with
           the surface-cuff-vs-bone-pin errors of Hamming et al. 2012 (J Biomech 45:1161, n = 19, average absolute
           error): elevation 0..4 deg, plane of elevation 0..2 deg (both grown linearly with elevation to 150 deg),
           axial 5 deg (about the humeral axis: moves the GH estimate ~0), pivoting about the elbow, lever |GH - elbow|
           from the rig (325 mm); plus an elbow-axis translation d_E (0..3 mm, assumed - no published number found).
  humerus axis h in the scapula frame: Ludewig 2009 mean scapula angles (pipeline/girdle/opensim_seth/ludewig2009.py)
           composed ISB Y-X-Z (IR, -UR, PT for the right side) with the humerus direction from (plane, elevation).

Mechanisms (no active DOF anywhere; every passive element is set by closure through the arm):
  fixed        base rigid on the handler (base_slip's R10 number)                 seen = e_H
  slider_ideal one torque-free slider u on the handler, set perfectly             seen = (I - u u^T) e_H
  stage2_ideal two-axis planar stage (normal n), set perfectly                     seen = n n^T e_H
  stage3_brace three-axis stage, set by the brace (rigid cuff)                     seen = e_C
  slider_brace slider u set by the brace ALONG THE HUMERUS (the cuff has two passive slides across the arm; a soft
               centring spring rho = k_spring / k_tissue holds the slider where the closure cannot set it, u.h -> 0):
               g = (u.h) / (rho + (u.h)^2),  seen = (I - g u h^T) e_H + g u h^T e_C
  follower     three-axis stage set by a point follower pressed on a bony spot P of the scapula (e.g. the lateral
               acromion, right above the GH centre): seen = (R_err - I)(GH - P) + d_f  (d_f = the 4.2 mm slip law);
               or a two-axis stage across n, the handler holding the centre along n (follower(..., normal=n))
  calibrated   any of the above with the handler's error angles (and optionally its slip) scaled by f: the systematic
               part removed by a per-user calibrated passive law (double / multiple calibration of an acromion
               cluster: max errors 44.8 -> 14.2 deg in cadavers, f ~ 0.32 - Cereatti et al., Med Biol Eng Comput;
               Brochard 2011: double calibration ~ palpation on 5 of 6 axes)
    python3 judge/base_stage.py [design id]   -> table of every mechanism (fit clips / held-out clips) + pipeline/girdle/base_stage.json
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import base_slip as BS
sys.path.insert(0, os.path.join(HERE, "..", "pipeline", "girdle", "opensim_seth")); import ludewig2009 as LW
REPO = os.path.abspath(os.path.join(HERE, "..")); D2R = math.pi / 180; E3 = np.eye(3)
HAMMING = dict(elev=4.0, plane=2.0)                                  # deg, at maximal elevation (average absolute error)
D_ELBOW = 3.0                                                        # mm at 150 deg (assumed)


def Rx(a): return BS.rot(E3[0], a)
def Ry(a): return BS.rot(E3[1], a)
def Rz(a): return BS.rot(E3[2], a)


def scapula_R(plane, elev):
    """thorax <- scapula (ISB, right side) from Ludewig 2009 means, interpolated over the plane (0 / 40 / 90)"""
    pl = float(np.clip(plane, 0, 90)); th = float(np.clip(elev, 0, 150))
    keys = [("abduction", 0.0), ("scaption", 40.0), ("flexion", 90.0)]
    if th < 15: A = dict(LW.REST); B, _ = LW.angles("scaption", 15.0); A = {k: A[k] + (B[k] - A[k]) * th / 15 for k in A}   # rest -> 15 deg
    else:
        for (n0, p0), (n1, p1) in zip(keys, keys[1:]):
            if pl <= p1: w = (pl - p0) / (p1 - p0); a0, _ = LW.angles(n0, th); a1, _ = LW.angles(n1, th); A = {k: a0[k] + w * (a1[k] - a0[k]) for k in a0}; break
    return Ry(A["IR"] * D2R) @ Rx(-A["UR"] * D2R) @ Rz(A["PT"] * D2R)


def hdir_thorax(plane, elev):
    """GH -> elbow unit vector, ISB thorax (x anterior, y superior, z lateral); plane 0 abduction .. 90 flexion"""
    p, e = plane * D2R, elev * D2R; return np.array([math.sin(e) * math.sin(p), -math.cos(e), math.sin(e) * math.cos(p)])


def sources(W, law="central", f_ang=1.0, f_slip=1.0, r=None):
    """per frame: handler source vectors (T, 6, 3) [UR, IR, PT, d/sqrt3 x3], brace sources (T, 5, 3), h (T, 3), R_s (T, 3, 3)"""
    W = np.asarray(W, float); T = len(W); r = BS.lever()[0] if r is None else np.asarray(r, float)
    th, d = BS.angles(W[:, :2], law); th = th * D2R * f_ang; d = d * f_slip
    H = np.zeros((T, 6, 3)); C = np.zeros((T, 5, 3)); h = np.zeros((T, 3)); RS = np.zeros((T, 3, 3))
    L = np.linalg.norm(json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json")))["landmarks"]["elbow"])
    for t in range(T):
        for k in range(3): H[t, k] = (BS.rot(E3[k], th[t, k]) - E3) @ r
        H[t, 3:] = E3 * d[t] / math.sqrt(3)
        pl, el = W[t, 0], max(W[t, 1], 0.0); R = scapula_R(pl, el); RS[t] = R; ht = hdir_thorax(pl, el); h[t] = R.T @ ht
        u = min(el, 150.0) / 150.0; de, dp = HAMMING["elev"] * u * D2R, HAMMING["plane"] * u * D2R
        ae = np.cross(ht, E3[1]); ae = ae / np.linalg.norm(ae) if np.linalg.norm(ae) > 1e-6 else E3[0]
        lev = -L * ht                                                                           # GH - elbow (thorax)
        C[t, 0] = R.T @ ((BS.rot(ae, de) - E3) @ lev); C[t, 1] = R.T @ ((Ry(dp) - E3) @ lev)
        C[t, 2:] = E3 * D_ELBOW * u / math.sqrt(3)
    return H, C, h, RS


PERP = None                                                          # (T, 3) unit h: rss() then reports only the part across the humerus
def rss(maps_srcs):
    """sqrt(sum_j |M v_j|^2) over (M (T,3,3) or (3,3), V (T,J,3)) pairs (across the humerus only when PERP is set)"""
    tot = 0.0
    for M, V in maps_srcs:
        MV = np.einsum("tij,tkj->tki", M, V) if np.ndim(M) == 3 else np.einsum("ij,tkj->tki", M, V)
        if PERP is not None: MV = MV - np.einsum("tk,t->tk", np.einsum("tki,ti->tk", MV, PERP), np.ones(len(PERP)))[:, :, None] * PERP[:, None, :]
        tot = tot + (MV ** 2).sum((1, 2))
    return np.sqrt(tot)


def fib(n):
    i = np.arange(n) + 0.5; phi = np.arccos(1 - 2 * i / n); th = math.pi * (1 + 5 ** 0.5) * i
    U = np.c_[np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)]; return U[U[:, 2] >= 0]     # half sphere (u ~ -u)


def mech(name, H, C, h, u=None, rho=0.05, P=None, r=None, f=None):
    T = len(H)
    if name == "fixed": return rss([(E3, H)])
    if name == "slider_ideal": return rss([(E3 - np.outer(u, u), H)])
    if name == "stage2_ideal": return rss([(np.outer(u, u), H)])
    if name == "stage3_brace": return rss([(E3, C)])
    if name == "slider_brace":
        uh = h @ u; g = uh / (rho + uh ** 2); G = g[:, None, None] * np.einsum("i,tj->tij", u, h)
        return rss([(E3[None] - G, H), (G, C)])
    raise ValueError(name)


_FCACHE = {}
def follower(W, P, law="central", f_ang=1.0, f_slip=1.0, normal=None):
    """stage set by a point follower on the scapula at P (ISB scapula, relative to the acromion-flat anchor A); GH - P = r - P.
    normal None: 3-axis stage, seen = (R_err - I)(GH - P) + d_f. normal n: 2-axis stage across n - the handler holds the
    centre along n (where its lever makes it good), the follower sets the two directions across it:
    seen = n n^T (R_err - I) r + (I - n n^T)(R_err - I)(GH - P) + d (one skin sheet: the same slip for both)"""
    key = (id(W), law, f_ang, f_slip)
    if key not in _FCACHE:
        th, d = BS.angles(np.asarray(W, float)[:, :2], law); th = th * D2R * f_ang
        _FCACHE[key] = (np.stack([np.stack([BS.rot(E3[k], a) - E3 for a in th[:, k]]) for k in range(3)], 1), d * f_slip)   # (T, 3, 3, 3)
    Rm, d = _FCACHE[key]; r = BS.lever()[0]; V = np.einsum("tkij,j->tki", Rm, r - P)
    if normal is not None:
        n = np.asarray(normal, float); n = n / np.linalg.norm(n); Q = np.outer(n, n)
        V = np.einsum("ij,tkj->tki", Q, np.einsum("tkij,j->tki", Rm, r)) + np.einsum("ij,tkj->tki", E3 - Q, V)
    D = np.repeat(d[:, None], 3, 1)[:, :, None] * E3[None] / math.sqrt(3)
    return rss([(E3, np.concatenate([V, D], 1))])


def search(fn, U, fit):
    best = None
    for u in U:
        m = fn(u); v = float(m[fit].max())
        if best is None or v < best[0]: best = (v, u, m)
    return best


def selftest(W):
    """known answers: rigid = base_slip's central law; a follower at the anchor = rigid; slider + stage-2 along the same
    direction split the rigid error (Pythagoras); h is a unit vector"""
    H, C, h, _ = sources(W); a = mech("fixed", H, C, h); b = BS.misalignment(W[:, :2], laws=("central",))["central"]; u = np.array([0, 0, 1.0])
    ok = [np.abs(a - b).max() < 1e-9, np.abs(follower(W, np.zeros(3)) - b).max() < 1e-9,
          np.abs(mech("slider_ideal", H, C, h, u) ** 2 + mech("stage2_ideal", H, C, h, u) ** 2 - a ** 2).max() < 1e-6, np.abs(np.linalg.norm(h, axis=1) - 1).max() < 1e-9]
    for name, g in zip(("rigid = base_slip central", "follower at the anchor = rigid", "slider + stage2 = rigid (Pythagoras)", "|h| = 1"), ok): print(f"  {'ok ' if g else 'BAD'} {name}")
    _FCACHE.clear(); return all(ok)


if __name__ == "__main__":
    design = sys.argv[1] if len(sys.argv) > 1 else "cad_r18_n3_s1392_1_f300"
    Cl = json.load(open(os.path.join(REPO, "pipeline", "full-exo", "designs", design, "clips.json")))["clips"]
    hold = json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["held_out"]
    names = np.array([c["name"] for c in Cl for _ in c["frames"]]); W = np.array([fr["want"] for c in Cl for fr in c["frames"]], float)
    fit = ~np.isin(names, hold); ev = W[:, 1]
    print("self-checks:"); assert selftest(W[::5])
    H, C, h, RS = sources(W); U = fib(3000); out = dict(design=design, frames=len(W), fit_frames=int(fit.sum()), law="central", rows={})
    def row(key, m, extra=None):
        d = dict(fit_max=round(float(m[fit].max()), 2), held_out_max=round(float(m[~fit].max()), 2), all_max=round(float(m.max()), 2),
                 p95=round(float(np.percentile(m, 95)), 2), share_over_4=round(float((m > 4).mean()), 3),
                 max_elev_le_120=round(float(m[ev <= 120].max()), 2), worst=[str(names[int(np.argmax(m))]), [round(float(x)) for x in W[int(np.argmax(m))][:3]]])
        if extra: d.update(extra)
        out["rows"][key] = d; print(f"  {key:44s} fit {d['fit_max']:6.2f}  held-out {d['held_out_max']:6.2f}  p95 {d['p95']:5.2f}  >4mm {100 * d['share_over_4']:4.1f}%  (<=120 deg {d['max_elev_le_120']:5.2f})  worst {d['worst']}" + (f"  {extra}" if extra else ""))
    print(f"{design}: {len(W)} frames ({fit.sum()} fit, {(~fit).sum()} held out), central law; humerus axis in the scapula frame from Ludewig 2009")
    row("fixed (base_slip R10)", mech("fixed", H, C, h))
    b = search(lambda u: mech("slider_ideal", H, C, h, u), U, fit); row("slider_ideal (best u, set perfectly)", b[2], dict(u=np.round(b[1], 2).tolist()))
    b2 = search(lambda u: mech("stage2_ideal", H, C, h, u), U, fit); row("stage2_ideal (best plane normal n)", b2[2], dict(n=np.round(b2[1], 2).tolist()))
    row("stage3_brace (3-axis stage set by the arm brace)", mech("stage3_brace", H, C, h))
    for rho in (0.02, 0.1, 0.3):
        bb = search(lambda u: mech("slider_brace", H, C, h, u, rho=rho), U[::3], fit); row(f"slider_brace rho {rho}", bb[2], dict(u=np.round(bb[1], 2).tolist(), uh_overhead=round(float(abs(h[int(np.argmax(ev))] @ bb[1])), 2)))
    # bony follower on the scapula: scan P over a shell around the GH centre (above / around: where bone is palpable)
    r = BS.lever()[0]; best = None
    for Ld in (25.0, 32.0, 40.0):
        for u in fib(400):
            for s in (1, -1):
                P = r - s * Ld * u                                                                  # GH - P = s Ld u
                m = follower(W, P); v = float(m[fit].max())
                if best is None or v < best[0]: best = (v, P, m, s * u, Ld)
    row("follower (best point, 25-40 mm from GH)", best[2], dict(GH_minus_P_dir=np.round(best[3], 2).tolist(), dist_mm=best[4]))
    row("follower lateral acromion (32 mm above GH)", follower(W, r - np.array([0, -32.0, 0])))
    PL = r - np.array([0, -32.0, 0]); bf = search(lambda u: follower(W, PL, normal=u), U, fit)
    row("follower 2-axis stage (handler holds along n)", bf[2], dict(n=np.round(bf[1], 2).tolist(), deg_from_lever=round(float(np.degrees(np.arccos(abs(bf[1] @ r) / np.linalg.norm(r)))), 1)))
    for f in (0.32, 0.55): row(f"calibrated f {f} (angles and slip): + follower 2-axis stage", follower(W, PL, f_ang=f, f_slip=f, normal=bf[1]))
    row("[low law] follower 2-axis stage", follower(W, PL, law="low", normal=bf[1]))
    # per-user calibrated law (systematic part removed): handler angles x f (slip kept / x f)
    for f, fs in ((0.32, 1.0), (0.32, 0.32), (0.5, 1.0)):
        Hc, _, _, _ = sources(W, f_ang=f, f_slip=fs); row(f"calibrated f_ang {f} f_slip {fs}: fixed", mech("fixed", Hc, C, h))
        bc = search(lambda u: mech("slider_ideal", Hc, C, h, u), U[::2], fit); row(f"calibrated f_ang {f} f_slip {fs}: + slider_ideal", bc[2], dict(u=np.round(bc[1], 2).tolist()))
        bcb = search(lambda u: mech("slider_brace", Hc, C, h, u, rho=0.1), U[::3], fit); row(f"calibrated f_ang {f} f_slip {fs}: + slider_brace rho 0.1", bcb[2], dict(u=np.round(bcb[1], 2).tolist()))
    for f, fs in ((0.32, 1.0), (0.32, 0.32)):
        row(f"calibrated f_ang {f} f_slip {fs}: + follower lateral acromion", follower(W, r - np.array([0, -32.0, 0]), f_ang=f, f_slip=fs))
    for law in ("low", "high"):                                       # 'high' here = the high law's ANGLES (no ramp) combined RSS, not base_slip's worst-sign bound
        Hl, Cl_, hl, _ = sources(W, law=law); row(f"[{law} law{' angles, RSS' if law == 'high' else ''}] fixed", mech("fixed", Hl, Cl_, hl))
        row(f"[{law} law{' angles, RSS' if law == 'high' else ''}] slider_ideal u={np.round(b[1], 2).tolist()}", mech("slider_ideal", Hl, Cl_, hl, b[1]))
        row(f"[{law} law{' angles, RSS' if law == 'high' else ''}] stage2_ideal n={np.round(b2[1], 2).tolist()}", mech("stage2_ideal", Hl, Cl_, hl, b2[1]))
        row(f"[{law} law{' angles, RSS' if law == 'high' else ''}] follower lateral acromion", follower(W, r - np.array([0, -32.0, 0]), law=law))
    # the R1-relevant part: across the humerus (normal to the upper-arm skin under the links)
    PERP = h; globals()["PERP"] = h
    row("ACROSS HUMERUS fixed", mech("fixed", H, C, h)); row("ACROSS HUMERUS slider_ideal", mech("slider_ideal", H, C, h, b[1]))
    row("ACROSS HUMERUS stage2_ideal", mech("stage2_ideal", H, C, h, b2[1])); row("ACROSS HUMERUS follower lateral acromion", follower(W, r - np.array([0, -32.0, 0])))
    globals()["PERP"] = None
    # what each source alone contributes at the worst fixed frame
    t = int(np.argmax(mech("fixed", H, C, h))); out["worst_fixed_components_mm"] = dict(UR=round(float(np.linalg.norm(H[t, 0])), 2), IR=round(float(np.linalg.norm(H[t, 1])), 2), PT=round(float(np.linalg.norm(H[t, 2])), 2), slip=round(float(np.linalg.norm(H[t, 3:])), 2), h_scapula=np.round(h[t], 2).tolist())
    print("worst fixed frame components:", out["worst_fixed_components_mm"])
    json.dump(out, open(os.path.join(REPO, "pipeline", "girdle", "base_stage.json"), "w"), indent=1); print("wrote pipeline/girdle/base_stage.json")
