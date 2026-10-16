"""L1 keep-out CAD of an offset-skin-normal-3r configuration (docs/concepts/offset-skin-normal-3r.md, default k 4216)
-> a judge-ready design dir pipeline/full-exo/designs/<out>/ (exo.glb, clips.json, workspace.json, design.json,
parts_full.json, build.json).

The shape is the concept model's own fit (osn Model = the seed-offset-3r-slides VModel checks + the inverted along
guide), refitted on the bench the configuration was searched on (Bench(60,160) fast: the claimed 32.61). The chain
(hubs, links, member 3's neck) is built from that fit at real size; the slide stage is built from the REAL catalogue
parts (tools/hardware_catalogue.json), not the model's 20 x 20 x 4 boxes:
  * hubs: O20 keep-outs (docs/HARDWARE.md v5, MR117 pairs): lower member's plate F..F+3, upper member's boss + cap
    F+3.15..F+12.25 (as build_seed_offset_l1.py);
  * links 1, 2: 8 x 3 mm straps through the model's fitted underside samples; the station past each hub rim is kept at
    or above that hub's member level (link 2 never dips into the next member's plate: the seed L1's R6 finding);
  * along guide, INVERTED THK RSR3M / HIWIN MGN03C (H 4.0, block W 8 x L 12, rail 3 x 2.6): the block (U keep-out, rail
    channel 3.4 wide) on a 1.5 mm cuff base plate (arm-fixed, at the stage's mid travel), its rail
    (12 + 2 S_a + 2 mm long) riding with carriage A;
  * carriage A = a 1 mm plus-shaped adapter plate under both rails (5 mm wide arms);
  * across guide, a second RSR3M crosswise: rail (12 + 2 S_t + 2 mm) on the adapter, its block = carriage B (member 3);
  * stack 1.5 + 4 + 1 + 4 = 10.5 mm from the model's fitted cuff level t_r (the model carried 13.5 mm). Member 3 above
    the stage is the model's (hub 3 plate, the ramped neck that ends at the model's carriage-B top t_r + 13.5); the
    bridge joins the neck end to the real block's top (t_r + 10.5..t_r + 16.5, over the block);
  * the cuff mount: a 1.5 mm slab from the base plate to the end of the user's BOTTOM bar (H group, "(proxy)");
  * the user's arm parts (H, F groups) from the champion's parametric build, minus that build's own arm end.
Member frames (clips.json "G" + "T" per group, scene_export.frame_xforms) reproduce the model's kinematics exactly:
world = RS (R_m x + t_m) for member m (x in the model's member-local rest coordinates); member 4 (along rail + carriage
A + across rail) is RS Q (x + s_a sa + m_t st + m_n sn) (the model's centred stage); the arm-fixed parts sit in the
humerus group H at x_H = HR (x + m) (m = the stage's mid travel).
Clip frames (30 fps, the champion's clips incl. the held-out Wave / Walking - judged, never fitted) are followed when
the chain closes on the design branch >= 10 deg from the J2 fold, the slides are in range, the closure residual is
< 0.5 deg, no joint steps > 25 deg, non-adjacent parts keep >= 1 mm (the model's collide incl. the moving rail), link 2
keeps 0.15 mm from member 3 (the verifier's adjacent check), and no metal sample - the model's, the verifier's outer
faces, and every BUILT part's own surface samples - is inside the exact posed skin; otherwise the arm is held at the
last followed pose until the motion comes back within RESUME deg.

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/build_osn_l1.py [--out ID] [--bench 60,160] [--jobs 2] [--no-clips]
"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo")); sys.path.insert(0, HERE)
import concept_bench as CB                                                      # noqa: E402
import build_seed_offset_l1 as REF                                              # noqa: E402  (mesh helpers, the user's parts)
BP = CB.BP


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


VER = _load("osn_verify", os.path.join(REPO, "docs", "concepts", "verify", "offset-skin-normal-3r.py"))   # its checks + batched run
OSN, S = VER.OSN, VER.S
FULL = os.path.join(REPO, "pipeline", "full-exo"); TEMPLATE = REF.TEMPLATE; USER_SRC = "l1_seed-offset-3r-slides"
HUB_R, CROWN, UP, T_LINK, W_LINK = S.HUB_R, S.CROWN, S.UP, S.T_LINK, S.W_LINK
PLATE = 3.0; RESUME = 4.0; ADJ = 0.15
HR = REF.HR; unit = S.unit
HW = {g["id"]: g for g in json.load(open(os.path.join(REPO, "tools", "hardware_catalogue.json")))["linear_guides"]}
G = HW["THK-RSR3M"]                                                             # H 4.0, W 8, L 12, rail 3 x 2.6
GH, GW, GL, RW, RH = G["H"], G["W"], G["L"], G["rail_W"], G["rail_H"]
H1 = 1.0                                                                        # rail bottom -> block body (RSR3M H1, [est])
BASE_T, ADAPT_T, ARM_W, CH = 1.5, 1.0, 5.0, 0.2                                 # base plate, carriage-A adapter, its arm width, channel play
STEEL = 7.85


# ---------------------------------------------------------------------------------------------------- meshes (L1)
def prism(poly, tris, h):
    """closed prism of a CCW 2-D polygon (n, 2) with the given cap triangulation, z 0..h"""
    P = np.asarray(poly, float); n = len(P)
    V = np.r_[np.c_[P, np.zeros(n)], np.c_[P, np.full(n, h)]]
    F = [[c, b, a] for a, b, c in tris] + [[a + n, b + n, c + n] for a, b, c in tris]
    for i in range(n):
        j = (i + 1) % n; F += [[i, j, j + n], [i, j + n, i + n]]
    m = trimesh.Trimesh(V, np.array(F), process=True); trimesh.repair.fix_normals(m); return m


def u_block(width, depth, ch_w, ch_d, length):
    """U section (x across +-width/2, y 0..depth, channel ch_w wide x ch_d deep open at y = depth) extruded along z"""
    w, cw = width / 2, ch_w / 2; y0 = depth - ch_d
    poly = [(-w, 0), (w, 0), (w, depth), (cw, depth), (cw, y0), (-cw, y0), (-cw, depth), (-w, depth)]
    return prism(poly, [(0, 1, 4), (0, 4, 5), (1, 2, 3), (1, 3, 4), (0, 5, 6), (0, 6, 7)], length)


def plus_plate(La, Lt, w, t):
    """plus-shaped plate: arm along x (+-La), arm along y (+-Lt), arm width 2 w, thickness t (z 0..t)"""
    poly = [(La, -w), (La, w), (w, w), (w, Lt), (-w, Lt), (-w, w), (-La, w), (-La, -w), (-w, -w), (-w, -Lt), (w, -Lt), (w, -w)]
    tris = [(11, 2, 5), (11, 5, 8), (0, 1, 2), (0, 2, 11), (2, 3, 4), (2, 4, 5), (5, 6, 7), (5, 7, 8), (8, 9, 10), (8, 10, 11)]
    return prism(poly, tris, t)


def place(m, origin, ex, ey, ez):
    """local (x, y, z) -> origin + x ex + y ey + z ez"""
    m = m.copy(); R = np.stack([ex, ey, ez], 1); m.vertices = np.asarray(m.vertices) @ R.T + origin
    if np.linalg.det(R) < 0: m.invert()
    return m


def sbox(D, cs, x0, x1, y0, y1, z0, z1):
    """box in the stage frame (sa, st, sn) around cs: along x0..x1, across y0..y1, height z0..z1"""
    Rst = np.stack([D.sa, D.st, D.sn], 1)
    return REF.box(cs + 0.5 * (x0 + x1) * D.sa + 0.5 * (y0 + y1) * D.st + 0.5 * (z0 + z1) * D.sn, Rst, [x1 - x0, y1 - y0, z1 - z0])


# ---------------------------------------------------------------------------------------------------- the fitted model
def fit(bench, k):
    L = json.load(open(os.path.join(REPO, "docs", "concepts", "sweeps", "offset-skin-normal-3r.json")))
    e = next(x for x in L if x.get("k") == k); P = dict(e["params"])
    B = CB.Bench(*bench); M = OSN.Model(B, dict(P)); r = M.run(); M._bench = (M.Q, M.s, M.RS, M.X)
    return M, r, e


def link_solid(M, lk, rows):
    """strap 8 x 3 mm through the model's fitted underside samples, one station past each hub rim; the past-rim station
    is lifted to that hub's member level (no dip into the neighbouring member's plate)"""
    D = M.D; u, c = D.u, D.c; F = M.f
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
    J = np.arange(j0, j1 + 1)
    Bot = np.stack([cols_d[q][J] * cols_r[q][J][:, None] for q in range(len(cols_d))], 1)
    Off = T_LINK * np.stack([cols_d[q][J] for q in range(len(cols_d))], 1)
    return REF.grid_solid(Bot, Off)


def build_parts(M):
    """[(group, member, name, mesh in the MEMBER-LOCAL rest frame, material)]; member 5 = arm-fixed (before the mid offset)"""
    D = M.D; P = D.p; u, c = D.u, D.c; F = M.f; tr = M.tr; sa, st, sn = D.sa, D.st, D.sn
    cs = D.stage_c(); neck = P["neck"]; Sa, St = P["S_a"], P["S_t"]
    ztop_m = M.zb + S.CAR_H                                                     # the model's carriage-B top = the neck's end level
    H = lambda k: c[k] + F[k] * u[k]; out = []
    out.append(("base", 0, "J1 upper boss + cap keep-out (O20, F+3.15..F+12.25; base = J1's upper member)", REF.cyl(H(0), u[0], UP, CROWN), "ti"))
    out.append(("l1", 1, "J1 lower plate keep-out (O20 x 3, link 1)", REF.cyl(H(0), u[0], 0.0, PLATE), "ti"))
    out.append(("l1", 1, "J2 lower plate keep-out (O20 x 3, link 1)", REF.cyl(H(1), u[1], 0.0, PLATE), "ti"))
    out.append(("l2", 2, "J2 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2)", REF.cyl(H(1), u[1], UP, CROWN), "ti"))
    out.append(("l2", 2, "J3 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2)", REF.cyl(H(2), u[2], UP, CROWN), "ti"))
    out.append(("l3", 3, "J3 lower plate keep-out (O20 x 3, member 3)", REF.cyl(H(2), u[2], 0.0, PLATE), "ti"))
    prof = REF.link_profiles(M)
    for nm, grp, mem in (("L1", "l1", 1), ("L2", "l2", 2)):
        lk, rows = prof[nm]; out.append((grp, mem, f"link {nm[1]} strap keep-out (8 x 3 mm Ti, fitted underside)", link_solid(M, lk, rows), "ti"))
    # member 3: the model's neck (<= 60 deg ramp from the J3 plate level to the model's carriage-B top), as fitted
    kr = math.tan(S.RAMP * S.D2R)
    xs = np.unique(np.r_[np.linspace(HUB_R - 2.0, HUB_R + neck, 40), HUB_R + neck - (ztop_m - F[2]) / kr])
    xs = xs[(xs >= HUB_R - 2.0) & (xs <= HUB_R + neck)]
    hh = np.maximum(F[2], ztop_m - kr * (HUB_R + neck - xs)); ys = np.array([-W_LINK / 2, 0.0, W_LINK / 2])
    Bot = c[2][None, None] + xs[:, None, None] * sa + ys[None, :, None] * st + hh[:, None, None] * sn
    out.append(("l3", 3, "member-3 neck keep-out (8 x 3 mm, ramp <= 60 deg from the J3 plate to the bridge)", REF.grid_solid(Bot, np.broadcast_to(T_LINK * sn, Bot.shape).copy()), "ti"))
    # the real stage, heights z from the fitted cuff level tr along sn, around the stage centre cs
    z_blk0 = BASE_T; z_rail0 = BASE_T + GH - RH; z_rail1 = BASE_T + GH                   # inverted along guide
    z_ad1 = z_rail1 + ADAPT_T; z_xr1 = z_ad1 + RH; z_xb0 = z_ad1 + H1; z_xb1 = z_ad1 + GH  # adapter, across rail, across block
    LA, LT = GL + 2 * Sa + 2.0, GL + 2 * St + 2.0                                       # real rail lengths (travel + block + 2)
    o = lambda z: cs + (tr + z) * sn
    out.append(("H", 5, f"cuff base plate (proxy) ({GL + 2:.0f} x {GW + 2:.0f} x {BASE_T} mm, arm-fixed, under the along block)",
                sbox(D, cs, -(GL / 2 + 1), GL / 2 + 1, -(GW / 2 + 1), GW / 2 + 1, tr, tr + BASE_T), "ti"))
    blk = u_block(GW, GH - H1, RW + 2 * CH, z_rail1 - z_rail0 - H1 + CH, GL)          # section (across, height), extruded along
    out.append(("H", 5, f"along guide block (proxy) (THK RSR3M / HIWIN MGN03C, inverted: W {GW} x L {GL}, body {GH - H1} mm, on the cuff)",
                place(blk, o(z_blk0) - (GL / 2) * sa, st, sn, sa), "steel"))
    out.append(("l4", 4, f"along guide rail (RSR3M rail {RW} x {RH} x {LA:.1f} mm, rides with carriage A)",
                sbox(D, cs, -LA / 2, LA / 2, -RW / 2, RW / 2, tr + z_rail0, tr + z_rail1), "steel"))
    out.append(("l4", 4, f"carriage A adapter keep-out (plus plate {ADAPT_T} mm, arms {ARM_W} wide, under both rails)",
                place(plus_plate(LA / 2, LT / 2, ARM_W / 2, ADAPT_T), o(z_rail1), sa, st, sn), "ti"))
    out.append(("l4", 4, f"across guide rail (RSR3M rail {RW} x {RH} x {LT:.1f} mm, crosswise on carriage A)",
                sbox(D, cs, -RW / 2, RW / 2, -LT / 2, LT / 2, tr + z_ad1, tr + z_xr1), "steel"))
    xblk = u_block(GW, GH - H1, RW + 2 * CH, z_xr1 - z_xb0 + CH, GL)                  # section (along, height from the top), extruded across
    out.append(("l3", 3, f"carriage B = across guide block (THK RSR3M / HIWIN MGN03C: W {GW} x L {GL}, body {GH - H1} mm)",
                place(xblk, o(z_xb1) - (GL / 2) * st, sa, -sn, st), "steel"))
    x_neck = -(S.CAR_L / 2 + Sa)                                                        # the neck's end, along from cs
    # bridge: one stepped section (along, height) extruded 8 mm across - neck end .. the model's carriage-B edge at the neck's
    # top (as the model's bridge), then over the block at the model's carriage-B top (inside the model's carriage-B box)
    xa, xb, xc = x_neck - 1.0, -S.CAR_L / 2, GW / 2; z0, z1, z2 = tr + z_xb1, ztop_m, ztop_m + T_LINK
    br = prism([(xa, z0), (xc, z0), (xc, z1), (xb, z1), (xb, z2), (xa, z2)], [(0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 5)], W_LINK)
    out.append(("l3", 3, "member-3 bridge keep-out (8 wide, stepped: neck end at the neck top, over carriage B at the model's carriage-B top)",
                place(br, cs + (W_LINK / 2) * st, sa, sn, -st), "ti"))
    stack = dict(base=[0, BASE_T], along_block=[z_blk0, z_blk0 + GH - H1], along_rail=[round(z_rail0, 2), z_rail1], adapter=[z_rail1, z_ad1],
                 across_rail=[z_ad1, round(z_xr1, 2)], across_block=[z_xb0, z_xb1], total=z_xb1, model_total=round(ztop_m - tr, 2),
                 rails_mm=dict(along=round(LA, 1), across=round(LT, 1)), bridge=[round(z_xb1, 2), round(ztop_m + T_LINK - tr, 2)])
    return out, stack


def cuff_mount(M, bottom_c):
    """1.5 mm slab from the base plate to the user's BOTTOM bar (canonical arm frame; member-5 local before the mid offset)"""
    D = M.D; sa, st, sn = D.sa, D.st, D.sn; cs = D.stage_c(); tr = M.tr; mv = D.m[0] * sa + D.m[1] * st + D.m[2] * sn
    rel = bottom_c - (cs + mv); a_, t_ = rel @ sa, rel @ st; end = GL / 2 + 1.0
    rep = {}
    for sgn in (1, -1):
        near = (sgn * a_ > end - 2) & (sgn * a_ < end + 40)
        if near.any(): rep[sgn] = (int(near.sum()), float(np.median(np.abs(a_[near]))), float(np.median(t_[near])))
    if not rep: return None, dict(note="no BOTTOM vertices within 40 mm of the base plate along the arm")
    sgn = max(rep, key=lambda s: rep[s][0]); near = (sgn * a_ > end - 2) & (sgn * a_ < end + 40)
    a1 = min(float(np.percentile(sgn * a_[near], 60)), end + 30.0); tb = float(np.median(t_[near]))
    t0, t1 = min(-(GW / 2 + 1), tb - 4), max(GW / 2 + 1, tb + 4)
    x0, x1 = (end - 1.0, a1) if sgn > 0 else (-a1, -(end - 1.0))
    m = sbox(D, cs, x0, x1, t0, t1, tr, tr + BASE_T)
    return m, dict(side="distal" if sgn > 0 else "proximal", along=[round(x0, 1), round(x1, 1)], across=[round(t0, 1), round(t1, 1)],
                   height=[round(tr, 1), round(tr + BASE_T, 1)], bottom_verts_near=rep[sgn][0])


def user_parts():
    """the user's arm parts (H, F groups, rest frame) as the other L1 builds carry them (the user's BOTTOM bar cut at s 255,
    the conformal upper cuff; taken from l1_seed-offset-3r-slides minus its own proxies: the champion's param2 build now
    fuses BOTTOM with its own arm end)"""
    s = trimesh.load(os.path.join(FULL, "designs", USER_SRC, "exo.glb")); out = []
    for node in s.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if g not in ("H", "F") or "(proxy)" in n: continue
        T_, gn = s.graph[node]; m = s.geometry[gn].copy(); m.apply_transform(T_); out.append((g, n, m))
    return out


# ---------------------------------------------------------------------------------------------------- kinematics per pose
def chain(M, poses):
    D = M.D; RS = np.array([S.scap(float(p[1])) for p in poses]); RH = np.array([S.humerus(p) for p in poses])
    Q = np.einsum("nji,njk->nik", RS, RH); q, ok, X1, X2, X3, s = D.ik(Q)
    R123 = X3[0]; res = np.degrees(np.arccos(np.clip((np.einsum("nij,nij->n", R123, Q) - 1) / 2, -1, 1)))
    sok = D.slides_ok(s); m = D.m
    loc4 = s[:, :1] * D.sa[None] + m[1] * D.st[None] + m[2] * D.sn[None]
    Gd = {"base": RS, "l1": RS @ X1[0], "l2": RS @ X2[0], "l3": RS @ X3[0], "l4": RS @ Q}
    T = {"base": np.zeros((len(Q), 3)), "l1": np.einsum("nij,nj->ni", RS, X1[1]), "l2": np.einsum("nij,nj->ni", RS, X2[1]),
         "l3": np.einsum("nij,nj->ni", RS, X3[1]), "l4": np.einsum("nij,nj->ni", RS @ Q, loc4)}
    return dict(q=np.degrees(q), ok=ok, sok=sok, res=res, G=Gd, T=T, s=s, Q=Q, RS=RS, X={1: X1, 2: X2, 3: X3})


def swap_in(M, K): M.Q, M.s, M.RS = K["Q"], K["s"], K["RS"]; M.X = K["X"]


def world_pts(M, j, pts): return np.concatenate([M.scap_pts(m, j, X) @ M.RS[j].T for m, X in pts])


def feasibility(M, K, poses, pts, jobs=1, skin=True):
    swap_in(M, K); n = len(poses)
    kin = K["ok"] & K["sok"] & (K["res"] < 0.5)
    clear = np.full(n, np.nan); adj = np.full(n, np.nan); smin = np.full(n, np.nan)
    for j in range(n):
        if kin[j]:
            clear[j] = M.collide(j); v = VER.l2_vs_member3(M, j); adj[j] = min(v.values()) if v else 1e9
    if skin:
        todo = [j for j in range(n) if kin[j] and clear[j] >= S.PART_CLEAR and adj[j] >= ADJ]
        items = [(poses[j], world_pts(M, j, pts)) for j in todo]
        if jobs > 1:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(jobs) as pool: vals = pool.map(REF.skin_min, items, chunksize=4)
        else: vals = list(map(REF.skin_min, items))
        for j, v in zip(todo, vals): smin[j] = v
    return kin, clear, adj, smin


def make_clips(M, pts, jobs):
    C = json.load(open(os.path.join(FULL, "designs", TEMPLATE, "clips.json"))); out = []; stats = {}
    for cl in C["clips"]:
        want = np.array([f["want"] for f in cl["frames"]], float)
        K = chain(M, want); kin, clear, adj, smin = feasibility(M, K, want, pts, jobs)
        frames = []; last = None; nheld = 0; whyc = {}
        for j in range(len(want)):
            why = None
            if not K["ok"][j]: why = "fold"
            elif not K["sok"][j]: why = "slide"
            elif K["res"][j] >= 0.5: why = "closure"
            elif clear[j] < S.PART_CLEAR: why = "parts"
            elif adj[j] < ADJ: why = "adjacent"
            elif not smin[j] >= 0.0: why = "skin"
            ok = why is None
            if ok and last is not None:
                dq = np.abs((K["q"][j] - K["q"][last] + 180) % 360 - 180).max()
                if dq > S.JUMP: ok = False; why = "flip"
                if frames and frames[-1]["held"]:
                    Rh = S.humerus(want[last]); Rw = S.humerus(want[j])
                    ang = math.degrees(math.acos(np.clip((np.trace(Rh.T @ Rw) - 1) / 2, -1, 1)))
                    if ang > RESUME: ok = False; why = why or "held"
            if ok: frames.append(REF.frame_dict(K, j, want[j], want[j], False)); last = j
            elif last is None: frames.append(REF.frame_dict(K, j, want[j], want[j], True, why)); nheld += 1
            else: frames.append(REF.frame_dict(K, last, want[last], want[j], True, why)); nheld += 1
            if why: whyc[why] = whyc.get(why, 0) + 1
        out.append(dict(name=cl["name"], fps=cl.get("fps", 30.0), frames=frames))
        stats[cl["name"]] = dict(frames=len(frames), held=nheld, follow=round(1 - nheld / len(frames), 3), reasons=whyc,
                                 min_skin_mm=round(float(np.nanmin(smin)), 2) if np.isfinite(smin).any() else None,
                                 min_adj_mm=round(float(np.nanmin(adj)), 2) if np.isfinite(adj).any() else None)
        print(f"  clip {cl['name']:24s} {len(frames)} frames, held {nheld} ({whyc}) min skin {stats[cl['name']]['min_skin_mm']}", flush=True)
    return dict(subtitle="", clips=out), stats


def make_workspace(M):
    W = json.load(open(os.path.join(FULL, "designs", TEMPLATE, "workspace.json")))
    want = np.array([p["want"] for p in W["poses"]], float); K = chain(M, want)
    kin, clear, adj, _ = feasibility(M, K, want, [], skin=False); poses = []
    for j in range(len(want)):
        f = REF.frame_dict(K, j, want[j], want[j], False); f["closes"] = bool(kin[j])
        f["eval_feasible"] = bool(kin[j] and clear[j] >= S.PART_CLEAR and adj[j] >= ADJ); poses.append(f)
    return dict(envelope=W.get("envelope"), poses=poses,
                note="eval_feasible = chain closes + slides in range + part clearance >= 1 mm + link 2 / member 3 >= 0.15 mm (no skin check)")


# ---------------------------------------------------------------------------------------------------- check vs the model
def check_frames(M, dd, parts, mv):
    """(a) the model's metal samples of the parts built at the model's shape (hubs, links, neck) vs the posed exo.glb
    surface of their own group; (b) every built part's vertices posed by the model's own member transforms vs posed by
    scene_export.frame_xforms on the clip frame dict (the frames themselves). Poses: first, middle and highest taken."""
    import scene_export as SE, igl
    M.Q, M.s, M.RS, M.X = M._bench
    taken = [i for i in range(len(M.B.idx)) if M.B.res[i] is not None and float(np.min(M.B.res[i])) >= 0]
    el = lambda i: M.B.poses[i]["elev"]
    pick = sorted({taken[0], taken[len(taken) // 2], max(taken, key=el), sorted(taken, key=el)[-2]})
    src = trimesh.load(os.path.join(dd, "exo.glb"))
    K = chain(M, np.array([[M.B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(M.B.idx))]))
    grp_of = {0: "base", 1: "l1", 2: "l2", 3: "l3", 4: "l4", 5: "H"}; out = []
    for i in pick:
        pz = [M.B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")]; fr = REF.frame_dict(K, i, pz, pz, False)
        X, _ = SE.frame_xforms(fr); meshes = {}; posed = {}
        for node in src.graph.nodes_geometry:
            g = node.split("|")[0]
            if g == "F" or (g == "H" and "(proxy)" not in node): continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            m.vertices = m.vertices @ np.asarray(R).T + t; meshes.setdefault(g, []).append(m); posed["|".join(node.split("|")[:2])] = m
        meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}
        res = {}
        for name, (m, Xp) in [(k, v) for k, v in M.rigid.items() if k in ("hub1", "hub2", "hub3", "neck")] + list(M.link_pts.items()):
            Pw = M.world(m, i, Xp); g = "l1" if name == "hub1" else grp_of[m]
            d = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes[g].vertices, float),
                                                        np.ascontiguousarray(meshes[g].faces, np.int64))[0])
            res[name] = [round(float(d.max()), 4), round(float(np.percentile(d, 95)), 4)]
        fdev = 0.0
        for g, mem, nm, mesh, mat in parts:
            V = np.asarray(mesh.vertices) if mem != 5 else np.asarray(mesh.vertices)       # member-local (member 5 before the mid offset)
            Vw = M.world(mem, i, V); Pg = np.asarray(posed[f"{g}|{nm}"].vertices)
            fdev = max(fdev, float(np.abs(Vw - Pg).max()))
        worst = max(v[0] for v in res.values())
        out.append(dict(bench_pose=int(i), pose=[round(float(x), 2) for x in pz[:3]], model_samples_max_mm=round(worst, 4), per_part=res,
                        frame_dev_mm=round(fdev, 6), res_deg=round(float(K["res"][i]), 4), slides=[round(float(x), 2) for x in K["s"][i]]))
        print(f"  check pose {i} {np.round(pz[:3], 1)}: model samples vs posed glb max {worst:.4f} mm, built-part frames dev {fdev:.2e} mm", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--k", type=int, default=4216); ap.add_argument("--out", default="l1_offset-skin-normal-3r")
    ap.add_argument("--bench", default="60,160"); ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--no-clips", action="store_true")
    a = ap.parse_args(); t0 = time.time()
    dd = os.path.join(FULL, "designs", a.out); os.makedirs(dd, exist_ok=True)
    M, rep, e = fit(tuple(int(x) for x in a.bench.split(",")), a.k); D = M.D; P = M.p
    print(f"fit k {a.k} on Bench({a.bench}) {M.B.mode}: gap {rep['gap']} reach {rep['reach']} follow {rep['follow']} ib14 {rep['inband14']} "
          f"ib10 {rep['inband10']} contact {rep['contact']} f {rep['f']} S {[P['S_a'], P['S_t'], P['R_r']]} m {np.round(D.m, 2)} ({time.time() - t0:.0f} s)", flush=True)
    parts, stack = build_parts(M)
    up = user_parts(); bot = next(m for g, n, m in up if n.startswith("BOTTOM"))
    bottom_c = np.asarray(bot.vertices) @ HR                                    # rest (H) -> canonical arm frame
    mount, mrep = cuff_mount(M, bottom_c)
    if mount is not None: parts.append(("H", 5, f"cuff mount to BOTTOM (proxy) ({BASE_T} mm slab, base plate -> the BOTTOM bar)", mount, "ti"))
    mv = D.m[0] * D.sa + D.m[1] * D.st + D.m[2] * D.sn
    def export_mesh(g, mem, m):
        if mem != 5: return m
        return trimesh.Trimesh((np.asarray(m.vertices) + mv) @ HR.T, m.faces, process=False)     # x_H = HR (x + m)
    sc = trimesh.Scene(); pf = []
    allp = [(g, n, export_mesh(g, mem, m), mat) for g, mem, n, m, mat in parts] + [(g, n, m, "user") for g, n, m in up]
    for i, (g, n, m, mat) in enumerate(allp):
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        user = mat == "user"; mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else 0.0
        rho = STEEL if mat == "steel" else 4.43
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material="user part" if user else ("steel (catalogue guide)" if mat == "steel" else "Ti-6Al-4V"),
                       mass_g=None if user else round(vol / 1000 * rho, 2), valid=bool(user or (mm.is_watertight and mm.is_volume)),
                       pieces=None if user else int(len(mm.split(only_watertight=False))), faces=len(m.faces)))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=3, level="L1 keep-out", FACES={str(j + 1): round(float(M.f[j]), 2) for j in range(3)}, parts=pf),
              open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    ours = [p for p in pf if p["material"] != "user part"]
    print(f"exo.glb: {len(parts)} keep-out parts ({sum(p['mass_g'] or 0 for p in ours):.1f} g) + {len(up)} user parts; invalid: "
          f"{[p['name'] for p in ours if not p['valid'] or p['pieces'] != 1] or 'none'}; mount {mrep}; stack {stack}", flush=True)
    # design.json: the orientation-equivalent spherical chain for R17 (bvec / w_dir of the axis directions) + the offsets
    u1, u2, u3 = D.u; w_d = math.degrees(math.acos(float(np.clip(-u3[1], -1, 1)))); w_a = math.degrees(math.atan2(u3[0], u3[2]))
    az = math.degrees(math.atan2(u1[2], -u1[0])); elv = math.degrees(math.asin(float(np.clip(u1[1], -1, 1))))
    chk = S.circ_int(S.bvec(az, elv), D.A[0], S.w_dir(w_d, w_a), D.A[1], D.branch)
    kin = dict(az=az, el=elv, a=[math.degrees(D.A[0]), math.degrees(D.A[1])], w=[w_d, w_a], branch=int(D.branch), order=[0, 1, 1],
               axis_points_mm=[np.round(c_, 3).tolist() for c_ in D.c], axes=[np.round(u_, 6).tolist() for u_ in D.u],
               axis_line_offsets_mm=[round(float(np.linalg.norm(c_)), 2) for c_ in D.c], u2_check_deg=round(math.degrees(math.acos(float(np.clip(chk @ u2, -1, 1)))), 5),
               seats=dict(az1=P["az1"], el1=P["el1"], az2=P["az2"], el2=P["el2"], wd=P["wd"], wa=P["wa"], b3=P["b3"]),
               passive_slides_mm=dict(along=P["S_a"], across=P["S_t"], radial_tolerance=P["R_r"]), slide_mid_mm=np.round(D.m, 3).tolist(), neck_mm=P["neck"])
    design = dict(id=a.out, source=f"docs/concepts/offset-skin-normal-3r.md, sweep log k {a.k} ({e.get('stage')}), refitted on Bench({a.bench}) {M.B.mode}",
                  n_joints=3, sliding_cuff=False, dof=3,
                  passive=dict(count=2, translations=2, outside_dof_count=True,
                               kind="self-aligning slides at the cuff in hub 3's plane (along, across the arm), set by loop closure (J1, J2 on GH rays: exact 2-slide closure)",
                               components=[dict(slide="along", travel_mm=[-P["S_a"], P["S_a"]], part="THK RSR3M / HIWIN MGN03C, INVERTED (block on the cuff base, rail rides with carriage A)",
                                                rail_mm=[RW, RH, stack["rails_mm"]["along"]], block_mm=[GW, GL, GH]),
                                           dict(slide="across", travel_mm=[-P["S_t"], P["S_t"]], part="THK RSR3M / HIWIN MGN03C crosswise (rail on carriage A, block = carriage B)",
                                                rail_mm=[RW, RH, stack["rails_mm"]["across"]], block_mm=[GW, GL, GH])],
                               radial="none (0.5 mm closure tolerance; a real GH translation's radial part goes to the cuff liner, R10)"),
                  joints=[dict(joint=f"J{k + 1}", part="O20 x 12.25 v5 hub (docs/HARDWARE.md), MR117 bearing pair", axis_offset_mm=kin["axis_line_offsets_mm"][k]) for k in range(3)],
                  kinematics=kin, base=dict(mount="girdle", chain="osn3_2slides", note="base rides the scapula on the user's scapula handler"),
                  built_with="pipeline/concept_l1/build_osn_l1.py (L1 keep-out meshes: O20 hub keep-outs, fitted 8 x 3 straps, the model's neck, real RSR3M guides)",
                  label=f"offset-skin-normal-3r k {a.k}, L1 keep-out", faces_mm=[round(float(x), 2) for x in M.f], tr=round(M.tr, 2), zb=round(M.zb, 2), stack_mm=stack,
                  bench=dict((k_, rep[k_]) for k_ in ("gap", "reach", "follow", "inband14", "inband10", "contact")),
                  note="R17's dynamics judge models the orientation-equivalent spherical chain (kinematics az/el/a/w); the J3 line offset "
                       f"({kin['axis_line_offsets_mm'][2]} mm) and the 2 passive slides are not in its MuJoCo model")
    json.dump(design, open(os.path.join(dd, "design.json"), "w"), indent=1)
    # skin-check samples: the model's metal + contact-only samples, the verifier's outer faces, every built part's own surface
    pts = [(m, X) for m, X in M.rigid.values()] + [(m, X) for m, X in M.link_pts.values()] + list(M.contact)
    pts += [(mem, X) for nm, mem, X in VER.outer_samples(M, False)]
    for g, mem, n, m, mat in parts:
        pts.append((mem, np.r_[np.asarray(m.vertices), trimesh.sample.sample_surface_even(m, 300, seed=1)[0]]))
    rep_out = dict(fit=dict(k=a.k, bench=a.bench, mode=M.B.mode, report={k_: rep.get(k_) for k_ in ("gap", "reach", "follow", "inband14", "inband10", "contact", "why", "f", "min_clear_taken", "parts_ib14")},
                            S=[P["S_a"], P["S_t"], P["R_r"]], m=np.round(D.m, 3).tolist()), stack=stack, mount=mrep, kin_u2_check_deg=kin["u2_check_deg"])
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    rep_out["check"] = check_frames(M, dd, parts, mv)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    if not a.no_clips:
        C, st = make_clips(M, pts, a.jobs); C["subtitle"] = design["label"]
        C["design"] = dict(n=3, hub_r=HUB_R, **{k_: kin[k_] for k_ in ("az", "el", "a", "w", "branch", "order")})
        json.dump(C, open(os.path.join(dd, "clips.json"), "w"), separators=(",", ":"))
        rep_out["clips"] = st; json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
        print(f"clips.json written ({time.time() - t0:.0f} s)", flush=True)
        W = make_workspace(M); json.dump(W, open(os.path.join(dd, "workspace.json"), "w"), separators=(",", ":"))
        rep_out["workspace"] = dict(poses=len(W["poses"]), closes=round(float(np.mean([p["closes"] for p in W["poses"]])), 4),
                                    feasible_kin_parts=round(float(np.mean([p["eval_feasible"] for p in W["poses"]])), 4))
        print(f"workspace.json: {rep_out['workspace']} ({time.time() - t0:.0f} s)", flush=True)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s -> {dd}")


if __name__ == "__main__":
    main()
