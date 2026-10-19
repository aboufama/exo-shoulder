/* fivebar-roll - spherical five-bar pointer plus an active arm roll (catalogue fivebar-roll, models/fivebar-roll.py;
 * dead at gap 90.30 with the spec's margins: sweeps/fivebar-roll.json k6, honest). Coaxial base at bvec(94.7, 83.7)
 * (top of the shoulder, one double-row hub) carries two ACTIVE cranks (A1, arc 75; A2, arc 90) -> passive elbow pins
 * B1, B2 -> couplers (60, 45) that close on ONE arm hub at the humerus-fixed axis W = wdir(90, 0): there coupler 2
 * turns about coupler 1 (C, passive) and the arm rolls about coupler 1 (D, ACTIVE). Spherical Gruebler: 6 bodies,
 * 6 R -> 3 DOF: A1, A2, D active; B1, B2, C passive, each set by closure. Each branch is the spherical 3R (u, e_k, W)
 * of KIN.sph3r (closed form); C = D - D2 (the roll seen from coupler 2). Kept out (model): leg margin < 8 deg,
 * parallel singularity |n1 x n2| < sin 12 (n_k = unit(e_k x W)), elbows < 17 deg apart. Radii follow the measured
 * limiter (docs/concepts/fivebar-roll.md): the elbow pins ride at ~99 / 120 mm over the cap and the couplers stack
 * over the cranks, each other and the arm plate (+3.15 mm each). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, D = K.D2R;
  const P = { uaz: 94.73248043278903, uel: 83.69955944451229, a: [75, 90], c: [60, 45], wd: 90, wa: 0, s: [-1, -1],
              margin: 8, par: 12, sep: 17, base: 52, pins: [120, 99], fW: 76, up: 3.15, neck_deg: 25, cuff_at: 165 };
  const u = K.bvec(P.uaz, P.uel), W0 = K.wdir(P.wd, P.wa);
  const B1 = K.sph3r(u, W0, P.a[0], P.c[0], P.s[0]), B2 = K.sph3r(u, W0, P.a[1], P.c[1], P.s[1]);
  const split = q => ({ q1: [q[0], q[3], q[2]], q2: [q[1], q[4], q[2] - q[5]] });   // q = A1, A2, D, B1, B2, C
  function solve(ctx) {
    const x = B1.solve(ctx), y = B2.solve(ctx);
    return [x[0], y[0], x[2], x[1], y[1], K.wrap180(x[2] - y[2])];
  }

  K.register({
    id: 'fivebar-roll',
    name: 'Five-bar pointer + arm roll',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['A1 crank 1', 'A2 crank 2', 'D arm roll', 'B1 elbow (passive)', 'B2 elbow (passive)', 'C couplers at W (passive)'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'],
    solve: (ctx) => solve(ctx),
    residual: (q, ctx) => { const s = split(q); return B1.residual(s.q1, ctx).concat(B2.residual(s.q2, ctx)); },
    check: (q, ctx) => {
      const m = Math.min(B1.margin(ctx), B2.margin(ctx));
      if (m < 0) return 'a leg cannot close: W is out of the five-bar\'s reach';
      if (m < P.margin) return `a leg within ${m.toFixed(0)} deg of its fold`;
      const s = split(q), f1 = B1.fk(s.q1, ctx), f2 = B2.fk(s.q2, ctx);
      const n1 = V.unit(V.cross(f1.p2, f1.p3)), n2 = V.unit(V.cross(f2.p2, f1.p3));
      if (V.norm(V.cross(n1, n2)) < Math.sin(P.par * D)) return 'parallel singularity: the couplers line up at W';
      if (V.angle(f1.p2, f2.p2) < P.sep) return 'elbow pins collide';
      return null;
    },
    parts: (q, ctx) => {
      const s = split(q), f1 = B1.fk(s.q1, ctx), f2 = B2.fk(s.q2, ctx), ub = f1.p1, e1 = f1.p2, e2 = f2.p2, W = f1.p3;
      const fb = P.base, fw = P.fW, up = P.up, harm = ctx.armAxis, ng = P.neck_deg * D;
      const nk = V.unit(V.add(V.scale(W, Math.cos(ng)), V.scale(V.unit(V.reject(harm, W)), Math.sin(ng))));
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(nk, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base plate', c: V.scale(ub, fb - 3), z: ub, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 34], t: 3 },
        { kind: 'hub', role: 'active', name: 'A1 + A2 (coaxial double-row base hub)', c: V.scale(ub, fb), axis: ub, r: 12, h: 16 },
        { kind: 'arc', role: 'link', name: 'crank 1', u: ub, v: e1, r0: fb + up, r1: P.pins[0], r: 2.5 },
        { kind: 'arc', role: 'link', name: 'crank 2 (over crank 1)', u: ub, v: e2, r0: fb + 2 * up, r1: P.pins[1], r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'B1 elbow pin', c: V.scale(e1, P.pins[0]), axis: e1, r: 7, h: 8 },
        { kind: 'hub', role: 'passive', name: 'B2 elbow pin', c: V.scale(e2, P.pins[1]), axis: e2, r: 7, h: 8 },
        { kind: 'arc', role: 'link', name: 'coupler 1', u: e1, v: W, r0: P.pins[0] + up, r1: fw + up, r: 2.2 },
        { kind: 'arc', role: 'link', name: 'coupler 2 (over coupler 1)', u: e2, v: W, r0: P.pins[1] + up, r1: fw + 2 * up, r: 2.2 },
        { kind: 'hub', role: 'active', name: 'D arm roll (hub at W)', c: V.scale(W, fw), axis: W, r: 12, h: 16.3 },
        { kind: 'ring', role: 'passive', name: 'C coupler 2 about coupler 1', c: V.scale(W, fw + 2 * up + 1), axis: W, ref: V.perp(W), r: 14, t: 2.2 },
        { kind: 'plate', role: 'fixed-arm', name: 'arm-end plate', c: V.scale(W, fw - 2), z: W, x: harm, size: [34, 28], t: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: W, v: nk, r0: fw - 1, r1: fw - 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: V.scale(nk, fw - 1), b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
