"""where can the scapula base's mount arm go? occupancy of every link over the arm footprint, per arm direction about J1"""
import sys, math, numpy as np
KEY = sys.argv[1]; sys.argv = ["x", KEY, "members"]; sys.path.insert(0, ".")
import fair_build as FB, envelope as EV, members as MB
E = EV.Envelope(FB.CAD_DIR); frames = [G for _, G in E.frames]; mem = FB.make_members()
base = mem["base"]; a = base.hubs[0]["axis"]; S = base.hubs[0]["lv"]["S"]
e1 = np.array([0, -1.0, 0]); e2 = np.cross(a, e1)
print(KEY, "J1 role of base:", base.hubs[0]["role"])
for beta in range(0, 360, 20):
    b = math.radians(beta); u = math.cos(b) * e1 + math.sin(b) * e2
    pts = []
    for r in np.linspace(MB.HUB_R + 2, MB.HUB_R + FB.MOUNT_LEN, 7):
        for w in (-6, 0, 6):
            p = a * S + u * r + np.cross(a, u) * w; pts.append(p / np.linalg.norm(p))
    P = np.array(pts); occ = {}
    for n in [k for k in mem if k != "base"]:
        m = mem[n]; hit = 0
        for G in frames:
            Dl = P @ (G[n].T @ G["base"]).T; xy = m.chart.xy(Dl); hit += bool((m.sdf2(xy[:, 0], xy[:, 1]) <= 0).any())
        occ[n] = round(100 * hit / len(frames), 1)
    Rs0 = frames[0]["base"]; wd = Rs0 @ u
    print(f"beta {beta:3d}  arm dir (thorax ant, up, lat at frame 0) {np.round(wd, 2)}  occupied by: {occ}")
