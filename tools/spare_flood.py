"""Shared continuity flood for a SCAPULAR SPARE (a spring-centred J0 carrying J1 of a spherical dyad J1-J2-J3) on the
FULL 15-deg workspace envelope grid (1432 poses of concept_bench's 'Workspace (envelope)' clip: 17 planes x 12
elevations x <= 25 axial; the Bench(110,360) ws poses are a 1-in-4 subsample of it).

Why (round 101 judge, docs/concepts/round101_ideation.md 1.1): stop-relay-rocker-3r's connected() floods only the 360
bench ws poses, a graph of 157 components (largest 10, 52 isolated, mean degree 1.13) that cannot carry a continuous
motion; the full grid is the instrument. Held-out poses become TRANSIT nodes only (kinematics, no skin, nothing scored or
tuned on them) - state this in every claim that uses it.

Everything lives in the scapula frame: u3S = HGrel @ w (HGrel = scapula -> humerus band rotation of the pose), J1 at
rotation q (deg) of u1r about the J0 axis c, th = angle(J1, J3); J2 closes iff lo <= th <= hi with lo = |a1 - a2| + m,
hi = min(a1 + a2, 360 - a1 - a2) - m (J2's own-angle stops at fold margin m in th, the H1 metric).
Policies (the spare's state q is TRACKED along 2-deg HG slerps between grid neighbours, up to max_states per node):
  clamp : spring-centred J0 + J2 stops. q -> nearest feasible (a push of <= jump deg, else a snap = no edge), then
          relax toward 0 inside the feasible component (the spring's preload wins while J2 is off its stops); when q != 0
          (J2 on a stop) the J0-J1-J3 sub-chain (arcs a0, th_stop) keeps a fold margin >= m_sw (no relay through its
          own singularity). This is stop-relay-rocker-3r's relay() made path-dependent.
  energy: twin spring (J0 spring k0 = 1 per rad^2 + J2 spring k2 about the rest-pose J2 interior angle psi_r): q ->
          local minimum of E reached by descent from the previous q inside the feasible window.
Seeds: 'rest' = every grid node of elevation <= seed_elev whose rest-proxy state is q = 0 (the proposer's setup);
'modeA' = every node where q = 0 is feasible (the stop-relay / minarc convention: mode-A poses are the plain chain).
Restricting the graph to the bench's own 360 nodes (nodes=bench) reproduces the old sparse instrument.

Validation (stop-relay section-5 setup; tools/spare_flood.py validate): C-stream seats u1r = bvec(98.84, 64.44),
J3 wdir(83.01, -15.19), a1 41.76 / a2 72.34, m = 10, T = 75, pivot = u1r tilted 40 deg at phi 120:
sparse 360-node ~0.67, full grid ~0.91 (bench-node reach).

    OMP_NUM_THREADS=1 nice -n 10 python3 tools/spare_flood.py validate
"""
import collections, math, os, sys
import numpy as np
from scipy.spatial.transform import Rotation as R, Slerp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import concept_kit as K                                       # noqa: E402
import concept_bench as CB                                    # noqa: E402

Z = CB._poses_all(); _names = list(Z['NAMES']); _wsid = _names.index('Workspace (envelope)')
GI = np.nonzero(Z['CID'] == _wsid)[0]                         # 1432 envelope poses (indices into the pose table)
HGrel = Z['HG'][GI].astype(float); GP = Z['POSE'][GI][:, :3].astype(float)
_pos = {tuple(p): j for j, p in enumerate(GP.round(3))}
VALS = [np.unique(GP[:, d]) for d in range(3)]
D2R = math.pi / 180
QG = np.arange(-120, 120.01, 0.5)


def node_of(plane, elev, axial):
    """grid node index of a ws pose (plane, elev, axial), or None"""
    return _pos.get(tuple(np.round(np.array([plane, elev, axial], float), 3)))


def bench_nodes(B):
    """(ws bench indices, their grid nodes) for a concept_bench Bench"""
    ws = [i for i in range(len(B.kind)) if B.kind[i] == 'ws']
    return ws, np.array([node_of(B.poses[i]['plane'], B.poses[i]['elev'], B.poses[i]['axial']) for i in ws])


def rot(k, v, a):
    a = np.radians(a)[..., None]; k = np.asarray(k, float)
    return v * np.cos(a) + np.cross(k, v) * np.sin(a) + k * (v @ k)[..., None] * (1 - np.cos(a))


def ang(a, b): return np.degrees(np.arccos(np.clip((a * b).sum(-1), -1, 1)))


def nbrs(j, allowed=None):
    x = GP[j]
    for d in range(3):
        k = int(np.searchsorted(VALS[d], x[d]))
        for kk in (k - 1, k + 1):
            if 0 <= kk < len(VALS[d]):
                y = x.copy(); y[d] = VALS[d][kk]; t = _pos.get(tuple(y.round(3)))
                if t is not None and (allowed is None or t in allowed): yield t


class Cfg:
    """one spare + dyad configuration in the scapula frame (unit vectors c, u1r, w = J3 in the humerus band frame)"""

    def __init__(s, c, u1r, w, a1, a2, T=60.0, m=5.0, policy='clamp', k2=0.0, m_sw=None, m_lo=None, m_hi=None,
                 relay_lo=True, relay_hi=True):
        s.c = K.unit(np.asarray(c, float)); s.u1r = K.unit(np.asarray(u1r, float)); s.w = K.unit(np.asarray(w, float))
        s.a1, s.a2, s.T, s.m, s.policy, s.k2 = float(a1), float(a2), float(T), float(m), policy, float(k2)
        s.m_sw = float(m if m_sw is None else m_sw)          # sub-chain (J0-J1-J3) fold margin while J2 is on a stop
        s.lo = abs(s.a1 - s.a2) + float(m if m_lo is None else m_lo)
        s.hi = min(s.a1 + s.a2, 360 - s.a1 - s.a2) - float(m if m_hi is None else m_hi)
        s.relay_lo, s.relay_hi = bool(relay_lo), bool(relay_hi)   # False: that stop is a plain joint limit (no relay)
        s.a0 = float(ang(s.c, s.u1r))
        s.U1 = rot(s.c, np.broadcast_to(s.u1r, (len(QG), 3)), QG)
        s.trav = np.abs(QG) <= s.T
        j0 = node_of(0, 0, 0); s.psir = float(s.psi(ang(s.u1r, HGrel[j0] @ s.w)))
        s.U3 = HGrel @ s.w

    def psi(s, th):
        a1, a2 = s.a1 * D2R, s.a2 * D2R
        c = (np.cos(np.asarray(th) * D2R) - math.cos(a1) * math.cos(a2)) / (math.sin(a1) * math.sin(a2))
        return np.degrees(np.arccos(np.clip(c, -1, 1)))

    def th(s, u3): return np.degrees(np.arccos(np.clip(u3 @ s.U1.T, -1, 1)))

    def submargin(s, u3, ths):
        g = float(ang(s.c, u3)); return min(g - abs(s.a0 - ths), s.a0 + ths - g, 360 - s.a0 - ths - g)

    def step(s, u3, q, jump=10.0):
        """new q (deg) from the previous q at arm direction u3, or None (jam / snap / sub-chain fold)"""
        TH = s.th(u3); feas = (TH >= s.lo) & (TH <= s.hi) & s.trav
        if not feas.any(): return None
        iq = int(round((q - QG[0]) / 0.5)); iq = min(max(iq, 0), len(QG) - 1)
        if not feas[iq]:                                       # pushed by a J2 stop: nearest feasible q
            idx = np.nonzero(feas)[0]; k = idx[np.argmin(np.abs(idx - iq))]
            if abs(QG[k] - q) > jump: return None
            iq = int(k)
        if s.policy == 'clamp':                                # the J0 spring relaxes q toward 0 inside the component
            i0 = int(round((0 - QG[0]) / 0.5)); sd = 1 if i0 > iq else -1
            while iq != i0 and feas[iq + sd]: iq += sd
            qn = float(QG[iq])
            if abs(qn) > 1e-9:
                ths = s.hi if TH[iq] > (s.lo + s.hi) / 2 else s.lo
                if not (s.relay_hi if ths == s.hi else s.relay_lo): return None
                if s.submargin(u3, ths) < s.m_sw: return None
        else:                                                  # twin spring: energy descent
            E = (QG * D2R) ** 2 + s.k2 * ((s.psi(TH) - s.psir) * D2R) ** 2
            E = np.where(feas, E, np.inf)
            while True:
                nb = [j for j in (iq - 1, iq + 1) if 0 <= j < len(QG)]
                j = min(nb, key=lambda j: E[j])
                if E[j] < E[iq]: iq = j
                else: break
            qn = float(QG[iq])
            if abs(TH[iq] - s.hi) < 0.6 or abs(TH[iq] - s.lo) < 0.6:
                ths = s.hi if abs(TH[iq] - s.hi) < 0.6 else s.lo
                if s.submargin(u3, ths) < s.m_sw: return None
        if abs(qn - q) > jump: return None
        return qn

    def static_q(s, u3):
        """the pose-local state: one step from q = 0 with no jump limit (least |q| feasible for the clamp)"""
        return s.step(u3, 0.0, jump=999.0)


def slerp_u3(ja, jb, w, step=2.0):
    r = R.from_matrix(np.stack([HGrel[ja], HGrel[jb]])); a = np.degrees((r[0].inv() * r[1]).magnitude())
    n = max(2, int(math.ceil(a / step)) + 1); M = Slerp([0, 1], r)(np.linspace(0, 1, n)).as_matrix()
    return M @ w


def flood(s, seeds='rest', seed_elev=30.0, max_states=6, nodes=None, jump=10.0):
    """BFS over (node, q) states. nodes: restrict the graph (e.g. the bench's 360 ws nodes = the old sparse instrument).
    -> conn (1432,) bool, states {node: set of rounded q}"""
    N = len(GP); allowed = None if nodes is None else set(int(x) for x in nodes)
    states = collections.defaultdict(set); front = []
    cand = range(N) if allowed is None else sorted(allowed)
    for j in cand:
        if seeds == 'rest' and GP[j, 1] > seed_elev: continue
        q = s.static_q(s.U3[j])
        if q is not None and abs(q) < 1e-9: states[j].add(0.0); front.append((j, 0.0))
    while front:
        nxt = []
        for j, q in front:
            for t in nbrs(j, allowed):
                if len(states[t]) >= max_states: continue
                qq = q; ok = True
                for u3 in slerp_u3(j, t, s.w)[1:]:
                    qq = s.step(u3, qq, jump=jump)
                    if qq is None: ok = False; break
                if not ok: continue
                key = round(qq)
                if any(abs(key - x) < 2 for x in states[t]): continue
                states[t].add(key); nxt.append((t, qq))
        front = nxt
    conn = np.array([len(states[j]) > 0 for j in range(N)])
    return conn, states


def run(s, nodes_b, tag='', **kw):
    """reach on the given bench nodes: plain (q = 0), free (any q in travel), static (pose-local state), connected (full
    grid flood), connected_sparse (flood restricted to nodes_b); overhead (elev >= 140) counts"""
    TH = s.th(s.U3[nodes_b]); feas = (TH >= s.lo) & (TH <= s.hi) & s.trav[None, :]
    i0 = int(round((0 - QG[0]) / 0.5)); plain = feas[:, i0]; free = feas.any(1)
    stat = np.array([s.static_q(u3) is not None for u3 in s.U3[nodes_b]])
    conn, states = flood(s, **kw); cb = conn[nodes_b]
    connS, _ = flood(s, nodes=nodes_b, **kw); cs = connS[nodes_b]
    ov = GP[nodes_b, 1] >= 140
    qs = [x for j in nodes_b for x in states[j]]
    out = dict(tag=tag, plain=round(float(plain.mean()), 3), free=round(float(free.mean()), 3), static=round(float(stat.mean()), 3),
               connected=round(float(cb.mean()), 3), connected_sparse=round(float(cs.mean()), 3),
               ov_plain=int(plain[ov].sum()), ov_static=int(stat[ov].sum()), ov_conn=int(cb[ov].sum()),
               ov_conn_sparse=int(cs[ov].sum()), n_ov=int(ov.sum()), grid_conn=round(float(conn.mean()), 3),
               q_range=[min(qs), max(qs)] if qs else None)
    return out, conn, states


def tilt_pivot(u1r, a0, phi):
    """stop-relay's pivot_dir(): u1r tilted by a0 about a normal turned phi about u1r"""
    u1r = np.asarray(u1r, float); ref = K.unit(np.cross(u1r, [0.0, 1.0, 0.0])); ax = rot(u1r, ref, np.array(phi))
    return rot(ax, u1r, np.array(a0))


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'validate':
    import json, time
    B = CB.Bench(110, 360); _, nb = bench_nodes(B)
    w = K.wdir(83.01, -15.19); u1r = K.bvec(98.84, 64.44)
    for seeds in ('rest', 'modeA'):
        s = Cfg(tilt_pivot(u1r, 40, 120), u1r, w, 41.76, 72.34, T=75.0, m=10.0, policy='clamp')
        t = time.time(); o, _, _ = run(s, nb, f'stop-relay section-5 seats m10 beta 40 phi 120 seeds {seeds}', seeds=seeds)
        o['secs'] = round(time.time() - t, 1); print(json.dumps(o), flush=True)
    s = Cfg(tilt_pivot(u1r, 40, 120), u1r, w, 41.76, 72.34, T=0.0, m=10.0, policy='clamp')
    o, _, _ = run(s, nb, 'mode A only (T 0)'); print(json.dumps(o), flush=True)
