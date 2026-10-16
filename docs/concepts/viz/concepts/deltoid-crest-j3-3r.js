/* deltoid-crest-j3-3r - zero-passive spherical 3R with J3 moved ~25 deg higher on the arm, onto the DELTOID CREST just
 * below the lateral acromion edge (catalogue deltoid-crest-j3-3r, round 4, ideated; no verified number). Seed A of the
 * spec: J1 bvec(94.09, 61.93) on the anterior acromion top, nearly equal arcs a1 45.06 / a2 50.02, branch -1 (hub 2
 * parked over the posterior-superior cap, home near bvec(17, 46)), J3 humerus axis wdir(108.48, -6.87). Member 3 is
 * j3-neck-over-3r's INVERTED stack: link 2 is the lower (face) member at hub 3 and the cap plate + K7 neck the upper one,
 * bridging over link 2's swept zone to BOTTOM's bar (link 2 orbits hub 3 through ~340 deg). Hubs as the catalogue spec:
 * O15 slim (r 7.5, 12.25 mm stack); under the 2026-10-16 "O20 only" ruling a build would re-measure at O20. Closed form
 * (KIN.sph3r); red = within 5 deg of the J1-J3 fold (the user's MVP1 margin). Hub levels are schematic (49 / 56 / 72 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 94.09, el: 61.93, a1: 45.06, a2: 50.02, wd: 108.48, wa: -6.87, sigma: -1, margin: 5,
              F: [49, 56, 72], hub_r: 7.5, stack: 12.25, neck_lift: 15, cuff_at: 165 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.wd, P.wa), P.a1, P.a2, P.sigma);
  const WB = [0, -0.0713, 0.9975], DB = [0, -0.9975, -0.0713], BAR0 = V.add(V.scale(WB, 67.5), V.scale(DB, 40));
  const prof = (u, v, r0, r1, n) => K.greatArc(u, v, 1, 1, n).map((d, i) => V.scale(V.unit(d), r0 + (r1 - r0) * i / n));

  K.register({
    id: 'deltoid-crest-j3-3r',
    name: 'Deltoid-crest J3 equal-arc 3R (inverted J3 stack)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => C.solve(ctx),
    qNames: ['J1', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => C.solve(ctx),
    residual: (q, ctx) => C.residual(q, ctx),
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), F = P.F, h = P.stack, harm = ctx.armAxis;
      const bar0 = M.mulv(ctx.Hb, BAR0), barDn = M.mulv(ctx.Hb, DB);
      const top3 = F[2] + h + 2, neck = prof(f.p3, bar0, top3, Math.max(top3, V.norm(bar0) + P.neck_lift), 16);
      const neckEnd = neck[neck.length - 1], cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      const barEnd = V.madd(neckEnd, barDn, Math.max(20, V.dot(V.sub(cuffTop, neckEnd), barDn)));
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (scapula handler at the J1 hub ring)', c: V.scale(f.p1, F[0] - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [36, 28], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (O15, anterior acromion top)', c: V.scale(f.p1, F[0]), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1 (12 x 3 Ti, a1 45)', pts: prof(f.p1, f.p2, F[0] + 4, F[1] + 1.5, 16), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (O15, posterior-superior cap)', c: V.scale(f.p2, F[1]), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2 (12 x 3 Ti, a2 50; LOWER member at hub 3)', pts: prof(f.p2, f.p3, F[1] + 4.5, F[2] + 1.5, 16), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O15, deltoid crest, humerus-fixed axis)', c: V.scale(f.p3, F[2]), axis: f.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'member 3: cap plate + K7 neck (UPPER member, over link 2)', pts: neck, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: "BOTTOM's bar", a: neckEnd, b: barEnd, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'bar to cuff', a: barEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
