"""Concept model: POSTERIOR MAX-MARGIN CARDAN (id posterior-max-margin-cardan), docs/concepts/catalogue.json.

A spherical 3R (every axis through the GH centre) with both link arcs at 90 deg (a Cardan), placed so that the line
of the first axis stays far from the arm's last axis over the functional workspace (the largest singularity margin a
spherical 3R can have), with the whole chain behind the frontal plane:
  scapula base -> J1 (O20 hub, axis b fixed in the scapula, pole low on the infraspinatus) -> link 1 (90 deg strap up
  the back of the scapula) -> J2 (O20 hub, pole p2 = sigma (b x w)/|b x w| on the posterior-superior shoulder) ->
  link 2 (90 deg strap down the posterior deltoid) -> J3 (O20 hub, axis W fixed in the humerus, posterior upper arm)
  -> arm-end plate + 14 x 6 neck to BOTTOM's bar.
DOF: 3 ACTIVE (J1-J3), 0 PASSIVE; closed-form closure (K1 with a1 = a2 = 90), nothing left undetermined (R17).

Built on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md: K1 closure, K3 march, K4 hubs, K5 straps, K6
collisions, K2 dense continuity). Departures from the kit defaults, all toward honesty (docs/concepts/<id>.md):
  * every part is laid out at its REAL radius (two-pass: a first fit gives each strap's underside radius along its
    length and each hub's level; the second pass lays 2 mm samples in true mm there). The kit's straps are laid out
    at r_ref = 70 mm, which makes a 12 mm strap at 130 mm 22 mm wide.
  * hub seats: 'wedge' (the lower member's underside under the O20 disc is skin-fitted; the flat bearing face F sits
    on top of it; crown = F + 12.25, K6 counts the wedge height as stack) or 'flat' (kit K4 disc normal to the axis).
  * stacking: 'A' = link 1 lowest at J2, link 2 passes over link 1 and the neck (the template); 'B' = link 2 lowest
    everywhere (it is the long arc over the deltoid), link 1 and the neck pass over it.
  * variant a1, a2 < 90 (shorter arcs, smaller margin) to test whether arc length is the limiter.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/posterior-max-margin-cardan.py [check|landscape|sweep|redteam|plot]
"""
import itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402

ID = "posterior-max-margin-cardan"
NAME = "Posterior max-margin Cardan"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
PARAMS = dict(b_az=-28.0, b_el=-19.0, w_d=42.0, w_a=-64.0, a1=90.0, a2=90.0, sigma=1, margin=5.0,
              seat="wedge", stack="A", q=1.0, width=12.0, t_link=3.0)
SWEEP = dict(seat=["wedge", "flat"], stack=["A", "B"], q=[1.0, 0.95], sigma=[1, -1])
CAL_KEYS = ("rk_link1", "rk_link2", "rk_neck", "h_hub1", "h_hub2", "h_hub3", "wh_hub1", "wh_hub2", "wh_hub3")
NK = 13                                                      # radius knots along a strap (calibration)
# K6 bookkeeping: the kit scales a sample's extent and the shared-joint exemption by max(1, x / r_ref); with r_ref at
# the calibrated radius the exemption would shrink when a part is raised after its `over` pass and parts that `over`
# separated could collide again just outside the hub zone (measured: 80 link2/neck poses). r_ref = 0.8 x the layout
# radius keeps x / r_ref > 1 always (true-mm extent at the layout radius via hw = 0.8, mass via cell = 4 x 0.64).
RR = 0.8


def fit_profiles(B, chain, fit, q=1.0, mode="march"):
    """the kit's fit_profiles with the K5 climb limit applied BEFORE the `over` pass and the pair repeated until stable.
    The kit applies `over` then the climb: the climb lifts samples near a hub ramp that `over` left alone (they were at
    a lower radius, inside the shared-joint exemption) back into the member they must clear (measured: 67-80 link2 /
    neck poses rejected by K6 on this design). Raising only, so every part stays at or above the kit's level."""
    raw = K._levels(B, chain, fit, q, mode); prof = {}; level = {}

    def climb(m, r):
        if not (m.climb_deg and m.grid): return r
        ns, nc = m.grid; R2 = r.reshape(ns, nc); x = np.arange(ns) * m.step_mm; sl = math.tan(m.climb_deg * K.D2R)
        return (R2[None, :, :] - sl * np.abs(x[:, None, None] - x[None, :, None])).max(1).ravel()
    for m in sorted(chain.members, key=lambda m: (len(m.over) > 0, len(m.ramps) > 0)):
        r = raw[m.name].copy()
        if m.kind in ("cap", "flat"): r[:] = r.max()
        r = r + m.off
        for mask, other, dz in m.ramps: r[mask] = np.maximum(r[mask], level[other] + dz)
        r = climb(m, r)
        for _ in range(4 if m.over else 0):
            r2 = climb(m, K._over(chain, m, r, prof, fit))
            if np.allclose(r2, r): break
            r = r2
        prof[m.name] = r; level[m.name] = float(r.max())
    return prof


K.fit_profiles = fit_profiles          # evaluate() looks it up in the kit module


def perp(v):
    """a fixed unit vector perpendicular to v (local zero of a joint angle)"""
    v = K.unit(np.asarray(v, float)); r = np.array([0.0, 1.0, 0.0]) if abs(v[1]) < 0.9 else np.array([1.0, 0.0, 0.0])
    return K.unit(np.cross(v, r))


def strap(name, u, v, joints, rk, width=12.0, t=3.0, step=2.0, ramp_to=(), **kw):
    """a strap on the great circle u -> v (P, 3), samples every 2 mm in TRUE mm along and across at the radius profile
    rk (NK knots over the arc, from the calibration pass); K3 underside, K5 climb <= 60 deg, ramps at the ends"""
    u, v = K.unit(u), K.unit(v); ang = float(np.arccos(np.clip((u * v).sum(-1), -1, 1)).mean())
    rk = np.asarray(rk, float) * np.ones(NK); sk = np.linspace(0, 1, NK); sf = np.linspace(0, 1, 401)
    L = np.concatenate([[0], np.cumsum(np.diff(sf) * 0.5 * (np.interp(sf[1:], sk, rk) + np.interp(sf[:-1], sk, rk)))]) * ang
    ns = max(3, int(L[-1] / step) + 1); s = np.interp(np.linspace(0, L[-1], ns), L, sf); rr = np.interp(s, sk, rk)
    nrm = K.unit(np.cross(u, v)); e2 = K.unit(np.cross(nrm, u)); th = s[None, :] * ang
    Dd = np.cos(th)[..., None] * u[:, None] + np.sin(th)[..., None] * e2[:, None]
    off = np.arange(-width / 2, width / 2 + 1e-6, step); nc = len(off); cs = off[None, :] / rr[:, None]      # (ns, nc)
    D = K.unit(Dd[:, :, None, :] * np.cos(cs)[None, :, :, None] + nrm[:, None, None, :] * np.sin(cs)[None, :, :, None])
    Lr = np.interp(s, sf, L / max(L[-1], 1e-9)) * L[-1]; ramps = []
    for (h, dz), m in zip(ramp_to, (Lr <= K.HUB_R + 2.0, Lr >= L[-1] - K.HUB_R - 2.0)):
        if h: ramps.append((np.repeat(m, nc), h, dz))
    return K.Member(name, D.reshape(len(D), -1, 3), t=t, width=width, joints=tuple(joints), grid=(ns, nc), climb_deg=60.0,
                    step_mm=step, ramps=ramps, strap=True, r_ref=RR * np.repeat(rr, nc), hw=RR, cell=4.0 * RR ** 2, **kw)


def hub(name, axis, joint, p, seat):
    """O20 hub (docs/HARDWARE.md v5) laid out at its fitted level h: 'flat' = kit K4 disc normal to the axis at F;
    'wedge' = the lower member's skin-fitted underside under the disc (2 mm grid in true mm), F = its top, the K6
    thickness = wedge height + 12.25 (crown)"""
    h = float(p.get("h_" + name, 90.0))
    if seat == "flat": return K.hub_member(name, axis, joint, h0=h)
    k = K.unit(axis); a, b = K.plane_frame(k); xy = K.disc_xy(K.HUB_R, 2.0)
    D = K.unit(h * k[:, None] + xy[None, :, :1] * a[:, None] + xy[None, :, 1:] * b[:, None])
    return K.Member(name, D, kind="free", t=K.CROWN + float(p.get("wh_" + name, 0.0)), width=2 * K.HUB_R, joints=(joint,),
                    cell=4.0 * RR ** 2, r_ref=RR * h, hw=RR)


def build(B, F, p):
    b, W = K.bvec(p["b_az"], p["b_el"]), K.wdir(p["w_d"], p["w_a"])
    p1 = F.S(b); p3 = F.HG(W)                                                   # J1 in the scapula, J3 in the humerus
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])   # K1: Cardan pole
    q = np.stack([K.axis_angle(p1, F.S(perp(b)), p2), K.axis_angle(p2, p1, p3), K.axis_angle(p3, F.HG(perp(W)), p2)], -1)
    seat, w, t, A = p["seat"], p["width"], p["t_link"], p["stack"] == "A"
    hubs = [hub("hub1", p1, "J1", p, seat), hub("hub2", p2, "J2", p, seat), hub("hub3", p3, "J3", p, seat)]
    S = K.STACK
    if A:   # link 1 lowest at J2; link 2 over link 1 and the neck; neck = arm-end plate, lower member at J3
        l1 = strap("link1", p1, p2, ("J1", "J2"), p.get("rk_link1", 90.0), w, t, ramp_to=(("hub1", S), ("hub2", 0.0)))
        l2 = strap("link2", p2, p3, ("J2", "J3"), p.get("rk_link2", 90.0), w, t, ramp_to=(("hub2", S), ("hub3", S)),
                   over=[("link1", 1.0), ("neck", 1.0)])
        nk = strap("neck", p3, F.H(K.unit(K.BAR0_H)), ("J3",), p.get("rk_neck", 90.0), 14.0, 6.0, ramp_to=(("hub3", 0.0), (None, 0)))
    else:   # link 2 lowest everywhere; link 1 and the neck pass over it
        l1 = strap("link1", p1, p2, ("J1", "J2"), p.get("rk_link1", 90.0), w, t, ramp_to=(("hub1", S), ("hub2", S)),
                   over=[("link2", 1.0)])
        l2 = strap("link2", p2, p3, ("J2", "J3"), p.get("rk_link2", 90.0), w, t, ramp_to=(("hub2", 0.0), ("hub3", 0.0)))
        nk = strap("neck", p3, F.H(K.unit(K.BAR0_H)), ("J3",), p.get("rk_neck", 90.0), 14.0, 6.0, ramp_to=(("hub3", S), (None, 0)),
                   over=[("link2", 1.0)])
    res = K.closure_residual(p1, p3, p2, p["a1"], p["a2"])
    return K.Chain(members=hubs + [l1, l2, nk], ok=ok, q=q, joints=dict(J1=p1, J2=p2, J3=p3),
                   info=dict(residual_deg=round(float(res[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None))


def calibrate(B, p, passes=2):
    """two-pass layout: fit, read each strap's underside radius along its length (median over its lanes) and each hub's
    level + wedge height, re-lay the samples there (true mm). Returns params with the CAL_KEYS filled."""
    p = {k: v for k, v in p.items() if k not in CAL_KEYS}
    for _ in range(passes):
        K.evaluate(B, build, p, cont=False, collide=False); L = B._kit_last; ch, prof = L["chain"], L["prof"]
        for m in ch.members:
            r = np.minimum(prof[m.name], 250.0)                               # a part pushed past 250 mm is out of the game anyway
            if m.name.startswith("hub"):
                p["h_" + m.name] = round(float(r.max()), 2); p["wh_" + m.name] = round(float(r.max() - r.min()), 2) if m.kind == "free" else 0.0
            else:
                ns, nc = m.grid; rr = np.median(r.reshape(ns, nc), 1); p["rk_" + m.name] = [round(float(x), 1) for x in np.interp(np.linspace(0, ns - 1, NK), np.arange(ns), rr)]
    return p


def run(B, p):
    pc = calibrate(B, p); r = K.evaluate(B, build, pc); return pc, r


def margin_landscape(B, n=4000, cone=40.0, seed_b=(-28.0, -19.0), seed_w=(42.0, -64.0), top=40):
    """min over the bench poses of min(theta, 180 - theta), theta = angle(b, HG W) (RS cancels): Fibonacci grids of b
    (scapula) and W (humerus) within `cone` deg of the posterior seeds -> [(margin, b_az, b_el, w_d, w_a)] best first"""
    F = K.frames(B); HG = np.einsum("pji,pjk->pik", F.RS, F.RHG)
    i = np.arange(n) + 0.5; ph = np.arccos(1 - 2 * i / n); th = math.pi * (1 + 5 ** 0.5) * i
    G = np.stack([np.cos(th) * np.sin(ph), np.cos(ph), np.sin(th) * np.sin(ph)], 1)
    b0, w0 = K.bvec(*seed_b), K.wdir(*seed_w); Bs = G[G @ b0 > math.cos(math.radians(cone))]; Ws = G[G @ w0 > math.cos(math.radians(cone))]
    V = np.einsum("pij,wj->pwi", HG, Ws); c = np.abs(np.einsum("bi,pwi->bwp", Bs, V)).max(-1)
    mg = np.degrees(np.arccos(np.clip(c, -1, 1))); out = []
    for bi, wi in zip(*np.unravel_index(np.argsort(-mg, axis=None)[:top * 5], mg.shape)):
        b, w = Bs[bi], Ws[wi]
        out.append((round(float(mg[bi, wi]), 2), round(math.degrees(math.atan2(b[2], -b[0])), 1), round(math.degrees(math.asin(b[1])), 1),
                    round(math.degrees(math.acos(-w[1])), 1), round(math.degrees(math.atan2(w[0], w[2])), 1)))
    return out


def my_sweep(B, configs, out=SWEEP_JSON, resume=True, tag=""):
    rows = json.load(open(out)) if resume and os.path.exists(out) else []
    best = min(rows, key=lambda e: e["gap"]) if rows else None
    for p in configs:
        try:
            pc, r = run(B, p)
        except Exception as ex:                                          # a config the layout cannot place
            print("FAIL", p, ex); continue
        e = dict(k=len(rows), t=K.now(), params={k: v for k, v in p.items() if k not in CAL_KEYS},
                 **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")}, closure=r["closure"],
                 mass_g=r["mass_g"], flips=r["flips"], collide=r["collide"], min_margin=r.get("min_margin"),
                 inband_member=r["inband_member"], levels={k: pc[k] for k in ("h_hub1", "h_hub2", "h_hub3", "wh_hub1", "wh_hub2", "wh_hub3")})
        rows.append(e); json.dump(rows, open(out + ".tmp", "w"), indent=1); os.replace(out + ".tmp", out)
        if best is None or e["gap"] < best["gap"]:
            best = e; K.log_event(f"{ID}: new best gap {e['gap']} (reach {e['reach']}, follow {e['follow']}, inband14 {e['inband14']}, "
                                  f"inband10 {e['inband10']}, contact {e['contact']}) {tag} at {e['params']}")
        print(f"[{e['k']}] gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} ib10 {e['inband10']} "
              f"contact {e['contact']} cl {e['closure']} coll {e['collide']} mm {e['min_margin']} {e['inband_member']}", flush=True)
    return best, rows


if __name__ == "__main__":
    a = sys.argv[1:] or ["check"]
    B = K.bench(60, 160)
    if a[0] == "landscape":
        for x in margin_landscape(B)[:20]: print(x)
    elif a[0] == "sweep":
        stage = a[1] if len(a) > 1 else "1"
        if stage == "1":       # seat x stack x q at the catalogue seed (coarse)
            cfg = [dict(PARAMS, seat=se, stack=st, q=q) for se in ("wedge", "flat") for st in ("A", "B") for q in (1.0, 0.97, 0.93)]
        elif stage == "2":     # placements from the margin landscape (distinct poles) at the stage-1 best seat / stack
            base = json.loads(a[2]); top = margin_landscape(B, top=200); seen = []; cfg = []
            for mg, baz, bel, wd, wa in top:
                if any(abs(baz - x[0]) + abs(bel - x[1]) + abs(wd - x[2]) + abs(wa - x[3]) < 18 for x in seen): continue
                seen.append((baz, bel, wd, wa))
                if len(seen) > (int(a[3]) if len(a) > 3 else 8): break
                for q in (0.97, 0.93): cfg.append(dict(base, b_az=baz, b_el=bel, w_d=wd, w_a=wa, q=q))
        else:                  # explicit list of param overrides on a base
            base = json.loads(a[2]); cfg = [dict(base, **o) for o in json.loads(a[3])]
        my_sweep(B, cfg, tag=f"stage {stage}")
    elif a[0] == "check":
        p = dict(PARAMS)
        for kv in a[1:]:
            k, v = kv.split("="); p[k] = type(PARAMS[k])(v)
        pc, r = run(B, p); print({k: pc[k] for k in CAL_KEYS}); print(r)
