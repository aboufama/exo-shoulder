/* acromion-pointer-arm-ctrack - the user's own decomposition, as SCREENED (round J1, GATE 0; dead at 58.71 on
 * Bench(60,160) fast, k474). A 2-DOF gimbal at the shoulder POINTS the humerus, the humeral rotation is a third active joint
 * on the arm. J1 O20 hub at the BACK of the shoulder (a1 = bvec(-16.1, -20), scapula-fixed, through GH; the spec's
 * acromion-top seat needs a 20-60 % wider twist window, measured) -> L1 strap (92.8 deg) -> J2 O20 hub (97.4 deg from the
 * arm axis, branch +1: posterolateral at rest) -> L2 pointing yoke (follows the arm direction, not its twist) carrying
 * TWO shoes 79 deg apart on a fork (one tine each, merged at hub 2) -> an ARM-FIXED C-track at s 60.5 mm (deltoid) whose top is a CIRCULAR race about the humeral
 * axis, span -50.6..60.8 deg (the arm's torso-free arc, measured ~105 deg at every station), body skin-fitted under it,
 * merged into a shortened BOTTOM. Whichever shoe is on the race holds the twist (an open ring bearing with a carriage
 * pair spanning its gap). Active: J1, J2, the twist. Passive: NONE (the spec's radial slide + swivel need 20-34 mm of
 * skin-normal travel: replaced by the circular race). Out of range: gimbal within 5 deg of its fold, both shoes off the
 * track. Skin radius schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R, R2D = K.R2D;
  const P = { az1: -16.1, el1: -20, a12: 92.8, a23: 97.4, branch: 1, s_t: 60.5, span: [-50.6, 60.8], car_deg: 27.5, twin: 79.2,
              F1: 62, F2: 60, hub_r: 10, stack: 12.25, car: [24, 16, 7], margin: 5, cuff_at: 165 };
  P.take = [P.span[0] + P.car_deg / 2, P.span[1] - P.car_deg / 2];
  const e = [0, -1, 0], l = [0, 0, 1], bk = [-1, 0, 0];
  const Rs = th => 58 + 10 * Math.max(0, Math.cos((th - 30) * D2R));        // schematic skin radius about the humerus at s_t
  let Rr = 0; for (let th = P.span[0]; th <= P.span[1]; th += 2) Rr = Math.max(Rr, Rs(th) + 3);   // circular race radius
  const nrm = th => V.add(V.scale(l, Math.cos(th * D2R)), V.scale(bk, Math.sin(th * D2R)));
  const racePt = (th, dr) => V.madd(V.scale(e, P.s_t), nrm(th), Rr + (dr || 0));
  const skinPt = th => V.madd(V.scale(e, P.s_t), nrm(th), Rs(th) + 1);
  const a1 = K.bvec(P.az1, P.el1), d0 = e, u20 = K.circInt(a1, P.a12, d0, P.a23, P.branch).p;
  let thc0 = 0;                                                               // carriage angle in the pointing frame (from u2)
  function gimbal(ctx) {                                                     // closed form: J1, J2 from the arm direction
    const dS = M.mulv(M.T(ctx.S), ctx.armAxis), u2 = K.circInt(a1, P.a12, dS, P.a23, P.branch).p;
    const q1 = K.axisAngle(a1, u20, u2), R1 = M.rot(a1, q1), q2 = K.axisAngle(u2, M.mulv(R1, d0), dS);
    return [q1, q2];
  }
  const Rp = q => M.mul(M.rot(a1, q[0]), M.rot(u20, q[1]));                  // pointing frame (scapula coords)
  const cDir0 = () => { const t = V.cross(d0, u20), rr = V.sub(u20, V.scale(d0, V.dot(u20, d0)));
    const n = V.scale(rr, 1 / V.norm(rr)); return V.add(V.scale(n, Math.cos(thc0 * D2R)), V.scale(V.cross(d0, n), Math.sin(thc0 * D2R))); };
  const carArm = (q, ctx) => M.mulv(M.T(ctx.H), M.mulv(ctx.S, M.mulv(Rp(q), cDir0())));   // carriage direction in the arm frame
  const azim = Ya => Math.atan2(V.dot(Ya, bk), V.dot(Ya, l)) * R2D;
  function solve(ctx) { const g = gimbal(ctx); return [g[0], g[1], azim(carArm(g.concat([0]), ctx))]; }
  // centre the carriage window on the loop: median carriage angle = the middle of the take range
  (() => { const a = K.motion(240).map(f => solve(K.makeCtx(f.pose, f.t))[2]).sort((x, y) => x - y);
    thc0 = K.wrap180((P.take[0] + P.take[1]) / 2 - a[a.length >> 1]); })();

  K.register({
    id: 'acromion-pointer-arm-ctrack',
    name: 'Back gimbal + arm-fixed C-track, twin shoes',
    dof: { active: 3, passive: 0 },
    params: Object.assign({ race_r: Rr, carriage_angle_in_pointing_frame: thc0 }, P),
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'carriage on the C-track'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => {
      const dA = M.mulv(M.T(ctx.H), M.mulv(ctx.S, M.mulv(Rp(q), d0)));
      return [Math.asin(Math.max(-1, Math.min(1, dA[0]))) * R2D, Math.asin(Math.max(-1, Math.min(1, dA[2]))) * R2D,
              K.wrap180(azim(carArm(q, ctx)) - q[2])];
    },
    check: (q, ctx) => {
      const dS = M.mulv(M.T(ctx.S), ctx.armAxis), m = K.foldMargin(a1, dS, P.a12, P.a23);
      if (m < P.margin) return `gimbal within ${m.toFixed(0)} deg of its fold`;
      const on = t => t >= P.take[0] && t <= P.take[1];
      if (!on(q[2]) && !on(K.wrap180(q[2] + P.twin))) return 'both shoes off the C-track';
      return null;
    },
    parts: (q, ctx) => {
      const H = ctx.H, A = x => M.mulv(H, x), B1 = M.mulv(ctx.S, a1), R = M.mul(ctx.S, Rp(q)), U2 = M.mulv(R, u20);
      const th = q[2], n = A(nrm(th)), tg = A(nrm(th + 90)), harm = ctx.armAxis;
      const carC = A(racePt(th, P.car[2] / 2)), carTop = A(racePt(th, P.car[2]));
      const race = [], body = []; for (let t = P.span[0]; t <= P.span[1]; t += 5) { race.push(A(racePt(t))); body.push(A(skinPt(t))); }
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, A(l), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base plate (to the scapula handler)', c: V.madd(V.scale(B1, P.F1 - 3), ctx.attach.scapDir([-1, 0, 0]), 14), z: B1, x: ctx.attach.scapDir([-1, 0, 0]), size: [44, 24], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (back of the shoulder)', c: V.scale(B1, P.F1), axis: B1, r: P.hub_r, h: P.stack },
        { kind: 'arc', role: 'link', name: 'L1 strap (92.8 deg)', u: B1, v: U2, r0: P.F1 + 7, r1: P.F2 + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(U2, P.F2), axis: U2, r: P.hub_r, h: P.stack },
        { kind: 'arc', role: 'link', name: 'L2 fork tine 1 (to shoe 1)', u: U2, v: V.scale(carTop, 1 / V.norm(carTop)), r0: P.F2 + 9, r1: V.norm(carTop) + 2, r: 2.8 },
        { kind: 'carriage', role: 'active', name: 'shoe 1 on the circular race: position = humeral rotation', c: carC, x: tg, z: n, size: P.car },
        { kind: 'carriage', role: 'active', name: 'shoe 2 (rigid on L2, 79 deg on): holds the race when shoe 1 is off it', c: A(racePt(th + P.twin, P.car[2] / 2)), x: A(nrm(th + P.twin + 90)), z: A(nrm(th + P.twin)), size: P.car },
        { kind: 'arc', role: 'link', name: 'L2 fork tine 2 (to shoe 2)', u: U2, v: V.scale(A(racePt(th + P.twin, P.car[2])), 1 / V.norm(A(racePt(th + P.twin, P.car[2])))), r0: P.F2 + 9, r1: V.norm(A(racePt(th + P.twin, P.car[2]))) + 2, r: 2.8 },
        { kind: 'arc', role: 'fixed-arm', name: 'arm-fixed C-track: circular race', pts: race, r: 2 },
        { kind: 'arc', role: 'fixed-arm', name: 'track body skin face (saddle)', pts: body, r: 1.5 },
        { kind: 'link', role: 'fixed-arm', name: 'track bracket = shortened BOTTOM', a: A(racePt(30)), b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
