/* five-bar-pointer-turret - spherical FIVE-BAR pointer driven by two base hubs + an arm TURRET roll (catalogue
 * five-bar-pointer-turret, ideated; marked a duplicate of fivebar-roll, which shares the base-hub coaxial variant).
 * Leg A: S -> JA (ACTIVE, O20 hub on the dome, axis at p* = S lat 66 / lon -68) -> proximal link A (ap) -> vA (PASSIVE
 * elbow hub) -> distal link A (ad). Leg B: S -> JB (ACTIVE, O20 hub on the posterior scapula / infraspinous fossa, S lat -5
 * / lon -115) -> proximal B -> vB (PASSIVE) -> distal B, which turns on distal A about the common output axis w (PASSIVE).
 * J3 (ACTIVE): a thin-section turret ring about the same axis w between distal A and the arm, its stator on the lateral
 * arm strip; w = the arm-fixed axis j_o through GH at s ~130 mm, th 10 (wdir(21, -10)); the turret sits where that axis meets the lateral arm skin (~142 mm from GH). A spherical 5R loop (2-DOF
 * pointing of w) + a coaxial roll: 3 active, 3 passive, every passive set by closure. Each leg is the spherical 3R
 * (base, elbow, w) of KIN.sph3r (closed form); arcs from a kinematic loop screen inside the spec's 60-100 deg ranges
 * (A: ap 100, ad 60; B: ap 80, ad 100; branches +1 / -1: 140 of 141 screen frames close). Kept out as fivebar-roll:
 * leg margin < 8 deg, parallel singularity (distal links aligned at w, < 12 deg), elbows < 17 deg apart. Levels schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, D = K.D2R;
  const SL = (lat, lon) => [Math.cos(lat * D) * Math.sin(lon * D), Math.sin(lat * D), Math.cos(lat * D) * Math.cos(lon * D)];
  const P = Object.assign({}, { aLat: 66, aLon: -68, bLat: -5, bLon: -115, ap: [100, 80], ad: [60, 100], wd: 21, wa: -10, s: [1, -1],
              margin: 8, par: 12, sep: 17, faces: [52, 54], pins: [84, 80], fW: 142, up: 3.15, ring_r: 16, cuff_at: 165 });
  const ua = SL(P.aLat, P.aLon), ub = SL(P.bLat, P.bLon), W0 = K.wdir(P.wd, P.wa);
  const BA = K.sph3r(ua, W0, P.ap[0], P.ad[0], P.s[0]), BB = K.sph3r(ub, W0, P.ap[1], P.ad[1], P.s[1]);
  const split = q => ({ qa: [q[0], q[3], q[2]], qb: [q[1], q[4], q[2] - q[5]] });   // q = JA, JB, J3, vA, vB, w
  function solve(ctx) { const x = BA.solve(ctx), y = BB.solve(ctx); return [x[0], y[0], x[2], x[1], y[1], K.wrap180(x[2] - y[2])]; }
  K.register({
    id: 'five-bar-pointer-turret',
    name: 'Spherical five-bar pointer (two base hubs) + arm turret roll',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['JA (dome hub)', 'JB (posterior scapula hub)', 'J3 turret roll about w', 'vA elbow (passive)', 'vB elbow (passive)', 'w: distal B on distal A (passive)'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => { const s = split(q); return BA.residual(s.qa, ctx).concat(BB.residual(s.qb, ctx)); },
    check: (q, ctx) => {
      const m = Math.min(BA.margin(ctx), BB.margin(ctx));
      if (m < 0) return 'a leg cannot close: w is out of the five-bar\'s reach';
      if (m < P.margin) return `a leg within ${m.toFixed(0)} deg of its fold`;
      const s = split(q), fa = BA.fk(s.qa, ctx), fb = BB.fk(s.qb, ctx);
      const n1 = V.unit(V.cross(fa.p2, fa.p3)), n2 = V.unit(V.cross(fb.p2, fa.p3));
      if (V.norm(V.cross(n1, n2)) < Math.sin(P.par * D)) return 'parallel singularity: the distal links line up at w';
      if (V.angle(fa.p2, fb.p2) < P.sep) return 'elbow hubs collide';
      return null;
    },
    parts: (q, ctx) => {
      const s = split(q), fa = BA.fk(s.qa, ctx), fb = BB.fk(s.qb, ctx), A = fa.p1, B = fb.p1, eA = fa.p2, eB = fb.p2, W = fa.p3;
      const F = P.faces, fw = P.fW, up = P.up, harm = ctx.armAxis, h = 12.25, rr = V.perp(W);
      const cuffC = V.scale(harm, P.cuff_at), lat = V.unit(V.reject(V.scale(W, fw), harm)), cuffTop = V.madd(cuffC, lat, 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base A (dome, on the handler)', c: V.scale(A, F[0] - 3), z: A, x: ctx.attach.scapDir([1, 0, 0]), size: [32, 28], t: 3 },
        { kind: 'hub', role: 'active', name: 'JA (O20, dome)', c: V.scale(A, F[0]), axis: A, r: 10, h },
        { kind: 'plate', role: 'fixed-scapula', name: 'base B (infraspinous fossa, on the handler)', c: V.scale(B, F[1] - 3), z: B, x: ctx.attach.scapDir([0, 1, 0]), size: [32, 28], t: 3 },
        { kind: 'hub', role: 'active', name: 'JB (O20, posterior scapula)', c: V.scale(B, F[1]), axis: B, r: 10, h },
        { kind: 'arc', role: 'link', name: 'proximal link A (over the top / front)', u: A, v: eA, r0: F[0] + 7, r1: P.pins[0], r: 2.5 },
        { kind: 'arc', role: 'link', name: 'proximal link B (over the back)', u: B, v: eB, r0: F[1] + 7, r1: P.pins[1], r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'vA elbow hub (passive)', c: V.scale(eA, P.pins[0]), axis: eA, r: 7, h: 8 },
        { kind: 'hub', role: 'passive', name: 'vB elbow hub (passive)', c: V.scale(eB, P.pins[1]), axis: eB, r: 7, h: 8 },
        { kind: 'arc', role: 'link', name: 'distal link A', u: eA, v: W, r0: P.pins[0] + up, r1: fw + 8 + up, r: 2.2 },
        { kind: 'arc', role: 'link', name: 'distal link B (turns on distal A at w)', u: eB, v: W, r0: P.pins[1] + up, r1: fw + 8 + 2 * up, r: 2.2 },
        { kind: 'hub', role: 'passive', name: 'w: distal B on distal A (passive)', c: V.scale(W, fw + 8), axis: W, r: 7, h: 8 },
        { kind: 'ring', role: 'active', name: 'J3 turret ring (thin-section, roll about w)', c: V.scale(W, fw + 4), axis: W, ref: rr, r: P.ring_r, t: 2.4 },
        { kind: 'ring', role: 'fixed-arm', name: 'turret stator on the lateral arm strip', c: V.scale(W, fw), axis: W, ref: rr, r: P.ring_r, t: 2.4 },
        { kind: 'link', role: 'fixed-arm', name: 'turret to cuff / BOTTOM', a: V.scale(W, fw), b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
