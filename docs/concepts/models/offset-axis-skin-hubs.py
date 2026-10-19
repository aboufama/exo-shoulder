"""Concept model: OFF-SPHERE SKIN HUBS + PASSIVE CUFF STAGE (axis directions spherical, axis lines free), id offset-axis-skin-hubs.

Chain: scapula base -> J1 (O20 hub, active R) -> link 1 -> J2 (O20 hub, active R) -> link 2 -> J3 (O20 hub, active R)
-> member 3 (hub 3 + ramped neck + riser + bridge + across-carriage) -> passive XYZ translation stage (along the
humerus, across it, radial) -> arm-fixed cuff rail (BOTTOM's top, the user's cuff).

What is new against its relatives: each axis LINE is free - direction d_k (scapula frame at the rest pose; J1 bvec(az1,
el1), J2 bvec(az2, el2) at rest, J3 wdir(wd, wa) in the band humerus frame) AND a free 2-D offset o_k (mm, perpendicular
to d_k, in frame_of(d_k) at the rest pose, up to 30 mm each). The hub sits on its own line wherever the skin is (its
face height along the line is fitted, 2 mm off the skin over every pose taken). The family CONTAINS
  * skin-normal-hubs-selfaligning (lines through skin seats tilted by beta: a 1-D offset per hub, tied to the normal),
  * seed-offset-3r-slides (champion directions + small offsets),
  * the spherical 3R (all offsets 0, `slides` 0),
so the sweep starts from the best of them and can only lose to them by measurement. `pin1` 1 keeps the J1 line
through GH (offsets at J2 / J3 only). `neck` sets the stage station down the arm (the spec's cuff attach point Pc:
hub-3 rim + neck + S_a).

Kinematics and parts = the VERIFIED seed-offset-3r-slides model with ALL the verifier's checks (VModel: closure residual
< 0.5 deg, hub 3 / bridge vs rail and carriage A, carriage B vs rail, the member-3 bridge strap, dropped-and-jammed poses
never taken, the member-3 RISER) + skin-normal-hubs-selfaligning's centred stage and hub 1 / hub 2 check. Orientation =
the spherical IK of the three axis DIRECTIONS (q, branches and the J2 fold are the spherical chain's), the line offsets
give a pose-dependent drift t3(q) of member 3 that the three passive slides absorb exactly (s = Q^T t3). Loop mobility
3 + 3 + 3 - 6 = 3 = the arm's: 3 ACTIVE DOF, 3 PASSIVE DOF, every slide set by closure, none sags (R17).
Spec correction (measured by both relatives, kept): the passive stage needs 3 translations (along, across, radial),
not 1 along + 2 transverse in a plane - with non-concurrent lines the drift has a radial component. The spec's travel
budgets (along +-40, transverse +-8) are the S_max cap per slide.

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/offset-axis-skin-hubs.py [check|k722|redteam] '<json params>'
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402
_spec = importlib.util.spec_from_file_location("skin_normal_hubs_selfaligning", os.path.join(HERE, "skin-normal-hubs-selfaligning.py"))
SN = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SN)
S = SN.S; unit = S.unit; D2R = math.pi / 180
ID = "offset-axis-skin-hubs"
NAME = "Off-sphere skin hubs + passive cuff stage (axis directions spherical, axis lines free)"

# best 3R-family layout so far (skin-normal-hubs-selfaligning k 722) re-expressed as direction + free offset
# (computed by `k722` mode from that model's seats; reproduces its lines to 1e-9)
PARAMS = dict(SN.PARAMS)
PARAMS.update(remote=1, ramp=1, neck=5.0, S_auto=1, jam_contact=1, drop=1, slides=1, centre=1, S_max=21.22, bridge=0,
              az1=108.7248, el1=62.147, az2=32.3489, el2=53.7198, wd=80.7871, wa=-11.2591,
              o1x=-4.5545, o1y=-2.3172, o2x=-6.0912, o2y=2.3828, o3x=-5.8372, o3y=4.0874, pin1=0, riser=1)
O_MAX = 30.0


def b_inv(d):
    """bvec(az, el) inverse (scapula frame)"""
    d = unit(d); return math.degrees(math.atan2(d[2], -d[0])), math.degrees(math.asin(float(np.clip(d[1], -1, 1))))


def w_inv(d):
    """w_dir(d, az) inverse (band humerus frame)"""
    d = unit(d); return math.degrees(math.acos(float(np.clip(-d[1], -1, 1)))), math.degrees(math.atan2(d[0], d[2]))


def foot(c, u): return c - (c @ u) * u


class Design(SN.Design):
    def __init__(self, params=None):
        P = dict(PARAMS); P.update(params or {}); self.p = P
        R = SN.rest(); Q0 = R["Q0"]
        d1 = unit(S.bvec(P["az1"], P["el1"])); d2 = unit(S.bvec(P["az2"], P["el2"])); d3 = unit(Q0 @ S.w_dir(P["wd"], P["wa"]))
        off = []
        for k, d in enumerate((d1, d2, d3)):
            e, f = S.frame_of(d); ox, oy = P[f"o{k + 1}x"], P[f"o{k + 1}y"]
            if k == 0 and P.get("pin1"): ox = oy = 0.0
            off.append(ox * e + oy * f)
        self.seats = dict(P=off, d=[d1, d2, d3], tilt_deg=[0.0, 0.0, 0.0])
        u1, u3 = d1, unit(Q0.T @ d3)
        A = [math.acos(float(np.clip(d1 @ d2, -1, 1))), math.acos(float(np.clip(d2 @ d3, -1, 1)))]
        self.branch = float(np.sign(d2 @ np.cross(d1, d3)) or 1.0)
        u2 = S.circ_int(u1, A[0], u3, A[1], self.branch)
        self.u = [unit(u1), unit(u2), unit(u3)]; self.A = A; self.h0 = np.array([0.0, -1.0, 0.0])
        self.sn = self.u[2]; self.sa = unit(self.h0 - (self.h0 @ self.sn) * self.sn); self.st = np.cross(self.sn, self.sa)
        if not P.get("slides", 1):
            self.c = [np.zeros(3)] * 3
        else:                                                         # rest lines -> the closure's home frame (as SN)
            self.c = [foot(off[0], self.u[0]), np.zeros(3), np.zeros(3)]
            _, _, X1, _, _, _ = self.ik(Q0[None]); R1, tt1 = X1[0][0], X1[1][0]
            self.rest_err = float(np.degrees(np.arccos(np.clip((R1 @ self.u[1]) @ d2, -1, 1))))
            self.c[1] = foot(R1.T @ (off[1] - tt1), self.u[1])
            _, _, _, X2, _, _ = self.ik(Q0[None]); R12, tt2 = X2[0][0], X2[1][0]
            self.c[2] = foot(R12.T @ (off[2] - tt2), self.u[2])
        self.ea = self.ec = None; self.m = np.zeros(3)


class Model(SN.Model, S.VModel):
    """SN.Model (centred stage, S_max, hub 1 / hub 2) with this Design and the verifier's VModel checks (riser etc.)"""
    fix = dict(S.VModel.fix)
    ADJ = S.VModel.ADJ

    def __init__(self, B, params=None, verbose=False):
        P = dict(PARAMS); P.update(params or {})
        if not P.get("riser", 1): self.fix = dict(self.fix, riser=False)
        self.B = B; self.D = Design(P); self.p = self.D.p; self.v = verbose
        Z = CB._poses_all(); self.Z = Z
        self.RS = Z["RS"][B.idx].astype(float); self.Q = Z["HG"][B.idx].astype(float)
        q, ok, X1, X2, X3, s = self.D.ik(self.Q)
        if self.p.get("S_auto") and self.p.get("slides", 1):           # = SN.Model.__init__ (needed travel + 0.5, capped)
            names = list(Z["NAMES"]); ii = np.nonzero(np.isin(Z["CID"], [names.index(n) for n in CB.FIT]))[0]
            _, okc, _, _, _, sc = self.D.ik(Z["HG"][ii].astype(float))
            sv = np.r_[s[ok], sc[okc]]; cap = float(self.p.get("S_max", 25.0))
            if self.p.get("centre") and len(sv): self.D.m = 0.5 * (sv.max(0) + sv.min(0))
            sa = np.abs(sv - self.D.m); m = sa.max(0) if len(sa) else np.zeros(3)
            self.p["S_a"] = round(min(cap, max(2.0, float(m[0]) + 0.5)), 1); self.p["S_t"] = round(min(cap, max(2.0, float(m[1]) + 0.5)), 1)
            self.p["R_r"] = round(min(cap, max(0.5, float(m[2]) + 0.5)), 1)
        self.q, self.X = q, {1: X1, 2: X2, 3: X3}; self.s = s
        self.why = np.array([""] * len(B.idx), dtype=object)
        okf = ok.copy(); self.why[~ok] = "fold"
        sok = self.D.slides_ok(s); self.why[ok & ~sok] = "slide"; okf &= sok
        cont = self.continuity(); bad_c = okf & ~cont; self.why[bad_c] = "flip"; okf &= cont
        self.kin_ok = okf
        R123 = self.X[3][0]; c = (np.einsum("nij,nij->n", R123, self.Q) - 1) / 2       # VModel: closure residual
        self.res_deg = np.degrees(np.arccos(np.clip(c, -1, 1)))
        bad = self.kin_ok & (self.res_deg >= 0.5); self.why[bad] = "closure"; self.kin_ok &= ~bad

    # finalize / collide / run: MRO Model -> SN.Model -> S.VModel -> S.Model, so SN adds its hub 1 / hub 2 check on top
    # of the VModel checks (bridge + riser + hub3/bridge/carB vs rail and carriage A + jam rule); SN's own bridge is off


def evaluate(B, params):
    M = Model(B, params); r = M.run(); r["params"] = dict(M.p)
    D = M.D; r["lines"] = dict(a_deg=[round(math.degrees(a), 1) for a in D.A], offset_mm=[round(float(np.linalg.norm(c)), 1) for c in D.c],
                               rest_err_deg=round(getattr(D, "rest_err", 0.0), 4))
    return r, M


def bench_eval(B, params):
    """tools/concept_sweep.py hook (farm)"""
    P = dict(PARAMS); P.update(params)
    for k in ("o1x", "o1y", "o2x", "o2y", "o3x", "o3y"): P[k] = float(np.clip(P.get(k, 0.0), -O_MAX, O_MAX))
    r, M = evaluate(B, P)
    r.pop("params", None); r["S"] = [M.p["S_a"], M.p["S_t"], M.p["R_r"]]; r["riser_h"] = getattr(M, "riser_h", None)
    return r


def from_sn(snp):
    """skin-normal-hubs-selfaligning params -> this model's (same lines: direction + rest-frame perpendicular offset)"""
    D = SN.Design(snp); Pp, dd = D.seats["P"], D.seats["d"]; out = {}
    out["az1"], out["el1"] = b_inv(dd[0]); out["az2"], out["el2"] = b_inv(dd[1])
    out["wd"], out["wa"] = w_inv(SN.rest()["Q0"].T @ dd[2])
    for k in range(3):
        d = unit(dd[k]); o = foot(np.asarray(Pp[k], float), d); e, f = S.frame_of(d)
        out[f"o{k + 1}x"], out[f"o{k + 1}y"] = float(o @ e), float(o @ f)
    for k in ("S_max", "centre", "neck"):
        if k in snp: out[k] = snp[k]
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}, D


def from_seed(sp):
    """seed-offset-3r-slides params (home-frame lines) -> this model's rest-frame direction + offset"""
    D = S.Design(sp); Q0 = SN.rest()["Q0"]; _, _, X1, X2, _, _ = D.ik(Q0[None])
    R1, t1 = X1[0][0], X1[1][0]; R12, t2 = X2[0][0], X2[1][0]
    dd = [D.u[0], R1 @ D.u[1], R12 @ D.u[2]]; cc = [D.c[0], R1 @ D.c[1] + t1, R12 @ D.c[2] + t2]
    out = {}; out["az1"], out["el1"] = b_inv(dd[0]); out["az2"], out["el2"] = b_inv(dd[1]); out["wd"], out["wa"] = w_inv(Q0.T @ dd[2])
    for k in range(3):
        d = unit(dd[k]); o = foot(np.asarray(cc[k], float), d); e, f = S.frame_of(d)
        out[f"o{k + 1}x"], out[f"o{k + 1}y"] = float(o @ e), float(o @ f)
    out["neck"] = sp.get("neck", 5.0)
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}, D


K403 = {"o1a": 1.9, "o1c": -5.8, "o2a": 3.7, "o2c": -4.0, "o3a": 0.6, "o3c": 4.8, "d_az": -2.3, "d_el": -8.1, "d_a1": 3.3, "d_a2": -2.7,
        "d_wd": 3.7, "d_wa": 1.8, "neck": 17.6, "remote": 1, "ramp": 1, "slides": 1, "S_auto": 1, "drop": 1, "jam_contact": 1, "vfix": 1}

K722 = {"az1": 94.61, "el1": 60.68, "b1": 0.34, "az2": 24.06, "el2": 48.54, "b2": 0.42, "wd": 75.16, "wa": -13.04, "b3": 0.21,
        "S_max": 21.22, "centre": 1}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "k722":                                                  # conversion check: same lines as SN k 722
        mine, Dsn = from_sn(K722); Dm = Design(mine)
        print(json.dumps(mine))
        print("max |u - u_sn|", max(float(np.abs(a - b).max()) for a, b in zip(Dm.u, Dsn.u)),
              "max |c - c_sn|", max(float(np.abs(a - b).max()) for a, b in zip(Dm.c, Dsn.c)))
        sys.exit()
    if mode == "k403":                                                  # conversion check: same lines as seed-offset k 403
        mine, Ds = from_seed(K403); Dm = Design(dict(mine, centre=0, S_max=60.0))
        print(json.dumps(mine)); print("max |u - u_seed|", max(float(np.abs(a - b).max()) for a, b in zip(Dm.u, Ds.u)),
                                       "max |c - c_seed|", max(float(np.abs(a - b).max()) for a, b in zip(Dm.c, Ds.c)), "branch", Dm.branch, Ds.branch)
        B = CB.Bench(n_clip=60, n_ws=160); r = bench_eval(B, dict(mine, centre=0, S_max=60.0)); r0 = S.bench_eval(B, K403)
        print("mine", {k: r[k] for k in ("gap", "reach", "inband14", "contact")}, r["S"], "seed VModel", {k: r0[k] for k in ("gap", "reach", "inband14", "contact")}, r0["S"])
        sys.exit()
    if mode == "redteam":                                               # the pose that jams, the point that pinches, named groups
        B = CB.Bench(n_clip=60, n_ws=160); r, M = evaluate(B, par)
        print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "S", [M.p["S_a"], M.p["S_t"], M.p["R_r"]], "f", r.get("f"), r["lines"], "riser_h", r.get("riser_h"))
        print("parts in band 2-14 [share, median mm, samples]:", r["parts_ib14"]); print("why not taken:", r["why"], r["parts_pairs"], "res_max", r.get("res_max"), "min_clear_taken", r.get("min_clear_taken"))
        print("slide travel max |s - mid| (along, across, radial):", np.round(np.abs(M.s[M.kin_ok] - M.D.m).max(0), 1).tolist(), "mid", np.round(M.D.m, 1).tolist())
        lab = lambda i: f"#{i} {B.kind[i]} {B.clip[i][:22]:22s} plane {B.poses[i]['plane']:6.1f} elev {B.poses[i]['elev']:6.1f} axial {B.poses[i]['axial']:6.1f}"
        print("-- poses not taken (non-fold first, then fold) --")
        nt = [i for i in range(len(B.idx)) if M.why[i]]; nt.sort(key=lambda i: M.why[i] == "fold")
        for i in nt[:20]: print(f"  {M.why[i]:7s} {lab(i)}" + (f" clear {M.clear[i]:.1f} ({M.last_pair.get(i)})" if M.why[i] == "parts" else ""))
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
        if "--png" in sys.argv: S.ID = ID; S.sketch(M, os.path.join(REPO, "docs", "concepts", "img", ID + ".png")); print("sketch written")
        sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = evaluate(B, par)
    print({k: r[k] for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, "why", r["why"], "S", [M.p["S_a"], M.p["S_t"], M.p["R_r"]],
          "f", r.get("f"), r["lines"], "riser_h", r.get("riser_h"), "min_clear", r.get("min_clear_taken"), f"{time.time() - t:.0f}s")
    print("parts", r["parts_ib14"], r["parts_pairs"])
