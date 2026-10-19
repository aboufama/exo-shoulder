/* gh-tripod-telescoping-struts - three STRAIGHT U-P-U struts from quiet scapula seats to quiet arm seats; the human
 * GH is the only spherical constraint (a 3-UPU parallel mechanism about the user's own joint). Catalogue entry
 * gh-tripod-telescoping-struts (ideated; no bench model or sweep yet): its model_spec seats. Scapula seats
 * b_k = r_k sdir(lat, lon) (acromion top, posterior-superior, posterior scapula at GH level, r 48 / 62 / 88 mm as the
 * spec expects); arm seats c_k = armpt(s, th, R_env + 6 | + 12) on the rest-arm (body_pose) frame: anterolateral at
 * s 110, posterolateral at s 150, BOTTOM's outer face at s 220 (R_env schematic: 48 / 45 / 43 mm).
 * ACTIVE: the three strut lengths L_k (Ti tube in tube); PASSIVE: 2 + 2 cardan angles per leg (12), set by the strut
 * directions. Closed form L_k = |C_k - B_k|. Working range (spec): L_k in [Lmin_k, 1.9 Lmin_k] with Lmin_k the loop's
 * minimum - 5 mm, and |det[m1 m2 m3]| / prod|m_k| >= 0.15 (m_k = moment of strut k about GH); a strut whose chord
 * passes closer than 45 mm to GH cuts through the shoulder (the spec's main risk) and is flagged too. Measured on the
 * loop: near the rest pose the three struts hang along the arm and stop sensing axial twist (|det| ~ 0.06). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { seatsS: [[48, 55, 15], [62, 40, 95], [88, 0, 95]],                // r, lat, lon (sdir: lon 0 lateral, 90 posterior)
              seatsA: [[110, -30, 54], [150, 35, 51], [220, 8, 55]],             // s, th (deg, 0 lateral, + posterior), r (mm)
              ratio: 1.9, det: 0.15, head: 45, tube: [4, 2.6], uj: 6 };
  const sdir = (lat, lon) => [-Math.cos(lat * D) * Math.sin(lon * D), Math.sin(lat * D), Math.cos(lat * D) * Math.cos(lon * D)];
  const e = V.unit(K.BODY.elbow), l = [0.004, 0.164, 0.986], bb = [-1, 0.023, 0];
  const armpt = (s, th, r) => V.add(V.scale(e, s), V.scale(V.add(V.scale(l, Math.cos(th * D)), V.scale(bb, Math.sin(th * D))), r));
  const bS = P.seatsS.map(([r, la, lo]) => V.scale(sdir(la, lo), r)), cA = P.seatsA.map(([s, th, r]) => armpt(s, th, r));
  const ends = ctx => ({ B: bS.map(b => M.mulv(ctx.S, b)), C: cA.map(c => M.mulv(ctx.Hb, c)) });
  const lengths = ctx => { const { B, C } = ends(ctx); return [0, 1, 2].map(k => V.norm(V.sub(C[k], B[k]))); };
  // stroke: the loop's minimum length - 5 mm, telescope ratio 1.9 (spec)
  const Lmin = [1e9, 1e9, 1e9];
  for (const f of K.motion(120)) lengths(K.makeCtx(f.pose)).forEach((x, k) => { Lmin[k] = Math.min(Lmin[k], x - 5); });
  function detM(ctx) {
    const { B, C } = ends(ctx), m = [0, 1, 2].map(k => V.cross(C[k], V.unit(V.sub(C[k], B[k]))));
    return V.dot(m[0], V.cross(m[1], m[2])) / (V.norm(m[0]) * V.norm(m[1]) * V.norm(m[2]));
  }

  K.register({
    id: 'gh-tripod-telescoping-struts',
    name: 'GH tripod: telescoping struts',
    dof: { active: 3, passive: 12 },
    params: Object.assign({ Lmin }, P),
    q0: ctx => lengths(ctx),
    qNames: ['strut 1 (acromion -> anterolateral)', 'strut 2 (post.-sup. -> posterolateral)', 'strut 3 (posterior -> BOTTOM)'],
    qUnits: ['mm', 'mm', 'mm'], resUnits: ['mm', 'mm', 'mm'],
    solve: ctx => lengths(ctx),
    residual: (q, ctx) => lengths(ctx).map((x, k) => x - q[k]),
    check: (q, ctx) => {
      for (let k = 0; k < 3; k++) if (q[k] < Lmin[k] || q[k] > P.ratio * Lmin[k]) return `strut ${k + 1} past its telescope stroke`;
      const { B, C } = ends(ctx);                    // a straight chord over the convex shoulder: does it cut through it?
      for (let k = 0; k < 3; k++) {
        const d = V.sub(C[k], B[k]), s = Math.max(0, Math.min(1, -V.dot(B[k], d) / V.dot(d, d))), g = V.norm(V.madd(B[k], d, s));
        if (g < P.head) return `strut ${k + 1} cuts through the shoulder (${g.toFixed(0)} mm from GH)`;
      }
      const d = Math.abs(detM(ctx));
      return d < P.det ? `struts near-singular (|det| ${d.toFixed(2)})` : null;
    },
    parts: (q, ctx) => {
      const { B, C } = ends(ctx), out = [], ax = M.mulv(ctx.Hb, e);
      for (let k = 0; k < 3; k++) {
        const dir = V.unit(V.sub(C[k], B[k])), axB = V.unit(V.cross(dir, V.unit(B[k]))), axC = V.unit(V.cross(dir, V.unit(C[k])));
        out.push({ kind: 'plate', role: 'fixed-scapula', name: `scapula seat ${k + 1}`, c: V.madd(B[k], V.unit(B[k]), -4), z: V.unit(B[k]), x: dir, size: [16, 14], t: 4 },
          { kind: 'hub', role: 'passive', name: `cardan ${k + 1} (scapula)`, c: V.madd(B[k], axB, -P.uj), axis: axB, r: P.uj, h: 2 * P.uj },
          { kind: 'telescope', role: 'active', name: `strut ${k + 1} (P, active)`, a: B[k], b: C[k], split: 0.95 * Lmin[k], r0: P.tube[0], r1: P.tube[1] },
          { kind: 'hub', role: 'passive', name: `cardan ${k + 1} (arm)`, c: V.madd(C[k], axC, -P.uj), axis: axC, r: P.uj, h: 2 * P.uj },
          { kind: 'plate', role: 'fixed-arm', name: `arm seat ${k + 1}`, c: V.madd(C[k], V.unit(V.reject(C[k], ax)), -4),
          z: V.unit(V.reject(C[k], ax)), x: ax, size: [16, 14], t: 4 });
      }
      out.push({ kind: 'strap', role: 'fixed-arm', name: 'proximal arm cuff (seats 1, 2)', c: V.scale(ax, 130), axis: ax, r: 47, w: 50 },
        { kind: 'strap', role: 'fixed-arm', name: 'BOTTOM (seat 3)', c: V.scale(ax, 220), axis: ax, r: 45, w: 30 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 });
      return out;
    }
  });
})();
