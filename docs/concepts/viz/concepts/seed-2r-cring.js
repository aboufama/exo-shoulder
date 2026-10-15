/* seed-2r-cring - 2R spherical shoulder (two O20 hubs) + an open C-track round the upper arm for the axial rotation
 * (docs/concepts/seed-2r-cring.md, models/seed-2r-cring.py; DEAD, best k8 gap 129.98). Spherical 3R whose last axis d3
 * is humerus-fixed through GH, tilted 18 deg off the GH-elbow line (toward azimuth -30) so the circle sits round the arm:
 * J1 hub on p1 = bvec(125, 45) (S), J2 hub on p2 (two-cone closure, a1 = a2 = 90, branch -1), link 2 carries a carriage
 * that rides the C-track (inner radius 57.2 at L = 100 mm along d3): J3 = the carriage azimuth round d3. The C covers
 * +-61 deg about lateral (the bench's cov 0.6 arc + carriage + stop), open toward the torso; carriage azimuth = p2's
 * azimuth round d3 - c0 (c0 = centre of the arc holding 60 % of the poses, taken on this loop). The C-track rides the
 * cuff on a PASSIVE slide along d3: set by the GH translation along d3 (0 on this fixed-GH rig, so its residual is its
 * travel). 3 active + 1 passive; closed form for the 3R (KIN.sph3r). Hub faces 56 / 66 mm are schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 125, el: 45, a1: 90, a2: 90, sigma: -1, margin: 10, L: 100, tilt: 18, tilt_a: -30, R: 57.17, cov: 0.6,
              span: 61.25, car: [25, 12, 6], tr: [6, 8], slide: [40, 10, 6], faces: [56, 66], hub_r: 10, stack: 12.25, cuff_at: 175 };
  const d3L = K.wdir(P.tilt, P.tilt_a), elL = V.unit(V.reject([0, 0, 1], d3L)), eaL = V.cross(elL, d3L);
  const C = K.sph3r(K.bvec(P.az, P.el), d3L, P.a1, P.a2, P.sigma);
  const carHalf = (P.car[0] / 2 / P.R + 3 / P.R) * K.R2D, hw0 = P.span - carHalf;      // usable carriage travel each side
  /** azimuth of p2 round d3, humerus frame (0 lateral, +90 anterior) */
  function psiRaw(ctx, p2) { const E1 = M.mulv(ctx.H, elL), E2 = M.mulv(ctx.H, eaL); return Math.atan2(V.dot(p2, E2), V.dot(p2, E1)) * K.R2D; }
  let C0 = null;
  function c0() {                                          // smallest arc holding cov of the loop's closing frames: its centre
    if (C0 != null) return C0;
    const s = [];
    for (const f of K.motion(120)) { const ctx = K.makeCtx(f.pose); if (C.margin(ctx) < P.margin) continue; s.push(psiRaw(ctx, C.fk(C.solve(ctx), ctx).p2)); }
    s.sort((a, b) => a - b); const n = s.length, m = Math.max(1, Math.ceil(P.cov * n)), s2 = s.concat(s.map(x => x + 360));
    let best = 1e9, c = 0; for (let i = 0; i < n; i++) { const w = s2[i + m - 1] - s2[i]; if (w < best) { best = w; c = s2[i] + w / 2; } }
    return (C0 = K.wrap180(c));
  }
  const dirAt = (ctx, a) => V.add(V.scale(M.mulv(ctx.H, elL), Math.cos(a * K.D2R)), V.scale(M.mulv(ctx.H, eaL), Math.sin(a * K.D2R)));

  K.register({
    id: 'seed-2r-cring',
    name: '2R shoulder + C-ring on the arm',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => C.solve(ctx).concat([0]),
    qNames: ['J1 hub', 'J2 hub', 'J3 carriage on the C-track', 'cuff slide along d3 (passive)'], qUnits: ['deg', 'deg', 'deg', 'mm'],
    resUnits: ['deg', 'deg', 'deg', 'mm'],
    solve: ctx => C.solve(ctx).concat([0]),
    // 3R closure + the loop's translation along d3: every axis passes through GH, so the slide = GH translation (0 here)
    residual: (q, ctx) => C.residual(q, ctx).concat([q[3]]),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm is out of the 2R\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const a = K.wrap180(psiRaw(ctx, C.fk(q, ctx).p2) - c0());
      if (Math.abs(a) > hw0) return `carriage outside the C (${a.toFixed(0)} deg, C holds +-${hw0.toFixed(0)})`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.faces, h = P.stack, d3 = f.p3, R = P.R;
      const a = K.wrap180(psiRaw(ctx, f.p2) - c0()), cd = dirAt(ctx, a), o = V.scale(d3, P.L);
      const carC = V.madd(o, cd, R + P.tr[0] + 0.5 + P.car[2] / 2), carTop = V.madd(o, cd, R + P.tr[0] + 0.5 + P.car[2]);
      const tang = V.unit(V.cross(d3, cd)), E1 = M.mulv(ctx.H, elL);
      const se = dirAt(ctx, P.span + 6), s0 = V.madd(V.scale(d3, P.L - 4), se, R + 3), s1 = V.madd(V.scale(d3, P.L - 4 + P.slide[0]), se, R + 3);
      const harm = ctx.armAxis, cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(s1, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [44, 34], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1 (90 deg)', u: f.p1, v: f.p2, r0: F[0] + 7, r1: F[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(f.p2, F[1]), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2 (to the carriage)', pts: K.greatArc(f.p2, carTop, F[1] + h + 1, V.norm(carTop)), r: 2.5 },
        { kind: 'rail', role: 'fixed-arm', name: 'C-track (open toward the torso)', c: o, axis: d3, ref: E1, rho: R + P.tr[0] / 2, a0: -P.span, a1: P.span, r: 3 },
        { kind: 'carriage', role: 'active', name: 'J3 carriage (on link 2)', c: carC, x: tang, z: cd, size: P.car },
        { kind: 'slider', role: 'passive', name: 'cuff slide along d3 (passive)', a: s0, b: s1, at: V.madd(V.lerp(s0, s1, 0.5), d3, q[3]), z: se, size: [14, 10, 5] },
        { kind: 'link', role: 'fixed-arm', name: 'slide to cuff', a: s1, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
