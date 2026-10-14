"""verify the BUILT member fields: per followed frame, radial interpenetration of every member pair (caps included),
coaxial plates at a shared joint must keep >= 0 gap, everything else >= CLEAR (0.6 mm). Prints per-pair stats."""
import sys, pickle, numpy as np, math
from scipy.interpolate import RectBivariateSpline
KEY = sys.argv[1]; sys.argv = ["x", KEY, "members"]; sys.path.insert(0, ".")
import fair_build as FB, envelope as EV, members as MB
P = pickle.load(open(f"out_{KEY}/fields.pkl", "rb")); FB.FACES.update(P["FACES"])
E = EV.Envelope(FB.CAD_DIR); frames = [G for _, G in E.frames]; mem = FB.make_members()
for n, m in mem.items():
    d = P["mem"][n]; m.grid(); m.xs, m.ys = d["xs"], d["ys"]; m.X, m.Y = np.meshgrid(m.xs, m.ys, indexing="ij"); m.D = m.chart.dirs(m.X, m.Y)
    m.bot, m.top, m.top_hw = d["bot"], d["top"], d["top_hw"]
    m.fb = RectBivariateSpline(m.xs, m.ys, m.bot, kx=3, ky=3, s=0); m.ft = RectBivariateSpline(m.xs, m.ys, m.top, kx=3, ky=3, s=0); m.fh = RectBivariateSpline(m.xs, m.ys, m.top_hw, kx=1, ky=1, s=0)
names = list(mem); bad_frames = np.zeros(len(frames), bool); rep = []
for i, a in enumerate(names):
    for b in names[i + 1:]:
        A_, B_ = mem[a], mem[b]; sl = np.s_[::2, ::2]; ins = (A_.sdf2(A_.X, A_.Y)[sl] <= 0).ravel(); D = A_.D[sl].reshape(-1, 3)[ins]
        ab, at = A_.bot[sl].ravel()[ins], A_.top_hw[sl].ravel()[ins]
        near = np.zeros(len(D), bool); core = np.zeros(len(D), bool)
        for ha in A_.hubs:
            for hb in B_.hubs:
                if ha["joint"] == hb["joint"]:
                    c = np.clip(D @ ha["axis"], 1e-3, 1); r_ = ha["lv"]["S"] * np.sqrt(1 - c * c) / c; near = r_ <= MB.HUB_R + 15; core = r_ <= MB.HUB_R + 1
        need = np.where(near, -0.02, MB.CLEAR_MM); worst = np.zeros(len(frames))
        for f, G in enumerate(frames):
            Db = D @ (G[b].T @ G[a]).T; bb = B_.bot_at(Db); m_ = np.isfinite(bb) & ~core
            if not m_.any(): continue
            bt = B_.top_hw_at(Db[m_]); ov = np.minimum(at[m_], bt) - np.maximum(ab[m_], bb[m_]) + need[m_]
            worst[f] = max(0.0, float(ov.max()))
        bad = worst > 0.05; bad_frames |= bad
        if bad.any(): rep.append(f"{a} x {b}: {bad.sum()} frames, worst {worst.max():.2f} mm")
print("\n".join(rep) if rep else "no member interpenetration in any followed frame")
print(f"frames with any member collision: {bad_frames.sum()} of {len(frames)}")
import json, os
bad_p = [int(p) for (p, _), b_ in zip(E.frames, bad_frames) if b_]
ch = f"out_{KEY}/chosen.json"; exc = f"out_{KEY}/exclude.json"
if os.path.exists(ch) and bad_p:
    cmap = {}
    for p, c in json.load(open(ch)): cmap.setdefault(p, c)
    old = json.load(open(exc)) if os.path.exists(exc) else []
    new = sorted({tuple(x) for x in old} | {(p, cmap[p]) for p in bad_p if p in cmap})
    json.dump([list(x) for x in new], open(exc, "w")); print(f"exclude list now {len(new)} states")
