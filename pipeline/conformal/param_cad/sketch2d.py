"""Planar sketches of tangent lines and arcs (the side view of a bent bar), fitted to a clearance field.

A chain starts at a pose (x, y, heading psi) and is a list of segments (kappa, length): kappa = 0 is a line, otherwise an
arc of radius 1/|kappa| turning left for kappa > 0. Tangency is built in, so the sketch is G1 by construction and every
radius is a set value (fit_chain snaps them to round numbers before the lengths are solved exactly).

fit_chain finds the arcs between two fixed end poses (seat lines of two joints) that keep the bar's skin-side face at or
above a clearance field and hug it, with the climb angle relative to the GH sphere limited (CAD standard rule 4).
"""
import math
import numpy as np
from scipy.optimize import minimize, least_squares


def advance(x, y, psi, k, l):
    if abs(k) < 1e-9: return x + l * math.cos(psi), y + l * math.sin(psi), psi
    return x + (math.sin(psi + k * l) - math.sin(psi)) / k, y - (math.cos(psi + k * l) - math.cos(psi)) / k, psi + k * l


def end_pose(start, segs):
    x, y, p = start
    for k, l in segs: x, y, p = advance(x, y, p, k, l)
    return np.array([x, y, p])


def sample(start, segs, m=30):
    """points (N,2), headings (N,), segment index (N,) along the chain; m samples per segment (incl. its start)"""
    x, y, p = start; P, H, S = [], [], []
    for i, (k, l) in enumerate(segs):
        for u in np.linspace(0, l, m, endpoint=False):
            a = advance(x, y, p, k, u); P.append(a[:2]); H.append(a[2]); S.append(i)
        x, y, p = advance(x, y, p, k, l)
    P.append((x, y)); H.append(p); S.append(len(segs) - 1)
    return np.array(P), np.array(H), np.array(S)


def normals(H):
    """right-hand normals of headings H (for a chain running counter-clockwise about the origin: pointing outward)"""
    return np.stack([np.sin(H), -np.cos(H)], 1)


def wrap(a): return (a + math.pi) % (2 * math.pi) - math.pi


def snap_step(a, scale=1.0):
    return scale * (1.0 if a <= 40 else 2.5 if a <= 100 else 5.0 if a <= 250 else 10.0)


def snap_radius(R, up=None, scale=1.0):
    """round radius: 1 mm steps to 40, 2.5 to 100, 5 to 250, then 10 (x scale); up = None nearest, False floor, True ceil"""
    a = abs(R); s = snap_step(a, scale)
    q = round(a / s) if up is None else (math.ceil(a / s) if up else math.floor(a / s))
    return math.copysign(max(s, q * s), R)


def fit_chain(start, end, clear, t, n_arcs=3, climb_max=35.0, r_min=12.0, bend=40.0, m=30, seeds=24, rng=0, verbose=False, margin=0.4, l_min=6.0,
              snap_scale=1.0):
    """arcs between two poses. clear(P (N,2) skin-side points) -> clearance (mm, >= 0 required); t = bar thickness.
    Objective: mean clearance of the skin-side face + bend * sum(kappa^2 l) (fairness). Returns dict(segs, ...).
    snap_scale scales the round-radius steps (0.5: half-mm steps to R40, ...)."""
    start = np.asarray(start, float); end = np.asarray(end, float); R = np.random.default_rng(rng)
    n = n_arcs; chord = float(np.linalg.norm(end[:2] - start[:2])); kmax = 1.0 / r_min

    def unpack(z): return list(zip(z[:n], z[n:]))
    def under(z):
        P, H, _ = sample(start, unpack(z), m); return P - 0.5 * t * normals(H), P, H
    def climb(P, H):
        return np.degrees(np.abs(wrap(H - np.arctan2(P[:, 1], P[:, 0]) - math.pi / 2)))
    def f(z):
        U, P, H = under(z); c = clear(U)
        return float(np.mean(c)) + bend * float(np.sum(np.asarray(z[:n]) ** 2 * np.asarray(z[n:])))
    def eq(z):
        e = end_pose(start, unpack(z)) - end; e[2] = wrap(e[2]) * chord / 2; return e
    def ineq(z, mg=margin, cm=climb_max - 0.5):
        U, P, H = under(z); return np.concatenate([clear(U) - mg, cm - climb(P, H)])
    best = None
    for s in range(seeds):
        k0 = R.uniform(-0.6, 1.0, n) * (2.0 / chord)
        l0 = np.full(n, max(chord / n, l_min + 1))
        r = least_squares(lambda l: eq(np.concatenate([k0, l])), l0, bounds=(l_min, 4 * chord))
        z0 = np.concatenate([k0, r.x])
        res = minimize(f, z0, method="SLSQP", constraints=[dict(type="eq", fun=eq), dict(type="ineq", fun=ineq)],
                       bounds=[(-kmax, kmax)] * n + [(l_min, 4 * chord)] * n, options=dict(maxiter=300, ftol=1e-6))
        z = res.x; viol = max(float(np.abs(eq(z)).max()), float(-min(0.0, ineq(z).min())))
        if verbose: print(f"seed {s}: f {res.fun:.2f} viol {viol:.3f} R {np.round(1 / np.where(np.abs(z[:n]) > 1e-9, z[:n], 1e-9), 1)}")
        if viol < 0.05 and (best is None or res.fun < best[0]): best = (res.fun, z)
    if best is None: raise RuntimeError("fit_chain: no feasible chain")
    z = best[1]
    # snap the radii to round numbers, then solve the lengths exactly for the end pose; keep the best feasible variant
    cand = []
    import itertools
    R0 = [1.0 / z[i] if abs(z[i]) > 1e-6 else 1e6 for i in range(n)]
    opts = []
    for Rr in R0:
        if abs(Rr) > 2000: opts.append([0.0]); continue
        base = snap_radius(Rr, scale=snap_scale); a = abs(base); s_ = snap_step(a, snap_scale)
        opts.append([1.0 / math.copysign(a + j * s_, Rr) for j in (-2, -1, 0, 1, 2) if a + j * s_ >= max(s_, r_min)])
    for ks in itertools.product(*opts):
        ks = np.array(ks)
        r = least_squares(lambda l: eq(np.concatenate([ks, l])), np.maximum(z[n:], l_min), bounds=(l_min - 0.5, 4 * chord))
        zz = np.concatenate([ks, r.x]); e = float(np.abs(eq(zz)).max()); g = float(ineq(zz, 0.0, climb_max).min())
        cand.append((e < 1e-6 and g > -0.02, f(zz), zz, e, g))
    ok = [c for c in cand if c[0]]
    if not ok: raise RuntimeError(f"fit_chain: snapped radii infeasible (best before snap f {best[0]:.2f})")
    _, fz, zz, e, g = min(ok, key=lambda c: c[1])
    U, P, H = under(zz); c = clear(U)
    return dict(segs=unpack(zz), objective=fz, end_err=e, min_clear=float(c.min()), mean_clear=float(c.mean()),
                max_clear=float(c.max()), max_climb=float(climb(P, H).max()), radii=[(1 / k if k else None) for k in zz[:n]])


def offset_outline(start, segs, t):
    """closed outline of the bar: outer offset (+t/2, right-hand normal side) start->end, end cap, inner offset back,
    start cap. Returns a list of ('line', p0, p1) / ('arc', p0, pm, p1) in 2D."""
    def seg_pts(o):
        out = []; x, y, p = start
        for k, l in segs:
            a = np.array([x, y]); nb = np.array([math.sin(p), -math.cos(p)])
            xm, ym, pm = advance(x, y, p, k, l / 2); x1, y1, p1 = advance(x, y, p, k, l)
            q0 = a + o * nb; qm = np.array([xm, ym]) + o * np.array([math.sin(pm), -math.cos(pm)])
            q1 = np.array([x1, y1]) + o * np.array([math.sin(p1), -math.cos(p1)])
            out.append(("line", q0, q1) if abs(k) < 1e-9 else ("arc", q0, qm, q1)); x, y, p = x1, y1, p1
        return out
    outer = seg_pts(+t / 2); inner = seg_pts(-t / 2)
    rev = [("line", s[2], s[1]) if s[0] == "line" else ("arc", s[3], s[2], s[1]) for s in reversed(inner)]
    return outer + [("line", outer[-1][-1], rev[0][1])] + rev + [("line", rev[-1][-1], outer[0][1])]


def hug_chain(start, end, clear, t, outside, n=6, climb_max=60.0, r_min=3.0, target=0.3, margin=0.1, seeds=10, m=24, rng=0,
              tgt_curve=None, snap=0.5, lmin=0.8):
    """a chain of n tangent lines / arcs between two fixed poses that HUGS a clearance field (a 5-axis machined bar that
    follows the strap it replaces, user_style_pinknee.py): skin-side face >= margin above it (margin may be a function of
    the skin-side points, e.g. relaxed on a hub's own seat level), climb <= climb_max, every centre-line radius >= r_min;
    objective = mean clearance + 20 x mean((clearance - target)+^2 where outside(U)) + 0.5 x sum(kappa^2 l). Seeds: least
    squares of the centre line to tgt_curve (radial error, mm) under the end pose; then SLSQP; radii snapped to `snap` mm
    (to R40, then 2.5 / 5 / 10) with the lengths re-solved exactly for the end pose. Returns dict(segs, ...)."""
    start = np.asarray(start, float); end = np.asarray(end, float); R = np.random.default_rng(rng)
    chord = float(np.linalg.norm(end[:2] - start[:2])); kmax = 1.0 / r_min
    unpack = lambda z: list(zip(z[:n], z[n:2 * n]))
    mgf = (lambda U: margin(U)) if callable(margin) else (lambda U: np.full(len(U), float(margin)))
    def under(z):
        P, H, _ = sample(start, unpack(z), m); return P - 0.5 * t * normals(H), P, H
    climb = lambda P, H: np.degrees(np.abs(wrap(H - np.arctan2(P[:, 1], P[:, 0]) - math.pi / 2)))
    def eq(z):
        e = end_pose(start, unpack(z)) - end; e[2] = wrap(e[2]) * chord / 2; return e
    def f(z):
        U, P, H = under(z); c = clear(U); ex_ = np.maximum(c - target, 0.0) * outside(U)
        return float(np.mean(c)) + 20.0 * float(np.mean(ex_ ** 2)) + 0.5 * float(np.sum(z[:n] ** 2 * z[n:2 * n]))
    def ineq(z):
        U, P, H = under(z); return np.concatenate([clear(U) - mgf(U), climb_max - 0.5 - climb(P, H)])
    best = None
    for s in range(seeds):
        k0 = R.uniform(-1, 1, n) * min(kmax, 4.0 / chord); l0 = np.full(n, chord / n) * R.uniform(0.7, 1.3, n)
        def res(z2):
            P, H, _ = sample(start, unpack(z2), m); return np.r_[10 * eq(z2), tgt_curve(P) / math.sqrt(len(P))]
        r = least_squares(res, np.r_[k0, l0], bounds=(np.r_[[-kmax] * n, [lmin] * n], np.r_[[kmax] * n, [3 * chord] * n]))
        try:
            o = minimize(f, r.x, method="SLSQP", constraints=[dict(type="eq", fun=eq), dict(type="ineq", fun=ineq)],
                         bounds=[(-kmax, kmax)] * n + [(lmin, 3 * chord)] * n, options=dict(maxiter=400, ftol=1e-7))
        except ValueError: continue
        z = o.x; viol = max(float(np.abs(eq(z)).max()), float(-min(0.0, ineq(z).min())))
        if viol < 0.03 and (best is None or f(z) < best[0]): best = (f(z), z)
    if best is None: raise RuntimeError("hug_chain: no feasible chain")
    z = best[1].copy()
    def snapk(k):
        if abs(k) < 1.0 / 2000: return 0.0
        Rr = 1.0 / abs(k); st = snap if Rr <= 40 else 2.5 if Rr <= 100 else 5.0 if Rr <= 250 else 10.0
        return math.copysign(1.0 / max(round(Rr / st) * st, r_min), k)
    def fin(ks):
        r = least_squares(lambda l: eq(np.r_[ks, l]), z[n:2 * n], bounds=(lmin - 0.2, 3 * chord))
        zz = np.r_[ks, r.x]; U, P, H = under(zz)
        return zz, float(np.abs(eq(zz)).max()), float((clear(U) - mgf(U)).min()), float(climb(P, H).max())
    ok = lambda e, g, cl: e < 1e-6 and g > -0.1 and cl <= climb_max + 0.01
    ks = np.array([snapk(k) for k in z[:n]]); zz, e, g, cl = fin(ks); snapped = ok(e, g, cl)
    if not snapped:
        for i in range(n):                                                     # nudge one radius at a time
            for d in (+1, -1, +2, -2):
                if ks[i] == 0: continue
                k2 = ks.copy(); k2[i] = math.copysign(1 / max(1 / abs(k2[i]) + d * snap, r_min), k2[i])
                z2, e2, g2, cl2 = fin(k2)
                if ok(e2, g2, cl2): zz, e, g, cl, ks, snapped = z2, e2, g2, cl2, k2, True; break
            if snapped: break
    if not snapped: zz = z; e = float(np.abs(eq(z)).max())                     # the unsnapped optimum (radii to 0.01 mm)
    U, P, H = under(zz); c = clear(U); o = outside(U)
    segs = [(float(k), float(l)) for k, l in unpack(zz)]
    return dict(segs=segs, end_err=e, min_clear=float(c.min()), mean_clear=float(c.mean()), max_clear=float(c.max()),
                max_clear_outside=float(c[o].max()) if o.any() else None, max_climb=float(climb(P, H).max()),
                radii=[(1 / k if k else None) for k, _ in segs], objective=float(best[0]), snapped=snapped)
