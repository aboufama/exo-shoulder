"""Re-score the current CAD scissor under the same rules as the morphology searches: base rides on the scapula
(design_search rhythm), BOTTOM's post limited to 180 deg (centre optimised, relative to the output links' midline),
and every scissor link kept off the head, neck, torso and the upper arm. Mount orientation as in the CAD (thorax
axes: Z up, +Y lateral, +X posterior), so this is directly comparable with design_search_*.

    python3 current_rescore.py
"""
import math

import numpy as np
import design_search as D
import rom as R

LINK_PINS = dict(O3=("p3", "p5"), I12=("p3", "p2"), IL25=("p5", "p6", "p4"), OL5=("p2", "p6", "p1"), O4=("p4", "p0"), I9=("p1", "p0"))
Mt = R.M                                                            # thorax axes in CAD


def rescore():
    res = []
    for (plane, elev, axial, Hg, Rs), hg in zip(D.POSES, D.HG):
        Hc = Mt @ Hg                                                 # GH-relative humerus in CAD axes (base on the scapula)
        RB = Hc @ R.H_CAD.T
        u0 = RB @ R.U0["p0"]
        th = math.degrees(math.acos(max(-1, min(1, u0[0]))))
        s = R.sigma_of(th)
        if s is None:
            res.append((False, None)); continue
        RI9, u0s = R.table_R(s, "I9")
        psi = math.atan2(u0[2], u0[1]) - math.atan2(u0s[2], u0s[1]); Rp = R.rot([1, 0, 0], psi)
        links = {k: Rp @ R.table_R(s, k)[0] for k in LINK_PINS}
        Rg = RB @ links["I9"].T
        g = math.degrees(math.atan2(np.dot(u0, [Rg[2, 1] - Rg[1, 2], Rg[0, 2] - Rg[2, 0], Rg[1, 0] - Rg[0, 1]]), np.trace(Rg) - 1))
        Rd = links["O4"] @ links["I9"].T
        dl = math.degrees(math.atan2(np.dot(u0, [Rd[2, 1] - Rd[1, 2], Rd[0, 2] - Rd[2, 0], Rd[1, 0] - Rd[0, 1]]), np.trace(Rd) - 1))
        # sampled links (CAD axes -> thorax axes -> body test with the scapula rotation)
        pts = []
        for k, pins in LINK_PINS.items():
            ps = [links[k] @ R.U0[p] for p in pins]
            for a, b in zip(ps, ps[1:]):
                pts += list(D.slerp_pts(a[None], b[None], 6)[0])
        P = np.array(pts) @ Mt                                       # CAD -> thorax (Mt orthonormal: v_thorax = Mt^T v_cad)
        clear = np.degrees(np.arccos(np.clip(P @ hg, -1, 1))).min() >= D.RHO_ARM
        clear &= not D.in_body((Rs @ (P * D.R_SHELL).T).T).any()
        res.append((clear, g - dl / 2))
    best = (0, 0)
    for c in range(-180, 180, 10):
        ok = [a and abs((g - c + 180) % 360 - 180) <= 90 for a, g in res if g is not None] + [False] * sum(1 for _, g in res if g is None)
        cov = sum(ok) / len(res)
        if cov > best[0]: best = (cov, c)
    free = sum(1 for a, g in res if a) / len(res)
    return best, free


if __name__ == "__main__":
    (cov, c), free = rescore()
    print(f"current CAD scissor, scapula-mounted, 180 deg post (centre {c}): {100 * cov:.1f}%   (post unlimited: {100 * free:.1f}%)")
