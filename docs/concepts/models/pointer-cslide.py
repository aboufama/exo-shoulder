"""pointer-cslide: the user's split - a 2R "pointer" shoulder (two donut/O20 hubs) + a shoulder-side wire-race C-slide
that carries the humeral twist (3 ACTIVE DOF, 0 passive). Built on the shared kit (tools/concept_kit.py, KIT.md).

Topology (scapula handler -> user's upper-arm cuff):
    scapula base --J1 (hub on axis a1, S-fixed, through GH, over the anterior acromion)--> link 1 (strap a1 -> p2, 90 deg)
    --J2 (hub on p2 = sigma * unit(a1 x d3): 90 deg off a1 AND off the arm axis)--> link 2 = the POINTING link (follows
    the arm's direction, not its twist), ending on an open circular wire-race band (the C-rail) about d3 at station s
    --J3 (the arm-fixed shoe riding the band: rotation about d3 = humeral twist)--> shoe -> neck -> BOTTOM's bar (cuff).
d3 = the humerus long axis (band humerus frame -y = the GH-elbow line), optionally tilted (tilt, tilt_a) in the humerus.
Kinematics: a spherical 3R with a3 = d3: q1 (azimuth of p2 about a1) and q2 (angle a1 -> d3 about p2) point the arm,
q3 (the shoe's angle about d3 in the pointing frame P = [p2 x d3, ., d3]) is its twist; all three fixed by the humerus
orientation in closed form (K1 closure with 90/90 cones; residual reported). Singular when d3 is parallel to +-a1:
frames within `sing` deg are rejected. No passive coordinate (R17): nothing can sag.

Parts at real size (skin-facing surfaces sampled 2 x 2 mm; every pair K6 >= 1 mm or by construction):
  * hub1, hub2: O20 hubs (kit K4: 20 mm disc, 12.25 stack) or, hub='kaa10', the spec's KAA10XL0 donut in its housing
    (39 mm disc, 9 mm stack). link 1 upper member at J1 (base lower), lower at J2; link 2 upper at J2.
  * link 1, link 2: straps width x t_link, K3 skin-fitted, 60 deg climb; link 2 passes over link 1; it ends on the
    band's PROXIMAL edge at the band's mid angle c (the shoe wraps only the distal edge, so it never meets link 2).
  * band (C-rail): circular about d3 (a rotary track must be a surface of revolution), 26 mm wide (axial s-13..s+13),
    6 mm radial (wires incl.), skin face at rho + 2, fixed in link 2 (the frame P), spanning the shoe's travel window
    [c - T/2, c + T/2] + the shoe half-arc + 3 mm end stops each side. T and c = the smallest arc that holds the shoe in a
    share `cov` of the closing bench poses (a design decision from the data, then fixed).
  * shoe (arm-fixed, Ls deg of arc at arm angle phi_s): the spec's 2 + 6 + 2 stack - a 2 mm lip under the band's distal
    6 mm (skin face at rho), the distal wall (w s+13..s+15, down to rho) and a 2 mm cap over the band (to rho + 10).
  * neck: K7 14 x 6 strap from the shoe's distal wall (s + 17) to BOTTOM's bar start.
  rho = max(quantile_q_ring over the closing poses of the radial march (first radius with skin distance >= 2 mm) of
  the band samples - 2, the same for the shoe lip/wall samples). The band's outer face (rho + 8) and the shoe crown
  (rho + 10) are checked for contact with the torso (contact only, not in-band).
Clearances by construction: band-shoe (the bearing, 0.15 mm running gap in the 2+6+2 stack), link 2-band (one part),
shoe-neck (one part). Everything else: K6. Continuity: K2 dense (values + axes). Held-out clips never loaded.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/pointer-cslide.py [check|poses]
"""
import itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "pointer-cslide"
NAME = "The user's split: 2R donut pointer + shoulder-side wire-race C-slide for humeral twist"
BAND_W, BAND_T, LIP, CAP = 26.0, 6.0, 2.0, 2.0               # band 26 x 6; shoe lip under it 2, cap over it 2 (2+6+2)
PARAMS = dict(az=120.0, el=46.0, sigma=1, A1=90.0, A2=90.0, sing=15.0, tilt=0.0, tilt_a=0.0,
              s=120.0, phi_s=0.0, Ls=50.0, cov=0.9, c_off=0.0, q_ring=0.95, r_block=100.0, hub="o20", width=12.0, t_link=3.0, q=0.95)

# ---- fixed-geometry members (band, shoe: circles about d3, not GH-ray fitted) --------------------------------------
_orig_levels = K._levels


def _levels(B, chain, fit, q, mode):
    fixed = [m for m in chain.members if getattr(m, "fixed_rho", None) is not None]
    sub = K.Chain(members=[m for m in chain.members if getattr(m, "fixed_rho", None) is None], ok=chain.ok)
    out = _orig_levels(B, sub, fit, q, mode)
    for m in fixed: out[m.name] = m.fixed_rho.copy()
    return out


K._levels = _levels
EXEMPT = {frozenset(x) for x in (("band", "shoe"), ("link2", "band"), ("shoe", "neck"))}


def _collisions(chain, pts, ok, clear=1.0, overlap=0.5, chunk=24):
    """K.collisions (same code) with the by-construction pairs (bearing, one-part joints) left out"""
    hit = np.zeros(len(ok), bool); M = chain.members; Pi = np.nonzero(ok)[0]
    if not len(Pi): return hit
    nr = {m.name: np.linalg.norm(pts[m.name], axis=-1) for m in M}; dr = {m.name: pts[m.name] / nr[m.name][..., None] for m in M}
    for a in range(len(M)):
        for b in range(a + 1, len(M)):
            A, Bm = M[a], M[b]
            if frozenset((A.name, Bm.name)) in EXEMPT: continue
            shared = set(A.joints) & set(Bm.joints); ra, rb = nr[A.name], nr[Bm.name]
            if ra[Pi].min() > rb[Pi].max() + Bm.t + overlap or rb[Pi].min() > ra[Pi].max() + A.t + overlap: continue
            for c0 in range(0, len(Pi), chunk):
                P = Pi[c0:c0 + chunk]; xa, xb = ra[P], rb[P]
                res = K._near(A, Bm, dr[A.name][P], dr[Bm.name][P], xa, xb, chain.joints, shared, P, clear)
                if res is None: continue
                k, nm = res; xa, xb = xa[k], xb[k]
                ov = (xa[:, :, None] < xb[:, None, :] + Bm.t + overlap) & (xb[:, None, :] < xa[:, :, None] + A.t + overlap)
                hit[P[k]] |= (nm & ov).any((1, 2))
    return hit


K.collisions = _collisions


def wrap(x): return (np.asarray(x, float) + 180.0) % 360.0 - 180.0


# ---- kinematics ----------------------------------------------------------------------------------------------------
def arm_basis(p):
    """humerus (band frame) axis d3 and the in-plane basis: phi 0 lateral, +90 anterior"""
    d3 = K.wdir(p["tilt"], p["tilt_a"]); el = K.unit(np.array([0.0, 0, 1]) - d3[2] * d3); ea = np.cross(el, d3)
    return d3, el, ea


def kin(F, p):
    a1 = F.S(K.bvec(p["az"], p["el"])); d3l, el, ea = arm_basis(p); d3 = F.HG(d3l)
    p2, ok, margin = K.closure(a1, d3, p["A1"], p["A2"], p["sigma"], margin_deg=p["sing"])
    xP = K.unit(np.cross(p2, d3)); yP = np.cross(d3, xP)                       # pointing frame P (link 2)
    E1, E2 = F.HG(el), F.HG(ea); ps = math.radians(p["phi_s"])
    shoe = math.cos(ps) * E1 + math.sin(ps) * E2                               # shoe direction (arm-fixed) about d3
    th = np.degrees(np.arctan2((shoe * yP).sum(-1), (shoe * xP).sum(-1)))     # q3: shoe angle in P
    return a1, p2, d3, xP, yP, E1, E2, th, ok, margin


_CACHE = {}


def _key(p): return tuple(p[k] for k in ("az", "el", "sigma", "A1", "A2", "sing", "tilt", "tilt_a", "s", "phi_s", "Ls", "cov", "c_off", "q_ring", "r_block"))


def window(th, ok, cov):
    """(c, T): the smallest arc holding the shoe angle th in a share cov of the closing poses"""
    s = np.sort(wrap(th[ok])); n = len(s)
    if n < 3: return 0.0, 360.0
    m = max(1, int(math.ceil(cov * n))); s2 = np.r_[s, s + 360.0]
    w = s2[np.arange(n) + m - 1] - s2[np.arange(n)]; i = int(np.argmin(w))
    return float(wrap(s2[i] + w[i] / 2)), float(w[i])


def radial_req(B, I, Z, U, clr=2.0, r0=12.0, r_block=100.0):
    """per point: the first radius r >= r0 out from the axis point Z along the radial unit U (thorax, per pose I)
    where the skin distance is >= clr (Lipschitz march, 0.25 mm min step). Still blocked at r_block (torso pressed on
    the arm) -> 0: such a pose does not push the band out (it becomes a contact pose for the bench)"""
    R = np.full(len(Z), r0); act = np.ones(len(Z), bool)
    for _ in range(400):
        a = np.nonzero(act)[0]
        if not len(a): break
        g = K.dist_many(B, I[a], Z[a] + R[a, None] * U[a]); done = g >= clr
        act[a[done]] = False; R[a[~done]] += np.maximum(0.25, clr - g[~done]); act &= R < r_block
    return np.where(R < r_block, R, 0.0)


def ring_pts(axis_pt, e1, e2, d3, rows, ang_deg, R):
    """points (P, len(rows) * len(ang), 3): w d3 + R (cos a e1 + sin a e2); e1, e2, d3 (P, 3); ang (P, n) or (n,)"""
    a = np.radians(np.asarray(ang_deg, float)); a = np.broadcast_to(a, (len(e1), a.shape[-1]))
    e = np.cos(a)[..., None] * e1[:, None] + np.sin(a)[..., None] * e2[:, None]          # (P, n, 3)
    R = np.asarray(R, float).reshape(-1, 1, 1, 1) if np.ndim(R) else R
    X = np.asarray(rows)[None, :, None, None] * d3[:, None, None] + R * e[:, None]      # (P, rows, n, 3)
    return X.reshape(len(e1), -1, 3)


def design(B, p):
    """the fixed design decisions taken from the bench data (cached): window (c, T) and the band / shoe radius rho"""
    key = _key(p)
    if key in _CACHE: return _CACHE[key]
    F = B._kitF; a1, p2, d3, xP, yP, E1, E2, th, ok, margin = kin(F, p)
    c, T = window(th, ok, p["cov"]); c = float(wrap(c + p["c_off"]))
    ok = ok & (np.abs(wrap(th - c)) <= T / 2 + 1e-9)
    Pi = np.nonzero(ok)[0]; rho = 60.0
    if len(Pi):
        band_ang, shoe_ang = angles(p, c, T, 60.0)
        rowsB = p["s"] + np.arange(-BAND_W / 2, BAND_W / 2 + 1e-6, 2.0)
        rowsS = p["s"] + np.array([BAND_W / 2 - 6, BAND_W / 2 - 4, BAND_W / 2 - 2, BAND_W / 2, BAND_W / 2 + 2])
        U = ring_pts(None, xP[Pi], yP[Pi], d3[Pi], [0.0], band_ang, 1.0)                 # unit radials (band, P frame)
        Zb = np.repeat(rowsB, U.shape[1])[None, :, None] * d3[Pi][:, None]
        Ub = np.tile(U, (1, len(rowsB), 1))
        Us = ring_pts(None, E1[Pi], E2[Pi], d3[Pi], [0.0], p["phi_s"] + shoe_ang, 1.0)
        Zs = np.repeat(rowsS, Us.shape[1])[None, :, None] * d3[Pi][:, None]; Us = np.tile(Us, (1, len(rowsS), 1))
        I = np.repeat(Pi, Ub.shape[1]); rb = radial_req(B, I, Zb.reshape(-1, 3), Ub.reshape(-1, 3), r_block=p["r_block"]).reshape(len(Pi), -1).max(1)
        I = np.repeat(Pi, Us.shape[1]); rs = radial_req(B, I, Zs.reshape(-1, 3), Us.reshape(-1, 3), r_block=p["r_block"]).reshape(len(Pi), -1).max(1)
        qq = p["q_ring"]; f = (lambda x: np.quantile(x, qq)) if qq < 1 else np.max
        rho = float(max(f(rb) - LIP, f(rs), 20.0))
    _CACHE[key] = dict(c=c, T=T, rho=rho)
    return _CACHE[key]


def angles(p, c, T, rho):
    """band columns (P-frame deg) and shoe columns (offsets about its centre, deg), 2 mm apart at the band radius"""
    hs = p["Ls"] / 2; stop = math.degrees(3.0 / (rho + LIP))
    lo, hi = c - T / 2 - hs - stop, c + T / 2 + hs + stop
    nb = max(2, int(math.ceil(math.radians(hi - lo) * (rho + LIP) / 2.0)) + 1)
    ns = max(2, int(math.ceil(math.radians(2 * hs) * rho / 2.0)) + 1)
    return np.linspace(lo, hi, nb), np.linspace(-hs, hs, ns)


def fixed_member(name, X, joints, t):
    """a rigid part with given thorax points X (P, m, 3) (its skin face); t = radial thickness (K6, contact)"""
    rho = np.linalg.norm(X, axis=-1); D = X / rho[..., None]
    m = K.Member(name, D, t=float(t), joints=tuple(joints), r_ref=float(rho.max()))
    m.fixed_rho = rho[0]                                    # same layout in every pose (rigid in its own frame)
    return m


def hub(name, axis, joint, p):
    if p.get("hub", "o20") == "kaa10": return K.hub_member(name, axis, joint, t=9.0, rad=19.5)   # KAA10XL0 + 2 mm housing
    return K.hub_member(name, axis, joint)


# ---- the model -----------------------------------------------------------------------------------------------------
def build_chain(B, F, p):
    if getattr(B, "_kitF", None) is None: B._kitF = K.frames(B)
    a1, p2, d3, xP, yP, E1, E2, th, ok, margin = kin(F, p)
    D = design(B, p); c, T, rho = D["c"], D["T"], D["rho"]
    ok = ok & (np.abs(wrap(th - c)) <= T / 2 + 1e-9)                                     # J3 range: shoe on the band
    band_ang, shoe_off = angles(p, c, T, rho); s = p["s"]
    rowsB = s + np.arange(-BAND_W / 2, BAND_W / 2 + 1e-6, 2.0)
    Xb = ring_pts(None, xP, yP, d3, rowsB, band_ang, rho + LIP)                          # band skin face (P frame)
    rowsS = s + np.array([BAND_W / 2 - 6, BAND_W / 2 - 4, BAND_W / 2 - 2, BAND_W / 2, BAND_W / 2 + 2])
    Xs = ring_pts(None, E1, E2, d3, rowsS, p["phi_s"] + shoe_off, rho)                   # shoe lip + wall (arm frame)
    band = fixed_member("band", Xb, ("J2", "J3"), BAND_T)
    shoe = fixed_member("shoe", Xs, ("J3",), LIP + BAND_T + CAP)
    # link 2 ends on the band's proximal edge at its mid angle c
    att = K.unit(ring_pts(None, xP, yP, d3, [s - BAND_W / 2 + 1], [c], rho + LIP)[:, 0])
    ps = math.radians(p["phi_s"]); shoe_dir = math.cos(ps) * E1 + math.sin(ps) * E2
    neck_from = K.unit((s + BAND_W / 2 + 4) * d3 + (rho + 2) * shoe_dir)
    w, t = p["width"], p["t_link"]
    hubs = [hub("hub1", a1, "J1", p), hub("hub2", p2, "J2", p)]
    link1 = K.strap_member("link1", a1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)))
    link2 = K.strap_member("link2", p2, att, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), (None, 0.0)),
                           over=[("link1", 1.0)])
    neck = K.neck_member(F, neck_from, joints=("J3",))
    q = np.stack([K.axis_angle(a1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, a1, d3), th], -1)
    res = K.closure_residual(a1, d3, p2, p["A1"], p["A2"])
    return K.Chain(members=hubs + [link1, link2, band, shoe, neck], ok=ok, q=q, joints=dict(J1=a1, J2=p2, J3=d3),
                   hubless=("J3",),
                   info=dict(residual_deg=round(float(res[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                             rho=round(rho, 2), c=round(c, 1), T=round(T, 1),
                             band_arc=round(float(band_ang[-1] - band_ang[0]), 1)))


def outer_contact(B, p, rep):
    """contact-only check of the faces that can meet the torso: band outer face (rho + 8) and shoe crown (rho + 10)"""
    L = B._kit_last; ch = L["chain"]; take = L["take"]; Pi = np.nonzero(take)[0]
    if not len(Pi): return rep
    F = B._kitF; a1, p2, d3, xP, yP, E1, E2, th, ok, margin = kin(F, p)
    Dd = design(B, p); c, T, rho = Dd["c"], Dd["T"], Dd["rho"]; band_ang, shoe_off = angles(p, c, T, rho); s = p["s"]
    Xb = ring_pts(None, xP[Pi], yP[Pi], d3[Pi], s + np.array([-BAND_W / 2, 0.0, BAND_W / 2]), band_ang, rho + LIP + BAND_T)
    Xs = ring_pts(None, E1[Pi], E2[Pi], d3[Pi], s + np.array([-BAND_W / 2, 0.0, BAND_W / 2 + 2]), p["phi_s"] + shoe_off,
                  rho + LIP + BAND_T + CAP)
    Y = np.concatenate([Xb, Xs], 1); m = Y.shape[1]
    d = K.dist_many(B, np.repeat(Pi, m), Y.reshape(-1, 3)).reshape(len(Pi), m).min(1); n_out = 0
    for j, i in enumerate(Pi):
        if d[j] < 0: B.res[i] = np.append(B.res[i], d[j]); n_out += 1
    r = B.report(); rep.update({k: r[k] for k in ("reach", "follow", "inband14", "inband10", "contact", "gap")})
    rep["outer_contact_poses"] = n_out
    return rep


def bench_eval(B, params):
    """the sweep hook (tools/concept_sweep.py): honest kit evaluation (march, K2 dense, K6) + outer-face contact"""
    p = dict(PARAMS, **params)
    if getattr(B, "_kitF", None) is None: B._kitF = K.frames(B)
    rep = K.evaluate(B, build_chain, p)
    rep = outer_contact(B, p, rep)
    return json.loads(json.dumps(rep, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def metal(pose, frames, params):
    L = getattr(frames, "_kit_last", None)
    if L is None or not L["take"][pose]: return None
    return np.concatenate([L["pts"][m.name][pose] for m in L["chain"].members], 0)


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    B = K.bench(60, 160); B._kitF = K.frames(B)
    p = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 else {}))
    if a[0] == "check":
        import time; t0 = time.time(); r = bench_eval(B, p); print(round(time.time() - t0, 1), "s"); print(r)
        L = B._kit_last; tk = L["take"]
        for m in L["chain"].members:
            X = np.linalg.norm(L["pts"][m.name], axis=-1); d = K.dist_many(B, np.repeat(np.nonzero(tk)[0], X.shape[1]), L["pts"][m.name][tk].reshape(-1, 3)) if tk.any() else np.zeros(1)
            print(m.name, "radius", round(float(X.min()), 1), round(float(X.max()), 1), "skin dist med/p10/p90", np.percentile(d, [50, 10, 90]).round(1) if d.size else None)
    elif a[0] == "redteam":                   # the red-team pose list: why each pose is (not) taken, the nearest metal
        r = bench_eval(B, p); print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, r["inband_member"])
        L = B._kit_last; ch = L["chain"]; F = B._kitF; a1, p2, d3, xP, yP, E1, E2, th, ok0, margin = kin(F, p)
        Dd = design(B, p); win = np.abs(wrap(th - Dd["c"])) <= Dd["T"] / 2 + 1e-9
        pz = np.array([(q["plane"], q["elev"], q["axial"]) for q in B.poses])
        tg = dict(rest=(0, 0, 0), rest_ir=(0, 0, -80), rest_er=(0, 0, 60), abd90=(0, 90, 0), overhead_abd=(0, 160, 0),
                  overhead_flex=(90, 160, 0), across_body=(130, 90, 0), across_low=(120, 45, -40), behind_back=(-90, 40, -90),
                  ext=(-60, 50, 0), abd90_ir=(0, 90, -80), abd90_er=(0, 90, 90))
        for nm, t3 in tg.items():
            dd = np.abs(pz - np.array(t3)); dd[:, 2] = np.minimum(dd[:, 2], 360 - dd[:, 2]); i = int(np.argmin(dd @ [1, 1, 0.5]))
            why = "TAKEN" if L["take"][i] else ("singular" if not (margin[i] >= p["sing"]) else "window" if not win[i] else "K2" if not L["ok"][i] else "collide" if L["hit"][i] else "?")
            line = f"{nm:13s} pose {i:3d} {B.kind[i]:4s} {tuple(round(float(x)) for x in pz[i])} q3 {th[i]:7.1f} margin {margin[i]:5.1f} {why}"
            if L["take"][i]:
                for m in ch.members:
                    dm = K.dist_many(B, np.full(L["pts"][m.name].shape[1], i), L["pts"][m.name][i]); line += f" | {m.name} {dm.min():.1f}/{np.median(dm):.1f}"
            if why == "collide":
                pr = []
                for x, y in itertools.combinations(ch.members, 2):
                    sub = K.Chain(members=[x, y], ok=ch.ok, joints=ch.joints); msk = np.zeros(len(L["ok"]), bool); msk[i] = True
                    if _collisions(sub, {x.name: L["pts"][x.name], y.name: L["pts"][y.name]}, msk)[i]: pr.append(f"{x.name}-{y.name}")
                line += " " + ",".join(pr)
            print(line)
        print("contact poses:", int(sum(1 for i in range(len(B.res)) if B.res[i] is not None and np.min(B.res[i]) < 0)), "outer", r.get("outer_contact_poses"))
    elif a[0] == "twist":                     # the shoe-angle distribution: what travel T a share of poses needs
        F = B._kitF; a1, p2, d3, xP, yP, E1, E2, th, ok, margin = kin(F, p)
        for cov in (0.5, 0.7, 0.8, 0.9, 0.95, 1.0):
            for nm, msk in (("all", ok), ("clip", ok & F.clip), ("ws", ok & F.ws)):
                print(cov, nm, [round(x, 1) for x in window(th, msk, cov)], int(msk.sum()), end=" | ")
            print()
