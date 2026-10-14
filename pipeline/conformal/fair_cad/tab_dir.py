import sys, numpy as np, math
KEY = sys.argv[1]; sys.argv = ["x", KEY, "members"]; sys.path.insert(0, ".")
import fair_build as FB, envelope as EV, members as MB
E = EV.Envelope(FB.CAD_DIR); frames = [G for _, G in E.frames]; R = FB.R
off = np.r_[0, np.cumsum(R["sizes"])]; hh = np.array(R["h"]); kd = np.array(R["kind"])
mem = FB.make_members()
for n, m in mem.items():
    if n == "base": continue
    m.grid(); m.env = E.min_radius(n, m.D.reshape(-1, 3)).reshape(m.D.shape[:-1]); mi = int(n[1:])
    m.fields(m.env, baseline=MB.band_baseline(m, R["dirs_local"][mi], hh[off[mi]:off[mi + 1]], kd[off[mi]:off[mi + 1]]))
b0 = mem["base"]; a = b0.hubs[0]["axis"]; e1 = np.array([0, -1.0, 0]); e2 = np.cross(a, e1)
for beta in range(0, 360, 30):
    u = math.cos(math.radians(beta)) * e1 + math.sin(math.radians(beta)) * e2
    B = MB.Member("base", "base", b0.hubs, strip_dir=u, strip_len=FB.MOUNT_LEN, R0=b0.R0, flat=True); B.grid()
    B.env = E.min_radius("base", B.D.reshape(-1, 3)).reshape(B.D.shape[:-1]); B.fields(B.env)
    row = []
    for n in ("l1", "l2", "l3"):
        core = FB.shared_core(B, mem[n]) if FB.adjacent(B, mem[n]) else None
        Lb, sb, _ = MB.pair_lift(B, mem[n], frames, core)               # base over n
        Ln, sn, _ = MB.pair_lift(mem[n], B, frames, FB.shared_core(mem[n], B) if core is not None else None)  # n over base
        row.append(f"{n}: base-over {Lb:4.1f} ({100 * sb:3.0f}%) / {n}-over {Ln:4.1f} ({100 * sn:3.0f}%)")
    d = frames[0]["base"] @ u
    print(f"beta {beta:3d} tab (ant, up, lat) {np.round(d, 2)}  " + "  ".join(row), flush=True)
print("--- where (beta 0)")
u = e1; B = MB.Member("base", "base", b0.hubs, strip_dir=u, strip_len=FB.MOUNT_LEN, R0=b0.R0, flat=True); B.grid(); B.env = E.min_radius("base", B.D.reshape(-1, 3)).reshape(B.D.shape[:-1]); B.fields(B.env)
for n in ("l1", "l2"):
    A_ = mem[n]; core = FB.shared_core(A_, B) if FB.adjacent(A_, B) else None
    L, s, c = MB.pair_lift(A_, B, frames, core); ins = A_.sdf2(A_.X, A_.Y) <= 0; v = np.where(ins & np.isfinite(c), c - A_.bot, -np.inf)
    i, j = np.unravel_index(np.argmax(v), v.shape); d = A_.D[i, j]
    rs = [round(float(h_["lv"]["S"] * math.tan(math.acos(np.clip(d @ h_["axis"], -1, 1)))), 1) for h_ in A_.hubs]
    # which frame / where on the base
    best = None
    for f, G in enumerate(frames):
        Db = (G["base"].T @ G[n]) @ d; t = B.top_hw_at(Db[None])[0]
        if np.isfinite(t) and (best is None or t > best[0]): best = (t, f, Db)
    rb = float(B.hubs[0]["lv"]["S"] * math.tan(math.acos(np.clip(best[2] @ B.hubs[0]["axis"], -1, 1))))
    print(f"{n} over base: lift {v.max():.1f} at {n} r-from-hubs {rs}; {n} bot {A_.bot[i, j]:.1f} top {A_.top[i, j]:.1f}; base top {best[0]:.1f} (frame {best[1]}), at base r {rb:.1f} from J1; base bot there {B.bot_at(best[2][None])[0]:.1f}")
