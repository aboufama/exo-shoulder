"""fraction-pauldron: graded telescoping lames (a pauldron whose pieces each turn a FRACTION of the arm's motion) on a
spherical gimbal, twist at the cuff. Lens: proximity atlas (docs/research/proximity_atlas.md).

Why this family, and why this realisation (the type synthesis, measured with the atlas - see docs/concepts/fraction-pauldron.md):
the atlas says skin over the cap moves with graded fractions of the arm's TWIST-FREE swing (S * swing^t). Exact 2-DOF
swing fractions are not holonomically realisable with 1-D couplings (a member at swing^t has every point sweeping a 2-D
region relative to both the scapula and the arm, so no slot / groove / rail can hold it; rolling balls are
non-holonomic and drift). What IS realisable exactly, unpowered and determined, is a fraction of ONE angle about ONE
axis: coaxial members coupled by rolling cages (bearing-cage principle: a roller rolling between member k-1 and k+1,
its axle on member k, puts k at a fixed weighted mean of its neighbours; stepped rollers set the weights) or by a
lazy-tongs. So the mechanism distributes the gimbal's OUTER angle over N lames:

    scapula plate S --[N lames telescoping about axis x, lame k at fraction g_k of alpha, cage-coupled]--> tip T (g=1)
    T --J2: O20 hub about z (z perpendicular to x, carried by T), angle beta--> arm strap A
    A --J3: carriage on a thin-section arc rail around the arm (cone gamma about the humerus axis), twist psi--> cuff
    rail on the humerus side (BOTTOM) + K7 neck to BOTTOM's bar

3 ACTIVE DOF (alpha = the telescope's total, beta = J2, psi = the cuff arc). PASSIVE: the N-1 inner lame positions,
each set by its cage (holonomic: all lames turn about the same axis x, so fractions compose exactly); nothing sags.
alpha, beta = the Fick angles of the arm direction about x in the scapula frame (alpha the azimuth about x, beta the
polar change; inner axis z0 = x X a0, a0 = the rest arm direction; x perpendicular to a0 gives the Cardan pair);
gimbal lock when the arm comes within lock_deg of +-x (pose not taken).

Geometry at real size (kit conventions, tools/concept_kit.py, same sampling as the baseline): every lame / plate is a
strap of width w along the great circle perpendicular to x (the telescope's own circle: relative motion of consecutive
lames is rotation about x, so the sliding tracks are constant-radius along that circle - enforced over each overlap
zone, which is also where the next lame stacks on top: outer underside >= inner underside + t + gap). Lame t = 2 mm,
running gap 0.5 (rollers live in windows of the middle lame). J2 = O20 hub (T plate at F, A from F + 3.15, crown
F + 12.25). A = 8 x 3 strap from J2 to the carriage. Rail = 8 x 3 arc around the arm covering the twist range of the
poses taken (+ carriage half-length), humerus-fixed; carriage = 16 x 10 x 3 on A. Neck K7 to BOTTOM's bar.

Every face is capped at RMAX = 130 mm from GH (a pose whose skin would need more counts as contact).
Taken (bench + kit honesty rules): Cardan solution away from gimbal lock, alpha within the telescope's stroke, psi on
the rail, K2 continuity along the interpolated motion, K6 no part collisions, metal never inside the skin.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/fraction-pauldron.py check|sweep|redteam
"""
import json, math, os, sys, time, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                       # noqa: E402

ID = "fraction-pauldron"
D2R = math.pi / 180
SWEEP = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
T_LAME, GAP, T_STRAP = 2.0, 0.6, 3.0
REV = 3           # model revision in each sweep entry. rev 1: rail underside free-shaped (a circular track cannot be). rev 2: no cap on the
                  # fitted radius (a part needing no clearance in >1-q of poses floated at 400 mm). rev 3: every face capped at RMAX
                  # from GH - poses whose skin needs more count as contact. Only rev 3 is reported.
RMAX = 130.0
SAME_PART = {frozenset(x) for x in (("hubT", "tip"), ("hubA", "strapA"), ("strapA", "carriage"), ("hubA", "carriage"), ("rail", "neck"))}


def ddir(lat, lon):
    """scapula-frame direction (deg), atlas convention: x anterior, y up, z lateral; lon 0 anterior, 90 lateral"""
    la, lo = lat * D2R, lon * D2R
    return np.array([math.cos(la) * math.cos(lo), math.sin(la), math.cos(la) * math.sin(lo)])


def rot(k, ang):
    """rotation matrices about unit axis k (3,) or (P, 3) by ang (P,) rad -> (P, 3, 3)"""
    ang = np.asarray(ang, float); k = np.broadcast_to(np.asarray(k, float), ang.shape + (3,))
    K_ = np.zeros(ang.shape + (3, 3)); K_[..., 0, 1], K_[..., 0, 2], K_[..., 1, 2] = -k[..., 2], k[..., 1], -k[..., 0]
    K_[..., 1, 0], K_[..., 2, 0], K_[..., 2, 1] = k[..., 2], -k[..., 1], k[..., 0]
    s, c = np.sin(ang)[..., None, None], np.cos(ang)[..., None, None]
    return np.eye(3) + s * K_ + (1 - c) * (K_ @ K_)


def arm_s(F):
    """arm direction (down the humerus) in the scapula frame, per pose"""
    return np.einsum("pji,pj->pi", F.RS, F.H(np.array([0.0, -1.0, 0.0])))


def axes(p):
    """a0 rest arm direction, x the outer (telescope) axis fixed in S, z0 = unit(x X a0) the inner axis at rest"""
    a0 = K.unit(np.array(p["a0"])); x = ddir(p["x_lat"], p["x_lon"])
    z0 = K.unit(np.cross(x, a0)); return a0, x, z0


def cardan(F, p):
    """Fick/Cardan angles of the arm about the outer axis x: Rot(x, alpha) Rot(z0, -beta) a0 = a.
    beta changes the polar angle from x, alpha the azimuth about x (x perpendicular to a0: the Cardan pair)."""
    a0, x, z0 = axes(p); a = arm_s(F)
    th = np.arccos(np.clip(a @ x, -1, 1)); th0 = math.acos(float(np.clip(a0 @ x, -1, 1)))
    be = th0 - th                                                               # Rot(z0, -beta) a0 has polar angle th0 - beta
    b = np.einsum("pij,j->pi", rot(z0, -be), a0)
    al = np.radians(K.axis_angle(np.broadcast_to(x, b.shape), b, a))
    return al, be


def twist_az(F, p, Rc):
    """azimuth (deg) of the A-carriage point around the humerus axis, in the humerus (body_pose) frame"""
    a0, x, z0 = axes(p); g = p["gamma"] * D2R
    c = math.cos(g) * a0 + math.sin(g) * z0 * p["zsign"]                      # carriage direction in A coords
    cs = np.einsum("pij,j->pi", Rc, c)                                          # scapula coords
    ch = np.einsum("pji,pj->pi", F.RH, np.einsum("pij,pj->pi", F.RS, cs))      # humerus coords
    return np.degrees(np.arctan2(ch[:, 0], ch[:, 2])), c


def fractions(p):
    n = int(p["n"]); e = p.get("expo", 1.0)
    return [0.0] + [(k / n) ** e for k in range(1, n)] + [1.0]               # S plate, lames 1..n-1, tip T


def layout(p):
    """cage-coupled telescope along the circle perpendicular to x, in collapsed stack coords s (= side * azimuth, deg).
    Roller set R_k rides on stage k (k = 1..n-1) between stage k-1 (below, race ahead of it by the stroke D_k) and
    stage k+1 (above, race behind it by D_k+1); stage k spans the union of its own window and the two races it
    offers. Returns fractions g, own-frame azimuth intervals per stage, race zones per stage (own azimuth), strokes."""
    g = fractions(p); n = len(g) - 1; amin, amax = p["amin"], p["amax"]; ov = p["ov"]; sd = p["side"]
    D = [None] + [(g[k] - g[k - 1]) * (amax - amin) for k in range(1, n + 1)]
    ref = amin if sd > 0 else amax
    c = {k: (k - 1) * p["pitch"] for k in range(1, n)}                           # roller sets (collapsed s)
    ext = {k: [] for k in range(n + 1)}; race = {k: [] for k in range(n + 1)}
    for k in range(1, n):
        ext[k].append((c[k] - ov / 2, c[k] + ov / 2))
        r_lo = (c[k] - ov / 2, c[k] + ov / 2 + D[k]); race[k - 1].append(r_lo); ext[k - 1].append(r_lo)
        r_hi = (c[k] - ov / 2 - D[k + 1], c[k] + ov / 2); race[k + 1].append(r_hi); ext[k + 1].append(r_hi)
    if n == 1:                                                                   # plain curved slide: plate rail, tip carriage
        race[0].append((0.0, ov + D[1])); ext[0].append(race[0][0]); race[1].append((0.0, ov)); ext[1].append((0.0, ov))
    top = max(hi for lo, hi in ext[n]); hub = top + p["hub_gap"]                  # J2 hub centre, past the tip's last race
    ext[n].append((top, hub + p["hub_ext"]))
    lo0 = min(lo for lo, hi in ext[0]); ext[0].append((lo0 - p["ls"], lo0))       # the plate's anchor on the scapula handler
    shift = sd * ref - hub                                                       # hub at azimuth ref when collapsed
    own, zones = [], []
    for k in range(n + 1):
        lo = min(a for a, b in ext[k]) + shift; hi = max(b for a, b in ext[k]) + shift
        o = sorted((sd * lo - g[k] * ref, sd * hi - g[k] * ref)); own.append(tuple(o))
        zones.append([tuple(sorted((sd * (a + shift) - g[k] * ref, sd * (b + shift) - g[k] * ref))) for a, b in race[k]])
    return g, own, zones, D


def strap_on_circle(x, z0, lo, hi, width, Rm, step=2.0, r_ref=70.0):
    """unit dirs (P, ns, nc, 3) of a strap on the great circle perpendicular to x, azimuth lo..hi (deg, own frame),
    member rotation Rm (P, 3, 3) in scapula coords then RS applied by caller"""
    y = np.cross(x, z0); ang = (hi - lo) * D2R; ns = max(3, int(ang * r_ref / step) + 1)
    t = np.linspace(lo, hi, ns) * D2R; C = np.cos(t)[:, None] * z0 + np.sin(t)[:, None] * y   # (ns, 3)
    cs = np.arange(-width / 2, width / 2 + 1e-6, step) / r_ref
    U = K.unit(C[:, None, :] * np.cos(cs)[None, :, None] + x[None, None, :] * np.sin(cs)[None, :, None])  # (ns, nc, 3)
    return np.einsum("pij,mnj->pmni", Rm, U), np.degrees(t)


def design(B, F, p):
    """fill the design constants that must not depend on the evaluated frames: a0, strokes, rail span"""
    p = dict(p)
    if "a0" not in p:
        ref = int(np.argmin([q["elev"] for q in B.poses])); p["a0"] = arm_s(F)[ref].tolist()
    if p.get("zsign", 0) == 0:                                                  # J2 hub on the lateral side at rest
        a0, x, z0 = axes(p); p["zsign"] = 1 if z0[2] >= 0 else -1
    al, be = cardan(F, p); al, be = np.degrees(al), np.degrees(be)
    th0 = math.degrees(math.acos(float(np.clip(axes(p)[0] @ axes(p)[1], -1, 1)))); ok = (th0 - be >= p["lock"]) & (th0 - be <= 180 - p["lock"])
    lo, hi = np.quantile(al[ok], [1 - p["cov"], p["cov"]]); p["amin"], p["amax"] = float(lo), float(hi)
    okk = ok & (al >= lo) & (al <= hi)
    a0, x, z0 = axes(p); Rc = np.einsum("pij,pjk->pik", rot(x, al * D2R), rot(z0, -be * D2R))
    ps, _ = twist_az(F, p, Rc); ps = ps[okk]
    mid = math.degrees(math.atan2(np.sin(ps * D2R).mean(), np.cos(ps * D2R).mean()))
    rel = (ps - mid + 180) % 360 - 180; rc = p.get("rcov", p["cov"]); plo, phi = np.quantile(rel, [1 - rc, rc])
    p["pmid"], p["plo"], p["phi"] = float(mid), float(plo), float(phi)
    return p


def build(B, F, p):
    a0, x, z0 = axes(p); P_ = len(F.RS)
    al, be = cardan(F, p); ald, bed = np.degrees(al), np.degrees(be)
    th0 = math.degrees(math.acos(float(np.clip(a0 @ x, -1, 1))))
    ok = (th0 - bed >= p["lock"]) & (th0 - bed <= 180 - p["lock"]) & (ald >= p["amin"] - 1e-6) & (ald <= p["amax"] + 1e-6)
    Rc = np.einsum("pij,pjk->pik", rot(x, al), rot(z0, -be))                   # A in scapula coords
    psi, c = twist_az(F, p, Rc); rel = (psi - p["pmid"] + 180) % 360 - 180
    ok &= (rel >= p["plo"] - 1e-6) & (rel <= p["phi"] + 1e-6)
    g, own, zones, D = layout(p)
    toT = lambda Rm: np.einsum("pij,pjk->pik", F.RS, Rm)
    mem = []; w = p["w"]
    for k in range(len(g)):
        Rk = toT(rot(x, g[k] * al)); lo, hi = own[k]
        Dd, az = strap_on_circle(x, z0 * p["zsign"], lo, hi, w, Rk)
        nm = "plate" if k == 0 else ("tip" if k == len(g) - 1 else f"lame{k}")
        mem.append(K.Member(nm, Dd.reshape(P_, -1, 3), t=T_LAME, width=w, grid=Dd.shape[1:3], joints=(("J2",) if k == len(g) - 1 else ()),
                            strap=True))
        mem[-1].az = az
    zs = p["zsign"]; zT = toT(rot(x, al)) @ (z0 * zs)                         # J2 axis (thorax)
    RA = toT(Rc)
    hubT = K.Member("hubT", K.cap_dirs(zT), kind="cap", t=T_LAME, width=20.0, joints=("J2",), cell=6.25)
    hubA = K.Member("hubA", K.cap_dirs(zT), kind="cap", t=T_STRAP, off=K.STACK, width=20.0, joints=("J2",), cell=6.25)
    cA = np.einsum("pij,j->pi", RA, c)                                          # carriage direction (thorax)
    zA = np.einsum("pij,j->pi", RA, z0 * zs)
    SA = K.strap_dirs(zA, cA, width=8.0)
    strapA = K.Member("strapA", SA.reshape(P_, -1, 3), t=T_STRAP, off=K.STACK, width=8.0, grid=SA.shape[1:3], joints=("J2", "J3"),
                      climb_deg=60.0, strap=True)
    # carriage on A (16 along the rail x 10 across), at the strap end, same level
    hum = F.H(np.array([0.0, -1.0, 0.0])); e1 = K.unit(np.cross(hum, cA)); e2 = K.unit(np.cross(cA, e1))
    xy = K.rect_xy(16.0, 10.0); car = K.unit(cA[:, None] + (xy[None, :, :1] * e1[:, None] + xy[None, :, 1:] * e2[:, None]) / 70.0)
    carr = K.Member("carriage", car, t=T_STRAP, off=K.STACK, width=10.0, joints=("J3",))
    # rail: humerus-fixed arc at cone gamma about the humerus axis (body_pose humerus frame), covering the twist range
    gm = p["gamma"] * D2R; half = 8.0 / (70.0 * math.sin(gm)) / D2R + 1.0       # + carriage half length (deg of azimuth)
    azs = np.arange(p["pmid"] + p["plo"] - half, p["pmid"] + p["phi"] + half + 1e-6, max(1.0, 2.0 / (70 * math.sin(gm)) / D2R))
    cs = np.arange(-4.0, 4.0 + 1e-6, 2.0) / 70.0
    Ur = []
    for azd in azs:
        aa = azd * D2R; u = np.array([math.sin(gm) * math.sin(aa), -math.cos(gm), math.sin(gm) * math.cos(aa)])
        v = np.array([math.cos(gm) * math.sin(aa), math.sin(gm), math.cos(gm) * math.cos(aa)])     # along the humerus axis
        Ur.append([K.unit(u + cc * v) for cc in cs])
    Ur = np.array(Ur).reshape(-1, 3); rail = K.Member("rail", F.H(Ur), t=T_STRAP, width=8.0, joints=("J3",),
                                                       grid=(len(azs), len(cs)), climb_deg=60.0, strap=True)
    mid = p["pmid"] * D2R; um = np.array([math.sin(gm) * math.sin(mid), -math.cos(gm), math.sin(gm) * math.cos(mid)])
    neck = K.neck_member(F, F.H(um), joints=("J3",))
    mem += [hubT, hubA, strapA, carr, rail, neck]
    q = np.stack([ald, bed, psi], -1)
    return K.Chain(members=mem, ok=ok, q=q, joints=dict(J2=zT, J3=cA), info=dict(n=int(p["n"]), stroke_deg=round(p["amax"] - p["amin"], 1),
                                                                                    rail_deg=round(p["phi"] - p["plo"], 1)))


# ---- profiles: the telescope's stacking and constant-radius tracks ----------------------------------------------------
def profiles(B, ch, fit, p, q, mode="march"):
    raw = K._levels(B, ch, fit, q, mode); prof = {}
    g, own, zones, D = layout(p); n = len(g) - 1
    names = ["plate"] + [f"lame{k}" for k in range(1, n)] + ["tip"]
    M = {m.name: m for m in ch.members}; lvl = None
    for k, nm in enumerate(names):          # every stage slides along its whole length over the stroke: one radius per
        m = M[nm]; ns, nc = m.grid; r = raw[nm].reshape(ns, nc)      # across-column (constant along the slide), each stage
        col = r.max(0)                                                # stacked on the one below (t + running gap)
        if lvl is not None: col = np.maximum(col, lvl + T_LAME + GAP)
        r = np.broadcast_to(col, (ns, nc)).copy(); lvl = float(col.max()); prof[nm] = r.ravel()
    lvT = prof["tip"].reshape(M["tip"].grid)
    for nm in ("hubT", "hubA", "strapA", "carriage", "rail", "neck"):
        r = raw[nm].copy(); m = M[nm]
        if m.kind == "cap": r[:] = r.max()
        if nm == "rail":                     # a circular track about the humerus axis: constant radius along its length
            ns, nc = m.grid; r = np.broadcast_to(r.reshape(ns, nc).max(0), (ns, nc)).ravel().copy(); prof[nm] = r; continue
        if m.climb_deg and m.grid:
            ns, nc = m.grid; R2 = r.reshape(ns, nc); x_ = np.arange(ns) * 2.0; sl = math.tan(m.climb_deg * D2R)
            r = ((R2[None] - sl * np.abs(x_[:, None, None] - x_[None, :, None])).max(1)).ravel()
        prof[nm] = r + m.off
    # the tip lame's end under the hub sits at the hub plate level; hub A on top; strap A starts at hub A's level
    prof["hubT"][:] = max(prof["hubT"].max(), lvT[-max(2, lvT.shape[0] // 8):].max())
    prof["hubA"][:] = max(prof["hubA"].max(), prof["hubT"].max() + K.STACK)
    sA = prof["strapA"].reshape(M["strapA"].grid); e = max(2, sA.shape[0] // 6); sA[:e] = np.maximum(sA[:e], prof["hubA"].max())
    prof["strapA"] = sA.ravel()
    prof["carriage"][:] = max(prof["carriage"].max(), prof["rail"].max() + T_STRAP + GAP)
    sA = prof["strapA"].reshape(M["strapA"].grid); sA[-e:] = np.maximum(sA[-e:], prof["carriage"].max()); prof["strapA"] = sA.ravel()
    for nm in prof: prof[nm] = np.minimum(prof[nm], RMAX + M[nm].off)  # no face floats beyond RMAX from GH (rev 3)
    return prof


def collisions(ch, pts, ok, clear=1.0, overlap=0.5):
    """K6 (tools/concept_kit.collisions) over every pair of members except the faces of one rigid part (SAME_PART);
    returns (P,) bool and keeps the per-pair shares in collisions.last"""
    hit = np.zeros(len(ok), bool); M = ch.members; collisions.last = {}
    for i in range(len(M)):
        for j in range(i + 1, len(M)):
            if frozenset((M[i].name, M[j].name)) in SAME_PART: continue
            sub = K.Chain(members=[M[i], M[j]], ok=ok, joints=ch.joints)
            h = K.collisions(sub, {M[i].name: pts[M[i].name], M[j].name: pts[M[j].name]}, ok, clear, overlap)
            if h[ok].any(): collisions.last[f"{M[i].name}/{M[j].name}"] = round(float(h[ok].mean()), 3)
            hit |= h
    return hit


def evaluate(B, p, q=None, cont=True, collide=True, jump_deg=25.0, keep=False):
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    p = design(B, F, p); q = p.get("q", 1.0) if q is None else q
    ch = build(B, F, p); ok = np.asarray(ch.ok, bool); flips = 0
    if cont: ok, flips = K.continuity_dense(B, F, build, p, ok, jump_deg)
    prof = profiles(B, ch, ok, p, q)
    pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}
    hit = collisions(ch, pts, ok) if collide else np.zeros(len(ok), bool)
    take = ok & ~hit; Pi = np.nonzero(take)[0]
    allp = np.concatenate([pts[m.name][Pi] for m in ch.members], 1)
    d = K.dist_many(B, np.repeat(Pi, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Pi), allp.shape[1])
    B.reset()
    for j, i in enumerate(Pi): B.res[i] = d[j]
    r = B.report(); o = 0; per = {}; clip = np.array([B.kind[i] == "clip" for i in Pi], bool); good = d.min(1) >= 0 if len(d) else np.zeros(0, bool)
    for m in ch.members:
        s = pts[m.name].shape[1]; dm = d[clip & good, o:o + s] if len(d) else np.zeros((0, s)); o += s
        per[m.name] = round(float(((dm >= 2) & (dm <= 14)).mean()), 3) if dm.size else 0.0
    r.update(inband_member=per, closure=round(float(np.mean(ch.ok)), 4), flips=int(flips), collide=round(float(np.mean(hit[ok])) if ok.any() else 0.0, 4),
             q=q, pairs=dict(getattr(collisions, 'last', {})), **ch.info)
    if keep: B._fp = dict(ch=ch, prof=prof, pts=pts, take=take, ok=ok, hit=hit, d=d, Pi=Pi, p=p)
    return r


BASE = dict(x_lat=40.0, x_lon=0.0, n=3, expo=1.0, side=1, zsign=0, ov=12.0, pitch=0.0, ls=20.0, hub_gap=10.0, hub_ext=10.0, w=10.0,
            gamma=55.0, lock=12.0, cov=0.95, rcov=0.95, q=1.0)


def log(msg): print(msg, flush=True)


def record(rows, p, r):
    e = dict(k=len(rows), t=K.now(), rev=REV, params=p, **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
             closure=r["closure"], flips=r["flips"], collide=r["collide"], inband_member=r["inband_member"])
    rows.append(e); tmp = SWEEP + ".tmp"; json.dump(rows, open(tmp, "w"), indent=1); os.replace(tmp, SWEEP); return e


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    B = K.bench(60, 160)
    if a[0] == "check":
        t = time.time(); r = evaluate(B, dict(BASE)); log(f"{time.time() - t:.1f} s {r}")
    elif a[0] == "redteam":                                                    # the jam, the pinch, overhead - on the best config
        rows = [e for e in json.load(open(SWEEP)) if e.get("rev") == REV]; best = min(rows, key=lambda e: e["gap"]); p = best["params"]
        r = evaluate(B, dict(p), keep=True); X = B._fp; ch, pts, ok, take, hit, d, Pi = X["ch"], X["pts"], X["ok"], X["take"], X["hit"], X["d"], X["Pi"]
        q = X["p"]; F = B._kitF; al, be = cardan(F, q); a0, x, z0 = axes(q); th = math.degrees(math.acos(float(np.clip(a0 @ x, -1, 1)))) - np.degrees(be)
        Rc = np.einsum("pij,pjk->pik", rot(x, al), rot(z0, -be)); psi, _ = twist_az(F, q, Rc); rel = (psi - q["pmid"] + 180) % 360 - 180
        el = np.array([pp["elev"] for pp in B.poses]); why = {}
        clos = build(B, F, q).ok
        for i in range(len(el)):
            if take[i]: w = "taken" if (d[list(Pi).index(i)].min() >= 0) else "contact"
            elif not clos[i]:
                w = ("gimbal lock" if (th[i] < q["lock"] or th[i] > 180 - q["lock"]) else "telescope stroke" if not (q["amin"] <= math.degrees(al[i]) <= q["amax"])
                     else "twist off the rail")
            elif not ok[i]: w = "branch flip / continuity"
            else: w = "part collision"
            why[i] = w
        from collections import Counter
        out = dict(params=p, report={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, inband_member=r["inband_member"],
                   collision_pairs=r["pairs"], reasons_all=dict(Counter(why.values())), reasons_overhead=dict(Counter(why[i] for i in range(len(el)) if el[i] >= 120)),
                   n_overhead=int((el >= 120).sum()), stroke_deg=r["stroke_deg"], rail_deg=r["rail_deg"])
        good = [j for j, i in enumerate(Pi) if d[j].min() >= 0]
        if good:
            dm = np.array([d[j].min() for j in good]); j = good[int(np.argmin(dm))]; i = int(Pi[j]); o = 0
            for m in ch.members:
                s_ = pts[m.name].shape[1]
                if o <= int(np.argmin(d[j])) < o + s_: out["pinch"] = dict(pose=i, member=m.name, d_mm=round(float(d[j].min()), 2), pose_deg=B.poses[i])
                o += s_
            far = np.concatenate([d[j] for j in good]); out["share_gt14"] = round(float((far > 14).mean()), 3)
        bad = [j for j, i in enumerate(Pi) if d[j].min() < 0]
        if bad:
            j = min(bad, key=lambda j: d[j].min()); i = int(Pi[j]); o = 0
            for m in ch.members:
                s_ = pts[m.name].shape[1]
                if o <= int(np.argmin(d[j])) < o + s_: out["deepest_contact"] = dict(pose=i, member=m.name, d_mm=round(float(d[j].min()), 2), pose_deg=B.poses[i])
                o += s_
        jams = [i for i in range(len(el)) if why[i] == "part collision"]
        if jams: i = max(jams, key=lambda i: el[i]); out["jam_example"] = dict(pose=i, pose_deg=B.poses[i])
        print(json.dumps(out, indent=1))
        json.dump(out, open(os.path.join(REPO, ".cache", f"{ID}_redteam.json"), "w"), indent=1)
    elif a[0] == "sweep":
        rows = json.load(open(SWEEP)) if os.path.exists(SWEEP) else []
        done = {json.dumps(e["params"], sort_keys=True) for e in rows if e.get("rev") == REV}
        cur = [e for e in rows if e.get("rev") == REV]; best = min(cur, key=lambda e: e["gap"]) if cur else None
        grid = json.loads(a[1]) if len(a) > 1 else []
        for over in grid:
            p = dict(BASE, **over); key = json.dumps(p, sort_keys=True)
            if key in done: continue
            t = time.time()
            try: r = evaluate(B, p)
            except Exception as ex: log(f"ERR {over} {ex}"); continue
            e = record(rows, p, r); done.add(key)
            log(f"[{e['k']}] {time.time() - t:.1f}s gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} ib10 {e['inband10']} "
                f"contact {e['contact']} flips {e['flips']} coll {e['collide']} {over} | {r['inband_member']} | {r['pairs']}")
            if best is None or e["gap"] < best["gap"]:
                best = e; K.log_event(f"{ID}: new best gap {e['gap']} (reach {e['reach']}, follow {e['follow']}, inband14 {e['inband14']}, contact {e['contact']}) at {over}")
