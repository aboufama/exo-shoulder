"""Concept model: FLOATING-CENTRE 3R (id floating-centre-3r), rebuilt on the shared kit (tools/concept_kit.py).

The champion spherical 3R (every joint axis through the GH centre) whose J1 hub sits on a passive 3-axis FLOAT on the
scapula base plate, with a RIGID arm member on the user's cuff (no cuff slides).

Chain (scapula handler -> user's upper-arm cuff):
    base plate (contoured underside, flat slide face normal to J1's axis b) --[X slide]--[Y slide]--[normal slide
    along b]--> J1 lower member (O20 hub) --J1 R--> link 1 --J2 R--> link 2 --J3 R--> arm member (K7 neck), rigid on
    the cuff.
DOF: 3 ACTIVE (J1-J3) + 3 PASSIVE (the float). A spherical 3R rigid on the arm is mobile only if its centre c sits on
the arm's rotation centre; the float's 3 translations are the 3 equations c = GH, so the serial chain (3P + 3R = 6)
matches the cuff's 6 DOF relative to the handler one to one: no free coordinate (R17), the float is set by closure.

Parts at real size (kit conventions: K4 flat O20 hubs with the 12.25 stack, K5 12 x 3 straps with the 60 deg climb,
K7 14 x 6 neck to BOTTOM's bar, K3 march, K2 dense continuity, K6 collisions + `over`) plus the float:
  * PLATE: a disc about b of lateral radius plate_r = HUB_R + 4 + trav_t, laid out at its true height (2 mm grid in
    mm at h0), skin-contoured underside (K3, free member), flat slide face at plate_top = max_j(rho_j cos alpha_j) +
    t_low along b. Its K6 slab thickness is the whole float stack above its lowest underside point:
    t = plate_top + h_xy - min_j(rho_j cos alpha_j) (conservative where the underside is high).
  * XY stage (h_xy: two crossed miniature slides) and the NORMAL slide: J1's hub skin face sits >= plate_top + h_xy +
    n_down + 0.5 along b (it can descend n_down) -> hub1 ramp on the plate; link 1 (and link 2) pass over the plate
    + stage with n_down + 1 mm (`over`).
  The plate top needs the fitted plate profile, so evaluate() runs the kit fit twice: pass 1 measures the two plate
  constants (the radial-vs-axial correction and the slab thickness), pass 2 is the scored one; a post-check confirms
  hub1's F clears the true stage top + n_down + 0.5 in the scored fit.

SLIP EXTENSION (spec; the rig has no GH-vs-handler translation): judge/base_slip.py's error angles about the ISB
scapula axes and translation d, lever r = base_slip.lever()[0]; ISB -> bench scapula frame Zs = unit(0.5, 0, 0.87),
Ys = y, Xs = Ys x Zs; delta = (Rx(th0) Ry(th1) Rz(th2) - I) r + d t_hat (t_hat superior), + signs ('central') or the
worst of 8 sign patterns ('high'). Each sample is classed by the skin it rides (nearest posed skin vertex of its
point in BP.ARMV = arm skin, else scapula / trunk skin, which slips with the handler). mode 'parent' (rigid base +
cuff slides): chain samples over arm skin +delta; mode 'float': plate 0, chain samples over scapula / trunk skin
-delta, arm skin 0, pose not taken outside the float travel. The offsets are applied BEFORE the K3 fit (ray origins
shifted), so the undersides are fitted to the skin they really meet; K6 uses the chain-frame points (+delta on the
plate in float mode: the plate moves under the chain).

  VARIANT stage="beside" (the one that removes the measured limiter of the float under J1): the plate centred at
  (az_s, el_s) on flatter scapula skin, a 12 x 3 bracket (the top carriage arm, J1 lower member) from it to hub 1
  at the parent level, link 1 over the bracket and the stage; the stage axis JF is declared hubless (slides).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/floating-centre-3r.py [check|sweep|beside|slip|bs|redteam|sketch]
"""
import itertools, json, math, os, sys
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "judge"))
import concept_kit as K                                      # noqa: E402
import base_slip as BS                                       # noqa: E402

ID = "floating-centre-3r"
NAME = "Floating-centre 3R: the spherical chain on a closure-set 3-axis float under J1, rigid cuff"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
D2R = math.pi / 180

# parents: the top band / CAD 3R picks (kinematics only; sigma = branch)
PARENTS = {
    "r20_s1414_4": dict(az=2.4305071427308924, el=80.67633718429899, a1=76.90180446920043, a2=66.74921235407174, wd=86.32769021001913, wa=21.829657347343378, sigma=-1),
    "r18_s1392_1": dict(az=32.55159237005438, el=80.5631251310032, a1=77.40737955825345, a2=81.44799921589232, wd=71.38254048198503, wa=4.778729451604692, sigma=-1),
    "r20_s1414_0": dict(az=14.334325229499703, el=82.3438225055715, a1=73.14527820556887, a2=66.11369579887129, wd=85.02889058725152, wa=26.032150845040853, sigma=-1),
    "r20_s1411_2": dict(az=77.7131348211075, el=85.10998577949123, a1=76.60886566496094, a2=77.72756967198949, wd=69.22974128541614, wa=4.398159892313142, sigma=-1),
    "r17_s1381_0": dict(az=21.572004256164064, el=74.65677070921748, a1=76.6942876679089, a2=77.02221721376192, wd=72.53676340483199, wa=19.169823974377792, sigma=-1),
    "r18_s1394_1": dict(az=57.9420534734179, el=78.4471717690747, a1=69.3505972727849, a2=80.165684701384, wd=66.87006930589727, wa=4.083931436659226, sigma=-1),
}
PARAMS = dict(parent="r20_s1414_4", **PARENTS["r20_s1414_4"], margin=10.0, width=12.0, t_link=3.0, q=0.95,
              float=1, trav_t=12.0, n_down=4.0, h_xy=5.5, t_low=1.5, h0=56.0, slip="none", smode="float",
              plane="fit", stage="under", az_s=0.0, el_s=45.0, _dz=10.0, _tplate=7.0, _n=None, _rl1=70.0, _rl2=70.0)
SWEEP = dict(parent=list(PARENTS), q=[0.9, 0.95, 0.97, 1.0], trav_t=[8.0, 12.0, 15.0], n_down=[2.0, 4.0, 6.0], h_xy=[3.5, 5.5])


def strap(name, u, v, joints, width, t, ramp_to, over, r_lay=70.0, climb_deg=60.0, end_mm=K.HUB_R + 2.0):
    """K.strap_member with its 2 mm grid laid out at r_lay (the link's true radius) instead of 70 mm, so a link the
    float pushes out keeps ~1 sample / 4 mm2 (K.strap_member's layout at 70 mm thins to > 4 mm spacing above ~140 mm)"""
    import math
    D = K.strap_dirs(u, v, None, width=width, r_ref=r_lay); ns, nc = D.shape[1:3]
    n_end = int(math.ceil(end_mm / 2.0)) + 1; s_ = np.repeat(np.arange(ns), nc); ramps = []
    for (h, dz), m in zip(ramp_to, (s_ < n_end, s_ >= ns - n_end)):
        if h: ramps.append((m, h, dz))
    return K.Member(name, D.reshape(len(D), -1, 3), t=t, width=width, joints=tuple(joints), grid=(ns, nc), climb_deg=climb_deg,
                    ramps=ramps, strap=True, over=over, r_ref=r_lay, cell=4.0)


def with_parent(p, name): return dict(p, parent=name, **PARENTS[name])


def build(B, F, p):
    p1 = F.S(K.bvec(p["az"], p["el"]))                        # J1 fixed in the scapula (on the float: c = GH by closure)
    p3 = F.HG(K.wdir(p["wd"], p["wa"]))                       # J3 fixed in the humerus (rigid cuff)
    p2, ok, margin = K.closure(p1, p3, p["a1"], p["a2"], p["sigma"], margin_deg=p["margin"])
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2)], -1)
    hubs = [K.hub_member("hub1", p1, "J1"), K.hub_member("hub2", p2, "J2"), K.hub_member("hub3", p3, "J3")]
    w, t = p["width"], p["t_link"]
    l1_over, l2_over = [], [("link1", 1.0), ("neck", 1.0)]
    mem = []
    joints = dict(J1=p1, J2=p2, J3=p3); hubless = ()
    if p["float"]:
        plate_r = K.HUB_R + 4.0 + p["trav_t"]; h0 = p["h0"]
        pc = p1 if p["stage"] == "under" else F.S(K.bvec(p["az_s"], p["el_s"]))   # stage centre direction
        a, bb = K.plane_frame(pc); xy = K.disc_xy(plate_r, 2.0)
        D = K.unit(h0 * pc[:, None] + xy[None, :, :1] * a[:, None] + xy[None, :, 1:] * bb[:, None])
        tpl = max(p["_tplate"], p["t_low"] + p["h_xy"])          # K6 slab: plate + XY stage above its lowest point
        jf = "J1" if p["stage"] == "under" else "JF"
        mem.append(K.Member("plate", D, kind="free", t=tpl, width=2 * plate_r, joints=(jf,), r_ref=h0, cell=4.0))
        if p["stage"] == "under":
            # hub1 skin face >= stage top + normal travel + 0.5 under its whole disc (_dz from plate_consts: required F
            # minus the plate's radial max, since a ramp compares with the other member's max radius)
            hubs[0].ramps.append((np.ones(len(hubs[0].xy), bool), "plate", p["_dz"]))
        else:
            # the stage sits BESIDE J1 on flatter skin; a 12 x 3 bracket (the top carriage's arm, J1's lower member)
            # runs from the stage over its top (+ normal travel + 1) down to hub 1 at the parent's level
            joints["JF"] = pc; hubless = ("JF",)
            mem.append(strap("bracket", pc, p1, ("JF", "J1"), 12.0, 3.0, ((None, 0), ("hub1", 0.0)), [("plate", p["n_down"] + 1.0)], r_lay=h0))
        l1_over = [("plate", p["n_down"] + 1.0)] + ([("bracket", 1.0)] if p["stage"] != "under" else [])
        l2_over = l2_over + [("plate", p["n_down"] + 1.0)]
    links = [strap("link1", p1, p2, ("J1", "J2"), w, t, (("hub1", K.STACK), ("hub2", 0.0)), l1_over, r_lay=p["_rl1"]),
             strap("link2", p2, p3, ("J2", "J3"), w, t, (("hub2", K.STACK), ("hub3", K.STACK)), l2_over, r_lay=p["_rl2"]),
             K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))]
    return K.Chain(members=mem + hubs + links, ok=ok, q=q, joints=joints, hubless=hubless,
                   info=dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a1"], p["a2"])[ok].max()), 5) if ok.any() else None,
                             min_margin=round(float(margin[ok].min()), 2) if ok.any() else None))


def kin_ok(B, F, p):
    """closure + K2 dense continuity (the float changes no kinematics: cached per chain)"""
    key = tuple(round(float(p[k]), 6) for k in ("az", "el", "a1", "a2", "wd", "wa", "sigma", "margin"))
    C = B.__dict__.setdefault("_fc_ok", {})
    if key not in C:
        ch = build(B, F, dict(p, float=0)); C[key] = K.continuity_dense(B, F, build, dict(p, float=0), ch.ok)
    return C[key]


def plate_consts(B, F, p, fit, rho=None):
    """the float's flat slide face: plane normal n (scapula frame; 'fit' = least-squares plane of the contoured
    underside, 'b' = normal to J1's axis), its top along n, the hub-1 level that clears the XY stage + normal travel
    under the whole O20 disc, and the K6 slab thickness. rho = a fitted plate underside (else fitted here, K3 march)."""
    ch = build(B, F, p); m = ch.members[0]; Pi = np.nonzero(fit)[0]; i0 = int(Pi[0]); n_s = len(m.D[0])
    if rho is None:
        R = K.requirement(B, np.repeat(Pi, n_s), m.D[Pi].reshape(-1, 3)).reshape(len(Pi), n_s); rho = K.quantile(R, p["q"])
    RS = F.RS[i0]; Ds = m.D[i0] @ RS; Xs = Ds * rho[:, None]; bS = K.bvec(p["az"], p["el"])
    if p["stage"] != "under": bS = K.bvec(p["az_s"], p["el_s"])
    if p["plane"] == "fit":
        c = Xs.mean(0); n = np.linalg.svd(Xs - c)[2][-1]; n = n if n @ bS > 0 else -n
    else: n = bS
    h = Xs @ n; top = float(h.max()) + p["t_low"]
    if p["stage"] == "under":
        hb = [x for x in ch.members if x.name == "hub1"][0]; Os = (hb.xy[:, :1] * hb.A[i0] + hb.xy[:, 1:] * hb.Bv[i0]) @ RS
        F_req = float(((top + p["h_xy"] + p["n_down"] + 0.5 - Os @ n) / (bS @ n)).max())
    else: F_req = -1e9
    t_slab = float(((top + p["h_xy"]) / (Ds @ n) - rho).max())
    return dict(n=n, top=top, F_req=F_req, dz=F_req - float(rho.max()), t_slab=t_slab, tilt=float(np.degrees(np.arccos(np.clip(n @ bS, -1, 1)))))


def chain_only(B):
    """in-band over the clip frames taken WITHOUT the float plate's samples (the plate hugs the skin by construction, so
    its many samples lift the share metric while the chain itself moves away: report both)"""
    L = B._kit_last; names = [m.name for m in L["chain"].members]; take = np.nonzero(L["take"])[0]
    sizes = [L["pts"][n].shape[1] for n in names]; o = np.cumsum([0] + sizes)
    keep = np.concatenate([np.arange(o[k], o[k + 1]) for k, n in enumerate(names) if n != "plate"])
    D = [B.res[i][keep] for i in take if B.kind[i] == "clip" and B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    if not D: return dict(inband14_chain=0.0, inband10_chain=0.0)
    D = np.concatenate(D); return dict(inband14_chain=round(float(np.mean((D >= 2) & (D <= 14))), 4), inband10_chain=round(float(np.mean((D >= 2) & (D <= 10))), 4))


def evaluate(B, p, verbose=False):
    """the kit's evaluate (honest defaults); with the float on, the slide-face constants are measured first on the same
    fit poses (closure + K2), then checked again in the scored fit"""
    p = dict(p)
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    if p["float"]:
        ok, _ = kin_ok(B, F, p); c = plate_consts(B, F, p, ok)
        p["_dz"] = c["dz"]; p["_tplate"] = c["t_slab"]; p["_n"] = c["n"].tolist()
    r = K.evaluate(B, build, p, verbose=verbose)
    for _ in range(2):                                        # links pushed out (audit: > 4 mm spacing): re-lay at the true radius
        if not any("sparse" in a for a in r["audit"]): break
        L = B._kit_last; i0 = int(np.nonzero(L["take"] if L["take"].any() else L["ok"])[0][0])
        rl = {k: min(200.0, max(70.0, float(np.median(np.linalg.norm(L["pts"][k][i0], axis=-1))))) for k in ("link1", "link2")}
        # (capped at 200 mm: a link that far out is > 100 mm off the skin, never in band; the K6 arrays of a denser
        # layout exhaust memory - the audit still flags it, so such a configuration is reported as not honest)
        p["_rl1"], p["_rl2"] = round(rl["link1"], 0), round(rl["link2"], 0)
        if p["float"]:
            c = plate_consts(B, F, p, kin_ok(B, F, p)[0]); p["_dz"] = c["dz"]; p["_tplate"] = c["t_slab"]
        r = K.evaluate(B, build, p, verbose=verbose)
    r["layout_r"] = [p["_rl1"], p["_rl2"]]
    r.update(chain_only(B))
    if p["float"]:                                            # post-check in the scored fit
        L = B._kit_last
        c2 = plate_consts(B, F, p, L["ok"], rho=L["prof"]["plate"]); F1 = float(L["prof"]["hub1"].max())
        r.update(float_check_mm=round(F1 - c2["F_req"], 2) if p["stage"] == "under" else None, plate_top=round(c2["top"], 1), hub1_F=round(F1, 1),
                 plane_tilt_deg=round(c2["tilt"], 1), plate_slab=round(c2["t_slab"], 1))
    return r


# ---- slip extension -----------------------------------------------------------------------------------------------
ZS = K.unit(np.array([0.5, 0.0, 0.87])); YS = np.array([0.0, 1.0, 0.0]); XS = np.cross(YS, ZS)
ISB2S = np.c_[XS, YS, ZS]


def slip_delta(poses, law="central", t_hat=YS):
    """(n, 3) handler-vs-bone offset of the chain centre in the bench SCAPULA frame per pose (plane, elev)"""
    P = np.array([[q["plane"], q["elev"]] for q in poses]); r = ISB2S @ BS.lever()[0]
    th, d = BS.angles(P, law); th = th * D2R; out = np.zeros((len(P), 3))
    signs = [np.ones(3)] if law == "central" else [np.array(s) for s in np.array(np.meshgrid([-1, 1], [-1, 1], [-1, 1])).T.reshape(-1, 3)]
    for k in range(len(P)):
        best = None
        for s in signs:
            R = BS.rot(XS, s[0] * th[k, 0]) @ BS.rot(YS, s[1] * th[k, 1]) @ BS.rot(ZS, s[2] * th[k, 2])
            v = (R - np.eye(3)) @ r + d[k] * t_hat
            if best is None or np.linalg.norm(v) > np.linalg.norm(best): best = v
        out[k] = best
    return out


def _arm_class(B, ch, prof, Pi):
    """(P, m) bool per member: the sample's skin point (nearest posed vertex) is arm skin"""
    from scipy.spatial import cKDTree
    import body_pose as BP
    ARMV = np.asarray(BP.ARMV); cls = {m.name: np.zeros((len(m.D), len(m.xy) if m.kind == "flat" else m.D.shape[1]), bool) for m in ch.members}
    pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}
    for i in Pi:
        V = np.asarray(B.skin(int(i))[0]); near = np.linalg.norm(V, axis=1) < 320; tr = cKDTree(V[near]); av = ARMV[near]
        for m in ch.members:
            _, j = tr.query(pts[m.name][i]); cls[m.name][i] = av[j]
    return cls


def evaluate_slip(B, p, law, smode, verbose=False):
    """slip-extension report (see module doc): the same chain, per-sample offsets by the skin each rides, K3 refit
    with shifted ray origins, K2 dense (kinematics unchanged by slip), K6 in the chain frame (+delta on the plate)"""
    p = dict(p, slip=law, smode=smode, float=1 if smode == "float" else 0)
    F = getattr(B, "_kitF", None) or K.frames(B); B._kitF = F
    ok, flips = kin_ok(B, F, p); ok = ok.copy()
    if p["float"]:
        c = plate_consts(B, F, p, ok); p["_dz"] = c["dz"]; p["_tplate"] = c["t_slab"]; p["_n"] = c["n"].tolist()
    ch = build(B, F, p); prof0 = K.fit_profiles(B, ch, ok, p["q"], "march")
    Pi = np.nonzero(ok)[0]; cls = _arm_class(B, ch, prof0, Pi)
    eS = slip_delta(B.poses, law); e = np.einsum("pij,pj->pi", F.RS, eS)          # thorax frame
    off = {}
    for m in ch.members:
        if smode == "parent": off[m.name] = np.where(cls[m.name][..., None], e[:, None, :], 0.0)
        elif m.name == "plate": off[m.name] = np.zeros(cls[m.name].shape + (3,))
        else: off[m.name] = np.where(cls[m.name][..., None], 0.0, -e[:, None, :])
    if smode == "float":                                      # travel: the chain relative to the plate is -e
        b = F.S(np.asarray(p["_n"])); en = -(e * b).sum(-1); et = np.linalg.norm(-e - en[:, None] * b, axis=1)
        trav = (et <= p["trav_t"] + 1e-9) & (en >= -p["n_down"] - 1e-9) & (en <= p["n_down"] + 1e-9)
        ok = ok & trav
    # K3 fit with shifted origins (copy of K.fit_profiles' level pass, offsets added to the ray origins)
    Pf = np.nonzero(ok)[0]; raw = {}
    for m in ch.members:
        if m.kind == "flat":
            n = len(m.xy); Dm = np.broadcast_to(m.K[Pf][:, None, :], (len(Pf), n, 3))
            Om = m.xy[None, :, :1] * m.A[Pf][:, None, :] + m.xy[None, :, 1:] * m.Bv[Pf][:, None, :] + off[m.name][Pf]
        else:
            Dm = m.D[Pf]; Om = off[m.name][Pf]
        R = K.requirement(B, np.repeat(Pf, Dm.shape[1]), Dm.reshape(-1, 3), O=Om.reshape(-1, 3)).reshape(len(Pf), -1)
        raw[m.name] = K.quantile(R, p["q"])
    _levels0 = K._levels
    try:                                                      # reuse fit_profiles' ordering/ramps/over/climb on these levels
        K._levels = lambda B_, ch_, fit_, q_, mode_: raw
        prof = K.fit_profiles(B, ch, ok, p["q"], "march")
    finally:
        K._levels = _levels0
    pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}          # chain frame
    cpts = dict(pts)
    if smode == "float": cpts["plate"] = pts["plate"] + e[:, None, :]           # plate moves by +e under the chain
    hit = K.collisions(ch, cpts, ok)
    take = ok & ~hit; Pt = np.nonzero(take)[0]
    allp = np.concatenate([(pts[m.name] + off[m.name])[Pt] for m in ch.members], 1)
    d = K.dist_many(B, np.repeat(Pt, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Pt), allp.shape[1])
    B.reset()
    for j, i in enumerate(Pt): B.res[i] = d[j]
    r = B.report(); r.update(law=law, smode=smode, slip_max_mm=round(float(np.linalg.norm(eS, axis=1).max()), 1),
                             travel_out=int((~trav).sum()) if smode == "float" else 0, collide=int(hit.sum()), flips=int(flips),
                             arm_share={m.name: round(float(cls[m.name][Pi].mean()), 2) for m in ch.members})
    if verbose: print(r)
    return r


# ---- runs -----------------------------------------------------------------------------------------------------------
def entry_of(k, p, r, tag):
    return dict(k=k, t=K.now(), params={a: b for a, b in p.items() if not a.startswith("_")}, **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                closure=r.get("closure"), mass_g=r.get("mass_g"), honest=r.get("honest"), kmode=r.get("kmode", "march"),
                inband_member=r.get("inband_member"), float_check_mm=r.get("float_check_mm"), tag=tag,
                inband14_chain=r.get("inband14_chain"), inband10_chain=r.get("inband10_chain"), hub1_F=r.get("hub1_F"), layout_r=r.get("layout_r"))


class Runner:
    def __init__(self, B, resume=True):
        self.B = B; self.rows = json.load(open(SWEEP_JSON)) if resume and os.path.exists(SWEEP_JSON) else []
        self.best = min((e for e in self.rows if e["params"].get("float") and e["params"].get("slip", "none") == "none"),
                        key=lambda e: e["gap"], default=None)

    def run(self, p, tag="", slip=None):
        key = {a: b for a, b in p.items() if not a.startswith("_")}
        for e in self.rows:
            if e["params"] == key and e.get("tag", "").split(":")[0] == tag.split(":")[0]: return e
        r = evaluate_slip(self.B, p, *slip) if slip else evaluate(self.B, p)
        if slip: key = dict(key, slip=slip[0], smode=slip[1], float=1 if slip[1] == "float" else 0)
        e = entry_of(len(self.rows), key, r, tag); self.rows.append(e)
        json.dump(self.rows, open(SWEEP_JSON + ".tmp", "w"), indent=1); os.replace(SWEEP_JSON + ".tmp", SWEEP_JSON)
        print(f"[{e['k']}] {tag} gap {e['gap']} reach {e['reach']} follow {e['follow']} ib14 {e['inband14']} ib10 {e['inband10']} "
              f"contact {e['contact']} chk {e.get('float_check_mm')} per {e.get('inband_member')}", flush=True)
        if key.get("float") and not slip and (self.best is None or e["gap"] < self.best["gap"]):
            self.best = e
            K.log_event(f"{ID} new best gap {e['gap']} (reach {e['reach']}, follow {e['follow']}, in-band 14 {e['inband14']}, "
                        f"contact {e['contact']}; config k={e['k']}, parent {key['parent']}, q {key['q']}, float +-{key['trav_t']}/{key['n_down']} mm, XY {key['h_xy']})")
        return e


def sweep(B):
    R = Runner(B); base = with_parent(PARAMS, "r20_s1414_4")
    for q in (1.0, 0.95):                                     # A: the parent on these conventions (no float)
        R.run(dict(base, q=q, float=0), "A parent")
    for q in (1.0, 0.95):                                     # B: float travel x slide-face orientation
        for trav in (4.0, 8.0, 12.0, 20.0):
            for plane in ("b", "fit"):
                R.run(dict(base, q=q, trav_t=trav, plane=plane, n_down=4.0 if trav < 20 else 8.0), "B float")
    pb = min((e for e in R.rows if e["params"]["float"]), key=lambda e: e["gap"])["params"]
    for par in PARENTS:                                       # C: other parents at the best float setting
        if par != "r20_s1414_4":
            R.run(dict(PARAMS, **dict(pb, **PARENTS[par], parent=par)), "C parent pick")
            R.run(dict(PARAMS, **dict(pb, **PARENTS[par], parent=par, float=0)), "C parent pick (no float)")
    return R


def beside(B):
    """the variant that removes the measured limiter (J1 raised over a flat slide face on the sloped skin under it):
    the stage moves off J1 onto flatter scapula skin, a bracket carries J1 at the parent's level"""
    R = Runner(B); base = with_parent(PARAMS, "r20_s1414_4")
    for (az_s, el_s) in ((0.0, 35.0), (-45.0, 40.0), (45.0, 35.0)):
        R.run(dict(base, q=1.0, stage="beside", az_s=az_s, el_s=el_s, trav_t=8.0, n_down=4.0), "D beside")
    pb = min((e for e in R.rows if e["params"].get("stage") == "beside"), key=lambda e: e["gap"])["params"]
    R.run(dict(PARAMS, **dict(pb, trav_t=4.0)), "D beside travel")
    R.run(dict(PARAMS, **dict(pb, q=0.95)), "D beside q")
    return R


def slip_runs(B, R=None):
    R = R or Runner(B); b = R.best["params"]; p = dict(PARAMS, **b)
    for law in ("central", "high"):
        R.run(dict(p, float=0), f"S {law} parent+cuff slides", slip=(law, "parent"))
        R.run(p, f"S {law} float", slip=(law, "float"))
        for trav, nd in ((15.0, 6.0), (20.0, 8.0)):
            R.run(dict(p, trav_t=trav, n_down=nd), f"S {law} float wide", slip=(law, "float"))
    return R


def redteam(B, p):
    """named poses + the worst ones: per member min / median distance; the pose that jams; the point that pinches"""
    r = evaluate(B, p); L = B._kit_last; take = L["take"]; ok = L["ok"]; ch = L["chain"]; pts = L["pts"]
    poses = B.poses; el = np.array([q["elev"] for q in poses]); pl = np.array([q["plane"] for q in poses])
    out = dict(report={k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "inband_member", "float_check_mm", "plate_top", "hub1_F")})
    named = dict(rest=int(np.argmin(np.where(take, el, 1e9))), overhead=int(np.argmax(np.where(take, el, -1e9))),
                 across=int(np.argmax(np.where(take, pl, -1e9))), behind=int(np.argmin(np.where(take, pl, 1e9))))
    clip = np.array(B.clip, dtype=object) if hasattr(B, "clip") else None
    rows = {}
    for nm, i in named.items():
        s = {}
        for m in ch.members:
            dm = B.dist(i, pts[m.name][i]); s[m.name] = (round(float(dm.min()), 1), round(float(np.median(dm)), 1))
        rows[nm] = dict(pose={k: round(v) for k, v in poses[i].items()}, members=s)
    out["named"] = rows
    lost = np.nonzero(~take)[0]
    why = {}
    for i in lost:
        w = "fold/flip" if not ok[i] else ("collision" if L["hit"][i] else "contact")
        why.setdefault(w, []).append(i)
    out["lost"] = {w: dict(n=len(v), elev=[round(float(el[i])) for i in v[:8]], plane=[round(float(pl[i])) for i in v[:8]]) for w, v in why.items()}
    ci = [i for i in np.nonzero(take)[0] if B.res[i] is not None]
    worst = None
    for i in np.nonzero(take)[0]:
        for m in ch.members:
            dm = B.dist(int(i), pts[m.name][i]); j = int(np.argmin(dm))
            if worst is None or dm[j] < worst[0]: worst = (float(dm[j]), m.name, int(i))
    if worst: out["pinch"] = dict(min_mm=round(worst[0], 2), member=worst[1], pose={k: round(v) for k, v in poses[worst[2]].items()})
    return out


def sketch(B, p, path):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    r = evaluate(B, p); L = B._kit_last; take = np.nonzero(L["take"])[0]; el = np.array([B.poses[i]["elev"] for i in take])
    sel = (int(take[np.argmin(el)]), int(take[np.argmax(el)]))
    cols = dict(plate="#d1495b", hub1="#edae49", hub2="#e07a5f", hub3="#00798c", link1="#66a182", link2="#8d6a9f", neck="#30638e")
    fig = plt.figure(figsize=(12, 5.6))
    for k, i in enumerate(sel):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d"); V = np.asarray(B.skin(i)[0])
        near = V[np.linalg.norm(V, axis=1) < 150][::5]; ax.scatter(near[:, 2], near[:, 0], near[:, 1], s=0.3, c="#bbbbbb", alpha=0.3)
        for nm, X in L["pts"].items(): ax.scatter(X[i][:, 2], X[i][:, 0], X[i][:, 1], s=1.0, c=cols.get(nm, "k"), label=nm)
        q = B.poses[i]; ax.set_title(f"{'rest' if k == 0 else 'highest pose taken'}: plane {q['plane']:.0f}, elev {q['elev']:.0f}, axial {q['axial']:.0f}", fontsize=9)
        ax.view_init(elev=22, azim=-50 if k == 0 else -30); ax.set_xlabel("z lateral"); ax.set_ylabel("x anterior"); ax.set_zlabel("y up")
        ax.set_box_aspect((1, 1, 1)); ax.set_xlim(-80, 120); ax.set_ylim(-110, 90); ax.set_zlim(-90, 110)
        if k == 0: ax.legend(fontsize=7, markerscale=5, loc="upper left")
    fig.suptitle(f"{ID}: parent {p['parent']}, q {p['q']}, float +-{p['trav_t']:.0f}/{p['n_down']} mm, XY {p['h_xy']} mm; gap {r['gap']}, "
                 f"in band 14 {r['inband14']}, reach {r['reach']}, follow {r['follow']}", fontsize=9)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig); return r


def metal(pose, frames, params):
    """bench API: (k, 3) metal points of a bench pose for configuration params, or None if not taken (evaluates the
    configuration on the bench that holds the pose: undersides are fitted over all its poses, so a lone pose cannot be)"""
    B = metal.__dict__.setdefault("B", K.bench(60, 160)); key = json.dumps(params, sort_keys=True, default=str)
    if metal.__dict__.get("key") != key:
        evaluate(B, dict(PARAMS, **params)); L = B._kit_last; metal.L = L; metal.key = key
    L = metal.L; i = next(j for j, q in enumerate(B.poses) if q == pose)
    if not L["take"][i]: return None
    return np.concatenate([L["pts"][m.name][i] for m in L["chain"].members])


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "check"
    B = K.bench(60, 160); print("bench", B.mode, len(B.idx), flush=True)
    if mode == "check":
        for over in (dict(), dict(float=0)):
            print(over, json.dumps(evaluate(B, dict(PARAMS, **over)), default=str), flush=True)
    elif mode == "sweep": sweep(B)
    elif mode == "slip": slip_runs(B)
    elif mode == "beside": beside(B)
    elif mode == "bs": beside(B); slip_runs(B)
    elif mode == "redteam":
        p = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 else Runner(B).best["params"]))
        print(json.dumps(redteam(B, p), indent=1, default=str))
    elif mode == "sketch":
        p = dict(PARAMS, **(json.loads(a[1]) if len(a) > 1 else Runner(B).best["params"]))
        print(sketch(B, p, os.path.join(REPO, "docs", "concepts", "img", f"{ID}.png")))
