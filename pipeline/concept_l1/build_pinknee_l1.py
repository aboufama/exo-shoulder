"""L1 keep-out CAD of a skin-normal-3r-pin-knee configuration (docs/concepts/skin-normal-3r-pin-knee.md; the round-3 /
generation-3 winner k4598 by default) -> a judge-ready design dir pipeline/full-exo/designs/<out>/ (exo.glb, clips.json,
workspace.json, design.json, parts_full.json, build.json). Derived from build_osn_l1.py (the 2-slide leader's L1): the
chain (hubs, links) carries over, the crossed RSR3M cuff stage is replaced by the knee.

The shape is the VERIFIED model's own fit under the frozen-shape protocol (docs/concepts/verify/skin-normal-3r-pin-knee.py:
fit on Bench(60,160) FAST, that exact shape - heights, knee centre m - is what the verifier wore on Bench(110,360) exact).
Every part is built at its real size from that fit:
  * hubs: keep-outs of the DECLARED per-joint hub (rad1..rad3: O20 v5 / O17 / O15, all an MR117-2RS pair, 12.25 mm stack):
    lower member's plate F..F+3, upper member's boss + cap F+3.15..F+12.25;
  * links 1, 2: 8 x 3 mm straps through the model's fitted underside samples; columns inside a hub's footprint (+2.5 mm)
    lifted to that hub's member level (the seed L1's R6 lesson, as build_osn_l1.py);
  * member 3 = J3 lower plate + the E strap (8 x 3 Ti; underside = the model's fitted E profile: hub 3's face at the rim,
    <= 60 deg ramps, the knee level tr at the boss) + the E boss (O12 x tp at pin a, tr..tr+tp). The strap thins from 3 mm
    to the boss thickness tp over its last station before the boss rim (the knee link rides 0.5 mm over the boss: a 3 mm
    strap there would sit in the knee link; the model samples the strap only up to 6.5 mm from pin a);
  * knee link (its own group l4): a flat Ti bar (lc + 12) x 10 x tp at tr + tp + 0.5 (the model's box), pins a, b 6 mm from
    its ends;
  * arm pad (arm-fixed, H group): O12 x tp at pin b, tr..tr+tp, and the pad mount (proxy): a tp slab at the pad level from
    the pad to the proximal end of the user's BOTTOM bar (the pad has to be fixed to the cuff somewhere);
  * pin stacks: stk = tp + 0.5 + tp (5.0 mm: iglidur GSM sleeve + GTM washers on an integral O4 Ti pin, IGLIDUR-PIN;
    6.0 mm = MR63ZZ pair), the 0.5 mm running gap holds the washer;
  * the user's arm parts (H, F groups) as the other L1 builds carry them.
Member frames (clips.json "G" + "T" per group, scene_export.frame_xforms) reproduce the model's exact kinematics: world =
RS (R_m x + t_m) with (R_m, t_m) = the model's own Model.T(m, i) (member 3 turns q3' = q3 + phi about J3, the knee link
about pin a); the arm-fixed parts sit in the humerus group H at x_H = HR x.
Clip frames (30 fps, the champion's clips incl. the held-out Wave / Walking - judged, never fitted) are followed when the
chain closes on the design branch, the knee closes inside its [ang_min, 180 - ang_min] window, the closure residual is
< 0.5 deg, no joint (q1, q2, q3', pin a, pin b) steps > 25 deg, the model's part checks pass (non-adjacent >= 1 mm,
adjacent >= 0.15 mm), the verifier's added checks pass (knee vs hub 3's link-2 half >= 1 mm, E boss vs hubs 1-2 / link 1
>= 1 mm, vs link 2 >= 0.15 mm), the BUILT meshes of every adjacent / knee pair do not interpenetrate by > 0.15 mm, and no
metal sample - the model's and every built part's own surface - is inside the exact posed skin; otherwise the arm is held
at the last followed pose until the motion comes back within RESUME deg.

The configuration is an INPUT (the polish run may replace k4598): --params '<json>' | --params-file F | --k K (sweep log)
| default = docs/concepts/rows/skin-normal-3r-pin-knee.json best_params; per-joint hubs with --hubs 10,10,10 (or rad1..rad3
in the params).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/build_pinknee_l1.py [--out ID] [--params JSON] [--hubs R1,R2,R3]
                                                                                 [--jobs 1] [--no-clips]
"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo")); sys.path.insert(0, HERE)
os.environ.pop("CB_EXACT", None)                     # the fit bench of the frozen protocol is Bench(60,160) FAST
import concept_bench as CB                                                      # noqa: E402
import build_seed_offset_l1 as REF                                              # noqa: E402  (mesh helpers, HR, skin_min, frame_dict)
BP = CB.BP


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


ID = "skin-normal-3r-pin-knee"
MK = _load("pin_knee_model_l1", os.path.join(REPO, "docs", "concepts", "models", ID + ".py"))
S = MK.S
FULL = os.path.join(REPO, "pipeline", "full-exo"); TEMPLATE = REF.TEMPLATE; USER_SRC = "l1_seed-offset-3r-slides"
CROWN, UP, T_LINK, W_LINK, RUN = S.CROWN, S.UP, S.T_LINK, S.W_LINK, S.RUN
BOSS_R, PAD_R, KNEE_W = MK.BOSS_R, MK.PAD_R, MK.KNEE_W
PLATE = 3.0; RESUME = 4.0; ADJ = 0.15
HR = REF.HR; unit = S.unit
TI, STEEL = 4.43, 7.85


# ---------------------------------------------------------------------------------------------------- the fitted model
def params_from(a):
    if a.params: P = json.loads(a.params); src = "--params"
    elif a.params_file: P = json.load(open(a.params_file)); P = P.get("params", P); src = a.params_file
    elif a.k is not None:
        L = json.load(open(os.path.join(REPO, "docs", "concepts", "sweeps", ID + ".json")))
        e = next(x for x in L if x.get("k") == a.k); P = dict(e["params"]); src = f"sweep log k {a.k}"
    else:
        R = json.load(open(os.path.join(REPO, "docs", "concepts", "rows", ID + ".json"))); P = dict(R["best_params"]); src = f"rows best_params (k {R.get('best_k')})"
    if a.hubs:
        for k, r in enumerate(a.hubs.split(",")): P[f"rad{k + 1}"] = float(r)
    return P, src


def fit(P):
    """the frozen protocol's fit: Bench(60,160) fast (CB_EXACT unset), the model's own run"""
    B = CB.Bench(60, 160); M = MK.Model(B, dict(P)); r = M.run(); M._bench = (M.Q, M.s, M.RS, M.X, M.K, M.q)
    return M, r


def link_rows(M):
    """the model's finalize() link rows (MK.Model.finalize), keeping every station (also inside the hub footprints)"""
    D = M.D; u, c = D.u, D.c; k = math.tan(S.RAMP * S.D2R); keep = ~M.drop; F = M.f
    rL = {nm: [r[keep].max(0) for r in rows] for nm, rows in M.Lneed.items() if nm in ("L1", "L2")}
    lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): UP, ("L2", 2): UP}; out = {}
    for lk in M.geo.links:
        rows = []
        for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
            r = r.copy(); Sx = sarc
            for kk, end in ((lk["ka"], 0), (lk["kb"], -1)):
                idx = np.nonzero(keep_s)[0]
                if not len(idx): continue
                j = idx[0] if end == 0 else idx[-1]
                cen = c[kk] + F[kk] * u[kk]; den = float(dv[j] @ u[kk])
                rc = (cen @ u[kk] + lvl[(lk["name"], kk)]) / max(den, 0.2)
                r = np.maximum(r, rc - k * np.abs(Sx - Sx[j]))
            r = np.max(r[None, :] - k * np.abs(Sx[:, None] - Sx[None, :]), axis=1)
            rows.append((dv, keep_s, r))
        out[lk["name"]] = (lk, rows)
    return out


def link_solid(M, lk, rows):
    """strap 8 x 3 mm through the model's fitted underside samples, one station past each hub rim; the past-rim station
    and every column inside a hub's footprint (+2.5 mm) lifted to that hub's member level (build_osn_l1.link_solid with the
    declared per-joint hub radius)"""
    D = M.D; u, c = D.u, D.c; F = M.f; hr = M.hr
    lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): UP, ("L2", 2): UP}
    keep_any = np.any([kp for _, kp, _ in rows], axis=0); idx = np.nonzero(keep_any)[0]
    j0, j1 = max(0, idx[0] - 1), min(len(keep_any) - 1, idx[-1] + 1)
    dvs = [dv for dv, _, _ in rows]; rs = [r.copy() for _, _, r in rows]
    d_lo = unit(dvs[0] + (dvs[0] - dvs[1]) * 0.5); d_hi = unit(dvs[-1] + (dvs[-1] - dvs[-2]) * 0.5)
    cols_d = [d_lo] + dvs + [d_hi]; cols_r = [rs[0].copy()] + [r.copy() for r in rs] + [rs[-1].copy()]
    for kk, j in ((lk["ka"], j0), (lk["kb"], j1)):
        if j == (idx[0] if kk == lk["ka"] else idx[-1]): continue
        cen = c[kk] + F[kk] * u[kk]
        for q in range(len(cols_d)):
            den = float(cols_d[q][j] @ u[kk])
            if den > 0.2: cols_r[q][j] = max(cols_r[q][j], (cen @ u[kk] + lvl[(lk["name"], kk)]) / den + 0.02)
    for kk in (lk["ka"], lk["kb"]):
        cen = c[kk] + F[kk] * u[kk]; lv = lvl[(lk["name"], kk)] + 0.2
        for q in range(len(cols_d)):
            Pq = cols_d[q] * cols_r[q][:, None]; w = Pq - c[kk]
            off = np.linalg.norm(w - (w @ u[kk])[:, None] * u[kk], axis=1); den = cols_d[q] @ u[kk]
            sel = (off < hr[kk] + 2.5) & (den > 0.2)
            cols_r[q][sel] = np.maximum(cols_r[q][sel], (cen @ u[kk] + lv) / den[sel])
    J = np.arange(j0, j1 + 1)
    Bot = np.stack([cols_d[q][J] * cols_r[q][J][:, None] for q in range(len(cols_d))], 1)
    Off = T_LINK * np.stack([cols_d[q][J] for q in range(len(cols_d))], 1)
    return REF.grid_solid(Bot, Off)


def e_strap(M):
    """E strap (member 3, home frame): stations along eE from inside hub 3's plate (r3 - 2) to 1.5 mm inside the boss rim;
    underside = the model's fitted E profile (hub 3's face f3 at the rim, the knee level tr at the boss rim, the model's
    hEx in between); 3 mm thick up to the last sampled station, thinning to tp at the boss rim"""
    D = M.D; P = D.p; c3 = D.c[2]; sn = D.sn; fr = M.fr; eE, nE = fr["eE"], fr["nE"]
    r3 = M.hr[2]; lE = float(P["lE"]); tp = P["tp"]; f3, tr = M.f[2], M.tr
    xs_m = np.unique(np.round(M._Ex, 6)); hx_m = np.array([M.hEx[np.isclose(M._Ex, v)].max() for v in xs_m])
    x_rim, x_boss = lE - BOSS_R, lE - BOSS_R + 1.5
    xs = np.unique(np.r_[np.linspace(r3 - 2.0, r3, 3), xs_m, np.linspace(xs_m[-1], x_rim, 4), x_boss])
    h = np.interp(xs, np.r_[r3 - 2.0, r3, xs_m, x_rim, x_boss], np.r_[f3, f3, hx_m, tr, tr])
    th = np.where(xs <= xs_m[-1] + 1e-9, T_LINK, np.interp(xs, [xs_m[-1], x_rim], [T_LINK, tp]))
    ys = np.array([-W_LINK / 2, -1.0, 1.0, W_LINK / 2])
    Bot = c3[None, None] + xs[:, None, None] * eE + ys[None, :, None] * nE + h[:, None, None] * sn
    Off = th[:, None, None] * np.broadcast_to(sn, Bot.shape)
    return REF.grid_solid(Bot, Off.copy()), dict(x=[round(float(xs[0]), 2), round(float(xs[-1]), 2)], under=[round(float(h.min()), 2), round(float(h.max()), 2)],
                                                 thin_from=round(float(xs_m[-1]), 2), rim=round(x_rim, 2))


def build_parts(M):
    """[(group, member, name, mesh in the MEMBER-LOCAL home frame, material)]; member 5 = arm-fixed (canonical arm frame)"""
    D = M.D; P = D.p; u, c = D.u, D.c; F = M.f; tr = M.tr; tp = P["tp"]; sn = D.sn; fr = M.fr; hr = M.hr; lc = float(P["lc"])
    H = lambda k: c[k] + F[k] * u[k]; out = []
    hub = lambda k: f"O{2 * hr[k]:.0f}"
    out.append(("base", 0, f"J1 upper boss + cap keep-out ({hub(0)}, F+3.15..F+12.25; base = J1's upper member)", REF.cyl(H(0), u[0], UP, CROWN, r=hr[0]), "ti"))
    out.append(("l1", 1, f"J1 lower plate keep-out ({hub(0)} x 3, link 1)", REF.cyl(H(0), u[0], 0.0, PLATE, r=hr[0]), "ti"))
    out.append(("l1", 1, f"J2 lower plate keep-out ({hub(1)} x 3, link 1)", REF.cyl(H(1), u[1], 0.0, PLATE, r=hr[1]), "ti"))
    out.append(("l2", 2, f"J2 upper boss + cap keep-out ({hub(1)}, F+3.15..F+12.25, link 2)", REF.cyl(H(1), u[1], UP, CROWN, r=hr[1]), "ti"))
    out.append(("l2", 2, f"J3 upper boss + cap keep-out ({hub(2)}, F+3.15..F+12.25, link 2)", REF.cyl(H(2), u[2], UP, CROWN, r=hr[2]), "ti"))
    out.append(("l3", 3, f"J3 lower plate keep-out ({hub(2)} x 3, member 3)", REF.cyl(H(2), u[2], 0.0, PLATE, r=hr[2]), "ti"))
    prof = link_rows(M)
    for nm, grp, mem in (("L1", "l1", 1), ("L2", "l2", 2)):
        lk, rows = prof[nm]; out.append((grp, mem, f"link {nm[1]} strap keep-out (8 x 3 mm Ti, fitted underside)", link_solid(M, lk, rows), "ti"))
    Em, Einfo = e_strap(M)
    out.append(("l3", 3, f"E strap keep-out (8 x 3 mm Ti, fitted underside, hub 3 plate -> pin a, thins to {tp} at the boss)", Em, "ti"))
    out.append(("l3", 3, f"E boss = pin a lower plate (O{2 * BOSS_R:.0f} x {tp} mm, tr..tr+tp, member 3)", REF.cyl(fr["A0"], sn, tr, tr + tp, r=BOSS_R), "ti"))
    z0 = tr + tp + RUN
    ck = fr["A0m"] + (lc / 2) * fr["eK"] + (z0 + tp / 2) * sn
    out.append(("l4", 6, f"knee link keep-out (flat Ti bar {lc + 2 * BOSS_R:.1f} x {KNEE_W:.0f} x {tp} mm, pins a, b {BOSS_R:.0f} mm from its ends, tr+tp+0.5)",
                REF.box(ck, np.stack([fr["eK"], fr["nK"], sn], 1), [lc + 2 * BOSS_R, KNEE_W, tp]), "ti"))
    out.append(("H", 5, f"arm pad = pin b lower plate (O{2 * PAD_R:.0f} x {tp} mm, tr..tr+tp, arm-fixed on the cuff)", REF.cyl(fr["Bm"], sn, tr, tr + tp, r=PAD_R), "ti"))
    stack = dict(pin_stack_mm=float(P["stk"]), plate_tp=tp, run=RUN, knee_level_tr=round(float(tr), 3), f=[round(float(x), 3) for x in F],
                 boss=[round(float(tr), 3), round(float(tr + tp), 3)], knee=[round(float(z0), 3), round(float(z0 + tp), 3)], E=Einfo,
                 knee_link_mm=[round(lc + 2 * BOSS_R, 2), KNEE_W, tp], hubs_r=list(hr))
    return out, stack


def pad_mount(M, bottom_c):
    """tp slab at the pad level from the arm pad to the proximal end of the user's BOTTOM bar (canonical arm frame)"""
    D = M.D; tp = D.p["tp"]; tr = M.tr; sn = D.sn; Bm = M.fr["Bm"]; c3 = D.c[2]
    rel = bottom_c - Bm; z = (bottom_c - c3) @ sn - tr; inpl = rel - np.outer(rel @ sn, sn); d = np.linalg.norm(inpl, axis=1)
    near = (d < 45) & (z > -3) & (z < 6)
    if not near.any(): return None, dict(note="no BOTTOM vertices within 45 mm of the pad near the pad level")
    dmin = float(d[near].min()); sel = near & (d < dmin + 4.0)
    tgt = inpl[sel].mean(0); L = float(np.linalg.norm(tgt)) + 3.0; ex = unit(tgt); ey = np.cross(sn, ex)
    cen = Bm + (L / 2) * ex + (tr + tp / 2) * sn
    m = REF.box(cen, np.stack([ex, ey, sn], 1), [L, 2 * PAD_R, tp])
    return m, dict(length=round(L, 1), dir_along_across=[round(float(ex @ D.sa), 3), round(float(ex @ D.st), 3)], bottom_verts_near=int(sel.sum()),
                   bottom_end_dist=round(dmin, 1), bottom_height_rel_tr=[round(float(z[sel].min()), 1), round(float(z[sel].max()), 1)])


def user_parts():
    """the user's arm parts (H, F groups, rest frame) as the other L1 builds carry them (from l1_seed-offset-3r-slides
    minus its own proxies)"""
    s = trimesh.load(os.path.join(FULL, "designs", USER_SRC, "exo.glb")); out = []
    for node in s.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if g not in ("H", "F") or "(proxy)" in n: continue
        T_, gn = s.graph[node]; m = s.geometry[gn].copy(); m.apply_transform(T_); out.append((g, n, m))
    return out


# ---------------------------------------------------------------------------------------------------- kinematics per pose
GROUPS = ((1, "l1"), (2, "l2"), (3, "l3"), (6, "l4"))


def swap_in(M, K): M.Q, M.s, M.RS, M.X, M.K, M.q = K["Q"], K["s"], K["RS"], K["X"], K["Kn"], K["qr"]


def chain(M, poses):
    """poses (n, 5) -> per pose: IK, knee, closure residual, (G, T) per group from the model's own member transforms"""
    D = M.D; RS = np.array([S.scap(float(p[1])) for p in poses]); RH = np.array([S.humerus(p) for p in poses])
    Q = np.einsum("nji,njk->nik", RS, RH); q, ok, X1, X2, X3, s = D.ik(Q); Kn = D.knee(s)
    R123 = X3[0]; res = np.degrees(np.arccos(np.clip((np.einsum("nij,nij->n", R123, Q) - 1) / 2, -1, 1)))
    kok = Kn["ok"] & (np.abs(s[:, 2]) <= M.p["R_tol"])
    K = dict(q=np.degrees(q), qr=q, ok=ok, kok=kok, res=res, s=s, Q=Q, RS=RS, X={1: X1, 2: X2, 3: X3}, Kn=Kn,
             qq=np.degrees(np.c_[q[:, :2], q[:, 2] + Kn["phi"], Kn["qa"], Kn["qb"]]))
    n = len(Q); G = {"base": RS}; T = {"base": np.zeros((n, 3))}
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); swap_in(M, K)
    try:
        for m, g in GROUPS:
            Gm = np.zeros((n, 3, 3)); Tm = np.zeros((n, 3))
            for j in range(n):
                if not (ok[j] and np.isfinite(Kn["th"][j])): Gm[j] = RS[j]; continue
                R, t = M.T(m, j); Gm[j] = RS[j] @ R; Tm[j] = RS[j] @ t
            G[g] = Gm; T[g] = Tm
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    K["G"], K["T"] = G, T
    return K


def frame_dict(K, j, p, want, held, why=None):
    f = REF.frame_dict(K, j, p, want, held, why)
    f["knee"] = dict(phi=round(float(np.degrees(K["Kn"]["phi"][j])), 3), pin_a=round(float(np.degrees(K["Kn"]["qa"][j])), 3),
                     pin_b=round(float(np.degrees(K["Kn"]["qb"][j])), 3), angle=round(float(K["Kn"]["ang"][j]), 2))
    return f


def world_pts(M, j, pts): return np.concatenate([M.world(m, j, X) for m, X in pts])


ADJ_PAIRS = []                                                                  # [(name A, member A, samples A, name B, member B, V_B, F_B)]


def set_adjacent(parts):
    """built-part pairs that move relative to each other and can meet: the chain pairs at J2 / J3 (as build_osn_l1.py),
    the knee pairs (knee link vs the E strap, the E boss, hub 3, link 2; the arm pad + its mount vs the E strap / boss /
    hub 3) - their real meshes, vertex + surface samples"""
    find = lambda s: next((p for p in parts if s in p[2]), None); ADJ_PAIRS.clear()
    for a_, b_ in (("link 1 strap", "link 2 strap"), ("link 2 strap", "link 1 strap"), ("link 2 strap", "J3 lower plate"), ("J3 lower plate", "link 2 strap"),
                   ("link 1 strap", "J2 upper boss"), ("link 2 strap", "J2 lower plate"), ("J2 lower plate", "link 2 strap"),
                   ("E strap", "link 2 strap"), ("link 2 strap", "E strap"), ("E strap", "J3 upper boss"), ("J3 upper boss", "E strap"),
                   ("knee link", "E strap"), ("E strap", "knee link"), ("knee link", "E boss"), ("knee link", "J3 upper boss"), ("knee link", "link 2 strap"),
                   ("link 2 strap", "knee link"), ("arm pad", "E boss"), ("arm pad", "E strap"), ("E strap", "arm pad"), ("pad mount", "E boss"),
                   ("pad mount", "E strap"), ("E strap", "pad mount"), ("E boss", "pad mount"), ("knee link", "pad mount"), ("arm pad", "J3"),
                   ("pad mount", "J3 lower plate"), ("pad mount", "J3 upper boss"), ("link 2 strap", "arm pad"), ("link 2 strap", "pad mount")):
        A, Bp = find(a_), find(b_)
        if A is None or Bp is None: continue
        XA = np.r_[np.asarray(A[3].vertices), trimesh.sample.sample_surface_even(A[3], 1500, seed=3)[0]]
        ADJ_PAIRS.append((A[2][:24], A[1], XA, Bp[2][:24], Bp[1], np.ascontiguousarray(Bp[3].vertices, float), np.ascontiguousarray(Bp[3].faces, np.int64)))


def adj_built(M, j):
    """min signed distance of A's samples to B's mesh over the pairs (negative = inside), and the worst pair"""
    import igl
    out, worst = 1e9, None
    for na, ma, XA, nb, mb, VB, FB in ADJ_PAIRS:
        Ra, ta = M.T(ma, j); Rb, tb = M.T(mb, j); XB = ((XA @ Ra.T + ta) - tb) @ Rb
        v = float(igl.signed_distance(np.ascontiguousarray(XB), VB, FB)[0].min())
        if v < out: out, worst = v, f"{na} / {nb}"
    return out, worst


def extra_checks(M, j):
    """the verifier's added part checks at one pose: knee link vs hub 3 ABOVE its lower plate (rides with link 2: 1 mm),
    E boss vs hubs 1-2 and link 1 (1 mm) and link 2 (adjacent at J3: 0.15 mm). (min clearance, adjacent clearance)"""
    from scipy.spatial import cKDTree
    D = M.D; u, c = D.u, D.c; sn = D.sn; fr = M.fr; tr = M.tr; tp = D.p["tp"]; h = T_LINK / 2
    if not hasattr(M, "_xc"):
        _, X = M.cyl_surf["hub3"]; cen3 = c[2] + M.f[2] * u[2]; M._H3up = X[((X - cen3) @ u[2]) >= UP - 1e-6]
        e, f = S.frame_of(sn); ang = np.linspace(0, 2 * np.pi, 24, endpoint=False); dd = S.disc(BOSS_R, 1.0)
        M._boss = np.concatenate([fr["A0"] + z * sn + BOSS_R * (np.cos(ang)[:, None] * e + np.sin(ang)[:, None] * f) for z in (tr, tr + tp / 2, tr + tp)]
                                 + [fr["A0"] + z * sn + dd[:, :1] * e + dd[:, 1:] * f for z in (tr, tr + tp)]); M._xc = True
    R3, t3 = M.T(3, j); bx = M._boxes_at_final(j); kc, kR, kh = bx["knee"]
    v = {"knee-hub3up": float(M.sd_box(M._H3up @ R3.T + t3, kc, kR, kh).min())}
    bw = M._boss @ R3.T + t3
    cyl = {k: (M.T(m, j)[0] @ cc + M.T(m, j)[1], M.T(m, j)[0] @ ax) for k, (m, cc, ax) in M.cyl.items()}
    st = {k: X @ M.T(m, j)[0].T + M.T(m, j)[1] for k, (m, X) in M.strap.items()}
    v["boss-hub1"] = float(M.sd_cyl(bw, *cyl["hub1"], r=M.hr[0]).min()); v["boss-hub2"] = float(M.sd_cyl(bw, *cyl["hub2"], r=M.hr[1]).min())
    if len(st["L1"]): v["boss-L1"] = float(cKDTree(st["L1"]).query(bw)[0].min()) - h
    c3w, ax3 = cyl["hub3"]; w = st["L2"] - c3w; far = np.linalg.norm(w - (w @ ax3)[:, None] * ax3, axis=1) > M.hr[2] + 1
    vL2 = float(cKDTree(st["L2"][far]).query(bw)[0].min()) - h if far.any() else 1e9
    return min(v.values()), vL2


def feasibility(M, K, poses, pts, jobs=1, skin=True):
    old = (M.Q, M.s, M.RS, M.X, M.K, M.q); swap_in(M, K); n = len(poses)
    try:
        kin = K["ok"] & K["kok"] & (K["res"] < 0.5)
        clear = np.full(n, np.nan); adj = np.full(n, np.nan); smin = np.full(n, np.nan); worst = [None] * n
        for j in range(n):
            if kin[j]:
                clear[j] = M.collide(j); ex, exa = extra_checks(M, j); clear[j] = min(clear[j], ex)
                adj[j] = min(exa, 1e9)
                if ADJ_PAIRS:
                    v, worst[j] = adj_built(M, j); adj[j] = min(adj[j], v + 2 * ADJ)       # built pairs: a penetration > 0.15 mm jams
        if skin:
            todo = [j for j in range(n) if kin[j] and clear[j] >= S.PART_CLEAR and adj[j] >= ADJ]
            items = [(poses[j], world_pts(M, j, pts)) for j in todo]
            if jobs > 1:
                import multiprocessing as mp
                with mp.get_context("fork").Pool(jobs) as pool: vals = pool.map(REF.skin_min, items, chunksize=4)
            else: vals = list(map(REF.skin_min, items))
            for j, v in zip(todo, vals): smin[j] = v
    finally: M.Q, M.s, M.RS, M.X, M.K, M.q = old
    return kin, clear, adj, smin, worst


_G = {}                                                                         # (M, pts) for the forked clip / workspace workers


def _clip_feas(want):
    M, pts = _G["M"], _G["pts"]; K = chain(M, want); return K, feasibility(M, K, want, pts, 1)


def _ws_feas(want):
    M = _G["M"]; K = chain(M, want); kin, clear, adj, _, _ = feasibility(M, K, want, [], skin=False); return kin, clear, adj


def make_clips(M, pts, jobs):
    C = json.load(open(os.path.join(FULL, "designs", TEMPLATE, "clips.json"))); out = []; stats = {}
    wants = [np.array([f["want"] for f in cl["frames"]], float) for cl in C["clips"]]; _G.update(M=M, pts=pts)
    if jobs > 1:                                                                # one clip per process (fork: M, pts, ADJ_PAIRS shared)
        import multiprocessing as mp
        with mp.get_context("fork").Pool(min(jobs, len(wants))) as pool: RES = pool.map(_clip_feas, wants, chunksize=1)
    else: RES = [_clip_feas(w) for w in wants]
    for cl, want, (K, (kin, clear, adj, smin, worst)) in zip(C["clips"], wants, RES):
        frames = []; last = None; nheld = 0; whyc = {}; wp = {}
        for j in range(len(want)):
            why = None
            if not K["ok"][j]: why = "fold"
            elif not K["kok"][j]: why = "knee"
            elif K["res"][j] >= 0.5: why = "closure"
            elif clear[j] < S.PART_CLEAR: why = "parts"
            elif adj[j] < ADJ: why = "adjacent"; wp[worst[j]] = wp.get(worst[j], 0) + 1
            elif not smin[j] >= 0.0: why = "skin"
            ok = why is None
            if ok and last is not None:
                dq = np.abs((K["qq"][j] - K["qq"][last] + 180) % 360 - 180).max()
                if dq > S.JUMP: ok = False; why = "flip"
                if frames and frames[-1]["held"]:
                    Rh = S.humerus(want[last]); Rw = S.humerus(want[j])
                    ang = math.degrees(math.acos(np.clip((np.trace(Rh.T @ Rw) - 1) / 2, -1, 1)))
                    if ang > RESUME: ok = False; why = why or "held"
            if ok: frames.append(frame_dict(K, j, want[j], want[j], False)); last = j
            elif last is None: frames.append(frame_dict(K, j, want[j], want[j], True, why)); nheld += 1
            else: frames.append(frame_dict(K, last, want[last], want[j], True, why)); nheld += 1
            if why: whyc[why] = whyc.get(why, 0) + 1
        out.append(dict(name=cl["name"], fps=cl.get("fps", 30.0), frames=frames))
        stats[cl["name"]] = dict(frames=len(frames), held=nheld, follow=round(1 - nheld / len(frames), 3), reasons=whyc, adjacent_pairs=wp,
                                 min_skin_mm=round(float(np.nanmin(smin)), 2) if np.isfinite(smin).any() else None,
                                 min_adj_mm=round(float(np.nanmin(adj)), 2) if np.isfinite(adj).any() else None,
                                 knee_angle=[round(float(np.nanmin(K["Kn"]["ang"][kin])), 1), round(float(np.nanmax(K["Kn"]["ang"][kin])), 1)] if kin.any() else None)
        print(f"  clip {cl['name']:24s} {len(frames)} frames, held {nheld} ({whyc}) min skin {stats[cl['name']]['min_skin_mm']} adj {stats[cl['name']]['min_adj_mm']} {wp or ''}", flush=True)
    return dict(subtitle="", clips=out), stats


def make_workspace(M, jobs=1):
    W = json.load(open(os.path.join(FULL, "designs", TEMPLATE, "workspace.json")))
    want = np.array([p["want"] for p in W["poses"]], float); K = chain(M, want); _G.update(M=M)
    if jobs > 1:
        import multiprocessing as mp
        ch = np.array_split(np.arange(len(want)), jobs)
        with mp.get_context("fork").Pool(jobs) as pool: R = pool.map(_ws_feas, [want[c] for c in ch], chunksize=1)
        kin, clear, adj = (np.concatenate([r[k] for r in R]) for k in range(3))
    else: kin, clear, adj, _, _ = feasibility(M, K, want, [], skin=False)
    poses = []
    for j in range(len(want)):
        f = frame_dict(K, j, want[j], want[j], False); f["closes"] = bool(kin[j])
        f["eval_feasible"] = bool(kin[j] and clear[j] >= S.PART_CLEAR and adj[j] >= ADJ); poses.append(f)
    return dict(envelope=W.get("envelope"), poses=poses,
                note="eval_feasible = chain closes + knee in its window + part clearance >= 1 mm + adjacent / built pairs >= 0.15 mm (no skin check)")


# ---------------------------------------------------------------------------------------------------- check vs the model
def check_frames(M, dd, parts):
    """(a) the model's metal samples (hubs, E strap, E boss, arm pad, knee link, link straps) posed by the model's own member
    transforms vs the posed exo.glb surface of their group (scene_export.frame_xforms on the frame dict = the judges' path);
    (b) every built part's vertices posed by the model's member transforms vs posed by frame_xforms. Poses (fit bench, taken):
    arm at the side (lowest), the first, the middle, the highest two, across the body and behind the back."""
    import scene_export as SE, igl
    M.Q, M.s, M.RS, M.X, M.K, M.q = M._bench; B = M.B
    taken = [i for i in range(len(B.idx)) if B.res[i] is not None and float(np.min(B.res[i])) >= 0]
    el = lambda i: B.poses[i]["elev"]; pl = lambda i: B.poses[i]["plane"]
    behind = [i for i in taken if "back" in B.clip[i].lower() or (pl(i) < -30 and el(i) > 20)]
    across = [i for i in taken if pl(i) >= 100 and el(i) >= 40]
    pick = {"arm at side": min(taken, key=el), "first": taken[0], "middle": taken[len(taken) // 2], "highest": max(taken, key=el),
            "2nd highest": sorted(taken, key=el)[-2]}
    if behind: pick["behind the back"] = max(behind, key=lambda i: -pl(i))
    if across: pick["across the body"] = max(across, key=pl)
    src = trimesh.load(os.path.join(dd, "exo.glb"))
    K = chain(M, np.array([[B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(B.idx))]))
    grp_of = {0: "base", 1: "l1", 2: "l2", 3: "l3", 6: "l4", 5: "H"}; out = []
    for lab, i in pick.items():
        pz = [B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")]; fr = frame_dict(K, i, pz, pz, False)
        X, _ = SE.frame_xforms(fr); meshes = {}; posed = {}
        for node in src.graph.nodes_geometry:
            g = node.split("|")[0]
            if g == "F" or (g == "H" and not any(s in node for s in ("arm pad", "pad mount"))): continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            m.vertices = m.vertices @ np.asarray(R).T + t; meshes.setdefault(g, []).append(m); posed["|".join(node.split("|")[:2])] = m
        meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}
        res = {}
        for name, (m, Xp) in list(M.rigid.items()) + list(M.link_pts.items()):
            Pw = M.world(m, i, Xp); g = "l1" if name == "hub1" else grp_of[m]
            d = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes[g].vertices, float),
                                                        np.ascontiguousarray(meshes[g].faces, np.int64))[0])
            res[name] = [round(float(d.max()), 4), round(float(np.percentile(d, 95)), 4)]
            if name in ("L1", "L2"):                                    # the stated hub-zone lift (link_solid): inside / outside
                lk = next(x for x in M.geo.links if x["name"] == name); D = M.D; zone = np.zeros(len(Xp), bool)
                for kk in (lk["ka"], lk["kb"]):
                    w = Xp - D.c[kk]; zone |= np.linalg.norm(w - (w @ D.u[kk])[:, None] * D.u[kk], axis=1) < M.hr[kk] + 2.5 + 0.5
                res[name + " outside hub zones"] = [round(float(d[~zone].max()), 4) if (~zone).any() else None, int((~zone).sum())]
                res[name + " hub zones (lifted)"] = [round(float(d[zone].max()), 4) if zone.any() else None, int(zone.sum())]
        fdev = 0.0
        for g, mem, nm, mesh, mat in parts:
            Vw = M.world(mem, i, np.asarray(mesh.vertices)); Pg = np.asarray(posed[f"{g}|{nm}"].vertices)
            fdev = max(fdev, float(np.abs(Vw - Pg).max()))
        worst = max(v[0] for k, v in res.items() if not k.startswith(("L1", "L2"))); worst_l = max(v[0] for k, v in res.items() if k in ("L1", "L2"))
        worst_o = max((res[k][0] or 0) for k in ("L1 outside hub zones", "L2 outside hub zones"))
        out.append(dict(label=lab, bench_pose=int(i), pose=[round(float(x), 2) for x in pz[:3]], rigid_samples_max_mm=round(worst, 4),
                        strap_samples_max_mm=round(worst_l, 4), strap_samples_outside_hub_zones_max_mm=round(worst_o, 4), per_part=res, frame_dev_mm=round(fdev, 6), res_deg=round(float(K["res"][i]), 4),
                        knee_angle=round(float(K["Kn"]["ang"][i]), 1)))
        print(f"  check {lab:16s} pose {i} {np.round(pz[:3], 1)}: model rigid samples vs posed glb max {worst:.4f} mm, straps {worst_l:.3f} mm ({worst_o:.3f} outside the lifted hub zones), "
              f"built-part frames dev {fdev:.2e} mm, knee {K['Kn']['ang'][i]:.1f} deg", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="l1_skin-normal-3r-pin-knee")
    ap.add_argument("--params"); ap.add_argument("--params-file"); ap.add_argument("--k", type=int); ap.add_argument("--hubs")
    ap.add_argument("--jobs", type=int, default=1); ap.add_argument("--no-clips", action="store_true")
    a = ap.parse_args(); t0 = time.time()
    dd = os.path.join(FULL, "designs", a.out); os.makedirs(dd, exist_ok=True)
    P0, src = params_from(a); M, rep = fit(P0); D = M.D; P = M.p
    print(f"fit ({src}) on Bench(60,160) {M.B.mode}: gap {rep['gap']} reach {rep['reach']} follow {rep['follow']} ib14 {rep['inband14']} "
          f"ib10 {rep['inband10']} contact {rep['contact']} f {rep['f']} tr {M.tr:.2f} m {np.round(D.m, 3)} hubs {M.hr} ({time.time() - t0:.0f} s)", flush=True)
    parts, stack = build_parts(M)
    up = user_parts(); bot = next(m for g, n, m in up if n.startswith("BOTTOM"))
    bottom_c = np.asarray(bot.vertices) @ HR                                    # rest (H) -> canonical arm frame
    mount, mrep = pad_mount(M, bottom_c)
    if mount is not None: parts.append(("H", 5, f"pad mount to BOTTOM (proxy) ({P['tp']} mm slab at the pad level, arm pad -> the BOTTOM bar's end)", mount, "ti"))
    def export_mesh(g, mem, m):
        if mem != 5: return m
        return trimesh.Trimesh(np.asarray(m.vertices) @ HR.T, m.faces, process=False)     # x_H = HR x
    sc = trimesh.Scene(); pf = []
    allp = [(g, n, export_mesh(g, mem, m), mat) for g, mem, n, m, mat in parts] + [(g, n, m, "user") for g, n, m in up]
    for i, (g, n, m, mat) in enumerate(allp):
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        user = mat == "user"; mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else 0.0
        rho = STEEL if mat == "steel" else TI
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material="user part" if user else ("steel" if mat == "steel" else "Ti-6Al-4V"),
                       mass_g=None if user else round(vol / 1000 * rho, 2), valid=bool(user or (mm.is_watertight and mm.is_volume)),
                       pieces=None if user else int(len(mm.split(only_watertight=False))), faces=len(m.faces)))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=3, level="L1 keep-out", FACES={str(j + 1): round(float(M.f[j]), 2) for j in range(3)}, parts=pf),
              open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    ours = [p for p in pf if p["material"] != "user part"]
    print(f"exo.glb: {len(parts)} keep-out parts ({sum(p['mass_g'] or 0 for p in ours):.1f} g) + {len(up)} user parts; invalid: "
          f"{[p['name'] for p in ours if not p['valid'] or p['pieces'] != 1] or 'none'}; mount {mrep}; stack {stack}", flush=True)
    u1, u2, u3 = D.u; w_d = math.degrees(math.acos(float(np.clip(-u3[1], -1, 1)))); w_a = math.degrees(math.atan2(u3[0], u3[2]))
    az = math.degrees(math.atan2(u1[2], -u1[0])); elv = math.degrees(math.asin(float(np.clip(u1[1], -1, 1))))
    chk = S.circ_int(S.bvec(az, elv), D.A[0], S.w_dir(w_d, w_a), D.A[1], D.branch)
    kin = dict(az=az, el=elv, a=[math.degrees(D.A[0]), math.degrees(D.A[1])], w=[w_d, w_a], branch=int(D.branch), order=[0, 1, 1],
               axis_points_mm=[np.round(c_, 3).tolist() for c_ in D.c], axes=[np.round(u_, 6).tolist() for u_ in D.u],
               axis_line_offsets_mm=[round(float(np.linalg.norm(c_)), 2) for c_ in D.c], u2_check_deg=round(math.degrees(math.acos(float(np.clip(chk @ u2, -1, 1)))), 5),
               seats=dict((k_, P[k_]) for k_ in ("az1", "el1", "az2", "el2", "wd", "wa", "b3")),
               knee=dict((k_, P[k_]) for k_ in ("lE", "lc", "phiE", "phib", "stk", "ang_min")), knee_mid_m_mm=np.round(D.m, 3).tolist(), hub_r_mm=list(M.hr))
    pr = {k_: v for k_, v in P0.items()}
    design = dict(id=a.out, source=f"docs/concepts/{ID}.md, {src}, fit on Bench(60,160) {M.B.mode} = the shape the verifier wore frozen on Bench(110,360) exact",
                  params=pr, n_joints=3, sliding_cuff=False, dof=3,
                  passive=dict(count=2, translations=0, rotations=2, outside_dof_count=True,
                               kind="flat two-pin knee closing the 3R loop at the cuff (planar RRR with J3: pins a, b parallel to J3); set by loop closure, nothing sags",
                               components=[dict(pin="a", between="member 3 (E boss) / knee link", part="IGLIDUR-PIN: iglidur GSM sleeve + 2 GTM washers on an integral O4 Ti pin",
                                                stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]]),
                                           dict(pin="b", between="knee link / arm pad (cuff)", part="IGLIDUR-PIN (as pin a)", stack_mm=P["stk"], plates_mm=[P["tp"], P["tp"]])]),
                  joints=[dict(joint=f"J{k + 1}", part=f"O{2 * M.hr[k]:.0f} x 12.25 hub, MR117-2RS pair ({MK.HUBS.get(M.hr[k], '')})", axis_offset_mm=kin["axis_line_offsets_mm"][k]) for k in range(3)],
                  kinematics=kin, base=dict(mount="girdle", chain="osn3_pinknee", note="base rides the scapula on the user's scapula handler"),
                  built_with="pipeline/concept_l1/build_pinknee_l1.py (L1 keep-out meshes: declared hub keep-outs, fitted 8 x 3 straps, E strap + boss, knee link, arm pad)",
                  label=f"skin-normal-3r-pin-knee ({src}), L1 keep-out", faces_mm=[round(float(x), 2) for x in M.f], tr=round(float(M.tr), 2), stack_mm=stack,
                  bench=dict((k_, rep[k_]) for k_ in ("gap", "reach", "follow", "inband14", "inband10", "contact")),
                  note="R17's dynamics judge models the orientation-equivalent spherical chain (kinematics az/el/a/w); the J3 line offset "
                       f"({kin['axis_line_offsets_mm'][2]} mm) and the knee's 2 passive pins are not in its MuJoCo model")
    json.dump(design, open(os.path.join(dd, "design.json"), "w"), indent=1, default=float)
    set_adjacent(parts)
    pts = [(m, X) for m, X in M.rigid.values()] + [(m, X) for m, X in M.link_pts.values()] + list(M.contact)
    for g, mem, n, m, mat in parts:
        pts.append((mem, np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 300, seed=1)[0]]))
    rep_out = dict(fit=dict(params=pr, source=src, bench="60,160", mode=M.B.mode,
                            report={k_: rep.get(k_) for k_ in ("gap", "reach", "follow", "inband14", "inband10", "contact", "why", "f", "min_clear_taken", "parts_ib14", "knee", "hubs")},
                            m=np.round(D.m, 3).tolist(), tr=round(float(M.tr), 3)), stack=stack, mount=mrep, kin_u2_check_deg=kin["u2_check_deg"])
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep_out["check"] = check_frames(M, dd, parts)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    if not a.no_clips:
        C, st = make_clips(M, pts, a.jobs); C["subtitle"] = design["label"]
        C["design"] = dict(n=3, hub_r=max(M.hr), **{k_: kin[k_] for k_ in ("az", "el", "a", "w", "branch", "order")})
        json.dump(C, open(os.path.join(dd, "clips.json"), "w"), separators=(",", ":"))
        rep_out["clips"] = st; json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
        print(f"clips.json written ({time.time() - t0:.0f} s)", flush=True)
        W = make_workspace(M, a.jobs); json.dump(W, open(os.path.join(dd, "workspace.json"), "w"), separators=(",", ":"))
        rep_out["workspace"] = dict(poses=len(W["poses"]), closes=round(float(np.mean([p["closes"] for p in W["poses"]])), 4),
                                    feasible_kin_parts=round(float(np.mean([p["eval_feasible"] for p in W["poses"]])), 4))
        print(f"workspace.json: {rep_out['workspace']} ({time.time() - t0:.0f} s)", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s -> {dd}")


if __name__ == "__main__":
    main()
