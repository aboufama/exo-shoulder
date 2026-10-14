"""per followed frame: worst radial interpenetration between any two members (provisional fair fields incl. stack heights)
per-location order = whichever is higher there (mid-surface); shared-joint stack zones exempt"""
import sys, math, numpy as np, json
KEY = sys.argv[1]; sys.argv = ["x", KEY, "members"]; sys.path.insert(0, ".")
import fair_build as FB, envelope as EV, members as MB
E = EV.Envelope(FB.CAD_DIR); frames = [G for _, G in E.frames]; pidx = [p for p, _ in E.frames]
mem = FB.make_members(); off = np.r_[0, np.cumsum(FB.R["sizes"])]; h = np.array(FB.R["h"]); kd = np.array(FB.R["kind"])
for n, m in mem.items():
    m.grid(); m.env = E.min_radius(n, m.D.reshape(-1, 3)).reshape(m.D.shape[:-1]); mi = 0 if n == "base" else int(n[1:])
    m.fields(m.env, baseline=MB.band_baseline(m, FB.R["dirs_local"][mi], h[off[mi]:off[mi + 1]], kd[off[mi]:off[mi + 1]]))
    # stack tops (cap crowns) as part of the member that is lower at each joint: a disc of radius 10 at lv top
    m.sub = np.s_[::4, ::4]
names = list(mem); worst = np.zeros(len(frames)); pairs = {}
for i, a in enumerate(names):
    for b in names[i + 1:]:
        A_, B_ = mem[a], mem[b]; core = FB.shared_core(A_, B_) if FB.adjacent(A_, B_) else np.zeros(A_.D.shape[:-1], bool)
        D = A_.D[A_.sub].reshape(-1, 3); ins = (A_.sdf2(A_.X, A_.Y)[A_.sub] <= 0).ravel() & ~core[A_.sub].ravel()
        Abot, Atop = A_.bot[A_.sub].ravel(), A_.top[A_.sub].ravel(); pw = np.zeros(len(frames))
        for f, G in enumerate(frames):
            Db = D @ (G[b].T @ G[a]).T; bb, bt = B_.bot_at(Db), B_.top_at(Db); m = ins & np.isfinite(bb)
            if not m.any(): continue
            amid, bmid = 0.5 * (Abot[m] + Atop[m]), 0.5 * (bb[m] + bt[m])
            pen = np.where(amid > bmid, bt[m] + MB.CLEAR_MM - Abot[m], Atop[m] + MB.CLEAR_MM - bb[m])
            pw[f] = max(0.0, float(pen.max()))
        pairs[(a, b)] = pw; worst = np.maximum(worst, pw)
for k, v in pairs.items():
    if v.max() > 0: print(f"{k}: frames with overlap >0.5 mm {100 * np.mean(v > 0.5):.1f}%, >2 mm {100 * np.mean(v > 2):.1f}%, worst {v.max():.1f} mm")
print(f"ANY pair: frames with overlap > 0.5 mm: {100 * np.mean(worst > 0.5):.1f}%  > 2 mm: {100 * np.mean(worst > 2):.1f}%  (of {len(frames)} followed frames)")
np.save(f"out_{KEY}/overlap_frames.npy", np.c_[pidx, worst])
