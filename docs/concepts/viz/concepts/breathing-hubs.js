/* breathing-hubs - the final spherical 3R (r18 s1392 #1: catalogue chain) whose J2 and J3 hub blocks ride short
 * radial parallelogram stages along their OWN axes (docs/concepts/models/breathing-hubs.py, catalogue entry).
 * Every axis passes through GH, so a lift along an axis changes no axis direction and no joint angle: the 3 hub angles
 * are the plain 3R closure (closed form) and the two lifts are PASSIVE, each slaved to a joint angle by a positive
 * groove face cam: lift2 = c2(q1) (cam ring around J1 on the base, follower + pushrod along link 1 to the J2 stage),
 * lift3 = c3(q3) (cam ring around J3 on link 2's arm end, follower on BOTTOM's stage). The model was interrupted before
 * a cam was fitted, so the cams here are SCHEMATIC: zero lift at the rest pose's cam input, rising toward the input
 * the loop's overhead pose needs (J2 over the medial scapula) and toward the q3 of the behind-back pose (arm hub over
 * the bunched posterior deltoid) at the spec's slope limit (12 mm/rad, piecewise linear like the model's slope-limited
 * majorant), capped at the travel T. The slope limit is what bounds the lift on this loop (overhead is only ~33 deg of
 * q1 from rest: ~7 mm). Links S-bend between the fixed J1 radius and the lifted hubs. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V;
  const P = { az: 32.55159237005438, el: 80.5631251310032, a: [77.40737955825345, 81.44799921589232],
              w: [71.38254048198503, 4.778729451604692], branch: -1, sing_deg: 10,
              F1: 54, F2_0: 64, F3_0: 68, T2: 12, T3: 8, slope: 12, hub_r: 10, stack: 12.25,
              neck_deg: 25, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch);
  // cam inputs: zero lift at the rest pose, rising toward the overhead (q1) / behind-back (q3) key poses
  const keyQ = k => C.solve(K.makeCtx(K.KEYS.find(x => x.key === k).pose));
  const q0r = keyQ('rest'), q1pk = keyQ('overhead')[0], q3pk = keyQ('behind')[2];
  /** positive cam (piecewise linear, slope P.slope mm/rad): 0 on the rest side of q0, T beyond, toward pk */
  const cam = (q, q0, pk, T) => Math.max(0, Math.min(T, P.slope * K.D2R * Math.sign(pk - q0) * K.wrap180(q - q0)));
  const c2 = q => cam(q[0], q0r[0], q1pk, P.T2), c3 = q => cam(q[2], q0r[2], q3pk, P.T3);
  const ss = u => u * u * (3 - 2 * u);
  /** strap along the great circle u -> v whose radius blends r0 -> r1 by smoothstep (the S-bend over a stage) */
  function sArc(u, v, r0, r1, n) {
    const g = K.greatArc(u, v, 1, 1, n || 18), m = g.length - 1;
    return g.map((p, i) => V.scale(p, r0 + (r1 - r0) * ss(i / m)));
  }

  K.register({
    id: 'breathing-hubs',
    name: 'Breathing hubs (cam-slaved radial stages)',
    dof: { active: 3, passive: 2 },
    params: P,
    q0: ctx => { const q = C.solve(ctx); return q.concat([c2(q), c3(q)]); },
    qNames: ['J1', 'J2', 'J3', 'J2 lift (cam on q1)', 'J3 lift (cam on q3)'], qUnits: ['deg', 'deg', 'deg', 'mm', 'mm'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm'],
    solve: ctx => { const q = C.solve(ctx); return q.concat([c2(q), c3(q)]); },
    residual: (q, ctx) => C.residual(q, ctx).concat([q[3] - c2(q), q[4] - c3(q)]),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach';
      if (m < P.sing_deg) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), h = P.stack, F2 = P.F2_0 + q[3], F3 = P.F3_0 + q[4];
      const harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(f.p3, Math.cos(ng)), V.scale(V.unit(V.reject(harm, f.p3)), Math.sin(ng))));
      const neckEnd = V.scale(nk, F3 + 1);
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      // link 1 root direction (just off J1's rim) for the follower and the pushrod
      const r1 = K.greatArc(f.p1, f.p2, 1, 1, 18)[3];
      const stage = (p, F0, T, lift, name) => ({ kind: 'slider', role: 'passive', name, a: V.scale(p, F0 - 3), b: V.scale(p, F0 + T + 3),
        at: V.scale(p, F0 + lift - 2), z: V.perp(p), size: [14, 12, 4] });
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(f.p1, P.F1 - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'ring', role: 'fixed-scapula', name: 'cam ring c2(q1) around J1', c: V.scale(f.p1, P.F1), axis: f.p1, r: 15 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(f.p1, P.F1), axis: f.p1, r: P.hub_r, h },
        { kind: 'point', role: 'passive', name: 'cam follower (link 1 root)', p: V.scale(r1, P.F1 + 4), r: 2.5 },
        { kind: 'arc', role: 'link', name: 'link 1 (S-bends onto the J2 stage)', pts: sArc(f.p1, f.p2, P.F1 + 7, F2 + 2), r: 2.5 },
        { kind: 'arc', role: 'passive', name: 'pushrod to the J2 bell crank', pts: sArc(r1, f.p2, P.F1 + 11, F2 + 5, 14), r: 0.9 },
        stage(f.p2, P.F2_0, P.T2, q[3], 'J2 radial stage (lift = c2(q1))'),
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(f.p2, F2), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2 (follows both lifts)', pts: sArc(f.p2, f.p3, F2 + 9, F3 + h + 2), r: 2.5 },
        { kind: 'ring', role: 'link', name: 'cam ring c3(q3) on link 2', c: V.scale(f.p3, F3 + h), axis: f.p3, r: 15 },
        stage(f.p3, P.F3_0, P.T3, q[4], 'J3 radial stage (lift = c3(q3))'),
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(f.p3, F3), axis: f.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck (BOTTOM)', u: f.p3, v: nk, r0: F3 + 1, r1: F3 + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
