"""The swarm's reference: the current champion family - a pure spherical 3R chain (every joint axis through the GH
centre, 20 mm O20 hubs, 8 x 3 mm strap links) - as an idealised model on the common concept bench, so every new
morphology is compared with it on the same body, poses and metrics (tools/concept_bench.py).

Kinematics = the band evaluator's (pipeline/conformal/gpu/band_impl.py, Band.chain, N = 3, no cuff): base axis b(az, el)
fixed in the scapula frame, last axis HG W(w) fixed in the humerus, the middle axis from the two-circle closure on the
design's branch, J2 kept sing_deg away from the fold / stretch singularity; the scapula / humerus rotations RS, HG of
each bench pose come from the same pose file as the evaluator. Parameters default to the best judged 3R
(pipeline/conformal/band_cad/inputs/r20_n3_s1414_4.json).

Geometry (idealised, like every concept): a link is a strap on the great circle between its two joint axes, 8 mm wide;
its underside is sampled every ~2 mm along and across (~1 point / 4 mm2). A rigid link cannot follow the skin pose by
pose, so its radial profile r(s, c) (s along the arc, c across) is fixed in the link: the p-th percentile over the
kinematically valid poses of the outermost skin radius under that point, + 2 mm clearance. Hubs are 20 mm discs at
each joint axis at the same kind of radius; at each joint the distal link rides on top of the proximal one (+ stack +
link thickness = 6.15 mm). The arm-end part from J3 toward the humerus is a strap of arc `neck_deg` fixed to the
humerus. Poses where the skin rises above a link (p < 100) count as contact, as on the bench - the percentile trades
reach against closeness, as the evaluator's envelope does. The sweep over p picks the best gap.

    python3 tools/concept_baseline.py [--n-clip 60 --n-ws 160] [--write]   (--write: docs/concepts/families.json + rows/)
"""
import json, math, os, sys, time
import numpy as np
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import concept_bench as CB                                   # noqa: E402

D2R = math.pi / 180
CHAMP = dict(az=2.4305071427308924, el=80.67633718429899, a=[76.90180446920043, 66.74921235407174], w=[86.32769021001913, 21.829657347343378],
             branch=-1, hub_r=10.0, stack=3.15, t_link=3.0, sing_deg=10.0, width=8.0, clear=2.0, neck_deg=25.0)


def bvec(az, el):
    return np.array([-math.cos(el * D2R) * math.cos(az * D2R), math.sin(el * D2R), math.cos(el * D2R) * math.sin(az * D2R)])


def w_dir(delta, az):
    d, a = delta * D2R, az * D2R
    return np.array([math.sin(d) * math.sin(a), -math.cos(d), math.sin(d) * math.cos(a)])


def unit(x): return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def circ_int(c1, r1, c2, r2, sign):
    dd = np.clip((c1 * c2).sum(-1), -1, 1); n = unit(np.cross(c1, c2))
    den = 1 - dd ** 2 + 1e-12; a = (math.cos(r1) - dd * math.cos(r2)) / den; b = (math.cos(r2) - dd * math.cos(r1)) / den
    p = a[..., None] * c1 + b[..., None] * c2; h2 = 1 - (p * p).sum(-1)
    return p + sign * np.sqrt(np.clip(h2, 0, None))[..., None] * n, h2 > 0


def tri_ok(x, y, a, b, sing):
    th = np.arccos(np.clip((x * y).sum(-1), -1, 1))
    return (th >= abs(a - b) + sing) & (th <= min(a + b, 2 * math.pi - a - b) - sing)


def pins(d, HG, RS):
    """joint axes (P, 3, 3) in the thorax frame and kinematic validity (P,)"""
    A = [x * D2R for x in d["a"]]; b = bvec(d["az"], d["el"]); W0 = w_dir(*d["w"]); Pn = len(HG)
    p1 = np.broadcast_to(b, (Pn, 3)); p3 = HG @ W0
    p2, ok = circ_int(p1, A[0], p3, A[1], float(d["branch"]))
    ok &= tri_ok(p1, p3, A[0], A[1], d["sing_deg"] * D2R)
    P = np.stack([p1, p2, p3], 1)
    return np.einsum("pij,pkj->pki", RS, P), ok, np.einsum("pij,j->pi", RS @ HG, np.array([0.0, -1.0, 0.0]))


def arc_dirs(u, v, ang, ds_mm=2.0, width=8.0, r_ref=70.0):
    """unit directions sampling a strap on the great circle u -> v (P, 3) at arc angle ang (rad): (P, ns, nc, 3)"""
    ns = max(3, int(ang * r_ref / ds_mm) + 1); s = np.linspace(0, 1, ns)
    nrm = unit(np.cross(u, v))                               # great-circle normal
    e1 = u; e2 = unit(np.cross(nrm, u))
    th = s[None, :] * ang
    D = np.cos(th)[..., None] * e1[:, None] + np.sin(th)[..., None] * e2[:, None]          # (P, ns, 3)
    cs = np.arange(-width / 2, width / 2 + 1e-6, 2.0) / r_ref                                 # across, in rad
    return unit(D[:, :, None, :] * np.cos(cs)[None, None, :, None] + nrm[:, None, None, :] * np.sin(cs)[None, None, :, None])


def disc_dirs(u, rad_mm=10.0, r_ref=70.0, step=2.5):
    """unit directions under a hub disc centred on axis u (P, 3): (P, m, 3)"""
    g = np.arange(-rad_mm, rad_mm + 1e-6, step); X, Y = np.meshgrid(g, g); keep = X ** 2 + Y ** 2 <= rad_mm ** 2
    X, Y = X[keep] / r_ref, Y[keep] / r_ref
    a = unit(np.cross(u, np.array([0.0, 0.0, 1.0]) + 1e-3)); b = np.cross(u, a)
    return unit(u[:, None] + X[None, :, None] * a[:, None] + Y[None, :, None] * b[:, None])


def skin_radius(B, i, D, r_max=260.0):
    """outermost skin radius along unit directions D (k, 3) from the GH centre in pose i (sphere tracing inward)"""
    r = np.full(len(D), r_max); act = np.ones(len(D), bool); hit = np.zeros(len(D), bool)
    for _ in range(60):
        if not act.any(): break
        d = B.dist(i, D[act] * r[act, None]); a = np.nonzero(act)[0]
        done = d < 0.3; hit[a[done]] = True; act[a[done]] = False
        r[a[~done]] -= np.maximum(d[~done], 0.5)
        low = r < 15; act &= ~low
    return np.where(hit, r, 0.0)


def build(d=CHAMP, n_clip=60, n_ws=160, pcts=(60, 70, 80, 90, 95, 100), log=print):
    B = CB.Bench(n_clip, n_ws); Z = CB._poses_all(); HG = Z["HG"][B.idx].astype(float); RS = Z["RS"][B.idx].astype(float)
    t0 = time.time(); Pt, ok, harm = pins(d, HG, RS); A = [x * D2R for x in d["a"]]
    up = d["stack"] + d["t_link"]
    parts = {}                                                # name -> (dirs (P, m, 3), base offset mm)
    L1 = arc_dirs(Pt[:, 0], Pt[:, 1], A[0], width=d["width"]); L2 = arc_dirs(Pt[:, 1], Pt[:, 2], A[1], width=d["width"])
    ng = d["neck_deg"] * D2R; tgt = unit(Pt[:, 2] + 1e-9 * harm)
    nk_v = unit(np.cos(ng) * Pt[:, 2] + np.sin(ng) * unit(harm - (harm * Pt[:, 2]).sum(-1, keepdims=True) * Pt[:, 2]))
    NK = arc_dirs(Pt[:, 2], nk_v, ng, width=d["width"])
    for nm, Dd, off in (("link1", L1, 0.0), ("link2", L2, up), ("neck", NK, 2 * up)):
        parts[nm] = (Dd.reshape(len(Pt), -1, 3), off)
    for k, off in ((0, 0.0), (1, 0.0), (2, up)):
        parts[f"hub{k + 1}"] = (disc_dirs(Pt[:, k], d["hub_r"]), off)
    valid = np.nonzero(ok)[0]
    R = {nm: np.zeros(v[0].shape[:2]) for nm, v in parts.items()}
    for i in valid:                                           # outermost skin radius under every sample, every valid pose
        allD = np.concatenate([v[0][i] for v in parts.values()]); rr = skin_radius(B, int(i), allD); o = 0
        for nm, v in parts.items():
            m = v[0].shape[1]; R[nm][i] = rr[o:o + m]; o += m
    log(f"skin radii for {len(valid)} valid poses of {len(Pt)} in {time.time() - t0:.0f} s ({B.mode})")
    best = None; rows = []
    hub_of = {"link1": ("hub1", "hub2"), "link2": ("hub2", "hub3"), "neck": ("hub3", None)}
    for p in pcts:
        prof = {nm: np.percentile(R[nm][valid], p, axis=0) + d["clear"] for nm in parts}
        for nm in ("hub1", "hub2", "hub3"): prof[nm] = np.full_like(prof[nm], prof[nm].max())   # flat discs
        for nm, (h0, h1) in hub_of.items():                  # link ends sit on their hubs (distal link on top)
            n_s = (L1 if nm == "link1" else L2 if nm == "link2" else NK).shape[1]; nc = prof[nm].size // n_s
            pr = prof[nm].reshape(n_s, nc); end = max(2, n_s // 6)
            pr[:end] = np.maximum(pr[:end], prof[h0].max() + parts[nm][1] - parts[h0][1])
            if h1: pr[-end:] = np.maximum(pr[-end:], prof[h1].max() + parts[nm][1] - parts[h1][1])
            prof[nm] = pr.reshape(-1)
        B.reset()
        for i in range(len(Pt)):
            if not ok[i]: B.record(i, None); continue
            pts = np.concatenate([parts[nm][0][i] * (prof[nm] + parts[nm][1])[:, None] for nm in parts])
            B.record(i, pts)
        r = B.report(); r["pct"] = p; rows.append(r); log(f"  p{p}: {r}")
        if best is None or r["gap"] < best["gap"]: best = r
    return best, rows, B


if __name__ == "__main__":
    a = sys.argv[1:]
    nc = int(a[a.index("--n-clip") + 1]) if "--n-clip" in a else 60; nw = int(a[a.index("--n-ws") + 1]) if "--n-ws" in a else 160
    best, rows, B = build(n_clip=nc, n_ws=nw)
    print("BEST", best)
    if "--write" in a:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        row = dict(id="baseline-3r", name="Baseline: spherical 3R (r20 s1414 #4, O20 hubs, strap links)", lens="baseline", family="spherical 3R",
                   active_dof=3, passive_dof=0, status="screened", is_baseline=True, t_ideated=None, t_screened=now,
                   reach=best["reach"], follow=best["follow"], inband14=best["inband14"], inband10=best["inband10"], contact=best["contact"], gap=best["gap"],
                   v_reach=None, v_follow=None, v_inband14=None, v_inband10=None, v_gap=None, n_configs=len(rows),
                   verdict="the bar to beat", note=f"profile percentile p{best['pct']}; bench {B.mode}, {best['poses']}; real judged CAD of this design: R1 35.0 % (strap links), R3 98.2 %",
                   doc="tools/concept_baseline.py")
        os.makedirs(os.path.join(REPO, "docs", "concepts", "rows"), exist_ok=True)
        json.dump(row, open(os.path.join(REPO, "docs", "concepts", "rows", "baseline-3r.json"), "w"), indent=1)
        fj = os.path.join(REPO, "docs", "concepts", "families.json")
        fam = json.load(open(fj)) if os.path.exists(fj) else []
        fam = [r for r in fam if r.get("family") != "baseline spherical 3R"]
        fam.insert(0, dict(family="baseline spherical 3R", variant="r20 s1414 #4", active_dof=3, passive_dof=0, reach=best["reach"], follow=best["follow"],
                           inband14=best["inband14"], inband10=best["inband10"], contact=best["contact"], gap=best["gap"], verdict="baseline", notes=row["note"], is_baseline=True))
        json.dump(fam, open(fj, "w"), indent=1)
        print("wrote rows/baseline-3r.json and families.json")
