/* dome-telescope-tripod - CAREX made rigid: three CURVED telescopes (spherical 3-RPR) between base pivots on the
 * acromion / scapular spine and pivots on a rigid arm plate over the deltoid (catalogue dome-telescope-tripod; ideated,
 * no bench model yet: the model_spec defaults). Leg i: base pivot (passive R, radial axis b_i) -> curved telescope on
 * the great circle b_i -> a_i, constant radius R_i about GH (ACTIVE: its angular length theta_i = angle(b_i, a_i)) ->
 * arm pivot (passive R, radial axis a_i) on the arm plate; the user's cuff slides take up GH translation (outside the
 * count). b = anterior acromion, acromion top, scapular spine (S frame); a = anterior, lateral, posterior deltoid
 * (humerus band frame). Segments: the spec's 2 x 80 deg covers 62 of the 240 loop frames, 3 x 60 deg (the spec's
 * 3-segment option, middle stage centred by a mini scissor) 116, so this preview shows 3 x 60 (legal: L + 3 <= theta
 * <= 3L - 24, theta <= 165). Measured on the loop: theta spans 19-132 / 26-121 / 48-163 deg (ratio up to 7x) - the
 * catalogue's range risk. Parallel singularity: |det[n1 n2 n3]| >= 0.1, n_i = unit(b_i x a_i). Radii schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { b: [[0.30, 0.90, 0.30], [-0.36, 0.93, 0.09], [-0.75, 0.55, -0.37]].map(V.unit),
              a: [[0.85, -0.2, 0.49], [0, -0.2, 0.98], [-0.85, -0.2, 0.49]].map(V.unit),
              L: 60, seg: 3, R: [64, 60, 74], det: 0.1, piv: [8, 9], tube: [3.5, 2.8, 2.0], cuff_at: 165 };
  const legs = ctx => [0, 1, 2].map(i => ({ b: M.mulv(ctx.S, P.b[i]), a: M.mulv(ctx.H, P.a[i]) }));
  const thetas = ctx => legs(ctx).map(l => V.angle(l.b, l.a));
  const along = (b, a, s) => { const e = V.unit(V.reject(a, b)), r = s * D; return V.add(V.scale(b, Math.cos(r)), V.scale(e, Math.sin(r))); };
  const span = (b, a, s0, s1, R) => K.greatArc(along(b, a, s0), along(b, a, s1), R, R);
  const lo = P.L + 3, hi = Math.min(165, 3 * P.L - 24);

  K.register({
    id: 'dome-telescope-tripod',
    name: 'Dome tripod: curved telescopes',
    dof: { active: 3, passive: 6 },
    params: P,
    q0: ctx => thetas(ctx),
    qNames: ['front leg (deg)', 'top leg (deg)', 'back leg (deg)'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => thetas(ctx),
    residual: (q, ctx) => thetas(ctx).map((x, i) => x - q[i]),
    check: (q, ctx) => {
      const nm = ['front', 'top', 'back'];
      for (let i = 0; i < 3; i++) {
        if (q[i] < lo) return `${nm[i]} telescope fully collapsed (${q[i].toFixed(0)} deg < ${lo})`;
        if (q[i] > hi) return `${nm[i]} telescope past its stroke (${q[i].toFixed(0)} deg > ${hi})`;
      }
      const n = legs(ctx).map(l => V.unit(V.cross(l.b, l.a))), d = Math.abs(V.dot(n[0], V.cross(n[1], n[2])));
      return d < P.det ? `parallel singularity: the plate goes loose (|det| ${d.toFixed(2)})` : null;
    },
    parts: (q, ctx) => {
      const L = legs(ctx), out = [], Rb = P.R.map(r => r - P.piv[1]);
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base strap', pts: K.greatArc(L[0].b, L[1].b, Rb[0], Rb[1]).concat(K.greatArc(L[1].b, L[2].b, Rb[1], Rb[2])), r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'arm plate', pts: K.greatArc(L[0].a, L[1].a, Rb[0], Rb[1]).concat(K.greatArc(L[1].a, L[2].a, Rb[1], Rb[2])), r: 3.5 });
      L.forEach((l, i) => {
        const R = P.R[i], th = q[i], mouth = along(l.b, l.a, P.L), tan = V.unit(V.sub(along(l.b, l.a, P.L + 1), mouth));
        out.push({ kind: 'hub', role: 'passive', name: `base pivot ${i + 1}`, c: V.scale(l.b, R - P.piv[1]), axis: l.b, r: P.piv[0], h: P.piv[1] },
          { kind: 'arc', role: 'link', name: `leg ${i + 1} outer channel`, pts: span(l.b, l.a, 0, P.L, R), r: P.tube[0] },
          { kind: 'arc', role: 'link', name: `leg ${i + 1} middle stage`, pts: span(l.b, l.a, th / 2 - P.L / 2, th / 2 + P.L / 2, R), r: P.tube[1] },
          { kind: 'arc', role: 'link', name: `leg ${i + 1} inner bar`, pts: span(l.b, l.a, th - P.L, th, R), r: P.tube[2] },
          { kind: 'carriage', role: 'active', name: `leg ${i + 1} slide (active)`, c: V.scale(mouth, R), x: tan, z: mouth, size: [9, 13, 7.5] },
          { kind: 'hub', role: 'passive', name: `arm pivot ${i + 1}`, c: V.scale(l.a, R - P.piv[1]), axis: l.a, r: P.piv[0], h: P.piv[1] });
      });
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'arm cuff (passive slides)', c: V.scale(ctx.armAxis, P.cuff_at), axis: ctx.armAxis, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
