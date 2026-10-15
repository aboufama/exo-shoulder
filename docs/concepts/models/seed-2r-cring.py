"""seed-2r-cring: 2R spherical shoulder + open C-ring axial bearing on the upper arm (3 ACTIVE DOF, 1 passive slide).
Rebuilt on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md); the interrupted session's 535-line model was
replaced (it re-implemented frames / closure / fitting and used a 30 deg-per-frame flip rule the kit shows is wrong).

Topology (scapula handler -> user's upper-arm cuff):
    scapula base --J1 (O20 hub, axis p1 fixed in S, through GH)--> link 1 (strap p1 -> p2) --J2 (O20 hub, axis p2 through
    GH)--> link 2 (strap p2 -> carriage, down over the deltoid) -> carriage riding an open C-track whose axis d3 is
    fixed in the humerus and passes through GH (J3 = rotation about d3: the arm's axial rotation) -> C-track fixed to a
    passive slide along d3 (rail + block on the cuff side) -> user's cuff (BOTTOM).
Kinematics = a spherical 3R whose last axis is (close to) the humerus long axis: d3 = HG wdir(tilt, tilt_a) (tilt 0 =
the GH-elbow line, measured: it is exactly -y of the band humerus frame). p2 by the two-cone closure angle(p1, p2) = a1,
angle(p2, d3) = a2 on branch sigma (K1). J3 value = carriage azimuth psi_c round d3 in the humerus frame.
DOF: J1, J2, J3 active (3). The slide along d3 is passive and DETERMINED: every revolute axis passes through GH, so the
loop's translation equations leave the slide equal to the GH translation along d3 (zero on the bench rig, whose GH is
fixed); it cannot sag (both its ends are located: the cuff on the arm, the track by the 3R about GH). No other passive
coordinate.

Parts at real size (every skin-facing surface sampled at ~1 pt / 4 mm2):
  * hub1, hub2: kit O20 hubs (K4, 20 mm disc, 12.25 stack); link 1 is the upper member at J1 (base plate lower), lower
    at J2; link 2 upper at J2.
  * link 1, link 2: kit straps (K5) width x 3 mm, K3 skin-fitted underside, 60 deg climb; link 2 passes OVER link 1, the
    track and the slide (>= 1 mm, by construction) and ends on the carriage.
  * C-track: 8 mm axial x 6 mm radial ring, CIRCULAR about d3 (a rotary track must be a surface of revolution), at
    axial level L from GH, inner radius R fitted on the posed skin itself (Lipschitz march on the signed distance, all
    bench poses, quantile q_ring) + clr; open where the carriage never goes: the C span is the smallest arc holding
    the carriage centre over a share `cov` of the closing poses, + the carriage half-arc + 3 mm, the rest is open.
    Inner face sampled 4 rows x 2 mm (in-band and contact); outer face (R + 6) checked for contact (torso) only.
  * carriage: 25 mm (arc) x 12 mm (axial) block on the track's outer face, underside at R + 6.5, link-2 fixed;
    top (R + 12.5) checked for contact only.
  * passive slide: 40 x 10 mm rail + block, humerus-fixed, just outside the C's anterior... (side `slide_side`) end,
    from the track's proximal edge 40 mm distal; K3 skin-fitted underside, 6 mm thick.
Clearances the kit's GH-shell K6 cannot represent (all three ride the arm axis, not GH shells) are by construction:
carriage on track (bearing), slide fixed to the track end beyond the carriage's travel, link 2 merges into the
carriage. Every other pair: K6 (>= 1 mm). Continuity: K2 dense. Closure residual reported.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/seed-2r-cring.py [check|sweep|refine|redteam]
"""
import itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "seed-2r-cring"
NAME = "2R spherical shoulder + C-ring axial bearing on the upper arm"
TR_RAD, TR_AX = 6.0, 8.0                                     # C-track section (radial x axial)
CAR_ARC, CAR_AX, CAR_GAP = 25.0, 12.0, 0.5                   # carriage block on the track's outer face
SL_LEN, SL_W, SL_T = 40.0, 10.0, 6.0                         # passive slide (rail + block)
PARAMS = dict(az=125.0, el=45.0, a1=90.0, a2=90.0, sigma=1, margin=10.0, L=100.0, tilt=18.0, tilt_a=-30.0,
              c_target=0.0, clr=2.5, q_ring=0.8, cov=0.95, slide_side=1, width=10.0, t_link=3.0, q=0.97)
SWEEP = dict(q_ring=[0.5, 0.8], sigma=[1, -1], az=[125.0, 95.0], L=[100.0, 160.0])


# ---- fixed-geometry members (the track, carriage): the kit fits 'free' undersides on the skin; these are not fitted
_orig_levels = K._levels


def _levels(B, chain, fit, q, mode):
    fixed = [m for m in chain.members if getattr(m, "fixed_rho", None) is not None]
    sub = K.Chain(members=[m for m in chain.members if getattr(m, "fixed_rho", None) is None], ok=chain.ok)
    out = _orig_levels(B, sub, fit, q, mode)
    for m in fixed: out[m.name] = m.fixed_rho.copy()
    return out


K._levels = _levels
EXEMPT = {frozenset(x) for x in (("ring", "carriage"), ("ring", "slide"), ("carriage", "slide"), ("link2", "carriage"))}


def _collisions(chain, pts, ok, clear=1.0, overlap=0.5, chunk=24):
    """K.collisions with the by-construction pairs (track / carriage / slide / link 2 end) left out"""
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


# ---- geometry helpers ----------------------------------------------------------------------------------------------
def ring_basis(p):
    """local (band humerus frame) axis d3 and the in-plane basis: psi 0 lateral, +90 anterior"""
    d3 = K.wdir(p["tilt"], p["tilt_a"]); e_lat = K.unit(np.array([0.0, 0, 1]) - d3[2] * d3); e_ant = np.cross(e_lat, d3)
    return d3, e_lat, e_ant


def kin(F, p):
    p1 = F.S(K.bvec(p["az"], p["el"])); d3l, el, ea = ring_basis(p); d3 = F.HG(d3l); E1, E2 = F.HG(el), F.HG(ea)
    p2, ok, margin = K.closure(p1, d3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
    psi_raw = np.degrees(np.arctan2((p2 * E2).sum(-1), (p2 * E1).sum(-1)))     # azimuth of p2 round d3 (humerus frame)
    return p1, p2, d3, E1, E2, ok, margin, psi_raw


def wrap(x): return (np.asarray(x) + 180.0) % 360.0 - 180.0


_SPAN, _RAD = {}, {}


def span(B, p):
    """(c0, hw0): the smallest arc holding p2's azimuth round d3 in a share cov of the closing bench poses. The carriage
    sits on link 2 at azimuth offset off = c_target - c0 from p2's plane, so the C span is centred on c_target (0 =
    lateral) and its opening on the opposite side (the torso side for c_target 0)"""
    key = tuple(p[k] for k in ("az", "el", "a1", "a2", "sigma", "margin", "tilt", "tilt_a", "cov"))
    if key not in _SPAN:
        F = B._kitF; _, _, _, _, _, ok, _, psi = kin(F, p); s = np.sort(wrap(psi[ok])); n = len(s)
        if n < 3: _SPAN[key] = (0.0, 180.0); return _SPAN[key]
        m = max(1, int(math.ceil(p["cov"] * n))); s2 = np.r_[s, s + 360.0]
        w = s2[np.arange(n) + m - 1] - s2[np.arange(n)]; i = int(np.argmin(w))
        _SPAN[key] = (float(wrap(s2[i] + w[i] / 2)), float(w[i] / 2))
    return _SPAN[key]


def ring_local(p, c, hw, R, rows, rad_add=0.0, step=2.0, n=None):
    """local points of a band round d3: rows (axial z), psi in [c - hw, c + hw], radius R + rad_add, 2 mm spacing"""
    d3, el, ea = ring_basis(p); Rr = np.asarray(R, float) + rad_add
    n = n or (len(Rr) if Rr.ndim else max(2, int(math.ceil(2 * hw * K.D2R * Rr / step)) + 1))
    ps = np.radians(np.linspace(c - hw, c + hw, n)); e = np.cos(ps)[:, None] * el + np.sin(ps)[:, None] * ea
    return (np.asarray(rows)[:, None, None] * d3 + np.reshape(Rr, (-1, 1)) * e[None]).reshape(-1, 3)


def cam_n(p, c, hw):
    """columns of the inner face: 2 mm at the nominal 60 mm radius"""
    return max(2, int(math.ceil(2 * hw * K.D2R * 60 / 2.0)) + 1)


def full_span(B, p):
    """(span centre, half width incl. the carriage half-arc + 3 mm at a nominal R 50, offset off)"""
    c0, hw0 = span(B, p)
    return p["c_target"], min(180.0, hw0 + math.degrees((CAR_ARC / 2 + 3) / (50 + TR_RAD))), p["c_target"] - c0


def _rkey(p, c, hw): return (p["L"], p["tilt"], p["tilt_a"], round(c, 3), round(hw, 3), p["clr"], p["q_ring"])


def ring_radius(B, p, c, hw, r_block=95.0):
    """inner radius of the circular track, fitted on the posed skin: per bench pose and inner-face sample (4 rows, the C
    span), the first radius out from d3 where the skin distance is >= clr (Lipschitz march, exact on the 0.25 mm
    lattice of steps); samples still blocked at r_block (the torso pressed on the arm there) do not push the ring out -
    that pose is then a contact pose for the bench. R = quantile q_ring over the poses of the per-pose max."""
    key = _rkey(p, c, hw)
    if key not in _RAD:
        F = B._kitF; P = len(F.RS); rows = p["L"] + np.array([-3.0, -1, 1, 3])
        nn = max(2, int(math.ceil(2 * hw * K.D2R * 60 / 2.0)) + 1)
        u = ring_local(p, c, hw, 1.0, rows, n=nn) - ring_local(p, c, hw, 0.0, rows, n=nn)       # unit radial (m, 3)
        z = ring_local(p, c, hw, 0.0, rows, n=nn); m = len(u)
        I = np.repeat(np.arange(P), m); Rr = np.full(P * m, 15.0); act = np.ones(P * m, bool)
        Z = np.einsum("pij,mj->pmi", F.RHG, z).reshape(-1, 3); U = np.einsum("pij,mj->pmi", F.RHG, u).reshape(-1, 3)
        for _ in range(300):
            a = np.nonzero(act)[0]
            if not len(a): break
            g = K.dist_many(B, I[a], Z[a] + Rr[a, None] * U[a])
            done = g >= p["clr"]; act[a[done]] = False; Rr[a[~done]] += np.maximum(0.25, p["clr"] - g[~done])
            act &= Rr < r_block
        Rc = np.where(Rr < r_block, Rr, 0.0).reshape(P, 4, nn).max(1)                           # (P, columns)
        Rr = Rc.max(1)
        _RAD[key] = float(np.quantile(Rr, p["q_ring"])); _RAD[key + ("per",)] = Rr
        # cam variant: the track is a non-circular closed cam about d3 fitted per azimuth column (quantile q_ring over
        # the poses), the carriage follows it on a radial slide on link 2 (passive, set by the cam: determined)
        col = np.quantile(Rc, p["q_ring"], axis=0); w = max(1, int(round(6.0 / 2.0)))       # +-6 mm max filter: carriage wheel base
        _RAD[key + ("cam",)] = np.array([col[max(0, i - w):i + w + 1].max() for i in range(nn)])
    return _RAD[key]


def fixed_member(name, F, loc, joints, t, R):
    """a humerus-fixed (loc (m, 3) in the band humerus frame) or pose-wise (loc (P, m, 3) local) rigid part whose
    skin face sits at radius R from d3; t (radial from d3) is given to K6 / `over` as its extent along the GH ray"""
    X = np.einsum("pij,pmj->pmi", F.RHG, loc) if loc.ndim == 3 else F.HG(loc)
    rho = np.linalg.norm(X, axis=-1)[0]; D = X / rho[None, :, None]
    m = K.Member(name, D, t=float(t * rho.mean() / R), joints=tuple(joints), r_ref=float(rho.max()))
    m.fixed_rho = rho; return m


# ---- the model -----------------------------------------------------------------------------------------------------
def build(B, F, p):
    p1, p2, d3, E1, E2, ok, margin, psi_raw = kin(F, p)
    c, hw, off = full_span(B, p); psi_c = wrap(psi_raw + off); R = ring_radius(B, p, c, hw)
    nn = cam_n(p, c, hw); Rcol = _RAD[_rkey(p, c, hw) + ("cam",)] if p.get("cam") else np.full(nn, R)
    Rpsi = np.interp(wrap(psi_c - c), np.linspace(-hw, hw, nn), Rcol)                         # track radius under the carriage
    R = float(Rcol.mean()) if p.get("cam") else R; car_h = math.degrees((CAR_ARC / 2) / (R + TR_RAD))
    ok = ok & (np.abs(wrap(psi_c - c)) <= hw - car_h - math.degrees(3.0 / (R + TR_RAD)) + 1e-9)        # J3 range: carriage inside the C
    d3l, el, ea = ring_basis(p)
    # track inner face (humerus-fixed), 4 axial rows over 8 mm
    ring = fixed_member("ring", F, ring_local(p, c, hw, Rcol, p["L"] + np.array([-3.0, -1, 1, 3]), n=nn), ("J3",), TR_RAD, R)
    # carriage: link-2 fixed, at azimuth psi_c, underside on the track's outer face (pose-wise local points)
    rows = p["L"] + np.arange(-CAR_AX / 2 + 1, CAR_AX / 2, 2.0); Rc = (Rpsi + TR_RAD + CAR_GAP)[:, None, None, None]
    n = int(math.ceil(CAR_ARC / 2)) + 1; offs = np.radians(np.linspace(-car_h, car_h, n))
    ps = np.radians(psi_c)[:, None] + offs[None]                                                 # (P, n)
    e = np.cos(ps)[..., None] * el + np.sin(ps)[..., None] * ea                                 # (P, n, 3) local
    loc = (rows[None, :, None, None] * d3l + Rc * e[:, None]).reshape(len(ps), -1, 3)
    car = fixed_member("carriage", F, loc, ("J3",), 6.0, R + TR_RAD + CAR_GAP)
    # passive slide at the C end on side slide_side (just outside the span, in the opening), 40 mm distal of the track
    sh = math.degrees((SL_W / 2 + 1) / R); psl = c + p["slide_side"] * (hw + sh)
    sl_dir = F.HG(K.unit(ring_local(p, psl, 0.0, R, [p["L"] - 4.0])[0]))
    sl_end = F.HG(K.unit(ring_local(p, psl, 0.0, R, [p["L"] + SL_LEN - 4.0])[0]))
    slide = K.strap_member("slide", sl_dir[:, 0] if sl_dir.ndim == 3 else sl_dir, sl_end[:, 0] if sl_end.ndim == 3 else sl_end,
                           ("J3",), width=SL_W, t=SL_T, climb_deg=None)
    # hubs and links (K4, K5)
    cdir = K.unit(np.einsum("pij,pj->pi", F.RHG, p["L"] * d3l + (Rpsi + TR_RAD + 6)[:, None] * np.einsum("pk,kj->pj",
                  np.stack([np.cos(np.radians(psi_c)), np.sin(np.radians(psi_c))], -1), np.stack([el, ea]))))
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub2", p2, "J2")]
    w, t = p["width"], p["t_link"]
    link1 = K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)))
    link2 = K.strap_member("link2", p2, cdir, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), (None, 0.0)),
                           over=[("link1", 1.0), ("ring", 1.0), ("slide", 1.0)])
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, d3), psi_c], -1)
    res = K.closure_residual(p1, d3, p2, p["a1"], p["a2"])
    return K.Chain(members=hubs + [link1, link2, ring, car, slide], ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=d3), hubless=("J3",),
                   info=dict(residual_deg=round(float(res[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                             ring_R=round(R, 2), c_span=round(c, 1), half_span=round(hw, 1), opening=round(360 - 2 * hw, 1), car_off=round(off, 1)))


def outer_contact(B, p, rep):
    """contact-only check of the non-skin-facing faces that can meet the torso: track outer face (R + 6), carriage top
    (R + 12.5): a taken pose with any of them inside the body becomes a contact pose (bench rule)"""
    L = B._kit_last; ch = L["chain"]; take = L["take"]; Pi = np.nonzero(take)[0]
    if not len(Pi): return rep
    info = ch.info; R, c, hw = info["ring_R"], info["c_span"], info["half_span"]; F = B._kitF
    loc = ring_local(p, c, hw, R, p["L"] + np.array([-4.0, 0, 4]), rad_add=TR_RAD)
    X = np.einsum("pij,mj->pmi", F.RHG[Pi], loc)
    car = ch.members[[m.name for m in ch.members].index("carriage")]
    Xc = car.D[Pi] * (car.fixed_rho * (R + TR_RAD + CAR_GAP + 6) / (R + TR_RAD + CAR_GAP))[None, :, None]   # approx top
    Y = np.concatenate([X, Xc], 1); m = Y.shape[1]
    d = K.dist_many(B, np.repeat(Pi, m), Y.reshape(-1, 3)).reshape(len(Pi), m).min(1)
    n_out = 0
    for j, i in enumerate(Pi):
        if d[j] < 0: B.res[i] = np.append(B.res[i], d[j]); n_out += 1
    r = B.report(); rep.update({k: r[k] for k in ("reach", "follow", "inband14", "inband10", "contact", "gap")}); rep["outer_contact_poses"] = n_out
    return rep


def evaluate(B, p, **kw):
    if getattr(B, "_kitF", None) is None: B._kitF = K.frames(B)
    rep = K.evaluate(B, build, p, **kw)
    return outer_contact(B, p, rep)


SW = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")


def sweep(B, configs, out=SW, log=print):
    rows = json.load(open(out)) if os.path.exists(out) else []
    best = min(rows, key=lambda e: e["gap"]) if rows else None
    for p in configs:
        r = evaluate(B, dict(p))
        e = dict(k=len(rows), t=K.now(), params=p, **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                 closure=r["closure"], mass_g=r["mass_g"], ring_R=r.get("ring_R"), opening=r.get("opening"), flips=r["flips"],
                 collide=r["collide"], inband_member=r["inband_member"])
        rows.append(e); json.dump(rows, open(out + ".tmp", "w"), indent=1); os.replace(out + ".tmp", out)
        if best is None or e["gap"] < best["gap"]:
            best = e; K.log_event(f"seed-2r-cring new best gap {e['gap']} (reach {e['reach']}, follow {e['follow']}, in-band14 {e['inband14']}, contact {e['contact']}) at config {e['k']}")
        if log: log(f"[{e['k']}] gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} ib10 {e['inband10']} contact {e['contact']} clos {e['closure']} R {e['ring_R']} open {e['opening']} flips {e['flips']} coll {e['collide']} | {e['inband_member']}", flush=True)
    return best, rows


def metal(pose, frames, params):
    """bench contract: metal sample points of pose index `pose` (int, bench index) or None; uses the last evaluation"""
    L = getattr(frames, "_kit_last", None)
    if L is None or not L["take"][pose]: return None
    return np.concatenate([L["pts"][m.name][pose] for m in L["chain"].members], 0)


def configs(base=PARAMS, grid=SWEEP):
    keys = list(grid)
    return [dict(base, **dict(zip(keys, v))) for v in itertools.product(*(grid[k] for k in keys))]


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    B = K.bench(60, 160); B._kitF = K.frames(B)
    if a[0] == "check":
        r = evaluate(B, dict(PARAMS)); print(r)
    elif a[0] == "sweep":
        best, rows = sweep(B, configs()); print("BEST", best)
    elif a[0] == "sweep2":                    # u1 (singularity-free vs low over the shoulder) x C span (axial travel) x level
        base = dict(PARAMS, q_ring=0.9, q=0.95)
        cf = [dict(base, az=az, el=el, cov=cov) for (az, el) in ((125.0, 45.0), (60.0, 70.0), (2.4, 80.7)) for cov in (0.6, 0.95)]
        cf += [dict(base, az=125.0, el=45.0, cov=0.6, L=160.0, tilt=12.0), dict(base, az=125.0, el=45.0, cov=0.6, sigma=-1)]
        best, rows = sweep(B, cf); print("BEST", best)
