"""Concept model: OFFSET-CENTRE 2R POINTER + SLIDING TWIST SLEEVE AT THE CUFF (id offset-pointer-slip-sleeve).
Rebuilt on the shared kit (tools/concept_kit.py, docs/concepts/KIT.md); the interrupted session's per-pose model was
replaced (its fit loop was ~100x slower and its conventions differed from the kit's).

Chain (docs/concepts/catalogue.json entry; docs/concepts/offset-pointer-slip-sleeve.md):
  scapula -> J1 O20 hub, axis a1 through a centre O (|o| mm from GH, fixed in the scapula) -> link 1 (12 x 3 strap on
  the great circle about O from a1 to j2) -> J2 O20 hub, axis j2 = branch * unit(a1 x dh) through O -> bar (12 x 3
  strap: a cap arc about O from j2 down to th_k from dh, then a run along the rod line at azimuth psi_b, fitted
  radially FROM THE LINE) -> boss (rod clamp O12 x 10) -> O6 rod on the line O -> C, from lam_lo - 15 to lam_hi + 15
  -> linear-rotary sleeve O12 x 25 centred at C (J3 = spin about the rod, ACTIVE; slide lam = |C - O|, PASSIVE) ->
  Hooke U (ring around the sleeve, inner axis u1 in the sleeve, outer axis u2 on two cheeks on the cuff; 2 PASSIVE)
  -> the user's upper-arm cuff (C fixed in the humerus).
DOF: 3 ACTIVE (J1, J2, J3) + 3 PASSIVE (slide, U alpha, U beta). The cuff point fixes dh = unit(C - O) (J1, J2) and
lam (slide); the cuff's orientation about the rod fixes J3 and the two U angles: six chain coordinates for the cuff's
six DOF, every passive one set by closure (nothing sags, R17). Closed form: residual 0 by construction.

Spec corrections: C0 is placed on the BENCH skin in the band humerus frame (station s down the HG -y axis, azimuth
caz: 0 lateral, + anterior), at hC mm above the OUTERMOST skin under it over every bench pose (the spec took BP.V0,
the bind pose). The U neutral is the mean rod direction in the arm frame. The U is modelled at real size (ring + two
cheeks) instead of an O16 disc. Rod variant 'tilt': the prismatic axis may be tilted by rod_tilt deg in the bar
frame toward the arm (Stanford-arm offset P) - not used unless rod_tilt != 0 (see the .md for why it was not needed).

Every part is sampled on its skin-facing surface at ~1 pt / 4 mm2 (cap straps laid out at r_ref 70 like the kit;
the bar's arm run, the hubs and all cylinders in true mm); hub walls, the full circumference of the rod-line parts
and the cheek plates are checked for contact only. A pose is taken iff: dh >= sing deg from +-a1; |U angles| <= u_lim;
lam inside the rod's travel window (<= rod_cap); K2 dense continuity (joint values and axes, 2-deg steps); >= 1 mm
part-part clearance (KD-tree on layered point clouds through each part's thickness); no metal inside the body.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/offset-pointer-slip-sleeve.py [check|sweep|refine|red|plot]
"""
import itertools, json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K                                      # noqa: E402
from scipy.spatial import cKDTree                            # noqa: E402

ID = "offset-pointer-slip-sleeve"
NAME = "Offset-centre 2R pointer with a sliding twist sleeve at the cuff"
SWEEP_JSON = os.path.join(REPO, "docs", "concepts", "sweeps", f"{ID}.json")
D2R = math.pi / 180
HUB_R, STACK, CROWN = K.HUB_R, K.STACK, K.CROWN
ROD_R, BOSS_R, BOSS_L, SLV_R, SLV_L = 3.0, 6.0, 10.0, 6.0, 25.0
RING_RO0, RING_W, RING_SEC, CHEEK_T, CHEEK_L, CUFF_T = 9.0, 6.0, 2.5, 3.0, 10.0, 2.0
SP, CLR_PARTS = 2.0, 1.0

PARAMS = dict(o=20.0, o_az=14.2, o_el=68.4,        # O = o * bvec(o_az, o_el) (scapula frame); spec unit(-0.36, 0.93, 0.09)
              a1_az=115.0, a1_el=42.8,             # J1 axis bvec(a1_az, a1_el); spec unit(0.31, 0.68, 0.67)
              branch=-1,                           # j2 = branch * unit(a1 x dh)
              s=200.0, caz=0.0, hC=13.0,           # cuff station (mm down the humerus), azimuth (deg, 0 lateral, + anterior), rod axis over the outermost skin
              u_lim=40.0, rod_cap=70.0, sing=12.0, # U limit (deg), rod travel cap (mm), pointer singularity margin (deg)
              dpsi=0.0, th_k=35.0,                 # bar azimuth about the rod line vs the arm's mean outward side (deg); cap arc end (deg from dh)
              width=12.0, t_link=3.0, q=1.0)
SWEEP = dict(o=[0, 10, 20, 30], o_dir=["spec", "lat", "post", "ant"], a1=["spec", "hi", "ant", "post"])
O_DIRS = dict(spec=(14.2, 68.4), lat=(90.0, 30.0), post=(0.0, 30.0), ant=(180.0, 30.0), up=(90.0, 89.0))
A1_DIRS = dict(spec=(115.0, 42.8), hi=(100.0, 60.0), ant=(150.0, 35.0), post=(60.0, 40.0), lat=(90.0, 20.0))


# ---- kinematics (geometry from F only: K2 calls it on interpolated frames) -------------------------------------------
_DESIGN = {}


def cuff_point(B, F, p):
    """rest-frame (band HG) cuff point C0 and the arm's outward normal there: hC over the OUTERMOST skin under it"""
    key = (round(p["s"], 3), round(p["caz"], 3), round(p["hC"], 3))
    if key not in _DESIGN:
        n = np.array([math.sin(p["caz"] * D2R), 0.0, math.cos(p["caz"] * D2R)]); a = np.array([0.0, -p["s"], 0.0])
        Pi = np.arange(len(F.RS)); A = np.einsum("pij,j->pi", F.RHG, a); N = np.einsum("pij,j->pi", F.RHG, n)
        rr = np.arange(10.0, 90.0, 0.5); D = K.dist_many(B, np.repeat(Pi, len(rr)), (A[:, None] + rr[None, :, None] * N[:, None]).reshape(-1, 3)).reshape(len(Pi), -1)
        r = rr[np.argmax(D >= 0, axis=1)]                     # march OUT of the arm from its axis: first point outside the skin
        ro = float(np.quantile(r, 0.9))                       # q90 of the arm's own outer skin (max = poses where the arm presses on the trunk)
        _DESIGN[key] = (a + (ro + p["hC"]) * n, n, ro, float(np.median(r)))
    return _DESIGN[key]


def axes(p):
    o = p["o"] * K.bvec(p["o_az"], p["o_el"]); a1 = K.unit(K.bvec(p["a1_az"], p["a1_el"])); return o, a1


def raw_kin(F, p, C0, nC):
    o, a1s = axes(p)
    O = F.S(o); a1 = F.S(a1s); C = F.HG(C0); nW = F.HG(nC)
    d = C - O; lam = np.linalg.norm(d, axis=-1); dh = d / lam[:, None]
    ang = np.degrees(np.arccos(np.clip((dh * a1).sum(-1), -1, 1)))
    j2 = p["branch"] * K.unit(np.cross(a1, dh)); nb = np.cross(dh, j2)
    r_arm = np.einsum("pji,pj->pi", F.RHG, dh)               # rod direction in the arm frame
    v = nW - (nW * dh).sum(-1, keepdims=True) * dh             # arm's outward side at C, seen about the rod line
    psi_out = np.arctan2((v * nb).sum(-1), (v * j2).sum(-1))
    return dict(O=O, a1=a1, C=C, nW=nW, lam=lam, dh=dh, ang=ang, j2=j2, nb=nb, r_arm=r_arm, psi_out=psi_out,
                sing_ok=(ang >= p["sing"]) & (ang <= 180 - p["sing"]))


def design(B, F, p):
    """design-time constants from the bench poses (never held-out clips): U neutral, J1 zero, bar azimuth, rod window"""
    key = json.dumps({k: p[k] for k in ("o", "o_az", "o_el", "a1_az", "a1_el", "branch", "s", "caz", "hC", "u_lim", "rod_cap", "sing", "dpsi")}, sort_keys=True)
    if key in _DESIGN: return _DESIGN[key]
    C0, nC, r_out, r_med = cuff_point(B, F, p); k = raw_kin(F, p, C0, nC); ok = k["sing_ok"]
    e_r = K.unit(k["r_arm"][ok].mean(0)); u2 = K.unit(np.cross(nC, e_r)); e3 = np.cross(e_r, u2)
    j2s = np.einsum("pji,pj->pi", F.RS, k["j2"]); j2ref = K.unit(np.median(j2s[ok], 0))
    r = k["r_arm"]; alpha = np.degrees(np.arctan2(r @ e3, r @ e_r)); beta = np.degrees(np.arcsin(np.clip(r @ u2, -1, 1)))
    ok = ok & (np.abs(alpha) <= p["u_lim"]) & (np.abs(beta) <= p["u_lim"])
    ps = k["psi_out"][ok]; psi_ref = math.atan2(np.sin(ps).mean(), np.cos(ps).mean()) if ok.any() else 0.0
    lam = np.sort(k["lam"][ok]); cap = p["rod_cap"]
    if not len(lam): lo = hi = 0.0
    elif lam[-1] - lam[0] <= cap: lo, hi = lam[0], lam[-1]
    else:
        j = np.searchsorted(lam, lam + cap, side="right") - np.arange(len(lam)); a = int(np.argmax(j)); lo, hi = lam[a], lam[a] + cap
    okw = ok & (k["lam"] >= lo - 1e-6) & (k["lam"] <= hi + 1e-6)
    bmax = float(np.abs(beta[okw]).max()) * D2R if okw.any() else 0.0
    yaw = 0.5 * SLV_L * math.sin(bmax) + SLV_R * math.cos(bmax) + 0.5      # tilted sleeve inside the ring
    ring_ro = max(RING_RO0, yaw + RING_SEC)
    def foot_r(ax, rd, _F=F, _B=B):                                    # q90 arm skin radius along rd from the axis point ax
        Pi = np.arange(len(_F.RS)); A = np.einsum("pij,j->pi", _F.RHG, ax); N = np.einsum("pij,j->pi", _F.RHG, rd); rr = np.arange(10.0, 90.0, 0.5)
        D = K.dist_many(_B, np.repeat(Pi, len(rr)), (A[:, None] + rr[None, :, None] * N[:, None]).reshape(-1, 3)).reshape(len(Pi), -1)
        return float(np.quantile(rr[np.argmax(D >= 0, axis=1)], 0.9))
    dc = dict(foot_r=foot_r, C0=C0, nC=nC, r_out=r_out, r_med=r_med, e_r=e_r, u2=u2, e3=e3, j2ref=j2ref, psi_b=psi_ref + p["dpsi"] * D2R,
              psi_ref=psi_ref, lam_lo=float(lo), lam_hi=float(hi), ring_ro=ring_ro, beta_max=math.degrees(bmax),
              x_top=float(lo) - 15.0, x_bot=float(hi) + 15.0)
    _DESIGN[key] = dc; return dc


class Kin:
    def __init__(self, ok, q, joints, k): self.ok, self.q, self.joints, self.k, self.q_period, self.members, self.info = ok, q, joints, k, 360.0, [], {}


def kin(B, F, p):
    dc = design(B, K._F0, p); k = raw_kin(F, p, dc["C0"], dc["nC"])
    r = k["r_arm"]; alpha = np.degrees(np.arctan2(r @ dc["e3"], r @ dc["e_r"])); beta = np.degrees(np.arcsin(np.clip(r @ dc["u2"], -1, 1)))
    u2W = F.HG(dc["u2"]); u1 = K.unit(np.cross(u2W, k["dh"]))  # U cross: inner axis fixed in the sleeve, normal to the rod
    J1 = K.axis_angle(k["a1"], F.S(dc["j2ref"]), k["j2"]); J2 = K.axis_angle(k["j2"], k["a1"], k["dh"]); J3 = K.axis_angle(k["dh"], k["j2"], u1)
    ok = k["sing_ok"] & (np.abs(alpha) <= p["u_lim"]) & (np.abs(beta) <= p["u_lim"])
    ok &= (k["lam"] >= dc["lam_lo"] - 1e-6) & (k["lam"] <= dc["lam_hi"] + 1e-6)
    k.update(alpha=alpha, beta=beta, u1=u1, u2W=u2W, J1=J1, J2=J2, J3=J3)
    return Kin(ok, np.stack([J1, J2, J3, alpha, beta], -1), dict(J1=k["a1"], J2=k["j2"], J3=k["dh"], U1=u1), k)


# ---- members: rays (origin X, direction G) fitted along G, or fixed points ----------------------------------------
class M:
    def __init__(self, name, X, G, t=3.0, tmin=0.0, grid=None, step=2.0, fixed=False, extra=None):
        self.name, self.X, self.G, self.t, self.tmin, self.grid, self.step, self.fixed, self.extra = name, X, G, t, tmin, grid, step, fixed, extra
        self.ramps = []          # [(mask (m,), other name, dz, axis key)]: height along that hub's axis >= other's level + dz


def strap_rays(O, u, v, width, r_ref=70.0):
    D = K.strap_dirs(u, v, width=width, r_ref=r_ref); P_, ns, nc, _ = D.shape
    return np.broadcast_to(O[:, None, :], (P_, ns * nc, 3)), D.reshape(P_, -1, 3), (ns, nc)


def disc_rays(O, k, h0=70.0):
    a, b = K.plane_frame(k); xy = K.disc_xy(HUB_R, SP)
    X = O[:, None, :] + xy[None, :, :1] * a[:, None, :] + xy[None, :, 1:] * b[:, None, :]
    return X, np.broadcast_to(k[:, None, :], X.shape), xy, a, b


def cyl_pts(O, dh, vin, x0, x1, r, half=True):
    """points on a cylinder about the line O + x dh (P, 3), x in [x0, x1] (P,) or scalars; the half facing vin"""
    P_ = len(dh); x0 = np.broadcast_to(np.asarray(x0, float), (P_,)); x1 = np.broadcast_to(np.asarray(x1, float), (P_,))
    nx = max(2, int(float((x1 - x0).max()) / SP) + 1); s = np.linspace(0, 1, nx)
    span = (0.5 if half else 1.0) * math.pi; na = max(3, int(2 * span * r / SP) + 1)
    ph = np.linspace(-span, span, na, endpoint=half)
    vin = K.unit(vin - (vin * dh).sum(-1, keepdims=True) * dh); vb = np.cross(dh, vin)
    R = r * (np.cos(ph)[None, :, None] * vin[:, None, :] + np.sin(ph)[None, :, None] * vb[:, None, :])     # (P, na, 3)
    xs = x0[:, None] + (x1 - x0)[:, None] * s[None, :]
    return (O[:, None, None, :] + xs[:, :, None, None] * dh[:, None, None, :] + R[:, None, :, :]).reshape(P_, -1, 3)


def members(B, F, p, kn):
    dc = design(B, K._F0, p); k = kn.k; O, a1, j2, dh, nb = k["O"], k["a1"], k["j2"], k["dh"], k["nb"]; w, t = p["width"], p["t_link"]
    out = []
    X, G, xy1, A1, B1 = disc_rays(O, a1); h1 = M("hub1", X, G, t=CROWN); h1.flat = (a1, xy1); out.append(h1)
    X, G, xy2, A2, B2 = disc_rays(O, j2); h2 = M("hub2", X, G, t=CROWN); h2.flat = (j2, xy2); out.append(h2)
    X, G, g = strap_rays(O, a1, j2, w); l1 = M("link1", X, G, t=t, tmin=15.0, grid=g)
    l1.ramps = [("J1", "hub1", STACK), ("J2", "hub2", 0.0)]; out.append(l1)
    psb = dc["psi_b"]; uk = math.cos(psb) * j2 + math.sin(psb) * nb                    # bar azimuth about the rod line
    thk = p["th_k"] * D2R; vend = math.cos(thk) * dh + math.sin(thk) * uk
    X, G, g = strap_rays(O, j2, vend, w); bc = M("bar_cap", X, G, t=t, tmin=15.0, grid=g); bc.ramps = [("J2", "hub2", STACK)]; out.append(bc)
    x_k = 70.0 * math.cos(thk); x_e = dc["x_top"] - BOSS_L / 2
    ns = max(2, int((x_e - x_k) / SP) + 1); xs = np.linspace(x_k, x_e, ns); cs = np.arange(-w / 2, w / 2 + 1e-6, SP)
    tang = np.cross(dh, uk)
    X = O[:, None, None, :] + xs[None, :, None, None] * dh[:, None, None, :] + cs[None, None, :, None] * tang[:, None, None, :]
    ba = M("bar_arm", X.reshape(len(O), -1, 3), np.broadcast_to(uk[:, None, :], (len(O), ns * len(cs), 3)), t=t,
           tmin=np.where(np.repeat(xs, len(cs)) > dc["x_top"] - BOSS_L - 2, BOSS_R, ROD_R + 1.0), grid=(ns, len(cs)))
    out.append(ba)
    vin = -k["nW"]; lam = k["lam"]                                                        # arm side of the rod line
    rod_lo, rod_hi = dc["x_top"], dc["x_bot"]
    fixed = dict(boss=(dc["x_top"] - BOSS_L, dc["x_top"], BOSS_R), sleeve=(lam - SLV_L / 2, lam + SLV_L / 2, SLV_R))
    for nm, (x0, x1, r) in fixed.items():
        out.append(M(nm, cyl_pts(O, dh, vin, x0, x1, r), None, fixed=True, extra=cyl_pts(O, dh, vin, x0, x1, r, half=False)))
    out.append(M("rod", cyl_pts(O, dh, vin, rod_lo, rod_hi, ROD_R), None, fixed=True,          # whole rod (the 25 mm inside the sleeve too)
                 extra=cyl_pts(O, dh, vin, rod_lo, rod_hi, ROD_R, half=False)))
    rw = K.unit(k["r_arm"] - (k["r_arm"] @ dc["u2"])[:, None] * dc["u2"])                       # ring axis (arm frame): rotated by alpha about u2
    rwW = K.unit(np.einsum("pij,pj->pi", F.RHG, rw))
    ring = cyl_pts(k["C"] - RING_W / 2 * rwW, rwW, vin, 0.0, RING_W, dc["ring_ro"])
    out.append(M("ring", ring, None, fixed=True, extra=cyl_pts(k["C"] - RING_W / 2 * rwW, rwW, vin, 0.0, RING_W, dc["ring_ro"], half=False)))
    if "ch_foot" not in dc: dc["ch_foot"], dc["ch_full"] = cheeks(dc, True), cheeks(dc, False)
    out.append(M("cheeks", F.HG(dc["ch_foot"]), None, fixed=True, extra=F.HG(dc["ch_full"])))
    return out


def cheeks(dc, foot=True):
    """two 3 x 10 plates on the cuff carrying the U's outer pins (arm frame), feet on the cuff shell: each foot sample
    sits CUFF_T over the q90 (over the bench poses) of the arm's own skin under it; plates rise to the pin level"""
    C0, n, u2 = dc["C0"], dc["nC"], dc["u2"]; y = np.array([0.0, 1.0, 0.0]); g = np.arange(-CHEEK_L / 2, CHEEK_L / 2 + 1e-6, SP); pts = []
    piv = C0 @ n                                                       # pin level (rod axis height from the humerus axis)
    for sg in (-1, 1):
        for tt in np.arange(0, CHEEK_T + 1e-6, 1.5):
            for a in g:
                P0 = C0 + sg * (dc["ring_ro"] + 0.5 + tt) * u2 + a * y; ax = (P0 @ y) * y; rd = K.unit(P0 - ax)
                rf = dc["foot_r"](ax, rd) + CUFF_T
                for hh in ([0.0] if foot else np.arange(0, max(0.0, piv - rf) + 1e-6, SP)):
                    pts.append(ax + (rf + hh) * rd)
    return np.array(pts)


# ---- fit / collide / score ----------------------------------------------------------------------------------------
def fit(B, mem, fit_idx, q):
    """per-sample heights along G (quantile q over the fit poses), hub levels, ramps, climb limit -> {name: h (m,)}"""
    Pi = fit_idx; fm = [m for m in mem if not m.fixed]; segs = []; I, Og, Dg = [], [], []
    for m in fm:
        n = m.X.shape[1]; segs.append(n); tmin = np.broadcast_to(np.asarray(m.tmin, float), (n,))
        I.append(np.repeat(Pi, n)); Og.append((m.X[Pi] + tmin[None, :, None] * m.G[Pi]).reshape(-1, 3)); Dg.append(m.G[Pi].reshape(-1, 3))
    R = K.requirement(B, np.concatenate(I), np.concatenate(Dg), t0=0.0, O=np.concatenate(Og)) if len(Pi) else None
    h, o = {}, 0
    for m, n in zip(fm, segs):
        Rm = R[o:o + len(Pi) * n].reshape(len(Pi), n) + np.broadcast_to(np.asarray(m.tmin, float), (n,))[None]; o += len(Pi) * n
        h[m.name] = K.quantile(Rm, q)
    for nm in ("hub1", "hub2"): h[nm][:] = h[nm].max()                         # flat O20 disc at its level F
    lv = dict(hub1=float(h["hub1"][0]), hub2=float(h["hub2"][0]))
    for m in fm:
        for jn, hub, dz in m.ramps:                                            # ends at a hub: height along its axis
            ax = dict(J1="a1", J2="j2")[jn]; kv = mem[0].ax[ax][Pi]
            c = np.abs(np.einsum("pmd,pd->pm", m.G[Pi], kv)).min(0)            # cos(angle from the hub axis), worst pose
            near = np.arccos(np.clip(c, -1, 1)) * 70.0 < HUB_R + 2.0
            h[m.name][near] = np.maximum(h[m.name][near], (lv[hub] + dz) / np.maximum(c[near], 0.5))
        if m.name == "bar_cap" and "link1" in h:                               # K6 by construction: the bar passes OVER link 1
            h[m.name] = over(m, h[m.name], [x for x in fm if x.name == "link1"][0], h["link1"], mem[0].ax["j2"], Pi)
        if m.grid:                                                             # K5 climb <= 60 deg (raises only)
            ns, nc = m.grid; R2 = h[m.name].reshape(ns, nc); x = np.arange(ns) * m.step; sl = math.tan(60 * D2R)
            h[m.name] = (R2[None] - sl * np.abs(x[:, None, None] - x[None, :, None])).max(1).ravel()
    return h


def over(m, hm, o, ho, j2, Pi, gap=CLR_PARTS + 1.0, chunk=16):
    """raise member m (rays from O) to >= o's top + gap wherever o passes under it in any fit pose (angular distance x
    radius < 1 + 1 + gap); the J2 stack zone (HUB_R + 2 of the j2 axis) is left to the hub stack"""
    need = np.zeros(len(hm)); thr = 2.0 + gap
    for c0 in range(0, len(Pi), chunk):
        P = Pi[c0:c0 + chunk]; Dm, Do = m.G[P].astype(np.float32), o.G[P].astype(np.float32)
        dot = np.matmul(Dm, Do.transpose(0, 2, 1))                            # (k, m, n)
        rr = np.minimum(hm[None, :, None], ho[None, None, :])
        near = dot > 1 - 0.5 * (thr / rr) ** 2
        zone = np.arccos(np.clip(np.abs(np.einsum("pmd,pd->pm", m.G[P], j2[P])), -1, 1)) * hm[None] > HUB_R + 2.0
        near &= zone[:, :, None]
        top = np.where(near, (ho + o.t + gap)[None, None, :], 0.0).max(2).max(0)
        need = np.maximum(need, top)
    return np.maximum(hm, need)


def points(mem, h, layers=False):
    out = {}
    for m in mem:
        if m.fixed: out[m.name] = m.X
        else:
            P0 = m.X + h[m.name][None, :, None] * m.G
            out[m.name] = P0 if not layers else np.concatenate([P0, P0 + m.t / 2 * m.G, P0 + m.t * m.G], 1)
    return out


PAIRS = [("link1", "bar_cap"), ("link1", "bar_arm"), ("hub1", "bar_cap"), ("hub1", "bar_arm")] + \
        [(a, b) for a in ("hub1", "link1", "hub2", "bar_cap") for b in ("sleeve", "ring", "cheeks", "rod", "boss")] + \
        [("bar_arm", "ring"), ("bar_arm", "cheeks"), ("boss", "ring"), ("boss", "cheeks"), ("boss", "sleeve"), ("hub1", "hub2")]


def collide(mem, h, take, kn):
    """(P,) bool: some pair of non-adjacent parts closer than 1 mm (layered clouds through the thickness; 2 mm grid ->
    + 1.0 mm sampling slack); hub stacks: link 1 / bar samples within HUB_R + 2 of the J2 axis are the joint itself"""
    L = points(mem, h, layers=True); Mm = {m.name: m for m in mem}
    for nm in ("hub1", "hub2"):                                                # hub bodies: disc layers to the crown
        m = Mm[nm]; k_ = m.ax_self; L[nm] = np.concatenate([L[nm][:, :len(m.X[0])] + z * k_[:, None, :] for z in (0, 4, 8, 12.25)], 1)
    for nm in ("sleeve", "ring", "rod", "boss", "cheeks"): L[nm] = Mm[nm].extra
    hit = np.zeros(len(take), bool); j2 = kn.k["j2"]; O = kn.k["O"]; why = {}
    lo = {n: L[n].min(1) for n in L}; hi = {n: L[n].max(1) for n in L}             # AABB prefilter per pose
    for i in np.nonzero(take)[0]:
        for a, b in PAIRS:
            if np.any(lo[a][i] > hi[b][i] + CLR_PARTS + 1.0) or np.any(lo[b][i] > hi[a][i] + CLR_PARTS + 1.0): continue
            A, Bp = L[a][i], L[b][i]
            if {a, b} & {"bar_cap", "bar_arm"} and "link1" in (a, b):              # J2 stack zone exempt
                ra = np.linalg.norm(np.cross(A - O[i], j2[i]), axis=1); rb = np.linalg.norm(np.cross(Bp - O[i], j2[i]), axis=1)
                A, Bp = A[ra > HUB_R + 2], Bp[rb > HUB_R + 2]
                if not len(A) or not len(Bp): continue
            dmin = cKDTree(A).query(Bp, distance_upper_bound=CLR_PARTS + 1.0)[0].min()
            if dmin < CLR_PARTS + 1.0: hit[i] = True; why[i] = (a, b); break
    return hit, why


def evaluate(B, p, verbose=False, cont=True):
    p = dict(PARAMS, **p); F = K._F0; t0 = time.time()
    kn = kin(B, F, p); ok = kn.ok.copy(); flips = 0
    if cont: ok, flips = K.continuity_dense(B, F, lambda B_, F_, p_: kin(B_, F_, p_), p, ok)
    mem = members(B, F, p, kn)
    mem[0].ax = dict(a1=kn.k["a1"], j2=kn.k["j2"]); mem[0].ax_self = kn.k["a1"]; mem[1].ax_self = kn.k["j2"]
    Pi = np.nonzero(ok)[0]
    if len(Pi) < 3:
        B.reset(); r = B.report(); r.update(closure=round(float(kn.ok.mean()), 4), flips=flips); return r, None
    h = fit(B, mem, Pi, p["q"])
    hit, why = collide(mem, h, ok, kn); take = ok & ~hit; Ti = np.nonzero(take)[0]
    pts = points(mem, h); names = [m.name for m in mem]
    allp = np.concatenate([pts[n][Ti] for n in names], 1)
    d = K.dist_many(B, np.repeat(Ti, allp.shape[1]), allp.reshape(-1, 3)).reshape(len(Ti), -1)
    ex = [m.extra[Ti] for m in mem if m.extra is not None]
    hubw = []
    for m in mem[:2]:                                                          # hub walls to the crown (contact only)
        k_ = m.ax_self[Ti]; a, b = K.plane_frame(k_); ang = np.linspace(0, 2 * np.pi, 32, endpoint=False)
        ring = HUB_R * (np.cos(ang)[None, :, None] * a[:, None, :] + np.sin(ang)[None, :, None] * b[:, None, :])
        base = kn.k["O"][Ti] + h[m.name][0] * k_
        hubw.append(np.concatenate([base[:, None, :] + ring + z * k_[:, None, :] for z in (0, 4, 8, 12.25)], 1))
    E = np.concatenate(ex + hubw, 1); de = K.dist_many(B, np.repeat(Ti, E.shape[1]), E.reshape(-1, 3)).reshape(len(Ti), -1).min(1)
    B.reset()
    for j, i in enumerate(Ti): B.res[i] = d[j] if de[j] >= 0 else np.r_[d[j], de[j]]
    r = B.report(); clip = np.array([B.kind[i] == "clip" for i in Ti], bool); good = (d.min(1) >= 0) & (de >= 0); o = 0; per = {}
    for n in names:
        s = pts[n].shape[1]; dm = d[clip & good, o:o + s]; o += s
        per[n] = [round(float(((dm >= 2) & (dm <= 14)).mean()), 3) if dm.size else 0.0, round(float(np.median(dm)), 1) if dm.size else None, s]
    cb = {}; o = 0
    for n in names:
        s_ = pts[n].shape[1]; cb[n] = int((d[:, o:o + s_].min(1) < 0).sum()); o += s_
    cb["walls/full"] = int((de < 0).sum())
    dc = design(B, F, p); kk = kn.k
    r.update(per=per, contact_by=cb, closure=round(float(kn.ok.mean()), 4), flips=int(flips), collide=round(float(hit[ok].mean()) if ok.any() else 0, 4),
             residual_mm=0.0, F1=round(float(h["hub1"][0]), 1), F2=round(float(h["hub2"][0]), 1), lam=[round(dc["lam_lo"], 1), round(dc["lam_hi"], 1)],
             ring_ro=round(dc["ring_ro"], 1), beta_max=round(dc["beta_max"], 1), hC_skin=[round(dc["r_med"], 1), round(dc["r_out"], 1)],
             why=dict(sing=int((~kk["sing_ok"]).sum()), U=int((kk["sing_ok"] & ~((np.abs(kk["alpha"]) <= p["u_lim"]) & (np.abs(kk["beta"]) <= p["u_lim"]))).sum()),
                      slide=int(((kk["lam"] < dc["lam_lo"] - 1e-6) | (kk["lam"] > dc["lam_hi"] + 1e-6)).sum()), flip=int(flips), parts=int(hit.sum()),
                      contact=int(sum(1 for i in Ti if B.res[i].min() < 0))),
             secs=round(time.time() - t0, 1))
    B._last = dict(kn=kn, mem=mem, h=h, pts=pts, take=take, ok=ok, hit=hit, why=why, d=d, de=de, Ti=Ti, names=names)
    if verbose: print(json.dumps(r, default=str))
    return r, B._last


def metal(pose, frames, params, B=None, i=None):
    """(k, 3) metal sample points of bench pose i (thorax frame) or None. The rigid undersides are fitted over the
    whole bench, so B and i are required (pose / frames are kept for the swarm signature)."""
    key = json.dumps(dict(PARAMS, **params), sort_keys=True)
    if getattr(B, "_mkey", None) != key: evaluate(B, params); B._mkey = key
    L = B._last
    if not L["take"][i]: return None
    return np.concatenate([L["pts"][n][i] for n in L["names"]])


def setup(n_clip=60, n_ws=160):
    B = K.bench(n_clip, n_ws); K._F0 = K.frames(B); return B


def write_entry(rows, p, r):
    rows.append(dict(k=len(rows), t=K.now(), params=p, **{x: r[x] for x in ("inband14", "inband10", "reach", "follow", "contact", "gap")},
                     closure=r.get("closure"), why=r.get("why"), per=r.get("per")))
    tmp = SWEEP_JSON + ".tmp"; json.dump(rows, open(tmp, "w"), indent=1); os.replace(tmp, SWEEP_JSON)


def run_sweep(B, cfgs, rows, best=None):
    for p in cfgs:
        try: r, _ = evaluate(B, p)
        except Exception as e: print("ERR", p, e, flush=True); continue
        write_entry(rows, p, r)
        print(f"[{rows[-1]['k']}] gap {r['gap']} reach {r['reach']} follow {r['follow']} ib14 {r['inband14']} ib10 {r['inband10']} contact {r['contact']} "
              f"why {r.get('why')} {r.get('secs')}s  {p}", flush=True)
        if best is None or r["gap"] < best[0]:
            best = (r["gap"], p, r); K.log_event(f"offset-pointer-slip-sleeve new best gap {r['gap']} (reach {r['reach']}, follow {r['follow']}, in-band 14 {r['inband14']}, contact {r['contact']}) at {json.dumps(p)}")
    return best


if __name__ == "__main__":
    a = sys.argv[1:]; mode = a[0] if a else "check"
    nc = int(a[a.index("--n-clip") + 1]) if "--n-clip" in a else 60; nw = int(a[a.index("--n-ws") + 1]) if "--n-ws" in a else 160
    B = setup(nc, nw); print("bench", B.mode, len(B.idx), flush=True)
    if mode == "check":
        r, _ = evaluate(B, json.loads(a[1]) if len(a) > 1 and a[1].startswith("{") else {}, verbose=True)
    elif mode in ("sweep", "refine"):
        rows = json.load(open(SWEEP_JSON)) if os.path.exists(SWEEP_JSON) and "--resume" in a else []
        best = min(((e["gap"], e["params"], None) for e in rows), key=lambda x: x[0]) if rows else None
        if mode == "sweep":                                # coarse: centre offset, J1 axis, cuff height, underside quantile
            cfgs = []
            for o, a1, dpsi, q in itertools.product([0.0, 10.0, 20.0], ["spec", "hi", "post", "ant"], [0.0, -45.0, 45.0], [0.9, 0.95]):
                cfgs.append(dict(PARAMS, o=o, a1_az=A1_DIRS[a1][0], a1_el=A1_DIRS[a1][1], dpsi=dpsi, q=q))
        else:                                              # refine around the best: bar azimuth, cuff station / azimuth, cap end, O direction
            b = dict(best[1]); cfgs = []
            for k_, vals in dict(q=[0.98, 1.0], dpsi=[b["dpsi"] - 20, b["dpsi"] + 20], s=[130, 160, 180, 230], caz=[-40, -20, 20, 40], th_k=[25, 45, 55],
                                 o_dir=list(O_DIRS), branch=[1], sing=[8, 16], hC=[b["hC"] - 2, b["hC"] + 3], o=[5.0, 10.0]).items():
                for v in vals:
                    c = dict(b)
                    if k_ == "o_dir": c["o_az"], c["o_el"] = O_DIRS[v]
                    else: c[k_] = v
                    if c != b: cfgs.append(c)
        if "--q1" in a:                                    # second refine at q = 1 (no pose sacrificed): J1 axis, bar routing, station
            b = dict(min(rows, key=lambda e: e["gap"])["params"]); cfgs = []
            for k_, vals in dict(a1_az=[85, 115], a1_el=[50, 70], dpsi=[30, 60], th_k=[55, 65], s=[190, 210], hC=[14], width=[10], q=[0.995]).items():
                for v in vals: c = dict(b); c[k_] = v; cfgs.append(c)
        best = run_sweep(B, cfgs, rows, best); print("BEST", best[0], json.dumps(best[1]))
    elif mode == "red":                                    # red team the best configuration: jams, pinches, the poses it loses
        rows = json.load(open(SWEEP_JSON)); b = min(rows, key=lambda e: e["gap"]); r, L = evaluate(B, b["params"])
        print("BEST k", b["k"], json.dumps({x: r[x] for x in ("gap", "reach", "follow", "inband14", "inband10", "contact", "per", "contact_by", "why", "F1", "F2", "lam")}))
        kk = L["kn"].k; d, Ti = L["d"], L["Ti"]; names = L["names"]; sizes = [L["pts"][n].shape[1] for n in names]; cut = np.cumsum([0] + sizes)
        lost = [i for i in range(len(B.idx)) if not (B.res[i] is not None and B.res[i].min() >= 0)]
        why = lambda i: ("sing" if not kk["sing_ok"][i] else "U/slide" if not L["kn"].ok[i] else "flip" if not L["ok"][i] else
                         "parts " + "-".join(L["why"].get(i, ("?",))) if L["hit"][i] else "contact " + ",".join(n for j, n in enumerate(names) if (B.res[i][cut[j]:cut[j + 1]].min() < 0)) or "walls")
        from collections import Counter
        print("lost poses by reason:", Counter(why(i).split(" ")[0] for i in lost))
        print("contact by part:", Counter(p_ for i in lost for p_ in (why(i).split(" ")[1].split(",") if why(i).startswith("contact") else [])))
        tests = dict(rest=dict(plane=0, elev=0), overhead=dict(elev=150), across=dict(plane=110), behind=dict(axial=-80))
        for nm, cond in tests.items():
            sel = [i for i, p_ in enumerate(B.poses) if all((p_[k_] >= v) if v > 0 else (p_[k_] <= v) if v < 0 else abs(p_[k_]) < 10 for k_, v in cond.items())]
            tk = [i for i in sel if B.res[i] is not None and B.res[i].min() >= 0]
            print(f"{nm}: {len(tk)}/{len(sel)} taken; lost:", Counter(why(i) for i in sel if i not in tk).most_common(4))
        j, m = np.unravel_index(np.argmin(np.where(d.min(1, keepdims=True) >= 0, d, 99)), d.shape); part = names[np.searchsorted(cut, m, side="right") - 1]
        print("pinch (closest metal in a taken pose):", round(float(d[j, m]), 2), "mm", part, B.poses[Ti[j]])
        J = np.stack([kk["J1"], kk["J2"], kk["J3"], kk["alpha"], kk["beta"]], 1)[L["take"]]
        print("ranges deg J1 J2 J3 alpha beta:", [[round(float(np.min(c)), 1), round(float(np.max(c)), 1)] for c in J.T])
