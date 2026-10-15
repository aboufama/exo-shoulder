/* tongs-tripod - spherical 3-RPR parallel mechanism whose three 'prismatic' legs are lazy-tongs scissor lattices
 * (catalogue tongs-tripod, models/tongs-tripod.py LEGS0 / PARAMS; no sweep result yet). Leg k: a scapula-fixed O16 boss
 * at a_k (axis through GH) carrying two coaxial half-bars - their opening is the leg's extension Theta_k = angle(a_k,
 * b_k), the ACTIVE joint (sensed there), their mean a PASSIVE swivel - then a lazy tongs of n = 2 units (6 x 2 mm Ti
 * bars, half-arc beta 28 deg, two layers 2.5 mm apart, every pivot radial through GH; beta is a sweep parameter 12-30:
 * the model's default 20 spans at most 78 deg and keeps 43 / 239 loop frames, 28 spans 110 deg and keeps 108), then two coaxial half-bars on an
 * arm boss at b_k (PASSIVE) on one humerus-fixed arm frame (pads + 2 struts) with the neck to BOTTOM. Every node sits at
 * a fixed fraction of the arc a_k -> b_k: centre pivots c_j = g(j / n), lateral pivots cos(delta) g((j - 1/2) / n) +-
 * sin(delta) n_hat, cos(delta) = cos(beta) / cos(Theta / 2n) (model Tongs.nodes). Legs: a = bvec(180, 40) -> b =
 * wdir(60, 20); bvec(-30, 40) -> wdir(100, -60); bvec(150, 80) -> wdir(115, 20). 27 joints: 3 ACTIVE + 24 PASSIVE,
 * all set by closure. q = the three extensions; residual = the part of Theta_k the lattice cannot span (> 2 n beta).
 * Out of range: a leg outside its lattice window (fully stretched: eyes of a lateral pair < 9 mm apart; folded: any
 * two pivots, a pivot and a bar it does not carry, or two same-layer bars within 1 mm - the model's self_ok, scanned
 * at load), the forward singularity |det[unit(b_k x a_k)]| < 0.15, or two legs' centre arcs crossing (all on level 0).
 * Lattice radius 62 / 62 / 60 mm, bosses 56 / 58 mm (schematic; the model fits R(f) per leg). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R, R2D = K.R2D;
  const P = { legs: [{ a: [180, 40], b: [60, 20] }, { a: [-30, 40], b: [100, -60] }, { a: [150, 80], b: [115, 20] }], n: 2, beta: 28,
              r_leg: [62, 62, 60], bar_w: 6, pitch: 2.5, eye_r: 4, shaft_r: 5.5, gap: 1, boss_r: 8, det_min: 0.15,
              bar0: [0, -0.0713 * 67.5 - 0.9975 * 40, 0.9975 * 67.5 - 0.0713 * 40], cuff_at: 165 };
  const n = P.n, beta = P.beta * D;
  const A0 = P.legs.map(l => V.unit(K.bvec(l.a[0], l.a[1]))), B0 = P.legs.map(l => V.unit(K.wdir(l.b[0], l.b[1])));
  const slerp = (a, b, s) => { const th = V.angle(a, b) * D; if (th < 1e-9) return a;
    return V.unit(V.add(V.scale(a, Math.sin((1 - s) * th) / Math.sin(th)), V.scale(b, Math.sin(s * th) / Math.sin(th)))); };
  // node ids: c_j -> j (0..n), l_j+ -> n + 1 + 2(j - 1), l_j- -> n + 2 + 2(j - 1); bars (layer, from, to, pivots on it)
  const lp = j => n + 1 + 2 * (j - 1), lm = j => n + 2 + 2 * (j - 1);
  const BARS = [[0, 0, lm(1), [0, lm(1)]], [1, 0, lp(1), [0, lp(1)]]];
  for (let j = 1; j < n; j++) BARS.push([0, lp(j), lm(j + 1), [lp(j), j, lm(j + 1)]], [1, lm(j), lp(j + 1), [lm(j), j, lp(j + 1)]]);
  BARS.push([0, lp(n), n, [lp(n), n]], [1, lm(n), n, [lm(n), n]]);
  const prad = i => (i === 0 || i === n ? P.shaft_r : P.eye_r);
  function nodes(a, b) {                                                   // unit node directions, Theta, delta (rad)
    const Th = V.angle(a, b) * D, et = V.unit(V.reject(b, a)), nh = V.unit(V.cross(a, b));
    const g = f => V.add(V.scale(a, Math.cos(f * Th)), V.scale(et, Math.sin(f * Th)));
    const cd = Math.cos(beta) / Math.cos(Th / n / 2), de = Math.acos(Math.max(-1, Math.min(1, cd)));
    const N = []; for (let j = 0; j <= n; j++) N.push(g(j / n));
    for (let j = 1; j <= n; j++) { const m = g((j - 0.5) / n); N.push(V.add(V.scale(m, Math.cos(de)), V.scale(nh, Math.sin(de))), V.sub(V.scale(m, Math.cos(de)), V.scale(nh, Math.sin(de)))); }
    return { N, Th, de };
  }
  function selfOk(Th, r) {                                                 // model Tongs.self_ok at constant radius r
    const { N, de } = nodes([1, 0, 0], [Math.cos(Th), 0, Math.sin(Th)]);
    if (!(de > 1e-4) || Th / n / 2 >= beta) return false;
    const dist = (p, q) => V.angle(p, q) * D * r;
    for (let i = 0; i < N.length; i++) for (let j = i + 1; j < N.length; j++) if (dist(N[i], N[j]) < prad(i) + prad(j) + P.gap) return false;
    const cl = BARS.map(([, i0, i1]) => { const o = []; for (let s = 0; s <= 1.0001; s += 0.05) o.push(slerp(N[i0], N[i1], s)); return o; });
    for (let k = 0; k < BARS.length; k++) for (let j = 0; j < N.length; j++)
      if (!BARS[k][3].includes(j) && Math.min(...cl[k].map(p => dist(p, N[j]))) < prad(j) + P.bar_w / 2 + P.gap) return false;
    for (let k1 = 0; k1 < BARS.length; k1++) for (let k2 = k1 + 1; k2 < BARS.length; k2++) {
      if (BARS[k1][0] !== BARS[k2][0] || BARS[k1][3].some(x => BARS[k2][3].includes(x))) continue;
      for (const p of cl[k1]) if (Math.min(...cl[k2].map(q => dist(p, q))) < P.bar_w + P.gap) return false;
    }
    return true;
  }
  const win = P.r_leg.map(r => {                                           // largest contiguous valid Theta interval (deg)
    let best = null, cur = null; const th = []; for (let t = 0.5; t < 2 * P.n * P.beta; t += 0.5) th.push(t);
    th.forEach((t, k) => { const o = selfOk(t * D, r);
      if (o && cur === null) cur = k;
      if ((!o || k === th.length - 1) && cur !== null) { const e = o ? k : k - 1; if (!best || e - cur > best[1] - best[0]) best = [cur, e]; cur = null; } });
    return best ? [th[best[0]], th[best[1]]] : [1, 0];
  });
  function legs(ctx) { const A = A0.map(a => M.mulv(ctx.S, a)), B = B0.map(b => M.mulv(ctx.H, b)); return { A, B, Th: A.map((a, k) => V.angle(a, B[k])) }; }
  const span = 2 * P.n * P.beta - 0.01;
  function arcsCross(a1, b1, a2, b2) {
    const x = V.cross(V.cross(a1, b1), V.cross(a2, b2)); if (V.norm(x) < 1e-9) return false;
    return [V.unit(x), V.scale(V.unit(x), -1)].some(p => Math.abs(V.angle(a1, p) + V.angle(p, b1) - V.angle(a1, b1)) < 1e-6
      && Math.abs(V.angle(a2, p) + V.angle(p, b2) - V.angle(a2, b2)) < 1e-6);
  }

  K.register({
    id: 'tongs-tripod',
    name: 'Tongs tripod (3 scissor legs, 3-RPR)',
    dof: { active: 3, passive: 24 },
    params: Object.assign({ window_deg: win }, P),
    q0: ctx => legs(ctx).Th.map(t => Math.min(t, span)),
    qNames: ['leg 1 extension', 'leg 2 extension', 'leg 3 extension'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg'],
    solve: ctx => legs(ctx).Th.map(t => Math.min(t, span)),
    residual: (q, ctx) => legs(ctx).Th.map((t, k) => t - q[k]),
    check: (q, ctx) => {
      const L = legs(ctx);
      for (let k = 0; k < 3; k++) {
        if (L.Th[k] > win[k][1]) return `leg ${k + 1} lattice fully stretched`;
        if (L.Th[k] < win[k][0]) return `leg ${k + 1} lattice folded shut`;
      }
      const m = [0, 1, 2].map(k => V.unit(V.cross(L.B[k], L.A[k])));
      if (Math.abs(V.dot(m[0], V.cross(m[1], m[2]))) < P.det_min) return 'forward singularity: the arm frame goes loose';
      for (const [i, j] of [[0, 1], [0, 2], [1, 2]]) if (arcsCross(L.A[i], L.B[i], L.A[j], L.B[j])) return `legs ${i + 1} and ${j + 1} cross`;
      return null;
    },
    parts: (q, ctx) => {
      const L = legs(ctx), out = [];
      out.push({ kind: 'arc', role: 'fixed-scapula', name: 'base strut 1-3', u: L.A[0], v: L.A[2], r0: 56, r1: 56, r: 3 },
        { kind: 'arc', role: 'fixed-scapula', name: 'base strut 3-2', u: L.A[2], v: L.A[1], r0: 56, r1: 56, r: 3 });
      for (let k = 0; k < 3; k++) {
        const r = P.r_leg[k], a = L.A[k], th = Math.min(L.Th[k], q[k]) * D;
        const b = th < 1e-6 ? a : V.unit(V.add(V.scale(a, Math.cos(th)), V.scale(V.unit(V.reject(L.B[k], a)), Math.sin(th))));
        const { N } = nodes(a, b);
        out.push({ kind: 'hub', role: 'active', name: `leg ${k + 1} base boss (extension sensed here)`, c: V.scale(a, r - 4), axis: a, r: P.boss_r, h: 10.5 });
        BARS.forEach(([ly, i0, i1], bi) => out.push({ kind: 'arc', role: 'link', name: `leg ${k + 1} bar ${bi + 1} (layer ${ly + 1})`,
          pts: K.greatArc(N[i0], N[i1], r + ly * P.pitch, r + ly * P.pitch, 8), r: 1.5 }));
        for (let i = 1; i < N.length; i++) if (i !== n) {
          const p = V.scale(N[i], r + P.pitch / 2);
          out.push({ kind: 'hub', role: 'passive', name: `leg ${k + 1} ${i < n ? 'centre' : 'side'} pivot`, c: V.madd(p, N[i], -2.5), axis: N[i], p0: p, r: P.eye_r, h: 6 });
        }
        out.push({ kind: 'hub', role: 'passive', name: `leg ${k + 1} arm boss`, c: V.scale(L.B[k], r - 4), axis: L.B[k], r: P.boss_r, h: 10.5 });
      }
      const harm = ctx.armAxis, bar = M.mulv(ctx.H, P.bar0), cuffC = V.scale(harm, P.cuff_at);
      out.push({ kind: 'arc', role: 'fixed-arm', name: 'arm frame strut 1-3', u: L.B[0], v: L.B[2], r0: 58, r1: 58, r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'arm frame strut 3-2', u: L.B[2], v: L.B[1], r0: 58, r1: 58, r: 3 },
        { kind: 'arc', role: 'fixed-arm', name: 'neck to BOTTOM', u: L.B[2], v: bar, r0: 58, r1: V.norm(bar), r: 3.5 },
        { kind: 'link', role: 'fixed-arm', name: 'BOTTOM to the cuff', a: bar, b: V.madd(cuffC, V.unit(V.reject(bar, harm)), 47), r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
