"""links vs arm-end parts (merged BOTTOM/neck/track in H, carriage + wheels in 'cuff') over every followed frame.
Arm-end parts become radial interval maps (0.25 deg bins: min/max radius from GH along each ray) in their own frames."""
import sys, pickle, json, numpy as np, math, trimesh
from scipy.interpolate import RectBivariateSpline
KEY = sys.argv[1]; sys.argv = ["x", KEY, "none"]; sys.path.insert(0, ".")
import fair_build as FB, envelope as EV, members as MB
P = pickle.load(open(f"out_{KEY}/fields.pkl", "rb")); FB.FACES.update(P["FACES"])
E = EV.Envelope(FB.CAD_DIR); mem = FB.make_members()
for n, m in mem.items():
    d = P["mem"][n]; m.xs, m.ys = d["xs"], d["ys"]; m.X, m.Y = np.meshgrid(m.xs, m.ys, indexing="ij"); m.D = m.chart.dirs(m.X, m.Y)
    m.bot, m.top, m.top_hw = d["bot"], d["top"], d["top_hw"]
HR = np.array(json.load(open("../../avg/body_mesh.json"))["landmarks"]["rest_humerus"]); U_, _, Vt_ = np.linalg.svd(HR); HR = U_ @ Vt_
sc = trimesh.load(f"out_{KEY}/exo.glb"); RES = 0.25 * math.pi / 180
class Radial:
    def __init__(self, mesh):
        p, _ = trimesh.sample.sample_surface(mesh, 400000, seed=2); p = np.r_[p, mesh.vertices]
        r = np.linalg.norm(p, axis=1); d = p / r[:, None]; i, j = self.bins(d)
        key = i * 100000 + j; o = np.argsort(key); key, r = key[o], r[o]; u, s = np.unique(key, return_index=True)
        self.k = u; self.rmin = np.minimum.reduceat(r, s); self.rmax = np.maximum.reduceat(r, s)
    def bins(self, d): return np.floor((np.arcsin(np.clip(d[..., 1], -1, 1)) + math.pi / 2) / RES).astype(np.int64), np.floor((np.arctan2(d[..., 2], d[..., 0]) + math.pi) / RES).astype(np.int64)
    def look(self, d):
        i, j = self.bins(d); key = i * 100000 + j; pos = np.searchsorted(self.k, key); pos = np.clip(pos, 0, len(self.k) - 1); hit = self.k[pos] == key
        return np.where(hit, self.rmin[pos], np.nan), np.where(hit, self.rmax[pos], np.nan)
parts = {}
for node in sc.graph.nodes_geometry:
    g = node.split("|")[0]; nm = node.split("|")[1]
    if g == "cuff" or (g == "H" and (nm.startswith("BOTTOM +") or nm.startswith("J"))):
        T_, gn = sc.graph[node]; mm = sc.geometry[gn].copy(); mm.apply_transform(T_)
        if g == "H": mm.vertices = mm.vertices @ HR                                   # rest -> canonical (x_can = HR^T x_rest)
        key = "track" if g == "H" else ("carriage" if nm.startswith(("D4-C", "D4-S")) else ("wheels" if ("wheel" in nm.lower() or "bearing" in nm.lower() or "spacer" in nm.lower() or "bushing" in nm.lower() or "pin" in nm.lower() and "stop" not in nm.lower()) else "J4 hw"))
        parts.setdefault((key, "can" if g == "H" else "cuff"), []).append(mm)
rad = {k: Radial(trimesh.util.concatenate(v)) for k, v in parts.items()}
print("arm-end radial maps:", list(rad))
frames = E.frames; tot_bad = np.zeros(len(frames), bool)
for n, m in mem.items():
    sl = np.s_[::2, ::2]; ins = (m.sdf2(m.X, m.Y)[sl] <= 0).ravel(); D = m.D[sl].reshape(-1, 3)[ins]
    ab, at = m.bot[sl].ravel()[ins], m.top_hw[sl].ravel()[ins]
    jn = [h for h in m.hubs if h["joint"] == FB.N]                                           # link N-1's JN hub sits on the carriage
    core = np.zeros(len(D), bool)
    for h in jn:
        c = np.clip(D @ h["axis"], 1e-3, 1); core |= h["lv"]["S"] * np.sqrt(1 - c * c) / c <= MB.HUB_R + 15.0
    for (k, fr), R_ in rad.items():
        worst = np.zeros(len(frames))
        for f, (p, G) in enumerate(frames):
            W = D @ G[n].T
            Dl = W @ (E.RS[p] @ E.HG[p]) if fr == "can" else W @ G["cuff"]
            lo, hi = R_.look(Dl); mk = np.isfinite(lo)
            if k in ("carriage", "J4 hw") or (k == "track" and not FB.R.get("cuff")): mk &= ~core
            if not mk.any(): continue
            ov = np.minimum(at[mk], hi[mk]) - np.maximum(ab[mk], lo[mk]) + 0.6; worst[f] = max(0, float(ov.max()))
        bad = worst > 0.05; tot_bad |= bad
        if bad.any(): print(f"{n} x {k}: {bad.sum()} frames, worst {worst.max():.1f} mm")
print(f"frames with any link/arm-end collision: {tot_bad.sum()} of {len(frames)}")
