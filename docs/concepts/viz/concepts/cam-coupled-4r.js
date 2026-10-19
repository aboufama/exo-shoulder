/* cam-coupled-4r - a spherical 4R whose spare is set by a roller on link 2's tail in a scapula-fixed groove
 * (catalogue cam-coupled-4r, docs/concepts/models/cam-coupled-4r.py, best configuration of docs/concepts/sweeps/).
 * J1 = bvec(az, el) in the scapula frame, J4 = wdir(wd, wa) in the humerus frame, arcs a1 / a2 / a3. The pin is fixed in
 * link 2 (polar tr from J2, azimuth tp from link 2's direction) and runs on the small circle {x . n = cos beta} of an
 * S-fixed spherical groove plate (the "eccentric J1 groove": n = J1 tilted by ecc). The pin depends on q1, q2 only, so
 * the slot is a law q2 = f(q1): J1, J3, J4 ACTIVE; J2, the pin's slide and its roll PASSIVE. Mobility 4 x 3 - 4 x 2 - 1
 * = 3. Solve = the model's IK: a 1 deg root scan of G(q1) = pin . n - cos beta on BOTH J3-dyad branches (the 4-bar
 * circuit crosses between them at its dead points), bisection, root nearest the previous frame. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { az: 74.006, el: 76.986, wd: 86.388, wa: -12.48, a1: 32.458, a2: 56.791, a3: 46.764, tr: 32.493, tp: 150.293,
              n_az: 48.168, n_el: 65.141, beta: 26.02, s_c: -107.614, s_half: 173.242, mode: -1, pa_min: 0.25,
              faces: [55, 64, 70, 66], hub_r: 10, stack: 12.25, slot_w: 14, neck_deg: 25, cuff_at: 165 };
  const u1 = K.bvec(P.az, P.el), W0 = K.wdir(P.wd, P.wa), ns = K.bvec(P.n_az, P.n_el), cb = Math.cos(P.beta * K.D2R);
  const ea = V.unit(V.reject([0, 1, 0], u1)), eb = V.cross(u1, ea);
  const se1 = V.unit(V.cross(ns, [0, 1, 0])), se2 = V.cross(ns, se1);
  const Qof = ctx => M.mul(M.T(ctx.S), ctx.H);
  function state(q1, s3, p4) {                       // scapula frame, q1 deg
    const p2 = V.unit(V.add(V.scale(u1, Math.cos(P.a1 * K.D2R)), V.scale(V.add(V.scale(ea, Math.cos(q1 * K.D2R)), V.scale(eb, Math.sin(q1 * K.D2R))), Math.sin(P.a1 * K.D2R))));
    const c = K.circInt(p2, P.a2, p4, P.a3, s3), p3 = c.p, pin = K.onCone(p2, p3, P.tr, P.tp);
    return { p2, p3, p4, pin, ok: c.ok, g: V.dot(pin, ns) - cb };
  }
  const slotS = pin => Math.atan2(V.dot(pin, se2), V.dot(pin, se1)) * K.R2D;
  function solve(ctx, qPrev) {
    const p4 = M.mulv(Qof(ctx), W0); let best = null;
    for (const s3 of [1, -1]) {
      let prev = state(-180, s3, p4);
      for (let t = -179; t <= 180; t++) {
        const cur = state(t, s3, p4);
        if (prev.ok && cur.ok && Math.sign(prev.g) !== Math.sign(cur.g) && s3 * Math.sign(cur.g - prev.g) === P.mode) {
          let lo = t - 1, hi = t, glo = prev.g;
          for (let i = 0; i < 40; i++) { const m = (lo + hi) / 2, gm = state(m, s3, p4).g; if (Math.sign(gm) === Math.sign(glo)) { lo = m; glo = gm; } else hi = m; }
          const r = (lo + hi) / 2, d = qPrev ? Math.abs(K.wrap180(r - qPrev[0])) + (s3 === qPrev[5] ? 0 : 0.5) : Math.abs(r);
          if (!best || d < best.d) best = { q1: r, s3, d };
        }
        prev = cur;
      }
    }
    if (!best) return qPrev ? qPrev.slice() : [0, 0, 0, 0, 0, 1];
    const s = state(best.q1, best.s3, p4);
    return [best.q1, K.axisAngle(s.p2, u1, s.p3), K.axisAngle(s.p3, s.p2, s.p4), K.axisAngle(s.p4, [0, -1, 0], s.p3), slotS(s.pin), best.s3];
  }
  const at = (q, ctx) => state(q[0], q[5], M.mulv(Qof(ctx), W0));
  K.register({
    id: 'cam-coupled-4r',
    name: 'Cam-coupled 4R (roller in a scapula groove)',
    dof: { active: 3, passive: 3 },
    params: P,
    q0: ctx => solve(ctx, null),
    qNames: ['J1', 'J2 (passive, slot law)', 'J3', 'J4', 'pin along the slot (passive)', 'J3-dyad branch'],
    qUnits: ['deg', 'deg', 'deg', 'deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => {
      const s = at(q, ctx);
      return [V.angle(s.p2, s.p3) - P.a2, V.angle(s.p3, s.p4) - P.a3, Math.acos(Math.max(-1, Math.min(1, V.dot(s.pin, ns)))) * K.R2D - P.beta];
    },
    check: (q, ctx) => {
      const s = at(q, ctx);
      if (!s.ok) return 'the 4R cannot close on the slot here';
      const nt = V.unit(V.reject(ns, s.pin)), t2 = V.cross(s.p2, s.pin), pa = Math.abs(V.dot(t2, nt)) / (V.norm(t2) || 1e-9);
      if (pa < P.pa_min) return `cam pressure angle: pin transmits ${pa.toFixed(2)} < ${P.pa_min}`;
      if (Math.abs(K.wrap180(slotS(s.pin) - P.s_c)) > P.s_half) return 'pin past the end of the cut slot';
      return null;
    },
    parts: (q, ctx) => {
      const s = at(q, ctx), S = ctx.S, W = d => M.mulv(S, d), F = P.faces, h = P.stack;
      const p = [u1, s.p2, s.p3, s.p4].map(W), pin = W(s.pin), harm = ctx.armAxis, ng = P.neck_deg * K.D2R;
      const nk = V.unit(V.add(V.scale(p[3], Math.cos(ng)), V.scale(V.unit(V.reject(harm, p[3])), Math.sin(ng))));
      const neckEnd = V.scale(nk, F[3] + 1), cuffC = V.scale(harm, P.cuff_at);
      const cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), RS = F[0] - 2;
      const nsW = W(ns), rho = RS * Math.sin(P.beta * K.D2R);
      return [
        { kind: 'plate', role: 'fixed-scapula', c: V.scale(p[0], F[0] - 3), z: p[0], x: W([1, 0, 0]), size: [46, 32], t: 3 },
        { kind: 'rail', role: 'fixed-scapula', name: 'groove plate (S-fixed)', c: V.scale(nsW, RS * Math.cos(P.beta * K.D2R)), axis: nsW,
          ref: W(se1), rho, a0: P.s_c - P.s_half, a1: P.s_c + P.s_half, r: 3, w: P.slot_w },
        { kind: 'hub', role: 'active', name: 'J1', c: V.scale(p[0], F[0]), axis: p[0], r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 1', u: p[0], v: p[1], r0: F[0] + 7, r1: F[1] + 2, r: 2.5 },
        { kind: 'hub', role: 'passive', name: 'J2 (slot law)', c: V.scale(p[1], F[1]), axis: p[1], r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2', u: p[1], v: p[2], r0: F[1] + 9, r1: F[2] + 2, r: 2.5 },
        { kind: 'arc', role: 'link', name: 'link 2 tail', u: p[1], v: pin, r0: F[1] + 9, r1: RS + 6, r: 2.2 },
        { kind: 'hub', role: 'passive', name: 'MR63 roller in the groove', c: V.scale(pin, RS), axis: pin, r: 3, h: 6 },
        { kind: 'hub', role: 'active', name: 'J3', c: V.scale(p[2], F[2]), axis: p[2], r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 3', u: p[2], v: p[3], r0: F[2] + 9, r1: F[3] + 2, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J4 (arm hub)', c: V.scale(p[3], F[3]), axis: p[3], r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: p[3], v: nk, r0: F[3] + 1, r1: F[3] + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
