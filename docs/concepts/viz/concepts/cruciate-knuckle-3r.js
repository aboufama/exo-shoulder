/* cruciate-knuckle-3r - a spherical 3R whose three revolutes are cruciate-ligament KNUCKLES: two Ti ligament bars
 * crossing in an X between the butted ends of adjacent members (like the knee), all pivot axes radial through GH
 * (catalogue cruciate-knuckle-3r; ideated, no bench model yet: the model_spec). Seed: the final 3R (r18 s1392 #1,
 * b = bvec(32.6, 80.6), arcs 77.4 / 81.4, W = wdir(71.4, 4.8), branch -1) at the loop's rest pose: j1 = b, j2, j3 =
 * its axes there, T0 = the rest arm orientation. Knuckle k (the spec's idealisation: rolling equal pitch cones, which
 * the symmetric crossed four-bar approximates): Rot(j_k, q) -> Rot(c_k, q / 2) Rot(c'_k, q / 2), c_k = Rot(n_k, -beta)
 * j_k (proximal centrode, in member k-1), c'_k = Rot(n_k, +beta) j_k (distal, in member k), n_k = unit(j_k x j_k+1)
 * (k = 3: j2 x j3, so c'_3 sits in the arm piece). 3 ACTIVE (one input pivot per knuckle) + 9 PASSIVE (the other 3
 * pivots of each loop, set by closure); numeric IK on q1..q3 from rest (q = 0). The ligaments are drawn between their
 * real pivots on the posed members, so the idealisation's error shows: measured on the loop, a ligament drifts at most
 * 2.5 mm from its rest length (`drift(q)`; a real crossed four-bar holds it at 0, its centrodes are ellipses, not
 * circles). Members one layer at rho 62 mm; ligaments at rho + 7 / + 10; schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 32.6, el: 80.6, a: [77.4, 81.4], w: [71.4, 4.8], branch: -1, beta: 6, rho: 62, spread: 7.5, q_max: 70,
              sing_deg: 10, neck_deg: 25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);
  const ctx0 = K.makeCtx(K.motion(240)[0].pose, 0), f0 = C.fk(C.solve(ctx0), ctx0);
  const toS = d => M.mulv(M.T(ctx0.S), d), j = [toS(f0.p1), toS(f0.p2), toS(f0.p3)], T0 = M.mul(M.T(ctx0.S), ctx0.H);
  const n = [V.unit(V.cross(j[0], j[1])), V.unit(V.cross(j[1], j[2])), V.unit(V.cross(j[1], j[2]))];
  const kn = [0, 1, 2].map(k => ({ c: M.mulv(M.rot(n[k], -P.beta), j[k]), c2: M.mulv(M.rot(n[k], P.beta), j[k]) }));
  const q3r = C.solve(ctx0), med = (() => {                      // median 3R joint travel over the loop (the q_max reference)
    const d = K.motion(240).map(f => { const c = K.makeCtx(f.pose, f.t), q = C.solve(c); return q.map((x, k) => K.wrap180(x - q3r[k])); });
    return [0, 1, 2].map(k => d.map(x => x[k]).sort((a, b) => a - b)[d.length >> 1]);
  })();
  function members(q) {
    const B = [M.I3()]; let T = B[0];
    for (let k = 0; k < 3; k++) { T = M.mul(M.mul(T, M.rot(kn[k].c, q[k] / 2)), M.rot(kn[k].c2, q[k] / 2)); B.push(T); }
    return B;
  }
  const off = (d, k, s) => V.unit(V.madd(d, n[k], s * P.spread / P.rho));      // pivot: a centrode centre +- the spread
  const pivots = (B, k) => [off(kn[k].c, k, 1), off(kn[k].c, k, -1)].map(d => M.mulv(B[k], d))
    .concat([off(kn[k].c2, k, 1), off(kn[k].c2, k, -1)].map(d => M.mulv(B[k + 1], d)));
  const ligLen = (B, k, i) => { const p = pivots(B, k); return V.norm(V.sub(V.scale(p[i], P.rho + 6 + 3 * i), V.scale(p[3 - i], P.rho + 6 + 3 * i))); };
  const L0 = [0, 1, 2].map(k => [0, 1].map(i => ligLen(members([0, 0, 0]), k, i)));
  /** ligament length drift of the rolling idealisation (mm): a real crossed four-bar keeps it 0 */
  const drift = q => { const B = members(q); return Math.max(...[0, 1, 2].map(k => Math.max(...[0, 1].map(i => Math.abs(ligLen(B, k, i) - L0[k][i]))))); };

  K.register({
    id: 'cruciate-knuckle-3r',
    name: 'Cruciate-ligament knuckles 3R',
    dof: { active: 3, passive: 9 },
    params: P,
    q0: [0, 0, 0],
    qNames: ['knuckle 1', 'knuckle 2', 'knuckle 3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    residual: (q, ctx) => M.rotErrDeg(M.mul(members(q)[3], T0), M.mul(M.T(ctx.S), ctx.H)),
    check: (q, ctx) => {
      const mg = C.margin(ctx);
      if (mg < P.sing_deg) return mg < 0 ? 'the seed 3R cannot close here' : `within ${mg.toFixed(0)} deg of the chain's fold`;
      for (let k = 0; k < 3; k++) if (Math.abs(q[k] - med[k]) > P.q_max) return `knuckle ${k + 1} past ${P.q_max} deg from its median`;
      return null;
    },
    drift,
    parts: (q, ctx) => {
      const B = members(q), S = ctx.S, W = d => M.mulv(S, d), R = P.rho, out = [];
      out.push({ kind: 'plate', role: 'fixed-scapula', name: 'base pad (handler)', c: W(V.scale(M.mulv(M.rot(n[0], -3 * P.beta), j[0]), R - 3)),
                 z: W(j[0]), x: W(V.cross(n[0], j[0])), size: [30, 20], t: 3 });
      const ends = [[kn[0].c2, kn[1].c], [kn[1].c2, kn[2].c]];
      for (let k = 0; k < 3; k++) {
        const p = pivots(B, k).map(W);
        p.forEach((d, i) => out.push({ kind: 'hub', role: i === 0 ? 'active' : 'passive', name: `knuckle ${k + 1} pivot ${i + 1}${i === 0 ? ' (input, sensed)' : ''}`,
                                       c: V.scale(d, R + 3), axis: d, r: 4, h: 7 + (i % 2 ? 3 : 0) }));
        out.push({ kind: 'link', role: 'link', name: `knuckle ${k + 1} ligament a`, a: V.scale(p[0], R + 7), b: V.scale(p[3], R + 7), r: 2 });
        out.push({ kind: 'link', role: 'link', name: `knuckle ${k + 1} ligament b`, a: V.scale(p[1], R + 10), b: V.scale(p[2], R + 10), r: 2 });
        if (k < 2) out.push({ kind: 'arc', role: 'link', name: `member ${k + 1} (one layer)`, u: W(M.mulv(B[k + 1], ends[k][0])),
                              v: W(M.mulv(B[k + 1], ends[k][1])), r0: R + 1.5, r1: R + 1.5, r: 3 });
      }
      const harm = ctx.armAxis, a3 = W(M.mulv(B[3], kn[2].c2)), ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(a3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, a3)), Math.sin(ng)))), neckEnd = V.scale(nk, R + 1.5);
      const cuffC = V.scale(harm, P.cuff_at);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm piece', u: a3, v: nk, r0: R + 1.5, r1: R + 1.5, r: 3 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'arm piece to cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), r: 3 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
