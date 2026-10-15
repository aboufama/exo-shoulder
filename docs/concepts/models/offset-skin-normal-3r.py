"""Concept model: NON-CONCURRENT 3R ON SKIN-NORMAL HUBS + a 2-SLIDE PASSIVE CUFF (id offset-skin-normal-3r).

Chain: scapula base -> J1 (O20 hub, active R) -> link 1 -> J2 (O20 hub, active R) -> link 2 -> J3 (O20 hub, active R,
axis = the local skin normal of its seat on the arm, its line misses GH) -> member 3 (hub 3 + neck + riser + bridge +
across-carriage) -> TWO passive rolling slides (along the humerus, across the arm; both in hub 3's plane) -> arm-fixed
cuff rail (BOTTOM's top). 3 ACTIVE DOF, 2 PASSIVE DOF; loop mobility 3 + 2 + 3 - 6 = 2 in general, = 3 on the exact
subfamily below (the slides are then set by closure, none sags: R17).

SPEC CORRECTION (proved here, measured in `kin` mode). The catalogue entry puts all three hubs on skin-normal axes that
miss GH and absorbs the mismatch e with 2 slides, the radial part "<= 3 mm by design". With translations only, the end
link is X(x) = R x + t(q), t = (I-R1)c1 + R1(I-R2)c2 + R1R2(I-R3)c3 (c_k a point of line k, R = R1R2R3 = the arm's
rotation, exact by the spherical IK of the axis DIRECTIONS). Two slides spanning the plane normal to an arm-fixed n
close iff (R n).t = 0 for every arm orientation. Term 3 gives n.(R3^T - I)c3 = 0 for all q3 -> n = d3 (or c3 on d3).
Term 2 gives c2.(R2 - I)R3 n = 0 for all q2, q3 -> c2 parallel to d2: line 2 through GH. Term 1 likewise -> line 1
through GH. So the 2-slide cuff closes EXACTLY iff lines 1 and 2 pass through GH and the slide plane is hub 3's plane;
line 3 is free (its position and its skin-normal tilt). A 3 mm radial residual is not a closure (honesty rule:
< 0.5 mm) - it would be 3 mm of skin compression under the cuff at every pose. The model therefore builds the exact
subfamily: J1 and J2 on seats whose axis is the GH ray (b1 = b2 = 0, they can still be swept as small tilts: any pose
whose radial drift exceeds the 0.5 mm closure tolerance is NOT taken), J3 on a skin seat with its axis tilted toward
the local skin normal by b3 (b3 = 1: square on the skin). The radial slide of the 3-slide relatives
(seed-offset-3r-slides, skin-normal-hubs-selfaligning) is absent: R_r is fixed at the 0.5 mm closure tolerance.

Built on the VERIFIED seed-offset-3r-slides model (docs/concepts/models/seed-offset-3r-slides.py): its VModel (the
verifier's checks: rotation closure < 0.5 deg, hub 3 / bridge vs rail and carriage A, carriage B vs rail, the member-3
riser and bridge, jam rule) and its parts at real size (O20 x 12.25 hubs, 8 x 3 straps with skin-fitted undersides and
<= 60 deg ramps, rail 8 x 4, carriages 20 x 20(+2 S) x 4, 0.5 running gaps, 2 mm sample grid). The seat geometry
(rest pose, outward skin normal at a seat, line pulled back to the home frame) follows
docs/concepts/models/skin-normal-hubs-selfaligning.py (copied, not imported: that file is live in another track).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/offset-skin-normal-3r.py [check|kin|redteam] ['<json params>']
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("seed_offset_3r_slides", os.path.join(HERE, "seed-offset-3r-slides.py"))
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)
BP = CB.BP; unit = S.unit
ID = "offset-skin-normal-3r"
NAME = "Non-concurrent 3R on skin-normal hubs with a passive self-aligning cuff (2 slides)"

PARAMS = dict(S.PARAMS)
PARAMS.update(remote=1, ramp=1, neck=13.0, S_auto=1, jam_contact=1, drop=1, slides=1, vfix=1,
              az1=94.6, el1=60.7, b1=0.0,       # J1 seat on the dome (scapula frame bvec); b1 0 = axis on the GH ray (exact)
              az2=24.1, el2=48.5, b2=0.0,       # J2 home seat (posterior acromion / deltoid); b2 0 = exact
              wd=75.2, wa=-13.0, b3=0.6,        # J3 seat on the arm (band humerus frame w_dir), axis tilted to the skin normal by b3
              S_max=25.0, centre=1,             # slide travel cap (mm each); ranges centred on the mid travel
              R_tol=0.5,                        # the radial (hub-3 normal) closure tolerance = the honesty rule; NO radial slide
              inv=1)                            # 1: INVERTED along-guide - its short carriage is fixed on the cuff and its rail
                                                #    rides with carriage A (member 4), so nothing arm-fixed reaches under the neck

# ---- the rest pose and its skin (bench independent; as skin-normal-hubs-selfaligning.py) ------------------------------
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
    """seat on the rest skin along the scapula-frame ray d from GH: point P (2 mm off the outermost skin), the mean
    outward skin normal n within 10 mm (area weighted), the axis direction nlerp(d, n, beta) (scapula frame)"""
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

    def slides_ok(self, s):
        P = self.p; d = s - self.m
        return (np.abs(d[:, 0]) <= P["S_a"]) & (np.abs(d[:, 1]) <= P["S_t"]) & (np.abs(d[:, 2]) <= P["R_r"])


class Geometry(S.Geometry):
    """inv=1: the along-guide upside down. Arm-fixed (member 5) = the guide's carriage, a CAR_L x CAR_W x RAIL_H block at
    the stage centre (mid travel); member 4 = carriage A + the along rail (RAIL_W x CAR_L + 2 S_a, overhanging carriage A
    along the arm) in one layer at RAIL_H + RUN. Same stack height as the seed's stage. The rail's proximal end stays at
    the neck end (it follows member 3 along the arm), the arm-fixed block never comes nearer than the neck end + 0, so the
    member-3 neck and hub 3 never pass over arm-fixed metal (the seed's neck-rail / hub3-rail jams, measured here: 55-103
    poses with the arm-fixed long rail)."""
    def __init__(self, D):
        super().__init__(D)
        P = D.p
        if not (P.get("inv") and P.get("slides", 1)): return
        cs = D.stage_c(); sa, st, sn = D.sa, D.st, D.sn; Sa, St = P["S_a"], P["S_t"]
        g = {x["name"]: x for x in self.groups}
        def put(r): return cs[None] + r[:, :1] * sa + r[:, 1:] * st
        Bb = put(S.rect(S.CAR_L, S.CAR_W)); g["rail"].update(B=Bb, N=np.broadcast_to(sn, Bb.shape).copy(), off=np.zeros(len(Bb)))
        Bc = put(S.rect(S.CAR_L, S.CAR_W + 2 * St)); g["carA"].update(B=Bc, N=np.broadcast_to(sn, Bc.shape).copy(), off=np.full(len(Bc), S.RAIL_H + S.RUN))
        r = S.rect(S.CAR_L + 2 * Sa, S.RAIL_W); r = r[np.abs(r[:, 0]) > S.CAR_L / 2]
        if len(r):
            Br = put(r); self.groups.append(dict(name="strip", mem=4, B=Br, N=np.broadcast_to(sn, Br.shape).copy(), shared="stack",
                                                 off=np.full(len(Br), S.RAIL_H + S.RUN)))


S.Geometry = Geometry          # this module's private copy of the seed model builds the inverted stage when inv=1


class Model(S.VModel):
    """S.VModel (the verifier's checks) on this Design; R_r is the closure tolerance (no radial slide)"""
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
        self.p["R_r"] = float(self.p.get("R_tol", 0.5))           # no radial slide: the closure tolerance only
        self.radial_span = round(float(sv[:, 2].max() - sv[:, 2].min()), 3) if len(sv) else 0.0
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
        """centred stage: the arm-fixed rail (5) and the along-carriage (4) sit at the mid travel D.m"""
        if m in (4, 5) and self.D.m.any():
            Q = self.Q[i]; D = self.D; mm = D.m
            loc = (mm[0] if m == 5 else self.s[i, 0]) * D.sa + mm[1] * D.st + mm[2] * D.sn
            return Q, Q @ loc
        return super().T(m, i)

    def _inv(self): return bool(self.p.get("inv")) and bool(self.p.get("slides", 1))

    def _boxes_at(self, i):
        out = super()._boxes_at(i)
        if not self._inv(): return out
        D = self.D; P = D.p; tr = self._tr_fit; cs = D.stage_c(); sn = D.sn; Rst = np.stack([D.sa, D.st, sn], 1)
        spec = {"rail": (5, cs + (tr + S.RAIL_H / 2) * sn, np.array([S.CAR_L / 2, S.CAR_W / 2, S.RAIL_H / 2])),
                "carA": (4, cs + (tr + S.RAIL_H + S.RUN + S.CAR_H / 2) * sn, np.array([S.CAR_L / 2 + P["S_a"], (S.CAR_W + 2 * P["S_t"]) / 2, S.CAR_H / 2]))}
        for nm, (m, cen, half) in spec.items():                     # carA here = the bounding box of carriage A + the rail (link 2 avoids it)
            R, t = self.T(m, i); out[nm] = (R @ cen + t, R @ Rst, half)
        return out

    def _contact_only(self):
        super()._contact_only()
        if not self._inv(): return
        D = self.D; P = D.p; tr = self.tr; sa, st, sn = D.sa, D.st, D.sn
        def box_edges(mem, L, W, z0, z1):
            pts = []
            for z in (z0, z1):
                for x in np.arange(-L / 2, L / 2 + 1e-6, S.SPACING): pts += [(x, -W / 2, z), (x, W / 2, z)]
                for y in np.arange(-W / 2, W / 2 + 1e-6, S.SPACING): pts += [(-L / 2, y, z), (L / 2, y, z)]
            a = np.array(pts); return (mem, D.stage_c() + a[:, :1] * sa + a[:, 1:2] * st + a[:, 2:] * sn)
        z1 = tr + S.RAIL_H + S.RUN
        self.contact = self.contact[:-3] + [box_edges(5, S.CAR_L, S.CAR_W, tr, tr + S.RAIL_H),
                                            box_edges(4, S.CAR_L, S.CAR_W + 2 * P["S_t"], z1, z1 + S.CAR_H),
                                            box_edges(4, S.CAR_L + 2 * P["S_a"], S.RAIL_W, z1, z1 + S.CAR_H),
                                            box_edges(3, S.CAR_L, S.CAR_W, self.zb, self.zb + S.CAR_H)]

    def _solids(self):
        super()._solids()
        if not self._inv() or not self.box: return
        D = self.D; P = D.p; tr = self.tr; cs = D.stage_c(); sn = D.sn
        self.box["rail"] = (5, cs + (tr + S.RAIL_H / 2) * sn, np.array([S.CAR_L / 2, S.CAR_W / 2, S.RAIL_H / 2]))
        self.box_strip = (4, cs + (tr + S.RAIL_H + S.RUN + S.CAR_H / 2) * sn, np.array([S.CAR_L / 2 + P["S_a"], S.RAIL_W / 2, S.CAR_H / 2]))

    def hub12(self):
        """hub 1 vs hub 2 cylinders (both in member 1: one static check)"""
        if not hasattr(self, "_h12"):
            D = self.D; u, c = D.u, D.c; C1 = c[0] + self.f[0] * u[0]; C2 = c[1] + self.f[1] * u[1]
            e2, f2 = S.frame_of(u[1]); ang = np.linspace(0, 2 * np.pi, 72, endpoint=False); dd = S.disc(S.HUB_R, 1.0)
            P = np.concatenate([C2 + z * u[1] + S.HUB_R * (np.cos(ang)[:, None] * e2 + np.sin(ang)[:, None] * f2) for z in np.linspace(0, S.CROWN, 13)]
                               + [C2 + z * u[1] + dd[:, :1] * e2 + dd[:, 1:] * f2 for z in (0.0, S.CROWN)])
            self._h12 = float(self.sd_cyl(P, C1, u[0]).min())
        return self._h12

    def collide(self, i):
        m0 = super().collide(i); self.last_clear["hub1-hub2"] = round(self.hub12(), 1); out = [m0, self.hub12()]
        if self._inv() and self.box:                                  # the moving along-rail (member 4) vs every non-adjacent part
            D = self.D; Rst = np.stack([D.sa, D.st, D.sn], 1); mb, cen, half = self.box_strip; Rb, tb = self.T(mb, i)
            cw, Rw = Rb @ cen + tb, Rb @ Rst
            def tf(m, P): R, t = self.T(m, i); return P @ R.T + t
            for nm in ("hub1", "hub2"):
                m, P = self.cyl_surf[nm]; v = float(self.sd_box(tf(m, P), cw, Rw, half).min()); out.append(v); self.last_clear[f"strip-{nm}"] = round(v, 1)
            for nm in ("L1", "L2"):
                m, P = self.strap[nm]
                if len(P): v = float(self.sd_box(tf(m, P), cw, Rw, half).min()) - S.T_LINK / 2; out.append(v); self.last_clear[f"strip-{nm}"] = round(v, 1)
        return min(out)


def _report(B, params):
    M = Model(B, params); r = M.run(); D = M.D
    r["seats"] = dict(tilt_deg=D.seats["tilt_deg"], a_deg=[round(math.degrees(a), 1) for a in D.A],
                      offset_mm=[round(float(np.linalg.norm(c)), 1) for c in D.c], rest_err_deg=round(D.rest_err, 4))
    r["S"] = [M.p["S_a"], M.p["S_t"], M.p["R_r"]]; r["radial_span"] = M.radial_span
    r["honest"] = bool(M.p.get("jam_contact")) and all(M.fix.values())
    r["checks"] = dict(fix=M.fix, jam_contact=M.p.get("jam_contact"), closure_deg=0.5, radial_mm=M.p["R_r"], cont="10 fps clips, 25 deg")
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
    """the theorem on data: radial (hub-3 normal) drift the 2-slide cuff cannot absorb, over the fit clips at 10 fps +
    the bench workspace, for the spec's all-skin-normal hubs and for the exact subfamily"""
    B = CB.Bench(n_clip=60, n_ws=160); Z = CB._poses_all(); names = list(Z["NAMES"])
    ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
    Q = np.r_[Z["HG"][ii].astype(float), Z["HG"][B.idx].astype(float)]
    for lab, b in (("spec: all skin-normal (b 1,1,1)", (1, 1, 1)), ("half tilt (b .5,.5,.5)", (.5, .5, .5)),
                   ("b1 .1 only", (.1, 0, 0)), ("exact subfamily (b 0,0,1)", (0, 0, 1)), ("exact (b 0,0,.6)", (0, 0, .6))):
        D = Design(dict(par, b1=b[0], b2=b[1], b3=b[2])); q, ok, _, _, _, s = D.ik(Q); sn = np.sort(s[ok, 2]); n = len(sn)
        def win(w):
            if not n: return 0.0
            j = np.searchsorted(sn, sn + 2 * w, side="right"); return float((j - np.arange(n)).max() / n)
        print(f"{lab:34s} offsets {[round(float(np.linalg.norm(c)), 1) for c in D.c]} tilt {D.seats['tilt_deg']} poses {n}: "
              f"radial drift span {sn[-1] - sn[0] if n else 0:.2f} mm; share closable +-0.5 mm {win(0.5):.3f}, +-3 mm {win(3.0):.3f}; "
              f"along/across travel {np.ptp(s[ok, 0]):.1f}/{np.ptp(s[ok, 1]):.1f} mm")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "kin": kin(par); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], "S", r["S"],
          "radial span", r["radial_span"], "f", r["f"], "seats", r["seats"], f"{time.time() - t:.0f}s")
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
        for dd, i, part in low[:6]: print(f"  {dd:5.2f} mm  {part:6s} {lab(i)}")
        taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
        el = np.array([p["elev"] for p in B.poses]); pl = np.array([p["plane"] for p in B.poses])
        groups = dict(rest=np.argsort(el)[:5], overhead=np.nonzero(el >= 120)[0], across=np.nonzero((pl >= 100) & (el >= 40))[0],
                      behind=np.array([i for i in range(len(B.idx)) if "back" in B.clip[i].lower() or (pl[i] < -30 and el[i] > 20)], int))
        print("-- named pose groups: taken / total, median metal-skin mm, in band 2-14 --")
        for g, ii in groups.items():
            ii = list(ii); tk = [i for i in ii if taken(i)]; dd = np.concatenate([B.res[i] for i in tk]) if tk else np.array([np.nan])
            print(f"  {g:9s} {len(tk)}/{len(ii)}  median {float(np.median(dd)):.1f} mm  ib14 {float(((dd >= 2) & (dd <= 14)).mean()):.3f}  not taken: {[(int(i), M.why[i]) for i in ii if not taken(i)][:8]}")
        H2 = M.Hneed["hub2"]; top = np.argsort(-H2.max(1))[:5]
        print("-- hub 2 face: poses that set it --")
        for a in top: print(f"  {H2[a].max():6.1f}  {lab(int(M.poses_fit[a]))}  dropped {bool(M.drop[a])}")
        print("slide travel used (along, across, radial) max |s - mid|:", [round(float(np.abs(M.s[M.kin_ok][:, k] - M.D.m[k]).max()), 1) for k in range(3)])
        if "--png" in sys.argv:
            S.ID = ID; S.sketch(M, os.path.join(REPO, "docs", "concepts", "img", ID + ".png")); print("sketch written")
