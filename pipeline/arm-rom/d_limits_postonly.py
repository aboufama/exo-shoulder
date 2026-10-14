"""Family D re-scored with physical joint limits: J1 (scapula pivot) and J4 (upper-arm post) each limited to a 180 deg
window (centres optimised), one J3 branch for the whole range. Coverage = fraction of poses reachable by some q1
inside the J1 window with the post inside its window and everything clear (as in design_search_families.eval_D)."""
import json, math, sys
import numpy as np
import design_search as D
import design_search_families as F
from design_search_pivots import H_FRAMES, w_dir

LIM = 181
QS = np.radians(np.arange(0, 360, 10))


LIM = 181
def score(design):
    b = np.asarray(design["b"], float); a1, a2, a3 = (design[k] * D.D2R for k in ("a1", "a2", "a3"))
    u4 = H_FRAMES @ w_dir(design["delta"], design["waz"]); h = D.HG; N = len(u4)
    e = np.cross(b, [0.0, 1.0, 0.0]); e /= np.linalg.norm(e); f = np.cross(b, e)
    c2 = math.cos(a1) * b + math.sin(a1) * (np.cos(QS)[:, None] * e + np.sin(QS)[:, None] * f)
    C2 = np.broadcast_to(c2[None], (N, len(QS), 3)); U4 = np.broadcast_to(u4[:, None], C2.shape)
    br = design["branch"]
    c3, ok = F.circ_int(C2, a2, U4, a3, br)
    ok &= F.triangle_ok(C2, U4, a2, a3)
    bb = np.broadcast_to(b, C2.shape)
    ok &= np.abs((bb * U4).sum(-1)) <= math.cos(F.SING)
    ok &= F.triangle_ok(bb, c3, a1, a2)
    pts = np.concatenate([D.slerp_pts(bb, C2, 7), D.slerp_pts(C2, c3, 7), D.slerp_pts(c3, U4, 7)], axis=-2)
    ok &= F.off_body_and_arm(pts, np.broadcast_to(h[:, None], C2.shape))
    # post angle at J4: link direction (to c3) vs the arm, about u4
    H = np.broadcast_to(h[:, None], C2.shape)
    tl = c3 - (c3 * U4).sum(-1, keepdims=True) * U4; tl /= np.linalg.norm(tl, axis=-1, keepdims=True) + 1e-12
    th = H - (H * U4).sum(-1, keepdims=True) * U4; th /= np.linalg.norm(th, axis=-1, keepdims=True) + 1e-12
    post = np.degrees(np.arctan2((np.cross(tl, th) * U4).sum(-1), (tl * th).sum(-1)))
    q = np.degrees(QS)[None, :]
    best = (0, 0, 0)
    for cq in range(0, 360, 20):
        inq = np.abs((q - cq + 180) % 360 - 180) <= LIM
        for cp in range(-180, 180, 20):
            inp = np.abs((post - cp + 180) % 360 - 180) <= 90
            cov = float((ok & inq & inp).any(1).mean())
            if cov > best[0]: best = (cov, cq, cp)
    return dict(design, cov_unlimited=float(ok.any(1).mean()), cov_limited=best[0], q1_centre=best[1], post_centre=best[2])


if __name__ == "__main__":
    top = json.load(open("design_search_D.json"))
    seen, out = set(), []
    for r in top:
        key = (r["el"], r["a1"], r["a2"], r["a3"], r["delta"], r["waz"], r["branch"])
        if key in seen and r["el"] == 85: continue
        seen.add(key); out.append(score(r))
    out.sort(key=lambda r: -r["cov_limited"])
    for r in out[:8]:
        print(f"limited {100*r['cov_limited']:5.1f}%  unlimited {100*r['cov_unlimited']:5.1f}%  az {r['az']} el {r['el']} arcs {r['a1']}/{r['a2']}/{r['a3']} delta {r['delta']} waz {r['waz']} br {r['branch']} q1c {r['q1_centre']} postc {r['post_centre']}")
    json.dump(out, open("design_search_D_postonly.json", "w"))
