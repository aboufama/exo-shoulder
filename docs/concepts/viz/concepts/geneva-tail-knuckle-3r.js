/* geneva-tail-knuckle-3r - the PLAIN spherical chain (J1 / J2 / J3 axes through GH) with link 1 split by a passive O20
 * knuckle K (clock spring onto stop A) that is SLAVED to q2 by a one-tooth Geneva drive: link 2 continues past hub 2 as
 * a rigid tail whose MR63ZZ roller pushes one flank fixed to link 1a. Inside the window [thLo, thHi] of the J1-J3 angle
 * K sits on stop A (a rigid 3R); past thHi the roller opens K by the exact contact law (a1e(th) tabulated from
 * docs/concepts/models/geneva-tail-knuckle-3r.py), so the J1, J2, J3 encoders give the pose (3 active, K never read).
 * The folded side has no tooth (J2 dowel). Hub / link levels are the model's fitted medians on Bench(60,160).
 * Best configuration: farm CMA stream s4 (11270 evaluations over 6 streams), fast near-touch gap 39.36: LA1-family seats, beside embodiment (roller 19.5 mm from K's axis, lug on link 1a), onset 13.3 deg from the stretched fold. Red = outside the drive's range (folded dowel / past stop B). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const G = {"u1": [0.0167, 0.8912, 0.4533], "u3": [-0.04911, -0.80566, 0.59034], "a1": 40.8271, "a2": 74.3853, "b1": 33.4351, "b2": 55.698, "sigma": -1, "sK": -1, "thLo": 40.753, "thHi": 101.95, "lawTh": [101.95, 102.575, 103.223, 103.895, 104.589, 105.308, 106.05, 106.815, 107.603, 108.414, 109.246, 110.1, 110.973, 111.866, 112.777, 113.704, 114.646, 115.602, 116.569, 117.546, 118.696, 119.689, 120.685, 121.682, 122.68, 123.676, 124.668, 125.654, 126.632, 127.602, 128.56, 129.506, 130.438, 131.355, 132.255, 133.138, 134.003, 134.847, 135.672, 136.606], "lawA1e": [40.827, 41.45, 42.089, 42.744, 43.414, 44.098, 44.797, 45.508, 46.23, 46.963, 47.706, 48.456, 49.213, 49.975, 50.741, 51.509, 52.277, 53.045, 53.809, 54.569, 55.448, 56.194, 56.93, 57.656, 58.371, 59.072, 59.76, 60.433, 61.091, 61.732, 62.357, 62.964, 63.554, 64.126, 64.68, 65.215, 65.733, 66.233, 66.715, 67.255], "coef": [0.94734, -0.66283, -0.03531], "coefL": [-0.58165, 0.69699, -0.92332], "emb": "beside", "lv": {"hub1": 51.0, "hubK": 56.0, "hub2": 63.6, "hub3": 119.0, "link1b": 56.0, "neck": 119.0, "link1a": 54.1, "link2": 97.9, "lug": 60.0, "roller": 88.0, "tail": 90.1}, "mx": {"hub1": 51.0, "hubK": 56.0, "hub2": 63.6, "hub3": 119.0, "link1b": 63.6, "neck": 119.0, "link1a": 60.0, "link2": 131.3, "lug": 60.0, "roller": 100.0, "tail": 104.0}, "capK": 6.0, "inv3": 0, "tailw": 8.0, "lug": 50.0, "score": {"gap": 39.36, "plain": 39.36, "reach": 0.825, "inband14": 0.6727}};
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
