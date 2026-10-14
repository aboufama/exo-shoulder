"""Geometry of the built band-design members, re-derived from the user's own generator (band_cad/build_band_cad.py,
imported read-only, nothing written there) and meshed as structured hex8 for fe_core.

How: the generator is imported as a module with its section builder and loft monkey-patched to RECORD the section
parameters (centre, frame, width, thickness, contour) instead of building B-rep. Thickness variants are made by changing
the generator's own globals (T_LINK, T_LO / STACK, T_SEAT, T_W) before re-recording, so every height, path and contour
follows exactly as the CAD would.

Mesh: each hub is an O-grid (polar) around its pin from the bore / pin radius to the planform outline, cut by the line
where the ribbon starts (long links) or by the bisector (short links); the ribbon is a section stack between the two
cut lines; nodes on the cut lines are shared. In-plane (x along the hub's link direction, y lateral), through-thickness
nl layers (the contoured skin side moves the bottom face). The G2 edge rounds are approximated by a corner squash.

Short-link planform note: the generator's build_link_short() uses 'union of the two discs' only. With the O26 hubs
(HUB_R 13) the short-link switch (centre distance < 2 HUB_R + 8 = 34) lets discs that do NOT overlap (26 < d < 34) through,
which leaves a 1.6 mm wide neck (sections of width 2 * max(hw, 0.8)). `fix_short=True` (default for the FEA) uses the
intended planform: smooth union of the two discs and the 14 mm strip (same k = 8 smooth-min as the long links).
"""
import sys, os, math, importlib.util, types
sys.dont_write_bytecode = True
import numpy as np
from scipy.spatial import cKDTree
from scipy.interpolate import CubicSpline

BAND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "band_cad")
SNAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshot", "build_band_cad.py")
_GEN = {}


def generator(key):
    """import build_band_cad for design `key` (fresh module object per key)"""
    if key in _GEN: return _GEN[key]
    argv = list(sys.argv); sys.argv = [os.path.join(BAND, "build_band_cad.py"), key, "1"]
    if BAND not in sys.path: sys.path.insert(0, BAND)                       # arm_end (read-only import)
    src = open(SNAP).read()                                                  # frozen copy of the generator (10:16, 2026-10-14)
    mod = types.ModuleType(f"bbc_{key}"); mod.__file__ = os.path.join(BAND, "build_band_cad.py")   # HERE -> band_cad/inputs
    cwd = os.getcwd()
    try:
        exec(compile(src, mod.__file__, "exec"), mod.__dict__)
    finally:
        sys.argv = argv; os.chdir(cwd)
    mod._rec = []
    def rec_section(c, acr, up, wd, tp, depth_fn=None, x_plate=0.0):
        mod._rec.append(dict(c=np.array(c, float), acr=np.array(acr, float), up=np.array(up, float), wd=float(wd), tp=float(tp),
                             dep=depth_fn, x=float(x_plate)))
        return np.zeros((4, 3))
    mod.section_pts = rec_section
    class _Dummy:
        def __getattr__(self, k): return lambda *a, **kw: self
    mod.loft = lambda secs: _Dummy()
    mod._defaults = dict(T_LINK=mod.T_LINK, T_LO=mod.T_LO, T_SEAT=mod.T_SEAT, T_W=mod.T_W, STACK=mod.STACK)
    _GEN[key] = mod
    return mod


def set_thickness(mod, t_link=None, t_lo=None, t_seat=None, t_w=None):
    d = mod._defaults
    mod.T_LINK = d["T_LINK"] if t_link is None else t_link
    mod.T_LO = d["T_LO"] if t_lo is None else t_lo
    mod.T_SEAT = d["T_SEAT"] if t_seat is None else t_seat
    mod.T_W = d["T_W"] if t_w is None else t_w
    mod.STACK = mod.T_LO + mod.T_W


def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v, axis=-1, keepdims=True)


def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0.0) / k; return np.minimum(a, b) - h ** 3 * k / 6.0


def halfwidth_from_sdf(sdf2, x, hi=40.0):
    """largest y with sdf2(x, y) < 0 (planforms here are y-convex), vectorised bisection"""
    x = np.atleast_1d(np.asarray(x, float)); lo = np.zeros_like(x); hi_ = np.full_like(x, hi)
    inside0 = sdf2(x, lo) < 0
    for _ in range(50):
        m = 0.5 * (lo + hi_); ins = sdf2(x, m) < 0; lo = np.where(ins, m, lo); hi_ = np.where(ins, hi_, m)
    return np.where(inside0, lo, 0.0)


# ------------------------------------------------------------------------------------------- member descriptions
class Hub:
    """one hub: plate frame (axis n, link direction d, lateral lat), skin face z0 along n, plate thickness tp, role,
    depth function dep(x, y) (>= 0, skin side) or None, planform half-width hw(x) for x <= x_end (local coords)"""
    def __init__(self, **kw): self.__dict__.update(kw)


def describe_member(key, mi, fix_short=True, x_cut=None):
    """returns dict(kind='long'|'short'|'base', hubs=[Hub, ...], strip=..., map=callable) for member mi of design key
    (mi = 0: scapula base). Uses the generator's current thickness globals."""
    G = generator(key); CH = G.CH; HUB_R, HW = G.HUB_R, G.HW
    G._rec.clear()
    if mi == 0:
        body, bi = G.build_base(); rec = list(G._rec)
        a = np.array([1.0, 0, 0]); d = np.array([0, -1.0, 0]); lat = np.array([0, 0, 1.0])
        TAB = 24.0; xe = HUB_R + TAB - HW
        def sdf2(x, y):
            disc = np.hypot(x, y) - HUB_R
            q = np.maximum(x - xe, 0.0); strip = np.where(x <= xe, np.maximum(np.abs(y) - HW, -x), np.hypot(q, y) - HW)
            return -smax_(-disc, -strip)
        depf = rec[0]["dep"]
        xj = HUB_R + 7.0
        hub = Hub(n=a, d=d, lat=lat, z0=bi["z0"], tp=bi["tp"], low=bi["low"], dep=depf, x_end=xj,
                  sdf2=lambda x, y: base_sdf(x, y, HUB_R, HW, xe), J=1, mi=0, end=1, bolts=[HUB_R + 8.0, HUB_R + 18.0])
        # the tab beyond the cut line: a flat strip in the plate frame to the tab tip (square tip instead of the stadium
        # round: the last 7 mm beyond the outer bolt are unloaded)
        xs = np.linspace(xj, xe + HW, int(math.ceil((xe + HW - xj) / 0.65)) + 1)
        C = np.array([a * (bi["z0"] + bi["tp"] / 2) + x * d for x in xs])
        strip = dict(direct=(C, np.repeat(lat[None], len(xs), 0), np.repeat(a[None], len(xs), 0), np.full(len(xs), bi["tp"]), xs), hw=HW)
        return dict(kind="base", hubs=[hub], strip=strip, key=key, mi=mi, rec=rec)
    th = G.A[mi - 1]; a = np.array([1.0, 0, 0]); b = np.array([math.cos(th), math.sin(th), 0.0]); LAT = np.array([0, 0, 1.0])
    (zA, tA, lowA), (zB, tB, lowB) = G.plate_role(mi, 0), G.plate_role(mi, 1)
    short_gen = th * 0.5 * (zA + zB) < 2 * HUB_R + 8.0
    xj_ = HUB_R + 7.0; sA_ = xj_ / (zA + tA / 2) / th; sB_ = 1 - xj_ / (zB + tB / 2) / th
    folded = (not short_gen) and sA_ > sB_ - 0.02                          # generator's long-link ribbon would run backwards
    short = short_gen or folded
    body, li = G.build_link(mi); rec = list(G._rec)
    dA = unit(b - (b @ a) * a); dB = unit(a - (a @ b) * b); latA = unit(LAT - (LAT @ a) * a); latB = unit(LAT - (LAT @ b) * b)
    JA, JB = G.joint_of(mi, 0), G.joint_of(mi, 1)
    if not short:
        assert len(rec) == 19 + 5 + 20 + 5 + 19, len(rec)
        depA = rec[0]["dep"]; depB = rec[-1]["dep"]
        xj = HUB_R + 7.0
        pf = lambda x, y: planform_sdf(x, y, HUB_R, HW)
        hA = Hub(n=a, d=dA, lat=latA, z0=zA, tp=tA, low=lowA, dep=depA, x_end=xj, sdf2=pf, J=JA, mi=mi, end=0)
        hB = Hub(n=b, d=dB, lat=latB, z0=zB, tp=tB, low=lowB, dep=depB, x_end=xj, sdf2=pf, J=JB, mi=mi, end=1)
        if x_cut is not None and x_cut < xj:                                     # shorter flat stubs: more room for a steep ramp
            xj = x_cut; hA.x_end = xj; hB.x_end = xj
        def stub(h, x):
            return dict(c=h.n * (h.z0 + h.tp / 2) + x * h.d, acr=h.lat, up=h.n, tp=h.tp)
        secs = [stub(hA, xj - 2.0), stub(hA, xj - 1.0), stub(hA, xj)] + rec[24:44] + [stub(hB, xj), stub(hB, xj - 1.0), stub(hB, xj - 2.0)]
        C = np.array([s["c"] for s in secs]); seg = np.linalg.norm(np.diff(C, axis=0), axis=1)
        X = np.r_[0.0, np.cumsum(seg)]; X = X - X[2] + xj                         # planform coordinate: X = xj at the cut line A
        L_c = X[-3] + xj                                                           # pin B at X = L_c
        strip = dict(X=X, C=C, ACR=np.array([s["acr"] for s in secs]), UP=np.array([s["up"] for s in secs]),
                     TP=np.array([s["tp"] for s in secs]), X0=xj, X1=X[-3], hw=HW)
        return dict(kind="long", hubs=[hA, hB], strip=strip, L_c=L_c, key=key, mi=mi, rec=rec, th=th, gen_path="long",
                    centre_dist=float(th * 0.5 * (zA + zB)))
    # short link: one blended frame map along x from pin A (0) to pin B (dist)
    dist = th * 0.5 * (zA + zB + 0.5 * (tA + tB))
    depA = G.contour_field(mi, 0, a, dA, latA) if lowA else None
    depB = G.contour_field(mi, 1, b, dB, latB) if lowB else None
    seat = 10.6; x0, x1 = min(seat, dist / 2 - 0.5), max(dist - seat, dist / 2 + 0.5)
    if fix_short:
        sdf_full = lambda x, y: short_sdf(x, y, HUB_R, HW, dist)
    else:
        def sdf_full(x, y):
            hA_ = np.sqrt(np.maximum(HUB_R ** 2 - x ** 2, 0)); hB_ = np.sqrt(np.maximum(HUB_R ** 2 - (x - dist) ** 2, 0))
            hmax, hmin = np.maximum(hA_, hB_), np.minimum(hA_, hB_); k = 5.0
            hw = hmax + np.where(hmin > 0, np.maximum(0.0, k - (hmax - hmin)) ** 3 / (6 * k * k), 0.0); hw = np.maximum(hw, 0.8)
            return np.abs(y) - hw
    def frame(x):
        """blended section frame at planform x (vectorised): centre of the mid-thickness, lat, up, thickness, w"""
        x = np.atleast_1d(np.asarray(x, float))
        w = np.clip((x - x0) / max(x1 - x0, 1e-3), 0, 1); w = w * w * (3 - 2 * w)
        cA = a * (zA + tA / 2) + x[:, None] * dA; cB = b * (zB + tB / 2) + (dist - x)[:, None] * dB
        up = unit((1 - w)[:, None] * a + w[:, None] * b); c = (1 - w)[:, None] * cA + w[:, None] * cB
        lat = unit((1 - w)[:, None] * latA + w[:, None] * latB); lat = unit(lat - np.einsum("ij,ij->i", lat, up)[:, None] * up)
        tp = (1 - w) * tA + w * tB
        return c, lat, up, tp, w
    hA = Hub(n=a, d=dA, lat=latA, z0=zA, tp=tA, low=lowA, dep=depA, x_end=dist / 2, sdf2=sdf_full, J=JA, mi=mi, end=0)
    hB = Hub(n=b, d=dB, lat=latB, z0=zB, tp=tB, low=lowB, dep=depB, x_end=dist / 2,
             sdf2=lambda x, y, f=sdf_full: f(dist - x, y), J=JB, mi=mi, end=1)
    return dict(kind="short", hubs=[hA, hB], dist=dist, frame=frame, depA=depA, depB=depB, key=key, mi=mi, rec=rec, th=th,
                gen_path=("short" if short_gen else "long-folded"), centre_dist=float(th * 0.5 * (zA + zB)),
                neck_as_built=float(2 * max(0.8, _short_hw_as_built(dist / 2, HUB_R, dist))))


def _short_hw_as_built(x, R, dist):
    hA = math.sqrt(max(R * R - x * x, 0)); hB = math.sqrt(max(R * R - (x - dist) ** 2, 0)); hmax, hmin = max(hA, hB), min(hA, hB)
    k = 5.0; return hmax + (max(0.0, k - (hmax - hmin)) ** 3 / (6 * k * k) if hmin > 0 else 0.0)


def smax_(a, b, k=6.0):
    h = np.maximum(k - np.abs(a - b), 0) / k; return np.maximum(a, b) + h ** 3 * k / 6


def planform_sdf(x, y, R, HW, stub_len=60.0, k=8.0):
    d1 = np.hypot(x, y) - R; d2 = np.maximum(np.abs(y) - HW, np.maximum(x - stub_len, -x)); return smin(d1, d2, k)


def short_sdf(x, y, R, HW, dist, k=8.0):
    d1 = np.hypot(x, y) - R; d2 = np.hypot(x - dist, y) - R; d3 = np.maximum(np.abs(y) - HW, np.maximum(x - dist, -x))
    return smin(smin(d1, d2, k), d3, k)


def base_sdf(x, y, R, HW, xe, k=6.0):
    disc = np.hypot(x, y) - R
    q = np.maximum(x - xe, 0.0)
    strip = np.where(x <= xe, np.maximum(np.abs(y) - HW, -x), np.hypot(q, y) - HW)
    # generator: smooth-max of the half-widths (k = 6) == smooth union of the two regions
    return smin(disc, strip, k)


# ------------------------------------------------------------------------------------------- meshing
def radial_nodes(r_in, R, n1, n2, r_w=9.0):
    """r_in .. r_w uniform (washer zone), r_w .. R uniform"""
    s = np.linspace(0, 1, n2 + 1); g = s                                     # uniform (finer rim grading inverted corner elements)
    return np.r_[np.linspace(r_in, r_w, n1 + 1)[:-1], r_w + (R - r_w) * g]


def ray_extent(sdf2, th, x_end, rmax=60.0):
    c, s = math.cos(th), math.sin(th); lo, hi = 0.0, rmax
    if x_end is not None and c > 1e-9: hi = min(hi, x_end / c)
    if sdf2(np.array([hi * c]), np.array([hi * s]))[0] < 0: return hi
    for _ in range(60):
        m = 0.5 * (lo + hi)
        if sdf2(np.array([m * c]), np.array([m * s]))[0] < 0: lo = m
        else: hi = m
    return lo


def outline_points(sdf2, x_end, xr=(-20, 60), h=0.02):
    """dense polyline points of the free outline sdf2 = 0 (x <= x_end), for edge distances"""
    xs = np.arange(xr[0], xr[1], h)
    if x_end is not None: xs = xs[xs <= x_end + 1e-9]
    hw = halfwidth_from_sdf(sdf2, xs); ok = hw > 0
    P = np.r_[np.c_[xs[ok], hw[ok]], np.c_[xs[ok], -hw[ok]]]
    # close the far ends with a vertical fan (disc back / tab end) so rays there have a boundary too
    return P


def hub_grid(hub, r_in, y_end, n_back=110, n1=6, n2=14, rmax=60.0):
    """O-grid nodes (in-plane x, y) of a hub: rays (n_rays,) x radial (n_r,). Rays in the cut sector end on the cut line
    at y_end; the other rays end on the outline."""
    if hub.x_end is not None:
        th_end = np.arctan2(y_end, hub.x_end)                                   # ascending
        th0, th1 = th_end[-1], th_end[0] + 2 * np.pi
        back = np.linspace(th0, th1, n_back + 2)[1:-1]
        ths = np.r_[th_end, back]
        R = np.array([hub.x_end / math.cos(t) for t in th_end] + [ray_extent(hub.sdf2, t, None, rmax) for t in back])
        # cut-sector rays must not hit the outline first
        for k, t in enumerate(th_end):
            R[k] = min(R[k], ray_extent(hub.sdf2, t, hub.x_end + 1e-6, rmax) + 1e-9) if abs(y_end[k]) < np.max(np.abs(y_end)) - 1e-9 else R[k]
    else:
        ths = np.linspace(0, 2 * np.pi, n_back + 1)[:-1]; R = np.array([ray_extent(hub.sdf2, t, None, rmax) for t in ths])
    rad = np.stack([radial_nodes(r_in, Rk, n1, n2) for Rk in R])               # (n_rays, n_r)
    XY = np.stack([rad * np.cos(ths)[:, None], rad * np.sin(ths)[:, None]], -1)
    if hub.x_end is not None:                                                   # exact cut-line end nodes
        XY[:len(y_end), -1, 0] = hub.x_end; XY[:len(y_end), -1, 1] = y_end
    return XY, ths, rad


def strip_frames(S, hubs, dx, max_slope=0.7):
    """ribbon centre path + section frames between the two cut lines. The generator's ribbon can start well above / below
    the hub plate (it follows the fitted envelope); its loft then makes a near-vertical step at the stub end. Here ribbon
    sections closer to a stub end than (radial jump / max_slope) are dropped so the path ramps smoothly, and every section
    is set perpendicular to the path tangent (no sheared elements). The end sections are the exact plate frames."""
    C, U, A_, T = S["C"], S["UP"], S["ACR"], S["TP"]
    nA, dA = hubs[0].n, hubs[0].d; nB, dB = hubs[1].n, hubs[1].d
    keep = list(range(len(C)))
    rib = list(range(3, len(C) - 3))
    def jump(i, end):
        c0 = C[2] if end == 0 else C[-3]; t0 = T[2] if end == 0 else T[-3]; n_, d_ = (nA, dA) if end == 0 else (nB, dB); v = C[i] - c0
        along = abs(v @ d_)
        if along >= 10.0: return 0.0, along                                   # far enough: the sphere / envelope curvature is fine
        return abs(v @ n_) + 0.5 * abs(T[i] - t0) + (1e9 if along < 2.5 else 0.0), along
    dropA = 0
    while dropA < len(rib):
        r_, a_ = jump(rib[dropA], 0)
        if r_ <= max_slope * max(a_, 1e-6): break
        dropA += 1
    dropB = 0
    while dropB < len(rib) - dropA:
        r_, a_ = jump(rib[-1 - dropB], 1)
        if r_ <= max_slope * max(a_, 1e-6): break
        dropB += 1
    kr = rib[dropA:len(rib) - dropB]
    idx = [2] + kr + [len(C) - 3]                                             # cut line A, kept ribbon sections, cut line B
    Ck = C[idx]; seg = np.linalg.norm(np.diff(Ck, axis=0), axis=1); u = np.r_[0, np.cumsum(seg)]
    u0, u1 = u[0], u[-1]
    # clamped: leaves cut line A along d_A and arrives at cut line B along -d_B (tangent to the flat stubs)
    csC = CubicSpline(u, Ck, bc_type=((1, dA), (1, -dB))); csU = CubicSpline(u, U[idx], bc_type=((1, np.zeros(3)), (1, np.zeros(3))))
    n = max(2, int(math.ceil((u1 - u0) / dx))); us = np.linspace(u0, u1, n + 1)
    Cs = csC(us); Tg = unit(csC(us, 1)); Up = unit(csU(us)); Up = unit(Up - np.einsum("ij,ij->i", Up, Tg)[:, None] * Tg)
    Ac = unit(np.cross(Tg, Up)); sgn = np.sign(np.einsum("ij,ij->i", Ac, A_[2][None]))
    Ac = Ac * np.where(sgn == 0, 1, sgn)[:, None]
    TPs = np.interp(us, u, T[idx])
    Cs[0], Ac[0], Up[0], TPs[0] = C[2], A_[2], U[2], T[2]
    Cs[-1], Ac[-1], Up[-1], TPs[-1] = C[-3], A_[-3], U[-3], T[-3]
    S["dropped"] = (dropA, dropB)
    return Cs, Ac, Up, TPs, us


def build_mesh(desc, nl=4, ny=24, dx=0.65, n_back=110, r_in_low=5.0, r_in_up=6.0, e_edge=1.2):
    """hex mesh of a member. Returns dict X, H, node tags (hub index, rho, layer, ring index), hub list, volume."""
    G = generator(desc["key"]); hubs = desc["hubs"]
    nodes = []; hexes = []; tags = []; htags = []                                               # tags: (hub, rho, layer, ring, x, y)
    base_off = 0
    hw_cut = None
    if desc["kind"] in ("long", "base"): hw_cut = desc["strip"]["hw"]
    elif desc["kind"] == "short": hw_cut = float(halfwidth_from_sdf(hubs[0].sdf2, np.array([desc["dist"] / 2]))[0])
    y_end = np.linspace(-hw_cut, hw_cut, ny + 1) if hw_cut is not None else None

    def edge_dist(hub, x, y):
        """in-plane distance to the free outline and the outward normal there"""
        if not hasattr(hub, "_tree"):
            hub._OP = outline_points(hub.sdf2, hub.x_end); hub._tree = cKDTree(hub._OP)
        db, ii = hub._tree.query(np.c_[x, y]); q = hub._OP[ii]
        nrm = unit(np.c_[x, y] - q + 1e-12 * np.c_[np.ones_like(x), np.zeros_like(x)])
        inside = hub.sdf2(x, y) < 0
        return db, np.where(inside[:, None], -nrm, nrm)

    def zspan(hub, x, y, db):
        """bottom / top of the plate (along n, from the skin face) at local x, y incl. the contoured skin side. The contour
        is faded to 0 over max(1.5 x the edge round, 1.5 x the local depth) from the outline (the generator fades it laterally only, which leaves a
        near-vertical step at the front / back of the disc; this keeps the elements valid and is slightly conservative)"""
        tp = hub.tp
        bot = np.zeros_like(x); top = np.full_like(x, tp)
        if hub.dep is not None:
            dep = np.asarray(hub.dep(x, y), float).reshape(-1)
            ec = min(e_edge, tp / 2 - 0.1)
            wy = np.clip(db / np.maximum(max(ec * 1.5, 0.3), 1.5 * dep), 0, 1); wy = wy * wy * (3 - 2 * wy)   # slope <= 1
            bot = -dep * wy
        return bot, top

    for hi, hub in enumerate(hubs):
        r_in = r_in_low if hub.low else r_in_up
        XY, ths, rad = hub_grid(hub, r_in, y_end, n_back=n_back, n2=16)
        nr, nrr = XY.shape[0], XY.shape[1]
        x, y = XY[..., 0].ravel(), XY[..., 1].ravel()
        db0, _ = edge_dist(hub, x, y)
        bot, top = zspan(hub, x, y, db0)
        P = []
        for l in range(nl + 1):
            z = bot + (top - bot) * l / nl
            P.append(np.c_[x, y, z])
        P = np.stack(P, 1)                                                          # (nr*nrr, nl+1, 3) local (x, y, z)
        idx = base_off + np.arange(P.shape[0] * P.shape[1]).reshape(nr, nrr, nl + 1)
        periodic = True
        I, J, L = np.meshgrid(np.arange(nr), np.arange(nrr - 1), np.arange(nl), indexing="ij")
        I, J, L = I.ravel(), J.ravel(), L.ravel(); I2 = (I + 1) % nr
        if hub.x_end is not None:
            # the cut sector is the first len(y_end) rays: no element between the last cut ray and ... (all rays are
            # consecutive around the circle; the cut line is the outer boundary of the cut-sector rays) -> keep all
            pass
        hx = np.stack([idx[I, J, L], idx[I2, J, L], idx[I2, J + 1, L], idx[I, J + 1, L],
                       idx[I, J, L + 1], idx[I2, J, L + 1], idx[I2, J + 1, L + 1], idx[I, J + 1, L + 1]], 1)
        nodes.append(("hub", hi, P.reshape(-1, 3))); hexes.append(hx); htags.append(np.c_[np.full(len(I), hi), L, J, I])
        rr = np.repeat(rad.ravel(), nl + 1); ll = np.tile(np.arange(nl + 1), nr * nrr); ring = np.repeat(np.tile(np.arange(nrr), nr), nl + 1)
        ray = np.repeat(np.repeat(np.arange(nr), nrr), nl + 1)
        tags.append(np.c_[np.full(len(rr), hi), rr, ll, ring, ray])
        base_off += P.shape[0] * P.shape[1]
    if desc["kind"] in ("long", "base"):
        S = desc["strip"]
        C, ACR, UP, TP, Xs = strip_frames(S, hubs, dx) if "direct" not in S else S["direct"]
        nx = len(Xs) - 1
        P = np.zeros((nx + 1, ny + 1, nl + 1, 3))
        for l in range(nl + 1):
            P[:, :, l] = C[:, None] + y_end[None, :, None] * ACR[:, None] + ((l / nl - 0.5) * TP)[:, None, None] * UP[:, None]
        desc["_strip_frames"] = (Xs, C, ACR, UP, TP)
        idx = base_off + np.arange(P.shape[0] * P.shape[1] * P.shape[2]).reshape(nx + 1, ny + 1, nl + 1)
        I, J, L = np.meshgrid(np.arange(nx), np.arange(ny), np.arange(nl), indexing="ij"); I, J, L = I.ravel(), J.ravel(), L.ravel()
        hx = np.stack([idx[I, J, L], idx[I + 1, J, L], idx[I + 1, J + 1, L], idx[I, J + 1, L],
                       idx[I, J, L + 1], idx[I + 1, J, L + 1], idx[I + 1, J + 1, L + 1], idx[I, J + 1, L + 1]], 1)
        nodes.append(("strip", -1, P.reshape(-1, 3))); hexes.append(hx); htags.append(np.c_[np.full(len(I), -1), L, np.full(len(I), -1), I])
        n_ = P.shape[0] * P.shape[1] * P.shape[2]
        tags.append(np.c_[np.full(n_, -1), np.full(n_, 99.0), np.tile(np.arange(nl + 1), (nx + 1) * (ny + 1)), np.full(n_, -1), np.full(n_, -1)])
        base_off += n_
    # ---- edge rounds (corner squash) and the map to 3D
    Xall = []; X0all = []
    for kind_, hi, P in nodes:
        if kind_ == "hub":
            hub = hubs[hi]; x, y, z = P[:, 0].copy(), P[:, 1].copy(), P[:, 2].copy()
            db, nrm = edge_dist(hub, x, y)
            bot, top = zspan(hub, x, y, db)
            X0all.append(to3d(desc, hub, x, y, z))
            x, y, z = squash(x, y, z, db, nrm, bot, top, hub.tp, e_edge)
            Xall.append(to3d(desc, hub, x, y, z))
        else:
            # strip: lateral edges at |y| = hw; rounds in the section plane
            S = desc["strip"]; Xs, C, ACR, UP, TP = desc["_strip_frames"]
            nx1 = len(Xs); P4 = P.reshape(nx1, ny + 1, nl + 1, 3)
            yy = np.broadcast_to(y_end[None, :, None], (nx1, ny + 1, nl + 1)).astype(float)
            zz = np.broadcast_to(((np.arange(nl + 1) / nl - 0.5))[None, None, :] * TP[:, None, None], (nx1, ny + 1, nl + 1)).astype(float)
            tp = np.broadcast_to(TP[:, None, None], zz.shape)
            ec = np.minimum(e_edge, tp / 2 - 0.1)
            a_ = np.clip(np.abs(yy) - (S["hw"] - ec), 0, None); b_ = np.clip(np.abs(zz) - (tp / 2 - ec), 0, None)
            hyp = np.hypot(a_, b_); sc = np.where(hyp > 1e-12, np.maximum(a_, b_) / np.maximum(hyp, 1e-12), 1.0)
            yy2 = np.sign(yy) * ((S["hw"] - ec) + a_ * sc) * (a_ > 0) + yy * (a_ <= 0)
            zz2 = np.where((a_ > 0) & (b_ > 0), np.sign(zz) * ((tp / 2 - ec) + b_ * sc), zz)
            yy2 = np.where((a_ > 0) & (b_ > 0), yy2, yy)
            P4 = C[:, None, None] + yy2[..., None] * ACR[:, None, None] + zz2[..., None] * UP[:, None, None]
            P0 = C[:, None, None] + yy[..., None] * ACR[:, None, None] + zz[..., None] * UP[:, None, None]
            Xall.append(P4.reshape(-1, 3)); X0all.append(P0.reshape(-1, 3))
    X = np.concatenate(Xall); X0 = np.concatenate(X0all); H = np.concatenate(hexes); T = np.concatenate(tags)
    # merge coincident nodes (cut lines), by the un-rounded positions
    key = np.round(X0 / 1e-4).astype(np.int64)
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.ravel()
    # keep the hub tag for merged nodes (first occurrence comes from the hubs, which are meshed first)
    Xm = X[first]; X0m = X0[first]; Tm = T[first]; Hm = inv[H]
    # drop degenerate hexes (none expected)
    ok = np.array([len(set(h)) == 8 for h in Hm[:50]])
    import fe_core as F
    HT = np.concatenate(htags)
    # orientation per block (a whole block flips together; a mixed sign means a folded / broken mesh -> error)
    off = 0
    for hb in hexes:
        sl = slice(off, off + len(hb)); v = F.hex_volume(Xm, Hm[sl])
        if (v < 0).mean() > 0.5: Hm[sl] = Hm[sl][:, [1, 0, 3, 2, 5, 4, 7, 6]]
        off += len(hb)
    # undo the edge-round squash on the nodes of any element it distorted (corner detJ ratio < 0.25), until none are left
    n_undo = 0
    for _ in range(8):
        q = np.min([F._jac(Xm[Hm], F.DN_CORNER[c])[1] for c in range(8)], axis=0) / F._jac(X0m[Hm], F.DN_C)[1]
        q0 = np.min([F._jac(X0m[Hm], F.DN_CORNER[c])[1] for c in range(8)], axis=0) / F._jac(X0m[Hm], F.DN_C)[1]
        bad = (q < 0.25) & (q < q0 - 1e-9)
        if not bad.any(): break
        nb = np.unique(Hm[bad]); moved = np.linalg.norm(Xm[nb] - X0m[nb], axis=1) > 1e-12
        if not moved.any(): break
        Xm[nb] = X0m[nb]; n_undo += int(moved.sum())
    vol = F.hex_volume(Xm, Hm)
    if (vol <= 0).any(): raise ValueError(f"{int((vol <= 0).sum())} inverted hexes in {desc['key']} member {desc['mi']}")
    dj = np.min([F._jac(Xm[Hm], F.DN_CORNER[c])[1] for c in range(8)], axis=0) / F._jac(Xm[Hm], F.DN_C)[1]
    if (dj <= 0.05).any(): raise ValueError(f"{int((dj <= 0.05).sum())} badly shaped hexes (corner detJ ratio min {dj.min():.3f}) in {desc['key']} member {desc['mi']}")
    return dict(X=Xm, H=Hm, tags=Tm, htags=HT, hubs=hubs, vol=float(vol.sum()), nl=nl, desc=desc, qmin=float(dj.min()), n_unrounded=n_undo)


def mesh_member(key, mi, **kw):
    """describe + mesh; long links whose ribbon must ramp steeply between the hub planes are retried with shorter flat
    stubs (cut line at 15 / 14 mm from the pin instead of the generator's 20 mm)"""
    last = None
    for xc in (None, 15.0, 14.0):
        d = describe_member(key, mi, x_cut=xc)
        try:
            m = build_mesh(d, **kw); d["x_cut"] = d["hubs"][0].x_end; return d, m
        except ValueError as e:
            last = e
            if d["kind"] != "long": raise
    raise last


def squash(x, y, z, db, nrm, bot, top, tp, e_edge):
    """G2 edge-round approximation: map the corner squares (within ec of the outline and of the top/bottom face) onto
    quarter discs of radius ec"""
    T_loc = top - bot; ec = np.minimum(e_edge, np.maximum(T_loc / 2 - 0.1, 0.2))
    zc = 0.5 * (top + bot)
    a_ = np.clip(ec - db, 0, None); b_ = np.clip(np.abs(z - zc) - (T_loc / 2 - ec), 0, None)
    m = (a_ > 0) & (b_ > 0)
    hyp = np.hypot(a_, b_); sc = np.where(m, np.maximum(a_, b_) / np.maximum(hyp, 1e-12), 1.0)
    da = a_ * (1 - sc); dbz = b_ * (1 - sc)
    x2 = x - np.where(m, da, 0) * nrm[:, 0]; y2 = y - np.where(m, da, 0) * nrm[:, 1]
    z2 = z - np.where(m, dbz, 0) * np.sign(z - zc)
    return x2, y2, z2


def to3d(desc, hub, x, y, z):
    """local hub coords (x along d from the pin, y lateral, z from the skin face along n) -> member frame 3D"""
    if desc["kind"] != "short":
        return hub.n * (hub.z0 + z)[:, None] + x[:, None] * hub.d + y[:, None] * hub.lat
    dist = desc["dist"]; X = x if hub.end == 0 else dist - x
    c, lat, up, tp, w = desc["frame"](X)
    # z measured from the hub's own skin face; in the blend zone use the blended section (centre c, thickness tp)
    zl = z - hub.tp / 2                                                          # relative to the hub plate mid-plane
    # scale the through-thickness coordinate with the blended thickness (keeps the contour depth unscaled below 0)
    zrel = np.where(z >= 0, (z / hub.tp - 0.5) * tp, -0.5 * tp + z)
    ysign = 1.0
    return c + (y * ysign)[:, None] * lat + zrel[:, None] * up


# ------------------------------------------------------------------------------------------- quick check
if __name__ == "__main__":
    import json
    for key in ("4c_best", "5r_thin", "4r_thin"):
        G = generator(key)
        for mi in range(0, G.N):
            d, msh = mesh_member(key, mi)
            pin = 0.0
            for h in d["hubs"]:
                if h.low: pin += math.pi * 25 * 7.07 - math.pi * 1.65 ** 2 * 7.0
            extra = f"  generator path {d.get('gen_path', 'base')}, centre dist {d.get('centre_dist', 0):.1f}" + ("" if d["kind"] != "short" else f", as-built neck {d['neck_as_built']:.1f} mm")
            print(f"{key} member {mi} {d['kind']:5s}: q {msh['qmin']:.2f} unrounded {msh['n_unrounded']} {len(msh['X'])} nodes {len(msh['H'])} hex, mesh vol {msh['vol']:.0f} mm3 (+pin {pin:.0f})"
                  f" roles {[('low' if h.low else 'up') + f' J{h.J} t{h.tp}' for h in d['hubs']]}{extra}", flush=True)
