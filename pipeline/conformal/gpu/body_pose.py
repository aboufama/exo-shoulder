"""Posed skin of the viewer's body rig (output/arm-rom/body.js), ported to numpy for the exo's skin maps.

Same maths, step for step, as body.js update(): centre-of-rotation skinning (4 influences, forearm twist), the muscle
models (spindle muscles about their centreline with the bowstring length change, flat muscles thickened with the fibre
stretch, exact volume correction), the relaxed axilla, Delta Mush over the blended joints, the skin height field over
the muscles and the humeral-head guard. The only thing left out is the GPU-only hair volume on the scalp.

    import body_pose as BP
    P = BP.posed(dict(plane=30, elev=97, axial=-6, flex=12, pron=0))    # (N, 3) render-skin vertices, mm
    BP.F            (M, 3) faces of the render skin (outer shell + axilla pocket + full-res head), watertight
    BP.V0           (N, 3) rest positions
    BP.ARMV / ARMF  skin driven by the right arm (humerus + forearm + hand weight > 0.5) / faces with >= 2 such vertices,
                    as radial_maps.ARMV / ARMF; ~ARMV is the trunk + scapula skin
    BP.SRC          legacy skin vertex of each render vertex (-1: pocket or full-res head vertex)

Frame: thorax mm, x anterior, y up, z right, origin = right GH centre; the trunk moved by -lift exactly like
radial_maps.posed() (segs()[0] = (I, -lift)), the arm about the GH centre.
Optional: posed(pose, act=dict(shoulder=, flexor=, extensor=)) overrides the gravity activation, as body.js does.
Check against the browser rig: node ../arm-rom/export_posed_skin.mjs body_mesh.json poses.json out (see __main__).
"""
import base64, json, math, os
try:
    import numpy as np                                         # the Flash build imports this file without numpy
    from scipy.sparse import csr_matrix
except ImportError:
    np = csr_matrix = None

D2R = math.pi / 180
HERE = os.path.dirname(os.path.abspath(__file__))
MUSH_IT = 10
dec = lambda s, t: np.frombuffer(base64.b64decode(s), dtype=t)


def rot(ax, a):
    ax = np.asarray(ax, float); ax = ax / np.linalg.norm(ax)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def scap(elev):
    n = [math.cos(30 * D2R), 0, -math.sin(30 * D2R)]
    return rot([0, 0, 1], 0.12 * elev * D2R) @ rot(n, -0.36 * max(0, elev - 20) * D2R)


def segs(L, S, pose, girdle=True):
    """body.js segmentTransforms: [T, S, H, F, P] as (R, t)"""
    lift = np.array([0, 0.2 * max(0, pose["elev"] - 30) * S, 0]) if girdle else np.zeros(3)
    Rh = rot([0, 1, 0], pose["plane"] * D2R) @ rot([1, 0, 0], -pose["elev"] * D2R) @ rot([0, 1, 0], pose["axial"] * D2R)
    T = (np.eye(3), -lift); Sg = (scap(pose["elev"]), np.zeros(3)); H = (Rh @ np.array(L["rest_humerus"]).T, np.zeros(3))
    ap = lambda A, p: A[0] @ p + A[1]
    E = ap(H, np.array(L["elbow"])); ax = H[0] @ np.array(L["elbow_axis"])
    Rf = rot(ax, (pose["flex"] - L["rest_flex"]) * D2R); Fs = (Rf @ H[0], Rf @ H[1] + E - Rf @ E)
    rh, uh = ap(Fs, np.array(L["radial_head"])), ap(Fs, np.array(L["ulnar_head"]))
    Rp = rot(rh - uh, (pose["pron"] + 90) * D2R); P = (Rp @ Fs[0], Rp @ Fs[1] + rh - Rp @ rh)
    return [T, Sg, H, Fs, P], lift


def quat(R):                                              # same branches as body.js quat()
    m00, m11, m22 = R[0, 0], R[1, 1], R[2, 2]; tr = m00 + m11 + m22
    if tr > 0: S = math.sqrt(tr + 1) * 2; q = [0.25 * S, (R[2, 1] - R[1, 2]) / S, (R[0, 2] - R[2, 0]) / S, (R[1, 0] - R[0, 1]) / S]
    elif m00 > m11 and m00 > m22: S = math.sqrt(1 + m00 - m11 - m22) * 2; q = [(R[2, 1] - R[1, 2]) / S, 0.25 * S, (R[0, 1] + R[1, 0]) / S, (R[0, 2] + R[2, 0]) / S]
    elif m11 > m22: S = math.sqrt(1 + m11 - m00 - m22) * 2; q = [(R[0, 2] - R[2, 0]) / S, (R[0, 1] + R[1, 0]) / S, 0.25 * S, (R[1, 2] + R[2, 1]) / S]
    else: S = math.sqrt(1 + m22 - m00 - m11) * 2; q = [(R[1, 0] - R[0, 1]) / S, (R[0, 2] + R[2, 0]) / S, (R[1, 2] + R[2, 1]) / S, 0.25 * S]
    q = np.array(q); return q / np.linalg.norm(q)


def qrot(q, v):                                           # rotate v (n,3) by unit quaternions q (n,4) [w,x,y,z]
    w, u = q[:, :1], q[:, 1:]; t = 2 * np.cross(u, v); return v + w * t + np.cross(u, t)


def smooth01(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)


def neighbour_lists(F, n):
    """body.js order: per face, per edge (a, b): b appended to a's list, then a to b's (duplicates kept)"""
    a = np.r_[F[:, [0, 1, 2]]].T.ravel(); b = F[:, [1, 2, 0]].T.ravel()        # edge k of every face, k-major
    f_ = np.tile(np.arange(len(F)), 3); k_ = np.repeat(np.arange(3), len(F))
    owner = np.r_[a, b]; other = np.r_[b, a]; seq = np.r_[6 * f_ + 2 * k_, 6 * f_ + 2 * k_ + 1]
    o = np.lexsort((seq, owner)); owner, other = owner[o], other[o]
    start = np.r_[0, np.cumsum(np.bincount(owner, minlength=n))]
    return start, other


def avg_matrix(start, nb, n):
    cnt = np.diff(start); rows = np.repeat(np.arange(n), cnt)
    return csr_matrix((1.0 / np.maximum(cnt, 1)[rows], (rows, nb)), shape=(n, n))


def mesh_volume(P, F):
    a, b, c = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]; return (a * np.cross(b, c)).sum() / 6


class Rig:
    def __init__(self, path=os.path.join(HERE, "body_mesh.json")):
        J = json.load(open(path)); self.J = J; L = self.L = J["landmarks"]; s = self.s = J["scale"]
        ua = np.array(L["radial_head"]) - np.array(L["ulnar_head"]); self._ua, self._uu, self._uh = ua, ua @ ua, np.array(L["ulnar_head"])
        sk = next(p for p in J["parts"] if p["cls"] == "skin")
        if "rpos" not in sk: raise ValueError("body_mesh.json has no render-skin rig (rebuild with anatomy-build/build_body.py)")
        self.dyn = []; self.by_part = {}
        for pi, p in enumerate(J["parts"]):
            if "w4i" not in p: continue
            d = self._load_dynamic(p); self.dyn.append(d); self.by_part[pi] = d
        self.moving = [self.by_part.get(i) for i in J["moving"]]
        self.skin = next(d for d in self.dyn if d["cls"] == "skin")
        self._init_skin(sk)

    # ------------------------------------------------------------------ loading
    def twist(self, X):
        al = (X - self._uh) @ self._ua / self._uu; t = np.clip(1.1 - al, 0, 1); return t * t * (3 - 2 * t)

    def _load_dynamic(self, p):
        if p["cls"] == "skin":
            pos = dec(p["rpos"], np.int16).reshape(-1, 3).astype(np.float32) / np.float32(10)
            idx = dec(p["ridx"], np.uint32 if p.get("ri32") else np.uint16).reshape(-1, 3).astype(int)
        else:
            pos = dec(p["pos"], np.int16).reshape(-1, 3).astype(np.float32) / np.float32(10)
            idx = dec(p["idx"], np.uint32 if p.get("i32") else np.uint16).reshape(-1, 3).astype(int)
        n = len(pos); d = dict(name=p["name"], cls=p["cls"], n=n, F=idx, rest=pos.astype(float))
        d["wi"] = dec(p["w4i"], np.uint8).reshape(-1, 4).astype(int); d["ww"] = dec(p["w4w"], np.uint8).reshape(-1, 4).astype(float) / 255
        d["C"] = (dec(p["cor"], np.int16).reshape(-1, 3).astype(np.float32) / np.float32(10)).astype(float)
        d["tw"] = self.twist(d["rest"]); d["arch"] = p.get("arch") or [0.4, 5, 0]
        M = p.get("mdl")
        if M: self._init_model(d, M, dec(p["belly"], np.uint8).astype(float) / 255 if "belly" in p else None)
        return d

    def _init_model(self, d, M, belly):
        R, n = d["rest"], d["n"]
        if M["type"] == "sheet":
            d["shm"] = dict(nrm=dec(M["n"], np.int8).reshape(-1, 3).astype(np.float32) / np.float32(127), sup=dec(M["sup"], np.uint8).astype(float) / 255,
                            pf=dec(M["pf"], np.uint16).astype(int), pb=dec(M["pb"], np.uint16).astype(int),
                            l0=dec(M["l0"], np.uint16).astype(np.float32) / np.float32(10), th=dec(M["th"], np.uint8).astype(np.float32) / np.float32(8))
            d["vfixW"] = d["shm"]["sup"] * (belly if belly is not None else 1.0)
            d["V0"] = mesh_volume(R, d["F"]); return
        K = M["K"]; sk = np.array(M["sk"]); L0 = M["L0"]
        s_ = dec(M["s"], np.uint16).astype(float) / 65535 * L0
        x = (dec(M["x"], np.int16).reshape(-1, 3).astype(np.float32) / np.float32(10)).astype(float)
        mu = dec(M["mu"], np.uint8).astype(float) / 255; kv = dec(M["k"], np.uint8).astype(int)
        j = np.clip(np.searchsorted(sk[1:K - 1], s_, side="left"), 0, K - 2)              # while (j < K-2 && sk[j+1] < s) j++
        u = np.clip((s_ - sk[j]) / (sk[j + 1] - sk[j] + 1e-9), 0, 1)
        cnt = np.bincount(kv, minlength=K).astype(float); G = np.zeros((K, 3)); np.add.at(G, kv, R)
        C = np.array(M["C"]); off = np.where(cnt[:, None] > 0, C - G / np.maximum(cnt, 1)[:, None], 0.0)
        phi = np.array(M["phi"]); Phi = float((0.5 * (phi[:-1] + phi[1:]) * np.diff(sk)).sum())
        be = K - 1
        while be > 0 and phi[be] < 0.05: be -= 1
        tau, fr, tauL = (M.get("taut") or [0, 1, 0]) + [None] * 0
        kf = min(K - 2, max(1, int(math.floor(fr * (K - 1) + 0.5))))
        arc = float(np.linalg.norm(np.diff(C[:kf + 1], axis=0), axis=1).sum())
        ins = M.get("ins") or [4, C[K - 1].tolist()]
        eO = np.zeros(K); eD = np.zeros(K); cO = np.zeros(K); cD = np.zeros(K); xe = x[:, 1]
        np.add.at(eO, kv[xe > 0], xe[xe > 0]); np.add.at(cO, kv[xe > 0], 1); np.add.at(eD, kv[xe <= 0], -xe[xe <= 0]); np.add.at(cD, kv[xe <= 0], 1)
        eO = np.where(cO > 0, eO / np.maximum(cO, 1), 1.0); eD = np.where(cD > 0, eD / np.maximum(cD, 1), 1.0)
        dev = np.zeros((K, 3))
        for k in range(kf + 1, K):
            uu = (sk[k] - sk[kf]) / (sk[K - 1] - sk[kf]); dev[k] = C[k] - (C[kf] + uu * (C[K - 1] - C[kf]))
        ph = phi[j] + u * (phi[j + 1] - phi[j])
        d["fus"] = dict(K=K, sk=sk, L0=L0, C=C, E=np.array(M["E"]), phi=phi, NW=np.array(M["NW"]), RT=np.array(M["RT"]), x=x, mu=mu, kv=kv, s=s_, j=j, u=u,
                        cnt=cnt, off=off, tw=self.twist(C), Phi=Phi, sBellyEnd=sk[be], biceps="biceps brachii" in d["name"], freeEnd=bool(M.get("free_end")),
                        tau=tau, tauL=tau if tauL is None else tauL, kf=kf, ins=(int(ins[0]), np.array(ins[1], float)), chordRes=L0 - arc - float(np.linalg.norm(np.array(ins[1]) - C[kf])),
                        eO=eO, eD=eD, dev=dev)
        d["vfixW"] = ph * mu * np.where(xe > 0, 1.0, 0.3); d["V0"] = mesh_volume(R, d["F"])

    def _init_skin(self, sk):
        d = self.skin; n = d["n"]; F = d["F"]; s = self.s
        self.V0 = d["rest"].copy(); self.F = F; self.SRC = np.where(dec(sk["rsrc"], np.uint16) == 65535, -1, dec(sk["rsrc"], np.uint16).astype(int))
        W = np.zeros((n, 5)); np.add.at(W, (np.repeat(np.arange(n), 4), d["wi"].ravel()), d["ww"].ravel())
        self.ARMV = W[:, 2:].sum(1) > 0.5; self.ARMF = self.ARMV[F].sum(1) >= 2
        d["rest0"] = d["rest"].copy()
        d["rlxi"] = dec(sk["rlxi"], np.uint32).astype(int) if "rlxi" in sk else np.zeros(0, int)
        d["rlxd"] = (dec(sk["rlxd"], np.int16).reshape(-1, 3).astype(np.float32) / np.float32(10)).astype(float) if "rlxi" in sk else np.zeros((0, 3))
        d["rsm"] = dec(sk["rsm"], np.uint32).astype(int) if "rsm" in sk else np.zeros(0, int)
        start, nb = neighbour_lists(F, n); d["start"], d["nb"] = start, nb; A = avg_matrix(start, nb, n); d["A"] = A
        first = nb[start[:-1]]
        # skin binding (follow) region: bound vertices + two rings
        d["foj"] = dec(sk["foj"], np.uint8).astype(int); d["fov"] = dec(sk["fov"], np.uint16).astype(int); d["fow"] = dec(sk["fow"], np.uint8).astype(float) / 255
        bound = np.flatnonzero((d["foj"] != 255) & (d["fow"] > 0)); region = np.zeros(n, bool); region[bound] = True
        cnt = np.diff(start); owner = np.repeat(np.arange(n), cnt)
        for _ in range(2): region[nb[region[owner]]] = True
        d["bound"] = bound; d["region"] = np.flatnonzero(region); d["regionF"] = F[region[F].any(1)]
        # Delta Mush region: blended weights (+ relaxed axilla), three feathering rings, ring 4 fixed
        ring = np.full(n, -1); ring[(d["ww"] * 255 + 0.5).astype(int).max(1) < 248] = 0; ring[d["rlxi"]] = 0; ring[d["rsm"]] = 0
        for r in range(1, 5):
            src = ring[owner] == r - 1; tgt = nb[src]; tgt = tgt[ring[tgt] < 0]; ring[tgt] = r
        lst = np.flatnonzero((ring >= 0) & (ring < 4)); inR = np.zeros(n, bool); inR[lst] = True
        amt = np.where(ring <= 1, 1.0, np.where(ring == 2, 0.66, 0.33))
        m = dict(list=lst, amt=amt, faces=F[inR[F].any(1)], first=first)
        rx = np.unique(np.r_[d["rlxi"], d["rsm"]]); m["relaxList"] = rx[inR[rx]] if len(d["rlxi"]) else np.zeros(0, int)
        d["mush"] = m
        rest1 = d["rest0"].copy()
        if len(d["rlxi"]): rest1[d["rlxi"]] += d["rlxd"]
        m["C0"] = self._mush_coeffs(d, d["rest0"]); m["C1"] = self._mush_coeffs(d, rest1) if len(d["rlxi"]) else m["C0"].copy()
        if len(d["rlxi"]): m["C1"][rx] = 0
        r0 = np.linalg.norm(d["rest0"], axis=1); g = np.flatnonzero(r0 < 160 * s)
        d["guard"] = g; d["guardR"] = np.minimum(r0[g] - 2, 38 * s)

    # ------------------------------------------------------------------ Delta Mush
    def _mush_smooth(self, d, P, al=0.0):
        m = d["mush"]; A = d["A"]; S = P.copy(); L_ = m["list"]
        for _ in range(MUSH_IT): T = A @ S; S[L_] = 0.5 * S[L_] + 0.5 * T[L_]
        if al > 0 and len(m["relaxList"]):
            Rl = m["relaxList"]
            for _ in range(int(math.floor(30 * al + 0.5))): T = A @ S; S[Rl] = 0.5 * S[Rl] + 0.5 * T[Rl]
        Fm = m["faces"]; fn = np.cross(S[Fm[:, 1]] - S[Fm[:, 0]], S[Fm[:, 2]] - S[Fm[:, 0]]); N = np.zeros_like(S)
        for k in range(3): np.add.at(N, Fm[:, k], fn)
        return S, N

    def _frames(self, d, S, N, idx):
        m = d["mush"]; n_ = N[idx]; nl = np.linalg.norm(n_, axis=1, keepdims=True); nl[nl == 0] = 1; n_ = n_ / nl
        t = S[m["first"][idx]] - S[idx]; t -= (t * n_).sum(1, keepdims=True) * n_; tl = np.linalg.norm(t, axis=1, keepdims=True); tl[tl == 0] = 1; t = t / tl
        return t, np.cross(n_, t), n_

    def _mush_coeffs(self, d, R):
        S, N = self._mush_smooth(d, R); L_ = d["mush"]["list"]; t, b, n_ = self._frames(d, S, N, L_); D = R[L_] - S[L_]
        C = np.zeros((d["n"], 3)); C[L_] = np.c_[(D * t).sum(1), (D * b).sum(1), (D * n_).sum(1)]; return C

    # ------------------------------------------------------------------ per pose
    def _ctx(self, pose, act):
        L = self.L; sg, lift = segs(L, self.s, pose)
        HR = np.array(L["rest_humerus"])
        arm = sg[2][0] @ (HR.T @ np.array([0, -1.0, 0]))
        armLoad = min(1, 1.1 * math.sqrt(max(0, 1 - arm[1] ** 2)))
        fd = np.array(L["ulnar_head"]) - np.array(L["elbow"]); fore = sg[3][0] @ (fd / np.linalg.norm(fd)); eax = sg[2][0] @ np.array(L["elbow_axis"])
        gm = (fore[1] * 0 - fore[2] * -1) * eax[0] + (fore[2] * 0 - fore[0] * 0) * eax[1] + (fore[0] * -1 - fore[1] * 0) * eax[2]
        foreLoad = min(1, 1.3 * math.sqrt(max(0, 1 - fore[1] ** 2)))
        if act: ACT = [0, act.get("shoulder", armLoad), act.get("flexor", 0), act.get("extensor", 0)]
        else: ACT = [0, armLoad, foreLoad if gm < 0 else 0.1 * foreLoad, foreLoad if gm > 0 else 0.1 * foreLoad]
        ACT = [0] + [max(0.06, min(1, a)) for a in ACT[1:]]
        Q = np.array([quat(A[0]) for A in sg]); Q[4] = Q[3]
        Ra = np.stack([A[0] for A in sg]); ta = np.stack([A[1] for A in sg]); Ra[4] = Ra[3]; ta[4] = ta[3]
        rhP = sg[3][0] @ np.array(L["radial_head"]) + sg[3][1]; uhP = sg[3][0] @ np.array(L["ulnar_head"]) + sg[3][1]
        k = (rhP - uhP) / np.linalg.norm(rhP - uhP)
        return dict(segs=sg, lift=lift, Q=Q, Ra=Ra, ta=ta, rhP=rhP, k=k, th=(pose["pron"] + 90) * D2R, ACT=ACT, pose=pose)

    def _cor(self, d, R, ctx, want_q=False):
        wi, ww, C, Q, Ra, ta = d["wi"], d["ww"], d["C"], ctx["Q"], ctx["Ra"], ctx["ta"]
        r0 = Q[wi[:, 0]]; q = np.zeros((len(R), 4)); c = np.zeros((len(R), 3)); fp = np.zeros(len(R))
        for j in range(4):
            kk = wi[:, j]; w = ww[:, j]; qk = Q[kk]; sg = np.where((qk * r0).sum(1) < 0, -w, w)
            q += sg[:, None] * qk; c += w[:, None] * (np.einsum("nij,nj->ni", Ra[kk], C) + ta[kk]); fp += np.where(kk >= 3, w, 0)
        q /= np.linalg.norm(q, axis=1, keepdims=True)
        P = c + qrot(q, R - C)
        ang = ctx["th"] * d["tw"] * fp; m = ang != 0
        if m.any():
            kx = ctx["k"]; v = P[m] - ctx["rhP"]; ca = np.cos(ang[m])[:, None]; sa = np.sin(ang[m])[:, None]
            P[m] = ctx["rhP"] + v * ca + np.cross(kx, v) * sa + np.outer(v @ kx, kx) * (1 - ca)
            if want_q:
                h = ang[m] / 2; a4 = np.c_[np.cos(h), np.outer(np.sin(h), kx)]; b4 = q[m]
                q[m] = np.c_[a4[:, 0] * b4[:, 0] - (a4[:, 1:] * b4[:, 1:]).sum(1),
                             a4[:, :1] * b4[:, 1:] + b4[:, :1] * a4[:, 1:] + np.cross(a4[:, 1:], b4[:, 1:])]
        return P, q

    def _turn(self, Wv, v, tw, ctx):
        Q = ctx["Q"]; k0 = int(np.argmax(Wv)); r0 = Q[k0]; q = np.zeros(4); fp = 0.0
        for k in range(5):
            w = Wv[k]
            if not w: continue
            if k >= 3: fp += w
            q += (-w if Q[k] @ r0 < 0 else w) * Q[k]
        q /= np.linalg.norm(q); r = qrot(q[None], np.asarray(v, float)[None])[0]
        ang = ctx["th"] * tw * fp
        if ang:
            kx = ctx["k"]; c, s_ = math.cos(ang), math.sin(ang); r = r * c + np.cross(kx, r) * s_ + kx * (kx @ r) * (1 - c)
        return r

    def _fusiform(self, d, B, ctx):
        f = d["fus"]; K, sk = f["K"], f["sk"]; a = ctx["ACT"][d["arch"][2]] or 0.06; s = self.s
        G = np.zeros((K, 3)); np.add.at(G, f["kv"], B)
        cp = np.full((K, 3), np.nan); ep = np.zeros((K, 3))
        for k in range(K):
            o = self._turn(f["NW"][k], f["off"][k], f["tw"][k], ctx); ep[k] = self._turn(f["NW"][k], f["E"][k], f["tw"][k], ctx)
            if f["cnt"][k]: cp[k] = G[k] / f["cnt"][k] + o
        for k in range(K):
            if np.isnan(cp[k, 0]):
                lo, hi = k - 1, k + 1
                while lo >= 0 and np.isnan(cp[lo, 0]): lo -= 1
                while hi < K and np.isnan(cp[hi, 0]): hi += 1
                cp[k] = cp[hi] if lo < 0 else cp[lo] if hi >= K else cp[lo] + (cp[hi] - cp[lo]) * (k - lo) / (hi - lo)
        seg = np.linalg.norm(np.diff(cp, axis=0), axis=1); L1cor = seg.sum(); arcF = seg[:f["kf"]].sum()
        Ip = ctx["segs"][f["ins"][0]][0] @ f["ins"][1] + ctx["segs"][f["ins"][0]][1]
        Lch = arcF + np.linalg.norm(Ip - cp[f["kf"]]) + f["chordRes"]
        if f["tau"] > 0:
            kf = f["kf"]
            for k in range(kf + 1, K - 1):
                u = (sk[k] - sk[kf]) / (sk[K - 1] - sk[kf]); dv = self._turn(f["NW"][k], f["dev"][k], f["tw"][k], ctx)
                cp[k] += f["tau"] * (cp[kf] + u * (cp[K - 1] - cp[kf]) + dv - cp[k])
        k0 = np.maximum(np.arange(K) - 1, 0); k1 = np.minimum(np.arange(K) + 1, K - 1)
        tp = cp[k1] - cp[k0]; tn = np.linalg.norm(tp, axis=1, keepdims=True); tn[tn == 0] = 1; tp /= tn
        sc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(cp, axis=0), axis=1))]; L1 = sc[-1]
        wrap = 3 * s * max(0, (ctx["pose"]["pron"] + 90) * D2R) if f["biceps"] else 0
        L1e = f["L0"] + (1 - f["tauL"]) * (L1cor - f["L0"]) + f["tauL"] * (Lch - f["L0"]) + wrap; eps = 0.025 * a
        kap = (L1e - f["L0"] - eps * (f["L0"] - f["Phi"])) / max(1e-6, f["Phi"])
        phi = f["phi"]; sn = np.clip(1 + kap * phi + eps * (1 - phi), 0.42, 1.9)
        tot = (0.5 * (sn[:-1] + sn[1:]) * np.diff(sk)).sum(); fix = (L1e - tot) / max(1e-6, f["L0"] - f["Phi"])
        gam = 0.5 + 0.1 * a; firm = 1 + 0.06 * a
        g = sn + fix * (1 - phi); A_ = 1 / g; fk = np.where(phi > 0, firm, 1.0); t = A_ ** gam * fk; w = A_ ** (1 - gam) / fk
        aD = 1 + 0.3 * (t - 1); aO = np.maximum(0.3, (t * (f["eO"] + f["eD"]) - aD * f["eD"]) / f["eO"]); aB = w
        sN = np.r_[0, np.cumsum(0.5 * (g[:-1] + g[1:]) * np.diff(sk))]
        endFix = 0 if f["freeEnd"] else L1 - sN[-1]
        bt = np.clip((sk - f["sBellyEnd"]) / (f["L0"] - f["sBellyEnd"]), 0, 1); sN = sN + endFix * bt * bt * (3 - 2 * bt)
        # vertices
        j, u, x = f["j"], f["u"], f["x"]
        mu = np.where(f["freeEnd"] & (f["s"] > 0.5 * f["L0"]), 1.0, f["mu"]); act_ = mu > 0
        sig = sN[j] + u * (sN[j + 1] - sN[j])
        m = np.clip(np.searchsorted(sc[1:K - 1], sig, side="left"), 0, K - 2)              # interval of sig in sc
        v = np.clip((sig - sc[m]) / (sc[m + 1] - sc[m] + 1e-9), 0, 1)[:, None]
        cxyz = cp[m] + v * (cp[m + 1] - cp[m])
        tt = tp[m] + v * (tp[m + 1] - tp[m]); tt /= np.linalg.norm(tt, axis=1, keepdims=True)
        ee = ep[m] + v * (ep[m + 1] - ep[m]); ee -= (ee * tt).sum(1, keepdims=True) * tt; ee /= np.linalg.norm(ee, axis=1, keepdims=True)
        bb = np.cross(tt, ee)
        uu = u; aOv = aO[j] + uu * (aO[j + 1] - aO[j]); aDv = aD[j] + uu * (aD[j + 1] - aD[j]); aBv = aB[j] + uu * (aB[j + 1] - aB[j])
        se = x[:, 1] * np.where(x[:, 1] > 0, aOv, aDv); sb = x[:, 2] * aBv
        pm = cxyz + x[:, :1] * tt + se[:, None] * ee + sb[:, None] * bb
        P = B + mu[:, None] * (pm - B); P[~act_] = B[~act_]
        f["state"] = dict(sc=sc, sN=sN, aO=aO, aD=aD, aB=aB, L1=L1e)
        return P

    def _sheet(self, d, B, q, ctx):
        S_ = d["shm"]; a = ctx["ACT"][d["arch"][2]] or 0.06; ca = math.cos(d["arch"][1] * D2R) ** 2
        lam = np.clip(np.linalg.norm(B[S_["pf"]] - B[S_["pb"]], axis=1) / S_["l0"], 0.5, 1.8)
        k = S_["sup"] * S_["th"] * ((lam ** (-0.8 * ca) - 1) + 0.05 * a)
        k = np.where((S_["sup"] > 0) & (S_["pf"] != S_["pb"]), k, 0.0)
        return B + k[:, None] * qrot(q, S_["nrm"].astype(float))

    def _volfix(self, d, P):
        F = d["F"]; a, b, c = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]; v = (a * np.cross(b, c)).sum() / 6
        fn = np.cross(b - a, c - a) / 6; N = np.zeros_like(P)
        for k in range(3): np.add.at(N, F[:, k], fn)
        nl = np.linalg.norm(N, axis=1); den = (d["vfixW"] * nl).sum()
        if den < 1e-6: return P, 0.0
        dl = max(-6, min(6, (d["V0"] - v) / den)); nl[nl == 0] = 1
        return P + (d["vfixW"] * dl / nl)[:, None] * N, abs(d["V0"] - v) / abs(d["V0"])

    def _lerp(self, xs, ys, x):                            # body.js lerpAt, vectorised
        n = len(xs); k = np.clip(np.searchsorted(xs[1:n - 1], x, side="left"), 0, n - 2)
        u = (x - xs[k]) / (xs[k + 1] - xs[k] + 1e-9); out = ys[k] + u * (ys[k + 1] - ys[k])
        return np.where(x <= xs[0], ys[0], np.where(x >= xs[-1], ys[-1], out))

    def _rt(self, f, s_, th):
        K, sk = f["K"], f["sk"]; k = np.clip(np.searchsorted(sk[1:K - 1], s_, side="left"), 0, K - 2)
        u = np.clip((s_ - sk[k]) / (sk[k + 1] - sk[k] + 1e-9), 0, 1)
        a = (th + math.pi) / (2 * math.pi) * 16 - 0.5; a0 = np.floor(a); v = a - a0; j0 = (a0.astype(int) % 16 + 16) % 16; j1 = (j0 + 1) % 16
        RT = f["RT"]; return (1 - u) * ((1 - v) * RT[k, j0] + v * RT[k, j1]) + u * ((1 - v) * RT[k + 1, j0] + v * RT[k + 1, j1])

    def posed(self, pose, act=None, relax=None, muscles=False):
        ctx = self._ctx(pose, act); out = {}
        sk = self.skin
        E = ctx["segs"][2][0] @ np.array(self.L["elbow"]); ang = math.acos(max(-1, min(1, -E[1] / np.linalg.norm(E)))) / D2R
        al = smooth01(15, 55, ang) if relax is None else relax
        rest = sk["rest0"].copy()
        if len(sk["rlxi"]): rest[sk["rlxi"]] += al * sk["rlxd"]
        for d in self.dyn:
            R = rest if d is sk else d["rest"]
            B, q = self._cor(d, R, ctx, want_q="shm" in d)
            P = B
            if "fus" in d: P = self._fusiform(d, B, ctx)
            elif "shm" in d: P = self._sheet(d, B, q, ctx)
            if "vfixW" in d:
                P, err = self._volfix(d, P)
                if err > 0.015: P, _ = self._volfix(d, P)
            out[id(d)] = (P, B, q)
        P, B, _ = out[id(sk)]; P = P.copy()
        # Delta Mush
        m = sk["mush"]; S, N = self._mush_smooth(sk, P, al); L_ = m["list"]; t, b, n_ = self._frames(sk, S, N, L_)
        c = m["C0"][L_] + al * (m["C1"][L_] - m["C0"][L_])
        qm = S[L_] + c[:, :1] * t + c[:, 1:2] * b + c[:, 2:] * n_
        P[L_] += m["amt"][L_, None] * (qm - P[L_])
        # skin height field over the muscles
        H = np.zeros(sk["n"]); bi = sk["bound"]; foj, fov, fow = sk["foj"][bi], sk["fov"][bi], sk["fow"][bi]
        for mi in np.unique(foj):
            md = self.moving[mi] if mi < len(self.moving) else None
            if md is None: continue
            sel = foj == mi; j = fov[sel]; MP, MB, Mq = out[id(md)]
            if "fus" in md and "state" in md["fus"]:
                f = md["fus"]; st = f["state"]; sj = f["s"][j]; xe, xb = f["x"][j, 1], f["x"][j, 2]; th = np.arctan2(xb, xe)
                sig = self._lerp(f["sk"], st["sc"], sj); sst = self._lerp(st["sN"], f["sk"], sig)
                es = np.where(xe > 0, self._lerp(f["sk"], st["aO"], sst), self._lerp(f["sk"], st["aD"], sst)); bs = self._lerp(f["sk"], st["aB"], sst)
                h = (self._rt(f, sst, th) * np.hypot(es * np.cos(th), bs * np.sin(th)) - self._rt(f, sj, th)) * f["mu"][j]
            elif "shm" in md:
                nrm = qrot(Mq[j], md["shm"]["nrm"][j].astype(float)); h = ((MP[j] - MB[j]) * nrm).sum(1)
            else: continue
            H[bi[sel]] = fow[sel] * h
        R_ = sk["region"]; A = sk["A"]
        for _ in range(4): T = A @ H; H[R_] = 0.5 * H[R_] + 0.5 * T[R_]
        Fr = sk["regionF"]; fn = np.cross(P[Fr[:, 1]] - P[Fr[:, 0]], P[Fr[:, 2]] - P[Fr[:, 0]]); Nn = np.zeros_like(P)
        for k in range(3): np.add.at(Nn, Fr[:, k], fn)
        nl = np.linalg.norm(Nn[R_], axis=1); nl[nl == 0] = 1; P[R_] += (H[R_] / nl)[:, None] * Nn[R_]
        # humeral-head guard
        g = sk["guard"]; r = np.linalg.norm(P[g], axis=1); rmin = sk["guardR"]; w = 4 * self.s
        m_ = (r < rmin + w) & (r >= 1e-6); fct = (rmin[m_] + w * np.exp((r[m_] - rmin[m_]) / w - 1)) / r[m_]; P[g[m_]] *= fct[:, None]
        self.last = dict(lift=ctx["lift"], act=ctx["ACT"], relax=al)
        if muscles: return P, {d["name"]: out[id(d)][0] for d in self.dyn if d is not sk}
        return P


_RIG = None
def _rig():
    global _RIG
    if _RIG is None: _RIG = Rig()
    return _RIG


def posed(pose, **kw):
    """(N, 3) posed render-skin vertices for pose dict(plane, elev, axial, flex, pron) (degrees)"""
    return _rig().posed(pose, **kw)


def __getattr__(name):                                     # BP.F, BP.V0, BP.ARMV, BP.ARMF, BP.SRC (lazy)
    if name in ("F", "V0", "ARMV", "ARMF", "SRC"): return getattr(_rig(), name)
    raise AttributeError(name)


if __name__ == "__main__":                                 # check against body.js (node, headless)
    import subprocess, sys, tempfile, time
    poses = [dict(plane=0, elev=6, axial=0, flex=12.5, pron=-90), dict(plane=30, elev=97, axial=-6, flex=12, pron=0), dict(plane=62, elev=52, axial=15, flex=128, pron=30),
             dict(plane=15, elev=95, axial=-65, flex=95, pron=0), dict(plane=0, elev=150, axial=0, flex=12, pron=0), dict(plane=90, elev=180, axial=0, flex=40, pron=-60)]
    with tempfile.TemporaryDirectory() as td:
        json.dump(poses, open(os.path.join(td, "p.json"), "w"))
        subprocess.run(["node", os.path.join(HERE, "..", "arm-rom", "export_posed_skin.mjs"), os.path.join(HERE, "body_mesh.json"), os.path.join(td, "p.json"), os.path.join(td, "o")], check=True, stdout=subprocess.DEVNULL)
        meta = json.load(open(os.path.join(td, "o.json"))); ref = np.fromfile(os.path.join(td, "o.bin"), np.float32).reshape(len(poses), meta["n"], 3)
    t0 = time.time(); rig = _rig(); t1 = time.time()
    for k, p in enumerate(poses):
        t2 = time.time(); P = rig.posed(p); dt = time.time() - t2; e = np.linalg.norm(P - ref[k], axis=1)
        print(f"{p}: max |numpy - body.js| {e.max():.4f} mm, mean {e.mean():.5f} mm, {dt * 1000:.0f} ms")
    print(f"load {1000 * (t1 - t0):.0f} ms; {len(rig.V0)} vertices, {len(rig.F)} faces, arm vertices {rig.ARMV.sum()}")
