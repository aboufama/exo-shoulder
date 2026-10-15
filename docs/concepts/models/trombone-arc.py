"""trombone-arc: one curved Ti band on the arm-side member sliding through a swivelling guide on top of the scapula.
3 ACTIVE DOF (J1 swivel, J2 band position, J3 hub), 0 passive. Built on the shared kit (tools/concept_kit.py).

Topology (scapula handler -> user's upper-arm cuff), every axis through GH (a spherical 3R in disguise):
  S   scapula base = outer housing of the J1 ring
  J1  swivel about b (S-fixed): thin-section ring (KAA15XL0 class, 38.1 x 47.6 x 4.76) in housings = flat annulus
      19-26 mm from the b axis, 6 mm axial, at its fitted level z (member 'ring'; no O20 hub: declared hubless)
  L1  the guide: needle cam-follower box 30 (along the band) x 22 (across), lower rollers 3 mm under the band, two
      10 mm arms across the band to the ring's inner race (member 'guide': its skin-facing underside, flat, normal to b)
  J2  rotation about p2 (two-circle closure: angle A1 to b, A2 to W): the band is a circle about p2 at polar angle A1
      through b, so sliding it through the guide IS the rotation about p2. No metal at p2 (hubless).
  L2  the band (10 wide x 4 radial Ti, ONE radius R_a from GH over its whole length: it is a surface of revolution about
      p2 wherever it passes the guide; member 'band', kind 'cap') + a connector strap from the band's arm-side end to
      J3 (member 'conn', skin-fitted, the upper member of J3, passes over the neck)
  J3  O20 v5 hub about W (humerus-fixed), member 'hub3'; lower member = the K7 neck to BOTTOM's bar ('neck').
VARIANTS (measured, docs/concepts/trombone-arc.md): j1='hub' replaces the ring by an O20 hub on b with the guide offset
goff deg across the band (the ring's 52 mm footprint sits at 67-72 mm and forces the band 15 mm over it); tele=1 is the
spec's 2-stage telescoping arc (sleeve A through the guide, band B in A, A turns half of J2: 2:1 cable, no extra DOF).
Arc ends: the band spans [phi_lo, phi_hi] (azimuth about p2 in the L2 frame e2 = toward W, e3 = p2 x e2) - CONSTANT
params (it is one rigid part), set by arc_range() from the guide azimuths the poses need; a pose is taken only if the
whole guide (+- its half length) stays on the band.
Level rules (the kit fits each member's underside on the K3 march, quantile q over the fit poses): guide >= ring + 6.5
(its arms sit on the inner race, 0.5 mm K6 radial clearance), band >= guide + 3.5 (lower rollers 3 mm + 0.5),
band >= ring + dz_ring (the band crosses the annulus; 15 mm clears its outer edge for ring levels >= 35 mm in the kit's
radial test), connector start >= band, connector end >= hub3 + STACK, neck start >= hub3.
"""
import itertools, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                                    # noqa: E402

ID = "trombone-arc"
NAME = "Trombone arc: one curved slide through a swivel guide on top of the scapula"
D2R = math.pi / 180
SWEEP_OUT = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
# baseline champion axes (tools/concept_baseline.py = the bench's 68.93)
# best honest configuration of the sweep (k 143, gap 88.29): 2-stage telescoping arc, O20 hub at J1, guide offset 22 deg,
# band laid out at its fitted radius (Rn 106; it fits at 110.6).
# The champion axes (az 2.43, el 80.68, A1 76.9, A2 66.75) with a single-stage band: the tail runs into the neck/head.
PARAMS = dict(az=45.0, el=30.0, A1=90.0, A2=90.0, wd=86.33, wa=21.83, sigma=-1, margin=5.0,
              phi_lo=20.0, phi_hi=140.0, src="p5-95", Rn=106.0, width=10.0, band_t=4.0, qb=1.0, dR=0.0,
              guide_L=30.0, guide_W=22.0, ring_ri=19.0, ring_ro=26.0, ring_t=6.0, dz_ring=15.0,
              conn_w=12.0, conn_t=3.0, q=0.95, j1="hub", goff=22.0, tele=1)
# variants: j1 'ring' (KAA15XL0 ring about b, guide in its bore, goff 0) or 'hub' (O20 hub on b, guide offset goff deg
# across the band on an L1 strap 'arm1'); tele 0 = single-stage band, 1 = 2-stage telescoping arc (sleeve + band)


def axes(F, p):
    b = F.S(K.bvec(p["az"], p["el"])); W = F.HG(K.wdir(p["wd"], p["wa"]))
    p2, ok, margin = K.closure(b, W, p["A1"], p["A2"], p["sigma"], margin_deg=p["margin"])
    e2 = K.unit(W - (W * p2).sum(-1, keepdims=True) * p2); e3 = np.cross(p2, e2)
    phi_g = np.degrees(np.arctan2((b * e3).sum(-1), (b * e2).sum(-1)))
    return b, W, p2, e2, e3, phi_g, ok, margin


def half_len(p):
    """guide half length along the band, deg of azimuth about p2 (taken at Rn: conservative when R_a >= Rn)"""
    return math.degrees(p["guide_L"] / 2 / (p["Rn"] * math.sin(p["A1"] * D2R)))


def arc_range(F, p):
    """band ends from the guide azimuths the poses need: 'clip' = all closing fit-clip frames, 'wsNN' = clip frames
    + workspace poses between the (100-NN)/2 and (100+NN)/2 percentiles"""
    *_, phi_g, ok, _ = axes(F, p); hl = half_len(p) + 1.0
    c = phi_g[ok & F.clip]
    if not len(c): return None
    lo, hi = c.min(), c.max()
    if p["src"].startswith("p"):                     # 'pLO-HI': percentiles of the guide azimuth over clip + ws poses
        a_, b_ = (float(x) for x in p["src"][1:].split("-")); w = phi_g[ok]
        lo, hi = np.percentile(w, a_), np.percentile(w, b_)
    elif p["src"].startswith("ws"):
        w = phi_g[ok & F.ws]; s = float(p["src"][2:])
        if len(w): lo = min(lo, np.percentile(w, 50 - s / 2)); hi = max(hi, np.percentile(w, 50 + s / 2))
    return round(float(lo - hl), 2), round(float(hi + hl), 2)


def band_dirs(p2, e2, e3, p):
    A1 = p["A1"] * D2R; Rs = p["Rn"] * math.sin(A1)
    n = max(3, int(round((p["phi_hi"] - p["phi_lo"]) * D2R * Rs / 2.0)) + 1)
    ph = np.linspace(p["phi_lo"], p["phi_hi"], n) * D2R
    de = np.arange(-p["width"] / 2, p["width"] / 2 + 1e-6, 2.0) / p["Rn"]
    pol = A1 + de                                                            # polar angles about p2 across the band
    rad = np.cos(ph)[:, None, None] * e2[:, None, None, :] + np.sin(ph)[:, None, None] * e3[:, None, None, :]   # (P, ns, 1, 3)
    D = np.cos(pol)[None, None, :, None] * p2[:, None, None, :] + np.sin(pol)[None, None, :, None] * rad
    return D.reshape(len(p2), -1, 3), (n, len(de))


def arc_dirs(p2, e2, e3, Ab, ph, width, Rn):
    """band directions on the circle about p2 at polar angle Ab (rad), azimuths ph (P, n) deg, width mm at Rn"""
    ph = np.asarray(ph) * D2R; de = np.arange(-width / 2, width / 2 + 1e-6, 2.0) / Rn; pol = Ab + de
    rad = np.cos(ph)[..., None, None] * e2[:, None, None, :] + np.sin(ph)[..., None, None] * e3[:, None, None, :]
    D = np.cos(pol)[None, None, :, None] * p2[:, None, None, :] + np.sin(pol)[None, None, :, None] * rad
    return D.reshape(len(p2), -1, 3)


def build(B, F, p):
    b, W, p2, e2, e3, phi_g, ok, margin = axes(F, p)
    hl = half_len(p)
    ok = ok & (phi_g >= p["phi_lo"] + hl) & (phi_g <= p["phi_hi"] - hl)     # whole guide on the band (J2 range)
    A1 = p["A1"] * D2R; Ab = (p["A1"] + p.get("goff", 0.0)) * D2R          # band polar angle about p2 (goff: guide offset)
    u = K.unit(b - (b * p2).sum(-1, keepdims=True) * p2)                     # from p2 toward b, normal to p2
    g = math.cos(Ab) * p2 + math.sin(Ab) * u                                  # guide centre direction (fixed in L1)
    c_lo = math.cos(Ab) * p2 + math.sin(Ab) * (math.cos(p["phi_lo"] * D2R) * e2 + math.sin(p["phi_lo"] * D2R) * e3)
    m = K.unit(p2 - (p2 * g).sum(-1, keepdims=True) * g); t = np.cross(g, m)  # guide frame: across (toward p2), along
    members = []; joints = dict(J1=b, J2=p2, J3=W, Jc=c_lo); hubless = ["J2", "Jc"]; ramps_band = []
    if p["j1"] == "ring":       # J1 = thin-section ring about b, guide inside its bore (goff must be 0)
        ra, rb = K.plane_frame(b); xy = K.disc_xy(p["ring_ro"], 2.0); xy_r = xy[np.linalg.norm(xy, axis=1) >= p["ring_ri"] - 1e-9]
        D0 = K.unit(70 * b[:, None] + xy_r[None, :, :1] * ra[:, None] + xy_r[None, :, 1:] * rb[:, None])
        members.append(K.Member("ring", D0, kind="flat", t=p["ring_t"], width=2 * p["ring_ro"], joints=("J1",), K=b, A=ra,
                                Bv=rb, xy=xy_r, cell=4.0))
        # guide: 30 x 22 box underside + two 10 mm arms across to the inner race (|m| <= 15: 4 mm short of the ring's
        # inner edge so the kit's lateral K6 test does not read the bolted joint as a collision)
        gx = K.rect_xy(p["guide_L"], p["guide_W"]); arms = K.rect_xy(10.0, 30.0); arms = arms[np.abs(arms[:, 1]) > p["guide_W"] / 2 + 1e-6]
        xy_g = np.concatenate([gx, arms]); gram = [(np.ones(len(xy_g), bool), "ring", p["ring_t"] + 0.5)]
        gj = ("J1", "J2"); hubless.append("J1"); ramps_band.append(("ring", p["dz_ring"]))
    else:                       # J1 = O20 hub on b; guide offset goff deg across the band, carried by an L1 strap
        members.append(K.hub_member("hub1", b, "J1"))
        xy_g = K.rect_xy(p["guide_L"], p["guide_W"]); gram = []; gj = ("J2", "Ja"); joints["Ja"] = g; hubless.append("Ja")
    Dg = K.unit(70 * g[:, None] + xy_g[None, :, :1] * t[:, None] + xy_g[None, :, 1:] * m[:, None])
    members.append(K.Member("guide", Dg, kind="flat", t=3.0, width=p["guide_W"], joints=gj, K=g, A=t, Bv=m, xy=xy_g,
                            cell=4.0, ramps=gram))
    if p["j1"] != "ring":
        members.append(K.strap_member("arm1", b, g, ("J1", "Ja"), width=12.0, t=3.0, ramp_to=(("hub1", K.STACK), ("guide", 0.0))))
    Rs = p["Rn"] * math.sin(Ab)
    if not p.get("tele"):
        # band L2: one radius (cap), fitted, raised over the guide (lower rollers) and the ring
        pb = dict(p, A1=math.degrees(Ab))
        Db, grid = band_dirs(p2, e2, e3, pb); nb = Db.shape[1]; allb = np.ones(nb, bool)
        members.append(K.Member("band", Db, kind="cap", t=p["band_t"], width=p["width"], joints=("J2", "Jc"), r_ref=p["Rn"],
                                cell=4.0, q=p["qb"], off=p["dR"],
                                ramps=[(allb, "guide", 3.6)] + [(allb, o, dz) for o, dz in ramps_band]))
        phM = phi_g
    else:
        # 2-stage telescoping arc: sleeve A (middle body, C-channel, 2 mm walls + 0.5 gaps around B, width + 5) slides
        # through the guide; band B (L2) slides in A. A turns half of J2 about p2 (2:1 cable over pulleys at A's ends,
        # inside A's section), so its tail past the guide is half the single-stage one. Lower wall of A = member
        # 'sleeve' [R_A, R_A + 2]; B at exactly R_A + 2.5 (off -1000 + ramp); A >= guide + 3.5.
        g0, g1 = p["phi_lo"] + hl + 1.0, p["phi_hi"] - hl - 1.0
        ok = ok & (phi_g >= g0) & (phi_g <= g1)
        phM = (phi_g + g1) / 2
        nA = max(3, int(round(((g1 - g0) / 2 + 2 * hl + 2) * D2R * Rs / 2.0)) + 1)
        sA = np.linspace(-(g1 - g0) / 2 - hl - 1, hl + 1, nA)
        DA = arc_dirs(p2, e2, e3, Ab, phM[:, None] + sA[None, :], p["width"] + 5.0, p["Rn"]); nA_ = DA.shape[1]
        members.append(K.Member("sleeve", DA, kind="cap", t=2.0, width=p["width"] + 5, joints=("J2",), r_ref=p["Rn"],
                                cell=4.0, q=p["qb"], off=p["dR"],
                                ramps=[(np.ones(nA_, bool), "guide", 3.6)] + [(np.ones(nA_, bool), o, dz) for o, dz in ramps_band]))
        hiB = (g0 + g1) / 2 + hl - 1.0
        nB = max(3, int(round((hiB - p["phi_lo"]) * D2R * Rs / 2.0)) + 1)
        DB_ = arc_dirs(p2, e2, e3, Ab, np.broadcast_to(np.linspace(p["phi_lo"], hiB, nB), (len(p2), nB)), p["width"], p["Rn"])
        members.append(K.Member("band", DB_, kind="cap", t=p["band_t"], width=p["width"], joints=("J2", "Jc"), r_ref=p["Rn"],
                                cell=4.0, off=-1000.0, ramps=[(np.ones(DB_.shape[1], bool), "sleeve", 2.6)]))
    members.append(K.hub_member("hub3", W, "J3"))
    members.append(K.neck_member(F, W, joints=("J3",), ramps=(("hub3", 0.0), (None, 0))))
    members.append(K.strap_member("conn", c_lo, W, ("J3", "Jc"), width=p["conn_w"], t=p["conn_t"],
                                  ramp_to=(("band", 0.0), ("hub3", K.STACK)), over=[("neck", 1.0)]))
    q = np.stack([K.axis_angle(b, F.S([1.0, 0, 0]), p2), phi_g, K.axis_angle(W, F.HG([0.0, -1, 0]), p2), phM], -1)
    res = K.closure_residual(b, W, p2, p["A1"], p["A2"])
    return K.Chain(members=members, ok=ok, q=q, joints=joints, hubless=tuple(hubless),
                   info=dict(residual_deg=round(float(res[ok].max()), 6) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None))


def with_arc(F, p):
    p = dict(p); r = arc_range(F, p)
    if r is None: return None
    p["phi_lo"], p["phi_hi"] = r; return p


def details(B, p, rep=None):
    """R_a, levels, tail length per pose, worst poses (after an evaluate)"""
    L = B._kit_last; ch, prof, take = L["chain"], L["prof"], L["take"]
    F = B._kitF; b, W, p2, e2, e3, phi_g, ok, _ = axes(F, p)
    Ra = float(prof["band"][0]); A1 = p["A1"] * D2R
    A1 = (p["A1"] + p.get("goff", 0.0)) * D2R
    tail = (p["phi_hi"] - phi_g) * D2R * Ra * math.sin(A1) - p["guide_L"] / 2
    if p.get("tele"): tail = ((p["phi_hi"] - half_len(p) - 1 - phi_g) / 2 + half_len(p) + 1) * D2R * Ra * math.sin(A1) - p["guide_L"] / 2
    j1 = "ring" if "ring" in prof else "hub1"
    return dict(R_a=round(Ra, 2), j1=round(float(prof[j1][0]), 2), guide=round(float(prof["guide"][0]), 2),
                hub3=round(float(prof["hub3"][0]), 2), arc_deg=round(p["phi_hi"] - p["phi_lo"], 1),
                arc_mm=round((p["phi_hi"] - p["phi_lo"]) * D2R * Ra * math.sin(A1), 1),
                tail_mm=[round(float(tail[take].min()), 1), round(float(tail[take].max()), 1)] if take.any() else None)


def run(B, configs, resume=True):
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    cf = [c for c in (with_arc(F, c) for c in configs) if c is not None]
    return K.sweep(B, build, cf, SWEEP_OUT, resume=resume)


if __name__ == "__main__":
    a = sys.argv[1:]
    B = K.bench(60, 160); F = K.frames(B); B._kitF = F
    p = with_arc(F, PARAMS); t0 = time.time()
    r = K.evaluate(B, build, p); print(time.time() - t0, "s")
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "flips", "collide", "inband_member", "honest", "audit", "sample_mm")})
    print(details(B, p))
