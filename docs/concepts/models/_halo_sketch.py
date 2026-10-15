"""Sketch of the best scapula-halo-track configuration (docs/concepts/img/scapula-halo-track.png): the posed skin near
the shoulder (grey points) and the metal (track, carriage, link 2, J3 disc + neck) at rest and overhead, two views."""
import importlib.util, json, os, sys
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
spec = importlib.util.spec_from_file_location("halo", os.path.join(HERE, "scapula-halo-track.py")); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
CB = M.CB


def main(params, out):
    B = CB.Bench(60, 160); ctx = M.Ctx(B); D = M.Design(params, ctx)
    want = [("rest", dict(plane=30, elev=10)), ("overhead", dict(plane=60, elev=150)), ("across", dict(plane=120, elev=90)), ("behind back", dict(plane=-60, elev=40))]
    picks = []
    for name, q in want:
        cand = [i for i in range(len(B.poses)) if isinstance(D.cand[i], list)]
        if not cand: continue
        i = min(cand, key=lambda j: (B.poses[j]["plane"] - q["plane"]) ** 2 / 4 + (B.poses[j]["elev"] - q["elev"]) ** 2)
        picks.append((name, i))
    cols = dict(track="#d9822b", carriage="#2b6cb0", link2="#2f855a", armend="#9b2c2c")
    fig, ax = plt.subplots(2, len(picks), figsize=(4.2 * len(picks), 8.4))
    for c, (name, i) in enumerate(picks):
        V, _ = B.skin(i); V = np.asarray(V); V = V[np.linalg.norm(V, axis=1) < 150]
        r = D.cand[i][0]; P = D.parts(i, r); RS = ctx.RS[i]
        for row, (view, lab) in enumerate([((0, 1), "front (x ant, y up)"), ((2, 1), "side (z lat, y up)")]):
            a = ax[row, c]; a.scatter(V[::3, view[0]], V[::3, view[1]], s=0.3, c="#bbbbbb")
            for k, m in P.items():
                X = m["face"] @ RS.T; a.scatter(X[:, view[0]], X[:, view[1]], s=1.2, c=cols[k], label=k if (row == 0 and c == 0) else None)
            a.set_aspect("equal"); a.set_xlim(-150, 150); a.set_ylim(-150, 150); a.set_title(f"{name} {lab}", fontsize=9)
            pz = B.poses[i]; a.text(-145, -145, f"plane {pz['plane']:.0f} elev {pz['elev']:.0f} axial {pz['axial']:.0f}", fontsize=7)
    ax[0, 0].legend(loc="upper left", fontsize=7, markerscale=6)
    fig.suptitle("scapula-halo-track, best bench configuration (metal skin-facing samples; grey = posed skin)", fontsize=10)
    fig.tight_layout(); fig.savefig(out, dpi=110); print("wrote", out)


if __name__ == "__main__":
    main(json.loads(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else os.path.join(REPO, "docs", "concepts", "img", "scapula-halo-track.png"))
