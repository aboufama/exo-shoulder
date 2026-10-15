"""Band-searched design -> viewer design dir (proxy meshes + smooth 30 fps clips), ready for score_design.py.

Input: a band_eval detail result (conformal/gpu_client/band_eval_<tag>.json, DETAIL=1): design, link undersides h per
sample, per-frame feasibility + in-band share of every spare-joint configuration (10 fps clip frames).
  - clip paths: dynamic programming per clip over the configuration grid, moves of <= 180 deg/s in every
    spare joint (<= 180 deg/s, no flicks), maximising frames followed then in-band share; where nothing works the arm is held
    until the motion comes back within RESUME deg (same rule as make_clips_full.py); upsampled to 30 fps.
  - proxies: flat hub discs (5 mm) at each member's face, ribbons lofted through the fitted underside samples (5.5 mm
    thick), the user's arm parts (BOTTOM, cuffs) from designs/final, plus a hub block where JN's axis was moved.

    python3 band_to_design.py <band_eval json> <result index> <design name> ["subtitle"]
"""
import base64, gzip, io, json, math, os, sys
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); EXO = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(EXO, "avg"))
os.environ.setdefault("CLEAR", "4"); os.environ.setdefault("POST_HALF", "180"); os.environ.setdefault("H_LEN", "325")
_c = os.getcwd(); os.chdir(os.path.join(EXO, "avg")); import design_search as DS; os.chdir(_c)
D2R = math.pi / 180; HUB_R, T_LO, T_LINK, T_BOT = 17.0, 5.0, 5.5, 6.5; RESUME = 4.0
SRC, IDX, NAME = sys.argv[1], int(sys.argv[2]), sys.argv[3]; SUB = sys.argv[4] if len(sys.argv) > 4 else NAME
R = json.load(open(SRC))["results"][IDX]; N = R["n"]; A = [x * D2R for x in R["a"]]; m = N - 3
Z = np.load(io.BytesIO(gzip.decompress(base64.b64decode(open(os.path.join(EXO, "conformal", "band_poses.b64")).read()))))
POSE, CID, FI, NAMES, FPS = Z["POSE"], Z["CID"], Z["FI"], [str(x) for x in Z["NAMES"]], float(Z["FPS"])
ST = int(R.get("stride", 1)); POSE, CID, FI = POSE[::ST], CID[::ST], FI[::ST]; FPS = FPS / ST          # frames the evaluator saw
P_, C_ = R["PC"]; FEAS = np.unpackbits(np.frombuffer(base64.b64decode(R["feas_all"]), np.uint8))[:P_ * C_].reshape(P_, C_).astype(bool)
SHARE = np.frombuffer(base64.b64decode(R["share_all"]), np.uint8).reshape(P_, C_) / 255.0
QD = len(R["Q"][0]) if R["Q"] and isinstance(R["Q"][0], list) else 0
Qg = np.array(R["Q"]).reshape(C_, QD) if QD else np.zeros((C_, 0)); nq = int(round(360 / R["q_step"]))

def unit(v): return v / np.linalg.norm(v, axis=-1, keepdims=True)
def bvec(az, el): return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])
def w_dir(d, a): d, a = d * D2R, a * D2R; return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])
B = bvec(R["az"], R["el"]); W = w_dir(*R["w"]); e_ = unit(np.cross(B, [0, 1.0, 0])); f_ = np.cross(B, e_)
def pose_mats(pl, el, ax):
    H = DS.Ry(pl * D2R) @ DS.Rx(-el * D2R) @ DS.Ry(ax * D2R); Rs = DS.scapula(el); return Rs.T @ H, Rs
CUFF = R.get("cuff"); HA = np.array([0.0, -1.0, 0.0])
def rot_about(ax, ang, v): return v * math.cos(ang) + np.cross(ax, v) * math.sin(ang) + ax * (ax @ v) * (1 - math.cos(ang))
def rot_mat(ax, ang):
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]]); return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K
def chain(HG, q):
    """pins (N,3) in the scapula frame for grid coordinates q (spare joint angles, then the cuff angle), or None"""
    mq = m if not (CUFF and N == 3) else 1
    pins = [B]
    for k in range(mq):
        pk = pins[-1]
        if k == 0: ek, fk = e_, f_
        else: prev = pins[-2]; ek = unit(prev - (prev @ pk) * pk); fk = np.cross(pk, ek)
        pins.append(math.cos(A[k]) * pk + math.sin(A[k]) * (math.cos(q[k]) * ek + math.sin(q[k]) * fk))
    if CUFF and N == 3:
        h = HG @ HA; w0 = HG @ W; cd = w0 @ h; wp = w0 - cd * h; ws = np.cross(h, wp); p2 = pins[-1]
        Aa, Bb, Cc = p2 @ wp, p2 @ ws, math.cos(A[1]) - cd * (p2 @ h); rr = math.hypot(Aa, Bb) + 1e-9
        if abs(Cc / rr) > 1: return None
        phi = math.atan2(Bb, Aa) + CUFF.get("branch", 1) * math.acos(max(-1, min(1, Cc / rr))); phi = (phi + math.pi) % (2 * math.pi) - math.pi
        if abs(phi) > CUFF.get("range", 90.0) * D2R + 1e-6: return None
        return np.array([B, p2, cd * h + math.cos(phi) * wp + math.sin(phi) * ws])
    Wc = rot_about(HA, q[-1], W) if (CUFF and N >= 4) else W
    pa, pz = pins[-1], HG @ Wc; d = np.clip(pa @ pz, -1, 1); n = unit(np.cross(pa, pz)); den = 1 - d * d + 1e-12
    a = (math.cos(A[N - 3]) - d * math.cos(A[N - 2])) / den; b = (math.cos(A[N - 2]) - d * math.cos(A[N - 3])) / den
    p = a * pa + b * pz; h2 = 1 - p @ p
    if h2 <= 0:
        if h2 < -2e-3: return None
        h2 = 0.0                                                                      # grazing closure (float32 on the GPU accepted it)
    return np.array(pins + [p + R["branch"] * math.sqrt(h2) * n, pz])
def frames_of_members(pins):
    Fm = []
    a_ = pins[0]; nb = unit(pins[1] - (a_ @ pins[1]) * a_); Fm.append(np.c_[a_, nb, np.cross(a_, nb)])
    for k in range(N - 1):
        a_ = pins[k]; c_ = pins[k + 1]; n_ = unit(c_ - (a_ @ c_) * a_); Fm.append(np.c_[a_, n_, np.cross(a_, n_)])
    return Fm
GRP = ["base"] + [f"l{k}" for k in range(1, N)]

# ---------------------------------------------------------------- smooth clip paths (10 fps), then 30 fps
if os.environ.get("OWN_DP") == "1":                                                 # optional own smoothing (plain spare-joint grids)
    MI = np.array(np.unravel_index(np.arange(C_), [nq] * m)).T if m else np.zeros((C_, 0), int)
    KQ = max(1, int(math.ceil(180.0 / FPS / R["q_step"] - 1e-9)))                          # spare joints move <= 180 deg/s
    offs = np.array(np.meshgrid(*[list(range(-KQ, KQ + 1))] * m, indexing="ij")).reshape(m, -1).T if m else np.zeros((1, 0), int)
    NB = np.array([np.ravel_multi_index(tuple(((MI[c] + o) % nq)), [nq] * m) if m else 0 for c in range(C_) for o in offs]).reshape(C_, len(offs))
def dp(ix):
    nf = len(ix); F = FEAS[ix]; S = SHARE[ix]; NEG = -1e18; val = np.full((nf, C_), NEG); prv = {}
    f0 = next((i for i in range(nf) if F[i].any()), None)
    if f0 is None: return None
    val[f0] = np.where(F[f0], 1000 + 10 * S[f0], NEG)
    sh = POSE[ix][:, :3]
    for i in range(f0, nf - 1):
        cand = np.where(val[i][NB] > NEG / 2, val[i][NB], NEG)                       # (C, nb): value of each neighbour at i
        best_nb = cand.argmax(1); bv = cand[np.arange(C_), best_nb]
        nv = np.where(F[i + 1] & (bv > NEG / 2), bv + 1000 + 10 * S[i + 1], NEG)
        upd = nv > val[i + 1]; val[i + 1][upd] = nv[upd]
        for c in np.nonzero(upd)[0]: prv[(i + 1, c)] = (i, NB[c, best_nb[c]], "follow")
        # states at i with no feasible move: held until the motion returns close to frame i's pose
        stuck = (val[i] > NEG / 2) & ~(F[i + 1][NB].any(1))
        for c in np.nonzero(stuck)[0]:
            for k in range(i + 2, nf):
                if np.abs(sh[k] - sh[i]).max() <= RESUME:
                    for c2 in NB[c]:
                        if F[k, c2] and val[i, c] + 200 + 10 * S[k, c2] > val[k, c2]:
                            val[k, c2] = val[i, c] + 200 + 10 * S[k, c2]; prv[(k, c2)] = (i, c, "hold")
                    break
    last = max(range(nf), key=lambda i: (val[i].max() > NEG / 2, i if val[i].max() > NEG / 2 else -1))
    cur = (last, int(val[last].argmax())); path = {}
    while True:
        path[cur[0]] = (cur[1], None)
        if cur not in prv: break
        i0, c0, how = prv[cur]
        if how == "hold":
            for tt in range(i0 + 1, cur[0]): path[tt] = (c0, i0)
        cur = (i0, c0)
    out = []
    for i in range(nf):
        if i in path: out.append(path[i])
        else:                                                                           # before the first / after the last state
            k = min(path, key=lambda t: abs(t - i)); c, h = path[k]; out.append((c, k if h is None else h))
    return out
qrad = lambda c: (Qg[c] * 1.0) if QD else np.zeros(0)
CFG = np.array(R["cfg"]); FEA = np.array(R["feasible"], bool)
def path_of(ix):
    """the evaluator's continuous path; infeasible frames hold the arm at the last followed frame until the motion
    comes back within RESUME deg of it (then it resumes on the path)"""
    out = []; held_at = None; sh = POSE[ix][:, :3]
    first = next((i for i in range(len(ix)) if FEA[ix[i]]), None)
    if first is None: return None
    for i in range(len(ix)):
        if i < first: out.append((CFG[ix[first]], first)); continue
        if held_at is None:
            if FEA[ix[i]]: out.append((CFG[ix[i]], None))
            else: held_at = i - 1; out.append((CFG[ix[held_at]], held_at))
        else:
            if FEA[ix[i]] and np.abs(sh[i] - sh[held_at]).max() <= RESUME: held_at = None; out.append((CFG[ix[i]], None))
            else: out.append((CFG[ix[held_at]], held_at))
    return out
clips = []; nfol = 0; ntot = 0
for ci, name in enumerate(NAMES):
    ix = np.nonzero(CID == ci)[0]; ix = ix[np.argsort(FI[ix])]; path = path_of(ix) if os.environ.get("OWN_DP") != "1" else dp(ix)
    frames = []
    if not path:                                                                         # never followed: hold the clip's first pose at a closing config
        HG0, _ = pose_mats(*POSE[ix[0]][:3]); c0 = next((c for c in range(C_) if chain(HG0, qrad(c)) is not None), 0)
        path = [(c0, 0)] * len(ix)
    for i in range(len(ix)):
        c, held = path[i]
        frames.append(dict(c=c, held=held is not None, src=held if held is not None else i))
    # upsample to 30 fps: interpolate pose and spare angles between consecutive 10 fps frames
    up = max(1, int(round(30 / FPS))); out = []
    for i in range(len(frames) - 1 if len(frames) > 1 else 1):
        for s in range(up if i < len(frames) - 1 else 1):
            a_, b_ = frames[i], frames[min(i + 1, len(frames) - 1)]; tt = s / up
            pa = POSE[ix[a_["src"]]]; pb = POSE[ix[b_["src"]]]; want = POSE[ix[i]] * (1 - tt) + POSE[ix[min(i + 1, len(ix) - 1)]] * tt
            pose = pa * (1 - tt) + pb * tt
            qa, qb = qrad(a_["c"]), qrad(b_["c"]); dq = (qb - qa + math.pi) % (2 * math.pi) - math.pi; q = qa + tt * dq
            HG, Rs = pose_mats(*pose[:3]); pins = chain(HG, q)
            if pins is None: HG, Rs = pose_mats(*pa[:3]); pins = chain(HG, qa); pose = pa
            if pins is None and out: out.append(dict(out[-1])); continue                   # keep the previous frame
            held = a_["held"] and b_["held"]
            Fm = frames_of_members(pins)
            Gx = {}
            if CUFF:                                                                   # carriage turns round the humerus axis with the cuff
                v = HG.T @ pins[-1]; w0p = W - (W @ HA) * HA; vp = v - (v @ HA) * HA
                phi = math.atan2(HA @ np.cross(w0p, vp), w0p @ vp); Gx["cuff"] = (Rs @ HG @ rot_mat(HA, phi)).round(6).ravel().tolist()
            out.append(dict(p=[round(float(x), 2) for x in pose], want=[round(float(x), 2) for x in want], held=bool(held), q=round(float(np.degrees(q[0])) if QD else 0.0, 1),
                            clr=0.0, back=0.0, med=None, G=dict({g: (Rs @ F_).round(6).ravel().tolist() for g, F_ in zip(GRP, Fm)}, **Gx)))
    out.append(dict(out[-1])); clips.append(dict(name=name, fps=FPS * up, frames=out))
    fol = sum(not f["held"] for f in frames); nfol += fol; ntot += len(frames)
    print(f"{name:24s} follows {100 * fol / len(frames):5.1f}% of frames (smooth path)")
print(f"overall follow (smooth) {100 * nfol / ntot:.1f}%")

# ---------------------------------------------------------------- proxy meshes (member local frames, mm)
h = np.array(R["h"]); sizes = R["sizes"]; kind = np.array(R["kind"]); off = np.r_[0, np.cumsum(sizes)]
HUBR = float(R.get("hub_r", HUB_R)); TL = float(R.get("t_link", T_LINK)); STK = float(R.get("stack", 6.0)); TLO = STK - 1.0
IS_LOW = np.array(R.get("is_low", [False] * len(h)), bool); IS_BOT = np.array(R.get("is_bot", [False] * len(h)), bool)
BOT_UNDER = np.array(R.get("bot_under", h), float); FACES = {k: v for k, v in R.get("faces", {}).items()}
def disc(axis, face, t, rad=None):
    rad = HUBR if rad is None else rad
    c = trimesh.creation.cylinder(radius=rad, height=t, sections=64); z = np.array([0, 0, 1.0]); ax = unit(np.asarray(axis, float))
    Rm = trimesh.geometry.align_vectors(z, ax); c.apply_transform(Rm); c.apply_translation(ax * (face + t / 2)); return c
def contoured_hub(dirs, hh, axis, top):
    """hub plate whose top (washer seat side) is the plane `top` along `axis` and whose skin-side underside passes
    through the fitted samples (centre, ring 0.55 R, ring R - 1.5): rings resampled to 48 angles, a rim ring at R"""
    ax = unit(np.asarray(axis, float)); t1 = unit(np.cross(ax, [0, 0, 1.0]) if abs(ax[2]) < 0.9 else np.cross(ax, [1.0, 0, 0])); t2 = np.cross(ax, t1)
    P = dirs * hh[:, None]; z = P @ ax; x, y = P @ t1, P @ t2; r = np.hypot(x, y); phi = np.arctan2(y, x)
    rings = [np.arange(0, 1), np.arange(1, 9), np.arange(9, 21)]; NA = 48; ang = np.linspace(-math.pi, math.pi, NA, endpoint=False)
    def ring_z(ix):
        if len(ix) == 1: return np.full(NA, z[ix[0]])
        o = np.argsort(phi[ix]); pp = np.r_[phi[ix][o] - 2 * math.pi, phi[ix][o], phi[ix][o] + 2 * math.pi]; zz = np.tile(z[ix][o], 3)
        return np.interp(ang, pp, zz)
    radii = [0.0, 0.55 * HUBR, HUBR - 1.5, HUBR]; zs = [ring_z(rings[0]), ring_z(rings[1]), ring_z(rings[2])]; zs.append(zs[-1] + 0.6)
    V, F_ = [], []
    for ri, (rr_, zz) in enumerate(zip(radii, zs)):
        for k_ in range(NA): V.append(ax * zz[k_] + rr_ * (math.cos(ang[k_]) * t1 + math.sin(ang[k_]) * t2))
    for k_ in range(NA): V.append(ax * top + HUBR * (math.cos(ang[k_]) * t1 + math.sin(ang[k_]) * t2))
    V.append(ax * top)
    nr = len(radii) + 1
    for ri in range(nr - 1):
        for k_ in range(NA):
            a0, a1 = ri * NA + k_, ri * NA + (k_ + 1) % NA; b0, b1 = (ri + 1) * NA + k_, (ri + 1) * NA + (k_ + 1) % NA
            F_ += [[a0, b0, b1], [a0, b1, a1]]
    ctop = len(V) - 1
    for k_ in range(NA): F_.append([(nr - 1) * NA + k_, ctop, (nr - 1) * NA + (k_ + 1) % NA])
    return trimesh.Trimesh(np.array(V), np.array(F_), process=False)
meshes = {}
for mi in range(N):
    dl = np.array(R["dirs_local"][mi]); hm = h[off[mi]:off[mi + 1]]; kd = kind[off[mi]:off[mi + 1]]; parts = []
    il = IS_LOW[off[mi]:off[mi + 1]]; theta = 0.0 if mi == 0 else A[mi - 1]
    for kk, axv, J in ((1, [1.0, 0, 0], mi), (2, [math.cos(theta), math.sin(theta), 0.0], mi + 1)):
        idx = np.nonzero(kd == kk)[0]
        if not len(idx): continue
        if il[idx[0]] and str(J) in FACES:                                                  # lower member: contoured underside, flat seat on top
            parts.append(contoured_hub(dl[idx], hm[idx], axv, FACES[str(J)] + TLO))
        else: parts.append(disc(axv, hm[idx[0]], TL))
    rib = np.nonzero(kd == 0)[0]
    if len(rib):
        st = rib.reshape(-1, 3); V = []; Fc = []
        for s in st:
            pl, pc, pr = (hm[s[j]] * dl[s[j]] for j in range(3))
            el = pl + (pl - pc) / 6.0; er = pr + (pr - pc) / 6.0                              # to the 7 mm edges
            ring = [el, pc, er, er + TL * unit(er), pc + TL * unit(pc), el + TL * unit(el)]
            V += ring
        V = np.array(V); nr = 6; ns = len(st)
        for i in range(ns - 1):
            for j in range(nr):
                a0, a1, b0, b1 = i * nr + j, i * nr + (j + 1) % nr, (i + 1) * nr + j, (i + 1) * nr + (j + 1) % nr
                Fc += [[a0, b0, b1], [a0, b1, a1]]
        for e0 in (0, (ns - 1) * nr):
            for j in range(1, nr - 1): Fc.append([e0, e0 + j, e0 + j + 1])
        parts.append(trimesh.Trimesh(V, np.array(Fc), process=False))
    meshes[GRP[mi]] = trimesh.util.concatenate(parts)

# ---------------------------------------------------------------- write the design dir
DD = os.path.join(HERE, "designs", NAME); os.makedirs(DD, exist_ok=True)
sc = trimesh.Scene(); _fin = os.path.join(HERE, "designs", "final", "exo.glb")              # the user's arm parts (viewer only; not committed)
src = trimesh.load(_fin) if os.path.exists(_fin) else trimesh.Scene()
for g, mesh in meshes.items(): sc.add_geometry(mesh, node_name=f"{g}|D4 member {g} (proxy)|0", geom_name=f"{g}|proxy")
moved_w = abs(R["w"][0] - 85.9) > 0.5 or abs(R["w"][1]) > 0.5
for node in src.graph.nodes_geometry:                                                  # the user's arm parts ride on
    T_, gname = src.graph[node]; g = node.split("|")[0]
    if g not in ("H", "F") or "J4 " in node: continue
    mm = src.geometry[gname].copy(); mm.apply_transform(T_); sc.add_geometry(mm, node_name=node, geom_name=node)
HR = np.array(json.load(open(os.path.join(EXO, "avg", "body_mesh.json")))["landmarks"]["rest_humerus"]); U_, _, Vt_ = np.linalg.svd(HR); HR = U_ @ Vt_
ib = np.nonzero(IS_BOT)[0]
if len(ib) and "bot_under" in R:                                                       # BOTTOM's JN hub (block), turned contour, canonical -> rest
    dl_b = np.array(R["dirs_local"][N - 1]); kd_b = kind[off[N - 1]:off[N]]; idxb = np.nonzero(kd_b == 2)[0]
    # samples of link N-1's end hub expressed round W in the canonical humerus frame: same rings (axisymmetric heights)
    loc = dl_b[idxb]; xax = np.array([math.cos(A[N - 2]), math.sin(A[N - 2]), 0.0]); cz = loc @ xax
    tmp = np.array([1.0, 0, 0]) if abs(W[0]) < 0.9 else np.array([0, 1.0, 0]); n_ = unit(tmp - (tmp @ W) * W); Fw = np.c_[W, n_, np.cross(W, n_)]
    sn = np.sqrt(np.clip(1 - cz ** 2, 0, 1)); ph = np.linspace(0, 2 * math.pi, len(idxb), endpoint=False)
    dirs_w = (Fw @ np.c_[cz, sn * np.cos(ph), sn * np.sin(ph)].T).T
    blk = contoured_hub(dirs_w, BOT_UNDER[ib], W, R["zj4"] + T_BOT)
else: blk = disc(W, R["zj4"], T_BOT)
if CUFF:
    sc.add_geometry(blk, node_name="cuff|JN carriage on the sliding cuff (proxy)|0", geom_name="cuff|carriage")
    if "rail_dirs" in R:                                                                # arm-fixed guide rail: contoured underside, 4 mm min, turned top
        RD = np.array(R["rail_dirs"]); RU = np.array(R["rail_under"]); nrow = 3; ncol = len(RD) // nrow
        top = (RU.max() + 4.0); V, Fc = [], []
        for k_ in range(ncol):
            for r_ in range(nrow): V.append(RD[r_ * ncol + k_] * RU[r_ * ncol + k_])
            for r_ in range(nrow): V.append(RD[r_ * ncol + k_] * top)
        V = np.array(V); nr = 2 * nrow
        ring = [0, 1, 2, 5, 4, 3]
        for k_ in range(ncol - 1):
            for j_ in range(nr):
                a0, a1 = k_ * nr + ring[j_], k_ * nr + ring[(j_ + 1) % nr]; b0, b1 = (k_ + 1) * nr + ring[j_], (k_ + 1) * nr + ring[(j_ + 1) % nr]
                Fc += [[a0, b0, b1], [a0, b1, a1]]
        rail = trimesh.Trimesh(V @ HR.T, np.array(Fc), process=False)
        sc.add_geometry(rail, node_name="H|sliding-cuff guide rail (proxy)|0", geom_name="H|rail")
else:
    blk.vertices = blk.vertices @ HR.T
    sc.add_geometry(blk, node_name="H|BOTTOM JN hub block (proxy)|0", geom_name="H|hubblock")
sc.export(os.path.join(DD, "exo.glb"))
axes = [["base", [1.0, 0, 0]]] + [[f"l{k}", [1.0, 0, 0]] for k in range(1, N)] + [[f"l{N - 1}", [math.cos(A[N - 2]), math.sin(A[N - 2]), 0.0]]]
json.dump(dict(subtitle=SUB, clips=clips, axes=axes, design={k: R[k] for k in ("n", "az", "el", "a", "w", "branch", "order", "zj4", "score", "follow", "in_band")}),
          open(os.path.join(DD, "clips.json"), "w"), separators=(",", ":"))
print("wrote", DD)
