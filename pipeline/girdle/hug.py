"""L1 keep-out build of a 3-DOF chain on a thorax-fixed base, so the repo's judges can score it (P3 instrument, v1).

L1 = keep-out CAD (docs/CAD_STANDARD.md scope, user 2026-10-14): hubs are cylinders of the real v4 stack (O23, 10.47 mm:
a 3.0 mm lower plate on the lower member, the rest on the upper one), links are constant 5.5 mm slabs 14 mm wide whose
underside sits on the swept skin envelope + 2 mm, the humeral-rotation rail is a 12 x (shaped) section arc with a circular
top. No fillets, no fairing. Meshes only (watertight), written as a design dir the judges read:
    design.json (dof 3, base = offset3 chain -> judge/base_mount.py), clips.json (per frame G and T for every group),
    exo.glb, parts_full.json (mesh volume x density).

Kinematics: girdle.Chain3 + the minimax axis points from p0_results.json. Rest frame of every member = the thorax frame at
the reference pose (arm hanging). Groups: base (thorax-fixed: world T = -lift), l1, l2 (chain: T = t_k - lift), cuff
(arm-fixed custom parts: the arm's rotation about the GH centre the CHAIN carries, T = p - lift - the residual
misalignment moves them against the skin, as a rigid joint would).

Envelope: skin samples posed per frame (avg/body_pose.py, exact render skin, thorax frame); per member, rays from the
rest-frame origin: r1c = radius beyond which the ray point is >= 2 mm from the first skin sheet; re-entry sheets beyond
it are obstacles (frames where a member would cut one are reported as blocked). Shaped on the FITTING clips only
(data/raw/split.json); evaluated on all.

    python3 hug.py <arch: ring | 3r> [--name l1_ring] [--station 80] [--step 3]
"""
import argparse, hashlib, json, math, os, sys, time
import numpy as np, trimesh
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); import girdle as GD
from girdle import BP, D2R, unit
CLR, T_LINK, W_LINK, HUB_R, STACK, T_LO, GAP_STACK = 2.0, 5.5, 14.0, 11.5, 10.47, 3.0, 0.15
FIRST_SHEET = 6.0; RAMP = math.tan(35 * D2R); RHO = dict(ti=4.43, al=2.70)            # g/cm3: Ti-6Al-4V, AlSi10Mg
HOLD_OUT = tuple(json.load(open(os.path.join(REPO, "data", "raw", "split.json")))["motions"]["held_out"])


# ------------------------------------------------------------------ skin per frame (thorax frame)
def skin_frames(poses, spacing=2.0, r_max=190.0):
    key = hashlib.md5(np.asarray(poses, np.float32).tobytes() + f"{spacing}{r_max}".encode()).hexdigest()[:12]
    path = os.path.join(REPO, ".cache", f"hug_skin_{key}.npy")
    if os.path.exists(path): return np.load(path, mmap_mode="r")
    F = BP.F; V0 = BP.V0; near = np.nonzero(np.linalg.norm(V0[F].mean(1), axis=1) < r_max)[0]
    A = 0.5 * np.linalg.norm(np.cross(V0[F[near, 1]] - V0[F[near, 0]], V0[F[near, 2]] - V0[F[near, 0]]), axis=1)
    n = np.maximum(1, np.ceil(A / spacing ** 2)).astype(int); fi = np.repeat(near, n)
    uv = np.random.default_rng(0).random((len(fi), 2)); fl = uv.sum(1) > 1; uv[fl] = 1 - uv[fl]
    out = np.zeros((len(poses), len(fi), 3), np.float32); t0 = time.time()
    for k, p in enumerate(poses):
        X = BP.posed(dict(zip(["plane", "elev", "axial", "flex", "pron"], p)))
        rig = BP._rig(); _, lift = BP.segs(rig.L, rig.s, dict(zip(["plane", "elev", "axial", "flex", "pron"], p)))
        a, b, c = X[F[fi, 0]], X[F[fi, 1]], X[F[fi, 2]]; out[k] = a + uv[:, :1] * (b - a) + uv[:, 1:] * (c - a) + lift
        if k % 50 == 0: print(f"  skin frames {k}/{len(poses)} {time.time() - t0:.0f}s ({len(fi)} samples)", flush=True)
    os.makedirs(os.path.dirname(path), exist_ok=True); np.save(path, out); return out


# ------------------------------------------------------------------ rays (columns) of a member vs the skin
def ray_bounds(U, Rm, tm, P, frames, obstacles=None, rho_max=160.0):
    """per frame and column: r1 (first skin exit along the ray from the member origin), r1c (beyond: >= CLR from the
    first sheet and from any obstacle points), r2c (below: >= CLR from re-entry sheets). U (J,3) rest-frame directions;
    Rm (T,3,3), tm (T,3) member rest -> thorax; P skin (T,N,3) thorax; obstacles(t) -> (M,3) thorax points (always below)."""
    J = len(U); tree = cKDTree(U); uc = unit(U.mean(0)); cone = math.cos(min(math.pi, math.acos(float(np.clip((U @ uc).min(), -1, 1))) + 0.35))
    r1 = np.full((len(frames), J), np.inf); r1c = np.full((len(frames), J), -np.inf); r2c = np.full((len(frames), J), np.inf)
    for i, t in enumerate(frames):
        Y = (np.asarray(P[t], float) - tm[t]) @ Rm[t]; rho = np.linalg.norm(Y, axis=1); w = Y / rho[:, None]
        keep = (w @ uc > cone) & (rho > 15) & (rho < rho_max); Y, rho, w = Y[keep], rho[keep], w[keep]
        al = np.arcsin(np.clip(CLR / rho, 0, 1)); nb = tree.query_ball_point(w, 2 * np.sin(al / 2) + 1e-9)
        cnt = np.fromiter((len(x) for x in nb), int, len(nb))
        if cnt.sum():
            k = np.repeat(np.arange(len(w)), cnt); j = np.fromiter((v for x in nb for v in x), int, cnt.sum())
            ca = np.clip((w[k] * U[j]).sum(1), -1, 1); along = rho[k] * ca; half = np.sqrt(np.clip(CLR ** 2 - (rho[k] ** 2) * (1 - ca ** 2), 0, None))
            np.minimum.at(r1[i], j, along)
            first = along <= r1[i][j] + FIRST_SHEET
            np.maximum.at(r1c[i], j[first], along[first] + half[first]); np.minimum.at(r2c[i], j[~first], along[~first] - half[~first])
        if obstacles is not None:
            O = (obstacles(t) - tm[t]) @ Rm[t]; ro = np.linalg.norm(O, axis=1); wo = O / ro[:, None]
            al = np.arcsin(np.clip(0.5 / ro, 0, 1)); nb = tree.query_ball_point(wo, 2 * np.sin(al / 2) + 1e-3)
            cnt = np.fromiter((len(x) for x in nb), int, len(nb))
            if cnt.sum():
                k = np.repeat(np.arange(len(wo)), cnt); j = np.fromiter((v for x in nb for v in x), int, cnt.sum())
                np.maximum.at(r1c[i], j, ro[k] * np.clip((wo[k] * U[j]).sum(1), -1, 1) + 0.5)
    return r1, r1c, r2c


def strip_dirs(a, b, rho, n_w=5, step=2.0):
    """column directions of a 14 mm strip along the great circle a -> b at radius rho (rest frame)"""
    a, b = unit(a), unit(b); ang = math.acos(np.clip(a @ b, -1, 1)); ns = max(3, int(ang * rho / step) + 1)
    nrm = unit(np.cross(a, b)); out = []
    for s in np.linspace(0, 1, ns):
        c = unit(math.sin((1 - s) * ang) / math.sin(ang) * a + math.sin(s * ang) / math.sin(ang) * b) if ang > 1e-6 else a
        for wv in np.linspace(-W_LINK / 2, W_LINK / 2, n_w): out.append(unit(c + (wv / rho) * nrm))
    return np.array(out).reshape(ns, n_w, 3)


def disc_dirs(centre, axis, r=HUB_R + 0.5, n_r=4, n_phi=16):
    e1 = unit(np.cross(axis, [1.0, 0, 0] if abs(axis[0]) < 0.9 else [0, 1.0, 0])); e2 = np.cross(axis, e1); pts = [centre]
    for rr in np.linspace(r / n_r, r, n_r):
        for ph in np.linspace(0, 2 * math.pi, n_phi, endpoint=False): pts.append(centre + rr * (math.cos(ph) * e1 + math.sin(ph) * e2))
    return np.array(pts)


# ------------------------------------------------------------------ meshes
def slab_mesh(D, h, t):
    """closed mesh from a (ns, nw) grid of directions D with underside radii h (ns, nw), thickness t along the ray"""
    ns, nw, _ = D.shape; lo = D * h[..., None]; hi = D * (h + t)[..., None]; V = np.r_[lo.reshape(-1, 3), hi.reshape(-1, 3)]; o = ns * nw; Fc = []
    idx = lambda i, j: i * nw + j
    for i in range(ns - 1):
        for j in range(nw - 1):
            a, b, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            Fc += [[a, c, b], [a, d, c], [a + o, b + o, c + o], [a + o, c + o, d + o]]
    for i in range(ns - 1):
        for j in (0, nw - 1):
            a, b = idx(i, j), idx(i + 1, j); Fc += ([[a, b, b + o], [a, b + o, a + o]] if j == 0 else [[a, b + o, b], [a, a + o, b + o]])
    for j in range(nw - 1):
        for i in (0, ns - 1):
            a, b = idx(i, j), idx(i, j + 1); Fc += ([[a, b + o, b], [a, a + o, b + o]] if i == 0 else [[a, b, b + o], [a, b + o, a + o]])
    m = trimesh.Trimesh(V, np.array(Fc), process=True); m.fix_normals(); return m


def hub_mesh(centre_axis_pt, axis, z0, z1, r=HUB_R):
    """cylinder about the joint axis between heights z0 .. z1 measured along the axis from centre_axis_pt"""
    h = z1 - z0; T = np.eye(4); z = unit(axis); x = unit(np.cross(z, [1.0, 0, 0] if abs(z[0]) < 0.9 else [0, 1.0, 0])); T[:3, :3] = np.c_[x, np.cross(z, x), z]
    T[:3, 3] = centre_axis_pt + z * (z0 + h / 2); return trimesh.creation.cylinder(radius=r, height=h, sections=48, transform=T)


# ------------------------------------------------------------------ build
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("arch", choices=["ring", "3r"]); ap.add_argument("--name"); ap.add_argument("--station", type=float, default=80.0)
    ap.add_argument("--step", type=int, default=3); ap.add_argument("--ring-centre", type=float, default=21.0, help="deg about the humerus axis, 0 lateral, + posterior (FINDINGS: rigid arm parts fit in -20..+62)")
    a = ap.parse_args(); name = a.name or f"l1_{a.arch}"
    R0 = json.load(open(os.path.join(HERE, "p0_results.json")))["architectures"]
    key = "3 DOF: 2R shoulder (offset axes) + humeral-rotation ring" if a.arch == "ring" else "3 DOF: 3R, offset axes"
    A0 = R0[key]; pr = dict(A0["params"]); pr["b"] = tuple(pr["b"]); pr["w"] = None if pr.get("w") is None else tuple(pr["w"]); x = np.array(A0["_x"])
    ch = GD.Chain3(pr)
    src = os.path.join(REPO, "pipeline", "full-exo", "designs", "cad_r13_n4_s1343_1", "clips.json"); C = json.load(open(src))
    names = [c["name"] for c in C["clips"] for f in c["frames"]]; W = np.array([f["want"] for c in C["clips"] for f in c["frames"]], float)
    M = GD.Motion(W); A, mg, ok, R1, R2, RA = ch.kin(M); I = np.eye(3)
    o1, o2, o3 = x[:3], x[3:6], x[6:9]
    t1 = (I - R1) @ o1; t2 = t1 + (R1 - R2) @ o2; pA = t2 + (R2 - RA) @ o3        # thorax frame: link translations, chain-carried GH
    Tn = len(W); Rb = np.repeat(I[None], Tn, 0); tb = np.zeros((Tn, 3))
    sel = np.arange(0, Tn, a.step); fit = np.array([names[i] not in HOLD_OUT for i in sel])
    print(f"{name}: {key}; {len(sel)} frames ({fit.sum()} fitting); misalignment worst {np.linalg.norm(pA - M.lift, axis=1).max():.2f} mm", flush=True)
    P = skin_frames(W[sel]); FR = np.arange(len(sel))                                 # P indexed by position in sel
    sub = lambda X: X[sel]
    MB = dict(base=(sub(Rb), sub(tb)), l1=(sub(R1), sub(t1)), l2=(sub(R2), sub(t2)), cuff=(sub(RA), sub(pA)))
    dirs0 = [ch.b, ch.c0, GD.Rh_of(0, 0, 0) @ ch.w]; opp = [x[3 * i:3 * i + 3] - (x[3 * i:3 * i + 3] @ d) * d for i, d in enumerate(dirs0)]
    report = dict(name=name, arch=key, frames=len(sel), fitting_frames=int(fit.sum()), station_mm=a.station)

    def env_along(member, D, obstacles=None):
        Rm, tm = MB[member]; r1, r1c, r2c = ray_bounds(D.reshape(-1, 3), Rm, tm, P, FR, obstacles)
        return r1, r1c, r2c

    def hub_height(member, axis_pt, axis):
        """axial height (from axis_pt along axis) of a flat hub face that clears the swept skin under a O23 disc"""
        Rm, tm = MB[member]; lam = 70.0
        for _ in range(4):
            D = unit(disc_dirs(axis_pt + lam * axis, axis)); r1, r1c, r2c = ray_bounds(D, Rm, tm, P, FR[fit])
            need = np.nanmax(np.where(np.isfinite(r1c), r1c, -np.inf), 0)               # per disc column, over fitting frames
            pts = disc_dirs(axis_pt + lam * axis, axis); rad = np.linalg.norm(pts, axis=1)
            dl = np.where(np.isfinite(need), (need - rad) / np.clip(unit(pts) @ axis, 0.2, 1), -np.inf).max()
            if not np.isfinite(dl): break
            lam = lam + dl
        return float(lam)

    # joints: axis directions pointing out of the body
    hubs = []
    for i, d in enumerate(dirs0[:2] if a.arch == "ring" else dirs0):
        d = unit(d)
        if (opp[i] + 80 * d) @ np.array([0.0, 0.3, 1.0]) < (opp[i] - 80 * d) @ np.array([0.0, 0.3, 1.0]): d = -d     # the lateral-superior sense
        hubs.append([opp[i], d])
    lower = ["base", "l1", "cuff"]; upper = ["l1", "l2", "l2"]
    for i, (pt, d) in enumerate(hubs):
        lam = hub_height(lower[i], pt, d); hubs[i].append(lam); print(f"  J{i + 1} hub face {lam:.1f} mm out along its axis ({lower[i]} lower / {upper[i]} upper)", flush=True)
    parts = []                                                                       # (group, name, mesh, material)
    for i, (pt, d, lam) in enumerate(hubs):
        parts.append((lower[i], f"J{i + 1} lower plate keep-out (O23 x {T_LO})", hub_mesh(pt, d, lam, lam + T_LO), "ti"))
        parts.append((upper[i], f"J{i + 1} upper hub + cap keep-out (O23 x {STACK - T_LO - GAP_STACK:.2f})", hub_mesh(pt, d, lam + T_LO + GAP_STACK, lam + STACK), "ti"))
    hubc = [pt + (lam + T_LO / 2) * d for pt, d, lam in hubs]
    lvl_up = [float(np.linalg.norm(pt + (lam + T_LO + GAP_STACK) * d)) for pt, d, lam in hubs]   # an upper member leaves its hub here
    lvl_lo = [float(np.linalg.norm(pt + lam * d)) for pt, d, lam in hubs]                         # a lower member's plate face
    # the ring: arm-fixed rail at the station, carriage on link 2
    if a.arch == "ring":
        tr = ch.joint_travel(M)["J3"]; psi = np.radians(np.arange(-180, 180, 2.0)); s = a.station
        # rail spans the arm angles the carriage visits (travel) + the carriage's half arc, centred on ring_centre
        span = tr["span"] + 2 * math.degrees(12.0 / 60.0); th = np.radians(np.linspace(-span / 2, span / 2, int(span / 2) + 1) + a.ring_centre)
        # columns: rays from the GH centre through points on the arm at station s +- 6 mm, around theta
        rows = []
        for ds in np.linspace(-6, 6, 4):
            rows.append([unit(np.array([-60 * math.sin(t_), -(s + ds), 60 * math.cos(t_)])) for t_ in th])
        Dr = np.transpose(np.array(rows), (1, 0, 2))                                  # (n_theta, 4, 3) in the arm (canonical) frame
        r1, r1c, r2c = env_along("cuff", Dr); need = np.where(np.isfinite(r1c[fit]), r1c[fit], -np.inf).max(0).reshape(Dr.shape[:2])
        need = np.where(np.isfinite(need), need, np.nanmax(np.where(np.isfinite(need), need, np.nan)))
        hr = need; rail = slab_mesh(Dr, hr, 4.0); parts.append(("cuff", "humeral-rotation rail keep-out (arm-fixed)", rail, "ti"))
        # radius of the circular rail top (about the humerus axis) and the carriage
        top = Dr * (hr + 4.0)[..., None]; rho_top = float(np.hypot(top[..., 0], top[..., 2]).max())
        report["ring"] = dict(travel=tr, rail_arc_deg=round(span, 1), rail_centre_deg=a.ring_centre, rail_top_radius_mm=round(rho_top, 1),
                              rail_underside_gap_note="shaped to the arm envelope (fitting frames) + 2 mm")
        # carriage on link 2: at the arm angle ring_centre when the ring angle is at mid-travel; link-2 rest frame = canonical at reference
        mid = math.radians(a.ring_centre + (tr["min"] + tr["max"]) / 2)              # carriage angle in link 2: arm angle = carriage - q3(t)
        cth = np.radians(np.linspace(-12, 12, 7)) + mid; cr = []
        for ds in np.linspace(-6, 6, 4): cr.append([unit(np.array([-rho_top * math.sin(t_), -(s + ds), rho_top * math.cos(t_)])) for t_ in cth])
        Dc = np.transpose(np.array(cr), (1, 0, 2)); hc = np.linalg.norm(np.array([[-rho_top * math.sin(t_), -(s), rho_top * math.cos(t_)] for t_ in cth]), axis=1)[:, None].repeat(4, 1) + 0.3
        parts.append(("l2", "ring carriage keep-out (on link 2)", slab_mesh(Dc, hc, 6.0), "ti")); carriage_c = unit(Dc.mean((0, 1))) * (hc.mean() + 3)
        ends = [(0, hubc[0], hubc[1]), (1, hubc[1], carriage_c)]
    else:
        ends = [(0, hubc[0], hubc[1]), (1, hubc[1], hubc[2])]
    # links: slabs on the swept envelope; link 2 rides over link 1 (nested) where they meet
    tops = {}
    for k, ca, cb in ends:
        mem = ["l1", "l2"][k]; rho = 0.5 * (np.linalg.norm(ca) + np.linalg.norm(cb)); D = strip_dirs(ca, cb, rho)
        obst = None
        if mem == "l2" and "l1" in tops:
            Tl1 = tops["l1"]; Rl1, tl1 = MB["l1"]; obst = lambda t, Tl1=Tl1, Rl1=Rl1, tl1=tl1: Tl1 @ Rl1[t].T + tl1[t]
        r1, r1c, r2c = env_along(mem, D, obst); need = np.where(np.isfinite(r1c[fit]), r1c[fit], -np.inf).max(0).reshape(D.shape[:2])
        need = np.where(np.isfinite(need), need, np.nanmedian(np.where(np.isfinite(need), need, np.nan)))
        ns = D.shape[0]; sa = np.linspace(0, 1, ns)[:, None] * np.linalg.norm(cb - ca)              # mm along the strip
        lam_a = lvl_up[k]; lam_b = lvl_lo[k + 1] if k + 1 < len(lvl_lo) else float(np.linalg.norm(cb)) - 3.0
        h = np.maximum(need, np.maximum(lam_a - RAMP * sa, lam_b - RAMP * (sa[-1] - sa)))      # leave each hub level, ramp <= 35 deg
        m = slab_mesh(D, h, T_LINK); parts.append((mem, f"link {k + 1} slab keep-out ({T_LINK} mm Ti, {W_LINK:.0f} wide)", m, "ti"))
        tops[mem] = (D * (h + T_LINK)[..., None]).reshape(-1, 3)
        blocked = ((r2c < (h + T_LINK).reshape(-1)[None]) & np.isfinite(r2c)).any(1)
        gap = np.where(np.isfinite(r1), h.reshape(-1)[None] - r1, np.nan); cov = np.isfinite(gap) & (gap < 60)
        inb = np.where(cov.any(1), ((gap >= 2) & (gap <= 10) & cov).sum(1) / np.maximum(1, cov.sum(1)), np.nan)
        inb14 = np.where(cov.any(1), ((gap >= 2) & (gap <= 14) & cov).sum(1) / np.maximum(1, cov.sum(1)), np.nan)
        report[f"link{k + 1}"] = dict(length_mm=round(float(sa[-1, 0]), 1), underside_mm=[round(float(h.min()), 1), round(float(h.max()), 1)],
                                      blocked_frames_fit=int(blocked[fit].sum()), blocked_frames_held_out=int(blocked[~fit].sum()),
                                      in_band_2_10_fit=round(float(np.nanmean(inb[fit])), 3), in_band_2_10_held_out=round(float(np.nanmean(inb[~fit])), 3),
                                      in_band_2_14_fit=round(float(np.nanmean(inb14[fit])), 3), median_gap=round(float(np.nanmedian(gap[cov])), 1))
        print(f"  link {k + 1}: {report[f'link{k + 1}']}", flush=True)
        report.setdefault("_blocked", np.zeros(len(sel), bool)); report["_blocked"] |= blocked
    # ---------------- write the design dir
    dd = os.path.join(REPO, "pipeline", "full-exo", "designs", name); os.makedirs(dd, exist_ok=True)
    sc = trimesh.Scene(); pf = []
    for k, (g, nm, m, mat) in enumerate(parts):
        sc.add_geometry(m, node_name=f"{g}|{nm}|{k}", geom_name=f"{g}|{nm}|{k}")
        pf.append(dict(k=k, group=g, name=nm, vol_cm3=round(abs(m.volume) / 1000, 3), material=dict(ti="Ti-6Al-4V", al="AlSi10Mg")[mat],
                       mass_g=round(abs(m.volume) / 1000 * RHO[mat], 2), valid=bool(m.is_watertight), faces=len(m.faces)))
    sc.export(os.path.join(dd, "exo.glb"))
    json.dump(dict(key=name, n=3, level="L1 keep-out", parts=pf), open(os.path.join(dd, "parts_full.json"), "w"), indent=1)
    blocked_all = np.zeros(Tn, bool); blocked_all[sel] = report.pop("_blocked")                   # judges see a blocked sample frame and its neighbours
    for j in range(1, a.step): blocked_all[np.clip(sel + j, 0, Tn - 1)] |= blocked_all[sel]
    clips = dict(subtitle=f"{name} (L1 keep-out, thorax-fixed base)", design=name, clips=[]); k = 0
    for c in C["clips"]:
        fr = []
        for f in c["frames"]:
            G = dict(base=I, l1=R1[k], l2=R2[k], cuff=RA[k]); T = dict(base=-M.lift[k], l1=t1[k] - M.lift[k], l2=t2[k] - M.lift[k], cuff=pA[k] - M.lift[k])
            fr.append(dict(p=f["want"], want=f["want"], held=bool(blocked_all[k]), G={g: np.asarray(v).round(6).ravel().tolist() for g, v in G.items()},
                           T={g: np.asarray(v).round(3).tolist() for g, v in T.items()})); k += 1
        clips["clips"].append(dict(name=c["name"], frames=fr))
    json.dump(clips, open(os.path.join(dd, "clips.json"), "w"), separators=(",", ":"))
    base = dict(mount="thorax", chain="offset3", prm=dict(b=list(pr["b"]), a1=pr["a1"], a2=pr["a2"], branch=pr["branch"], w=None if pr["w"] is None else list(pr["w"])),
                axis_points_mm=[o1.tolist(), o2.tolist(), o3.tolist()])
    json.dump(dict(id=name, source="pipeline/girdle/hug.py (L1 keep-out)", n_joints=3 if a.arch == "3r" else 2, sliding_cuff=a.arch == "ring", dof=3,
                   kinematics=dict(arch=key, **{k_: v for k_, v in A0["params"].items()}), base=base, built_with="L1 keep-out: cylinders + slabs, no fairing",
                   note="ring = humeral-rotation joint about the humerus axis on the upper arm" if a.arch == "ring" else "3R, offset axes"),
              open(os.path.join(dd, "design.json"), "w"), indent=1)
    report["mass_custom_g"] = round(sum(p["mass_g"] for p in pf), 1); report["all_watertight"] = all(p["valid"] for p in pf)
    json.dump(report, open(os.path.join(dd, "hug_report.json"), "w"), indent=1)
    print(f"-> {dd}: {len(parts)} parts, {report['mass_custom_g']} g, watertight {report['all_watertight']}; blocked frames {int(blocked_all.sum())}/{Tn}")


if __name__ == "__main__":
    main()
