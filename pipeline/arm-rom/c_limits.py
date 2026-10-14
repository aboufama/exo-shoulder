"""Family C (pivot-pivot 3R) re-scored with the same physical limits as d_limits.py: J1 and the upper-arm post J3
each limited to a 180 deg window (centres optimised)."""
import json, math
import numpy as np
import design_search as D
import design_search_families as F
from design_search_pivots import H_FRAMES, w_dir


def score(design):
    b = np.asarray(design["b"], float); a1, a2 = design["a1"] * D.D2R, design["a2"] * D.D2R
    u3 = H_FRAMES @ w_dir(design["delta"], design["waz"]); h = D.HG
    B = np.broadcast_to(b, u3.shape)
    c, ok = F.circ_int(B, a1, u3, a2, design["branch"])
    ok &= F.triangle_ok(B, u3, a1, a2)
    ok &= np.abs((B * u3).sum(-1)) <= math.cos(F.SING)
    pts = np.concatenate([D.slerp_pts(B, c, 7), D.slerp_pts(c, u3, 7)], axis=-2)
    ok &= F.off_body_and_arm(pts, h)
    e = np.cross(b, [0.0, 1.0, 0.0]); e /= np.linalg.norm(e); f = np.cross(b, e)
    q1 = np.degrees(np.arctan2(c @ f, c @ e))
    tl = c - (c * u3).sum(-1, keepdims=True) * u3; tl /= np.linalg.norm(tl, axis=-1, keepdims=True) + 1e-12
    th = h - (h * u3).sum(-1, keepdims=True) * u3; th /= np.linalg.norm(th, axis=-1, keepdims=True) + 1e-12
    post = np.degrees(np.arctan2((np.cross(tl, th) * u3).sum(-1), (tl * th).sum(-1)))
    best = (0, 0, 0)
    for cq in range(-180, 180, 10):
        inq = np.abs((q1 - cq + 180) % 360 - 180) <= 90
        for cp in range(-180, 180, 10):
            cov = float((ok & inq & (np.abs((post - cp + 180) % 360 - 180) <= 90)).mean())
            if cov > best[0]: best = (cov, cq, cp)
    return dict(design, cov_unlimited=float(ok.mean()), cov_limited=best[0], q1_centre=best[1], post_centre=best[2])


if __name__ == "__main__":
    top = json.load(open("design_search_pivots.json"))[:60]
    out = sorted((score(r) for r in top), key=lambda r: -r["cov_limited"])
    for r in out[:6]:
        print(f"limited {100*r['cov_limited']:5.1f}%  unlimited {100*r['cov_unlimited']:5.1f}%  az {r['az']} el {r['el']} arcs {r['a1']}/{r['a2']} delta {r['delta']} waz {r['waz']} br {r['branch']} q1c {r['q1_centre']} postc {r['post_centre']}")
    json.dump(out, open("design_search_C_limited.json", "w"))
