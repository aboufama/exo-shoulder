"""L1 keep-out CAD of a seed-offset-3r-slides configuration (docs/concepts/seed-offset-3r-slides.md) -> a judge-ready
design dir pipeline/full-exo/designs/<out>/ (exo.glb, clips.json, workspace.json, design.json, parts_full.json).

The shape is the concept model's own fit (VModel: the verifier's checks + the riser), refitted here on the same bench the
configuration was searched on; every part is then built at real size from that fit:
  * hubs: O20 keep-outs (docs/HARDWARE.md v5): lower member's plate F..F+3, upper member's boss + cap F+3.15..F+12.25;
  * links 1, 2: 8 mm wide x 3 mm straps whose underside passes through the model's fitted samples (rows at -3, -1, 1, 3 mm
    across, edges at +-4 mm), thickness 3 mm along the radial direction (the model's strap mid-surface convention);
  * member 3: J3 plate + the ramped neck (<= 60 deg from the plate to carriage B's top) + the bridge to carriage B
    (underside at carriage B's underside, top flush with the neck's top so member 3 is one connected body) + carriage B;
  * carriage A (its own group, it slides along the rail) and the arm-fixed cuff rail;
  * NEW (missing in the model): the rail mount, a 4 mm slab from the rail's far end to the end of the user's BOTTOM bar
    (the rail has to be fixed to the arm somewhere);
  * the user's arm parts (H, F groups) from the champion's parametric build, minus that build's own arm end.
Member frames (clips.json "G" rotation + "T" translation per group, scene_export.frame_xforms) reproduce the model's
kinematics exactly: world = RS (R_m x + t_m) for member m, x in the model's member-local rest coordinates; the arm-fixed
parts sit in the humerus group H (x_H = HR x_canonical, since body_pose's humerus frame is RS HG HR^T).
Clip frames (30 fps, the champion's clips incl. the held-out ones - judged, never fitted) are followed when the chain
closes on the design branch >= 10 deg from the J2 fold, the slides are in range, the closure residual is < 0.5 deg, no
joint steps > 25 deg from the previous followed frame, non-adjacent parts keep >= 1 mm (the model's collide) and no
model metal sample is inside the exact posed skin; otherwise the arm is held at the last followed pose until the motion
comes back within RESUME deg (band_to_design.py's rule).

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/build_seed_offset_l1.py [k] [--out ID] [--bench 60,160] [--jobs 2]
"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo"))
import concept_bench as CB                                                      # noqa: E402
BP = CB.BP
spec = importlib.util.spec_from_file_location("so3r", os.path.join(REPO, "docs", "concepts", "models", "seed-offset-3r-slides.py"))
MM = importlib.util.module_from_spec(spec); spec.loader.exec_module(MM)
FULL = os.path.join(REPO, "pipeline", "full-exo"); TEMPLATE = "param2_r20_n3_s1414_4"   # clips / workspace poses + the user's arm parts
HUB_R, CROWN, UP, T_LINK, W_LINK = MM.HUB_R, MM.CROWN, MM.UP, MM.T_LINK, MM.W_LINK
PLATE = 3.0; RESUME = 4.0; MOUNT_T = 4.0
L_ = json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json")))
HR = np.array(L_["landmarks"]["rest_humerus"]); _U, _, _Vt = np.linalg.svd(HR); HR = _U @ _Vt
unit = MM.unit


# ---------------------------------------------------------------------------------------------------- meshes (L1)
def cyl(p0, axis, h0, h1, r=HUB_R):
    return trimesh.creation.cylinder(radius=r, segment=[p0 + h0 * axis, p0 + h1 * axis], sections=64)


def box(cen, frame, ext):
    T = np.eye(4); T[:3, :3] = frame; T[:3, 3] = cen; return trimesh.creation.box(extents=ext, transform=T)


def grid_solid(Bot, Off):
    """watertight slab from a (ns, nc, 3) grid of underside points and per-vertex offsets to the top (ns, nc, 3)"""
    ns, nc, _ = Bot.shape; Top = Bot + Off; V = np.concatenate([Bot.reshape(-1, 3), Top.reshape(-1, 3)]); n = ns * nc
    idx = lambda i, j, top=0: i * nc + j + top * n
    F = []
    for i in range(ns - 1):
        for j in range(nc - 1):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            F += [[a, c, b], [a, d, c]]                                         # bottom
            a, b, c, d = idx(i, j, 1), idx(i + 1, j, 1), idx(i + 1, j + 1, 1), idx(i, j + 1, 1)
            F += [[a, b, c], [a, c, d]]                                         # top
    for i in range(ns - 1):                                                     # long sides (j = 0, nc - 1)
        for j, s in ((0, 1), (nc - 1, -1)):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j, 1), idx(i, j, 1)
            F += ([[a, b, c], [a, c, d]] if s > 0 else [[a, c, b], [a, d, c]])
    for j in range(nc - 1):                                                     # ends (i = 0, ns - 1)
        for i, s in ((0, 1), (ns - 1, -1)):
            a, b, c, d = idx(i, j), idx(i, j + 1), idx(i, j + 1, 1), idx(i, j, 1)
            F += ([[a, b, c], [a, c, d]] if s < 0 else [[a, c, b], [a, d, c]])
    m = trimesh.Trimesh(V, np.array(F), process=True); trimesh.repair.fix_normals(m)
    return m


# ---------------------------------------------------------------------------------------------------- the fitted model
def fit(k, bench):
    L = json.load(open(os.path.join(REPO, "docs", "concepts", "sweeps", "seed-offset-3r-slides.json")))
    e = next(x for x in L if x["k"] == k); P = dict(e.get("asked") or e["params"])
    B = CB.Bench(*bench); M = MM.VModel(B, P); r = M.run(); M._bench = (M.Q, M.s, M.RS, M.X)
    return M, r, e


def link_profiles(M):
    """the model's finalize() link computation, keeping the full rows (also inside the hub footprints)"""
    D = M.D; u, c = D.u, D.c; k = math.tan(MM.RAMP * MM.D2R); keep = ~M.drop
    _, _, _, rL = M._heights(keep); F = M.f
    lvl = {("L1", 0): 0.0, ("L1", 1): 0.0, ("L2", 1): UP, ("L2", 2): 0.0 if D.p.get("flip3") else UP}
    out = {}
    # rebuild the link rows exactly as add_links did (first-pass hub centres)
    for lk in M.geo.links:
        rows = []
        for (dv, keep_s, sarc), r in zip(lk["rows"], rL[lk["name"]]):
            r = r.copy(); S = sarc
            for kk, end in ((lk["ka"], 0), (lk["kb"], -1)):
                idx = np.nonzero(keep_s)[0]
                if not len(idx): continue
                j = idx[0] if end == 0 else idx[-1]
                cen = c[kk] + F[kk] * u[kk]; den = float(dv[j] @ u[kk])
                rc = (cen @ u[kk] + lvl[(lk["name"], kk)]) / max(den, 0.2)
                r = np.maximum(r, rc - k * np.abs(S - S[j]))
            r = np.max(r[None, :] - k * np.abs(S[:, None] - S[None, :]), axis=1)
            rows.append((dv, keep_s, r))
        out[lk["name"]] = (lk, rows)
    return out


def link_solid(M, lk, rows):
    """strap 8 x 3 mm through the model's fitted underside samples (rows -3 -1 1 3), one station past each hub rim"""
    D = M.D; u, c = D.u, D.c
    keep_any = np.any([kp for _, kp, _ in rows], axis=0); idx = np.nonzero(keep_any)[0]
    j0, j1 = max(0, idx[0] - 1), min(len(keep_any) - 1, idx[-1] + 1)
    dvs = [dv for dv, _, _ in rows]; rs = [r for _, _, r in rows]
    # edge columns (+-4 mm): the outer rows' heights, directions extrapolated across the strap
    d_lo = unit(dvs[0] + (dvs[0] - dvs[1]) * 0.5); d_hi = unit(dvs[-1] + (dvs[-1] - dvs[-2]) * 0.5)
    cols_d = [d_lo] + dvs + [d_hi]; cols_r = [rs[0]] + rs + [rs[-1]]
    J = np.arange(j0, j1 + 1)
    Bot = np.stack([cols_d[q][J] * cols_r[q][J][:, None] for q in range(len(cols_d))], 1)
    Off = T_LINK * np.stack([cols_d[q][J] for q in range(len(cols_d))], 1)
    return grid_solid(Bot, Off)


def build_parts(M):
    D = M.D; P = D.p; u, c = D.u, D.c; F = M.f; tr, zb = M.tr, M.zb; sa, st, sn = D.sa, D.st, D.sn
    Rst = np.stack([sa, st, sn], 1); cs = D.stage_c(); neck = P["neck"]; Sa, St = P["S_a"], P["S_t"]
    ztop = zb + MM.CAR_H; parts = []                                            # (group, name, mesh in the group's local frame)
    H = lambda k: c[k] + F[k] * u[k]
    parts.append(("base", "J1 upper boss + cap keep-out (O20, F+3.15..F+12.25; base = J1's upper member)", cyl(H(0), u[0], UP, CROWN)))
    parts.append(("l1", "J1 lower plate keep-out (O20 x 3, link 1)", cyl(H(0), u[0], 0.0, PLATE)))
    parts.append(("l1", "J2 lower plate keep-out (O20 x 3, link 1)", cyl(H(1), u[1], 0.0, PLATE)))
    parts.append(("l2", "J2 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2)", cyl(H(1), u[1], UP, CROWN)))
    parts.append(("l2", "J3 upper boss + cap keep-out (O20, F+3.15..F+12.25, link 2)", cyl(H(2), u[2], UP, CROWN)))
    parts.append(("l3", "J3 lower plate keep-out (O20 x 3, member 3)", cyl(H(2), u[2], 0.0, PLATE)))
    prof = link_profiles(M)
    for nm, grp in (("L1", "l1"), ("L2", "l2")):
        lk, rows = prof[nm]; parts.append((grp, f"link {nm[1]} strap keep-out (8 x 3 mm Ti, fitted underside)", link_solid(M, lk, rows)))
    # member 3: neck (<= 60 deg ramp from the J3 plate level to carriage B's top), bridge, carriage B
    xs = np.unique(np.r_[np.linspace(HUB_R - 2.0, HUB_R + neck, 40), HUB_R + neck - (ztop - F[2]) / math.tan(MM.RAMP * MM.D2R)])
    xs = xs[(xs >= HUB_R - 2.0) & (xs <= HUB_R + neck)]
    hh = np.maximum(F[2], ztop - math.tan(MM.RAMP * MM.D2R) * (HUB_R + neck - xs))
    ys = np.array([-W_LINK / 2, 0.0, W_LINK / 2])
    Bot = c[2][None, None] + xs[:, None, None] * sa + ys[None, :, None] * st + hh[:, None, None] * sn
    parts.append(("l3", "member-3 neck keep-out (8 x 3 mm, ramp <= 60 deg from the J3 plate to carriage B's top)", grid_solid(Bot, np.broadcast_to(T_LINK * sn, Bot.shape).copy())))
    x0, x1 = HUB_R + neck - 1.0, HUB_R + neck + Sa + 1.0
    parts.append(("l3", "member-3 bridge keep-out (8 wide, underside at carriage B's underside, top flush with the neck)",
                  box(c[2] + 0.5 * (x0 + x1) * sa + 0.5 * (zb + ztop + T_LINK) * sn, Rst, [x1 - x0, W_LINK, ztop + T_LINK - zb])))
    parts.append(("l3", "carriage B keep-out (20 x 20 x 4, across + radial slides)", box(cs + (zb + MM.CAR_H / 2) * sn, Rst, [MM.CAR_L, MM.CAR_W, MM.CAR_H])))
    parts.append(("l4", "carriage A keep-out (20 x (20 + 2 S_t) x 4, along slide)", box(cs + (tr + MM.RAIL_H + MM.RUN + MM.CAR_H / 2) * sn, Rst,
                                                                                         [MM.CAR_L, MM.CAR_W + 2 * St, MM.CAR_H])))
    rail = box(cs + (tr + MM.RAIL_H / 2) * sn, Rst, [MM.CAR_L + 2 * Sa, MM.RAIL_W, MM.RAIL_H])
    return parts, rail


def rail_mount(M, bottom_c):
    """slab from the rail's far end to the end of the user's BOTTOM bar (canonical arm frame), at the rail's level"""
    D = M.D; P = D.p; sa, st, sn = D.sa, D.st, D.sn; cs = D.stage_c(); tr = M.tr; Rst = np.stack([sa, st, sn], 1)
    end = MM.CAR_L / 2 + P["S_a"]                                                # rail end (along, from the stage centre)
    rel = bottom_c - cs; a_, t_ = rel @ sa, rel @ st
    near = (a_ > end - 2) & (a_ < end + 25)
    if not near.any(): return None, None
    a1 = min(float(np.percentile(a_[near], 60)), end + 16.0); tb = float(np.median(t_[near]))
    t0, t1 = min(-MM.RAIL_W / 2, tb), max(MM.RAIL_W / 2, tb)
    a0 = end - 1.0
    m = box(cs + 0.5 * (a0 + a1) * sa + 0.5 * (t0 + t1) * st + (tr + MOUNT_T / 2) * sn, Rst, [a1 - a0, t1 - t0, MOUNT_T])
    return m, dict(along=[round(a0, 1), round(a1, 1)], across=[round(t0, 1), round(t1, 1)], height=[round(tr, 1), round(tr + MOUNT_T, 1)])


def user_parts():
    """the user's arm parts (H, F groups, rest frame) from the template build, minus that build's own arm end"""
    s = trimesh.load(os.path.join(FULL, "designs", TEMPLATE, "exo.glb")); out = []
    for node in s.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if g not in ("H", "F") or n.startswith(("D6-04", "J3 ring nut", "J3 inner spacer")): continue
        T_, gn = s.graph[node]; m = s.geometry[gn].copy(); m.apply_transform(T_); out.append((g, n, m))
    return out


# ---------------------------------------------------------------------------------------------------- kinematics per pose
def chain(M, poses):
    """poses (n, 5) -> per pose: q (deg), ok flags, (G, T) per group, slides, closure residual"""
    D = M.D; RS = np.array([MM.scap(float(p[1])) for p in poses]); RH = np.array([MM.humerus(p) for p in poses])
    Q = np.einsum("nji,njk->nik", RS, RH); q, ok, X1, X2, X3, s = D.ik(Q)
    R123 = X3[0]; res = np.degrees(np.arccos(np.clip((np.einsum("nij,nij->n", R123, Q) - 1) / 2, -1, 1)))
    sok = D.slides_ok(s)
    G = {"base": RS, "l1": RS @ X1[0], "l2": RS @ X2[0], "l3": RS @ X3[0], "l4": RS @ Q}
    T = {"base": np.zeros((len(Q), 3)), "l1": np.einsum("nij,nj->ni", RS, X1[1]), "l2": np.einsum("nij,nj->ni", RS, X2[1]),
         "l3": np.einsum("nij,nj->ni", RS, X3[1]), "l4": np.einsum("nij,nj->ni", RS @ Q, s[:, :1] * D.sa[None])}
    return dict(q=np.degrees(q), ok=ok, sok=sok, res=res, G=G, T=T, s=s, Q=Q, RS=RS, X={1: X1, 2: X2, 3: X3})


def model_points(M, extra):
    """model metal + contact-only samples in member-local coordinates [(member, pts)]"""
    pts = [(m, X) for m, X in M.rigid.values()] + [(m, X) for m, X in M.link_pts.values()] + list(M.contact)
    return pts + extra


def swap_in(M, K):
    M.Q, M.s, M.RS = K["Q"], K["s"], K["RS"]; M.X = K["X"]


def skin_min(item):
    """exact signed distance (min, mm) of the model's metal to the posed skin, one pose"""
    pose, W = item
    ex = CB._Exact(BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], pose))))
    return float(ex(W).min())


def world_pts(M, j, pts):
    return np.concatenate([M.scap_pts(m, j, X) @ M.RS[j].T for m, X in pts])


def feasibility(M, K, poses, pts, jobs=1, skin=True):
    """per pose: kinematic ok, parts clearance, skin min (exact) - arrays"""
    swap_in(M, K); n = len(poses)
    kin = K["ok"] & K["sok"] & (K["res"] < 0.5)
    clear = np.full(n, np.nan); smin = np.full(n, np.nan)
    for j in range(n):
        if kin[j]: clear[j] = M.collide(j)
    if skin:
        todo = [j for j in range(n) if kin[j] and clear[j] >= MM.PART_CLEAR]
        items = [(poses[j], world_pts(M, j, pts)) for j in todo]
        if jobs > 1:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(jobs) as pool: vals = pool.map(skin_min, items, chunksize=4)
        else: vals = list(map(skin_min, items))
        for j, v in zip(todo, vals): smin[j] = v
    return kin, clear, smin


def frame_dict(K, j, p, want, held, why=None):
    f = dict(p=[round(float(x), 4) for x in p], want=[round(float(x), 4) for x in want], held=bool(held),
             q=[round(float(x), 3) for x in K["q"][j]], s=[round(float(x), 3) for x in K["s"][j]],
             G={g: K["G"][g][j].round(6).ravel().tolist() for g in K["G"]}, T={g: K["T"][g][j].round(4).tolist() for g in K["T"]})
    if why: f["why"] = why
    return f


def make_clips(M, pts, jobs):
    C = json.load(open(os.path.join(FULL, "designs", TEMPLATE, "clips.json"))); out = []; stats = {}
    for cl in C["clips"]:
        want = np.array([f["want"] for f in cl["frames"]], float)
        K = chain(M, want); kin, clear, smin = feasibility(M, K, want, pts, jobs)
        good = kin & (clear >= MM.PART_CLEAR) & (smin >= 0.0)
        frames = []; last = None; nheld = 0; whyc = {}
        for j in range(len(want)):
            why = None
            if not K["ok"][j]: why = "fold"
            elif not K["sok"][j]: why = "slide"
            elif K["res"][j] >= 0.5: why = "closure"
            elif clear[j] < MM.PART_CLEAR: why = "parts"
            elif not smin[j] >= 0.0: why = "skin"
            ok = why is None
            if ok and last is not None:
                dq = np.abs((K["q"][j] - K["q"][last] + 180) % 360 - 180).max()
                if dq > MM.JUMP: ok = False; why = "flip"
                if frames and frames[-1]["held"]:                                     # resume only near the held pose
                    Rh = MM.humerus(want[last]); Rw = MM.humerus(want[j])
                    ang = math.degrees(math.acos(np.clip((np.trace(Rh.T @ Rw) - 1) / 2, -1, 1)))
                    if ang > RESUME: ok = False; why = why or "held"
            if ok: frames.append(frame_dict(K, j, want[j], want[j], False)); last = j
            elif last is None: frames.append(frame_dict(K, j, want[j], want[j], True, why)); nheld += 1   # nothing followed yet
            else:
                fr = frame_dict(K, last, want[last], want[j], True, why); frames.append(fr); nheld += 1
            if why: whyc[why] = whyc.get(why, 0) + 1
        out.append(dict(name=cl["name"], fps=cl.get("fps", 30.0), frames=frames))
        stats[cl["name"]] = dict(frames=len(frames), held=nheld, follow=round(1 - nheld / len(frames), 3), reasons=whyc,
                                 min_skin_mm=round(float(np.nanmin(smin)), 2) if np.isfinite(smin).any() else None)
        print(f"  clip {cl['name']:24s} {len(frames)} frames, held {nheld} ({whyc})", flush=True)
    return dict(subtitle="", clips=out), stats


def make_workspace(M, pts):
    W = json.load(open(os.path.join(FULL, "designs", TEMPLATE, "workspace.json")))
    want = np.array([p["want"] for p in W["poses"]], float); K = chain(M, want)
    kin, clear, _ = feasibility(M, K, want, pts, skin=False)
    poses = []
    for j in range(len(want)):
        f = frame_dict(K, j, want[j], want[j], False); f["closes"] = bool(kin[j])
        f["eval_feasible"] = bool(kin[j] and clear[j] >= MM.PART_CLEAR)       # kinematics + parts (the model's skin check not run here)
        poses.append(f)
    return dict(envelope=W.get("envelope"), poses=poses, note="eval_feasible = chain closes + slides in range + part clearance >= 1 mm (no skin check)")


# ---------------------------------------------------------------------------------------------------- check vs the model
def check_frames(M, dd, n=3):
    """the model's metal samples at n bench poses vs the posed exo.glb (scene_export frame_xforms): distance to the nearest
    surface of the part's own group"""
    import scene_export as SE
    taken = [i for i in range(len(M.B.idx)) if M.B.res[i] is not None and float(np.min(M.B.res[i])) >= 0]
    pick = [taken[0], taken[len(taken) // 2], max(taken, key=lambda i: M.B.poses[i]["elev"])][:n]
    src = trimesh.load(os.path.join(dd, "exo.glb")); out = []; M.Q, M.s, M.RS, M.X = M._bench
    K = chain(M, np.array([[M.B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(M.B.idx))]))
    grp_of = {0: "base", 1: "l1", 2: "l2", 3: "l3", 4: "l4", 5: "H"}
    for i in pick:
        pz = [M.B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")]; fr = frame_dict(K, i, pz, pz, False)
        X, _ = SE.frame_xforms(fr); meshes = {}
        for node in src.graph.nodes_geometry:
            g = node.split("|")[0]
            if g == "F" or (g == "H" and "(proxy)" not in node): continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            m.vertices = m.vertices @ np.asarray(R).T + t; meshes.setdefault(g, []).append(m)
        meshes = {g: trimesh.util.concatenate(v) for g, v in meshes.items()}
        res = {}
        for name, (m, Xp) in list(M.rigid.items()) + list(M.link_pts.items()):
            Pw = M.world(m, i, Xp); g = "l1" if name == "hub1" else grp_of[m]          # J1's plate is link 1's (a disc about its own axis)
            import igl
            d = np.sqrt(igl.point_mesh_squared_distance(np.ascontiguousarray(Pw, float), np.ascontiguousarray(meshes[g].vertices, float),
                                                        np.ascontiguousarray(meshes[g].faces, np.int64))[0])
            res[name] = [round(float(d.max()), 3), round(float(np.percentile(d, 95)), 3)]
        worst = max(v[0] for v in res.values())
        # the model's own transform vs the clips' G/T: same world points (exact kinematics)
        out.append(dict(bench_pose=int(i), pose=fr["p"][:3], max_mm=round(worst, 3), per_part=res,
                        res_deg=round(float(K["res"][i]), 4)))
        print(f"  check pose {i} {np.round(fr['p'][:3], 1)}: model samples vs posed glb max {worst:.3f} mm  {res}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("k", type=int, nargs="?", default=403); ap.add_argument("--out", default="l1_seed-offset-3r-slides")
    ap.add_argument("--bench", default="60,160"); ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--no-clips", action="store_true")
    a = ap.parse_args(); t0 = time.time()
    dd = os.path.join(FULL, "designs", a.out); os.makedirs(dd, exist_ok=True)
    M, rep, e = fit(a.k, tuple(int(x) for x in a.bench.split(",")))
    print(f"fit k {a.k} on Bench({a.bench}) {M.B.mode}: gap {rep['gap']} reach {rep['reach']} follow {rep['follow']} ib14 {rep['inband14']} "
          f"ib10 {rep['inband10']} contact {rep['contact']} f {rep['f']} S {[M.p['S_a'], M.p['S_t'], M.p['R_r']]} ({time.time() - t0:.0f} s)", flush=True)
    parts, rail = build_parts(M)
    up = user_parts()
    bot = next(m for g, n, m in up if n.startswith("BOTTOM"))
    bottom_c = np.asarray(bot.vertices) @ HR                                    # rest (H) -> canonical arm frame: x_c = HR^T x_H
    mount, mrep = rail_mount(M, bottom_c)
    toH = lambda m: trimesh.Trimesh(np.asarray(m.vertices) @ HR.T, m.faces, process=False)
    parts.append(("H", "cuff rail keep-out (proxy) (8 x 4 x (20 + 2 S_a), arm-fixed)", toH(rail)))
    extra = []
    if mount is not None:
        parts.append(("H", "rail mount to BOTTOM (proxy) (4 mm slab, not in the concept model)", toH(mount)))
        extra.append((5, np.r_[np.asarray(mount.vertices), trimesh.sample.sample_surface_even(mount, 400, seed=1)[0]]))   # skin check
    # ---- export
    sc = trimesh.Scene(); pf = []
    allp = parts + up
    for i, (g, n, m) in enumerate(allp):
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}")
        user = i >= len(parts)
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else 0.0
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material="user part" if user else "Ti-6Al-4V",
                       mass_g=None if user else round(vol / 1000 * 4.43, 2), valid=bool(user or (mm.is_watertight and mm.is_volume)), faces=len(m.faces)))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=3, level="L1 keep-out", FACES={str(j + 1): round(float(M.f[j]), 2) for j in range(3)}, parts=pf),
              open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    print(f"exo.glb: {len(parts)} keep-out parts ({sum(p['mass_g'] or 0 for p in pf):.1f} g Ti) + {len(up)} user parts; invalid: "
          f"{[p['name'] for p in pf if not p['valid']] or 'none'}; rail mount {mrep}", flush=True)
    D = M.D; s = MM.SEED; P = M.p
    kin = dict(az=s["az"] + P.get("d_az", 0.0), el=s["el"] + P.get("d_el", 0.0), a=[s["a"][0] + P.get("d_a1", 0.0), s["a"][1] + P.get("d_a2", 0.0)],
               w=[s["w"][0] + P.get("d_wd", 0.0), s["w"][1] + P.get("d_wa", 0.0)], branch=D.branch, order=[0, 1, 1],
               offsets_mm={k_: P[k_] for k_ in ("o1a", "o1c", "o2a", "o2c", "o3a", "o3c")}, axis_points_mm=[np.round(c_, 3).tolist() for c_ in D.c],
               axes=[np.round(u_, 6).tolist() for u_ in D.u], passive_slides_mm=dict(along=P["S_a"], across=P["S_t"], radial=P["R_r"]), neck_mm=P["neck"])
    design = dict(id=a.out, source=f"docs/concepts/seed-offset-3r-slides.md, sweep log k {a.k} ({e.get('label')}), refitted on Bench({a.bench}) {M.B.mode}",
                  n_joints=3, sliding_cuff=False, dof=3, passive=dict(count=3, kind="self-aligning slides at the cuff (along, across, radial), set by loop closure",
                                                                     outside_dof_count=True),
                  kinematics=kin, base=dict(mount="girdle", chain="offset3_slides", note="base rides the scapula on the user's scapula handler"),
                  built_with="pipeline/concept_l1/build_seed_offset_l1.py (L1 keep-out meshes: O20 hub keep-outs, fitted 8 x 3 straps, slide-stage boxes)",
                  label=f"seed-offset-3r-slides k {a.k}, L1 keep-out", faces_mm=[round(float(x), 2) for x in M.f], tr=round(M.tr, 2), zb=round(M.zb, 2),
                  bench=dict((k_, rep[k_]) for k_ in ("gap", "reach", "follow", "inband14", "inband10", "contact")),
                  note="R17's dynamics judge models the orientation-equivalent spherical chain (kinematics az/el/a/w); the offsets and the 3 passive "
                       "slides are not in its MuJoCo model")
    json.dump(design, open(os.path.join(dd, "design.json"), "w"), indent=1)
    pts = model_points(M, extra)
    rep_out = dict(fit=dict(k=a.k, bench=a.bench, mode=M.B.mode, report={k_: rep[k_] for k_ in ("gap", "reach", "follow", "inband14", "inband10", "contact", "why", "f", "min_clear_taken", "parts_ib14")},
                            S=[P["S_a"], P["S_t"], P["R_r"]]), rail_mount=mrep)
    if not a.no_clips:
        C, st = make_clips(M, pts, a.jobs); C["subtitle"] = design["label"]
        C["design"] = dict(n=3, hub_r=HUB_R, **{k_: kin[k_] for k_ in ("az", "el", "a", "w", "branch", "order")})
        json.dump(C, open(os.path.join(dd, "clips.json"), "w"), separators=(",", ":"))
        rep_out["clips"] = st; print(f"clips.json written ({time.time() - t0:.0f} s)", flush=True)
        W = make_workspace(M, pts); json.dump(W, open(os.path.join(dd, "workspace.json"), "w"), separators=(",", ":"))
        rep_out["workspace"] = dict(poses=len(W["poses"]), closes=round(float(np.mean([p["closes"] for p in W["poses"]])), 4),
                                    feasible_kin_parts=round(float(np.mean([p["eval_feasible"] for p in W["poses"]])), 4))
        print(f"workspace.json: {rep_out['workspace']} ({time.time() - t0:.0f} s)", flush=True)
    rep_out["check"] = check_frames(M, dd)
    json.dump(rep_out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s -> {dd}")


if __name__ == "__main__":
    main()
