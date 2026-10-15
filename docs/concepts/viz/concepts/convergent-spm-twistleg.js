/* convergent-spm-twistleg - convergent 2+1 spherical parallel mechanism: a five-bar A-frame whose two couplers meet at
 * ONE double pin on the arm (axis W), plus a light third "twist" leg to a second arm pin (axis v3), all three actives
 * on the scapula dome (catalogue convergent-spm-twistleg; models/convergent-spm-twistleg.py, no sweep yet: its PARAMS).
 * Base hubs u_k = bvec(-75, 40), bvec(-35, 40) (the model's) and bvec(150, 45) (the catalogue's anterior-dome twist
 * hub) (ACTIVE) -> crank (arc a_k = 60 / 60 / 70) -> elbow pin e_k (passive) -> coupler (arc c_k = 120 / 120 / 85) -> arm
 * pin about W (legs 1, 2: coaxial, one double-row hub) or v3 (leg 3: W turned 45 deg toward 225, posterior-distal)
 * (passive). Leg 3 screened kinematically first, as the spec asks: over 3 base hubs x branches x 8 v3 directions x 2
 * arcs, the model's bvec(-45, 65) / v3_dir 45 keeps 70 of the 240 loop frames in range (elbows collide, det flips), this
 * one 227. 3 ACTIVE + 6 PASSIVE (spherical Gruebler: 8 bodies, 9 revolutes, M = 3). Closed form as the model:
 * e_k = the two-circle closure (cone a_k about u_k) x (cone c_k about the leg's arm axis) on branch s_k = (-1, 1, 1);
 * q_k = the crank angle about u_k from its rest elbow. Working range (the model's): fold / stretch margin >= 8 deg per
 * leg, det[unit(e1 x W), unit(e2 x W), unit(e3 x v3)] keeps its rest sign with |det| >= 0.1, elbows >= 17 deg apart.
 * Radii schematic (base hubs on the dome, elbows on its rim, the arm plate over the deltoid). Seen in this preview:
 * leg 2 passes its fold behind the back (frames out of range, its crank whips ~100 deg there) and the twist coupler's
 * great arc crosses the humerus axis line (~4 mm) during the forward raise: the bench's contact rule has to decide. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M;
  const P = { u: [[-75, 40], [-35, 40], [150, 45]], a: [60, 60, 70], c: [120, 120, 85], W: [71.38, 4.78], v3_off: 45, v3_dir: 225,
              s: [-1, 1, 1], det_min: 0.1, margin: 8, sep: 17, Fb: [56, 56, 58], Fe: 62, Fa: 68, stack: 12.25, neck_deg: 25, cuff_at: 165 };
  const U = P.u.map(x => V.unit(K.bvec(x[0], x[1]))), W = V.unit(K.wdir(P.W[0], P.W[1]));
  const v3 = (() => {                                             // models/convergent-spm-twistleg.py v3_of
    const td = V.unit(V.scale(V.reject([0, -1, 0], W), -1)); let ta = V.cross(W, td);
    if (V.dot(ta, K.wdir(90, 90)) < 0) ta = V.scale(ta, -1);
    const t = V.add(V.scale(ta, Math.cos(P.v3_dir * K.D2R)), V.scale(td, Math.sin(P.v3_dir * K.D2R)));
    return M.mulv(M.rot(V.cross(W, t), P.v3_off), W);
  })();
  const targets = ctx => { const Q = M.mul(M.T(ctx.S), ctx.H); return [M.mulv(Q, W), M.mulv(Q, W), M.mulv(Q, v3)]; };
  const elbows = ctx => targets(ctx).map((t, k) => K.circInt(U[k], P.a[k], t, P.c[k], P.s[k]));
  const e0 = elbows(K.makeCtx(K.motion(240)[0].pose, 0)).map(x => x.p);          // rest elbows: q = 0
  const elbowAt = (q, k) => M.mulv(M.rot(U[k], q[k]), e0[k]);
  const detOf = (e, t) => { const n = [0, 1, 2].map(k => V.unit(V.cross(e[k], t[k]))); return V.dot(n[0], V.cross(n[1], n[2])); };
  const sgn0 = Math.sign(detOf(e0, targets(K.makeCtx(K.motion(240)[0].pose, 0))));
  const solve = ctx => elbows(ctx).map((x, k) => K.axisAngle(U[k], e0[k], x.p));

  K.register({
    id: 'convergent-spm-twistleg',
    name: 'Convergent 2+1 SPM (twist leg)',
    dof: { active: 3, passive: 6 },
    params: P,
    q0: ctx => solve(ctx),
    qNames: ['base 1 (posterior)', 'base 2 (posterior-lateral)', 'base 3 (twist leg, anterior)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => targets(ctx).map((t, k) => V.angle(elbowAt(q, k), t) - P.c[k]),
    check: (q, ctx) => {
      const t = targets(ctx), e = [0, 1, 2].map(k => elbowAt(q, k));
      for (let k = 0; k < 3; k++) {
        const m = K.foldMargin(U[k], t[k], P.a[k], P.c[k]);
        if (m < P.margin) return m < 0 ? `leg ${k + 1} cannot reach its arm pin` : `leg ${k + 1} within ${m.toFixed(0)} deg of its fold`;
      }
      const d = detOf(e, t);
      if (Math.sign(d) !== sgn0 || Math.abs(d) < P.det_min) return `parallel singularity: the twist goes loose (det ${d.toFixed(2)})`;
      for (let i = 0; i < 3; i++) for (let j = i + 1; j < 3; j++) if (V.angle(e[i], e[j]) < P.sep) return `elbows ${i + 1} and ${j + 1} collide`;
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, Wd = d => M.mulv(S, d), u = U.map(Wd), e = [0, 1, 2].map(k => Wd(elbowAt(q, k)));
      const Wa = M.mulv(ctx.H, W), Va = M.mulv(ctx.H, v3), pin = [Wa, Wa, Va], out = [];
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base frame (1-2)', u: u[0], v: u[1], r0: P.Fb[0] - 2, r1: P.Fb[1] - 2, r: 2.5 });
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base frame (2-3)', u: u[1], v: u[2], r0: P.Fb[1] - 2, r1: P.Fb[2] - 2, r: 2.5 });
      for (let k = 0; k < 3; k++) {
        const hk = P.stack, rE = P.Fe + 3 * k, rP = P.Fa + (k < 2 ? 3.15 * (k + 1) : 3.15);
        out.push({ kind: 'hub', role: 'active', name: `base hub ${k + 1}`, c: V.scale(u[k], P.Fb[k]), axis: u[k], r: 10, h: hk });
        out.push({ kind: 'arc', role: 'link', name: `crank ${k + 1}`, u: u[k], v: e[k], r0: P.Fb[k] + 3.15, r1: rE, r: 2.5 });
        out.push({ kind: 'hub', role: 'passive', name: `elbow pin ${k + 1}`, c: V.scale(e[k], rE), axis: e[k], r: 7, h: 8 });
        out.push({ kind: 'arc', role: 'link', name: k < 2 ? `coupler ${k + 1} (to the W double pin)` : 'twist coupler (to v3)', u: e[k], v: pin[k], r0: rE + 3.15, r1: rP, r: 2.5 });
      }
      out.push({ kind: 'hub', role: 'passive', name: 'arm double pin (W, couplers 1 + 2)', c: V.scale(Wa, P.Fa), axis: Wa, r: 8, h: 10 });
      out.push({ kind: 'hub', role: 'passive', name: 'arm pin v3 (twist leg)', c: V.scale(Va, P.Fa), axis: Va, r: 7, h: 8 });
      const harm = ctx.armAxis, ng = P.neck_deg * K.D2R, nk = V.unit(V.add(V.scale(Wa, Math.cos(ng)), V.scale(V.unit(V.reject(harm, Wa)), Math.sin(ng))));
      const neckEnd = V.scale(nk, P.Fa - 1), cuffC = V.scale(harm, P.cuff_at);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm plate (W - v3)', u: Wa, v: Va, r0: P.Fa - 2, r1: P.Fa - 2, r: 3.5 });
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'neck', u: Wa, v: nk, r0: P.Fa - 1, r1: P.Fa - 1, r: 3 });
      out.push({ kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47), r: 3 });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 });
      out.push({ kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
