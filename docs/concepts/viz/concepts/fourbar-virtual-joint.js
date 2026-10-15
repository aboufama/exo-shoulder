/* fourbar-virtual-joint - polycentric 3R: the champion's J2 hub replaced by a spherical four-bar 'virtual joint'
 * (catalogue fourbar-virtual-joint, models/fourbar-virtual-joint.py; modelling interrupted, no sweep yet: the model's
 * defaults). L1 (a V of straps from J1) carries pins p1 (ACTIVE: rocker-1 angle phi = the virtual J2 coordinate) and
 * p2; two crossed two-force rockers reach pins q1, q2 on L2 (the coupler), which carries J3 (ACTIVE, arm-fixed W).
 * Spherical Gruebler: 6 bodies, 6 revolutes, M = 3: J1, p1, J3 ACTIVE; p2, q1, q2 PASSIVE (set by the loop). Every
 * axis through GH. Pins sit d 20 deg up / down from the old J2 spot, spread +-12 deg, rockers crossed. Kinematics =
 * the model's exact IK: with L1 at rest the coupler's pose is a function of phi alone, closure <=> b . W_L(phi) = b . y
 * (a 1-D root on the design piece: monotone, both transmission angles in [25, 155], pins >= 15 deg apart), then J1 =
 * the azimuth of W_L(phi) to y about b and J3 = the arm's twist. Reference = the rest pose. Faces are schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { az: 2.4305071427308924, el: 80.67633718429899, a0: 76.90180446920043, a1: 66.74921235407174,
              wd: 86.32769021001913, wa: 21.829657347343378, branch: -1, d_up: 20, d_dn: 20, s_up: 12, s_dn: 12, crossed: 1,
              skew: 0, sing: 10, tmin: 25, pin_sep: 15, faces: [52.8, 74, 80, 71.85], hub_r: 10, pin_r: 7, stack: 12.25,
              neck_deg: 25, cuff_at: 165 };
  const mv = (p, t, a) => V.unit(V.add(V.scale(p, Math.cos(a * D)), V.scale(t, Math.sin(a * D))));
  const frame2 = (u, v) => M.fromCols(V.unit(u), V.unit(V.reject(v, V.unit(u))), V.cross(V.unit(u), V.unit(V.reject(v, V.unit(u)))));
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  // design at the reference (rest) configuration, scapula frame (model design())
  const b = K.bvec(P.az, P.el), W0 = K.wdir(P.wd, P.wa), Qr = Qof(K.makeCtx(K.KEYS[0].pose)), Wr = M.mulv(Qr, W0);
  const J2 = K.circInt(b, P.a0, Wr, P.a1, P.branch).p, mUp = V.unit(V.reject(b, J2)), mDn = V.unit(V.reject(Wr, J2));
  const sUp = V.unit(V.cross(J2, mUp)), sDn = V.unit(V.cross(mDn, J2)), pc = mv(J2, mUp, P.d_up), sg = P.crossed ? -1 : 1;
  const p1 = mv(pc, sUp, P.s_up), p2 = mv(pc, sUp, -P.s_up);
  const q1 = mv(mv(J2, mDn, P.d_dn + P.skew), sDn, sg * P.s_dn), q2 = mv(mv(J2, mDn, P.d_dn - P.skew), sDn, -sg * P.s_dn);
  const lam2 = V.angle(p2, q2), c12 = V.angle(q1, q2), F12 = frame2(q1, q2);
  const sigma = V.angle(K.circInt(p2, lam2, q1, c12, 1).p, q2) < 1e-4 ? 1 : -1;
  const e0 = V.unit(V.cross(W0, [1, 0, 0])), er = M.mulv(Qr, e0);
  /** the loop with L1 at rest, rocker-1 angle ph (deg): coupler pins, coupler rotation R, W_L, transmissions, validity */
  function loop(ph) {
    const Q1 = M.mulv(M.rot(p1, ph), q1), c = K.circInt(p2, lam2, Q1, c12, sigma), Q2 = c.p, R = M.mul(frame2(Q1, Q2), M.T(F12));
    const mu1 = V.angle(V.reject(p1, Q1), V.reject(Q2, Q1)), mu2 = V.angle(V.reject(p2, Q2), V.reject(Q1, Q2));
    const sep = Math.min(V.angle(p1, Q2), V.angle(p2, Q1));
    const ok = c.ok && Math.min(mu1, mu2) >= P.tmin && Math.max(mu1, mu2) <= 180 - P.tmin && sep >= P.pin_sep;
    return { Q1, Q2, R, WL: M.mulv(R, Wr), mu1, mu2, ok };
  }
  // the design piece: monotone, valid run of G(phi) = b . W_L around phi = 0; fold ends keep `sing` deg (model)
  const PH = [], G = []; for (let x = -180; x < 180; x += 0.25) { PH.push(x); G.push(V.dot(loop(x).WL, b)); }
  const okA = PH.map(x => loop(x).ok), i0 = PH.indexOf(0), dG = i => G[Math.min(i + 1, G.length - 1)] - G[Math.max(i - 1, 0)], s0 = Math.sign(dG(i0));
  let lo = i0, hi = i0;
  while (lo > 0 && okA[lo - 1] && Math.sign(dG(lo - 1)) === s0) lo--;
  while (hi < PH.length - 1 && okA[hi + 1] && Math.sign(dG(hi + 1)) === s0) hi++;
  const thOf = g => Math.acos(Math.max(-1, Math.min(1, g))) * K.R2D;
  let tlo = Math.min(thOf(G[lo]), thOf(G[hi])), thi = Math.max(thOf(G[lo]), thOf(G[hi]));
  for (const [j, nx] of [[lo, lo - 1], [hi, hi + 1]]) {
    if (nx >= 0 && nx < PH.length && okA[nx] && Math.sign(dG(nx)) !== s0) {
      if (Math.abs(thOf(G[j]) - tlo) <= Math.abs(thOf(G[j]) - thi)) tlo = thOf(G[j]) + P.sing; else thi = thOf(G[j]) - P.sing;
    }
  }
  function phiOf(gy) {                                          // the unique root on the piece (clamped at its ends)
    let a = PH[lo], c = PH[hi], ga = G[lo] - gy;
    if (Math.sign(ga) === Math.sign(G[hi] - gy)) return Math.abs(ga) < Math.abs(G[hi] - gy) ? a : c;
    for (let i = 0; i < 50; i++) { const m = (a + c) / 2, gm = V.dot(loop(m).WL, b) - gy; if (Math.sign(gm) === Math.sign(ga)) { a = m; ga = gm; } else c = m; }
    return (a + c) / 2;
  }
  /** q = [J1, phi (p1, virtual J2), J3, p2, q1, q2 (passive pin angles, reported)] */
  function fk(q) {
    const L = loop(q[1]), R1 = M.rot(b, q[0]), RL2 = M.mul(R1, L.R), y = M.mulv(RL2, Wr);
    return Object.assign(L, { R1, RL2, y, E: M.mul(M.mul(M.rot(y, q[2]), RL2), Qr) });
  }
  function solve(ctx) {
    const Q = Qof(ctx), y = M.mulv(Q, W0), ph = phiOf(V.dot(y, b)), L = loop(ph);
    const th1 = K.axisAngle(b, L.WL, y), RL2 = M.mul(M.rot(b, th1), L.R), th3 = K.axisAngle(y, M.mulv(RL2, er), M.mulv(Q, e0));
    return [th1, ph, th3, K.axisAngle(p2, q2, L.Q2), K.axisAngle(L.Q1, p1, L.Q2) - K.axisAngle(q1, p1, q2), K.axisAngle(L.Q2, p2, L.Q1) - K.axisAngle(q2, p2, q1)];
  }

  K.register({
    id: 'fourbar-virtual-joint',
    name: 'Polycentric 3R (four-bar virtual J2)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'p1 rocker (virtual J2)', 'J3', 'p2 rocker (passive)', 'q1 pin (passive)', 'q2 pin (passive)'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => M.rotErrDeg(M.mul(ctx.S, fk(q).E), ctx.H),
    check: (q, ctx) => {
      const th = V.angle(M.mulv(Qof(ctx), W0), b), L = loop(q[1]);
      if (!L.ok) return `four-bar transmission ${Math.min(L.mu1, L.mu2).toFixed(0)} deg (toggle)`;
      if (th < tlo || th > thi) return 'arm axis outside the virtual joint\'s band (fold / toggle)';
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q), W = d => M.mulv(ctx.S, d), F = P.faces, h = P.stack, ng = P.neck_deg * D, harm = ctx.armAxis;
      const B = W(b), P1 = W(M.mulv(f.R1, p1)), P2 = W(M.mulv(f.R1, p2)), Q1 = W(M.mulv(f.R1, f.Q1)), Q2 = W(M.mulv(f.R1, f.Q2)), Y = W(f.y);
      const nk = V.unit(V.add(V.scale(Y, Math.cos(ng)), V.scale(V.unit(V.reject(harm, Y)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[3] + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const pin = (c, role, name, r) => ({ kind: 'hub', role, name, c: V.scale(c, r), axis: c, r: P.pin_r, h: 8 });
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(B, F[0] - 3), z: B, x: W([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(B, F[0]), axis: B, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'L1 strap to p1', u: B, v: P1, r0: F[0] + 7, r1: F[1], r: 2.5 },
        { kind: 'arc', role: 'link', name: 'L1 strap to p2', u: B, v: P2, r0: F[0] + 7, r1: F[1], r: 2.5 },
        pin(P1, 'active', 'p1 (virtual J2, sensed)', F[1]),
        pin(P2, 'passive', 'p2', F[1]),
        { kind: 'arc', role: 'link', name: 'rocker 1', u: P1, v: Q1, r0: F[1] + 5, r1: F[2] - 3, r: 2 },
        { kind: 'arc', role: 'link', name: 'rocker 2 (crossed)', u: P2, v: Q2, r0: F[1] + 9, r1: F[2] + 1, r: 2 },
        pin(Q1, 'passive', 'q1', F[2]),
        pin(Q2, 'passive', 'q2', F[2]),
        { kind: 'arc', role: 'link', name: 'L2 (coupler) strap q1', u: Q1, v: Y, r0: F[2] + 6, r1: F[3] + h + 1, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'L2 (coupler) strap q2', u: Q2, v: Y, r0: F[2] + 6, r1: F[3] + h + 1, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(Y, F[3]), axis: Y, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: Y, v: nk, r0: F[3] + 1, r1: F[3] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
