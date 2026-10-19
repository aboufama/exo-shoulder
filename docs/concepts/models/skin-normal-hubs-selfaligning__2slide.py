"""Concept model: skin-normal-hubs-selfaligning RE-SCORED UNDER THE USER'S RULE (2026-10-15, CLAUDE.md "Manufacturable
joints only"): at most 2 passive translations, every joint a real component at its real envelope.
id skin-normal-hubs-selfaligning__2slide (a copy; the 3-slide model docs/concepts/models/skin-normal-hubs-selfaligning.py
and its rows are untouched).

Chain: scapula base -> J1 (O20 hub, 2x MR117-2RS, 12.25 stack, active R) -> link 1 -> J2 (same) -> link 2 -> J3 (same)
-> member 3 (hub 3 + ramped neck + riser + bridge + the across guide's block and its top plate) -> TWO passive miniature
ball guides crossed (along the humerus, across it) -> base plate on the cuff (BOTTOM's top). No radial slide.

What closes with 2 slides (proof in docs/concepts/offset-skin-normal-3r.md, re-derived here): with translations only the
end link moves X(x) = R x + t(q), t = (I-R1)c1 + R1(I-R2)c2 + R1R2(I-R3)c3. Two slides spanning the plane normal to an
arm-fixed n close iff (R n).t = 0 for all q. Setting q1 = q2 = 0 leaves n.(R3^T - I)c3 = 0 for all q3 -> n = d3 (slide
plane = hub 3's plane); then q1 = 0 leaves (R3 n).(R2^T - I)c2 = d3.(R2^T - I)c2 = 0 for all q2 -> c2 on d2 (line 2
through GH) unless d3 || d2 (no chain); likewise line 1 through GH. So of the 3-slide model's 9 seat parameters, b1 and
b2 must be 0; J3's seat and its skin-normal tilt b3 stay free. A residual radial drift from small b1, b2 > 0 may be
taken by the cuff liner (<= R_l, at most 2 mm, user rule), counted as compliance: the cuff (base + along carriage) then
floats radially with it, and the base is lifted by a liner of 2.5x the used amplitude (6-8 mm foam per +-3 mm,
docs/research/passive_dof_hardware.md) minus the 2 mm clearance.

Stage at its real envelope (tools/hardware_catalogue.json, `guide` = THK-RSR3M by default: H 4.0, W 8, block L 12,
rail 3 x 2.6, catalogue conf.):
  z from the base underside (the fitted stack height tr):
  base plate 1.5 (arm-fixed, footprint nA*L + 4 x W + 4)  -> along guide INVERTED: nA blocks on the base [1.5, 1.5+H-H1],
  its rail riding with member 4 [1.5+H-rail_H, 1.5+H], length nA*L + 2 S_a + 2 -> adapter plate 1.0 (member 4, 14 x the
  across rail) -> across guide: rail [.., +rail_H], length nT*L + 2 S_t + 2, nT blocks (member 3) up to H -> member-3
  top plate 2.0 (W + 4 x nT*L + 4), which the bridge strap (8 x 3) joins at its underside.
  Total 1.5 + 4 + 1 + 4 + 2 = 12.5 mm (the template stage of the 3-slide model: 13.5 + R_r). H1 (block underside over
  the rail's mounting face) = 1.0 is assumed [confirm on the drawing]. nA = 2 (double block, MA 2.11 N.m: the arm's
  orientation torque goes through the stage; one block's MA1 is 0.29 N.m), nT = 1 (MC 0.45 N.m) - parameters.
Every plate underside not covered by the part below it is sampled as metal on the 2 mm grid and scored; every box edge
is checked for skin contact; boxes / cylinders / straps are checked part-to-part (>= 1 mm, the verifier's VModel set +
the moving along rail vs hubs 1-3, links 1-2 and the member-3 neck).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/skin-normal-hubs-selfaligning__2slide.py [check|kin|redteam] ['<json>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("seed_offset_3r_slides_2s", os.path.join(HERE, "seed-offset-3r-slides.py"))
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)   # a PRIVATE copy: its stage constants are re-set below
BP = CB.BP; unit = S.unit
ID = "skin-normal-hubs-selfaligning__2slide"
NAME = "Skin-normal hubs, 2 crossed miniature guides at real size (user rule: <= 2 passive translations)"

# ---- the real stage (tools/hardware_catalogue.json) -----------------------------------------------------------------
HWC = json.load(open(os.path.join(REPO, "tools", "hardware_catalogue.json")))
GUIDES = {g["id"]: g for g in HWC["linear_guides"]}
T_BASE, T_ADAPT, T_TOP, FL, H1 = 1.5, 1.0, 2.0, 2.0, 1.0      # plates (mm), plate margin round a block, block underside over the rail face

PARAMS = dict(S.PARAMS)
PARAMS.update(remote=1, ramp=1, neck=13.0, S_auto=1, jam_contact=1, drop=1, slides=1, vfix=1,
              az1=94.61, el1=60.68, b1=0.0,     # J1 seat (skin-normal-hubs k722's seat), b1 must be 0 for exact closure
              az2=24.06, el2=48.54, b2=0.0,     # J2 rest seat (k722), b2 must be 0 for exact closure
              wd=75.16, wa=-13.04, b3=0.21,     # J3 seat on the arm (k722), free
              S_max=25.0, centre=1,
              R_l=0.5,                          # radial residual the cuff liner may take (mm, <= 2 by the user rule); 0.5 = closure tol.
              guide="THK-RSR3M", nA=2, nT=1)


def stack(P):
    """layer heights (mm over tr) and footprints of the real stage for params P"""
    g = GUIDES[P.get("guide", "THK-RSR3M")]; H, W, L, rW, rH = g["H"], g["W"], g["L"], g["rail_W"], g["rail_H"]
    nA, nT = int(P.get("nA", 2)), int(P.get("nT", 1))
    z = dict(blkA0=T_BASE, blkA1=T_BASE + H - H1, railA0=T_BASE + H - rH, railA1=T_BASE + H)
    z.update(ad0=z["railA1"], ad1=z["railA1"] + T_ADAPT)
    z.update(railT0=z["ad1"], railT1=z["ad1"] + rH, blkT0=z["ad1"] + H1, blkT1=z["ad1"] + H)
    z.update(top0=z["blkT1"], top1=z["blkT1"] + T_TOP)
    pitch = g.get("rail_pitch", 10)
    f = dict(base=(nA * L + 2 * FL, W + 2 * FL), blkA=(nA * L, W), railA=(nA * L + 2 * P["S_a"] + 2, rW),
             ad=(max(W + 2 * FL, pitch + 4), nT * L + 2 * P["S_t"] + 2), railT=(rW, nT * L + 2 * P["S_t"] + 2),
             blkT=(W, nT * L), top=(W + 2 * FL, nT * L + 2 * FL))
    return g, z, f


# The member-3 BRIDGE strap (8 x 3) runs from the neck end over the moving along rail (member 4, adjacent: 0.5 mm running
# gap) at z_lo = railA1 + 0.5, then climbs at <= 60 deg onto the top plate (underside top0) before the adapter's edge.
# The template formulas of the seed (carriage-B underside zb = tr + RAIL_H + RUN + CAR_H + RUN + R_r = the bridge's low
# underside, the neck's ramp target and the riser top = zb + CAR_H) give that with RAIL_H = z_lo, the rest 0, R_r 0.
_Z = stack(dict(PARAMS, S_a=0, S_t=0))[1]; Z_LO = _Z["railA1"] + 0.5
S.RAIL_H, S.RUN, S.CAR_H = Z_LO, 0.0, 0.0


# ---- the rest pose and its skin (copied from skin-normal-hubs-selfaligning.py, unchanged) ----------------------------
_REST = {}
def rest():
    if not _REST:
        Z = CB._poses_all(); names = list(Z["NAMES"]); held = [names.index(n) for n in ("Wave", "Walking arm swing")]
        ok = np.nonzero(~np.isin(Z["CID"], held))[0]; j = int(ok[np.argmin(Z["POSE"][ok, 1])])
        pose = dict(zip(("plane", "elev", "axial", "flex", "pron"), map(float, Z["POSE"][j])))
        V = np.asarray(BP.posed(pose), float); Fc = np.asarray(BP.F)
        RS0 = Z["RS"][j].astype(float); Q0 = Z["HG"][j].astype(float)
        tri = V[Fc]; fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); cen = tri.mean(1)
        near = np.linalg.norm(cen, axis=1) < 300
        _REST.update(j=j, pose=pose, V=V, RS0=RS0, Q0=Q0, ex=CB._Exact(V), fn=fn[near], cen=cen[near])
    return _REST


def seat(d_scap, beta):
    R = rest(); d = unit(np.asarray(d_scap, float)); dw = R["RS0"] @ d
    rho = np.arange(260.0, 14.0, -0.5); dist = R["ex"](rho[:, None] * dw[None])
    k = int(np.argmax(dist < 2.0)) if (dist < 2.0).any() else len(rho) - 1
    r2 = rho[k] + (2.0 - dist[k]) * 0.5 / max(dist[k - 1] - dist[k], 1e-6) if k > 0 else rho[k]
    k0 = int(np.argmax(dist < 0.0)) if (dist < 0).any() else k
    X = rho[k0] * dw
    m = np.linalg.norm(R["cen"] - X, axis=1) < 10.0
    n = unit(R["fn"][m].sum(0) if m.any() else dw)
    if R["ex"]((X + 3 * n)[None])[0] < R["ex"]((X - 3 * n)[None])[0]: n = -n
    n_s = R["RS0"].T @ n
    u = unit((1 - beta) * d + beta * n_s)
    return r2 * d, u, n_s, float(np.degrees(np.arccos(np.clip(d @ n_s, -1, 1))))


def foot(c, u): return c - (c @ u) * u


class Design(S.Design):
    def __init__(self, params=None):
        P = dict(PARAMS); P.update(params or {}); self.p = P
        for k in ("b1", "b2", "b3"): P[k] = float(min(1.0, max(0.0, P[k])))
        R = rest(); Q0 = R["Q0"]
        P1, d1, n1, t1 = seat(S.bvec(P["az1"], P["el1"]), P["b1"])
        P2, d2, n2, t2 = seat(S.bvec(P["az2"], P["el2"]), P["b2"])
        P3, d3, n3, t3 = seat(Q0 @ S.w_dir(P["wd"], P["wa"]), P["b3"])
        self.seats = dict(P=[P1, P2, P3], d=[d1, d2, d3], tilt_deg=[round(t1, 1), round(t2, 1), round(t3, 1)])
        u1, u3 = d1, unit(Q0.T @ d3)
        A = [math.acos(float(np.clip(d1 @ d2, -1, 1))), math.acos(float(np.clip(d2 @ d3, -1, 1)))]
        self.branch = float(np.sign(d2 @ np.cross(d1, d3)) or 1.0)
        u2 = S.circ_int(u1, A[0], u3, A[1], self.branch)
        self.u = [unit(u1), unit(u2), unit(u3)]; self.A = A; self.h0 = np.array([0.0, -1.0, 0.0])
        self.sn = self.u[2]; self.sa = unit(self.h0 - (self.h0 @ self.sn) * self.sn); self.st = np.cross(self.sn, self.sa)
        self.c = [foot(P1, self.u[0]), np.zeros(3), np.zeros(3)]
        _, _, X1, _, _, _ = self.ik(Q0[None])
        R1, tt1 = X1[0][0], X1[1][0]; self.rest_err = float(np.degrees(np.arccos(np.clip((R1 @ self.u[1]) @ d2, -1, 1))))
        self.c[1] = foot(R1.T @ (P2 - tt1), self.u[1])
        _, _, _, X2, _, _ = self.ik(Q0[None]); R12, tt2 = X2[0][0], X2[1][0]
        self.c[2] = foot(R12.T @ (P3 - tt2), self.u[2])
        self.ea = self.ec = None; self.m = np.zeros(3)

    def stage_c(self):
        """the stage centre at mid travel: the arm-fixed base's near edge S_a + 1 mm past the neck end, so the neck and
        hub 3 never pass over the base (the inverted-guide rule of offset-skin-normal-3r); the bridge strap spans from
        the neck end to the member-3 top plate's near edge (S_a + 1 + (base - plate) / 2 long)"""
        P = self.p; _, _, f = stack(P)
        return self.c[2] + (S.HUB_R + P["neck"] + P["S_a"] + 1.0 + f["base"][0] / 2) * self.sa

    def bridge_len(self):
        P = self.p; _, _, f = stack(P); return P["S_a"] + 1.0 + (f["base"][0] - f["top"][0]) / 2

    def slides_ok(self, s):
        P = self.p; d = s - self.m
        return (np.abs(d[:, 0]) <= P["S_a"]) & (np.abs(d[:, 1]) <= P["S_t"]) & (np.abs(d[:, 2]) <= P["R_l"])


def _put(D, r, z=0.0):
    return D.stage_c()[None] + r[:, :1] * D.sa + r[:, 1:2] * D.st + z * D.sn


class Geometry(S.Geometry):
    """seed Geometry (hubs 1-3, the ramped neck) with the template stage replaced by the real stage's undersides"""
    def __init__(self, D):
        super().__init__(D)
        P = D.p; _, z, f = stack(P); sn = D.sn
        self.groups = [g for g in self.groups if g["name"] not in ("rail", "carA")]
        def grp(name, mem, r, off):
            B = _put(D, r); self.groups.append(dict(name=name, mem=mem, B=B, N=np.broadcast_to(sn, B.shape).copy(), shared="stack",
                                                    off=np.full(len(B), off)))
        grp("base", 5, S.rect(*f["base"]), 0.0)                                     # arm-fixed base plate
        r = S.rect(*f["railA"]); r = r[np.abs(r[:, 0]) > f["base"][0] / 2]           # the moving along rail beyond the base
        if len(r): grp("railA", 4, r, z["railA0"])
        r = S.rect(*f["ad"]); r = r[np.abs(r[:, 1]) > f["railA"][1] / 2]             # adapter plate, off the along rail
        grp("adapter", 4, r, z["ad0"])
        r = S.rect(*f["top"]); r = r[(np.abs(r[:, 0]) > f["blkT"][0] / 2) | (np.abs(r[:, 1]) > f["blkT"][1] / 2)]
        if len(r): grp("plate3", 3, r, z["top0"])                                   # member-3 top plate rim round the block


S.Geometry = Geometry


class Model(S.VModel):
    """the verifier's VModel on this Design, the real stage, R_l = the liner's radial allowance (no radial slide)"""
    def __init__(self, B, params=None, verbose=False):
        self.fix = dict(S.VModel.fix)
        self.B = B; self.D = Design(params); self.p = self.D.p; self.v = verbose
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)
        q, ok, X1, X2, X3, s = self.D.ik(self.Q)
        names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
        _, okc, _, _, _, sc = self.D.ik(Z["HG"][ii].astype(float))
        sv = np.r_[s[ok], sc[okc]]; cap = float(self.p.get("S_max", 25.0))
        if self.p.get("centre") and len(sv): self.D.m = 0.5 * (sv.max(0) + sv.min(0))
        sa = np.abs(sv - self.D.m); mx = sa.max(0) if len(sa) else np.zeros(3)
        self.p["S_a"] = round(min(cap, max(2.0, float(mx[0]) + 0.5)), 1); self.p["S_t"] = round(min(cap, max(2.0, float(mx[1]) + 0.5)), 1)
        self.p["R_l"] = float(min(2.0, self.p.get("R_l", 0.5)))   # user rule: <= 2 mm to the liner
        self.p["R_r"] = 0.0                                      # NO radial slide in the stack
        self.radial_used = round(float(min(mx[2], self.p["R_l"])), 2); self.radial_span = round(float(np.ptp(sv[:, 2])), 3) if len(sv) else 0.0
        self.liner = round(2.5 * self.radial_used, 2) if self.radial_used > 0.5 else 0.0
        self.q, self.X = q, {1: X1, 2: X2, 3: X3}; self.s = s
        self.why = np.array([""] * len(B.idx), dtype=object)
        okf = ok.copy(); self.why[~ok] = "fold"
        sok = self.D.slides_ok(s); self.why[ok & ~sok] = "slide"; okf &= sok
        cont = self.continuity()
        bad_c = okf & ~cont; self.why[bad_c] = "flip"; okf &= cont
        self.kin_ok = okf
        R123 = self.X[3][0]; c = (np.einsum("nij,nij->n", R123, self.Q) - 1) / 2
        self.res_deg = np.degrees(np.arccos(np.clip(c, -1, 1)))
        bad = self.kin_ok & (self.res_deg >= 0.5); self.why[bad] = "closure"; self.kin_ok &= ~bad

    def T(self, m, i):
        """centred stage; the cuff (5) and the along member (4) float radially with the liner (s_n), member 3 is X3"""
        if m in (4, 5):
            Q = self.Q[i]; D = self.D; mm = D.m
            loc = (mm[0] if m == 5 else self.s[i, 0]) * D.sa + mm[1] * D.st + self.s[i, 2] * D.sn
            return Q, Q @ loc
        return super().T(m, i)

    def needed(self, items, poses, iters=16, lift_max=35.0):
        res = super().needed(items, poses, iters, lift_max)
        geo = getattr(self, "geo", None)
        if self.liner > 0 and geo is not None and len(items) == len(geo.groups) and items[0][1] is geo.groups[0]["B"]:
            k = [g["name"] for g in geo.groups].index("base")
            res[k] = res[k] + max(0.0, self.liner - S.CLEAR)   # the liner under the base: lift it (non-metal, not scored)
        return res

    def finalize(self):
        super().finalize()
        D = self.D; P = self.p
        if "bridge" in self.rigid:                                 # the real bridge (VModel builds it S_a long, flat at zb)
            _, z, f = stack(P); L = D.bridge_len(); r = S.rect(L, S.W_LINK); r[:, 0] += S.HUB_R + P["neck"] + L / 2
            u = r[:, 0] - (D.stage_c() - D.c[2]) @ D.sa                 # x relative to the stage centre (< -top/2)
            ue = -max(f["top"][0], f["ad"][0]) / 2                      # at the plate level before it crosses the adapter's edge
            zz = self.tr + np.maximum(Z_LO, z["top0"] - math.tan(S.RAMP * S.D2R) * np.maximum(0.0, ue - u))
            self.rigid["bridge"] = (3, D.c[2][None] + r[:, :1] * D.sa + r[:, 1:] * D.st + zz[:, None] * D.sn[None])

    def _boxes(self):
        """(member, centre, half sizes) in the member-local rest frame, from the fitted stack height"""
        P = self.p; D = self.D; _, z, f = stack(P); tr = self._tr_fit if not hasattr(self, "tr") else self.tr
        cs = D.stage_c(); sn = D.sn
        def bx(m, L, W, z0, z1): return (m, cs + (tr + 0.5 * (z0 + z1)) * sn, np.array([L / 2, W / 2, 0.5 * (z1 - z0)]))
        mem4L = max(f["railA"][0], f["ad"][0])
        return {"rail": bx(5, f["base"][0], f["base"][1], 0.0, z["blkA1"]),
                "carA": bx(4, f["ad"][0], f["ad"][1], z["ad0"], z["ad1"]),           # adapter (the across rail sits under member 3's plate)
                "strip": bx(4, f["railA"][0], f["railA"][1], z["railA0"], z["railA1"]),
                "carA_all": bx(4, mem4L, f["ad"][1], z["railA0"], z["railT1"]),
                "carB": bx(3, f["top"][0], f["top"][1], z["blkT0"], z["top1"])}

    def _boxes_at(self, i):
        Rst = np.stack([self.D.sa, self.D.st, self.D.sn], 1); out = {}
        for nm, src in (("rail", "rail"), ("carA", "carA_all"), ("carB", "carB")):
            m, cen, half = self._boxes()[src]; R, t = self.T(m, i); out[nm] = (R @ cen + t, R @ Rst, half)
        return out

    def _contact_only(self):
        super()._contact_only()
        D = self.D; P = self.p; tr = self.tr; _, z, f = stack(P)
        def box_edges(mem, L, W, z0, z1):
            pts = []
            for zz in (z0, z1):
                for x in np.arange(-L / 2, L / 2 + 1e-6, S.SPACING): pts += [(x, -W / 2, zz), (x, W / 2, zz)]
                for y in np.arange(-W / 2, W / 2 + 1e-6, S.SPACING): pts += [(-L / 2, y, zz), (L / 2, y, zz)]
            a = np.array(pts); return (mem, D.stage_c() + a[:, :1] * D.sa + a[:, 1:2] * D.st + (tr + a[:, 2:]) * D.sn)
        self.contact = self.contact[:-3] + [box_edges(5, *f["base"], 0.0, z["blkA1"]),
                                            box_edges(4, *f["railA"], z["railA0"], z["railA1"]),
                                            box_edges(4, *f["ad"], z["ad0"], z["railT1"]),
                                            box_edges(3, *f["top"], z["blkT0"], z["top1"])]

    def _solids(self):
        super()._solids()
        if not self.box: return
        b = self._boxes(); self.box = {k: b[k] for k in ("rail", "carA", "carB")}; self.box_strip = b["strip"]

    def hub12(self):
        if not hasattr(self, "_h12"):
            D = self.D; u, c = D.u, D.c; C1 = c[0] + self.f[0] * u[0]; C2 = c[1] + self.f[1] * u[1]
            e2, f2 = S.frame_of(u[1]); ang = np.linspace(0, 2 * np.pi, 72, endpoint=False); dd = S.disc(S.HUB_R, 1.0)
            P = np.concatenate([C2 + z * u[1] + S.HUB_R * (np.cos(ang)[:, None] * e2 + np.sin(ang)[:, None] * f2) for z in np.linspace(0, S.CROWN, 13)]
                               + [C2 + z * u[1] + dd[:, :1] * e2 + dd[:, 1:] * f2 for z in (0.0, S.CROWN)])
            self._h12 = float(self.sd_cyl(P, C1, u[0]).min())
        return self._h12

    def collide(self, i):
        m0 = super().collide(i); self.last_clear["hub1-hub2"] = round(self.hub12(), 1); out = [m0, self.hub12()]
        if self.box:                                               # the moving along rail (member 4) vs every non-adjacent part
            D = self.D; Rst = np.stack([D.sa, D.st, D.sn], 1); mb, cen, half = self.box_strip; Rb, tb = self.T(mb, i)
            cw, Rw = Rb @ cen + tb, Rb @ Rst
            def tf(m, P): R, t = self.T(m, i); return P @ R.T + t
            for nm in ("hub1", "hub2", "hub3"):
                m, P = self.cyl_surf[nm]; v = float(self.sd_box(tf(m, P), cw, Rw, half).min()); out.append(v); self.last_clear[f"strip-{nm}"] = round(v, 1)
            for nm in ("L1", "L2"):
                m, P = self.strap[nm]
                if len(P): v = float(self.sd_box(tf(m, P), cw, Rw, half).min()) - S.T_LINK / 2; out.append(v); self.last_clear[f"strip-{nm}"] = round(v, 1)
            if "neck" in self.rigid:
                m, P = self.rigid["neck"]; v = float(self.sd_box(tf(m, P + (S.T_LINK / 2) * D.sn), cw, Rw, half).min()) - S.T_LINK / 2
                out.append(v); self.last_clear["strip-neck"] = round(v, 1)
        return min(out)


def _report(B, params):
    M = Model(B, params); r = M.run(); D = M.D
    r["seats"] = dict(tilt_deg=D.seats["tilt_deg"], a_deg=[round(math.degrees(a), 1) for a in D.A],
                      offset_mm=[round(float(np.linalg.norm(c)), 1) for c in D.c], rest_err_deg=round(D.rest_err, 4))
    g, z, f = stack(M.p)
    r["S"] = [M.p["S_a"], M.p["S_t"]]; r["radial"] = dict(span=M.radial_span, used=M.radial_used, liner=M.liner, allowed=M.p["R_l"])
    r["stage"] = dict(guide=g["id"], nA=M.p["nA"], nT=M.p["nT"], height=round(z["top1"], 2), rail_along=round(f["railA"][0], 1),
                      rail_across=round(f["railT"][1], 1), base=f["base"], top=f["top"])
    r["passive_translations"] = 2
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    return r, M


def evaluate(B, params):
    """tools/concept_cma.py hook: (params, report)"""
    r, M = _report(B, params); p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    """tools/concept_sweep.py hook"""
    r, M = _report(B, params); r.pop("params", None)
    return r


def kin(par):
    """radial drift the 2-slide cuff cannot absorb (fit clips at 10 fps + the bench workspace) vs b1, b2"""
    B = CB.Bench(n_clip=60, n_ws=160); Z = CB._poses_all(); names = list(Z["NAMES"])
    ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
    Q = np.r_[Z["HG"][ii].astype(float), Z["HG"][B.idx].astype(float)]
    for b1, b2 in ((0, 0), (0.02, 0), (0, 0.02), (0.05, 0), (0, 0.05), (0.05, 0.05), (0.1, 0.1), (0.34, 0.42)):
        D = Design(dict(par, b1=b1, b2=b2)); q, ok, _, _, _, s = D.ik(Q); sn = np.sort(s[ok, 2]); n = len(sn)
        def win(w):
            if not n: return 0.0
            j = np.searchsorted(sn, sn + 2 * w, side="right"); return float((j - np.arange(n)).max() / n)
        print(f"b1 {b1:.2f} b2 {b2:.2f} offsets {[round(float(np.linalg.norm(c)), 1) for c in D.c]} poses {n}: radial span "
              f"{sn[-1] - sn[0] if n else 0:.2f} mm, closable +-0.5 {win(0.5):.3f}, +-2 (liner) {win(2.0):.3f}; along/across travel "
              f"{np.ptp(s[ok, 0]):.1f}/{np.ptp(s[ok, 1]):.1f}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "kin": kin(par); sys.exit()
    nc, nw = (110, 360) if mode == "full" else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    r, M = _report(B, par)
    print(json.dumps({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact", "why", "S", "radial", "stage", "f", "seats", "honest")}),
          f"{time.time() - t:.0f}s mode {B.mode if hasattr(B, 'mode') else '?'}")
    print("parts", r["parts_ib14"], r["parts_pairs"], "min clear", r.get("min_clear_taken"), "riser", r.get("riser_h"), "res", r.get("res_max"))
    if mode == "redteam":
        lab = lambda i: f"#{i} {B.kind[i]} {B.clip[i][:22]:22s} plane {B.poses[i]['plane']:6.1f} elev {B.poses[i]['elev']:6.1f} axial {B.poses[i]['axial']:6.1f}"
        print("-- poses not taken --")
        for i in [i for i in range(len(B.idx)) if M.why[i]]:
            print(f"  {M.why[i]:7s} {lab(i)}" + (f" clear {M.clear[i]:.1f} ({M.last_pair.get(i)})" if M.why[i] == "parts" else ""))
        names = list(M.rigid) + list(M.link_pts); sizes = [len(X) for _, X in M.rigid.values()] + [len(X) for _, X in M.link_pts.values()]
        cut = np.cumsum([0] + sizes); low = []
        for i in range(len(B.idx)):
            d = B.res[i]
            if d is None or float(np.min(d)) < 0: continue
            j = int(np.argmin(d[:cut[-1]])); low.append((float(d[j]), i, names[int(np.searchsorted(cut, j, side="right") - 1)]))
        low.sort(); print("-- closest metal over taken poses (the point that pinches) --")
        for dd, i, part in low[:8]: print(f"  {dd:5.2f} mm  {part:7s} {lab(i)}")
        for thr in (1.0, 2.0):
            near = sum(1 for dd, i, part in low if dd < thr); print(f"taken poses with metal < {thr} mm: {near}")
        taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
        el = np.array([p["elev"] for p in B.poses]); pl = np.array([p["plane"] for p in B.poses])
        groups = dict(rest=np.argsort(el)[:5], overhead=np.nonzero(el >= 120)[0], across=np.nonzero((pl >= 100) & (el >= 40))[0],
                      behind=np.array([i for i in range(len(B.idx)) if "back" in B.clip[i].lower() or (pl[i] < -30 and el[i] > 20)], int))
        print("-- named pose groups: taken / total, median metal-skin mm, in band 2-14 --")
        for gname, ii in groups.items():
            ii = list(ii); tk = [i for i in ii if taken(i)]; dd = np.concatenate([B.res[i] for i in tk]) if tk else np.array([np.nan])
            print(f"  {gname:9s} {len(tk)}/{len(ii)}  median {float(np.median(dd)):.1f} mm  ib14 {float(((dd >= 2) & (dd <= 14)).mean()):.3f}  not taken: {[(int(i), M.why[i]) for i in ii if not taken(i)][:8]}")
        print("slide travel used (along, across, radial) max |s - mid|:", [round(float(np.abs(M.s[M.kin_ok][:, k] - M.D.m[k]).max()), 2) for k in range(3)])
