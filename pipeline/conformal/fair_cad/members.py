"""Shoulder members of a band design as fair G2 sheet bodies (fair CAD pipeline).

Every member (scapula base, links) is ONE sheet: skin side + outer side over one closed planform, rounded all round.
  - hub zones are exact planes square to their joint axis: the lower member of a joint carries the flat washer seat on
    top (skin side contoured to the skin), the upper member a flat underside and flat cap seat (5.05 apart)
  - away from the hubs the skin side hugs the dense skin envelope (every followed frame, 2 mm skin clearance + margin,
    smoothed into a fair surface that never dips below it) and the outer side is a constant 4.0 mm above it
  - the outer member of every joint clears the inner member's swept outer side (all followed frames) by CLEAR_MM
  - hub -> ribbon transitions are smootherstep blends over an adaptive length (<= 35 deg ramps)
  - short links whose hubs nearly touch get a stadium (hull) planform instead of a pinched waist
Stack v3.1 (washers recessed, hairline seams, screw hidden on the skin side) is set by stack_levels().
"""
import math
import numpy as np
from scipy.interpolate import RectBivariateSpline
from scipy.ndimage import gaussian_filter, distance_transform_edt
import sheet as SH

HUB_R, HW, T_LINK, T_LO, T_SEAT, T_BOT = 11.5, 7.0, 5.5, 3.0, 4.05, 6.5            # FEA-sized (thin_study): 5.5 link bodies, 3.0 plate; v4 Ø23 hubs
RECESS, PROUD, FLOAT, CAP_CROWN, T_WASH = 0.35, 0.15, 0.02, 2.6, 0.5                 # v3.2: 0.5 mm washers recessed 0.35
MARGIN, CLEAR_MM, GRID = 0.5, 0.6, 0.5
RAMP_MM = 8.0
RAMP_DEG = float(__import__("os").environ.get("RAMP_DEG", 55.0))
LIFT_CAP = float(__import__("os").environ.get("LIFT_CAP", 15.0))
D2R = math.pi / 180
unit = SH.unit
FAIR = __import__("os").environ.get("FAIR", "1") == "1"                               # fair surfaces (stiff shrink-wrap) instead of local lifts/ramps
FAIR_LAM = float(__import__("os").environ.get("FAIR_LAM", 300.0)); FAIR_BLEND = 4.0
FIELD_MODE = __import__("os").environ.get("FIELD_MODE", "swept")                    # "swept": arms = swept constant-section bands (designed look); "fair": 2D fair fields
RAMP_TOP = 35.0                                                                       # max ramp out of a hub plane (deg)
L_FLAT = float(__import__("os").environ.get("L_FLAT", 0.0))                          # hub planes continue flat this far along the arm (stacked plates leave the joint parallel)   # bending weight; G2 blend into the hub planes (mm)
def _fair1d(m, end0, end1, dt, lam, a0=0.02, iters=20):
    """1-D stiff shrink-wrap: h >= m (where finite), h clamped to end0 = (h[0], h[1]) and end1 = (h[-1], h[-2]) (value + slope)"""
    from scipy.sparse import diags
    from scipy.sparse.linalg import spsolve
    n = len(m); D2 = diags([np.ones(n - 1), -2 * np.ones(n), np.ones(n - 1)], [-1, 0, 1]).tolil(); D2[0, :] = 0; D2[-1, :] = 0; D2 = D2.tocsr() / dt ** 2
    B = lam * (D2.T @ D2); ok = np.isfinite(m); t = np.where(ok, m, 0.0); w = np.where(ok, a0, 0.0)
    cl = np.zeros(n, bool); cl[[0, 1, -1, -2]] = True; t[0], t[1] = end0; t[-1], t[-2] = end1; w[cl] = 1e6; act = np.zeros(n, bool); h = t
    for _ in range(iters):
        W = w.copy(); tt = t.copy(); k = act & ~cl; W[k] = 1e6; tt[k] = m[k] + 0.02
        h = spsolve((B + diags(W)).tocsc(), W * tt); v = ok & ~cl & (h < m - 0.005)
        if not v.any(): break
        act |= v
    return h
def _bilap(nx, ny, h):
    from scipy.sparse import diags, kron, identity
    def d2(n):
        D = diags([np.ones(n - 1), -2 * np.ones(n), np.ones(n - 1)], [-1, 0, 1]).tolil(); D[0, 0] = D[-1, -1] = -1; return D.tocsr() / h ** 2
    Lp = kron(d2(nx), identity(ny)) + kron(identity(nx), d2(ny)); return (Lp.T @ Lp).tocsr()
def fair_field(target, lb, clamp, inside, lam, a0=0.02, h=GRID, iters=12, ub=None):
    """stiffest smooth field (bi-Laplacian energy) equal to target on clamp, >= lb (and <= ub) on inside, attracted to target"""
    from scipy.sparse import diags
    from scipy.sparse.linalg import spsolve
    nx, ny = target.shape; B = lam * _bilap(nx, ny, h)
    t = np.nan_to_num(target.ravel(), nan=0.0); w = np.where(inside, a0, 0.0).ravel(); cl = clamp.ravel(); w[cl] = 1e5
    lbv = lb.ravel(); okb = np.isfinite(lbv); ubv = (np.full_like(lbv, np.inf) if ub is None else ub.ravel()); oku = np.isfinite(ubv)
    act = np.zeros_like(cl); acu = np.zeros_like(cl); u = t
    for _ in range(iters):
        W = w.copy(); tt = t.copy(); m = act & ~cl; W[m] = 1e5; tt[m] = lbv[m] + 0.02; m2 = acu & ~cl & ~act; W[m2] = 1e5; tt[m2] = ubv[m2] - 0.02
        u = spsolve((B + diags(W)).tocsc(), W * tt)
        viol = inside.ravel() & ~cl & okb & (u < np.where(okb, lbv, 0) - 0.005)
        vio2 = inside.ravel() & ~cl & oku & (u > np.where(oku, ubv, 0) + 0.005)
        if not viol.any() and not vio2.any(): break
        act |= viol; acu |= vio2
    return u.reshape(nx, ny)

def stack_levels(F, t_lo=T_LO):
    """v4 encoder stack (joint_v4.py) along the joint axis from the lower member's skin-side face F"""
    import joint_v4 as J4
    lv = J4.levels(F)
    if t_lo != J4.T_LO:                                                                  # arm-end lower member (thicker plate)
        d = t_lo - J4.T_LO; lv = {k: (v + d if k != "F" else v) for k, v in lv.items()}
    lv["pin_top"] = lv["R1"]; return lv

def smootherstep(t): t = np.clip(t, 0.0, 1.0); return t * t * t * (t * (6 * t - 15) + 10)

def smooth_upper(F, valid, sigma_px, iters=60):
    """fair field >= F wherever valid (Gaussian of the running max; invalid pixels take their nearest valid value)"""
    if not valid.any(): return np.full_like(F, np.nan)
    idx = distance_transform_edt(~valid, return_distances=False, return_indices=True)
    F = F[tuple(idx)]; s = gaussian_filter(F, sigma_px)
    for _ in range(iters * 2):                                                           # gentle: no overshoot past the data
        v = F - s
        if v.max() <= 1e-3: break
        s = s + gaussian_filter(np.maximum(v, 0.0), sigma_px)
    return s + max(0.0, float((F - s).max()))

class Member:
    """one sheet member in its own (viewer) frame. hubs: list of dicts(axis, role 'lower'|'upper', lv=stack levels, joint)"""
    def __init__(self, name, group, hubs, theta=None, strip_dir=None, strip_len=None, R0=None, flat=False):
        self.name, self.group, self.hubs = name, group, hubs; self.theta = theta; self.flat = flat; self.lift_cap = LIFT_CAP; self.disc_r = HUB_R
        axes = [h["axis"] for h in hubs]
        if strip_dir is not None:                                                         # base: hub + mount arm
            self.c0 = unit(axes[0] * 1.0 + strip_dir * (max(strip_len, 0) / 2 + HUB_R) / max(R0, 1.0)) if strip_len > 0 else unit(axes[0]); self.e1 = strip_dir
        else:
            self.c0 = unit(axes[0] + axes[1]); self.e1 = unit(axes[1] - axes[0])
        self.R0 = R0 if R0 else float(np.mean([h["lv"]["S"] for h in hubs]))
        self.chart = SH.Chart(self.c0, self.e1, self.R0)
        self.strip_dir, self.strip_len = strip_dir, strip_len
        self.extra = []                                                                    # extra min-radius constraints (grid)

    # ---- planform (chart mm, approx. arc mm at R0)
    def _hub_xy(self, h): return self.chart.xy(h["axis"][None])[0]
    def sdf2(self, x, y):
        x = np.asarray(x, float); y = np.asarray(y, float); hubs = self.hubs; ds = []
        for h in hubs:
            cx, cy = self._hub_xy(h); rr = HUB_R * self.R0 / h["lv"]["S"]; ds.append(np.hypot(x - cx, y - cy) - rr)
        if self.strip_dir is not None and self.strip_len <= 0:                             # base anchored from above: a larger disc
            return ds[0] - (self.disc_r - HUB_R) * self.R0 / hubs[0]["lv"]["S"]
        if self.strip_dir is not None:                                                     # base: disc + arm (stadium end)
            cx, cy = self._hub_xy(hubs[0]); L = self.strip_len + HUB_R; ex, ey = self.chart.xy(unit(hubs[0]["axis"] + self.strip_dir * L / self.R0)[None])[0] - (cx, cy)
            n = math.hypot(ex, ey); ux, uy = ex / n, ey / n; t = np.clip((x - cx) * ux + (y - cy) * uy, 0, n)
            arm = np.hypot(x - (cx + t * ux), y - (cy + t * uy)) - HW
            return _smin(ds[0], arm, 8.0)
        (ax, ay), (bx, by) = self._hub_xy(hubs[0]), self._hub_xy(hubs[1]); L = math.hypot(bx - ax, by - ay)
        rr = HUB_R * self.R0 / np.mean([h["lv"]["S"] for h in hubs])
        ux, uy = (bx - ax) / L, (by - ay) / L; t = np.clip((x - ax) * ux + (y - ay) * uy, 0, L)
        seg = np.hypot(x - (ax + t * ux), y - (ay + t * uy))
        if L < 2 * HUB_R + 12.0: return seg - rr                                           # stadium (hull): no pinched waist
        strip = seg - HW
        return _smin(_smin(ds[0], ds[1], 0.1), strip, 8.0)
    def extent(self, pad=4.0):
        cs = [self._hub_xy(h) for h in self.hubs]
        if self.strip_dir is not None and self.strip_len > 0:
            cs.append(self.chart.xy(unit(self.hubs[0]["axis"] + self.strip_dir * (self.strip_len + HUB_R) / self.R0)[None])[0])
        cs = np.array(cs); r = max(HUB_R, self.disc_r) * 1.3 + pad
        return (cs[:, 0].min() - r, cs[:, 0].max() + r, cs[:, 1].min() - r, cs[:, 1].max() + r)

    # ---- fields on the chart grid
    def grid(self):
        x0, x1, y0, y1 = self.extent(); self.xs = np.arange(x0, x1 + GRID, GRID); self.ys = np.arange(y0, y1 + GRID, GRID)
        self.X, self.Y = np.meshgrid(self.xs, self.ys, indexing="ij"); self.D = self.chart.dirs(self.X, self.Y)
        self.inside = self.sdf2(self.X, self.Y) <= 2.0
        return self.D

    def fields(self, env, sigma_mm=4.0, baseline=None):
        """env: min metal radius over followed frames per grid direction (skin + 2 mm), nan where no skin;
        baseline: the band design's fitted ribbon underside (grid), kept as a floor"""
        D = self.D; ok = np.isfinite(env) & (env > 20)
        need = np.where(ok, env + MARGIN, -np.inf)
        if baseline is not None:                                                            # BASE_CAP=0: the old uncapped floor (reproduction)
            bl = np.where(np.isfinite(baseline), baseline, -np.inf)
            need = np.maximum(need, bl if __import__("os").environ.get("BASE_CAP", "1") == "0" else np.minimum(bl, self.ramp_cap()))
        for c in self.extra: need = np.maximum(need, np.where(np.isfinite(c), c, -np.inf))
        valid = np.isfinite(need); self.need = need
        rib = smooth_upper(np.where(valid, need, 0.0), valid, sigma_mm / GRID)
        bot = np.zeros_like(rib); top = np.zeros_like(rib); wsum = np.zeros_like(rib)
        self.hub_report = []
        for h in self.hubs:
            a = h["axis"]; c = np.clip(D @ a, 1e-3, 1); lv = h["lv"]
            r_in = lv["S"] * np.sqrt(1 - c * c) / c                                        # in-plane radius at the hub plane
            if h["role"] == "lower":
                hb_top = lv["S"] / c; face = (lv["S"] - 2.85) / c; deep = (lv["S"] - T_BOT) / c          # plate 2.85..6.5 thick, skin side contoured within that
                hb_bot = np.minimum(np.maximum(smooth_upper(np.where(valid, need, 0.0), valid, 3.0 / GRID), deep), face)
            else:
                hb_bot = lv["U0"] / c; hb_top = lv["U1"] / c
            dz = np.abs(hb_bot - rib)[(r_in > HUB_R + 0.5) & (r_in < HUB_R + 10) & self.inside]
            Lt = float(np.clip((np.percentile(dz, 90) if len(dz) else 0.0) / math.tan(35 * D2R), 8.0, 25.0))
            w = 1.0 - smootherstep((r_in - h.get("flat_r", HUB_R + 0.5)) / Lt) if not self.flat else np.ones_like(r_in); h["Lt"] = Lt
            bot += w * hb_bot; top += w * hb_top; wsum += w; h["_hb"] = (np.broadcast_to(hb_bot, bot.shape).copy(), np.broadcast_to(hb_top, bot.shape).copy())
            core = (r_in <= HUB_R) & valid
            if core.any(): self.hub_report.append((h["joint"], h["role"], float((hb_bot - need)[core].min())))
        over = np.maximum(wsum, 1.0); bot /= over; top /= over; wr = 1.0 - np.minimum(wsum, 1.0)
        bot += wr * rib; top += wr * (rib + T_LINK)
        # anything still under the need (transitions): lift both sides smoothly, outside the hub cores
        ramp = np.ones_like(bot)                                                            # lifts fade G2-smoothly into every hub core
        for h in self.hubs:
            c = np.clip(D @ h["axis"], 1e-3, 1); r_ = h["lv"]["S"] * np.sqrt(1 - c * c) / c
            ramp = np.minimum(ramp, smootherstep((r_ - h.get("flat_r", HUB_R + 0.5)) / RAMP_MM))
        hubcore = ramp <= 0.0
        v = np.where(valid & ~hubcore, need - bot, 0.0)
        if v.max() > 0:
            lift = smooth_upper(np.maximum(v, 0) / np.maximum(ramp, 0.05), np.ones_like(v, bool), 2.5 / GRID)
            lift = np.minimum(lift, 40.0) * ramp; bot += lift; top += lift
        if FAIR and not self.flat: bot, top = (self._swept if FIELD_MODE == "swept" and len(self.hubs) == 2 else self._fair)(bot, top, need, valid)
        self.bot, self.top = bot, top
        cap = np.zeros_like(top)                                                            # dome caps riding on this member's upper hubs
        for h in self.hubs:
            if h["role"] != "upper": continue
            c = np.clip(D @ h["axis"], 1e-3, 1); lv = h["lv"]; r_in = lv["U1"] * np.sqrt(1 - c * c) / c
            crown = (lv["top"] + 0.3) / c; rim = lv["U1"] / c
            cap = np.maximum(cap, np.where(r_in <= 11.3, rim + (crown - rim) * np.sqrt(np.clip(1 - (r_in / 11.3) ** 2, 0, 1)) - top, 0.0))
        self.top_hw = top + np.maximum(cap, 0.0)
        self.fh = RectBivariateSpline(self.xs, self.ys, self.top_hw, kx=1, ky=1, s=0)
        self.fb = RectBivariateSpline(self.xs, self.ys, bot, kx=3, ky=3, s=0); self.ft = RectBivariateSpline(self.xs, self.ys, top, kx=3, ky=3, s=0)
        ins = self.sdf2(self.X, self.Y) <= 0
        self.gap_min = float(np.nanmin(np.where(valid & ins, bot - need, np.nan))) if (valid & ins).any() else float("nan")
        self.t_min = float((top - bot)[ins].min())
        return self

    def ramp_cap(self):
        """highest the band design's fitted ribbon may hold the skin side: out of every hub's skin-side plane at most
        RAMP_DEG (the steepest lift the sheet can take). The evaluator ramp-limits a ribbon only from one hub; where the
        two hubs of a link sit at very different heights (r13 n3 link 2: J2 plane 61 mm, JN plane 119 mm from GH) its
        ribbon started 29 mm above J2's plane at J2's rim -> an 85 deg wall the sheet could not be built on"""
        cap = np.full(self.D.shape[:-1], np.inf); k = math.tan(RAMP_DEG * D2R)
        for h in self.hubs:
            c = np.clip(self.D @ h["axis"], 1e-3, 1); lv = h["lv"]; r_in = lv["S"] * np.sqrt(1 - c * c) / c
            plane = (lv["U0"] if h["role"] == "upper" else lv["S"] - 2.85) / c
            cap = np.minimum(cap, plane + k * np.maximum(r_in - h.get("flat_r", HUB_R + 0.5), 0.0))
        return cap

    def _fair(self, bot, top, need, valid):
        """replace ribbon + transitions + lifts by fair fields: the skin side is the stiffest smooth surface that stays on
        or above the need (skin envelope, stacking floors) and is clamped to the exact hub planes in the hub cores; the
        thickness is a fair field (T_LINK on the ribbons, the stack heights in the cores); G2 smootherstep into the planes"""
        D = self.D; cores = np.zeros(bot.shape, bool); rmin = np.full(bot.shape, np.inf); hb_b = bot.copy(); hb_t = top.copy()
        near = np.full(bot.shape, np.inf)
        for h in self.hubs:
            c = np.clip(D @ h["axis"], 1e-3, 1); r_ = h["lv"]["S"] * np.sqrt(1 - c * c) / c; fr = h.get("flat_r", HUB_R + 0.5) + L_FLAT; d_ = r_ - fr
            cores |= d_ <= 0; closer = d_ < near; near = np.where(closer, d_, near)
            if "_hb" in h: hb_b = np.where(closer, h["_hb"][0], hb_b); hb_t = np.where(closer, h["_hb"][1], hb_t)
        ins = self.inside; lb = np.where(valid, need, -np.inf)
        bf = fair_field(np.where(cores, bot, np.where(valid, need, bot)), lb, cores, ins, FAIR_LAM)
        # top: T_LINK above the skin side, but near a LOWER hub it stays under the seat plane + 35 deg (the upper link leaves flat over it)
        ubt = np.full(bot.shape, np.inf); ramp = math.tan(RAMP_TOP * D2R); self.ramp_excess = {}
        for h in self.hubs:
            c = np.clip(D @ h["axis"], 1e-3, 1); r_ = h["lv"]["S"] * np.sqrt(1 - c * c) / c; d_ = r_ - h.get("flat_r", HUB_R + 0.5)
            if h["role"] == "lower": ubt = np.minimum(ubt, np.where(d_ < 25.0, h["lv"]["S"] / c + ramp * np.maximum(d_, 0.0), np.inf))
            rim = (d_ > 0) & (d_ <= 12.0) & valid & ins & (near >= d_ - 1e-6)                # this hub's own rim
            if rim.any(): self.ramp_excess[h["joint"]] = float(np.max((need - hb_b - ramp * np.maximum(d_, 0.0))[rim]))
        tf = fair_field(np.where(cores, top, bf + T_LINK), bf + T_LO, cores, ins, FAIR_LAM, a0=0.004, ub=np.maximum(ubt, bf + T_LO))
        w = 1.0 - smootherstep(np.maximum(near, 0.0) / FAIR_BLEND)
        b2 = w * hb_b + (1 - w) * bf; t2 = w * hb_t + (1 - w) * tf
        self.fair_report = dict(gap_med=float(np.nanmedian(np.where(valid & (self.sdf2(self.X, self.Y) <= 0) & ~cores, b2 - need, np.nan))))
        return b2, t2

    def _swept(self, bot, top, need, valid):
        """links as designed parts: each hub an exact seat plane (lower plates: turned skin side), the arm a swept band of
        constant section - straight generators across its width, one fair height profile h(t) along it (stiff 1-D
        shrink-wrap over the skin envelope + stacking floors, clamped in value and slope to both hub planes), thickness
        easing from the hub stack to T_LINK over EASE mm; arm and hub planes blend G2 over FAIR_BLEND"""
        D = self.D; X, Y = self.X, self.Y; (ax, ay), (bx, by) = self._hub_xy(self.hubs[0]), self._hub_xy(self.hubs[1])
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        T = (X - ax) * ux + (Y - ay) * uy; Vc = -(X - ax) * uy + (Y - ay) * ux                       # along / across the arm (chart mm)
        cores = np.zeros(bot.shape, bool); near = np.full(bot.shape, np.inf); hb_b = bot.copy(); hb_t = top.copy(); dd = []
        for h in self.hubs:
            c = np.clip(D @ h["axis"], 1e-3, 1); r_ = h["lv"]["S"] * np.sqrt(1 - c * c) / c; d_ = r_ - h.get("flat_r", HUB_R + 0.5); dd.append(d_)
            hb, ht = h["_hb"]
            if h["role"] == "lower":                                                                 # turned skin side: per ring the shallowest the skin allows
                ring = np.clip(np.round(r_ / 0.5).astype(int), 0, 200); ok = valid & (r_ <= HUB_R + 3.0)
                prof = np.full(201, -np.inf); np.maximum.at(prof, ring[ok], (need * c)[ok])
                for k in range(199, -1, -1): prof[k] = max(prof[k], prof[k + 1])               # monotone: deepest ring governs inward
                lv = h["lv"]; zb = np.clip(prof, lv["S"] - T_BOT, lv["S"] - 2.85); zb[~np.isfinite(prof)] = lv["S"] - T_LO
                from scipy.ndimage import gaussian_filter1d
                zb = np.maximum(gaussian_filter1d(zb, 2.0), zb); hb = zb[ring] / c
            closer = d_ < near; near = np.where(closer, d_, near); cores |= d_ <= 0
            hb_b = np.where(closer, hb, hb_b); hb_t = np.where(closer, ht, hb_t); h["_hbs"] = (hb, ht)
        # 1-D profile along the arm: the floor m(t) = max across the band of (need - cross-slope * v)
        tA = HUB_R + 0.5 + 0.0; tB = L - (HUB_R + 0.5); dt = GRID
        ts = np.arange(tA - 2 * dt, tB + 2 * dt + 1e-9, dt); band = (np.abs(Vc) <= HW + 1.5) & (T > tA - 1) & (T < tB + 1) & valid
        def plane_cl(k, t):                                                                          # hub k's bottom plane along the centreline + its cross slope
            hb = self.hubs[k]["_hbs"][0]; fb = RectBivariateSpline(self.xs, self.ys, np.where(np.isfinite(hb), hb, 0.0), kx=1, ky=1, s=0)
            px, py = ax + t * ux, ay + t * uy; v0 = fb.ev(px, py); cs = (fb.ev(px - uy, py + ux) - fb.ev(px + uy, py - ux)) / 2.0
            return v0, cs
        if tB - tA < 2.0:                                                                            # hubs (nearly) touching: blend the two planes across the waist
            w = smootherstep((T - (L / 2 - 6.0)) / 12.0)
            bA, bB = self.hubs[0]["_hbs"][0], self.hubs[1]["_hbs"][0]; tA_, tB_ = self.hubs[0]["_hbs"][1], self.hubs[1]["_hbs"][1]
            arm_b = (1 - w) * bA + w * bB; arm_t = (1 - w) * tA_ + w * tB_
            lbb = np.where(valid & ~cores, need - arm_b, -np.inf)                                  # where the skin / stacking floor is above the blend: one fair bump
            bump = fair_field(np.zeros(bot.shape), lbb, cores, self.inside, FAIR_LAM) if np.isfinite(lbb).any() and np.nanmax(lbb) > 0 else np.zeros(bot.shape)
            bump = np.maximum(bump, 0.0); arm_b = arm_b + bump; arm_t = np.maximum(arm_t + bump, arm_b + T_LO)
            self.ramp_excess = {}
        else:
            (hA, cA), (hB, cB) = plane_cl(0, ts[0]), plane_cl(1, ts[-1]); (hA1, _), (hB1, _) = plane_cl(0, ts[1]), plane_cl(1, ts[-2])
            wc = smootherstep((ts - tA) / max(tB - tA, 1e-6)); cs = (1 - wc) * cA + wc * cB              # cross slope eases from hub A's to hub B's
            ti = np.clip(np.round((T - ts[0]) / dt).astype(int), 0, len(ts) - 1)
            m = np.full(len(ts), -np.inf); np.maximum.at(m, ti[band], (need - cs[ti] * Vc)[band])
            h1 = _fair1d(m, (hA, hA1), (hB, hB1), dt, FAIR_LAM)
            ramp = math.tan(RAMP_TOP * D2R); self.ramp_excess = {}
            for k, (h0, idx) in enumerate(((hA, 0), (hB, len(ts) - 1))):
                d1 = np.abs(np.arange(len(ts)) - idx) * dt; z = (h1 - h0) - ramp * d1 - 0.0
                self.ramp_excess[self.hubs[k]["joint"]] = float(np.max(np.where(d1 <= 12.0, (m - h0) - ramp * d1, -np.inf)))
            arm_b = h1[ti] + cs[ti] * Vc
            # thickness: hub stack -> T_LINK over EASE, under a lower hub's seat + 35 deg
            thA = float(np.nanmedian((self.hubs[0]["_hbs"][1] - self.hubs[0]["_hbs"][0])[(dd[0] > -1) & (dd[0] < 0.5)])) if ((dd[0] > -1) & (dd[0] < 0.5)).any() else T_LINK
            thB = float(np.nanmedian((self.hubs[1]["_hbs"][1] - self.hubs[1]["_hbs"][0])[(dd[1] > -1) & (dd[1] < 0.5)])) if ((dd[1] > -1) & (dd[1] < 0.5)).any() else T_LINK
            EASE = 12.0; tt = T.clip(tA, tB)
            thk = T_LINK + (thA - T_LINK) * (1 - smootherstep((tt - tA) / EASE)) + (thB - T_LINK) * (1 - smootherstep((tB - tt) / EASE))
            ub = np.full(bot.shape, np.inf)
            for k, h in enumerate(self.hubs):
                if h["role"] == "lower":
                    c = np.clip(D @ h["axis"], 1e-3, 1); ub = np.minimum(ub, np.where(dd[k] < 25.0, h["lv"]["S"] / c + ramp * np.maximum(dd[k], 0.0), np.inf))
            arm_t = np.maximum(np.minimum(arm_b + thk, ub), arm_b + T_LO)
        w = 1.0 - smootherstep(np.maximum(near, 0.0) / FAIR_BLEND)
        b2 = w * hb_b + (1 - w) * arm_b; t2 = w * hb_t + (1 - w) * arm_t
        ins = (self.sdf2(X, Y) <= 0) & valid & ~cores
        self.fair_report = dict(gap_med=float(np.nanmedian(np.where(ins, b2 - need, np.nan))), gap_min=float(np.nanmin(np.where(ins, b2 - need, np.nan))) if ins.any() else 0.0)
        return b2, t2

    def max_bot_at(self, dirs):
        """highest the skin side may go along local dirs: +inf on ribbons/transitions, S - 2.85 in a lower hub's core,
        the plane itself in an upper hub's core"""
        out = np.full(dirs.shape[:-1], np.inf)
        for h in self.hubs:
            c = np.clip(dirs @ h["axis"], 1e-3, 1); lv = h["lv"]; core = lv["S"] * np.sqrt(1 - c * c) / c <= HUB_R + 0.5
            lim = (lv["S"] - 2.85) / c if h["role"] == "lower" else lv["U0"] / c
            out = np.where(core, np.minimum(out, lim), out)
        return out
    def lift_allow(self, dirs):
        """largest local lift the shape can take there and stay fair: min(cap, tan 40 deg x distance out of the hub cores)"""
        dmin = np.full(dirs.shape[:-1], np.inf)
        for h in self.hubs:
            c = np.clip(dirs @ h["axis"], 1e-3, 1); dmin = np.minimum(dmin, h["lv"]["S"] * np.sqrt(1 - c * c) / c - h.get("flat_r", HUB_R + 0.5))
        return np.minimum(self.lift_cap, math.tan(RAMP_DEG * D2R) * np.maximum(dmin, 0.0))
    def rho_bot(self, X, Y): return self.fb.ev(np.ravel(X), np.ravel(Y)).reshape(np.shape(X))
    def rho_top(self, X, Y): return self.ft.ev(np.ravel(X), np.ravel(Y)).reshape(np.shape(X))
    def top_at(self, dirs):
        """outer-side radius along local dirs (nan outside the planform)"""
        xy = self.chart.xy(dirs); x, y = xy[..., 0].ravel(), xy[..., 1].ravel()
        ins = (self.sdf2(x, y) <= 0) & (x >= self.xs[0]) & (x <= self.xs[-1]) & (y >= self.ys[0]) & (y <= self.ys[-1])
        out = np.full(len(x), np.nan); out[ins] = self.ft.ev(x[ins], y[ins]); return out.reshape(xy.shape[:-1])
    def top_hw_at(self, dirs):
        """outer envelope incl. dome caps (what another member passing over must clear)"""
        xy = self.chart.xy(dirs); x, y = xy[..., 0].ravel(), xy[..., 1].ravel()
        ins = (self.sdf2(x, y) <= 0) & (x >= self.xs[0]) & (x <= self.xs[-1]) & (y >= self.ys[0]) & (y <= self.ys[-1])
        out = np.full(len(x), np.nan); out[ins] = self.fh.ev(x[ins], y[ins]); return out.reshape(xy.shape[:-1])
    def bot_at(self, dirs):
        xy = self.chart.xy(dirs); x, y = xy[..., 0].ravel(), xy[..., 1].ravel()
        ins = (self.sdf2(x, y) <= 0) & (x >= self.xs[0]) & (x <= self.xs[-1]) & (y >= self.ys[0]) & (y <= self.ys[-1])
        out = np.full(len(x), np.nan); out[ins] = self.fb.ev(x[ins], y[ins]); return out.reshape(xy.shape[:-1])

    def solid(self, e=0.5):                                                                  # 0.5 G2 round: the hub seat stays flat under the whole Ø22 cap skirt
        s, info = SH.sheet_solid(self.chart, self.rho_bot, self.rho_top, self.sdf2, self.extent(), e=e)
        self.info = info; return s

def _smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0) / k; return np.minimum(a, b) - h ** 3 * k / 6

def swept_top_constraint(outer, inner, frames, clear=CLEAR_MM):
    """min radius for `outer`'s skin side so it clears `inner`'s outer side over every frame (grid of outer)"""
    D = outer.D.reshape(-1, 3); need = np.full(len(D), -np.inf)
    for G in frames:
        Ro, Ri = G[outer.group], G[inner.group]; Di = D @ (Ri.T @ Ro).T
        t = inner.top_at(Di); m = np.isfinite(t)
        need[m] = np.maximum(need[m], t[m] + clear)
    need[~np.isfinite(need)] = np.nan
    return need.reshape(outer.D.shape[:-1])

def band_baseline(m, dirs_local, h, kind):
    """band design's fitted ribbon underside interpolated over the member's chart grid (nan away from the ribbon)"""
    from scipy.interpolate import griddata
    ix = np.nonzero(np.asarray(kind) == 0)[0]
    if len(ix) < 4: return None
    xy = m.chart.xy(np.asarray(dirs_local)[ix]); v = np.asarray(h)[ix]
    out = griddata(xy, v, (m.X, m.Y), method="linear")
    return out

def pair_lift(outer, inner, frames, mask=None, clear=CLEAR_MM):
    """how much `outer` must rise (max, and share of its planform affected) to clear `inner`'s swept outer side"""
    c = swept_top_constraint(outer, inner, frames, clear)
    if mask is not None: c[mask] = np.nan
    ins = outer.sdf2(outer.X, outer.Y) <= 0; v = np.where(np.isfinite(c) & ins, c - outer.bot, np.nan)
    if not np.isfinite(v).any(): return 0.0, 0.0, c
    return float(max(0.0, np.nanmax(v))), float(np.mean(np.nan_to_num(v, nan=-1) > 0)), c

_DECIDE = {}; HARD = {}; CE = {}
def location_constraint(A, B, frames, core=None, clear=CLEAR_MM, sub=2):
    """min radius for A's skin side: wherever A and B overlap radially in a frame, the part that can clear the other more
    cheaply rises over it (planes can't move; lower-hub undersides may rise to S - 2.85); near a shared joint the stack
    decides. Decided once (first call) and frozen. Overlaps neither side can resolve are recorded in HARD."""
    sl = np.s_[::sub, ::sub]; D = A.D[sl].reshape(-1, 3); ins = (A.sdf2(A.X, A.Y)[sl] <= 1.5).ravel()
    if core is not None: ins &= ~core[sl].ravel()
    key = (A.name, B.name); first = key not in _DECIDE
    order, near = None, None
    for ha in A.hubs:
        for hb in B.hubs:
            if ha["joint"] == hb["joint"]:
                c = np.clip(D @ ha["axis"], 1e-3, 1); near = ha["lv"]["S"] * np.sqrt(1 - c * c) / c <= HUB_R + 15.0; order = ha["role"] == "upper"
    if first: _DECIDE[key] = []; HARD[key] = np.zeros(len(frames), bool)
    abot = A.bot[sl].ravel(); atop = A.top_hw[sl].ravel(); amax = A.max_bot_at(D); aall = A.lift_allow(D)
    need = np.full(len(D), -np.inf)
    for f, G in enumerate(frames):
        Db = D @ (G[B.group].T @ G[A.group]).T
        if first:
            bb = B.bot_at(Db); m = ins & np.isfinite(bb); ix = np.nonzero(m)[0]
            if len(ix):
                bt = B.top_hw_at(Db[ix]); bmax = B.max_bot_at(Db[ix])
                ce = np.where(near[ix], -0.05, clear) if near is not None else np.full(len(ix), clear)   # coaxial plates: the 0.15 stack gap itself (numeric slack)
                ov = np.minimum(atop[ix], bt) - np.maximum(abot[ix], bb[ix]) + ce > 0
                ix, bt, bmax, bbx, ce = ix[ov], bt[ov], bmax[ov], bb[ix][ov], ce[ov]
                costA = bt + ce - abot[ix]; okA = (bt + ce <= amax[ix]) & ((costA <= aall[ix]) | (costA <= 0.3))
                costB = atop[ix] + ce - bbx; okB = (atop[ix] + ce <= bmax) & ((costB <= B.lift_allow(Db[ix])) | (costB <= 0.3))
                upA = okA & (~okB | (costA <= costB))
                if order is not None:                                                    # the stack decides near a shared joint
                    upA = np.where(near[ix], order & okA, upA); bad = near[ix] & np.where(order, ~okA, ~okB)
                else: bad = np.zeros(len(ix), bool)
                HARD[key][f] = bool((~okA & ~okB).any() | bad.any())
                ix = ix[upA]; CE[key + (f,)] = ce[upA]
            _DECIDE[key].append(ix)
        ix = _DECIDE[key][f]
        if not len(ix): continue
        bt = B.top_hw_at(Db[ix]); ok = np.isfinite(bt); ce = CE.get(key + (f,), np.full(len(ix), clear)); need[ix[ok]] = np.maximum(need[ix[ok]], bt[ok] + ce[ok])
    need = need.reshape(A.D[sl].shape[:-1])
    if not np.isfinite(need).any(): return None
    full = np.full(A.D.shape[:-1], -np.inf); full[sl] = need
    from scipy.ndimage import maximum_filter
    full = maximum_filter(full, size=sub + 1)
    return np.where(np.isfinite(full), full, np.nan)
