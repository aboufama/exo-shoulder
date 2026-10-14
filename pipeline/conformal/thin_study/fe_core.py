"""Small linear-elastic solid FE core for the thin study (numpy / scipy only, CPU, 2 threads).

Element: 8-node hexahedron with Wilson-Taylor incompatible modes (the C3D8I idea): 9 internal bubble DOFs per element,
statically condensed, Taylor's det(J0)/det(J) correction so the patch test passes. Unlike the fully integrated hex8 used
in shoulder-d4/fea_link.py it does not shear-lock in bending, so 4 layers through a 2.5-5 mm plate give beam-theory
accuracy (checked in fe_validate.py).

Joint interfaces are modelled as they are built, not as rigid inserts:
  - masters: 6-DOF rigid bodies (a pin assembly, the other member's hub) with a reference point
  - springs: node <-> master elastic layers along a direction (the iglidur washer faces, the sleeve), stiffness per area
    k = E_layer / t_layer times the node's tributary area
  - ties: nodes rigidly slaved to a master (the integral pin column), eliminated exactly by a transformation T
  - master <-> master 6x6 springs (washer B + cap + sleeve between the upper hub and the pin)
"""
import os
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = "2"
import math, time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

E_TI, NU_TI = 113.8e3, 0.342          # Ti-6Al-4V (MPa)
RHO_TI = 4.43e-3                      # g/mm3
SY_TI, SE_TI = 880.0, 500.0           # yield (annealed), smooth endurance (R=-1, ~1e7)


def dmat(E, nu):
    lam, mu = E * nu / ((1 + nu) * (1 - 2 * nu)), E / (2 * (1 + nu))
    D = np.zeros((6, 6)); D[:3, :3] = lam; D[np.arange(3), np.arange(3)] += 2 * mu; D[3:, 3:] = np.eye(3) * mu
    return D


NXI = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float)
GP = NXI / math.sqrt(3.0)


def dN(xi):
    return 0.125 * NXI * np.stack([(1 + NXI[:, 1] * xi[1]) * (1 + NXI[:, 2] * xi[2]),
                                   (1 + NXI[:, 0] * xi[0]) * (1 + NXI[:, 2] * xi[2]),
                                   (1 + NXI[:, 0] * xi[0]) * (1 + NXI[:, 1] * xi[1])], 1)


DN_GP = np.stack([dN(g) for g in GP]); DN_C = dN(np.zeros(3)); DN_CORNER = np.stack([dN(x) for x in NXI])


def _jac(Xe, dn):
    J = np.einsum("ai,naj->nij", dn, Xe); return J, np.linalg.det(J)


def _B_from_dX(dX):
    """dX (n, m, 3) shape derivatives w.r.t. x for m 'nodes' -> B (n, 6, 3m)"""
    n, m, _ = dX.shape; B = np.zeros((n, 6, 3 * m))
    B[:, 0, 0::3] = dX[:, :, 0]; B[:, 1, 1::3] = dX[:, :, 1]; B[:, 2, 2::3] = dX[:, :, 2]
    B[:, 3, 0::3] = dX[:, :, 1]; B[:, 3, 1::3] = dX[:, :, 0]
    B[:, 4, 1::3] = dX[:, :, 2]; B[:, 4, 2::3] = dX[:, :, 1]
    B[:, 5, 0::3] = dX[:, :, 2]; B[:, 5, 2::3] = dX[:, :, 0]
    return B


def _B_inc(xi, J0i, scale):
    """incompatible-mode B (n, 6, 9) at natural point xi: modes P_k = 1 - xi_k^2, derivatives with J0 (Taylor)"""
    dP = np.zeros((3, 3)); dP[[0, 1, 2], [0, 1, 2]] = -2.0 * np.asarray(xi)       # dP_k/dxi_j  (k rows)
    dX = np.einsum("nij,kj->nki", J0i, dP) * scale[:, None, None]                  # (n, 3 modes, 3)
    return _B_from_dX(dX)


def element_mats(Xe, D):
    """condensed stiffness Ke (n,24,24) and recovery matrices R (n,9,24): alpha = R @ ue"""
    J0, d0 = _jac(Xe, DN_C); J0i = np.linalg.inv(J0)
    n = len(Xe); Kuu = np.zeros((n, 24, 24)); Kua = np.zeros((n, 24, 9)); Kaa = np.zeros((n, 9, 9))
    for g in range(8):
        J, dj = _jac(Xe, DN_GP[g])
        if (dj <= 0).any(): raise ValueError(f"{int((dj <= 0).sum())} inverted elements")
        Ji = np.linalg.inv(J); Bu = _B_from_dX(np.einsum("nij,aj->nai", Ji, DN_GP[g]))
        Ba = _B_inc(GP[g], J0i, d0 / dj)
        DBu = np.einsum("kl,nlj->nkj", D, Bu); DBa = np.einsum("kl,nlj->nkj", D, Ba)
        Kuu += np.einsum("nki,nkj,n->nij", Bu, DBu, dj); Kua += np.einsum("nki,nkj,n->nij", Bu, DBa, dj)
        Kaa += np.einsum("nki,nkj,n->nij", Ba, DBa, dj)
    Kaai = np.linalg.inv(Kaa)
    R = -np.einsum("nij,nkj->nik", Kaai, Kua)                                       # (n,9,24)
    Ke = Kuu + np.einsum("nij,njk->nik", Kua, R)
    return 0.5 * (Ke + Ke.transpose(0, 2, 1)), R, J0i, d0


def assemble(X, H, D, chunk=20000):
    rows, cols, vals, Rs, J0s, d0s = [], [], [], [], [], []
    for s in range(0, len(H), chunk):
        Hc = H[s:s + chunk]; Ke, R, J0i, d0 = element_mats(X[Hc], D)
        dof = (3 * Hc[:, :, None] + np.arange(3)).reshape(len(Hc), 24)
        rows.append(np.repeat(dof, 24, 1).ravel()); cols.append(np.tile(dof, (1, 24)).ravel()); vals.append(Ke.ravel())
        Rs.append(R); J0s.append(J0i); d0s.append(d0)
    n = 3 * len(X)
    K = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)).tocsr()
    return K, dict(R=np.concatenate(Rs), J0i=np.concatenate(J0s), d0=np.concatenate(d0s))


def corner_stress(X, H, D, U, aux):
    """(ne, 8, 6) stresses at the element corners (incl. incompatible modes)"""
    Xe = X[H]; ue = U[H].reshape(len(H), 24); al = np.einsum("nij,nj->ni", aux["R"], ue); out = []
    for c in range(8):
        J, dj = _jac(Xe, DN_CORNER[c]); Ji = np.linalg.inv(J)
        Bu = _B_from_dX(np.einsum("nij,aj->nai", Ji, DN_CORNER[c])); Ba = _B_inc(NXI[c], aux["J0i"], aux["d0"] / dj)
        eps = np.einsum("nij,nj->ni", Bu, ue) + np.einsum("nij,nj->ni", Ba, al)
        out.append(eps @ D.T)
    return np.stack(out, 1)


def nodal_average(H, Sc, nn):
    """average corner stresses at nodes -> (nn, 6)"""
    acc = np.zeros((nn, Sc.shape[-1])); cnt = np.zeros(nn)
    np.add.at(acc, H.ravel(), Sc.reshape(-1, Sc.shape[-1])); np.add.at(cnt, H.ravel(), 1.0)
    return acc / np.maximum(cnt, 1)[:, None]


VMQ = np.zeros((6, 6))
VMQ[:3, :3] = np.array([[1, -0.5, -0.5], [-0.5, 1, -0.5], [-0.5, -0.5, 1]]); VMQ[3:, 3:] = 3 * np.eye(3)


def vm(s): return np.sqrt(np.maximum(np.einsum("...i,ij,...j->...", s, VMQ, s), 0))


def worst_vm(fields, scale=1.0):
    """fields: list of (nn,6) unit stress fields; returns the von Mises maximised over unit combinations
    c (|c| = 1) of the fields, per node (largest eigenvalue of the quadratic form), times scale"""
    S = np.stack(fields, 1)                                           # (nn, k, 6)
    Q = np.einsum("nki,ij,nlj->nkl", S, VMQ, S)
    return np.sqrt(np.maximum(np.linalg.eigvalsh(Q)[:, -1], 0)) * scale


def hex_volume(X, H):
    v = 0.0
    for g in range(8): v = v + _jac(X[H], DN_GP[g])[1]
    return v                                                          # (ne,) mm3 (weights 1)


def face_areas(X, quads):
    """tributary area per node of a quad surface (list of 4-node quads) -> (nn,) and quad normals"""
    p = X[quads]; n = np.cross(p[:, 2] - p[:, 0], p[:, 3] - p[:, 1]) * 0.5
    A = np.linalg.norm(n, axis=1); w = np.zeros(len(X)); np.add.at(w, quads.ravel(), np.repeat(A / 4, 4))
    return w, n / np.maximum(A, 1e-12)[:, None]


def skew(v): return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


class Model:
    """nodes X (nn,3), hexes H; masters added with add_master; springs / ties / master springs; solve."""
    def __init__(self, X, H, E=E_TI, nu=NU_TI):
        self.X, self.H = np.asarray(X, float), np.asarray(H, int); self.D = dmat(E, nu)
        self.masters = []; self.spr = []; self.ties = {}; self.mspr = []; self.fixed_m = set(); self.fixed_nodes = None
    def add_master(self, c, name=""):
        self.masters.append((np.asarray(c, float), name)); return len(self.masters) - 1
    def mdof(self, m): return 3 * len(self.X) + 6 * m
    def add_springs(self, nodes, dirs, kA, m):
        """springs node_i <-> master m along dirs[i] (unit), stiffness kA[i] (N/mm)"""
        nodes = np.asarray(nodes, int); dirs = np.asarray(dirs, float).reshape(-1, 3); kA = np.broadcast_to(np.asarray(kA, float), (len(nodes),))
        self.spr.append((nodes, dirs, np.array(kA), m))
    def tie(self, nodes, m):
        for i in np.asarray(nodes, int): self.ties[int(i)] = m
    def add_mspring(self, m1, m2, K6):
        """6x6 spring (global coords, about the common reference point) between masters m1 and m2 (m2=None: ground)"""
        self.mspr.append((m1, m2, np.asarray(K6, float)))
    def fix_master(self, m): self.fixed_m.add(m)
    def fix_nodes(self, nodes): self.fixed_nodes = np.unique(np.r_[self.fixed_nodes if self.fixed_nodes is not None else [], nodes]).astype(int)

    def _spring_matrix(self, n):
        rows, cols, vals = [], [], []
        for nodes, dirs, kA, m in self.spr:
            c = self.masters[m][0]; r = self.X[nodes] - c; rxn = np.cross(r, dirs)
            g = np.concatenate([dirs, -dirs, -rxn], 1)                                     # (k, 9)
            idx = np.concatenate([3 * nodes[:, None] + np.arange(3), self.mdof(m) + np.arange(6)[None].repeat(len(nodes), 0)], 1)
            rows.append(np.repeat(idx, 9, 1).ravel()); cols.append(np.tile(idx, (1, 9)).ravel())
            vals.append((kA[:, None, None] * g[:, :, None] * g[:, None, :]).ravel())
        for m1, m2, K6 in self.mspr:
            if m2 is None:
                idx = self.mdof(m1) + np.arange(6); Kb = K6
            else:
                idx = np.r_[self.mdof(m1) + np.arange(6), self.mdof(m2) + np.arange(6)]; Kb = np.block([[K6, -K6], [-K6, K6]])
            rows.append(np.repeat(idx, len(idx))); cols.append(np.tile(idx, len(idx))); vals.append(Kb.ravel())
        if not rows: return sp.csr_matrix((n, n))
        return sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n)).tocsr()

    def _T(self):
        """full dof = T @ reduced dof (ties and fixed masters / nodes eliminated)"""
        nn = len(self.X); nm = len(self.masters); n = 3 * nn + 6 * nm
        fixedn = np.zeros(nn, bool)
        if self.fixed_nodes is not None: fixedn[self.fixed_nodes] = True
        tied = np.zeros(nn, bool); tied[list(self.ties.keys())] = True
        free_nodes = np.nonzero(~tied & ~fixedn)[0]; free_m = [m for m in range(nm) if m not in self.fixed_m]
        red = {}; k = 0
        for i in free_nodes:
            pass
        ndof_red = 3 * len(free_nodes) + 6 * len(free_m)
        rmap_node = -np.ones(nn, int); rmap_node[free_nodes] = np.arange(len(free_nodes))
        rmap_m = {m: 3 * len(free_nodes) + 6 * j for j, m in enumerate(free_m)}
        rows, cols, vals = [], [], []
        fd = 3 * free_nodes[:, None] + np.arange(3); rd = 3 * rmap_node[free_nodes][:, None] + np.arange(3)
        rows.append(fd.ravel()); cols.append(rd.ravel()); vals.append(np.ones(fd.size))
        for m in free_m:
            rows.append(self.mdof(m) + np.arange(6)); cols.append(rmap_m[m] + np.arange(6)); vals.append(np.ones(6))
        if self.ties:
            tn = np.array(list(self.ties.keys())); tm = np.array([self.ties[i] for i in tn])
            for m in np.unique(tm):
                sel = tn[tm == m]; c = self.masters[m][0]
                if m in self.fixed_m: continue
                r = self.X[sel] - c
                for a in range(3):                                                   # u_a = U_a + (theta x r)_a
                    rows.append(3 * sel + a); cols.append(np.full(len(sel), rmap_m[m] + a)); vals.append(np.ones(len(sel)))
                    # (theta x r)_a = sum_b theta_b * (e_b x r)_a
                    for b in range(3):
                        eb = np.zeros(3); eb[b] = 1; coef = np.cross(eb, r)[:, a]
                        nz = np.abs(coef) > 0
                        rows.append(3 * sel[nz] + a); cols.append(np.full(nz.sum(), rmap_m[m] + 3 + b)); vals.append(coef[nz])
        T = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, ndof_red)).tocsr()
        return T

    def solve(self, loads):
        """loads: list of dicts {"nodal": (nn,3) array or None, "master": {m: 6-vector (F, M) about its reference}}.
        Returns list of (U nodes (nn,3), master displacements (nm,6))"""
        t0 = time.time(); nn = len(self.X); nm = len(self.masters); n = 3 * nn + 6 * nm
        K, self.aux = assemble(self.X, self.H, self.D)
        K = sp.block_diag([K, sp.csr_matrix((6 * nm, 6 * nm))]).tocsr() + self._spring_matrix(n)
        T = self._T(); Kr = (T.T @ K @ T).tocsc()
        self.t_asm = time.time() - t0
        lu = sla.splu(Kr, permc_spec="MMD_AT_PLUS_A", options=dict(SymmetricMode=True))
        self.t_fact = time.time() - t0 - self.t_asm
        out = []
        for L in loads:
            f = np.zeros(n)
            if L.get("nodal") is not None: f[:3 * nn] = np.asarray(L["nodal"]).ravel()
            for m, v in L.get("master", {}).items(): f[self.mdof(m):self.mdof(m) + 6] += v
            ur = lu.solve(T.T @ f); u = T @ ur
            out.append((u[:3 * nn].reshape(-1, 3), u[3 * nn:].reshape(-1, 6) if nm else np.zeros((0, 6))))
        self.t_total = time.time() - t0; self.ndof = Kr.shape[0]
        return out

    def nodal_stress(self, U):
        Sc = corner_stress(self.X, self.H, self.D, U, self.aux)
        return nodal_average(self.H, Sc, len(self.X)), Sc

    def spring_forces(self, U, Um, which):
        """total force/moment (about the master reference) carried by spring set index `which`, on the nodes"""
        nodes, dirs, kA, m = self.spr[which]; c = self.masters[m][0]; r = self.X[nodes] - c
        um = Um[m]; urb = um[:3] + np.cross(um[3:], r)
        d = np.einsum("ij,ij->i", U[nodes] - urb, dirs); f = (kA * d)[:, None] * dirs   # force on master from nodes = +k d n
        return f.sum(0), np.cross(r, f).sum(0)


def rigid_fit(X, U, sel, c):
    """least-squares rigid motion (translation at c, rotation) of nodes sel"""
    d = X[sel] - c; A = np.zeros((3 * len(sel), 6)); A[:, :3] = np.tile(np.eye(3), (len(sel), 1))
    for i in range(len(sel)): A[3 * i:3 * i + 3, 3:] = -skew(d[i])
    return np.linalg.lstsq(A, U[sel].ravel(), rcond=None)[0]
