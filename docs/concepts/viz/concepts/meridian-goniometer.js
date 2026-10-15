/* meridian-goniometer - the pointer of pointer-cslide with NO J2 HUB: J2 is a goniometer-cradle ARC RAIL fixed to the
 * J1 rotor, a small circle about the VIRTUAL axis a2 = unit(a1 x t) at cone alpha_r, beside the arm's elevation path;
 * a 40 deg shoe carriage rides it level with the arm root (catalogue entry meridian-goniometer; no bench model yet).
 * Same spherical kinematics as pointer-cslide: q1 = J1 azimuth (donut on p* = bvec(120, 46)), q2 = the carriage's
 * position along the rail (rotation about the virtual a2, = angle(a1, t)), q3 = humeral twist on a shoulder-side C-slide
 * (arm-fixed shoe on a wire-race band carried by link 2 = carriage + bridge). 3 active, 0 passive, closed form. The
 * rail is cut to the q2 range this loop needs + half a carriage each end (the spec's first pass on the bench poses);
 * radii (rail 70 mm from GH, band 62 at s 90) are schematic; C-rail travel T 165 deg as measured for pointer-cslide. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 120, el: 46, sigma: 1, side: 1, alpha_r: 45, Rr: 70, Lc: 40, sing: 15, s: 90, phi_s: 0, Ls: 50, T: 165,
              rho: 62, band_w: 26, band_t: 6, R1: 56, donut_r: 17.5, donut_t: 9, neck_to: 175 };
  const a1L = K.bvec(P.az, P.el), shoeL = [Math.sin(P.phi_s * K.D2R), 0, Math.cos(P.phi_s * K.D2R)];

  function point(ctx) {                       // the pointer IK of pointer-cslide (a2 virtual here)
    const a1 = M.mulv(ctx.S, a1L), d3 = ctx.armAxis, a2 = K.circInt(a1, 90, d3, 90, P.sigma).p;
    const xP = V.unit(V.cross(a2, d3)), yP = V.cross(d3, xP), shoe = M.mulv(ctx.H, shoeL);
    return { a1, a2, d3, xP, yP, shoe, q: [K.axisAngle(a1, ctx.attach.scapDir([1, 0, 0]), a2), K.axisAngle(a2, a1, d3),
                                            Math.atan2(V.dot(shoe, yP), V.dot(shoe, xP)) * K.R2D] };
  }
  function fk(q, ctx) {
    const a1 = M.mulv(ctx.S, a1L), a2 = M.mulv(M.rot(a1, q[0]), V.unit(V.reject(ctx.attach.scapDir([1, 0, 0]), a1)));
    const d3 = M.mulv(M.rot(a2, q[1]), a1), xP = V.unit(V.cross(a2, d3)), yP = V.cross(d3, xP);
    const shoe = V.add(V.scale(xP, Math.cos(q[2] * K.D2R)), V.scale(yP, Math.sin(q[2] * K.D2R)));
    return { a1, a2, d3, xP, yP, shoe };
  }
  // design decisions from the loop (fixed afterwards): the rail's q2 span and the C-rail window centre
  let D = null;
  function design() {
    if (D) return D;
    const Q = K.motion(120).map(f => point(K.makeCtx(f.pose)).q), r3 = Q[0][2], rel = Q.map(q => K.wrap180(q[2] - r3));
    const q2 = Q.map(q => q[1]);
    return (D = { q2lo: Math.min(...q2), q2hi: Math.max(...q2), c: K.wrap180(r3 + 0.5 * (Math.max(...rel) + Math.min(...rel))) });
  }
  const endFrame = (d3, shoe) => M.fromCols(shoe, V.cross(d3, shoe), d3);
  const ca = Math.cos(P.alpha_r * K.D2R), sa = Math.sin(P.alpha_r * K.D2R);
  // a point on the rail at angle phi (about a2 from a1) and radius R
  const railPt = (f, phi, R) => V.scale(V.add(V.scale(f.a2, P.side * ca), V.scale(M.mulv(M.rot(f.a2, phi), f.a1), sa)), R);

  K.register({
    id: 'meridian-goniometer',
    name: 'Goniometer pointer (J2 = arc rail, virtual axis)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => point(ctx).q,
    qNames: ['J1 donut', 'J2 carriage on the arc rail', 'J3 shoe on the C-rail'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => point(ctx).q,
    residual: (q, ctx) => { const f = fk(q, ctx), A = point(ctx); return M.rotErrDeg(endFrame(f.d3, f.shoe), endFrame(A.d3, A.shoe)); },
    check: (q, ctx) => {
      const A = point(ctx), g = V.angle(A.a1, A.d3), d = design();
      if (Math.min(g, 180 - g) < P.sing) return `arm within ${Math.min(g, 180 - g).toFixed(0)} deg of the J1 pole (pointer singular)`;
      if (q[1] < d.q2lo || q[1] > d.q2hi) return 'carriage past the end of the arc rail';
      if (Math.abs(K.wrap180(q[2] - d.c)) > P.T / 2) return 'shoe past the end of the C-rail';
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q, ctx), d = design(), s = P.s, rB = P.rho + 2, hw = P.band_w / 2;
      const lo = d.q2lo - P.Lc / 2, hi = d.q2hi + P.Lc / 2;
      const car = railPt(f, q[1], P.Rr + 5), carX = V.unit(V.sub(railPt(f, q[1] + 1, 1), railPt(f, q[1] - 1, 1)));
      // C-rail window and the bridge's landing: the band point nearest the carriage side (azimuth of side * a2 = 90 deg)
      const stop = 3 / rB * K.R2D, blo = d.c - P.T / 2 - P.Ls / 2 - stop, bhi = d.c + P.T / 2 + P.Ls / 2 + stop;
      let aB = P.side > 0 ? 90 : -90; if (Math.abs(K.wrap180(aB - d.c)) > (bhi - blo) / 2 - 4) aB = d.c + Math.sign(K.wrap180(aB - d.c)) * ((bhi - blo) / 2 - 4);
      const dirP = a => V.add(V.scale(f.xP, Math.cos(a * K.D2R)), V.scale(f.yP, Math.sin(a * K.D2R)));
      const land = V.madd(V.scale(f.d3, s - hw + 1), dirP(aB), rB + P.band_t);
      const rootA = V.scale(f.a1, P.R1 + P.donut_t), rootB = railPt(f, lo, P.Rr);
      const shoeC = V.madd(V.scale(f.d3, s + 2), f.shoe, P.rho + 5), tang = V.unit(V.cross(f.d3, f.shoe));
      const neckA = V.madd(V.scale(f.d3, s + hw + 4), f.shoe, P.rho + 4), neckB = V.madd(V.scale(f.d3, P.neck_to - 12), f.shoe, 49);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'bracket (anterior acromion)', c: V.scale(f.a1, P.R1 - 3), z: f.a1, x: ctx.attach.scapDir([1, 0, 0]), size: [44, 40], t: 3 },
        { kind: 'ring', role: 'active', name: 'J1 donut (KAA10)', c: V.scale(f.a1, P.R1 + P.donut_t / 2), axis: f.a1, r: P.donut_r, w: 9.5, t: P.donut_t },
        { kind: 'link', role: 'link', name: 'rail root (on the J1 rotor)', a: rootA, b: rootB, r: 3 },
        { kind: 'rail', role: 'link', name: 'J2 arc rail (cradle about virtual a2)', c: V.scale(f.a2, P.side * ca * P.Rr), axis: f.a2, ref: f.a1, rho: sa * P.Rr, a0: lo, a1: hi, r: 3, w: 6 },
        { kind: 'point', role: 'link', name: 'virtual J2 axis a2 (no hub)', p: V.scale(f.a2, P.side * 40), r: 2 },
        { kind: 'carriage', role: 'active', name: 'J2 carriage (40 deg shoe)', c: car, x: carX, z: V.unit(car), size: [P.Lc * K.D2R * P.Rr * sa, 14, 8] },
        { kind: 'link', role: 'link', name: 'bridge (link 2) to the C-rail', a: V.madd(car, V.unit(car), 4), b: land, r: 3 },
        { kind: 'rail', role: 'link', name: 'C-rail (wire-race band)', c: V.scale(f.d3, s), axis: f.d3, ref: f.xP, rho: rB + P.band_t / 2, a0: blo, a1: bhi, r: 3, w: P.band_w },
        { kind: 'carriage', role: 'active', name: 'J3 shoe (arm-fixed)', c: shoeC, x: tang, z: f.shoe, size: [P.Ls * K.D2R * P.rho, 16, 10] },
        { kind: 'link', role: 'fixed-arm', name: 'shoe neck', a: neckA, b: neckB, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(f.d3, P.neck_to), axis: f.d3, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
