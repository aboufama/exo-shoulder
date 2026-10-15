/* cam-unfold-4th - the champion spherical 3R with a slaved KNEE in link 2 (catalogue cam-unfold-4th,
 * models/cam-unfold-4th.py; modelling interrupted, no sweep yet). Link 2 is split at f = 0.5 by J4, a cross-spring
 * flexure pivot (axis p4 through GH, +-18 deg) whose angle is SLAVED q4 = c(q2) by a groove face cam around J2 on
 * link 1 (follower + pushrod along link 2a + crank on 2b). 3 ACTIVE hubs (J1, J2, J3) + 1 PASSIVE slaved knee: J4
 * cannot move unless J2 moves. Cam law: one of the model's check designs (bent neutral c0 = -18 deg, link 2 laid out
 * dS = 12 deg longer, knots 0 / 6 / 12 / 18 / 18 deg over the straight-knee J2 range: the knee opens as J2 turns, so
 * link 2 lengthens). Closed form = the model's IK: for a trial knee angle the 3R closure gives q2, the knee angle is
 * a root of c(q2(q4)) - q4 on a 0.5 deg grid (secant polish), the root nearest the previous frame. Joint values are
 * measured from the rest pose; faces follow the champion's (J2 93 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { az: 2.4305071427308924, el: 80.67633718429899, a1: 76.90180446920043, a2: 66.74921235407174,
              w: [86.32769021001913, 21.829657347343378], branch: -1, f: 0.5, dS: 12, c0: -18, knots: [0, 6, 12, 18, 18],
              rng: 18, sing: 10, faces: [52.8, 93.2, 86, 78.5], hub_r: 10, stack: 12.25, cam_r: 14, neck_deg: 25, cuff_at: 165 };
  const p1 = K.bvec(P.az, P.el), W0 = K.wdir(P.w[0], P.w[1]), Sarc = P.a2 + P.dS, al = P.f * Sarc, be = Sarc - al;
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  /** knee table (link 2a frame): effective arc a2e and the angle phi at p2 from p4 to p3, for knee angle q4 (deg) */
  function knee(q4) {
    const c = Math.cos(q4 * D), s = Math.sin(q4 * D), x = Math.cos((al + be) * D) * c + Math.cos(al * D) * Math.cos(be * D) * (1 - c);
    const y = Math.sin((al + be) * D) * c + Math.sin(al * D) * Math.cos(be * D) * (1 - c), z = Math.sin(be * D) * s;
    return { a2e: Math.acos(Math.max(-1, Math.min(1, x))) * K.R2D, phi: Math.atan2(z, y) * K.R2D };
  }
  /** closure for arm axis p3 and knee angle q4: axes p1, p2, p4, p3, J2 angle psi (p1 -> p4 at p2), validity */
  function closure(p3, q4) {
    const k = knee(q4), c = K.circInt(p1, P.a1, p3, k.a2e, P.branch), p2 = c.p;
    const ok = c.ok && K.foldMargin(p1, p3, P.a1, k.a2e) >= P.sing;
    const t4 = M.mulv(M.rot(p2, -k.phi), V.unit(V.reject(p3, p2)));
    const p4 = V.add(V.scale(p2, Math.cos(al * D)), V.scale(t4, Math.sin(al * D)));
    return { p: [p1, p2, p4, p3], psi: K.axisAngle(p2, p1, p3) - k.phi, ok };
  }
  // the cam law c(q2): monotone cubic (pchip) through the knots spread over the straight-knee J2 range of the loop
  const rest = K.makeCtx(K.KEYS[0].pose), loop = K.motion(120).map(f => Qof(K.makeCtx(f.pose)));
  const ref = closure(M.mulv(Qof(rest), W0), P.c0).psi;
  let lo = 1e9, hi = -1e9;
  for (const Q of loop) { const c = closure(M.mulv(Q, W0), P.c0); if (c.ok) { const x = K.wrap180(c.psi - ref); lo = Math.min(lo, x); hi = Math.max(hi, x); } }
  const kx = P.knots.map((_, i) => lo + (hi - lo) * i / (P.knots.length - 1)), ky = P.knots, n = ky.length;
  const dl = kx.slice(1).map((x, i) => (ky[i + 1] - ky[i]) / (x - kx[i]));
  const md = ky.map((_, i) => i === 0 ? dl[0] : i === n - 1 ? dl[n - 2] : (dl[i - 1] * dl[i] <= 0 ? 0 : 2 / (1 / dl[i - 1] + 1 / dl[i])));
  function cam(q2) {
    const x = Math.max(lo, Math.min(hi, q2)); let i = Math.min(n - 2, Math.max(0, Math.floor((x - lo) / (hi - lo) * (n - 1))));
    const h = kx[i + 1] - kx[i], t = (x - kx[i]) / h, t2 = t * t, t3 = t2 * t;
    return P.c0 + (2 * t3 - 3 * t2 + 1) * ky[i] + (t3 - 2 * t2 + t) * h * md[i] + (-2 * t3 + 3 * t2) * ky[i + 1] + (t3 - t2) * h * md[i + 1];
  }
  const rres = (p3, q4) => { const c = closure(p3, q4); return { r: cam(K.wrap180(c.psi - ref)) - q4, c }; };
  /** knee roots for one arm axis: all roots in the flexure range, the one nearest `guess` */
  function knee_root(p3, guess) {
    let best = null, a = rres(p3, P.c0 - P.rng);
    for (let g = P.c0 - P.rng + 0.5; g <= P.c0 + P.rng + 1e-9; g += 0.5) {
      const b = rres(p3, g);
      if (a.c.ok && b.c.ok && Math.sign(a.r) !== Math.sign(b.r)) {
        let x0 = g - 0.5, x1 = g, r0 = a.r, r1 = b.r;
        for (let i = 0; i < 30 && Math.abs(r1) > 1e-10; i++) { const x2 = x1 - r1 * (x1 - x0) / (r1 - r0 || 1e-12); x0 = x1; r0 = r1; x1 = x2; r1 = rres(p3, x1).r; }
        if (!best || Math.abs(x1 - guess) < Math.abs(best - guess)) best = x1;
      }
      a = b;
    }
    return best;
  }
  // home = the rest configuration
  const Qh = Qof(rest), p3h = M.mulv(Qh, W0), q4h = knee_root(p3h, cam(0)), H0 = closure(p3h, q4h), U = H0.p, off = H0.psi - ref;
  function angles(Pa, Q) {                                     // PoE joint values (deg) of posed axes, order J1 J2 J4 J3
    const q = []; let R = M.I3();
    for (let k = 0; k < 3; k++) { q.push(K.axisAngle(U[k], U[k + 1], M.mulv(M.T(R), Pa[k + 1]))); R = M.mul(R, M.rot(U[k], q[k])); }
    const v = V.perp(U[3]); q.push(K.axisAngle(U[3], v, M.mulv(M.mul(M.mul(M.T(R), Q), M.T(Qh)), v))); return q;
  }
  function fk(q) {
    const Rs = [M.rot(U[0], q[0])]; for (let k = 1; k < 4; k++) Rs.push(M.mul(Rs[k - 1], M.rot(U[k], q[k])));
    return { p: [U[0], M.mulv(Rs[0], U[1]), M.mulv(Rs[1], U[2]), M.mulv(Rs[2], U[3])], E: M.mul(Rs[3], Qh) };
  }
  function solve(ctx, qPrev) {
    const Q = Qof(ctx), p3 = M.mulv(Q, W0), guess = qPrev ? q4h + qPrev[2] : q4h, x = knee_root(p3, guess);
    if (x == null) return qPrev ? qPrev.slice() : [0, 0, 0, 0];
    return angles(closure(p3, x).p, Q);
  }

  K.register({
    id: 'cam-unfold-4th',
    name: 'Cam-unfolding link (slaved knee)',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => solve(ctx, null),
    qNames: ['J1', 'J2', 'J4 knee (passive, = c(J2))', 'J3'], qUnits: ['deg', 'deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => M.rotErrDeg(M.mul(ctx.S, fk(q).E), ctx.H).concat([cam(q[1] + off) - (q4h + q[2])]),
    check: (q, ctx) => {
      const p = fk(q).p, k = knee(q4h + q[2]), m = K.foldMargin(p[0], p[3], P.a1, k.a2e);
      if (m < 0) return 'J2 cannot close: the arm axis is out of reach';
      if (m < P.sing) return `J2 within ${m.toFixed(0)} deg of its fold`;
      if (Math.abs(q4h + q[2] - P.c0) > P.rng + 1e-6) return 'knee flexure past its range';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = d => M.mulv(S, d), F = P.faces, h = P.stack, p = fk(q).p.map(W);
      const harm = ctx.armAxis, ng = P.neck_deg * D;
      const nk = V.unit(V.add(V.scale(p[3], Math.cos(ng)), V.scale(V.unit(V.reject(harm, p[3])), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[3] + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const t24 = V.unit(V.reject(p[2], p[1])), side = V.cross(p[2], t24);
      const fol = V.madd(V.madd(V.scale(p[1], F[1] + h + 4), t24, P.cam_r), side, 4);       // cam follower on its lever
      const crank = V.madd(V.scale(p[2], F[2] + 9), side, 6);                               // 6 mm crank on link 2b
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(p[0], F[0] - 3), z: p[0], x: W([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(p[0], F[0]), axis: p[0], r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1', u: p[0], v: p[1], r0: F[0] + 7, r1: F[1] + 2, r: 2.5 },
        { kind: 'ring', role: 'link', name: 'groove face cam (on link 1)', c: V.scale(p[1], F[1] + 2), axis: p[1], r: P.cam_r, w: 3 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(p[1], F[1]), axis: p[1], r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2a', u: p[1], v: p[2], r0: F[1] + 9, r1: F[2] + 2, r: 2.5 },
        { kind: 'link', role: 'passive', name: 'pushrod (cam follower to knee crank)', a: fol, b: crank, r: 1.2 },
        { kind: 'hub', role: 'passive', name: 'J4 knee: crossed-leaf flexure (slaved)', c: V.scale(p[2], F[2]), axis: p[2], r: 6, h: 6 },
        { kind: 'arc', role: 'link', name: 'link 2b', u: p[2], v: p[3], r0: F[2] + 6, r1: F[3] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(p[3], F[3]), axis: p[3], r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: p[3], v: nk, r0: F[3] + 1, r1: F[3] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
