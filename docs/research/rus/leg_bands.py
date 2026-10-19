"""fold band of one RUS leg closed by the user's GH (bench: GH fixed in S, triangle GH-T-Q rigid): for crank seat c
(S-frame bvec) and arm stud q (H frame: s mm down the humerus, theta deg about it, + posterior, ball ~61 mm off the
axis), the smallest crank arc beta (with the best rod angle gamma) whose band [|beta - gamma| + 10, min(beta + gamma,
360 - beta - gamma) - 10] holds >= 98 % of the workspace and every clip frame of Bench(60,160)."""
import sys, math, json, numpy as np, importlib.util
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, REPO + "/tools")
spec = importlib.util.spec_from_file_location("hccr", REPO + "/docs/concepts/models/human-closed-crank-rods.py")
H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)
B = H.CB.Bench(60, 160)
RS = np.stack([B.frames(i)["S"][0] for i in range(len(B.poses))]); RH = np.stack([B.frames(i)["H"][0] for i in range(len(B.poses))])
ws = np.array([k == "ws" for k in B.kind])
out = []
for az, el in [(-30, 8), (-24, 4), (-36, 16), (-30, 12), (-24, 78), (84, 82), (60, 75), (-10, 40)]:
    c = np.einsum("nij,j->ni", RS, H.bvec(az, el))
    for s in (0, 10, 20, 30, 45):
        for th in (30, 60, 75, 90, 105, 120, 150):
            t = math.radians(th); q = np.array([0, -s, 0]) + 61 * np.array([-math.sin(t), 0, math.cos(t)])
            Q = np.einsum("nij,j->ni", RH, q / np.linalg.norm(q))
            a = np.degrees(np.arccos(np.clip((c * Q).sum(1), -1, 1)))
            best = None
            for beta in range(30, 95, 5):
                g = np.arange(10, 175, 1.0); lo = np.abs(beta - g)[:, None] + 10; hi = np.minimum(beta + g, 360 - beta - g)[:, None] - 10
                cov_ws = ((a[ws][None] >= lo) & (a[ws][None] <= hi)).mean(1); cov_cl = ((a[~ws][None] >= lo) & (a[~ws][None] <= hi)).mean(1)
                j = int(np.argmax(cov_ws + cov_cl))
                if cov_ws[j] >= 0.98 and cov_cl[j] >= 0.999: best = (beta, float(g[j]), round(float(cov_ws[j]), 3)); break
            out.append(dict(seat=[az, el], s=s, th=th, rng=[round(float(a[ws].min()), 1), round(float(a[ws].max()), 1)], best=best))
json.dump(out, open(REPO + "/docs/research/rus/leg_bands.json", "w"), indent=1)
print(sum(1 for o in out if o["best"]), "of", len(out), "seat-stud pairs have a fold-free leg with beta <= 90")
