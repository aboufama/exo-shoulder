/* scapula-halo-track - the base is a CLOSED, NON-CIRCULAR TRACK fixed to the scapula handler, drawn around the acromion
 * summit on the skin that stays in band in every pose; J1 is a bogie carriage on it (its arc position s is the joint),
 * J2 an O20 hub on the carriage with its axis radial through GH (p2 = u(s)), link 2 a strap of arc a2 to J3, an O20 hub
 * fixed to the arm at W (docs/concepts/scapula-halo-track.md, models/scapula-halo-track.py; best k124, gap 87.64:
 * W = wdir(100, -15), a2 75, sigma -1, track underside 51-65 mm, J2 eye 74.7 mm, J3 disc 71.9 mm). Closure: s solves
 * angle(u(s), w) = a2, a 1-D root on the loop (branch = the sign of the track tangent along w), picked nearest the
 * previous frame (q1 = its phase on the loop, 360 deg = once round); q2 = azimuth of w about p2 from the track tangent; q3 = twist about w. 3 active, 0 passive: the
 * radial J2 pin slide (13 mm, the track's radius follows the skin) is cam-set by s, not free. Rejected: no crossing
 * (the circle of radius a2 about w misses the loop: 35 % of bench poses) or a near-tangent crossing (< 10 deg, the
 * carriage would back-drive). The loop shape is a stand-in for the model's bench in-band contour "ib100" (polar cap
 * above el ~76 + a posterior lobe az -24..72 down to el ~38, fitted by a small circle + 3 harmonics as the model does);
 * its radius profile 51-65 mm by elevation is schematic. */
(function () {
  const K = (typeof window !== 'undefined' ? window : globalThis).KIN, V = K.V, M = K.M, D2R = K.D2R, R2D = K.R2D;
  const P = { W: [100, -15], a2: 75, sigma: -1, cap_el: 76, lobe: [-24, 72], lobe_el: 38, ramp: 24, NT: 240,
              Rt: [51.4, 64.7], H2: 74.7, slide: 13.2, F3: 71.9, hub_r: 10, stack: 12.25, car: [20, 16, 9], transv: 10,
              neck_deg: 25, cuff_at: 165 };
  const W0 = K.wdir(...P.W), ref3L = V.unit(V.reject([0, -1, 0], W0));

  // ---- the track (scapula frame): zone boundary el*(az) -> small circle + 3 harmonics -> NT points even in arc length
  const TR = (function () {
    const lobeW = az => { const lo = P.lobe[0], hi = P.lobe[1], d = az < lo ? lo - az : az > hi ? az - hi : 0;
      const x = Math.max(0, 1 - d / P.ramp); return x * x * (3 - 2 * x); };
    const U = []; for (let az = -180; az < 180; az += 3) U.push(K.bvec(az, P.cap_el - (P.cap_el - P.lobe_el) * lobeW(az)));
    const c = V.unit(U.reduce((a, b) => V.add(a, b), [0, 0, 0])), ex = V.perp(c), ey = V.cross(c, ex);
    const basis = ps => [1, Math.cos(ps), Math.sin(ps), Math.cos(2 * ps), Math.sin(2 * ps), Math.cos(3 * ps), Math.sin(3 * ps)];
    const A = [], b = []; for (let i = 0; i < 7; i++) { A.push(new Array(7).fill(0)); b.push(0); }
    for (const u of U) {                                         // least squares of the polar angle about c
      const f = basis(Math.atan2(V.dot(u, ey), V.dot(u, ex))), y = Math.acos(Math.max(-1, Math.min(1, V.dot(u, c))));
      for (let i = 0; i < 7; i++) { b[i] += f[i] * y; for (let j = 0; j < 7; j++) A[i][j] += f[i] * f[j]; }
    }
    for (let i = 0; i < 7; i++) for (let r = i + 1; r < 7; r++) { const k = A[r][i] / A[i][i]; for (let j = i; j < 7; j++) A[r][j] -= k * A[i][j]; b[r] -= k * b[i]; }
    const co = new Array(7).fill(0); for (let i = 6; i >= 0; i--) { let s = b[i]; for (let j = i + 1; j < 7; j++) s -= A[i][j] * co[j]; co[i] = s / A[i][i]; }
    const dense = [], N = 1440;
    for (let i = 0; i < N; i++) { const ps = 2 * Math.PI * i / N, rh = basis(ps).reduce((s, f, j) => s + f * co[j], 0);
      dense.push(V.add(V.scale(c, Math.cos(rh)), V.scale(V.add(V.scale(ex, Math.cos(ps)), V.scale(ey, Math.sin(ps))), Math.sin(rh)))); }
    const cum = [0]; for (let i = 1; i <= N; i++) cum.push(cum[i - 1] + V.angle(dense[i - 1], dense[i % N]));
    const L = cum[N], Ut = []; let j = 0;
    for (let k = 0; k < P.NT; k++) { const s = L * k / P.NT; while (cum[j + 1] < s) j++;
      Ut.push(V.unit(V.lerp(dense[j], dense[(j + 1) % N], (s - cum[j]) / (cum[j + 1] - cum[j] || 1)))); }
    const Tt = Ut.map((u, k) => V.unit(V.reject(V.sub(Ut[(k + 1) % P.NT], Ut[(k + P.NT - 1) % P.NT]), u)));
    return { U: Ut, T: Tt, L, ds: L / P.NT, c };
  })();
  const elev = u => Math.asin(Math.max(-1, Math.min(1, u[1]))) * R2D;
  const Rt = u => Math.max(P.Rt[0], Math.min(P.Rt[1], 56 + (P.Rt[1] - 56) * (elev(u) - P.lobe_el) / (P.cap_el - P.lobe_el)));
  /** unit dir, tangent, normal at arc position s (deg), scapula frame */
  function at(s) {
    const x = ((s % TR.L) + TR.L) % TR.L / TR.ds, j = Math.floor(x) % P.NT, k = (j + 1) % P.NT, t = x - Math.floor(x);
    const u = V.unit(V.lerp(TR.U[j], TR.U[k], t)), T = V.unit(V.reject(V.lerp(TR.T[j], TR.T[k], t), u));
    return { u, T, N: V.cross(u, T) };
  }
  /** crossings of the track with the circle of radius a2 about w (scapula frame) on branch sigma */
  function roots(wS) {
    const f = TR.U.map(u => V.angle(u, wS) - P.a2), out = [];
    for (let j = 0; j < P.NT; j++) {
      const g0 = f[j], g1 = f[(j + 1) % P.NT]; if ((g0 <= 0) === (g1 <= 0)) continue;
      let s = (j + g0 / (g0 - g1)) * TR.ds;
      for (let it = 0; it < 3; it++) { const a = at(s), fs = V.angle(a.u, wS) - P.a2, sn = Math.sin(Math.acos(Math.max(-1, Math.min(1, V.dot(a.u, wS)))));
        const df = -V.dot(a.T, wS) / Math.max(sn, 1e-6) * R2D * D2R; if (Math.abs(df) > 1e-6) s -= fs / df; }
      const a = at(s), cphi = V.dot(a.T, wS) / Math.sin(P.a2 * D2R);
      if ((cphi > 0 ? 1 : -1) === P.sigma) out.push({ s: ((s % TR.L) + TR.L) % TR.L, cphi });
    }
    return out;
  }
  function joints(s, ctx) {
    const a = at(s), S = ctx.S, p2 = M.mulv(S, a.u), T = M.mulv(S, a.T), N = M.mulv(S, a.N), w = M.mulv(ctx.H, W0);
    const ref3 = M.mulv(ctx.H, ref3L);
    return [s * 360 / TR.L, Math.atan2(V.dot(N, w), V.dot(T, w)) * R2D, Math.atan2(V.dot(p2, V.cross(w, ref3)), V.dot(p2, ref3)) * R2D];
  }
  function solve(ctx, qPrev) {
    const wS = M.mulv(M.T(ctx.S), M.mulv(ctx.H, W0)), r = roots(wS);
    let s;
    if (r.length) {
      const ref = qPrev && isFinite(qPrev[0]) ? qPrev[0] * TR.L / 360 : r[0].s;
      s = r.reduce((b, x) => Math.abs(K.wrap180((x.s - ref) * 360 / TR.L)) < Math.abs(K.wrap180((b.s - ref) * 360 / TR.L)) ? x : b).s;
    } else {                                                   // no crossing: the closest approach (the residual reports it)
      let best = 1e9; TR.U.forEach((u, k) => { const d = Math.abs(V.angle(u, wS) - P.a2); if (d < best) { best = d; s = k * TR.ds; } });
    }
    return joints(s, ctx);
  }

  K.register({
    id: 'scapula-halo-track',
    name: 'Scapula halo track (J1 = bogie on a closed loop)',
    dof: { active: 3, passive: 0 },
    params: P,
    q0: ctx => solve(ctx, null),
    qNames: ['J1 carriage phase on the loop (360 = once round)', 'J2', 'J3'], qUnits: ['deg', 'deg', 'deg'], resUnits: ['deg', 'deg', 'deg', 'deg'],
    solve,
    residual: (q, ctx) => {
      const a = at(q[0] * TR.L / 360), S = ctx.S, p2 = M.mulv(S, a.u), e = V.add(V.scale(M.mulv(S, a.T), Math.cos(q[1] * D2R)), V.scale(M.mulv(S, a.N), Math.sin(q[1] * D2R)));
      const wc = V.add(V.scale(p2, Math.cos(P.a2 * D2R)), V.scale(e, Math.sin(P.a2 * D2R))), w = M.mulv(ctx.H, W0), ref3 = M.mulv(ctx.H, ref3L);
      return V.scale(V.sub(wc, w), R2D).concat([K.wrap180(q[2] - Math.atan2(V.dot(p2, V.cross(w, ref3)), V.dot(p2, ref3)) * R2D)]);
    },
    check: (q, ctx) => {
      const wS = M.mulv(M.T(ctx.S), M.mulv(ctx.H, W0)), r = roots(wS);
      if (!r.length) return 'no crossing: the circle about W misses the track';
      const a = at(q[0] * TR.L / 360), cphi = V.dot(a.T, wS) / Math.sin(P.a2 * D2R);
      if (Math.abs(cphi) < Math.sin(P.transv * D2R)) return 'crossing near tangent (the carriage would back-drive)';
      return null;
    },
    parts: (q, ctx) => {
      const S = ctx.S, a = at(q[0] * TR.L / 360), p2 = M.mulv(S, a.u), T = M.mulv(S, a.T), w = M.mulv(ctx.H, W0), h = P.stack, rt = Rt(a.u);
      const loop = TR.U.concat([TR.U[0]]).map(u => M.mulv(S, V.scale(u, Rt(u))));
      const harm = ctx.armAxis, ng = P.neck_deg * D2R;
      const nk = V.unit(V.add(V.scale(w, Math.cos(ng)), V.scale(V.unit(V.reject(harm, w)), Math.sin(ng))));
      const neckEnd = V.scale(nk, P.F3 + 1), cuffC = V.scale(harm, P.cuff_at), cuffTop = V.madd(cuffC, V.unit(V.reject(neckEnd, harm)), 47);
      return [
        { kind: 'plate', role: 'fixed-scapula', name: 'handler mount', c: M.mulv(S, V.scale(TR.c, P.Rt[0] - 4)), z: M.mulv(S, TR.c), x: M.mulv(S, [1, 0, 0]), size: [26, 18], t: 3 },
        { kind: 'arc', role: 'fixed-scapula', name: 'halo track (closed loop, scapula-fixed)', pts: loop, r: 3, w: 8 },
        { kind: 'carriage', role: 'active', name: 'J1 bogie carriage', c: V.scale(p2, rt + 2), x: T, z: p2, size: P.car },
        { kind: 'slider', role: 'passive', name: 'J2 pin radial slide (cam-set by s, not a DOF)', a: V.scale(p2, P.H2 - P.slide - 4), b: V.scale(p2, P.H2), at: V.scale(p2, rt + P.car[2]), z: T, size: [8, 8, 4] },
        { kind: 'hub', role: 'active', name: 'J2 (radial axis through GH)', c: V.scale(p2, P.H2 - 3), axis: p2, r: P.hub_r, h },
        { kind: 'arc', role: 'link', name: 'link 2', u: p2, v: w, r0: P.H2 + h - 2, r1: P.F3 + h + 1, r: 2.5 },
        { kind: 'hub', role: 'active', name: 'J3 (arm-fixed W)', c: V.scale(w, P.F3), axis: w, r: P.hub_r, h },
        { kind: 'arc', role: 'fixed-arm', name: 'neck', u: w, v: nk, r0: P.F3 + 1, r1: P.F3 + 1, r: 3 },
        { kind: 'link', role: 'fixed-arm', name: 'neck to cuff', a: neckEnd, b: cuffTop, r: 3 },
        { kind: 'strap', role: 'fixed-arm', name: 'arm cuff', c: cuffC, axis: harm, r: 47, w: 26 },
        { kind: 'point', role: 'link', name: 'GH centre', p: [0, 0, 0], r: 4 }
      ];
    }
  });
})();
