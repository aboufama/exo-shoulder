/* armband-pointer - a 2R donut "pointer" over the shoulder points the arm, and a CLOSED thin-section ring bearing round
 * the distal upper arm, just above the user's cuff, takes the humeral twist (catalogue armband-pointer; ideated, no bench
 * model yet). Spherical 3R with a3 = the humerus axis t: J1 donut about a1 = p* = bvec(120, 46) (S-fixed, anterior
 * acromion), J2 donut about a2 = unit(a1 x t) (90 deg from a1 and from the arm), link 2 = a long LATERAL SPAR down the
 * outside of the arm in the pointing frame P = [a2 x t, a2, t] (it follows the arm's direction, not its twist) to the
 * ring's stator; J3 = the ring's rotor, bolted to the cuff (KA045XP0 class: bore 114.3, 6.35 section, housings to
 * r_in + 10, 10 mm wide) at s_r 205 mm. q3 = the arm-fixed lateral's angle in P; a closed ring has no travel limit, so
 * the only limit is the pointer's pole (arm within 15 deg of +-a1). Spar angle c = the arm-lateral's mean angle in P
 * over this loop; donut radii and the spar height (64 mm off the axis) are schematic, as in pointer-cslide.
 * 3 active, 0 passive; closed form. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { az: 120, el: 46, sigma: 1, sing: 15, R1: 56, R2: 64, donut_r: 17.5, donut_t: 9, s_r: 205, r_in: 57.15,
              ring_w: 10, ring_h: 10, spar_r: 64, cuff_r: 45 };
  const a1L = K.bvec(P.az, P.el), latL = [0, 0, 1];
  /** pointer frame of a pose (closed form): a1, p2, t, xP, yP, the arm-fixed lateral, q */
  function point(ctx) {
    const a1 = M.mulv(ctx.S, a1L), t = ctx.armAxis, p2 = K.circInt(a1, 90, t, 90, P.sigma).p;
    const xP = V.unit(V.cross(p2, t)), yP = V.cross(t, xP), lat = V.unit(V.reject(M.mulv(ctx.H, latL), t));
    return { a1, p2, t, xP, yP, lat, q: [K.axisAngle(a1, ctx.attach.scapDir([1, 0, 0]), p2), K.axisAngle(p2, a1, t),
      Math.atan2(V.dot(lat, yP), V.dot(lat, xP)) * K.R2D] };
  }
  /** forward kinematics from q */
  function fk(q, ctx) {
    const a1 = M.mulv(ctx.S, a1L), p2 = M.mulv(M.rot(a1, q[0]), V.unit(V.reject(ctx.attach.scapDir([1, 0, 0]), a1)));
    const t = M.mulv(M.rot(p2, q[1]), a1), xP = V.unit(V.cross(p2, t)), yP = V.cross(t, xP);
    return { a1, p2, t, xP, yP, lat: V.add(V.scale(xP, Math.cos(q[2] * D2R)), V.scale(yP, Math.sin(q[2] * D2R))) };
  }
  const endFrame = (t, lat) => M.fromCols(lat, V.cross(t, lat), t);
  let C0 = null;
  function spar() {                                        // spar angle c: the arm-lateral's mean angle in P over the loop
    if (C0 != null) return C0;
    let x = 0, y = 0; for (const f of K.motion(120)) { const a = point(K.makeCtx(f.pose)).q[2] * D2R; x += Math.cos(a); y += Math.sin(a); }
    return (C0 = Math.atan2(y, x) * K.R2D);
  }

  K.register({
    id: 'armband-pointer',
    name: '2R donut pointer + closed armband ring',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => point(ctx).q,
    qNames: ['J1 donut', 'J2 donut', 'J3 armband ring (twist)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => point(ctx).q,
    residual: (q, ctx) => { const f = fk(q, ctx), A = point(ctx); return M.rotErrDeg(endFrame(f.t, f.lat), endFrame(A.t, A.lat)); },
    check: (q, ctx) => {
      const A = point(ctx), g = V.angle(A.a1, A.t), m = Math.min(g, 180 - g);
      return m < P.sing ? `arm within ${m.toFixed(0)} deg of the J1 pole (pointer singular)` : null;
    },
    parts: (q, ctx) => {
      const f = fk(q, ctx), c = spar() * D2R, dc = V.add(V.scale(f.xP, Math.cos(c)), V.scale(f.yP, Math.sin(c)));
      const j2top = V.scale(f.p2, P.R2 + P.donut_t + 1), sp1 = V.madd(V.scale(f.t, 70), dc, P.spar_r);
      const sp2 = V.madd(V.scale(f.t, P.s_r - P.ring_w / 2 - 4), dc, P.r_in + P.ring_h + 2);
      const sparPts = K.greatArc(j2top, sp1, V.norm(j2top), V.norm(sp1), 16).concat([V.lerp(sp1, sp2, 0.5), sp2]);
      const o = V.scale(f.t, P.s_r), cuffC = V.scale(f.t, P.s_r + 24);
      const brk = s => { const d = V.scale(f.lat, s); return { kind: 'link', role: 'fixed-arm', name: 'rotor to cuff bracket',
        a: V.madd(V.scale(f.t, P.s_r + P.ring_w / 2), d, P.r_in + 1), b: V.madd(cuffC, d, P.cuff_r + 1), r: 3 }; };
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'bracket (anterior acromion)', c: V.scale(f.a1, P.R1 - 3), z: f.a1, x: ctx.attach.scapDir([1, 0, 0]), size: [44, 40], t: 3 },
        { kind: 'ring', role: 'active', name: 'J1 donut', c: V.scale(f.a1, P.R1 + P.donut_t / 2), axis: f.a1, r: P.donut_r, t: P.donut_t / 2, h: P.donut_t },
        { kind: 'arc', role: 'link', name: 'link 1 (90 deg)', u: f.a1, v: f.p2, r0: P.R1 + P.donut_t, r1: P.R2, r: 2.5 },
        { kind: 'ring', role: 'active', name: 'J2 donut', c: V.scale(f.p2, P.R2 + P.donut_t / 2), axis: f.p2, r: P.donut_r, t: P.donut_t / 2, h: P.donut_t },
        { kind: 'arc', role: 'link', name: 'lateral spar (link 2, no twist)', pts: sparPts, r: 3 },
        // the closed ring as full-circle tubes (rail 0..360: the harness samples its circle, not only its centre)
        { kind: 'rail', role: 'link', name: 'ring stator + housing (on the spar)', c: o, axis: f.t, ref: dc, rho: P.r_in + 7, a0: 0, a1: 360, r: 3.2 },
        { kind: 'rail', role: 'active', name: 'J3 armband ring rotor (thin section)', c: V.madd(o, f.t, 2), axis: f.t, ref: f.lat, rho: P.r_in + 1.8, a0: 0, a1: 360, r: 1.8 },
        brk(1), brk(-1),
        { kind: 'strap', role: 'fixed-arm', name: 'user cuff (BOTTOM)', c: cuffC, axis: f.t, r: P.cuff_r, w: 30 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
