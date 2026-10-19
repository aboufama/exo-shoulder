/* offset-flex-aligner - non-concurrent 3R on a COMPLIANT translation stage (catalogue offset-flex-aligner; ideated, no
 * model or sweep yet). Axis directions = the final's spherical 3R (b = bvec(32.55, 80.56), arcs 77.41 / 81.45,
 * W0 = wdir(71.38, 4.78), branch -1), so the orientation IK stays closed form; each axis LINE is moved |o_k| ~8 mm off
 * GH (the seed-offset bench optimum's offset pattern scaled to the spec's 10 mm cap; the spec's skin-normal tilts need
 * the scanned skin and are not applied). J3 sits on a FLOATING arm-end block; under it, Ti parallel-leaf flexures give
 * along-arm +-12, around-arm +-8 and radial +-4 mm (centring stiffness <= 0.4 N/mm) down to BOTTOM. The chain is
 * assembled at the rest pose with the stage centred, so the stage deflection = the chain's drift since rest.
 * 3 ACTIVE + 3 PASSIVE (mobility 3 + 3 + 3 - 6 = 3): every flexure coordinate is set by the arm. With these 8 mm
 * offsets the loop needs radial -8.8 / around +-10 mm: the +-4 / +-8 leaves bind in ~140 of 239 frames (the IK says so). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 32.55, el: 80.56, a: [77.41, 81.45], w: [71.38, 4.78], branch: -1,
              o: [[2.2, -7.7], [3.1, -7.4], [-0.5, 8.0]], lim: [12, 8, 4], faces: [54, 78, 70], hub_r: 10, stack: 12.25,
              stage: [60, 40, 6], sing: 10 };
  const C = K.sph3r(K.bvec(P.az, P.el), K.wdir(P.w[0], P.w[1]), P.a[0], P.a[1], P.branch), u = [C.u1, C.u2, C.u3];
  const nb = [u[1], u[2], u[1]], ea = u.map((x, k) => V.unit(V.reject(nb[k], x))), ec = u.map((x, k) => V.cross(x, ea[k]));
  const c = [0, 1, 2].map(k => V.add(V.scale(ea[k], P.o[k][0]), V.scale(ec[k], P.o[k][1])));     // axis-line feet (mm)
  const h0 = [0, -1, 0], sn = u[2], sa = V.unit(V.reject(h0, sn)), st = V.cross(sn, sa);            // stage: along, around, radial
  function fk(q) {                                           // member transforms about the axis LINES, scapula frame
    const R2 = M.rot(u[1], q[1]), R3 = M.rot(u[2], q[2]), R1 = M.rot(u[0], q[0]), R12 = M.mul(R1, R2);
    const t1 = V.sub(c[0], M.mulv(R1, c[0])), t2 = V.add(t1, M.mulv(R1, V.sub(c[1], M.mulv(R2, c[1]))));
    return { X1: [R1, t1], X2: [R12, t2], X3: [M.mul(R12, R3), V.add(t2, M.mulv(R12, V.sub(c[2], M.mulv(R3, c[2]))))] };
  }
  const ap = (X, p) => V.add(M.mulv(X[0], p), X[1]), Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  const drift = (q, Q) => M.mulv(M.T(Q), fk(q).X3[1]);                                               // in the arm rest frame
  const rc = K.makeCtx(K.KEYS[0].pose), d0 = drift(C.solve(rc), Qof(rc));                           // assembled at rest
  const sv = q => V.add(d0, V.add(V.add(V.scale(sa, q[3]), V.scale(st, q[4])), V.scale(sn, q[5])));
  function solve(ctx) {
    const q = C.solve(ctx), d = V.sub(drift(q, Qof(ctx)), d0);
    return q.concat([V.dot(d, sa), V.dot(d, st), V.dot(d, sn)]);
  }

  K.register({
    id: 'offset-flex-aligner',
    name: 'Offset 3R on a flexure stage',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['J1', 'J2', 'J3', 'flexure along the arm', 'flexure around the arm', 'flexure radial'], qUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    resUnits: ['deg', 'deg', 'deg', 'mm', 'mm', 'mm'],
    solve,
    residual: (q, ctx) => { const X = fk(q).X3, Q = Qof(ctx); return M.rotErrDeg(X[0], Q).concat(V.sub(X[1], M.mulv(Q, sv(q)))); },
    check: (q, ctx) => {
      const m = C.margin(ctx);
      if (m < 0) return 'J2 cannot close: the arm axis is out of reach';
      if (m < P.sing) return `J2 within ${m.toFixed(0)} deg of its fold`;
      const nm = ['along', 'around', 'radial'];
      for (let i = 0; i < 3; i++) if (Math.abs(q[3 + i]) > P.lim[i]) return `flexure ${nm[i]} past its +-${P.lim[i]} mm (${q[3 + i].toFixed(1)})`;
      return null;
    },
    parts: (q, ctx) => {
      const W = p => M.mulv(ctx.S, p), F = P.faces, h = P.stack, { X1, X2, X3 } = fk(q), Q = Qof(ctx), arm = p => W(M.mulv(Q, p));
      const hubs = [[0, [M.I3(), [0, 0, 0]]], [1, X1], [2, X2]].map(([k, X]) => {
        const ax = M.mulv(X[0], u[k]), p0 = ap(X, c[k]);
        return { kind: 'hub', role: 'active', name: `J${k + 1} (line ${V.norm(c[k]).toFixed(0)} mm off GH)`, c: W(V.madd(p0, ax, F[k])), axis: W(ax), r: P.hub_r, h };
      });
      const top = (hb, dz) => V.madd(hb.c, hb.axis, dz), arcPts = (a, b) => K.greatArc(a, b, V.norm(a), V.norm(b));
      const s = [q[3], q[4], q[5]], base = V.madd(c[2], u[2], F[2] - 9);                // BOTTOM-side stage centre (arm rest frame)
      const blk = ap(X3, V.madd(c[2], u[2], F[2] - 3)), Sx = P.stage[0] / 2, Sy = P.stage[1] / 2;
      const leaf = (dir, half, at, name, z, sz) => ({ kind: 'slider', role: 'passive', name, a: arm(V.madd(at, dir, -half)), b: arm(V.madd(at, dir, half)),
        at: arm(V.add(at, V.scale(dir, V.dot(V.sub(M.mulv(M.T(Q), W(blk)), at), dir)))), z: arm(z), size: sz });
      return [
        { kind: 'plate', role: 'fixed-scapula', c: W(V.madd(c[0], u[0], F[0] - 3)), z: W(u[0]), x: W([1, 0, 0]), size: [46, 32], t: 3 },
        hubs[0],
        { kind: 'arc', role: 'link', name: 'link 1', pts: arcPts(top(hubs[0], 7), V.madd(hubs[1].c, hubs[1].axis, 2)), r: 2.5 },
        hubs[1],
        { kind: 'arc', role: 'link', name: 'link 2', pts: arcPts(top(hubs[1], 9), top(hubs[2], h + 1)), r: 2.5 },
        hubs[2],
        { kind: 'plate', role: 'link', name: 'floating arm-end block (carries J3)', c: W(blk), z: W(M.mulv(X3[0], sn)), x: W(M.mulv(X3[0], sa)), size: [32, 26], t: 4 },
        { kind: 'plate', role: 'fixed-arm', name: 'Ti leaf stage under BOTTOM', c: arm(base), z: arm(sn), x: arm(sa), size: [P.stage[0], P.stage[1]], t: 2 },
        leaf(sa, Sx - 4, V.madd(base, sn, 1.5), 'leaf flexure along the arm (+-12)', sn, [10, Sy * 2 - 4, 2]),
        leaf(st, Sy - 4, V.madd(V.madd(base, sa, s[0]), sn, 3), 'leaf flexure around the arm (+-8)', sn, [Sx, 8, 2]),
        leaf(sn, P.lim[2] + 2, V.madd(V.madd(V.madd(base, sa, s[0]), st, s[1]), sn, 5), 'leaf pair radial (+-4)', sa, [8, 8, 3]),
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: arm(V.scale(h0, 160)), axis: arm(h0), r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
