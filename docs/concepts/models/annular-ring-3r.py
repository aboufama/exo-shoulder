"""Concept model: ANNULAR-RING 3R (id annular-ring-3r), on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md).

The champion's spherical 3R (every joint axis through GH; the baseline's own axes, tools/concept_baseline.py CHAMP) with
each revolute realised as an OPEN-BORE thin-section ring bearing coaxial with its joint axis, so the skin under the
axis pierce point may rise into the bore instead of lifting a solid O20 hub. The links leave from the ring rims.

Chain (scapula handler -> user's upper-arm cuff), 3 ACTIVE DOF (the three ring angles), 0 PASSIVE:
    base --J1 ring about p1 (lower race = base, upper race = link 1)--> link 1 (strap on the great circle p1 -> p2)
    --J2 ring about p2 (lower = link 1, upper = link 2)--> link 2 (strap p2 -> p3)
    --J3 ring about p3 (upper = link 2, lower = the arm side)--> neck (14 x 6 strap, humerus-fixed, to BOTTOM's bar)
J2 = K1 two-circle closure on branch sigma (unique, continuous: K2 dense along the clips checks it).

Parts at real size (mm):
  * ring k (r_k > 0): a FLAT annulus normal to its axis, bore radius r_k (no metal inside), housed radial width w and
    axial height h (Reali-Slim KAA 4.76 section: w 9, h 8, lower race housing 0..4 = proximal member, upper 4..8 =
    distal member; KA 6.35 section: w 10.6, h 9.6, split 4.8). Underside sampled on a 2 mm grid + its inner and outer
    edge circles every 2 mm; its level is fitted like a K4 hub (every sample marched along the axis from its true
    in-plane offset, max over samples of the quantile q over the fit poses). The bore and outer WALLS are checked for
    contact on every taken pose (walls='contact', a wall point inside the body makes the pose a contact pose) or also
    scored for in-band (walls='score'); the top face sits 8 mm above a checked underside and cannot meet the skin
    without a wall doing so first.
  * r_k = 0 is the A/B TWIN at that joint: the kit's O20 v5 hub (K4), so the ring's own effect is measured.
  * links: K5 straps (width x t_link) on the great circle between the axes, cut at each ring's outer rim + a lug
    (`lug` mm, the strap's root tab, the only unsampled metal: lug x width per strap end); the strap root sits at the
    ring member's level (lower race: + 0, upper race: + split), as a true 3-D point (sqrt((h + dz)^2 + (r_o + lug)^2)
    from GH, with h the ring level of the previous pass: two passes per configuration, the second at the first's
    levels; the report says how far the nominal level was off).
  * neck: K7 14 x 6 strap from the J3 ring's rim (lower race level) to the start of BOTTOM's bar.
Honesty: K3 march, K2 dense continuity (joint values + axes), K6 collisions (+ `over`: link 2 over link 1 and the neck),
closure residual reported, held-out clips never loaded (kit check), ring joints declared hubless (they carry a ring,
not an O20 hub; the kit audit then does not ask for an O20 disc there).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/annular-ring-3r.py [check|sweep|redteam|sketch] [--fast]
"""
import itertools, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "annular-ring-3r"
NAME = "Annular-ring 3R: open-bore thin-section rings at every joint axis"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
SEC = {4.76: (9.0, 8.0, 4.0), 6.35: (10.6, 9.6, 4.8)}      # section -> housed radial width, axial height, race split
KAA = [12.7, 19.05, 25.4, 31.75]                             # Reali-Slim KAA10/15/20/25 bore radii (4.76 section)
# the baseline champion's axes (tools/concept_baseline.CHAMP; the spec's A2 81.45 is not the champion's 66.75)
CHAMP = dict(az=2.4305071427308924, el=80.67633718429899, a1=76.90180446920043, a2=66.74921235407174,
             wd=86.32769021001913, wa=21.829657347343378)
PARAMS = dict(CHAMP, sigma=-1, margin=10.0, width=12.0, t_link=3.0, q=0.95, r1=19.05, r2=19.05, r3=19.05, sec=4.76,
              lug=2.0, h1=100.0, h2=115.0, h3=68.0, walls="contact")


def toward(u, v, ang_deg):
    """unit vector at ang_deg from u toward v on their great circle (u, v (P, 3))"""
    u, v = K.unit(u), K.unit(v); e = K.unit(v - (u * v).sum(-1, keepdims=True) * u); a = ang_deg * K.D2R
    return math.cos(a) * u + math.sin(a) * e


def ring_xy(ri, ro, step=2.0):
    """underside samples of an annulus: 2 mm grid strictly inside + the two edge circles every 2 mm"""
    g = np.arange(-ro, ro + 1e-6, step); X, Y = np.meshgrid(g, g); R = np.hypot(X, Y)
    keep = (R > ri + 0.5) & (R < ro - 0.5); pts = [np.stack([X[keep], Y[keep]], -1)]
    for r in (ri, ro):
        n = max(8, int(math.ceil(2 * math.pi * r / step))); a = 2 * math.pi * (np.arange(n) + 0.5) / n
        pts.append(np.stack([r * np.cos(a), r * np.sin(a)], -1))
    return np.concatenate(pts)


def ring_member(name, axis, joint, ri, sec, h0=70.0):
    w, h, split = SEC[float(sec)]; ro = ri + w
    k = K.unit(axis); a, b = K.plane_frame(k); xy = ring_xy(ri, ro)
    D = K.unit(h0 * k[:, None] + xy[None, :, :1] * a[:, None] + xy[None, :, 1:] * b[:, None])
    area = math.pi * (ro ** 2 - ri ** 2)
    m = K.Member(name, D, kind="flat", t=h, width=2 * ro, joints=(joint,), K=k, A=a, Bv=b, xy=xy, cell=area / len(xy))
    m.ring = (ri, ro, h, split); return m


def joint_geo(p, j):
    """(member kind, outer radius, split dz of the upper member) of joint j (1..3)"""
    r = p[f"r{j}"]
    if r <= 0: return "hub", K.HUB_R, K.STACK
    w, h, split = SEC[float(p["sec"])]; return "ring", r + w, split


def root(p, j, upper):
    """(trim angle deg from the axis, ramp dz on the ring level) of a strap end at joint j: the strap starts at the
    rim + lug, at the member's race level, as a 3-D point (the ring level h_j of the previous pass)"""
    kind, ro, split = joint_geo(p, j); dz = split if upper else 0.0
    if kind == "hub": return 0.0, dz                           # the kit's hub convention (ramp over the first 12 mm)
    h = p[f"h{j}"] + dz; R = ro + p["lug"]
    return math.degrees(math.atan2(R, h)), math.hypot(h, R) - p[f"h{j}"]


def build(B, F, p):
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    axes = {1: p1, 2: p2, 3: p3}; members = []; hubless = []
    for j in (1, 2, 3):
        if p[f"r{j}"] > 0: members.append(ring_member(f"ring{j}", axes[j], f"J{j}", p[f"r{j}"], p["sec"])); hubless.append(f"J{j}")
        else: members.append(K.hub_member(f"hub{j}", axes[j], f"J{j}"))
    nm = {j: members[j - 1].name for j in (1, 2, 3)}
    w, t = p["width"], p["t_link"]

    def ramps_for(m, ends):
        """ends: [(start?, member name, dz, ramp mm)]: the first / last rows of the strap at >= that member's level + dz"""
        ns, nc = m.grid; srow = np.repeat(np.arange(ns), nc)
        for start, other, dz, mm in ends:
            n_end = int(math.ceil(mm / 2.0)) + 1; m.ramps.append((srow < n_end if start else srow >= ns - n_end, other, dz))
        return m

    def strap(name, ja, jb, ua, vb, up_a, up_b, **kw):
        ta, da = root(p, ja, up_a); tb, db = root(p, jb, up_b)
        u = toward(ua, vb, ta) if ta else ua; v = toward(vb, ua, tb) if tb else vb
        m = K.strap_member(name, u, v, (f"J{ja}", f"J{jb}"), **kw)
        return ramps_for(m, [(True, nm[ja], da, 2.0 if ta else K.HUB_R + 2.0), (False, nm[jb], db, 2.0 if tb else K.HUB_R + 2.0)])
    links = [strap("link1", 1, 2, p1, p2, True, False, width=w, t=t),
             strap("link2", 2, 3, p2, p3, True, True, width=w, t=t, over=[("link1", 1.0), ("neck", 1.0)])]
    bar = F.H(K.unit(K.BAR0_H)); tn, dn = root(p, 3, False)
    arc = np.degrees(np.arccos(np.clip((K.unit(p3) * K.unit(bar)).sum(-1), -1, 1)))
    u = toward(p3, bar, tn) if tn else p3
    # if the ring rim already reaches past the bar start, the neck is a 6 deg stub beyond the rim (it still exists)
    v = np.where((arc - tn < 6.0)[:, None], toward(p3, bar, tn + 6.0), bar)
    links.append(ramps_for(K.strap_member("neck", u, v, ("J3",), width=14.0, t=6.0), [(True, nm[3], dn, 2.0 if tn else K.HUB_R + 2.0)]))
    info = dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None,
                min_margin=round(float(margin[ok].min()), 2) if ok.any() else None)
    ch = K.Chain(members=members + links, ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3), info=info, hubless=tuple(hubless))
    ch.ring_r = {f"J{j}": joint_geo(p, j)[1] + p["lug"] for j in (1, 2, 3) if p[f"r{j}"] > 0}
    return ch


_K6 = K.collisions


def collisions(chain, pts, ok, **kw):
    """K6 with the kit's rule, except that partners sharing a RING joint are exempt within the ring's outer radius +
    lug + 2 mm of its axis (the kit's O20 rule is HUB_R + 2 = 12 mm: the analog for a ring, whose two races and the
    straps rooted on them all live in that zone; the upper member clears the lower by the race split by construction)"""
    hit = np.zeros(len(ok), bool); M = chain.members; R = getattr(chain, "ring_r", {})
    for a in range(len(M)):
        for b in range(a + 1, len(M)):
            sh = set(M[a].joints) & set(M[b].joints); rr = max([R.get(j, K.HUB_R) for j in sh], default=K.HUB_R)
            sub = K.Chain(members=[M[a], M[b]], ok=ok, joints=chain.joints)
            old = K.HUB_R
            try:
                K.HUB_R = rr; hit |= _K6(sub, {M[a].name: pts[M[a].name], M[b].name: pts[M[b].name]}, ok, **kw)
            finally:
                K.HUB_R = old
    return hit


K.collisions = collisions                                    # used by K.evaluate (same rule; ring partner zone above)


def walls(B, p, rep):
    """bore and outer walls of every ring on every taken pose: contact always; in-band too if p['walls'] == 'score'"""
    L = B._kit_last; take = L["take"]; Pi = np.nonzero(take)[0]; ch = L["chain"]; extra = {}
    if not len(Pi): return rep
    W = []
    for m in ch.members:
        if not hasattr(m, "ring"): continue
        ri, ro, h, _ = m.ring; lvl = float(L["prof"][m.name][0]); zs = np.arange(2.0, h + 1e-6, 2.0)
        for r in (ri, ro):
            n = max(8, int(math.ceil(2 * math.pi * r / 2.0))); a = 2 * math.pi * (np.arange(n) + 0.5) / n
            X = (lvl + zs)[None, :, None, None] * m.K[Pi][:, None, None, :] + r * (np.cos(a)[None, None, :, None] * m.A[Pi][:, None, None, :]
                                                                            + np.sin(a)[None, None, :, None] * m.Bv[Pi][:, None, None, :])
            W.append(X.reshape(len(Pi), -1, 3))
    if not W: return rep
    W = np.concatenate(W, 1); d = K.dist_many(B, np.repeat(Pi, W.shape[1]), W.reshape(-1, 3)).reshape(len(Pi), -1)
    nwc = 0
    for j, i in enumerate(Pi):
        nwc += int(d[j].min() < 0 <= B.res[i].min())
        if p.get("walls", "contact") == "score": B.res[i] = np.concatenate([B.res[i], d[j]])
        elif d[j].min() < 0: B.res[i] = np.concatenate([B.res[i], [d[j].min()]])
    r2 = B.report(); rep.update({x: r2[x] for x in ("reach", "follow", "inband14", "inband10", "contact", "gap")})
    rep["wall_contact_poses"] = nwc; rep["wall_min_mm"] = round(float(d.min()), 2); return rep


def levels(B):
    L = B._kit_last; return {m.name: round(float(L["prof"][m.name][0]), 1) for m in L["chain"].members if m.kind == "flat"}


def evaluate(B, p, passes=2, verbose=False):
    """two passes: the second uses the ring levels of the first for the strap roots (h1..h3)"""
    p = dict(p)
    for k in range(passes):
        rep = K.evaluate(B, build, p); lv = levels(B)
        new = {f"h{j}": lv.get(f"ring{j}", p[f"h{j}"]) for j in (1, 2, 3)}
        if k == passes - 1 or all(abs(new[x] - p[x]) < 1.0 for x in new): break
        p.update(new)
    rep = walls(B, p, rep); lv = levels(B)
    rep["levels"] = lv; rep["h_err"] = {f"h{j}": round(lv[f"ring{j}"] - p[f"h{j}"], 1) for j in (1, 2, 3) if f"ring{j}" in lv}
    rep["params_used"] = p
    if verbose: print({x: rep.get(x) for x in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit",
                                           "inband_member", "levels", "h_err", "mass_g", "flips", "collide", "wall_contact_poses", "wall_min_mm")}, flush=True)
    return rep


def run_configs(B, cfgs, resume=True, tag=""):
    rows = json.load(open(SWEEP_JSON)) if resume and os.path.exists(SWEEP_JSON) else []
    best = min((e for e in rows if e.get("honest")), key=lambda e: e["gap"], default=None)
    for c in cfgs:
        t0 = time.time(); r = evaluate(B, c)
        e = dict(k=len(rows), t=K.now(), params=r["params_used"], **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                 closure=r["closure"], mass_g=r["mass_g"], honest=r["honest"], kmode=r["kmode"], levels=r["levels"],
                 inband_member=r["inband_member"], wall_contact_poses=r.get("wall_contact_poses"), tag=tag)
        rows.append(e); json.dump(rows, open(SWEEP_JSON + ".tmp", "w"), indent=1); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)
        print(f"[{e['k']}] {tag} gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} ib10 {e['inband10']} "
              f"contact {e['contact']} honest {e['honest']} lv {e['levels']} mem {e['inband_member']} ({time.time() - t0:.0f}s)", flush=True)
        if e["honest"] and (best is None or e["gap"] < best["gap"]):
            best = e; K.log_event(f"Annular-ring 3R new best gap {e['gap']} (reach {e['reach']}, follow {e['follow']}, in-band14 {e['inband14']}, "
                                  f"contact {e['contact']}; rings r {c['r1']}/{c['r2']}/{c['r3']}, q {c['q']}; baseline 68.93)")
    return best, rows


if __name__ == "__main__":
    a = sys.argv[1:]; B = K.bench(20, 40) if "--small" in a else K.bench(60, 160)
    if "sweep" in a:
        H = dict(r1=0, r2=0, r3=0)
        stageA = [dict(PARAMS, **H)] + [dict(PARAMS, **dict(H, **{f"r{j}": r})) for j in (1, 2, 3) for r in KAA] + \
                 [dict(PARAMS, r1=r, r2=r, r3=r) for r in KAA]
        best, rows = run_configs(B, stageA if "A" in a else [], tag="A bore per joint")
    if "bores" in a:
        for r in [0, 12.7, 19.05, 25.4, 31.75]:
            evaluate(B, dict(PARAMS, r1=r, r2=r, r3=r), verbose=True)
    if "check" in a:
        for tw in (dict(), dict(r1=0, r2=0, r3=0)):
            t0 = time.time(); evaluate(B, dict(PARAMS, **tw), verbose=True); print(f"{time.time() - t0:.0f}s")
