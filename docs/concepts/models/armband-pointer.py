"""armband-pointer: a closed thin-section ring bearing round the distal upper arm, coaxial (or near-coaxial) with the
humerus, under a 2R donut pointer (3 ACTIVE DOF, 0 passive, 0 passive translations). Built on the shared kit
(tools/concept_kit.py, KIT.md); helpers for rigid non-GH-ray parts follow pointer-cslide.py.

Topology (scapula handler -> user's upper-arm cuff):
    scapula base --J1 (O20 hub on a1 = bvec(az, el), S-fixed)--> link 1 (strap a1 -> p2)
    --J2 (O20 hub on p2: angle A1 from a1 and A2 from d3; the pointer is A1 = A2 = 90)--> link 2 = strap from hub 2 over
    the shoulder to the lateral arm at station s0 + a SPAR fixed in the pointing frame P = [p2 x d3, d3 x ., d3] down
    the arm at P-angle c to the ring stator --J3 (closed ring bearing about d3 at station s)--> rotor housing bolted into
    the user's upper-arm cuff (BOTTOM; the cuff shell is the user's part).
d3 = the J3 axis through GH: the humerus long axis (band HG frame -y) tilted by (tilt, tilt_a) to centre the ring on
the arm section. Kinematics: spherical 3R, all three angles fixed by the humerus orientation in closed form (K1 with the
A1/A2 cones); fold / singularity margin K.FOLD_MARGIN in th = angle(a1, d3) (the metric every verified row uses).
No passive coordinate (R17). No gears, pulleys, cables (MVP1).

Parts at real size (skin-facing surfaces sampled ~2 x 2 mm; every pair K6 >= 1 mm or by construction):
  * hub1, hub2: O20 hubs (kit K4, 12.25 stack). link 1 lower member at J2, link 2 upper at J2 (over link 1).
  * link2a: 12 x 3 strap (K3 fitted, 60 deg climb) from hub 2 to the arm direction unit(s0 d3 + 45 cdir).
  * spar: 16 x 4 bar in P from s0 to the ring's far side, its underside per sample = quantile q over the closing fit
    poses of the radial march from the J3 axis (first radius with skin distance >= 2 mm) at its P-angle (the arm
    twists under it), K5 climb along the bar, and >= the ring's outer radius over the ring (it carries the stator).
  * ring: a Kaydon Reali-Slim KA..XP0 (6.35 x 6.35 mm 4-point) at bore radius `bore` with 1.5 mm housings each side:
    skin face (rotor housing bore) at bore - 1.5, outer face (stator housing) at bore + 6.35 + 1.5, axial width
    ring_w (10). The skin face (full 360 deg, 2 mm grid) is a K6 member scored for in-band; the outer cylinder and the
    two side annuli are contact-checked (they face the trunk / forearm in adducted and flexed poses).
Clearances by construction: ring-spar (stator bolted to the spar), link2a-spar (one bent bar). Everything else: K6.
Continuity: K2 dense (values + axes). Held-out clips never loaded.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/armband-pointer.py check '{json params}'
"""
import itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "armband-pointer"
NAME = "Closed thin-section armband at the distal arm + 2R donut pointer with a lateral spar"
SEC, WALL = 6.35, 1.5                                         # KA..XP0 radial section, housing wall each side
PARAMS = dict(az=30.0, el=70.0, sigma=1, A1=90.0, A2=90.0, tilt=0.0, tilt_a=0.0, s=260.0, bore=57.15, ring_w=10.0,
              c=0.0, s0=80.0, q=1.0, q_spar=1.0, r_block=110.0, width=12.0, t_link=3.0, w_spar=16.0, t_spar=4.0)

# ---- fixed-geometry members (ring, spar: about d3, not GH-ray fitted) ----------------------------------------------
_orig_levels = K._levels


def _levels(B, chain, fit, q, mode):
    fixed = [m for m in chain.members if getattr(m, "fixed_rho", None) is not None]
    sub = K.Chain(members=[m for m in chain.members if getattr(m, "fixed_rho", None) is None], ok=chain.ok)
    out = _orig_levels(B, sub, fit, q, mode)
    for m in fixed: out[m.name] = m.fixed_rho.copy()
    return out


K._levels = _levels
EXEMPT = {frozenset(x) for x in (("ring", "spar"), ("link2a", "spar"))}


def _collisions(chain, pts, ok, clear=1.0, overlap=0.5, chunk=24):
    """K.collisions (same code) with the by-construction pairs left out"""
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


def radial_req(B, I, Z, U, clr=2.0, r0=12.0, r_block=110.0):
    """per point: first radius r >= r0 from the axis point Z along the radial unit U (pose I) with skin distance >= clr
    (Lipschitz march). Still blocked at r_block (the trunk pressed on the arm) -> 0 (the pose becomes a contact pose)"""
    R = np.full(len(Z), r0); act = np.ones(len(Z), bool)
    for _ in range(400):
        a = np.nonzero(act)[0]
        if not len(a): break
        g = K.dist_many(B, I[a], Z[a] + R[a, None] * U[a]); done = g >= clr
        act[a[done]] = False; R[a[~done]] += np.maximum(0.25, clr - g[~done]); act &= R < r_block
    return np.where(R < r_block, R, 0.0)


def fixed_member(name, X, joints, t):
    """a rigid part with thorax points X (P, m, 3) (its skin face); t = radial thickness (K6)"""
    rho = np.linalg.norm(X, axis=-1); D = X / rho[..., None]
    m = K.Member(name, D, t=float(t), joints=tuple(joints), r_ref=float(rho.max()))
    m.fixed_rho = rho[0]
    return m


def strap(name, u, v, joints, width=12.0, t=3.0, ramp_to=(), r_ref=70.0, **kw):
    """K.strap_member with the sample layout made at r_ref (2 x 2 mm there): hub 2 / link 2 ride 90-160 mm from GH in this
    design, where the kit's 70-mm layout spaces samples 4-11 mm apart (the audit's sparse-sampling flag)"""
    D = K.strap_dirs(u, v, None, width=width, r_ref=r_ref); ns, nc = D.shape[1:3]
    n_end = int(math.ceil((K.HUB_R + 2.0) * r_ref / 70.0 / 2.0)) + 1; sidx = np.repeat(np.arange(ns), nc); ramps = []
    for (h, dz), m in zip(ramp_to, (sidx < n_end, sidx >= ns - n_end)):
        if h: ramps.append((m, h, dz))
    return K.Member(name, D.reshape(len(D), -1, 3), t=t, width=width, joints=tuple(joints), grid=(ns, nc), climb_deg=60.0,
                    ramps=ramps, strap=True, r_ref=r_ref, **kw)


def kin(F, p):
    a1 = F.S(K.bvec(p["az"], p["el"])); d3 = F.HG(K.wdir(p["tilt"], p["tilt_a"]))
    p2, ok, margin = K.closure(a1, d3, p["A1"], p["A2"], p["sigma"], margin_deg=K.FOLD_MARGIN)
    xP = K.unit(np.cross(p2, d3)); yP = np.cross(d3, xP)
    E1 = F.HG(np.array([0.0, 0, 1])); E1 = K.unit(E1 - (E1 * d3).sum(-1, keepdims=True) * d3)   # arm lateral about d3
    q3 = np.degrees(np.arctan2((E1 * yP).sum(-1), (E1 * xP).sum(-1)))                           # twist of the rotor in P
    th = np.degrees(np.arccos(np.clip((a1 * d3).sum(-1), -1, 1)))
    return a1, p2, d3, xP, yP, q3, th, ok, margin


def circ(d3, e1, e2, rows, ang_deg, R):
    """(P, rows * n, 3): w d3 + R (cos a e1 + sin a e2); R scalar or (rows, n)"""
    a = np.radians(np.asarray(ang_deg, float)); E = np.cos(a)[None, :, None] * e1[:, None] + np.sin(a)[None, :, None] * e2[:, None]
    R = np.broadcast_to(np.asarray(R, float), (len(rows), len(a)))
    X = np.asarray(rows)[None, :, None, None] * d3[:, None, None] + R[None, :, :, None] * E[:, None]
    return X.reshape(len(d3), -1, 3)


def spar_layout(p):
    r_out = p["bore"] + SEC + WALL; rows = np.arange(p["s0"], p["s"] + p["ring_w"] / 2 + 1e-6, 2.0)
    cols = p["c"] + np.degrees(np.arange(-p["w_spar"] / 2, p["w_spar"] / 2 + 1e-6, 2.0) / max(r_out, 45.0))
    return rows, cols, r_out


_CACHE = {}


def design(B, p):
    """the spar profile from the bench data (the closing fit poses), then fixed: per sample quantile q_spar of the radial
    requirement about d3 at its P-angle, K5 climb along the bar, >= the ring's outer radius over the ring"""
    key = tuple(sorted((k, v) for k, v in p.items() if not isinstance(v, (list, dict))))
    if key in _CACHE: return _CACHE[key]
    F = B._kitF; a1, p2, d3, xP, yP, q3, th, ok, margin = kin(F, p); Pi = np.nonzero(ok)[0]
    rows, cols, r_out = spar_layout(p)
    if not len(Pi): _CACHE[key] = None; return None
    U = circ(d3[Pi], xP[Pi], yP[Pi], [0.0], cols, 1.0); U = np.tile(U, (1, len(rows), 1))
    Z = np.repeat(rows, len(cols))[None, :, None] * d3[Pi][:, None]
    I = np.repeat(Pi, U.shape[1])
    R = radial_req(B, I, Z.reshape(-1, 3), U.reshape(-1, 3), r_block=p["r_block"]).reshape(len(Pi), len(rows), len(cols))
    qq = p["q_spar"]; prof = np.quantile(R, qq, axis=0) if qq < 1 else R.max(0)
    prof = np.maximum(prof, 20.0)
    ring_rows = np.abs(rows - p["s"]) <= p["ring_w"] / 2 + 1e-6; prof[ring_rows] = np.maximum(prof[ring_rows], r_out)
    sl = math.tan(math.radians(60.0)); x = rows - rows[0]                                          # K5 climb (raises only)
    prof = (prof[None, :, :] - sl * np.abs(x[:, None, None] - x[None, :, None])).max(1)
    _CACHE[key] = dict(prof=prof, rows=rows, cols=cols, r_out=r_out); return _CACHE[key]


def ring_layout(p):
    r_face = p["bore"] - WALL; rows = p["s"] + np.arange(-p["ring_w"] / 2, p["ring_w"] / 2 + 1e-6, 2.0)
    n = int(math.ceil(2 * math.pi * r_face / 2.0)); ang = np.arange(n) * 360.0 / n
    return rows, ang, r_face


def build_chain(B, F, p):
    if getattr(B, "_kitF", None) is None: B._kitF = K.frames(B)
    a1, p2, d3, xP, yP, q3, th, ok, margin = kin(F, p)
    D = design(B, p); w, t = p["width"], p["t_link"]
    hubs = [K.hub_member("hub1", a1, "J1"), K.hub_member("hub2", p2, "J2")]
    rr = p.get("r_ref", 140.0)
    link1 = strap("link1", a1, p2, ("J1", "J2"), width=w, t=t, ramp_to=(("hub1", K.STACK), ("hub2", 0.0)), r_ref=rr)
    cr = math.radians(p["c"]); cdir = math.cos(cr) * xP + math.sin(cr) * yP
    att = K.unit(p["s0"] * d3 + 45.0 * cdir)
    link2a = strap("link2a", p2, att, ("J2", "J3"), width=w, t=t, ramp_to=(("hub2", K.STACK), (None, 0.0)),
                   over=[("link1", 1.0)], r_ref=rr)
    members = hubs + [link1, link2a]
    if D is not None:
        Xs = circ(d3, xP, yP, D["rows"], D["cols"], D["prof"])
        members.append(fixed_member("spar", Xs, ("J2", "J3"), p["t_spar"]))
        rows, ang, r_face = ring_layout(p)
        members.append(fixed_member("ring", circ(d3, xP, yP, rows, ang, r_face), ("J3",), SEC + 2 * WALL))
    q = np.stack([K.axis_angle(a1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, a1, d3), q3], -1)
    res = K.closure_residual(a1, d3, p2, p["A1"], p["A2"])
    return K.Chain(members=members, ok=ok, q=q, joints=dict(J1=a1, J2=p2, J3=d3), hubless=("J3",),
                   info=dict(residual_deg=round(float(res[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None,
                             th_min=round(float(th[ok].min()), 1) if ok.any() else None,
                             th_max=round(float(th[ok].max()), 1) if ok.any() else None))


def outer_contact(B, p, rep):
    """contact-only check of the ring faces that meet the trunk / forearm: outer cylinder (stator housing) and the two
    side annuli (bore - 1.5 .. outer). A pose with any of them inside the skin is a contact pose (B.res gets it)."""
    L = B._kit_last; take = L["take"]; Pi = np.nonzero(take)[0]; rep["outer_contact_poses"] = 0
    if not len(Pi): return rep
    F = B._kitF; a1, p2, d3, xP, yP, q3, th, ok, margin = kin(F, p)
    rows, ang, r_face = ring_layout(p); r_out = p["bore"] + SEC + WALL
    Xo = circ(d3[Pi], xP[Pi], yP[Pi], rows, ang, r_out)
    sides = []
    for r in np.arange(r_face + 2.0, r_out, 2.0):
        sides.append(circ(d3[Pi], xP[Pi], yP[Pi], [rows[0], rows[-1]], ang, r))
    Y = np.concatenate([Xo] + sides, 1); m = Y.shape[1]
    d = K.dist_many(B, np.repeat(Pi, m), Y.reshape(-1, 3)).reshape(len(Pi), m).min(1); n_out = 0
    for j, i in enumerate(Pi):
        if d[j] < 0: B.res[i] = np.append(B.res[i], d[j]); n_out += 1
    r = B.report(); rep.update({k: r[k] for k in ("reach", "follow", "inband14", "inband10", "contact", "gap")})
    rep["outer_contact_poses"] = n_out
    return rep


def bench_eval(B, params):
    p = dict(PARAMS, **params)
    if getattr(B, "_kitF", None) is None: B._kitF = K.frames(B)
    rep = K.evaluate(B, build_chain, p)
    rep = outer_contact(B, p, rep)
    return json.loads(json.dumps(rep, default=lambda o: o.item() if hasattr(o, "item") else str(o)))


def metal(pose, frames, params):
    L = getattr(frames, "_kit_last", None)
    if L is None or not L["take"][pose]: return None
    return np.concatenate([L["pts"][m.name][pose] for m in L["chain"].members], 0)


def ring_bound(B, F, stations=(160, 180, 200, 220, 240, 260, 280, 300), tilts=((0, 0),), secs=(8.0, 9.35), rmax=120.0):
    """PARAMETER-FREE bound for ANY closed ring about a GH axis (the J3 axis wdir(tilt)): per pose and station, march the
    skin distance out from the axis every 10 deg to rmax; r0 = max over angles of the first radius with dist >= clr (arm
    cleared; clr 0 = the most generous), r1 = min over angles of the first radius beyond it with dist < 0 (trunk, axilla,
    forearm, head). A ring of radial section sec fits iff r0 <= r_face and r_face + sec <= r1. Prints per-pose-bore
    and best fixed-bore shares (clip = follow ceiling, ws = reach ceiling) and the gap lower bound from them."""
    P = len(B.poses); kind = np.array(B.kind); ANG = np.arange(0, 360, 10.0); R = np.arange(0, rmax + 1e-6, 2.0); out = []
    for (td, ta) in tilts:
        d3 = F.HG(K.wdir(td, ta)); E1 = F.HG(np.array([0, 0, 1.0])); E1 = K.unit(E1 - (E1 * d3).sum(-1, keepdims=True) * d3)
        E2 = np.cross(E1, d3); a = np.radians(ANG); U = np.cos(a)[None, :, None] * E1[:, None] + np.sin(a)[None, :, None] * E2[:, None]
        for s in stations:
            X = s * d3[:, None, None] + R[None, None, :, None] * U[:, :, None]
            D = K.dist_many(B, np.repeat(np.arange(P), X[0].size // 3), X.reshape(-1, 3)).reshape(P, len(ANG), len(R))
            idx = np.arange(len(R))[None, None]; o0 = D >= 0; f0 = np.where(o0.any(-1), o0.argmax(-1), len(R) - 1)
            r1 = np.where(((D < 0) & (idx > f0[..., None])).any(-1), R[((D < 0) & (idx > f0[..., None])).argmax(-1)], 999).min(1)
            for clr in (0.0, 2.0):
                o = D >= clr; r0 = np.where(o.any(-1), R[np.where(o.any(-1), o.argmax(-1), 0)], 999).max(1)
                for sec in secs:
                    pp = r0 + sec <= r1; best = None
                    for rf in np.arange(30, rmax - sec + 1e-6, 0.5):
                        fit = (r0 <= rf) & (rf + sec <= r1); fo, re = fit[kind == "clip"].mean(), fit[kind == "ws"].mean()
                        g = 100 * (max(0, .95 - fo) + max(0, .90 - re))
                        if best is None or g < best[0]: best = (g, rf, fo, re)
                    row = dict(tilt=(td, ta), s=s, clr=clr, sec=sec, pp_clip=round(float(pp[kind == "clip"].mean()), 3),
                               pp_ws=round(float(pp[kind == "ws"].mean()), 3),
                               pp_gap_lb=round(100 * (max(0, .95 - pp[kind == "clip"].mean()) + max(0, .90 - pp[kind == "ws"].mean())), 1),
                               fixed_gap_lb=round(best[0], 1), r_face=best[1], follow_ub=round(float(best[2]), 3), reach_ub=round(float(best[3]), 3),
                               arm_meets_body=round(float((r0 >= 999).mean()), 3))
                    out.append(row); print(json.dumps(row), flush=True)
    return out


def ring_bound2(B, F, stations=(240, 260, 280, 300), tilts=((0, 0),), rmax=120.0):
    """the bound with the general ring test (supersedes ring_bound, which assumed the ring centre inside the arm and so
    mis-scored tilted axes whose centre leaves the arm): a ring of face radius rf and section sec about the J3 axis at
    station s fits a pose iff (a) no skin (dist < 0) anywhere in its annulus [rf, rf + sec] on every ray (36 rays, 2 mm
    lattice) and (b) it encloses the humerus line's point in its plane (offset e < rf), i.e. the arm passes through it.
    sec 8 = the thinnest real ring + housings; sec 6 gives the lattice error to the ring. Fixed bore = one rf for all."""
    P = len(B.poses); kind = np.array(B.kind); ANG = np.arange(0, 360, 10.0); R = np.arange(0, rmax + 1e-6, 2.0); out = []
    th = F.HG(K.wdir(0, 0))
    for (td, ta) in tilts:
        d3 = F.HG(K.wdir(td, ta)); E1 = F.HG(np.array([0, 0, 1.0])); E1 = K.unit(E1 - (E1 * d3).sum(-1, keepdims=True) * d3)
        E2 = np.cross(E1, d3); a = np.radians(ANG); U = np.cos(a)[None, :, None] * E1[:, None] + np.sin(a)[None, :, None] * E2[:, None]
        for s in stations:
            X = s * d3[:, None, None] + R[None, None, :, None] * U[:, :, None]
            D = K.dist_many(B, np.repeat(np.arange(P), X[0].size // 3), X.reshape(-1, 3)).reshape(P, len(ANG), len(R))
            lam = s / np.clip((th * d3).sum(-1), 1e-3, None); e = np.linalg.norm(lam[:, None] * th - s * d3, axis=-1)
            C = np.concatenate([np.zeros((P, len(ANG), 1)), np.cumsum(D < 0, -1)], -1)       # C[..., j] = # inside in R[:j]
            for sec in (8.0, 6.0):
                n = int(round(sec / 2.0)) + 1; best = None; pp = np.zeros(P, bool)
                fits = []
                for j in range(1, len(R) - n + 1):
                    free = ((C[..., j + n] - C[..., j]) == 0).all(1) & (e < R[j]); pp |= free; fits.append(free)
                    fo, re = free[kind == "clip"].mean(), free[kind == "ws"].mean(); g = 100 * (max(0, .95 - fo) + max(0, .90 - re))
                    if best is None or g < best[0]: best = (g, R[j], fo, re)
                row = dict(tilt=(td, ta), s=s, sec=sec, e_med=round(float(np.median(e)), 1), pp_clip=round(float(pp[kind == "clip"].mean()), 3),
                           pp_ws=round(float(pp[kind == "ws"].mean()), 3),
                           pp_gap_lb=round(100 * (max(0, .95 - pp[kind == "clip"].mean()) + max(0, .90 - pp[kind == "ws"].mean())), 1),
                           fixed_gap_lb=round(best[0], 1), r_face=float(best[1]), follow_ub=round(float(best[2]), 3), reach_ub=round(float(best[3]), 3))
                out.append(row); print(json.dumps(row), flush=True)
    return out


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    if a[0] == "bound2":                      # bound2 '{"nc":60,"nw":160,"stations":[...],"tilts":[[0,0]]}'  (CB_EXACT=1 for the exact path)
        o = json.loads(a[1]) if len(a) > 1 else {}
        B = K.bench(o.get("nc", 60), o.get("nw", 160)); F = K.frames(B)
        ring_bound2(B, F, stations=o.get("stations", (240, 260, 280, 300)), tilts=[tuple(t) for t in o.get("tilts", [[0, 0]])])
        sys.exit(0)
    if a[0] == "bound":                       # bound '{"nc":60,"nw":160,"stations":[...],"tilts":[[0,0]]}'  (CB_EXACT=1 for the exact path)
        o = json.loads(a[1]) if len(a) > 1 else {}
        B = K.bench(o.get("nc", 60), o.get("nw", 160)); F = K.frames(B)
        ring_bound(B, F, stations=o.get("stations", (160, 180, 200, 220, 240, 260, 280, 300)), tilts=[tuple(t) for t in o.get("tilts", [[0, 0]])])
        sys.exit(0)
    B = K.bench(60, 160); B._kitF = K.frames(B)
    p = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 else {}))
    if a[0] == "check":
        import time; t0 = time.time(); r = bench_eval(B, p); print(round(time.time() - t0, 1), "s")
        print({k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "honest", "outer_contact_poses", "inband_member", "residual_deg", "min_margin", "th_min", "th_max", "audit")})
        L = B._kit_last; tk = L["ok"] & ~L["hit"]; Pi = np.nonzero(tk)[0]
        cs = {}
        for m in L["chain"].members:
            X = L["pts"][m.name][Pi]; d = K.dist_many(B, np.repeat(Pi, X.shape[1]), X.reshape(-1, 3)).reshape(len(Pi), -1)
            cs[m.name] = (int((d.min(1) < 0).sum()), round(float(np.median(d)), 1))
        print("closing + K6-clear poses", len(Pi), "| per member: (poses with it inside the skin, median skin distance mm):", cs)
        ov = [i for i in range(len(B.res)) if B.res[i] is not None and np.min(B.res[i]) < 0]
        pz = np.array([(q["plane"], q["elev"], q["axial"]) for q in B.poses])
        print("contact poses", len(ov), "| of them elev < 40:", int(sum(pz[i, 1] < 40 for i in ov)), "| overhead taken (ws elev >= 140):",
              int(sum(1 for i in range(len(B.res)) if B.kind[i] == "ws" and pz[i, 1] >= 140 and B.res[i] is not None and np.min(B.res[i]) >= 0)),
              "/", int(sum(1 for i in range(len(B.res)) if B.kind[i] == "ws" and pz[i, 1] >= 140)))
    elif a[0] == "sweep":                     # sweep '{}' configs.json : append every evaluated config to the sweep file, in order
        SW = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
        for cfg in json.load(open(a[2])):
            pp = dict(PARAMS, **cfg)
            try: r = bench_eval(B, pp)
            except Exception as ex: print("FAIL", cfg, ex, flush=True); continue
            rows = json.load(open(SW)) if os.path.exists(SW) else []
            rows.append(dict(k=len(rows), t=K.now(), params=pp, **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                             closure=r.get("closure"), honest=r.get("honest"), kmode=r.get("kmode"), outer_contact_poses=r.get("outer_contact_poses"),
                             inband_member=r.get("inband_member"), min_margin=r.get("min_margin"), audit=r.get("audit")))
            json.dump(rows, open(SW + ".tmp", "w"), indent=1); os.replace(SW + ".tmp", SW)
            print(len(rows) - 1, cfg, "gap", r["gap"], "reach", r["reach"], "follow", r["follow"], "ib14", r["inband14"], "contact", r["contact"],
                  "outer", r.get("outer_contact_poses"), r.get("inband_member"), flush=True)
