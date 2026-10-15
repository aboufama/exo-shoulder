/* base-rail-tripod - spherical 3-PRR (Hexaglide-like): three curved RAILS fixed on the scapula base, a carriage on each
 * (ACTIVE curved P), and from each carriage a rigid FIXED-LENGTH leg arc over the shoulder cap to a pivot on an arm
 * plate on the deltoid (catalogue base-rail-tripod; ideated, no bench model yet: the model_spec defaults). Leg i:
 * rail c_i(t) = cos t r1_i + sin t r2_i (t in [0, T_i]) -> carriage pivot (passive R, radial) -> leg arc of fixed
 * angular length L_i -> arm pivot (passive R, radial) at a_i. 3 ACTIVE + 6 PASSIVE (M = 3: 7 bodies, 9 joints). Closed
 * form per leg: alpha = r1 . a, beta = r2 . a, t = atan2(beta, alpha) +- acos(cos L / hypot) on the branch inside
 * [0, T] at the reference pose. Rails: the spec's (acromion top -> medial spine 55 deg, anterior acromion ->
 * supraspinatus 50, lateral acromion rim 50); arm points as dome-telescope-tripod (anterior / lateral / posterior
 * deltoid, humerus band frame); L_i = angle(c_i(T_i / 2), a_i) at a mid pose (plane 30, elev 45, axial -15; the
 * spec's median clip pose). Pairing: of the 6 rail -> arm-point pairings x 4 mid poses, spine rail -> lateral leg,
 * acromion rail -> anterior, rim rail -> posterior keeps the most of the loop. Working range: t in [0, T], serial
 * |tau . m| >= 0.25, parallel |det| >= 0.1. Measured on the loop (the catalogue's risk, quantified): only 155 / 239
 * frames close at all (a fixed-length leg cannot reach the arm point, 27 of the misses overhead) and 52 stay on the
 * rails; following the closing frames needs t from -46..78 / -105..118 / -119..61 deg, i.e. rails of ~125 / 225 / 180
 * deg against the spec's 55 / 50 / 50. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const RAIL = [[[-0.36, 0.93, 0.09], [-0.85, 0.35, -0.40], 55], [[0.40, 0.88, 0.25], [-0.20, 0.85, -0.48], 50],
                [[0.30, 0.80, 0.52], [-0.55, 0.72, 0.42], 50]];
  const A = [[0, -0.2, 0.98], [0.85, -0.2, 0.49], [-0.85, -0.2, 0.49]].map(V.unit);    // lateral, anterior, posterior deltoid
  const P = { rails: RAIL, a: A, mid: { plane: 30, elev: 45, axial: -15, flex: 20 }, Rr: [56, 58, 55], Ra: [62, 62, 60],
              stack: 9, serial: 0.25, det: 0.1, cuff_at: 165 };
  const legs = RAIL.map(([s, e, T]) => { const r1 = V.unit(s); return { r1, r2: V.unit(V.reject(V.unit(e), r1)), T }; });
  const cdir = (l, t) => V.add(V.scale(l.r1, Math.cos(t * D)), V.scale(l.r2, Math.sin(t * D)));
  const armS = (ctx, i) => M.mulv(M.mul(M.T(ctx.S), ctx.H), A[i]);                       // arm point dir, scapula frame
  const two = (l, a, L) => { const al = V.dot(l.r1, a), be = V.dot(l.r2, a), rho = Math.hypot(al, be);
    const x = Math.max(-1, Math.min(1, Math.cos(L * D) / rho)), base = Math.atan2(be, al) * K.R2D, d = Math.acos(x) * K.R2D;
    return [base + d, base - d]; };
  const cm = K.makeCtx(Object.assign({ pron: 0 }, P.mid), 0);
  legs.forEach((l, i) => {
    l.L = V.angle(cdir(l, l.T / 2), armS(cm, i));
    const ts = two(l, armS(cm, i), l.L); l.br = Math.abs(K.wrap180(ts[0] - l.T / 2)) < Math.abs(K.wrap180(ts[1] - l.T / 2)) ? 0 : 1;
  });
  const solve = ctx => legs.map((l, i) => { const t = two(l, armS(ctx, i), l.L)[l.br]; return l.T / 2 + K.wrap180(t - l.T / 2); });
  const nm = ['lateral leg (spine rail)', 'anterior leg (acromion rail)', 'posterior leg (rim rail)'];

  K.register({
    id: 'base-rail-tripod',
    name: 'Base-rail tripod (3-PRR)',
    dof: { active: 3, passive: 6 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['carriage 1 (spine rail)', 'carriage 2 (acromion rail)', 'carriage 3 (rim rail)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => legs.map((l, i) => V.angle(cdir(l, q[i]), armS(ctx, i)) - l.L),
    check: (q, ctx) => {
      for (let i = 0; i < 3; i++) {
        if (q[i] < 0 || q[i] > legs[i].T) return `${nm[i]} carriage off its rail (${q[i].toFixed(0)} deg of ${legs[i].T})`;
        const c = cdir(legs[i], q[i]), tau = V.cross(V.unit(V.cross(legs[i].r1, legs[i].r2)), c), m = V.unit(V.reject(armS(ctx, i), c));
        if (Math.abs(V.dot(tau, m)) < P.serial) return `${nm[i]} leg square to its rail (serial singularity)`;
      }
      const n = legs.map((l, i) => V.unit(V.cross(cdir(l, q[i]), armS(ctx, i)))), d = Math.abs(V.dot(n[0], V.cross(n[1], n[2])));
      return d < P.det ? `parallel singularity (|det| ${d.toFixed(2)})` : null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, W = d => M.mulv(S, d), out = [], ap = [];
      legs.forEach((l, i) => {
        const ax = W(V.cross(l.r1, l.r2)), c = W(cdir(l, q[i])), a = M.mulv(ctx.H, A[i]), tg = V.cross(ax, c);
        ap.push(V.scale(a, P.Ra[i]));
        out.push({ kind: 'rail', role: 'fixed-scapula', name: `rail ${i + 1}`, c: [0, 0, 0], axis: ax, ref: W(l.r1), rho: P.Rr[i], a0: 0, a1: l.T, r: 2.6 });
        out.push({ kind: 'carriage', role: 'active', name: `carriage ${i + 1} (${nm[i]})`, c: V.scale(c, P.Rr[i] + 4), x: tg, z: c, size: [16, 14, 5] });
        out.push({ kind: 'hub', role: 'passive', name: `carriage pivot ${i + 1}`, c: V.scale(c, P.Rr[i] + 6.5), axis: c, r: 6, h: 3 });
        out.push({ kind: 'arc', role: 'link', name: `leg ${i + 1} (fixed length ${l.L.toFixed(0)} deg)`, u: c, v: a, r0: P.Rr[i] + P.stack, r1: P.Ra[i] + 4, r: 2.5 });
        out.push({ kind: 'hub', role: 'passive', name: `arm pivot ${i + 1}`, c: V.scale(a, P.Ra[i]), axis: a, r: 8, h: 4 });
      });
      const plate = K.greatArc(ap[1], ap[2], P.Ra[1], P.Ra[2], 10).concat(K.greatArc(ap[2], ap[0], P.Ra[2], P.Ra[0], 10).slice(1));
      const harm = ctx.armAxis, cuffC = V.scale(harm, P.cuff_at), lat = ap[2];
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm plate (deltoid)', pts: plate.map(p => V.madd(p, V.unit(p), -2)), r: 3 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'plate to cuff', a: lat, b: V.madd(cuffC, V.unit(V.reject(lat, harm)), 47), r: 3 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
