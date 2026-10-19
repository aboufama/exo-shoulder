"""one-level band proximity for the rolling pairs of a knee-type cell on Bench(60,160) fast: each band (sun on the
proximal member, planet on the distal) sampled 2 mm along its used arc x 2 rows across the 2.5 mm wall, ONE underside
level R_lo per band (measure(): quantile 0.97 over taken poses, the rest are contact poses), metal points at R_lo; reports
in-band 14 / 10 (B.dist of the underside points in [2, 14] / [2, 10]), contact share, min metal-skin distance, R_lo,
and the same for an O20 cap disc (radius 10, one level) on the contact axis at rest as the control."""
import importlib.util, json, math, sys
import numpy as np
sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', '..', 'tools'))
spec = importlib.util.spec_from_file_location('rc', __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', '..', 'concepts', 'models', 'rolling-cone-3r.py'))
rc = importlib.util.module_from_spec(spec); spec.loader.exec_module(rc)
import concept_bench as CB, concept_kit as K
B = CB.Bench(60, 160); F = K.frames(B); Z = CB._poses_all(); HG = Z['HG'][B.idx].astype(float)
def band_dirs(axis, w, a_lo, a_hi, sgn, g, R=60.0, step=2.0):
    n = max(3, int(math.ceil(R * math.sin(math.radians(g)) * math.radians(a_hi - a_lo) / step)) + 1)
    ang = np.radians(np.linspace(a_lo, a_hi, n)) * sgn
    d = np.einsum('nij,j->ni', rc.rodr(axis, ang), w)                      # pitch-line directions
    rad = rc.unit(d - (d @ axis)[:, None] * axis)                            # outward from the cone axis
    rows = [rc.unit(d + (o / R) * rad) for o in (-0.6, 0.6)]
    return np.concatenate(rows)
def measure(B, I, Dw, label, q=0.97):
    """ONE level per part = quantile q over the taken poses of the per-pose max requirement of its samples (the kit's
    q rule: the worst poses become contact poses instead of lifting the part); in-band over the non-contact poses"""
    R = K.requirement(B, I.ravel(), Dw.reshape(-1, 3)).reshape(Dw.shape[:2])
    miss = ~np.isfinite(R) | (R > 215); Rp = np.where(miss, -1, R).max(1); lvl = float(np.quantile(Rp, q))
    P = lvl * Dw
    d = K.dist_many(B, I.ravel(), P.reshape(-1, 3)).reshape(Dw.shape[:2]); cp = (d < 0).any(1); dn = d[~cp]
    return dict(member=label, R_lo=round(lvl, 1), off_body_rays=round(float(miss.mean()), 4), contact_poses=int(cp.sum()), n_poses=len(cp),
                inband14=round(float(((dn >= 2) & (dn <= 14)).mean()), 3), inband10=round(float(((dn >= 2) & (dn <= 10)).mean()), 3),
                min_mm=round(float(dn.min()), 2), p95_mm=round(float(np.percentile(dn, 95)), 1), n_samples=Dw.shape[1])


if __name__ == '__main__':
    cell = json.loads(sys.argv[1]); G = rc.Ghost(cell); ok, t, m, th = G.take(HG)
    Pi = np.nonzero(ok)[0]; RS = F.RS[Pi]; out = []
    cum = [np.broadcast_to(np.eye(3), (len(Pi), 3, 3))]
    for k, j in enumerate(G.j): cum.append(cum[-1] @ j.T(t[Pi, k]))
    frames_prox = cum[:-1]; frames_dist = cum[1:]
    for k, j in enumerate(G.j):
        Rp = RS @ frames_prox[k]; Rd = RS @ frames_dist[k]
        I = np.repeat(Pi[:, None], 1, 1)
        if j.kind == 'roll':
            x = t[Pi, k] / (1 + j.r); y = t[Pi, k] * j.r / (1 + j.r)
            Ds = band_dirs(j.c, j.w, math.degrees(x.min()), math.degrees(x.max()), 1, j.ga)       # sun: contact R(c, x) w
            Dp = band_dirs(j.m0, j.w, math.degrees(-y.max()), math.degrees(-y.min()), 1, j.gb)   # planet: contact R(m0, -y) w
            for D, Rm, lab in ((Ds, Rp, f'J{k+1} sun band (proximal)'), (Dp, Rd, f'J{k+1} planet band (distal)')):
                Dw = np.einsum('pij,nj->pni', Rm, D); out.append(measure(B, np.repeat(Pi[:, None], Dw.shape[1], 1), Dw, lab))
        # O20 cap disc control on the rest contact axis, fixed in the proximal member (the hub's lower member face)
        Dc = K.cap_dirs(np.broadcast_to(j.w, (1, 3)), rad=10.0, step=2.0)[0]
        Dw = np.einsum('pij,nj->pni', Rp, Dc); r = measure(B, np.repeat(Pi[:, None], Dw.shape[1], 1), Dw, f'J{k+1} O20 disc control (one level)')
        out.append(r)
        print(json.dumps(out[-3:]), file=sys.stderr, flush=True)
    print(json.dumps(dict(cell=cell, taken=int(ok.sum()), members=out), indent=0))
