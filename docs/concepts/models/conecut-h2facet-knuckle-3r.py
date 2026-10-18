"""conecut-h2facet-knuckle-3r (round 15, lens C 'conecut-sidestep-metal'): the verified lead conecut-knee-knuckle-3r
(docs/concepts/models/conecut-knee-knuckle-3r.py imported UNCHANGED, at its verified best_params: slipper-nose K drive,
conecut knee, J3 own-angle dowel stop, O20 hubs, metal, near-touch rules) with two milled cuts on hub 2's O20 x 12.25
Ti housing (member 7 = link 1b's J2 hub). Nothing else moves: the frozen claim protocol re-fits the lead's own shape.

  (1) BOTTOM-EDGE CHAMFER: a c x 45-deg chamfer on the skin-side bottom edge (z = F+0, r 10) over the azimuth sector
      |az - (AZ203 + daz)| <= hw (a chamfer mill run along the edge; the cone face r = 10 - c + z, z in [0, c]; the
      sector ends are the cutter's run-out, sampled as triangular end faces). AZ203 = 142.8 deg is pose 203's binder
      (ring c10 sample 17) in the judge's frame e = unit(u2 x [0.3, 0.5, 0.8]), f = u2 x e.
  (2) UPPER FLAT: a PLANAR flat of depth fd (one end-mill pass) whose normal points at az AZ264 + dazf (AZ264 = 124 deg,
      between 264's hub-2 binders c12 / c13 samples 15 - 16), from the crown (z 12.25) down to z0, with a 45-deg run-out
      below z0 (the cut plane offset grows 1:1 under z0, so there is no ledge). A flat of depth fd meets the cylinder at
      |az - azf| = acos((10 - fd) / 10) (19.9 deg at fd 0.6): no stepped sector faces (the spec's 'r' = min(r, 10 - f)'
      pocket would have them; the flat is the simpler, machinable cut that clears the same centre).

SAMPLING (judge's rule: the cut is a SOLID, not a sample move). The cut region is a set R1 u R2; hub 2's contact-only
rings (c10 .. c14: z 0 / 4.08 / 8.17 / 12.25 and the crown disc) lose every sample inside R1 u R2, the in-band (rigid)
bottom disc keeps its 80 samples with those inside R1 clipped radially to the chamfer (S6: equal sample count), and a
DENSE contact-only solid is added in the cut sectors (+- 6 deg around them): the remaining cylinder wall (0.5 mm in z,
1 deg in az), the bottom disc outer band, the crown disc band, the cone face, the chamfer's top edge on the unchanged
wall, the end faces and the flat face. dense = 1 adds that dense solid also at c = fd = 0 (the MEASUREMENT-change
control: the lead with the dense sector solid and no cut); dense = 0 = the lead's own sampling (cuts then only drop /
clip samples - optimistic, reported only).
Part-vs-part collisions keep the UNCUT hub-2 cylinder (sd_cyl / cyl_surf): a cut only removes metal, so this is the
conservative side (it can cost takes, never buy them).

BUILD LIMITS: hub bore = MR117 OD 11 (r 5.5): wall >= 3.0 needs r >= 8.5 everywhere on the cut -> c <= 1.5, fd <= 1.5.
The chamfer stays under z = c <= 1.5 (link 1b's lower plate F+0..3.0; the member interface F+3..3.15 and any stop groove
there are untouched); the flat's run-out stops at z0 - fd >= 3.9 (above the plate band). lowarm-kstop's short-arm plate
notch (az 66 - 95, floor F+1.0) in this frame: the chamfer sector's lower edge AZ203 + daz - hw is reported as
'notch_clear_deg' (must be > 0 for the kstop cell).

DOF: unchanged from the lead - 3 ACTIVE (J1, J2, J3), K slaved and never read, knee pins a / b passive rotations outside
the count, 0 passive translations, no gears / pulleys / cables. Complexity 18.5 (a cut on an existing made part, +0).

    OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/models/conecut-h2facet-knuckle-3r.py [check] ['<json>']
    CB_EXACT=1 ... frozen|held '<json>' [out.json]
    ... guard '<json list of param dicts>'   (exact Bench(110,360) guard poses 139/203/205/237/264/316 on the lead's frozen
                                             member rotations: per-part minima, the cut's own minima, the +0.1 / +0.2 probes)
    hooks: bench_eval(B, params) (tools/concept_sweep.py), evaluate(B, params) (tools/concept_cma.py)
"""
import importlib.util, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))
_sp = importlib.util.spec_from_file_location("conecut_for_h2facet", os.path.join(HERE, "conecut-knee-knuckle-3r.py"))
CC = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(CC)
CB, S, SN, PK, SC, FL, RF, BM = CC.CB, CC.S, CC.SN, CC.PK, CC.SC, CC.FL, CC.RF, CC.BM
ID = "conecut-h2facet-knuckle-3r"
LEAD = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", "conecut-knee-knuckle-3r.json")))["best_params"]
BASE = CC._clamp(dict(CC.PARAMS, **LEAD))                    # the verified lead, every parameter
FACET = dict(c=0.0, hw=35.0, daz=0.0, fd=0.0, dazf=0.0, z0=6.0, dense=1)
PARAMS = dict(BASE, **FACET)
AZ203, AZ264 = 142.8, 124.0                                  # judge's frame (see docstring)
HUB_R, CROWN = 10.0, 12.25
NOTCH_HI = 95.0                                              # lowarm-kstop's plate notch upper az (judge's frame)
GUARD = (139, 203, 205, 237, 264, 316)


def _clamp(p):
    p = dict(p)
    for k, lo, hi in (("c", 0.0, 1.5), ("hw", 25.0, 45.0), ("daz", -10.0, 10.0), ("fd", 0.0, 0.6), ("dazf", -10.0, 10.0),
                      ("z0", 4.5, 8.0)):
        p[k] = min(max(float(p.get(k, FACET[k])), lo), hi)
    p["dense"] = int(p.get("dense", 1))
    return CC._clamp(p)


def _unit(v): return v / np.linalg.norm(v)


def frame(ax):
    u = _unit(np.asarray(ax, float)); e = _unit(np.cross(u, [0.3, 0.5, 0.8])); return u, e, np.cross(u, e)


def wrapd(a): return (a + 180.0) % 360.0 - 180.0


class Facet:
    """the cut solid in hub 2's cylinder coordinates (r, az deg, z from the face F)"""
    def __init__(self, P):
        self.c = float(P["c"]); self.hw = float(P["hw"]); self.az0 = AZ203 + float(P["daz"])
        self.fd = float(P["fd"]); self.azf = AZ264 + float(P["dazf"]); self.z0 = float(P["z0"])

    def removed(self, r, az, z, eps=1e-6):
        r1 = np.zeros(len(r), bool)
        if self.c > 0:
            r1 = (np.abs(wrapd(az - self.az0)) <= self.hw + 1e-9) & (z < self.c) & (r > HUB_R - self.c + z + eps)
        r2 = np.zeros(len(r), bool)
        if self.fd > 0:
            r2 = r * np.cos(np.radians(az - self.azf)) > HUB_R - self.fd + np.maximum(0.0, self.z0 - z) + eps
        return r1 | r2, r1, r2

    def sectors(self):
        """azimuth windows (deg) where the solid is re-sampled densely (cut sectors +- 6 deg)"""
        out = [(self.az0 - self.hw - 6.0, self.az0 + self.hw + 6.0, 0.0, max(self.c, 0.0) + 4.1)]
        hf = math.degrees(math.acos((HUB_R - max(self.fd, 0.3)) / HUB_R))
        out.append((self.azf - hf - 6.0, self.azf + hf + 6.0, max(self.z0 - max(self.fd, 0.3) - 1.0, 0.0), CROWN))
        return out

    def solid(self, dense=True):
        """dense boundary samples (cylinder coords) of hub 2 minus the cut, inside the cut sectors"""
        pts = []
        def add(r, az, z): pts.append(np.stack(np.broadcast_arrays(np.asarray(r, float), np.asarray(az, float), np.asarray(z, float)), -1).reshape(-1, 3))
        if not dense: return np.zeros((0, 3))
        for a0, a1, zlo, zhi in self.sectors():
            az = np.arange(a0, a1 + 1e-9, 1.0)
            zz = np.unique(np.r_[np.arange(zlo, zhi + 1e-9, 0.5), zhi, [self.c] if 0 < self.c < zhi else []])
            A, Zg = np.meshgrid(az, zz); add(HUB_R, A, Zg)                                 # remaining wall
            rr = np.arange(7.0, HUB_R + 1e-9, 0.5)
            if zlo <= 0.0: A, R_ = np.meshgrid(az, np.unique(np.r_[rr, HUB_R - self.c])); add(R_, A, 0.0)   # bottom disc band
            if zhi >= CROWN - 1e-9: A, R_ = np.meshgrid(az, rr); add(R_, A, CROWN)         # crown disc band
        if self.c > 0:                                                                     # cone face + its two edges
            az = np.arange(self.az0 - self.hw, self.az0 + self.hw + 1e-9, 1.0); zc = np.linspace(0.0, self.c, max(int(math.ceil(self.c / 0.2)) + 1, 3))
            A, Zg = np.meshgrid(az, zc); add(HUB_R - self.c + Zg, A, Zg)
            for ae in (self.az0 - self.hw, self.az0 + self.hw):                            # run-out end faces (triangles)
                for z in zc:
                    rr = np.linspace(HUB_R - self.c + z, HUB_R, 5); add(rr, ae, z)
        if self.fd > 0:                                                                    # flat face (+ its run-out plane)
            zz = np.unique(np.r_[np.arange(max(self.z0 - self.fd, 0.0), CROWN + 1e-9, 0.5), self.z0, CROWN])
            for z in zz:
                d = HUB_R - self.fd + max(0.0, self.z0 - z)
                if d >= HUB_R: continue
                h = math.sqrt(HUB_R ** 2 - d ** 2); s = np.unique(np.r_[np.arange(-h, h + 1e-9, 0.5), h])
                r = np.hypot(d, s); az = self.azf + np.degrees(np.arctan2(s, d)); add(r, az, z)
        X = np.concatenate(pts) if pts else np.zeros((0, 3))
        rem, _, _ = self.removed(X[:, 0], X[:, 1], X[:, 2], eps=1e-4)
        return X[~rem]


def to_xyz(C, cen, u, e, f):
    a = np.radians(C[:, 1]); return cen + C[:, 2:3] * u + C[:, 0:1] * (np.cos(a)[:, None] * e + np.sin(a)[:, None] * f)


def to_cyl(X, cen, u, e, f):
    w = X - cen; z = w @ u; rr = w - z[:, None] * u
    return np.linalg.norm(rr, axis=1), np.degrees(np.arctan2(rr @ f, rr @ e)) % 360.0, z


def apply_facet(M, P):
    """edit hub 2's samples on a built model (after the metal synthesis)"""
    F = Facet(P); mem2, cen2, ax2 = M.cyl["hub2"]; u, e, f = frame(ax2); info = dict(c=F.c, hw=F.hw, az0=round(F.az0, 2), fd=F.fd,
                                                                                         azf=round(F.azf, 2), z0=F.z0, dense=int(P["dense"]))
    m, X = M.rigid["hub2"]; r, az, z = to_cyl(X, cen2, u, e, f); rem, r1, r2 = F.removed(r, az, z)
    Y = X.copy()
    if r1.any():                                                                           # clip radially onto the cone at z
        rn = np.minimum(r, HUB_R - F.c + z); Y[r1] = to_xyz(np.stack([rn, az, z], 1)[r1], cen2, u, e, f)
    if r2.any():                                                                           # onto the flat plane (crown side)
        info["rigid_on_flat"] = int(r2.sum())
    M.rigid["hub2"] = (m, Y); info["rigid_clipped"] = int(r1.sum())
    dropped = 0; new = []
    for ci, (mm, Xc) in enumerate(M.contact):
        if mm != mem2 or not len(Xc): new.append(M.contact[ci]); continue
        rr_, aa_, zz_ = to_cyl(Xc, cen2, u, e, f)
        hub = (rr_ <= HUB_R + 1e-3) & (zz_ >= -1e-3) & (zz_ <= CROWN + 1e-3)
        rm, _, _ = F.removed(rr_, aa_, zz_); rm = rm & hub
        dropped += int(rm.sum())
        new.append((mm, Xc[~rm]) if rm.any() else M.contact[ci])
    sol = F.solid(dense=int(P["dense"]) >= 1)
    if len(sol): new.append((mem2, to_xyz(sol, cen2, u, e, f)))
    M.contact = new; info.update(contact_dropped=dropped, solid_n=int(len(sol)), notch_clear_deg=round(F.az0 - F.hw - NOTCH_HI, 2),
                                 wall_min_mm=round(min(HUB_R - F.c, HUB_R - F.fd) - 5.5, 2),
                                 flat_halfwidth_deg=(round(math.degrees(math.acos((HUB_R - F.fd) / HUB_R)), 2) if F.fd > 0 else 0.0),
                                 mass_removed_mg=round(4.43 * (math.radians(2 * F.hw) * HUB_R * F.c ** 2 / 2
                                                               + (CROWN - F.z0 + F.fd / 2) * (HUB_R ** 2 * (math.acos((HUB_R - F.fd) / HUB_R)) - (HUB_R - F.fd) * math.sqrt(max(HUB_R ** 2 - (HUB_R - F.fd) ** 2, 0)))), 1))
    M._facet_info = info
    return info


class FTModel(CC.CCModel):
    def _rod_metal(self):
        super()._rod_metal()
        apply_facet(self, dict(FACET, **{k: self.D.p[k] for k in FACET if k in self.D.p}))
        try: self._sc_info["facet"] = self._facet_info; self._rod_info = self._sc_info
        except Exception: pass


# the lead's module and its parents build models through these names: point them at FTModel
CC.CCModel = FTModel; SN.SNModel = FTModel; SC.SCModel = FTModel; FL.G.KR.KB.KModel = FTModel; FL.FLModel_SC = FTModel


def probe(M, B, thrs=(0.1, 0.2)):
    """tolerance probe (round-15 rule, acroant-conecut's reading): every taken pose whose lowest metal (rigid or extra
    walls) is under thr counted as contact"""
    taken = lambda i: B.res[i] is not None and float(np.min(B.res[i])) >= 0
    cm = getattr(M, "cmin", {}) or {}
    mins = [(min(float(np.min(B.res[i])), cm.get(i, 1e9)), i) for i in range(len(B.idx)) if taken(i)]
    res0 = list(B.res); out = {}
    for t in thrs:
        for d, i in mins:
            if d < t: B.res[i] = np.r_[B.res[i], -1e-3]
        out[f"gap_probe{t:g}"] = B.report()["gap"]; out[f"probe{t:g}_poses"] = int(sum(1 for d, i in mins if d < t)); B.res = list(res0)
    out["shell12_poses"] = int(sum(1 for d, i in mins if 1.0 <= d < 2.0))
    return out


def _report(B, params):
    p = _clamp(dict(PARAMS, **params))
    r, M = CC._report(B, p)
    try: r.update(probe(M, B))
    except Exception as e: r["probe_err"] = str(e)[:100]
    r["facet"] = getattr(M, "_facet_info", None)
    return r, M


def evaluate(B, params):
    """objective = the 1 mm near-touch gap (CLAUDE.md search rule); r['plain'] keeps the plain gap"""
    r, M = _report(B, params)
    if r.get("gap_near1") is not None: r["gap"] = r["gap_near1"]
    if r.get("sidecar_fail") or r.get("drive_idle") or r.get("pa_fail") or r.get("knee_moved"): r["honest"] = False
    p = {k: v for k, v in M.p.items() if isinstance(v, (int, float, str, bool)) or v is None}
    return p, r


def bench_eval(B, params):
    r, M = _report(B, params); r.pop("params", None); return r


def frozen(P, nc=110, nw=360):
    out = CC.frozen(_clamp(dict(PARAMS, **P)), nc, nw)
    return out


def frozen_held(P): return CC.frozen(_clamp(dict(PARAMS, **P)), -1, -1)


def viz_export(par): return CC.viz_export(_clamp(dict(PARAMS, **par)))


# ------------------------------------------------------------------------------------------------------------------
# guard-pose reads on the exact Bench(110,360): the lead's frozen member rotations (all members turn about GH, so a pure
# rotation per member and pose) recovered from the lead's own fit, hub 2's cut metal worn at those rotations
_GB = {}


def guard_bench(poses=GUARD, n_clip_keep=4):
    """Bench(110,360) EXACT reduced to the guard poses (+ n_clip_keep clip frames so the report has clips): the frozen
    wear of a chain at only these poses takes seconds; per-pose results are identical to the full bench (ws poses are
    scored one by one)"""
    old = os.environ.get("CB_EXACT"); os.environ["CB_EXACT"] = "1"; os.environ["CB_QUIET_EXACT"] = "1"
    try: B = CB._Bench0(110, 360) if hasattr(CB, "_Bench0") else CB.Bench(110, 360)
    finally:
        if old is None: os.environ.pop("CB_EXACT")
        else: os.environ["CB_EXACT"] = old
    sel = [j for j in range(len(B.idx)) if B.kind[j] == "clip"][:n_clip_keep] + list(poses)
    B.orig = sel; B.idx = np.asarray(B.idx)[sel]; B.kind = [B.kind[j] for j in sel]; B.clip = [B.clip[j] for j in sel]
    B.poses = [B.poses[j] for j in sel]; B.res = [None] * len(sel); B._skin = {}; B._ex = {}; B._frames = {}; B.key = CB._key(B.idx)
    return B


def with_guard_bench(fn, poses=GUARD):
    """run fn() with CB.Bench(110, 360) returning the reduced guard bench (any chain's frozen protocol)"""
    if not hasattr(CB, "_Bench0"): CB._Bench0 = CB.Bench
    orig = CB.Bench
    def Bench(n_clip=60, n_ws=160, *a, **k):
        if (n_clip, n_ws) == (110, 360): return guard_bench(poses)
        return CB._Bench0(n_clip, n_ws, *a, **k)
    CB.Bench = Bench
    try: return fn()
    finally: CB.Bench = orig


def guard_on(M, B, plist, poses=None, apply=None):
    """per config: the min distance at each guard pose (bench positions; B.orig maps them back) of (a) every part of the
    chain except hub 2 (unchanged metal), (b) hub 2's rigid disc and contact rings after the cut, (c) the cut solid"""
    apply = apply or apply_facet
    poses = list(range(len(B.idx))) if poses is None else poses
    poses = [j for j in poses if B.kind[j] == "ws"]
    name = (lambda j: int(B.orig[j])) if hasattr(B, "orig") else (lambda j: int(j))
    mem2 = M.cyl["hub2"][0]
    base_rigid = {nm: (m, X.copy()) for nm, (m, X) in M.rigid.items()}; base_contact = list(M.contact)
    other, binder = {}, {}
    for j in poses:
        dm = []
        for nm, (m, X) in base_rigid.items():
            if m != mem2 and len(X): dm.append((float(B.dist(j, M.world(m, j, X)).min()), "r:" + nm))
        for ci, (m, X) in enumerate(base_contact):
            if m != mem2 and len(X): dm.append((float(B.dist(j, M.world(m, j, X)).min()), "c%d" % ci))
        d0 = min(dm); other[j] = round(d0[0], 3); binder[j] = d0[1]
    rows = []
    for P in plist:
        Pc = dict(FACET, **P); M.rigid = dict(base_rigid); M.contact = list(base_contact)
        info = apply(M, Pc); row = dict(params={k: Pc[k] for k in FACET}, facet=info, poses={})
        mem2_, cen2, ax2 = M.cyl["hub2"]; u, e, f = frame(ax2)
        for j in poses:
            Xr = M.rigid["hub2"][1]; dr = B.dist(j, M.world(mem2, j, Xr)); mr = float(dr.min())
            cs = []; az_min = None; best = 1e9
            for (m, X) in M.contact:
                if m == mem2 and len(X):
                    d = B.dist(j, M.world(m, j, X)); k = int(np.argmin(d))
                    cs.append(float(d[k]))
                    if d[k] < best: best = float(d[k]); rr, aa, zz = to_cyl(X[k:k + 1], cen2, u, e, f); az_min = [round(float(rr[0]), 2), round(float(aa[0]), 1), round(float(zz[0]), 2)]
            row["poses"][name(j)] = dict(hub2_rigid=round(mr, 3), hub2_walls=round(min(cs), 3) if cs else None, others=other[j], other_binder=binder[j],
                                         pose_min=round(min([mr, other[j]] + cs), 3), hub2_min_at_r_az_z=az_min)
        m203 = row["poses"].get(203, {}).get("pose_min")
        if m203 is not None:
            row["p203"] = dict(plain=m203, probe01=round(m203 - 0.1, 3), probe02=round(m203 - 0.2, 3), prereg_035=bool(m203 >= 0.35))
        row["t5"] = {j: v["pose_min"] for j, v in row["poses"].items() if v["pose_min"] < 0}
        row["t5_sum"] = round(-sum(row["t5"].values()), 3)
        rows.append(row)
    M.rigid = base_rigid; M.contact = base_contact
    return rows


def guard(plist, poses=GUARD, full=False):
    """the lead's chain: frozen protocol (fit Bench(60,160) fast) worn on the guard bench (full=True: the whole exact
    Bench(110,360), which also re-measures the control claim)"""
    P0 = _clamp(dict(PARAMS, c=0.0, fd=0.0, dense=0))
    if full:
        fit, M1, M, B, r = CC._frozen_model(P0, 110, 360); sel = [j for j in poses]
    else:
        fit, M1, M, B, r = with_guard_bench(lambda: CC._frozen_model(P0, 110, 360), poses); sel = None
    rows = guard_on(M, B, [_clamp(dict(PARAMS, **P)) for P in plist], sel)
    rows.insert(0, dict(control={k: r.get(k) for k in ("gap", "reach", "follow", "inband14", "inband10", "contact")}, full=full))
    return rows


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    par = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    if mode == "viz":
        print(json.dumps(viz_export(par), default=float)); sys.exit()
    if mode == "guard":
        os.environ["CB_EXACT"] = "1"; os.environ["CB_QUIET_EXACT"] = "1"
        t = time.time(); rows = guard(par if isinstance(par, list) else [par], full=os.environ.get("H2F_FULL") == "1")
        out = dict(row=ID, rows=rows, secs=round(time.time() - t, 1))
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        print(json.dumps(rows[0])); rows = rows[1:]
        for rw in rows: print(json.dumps(dict(p=rw["params"], poses={j: (v["hub2_rigid"], v["hub2_walls"], v["others"]) for j, v in rw["poses"].items()},
                                              p203=rw.get("p203"), notch=rw["facet"]["notch_clear_deg"], solid_n=rw["facet"]["solid_n"]), default=float))
        sys.exit()
    if mode in ("frozen", "held"):
        t = time.time(); out = {"frozen": frozen, "held": frozen_held}[mode](par); out["params"] = par
        out["row"] = ID; out["secs"] = round(time.time() - t, 1)
        if len(sys.argv) > 3: json.dump(out, open(sys.argv[3], "w"), indent=1, default=float)
        a = out.get("audit", {})
        print(json.dumps(dict(row=ID, fit=out.get("fit_fast"), frozen=out["frozen"], why=out.get("why"), near1=a.get("gap_near1"),
                              near2=a.get("gap_near2"), minmetal=a.get("near_touch_min_mm"), ovh=out.get("overhead"),
                              contacts=out.get("contact_poses"), stopped=out.get("stopped"), secs=out["secs"]), default=float)); sys.exit()
    B = CB.Bench(n_clip=60, n_ws=160); t = time.time()
    r, M = _report(B, par)
    print(json.dumps(dict(row=ID, gap=r["gap"], plain=r.get("plain"), near1=r.get("gap_near1"), near2=r.get("gap_near2"), min_metal=r.get("min_metal_mm"),
                          reach=r["reach"], follow=r["follow"], inband14=r["inband14"], inband10=r.get("inband10"), contact=r["contact"], honest=r.get("honest"),
                          why=r.get("why"), probe={k: r.get(k) for k in ("gap_probe0.1", "gap_probe0.2", "probe0.1_poses", "probe0.2_poses", "shell12_poses")},
                          facet=r.get("facet"), parts_hub2=(r.get("parts_ib14") or {}).get("hub2"), secs=round(time.time() - t)), default=float))
