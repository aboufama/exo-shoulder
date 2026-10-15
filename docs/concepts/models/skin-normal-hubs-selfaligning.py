"""Concept model: SKIN-NORMAL HUBS + PASSIVE CUFF TRANSLATION STAGE (non-concurrent 3R), id skin-normal-hubs-selfaligning.

Chain: scapula base -> J1 (O20 hub, active R) -> link 1 -> J2 (O20 hub, active R) -> link 2 -> J3 (O20 hub, active R)
-> member 3 (hub 3 + neck + bridge + across-carriage) -> passive XYZ translation stage (along the humerus, across it,
radial) -> arm-fixed cuff rail (BOTTOM's top).

Each hub axis LINE is placed on a skin seat at the rest pose: through the seat point (2 mm off the skin along the
seat ray from GH) with direction nlerp(seat ray, mean outward skin normal within 10 mm, beta_k). beta 0 = the line
passes through GH (the spherical 3R, concurrent axes), beta 1 = the hub stands square on its seat (the catalogue's
morphology). Seats: J1 and J2 in the scapula frame (bvec az / el), J3 on the arm (wdir d / a, band humerus frame).

Kinematics and every part are the VERIFIED seed-offset-3r-slides model (docs/concepts/models/seed-offset-3r-slides.py,
verifier 2026-10-15: 66.47 on Bench(110, 360)): orientation = the spherical IK of the three axis directions (only
directions matter for orientation), the offsets of the axis lines show up as a pose-dependent drift t3(q) of member 3
that the three passive slides absorb exactly (s = Q^T t3, loop mobility 3 + 3 + 3 - 6 = 3 = the arm's: 3 ACTIVE DOF,
3 PASSIVE DOF, every slide set by closure, none sags). Remote stage (hub 3 + a ramped neck at their own fitted height,
the stage down the arm), S_auto slide ranges (needed travel + 0.5 mm, capped at S_max), jam_contact on, greedy
skin-pose dropping recorded as contact. Fixes the verifier's missing part: the BRIDGE strap of member 3 between the
neck end and the across-carriage (8 mm x S_a, underside at the carriage underside), scored, and checked against the
rail and the along-carriage for >= 1 mm.

The spec's "q = 0 at the rest pose" is kept physically: the design is defined at the rest pose (the lowest-elevation
non-held-out pose of the pose file, independent of the bench size) and mapped to the closure's home frame by the
spherical IK at that pose (u2, c2, c3 = the rest lines pulled back through X1, X2).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/skin-normal-hubs-selfaligning.py [check|seats|redteam <json params>]
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("seed_offset_3r_slides", os.path.join(HERE, "seed-offset-3r-slides.py"))
S = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(S)
BP = CB.BP; unit = S.unit; D2R = math.pi / 180
ID = "skin-normal-hubs-selfaligning"
NAME = "Skin-normal hubs + passive cuff translation stage (non-concurrent 3R)"

# champion spherical 3R (r20 s1414 #4): J1 bvec(2.43, 80.68), J3 wdir(86.33, 21.83); J2 rest seat = its rest-pose axis
CHAMP = dict(az1=2.43, el1=80.68, wd=86.33, wa=21.83)
PARAMS = dict(S.PARAMS)
PARAMS.update(remote=1, ramp=1, neck=5.0, S_auto=1, jam_contact=1, drop=1, slides=1,
              az1=75.0, el1=55.0, b1=1.0,        # J1 seat: spec sdir(55, 15) = bvec(75, 55), skin normal
              az2=-5.0, el2=40.0, b2=1.0,        # J2 home seat: spec sdir(40, 95) = bvec(-5, 40), skin normal
              wd=86.33, wa=21.83, b3=0.0,        # J3: GH-radial hub on the arm (spec), b3 1 = skin normal on the deltoid
              S_max=25.0, bridge=1,             # stage travel cap (mm, each slide); member-3 bridge strap (verifier fix)
              centre=0)                         # 1: each slide range centred on its mid travel (rail / carriages shifted)
SEAT_KEYS = ("az1", "el1", "b1", "az2", "el2", "b2", "wd", "wa", "b3")


# ---- the rest pose and its skin (bench independent) -----------------------------------------------------------------
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
    outward skin normal n within 10 mm (area weighted), the axis direction nlerp(d, n, beta). All in the scapula frame."""
    R = rest(); d = unit(np.asarray(d_scap, float)); dw = R["RS0"] @ d
    rho = np.arange(260.0, 14.0, -0.5); dist = R["ex"](rho[:, None] * dw[None])
    k = int(np.argmax(dist < 2.0)) if (dist < 2.0).any() else len(rho) - 1
    r2 = rho[k] + (2.0 - dist[k]) * 0.5 / max(dist[k - 1] - dist[k], 1e-6) if k > 0 else rho[k]   # dist = 2 crossing
    k0 = int(np.argmax(dist < 0.0)) if (dist < 0).any() else k
    X = rho[k0] * dw                                              # skin hit (thorax frame)
    m = np.linalg.norm(R["cen"] - X, axis=1) < 10.0
    n = R["fn"][m].sum(0) if m.any() else dw
    n = unit(n)
    if R["ex"]((X + 3 * n)[None])[0] < R["ex"]((X - 3 * n)[None])[0]: n = -n   # outward
    n_s = R["RS0"].T @ n
    u = unit((1 - beta) * d + beta * n_s)
    return r2 * d, u, n_s, float(np.degrees(np.arccos(np.clip(d @ n_s, -1, 1))))


def foot(c, u): return c - (c @ u) * u


class Design(S.Design):
    """seed-offset Design with axis directions AND lines from the skin seats (home frame = the closure's Q = I frame)"""
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
        if not P.get("slides", 1):                                  # spherical reference: concurrent lines
            self.c = [np.zeros(3)] * 3
        else:
            self.c = [foot(P1, self.u[0]), np.zeros(3), np.zeros(3)]
            _, _, X1, _, _, _ = self.ik(Q0[None])                    # rest transforms: pull the rest lines back to home
            R1, tt1 = X1[0][0], X1[1][0]; self.rest_err = float(np.degrees(np.arccos(np.clip((R1 @ self.u[1]) @ d2, -1, 1))))
            self.c[1] = foot(R1.T @ (P2 - tt1), self.u[1])
            _, _, _, X2, _, _ = self.ik(Q0[None]); R12, tt2 = X2[0][0], X2[1][0]
            self.c[2] = foot(R12.T @ (P3 - tt2), self.u[2])
        self.ea = self.ec = None; self.m = np.zeros(3)

    def slides_ok(self, s):
        P = self.p; d = s - self.m
        if not P.get("slides", 1): return np.ones(len(s), bool)
        return (np.abs(d[:, 0]) <= P["S_a"]) & (np.abs(d[:, 1]) <= P["S_t"]) & (np.abs(d[:, 2]) <= P["R_r"])


class Model(S.Model):
    def __init__(self, B, params=None, verbose=False):           # = S.Model.__init__ with this Design and the S_max cap
        self.B = B; self.D = Design(params); self.p = self.D.p; self.v = verbose
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)
        q, ok, X1, X2, X3, s = self.D.ik(self.Q)
        if self.p.get("S_auto") and self.p.get("slides", 1):
            names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
            _, okc, _, _, _, sc = self.D.ik(Z["HG"][ii].astype(float))
            sv = np.r_[s[ok], sc[okc]]; cap = float(self.p.get("S_max", 25.0))
            if self.p.get("centre") and len(sv): self.D.m = 0.5 * (sv.max(0) + sv.min(0))   # centred ranges (mid travel)
            sa = np.abs(sv - self.D.m); m = sa.max(0) if len(sa) else np.zeros(3)
            self.p["S_a"] = round(min(cap, max(2.0, float(m[0]) + 0.5)), 1); self.p["S_t"] = round(min(cap, max(2.0, float(m[1]) + 0.5)), 1)
            self.p["R_r"] = round(min(cap, max(0.5, float(m[2]) + 0.5)), 1)
        self.q, self.X = q, {1: X1, 2: X2, 3: X3}; self.s = s
        self.why = np.array([""] * len(B.idx), dtype=object)
        okf = ok.copy(); self.why[~ok] = "fold"
        sok = self.D.slides_ok(s); self.why[ok & ~sok] = "slide"; okf &= sok
        cont = self.continuity()
        bad_c = okf & ~cont; self.why[bad_c] = "flip"; okf &= cont
        self.kin_ok = okf

    def T(self, m, i):
        """member transforms; centred stage: the arm-fixed rail (5) and the along-carriage (4) sit at the mid travel D.m"""
        if m in (4, 5) and self.D.m.any():
            Q = self.Q[i]; D = self.D; mm = D.m
            loc = (mm[0] if m == 5 else self.s[i, 0]) * D.sa + mm[1] * D.st + mm[2] * D.sn
            return Q, Q @ loc
        return super().T(m, i)

    def finalize(self):
        super().finalize()
        D = self.D; P = D.p
        if P.get("bridge", 1) and P.get("remote") and P.get("slides", 1) and P["S_a"] > 0:   # verifier's missing part
            L = P["S_a"]; r = S.rect(L, S.W_LINK); r[:, 0] += S.HUB_R + P["neck"] + L / 2
            Bb = D.c[2][None] + r[:, :1] * D.sa + r[:, 1:] * D.st + self.zb * D.sn
            self.rigid["bridge"] = (3, Bb)
            self.bridge_pts = Bb + (S.T_LINK / 2) * D.sn

    def collide(self, i):
        m0 = super().collide(i)
        if not hasattr(self, "bridge_pts") or not self.box: return m0
        R, t = self.T(3, i); Pb = self.bridge_pts @ R.T + t; Rst = np.stack([self.D.sa, self.D.st, self.D.sn], 1); out = []
        for b in ("rail", "carA"):
            m, cen, half = self.box[b]; Rb, tb = self.T(m, i)
            out.append(float(self.sd_box(Pb, Rb @ cen + tb, Rb @ Rst, half).min()) - S.T_LINK / 2)
        self.last_clear.update({"bridge-rail": round(out[0], 1), "bridge-carA": round(out[1], 1)})
        return min([m0] + out)


def evaluate(B, params):
    M = Model(B, params); r = M.run(); r["params"] = dict(M.p)
    D = M.D; r["seats"] = dict(tilt_deg=D.seats["tilt_deg"], a_deg=[round(math.degrees(a), 1) for a in D.A],
                               offset_mm=[round(float(np.linalg.norm(c)), 1) for c in D.c], rest_err_deg=round(getattr(D, "rest_err", 0.0), 4))
    return r, M


def bench_eval(B, params):
    """tools/concept_sweep.py hook"""
    r, M = evaluate(B, params)
    r.pop("params", None); r["S"] = [M.p["S_a"], M.p["S_t"], M.p["R_r"]]
    return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "seats":
        D = Design(par); print("tilt (deg between seat ray and skin normal)", D.seats["tilt_deg"], "a", [round(math.degrees(a), 1) for a in D.A],
                              "offsets", [round(float(np.linalg.norm(c)), 1) for c in D.c], "rest err", getattr(D, "rest_err", None))
        sys.exit()
    if mode == "redteam":                                         # the pose that jams, the point that pinches, named groups
        B = CB.Bench(n_clip=60, n_ws=160); r, M = evaluate(B, par)
        print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "S", [M.p["S_a"], M.p["S_t"], M.p["R_r"]], "f", r["f"], r["seats"])
        print("parts in band 2-14 [share, median mm, samples]:", r["parts_ib14"]); print("reasons not taken:", r["why"], r["parts_pairs"])
        print("slide travel max |s| over the poses kept (along, across, radial):", r["s_abs_max"])
        lab = lambda i: f"#{i} {B.kind[i]} {B.clip[i][:22]:22s} plane {B.poses[i]['plane']:6.1f} elev {B.poses[i]['elev']:6.1f} axial {B.poses[i]['axial']:6.1f}"
        print("-- poses not taken (first 25) --")
        for i in [i for i in range(len(B.idx)) if M.why[i]][:25]:
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
        print("-- hub 2 face: poses that set it (needed face height mm) --")
        for a in top: print(f"  {H2[a].max():6.1f}  {lab(int(M.poses_fit[a]))}  dropped {bool(M.drop[a])}")
        print("  median need over kept poses", round(float(np.median(H2[~M.drop].max(1))), 1), "fitted", round(M.f[1], 1))
        if "--png" in sys.argv: S.ID = ID; S.sketch(M, os.path.join(REPO, "docs", "concepts", "img", ID + ".png")); print("sketch written")
        sys.exit()
    nc, nw = (20, 40) if mode == "quick" else (60, 160)
    B = CB.Bench(n_clip=nc, n_ws=nw); t = time.time()
    r, M = evaluate(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], "S", [M.p["S_a"], M.p["S_t"], M.p["R_r"]],
          "f", r["f"], "seats", r["seats"], f"{time.time() - t:.0f}s")
    print("parts", r["parts_ib14"], r["parts_pairs"])
