"""Why poses are lost, for the best anatomical design of each family (design_search_anat_*.json): first failing rule
per pose, in order kinematics -> trunk/girdle skin (by region) -> upper-arm skin -> post bearing in the deltoid -> post
travel. D uses its best spare-joint angle per pose (a pose is charged to the rule that blocks its least-bad angle)."""
import json, math, sys
import numpy as np
import design_search as D
import design_search_anat as A
import design_search_families as F
from design_search_pivots import w_dir

S = 411 / 310


def classify(pts, R, post, kin_ok, postang, pc):
    hf, rs, eb = A.HF_ALL, A.RS_ALL, A.EBIN_ALL
    N = pts.shape[0]; P = pts.reshape(N, -1, 3) * (R - 5.0)
    Pt = np.einsum("nij,nmj->nmi", rs, P); Ph = np.einsum("nji,nmj->nmi", hf, P)
    dt = np.empty(Pt.shape[:2])
    for b in np.unique(eb): sel = eb == b; dt[sel] = A.lookup(A.TRUNK[b], Pt[sel])
    da = A.lookup(A.ARM, Ph)
    near = np.degrees(np.arccos(np.clip(np.einsum("nmj,nj->nm", pts.reshape(N, -1, 3), post), -1, 1))) < A.POST_EXCL
    trunk_bad = dt < A.CLEAR; arm_bad = (da < A.CLEAR) & ~near
    dpa = A.lookup(A.ARM, np.einsum("nji,nj->ni", hf, post * R))
    out = np.full(N, "ok", dtype=object)
    inwin = np.abs((postang - pc + 180) % 360 - 180) <= 90
    for i in range(N):
        if not kin_ok[i]: out[i] = "kinematics (singular / out of reach / gimbal)"
        elif trunk_bad[i].any():
            y = Pt[i][trunk_bad[i]][:, 1].max(); x = Pt[i][trunk_bad[i]][:, 0].min()
            out[i] = "presses on trapezius / neck" if y > 55 * S else ("presses on scapula / back" if x < -40 * S else "presses on chest / front of shoulder")
        elif arm_bad[i].any(): out[i] = "presses on the upper arm (deltoid)"
        elif dpa[i] < A.POST_CLEAR: out[i] = "post bearing sits in the deltoid"
        elif not inwin[i]: out[i] = "post at the end of its 180 deg travel"
    return out


def run(fam, R):
    best = [r for r in json.load(open(f"design_search_anat_{fam}.json")) if r["R"] == R][0]
    hf, h = A.HF_ALL, A.HG_ALL
    if fam == "B":
        b = np.asarray(best["b"]); u = hf @ w_dir(best["delta"], best["waz"]); B = np.broadcast_to(b, u.shape)
        pts, kin = D.scissor(B, u, best["alpha"] * D.D2R); pa = A.about(B, h, u)
    elif fam == "C":
        b = np.asarray(best["b"]); u = hf @ w_dir(best["delta"], best["waz"]); B = np.broadcast_to(b, u.shape)
        c, kin = F.circ_int(B, best["a1"] * D.D2R, u, best["a2"] * D.D2R, best["branch"])
        kin &= F.triangle_ok(B, u, best["a1"] * D.D2R, best["a2"] * D.D2R) & (np.abs((B * u).sum(-1)) <= math.cos(A.SING))
        pts = np.concatenate([D.slerp_pts(B, c, 7), D.slerp_pts(c, u, 7)], axis=-2); pa = A.about(c, h, u)
    else:
        return None
    lab = classify(pts, R, u, kin, pa, best["post_centre"])
    vals, cnt = np.unique(lab, return_counts=True)
    return best, sorted(zip(cnt / len(lab), vals), reverse=True)


if __name__ == "__main__":
    for fam in sys.argv[1:]:
        for R in A.RADII:
            r = run(fam, R)
            if r: print(fam, R, f"{100 * r[0]['cov']:.1f}%", "  ".join(f"{v}: {100 * c:.0f}%" for c, v in r[1]))
