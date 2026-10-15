/* pointer-cslide - the user's split: a 2R "pointer" over the shoulder (two donut bearings) points the arm, and an open
 * C-RAIL on link 2 around the arm carries the humeral twist (docs/concepts/pointer-cslide.md, models/pointer-cslide.py).
 * Spherical 3R with a3 = the humerus axis d3: J1 about a1 = p* = bvec(120, 46) (S-fixed, over the anterior acromion),
 * J2 about p2 = unit(a1 x d3) (90 deg from a1 AND from the arm), link 2 = the pointing link (follows the arm's direction,
 * not its twist) ending on a circular wire-race band about d3 at station s; J3 = the arm-fixed shoe riding the band.
 * 3 active, 0 passive; closed form (q1 azimuth of p2 about a1, q2 angle a1 -> d3 about p2, q3 the shoe angle in the
 * pointing frame P = [p2 x d3, d3 x ., d3]). Singular when d3 comes within `sing` of +-a1. Spec parameters (the sweep is
 * still running); band travel T = 165 deg, the share the bench measured for 90 % of its poses (the spec's 60-90 deg came
 * from clips only), centred on this loop; band radius rho 62 at s 120 is schematic (the model marches it on the skin). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 120, el: 46, sigma: 1, sing: 15, s: 120, phi_s: 0, Ls: 50, T: 165, rho: 62, band_w: 26, band_t: 6,
              R1: 56, R2: 64, donut_r: 17.5, donut_t: 9, neck_to: 185 };
  const a1L = K.bvec(P.az, P.el), shoeL = [Math.sin(P.phi_s * K.D2R), 0, Math.cos(P.phi_s * K.D2R)];

  /** pointer frame of a pose: a1, p2, d3, P = (xP, yP), shoe dir, q (closed form) */
  function point(ctx) {
    const a1 = M.mulv(ctx.S, a1L), d3 = ctx.armAxis, p2 = K.circInt(a1, 90, d3, 90, P.sigma).p;
    const xP = V.unit(V.cross(p2, d3)), yP = V.cross(d3, xP), shoe = M.mulv(ctx.H, shoeL);
    const q = [K.axisAngle(a1, ctx.attach.scapDir([1, 0, 0]), p2), K.axisAngle(p2, a1, d3),
               Math.atan2(V.dot(shoe, yP), V.dot(shoe, xP)) * K.R2D];
    return { a1, p2, d3, xP, yP, shoe, q };
  }
  /** forward kinematics from q: p2, d3, pointing frame and the shoe direction the chain carries */
  function fk(q, ctx) {
    const a1 = M.mulv(ctx.S, a1L), p2 = M.mulv(M.rot(a1, q[0]), V.unit(V.reject(ctx.attach.scapDir([1, 0, 0]), a1)));
    const d3 = M.mulv(M.rot(p2, q[1]), a1), xP = V.unit(V.cross(p2, d3)), yP = V.cross(d3, xP);
    const c3 = Math.cos(q[2] * K.D2R), s3 = Math.sin(q[2] * K.D2R);
    return { a1, p2, d3, xP, yP, shoe: V.add(V.scale(xP, c3), V.scale(yP, s3)) };
  }
  // the band window: T (bench-measured) centred on the shoe's range over this loop (a design decision, then fixed)
  let C0 = null;
  function centre() {
    if (C0 != null) return C0;
    const th = K.motion(120).map(f => point(K.makeCtx(f.pose)).q[2]), r = th[0];
    const rel = th.map(x => K.wrap180(x - r));
    return (C0 = K.wrap180(r + 0.5 * (Math.max(...rel) + Math.min(...rel))));
  }
  const endFrame = (d3, shoe) => M.fromCols(shoe, V.cross(d3, shoe), d3);

  K.register({
    id: 'pointer-cslide',
    name: '2R donut pointer + C-slide (humeral twist on a rail)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => point(ctx).q,
    qNames: ['J1 donut', 'J2 donut', 'J3 shoe on the C-rail'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => point(ctx).q,
    residual: (q, ctx) => {
      const f = fk(q, ctx), A = point(ctx);
      return M.rotErrDeg(endFrame(f.d3, f.shoe), endFrame(A.d3, A.shoe));
    },
    check: (q, ctx) => {
      const A = point(ctx), g = V.angle(A.a1, A.d3);
      if (Math.min(g, 180 - g) < P.sing) return `arm within ${Math.min(g, 180 - g).toFixed(0)} deg of the J1 pole (pointer singular)`;
      if (Math.abs(K.wrap180(q[2] - centre())) > P.T / 2) return 'shoe past the end of the C-rail';
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q, ctx), c = centre(), s = P.s, rB = P.rho + 2, hw = P.band_w / 2;
      const stop = 3 / rB * K.R2D, lo = c - P.T / 2 - P.Ls / 2 - stop, hi = c + P.T / 2 + P.Ls / 2 + stop;
      const dirP = a => V.add(V.scale(f.xP, Math.cos(a * K.D2R)), V.scale(f.yP, Math.sin(a * K.D2R)));
      const att = V.madd(V.scale(f.d3, s - hw + 1), dirP(c), rB + P.band_t);          // link 2 lands on the band's proximal edge
      const tang = V.unit(V.cross(f.d3, f.shoe)), shoeC = V.madd(V.scale(f.d3, s + 2), f.shoe, P.rho + 5);
      const neckA = V.madd(V.scale(f.d3, s + hw + 4), f.shoe, P.rho + 4), neckB = V.madd(V.scale(f.d3, P.neck_to - 12), f.shoe, 49);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'bracket (anterior acromion)', c: V.scale(f.a1, P.R1 - 3), z: f.a1, x: ctx.attach.scapDir([1, 0, 0]), size: [44, 40], t: 3 },
        { kind: 'ring', role: 'active', name: 'J1 donut (KAA10)', c: V.scale(f.a1, P.R1 + P.donut_t / 2), axis: f.a1, r: P.donut_r, w: 9.5, t: P.donut_t },
        { kind: 'arc', role: 'link', name: 'link 1 (90 deg)', u: f.a1, v: f.p2, r0: P.R1 + P.donut_t, r1: P.R2, r: 2.5 },
        { kind: 'ring', role: 'active', name: 'J2 donut (KAA10)', c: V.scale(f.p2, P.R2 + P.donut_t / 2), axis: f.p2, r: P.donut_r, w: 9.5, t: P.donut_t },
        { kind: 'arc', role: 'link', name: 'link 2 (pointing link)', pts: K.greatArc(f.p2, att, P.R2 + P.donut_t, V.norm(att)), r: 2.5 },
        { kind: 'rail', role: 'link', name: 'C-rail (wire-race band on link 2)', c: V.scale(f.d3, s), axis: f.d3, ref: f.xP, rho: rB + P.band_t / 2, a0: lo, a1: hi, r: 3, w: P.band_w },
        { kind: 'carriage', role: 'active', name: 'J3 shoe (arm-fixed)', c: shoeC, x: tang, z: f.shoe, size: [P.Ls * K.D2R * P.rho, 16, 10] },
        { kind: 'link', role: 'fixed-arm', name: 'shoe neck', a: neckA, b: neckB, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(f.d3, P.neck_to), axis: f.d3, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
