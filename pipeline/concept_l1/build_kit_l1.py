"""L1 keep-out CAD of a concept-kit model configuration (tools/concept_kit.py; docs/concepts/KIT.md) -> a judge-ready design
dir pipeline/full-exo/designs/<out>/ (exo.glb, clips.json, workspace.json, design.json, parts_full.json, build.json).

Models handled (all spherical: every joint axis through the GH centre, so every member frame is a rotation about GH, T = 0):
  rail-elbow (docs/concepts/models/rail-elbow.py, telescopic or rigid rail) and _template (the plain spherical 3R).
The shape is the model's own fit, refitted here with K.evaluate on the bench the configuration was searched on (the
report must reproduce the sweep entry); every part is then built at real size from the fitted samples:
  * hubs (kit 'flat' members, O20 v5 stack): the LOWER member's plate F..F+3, the UPPER member's boss + cap F+3.15..F+12.25,
    10 mm radius, coaxial with the joint axis (which member is lower follows the model's ramps: a strap ramped to the hub at
    STACK is the upper member there);
  * straps (strap1 / bridge / link1 / link2 / neck): the model's sample grid IS the underside (the fitted rho per sample),
    the top is the underside + t along the radial direction (the kit's convention): the CAD's metal = the model's metal;
  * rail-elbow rails: stage 1 (link 1) and stage 2 (its own group l3, driven at half the carriage travel) from their sample
    grids at their fitted cap radius, 5 mm radial (the rail section; the model gives the stage-2 member 9 mm, the carriage's
    height, for K6); the carriage (link 2) as an L section swept along the arc about J2 (a revolve, no loft): the 4 mm
    overhang strip beside stage 2 full height (9 mm, underside at the rail's underside, as the model) plus a top plate
    over stage 2 (rail top + 0.15 .. 9 mm), +-10 mm along the rail; 0.15 mm running clearance between stages and carriage;
  * the user's arm parts (H, F groups: BOTTOM cut at s 255, cuffs, screws) from the newest L1 build that has them.
Member frames (clips.json "G" per group; scene_export.frame_xforms): base = RS (scapula), l1 = frame(J1, J2), l2 =
frame(J2, J3) (= judge/dynamics.py Chain.frame, so its ik_check reads them), l3 (rail stage 2) = l1 x the rotation about
J2 found by Kabsch on the stage's own samples, H = body_pose's humerus segment. A rigidity check proves every member's
samples are constant in its group frame over all taken poses.
Clip frames (30 fps, the champion's clips incl. the held-out ones - judged, never fitted) are followed when the chain
closes (fold margin, J2 rail range), the closure residual < 0.5 deg, no joint value or axis steps > 25 deg from the
previous followed frame, K6 passes (the model's own collision rule) and no model metal sample is inside the exact posed
skin; otherwise the arm is held at the last followed pose until the motion comes back within RESUME deg.

    OMP_NUM_THREADS=1 nice -n 10 python3 pipeline/concept_l1/build_kit_l1.py rail-elbow --k 2221 --out l1_rail-elbow [--jobs 2]
    ... _template --params '{"az": .., ...}' --out l1_3r-k1530
"""
import argparse, importlib.util, json, math, os, sys, time
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools")); sys.path.insert(0, os.path.join(REPO, "pipeline", "full-exo"))
import concept_kit as K                                                         # noqa: E402
import concept_bench as CB                                                      # noqa: E402
BP = CB.BP
FULL = os.path.join(REPO, "pipeline", "full-exo")
CLIPS_FROM = "param2_r20_n3_s1414_4"            # clip / workspace poses (the champion's: 8 clips incl. the 2 held out)
USER_FROM = "l1_seed-offset-3r-slides"          # the user's arm parts (H, F groups) with BOTTOM as its own part
PLATE, GAP_RUN, RESUME, JUMP = 3.0, 0.15, 4.0, 25.0
L_ = json.load(open(os.path.join(REPO, "pipeline", "avg", "body_mesh.json")))
HR = np.array(L_["landmarks"]["rest_humerus"]); _U, _, _Vt = np.linalg.svd(HR); HR = _U @ _Vt
unit = K.unit

# model -> which group each member (or hub level) belongs to. hubs: (joint, lower member group, upper member group)
SPEC = {
    "rail-elbow": dict(hubs={"hub1": ("J1", "base", "l1"), "hub3": ("J3", "H", "l2")},
                       straps={"strap1": "l1", "bridge": "l2", "neck": "H"}, rails=True),
    "_template": dict(hubs={"hub1": ("J1", "base", "l1"), "hub2": ("J2", "l1", "l2"), "hub3": ("J3", "H", "l2")},
                      straps={"link1": "l1", "link2": "l2", "neck": "H"}, rails=False),
}


def load_model(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), os.path.join(REPO, "docs", "concepts", "models", f"{name}.py"))
    M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); return M


# ---------------------------------------------------------------------------------------------------- meshes (L1)
def grid_solid(Bot, Off):
    """watertight slab from a (ns, nc, 3) grid of underside points and per-vertex offsets to the top (ns, nc, 3)"""
    ns, nc, _ = Bot.shape; Top = Bot + Off; V = np.concatenate([Bot.reshape(-1, 3), Top.reshape(-1, 3)]); n = ns * nc
    idx = lambda i, j, top=0: i * nc + j + top * n
    F = []
    for i in range(ns - 1):
        for j in range(nc - 1):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            F += [[a, c, b], [a, d, c]]
            a, b, c, d = idx(i, j, 1), idx(i + 1, j, 1), idx(i + 1, j + 1, 1), idx(i, j + 1, 1)
            F += [[a, b, c], [a, c, d]]
    for i in range(ns - 1):
        for j, s in ((0, 1), (nc - 1, -1)):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j, 1), idx(i, j, 1)
            F += ([[a, b, c], [a, c, d]] if s > 0 else [[a, c, b], [a, d, c]])
    for j in range(nc - 1):
        for i, s in ((0, 1), (ns - 1, -1)):
            a, b, c, d = idx(i, j), idx(i, j + 1), idx(i, j + 1, 1), idx(i, j, 1)
            F += ([[a, b, c], [a, c, d]] if s < 0 else [[a, c, b], [a, d, c]])
    m = trimesh.Trimesh(V, np.array(F), process=True); trimesh.repair.fix_normals(m)
    return m


def revolve_poly(axis, ref, tt, poly, az0, az1, step_mm=1.0, fan=0):
    """solid of a closed section polygon [(polar rad, radius mm)] revolved about `axis` (through GH) from azimuth az0 to
    az1 (rad, in the (ref, tt) frame): a revolve of one constant section (no loft). The end caps are fans from vertex
    `fan` (pass a vertex that sees the whole section, e.g. the reflex corner of an L)."""
    poly = np.asarray(poly, float); m = len(poly)
    rmax = float((poly[:, 1] * np.sin(poly[:, 0])).max()); n = max(4, int(math.ceil(abs(az1 - az0) * rmax / step_mm)) + 1)
    az = np.linspace(az0, az1, n); pol, r = poly[:, 0], poly[:, 1]
    V = (r[None, :, None] * (np.cos(pol)[None, :, None] * axis + np.sin(pol)[None, :, None]
                             * (np.cos(az)[:, None, None] * ref + np.sin(az)[:, None, None] * tt))).reshape(-1, 3)
    F = []
    for i in range(n - 1):
        for j in range(m):
            a, b, c, d = i * m + j, i * m + (j + 1) % m, (i + 1) * m + (j + 1) % m, (i + 1) * m + j
            F += [[a, b, c], [a, c, d]]
    for i, s in ((0, 1), (n - 1, -1)):
        for j in range(1, m - 1):
            a, b, c = i * m + fan, i * m + (fan + j) % m, i * m + (fan + j + 1) % m
            F.append([a, c, b] if s > 0 else [a, b, c])
    msh = trimesh.Trimesh(V, np.array(F), process=True); trimesh.repair.fix_normals(msh)
    return msh


def cyl(axis, h0, h1, r=K.HUB_R):
    return trimesh.creation.cylinder(radius=r, segment=[h0 * axis, h1 * axis], sections=64)


# ---------------------------------------------------------------------------------------------------- frames
def frame(a, c):
    """judge/dynamics.py Chain.frame: columns a, unit(c _|_ a), a x that (works on (..., 3))"""
    a = unit(a); n = unit(c - (a * c).sum(-1, keepdims=True) * a); return np.stack([a, n, np.cross(a, n)], -1)


def kabsch(X, Y):
    """rotation R (3, 3) with R X_i ~ Y_i (points about the origin, (m, 3) each)"""
    U, _, Vt = np.linalg.svd(Y.T @ X); d = np.sign(np.linalg.det(U @ Vt)); return U @ np.diag([1, 1, d]) @ Vt


class PoseSet:
    """kit Frames + body_pose segments for arbitrary poses (n, 5) [plane, elev, axial, flex, pron]"""
    def __init__(self, poses, C):
        r = BP._rig(); RS, RH, TH = [], [], []
        for p in poses:
            (T, S, H, Fa, Pr), _ = BP.segs(r.L, r.s, dict(zip(["plane", "elev", "axial", "flex", "pron"], map(float, p))))
            RS.append(S[0]); RH.append(H[0]); TH.append(H[1])
        self.RS = np.array(RS, float); self.RHseg = np.array(RH, float); self.TH = np.array(TH, float)
        RHG = self.RHseg @ C.T                                                  # band humerus frame (K.frames: RH = RHG C)
        n = len(poses); self.F = K.Frames(RS=self.RS, RHG=RHG, RH=self.RHseg, clip=np.ones(n, bool), ws=np.zeros(n, bool))


def bench_C(B):
    F = K.frames(B); f0 = B.frames(0); C = F.RHG[0].T @ f0["H"][0]
    err = max(float(np.abs(F.RHG[i] @ C - B.frames(i)["H"][0]).max()) for i in range(0, len(B.idx), 23))
    errS = max(float(np.abs(F.RS[i] - B.frames(i)["S"][0]).max()) for i in range(0, len(B.idx), 23))
    return C, err, errS


# ---------------------------------------------------------------------------------------------------- the fitted model
def fit(MOD, model, params, bench):
    B = K.bench(*bench); p = MOD.full(B, params) if hasattr(MOD, "full") else dict(MOD.PARAMS, **params)
    rep = K.evaluate(B, MOD.build, p); L = B._kit_last
    return B, p, rep, L


def chain_at(MOD, B, p, prof, F):
    ch = MOD.build(B, F, p); pts = {m.name: K.member_points(m, prof[m.name]) for m in ch.members}
    return ch, pts


def rail_split(ch):
    """rail-elbow: sample index sets of the rail members -> [(group, member, idx, kind)]"""
    M = {m.name: m for m in ch.members}; out = []
    if "stage2" in M:
        nD = M["stage2"].D.shape[1]; nDc = 2 * 11                               # carriage overhang strips: 11 x 2 samples
        out += [("l1", "rail", np.arange(M["rail"].D.shape[1]), "stage1"), ("l3", "stage2", np.arange(nD - nDc), "stage2"),
                ("l2", "stage2", np.arange(nD - nDc, nD), "car")]
    elif "rail" in M:                                                           # rigid rail: Dr (stations x 5) + carriage 11 x 4
        nD = M["rail"].D.shape[1]; nDc = 11 * 4
        out += [("l1", "rail", np.arange(nD - nDc), "stage1"), ("l2", "rail", np.arange(nD - nDc, nD), "car")]
    return out


def group_frames(spec, ch, pts, PS, l3_ref=None):
    """rotation per group per pose (n, 3, 3); l3 by Kabsch of stage 2's samples (in l1's frame) against l3_ref"""
    J = ch.joints; G = {"base": PS.RS, "l1": frame(J["J1"], J["J2"]), "l2": frame(J["J2"], J["J3"]), "H": PS.RHseg}
    if spec["rails"] and "stage2" in pts:
        sl = [s for s in rail_split(ch) if s[3] == "stage2"][0]; P2 = pts["stage2"][:, sl[2]]
        loc = np.einsum("nji,nmj->nmi", G["l1"], P2)                            # stage 2 in link 1's frame
        ref = loc[0] if l3_ref is None else l3_ref
        Rr = np.array([kabsch(ref, loc[j]) for j in range(len(loc))]); G["l3"] = G["l1"] @ Rr; l3_ref = ref
    return G, l3_ref


def to_local(G, g, j, X, PS):
    """thorax points X (m, 3) of pose j -> group g's local frame (H: body_pose humerus segment incl. its translation)"""
    if g == "H": return (X - PS.TH[j]) @ PS.RHseg[j]
    return X @ G[g][j]


def rigidity(spec, ch, pts, G, PS, sel):
    """max deviation (mm) over the poses `sel` of every member's samples in its group frame (hubs: axis level only)"""
    out = {}; split = rail_split(ch) if spec["rails"] else []
    items = [(spec["straps"][n], n, slice(None)) for n in spec["straps"]] + [(g, n, ix) for g, n, ix, _ in split]
    for g, n, ix in items:
        X = np.stack([to_local(G, g, j, pts[n][j][ix], PS) for j in sel]); out[n + ("" if isinstance(ix, slice) else f"[{g}]")] = round(float(np.abs(X - X[0]).max()), 6)
    for h, (jn, lo, up) in spec["hubs"].items():
        for g in (lo, up):
            k = np.stack([to_local(G, g, j, ch.joints[jn][j][None], PS)[0] for j in sel]); out[f"{h} axis in {g}"] = round(float(np.abs(k - k[0]).max()), 6)
    return out


def build_parts(MOD, spec, p, ch, pts, prof, G, PS, j0):
    """keep-out meshes in their group's local frame: [(group, name, mesh)]"""
    parts = []; Mm = {m.name: m for m in ch.members}; J = ch.joints
    loc = lambda g, mesh: trimesh.Trimesh(to_local(G, g, j0, np.asarray(mesh.vertices), PS), mesh.faces, process=False)
    for h, (jn, lo, up) in spec["hubs"].items():
        k = unit(J[jn][j0]); Fh = float(prof[h][0])
        parts.append((lo, f"{jn} lower plate keep-out (O20 x 3, F {Fh:.1f} mm)", loc(lo, cyl(k, Fh, Fh + PLATE))))
        parts.append((up, f"{jn} upper boss + cap keep-out (O20, F+3.15..F+12.25)", loc(up, cyl(k, Fh + K.STACK, Fh + K.CROWN))))
    for n, g in spec["straps"].items():
        m = Mm[n]; ns, nc = m.grid; X = pts[n][j0].reshape(ns, nc, 3); D = unit(X)
        what = "neck to BOTTOM's bar" if n == "neck" else "strap"
        parts.append((g, f"{n} {what} keep-out ({m.width:g} x {m.t:g} mm Ti at r_ref 70, fitted underside)", loc(g, grid_solid(X, m.t * D))))
    info = {}
    if spec["rails"]:
        RE = MOD; p2 = unit(J["J2"][j0]); p1 = unit(J["J1"][j0]); ref = unit(p1 - (p1 @ p2) * p2); tt = np.cross(p2, ref)
        RL = p.get("r_lay", RE.R_REF); sg = 1.0 if p["d_off"] >= 0 else -1.0; h = -sg
        for g, n, ix, kind in rail_split(ch):
            X = pts[n][j0][ix]; rho = float(np.linalg.norm(X, axis=1).mean())
            if kind in ("stage1", "stage2"):
                nac = 5; ns = len(ix) // nac; Xg = X.reshape(ns, nac, 3)
                # 0.15 mm running clearance on stage 1's edge beside stage 2 (telescopic: the column nearest stage 2)
                if kind == "stage1" and "stage2" in Mm:
                    pol = np.arccos(np.clip(unit(Xg) @ p2, -1, 1)); edge = int(np.argmax(h * pol.mean(0)))
                    Xg = Xg.copy(); v = Xg[:, edge]; Xg[:, edge] = v - h * GAP_RUN * pol_dir(v, p2)
                parts.append((g, f"rail {'stage 1 (link 1)' if kind == 'stage1' else 'stage 2 (driven 2:1, its own group)'} keep-out "
                                 f"(8 x {RE.RAIL_T:g} mm section, r {rho:.1f} mm)", loc(g, grid_solid(Xg, RE.RAIL_T * unit(Xg)))))
                info[kind] = dict(r_mm=round(rho, 2), stations=ns, span_deg=round(float(np.degrees(np.ptp(np.arctan2(unit(Xg[:, 2]) @ tt, unit(Xg[:, 2]) @ ref)))), 1))
            else:                                                               # carriage: L section swept about J2
                u = unit(X); pol = np.arccos(np.clip(u @ p2, -1, 1)); az = np.arctan2(u @ tt, u @ ref)
                psi = float(np.arctan2(np.sin(az).mean(), np.cos(az).mean())); daz = np.angle(np.exp(1j * (az - psi)))
                if "stage2" in Mm:
                    o2 = float(np.median(pol)) - h * 7.0 / RL                    # samples at o2 + h 6, o2 + h 8 mm (at RL)
                    car_t = RE.CAR_T; rt = RE.RAIL_T
                    poly = [(o2 + h * (4.0 + GAP_RUN) / RL, rho), (o2 + h * 8.0 / RL, rho), (o2 + h * 8.0 / RL, rho + car_t),
                            (o2 - h * (4.0 - GAP_RUN) / RL, rho + car_t), (o2 - h * (4.0 - GAP_RUN) / RL, rho + rt + GAP_RUN),
                            (o2 + h * (4.0 + GAP_RUN) / RL, rho + rt + GAP_RUN)]
                    if h < 0: poly = poly[::-1]
                    fan = 0 if h > 0 else 5
                else:                                                            # rigid rail: 16 wide over the 8 rail
                    o = float(np.median(pol)); car_t, rt = RE.CAR_T, RE.RAIL_T
                    poly = [(o - 8.0 / RL, rho), (o - (4.0 + GAP_RUN) / RL, rho), (o - (4.0 + GAP_RUN) / RL, rho + rt + GAP_RUN),
                            (o + (4.0 + GAP_RUN) / RL, rho + rt + GAP_RUN), (o + (4.0 + GAP_RUN) / RL, rho), (o + 8.0 / RL, rho),
                            (o + 8.0 / RL, rho + car_t), (o - 8.0 / RL, rho + car_t)]
                    fan = 2
                msh = revolve_poly(p2, ref, tt, poly, psi + daz.min(), psi + daz.max(), fan=fan)
                if not msh.is_volume and "stage2" in Mm:                         # the other reflex corner
                    msh = revolve_poly(p2, ref, tt, poly, psi + daz.min(), psi + daz.max(), fan=(fan + 4) % 6)
                parts.append((g, f"carriage keep-out (L section: 4 mm overhang x {car_t:g} + plate over the rail, 20 long)", loc(g, msh)))
                info["carriage"] = dict(r_mm=round(rho, 2), psi_deg=round(math.degrees(psi), 2))
    return parts, info


def pol_dir(v, p2):
    """unit vector at points v (m, 3) along increasing polar angle from p2 (on the sphere through v)"""
    u = unit(v); w = unit(u - (u @ p2)[:, None] * p2); pol = np.arccos(np.clip(u @ p2, -1, 1))
    return unit(-np.sin(pol)[:, None] * p2 + np.cos(pol)[:, None] * w)       # d/dpol of cos(pol) p2 + sin(pol) w


def user_parts():
    s = trimesh.load(os.path.join(FULL, "designs", USER_FROM, "exo.glb")); out = []
    for node in s.graph.nodes_geometry:
        g, n = node.split("|")[:2]
        if g not in ("H", "F") or "(proxy)" in n: continue
        T_, gn = s.graph[node]; m = s.geometry[gn].copy(); m.apply_transform(T_); out.append((g, n, m))
    return out


# ---------------------------------------------------------------------------------------------------- per-pose evaluation
def evaluate_poses(MOD, spec, B, p, prof, poses, C, l3_ref, skin=True, jobs=1):
    PS = PoseSet(poses, C); ch, pts = chain_at(MOD, B, p, prof, PS.F); n = len(poses)
    G, l3_ref = group_frames(spec, ch, pts, PS, l3_ref)
    ok = np.asarray(ch.ok, bool)
    J = ch.joints; a1, a2 = p["a1"], p["a2"]
    res = K.closure_residual(J["J1"], J["J3"], J["J2"], a1, a2); kin = ok & (res < 0.5)
    hit = K.collisions(ch, pts, kin)
    q = np.asarray(ch.q, float).reshape(n, -1); axes = np.stack([unit(np.asarray(v, float).reshape(n, 3)) for v in J.values()], 1)
    smin = np.full(n, np.nan)
    if skin:
        todo = [j for j in range(n) if kin[j] and not hit[j]]
        items = [(poses[j], np.concatenate([pts[m.name][j] for m in ch.members])) for j in todo]
        if jobs > 1:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(jobs) as pool: vals = pool.map(skin_min, items, chunksize=4)
        else: vals = list(map(skin_min, items))
        for j, v in zip(todo, vals): smin[j] = v
    return dict(PS=PS, ch=ch, pts=pts, G=G, ok=ok, res=res, kin=kin, hit=hit, q=q, axes=axes, smin=smin, l3_ref=l3_ref)


def skin_min(item):
    pose, W = item
    return float(CB._Exact(BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], map(float, pose)))))(W).min())


def frame_dict(E, j, want, held, why=None):
    f = dict(p=[round(float(x), 4) for x in E["poses"][j]], want=[round(float(x), 4) for x in want], held=bool(held),
             q=[round(float(x), 3) for x in E["q"][j]], G={g: E["G"][g][j].round(6).ravel().tolist() for g in E["G"] if g != "H"})
    if why: f["why"] = why
    return f


def make_clips(MOD, spec, B, p, prof, C, l3_ref, jobs):
    CL = json.load(open(os.path.join(FULL, "designs", CLIPS_FROM, "clips.json"))); out = []; stats = {}
    for cl in CL["clips"]:
        want = np.array([f["want"] for f in cl["frames"]], float)
        E = evaluate_poses(MOD, spec, B, p, prof, want, C, l3_ref, skin=True, jobs=jobs); E["poses"] = want
        frames = []; last = None; nheld = 0; whyc = {}
        for j in range(len(want)):
            why = None
            if not E["ok"][j]: why = "fold"
            elif E["res"][j] >= 0.5: why = "closure"
            elif E["hit"][j]: why = "parts"
            elif not E["smin"][j] >= 0.0: why = "skin"
            ok = why is None
            if ok and last is not None:
                dq = float(np.abs((E["q"][j] - E["q"][last] + 180) % 360 - 180).max())
                dax = float(np.degrees(np.arccos(np.clip((E["axes"][j] * E["axes"][last]).sum(-1), -1, 1))).max())
                if max(dq, dax) > JUMP: ok = False; why = "flip"
                elif frames and frames[-1]["held"]:
                    Rh = BP_h(want[last]); Rw = BP_h(want[j])
                    ang = math.degrees(math.acos(np.clip((np.trace(Rh.T @ Rw) - 1) / 2, -1, 1)))
                    if ang > RESUME: ok = False; why = "held"
            if ok: frames.append(frame_dict(E, j, want[j], False)); last = j
            elif last is None: frames.append(frame_dict(E, j, want[j], True, why)); nheld += 1
            else: frames.append(frame_dict(E, last, want[j], True, why)); nheld += 1
            if why: whyc[why] = whyc.get(why, 0) + 1
        out.append(dict(name=cl["name"], fps=cl.get("fps", 30.0), frames=frames))
        fin = E["smin"][np.isfinite(E["smin"])]
        stats[cl["name"]] = dict(frames=len(frames), held=nheld, follow=round(1 - nheld / len(frames), 3), reasons=whyc,
                                 min_skin_mm=round(float(fin.min()), 2) if len(fin) else None)
        print(f"  clip {cl['name']:24s} {len(frames)} frames, held {nheld} ({whyc})", flush=True)
    return dict(subtitle="", clips=out), stats


def BP_h(pose):
    r = BP._rig(); (T, S, H, Fa, Pr), _ = BP.segs(r.L, r.s, dict(zip(["plane", "elev", "axial", "flex", "pron"], map(float, pose)))); return np.asarray(H[0])


def make_workspace(MOD, spec, B, p, prof, C, l3_ref):
    W = json.load(open(os.path.join(FULL, "designs", CLIPS_FROM, "workspace.json")))
    want = np.array([q["want"] for q in W["poses"]], float)
    E = evaluate_poses(MOD, spec, B, p, prof, want, C, l3_ref, skin=False); E["poses"] = want; poses = []
    for j in range(len(want)):
        f = frame_dict(E, j, want[j], False); f["closes"] = bool(E["kin"][j]); f["eval_feasible"] = bool(E["kin"][j] and not E["hit"][j])
        poses.append(f)
    return dict(envelope=W.get("envelope"), poses=poses, note="eval_feasible = chain closes (fold margin, J2 range, residual) + K6 parts clear (no skin check)")


# ---------------------------------------------------------------------------------------------------- check vs the model
def check_frames(B, L, E, dd, n=3):
    """the model's metal samples (K.evaluate's own points) at n taken bench poses vs the posed exo.glb
    (scene_export.frame_xforms on this build's frame dicts): distance to the nearest surface of the part's group"""
    import scene_export as SE, igl
    take = np.nonzero(L["take"])[0]; elev = np.array([B.poses[i]["elev"] for i in take])
    pick = [int(take[0]), int(take[len(take) // 2]), int(take[int(np.argmax(elev))])][:n]
    src = trimesh.load(os.path.join(dd, "exo.glb")); out = []
    for i in pick:
        fr = frame_dict(E, i, E["poses"][i], False); X, _ = SE.frame_xforms(fr); meshes = {}
        for node in src.graph.nodes_geometry:
            g = node.split("|")[0]
            if g == "F" or (g == "H" and "keep-out" not in node): continue
            T_, gn = src.graph[node]; m = src.geometry[gn].copy(); m.apply_transform(T_); R, t = X[g]
            m.vertices = m.vertices @ np.asarray(R).T + t; meshes.setdefault(g, []).append(m)
        allm = trimesh.util.concatenate([trimesh.util.concatenate(v) for v in meshes.values()])
        res = {}
        for name, P in L["pts"].items():
            Pw = np.ascontiguousarray(P[i], float)
            d = np.sqrt(igl.point_mesh_squared_distance(Pw, np.ascontiguousarray(allm.vertices, float), np.ascontiguousarray(allm.faces, np.int64))[0])
            res[name] = [round(float(d.max()), 3), round(float(np.percentile(d, 95)), 3)]
        worst = max(v[0] for v in res.values())
        out.append(dict(bench_pose=int(i), pose=[round(float(x), 1) for x in E["poses"][i][:3]], max_mm=round(worst, 3), per_member=res))
        print(f"  check bench pose {i} {out[-1]['pose']}: model samples vs posed glb max {worst:.3f} mm  {res}", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("--k", type=int); ap.add_argument("--params")
    ap.add_argument("--out", required=True); ap.add_argument("--bench", default="60,160"); ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--no-clips", action="store_true"); ap.add_argument("--label", default="")
    a = ap.parse_args(); t0 = time.time(); spec = SPEC[a.model]; MOD = load_model(a.model)
    if a.k is not None:
        Lsw = json.load(open(os.path.join(REPO, "docs", "concepts", "sweeps", f"{a.model}.json"))); e = next(x for x in Lsw if x["k"] == a.k)
        params = {k: v for k, v in e["params"].items() if not k.startswith("psi_")}; src = f"docs/concepts/sweeps/{a.model}.json k {a.k} ({e.get('stage')}, gap {e['gap']})"
    else:
        params = json.loads(a.params); src = "params " + json.dumps(params)
    dd = os.path.join(FULL, "designs", a.out); os.makedirs(dd, exist_ok=True)
    B, p, rep, L = fit(MOD, a.model, params, tuple(int(x) for x in a.bench.split(",")))
    keys = ("gap", "reach", "follow", "inband14", "inband10", "contact", "closure", "collide", "flips", "honest", "audit", "inband_member", "mass_g")
    print(f"fit {a.model} on Bench({a.bench}) {B.mode}: " + str({k: rep.get(k) for k in keys}) + f" ({time.time() - t0:.0f} s)", flush=True)
    C, errH, errS = bench_C(B); print(f"frames: RHG C vs body_pose H max {errH:.2e}, RS vs body_pose S max {errS:.2e}", flush=True)
    prof = L["prof"]
    # bench poses through this builder's own pose path (must equal the model's)
    bp = np.array([[B.poses[i][k] for k in ("plane", "elev", "axial", "flex", "pron")] for i in range(len(B.idx))])
    E = evaluate_poses(MOD, spec, B, p, prof, bp, C, None, skin=False); E["poses"] = bp; l3_ref = E["l3_ref"]
    take = np.nonzero(L["take"])[0]; j0 = int(take[0])
    dpts = max(float(np.abs(E["pts"][n][take] - L["pts"][n][take]).max()) for n in L["pts"])
    rig = rigidity(spec, E["ch"], E["pts"], E["G"], E["PS"], take)
    print(f"pose path vs the model's points: max {dpts:.2e} mm; rigidity in group frames (mm): {rig}", flush=True)
    parts, rinfo = build_parts(MOD, spec, p, E["ch"], E["pts"], prof, E["G"], E["PS"], j0)
    up = user_parts()
    sc = trimesh.Scene(); pf = []
    for i, (g, n, m) in enumerate(parts + up):
        sc.add_geometry(m, node_name=f"{g}|{n}|{i}", geom_name=f"{g}|{n}|{i}"); user = i >= len(parts)
        mm = m.copy(); mm.merge_vertices(); vol = abs(mm.volume) if mm.is_watertight else 0.0
        pf.append(dict(k=i, group=g, name=n, vol_cm3=round(vol / 1000, 3), material="user part" if user else "Ti-6Al-4V",
                       mass_g=None if user else round(vol / 1000 * 4.43, 2), valid=bool(user or (mm.is_watertight and mm.is_volume)), faces=len(m.faces)))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=a.out, n=3, level="L1 keep-out", FACES={h: round(float(prof[h][0]), 2) for h in spec["hubs"]}, parts=pf),
              open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    print(f"exo.glb: {len(parts)} keep-out parts ({sum(q['mass_g'] or 0 for q in pf):.1f} g Ti) + {len(up)} user parts; invalid: "
          f"{[q['name'] for q in pf if not q['valid']] or 'none'}; rails {rinfo}", flush=True)
    tele = bool(p.get("tele")) and spec["rails"]
    kin = dict(az=p["az"], el=p["el"], a=[p["a1"], p["a2"]], w=[p["wd"], p["wa"]], branch=int(p["sigma"]), order=[0, 1, 1])
    design = dict(id=a.out, source=f"{src}, refitted on Bench({a.bench}) {B.mode}", n_joints=3, sliding_cuff=False, dof=3,
                  kinematics=kin, base=dict(mount="girdle", chain="spherical", note="base rides the scapula on the user's scapula handler"),
                  built_with="pipeline/concept_l1/build_kit_l1.py (L1 keep-out meshes from the kit model's fitted samples: O20 hub keep-outs, "
                             "fitted straps, rail stages and an L-section carriage revolved about J2)",
                  label=a.label or f"{a.model} {('k ' + str(a.k)) if a.k is not None else ''}, L1 keep-out",
                  model=f"docs/concepts/models/{a.model}.py", params={k: v for k, v in p.items()},
                  bench=dict((k_, rep[k_]) for k_ in ("gap", "reach", "follow", "inband14", "inband10", "contact")))
    if spec["rails"]:
        design["joints"] = dict(J1="O20 hub (base / link 1)", J2="curved rail about the J2 axis: carriage (link 2) on " +
                                ("a 2-stage telescopic rail (stage 2 = group l3, driven at half the carriage travel)" if tele else "a rigid rail on link 1"),
                                J3="O20 hub (link 2 / arm end)")
        if tele:
            design["mvp1_legal"] = False
            design["note"] = ("NOT MVP1-legal: stage 2 of the telescopic rail must be synchronised 2:1 with the carriage (cable loop with pulleys "
                              "or a rack and pinion = gearing, both ruled out for MVP1; a floating stage would be an undriven coordinate, R17). "
                              "R17's dynamics judge models the orientation-equivalent spherical 3R (kinematics); stage 2 (group l3) is not in its MuJoCo model.")
    json.dump(design, open(os.path.join(dd, "design.json"), "w"), indent=1)
    out = dict(fit=dict(model=a.model, k=a.k, bench=a.bench, mode=B.mode, report={k: rep.get(k) for k in keys}),
               frames_err=dict(RHG_vs_bodypose_H=errH, RS_vs_bodypose_S=errS), pose_path_err_mm=dpts, rigidity_mm=rig, rails=rinfo)
    json.dump(out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    out["check"] = check_frames(B, L, E, dd)
    json.dump(out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    if not a.no_clips:
        Cl, st = make_clips(MOD, spec, B, p, prof, C, l3_ref, a.jobs); Cl["subtitle"] = design["label"]
        Cl["design"] = dict(n=3, hub_r=K.HUB_R, **kin)
        json.dump(Cl, open(os.path.join(dd, "clips.json"), "w"), separators=(",", ":")); out["clips"] = st
        print(f"clips.json written ({time.time() - t0:.0f} s)", flush=True)
        W = make_workspace(MOD, spec, B, p, prof, C, l3_ref); json.dump(W, open(os.path.join(dd, "workspace.json"), "w"), separators=(",", ":"))
        out["workspace"] = dict(poses=len(W["poses"]), closes=round(float(np.mean([q["closes"] for q in W["poses"]])), 4),
                                feasible_kin_parts=round(float(np.mean([q["eval_feasible"] for q in W["poses"]])), 4))
        print(f"workspace.json: {out['workspace']} ({time.time() - t0:.0f} s)", flush=True)
        json.dump(out, open(os.path.join(dd, "build.json"), "w"), indent=1, default=float)
    print(f"done in {time.time() - t0:.0f} s -> {dd}")


if __name__ == "__main__":
    main()
