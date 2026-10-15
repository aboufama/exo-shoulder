/* cuff-sleeve-3r - spherical 3R whose twist joint is not a ring around the arm but a GH-aimed ROD-AND-SLEEVE down by
 * the cuff: J1 O20 hub on the anterior acromion (p1 = unit(0.46, 0.84, 0.30), scapula-fixed), link 1 (64 deg arc) to
 * the J2 O20 hub riding around the shoulder cap, link 2 over the deltoid cap and down the lateral arm to a short O5 rod
 * coaxial with the arm-fixed line e3 through GH (13.6 deg off the humerus axis toward lateral, grazing the lateral arm
 * at s 230); J3 = the O11 x 30 sleeve on a cuff bracket turning about e3 (a23 = 90), with a +-5 mm axial float
 * (PASSIVE P along e3: with GH fixed the rod's distance from GH never changes, so closure holds it at 0 - it only takes
 * up GH translation). Catalogue entry (not modelled yet), branch -1 (J2 lateral-superior at rest). Out of range: fold
 * margin < 10 deg, the arm axis within 15 deg of +-p1, J3 more than 100 deg from its loop median. Red team: link 2
 * turns about e3 relative to the arm, so its straight run swings medially - in the behind-the-back transition it
 * passes 32 mm from the humerus axis at s 115 (inside the ~45 mm arm): the 'link 2 path' the sweep must settle.
 * Closed form (KIN.sph3r) + the determined float: 3 active, 1 passive. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const P = { p1: [0.46, 0.84, 0.30], a12: 64, a23: 90, gamma: 13.6, psi3: 0, sb: -1, s3: 230, rod: [200, 260], sleeve: [5.5, 30],
              float: 5, rho1: 58, rho2: 62, cap_beta: 42, hub_r: 10, stack: 12.25, margin: 10, j3_cap: 100, cuff_at: 165 };
  const p1 = V.unit(P.p1), e3 = K.wdir(P.gamma, P.psi3);
  const C = K.sph3r(p1, e3, P.a12, P.a23, P.sb);
  const j3med = (() => { const a = K.motion(240).map(f => C.solve(K.makeCtx(f.pose, f.t))[2]).sort((x, y) => x - y); return a[a.length >> 1]; })();

  K.register({
    id: 'cuff-sleeve-3r',
    name: 'Cuff-sleeve 3R (GH-aimed rod-and-sleeve twist joint)',
    dof: { active: 3, passive: 1 },
    params: P,
    q0: ctx => C.solve(ctx).concat([0]),
    qNames: ['J1', 'J2', 'J3 sleeve', 'sleeve float'], qUnits: ['deg', 'deg', 'deg', 'mm'], resUnits: ['deg', 'deg', 'deg', 'mm'],
    solve: ctx => C.solve(ctx).concat([0]),                 // the float is set by closure: rod and sleeve both sit s3 from GH
    residual: (q, ctx) => C.residual(q, ctx).concat([q[3]]),
    check: (q, ctx) => {
      const m = C.margin(ctx), E3 = M.mulv(ctx.H, e3), P1 = M.mulv(ctx.S, p1);
      if (m < 0) return 'J2 cannot close: the arm axis is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      if (Math.min(V.angle(P1, E3), 180 - V.angle(P1, E3)) < 15) return 'e3 within 15 deg of the J1 axis';
      if (Math.abs(K.wrap180(q[2] - j3med)) > P.j3_cap) return 'J3 sleeve past its travel';
      if (Math.abs(q[3]) > P.float) return 'sleeve float past its travel';
      return null;
    },
    parts: (q, ctx) => {
      const f = C.fk(q, ctx), E3 = f.p3, harm = ctx.armAxis, s1 = ctx.attach.scapDir([1, 0, 0]);
      // link 2: over the cap from J2 toward e3 (great circle at the cap radius), then straight down to the rod top
      const capDir = K.onCone(E3, f.p2, P.cap_beta, 0), capPt = V.scale(capDir, P.rho2 + 4);
      const rodTop = V.scale(E3, P.rod[0] + q[3]), rodEnd = V.scale(E3, P.rod[1] + q[3]);
      const sl0 = V.scale(E3, P.s3 - P.sleeve[1] / 2);
      // bracket side: toward the arm axis from the sleeve
      const inw = V.unit(V.reject(V.sub(V.scale(harm, P.s3), V.scale(E3, P.s3)), E3));
      const fl = s => V.madd(V.scale(E3, P.s3 + s), inw, 9);
      const cuffC = V.scale(harm, P.cuff_at + 40), cuffTop = V.madd(cuffC, V.unit(V.reject(fl(0), harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base (anterior acromion)', c: V.scale(f.p1, P.rho1 - 3), z: f.p1, x: s1, size: [40, 28], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(f.p1, P.rho1), axis: f.p1, r: P.hub_r, h: P.stack },
        { kind: 'arc', role: 'link', name: 'link 1 (64 deg)', u: f.p1, v: f.p2, r0: P.rho1 + 7, r1: P.rho2 + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(f.p2, P.rho2), axis: f.p2, r: P.hub_r, h: P.stack },
        { kind: 'arc', role: 'link', name: 'link 2 over the deltoid cap', u: f.p2, v: capDir, r0: P.rho2 + 9, r1: P.rho2 + 4, r: 2.5 },
        { kind: 'link', role: 'link', name: 'link 2 down the lateral arm', a: capPt, b: rodTop, r: 2.5 },
        { kind: 'link', role: 'link', name: 'O5 rod on e3 (aimed at GH)', a: rodTop, b: rodEnd, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3: sleeve bearing about e3', c: sl0, axis: E3, r: P.sleeve[0], h: P.sleeve[1] },
        { kind: 'slider', role: 'passive', name: 'sleeve axial float (set by closure)', a: fl(-P.float - 6), b: fl(P.float + 6), at: fl(q[3]), z: inw, size: [12, 8, 4] },
        { kind: 'link', role: 'fixed-arm', name: 'cuff bracket', a: fl(0), b: cuffTop, r: 2.5 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 45, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
