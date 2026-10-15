"""JUDGE (R9 strength): independent FEA of the custom load-path parts - CalculiX (ccx 2.21, linear static) on gmsh tet10
(C3D10) meshes of the exported STEP solids. Outside the design pipeline: it reads only <design>/step/*.step,
parts_full.json (names, materials), score_14mm.json (min skin gap) and the design-load constants below.

Parts (the load path, scapula -> arm): D4-01 base (Ti), D4-02.. links (Ti), BOTTOM (BOTTOM + neck + JN hub, 7075-T6).
Hubs are found from the B-rep: coaxial pin / bore cylinders whose axis passes through GH (the part frame's origin; every
joint axis of the spherical chain does). Joint surfaces of a hub (where the bearing hardware bears on the part), by the
joint version the radii identify:
  v4 lower (integral O10 pin):  recess floor + wall, pin O10, ring-nut shoulder, M8 stub   (r 3.9-9.3, from the seat up)
  v4 upper (O12 sleeve bore):   bore, chamfers, washer A / B annuli under / on the boss     (r 5.9-9.0, U0..U1)
  v5 lower (O7 pin, O8.2 collar): collar top (inner-ring shoulder), pin O7, nut thread       (r 2.4-4.2, from L1 up)
  v5 upper (O11 bearing bore):  lip, bore, M18 spigot thread for the clamping cap          (r 4.85-5.6 and 8.9-9.1)
Supports and loads act through *COUPLING / *DISTRIBUTING (RBE3-type: the joint is the hardware, the part is not
stiffened): the support hub's reference node is fixed in 6 DOF, the loads go on the load hub's reference node.
  base   support: the mount tab's last 6 mm (bolted / bonded to the user's scapula handler); load: J1 hub
  links  support: the proximal hub (lower joint index); load: the distal hub
  BOTTOM support: the upper-cuff M4 tapped holes (the arm load enters through the cuff); load: the JN hub
Unit load cases (6 ccx steps, superposed in post): moments and forces along the load hub's axis and two perpendiculars.
Design cases (user 2026-10-15: MVP2 assist = arm gravity support + margin, ~10 N.m; MVP1 unpowered):
  D1   10 N.m in the WORST direction (exact: largest singular value of the nodal stress map) - covers 10 N.m about each
       axis perpendicular to the joint axis and the 10 N.m cable torque about it, and every mix with |M| <= 10 N.m
  D1F  the full cuff wrench behind that moment: 10 N.m about GH delivered by a 50 N cuff force at 200 mm, i.e. 50 N
       through GH plus 10 N.m perpendicular to it, worst pair (sampled) - governs; D1F >= D1 at every node
  MVP1 R17's envelope (1 N.m about GH, 5 N at the cuff = D1F / 10) + 3 g of the part's own weight
Stress: nodal von Mises (ccx extrapolated, averaged). Rule for idealised zones: nodes within one element size of a
coupling surface (bearing / support idealised) are excluded from the judged maximum; their peak is reported.
Fatigue: Goodman, 1e7 cycles; MVP2 range taken fully reversed (+-D1F: the assist direction turns with the pose),
endurance of a machined surface; R = 0 also reported. Deflection: the hub-to-hub rigid motion (least-squares fit of
the load hub's coupling nodes) moves the point at GH by d_GH; points at radius R from GH move radially (toward or away
from the skin) only by d_GH, since a rotation about GH is tangential. Chain bound = sum of the parts' worst d_GH,
compared with the 2 mm floor and the design's min skin gap (score_14mm.json).
Mesh: size from the thinnest wall (area-weighted 5th percentile of the inward ray thickness): h = t/2 and t/3, both
solved (convergence check); the finer mesh is judged.

    python3 judge/fea.py <design id> [--parts D4-01,BOTTOM] [--fast]   -> <design>/judge/fea.json
    python3 judge/fea.py --validate                                     -> judge/fea_validation.json
    (--fast: one mesh (t/2.5), no convergence pair. Work files in .cache/fea/. OMP_NUM_THREADS defaults to 2.)
"""
import argparse, json, math, os, re, shutil, subprocess, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import design_dir, REPO

VERSION = "fea-2026-10-15a (CalculiX 2.21 C3D10, gmsh tet10, distributing couplings)"
# ---------------------------------------------------------------- materials (MPa, g/cm3); endurance at 1e7, R = -1, machined
MAT = {"Ti-6Al-4V": dict(E=114e3, nu=0.34, Sy=880.0, Su=950.0, Se=425.0, rho=4.43,
                         src="annealed: E 114 GPa, Sy 880, Su 950 (MMPDS); Se 500 smooth x 0.85 machined (thin_study)"),
       "7075-T6": dict(E=71.7e3, nu=0.33, Sy=503.0, Su=572.0, Se=160.0, rho=2.81,
                       src="Sy 503, Su 572 (MMPDS); Se 160 at 5e8 rotating beam (ASM) used at 1e7 (conservative)"),
       "AlSi10Mg (SLM)": dict(E=70e3, nu=0.33, Sy=230.0, Su=350.0, Se=60.0, rho=2.67,
                              src="SLM stress-relieved: Sy 230, Su 350; Se ~60 as-built surface at 1e7 (literature low end)")}
# ---------------------------------------------------------------- design loads (N, mm)
M_DESIGN = 10.0e3          # N.mm: arm gravity support + margin (user 2026-10-15; was 25 N.m)
CUFF_MM = 200.0            # cuff centre from GH (judge/dynamics.py CUFF_MM)
F_CUFF = M_DESIGN / CUFF_MM  # 50 N: the cuff force that delivers M_DESIGN
MVP1_SCALE = 0.1           # R17 envelope: 1 N.m about GH, 5 N at the cuff = D1F / 10
G_MULT = 3.0               # MVP1 own weight x 3 (gravity + R17's peak joint accelerations, ~2500 deg/s2 at <= 0.1 m)
SF_MIN, FATIGUE_MIN, FLOOR_MM = 1.5, 1.0, 2.0
GH = np.zeros(3)
UNIT_M, UNIT_F = 1000.0, 10.0  # unit cases applied (N.mm, N); scaled in post

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

# ================================================================ geometry: hubs from the B-rep
def _sample(gm, tag, n=9):
    (u0, v0), (u1, v1) = [np.array(x) for x in gm.model.getParametrizationBounds(2, tag)]
    uu, vv = np.meshgrid(np.linspace(u0, u1, n), np.linspace(v0, v1, n)); uv = np.c_[uu.ravel(), vv.ravel()].ravel()
    return np.array(gm.model.getValue(2, tag, uv)).reshape(-1, 3), np.array(gm.model.getNormal(tag, uv)).reshape(-1, 3)

def _fit_cyl(P, N):
    w, V = np.linalg.eigh(N.T @ N); a = V[:, 0]
    e1 = np.cross(a, [1, 0, 0] if abs(a[0]) < 0.9 else [0, 1, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(a, e1)
    x, y = P @ e1, P @ e2; s = np.linalg.lstsq(np.c_[2 * x, 2 * y, np.ones_like(x)], x * x + y * y, rcond=None)[0]
    r = math.sqrt(max(s[2] + s[0] ** 2 + s[1] ** 2, 0.0)); c = s[0] * e1 + s[1] * e2
    rad = P - c - np.outer(P @ a - c @ a, a); convex = bool(np.mean(np.sum(rad * N, 1)) > 0)
    return a, c, r, convex

def cylinders(gm):
    """every cylindrical B-rep face: axis direction a, a point c on the axis, radius, convex (pin) or concave (bore)"""
    out = []
    for _, t in gm.model.getEntities(2):
        if gm.model.getType(2, t) != "Cylinder": continue
        P, N = _sample(gm, t); a, c, r, cv = _fit_cyl(P, N); z = P @ a
        out.append(dict(tag=t, a=a, c=c, r=r, convex=cv, z0=float(z.min()), z1=float(z.max()), off=float(np.linalg.norm(c - (c @ a) * a))))
    return out

JOINTS = {"v4": dict(pin=5.0, bore=6.0), "v5": dict(pin=3.5, bore=5.5)}
def find_hubs(cyls, tol=0.03):
    """hubs = joint axes through GH carrying a joint pin (lower member) or bearing bore (upper member)"""
    hubs = []
    for cy in cyls:
        if cy["off"] > 0.5: continue                                                     # axis must pass through GH
        for ver, R in JOINTS.items():
            role = "lower" if (cy["convex"] and abs(cy["r"] - R["pin"]) < tol) else ("upper" if (not cy["convex"] and abs(cy["r"] - R["bore"]) < tol) else None)
            if role is None: continue
            a = cy["a"] * (1 if (cy["z0"] + cy["z1"]) >= 0 else -1)                         # axis pointing away from GH
            h = next((h for h in hubs if abs(h["a"] @ a) > 0.9995), None)
            if h is None: hubs.append(dict(a=a, role=role, ver=ver, z=[cy["z0"] * np.sign(a @ cy["a"]), cy["z1"] * np.sign(a @ cy["a"])]))
            else: h["z"] += [cy["z0"] * np.sign(a @ cy["a"]), cy["z1"] * np.sign(a @ cy["a"])]
    for h in hubs: h["z"] = [float(min(h["z"])), float(max(h["z"]))]
    return hubs

# ================================================================ mesh (gmsh, tet10 -> C3D10 node order)
GMSH2CCX = [0, 1, 2, 3, 4, 5, 6, 7, 9, 8]                                               # gmsh tet10 edges (2,3),(1,3) -> ccx (1,3),(2,3) [0-based]
FACES = np.array([[0, 1, 2], [0, 3, 1], [1, 3, 2], [2, 3, 0]])                            # C3D10 faces S1..S4 (corner nodes)
FACE_MID = np.array([[4, 5, 6], [7, 8, 4], [8, 9, 5], [9, 7, 6]])                       # their mid-side nodes (ccx order)

def wall_thickness(step, h_probe=1.0):
    """wall thickness from the surface: for every surface triangle the inward ray is marched with the exact signed
    distance (judge/sdist.py; a step of |d| never crosses the surface) until it exits. Returns (thin = area-weighted 10th
    percentile, median, centroids, thickness per centroid). The 10th percentile skips the edge rounds and chamfers
    (rays there exit early) but sees a thinned strap (cad_r18 link 2: 2.2-2.5 mm over its middle)"""
    import gmsh, trimesh
    from sdist import mesh as sd_mesh
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.model.occ.importShapes(step); gmsh.model.occ.synchronize()
        gmsh.option.setNumber("Mesh.MeshSizeMax", h_probe); gmsh.option.setNumber("Mesh.MeshSizeMin", 0.2 * h_probe); gmsh.model.mesh.generate(2)
        tags, X, _ = gmsh.model.mesh.getNodes(); X = X.reshape(-1, 3); idx = {t: i for i, t in enumerate(tags)}
        _, _, ntag = gmsh.model.mesh.getElements(2); T = np.array([idx[t] for t in ntag[0]]).reshape(-1, 3)
    finally: gmsh.finalize()
    m = trimesh.Trimesh(X, T, process=True); m.fix_normals(); M = sd_mesh(np.asarray(m.vertices, float), np.asarray(m.faces), h=0.3)
    c = m.triangles_center; n = m.face_normals; s = np.full(len(c), 0.02); done = np.zeros(len(c), bool)
    for _ in range(80):
        live = ~done
        if not live.any(): break
        d = M.signed(c[live] - s[live, None] * n[live])
        ex = d > -0.01; s_l = s[live]; s_l = np.where(ex, s_l, s_l + np.maximum(-d, 0.01)); s[live] = s_l
        done[np.nonzero(live)[0][ex]] = True
        done |= s > 60.0
    ok = done & (s < 60.0) & (s > 0.05); w = m.area_faces[ok]; ts = s[ok]; o_ = np.argsort(ts); cw = np.cumsum(w[o_]) / w.sum()
    return float(ts[o_][np.searchsorted(cw, 0.10)]), float(np.median(ts)), c[ok], ts

def mesh_step(step, h, out_msh=None, local=None):
    """tet10 mesh of the STEP solid: nodes (n,3), tets (m,10) in C3D10 order (0-based). h: uniform size, or with
    local = (centroids, thickness, k, h_min, h_max) the size at x is the wall thickness at the nearest surface sample / k"""
    import gmsh
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.model.occ.importShapes(step); gmsh.model.occ.synchronize()
        vols = gmsh.model.getEntities(3)
        if len(vols) != 1: raise RuntimeError(f"{step}: {len(vols)} volumes (one solid expected)")
        if local is None:
            gmsh.option.setNumber("Mesh.MeshSizeMax", h); gmsh.option.setNumber("Mesh.MeshSizeMin", 0.15 * h)
            gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
        else:
            # background size field: a coarse linear tet mesh carries the size (wall at the nearest surface samples / k)
            from scipy.spatial import cKDTree
            C, t, k, hmin, hmax = local; sz = np.clip(t / k, hmin, hmax)
            for hb_ in (2.0, 1.2, 0.8, 0.5):                                                    # thin twisted straps: a coarse PLC can self-intersect
                try:
                    gmsh.model.mesh.clear(); gmsh.option.setNumber("Mesh.MeshSizeMax", hb_); gmsh.option.setNumber("Mesh.MeshSizeMin", 0.25 * hb_); gmsh.model.mesh.generate(3); break
                except Exception:
                    if hb_ == 0.5: raise
            _, Xb, _ = gmsh.model.mesh.getNodes(); Xb = Xb.reshape(-1, 3); tg, _, _ = gmsh.model.mesh.getNodes()
            et, _, en = gmsh.model.mesh.getElements(3); ib = np.full(int(tg.max()) + 1, -1); ib[tg] = np.arange(len(tg)); Tb = ib[np.asarray(en[list(et).index(4)]).reshape(-1, 4)]
            _, i8 = cKDTree(C).query(Xb, k=8); hb = sz[i8].min(1)                       # both walls of a thin section are among the 8 nearest
            data = np.c_[Xb[Tb][:, :, 0], Xb[Tb][:, :, 1], Xb[Tb][:, :, 2], hb[Tb]].ravel()
            v = gmsh.view.add("size"); gmsh.view.addListData(v, "SS", len(Tb), data.tolist())
            gmsh.model.mesh.clear()
            f = gmsh.model.mesh.field.add("PostView"); gmsh.model.mesh.field.setNumber(f, "ViewTag", v); gmsh.model.mesh.field.setAsBackgroundMesh(f)
            gmsh.option.setNumber("Mesh.MeshSizeMax", hmax); gmsh.option.setNumber("Mesh.MeshSizeMin", hmin)
            gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0); gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0); gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
        gmsh.option.setNumber("Mesh.ElementOrder", 2); gmsh.option.setNumber("Mesh.SecondOrderLinear", 1)   # straight-edged tet10: projecting
        gmsh.option.setNumber("Mesh.HighOrderOptimize", 0)                                       # mid-nodes onto BSpline faces takes minutes
        gmsh.option.setNumber("Mesh.Optimize", 1); gmsh.option.setNumber("Mesh.Algorithm3D", 1)
        try: gmsh.model.mesh.generate(3)
        except Exception:
            gmsh.model.mesh.clear(); gmsh.option.setNumber("Mesh.Algorithm", 1); gmsh.model.mesh.generate(3)   # MeshAdapt surfaces
        tags, X, _ = gmsh.model.mesh.getNodes(); X = X.reshape(-1, 3)
        et, _, en = gmsh.model.mesh.getElements(3)
        k_ = list(et).index(11)                                                          # 11 = 10-node tetrahedron
        idx = np.full(int(tags.max()) + 1, -1); idx[tags] = np.arange(len(tags))
        T = idx[np.asarray(en[k_]).reshape(-1, 10)][:, GMSH2CCX]
        if out_msh: gmsh.write(out_msh)
    finally: gmsh.finalize()
    used = np.unique(T); remap = np.full(len(X), -1); remap[used] = np.arange(len(used))
    return X[used], remap[T]

def tet_volumes(X, T):
    a, b, c, d = (X[T[:, i]] for i in range(4)); return np.einsum("ij,ij->i", np.cross(b - a, c - a), d - a) / 6.0

def boundary_faces(T):
    """(elem, face 0..3) of every boundary face of the tet10 mesh, and the boundary node mask"""
    F = T[:, FACES].reshape(-1, 3); S = np.sort(F, 1); key = (S[:, 0].astype(np.int64) << 42) | (S[:, 1].astype(np.int64) << 21) | S[:, 2]
    _, inv, cnt = np.unique(key, return_inverse=True, return_counts=True); b = np.nonzero(cnt[inv] == 1)[0]
    el, fc = b // 4, b % 4
    return el, fc

# ================================================================ CalculiX deck, run, results
def write_inp(path, X, T, mat, couplings, steps, fixed_nodes=None, extra=""):
    """couplings: {name: (ref id (1-based), ref xyz, [(elem, face)])} - distributing (load) couplings; fixed_nodes: 0-based
    node ids held in u1-u3 (the support; ccx 2.21 does not let a fixed DISTRIBUTING reference node restrain the part);
    steps: [list of (node, dof, value)] or a raw load block per step"""
    n = len(X)
    with open(path, "w") as f:
        f.write("*HEADING\nexo R9 FEA (judge/fea.py)\n*NODE, NSET=NALL\n")
        f.write("".join(f"{i + 1},{x:.6f},{y:.6f},{z:.6f}\n" for i, (x, y, z) in enumerate(X)))
        for nm, (rid, rx, _) in couplings.items(): f.write(f"*NODE, NSET=R{nm}\n{rid},{rx[0]:.6f},{rx[1]:.6f},{rx[2]:.6f}\n")
        f.write("*ELEMENT, TYPE=C3D10, ELSET=EALL\n")
        f.write("".join(f"{e + 1}," + ",".join(str(v + 1) for v in t) + "\n" for e, t in enumerate(T)))
        for nm, (rid, _, ef) in couplings.items():
            f.write(f"*SURFACE, NAME=S{nm}, TYPE=ELEMENT\n" + "".join(f"{e + 1},S{fc + 1}\n" for e, fc in ef))
            f.write(f"*COUPLING, REF NODE={rid}, SURFACE=S{nm}, CONSTRAINT NAME=C{nm}\n*DISTRIBUTING\n1,6\n")
        f.write(f"*MATERIAL, NAME=M\n*ELASTIC\n{mat['E']:.1f},{mat['nu']:.3f}\n*SOLID SECTION, ELSET=EALL, MATERIAL=M\n")
        if fixed_nodes is not None and len(fixed_nodes): f.write("*BOUNDARY\n" + "".join(f"{i + 1},1,3\n" for i in fixed_nodes))
        f.write(extra)
        for loads in steps:
            f.write("*STEP\n*STATIC\n")
            if loads and isinstance(loads, str): f.write(loads)
            elif loads: f.write("*CLOAD, OP=NEW\n" + "".join(f"{nd},{dof},{v:.6e}\n" for nd, dof, v in loads))
            f.write("*NODE FILE\nU\n*EL FILE\nS\n*END STEP\n")

def run_ccx(workdir, job, threads=2, timeout=3600):
    env = dict(os.environ, OMP_NUM_THREADS=str(threads), CCX_NPROC_EQUATION_SOLVER=str(threads), CCX_NPROC_STIFFNESS=str(threads))
    t0 = time.time(); p = subprocess.run(["ccx", "-i", job], cwd=workdir, env=env, capture_output=True, text=True, timeout=timeout)
    open(os.path.join(workdir, job + ".ccx.log"), "w").write(p.stdout + p.stderr)
    if p.returncode != 0 or "*ERROR" in p.stdout or not os.path.exists(os.path.join(workdir, job + ".frd")):
        err = [l for l in (p.stdout + p.stderr).splitlines() if "ERROR" in l or "error" in l][:5]
        raise RuntimeError(f"ccx failed ({job}): {err or p.stdout[-500:]}")
    return time.time() - t0

def read_frd(path, n):
    """[(U (n,3), S (n,6) [xx yy zz xy yz zx])] per step, nodes 1..n (extra coupling nodes dropped)"""
    out, cur, blk, rows = [], {}, None, []
    def flush():
        nonlocal blk, rows
        if blk is None: return
        arr = np.zeros((n, 6 if blk == "STRESS" else 3))
        for nd, vals in rows:
            if nd <= n: arr[nd - 1] = vals[:arr.shape[1]]
        cur["U" if blk == "DISP" else "S"] = arr; blk, rows = None, []
    with open(path) as f:
        for line in f:
            if line.startswith(" -4"):
                flush(); name = line.split()[1]; blk = name if name in ("DISP", "STRESS") else "skip"
            elif line.startswith(" -1") and blk:
                if blk == "skip": continue
                s = line[13:].rstrip("\n"); rows.append((int(line[3:13]), [float(s[i:i + 12]) for i in range(0, len(s), 12) if s[i:i + 12].strip()]))
            elif line.startswith(" -3") and blk:
                if blk == "skip": blk = None; continue
                flush()
                if "U" in cur and "S" in cur: out.append((cur["U"], cur["S"])); cur = {}
    return out

# ================================================================ von Mises as a norm: VM(s) = |L s|
_Q = np.zeros((6, 6)); _Q[:3, :3] = [[1, -0.5, -0.5], [-0.5, 1, -0.5], [-0.5, -0.5, 1]]; _Q[3:, 3:] = 3 * np.eye(3)
_L = np.linalg.cholesky(_Q + 1e-12 * np.eye(6)).T
def vm(S): return np.sqrt(np.maximum(np.einsum("...i,ij,...j->...", S, _Q, S), 0.0))

def rigid_fit(P, U):
    """least-squares rigid motion of points P under displacements U: (translation at the centroid c, rotation phi, c)"""
    c = P.mean(0); r = P - c; t = U.mean(0); A = np.zeros((3 * len(P), 3))
    A[0::3, 1], A[0::3, 2] = r[:, 2], -r[:, 1]; A[1::3, 0], A[1::3, 2] = -r[:, 2], r[:, 0]; A[2::3, 0], A[2::3, 1] = r[:, 1], -r[:, 0]
    phi = np.linalg.lstsq(A, (U - t).ravel(), rcond=None)[0]                                # phi x r = A phi
    return t, phi, c

# ================================================================ one part
def frame_of(a):
    a = a / np.linalg.norm(a); e1 = np.cross(a, [0, 0, 1.0] if abs(a[2]) < 0.9 else [1.0, 0, 0]); e1 /= np.linalg.norm(e1); return a, e1, np.cross(a, e1)

def hub_nodes(X, bn, hub):
    """boundary nodes on the joint surfaces of a hub (see the module doc) and the hub's reference point on its axis"""
    a = hub["a"]; z = X @ a; r = np.linalg.norm(X - np.outer(z, a), axis=1); zc = 0.5 * (hub["z"][0] + hub["z"][1])
    near = bn & (np.abs(z - zc) < 15.0)
    if hub["ver"] == "v4" and hub["role"] == "lower":
        ring = near & (r > 5.6) & (r < 9.1); zs = z[ring].max(); sel = near & (r > 3.9) & (r < 9.32) & (z > zs - 0.05)
    elif hub["ver"] == "v4":
        ring = near & (r > 6.4) & (r < 8.9); z0, z1 = z[ring].min(), z[ring].max(); sel = near & (r > 5.9) & (r < 9.02) & (z > z0 - 0.05) & (z < z1 + 0.05)
    elif hub["role"] == "lower":
        ring = near & (r > 3.6) & (r < 4.05); zs = z[ring].max(); sel = near & (r > 2.4) & (r < 4.2) & (z > zs - 0.05)
    else:
        ring = near & (r > 5.6) & (r < 8.8); z0, z1 = z[ring].min(), z[ring].max(); sel = near & (((r > 4.85) & (r < 5.6)) | ((r > 8.9) & (r < 9.1))) & (z > z0 - 0.05) & (z < z1 + 0.05)
    zz = z[sel]; return sel, a * 0.5 * (zz.min() + zz.max())

def tab_nodes(X, bn, hub, L=6.0):
    """the base's mount tab end: boundary nodes in the last L mm of the tab, measured outward from the hub axis"""
    a = hub["a"]; R = X - np.outer(X @ a, a); far = np.argmax(np.linalg.norm(R, axis=1)); d = R[far] / np.linalg.norm(R[far])
    s = X @ d; sel = bn & (s > s.max() - L) & (np.linalg.norm(R, axis=1) > 13.0)
    return sel, X[sel].mean(0)

def hole_nodes(X, bn, cyls, centres=None, r_rng=(1.5, 1.8), max_r=260.0):
    """BOTTOM's upper-cuff tapped M4 holes: boundary nodes on those hole walls (hole axis near a cuff screw if known)"""
    sel = np.zeros(len(X), bool); used = []
    for cy in cyls:
        if cy["convex"] or not (r_rng[0] < cy["r"] < r_rng[1]): continue
        mid = cy["c"] + cy["a"] * (cy["c"] @ cy["a"]) * 0 + cy["a"] * (0.5 * (cy["z0"] + cy["z1"]) - cy["c"] @ cy["a"])
        if centres is not None and len(centres):
            dl = min(np.linalg.norm(np.cross(cc - mid, cy["a"])) for cc in centres)
            if dl > 1.5: continue
        elif np.linalg.norm(mid) > max_r: continue
        z = (X - cy["c"]) @ cy["a"]; rr = np.linalg.norm(X - cy["c"] - np.outer(z, cy["a"]), axis=1)
        z0, z1 = cy["z0"] - cy["c"] @ cy["a"], cy["z1"] - cy["c"] @ cy["a"]
        sel |= bn & (np.abs(rr - cy["r"]) < 0.05) & (z > z0 - 0.05) & (z < z1 + 0.05); used.append(mid)
    return sel, (np.mean(used, 0) if used else None), len(used)

def coupling_faces(T, el, fc, mask):
    corners = T[el][np.arange(len(el))[:, None], FACES[fc]]
    ok = mask[corners].all(1); return list(zip(el[ok], fc[ok]))

def part_setup(step, name, kind, hub_idx=None, cuff_centres=None):
    """geometry analysis: hubs, which is supported and which loaded"""
    import gmsh
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.model.occ.importShapes(step); gmsh.model.occ.synchronize(); cy = cylinders(gmsh)
        vol = sum(gmsh.model.occ.getMass(3, t) for _, t in gmsh.model.getEntities(3)); com = np.array(gmsh.model.occ.getCenterOfMass(3, gmsh.model.getEntities(3)[0][1]))
    finally: gmsh.finalize()
    hubs = find_hubs(cy)
    if not hubs: raise RuntimeError(f"{name}: no joint hub found (no pin / bore through GH)")
    for h in hubs: h["zc"] = 0.5 * (h["z"][0] + h["z"][1])
    return dict(hubs=hubs, cyls=cy, vol_mm3=vol, com=com)

H_RANGE = {2: (0.4, 3.0), 3: (0.3, 2.0), 2.5: (0.35, 2.5)}                          # size clamp per k (mm)
def prepare_part(step, name, kind, k, wall, cuff_centres=None):
    """mesh (size = local wall / k), the load hub's joint surfaces and the support nodes"""
    G = part_setup(step, name, kind); hubs = G["hubs"]
    if kind == "link": hubs = sorted(hubs, key=lambda h: -abs(h["a"][0]))                 # proximal hub axis = the member frame's x
    load = hubs[1] if kind == "link" else hubs[0]
    if kind == "link" and len(hubs) != 2: raise RuntimeError(f"{name}: {len(hubs)} hubs found (2 expected)")
    hmin, hmax = H_RANGE[k]; C, tw = wall[2], wall[3]
    X, T = mesh_step(step, None, local=(C, tw, k, hmin, hmax))
    vol = tet_volumes(X, T)
    if (vol <= 0).any(): raise RuntimeError(f"{name}: {int((vol <= 0).sum())} inverted tets")
    el, fc = boundary_faces(T); bn = np.zeros(len(X), bool); bn[np.unique(T[el][np.arange(len(el))[:, None], np.c_[FACES, FACE_MID][fc]])] = True
    ld_sel, ld_ref = hub_nodes(X, bn, load)
    if kind == "base": fx_sel, fx_ref = tab_nodes(X, bn, hubs[0]); fx_info = "mount tab, last 6 mm (encastre)"
    elif kind == "link": fx_sel, fx_ref = hub_nodes(X, bn, hubs[0]); fx_info = f"proximal hub joint surfaces ({hubs[0]['ver']} {hubs[0]['role']}, encastre)"
    else:
        fx_sel, fx_ref, nh = hole_nodes(X, bn, G["cyls"], cuff_centres); fx_info = f"{nh} upper-cuff M4 tapped hole walls (encastre)"
        if nh == 0: raise RuntimeError(f"{name}: no cuff holes found")
    ef = coupling_faces(T, el, fc, ld_sel)
    if len(ef) < 6: raise RuntimeError(f"{name}: load coupling has {len(ef)} faces")
    if fx_sel.sum() < 6: raise RuntimeError(f"{name}: support has {int(fx_sel.sum())} nodes")
    # idealised zones: within the coarse (k = 2) local element size of the support / of the load hub's joint surfaces
    from scipy.spatial import cKDTree
    _, i8 = cKDTree(C).query(X, k=8); dex = np.clip(tw[i8].min(1) / 2.0, *H_RANGE[2])
    d_fx, _ = cKDTree(X[fx_sel]).query(X, k=1); d_ld, _ = cKDTree(X[ld_sel]).query(X, k=1)
    supz = d_fx <= dex; ldz = (d_ld <= dex) & ~supz
    a, e1, e2 = frame_of(load["a"])
    info = dict(n_nodes=len(X), n_tets=len(T), k=k, h_range=[hmin, hmax], load_hub=dict(ver=load["ver"], role=load["role"], axis=np.round(load["a"], 4).tolist(), ref=np.round(ld_ref, 2).tolist()),
                hubs=[dict(ver=h["ver"], role=h["role"], axis=np.round(h["a"], 4).tolist()) for h in G["hubs"]],
                support=fx_info, support_ref=np.round(fx_ref, 2).tolist(), n_load_faces=len(ef), n_support_nodes=int(fx_sel.sum()),
                mesh_volume_mm3=round(float(vol.sum()), 1), brep_volume_mm3=round(float(G["vol_mm3"]), 1))
    return dict(X=X, T=T, ld_sel=ld_sel, fx_sel=fx_sel, ld_ref=ld_ref, ef=ef, supz=supz, ldz=ldz, bcz=supz | ldz, B=np.array([a, e1, e2]),
                vol_mm3=float(vol.sum()), com=G["com"], info=info)

def solve(P, mat, steps, work, threads=2):
    """steps: list of (moment N.mm (3), force N (3)) at the load hub's reference point -> U (k,n,3), S (k,n,6), seconds"""
    os.makedirs(work, exist_ok=True); X = P["X"]; rid = len(X) + 1
    loads = [[(rid, 4 + j, m[j]) for j in range(3) if abs(m[j]) > 0] + [(rid, 1 + j, f[j]) for j in range(3) if abs(f[j]) > 0] for m, f in steps]
    inp = os.path.join(work, "part.inp"); write_inp(inp, X, P["T"], mat, {"LD": (rid, P["ld_ref"], P["ef"])}, loads, np.nonzero(P["fx_sel"])[0])
    import hashlib
    hsh = hashlib.sha1(open(inp, "rb").read()).hexdigest(); cache = os.path.join(work, "result.npz")
    if os.path.exists(cache):                                                            # same deck solved before: reuse
        z = np.load(cache)
        if str(z["hash"]) == hsh: return z["U"], z["S"], float(z["sec"])
    sec = run_ccx(work, "part", threads); R = read_frd(os.path.join(work, "part.frd"), len(X))
    if len(R) != len(steps): raise RuntimeError(f"{len(R)} result steps for {len(steps)} load cases")
    for f in os.listdir(work):                                                           # keep the deck + log, drop the bulk
        if f.endswith((".frd", ".12d", ".cvg", ".sta", ".out")): os.remove(os.path.join(work, f))
    U, S = np.stack([r[0] for r in R]), np.stack([r[1] for r in R]); np.savez(cache, U=U, S=S, sec=sec, hash=hsh)
    return U, S, sec

def unit_data(P, mat, work, threads=2):
    """the six unit cases (moments, then forces, along the load hub's axis and two perpendiculars)"""
    B = P["B"]; steps = [(UNIT_M * B[i], np.zeros(3)) for i in range(3)] + [(np.zeros(3), UNIT_F * B[i]) for i in range(3)]
    U, S, sec = solve(P, mat, steps, work, threads)
    t_ph = [rigid_fit(P["X"][P["ld_sel"]], U[k][P["ld_sel"]]) for k in range(6)]
    dGH = np.array([t + np.cross(ph, GH - c) for t, ph, c in t_ph]); rot = np.array([ph for _, ph, _ in t_ph])
    return dict(X=P["X"], U=U, S=S, bcz=P["bcz"], ldz=P["ldz"], supz=P["supz"], B=B, ld_ref=P["ld_ref"], dGH=dGH, rot=rot,
                mass_g=P["vol_mm3"] * mat["rho"] / 1000.0, com=P["com"]), sec

# ================================================================ post: design cases
def fib_sphere(n):
    i = np.arange(n) + 0.5; phi = np.arccos(1 - 2 * i / n); th = math.pi * (1 + 5 ** 0.5) * i
    return np.c_[np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)]

def wrench_maps(D):
    """per-node stress maps for unit moment (N.mm) and unit force through GH (N), global xyz components: (n,6,3) each"""
    B = D["B"]; SM = np.einsum("knc,kj->ncj", D["S"][:3], B) / UNIT_M                      # rows of B are the case directions
    SFh = np.einsum("knc,kj->ncj", D["S"][3:], B) / UNIT_F                                 # force at the hub ref point
    c = D["ld_ref"]; Cx = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
    SF = SFh + np.einsum("ncj,jk->nck", SM, -Cx)                                         # force through GH: + moment (GH - c) x F = -c x F
    dM = np.einsum("kc,kj->cj", D["dGH"][:3], B) / UNIT_M; dFh = np.einsum("kc,kj->cj", D["dGH"][3:], B) / UNIT_F
    dF = dFh + dM @ (-Cx); rM = np.einsum("kc,kj->cj", D["rot"][:3], B) / UNIT_M
    return SM, SF, dM, dF, rM

def worst_pair(A, Bm, nf=240, nphi=24):
    """max over |m| = 1 (N.mm), |f| = 1 (N), m perpendicular to f, of |A m + B f| for stacked maps (k,p,3): the D1F wrench"""
    best = np.zeros(A.shape[0]); arg = [None] * A.shape[0]
    for fdir in fib_sphere(nf):
        e1 = np.cross(fdir, [0, 0, 1.0] if abs(fdir[2]) < 0.9 else [1.0, 0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(fdir, e1)
        bf = Bm @ (F_CUFF * fdir)                                                         # (k,p)
        for ph in np.linspace(0, 2 * math.pi, nphi, endpoint=False):
            m = M_DESIGN * (math.cos(ph) * e1 + math.sin(ph) * e2); v = np.linalg.norm(A @ m + bf, axis=-1)
            up = v > best; best = np.where(up, v, best)
            for i in np.nonzero(up)[0]: arg[i] = (fdir, m)
    return best, arg

def post_part(name, mat, res, D):
    SM, SF, dM, dF, rM = wrench_maps(D)
    LM = np.einsum("ic,ncj->nij", _L, SM); LF = np.einsum("ic,ncj->nij", _L, SF)            # VM-metric maps (n,6,3)
    sM = np.linalg.svd(LM, compute_uv=False)[:, 0]; d1 = M_DESIGN * sM                     # D1: worst direction, exact
    a = D["B"][0]; P = np.stack([D["B"][1], D["B"][2]], 1)
    d1_perp = M_DESIGN * np.linalg.svd(LM @ P, compute_uv=False)[:, 0]; d1_ax = M_DESIGN * np.linalg.norm(LM @ a, axis=1)
    d2 = F_CUFF * np.linalg.svd(LF, compute_uv=False)[:, 0]
    bound = d1 + d2; judged = ~D["bcz"]
    cand = np.argsort(-np.where(judged, bound, 0))[:600]; cand_bc = np.argsort(-np.where(D["ldz"], bound, 0))[:200]; cand_s = np.argsort(-np.where(D["bcz"] & ~D["ldz"], bound, 0))[:100]
    idx = np.unique(np.r_[cand, cand_bc, cand_s]); d1f = np.zeros(len(bound)); d1f[idx] = worst_pair(LM[idx], LF[idx])[0]
    w = np.where(judged)[0]
    kj = w[np.argmax(d1f[w])]; _, argw = worst_pair(LM[[kj]], LF[[kj]]); f_star, m_star = argw[0]
    m1 = np.linalg.svd(LM[kj])[2][0] * M_DESIGN                                              # D1's worst moment at that node
    def peak(v, mask):
        i = np.nonzero(mask)[0]; k = i[np.argmax(v[i])]; return float(v[k]), k
    out = {}
    for nm, v in (("D1", d1), ("D1_perp", d1_perp), ("D1_axial", d1_ax), ("D2_force_50N", d2), ("D1F", d1f)):
        s, k = peak(v, judged); sl, kl = peak(v, D["ldz"]) if D["ldz"].any() else (0.0, 0); ss, ks = peak(v, D["bcz"] & ~D["ldz"]) if (D["bcz"] & ~D["ldz"]).any() else (0.0, 0)
        out[nm] = dict(vm_MPa=round(s, 1), SF=round(mat["Sy"] / max(s, 1e-9), 2), at_mm=np.round(D["X"][k], 1).tolist(), r_from_GH_mm=round(float(np.linalg.norm(D["X"][k])), 1),
                       load_hub_zone_vm_MPa=round(sl, 1), load_hub_zone_at_mm=np.round(D["X"][kl], 1).tolist(), support_zone_vm_MPa=round(ss, 1), raw_vm_MPa=round(max(s, sl, ss), 1))
    # MVP1: D1F / 10 plus the own weight x G_MULT as a force at the COM carried to the load hub (bound)
    W = D["mass_g"] * 1e-3 * 9.81 * G_MULT; lever = np.linalg.norm(D["com"] - D["ld_ref"])
    s_w = W * np.max(np.linalg.svd(LF[w], compute_uv=False)[:, 0]) + W * lever * np.max(sM[w])
    mvp1 = MVP1_SCALE * out["D1F"]["vm_MPa"] + s_w
    out["MVP1"] = dict(vm_MPa=round(mvp1, 2), SF=round(mat["Sy"] / mvp1, 1), weight_N=round(W, 3), note="R17 envelope (D1F / 10) + 3 g own weight, bound")
    s = out["D1F"]["vm_MPa"]
    fat = dict(load="MVP2 +-D1F fully reversed, 1e7 cycles", sigma_a_MPa=s, Se_MPa=mat["Se"], SF_fully_reversed=round(mat["Se"] / s, 2),
               SF_R0_goodman=round(1.0 / ((s / 2) / mat["Se"] + (s / 2) / mat["Su"]), 2))
    # deflection: worst |d_GH| under D1F (sampled), hub rotation per N.m
    GdM, GdF = dM[None], dF[None]
    dgh = float(worst_pair(GdM, GdF, nf=400, nphi=36)[0][0])
    k_rot = 1.0 / (np.linalg.svd(rM, compute_uv=False) * 1e3 * 180 / math.pi)             # N.m/deg (soft, mid, stiff)
    Umax = 0.0
    LU = np.stack([np.einsum("knc,kj->ncj", D["U"][:3], D["B"]) / UNIT_M, np.einsum("knc,kj->ncj", D["U"][3:], D["B"]) / UNIT_F], 0)
    cU = np.argsort(-np.linalg.norm(LU[0], axis=(1, 2)))[:200]
    UF = LU[1][cU] + np.einsum("ncj,jk->nck", LU[0][cU], -np.array([[0, -D["ld_ref"][2], D["ld_ref"][1]], [D["ld_ref"][2], 0, -D["ld_ref"][0]], [-D["ld_ref"][1], D["ld_ref"][0], 0]]))
    Umax = float(worst_pair(LU[0][cU], UF, nf=200, nphi=24)[0].max())
    gov = dict(node=int(kj), m_about_GH_Nmm=np.round(m_star, 1).tolist(), f_through_GH_N=np.round(F_CUFF * f_star, 2).tolist(), m_D1_Nmm=np.round(m1, 1).tolist())
    return dict(material=mat_name_of(mat), Sy_MPa=mat["Sy"], cases=out, fatigue=fat, governing_wrench=gov,
                deflection=dict(d_GH_mm=round(dgh, 3), max_point_disp_mm=round(Umax, 3), k_rot_Nm_per_deg=np.round(k_rot, 2).tolist(),
                                note="d_GH: motion of the GH point carried by the load hub relative to the support under D1F (the radial = skin-gap part of every point's motion); max_point: largest |u| of any node (incl. tangential)"),
                mass_g=round(D["mass_g"], 2))

def mat_name_of(mat): return next(k for k, v in MAT.items() if v is mat)

# ================================================================ design
PARTS = (("D4-01", "base"), ("D4-02", "link"), ("D4-03", "link"), ("D4-04", "link"), ("D4-05", "link"), ("BOTTOM", "bottom"))
def material_for(parts_full, prefix):
    for p in parts_full["parts"]:
        if p["name"].startswith(prefix + " ") or (prefix == "BOTTOM" and p["name"].startswith("BOTTOM +")):
            m = p.get("material", ""); return MAT["7075-T6"] if "7075" in m or "7075" in p["name"] else (MAT["AlSi10Mg (SLM)"] if "AlSi" in m else MAT["Ti-6Al-4V"])
    return MAT["Ti-6Al-4V"]

def cuff_screw_centres(dd):
    """centres of the upper-cuff screws (exo.glb, group H, one node per screw) in BOTTOM's frame"""
    try:
        import trimesh
        sc = trimesh.load(os.path.join(dd, "exo.glb")); out = []
        for node in sc.graph.nodes_geometry:
            T_, gn = sc.graph[node]; g, nm = node.split("|")[:2]
            if g == "H" and "upper cuff" in nm.lower() and "m4" in nm.lower():
                V = sc.geometry[gn].vertices; out.append(((np.c_[V, np.ones(len(V))] @ T_.T)[:, :3]).mean(0))
        return out or None
    except Exception: return None

def min_skin_gap(dd):
    for f in ("score_14mm.json", "score.json"):
        try: return min(c["min_gap"] for c in json.load(open(os.path.join(dd, f)))["clips"]), f
        except Exception: pass
    return None, None

def wrench_at_hub(m_gh, f, c):
    """a wrench given about GH (moment m, force f through GH) as moment / force at the hub reference point c"""
    return np.asarray(m_gh, float) - np.cross(c, f), np.asarray(f, float)

def judged_peak(S, mask):
    v = vm(S); i = np.nonzero(mask)[0]; k = i[np.argmax(v[i])]; return float(v[k]), int(k)

def part_fea(step, pre, kind, mat, work0, fast=False, centres=None, threads=2):
    t0 = time.time(); wall = wall_thickness(step)
    log(f"{pre}: {mat_name_of(mat)}, wall thickness p10 {wall[0]:.2f} mm, median {wall[1]:.2f}")
    k0 = 2.5 if fast else 2
    P = prepare_part(step, pre, kind, k0, wall, centres)
    D, sec = unit_data(P, mat, os.path.join(work0, f"{pre}_k{k0}"), threads)
    p = post_part(pre, mat, P["info"], D); p["mesh"] = dict(P["info"], ccx_s=round(sec, 1)); p["wall_mm"] = dict(p10=round(wall[0], 2), median=round(wall[1], 2))
    log(f"  k {k0}: {P['info']['n_nodes']} nodes, ccx {sec:.0f} s; D1 {p['cases']['D1']['vm_MPa']} MPa, D1F {p['cases']['D1F']['vm_MPa']} MPa (SF {p['cases']['D1F']['SF']}) at {p['cases']['D1F']['at_mm']}; d_GH {p['deflection']['d_GH_mm']} mm")
    p["convergence"] = None
    if not fast:
        # the governing wrench again on the t/3 mesh: same exclusion zones (coarse size), one factorisation
        gw = p["governing_wrench"]; m_s, f_s = wrench_at_hub(gw["m_about_GH_Nmm"], gw["f_through_GH_N"], P["ld_ref"])
        S_c = np.einsum("k,knc->nc", np.r_[m_s @ D["B"].T / UNIT_M, f_s @ D["B"].T / UNIT_F], D["S"])   # the same wrench on the coarse mesh
        vc, kc = judged_peak(S_c, ~D["bcz"])
        P3 = prepare_part(step, pre, kind, 3, wall, centres)
        U3, S3, sec3 = solve(P3, mat, [(m_s, f_s)], os.path.join(work0, f"{pre}_k3"), threads)
        vf, kf = judged_peak(S3[0], ~P3["bcz"]); ratio = vf / vc
        t_, ph_, c_ = rigid_fit(P3["X"][P3["ld_sel"]], U3[0][P3["ld_sel"]]); dgh_f = float(np.linalg.norm(t_ + np.cross(ph_, GH - c_)))
        t_, ph_, c_ = rigid_fit(D["X"][P["ld_sel"]], np.einsum("k,knc->nc", np.r_[m_s @ D["B"].T / UNIT_M, f_s @ D["B"].T / UNIT_F], D["U"])[P["ld_sel"]]); dgh_c = float(np.linalg.norm(t_ + np.cross(ph_, GH - c_)))
        p["convergence"] = dict(wrench="governing D1F wrench", nodes=[P["info"]["n_nodes"], P3["info"]["n_nodes"]], vm_MPa=[round(vc, 1), round(vf, 1)], change=round(ratio - 1, 3),
                                at_mm=[np.round(D["X"][kc], 1).tolist(), np.round(P3["X"][kf], 1).tolist()], d_GH_mm=[round(dgh_c, 3), round(dgh_f, 3)], ccx_s=round(sec3, 1),
                                rule="judged D1F = coarse worst-wrench peak x max(1, fine / coarse) under the governing wrench")
        log(f"  k 3: {P3['info']['n_nodes']} nodes, ccx {sec3:.0f} s; governing wrench {vc:.1f} -> {vf:.1f} MPa ({100 * (ratio - 1):+.1f} %), d_GH {dgh_c:.3f} -> {dgh_f:.3f} mm")
        if ratio > 1.0:                                                                   # never let the coarse mesh flatter the part
            for nm in ("D1", "D1_perp", "D1_axial", "D2_force_50N", "D1F"):
                c_ = p["cases"][nm]; c_["vm_coarse_MPa"] = c_["vm_MPa"]; c_["vm_MPa"] = round(c_["vm_MPa"] * ratio, 1); c_["SF"] = round(mat["Sy"] / c_["vm_MPa"], 2)
                for z_ in ("load_hub_zone_vm_MPa", "support_zone_vm_MPa", "raw_vm_MPa"): c_[z_] = round(c_[z_] * ratio, 1)
            p["cases"]["MVP1"]["vm_MPa"] = round(p["cases"]["MVP1"]["vm_MPa"] * ratio, 2); p["cases"]["MVP1"]["SF"] = round(mat["Sy"] / p["cases"]["MVP1"]["vm_MPa"], 1)
            s_ = p["cases"]["D1F"]["vm_MPa"]; p["fatigue"].update(sigma_a_MPa=s_, SF_fully_reversed=round(mat["Se"] / s_, 2), SF_R0_goodman=round(1.0 / ((s_ / 2) / mat["Se"] + (s_ / 2) / mat["Su"]), 2))
        if dgh_f > dgh_c: p["deflection"]["d_GH_mm"] = round(p["deflection"]["d_GH_mm"] * dgh_f / dgh_c, 3)
    p["seconds"] = round(time.time() - t0, 1); return p

def summarise(out, dd):
    gap, gsrc = min_skin_gap(dd); P = out["parts"]
    sf = min(p["cases"]["D1F"]["SF"] for p in P.values()); worst = min(P, key=lambda k: P[k]["cases"]["D1F"]["SF"])
    fsf = min(p["fatigue"]["SF_fully_reversed"] for p in P.values()); dsum = sum(p["deflection"]["d_GH_mm"] for p in P.values())
    defl_ok = dsum <= FLOOR_MM and (gap is None or dsum < gap)
    chain = [k for k, _ in PARTS if os.path.exists(os.path.join(dd, "step", k + ".step"))]
    out["summary"] = dict(min_SF=sf, worst_part=worst, min_SF_D1=min(p["cases"]["D1"]["SF"] for p in P.values()), min_SF_MVP1=min(p["cases"]["MVP1"]["SF"] for p in P.values()),
                          fatigue_min_SF=fsf, chain_d_GH_mm=round(dsum, 3), min_skin_gap_mm=None if gap is None else round(gap, 2), gap_source=gsrc,
                          floor_kept=None if gap is None else bool(dsum <= gap - FLOOR_MM), deflection_ok=bool(defl_ok),
                          parts=sorted(P), complete=all(k in P for k in chain),
                          passes=bool(sf >= SF_MIN and fsf >= FATIGUE_MIN and defl_ok and all(k in P for k in chain)))
    return out

def judge_design(dd, only=None, fast=False, threads=2):
    did = os.path.basename(os.path.normpath(dd)); pf = json.load(open(os.path.join(dd, "parts_full.json")))
    work0 = os.path.join(REPO, ".cache", "fea", did); centres = cuff_screw_centres(dd); t_all = time.time()
    out = dict(version=VERSION, design=did, fast=fast, loads=dict(M_design_Nm=M_DESIGN / 1e3, F_cuff_N=F_CUFF, cuff_mm=CUFF_MM, mvp1_scale=MVP1_SCALE, own_weight_g=G_MULT),
               thresholds=dict(SF_min=SF_MIN, fatigue_SF_min=FATIGUE_MIN, floor_mm=FLOOR_MM), materials=MAT, parts={})
    for pre, kind in PARTS:
        step = os.path.join(dd, "step", pre + ".step")
        if not os.path.exists(step) or (only and pre not in only): continue
        out["parts"][pre] = part_fea(step, pre, kind, material_for(pf, pre), work0, fast, centres, threads)
    if not out["parts"]: raise RuntimeError("no parts analysed")
    out["seconds"] = round(time.time() - t_all, 1)
    return out

# ================================================================ validation (analytic cases through the same chain)
def _cq_step(shape, path):
    import cadquery as cq
    cq.exporters.export(cq.Workplane().add(shape), path); return path

def validate(threads=2):
    import cadquery as cq
    work = os.path.join(REPO, ".cache", "fea", "_validate"); os.makedirs(work, exist_ok=True); mat = MAT["Ti-6Al-4V"]; E, nu = mat["E"], mat["nu"]
    rows = []
    # 1) cantilever 100 x 10 x 3 (Ti): fixed end face (distributing coupling, ref fixed), end moment / tip force / torque
    L, b, t = 100.0, 10.0, 3.0; step = _cq_step(cq.Solid.makeBox(L, b, t, cq.Vector(0, -b / 2, -t / 2)), os.path.join(work, "beam.step"))
    I = b * t ** 3 / 12; G = E / (2 * (1 + nu))
    # torsion of a b x t rectangle (Timoshenko & Goodier series): J, tau_max
    ser = lambda f: sum(f(n) for n in range(1, 61, 2))
    J = (1 / 3) * b * t ** 3 * (1 - (192 / math.pi ** 5) * (t / b) * ser(lambda n: math.tanh(n * math.pi * b / (2 * t)) / n ** 5))
    k_tau = 1 - (8 / math.pi ** 2) * ser(lambda n: 1 / (n ** 2 * math.cosh(n * math.pi * b / (2 * t))))
    for h in (t / 2, t / 3):
        X, T = mesh_step(step, h); el, fc = boundary_faces(T)
        bn = np.zeros(len(X), bool); bn[np.unique(T[el][np.arange(len(el))[:, None], np.c_[FACES, FACE_MID][fc]])] = True
        end0, end1 = bn & (X[:, 0] < 1e-6), bn & (X[:, 0] > L - 1e-6)
        cpl = {"LD": (len(X) + 1, np.array([L, 0, 0]), coupling_faces(T, el, fc, end1))}
        M, F, Tq = 1.0e4, 50.0, 1.0e4; rid = len(X) + 1
        wd = os.path.join(work, f"beam_h{h:.2f}"); os.makedirs(wd, exist_ok=True)
        write_inp(os.path.join(wd, "v.inp"), X, T, mat, cpl, [[(rid, 5, M)], [(rid, 3, F)], [(rid, 4, Tq)]], np.nonzero(end0)[0])
        sec = run_ccx(wd, "v", threads); R = read_frd(os.path.join(wd, "v.frd"), len(X))
        mid = (np.abs(X[:, 0] - L / 2) < 0.6 * h) & (np.abs(X[:, 1]) < b / 2 - 1.0)
        top = mid & (X[:, 2] > t / 2 - 1e-6)
        s_m = float(np.mean(np.abs(R[0][1][top, 0]))); s_m_an = 6 * M / (b * t ** 2)
        tip = end1; th_m = float(np.mean(rigid_fit(X[tip], R[0][0][tip])[1][1])); th_an = M * L / (E * I)
        s_f = float(np.mean(np.abs(R[1][1][top, 0]))); s_f_an = 6 * F * (L / 2) / (b * t ** 2)
        w_f = float(np.mean(R[1][0][tip, 2])); w_an = F * L ** 3 / (3 * E * I) + F * L / (5 / 6 * G * b * t)
        # torsion: max shear at mid-length, middle of the long side (y = 0, z = +-t/2)
        sideM = (np.abs(X[:, 0] - L / 2) < 0.6 * h) & (np.abs(X[:, 1]) < 0.6 * h) & (np.abs(np.abs(X[:, 2]) - t / 2) < 1e-6)
        tau = float(np.mean(vm(R[2][1][sideM]) / math.sqrt(3))); tau_an = Tq * t * k_tau / J
        phi = float(rigid_fit(X[tip], R[2][0][tip])[1][0]); phi_an = Tq * L / (G * J)
        for case, fe, an in (("beam end moment 10 N.m: bending stress mid-span", s_m, s_m_an), ("beam end moment: tip rotation (rad)", th_m, th_an),
                             ("beam tip force 50 N: bending stress mid-span", s_f, s_f_an), ("beam tip force: tip deflection (mm, + shear)", w_f, w_an),
                             ("beam torque 10 N.m: max shear mid-span (warping free ends)", tau, tau_an), ("beam torque: twist (rad)", phi, phi_an)):
            rows.append(dict(case=case, h=round(h, 3), nodes=len(X), fe=round(fe, 5), analytic=round(an, 5), err=round(fe / an - 1, 4), ccx_s=round(sec, 1)))
    # 2) thick-walled ring (hub): ri 6, ro 11.5, 4 long, internal pressure 100 MPa, symmetry plane at z = 0 (= an 8 mm ring)
    ri, ro, H, p = 6.0, 11.5, 4.0, 100.0
    step = _cq_step(cq.Solid.makeCylinder(ro, H).cut(cq.Solid.makeCylinder(ri, H)), os.path.join(work, "ring.step"))
    for h in ((ro - ri) / 2, (ro - ri) / 3):
        X, T = mesh_step(step, h); el, fc = boundary_faces(T); corners = T[el][np.arange(len(el))[:, None], FACES[fc]]
        r_ = np.linalg.norm(X[:, :2], axis=1); bore = (np.abs(r_[corners] - ri) < 1e-3).all(1)
        dl = "*DLOAD\n" + "".join(f"{e + 1},P{f_ + 1},{p:.3f}\n" for e, f_ in zip(el[bore], fc[bore]))
        bot = np.nonzero(np.abs(X[:, 2]) < 1e-6)[0]; ix = bot[np.argmin(np.abs(X[bot, 1]) + np.abs(X[bot, 0] - ro))]; iy = bot[np.argmin(np.abs(X[bot, 0]) + np.abs(X[bot, 1] - ro))]
        ix2 = bot[np.argmin(np.abs(X[bot, 1]) + np.abs(X[bot, 0] + ro))]
        bc = "*BOUNDARY\n" + "".join(f"{i + 1},3,3\n" for i in bot) + f"{ix + 1},2,2\n{ix2 + 1},2,2\n{iy + 1},1,1\n"
        wd = os.path.join(work, f"ring_h{h:.2f}"); os.makedirs(wd, exist_ok=True)
        write_inp(os.path.join(wd, "v.inp"), X, T, mat, {}, [dl], None, extra=bc)
        sec = run_ccx(wd, "v", threads); U, S = read_frd(os.path.join(wd, "v.frd"), len(X))[0]
        inner = np.abs(r_ - ri) < 1e-3; outer = np.abs(r_ - ro) < 1e-3
        st_an = p * (ro ** 2 + ri ** 2) / (ro ** 2 - ri ** 2); vm_an = math.sqrt(st_an ** 2 + p ** 2 + st_an * p)
        ur_an = ri / E * (st_an + nu * p); ur_o_an = ro / E * (2 * p * ri ** 2 / (ro ** 2 - ri ** 2))
        ur = np.einsum("ij,ij->i", U[inner][:, :2], X[inner][:, :2] / ri); ur_o = np.einsum("ij,ij->i", U[outer][:, :2], X[outer][:, :2] / ro)
        for case, fe, an in (("ring 100 MPa: von Mises at the bore", float(np.mean(vm(S[inner]))), vm_an), ("ring: hoop stress at the outer wall", float(np.mean(
                [np.array([-y, x, 0]) @ np.array([[s[0], s[3], s[5]], [s[3], s[1], s[4]], [s[5], s[4], s[2]]]) @ np.array([-y, x, 0]) / ro ** 2 for (x, y, _), s in zip(X[outer], S[outer])])), 2 * p * ri ** 2 / (ro ** 2 - ri ** 2)),
                             ("ring: radial displacement at the bore (mm)", float(np.mean(ur)), ur_an), ("ring: radial displacement outside (mm)", float(np.mean(ur_o)), ur_o_an)):
            rows.append(dict(case=case, h=round(h, 3), nodes=len(X), fe=round(fe, 6), analytic=round(an, 6), err=round(fe / an - 1, 4), ccx_s=round(sec, 1)))
    ok = all(abs(r["err"]) <= 0.03 for r in rows if r["h"] in (round(1.0, 3), round((ro - ri) / 3, 3)))
    out = dict(version=VERSION, rows=rows, finer_mesh_all_within_3pct=ok)
    json.dump(out, open(os.path.join(REPO, "judge", "fea_validation.json"), "w"), indent=1)
    for r in rows: print(f"  {r['case']:<62} h {r['h']:<6} FE {r['fe']:<12} analytic {r['analytic']:<12} err {100 * r['err']:+.2f} %")
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("design", nargs="?"); ap.add_argument("--parts", default=""); ap.add_argument("--fast", action="store_true")
    ap.add_argument("--validate", action="store_true"); ap.add_argument("--threads", type=int, default=int(os.environ.get("OMP_NUM_THREADS", 2)))
    A = ap.parse_args()
    if A.validate: validate(A.threads); sys.exit(0)
    dd = design_dir(A.design); out = judge_design(dd, [p for p in A.parts.split(",") if p] or None, A.fast, A.threads)
    os.makedirs(os.path.join(dd, "judge"), exist_ok=True); fn = os.path.join(dd, "judge", "fea.json")
    if A.parts and os.path.exists(fn):                                                     # partial re-run: merge into the existing result
        old = json.load(open(fn)); old["parts"].update(out["parts"]); out["parts"] = old["parts"]
    summarise(out, dd); json.dump(out, open(fn, "w"), indent=1)
    S_ = out["summary"]
    for k, p in out["parts"].items():
        c = p["cases"]; print(f"{k:7s} {p['material']:10s} D1 {c['D1']['vm_MPa']:7.1f} MPa  D1F {c['D1F']['vm_MPa']:7.1f} MPa SF {c['D1F']['SF']:5.2f}  fatigue SF {p['fatigue']['SF_fully_reversed']:5.2f}  d_GH {p['deflection']['d_GH_mm']:.3f} mm")
    print(f"R9: min SF {S_['min_SF']} ({S_['worst_part']}), fatigue {S_['fatigue_min_SF']}, chain d_GH {S_['chain_d_GH_mm']} mm vs gap {S_['min_skin_gap_mm']} -> {'PASS' if S_['passes'] else 'FAIL'}")
