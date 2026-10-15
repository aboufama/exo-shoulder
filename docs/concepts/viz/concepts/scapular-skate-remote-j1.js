/* scapular-skate-remote-j1 - J1 is a PUCK gliding on a flat plate on the back of the shoulder (catalogue entry; ideated,
 * no bench model yet). The plate (3 mm Ti) lies parallel to the posterior scapular skin plane, normal n = sdir(27, 75)
 * in the scapula frame, top 65 mm from GH; the puck (disc r 25, 6 tall, on a ball cage under a lip) has 3 planar
 * coordinates: its turn about the plate normal THROUGH GH is the active J1 (a remote axis, no hub), its 2 in-plane
 * translations are PASSIVE and set by closure: J2's axis (an O20 hub on the puck, tilted 55 deg to the plate) must pass
 * through GH because L2, J3 and the arm are concurrent there. L2 strap -> J3 O20 hub on w = armpt(30, 40, 80) (humerus,
 * posterolateral), alpha12 55, alpha23 90, branch -1 (rest: puck on the infraspinatus ~90 mm from the foot of GH) ->
 * neck to BOTTOM's top (armpt(65, 0, 50)) -> cuff. Solved by the NUMERIC IK: unknowns q1..q3 (deg) + the puck slip x, y
 * (mm, plate frame: x down the plate, y lateral); residual = the chain end vs the humerus (3 deg) + J2's axis line vs
 * GH (3 mm). Plate 130 x 90 (the sweep's largest) centred on the puck's path over this loop, long side along its chord;
 * "puck off the plate" = puck centre within 25 mm of the outline (the catalogue's main risk), fold margin 8 deg.
 * Hub faces (J3 60 mm) schematic. 3 active + 2 passive. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R;
  const sdir = (lat, lon) => [-Math.cos(lat * D2R) * Math.sin(lon * D2R), Math.sin(lat * D2R), Math.cos(lat * D2R) * Math.cos(lon * D2R)];
  const P = { n: [27, 75], top: 65, a12: 55, a23: 90, branch: -1, w: [30, 40, 80], margin: 8, plate: [130, 90], edge: 25,
              puck_r: 25, puck_h: 6, F3: 60, hub_r: 10, stack: 12.25, bottom: [65, 0, 50], cuff_at: 165 };
  const n = sdir(...P.n), eA = V.unit(K.BODY.elbow), lA = [0.004, 0.164, 0.986], bA = [-1, 0.023, 0];
  const armpt = (s, th, r) => V.add(V.scale(eA, s), V.scale(V.add(V.scale(lA, Math.cos(th * D2R)), V.scale(bA, Math.sin(th * D2R))), r));
  const wB = M.mulv(M.T(K.BODY.rest_humerus), V.unit(armpt(...P.w)));       // body_pose humerus frame -> band frame
  const C = K.sph3r(n, wB, P.a12, P.a23, P.branch);
  const e1 = V.unit(V.reject([0, -1, 0], n)), e2 = V.cross(n, e1);             // plate frame (scapula): down, lateral
  const plane = (x, y, dz) => V.add(V.scale(n, P.top + (dz || 0)), V.add(V.scale(e1, x), V.scale(e2, y)));
  /** the puck point where J2's axis must pierce the plate top (closed form, scapula frame) */
  const pierce = (ctx, p2) => { const u = M.mulv(M.T(ctx.S), p2), Pp = V.scale(u, P.top / V.dot(u, n)); return [V.dot(Pp, e1), V.dot(Pp, e2)]; };
  let PL = null;
  function plate() {                                       // plate centre + long-side direction from the puck's path on this loop
    if (PL) return PL;
    const pts = []; for (const f of K.motion(120)) { const ctx = K.makeCtx(f.pose); if (C.margin(ctx) < P.margin) continue;
      pts.push(pierce(ctx, C.fk(C.solve(ctx), ctx).p2)); }
    const c = [0, 1].map(j => pts.reduce((s, p) => s + p[j], 0) / pts.length);
    let sxx = 0, sxy = 0, syy = 0; for (const p of pts) { const dx = p[0] - c[0], dy = p[1] - c[1]; sxx += dx * dx; sxy += dx * dy; syy += dy * dy; }
    const th = 0.5 * Math.atan2(2 * sxy, sxx - syy);
    return (PL = { c, u: [Math.cos(th), Math.sin(th)], v: [-Math.sin(th), Math.cos(th)] });
  }

  K.register({
    id: 'scapular-skate-remote-j1',
    name: 'Scapular skate (puck J1 on a back plate)',
    dof: { active: 3, passive: 2 },
    params: P,
    q0: ctx => { const q = C.solve(ctx); return q.concat(pierce(ctx, C.fk(q, ctx).p2)); },
    qNames: ['J1 puck turn (remote axis)', 'J2 hub (on the puck)', 'J3 hub', 'puck slip down (passive)', 'puck slip lateral (passive)'],
    qUnits: ['deg', 'deg', 'deg', 'mm', 'mm'], resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    residual: (q, ctx) => {
      const f = C.fk(q, ctx), Pc = M.mulv(ctx.S, plane(q[3], q[4]));
      return C.residual(q, ctx).concat(V.reject(Pc, f.p2));                   // J2's axis through the puck must hit GH
    },
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm is out of the chain\'s reach';
      if (m < P.margin) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const L = plate(), d = [q[3] - L.c[0], q[4] - L.c[1]], a = d[0] * L.u[0] + d[1] * L.u[1], b = d[0] * L.v[0] + d[1] * L.v[1];
      if (Math.abs(a) > P.plate[0] / 2 - P.edge || Math.abs(b) > P.plate[1] / 2 - P.edge) return 'puck off the plate (within 25 mm of its edge)';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = p => M.mulv(S, p), f = C.fk(q, ctx), L = plate(), nW = W(n), h = P.stack;
      const pc = plane(q[3], q[4]), r2 = (P.top + 0.5 + P.puck_h) / Math.max(0.2, V.dot(f.p2, nW));   // J2 hub on the puck top, along p2
      const j2 = V.scale(f.p2, r2), j3 = V.scale(f.p3, P.F3);
      const bot = M.mulv(ctx.Hb, armpt(...P.bottom)), harm = ctx.armAxis, cuffC = V.scale(harm, P.cuff_at);
      const cuffTop = V.madd(cuffC, V.unit(V.reject(bot, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'back plate (scapula handler)', c: W(plane(L.c[0], L.c[1], -1.5)), z: nW,
          x: W(V.add(V.scale(e1, L.u[0]), V.scale(e2, L.u[1]))), size: P.plate, t: 3 },
        { kind: 'point', role: 'active', name: 'J1 remote axis foot (plate normal through GH)', p: W(plane(0, 0, 0.5)), r: 3 },
        { kind: 'ring', role: 'passive', name: 'ball cage (passive in-plane slip, set by closure)', c: W(plane(q[3], q[4], 1)), axis: nW, r: P.puck_r + 3, t: 1.5 },
        { kind: 'hub', role: 'active', name: 'J1 puck (turns about the plate normal through GH)', c: W(plane(q[3], q[4], 0.5)), axis: nW, p0: W(pc), r: P.puck_r, h: P.puck_h },
        { kind: 'hub', role: 'active', name: 'J2 (O20 on the puck, 55 deg tilt)', c: j2, axis: f.p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'L2 strap', pts: K.greatArc(V.madd(j2, f.p2, h + 1), V.madd(j3, f.p3, h + 1), r2 + h + 1, P.F3 + h + 1), r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (O20, posterolateral arm)', c: j3, axis: f.p3, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck to BOTTOM', pts: K.greatArc(j3, bot, P.F3 + 1, V.norm(bot)), r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM to cuff', a: bot, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
