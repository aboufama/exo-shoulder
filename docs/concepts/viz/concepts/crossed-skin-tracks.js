/* crossed-skin-tracks - two skin-shaped tracks that cross at a radial swivel, no intermediate links at all (catalogue
 * crossed-skin-tracks, models/crossed-skin-tracks.py; dead: best gap 94.55, sweeps/crossed-skin-tracks.json k338).
 * T_S = a halo fixed to the scapula handler: the scapula-frame parallel bvec(az, el(az)), el = 31.9 deg + the k338
 * harmonics; T_H = a thin oval fixed to the arm along the deltoid meridian, wdir(101.7 + 54.1 cos t, -6.9 + 3.0 sin t)
 * in the body_pose humerus frame (the model's RH). Carriage A on T_S (J1, s, ACTIVE) -> thin-section swivel about the
 * radial line through the crossing (J2, q2 = angle between the two track tangents, ACTIVE) -> PASSIVE radial slide
 * (rods on A, bushings in B: L = rho_H - rho_S - stack, closure-set) -> carriage B hanging under T_H (J3, t, ACTIVE).
 * Closed form = the model's crossing finder: exact polyline-polyline intersection on the sphere (1 deg samples, then
 * Gauss-Newton on the exact curves), the crossing of sign sigma = -1 nearest the previous frame; with no crossing the IK reports the closest approach (the
 * chain does not close). Both tracks are trimmed as in the model to the arc the crossing visits (here over the loop),
 * capped at the published lengths (halo 195 deg, arm track 95 deg of arc), placed to cover the most loop frames. Not
 * taken: no crossing, a near-tangent crossing (< 20 deg: jams), crossing off a trimmed track, slide outside 0-25 mm.
 * Radii schematic within the published ranges (halo 58-70 mm, posterior highest; arm track one radius lifted 13 mm
 * over the highest halo point it crosses; stack 11 mm). */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D = K.D2R;
  const P = { halo_el: 31.92, f1c: -0.17, f1s: -4.75, f2c: 0.69, f2s: 0.42, o_d: 101.67, o_a: -6.86, o_A: 54.14, o_B: 3.01,
              sigma: -1, stack: 11, Lmax: 25, trans: 20, arcS: 195, arcH: 95, margin: 12 };
  const elOf = az => { const A = az * D; return P.halo_el + P.f1c * Math.cos(A) + P.f1s * Math.sin(A) + P.f2c * Math.cos(2 * A) + P.f2s * Math.sin(2 * A); };
  const halo = s => V.unit(K.bvec(s, elOf(s)));                                      // scapula frame, s = azimuth (deg)
  const oval = t => V.unit(K.wdir(P.o_d + P.o_A * Math.cos(t * D), P.o_a + P.o_B * Math.sin(t * D)));   // humerus (Hb) frame
  const tang = (f, x) => V.unit(V.sub(f(x + 0.5), f(x - 0.5)));
  const rhoS = s => 64 + 6 * Math.cos(s * D);                                        // posterior (az 0) highest
  const HS = [], HT = []; for (let i = 0; i < 360; i++) { HS.push(halo(i)); HT.push(oval(i)); }
  const cdist = (a, b) => Math.abs(K.wrap180(a - b));

  const ELS = HS.map(u => Math.asin(u[1]) * K.R2D), elLo = Math.min(...ELS) - 1, elHi = Math.max(...ELS) + 1;
  /** crossings of the halo and the arm oval at this pose, in the scapula frame (exact polyline intersection on the
   *  sphere, pruned to the oval segments that reach the halo's band), each refined by Gauss-Newton on the exact curves */
  function crossings(ctx) {
    const Qb = M.mul(M.T(ctx.S), ctx.Hb), B = HT.map(u => M.mulv(Qb, u)), out = [];
    for (let k = 0; k < 360; k++) {
      const b0 = B[k], b1 = B[(k + 1) % 360], e0 = Math.asin(b0[1]) * K.R2D, e1 = Math.asin(b1[1]) * K.R2D;
      if (Math.max(e0, e1) < elLo || Math.min(e0, e1) > elHi) continue;
      const nB = V.cross(b0, b1), az = Math.atan2(b0[2], -b0[0]) * K.R2D;
      for (let dj = -6; dj <= 6; dj++) {
        const j = ((Math.floor(az) + dj) % 360 + 360) % 360, a0 = HS[j], a1 = HS[(j + 1) % 360], nA = V.cross(a0, a1);
        const m0 = V.dot(b0, nA), m1 = V.dot(b1, nA), n0 = V.dot(a0, nB), n1 = V.dot(a1, nB);
        if (m0 * m1 >= 0 || n0 * n1 >= 0 || V.dot(a0, b0) <= 0) continue;
        out.push(refine(Qb, j + n0 / (n0 - n1), k + m0 / (m0 - m1)));
      }
    }
    return out.filter(c => c.sign === P.sigma);
  }
  function refine(Qb, s, t) {
    const F = (s, t) => V.sub(halo(s), M.mulv(Qb, oval(t)));
    for (let it = 0; it < 4; it++) {
      const f = F(s, t), js = V.scale(V.sub(F(s + 1e-3, t), F(s - 1e-3, t)), 500), jt = V.scale(V.sub(F(s, t + 1e-3), F(s, t - 1e-3)), 500);
      const a = V.dot(js, js), b = V.dot(js, jt), c = V.dot(jt, jt), g1 = -V.dot(js, f), g2 = -V.dot(jt, f), det = a * c - b * b;
      if (Math.abs(det) < 1e-14) break;
      s += (c * g1 - b * g2) / det; t += (a * g2 - b * g1) / det;
    }
    const p = halo(s), tS = V.unit(V.reject(tang(halo, s), p)), tH = V.unit(V.reject(M.mulv(Qb, tang(oval, t)), p));
    const sn = V.dot(p, V.cross(tS, tH)), cs = V.dot(tS, tH), th = Math.atan2(Math.abs(sn), cs) * K.R2D;
    return { s: (s % 360 + 360) % 360, t: (t % 360 + 360) % 360, sign: sn > 0 ? 1 : -1, trans: Math.min(th, 180 - th), q2: Math.atan2(sn, cs) * K.R2D };
  }
  /** closed form: the crossing nearest qPrev (s, t); none -> the closest approach of the two curves */
  function cross(ctx, qp) {
    const cs = crossings(ctx);
    if (cs.length) {
      const c = qp ? cs.reduce((x, y) => Math.max(cdist(y.s, qp[0]), cdist(y.t, qp[2])) < Math.max(cdist(x.s, qp[0]), cdist(x.t, qp[2])) ? y : x)
                   : cs.reduce((x, y) => (y.trans > x.trans ? y : x));
      return Object.assign({ hit: true }, c);
    }
    let best = null; const Qb = M.mul(M.T(ctx.S), ctx.Hb), Bq = HT.map(u => M.mulv(Qb, u));
    for (let j = 0; j < 360; j += 2) for (let k = 0; k < 360; k += 2) { const d = V.dot(HS[j], Bq[k]); if (!best || d > best.d) best = { d, s: j, t: k }; }
    const U = M.mulv(ctx.S, halo(best.s)), tS = M.mulv(ctx.S, tang(halo, best.s)), tH = V.unit(V.reject(M.mulv(ctx.Hb, tang(oval, best.t)), U));
    return { hit: false, s: best.s, t: best.t, trans: 0, q2: Math.atan2(V.dot(U, V.cross(tS, tH)), V.dot(tS, tH)) * K.R2D };
  }
  // pre-pass over the loop: visited crossings -> trimmed arcs (capped windows covering the most frames), arm radius
  const vis = []; let qp = null;
  for (const f of K.motion(120)) { const c = cross(K.makeCtx(f.pose), qp); if (c.hit) { vis.push(c); qp = [c.s, 0, c.t]; } }
  function placeWin(vals, len, arcLen) {                  // start (deg of param) of the window of arc length len covering most vals
    let best = 0, nb = -1;
    for (let a = 0; a < 360; a += 2) { const n = vals.filter(v => arcLen(a, v) <= len).length; if (n > nb) { nb = n; best = a; } }
    return best;
  }
  const arcH = (t0, t1) => { let s = 0; const n = Math.ceil(((t1 - t0) % 360 + 360) % 360); for (let i = 0; i < n; i++) s += V.angle(oval(t0 + i), oval(t0 + i + 1)); return s; };
  const s0 = placeWin(vis.map(c => c.s), P.arcS, (a, v) => ((v - a) % 360 + 360) % 360);
  const t0 = placeWin(vis.map(c => c.t), P.arcH, (a, v) => arcH(a, v));
  let t1 = t0; while (arcH(t0, t1 + 1) <= P.arcH) t1++;
  const inS = s => ((s - s0) % 360 + 360) % 360 <= P.arcS, inH = t => ((t - t0) % 360 + 360) % 360 <= t1 - t0;
  const rhoH = Math.max(74, ...vis.filter(c => inS(c.s) && inH(c.t)).map(c => rhoS(c.s) + P.stack + 2));
  const Lof = (s) => rhoH - rhoS(s) - P.stack;
  const fA = (ctx, s) => { const U = M.mulv(ctx.S, halo(s)), T = V.unit(V.reject(M.mulv(ctx.S, tang(halo, s)), U)); return M.fromCols(U, T, V.cross(U, T)); };
  const fB = (ctx, t) => { const U = M.mulv(ctx.Hb, oval(t)), T = V.unit(V.reject(M.mulv(ctx.Hb, tang(oval, t)), U)); return M.fromCols(U, T, V.cross(U, T)); };

  K.register({
    id: 'crossed-skin-tracks',
    name: 'Crossed skin tracks + telescoping swivel',
    dof: { active: 3, passive: 1 },
    params: Object.assign({ halo_from: s0, arm_t: [t0, t1], rhoH }, P),
    q0: ctx => { const c = cross(ctx); return [c.s, c.q2, c.t, Lof(c.s)]; },
    qNames: ['J1 carriage A on the halo (az)', 'J2 swivel', 'J3 carriage B on the arm track (t)', 'radial slide (passive)'],
    qUnits: ['deg', 'deg', 'deg', 'mm'], resUnits: ['deg', 'deg', 'deg', 'mm'],
    solve: (ctx, q) => { const c = cross(ctx, q); return [c.s, q ? q[1] + K.wrap180(c.q2 - q[1]) : c.q2, c.t, Lof(c.s)]; },
    residual: (q, ctx) => M.rotErrDeg(M.mul(fA(ctx, q[0]), M.rot([1, 0, 0], q[1])), fB(ctx, q[2])).concat([q[3] - Lof(q[0])]),
    check: (q, ctx) => {
      const U = M.mulv(ctx.S, halo(q[0])), W = M.mulv(ctx.Hb, oval(q[2]));
      if (V.angle(U, W) > 0.5) return 'the tracks do not cross';
      const tq = Math.abs(K.wrap180(q[1])), tr = Math.min(tq, 180 - tq);
      if (tr < P.trans) return `near-tangent crossing (${tr.toFixed(0)} deg): jams`;
      if (!inS(q[0])) return 'crossing off the trimmed halo';
      if (!inH(q[2])) return 'crossing off the trimmed arm track';
      if (q[3] < 0 || q[3] > P.Lmax) return 'radial slide out of range';
      return null;
    },
    parts: (q, ctx) => {
      const ptsS = [], ptsH = [];
      for (let i = 0; i <= 60; i++) { const s = s0 + P.arcS * i / 60; ptsS.push(V.scale(M.mulv(ctx.S, halo(s)), rhoS(s))); }
      for (let i = 0; i <= 40; i++) ptsH.push(V.scale(M.mulv(ctx.Hb, oval(t0 + (t1 - t0) * i / 40)), rhoH));
      const A = fA(ctx, q[0]), B = fB(ctx, q[2]), U = M.col(A, 0), W = M.col(B, 0), rs = rhoS(q[0]);
      // the arm track is held by a neck from its lower end (the one farther down the arm) to the cuff
      const e0 = ptsH[0], e1 = ptsH[ptsH.length - 1], harm = M.mulv(ctx.Hb, [0, -1, 0]);
      const low = V.dot(e0, harm) > V.dot(e1, harm) ? e0 : e1, cuffC = V.scale(harm, 165), cuffTop = V.madd(cuffC, V.unit(V.reject(low, harm)), 47);
      return [
        { kind: 'arc', role: 'fixed-scapula', name: 'halo track T_S', pts: ptsS, r: 3 },
        { kind: 'carriage', role: 'active', name: 'J1 carriage A', c: V.scale(U, rs + 1), x: M.col(A, 1), z: U, size: [20, 16, 9] },
        { kind: 'hub', role: 'active', name: 'J2 swivel (radial)', c: V.scale(U, rs + 5.5), axis: U, r: 11, h: 4 },
        { kind: 'slider', role: 'passive', name: 'radial slide (rods on A)', a: V.scale(U, rs + 9.5), b: V.scale(U, rs + 9.5 + P.Lmax), at: V.scale(W, rhoH - 6), z: M.col(B, 1), size: [8, 12, 6] },
        { kind: 'carriage', role: 'active', name: 'J3 carriage B (hangs under T_H)', c: V.scale(W, rhoH - 4), x: M.col(B, 1), z: W, size: [20, 16, 9] },
        { kind: 'arc', role: 'fixed-arm', name: 'arm track T_H', pts: ptsH, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to BOTTOM', a: low, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
