/* seed-arc-rails - three concentric arc rails about GH, each a revolute joint with a REMOTE axis through GH (carriage
 * position = joint angle): a spherical 3R whose three joints are rail + carriage pairs instead of hubs
 * (docs/concepts/seed-arc-rails.md, models/seed-arc-rails.py; DEAD, converged best k438 / k441, gap 73.0). Axes: u1 =
 * bvec(-30, 80.68) on the scapula, u2 by the two-cone closure (a12 76.9, a23 66.75, branch -1), W = wdir(86.33, 21.83) on
 * the humerus. Rails are small crowns at polar rho about their axis on a sphere about GH: rail 1 (scapula, rho 12,
 * R 61.6, a full ring) -> carriage 1 -> link 1 -> rail 2 (on link 1, rho 20, R 170.9, 154 deg, cut round its mount: it
 * has to clear the raised arm, the measured limiter) -> carriage 2 -> link 2 -> carriage 3 riding the C-ring fixed to
 * the cuff (about W, rho 12, R 74.7, 304 deg, opening where carriage 3 never goes). Rail 2's and the ring's windows hold
 * their bench spans, centred on the carriages' range over this loop. Cuff slide along the humerus: PASSIVE, set by the
 * GH translation (0 on this fixed-GH rig). 3 active + 1 passive; closed form (KIN.sph3r). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { u_az: -30, u_el: 80.68, a12: 76.9, a23: 66.75, branch: -1, w_delta: 86.33, w_az: 21.83, rho: [12, 20, 12],
              R: [61.6, 170.9, 74.7], span2: 153.9, span3: 303.6, car: [20, 12, 8], margin: 10, slide: 30, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.u_az, P.u_el), K.wdir(P.w_delta, P.w_az), P.a12, P.a23, P.branch);
  const crown = (k, toward, rho) => V.add(V.scale(k, Math.cos(rho * D2R)), V.scale(V.unit(V.reject(toward, k)), Math.sin(rho * D2R)));
  const c1L = crown(C.u1, C.u2, P.rho[0]);                 // carriage 1 (body 1), on the side of u2
  const attL = crown(C.u2, c1L, P.rho[1]);                 // rail-2 mount (body 1): where link 1 holds rail 2
  const d2L = crown(C.u2, C.u3, P.rho[1]);                 // carriage 2 (body 2), toward the arm (phi2 = 0)
  const g0L = crown(C.u3, d2L, P.rho[2]);                  // carriage 3 (body 2) on the C-ring
  const refArm = V.unit(V.reject([0, -1, 0], K.wdir(P.w_delta, P.w_az)));   // ring azimuth 0 (humerus frame, down the arm)
  function frame(q, ctx) {
    const f = C.fk(q, ctx), S = ctx.S, b1 = M.mul(S, f.R1), b2 = M.mul(S, f.R12);
    const c1 = M.mulv(b1, c1L), att = M.mulv(b1, attL), d2 = M.mulv(b2, d2L), g = M.mulv(b2, g0L), ref3 = M.mulv(ctx.H, refArm);
    return Object.assign(f, { c1, att, d2, g, ref3, az2: K.axisAngle(f.p2, att, d2), az3: K.axisAngle(f.p3, ref3, g) });
  }
  let WIN = null;                                          // rail-2 and ring windows: bench spans centred on this loop's range
  function win() {
    if (WIN) return WIN;
    const a2 = [], a3 = [];
    for (const fr of K.motion(120)) { const ctx = K.makeCtx(fr.pose); if (C.margin(ctx) < P.margin) continue;
      const f = frame(C.solve(ctx), ctx); a2.push(((f.az2 % 360) + 360) % 360); a3.push(f.az3); }
    const mid = a => { const r = a[0], rel = a.map(x => K.wrap180(x - r)); return r + 0.5 * (Math.max(...rel) + Math.min(...rel)); };
    return (WIN = { c2: mid(a2), c3: K.wrap180(mid(a3)) });
  }
  const half = i => P.car[0] / 2 / (P.R[i] * Math.sin(P.rho[i] * D2R)) * K.R2D;   // carriage half arc on rail i (deg)

  K.register({
    id: 'seed-arc-rails',
    name: 'Three concentric arc rails about GH',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => C.solve(ctx).concat([0]),
    qNames: ['J1 carriage on rail 1', 'J2 carriage on rail 2', 'J3 carriage on the C-ring', 'cuff slide (passive)'],
    qUnits: ['deg', 'deg', 'deg', 'mm'], resUnits: ['deg', 'deg', 'deg', 'mm'],
    solve: ctx => C.solve(ctx).concat([0]),
    residual: (q, ctx) => C.residual(q, ctx).concat([q[3]]),   // every rail axis through GH: the slide = GH translation (0)
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const f = frame(q, ctx), w = win();
      if (Math.abs(K.wrap180(f.az2 - w.c2)) > P.span2 / 2 - half(1)) return 'carriage 2 past the end of rail 2';
      if (Math.abs(K.wrap180(f.az3 - w.c3)) > P.span3 / 2 - half(2)) return 'carriage 3 in the C-ring\'s gap';
      return null;
    },
    parts: (q, ctx) => {
      const f = frame(q, ctx), w = win(), R = P.R, rho = P.rho.map(x => x * D2R), ct = P.car[2];
      const rail = (role, name, k, Ri, rh, ref, a0, a1) => ({ kind: 'rail', role, name, c: V.scale(k, Ri * Math.cos(rh)), axis: k, ref,
        rho: Ri * Math.sin(rh), a0, a1, r: 2.6 });
      const car = (name, k, dir, Ri) => ({ kind: 'carriage', role: 'active', name, c: V.scale(dir, Ri + ct / 2 + 2), x: V.unit(V.cross(k, dir)), z: dir, size: P.car });
      const harm = ctx.armAxis, ringC = V.scale(f.p3, R[2] * Math.cos(rho[2]));
      const nk = V.madd(ringC, V.unit(V.reject(V.scale(f.g, -1), f.p3)), R[2] * Math.sin(rho[2]) + 3);    // ring mount, opposite the carriage side
      const sA = V.scale(harm, P.cuff_at - P.slide - 12), sB = V.scale(harm, P.cuff_at - 12), lat = V.unit(V.reject(nk, harm));
      const s0 = V.madd(sA, lat, 52), s1 = V.madd(sB, lat, 50);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler)', c: V.scale(f.p1, R[0] - 4), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 40], t: 3 },
        rail('fixed-scapula', 'rail 1 (full crown ring about u1)', f.p1, R[0], rho[0], f.c1, 0, 360),
        car('J1 carriage', f.p1, f.c1, R[0]),
        { kind: 'arc', role: 'link', name: 'link 1', pts: K.greatArc(f.c1, f.att, R[0] + ct + 2, R[1] + 3), r: 2.5 },
        rail('link', 'rail 2 (on link 1, about u2)', f.p2, R[1], rho[1], f.att, w.c2 - P.span2 / 2, w.c2 + P.span2 / 2),
        car('J2 carriage', f.p2, f.d2, R[1]),
        { kind: 'arc', role: 'link', name: 'link 2', pts: K.greatArc(f.d2, f.g, R[1] + ct + 2, R[2] + ct + 2), r: 2.5 },
        car('J3 carriage', f.p3, f.g, R[2]),
        rail('fixed-arm', 'C-ring about W (on the cuff)', f.p3, R[2], rho[2], f.ref3, w.c3 - P.span3 / 2, w.c3 + P.span3 / 2),
        { kind: 'link', role: 'fixed-arm', name: 'ring to slide', a: nk, b: s0, r: 3 },
        { kind: 'slider', role: 'passive', name: 'cuff slide along the humerus (passive)', a: s0, b: s1, at: V.madd(V.lerp(s0, s1, 0.5), harm, q[3]), z: lat, size: [14, 10, 5] },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: V.scale(harm, P.cuff_at), axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
