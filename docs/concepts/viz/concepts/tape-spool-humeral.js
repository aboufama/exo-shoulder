/* tape-spool-humeral - a 2R pointing chain + a carriage running on a self-stowing conformal humeral TAPE (catalogue
 * entry; not modelled yet, so the catalogue's model_spec is the source). J1 hub on the lateral acromion edge
 * (b = bvec(100, 20), the hub-able default, 18.6 deg singular margin), a1 = a2 = 90: link 2 carries the humerus long
 * axis. The third DOF, the arm's spin about its own axis, is the position of a carriage along a pre-shaped NiTi tape
 * (18 mm) that is ARM-FIXED 2-3 mm over the skin at station z = 100 mm, wrapped in the body-free window theta
 * -20..+62 deg (0 lateral, + posterior), anchored at the posterior end. The carriage rides link 2 through a PASSIVE
 * radial slide and a PASSIVE yaw pivot (the tape follows the non-round arm), and the tape behind it winds onto an O14
 * constant-force spool (PASSIVE, set by the carriage position): 3 ACTIVE + 3 PASSIVE, every passive set by closure.
 * Tape radius profile r_t(theta) is SCHEMATIC (46-52 mm deltoid section + 2.35). The carriage angle on link 2 puts the
 * rest pose at theta -9 (the layout that keeps most of the loop in the window); the loop spins the arm ~84 deg, more
 * than the window's 66 usable deg, so the extreme internal rotation (hand behind the back) is reported out of window.
 * Solved by the NUMERIC IK (8 residuals: pointing 3 deg, carriage on the tape 3 mm, yaw 1 deg, spool 1 deg). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { b_az: 100, b_el: 20, branch: 1, z: 100, win: [-20, 62], half_car: 8, rest_th: -9, anchor: 62, r_spool: 7, slide: 12,
              F1: 55, F2: 60, hub_r: 10, stack: 12.25, cuff_at: 185, sing: 15 };
  const u1 = K.bvec(P.b_az, P.b_el), h0 = [0, -1, 0], u2 = V.scale(V.unit(V.cross(u1, h0)), P.branch);
  const rt = th => 49 + 3 * Math.cos(2 * (th - 10) * K.D2R) + 2.35;                         // tape radius (mm)
  const drt = th => -6 * Math.sin(2 * (th - 10) * K.D2R);                                    // d r_t / d theta (per rad)
  const Rm = 52.4 + 2.35 + 9;                                                                // slide mount: max r_t + 9
  const yawOf = th => Math.atan2(drt(th), rt(th)) * K.R2D;
  const tapeLen = th => { let L = 0; const n = 16, d = (P.anchor - th) / n; for (let i = 0; i < n; i++) L += rt(th + (i + 0.5) * d) * d * K.D2R; return L; };
  const spoolOf = th => -tapeLen(th) / P.r_spool * K.R2D;
  /** 2R forward kinematics: link-2 frame (world): h (pointing axis), e2 (= J2 axis), e3 = h x e2 */
  function fk(q, ctx) {
    const R1 = M.rot(u1, q[0]), R12 = M.mul(R1, M.rot(u2, q[1])), X = M.mul(ctx.S, R12);
    const h = M.mulv(X, h0), e2 = M.mulv(X, u2);
    return { p1: M.mulv(ctx.S, u1), p2: e2, h, e2, e3: V.cross(h, e2) };
  }
  const dirL2 = (f, psi) => V.add(V.scale(f.e2, Math.cos(psi * K.D2R)), V.scale(f.e3, Math.sin(psi * K.D2R)));
  const armDir = (ctx, th) => ctx.attach.armDir([-Math.sin(th * K.D2R), 0, Math.cos(th * K.D2R)]);
  const tapePt = (ctx, th) => V.add(V.scale(ctx.armAxis, P.z), V.scale(armDir(ctx, th), rt(th)));
  /** closed-form 2R + arm spin (used for q0 and to centre the carriage on the window) */
  function closed(ctx) {
    const hS = M.mulv(M.T(ctx.S), ctx.armAxis), p2 = V.scale(V.unit(V.cross(u1, hS)), P.branch);
    const q1 = K.axisAngle(u1, u2, p2), q2 = K.axisAngle(u2, h0, M.mulv(M.T(M.rot(u1, q1)), hS));
    const f = fk([q1, q2], ctx), phi = K.axisAngle(f.h, f.e2, ctx.attach.armDir([0, 0, 1]));
    return { q1, q2, phi };
  }
  // carriage angle on link 2: the rest pose puts the carriage at rest_th, near the anterior end of the window, so
  // internal rotation (the larger excursion of the loop) runs toward the anchor (this layout keeps the most frames in)
  const psiC = P.rest_th + closed(K.makeCtx(K.motion(240)[0].pose)).phi;

  K.register({
    id: 'tape-spool-humeral',
    name: '2R + self-stowing humeral tape',
    dof: { active: 3, passive: 3 },
    params: Object.assign({ psi_c: psiC }, P),
    q0: ctx => { const c = closed(ctx), th = psiC - c.phi; return [c.q1, c.q2, th, Rm - 9 - rt(th), yawOf(th), spoolOf(th)]; },
    qNames: ['J1', 'J2', 'humeral (carriage on the tape, arm angle)', 'radial slide', 'yaw pivot', 'spool turn'],
    qUnits: ['deg', 'deg', 'deg', 'mm', 'deg', 'deg'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm', 'deg', 'deg'],
    residual: (q, ctx) => {
      const f = fk(q, ctx), d = dirL2(f, psiC);
      const pc = V.add(V.scale(f.h, P.z), V.scale(d, Rm - 9 - q[3]));                       // carriage contact (link 2 side)
      const point = V.scale(V.cross(f.h, ctx.armAxis), K.R2D);                              // pointing error (deg)
      return point.concat(V.sub(pc, tapePt(ctx, q[2])), [q[4] - yawOf(q[2]), q[5] - spoolOf(q[2])]);
    },
    check: (q, ctx) => {
      const a = V.angle(M.mulv(ctx.S, u1), ctx.armAxis);
      if (a < P.sing || a > 180 - P.sing) return `2R within ${Math.min(a, 180 - a).toFixed(0)} deg of its pointing singularity`;
      if (q[2] < P.win[0] + P.half_car || q[2] > P.win[1] - P.half_car) return 'carriage outside the body-free window';
      if (q[3] < 0 || q[3] > P.slide) return 'radial slide past its travel';
      return null;
    },
    parts: (q, ctx) => {
      const f = fk(q, ctx), h = P.stack, d = dirL2(f, psiC), th = q[2], ax = ctx.armAxis;
      const mount = V.add(V.scale(f.h, P.z), V.scale(d, Rm)), pc = V.add(V.scale(f.h, P.z), V.scale(d, Rm - 9 - q[3]));
      const tan = V.unit(V.sub(tapePt(ctx, th + 1), tapePt(ctx, th - 1))), tape = [];
      for (let i = 0; i <= 20; i++) tape.push(tapePt(ctx, th + (P.anchor - th) * i / 20));
      const spTh = th - 9, spC = V.add(V.scale(ax, P.z - 9), V.scale(armDir(ctx, spTh), rt(spTh) + 9));
      const cuffC = V.scale(ax, P.cuff_at);
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(f.p1, P.F1 - 3), z: f.p1, x: ctx.attach.scapDir([1, 0, 0]), size: [40, 30], t: 3 },
        { kind: 'hub', role: 'active', name: 'J1 (lateral acromion)', c: V.scale(f.p1, P.F1), axis: f.p1, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1', u: f.p1, v: f.p2, r0: P.F1 + 7, r1: P.F2 + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J2 (posterior shoulder)', c: V.scale(f.p2, P.F2), axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2 (down the posterolateral deltoid)', u: f.p2, v: V.unit(mount), r0: P.F2 + 9, r1: V.norm(mount) + 4, r: 2.5 },
        { kind: 'slider', role: 'passive', name: 'radial slide', a: V.madd(mount, d, 3), b: V.madd(mount, d, -9 - P.slide), at: V.madd(pc, d, 8), z: f.h, size: [8, 8, 4] },
        { kind: 'hub', role: 'passive', name: 'yaw pivot (parallel to the humerus)', c: V.madd(pc, d, 6), axis: f.h, r: 4, h: 3 },
        { kind: 'carriage', role: 'active', name: 'carriage on the tape (humeral DOF)', c: V.madd(pc, d, 3.9), x: tan, z: V.unit(V.cross(tan, ax)), size: [22, 20, 7] },
        { kind: 'arc', role: 'fixed-arm', name: 'NiTi tape (anchor -> carriage)', pts: tape, r: 1.2 },
        { kind: 'plate', role: 'fixed-arm', name: 'tape anchor', c: tapePt(ctx, P.anchor), z: armDir(ctx, P.anchor), x: ax, size: [10, 20], t: 3 },
        { kind: 'hub', role: 'passive', name: 'O14 constant-force spool', c: spC, axis: ax, r: P.r_spool, h: 18 },
        { kind: 'strap', role: 'fixed-arm', name: 'upper-arm cuff (BOTTOM side)', c: cuffC, axis: ax, r: 46, w: 24 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
