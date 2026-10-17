# auditor harness (2026-10-17), run from the repo root: OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/armband-pointer-audit-stops.py '{"cells":[[8,-45,280]]}'
"""stop-aware ring bound: a closed ring cannot vanish, so a pose where no ring fits is either CONTACT or excluded by a
joint stop. Stops are generous here: J1/J2 stops exclude any spherical CAP of arm directions (any axis, any half-angle:
the th window is a cap about a1 / -a1), and a twist window on the bench's axial angle (J3 stop proxy). Everything else
ideal (in-band 0.90, no hub / spar / link losses). gap = follow + reach losses + 100 * contact share of recorded poses."""
import json, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K

o = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
B = K.bench(o.get("nc", 60), o.get("nw", 160)); F = K.frames(B)
P = len(B.poses); kind = np.array(B.kind); clip = kind == "clip"; ws = kind == "ws"
ANG = np.arange(0, 360, 10.0); rmax = 120.0; R = np.arange(0, rmax + 1e-6, 2.0)
th = F.HG(K.wdir(0, 0)); axial = np.array([q["axial"] for q in B.poses])
# cap axes: Fibonacci sphere (thorax frame) 600 directions; half-angles 5..120
nA = 600; i = np.arange(nA) + 0.5; phi = np.arccos(1 - 2 * i / nA); tht = np.pi * (1 + 5 ** 0.5) * i
AX = np.stack([np.cos(tht) * np.sin(phi), np.sin(tht) * np.sin(phi), np.cos(phi)], -1)
COS = (th @ AX.T)                                            # (P, nA) cos angle between humerus axis and cap axis
HALF = np.arange(5, 125, 5.0)
TW = [(-999, 999)] + [(lo, hi) for lo in range(-120, 1, 15) for hi in range(30, 181, 15)]


def score(fit, excl):
    rec = ~excl; tk = fit & rec
    fo, re = tk[clip].mean(), tk[ws].mean(); con = ((~fit) & rec).sum() / max(rec.sum(), 1)
    return 100 * (max(0, .95 - fo) + max(0, .90 - re)) + 100 * con, fo, re, con


for (td, ta, s) in [tuple(c) for c in o.get("cells", [[8, -45, 280]])]:
    d3 = F.HG(K.wdir(td, ta)); E1 = F.HG(np.array([0, 0, 1.0])); E1 = K.unit(E1 - (E1 * d3).sum(-1, keepdims=True) * d3)
    E2 = np.cross(E1, d3); a = np.radians(ANG); U = np.cos(a)[None, :, None] * E1[:, None] + np.sin(a)[None, :, None] * E2[:, None]
    X = s * d3[:, None, None] + R[None, None, :, None] * U[:, :, None]
    D = K.dist_many(B, np.repeat(np.arange(P), X[0].size // 3), X.reshape(-1, 3)).reshape(P, len(ANG), len(R))
    lam = s / np.clip((th * d3).sum(-1), 1e-3, None); e = np.linalg.norm(lam[:, None] * th - s * d3, axis=-1)
    C = np.concatenate([np.zeros((P, len(ANG), 1)), np.cumsum(D < 0, -1)], -1); n = 5
    best = None; nostop = None
    for j in range(1, len(R) - n + 1):
        fit = ((C[..., j + n] - C[..., j]) == 0).all(1) & (e < R[j])
        if fit.mean() < 0.4: continue
        for (lo, hi) in TW:
            tw_ex = (axial < lo) | (axial > hi)
            for h in HALF:
                excl = (COS > np.cos(np.radians(h))) | tw_ex[:, None]          # (P, nA)
                rec = ~excl; tk = fit[:, None] & rec
                fo = tk[clip].mean(0); re = tk[ws].mean(0); con = ((~fit)[:, None] & rec).sum(0) / np.maximum(rec.sum(0), 1)
                g = 100 * (np.maximum(0, .95 - fo) + np.maximum(0, .90 - re)) + 100 * con; k = int(np.argmin(g))
                if best is None or g[k] < best[0]:
                    best = (round(float(g[k]), 1), float(R[j]), dict(cap_axis=[round(float(x), 2) for x in AX[k]], half=float(h), twist=(lo, hi)),
                            round(float(fo[k]), 3), round(float(re[k]), 3), round(float(con[k]), 3))
            # no stops at all (reference)
            g0 = score(fit, np.zeros(P, bool))
            if j and (nostop is None or g0[0] < nostop[0]): nostop = (round(g0[0], 1), float(R[j]))
    print(json.dumps(dict(cell=(td, ta, s), stop_bound=best[0], no_stop_bound=nostop, r_face=best[1], stops=best[2], follow=best[3], reach=best[4], contact=best[5])), flush=True)
