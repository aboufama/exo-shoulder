/* three-head-deltoid-spm - three-headed exo-deltoid: a 3-RRR spherical parallel mechanism with every actuator on the
 * scapula (catalogue three-head-deltoid-spm; ideated, no bench model or sweep yet: the spec's seed layout). Three legs
 * follow the three deltoid heads. Base hub (ACTIVE, radial, scapula-fixed): anterior head over the front of the
 * acromion u_A = bvec(120, 60), middle head on the acromion top u_M = bvec(70, 70), posterior head on the spine
 * u_P = bvec(10, 50); proximal arc (90 deg) -> elbow hub (PASSIVE) -> distal arc (90 deg) -> platform hub (PASSIVE) on
 * a small arm pad on the cap band: v_A = wdir(95, 15), v_M = wdir(112, -15), v_P = wdir(100, -55), the pads tied by an
 * arm-fixed bridge that runs on to BOTTOM. All 9 axes through GH; elbow W_k = two-cone closure on working mode s_k,
 * picked at rest as the spec says (the elbow farther from the other legs). Layers (spec): base pads + bridge at rho0,
 * proximal arcs + arm pads at rho0 + 3.15, distal arcs at rho0 + 6.3 (rho0 = 55 mm, schematic before the skin fit).
 * Out of range (spec rules): a leg within 12 deg of stretched / folded (theta_k < 12 or > 168), an elbow hub within
 * 17 mm of another leg's elbow or arc; type-2 index |det[unit(W_k x V_k)]| < 0.05 reported as the platform going loose.
 * Closed form; residual = each leg's distal-arc error. Mobility 3: 3 ACTIVE (base hubs) + 6 PASSIVE. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { base: [[120, 60], [70, 70], [10, 50]], pad: [[95, 15], [112, -15], [100, -55]], ap: 90, ad: 90, margin: 12,
              rho0: 55, up: 3.15, hub_r: 10, stack: 12.25, clash: 17, det_min: 0.05, bar: [0, -70, 67.5], cuff_at: 165 };
  const names = ['anterior', 'middle', 'posterior'];
  const U = P.base.map(b => V.unit(K.bvec(b[0], b[1]))), Vh = P.pad.map(w => V.unit(K.wdir(w[0], w[1])));
  const ref = U.map(u => V.perp(u)), rE = P.rho0 + P.up;                              // elbow hub face on the proximal layer
  const Vsc = ctx => { const Q = M.mul(M.T(ctx.S), ctx.H); return Vh.map(v => M.mulv(Q, v)); };
  // working modes: at rest, each leg takes the elbow farther from the other legs' base and platform axes
  const modes = (() => {
    const ctx = K.makeCtx(K.KEYS[0].pose, 0), Vs = Vsc(ctx);
    return [0, 1, 2].map(k => {
      const score = s => { const w = K.circInt(U[k], P.ap, Vs[k], P.ad, s).p;
        return Math.min(...[0, 1, 2].filter(j => j !== k).map(j => Math.min(V.angle(w, U[j]), V.angle(w, Vs[j])))); };
      return score(1) >= score(-1) ? 1 : -1;
    });
  })();
  function frame(ctx) {
    const Vs = Vsc(ctx);
    return Vs.map((v, k) => { const c = K.circInt(U[k], P.ap, v, P.ad, modes[k]); return { v, w: c.p, ok: c.ok, th: V.angle(U[k], v) }; });
  }
  const elbow = (q, k) => K.onCone(U[k], ref[k], P.ap, q[k]);
  const solve = ctx => frame(ctx).map((l, k) => K.axisAngle(U[k], ref[k], l.w));

  K.register({
    id: 'three-head-deltoid-spm',
    name: 'Three-headed exo-deltoid (3-RRR SPM)',
    dof: { active: 3, passive: 6 },
    params: Object.assign({ modes }, P),
    q0: ctx => solve(ctx),
    qNames: names.map(n => `${n} head base hub`), qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => solve(ctx),
    residual: (q, ctx) => frame(ctx).map((l, k) => V.angle(elbow(q, k), l.v) - P.ad),
    check: (q, ctx) => {
      const L = frame(ctx);
      for (let k = 0; k < 3; k++) {
        if (!L[k].ok) return `${names[k]} head cannot close`;
        if (L[k].th < Math.abs(P.ap - P.ad) + P.margin || L[k].th > P.ap + P.ad - P.margin) return `${names[k]} head within ${P.margin} deg of stretched / folded`;
      }
      const W = [0, 1, 2].map(k => elbow(q, k));
      for (let k = 0; k < 3; k++) for (let j = 0; j < 3; j++) {
        if (j === k) continue;
        const arcs = K.greatArc(U[j], W[j], 1, 1, 16).concat(K.greatArc(W[j], L[j].v, 1, 1, 16));
        if (Math.min(...arcs.map(d => V.angle(d, W[k]))) * D * rE < P.clash) return `${names[k]} elbow hits the ${names[j]} head`;
      }
      const det = V.dot(V.unit(V.cross(W[0], L[0].v)), V.cross(V.unit(V.cross(W[1], L[1].v)), V.unit(V.cross(W[2], L[2].v))));
      return Math.abs(det) < P.det_min ? 'type-2 singularity: the arm pads go loose' : null;
    },
    parts: (q, ctx) => {
      const L = frame(ctx), S = x => M.mulv(ctx.S, x), r0 = P.rho0, h = P.stack, out = [];
      const Uw = U.map(S), Ww = [0, 1, 2].map(k => S(elbow(q, k))), Vw = L.map(l => S(l.v));
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base bridge A-M', u: Uw[0], v: Uw[1], r0: r0, r1: r0, r: 3 },
        { kind: 'arc', role: 'fixed-scapula', name: 'base bridge M-P', u: Uw[1], v: Uw[2], r0: r0, r1: r0, r: 3 });
      for (let k = 0; k < 3; k++) {
        out.push({ kind: 'hub', role: 'active', name: `${names[k]} head: base hub`, c: V.scale(Uw[k], r0), axis: Uw[k], r: P.hub_r, h },
          { kind: 'arc', role: 'link', name: `${names[k]} head: proximal arc`, u: Uw[k], v: Ww[k], r0: r0 + P.up + 1.5, r1: rE + 1.5, r: 2.5 },
          { kind: 'hub', role: 'passive', name: `${names[k]} head: elbow hub`, c: V.scale(Ww[k], rE), axis: Ww[k], r: P.hub_r, h },
          { kind: 'arc', role: 'link', name: `${names[k]} head: distal arc`, u: Ww[k], v: Vw[k], r0: r0 + 2 * P.up + 1.5, r1: r0 + 2 * P.up + 1.5, r: 2.5 },
          { kind: 'hub', role: 'passive', name: `${names[k]} head: arm pad hub`, c: V.scale(Vw[k], r0 + P.up), axis: Vw[k], r: P.hub_r, h });
      }
      const harm = ctx.armAxis, bar = M.mulv(ctx.H, P.bar), cuffC = V.scale(harm, P.cuff_at), rp = r0 + P.up - 2;
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm bridge A-M', u: Vw[0], v: Vw[1], r0: rp, r1: rp, r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'arm bridge M-P', u: Vw[1], v: Vw[2], r0: rp, r1: rp, r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'strip to BOTTOM\'s cut end', u: Vw[1], v: bar, r0: rp, r1: V.norm(bar), r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM to the cuff', a: bar, b: V.madd(cuffC, V.unit(V.reject(bar, harm)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
