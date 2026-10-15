/* seed-spm-3rrr - Agile-Eye-type spherical parallel 3-RRR wrapped around the shoulder (docs/concepts/seed-spm-3rrr.md,
 * models/seed-spm-3rrr.py). Three base hubs on the scapula (b_rho deg around a centre direction), each the ACTIVE
 * joint of one leg: proximal arc (a1) -> PASSIVE elbow hub -> distal arc (a2) -> PASSIVE platform hub whose axis is
 * fixed in the humerus (a cone p_cone about the arm axis: the platform IS the arm side of the cuff, no extra ring).
 * All 9 axes through GH; spherical Gruebler 3(8-1-9)+9 = 3. Elbow = two-cone closure (angle a1 from the base axis,
 * a2 from the platform axis) on a fixed branch per leg. Best honest sweep entry (k46, gap 193.44, hub-axis
 * accessibility enforced). Out of range: a leg cannot close, or cond(J) > 50 (Gosselin J = B^-1 A). Hub radii are
 * schematic (base 56, elbow 70, platform 62 mm): the bench fit put HW0 / HW1 at 201 / 157 mm, which is the concept's
 * red-team result, not a plausible part. Closed form; residual = each leg's distal-arc error. 3 ACTIVE + 6 PASSIVE. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { b_th: 33.713, b_ph: 26.438, b_rho: 30.684, b_psi0: 360.0, b_psis: 121.565, p_cone: 48.536, p_az: -47.436,
              p_spread: 51.204, a1: 85.836, a2: 50.662, br: [1, -1, 1], perm: [1, 0, 2], cond_max: 50,
              rB: 56, rW: 70, rV: 62, hub_r: 10, stack: 12.25, cuff_at: 165 };
  // base axes (scapula frame): 3 spots b_rho around c = sph(b_th, b_ph) (th from lateral, ph 0 = up, 90 = back)
  const sph = (th, ph) => [-Math.sin(th * D) * Math.sin(ph * D), Math.sin(th * D) * Math.cos(ph * D), Math.cos(th * D)];
  const c = sph(P.b_th, P.b_ph), e1 = V.unit(V.sub(sph(P.b_th + 1e-3, P.b_ph), c)), e2 = V.cross(c, e1);
  const U = [-1, 0, 1].map(k => {
    const ps = (P.b_psi0 + k * P.b_psis) * D, d = V.add(V.scale(e1, Math.cos(ps)), V.scale(e2, Math.sin(ps)));
    return V.unit(M.mulv(M.rot(V.cross(c, d), P.b_rho), c));
  });
  // platform axes (humerus frame): cone p_cone about the arm axis, azimuths p_az +- p_spread, leg i -> axis perm[i]
  const V0 = [P.p_az - P.p_spread, P.p_az, P.p_az + P.p_spread].map(az => K.wdir(P.p_cone, az));
  const Vh = P.perm.map(j => V0[j]), ref = U.map(u => V.perp(u));
  function eig3(A) {                                            // eigenvalues of a symmetric 3x3 (descending)
    const p1 = A[0][1] ** 2 + A[0][2] ** 2 + A[1][2] ** 2, q = (A[0][0] + A[1][1] + A[2][2]) / 3;
    const p2 = (A[0][0] - q) ** 2 + (A[1][1] - q) ** 2 + (A[2][2] - q) ** 2 + 2 * p1, p = Math.sqrt(p2 / 6) || 1e-12;
    const B = A.map((r, i) => r.map((x, j) => (x - (i === j ? q : 0)) / p));
    const det = B[0][0] * (B[1][1] * B[2][2] - B[1][2] * B[2][1]) - B[0][1] * (B[1][0] * B[2][2] - B[1][2] * B[2][0]) + B[0][2] * (B[1][0] * B[2][1] - B[1][1] * B[2][0]);
    const ph = Math.acos(Math.max(-1, Math.min(1, det / 2))) / 3, l1 = q + 2 * p * Math.cos(ph), l3 = q + 2 * p * Math.cos(ph + 2 * Math.PI / 3);
    return [l1, 3 * q - l1 - l3, l3];
  }
  function frame(ctx) {                                         // scapula frame: platform axes and closure elbows
    const Q = M.mul(M.T(ctx.S), ctx.H), Vs = Vh.map(v => M.mulv(Q, v));
    const legs = Vs.map((v, i) => { const ci = K.circInt(U[i], P.a1, v, P.a2, P.br[i]); return { v, w: ci.p, ok: ci.ok }; });
    return { Vs, legs };
  }
  const elbow = (q, i) => K.onCone(U[i], ref[i], P.a1, q[i]);
  function condJ(W, Vs) {                                       // Gosselin J = B^-1 A, cond = sqrt(l_max / l_min) of J^T J
    const J = [0, 1, 2].map(i => V.scale(V.cross(W[i], Vs[i]), 1 / (V.dot(V.cross(U[i], W[i]), Vs[i]) || 1e-12)));
    const JtJ = [0, 1, 2].map(a => [0, 1, 2].map(b => J[0][a] * J[0][b] + J[1][a] * J[1][b] + J[2][a] * J[2][b]));
    const l = eig3(JtJ); return Math.sqrt(Math.max(l[0], 0) / Math.max(l[2], 1e-12));
  }
  const solve = ctx => frame(ctx).legs.map((l, i) => K.axisAngle(U[i], ref[i], l.w));

  K.register({
    id: 'seed-spm-3rrr',
    name: 'Spherical parallel 3-RRR (three legs)',
    dof: { active: 3, passive: 6 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['base hub 1', 'base hub 2', 'base hub 3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => { const f = frame(ctx); return f.legs.map((l, i) => V.angle(elbow(q, i), l.v) - P.a2); },
    check: (q, ctx) => {
      const f = frame(ctx);
      for (let i = 0; i < 3; i++) if (!f.legs[i].ok) return `leg ${i + 1} cannot close (its two cones separate)`;
      const cj = condJ([0, 1, 2].map(i => elbow(q, i)), f.Vs);
      return cj > P.cond_max ? `near a singularity (cond J ${cj.toFixed(0)} > ${P.cond_max})` : null;
    },
    parts: (q, ctx) => {
      const f = frame(ctx), S = d => M.mulv(ctx.S, d), h = P.stack, out = [];
      const Uw = U.map(S), Ww = [0, 1, 2].map(i => S(elbow(q, i))), Vw = f.Vs.map(S);
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base frame 1-2', u: Uw[0], v: Uw[1], r0: P.rB - 2, r1: P.rB - 2, r: 3 },
        { kind: 'arc', role: 'fixed-scapula', name: 'base frame 2-3', u: Uw[1], v: Uw[2], r0: P.rB - 2, r1: P.rB - 2, r: 3 });
      for (let i = 0; i < 3; i++) {
        out.push({ kind: 'hub', role: 'active', name: `base hub ${i + 1} (leg ${i + 1})`, c: V.scale(Uw[i], P.rB), axis: Uw[i], r: P.hub_r, h },
          { kind: 'arc', role: 'link', name: `proximal arc ${i + 1}`, u: Uw[i], v: Ww[i], r0: P.rB + 6, r1: P.rW + 3, r: 2.5 },
          { kind: 'hub', role: 'passive', name: `elbow hub ${i + 1}`, c: V.scale(Ww[i], P.rW), axis: Ww[i], r: P.hub_r, h },
          { kind: 'arc', role: 'link', name: `distal arc ${i + 1}`, u: Ww[i], v: Vw[i], r0: P.rW + 9, r1: P.rV + 6, r: 2.5 },
          { kind: 'hub', role: 'passive', name: `platform hub ${i + 1}`, c: V.scale(Vw[i], P.rV), axis: Vw[i], r: P.hub_r, h });
      }
      const harm = ctx.armAxis, mid = Vw[P.perm.indexOf(1)], cuffC = V.scale(harm, P.cuff_at);
      const drop = V.scale(V.unit(V.add(V.scale(mid, 0.6), V.scale(harm, 0.4))), P.rV + 1);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'platform strap a', u: Vw[0], v: Vw[1], r0: P.rV - 2, r1: P.rV - 2, r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'platform strap b', u: Vw[1], v: Vw[2], r0: P.rV - 2, r1: P.rV - 2, r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'arm-end drop strap', u: mid, v: drop, r0: P.rV - 2, r1: P.rV + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'drop strap to cuff', a: drop, b: V.madd(cuffC, V.unit(V.reject(drop, harm)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
