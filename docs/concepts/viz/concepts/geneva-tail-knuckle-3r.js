/* geneva-tail-knuckle-3r - the PLAIN spherical chain (J1 / J2 / J3 axes through GH) with link 1 split by a passive O20
 * knuckle K (clock spring onto stop A) that is SLAVED to q2 by a one-tooth Geneva drive: link 2 continues past hub 2 as
 * a rigid tail whose MR63ZZ roller pushes one flank fixed to link 1a. Inside the window [thLo, thHi] of the J1-J3 angle
 * K sits on stop A (a rigid 3R); past thHi the roller opens K by the exact contact law (a1e(th) tabulated from
 * docs/concepts/models/geneva-tail-knuckle-3r.py), so the J1, J2, J3 encoders give the pose (3 active, K never read).
 * The folded side has no tooth (J2 dowel). Hub / link levels are the model's fitted medians on Bench(60,160).
 * Placeholder: LA1 seats, beside embodiment (d 14, psi_c 8). Red = outside the drive's range (folded dowel / past stop B). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const G = {"u1": [0.07713, 0.90926, 0.40902], "u3": [-0.07773, -0.69267, 0.71706], "a1": 43.8793, "a2": 71.1868, "b1": 30.6983, "b2": 56.392, "sigma": -1, "sK": -1, "thLo": 36.223, "thHi": 108.972, "lawTh": [108.972, 109.121, 109.424, 109.732, 110.045, 110.363, 110.685, 110.849, 111.179, 111.513, 111.853, 112.197, 112.546, 112.899, 113.078, 113.438, 113.803, 114.172, 114.546, 114.923, 115.113, 115.497, 115.884, 116.276, 116.67, 117.069, 117.47, 117.672, 118.078, 118.487, 118.899, 119.314, 119.73, 119.939, 120.359, 120.781, 121.204, 121.629, 122.055, 122.482], "lawA1e": [43.879, 44.03, 44.334, 44.642, 44.953, 45.268, 45.586, 45.746, 46.07, 46.396, 46.725, 47.058, 47.393, 47.732, 47.902, 48.244, 48.589, 48.936, 49.286, 49.637, 49.814, 50.168, 50.525, 50.882, 51.242, 51.602, 51.964, 52.145, 52.508, 52.871, 53.236, 53.6, 53.964, 54.147, 54.511, 54.875, 55.239, 55.602, 55.964, 56.325], "coef": [0.94219, -0.7264, -0.1614], "coefL": [-0.5828, 0.67778, -0.93823], "emb": "beside", "lv": {"hub1": 51.0, "hubK": 55.0, "hub2": 64.1, "hub3": 104.1, "link1b": 55.0, "neck": 104.1, "roller": 135.0, "lug": 59.0, "link1a": 55.5, "link2": 99.7, "tail": 136.1}, "mx": {"hub1": 51.0, "hubK": 55.0, "hub2": 64.1, "hub3": 104.1, "link1b": 64.1, "neck": 106.1, "roller": 152.1, "lug": 59.0, "link1a": 59.0, "link2": 113.1, "tail": 155.1}, "capK": 6.0, "inv3": 0, "tailw": 8.0, "lug": 22.0, "score": {"gap": 59.9, "plain": 54.17, "reach": 0.6937, "inband14": 0.6323}};
  const P = { a1: G.a1, a2: G.a2, b1: G.b1, b2: G.b2, sigma: G.sigma, sK: G.sK, thLo: G.thLo, thHi: G.thHi, emb: G.emb };
  const u1 = V.unit(G.u1), u3 = V.unit(G.u3), lv = G.lv, mx = G.mx, hub = 12.25, rad = 10;
  const thMax = G.lawTh.length ? G.lawTh[G.lawTh.length - 1] : G.thHi;
  function a1eOf(th) {
    if (th >= G.thLo && th <= G.thHi) return { a1e: G.a1, state: 0, ok: true };
    if (th < G.thLo) return { a1e: G.a1, state: -1, ok: false };
    const T = G.lawTh, A = G.lawA1e, n = T.length;
    if (!n || th > thMax) return { a1e: n ? A[n - 1] : G.a1, state: 1, ok: false };
    let j = 0; while (j < n - 2 && T[j + 1] < th) j++;
    const s = Math.max(0, Math.min(1, (th - T[j]) / Math.max(T[j + 1] - T[j], 1e-9)));
    return { a1e: A[j] + s * (A[j + 1] - A[j]), state: 1, ok: true };
  }
  function axes(Q) {                          // scapula-frame axes at arm rotation Q (= S^T H)
    const w = M.mulv(Q, u3), th = V.angle(w, u1), L = a1eOf(th);
    const p2 = K.circInt(u1, L.a1e, w, G.a2, G.sigma).p, pK = K.circInt(u1, G.b1, p2, G.b2, G.sK).p;
    return { w, th, L, p2, pK };
  }
  const H0 = axes(M.I3()), U1 = u1, U2 = H0.p2, UK = H0.pK, U3 = u3, v3 = V.unit(V.cross(U3, [0.3, 0.5, 0.8]));
  function chain(q) {
    const R1 = M.rot(U1, q[0]), R1b = M.mul(R1, M.rot(UK, q[1])), R12 = M.mul(R1b, M.rot(U2, q[2])), R123 = M.mul(R12, M.rot(U3, q[3]));
    return { R1, R1b, R12, R123 };
  }
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function solve(ctx) {
    const Q = Qof(ctx), A = axes(Q);
    const q1 = K.axisAngle(U1, UK, A.pK), R1 = M.rot(U1, q1);
    const kap = K.axisAngle(UK, U2, M.mulv(M.T(R1), A.p2)), R1b = M.mul(R1, M.rot(UK, kap));
    const q2 = K.axisAngle(U2, U3, M.mulv(M.T(R1b), A.w)), R12 = M.mul(R1b, M.rot(U2, q2));
    const q3 = K.axisAngle(U3, v3, M.mulv(M.mul(M.T(R12), Q), v3));
    return [q1, kap, q2, q3];
  }
  const tipOf = (p2, w, c) => V.unit(V.add(V.add(V.scale(p2, c[0]), V.scale(w, c[1])), V.scale(V.unit(V.cross(p2, w)), c[2])));
  const C = {
    id: 'geneva-tail-knuckle-3r', name: 'Geneva-tail knuckle on the plain spherical chain (3 active, K slaved to q2, not read)',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'K (passive, slaved to q2 by the tail)', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg'],
    solve: (ctx, qPrev) => solve(ctx),
    residual: (q, ctx) => M.rotErrDeg(M.mul(ctx.S, chain(q).R123), ctx.H),
    check: (q, ctx) => {
      const A = axes(Qof(ctx));
      if (!A.L.ok) return A.L.state === 1 ? 'past the drive stop B (law end)' : 'folded side: J2 on its dowel (no tooth)';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = v => M.mulv(S, v), X = chain(q), Q = Qof(ctx);
      const p1 = U1, pK = M.mulv(X.R1, UK), p2 = M.mulv(X.R1b, U2), w = M.mulv(X.R12, U3);
      const out = [
        { kind: 'plate', role: 'fixed-scapula', name: 'base on the scapula handler (at the J1 hub ring)', c: V.scale(W(p1), lv.hub1 - 3), z: W(p1), x: ctx.attach.scapDir([1, 0, 0]), size: [30, 24], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O20, axis on a GH ray)', c: V.scale(W(p1), lv.hub1), axis: W(p1), r: rad, h: hub },
        { kind: 'arc', role: 'link', name: 'link 1a (12 x 3 Ti strap, J1 -> K; carries the tooth flank)', u: W(p1), v: W(pK), r0: lv.link1a + 1.5, r1: lv.link1a + 1.5, r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'K (O20, passive, clock-spring cap, stop A; slaved by the tail roller)', c: V.scale(W(pK), lv.hubK), axis: W(pK), r: rad, h: hub + G.capK },
        { kind: 'arc', role: 'link', name: 'link 1b (12 x 3 Ti strap, K -> J2)', u: W(pK), v: W(p2), r0: lv.link1b + 1.5, r1: lv.link1b + 1.5, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O20, axis on a GH ray; folded dowel, drive stop B)', c: V.scale(W(p2), lv.hub2), axis: W(p2), r: rad, h: hub },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti strap, J2 -> J3)', u: W(p2), v: W(w), r0: lv.link2 + 1.5, r1: lv.link2 + 1.5, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20, humerus-fixed axis through GH)', c: V.scale(W(w), lv.hub3), axis: W(w), r: rad, h: hub },
        { kind: 'link', role: 'link', name: 'neck (14 x 6, member 3) to BOTTOM', a: V.scale(W(w), lv.hub3 + 3), b: ctx.attach.onArm(150, 48), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(ctx.armAxis, 155), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
      if (G.coef) {
        const tip = tipOf(p2, w, G.coef), rr = lv.roller !== undefined ? lv.roller : lv.hubK + hub + G.capK + 1.2;
        out.push({ kind: 'arc', role: 'link', name: 'tail (8 x 3, rigid with link 2, past hub 2)', u: W(p2), v: W(tip), r0: (lv.tail || rr + 3) + 1.5, r1: (lv.tail || rr + 3) + 1.5, r: 2.0 });
        out.push({ kind: 'hub', role: 'passive', name: 'MR63ZZ roller on the tail tip (pushes the flank on link 1a)', c: V.scale(W(tip), rr), axis: W(tip), r: 4, h: 3 });
      }
      if (G.coefL && G.emb === 'beside') {
        const fl = V.unit(V.add(V.add(V.scale(pK, G.coefL[0]), V.scale(p1, G.coefL[1])), V.scale(V.unit(V.cross(pK, p1)), G.coefL[2])));
        const g = G.lug / 70, e = V.unit(V.add(V.scale(pK, Math.cos(g)), V.scale(fl, Math.sin(g))));
        out.push({ kind: 'arc', role: 'link', name: 'tooth lug on link 1a (the flank the roller pushes)', u: W(pK), v: W(e), r0: (lv.lug || lv.hubK + 4) + 1.5, r1: (lv.lug || lv.hubK + 4) + 1.5, r: 1.8 });
      }
      return out;
    }
  };
  K.register(C);
})();
