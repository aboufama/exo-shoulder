"""Validate the hex8-incompatible element (fe_core) against beam theory: a straight Ti-6Al-4V cantilever 14 x t x 100 mm,
root nodes fixed, a rigid end (tied master) loaded by a flatwise moment, an edgewise moment, a torque and a tip force.

    python3 -B fe_validate.py
"""
import sys, json, math, time
sys.dont_write_bytecode = True
import numpy as np
import fe_core as F


def box(L, W, T, nx, ny, nz):
    xs, ys, zs = np.linspace(0, L, nx + 1), np.linspace(-W / 2, W / 2, ny + 1), np.linspace(-T / 2, T / 2, nz + 1)
    X = np.stack(np.meshgrid(xs, ys, zs, indexing="ij"), -1).reshape(-1, 3)
    nid = lambda i, j, k: (i * (ny + 1) + j) * (nz + 1) + k
    I, J, K = np.meshgrid(np.arange(nx), np.arange(ny), np.arange(nz), indexing="ij"); I, J, K = I.ravel(), J.ravel(), K.ravel()
    H = np.stack([nid(I, J, K), nid(I + 1, J, K), nid(I + 1, J + 1, K), nid(I, J + 1, K),
                  nid(I, J, K + 1), nid(I + 1, J, K + 1), nid(I + 1, J + 1, K + 1), nid(I, J + 1, K + 1)], 1)
    return X, H


def run(t=4.0, W=14.0, L=100.0, h=0.7, nz=4):
    X, H = box(L, W, t, int(round(L / h)), int(round(W / h)), nz)
    m = F.Model(X, H); root = np.nonzero(X[:, 0] < 1e-9)[0]; tip = np.nonzero(X[:, 0] > L - 1e-9)[0]
    m.fix_nodes(root); M = m.add_master([L, 0, 0]); m.tie(tip, M)
    loads = [{"master": {M: np.r_[0, 0, 0, 0, 1e3, 0]}},         # flatwise moment (about y, bends through t)
             {"master": {M: np.r_[0, 0, 0, 0, 0, 1e3]}},         # edgewise moment (about z)
             {"master": {M: np.r_[0, 0, 0, 1e3, 0, 0]}},         # torque about x
             {"master": {M: np.r_[0, 0, 100.0, 0, 0, 0]}}]       # tip force 100 N through t
    out = m.solve(loads)
    G = F.E_TI / (2 * (1 + F.NU_TI)); I_f = W * t ** 3 / 12; I_e = t * W ** 3 / 12
    b, tt = max(W, t), min(W, t); Jt = b * tt ** 3 * (1 / 3 - 0.21 * tt / b * (1 - tt ** 4 / (12 * b ** 4))); Qt = b * b * tt * tt / (3 * b + 1.8 * tt)
    xm = X[np.argmin(np.abs(X[:, 0] - L / 2)), 0]; mid = np.nonzero(np.abs(X[:, 0] - xm) < 1e-9)[0]
    res = {}
    names = ["flatwise", "edgewise", "torsion", "tipforce"]
    theory_rot = [1e3 * L / (F.E_TI * I_f), 1e3 * L / (F.E_TI * I_e), 1e3 * L / (G * Jt), None]
    theory_s = [6e3 / (W * t * t), 6e3 / (t * W * W), math.sqrt(3) * 1e3 / Qt, 6 * 100 * L / 2 / (W * t * t)]
    for k, (U, Um) in enumerate(out):
        Sn, _ = m.nodal_stress(U); v = F.vm(Sn)
        rot = float(np.max(np.abs(Um[M, 3:]))) if k < 3 else float(Um[M, 2])
        th_rot = theory_rot[k] if k < 3 else 100 * L ** 3 / (3 * F.E_TI * I_f)
        res[names[k]] = dict(fe_mid_vm=float(v[mid].max()), beam_vm=theory_s[k], ratio_s=float(v[mid].max() / theory_s[k]),
                             fe_rot=rot, beam_rot=th_rot, ratio_rot=rot / th_rot)
    return res, m.ndof, m.t_total


if __name__ == "__main__":
    allres = {}
    for t, nz, h in ((4.0, 4, 0.7), (4.0, 2, 0.7), (2.5, 4, 0.7), (4.0, 4, 1.4)):
        r, nd, tt = run(t=t, nz=nz, h=h)
        print(f"t {t} nz {nz} h {h}: {nd} dof, {tt:.1f}s")
        for k, v in r.items():
            print(f"   {k:9s} stress FE/beam {v['ratio_s']:.3f} ({v['fe_mid_vm']:.1f} vs {v['beam_vm']:.1f} MPa)   rotation/defl FE/beam {v['ratio_rot']:.3f}")
        allres[f"t{t}_nz{nz}_h{h}"] = r
    json.dump(allres, open("validate.json", "w"), indent=1)
