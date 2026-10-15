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
RAMP_TOP = float(__import__("os").environ.get("RAMP_TOP", 35.0))                      # max ramp out of a hub plane (deg); fair_build sets the input's ramp_deg
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

JOINT = __import__("os").environ.get("JOINT", "v4")                                    # "v5": O20 hub, 2x MR117-2RS (joint_v5.py)
if JOINT == "v5": HUB_R = 10.0                                                          # the v5 boss / cap / pad radius (user: "We can go to 20mm hubs")
CAP_RK = HUB_R + 0.0 if JOINT == "v5" else 11.3                                          # cap dome keep-out radius (v4: O22 cap + 0.3)
def stack_levels(F, t_lo=T_LO):
    """joint stack along the joint axis from the lower member's skin-side face F: v4 (joint_v4.py) or v5 (joint_v5.py)"""
    if JOINT == "v5":
        import joint_v5 as J5
        return J5.levels(F, t_lo)
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
            cap = np.maximum(cap, np.where(r_in <= CAP_RK, rim + (crown - rim) * np.sqrt(np.clip(1 - (r_in / CAP_RK) ** 2, 0, 1)) - top, 0.0))
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


# ================================================================ STRAP links (LINK_STYLE=strap): the user's CAD standard
# Each link is ONE constant section (2 HW x T_LINK, edges rounded STRAP_E) on ONE planar fair spine, leaving each hub
# through an exact flat circular pad. Why it cannot twist: both hub axes pass through GH, so the plane spanned by them
# contains both axes; the spine lies in that plane and the strap is the spine extruded across it (along the plane's normal
# ez) - a bent flat bar. Every hub pad plane contains ez too, so the pads are the straight ends of the same planar curve
# and the whole skin side (pads + strap) is one extruded G2 curve: straight on each pad, a clamped cubic B-spline with
# few control points between (its first / last three control points on the pad lines: tangent AND zero curvature at the
# joins -> G2 by construction). The spine is fitted to the floor the band evaluator's fitted shape gives (its ribbon
# underside + the dense skin envelope + stacking floors, members' need) - as low as the floor allows, fair (bending
# energy), bend radius >= STRAP_RMIN, ramp <= RAMP_TOP. Walls are designed (sheet.sheet_solid_v2): true cylinders about
# each hub axis around the pads, the strap's own normal along it (rectangular section). Upper hubs: a boss (U0..H1)
# whose top blends G2 into the strap top over GUSSET mm; lower hubs: a turned skin side (centre flat + cone, smooth
# corners) fitted under the pad where the skin allows, never above the face F.
import os as _os
LINK_STYLE = _os.environ.get("LINK_STYLE", "sheet")
STRAP_E = float(_os.environ.get("STRAP_E", 1.2))                                         # strap edge rounds (user: 1-1.5)
PAD_E = {"upper": (0.4, 0.3), "lower": (0.8, 0.4)}                                       # (skin-side, outer) rounds at a pad: the boss-top round sits under the cap skirt
# Bend radius / fairness / control points (2026-10-15, measured on r20 s1414 #4): at R 25 mm, fairness 1500 and <= 5
# control points the spine could not get down from hubs that sit 11-21 mm over the skin need (l2: both hubs upper,
# 21.3 / 11.5 mm up; an S-bend at R 25 + 60 deg ramp needs ~45 mm to drop 21 mm) -> l2 rode 9.6 mm (median) over the
# evaluator's fitted ribbon, the fair link 0.1 mm; l1 3.6 vs 1.3 (R1 2-14: strap 35.0 %, fair 46.2 %). The fair link bends
# at ~5 mm (smootherstep over Lt 8-25 mm). R 10 = 3.3 t for the 3.0 Ti strap (hot-formed / 5-axis machined), fairness
# 150, 3-6 control points: spine gap over its floor l1 1.28 -> 0.36, l2 8.41 -> 0.49 mm (median, offline refit).
GUSSET = float(_os.environ.get("GUSSET_MM", 7.0)); STRAP_RMIN = float(_os.environ.get("STRAP_RMIN", 10.0))
FILLET_K = 4.0; STRAP_FAIR = float(_os.environ.get("STRAP_FAIR", 150.0)); DIMPLE_MAX = float(_os.environ.get("DIMPLE_MAX", 8.0)); DIMPLE_BW = 1.5
STRAP_KS = tuple(int(k) for k in _os.environ.get("STRAP_KS", "3,4,5,6").split(","))    # interior control-point counts tried by the spine fit
TAB_RMIN = 8.0                                                                           # the base's short mount tab may bend tighter than a link
FLOOR_TOL = 0.12                                                                         # a spine may dip this far into the need's 0.5 mm margin (joint raises start at 0.1)
REACH_K = 1.6                                                                            # the reach cap's bend radius / STRAP_RMIN (room for the G2 lead-in)
L_FLAT_UP = float(_os.environ.get("L_FLAT_UP", 2.0))                                     # an upper link runs flat this far past its pad (clear of the cap skirt)

def _ss(x): return smootherstep((np.asarray(x, float) + 1.0) / 2.0)                    # 0 at x <= -1, 1 at x >= 1, C2
def _sstep_int(x):
    """integral of _ss from -inf to x (C3): 0 for x <= -1, x for x >= 1"""
    x = np.asarray(x, float); t = np.clip((x + 1.0) / 2.0, 0.0, 1.0)
    return np.where(x >= 1.0, x, 2.0 * (t ** 6 - 3.0 * t ** 5 + 2.5 * t ** 4))       # 2 * int_0^t (6s^5 - 15s^4 + 10s^3) ds
def _smax(a, b, k): return -_smin(-a, -b, k)

def dimple_profile(r, zb, zc, r1, al, bw=DIMPLE_BW):
    """turned skin side of a lower pad: flat at zc out to r1, cone at al back up to the face zb, smooth (C3) corners of
    half-width bw: z(r) = zc + tan(al) * (I((r - r1)/bw) - I((r - r2)/bw)) * bw, r2 = r1 + (zb - zc)/tan(al)"""
    if zc >= zb - 1e-9 or al <= 0: return np.full_like(np.asarray(r, float), zb)
    r2 = r1 + (zb - zc) / math.tan(al)
    return zc + math.tan(al) * bw * (_sstep_int((np.asarray(r, float) - r1) / bw) - _sstep_int((np.asarray(r, float) - r2) / bw))

def fit_dimple(rr, zneed, zb, r_max, depth_max=DIMPLE_MAX, bw=DIMPLE_BW):
    """lowest-stand-off profile of the family above zneed(rr) (axial heights per ring), inside r_max, <= depth_max under zb"""
    zn = np.where(np.isfinite(zneed), np.minimum(zneed, zb), -np.inf); floor = zb - depth_max; nf = np.maximum(zn, floor); w = np.maximum(rr, 0.1)
    best = (float(np.sum((zb - nf) * w)), zb, 0.0, 0.0)                                  # no dimple
    if np.all(zn >= zb - 0.05): return dict(zc=zb, r1=0.0, al=0.0, J=best[0])
    for al in np.radians(np.arange(5.0, 45.01, 2.5)):
        for r1 in np.arange(bw, r_max, 0.25):
            lo, hi = floor, zb - 0.05
            ok = lambda zc: (r1 + (zb - zc) / math.tan(al) + bw <= r_max) and bool(np.all(dimple_profile(rr, zb, zc, r1, al, bw) >= zn - 1e-6))
            if not ok(hi): continue
            if ok(lo): zc = lo
            else:
                for _ in range(30):
                    mid = 0.5 * (lo + hi); lo, hi = (lo, mid) if ok(mid) else (mid, hi)
                zc = hi
            J = float(np.sum((dimple_profile(rr, zb, zc, r1, al, bw) - nf) * w))
            if J < best[0] - 1e-9: best = (J, zc, r1, al)
    return dict(J=best[0], zc=best[1], r1=best[2], al=best[3])

class Strap(Member):
    """a link (2 hubs) or the base (1 hub + flat mount tab) as a strap; same API as Member for the pipeline"""
    def __init__(self, name, group, hubs, theta=None, strip_dir=None, strip_len=None, R0=None, flat=False):
        super().__init__(name, group, hubs, theta, strip_dir, strip_len, R0, flat)
        a0 = np.asarray(hubs[0]["axis"], float)
        if len(hubs) == 2:
            a1 = np.asarray(hubs[1]["axis"], float); ez = unit(np.cross(a0, a1)); self.th = math.acos(float(np.clip(a0 @ a1, -1, 1)))
        else:
            s = unit(np.asarray(strip_dir, float) - (np.asarray(strip_dir, float) @ a0) * a0); ez = unit(np.cross(a0, s))
            self.th = math.atan((max(strip_len, 0.0) + HUB_R) / self._zb(hubs[0]))       # tab end (polar angle)
        self.ex, self.ez = a0, ez; self.ey = np.cross(ez, a0); self.sp = None
        self.phik = [0.0] + ([self.th] if len(hubs) == 2 else [])
    # ---- levels of a hub pad: skin side (zb) and top (zt: lower seat S, upper boss top H1 under the cap skirt)
    @staticmethod
    def _zb(h): return h["lv"]["F"] if h["role"] == "lower" else h["lv"]["U0"]
    @staticmethod
    def _zt(h): return h["lv"]["S"] if h["role"] == "lower" else h["lv"].get("H1", h["lv"]["U1"])
    def _polar(self, D):
        px, py, pz = D @ self.ex, D @ self.ey, D @ self.ez; cps = np.maximum(np.hypot(px, py), 1e-6)
        return np.arctan2(py, px), cps, pz / cps
    def _r_at(self, D, k, z):
        c = np.clip(D @ self.hubs[k]["axis"], 1e-3, 1); return z * np.sqrt(1 - c * c) / c, c
    # ---- the skin-side spine in polar form Q(phi) (radius from GH in the strap plane) and its outer offset
    def _line(self, k, phi, z):
        return z / np.maximum(np.cos(np.asarray(phi, float) - self.phik[k]), 1e-3)
    def Qb(self, phi):
        phi = np.asarray(phi, float); h = self.hubs; zA = self._zb(h[0])
        if len(h) == 1 and self.sp is None: return self._line(0, phi, zA)
        if len(h) == 1:
            sp = self.sp; out = np.interp(phi, sp["phi_b"], sp["Q_b"]); out = np.where(phi <= sp["phi_b"][0], self._line(0, phi, zA), out)
            return np.where(phi >= sp["phi_b"][-1], sp["end_d"] / np.maximum(np.cos(phi - sp["nu"][-1]), 1e-3), out)
        zB = self._zb(h[1])
        if self.sp is None:                                                              # before the fit: blend of the two pad lines
            s = smootherstep(phi / self.th); return (1 - s) * self._line(0, phi, zA) + s * self._line(1, phi, zB)
        sp = self.sp; out = np.interp(phi, sp["phi_b"], sp["Q_b"])
        out = np.where(phi <= sp["phi_b"][0], self._line(0, phi, zA), out); return np.where(phi >= sp["phi_b"][-1], self._line(1, phi, zB), out)
    def Qt(self, phi):
        phi = np.asarray(phi, float); h = self.hubs; zA = self._zb(h[0]) + T_LINK
        if self.sp is None: return self.Qb(phi) + T_LINK if len(h) == 2 else self._line(0, phi, zA)
        if len(h) == 1:
            sp = self.sp; out = np.interp(phi, sp["phi_t"], sp["Q_t"]); out = np.where(phi <= sp["phi_t"][0], self._line(0, phi, zA), out)
            return np.where(phi >= sp["phi_t"][-1], (sp["end_d"] + T_LINK) / np.maximum(np.cos(phi - sp["nu"][-1]), 1e-3), out)
        sp = self.sp; zB = self._zb(h[1]) + T_LINK; out = np.interp(phi, sp["phi_t"], sp["Q_t"])
        out = np.where(phi <= sp["phi_t"][0], self._line(0, phi, zA), out); return np.where(phi >= sp["phi_t"][-1], self._line(1, phi, zB), out)
    def nang(self, phi):
        """angle (in the strap plane, from ex) of the spine's outward normal at polar angle phi: the hub axis on a pad"""
        phi = np.asarray(phi, float)
        if self.sp is None: return np.clip(phi, 0.0, self.th) if len(self.hubs) == 2 else np.zeros_like(phi)
        sp = self.sp; out = np.interp(phi, sp["phi_b"], sp["nu"])
        return np.where(phi <= sp["phi_b"][0], 0.0, np.where(phi >= sp["phi_b"][-1], self.th if len(self.hubs) == 2 else sp["nu"][-1], out))
    # ---- planform (true mm on the skin side): hub discs + the strap / tab capsule, G2 blends
    def sdf2(self, x, y):
        x = np.asarray(x, float); y = np.asarray(y, float); D = self.chart.dirs(x, y); phi, cps, tps = self._polar(D)
        ds = [self._r_at(D, k, self._zb(h))[0] - HUB_R for k, h in enumerate(self.hubs)]
        Q = self.Qb(phi); z = Q * tps; along = Q * np.maximum(np.maximum(-phi, phi - self.th), 0.0)
        strap = np.hypot(along, z) - HW; out = _smin(ds[0], strap, FILLET_K)
        if len(ds) == 2: out = _smin(out, ds[1], FILLET_K)
        return out
    def _pad_w(self, D):
        """blend weight of each hub pad (1 on the pad, 0 on the strap 6 mm past its rim)"""
        return [1.0 - smootherstep((self._r_at(D, k, self._zb(h))[0] - HUB_R - 0.5) / 6.0) for k, h in enumerate(self.hubs)]
    def e_bot(self, x, y):
        D = self.chart.dirs(np.asarray(x, float), np.asarray(y, float)); e = np.full(D.shape[:-1], STRAP_E)
        for w, h in zip(self._pad_w(D), self.hubs): e = e + w * (PAD_E[h["role"]][0] - STRAP_E)
        return e
    def e_top(self, x, y):
        D = self.chart.dirs(np.asarray(x, float), np.asarray(y, float)); e = np.full(D.shape[:-1], STRAP_E)
        for w, h in zip(self._pad_w(D), self.hubs): e = e + w * (PAD_E[h["role"]][1] - STRAP_E)
        return e
    def wall_dir(self, P):
        P = np.asarray(P, float); phi = np.arctan2(P @ self.ey, P @ self.ex); nu = self.nang(phi)
        return np.cos(nu)[:, None] * self.ex[None] + np.sin(nu)[:, None] * self.ey[None]
    # ---- analytic fields (chart mm -> radius from GH along the chart direction)
    def field_bot(self, x, y):
        D = self.chart.dirs(np.asarray(x, float), np.asarray(y, float)); phi, cps, _ = self._polar(D); b = self.Qb(phi) / cps
        for k, h in enumerate(self.hubs):
            dm = h.get("_dimple")
            if h["role"] == "lower" and dm is not None and dm["zc"] < self._zb(h) - 1e-6:
                r, c = self._r_at(D, k, self._zb(h)); inner = r < HUB_R - PAD_E["lower"][0]                 # (the profile is the pad plane past its cone)
                b = np.where(inner, np.minimum(b, dimple_profile(r, self._zb(h), dm["zc"], dm["r1"], dm["al"]) / c), b)
        return b
    def field_top(self, x, y):
        D = self.chart.dirs(np.asarray(x, float), np.asarray(y, float)); phi, cps, _ = self._polar(D); t = self.Qt(phi) / cps
        for k, h in enumerate(self.hubs):
            if h["role"] != "upper": continue
            zt = self._zt(h); r, c = self._r_at(D, k, zt); w = 1.0 - smootherstep((r - (HUB_R - PAD_E["upper"][1])) / GUSSET)
            boss = (t - 2.5) + w * (zt / c - (t - 2.5))                                    # the boss top plane, easing to 2.5 under the strap top
            t = _smax(t, boss, 1.5)                                                       # (exactly the plane on the pad, exactly the strap past the gusset)
        return t
    def rho_bot(self, X, Y): return self.field_bot(X, Y)
    def rho_top(self, X, Y): return self.field_top(X, Y)
    def max_bot_at(self, dirs):
        out = np.full(dirs.shape[:-1], np.inf)
        for k, h in enumerate(self.hubs):
            r, c = self._r_at(dirs, k, self._zb(h)); out = np.where(r <= HUB_R + 0.5, np.minimum(out, self._zb(h) / c), out)
        return out

    def _reach(self, d):
        """height a spine can gain d mm past its bend start: flat, then a bend of radius REACH_R (G2 lead-in included),
        then the RAMP_TOP slope"""
        d = np.maximum(np.asarray(d, float), 0.0); b = RAMP_TOP * D2R; R = REACH_K * STRAP_RMIN; d1 = R * math.sin(b)
        return np.where(d <= d1, R - np.sqrt(np.maximum(R * R - np.minimum(d, d1) ** 2, 0.0)), R * (1 - math.cos(b)) + (d - d1) * math.tan(b))
    def _w0(self, h): return max(HUB_R + (L_FLAT_UP if h["role"] == "upper" else 0.3), h.get("flat_r", 0.0))   # flat_r: stays flat under a top-mounted base disc
    def ramp_cap(self):
        """the evaluator's ribbon floor capped by what the strap can reach out of every pad (flat run, bend radius, ramp):
        the evaluator ramps its free ribbon straight out of the hub rim; a fair G2 spine cannot (r20 s1411 #2: the capped
        floor rose at 60 deg from J1's rim after a 1 mm joint raise -> no feasible spine). The skin envelope stays hard."""
        cap = np.full(self.D.shape[:-1], np.inf)
        for k, h in enumerate(self.hubs):
            r, c = self._r_at(self.D, k, self._zb(h)); cap = np.minimum(cap, self._zb(h) / c + self._reach(r - self._w0(h)))
        return cap

    # ---- the spine fit
    def _floor(self, need, valid):
        """per polar angle: the lowest skin-side spine radius Q(phi) that keeps the extruded strap on or above need across
        its width (max over the band of need * cos(psi)); the pad discs are left to the joint raise logic"""
        D = self.D; phi, cps, tps = self._polar(D); z = self.Qb(phi) * tps
        outside = np.ones(phi.shape, bool)
        for k, h in enumerate(self.hubs): outside &= self._r_at(D, k, self._zb(h))[0] > HUB_R - 0.5
        band = (self.sdf2(self.X, self.Y) <= 0.3) & valid & outside & (phi > -0.02)       # every planform point off the pads (incl. the pad fillets)
        dphi = 0.3 / max(self.R0, 1.0); bins = np.arange(-0.03, self.th + 0.03 + (HW + 2.0) / self._zb(self.hubs[0]) + dphi, dphi); fl = np.full(len(bins), -np.inf)
        ib = np.clip(np.round((phi[band] - bins[0]) / dphi).astype(int), 0, len(bins) - 1); np.maximum.at(fl, ib, (need * cps)[band])
        from scipy.ndimage import maximum_filter1d
        fl = maximum_filter1d(np.where(np.isfinite(fl), fl, -1e9), 3); fl[fl < -1e8] = -np.inf
        return bins, fl
    def ramp_report(self, bins, fl):
        """per hub: how far the floor rises above what a ramp of RAMP_TOP out of the pad allows (> 0: raise the joint)"""
        k_ = math.tan(RAMP_TOP * D2R); out = {}
        for k, h in enumerate(self.hubs):
            dph = np.abs(bins - self.phik[k]); m = np.isfinite(fl) & (dph < math.pi / 2)
            rho = fl * np.sin(dph); zax = fl * np.cos(dph); d = rho - HUB_R; sel = m & (d > -0.5) & (d <= 12.0)
            out[h["joint"]] = float(np.max(zax[sel] - (self._zb(h) + self._reach(rho[sel] - self._w0(h))))) if sel.any() else -1.0
        return out
    def fit_spine(self, bins, fl, ks=None):
        ks = STRAP_KS if ks is None else ks
        from scipy.interpolate import BSpline
        from scipy.optimize import minimize
        h = self.hubs; zA = self._zb(h[0]); th = self.th; free = len(h) == 1; zB = zA if free else self._zb(h[1])
        a1 = np.array([math.cos(th), math.sin(th)]); tA = np.array([0.0, 1.0]); tB = np.array([math.sin(th), -math.cos(th)])
        LA = lambda w: np.array([zA, 0.0]) + np.multiply.outer(w, tA); LB = lambda w: zB * a1 + np.multiply.outer(w, tB)
        ok_f = np.isfinite(fl); flv = np.where(ok_f, fl, -1e9)
        def floor_at(ph): return np.interp(ph, bins, flv)
        sR, kR = math.sin(RAMP_TOP * D2R), math.tan(RAMP_TOP * D2R); u = np.linspace(0, 1, 260)
        w0A = self._w0(h[0]); w0B = w0A if free else self._w0(h[1])
        lowers = [(k, hh) for k, hh in enumerate(h) if hh["role"] == "lower"]
        def ctrl(p, k):
            I = p[6:].reshape(k, 2)
            if free: return np.vstack([LA(p[0]), LA(p[0] + p[1]), LA(p[0] + p[1] + p[2]), I])          # the tab's end is free
            return np.vstack([LA(p[0]), LA(p[0] + p[1]), LA(p[0] + p[1] + p[2]), I, LB(p[3] + p[4] + p[5]), LB(p[3] + p[4]), LB(p[3])])
        def curve(p, k):
            C = ctrl(p, k); n = len(C); t = np.r_[[0.0] * 4, np.linspace(0, 1, n - 2)[1:-1], [1.0] * 4]
            b = BSpline(t, C, 3); P = b(u); d1 = b.derivative(1)(u); d2 = b.derivative(2)(u); sp = np.linalg.norm(d1, axis=1)
            kap = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / sp ** 3; return P, d1 / sp[:, None], kap, sp
        def parts(p, k):
            P, T, kap, sp = curve(p, k); ph = np.arctan2(P[:, 1], P[:, 0]); Q = np.hypot(P[:, 0], P[:, 1])
            wl = np.r_[np.linspace(HUB_R + 0.3, p[0], 10)]; PA = LA(wl); wl2 = np.linspace(HUB_R + 0.3, p[3], 10); PB = PA[:0] if free else LB(wl2)
            Ps = np.vstack([P, PA, PB]); phs = np.arctan2(Ps[:, 1], Ps[:, 0]); Qs = np.hypot(Ps[:, 0], Ps[:, 1]); fs = floor_at(phs)
            g_floor = np.where(fs > -1e8, Qs - fs + FLOOR_TOL, 10.0)                       # FLOOR_TOL into the 0.5 margin: below fair_build's 0.1 raise threshold
            self._gfloor_at = (np.degrees(phs), Qs, fs, len(P), len(PA))
            g_kap = 1.0 / (TAB_RMIN if free else STRAP_RMIN) - np.abs(kap)
            er = np.c_[np.cos(ph), np.sin(ph)]; g_ramp = sR - np.abs((T * er).sum(1))
            g_mono = np.diff(ph) * 1e3
            g_ceil = []
            for k_, hh in lowers:                                                         # the lower link leaves under its seat + ramp
                dph = np.abs(ph - self.phik[k_]); rho = (Q + T_LINK) * np.sin(dph); m = rho < HUB_R + 25.0
                g_ceil.append(np.where(m, hh["lv"]["S"] + self._reach(rho - self._w0(hh)) - (Q + T_LINK) * np.cos(dph), 5.0))
            g_end = [np.array([ph[-1] - (th + (HW + 1.0) / zA)]) * 100.0] if free else []     # the spine reaches past the tab's round end
            blocks = [("floor", g_floor), ("bend", g_kap), ("ramp", g_ramp), ("mono", g_mono)] + [(f"ceil{i}", c_) for i, c_ in enumerate(g_ceil)] + [("end", e_) for e_ in g_end]
            soft = getattr(self, "_soft_floor", False)                                    # soft floor: bend / ramp / mono / ceil stay hard, the floor goes to the objective
            g = np.concatenate([b_ for n_, b_ in blocks if not (soft and n_ == "floor")]); self._gblocks = [(nm_, float(b_.min())) for nm_, b_ in blocks]
            ds = sp / (len(u) - 1); f_ = floor_at(ph); gap = np.where(f_ > -1e8, Q - f_, 0.0)
            J = float(np.sum(gap * ds) + STRAP_FAIR * np.sum(kap ** 2 * ds)) + (1e3 * float(np.sum(np.minimum(g_floor, 0.0) ** 2)) if soft else 0.0)
            return J, g, dict(P=P, T=T, kap=kap, ph=ph, Q=Q, gap=gap, ds=ds)
        best = None
        # pass 1: floor hard. If no k then meets the bend radius (the floor needs a joint raise first: provisional fields in
        # replan / before fair_build's ramp raises), pass 2 keeps the bend hard and the floor soft -> a bend-true spine
        # whose floor shortfall is reported (bad = True; ramp_report drives the joint raise), instead of an exception
        for soft_ in (False, True):
          if soft_ and best is not None and not best[0][0]: break
          self._soft_floor = soft_
          if soft_: print(f"  {self.group} spine: no k meets R {STRAP_RMIN} with the floor hard -> soft floor", flush=True); best = None
          for k in ((1, 2) if free else ks):
              pA, pB = w0A + 2.0, w0B + 2.0
              phA = math.atan2(pA + 8.0, zA); phB = (th + 0.05) if free else th - math.atan2(pB + 8.0, zB)
              I = []
              for j in range(k):
                  ph = phA + (phB - phA) * ((j + 1) / k if free else (j + 1) / (k + 1)); m = np.abs(bins - ph) < 0.06
                  if free: ph = phA + (th + (HW + 1.5) / zA - phA) * (j + 1) / k; m = np.abs(bins - ph) < 0.06; fq = max(fl[m & ok_f].max() if (m & ok_f).any() else -1e9, zA / math.cos(ph))
                  else: fq = fl[m & ok_f].max() if (m & ok_f).any() else (1 - (j + 1) / (k + 1)) * zA / math.cos(ph) + (j + 1) / (k + 1) * zB / math.cos(th - ph)
                  q = max(fq + 1.0, 0.0); I.append([q * math.cos(ph), q * math.sin(ph)])
              p0 = np.r_[pA, 4.0, 4.0, pB, 4.0, 4.0, np.ravel(I)]
              bnds = [(w0A, w0A + 30.0), (0.5, 30.0), (0.5, 30.0), (w0B, w0B + 30.0), (0.5, 30.0), (0.5, 30.0)] + [(-300.0, 300.0)] * (2 * k)
              if free: bnds = bnds[:3] + [(w0A, w0A + 1.0), (0.5, 1.0), (0.5, 1.0)] + bnds[6:]          # unused B-end parameters
              def pen(p):                                                                   # stage 1: penalty (always converges to something)
                  J, g, _ = parts(p, k); return J + 1e4 * float(np.sum(np.minimum(g, 0.0) ** 2))
              try:
                  p1 = minimize(pen, p0, method="L-BFGS-B", bounds=bnds, options=dict(maxiter=300)).x
              except Exception as ex_:
                  p1 = p0
              try:
                  res = minimize(lambda p: parts(p, k)[0], p1, method="SLSQP", bounds=bnds, constraints=[dict(type="ineq", fun=lambda p: parts(p, k)[1])],
                                 options=dict(maxiter=400, ftol=1e-7))
                  p = res.x if max(0.0, -parts(res.x, k)[1].min()) <= max(0.05, max(0.0, -parts(p1, k)[1].min())) else p1
              except Exception as ex_:
                  print(f"  strap fit k={k}: {ex_}", flush=True); p = p1; res = type("r", (), dict(nit=0, message=str(ex_)))
              J, g, info = parts(p, k); viol = float(max(0.0, -g.min(), -min(v_ for _, v_ in self._gblocks))); worst = min(self._gblocks, key=lambda t: t[1])
              hard = max(0.0, -min(v_ for n_, v_ in self._gblocks if n_ in ("bend", "mono")) * (STRAP_RMIN if True else 1.0))
              key = (hard > 0.02, viol > 0.05, J if viol <= 0.05 else viol)
              print(f"  {self.group} spine k={k}: J {J:.1f}  viol {viol:.3f}  gap med {np.median(info['gap'][info['gap'] != 0]) if (info['gap'] != 0).any() else 0:.2f}  "
                    f"min R {1 / max(np.abs(info['kap']).max(), 1e-6):.1f} mm  ({res.nit} it, {res.message})" + (f"  worst: {worst[0]} {worst[1]:.2f}" if viol > 0.05 else ""), flush=True)
              if viol > 0.05 and worst[0] == "floor":
                  t_ = self._gfloor_at; i_ = int(np.argmin(np.where(t_[2] > -1e8, t_[1] - t_[2], 1e9)))
                  print(f"    floor worst at {t_[0][i_]:.1f} deg (sample {i_}: spine 0..{t_[3] - 1}, line A ..{t_[3] + t_[4] - 1}, line B after), Q {t_[1][i_]:.2f} floor {t_[2][i_]:.2f}", flush=True)
              if best is None or key < best[0] or (not key[0] and not key[1] and not best[0][0] and not best[0][1] and J < best[0][2] * 0.97): best = (key, k, p, info)
        self._soft_floor = False; key, k, p, info = best
        if key[0]: raise ValueError(f"{self.name}: no spine meets the bend radius {STRAP_RMIN} mm (STRAP_RMIN / ramp / floor incompatible)")
        return k, p, ctrl(p, k), info, key[1]
    def fit_tab(self, bins, fl, Lb=6.0):
        """the base's mount tab: straight off the pad line to w0, one G2 bend (curvature sin^2 over Lb mm) of angle beta
        away from the skin, straight after; the smallest (w0, beta) that clears the floor, brute force"""
        h = self.hubs[0]; zA = self._zb(h); flv = np.where(np.isfinite(fl), fl, -1e9); ok = np.isfinite(fl)
        L_end = (max(self.strip_len, 0.0) + HUB_R + HW + 2.0) * 1.3; best = None
        for beta in np.radians(np.arange(0.0, 60.01, 1.0)):
            for w0 in np.arange(HUB_R + 0.3, HUB_R + 12.0, 0.5):
                s = np.linspace(0, Lb, 120); kap = beta * 2.0 / Lb * np.sin(np.pi * s / Lb) ** 2; ang = np.r_[0.0, np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(s))]
                P = np.c_[zA - np.r_[0.0, np.cumsum(np.sin(ang[1:]) * np.diff(s))], w0 + np.r_[0.0, np.cumsum(np.cos(ang[1:]) * np.diff(s))]]   # bends toward +x (away from GH)
                P[:, 0] = zA + (zA - P[:, 0])                                                 # (mirror: outward = +x)
                t_end = np.array([math.sin(ang[-1]), math.cos(ang[-1])]); tail = P[-1] + np.multiply.outer(np.linspace(0, L_end, 80)[1:], t_end)
                line = np.c_[np.full(30, zA), np.linspace(HUB_R + 0.3, w0, 30)]; Pall = np.vstack([line, P, tail])
                ph = np.arctan2(Pall[:, 1], Pall[:, 0]); Q = np.hypot(Pall[:, 0], Pall[:, 1]); f_ = np.interp(ph, bins, flv)
                viol = float(np.max(np.where(f_ > -1e8, f_ - Q, -1.0)))                     # <= 0.2 mm into the 0.5 margin is accepted
                J = float(np.sum(np.where(f_ > -1e8, Q - f_, 0.0))); key = (round(max(viol - 0.2, 0.0), 2), J)
                if best is None or key < best[0]: best = (key, beta, w0, Pall, viol)
            if best is not None and best[0][0] == 0 and math.degrees(beta) > math.degrees(best[1]) + 10: break
        key, beta, w0, Pall, viol = best
        print(f"  {self.group} tab: bend {math.degrees(beta):.0f} deg at {w0 - HUB_R:.1f} mm past the pad (into the floor {viol:.2f} mm)", flush=True)
        return Pall
    def spine_from_points(self, P):
        """sp dict from a dense skin-side spine polyline P (n, 2) in the strap plane (outer offset T_LINK along its normal)"""
        P = P[np.r_[True, np.linalg.norm(np.diff(P, axis=0), axis=1) > 1e-6]]
        T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]; N = np.c_[T[:, 1], -T[:, 0]]; Pt = P + T_LINK * N
        sp = dict(phi_b=np.arctan2(P[:, 1], P[:, 0]), Q_b=np.hypot(P[:, 0], P[:, 1]), phi_t=np.arctan2(Pt[:, 1], Pt[:, 0]), Q_t=np.hypot(Pt[:, 0], Pt[:, 1]),
                  nu=np.unwrap(np.arctan2(N[:, 1], N[:, 0])), C=P[::20], k=0, p=None, end_d=float(P[-1] @ N[-1]))
        for a in ("phi_b", "phi_t"):
            if np.any(np.diff(sp[a]) <= 0): raise ValueError(f"{self.name}: spine not monotone in polar angle ({a})")
        return sp
    def build_spine(self, k, p, C):
        """dense polar samples of the B-spline part of the skin-side spine and its outer offset (T_LINK along the normal)"""
        from scipy.interpolate import BSpline
        n = len(C); t = np.r_[[0.0] * 4, np.linspace(0, 1, n - 2)[1:-1], [1.0] * 4]; b = BSpline(t, C, 3); u = np.linspace(0, 1, 3000)
        P = b(u); d1 = b.derivative(1)(u); T = d1 / np.linalg.norm(d1, axis=1)[:, None]; N = np.c_[T[:, 1], -T[:, 0]]
        Pt = P + T_LINK * N; nu = np.unwrap(np.arctan2(N[:, 1], N[:, 0]))
        sp = dict(phi_b=np.arctan2(P[:, 1], P[:, 0]), Q_b=np.hypot(P[:, 0], P[:, 1]), phi_t=np.arctan2(Pt[:, 1], Pt[:, 0]), Q_t=np.hypot(Pt[:, 0], Pt[:, 1]), nu=nu, C=C, k=k, p=p,
                  end_d=float(P[-1] @ N[-1]))                                             # free end: the straight run on past it (normal form)
        for a, b_ in (("phi_b", "Q_b"), ("phi_t", "Q_t")):
            if np.any(np.diff(sp[a]) <= 0): raise ValueError(f"{self.name}: spine not monotone in polar angle ({a})")
        return sp

    def fields(self, env, sigma_mm=4.0, baseline=None):
        D = self.D; ok = np.isfinite(env) & (env > 20)
        need = np.where(ok, env + MARGIN, -np.inf)
        if baseline is not None:
            bl = np.where(np.isfinite(baseline), baseline, -np.inf); need = np.maximum(need, np.minimum(bl, self.ramp_cap()))
        for c in self.extra: need = np.maximum(need, np.where(np.isfinite(c), c, -np.inf))
        valid = np.isfinite(need); self.need = need
        # hub reports + lower-pad turned skin sides
        self.hub_report = []
        for k, h in enumerate(self.hubs):
            zb = self._zb(h); r, c = self._r_at(D, k, zb); core = (r <= HUB_R) & valid
            if core.any(): self.hub_report.append((h["joint"], h["role"], float((zb / c - need)[core].min())))
            h["_dimple"] = None
            if h["role"] == "lower":
                rmax = HUB_R - PAD_E["lower"][0] - 0.5; ring = np.clip(np.round(r / 0.25).astype(int), 0, 400); m = valid & (r <= rmax + 0.5)
                prof = np.full(401, -np.inf); np.maximum.at(prof, ring[m], (need * c)[m]); rr = np.arange(401) * 0.25; sel = rr <= rmax
                h["_dimple"] = fit_dimple(rr[sel], prof[sel], zb, rmax)
        # the spine
        self.ramp_excess = {}
        if len(self.hubs) == 1 and (self.strip_len or 0) > 0:                         # the base's tab
            self.sp = None; bins, fl = self._floor(need, valid); P = self.fit_tab(bins, fl)
            if P is not None:
                self.sp = self.spine_from_points(P); bins, fl = self._floor(need, valid); P = self.fit_tab(bins, fl)
                self.sp = self.spine_from_points(P) if P is not None else self.sp
            self.sp is not None and self.sp.__setitem__("floor", (bins, fl)); self.ramp_excess = self.ramp_report(bins, fl); self.fit_info = dict(k=0, tab=self.sp is not None)
        elif len(self.hubs) == 2:
            self.sp = None; bins, fl = self._floor(need, valid)
            for _ in range(2):                                                               # 2nd pass: band width from the fitted spine
                self.ramp_excess = self.ramp_report(bins, fl)
                k, p, C, info, bad = self.fit_spine(bins, fl)
                try: self.sp = self.build_spine(k, p, C)
                except ValueError as ex_:
                    if len(self.hubs) == 2: raise
                    print(f"  {self.name}: tab spine failed ({ex_}): flat tab", flush=True); self.sp = None; break
                self.sp["floor"] = (bins, fl); bins, fl = self._floor(need, valid)
            self.fit_info = dict(k=k, infeasible=bad, gap_med=float(np.median(info["gap"][info["gap"] != 0])) if (info["gap"] != 0).any() else 0.0,
                                 rmin=float(1 / max(np.abs(info["kap"]).max(), 1e-6)))
        else:
            self.ramp_excess = {}; self.fit_info = dict(k=0)
        bot = self.field_bot(self.X, self.Y); top = self.field_top(self.X, self.Y)
        self.bot, self.top = bot, top
        cap = np.zeros_like(top)
        for h in self.hubs:
            if h["role"] != "upper": continue
            c = np.clip(D @ h["axis"], 1e-3, 1); lv = h["lv"]; r_in = lv["U1"] * np.sqrt(1 - c * c) / c
            crown = (lv["top"] + 0.3) / c; rim = lv["U1"] / c
            cap = np.maximum(cap, np.where(r_in <= CAP_RK, rim + (crown - rim) * np.sqrt(np.clip(1 - (r_in / CAP_RK) ** 2, 0, 1)) - top, 0.0))
        self.top_hw = top + np.maximum(cap, 0.0)
        self.fh = RectBivariateSpline(self.xs, self.ys, self.top_hw, kx=1, ky=1, s=0)
        self.fb = RectBivariateSpline(self.xs, self.ys, bot, kx=3, ky=3, s=0); self.ft = RectBivariateSpline(self.xs, self.ys, top, kx=3, ky=3, s=0)
        ins = self.sdf2(self.X, self.Y) <= 0
        self.gap_min = float(np.nanmin(np.where(valid & ins, bot - need, np.nan))) if (valid & ins).any() else float("nan")
        self.t_min = float((top - bot)[ins].min())
        cores = np.zeros(ins.shape, bool)
        for k, h in enumerate(self.hubs): cores |= self._r_at(D, k, self._zb(h))[0] <= HUB_R
        arm = ins & valid & ~cores
        self.fair_report = dict(gap_med=float(np.nanmedian(np.where(arm, bot - need, np.nan))) if arm.any() else 0.0,
                                gap_min=float(np.nanmin(np.where(arm, bot - need, np.nan))) if arm.any() else 0.0)
        return self

    def solid(self, e=None):
        s, info = SH.sheet_solid_v2(self.chart, self.field_bot, self.field_top, self.sdf2, self.extent(), self.e_bot, self.e_top, self.wall_dir)
        self.info = info; return s

def make_member(*a, **k):
    """Member (default sheet links) or Strap (LINK_STYLE=strap)"""
    return (Strap if LINK_STYLE == "strap" else Member)(*a, **k)
