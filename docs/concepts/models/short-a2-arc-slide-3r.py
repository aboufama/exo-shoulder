"""short-a2-arc-slide-3r: a spherical 3R with a SHORT link 2 whose J3 hub rides a spring-returned, GH-concentric arc
slide in link 2 (a one-sided a2 relay); J2 has hard stops at the fold margin, and the slide opens only while J2 sits
on a stop.

Chain: scapula handler -> J1 (O20 hub, ACTIVE R through GH, scapula-fixed u1) -> link 1 (12 x 3 Ti strap, arc a1) ->
J2 (O20 hub, ACTIVE R through GH, two hard-stop dowels at the dihedrals mu_lo / mu_hi) -> link 2a = Ti rail plate
(root bolted to hub 2, skin-contoured; its last part a constant-radius arc slot concentric with GH: ONE level, a cap)
-> PASSIVE R about n = unit(p2 x p3) through GH (the arc slot + a carriage on two M4 shoulder screws in iglidur flanged
bushings, a constant-force spring strip pulling it onto its home stop at a2 = a2h, travel to a2max, Hall-sensed) ->
carriage (2 mm plate, or 0 = hub 3's lower member machined as the sliding sole) -> J3 (O20 hub on the carriage, ACTIVE
R through GH, humerus-fixed u3) -> member 3 = hub 3's upper member + the K7 14 x 6 neck rigid to BOTTOM -> cuff.
Passive translations 0 (the slot is a rotation about GH), passive rotations 1 (the slide, sensed, spring-returned).

Relay = force closure (every coordinate determined, R17). th = angle(p1, p3). The stops are PHYSICAL dihedrals of J2:
mu_hi = the J2 dihedral at th = a1 + a2h - m_stop, mu_lo at th = |a1 - a2h| + m_stop (a2 = a2h).
  mode A  lo <= th <= hi : a2 = a2h (the spring preload holds the carriage on its home stop; J2 inside its stops)
  mode B  th > hi        : J2 on its high stop (dihedral mu_hi); a2 = the SMALLEST root >= a2h of
                           cos th = cos a1 cos a2 + sin a1 sin a2 cos mu_hi  (the spring's energy minimum)
  mode C  th < lo        : the same with mu_lo (folded side; small gain when a2h < a1, kept for honesty)
  not taken: no root within [a2h, a2max], or the sub-chain margin < K.FOLD_MARGIN.
This is NOT the window estimate a1 + a2max - m (the judge's kinematic check): with the stop on a fixed dihedral the
reachable th at full travel is th(mu_hi, a2max); the model measures it (info 'th_top').

Members (kit): hub1 / hub2 / hub3 (O20 flat discs), link 1 (upper member at J1 and J2 in layout 0), rail_r (root of
link 2a: free skin-fitted underside, lower member under hub 2 in layout 0, its end ramped to the travel level), rail_t
(the slot zone: kind 'cap' = ONE GH radius, spans [a2h - e, a2max + e] in link 2a, e = max(carriage / 2, 7.1) + 2 mm
of end wall; flush underside: the keeper plate runs in an underside groove), carriage (flat 2 mm plate on top of the
rail, on p3), hub3 (F3 = rail level + rail 3 + 0.15 running gap + carriage), neck (K7, the UPPER member at J3: ramp
STACK; over the rail and carriage by 1 mm). Layout 1 swaps J2's members (rail upper over link 1, as the template's
link 2). The rail and carriage are laid out with their REAL width at r_lay (the kit lays straps out at 70 mm; a strap
below 70 mm would otherwise be narrower than the part), and the slot angles use r_lay <= the fitted rail radius
(conservative: a longer rail).

Continuity: K2 dense on every joint value, every axis and the slide (q includes a2); plus a flood fill over the raw
1432-pose workspace grid (15-deg steps, 8 sub-frames per edge): a workspace pose taken with the slide open counts only
if a continuous motion reaches it from the home (mode A) region without the slide stepping > 5 deg per sub-step or the
chain failing to close (isolated relay islands are not reachable, the stop-relay lesson).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/short-a2-arc-slide-3r.py [check|redteam] ['<json params>']
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) -> (params, report) (tools/concept_cma.py)
    big:   CB_EXACT=1 python3 docs/concepts/models/short-a2-arc-slide-3r.py frozen '<json params>' --out R.json [--redteam]
"""
import functools, importlib.util, json, math, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("spm_for_a2slide", os.path.join(HERE, "spine-parked-j2-3r.py"))
SPM = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SPM)

ID = "short-a2-arc-slide-3r"
NAME = ("Short-link-2 3R whose J3 hub rides a spring-returned GH-concentric arc slide in link 2 "
        "(one-sided a2 relay, J2 on hard stops)")
# seed S1 of the round-5 judge (catalogue model_spec): u1 = bvec(107.18, 64.67), u3 = wdir(103.39, -5.90)
PARAMS = dict(az=107.18, el=64.67, wd=103.39, wa=-5.90, a1=44.138, a2h=40.730, a2max=54.591, sigma=-1,
              m_stop=K.FOLD_MARGIN, q=0.97, width=12.0, t_link=3.0,
              rail_w=14.0, rail_th=3.0, carr_t=2.0, carr_len=16.0, rail_end=2.0, r_lay=56.0, layout=0, lift1=1.0, l1_end=2.0, side=0, a2min=None, c_extra=0.0,
              connect=1, near=0)
ELEV_OVER = SPM.ELEV_OVER
GAP = 0.15                                                   # running gap carriage / rail
QS = 4.0                                                     # a2 enters K2 x4: a > 6.25-deg slide step per 2-deg sub-step is a jump


def _cosd(x): return np.cos(np.radians(x))
def _sind(x): return np.sin(np.radians(x))


def dihedral(a1, a2, th):
    """J2 dihedral (deg) at which angle(p1, p3) = th for arcs a1, a2"""
    c = (_cosd(th) - _cosd(a1) * _cosd(a2)) / (_sind(a1) * _sind(a2))
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def stop_root(th, a1, mu, lo_a2, hi_a2):
    """all roots a2 in [lo_a2, hi_a2] of cos th = cos a1 cos a2 + sin a1 sin a2 cos mu -> (6, n) array, inf where none"""
    A = math.cos(math.radians(a1)); Bc = math.sin(math.radians(a1)) * math.cos(math.radians(mu))
    R = math.hypot(A, Bc); phi = math.degrees(math.atan2(Bc, A)); C = _cosd(th) / R
    ok = np.abs(C) <= 1.0; d = np.degrees(np.arccos(np.clip(C, -1, 1)))
    X = np.stack([phi + d, phi - d, phi + d + 360.0, phi - d + 360.0, phi + d - 360.0, phi - d - 360.0])
    return np.where(ok[None] & (X >= lo_a2 - 1e-7) & (X <= hi_a2 + 1e-7), np.clip(X, lo_a2, hi_a2), np.inf)


def th_of(a1, a2, mu):
    return np.degrees(np.arccos(np.clip(_cosd(a1) * _cosd(a2) + _sind(a1) * _sind(a2) * _cosd(mu), -1, 1)))


def closure_var(b, w, a1, a2, sigma):
    """K.closure with a per-pose a2 (P,): -> p (P,3), h2 > 0 (P,), margin (P,) deg"""
    b, w = K.unit(b), K.unit(w); c = np.clip((b * w).sum(-1), -1, 1); n = K.unit(np.cross(b, w))
    A1, A2 = math.radians(a1), np.radians(a2); den = 1 - c ** 2 + 1e-12
    Aq = (math.cos(A1) - c * np.cos(A2)) / den; Bq = (np.cos(A2) - c * math.cos(A1)) / den
    p0 = Aq[..., None] * b + Bq[..., None] * w; h2 = 1 - (p0 * p0).sum(-1)
    p = p0 + sigma * np.sqrt(np.clip(h2, 0, None))[..., None] * n
    th = np.degrees(np.arccos(c)); margin = np.minimum.reduce([th - np.abs(a1 - a2), a1 + a2 - th, 360 - a1 - a2 - th])
    return p, h2 > 0, margin


def kin(p1, p3, p):
    """relay + closure for axes p1, p3 (P,3) -> dict(p2, a2, mode (0 A / 1 B / 2 C / -1 none), ok, margin, th).
    The spring's energy minimum: the feasible a2 (J2 dihedral within [mu_lo, mu_hi]) nearest a2h in [a2min, a2max];
    when a2h is infeasible it lies on a stop (a root of th(mu_stop, a2) = th). One-sided (a2min = a2h): the spec."""
    a1, a2h, a2max, m = p["a1"], p["a2h"], p["a2max"], p["m_stop"]; a2min = min(a2h, float(p.get("a2min", a2h)))
    th = np.degrees(np.arccos(np.clip((K.unit(p1) * K.unit(p3)).sum(-1), -1, 1)))
    lo, hi = abs(a1 - a2h) + m, a1 + a2h - m
    mu_lo, mu_hi = dihedral(a1, a2h, lo), dihedral(a1, a2h, hi)
    a2 = np.full(len(th), float(a2h)); mode = np.where((th >= lo) & (th <= hi), 0, -1)
    sel = mode < 0
    if sel.any():
        t = th[sel]; Xh = stop_root(t, a1, mu_hi, a2min, a2max); Xl = stop_root(t, a1, mu_lo, a2min, a2max)
        X = np.concatenate([Xh, Xl]); code = np.r_[np.ones(len(Xh)), 2 * np.ones(len(Xl))]
        fin = np.isfinite(X); Xs = np.where(fin, X, a2h)
        feas = fin & (th_of(a1, Xs, mu_lo) <= t[None] + 1e-6) & (th_of(a1, Xs, mu_hi) >= t[None] - 1e-6)
        dist = np.where(feas, np.abs(Xs - a2h), np.inf); j = dist.argmin(0); g = np.isfinite(dist.min(0))
        ii = np.nonzero(sel)[0]; a2[ii[g]] = Xs[j[g], np.nonzero(g)[0]]; mode[ii[g]] = code[j[g]].astype(int)
    p2, h2ok, margin = closure_var(p1, p3, a1, a2, p["sigma"])
    ok = (mode >= 0) & h2ok & (margin >= K.FOLD_MARGIN - 1e-3)
    return dict(p2=p2, a2=a2, mode=mode, ok=ok, margin=margin, th=th, mu=(mu_lo, mu_hi), lo=lo, hi=hi, a2min=a2min)


def _rot_arc(p2, e, s_deg):
    """direction at arc s (deg) along the great circle from p2 toward e (both (P,3))"""
    s = np.radians(np.asarray(s_deg, float))
    if s.ndim: s = s[:, None]
    return K.unit(np.cos(s) * p2 + np.sin(s) * e)


def build(B, F, p):
    """side 0 (the spec): the slot under hub 3 (hub 3 on the carriage). side 1: the slot at the ROOT of link 2 (hub-2
    end of link 2a), the carriage carries link 2b to hub 3, which sits at its own level (removes the hub-3-on-rail
    stack, the measured limiter of side 0); travel bilateral [a2min, a2max] around the spring's home a2h."""
    p1 = F.S(K.bvec(p["az"], p["el"])); p3 = F.HG(K.wdir(p["wd"], p["wa"]))
    k = kin(p1, p3, p); p2, a2, ok = k["p2"], k["a2"], k["ok"]; a2min = k["a2min"]
    n = K.unit(np.cross(p2, p3))                                   # slide axis, fixed in link 2a, through GH
    e = K.unit(np.cross(n, p2))                                    # rail direction at hub 2 (toward p3)
    R = float(p["r_lay"]); deg = lambda mm: math.degrees(mm / R)
    ext = max(p["carr_len"] / 2.0, 7.1) + p["rail_end"]           # carriage / screw + bushing, plus the end wall
    side = int(p.get("side", 0)); infeasible = False
    if side:                                                       # carriage home c_h (deg from p2, in link 2a)
        s0 = deg(K.HUB_R + 2.0 + float(p["c_extra"])); c_h = s0 + deg(ext) + (p["a2h"] - a2min)
        s1 = c_h + (p["a2max"] - p["a2h"]) + deg(ext)
        infeasible = s1 + deg(K.HUB_R + 1.0) > a2min           # the rail tail would run under hub 3
        cdir = _rot_arc(p2, e, c_h + (a2 - p["a2h"]))            # carriage centre (moves with the slide)
    else:
        s0, s1 = p["a2h"] - deg(ext), p["a2max"] + deg(ext); cdir = p3
    tc = K.unit(np.cross(n, cdir))                                 # slot tangent at the carriage
    wl = lambda w: w * 70.0 / R                                    # real width at r_lay in the kit's 70-mm layout
    q = np.stack([K.axis_angle(p1, F.S([1.0, 0, 0]), p2), K.axis_angle(p2, p1, p3),
                  K.axis_angle(p3, F.HG([0.0, -1, 0]), p2), QS * a2], -1)
    hub1 = K.hub_member("hub1", p1, "J1"); hub2 = K.hub_member("hub2", p2, "J2"); hub3 = K.hub_member("hub3", p3, "J3")
    rt = K.strap_member("rail_t", _rot_arc(p2, e, s0), _rot_arc(p2, e, s1), ("S",), ang=math.radians(s1 - s0),
                        width=wl(p["rail_w"]), t=p["rail_th"], climb_deg=None)
    rt.kind = "cap"; rt.joints = ("S", "Sc", "Rj")              # Rj: the root / slot junction of the ONE rail plate
    lay = 1 if side else int(p.get("layout", 0)); w, t = p["width"], p["t_link"]; end = K.HUB_R + 2.0
    rr = K.strap_member("rail_r", p2, p3, ("J2", "S", "Rj"), ang=math.radians(s0), width=wl(p["rail_w"]), t=p["rail_th"],
                        ramp_to=(("hub2", K.STACK if lay else 0.0), ("rail_t", 0.0)), end_mm=end)
    # link 1's J2 end zone is lift1 mm above hub 2's upper flange (a spacer: only raises metal) and l1_end mm long, so
    # the upper member clears the rail root by >= 1 mm just past K6's 12-mm exempt zone (the kit's `over` measures that
    # zone at the pre-climb radius, K6 at the final one: without this, 17 % of poses jam link 1 on the rail root)
    l1 = K.strap_member("link1", p1, p2, ("J1", "J2"), width=w, t=t,
                        ramp_to=(("hub1", K.STACK), ("hub2", (0.0 if lay else K.STACK) + float(p["lift1"]))),
                        end_mm=end + float(p["l1_end"]))
    if lay: rr.over = [("link1", 1.0)]
    else: l1.over = [("rail_r", 1.0), ("rail_t", 1.0)]
    ct = float(p["carr_t"]); mem = [hub1, hub2, rt, rr, l1]; carr = None
    if ct > 0:
        xy = K.rect_xy(p["carr_len"], 12.0)
        D = K.unit(70.0 * cdir[:, None] + xy[None, :, :1] * tc[:, None] + xy[None, :, 1:] * n[:, None])
        carr = K.Member("carriage", D, kind="flat", t=ct, width=12.0, joints=("Sc", "J3") if not side else ("Sc",), K=cdir, A=tc,
                        Bv=n, xy=xy, cell=4.0, ramps=[(np.ones(len(xy), bool), "rail_t", p["rail_th"] + GAP)])
        mem.append(carr)
    if not side:                                                   # hub 3 on the carriage, neck = J3's upper member
        hub3.joints = ("J3", "Sc")
        hub3.ramps = [(np.ones(len(hub3.xy), bool), "rail_t", p["rail_th"] + GAP + ct)]
        neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", K.STACK), (None, 0)))
        neck.over = [("rail_t", 1.0), ("rail_r", 1.0)] + ([("carriage", 1.0)] if carr else [])
        mem += [hub3, neck]
    else:                                                          # link 2b: carriage -> hub 3 (upper member at J3)
        neck = K.neck_member(F, p3, joints=("J3",), ramps=(("hub3", 0.0), (None, 0)))
        l2b = K.strap_member("link2b", cdir, p3, ("Sc", "J3"), width=w, t=t,
                             ramp_to=(("carriage", ct) if carr else ("rail_t", p["rail_th"] + GAP), ("hub3", K.STACK)),
                             end_mm=end, over=[("rail_t", 1.0), ("link1", 1.0), ("neck", 1.0)])
        mem += [hub3, neck, l2b]
    okk = ok & np.isfinite(q).all(-1) & (not infeasible)
    mv = okk & (k["mode"] > 0)
    info = dict(residual_deg=round(float(K.closure_residual(p1, p3, p2, p["a1"], a2)[okk].max()), 5) if okk.any() else None,
                min_margin=round(float(k["margin"][okk].min()), 2) if okk.any() else None,
                modes=dict(A=int(((k["mode"] == 0) & okk).sum()), B=int(((k["mode"] == 1) & okk).sum()),
                           C=int(((k["mode"] == 2) & okk).sum()), none=int((~okk).sum())),
                slide_deg_max=round(float(np.abs(a2[mv] - p["a2h"]).max()), 2) if mv.any() else 0.0,
                stops_mu=[round(k["mu"][0], 2), round(k["mu"][1], 2)], window=[round(k["lo"], 2), round(k["hi"], 2)],
                th_top=round(float(th_of(p["a1"], p["a2max"], k["mu"][1])), 2), th_bottom=round(float(th_of(p["a1"], a2min, k["mu"][0])), 2),
                rail_span_deg=[round(s0, 2), round(s1, 2)], infeasible=bool(infeasible))
    return K.Chain(members=mem, ok=okk, q=q, joints=dict(J1=p1, J2=p2, J3=p3, S=n, Sc=cdir, Rj=_rot_arc(p2, e, s0)),
                   info=info, hubless=("S", "Rj") if not side else ("S", "Rj", "Sc"))


# ---- continuity over the raw 1432-pose workspace grid (kinematics only) --------------------------------------------
_GRID = {}


def _grid(nsub=8):
    if nsub in _GRID: return _GRID[nsub]
    from scipy.spatial.transform import Rotation as Rot, Slerp
    Z = CB._poses_all(); names = list(Z["NAMES"]); WI = np.nonzero(Z["CID"] == names.index("Workspace (envelope)"))[0]
    PW = Z["POSE"][WI][:, :3].round().astype(int); RS = Z["RS"][WI].astype(float); RH = RS @ Z["HG"][WI].astype(float)
    key = {tuple(x): i for i, x in enumerate(PW)}; nb = []
    for i, x in enumerate(PW):
        for ax in range(3):
            y = x.copy(); y[ax] += 15; j = key.get(tuple(y))
            if j is not None: nb.append((i, j))
    nb = np.array(nb); s = np.linspace(0, 1, nsub); E = len(nb)
    RSp = np.empty((E, nsub, 3, 3)); RHp = np.empty((E, nsub, 3, 3))
    for a, (i, j) in enumerate(nb):
        RSp[a] = Slerp([0, 1], Rot.from_matrix(np.stack([RS[i], RS[j]])))(s).as_matrix()
        RHp[a] = Slerp([0, 1], Rot.from_matrix(np.stack([RH[i], RH[j]])))(s).as_matrix()
    _GRID[nsub] = dict(WI=WI, PW=PW, RS=RS, RH=RH, nb=nb, RSp=RSp.reshape(-1, 3, 3), RHp=RHp.reshape(-1, 3, 3), nsub=nsub)
    return _GRID[nsub]


def flood(p, jump=5.0, axjump=25.0):
    """-> (conn: {global pose index: bool} for the ws grid, stats). Seeds = closing mode-A grid poses."""
    G = _grid(); u1 = K.bvec(p["az"], p["el"]); u3 = K.wdir(p["wd"], p["wa"])
    f = lambda RS, RH: kin(np.einsum("pij,j->pi", RS, u1), np.einsum("pij,j->pi", RH, u3), p)
    k = f(G["RS"], G["RH"]); ok = k["ok"]; home = ok & (k["mode"] == 0)
    ke = f(G["RSp"], G["RHp"]); n = G["nsub"]; E = len(G["nb"])
    ok2 = ke["ok"].reshape(E, n); a2 = ke["a2"].reshape(E, n); p2 = K.unit(ke["p2"]).reshape(E, n, 3)
    da = np.abs(np.diff(a2, axis=1)).max(1); dax = np.degrees(np.arccos(np.clip((p2[:, 1:] * p2[:, :-1]).sum(-1), -1, 1))).max(1)
    good = ok2.all(1) & (da <= jump) & (dax <= axjump)
    I, J = G["nb"][:, 0], G["nb"][:, 1]; adj = [[] for _ in range(len(ok))]
    for a in np.nonzero(good)[0]: adj[I[a]].append(J[a]); adj[J[a]].append(I[a])
    reach = home.copy(); st = list(np.nonzero(home)[0])
    while st:
        u = st.pop()
        for v in adj[u]:
            if not reach[v] and ok[v]: reach[v] = True; st.append(v)
    both = ok[I] & ok[J]; rel = both & ~(home[I] & home[J]); jam = both & ~good
    el = G["PW"][:, 1]
    stats = dict(grid=int(len(ok)), static=round(float(ok.mean()), 4), connected=round(float(reach.mean()), 4),
                 home=round(float(home.mean()), 4), relay_edges=int(rel.sum()), relay_jams=int((jam & rel).sum()), jams=int(jam.sum()),
                 overhead_static=round(float(ok[el >= 140].mean()), 4), overhead_connected=round(float(reach[el >= 140].mean()), 4),
                 islands=int((ok & ~reach).sum()))
    return {int(g): bool(r) for g, r in zip(G["WI"], reach)}, stats


def extras(B, r, p):
    """crown / wall check of every hub, near-touch, overhead >= 140, slide statistics of taken poses"""
    L = B._kit_last; ch, prof, take = L["chain"], L["prof"], L["take"]
    Pi = np.array([j for j in np.nonzero(take)[0] if B.res[j] is not None], int)
    hubs = [m for m in ch.members if m.kind == "flat" and m.name.startswith("hub")]
    cmin = np.full(len(B.res), np.inf); cwho = {}
    if len(Pi):
        parts = [SPM.crown_points(m, prof[m.name], m.width / 2.0)[Pi] for m in hubs]
        C = np.concatenate(parts, 1)
        dc = K.dist_many(B, np.repeat(Pi, C.shape[1]), C.reshape(-1, 3)).reshape(len(Pi), C.shape[1])
        cmin[Pi] = dc.min(1); cut = np.cumsum([0] + [x.shape[1] for x in parts])
        for a, j in enumerate(Pi): cwho[int(j)] = hubs[int(np.searchsorted(cut, int(np.argmin(dc[a])), side="right") - 1)].name
    bad = np.nonzero(cmin < 0)[0]
    for j in bad: B.res[j] = np.append(B.res[j], cmin[j])
    rr = B.report(); tk = SPM._taken
    allmin = sorted((min(float(np.min(B.res[j])), cmin[j]), j) for j in range(len(B.res)) if tk(B, j))
    save = list(B.res)
    for d, j in allmin:
        if d < 1.0: B.res[j] = np.append(B.res[j], -1e-3)
    rn = B.report(); B.res = save
    el = np.array([q["elev"] for q in B.poses]); ws = np.array([k == "ws" for k in B.kind]); cl = ~ws
    ov = np.nonzero(el >= ELEV_OVER)[0]; ovw = ov[ws[ov]]; ovc = ov[cl[ov]]
    to = [j for j in ov if tk(B, j)]; d = np.concatenate([B.res[j] for j in to]) if to else np.zeros(0)
    over = dict(n_ws=int(len(ovw)), reach=round(float(np.mean([tk(B, j) for j in ovw])), 4) if len(ovw) else None,
                n_clip=int(len(ovc)), follow=round(float(np.mean([tk(B, j) for j in ovc])), 4) if len(ovc) else None,
                n_taken=len(to), inband14=round(float(((d >= 2) & (d <= 14)).mean()), 4) if len(d) else None,
                inband10=round(float(((d >= 2) & (d <= 10)).mean()), 4) if len(d) else None)
    a2 = np.asarray(ch.q)[:, 3] / QS; tkn = np.array([tk(B, j) for j in range(len(B.res))]); mv = tkn & (np.abs(a2 - p["a2h"]) > 1e-6)
    for k in ("reach", "follow", "inband14", "inband10", "contact", "gap"): r[k] = rr[k]
    r.update(crown_contact_poses=int(len(bad)), crown_min=round(float(np.min(cmin[np.isfinite(cmin)])), 2) if np.isfinite(cmin).any() else None,
             min_metal_skin=round(float(allmin[0][0]), 2) if allmin else None,
             near_low=[dict(mm=round(float(dd), 2), i=int(j), kind=B.kind[j], plane=B.poses[j]["plane"], elev=B.poses[j]["elev"],
                            axial=B.poses[j]["axial"], crown=cwho.get(int(j)) if cmin[j] <= float(np.min(B.res[j])) else "face")
                       for dd, j in allmin[:5]],
             gap_near1=rn["gap"], near1=dict(reach=rn["reach"], follow=rn["follow"], inband14=rn["inband14"], contact=rn["contact"]),
             overhead=over,
             taken_slide=dict(home=int((tkn & ~mv).sum()), open=int(mv.sum()), ws_open=int((mv & ws).sum()), clip_open=int((mv & cl).sum()),
                              slide_p95=round(float(np.percentile(np.abs(a2[mv] - p["a2h"]), 95)), 2) if mv.any() else 0.0),
             levels={m.name: round(float(np.max(prof[m.name])), 2) for m in ch.members})
    r["rlay_ok"] = bool(r["levels"]["rail_t"] >= p["r_lay"] - 1e-6)
    return r


def snap(p):
    p = dict(PARAMS, **p); p["q"] = min(1.0, max(0.8, float(p["q"]))); p["sigma"] = 1 if float(p["sigma"]) >= 0 else -1
    p["m_stop"] = min(25.0, max(K.FOLD_MARGIN, float(p["m_stop"])))
    p["a2max"] = max(float(p["a2h"]) + 1.0, float(p["a2max"]))
    p["carr_t"] = 2.0 if float(p["carr_t"]) >= 1.0 else 0.0
    p["carr_len"] = min(22.0, max(16.0, float(p["carr_len"])))
    p["layout"] = 1 if float(p.get("layout", 0)) >= 0.5 else 0
    p["r_lay"] = min(80.0, max(40.0, float(p["r_lay"])))
    p["side"] = 1 if float(p.get("side", 0)) >= 0.5 else 0
    p["a2min"] = p["a2h"] if (p.get("a2min") is None or not p["side"]) else min(float(p["a2h"]), float(p["a2min"]))
    p["c_extra"] = min(30.0, max(0.0, float(p.get("c_extra", 0.0))))
    p["lift1"] = min(4.0, max(0.0, float(p["lift1"]))); p["l1_end"] = min(8.0, max(0.0, float(p["l1_end"])))
    for k in ("width", "t_link", "rail_w", "rail_th", "rail_end"): p[k] = PARAMS[k]   # never thinned by a search
    return p


def evaluate(B, params):
    """tools/concept_cma.py hook -> (params, report)"""
    p = snap(params)
    r = K.evaluate(B, build, p)
    if p.get("connect", 1):                                   # isolated relay islands are not reachable (flood fill)
        conn, st = flood(p); ch = B._kit_last["chain"]; a2 = np.asarray(ch.q)[:, 3] / QS
        drop = [j for j in range(len(B.res)) if B.res[j] is not None and B.kind[j] == "ws" and abs(a2[j] - p["a2h"]) > 1e-6
                and not conn.get(int(B.idx[j]), False)]
        for j in drop: B.res[j] = None
        B._kit_last["take"] = B._kit_last["take"].copy(); B._kit_last["take"][drop] = False
        r["islands_dropped"] = len(drop); r["flood"] = st
    r = extras(B, r, p)
    if not r["rlay_ok"]: r["audit"] = list(r.get("audit") or []) + [f"rail laid out at r_lay {p['r_lay']} > fitted rail radius {r['levels']['rail_t']}"]; r["honest"] = False
    if p.get("near"):
        r["gap_plain"] = r["gap"]; r["gap"] = r["gap_near1"]
        for k in ("reach", "follow", "inband14", "contact"): r[k + "_plain"] = r[k]; r[k] = r["near1"][k]
    return p, r


REPORT_KEYS = ("modes", "slide_deg_max", "th_top", "window", "stops_mu", "taken_slide", "overhead", "min_metal_skin", "gap_near1",
               "crown_contact_poses", "islands_dropped", "flood", "levels", "rlay_ok")


def bench_eval(B, params):
    _, r = evaluate(B, params)
    return {k: v for k, v in r.items() if SPM._jsonable(v)}


def statics(B, p, r, F_spring=1.5, mu_f=0.15):
    """R17 sag check in mode A: the generalised gravity force of the self-motion (a2 +1 deg, arm and scapula fixed:
    link 1, hub 2, rail move) + slot friction vs the spring moment F_spring * r_slot. Masses from the fitted parts."""
    L = B._kit_last; ch, pts, take = L["chain"], L["pts"], L["take"]; F = B._kitF
    tk = np.nonzero(take)[0]; a2 = np.asarray(ch.q)[:, 3] / QS; A = [j for j in tk if abs(a2[j] - p["a2h"]) <= 1e-6]
    if not A: return None
    mass = {}
    for m in ch.members:
        rho = np.linalg.norm(pts[m.name][A[0]], axis=-1)
        area = float(m.cell * ((rho / m.r_ref) ** 2).sum()) if m.kind != "flat" else float(m.cell * rho.size)
        mass[m.name] = area * m.t * K.TI
    mass["hub2"] = max(mass.get("hub2", 0), 14.0)               # O20 v5 hub: housing + 2 MR117 + encoder (~14 g)
    moving = ["link1", "hub2", "rail_r", "rail_t"] + (["carriage", "link2b"] if p.get("side") else [])
    # finite self-motion: a2 -> a2 + 1 deg, J2 dihedral free, p1 / p3 fixed -> new p2; body points rotate with their frame
    out = []
    for j in A:
        p1 = ch.joints["J1"][j][None]; p3 = ch.joints["J3"][j][None]; p2 = ch.joints["J2"][j][None]
        p2b, _, _ = closure_var(p1, p3, p["a1"], np.array([p["a2h"] + 1.0]), p["sigma"])
        # link 1 + hub 2: rotation about p1 taking p2 -> p2b; rail: the rotation taking (p2, p3) -> (p2b, p3) frames
        def frm(a, b): x = K.unit(a); z = K.unit(np.cross(a, b)); return np.stack([x[0], np.cross(z, x)[0], z[0]], 1)
        R1 = frm(p2b, p1) @ frm(p2, p1).T; R2 = frm(p2b, p3) @ frm(p2, p3).T
        g = F.RS[j] @ np.array([0.0, -9.81, 0.0]) if False else np.array([0.0, -9.81, 0.0])   # thorax frame: y up (bench)
        W = 0.0
        for nm in moving:
            if nm not in pts: continue
            X = pts[nm][j]; c = X.mean(0) * 1e-3; Rm = R1 if nm in ("link1", "hub2") else R2   # side 1: link 2b / carriage ride with hub 3 about the fixed p3 (~R2)
            W += mass[nm] * 1e-3 * float(g @ (Rm @ c - c))
        out.append(abs(W) / math.radians(1.0))                    # N m per rad of the slide coordinate
    Q = np.array(out); r_slot = r["levels"]["rail_t"] * 1e-3
    Mspring = F_spring * r_slot; Mfric = mu_f * sum(mass[n] for n in moving) * 1e-3 * 9.81 * r_slot
    return dict(Q_grav_p95=round(float(np.percentile(Q, 95)), 4), Q_grav_max=round(float(Q.max()), 4), M_spring=round(Mspring, 4),
                M_friction=round(Mfric, 4), holds=bool(Mspring > Q.max() + Mfric), mass_g={k: round(v, 1) for k, v in mass.items()},
                felt_N_at_cuff_100mm=round(Mspring / 0.1, 2))


def redteam(B, p, r):
    SPM.redteam(B, p, r)
    L = B._kit_last; ch = L["chain"]; a2 = np.asarray(ch.q)[:, 3] / QS; tk = np.array([SPM._taken(B, j) for j in range(len(B.res))])
    print("-- slide: taken by state", r.get("taken_slide"), "modes", ch.info.get("modes"), "th_top", ch.info.get("th_top"),
          "window", ch.info.get("window"), "stops", ch.info.get("stops_mu"))
    o = np.argsort(-a2)[:10]
    for i in o: print(f"  a2 {a2[i]:6.2f} taken {bool(tk[i])} {SPM.lab(B, int(i))}")
    print("-- flood", r.get("flood"), "islands dropped", r.get("islands_dropped"))
    print("-- statics (R17 sag, spring 1.5 N)", statics(B, p, r))


def frozen(p0, out, overlap=1.0, fit=(60, 160), big=(110, 360)):
    """fit on Bench(fit) fast, freeze every level, wear on Bench(big) (CB_EXACT=1: exact), K6 at 1 mm radial"""
    coll = K.collisions; K.collisions = functools.partial(coll, overlap=overlap - 1e-4)
    res = dict(model=f"docs/concepts/models/{ID}.py", params=p0, overlap=overlap, exact=os.environ.get("CB_EXACT") == "1", runs={})
    ex = os.environ.pop("CB_EXACT", None)
    try:
        Bf = K.bench(*fit)
    finally:
        if ex is not None: os.environ["CB_EXACT"] = ex
    pf, rf = evaluate(Bf, dict(p0)); prof = {k: np.array(v) for k, v in Bf._kit_last["prof"].items()}
    keep = lambda r: {k: v for k, v in r.items() if SPM._jsonable(v) and k not in ("checks",)}
    res["runs"]["fit"] = dict(keep(rf), bench=list(fit), mode=Bf.mode); json.dump(res, open(out, "w"), indent=1, default=float)
    print("fit", Bf.mode, {k: rf[k] for k in ("gap", "reach", "follow", "inband14", "contact", "honest")}, flush=True)
    Bb = K.bench(*big); fp = K.fit_profiles; t0 = time.time()
    K.fit_profiles = lambda B, chain, fit, q=1.0, mode="march": {k: v.copy() for k, v in prof.items()}
    try:
        r = K.evaluate(Bb, build, pf)
        if pf.get("connect", 1):
            conn, st = flood(pf); a2 = np.asarray(Bb._kit_last["chain"].q)[:, 3] / QS
            drop = [j for j in range(len(Bb.res)) if Bb.res[j] is not None and Bb.kind[j] == "ws" and abs(a2[j] - pf["a2h"]) > 1e-6
                    and not conn.get(int(Bb.idx[j]), False)]
            for j in drop: Bb.res[j] = None
            Bb._kit_last["take"] = Bb._kit_last["take"].copy(); Bb._kit_last["take"][drop] = False
            r["islands_dropped"] = len(drop); r["flood"] = st
        r = extras(Bb, r, pf)
    finally:
        K.fit_profiles = fp
    res["runs"]["frozen"] = dict(keep(r), bench=list(big), mode=Bb.mode, secs=round(time.time() - t0, 1))
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("frozen", Bb.mode, {k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "gap_near1",
                                                     "min_metal_skin", "overhead", "inband_member", "modes", "taken_slide", "flood")}, flush=True)
    if "--redteam" in sys.argv: redteam(Bb, pf, r)
    return res


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].startswith("{") else {}
    if mode == "frozen":
        o = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "frozen.json"
        frozen(snap(par), o); sys.exit()
    B = K.bench(60, 160); t = time.time()
    p, r = evaluate(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "honest", "audit", "closure", "flips", "collide")},
          f"{time.time() - t:.1f}s")
    print("per member", r["inband_member"], "mass", r["mass_g"], "res", r.get("residual_deg"), "margin", r.get("min_margin"))
    print("modes", r.get("modes"), "slide max", r.get("slide_deg_max"), "th_top", r.get("th_top"), "window", r.get("window"),
          "stops", r.get("stops_mu"), "taken", r.get("taken_slide"), "levels", r.get("levels"))
    print("crowns: contact poses", r["crown_contact_poses"], "min", r["crown_min"], "| min metal-skin", r["min_metal_skin"],
          "| gap near1", r["gap_near1"], r["near1"], "| overhead", r["overhead"])
    print("flood", r.get("flood"), "islands dropped", r.get("islands_dropped"))
    print("near", r["near_low"])
    if mode == "redteam": redteam(B, p, r)
