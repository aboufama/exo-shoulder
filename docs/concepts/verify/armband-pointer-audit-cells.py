# auditor harness (2026-10-17), run from the repo root: OMP_NUM_THREADS=1 nice -n 10 python3 docs/concepts/verify/armband-pointer-audit-cells.py '{"cells":[[8,-45,280],[8,-45,220]]}'
"""audit of armband-pointer's ring bound: reproduce ring_bound2's fixed-bore cell, then (a) the contact-aware bound
(no stops: a closed ring cannot vanish, so every pose where it does not fit is a CONTACT pose - the bench counts those
as not taken AND as contact), (b) the circular ring face's own in-band share at that ring over the fit clip poses,
(c) extra cells the claim did not cover (s 200-220 tilted)."""
import json, os, sys
import numpy as np
REPO = "/home/user/exo-shoulder"; sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_kit as K

o = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
B = K.bench(o.get("nc", 60), o.get("nw", 160)); F = K.frames(B)
P = len(B.poses); kind = np.array(B.kind); ANG = np.arange(0, 360, 10.0); rmax = 120.0; R = np.arange(0, rmax + 1e-6, 2.0)
th = F.HG(K.wdir(0, 0)); NC, NW = (kind == "clip").sum(), (kind == "ws").sum()
cells = [tuple(c) for c in o.get("cells", [[8, -45, 280], [0, 0, 260], [0, 0, 280], [8, 0, 280], [8, -45, 240]])]
for (td, ta, s) in cells:
    d3 = F.HG(K.wdir(td, ta)); E1 = F.HG(np.array([0, 0, 1.0])); E1 = K.unit(E1 - (E1 * d3).sum(-1, keepdims=True) * d3)
    E2 = np.cross(E1, d3); a = np.radians(ANG); U = np.cos(a)[None, :, None] * E1[:, None] + np.sin(a)[None, :, None] * E2[:, None]
    X = s * d3[:, None, None] + R[None, None, :, None] * U[:, :, None]
    D = K.dist_many(B, np.repeat(np.arange(P), X[0].size // 3), X.reshape(-1, 3)).reshape(P, len(ANG), len(R))
    lam = s / np.clip((th * d3).sum(-1), 1e-3, None); e = np.linalg.norm(lam[:, None] * th - s * d3, axis=-1)
    C = np.concatenate([np.zeros((P, len(ANG), 1)), np.cumsum(D < 0, -1)], -1)
    sec = 8.0; n = int(round(sec / 2.0)) + 1
    best_ns = best_ps = None
    for j in range(1, len(R) - n + 1):
        free = ((C[..., j + n] - C[..., j]) == 0).all(1) & (e < R[j])
        fo, re = free[kind == "clip"].mean(), free[kind == "ws"].mean()
        g_ps = 100 * (max(0, .95 - fo) + max(0, .90 - re))                    # claim's bound (perfect stops, in-band 0.9)
        g_ns = g_ps + 100 * (1 - free.mean())                                 # no stops: every non-fit pose is contact
        # the circular ring face (skin face at R[j]) in-band over the fit clip poses: D at R[j] on every ray
        fc = free & (kind == "clip"); dface = D[fc][:, :, j]
        ib = float(((dface >= 2) & (dface <= 14)).mean()) if fc.any() else 0.0
        if best_ps is None or g_ps < best_ps[0]: best_ps = (round(g_ps, 1), float(R[j]), round(fo, 3), round(re, 3), round(ib, 3))
        if best_ns is None or g_ns < best_ns[0]: best_ns = (round(g_ns, 1), float(R[j]), round(fo, 3), round(re, 3), round(ib, 3), round(1 - free.mean(), 3))
    print(json.dumps(dict(cell=(td, ta, s), perfect_stops=dict(zip(("gap_lb", "r_face", "follow_ub", "reach_ub", "ring_face_ib14"), best_ps)),
                          no_stops=dict(zip(("gap_lb", "r_face", "follow_ub", "reach_ub", "ring_face_ib14", "contact_lb"), best_ns)))), flush=True)
