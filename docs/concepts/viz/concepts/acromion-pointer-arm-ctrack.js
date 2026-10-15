/* acromion-pointer-arm-ctrack - the user's own decomposition: a 2-DOF orthogonal gimbal at the shoulder POINTS the
 * humerus, and the humeral rotation gets its own joint lower on the arm. J1 O20 hub on the lateral acromion top (axis
 * a1 = sdir(40, 0), scapula-fixed, through GH) -> L1 strap -> J2 O20 hub (u2 _|_ a1 and _|_ the arm axis, branch -1:
 * behind the humeral head at rest) -> L2 short pointing yoke (follows the arm direction, not its twist) -> carriage
 * on an ARM-FIXED C-track at s_t 100 (deltoid insertion), shaped to the arm's skin at +4 mm, spanning -110..80 deg
 * (anteromedial -> lateral -> posterolateral, open medially), merged into a shortened BOTTOM. Active: J1, J2 and the
 * carriage's arc position (= the humeral rotation about the GH-elbow line). Passive (set by closure, cannot sag): the
 * carriage's radial slide and its swivel about an axis parallel to the humerus, both forced by the non-round track.
 * Catalogue entry (not modelled yet); the skin profile at s 100 is schematic (44 mm front / back, 52 lateral). Out of
 * range: arm within 10 deg of the gimbal pole, carriage off the track span [-103, 73]. Closed form, 3 active + 2 passive. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R, R2D = K.R2D;
  const P = { lat1: 40, lon1: 0, branch: -1, s_t: 100, span: [-110, 80], take: [-103, 73], centre: -15, gap: 4,
              F1: 52, F2: 60, hub_r: 10, stack: 12.25, car: [24, 16, 7], pole: 10, cuff_at: 165 };
  // this spec's conventions: sdir lon 0 lateral, +90 posterior; arm theta 0 lateral, +90 posterior (band frame)
  const sdir = (lat, lon) => [-Math.cos(lat * D2R) * Math.sin(lon * D2R), Math.sin(lat * D2R), Math.cos(lat * D2R) * Math.cos(lon * D2R)];
  const e = [0, -1, 0], l = [0, 0, 1], bk = [-1, 0, 0];
  const Rs = th => 44 + 8 * Math.cos(th * D2R) ** 2;                         // schematic skin radius about the humerus at s_t
  const Rtr = th => Rs(th) + P.gap + 1.5;                                    // track centreline (3 mm section)
  const nrm = th => V.add(V.scale(l, Math.cos(th * D2R)), V.scale(bk, Math.sin(th * D2R)));
  const trackPt = (th, dr) => V.madd(V.scale(e, P.s_t), nrm(th), Rtr(th) + (dr || 0));
  const swivel = th => Math.atan2(-8 * Math.sin(2 * th * D2R), Rtr(th)) * R2D;  // track normal vs the radial slide (deg)
  let rY = 0; for (let th = P.span[0]; th <= P.span[1]; th += 2) rY = Math.max(rY, Rs(th) + P.gap + 3 + 7);   // yoke end radius
  const a1 = sdir(P.lat1, P.lon1), d0 = e, u20 = K.circInt(a1, 90, d0, 90, P.branch).p, t0 = V.cross(d0, u20);
  let thc0 = 0;                                                               // carriage angle in the pointing frame
  const Y0 = () => V.add(V.scale(d0, P.s_t), V.scale(V.add(V.scale(u20, Math.cos(thc0 * D2R)), V.scale(t0, Math.sin(thc0 * D2R))), rY));

  function gimbal(ctx) {                                                     // closed form: J1, J2 from the arm direction
    const dS = M.mulv(M.T(ctx.S), ctx.armAxis), u2 = K.circInt(a1, 90, dS, 90, P.branch).p;
    const q1 = K.axisAngle(a1, u20, u2), R1 = M.rot(a1, q1), q2 = K.axisAngle(u2, M.mulv(R1, d0), dS);
    return [q1, q2];
  }
  const Rp = q => M.mul(M.rot(a1, q[0]), M.rot(u20, q[1]));                  // pointing frame (scapula coords)
  const yokeArm = (q, ctx) => M.mulv(M.T(ctx.H), M.mulv(ctx.S, M.mulv(Rp(q), Y0())));   // yoke end in the arm frame
  const azim = Ya => Math.atan2(V.dot(Ya, bk), V.dot(Ya, l)) * R2D;
  const slideOf = th => rY - (Rtr(th) + 1.5 + P.car[2]);
  function solve(ctx) {
    const g = gimbal(ctx), th = azim(yokeArm(g.concat([0]), ctx));
    return [g[0], g[1], th, slideOf(th), swivel(th)];
  }
  // centre the track on the loop: median carriage angle = P.centre
  (() => { const a = K.motion(240).map(f => solve(K.makeCtx(f.pose, f.t))[2]).sort((x, y) => x - y); thc0 = K.wrap180(P.centre - a[a.length >> 1]); })();

  K.register({
    id: 'acromion-pointer-arm-ctrack',
    name: 'Acromion gimbal + arm-fixed C-track',
    dof: { active: 3, passive: 2 },
    params: Object.assign({ yoke_r: rY, carriage_angle_in_pointing_frame: thc0 }, P),
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'carriage on the C-track', 'radial slide', 'swivel'], qUnits: ['deg', 'deg', 'deg', 'mm', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => {
      const dA = M.mulv(M.T(ctx.H), M.mulv(ctx.S, M.mulv(Rp(q), d0))), Ya = yokeArm(q, ctx);
      return [Math.asin(Math.max(-1, Math.min(1, dA[0]))) * R2D, Math.asin(Math.max(-1, Math.min(1, dA[2]))) * R2D,
              K.wrap180(azim(Ya) - q[2]), q[3] - slideOf(q[2]), q[4] - swivel(q[2])];
    },
    check: (q, ctx) => {
      const dS = M.mulv(M.T(ctx.S), ctx.armAxis), pole = Math.min(V.angle(dS, a1), 180 - V.angle(dS, a1));
      if (pole < P.pole) return `arm within ${pole.toFixed(0)} deg of the gimbal pole`;
      if (q[2] < P.take[0] || q[2] > P.take[1]) return 'carriage off the end of the C-track';
      return null;
    },
    parts: (q, ctx) => {
      const H = ctx.H, A = x => M.mulv(H, x), B1 = M.mulv(ctx.S, a1), R = M.mul(ctx.S, Rp(q)), U2 = M.mulv(R, u20);
      const th = q[2], Yw = M.mulv(R, Y0()), n = A(nrm(th)), tg = A(nrm(th + 90)), harm = ctx.armAxis;
      const carC = A(trackPt(th, 1.5 + P.car[2] / 2)), carTop = A(trackPt(th, 1.5 + P.car[2]));
      const track = []; for (let t = P.span[0]; t <= P.span[1]; t += 5) track.push(A(trackPt(t)));
      const cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, A(l), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'base plate (to the scapula handler)', c: V.madd(V.scale(B1, P.F1 - 3), ctx.attach.scapDir([-1, 0, 0]), 14), z: B1, x: ctx.attach.scapDir([-1, 0, 0]), size: [44, 24], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (acromion top)', c: V.scale(B1, P.F1), axis: B1, r: P.hub_r, h: P.stack },
        { kind: 'arc', role: 'link', name: 'L1 strap (90 deg)', u: B1, v: U2, r0: P.F1 + 7, r1: P.F2 + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2', c: V.scale(U2, P.F2), axis: U2, r: P.hub_r, h: P.stack },
        { kind: 'arc', role: 'link', name: 'L2 pointing yoke', u: U2, v: Yw, r0: P.F2 + 9, r1: V.norm(Yw), r: 2.8 },
        { kind: 'slider', role: 'passive', name: 'radial slide (set by the track)', a: carTop, b: V.madd(Yw, n, 4), at: Yw, z: tg, size: [10, 10, 6] },
        { kind: 'hub', role: 'passive', name: 'swivel (axis parallel to the humerus)', c: V.madd(carC, harm, -6), axis: harm, r: 5, h: 12 },
        { kind: 'carriage', role: 'active', name: 'carriage: position on the track = humeral rotation', c: carC, x: tg, z: n, size: P.car },
        { kind: 'arc', role: 'fixed-arm', name: 'arm-fixed skin-shaped C-track', pts: track, r: 2 },
        { kind: 'link', role: 'fixed-arm', name: 'track bracket = shortened BOTTOM', a: A(trackPt(0)), b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
